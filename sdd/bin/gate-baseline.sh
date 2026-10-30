#!/usr/bin/env bash
# gate-baseline.sh — prova que a asserção do gate TEM DENTES: roda o Verify Gate do DEFINE contra o
# código ANTERIOR (a branch de produção, numa cópia isolada) e exige que ele fique VERMELHO lá.
#
# Um gate que passa no código anterior não avalia nada, e "corrigir" a asserção até ela ficar verde é
# indistinguível de afrouxá-la. Rode isto quando o build corrigiu (ou escreveu) a asserção do gate.
#
# Uso:
#   sdd/bin/gate-baseline.sh <DEFINE.md> [--base <ref>] [--feature <NOME>] [--sobrepor <caminho>]…
#     --base      estado anterior (default: origin/<project.default_branch>, depois <default_branch>)
#     --feature   nome para a evidência (default: o DEFINE sem DEFINE_ e .md)
#     --sobrepor  arquivo ou pasta do BUILD levado para a cópia (o script do gate, as fixtures dele);
#                 repita para vários. O DEFINE e sdd/bin/ do build já vão sempre: é a asserção de AGORA
#                 contra o código de ANTES.
#
# Exit:
#   0  = a base reprovou AVALIANDO: o gate saiu 2 e a saída tem o 🔴 do runner (o comando declarou
#        VERMELHO) ou um marcador de asserção de teste (unittest, pytest, jest, vitest, go, deno)
#   2  = a base PASSOU: a asserção não distingue o antes do depois
#   3  = INCONCLUSIVO: vermelho sem sinal de asserção (crash, arquivo ausente, sintaxe — o "(rc=N)" do
#        runner é o rc bruto do comando e não prova nada), exit 3/4/5/64 na base, ou base inexistente
#   64 = uso: argumento errado, DEFINE ou --sobrepor inexistente
#
# Evidência: sdd/reports/evidence/<FEATURE>/BASELINE-gate.log (1ª linha `$ comando`).
# ⚠️ bash 3.2 · nunca toca o worktree do build · a cópia não grava trace (SDD_TRACE=off).

set -uo pipefail

uso() {
  echo "🛑 uso: sdd/bin/gate-baseline.sh <DEFINE.md> [--base <ref>] [--feature <NOME>] [--sobrepor <caminho>]…" >&2
  [ -n "${1:-}" ] && echo "   ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ corrija a chamada e rode de novo.\n' >&2
  exit 64
}
inconclusivo() {
  echo "⚠️  ${1}"
  printf 'RESULTADO: INCONCLUSIVO\n→ %s\n' "${2:-faça o gate rodar no estado anterior e repita; isto não prova dentes.}"
  exit 3
}

DEFINE=""; BASE=""; FEATURE=""; SOBREPOR=""
while [ $# -gt 0 ]; do
  case "${1}" in
    --base)     [ $# -ge 2 ] || uso "--base exige uma ref"; BASE="${2}"; shift 2 ;;
    --feature)  [ $# -ge 2 ] || uso "--feature exige um nome"; FEATURE="${2}"; shift 2 ;;
    --sobrepor) [ $# -ge 2 ] || uso "--sobrepor exige um caminho"; SOBREPOR="${SOBREPOR}${2}
"; shift 2 ;;
    -h|--help)  sed -n '2,25p' "$0"; exit 64 ;;
    -*)         uso "opção desconhecida: ${1}" ;;
    *)          [ -z "${DEFINE}" ] || uso "argumento inesperado: ${1}"; DEFINE="${1}"; shift ;;
  esac
done
[ -n "${DEFINE}" ] || uso
[ -f "${DEFINE}" ] || uso "DEFINE não encontrado: ${DEFINE}"

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || inconclusivo "não é um repositório git" "rode dentro do projeto."
ROOT="$(cd "${ROOT}" && pwd -P)"
DEFINE_ABS="$(cd "$(dirname "${DEFINE}")" && pwd -P)/$(basename "${DEFINE}")"
case "${DEFINE_ABS}" in
  "${ROOT}"/*) DEFINE_REL="${DEFINE_ABS#"${ROOT}"/}" ;;
  *) DEFINE_REL="DEFINE_baseline.md" ;;
esac
[ -n "${FEATURE}" ] || FEATURE="$(basename "${DEFINE}" .md | sed -E 's/^DEFINE_//; s/[^A-Za-z0-9._-]/_/g')"

cd "${ROOT}" || exit 64
falta=""
while IFS= read -r p; do
  [ -n "${p}" ] || continue
  [ -e "${p}" ] || { falta="${p}"; break; }
done <<EOF
${SOBREPOR}
EOF
[ -z "${falta}" ] || uso "--sobrepor inexistente (caminho relativo à raiz): ${falta}"

# ---- a base: --base, ou origin/<default_branch>, ou <default_branch> -------------------------
DB="$(sed -n 's/^[[:space:]]*default_branch:[[:space:]]*//p' sdd/config.yaml 2>/dev/null | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d "\"' ")"
[ -n "${DB}" ] || DB="main"
if [ -z "${BASE}" ]; then
  for cand in "origin/${DB}" "${DB}"; do
    git rev-parse --verify -q "${cand}^{commit}" >/dev/null 2>&1 && { BASE="${cand}"; break; }
  done
