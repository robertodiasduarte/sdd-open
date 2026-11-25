"""F31 — vermelho avaliado (DEFINE_F31_VERMELHO_AVALIADO, AT-001 a AT-007 e AT-009).

O `report-lint.py` lê `AT-nnn … (PASS n · FAIL n)` na linha do próprio AT, nos logs que ele já confere, e avisa (nunca
reprova) quando o log não prova o AT: zero casos avaliados, AT que já passava antes, ou comando compartilhado por
vários ATs sem a contagem de cada um.
"""
from __future__ import annotations

import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = "sdd/bin/report-lint.py"
F = "EXEMPLO"
EV = "sdd/reports/evidence/%s/" % F
GATE = "bash scripts/gate.sh"
CLASSE = "[casos avaliados]"
DEFINE = """# DEFINE: exemplo

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** x, the system **shall** y | test |
| AT-002 | Non-regression | The system **shall continue to** z | test |
| AT-003 | Event-driven | **When** a tela abre, the system **shall** mostrar | manual-ux |
| AT-004 | Event-driven | **When** w, the system **shall** v | test |
| AT-005 | Event-driven | **When** w, the system **shall** v | test |

## Verify Gate

```yaml
verify_gate:
  kind: test
```
"""
CABECALHO = "| ID | Critério | Antes | Resultado | Evidência |\n|---|---|---|---|---|\n"
CABECALHO_S1 = "| ID | Critério | Resultado | Evidência |\n|---|---|---|---|\n"


def log(corpo: str, rc: int, cmd: str = GATE) -> str:
    return "$ %s\n%s[exit=%d]\n" % (cmd, corpo, rc)


def linha(at: str) -> str:
    return "| %s | x | `evidence/%s/%s.antes.log` | true | `evidence/%s/%s.log` |\n" % (at, F, at, F, at)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.escreve(self.r, "sdd/features/DEFINE_%s.md" % F, DEFINE)

    def logs(self, at: str, corpo: str, rc: int = 2, cmd: str = GATE, final: str = "") -> None:
        self.escreve(self.r, EV + at + ".antes.log", log(corpo, rc, cmd))
        self.escreve(self.r, EV + at + ".log", log(final or "%s ✅ (PASS 2 · FAIL 0)\n" % at, 0, cmd))

    def lint(self, linhas: str, cabecalho: str = CABECALHO) -> tuple[int, str]:
        nome = "sdd/reports/BUILD_REPORT_%s.md" % F
        self.escreve(self.r, nome, "# BUILD REPORT\n\n" + cabecalho + linhas + "\navaliador: N.A. (1 camada)\n")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, nome], self.r)
        return rc, out + err

    def avisa(self, linhas: str, *trechos: str, vezes: int = 1) -> str:
        rc, out = self.lint(linhas)
        self.assertEqual(rc, 0, out)   # só aviso: o exit não muda
        self.assertIn("RESULTADO: VERDE", out)
        self.assertEqual(out.count(CLASSE), vezes, out)
        for t in trechos:
            self.assertIn(t, out)
        return out

    def calado(self, linhas: str, cabecalho: str = CABECALHO) -> None:
        rc, out = self.lint(linhas, cabecalho)
        self.assertEqual(rc, 0, out)
        self.assertNotIn(CLASSE, out)


class AT001ZeroCasos(Base):
    def test_antes_vermelho_com_zero_casos_na_propria_linha_avisa(self):
        self.logs("AT-001", "AT-001 ❌ saque (PASS 0 · FAIL 0)\nAT-005 ❌ recusa (PASS 1 · FAIL 3)\n")
        self.avisa(linha("AT-001"), "AT-001:", "AT-001.antes.log", "nenhum caso avaliado", "conte o erro de carga em FAIL")

    def test_linhas_do_mesmo_at_somam(self):
        self.logs("AT-001", "AT-001 parte 1 (PASS 0 · FAIL 0)\nAT-001 parte 2 (PASS 0 · FAIL 1)\n")
        self.calado(linha("AT-001"))

    def test_antes_que_ja_reprova_nao_ganha_aviso(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 0)\n", rc=127)
        rc, out = self.lint(linha("AT-001"))
        self.assertEqual(rc, 1, out)
        self.assertIn("[vermelho antes] AT-001", out)
        self.assertNotIn(CLASSE, out)

    def test_at_false_nao_e_lido(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 0)\n")
        self.calado(linha("AT-001").replace("| true |", "| false |"))


