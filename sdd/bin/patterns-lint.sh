#!/usr/bin/env bash
# patterns-lint.sh — lint dos patterns do projeto (sdd/patterns/): como a casa CONSTRÓI.
#
# O playbook (sdd/playbook.md) guarda o que MORDE; os patterns guardam o esqueleto que se copia. Este
# lint prova que um pattern não apodreceu em silêncio: seções na ordem, todo arquivo:linha citado
# existe, todo LM-nnn está vivo, e a data de validação é legível. Formato: sdd/patterns/README.md.
#
# Uso:
#   sdd/bin/patterns-lint.sh [--playbook F] <pasta>                     # lint da pasta    exit 0 | 2
#   (sem argumento ⇒ exit 64: nunca lintar um default em silêncio)
#   sdd/bin/patterns-lint.sh [--playbook F] --design <DESIGN.md> [<pasta>]  # regime do Design  exit 0 | 2
#   sdd/bin/patterns-lint.sh --self-test                                # exit 0 | 2
#
# Regimes:
#   sem --design : estrutura, caminhos e LM bloqueiam; idade só AVISA.
#   com --design : idade e caminho morto de pattern CITADO no DESIGN bloqueiam (exit 2); os mesmos
#                  defeitos em pattern NÃO citado viram aviso. DESIGN que não cita nada ⇒ aviso + exit 0.
#   Citação = a linha **Pattern:** `patterns/<x>.md §Esqueleto` (validado_em AAAA-MM-DD).
#
# Classes de erro (texto estável; o self-test exige a classe CERTA):
#   secao-ausente · secao-fora-de-ordem · path-morto · lm-morto · validado-vencido
#
# Exit: 0 ok · 2 formato inválido / self-test falhou · 64 erro de uso
#
# Compat: bash 3.2, awk POSIX, grep básico. Sem arrays associativos. ${VAR} com chaves antes de
# não-ASCII. A regex de âncora e a resolução de caminho são iguais às de sdd/bin/contexto-lint.sh.
set -uo pipefail
export LC_ALL=C

SELF="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"

PATTERNS_DIR_DEFAULT="sdd/patterns"
PLAYBOOK="sdd/playbook.md"
FIXTURES="sdd/fixtures/patterns"
IDADE_MAX_DIAS=90
EXT='ts|tsx|js|jsx|mjs|cjs|sql|md|php|sh|py|go|rb|rs|java|kt|cs|yaml|yml|toml|json|tsv|css|html'

SECOES="Quando se aplica
Esqueleto
Checklist de conformidade
Exemplos canônicos
Landmines
Validado em"

usage() { sed -n '2,22p' "${SELF}" >&2; exit 64; }

TMP="$(mktemp -d)"
trap 'rm -rf "${TMP}"' EXIT

erros=0
avisos=0
primeira_classe=""
erro()  { printf '  🛑 [%s] %s\n' "$1" "$2"; erros=$((erros + 1)); [ -n "${primeira_classe}" ] || primeira_classe="$1"; }
aviso() { printf '  ⚠️  %s\n' "$1"; avisos=$((avisos + 1)); }

conserto() {
  case "$1" in
    secao-ausente)       echo "acrescente a seção que falta (as 6 seções estão em sdd/patterns/README.md)" ;;
    secao-fora-de-ordem) echo "reordene: Quando se aplica, Esqueleto, Checklist de conformidade, Exemplos canônicos, Landmines, Validado em" ;;
    path-morto)          echo "cite o caminho e a linha atuais (o arquivo mudou) ou tire a âncora; no DESIGN, cite um pattern que exista" ;;
    lm-morto)            echo "tire a landmine aposentada ou inexistente da seção Landmines" ;;
    validado-vencido)    echo "revalide o esqueleto contra o código e atualize a data em '## Validado em', ou deixe de citá-lo no DESIGN" ;;
    *)                   echo "corrija o que a linha acima aponta e rode de novo" ;;
  esac
}

# ── dias entre uma data AAAA-MM-DD e hoje (BSD date no macOS, GNU no Linux) ──
dias_desde() {
  local d="$1" epoch hoje
  epoch=$(date -j -f '%Y-%m-%d' "${d}" '+%s' 2>/dev/null) \
    || epoch=$(date -d "${d}" '+%s' 2>/dev/null) \
    || { echo -1; return; }
  hoje=$(date '+%s')
  echo $(( (hoje - epoch) / 86400 ))
}

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
  [ "${ordem_ok}" -eq 1 ] || erro "secao-fora-de-ordem" "${nome}: seções fora da ordem (Quando se aplica → Esqueleto → Checklist → Exemplos → Landmines → Validado em)"
}

