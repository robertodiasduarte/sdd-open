#!/usr/bin/env bash
# Sabotagem da F7: 1 mutação por script alterado ou novo. Cada uma tem de deixar vermelho um teste
# nomeado; `git checkout` devolve o verde. Roda da raiz da worktree, com a árvore commitada.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
export SDD_TEST_BASH=/bin/bash
falhas=0

sabota() { # $1=rótulo $2=arquivo $3=trecho original $4=trecho sabotado $5=módulo de teste
  /usr/bin/python3 -B - "$2" "$3" "$4" <<'PY' || { echo "✗ $1: trecho não encontrado"; falhas=$((falhas + 1)); return; }
import sys
p, a, b = sys.argv[1:4]
t = open(p, encoding="utf-8").read()
if t.count(a) != 1:
    sys.exit(1)
open(p, "w", encoding="utf-8").write(t.replace(a, b))
PY
  out="$(cd tests && /usr/bin/python3 -B -m unittest "$5" 2>&1)"; rc=$?
  nomes="$(printf '%s\n' "${out}" | grep -oE '^(FAIL|ERROR): [^ ]+' | sed -E 's/^(FAIL|ERROR): //' | sort -u | head -5 | tr '\n' ' ')"
  git checkout -q -- "$2"
  out2="$(cd tests && /usr/bin/python3 -B -m unittest "$5" 2>&1)"; rc2=$?
  if [ "${rc}" -ne 0 ] && [ "${rc2}" -eq 0 ]; then
    echo "✅ $1 → vermelho (${nomes}) · restaurado → verde"
  else
    echo "✗ $1 → rc sabotado=${rc}, rc restaurado=${rc2}"; falhas=$((falhas + 1))
  fi
}

sabota "report-lint: sem a regra de existência" sdd/bin/report-lint.py \
  "    violations += existencia_avaliacao(content, root, feature, warnings)" "    pass" test_report_lint_evidencia
sabota "verify-gate: sem o trap do trace" sdd/bin/verify-gate.sh \
  'cd "${REPO_ROOT}" || finalizar 64
trap trace_gravar EXIT' 'cd "${REPO_ROOT}" || finalizar 64' test_verify_gate_trace
sabota "gate-baseline: base verde vira dentes" sdd/bin/gate-baseline.sh \
  "não distingue o antes do depois.\"
    printf 'RESULTADO: VERMELHO\n→ ancore a asserção no que a feature muda (o comportamento novo) e rode de novo.\n'
    exit 2 ;;" "não distingue o antes do depois.\"
    printf 'RESULTADO: VERMELHO\n→ ancore a asserção no que a feature muda (o comportamento novo) e rode de novo.\n'
    exit 0 ;;" test_gate_baseline
sabota "gate-shell-evidencia: tail fora da lista" sdd/bin/gate-shell-evidencia.sh \
  "^(tail|head|cat|" "^(head|cat|" test_gate_shell_evidencia
sabota "avaliador-guard: ignora não rastreados" sdd/bin/avaliador-guard.sh \
  "--untracked-files=all" "--untracked-files=no" test_avaliador_guard
sabota "test-baseline: toda falha vira conhecida" sdd/bin/test-baseline.sh \
  "novos = [i for i in ids if i not in conhecidos]" "novos = []" test_test_baseline

git diff --quiet -- sdd/bin || { echo "✗ a árvore não voltou ao commit"; falhas=$((falhas + 1)); }
if [ "${falhas}" -eq 0 ]; then echo "🟢 6/6 sabotagens vermelhas e restauradas"; exit 0; fi
echo "🛑 ${falhas} sabotagem(ns) sem dentes"; exit 1