class AT002SoALinhaDoProprioAt(Base):
    def test_fail_de_outro_at_nao_tira_o_aviso(self):
        self.logs("AT-001", "AT-005 (PASS 0 · FAIL 3)\nAT-001 (PASS 0 · FAIL 0)\n")
        self.avisa(linha("AT-001"), "AT-001:")

    def test_zero_de_outro_at_nao_cria_aviso(self):
        self.logs("AT-001", "AT-005 (PASS 0 · FAIL 0)\nAT-001 (PASS 0 · FAIL 1)\n")
        self.calado(linha("AT-001"))

    def test_id_com_o_mesmo_prefixo_nao_conta(self):
        for vizinho in ("AT-0010", "AT-001b", "AT-001-x"):
            with self.subTest(vizinho=vizinho, caso="não salva"):
                self.logs("AT-001", "%s (PASS 0 · FAIL 3)\nAT-001 (PASS 0 · FAIL 0)\n" % vizinho)
                self.avisa(linha("AT-001"))
            with self.subTest(vizinho=vizinho, caso="não acusa"):
                self.logs("AT-001", "%s (PASS 0 · FAIL 0)\n" % vizinho)
                self.calado(linha("AT-001"))

    def test_a_linha_do_comando_nao_conta(self):
        self.logs("AT-001", "ImportError: conta\n", cmd="AT-001 (PASS 0 · FAIL 0)")
        self.calado(linha("AT-001"))

    def test_citar_o_at_no_meio_da_linha_de_outro_nao_conta(self):
        self.logs("AT-001", "AT-005 depende do AT-001 (PASS 0 · FAIL 0)\nveja AT-001 (PASS 0 · FAIL 0)\n")
        self.calado(linha("AT-001"))


    def test_vale_a_ultima_contagem_da_linha(self):
        # avaliador, ciclo 1 (A1b): o título do caso pode citar a contagem de outro AT
        self.logs("AT-001", "AT-001 ❌ ignora AT-002 PASS 0 · FAIL 3 (PASS 0 · FAIL 0)\n")
        self.avisa(linha("AT-001"), "AT-001:")

    def test_numero_enorme_nao_derruba_o_lint(self):
        self.logs("AT-001", "AT-001 (PASS %s · FAIL 0)\n" % ("9" * 5000))
        self.calado(linha("AT-001"))


class AT003SemContagem(Base):
    def test_comando_proprio_sem_contagem_nao_avisa(self):
        self.logs("AT-001", "ImportError: conta\n", cmd="python3 -m unittest tests.a")
        self.logs("AT-004", "ImportError: conta\n", cmd="python3 -m unittest tests.b")
        self.calado(linha("AT-001") + linha("AT-004"))

    def test_comando_compartilhado_sem_contagem_avisa_uma_vez_com_os_ids(self):
        for at in ("AT-001", "AT-004", "AT-005"):
            self.logs(at, "AT-005 ❌ (PASS 0 · FAIL 1)\nFALHOU\n")
        out = self.avisa(linha("AT-001") + linha("AT-004") + linha("AT-005"), "AT-001, AT-004", GATE)
        self.assertNotIn("AT-001, AT-004, AT-005", out)

    def test_comando_compartilhado_com_contagem_de_todos_nao_avisa(self):
        for at in ("AT-001", "AT-004"):
            self.logs(at, "AT-001 (PASS 0 · FAIL 1)\nAT-004 (PASS 0 · FAIL 2)\n")
        self.calado(linha("AT-001") + linha("AT-004"))

    def test_o_mesmo_at_em_duas_tabelas_nao_e_comando_compartilhado(self):
        # avaliador, ciclo 1 (A2)
        self.logs("AT-001", "ImportError\n")
        self.calado(linha("AT-001") + "\n" + CABECALHO + linha("AT-001"))

    def test_nao_regressao_com_o_mesmo_comando_nao_forma_grupo(self):
        self.logs("AT-001", "ImportError\n")
        self.logs("AT-002", "ok\n", rc=0)
        self.calado(linha("AT-001") + linha("AT-002"))


