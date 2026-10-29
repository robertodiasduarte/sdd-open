#!/usr/bin/env bash
# Gera a evidência da F4 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim. Roda da raiz da worktree, depois do commit (o gate usa git archive;
# comandos-intactos e check-versions comparam HEAD com a tag v2.2.4).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F4_CONVERSA
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | grep -v ResourceWarning | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

cmdlog GATE 'bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F4_CONVERSA.md'
cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.4 --base-obrigatoria'
cmdlog skill-lint-conversa 'python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog design-lint-reais 'for f in sdd/features/DESIGN_F1_MANUTENCAO.md sdd/features/DESIGN_F2_TERRENO.md sdd/features/DESIGN_F3_BUILD_RELEASE.md sdd/features/DESIGN_F4_CONVERSA.md; do python3 -B sdd/bin/design-lint.py "$f" || exit 1; done'
cmdlog comandos-intactos 'python3 -B sdd/reports/evidence/F4_CONVERSA/comandos-intactos.py'
cmdlog baseline-agnostico 'T=$(mktemp -d) && git archive v2.2.4 | tar -x -C $T && cp tests/test_agnostico.py tests/apoio.py $T/tests/ && cd $T/tests && /usr/bin/python3 -B -m unittest test_agnostico 2>&1 | grep -E "AssertionError|^\+|^-  |^FAIL|^Ran|^OK|^FAILED|CLARIFY|BUILD_REPORT"; test ${PIPESTATUS[0]} -ne 0 && echo "(test_agnostico do HEAD reprova a árvore da v2.2.4, como esperado)"'
cmdlog contratos-intactos 'git diff --stat v2.2.4 HEAD -- sdd/bin/verify-gate.sh sdd/bin/report-lint.py sdd/bin/playbook-lint.sh scripts/publish-gate.sh scripts/check-versions.py sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md sdd/fixtures/DEFINE_FIXTURE_GOVERNANCA.md sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md sdd/fixtures/DEFINE_FIXTURE_SEM_BLOCO.md sdd/fixtures/BRAINSTORM_EXEMPLO.md sdd/fixtures/playbook sdd/templates/fragments/RESUMO_ETAPA.md .agents/skills/sdd-iniciar-repo .agents/skills/sdd-higiene-dado | grep . ; test ${PIPESTATUS[0]} -eq 0 && echo "(diff vazio: nenhum dos contratos mudou)"'
cmdlog escopo 'git diff --stat v2.2.4 HEAD | tail -1 && git diff --name-status v2.2.4 HEAD'
cmdlog linhas 'wc -l .agents/skills/sdd-*/SKILL.md | sort -n | tail -4'
cmdlog testes-f4 'cd tests && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest -v test_skill_lint test_design_lint test_handoff_lint test_agnostico test_conversa test_correcoes_w0 test_contrato_build_release test_matriz_new_session test_release_workflow'
cmdlog suite-piso 'SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p "test_*.py" && /usr/bin/python3 --version && /bin/bash -c "echo bash \$BASH_VERSION"'
