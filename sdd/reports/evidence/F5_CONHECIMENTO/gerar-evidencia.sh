#!/usr/bin/env bash
# Gera a evidência da F5 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim. Roda da raiz da worktree, depois do commit (o gate usa git archive;
# comandos-intactos, contratos e check-versions comparam HEAD com a tag v2.2.5).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F5_CONHECIMENTO
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | grep -v ResourceWarning | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.5 --base-obrigatoria'
cmdlog comandos-intactos '/usr/bin/python3 -B sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.py'
cmdlog contratos-intactos 'git diff --stat v2.2.5 HEAD -- sdd/bin/verify-gate.sh sdd/bin/report-lint.py sdd/bin/skill-lint.py sdd/bin/design-lint.py sdd/bin/handoff-lint.py sdd/bin/playbook-lint.sh scripts/publish-gate.sh scripts/check-versions.py sdd/fixtures sdd/templates/UX_REVIEW_TEMPLATE.md sdd/templates/fragments .agents/skills/sdd-iniciar-repo .agents/skills/sdd-higiene-dado | grep . ; test ${PIPESTATUS[0]} -eq 0 && echo "(diff vazio: nenhum dos contratos mudou)" && bash sdd/bin/playbook-lint.sh --self-test >/dev/null && echo "playbook-lint --self-test: 0"'
cmdlog gate-kb 'PYTHON=/usr/bin/python3 /bin/bash .agents/skills/sdd-kb/scripts/gate.sh'
cmdlog skill-lint-conversa '/usr/bin/python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog kb-dominios-proprio '/usr/bin/python3 -B sdd/bin/kb-dominios.py sdd/features/DEFINE_F5_CONHECIMENTO.md'
cmdlog escopo 'git diff --stat v2.2.5 HEAD | tail -1 && git diff --name-status v2.2.5 HEAD'
cmdlog linhas 'wc -l .agents/skills/sdd-*/SKILL.md | sort -n | tail -4'
cmdlog testes-f5 'cd tests && /usr/bin/python3 -B -m unittest -v test_sdd_kb test_sdd_kb_normativo test_kb_dominios test_conversa test_skill_lint test_matriz_new_session'
