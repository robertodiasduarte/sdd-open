#!/usr/bin/env bash
# Gera a evidência da F8 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim; por fim `[exit=N]` com o rc do COMANDO, capturado antes de qualquer
# pipe (a regra da F7). Roda da raiz da worktree, depois do commit do build.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F8_HOOKS
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  local out rc
  out="$(bash -c "${2}" 2>&1)"; rc=$?
  { printf '$ %s\n' "${2}"; printf '%s\n' "${out}" | grep -v ResourceWarning | tail -n 200; printf '[exit=%s]\n' "${rc}"; } > "${E}/${1}.log"
  printf '%s [exit=%s]\n' "${1}" "${rc}"
}

cmdlog testes-hooks '/usr/bin/python3 -B -m unittest discover -s tests -p "test_hooks.py" -v'
cmdlog testes-adaptador '/usr/bin/python3 -B -m unittest discover -s tests -p "test_claude_adapter.py" -v'
cmdlog testes-alarme '/usr/bin/python3 -B -m unittest discover -s tests -p "test_alarme.py" -v'
cmdlog testes-init '/usr/bin/python3 -B -m unittest discover -s tests -p "test_sdd_open.py" -v'
cmdlog testes-lints-do-pacote '/usr/bin/python3 -B -m unittest discover -s tests -p "test_docs.py" && /usr/bin/python3 -B -m unittest discover -s tests -p "test_bash32.py" && /usr/bin/python3 -B -m unittest discover -s tests -p "test_agnostico.py" && /usr/bin/python3 -B -m unittest discover -s tests -p "test_release_workflow.py"'
cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.8 --base-obrigatoria && printf "sdd-higiene-dado %s → %s\n" "$(sed -n "s/^  version: \"\(.*\)\"$/\1/p" <(git show v2.2.8:.agents/skills/sdd-higiene-dado/SKILL.md))" "$(sed -n "s/^  version: \"\(.*\)\"$/\1/p" .agents/skills/sdd-higiene-dado/SKILL.md)"'
cmdlog skill-lint-conversa '/usr/bin/python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog bash32 'grep -nE "mapfile|declare -A|\\\$\{[a-zA-Z_]+\^\^" sdd/bin/*.sh sdd/hooks/pre-commit sdd/hooks/pre-push .agents/skills/sdd-higiene-dado/scripts/*.sh bin/sdd-open.sh bin/lib/*.sh | grep -vE "^[^:]+:[0-9]+:[[:space:]]*#"; test $? -eq 1 && echo "(nenhum bashismo fora de comentário)"'
cmdlog gitleaks-tests 'gitleaks detect --source tests --no-git --redact --no-banner --exit-code 1 && gitleaks detect --source sdd/fixtures/hooks --no-git --redact --no-banner --exit-code 1 && echo "(G1 verde em tests/ e sdd/fixtures/hooks/)"'
cmdlog linhas 'wc -l sdd/hooks/pre-commit sdd/hooks/pre-push bin/sdd-open.sh bin/lib/vendors.sh bin/lib/merge.sh bin/adapters/claude/sdd-report-guard.py bin/adapters/claude/sdd-avaliador-guard.py .agents/skills/sdd-higiene-dado/scripts/alarme.sh .agents/skills/sdd-higiene-dado/scripts/pre-commit.sh .agents/skills/sdd-higiene-dado/SKILL.md tests/test_hooks.py tests/test_claude_adapter.py'
cmdlog escopo 'git diff --shortstat v2.2.8 HEAD && git diff --name-status v2.2.8 HEAD'
cmdlog init-em-projeto-real 'W=$PWD && T=$(mktemp -d) && cd "$T" && git init -q -b main p && cd p && git config user.email t@example.com && git config user.name t && printf "# projeto\n" > AGENTS.md && git add -A && git commit -q -m base && bash "$W/bin/sdd-open.sh" init --yes --vendors claude,codex > init.out 2>&1 && grep -E "hooksPath|hooks ligados|RESULTADO" init.out && rm init.out && echo "core.hooksPath=$(git config core.hooksPath)" && ls -l sdd/hooks/pre-commit sdd/hooks/pre-push && git add -A && git commit -q -m init && echo "1º commit depois do init: ok" && printf "{\"password\": \"%s\"}\n" "$(python3 -c "import secrets; print(secrets.token_hex(8))")" > cfg.json && git add cfg.json; git commit -q -m cfg; echo "commit com credencial: rc=$?"; ls .claude/hooks; python3 -c "import json; d=json.load(open(\".claude/settings.json\")); print([e[\"matcher\"] for e in d[\"hooks\"][\"PreToolUse\"]])"; cd /; rm -rf "${T:?}"'
# Só os logs deste script e do build: os AVAL-*.log são sondas dos avaliadores (comandos compostos com formatador no
# meio), não evidência citada pelo relatório; a pasta inteira é conferida à parte e declarada no BUILD_REPORT.
cmdlog shell-da-f8 'find sdd/reports/evidence/F8_HOOKS -name "*.log" -not -name "AVAL*" -exec bash sdd/bin/gate-shell-evidencia.sh {} +'
cmdlog shell-da-f8-pasta-inteira 'bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F8_HOOKS'
