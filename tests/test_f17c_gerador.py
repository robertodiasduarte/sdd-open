"""F17c (AT-002, AT-003, AT-008, AT-009): define, design e build do starter saem só do modo web da skill do Open.

O modo mora em `.agents/skills/<skill>/web/` (MODO_WEB.md, references/, assets/) e `scripts/starter/modos.tsv` diz a
pasta-base (3ª coluna): o que o modo cita sai de lá com o mesmo caminho relativo (Decision 1 do DESIGN_F17C).
"""
from __future__ import annotations

import re
import shutil

from apoio import RAIZ
from test_gerar_starter import DA_F17C, NO_STARTER, PY, Base, arvore, skill_minima

DO_OPEN = ("references/cartografo.md", "references/modos-e-retry.md", "references/contexto-fresco.md")


def versao_do_open(skill: str) -> str:
    texto = (RAIZ / ".agents/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
    return re.search(r'version: "([^"]+)"', texto).group(1)


class ModoWeb(Base):
    def test_at002_as_3_saem_so_do_modo_web(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for skill in DA_F17C:
            with self.subTest(skill=skill):
                self.assertIn("%s: " % skill, out)
                self.assertRegex(out, r"✅ %s: .*de modo \(web/MODO_WEB\.md\)" % skill)
                d = self.starter / "skills" / skill
                web = RAIZ / ".agents/skills" / skill / "web"
                gerados = set(arvore(d))
                do_web = {p.relative_to(web).as_posix() for p in web.rglob("*") if p.is_file()} - {"MODO_WEB.md"}
                # só o que o modo cita, do web/, mais o que toda skill gerada tem
                self.assertTrue(gerados - {"SKILL.md", "agents/openai.yaml", "GERADO.txt"} <= do_web, gerados - do_web)
                self.assertIn("references/como-falar.md", gerados)      # o publish-check do starter exige
                self.assertFalse(any(r.startswith(("scripts/", "tests/")) for r in gerados), gerados)
                for rel in DO_OPEN:
                    self.assertNotIn(rel, gerados)
                # nota 11 da revisão do DESIGN: cada arquivo levado é o do web/ (o como-falar e o aplicar-migration
                # têm o mesmo nome no Open); só a URL do Open muda para a do starter
                for rel in sorted(gerados - {"SKILL.md", "agents/openai.yaml", "GERADO.txt"}):
                    origem = (web / rel).read_text(encoding="utf-8").replace(
                        "https://github.com/robertodiasduarte/sdd-open/releases/latest",
                        "https://github.com/robertodiasduarte/sdd-starter/releases/latest")
                    with self.subTest(arquivo="%s/%s" % (skill, rel)):
                        self.assertEqual((d / rel).read_text(encoding="utf-8"), origem)
                s = (d / "SKILL.md").read_text(encoding="utf-8")
                fm = s[:s.index("\n---\n", 4)]
                self.assertIn("name: %s" % skill, fm)
                self.assertIn('version: "%s"' % versao_do_open(skill), fm)
                self.assertNotIn("SDD Open —", fm)                      # a description do Open nunca vai
                self.assertIn("compatibility:", fm)
                self.assertEqual(s.count("`%s v%s · nov/2026 · versão atual: https://github.com/robertodiasduarte/"
                                         "sdd-starter/releases/latest`" % (skill, versao_do_open(skill))), 1)
                self.assertIn("## Como falar com o aluno", s)
                self.assertNotIn("web/MODO_WEB.md", s)
        # o aplicar-migration do build é o do modo (o do Open cita evidence/ e o report-lint)
        mig = (self.starter / "skills/sdd-build/references/aplicar-migration.md").read_text(encoding="utf-8")
        self.assertNotIn("report-lint", mig)
        self.assertNotIn("MIG-001.log", mig)

    def test_sem_pasta_base_o_modo_continua_na_raiz_da_skill(self):
        # a release (F17b) não tem 3ª coluna: o que o modo cita vem da raiz da skill, como antes
        modo = self.open / ".agents/skills/sdd-release/references/MODO_INICIANTE.md"
        modo.write_text(modo.read_text(encoding="utf-8") + "\nVeja `references/um.md`.\n", encoding="utf-8")
        self.escreve(self.open, ".agents/skills/sdd-release/references/um.md", "Um.\n")
        self.reetiquetar()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertTrue((self.starter / "skills/sdd-release/references/um.md").is_file())

    def test_at003_modo_web_quebrado_sai_65_sem_gravar(self):
        tsv = self.open / "scripts/starter/modos.tsv"
        modo = self.open / ".agents/skills/sdd-build/web/MODO_WEB.md"
        casos = {
            "pasta-base que não existe": lambda: tsv.write_text(
                tsv.read_text(encoding="utf-8").replace("sdd-build\tweb/MODO_WEB.md\tweb", "sdd-build\tweb/MODO_WEB.md\tnao-ha"),
                encoding="utf-8"),
            "pasta-base que sai da skill": lambda: tsv.write_text(
                tsv.read_text(encoding="utf-8").replace("sdd-build\tweb/MODO_WEB.md\tweb", "sdd-build\tweb/MODO_WEB.md\t.."),
                encoding="utf-8"),
            "linha com 4 colunas": lambda: tsv.write_text(
                tsv.read_text(encoding="utf-8").replace("sdd-build\tweb/MODO_WEB.md\tweb", "sdd-build\tweb/MODO_WEB.md\tweb\tx"),
                encoding="utf-8"),
            "cita arquivo que não existe na pasta-base": lambda: modo.write_text(
                modo.read_text(encoding="utf-8") + "\nVeja `references/nao-existe.md`.\n", encoding="utf-8"),
            # sabotagem 2: sem a guarda de `..`, este escaparia da skill (e da saída) e o lint não o veria
            "cita arquivo fora da pasta-base": lambda: modo.write_text(
                modo.read_text(encoding="utf-8") + "\nVeja `references/" + "../" * 5 + "sdd/templates/HANDOFF_TEMPLATE.md`.\n",
                encoding="utf-8"),
            "cita o arquivo do Open (fora do web/)": lambda: modo.write_text(
                modo.read_text(encoding="utf-8") + "\nVeja `references/contexto-fresco.md`.\n", encoding="utf-8"),
            "cita caminho do init": lambda: modo.write_text(
                modo.read_text(encoding="utf-8") + "\nRode `bash sdd/bin/verify-gate.sh`.\n", encoding="utf-8"),
        }
        orig_tsv, orig_modo = tsv.read_bytes(), modo.read_bytes()
        for nome, mexe in casos.items():
            with self.subTest(caso=nome):
                tsv.write_bytes(orig_tsv)
                modo.write_bytes(orig_modo)
                mexe()
                self.reetiquetar()
                antes = arvore(self.starter)
                rc, out, err = self.gerar()
                self.assertEqual(rc, 65, out + err)
                self.assertEqual(arvore(self.starter), antes)

    def test_at003_a_copia_crua_das_3_reprova_no_lint(self):
        for skill in DA_F17C:
            with self.subTest(skill=skill):
                crua = self.tmp / ("crua-" + skill)
                shutil.copytree(str(RAIZ / ".agents/skills" / skill), str(crua / skill))
                shutil.rmtree(str(crua / skill / "web"))    # só o caminho do Open
                rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", crua], self.tmp)
                self.assertEqual(rc, 65, out + err)
                self.assertIn("sdd/", out)

    def test_at009_versao_que_nao_sobe_nas_3(self):
        for skill in DA_F17C:
            with self.subTest(skill=skill):
                self.assertGreater(tuple(map(int, versao_do_open(skill).split("."))),
                                   tuple(map(int, NO_STARTER[skill].split("."))))
                st = self.replica("st-%s" % skill)
                self.escreve(st, "skills/%s/SKILL.md" % skill, skill_minima(skill, versao_do_open(skill), "2026-11"))
                self.commit(st, "mesma versao")
                rc, out, err = self.gerar(st)
                self.assertEqual(rc, 65, out + err)
                self.assertIn("%s: a cópia gerada mudou e a versão não subiu" % skill, out)

    def test_at008_um_byte_trocado_no_build_gerado_e_acusado(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.commit(self.starter, "gerado")
        rc, out, err = self.roda([PY, "-B", "scripts/check-gerado.py"], self.starter)
        self.assertEqual(rc, 0, out + err)
        alvo = self.starter / "skills/sdd-build/references/verify-gate.md"
        alvo.write_bytes(alvo.read_bytes() + b" ")
        rc, out, err = self.roda([PY, "-B", "scripts/check-gerado.py"], self.starter)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("sdd-build", out + err)


if __name__ == "__main__":
    import unittest
    unittest.main()
