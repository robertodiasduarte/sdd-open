#!/usr/bin/env bash
# contexto-lint.sh — lint, validade e sugestão do CONTEXTO de domínio (sdd/contexto/<slug>.md).
#
# O CONTEXTO é a engenharia reversa de UM domínio (ctx:<slug> de sdd/patterns/dominio.md), gravada
# pelo cartógrafo fresco do passo 1.5 do sdd-define (.agents/skills/sdd-define/references/cartografo.md):
# cabeçalho (ctx · gerado_em · sha · superficies · sup) + 7 seções, toda afirmação com arquivo:linha.
# Este lint prova que ele não apodreceu em silêncio.
#
# Uso:
#   sdd/bin/contexto-lint.sh [--dominio F] [--playbook F] <arquivo.md | pasta>      # lint      exit 0 | 2
#   (sem argumento ⇒ exit 64: nunca lintar um default em silêncio)
#   sdd/bin/contexto-lint.sh [--dominio F] --validade <arquivo.md> [--ref <ref>]     # validade  exit 0 | 1 | 2
#       0 CONTEXTO VALIDO  ⇔ git diff --quiet <sha>..<ref> -- <superficies>
#       1 CONTEXTO VENCIDO + arquivos alterados (informativo; nunca é vermelho de gate)
#       2 [sha-inexistente] (sha ou ref que não existe)
#   sdd/bin/contexto-lint.sh [--dominio F] --sugerir <entrada.md> [--dir D] [--ref R]  # exit 0 | 2
#       heurística do passo 1.5: até 2 ctx: do mapa citados na entrada, camadas de `layers:`, estado de
#       <dir>/<slug>.md e UMA linha "recomendacao: gerar|reusar|pular (motivo)"
#   sdd/bin/contexto-lint.sh --self-test                                              # exit 0 | 2
#   <ref> padrão: origin/<project.default_branch> se existir, senão <project.default_branch> (main).
#
# Classes de erro (texto estável; o self-test exige a classe CERTA, não só exit ≠ 0):
#   cabecalho-ausente · secao-ausente · secao-fora-de-ordem · path-morto · sup-ausente ·
#   ctx-desconhecido · lm-morto · validade-vencida (só --validade, exit 1) · sha-inexistente
#   aviso (não muda o exit): superficie-nao-cobre — código citado fora de `superficies:`
#
# Exit: 0 ok · 1 vencido (só --validade) · 2 formato inválido / self-test falhou · 64 erro de uso
#
# Compat: bash 3.2, awk POSIX, grep básico. Sem arrays associativos. ${VAR} com chaves antes de
# não-ASCII. `while read` sempre sobre arquivo terminado em newline. `superficies:` é dividida com
# globbing DESLIGADO (set -f) e passada ao git como argv. A regex de âncora e a resolução de caminho
# são iguais às de sdd/bin/patterns-lint.sh: extensão nova entra nos dois.
set -uo pipefail
export LC_ALL=C

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

CONTEXTO_DIR_DEFAULT="sdd/contexto"
DOMINIO="sdd/patterns/dominio.md"
PLAYBOOK="sdd/playbook.md"
FIXTURES="sdd/fixtures/contexto"
LIMIAR_TERMOS=2
MAX_DOMINIOS=2
EXT='ts|tsx|js|jsx|mjs|cjs|sql|md|php|sh|py|go|rb|rs|java|kt|cs|yaml|yml|toml|json|tsv|css|html'

CHAVES="ctx
gerado_em
sha
superficies
sup"

SECOES="Escopo
Dados
Operações
Interfaces
Regras vigentes
Landmines
Histórico SDD"

usage() { sed -n '2,30p' "${SELF}" >&2; exit 64; }

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

erros=0
avisos=0
primeira_classe=""
erro()  { printf '  🛑 [%s] %s\n' "$1" "$2"; erros=$((erros + 1)); [ -n "${primeira_classe}" ] || primeira_classe="$1"; }
aviso() { printf '  ⚠️  %s\n' "$1"; avisos=$((avisos + 1)); }

conserto() { # $1 = classe ⇒ o que fazer, em palavras
  case "$1" in
    cabecalho-ausente)   echo "escreva as 5 linhas do cabeçalho (ctx, gerado_em, sha, superficies, sup) antes da 1ª seção" ;;
    secao-ausente)       echo "acrescente a seção que falta, mesmo vazia (as 7 seções estão no brief do cartógrafo)" ;;
    secao-fora-de-ordem) echo "reordene as seções: Escopo, Dados, Operações, Interfaces, Regras vigentes, Landmines, Histórico SDD" ;;
    path-morto)          echo "cite o caminho atual (o arquivo mudou de lugar ou encolheu) ou tire a linha; ou gere o CONTEXTO de novo" ;;
    sup-ausente)         echo "ponha na linha sup: os termos do domínio entre crases, como no playbook" ;;
    ctx-desconhecido)    echo "use um ctx: que exista em sdd/patterns/dominio.md, ou acrescente o bloco ### ctx:<slug> lá" ;;
    lm-morto)            echo "tire a citação da landmine aposentada ou inexistente; rode playbook-lint.sh --grep de novo" ;;
    *)                   echo "corrija o que a linha acima aponta e rode de novo" ;;
  esac
}

# ── cabeçalho = tudo antes da 1ª linha "## " ─────────────────────────────────
cabecalho() { awk '/^## /{exit} {print}' "$1"; }
valor() { cabecalho "$1" | grep "^$2: " | head -1 | sed "s/^$2: //"; }

