"""Contrato de evidência do sdd/bin/report-lint.py: todo `true` aponta para algo que abre.

Exit 0 = todo critério verdadeiro tem evidência · 1 = violação · 64 = uso. O contrato completo está
em sdd/templates/fragments/EVIDENCIA.md.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, Sandbox

SCRIPT = "sdd/bin/report-lint.py"
REPORT = "sdd/reports/BUILD_REPORT_EXEMPLO.md"
CABECALHO = "| AT | Critério | Resultado | Evidência |\n|---|---|---|---|\n"


class ReportLint(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.kind("test")

    def kind(self, kind: str) -> None:
        self.escreve(self.r, "sdd/features/DEFINE_EXEMPLO.md",
                     "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: " + kind + "\n```\n")

    def log(self, rel: str, texto: str = "$ npm test\nok 3 testes\n") -> None:
        self.escreve(self.r, rel, texto)

    def lint(self, linhas: str, nome: str = REPORT) -> tuple[int, str]:
        self.escreve(self.r, nome, "# BUILD REPORT\n\n" + CABECALHO + linhas)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, nome], self.r)
        return rc, out + err

    # ── evidência válida ─────────────────────────────────────────────────────
    def test_log_capturado_da_feature_passa(self):
        self.log("sdd/reports/evidence/EXEMPLO/AT-001.log")
        rc, out = self.lint("| AT-001 | soma | true | `evidence/EXEMPLO/AT-001.log` |\n")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_avaliacao_em_contexto_fresco_passa(self):
        self.escreve(self.r, "sdd/reviews/AVALIACAO_EXEMPLO_20261029.md", "Veredito: PASS\n")
        rc, out = self.lint("| AT-001 | soma | ✅ | `AVALIACAO_EXEMPLO_20261029.md` |\n")
        self.assertEqual(rc, 0, out)

    def test_recibo_humano_em_gate_manual_ux_passa(self):
        self.kind("manual-ux")
        rc, out = self.lint("| AT-001 | tela | true | recibo: Ana 2026-10-29 |\n")
        self.assertEqual(rc, 0, out)

    def test_criterio_false_nao_exige_evidencia(self):
        rc, out = self.lint("| AT-001 | soma | false | — |\n")
        self.assertEqual(rc, 0, out)

    # ── evidência negada ─────────────────────────────────────────────────────
    def test_declaracao_nao_e_prova(self):
        for frase in ("deve funcionar", "✅ por raciocínio", "provavelmente ok"):
            with self.subTest(frase=frase):
                rc, out = self.lint("| AT-001 | soma | true | " + frase + " |\n")
                self.assertEqual(rc, 1, out)
                self.assertIn("RESULTADO: VERMELHO", out)

    def test_arquivo_inexistente(self):
        rc, out = self.lint("| AT-001 | soma | true | `evidence/EXEMPLO/AT-009.log` |\n")
        self.assertEqual(rc, 1, out)

    def test_log_vazio(self):
        self.log("sdd/reports/evidence/EXEMPLO/AT-001.log", "")
        rc, out = self.lint("| AT-001 | soma | true | `evidence/EXEMPLO/AT-001.log` |\n")
        self.assertEqual(rc, 1, out)

    def test_log_sem_linha_de_comando(self):
        self.log("sdd/reports/evidence/EXEMPLO/AT-001.log", "ok 3 testes\n")
        rc, out = self.lint("| AT-001 | soma | true | `evidence/EXEMPLO/AT-001.log` |\n")
        self.assertEqual(rc, 1, out)

    def test_log_de_outra_feature(self):
        self.log("sdd/reports/evidence/OUTRA/AT-001.log")
        rc, out = self.lint("| AT-001 | soma | true | `evidence/OUTRA/AT-001.log` |\n")
        self.assertEqual(rc, 1, out)

    def test_recibo_fora_de_manual_ux(self):
        rc, out = self.lint("| AT-001 | soma | true | recibo: Ana 2026-10-29 |\n")
        self.assertEqual(rc, 1, out)

    def test_veredito_do_avaliador_sem_arquivo(self):
        rc, out = self.lint("| AT-001 | soma | false | — |\n\n**Veredito do avaliador:** PASS `AVALIACAO_EXEMPLO_1.md`\n")
        self.assertEqual(rc, 1, out)

    # ── uso ──────────────────────────────────────────────────────────────────
    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.r)
        self.assertEqual(rc, 64, out + err)

    def test_nome_fora_do_padrao_e_64(self):
        rc, out = self.lint("| AT-001 | soma | false | — |\n", nome="sdd/reports/relatorio.md")
        self.assertEqual(rc, 64, out)


if __name__ == "__main__":
    unittest.main()
