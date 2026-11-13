#!/usr/bin/env bash
# checagens-starter.sh <clone do starter> <base>: as checagens do CI do starter, uma por linha, com rc
set -u
cd "$1" || exit 64
BASE="$2"; falhas=0
roda() { echo "\$ $*"; "$@" > /tmp/checagem.$$ 2>&1 < /dev/null; rc=$?; tail -6 /tmp/checagem.$$; echo "rc=$rc"; [ $rc -eq 0 ] || falhas=$((falhas+1)); }
roda python3 -B scripts/check-gerado.py
roda bash scripts/publish-check.sh
roda python3 -B scripts/check-versions.py --base "$BASE"
roda bash -c 'python3 -m py_compile skills/*/scripts/*.py scripts/*.py'
roda bash -c 'for f in scripts/package.sh scripts/publish-check.sh skills/*/scripts/*.sh; do bash -n "$f" || exit 1; done'
roda bash -c 'for t in skills/*/tests; do [ -d "$t" ] || continue; python3 -B -m unittest discover -s "$t" -p "test_*.py" || exit 1; done'
roda bash -c 'if [ -d tests ]; then python3 -B -m unittest discover -s tests -p "test_*.py"; fi'
roda bash skills/sdd-kb/scripts/gate.sh
roda bash scripts/package.sh
rm -f /tmp/checagem.$$
echo "falhas=$falhas"
[ $falhas -eq 0 ]
