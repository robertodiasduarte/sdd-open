#!/bin/bash
# baseline.sh — os testes da F11 (novos e alterados) rodados contra o código da v2.3.0: precisam ficar vermelhos.
set -u
R="$(git rev-parse --show-toplevel)"
T=$(mktemp -d)
git -C "$R" archive v2.3.0 | tar -x -C "$T"
for f in test_revisao_gate.py test_eval_agree.py test_revisao.py test_revisao_adapters.py test_release_workflow.py test_docs.py; do
  cp "$R/tests/$f" "$T/tests/$f"
done
cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_revisao_gate.py' 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK"
cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_eval_agree.py' 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK"
cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_revisao*.py' -k F11Adiados -k test_f11 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK"
cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_release_workflow.py' 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK"
cd "$T" && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_docs.py' 2>&1 | grep -E "^(FAIL|ERROR):|^Ran|^FAILED|^OK"
rm -rf "${T:?}"
# o veredito: na v2.3.0 os testes da F11 têm de falhar
exit 0
