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
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# F22: a suíte nunca vai à rede. O doctor (que roda no fim de todo init) consulta se saiu versão nova do SDD Open; aqui
# a consulta fica desligada, e o endereço aponta para uma pasta que não existe, para falhar local mesmo se um teste a
# religar por engano. Quem testa a consulta liga a variável e aponta SDD_OPEN_REMOTO para um repositório local.
# setdefault: quem roda a suíte pode trocar os dois de propósito. Todo módulo que roda o sdd-open.sh importa este
# (tests/test_f22_versao.py reprova o que não importa).
os.environ.setdefault("SDD_OPEN_CHECK_UPDATES", "0")
os.environ.setdefault("SDD_OPEN_REMOTO", os.path.join(tempfile.gettempdir(), "sdd-open-sem-rede-nos-testes", "nada.git"))

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
SEM_NOME_ESPECIAL = (WINDOWS, "nome de arquivo com aspas, dois-pontos, barra vertical, quebra de linha ou terminado em espaço: "
                                "o Windows não aceita")
SEM_POSIX_UID = (not hasattr(os, "geteuid"), "os.geteuid: só existe em sistema POSIX")
SEM_PATH_SEM_FERRAMENTA = (WINDOWS, "PATH sem uma ferramenta: no Windows o PATH restrito é feito das pastas de verdade (o "
                                    "executável chamado por link não acha as DLLs ao lado), e a pasta traz a ferramenta junto")
SEM_ARGV_COM_QUEBRA = (WINDOWS, "argumento com quebra de linha: no Windows a linha de comando o parte em dois")
SEM_PTY = (WINDOWS, "pty: o Windows não tem terminal POSIX (termios)")
SEM_FIFO = (not hasattr(os, "mkfifo"), "fifo (os.mkfifo): o Windows não tem pipe com nome no sistema de arquivos")
SO_NO_WINDOWS = (WINDOWS, "caminho C:\\…: só o Windows tem letra de unidade")   # para skipUnless
SEM_PACOTE_ANTIGO = (WINDOWS, "pacote real anterior à v2.16.1: o init dele não roda no Git Bash do Windows (o porte é "
                              "da F16W2); o caminho do upgrade no Windows é provado pelo pacote de teste")


def path_restrito(pasta: Path, ferramentas, python: bool = True, ausentes=(), extra=None) -> str:
    """PATH só com as ferramentas pedidas (e o Python da suíte, se python=True), para testar "sem X no PATH".

    Fora do Windows: uma pasta de links, como os testes sempre fizeram. No Windows, o executável chamado por link não
    acha as DLLs ao lado (msys-2.0.dll, python3xx.dll): o `dirname` "existia" e devolvia vazio, e o python3 não rodava
    (F16W2, ~105 quedas). Lá, o PATH são as pastas de verdade das ferramentas (nunca a System32, que tem o bash do WSL)
    e a do Python. `ausentes` são os nomes que o teste quer fora do PATH: no Windows, se a pasta de verdade traz um
    deles, o teste é pulado (SEM_PATH_SEM_FERRAMENTA). `extra` = {nome: arquivo} postos na pasta (scripts falsos)."""
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, alvo in (extra or {}).items():
        if WINDOWS:   # o script falso chamado pelo caminho de verdade: $0 continua apontando para ele
            p = pasta / nome
            p.write_text("#!/bin/sh\nexec '%s' \"$@\"\n" % caminho_bash(alvo), encoding="utf-8")
            p.chmod(0o755)
        else:
            (pasta / nome).symlink_to(alvo)
    if not WINDOWS:
        for f in ferramentas:
            w = shutil.which(f)
            if w and not (pasta / f).exists():
                (pasta / f).symlink_to(w)
        if python and not (pasta / "python3").exists():
            (pasta / "python3").symlink_to(sys.executable)
        path = str(pasta)
    else:
        sistema = os.path.normcase(os.environ.get("SystemRoot", r"C:\Windows"))
        dirs = []
        for f in ferramentas:
            w = os.path.dirname(BASH) if f in ("bash", "sh") else os.path.dirname(shutil.which(f) or "")
            if w and not os.path.normcase(w).startswith(sistema) and w not in dirs:
                dirs.append(w)
        if python and os.path.dirname(sys.executable) not in dirs:
            dirs.append(os.path.dirname(sys.executable))
        path = os.pathsep.join([str(pasta)] + dirs)
    for nome in ausentes:
        if shutil.which(nome, path=path):
            if WINDOWS:
                raise unittest.SkipTest(SEM_PATH_SEM_FERRAMENTA[1] + " (%s)" % nome)
            raise AssertionError("%s não devia estar no PATH restrito" % nome)
    return path


# F16W2: no Windows, Path.write_text troca "\n" por "\r\n"; o repositório é LF (.gitattributes, eol=lf) e os scripts
# leem as fixtures em bytes (o gerador do starter recusava "---\r\n" como frontmatter). Nos testes, o padrão é "\n";
# quem quer CRLF escreve "\r\n" (passa intacto) ou passa newline= explícito.
if WINDOWS:
    def _write_text_lf(self, data, encoding=None, errors=None, newline=None):
        # por open() e não pelo write_text(newline=), que só existe a partir do Python 3.10 (revisão, rodada 3, R2)
        with open(str(self), "w", encoding=encoding, errors=errors, newline="\n" if newline is None else newline) as f:
            return f.write(data)

    Path.write_text = _write_text_lf


def apaga(p) -> None:
    """rmtree que também apaga o arquivo só leitura (no Windows, os objetos do git): sem isso a pasta ficava, e o
    próximo subteste que a recriava caía com FileExistsError (F16W2)."""
    def _de_novo(func, caminho, _erro):
        os.chmod(caminho, 0o700)
        func(caminho)
    if sys.version_info >= (3, 12):
        shutil.rmtree(str(p), onexc=_de_novo)
    else:
        shutil.rmtree(str(p), onerror=_de_novo)


def caminho_neutro(s: str) -> str:
    """No Windows, C:\\x, C:/x e /c/x viram /c/x: o produto escreve uma forma ou outra conforme quem lhe deu o caminho
    (o git, o HOME, o pwd do Git Bash), e o teste compara o lugar, não a grafia (F16W2). Fora do Windows, nada muda."""
    if not WINDOWS:
        return s
    s = s.replace("\\", "/")
    return re.sub(r"(?<![\w/])([A-Za-z]):/", lambda m: "/" + m.group(1).lower() + "/", s)


def caminho_bash(p) -> str:
    """Caminho como o bash do Git o lê: no Windows, C:\\x\\y vira /c/x/y (C: partiria o PATH em dois)."""
    s = str(p)
    if WINDOWS and len(s) > 1 and s[1] == ":":
        return "/" + s[0].lower() + s[2:].replace("\\", "/")
    return s


def caminho_nativo(s: str) -> str:
    """O contrário de caminho_bash: no Windows, /c/x/y volta a ser C:\\x\\y para o Python abrir."""
    if WINDOWS and len(s) > 2 and s[0] == "/" and s[2] == "/" and s[1].isalpha():
        return s[1].upper() + ":" + s[2:].replace("/", "\\")
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
        # F16: SDD_PYTHON_RESOLVIDO e PYTHONIOENCODING também não: rodando debaixo de um script do pacote (test-baseline,
        # verify-gate), o teste herdaria o Python resolvido pelo pai e o "sem python3" deixaria de valer.
        base = {k: v for k, v in os.environ.items()
                if k not in ("SDD_TRACE", "SDD_TRACE_DIR", "SDD_PYTHON_RESOLVIDO", "PYTHONIOENCODING")}
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
