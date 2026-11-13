"""F17b, passo 0: os pendentes da revisão da F17 que o Roberto pôs nesta frente (2026-11-13).

Cada um tinha "sem ocorrência hoje"; o teste cria a ocorrência e confere o comportamento novo.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from apoio import RAIZ, SEM_CHMOD, Sandbox
from test_gerar_starter import PY, Base

GERADOR = RAIZ / "scripts/gerar-starter.py"


class Gerador(Base):
    def test_arquivo_que_nenhuma_regra_muda_sai_byte_a_byte_mesmo_com_crlf(self):
        crlf = b"# Nota\r\n\r\nTexto com fim de linha do Windows.\r\n"
        alvo = self.open / ".agents/skills/sdd-loop-builder/references/nota-crlf.md"
        alvo.write_bytes(crlf)
        self.reetiquetar()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((self.starter / "skills/sdd-loop-builder/references/nota-crlf.md").read_bytes(), crlf)

    def test_molde_citado_so_no_changelog_nao_vai_para_references(self):
        self.escreve(self.open, ".agents/skills/sdd-loop-builder/CHANGELOG.md",
                     "# Changelog\n\n## 1.0.0\n\n- Antes usava `sdd/templates/DEFINE_TEMPLATE.md`.\n")
        self.reetiquetar()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        skill = self.starter / "skills/sdd-loop-builder"
        self.assertFalse((skill / "references/DEFINE_TEMPLATE.md").exists())
        # o histórico fica como foi escrito (não aponta para um references/ que não existe)
        self.assertIn("`sdd/templates/DEFINE_TEMPLATE.md`", (skill / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_caminho_de_skill_irma_num_script_vira_o_nome_da_pasta(self):
        self.escreve(self.open, ".agents/skills/sdd-loop-builder/scripts/confere.sh",
                     "#!/usr/bin/env bash\n# depois, rode bash .agents/skills/sdd-kb/scripts/gate.sh\necho ok\n")
        self.reetiquetar()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        s = (self.starter / "skills/sdd-loop-builder/scripts/confere.sh").read_text(encoding="utf-8")
        self.assertIn("bash <pasta da skill sdd-kb>/scripts/gate.sh", s)
        self.assertNotIn(".agents/skills/", s)

    @unittest.skipIf(*SEM_CHMOD)
    def test_gate_da_kb_sai_executavel(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(os.access(str(self.starter / "skills/sdd-kb/scripts/gate.sh"), os.X_OK))

    def test_os_dois_workflows_rodam_os_testes_da_raiz_do_mesmo_jeito(self):
        passos = []
        for wf in ("ci.yml", "auto-release.yml"):
            t = (RAIZ / "scripts/starter/raiz/.github/workflows" / wf).read_text(encoding="utf-8")
            ini = t.index("- name: Root tests")
            passos.append(t[ini:t.index("- name:", ini + 1)])
            self.assertLess(t.index("- name: Skill tests"), ini)
        self.assertEqual(passos[0], passos[1])
        self.assertIn("python3 -B -m unittest discover -s tests -p 'test_*.py'", passos[0])


class LintSemBarra(Sandbox):
    def lint(self, texto: str) -> tuple[int, str]:
        pasta = self.tmp / "l"
        self.escreve(pasta, "skills/sdd-kb/SKILL.md", texto)
        rc, out, err = self.roda([PY, "-B", GERADOR, "--lint", pasta], self.tmp)
        return rc, out + err

    def test_pasta_do_init_sem_a_barra_reprova(self):
        for cita in ("`sdd/hooks`", "(sdd/bin)", "sdd/templates.", "pasta sdd/review", "sdd/patterns\n"):
            with self.subTest(cita=cita):
                rc, out = self.lint("Rode o que está em %s agora.\n" % cita)
                self.assertEqual(rc, 65, out)

    def test_nome_mais_longo_nao_e_a_pasta_do_init(self):
        rc, out = self.lint("Os relatórios ficam em `sdd/reviews/` e `sdd/hooksfoo`.\n")
        self.assertEqual(rc, 0, out)


class AuditoriaSemNodeModules(Sandbox):
    def test_claude_md_de_dependencia_nao_entra_no_inventario(self):
        self.escreve(self.tmp, "proj/CLAUDE.md", "# Projeto\n")
        self.escreve(self.tmp, "proj/node_modules/pacote/CLAUDE.md", "# de terceiro\n")
        self.escreve(self.tmp, "proj/node_modules/pacote/AGENTS.md", "# de terceiro\n")
        self.escreve(self.tmp, "proj/sdd/node_modules/x/notas.md", "# de terceiro\n")
        r = subprocess.run([sys.executable, str(RAIZ / ".agents/skills/sdd-auditoria-harness/scripts/collect_evidence.py"),
                            str(self.tmp / "proj")], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        caminhos = {i["path"] for i in json.loads(r.stdout)["items"]}
        self.assertIn("CLAUDE.md", caminhos)
        self.assertFalse([c for c in caminhos if "node_modules" in c], caminhos)


if __name__ == "__main__":
    unittest.main()
