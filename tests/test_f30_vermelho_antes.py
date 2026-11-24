"""F30 S2 — vermelho antes do verde no BUILD_REPORT (DEFINE_F30_QUALIDADE_CODIGO, AT-010, AT-011 e AT-012).

AT-010: numa tabela de critérios com a coluna `Antes`, todo AT `true` de comportamento novo (gate `test`/`cmd`, sem
`shall continue to`) exige `evidence/{F}/AT-nnn.antes.log` com o mesmo comando do `AT-nnn.log` e `[exit=n]`, n fora de
0, 126 e 127.
AT-011: `shall continue to` exige o antes verde; gate `manual-ux` ou de outro kind aceita `N.A. (<motivo>)`.
AT-012: sem a coluna `Antes` (relatório anterior à S2), aprova com 1 aviso; sem o DEFINE, aviso com a causa.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, Sandbox

SCRIPT = "sdd/bin/report-lint.py"
F = "EXEMPLO"
EV = "sdd/reports/evidence/%s/" % F
CMD = "python3 -m unittest tests.test_conta"
DEFINE = """# DEFINE: exemplo

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o saque passa do saldo, the system **shall** recusar | test |
| AT-002 | Non-regression | The system **Shall Continue To** aceitar o saque dentro do saldo | test |
| AT-003 | Event-driven | **When** a tela abre, the system **shall** mostrar o saldo | manual-ux |
| AT-004 | Event-driven | **When** o deploy termina, the system **shall** responder 200 | `smoke` |
| AT-005 | Unwanted | **If** o AT é `shall continue to`, **then** the system **shall** exigir o antes verde | test |

## Verify Gate

