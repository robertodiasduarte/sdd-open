#!/usr/bin/env bash
# verify-gate.sh <log>: o Verify Gate da F16W no HEAD, com o rc
cd "$(git rev-parse --show-toplevel)" || exit 64
{ echo "\$ bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F16W_WINDOWS.md   # HEAD $(git rev-parse --short HEAD)"
  start=$(date +%s); bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F16W_WINDOWS.md; rc=$?
  echo "duração: $(( $(date +%s) - start )) s"; echo "rc=$rc"; } > "$1" 2>&1
