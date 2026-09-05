#!/usr/bin/env bash
# vendors.sh — tabela de vendors do SDD Open.
#
# ⛔ bash 3.2 (o /bin/bash do macOS) NÃO tem `declare -A`. A tabela é `case` + funções.
# ⚠️ LM-046: iteração usa `printf '%s\n'` — sem o \n final o `while read` DESCARTA o último
#    item, e o último vendor de --vendors sumiria em silêncio.

VENDORS_SUPORTADOS="claude codex gemini cursor kimi"

vendor_valido() {
  case "${1}" in
    claude|codex|gemini|cursor|kimi) return 0 ;;
    *) return 1 ;;
  esac
}

# Arquivos/diretórios que o vendor GERA.
# Vazio = lê .agents/skills/ nativamente; nada a gerar (e isso é confirmação, não ausência).
vendor_alvos() {
  case "${1}" in
    claude) printf '%s\n' 'CLAUDE.md' '.claude/skills' ;;
    cursor) printf '%s\n' '.cursor/skills' ;;
    gemini) printf '%s\n' 'GEMINI.md' '.gemini/settings.json' ;;
    codex|kimi) : ;;
  esac
}

# Como o vendor é descoberto no ambiente (binário no PATH ou diretório no projeto).
vendor_binario() {
  case "${1}" in
    claude) printf 'claude' ;;
    codex)  printf 'codex' ;;
    gemini) printf 'gemini' ;;
    cursor) printf 'cursor' ;;
    kimi)   printf 'kimi' ;;
  esac
}

# 1 linha por vendor válido da lista separada por vírgula. Vendor inválido aborta com a
# lista dos suportados — nunca silêncio, nunca geração parcial.
vendores_da_lista() { # $1=lista
  printf '%s\n' "${1}" | tr ',' '\n' | while read -r v; do
    [ -n "${v}" ] || continue
    if ! vendor_valido "${v}"; then
      printf '__INVALIDO__%s\n' "${v}"
      continue
    fi
    printf '%s\n' "${v}"
  done
}

# Descrição de por que um vendor não gera arquivo (usada pelo doctor).
vendor_nativo_motivo() {
  case "${1}" in
    codex) printf 'lê .agents/skills/ e AGENTS.md nativamente' ;;
    kimi)  printf 'lê .agents/skills/, .kimi/skills e AGENTS.md nativamente' ;;
    *) printf '' ;;
  esac
}
