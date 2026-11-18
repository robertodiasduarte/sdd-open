#!/bin/bash
# baseline.sh — os testes novos e os modificados, da HEAD, sobre o código da v2.6.0: precisam ficar vermelhos lá.
R="$(git rev-parse --show-toplevel)"
T="$(mktemp -d)"
git -C "$R" archive v2.6.0 | tar -x -C "$T"
for t in test_drive test_deploy_do_sha test_sdd_archive test_f14_drive_textos; do
  cp "$R/tests/$t.py" "$T/tests/$t.py"
done
falhou=0
for t in test_drive test_deploy_do_sha test_sdd_archive test_f14_drive_textos; do
  saida="$(cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "$t.py" 2>&1)"; rc=$?
  printf '%s: rc=%s · %s\n' "$t" "$rc" "$(printf '%s\n' "$saida" | grep -E '^(FAILED|OK|Ran)' | tr '\n' ' ')"
  [ "$rc" -ne 0 ] || falhou=$((falhou + 1))
done
rm -rf "${T:?}"
printf 'testes novos que passam na base (tem de ser 0): %s\n' "$falhou"
[ "$falhou" -eq 0 ]
