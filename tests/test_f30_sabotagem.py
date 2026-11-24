"""F30 S2 — sabotagem do gate numa cópia descartável (DEFINE_F30_QUALIDADE_CODIGO, AT-013 e AT-014).

AT-013: o `sdd/bin/sabotagem.sh` extrai `git archive HEAD` numa pasta temporária, confere que o comando passa na cópia
limpa, troca o trecho declarado só na cópia e roda de novo: vermelho ⇒ exit 0 e `AT-nnn.sabotagem.log`; verde ⇒ exit 2
("o teste não pega o defeito"). A cópia é apagada e, fora o log, a árvore de trabalho fica idêntica (hash antes = depois).
AT-014: trecho que não casa exatamente 1 vez, comando que já falha ou não roda (126/127) ⇒ 3; caminho absoluto, com `..`,
link simbólico para fora, arquivo fora do HEAD, fora de git ou argumento faltando ⇒ 64. Sem log, árvore idêntica.
"""
from __future__ import annotations

import hashlib
import os
import unittest
from pathlib import Path

from apoio import BASH, PYTHON, RAIZ, SEM_SYMLINK, Sandbox, caminho_bash

SCRIPT = RAIZ / "sdd" / "bin" / "sabotagem.sh"
F = "FX"
LOG = "sdd/reports/evidence/%s/AT-001.sabotagem.log" % F
CONTA = (
    "def saca(saldo, valor):\n"
    "    if valor > saldo:\n"
    "        raise ValueError('saldo insuficiente')\n"
    "    return saldo - valor\n"
)
FORTE = (
    "import unittest\nfrom conta import saca\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_recusa(self):\n        with self.assertRaises(ValueError):\n            saca(10, 20)\n\n"
    "    def test_saca(self):\n        self.assertEqual(saca(10, 3), 7)\n"
)
FRACO = (
    "import unittest\nfrom conta import saca\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_saca(self):\n        self.assertEqual(saca(10, 3), 7)\n"
)
TROCAR = "if valor > saldo:"
POR = "if False:"


def cmd(modulo: str) -> str:
    return '"%s" -B -m unittest %s' % (caminho_bash(PYTHON), modulo)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.escreve(self.r, "conta.py", CONTA)
        self.escreve(self.r, "test_forte.py", FORTE)
        self.escreve(self.r, "test_fraco.py", FRACO)
        self.commit(self.r)
        self.tmpdir = self.tmp / "tmpdir"
        self.tmpdir.mkdir()
        self.env = dict(self.env, TMPDIR=str(self.tmpdir))

    def arvore(self) -> str:
        """Hash de cada arquivo (inclusive .git) e do git status, fora a pasta de evidência (onde o log vai)."""
        h = hashlib.sha256()
        for p in sorted(x for x in self.r.rglob("*") if x.is_file()):
            rel = p.relative_to(self.r).as_posix()
            if not rel.startswith("sdd/reports/evidence/"):
                h.update(rel.encode() + b"\0" + p.read_bytes())
        status = [l for l in self.git(self.r, "status", "--porcelain", "--untracked-files=all").splitlines()
                  if "sdd/" not in l]
        h.update("\n".join(status).encode())
        return h.hexdigest()

    def sabota(self, *, at="AT-001", arquivo="conta.py", trocar=TROCAR, por=POR, comando=None, sem=None,
               cwd=None) -> tuple[int, str]:
        args = {"--feature": F, "--at": at, "--arquivo": arquivo, "--trocar": trocar, "--por": por,
                "--cmd": comando if comando is not None else cmd("test_forte")}
        argv = [BASH, SCRIPT]
        for k, v in args.items():
            if k != sem:
                argv += [k, v]
        antes = self.arvore()
        rc, out, err = self.roda(argv, cwd or self.r)
        self.assertEqual(self.arvore(), antes, "a árvore de trabalho mudou\n" + out + err)
        self.assertEqual(list(self.tmpdir.iterdir()), [], "a cópia temporária ficou")
        self.assertEqual((self.r / "conta.py").read_text(encoding="utf-8"), CONTA)
        return rc, out + err

    def log(self) -> Path:
        return self.r / LOG


