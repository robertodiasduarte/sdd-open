"""F30 S3 — o texto das skills leva as métricas no diff (DEFINE_F30_QUALIDADE_CODIGO, AT-022).

A `sdd-build` do Open chama o `metricas-diff.sh` antes do relatório e cola a seção; o molde tem a seção; o config tem os 4
limites; a EVIDENCIA e as convenções descrevem o contrato; o texto mora em `web/references/metricas-do-diff.md` e chega ao
starter sem citar `sdd/bin/` (LM-035).
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ
from test_gerar_starter import Base

BUILD = RAIZ / ".agents/skills/sdd-build"
REF = BUILD / "web/references/metricas-do-diff.md"
F29 = ("Não cite nem resuma", "comece com esta linha", "versão atual: http")


def ler(rel: str) -> str:
    return re.sub(r"\s+", " ", (RAIZ / rel).read_text(encoding="utf-8"))


class AT022Textos(unittest.TestCase):
    def test_build_chama_antes_do_relatorio(self):
        skill = ler(".agents/skills/sdd-build/SKILL.md")
        cinco_b = skill[skill.index("**5b."):skill.index("**5c.")]
        self.assertIn("bash sdd/bin/metricas-diff.sh", cinco_b)
        self.assertIn("## Qualidade (avisos)", cinco_b)
        self.assertIn("web/references/metricas-do-diff.md", cinco_b)
        self.assertIn("Qualidade (avisos)", skill[skill.index("### 6. BUILD_REPORT"):])

    def test_teto_de_linhas(self):
        for rel in (".agents/skills/sdd-build/SKILL.md", ".agents/skills/sdd-build/web/MODO_WEB.md"):
            self.assertLessEqual(len((RAIZ / rel).read_text(encoding="utf-8").splitlines()), 500, rel)

    def test_referencia(self):
        texto = re.sub(r"\s+", " ", REF.read_text(encoding="utf-8"))
        for trecho in ("não medido", "lizard", "jscpd", "jscpd . --min-tokens 50 --min-lines 0", "python3 -m pip install lizard", "npm install -g jscpd",
                       "## Qualidade (avisos)", "`qualidade`", "só avisa"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)
        self.assertNotIn("sdd/bin/", texto)
        for padrao in F29:
            self.assertNotIn(padrao, texto)

    def test_modo_web_aponta(self):
        self.assertIn("references/metricas-do-diff.md", ler(".agents/skills/sdd-build/web/MODO_WEB.md"))

    def test_molde_config_contratos(self):
        for rel in ("sdd/templates/BUILD_REPORT_TEMPLATE.md", ".agents/skills/sdd-build/web/assets/BUILD_REPORT_TEMPLATE.md"):
            self.assertRegex((RAIZ / rel).read_text(encoding="utf-8"), r"(?m)^## Qualidade \(avisos\)$")
        config = (RAIZ / "sdd/config.example.yaml").read_text(encoding="utf-8")
        bloco = config[config.index("\nqualidade:\n"):]
        for chave, valor in (("max_complexidade", 10), ("max_linhas", 60), ("max_parametros", 5), ("min_tokens", 50)):
            self.assertRegex(bloco, r"(?m)^  %s: %d$" % (chave, valor))
        self.assertIn("## Qualidade (avisos)", ler("sdd/templates/fragments/EVIDENCIA.md"))
        self.assertIn("`metricas-diff.sh`", ler("docs/cli-conventions.md"))


class AT022Starter(Base):
    def test_starter_leva_as_metricas_sem_sdd_bin(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        build = self.starter / "skills" / "sdd-build"
        copia = build / "references" / "metricas-do-diff.md"
        self.assertTrue(copia.is_file())
        for p in (build / "SKILL.md", copia):
            self.assertNotIn("sdd/bin/", p.read_text(encoding="utf-8"))
        self.assertIn("references/metricas-do-diff.md", (build / "SKILL.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
