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
# forma mínima de um relatório que passa (F7): a tabela de critérios reconhecida e a linha do avaliador
AVALIADOR = "avaliador: N.A. (1 camada)\n\n"


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
        self.escreve(self.r, nome, "# BUILD REPORT\n\n" + AVALIADOR + CABECALHO + linhas)
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

    def test_declaracao_nega_mesmo_com_log_valido_na_celula(self):
        self.log("sdd/reports/evidence/EXEMPLO/AT-001.log")
        rc, out = self.lint("| AT-001 | soma | true | deve funcionar, ver `evidence/EXEMPLO/AT-001.log` |\n")
        self.assertEqual(rc, 1, out)

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


# timestamp montado em tempo de execução: 11+ dígitos seguidos reprovam no G2 do publish-gate
TS = "2026" + "1029" + "120000"
MIG = "supabase/migrations/" + TS + "_cliente_doc.sql"
ARQUIVOS = "## Files Created / Modified\n\n| # | Arquivo | Ação | Verificação |\n|---|---|---|---|\n"
APLICADAS = ("## Migrations aplicadas\n\n| Arquivo | Projeto (nome · ref) | Aplicada em | Prova por leitura |\n"
             "|---|---|---|---|\n")
PROJETO = "Curso Teste · `abcdefghijklmnopqrst`"
PROVA = "`evidence/EXEMPLO/MIG-001.log`"


