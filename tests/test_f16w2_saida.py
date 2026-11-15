"""F16W2, AT-001: a saída dos scripts Python do pacote em UTF-8 e "\\n", também num stdout cp1252.

No Windows, o Python com a saída num pipe (o Git Bash do aluno) escreve em cp1252 e troca "\\n" por "\\r\\n": o ✅
derrubava o `design-lint.py` com UnicodeEncodeError (exit 1) e o stderr saía com `\\U0001f6d1` no lugar do 🛑. Aqui o
cp1252 é simulado por PYTHONIOENCODING=cp1252, que vale em qualquer sistema; a troca no `__main__` passa por cima dele.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

from apoio import RAIZ, Sandbox

TRECHO = 'reconfigure(encoding="utf-8", errors="replace", newline="\\n")'
MAIN = 'if __name__ == "__main__":'
# Arquivos iguais byte a byte ao pacote de origem (SHA-256 conferido em test_f21_textos): não recebem a troca.
CONGELADOS = {".agents/skills/sdd-engenharia-reversa-saas/scripts/validate_reverse.py"}


def scripts_com_main() -> list[str]:
    saida = []
    for rel in (RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").split("\n"):
        rel = rel.strip()
        if not rel.endswith(".py") or rel.startswith(("tests/", "sdd/fixtures/")) or "/tests/" in rel:
            continue
        if MAIN in (RAIZ / rel).read_text(encoding="utf-8") and rel not in CONGELADOS:
            saida.append(rel)
    return saida


class Guarda(unittest.TestCase):
    def test_todo_script_com_main_troca_a_saida_antes_de_tudo(self):
        lista = scripts_com_main()
        self.assertGreaterEqual(len(lista), 20, lista)
        for rel in lista:
            with self.subTest(script=rel):
                texto = (RAIZ / rel).read_text(encoding="utf-8")
                bloco = texto.split(MAIN, 1)[1]
                # o 1º comando do bloco (fora comentário) é o laço da troca, e o trecho vem logo depois
                linhas = [ln.strip() for ln in bloco.split("\n")[1:] if ln.strip() and not ln.strip().startswith("#")]
                self.assertEqual(linhas[0], "for _canal in (sys.stdout, sys.stderr):", rel)
                self.assertIn("_canal." + TRECHO, linhas[2], rel)


class GuardaEmbutidos(unittest.TestCase):
    def test_todo_python_embutido_num_script_troca_a_saida(self):
        # F16W2 (revisão da Decision 2): o UTF-8 e o "\n" vão no próprio programa embutido, não num calço no PATH (que
        # vazaria para o comando de teste do aluno)
        vistos = 0
        for rel in (RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").split("\n"):
            rel = rel.strip()
            if not rel.endswith(".sh") or rel.startswith(("tests/", "sdd/fixtures/", "scripts/starter/")):
                continue
            texto = (RAIZ / rel).read_text(encoding="utf-8")
            for m in re.finditer(r"<<'PY'[^\n]*\n(.*?)\nPY\n", texto, re.S):
                vistos += 1
                with self.subTest(script=rel, inicio=m.group(1)[:40]):
                    self.assertIn('_sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\\n")', m.group(1)[:1200])
        self.assertGreaterEqual(vistos, 20)


class SaidaCp1252(Sandbox):
    """Cada script, chamado como o aluno chama, com a saída em cp1252: o caractere sai inteiro e o exit é o de sempre."""

    def setUp(self):
        super().setUp()
        self.env_cp = dict(self.env, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        self.escreve(self.tmp, "DESIGN_X.md",
                     "# D\n\n## Key Decisions\n\n### Decision 1: x\n\ntexto\n\n## File Manifest\n\n"
                     "| # | File | Action | Purpose | Dependencies |\n|---|---|---|---|---|\n"
                     "| 1 | `a.py` | Create | ação | — |\n\n**Total Files:** 1\n")
        (self.tmp / "vazia").mkdir()

    def chama(self, rel: str, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([sys.executable, "-B", str(RAIZ / rel), *args], self.tmp, env=self.env_cp)
        return rc, out + err

    def test_os_scripts_imprimem_o_caractere_e_saem_com_o_exit_de_sempre(self):
        casos = (
            ("sdd/bin/design-lint.py", ("DESIGN_X.md",), 0, "✅ DESIGN_X.md: DESIGN válido"),
            ("sdd/bin/handoff-lint.py", ("DESIGN_X.md",), 1, "🛑 DESIGN_X.md: o 1º título não é"),
            ("sdd/bin/skill-lint.py", ("vazia",), 1, "🛑 vazia: não consegui ler"),
            ("sdd/bin/kb-dominios.py", ("DESIGN_X.md",), 1, "🛑 DESIGN_X.md: falta a linha **KB Domains**"),
            ("sdd/bin/governanca-bloco.py", (), 64, "→ chame com <resposta.txt>"),
            (".agents/skills/sdd-release/scripts/deploy-espera-testes.py", (), 3, "→ O deploy espera os testes? não se aplica"),
            ("scripts/check-versions.py", ("--base", "nada"), 0, "só as checagens estruturais"),
            (".agents/skills/sdd-kb/scripts/validate_kb.py", ("vazia",), 2, "FAIL: no concept found — a KB"),
            (".agents/skills/sdd-auditoria-harness/scripts/collect_evidence.py", ("vazia",), 0, '"read_only": true'),
        )
        for rel, args, rc_esperado, trecho in casos:
            with self.subTest(script=rel):
                rc, saida = self.chama(rel, *args)
                self.assertNotIn("UnicodeEncodeError", saida)
                self.assertNotRegex(saida, r"\\U0001|\\u2")
                self.assertNotIn("\r", saida)
                self.assertEqual(rc, rc_esperado, saida)
                self.assertIn(trecho, saida)

    def test_report_lint_le_o_stdin_em_utf8(self):
        rel = "sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md"
        alvo = self.copia(rel, self.tmp)
        rc_arq, saida_arq = self.chama("sdd/bin/report-lint.py", str(alvo))
        dado = alvo.read_bytes()
        import subprocess
        r = subprocess.run([sys.executable, "-B", str(RAIZ / "sdd/bin/report-lint.py"), "--stdin", str(alvo)],
                           cwd=str(self.tmp), env=self.env_cp, input=dado, capture_output=True)
        saida_in = (r.stdout + r.stderr).decode("utf-8", "replace")
        self.assertNotIn("UnicodeEncodeError", saida_arq + saida_in)
        self.assertNotIn("UnicodeDecodeError", saida_in)
        self.assertEqual((r.returncode, saida_in), (rc_arq, saida_arq))

    def test_stdin_lido_em_cp1252_daria_verde_falso(self):
        # o critério com ✅ e sem evidência é vermelho; lido em cp1252, o ✅ virava lixo, o critério deixava de ser
        # "verdadeiro" e o relatório saía VERDE (sabotagem S9 da F16W2)
        import subprocess
        alvo = self.escreve(self.tmp, "BUILD_REPORT_X.md",
                            "# BUILD REPORT: X\n\n| ID | Critério (EARS) | Resultado | Evidência |\n|----|---|---|---|\n"
                            "| AT-001 | When x, the system shall y | ✅ | — |\n\navaliador: N.A. (1 camada)\n")
        r = subprocess.run([sys.executable, "-B", str(RAIZ / "sdd/bin/report-lint.py"), "--stdin", str(alvo)],
                           cwd=str(self.tmp), env=self.env_cp, input=alvo.read_bytes(), capture_output=True)
        saida = (r.stdout + r.stderr).decode("utf-8", "replace")
        self.assertEqual(r.returncode, 1, saida)
        self.assertIn("RESULTADO: VERMELHO", saida)


if __name__ == "__main__":
    unittest.main()
