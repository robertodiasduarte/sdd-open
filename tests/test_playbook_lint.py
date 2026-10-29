"""Contrato do sdd/bin/playbook-lint.sh sobre as fixtures de sdd/fixtures/playbook/.

Exit: 0 ok · 1 = 0 hits / colapso · 2 = formato inválido / self-test falhou · 64 = uso ou fora de git.
"""
from __future__ import annotations

import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/playbook-lint.sh"
FX = "sdd/fixtures/playbook/"


class PlaybookLint(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.copia("sdd/fixtures/playbook", self.r)

    def lint(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, *args], self.r)
        return rc, out + err

    def test_fixture_valida_passa(self):
        rc, out = self.lint(FX + "playbook-valido.md")
        self.assertEqual(rc, 0, out)

    def test_fixture_delta_ok_passa(self):
        rc, out = self.lint(FX + "playbook-delta-ok.md")
        self.assertEqual(rc, 0, out)

    def test_fixture_invalida_reprova_com_2(self):
        rc, out = self.lint(FX + "playbook-invalido.md")
        self.assertEqual(rc, 2, out)

    def test_anti_collapse_bloqueia_colapso(self):
        rc, out = self.lint("--anti-collapse", FX + "playbook-valido.md", FX + "playbook-colapso.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("LM-002", out)

    def test_anti_collapse_aceita_delta(self):
        rc, out = self.lint("--anti-collapse", FX + "playbook-valido.md", FX + "playbook-delta-ok.md")
        self.assertEqual(rc, 0, out)

    def test_grep_sem_hit_e_1(self):
        rc, out = self.lint("--grep", "superficie_que_nao_existe_xyz", FX + "playbook-valido.md")
        self.assertEqual(rc, 1, out)

    def test_self_test_passa(self):
        rc, out = self.lint("--self-test")
        self.assertEqual(rc, 0, out)

    def test_fora_de_git_e_64(self):
        solta = self.tmp / "sem-git"
        solta.mkdir()
        rc, out, err = self.roda([BASH, self.r / SCRIPT, "--stats", "x.md"], solta)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
