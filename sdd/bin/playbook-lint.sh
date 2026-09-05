#!/usr/bin/env bash
# playbook-lint.sh — valida sdd/playbook.md (formato ACE-lite), faz retrieval por superfície
# e protege contra "context collapse" (delta only).
#
# Gramática (1 linha de cabeçalho por bullet; continuação indentada com 2 espaços):
#   - [LM-nnn] ajudou=N mordeu=N · conf=YYYY-MM-DD · sup: `t1` `t2` :: regra … **Do instead:** … → ficha: x · promovido_para: —
#   - [LM-nnn] ☠ YYYY-MM-DD :: motivo          (tombstone — só sob "## Tombstones")
#
# Uso:
#   sdd/bin/playbook-lint.sh <playbook.md>                          # lint          exit 0 | 2
#   sdd/bin/playbook-lint.sh --grep <termo> <playbook.md>           # retrieval por sup:  exit 0 | 1 (0 hits)
#   sdd/bin/playbook-lint.sh --grep-all <termo> <playbook.md>       # busca no bloco inteiro (cabeçalho+continuação)
#   sdd/bin/playbook-lint.sh --anti-collapse <head.md> <staged.md>  # delta only    exit 0 | 1 (bloqueia)
#   sdd/bin/playbook-lint.sh --check-fichas <playbook.md>           # fichas        exit 0 | 2 (ausente)
#   sdd/bin/playbook-lint.sh --stats <playbook.md>                  # contagens     exit 0
#   sdd/bin/playbook-lint.sh --self-test                            # baseline vermelho nas fixtures  exit 0 | 2
#
# Exit: 0 ok · 1 = 0 hits / colapso · 2 = formato inválido / ficha ausente / self-test falhou · 64 = uso
#
# Compat: bash 3.2 (macOS), awk POSIX, grep básico (-E/-c/-i/-F). Sem arrays associativos, sem gensub.
# Landmine: expansão colada em não-ASCII usa SEMPRE ${VAR} (bash 3.2 + set -u).
set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "não é um repo git" >&2; exit 64; }
cd "${REPO_ROOT}" || exit 64

# Seções permitidas, na ORDEM fixa. Só 'Sempre' e 'Tombstones' são obrigatórias; as demais são
# opcionais e podem ser trocadas em PLAYBOOK_SECTIONS (mesmo formato: nomes separados por |,
# 'Sempre' primeiro, 'Tombstones' por último).
SECTIONS="${PLAYBOOK_SECTIONS:-Sempre|Dados|Backend|Frontend|Infra / deploy|Reviews / harness|Domínio|Tombstones}"
SECTIONS_OBRIGATORIAS='Sempre|Tombstones'
SEMPRE_MAX_BULLETS=10
SEMPRE_MAX_WORDS=1500
BLOCK_WARN=6
BLOCK_ERR=12
COLLAPSE_PCT=20
MEM_DIR="${PLAYBOOK_MEM_DIR:-sdd/handoffs}"   # onde as fichas (→ ficha: x) vivem: sdd/handoffs/x.md

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t pblint)"
trap 'rm -rf "${TMP}"' EXIT

usage() { sed -n '2,20p' "$0" >&2; exit 64; }

