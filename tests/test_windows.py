"""F16 (AT-008): o que a suíte faz no Windows com Git Bash e Python nativo.

Teste que depende de recurso que o Windows não tem é pulado por uma constante de tests/apoio.py, com um
motivo que nomeia o recurso; nenhum outro arquivo decide sozinho que "no Windows não roda". Os 5 achados de
Windows guardados das revisões (F14) têm teste que roda no job `testes-windows`.
"""
from __future__ import annotations

import io
import re
import subprocess
import tokenize
import unittest

from apoio import BASH, RAIZ, Sandbox

TESTES = RAIZ / "tests"
# Pergunta de plataforma escrita à mão: decide o pulo sem passar pela constante. Lida pelos tokens do Python
# (nome, ponto, nome), nunca por expressão regular: texto entre aspas e comentário não contam (LM-005).
PERGUNTAS = {("os", "name"), ("sys", "platform"), ("platform", "system"), ("os", "geteuid")}


def perguntas_de_plataforma(codigo: str) -> list:
    """(linha, 'os.name') de cada pergunta de plataforma no código, fora de texto e de comentário."""
    nomes = [t for t in tokenize.generate_tokens(io.StringIO(codigo).readline)
             if t.type in (tokenize.NAME, tokenize.OP)]
    achou = []
    for a, b, c in zip(nomes, nomes[1:], nomes[2:]):
        if a.type == tokenize.NAME and b.string == "." and c.type == tokenize.NAME and (a.string, c.string) in PERGUNTAS:
            achou.append((a.start[0], a.string + "." + c.string))
    return achou

# Achado guardado → (arquivo de teste, teste que o mede no job do Windows).
ACHADOS = {
    "CRLF no stdout do playbook-curator.sh (F14 Playbook, rodada 4)":
        ("test_windows.py", "test_stdout_do_curator_sem_crlf"),
    "ramo tasklist do sdd-drive.sh (dono da trava vivo ou morto)":
        ("test_drive.py", "test_trava_de_processo_morto_se_libera"),
    "report-lint sem prova no Windows":
        ("test_report_lint.py", "test_log_capturado_da_feature_passa"),
    "sdd-archive sem prova no Windows":
        ("test_sdd_archive.py", "test_lista_por_lote_e_nao_muda_nada"),
    "trava sem O_NOFOLLOW (link no lugar da trava, F14 Drive, rodada 7)":
        ("test_drive.py", "test_trava_que_e_link_nao_cria_arquivo_fora"),
}


class Pulos(unittest.TestCase):
    def test_pulo_de_plataforma_so_por_constante_do_apoio(self):
        fora = []
        for f in sorted(TESTES.glob("*.py")):
            if f.name in ("apoio.py", "test_windows.py"):
                continue
            for n, pergunta in perguntas_de_plataforma(f.read_text(encoding="utf-8")):
                fora.append("%s:%d: %s" % (f.name, n, pergunta))
        self.assertEqual(fora, [], "use as constantes SEM_* / SOU_ROOT de tests/apoio.py")

    def test_a_varredura_acusa_a_pergunta_escrita_a_mao(self):
        for linha in ('@unittest.skipIf(os.name == "nt", "fcntl")\n', "if os.geteuid() == 0:\n    pass\n",
                      '@unittest.skipUnless(sys.platform == "darwin", "x")\n', "x = platform.system() == 'Windows'\n"):
            with self.subTest(linha=linha):
                self.assertEqual(len(perguntas_de_plataforma(linha)), 1)
        for limpo in ("@unittest.skipIf(*SEM_FCNTL)\n", 'x = "sys.exit(os.name != 1)"  # os.name num texto\n'):
            with self.subTest(limpo=limpo):
                self.assertEqual(perguntas_de_plataforma(limpo), [])

    def test_cada_constante_tem_motivo_que_nomeia_o_recurso(self):
        import apoio
        for nome, recurso in (("SEM_SYMLINK", "link simbólico"), ("SEM_FCNTL", "fcntl"), ("SEM_CHMOD", "chmod"),
                              ("SEM_SINAL", "sinal"), ("SEM_POSIX_UID", "geteuid"), ("SOU_ROOT", "root")):
            with self.subTest(constante=nome):
                cond, motivo = getattr(apoio, nome)
                self.assertIsInstance(cond, bool)
                self.assertIn(recurso, motivo)


class AchadosGuardados(unittest.TestCase):
    def test_cada_achado_tem_teste_que_roda_no_job(self):
        for achado, (arquivo, teste) in ACHADOS.items():
            with self.subTest(achado=achado):
                # cada achado cita um teste que existe (rodada 3, R4: dois não citavam nenhum)
                self.assertTrue(teste, achado)
                self.assertIn("def %s(" % teste, (TESTES / arquivo).read_text(encoding="utf-8"))


# F16W: subprocess em modo texto sem encoding decodifica no Windows em cp1252 (LM-014): a revisão em português e o
# caminho do `git rev-parse` numa pasta com acento chegariam trocados. Fora daqui: os arquivos que vão ao starter como
# estão (o starter tem o próprio CI) e 2 de skill cuja saída lida é só ASCII.
TEXTO_SEM_ENCODING_ACEITO = {
    ".agents/skills/sdd-auditoria-harness/scripts/collect_evidence.py": "lê só a data do git (%cs), ASCII",
    ".agents/skills/ux-review-builder/tests/test_validate_generated_bundle.py": "teste da skill; lê o exit, não o texto",
}


