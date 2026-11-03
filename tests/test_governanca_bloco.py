"""sdd/bin/governanca-bloco.py (F12, C8): o bloco <<<GOVERNANCA que o revisor fresco devolve ao passo 11.

DEFINE F12 AT-026: 0 válido (NA, REVISADO, PADRAO_AUSENTE), 1 FALHA, 2 inválido em cada forma de
ilegível ou incoerente com o relatório e a fronteira, 64 uso.
"""
from __future__ import annotations

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = str(RAIZ / "sdd/bin/governanca-bloco.py")
RELATORIO = """# GOVERNANCA REVIEW: X

**Cobertura:** 12 itens: 8 já cobertos · 2 lacunas · 2 N.A. · 0 na 2ª camada

## Lacunas

### G01 — Lançamento que não se apaga

texto

### G05 — Trilha de auditoria

texto

## Já cobertos
"""


def revisado(lacunas=("G01 | alta | AT-003\nmuda: m\nporque: p", "G05 | média | —\nmuda: m\nporque: p"),
             relatorio="SAIDA") -> str:
    corpo = "".join("lacuna: " + l + "\n" for l in lacunas)
    return ("bla bla\n<<<GOVERNANCA\nresultado: REVISADO\nmotivo: achei 2 lacunas\nrelatorio: " + relatorio +
            "\ncobertura: 12 itens\n" + corpo + ">>>\n")


class Bloco(Sandbox):
    def setUp(self):
        super().setUp()
        self.saida = self.escreve(self.tmp, "sdd/reviews/GOVERNANCA_REVIEW_X.md", RELATORIO)
        self.mudou = self.escreve(self.tmp, "comparar-mudou.txt", "MUDOU: " + str(self.saida) + "\nRESULTADO: x\n")
        self.nada = self.escreve(self.tmp, "comparar-nada.txt", "RESULTADO: x\n")

    def bloco(self, resposta: str, *extra: str) -> tuple[int, str]:
        r = self.escreve(self.tmp, "resp.txt", resposta.replace("SAIDA", str(self.saida)))
        rc, out, err = self.roda([PYTHON, SCRIPT, str(r), "--saida", str(self.saida), *extra], self.tmp)
        return rc, out + err

    def test_validos(self):
        casos = {
            "revisado": (revisado(), ("--comparar", str(self.mudou)), "RESULTADO: REVISADO"),
            "na": ("<<<GOVERNANCA\nresultado: NA\nmotivo: sem tema\nrelatorio: —\ncobertura: —\n>>>",
                   ("--comparar", str(self.nada)), "RESULTADO: NA"),
            "padrao ausente": ("<<<GOVERNANCA\nresultado: PADRAO_AUSENTE\nmotivo: achei tributo, sem padrão\nrelatorio: —\n>>>",
                               (), "RESULTADO: PADRAO_AUSENTE"),
        }
        for nome, (resp, extra, esperado) in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.bloco(resp, *extra)
                self.assertEqual(rc, 0, out)
                self.assertIn(esperado, out)

    def test_falha_sai_1(self):
        rc, out = self.bloco("<<<GOVERNANCA\nresultado: FALHA\nmotivo: DEFINE ilegível\nrelatorio: —\n>>>")
        self.assertEqual(rc, 1, out)
        self.assertIn("RESULTADO: FALHA", out)

    def test_invalidos_saem_2(self):
        casos = {
            "sem o par": "resultado: NA\nmotivo: x\n",
            "resultado fora da lista": "<<<GOVERNANCA\nresultado: OK\nmotivo: x\nrelatorio: —\n>>>",
            "lacuna sem os 3 campos": revisado(lacunas=("G01 | alta\nmuda: m\nporque: p", "G05 | média | —\nmuda: m\nporque: p")),
            "lacuna sem muda/porque": revisado(lacunas=("G01 | alta | AT-003\nporque: p", "G05 | média | —\nmuda: m\nporque: p")),
            "relatorio diferente do saida": revisado(relatorio="/outro/caminho.md"),
            "gnn não bate com o relatório": revisado(lacunas=("G01 | alta | AT-003\nmuda: m\nporque: p",)),
"lacuna repetida": revisado(lacunas=("G01 | alta | AT-003\nmuda: m\nporque: p", "G01 | alta | AT-003\nmuda: m\nporque: p",
                                                "G05 | média | —\nmuda: m\nporque: p")),
            "NA com relatorio preenchido": "<<<GOVERNANCA\nresultado: NA\nmotivo: x\nrelatorio: SAIDA\n>>>",
        }
        for nome, resp in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.bloco(resp)
                self.assertEqual(rc, 2, out)
                self.assertIn("RESULTADO: BLOCO INVÁLIDO", out)

    def test_bloco_incoerente_com_a_fronteira_sai_2(self):
        rc, out = self.bloco(revisado(), "--comparar", str(self.nada))
        self.assertEqual(rc, 2, out)
        self.assertIn("não mostra MUDOU", out)
        rc, out = self.bloco("<<<GOVERNANCA\nresultado: NA\nmotivo: x\nrelatorio: —\n>>>", "--comparar", str(self.mudou))
        self.assertEqual(rc, 2, out)
        self.assertIn("gravou o relatório", out)

    def test_vale_o_ultimo_bloco(self):
        rc, out = self.bloco("<<<GOVERNANCA\nresultado: OK\n>>>\nrevi de novo\n" + revisado(), "--comparar", str(self.mudou))
        self.assertEqual(rc, 0, out)

    def test_uso_sai_64(self):
        r = self.escreve(self.tmp, "r.txt", "x")
        for args in ((), (str(r),), (str(r), "--saida"), (str(self.tmp / "nao.txt"), "--saida", "x"),
                     (str(r), "--saida", "x", "--comparar", str(self.tmp / "nao.txt"))):
            with self.subTest(args=args):
                rc, _, _ = self.roda([PYTHON, SCRIPT, *args], self.tmp)
                self.assertEqual(rc, 64)
