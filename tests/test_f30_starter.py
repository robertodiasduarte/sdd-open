"""F30 S1 — as regras de qualidade chegam ao starter (DEFINE_F30_QUALIDADE_CODIGO, AT-008).

O starter não tem AGENTS.md: a sdd-build dele sai do `web/MODO_WEB.md`, e o catálogo de qualidade vai junto porque o
modo o cita. O gerador roda numa pasta temporária (a base do test_gerar_starter); o starter gerado não cita
`sdd/bin/` (LM-035) e passa nos grep da F29.
"""
from __future__ import annotations

import re
import unittest

from test_gerar_starter import Base

F29 = ("Não cite nem resuma", "comece com esta linha", "versão atual: http")


class AT008Starter(Base):
    def test_build_do_starter_traz_as_regras_e_o_catalogo(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        build = self.starter / "skills" / "sdd-build"
        skill = re.sub(r"\s+", " ", (build / "SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("references/CATALOGO_QUALIDADE.md", skill)
        self.assertIn("reusar a função que já existe antes de criar outra", skill)
        self.assertIn("`project.lint_cmd` e", skill)
        self.assertIn("`lint: slot vazio`", skill)
        catalogo = build / "references" / "CATALOGO_QUALIDADE.md"
        self.assertTrue(catalogo.is_file())
        self.assertIn("## Ferramentas por stack", catalogo.read_text(encoding="utf-8"))
        for p in (build / "SKILL.md", catalogo):
            with self.subTest(arquivo=p.name):
                self.assertNotIn("sdd/bin/", p.read_text(encoding="utf-8"))

    def test_starter_gerado_passa_nos_grep_da_f29(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        achados = [(p.relative_to(self.starter).as_posix(), padrao)
                   for p in (self.starter / "skills").rglob("*.md")
                   for padrao in F29 if padrao in p.read_text(encoding="utf-8")]
        self.assertEqual(achados, [])

    def test_checar_do_starter_tem_o_modo_linter(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        checar = (self.starter / "skills/sdd-checar-ambiente/scripts/checar.sh").read_text(encoding="utf-8")
        self.assertIn("--linter) MODO=linter", checar)


if __name__ == "__main__":
    unittest.main()
