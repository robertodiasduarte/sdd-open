"""F19: o que o pacote diz e leva sobre o custo dos revisores (DEFINE_F19_CUSTO_REVISORES, AT-008 e AT-009).

Os dois scripts têm os próprios testes (tests/test_eval_revisores.py, tests/test_ledger_revisao_lint.py) e o
loop tem o dele (tests/test_fluxo.py). Aqui ficam o critério de dano, o molde do ledger, o texto das duas
skills que pedem o ledger, os documentos, os contratos e o caminho pelo `init`.
"""
from __future__ import annotations

import re
import unittest

from apoio import BASH, RAIZ, Sandbox

CLI = RAIZ / "bin/sdd-open.sh"
NOVOS = ("sdd/bin/eval-revisores.sh", "sdd/bin/ledger-revisao-lint.sh", "sdd/review/CRITERIO_DANO.md",
         "sdd/templates/LEDGER_REVISAO_TEMPLATE.md")
CABECALHO = "| achado | sev | veredito | rodada | evidência | dano | revisão |"
# Nome de engine é dado do registry.tsv, não texto de skill (P2): nenhuma destas palavras entra no texto novo.
ENGINES = re.compile(r"\b(claude|codex|gemini|openrouter|qwen|deepseek|glm)\b", re.I)


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def trecho(texto: str, inicio: str, fim: str) -> str:
    return texto.split(inicio, 1)[1].split(fim, 1)[0]