fi
[ -n "${BASE}" ] || inconclusivo "sem estado anterior: nem origin/${DB} nem ${DB} existem" "passe --base <ref> com o estado anterior ao build."
git rev-parse --verify -q "${BASE}^{commit}" >/dev/null 2>&1 || inconclusivo "ref de base inválida: ${BASE}" "passe --base <ref> existente."
BASE_SHA="$(git rev-parse --short "${BASE}^{commit}")"

# ---- a cópia: base + DEFINE + sdd/bin + --sobrepor do build ---------------------------------
WORK="$(mktemp -d 2>/dev/null || mktemp -d -t gatebase)" || inconclusivo "mktemp falhou"
trap 'rm -rf "${WORK:?}"' EXIT
git archive --format=tar "${BASE}" 2>/dev/null | (cd "${WORK}" && tar -xf -) || inconclusivo "git archive de ${BASE} falhou"
mkdir -p "${WORK}/$(dirname "${DEFINE_REL}")" && cp "${DEFINE_ABS}" "${WORK}/${DEFINE_REL}" || inconclusivo "não consegui copiar o DEFINE"
while IFS= read -r p; do
  [ -n "${p}" ] && [ -e "${p}" ] || continue
  tar -cf - "${p}" | (cd "${WORK}" && tar -xf -) || inconclusivo "não consegui sobrepor ${p} na cópia"
done <<EOF
sdd/bin
${SOBREPOR}
EOF
[ -f "${WORK}/sdd/bin/verify-gate.sh" ] || inconclusivo "sdd/bin/verify-gate.sh ausente no build"
( cd "${WORK}" && git init -q . && git add -A >/dev/null 2>&1 \
  && git -c user.name=sdd-baseline -c user.email=baseline@example.com -c commit.gpgsign=false \
         -c core.hooksPath=/dev/null commit -q --no-verify -m baseline >/dev/null 2>&1 ) \
  || inconclusivo "não consegui montar o repositório da cópia"

# ---- o gate do build contra o código anterior ------------------------------------------------
echo "▶ base: ${BASE} (${BASE_SHA}) · gate: sdd/bin/verify-gate.sh ${DEFINE_REL}"
OUT="$(cd "${WORK}" && SDD_TRACE=off bash sdd/bin/verify-gate.sh "${DEFINE_REL}" 2>&1)"
RC=$?
printf '%s\n' "${OUT}" | tail -n 30 | sed 's/^/   │ /'

EVID="sdd/reports/evidence/${FEATURE}"
if mkdir -p "${EVID}" 2>/dev/null; then
  { echo "\$ bash sdd/bin/gate-baseline.sh ${DEFINE_REL} --base ${BASE}$(printf '%s' "${SOBREPOR}" | sed 's/^/ --sobrepor /' | tr -d '\n')"
    echo "# base=${BASE} (${BASE_SHA}) · exit_do_gate=${RC}"
    printf '%s\n' "${OUT}" | tail -n 200
  } > "${EVID}/BASELINE-gate.log" 2>/dev/null || echo "⚠️  não consegui gravar ${EVID}/BASELINE-gate.log"
else
  echo "⚠️  não consegui criar ${EVID}/"
fi

# ---- veredito --------------------------------------------------------------------------------
MARCADORES='🔴|FAILED \(failures=|=+ .*[0-9]+ failed|--- FAIL:|Tests: +[0-9]+ failed|(Test Files|Tests) +[0-9]+ failed|FAILED \|'
case "${RC}" in
  0)
    echo "🛑 a base PASSOU: a asserção fica verde no código anterior e não distingue o antes do depois."
    printf 'RESULTADO: VERMELHO\n→ ancore a asserção no que a feature muda (o comportamento novo) e rode de novo.\n'
    exit 2 ;;
  2)
    if printf '%s\n' "${OUT}" | grep -qE "${MARCADORES}"; then
      echo "✅ a base reprovou AVALIANDO: a asserção tem dentes."
      printf 'RESULTADO: VERDE\n→ siga; a prova está em %s/BASELINE-gate.log.\n' "${EVID}"
      exit 0
    fi
    rc_cmd="$(printf '%s\n' "${OUT}" | sed -n 's/.*GATE VERMELHO.*(rc=\([0-9][0-9]*\)).*/\1/p' | tail -1)"
    inconclusivo "a base ficou vermelha sem sinal de asserção (rc do comando=${rc_cmd:-?}): crash, arquivo ausente ou sintaxe não provam dentes" ;;
  *)
    inconclusivo "o gate não chegou a avaliar na base (exit ${RC}): ferramenta ou arquivo ausente, manual-ux, clarificação ou DEFINE sem gate" ;;
esac
