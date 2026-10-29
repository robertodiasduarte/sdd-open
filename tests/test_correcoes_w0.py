"""As 5 correções da W0: o que o texto do pacote promete existe e as checagens escritas disparam.

4.1 — o passo 4 da sdd-iterate roda `--print` (parse) e o gate sem `--print` (marcador ⇒ 5); os
comandos são lidos da própria skill e executados sobre as fixtures, então o texto antigo (só
`--print`, que é isento de marcador) fica vermelho aqui.
4.2–4.4 — nenhum arquivo do pacote (o que está no MANIFEST.txt) cita o que o pacote não tem
(contexto de domínio, `/drive`, o guard de git hook, passos e skills de outro SDD); 4.5 — o
avaliador fresco só grava `AVAL-*.log` em evidence/.
"""
from __future__ import annotations

import re
import unittest

from apoio import BASH, RAIZ, Sandbox

SKILLS = RAIZ / ".agents/skills"
ITERATE = SKILLS / "sdd-iterate/SKILL.md"
CONTEXTO_FRESCO = SKILLS / "sdd-build/references/contexto-fresco.md"
EVIDENCIA = RAIZ / "sdd/templates/fragments/EVIDENCIA.md"
TEMPLATE = RAIZ / "sdd/templates/BUILD_REPORT_TEMPLATE.md"
GATE = "sdd/bin/verify-gate.sh"
FIXTURE_CLARIFICAR = "sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md"
FIXTURE_CONTROLE = "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md"
# O que o pacote não tem: o contexto de domínio (volta na F12), a skill de drive (F14), o guard
# de git hook (F7) e passos/skills de outro SDD. Só conta o que vai no pacote (MANIFEST.txt):
# artefatos locais (sdd/features/, sdd/reviews/ …) ficam de fora.
PROMESSA_VAZIA = re.compile(
    r"build-report-guard|/drive|Step 1\.5|slice 2|CONTEXTO de domínio|/bug-pipeline|`/define` \(Step"
)
MANIFEST = RAIZ / "MANIFEST.txt"


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


def versao(p) -> str:
    return re.search(r'(?m)^\s+version: "([0-9.]+)"', ler(p)).group(1)


def passo_4_do_iterate() -> str:
    m = re.search(r"(?ms)^4\. \*\*Verify Gate\b.*?(?=^\d+\. \*\*)", ler(ITERATE))
    assert m, "passo 4 (Verify Gate) não achado na sdd-iterate"
    return m.group(0)


def chamadas_do_gate() -> list[str]:
    return re.findall(r"`(sdd/bin/verify-gate\.sh[^`]*<DEFINE>)`", passo_4_do_iterate())


class IterateVeClarificacaoAberta(Sandbox):
    """4.1: as chamadas que a skill manda rodar, rodadas de verdade, acusam o marcador."""

    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd", self.r)

    def roda_chamada(self, chamada: str, define: str) -> tuple[int, str]:
        argv = chamada.replace("<DEFINE>", define).split()
        rc, out, err = self.roda([BASH, *argv], self.r)
        return rc, out + err

    def test_versao(self):
        self.assertEqual(versao(ITERATE), "2.1.0")

    def test_passo_4_tem_as_duas_chamadas(self):
        chamadas = chamadas_do_gate()
        com_print = [c for c in chamadas if "--print" in c.split()]
        sem_print = [c for c in chamadas if "--print" not in c.split()]
        self.assertTrue(com_print, chamadas)
        self.assertTrue(sem_print, chamadas)
        self.assertLess(chamadas.index(com_print[0]), chamadas.index(sem_print[0]), chamadas)

    def test_fixture_de_clarificacao_da_0_com_print_e_5_sem(self):
        rc, out = self.roda_chamada(GATE + " --print <DEFINE>", FIXTURE_CLARIFICAR)
        self.assertEqual(rc, 0, out)
        rc, out = self.roda_chamada(GATE + " <DEFINE>", FIXTURE_CLARIFICAR)
        self.assertEqual(rc, 5, out)
        self.assertIn("RESULTADO: CLARIFICAR", out)

    def test_as_chamadas_da_skill_acusam_o_marcador(self):
        saidas = {c: self.roda_chamada(c, FIXTURE_CLARIFICAR)[0] for c in chamadas_do_gate()}
        self.assertIn(5, saidas.values(), saidas)
        for c, rc in saidas.items():
            if "--print" in c.split():
                self.assertEqual(rc, 0, c)

    def test_as_chamadas_da_skill_nao_acusam_sem_marcador(self):
        saidas = {c: self.roda_chamada(c, FIXTURE_CONTROLE)[0] for c in chamadas_do_gate()}
        self.assertTrue(saidas)
        self.assertNotIn(5, saidas.values(), saidas)

    def test_passo_4_explica_o_que_cada_exit_quer_dizer(self):
        passo = passo_4_do_iterate()
        self.assertIn("exit 5", passo)
        self.assertIn("64", passo)
        self.assertIn("isento de marcador", passo)
        # a 2ª chamada roda o cmd: smoke/eval (URL, custo) usam a busca do marcador, não o gate
        self.assertIn("smoke", passo)
        self.assertIn("CLARIFY.md", passo)


