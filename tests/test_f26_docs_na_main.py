"""F26, bloco dos documentos (AT-001 a AT-007, AT-011, AT-012): os documentos das frentes vivem na main e nunca chegam
ao pacote (trava 1: export-ignore; trava 2: o CI confere o pacote montado), a varredura própria deles, a migração da
branch de documentos por lista, o anexo do bruto e a prova de remoção a pedido.

Tudo roda em repositórios temporários montados aqui (o Verify Gate roda a suíte numa cópia sem .git). Número longo,
caminho de pasta pessoal, e-mail e chave de teste são montados em tempo de execução: este arquivo vai no pacote e o
G2 do publish-gate o confere (LM-012, LM-020)."""
from __future__ import annotations

import io
import os
import random
import re
import shutil
import string
import subprocess
import sys
import tarfile
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, SEM_NOME_ESPECIAL, Sandbox, path_restrito

PY = sys.executable
GITLEAKS = shutil.which("gitleaks")
SEM_GITLEAKS = (GITLEAKS is None, "gitleaks ausente: a varredura e o publish-gate exigem")
PASTAS_DOC = ("sdd/features", "sdd/handoffs", "sdd/reviews", "sdd/releases", "sdd/archive", "sdd/curadoria",
              "sdd/reports")
MANIFEST = [ln for ln in (RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").split("\n") if ln]

NUM_LONGO = "1234567" + "8901"                     # 11 dígitos, sem dígito verificador de CPF válido
PASTA_PESSOAL = "/" + "Users" + "/fulano/projeto"
ARROBA = "@"


def cpf(base9: str) -> str:
    d = [int(x) for x in base9]
    for n in (9, 10):
        s = sum(d[i] * (n + 1 - i) for i in range(n))
        d.append((s * 10) % 11 % 10)
    return "".join(str(x) for x in d)


def cnpj(base12: str) -> str:
    d = [int(x) for x in base12]
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    for pesos in (p1, [6] + p1):
        r = sum(d[i] * pesos[i] for i in range(len(pesos))) % 11
        d.append(0 if r < 2 else 11 - r)
    return "".join(str(x) for x in d)


def chave_github() -> str:
    return "gh" + "p_" + "".join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(36))


def cabecalho_chave() -> str:
    return "-----BEGIN " + "RSA PRIVATE KEY-----"


class Base(Sandbox):
    def roda_longo(self, args, cwd, env=None, teto=900):
        r = subprocess.run([str(a) for a in args], cwd=str(cwd), env=env or self.env, capture_output=True,
                           encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=teto)
        return r.returncode, r.stdout, r.stderr

    def pacote(self, nome="open") -> Path:
        """Repositório com os arquivos do pacote (o MANIFEST.txt), como a main sem documentos."""
        r = self.repo(nome)
        for rel in MANIFEST:
            origem = RAIZ / rel
            alvo = r / rel
            alvo.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(origem), str(alvo))
        self.commit(r, "pacote")
        return r

    def com_varredura(self, nome="repo") -> Path:
        """Repositório com a trava 1 e a varredura dos documentos (o que ela precisa para rodar)."""
        r = self.repo(nome)
        for rel in (".gitattributes", ".gitignore", "sdd/bin/docs-varredura.sh", "sdd/bin/docs-varredura.py",
                    "sdd/bin/lib"):
            self.copia(rel, r)
        self.commit(r, "base")
        return r

    def documentos_de_teste(self, r: Path) -> None:
        texto = "# Documento\n\nNúmero de run %s, pasta %s, contato fulano%sexample.com.\n" % (
            NUM_LONGO, PASTA_PESSOAL, ARROBA)
        for p in PASTAS_DOC:
            self.escreve(r, p + "/DOC_TESTE.md", texto)
        self.escreve(r, "sdd/reports/evidence/F_TESTE/quebrado.sh", "if then fi (\n")
        self.escreve(r, "sdd/GOVERNANCA_PADRAO.md", "uso: só eu\n")
        self.escreve(r, "sdd/estudos/nota.md", "pasta de documento nova\n")


# ── AT-001 a AT-003: as travas ───────────────────────────────────────────────────────────────────────────────────

