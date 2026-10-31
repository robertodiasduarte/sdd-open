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
        self.assertEqual(versao(RELEASE), "2.5.0")

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
        self.assertEqual(versao(BUILD), "2.4.0")

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


def passo(texto: str, inicio: str, fim: str) -> str:
    return texto.split(inicio, 1)[1].split(fim, 1)[0]


def por_que(p) -> str:
    return passo(ler(p), "## Por que cada regra existe", "## Encerramento (obrigatório)")


class SddBuildEvidencia(unittest.TestCase):
    """F7: a sdd-build liga o guard, o baseline do gate, o baseline de testes e a linha do avaliador."""

    def test_passo_1_confere_a_flag_de_prompts(self):
        p1 = passo(ler(BUILD), "### 1. Contexto e landmines", "### 1.5.")
        self.assertIn("flag `LLM Prompts` do DEFINE contra o DESIGN", p1)
        self.assertIn("pare e itere o DESIGN", p1)
        self.assertIn("evidence.require_avaliacao_layers", p1)
        self.assertIn("rode o `init` de novo", p1)

    def test_guard_antes_dos_dois_despachos(self):
        p15 = passo(ler(BUILD), "### 1.5.", "### 2–3.")
        p5d = passo(ler(BUILD), "**5d.", "### 6.")
        for trecho in (p15, p5d):
            self.assertIn("bash sdd/bin/avaliador-guard.sh", trecho)
            self.assertIn("exit 1", trecho)
            self.assertIn("2", trecho)

    def test_gate_baseline_e_test_baseline_no_passo_5(self):
        p5 = passo(ler(BUILD), "### 5. Validação", "**5c.")
        self.assertIn("bash sdd/bin/gate-baseline.sh sdd/features/DEFINE_{F}.md --sobrepor", p5)
        self.assertIn("bash sdd/bin/test-baseline.sh", p5)
        self.assertIn("--aceitar", p5)

    def test_passo_6_tem_a_linha_do_avaliador_e_o_fragmento(self):
        p6 = passo(ler(BUILD), "### 6. BUILD_REPORT", "## Quality Gate")
        for trecho in ("avaliador: N.A. (<motivo>)", "avaliador: PENDENTE (<motivo>)",
                       "sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md"):
            self.assertIn(trecho, p6)
        self.assertTrue((RAIZ / "sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md").is_file())

    def test_um_por_que_por_regra_nova(self):
        texto = por_que(BUILD)
        for regra in ("**Guard antes de despachar o avaliador**", "**Gate corrigido roda contra o código anterior**",
                      "**Só falha de teste nova aborta**", "**A linha do avaliador é obrigatória**",
                      "**A flag `LLM Prompts` do DEFINE confere com o DESIGN antes de codar**"):
            self.assertIn(regra, texto)


class SddReleaseEvidencia(unittest.TestCase):
    """F7: a 0a aborta com PENDENTE e com exit de formatador — qualquer exit ≠ 0, não só 1 ou 2."""

    def test_0a_tem_os_dois_comandos_com_diferente_de_zero(self):
        fase0a = passo(ler(RELEASE), "**0a. Determinístico**", "**0b.")
        self.assertRegex(fase0a, r"report-lint\.py --pendente sdd/reports/BUILD_REPORT_\{F\}\.md`:\s+exit ≠ 0")
        self.assertRegex(fase0a, r"bash sdd/bin/gate-shell-evidencia\.sh`[^\n]*\n[^\n]*exit ≠ 0")
        self.assertIn("Exit 64 ou 127", fase0a)
        self.assertIn("bash sdd/bin/verify-gate.sh --sem-define <F>", fase0a)

    def test_gates_de_abortar(self):
        gates = passo(ler(RELEASE), "## Gates de ABORTAR", "## Quando pular")
        self.assertIn("report-lint --pendente ≠0", gates)
        self.assertIn("gate-shell-evidencia ≠0", gates)

    def test_um_por_que_por_regra_nova(self):
        texto = por_que(RELEASE)
        self.assertIn("**Avaliação `PENDENTE` aborta a release**", texto)
        self.assertIn("**O exit de cada log é conferido**", texto)
        self.assertIn("**Release sem DEFINE também deixa registro**", texto)


class TemplatesEvidencia(unittest.TestCase):
    EVIDENCIA = RAIZ / "sdd/templates/fragments/EVIDENCIA.md"

    def test_evidencia_tem_receita_forma_minima_e_as_tres_formas(self):
        texto = ler(self.EVIDENCIA)
        for trecho in ("out=$(eval \"$cmd\" 2>&1); rc=$?", "printf '[exit=%s]\\n' \"$rc\"",
                       "### A linha do avaliador", "avaliador: N.A. (<motivo>)", "avaliador: PENDENTE (<motivo>)",
                       "**forma mínima**", "**reprova**", "git check-ignore", "Result | Evidence"):
            self.assertIn(trecho, texto)
        self.assertNotIn("não confere linha nenhuma e sai 0", texto)

    def test_template_aceita_pendente_e_cita_layers(self):
        texto = ler(TEMPLATE)
        self.assertIn("PENDENTE (motivo)", texto)
        self.assertIn("`layers:`", texto)
        self.assertNotIn("`sql` · `edge` · `front`", texto)

    def test_fragmento_llm_tem_as_5_partes(self):
        texto = ler(RAIZ / "sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md")
        for parte in ("## Inventário executado", "## Detalhe por prompt", "## Drift", "## Versionamento", "## Rollback"):
            self.assertIn(parte, texto)

    def test_config_tem_o_slot_sob_evidence(self):
        texto = ler(RAIZ / "sdd/config.example.yaml")
        self.assertRegex(texto, r"(?m)^evidence:\n  require_avaliacao_layers: 2$")


if __name__ == "__main__":
    unittest.main()
