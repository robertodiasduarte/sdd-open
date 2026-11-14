"""F16 (AT-004, AT-005): o texto das 3 skills de entrada e as cópias que precisam ficar iguais.

As skills são instaladas sozinhas (a F17 as gera como zip): a tabela de instalação mora nos 3 SKILL.md e as
funções do gh moram nos 2 scripts. Este teste é o que impede uma cópia de derivar da outra.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILLS = RAIZ / ".agents/skills"
TRES = ("sdd-checar-ambiente", "sdd-iniciar-repo", "sdd-new-session")
CHECAR = SKILLS / "sdd-checar-ambiente/scripts/checar.sh"
INVENTARIO = SKILLS / "sdd-iniciar-repo/scripts/inventario.sh"


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


def skill(nome: str) -> str:
    return ler(SKILLS / nome / "SKILL.md")


def bloco_instalar(texto: str) -> str:
    m = re.search(r"<!-- INSTALAR-INICIO -->\n.*?<!-- INSTALAR-FIM -->\n", texto, re.S)
    assert m, "bloco INSTALAR ausente"
    return m.group(0)


def bloco_gh(texto: str) -> str:
    ini = texto.index("\n# ── gh e instalação por sistema (F16)")
    fim = texto.index("\n# ── fim do gh", ini)   # no começo da linha: o cabeçalho cita o marcador no meio do texto
    bloco = texto[ini:fim]
    assert "gh_estado() {" in bloco and "instalar_gh() {" in bloco, "o bloco do gh não tem as funções"
    return bloco


class Instalacao(unittest.TestCase):
    def test_o_bloco_de_instalacao_e_igual_nas_3_skills(self):
        blocos = {n: bloco_instalar(skill(n)) for n in TRES}
        self.assertEqual(len(set(blocos.values())), 1, list(blocos))

    def test_o_bloco_tem_os_comandos_de_cada_sistema_e_o_login(self):
        b = bloco_instalar(skill(TRES[0]))
        for termo in ("xcode-select --install", "brew install git", "winget install --id Git.Git -e", "sudo apt install git",
                      "brew install gh", "https://cli.github.com", "winget install --id GitHub.cli -e",
                      "https://github.com/cli/cli/blob/trunk/docs/install_linux.md", "feche e abra o terminal",
                      "`gh auth login` → **GitHub.com** → **HTTPS** →\n**Yes** → **Login with a web browser**",
                      "O `gh` não é obrigatório"):
            with self.subTest(termo=termo):
                self.assertIn(termo, b)

    def test_o_comando_que_o_script_imprime_esta_na_tabela(self):
        b = bloco_instalar(skill(TRES[0]))
        comandos = re.findall(r'echo "([^"(]*?)\s{3}', bloco_gh(ler(CHECAR)))
        self.assertEqual(len(comandos), 3, comandos)   # macOS, Windows e Linux: sem eles o teste não avalia nada
        for comando in comandos:
            with self.subTest(comando=comando):
                self.assertIn(comando.replace("siga ", ""), b)

    def test_as_funcoes_do_gh_sao_iguais_nos_2_scripts(self):
        self.assertEqual(bloco_gh(ler(CHECAR)), bloco_gh(ler(INVENTARIO)))


class Versoes(unittest.TestCase):
    def test_as_3_skills_sobem_de_versao(self):
        for nome, versao in (("sdd-checar-ambiente", "1.5.2"), ("sdd-iniciar-repo", "1.2.1"), ("sdd-new-session", "1.6.1")):
            with self.subTest(skill=nome):
                texto = skill(nome)
                self.assertIn('  version: "%s"' % versao, texto)
                self.assertIn("`%s v%s · nov/2026 ·" % (nome, versao), texto)


class IniciarRepo(unittest.TestCase):
    def test_passo_0_avisa_do_gh_cedo_sem_parar(self):
        passo0 = skill("sdd-iniciar-repo").split("## Passo 0", 1)[1].split("## Passo 1", 1)[0]
        for termo in ("`gh --version` falha, ou `gh auth status` diz que não há conta logada", "**não pare**",
                      "[auto · de rotina] **Instalo o programa do GitHub agora ou depois?**", "**instalar agora** (recomendado)",
                      "**depois** — eu sigo, e paro só na publicação (Passo 6)", "**não sei**", "<!-- INSTALAR-INICIO -->"):
            with self.subTest(termo=termo):
                self.assertIn(termo, passo0)

    def test_passo_2_le_a_linha_gh_e_passo_6_mantem_a_checagem(self):
        texto = skill("sdd-iniciar-repo")
        passo2 = texto.split("## Passo 2", 1)[1].split("## Passo 3", 1)[0]
        self.assertIn("`gh: ausente`, `gh: deslogado`, `gh: ok` ou `gh: sem resposta`", passo2)
        passo6 = texto.split("## Passo 6", 1)[1].split("## Passo 7", 1)[0]
        self.assertIn("`gh --version` falha", passo6)
        self.assertIn("`gh auth status` sem conta logada", passo6)
        self.assertNotIn("Mac: baixe o instalador", passo6)


class NovaSessao(unittest.TestCase):
    def setUp(self):
        self.texto = skill("sdd-new-session")

    def test_slot_cheio_como_esta_e_vazio_pelo_checar_editores(self):
        for termo in ("**cheio ⇒ use como está**, inclusive com argumentos (`open -a \"Cursor\"`)",
                      "scripts/checar.sh --editores`", "`open -a \"<App>\"`", "`%LOCALAPPDATA%\\Programs`",
                      "`Get-Command\n  <nome>`", "modo terminal", "`editor: 'open -a \"Visual Studio Code\"'`"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_lista_do_checar_editores_so_vale_com_versao_e_forma(self):
        # F16 rodada 4, R1 (corrigido na F18/F20): uma sdd-checar-ambiente anterior à 1.5.0 não conhece
        # --editores, cai no modo normal e sai 0; a lista só vale com a versão e a forma "<nome><TAB><comando>".
        for termo in ("**Confira a lista antes de usá-la:**", "for 1.5.0 ou maior **e** toda linha não vazia",
                      "`<nome><TAB><comando>`\n  (exatamente um TAB", "cai no\n  diagnóstico normal e sai 0",
                      "⇒ trate como \"nenhum editor achado\""):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_slot_vazio_pergunta_uma_vez_e_nunca_escolhe_sozinho(self):
        # pedido do Roberto (2026-11-11): "antes de abrir pela primeira vez, o sdd deveria perguntar o default"
        for termo in ("duas vazias ⇒ pergunte, uma vez só, e nunca escolha sozinho:**",
                      "**Sua decisão** — [D2 · muda o produto] **Onde você quer abrir as frentes deste projeto?**",
                      "**o 1º editor da lista** (recomendado)", "**cada outro editor da lista**",
                      "**só no terminal, com Claude Code**", '`editor: "terminal:claude"`',
                      "**só no terminal, com Codex**", '`editor: "terminal:codex"`', "**dizer o meu comando**",
                      "**não sei**", "pergunta não volta enquanto ele estiver cheio",
                      # rodada 5, R1: a escolha é deste computador e vale para todas as frentes na hora
                      "`git config --get sdd.editor`", "`git config --local sdd.editor '<valor>'`",
                      "nunca no slot", "basta preencher o slot `editor`",
                      # rodada 5, R2: a ordem da detecção, não "o que o terminal acha pelo nome"
                      "o 1º na ordem da detecção (o comando no PATH vem antes do app do macOS"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)
        self.assertNotIn("**outro**", self.texto)   # PERGUNTA_DECISAO: nunca "Outro"

    def test_modo_terminal_em_3_passos_sem_presumir_um_agente(self):
        passo3 = self.texto.split("## Passo 3", 1)[1]
        self.assertIn("**Em modo terminal** (slot `terminal:<agente>`, ou sem editor)", passo3)
        self.assertIn("1. abra um terminal novo; 2. `cd \"<pasta da frente>\"`; 3. rode nele o agente do slot (`claude`, "
                      "`codex`…; sem\n   slot, o que você usa)", passo3)

    def test_aviso_final_nas_duas_formas(self):
        passo3 = self.texto.split("## Passo 3", 1)[1]
        self.assertIn("com editor: `⚠️ Continue na janela nova.", passo3)
        self.assertIn("em modo terminal: `⚠️ Continue num terminal novo aberto na pasta da frente. Esta sessão do agente "
                      "continua presa\n     à pasta onde foi aberta — nenhum cd muda isso. Build, commit e push rodam lá.`",
                      passo3)


class ChecarAmbiente(unittest.TestCase):
    def test_skill_descreve_o_gh_o_editor_e_o_modo_editor(self):
        texto = skill("sdd-checar-ambiente")
        for termo in ("`gh auth status --hostname github.com`", "**Nunca 🔴**", "o `--frente` não fala dele",
                      "scripts/checar.sh --editor`", "`/Applications` ou `~/Applications`", "`code.cmd` ou `cursor.cmd`",
                      "**Sem editor não é problema**"):
            with self.subTest(termo=termo):
                self.assertIn(termo, texto)


if __name__ == "__main__":
    unittest.main()
