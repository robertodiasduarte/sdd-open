"""Contrato do sdd/bin/skill-lint.py (spec Agent Skills): name = pasta, description ≤ 1024.

Exit 0 = todos válidos · 1 = algum inválido · 64 = uso.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/skill-lint.py"


def skill(name: str, description: str) -> str:
    return "---\nname: " + name + "\ndescription: " + description + "\nlicense: MIT\n---\n\n# Corpo\n"


class SkillLint(Sandbox):
    def lint(self, pasta: str, texto: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "skills/" + pasta + "/SKILL.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def test_as_13_skills_reais_passam(self):
        skills = sorted((RAIZ / ".agents/skills").glob("sdd-*/SKILL.md"))
        self.assertEqual(len(skills), 13, [s.parent.name for s in skills])
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, *skills], RAIZ)
        self.assertEqual(rc, 0, out + err)

    def test_skill_minima_valida(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "Faz uma coisa util."))
        self.assertEqual(rc, 0, out)

    def test_description_com_1024_caracteres_passa(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "a" * 1024))
        self.assertEqual(rc, 0, out)

    def test_description_com_1025_caracteres_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "a" * 1025))
        self.assertEqual(rc, 1, out)
        self.assertIn("RESULTADO: VERMELHO", out)

    def test_name_diferente_da_pasta_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-outro-nome", "Faz uma coisa util."))
        self.assertEqual(rc, 1, out)

    def test_sem_frontmatter_reprova(self):
        rc, out = self.lint("sdd-exemplo", "# Só corpo, sem frontmatter\n")
        self.assertEqual(rc, 1, out)

    def test_description_vazia_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", '""'))
        self.assertEqual(rc, 1, out)

    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.tmp)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
