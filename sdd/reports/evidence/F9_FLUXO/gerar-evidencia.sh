#!/usr/bin/env bash
# Gera a evidência da F9 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim; por fim `[exit=N]` com o rc do COMANDO, capturado antes de qualquer
# pipe (a regra da F7). Roda da raiz da worktree, depois do commit do build.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F9_FLUXO
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  local out rc
  out="$(bash -c "${2}" 2>&1)"; rc=$?
  { printf '$ %s\n' "${2}"; printf '%s\n' "${out}" | grep -v ResourceWarning | tail -n 200; printf '[exit=%s]\n' "${rc}"; } > "${E}/${1}.log"
  printf '%s [exit=%s]\n' "${1}" "${rc}"
}

# Fonte do privado (só leitura), para a verdade conhecida do review-design e o diferencial do loop.
FONTE="$(mktemp -d)/sdd-fluxo-privado.sh"
git -C "${HOME}/RDD/Wordpress" show origin/main:scripts/sdd-fluxo.sh > "${FONTE}" || exit 64
export FONTE

cmdlog testes-fluxo '/usr/bin/python3 -B -m unittest discover -s tests -p "test_fluxo.py" -v'
cmdlog testes-decisoes-lint '/usr/bin/python3 -B -m unittest discover -s tests -p "test_decisoes_lint.py" -v'
cmdlog testes-contratos-tocados 'for t in conversa docs contrato_build_release correcoes_w0 matriz_new_session release_workflow agnostico bash32 skill_lint; do /usr/bin/python3 -B -m unittest discover -s tests -p "test_$t.py" || exit 1; done'
cmdlog self-test-fluxo '/bin/bash sdd/bin/sdd-fluxo.sh --self-test'
cmdlog self-test-decisoes-lint '/bin/bash sdd/bin/sdd-decisoes-lint.sh --self-test'
cmdlog decisoes-lint-sites '/bin/bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments'
cmdlog skill-lint-conversa '/usr/bin/python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.9 --base-obrigatoria'
cmdlog bash32 'grep -nE "mapfile|declare -A|\\\$\{[a-zA-Z_]+\^\^" sdd/bin/sdd-fluxo.sh sdd/bin/sdd-decisoes-lint.sh; test $? -eq 1 && echo "(nenhum achado, nem em comentário)"'
cmdlog review-design-8 'for d in sdd/features/DESIGN_F[1-8]_*.md; do p=$(/bin/bash sdd/bin/sdd-fluxo.sh review-design "$d" | grep -oE "[0-9]+ arquivo\(s\) novo" | grep -oE "^[0-9]+"); f=$(zsh "$FONTE" review-design "$d" | grep -oE "[0-9]+ arquivo\(s\) Create" | grep -oE "^[0-9]+"); printf "%s porte=%s fonte=%s %s\n" "$(basename "$d")" "$p" "$f" "$([ "$p" = "$f" ] && echo igual || echo DIFERENTE)"; [ "$p" = "$f" ] || exit 1; done'
cmdlog loop-diferencial 'F=sdd/fixtures/fluxo; T=$(mktemp -d); mkdir "$T/inv"; cp $F/review-invalida/META.txt "$T/inv/"; printf "| a | s | v | r | e |\n|---|---|---|---|---|\n| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=3 | x |\n" > "$T/led3.md"; for caso in "A|--review $T/inv --rodada 1" "B|--review $F/review-ok --ledger $T/led3.md --rodada 3 --avaliacao $F/AVALIACAO_needs_work.md --ciclo-avaliador 1" "C|--review $F/review-ok --rodada 1 --avaliacao $F/AVALIACAO_recibo.md"; do n=${caso%%|*}; a=${caso#*|}; /bin/bash sdd/bin/sdd-fluxo.sh loop $a >/dev/null 2>&1; p=$?; zsh "$FONTE" loop $a >/dev/null 2>&1; f=$?; echo "caso $n: porte=$p fonte=$f"; [ "$p" = "$f" ] || exit 1; done; rm -rf "${T:?}"'
cmdlog linhas 'wc -l sdd/bin/sdd-fluxo.sh sdd/bin/sdd-decisoes-lint.sh sdd/templates/fragments/FLUXO_ENCADEADO.md tests/test_fluxo.py tests/test_decisoes_lint.py'
cmdlog escopo 'git diff --shortstat v2.2.9 HEAD && git diff --name-status v2.2.9 HEAD'
# Só os logs deste script e do build: os AVAL-*.log são sondas dos avaliadores, não evidência citada pelo
# relatório; a pasta inteira é conferida à parte e declarada no BUILD_REPORT.
cmdlog shell-da-f9 'find sdd/reports/evidence/F9_FLUXO -name "*.log" -not -name "AVAL*" -exec bash sdd/bin/gate-shell-evidencia.sh {} +'
cmdlog shell-da-f9-pasta-inteira 'bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F9_FLUXO'
rm -f "${FONTE:?}"
