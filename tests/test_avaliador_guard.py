"""sdd/bin/avaliador-guard.sh (F7): o avaliador só é despachado com a árvore commitada. Permitidos:
sdd/reports/evidence/, sdd/traces/ e os prefixos de --permitir. 0 limpo · 1 sujo · 2 não conferido.
"""
from __future__ import annotations

import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/avaliador-guard.sh"
QUATRO = ["--permitir", "sdd/features/", "--permitir", "sdd/handoffs/", "--permitir", "sdd/reports/",
          "--permitir", "sdd/reviews/"]


class AvaliadorGuard(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin", self.r)
        self.copia("sdd/fixtures", self.r)
        self.escreve(self.r, "src/app.py", "x = 1\n")
        self.commit(self.r, "base")

    def guard(self, *args: str, env: dict | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, *args], self.r, env)
        return rc, out + err

    def test_limpo_sai_0(self):
        rc, out = self.guard()
        self.assertEqual(rc, 0, out)
        self.assertResultado(out)

    def test_so_evidencia_sai_0(self):
        self.escreve(self.r, "sdd/reports/evidence/X/AVAL-1.log", "$ true\n")
        rc, out = self.guard()
        self.assertEqual(rc, 0, out)

    def test_trace_do_gate_nao_suja(self):
        rc, _, _ = self.roda([BASH, "sdd/bin/verify-gate.sh", "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md"], self.r)
        self.assertEqual(rc, 0)
        self.assertTrue((self.r / "sdd/traces/FIXTURE_CONTROLE.jsonl").is_file())
        rc, out = self.guard()
        self.assertEqual(rc, 0, out)

    def test_modificado_e_nao_rastreado_saem_1_com_o_commit(self):
        self.escreve(self.r, "src/app.py", "x = 2\n")
        self.escreve(self.r, "src/novo dir/ação.py", "y = 1\n")
        rc, out = self.guard()
        self.assertEqual(rc, 1, out)
        self.assertIn("   - src/app.py", out)
        self.assertIn("   - src/novo dir/ação.py", out)
        self.assertIn("commit -m", out)
        self.assertIn("'src/novo dir/ação.py'", out)
        self.assertIn("add -A -- ", out)  # só os caminhos listados, nunca a árvore inteira

    def test_renomear_para_dentro_de_evidence_conta_a_origem(self):
        (self.r / "sdd/reports/evidence/X").mkdir(parents=True)
        self.git(self.r, "mv", "src/app.py", "sdd/reports/evidence/X/app.py")
        rc, out = self.guard()
        self.assertEqual(rc, 1, out)
        self.assertIn("   - src/app.py", out)
        self.assertNotIn("   - sdd/reports/evidence/X/app.py", out)

    def test_o_commit_sugerido_funciona_com_renomeacao(self):
        self.git(self.r, "mv", "src/app.py", "src/app2.py")
        rc, out = self.guard()
        self.assertEqual(rc, 1, out)
        comando = out.splitlines()[-1][len("→ "):]
        rc2, o2, e2 = self.roda(["bash", "-c", comando], self.r)
        self.assertEqual(rc2, 0, o2 + e2)
        rc, out = self.guard()
        self.assertEqual(rc, 0, out)

    def test_quatro_prefixos_nao_liberam_sdd_bin(self):
        self.escreve(self.r, "sdd/features/DEFINE_X.md", "# x\n")
        self.escreve(self.r, "sdd/bin/x.sh", "echo x\n")
        rc, out = self.guard(*QUATRO)
        self.assertEqual(rc, 1, out)
        self.assertIn("   - sdd/bin/x.sh", out)
        self.assertNotIn("DEFINE_X.md", out)

    def test_fora_de_git_sai_2(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, out = self.guard("--root", str(fora))
        self.assertEqual(rc, 2, out)
        self.assertIn("INCONCLUSIVO", out)

    def test_desligado_sai_0_com_aviso(self):
        self.escreve(self.r, "src/app.py", "x = 3\n")
        rc, out = self.guard(env=dict(self.env, SDD_AVALIADOR_GUARD="off"))
        self.assertEqual(rc, 0, out)
        self.assertIn("declare no BUILD_REPORT", out)

    def test_uso(self):
        for args in (["--root"], ["--permitir"], ["--xyz"], ["--root", "nao/existe"]):
            with self.subTest(args=args):
                rc, out = self.guard(*args)
                self.assertEqual(rc, 64, out)


if __name__ == "__main__":
    unittest.main()
