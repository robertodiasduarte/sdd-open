#!/usr/bin/env bash
# Builds one distributable zip per skill into dist/.
# Zips contain the skill folder at the archive root (e.g. sdd-define/SKILL.md).
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p dist
rm -f dist/*.zip

for dir in skills/*/; do
  name="$(basename "$dir")"
  (cd skills && zip -r -q -X "../dist/${name}.zip" "$name" \
    -x "*.DS_Store" -x "*__MACOSX*" -x "*.pyc" -x "*__pycache__*")
  echo "packaged dist/${name}.zip"
done

echo "PASS: $(ls dist/*.zip | wc -l | tr -d ' ') skill zips built in dist/"
