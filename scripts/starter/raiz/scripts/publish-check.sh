#!/usr/bin/env bash
# Content safety gate: fails (exit 1) if any pattern that must never ship
# appears in the repository content. Runs locally and in CI. Fail-closed:
# a hit on any pattern blocks the release until resolved.
set -uo pipefail
cd "$(dirname "$0")/.."

# Everything except VCS internals, build output, this script itself (it necessarily contains the
# patterns it greps for) and GERADO.txt: a sha256 written in full often has 11 digits in a row and would
# be read as a CPF. GERADO.txt is written by the sdd-open generator and checked by check-gerado.py.
SCAN_ARGS=(-rIEn --exclude-dir=.git --exclude-dir=dist --exclude-dir=node_modules \
  --exclude=publish-check.sh --exclude=GERADO.txt)

PATTERNS=(
  '[0-9]{11}'                                        # CPF-like 11-digit runs
  '\+55[0-9]{8,}'                                    # Brazilian phone numbers
  '[[:alnum:]._%+-]+@(gmail|hotmail|outlook|yahoo|uol|terra)\.'   # personal emails
  'sk-[A-Za-z0-9]{20,}'                              # API-key-like tokens
  'eyJ[A-Za-z0-9_-]{30,}\.'                          # JWT-like tokens
  'AKIA[0-9A-Z]{16}'                                 # AWS access keys
  '-----BEGIN [A-Z ]*PRIVATE KEY-----'               # private key material
)

fail=0
for p in "${PATTERNS[@]}"; do
  hits="$(grep "${SCAN_ARGS[@]}" -- "$p" . 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    echo "FAIL: pattern matched: $p"
    echo "$hits" | head -20
    fail=1
  fi
done

# Skills that talk to the student (Grupos 1 e 2 da frente LINGUAGEM_ALUNO): without the section
# "## Como falar com o aluno" (and, for Grupo 2, references/como-falar.md) the skill does not ship.
ALUNO_SKILLS="sdd-release sdd-new-session sdd-higiene-dado sdd-brainstorm sdd-define sdd-design sdd-build sdd-handoff sdd-kb ux-review-builder"
ALUNO_COM_REFERENCIA="sdd-brainstorm sdd-define sdd-design sdd-build sdd-handoff sdd-kb ux-review-builder"
for s in $ALUNO_SKILLS; do
  if ! grep -q '^## Como falar com o aluno' "skills/$s/SKILL.md"; then
    echo "FAIL: skills/$s/SKILL.md sem a seção '## Como falar com o aluno'"
    fail=1
  fi
done
for s in $ALUNO_COM_REFERENCIA; do
  if [ ! -f "skills/$s/references/como-falar.md" ]; then
    echo "FAIL: skills/$s/references/como-falar.md ausente"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "publish-check: FAIL — resolve the hits above before publishing."
  exit 1
fi
echo "PASS: publish-check found no forbidden content."
