"""F30 S1 — o checar.sh sugere o linter da stack (DEFINE_F30_QUALIDADE_CODIGO, AT-006).

Projeto com stack reconhecida, sem config de linter e com project.lint_cmd e project.typecheck_cmd vazios ⇒ ⚠️ com o
comando de instalar e o par lint/tipos; `--linter` dá a mesma sugestão em linhas por máquina (a sdd-new-session lê).
Nada é instalado nem gravado: o hash da árvore antes e depois é o mesmo. A tabela de ferramentas do checar.sh é uma
cópia da do catálogo de qualidade da sdd-build; o teste de paridade compara as duas (LM-005).
"""
from __future__ import annotations

import hashlib
import re
import unittest
from pathlib import Path

from test_checar import SCRIPT, Base

CATALOGO = SCRIPT.parents[2] / "sdd-build" / "web" / "references" / "CATALOGO_QUALIDADE.md"
AVISO = "não tem conferência de estilo (linter) nem de tipos configurada"


def ferramentas_do_catalogo() -> dict:
    texto = CATALOGO.read_text(encoding="utf-8")
    secao = texto[texto.index("## Ferramentas por stack"):]
    fichas = {}
    for m in re.finditer(r"^### (\w+)\n((?:- \w+: .+\n?)+)", secao, re.M):
        fichas[m.group(1)] = dict(re.findall(r"^- (\w+): (.+)$", m.group(2), re.M))
    return fichas


class Linter(Base):
    def arvore(self) -> str:
        """Hash de cada arquivo da pasta (inclusive .git) e do git status: igual antes e depois = nada gravado."""
        h = hashlib.sha256()
        for p in sorted(x for x in self.raiz.rglob("*") if x.is_file()):
            h.update(str(p.relative_to(self.raiz)).encode() + b"\0" + p.read_bytes())
        h.update(self.git("status", "--porcelain", "--untracked-files=all").encode())
        return h.hexdigest()

    def linter(self) -> tuple[int, list]:
        rc, out, _ = self.roda("--linter")
        return rc, [l.split("\t") for l in out.splitlines() if l]

    def test_python_sem_linter_sugere_e_nao_grava(self):
        self.escreve("app.py", "print(1)\n")
        self.escreve("pyproject.toml", "[project]\nname = 'x'\n")
        antes = self.arvore()
        out = self.checar()
        self.assertIn("Este projeto em Python " + AVISO, out)
        self.assertIn("python3 -m pip install ruff mypy   (depois: ruff check e mypy .; grave em project.lint_cmd e "
                      "project.typecheck_cmd do sdd/config.yaml)", out)
        rc, linhas = self.linter()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas, [["python", "ruff check", "mypy .", "python3 -m pip install ruff mypy"]])
        self.assertEqual(self.arvore(), antes)

    def test_ts_vale_no_lugar_de_js(self):
        self.escreve("package.json", "{}\n")
        self.escreve("tsconfig.json", "{}\n")
        rc, linhas = self.linter()
        self.assertEqual(rc, 0)
        self.assertEqual([l[0] for l in linhas], ["ts"])
        self.assertEqual(linhas[0][2], "npx tsc --noEmit")

    def test_js_sem_tipos_sugere_so_o_lint(self):
        self.escreve("package.json", "{}\n")
        antes = self.arvore()
        out = self.checar()
        self.assertIn("Este projeto em JavaScript " + AVISO, out)
        self.assertIn("(depois: npx eslint .; grave em project.lint_cmd do sdd/config.yaml)", out)
        self.assertEqual(self.arvore(), antes)

    def test_php(self):
        self.escreve("index.php", "<?php echo 1;\n")
        rc, linhas = self.linter()
        self.assertEqual(rc, 0)
        self.assertEqual(linhas[0][:2], ["php", "vendor/bin/phpcs --standard=PSR12"])

    def test_linter_configurado_nao_sugere(self):
        self.escreve("pyproject.toml", "[project]\nname = 'x'\n\n[tool.ruff]\nline-length = 100\n")
        rc, linhas = self.linter()
        self.assertEqual(rc, 1, linhas)
        self.assertNotIn(AVISO, self.checar())

    def test_script_lint_no_package_json_conta_como_configurado(self):
        self.escreve("package.json", '{"scripts": {"lint": "eslint ."}}\n')
        self.assertEqual(self.linter()[0], 1)

    def test_slot_cheio_nao_sugere(self):
        self.escreve("app.py", "print(1)\n")
        self.escreve("sdd/config.yaml", 'project:\n  name: x\n  lint_cmd: "flake8"\n')
        self.assertEqual(self.linter()[0], 1)
        self.escreve("sdd/config.yaml", 'project:\n  name: x\n  typecheck_cmd: "pyright"\n')
        self.assertEqual(self.linter()[0], 1)

    def test_sem_stack_nao_sugere(self):
        antes = self.arvore()
        rc, linhas = self.linter()
        self.assertEqual(rc, 1, linhas)
        self.assertNotIn(AVISO, self.checar())
        self.assertEqual(self.arvore(), antes)

    def test_py_so_nas_pastas_do_sdd_nao_e_stack(self):
        self.escreve("sdd/bin/x.py", "print(1)\n")
        self.escreve(".agents/skills/s/scripts/y.py", "print(1)\n")
        self.assertEqual(self.linter()[0], 1)

    def test_frente_nao_fala_de_linter(self):
        self.escreve("app.py", "print(1)\n")
        rc, out, _ = self.roda("--frente")
        self.assertNotIn(AVISO, out)


class Paridade(unittest.TestCase):
    def test_tabela_do_checar_e_a_do_catalogo(self):
        texto = SCRIPT.read_text(encoding="utf-8")
        corpo = texto[texto.index("qualidade_tabela() {"):texto.index("qualidade_nome()")]
        campos = [c.replace('\\"', '"') for c in re.findall(r'"((?:[^"\\]|\\.)*)"', corpo)]
        stacks = re.findall(r"^\s+(python|js|ts|php|sql) ", corpo, re.M)
        self.assertEqual(len(campos), 5 * len(stacks))
        do_checar = {s: dict(zip(("detecta", "config", "lint", "tipos", "instalar"), campos[5 * i:5 * i + 5]))
                     for i, s in enumerate(stacks)}
        self.assertEqual(do_checar, ferramentas_do_catalogo())


if __name__ == "__main__":
    unittest.main()