class AT004FalhouAvaliando(Base):
    def test_fail_1_na_propria_linha_nao_avisa(self):
        self.logs("AT-001", "AT-001 ❌ (PASS 0 · FAIL 1)\n")
        self.calado(linha("AT-001"))

    def test_modulo_ausente_contado_em_fail_nao_avisa(self):
        self.logs("AT-001", "ModuleNotFoundError: No module named 'conta'\nAT-001 ❌ (PASS 0 · FAIL 1)\n", rc=1)
        self.calado(linha("AT-001"))

    def test_titulo_do_caso_que_cita_zero_nao_avisa(self):
        # avaliador, ciclo 1 (A1a)
        self.logs("AT-001", "AT-001 ❌ avisa quando a linha diz PASS 0 · FAIL 0 (PASS 0 · FAIL 2)\n")
        self.calado(linha("AT-001"))

    def test_fail_com_dois_digitos_e_passou_parte(self):
        self.logs("AT-001", "AT-001 ❌ (PASS 3 · FAIL 10)\n")
        self.calado(linha("AT-001"))


class AT005Windows(Base):
    def grava_bytes(self, corpo: bytes, rc: int = 2) -> None:
        self.logs("AT-001", "x\n")
        (self.r / (EV + "AT-001.antes.log")).write_bytes(
            b"$ " + GATE.encode("ascii") + b"\r\n" + corpo + b"\r\n[exit=%d]\r\n" % rc)

    def test_crlf_e_cp1252_dao_o_mesmo_resultado(self):
        for nome, ponto in (("utf-8", "·".encode("utf-8")), ("cp1252", b"\xb7"), ("duplo", "Â·".encode("utf-8"))):
            with self.subTest(caso=nome, avisa=True):
                self.grava_bytes(b"AT-001 (PASS 0 " + ponto + b" FAIL 0)")
                self.avisa(linha("AT-001"), "AT-001:")
            with self.subTest(caso=nome, avisa=False):
                self.grava_bytes(b"AT-001 (PASS 0 " + ponto + b" FAIL 1)")
                self.calado(linha("AT-001"))

    def test_codigo_de_cor_nao_esconde_a_linha(self):
        self.grava_bytes(b"\x1b[31mAT-001\x1b[0m (PASS \x1b[1m0\x1b[0m \xc2\xb7 FAIL 0)")
        self.avisa(linha("AT-001"))

    def test_fim_de_cor_do_tput_nao_esconde_a_linha(self):
        self.grava_bytes(b"\x1b(B\x1b[m\x1b[38:2::9mAT-001\x1b(B\x1b[m (PASS 0 \xc2\xb7 FAIL 0)")
        self.avisa(linha("AT-001"))

    def test_marca_antes_do_id_e_aceita(self):
        self.grava_bytes("  ❌ - **AT-001** (PASS 0 · FAIL 0)".encode("utf-8"))
        self.avisa(linha("AT-001"))


class AT006Textos(unittest.TestCase):
    TEXTOS = (".agents/skills/sdd-define/SKILL.md",
              ".agents/skills/sdd-build/web/references/disciplina-de-teste.md",
              "sdd/templates/fragments/EVIDENCIA.md")

    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("report_lint", str(RAIZ / SCRIPT))
        cls.lint = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.lint)

    def test_o_exemplo_de_cada_texto_e_lido_pelo_lint(self):
        for nome in self.TEXTOS:
            with self.subTest(texto=nome):
                texto = (RAIZ / nome).read_text(encoding="utf-8")
                exemplos = re.findall(r"`(AT-\d+ [^`]*PASS \d+ · FAIL \d+\))`", texto)
                self.assertTrue(exemplos, "sem exemplo da linha do AT")
                with tempfile.TemporaryDirectory() as d:
                    for exemplo in exemplos:
                        caminho = Path(d) / "x.log"
                        caminho.write_text("$ x\n%s\n[exit=2]\n" % exemplo, encoding="utf-8")
                        esperado = tuple(int(n) for n in re.findall(r"(?:PASS|FAIL) (\d+)", exemplo))
                        self.assertEqual(self.lint.contagem_do_at(str(caminho), exemplo.split()[0]), esperado)

    def test_cada_texto_ensina_a_contar_o_erro_de_carga(self):
        for nome in self.TEXTOS:
            with self.subTest(texto=nome):
                texto = " ".join((RAIZ / nome).read_text(encoding="utf-8").split())
                self.assertIn("erro de carga", texto)

    def test_o_texto_do_starter_nao_cita_o_script(self):
        self.assertNotIn("sdd/bin", (RAIZ / self.TEXTOS[1]).read_text(encoding="utf-8"))


