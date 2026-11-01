"""Piso bash 3.2 (o /bin/bash do macOS) nos scripts de sdd/bin/ e nos hooks de sdd/hooks/: nada de mapfile,
declare -A nem as expansões de caixa (`^^`, `,,`), que só existem no bash 4+. Comentário não conta.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

BASHISMO = re.compile(r"mapfile|readarray|declare -A|\$\{[a-zA-Z_]+(?:\^\^|,,)")
NOVOS = ("gate-baseline.sh", "gate-shell-evidencia.sh", "avaliador-guard.sh", "test-baseline.sh",
         "adversarial-review.sh")


class Bash32(unittest.TestCase):
    def test_sem_bashismo_em_sdd_bin(self):
        scripts = (sorted((RAIZ / "sdd/bin").glob("*.sh")) + sorted((RAIZ / "sdd/bin/adapters").glob("*.sh"))
                   + sorted((RAIZ / "sdd/hooks").glob("pre-*")) + [RAIZ / "sdd/fixtures/revisao/adapters/stub.sh"])
        self.assertGreaterEqual(len(scripts), 13)
        self.assertIn(RAIZ / "sdd/bin/adapters/openrouter.sh", scripts)
        self.assertIn(RAIZ / "sdd/hooks/pre-commit", scripts)
        for s in scripts:
            for n, linha in enumerate(s.read_text(encoding="utf-8").splitlines(), 1):
                if linha.lstrip().startswith("#"):
                    continue
                with self.subTest(script=s.name, linha=n):
                    self.assertIsNone(BASHISMO.search(linha), linha)

    def test_os_scripts_novos_existem_e_awk_de_log_usa_lc_all_c(self):
        for nome in NOVOS:
            self.assertTrue((RAIZ / "sdd/bin" / nome).is_file(), nome)
        texto = (RAIZ / "sdd/bin/gate-shell-evidencia.sh").read_text(encoding="utf-8")
        for linha in texto.splitlines():
            if re.search(r"\bawk -f\b", linha):
                self.assertIn("LC_ALL=C awk", linha)

    def test_o_padrao_pega_o_que_deve(self):
        for ruim in ("mapfile -t x < f", 'echo "${nome^^}"', 'echo "${nome,,}"', "declare -A mapa"):
            self.assertIsNotNone(BASHISMO.search(ruim), ruim)
        self.assertIsNone(BASHISMO.search('echo "${nome:-x}"'))


if __name__ == "__main__":
    unittest.main()