class AT013Sabotagem(Base):
    def test_teste_forte_pega_a_sabotagem(self):
        rc, out = self.sabota()
        self.assertEqual(rc, 0, out)
        self.assertIn("o teste pega o defeito", out)
        self.assertResultado(out)
        linhas = self.log().read_text(encoding="utf-8").splitlines()
        self.assertEqual(linhas[0], "$ " + cmd("test_forte"))
        self.assertTrue(any(l.startswith("# sabotagem: conta.py") and TROCAR in l and POR in l for l in linhas), linhas)
        self.assertIn("# sem a sabotagem: exit 0", linhas)
        self.assertRegex(linhas[-1], r"^\[exit=[1-9]\d*\]$")

    def test_teste_fraco_nao_pega(self):
        rc, out = self.sabota(comando=cmd("test_fraco"))
        self.assertEqual(rc, 2, out)
        self.assertIn("o teste não pega o defeito", out)
        self.assertResultado(out)
        self.assertEqual(self.log().read_text(encoding="utf-8").splitlines()[-1], "[exit=0]")

    def test_mudanca_nao_commitada_fica_e_a_copia_e_do_commit(self):
        self.escreve(self.r, "conta.py", CONTA + "# rascunho do aluno\n")
        antes = (self.r / "conta.py").read_bytes()
        argv = [BASH, SCRIPT, "--feature", F, "--at", "AT-001", "--arquivo", "conta.py", "--trocar", TROCAR,
                "--por", POR, "--cmd", cmd("test_forte")]
        rc, out, err = self.roda(argv, self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("último commit", out + err)
        self.assertEqual((self.r / "conta.py").read_bytes(), antes)
        self.assertEqual(list(self.tmpdir.iterdir()), [])


class AT014Inconclusivo(Base):
    def sem_log(self, rc: int, out: str, esperado: int, trecho: str) -> None:
        self.assertEqual(rc, esperado, out)
        self.assertIn(trecho, out)
        self.assertFalse(self.log().exists(), "gravou log fora do 0 e do 2")
        self.assertResultado(out)

    def test_trecho_que_nao_aparece(self):
        rc, out = self.sabota(trocar="if valor >= saldo:")
        self.sem_log(rc, out, 3, "0 vez(es)")

    def test_trecho_que_aparece_duas_vezes(self):
        rc, out = self.sabota(trocar="saldo")
        self.sem_log(rc, out, 3, "vez(es)")

    def test_comando_que_ja_falha_sem_a_sabotagem(self):
        rc, out = self.sabota(comando="false")
        self.sem_log(rc, out, 3, "já falha sem a sabotagem")

    def test_comando_que_nem_roda(self):
        rc, out = self.sabota(comando="comando-que-nao-existe-sdd")
        self.sem_log(rc, out, 3, "nem rodou")

    def test_caminho_absoluto(self):
        rc, out = self.sabota(arquivo=str(self.r / "conta.py"))
        self.sem_log(rc, out, 64, "relativo")

    def test_caminho_com_ponto_ponto(self):
        rc, out = self.sabota(arquivo="sub/../conta.py")
        self.sem_log(rc, out, 64, "..")

    def test_arquivo_fora_do_commit(self):
        self.escreve(self.r, "nova.py", "x = 1\n")
        rc, out = self.sabota(arquivo="nova.py", trocar="x = 1")
        self.sem_log(rc, out, 64, "commite")

    def test_argumento_faltando(self):
        rc, out = self.sabota(sem="--cmd")
        self.sem_log(rc, out, 64, "--cmd")

    def test_fora_de_git(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, out = self.sabota(cwd=fora)
        self.sem_log(rc, out, 64, "git")

    @unittest.skipIf(*SEM_SYMLINK)
    def test_link_simbolico_para_fora_da_copia(self):
        alvo = self.tmp / "fora.py"
        alvo.write_text(CONTA, encoding="utf-8")
        os.symlink(str(alvo), str(self.r / "link.py"))
        self.commit(self.r, "link")
        rc, out = self.sabota(arquivo="link.py")
        self.sem_log(rc, out, 64, "link simbólico")
        self.assertEqual(alvo.read_text(encoding="utf-8"), CONTA)


if __name__ == "__main__":
    unittest.main()
