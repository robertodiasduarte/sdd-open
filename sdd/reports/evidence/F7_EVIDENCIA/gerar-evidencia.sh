#!/usr/bin/env bash
# Gera a evidência da F7 no piso (/usr/bin/python3 3.9 + /bin/bash 3.2). 1ª linha de cada log = o
# comando; depois a saída verbatim; por fim `[exit=N]` com o rc do COMANDO, capturado antes de qualquer
# pipe (a regra que a própria F7 cobra). Roda da raiz da worktree, depois do commit.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
E=sdd/reports/evidence/F7_EVIDENCIA
export SDD_TEST_BASH=/bin/bash

cmdlog() { # $1=nome do log $2=comando (bash -c)
  local out rc
  out="$(bash -c "${2}" 2>&1)"; rc=$?
  { printf '$ %s\n' "${2}"; printf '%s\n' "${out}" | grep -v ResourceWarning | tail -n 200; printf '[exit=%s]\n' "${rc}"; } > "${E}/${1}.log"
  printf '%s [exit=%s]\n' "${1}" "${rc}"
}

cmdlog relatorios-do-open '/usr/bin/python3 -B -c "
import re, subprocess
for f in (\"F1_MANUTENCAO\", \"F2_TERRENO\", \"F3_BUILD_RELEASE\", \"F4_CONVERSA\", \"F5_CONHECIMENTO\", \"F6_DOCS\", \"M1\", \"W0\"):
    p = subprocess.run([\"/usr/bin/python3\", \"-B\", \"sdd/bin/report-lint.py\", \"sdd/reports/BUILD_REPORT_%s.md\" % f], capture_output=True, text=True)
    classes = sorted(set(re.findall(r\"^🛑 \[([^]]+)\]\", p.stderr, re.M)))
    print(\"BUILD_REPORT_%s.md rc=%d classes=%s\" % (f, p.returncode, classes))
"'
cmdlog corpus-shell 'bash sdd/bin/gate-shell-evidencia.sh $(ls -d sdd/reports/evidence/*/ | grep -v F7_EVIDENCIA)'
cmdlog corpus-shell-diff 'bash sdd/bin/gate-shell-evidencia.sh $(ls -d sdd/reports/evidence/*/ | grep -v F7_EVIDENCIA) > "$TMPDIR/c.txt"; sed -n "s/^🛑 \([^ ]*\.log:[0-9]*\).*/\1/p" "$TMPDIR/c.txt" > "$TMPDIR/n0.txt"; LC_ALL=C sort -o "$TMPDIR/n.txt" "$TMPDIR/n0.txt"; diff sdd/reports/evidence/F7_EVIDENCIA/corpus-esperado.txt "$TMPDIR/n.txt" && echo "(diff vazio: as $(grep -c . "$TMPDIR/n.txt") acusações são as esperadas)"'
cmdlog saidas-v2.2.7 'S=$(mktemp -d) && git init -q "$S" && mkdir -p "$S/sdd/bin" && cp sdd/fixtures/DEFINE_FIXTURE_*.md "$S/" && git show v2.2.7:sdd/bin/verify-gate.sh > "$S/velho.sh" && cp sdd/bin/verify-gate.sh "$S/novo.sh" && cd "$S" && for f in DEFINE_FIXTURE_*.md; do for fl in "" --strict --print; do bash velho.sh $fl $f > a.txt 2>&1; ra=$?; SDD_TRACE=off bash novo.sh $fl $f > b.txt 2>&1; rb=$?; bash novo.sh $fl $f > c.txt 2>&1; rc=$?; if cmp -s a.txt b.txt && cmp -s a.txt c.txt && [ $ra = $rb ] && [ $ra = $rc ]; then r=igual; else r=DIFERENTE; fi; echo "$f [$fl] v2.2.7=$ra off=$rb on=$rc saida=$r"; done; done; ls sdd/traces; cd /; rm -rf "${S:?}"'
cmdlog check-versions 'python3 -B scripts/check-versions.py --base v2.2.7 --base-obrigatoria && for s in build release; do printf "sdd-%s %s → %s\n" "$s" "$(sed -n "s/^  version: \"\(.*\)\"$/\1/p" <(git show v2.2.7:.agents/skills/sdd-$s/SKILL.md))" "$(sed -n "s/^  version: \"\(.*\)\"$/\1/p" .agents/skills/sdd-$s/SKILL.md)"; done'
cmdlog skill-lint-conversa '/usr/bin/python3 -B sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md'
cmdlog bash32 'grep -nE "mapfile|declare -A|\\\$\{[a-zA-Z_]+\^\^" sdd/bin/*.sh | grep -vE "^[^:]+:[0-9]+:[[:space:]]*#"; test $? -eq 1 && echo "(nenhum bashismo fora de comentário em $(ls sdd/bin/*.sh | grep -c .) scripts)"'
cmdlog linhas 'wc -l .agents/skills/sdd-build/SKILL.md .agents/skills/sdd-release/SKILL.md sdd/bin/report-lint.py sdd/bin/verify-gate.sh sdd/bin/gate-baseline.sh sdd/bin/gate-shell-evidencia.sh sdd/bin/avaliador-guard.sh sdd/bin/test-baseline.sh'
cmdlog escopo 'git diff --stat v2.2.7 HEAD && git diff --name-status v2.2.7 HEAD'
cmdlog contratos-report-lint 'git diff v2.2.7 HEAD -- tests/test_report_lint.py'
cmdlog baseline 'T=$(mktemp -d) && git archive v2.2.7 | tar -x -C "$T" && cp tests/test_report_lint_evidencia.py tests/test_verify_gate_trace.py tests/test_gate_baseline.py tests/test_gate_shell_evidencia.py tests/test_avaliador_guard.py tests/test_test_baseline.py tests/test_bash32.py "$T/tests/" && cp -R sdd/fixtures/evidencia "$T/sdd/fixtures/" && cd "$T/tests" && /usr/bin/python3 -B -m unittest test_report_lint_evidencia test_verify_gate_trace test_gate_baseline test_gate_shell_evidencia test_avaliador_guard test_test_baseline test_bash32 > "$T/saida.txt" 2>&1; rc=$?; grep -E "^(FAIL|ERROR|Ran|OK|FAILED)" "$T/saida.txt"; cd /; rm -rf "${T:?}"; exit $rc'
cmdlog baseline-ciclo1 'T=$(mktemp -d) && git archive 514324f | tar -x -C "$T" && cp tests/test_verify_gate_trace.py tests/test_gate_shell_evidencia.py tests/test_test_baseline.py tests/test_report_lint_evidencia.py tests/test_avaliador_guard.py tests/test_contrato_build_release.py "$T/tests/" && cd "$T/tests" && /usr/bin/python3 -B -m unittest test_verify_gate_trace test_gate_shell_evidencia test_test_baseline test_report_lint_evidencia test_avaliador_guard test_contrato_build_release > "$T/saida.txt" 2>&1; rc=$?; grep -E "^(FAIL|ERROR|Ran|OK|FAILED)" "$T/saida.txt"; cd /; rm -rf "${T:?}"; exit $rc'
cmdlog baseline-ciclo2 'T=$(mktemp -d) && git archive bed1f69 | tar -x -C "$T" && cp tests/test_test_baseline.py tests/test_avaliador_guard.py tests/test_report_lint_evidencia.py tests/test_gate_shell_evidencia.py tests/test_verify_gate_trace.py "$T/tests/" && cd "$T/tests" && /usr/bin/python3 -B -m unittest test_test_baseline test_avaliador_guard test_report_lint_evidencia test_gate_shell_evidencia test_verify_gate_trace > "$T/saida.txt" 2>&1; rc=$?; grep -E "^(FAIL|ERROR|Ran|OK|FAILED)" "$T/saida.txt"; cd /; rm -rf "${T:?}"; exit $rc'
cmdlog shell-da-f7 'bash sdd/bin/gate-shell-evidencia.sh sdd/reports/evidence/F7_EVIDENCIA'
cmdlog GATE 'bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F7_EVIDENCIA.md'
