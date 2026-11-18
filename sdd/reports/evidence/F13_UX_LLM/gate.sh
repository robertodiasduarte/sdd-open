#!/bin/bash
# Roda o Verify Gate do commit atual e grava o log com o exit real.
cd "$(git rev-parse --show-toplevel)" || exit 64
sha="$(git rev-parse --short HEAD)"; log="sdd/reports/evidence/F13_UX_LLM/verify-gate-$sha.log"
t0=$(date +%s)
out=$(bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F13_UX_LLM.md 2>&1); rc=$?
{ printf '$ bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F13_UX_LLM.md   # HEAD=%s\n' "$sha"; printf '%s\n' "$out"; printf 'segundos: %s\n' "$(( $(date +%s) - t0 ))"; printf '[exit=%s]\n' "$rc"; } > "$log"
echo "$log rc=$rc"; exit "$rc"
