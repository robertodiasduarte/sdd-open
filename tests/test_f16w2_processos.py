"""F16W2, AT-004: o pre-commit e o init sem programa externo por arquivo onde um builtin do bash basta.

No Git Bash do Windows cada processo custa 10 a 20 ms: o 1º commit depois do init (~600 arquivos) passava de 120 s
(o hook lançava ~9 programas por arquivo) e o init, ~12 por arquivo gerado. A prova é contagem, não relógio (LM-031):
uma armadilha no PATH (cada ferramenta vira um script que anota a chamada e repassa à de verdade) conta os programas.
As recusas do hook continuam as de antes (governança dispensada com esta condição, DEFINE v1.1): as bordas que a
reescrita poderia afrouxar são testadas aqui; as regras inteiras seguem em test_hooks.py e test_alarme.py.
"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
from pathlib import Path

from apoio import BASH, RAIZ, SEM_CHMOD, Sandbox, caminho_bash
from test_alarme import cnpj, com_mascara_cnpj, com_mascara_cpf, cpf

HIGIENE = ".agents/skills/sdd-higiene-dado"
CONTADAS = ("basename", "dirname", "od", "tr", "wc", "grep", "head", "tail", "sed", "cmp", "awk", "cat", "cut",
            "mkdir", "chmod", "cp", "rm", "mktemp", "find", "sort", "git", "env", "ls", "date", "python3")


class Armadilha(Sandbox):
    def setUp(self):
        super().setUp()
        self.trap = self.tmp / "trap"
        self.trap.mkdir()
        self.contador = self.tmp / "contador.txt"
        for nome in CONTADAS:
            real = shutil.which(nome)
            if not real:
                continue
            p = self.trap / nome
            p.write_text('#!/bin/sh\necho %s >> "$CONTADOR"\nexec \'%s\' "$@"\n' % (nome, caminho_bash(real)),
                         encoding="utf-8")
            p.chmod(0o755)
        self.env_trap = dict(self.env, CONTADOR=caminho_bash(self.contador),
                             PATH=str(self.trap) + os.pathsep + self.env["PATH"])   # no Windows, ";" (revisão, rodada 2, R4)

    def contagem(self) -> int:
        return len(self.contador.read_text(encoding="utf-8").split("\n")) - 1 if self.contador.exists() else 0


class Contagem(Armadilha):
    def test_commit_de_600_arquivos_lanca_no_maximo_3_programas_por_arquivo(self):
        p = self.repo("projeto")
        self.copia("sdd/hooks", p)
        self.copia(HIGIENE, p)
        self.git(p, "config", "core.hooksPath", "sdd/hooks")
        self.git(p, "config", "sdd.higieneDado", "on")
        tipos = (".md", ".py", ".sh", ".json", ".yml", "", ".png", ".txt")
        for i in range(600):
            ext = tipos[i % len(tipos)]
            corpo = ("#!/bin/sh\necho %d\n" % i) if ext in ("", ".sh") else ("linha %d\n" % i)
            self.escreve(p, "d%02d/arq%03d%s" % (i % 20, i, ext), corpo)
        self.git(p, "add", "-A")
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "c"], p, env=self.env_trap)
        self.assertEqual(rc, 0, out + err)
        n = self.contagem()
        self.assertLessEqual(n, 3 * 600, "o hook lançou %d programas para 600 arquivos" % n)

    def test_init_lanca_no_maximo_3_programas_por_arquivo_gerado(self):
        p = self.repo("projeto")
        self.commit(p, "0")
        rc, out, err = self.roda([BASH, str(RAIZ / "bin/sdd-open.sh"), "init", "--yes", "--vendors", "claude,codex"],
                                 p, env=self.env_trap)
        self.assertEqual(rc, 0, out + err)
        gerados = sum(1 for f in p.rglob("*") if f.is_file() and ".git" not in f.parts)
        self.assertGreater(gerados, 300)
        n = self.contagem()
        # v2.16.0: ~11,7 programas por arquivo gerado (9.360 para 803, com os 5 vendors); a meta é menos da metade
        self.assertLessEqual(n, 3 * gerados, "o init lançou %d programas para %d arquivos" % (n, gerados))
        # o chmod passou a rodar só quando precisa: a cópia tem o bit de execução exatamente quando a fonte tem
        if not SEM_CHMOD[0]:
            fontes = RAIZ / ".agents/skills"
            vistos = 0
            for copia in (p / ".claude/skills").rglob("*"):
                if copia.is_file():
                    fonte = fontes / copia.relative_to(p / ".claude/skills")
                    with self.subTest(copia=str(copia.relative_to(p))):
                        self.assertEqual(os.access(str(copia), os.X_OK), os.access(str(fonte), os.X_OK))
                    vistos += os.access(str(fonte), os.X_OK)
            self.assertGreaterEqual(vistos, 1, "a amostra precisa de ao menos uma fonte executável")


class Recusas(Sandbox):
    """As bordas das recusas que a reescrita do hook mexeu: o hook novo recusa como o de antes."""

    def setUp(self):
        super().setUp()
        self.rng = random.Random(20261114)
        self.p = self.repo("projeto")
        self.copia("sdd/hooks", self.p)
        self.copia(HIGIENE, self.p)
        self.git(self.p, "config", "core.hooksPath", "sdd/hooks")
        self.git(self.p, "config", "sdd.higieneDado", "on")
        self.escreve(self.p, "README.md", "# projeto\n")
        self.commit(self.p, "base")

    def tenta(self, env: dict | None = None) -> tuple[int, str]:
        self.git(self.p, "add", "-A")
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t"], self.p, env=env)
        return rc, out + err

    def bytes(self, rel: str, dado: bytes) -> None:
        alvo = self.p / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_bytes(dado)

    def test_nul_depois_de_8_kb_e_extensao_maiuscula_sao_recusados(self):
        self.bytes("fundo.md", b"x" * 9000 + b"\x00\n")
        self.bytes("GRITO.MD", b"a\x00b\n")
        rc, saida = self.tenta()
        self.assertEqual(rc, 1, saida)
        self.assertIn("[H5] fundo.md: 1 byte(s) NUL", saida)
        self.assertIn("[H5] GRITO.MD: 1 byte(s) NUL", saida)

    def test_commit_grande_com_cor_ligada_acha_o_nul(self):
        # acima de 40 candidatos o hook usa o git grep do índice; com color.ui=always o nome vinha com códigos ANSI e
        # nunca casava (raio de impacto da release)
        self.git(self.p, "config", "color.ui", "always")
        self.git(self.p, "config", "color.grep", "always")
        for i in range(45):
            self.escreve(self.p, "docs/n%02d.md" % i, "limpo %d\n" % i)
        self.bytes("fundo.md", b"x" * 9000 + b"\x00\n")
        self.bytes("GRITO.MD", b"a\x00b\n")
        rc, saida = self.tenta()
        self.assertEqual(rc, 1, saida)
        self.assertIn("[H5] fundo.md: 1 byte(s) NUL", saida)
        self.assertIn("[H5] GRITO.MD: 1 byte(s) NUL", saida)

    def test_nome_com_byte_que_nao_e_utf8_ainda_e_conferido(self):
        # num terminal UTF-8, o [[ =~ ]] do bash não casava o nome com byte inválido; o hook compara em bytes (LC_ALL=C)
        r = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=str(self.p), env=self.env, input=b"a\x00b\n",
                           capture_output=True)
        sha = r.stdout.decode().strip()
        try:
            r = subprocess.run([b"git", b"update-index", b"--add", b"--cacheinfo", b"100644," + sha.encode() + b",caf\xe9.MD"],
                               cwd=str(self.p), env=self.env, capture_output=True)
        except (OSError, UnicodeError, TypeError):
            self.skipTest("este sistema não passa nome que não é UTF-8 na linha de comando")
        self.assertEqual(r.returncode, 0, r.stderr)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t"], self.p, env=dict(self.env, LANG="en_US.UTF-8",
                                                                                      LC_ALL="en_US.UTF-8"))
        self.assertEqual(rc, 1, out + err)
        self.assertIn("[H5] caf", out + err)

    def test_utf16_com_bom_e_binario_passam(self):
        self.bytes("planilha.txt", b"\xff\xfea\x00b\x00")
        self.bytes("img.png", b"\x89PNG\x00\x00")
        self.bytes("sem_ext_binario", b"\x7fELF\x00\x00")
        rc, saida = self.tenta()
        self.assertEqual(rc, 0, saida)

    def test_sem_pcre_o_caminho_por_arquivo_recusa_igual(self):
        # um git falso que diz "sem PCRE" ao `git grep -P` e repassa o resto ao git de verdade
        falso = self.tmp / "semPcre"
        falso.mkdir()
        g = falso / "git"
        g.write_text('#!/bin/sh\ncase "$1" in grep) echo "fatal: sem PCRE" >&2; exit 128 ;; esac\n'
                     "exec '%s' \"$@\"\n" % caminho_bash(shutil.which("git")), encoding="utf-8")
        g.chmod(0o755)
        for i in range(45):   # acima de 40 candidatos: o hook tenta o git grep, que aqui diz "sem PCRE"
            self.escreve(self.p, "docs/n%02d.md" % i, "limpo %d\n" % i)
        self.bytes("a.md", b"a\x00b\n")
        self.bytes("u16.txt", b"\xfe\xff\x00a")
        self.bytes("script", b"#!/bin/sh\n\x00\n")
        env = dict(self.env, PATH=caminho_bash(falso) + ":" + self.env["PATH"])
        rc, saida = self.tenta(env)
        self.assertEqual(rc, 1, saida)
        self.assertIn("[H5] a.md: 1 byte(s) NUL", saida)
        self.assertIn("[H5] script: 1 byte(s) NUL", saida)
        self.assertNotIn("u16.txt", saida)

    def test_cpf_cnpj_certificado_env_planilha_e_credencial_continuam_recusados(self):
        cpf_m = com_mascara_cpf(cpf(self.rng))
        cnpj_m = com_mascara_cnpj(cnpj(self.rng))
        self.escreve(self.p, "notas.md", "cliente %s, empresa %s\n" % (cpf_m, cnpj_m))
        self.bytes("CERT.PFX", b"\x30\x82binario")
        self.escreve(self.p, "chave.pem", "-----BEGIN PRIVATE" + " KEY-----\nabc\n")
        self.escreve(self.p, ".env", "X=1\n")
        self.escreve(self.p, "clientes.XLSX", "dado")
        self.escreve(self.p, "conf/App.JSON", '{"password": "%s"}\n' % ("s3gr3d0" + "Real9"))
        rc, saida = self.tenta()
        self.assertEqual(rc, 1, saida)
        for trecho in ("[H3] conf/App.JSON: credencial em texto claro (chave: password)",
                       "CERT.PFX: certificado digital", "chave.pem: chave privada", ".env: arquivo de senhas",
                       "clientes.XLSX: planilha nova", "notas.md:1: CPF", "notas.md:1: CNPJ"):
            self.assertIn(trecho, saida)


if __name__ == "__main__":
    import unittest
    unittest.main()
