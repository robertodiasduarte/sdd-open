"""Contrato do scripts/check-versions.py: versão X.Y.Z por skill, JSONs coerentes, bump contra a base.

Cada teste monta um repositório com .agents/skills/, commita, marca a tag v1.0.0 e então muda o que
o caso pede. Exit 0 = PASS · 1 = FAIL · 64 = uso.
"""
from __future__ import annotations

import json
import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "scripts/check-versions.py"


def skill(name: str, version: str | None) -> str:
    meta = "metadata:\n  author: teste\n" + ('  version: "' + version + '"\n' if version else "")
    return "---\nname: " + name + "\ndescription: Faz uma coisa.\n" + meta + "---\n\n# Corpo\n"


class CheckVersions(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.skill("sdd-a", "1.0.0")
        self.skill("sdd-b", "2.1.0")
        self.commit(self.r, "base")
        self.git(self.r, "tag", "v1.0.0")

    def skill(self, name: str, version: str | None, corpo: str = "") -> None:
        self.escreve(self.r, ".agents/skills/" + name + "/SKILL.md", skill(name, version) + corpo)

    def check(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--root", self.r, *args], self.r)
        return rc, out + err

    # ── PASS ─────────────────────────────────────────────────────────────────
    def test_estrutura_valida_passa(self):
        rc, out = self.check()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_skill_mudada_com_bump_passa(self):
        self.skill("sdd-a", "1.1.0", "Passo novo.\n")
        rc, out = self.check("--base", "v1.0.0", "--base-obrigatoria")
        self.assertEqual(rc, 0, out)

    def test_skill_nova_passa(self):
        self.skill("sdd-c", "1.0.0")
        rc, out = self.check("--base", "v1.0.0", "--base-obrigatoria")
        self.assertEqual(rc, 0, out)

    def test_skill_que_nao_tinha_versao_na_base_passa(self):
        self.skill("sdd-sem", None)
        self.commit(self.r, "sem versao")
        self.git(self.r, "tag", "v1.0.1")
        self.skill("sdd-sem", "1.0.0")
        rc, out = self.check("--base", "v1.0.1", "--base-obrigatoria")
        self.assertEqual(rc, 0, out)

    def test_base_indisponivel_sem_obrigatoria_cai_para_estrutural(self):
        rc, out = self.check("--base", "v9.9.9")
        self.assertEqual(rc, 0, out)
        self.assertIn("só as checagens estruturais", out)

    # ── FAIL ─────────────────────────────────────────────────────────────────
    def test_skill_mudada_sem_bump_reprova(self):
        self.skill("sdd-a", "1.0.0", "Passo novo.\n")
        rc, out = self.check("--base", "v1.0.0")
        self.assertEqual(rc, 1, out)
        self.assertIn("sdd-a", out)
        self.assertIn("não subiu", out)

    def test_versao_que_desce_reprova(self):
        self.skill("sdd-b", "2.0.9", "Mudou.\n")
        rc, out = self.check("--base", "v1.0.0")
        self.assertEqual(rc, 1, out)

    def test_versao_ausente_reprova(self):
        self.skill("sdd-a", None)
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertIn("sdd-a", out)

    def test_versao_malformada_reprova(self):
        self.skill("sdd-a", "1.0")
        rc, out = self.check()
        self.assertEqual(rc, 1, out)

    def test_manifest_divergente_reprova(self):
        self.escreve(self.r, ".agents/skills/sdd-a/manifest.json", json.dumps(dict(version="0.9.0")))
        rc, out = self.check()
        self.assertEqual(rc, 1, out)
        self.assertIn("manifest.json", out)

    def test_evals_divergente_reprova(self):
        self.escreve(self.r, ".agents/skills/sdd-a/evals/cases.json", json.dumps(dict(version="0.9.0")))
        rc, out = self.check()
        self.assertEqual(rc, 1, out)

    def test_manifest_sem_chave_version_passa(self):
        self.escreve(self.r, ".agents/skills/sdd-a/manifest.json", json.dumps(dict(pending=[])))
        rc, out = self.check()
        self.assertEqual(rc, 0, out)

    def test_base_obrigatoria_que_nao_resolve_reprova(self):
        rc, out = self.check("--base", "v9.9.9", "--base-obrigatoria")
        self.assertEqual(rc, 1, out)
        self.assertIn("indisponível", out)

    def test_base_obrigatoria_sem_base_reprova(self):
        rc, out = self.check("--base-obrigatoria")
        self.assertEqual(rc, 1, out)

    def test_opcao_desconhecida_e_64(self):
        rc, out = self.check("--nao-existe")
        self.assertEqual(rc, 64, out)


class SkillsDoPacote(Sandbox):
    def test_as_13_skills_do_open_passam(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], RAIZ)
        self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    unittest.main()
