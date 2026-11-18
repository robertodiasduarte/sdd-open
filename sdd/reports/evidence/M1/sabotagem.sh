#!/usr/bin/env bash
# Sabotagem da M1: desfaz uma garantia por vez nos workflows, prova que
# test_release_workflow fica vermelho com o nome do teste, desfaz com git checkout e prova verde de novo.
# Roda da raiz da worktree, depois do commit (git checkout só desfaz arquivo rastreado). sed por
# padrão, nunca por número de linha.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
PY=/usr/bin/python3
export SDD_TEST_BASH=/bin/bash
SUITE=test_release_workflow.py
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

sabota .github/workflows/release.yml 's#^    needs: \[testes, testes-macos\]#    needs: testes#' \
  "release deixa de esperar o piso no macOS"
sabota .github/workflows/publish-gate.yml 's#^    runs-on: macos-latest#    runs-on: ubuntu-latest#' \
  "o job do piso deixa de rodar no macOS"
sabota .github/workflows/release.yml 's#fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 \# v5.1.0#11d5960a326750d5838078e36cf38b85af677262 \# v4.4.0#' \
  "um checkout volta ao v4.4.0 (Node 20)"
sabota .github/workflows/release.yml 's#\\u061c##' \
  "a varredura deixa de ver o ALM (controle bidi U+061C)"
sabota .github/workflows/release.yml 's#^          if not lidos:#          if False:#' \
  "revisão, nota 1: alvo vazio volta a passar sem varrer nada"
sabota .github/workflows/publish-gate.yml "s#; sys.exit(sys.version_info\[:2\] != (3, 9))'\$#'#" \
  "revisão, nota 2: o piso volta a ser só impresso"
sabota .github/workflows/release.yml 's#(source|\\.)\\s+<#(sourcex)\\s+<#' \
  "revisão, nota 3: source <(curl …) deixa de reprovar"
sabota .github/workflows/publish-gate.yml 's#sys.exit(1 if achados else 0)#sys.exit(0)#' \
  "a varredura do gate acha e não reprova"

echo "════"
git status --short -- .github
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
