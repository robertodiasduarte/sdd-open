#!/usr/bin/env bash
# AT-014 da F6: 3 sabotagens contra tests/test_docs.py e 1 contra o comandos-intactos.py, cada uma num clone temporário de HEAD (nunca na
# worktree). Cada sabotagem tem de deixar o módulo vermelho com o nome do teste; o clone limpo tem de
# sair verde. Piso: /usr/bin/python3 (3.9) e /bin/bash (3.2). Exit 0 = as 3 pegas e o limpo verde.
set -u
cd "$(git rev-parse --show-toplevel)" || exit 64
RAIZ="$(pwd)"
PY=/usr/bin/python3
falhas=0

roda() { # $1 = pasta do clone → imprime o resumo do unittest e devolve o exit
  (cd "${1}/tests" && "${PY}" -B -m unittest test_docs 2>&1) > "${1}.saida"
  local rc=$?
  grep -E '^(FAIL|ERROR):' "${1}.saida" | sed 's/^/    /'
  tail -1 "${1}.saida" | sed 's/^/    /'
  return "${rc}"
}

clone() { local d; d="$(mktemp -d)"; git clone -q . "${d}/c" && printf '%s\n' "${d}/c"; }

caso() { # $1 = nome  $2 = programa Python que sabota o clone (cwd = clone)
  local c; c="$(clone)" || { echo "não consegui clonar"; exit 64; }
  (cd "${c}" && "${PY}" -B -c "${2}") || { echo "sabotagem ${1}: a troca não aplicou"; falhas=$((falhas + 1)); return; }
  echo "── sabotagem: ${1}"
  if roda "${c}"; then echo "    ✗ verde com a sabotagem — o teste não pega"; falhas=$((falhas + 1));
  else echo "    ✓ vermelho"; fi
  d="${c%/c}"; rm -rf "${d:?}"
}

caso "link do sumário do guia aponta para âncora inexistente" '
from pathlib import Path
p = Path("docs/pt-BR/guia-do-aluno.md"); t = p.read_text(encoding="utf-8")
assert "(#9-glossário)" in t
p.write_text(t.replace("(#9-glossário)", "(#9-glossario-que-nao-existe)", 1), encoding="utf-8")'

caso "seção Por que cada regra existe apagada da sdd-build" '
import re
from pathlib import Path
p = Path(".agents/skills/sdd-build/SKILL.md"); t = p.read_text(encoding="utf-8")
n = re.sub(r"\n## Por que cada regra existe\n.*?(?=\n## )", "\n", t, flags=re.S)
assert n != t
p.write_text(n, encoding="utf-8")'

caso "Specs como deltas marcado ✅ na coluna do SDD Open (PT)" '
from pathlib import Path
p = Path("docs/pt-BR/comparison.md"); ls = p.read_text(encoding="utf-8").split("\n")
i = next(i for i, l in enumerate(ls) if l.startswith("| Specs como deltas"))
celulas = ls[i].rstrip().rstrip("|").split("|")
celulas[-1] = " ✅ "
ls[i] = "|".join(celulas) + "|"
p.write_text("\n".join(ls), encoding="utf-8")'

c="$(clone)"
echo "── sabotagem do próprio comandos-intactos.py: 1 palavra mudada no Quality Gate da sdd-build, commitada"
( cd "${c}" && "${PY}" -B -c '
from pathlib import Path
p = Path(".agents/skills/sdd-build/SKILL.md"); t = p.read_text(encoding="utf-8")
assert "Camadas contadas" in t
p.write_text(t.replace("Camadas contadas", "Camadas medidas", 1), encoding="utf-8")' \
  && git -c user.name=sabotagem -c user.email=sabotagem@example.com commit -qam sabotagem \
  && "${PY}" -B "${RAIZ}/sdd/reports/evidence/F6_DOCS/comandos-intactos.py" \
  ) > "${c}.saida" 2>&1
rc=$?
grep -E '^(OK|FALHA)|^skills:' "${c}.saida" | sed 's/^/    /'
if [ "${rc}" -ne 0 ] && grep -q '^FALHA sdd-build' "${c}.saida"; then echo "    ✓ vermelho na sdd-build"
else echo "    ✗ o script não acusou a mudança"; falhas=$((falhas + 1)); fi
d="${c%/c}"; rm -rf "${d:?}"

c="$(clone)"
echo "── clone limpo de HEAD"
if roda "${c}"; then echo "    ✓ verde"; else echo "    ✗ vermelho sem sabotagem"; falhas=$((falhas + 1)); fi
d="${c%/c}"; rm -rf "${d:?}"

echo "sabotagens: 4 · não pegas ou limpo vermelho: ${falhas}"
[ "${falhas}" -eq 0 ]
