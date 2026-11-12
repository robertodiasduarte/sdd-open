"""F17 (AT-008, AT-009): o que o Open recebeu do starter antes da 1ª geração e os 2 consertos da comparação."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from apoio import RAIZ


# documentos SDD de uma frente ficam fora do git (não são pacote): a frente que cita o defeito não reprova
DOCUMENTOS_DA_FRENTE = {"reports", "features", "reviews", "handoffs", "releases"}


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Consertos(unittest.TestCase):
    """AT-009."""

    def test_nenhum_arquivo_do_pacote_cita_skill_rdd_audita(self):
        achados = []
        for p in sorted((RAIZ / ".agents").rglob("*")) + sorted((RAIZ / "sdd").rglob("*")):
            if p.is_file() and not DOCUMENTOS_DA_FRENTE & set(p.parts) and p.suffix in (".md", ".json", ".py", ".sh", ".yaml"):
                if "rdd-audita-" in p.read_text(encoding="utf-8", errors="replace"):
                    achados.append(str(p.relative_to(RAIZ)))
        self.assertEqual(achados, [])

    def test_governanca_prova_pos_build_pela_leitura_do_aplicar_a_migration(self):
        cat = ler(".agents/skills/sdd-governanca/references/CATALOGO_GOVERNANCA.md")
        self.assertIn("`prova pós-build` = `sim`", cat)
        self.assertIn("o passo *Aplicar a migration* da `sdd-build` prova por leitura", cat)
        for rel in (".agents/skills/sdd-governanca/references/PROCEDIMENTO.md",
                    ".agents/skills/sdd-governanca/assets/GOVERNANCA_REVIEW_TEMPLATE.md"):
            with self.subTest(rel=rel):
                self.assertIn("No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura", ler(rel))
        # a última célula de cada linha G é "sim" ou "—", nunca número de checklist de outra skill
        for linha in cat.splitlines():
            if linha.startswith("| G"):
                with self.subTest(linha=linha[:8]):
                    self.assertIn(linha.rstrip(" |").split("|")[-1].strip(), ("sim", "—"))

    def test_molde_do_brainstorm_sem_restos_de_outro_dominio(self):
        t = ler("sdd/templates/BRAINSTORM_TEMPLATE.md")
        for resto in ("pydantic", "gcp", "Terraform", "functions/ | gen/"):
            with self.subTest(resto=resto):
                self.assertNotIn(resto, t)
        self.assertIn("| Likely Location | {path or N/A} |", t)


class AuditoriaVariosMotores(unittest.TestCase):
    """AT-008: a sdd-auditoria-harness do Open só olhava .claude/ e voltava vazia num projeto de outro motor."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="auditoria-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def escreve(self, rel, txt="# x\n"):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")

    def inventario(self):
        r = subprocess.run([sys.executable, str(RAIZ / ".agents/skills/sdd-auditoria-harness/scripts/collect_evidence.py"),
                            str(self.tmp)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        return {i["path"]: i["type"] for i in json.loads(r.stdout)["items"]}

    def test_projeto_so_com_agents_e_codex_nao_volta_vazio(self):
        self.escreve("AGENTS.md")
        self.escreve(".agents/skills/minha/SKILL.md", "---\nname: minha\n---\n")
        self.escreve(".agents/agents/revisor.md")
        self.escreve(".agents/scripts/x.sh", "echo\n")
        self.escreve(".codex/skills/outra/SKILL.md", "---\nname: outra\n---\n")
        self.escreve(".codex/prompts/p.md")
        self.escreve(".codex/config.toml", "x = 1\n")
        inv = self.inventario()
        esperado = {"AGENTS.md": "fonte-de-verdade", ".agents/skills/minha/SKILL.md": "skill",
                    ".agents/agents/revisor.md": "agente", ".agents/scripts/x.sh": "script",
                    ".codex/skills/outra/SKILL.md": "skill", ".codex/prompts/p.md": "comando",
                    ".codex/config.toml": "settings"}
        for caminho, tipo in esperado.items():
            with self.subTest(caminho=caminho):
                self.assertEqual(inv.get(caminho), tipo, inv)

    def test_skill_cita_os_motores_e_a_precedencia(self):
        s = ler(".agents/skills/sdd-auditoria-harness/SKILL.md")
        for termo in ("AGENTS.md", ".agents/skills", ".codex/", "sdd/_index.md", "@AGENTS.md"):
            with self.subTest(termo=termo):
                self.assertIn(termo, s)


class PromptBuilderSemScript(unittest.TestCase):
    """AT-008: sem o prompt-drift-scan.sh (projeto sem init, agente sem terminal) o drift se confere à mão."""

    def test_drift_a_mao_quando_o_script_nao_existe(self):
        s = ler(".agents/skills/sdd-prompt-builder/references/sdd-integration.md")
        trecho = s[s.index("## Drift detection"):]
        self.assertIn("**Sem o script**", trecho)
        self.assertIn("se nada centraliza, as assinaturas do SDK são o sinal", trecho)


class NewSessionDoStarter(unittest.TestCase):
    """AT-008: C1–C4 da comparação (evidence/F17_STARTER_GERADO/COMPARACAO-terreno.md)."""

    def setUp(self):
        self.s = ler(".agents/skills/sdd-new-session/SKILL.md")

    def test_c1_pre_voo_a_mao_com_a_nuvem_e_os_4_casos(self):
        mao = self.s[self.s.index("### Pré-voo à mão"):]
        mao = mao[:mao.index("Depois, o remoto")]
        for termo in ("Pasta sincronizada", "Library/Mobile Documents", "OneDrive", "Mesa e Documentos",
                      "A. **Pasta pessoal**", "B. **Git numa subpasta**", "C. **Pasta vazia**", "D. **Arquivos sem git**",
                      "Get-ChildItem"):
            with self.subTest(termo=termo):
                self.assertIn(termo, mao)

    def test_c2_skills_fora_do_git_vao_para_a_frente(self):
        self.assertIn("**Skills do agente fora do git**", self.s)
        self.assertIn("`git ls-files <pasta>` vazio", self.s)
        self.assertIn("sdd-release", self.s[self.s.index("## Passo 2"):self.s.index("## Passo 3")])
        self.assertIn("se a cópia for negada, **não pare**", self.s)

    def test_c3_as_duas_notas_do_por_que(self):
        porque = self.s[self.s.index("## Por que cada regra existe"):]
        self.assertIn("**A mesma branch não abre em duas worktrees**", porque)
        self.assertIn("O `-d` minúsculo é proteção", porque)

    def test_c4_textos_curtos(self):
        self.assertIn("nada vai para a internet; nenhum arquivo seu é alterado", self.s)
        self.assertIn("nenhum cd muda isso. Build, commit e push rodam lá dentro.`", self.s)
        g = ler(".agents/skills/sdd-new-session/references/como-falar.md")
        self.assertIn("- commit —", g)
        self.assertIn("- dependências —", g)


if __name__ == "__main__":
    unittest.main()
