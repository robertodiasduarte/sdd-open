#!/usr/bin/env bash
# verify-gate.sh <log>: o Verify Gate da F17c no HEAD, com o rc
cd /Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3 || exit 64
{ echo "\$ bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F17C_STARTER_ETAPA3.md   # HEAD $(git rev-parse --short HEAD)"
  start=$(date +%s); bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F17C_STARTER_ETAPA3.md; rc=$?
  echo "duração: $(( $(date +%s) - start )) s"; echo "rc=$rc"; } > "$1" 2>&1
