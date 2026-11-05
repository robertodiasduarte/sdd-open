"""AT-030: a sandbox da suíte não herda SDD_TRACE nem SDD_TRACE_DIR de quem a chama."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox


class Ambiente(unittest.TestCase):
    def test_a_suite_de_trace_passa_com_as_2_variaveis_no_ambiente(self):
        with tempfile.TemporaryDirectory(prefix="sdd-trace-") as d:
            destino = Path(d) / "herdada"
            env = dict(os.environ, SDD_TRACE="off", SDD_TRACE_DIR=str(destino), SDD_TEST_BASH=BASH)
            for padrao in ("test_verify_gate_trace.py", "test_governanca_gate.py"):
                with self.subTest(padrao=padrao):
                    r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", padrao],
                                       cwd=str(RAIZ), env=env, capture_output=True, encoding="utf-8", errors="replace")
                    self.assertEqual(r.returncode, 0, r.stderr[-1500:])
            self.assertFalse(destino.exists(), "nada pode vazar para a pasta herdada")


class SandboxLimpa(Sandbox):
    def test_o_ambiente_base_nao_traz_as_2_variaveis(self):
        antes = {k: os.environ.get(k) for k in ("SDD_TRACE", "SDD_TRACE_DIR")}
        os.environ["SDD_TRACE"], os.environ["SDD_TRACE_DIR"] = "off", "/nao"
        try:
            outro = Sandbox("setUp")
            outro.setUp()
            self.addCleanup(outro.tearDown)
            self.assertNotIn("SDD_TRACE", outro.env)
            self.assertNotIn("SDD_TRACE_DIR", outro.env)
        finally:
            for k, v in antes.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
