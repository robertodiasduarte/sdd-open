#!/usr/bin/env bash
# Sabotagem da F4: desfaz uma garantia por vez (nos 3 lints, na lista do test_agnostico e no texto de uma
# skill), prova que a suíte nomeada fica vermelha com o nome do teste, desfaz com git checkout e prova
# verde de novo. Roda da raiz da worktree, depois do commit. sed por padrão, nunca por número de linha.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
PY=/usr/bin/python3
export SDD_TEST_BASH=/bin/bash
falhas=0

sabota() { # $1=arquivo $2=sed $3=suíte $4=descrição
  local f="${1}" expr="${2}" suite="${3}" desc="${4}" out rc
  echo "════ ${f} — ${desc}"
  git diff --quiet -- "${f}" || { echo "ABORTA: ${f} já tem mudança local"; falhas=$((falhas + 1)); return; }
  sed -i '' -e "${expr}" "${f}"
  echo "-- diff da sabotagem:"; git diff -U0 -- "${f}" | grep '^[-+][^-+]'
  git diff --quiet -- "${f}" && { echo "!! o sed não casou nada"; falhas=$((falhas + 1)); return; }
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- suíte ${suite} com a sabotagem: rc=${rc}"
  printf '%s\n' "${out}" | grep -E '^(FAIL|ERROR):|^Ran |^FAILED|^OK'
  [ "${rc}" -ne 0 ] || { echo "!! a suíte NÃO ficou vermelha"; falhas=$((falhas + 1)); }
  git checkout -- "${f}"
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- depois de git checkout -- ${f}: rc=${rc}"; printf '%s\n' "${out}" | grep -E '^Ran |^OK|^FAILED'
  [ "${rc}" -eq 0 ] || { echo "!! não voltou ao verde"; falhas=$((falhas + 1)); }
}

sabota sdd/bin/skill-lint.py 's#if "não sei" not in rotulos:#if False:#' test_skill_lint.py \
  "skill-lint --conversa deixa de exigir a opção \"não sei\""
sabota sdd/bin/design-lint.py 's#if c is not None:#if False:#' test_design_lint.py \
  "design-lint deixa de reprovar dependência em ciclo"
sabota sdd/bin/handoff-lint.py 's#m = PLACEHOLDER_EM_CODIGO.search(ln)#m = None#' test_handoff_lint.py \
  "handoff-lint deixa de ver placeholder dentro do prompt de retomada"
sabota tests/test_agnostico.py 's#(AskUserQuestion|#(#' test_agnostico.py \
  "test_agnostico deixa de proibir AskUserQuestion"
sabota .agents/skills/sdd-build/references/como-falar.md '/^- \*\*não sei\*\* —/d' test_skill_lint.py \
  "a pergunta de exemplo da sdd-build perde a opção \"não sei\""
sabota .agents/skills/sdd-define/SKILL.md 's#^Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:$#> Abra a resposta com o banner: `🧠 DEFINE (Fase 1)`.#' test_conversa.py \
  "o banner volta à sdd-define"

echo "════"
git status --short -- sdd/bin tests .agents
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