class Migrations(Sandbox):
    """Migration listada nos arquivos do relatório só passa com a linha provada em `## Migrations aplicadas`."""

    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.escreve(self.r, "sdd/features/DEFINE_EXEMPLO.md",
                     "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n```\n")
        self.escreve(self.r, "sdd/reports/evidence/EXEMPLO/MIG-001.log",
                     "$ supabase migration list --linked\n " + TS + " | " + TS + " | 2026-10-29\n")

    def lint(self, arquivos: str, aplicadas: str | None = None) -> tuple[int, str]:
        texto = "# BUILD REPORT\n\n" + AVALIADOR + CABECALHO + "\n" + ARQUIVOS + arquivos + "\n"
        if aplicadas is not None:
            texto += APLICADAS + aplicadas
        self.escreve(self.r, REPORT, texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, REPORT], self.r)
        return rc, out + err

    def linha(self, caminho: str = MIG, projeto: str = PROJETO, data: str = "2026-10-29 14:32 (cli)",
              prova: str = PROVA) -> str:
        return "| `" + caminho + "` | " + projeto + " | " + data + " | " + prova + " |\n"

    def arquivo(self, caminho: str = MIG, acao: str = "Create") -> str:
        return "| 1 | `" + caminho + "` | " + acao + " | ok |\n"

    # ── passa ────────────────────────────────────────────────────────────────
    def test_migration_com_log_passa(self):
        rc, out = self.lint(self.arquivo(), self.linha())
        self.assertEqual(rc, 0, out)

    def test_recibo_vale_mesmo_com_gate_test(self):
        rc, out = self.lint(self.arquivo(), self.linha(prova="(b) entregue ao SQL Editor · recibo: Ana 2026-10-29"))
        self.assertEqual(rc, 0, out)

    def test_ja_aplicada_em_vale_como_data(self):
        rc, out = self.lint(self.arquivo(), self.linha(data="já aplicada em 2026-10-20"))
        self.assertEqual(rc, 0, out)

    def test_relatorio_sem_migration_nao_exige_a_secao(self):
        rc, out = self.lint(self.arquivo("src/app.py"))
        self.assertEqual(rc, 0, out)

    def test_migration_apagada_nao_exige_linha(self):
        rc, out = self.lint(self.arquivo(acao="Delete"))
        self.assertEqual(rc, 0, out)

    def test_sql_citado_fora_da_secao_de_arquivos_nao_conta(self):
        rc, out = self.lint(self.arquivo("src/app.py") + "\n## Issues Encountered\n\n| 1 | `" + MIG + "` | ok |\n")
        self.assertEqual(rc, 0, out)

    # ── reprova ──────────────────────────────────────────────────────────────
    def test_migration_sem_linha_reprova(self):
        rc, out = self.lint(self.arquivo(), self.linha("supabase/migrations/outra.sql"))
        self.assertEqual(rc, 1, out)
        self.assertIn(MIG, out)
        self.assertIn("aplicar-migration.md", out)

    def test_migration_sem_a_secao_reprova(self):
        rc, out = self.lint(self.arquivo())
        self.assertEqual(rc, 1, out)
        self.assertIn("sem linha em `## Migrations aplicadas`", out)

    def test_pasta_migrations_conta_como_migration(self):
        rc, out = self.lint(self.arquivo("db/migrations/0001_init.rb"))
        self.assertEqual(rc, 1, out)

    def test_prova_que_nao_prova_reprova(self):
        casos = {"vazia": "", "travessão": "—", "exit 0": "db push saiu exit 0",
                 "declaração": "deve funcionar", "log inexistente": "`evidence/EXEMPLO/MIG-009.log`",
                 "log de outra feature": "`evidence/OUTRA/MIG-001.log`"}
        for nome, prova in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.lint(self.arquivo(), self.linha(prova=prova))
                self.assertEqual(rc, 1, out)
                self.assertIn("migration `" + MIG + "`", out)

    def test_exit_0_reprova_mesmo_com_log_valido(self):
        rc, out = self.lint(self.arquivo(), self.linha(prova="exit 0 · " + PROVA))
        self.assertEqual(rc, 1, out)
        self.assertIn("exit 0 não prova migration", out)

    def test_log_sem_linha_de_comando_reprova(self):
        self.escreve(self.r, "sdd/reports/evidence/EXEMPLO/MIG-001.log", TS + " aplicada\n")
        rc, out = self.lint(self.arquivo(), self.linha())
        self.assertEqual(rc, 1, out)

    def test_projeto_sem_nome_e_ref_reprova(self):
        for projeto in ("Curso Teste", "`abcdefghijklmnopqrst`", " · `abcdefghijklmnopqrst`", ""):
            with self.subTest(projeto=projeto):
                rc, out = self.lint(self.arquivo(), self.linha(projeto=projeto))
                self.assertEqual(rc, 1, out)
                self.assertIn("nome · ref", out)

    def test_sem_data_reprova(self):
        rc, out = self.lint(self.arquivo(), self.linha(data="hoje (cli)"))
        self.assertEqual(rc, 1, out)
        self.assertIn("AAAA-MM-DD", out)

    def test_titulos_reais_numerados_ou_com_prefixo_contam(self):
        for titulo in ("## 2. Arquivos criados / modificados", "## Fase A — Files Created/Modified",
                       "## Files Changed", "## Arquivos do manifest"):
            with self.subTest(titulo=titulo):
                texto = ("# BUILD REPORT\n\n" + titulo + "\n\n| # | Arquivo | Ação |\n|---|---|---|\n"
                         "| 1 | `" + MIG + "` | Create |\n")
                self.escreve(self.r, REPORT, texto)
                rc, out, err = self.roda([PYTHON, "-B", SCRIPT, REPORT], self.r)
                self.assertEqual(rc, 1, out + err)
                self.assertIn(MIG, out + err)

    def test_projeto_so_com_travessoes_reprova(self):
        rc, out = self.lint(self.arquivo(), self.linha(projeto="— · —"))
        self.assertEqual(rc, 1, out)
        self.assertIn("nome · ref", out)

    # ── layers.sql do config ─────────────────────────────────────────────────
    def config(self, sql: str) -> None:
        self.escreve(self.r, "sdd/config.yaml",
                     "project:\n  name: x\nlayers:\n  api: \"\"\n  sql: " + sql + "  # camada de banco\n  ui: \"\"\n")

    def test_layers_sql_preenchido_conta_como_migration(self):
        self.config('"db/changes/**"')
        rc, out = self.lint(self.arquivo("db/changes/2026/add_doc.rb"))
        self.assertEqual(rc, 1, out)
        self.assertIn("db/changes/2026/add_doc.rb", out)

    def test_layers_sql_vazio_usa_so_o_glob_fixo(self):
        self.config('""')
        rc, out = self.lint(self.arquivo("db/changes/2026/add_doc.rb"))
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