```yaml
verify_gate:
  kind: test
```
"""
CABECALHO = "| ID | Critério | Antes | Resultado | Evidência |\n|---|---|---|---|---|\n"
CABECALHO_S1 = "| ID | Critério | Resultado | Evidência |\n|---|---|---|---|\n"
AVISO_COLUNA = "não tem a coluna `Antes`"


def log(cmd: str = CMD, rc: int = 0, corpo: str = "Ran 1 test\n") -> str:
    return "$ %s\n%s[exit=%d]\n" % (cmd, corpo, rc)


def linha(at: str, antes: str, resultado: str = "true") -> str:
    return "| %s | x | %s | %s | `evidence/%s/%s.log` |\n" % (at, antes, resultado, F, at)


def antes(at: str) -> str:
    return "`evidence/%s/%s.antes.log`" % (F, at)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.escreve(self.r, "sdd/features/DEFINE_%s.md" % F, DEFINE)
        for at in ("AT-001", "AT-002", "AT-003", "AT-004"):
            self.escreve(self.r, EV + at + ".log", log())

    def lint(self, linhas: str, cabecalho: str = CABECALHO) -> tuple[int, str]:
        nome = "sdd/reports/BUILD_REPORT_%s.md" % F
        self.escreve(self.r, nome, "# BUILD REPORT\n\n" + cabecalho + linhas + "\navaliador: N.A. (1 camada)\n")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, nome], self.r)
        return rc, out + err

    def reprova(self, linhas: str, *trechos: str) -> str:
        rc, out = self.lint(linhas)
        self.assertEqual(rc, 1, out)
        self.assertIn("[vermelho antes] AT-", out)
        self.assertIn("citado na coluna `Antes`", out)   # o conserto da classe, em 1 linha
        for t in trechos:
            self.assertIn(t, out)
        self.assertResultado(out)
        return out


class AT010ComportamentoNovo(Base):
    def test_antes_vermelho_do_mesmo_comando_aprova(self):
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=1, corpo="ImportError: conta\n"))
        rc, out = self.lint(linha("AT-001", antes("AT-001")))
        self.assertEqual(rc, 0, out)
        self.assertNotIn(AVISO_COLUNA, out)

    def test_sem_antes_reprova(self):
        self.reprova(linha("AT-001", "—"), "AT-001", "AT-001.antes.log")

    def test_antes_verde_reprova(self):
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=0))
        self.reprova(linha("AT-001", antes("AT-001")), "o antes de um AT de comportamento novo tem de falhar")

    def test_antes_127_nao_e_vermelho(self):
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=127, corpo="python3: command not found\n"))
        self.reprova(linha("AT-001", antes("AT-001")), "`[exit=127]`")

    def test_antes_de_outro_comando_reprova(self):
        self.escreve(self.r, EV + "AT-001.antes.log", log("false", rc=1))
        self.reprova(linha("AT-001", antes("AT-001")), "não o mesmo comando")

    def test_antes_sem_exit_no_fim_reprova(self):
        self.escreve(self.r, EV + "AT-001.antes.log", "$ %s\nFAILED\n[exit=]\n" % CMD)
        self.reprova(linha("AT-001", antes("AT-001")), "`[exit=<n>]`")

    def test_na_em_at_novo_reprova(self):
        self.reprova(linha("AT-001", "N.A. (é fácil)"), "N.A.")

    def test_antes_de_outro_at_reprova(self):
        self.escreve(self.r, EV + "AT-002.antes.log", log(rc=1))
        self.reprova(linha("AT-001", antes("AT-002")), "AT-001.antes.log")

    def test_antes_fora_da_evidencia_da_feature_reprova(self):
        self.escreve(self.r, "sdd/reports/evidence/OUTRA/AT-001.antes.log", log(rc=1))
        self.reprova(linha("AT-001", "`evidence/OUTRA/AT-001.antes.log`"), "evidence/%s/" % F)

    def test_antes_ignorado_pelo_git_reprova(self):
        self.escreve(self.r, ".gitignore", "*.antes.log\n")
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=1))
        self.reprova(linha("AT-001", antes("AT-001")), "IGNORA")

    def test_criterio_que_so_cita_shall_continue_to_e_novo(self):
        # revisão do DESIGN, N1: a classe vem do padrão do AT, não da expressão citada no meio do critério
        self.escreve(self.r, EV + "AT-005.log", log())
        self.escreve(self.r, EV + "AT-005.antes.log", log(rc=1))
        rc, out = self.lint(linha("AT-005", antes("AT-005")))
        self.assertEqual(rc, 0, out)
        self.escreve(self.r, EV + "AT-005.antes.log", log(rc=0))
        self.reprova(linha("AT-005", antes("AT-005")), "o antes de um AT de comportamento novo tem de falhar")

    def test_evidencia_so_pela_avaliacao_ainda_confere_o_comando(self):
        # avaliador, ciclo 1 (O1): sem log citado na evidência, o antes é comparado com o AT-nnn.log do disco
        self.escreve(self.r, "sdd/reviews/AVALIACAO_%s_20261124-1200.md" % F, "VEREDITO: PASS\n")
        self.escreve(self.r, EV + "AT-001.antes.log", log("outro-comando", rc=1))
        self.reprova("| AT-001 | x | %s | true | `AVALIACAO_%s_20261124-1200.md` |\n" % (antes("AT-001"), F),
                     "não o mesmo comando")

    def test_cabecalho_antes_com_complemento_ainda_e_a_coluna(self):
        # avaliador, ciclo 1 (O2)
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=0))
        rc, out = self.lint(linha("AT-001", antes("AT-001")),
                            "| ID | Critério | Antes (vermelho) | Resultado | Evidência |\n|---|---|---|---|---|\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("[vermelho antes]", out)

    def test_at_false_nao_e_conferido(self):
        rc, out = self.lint(linha("AT-001", "—", resultado="false"))
        self.assertEqual(rc, 0, out)


class AT011ContinuaEFora(Base):
    def test_continua_com_antes_verde_aprova(self):
        self.escreve(self.r, EV + "AT-002.antes.log", log(rc=0))
        rc, out = self.lint(linha("AT-002", antes("AT-002")))
        self.assertEqual(rc, 0, out)

    def test_continua_com_antes_vermelho_reprova(self):
        self.escreve(self.r, EV + "AT-002.antes.log", log(rc=1))
        self.reprova(linha("AT-002", antes("AT-002")), "`shall continue to` exige o antes verde")

    def test_continua_sem_antes_reprova(self):
        self.reprova(linha("AT-002", "N.A. (regressão)"), "AT-002")

    def test_manual_ux_aceita_na(self):
        rc, out = self.lint(linha("AT-003", "N.A. (assinatura humana)"))
        self.assertEqual(rc, 0, out)

    def test_kind_fora_de_test_e_cmd_aceita_na(self):
        rc, out = self.lint(linha("AT-004", "N.A. (smoke de produção)"))
        self.assertEqual(rc, 0, out)

    def test_varios_ats_cada_um_pela_sua_classe(self):
        self.escreve(self.r, EV + "AT-001.antes.log", log(rc=1))
        self.escreve(self.r, EV + "AT-002.antes.log", log(rc=0))
        rc, out = self.lint(linha("AT-001", antes("AT-001")) + linha("AT-002", antes("AT-002"))
                            + linha("AT-003", "N.A. (assinatura)"))
        self.assertEqual(rc, 0, out)


class AT012RelatorioAnterior(Base):
    def test_sem_a_coluna_aprova_com_aviso(self):
        rc, out = self.lint("| AT-001 | x | true | `evidence/%s/AT-001.log` |\n" % F, CABECALHO_S1)
        self.assertEqual(rc, 0, out)
        self.assertIn(AVISO_COLUNA, out)
        self.assertNotIn("[vermelho antes]", out)

    def test_sem_a_coluna_e_sem_at_true_nao_avisa(self):
        rc, out = self.lint("| AT-001 | x | false | — |\n", CABECALHO_S1)
        self.assertEqual(rc, 0, out)
        self.assertNotIn(AVISO_COLUNA, out)

    def test_sem_define_avisa_com_a_causa(self):
        (self.r / ("sdd/features/DEFINE_%s.md" % F)).unlink()
        rc, out = self.lint(linha("AT-001", "—"))
        self.assertEqual(rc, 0, out)
        self.assertIn("DEFINE_%s.md" % F, out)
        self.assertIn("vermelho antes do verde não foi conferido", out)

    def test_at_fora_do_define_avisa(self):
        self.escreve(self.r, EV + "AT-009.log", log())
        rc, out = self.lint(linha("AT-009", "—"))
        self.assertEqual(rc, 0, out)
        self.assertIn("AT-009", out)
        self.assertIn("não está no DEFINE", out)

    def test_define_sem_coluna_de_kind_usa_o_do_gate(self):
        self.escreve(self.r, "sdd/features/DEFINE_%s.md" % F,
                     "| ID | Critério |\n|---|---|\n| AT-001 | **When** x, the system **shall** y |\n\n"
                     "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n```\n")
        self.reprova(linha("AT-001", "—"), "AT-001")


if __name__ == "__main__":
    unittest.main()
