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

# Linha de plano. Cópias de skill decidem o estado por gerado_em_dia (sdd-open.sh), que compara
# com o que o escritor renderiza agora; blocos do AGENTS.md e chaves do JSON, pelo merge de cada um.
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