class Travas(Base):
    def setUp(self):
        super().setUp()
        self.r = self.pacote()
        self.documentos_de_teste(self.r)
        self.commit(self.r, "documentos")

    def arquivos_do_tarball(self, r: Path) -> set:
        alvo = self.tmp / "pacote.tar.gz"
        self.git(r, "archive", "--format=tar.gz", "--prefix=sdd-open-v9.9.9/", "-o", str(alvo), "HEAD")
        with tarfile.open(str(alvo)) as t:
            return {m.name[len("sdd-open-v9.9.9/"):] for m in t.getmembers() if m.isfile()}

    def test_at001_tarball_como_o_release_sem_documento_e_manifest_nos_2_sentidos(self):
        arquivos = self.arquivos_do_tarball(self.r)
        docs = sorted(a for a in arquivos if a.startswith(PASTAS_DOC + ("sdd/estudos",)) or a == "sdd/GOVERNANCA_PADRAO.md")
        self.assertEqual(docs, [])
        self.assertEqual(arquivos, set(MANIFEST))

    def test_at001_extrair_tag_do_gerador_sem_documento_e_baseline_sem_a_trava(self):
        prog = ("import importlib.util, sys; from pathlib import Path\n"
                "spec = importlib.util.spec_from_file_location('g', sys.argv[1]); g = importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(g); g.extrair_tag(sys.argv[2], Path(sys.argv[3]))\n")

        def extrair(destino: Path) -> list:
            self.git(self.r, "tag", "-f", "v9.9.9")
            rc, out, err = self.roda([PY, "-B", "-c", prog, self.r / "scripts/gerar-starter.py", "v9.9.9", destino], self.r)
            self.assertEqual(rc, 0, out + err)
            return sorted(p.relative_to(destino).as_posix() for p in destino.rglob("*")
                          if p.is_file() and p.relative_to(destino).as_posix().startswith(PASTAS_DOC + ("sdd/estudos",)))

        self.assertEqual(extrair(self.tmp / "extraido1"), [])
        ga = self.r / ".gitattributes"
        ga.write_text(ga.read_text(encoding="utf-8").replace("sdd/** export-ignore\n", ""), encoding="utf-8")
        self.commit(self.r, "sem a trava")
        self.assertGreater(len(extrair(self.tmp / "extraido2")), 0)   # o baseline: sem a trava, os documentos vêm

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at002_at003_publish_gate_sobre_o_pacote_verde_e_os_3_defeitos_vermelhos(self):
        env = dict(self.env, PUBLISH_GATE_MODE="ci")
        rc, out, err = self.roda_longo([BASH, "scripts/montar-pacote.sh"], self.r)
        self.assertEqual(rc, 0, out + err)
        pacote = out.strip()
        rc, out, err = self.roda_longo([BASH, "scripts/publish-gate.sh", pacote], self.r, env)
        self.assertEqual(rc, 0, out + err)                       # AT-003: documentos no checkout não derrubam o gate
        ga = self.r / ".gitattributes"
        ga.write_text(ga.read_text(encoding="utf-8").replace("sdd/bin -export-ignore\n", ""), encoding="utf-8")
        self.escreve(self.r, "sdd/templates/NOTAS_SOLTAS.md", "documento numa pasta do pacote\n")
        leia = self.r / "README.md"
        leia.write_text(leia.read_text(encoding="utf-8") + "\nrun %s\n" % NUM_LONGO, encoding="utf-8")
        self.commit(self.r, "3 defeitos")
        rc, out, err = self.roda_longo([BASH, "scripts/montar-pacote.sh"], self.r)
        self.assertEqual(rc, 0, out + err)
        rc, out, err = self.roda_longo([BASH, "scripts/publish-gate.sh", out.strip()], self.r, env)
        self.assertNotEqual(rc, 0, out + err)
        self.assertIn("declared but missing: sdd/bin/", out + err)                 # a linha da pasta que faltou
        self.assertIn("undeclared file: sdd/templates/NOTAS_SOLTAS.md", out + err)  # o documento que escapou
        self.assertIn("[0-9]{11,}", out + err)                                     # o G2 não foi afrouxado

    def test_at002_workflows_so_leem_o_pacote(self):
        for nome, n_gate, n_shell in (("publish-gate.yml", 2, 1), ("release.yml", 2, 1)):
            texto = (RAIZ / ".github/workflows" / nome).read_text(encoding="utf-8")
            passos = re.split(r"\n      - (?=name:|uses:)", texto)
            gate = [p for p in passos if "publish-gate.sh" in p]
            shell = [p for p in passos if "find . -name '*.sh'" in p]
            with self.subTest(workflow=nome):
                self.assertEqual((len(gate), len(shell)), (n_gate, n_shell))
                for p in gate + shell:
                    self.assertIn("montar-pacote.sh", p)
                    self.assertNotIn('"$GITHUB_WORKSPACE"', p)
                    self.assertNotIn('"$(pwd)"', p)
                for p in gate:
                    self.assertIn('P="$(bash scripts/montar-pacote.sh)" || exit 1', p)
        pg = (RAIZ / ".github/workflows/publish-gate.yml").read_text(encoding="utf-8")
        self.assertIn("run: bash sdd/bin/docs-varredura.sh .", pg)

    def test_at003_o_passo_de_shell_executado_como_esta_no_workflow(self):
        texto = (RAIZ / ".github/workflows/publish-gate.yml").read_text(encoding="utf-8")
        passo = [p for p in re.split(r"\n      - (?=name:|uses:)", texto) if "find . -name '*.sh'" in p][0]
        corpo = passo.split("run: |\n", 1)[1]
        run = "\n".join(ln[10:] for ln in corpo.split("\n") if ln.startswith("          ") or not ln.strip())
        rc, out, err = self.roda_longo([BASH, "-c", run], self.r)
        self.assertEqual(rc, 0, out + err)                  # o .sh quebrado da evidência não está no pacote
        self.escreve(self.r, "scripts/quebrado.sh", "if then fi (\n")
        self.commit(self.r, "script quebrado no pacote")
        rc, out, err = self.roda_longo([BASH, "-c", run], self.r)
        self.assertNotEqual(rc, 0, out + err)
        self.assertIn("quebrado.sh", out + err)


