"""Regras fail-closed do sdd/bin/report-lint.py (F7): tabela reconhecida, existência da avaliação,
camadas, declaração com motivo, PENDENTE, evidência ignorada pelo git, veredito fora de bloco
cercado e --stdin. Os 32 contratos anteriores ficam em tests/test_report_lint.py.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = "sdd/bin/report-lint.py"
FIXTURES = RAIZ / "sdd/fixtures/evidencia"
TAB = "| ID | Critério | Resultado | Evidência |\n|---|---|---|---|\n"
TS = "2026" + "1030" + "-1200"  # montado em execução: 11+ dígitos seguidos reprovam no G2 do publish-gate
LOG = "$ npm test\nok 3 testes\n[exit=0]\n"


class Base(Sandbox):
    FEATURE = "EXEMPLO"

    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.escreve(self.r, "sdd/features/DEFINE_%s.md" % self.FEATURE,
                     "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n```\n")

    def lint(self, texto: str, feature: str | None = None, *extra: str) -> tuple[int, str]:
        nome = "sdd/reports/BUILD_REPORT_%s.md" % (feature or self.FEATURE)
        self.escreve(self.r, nome, texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, *extra, nome], self.r)
        return rc, out + err

    def avaliacao(self, nome: str, texto: str = "<<<AVALIACAO\nVEREDITO: PASS\n>>>\n") -> None:
        self.escreve(self.r, "sdd/reviews/" + nome, texto)

    def config(self, layers: str, evidence: str = "") -> None:
        self.escreve(self.r, "sdd/config.yaml", "project:\n  name: x\nlayers:\n" + layers + evidence)

    def design(self, *caminhos: str) -> None:
        linhas = "".join("| %d | `%s` | Create | x | (general) | None |\n" % (i + 1, c) for i, c in enumerate(caminhos))
        self.escreve(self.r, "sdd/features/DESIGN_%s.md" % self.FEATURE,
                     "# DESIGN\n\n## File Manifest\n\n| # | File | Action | Purpose | Agent | Dependencies |\n"
                     "|---|---|---|---|---|---|\n" + linhas + "\n**Total Files:** %d\n\n## Code Patterns\n" % len(caminhos))

    def relatorio(self, extra: str = "", tabela: str = TAB) -> str:
        return "# BUILD REPORT\n\n" + tabela + "| AT-001 | x | false | — |\n\n" + extra


class Tabela(Base):
    def test_sem_tabela_reprova(self):
        rc, out = self.lint("# BUILD REPORT\n\navaliador: N.A. (1 camada)\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("[tabela]", out)
        self.assertIn("| ID | Critério | Resultado | Evidência |", out)
        self.assertResultado(out)

    def test_cabecalho_em_ingles_e_conferido(self):
        tabela = "| ID | Criterion | Result | Evidence |\n|---|---|---|---|\n"
        rc, out = self.lint("# R\n\n" + tabela + "| AT-001 | x | true | — |\n\navaliador: N.A. (1 camada)\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("AT-001", out)
        self.escreve(self.r, "sdd/reports/evidence/EXEMPLO/AT-001.log", LOG)
        rc, out = self.lint("# R\n\n" + tabela + "| AT-001 | x | true | `evidence/EXEMPLO/AT-001.log` |\n\n"
                            "avaliador: N.A. (1 camada)\n")
        self.assertEqual(rc, 0, out)


class Existencia(Base):
    def test_sem_avaliacao_reprova_com_as_tres_saidas(self):
        rc, out = self.lint(self.relatorio())
        self.assertEqual(rc, 1, out)
        self.assertIn("[avaliação ausente]", out)
        for trecho in ("rode o avaliador", "avaliador: N.A. (<motivo>)", "avaliador: PENDENTE (<motivo>)"):
            self.assertIn(trecho, out)
        self.assertNotIn("produza `evidence/", out)  # o conserto é o da classe, não o de evidência

    def test_avaliacao_existente_prova_sem_ser_citada(self):
        self.avaliacao("AVALIACAO_EXEMPLO_" + TS + ".md")
        rc, out = self.lint(self.relatorio())
        self.assertEqual(rc, 0, out)

    def test_avaliacao_vazia_nao_prova(self):
        self.avaliacao("AVALIACAO_EXEMPLO_" + TS + ".md", "")
        rc, out = self.lint(self.relatorio())
        self.assertEqual(rc, 1, out)

    def test_avaliacao_de_slice_nao_prova_a_familia(self):
        self.avaliacao("AVALIACAO_EXEMPLO_S2_" + TS + ".md")
        rc, out = self.lint(self.relatorio())
        self.assertEqual(rc, 1, out)
        self.assertIn("[avaliação ausente]", out)

    def test_avaliacao_ignorada_pelo_git_nao_prova(self):
        self.avaliacao("AVALIACAO_EXEMPLO_" + TS + ".md")
        self.escreve(self.r, ".gitignore", "sdd/reviews/\n")
        rc, out = self.lint(self.relatorio())
        self.assertEqual(rc, 1, out)
        self.assertIn("IGNORA", out)
        self.assertIn("git add -f", out)

    def test_na_com_uma_camada_passa(self):
        self.config('  api: "src/api/**"\n  ui: "src/ui/**"\n')
        self.design("src/api/conta.py", "tests/test_conta.py")
        rc, out = self.lint(self.relatorio("avaliador: N.A. (1 camada)\n"))
        self.assertEqual(rc, 0, out)

    def test_na_com_duas_camadas_reprova(self):
        self.config('  api: "src/api/**"\n  ui: "src/ui/**"\n')
        self.design("src/api/conta.py", "src/ui/tela.js")
        rc, out = self.lint(self.relatorio("avaliador: N.A. (é pequeno)\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("[declaração]", out)
        self.assertIn("toca 2 camadas (api, ui)", out)

    def test_na_no_formato_do_template_tambem_e_conferido(self):
        self.config('  api: "src/api/**"\n  ui: "src/ui/**"\n')
        self.design("src/api/conta.py", "src/ui/tela.js")
        rc, out = self.lint(self.relatorio("**Veredito do avaliador (C1):** N.A. (1 camada) · ciclos: 0\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("toca 2 camadas", out)

    def test_limite_1_reprova_uma_camada(self):
        self.config('  api: "src/api/**"\n', "evidence:\n  require_avaliacao_layers: 1\n")
        self.design("src/api/conta.py")
        rc, out = self.lint(self.relatorio("avaliador: N.A. (1 camada)\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("o limite é 1", out)

    def test_limite_invalido_vira_2_com_aviso(self):
        self.config('  api: "src/api/**"\n', "evidence:\n  require_avaliacao_layers: dois\n")
        self.design("src/api/conta.py")
        rc, out = self.lint(self.relatorio("avaliador: N.A. (1 camada)\n"))
        self.assertEqual(rc, 0, out)
        self.assertIn("não é inteiro", out)

    def test_contagem_impossivel_aceita_com_aviso(self):
        rc, out = self.lint(self.relatorio("avaliador: N.A. (1 camada)\n"))
        self.assertEqual(rc, 0, out)
        self.assertIn("N.A. aceito sem conferir camadas", out)
        self.assertIn("preencha `layers:`", out)

    def test_declaracao_sem_motivo_reprova(self):
        for linha in ("avaliador: N.A.\n", "avaliador: PENDENTE ()\n"):
            with self.subTest(linha=linha):
                rc, out = self.lint(self.relatorio(linha))
                self.assertEqual(rc, 1, out)
                self.assertIn("[declaração]", out)
                self.assertIn("sem motivo", out)

    def test_prosa_nao_vira_declaracao(self):
        rc, out = self.lint(self.relatorio("O avaliador na rodada 1 achou 2 notas; avaliador pendente de recibo.\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("[avaliação ausente]", out)

    def test_declaracao_dentro_de_bloco_cercado_nao_vale(self):
        rc, out = self.lint(self.relatorio("```text\navaliador: N.A. (1 camada)\n```\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("[avaliação ausente]", out)


class Pendente(Base):
    def test_pendente_passa_no_modo_comum_com_aviso(self):
        rc, out = self.lint(self.relatorio("avaliador: PENDENTE (o build travou no gate)\n"))
        self.assertEqual(rc, 0, out)
        self.assertIn("a release não sai enquanto esta linha existir", out)
        self.assertIn("troque a linha pelo veredito", out)

    def test_modo_pendente_lista_e_sai_1(self):
        texto = self.relatorio("avaliador: PENDENTE (o build travou no gate)\n")
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_EXEMPLO.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--pendente", "sdd/reports/BUILD_REPORT_EXEMPLO.md"], self.r)
        self.assertEqual(rc, 1, out + err)
        linha = texto.splitlines().index("avaliador: PENDENTE (o build travou no gate)") + 1
        self.assertIn("sdd/reports/BUILD_REPORT_EXEMPLO.md:%d: PENDENTE (o build travou no gate)" % linha, out)
        self.assertResultado(out)

    def test_modo_pendente_sem_pendente_sai_0(self):
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_EXEMPLO.md", self.relatorio("avaliador: N.A. (1 camada)\n"))
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--pendente", "sdd/reports/BUILD_REPORT_EXEMPLO.md"], self.r)
        self.assertEqual(rc, 0, out + err)

    def test_modo_pendente_ignora_bloco_cercado(self):
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_EXEMPLO.md",
                     self.relatorio("```\navaliador: PENDENTE (exemplo de um ciclo antigo)\n```\navaliador: N.A. (1 camada)\n"))
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--pendente", "sdd/reports/BUILD_REPORT_EXEMPLO.md"], self.r)
        self.assertEqual(rc, 0, out + err)

    def test_modo_pendente_uso(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--pendente"], self.r)
        self.assertEqual(rc, 64, out + err)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--pendente", "sdd/reports/BUILD_REPORT_NAO.md"], self.r)
        self.assertEqual(rc, 64, out + err)


class EvidenciaIgnorada(Base):
    def test_log_ignorado_pelo_git_reprova(self):
        self.escreve(self.r, "sdd/reports/evidence/EXEMPLO/AT-001.log", LOG)
        self.escreve(self.r, ".gitignore", "sdd/reports/evidence/\n")
        rc, out = self.lint("# R\n\n" + TAB + "| AT-001 | x | true | `evidence/EXEMPLO/AT-001.log` |\n\n"
                            "avaliador: N.A. (1 camada)\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("o git o IGNORA", out)

    def test_avaliacao_citada_e_ignorada_reprova(self):
        self.avaliacao("AVALIACAO_EXEMPLO_" + TS + ".md")
        self.escreve(self.r, ".git/info/exclude", "sdd/reviews/\n")
        rc, out = self.lint("# R\n\n" + TAB + "| AT-001 | x | true | `AVALIACAO_EXEMPLO_" + TS + ".md` |\n\n"
                            "avaliador: N.A. (1 camada)\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("IGNORA", out)


class Veredito(Base):
    def setUp(self):
        super().setUp()
        self.nome = "AVALIACAO_EXEMPLO_" + TS + ".md"

    def test_veredito_em_titulo_sem_avaliacao_reprova(self):
        rc, out = self.lint(self.relatorio("## Veredito do avaliador (C1)\n\n**PASS** · ciclos: 1\n\navaliador: N.A. (x)\n"))
        self.assertEqual(rc, 1, out)
        self.assertIn("Veredito do avaliador `PASS`", out)

    def test_veredito_em_titulo_com_avaliacao_no_paragrafo_seguinte_passa(self):
        self.avaliacao(self.nome)
        rc, out = self.lint(self.relatorio("## Veredito do avaliador (C1) — ciclo 2\n\n**PASS** · `" + self.nome + "`\n"))
        self.assertEqual(rc, 0, out)

    def test_veredito_em_tabela(self):
        tabela = "| Item | Valor |\n|---|---|\n| **Veredito do avaliador (C1)** | NEEDS_WORK |\n"
        rc, out = self.lint(self.relatorio(tabela + "\navaliador: N.A. (x)\n"))
        self.assertEqual(rc, 1, out)
        self.avaliacao(self.nome)
        rc, out = self.lint(self.relatorio(tabela + "| Relatório | `" + self.nome + "` |\n"))
        self.assertEqual(rc, 1, out)  # numa tabela, a unidade é a linha do rótulo
        linha = "| **Veredito do avaliador (C1)** | NEEDS_WORK · `" + self.nome + "` |\n"
        rc, out = self.lint(self.relatorio("| Item | Valor |\n|---|---|\n" + linha))
        self.assertEqual(rc, 0, out)

    def test_rotulos_em_negrito_e_em_tabela_sem_c1(self):
        self.avaliacao("AVALIACAO_EXEMPLO_" + TS + "-ciclo1.md")  # avaliação antiga: a existência passa
        for texto in ("**Veredito do avaliador**: PASS · ciclos: 2\n",
                      "| Item | Valor |\n|---|---|\n| Veredito do avaliador | PASS |\n"):
            with self.subTest(texto=texto):
                rc, out = self.lint(self.relatorio(texto))
                self.assertEqual(rc, 1, out)
                self.assertIn("Veredito do avaliador `PASS`", out)

    def test_rotulos_sem_c1(self):
        for texto in ("Veredito do avaliador: PASS · ciclos: 1\n", "## Veredito do avaliador\n\n**PASS**\n"):
            with self.subTest(texto=texto):
                rc, out = self.lint(self.relatorio(texto + "\navaliador: N.A. (x)\n"))
                self.assertEqual(rc, 1, out)
                self.assertIn("Veredito do avaliador `PASS`", out)

    def test_avaliacao_em_outro_paragrafo_nao_conta(self):
        self.avaliacao(self.nome)
        rc, out = self.lint(self.relatorio("**Veredito do avaliador (C1):** PASS · ciclos: 1\n\n"
                                           "Ver também `" + self.nome + "`.\n"))
        self.assertEqual(rc, 1, out)

    def test_veredito_citado_em_bloco_cercado_nao_vira_exigencia(self):
        rc, out = self.lint(self.relatorio("```text\n**Veredito do avaliador (C1):** PASS\n```\n\navaliador: N.A. (1 camada)\n"))
        self.assertEqual(rc, 0, out)


class Stdin(Base):
    def test_stdin_confere_como_o_arquivo(self):
        texto = self.relatorio()
        import subprocess
        p = subprocess.run([PYTHON, "-B", SCRIPT, "--stdin", "sdd/reports/BUILD_REPORT_EXEMPLO.md"], cwd=str(self.r),
                           env=self.env, input=texto, capture_output=True, encoding="utf-8", timeout=60)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("[avaliação ausente]", p.stderr)
        p = subprocess.run([PYTHON, "-B", SCRIPT, "--stdin", "sdd/reports/BUILD_REPORT_EXEMPLO.md"], cwd=str(self.r),
                           env=self.env, input=texto + "avaliador: N.A. (1 camada)\n", capture_output=True,
                           encoding="utf-8", timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_stdin_com_nome_errado_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--stdin", "relatorio.md"], self.r)
        self.assertEqual(rc, 64, out + err)


class Fixtures(Sandbox):
    """As 4 fixtures do pacote: reprovam (ou passam) pelo motivo certo."""

    def prepara(self, feature: str) -> object:
        r = self.repo(feature)
        self.copia(SCRIPT, r)
        (r / "sdd/reports").mkdir(parents=True)
        destino = r / ("sdd/reports/BUILD_REPORT_%s.md" % feature)
        destino.write_text((FIXTURES / ("BUILD_REPORT_%s.md" % feature)).read_text(encoding="utf-8"), encoding="utf-8")
        self.escreve(r, "sdd/reports/evidence/%s/AT-001.log" % feature, LOG)
        return r

    def lint(self, r, feature: str, *extra: str) -> tuple[int, str]:
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, *extra, "sdd/reports/BUILD_REPORT_%s.md" % feature], r)
        return rc, out + err

    def test_controle_passa(self):
        r = self.prepara("controle")
        self.escreve(r, "sdd/reviews/AVALIACAO_controle_" + TS + ".md", "<<<AVALIACAO\nVEREDITO: PASS\n>>>\n")
        rc, out = self.lint(r, "controle")
        self.assertEqual(rc, 0, out)

    def test_sem_avaliacao_reprova(self):
        r = self.prepara("sem_avaliacao")
        rc, out = self.lint(r, "sem_avaliacao")
        self.assertEqual(rc, 1, out)
        self.assertIn("[avaliação ausente]", out)

    def test_pendente_reprova_no_modo_pendente(self):
        r = self.prepara("pendente")
        rc, out = self.lint(r, "pendente")
        self.assertEqual(rc, 0, out)
        rc, out = self.lint(r, "pendente", "--pendente")
        self.assertEqual(rc, 1, out)
        self.assertIn(": PENDENTE (o build travou no Verify Gate", out)

    def test_evidencia_ignorada_reprova(self):
        r = self.prepara("evidencia_ignorada")
        rc, out = self.lint(r, "evidencia_ignorada")
        self.assertEqual(rc, 0, out)  # o lado verde: sem a regra de ignore, a mesma fixture passa
        self.escreve(r, ".gitignore", "sdd/reports/evidence/evidencia_ignorada/\n")
        rc, out = self.lint(r, "evidencia_ignorada")
        self.assertEqual(rc, 1, out)
        self.assertIn("o git o IGNORA", out)


class Saida(Base):
    def test_uma_seta_por_classe(self):
        rc, out = self.lint("# BUILD REPORT\n\nnada aqui\n")
        self.assertEqual(rc, 1, out)
        setas = [l for l in out.splitlines() if l.startswith("→ ")]
        self.assertEqual(len(setas), 2, out)  # [tabela] e [avaliação ausente]
        self.assertTrue(out.index("[tabela]") < out.index("[avaliação ausente]"))


if __name__ == "__main__":
    unittest.main()