checa_cabecalho() {
  local f="$1" nome="$2" k n c
  cabecalho "${f}" > "${TMP}/cab.txt"
  printf '%s\n' "${CHAVES}" > "${TMP}/chaves.txt"
  local pos ultima=0 ordem=1
  while IFS= read -r k; do
    [ -n "${k}" ] || continue
    pos=$(grep -nE "^${k}: ." "${TMP}/cab.txt" | head -1 | cut -d: -f1)
    if [ -z "${pos}" ]; then erro "cabecalho-ausente" "${nome}: falta a linha '${k}:' antes da 1ª seção"; continue; fi
    [ "${pos}" -gt "${ultima}" ] || ordem=0
    ultima="${pos}"
  done < "${TMP}/chaves.txt"
  [ "${ordem}" -eq 1 ] || erro "cabecalho-ausente" "${nome}: as linhas do cabeçalho estão fora da ordem (ctx, gerado_em, sha, superficies, sup)"
  # superficies: pathspecs crus (sem crase), e cada um casa ≥ 1 arquivo versionado — senão o --validade
  # compara o vazio e o CONTEXTO nunca vence
  local sups spec
  sups=$(grep '^superficies: ' "${TMP}/cab.txt" | head -1 | sed 's/^superficies: //')
  if [ -n "${sups}" ]; then
    case "${sups}" in *'`'*) erro "cabecalho-ausente" "${nome}: 'superficies:' leva caminhos crus, sem crase (as crases são da linha sup:)" ;; esac
    set -f
    for spec in ${sups}; do
      case "${spec}" in *'`'*) continue ;; esac
      [ -n "$(git ls-files -- "${spec}" 2>/dev/null | head -1)" ] || erro "path-morto" "${nome}: 'superficies:' tem '${spec}', que não casa nenhum arquivo versionado (o --validade não veria mudança nele)"
    done
    set +f
  fi
  if grep -q '^sha: ' "${TMP}/cab.txt"; then
    grep -qE '^sha: [0-9a-f]{7,40}$' "${TMP}/cab.txt" || erro "cabecalho-ausente" "${nome}: 'sha:' não é hex de 7 a 40 caracteres"
  fi
  if grep -q '^gerado_em: ' "${TMP}/cab.txt"; then
    grep -qE '^gerado_em: [0-9]{4}-[0-9]{2}-[0-9]{2}$' "${TMP}/cab.txt" || erro "cabecalho-ausente" "${nome}: 'gerado_em:' não é AAAA-MM-DD"
  fi
  if grep -q '^sup: ' "${TMP}/cab.txt"; then
    # ao menos um termo de verdade entre crases (crases vazias ou só com espaço não contam)
    n=$(grep '^sup: ' "${TMP}/cab.txt" | head -1 | grep -cE '`[^`[:space:]][^`]*`')
    [ "${n}" -ge 1 ] || erro "sup-ausente" "${nome}: 'sup:' sem termo entre crases (formato do playbook: sup: \`t1\` \`t2\`)"
  fi
  c=$(grep '^ctx: ' "${TMP}/cab.txt" | head -1 | sed 's/^ctx: //')
  if [ -n "${c}" ]; then
    [ -f "${DOMINIO}" ] || { erro "ctx-desconhecido" "${nome}: ${DOMINIO} ausente, impossível validar '${c}'"; return; }
    grep -qxF "### ${c}" "${DOMINIO}" || erro "ctx-desconhecido" "${nome}: '${c}' não é um '### ctx:<slug>' de ${DOMINIO}"
  fi
}

# ── seções: presença e ordem (cercas ignoradas) ──────────────────────────────
checa_secoes() {
  local f="$1" nome="$2" s pos ultima_pos ordem_ok
  awk '/^```/{b=!b;next} !b && /^## /' "${f}" | sed -E 's/^## //' > "${TMP}/achadas.txt"
  printf '%s\n' "${SECOES}" > "${TMP}/esperadas.txt"
  ultima_pos=0; ordem_ok=1
  while IFS= read -r s; do
    [ -n "${s}" ] || continue
    pos=$(grep -nxF "${s}" "${TMP}/achadas.txt" 2>/dev/null | head -1 | cut -d: -f1)
    if [ -z "${pos}" ]; then erro "secao-ausente" "${nome}: falta a seção '## ${s}'"; continue; fi
    if [ "${pos}" -lt "${ultima_pos}" ]; then ordem_ok=0; fi
    ultima_pos="${pos}"
  done < "${TMP}/esperadas.txt"
  [ "${ordem_ok}" -eq 1 ] || erro "secao-fora-de-ordem" "${nome}: seções fora da ordem (Escopo → Dados → Operações → Interfaces → Regras vigentes → Landmines → Histórico SDD)"
}

