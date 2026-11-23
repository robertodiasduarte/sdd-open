"""F30 S1 — regras de qualidade no AGENTS.md (DEFINE_F30_QUALIDADE_CODIGO, AT-004, AT-005 e parte do AT-009).

AT-004: `init` e `sync` escrevem `### Qualidade ao construir` com as 6 regras gerais e as da stack, lidas do catálogo
pelo único leitor (`sdd/bin/qualidade-regras.sh`); sem stack, só as gerais; `sync` 2 vezes deixa 1 bloco.
AT-005: sem o catálogo, com o catálogo fora do formato ou sem Python, fica o ponteiro e um aviso com a causa.
AT-009: o bloco de segurança continua o que o leitor dele imprime.
"""
from __future__ import annotations

import os
import re
import shutil
import unittest

from apoio import BASH, RAIZ, Sandbox

CLI = RAIZ / "bin/sdd-open.sh"
SCRIPT = RAIZ / "sdd/bin/qualidade-regras.sh"
CATALOGO = RAIZ / ".agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md"
INICIO = "### Qualidade ao construir"
FIM = "Agentes preparados neste projeto:"
GERAIS = 6


def frases(stack: str) -> list:
    """As frases do catálogo de uma stack, lidas à parte do script (o teste não confia no leitor que testa)."""
    texto = CATALOGO.read_text(encoding="utf-8")
    return re.findall(r"^- stack: %s\n- frase: (.+)$" % re.escape(stack), texto, re.M)


class Base(Sandbox):
    def init(self, p, cli=CLI, env=None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, cli, "init", "--yes", "--vendors", "codex"], p, env)
        return rc, out + err

    def bloco(self, p) -> str:
        texto = (p / "AGENTS.md").read_text(encoding="utf-8")
        return texto[texto.index(INICIO):texto.index(FIM)]

    def regras(self, p) -> list:
        return [ln for ln in self.bloco(p).splitlines() if ln.startswith("- ")]

    def qualidade(self, p, *modo: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, *modo, "--raiz", p, "--catalogo", CATALOGO], p)
        return rc, out + err


