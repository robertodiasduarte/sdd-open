"""Contrato do sdd/bin/handoff-lint.py: o mínimo do HANDOFF_TEMPLATE.md do sdd-open.

Confere `# HANDOFF:`, a Ficha com Objetivo, Status e Verify Gate, o Prompt de retomada com bloco de
código, ≥1 slice datado no histórico, nenhum placeholder e nenhuma frase que dependa da conversa
anterior. Seção a mais passa e `## Eventos` não é exigido: o template ainda vai crescer. Cada caso
vermelho é a fixture válida com uma troca.

Exit 0 = válido · 1 = violações · 64 = uso.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/handoff-lint.py"
FIXTURE = RAIZ / "sdd/fixtures/handoff/HANDOFF_VALIDO.md"
L, R = chr(0x7B), chr(0x7D)

# caso → (trecho da fixture, troca, trecho esperado na mensagem)
CASOS = {
    "sem_titulo": ("# HANDOFF: ", "# Passagem: ", "# HANDOFF:"),
    "ficha_sem_objetivo": ("| **Objetivo** |", "| **Meta** |", "Objetivo"),
    "ficha_sem_verify_gate": ("| **Verify Gate** |", "| **Gate** |", "Verify Gate"),
    "prompt_sem_bloco": ("```text\nRetomar", "Retomar", "Prompt de retomada"),
    "historico_sem_data": ("### Sessão 1 — 2026-10-29", "### Sessão 1", "Histórico de slices"),
    "placeholder_em_prosa": ("- Lint novo publicado", "- " + L + "o que está pronto" + R, "placeholder"),
    "placeholder_no_prompt": ("Próxima ação: rodar", "Próxima ação: «comando»", "placeholder"),
    "como_discutimos": ("- Lint novo publicado", "- Como discutimos, o lint saiu", "como discutimos"),
    "de_onde_paramos": ("Próxima ação: rodar", "Continue de onde paramos e rode", "de onde paramos"),
}


class HandoffLint(Sandbox):
    def lint(self, texto: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "HANDOFF_X.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def test_fixture_valida_passa(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, FIXTURE], RAIZ)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("✅", out)

    def test_fixture_nao_tem_eventos_e_tem_comando_com_chaves_no_prompt(self):
        texto = FIXTURE.read_text(encoding="utf-8")
        self.assertNotIn("## Eventos", texto)
        self.assertIn("awk '" + L + "print $1" + R + "'", texto)
        self.assertIn("$" + L + "HOME" + R, texto)

    def test_secao_extra_passa(self):
        base = FIXTURE.read_text(encoding="utf-8")
        extra = base.replace("## Prompt de retomada",
                             "## Recomendações\n\n- Rodar o lint antes de cada sessão.\n\n## Prompt de retomada", 1)
        self.assertNotEqual(extra, base)
        rc, out = self.lint(extra)
        self.assertEqual(rc, 0, out)

    def test_com_eventos_tambem_passa(self):
        base = FIXTURE.read_text(encoding="utf-8")
        rc, out = self.lint(base.replace("## Feito", "## Eventos\n\n- 2026-10-29 — escopo mudou.\n\n## Feito", 1))
        self.assertEqual(rc, 0, out)

    def test_cada_mutacao_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        for nome, (de, para, trecho) in CASOS.items():
            with self.subTest(caso=nome):
                self.assertIn(de, base)
                rc, out = self.lint(base.replace(de, para, 1))
                self.assertEqual(rc, 1, out)
                self.assertIn(trecho, out)
                self.assertIn("RESULTADO: VERMELHO", out)

    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.tmp)
        self.assertEqual(rc, 64, out + err)

    def test_arquivo_ausente_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, self.tmp / "nao-existe.md"], self.tmp)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
