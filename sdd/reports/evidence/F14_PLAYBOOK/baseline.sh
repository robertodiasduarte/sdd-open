#!/bin/bash
# baseline.sh — os 6 arquivos de teste novos rodam numa cópia da v2.5.0: cada um precisa falhar lá.
R="$(git rev-parse --show-toplevel)"; T="$(mktemp -d)"; trap 'rm -rf "${T:?}"' EXIT
git -C "$R" archive v2.5.0 | tar -x -C "$T"
cp "$R"/tests/test_playbook_curator.py "$R"/tests/test_playbook_invariantes.py "$R"/tests/test_curadoria_bloco.py \
   "$R"/tests/test_copiar_docs.py "$R"/tests/test_f14_textos.py "$R"/tests/test_apoio_ambiente.py "$T/tests/"
falhou=0
for f in playbook_curator playbook_invariantes curadoria_bloco copiar_docs f14_textos apoio_ambiente; do
  saida="$(cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "test_$f.py" 2>&1)"; rc=$?
  printf 'test_%s: rc=%s · %s\n' "$f" "$rc" "$(printf '%s\n' "$saida" | grep -E '^(Ran |FAILED|OK)' | tr '\n' ' ')"
  [ "$rc" -ne 0 ] && falhou=$((falhou + 1))
done
printf 'vermelhos: %s de 6\n' "$falhou"
[ "$falhou" -eq 6 ]
