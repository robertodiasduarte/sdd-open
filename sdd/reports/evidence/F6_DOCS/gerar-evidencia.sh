#!/usr/bin/env bash
# Gera a evidência da F6 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim. Roda da raiz da worktree, depois do commit (comandos-intactos,
# contratos e check-versions comparam HEAD com a tag v2.2.6; a baseline roda o teste novo na v2.2.6).
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F6_DOCS
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  { echo "\$ ${2}"; bash -c "${2}" 2>&1 | grep -v ResourceWarning | tail -n 200; echo "exit=${PIPESTATUS[0]}"; } > "${E}/${1}.log"
  printf '%s %s\n' "${1}" "$(tail -1 "${E}/${1}.log")"
}

cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.6 --base-obrigatoria && for s in brainstorm define governanca ux-review design build release; do printf "sdd-%s %s → %s\n" "$s" "$(git show v2.2.6:.agents/skills/sdd-$s/SKILL.md | sed -n "s/^  version: \"\(.*\)\"$/\1/p")" "$(sed -n "s/^  version: \"\(.*\)\"$/\1/p" .agents/skills/sdd-$s/SKILL.md)"; done'
cmdlog comandos-intactos '/usr/bin/python3 -B sdd/reports/evidence/F6_DOCS/comandos-intactos.py'
cmdlog contratos-intactos 'git diff --stat v2.2.6 HEAD -- sdd/bin sdd/fixtures sdd/templates sdd/playbook.md sdd/config.example.yaml scripts bin .github | grep . ; test ${PIPESTATUS[0]} -eq 0 && echo "(diff vazio: nenhum dos contratos mudou)" && bash sdd/bin/playbook-lint.sh --self-test >/dev/null && echo "playbook-lint --self-test: 0"'
cmdlog skill-lint-conversa '/usr/bin/python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog linhas 'wc -l .agents/skills/sdd-*/SKILL.md | sort -n | tail -4'
cmdlog escopo 'git diff --stat v2.2.6 HEAD | tail -1 && git diff --name-status v2.2.6 HEAD'
cmdlog codepoints '/usr/bin/python3 -B -c "
import re, unicodedata
from pathlib import Path
vistos = dict()
for s in (\"brainstorm\", \"define\", \"governanca\", \"ux-review\", \"design\", \"build\", \"release\"):
    t = Path(\".agents/skills/sdd-%s/SKILL.md\" % s).read_text(encoding=\"utf-8\")
    sec = re.search(r\"\n## Por que cada regra existe\n.*?(?=\n## )\", t, re.S).group(0)
    for c in sec:
        if ord(c) > 127:
            vistos[c] = vistos.get(c, 0) + 1
for c in sorted(vistos):
    print(\"U+%04X %-4s %-3s %d  %s\" % (ord(c), unicodedata.category(c), c, vistos[c], unicodedata.name(c, \"?\")))
invisiveis = [c for c in vistos if unicodedata.category(c) in (\"Cf\", \"Zs\") and c != \" \"]
print(\"invisíveis ou espaços especiais:\", len(invisiveis))
"'
cmdlog testes-f6 'cd tests && /usr/bin/python3 -B -m unittest -v test_docs test_contrato_build_release test_correcoes_w0 test_conversa test_skill_lint test_agnostico test_sdd_open'
cmdlog baseline 'T=$(mktemp -d) && git archive v2.2.6 | tar -x -C "$T" && cp tests/test_docs.py "$T/tests/" && cd "$T/tests" && /usr/bin/python3 -B -m unittest test_docs 2>&1 | grep -E "^(FAIL|ERROR|Ran|OK|FAILED)"; rc=${PIPESTATUS[0]}; cd / && rm -rf "${T:?}"; exit $rc'
cmdlog sabotagem '/bin/bash sdd/reports/evidence/F6_DOCS/sabotagem.sh'
cmdlog GATE 'bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md'