# ── resolução de caminho (igual à de contexto-lint.sh) ──────────────────────
resolve_path() {
  local p="$1"
  p="${p#./}"
  case "${p}" in ../*) p="${p#../}" ;; esac
  [ -f "${p}" ] && { printf '%s' "${p}"; return; }
  # um pattern cita outro na forma canônica patterns/<x>.md
  case "${p}" in patterns/*) [ -f "sdd/${p}" ] && printf '%s' "sdd/${p}" ;; esac
}
resolve_basename() {
  local nome="$1" hits
  hits=$(git ls-files 2>/dev/null | awk -v n="${nome}" '{ b=$0; sub(/.*\//, "", b); if (b == n) print }' | head -2)
  [ "$(printf '%s\n' "${hits}" | grep -c .)" -eq 1 ] || return 0
  printf '%s' "${hits}"
}

reporta() { # $1=bloqueia(sim|nao) $2=classe $3=mensagem
  if [ "$1" = "sim" ]; then erro "$2" "$3"; else aviso "$3 — não citado no DESIGN, não bloqueia"; fi
}

checa_paths() {
  local f="$1" nome="$2" bloqueia="$3" tok path linha total real
  grep -oE "[A-Za-z0-9_./-]+\.(${EXT})(:[0-9]+)?" "${f}" | sort -u > "${TMP}/paths.txt"
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
        # sem diretório: é âncora (com :linha) ou só menção em prosa (`README.md`), que se ignora
        [ -n "${linha}" ] || continue
        real=$(resolve_basename "${path}")
        if [ -z "${real}" ]; then reporta "${bloqueia}" "path-morto" "${nome}: a âncora '${path}:${linha}' não aponta para um arquivo único do repositório"; continue; fi
        total=$(wc -l < "${real}" | tr -d ' ')
        [ "${linha}" -ge 1 ] && [ "${linha}" -le "${total}" ] || reporta "${bloqueia}" "path-morto" "${nome}: cita '${path}:${linha}', mas ${real} tem ${total} linhas"
        continue ;;
    esac
    case "${path}" in *'<'*|*'>'*|/*) continue ;; esac
    real=$(resolve_path "${path}")
    if [ -z "${real}" ]; then reporta "${bloqueia}" "path-morto" "${nome}: cita '${path}', que não existe no repositório"; continue; fi
    if [ -n "${linha}" ]; then
      total=$(wc -l < "${real}" | tr -d ' ')
      [ "${linha}" -ge 1 ] && [ "${linha}" -le "${total}" ] || reporta "${bloqueia}" "path-morto" "${nome}: cita '${path}:${linha}', mas ${real} tem ${total} linhas"
    fi
  done < "${TMP}/paths.txt"
}

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

checa_validado() {
  local f="$1" nome="$2" citado="$3" data d
  data=$(awk '/^## Validado em/{v=1; next} v && /^## /{exit} v && /[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/{print; exit}' "${f}" \
    | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  if [ -z "${data}" ]; then erro "validado-vencido" "${nome}: '## Validado em' sem data AAAA-MM-DD legível"; return; fi
  d=$(dias_desde "${data}")
  if [ "${d}" -lt 0 ]; then erro "validado-vencido" "${nome}: a data '${data}' não é interpretável"; return; fi
  if [ "${d}" -gt "${IDADE_MAX_DIAS}" ]; then
    if [ "${citado}" = "sim" ]; then
      erro "validado-vencido" "${nome}: citado no DESIGN e validado em ${data} (${d} dias; o limite é ${IDADE_MAX_DIAS})"
    else
      aviso "${nome}: validado em ${data} (${d} dias; o limite é ${IDADE_MAX_DIAS}) — não citado no DESIGN, não bloqueia"
    fi
  fi
}

lint_arquivo() {
  local f="$1" citado="$2" design="$3" nome bloqueia
  nome=$(basename "${f}")
  # sem --design todo caminho morto bloqueia; com --design, só o do pattern CITADO
  if [ -z "${design}" ] || [ "${citado}" = "sim" ]; then bloqueia="sim"; else bloqueia="nao"; fi
  checa_secoes    "${f}" "${nome}"
  checa_paths     "${f}" "${nome}" "${bloqueia}"
  checa_landmines "${f}" "${nome}"
  checa_validado  "${f}" "${nome}" "${citado}"
}

rodar_lint() {
  local dir="$1" design="$2" cit f base citado n=0
  [ -d "${dir}" ] || { echo "pasta inexistente: ${dir}" >&2; exit 64; }
  : > "${TMP}/citados.txt"
  if [ -n "${design}" ]; then
    [ -f "${design}" ] || { echo "DESIGN inexistente: ${design}" >&2; exit 64; }
    # CITAÇÃO ≠ MENÇÃO: só a linha **Pattern:** conta (um caminho de fixture no File Manifest não é citação)
    # só a linha que COMEÇA com **Pattern:** (também como item de lista ou com recuo), fora de cerca ``` ou ~~~:
    # o blockquote de orientação do template (`> **Pattern:** …`) e um exemplo em cerca são menção, não citação
    awk '/^[[:space:]]*(```|~~~)/{f=!f; next} !f && /^[[:space:]]*([-*+]|[0-9]+\.)?[[:space:]]*\*\*Pattern:?\*\*:?/' "${design}" \
      | grep -oE 'patterns/[A-Za-z0-9_-]+\.md' | sed -E 's#^patterns/##' | sort -u > "${TMP}/citados.txt"
    [ -s "${TMP}/citados.txt" ] || aviso "nenhum pattern citado em $(basename "${design}"): o lint não tem o que exigir"
  fi
  printf '\n' >> "${TMP}/citados.txt"
  # citação ÓRFÃ: o DESIGN cita patterns/x.md e x.md não está na pasta
  while IFS= read -r cit; do
    [ -n "${cit}" ] || continue
    [ -f "${dir}/${cit}" ] || erro "path-morto" "$(basename "${design}") cita patterns/${cit}, que não existe em ${dir}"
  done < "${TMP}/citados.txt"
  ls "${dir}"/*.md > "${TMP}/arquivos.txt" 2>/dev/null
  printf '\n' >> "${TMP}/arquivos.txt"
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    base=$(basename "${f}")
    [ "${base}" = "README.md" ] && continue
    citado="nao"
    if [ -n "${design}" ] && grep -qxF "${base}" "${TMP}/citados.txt"; then citado="sim"; fi
    lint_arquivo "${f}" "${citado}" "${design}"
    n=$((n + 1))
  done < "${TMP}/arquivos.txt"
  if [ "${erros}" -gt 0 ]; then
    printf '🛑 patterns-lint: %d erro(s), %d aviso(s) em %d pattern(s)\n' "${erros}" "${avisos}" "${n}"
    printf 'RESULTADO: VERMELHO\n→ %s.\n' "$(conserto "${primeira_classe}")"
    exit 2
  fi
  printf '✅ patterns-lint: %d pattern(s) OK, %d aviso(s)\n' "${n}" "${avisos}"
  printf 'RESULTADO: VERDE\n→ os patterns podem ser citados.\n'
  exit 0
}

# ── --self-test: VERMELHOS antes dos VERDES ─────────────────────────────────
self_test() {
  local fails=0 ign caso fx classe out rc hoje PX
  PX="sdd/fixtures/contexto/playbook.md"
  hoje=$(date '+%Y-%m-%d')
  echo "self-test (bash) — fixtures em ${FIXTURES}/"
  [ -d "${FIXTURES}" ] || { echo "🛑 fixtures ausentes em ${FIXTURES} (o init só as copia na 1ª instalação; copie a pasta do pacote)" >&2; return 64; }
  [ -f "${PX}" ] || { echo "🛑 playbook de fixture ausente: ${PX}" >&2; return 2; }
  ign=$(git check-ignore "${FIXTURES}"/*.md 2>/dev/null | wc -l | tr -d ' ')
  if [ "${ign}" = "0" ]; then echo "  ✅ nenhuma fixture casada pelo .gitignore"
  else echo "  🛑 ${ign} fixture(s) ignoradas pelo git: o self-test não viajaria"; fails=$((fails + 1)); fi
  # a fixture verde leva a data de hoje: uma data fixa vencia sozinha depois de 90 dias
  verde() { sed "s/__HOJE__/${hoje}/" "${FIXTURES}/valido-completo.md" > "$1"; }
  mkdir -p "${TMP}/ok"; verde "${TMP}/ok/pedidos.md"

  echo "── VERMELHOS (cada fixture falha pela SUA classe) ──"
  cat > "${TMP}/casos.txt" <<'CASOS'
sem-secao:secao-ausente
secao-fora-de-ordem:secao-fora-de-ordem
path-morto:path-morto
lm-morto:lm-morto
linha-alem-do-fim:path-morto
linha-alem-do-fim-basename:path-morto
CASOS
  printf '\n' >> "${TMP}/casos.txt"
  while IFS= read -r caso; do
    [ -n "${caso}" ] || continue
    fx="${caso%%:*}"; classe="${caso##*:}"
    [ -f "${FIXTURES}/${fx}.md" ] || { echo "  🛑 fixture ausente: ${FIXTURES}/${fx}.md"; fails=$((fails + 1)); continue; }
    mkdir -p "${TMP}/solo/${fx}"
    sed "s/__HOJE__/${hoje}/" "${FIXTURES}/${fx}.md" > "${TMP}/solo/${fx}/${fx}.md"
    out=$(bash "${SELF}" --playbook "${PX}" "${TMP}/solo/${fx}" 2>&1); rc=$?
    if [ "${rc}" -ne 2 ]; then echo "  🛑 ${fx}: esperado exit 2, veio ${rc}"; fails=$((fails + 1))
    elif ! printf '%s' "${out}" | grep -qF "[${classe}]"; then
      echo "  🛑 ${fx}: saiu 2 pela classe ERRADA (esperava ${classe}) — $(printf '%s' "${out}" | grep -oE '\[[a-z-]+\]' | head -1)"; fails=$((fails + 1))
    else echo "  ✅ ${fx} ⇒ exit 2 [${classe}]"; fi
  done < "${TMP}/casos.txt"

  mkdir -p "${TMP}/venc"; cp "${FIXTURES}/valido-vencido.md" "${TMP}/venc/pedidos.md"
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_CITA_PEDIDOS.md" "${TMP}/venc" 2>&1); rc=$?
  if [ "${rc}" -eq 2 ] && printf '%s' "${out}" | grep -qF '[validado-vencido]' && printf '%s' "${out}" | grep -qF 'o limite é'; then
    echo "  ✅ vencido CITADO ⇒ exit 2 [validado-vencido], com a data e o limite"
  else echo "  🛑 vencido CITADO: esperado exit 2 [validado-vencido], veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  mkdir -p "${TMP}/pmc"; sed "s/__HOJE__/${hoje}/" "${FIXTURES}/path-morto.md" > "${TMP}/pmc/pedidos.md"
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_CITA_PEDIDOS.md" "${TMP}/pmc" 2>&1); rc=$?
  if [ "${rc}" -eq 2 ] && printf '%s' "${out}" | grep -qF '[path-morto]'; then echo "  ✅ caminho morto CITADO ⇒ exit 2 [path-morto]"
  else echo "  🛑 caminho morto CITADO: esperado exit 2 [path-morto], veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_CITA_INEXISTENTE.md" "${TMP}/ok" 2>&1); rc=$?
  if [ "${rc}" -eq 2 ] && printf '%s' "${out}" | grep -qF 'que não existe em'; then echo "  ✅ DESIGN cita pattern inexistente ⇒ exit 2 [path-morto]"
  else echo "  🛑 DESIGN cita pattern inexistente: esperado exit 2, veio ${rc}: ${out}"; fails=$((fails + 1)); fi

  echo "── USO ──"
  out=$(bash "${SELF}" 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ sem argumento ⇒ exit 64"; else echo "  🛑 sem argumento ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --flag-que-nao-existe 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ flag desconhecida ⇒ exit 64"; else echo "  🛑 flag desconhecida ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" sdd/pasta-que-nao-existe 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ pasta inexistente ⇒ exit 64"; else echo "  🛑 pasta inexistente ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --design sdd/nao-existe.md 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ --design inexistente ⇒ exit 64"; else echo "  🛑 --design inexistente ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --playbook 2>&1); rc=$?
  if [ "${rc}" -eq 64 ]; then echo "  ✅ --playbook sem valor ⇒ exit 64"; else echo "  🛑 --playbook sem valor ⇒ ${rc} (esperado 64)"; fails=$((fails + 1)); fi

  echo "── VERDES ──"
  out=$(bash "${SELF}" --playbook "${PX}" "${TMP}/ok" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ]; then echo "  ✅ fixture válida (data de hoje) ⇒ exit 0"; else echo "  🛑 fixture válida ⇒ ${rc}: ${out}"; fails=$((fails + 1)); fi
  mkdir -p "${TMP}/vnc"; cp "${FIXTURES}/valido-vencido.md" "${TMP}/vnc/estoque.md"; verde "${TMP}/vnc/pedidos.md"
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_CITA_PEDIDOS.md" "${TMP}/vnc" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF '⚠️'; then echo "  ✅ vencido NÃO citado ⇒ exit 0 + aviso"
  else echo "  🛑 vencido NÃO citado: esperado exit 0 com aviso, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  mkdir -p "${TMP}/pmn"; sed "s/__HOJE__/${hoje}/" "${FIXTURES}/path-morto.md" > "${TMP}/pmn/estoque.md"; verde "${TMP}/pmn/pedidos.md"
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_CITA_PEDIDOS.md" "${TMP}/pmn" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF '⚠️'; then echo "  ✅ caminho morto NÃO citado ⇒ exit 0 + aviso"
  else echo "  🛑 caminho morto NÃO citado: esperado exit 0 com aviso, veio ${rc}: ${out}"; fails=$((fails + 1)); fi
  out=$(bash "${SELF}" --playbook "${PX}" --design "${FIXTURES}/DESIGN_FIXTURE_SEM_CITACAO.md" "${TMP}/ok" 2>&1); rc=$?
  if [ "${rc}" -eq 0 ] && printf '%s' "${out}" | grep -qF 'nenhum pattern citado'; then echo "  ✅ DESIGN sem citação ⇒ exit 0 + aviso"
  else echo "  🛑 DESIGN sem citação: esperado exit 0 + aviso, veio ${rc}: ${out}"; fails=$((fails + 1)); fi

  if [ "${fails}" -gt 0 ]; then
    printf '🔴 self-test: %d falha(s) — o lint NÃO está provando o que promete\n' "${fails}"
    printf 'RESULTADO: VERMELHO\n→ corrija o lint ou a fixture apontada acima.\n'
    return 2
  fi
  echo "✅ self-test: cada classe vermelha acusa a classe certa; citado × não citado; verdes verdes."
  printf 'RESULTADO: VERDE\n→ o lint prova o que promete.\n'
  return 0
}

ORIG="$(pwd -P)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "não é um repositório git" >&2; exit 64; }
cd "${REPO_ROOT}" || exit 64
de_quem_chamou() { case "$1" in /*) printf '%s' "$1" ;; *) if [ -e "${ORIG}/$1" ]; then printf '%s' "${ORIG}/$1"; else printf '%s' "$1"; fi ;; esac; }

if [ $# -eq 0 ]; then
  echo "erro de uso: informe a pasta de patterns (ex.: ${PATTERNS_DIR_DEFAULT}), --design <DESIGN.md> ou --self-test" >&2
  usage
fi
while [ $# -gt 0 ]; do
  case "$1" in
    --playbook) [ $# -ge 2 ] || { echo "--playbook exige valor" >&2; usage; }; PLAYBOOK="$(de_quem_chamou "$2")"; shift 2 ;;
    *) break ;;
  esac
done
[ $# -gt 0 ] || usage
case "$1" in
  --self-test) self_test; exit $? ;;
  --design)
    [ $# -ge 2 ] || usage
    [ $# -le 3 ] || { echo "argumento a mais: $4" >&2; usage; }
    rodar_lint "$(de_quem_chamou "${3:-${PATTERNS_DIR_DEFAULT}}")" "$(de_quem_chamou "$2")" ;;
  -h|--help) usage ;;
  --*) echo "flag desconhecida: $1" >&2; usage ;;
  *) [ $# -eq 1 ] || { echo "argumento a mais: $2" >&2; usage; }; rodar_lint "$(de_quem_chamou "$1")" "" ;;
esac
