#!/usr/bin/env bash
# Sabotagem da F1: quebra UMA linha de cada script, prova que a suíte fica vermelha com o nome do
# teste, desfaz com git checkout e prova verde de novo. Roda da raiz da worktree.
set -u
PY=/usr/bin/python3
falhas=0

sabota() { # $1=arquivo $2=sed $3=suite $4=descrição
  local f="${1}" expr="${2}" suite="${3}" desc="${4}" out rc
  echo "════ ${f} — ${desc}"
  git diff --quiet -- "${f}" || { echo "ABORTA: ${f} já tem mudança local"; falhas=$((falhas + 1)); return; }
  sed -i '' -e "${expr}" "${f}"
  echo "-- diff da sabotagem:"; git diff -U0 -- "${f}" | grep '^[-+][^-+]'
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- suíte ${suite} com a sabotagem: rc=${rc}"
  printf '%s\n' "${out}" | grep -E '^(FAIL|ERROR):|^Ran |^FAILED|^OK'
  [ "${rc}" -ne 0 ] || { echo "!! a suíte NÃO ficou vermelha"; falhas=$((falhas + 1)); }
  git checkout -- "${f}"
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- depois de git checkout -- ${f}: rc=${rc}"; printf '%s\n' "${out}" | grep -E '^Ran |^OK|^FAILED'
  [ "${rc}" -eq 0 ] || { echo "!! não voltou ao verde"; falhas=$((falhas + 1)); }
}

sabota sdd/bin/verify-gate.sh '82s/finalizar 5/finalizar 2/' test_verify_gate.py \
  "marcador ativo de clarificação sai 2 em vez de 5"
sabota sdd/bin/report-lint.py '62s/if FAKE_RE.search(cell):/if False and FAKE_RE.search(cell):/' test_report_lint.py \
  "'deve funcionar' deixa de ser negado"
sabota sdd/bin/skill-lint.py '98s/> 1024/> 2048/' test_skill_lint.py \
  "limite da description vai de 1024 para 2048"
sabota sdd/bin/playbook-lint.sh '159s/return 2/return 0/' test_playbook_lint.py \
  "playbook com formato inválido sai 0"
sabota bin/sdd-open.sh '342s/DIVERGENTES + 1/DIVERGENTES + 0/' test_sdd_open.py \
  "sync --check deixa de contar cópia gerada desatualizada"
sabota scripts/check-versions.py '83s/semver(v) <= semver(ov)/semver(v) < semver(ov)/' test_check_versions.py \
  "skill alterada com a mesma versão passa"

echo "════"
git status --short -- sdd/bin bin scripts
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
