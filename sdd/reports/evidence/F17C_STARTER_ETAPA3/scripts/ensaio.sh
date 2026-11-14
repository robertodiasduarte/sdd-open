#!/usr/bin/env bash
# ensaio.sh <worktree do Open> <pasta de trabalho>: gera o starter da árvore de trabalho num clone da v1.5.18
set -u
W="$1"; D="$2"
rm -rf "$D" && mkdir -p "$D/open"
for rel in .agents/skills sdd/templates scripts/starter; do mkdir -p "$D/open/$(dirname $rel)"; cp -R "$W/$rel" "$D/open/$rel"; done
cp "$W/scripts/gerar-starter.py" "$D/open/scripts/gerar-starter.py"
find "$D/open" -name __pycache__ -prune -exec rm -rf {} + ; find "$D/open" -name .DS_Store -delete
cd "$D/open" && git init -q && git add -A && git -c user.name=t -c user.email=t@e commit -qm open && git tag v9.9.9
git clone -q /Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-ref "$D/starter" && git -C "$D/starter" checkout -q -B ensaio v1.5.18
python3 -B "$D/open/scripts/gerar-starter.py" --tag v9.9.9 "$D/starter"
echo "rc=$?"
