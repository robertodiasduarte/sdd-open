#!/bin/bash
# Baseline vermelha: os testes novos rodando sobre os scripts e textos da v2.4.0 precisam falhar.
cd "$(git rev-parse --show-toplevel)" || exit 64
T="$(mktemp -d)"; git archive v2.4.0 | tar -x -C "$T"
for f in tests/test_contraste.py tests/test_prompt_drift_scan.py tests/test_f13_textos.py tests/test_design_lint.py; do cp "$f" "$T/$f"; done
cd "$T" || exit 64
for m in test_contraste test_prompt_drift_scan test_f13_textos test_design_lint; do
  out=$(SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "$m.py" 2>&1); rc=$?
  printf '$ (v2.4.0 + testes novos) unittest %s\n%s\n[exit=%s]\n' "$m" "$(printf '%s\n' "$out" | tail -3)" "$rc"
done
rm -rf "${T:?}"
