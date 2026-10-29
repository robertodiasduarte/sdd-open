"""Contrato do sdd/bin/design-lint.py: o DESIGN segue o template do sdd-open.

Títulos de decisão `### Decision N: <nome>` em sequência sob `## Key Decisions` (outras ferramentas
leem esses títulos), File Manifest com `**Total Files:**` igual ao número de linhas, dependências que
apontam para linhas existentes e sem ciclo, nenhum placeholder fora de código. Cada caso vermelho é a
fixture válida com uma troca.

Exit 0 = válido · 1 = violações · 64 = uso.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/design-lint.py"
FIXTURE = RAIZ / "sdd/fixtures/design/DESIGN_VALIDO.md"
L, R = chr(0x7B), chr(0x7D)  # chaves: o próprio DESIGN da F4 não pode tê-las em prosa

# caso → (trecho da fixture, troca, trecho esperado na mensagem)
CASOS = {
    "sem_key_decisions": ("## Key Decisions", "## Decisions", "Key Decisions"),
    "decisao_em_portugues": ("### Decision 2: ", "### Decisão 2: ", "Decision N"),
    "decisao_fora_de_sequencia": ("### Decision 2: ", "### Decision 3: ", "sequência"),
    "titulo_sem_nome": ("### Decision 1: Lint em Python", "### Decision 1:", "Decision N"),
    "total_errado": ("**Total Files:** 3", "**Total Files:** 4", "Total Files"),
    "dependencia_inexistente": ("| (general) | 1, 2 |", "| (general) | 1, 9 |", "9"),
    "ciclo": ("| Create | Lint | (general) | None |", "| Create | Lint | (general) | 3 |", "ciclo"),
    "placeholder_em_prosa": ("**Context:** o projeto", "**Context:** " + L + "contexto da decisão" + R, "placeholder"),
}


class DesignLint(Sandbox):
    def lint(self, texto: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "DESIGN_X.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def test_fixture_valida_passa(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, FIXTURE], RAIZ)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("✅", out)

    def test_placeholder_dentro_de_codigo_nao_conta(self):
        texto = FIXTURE.read_text(encoding="utf-8")
        self.assertIn("```", texto)
        self.assertRegex(texto, "`[^`\n]*" + "\\" + L)  # há chave dentro de crase simples na fixture

    def test_cada_mutacao_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        for nome, (de, para, trecho) in CASOS.items():
            with self.subTest(caso=nome):
                self.assertIn(de, base)
                rc, out = self.lint(base.replace(de, para, 1))
                self.assertEqual(rc, 1, out)
                self.assertIn(trecho, out)
                self.assertIn("RESULTADO: VERMELHO", out)

    def test_manifest_sem_linhas_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        linhas = [l for l in base.splitlines() if not l.startswith(("| 1 |", "| 2 |", "| 3 |"))]
        rc, out = self.lint("\n".join(linhas) + "\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("File Manifest", out)

    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.tmp)
        self.assertEqual(rc, 64, out + err)

    def test_arquivo_ausente_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, self.tmp / "nao-existe.md"], self.tmp)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
