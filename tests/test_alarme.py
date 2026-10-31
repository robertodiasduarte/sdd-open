"""Testes do alarme de commit da sdd-higiene-dado.

Portado do sdd-starter (skills/sdd-higiene-dado/tests, commit 17c69c4) para tests/ do sdd-open: a skill
fica em .agents/skills/sdd-higiene-dado/ e o teste não vai para o projeto do usuário.
Rodar: python3 -B -m unittest discover -s tests -p "test_alarme.py"

Todo CPF/CNPJ usado aqui é gerado em tempo de execução: o repositório não pode conter CPF, CNPJ nem
sequência literal de 11 dígitos (o G2 de scripts/publish-gate.sh reprova).
Requer bash, git e awk.
"""
from __future__ import annotations

import os
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SKILL = RAIZ / ".agents" / "skills" / "sdd-higiene-dado"
ALARME = SKILL / "scripts" / "alarme.sh"
HOOK_ORIGEM = SKILL / "scripts" / "pre-commit.sh"
# A configuração git de quem roda fica de fora: um core.hooksPath global (git-secrets, padrão corporativo)
# faria o alarme recusar a instalação e a suíte ficar vermelha sem defeito no código.
ISOLADO = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
BASH = os.environ.get("SDD_TEST_BASH") or shutil.which("bash") or "bash"   # SDD_TEST_BASH=/bin/bash: piso 3.2


def dv_cpf(base: str) -> str:
    for n in (9, 10):
        t = sum(int(base[i]) * (n + 1 - i) for i in range(n))
        r = (t * 10) % 11
        base += str(0 if r == 10 else r)
    return base


def dv_cnpj(base: str) -> str:
    for n in (12, 13):
        # pesos: 12 -> 5,4,3,2,9..2 ; 13 -> 6,5,4,3,2,9..2
        pesos = list(range(n - 7, 1, -1)) + list(range(9, 1, -1))
        t = sum(int(base[i]) * pesos[i] for i in range(n))
        r = t % 11
        base += str(0 if r < 2 else 11 - r)
    return base


def cpf(rng: random.Random) -> str:
    while True:
        base = "".join(str(rng.randrange(10)) for _ in range(9))
        if len(set(base)) > 1:
            return dv_cpf(base)


def cnpj(rng: random.Random) -> str:
    while True:
        base = "".join(str(rng.randrange(10)) for _ in range(8)) + "0001"
        if len(set(base)) > 1:
            return dv_cnpj(base)


def com_mascara_cpf(s: str) -> str:
    return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"


def com_mascara_cnpj(s: str) -> str:
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


def dv_errado(s: str) -> str:
    return s[:-1] + str((int(s[-1]) + 1) % 10)


def chave_privada_falsa() -> str:
    cab = "-" * 5 + "BEGIN " + "PRIVATE" + " KEY" + "-" * 5
    fim = "-" * 5 + "END " + "PRIVATE" + " KEY" + "-" * 5
    return f"{cab}\nAAAA\n{fim}\n"


def certificado_publico_falso() -> str:
    return "-" * 5 + "BEGIN CERTIFICATE" + "-" * 5 + "\nAAAA\n" + "-" * 5 + "END CERTIFICATE" + "-" * 5 + "\n"


