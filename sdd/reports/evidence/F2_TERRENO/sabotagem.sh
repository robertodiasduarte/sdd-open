#!/usr/bin/env bash
# Sabotagem da F2: quebra UMA linha de cada script portado e do doctor, prova que a suíte dele fica
# vermelha com o nome do teste, desfaz com git checkout e prova verde de novo. Roda da raiz da worktree,
# depois do commit (git checkout só desfaz arquivo rastreado).
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
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- suíte ${suite} com a sabotagem: rc=${rc}"
  printf '%s\n' "${out}" | grep -E '^(FAIL|ERROR):|^Ran |^FAILED|^OK'
  [ "${rc}" -ne 0 ] || { echo "!! a suíte NÃO ficou vermelha"; falhas=$((falhas + 1)); }
  git checkout -- "${f}"
  out="$(${PY} -B -m unittest discover -s tests -p "${suite}" 2>&1)"; rc=$?
  echo "-- depois de git checkout -- ${f}: rc=${rc}"; printf '%s\n' "${out}" | grep -E '^Ran |^OK|^FAILED'
  [ "${rc}" -eq 0 ] || { echo "!! não voltou ao verde"; falhas=$((falhas + 1)); }
}

sabota .agents/skills/sdd-checar-ambiente/scripts/checar.sh 's/\*\.pfx|\*\.p12)/*.pfx)/' test_checar.py \
  "certificado .p12 deixa de ser dado exposto"
sabota .agents/skills/sdd-higiene-dado/scripts/alarme.sh "s/grep -v -F 'sdd-open:generated'/cat/" test_alarme.py \
  "instalar deixa de tirar o cabeçalho sdd-open:generated do hook"
sabota .agents/skills/sdd-higiene-dado/scripts/pre-commit.sh 's/return r == substr(s, 11, 1) + 0/return 1/' test_alarme.py \
  "2º dígito verificador do CPF deixa de ser conferido"
sabota .agents/skills/sdd-iniciar-repo/scripts/inventario.sh 's/^LIMITE_MB=50 /LIMITE_MB=500 /' test_inventario.py \
  "arquivo de 55–60 MB deixa de ser sinalizado como grande"
sabota bin/sdd-open.sh '/--segredo 2>&1)"; rc=\$?/s/.*/    saida=""; rc=0/' test_sdd_open.py \
  "doctor deixa de chamar o checar.sh --segredo"

echo "════"
git status --short -- .agents bin
echo "sabotagens sem prova: ${falhas}"
exit "${falhas}"
