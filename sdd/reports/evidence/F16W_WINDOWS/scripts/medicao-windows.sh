#!/usr/bin/env bash
# medicao-windows.sh <id do run> <pasta de saída>: baixa os artefatos testes-windows-fatia-* do run (dado não confiável:
# pasta própria, vazia) e monta a tabela por módulo com juntar-medicao.py, que fica fora dela.
set -u
run="$1"; out="$2"
aqui="$(cd "$(dirname "$0")" && pwd)"
[ -e "$out" ] && { echo "a pasta $out já existe: use uma nova" >&2; exit 64; }
mkdir -p "$out/baixado"
gh run download "$run" -R robertodiasduarte/sdd-open -p 'testes-windows-fatia-*' -D "$out/baixado"; rc=$?
[ "$rc" = 0 ] || { echo "gh run download saiu $rc" >&2; exit "$rc"; }
python3 -I "$aqui/juntar-medicao.py" "$out/baixado" > "$out/TABELA.md"
echo "tabela em $out/TABELA.md"