class Repo:
    def __init__(self, raiz: Path):
        self.raiz = raiz
        raiz.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Teste")
        self.git("config", "user.email", "teste@example.com")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=self.raiz, capture_output=True, encoding="utf-8", errors="replace", check=check,
                              env=ISOLADO)

    def escreve(self, nome: str, conteudo: str | bytes) -> None:
        p = self.raiz / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(conteudo, bytes):
            p.write_bytes(conteudo)
        else:
            p.write_text(conteudo, encoding="utf-8")

    def commit(self, *nomes: str, extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
        self.git("add", "--", *nomes)
        return self.git("commit", "-q", "-m", "teste", *extra, check=False)

    def alarme(self, acao: str) -> subprocess.CompletedProcess:
        return subprocess.run([BASH, str(ALARME), acao], cwd=self.raiz, capture_output=True, encoding="utf-8", errors="replace",
                              env=ISOLADO)


class Base(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="hd-"))
        self.repo = Repo(self.tmp / "projeto")
        self.rng = random.Random(20261002)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestDeteccao(Base):
    def setUp(self) -> None:
        super().setUp()
        r = self.repo.alarme("instalar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def assertRecusa(self, r: subprocess.CompletedProcess, trecho: str = "") -> None:
        self.assertNotEqual(r.returncode, 0, "o commit deveria ter sido recusado")
        self.assertIn("commit recusado", r.stderr)
        if trecho:
            self.assertIn(trecho, r.stderr)

    def assertAceita(self, r: subprocess.CompletedProcess) -> None:
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_primeiro_commit_limpo_passa(self):
        self.repo.escreve("README.md", "projeto de teste\n")
        self.assertAceita(self.repo.commit("README.md"))

    def test_cpf_sem_mascara_bloqueia(self):
        self.repo.escreve("notas.txt", f"cliente {cpf(self.rng)} pagou\n")
        self.assertRecusa(self.repo.commit("notas.txt"), "CPF")

    def test_cpf_com_mascara_bloqueia(self):
        self.repo.escreve("notas.md", f"CPF: {com_mascara_cpf(cpf(self.rng))}.\n")
        self.assertRecusa(self.repo.commit("notas.md"), "notas.md:1: CPF")

    def test_cnpj_com_e_sem_mascara_bloqueia(self):
        c = cnpj(self.rng)
        self.repo.escreve("a.json", f'{{"cnpj": "{c}"}}\n')
        self.assertRecusa(self.repo.commit("a.json"), "CNPJ")
        self.repo.git("reset", "-q")
        self.repo.escreve("b.txt", f"fornecedor {com_mascara_cnpj(c)}\n")
        self.assertRecusa(self.repo.commit("b.txt"), "CNPJ")

    def test_valor_nao_aparece_inteiro_na_mensagem(self):
        c = cpf(self.rng)
        self.repo.escreve("n.txt", c + "\n")
        r = self.repo.commit("n.txt")
        self.assertRecusa(r)
        self.assertNotIn(c, r.stderr)
        self.assertNotIn(com_mascara_cpf(c), r.stderr)

    def test_digito_errado_nao_bloqueia(self):
        self.repo.escreve("n.txt", f"{dv_errado(cpf(self.rng))} e {com_mascara_cnpj(dv_errado(cnpj(self.rng)))}\n")
        self.assertAceita(self.repo.commit("n.txt"))

    def test_sequencia_repetida_nao_bloqueia(self):
        self.repo.escreve("n.txt", "1" * 11 + " " + "0" * 14 + " " + "000." + "000." + "000-" + "00\n")
        self.assertAceita(self.repo.commit("n.txt"))

    def test_numero_colado_em_letras_ou_longo_nao_bloqueia(self):
        c = cpf(self.rng)
        chave44 = "".join(str(self.rng.randrange(10)) for _ in range(44))
        self.repo.escreve("n.txt", f"id_{c} hash{c}abc {chave44}\n")
        self.assertAceita(self.repo.commit("n.txt"))

    def test_linha_removida_nao_conta(self):
        c = cpf(self.rng)
        self.repo.escreve("n.txt", f"{c}\n")
        self.repo.commit("n.txt", extra=("--no-verify",))
        self.repo.escreve("n.txt", "anonimizado\n")
        self.assertAceita(self.repo.commit("n.txt"))

    def test_env_bloqueia_e_example_passa(self):
        self.repo.escreve(".env.example", "SENHA=\n")
        self.assertAceita(self.repo.commit(".env.example"))
        self.repo.escreve("config/.env.production", "SENHA=x\n")
        self.assertRecusa(self.repo.commit("config/.env.production"), "arquivo de senhas")

    def test_pfx_e_p12_bloqueiam(self):
        self.repo.escreve("cert/empresa.PFX", b"\x30\x82\x00\x01")
        self.assertRecusa(self.repo.commit("cert/empresa.PFX"), "certificado digital")
        self.repo.git("reset", "-q")
        self.repo.escreve("b.p12", b"\x30\x82")
        self.assertRecusa(self.repo.commit("b.p12"), "certificado digital")

    def test_pem_publico_passa_privado_bloqueia(self):
        self.repo.escreve("ca.pem", certificado_publico_falso())
        self.assertAceita(self.repo.commit("ca.pem"))
        self.repo.escreve("chave.pem", chave_privada_falsa())
        self.assertRecusa(self.repo.commit("chave.pem"), "chave privada")

    def test_planilha_nova_de_qualquer_tamanho_bloqueia(self):
        for nome in ("p.xlsx", "p.xls", "p.ods", "p.csv"):
            self.repo.escreve(nome, b"x")
            self.assertRecusa(self.repo.commit(nome), "planilha nova")
            self.repo.git("reset", "-q")

    def test_csv_latin1_com_cpf_bloqueia(self):
        # CSV exportado do Excel no Windows: Latin-1, com acento antes do número.
        self.repo.escreve("clientes.txt", f"João;São Paulo;{cpf(self.rng)}\n".encode("latin-1"))
        self.assertRecusa(self.repo.commit("clientes.txt"), "clientes.txt:1: CPF")

    def test_planilha_ja_versionada_alterada_sem_cpf_passa(self):
        self.repo.escreve("tabela.csv", "a;b\n")
        self.repo.commit("tabela.csv", extra=("--no-verify",))
        self.repo.escreve("tabela.csv", "a;b\n1;2\n")
        self.assertAceita(self.repo.commit("tabela.csv"))

    def test_csv_alterado_com_cpf_bloqueia(self):
        self.repo.escreve("tabela.csv", "nome;doc\n")
        self.repo.commit("tabela.csv", extra=("--no-verify",))
        self.repo.escreve("tabela.csv", f"nome;doc\nFulano;{com_mascara_cpf(cpf(self.rng))}\n")
        self.assertRecusa(self.repo.commit("tabela.csv"), "tabela.csv:2: CPF")

    def test_mensagem_ensina_no_verify_e_desinstalar(self):
        self.repo.escreve(".env", "X=1\n")
        r = self.repo.commit(".env")
        self.assertRecusa(r)
        self.assertIn("git commit --no-verify", r.stderr)
        self.assertIn("Para desinstalar o alarme: rm", r.stderr)
        self.assertIn("git restore --staged", r.stderr)

    def test_no_verify_grava(self):
        self.repo.escreve(".env", "X=1\n")
        self.assertAceita(self.repo.commit(".env", extra=("--no-verify",)))

    def test_vale_para_frente_worktree(self):
        self.repo.escreve("README.md", "x\n")
        self.repo.commit("README.md")
        frente = self.tmp / "frente"
        self.repo.git("worktree", "add", "-q", "-b", "frente", str(frente))
        (frente / ".env").write_text("X=1\n", encoding="utf-8")
        subprocess.run(["git", "add", ".env"], cwd=frente, check=True, env=ISOLADO)
        r = subprocess.run(["git", "commit", "-q", "-m", "t"], cwd=frente, capture_output=True, encoding="utf-8", errors="replace",
                           env=ISOLADO)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("arquivo de senhas", r.stderr)


class TestInstalacao(Base):
    def hook(self) -> Path:
        return self.repo.raiz / ".git" / "hooks" / "pre-commit"

    def test_verificar_so_le(self):
        antes = sorted(p.name for p in (self.repo.raiz / ".git" / "hooks").iterdir())
        r = self.repo.alarme("verificar")
        self.assertEqual(r.returncode, 0)
        self.assertIn("nenhum alarme", r.stdout)
        depois = sorted(p.name for p in (self.repo.raiz / ".git" / "hooks").iterdir())
        self.assertEqual(antes, depois)
        self.assertFalse(self.hook().exists())

    def test_instalar_grava_marca_e_versao(self):
        r = self.repo.alarme("instalar")
        self.assertEqual(r.returncode, 0, r.stdout)
        texto = self.hook().read_text(encoding="utf-8")
        self.assertIn("# sdd-higiene-dado: alarme de commit (pre-commit)", texto)
        self.assertRegex(texto, r"# versão: \d+\.\d+\.\d+")
        self.assertTrue(os.access(self.hook(), os.X_OK))
        self.assertIn("desinstalar", r.stdout)

    def test_reinstalar_atualiza(self):
        self.repo.alarme("instalar")
        r = self.repo.alarme("instalar")
        self.assertEqual(r.returncode, 0)

    def test_hook_alheio_nao_e_tocado(self):
        alheio = "#!/bin/sh\necho alheio\n"
        self.hook().write_text(alheio, encoding="utf-8")
        for acao in ("verificar", "instalar", "desinstalar"):
            r = self.repo.alarme(acao)
            self.assertEqual(r.returncode, 2, acao)
            self.assertEqual(self.hook().read_text(encoding="utf-8"), alheio)
        self.assertIn("à mão", self.repo.alarme("instalar").stdout)

    def test_core_hooks_path_recusa(self):
        self.repo.git("config", "core.hooksPath", ".husky/_")
        r = self.repo.alarme("instalar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("core.hooksPath", r.stdout)
        self.assertFalse(self.hook().exists())
        self.assertFalse((self.repo.raiz / ".husky").exists())

    def test_desinstalar_remove_so_o_nosso(self):
        self.repo.alarme("instalar")
        r = self.repo.alarme("desinstalar")
        self.assertEqual(r.returncode, 0)
        self.assertFalse(self.hook().exists())
        r = self.repo.alarme("desinstalar")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Nada foi alterado", r.stdout)

    def test_fora_de_repositorio(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        r = subprocess.run([BASH, str(ALARME), "verificar"], cwd=fora, capture_output=True, encoding="utf-8", errors="replace",
                           env=ISOLADO)
        self.assertEqual(r.returncode, 1)
        self.assertIn("não é um repositório git", r.stdout)


class TestCopiaGerada(Base):
    """sdd-open: o sync copia a skill para .claude/skills com 2 linhas sdd-open:generated depois do shebang, e o
    init liga os hooks do projeto (core.hooksPath = sdd/hooks). A cópia gerada tem de reconhecer o dispatcher
    e ligar o alarme nele, sem gravar nada em .git/hooks/ — e, sem o dispatcher, instalar da fonte ou da cópia
    produz o mesmo arquivo."""

    def init_sdd_open(self, projeto: Path) -> None:
        vazio = self.tmp / "gitconfig-vazio"
        vazio.write_text("", encoding="utf-8")
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(vazio), "GIT_CONFIG_NOSYSTEM": "1",
               "GIT_CEILING_DIRECTORIES": str(self.tmp), "GIT_TERMINAL_PROMPT": "0"}
        r = subprocess.run([BASH, str(RAIZ / "bin" / "sdd-open.sh"), "init", "--yes", "--vendors", "claude"],
                           cwd=projeto, env=env, capture_output=True, encoding="utf-8", errors="replace",
                           stdin=subprocess.DEVNULL, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def copia_alarme(self, acao: str) -> subprocess.CompletedProcess:
        copia = self.repo.raiz / ".claude" / "skills" / "sdd-higiene-dado" / "scripts"
        return subprocess.run([BASH, str(copia / "alarme.sh"), acao], cwd=self.repo.raiz,
                              capture_output=True, encoding="utf-8", errors="replace", env=ISOLADO)

    def test_copia_gerada_liga_o_alarme_nos_hooks_do_projeto(self):
        self.init_sdd_open(self.repo.raiz)
        copia = self.repo.raiz / ".claude" / "skills" / "sdd-higiene-dado" / "scripts"
        self.assertIn("sdd-open:generated", (copia / "pre-commit.sh").read_text(encoding="utf-8"),
                      "pré-condição: a cópia gerada deveria ter o cabeçalho do sync")
        self.assertEqual(self.repo.git("config", "--get", "core.hooksPath").stdout.strip(), "sdd/hooks",
                         "pré-condição: o init liga os hooks do projeto")
        r = self.copia_alarme("verificar")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("hooks do sdd-open (sdd/hooks)", r.stdout)
        self.assertIn("desligado", r.stdout)
        r = self.copia_alarme("instalar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("ligado nos hooks do projeto", r.stdout)
        self.assertEqual(self.repo.git("config", "--get", "sdd.higieneDado").stdout.strip(), "on")
        self.assertFalse((self.repo.raiz / ".git" / "hooks" / "pre-commit").exists(), "nada é gravado em .git/hooks/")
        r = self.copia_alarme("verificar")
        self.assertIn("ligado pelos hooks do projeto (sdd/hooks)", r.stdout)
        # a cópia gerada e a fonte ligam o mesmo alarme: um .env staged é recusado pelo dispatcher
        self.repo.escreve(".env", "X=1\n")
        r = self.repo.commit(".env")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("arquivo de senhas", r.stderr)

    def test_sem_dispatcher_a_copia_gerada_grava_o_mesmo_arquivo_da_fonte(self):
        self.init_sdd_open(self.repo.raiz)
        self.repo.git("config", "--unset", "core.hooksPath")
        copia = self.repo.raiz / ".claude" / "skills" / "sdd-higiene-dado" / "scripts"
        r = self.copia_alarme("instalar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        hook = (self.repo.raiz / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertNotIn("sdd-open:generated", hook)
        fonte = Repo(self.tmp / "fonte")
        self.assertEqual(fonte.alarme("instalar").returncode, 0)
        self.assertEqual(hook, (fonte.raiz / ".git" / "hooks" / "pre-commit").read_text(encoding="utf-8"))
        self.assertIn("o alarme desta skill já está instalado", self.copia_alarme("verificar").stdout)


class TestModoHooks(Base):
    """F8: com core.hooksPath = sdd/hooks e o dispatcher do sdd-open presente, o alarme é ligado/desligado por
    `git config sdd.higieneDado`; qualquer outro hooksPath continua recusado; o desinstalar nunca toca o dispatcher."""

    MARCA_DISPATCHER = "# sdd-open: dispatcher de hooks (pre-commit)"

    def setUp(self) -> None:
        super().setUp()
        hooks = self.repo.raiz / "sdd" / "hooks"
        hooks.mkdir(parents=True)
        for nome in ("pre-commit", "pre-push"):
            shutil.copy2(str(RAIZ / "sdd" / "hooks" / nome), str(hooks / nome))
        (self.repo.raiz / "sdd" / "bin").mkdir()
        # o dispatcher chama a skill instalada no projeto (.agents/skills/…), como depois de um init
        scripts = self.repo.raiz / ".agents" / "skills" / "sdd-higiene-dado" / "scripts"
        scripts.mkdir(parents=True)
        shutil.copy2(str(HOOK_ORIGEM), str(scripts / "pre-commit.sh"))
        shutil.copy2(str(ALARME), str(scripts / "alarme.sh"))
        self.repo.git("config", "core.hooksPath", "sdd/hooks")

    def config(self) -> str:
        return self.repo.git("config", "--get", "sdd.higieneDado", check=False).stdout.strip()

    def test_verificar_instalar_desinstalar_pela_config(self):
        r = self.repo.alarme("verificar")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("hooks do sdd-open (sdd/hooks)", r.stdout)
        self.assertIn("Dá para ligar", r.stdout)
        r = self.repo.alarme("instalar")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.config(), "on")
        self.assertFalse((self.repo.raiz / ".git" / "hooks" / "pre-commit").exists())
        self.assertIn("nada foi gravado em .git/", r.stdout)
        self.assertIn("desinstalar", r.stdout)
        r = self.repo.alarme("verificar")
        self.assertIn("ligado pelos hooks do projeto", r.stdout)
        r = self.repo.alarme("desinstalar")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(self.config(), "")
        self.assertTrue((self.repo.raiz / "sdd" / "hooks" / "pre-commit").is_file(), "o dispatcher nunca é tocado")
        self.assertIn("Os hooks do sdd-open continuam no lugar", r.stdout)
        r = self.repo.alarme("desinstalar")
        self.assertEqual(r.returncode, 0)
        self.assertIn("Nada foi alterado", r.stdout)

    def test_desinstalar_remove_o_arquivo_legado_da_migracao_e_so_ele(self):
        legado = self.repo.raiz / ".git" / "hooks" / "pre-commit"
        legado.parent.mkdir(parents=True, exist_ok=True)
        legado.write_text("#!/usr/bin/env bash\n# sdd-higiene-dado: alarme de commit (pre-commit)\n# versão: 1.1.1\nexit 0\n",
                          encoding="utf-8")
        self.repo.git("config", "sdd.higieneDado", "on")
        r = self.repo.alarme("desinstalar")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertFalse(legado.exists())
        self.assertTrue((self.repo.raiz / "sdd" / "hooks" / "pre-commit").is_file())
        self.assertIn(self.MARCA_DISPATCHER, (self.repo.raiz / "sdd" / "hooks" / "pre-commit").read_text(encoding="utf-8"))

    def test_hooks_path_absoluto_por_link_simbolico_e_modo_hooks(self):
        link = self.tmp / "link"
        os.symlink(self.repo.raiz, link)
        self.repo.git("config", "core.hooksPath", str(link / "sdd" / "hooks"))
        r = self.repo.alarme("verificar")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("hooks do sdd-open (sdd/hooks)", r.stdout)

    def test_hooks_path_sem_o_dispatcher_e_outro(self):
        (self.repo.raiz / "sdd" / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        for acao in ("verificar", "instalar", "desinstalar"):
            r = self.repo.alarme(acao)
            self.assertEqual(r.returncode, 2, acao)
            self.assertIn("core.hooksPath", r.stdout)
        self.assertEqual(self.config(), "")

    def test_recusa_pelo_dispatcher_ensina_desinstalar_sem_rm(self):
        self.repo.git("config", "sdd.higieneDado", "on")
        self.repo.escreve(".env", "X=1\n")
        r = self.repo.commit(".env")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("arquivo de senhas", r.stderr)
        self.assertIn("alarme.sh desinstalar", r.stderr)
        self.assertNotIn("rm ", r.stderr)


class TestGeradores(unittest.TestCase):
    """Controle positivo dos geradores: casos com DV conhecidos publicamente por fórmula."""

    def test_dv_cpf(self):
        self.assertEqual(dv_cpf("111444777")[-2:], "35")

    def test_dv_cnpj(self):
        self.assertEqual(dv_cnpj("11222333" + "0001")[-2:], "81")


if __name__ == "__main__":
    unittest.main()
