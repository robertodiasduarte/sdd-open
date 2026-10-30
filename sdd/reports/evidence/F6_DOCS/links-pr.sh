#!/usr/bin/env bash
# A-002 do DEFINE: as âncoras do sumário do guia existem na página que o GitHub renderiza (branch do PR),
# e a função ancora() do tests/test_docs.py gera as mesmas para cada título do guia.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
H="$(mktemp)"
curl -sL "https://github.com/robertodiasduarte/sdd-open/blob/${1:-feat/f6-docs}/docs/pt-BR/guia-do-aluno.md" -o "${H}"
grep -o 'user-content-[^"\\&]*' "${H}" | sed 's/^user-content-//' | sort -u > "${H}.ids"
echo "ids na página do GitHub: $(wc -l < "${H}.ids" | tr -d ' ')"
falhas=0
for a in $(grep -o '](#[^)]*)' docs/pt-BR/guia-do-aluno.md | sed 's/](#//; s/)$//' | sort -u); do
  if grep -qxF "${a}" "${H}.ids"; then echo "abre      #${a}"; else echo "NÃO ABRE  #${a}"; falhas=$((falhas + 1)); fi
done
cd tests && /usr/bin/python3 -B -c "
import sys
from pathlib import Path
import test_docs as v
gh = set(Path(sys.argv[1]).read_text(encoding='utf-8').split())
nossas = v.ancoras(v.GUIA)
print('títulos do guia: %d · âncora do teste igual à do GitHub: %d · diferentes: %s' % (len(nossas), len(nossas & gh), sorted(nossas - gh) or 'nenhuma'))
sys.exit(1 if nossas - gh else 0)
" "${H}.ids" || falhas=$((falhas + 1))
rm -f "${H:?}" "${H}.ids"
echo "âncoras do sumário que não abrem + divergências: ${falhas}"
[ "${falhas}" -eq 0 ]
