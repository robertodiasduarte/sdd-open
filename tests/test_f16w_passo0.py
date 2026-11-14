"""F16W, passo 0: as sobras da F17c que o Roberto pôs nesta frente (2026-11-14).

A curadoria do playbook da F17c: LM-027 e LM-028 entram; as 12 contagens "ajudou" e as 2 sugestões de "mordeu"
da colheita ficam de fora (decisão do Roberto).
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Curadoria(unittest.TestCase):
    def test_as_duas_licoes_da_f17c_estao_no_playbook(self):
        pb = ler("sdd/playbook.md")
        for lm, trecho in (("LM-027", '`claude -p --tools ""` não simula a web'),
                           ("LM-028", "Um juiz por expressão regular de comportamento de LLM")):
            with self.subTest(lm=lm):
                linha = next((ln for ln in pb.split("\n") if ln.startswith("- [%s]" % lm)), "")
                self.assertIn(trecho, linha)
                self.assertIn("**Do instead:**", linha)
                self.assertIn("conf=2026-11-14", linha)

    def test_as_contagens_da_f17c_nao_foram_aplicadas(self):
        # Roberto, 2026-11-14: só as 2 lições entram; nenhuma lição antiga ganhou conf=2026-11-14
        pb = ler("sdd/playbook.md")
        datadas = re.findall(r"^- \[(LM-\d+)\] .*conf=2026-11-14", pb, re.M)
        self.assertEqual(sorted(datadas), ["LM-027", "LM-028"])


if __name__ == "__main__":
    unittest.main()
