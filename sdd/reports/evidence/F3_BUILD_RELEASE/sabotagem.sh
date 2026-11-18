#!/usr/bin/env bash
# Sabotagem da F3: quebra UMA regra de cada script alterado (report-lint.py, deploy-espera-testes.py,
# doctor do sdd-open.sh), prova que a suíte dele fica vermelha com o nome do teste, desfaz com
# git checkout e prova verde de novo. Roda da raiz da worktree, depois do commit (git checkout só
# desfaz arquivo rastreado). sed por padrão, nunca por número de linha.
set -u
PY=/usr/bin/python3
export SDD_TEST_BASH=/bin/bash
falhas=0

sabota() { # $1=arquivo $2=sed $3=suite $4=descrição
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

sabota sdd/bin/report-lint.py '/aplicada onde? provada como?/s/violations\.append(.*/pass/' test_report_lint.py \
  "migration listada sem linha em ## Migrations aplicadas deixa de reprovar"
sabota .agents/skills/sdd-release/scripts/deploy-espera-testes.py \
  's/if verdade(st\.get("continue-on-error")):/if False:/' test_deploy_espera_testes.py \
  "continue-on-error no passo de teste deixa de contar como não segura"
sabota bin/sdd-open.sh '/cmp -s "\${f}"/s/.*/    continue/' test_sdd_open.py \
  "doctor deixa de comparar sdd/bin/ com o pacote"

echo "════"
git status --short -- .agents bin sdd/bin
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
