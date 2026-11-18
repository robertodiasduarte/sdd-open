#!/bin/bash
# tabelas-reais.sh — colhe, com a regra do cabeçalho, cada DESIGN e BUILD_REPORT real do repositório, um por vez.
R="$(git rev-parse --show-toplevel)"; T="$(mktemp -d)"; trap 'rm -rf "${T:?}"' EXIT
total=0; sem=0; deltas=0
for f in "$R"/sdd/features/DESIGN_*.md "$R"/sdd/reports/BUILD_REPORT_*.md; do
  rm -rf "${T:?}/d"; mkdir "$T/d"; cp "$f" "$T/d/"
  out="$(SDD_TRACE=off bash "$R/sdd/bin/playbook-curator.sh" --colher "$T/d" "$R/sdd/playbook.md" 2>/dev/null)"
  total=$((total + 1))
  n="$(printf '%s\n' "$out" | grep -c '^TABELA_SEM_CABECALHO')"; sem=$((sem + n))
  d="$(printf '%s\n' "$out" | grep -c '^DELTA ')"; deltas=$((deltas + d))
  [ "$n" -eq 0 ] || printf '%s\n' "$out" | grep '^TABELA_SEM_CABECALHO'
done
printf 'documentos: %s · linhas DELTA: %s · tabelas sem cabeçalho: %s\n' "$total" "$deltas" "$sem"
[ "$sem" -eq 0 ]
