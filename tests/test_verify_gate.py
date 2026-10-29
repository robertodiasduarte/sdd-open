"""Contrato de exit do sdd/bin/verify-gate.sh: 0 · 2 · 3 · 4 · 5 · 64, --print, --strict e pass_when.

Cada teste monta um repositório temporário com o script copiado e um DEFINE mínimo. O contrato
está em docs/verify-gate-contract.md; estes testes são a prova executável dele.
"""
from __future__ import annotations

import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/verify-gate.sh"
# Montado em tempo de execução: o marcador ativo literal neste arquivo seria lido como dúvida aberta
# por qualquer ferramenta que varra a árvore atrás dele.
MARCADOR = "[NEEDS " + "CLARIFICATION: qual moeda?]"


def define(kind: str = "test", cmd: str = "true", pass_when: str = "exit 0", corpo: str = "") -> str:
    return (
        "# DEFINE: EXEMPLO\n\n" + corpo + "\n## Verify Gate\n\n```yaml\nverify_gate:\n"
        "  kind: " + kind + "\n"
        '  cmd: "' + cmd + '"\n'
        '  pass_when: "' + pass_when + '"\n'
        '  threshold: "—"\n  manual_fallback: "—"\n```\n\n## Next Step\n'
    )


class VerifyGate(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)

    def gate(self, texto: str, *flags: str) -> tuple[int, str]:
        self.escreve(self.r, "sdd/features/DEFINE_EXEMPLO.md", texto)
        rc, out, err = self.roda([BASH, SCRIPT, *flags, "sdd/features/DEFINE_EXEMPLO.md"], self.r)
        return rc, out + err

    # ── os seis estados ──────────────────────────────────────────────────────
    def test_0_verde_quando_cmd_passa(self):
        rc, out = self.gate(define(cmd="true"))
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_2_vermelho_quando_cmd_falha(self):
        rc, out = self.gate(define(cmd="false"))
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: VERMELHO", out)

    def test_3_inconclusivo_quando_ferramenta_ausente(self):
        rc, out = self.gate(define(cmd="ferramenta-que-nao-existe-sdd-open --run"))
        self.assertEqual(rc, 3, out)
        self.assertIn("RESULTADO: INCONCLUSIVO", out)

    def test_3_smoke_com_403_inesperado_e_ruido_de_infra(self):
        rc, out = self.gate(define(kind="smoke", cmd="echo HTTP 403 Forbidden; exit 1"))
        self.assertEqual(rc, 3, out)

    def test_smoke_com_403_esperado_passa(self):
        rc, out = self.gate(define(kind="smoke", cmd="echo HTTP 403", pass_when="contains: 403"))
        self.assertEqual(rc, 0, out)

    def test_3_comando_que_declara_inconclusivo_propaga(self):
        rc, out = self.gate(define(cmd="echo INCONCLUSIVO: banco fora; exit 3"))
        self.assertEqual(rc, 3, out)

    def test_2_vermelho_declarado_vence_ruido_de_ferramenta(self):
        rc, out = self.gate(define(cmd="echo 'x: command not found'; echo 'RESULTADO: VERMELHO'; exit 1"))
        self.assertEqual(rc, 2, out)

    def test_4_manual_ux_exige_assinatura(self):
        rc, out = self.gate(define(kind="manual-ux", cmd="N/A (manual-ux)", pass_when="checklist signed"))
        self.assertEqual(rc, 4, out)
        self.assertIn("RESULTADO: ASSINATURA HUMANA", out)

    def test_5_marcador_ativo_fora_de_fence(self):
        rc, out = self.gate(define(corpo="Pergunta: " + MARCADOR + "\n"))
        self.assertEqual(rc, 5, out)
        self.assertIn("RESULTADO: CLARIFICAR", out)

    def test_marcador_dentro_de_fence_e_documentacao_nao_duvida(self):
        rc, out = self.gate(define(corpo="```text\n" + MARCADOR + "\n```\n"))
        self.assertEqual(rc, 0, out)

    def test_64_sem_bloco(self):
        rc, out = self.gate("# DEFINE: EXEMPLO\n\nSem gate.\n")
        self.assertEqual(rc, 64, out)
        self.assertIn("RESULTADO: SPEC INVÁLIDA", out)

    def test_64_kind_invalido(self):
        rc, out = self.gate(define(kind="vibes"))
        self.assertEqual(rc, 64, out)

    def test_64_kind_test_sem_cmd_executavel(self):
        rc, out = self.gate(define(cmd="N/A"))
        self.assertEqual(rc, 64, out)

    def test_64_arquivo_inexistente(self):
        rc, out, err = self.roda([BASH, SCRIPT, "sdd/features/NAO_EXISTE.md"], self.r)
        self.assertEqual(rc, 64, out + err)

    def test_64_fora_de_repositorio_git(self):
        solta = self.tmp / "sem-git"
        self.escreve(solta, "DEFINE_EXEMPLO.md", define())
        rc, out, err = self.roda([BASH, str(self.r / SCRIPT), "DEFINE_EXEMPLO.md"], solta)
        self.assertEqual(rc, 64, out + err)

    # ── pass_when ────────────────────────────────────────────────────────────
    def test_contains_presente_passa(self):
        rc, out = self.gate(define(cmd="echo tudo ok: 12 testes", pass_when="contains: 12 testes"))
        self.assertEqual(rc, 0, out)

    def test_contains_ausente_e_vermelho(self):
        rc, out = self.gate(define(cmd="echo 11 testes", pass_when="contains: 12 testes"))
        self.assertEqual(rc, 2, out)

    def test_exit_n_explicito(self):
        rc, out = self.gate(define(cmd="exit 7", pass_when="exit 7"))
        self.assertEqual(rc, 0, out)

    # ── --print e --strict ───────────────────────────────────────────────────
    def test_print_lista_o_bloco_mesmo_com_marcador(self):
        rc, out = self.gate(define(cmd="make check", corpo=MARCADOR + "\n"), "--print")
        self.assertEqual(rc, 0, out)
        self.assertIn("kind:       test", out)
        self.assertIn("cmd:        make check", out)
        self.assertIn("pass_when:  exit 0", out)

    def test_strict_remapeia_3_4_5_para_1(self):
        casos = {
            "3": define(cmd="ferramenta-que-nao-existe-sdd-open"),
            "4": define(kind="manual-ux", cmd="N/A (manual-ux)"),
            "5": define(corpo=MARCADOR + "\n"),
        }
        for original, texto in casos.items():
            with self.subTest(exit_original=original):
                rc, out = self.gate(texto, "--strict")
                self.assertEqual(rc, 1, out)

    def test_strict_preserva_0_2_64(self):
        casos = {0: define(cmd="true"), 2: define(cmd="false"), 64: "# DEFINE sem gate\n"}
        for esperado, texto in casos.items():
            with self.subTest(exit=esperado):
                rc, out = self.gate(texto, "--strict")
                self.assertEqual(rc, esperado, out)


class FixturesDoRepositorio(Sandbox):
    """AT-025: as três fixtures de G4 e do CI continuam saindo 5 · 0 · 64."""

    def test_fixtures_canonicas(self):
        r = self.repo()
        self.copia("sdd", r)
        esperados = {
            "DEFINE_FIXTURE_NEEDS_CLARIFICATION.md": 5,
            "DEFINE_FIXTURE_CONTROLE.md": 0,
            "DEFINE_FIXTURE_SEM_BLOCO.md": 64,
        }
        for fx, esperado in esperados.items():
            with self.subTest(fixture=fx):
                rc, out, err = self.roda([BASH, SCRIPT, "sdd/fixtures/" + fx], r)
                self.assertEqual(rc, esperado, out + err)

    def test_fixtures_existem_no_pacote(self):
        for fx in ("DEFINE_FIXTURE_NEEDS_CLARIFICATION.md", "DEFINE_FIXTURE_CONTROLE.md",
                   "DEFINE_FIXTURE_SEM_BLOCO.md"):
            self.assertTrue((RAIZ / "sdd/fixtures" / fx).is_file(), fx)


if __name__ == "__main__":
    unittest.main()
