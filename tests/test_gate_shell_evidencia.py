"""sdd/bin/gate-shell-evidencia.sh (F7): `[exit=N]` que é exit do formatador, `[exit=]` vazio e
`[exit=$?]` literal saem 2 com `arquivo:linha`; logs honestos e pipe assertivo saem 0.
"""
from __future__ import annotations

import re
import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/gate-shell-evidencia.sh"
FX = "sdd/fixtures/evidencia/"


class GateShellEvidencia(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin", self.r)
        self.copia("sdd/fixtures/evidencia", self.r)

    def gate(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, *args], self.r)
        return rc, out + err

    @staticmethod
    def acusados(out: str) -> list:
        return re.findall(r"^🛑 (\S+\.log:\d+)", out, re.M)

    def test_falso_verde_acusa_exatamente_as_linhas_esperadas(self):
        rc, out = self.gate(FX + "shell-falso-verde.log")
        self.assertEqual(rc, 2, out)
        esperadas = [FX + "shell-falso-verde.log:%d" % n for n in (3, 6, 9, 12, 15, 17)]
        self.assertEqual(self.acusados(out), esperadas)
        self.assertIn("é o exit de `tail`", out)
        self.assertIn("é o exit de `cut`", out)
        self.assertIn("rc=$?", out.splitlines()[-1])
        self.assertResultado(out)

    def test_honesto_e_pipe_assertivo_saem_0(self):
        for f in ("shell-honesto.log", "shell-pipe-assertivo.log"):
            with self.subTest(f=f):
                rc, out = self.gate(FX + f)
                self.assertEqual(rc, 0, out)

    def test_cada_formatador_e_acusado(self):
        for fmt in ("tail", "head", "cat", "tee", "wc", "sed", "cut", "sort", "uniq", "column", "tr", "fold", "nl"):
            with self.subTest(fmt=fmt):
                self.escreve(self.r, "l.log", "$ grep -rn X src/ | %s -n 2\nlinha\n[exit=0]\n" % fmt)
                rc, out = self.gate("l.log")
                self.assertEqual(rc, 2, out)

    def test_bordas_do_pipe(self):
        casos = {
            "$ cmd | LC_ALL=C sort\n[exit=0]\n": 2,
            "$ cmd |& tail -1\n[exit=0]\n": 2,
            "$ cmd\n[exit= ]\n": 2,
            "$ cmd | tail -3; echo \"[exit=${PIPESTATUS[0]}]\"\n[exit=1]\n": 0,
            "$ set -o pipefail; cmd | tail -3\n[exit=1]\n": 0,
            "$\ncmd | tail -1\n[exit=0]\n": 2,
            "$ cmd | tail -1 # PIPESTATUS\n[exit=0]\n": 2,
            "$ cmd | (tail -1)\n[exit=0]\n": 2,
            "$ cmd | command tail -1\n[exit=0]\n": 2,
            "$ cmd | env LC_ALL=C sort -u\n[exit=0]\n": 2,
            "$ out=$(cmd); r=$?; printf x | tail -1\n[exit=1]\n": 0,
        }
        for log, esperado in casos.items():
            with self.subTest(log=log):
                self.escreve(self.r, "l.log", log)
                rc, out = self.gate("l.log")
                self.assertEqual(rc, esperado, out)

    def test_rc_capturado_depois_do_pipe_nao_salva(self):
        self.escreve(self.r, "l.log", "$ npm test | tail -5; rc=$?\nerro\n[exit=0]\n")
        rc, out = self.gate("l.log")
        self.assertEqual(rc, 2, out)

    def test_pasta_e_utf8(self):
        self.escreve(self.r, "ev/ação.log", "$ echo 'ação — çã' | tail -1\nação — çã\nexit=0\n")
        self.escreve(self.r, "ev/ok.log", "$ true\n[exit=0]\n")
        rc, out = self.gate("ev")
        self.assertEqual(rc, 2, out)
        self.assertEqual(self.acusados(out), ["ev/ação.log:3"])

    def test_caminho_inexistente_e_64(self):
        rc, out = self.gate("nao/existe")
        self.assertEqual(rc, 64, out)

    def test_sem_log_sai_0(self):
        self.escreve(self.r, "vazio/leia.txt", "$ x | tail\n[exit=0]\n")
        rc, out = self.gate("vazio")
        self.assertEqual(rc, 0, out)
        self.assertIn("nada a conferir", out)


class ModoDiff(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.git(self.r, "checkout", "-q", "-b", "main")
        self.copia("sdd/bin", self.r)
        self.escreve(self.r, "sdd/reports/evidence/VELHA/a.log", "$ npm test | tail\n[exit=0]\n")
        self.commit(self.r, "base")
        self.git(self.r, "checkout", "-q", "-b", "feat")

    def gate(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, "--base", "main", *args], self.r)
        return rc, out + err

    def test_so_os_logs_do_diff_e_os_nao_rastreados(self):
        rc, out = self.gate()
        self.assertEqual(rc, 0, out)  # o log velho, fora do diff, não conta
        self.escreve(self.r, "sdd/reports/evidence/NOVA/b.log", "$ npm test | head -3\n[exit=0]\n")
        rc, out = self.gate()
        self.assertEqual(rc, 2, out)  # não rastreado
        self.commit(self.r, "build")
        self.escreve(self.r, "sdd/reports/evidence/NOVA/ação.log", "$ true\n[exit=]\n")
        self.commit(self.r, "build 2")
        rc, out = self.gate()
        self.assertEqual(rc, 2, out)
        self.assertEqual(sorted(re.findall(r"^🛑 (\S+\.log:\d+)", out, re.M)),
                         ["sdd/reports/evidence/NOVA/ação.log:2", "sdd/reports/evidence/NOVA/b.log:2"])

    def test_staged_e_rastreado_modificado_tambem_entram(self):
        self.escreve(self.r, "sdd/reports/evidence/NOVA/s.log", "$ y | head -1\ny\n[exit=0]\n")
        self.git(self.r, "add", "sdd/reports/evidence/NOVA/s.log")
        rc, out = self.gate()
        self.assertEqual(rc, 2, out)  # só staged
        self.git(self.r, "checkout", "-q", "main")
        self.git(self.r, "checkout", "-q", "-b", "feat2")
        self.escreve(self.r, "sdd/reports/evidence/VELHA/a.log", "$ npm test | cut -c1-9\n[exit=0]\n")
        rc, out = self.gate()
        self.assertEqual(rc, 2, out)  # rastreado, modificado e não commitado
        self.assertIn("sdd/reports/evidence/VELHA/a.log:2", out)

    def test_de_subpasta(self):
        self.escreve(self.r, "sdd/reports/evidence/NOVA/b.log", "$ npm test | head -3\n[exit=0]\n")
        rc, out, err = self.roda([BASH, "../bin/gate-shell-evidencia.sh", "--base", "main"], self.r / "sdd/reports")
        self.assertEqual(rc, 2, out + err)

    def test_base_invalida_e_64(self):
        rc, out = self.gate("--base", "nao-existe")
        self.assertEqual(rc, 64, out)


if __name__ == "__main__":
    unittest.main()
