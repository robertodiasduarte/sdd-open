"""F16W (AT-001, AT-002): scripts/testes-por-modulo.py, o executor da suíte módulo a módulo (unidade = classe).

Roda sobre uma pasta de testes falsa: um módulo verde, um que falha, um com pulo, um que pendura com um neto
vivo segurando a saída. O executor não usa git (o Verify Gate roda numa cópia sem .git, LM-006).
"""
from __future__ import annotations

import subprocess
import sys
import time
import unittest
from pathlib import Path

from apoio import RAIZ, Sandbox

EXECUTOR = RAIZ / "scripts" / "testes-por-modulo.py"

VERDE = """import unittest
class T(unittest.TestCase):
    def test_a(self): pass
    def test_b(self): pass
"""
FALHA = """import unittest
class T(unittest.TestCase):
    def test_ok(self): pass
    def test_cai(self): self.assertEqual(1, 2)
    def test_quebra(self): raise RuntimeError("x")
"""
PULO = """import unittest
class T(unittest.TestCase):
    @unittest.skip("sem o recurso")
    def test_pulado(self): pass
    def test_ok(self): pass
"""
# O neto herda a saída e dorme mais que o teto: sem matar a árvore, quem lê a saída esperaria por ele.
PENDURA = """import subprocess, sys, time, unittest
class T(unittest.TestCase):
    def test_pendura(self):
        subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
        time.sleep(120)
"""
QUEBRADO = "import modulo_que_nao_existe\n"


