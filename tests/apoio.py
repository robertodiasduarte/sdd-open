"""Sandbox comum das suítes de tests/: pasta temporária, git isolado, sem rede.

Rodar a suíte inteira: python3 -B -m unittest discover -s tests -p 'test_*.py'

Cada teste ganha uma pasta própria sem git acima dela (GIT_CEILING_DIRECTORIES), HOME falso e a
configuração global do git de quem roda fora (GIT_CONFIG_GLOBAL vazio, GIT_CONFIG_NOSYSTEM=1). Os
scripts rodam de verdade, por subprocess: o teste confere o contrato observável (exit e saída),
nunca a implementação. Requer bash, git e python3 >= 3.9; só stdlib.

⚠️ Nenhum teste pode conter literal que case com scripts/publish-gate-patterns.txt (CPF, CNPJ,
telefone, sequência de 11+ dígitos, caminho de home, e-mail fora de example.com): o publish-gate
reprovaria a própria pasta tests/. Amostras assim são montadas em tempo de execução.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
# SDD_TEST_BASH=/bin/bash roda a suíte no bash 3.2 do macOS, o piso que o open promete.
BASH = os.environ.get("SDD_TEST_BASH") or shutil.which("bash") or "bash"
PYTHON = sys.executable  # o mesmo interpretador da suíte: rodar com o 3.9 testa os linters no 3.9


def _symlink_ok() -> bool:
    """Tenta criar um link num temporário: no Windows, depende do modo de desenvolvedor."""
    d = tempfile.mkdtemp(prefix="sdd-open-link-")
    try:
        os.symlink(os.path.join(d, "alvo"), os.path.join(d, "link"))
        return True
    except (OSError, NotImplementedError, AttributeError):
        return False
    finally:
        shutil.rmtree(d, ignore_errors=True)


# F16: pulo por recurso que o sistema não tem. Um motivo por recurso, sempre daqui: tests/test_windows.py
# reprova skipIf/skipUnless de plataforma escrito fora deste arquivo. Uso: @unittest.skipIf(*SEM_FCNTL).
WINDOWS = os.name == "nt"
MACOS = sys.platform == "darwin"   # para o teste que NÃO pode ser pulado no piso (tests/test_contraste.py)
SEM_SYMLINK = (not _symlink_ok(), "link simbólico: este sistema não deixa criar (no Windows, exige o modo de desenvolvedor)")
SEM_FCNTL = (WINDOWS, "fcntl: o Windows não tem a trava POSIX")
SEM_CHMOD = (WINDOWS, "chmod: no Windows o bit de execução e a permissão de leitura não valem")
SEM_SINAL = (WINDOWS, "sinal POSIX: o Windows não entrega SIGTERM nem SIGKILL a um grupo de processos")
SEM_NOME_ESPECIAL = (WINDOWS, "nome de arquivo com aspas ou terminado em espaço: o Windows não aceita")
SEM_POSIX_UID = (not hasattr(os, "geteuid"), "os.geteuid: só existe em sistema POSIX")


def caminho_bash(p) -> str:
    """Caminho como o bash do Git o lê: no Windows, C:\\x\\y vira /c/x/y (C: partiria o PATH em dois)."""
    s = str(p)
    if WINDOWS and len(s) > 1 and s[1] == ":":
        return "/" + s[0].lower() + s[2:].replace("\\", "/")
    return s


SOU_ROOT = (hasattr(os, "geteuid") and os.geteuid() == 0, "root lê qualquer arquivo, com ou sem permissão")


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="sdd-open-")).resolve()
        self.home = self.tmp / "home"
        self.home.mkdir()
        vazio = self.tmp / "gitconfig-vazio"
        vazio.write_text("", encoding="utf-8")
        # SDD_TRACE e SDD_TRACE_DIR de quem roda a suíte não entram: com SDD_TRACE=off no ambiente, os testes
        # de trace cairiam sem o código ter mudado (🐛 da F12). Quem precisa de um dos dois passa no próprio teste.
        base = {k: v for k, v in os.environ.items() if k not in ("SDD_TRACE", "SDD_TRACE_DIR")}
        self.env = dict(
            base,
            HOME=str(self.home),
            GIT_CONFIG_GLOBAL=str(vazio),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CEILING_DIRECTORIES=str(self.tmp),
            GIT_TERMINAL_PROMPT="0",
            GIT_AUTHOR_NAME="teste",
            GIT_AUTHOR_EMAIL="teste@example.com",
            GIT_COMMITTER_NAME="teste",
            GIT_COMMITTER_EMAIL="teste@example.com",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def roda(self, args, cwd: Path, env: dict | None = None) -> tuple[int, str, str]:
        r = subprocess.run(
            [str(a) for a in args], cwd=str(cwd), env=env or self.env, capture_output=True,
            encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=120,
        )
        return r.returncode, r.stdout, r.stderr

    def git(self, repo: Path, *args: str) -> str:
        rc, out, err = self.roda(["git", *args], repo)
        self.assertEqual(rc, 0, "git " + " ".join(args) + " falhou: " + err)
        return out

    def repo(self, nome: str = "repo") -> Path:
        """Pasta nova com git init, sem nenhum repositório acima dela."""
        p = self.tmp / nome
        p.mkdir(parents=True)
        self.git(p, "init", "-q")
        return p

    def commit(self, repo: Path, msg: str = "c") -> None:
        self.git(repo, "add", "-A")
        self.git(repo, "commit", "-q", "--allow-empty", "-m", msg)

    def escreve(self, base: Path, rel: str, texto: str) -> Path:
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto, encoding="utf-8")
        return p

    def copia(self, rel: str, destino: Path) -> Path:
        """Copia RAIZ/rel (arquivo ou pasta) para destino/rel, preservando o bit de execução."""
        origem = RAIZ / rel
        alvo = destino / rel
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if origem.is_dir():
            shutil.copytree(str(origem), str(alvo))
        else:
            shutil.copy2(str(origem), str(alvo))
        return alvo

    def assertResultado(self, saida: str) -> None:
        """Convenção do open (docs/cli-conventions.md): todo veredito termina em RESULTADO: + →."""
        self.assertIn("RESULTADO:", saida)