# ── parser (awk) ─────────────────────────────────────────────────────────────
# Emite 1 registro TAB-separado por bullet:
#   id  tipo(ativo|tomb)  secao  linha  nlinhas  doinstead(0|1)  conteudo_normalizado  bloco(com \x01 no lugar de \n)
# conteudo_normalizado = texto após " :: " do cabeçalho (sem contadores/conf) + linhas de continuação
# (\x01 como separador) — é o que o anti-collapse compara (P2 do review: continuação reescrita conta).
PARSE_AWK='
function flush() {
  if (id != "") printf "%s\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n", id, tipo, sec, ln, nl, doi, cont, blk
  id = ""
}
BEGIN { sec = ""; id = "" }
/^## / { flush(); sec = substr($0, 4); next }
/^- \[LM-[0-9][0-9][0-9]\]/ {
  flush()
  match($0, /\[LM-[0-9][0-9][0-9]\]/); id = substr($0, RSTART + 1, RLENGTH - 2)
  tipo = ($0 ~ /^- \[LM-[0-9][0-9][0-9]\] ☠ /) ? "tomb" : "ativo"
  ln = NR; nl = 1
  cont = $0; if (index(cont, " :: ") > 0) cont = substr(cont, index(cont, " :: ") + 4); else cont = ""
  doi = (index($0, "Do instead:") > 0) ? 1 : 0
  blk = $0
  next
}
/^  / && id != "" { nl++; blk = blk "\001" $0; cont = cont "\001" $0; if (index($0, "Do instead:") > 0) doi = 1; next }
{ flush() }
END { flush() }
'

parse() { awk "${PARSE_AWK}" "$1"; }

# ── lint ─────────────────────────────────────────────────────────────────────
HDR_RE='^- \[LM-[0-9]{3}\] ajudou=[0-9]+ mordeu=[0-9]+ · conf=[0-9]{4}-[0-9]{2}-[0-9]{2} · sup: (`[^`]+` ?)+:: .+'
TOMB_RE='^- \[LM-[0-9]{3}\] ☠ [0-9]{4}-[0-9]{2}-[0-9]{2} :: .+'
# awk -v reinterpreta escapes ("\[" viraria "[" e a regex mudaria de sentido) — dobrar as barras ao passar.
HDR_AWK=$(printf '%s' "${HDR_RE}" | sed 's/\\/\\\\/g')
TOMB_AWK=$(printf '%s' "${TOMB_RE}" | sed 's/\\/\\\\/g')