class Executor(Sandbox):
    def setUp(self):
        super().setUp()
        self.pasta = self.tmp / "tests"
        self.pasta.mkdir()

    def modulo(self, nome: str, texto: str) -> None:
        (self.pasta / (nome + ".py")).write_text(texto, encoding="utf-8")

    def executa(self, *args, timeout=120):
        r = subprocess.run([sys.executable, "-B", str(EXECUTOR), "--pasta", str(self.pasta), *map(str, args)],
                           cwd=str(self.tmp), env=self.env, capture_output=True, encoding="utf-8",
                           errors="replace", stdin=subprocess.DEVNULL, timeout=timeout)
        return r.returncode, r.stdout, r.stderr

    def test_verde_sai_0_com_a_linha_de_cada_modulo(self):
        self.modulo("test_um", VERDE)
        self.modulo("test_dois", PULO)
        saida = self.tmp / "saida"
        rc, out, err = self.executa("--saida", saida)
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(out, r"test_um\.T\s+OK\s+testes=2\s+falhas=0\s+erros=0\s+pulados=0")
        self.assertRegex(out, r"test_dois\.T\s+OK\s+testes=2\s+falhas=0\s+erros=0\s+pulados=1")
        self.assertIn("total: 2 unidade(s), 4 teste(s): 0 falha(s), 0 erro(s), 1 pulado(s)", out)
        self.assertTrue(out.rstrip().endswith("RESULTADO: VERDE"), out)
        self.assertTrue((saida / "test_um.T.log").is_file())
        resumo = (saida / "resumo.tsv").read_text(encoding="utf-8").splitlines()
        self.assertEqual(resumo[0].split("\t"), ["unidade", "estado", "testes", "falhas", "erros", "pulados", "segundos"])
        self.assertEqual([l.split("\t")[:2] for l in resumo[1:]], [["test_dois.T", "OK"], ["test_um.T", "OK"]])

    def test_falha_e_erro_saem_1_com_os_nomes(self):
        self.modulo("test_um", VERDE)
        self.modulo("test_ruim", FALHA)
        self.modulo("test_quebrado", QUEBRADO)
        rc, out, err = self.executa()
        self.assertEqual(rc, 1, out + err)
        self.assertRegex(out, r"test_ruim\.T\s+FALHOU\s+testes=3\s+falhas=1\s+erros=1")
        self.assertIn("FAIL T.test_cai", out)
        self.assertIn("ERROR T.test_quebra", out)
        # import quebrado: a unidade é o módulo inteiro, e o unittest relata 1 erro de carga
        self.assertRegex(out, r"test_quebrado\s+FALHOU")
        self.assertIn("unidades com problema: test_quebrado (FALHOU), test_ruim.T (FALHOU)", out)
        self.assertTrue(out.rstrip().endswith("RESULTADO: VERMELHO"), out)

    def test_teto_mata_a_arvore_e_segue(self):
        self.modulo("test_a_pendura", PENDURA)
        self.modulo("test_b_verde", VERDE)
        inicio = time.monotonic()
        rc, out, err = self.executa("--teto-unidade", "3", timeout=100)
        gasto = time.monotonic() - inicio
        self.assertEqual(rc, 1, out + err)
        self.assertRegex(out, r"test_a_pendura\.T\s+TETO")
        self.assertRegex(out, r"test_b_verde\.T\s+OK")
        # o neto dorme 120 s: terminar bem antes disso prova que ninguém esperou por ele
        self.assertLess(gasto, 60, out)

    def test_fatias_disjuntas_completas_e_estaveis(self):
        pesos = {"test_a": 9, "test_b": 7, "test_c": 5, "test_d": 3, "test_e": 1, "test_f": 1, "test_g": 0}
        unidades = sorted(m + ".T" for m, k in pesos.items() if k)   # módulo sem teste não vira unidade
        for nome, n in pesos.items():
            self.modulo(nome, "import unittest\nclass T(unittest.TestCase):\n" +
                        "".join("    def test_%d(self): pass\n" % i for i in range(n)) + "    pass\n")
        for n in range(1, 9):
            with self.subTest(n=n):
                fatias = []
                for i in range(1, n + 1):
                    rc, out, err = self.executa("--lista", "--fatia", "%d/%d" % (i, n))
                    self.assertEqual(rc, 0, err)
                    fatias.append([l for l in out.splitlines() if l])
                juntas = [m for f in fatias for m in f]
                self.assertEqual(sorted(juntas), unidades)
                self.assertEqual(len(juntas), len(set(juntas)))
                de_novo = [self.executa("--lista", "--fatia", "%d/%d" % (i, n))[1].split() for i in range(1, n + 1)]
                self.assertEqual(fatias, de_novo)
        # 2 fatias: 9 na 1ª, 7 na 2ª, 5 na 2ª (7 < 9), 3 na 1ª, e no empate (12, 12) a 1ª ⇒ a, d, e | b, c, f
        self.assertEqual(self.executa("--lista", "--fatia", "1/2")[1].split(), ["test_a.T", "test_d.T", "test_e.T"])

    def test_classes_viram_unidades_e_a_herdada_conta_uma_vez(self):
        self.modulo("test_base", "import unittest\nclass Base(unittest.TestCase):\n    def test_x(self): pass\n")
        self.modulo("test_filho", "import unittest\nfrom test_base import Base\n"
                                  "class A(Base):\n    def test_y(self): pass\nclass B(unittest.TestCase):\n"
                                  "    def test_z(self): pass\n")
        rc, out, err = self.executa("--lista")
        self.assertEqual(rc, 0, err)
        # A herda test_x: a unidade A tem 2 testes; Base, importada em test_filho, fica só em test_base
        self.assertEqual(out.split(), ["test_base.Base", "test_filho.A", "test_filho.B"])
        rc, out, err = self.executa("--so", "test_filho")
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(out, r"test_filho\.A\s+OK\s+testes=2")
        self.assertNotIn("test_base", out)

    def test_so_roda_os_escolhidos(self):
        self.modulo("test_um", VERDE)
        self.modulo("test_ruim", FALHA)
        rc, out, err = self.executa("--so", "test_um")
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("test_ruim", out)

    def test_uso_errado_sai_64_sem_rodar(self):
        self.modulo("test_ruim", FALHA)
        for args in (["--fatia", "0/3"], ["--fatia", "4/3"], ["--fatia", "x"], ["--teto-unidade", "abc"],
                     ["--teto-unidade", "0"], ["--paralelo", "0"], ["--so", "test_nao_existe"], ["--nada"],
                     ["--fatia"]):
            with self.subTest(args=args):
                rc, out, err = self.executa(*args)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)
                self.assertNotIn("test_ruim", out)
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        r = subprocess.run([sys.executable, "-B", str(EXECUTOR), "--pasta", str(vazia)], capture_output=True,
                           encoding="utf-8", errors="replace", env=self.env, stdin=subprocess.DEVNULL, timeout=60)
        self.assertEqual(r.returncode, 64, r.stdout + r.stderr)


class SuiteReal(unittest.TestCase):
    def test_as_12_fatias_cobrem_a_suite(self):
        r = subprocess.run([sys.executable, "-B", str(EXECUTOR), "--lista", "--fatia", "1/1"], capture_output=True,
                           encoding="utf-8", stdin=subprocess.DEVNULL, timeout=120)
        todos = r.stdout.split()
        # todo módulo de teste aparece em pelo menos uma unidade
        modulos = {u.split(".", 1)[0] for u in todos}
        self.assertEqual(modulos, {p.stem for p in (RAIZ / "tests").glob("test_*.py")})
        doze = []
        for i in range(1, 13):
            doze += subprocess.run([sys.executable, "-B", str(EXECUTOR), "--lista", "--fatia", "%d/12" % i],
                                   capture_output=True, encoding="utf-8", stdin=subprocess.DEVNULL, timeout=120).stdout.split()
        self.assertEqual(sorted(doze), sorted(todos))
        self.assertEqual(len(doze), len(set(doze)))


if __name__ == "__main__":
    unittest.main()
