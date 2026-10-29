"""Contrato escrito da migration provada por leitura (sdd-build) e do bloco do OK (sdd-release).

As skills são texto lido pelo agente: estes testes conferem que as regras estão escritas e amarradas
aos scripts que as cobram (report-lint.py, deploy-espera-testes.py), não a obediência do agente.
"""
from __future__ import annotations

import re
import unittest

from apoio import BASH, RAIZ, Sandbox

SKILLS = RAIZ / ".agents/skills"
BUILD = SKILLS / "sdd-build/SKILL.md"
REFERENCIA = SKILLS / "sdd-build/references/aplicar-migration.md"
RELEASE = SKILLS / "sdd-release/SKILL.md"
TEMPLATE = RAIZ / "sdd/templates/BUILD_REPORT_TEMPLATE.md"
PLAYBOOK = RAIZ / "sdd/playbook.md"


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


def versao(p) -> str:
    return re.search(r'(?m)^\s+version: "([0-9.]+)"', ler(p)).group(1)


def bloco_do_ok() -> str:
    item = ler(RELEASE).split("7. **PARAR e mostrar (o 1 OK)", 1)[1].split("\n## FASE 2", 1)[0]
    return item.split("```markdown", 1)[1].split("```", 1)[0]


class SddRelease(unittest.TestCase):
    def test_versao(self):
        self.assertEqual(versao(RELEASE), "2.2.0")

    def test_item_7_roda_o_script(self):
        item = ler(RELEASE).split("7. **PARAR e mostrar (o 1 OK)", 1)[1].split("```markdown", 1)[0]
        self.assertIn("python3 .agents/skills/sdd-release/scripts/deploy-espera-testes.py", item)
        self.assertTrue((SKILLS / "sdd-release/scripts/deploy-espera-testes.py").is_file())

    def test_bloco_tem_os_campos_na_ordem(self):
        bloco = bloco_do_ok()
        rotulos = ["**O que sobe:**", "**O que muda em produção:**", "**O push publica sozinho?**",
                   "**O deploy espera os testes?**", "**Banco:**", "**Verificações:**", "**Veredito:**",
                   "**Ledger:**"]
        posicoes = [bloco.find(r) for r in rotulos]
        self.assertNotIn(-1, posicoes, dict(zip(rotulos, posicoes)))
        self.assertEqual(posicoes, sorted(posicoes))
        self.assertIn("WAIVED", bloco)
        self.assertIn("feature_id", bloco)
        self.assertIn("## Migrations aplicadas", bloco)

    def test_uma_pergunta_so_e_a_ultima_linha(self):
        linhas = [l.strip() for l in bloco_do_ok().splitlines() if l.strip()]
        self.assertEqual(linhas[-1], "**Posso finalizar (push + deploy + verificar)?**")
        perguntas = [l for l in linhas if l.startswith("**Posso")]
        self.assertEqual(len(perguntas), 1, perguntas)

    def test_cada_resultado_do_script_tem_traducao(self):
        item = ler(RELEASE).split("7. **PARAR e mostrar (o 1 OK)", 1)[1].split("\n## FASE 2", 1)[0]
        for res in ("`SIM`", "`NAO`", "`NAO_SEI`", "`NAO_SE_APLICA`"):
            self.assertIn(res, item)
        self.assertIn("não\n     consegui afirmar: <motivo>", item)
        self.assertIn('nunca "sim"', item)
        self.assertIn("Verificação ausente dita como ausente", item)

    def test_report_lint_da_fase_0_cita_migration(self):
        self.assertIn("migration listada sem a linha provada em `## Migrations aplicadas`", ler(RELEASE))


class SddBuild(unittest.TestCase):
    def test_versao(self):
        self.assertEqual(versao(BUILD), "2.1.0")

    def test_passo_4b_manda_ler_a_referencia(self):
        passo = ler(BUILD).split("### 4b. Migration", 1)[1].split("### 5.", 1)[0]
        self.assertIn("references/aplicar-migration.md", passo)
        self.assertIn("**antes** do Verify Gate", passo)
        self.assertIn("LM-004", passo)

    def test_referencia_tem_as_regras_do_starter(self):
        texto = ler(REFERENCIA)
        for trecho in ("Descubra, não pergunte o que dá para descobrir", "Nome **e** ref do projeto",
                       "**Exit 0 não é prova.**", "**Um passo por vez.**", "pare antes de qualquer confirmação",
                       "`supabase db reset` **apaga o banco local inteiro**", "## Migrations aplicadas",
                       "MIG-001.log", "recibo:"):
            self.assertIn(trecho, texto)

    def test_referencia_sem_arquivo_de_ambiente_do_starter(self):
        texto = ler(REFERENCIA)
        self.assertNotIn("sdd/ambiente.md", texto)
        self.assertNotIn("- banco:", texto)
        self.assertNotIn("sdd-starter", texto)


class TemplateEPlaybook(Sandbox):
    def test_template_tem_a_secao_com_as_colunas(self):
        secao = ler(TEMPLATE).split("## Migrations aplicadas", 1)[1].split("\n## ", 1)[0]
        self.assertIn("| Arquivo | Projeto (nome · ref) | Aplicada em | Prova por leitura |", secao)
        self.assertLess(ler(TEMPLATE).index("## Files Created"), ler(TEMPLATE).index("## Migrations aplicadas"))

    def test_lm_004_no_sempre_e_playbook_valido(self):
        sempre = ler(PLAYBOOK).split("\n## Sempre\n", 1)[1].split("\n## ", 1)[0]
        self.assertRegex(sempre, r"- \[LM-004\] .*`exit 0`.*migration")
        r = self.repo()  # o playbook-lint exige repo git; a cópia do Verify Gate (git archive) não tem
        self.copia("sdd/bin/playbook-lint.sh", r)
        self.copia("sdd/playbook.md", r)
        rc, out, err = self.roda([BASH, "sdd/bin/playbook-lint.sh", "sdd/playbook.md"], r)
        self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    unittest.main()
