#!/usr/bin/env bash
# Gera a evidência da W0 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim. Roda da raiz da worktree, depois do commit (o gate usa git archive).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/W0
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | grep -v ResourceWarning | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

cmdlog W0-4.1-fixture 'for f in --print ""; do bash sdd/bin/verify-gate.sh $f sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md >/dev/null 2>&1; echo "verify-gate.sh ${f:-(sem --print)} fixture de clarificação → exit $?"; done'
cmdlog W0-testes 'cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest -v test_correcoes_w0 test_contrato_build_release test_verify_gate'
cmdlog W0-grep "grep -rnE 'claude-build-report-guard|/drive|Step 1\\.5|slice 2' sdd/ .agents/ --exclude-dir=features --exclude-dir=handoffs --exclude-dir=reports; test \$? -eq 1 && echo '(sem achado fora dos artefatos SDD)'"
cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.3 --base-obrigatoria'
cmdlog contratos-intactos 'git diff --stat v2.2.3 HEAD -- sdd/bin/ sdd/fixtures/ scripts/ .github/ && echo "(diff vazio: sdd/bin, fixtures, scripts e workflows iguais a v2.2.3)" && bash sdd/bin/playbook-lint.sh --self-test | tail -n 3'
cmdlog GATE 'T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T'