# ── AT-004 e AT-012: a varredura dos documentos ─────────────────────────────────────────────────────────────────

class Varredura(Base):
    def setUp(self):
        super().setUp()
        self.r = self.com_varredura()

    def varrer(self, *args, env=None):
        return self.roda_longo([BASH, "sdd/bin/docs-varredura.sh", *args], self.r, env)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_cada_regra_reprova_e_o_vizinho_passa(self):
        valido, invalido = cpf("123456789"), cpf("123456789")[:9] + "00"
        casos = [
            ("CPF válido", "sdd/features/A.md", "run %s\n" % valido, 1, "CPF com dígito verificador válido"),
            ("CPF pontuado", "sdd/features/A.md", "doc %s.%s.%s-%s\n" % (valido[:3], valido[3:6], valido[6:9], valido[9:]),
             1, "CPF"),
            ("CPF de dígito errado", "sdd/features/A.md", "run %s\n" % invalido, 0, ""),
            ("CPF colado a letras (avaliador, A6)", "sdd/features/A.md", "CPF%sx\n" % valido, 1, "CPF"),
            ("compactado (avaliador, A5)", "sdd/reports/evidence/F/sessao.log.gz", "\x1f\x8b qualquer", 1, "compactado"),
            ("CNPJ válido", "sdd/features/A.md", "empresa %s\n" % cnpj("11222333" + "0001"), 1, "CNPJ"),
            ("e-mail real", "sdd/handoffs/H.md", "fulano%sempresa-real.com.br\n" % ARROBA, 1, "e-mail"),
            ("exemplo.com.br não é exemplo", "sdd/handoffs/H.md", "fulano%sexemplo.com.br\n" % ARROBA, 1, "e-mail"),
            ("e-mails de exemplo", "sdd/handoffs/H.md", "a%sexample.com b%sexemplo.com git%sgithub.com c%sx.invalid\n"
             % (ARROBA, ARROBA, ARROBA, ARROBA), 0, ""),
            ("chave privada", "sdd/reviews/R.md", cabecalho_chave() + "\n", 1, "PRIVATE KEY"),
            ("certificado sem chave", "sdd/reviews/R.pem", "-----BEGIN CERTIFICATE-----\n", 0, ""),
            ("segredo", "sdd/reports/S.md", "token = %s\n" % chave_github(), 1, "gitleaks"),
            ("número longo e pasta pessoal", "sdd/reports/N.md", "%s %s\n" % (NUM_LONGO, PASTA_PESSOAL), 0, ""),
            ("evidência no teto", "sdd/reports/evidence/F/a.log", "x" * 262144, 0, ""),
            ("evidência acima do teto", "sdd/reports/evidence/F/a.log", "x" * 262145, 1, "acima de 262144"),
        ]
        for nome, rel, conteudo, esperado, regra in casos:
            with self.subTest(caso=nome):
                p = self.escreve(self.r, rel, conteudo)
                rc, out, err = self.varrer(".")
                p.unlink()
                self.assertEqual(rc, esperado, out + err)
                self.assertIn(regra, out)
                if esperado:
                    self.assertIn(rel, out)                  # caminho e regra; nunca o trecho
        pfx = self.r / "sdd/archive/certificado.pfx"
        pfx.parent.mkdir(parents=True, exist_ok=True)
        pfx.write_bytes(b"\x30\x82\x00\x10binario")
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("certificado (.pfx/.p12)", out)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_aceite_so_com_motivo_e_so_na_linha_e_na_de_baixo(self):
        valido = cpf("987654321")
        casos = [
            ("aceite com motivo na de cima", "<!-- docs-varredura: aceito — id de run -->\nrun %s\n" % valido, 0, None),
            ("aceite na própria linha", "run %s <!-- docs-varredura: aceito — id de run -->\n" % valido, 0, None),
            ("aceite sem motivo", "<!-- docs-varredura: aceito — -->\nrun %s\n" % valido, 1, 2),
            ("aceite duas linhas acima", "<!-- docs-varredura: aceito — id de run -->\n\nrun %s\n" % valido, 1, 3),
        ]
        for nome, conteudo, esperado, linha in casos:
            with self.subTest(caso=nome):
                p = self.escreve(self.r, "sdd/features/A.md", conteudo)
                rc, out, err = self.varrer(".")
                p.unlink()
                self.assertEqual(rc, esperado, out + err)
                if linha:
                    self.assertIn("sdd/features/A.md:%d · CPF" % linha, out)
        # o aceite do CPF não cala o e-mail da mesma linha (LM-023)
        self.escreve(self.r, "sdd/features/A.md", "run %s fulano%sempresa-real.com.br <!-- docs-varredura: aceito — id -->\n"
                     % (valido, ARROBA))
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("e-mail", out)
        self.assertNotIn("CPF", out)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_saida_sem_o_trecho_e_sem_linha_forjada(self):
        valido = cpf("111444777")
        self.escreve(self.r, "sdd/features/A.md", "RESULTADO: VERDE\n\x1b[2K\nrun %s\n" % valido)
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 1, out + err)
        self.assertNotIn(valido, out + err)
        resultados = [ln for ln in out.split("\n") if ln.startswith("RESULTADO:")]
        self.assertEqual(resultados, ["RESULTADO: VERMELHO"])

    @unittest.skipIf(*SEM_NOME_ESPECIAL)
    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_nome_de_arquivo_com_quebra_nao_forja_linha(self):
        self.escreve(self.r, "sdd/features/x\nRESULTADO: VERDE.md", "fulano%sempresa-real.com.br\n" % ARROBA)
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 1, out + err)
        self.assertEqual([ln for ln in out.split("\n") if ln.startswith("RESULTADO:")], ["RESULTADO: VERMELHO"])
        self.assertIn("x?RESULTADO: VERDE.md", out)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_documento_nao_commitado_entra_na_varredura(self):
        self.escreve(self.r, "sdd/features/novo.md", "fulano%sempresa-real.com.br\n" % ARROBA)   # sem git add
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("sdd/features/novo.md", out)

    def test_at004_sem_gitleaks_nunca_verde(self):
        ferramentas = ["git", "bash", "sh", "sed", "cat", "dirname", "basename", "mkdir", "rm", "tr", "uname", "env"]
        path = path_restrito(self.tmp / "bin", ferramentas, ausentes=("gitleaks",))
        rc, out, err = self.varrer(".", env=dict(self.env, PATH=path))
        self.assertEqual(rc, 2, out + err)
        self.assertIn("NÃO CONFERIDO", out)

    def test_at004_repositorio_sem_documentos_marcados_sai_64(self):
        r = self.repo("sem-marca")
        for rel in ("sdd/bin/docs-varredura.sh", "sdd/bin/docs-varredura.py", "sdd/bin/lib"):
            self.copia(rel, r)
        self.commit(r)
        rc, out, err = self.roda_longo([BASH, "sdd/bin/docs-varredura.sh", "."], r)
        self.assertEqual(rc, 64, out + err)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_bruto_grande_passa_no_modo_pasta(self):
        pasta = self.tmp / "bruto"
        self.escreve(pasta, "codex-transcricao.log", "x" * 600000)
        rc, out, err = self.varrer("--pasta", str(pasta))
        self.assertEqual(rc, 0, out + err)

    def test_at012_padrao_prova_a_remocao_na_ref_inteira_e_na_pasta(self):
        dado = "Fulano" + " de Tal " + "Sobrenome"
        self.escreve(self.r, "bin/codigo.sh", "# autor: %s\n" % dado)        # fora das pastas de documento
        self.commit(self.r, "com o dado")
        self.git(self.r, "tag", "antes")
        rc, out, err = self.varrer("--ref", "antes", "--padrao", "Fulano de Tal")
        self.assertEqual(rc, 1, out + err)
        self.assertIn("bin/codigo.sh:1 · padrão pedido", out)
        self.assertNotIn(dado, out)
        self.escreve(self.r, "bin/codigo.sh", "# autor: removido a pedido\n")
        self.commit(self.r, "sem o dado")
        self.git(self.r, "tag", "depois")
        rc, out, err = self.varrer("--ref", "depois", "--padrao", "Fulano de Tal")
        self.assertEqual(rc, 0, out + err)
        rc, out, err = self.varrer(".", "--padrao", "Fulano de Tal")
        self.assertEqual(rc, 0, out + err)
        anexo = self.tmp / "anexo"
        self.escreve(anexo, "log/sessao.log", "falou %s\n" % dado)
        rc, out, err = self.varrer("--pasta", str(anexo), "--padrao", "Fulano de Tal")
        self.assertEqual(rc, 1, out + err)

    def test_at012_texto_procura_o_dado_letra_a_letra(self):
        # revisão do código, R1: o dado pedido como veio ("+", "." e parênteses) não pode virar regex e passar calado
        dado = "fulano" + "+teste(1)"
        self.escreve(self.r, "bin/codigo.sh", "# contato: %s\n" % dado)
        self.commit(self.r, "com o dado")
        rc, out, err = self.varrer(".", "--padrao", dado)
        self.assertEqual(rc, 0, out + err)                  # a regex não acha o texto: o motivo do --texto
        rc, out, err = self.varrer(".", "--texto", dado)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("bin/codigo.sh:1 · padrão pedido", out)
        self.assertNotIn(dado, out)
        self.escreve(self.r, "bin/codigo.sh", "# contato: removido a pedido\n")
        self.commit(self.r, "sem o dado")
        rc, out, err = self.varrer(".", "--texto", dado)
        self.assertEqual(rc, 0, out + err)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at004_log_em_utf16_e_varrido(self):
        # revisão do código, N2: o PowerShell 5 grava log em UTF-16; os NUL entre as letras não fazem dele binário
        linha = "run %s fulano%sempresa-real.com.br\r\n" % (cpf("123456789"), ARROBA)
        for nome, dados in (("com BOM", "\ufeff".encode("utf-16-le") + linha.encode("utf-16-le")),
                            ("sem BOM", linha.encode("utf-16-le")),
                            ("big-endian com BOM", b"\xfe\xff" + linha.encode("utf-16-be"))):
            with self.subTest(caso=nome):
                p = self.r / "sdd/reports/evidence/F/powershell.log"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(dados)
                rc, out, err = self.varrer(".")
                p.unlink()
                self.assertEqual(rc, 1, out + err)
                self.assertIn("CPF", out)
                self.assertIn("e-mail", out)
        p = self.r / "sdd/archive/imagem.bin"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(bytes(range(256)) * 4)              # binário de verdade continua sem as regras de texto
        rc, out, err = self.varrer(".")
        self.assertEqual(rc, 0, out + err)

    def test_at012_texto_com_ref_olha_o_historico_da_tag(self):
        # avaliador, A4: a tag regravada num commit filho ainda guarda o dado no histórico; a prova tem de ver
        dado = "Fulano" + " de Tal " + "Sobrenome"
        self.escreve(self.r, "sdd/features/NOTA.md", "autor: %s\n" % dado)
        self.escreve(self.r, "sdd/features/OUTRA.md", "fica\n")
        self.commit(self.r, "com o dado")
        (self.r / "sdd/features/NOTA.md").unlink()
        self.commit(self.r, "sem o arquivo, por cima")
        self.git(self.r, "tag", "arquivo/filho")
        rc, out, err = self.varrer("--ref", "arquivo/filho", "--texto", dado)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("histórico de arquivo/filho", out)
        self.assertNotIn(dado, out)
        arvore = self.git(self.r, "rev-parse", "HEAD^{tree}").strip()          # o histórico reescrito: sem o commit antigo
        orfao = self.git(self.r, "commit-tree", arvore, "-m", "arquivo sem o dado").strip()
        self.git(self.r, "tag", "arquivo/reescrita", orfao)
        rc, out, err = self.varrer("--ref", "arquivo/reescrita", "--texto", dado)
        self.assertEqual(rc, 0, out + err)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at011_bruto_compactado_nada_enviado_pela_varredura(self):
        # avaliador, A5: compactado não é lido por dentro; na pasta do bruto, reprova (e o anexo não sai)
        pasta = self.tmp / "bruto"
        pasta.mkdir()
        interno = io.BytesIO()
        with tarfile.open(fileobj=interno, mode="w:gz") as tf:
            corpo = ("contato fulano%sempresa-real.com.br\n" % ARROBA).encode("utf-8")
            info = tarfile.TarInfo("n.txt")
            info.size = len(corpo)
            tf.addfile(info, io.BytesIO(corpo))
        (pasta / "pacote.tar.gz").write_bytes(interno.getvalue())
        (pasta / "sem-extensao").write_bytes(interno.getvalue())
        rc, out, err = self.varrer("--pasta", str(pasta))
        self.assertEqual(rc, 1, out + err)
        self.assertIn("pacote.tar.gz · arquivo compactado", out)
        self.assertIn("sem-extensao · arquivo compactado", out)

    def test_at012_contributing_tem_o_procedimento(self):
        texto = (RAIZ / "CONTRIBUTING.md").read_text(encoding="utf-8")
        sec = texto.split("## Personal data removal requests (Pedido de remoção de dado pessoal)", 1)
        self.assertEqual(len(sec), 2)
        corpo = sec[1].split("\n## ", 1)[0]
        for termo in ("**30 days**", "A `main`", "arquivo/docs-incorporar-starter", "evidencia-bruta-<F>.tar.gz",
                      "--clobber", "--ref arquivo/docs-incorporar-starter --texto", "--pasta <anexo extraído> --texto",
                      "Report a", "histórico da `main` ainda guarda", "git filter-repo", "Um commit novo por cima não basta"):
            with self.subTest(termo=termo):
                self.assertIn(termo, corpo)


