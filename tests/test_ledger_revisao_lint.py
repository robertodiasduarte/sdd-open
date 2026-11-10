"""sdd/bin/ledger-revisao-lint.sh — o ledger da revisão de 7 colunas (F19: AT-006).

Fixtures em sdd/fixtures/revisao/ledger/: `controle.md` e `retroativo.md` passam; cada uma das outras reprova
por 1 motivo, dito com arquivo:linha. Exit 0 ok · 2 violação · 64 uso, arquivo ilegível ou sem linha de dados.
"""
from __future__ import annotations

from apoio import BASH, RAIZ, Sandbox

LINT = RAIZ / "sdd/bin/ledger-revisao-lint.sh"
FX = RAIZ / "sdd/fixtures/revisao/ledger"
REPROVAM = {
    "sem-dano.md": "falta a célula `dano`",
    "sim-sem-teste.md": "dano = sim sem `teste: <nome>` na evidência",
    "sim-rebatida.md": "dano = sim com veredito REBATIDA_EVIDENCIA",
    "interrogacao-fora-de-retroativo.md": "dano = ? num ledger que não é retroativo",
    "veredito-invalido.md": "veredito `APLICADA em parte` fora de",
    "achado-repetido.md": "achado R1@claude repetido na revisão EXTERNAL_REVIEW_20260201-000001",
    "retroativo-mal-escrito.md": "a marca de retroativo é a linha `retroativo: sim`, sozinha",
}
CAB = "| achado | sev | veredito | rodada | evidência | dano | revisão |\n|---|---|---|---|---|---|---|\n"
PASTA = "EXTERNAL_REVIEW_20260201-000001"