def chamadas_texto_sem_encoding(codigo: str) -> list:
    """Linha de cada subprocess.run/Popen/check_output/... com text=True e sem encoding na mesma chamada."""
    achou = []
    for m in re.finditer(r"subprocess\.(?:run|Popen|check_output|check_call|call)\(", codigo):
        i, prof, j = m.end(), 1, m.end()
        while prof and j < len(codigo):
            prof += {"(": 1, ")": -1}.get(codigo[j], 0)
            j += 1
        chamada = codigo[i:j]
        if re.search(r"\b(text|universal_newlines)=True", chamada) and "encoding=" not in chamada:
            achou.append(codigo.count("\n", 0, m.start()) + 1)
    return achou


def chamadas_bash_pelo_nome(codigo: str) -> list:
    """Linha de cada subprocess.run/Popen/... cujo programa é a palavra "bash" (no Windows, o CreateProcess acha o
    bash.exe do WSL em System32 antes do PATH; F16W, revisão rodada 2)."""
    return [codigo.count("\n", 0, m.start()) + 1
            for m in re.finditer(r"subprocess\.(?:run|Popen|check_output|check_call|call)\(\s*\[\s*[\"']bash[\"']", codigo)]


class Decodificacao(unittest.TestCase):
    def test_subprocess_em_modo_texto_sempre_com_encoding(self):
        arquivos = [l.strip() for l in (RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
                    if l.strip().endswith((".py", ".sh")) and not l.startswith("scripts/starter/raiz/")]
        self.assertGreater(len(arquivos), 100)   # a lista veio do MANIFEST, não vazia
        fora = []
        for rel in arquivos:
            if rel in TEXTO_SEM_ENCODING_ACEITO or rel == "tests/test_windows.py":   # este: os exemplos do autoteste
                continue
            for n in chamadas_texto_sem_encoding((RAIZ / rel).read_text(encoding="utf-8")):
                fora.append("%s:%d" % (rel, n))
        self.assertEqual(fora, [], 'passe encoding="utf-8", errors="replace" (LM-014)')

    def test_subprocess_nunca_chama_bash_pelo_nome(self):
        arquivos = [l.strip() for l in (RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
                    if l.strip().endswith((".py", ".sh")) and not l.startswith("scripts/starter/raiz/")
                    and l.strip() != "tests/test_windows.py"]
        fora = ["%s:%d" % (rel, n) for rel in arquivos
                for n in chamadas_bash_pelo_nome((RAIZ / rel).read_text(encoding="utf-8"))]
        self.assertEqual(fora, [], "chame o bash pelo caminho (BASH de tests/apoio.py; SDD_<SCRIPT>_BASH; achar_bash)")
        self.assertEqual(chamadas_bash_pelo_nome('r = subprocess.run(["bash", x], text=True)\n'), [1])
        self.assertEqual(chamadas_bash_pelo_nome("subprocess.Popen(\n  ['bash', '-c', c])\n"), [1])
        self.assertEqual(chamadas_bash_pelo_nome('subprocess.run([BASH, x])\n'), [])

    def test_a_varredura_acusa_e_respeita_o_encoding(self):
        self.assertEqual(chamadas_texto_sem_encoding('x = subprocess.run(["git"], capture_output=True, text=True)\n'), [1])
        self.assertEqual(chamadas_texto_sem_encoding('\nsubprocess.Popen(f(a), universal_newlines=True)\n'), [2])
        self.assertEqual(chamadas_texto_sem_encoding(
            'subprocess.run(["git"], text=True,\n               encoding="utf-8")\n'), [])
        self.assertEqual(chamadas_texto_sem_encoding('subprocess.run(["git"], capture_output=True)\n'), [])

    def test_os_aceitos_ainda_existem_e_ainda_precisam(self):
        for rel in TEXTO_SEM_ENCODING_ACEITO:
            with self.subTest(arquivo=rel):
                self.assertTrue(chamadas_texto_sem_encoding((RAIZ / rel).read_text(encoding="utf-8")))


class FimDeLinha(Sandbox):
    def test_gitattributes_poe_lf_em_todo_checkout(self):
        regras = [l for l in (RAIZ / ".gitattributes").read_text(encoding="utf-8").splitlines()
                  if l.strip() and not l.startswith("#")]
        self.assertEqual(regras[0], "* text=auto eol=lf")

    def test_stdout_do_curator_sem_crlf(self):
        # No Windows, o Python nativo traduz \n em \r\n no stdout em modo texto: quem lê a saída do curator
        # (o agente, o --conferir-bloco) veria \r no fim de cada linha. Lido em bytes, sem tradução.
        vazio = self.tmp / "colher"
        vazio.mkdir()
        r = subprocess.run([BASH, str(RAIZ / "sdd/bin/playbook-curator.sh"), "--colher", str(vazio),
                            str(RAIZ / "sdd/playbook.md")], cwd=str(self.tmp), env=dict(self.env, SDD_TRACE="off"),
                           capture_output=True, stdin=subprocess.DEVNULL, timeout=120)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(b"RESULTADO: NADA A COLHER", r.stdout)
        self.assertNotIn(b"\r", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
