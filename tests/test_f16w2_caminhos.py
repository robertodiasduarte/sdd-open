"""F16W2, AT-003: as formas de caminho e de fim de linha do Windows nos scripts que a 1ª medição acusou.

O Windows de verdade (C:\\ × /c/ × /tmp/, o \\r do print do Python) só o CI do PR mostra; aqui fica o que dá para
simular em qualquer sistema: o valor literal "C:\\…" e um python3 que escreve "\\r\\n" como o do Windows.
"""
from __future__ import annotations

import os
import sys

import test_sdd_archive
import test_test_baseline

from apoio import BASH, Sandbox, caminho_bash


class SlotComCr(Sandbox):
    """O slot.sh lia "VALOR\\r" e dizia que o slot estava vazio (39 quedas no Windows). Sem o calço (script copiado
    sozinho, sem lib/python.sh), a rede local do próprio slot tira o \\r."""

    def test_valor_com_cr_e_lido_e_roda(self):
        r = self.repo()
        self.copia("sdd/bin/slot.sh", r)
        self.escreve(r, "sdd/config.yaml", 'smoke:\n  before_ok_cmd: "echo rodou-o-slot"\n')
        self.commit(r, "base")
        falso = self.tmp / "py"
        falso.mkdir()
        py = falso / "python3"
        # awk, não sed: o sed BSD antigo troca "\\r" pela letra r (revisão, rodada 1, R4)
        py.write_text("#!/bin/sh\n'%s' \"$@\" | awk '{printf \"%%s\\r\\n\", $0}'\n" % caminho_bash(sys.executable),
                      encoding="utf-8")
        py.chmod(0o755)
        env = dict(self.env, PATH=str(falso) + os.pathsep + self.env["PATH"], TMPDIR=str(self.tmp))
        rc, out, err = self.roda([BASH, "sdd/bin/slot.sh", "smoke.before_ok_cmd"], r, env=env)
        self.assertNotIn("vazio: pulado", out + err)
        self.assertIn("rodou-o-slot", out + err)
        self.assertEqual(rc, 0, out + err)


# ── AT-003 no Mac: os.path.join do Windows (avaliador, ciclo 1, A1) ─────────────────────────────────────────────────
# Roda um programa Python cujo os.path.join é o ntpath.join (como o Python nativo do Windows), só nas chamadas do próprio
# programa (a stdlib segue posix), num sistema de arquivos que aceita "\\" e "/" (como o Windows). Aceita o jeito que os
# scripts chamam: `python3 [-B -I …] <script> args`, `python3 [flags] - args` (o programa no stdin) e `python3 -c código`.
WINPATH = r'''import builtins, ntpath, os, posixpath, sys
args = sys.argv[1:]
while args and args[0].startswith("-") and args[0] not in ("-", "-c"):
    args.pop(0)
if args and args[0] == "-c":
    sys.argv = ["-c"] + args[2:]
    exec(compile(args[1], "<string>", "exec"), {"__name__": "__main__"})
    sys.exit(0)
alvo = "<windows-stdin>" if args[0] == "-" else os.path.abspath(args[0])
fonte = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
import argparse, collections, datetime, re, subprocess, json, shlex, fnmatch, hashlib, tempfile, shutil  # antes do remendo
_pj = posixpath.join
barra = lambda p: p.replace("\\", "/") if isinstance(p, str) else p
os.path.join = lambda *a: (ntpath.join if sys._getframe(1).f_code.co_filename == alvo else _pj)(*a)
for nome in ("isdir", "isfile", "exists", "islink", "getmtime"):
    orig = getattr(os.path, nome); setattr(os.path, nome, (lambda o: lambda p, *a, **k: o(barra(p), *a, **k))(orig))
for nome in ("listdir", "stat", "lstat"):
    orig = getattr(os, nome); setattr(os, nome, (lambda o: lambda p=".", *a, **k: o(barra(p), *a, **k))(orig))
_open = builtins.open
builtins.open = lambda p, *a, **k: _open(barra(p), *a, **k)
sys.argv = args
exec(compile(fonte, alvo, "exec"), {"__name__": "__main__", "__file__": alvo})
'''


def winpath(tmp):
    """O executor e um python3 que o usa, numa pasta para pôr à frente do PATH."""
    runner = tmp / "winpath_run.py"
    runner.write_text(WINPATH, encoding="utf-8")
    pasta = tmp / "py-windows"
    pasta.mkdir(exist_ok=True)
    py = pasta / "python3"
    py.write_text("#!/bin/sh\nexec '%s' '%s' \"$@\"\n" % (caminho_bash(sys.executable), caminho_bash(runner)),
                  encoding="utf-8")
    py.chmod(0o755)
    return runner, pasta


class ArchiveComNtpath(test_sdd_archive.Base):
    """sdd-archive.py juntava "sdd" e a subpasta com os.path.join: no Windows, sdd\\features/X.md nunca casava com o git."""

    def test_os_lotes_saem_como_no_mac(self):
        runner, _ = winpath(self.tmp)
        self.doc("sdd/features/DEFINE_A.md")
        self.doc("sdd/reports/BUILD_REPORT_A.md")
        self.doc("sdd/releases/A/s1.yaml")
        self.doc("sdd/features/DESIGN_B.md")
        rc, out, err = self.roda([sys.executable, str(runner), str(test_sdd_archive.SCRIPT), "--hoje",
                                  test_sdd_archive.HOJE], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("== Lote com-ledger: 2 arquivo(s) ==", out)
        self.assertIn("sdd/features/DEFINE_A.md  →  sdd/archive/A/DEFINE_A.md", out)
        self.assertIn("sdd/features/DESIGN_B.md  →  sdd/archive/B/DESIGN_B.md", out)
        self.assertNotIn("\\", out)


class BaselineComNtpath(test_test_baseline.TestBaseline):
    """A suíte inteira do test-baseline, com o Python embutido dele juntando caminhos como no Windows (o id do
    vizinho em src\\foo.test.ts nunca casava com src/foo.test.ts)."""

    def setUp(self):
        super().setUp()
        _, pasta = winpath(self.tmp)
        self.env = dict(self.env, PATH=str(pasta) + os.pathsep + self.env["PATH"])


if __name__ == "__main__":
    import unittest
    unittest.main()