class Lint(Sandbox):
    def lint(self, *args) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, LINT, *args], self.tmp)
        return rc, out + err

    def um(self, linha: str, topo: str = "") -> tuple[int, str]:
        return self.lint(self.escreve(self.tmp, "LEDGER_REVISAO_X.md", "# x\n\n" + topo + CAB + linha + "\n"))

    def test_controle_e_retroativo_passam(self):
        for nome, n in (("controle.md", 4), ("retroativo.md", 1), ("so-sem-achados.md", 0)):
            with self.subTest(fixture=nome):
                rc, out = self.lint(FX / nome)
                self.assertEqual(rc, 0, out)
                self.assertIn("%d linha(s) e " % n, out)
                self.assertIn(" em 1 arquivo(s)", out)
                self.assertIn("RESULTADO: VERDE\n→ ", out)

    def test_cada_fixture_reprova_pelo_seu_motivo(self):
        self.assertEqual(sorted(f.name for f in FX.glob("*.md")),
                         sorted(list(REPROVAM) + ["controle.md", "retroativo.md", "sem-linhas.md", "so-sem-achados.md"]))
        for nome, trecho in REPROVAM.items():
            with self.subTest(fixture=nome):
                rc, out = self.lint(FX / nome)
                self.assertEqual(rc, 2, out)
                self.assertIn(trecho, out)
                self.assertRegex(out, r"🛑 \S*" + nome.replace(".", r"\.") + r":\d+ — ")
                self.assertIn("RESULTADO: VERMELHO\n→ ", out)

    def test_varios_arquivos_um_ruim_reprova_o_conjunto(self):
        rc, out = self.lint(FX / "so-sem-achados.md", FX / "sim-sem-teste.md")
        self.assertEqual(rc, 2, out)
        self.assertNotIn("so-sem-achados.md:", out)
        self.assertEqual(out.count("🛑"), 1, out)

    def test_celulas_fora_do_formato(self):
        casos = {
            "achado fora do formato": ("| A1 | HIGH | APLICADA | rodada=1 | x | nao | %s |" % PASTA, "achado `A1` fora do formato"),
            "rótulo vazio": ("| R1@ | HIGH | APLICADA | rodada=1 | x | nao | %s |" % PASTA, "achado `R1@` fora do formato"),
            "severidade": ("| R1@a | ALTA | APLICADA | rodada=1 | x | nao | %s |" % PASTA, "severidade `ALTA`"),
            "rodada": ("| R1@a | HIGH | APLICADA | 1 | x | nao | %s |" % PASTA, "rodada `1` fora do formato"),
            "evidência vazia": ("| R1@a | HIGH | APLICADA | rodada=1 | — | nao | %s |" % PASTA, "evidência vazia"),
            "dano": ("| R1@a | HIGH | APLICADA | rodada=1 | x | talvez | %s |" % PASTA, "dano `talvez` fora de sim, nao, ?"),
            "pasta": ("| R1@a | HIGH | APLICADA | rodada=1 | x | nao | rodada-1 |", "não é uma pasta EXTERNAL_REVIEW_"),
            "8 células": ("| R1@a | HIGH | APLICADA | rodada=1 | a | b | nao | %s |" % PASTA, "tem 8 células"),
        }
        for nome, (linha, trecho) in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.um(linha)
                self.assertEqual(rc, 2, out)
                self.assertIn(trecho, out)

    def test_o_que_o_formato_aceita(self):
        casos = {
            "barra escapada": "| R1@a | LOW | REBATIDA_ESCOPO | rodada=1 | `a \\| b` | nao | %s |" % PASTA,
            "engine com slug": "| N2@openrouter:qwen/q-plus | MED | REBATIDA_EVIDENCIA | rodada=3a | medido | nao | %s |" % PASTA,
            "sem barra no fim": "| R1@a | LOW | APLICADA | rodada=1 | x | nao | %s" % PASTA,
            "sim com teste": "| R1@a | HIGH | APLICADA | rodada=1 | teste: `tests.test_x.Classe.test_y` · x | sim | %s |" % PASTA,
            "id sem rótulo": "| R1 | HIGH | APLICADA | rodada=1 | x | nao | %s |" % PASTA,
            "novo do auditor sem rótulo": "| N1 | HIGH | REBATIDA_EVIDENCIA | rodada=1 | medido | nao | %s |" % PASTA,
            "pasta com sufixo de colisão": "| R1 | LOW | APLICADA | rodada=1 | x | nao | %s-2 |" % PASTA,
            "Teste: com maiúscula": "| R1 | HIGH | APLICADA | rodada=1 | Teste: tests/test_x.py::test_y · x | sim | %s |" % PASTA,
            "teste em arquivo de outra linguagem": "| R1 | HIGH | APLICADA | rodada=1 | teste: `src/x.test.ts::soma` | sim | %s |" % PASTA,
        }
        for nome, linha in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.um(linha)
                self.assertEqual(rc, 0, out)

    def test_o_mesmo_achado_em_revisoes_diferentes_nao_e_repeticao(self):
        outra = PASTA[:-1] + "2"
        rc, out = self.um("| R1@a | LOW | APLICADA | rodada=1 | x | nao | %s |\n| R1@a | LOW | APLICADA | rodada=2 | y | nao | %s |"
                          % (PASTA, outra))
        self.assertEqual(rc, 0, out)

    def test_teste_citado_tem_de_ter_forma_de_teste(self):
        for evidencia in ("commit abc; o teste: falha", "sem teste: nenhum", "teste: sim"):
            with self.subTest(evidencia=evidencia):
                rc, out = self.um("| R1 | HIGH | APLICADA | rodada=1 | %s | sim | %s |" % (evidencia, PASTA))
                self.assertEqual(rc, 2, out)
                self.assertIn("dano = sim sem `teste: <nome>`", out)

    def test_retroativo_so_vale_como_linha_propria_e_fora_de_cerca(self):
        linha = "| R1@a | MED | APLICADA | rodada=1 | x | ? | %s |" % PASTA
        rc, out = self.um(linha, "retroativo: sim\n\n")
        self.assertEqual(rc, 0, out)
        rc, out = self.um(linha, "Este ledger não é retroativo: sim, é da frente atual.\n\n")
        self.assertEqual(rc, 2, out)
        self.assertIn("dano = ? num ledger que não é retroativo", out)
        rc, out = self.um(linha, "```text\nretroativo: sim\n```\n\n")
        self.assertEqual(rc, 2, out)
        for quase in ("> retroativo: sim", "**retroativo:** sim", "Retroativo: sim", "- retroativo: sim"):
            with self.subTest(quase=quase):
                rc, out = self.um(linha, quase + "\n\n")
                self.assertEqual(rc, 2, out)
                self.assertIn("a marca de retroativo é a linha `retroativo: sim`", out)

    def test_outra_tabela_e_bloco_cercado_nao_sao_conferidos(self):
        rc, out = self.um("| R1@a | LOW | APLICADA | rodada=1 | x | nao | %s |\n\n| Engine | Papel |\n|---|---|\n| a | revisor |"
                          "\n\n```markdown\n%s| R9 | exemplo cercado |\n```" % (PASTA, CAB))
        self.assertEqual(rc, 0, out)
        self.assertIn("1 linha(s)", out)

    def test_linhas_depois_de_linha_em_branco_continuam_sendo_o_ledger(self):
        # Quem grava "depois de cada rodada" separa as rodadas por uma linha em branco, sem repetir o cabeçalho.
        boa = "| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |" % PASTA
        rc, out = self.um(boa + "\n\n| R2 | HIGH | APLICADA | rodada=2 | sem a marca de dano |")
        self.assertEqual(rc, 2, out)
        self.assertIn("LEDGER_REVISAO_X.md:7 — a linha tem 5 célula(s)", out)
        rc, out = self.um(boa + "\n\n| R2 | HIGH | APLICADA | rodada=2 | o total somava duas vezes | sim | %s |" % PASTA)
        self.assertEqual(rc, 2, out)
        self.assertIn("dano = sim sem `teste: <nome>`", out)
        rc, out = self.um(boa + "\n\n| N1 | LOW | REBATIDA_ESCOPO | rodada=2 | fora | nao | %s |" % PASTA)
        self.assertEqual(rc, 0, out)
        self.assertIn("2 linha(s)", out)

    def test_arquivo_vazio_nao_esconde_as_violacoes_de_outro(self):
        rc, out = self.lint(FX / "sim-sem-teste.md", FX / "sem-linhas.md")
        self.assertEqual(rc, 2, out)
        self.assertIn("sim-sem-teste.md:5 — dano = sim sem `teste: <nome>`", out)
        self.assertIn("sem-linhas.md — nenhuma linha de dados", out)
        rc, out = self.um("Sem achados na rodada 2.")   # só a quase-forma, sem nenhuma linha válida
        self.assertEqual(rc, 2, out)
        self.assertIn("rodada sem achados se escreve `sem achados: rodada=<N>", out)

    def test_comentario_html_nao_e_conferido(self):
        # O molde traz as regras num comentário, com um exemplo de linha e a forma do `sem achados:`.
        topo = "<!--\n  R9 · exemplo\n  sem achados: rodada=<N> EXTERNAL_REVIEW_AAAAMMDD-HHMMSS\n  retroativo: sim\n-->\n\n"
        rc, out = self.um("| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |" % PASTA, topo)
        self.assertEqual(rc, 0, out)
        rc, out = self.um("| R1 | MED | APLICADA | rodada=1 | x | ? | %s |" % PASTA, topo)
        self.assertEqual(rc, 2, out)   # o `retroativo: sim` de dentro do comentário não libera o `?`

    def test_cabecalho_fora_do_molde_da_uma_mensagem_so(self):
        texto = ("# x\n\n| achado | severidade | veredito | rodada | motivo | dano | revisão |\n|--|:-:|---|---|---|---|---|\n"
                 "| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |\n" % PASTA)
        rc, out = self.lint(self.escreve(self.tmp, "LEDGER_REVISAO_X.md", texto))
        self.assertEqual(rc, 2, out)
        self.assertEqual(out.count("🛑"), 1, out)
        self.assertIn("o cabeçalho não é o do molde", out)

    def test_rodada_sem_achados(self):
        rc, out = self.um("| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |\n\nsem achados: rodada=2 %s" % (PASTA, PASTA[:-1] + "2"))
        self.assertEqual(rc, 0, out)
        self.assertIn("1 linha(s) e 1 rodada(s) sem achados", out)
        rc, out = self.um("| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |\n\nSem achados na rodada 2." % PASTA)
        self.assertEqual(rc, 2, out)
        self.assertIn("rodada sem achados se escreve `sem achados: rodada=<N> EXTERNAL_REVIEW_", out)

    def test_o_mesmo_achado_em_dois_arquivos_e_repeticao(self):
        linha = "# x\n\n" + CAB + "| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |\n" % PASTA
        a = self.escreve(self.tmp, "LEDGER_REVISAO_A.md", linha)
        b = self.escreve(self.tmp, "LEDGER_REVISAO_B.md", linha)
        rc, out = self.lint(a, b)
        self.assertEqual(rc, 2, out)
        self.assertIn("LEDGER_REVISAO_B.md:5 — achado R1 repetido", out)
        self.assertIn("LEDGER_REVISAO_A.md:5)", out)

    def test_arquivo_ilegivel_depois_nao_esconde_nada(self):
        # Os caminhos são lidos antes de conferir: o 64 sai sem conferir pela metade.
        rc, out = self.lint(FX / "sim-sem-teste.md", self.tmp / "nada.md")
        self.assertEqual(rc, 64, out)
        self.assertIn("não consegui ler", out)
        self.assertNotIn("RESULTADO: VERMELHO", out)

    def test_uso_e_64(self):
        casos = {
            "sem argumento": ((), "faltou o arquivo"),
            "opção": (("--fix",), "opção desconhecida"),
            "inexistente": ((self.tmp / "nada.md",), "não consegui ler"),
            "sem linha de dados": ((FX / "sem-linhas.md",), "nada conferido nunca é verde"),
            "só outra tabela": ((self.escreve(self.tmp, "o.md", "| Engine | Papel |\n|---|---|\n| a | b |\n"),), "nada conferido nunca é verde"),
        }
        for nome, (args, trecho) in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.lint(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn(trecho, out)
                self.assertIn("RESULTADO: ERRO DE USO\n→ ", out)

    def test_ajuda(self):
        rc, out = self.lint("--help")
        self.assertEqual(rc, 0, out)
        self.assertIn("0 ok · 2 violação", out)


if __name__ == "__main__":
    import unittest
    unittest.main()
