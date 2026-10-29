"""Contrato escrito da camada "Como falar com o aluno" nas skills do pacote.

As skills são texto lido pelo agente: estes testes conferem que a camada está escrita igual nas 14
skills que a F4 cobriu e na sdd-kb (F5), que o formato de pergunta e de parada tem dono único
(sdd/templates/fragments/PERGUNTA_DECISAO.md), que a linha de identificação não mente a versão e que a
sdd-design e a sdd-handoff conferem o próprio documento com o lint, e que a entrevista de público da
sdd-ux-review só tem uma pergunta de decisão. Não conferem a obediência do agente.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import unittest

from apoio import PYTHON, RAIZ, Sandbox

SKILLS = RAIZ / ".agents/skills"
FRAGMENTO = RAIZ / "sdd/templates/fragments/PERGUNTA_DECISAO.md"
F4 = ("sdd-auditoria-harness", "sdd-brainstorm", "sdd-build", "sdd-checar-ambiente", "sdd-define",
      "sdd-design", "sdd-governanca", "sdd-handoff", "sdd-iterate", "sdd-new-session", "sdd-playbook",
      "sdd-prompt-builder", "sdd-release", "sdd-ux-review",
      "sdd-kb")  # as 14 da F4 + a sdd-kb da F5 (DESIGN_F5_CONHECIMENTO, Decision 7)
# Frases do bloco comum de regras: iguais nas 15 (DESIGN_F4_CONVERSA, Code Pattern 1).
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
    def test_sao_17_e_as_15_da_camada_existem(self):
        self.assertEqual(len(todas()), 17)
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
    def test_bloco_comum_igual_nas_15(self):
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


ENTREVISTA = SKILLS / "sdd-ux-review/references/entrevista-publico.md"
CONFIRMACAO = "Posso gravar este público em User and Context?"
ABERTA = re.compile(r"\*\*[^*\n]+\?\*\* Responda com [^\n]*não sei")


def perguntas_do_lint(texto):
    spec = importlib.util.spec_from_file_location("skill_lint", RAIZ / "sdd/bin/skill-lint.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.perguntas(texto)


class EntrevistaPublico(Sandbox):
    """Entrada opcional da sdd-ux-review: perguntas de fato abertas, uma só pergunta de decisão (F5)."""

    def test_passo_1_aponta_a_entrevista(self):
        texto = ler(SKILLS / "sdd-ux-review/SKILL.md")
        passo1 = texto.split("\n1. **Contexto.**", 1)[1].split("\n2. **Jornada.**", 1)[0]
        self.assertIn("references/entrevista-publico.md", passo1)
        self.assertIn("## User and Context", passo1)

    def test_cobre_publico_estagio_referencia_e_url(self):
        texto = ler(ENTREVISTA)
        for trecho in ("público", "estágio", "Catálogo de referências", "URL", "análise direta não disponível",
                       "Observado", "Desejado", "Recomendado", "sdd/templates/fragments/PERGUNTA_DECISAO.md"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)

    def test_perguntas_de_fato_sao_abertas(self):
        abertas = ABERTA.findall(ler(ENTREVISTA))
        self.assertGreaterEqual(len(abertas), 3)
        for inicio in ("**Quem vai usar", "**Em que estágio", "**Qual destas referências", "**Tem algum site"):
            with self.subTest(pergunta=inicio):
                self.assertTrue([a for a in abertas if a.startswith(inicio)], abertas)

    def test_pergunta_so_o_que_muda_a_experiencia(self):
        texto = ler(ENTREVISTA)
        for trecho in ("frequência de uso", "familiaridade com tecnologia", "volume de informação",
                       "risco de um erro", "aparelho"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)

    def test_so_a_confirmacao_tem_opcoes(self):
        achadas = perguntas_do_lint(ler(ENTREVISTA))
        self.assertEqual([p for _l, p, _o in achadas], ["**" + CONFIRMACAO + "**"], achadas)
        rotulos = [r.lower() for r, _resto in achadas[0][2]]
        self.assertEqual(rotulos[0], "sim", rotulos)
        self.assertIn("(recomendado)", achadas[0][2][0][1])
        self.assertIn("não sei", rotulos)
        self.assertFalse([r for r in rotulos if r.startswith("outr")], rotulos)

    def test_confirmacao_passa_no_skill_lint(self):
        s = self.tmp / "skills/sdd-entrevista"
        (s / "references").mkdir(parents=True)
        (s / "SKILL.md").write_text(ler(SKILLS / "sdd-ux-review/SKILL.md").replace(
            "name: sdd-ux-review", "name: sdd-entrevista", 1), encoding="utf-8")
        shutil.copy(str(ENTREVISTA), str(s / "references/como-falar.md"))
        rc, out, err = self.roda([PYTHON, "-B", RAIZ / "sdd/bin/skill-lint.py", "--conversa", s / "SKILL.md"],
                                 self.tmp)
        self.assertEqual(rc, 0, out + err)


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
