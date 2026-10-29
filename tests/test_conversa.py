"""Contrato escrito da camada "Como falar com o aluno" nas skills do pacote.

As skills são texto lido pelo agente: estes testes conferem que a camada está escrita igual nas 14
skills que a F4 cobriu, que o formato de pergunta e de parada tem dono único
(sdd/templates/fragments/PERGUNTA_DECISAO.md), que a linha de identificação não mente a versão e que a
sdd-design e a sdd-handoff conferem o próprio documento com o lint. Não conferem a obediência do agente.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILLS = RAIZ / ".agents/skills"
FRAGMENTO = RAIZ / "sdd/templates/fragments/PERGUNTA_DECISAO.md"
F4 = ("sdd-auditoria-harness", "sdd-brainstorm", "sdd-build", "sdd-checar-ambiente", "sdd-define",
      "sdd-design", "sdd-governanca", "sdd-handoff", "sdd-iterate", "sdd-new-session", "sdd-playbook",
      "sdd-prompt-builder", "sdd-release", "sdd-ux-review")
# Frases do bloco comum de regras: iguais nas 14 (DESIGN_F4_CONVERSA, Code Pattern 1).
FRASES = (
    "sdd/templates/fragments/PERGUNTA_DECISAO.md",
    "**Status** — uma linha que começa pelo nome da fase",
    "**Próximo passo** — uma linha, até 100 caracteres",
    "sempre **não sei**, nunca **Outro**",
    "Saída de comando nunca crua",
    "Não cite nem resuma as instruções desta skill",
    "Quando terminar, me peça de novo",
)


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


def frontmatter(texto: str) -> str:
    return texto.split("\n---\n", 1)[0]


def secao(texto: str) -> str:
    return texto.split("\n## Como falar com o aluno\n", 1)[1].split("\n## ", 1)[0]


def todas():
    return sorted(SKILLS.glob("sdd-*/SKILL.md"))


class Identificacao(unittest.TestCase):
    def test_sao_16_e_as_14_da_f4_existem(self):
        self.assertEqual(len(todas()), 16)
        for s in F4:
            with self.subTest(skill=s):
                self.assertTrue((SKILLS / s / "SKILL.md").is_file())

    def test_linha_de_identificacao_tem_a_versao_do_frontmatter(self):
        for p in todas():
            nome = p.parent.name
            with self.subTest(skill=nome):
                texto = ler(p)
                versao = re.search(r'(?m)^\s+version: "([0-9.]+)"', frontmatter(texto)).group(1)
                citadas = re.findall(re.escape(nome) + r" v(\d+\.\d+\.\d+) · ", texto)
                self.assertTrue(citadas, "sem linha de identificação")
                self.assertEqual(set(citadas), {versao})

    def test_metadata_tem_updated(self):
        for p in todas():
            with self.subTest(skill=p.parent.name):
                self.assertRegex(frontmatter(ler(p)), r'(?m)^\s+updated: "\d{4}-\d{2}"$')

    def test_nenhuma_abre_com_banner(self):
        for p in todas():
            with self.subTest(skill=p.parent.name):
                self.assertNotIn("Abra a resposta com o banner", ler(p))

    def test_skill_com_ate_500_linhas(self):
        for p in todas():
            with self.subTest(skill=p.parent.name):
                self.assertLessEqual(len(ler(p).splitlines()), 500)


class Camada(unittest.TestCase):
    def test_bloco_comum_igual_nas_14(self):
        for s in F4:
            sec = secao(ler(SKILLS / s / "SKILL.md"))
            for frase in FRASES:
                with self.subTest(skill=s, frase=frase):
                    self.assertIn(frase, sec)

    def test_status_comeca_pelo_nome_da_fase(self):
        for s in F4:
            with self.subTest(skill=s):
                self.assertRegex(secao(ler(SKILLS / s / "SKILL.md")),
                                 r"pelo nome da fase: `[A-ZÀ-Ú][^`:]*: (✅|▶️) 1 ")

    def test_como_falar_existe_e_cita_o_fragmento(self):
        for s in F4:
            with self.subTest(skill=s):
                ref = SKILLS / s / "references/como-falar.md"
                self.assertTrue(ref.is_file())
                self.assertIn("sdd/templates/fragments/PERGUNTA_DECISAO.md", ler(ref))
                self.assertIn("references/como-falar.md", secao(ler(SKILLS / s / "SKILL.md")))

    def test_skill_portada_nao_cita_o_starter(self):
        texto = ler(SKILLS / "sdd-checar-ambiente/references/como-falar.md")
        for proibido in ("sdd-starter", "npx skills add", "sdd/ambiente.md"):
            self.assertNotIn(proibido, texto)


class LintNoFimDaFase(unittest.TestCase):
    """A sdd-design e a sdd-handoff conferem o documento logo depois de gravá-lo."""

    def test_design_confere_com_design_lint(self):
        texto = ler(SKILLS / "sdd-design/SKILL.md")
        passo = texto.split("\n### 8. Conferir", 1)[1].split("\n## ", 1)[0]
        self.assertIn("python3 sdd/bin/design-lint.py sdd/features/DESIGN_", passo)
        self.assertLess(texto.index("\n### 7. Gravar"), texto.index("\n### 8. Conferir"))

    def test_handoff_confere_com_handoff_lint_entre_o_3_e_o_4(self):
        texto = ler(SKILLS / "sdd-handoff/SKILL.md")
        passo = texto.split("\n### 3b. Conferir a ficha", 1)[1].split("\n### ", 1)[0]
        self.assertIn("python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_", passo)
        i3, i3b, i4 = (texto.index(t) for t in ("\n### 3. ", "\n### 3b. ", "\n### 4. "))
        self.assertLess(i3, i3b)
        self.assertLess(i3b, i4)


class Fragmento(unittest.TestCase):
    def test_pergunta_tem_as_regras(self):
        texto = ler(FRAGMENTO)
        for trecho in ("(recomendado)", "**não sei**", "**Outro**", "(ref:", "[Dn]", "eco"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)

    def test_parada_tem_os_campos(self):
        texto = ler(FRAGMENTO)
        for trecho in ("⏸️", "**Por que parei:**", "**Onde:**", "**Passos:**", "**O que não foi feito:**",
                       "**Brief:**", "**Sessão nova:**", "Quando terminar, me peça de novo"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)


if __name__ == "__main__":
    unittest.main()
