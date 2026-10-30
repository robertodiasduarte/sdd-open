#!/usr/bin/env bash
# avaliador-guard.sh — o avaliador de contexto fresco só é despachado com a árvore COMMITADA.
#
# O avaliador usa o terminal para provar os critérios e pode restaurar arquivos do último commit
# (`git checkout -- …`) ou limpar o que não está no git: trabalho não commitado do build se perde.
# Com tudo commitado, restaurar devolve o próprio trabalho, e o alvo não se move durante a avaliação.
#
# Uso:
#   sdd/bin/avaliador-guard.sh [--root <dir>] [--permitir <prefixo>]…
# Sempre permitidos: sdd/reports/evidence/ (a evidência do próprio avaliador) e sdd/traces/ (o trace
# que o Verify Gate grava antes). --permitir acrescenta prefixos (ex.: um repositório que mantém as
# specs fora do git); nunca use um prefixo que contenha código do build.
#
# Exit: 0 limpo · 1 sujo (lista cada caminho e o comando de commit) · 2 não conferido (git falhou)
#       · 64 uso. SDD_AVALIADOR_GUARD=off → 0 com aviso (bypass humano, declarado no BUILD_REPORT).
# ⚠️ bash 3.2 · sem arrays.

set -uo pipefail

uso() {
  echo "🛑 ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ uso: sdd/bin/avaliador-guard.sh [--root <dir>] [--permitir <prefixo>]…\n' >&2
  exit 64
}

ROOT=""; PERMITIDOS="sdd/reports/evidence/
sdd/traces/
"
while [ $# -gt 0 ]; do
  case "${1}" in
    --root)     [ $# -ge 2 ] && [ -n "${2}" ] || uso "--root exige uma pasta"; ROOT="${2}"; shift 2 ;;
    --permitir) [ $# -ge 2 ] && [ -n "${2}" ] || uso "--permitir exige um prefixo"; PERMITIDOS="${PERMITIDOS}${2}
"; shift 2 ;;
    -h|--help)  sed -n '2,16p' "$0"; exit 64 ;;
    *)          uso "argumento inesperado: ${1}" ;;
  esac
done

if [ "$(printf '%s' "${SDD_AVALIADOR_GUARD:-}" | tr '[:upper:]' '[:lower:]')" = "off" ]; then
  echo "⚠️  guard desligado (SDD_AVALIADOR_GUARD=off) — declare no BUILD_REPORT."
  printf 'RESULTADO: VERDE\n→ o avaliador pode ser despachado; o bypass é decisão sua e fica registrado.\n'
  exit 0
fi

[ -n "${ROOT}" ] || ROOT="."
[ -d "${ROOT}" ] || uso "--root inexistente: ${ROOT}"
nao_conferido() {
  echo "⚠️  não consegui conferir a árvore: ${1}"
  printf 'RESULTADO: INCONCLUSIVO\n→ não despache o avaliador até o guard conferir; rode dentro do repositório do projeto.\n'
  exit 2
}
TOP="$(git -C "${ROOT}" rev-parse --show-toplevel 2>/dev/null)" || nao_conferido "${ROOT} não é um repositório git"
STATUS="$(git -C "${TOP}" -c core.quotepath=false status --porcelain --untracked-files=all 2>/dev/null)" \
  || nao_conferido "git status falhou"

permitido() { # $1=caminho → 0 se começa por um prefixo permitido
  while IFS= read -r pre; do
    [ -n "${pre}" ] || continue
    case "${1}" in "${pre}"*) return 0 ;; esac
  done <<EOF
${PERMITIDOS}
EOF
  return 1
}

SUJOS=""
while IFS= read -r linha; do
  [ "${#linha}" -ge 4 ] || continue
  st="$(printf '%s' "${linha}" | cut -c1-2)"
  resto="$(printf '%s' "${linha}" | cut -c4-)"
  case "${st}" in
    *R*|*C*) lados="$(printf '%s\n' "${resto}" | sed 's/ -> /\
/')" ;;
    *) lados="${resto}" ;;
  esac
  while IFS= read -r p; do
    p="$(printf '%s' "${p}" | sed 's/^"//; s/"$//')"
    [ -n "${p}" ] || continue
    permitido "${p}" && continue
    SUJOS="${SUJOS}${p}
"
  done <<EOF
${lados}
EOF
done <<EOF
${STATUS}
EOF

if [ -z "${SUJOS}" ]; then
  echo "✅ árvore commitada (fora de sdd/reports/evidence/, sdd/traces/ e dos prefixos permitidos)."
  printf 'RESULTADO: VERDE\n→ o avaliador pode ser despachado.\n'
  exit 0
fi
N="$(printf '%s' "${SUJOS}" | grep -c .)"
echo "🛑 ${N} arquivo(s) com mudança não commitada: o avaliador usa o terminal e pode restaurar arquivos do"
echo "   último commit — o que não foi commitado se perde. Commite antes de despachar (é rotina, não decisão):"
printf '%s' "${SUJOS}" | sed 's/^/   - /'
args="$(printf '%s' "${SUJOS}" | sed "s/'/'\\\\''/g; s/^/'/; s/\$/'/" | tr '\n' ' ')"
printf 'RESULTADO: VERMELHO\n→ git -C %s add -- %s&& git -C %s commit -m "wip(build): congelado para o avaliador"\n' \
  "${TOP}" "${args}" "${TOP}"
exit 1