class AT007ControlesIguais(Base):
    def test_fail_1(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 1)\n")
        self.calado(linha("AT-001"))

    def test_continua_verde_com_casos(self):
        self.logs("AT-002", "AT-002 (PASS 3 · FAIL 0)\n", rc=0)
        self.calado(linha("AT-002"))

    def test_na_de_gate_fora_de_test_e_cmd(self):
        self.logs("AT-003", "AT-003 (PASS 0 · FAIL 0)\n", final="AT-003 (PASS 0 · FAIL 0)\n")
        self.calado("| AT-003 | x | N.A. (humano) | true | `evidence/%s/AT-003.log` |\n" % F)

    def test_log_sem_contagem_de_comando_proprio(self):
        self.logs("AT-001", "ImportError\n", rc=1)
        self.calado(linha("AT-001"))

    def test_relatorio_sem_a_coluna_antes(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 0)\n", final="AT-001 (PASS 0 · FAIL 0)\n")
        self.calado("| AT-001 | x | true | `evidence/%s/AT-001.log` |\n" % F, CABECALHO_S1)


class AT009Vizinhos(Base):
    def test_continua_verde_com_zero_casos_avisa(self):
        self.logs("AT-002", "AT-002 (PASS 0 · FAIL 0)\n", rc=0)
        self.avisa(linha("AT-002"), "AT-002:", "AT-002.antes.log", "nenhum caso avaliado")

    def test_final_verde_com_zero_casos_avisa(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 1)\n", final="AT-001 (PASS 0 · FAIL 0)\n")
        self.avisa(linha("AT-001"), "AT-001:", "AT-001.log", "nenhum caso avaliado")

    def test_final_vermelho_com_zero_casos_fica_fora(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 1)\n")
        self.escreve(self.r, EV + "AT-001.log", log("AT-001 (PASS 0 · FAIL 0)\n", 2))
        self.calado(linha("AT-001"))

    def test_novo_que_ja_passava_avisa(self):
        self.logs("AT-001", "AT-001 (PASS 2 · FAIL 0)\nAT-005 (PASS 0 · FAIL 1)\n")
        self.avisa(linha("AT-001"), "AT-001:", "já passava antes")

    def test_antes_e_final_zerados_sao_dois_avisos(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 0)\n", final="AT-001 (PASS 0 · FAIL 0)\n")
        self.avisa(linha("AT-001"), "AT-001.antes.log", "AT-001.log", vezes=2)

    def test_antes_recusado_nao_cala_o_aviso_do_final(self):
        # avaliador, ciclo 1 (A3)
        self.logs("AT-001", "x\n", rc=0, final="AT-001 (PASS 0 · FAIL 0)\n")
        for celula in (linha("AT-001"), linha("AT-001").replace("`evidence/%s/AT-001.antes.log`" % F, "—")):
            rc, out = self.lint(celula)
            self.assertEqual(rc, 1, out)
            self.assertIn("[vermelho antes] AT-001", out)
            self.assertEqual(out.count(CLASSE), 1, out)

    def test_final_citado_depois_do_log_de_outra_feature_e_lido(self):
        # avaliador, ciclo 1 (A4)
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 1)\n", final="AT-001 (PASS 0 · FAIL 0)\n")
        self.avisa("| AT-001 | x | `evidence/%s/AT-001.antes.log` | true | `evidence/OUTRA/AT-001.log` · `evidence/%s/AT-001.log` |\n"
                   % (F, F), "AT-001.log")

    def test_mesmo_at_em_duas_tabelas_da_um_aviso_por_log(self):
        # revisão, rodadas 2 e 3 (R1, R2): quem tira a repetição é imprimir_avisos
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 0)\n", final="AT-001 (PASS 0 · FAIL 0)\n")
        self.avisa(linha("AT-001") + "\n" + CABECALHO + linha("AT-001"), vezes=2)

    def test_zero_de_outro_at_no_final_nao_avisa(self):
        self.logs("AT-001", "AT-001 (PASS 0 · FAIL 1)\n", final="AT-001 (PASS 1 · FAIL 0)\nAT-005 (PASS 0 · FAIL 0)\n")
        self.calado(linha("AT-001"))


if __name__ == "__main__":
    unittest.main()
