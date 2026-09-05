#!/usr/bin/env bash
# plan.sh — plano antes de escrever, e a confirmação.
#
# init e sync calculam TUDO antes de tocar em disco. O plano é uma linha por alvo:
#   + <caminho> (novo)          será criado
#   ~ <caminho> (atualizar)     existe e difere
#   = <caminho> (já correto)    existe e é igual — nada a fazer
# --dry-run para depois do plano. Sem --yes, Enter significa NÃO.
#
# ⚠️ bash 3.2 · ${VAR} com chaves antes de não-ASCII.

PLANO_NOVOS=0
PLANO_ATUALIZAR=0
PLANO_EMDIA=0

plano_reset() { PLANO_NOVOS=0; PLANO_ATUALIZAR=0; PLANO_EMDIA=0; }

# Classifica um destino contra a fonte. $3 opcional = "gerado" para ignorar as 2 linhas do
# cabeçalho GENERATED na comparação (adaptador nunca é byte-idêntico à fonte — Decision 1).
plano_linha() { # $1=destino $2=fonte [$3=gerado]
  local dest="${1}" fonte="${2}" modo="${3:-}"
  if [ ! -e "${dest}" ]; then
    PLANO_NOVOS=$((PLANO_NOVOS + 1)); printf '+ %s (novo)\n' "${dest}"
  elif [ "${modo}" = "gerado" ] && grep -vF 'sdd-open:generated' "${dest}" | cmp -s - "${fonte}"; then
    PLANO_EMDIA=$((PLANO_EMDIA + 1)); detalhe "= ${dest} (já correto)"
  elif [ "${modo}" != "gerado" ] && cmp -s "${dest}" "${fonte}"; then
    PLANO_EMDIA=$((PLANO_EMDIA + 1)); detalhe "= ${dest} (já correto)"
  else
    PLANO_ATUALIZAR=$((PLANO_ATUALIZAR + 1)); printf '~ %s (atualizar)\n' "${dest}"
  fi
}

# Linha de plano para algo que não é cópia de arquivo (bloco do AGENTS.md, chave do JSON).
plano_estado() { # $1=destino $2=novo|atualizar|emdia
  case "${2}" in
    novo)      PLANO_NOVOS=$((PLANO_NOVOS + 1));         printf '+ %s (novo)\n' "${1}" ;;
    atualizar) PLANO_ATUALIZAR=$((PLANO_ATUALIZAR + 1)); printf '~ %s (atualizar)\n' "${1}" ;;
    emdia)     PLANO_EMDIA=$((PLANO_EMDIA + 1));         detalhe "= ${1} (já correto)" ;;
  esac
}

plano_resumo() {
  printf '%s a criar · %s a atualizar · %s já corretos\n' "${PLANO_NOVOS}" "${PLANO_ATUALIZAR}" "${PLANO_EMDIA}"
}

plano_tem_mudanca() { [ $((PLANO_NOVOS + PLANO_ATUALIZAR)) -gt 0 ]; }

# Enter = NÃO. --yes pula. Fora de terminal interativo sem --yes = NÃO (nunca adivinha).
confirmar() {
  [ "${ASSUME_YES:-0}" = "1" ] && return 0
  if [ ! -t 0 ]; then
    resultado "CANCELADO" "nenhum arquivo foi escrito; sem terminal interativo, use --yes para aplicar."
    exit 0
  fi
  printf 'Aplicar? [y/N] '
  read -r r
  case "${r}" in
    y|Y|s|S) return 0 ;;
    *) resultado "CANCELADO" "nenhum arquivo foi escrito."; exit 0 ;;
  esac
}