# ── AT-005 e AT-006: a migração ─────────────────────────────────────────────────────────────────────────────────

@unittest.skipIf(*SEM_GITLEAKS)
class Migracao(Base):
    TAG = "arquivo/docs-teste"

    def setUp(self):
        super().setUp()
        self.origin = self.tmp / "origin.git"
        self.git(self.tmp, "init", "-q", "--bare", str(self.origin))
        self.r = self.com_varredura("main")
        self.copia("scripts/docs-migracao.py", self.r)
        self.escreve(self.r, "bin/codigo.sh", "echo main\n")
        self.commit(self.r, "main")
        self.git(self.r, "branch", "-M", "main")
        self.git(self.r, "remote", "add", "origin", str(self.origin))
        self.git(self.r, "push", "-q", "origin", "main")
        self.git(self.r, "checkout", "-q", "-b", "docs/incorporar-starter")
        self.escreve(self.r, "bin/codigo.sh", "echo código velho da branch de documentos\n")
        self.escreve(self.r, "sdd/features/DEFINE_A.md", "# DEFINE A\n")
        self.escreve(self.r, "sdd/reports/evidence/F/AT-001.log", "$ true\n[exit=0]\n")
        self.escreve(self.r, "sdd/reports/evidence/F/codex-sessao.log", "transcrição\n")
        self.escreve(self.r, "sdd/reports/evidence/F/grande.log", "x" * 300000)
        self.escreve(self.r, "sdd/reports/evidence/F/sonda.log", cabecalho_chave() + "\n")
        self.escreve(self.r, "sdd/handoffs/HANDOFF_A.md", "# Ficha\n\nruns %s\n" % cpf("222333444"))
        self.commit(self.r, "documentos")
        self.git(self.r, "push", "-q", "origin", "docs/incorporar-starter")
        self.git(self.r, "tag", self.TAG)
        self.git(self.r, "checkout", "-q", "main")

    def migracao(self, *args):
        return self.roda_longo([PY, "-B", "scripts/docs-migracao.py", *args], self.r)

    def migrar(self):
        rc, out, err = self.migracao("--copiar", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.git(self.r, "add", "sdd")
        self.git(self.r, "commit", "-q", "-m", "migração")

    def categorias(self) -> dict:
        linhas = (self.r / "sdd/reports/MIGRACAO_DOCS_F26.tsv").read_text(encoding="utf-8").split("\n")[1:]
        return {ln.split("\t")[0]: ln.split("\t")[1] for ln in linhas if ln}

    def test_at005_copia_classifica_e_confere(self):
        self.migrar()
        self.assertEqual(self.categorias(), {
            "sdd/features/DEFINE_A.md": "igual",
            "sdd/reports/evidence/F/AT-001.log": "igual",
            "sdd/reports/evidence/F/codex-sessao.log": "fora",
            "sdd/reports/evidence/F/grande.log": "fora",
            "sdd/reports/evidence/F/sonda.log": "fora",
            "sdd/handoffs/HANDOFF_A.md": "ajustado",
        })
        self.assertEqual((self.r / "bin/codigo.sh").read_text(encoding="utf-8"), "echo main\n")   # código não migra
        rc, out, err = self.migracao("--conferir", self.TAG)
        self.assertEqual(rc, 0, out + err)
        rc, out, err = self.roda_longo([BASH, "sdd/bin/docs-varredura.sh", "."], self.r)
        self.assertEqual(rc, 0, out + err)                    # a ficha ajustada passa na varredura

    def test_at005_cada_desvio_sai_1(self):
        self.migrar()
        base = self.git(self.r, "rev-parse", "HEAD").strip()

        def desvio(nome, mexer, trecho):
            with self.subTest(desvio=nome):
                mexer()
                self.git(self.r, "add", "-A")      # o desvio entra no próprio commit da migração
                self.git(self.r, "commit", "-q", "--amend", "--allow-empty", "-m", "migração: " + nome)
                rc, out, err = self.migracao("--conferir", self.TAG)
                self.git(self.r, "reset", "-q", "--hard", base)
                self.git(self.r, "clean", "-qfd")
                self.assertEqual(rc, 1, out + err)
                self.assertIn(trecho, out)

        desvio("igual com outro conteúdo",
               lambda: self.escreve(self.r, "sdd/features/DEFINE_A.md", "# mexido\n"), "igual na lista")
        desvio("fora presente na main",
               lambda: self.escreve(self.r, "sdd/reports/evidence/F/codex-sessao.log", "x\n"), "fora na lista, mas está")
        desvio("fila com entrada",
               lambda: self.escreve(self.r, "sdd/curadoria/fila/F/20261117T000000Z/colheita.txt", "x\n"), "fila")

        def fora_sem_motivo():
            lista = self.r / "sdd/reports/MIGRACAO_DOCS_F26.tsv"
            lista.write_text(lista.read_text(encoding="utf-8").replace(
                "sdd/features/DEFINE_A.md\tigual\t", "sdd/features/DEFINE_A.md\tfora\tbruto: inventado"), encoding="utf-8")
            (self.r / "sdd/features/DEFINE_A.md").unlink()
        desvio("fora sem ser bruto (N1)", fora_sem_motivo, "sem ser bruto")

        def ajustado_com_mais():   # revisão do código, R3: o ajustado é o da tag com o aceite, nada além
            ficha = self.r / "sdd/handoffs/HANDOFF_A.md"
            ficha.write_text(ficha.read_text(encoding="utf-8") + "linha que a tag não tem\n", encoding="utf-8")
        desvio("ajustado com outro conteúdo", ajustado_com_mais, "diferente do ajuste da tag")

        # o commit da migração que traz código da tag (o bin/codigo.sh velho da branch de documentos): reprova
        self.git(self.r, "reset", "-q", "--hard", "HEAD~1")
        self.git(self.r, "clean", "-qfd")
        rc, out, err = self.migracao("--copiar", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.git(self.r, "checkout", "-q", self.TAG, "--", "bin/codigo.sh")
        self.git(self.r, "add", "-A")
        self.git(self.r, "commit", "-q", "-m", "migração com código da tag")
        rc, out, err = self.migracao("--conferir", self.TAG)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("bin/codigo.sh · o commit da migração", out)

    def test_at005_squash_com_o_codigo_da_frente_confere(self):
        # revisão do código, R4: a main recebe a frente num commit só (squash); a migração vem junto do código dela
        rc, out, err = self.migracao("--copiar", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.escreve(self.r, "bin/codigo.sh", "echo código novo da frente\n")
        self.escreve(self.r, "bin/novo.sh", "echo arquivo novo da frente\n")
        self.git(self.r, "add", "-A")
        self.git(self.r, "commit", "-q", "-m", "F: frente inteira (squash)")
        rc, out, err = self.migracao("--conferir", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: VERDE", out)

    def test_at005_commit_depois_da_migracao_nao_conta(self):
        # a release atualiza a ficha e o plano, e a colheita põe entrada na fila: a prova da migração continua de pé
        self.migrar()
        self.escreve(self.r, "sdd/features/DEFINE_A.md", "# DEFINE A, atualizado na release\n")
        self.escreve(self.r, "sdd/curadoria/fila/F/20261118T000000Z/colheita.txt", "x\n")
        self.commit(self.r, "papel da release")
        rc, out, err = self.migracao("--conferir", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: VERDE", out)

    def test_at005_copiar_recusa_documento_da_main_com_outro_conteudo(self):
        self.escreve(self.r, "sdd/features/DEFINE_A.md", "# a versão da main\n")
        self.commit(self.r, "documento da main")
        rc, out, err = self.migracao("--copiar", self.TAG)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("sdd/features/DEFINE_A.md", out)
        self.assertEqual((self.r / "sdd/features/DEFINE_A.md").read_text(encoding="utf-8"), "# a versão da main\n")
        self.assertFalse((self.r / "sdd/reports/MIGRACAO_DOCS_F26.tsv").exists())

    def test_at006_pode_aposentar_so_com_a_tag_no_ultimo_commit_e_a_conferencia_verde(self):
        rc, out, err = self.migracao("--pode-aposentar", self.TAG)
        self.assertEqual(rc, 1, out + err)                    # While: ainda sem migração, a conferência não sai 0
        self.migrar()
        rc, out, err = self.migracao("--pode-aposentar", self.TAG)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: PODE", out)
        outro = self.tmp / "outro"
        self.git(self.tmp, "clone", "-q", "-b", "docs/incorporar-starter", str(self.origin), str(outro))
        self.escreve(outro, "sdd/features/NOVO.md", "depois da tag\n")
        self.commit(outro, "depois da tag")
        self.git(outro, "push", "-q", "origin", "docs/incorporar-starter")
        rc, out, err = self.migracao("--pode-aposentar", self.TAG)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("não é o último commit", out)


# ── AT-007: o que não muda ──────────────────────────────────────────────────────────────────────────────────────

class SemRegressao(Base):
    def test_at007_push_so_de_documento_nao_publica_e_com_playbook_publica(self):
        papel = RAIZ / ".agents/skills/sdd-release/scripts/push-de-papel.py"
        docs = [p + "/X.md" for p in PASTAS_DOC] + ["sdd/GOVERNANCA_PADRAO.md"]
        rc, out, err = self.roda([PY, "-B", papel, RAIZ, "--branch", "main", *docs], self.tmp)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("NAO_PUBLICA", out)
        rc, out, err = self.roda([PY, "-B", papel, RAIZ, "--branch", "main", "sdd/features/X.md", "sdd/playbook.md"],
                                 self.tmp)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("PUBLICA", out)

    def test_at007_init_de_um_clone_com_documentos_nao_instala_documento(self):
        pkg = self.pacote("pkg")
        self.documentos_de_teste(pkg)
        self.commit(pkg, "documentos")
        projeto = self.repo("projeto")
        env = dict(self.env, SDD_OPEN_CHECK_UPDATES="0")
        rc, out, err = self.roda_longo([BASH, pkg / "bin/sdd-open.sh", "init", "--yes", "--vendors", "claude"], projeto, env)
        self.assertEqual(rc, 0, out + err)
        instalados = [p.relative_to(projeto).as_posix() for p in projeto.rglob("*") if p.is_file() and ".git" not in p.parts]
        self.assertEqual([p for p in instalados if "DOC_TESTE" in p or "GOVERNANCA_PADRAO.md" == p.split("/")[-1]
                          or p.startswith("sdd/estudos")], [])
        self.assertIn("sdd/bin/docs-varredura.sh", instalados)


# ── AT-011: o anexo do bruto ────────────────────────────────────────────────────────────────────────────────────

GH_FALSO = r'''#!/usr/bin/env bash
store="$GH_FAKE_STORE"
case "$1 $2" in
  "release view") [ -f "$store/existe-$3" ] && exit 0; exit 1 ;;
  "release upload") cp "$4" "$store/" && exit 0; exit 1 ;;
  "release download")
    shift 3; n=""; d=""
    while [ $# -gt 0 ]; do case "$1" in --pattern) n="$2"; shift 2 ;; --dir) d="$2"; shift 2 ;; *) shift ;; esac; done
    if [ -n "${GH_FAKE_TROCA:-}" ]; then cp "$GH_FAKE_TROCA" "$d/$n"; else cp "$store/$n" "$d/$n"; fi ;;
  *) exit 2 ;;
esac
'''


class Bruto(Base):
    def setUp(self):
        super().setUp()
        self.r = self.com_varredura("projeto")
        self.copia(".agents/skills/sdd-release/scripts/anexar-bruto.sh", self.r)
        self.commit(self.r, "release")
        self.store = self.tmp / "store"
        self.store.mkdir()
        gh = self.tmp / "gh-falso"
        gh.write_text(GH_FALSO, encoding="utf-8")
        gh.chmod(0o755)
        self.env_gh = dict(self.env, SDD_ANEXAR_GH=str(gh), GH_FAKE_STORE=str(self.store))
        self.bruto = self.r / "sdd/reports/evidence/F26_T/bruto"

    def anexar(self, env=None):
        return self.roda_longo([BASH, ".agents/skills/sdd-release/scripts/anexar-bruto.sh", "F26_T", "v9.9.9"], self.r,
                               env or self.env_gh)

    def test_at011_sem_bruto(self):
        rc, out, err = self.anexar()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("SEM BRUTO", out)

    def test_at011_bruto_no_gitignore(self):
        self.escreve(self.bruto, "codex.log", "x\n")
        rc, out, err = self.roda(["git", "check-ignore", "-q", "sdd/reports/evidence/F26_T/bruto/codex.log"], self.r)
        self.assertEqual(rc, 0, out + err)

    def test_at011_release_ausente_nada_enviado(self):
        self.escreve(self.bruto, "codex.log", "x\n")
        rc, out, err = self.anexar()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("NADA ANEXADO", out)
        self.assertEqual(list(self.store.iterdir()), [])

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at011_varredura_vermelha_nada_enviado(self):
        (self.store / "existe-v9.9.9").write_text("", encoding="utf-8")
        self.escreve(self.bruto, "codex.log", "fulano%sempresa-real.com.br\n" % ARROBA)
        rc, out, err = self.anexar()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("varredura", out)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), ["existe-v9.9.9"])

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at011_anexado_e_conferido_e_download_diferente_reprova(self):
        (self.store / "existe-v9.9.9").write_text("", encoding="utf-8")
        self.escreve(self.bruto, "codex.log", "transcrição\n")
        self.escreve(self.bruto, "gabarito/caso1.txt", "gabarito\n")
        rc, out, err = self.anexar()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: ANEXADO", out)
        with tarfile.open(str(self.store / "evidencia-bruta-F26_T.tar.gz")) as t:
            nomes = sorted(m.name[2:] if m.name.startswith("./") else m.name for m in t.getmembers() if m.isfile())
        self.assertEqual(nomes, ["codex.log", "gabarito/caso1.txt"])
        # o mesmo nome e os mesmos arquivos, outro conteúdo: a lista bate e os bytes não
        troca = self.tmp / "troca"
        self.escreve(troca, "codex.log", "OUTRA transcrição\n")
        self.escreve(troca, "gabarito/caso1.txt", "gabarito\n")
        falso = self.tmp / "falso.tar.gz"
        with tarfile.open(str(falso), "w:gz") as t:
            t.add(str(troca), arcname=".")
        rc, out, err = self.anexar(dict(self.env_gh, GH_FAKE_TROCA=str(falso)))
        self.assertEqual(rc, 1, out + err)
        self.assertIn("ANEXO DIFERENTE", out)
        self.assertNotIn("RESULTADO: ANEXADO", out)

    @unittest.skipIf(*SEM_GITLEAKS)
    def test_at011_nome_acentuado_confere(self):
        # revisão do código, R7: o tar do macOS grava o nome decomposto ("a" + til); a pasta e o anexo são comparados em
        # NFC, também com a localidade C
        (self.store / "existe-v9.9.9").write_text("", encoding="utf-8")
        self.escreve(self.bruto, "sessão/transcrição.log", "texto\n")
        rc, out, err = self.anexar(dict(self.env_gh, LC_ALL="C", LANG="C"))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: ANEXADO", out)

    def test_at011_link_na_pasta_nada_enviado(self):
        (self.store / "existe-v9.9.9").write_text("", encoding="utf-8")
        self.escreve(self.bruto, "codex.log", "x\n")
        try:
            os.symlink(str(self.tmp), str(self.bruto / "atalho"))
        except (OSError, NotImplementedError):
            self.skipTest("este sistema não cria link simbólico sem privilégio")
        rc, out, err = self.anexar()
        self.assertEqual(rc, 1, out + err)
        self.assertIn("link", out)
        self.assertEqual(sorted(p.name for p in self.store.iterdir()), ["existe-v9.9.9"])

    def test_at011_texto_da_release_e_da_referencia(self):
        skill = (RAIZ / ".agents/skills/sdd-release/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("anexar-bruto.sh {F} <tag>", skill)
        self.assertIn("references/bruto.md", skill)
        self.assertIn("docs-varredura.sh .", skill)              # a varredura antes do push (contrato, ajuste 5)
        ref = (RAIZ / ".agents/skills/sdd-release/references/bruto.md").read_text(encoding="utf-8")
        for termo in ("SEM BRUTO", "ANEXADO", "NADA ANEXADO", "ANEXO DIFERENTE"):
            self.assertIn(termo, ref)
        self.assertIn("sdd/reports/evidence/*/bruto/", (RAIZ / ".gitignore").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
