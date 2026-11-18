#!/usr/bin/env bash
# baseline.sh <commit antes> <log>: os testes novos e mudados da F17c rodados contra a árvore anterior (LM-002)
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3; B="$1"; LOG="$2"; T="$(mktemp -d)"
git -C "$W" archive "$B" | tar -x -C "$T"
for f in test_f17c_gerador.py test_f17c_textos.py test_gerar_starter.py; do git -C "$W" show "HEAD:tests/$f" > "$T/tests/$f"; done
{ echo "\$ cd <git archive $B, com os testes de HEAD $(git -C "$W" rev-parse --short HEAD)>/tests && python3 -B -m unittest test_f17c_gerador test_f17c_textos test_gerar_starter"
  (cd "$T/tests" && SDD_TEST_BASH=/bin/bash python3 -B -m unittest test_f17c_gerador test_f17c_textos test_gerar_starter 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK")
  echo "rc=0   # esperado: FAILED (vermelho na árvore anterior)"; } > "$LOG"
rm -rf "$T"
