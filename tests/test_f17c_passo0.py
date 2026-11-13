"""F17c, passo 0: as sobras da F17b que o Roberto pôs nesta frente (2026-11-13).

A curadoria do playbook (LM-025 e LM-026 entram; as 13 contagens aplicadas) e o exemplo preenchido da ficha,
que saiu do starter na geração da F17b e volta pelo Open.
"""
from __future__ import annotations

import subprocess
import sys
import unittest

from apoio import RAIZ
from test_gerar_starter import Base

EXEMPLO = ".agents/skills/sdd-handoff/assets/HANDOFF_EXAMPLE.md"


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Curadoria(unittest.TestCase):
    def test_as_duas_licoes_da_f17b_estao_no_playbook(self):
        pb = ler("sdd/playbook.md")
        for lm, trecho in (("LM-025", "`ls a b` sai ≠ 0 quando um dos caminhos não existe"),
                           ("LM-026", "Um teste que procura comando por expressão regular")):
            with self.subTest(lm=lm):
                linha = next((ln for ln in pb.split("\n") if ln.startswith("- [%s]" % lm)), "")
                self.assertIn(trecho, linha)
                self.assertIn("**Do instead:**", linha)

    def test_as_contagens_da_f17b_foram_aplicadas(self):
        pb = ler("sdd/playbook.md")
        for lm, ajudou in (("LM-001", 8), ("LM-018", 1), ("LM-022", 1), ("LM-024", 1)):
            with self.subTest(lm=lm):
                self.assertRegex(pb, r"- \[%s\] ajudou=%d mordeu=0 · conf=2026-11-13" % (lm, ajudou))

    # o formato do playbook real já é conferido num repositório de teste por test_contrato_build_release
    # (o playbook-lint.sh exige git; o Verify Gate roda numa cópia sem .git: LM-006)


class Exemplo(unittest.TestCase):
    def test_a_skill_cita_o_exemplo_e_ele_passa_no_handoff_lint(self):
        self.assertIn("`assets/HANDOFF_EXAMPLE.md`", ler(".agents/skills/sdd-handoff/SKILL.md"))
        r = subprocess.run([sys.executable, "-B", str(RAIZ / "sdd/bin/handoff-lint.py"), str(RAIZ / EXEMPLO)],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_o_exemplo_segue_as_secoes_do_molde(self):
        molde = [ln for ln in ler("sdd/templates/HANDOFF_TEMPLATE.md").split("\n") if ln.startswith("## ")]
        exemplo = [ln for ln in ler(EXEMPLO).split("\n") if ln.startswith("## ")]
        # o exemplo apaga a seção que ficaria vazia (Veredito: nada publicado ainda), como a skill manda
        self.assertEqual([s for s in molde if s != "## Veredito"], exemplo)


class ExemploNoStarter(Base):
    def test_o_exemplo_vai_para_o_starter_sem_o_gate_por_comando(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        ex = self.starter / "skills/sdd-handoff/assets/HANDOFF_EXAMPLE.md"
        self.assertTrue(ex.is_file())
        texto = ex.read_text(encoding="utf-8")
        self.assertNotIn("Verify Gate", texto)
        self.assertNotIn("verify-gate", texto)
        self.assertIn("Padaria Aurora", texto)
        self.assertIn("`assets/HANDOFF_EXAMPLE.md`",
                      (self.starter / "skills/sdd-handoff/SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
