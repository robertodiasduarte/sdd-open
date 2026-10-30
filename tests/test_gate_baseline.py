"""sdd/bin/gate-baseline.sh (F7): o gate do build contra o código anterior. 0 só quando a base reprova
AVALIANDO (🔴 do runner ou marcador de asserção); 2 quando a base passa; 3 em crash ou quando não
avaliou; 64 em uso errado.
"""
from __future__ import annotations

import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/gate-baseline.sh"
CHECA = 'grep -q novo app.txt && echo ok || { echo "RESULTADO: VERMELHO"; exit 2; }\n'


def define(cmd: str) -> str:
    return ('# DEFINE\n\n## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n  cmd: "' + cmd
            + '"\n  pass_when: "exit 0"\n```\n')


class GateBaseline(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.git(self.r, "checkout", "-q", "-b", "main")
        self.copia("sdd/bin", self.r)
        self.escreve(self.r, "app.txt", "velho\n")
        self.commit(self.r, "base")
        self.git(self.r, "checkout", "-q", "-b", "feat")
        self.escreve(self.r, "app.txt", "novo\n")
        self.escreve(self.r, "checa.sh", CHECA)

    def roda_gate(self, cmd: str, *args: str, env: dict | None = None) -> tuple[int, str]:
        self.escreve(self.r, "sdd/features/DEFINE_X.md", define(cmd))
        self.commit(self.r, "build")
        rc, out, err = self.roda([BASH, SCRIPT, "sdd/features/DEFINE_X.md", "--base", "main", *args], self.r, env)
        return rc, out + err

    def test_base_reprova_avaliando_sai_0_e_grava_evidencia(self):
        rc, out = self.roda_gate("bash checa.sh", "--sobrepor", "checa.sh")
        self.assertEqual(rc, 0, out)
        self.assertResultado(out)
        log = (self.r / "sdd/reports/evidence/X/BASELINE-gate.log").read_text(encoding="utf-8")
        self.assertTrue(log.startswith("$ bash sdd/bin/gate-baseline.sh"), log)
        self.assertIn("--sobrepor checa.sh", log.splitlines()[0])

    def test_build_continua_verde(self):
        self.escreve(self.r, "sdd/features/DEFINE_X.md", define("bash checa.sh"))
        rc, out, err = self.roda([BASH, "sdd/bin/verify-gate.sh", "sdd/features/DEFINE_X.md"], self.r)
        self.assertEqual(rc, 0, out + err)

    def test_base_passa_sai_2(self):
        rc, out = self.roda_gate("true")
        self.assertEqual(rc, 2, out)
        self.assertIn("ancore a asserção", out)

    def test_sem_sobrepor_o_gate_novo_nao_existe_na_base(self):
        rc, out = self.roda_gate("bash checa.sh")
        self.assertEqual(rc, 3, out)

    def test_crash_com_rc_2_nao_prova_dentes(self):
        for cmd in ("grep -q ok nao_existe.txt", "if then fi", "echo 'FAILED (errors=1)'; exit 2"):
            with self.subTest(cmd=cmd):
                rc, out = self.roda_gate(cmd)
                self.assertEqual(rc, 3, out)
                self.assertIn("INCONCLUSIVO", out)

    def test_marcadores_de_asssercao_provam_dentes(self):
        for cmd in ("echo 'FAILED (failures=1)'; exit 1", "echo '==== 1 failed, 2 passed in 0.1s ===='; exit 1",
                    "echo '--- FAIL: TestX'; exit 1", "echo 'Tests: 1 failed, 2 total'; exit 1"):
            with self.subTest(cmd=cmd):
                rc, out = self.roda_gate(cmd)
                self.assertEqual(rc, 0, out)
                self.assertNotIn("syntax error", out)

    def test_hooks_e_assinatura_globais_nao_quebram_a_copia(self):
        hooks = self.escreve(self.tmp, "hooks/pre-commit", "#!/bin/sh\nexit 1\n")
        hooks.chmod(0o755)
        glob = self.escreve(self.tmp, "gitconfig-hostil",
                            "[commit]\n  gpgsign = true\n[core]\n  hooksPath = " + str(hooks.parent) + "\n")
        rc, out = self.roda_gate("bash checa.sh", "--sobrepor", "checa.sh",
                                 env=dict(self.env, GIT_CONFIG_GLOBAL=str(glob)))
        self.assertEqual(rc, 0, out)

    def test_base_default_vem_do_config(self):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  default_branch: main\n")
        self.escreve(self.r, "sdd/features/DEFINE_X.md", define("bash checa.sh"))
        self.commit(self.r, "build")
        rc, out, err = self.roda([BASH, SCRIPT, "sdd/features/DEFINE_X.md", "--sobrepor", "checa.sh"], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("base: main", out)

    def test_base_invalida_sai_3(self):
        rc, out = self.roda_gate("bash checa.sh", "--base", "nao-existe")
        self.assertEqual(rc, 3, out)

    def test_uso(self):
        self.escreve(self.r, "sdd/features/DEFINE_X.md", define("true"))
        for args in ([], ["sdd/features/NAO.md"], ["sdd/features/DEFINE_X.md", "--sobrepor", "nao_existe.sh"],
                     ["sdd/features/DEFINE_X.md", "--opcao"]):
            with self.subTest(args=args):
                rc, out, err = self.roda([BASH, SCRIPT, *args], self.r)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("ERRO DE USO", err)


if __name__ == "__main__":
    unittest.main()
