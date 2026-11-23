"""F30 S1 — lint e tipos com evidência no BUILD_REPORT (DEFINE_F30_QUALIDADE_CODIGO, AT-001 e AT-002).

AT-001: com `project.lint_cmd` (ou `typecheck_cmd`) cheio, o `report-lint.py` exige `LINT.log` (ou `TIPOS.log`) com a
1ª linha `$ <comando do slot>[ arquivos]`, fora do .gitignore, terminando em `[exit=0]`; `[exit≠0]` só passa, com
aviso, quando o `*.antes.log` do mesmo comando também falhava (dívida antiga).
AT-002: com os dois slots vazios (ou sem config), nunca há violação; sem a linha `lint: slot vazio`, um aviso.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, Sandbox

SCRIPT = "sdd/bin/report-lint.py"
F = "EXEMPLO"
EV = "sdd/reports/evidence/%s/" % F
RELATORIO = ("# BUILD REPORT\n\n| ID | Critério | Resultado | Evidência |\n|---|---|---|---|\n"
             "| AT-001 | x | false | — |\n\navaliador: N.A. (1 camada)\n")


def log(cmd: str, rc: int = 0, corpo: str = "ok\n") -> str:
    return "$ %s\n%s[exit=%d]\n" % (cmd, corpo, rc)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)
        self.escreve(self.r, "sdd/features/DEFINE_%s.md" % F, "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n```\n")

    def config(self, lint: str = "", tipos: str = "") -> None:
        self.escreve(self.r, "sdd/config.yaml",
                     'project:\n  name: x\n  lint_cmd: "%s"\n  typecheck_cmd: "%s"\nlayers:\n  api: ""\n' % (lint, tipos))

    def lint(self, texto: str = RELATORIO) -> tuple[int, str]:
        nome = "sdd/reports/BUILD_REPORT_%s.md" % F
        self.escreve(self.r, nome, texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, nome], self.r)
        return rc, out + err


class AT001SlotCheio(Base):
    def test_lint_cheio_sem_log_reprova_com_conserto(self):
        self.config(lint="ruff check")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("[lint] project.lint_cmd está cheio", out)
        self.assertIn("LINT.log` não existe", out)
        self.assertIn("1ª linha `$ <comando>`", out)   # o conserto da classe
        self.assertResultado(out)

    def test_log_certo_com_os_arquivos_da_tarefa_aprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.log", log("ruff check src/a.py src/b.py", 0, "All checks passed!\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertNotIn("lint: slot vazio", out)

    def test_log_de_outro_comando_reprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.log", log("ruff checkx a.py"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("não o comando do slot (`ruff check`)", out)

    def test_log_vermelho_reprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.log", log("ruff check a.py", 1, "a.py:1:1: F401 unused import\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("terminou em `[exit=1]`", out)

    def test_log_sem_exit_no_fim_reprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.log", "$ ruff check a.py\nAll checks passed!\n[exit=]\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("a última linha não é `[exit=<n>]`", out)

    def test_log_sem_primeira_linha_de_comando_reprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.log", "All checks passed!\n[exit=0]\n")
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("a 1ª linha não é `$ <comando>`", out)

    def test_log_ignorado_pelo_git_reprova(self):
        self.config(lint="ruff check")
        self.escreve(self.r, ".gitignore", "*.log\n")
        self.escreve(self.r, EV + "LINT.log", log("ruff check a.py"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("o git o IGNORA", out)

    def test_tipos_cheio_exige_tipos_log(self):
        self.config(lint="ruff check", tipos="mypy .")
        self.escreve(self.r, EV + "LINT.log", log("ruff check a.py"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("project.typecheck_cmd está cheio", out)
        self.assertIn("TIPOS.log` não existe", out)
        self.escreve(self.r, EV + "TIPOS.log", log("mypy .", 0, "Success: no issues found\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)

    def test_divida_antiga_com_log_de_antes_vira_aviso(self):
        self.config(tipos="mypy .")
        self.escreve(self.r, EV + "TIPOS.antes.log", log("mypy .", 1, "old.py:3: error: x\n"))
        self.escreve(self.r, EV + "TIPOS.log", log("mypy .", 1, "old.py:3: error: x\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertIn("já falhava antes do build", out)

    def test_verde_antes_e_vermelho_depois_reprova(self):
        self.config(tipos="mypy .")
        self.escreve(self.r, EV + "TIPOS.antes.log", log("mypy .", 0))
        self.escreve(self.r, EV + "TIPOS.log", log("mypy .", 1, "novo.py:1: error: x\n"))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)
        self.assertIn("terminou em `[exit=1]`", out)

    def test_log_de_antes_de_outro_comando_nao_vale(self):
        self.config(lint="ruff check")
        self.escreve(self.r, EV + "LINT.antes.log", log("ruff check outro.py", 1))
        self.escreve(self.r, EV + "LINT.log", log("ruff check a.py", 1))
        rc, out = self.lint()
        self.assertEqual(rc, 1, out)


class AT002SlotVazio(Base):
    def test_slots_vazios_com_a_linha_aprova_sem_aviso(self):
        self.config()
        rc, out = self.lint(RELATORIO + "\nlint: slot vazio\n")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("escreva a linha `lint: slot vazio`", out)

    def test_slots_vazios_sem_a_linha_aprova_com_aviso(self):
        self.config()
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertIn("escreva a linha `lint: slot vazio`", out)

    def test_sem_config_vale_como_vazio(self):
        rc, out = self.lint()
        self.assertEqual(rc, 0, out)
        self.assertIn("escreva a linha `lint: slot vazio`", out)

    def test_a_linha_dentro_de_bloco_cercado_nao_conta(self):
        self.config()
        rc, out = self.lint(RELATORIO + "\n```text\nlint: slot vazio\n```\n")
        self.assertEqual(rc, 0, out)
        self.assertIn("escreva a linha `lint: slot vazio`", out)


if __name__ == "__main__":
    unittest.main()
