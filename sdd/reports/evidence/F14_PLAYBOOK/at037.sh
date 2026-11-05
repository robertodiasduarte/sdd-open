#!/bin/bash
# AT-037: nada muda no gate, no report-lint, na revisão adversarial nem nos hooks. Sai 0 só com o diff vazio.
d="$(git diff --name-only v2.5.0 HEAD -- sdd/bin/verify-gate.sh sdd/bin/report-lint.py sdd/bin/adversarial-review.sh sdd/hooks)"; rc=$?
printf 'diff: [%s]\n' "$d"
[ "$rc" -eq 0 ] && [ -z "$d" ]
