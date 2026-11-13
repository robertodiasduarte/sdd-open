#!/usr/bin/env bash
# copias.sh <log>: o que a revisão deixou de fora (--paths) comparado à v1.5.17 publicada do starter
W=/Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2; S=/Users/robertoduarte/rdd-public/sdd-starter; T="$(mktemp -d)"
git -C "$S" archive v1.5.17 docs exemplos tests skills/ux-review-builder | tar -x -C "$T"
{ echo "\$ diff -rq <starter v1.5.17>/{docs,exemplos,tests,skills/ux-review-builder} <open $(git -C $W rev-parse --short HEAD)>/{scripts/starter/raiz/...,.agents/skills/ux-review-builder}"
  cd "$W"
  for p in docs exemplos tests; do diff -rq "$T/$p" "scripts/starter/raiz/$p"; done
  diff -rq "$T/skills/ux-review-builder" .agents/skills/ux-review-builder
  echo "arquivos comparados: $(find "$T" -type f | wc -l | tr -d ' ')"
  echo "os que diferem e estavam nas --paths da revisão: quickstart.md, quickstart.pt-BR.md, ux-review-builder/{SKILL.md,CHANGELOG.md,references/como-falar.md}"
  echo "os que diferem fora das --paths: ux-review-builder/{evals/cases.json,manifest.json} (só a versão: $(git diff --no-index -U0 "$T/skills/ux-review-builder/manifest.json" .agents/skills/ux-review-builder/manifest.json | grep '^[-+] ' | tr '\n' ' '))"
  echo "rc=0"; } 
rm -rf "$T"
