"""F17, passo 0: as sobras da F16 e da F18 + F20 e os achados do repositório privado de 2026-11-12."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, SEM_SYMLINK, caminho_bash


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Incidente(unittest.TestCase):
    """0a: o cenário incidente-chave reprovou 1 de 3 com "anote a data e a hora" como passo 1, antes de fechar."""

    def setUp(self):
        self.inc = ler(".agents/skills/sdd-seguranca/references/INCIDENTE.md")
        self.secao1 = self.inc[self.inc.index("## 1. Fechar a porta"):self.inc.index("## 2. Preservar a evidência")]

    def test_nada_se_pede_antes_de_fechar(self):
        self.assertIn("não peça nada antes de fechar", self.secao1)
        self.assertIn("nem anotar horário", self.secao1)
        self.assertIn("O 1º passo numerado da resposta é o do fechar", self.secao1)

    def test_a_hora_do_fechar_vem_depois(self):
        self.assertNotIn("inclusive do passo 1", self.inc)
        self.assertIn("A do fechar se anota logo **depois** de fechar, nunca antes.", self.inc)

    def test_manifest_registra_o_cenario_executado(self):
        m = json.loads(ler(".agents/skills/sdd-seguranca/manifest.json"))
        self.assertTrue(any(e.startswith("incidente-chave:") for e in m["executados"]))
        self.assertNotIn("Executar o cenário incidente-chave em contexto novo", m["pending"])


@unittest.skipIf(*SEM_SYMLINK)
class FronteiraHelpSemPython(unittest.TestCase):
    """0b: o --help da governanca-fronteira.sh exigia o Python antes de mostrar o uso."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for f in ("bash", "sh", "sed", "grep", "cat", "git"):
            achado = shutil.which(f)
            if achado:
                os.symlink(achado, str(self.bin / f))

    def rodar(self, *args):
        r = subprocess.run([BASH, caminho_bash(RAIZ / "sdd/bin/governanca-fronteira.sh"), *args],
                           capture_output=True, text=True, encoding="utf-8",
                           env=dict(os.environ, PATH=str(self.bin)))
        return r.returncode, r.stdout + r.stderr

    def test_help_sem_python_mostra_o_uso_e_sai_0(self):
        for flag in ("--help", "-h"):
            with self.subTest(flag=flag):
                rc, out = self.rodar(flag)
                self.assertEqual(rc, 0, out)
                self.assertIn("--snapshot <raiz-do-worktree>", out)
                self.assertNotIn("precisa do Python", out)

    def test_o_resto_sem_python_continua_parando(self):
        rc, out = self.rodar("--comparar", "a", "b")
        self.assertEqual(rc, 64, out)
        self.assertIn("precisa do Python", out)


class Textos(unittest.TestCase):
    """0b e 0c: os pequenos de texto."""

    def test_guia_cita_a_linha_gh_do_inventario(self):
        g = ler("docs/pt-BR/guia-do-aluno.md")
        self.assertIn("vem a linha `gh:`", g)
        for estado in ("`ok`", "`ausente`", "`deslogado`", "`sem resposta`"):
            self.assertIn(estado, g)

    def test_o_item_10_do_deploy_diz_a_fase(self):
        for rel in ("docs/adaptation-guide.md", "docs/pt-BR/adaptation-guide.md", "sdd/bin/slot.sh", "sdd/bin/deploy-do-sha.sh"):
            with self.subTest(rel=rel):
                txt = ler(rel)
                self.assertIn("FASE 2, item 10", txt)
                self.assertNotIn("release, item 10", txt)
                self.assertNotIn("item 10 da sdd-release", txt)

    def test_a_recuperacao_roda_os_passos_11_e_12(self):
        for rel in ("sdd/bin/verify-gate.sh", "docs/pt-BR/context-and-governance.md", "docs/pt-BR/guia-do-aluno.md",
                    "docs/pt-BR/verify-gate-contract.md", ".agents/skills/sdd-build/SKILL.md", ".agents/skills/sdd-define/SKILL.md"):
            with self.subTest(rel=rel):
                txt = ler(rel)
                self.assertNotIn("só o passo 11", txt)
                self.assertIn("passos 11", txt)
        for rel in ("docs/context-and-governance.md", "docs/verify-gate-contract.md"):
            with self.subTest(rel=rel):
                self.assertNotIn("only step 11", ler(rel))
                self.assertNotIn("only its step 11", ler(rel))

    def test_resumo_de_abortar_tem_o_127_e_o_ledger(self):
        r = ler(".agents/skills/sdd-release/SKILL.md")
        resumo = r[r.index("## Gates de ABORTAR"):r.index("## Quando pular o SDD formal")]
        self.assertIn("varredura de segurança `2` · `64` · `127`", resumo)
        self.assertIn("ledger-revisao-lint `2`", resumo)
        self.assertIn("playbook-lint `2`", resumo)

    def test_brainstorm_updated_no_mes_da_versao(self):
        b = ler(".agents/skills/sdd-brainstorm/SKILL.md")
        self.assertIn('updated: "2026-11"', b)
        self.assertIn("v2.4.0 · nov/2026", b)   # F17b: Sem terminal


if __name__ == "__main__":
    unittest.main()
