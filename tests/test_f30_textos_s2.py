"""F30 S2 — o texto das skills leva a disciplina de teste (DEFINE_F30_QUALIDADE_CODIGO, AT-015).

A `sdd-build` do Open tem o vermelho antes do verde (`AT-nnn.antes.log`, coluna `Antes`), a sabotagem declarada no
DESIGN rodada pelo `sabotagem.sh` e o passo Refatorar entre Verificar e Marcar, com `build.refatorar`; a `sdd-design` e o
molde do DESIGN pedem a tabela de sabotagens; o molde do relatório tem a coluna `Antes`; o config tem a chave. O texto da
disciplina mora em `web/references/disciplina-de-teste.md` e chega ao starter sem citar `sdd/bin/` (LM-035).
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ
from test_gerar_starter import Base

BUILD = RAIZ / ".agents/skills/sdd-build"
DISCIPLINA = BUILD / "web/references/disciplina-de-teste.md"
TABELA_SABOTAGEM = "| AT | Arquivo | Trocar | Por | O que o teste deve acusar |"
F29 = ("Não cite nem resuma", "comece com esta linha", "versão atual: http")


def ler(rel: str) -> str:
    return re.sub(r"\s+", " ", (RAIZ / rel).read_text(encoding="utf-8"))


class AT015Build(unittest.TestCase):
    def setUp(self):
        self.skill = ler(".agents/skills/sdd-build/SKILL.md")

    def test_vermelho_antes_do_verde(self):
        self.assertIn("AT-nnn.antes.log", self.skill)
        self.assertIn("coluna `Antes`", self.skill)
        self.assertIn("`shall continue to`", self.skill)
        self.assertIn("web/references/disciplina-de-teste.md", self.skill)

    def test_sabotagem_no_5a(self):
        cinco_a = self.skill[self.skill.index("**5a. Verify Gate"):self.skill.index("**5b.")]
        self.assertIn("bash sdd/bin/sabotagem.sh", cinco_a)
        self.assertIn("AT-nnn.sabotagem.log", cinco_a)
        self.assertIn("o teste não pega o defeito", cinco_a)

    def test_refatorar_entre_verificar_e_marcar(self):
        v = self.skill.index("4. **Verificar:**")
        r = self.skill.index("5. **Refatorar**")
        m = self.skill.index("6. **Marcar**")
        self.assertLess(v, r)
        self.assertLess(r, m)
        passo = self.skill[r:m]
        self.assertIn("build.refatorar: false", passo)
        self.assertIn("arquivos da tarefa", passo)
        self.assertIn("refatorar: desligado", passo)

    def test_skill_e_modo_web_no_teto(self):
        for rel in (".agents/skills/sdd-build/SKILL.md", ".agents/skills/sdd-build/web/MODO_WEB.md",
                    ".agents/skills/sdd-design/SKILL.md"):
            with self.subTest(arquivo=rel):
                self.assertLessEqual(len((RAIZ / rel).read_text(encoding="utf-8").splitlines()), 500)


class AT015Disciplina(unittest.TestCase):
    def test_texto_unico_sem_sdd_bin(self):
        texto = DISCIPLINA.read_text(encoding="utf-8")
        for trecho in ("AT-nnn.antes.log", "`shall continue to`", "cópia descartável", "`build.refatorar: false`",
                       "arquivos da tarefa", "CRITERIO_DANO"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, re.sub(r"\s+", " ", texto))
        self.assertNotIn("sdd/bin/", texto)
        for padrao in F29:
            self.assertNotIn(padrao, texto)

    def test_modo_web_cita_e_concilia_a_mudanca_cirurgica(self):
        modo = ler(".agents/skills/sdd-build/web/MODO_WEB.md")
        self.assertIn("references/disciplina-de-teste.md", modo)
        self.assertNotIn("não refatorar código adjacente sem necessidade", modo)
        self.assertIn("só o que a tarefa tocou", modo)


class AT015DesignMoldesConfig(unittest.TestCase):
    def test_design_pede_a_tabela_de_sabotagens(self):
        for rel in (".agents/skills/sdd-design/SKILL.md", "sdd/templates/DESIGN_TEMPLATE.md"):
            with self.subTest(arquivo=rel):
                texto = ler(rel)
                self.assertIn(TABELA_SABOTAGEM, texto)
                self.assertIn("CRITERIO_DANO.md", texto)
        self.assertIn("pelo menos uma por feature", ler(".agents/skills/sdd-design/SKILL.md"))

    def test_molde_do_relatorio_tem_a_coluna_antes(self):
        molde = (RAIZ / "sdd/templates/BUILD_REPORT_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertRegex(molde, r"(?m)^\| ID \| Critério[^|]*\| Antes \| Resultado \| Evidência \|$")
        self.assertIn("refatorar: desligado", molde)

    def test_config_tem_build_refatorar(self):
        config = (RAIZ / "sdd/config.example.yaml").read_text(encoding="utf-8")
        self.assertRegex(config, r"(?m)^build:\n(?:  #.*\n)*  refatorar: true$")

    def test_brief_do_worker_tem_a_excecao_da_nao_regressao(self):
        brief = ler("sdd/templates/fragments/WORKER_BRIEF.md")
        self.assertIn("vermelha no comportamento novo", brief)
        self.assertIn("verde no `shall continue to`", brief)

    def test_contrato_de_evidencia_e_convencoes(self):
        evid = ler("sdd/templates/fragments/EVIDENCIA.md")
        self.assertIn("AT-nnn.antes.log", evid)
        self.assertIn("AT-nnn.sabotagem.log", evid)
        self.assertIn("`sabotagem.sh`", ler("docs/cli-conventions.md"))


class AT015Starter(Base):
    def test_starter_leva_a_disciplina_sem_sdd_bin(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        build = self.starter / "skills" / "sdd-build"
        skill = (build / "SKILL.md").read_text(encoding="utf-8")
        copia = build / "references" / "disciplina-de-teste.md"
        self.assertIn("references/disciplina-de-teste.md", skill)
        self.assertTrue(copia.is_file())
        for p in (build / "SKILL.md", copia):
            with self.subTest(arquivo=p.name):
                self.assertNotIn("sdd/bin/", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
