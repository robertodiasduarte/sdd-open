#!/bin/bash
# R1@openrouter-deepseek-deepseek-v4-pro (rodada 4): "sem --ignored, ls-files --others não lista o que o .gitignore cobre".
# Mede o git de verdade, e o script real, num repositório temporário.
set -u
R="$(git rev-parse --show-toplevel)"; T="$(mktemp -d)"; trap 'rm -rf "${T:?}"' EXIT
git init -q "$T/p"; cd "$T/p" || exit 64
git -c user.name=p -c user.email=p@example.com commit -q --allow-empty -m base
mkdir -p sdd/features; printf 'sdd/features/\n' > .gitignore
printf 'x\n' > sdd/features/DEFINE_RELATORIO_MENSAL.md
echo '$ git check-ignore -v sdd/features/DEFINE_RELATORIO_MENSAL.md'; git check-ignore -v sdd/features/DEFINE_RELATORIO_MENSAL.md; echo "[exit=$?]"
echo '$ git ls-files --others -- sdd/features'; git ls-files --others -- sdd/features; echo "[exit=$?]"
echo '$ git ls-files --others --ignored -- sdd/features   # a correção proposta'; git ls-files --others --ignored -- sdd/features 2>&1; echo "[exit=$?]"
mkdir -p "$T/f"
echo '$ copiar-docs.sh <principal> <frente> relatorio-mensal'; bash "$R/.agents/skills/sdd-new-session/scripts/copiar-docs.sh" "$T/p" "$T/f" relatorio-mensal; echo "[exit=$?]"
echo '$ ls <frente>/sdd/features'; ls "$T/f/sdd/features"; echo "[exit=$?]"
