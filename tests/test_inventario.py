"""Testes do inventario.sh da sdd-iniciar-repo: o que entraria no git, a proposta de .gitignore e as
pré-condições (pasta sincronizada, pasta pessoal, repositório em subpasta ou acima).

Portado do sdd-starter (skills/sdd-iniciar-repo/tests, commit 17c69c4) para tests/ do sdd-open: o script
fica em .agents/skills/sdd-iniciar-repo/scripts/ e o teste não vai para o projeto do usuário.
Rodar: python3 -B -m unittest discover -s tests -p "test_inventario.py"

Sem rede. Cada teste monta uma pasta temporária sem git acima dela (GIT_CEILING_DIRECTORIES), com HOME
falso e a configuração global do git de quem roda fora (GIT_CONFIG_GLOBAL vazio). Requer bash e git.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / ".agents" / "skills" / "sdd-iniciar-repo" / "scripts" / "inventario.sh"
BASH = os.environ.get("SDD_TEST_BASH") or shutil.which("bash") or "bash"   # SDD_TEST_BASH=/bin/bash: piso 3.2


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="inventario-")).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.raiz = self.tmp / "RDD10V8M6Financas"
        self.raiz.mkdir()
        self.global_vazio = self.tmp / "gitconfig-global"
        self.global_vazio.write_text("", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def escreve(self, nome: str, conteudo: str = "x\n") -> Path:
        p = self.raiz / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8")
        return p

    def grande(self, nome: str, mb: int) -> None:
        p = self.raiz / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:   # esparso: não ocupa disco
            f.truncate(mb * 1024 * 1024)

    def git(self, *args: str, cwd: Path | None = None) -> None:
        subprocess.run(["git", *args], cwd=cwd or self.raiz, check=True, capture_output=True,
                       env={**os.environ, "GIT_CONFIG_GLOBAL": str(self.global_vazio), "GIT_CONFIG_NOSYSTEM": "1"})

    def roda(self, pasta: Path | None = None) -> tuple[int, str]:
        env = {**os.environ, "HOME": str(self.home), "GIT_CEILING_DIRECTORIES": str(self.tmp),
               "GIT_CONFIG_GLOBAL": str(self.global_vazio), "GIT_CONFIG_NOSYSTEM": "1"}
        r = subprocess.run([BASH, str(SCRIPT)], cwd=pasta or self.raiz, capture_output=True, text=True,
                           env=env, stdin=subprocess.DEVNULL, timeout=60)
        return r.returncode, r.stdout

    def inventario(self) -> str:
        rc, out = self.roda()
        self.assertEqual(rc, 0, out)
        return out

    @staticmethod
    def proposta(out: str) -> list[str]:
        """Linhas do bloco da proposta de .gitignore (depois do cabeçalho, sem comentários)."""
        linhas = out.splitlines()
        i = next(n for n, l in enumerate(linhas) if l.startswith("Proposta de .gitignore"))
        return [l for l in linhas[i + 1:] if l.strip() and not l.startswith("#")]


class TestAchados(Base):
    def test_cinco_categorias(self):
        self.escreve(".env", "SENHA=x\n")
        self.escreve(".env.example", "SENHA=\n")
        self.escreve("certificados/empresa.pfx")
        self.escreve("dados/clientes.xlsx")
        self.grande("aulas/aula-01.mp4", 60)
        self.escreve("node_modules/pacote/index.js")
        self.escreve("README.md")
        out = self.inventario()
        for achado in (".env", "certificados/empresa.pfx", "dados/clientes.xlsx", "aulas/aula-01.mp4",
                       "node_modules/"):
            self.assertIn(achado, out)
        self.assertIn("60 MB", out)
        self.assertNotIn(".env.example", out.split("Proposta de .gitignore")[0])
        self.assertNotIn("pacote/index.js", out)   # dependência aparece como pasta, não arquivo a arquivo

    def test_proposta_cobre_o_que_achou(self):
        self.escreve(".env")
        self.escreve("empresa.p12")
        self.escreve("dados/extrato.csv")
        self.grande("aula.mov", 55)
        self.escreve(".venv/lib/x.py")
        linhas = self.proposta(self.inventario())
        for esperado in (".env", ".env.*", "!.env.example", "*.p12", "*.pfx", "*.csv", "*.xlsx",
                         "/aula.mov", ".venv/", "node_modules/"):
            self.assertIn(esperado, linhas)

    def test_sem_planilha_nem_grande_a_proposta_fica_na_base(self):
        self.escreve("README.md")
        out = self.inventario()
        self.assertIn("Nada sensível", out)
        linhas = self.proposta(out)
        self.assertIn(".env", linhas)
        self.assertNotIn("*.xlsx", linhas)

    def test_gitignore_existente_nao_repete_linha(self):
        self.escreve(".gitignore", ".env\nnode_modules/\n")
        self.escreve("a.pfx")
        linhas = self.proposta(self.inventario())
        self.assertNotIn(".env", linhas)
        self.assertNotIn("node_modules/", linhas)
        self.assertIn("*.pfx", linhas)

    def test_gitignore_existente_ja_esconde_o_arquivo(self):
        self.escreve(".gitignore", "segredos/\n")
        self.escreve("segredos/.env")
        self.escreve("README.md")
        out = self.inventario()
        self.assertNotIn("segredos/.env", out)

    def test_limite_de_dez_por_categoria(self):
        for i in range(12):
            self.escreve(f"planilhas/cliente-{i:02d}.xlsx")
        out = self.inventario()
        self.assertIn("planilhas/cliente-09.xlsx", out)
        self.assertNotIn("planilhas/cliente-10.xlsx", out)
        self.assertIn("e mais 2", out)

    def test_nome_com_espaco(self):
        self.escreve("Ana Silva/dados clientes.xlsx")
        out = self.inventario()
        self.assertIn("Ana Silva/dados clientes.xlsx", out)

    def test_com_git_ve_o_que_esta_no_repositorio(self):
        self.git("init", "-q")
        self.escreve(".gitignore", "*.xlsx\n")
        self.escreve("ignorada.xlsx")
        self.escreve(".env")
        self.git("add", "-f", ".env", ".gitignore")
        self.git("-c", "user.name=T", "-c", "user.email=t@example.com", "commit", "-q", "--no-verify", "-m", "t")
        out = self.inventario()
        self.assertIn(".env", out.split("Proposta de .gitignore")[0])
        self.assertNotIn("ignorada.xlsx", out)

    def test_historico_mostra_segredo_ja_apagado(self):
        # Publicar leva o histórico inteiro: um .env apagado depois continua lá.
        ident = ("-c", "user.name=T", "-c", "user.email=t@example.com")
        self.git("init", "-q")
        self.escreve(".env")
        self.escreve("dados/clientes.csv")
        self.escreve("README.md")
        self.git("add", "-f", ".env", "dados/clientes.csv", "README.md")
        self.git(*ident, "commit", "-q", "--no-verify", "-m", "1")
        self.git("rm", "-q", ".env", "dados/clientes.csv")
        self.git(*ident, "commit", "-q", "--no-verify", "-m", "2")
        out = self.inventario()
        self.assertIn("histórico", out)
        historico = out.split("histórico", 1)[1].split("Proposta de .gitignore")[0]
        self.assertIn(".env", historico)
        self.assertIn("dados/clientes.csv", historico)

    def test_sem_commit_nao_fala_de_historico(self):
        self.git("init", "-q")
        self.escreve(".env")
        self.assertNotIn("histórico", self.inventario())

    def test_nome_com_aspas_e_barra(self):
        # O git põe entre aspas o caminho com " ou \ mesmo com core.quotepath=off: a lista vem com -z.
        self.escreve('dados "cliente"/cert.pfx')
        self.escreve("a\\b.xlsx")
        antes = self.inventario().split("Proposta de .gitignore")[0]
        self.assertIn('dados "cliente"/cert.pfx', antes)
        self.assertIn("a\\b.xlsx", antes)

    def test_nome_com_aspas_no_historico(self):
        ident = ("-c", "user.name=T", "-c", "user.email=t@example.com")
        self.git("init", "-q")
        self.escreve('dados "cliente"/cert.pfx')
        self.escreve("README.md")
        self.git("add", "-A")
        self.git(*ident, "commit", "-q", "--no-verify", "-m", "1")
        self.git("rm", "-q", "-r", "dados \"cliente\"")
        self.git(*ident, "commit", "-q", "--no-verify", "-m", "2")
        historico = self.inventario().split("histórico", 1)[1]
        self.assertIn('dados "cliente"/cert.pfx', historico)

    def ignorado_depois(self, nome: str) -> bool:
        """Aplica a proposta ao .gitignore numa cópia e pergunta ao git se o arquivo fica de fora."""
        out = self.inventario()
        linhas = out.splitlines()
        i = next(n for n, l in enumerate(linhas) if l.startswith("Proposta de .gitignore"))
        copia = self.tmp / "copia"
        shutil.rmtree(copia, ignore_errors=True)
        shutil.copytree(self.raiz, copia)
        with open(copia / ".gitignore", "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(linhas[i + 1:]) + "\n")
        self.git("init", "-q", cwd=copia)
        self.git("config", "core.ignoreCase", "false", cwd=copia)
        r = subprocess.run(["git", "check-ignore", "-q", "--no-index", nome], cwd=copia,
                           env={**os.environ, "GIT_CONFIG_GLOBAL": str(self.global_vazio)})
        return r.returncode == 0

    def test_proposta_vence_negacao_existente(self):
        self.escreve(".gitignore", ".env\n!.env\n")
        self.escreve(".env")
        self.assertTrue(self.ignorado_depois(".env"))

    def test_proposta_cobre_maiuscula(self):
        self.escreve("cert.PFX")
        self.escreve("dados/Clientes.XLSX")
        self.escreve(".ENV")
        for nome in ("cert.PFX", "dados/Clientes.XLSX", ".ENV"):
            self.assertTrue(self.ignorado_depois(nome), nome)

    def test_proposta_escapa_caminho_grande(self):
        self.grande("aula[1].mp4", 55)
        self.assertTrue(self.ignorado_depois("aula[1].mp4"))

    def test_proposta_escapa_espaco_no_fim(self):
        # O git descarta espaço no fim de uma linha do .gitignore, a não ser escapado.
        self.grande("video.mp4 ", 55)
        self.assertTrue(self.ignorado_depois("video.mp4 "))

    def test_falha_ao_listar_nao_vira_nada_sensivel(self):
        self.escreve(".env")
        bin_ = self.tmp / "bin"
        bin_.mkdir()
        falso = bin_ / "git"
        real = shutil.which("git")
        # git que funciona para as pré-condições e falha só ao listar arquivos.
        falso.write_text(f'#!/bin/sh\nfor a in "$@"; do [ "$a" = ls-files ] && exit 128; done\nexec "{real}" "$@"\n',
                         encoding="utf-8")
        falso.chmod(0o755)
        env = {**os.environ, "HOME": str(self.home), "GIT_CEILING_DIRECTORIES": str(self.tmp),
               "GIT_CONFIG_GLOBAL": str(self.global_vazio), "GIT_CONFIG_NOSYSTEM": "1",
               "PATH": f"{bin_}{os.pathsep}{os.environ['PATH']}"}
        r = subprocess.run([BASH, str(SCRIPT)], cwd=self.raiz, capture_output=True, text=True, env=env,
                           stdin=subprocess.DEVNULL, timeout=60)
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertNotIn("Nada sensível", r.stdout)

    def test_conta_arquivos(self):
        for n in ("a.md", "b.md", "c/d.md"):
            self.escreve(n)
        self.assertIn("3 arquivos", self.inventario())


class TestPreCondicoes(Base):
    def test_pasta_sincronizada(self):
        for rel, provedor in (("Dropbox/Financas", "Dropbox"),
                              ("home/Library/Mobile Documents/com~apple~CloudDocs/Financas", "iCloud Drive"),
                              ("OneDrive - Escritorio/Financas", "OneDrive")):
            with self.subTest(rel=rel):
                p = self.tmp / rel
                p.mkdir(parents=True)
                (p / "a.md").write_text("x\n", encoding="utf-8")
                rc, out = self.roda(p)
                self.assertEqual(rc, 2, out)
                self.assertIn(provedor, out)
                self.assertIn("sincroniza", out)
                self.assertNotIn("Proposta de .gitignore", out)

    def test_icloud_mesa_e_documentos(self):
        p = self.home / "Documents" / "Financas"
        p.mkdir(parents=True)
        nuvem = self.home / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
        nuvem.mkdir(parents=True)
        (nuvem / "Documents").symlink_to(self.home / "Documents")
        rc, out = self.roda(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("iCloud Drive", out)

    def test_pasta_pessoal(self):
        (self.home / "notas.txt").write_text("x\n", encoding="utf-8")
        rc, out = self.roda(self.home)
        self.assertEqual(rc, 2, out)
        self.assertIn("pasta pessoal", out)

    def test_repositorio_numa_subpasta(self):
        self.escreve("app/README.md")
        self.git("init", "-q", cwd=self.raiz / "app")
        rc, out = self.roda()
        self.assertEqual(rc, 2, out)
        self.assertIn("./app", out)

    def test_dentro_de_um_repositorio_maior(self):
        self.git("init", "-q")
        sub = self.raiz / "docs"
        sub.mkdir()
        (sub / "a.md").write_text("x\n", encoding="utf-8")
        rc, out = self.roda(sub)
        self.assertEqual(rc, 2, out)
        self.assertIn(str(self.raiz), out)


class TestSomenteLeitura(Base):
    def test_nao_grava_nada(self):
        self.escreve(".env")
        self.escreve("dados/clientes.xlsx")
        self.escreve("node_modules/p/i.js")
        antes = sorted((str(p), p.stat().st_mtime_ns) for p in self.raiz.rglob("*"))
        self.inventario()
        self.assertEqual(antes, sorted((str(p), p.stat().st_mtime_ns) for p in self.raiz.rglob("*")))
        self.assertFalse((self.raiz / ".git").exists())
        self.assertFalse((self.raiz / ".gitignore").exists())


if __name__ == "__main__":
    unittest.main()
