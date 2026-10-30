"""sdd/bin/test-baseline.sh (F7): só falha de teste nova aborta. 5 formatos (unittest, pytest, jest,
vitest, go, deno), poda só na execução completa, --touched, --aceitar, INCONCLUSIVO e PULADO.
"""
from __future__ import annotations

import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/test-baseline.sh"
FX = "sdd/fixtures/evidencia/"
BASELINE = "sdd/baselines/tests.txt"
# formato → (fixture, id conhecido, id novo)
FORMATOS = {
    "unittest": ("testes-unittest.txt", "test_conta.Caso.test_conhecido", "test_conta.Caso.test_novo"),
    "pytest": ("testes-pytest.txt", "tests/test_conta.py::test_conhecido", "tests/test_conta.py::test_novo"),
    "jest": ("testes-jest.txt", "Conta › conhecido", "Conta › novo"),
    "vitest": ("testes-vitest.txt", "src/conta.test.ts > Conta > conhecido", "src/conta.test.ts > Conta > novo"),
    "go": ("testes-go.txt", "TestConhecido", "TestNovo"),
    "deno": ("testes-deno.txt", "conta_test.ts::conhecido", "conta_test.ts::novo"),
}


class TestBaseline(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin", self.r)
        self.copia("sdd/fixtures/evidencia", self.r)

    def tb(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, *args], self.r)
        return rc, out + err

    def baseline(self, *ids: str) -> None:
        self.escreve(self.r, BASELINE, "# falhas conhecidas\n" + "".join(i + "\n" for i in ids))

    def config(self, cmd: str) -> None:
        self.escreve(self.r, "sdd/config.yaml", "project:\n  name: x\n  test_cmd: \"" + cmd + "\"\n")

    def test_cada_formato_so_aborta_pela_falha_nova(self):
        for nome, (fx, velho, novo) in FORMATOS.items():
            with self.subTest(formato=nome):
                self.baseline(velho)
                rc, out = self.tb("--cmd", "cat " + FX + fx + "; exit 1")
                self.assertEqual(rc, 2, out)
                self.assertIn("🛑 nova: " + novo, out)
                self.assertIn("ℹ️  conhecida: " + velho, out)
                self.assertNotIn("🛑 nova: " + velho, out)
                self.baseline(velho, novo)
                rc, out = self.tb("--cmd", "cat " + FX + fx + "; exit 1")
                self.assertEqual(rc, 0, out)
                self.assertResultado(out)

    def test_execucao_parcial_nao_poda(self):
        self.baseline("test_conta.Caso.test_conhecido", "test_conta.Caso.test_novo", "mod.C.test_b")
        antes = (self.r / BASELINE).read_bytes()
        rc, out = self.tb("--cmd", "cat " + FX + "testes-unittest.txt; exit 1")
        self.assertEqual(rc, 0, out)
        self.assertIn("baseline não podado (execução parcial)", out)
        self.assertEqual((self.r / BASELINE).read_bytes(), antes)

    def test_execucao_completa_poda_o_que_sarou(self):
        self.baseline("test_conta.Caso.test_conhecido", "test_conta.Caso.test_novo", "mod.C.test_b")
        self.config("cat " + FX + "testes-unittest.txt; exit 1")
        rc, out = self.tb()
        self.assertEqual(rc, 0, out)
        self.assertIn("sarou — removido do baseline", out)
        self.assertIn("mod.C.test_b", out)
        texto = (self.r / BASELINE).read_text(encoding="utf-8")
        self.assertNotIn("mod.C.test_b", texto)
        self.assertIn("# falhas conhecidas", texto)
        self.assertIn("test_conta.Caso.test_novo", texto)

    def test_falha_nova_nao_poda_nem_na_execucao_completa(self):
        self.baseline("test_conta.Caso.test_conhecido", "mod.C.test_b")
        antes = (self.r / BASELINE).read_bytes()
        self.config("cat " + FX + "testes-unittest.txt; exit 1")
        rc, out = self.tb()
        self.assertEqual(rc, 2, out)
        self.assertEqual((self.r / BASELINE).read_bytes(), antes)

    def test_touched_so_aborta_por_arquivo_tocado(self):
        self.git(self.r, "checkout", "-q", "-b", "main")
        self.escreve(self.r, "tests/test_conta.py", "# v1\n")
        self.escreve(self.r, "src/outro.py", "# v1\n")
        self.commit(self.r, "base")
        self.git(self.r, "checkout", "-q", "-b", "feat")
        self.baseline("tests/test_conta.py::test_conhecido")
        self.escreve(self.r, "src/outro.py", "# v2\n")
        self.commit(self.r, "build")
        rc, out = self.tb("--touched", "--base", "main", "--cmd", "cat " + FX + "testes-pytest.txt; exit 1")
        self.assertEqual(rc, 0, out)
        self.assertIn("fora do diff", out)
        self.escreve(self.r, "tests/test_conta.py", "# v2\n")
        rc, out = self.tb("--touched", "--base", "main", "--cmd", "cat " + FX + "testes-pytest.txt; exit 1")
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 nova: tests/test_conta.py::test_novo", out)

    def test_touched_com_base_invalida_e_64(self):
        rc, out = self.tb("--touched", "--base", "nao-existe", "--cmd", "true")
        self.assertEqual(rc, 64, out)

    def test_saida_nao_reconhecida_e_inconclusivo(self):
        rc, out = self.tb("--cmd", "echo 'algo deu errado'; exit 1")
        self.assertEqual(rc, 3, out)
        self.assertIn("RESULTADO: INCONCLUSIVO", out)

    def test_comando_ausente_e_inconclusivo(self):
        rc, out = self.tb("--cmd", "ferramenta_que_nao_existe_xyz")
        self.assertEqual(rc, 3, out)

    def test_test_cmd_vazio_e_pulado(self):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  test_cmd: \"\"\n")
        rc, out = self.tb()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: PULADO", out)

    def test_aceitar_nao_roda_e_e_idempotente(self):
        self.config("exit 1")
        rc, out = self.tb("--aceitar", "mod.C.test_x")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("▶ testes", out)
        self.tb("--aceitar", "mod.C.test_x")
        self.assertEqual((self.r / BASELINE).read_text(encoding="utf-8"), "mod.C.test_x\n")

    def test_uso(self):
        for args in (["--cmd"], ["--aceitar"], ["--xyz"]):
            with self.subTest(args=args):
                rc, out = self.tb(*args)
                self.assertEqual(rc, 64, out)


if __name__ == "__main__":
    unittest.main()