# ── resolução de caminho (igual à de patterns-lint.sh) ──────────────────────
resolve_path() {
  local p="$1"
  p="${p#./}"
  case "${p}" in ../*) p="${p#../}" ;; esac
  [ -f "${p}" ] && printf '%s' "${p}"
}
resolve_basename() { # só o nome do arquivo: casamento ÚNICO entre os arquivos versionados
  local nome="$1" hits
  hits=$(git ls-files 2>/dev/null | awk -v n="${nome}" '{ b=$0; sub(/.*\//, "", b); if (b == n) print }' | head -2)
  [ "$(printf '%s\n' "${hits}" | grep -c .)" -eq 1 ] || return 0
  printf '%s' "${hits}"
}

# ── caminhos citados: existem e a linha cabe (a linha superficies: fica de fora) ─
checa_paths() {
  local f="$1" nome="$2" tok path linha total real
  grep -v '^superficies: ' "${f}" | grep -oE "[A-Za-z0-9_./-]+\.(${EXT})(:[0-9]+)?" | sort -u > "${TMP}/paths.txt"
  printf '\n' >> "${TMP}/paths.txt"
  while IFS= read -r tok; do
    [ -n "${tok}" ] || continue
    case "${tok}" in
      *:*) path="${tok%%:*}"; linha="${tok##*:}" ;;
      *)   path="${tok}"; linha="" ;;
    esac
    case "${path}" in
      */*) : ;;
      *)
        [ -n "${linha}" ] || continue
        real=$(resolve_basename "${path}")
        if [ -z "${real}" ]; then erro "path-morto" "${nome}: a âncora '${path}:${linha}' não aponta para um arquivo único do repositório"; continue; fi
        total=$(awk 'END { print NR }' "${real}")   # awk conta a última linha sem quebra final; wc -l não
        [ "${linha}" -ge 1 ] && [ "${linha}" -le "${total}" ] || erro "path-morto" "${nome}: cita '${path}:${linha}', mas ${real} tem ${total} linhas"
        continue ;;
    esac
    case "${path}" in *'<'*|*'>'*|/*) continue ;; esac
    real=$(resolve_path "${path}")
    if [ -z "${real}" ]; then erro "path-morto" "${nome}: cita '${path}', que não existe no repositório"; continue; fi
    if [ -n "${linha}" ]; then
      total=$(awk 'END { print NR }' "${real}")   # awk conta a última linha sem quebra final; wc -l não
      [ "${linha}" -ge 1 ] && [ "${linha}" -le "${total}" ] || erro "path-morto" "${nome}: cita '${path}:${linha}', mas ${real} tem ${total} linhas"
    fi
  done < "${TMP}/paths.txt"
}

# ── LM-nnn: existe no playbook e está ATIVO (fora de ## Tombstones) ──────────
checa_landmines() {
  local f="$1" nome="$2" id
  grep -oE 'LM-[0-9]{3}' "${f}" | sort -u > "${TMP}/lms.txt"
  [ -s "${TMP}/lms.txt" ] || return 0
  [ -f "${PLAYBOOK}" ] || { erro "lm-morto" "${nome}: playbook '${PLAYBOOK}' ausente, impossível validar LM-nnn"; return; }
  awk '/^## Tombstones/{t=1} t' "${PLAYBOOK}" > "${TMP}/tomb.txt"
  printf '\n' >> "${TMP}/lms.txt"
  while IFS= read -r id; do
    [ -n "${id}" ] || continue
    if ! grep -qF "[${id}]" "${PLAYBOOK}"; then erro "lm-morto" "${nome}: cita ${id}, que não existe em ${PLAYBOOK}"
    elif grep -qF "[${id}]" "${TMP}/tomb.txt"; then erro "lm-morto" "${nome}: cita ${id}, que está aposentado (## Tombstones)"; fi
  done < "${TMP}/lms.txt"
}

# ── superficies: cobrem todo arquivo de CÓDIGO citado? (aviso) ───────────────
# Código = caminho citado que não é .md e não está nas pastas de documento do método (sdd/features,
# reports, reviews, handoffs, patterns, contexto, kb). Fora de `superficies:`, ele pode mudar sem o
# --validade acusar.
checa_superficies() {
  local f="$1" nome="$2" sups p cob spec
  sups=$(valor "${f}" superficies); [ -n "${sups}" ] || return 0
  grep -v '^superficies: ' "${f}" | grep -oE "[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.(${EXT})" \
    | grep -vE '\.md$|^sdd/(features|reports|reviews|handoffs|patterns|contexto|kb)/' | sort -u > "${TMP}/cod.txt"
  printf '\n' >> "${TMP}/cod.txt"
  set -f; set -- ${sups}; set +f
  while IFS= read -r p; do
    [ -n "${p}" ] || continue
    [ -e "${p}" ] || continue
    cob=0
    for spec in "$@"; do
      case "${p}" in ${spec}|${spec}/*) cob=1; break ;; esac
    done
    [ "${cob}" -eq 1 ] || aviso "${nome}: '${p}' é citado mas está fora de 'superficies:' (a validade não vê mudança nele) [superficie-nao-cobre]"
  done < "${TMP}/cod.txt"
}

lint_arquivo() {
  local f="$1" nome; nome=$(basename "${f}")
  checa_cabecalho    "${f}" "${nome}"
  checa_secoes       "${f}" "${nome}"
  checa_paths        "${f}" "${nome}"
  checa_landmines    "${f}" "${nome}"
  checa_superficies  "${f}" "${nome}"
}

rodar_lint() {  # $1 = arquivo ou pasta
  local alvo="$1" f base n=0
  if [ -f "${alvo}" ]; then
    printf '%s\n' "${alvo}" > "${TMP}/arquivos.txt"
  elif [ -d "${alvo}" ]; then
    ls "${alvo}"/*.md > "${TMP}/arquivos.txt" 2>/dev/null
  else
    echo "arquivo ou pasta inexistente: ${alvo}" >&2; exit 64
  fi
  printf '\n' >> "${TMP}/arquivos.txt"
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    base=$(basename "${f}")
    [ "${base}" = "README.md" ] && continue
    lint_arquivo "${f}"
    n=$((n + 1))
  done < "${TMP}/arquivos.txt"
  if [ "${erros}" -gt 0 ]; then
    printf '🛑 contexto-lint: %d erro(s), %d aviso(s) em %d CONTEXTO(s)\n' "${erros}" "${avisos}" "${n}"
    printf 'RESULTADO: VERMELHO\n→ %s.\n' "$(conserto "${primeira_classe}")"
    exit 2
  fi
  printf '✅ contexto-lint: %d CONTEXTO(s) OK, %d aviso(s)\n' "${n}" "${avisos}"
  printf 'RESULTADO: VERDE\n→ o CONTEXTO pode ser citado no DEFINE.\n'
  exit 0
}

# ── ref padrão: origin/<default_branch> se existir, senão <default_branch> ───
ref_padrao() {
  local db=""
  if [ -f sdd/config.yaml ]; then
    db=$(awk '/^project:/{p=1;next} /^[^[:space:]#]/{p=0} p && /^[[:space:]]+default_branch:/{sub(/^[[:space:]]+default_branch:[[:space:]]*/, ""); gsub(/["'"'"']/, ""); sub(/[[:space:]]+#.*$/, ""); print; exit}' sdd/config.yaml)
  fi
  [ -n "${db}" ] || db=main
  if git rev-parse --verify -q "origin/${db}^{commit}" >/dev/null 2>&1; then printf 'origin/%s' "${db}"; else printf '%s' "${db}"; fi
}