class Criterio(unittest.TestCase):
    def setUp(self):
        self.texto = ler("sdd/review/CRITERIO_DANO.md")

    def test_as_tres_condicoes_e_os_cinco_efeitos(self):
        for termo in ("**Foi aplicado.**", "**Há um teste que falha no código antigo.**", "`teste: <nome>`",
                      "**dado**", "**dinheiro**", "**acesso**", "**publicação**", "**disponibilidade**"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_os_tres_valores_quem_marca_e_o_falso_positivo(self):
        for termo in ("| `sim` |", "| `nao` |", "| `?` |", "`retroativo: sim`", "Nunca outro modelo",
                      "`REBATIDA_EVIDENCIA`", "`REBATIDA_ESCOPO` **não** é falso"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_exemplos_dos_dois_lados(self):
        exemplos = trecho(self.texto, "## Exemplos", "## Limites")
        self.assertGreaterEqual(exemplos.count("| `sim` |"), 2)
        self.assertGreaterEqual(exemplos.count("| `nao` |"), 3)


class Molde(Sandbox):
    def test_molde_tem_o_cabecalho_e_explica_as_regras(self):
        texto = ler("sdd/templates/LEDGER_REVISAO_TEMPLATE.md")
        self.assertIn(CABECALHO + "\n|---|---|---|---|---|---|---|", texto)
        for termo in ("copie o id do arquivo de vereditos", "sem achados: rodada=<N>", "retroativo: sim",
                      "sdd/review/CRITERIO_DANO.md", "sdd/bin/ledger-revisao-lint.sh"):
            with self.subTest(termo=termo):
                self.assertIn(termo, texto)

    def test_molde_preenchido_com_uma_linha_passa_no_lint(self):
        texto = ler("sdd/templates/LEDGER_REVISAO_TEMPLATE.md")
        linha = "| R1 | HIGH | APLICADA | rodada=1 | teste: `test_soma_do_mes` · x | sim | EXTERNAL_REVIEW_20260201-000001 |\n"
        preenchido = texto.replace("|---|---|---|---|---|---|---|\n", "|---|---|---|---|---|---|---|\n" + linha, 1)
        arq = self.escreve(self.tmp, "LEDGER_REVISAO_X.md", preenchido)
        rc, out, err = self.roda([BASH, RAIZ / "sdd/bin/ledger-revisao-lint.sh", arq], self.tmp)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("1 linha(s)", out)

    def test_molde_vazio_nao_e_verde(self):
        rc, out, err = self.roda([BASH, RAIZ / "sdd/bin/ledger-revisao-lint.sh",
                                  RAIZ / "sdd/templates/LEDGER_REVISAO_TEMPLATE.md"], self.tmp)
        self.assertEqual(rc, 64, out + err)


class Skills(unittest.TestCase):
    def test_build_5c_manda_gravar_conferir_e_passar_o_ledger(self):
        texto = ler(".agents/skills/sdd-build/SKILL.md")
        self.assertIn('version: "2.9.0"', texto)
        self.assertIn("`sdd-build v2.9.0 · nov/2026", texto)
        passo = trecho(texto, "**5c. Review adversarial pós-build.**", "**5d.")
        for termo in ("sdd/reviews/LEDGER_REVISAO_{F}.md", "sdd/templates/LEDGER_REVISAO_TEMPLATE.md",
                      "sdd/review/CRITERIO_DANO.md", "copiado do arquivo de vereditos", "`teste: <nome>`",
                      "sem achados: rodada=N", "bash sdd/bin/ledger-revisao-lint.sh sdd/reviews/LEDGER_REVISAO_{F}.md",
                      "--ledger\nsdd/reviews/LEDGER_REVISAO_{F}.md --rodada N", "bash sdd/bin/eval-revisores.sh"):
            with self.subTest(termo=termo):
                self.assertIn(termo, passo)
        self.assertEqual(ENGINES.findall(passo), [])
        # a ordem: gravar, conferir, depois o loop
        self.assertLess(passo.index("ledger-revisao-lint.sh"), passo.index("sdd-fluxo.sh loop"))

    def test_release_item_8_confere_o_lint_do_ledger(self):
        texto = ler(".agents/skills/sdd-release/SKILL.md")
        self.assertIn('version: "2.11.0"', texto)
        self.assertIn("`sdd-release v2.11.0 · nov/2026", texto)
        item = trecho(texto, "8. **Review externo (obrigatório, com dispensa registrada):**", "\n9. **Testes do diff:**")
        for termo in ("Com revisão feita (não dispensada)", "bash sdd/bin/ledger-revisao-lint.sh sdd/reviews/LEDGER_REVISAO_{F}.md",
                      "exit 2 ⇒ **abortar**", "exit 64", "sem achados: rodada=N"):
            with self.subTest(termo=termo):
                self.assertIn(termo, item)
        self.assertEqual(ENGINES.findall(item), [])

    def test_o_bloco_do_ok_nao_ganhou_rotulo(self):
        texto = ler(".agents/skills/sdd-release/SKILL.md")
        bloco = trecho(texto, "   ```markdown\n   **O que sobe:**", "   ```\n")
        self.assertNotIn("ledger da revisão", bloco.lower())
        self.assertEqual(bloco.count("?**"), 3)   # 2 rótulos que são afirmação + a pergunta única

    def test_molde_do_relatorio_aponta_o_ledger(self):
        secao = trecho(ler("sdd/templates/BUILD_REPORT_TEMPLATE.md"), "## Advisor Ledger", "\n## ")
        self.assertIn("**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_{FEATURE}.md`", secao)


class Documentos(unittest.TestCase):
    def test_secao_do_medidor_nos_dois_idiomas(self):
        casos = {
            "docs/adversarial-review.md": ("## eval-revisores", "## Limits", "It never calls an engine and\nnever uses the network",
                                           "Few rounds give unstable numbers", "never another model"),
            "docs/pt-BR/adversarial-review.md": ("## eval-revisores", "## Limites", "Nunca chama engine e nunca usa rede",
                                                 "Poucas\nrodadas dão número instável", "nunca outro modelo"),
        }
        for rel, (inicio, fim, rede, amostra, juiz) in casos.items():
            secao = trecho(ler(rel), inicio + "\n", fim + "\n")
            with self.subTest(doc=rel):
                for termo in ("bash sdd/bin/eval-revisores.sh", "bash sdd/bin/ledger-revisao-lint.sh", CABECALHO,
                              "sdd/reviews/LEDGER_REVISAO_{F}.md", "sdd/review/CRITERIO_DANO.md", "`pay-per-token`",
                              "n/d em N de M", "incerto em N de M", "trocada por outra engine", "fora da conta",
                              "`0` MEDIDO · `2` SEM DADOS", rede, amostra, juiz):
                    self.assertIn(termo, secao, termo)
                for coluna in ("Cobrança", "Pago US$", "Nominal US$", "Com dano", "Falsos positivos", "Sem classificar",
                               "Pago por dano", "AGREE"):
                    self.assertIn(coluna, secao, coluna)

    def test_cli_conventions_tem_as_duas_linhas(self):
        texto = ler("docs/cli-conventions.md")
        self.assertIn("| `eval-revisores.sh` | `0` MEDIDO · `2` SEM DADOS", texto)
        self.assertIn("| `ledger-revisao-lint.sh` | `0` ok · `2` violação (`arquivo:linha — motivo`) · `64` uso", texto)

    def test_o_pacote_ignora_o_que_a_suite_e_as_ferramentas_geram(self):
        # Sobra da F19 (F16, item 0d): sem .gitignore, `git add -A` depois da suíte sem -B levou .pyc e o trace
        # do gate para um commit. O arquivo é declarado no MANIFEST como qualquer outro (o publish-gate barra o resto).
        linhas = [ln for ln in ler(".gitignore").splitlines() if ln and not ln.startswith("#")]
        self.assertEqual(linhas, ["__pycache__/", "*.pyc", "sdd/reports/reviews/", "sdd/traces/"])
        self.assertIn(".gitignore", ler("MANIFEST.txt").splitlines())

    def test_contratos_e_manifest(self):
        contratos = ler("sdd/WORKFLOW_CONTRACTS.yaml")
        for termo in ("\nledger_revisao:\n", "\neval_revisores:\n", '  escreve: "nada"', '  rede: "nunca"',
                      '  rodada_sem_achados: "sem achados: rodada=<N> EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>"'):
            with self.subTest(termo=termo):
                self.assertIn(termo, contratos)
        manifest = ler("MANIFEST.txt").splitlines()
        esperados = list(NOVOS) + ["tests/test_eval_revisores.py", "tests/test_ledger_revisao_lint.py",
                                   "tests/test_f19_textos.py", "sdd/fixtures/fluxo/ledger-7-colunas.md"]
        esperados += [str(f.relative_to(RAIZ).as_posix()) for d in ("sdd/fixtures/revisao/custo", "sdd/fixtures/revisao/ledger")
                      for f in sorted((RAIZ / d).rglob("*")) if f.is_file()]
        self.assertEqual([e for e in esperados if e not in manifest], [])
        self.assertGreaterEqual(len(esperados), 35)


class NoProjeto(Sandbox):
    """AT-009: os arquivos chegam ao projeto pelo init e o medidor roda lá."""

    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        self.commit(self.p, "base")
        rc, out, err = self.roda([BASH, CLI, "init", "--vendors", "claude", "--yes"], self.p)
        self.assertEqual(rc, 0, out + err)

    def test_os_quatro_arquivos_chegam_iguais(self):
        for rel in NOVOS:
            with self.subTest(arquivo=rel):
                self.assertEqual((self.p / rel).read_bytes(), (RAIZ / rel).read_bytes())

    def test_medidor_sem_revisoes_e_sem_dados(self):
        rc, out, err = self.roda([BASH, self.p / "sdd/bin/eval-revisores.sh"], self.p)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("RESULTADO: SEM DADOS", out)

    def test_medidor_do_projeto_le_as_fixtures_que_o_init_trouxe(self):
        fx = self.p / "sdd/fixtures/revisao/custo"
        self.assertTrue((fx / "LEDGER_REVISAO_EXEMPLO.md").is_file(), "o init não trouxe as fixtures de custo")
        rc, out, err = self.roda([BASH, self.p / "sdd/bin/eval-revisores.sh", fx, "--ledgers", fx,
                                  "--registry", fx / "registry.tsv"], self.p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("| revisor | claude (claude-x) | assinatura | 6 |", out)

    def test_lint_do_projeto_confere_o_ledger_de_exemplo(self):
        rc, out, err = self.roda([BASH, self.p / "sdd/bin/ledger-revisao-lint.sh",
                                  self.p / "sdd/fixtures/revisao/custo/LEDGER_REVISAO_EXEMPLO.md"], self.p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("13 linha(s) e 1 rodada(s) sem achados", out)


if __name__ == "__main__":
    unittest.main()
