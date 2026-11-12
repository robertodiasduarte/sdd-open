"""F17, passo 0: as sobras da F16 e da F18 + F20 e os achados do repositório privado de 2026-11-12."""
from __future__ import annotations

import json
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Incidente(unittest.TestCase):
    """0a: o cenário incidente-chave reprovou 1 de 3 com "anote a data e a hora" como passo 1, antes de fechar."""

    def setUp(self):
        self.inc = ler(".agents/skills/sdd-seguranca/references/INCIDENTE.md")
        self.secao1 = self.inc[self.inc.index("## 1. Fechar a porta"):self.inc.index("## 2. Preservar a evidência")]

    def test_nada_se_pede_antes_de_fechar(self):
        self.assertIn("não peça nada antes de fechar", self.secao1)
        self.assertIn("nem anotar horário", self.secao1)
        self.assertIn("O 1º passo numerado da resposta é o do fechar", self.secao1)

    def test_a_hora_do_fechar_vem_depois(self):
        self.assertNotIn("inclusive do passo 1", self.inc)
        self.assertIn("A do fechar se anota logo **depois** de fechar, nunca antes.", self.inc)

    def test_manifest_registra_o_cenario_executado(self):
        m = json.loads(ler(".agents/skills/sdd-seguranca/manifest.json"))
        self.assertTrue(any(e.startswith("incidente-chave:") for e in m["executados"]))
        self.assertNotIn("Executar o cenário incidente-chave em contexto novo", m["pending"])


if __name__ == "__main__":
    unittest.main()