# ── --validade: git diff <sha>..<ref> -- <superficies> ───────────────────────
validade() {  # $1=arquivo $2=ref ⇒ 0 valido | 1 vencido | 2 sha-inexistente/cabeçalho
  local f="$1" ref="$2" sha sups nome; nome=$(basename "${f}")
  sha=$(valor "${f}" sha); sups=$(valor "${f}" superficies)
  [ -n "${sha}" ] || { erro "cabecalho-ausente" "${nome}: sem linha 'sha:'"; return 2; }
  [ -n "${sups}" ] || { erro "cabecalho-ausente" "${nome}: sem linha 'superficies:'"; return 2; }
  case "${sups}" in *'`'*) erro "cabecalho-ausente" "${nome}: 'superficies:' com crase não é pathspec; a validade não mede nada assim"; return 2 ;; esac
  git cat-file -e "${sha}^{commit}" 2>/dev/null || { erro "sha-inexistente" "${nome}: o sha '${sha}' não existe neste repositório"; return 2; }
  git rev-parse --verify -q "${ref}^{commit}" >/dev/null 2>&1 || { erro "sha-inexistente" "${nome}: a ref '${ref}' não existe neste repositório (use --ref)"; return 2; }
  set -f; set -- ${sups}; set +f
  # 1º o diff: arquivo apagado (vazio, binário ou não) depois do sha é VENCIDO. Só sem diff, um pathspec que
  # não casa nada no sha nem no índice é erro: a validade não mediria nada.
  if git diff --quiet "${sha}..${ref}" -- "$@"; then
    if [ -z "$(git grep -l -e '' "${sha}" -- "$@" 2>/dev/null | head -1)" ] && [ -z "$(git ls-files -- "$@" 2>/dev/null | head -1)" ]; then
      erro "path-morto" "${nome}: 'superficies:' não casa nenhum arquivo versionado; a validade não mediria nada"; return 2
    fi
    printf 'CONTEXTO VALIDO (%s..%s, %d pathspec)\n' "$(printf '%s' "${sha}" | cut -c1-7)" "${ref}" "$#"; return 0
  fi
  printf 'CONTEXTO VENCIDO (%s..%s): superfícies alteradas desde o sha:\n' "$(printf '%s' "${sha}" | cut -c1-7)" "${ref}"
  git diff --name-only "${sha}..${ref}" -- "$@" | head -20 | sed 's/^/  /'
  printf '  🛑 [validade-vencida] %s: gere de novo (passo 1.5 do sdd-define ⇒ gerar)\n' "${nome}"
  return 1
}

