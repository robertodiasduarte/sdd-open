#!/usr/bin/env bash
# Sabotagem da W0: devolve ao texto cada um dos defeitos corrigidos (4.1 a 4.5), prova que
# test_correcoes_w0 fica vermelho com o nome do teste, desfaz com git checkout e prova verde de novo.
# Roda da raiz da worktree, depois do commit (git checkout só desfaz arquivo rastreado). sed por
# padrão, nunca por número de linha.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
PY=/usr/bin/python3
export SDD_TEST_BASH=/bin/bash
SUITE=test_correcoes_w0.py
falhas=0

sabota() { # $1=arquivo $2=sed $3=descrição
  local f="${1}" expr="${2}" desc="${3}" out rc
  echo "════ ${f} — ${desc}"
  git diff --quiet -- "${f}" || { echo "ABORTA: ${f} já tem mudança local"; falhas=$((falhas + 1)); return; }
  sed -i '' -e "${expr}" "${f}"
  echo "-- diff da sabotagem:"; git diff -U0 -- "${f}" | grep '^[-+][^-+]'
  git diff --quiet -- "${f}" && { echo "!! o sed não casou nada"; falhas=$((falhas + 1)); return; }
  out="$(${PY} -B -m unittest discover -s tests -p "${SUITE}" 2>&1)"; rc=$?
  echo "-- suíte ${SUITE} com a sabotagem: rc=${rc}"
  printf '%s\n' "${out}" | grep -E '^(FAIL|ERROR):|^Ran |^FAILED|^OK'
  [ "${rc}" -ne 0 ] || { echo "!! a suíte NÃO ficou vermelha"; falhas=$((falhas + 1)); }
  git checkout -- "${f}"
  out="$(${PY} -B -m unittest discover -s tests -p "${SUITE}" 2>&1)"; rc=$?
  echo "-- depois de git checkout -- ${f}: rc=${rc}"; printf '%s\n' "${out}" | grep -E '^Ran |^OK|^FAILED'
  [ "${rc}" -eq 0 ] || { echo "!! não voltou ao verde"; falhas=$((falhas + 1)); }
}

sabota .agents/skills/sdd-iterate/SKILL.md 's#`sdd/bin/verify-gate.sh <DEFINE>`#`sdd/bin/verify-gate.sh --print <DEFINE>`#' \
  "4.1: o passo 4 volta a rodar só --print (isento de marcador)"
sabota sdd/config.example.yaml 's#de nova sessão (sdd-new-session)\.#de nova sessão (slice 2).#' \
  "4.2: o rótulo velho volta ao config.example.yaml"
sabota sdd/templates/fragments/CLARIFY.md 's#`/build` e a fase Release \*\*param#`/build`, a fase Release e `/drive` **param#' \
  "4.3: /drive volta a ser citado"
sabota sdd/templates/fragments/EVIDENCIA.md 's#`sdd/bin/report-lint.py`, que confere#`.githooks/claude-build-report-guard.py`, que confere#' \
  "4.4: o guard inexistente volta ao cabeçalho"
sabota sdd/templates/BUILD_REPORT_TEMPLATE.md 's#^> O `sdd/bin/report-lint.py` nega `PASS`#> O hook `build-report-guard` nega `PASS`#' \
  "4.4 (revisão, nota 3): o hook inexistente volta ao bloco do avaliador"
sabota AGENTS.md.tmpl '1s#$# · /drive#' \
  "4.3 (revisão, nota 3): /drive fora de sdd/ e .agents/, num arquivo do pacote"
sabota .agents/skills/sdd-iterate/SKILL.md 's#Com `kind` `smoke` ou `eval`#Com `kind` qualquer#' \
  "4.1 (revisão, nota 2): o aviso de smoke/eval some do passo 4"
sabota .agents/skills/sdd-build/references/contexto-fresco.md \
  '/Rode as sondas read-only/,/CONTRATO/s/Não edite código nem documento do projeto:/Não escreva em arquivo algum;/' \
  "4.5: o brief de contrato volta a proibir qualquer arquivo"

echo "════"
git status --short -- .agents sdd/templates sdd/config.example.yaml AGENTS.md.tmpl
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
