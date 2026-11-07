#!/bin/bash
# r7-repro.sh — mede o R1@claude da rodada 7: ficha e documento em caixas diferentes no sdd-archive.py
A="$1"; T="$(mktemp -d)"; cd "$T" || exit 2
git init -q . && git config user.email a@example.com && git config user.name a
mkdir -p sdd/handoffs sdd/reports sdd/features
printf '| **Status** | aberta |\n' > sdd/handoffs/HANDOFF_minha-frente.md
printf '| **Status** | aberta |\n' > sdd/handoffs/HANDOFF_Outra_s2.md
echo x > sdd/reports/BUILD_REPORT_MINHA-FRENTE.md; echo x > sdd/features/DEFINE_OUTRA.md; echo x > sdd/reports/NOTAS_MINHA-FRENTE.txt
git add -A && GIT_COMMITTER_DATE=2026-01-01T12:00:00 git commit -q --date 2026-01-01T12:00:00 -m c
/usr/bin/python3 -B "$A" --hoje 2026-11-05; rc=$?
cd / && rm -rf "${T:?}"; exit $rc
