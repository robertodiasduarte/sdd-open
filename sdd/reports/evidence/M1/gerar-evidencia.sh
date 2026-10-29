#!/usr/bin/env bash
# Gera a evidência da M1 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim. Roda da raiz da worktree, depois do commit (o gate usa git archive).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/M1
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | grep -v ResourceWarning | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.4 --base-obrigatoria'
cmdlog GATE 'T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T'
cmdlog escopo 'git diff --stat v2.2.4 HEAD && git diff --name-only v2.2.4 HEAD | grep -vxE "\.github/workflows/(publish-gate|release)\.yml|tests/test_release_workflow\.py"; test $? -eq 1 && echo "(só os 2 workflows e tests/test_release_workflow.py mudaram; nenhuma skill)"'
cmdlog deploy-espera-testes 'python3 -B .agents/skills/sdd-release/scripts/deploy-espera-testes.py .'
cmdlog checkout-v5 'git ls-remote https://github.com/actions/checkout refs/tags/v5.1.0 "refs/tags/v5.1.0^{}" && grep -n "actions/checkout@" .github/workflows/*.yml'
cmdlog testes-m1 'cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest -v test_release_workflow'
cmdlog suite-piso 'SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "test_*.py" && /usr/bin/python3 --version && /bin/bash -c "echo bash \$BASH_VERSION"'