lint() {
  local f="$1" errs=0 warns=0
  [ -f "${f}" ] || { echo "❌ arquivo não encontrado: ${f}" >&2; return 2; }
  err()  { errs=$((errs + 1)); printf '%s:%s: ❌ %s\n' "${f}" "$1" "$2" >&2; }
  warn() { warns=$((warns + 1)); printf '%s:%s: ⚠️  %s\n' "${f}" "$1" "$2" >&2; }

  # (a) seções: só as 8 conhecidas, cada uma no máximo 1 vez, "Tombstones" por último
  awk '/^## /{print NR "\t" substr($0,4)}' "${f}" > "${TMP}/secs"
  while IFS=$'\t' read -r ln name; do
    printf '%s' "${name}" | grep -qE "^(${SECTIONS})\$" || err "${ln}" "seção fora das permitidas (${SECTIONS}): '## ${name}'"
  done < "${TMP}/secs"
  cut -f2 "${TMP}/secs" | sort | uniq -d | while read -r dup; do err 0 "seção repetida: '## ${dup}'"; done
  last=$(tail -1 "${TMP}/secs" | cut -f2); [ -n "${last}" ] && [ "${last}" != "Tombstones" ] && err 0 "'## Tombstones' deve ser a última seção (última é '## ${last}')"
  # (a3) ordem fixa das 8 seções (P2 do review: nomes certos em ordem errada passavam)
  local ordem_esp ordem_obs
  ordem_esp=$(printf '%s\n' "${SECTIONS}" | tr '|' '\n' | grep -xF -f <(cut -f2 "${TMP}/secs") | tr '\n' '|')
  ordem_obs=$(cut -f2 "${TMP}/secs" | grep -xF -f <(printf '%s\n' "${SECTIONS}" | tr '|' '\n') | tr '\n' '|')
  [ "${ordem_esp}" != "${ordem_obs}" ] && err 0 "seções fora da ordem fixa (esperado: ${ordem_esp} · observado: ${ordem_obs})"
  # (a2) 'Sempre' e 'Tombstones' são obrigatórias (playbook vazio/truncado não é playbook)
  local missing=0
  printf '%s\n' "${SECTIONS_OBRIGATORIAS}" | tr '|' '\n' | while read -r req; do
    grep -qxF "${req}" <(cut -f2 "${TMP}/secs") || printf '%s\n' "${req}"
  done > "${TMP}/missing"
  missing=$(wc -l < "${TMP}/missing" | tr -d ' ')
  [ "${missing}" -gt 0 ] && err 0 "seção(ões) obrigatória(s) ausente(s): $(tr '\n' ',' < "${TMP}/missing" | sed 's/,$//; s/,/, /g')"

  # (b) toda linha que começa com "- [" ou "- " dentro de seção precisa casar a gramática
  awk -v HDR="${HDR_AWK}" -v TOMB="${TOMB_AWK}" '
    /^## / { insec = 1; next }
    insec && /^- / {
      if ($0 ~ HDR || $0 ~ TOMB) next
      print NR "\tcabeçalho fora da gramática (esperado: - [LM-nnn] ajudou=N mordeu=N · conf=YYYY-MM-DD · sup: `t` :: … | tombstone só com ☠ data :: motivo)"
      next
    }
    insec && !/^- / && !/^  / && !/^## / && !/^> / && !/^#/ && !/^[[:space:]]*$/ { print NR "\ttexto solto fora de bullet (todo conteúdo de seção vive num bullet)" }
  ' "${f}" | while IFS=$'\t' read -r ln msg; do err "${ln}" "${msg}"; done

  # (c) por bullet: seção conhecida, tombstone×seção, Do instead, tamanho do bloco
  parse "${f}" > "${TMP}/bul"
  while IFS=$'\t' read -r id tipo sec ln nl doi cont blk; do
    printf '%s' "${sec}" | grep -qE "^(${SECTIONS})\$" || err "${ln}" "${id} está fora das seções permitidas ('${sec}')"
    if [ "${tipo}" = "tomb" ]; then
      [ "${sec}" = "Tombstones" ] || err "${ln}" "${id} é tombstone (☠) fora de '## Tombstones'"
    else
      [ "${sec}" = "Tombstones" ] && err "${ln}" "${id} é bullet ATIVO dentro de '## Tombstones' (aposentar = ☠ data :: motivo)"
      [ "${doi:-0}" -eq 1 ] || err "${ln}" "${id} sem 'Do instead:' (regra sem ação corretiva não entra)"
      [ "${nl:-0}" -gt "${BLOCK_ERR}" ] && err "${ln}" "${id} tem ${nl} linhas (máx ${BLOCK_ERR}); detalhe vai para a ficha (→ ficha:)"
      [ "${nl:-0}" -gt "${BLOCK_WARN}" ] && [ "${nl:-0}" -le "${BLOCK_ERR}" ] && warn "${ln}" "${id} tem ${nl} linhas (ideal ≤${BLOCK_WARN})"
    fi
  done < "${TMP}/bul"

  # (d) unicidade de ID (ativos + tombstones)
  cut -f1 "${TMP}/bul" | sort | uniq -d | while read -r dup; do
    lns=$(awk -F'\t' -v d="${dup}" '$1==d{printf "%s ", $4}' "${TMP}/bul")
    err 0 "ID duplicado: ${dup} (linhas ${lns})"
  done

  # (e) ## Sempre: ≤N bullets e ≤M palavras
  sb=$(awk -F'\t' '$2=="ativo" && $3=="Sempre"' "${TMP}/bul" | wc -l | tr -d ' ')
  sw=$(awk '/^## Sempre/{f=1;next} /^## /{f=0} f' "${f}" | wc -w | tr -d ' ')
  [ "${sb}" -gt "${SEMPRE_MAX_BULLETS}" ] && err 0 "'## Sempre' tem ${sb} bullets (máx ${SEMPRE_MAX_BULLETS}) — o resto entra por superfície"
  [ "${sw}" -gt "${SEMPRE_MAX_WORDS}" ] && err 0 "'## Sempre' tem ${sw} palavras (máx ${SEMPRE_MAX_WORDS}) — orçamento de contexto"

  # (f) sanidade: erros contados via arquivo (subshells de pipe não propagam variáveis)
  # Recontagem determinística: refaz as checagens que rodaram em pipe.
  local pipe_errs
  pipe_errs=$( { awk -v HDR="${HDR_AWK}" -v TOMB="${TOMB_AWK}" '
      /^## / { insec = 1; next }
      insec && /^- / { if ($0 ~ HDR || $0 ~ TOMB) next; c++; next }
      insec && !/^- / && !/^  / && !/^## / && !/^> / && !/^#/ && !/^[[:space:]]*$/ { c++ }
      END { print c + 0 }' "${f}"; cut -f2 "${TMP}/secs" | sort | uniq -d | wc -l; cut -f1 "${TMP}/bul" | sort | uniq -d | wc -l; } | awk '{s+=$1} END{print s}')
  errs=$((errs + pipe_errs))

  local na nt
  na=$(awk -F'\t' '$2=="ativo"' "${TMP}/bul" | wc -l | tr -d ' ')
  nt=$(awk -F'\t' '$2=="tomb"'  "${TMP}/bul" | wc -l | tr -d ' ')
  [ "${na}" -eq 0 ] && err 0 "playbook sem NENHUM bullet ativo — arquivo vazio/truncado não passa (delta only ⇒ isso é collapse total)"
  if [ "${errs}" -gt 0 ]; then
    printf '🔴 %s: %d erro(s), %d aviso(s) — %d ativos, %d tombstones\n' "${f}" "${errs}" "${warns}" "${na}" "${nt}" >&2
    return 2
  fi
  printf '🟢 %s: formato OK — %d ativos, %d tombstones, Sempre=%d bullets/%d palavras, %d aviso(s)\n' "${f}" "${na}" "${nt}" "${sb}" "${sw}" "${warns}"
  return 0
}

# ── retrieval ────────────────────────────────────────────────────────────────
grep_ids() {
  local termo="$1" f="$2" modo="${3:-sup}" hits=0
  [ -f "${f}" ] || { echo "❌ arquivo não encontrado: ${f}" >&2; return 2; }
  parse "${f}" > "${TMP}/bul"
  local lc; lc=$(printf '%s' "${termo}" | tr '[:upper:]' '[:lower:]')
  while IFS=$'\t' read -r id tipo sec ln nl doi cont blk; do
    [ "${tipo}" = "ativo" ] || continue
    # modo sup (default): só os termos entre crases de "sup:" (retrieval POR SUPERFÍCIE — contrato do AT-003);
    # modo all (--grep-all): cabeçalho + continuação inteiros (busca livre).
    local alvo
    if [ "${modo}" = "sup" ]; then
      alvo=$(printf '%s' "${blk}" | tr '\001' '\n' | head -1 | sed -E 's/^.*· sup: //; s/ :: .*$//')
    else
      alvo="${blk}"
    fi
    if printf '%s' "${alvo}" | tr '[:upper:]' '[:lower:]' | grep -qF -- "${lc}"; then
      hits=$((hits + 1))
      printf '%s  [%s]  %s\n' "${id}" "${sec}" "$(printf '%s' "${cont}" | cut -c1-110)"
    fi
  done < "${TMP}/bul"
  if [ "${hits}" -eq 0 ]; then
    printf '0 bullets para "%s" em %s (modo %s)\n' "${termo}" "${f}" "${modo}" >&2
    return 1
  fi
  printf '%d bullet(s) para "%s" (modo %s)\n' "${hits}" "${termo}" "${modo}" >&2
  return 0
}

# ── anti-collapse ────────────────────────────────────────────────────────────
# Bloqueia (exit 1) se: (a) qualquer ID de HEAD desapareceu do staged; ou
# (b) > COLLAPSE_PCT% dos IDs de HEAD tiveram conteúdo (após ::) ou seção alterados
#     (tombstone conta como "movido"; contadores/conf NÃO contam).
anti_collapse() {
  local head="$1" staged="$2" total sumiu=0 mudou=0 ids=""
  [ -f "${head}" ] && [ -f "${staged}" ] || { echo "❌ --anti-collapse exige <head.md> <staged.md>" >&2; return 64; }
  parse "${head}"   | sort -t$'\t' -k1,1 > "${TMP}/h"
  parse "${staged}" | sort -t$'\t' -k1,1 > "${TMP}/s"
  total=$(wc -l < "${TMP}/h" | tr -d ' ')
  [ "${total}" -eq 0 ] && { echo "anti-collapse: HEAD sem bullets — nada a proteger"; return 0; }
  while IFS=$'\t' read -r id tipo sec ln nl doi cont blk; do
    sline=$(awk -F'\t' -v i="${id}" '$1==i{print; exit}' "${TMP}/s")
    if [ -z "${sline}" ]; then sumiu=$((sumiu + 1)); ids="${ids} ${id}"; continue; fi
    stipo=$(printf '%s\n' "${sline}" | cut -f2); ssec=$(printf '%s\n' "${sline}" | cut -f3); scont=$(printf '%s\n' "${sline}" | cut -f7)
    if [ "${tipo}" = "ativo" ] && [ "${stipo}" = "tomb" ]; then mudou=$((mudou + 1)); continue; fi
    if [ "${ssec}" != "${sec}" ] || [ "${scont}" != "${cont}" ]; then mudou=$((mudou + 1)); fi
  done < "${TMP}/h"
  local pct=$((mudou * 100 / total))
  if [ "${sumiu}" -gt 0 ]; then
    printf '⛔ anti-collapse: %d ID(s) de HEAD DESAPARECERAM do staged:%s\n' "${sumiu}" "${ids}" >&2
    printf '   IDs nunca somem: aposentar = mover para "## Tombstones" como "- [LM-nnn] ☠ data :: motivo".\n' >&2
    return 1
  fi
  if [ $((mudou * 100)) -gt $((total * COLLAPSE_PCT)) ]; then
    printf '⛔ anti-collapse: %d/%d bullets (%d%%) com conteúdo/seção reescritos num só commit (limite %d%%).\n' "${mudou}" "${total}" "${pct}" "${COLLAPSE_PCT}" >&2
    printf '   Delta only: reescrita grande = 2+ commits; contadores/conf não contam.\n' >&2
    return 1
  fi
  printf 'anti-collapse OK: %d IDs em HEAD, 0 sumiram, %d (%d%%) alterados (limite %d%%)\n' "${total}" "${mudou}" "${pct}" "${COLLAPSE_PCT}"
  return 0
}

# ── fichas ───────────────────────────────────────────────────────────────────
check_fichas() {
  local f="$1" n=0 miss=0
  [ -f "${f}" ] || { echo "❌ arquivo não encontrado: ${f}" >&2; return 2; }
  parse "${f}" > "${TMP}/bul"
  while IFS=$'\t' read -r id tipo sec ln nl doi cont blk; do
    [ "${tipo}" = "ativo" ] || continue
    refs=$(printf '%s' "${blk}" | tr '\001' '\n' | grep -oE '→ ficha: [^·]+' | sed -E 's/^→ ficha: //; s/[[:space:]]+$//' | tr ',' '\n' | sed -E 's/^[[:space:]]+//; s/[[:space:]]+$//')
    for r in ${refs}; do
      [ "${r}" = "—" ] && continue
      n=$((n + 1))
      if [ -f "${MEM_DIR}/${r}.md" ] || [ -f "${MEM_DIR}/${r}" ] || [ -f "${r}" ]; then :; else
        miss=$((miss + 1)); printf '%s:%s: ❌ %s aponta para ficha inexistente: %s (procurado em %s e no repo)\n' "${f}" "${ln}" "${id}" "${r}" "${MEM_DIR}" >&2
      fi
    done
  done < "${TMP}/bul"
  if [ "${miss}" -gt 0 ]; then printf '🔴 fichas: %d referenciada(s), %d ausente(s)\n' "${n}" "${miss}" >&2; return 2; fi
  printf '🟢 fichas: %d referenciada(s), 0 ausente(s)\n' "${n}"
  return 0
}

# ── stats (COULD) ────────────────────────────────────────────────────────────
stats() {
  local f="$1"
  [ -f "${f}" ] || { echo "❌ arquivo não encontrado: ${f}" >&2; return 2; }
  parse "${f}" > "${TMP}/bul"
  local today; today=$(date +%Y-%m-%d)
  awk -F'\t' -v today="${today}" '
    function ymd2days(s,   y,m,d) { y=substr(s,1,4)+0; m=substr(s,6,2)+0; d=substr(s,9,2)+0; return y*365 + m*30 + d }
    $2=="ativo" {
      n[$3]++; tot++
      h=$8; match(h,/ajudou=[0-9]+/); a=substr(h,RSTART+7,RLENGTH-7)+0
      match(h,/mordeu=[0-9]+/); m=substr(h,RSTART+7,RLENGTH-7)+0
      match(h,/conf=[0-9-]+/); c=substr(h,RSTART+5,RLENGTH-5)
      if (m>=a && m>0) prob++; if (a+m==0) unused++
      if (ymd2days(today)-ymd2days(c) > 180) stale++
      if (m>=2) promo++
    }
    $2=="tomb" { tomb++ }
    END {
      printf "ativos=%d tombstones=%d problematic(mordeu>=ajudou>0)=%d unused(0/0)=%d stale(conf>180d)=%d candidatos_promocao(mordeu>=2)=%d\n", tot, tomb, prob, unused, stale, promo
      for (s in n) printf "  %-26s %d\n", s, n[s]
    }' "${TMP}/bul"
}

# ── self-test: prova o baseline VERMELHO antes do verde ─────────────────────
self_test() {
  local FX="${PLAYBOOK_FIXTURES:-sdd/fixtures/playbook}" fails=0 out rc
  local SH="/bin/bash"; [ -x "${SH}" ] || SH="bash"
  expect() { # expect <descr> <rc_esperado> <padrao_obrigatorio_na_saida> -- cmd...
    local descr="$1" want="$2" pat="$3"; shift 3
    out=$("${SH}" "$0" "$@" 2>&1); rc=$?
    if [ "${rc}" -ne "${want}" ]; then fails=$((fails + 1)); printf '  ❌ %s → exit %s (esperado %s)\n' "${descr}" "${rc}" "${want}"; printf '%s\n' "${out}" | sed 's/^/     │ /' | head -20; return; fi
    if [ -n "${pat}" ] && ! printf '%s\n' "${out}" | grep -qE -- "${pat}"; then fails=$((fails + 1)); printf '  ❌ %s → exit %s ok, mas saída sem /%s/\n' "${descr}" "${rc}" "${pat}"; printf '%s\n' "${out}" | sed 's/^/     │ /' | head -20; return; fi
    printf '  ✅ %s → exit %s\n' "${descr}" "${rc}"
  }
  echo "self-test (${SH}: $("${SH}" -c 'echo ${BASH_VERSION}')) — fixtures em ${FX}/"
  for f in valido invalido colapso delta-ok; do [ -f "${FX}/playbook-${f}.md" ] || { echo "  ❌ fixture ausente: ${FX}/playbook-${f}.md"; fails=$((fails + 1)); }; done
  [ "${fails}" -gt 0 ] && return 2

  # VERMELHOS primeiro (se algum destes passar, o lint não avalia nada)
  expect "lint fixture INVÁLIDA ⇒ exit 2 com ≥5 motivos distintos" 2 "" "${FX}/playbook-invalido.md"
  local motivos; motivos=$("${SH}" "$0" "${FX}/playbook-invalido.md" 2>&1 | grep -cE 'cabeçalho fora da gramática|ID duplicado|fora das seções|Sempre.*tem 11|sem .Do instead|tombstone \(☠\) fora|ATIVO dentro')
  if [ "${motivos}" -ge 5 ]; then printf '  ✅ fixture inválida acusa %s classes de defeito distintas (≥5)\n' "${motivos}"; else printf '  ❌ fixture inválida acusa só %s classes (esperado ≥5)\n' "${motivos}"; fails=$((fails + 1)); fi
  expect "--grep termo INEXISTENTE ⇒ exit 1 e '0 bullets'" 1 '0 bullets para "tabela_inexistente_xyz"' --grep tabela_inexistente_xyz "${FX}/playbook-valido.md"
  expect "--anti-collapse válido×COLAPSO ⇒ exit 1 citando LM-002" 1 'DESAPARECERAM.*LM-002' --anti-collapse "${FX}/playbook-valido.md" "${FX}/playbook-colapso.md"
  # reescrita >20% sem sumiço: colapso com LM-002 reposto ainda deve bloquear (3 de 6 IDs de HEAD, incl. tombstone = 50%)
  awk '/^## Infra \/ deploy/ && !done { print; print ""; print "- [LM-002] ajudou=1 mordeu=0 · conf=2026-09-02 · sup: `deploy.yml` :: Deploy só em push para main. **Do instead:** trabalhar em branch off origin/main. · promovido_para: —"; done=1; next } { print }' "${FX}/playbook-colapso.md" > "${TMP}/colapso2.md"
  expect "--anti-collapse válido×REESCRITA 3/6=50% (sem sumiço) ⇒ exit 1 por percentual" 1 '50%' --anti-collapse "${FX}/playbook-valido.md" "${TMP}/colapso2.md"
  # (fixture da ficha ruim é gerada aqui para não depender da memória da máquina)
  : > "${TMP}/ficha-ruim.md"; printf '## Domínio\n\n- [LM-001] ajudou=0 mordeu=0 · conf=2026-09-02 · sup: `x` :: r. **Do instead:** y. → ficha: ficha_que_nao_existe_xyz · promovido_para: —\n\n## Tombstones\n' > "${TMP}/ficha-ruim.md"
  expect "--check-fichas com ficha inexistente ⇒ exit 2" 2 'ficha inexistente' --check-fichas "${TMP}/ficha-ruim.md"

  # P2: --grep só casa sup:; --grep-all casa o corpo
  expect "--grep termo só no CORPO (\"Deploy só em push\") ⇒ exit 1 (não é superfície)" 1 '0 bullets' --grep "Deploy só em push" "${FX}/playbook-valido.md"
  expect "--grep-all termo só no CORPO ⇒ exit 0 e LM-002" 0 '^LM-002' --grep-all "Deploy só em push" "${FX}/playbook-valido.md"
  # P2: ordem das seções
  awk '/^## Backend/ { print "## Infra \/ deploy"; next } /^## Infra \/ deploy/ { print "## Backend"; next } { print }' "${FX}/playbook-valido.md" > "${TMP}/ordem.md"
  expect "lint com Backend e Infra TROCADOS ⇒ exit 2 (ordem fixa)" 2 'fora da ordem fixa' "${TMP}/ordem.md"
  printf '# vazio\n' > "${TMP}/vazio.md"
  expect "lint playbook VAZIO ⇒ exit 2 (seções ausentes + 0 ativos)" 2 'sem NENHUM bullet ativo' "${TMP}/vazio.md"

  # VERDES
  expect "lint fixture VÁLIDA ⇒ exit 0" 0 '5 ativos, 1 tombstones' "${FX}/playbook-valido.md"
  expect "--grep termo_fixture ⇒ exit 0 e LM-001" 0 '^LM-001' --grep termo_fixture "${FX}/playbook-valido.md"
  expect "--anti-collapse válido×DELTA-OK (3 novos, contadores, 1 tombstone=20%) ⇒ exit 0" 0 'anti-collapse OK' --anti-collapse "${FX}/playbook-valido.md" "${FX}/playbook-delta-ok.md"
  expect "--anti-collapse arquivo idêntico ⇒ exit 0" 0 '0 sumiram, 0' --anti-collapse "${FX}/playbook-valido.md" "${FX}/playbook-valido.md"
  # R3 (review): caso-limite EXATO — HEAD com 5 IDs (sem o tombstone), staged move 1 para Tombstones = 20% ⇒ deve PASSAR
  # (um limiar com ">=" em vez de ">" bloquearia aqui e passaria nos demais casos).
  grep -v '^- \[LM-006\]' "${FX}/playbook-valido.md" > "${TMP}/head5.md"
  awk '/^- \[LM-005\]/ { skip=1; next } skip && /^  / { next } { skip=0; print } END { print "- [LM-005] ☠ 2026-09-03 :: promovido (teste do limite)" }' "${TMP}/head5.md" > "${TMP}/staged5.md"
  expect "--anti-collapse limite EXATO 1/5 = 20% ⇒ exit 0 (pega off-by-one >=)" 0 '1 \(20%\) alterados' --anti-collapse "${TMP}/head5.md" "${TMP}/staged5.md"
  # e 2/5 = 40% ⇒ bloqueia
  awk '/^- \[LM-00[45]\]/ { skip=1; next } skip && /^  / { next } { skip=0; print } END { print "- [LM-004] ☠ 2026-09-03 :: x"; print "- [LM-005] ☠ 2026-09-03 :: y" }' "${TMP}/head5.md" > "${TMP}/staged5b.md"
  expect "--anti-collapse 2/5 = 40% ⇒ exit 1" 1 '40%' --anti-collapse "${TMP}/head5.md" "${TMP}/staged5b.md"
  # P2 (review pós-build): continuação reescrita conta como alteração de conteúdo
  awk '/^  \*\*Do instead:\*\* rejeitar/ { print "  **Do instead:** CONTINUAÇÃO REESCRITA."; next } { print }' "${TMP}/head5.md" > "${TMP}/staged5c.md"
  expect "--anti-collapse só CONTINUAÇÃO de LM-005 reescrita (1/5) ⇒ conta como alterado (20%)" 0 '1 \(20%\) alterados' --anti-collapse "${TMP}/head5.md" "${TMP}/staged5c.md"

  if [ "${fails}" -gt 0 ]; then printf '🔴 self-test: %d falha(s) — o lint NÃO está provando o que promete\n' "${fails}" >&2; return 2; fi
  echo "🟢 self-test: todos os baselines vermelhos e verdes confirmados"
  return 0
}

# ── dispatch ─────────────────────────────────────────────────────────────────
case "${1:-}" in
  --grep)          [ $# -eq 3 ] || usage; grep_ids "$2" "$3" sup ;;
  --grep-all)      [ $# -eq 3 ] || usage; grep_ids "$2" "$3" all ;;
  --anti-collapse) [ $# -eq 3 ] || usage; anti_collapse "$2" "$3" ;;
  --check-fichas)  [ $# -eq 2 ] || usage; check_fichas "$2" ;;
  --stats)         [ $# -eq 2 ] || usage; stats "$2" ;;
  --self-test)     self_test ;;
  -h|--help|"")    usage ;;
  --*)             usage ;;
  *)               [ $# -eq 1 ] || usage; lint "$1" ;;
esac