class PacoteNaoPrometeOQueNaoTem(unittest.TestCase):
    """4.2–4.4: o grep do Verify Gate da W0, sobre o que vai no pacote."""

    def test_grep_da_w0_sem_achado(self):
        achados = []
        arquivos = [l.strip() for l in ler(MANIFEST).splitlines() if l.strip()]
        self.assertIn(".agents/skills/sdd-iterate/SKILL.md", arquivos)
        for rel in arquivos:
            if rel == "tests/test_correcoes_w0.py":
                continue  # o próprio padrão
            try:
                texto = ler(RAIZ / rel)
            except UnicodeDecodeError:
                continue
            for n, linha in enumerate(texto.splitlines(), 1):
                if PROMESSA_VAZIA.search(linha):
                    achados.append(f"{rel}:{n}: {linha.strip()}")
        self.assertEqual(achados, [], "\n".join(achados))

    def test_evidencia_e_template_apontam_o_report_lint_que_existe(self):
        self.assertTrue((RAIZ / "sdd/bin/report-lint.py").is_file())
        cabecalho = ler(EVIDENCIA).split("## Por que existe", 1)[0]
        self.assertIn("`sdd/bin/report-lint.py`", cabecalho)
        aceite = ler(TEMPLATE).split("## Acceptance Test Verification", 1)[1].split("| ID |", 1)[0]
        self.assertIn("`sdd/bin/report-lint.py` consegue abrir", aceite)

    def test_evidencia_nao_descreve_hook_de_um_agente_so(self):
        texto = ler(EVIDENCIA)
        for termo in ("PreToolUse", "systemMessage", ".githooks/", "pelo hook", "o hook NEGA"):
            self.assertNotIn(termo, texto)


class AvaliadorFrescoSoGravaEvidencia(unittest.TestCase):
    """4.5: os dois briefs dizem a mesma coisa que o EVIDENCIA.md espera (`AVAL-*.log`)."""

    REGRA = re.compile(r"o único arquivo\s+que você grava de propósito, pelo shell, é\s+"
                       r"`sdd/reports/evidence/\{F\}/AVAL-\*\.log`")

    def test_versao_do_build(self):
        self.assertEqual(versao(SKILLS / "sdd-build/SKILL.md"), "2.2.0")

    def test_os_dois_briefs_permitem_so_o_log_aval(self):
        texto = ler(CONTEXTO_FRESCO)
        self.assertNotIn("Não escreva em arquivo algum", texto)
        for modo in ("contrato", "veredito"):
            with self.subTest(modo=modo):
                brief = texto.split(f"## Brief — modo `{modo}`", 1)[1].split("```text", 1)[1].split("```", 1)[0]
                self.assertRegex(brief, self.REGRA)
                self.assertIn("Não edite código nem documento do projeto", brief)

    def test_evidencia_espera_o_prefixo_aval(self):
        self.assertIn("AVAL-roteiro-3.log", ler(EVIDENCIA))
        self.assertIn("prefixo AVAL-", ler(EVIDENCIA))


if __name__ == "__main__":
    unittest.main()
