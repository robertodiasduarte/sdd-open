#!/bin/bash
# r1-repro.sh — R1@claude da rodada 1: o verify-gate sem --strict devolve 0 no inconclusivo? Gate real, sem stub.
R="$(git rev-parse --show-toplevel)"
T="$(mktemp -d)"; cd "$T" || exit 64
git init -q; git symbolic-ref HEAD refs/heads/frente
mkdir -p sdd/bin sdd/features
cp "$R"/sdd/bin/verify-gate.sh "$R"/sdd/bin/sdd-drive.sh "$R"/sdd/bin/sdd-fluxo.sh "$R"/sdd/bin/design-lint.py sdd/bin/
printf 'import sys\nsys.exit(0)\n' > sdd/bin/report-lint.py
def() { printf '# D\n\n## Technical Context\n\n| Aspect | Value | Notes |\n|---|---|---|\n| **Governança** | N.A. — t | t |\n\n## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n  cmd: "%s"\n  pass_when: "exit 0"\n  threshold: "—"\n  manual_fallback: "—"\n```\n' "$1" > sdd/features/DEFINE_F.md; }
def "ferramenta-que-nao-existe --testa"
git add -A; git -c user.name=t -c user.email=t@example.com commit -qm base
bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F.md; echo "[verify-gate sem --strict: exit=$?]"
bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F.md; echo "[verify-gate --strict: exit=$?]"
printf '# DESIGN\n\n## Metadata\n\n| Attribute | Value |\n|---|---|\n| **Status** | Ready for Build |\n\n## Key Decisions\n\n### Decision 1: x\n\nx\n\n## File Manifest\n\n| # | File | Action | Purpose | Agent / Owner | Dependencies |\n|---:|---|---|---|---|---|\n| 1 | `a` | Modify | x | (general) | None |\n\n**Total Files:** 1\n' > sdd/features/DESIGN_F.md
git add -A; git -c user.name=t -c user.email=t@example.com commit -qm d
bash sdd/bin/sdd-drive.sh iniciar sdd/features/DEFINE_F.md >/dev/null
mkdir -p sdd/reports/progress; printf -- '- [x] a\n' > sdd/reports/progress/PROGRESS_F.md
bash sdd/bin/sdd-drive.sh verificar sdd/features/DEFINE_F.md; echo "[drive verificar: exit=$?]"
tail -2 sdd/reports/evidence/F/DRIVE-gate-r1.log