# ── camadas de layers: (sdd/config.yaml) citadas na entrada ──────────────────
camadas_da_entrada() { # $1=entrada ⇒ imprime "N nome1 nome2"
  local input="$1" nome globs g pref n=0 lista=""
  [ -f sdd/config.yaml ] || { echo "0"; return; }
  awk '/^layers:/{p=1;next} /^[^[:space:]#]/{p=0} p && /^[[:space:]]+[A-Za-z0-9_-]+:/{
         k=$0; sub(/^[[:space:]]+/, "", k); v=k; sub(/:.*/, "", k); sub(/^[^:]*:[[:space:]]*/, "", v)
         sub(/[[:space:]]+#.*$/, "", v); gsub(/["'"'"']/, "", v); gsub(/,/, " ", v); print k "\t" v }' sdd/config.yaml > "${TMP}/layers.tsv"
  printf '\n' >> "${TMP}/layers.tsv"
  while IFS="$(printf '\t')" read -r nome globs; do
    [ -n "${nome}" ] || continue
    [ -n "$(printf '%s' "${globs}" | tr -d '[:space:]')" ] || continue
    if grep -qiwF -- "${nome}" "${input}"; then n=$((n + 1)); lista="${lista} ${nome}"; continue; fi
    set -f
    for g in ${globs}; do
      pref="${g%%\**}"
      if [ "${#pref}" -ge 3 ] && grep -qF -- "${pref}" "${input}"; then n=$((n + 1)); lista="${lista} ${nome}"; break; fi
    done
    set +f
  done < "${TMP}/layers.tsv"
  printf '%s%s' "${n}" "${lista}"
}

# ── --sugerir: heurística do passo 1.5 ───────────────────────────────────────
termo_fraco() {  # sem _ - . / e com menos de 6 caracteres ⇒ fraco (nota, item…)
  case "$1" in *_*|*-*|*.*|*/*) return 1 ;; esac
  [ "${#1}" -lt 6 ]
}
sugerir() {  # $1=entrada $2=dir $3=ref
  local input="$1" dir="$2" ref="$3" cam ncam nomes_cam
  cam=$(camadas_da_entrada "${input}"); ncam="${cam%% *}"; nomes_cam="${cam#"${ncam}"}"; nomes_cam="${nomes_cam# }"
  printf 'CONTEXTO_SUGERIR entrada=%s camadas=%s (%s) dir=%s ref=%s\n' "${input}" "${ncam}" "${nomes_cam}" "${dir}" "${ref}"
  if [ ! -f "${DOMINIO}" ]; then
    printf 'recomendacao: pular (sem %s)\n' "${DOMINIO}"
    printf 'RESULTADO: PULAR\n→ o Define segue sem CONTEXTO; para ter o mapa de domínios, veja sdd/patterns/README.md.\n'
    return 0
  fi
  # termos por ctx: linhas **Âncoras:** e sup: do bloco ### ctx:<slug>
  awk '
    /^### ctx:/ { c=substr($2,5); ordem[c]=++o; next }
    /^#{1,3} / { c="" }
    c!="" && (/^\*\*Âncoras:\*\*/ || /^sup: /) {
      s=$0; while (match(s, /`[^`]+`/)) { t=substr(s, RSTART+1, RLENGTH-2); gsub(/\*/, "", t); print c "\t" t "\t" ordem[c]; s=substr(s, RSTART+RLENGTH) }
    }
  ' "${DOMINIO}" | sort -u > "${TMP}/termos.tsv"
  : > "${TMP}/hits.tsv"
  local c t o
  printf '\n' >> "${TMP}/termos.tsv"
  while IFS="$(printf '\t')" read -r c t o; do
    [ -n "${c}" ] || continue
    termo_fraco "${t}" && continue
    grep -qiF -- "${t}" "${input}" && printf '%s\t%s\t%s\n' "${c}" "${t}" "${o}" >> "${TMP}/hits.tsv"
  done < "${TMP}/termos.tsv"
  # candidatos: ≥ LIMIAR_TERMOS termos distintos; ordem por contagem, empate pela ordem do mapa; no máximo MAX_DOMINIOS
  awk -F'\t' '{ n[$1]++; o[$1]=$3; if (n[$1]<=4) l[$1]=(l[$1]==""?$2:l[$1] ", " $2) } END { for (c in n) printf "%d\t%d\t%s\t%s\n", n[c], o[c], c, l[c] }' "${TMP}/hits.tsv" \
    | sort -t"$(printf '\t')" -k1,1nr -k2,2n > "${TMP}/cand.tsv"
  printf '\n' >> "${TMP}/cand.tsv"
  local ncand=0 n lista estado arq principal="" principal_estado="" outros=""
  while IFS="$(printf '\t')" read -r n o c lista; do
    [ -n "${c}" ] || continue
    [ "${n}" -ge "${LIMIAR_TERMOS}" ] || continue
    [ "${ncand}" -lt "${MAX_DOMINIOS}" ] || break
    ncand=$((ncand + 1)); arq="${dir}/${c}.md"
    if [ ! -f "${arq}" ]; then estado="ausente"
    else
      ( erros=0; validade "${arq}" "${ref}" >/dev/null 2>&1 ); case $? in 0) estado="valido" ;; *) estado="vencido" ;; esac
    fi
    if [ -z "${principal}" ]; then principal="${c}"; principal_estado="${estado}"; else outros="${outros} ctx:${c}(${estado})"; fi
    printf 'ctx:%s termos=%d (%s) estado=%s arquivo=%s\n' "${c}" "${n}" "${lista}" "${estado}" "${arq}"
  done < "${TMP}/cand.tsv"
  if [ "${ncand}" -eq 0 ]; then
    printf '0 dominios inferidos (nenhum ctx: com %d ou mais termos de %s na entrada)\n' "${LIMIAR_TERMOS}" "${DOMINIO}"
    printf 'recomendacao: pular (nenhum domínio do mapa citado no pedido)\n'
    printf 'RESULTADO: PULAR\n→ o Define segue sem CONTEXTO.\n'
    return 0
  fi
  [ -n "${outros}" ] && outros="; outros:${outros}"
  if [ "${principal_estado}" = "valido" ]; then
    printf 'recomendacao: reusar (ctx:%s valido%s)\n' "${principal}" "${outros}"
    printf 'RESULTADO: REUSAR\n→ cite %s/%s.md no DEFINE.\n' "${dir}" "${principal}"
  else
    printf 'recomendacao: gerar (ctx:%s %s%s)\n' "${principal}" "${principal_estado}" "${outros}"
    printf 'RESULTADO: GERAR\n→ despache o cartógrafo para ctx:%s (passo 1.5 do sdd-define).\n' "${principal}"
  fi
  return 0
}

# ── --self-test: VERMELHOS antes dos VERDES ─────────────────────────────────
self_test() {
  local fails=0 out rc caso fx classe ign DX PX
  DX="${FIXTURES}/dominio.md"; PX="${FIXTURES}/playbook.md"
  echo "self-test (bash) — fixtures em ${FIXTURES}/"
  git rev-parse -q --verify HEAD >/dev/null 2>&1 || { echo "🛑 o self-test precisa de um commit (âncoras e superficies: são conferidas contra os arquivos versionados): faça o 1º commit e rode de novo" >&2; return 64; }
  [ -n "$(git ls-files -- "${FIXTURES}" 2>/dev/null | head -1)" ] || { echo "🛑 o self-test precisa das fixtures versionadas (âncoras e superficies: são conferidas contra os arquivos versionados): commite ${FIXTURES}/ e rode de novo" >&2; return 64; }
  [ -d "${FIXTURES}" ] || { echo "🛑 fixtures ausentes em ${FIXTURES} (o init só as copia na 1ª instalação; copie a pasta do pacote)" >&2; return 64; }
  ign=$(git check-ignore "${FIXTURES}"/*.md "${FIXTURES}"/app/* 2>/dev/null | wc -l | tr -d ' ')
  if [ "${ign}" = "0" ]; then echo "  ✅ nenhuma fixture casada pelo .gitignore"
  else echo "  🛑 ${ign} fixture(s) ignoradas pelo git: o self-test não viajaria"; fails=$((fails + 1)); fi

  echo "── VERMELHOS (cada fixture falha pela SUA classe) ──"
  cat > "${TMP}/casos.txt" <<'CASOS'
sem-cabecalho:cabecalho-ausente
sem-secao:secao-ausente
secao-fora-de-ordem:secao-fora-de-ordem
path-morto:path-morto
linha-alem-do-fim:path-morto
sup-ausente:sup-ausente
ctx-desconhecido:ctx-desconhecido
lm-morto:lm-morto
cabecalho-fora-de-ordem:cabecalho-ausente
superficies-com-crase:cabecalho-ausente
superficies-sem-arquivo:path-morto
CASOS
  printf '\n' >> "${TMP}/casos.txt"
  while IFS= read -r caso; do
    [ -n "${caso}" ] || continue
    fx="${caso%%:*}"; classe="${caso##*:}"
    [ -f "${FIXTURES}/${fx}.md" ] || { echo "  🛑 fixture ausente: ${FIXTURES}/${fx}.md"; fails=$((fails + 1)); continue; }
    out=$(bash "${SELF}" --dominio "${DX}" --playbook "${PX}" "${FIXTURES}/${fx}.md" 2>&1); rc=$?
    if [ "${rc}" -ne 2 ]; then echo "  🛑 ${fx}: esperado exit 2, veio ${rc}"; fails=$((fails + 1))
    elif ! printf '%s' "${out}" | grep -qF "[${classe}]"; then
      echo "  🛑 ${fx}: saiu 2 pela classe ERRADA (esperava ${classe}) — $(printf '%s' "${out}" | grep -oE '\[[a-z-]+\]' | head -1)"; fails=$((fails + 1))
    else echo "  ✅ ${fx} ⇒ exit 2 [${classe}]"; fi
  done < "${TMP}/casos.txt"

  echo "── VALIDADE (repositório temporário: c1 cria a.md · c2 altera a.md e cria b.md) ──"
  local repo="${TMP}/repo" c1 c2
  mkdir -p "${repo}"; git init -q "${repo}"
  g() { git -C "${repo}" -c user.email=self-test@example.com -c user.name=self-test -c core.hooksPath=/dev/null -c commit.gpgsign=false "$@"; }
  echo v1 > "${repo}/a.md"; g add a.md; g commit -q -m c1; c1=$(g rev-parse HEAD)
  echo v2 > "${repo}/a.md"; echo b > "${repo}/b.md"; g add a.md b.md; g commit -q -m c2; c2=$(g rev-parse HEAD)
  [ -f "${FIXTURES}/validade-template.md" ] || { echo "  🛑 fixture ausente: validade-template.md"; fails=$((fails + 1)); }
  sed "s/__SHA__/${c2}/" "${FIXTURES}/validade-template.md" > "${repo}/ctx-valido.md"
  sed "s/__SHA__/${c1}/" "${FIXTURES}/validade-template.md" > "${repo}/ctx-vencido.md"
  sed "s/__SHA__/0000000/" "${FIXTURES}/validade-template.md" > "${repo}/ctx-sha.md"
  out=$(cd "${repo}" && bash "${SELF}" --validade ctx-vencido.md --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 1 ] && printf '%s' "${out}" | grep -qF 'CONTEXTO VENCIDO' && printf '%s' "${out}" | grep -qF 'a.md' && printf '%s' "${out}" | grep -qF '[validade-vencida]'; then
    echo "  ✅ sha=c1 ⇒ exit 1 CONTEXTO VENCIDO nomeando a.md"
  else echo "  🛑 sha=c1: esperado exit 1 'CONTEXTO VENCIDO' + a.md, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(cd "${repo}" && bash "${SELF}" --validade ctx-sha.md --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 2 ] && printf '%s' "${out}" | grep -qF '[sha-inexistente]'; then echo "  ✅ sha=0000000 ⇒ exit 2 [sha-inexistente]"
  else echo "  🛑 sha inexistente: esperado exit 2 [sha-inexistente], veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(cd "${repo}" && bash "${SELF}" --validade ctx-valido.md --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF 'CONTEXTO VALIDO'; then echo "  ✅ sha=c2 ⇒ exit 0 CONTEXTO VALIDO"
  else echo "  🛑 sha=c2: esperado exit 0 'CONTEXTO VALIDO', veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(cd "${repo}" && bash "${SELF}" --validade ctx-valido.md --ref nao-existe 2>&1); rc=$?
  if [ "${rc}" -eq 2 ] && printf '%s' "${out}" | grep -qF '[sha-inexistente]'; then echo "  ✅ ref inexistente ⇒ exit 2 [sha-inexistente]"
  else echo "  🛑 ref inexistente: esperado exit 2, veio ${rc}: ${out}"; fails=$((fails + 1)); fi

  echo "── SUGERIR (entrada × estado do CONTEXTO) ──"
  local IN2="${FIXTURES}/INPUT_FIXTURE_PEDIDOS.md" IN0="${FIXTURES}/INPUT_FIXTURE_SEM_DOMINIO.md" head_sha
  mkdir -p "${TMP}/vazio" "${TMP}/dir-ok"
  out=$(bash "${SELF}" --dominio "${DX}" --sugerir "${IN2}" --dir "${TMP}/vazio" --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -q '^ctx:pedidos ' && printf '%s' "${out}" | grep -qF 'estado=ausente' \
     && printf '%s' "${out}" | grep -qF 'recomendacao: gerar'; then
    echo "  ✅ entrada de pedidos, pasta vazia ⇒ ctx:pedidos ausente ⇒ gerar"
  else echo "  🛑 entrada de pedidos, pasta vazia: esperado ctx:pedidos/ausente/gerar, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  if [ "$(printf '%s\n' "${out}" | grep -c '^ctx:')" -le "${MAX_DOMINIOS}" ]; then echo "  ✅ no máximo ${MAX_DOMINIOS} domínios"
  else echo "  🛑 mais de ${MAX_DOMINIOS} domínios sugeridos"; fails=$((fails + 1)); fi
  head_sha=$(git rev-parse HEAD)
  sed -e "s/^sha: .*/sha: ${head_sha}/" "${FIXTURES}/valido-completo.md" > "${TMP}/dir-ok/pedidos.md"
  out=$(bash "${SELF}" --dominio "${DX}" --sugerir "${IN2}" --dir "${TMP}/dir-ok" --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF 'estado=valido' && printf '%s' "${out}" | grep -qF 'recomendacao: reusar'; then
    echo "  ✅ entrada de pedidos, CONTEXTO válido (sha=HEAD, ref=HEAD) ⇒ reusar"
  else echo "  🛑 entrada de pedidos, CONTEXTO válido: esperado valido/reusar, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --dominio "${DX}" --sugerir "${IN0}" --dir "${TMP}/vazio" --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF '0 dominios' && printf '%s' "${out}" | grep -qF 'recomendacao: pular'; then
    echo "  ✅ entrada sem domínio ⇒ 0 domínios ⇒ pular"
  else echo "  🛑 entrada sem domínio: esperado 0 dominios/pular, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --dominio "${TMP}/nao-existe.md" --sugerir "${IN2}" --dir "${TMP}/vazio" --ref HEAD 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF 'recomendacao: pular (sem '; then
    echo "  ✅ sem mapa de domínios ⇒ pular, exit 0"
  else echo "  🛑 sem mapa: esperado pular/exit 0, veio ${rc}: ${out}"; fails=$((fails + 1)); fi

  echo "── USO ──"
  out=$(bash "${SELF}" 2>&1); rc=$?
  if [ "${rc}" -eq 64 ] && printf '%s' "${out}" | grep -qi 'uso'; then echo "  ✅ sem argumento ⇒ exit 64 com texto de uso"
  else echo "  🛑 sem argumento ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --flag-que-nao-existe 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ flag desconhecida ⇒ exit 64"; else echo "  🛑 flag desconhecida ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" sdd/contexto-que-nao-existe.md 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ arquivo inexistente ⇒ exit 64"; else echo "  🛑 arquivo inexistente ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --validade sdd/contexto-que-nao-existe.md 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ --validade inexistente ⇒ exit 64"; else echo "  🛑 --validade inexistente ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  # flag sem valor não pode entrar em laço: teto de 5 s
  local pid i
  for caso in "--validade ${FIXTURES}/valido-completo.md --ref" "--sugerir ${FIXTURES}/INPUT_FIXTURE_SEM_DOMINIO.md --dir" "--dominio"; do
    : > "${TMP}/rc-loop.txt"
    ( set -f; bash "${SELF}" ${caso} >/dev/null 2>&1; echo "$?" > "${TMP}/rc-loop.txt" ) & pid=$!
    i=0
    while kill -0 "${pid}" 2>/dev/null && [ "${i}" -lt 50 ]; do sleep 0.1; i=$((i + 1)); done
    if kill -0 "${pid}" 2>/dev/null; then kill -9 "${pid}" 2>/dev/null; echo "  🛑 '${caso##* }' sem valor TRAVOU (laço; esperado 64)"; fails=$((fails + 1))
    else rc=$(cat "${TMP}/rc-loop.txt"); if [ "${rc}" = "64" ]; then echo "  ✅ flag sem valor ('${caso##* }') ⇒ exit 64, sem laço"; else echo "  🛑 flag sem valor ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi; fi
  done

  echo "── VERDES ──"
  out=$(bash "${SELF}" --dominio "${DX}" --playbook "${PX}" "${FIXTURES}/valido-completo.md" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ]; then echo "  ✅ fixture válida ⇒ exit 0"; else echo "  🛑 fixture válida ⇒ ${rc}: ${out}"; fails=$((fails + 1)); fi
  if printf '%s' "${out}" | grep -qF '[superficie-nao-cobre]' && printf '%s' "${out}" | grep -qF 'app/estoque.sql'; then
    echo "  ✅ código citado fora de superficies: ⇒ aviso [superficie-nao-cobre], exit 0"
  else echo "  🛑 aviso superficie-nao-cobre ausente: ${out}"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --dominio "${DX}" --playbook "${PX}" "${FIXTURES}/superficies-nao-e-ancora.md" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ]; then echo "  ✅ glob em superficies: ⇒ exit 0 (pathspec, não âncora)"
  else echo "  🛑 superficies-nao-e-ancora ⇒ ${rc}: ${out}"; fails=$((fails + 1)); fi
  mkdir -p "${TMP}/pasta"; cp "${FIXTURES}/valido-completo.md" "${TMP}/pasta/pedidos.md"; echo "# readme" > "${TMP}/pasta/README.md"
  out=$(bash "${SELF}" --dominio "${DX}" --playbook "${PX}" "${TMP}/pasta" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF '1 CONTEXTO(s) OK'; then echo "  ✅ pasta com README ⇒ exit 0, README ignorado"
  else echo "  🛑 pasta com README ⇒ ${rc}: ${out}"; fails=$((fails + 1)); fi

  if [ "${fails}" -gt 0 ]; then
    printf '🔴 self-test: %d falha(s) — o lint NÃO está provando o que promete\n' "${fails}"
    printf 'RESULTADO: VERMELHO\n→ corrija o lint ou a fixture apontada acima.\n'
    return 2
  fi
  echo "✅ self-test: cada classe vermelha acusa a classe certa; validade nos 3 ramos; sugerir na matriz; verdes verdes."
  printf 'RESULTADO: VERDE\n→ o lint prova o que promete.\n'
  return 0
}

# ── despacho ─────────────────────────────────────────────────────────────────
ORIG="$(pwd -P)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "não é um repositório git" >&2; exit 64; }
cd "${REPO_ROOT}" || exit 64
# caminho dado por quem chamou de uma subpasta: vale relativo a onde ele estava, se existir lá
de_quem_chamou() { case "$1" in /*) printf '%s' "$1" ;; *) if [ -e "${ORIG}/$1" ]; then printf '%s' "${ORIG}/$1"; else printf '%s' "$1"; fi ;; esac; }

if [ $# -eq 0 ]; then
  echo "erro de uso: informe <arquivo.md|pasta> (ex.: ${CONTEXTO_DIR_DEFAULT}), --validade <arquivo> [--ref R], --sugerir <entrada> [--dir D] [--ref R] ou --self-test" >&2
  usage
fi
# opções globais antes do modo (shift 2 só com valor presente: sem valor, shift 2 falha e o laço não anda)
while [ $# -gt 0 ]; do
  case "$1" in
    --dominio)  [ $# -ge 2 ] || { echo "--dominio exige valor" >&2; usage; }; DOMINIO="$(de_quem_chamou "$2")"; shift 2 ;;
    --playbook) [ $# -ge 2 ] || { echo "--playbook exige valor" >&2; usage; }; PLAYBOOK="$(de_quem_chamou "$2")"; shift 2 ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || usage
case "$1" in
  --self-test) self_test; exit $? ;;
  --validade)
    [ $# -ge 2 ] || usage
    ARQ="$(de_quem_chamou "$2")"; REF=""; shift 2
    while [ $# -gt 0 ]; do case "$1" in --ref) [ $# -ge 2 ] || { echo "--ref exige valor" >&2; usage; }; REF="$2"; shift 2 ;; *) echo "flag desconhecida: $1" >&2; usage ;; esac; done
    [ -f "${ARQ}" ] || { echo "arquivo inexistente: ${ARQ}" >&2; exit 64; }
    [ -n "${REF}" ] || REF="$(ref_padrao)"
    validade "${ARQ}" "${REF}"; rc=$?
    case "${rc}" in
      0) printf 'RESULTADO: VALIDO\n→ reuse o CONTEXTO.\n' ;;
      1) printf 'RESULTADO: VENCIDO\n→ gere o CONTEXTO de novo (passo 1.5 do sdd-define).\n' ;;
      *) printf 'RESULTADO: VERMELHO\n→ confira o sha do cabeçalho e a ref (--ref).\n' ;;
    esac
    exit "${rc}" ;;
  --sugerir)
    [ $# -ge 2 ] || usage
    INPUT="$(de_quem_chamou "$2")"; DIR="${CONTEXTO_DIR_DEFAULT}"; REF=""; shift 2
    while [ $# -gt 0 ]; do case "$1" in --dir) [ $# -ge 2 ] || { echo "--dir exige valor" >&2; usage; }; DIR="$(de_quem_chamou "$2")"; shift 2 ;; --ref) [ $# -ge 2 ] || { echo "--ref exige valor" >&2; usage; }; REF="$2"; shift 2 ;; *) echo "flag desconhecida: $1" >&2; usage ;; esac; done
    [ -f "${INPUT}" ] || { echo "entrada inexistente: ${INPUT}" >&2; exit 64; }
    [ -n "${REF}" ] || REF="$(ref_padrao)"
    sugerir "${INPUT}" "${DIR}" "${REF}"; exit $? ;;
  -h|--help) usage ;;
  --*) echo "flag desconhecida: $1" >&2; usage ;;
  *) [ $# -eq 1 ] || { echo "argumento a mais: $2" >&2; usage; }; rodar_lint "$(de_quem_chamou "$1")" ;;
esac
