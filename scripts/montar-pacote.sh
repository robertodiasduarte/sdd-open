#!/usr/bin/env bash
# montar-pacote.sh — extrai numa pasta o pacote do commit atual, montado como a Release o monta (git archive), e imprime
# o caminho dela. Os passos do CI que leem a árvore (publish-gate, sintaxe de shell) rodam sobre esta pasta, não sobre o
# checkout: desde a F26 os documentos das frentes vivem na main, e o export-ignore os tira do pacote.
#
# USO-INICIO
#   montar-pacote.sh [DESTINO]     DESTINO vazio ou inexistente (padrão: uma pasta temporária nova); REF = HEAD
#       0 imprime o caminho da pasta (e só ele) · 1 o git archive ou o tar falhou, ou o pacote saiu sem o MANIFEST.txt
#       64 uso (fora de um repositório git, destino com arquivo dentro)
#   No workflow, em 2 linhas, para o exit do montador derrubar o passo:
#       P="$(bash scripts/montar-pacote.sh)"
#       bash scripts/publish-gate.sh "$P"
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · Git Bash no Windows (tar do Git).

set -u -o pipefail

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "🛑 montar-pacote: rode dentro de um repositório git." >&2
  exit 64
fi
if [ -n "${1:-}" ]; then
  destino="$1"
  if [ -e "$destino" ] && [ -n "$(ls -A "$destino" 2>/dev/null)" ]; then
    echo "🛑 montar-pacote: o destino não está vazio: $destino" >&2
    exit 64
  fi
  mkdir -p "$destino" || exit 1
else
  destino="$(mktemp -d 2>/dev/null || mktemp -d -t pacote)" || exit 1
fi

if ! git archive --format=tar HEAD | tar -x -C "$destino"; then
  echo "🛑 montar-pacote: o git archive ou o tar falhou; o pacote não foi montado." >&2
  exit 1
fi
if [ ! -f "$destino/MANIFEST.txt" ]; then
  echo "🛑 montar-pacote: o pacote saiu sem o MANIFEST.txt (montagem incompleta)." >&2
  exit 1
fi
printf '%s\n' "$destino"
