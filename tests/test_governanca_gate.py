"""verify-gate.sh e a linha Governança (F12, C6/C7): o 2º motivo do exit 5.

DEFINE F12 AT-012 e AT-013: linha ausente, vazia, pendente, falhou, placeholder do template, fora do
## Technical Context ou dentro de cerca ⇒ 5 com GOVERNANÇA NÃO REVISADA e as 2 saídas; o marcador do passo
11 imprime a mesma mensagem; os 3 valores finais passam; --print é isento; --strict remapeia para 1; a
ordem é marcador → linha → bloco. A sabotagem tira a checagem e a fixture sem a linha passa a sair 0.
"""
from __future__ import annotations

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/verify-gate.sh"
GATE = '## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n  cmd: "true"\n  pass_when: "exit 0"\n```\n'


def define(linha: str | None, gate: bool = True, extra: str = "") -> str:
    tc = ""
    if linha is not None:
        tc = "## Technical Context\n\n| Aspect | Value | Notes |\n|---|---|---|\n" + linha + "\n\n"
    return "# DEFINE: X\n\n## Problem Statement\n\nalgo\n\n" + tc + extra + (GATE if gate else "")


class Gate(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin", self.r)
        self.copia("sdd/fixtures", self.r)
        self.env = dict(self.env, SDD_TRACE="off")

    def gate(self, texto: str | None = None, *flags: str, arquivo: str = "sdd/features/DEFINE_X.md",
             script: str = SCRIPT) -> tuple[int, str]:
        if texto is not None:
            self.escreve(self.r, arquivo, texto)
        rc, out, err = self.roda([BASH, script, *flags, arquivo], self.r)
        return rc, out + err

    def assert_governanca(self, rc: int, out: str) -> None:
        self.assertEqual(rc, 5, out)
        self.assertIn("GOVERNANÇA NÃO REVISADA (exit 5)", out)
        self.assertIn("rode só o passo 11 (Governança) do sdd-define", out)
        self.assertIn("| **Governança** | dispensada — <motivo> | <seu nome, data> |", out)
        self.assertIn("RESULTADO: CLARIFICAR\n→ rode a revisão de governança", out)

    def test_fixture_sem_a_linha_sai_5_com_as_duas_saidas(self):
        rc, out = self.gate(None, arquivo="sdd/fixtures/DEFINE_FIXTURE_SEM_GOVERNANCA.md")
        self.assert_governanca(rc, out)
        self.assertIn("(encontrado: ausente)", out)

    def test_valores_que_nao_sao_finais_saem_5(self):
        casos = {
            "vazio": "| **Governança** |  | x |",
            "pendente": "| **Governança** | pendente | x |",
            "falhou": "| **Governança** | falhou — 2 tentativas | x |",
            "placeholder do template": "| **Governança** | N.A. — <motivo> | x |",
            "placeholder com chave": "| **Governança** | {pendente — o passo 11 escreve} | x |",
            "N.A. sem motivo": "| **Governança** | N.A. — | x |",
            "forma com dois-pontos": "Governança: N.A. — sem tema",
        }
        for nome, linha in casos.items():
            with self.subTest(caso=nome):
                self.assert_governanca(*self.gate(define(linha)))

    def test_linha_fora_do_technical_context_ou_em_cerca_nao_vale(self):
        fora = "## Clarifications\n\n| **Governança** | N.A. — sem tema | x |\n\n"
        self.assert_governanca(*self.gate(define(None, extra=fora)))
        cerca = "## Technical Context\n\n```markdown\n| **Governança** | N.A. — sem tema | x |\n```\n\n"
        self.assert_governanca(*self.gate(define(None, extra=cerca)))

    def test_valores_finais_passam(self):
        for linha in ("| **Governança** | N.A. — sem dinheiro, tributo ou dado pessoal | revisor |",
                      "| **Governança** | GOVERNANCA_REVIEW_X.md · 2 aplicadas · 0 recusadas · 1 adiadas | x |",
                      "| **Governança** | dispensada — DEFINE anterior à v2.4.0 | Roberto, 2026-11-03 |",
                      "| **Governança** | dispensada - sem hífen longo | x |"):
            with self.subTest(linha=linha):
                rc, out = self.gate(define(linha))
                self.assertEqual(rc, 0, out)

    def test_marcador_do_passo_11_imprime_a_mensagem_da_governanca(self):
        marcador = "## Clarifications\n\n- [NEEDS" + " CLARIFICATION: governança não rodou — rode só o passo 11]\n\n"
        rc, out = self.gate(define("| **Governança** | dispensada — x | y |", extra=marcador))
        self.assert_governanca(rc, out)
        self.assertIn("apague do DEFINE o marcador", out)
        outro = "## Clarifications\n\n- [NEEDS" + " CLARIFICATION: o mês fecha quando?]\n\n"
        rc, out = self.gate(define("| **Governança** | N.A. — x | y |", extra=outro))
        self.assertEqual(rc, 5, out)
        self.assertIn("CLARIFICAÇÃO PENDENTE", out)
        self.assertIn("→ resolva os marcadores de ambiguidade", out)

    def test_l2_marcador_de_governanca_com_outra_duvida_mostra_as_duas(self):
        marcadores = ("## Clarifications\n\n- [NEEDS" + " CLARIFICATION: governança não rodou — rode só o passo 11]\n"
                      "- [NEEDS" + " CLARIFICATION: o mês fecha quando?]\n\n")
        rc, out = self.gate(define("| **Governança** | pendente | y |", extra=marcadores))
        self.assert_governanca(rc, out)
        self.assertIn("responda também as dúvidas abertas", out)
        self.assertIn("o mês fecha quando?", out)

    def test_aval2_duas_duvidas_na_mesma_linha_aparecem(self):
        linha = ("## Clarifications\n\n- [NEEDS" + " CLARIFICATION: governança não rodou] e [NEEDS"
                 + " CLARIFICATION: qual teto por minuto?]\n\n")
        rc, out = self.gate(define("| **Governança** | pendente | y |", extra=linha))
        self.assert_governanca(rc, out)
        self.assertIn("qual teto por minuto?", out)

    def test_l3_linha_com_recuo_ou_sem_negrito_vale(self):
        for linha in ("  | **Governança** | N.A. — sem tema | x |", "| Governança | N.A. — sem tema | x |"):
            with self.subTest(linha=linha):
                rc, out = self.gate(define(linha))
                self.assertEqual(rc, 0, out)

    def test_print_isento_strict_remapeia_e_ordem(self):
        rc, out = self.gate(define(None), "--print")
        self.assertEqual(rc, 0, out)
        rc, out = self.gate(define(None), "--strict")
        self.assertEqual(rc, 1, out)
        rc, out = self.gate(define(None, gate=False))
        self.assertEqual(rc, 5, out)       # sem linha e sem bloco: a linha vem antes do bloco
        rc, out = self.gate(define("| **Governança** | N.A. — x | y |", gate=False))
        self.assertEqual(rc, 64, out)

    def test_fixtures_mantem_o_exit(self):
        esperado = {"DEFINE_FIXTURE_CONTROLE.md": 0, "DEFINE_FIXTURE_NEEDS_CLARIFICATION.md": 5,
                    "DEFINE_FIXTURE_SEM_BLOCO.md": 64, "DEFINE_FIXTURE_SEM_GOVERNANCA.md": 5,
                    "DEFINE_FIXTURE_GOVERNANCA.md": 5}
        for fx, rc_esperado in esperado.items():
            with self.subTest(fixture=fx):
                rc, out = self.gate(None, arquivo="sdd/fixtures/" + fx)
                self.assertEqual(rc, rc_esperado, out)

    def test_sabotagem_sem_a_checagem_a_fixture_sem_linha_passa(self):
        texto = (self.r / SCRIPT).read_text(encoding="utf-8")
        alvo = '    CLARIFICAR_MOTIVO=governanca\n    msg_governanca "${GOV:-ausente}"\n    finalizar 5\n'
        self.assertIn(alvo, texto)
        self.escreve(self.r, "sdd/bin/sabotado.sh", texto.replace(alvo, "    :\n"))
        rc, _ = self.gate(None, arquivo="sdd/fixtures/DEFINE_FIXTURE_SEM_GOVERNANCA.md", script="sdd/bin/sabotado.sh")
        self.assertEqual(rc, 0)
