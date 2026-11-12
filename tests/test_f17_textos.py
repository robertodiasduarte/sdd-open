"""F17 (AT-008, AT-009): o que o Open recebeu do starter antes da 1ª geração e os 2 consertos da comparação."""
from __future__ import annotations

import unittest

from apoio import RAIZ


# documentos SDD de uma frente ficam fora do git (não são pacote): a frente que cita o defeito não reprova
DOCUMENTOS_DA_FRENTE = {"reports", "features", "reviews", "handoffs", "releases"}


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class Consertos(unittest.TestCase):
    """AT-009."""

    def test_nenhum_arquivo_do_pacote_cita_rdd_audita_schema(self):
        achados = []
        for p in sorted((RAIZ / ".agents").rglob("*")) + sorted((RAIZ / "sdd").rglob("*")):
            if p.is_file() and not DOCUMENTOS_DA_FRENTE & set(p.parts) and p.suffix in (".md", ".json", ".py", ".sh", ".yaml"):
                if "rdd-audita-schema" in p.read_text(encoding="utf-8", errors="replace"):
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


if __name__ == "__main__":
    unittest.main()