class AT004Bloco(Base):
    def test_catalogo_tem_6_gerais_e_regras_de_cada_stack(self):
        self.assertEqual(len(frases("todas")), GERAIS)
        for stack in ("python", "js", "ts", "php", "sql"):
            with self.subTest(stack=stack):
                self.assertGreaterEqual(len(frases(stack)), 1)

    def test_python_traz_as_gerais_as_de_python_e_o_ponteiro(self):
        p = self.repo("py")
        self.escreve(p, "pyproject.toml", "[project]\nname = 'x'\n")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        regras = self.regras(p)
        esperado = ["- " + f for f in frases("todas") + frases("python")]
        self.assertEqual(regras[:-1], esperado)
        self.assertIn("qualidade-regras.sh --regras", regras[-1])
        self.assertNotIn("regras de qualidade da stack fora", out)

    def test_js_com_ts_traz_as_duas(self):
        p = self.repo("web")
        self.escreve(p, "package.json", "{}\n")
        self.escreve(p, "tsconfig.json", "{}\n")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        esperado = ["- " + f for f in frases("todas") + frases("js") + frases("ts")]
        self.assertEqual(self.regras(p)[:-1], esperado)

    def test_sem_stack_so_as_gerais(self):
        p = self.repo("vazio")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.regras(p)[:-1], ["- " + f for f in frases("todas")])

    def test_pastas_do_sdd_nao_decidem_a_stack(self):
        # o próprio init grava scripts .py em sdd/ e .agents/: um projeto sem código continua "sem stack"
        p = self.repo("vazio")
        self.init(p)
        rc, out = self.qualidade(p, "--stack")
        self.assertEqual(rc, 0, out)
        self.assertIn("stack: nenhuma reconhecida", out)

    def test_sync_duas_vezes_deixa_um_bloco_e_fica_em_dia(self):
        p = self.repo("py")
        self.escreve(p, "requirements.txt", "requests\n")
        self.init(p)
        self.commit(p, "init")
        for _ in range(2):
            rc, out, err = self.roda([BASH, CLI, "sync", "--yes", "--vendors", "codex"], p)
            self.assertEqual(rc, 0, out + err)
        texto = (p / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(texto.count(INICIO), 1)
        rc, out, err = self.roda([BASH, CLI, "sync", "--check", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)

    def test_stack_nova_deixa_o_bloco_divergente_e_o_sync_refaz(self):
        p = self.repo("app")
        self.init(p)
        self.commit(p, "init")
        self.escreve(p, "composer.json", "{}\n")
        rc, out, err = self.roda([BASH, CLI, "sync", "--check", "--vendors", "codex"], p)
        self.assertEqual(rc, 1, out + err)
        rc, out, err = self.roda([BASH, CLI, "sync", "--yes", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("- " + frases("php")[0], self.regras(p))


class AT005Reserva(Base):
    def pacote(self):
        pacote = self.tmp / "pacote"
        shutil.copytree(str(RAIZ), str(pacote), ignore=shutil.ignore_patterns(".git", "tests", "__pycache__"))
        return pacote

    def test_sem_o_catalogo_fica_o_ponteiro_e_o_aviso(self):
        pacote = self.pacote()
        (pacote / ".agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md").unlink()
        p = self.repo("app")
        rc, out = self.init(p, pacote / "bin/sdd-open.sh")
        self.assertEqual(rc, 0, out)
        self.assertIn("AGENTS.md: regras de qualidade da stack fora (o catálogo de qualidade da sdd-build não está no "
                      "pacote)", out)
        regras = self.regras(p)
        self.assertEqual(len(regras), 1, regras)
        self.assertIn("qualidade-regras.sh --regras", regras[0])

    def test_catalogo_fora_do_formato_diz_a_causa(self):
        pacote = self.pacote()
        cat = pacote / ".agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md"
        cat.write_text(cat.read_text(encoding="utf-8").replace("- stack: todas\n- frase:", "- frase:", 1), encoding="utf-8")
        p = self.repo("app")
        rc, out = self.init(p, pacote / "bin/sdd-open.sh")
        self.assertEqual(rc, 0, out)
        self.assertIn("regras de qualidade da stack fora (o leitor do catálogo falhou: catálogo fora do formato", out)
        self.assertEqual(len(self.regras(p)), 1)

    def test_sem_python_diz_a_causa(self):
        stubs = self.tmp / "sem-python"
        stubs.mkdir()
        for nome in ("python3", "python", "py"):
            s = stubs / nome
            s.write_text("#!/bin/sh\nexit 9009\n", encoding="utf-8")
            s.chmod(0o755)
        env = {k: v for k, v in self.env.items() if k not in ("SDD_PYTHON", "SDD_PYTHON_RESOLVIDO")}
        env["PATH"] = str(stubs) + os.pathsep + env.get("PATH", "")
        p = self.repo("app")
        rc, out = self.init(p, env=env)
        self.assertEqual(rc, 0, out)
        self.assertIn("regras de qualidade da stack fora (sem Python 3.9 para ler o catálogo)", out)

    def test_o_ponteiro_e_o_mesmo_nas_duas_copias(self):
        # LM-005: o init precisa do ponteiro quando o leitor falha; as duas cópias não podem divergir.
        sh = CLI.read_text(encoding="utf-8")
        py = SCRIPT.read_text(encoding="utf-8")
        no_init = re.search(r"^QUA_PONTEIRO='(.*)'$", sh, re.M).group(1)
        partes = re.search(r'^PONTEIRO = \((.*?)\)$', py, re.M | re.S).group(1)
        self.assertEqual(no_init, "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', partes)))


class Leitor(Base):
    def test_regras_cita_os_slots_cheios_e_vazios(self):
        p = self.repo("py")
        self.escreve(p, "app.py", "print(1)\n")
        self.escreve(p, "sdd/config.yaml", 'project:\n  lint_cmd: "ruff check"\n  typecheck_cmd: ""\n')
        rc, out = self.qualidade(p, "--regras")
        self.assertEqual(rc, 0, out)
        self.assertIn("stack: python", out)
        self.assertIn("lint: `ruff check` (project.lint_cmd)", out)
        self.assertIn("tipos: slot vazio (project.typecheck_cmd)", out)
        self.assertIn("Q07", out)
        self.assertNotIn("Q11", out)
        self.assertResultado(out)

    def test_uso_errado_sai_64(self):
        p = self.repo("x")
        for args in ([], ["--regras", "--agents"], ["--xyz"], ["--raiz"]):
            with self.subTest(args=args):
                rc, out, err = self.roda([BASH, SCRIPT, *args], p)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("🛑 qualidade-regras:", err)

    def test_mesma_leitura_do_config_que_o_report_lint(self):
        # LM-005: dois leitores do sdd/config.yaml usam o mesmo texto da função
        def corpo(arq):
            t = arq.read_text(encoding="utf-8")
            return re.search(r"^def ler_mapa\(root, mapa\):\n(.*?)\n\n\n", t, re.M | re.S).group(1)
        rl = corpo(RAIZ / "sdd/bin/report-lint.py").split("\n", 1)[1]   # sem a docstring
        self.assertEqual(corpo(SCRIPT), rl)


class AT009Seguranca(Base):
    def test_bloco_de_seguranca_e_o_que_o_leitor_dele_imprime(self):
        p = self.repo("app")
        self.escreve(p, "package.json", "{}\n")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        texto = (p / "AGENTS.md").read_text(encoding="utf-8")
        seg = texto[texto.index("### Segurança ao construir"):texto.index(INICIO)]
        rc2, esperado, err = self.roda([BASH, RAIZ / "sdd/bin/seguranca-varredura.sh", "--agents", "--raiz", p,
                                        "--catalogo", RAIZ / ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"], p)
        self.assertEqual(rc2, 0, err)
        self.assertEqual([l for l in seg.splitlines() if l.startswith("- ")], esperado.strip().splitlines())


if __name__ == "__main__":
    unittest.main()
