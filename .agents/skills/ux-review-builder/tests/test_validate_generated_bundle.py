import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "validate_generated_bundle.py"
spec = importlib.util.spec_from_file_location("validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

REVIEW_TEMPLATE_MIN = (
    "Canonical Conformance\nUX/CX Findings\nUniversal Principles Check\n"
    "Required States\nAccessibility and Responsiveness\nDesign Handoff\n"
    "Gate Outcome\nCanonical Evolution Proposals\nRegra canonica\nNAO AVALIAVEL\nBLOCKED FOR DESIGN\n"
)
CHILD_MIN = (
    "UX_STANDARD.md UX_REVIEW_TEMPLATE.md MUST NAO AVALIAVEL "
    "Os documentos ficam em `sdd/` (ou `.claude/sdd/`), sem subpastas. nao editar"
)
CORE = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11)) + "\n"


def write_bundle(root: Path, standard: str, template: str, child: str) -> None:
    (root / "UX_STANDARD.md").write_text(standard, encoding="utf-8")
    (root / "UX_REVIEW_TEMPLATE.md").write_text(template, encoding="utf-8")
    (root / "ux-review").mkdir(exist_ok=True)
    (root / "ux-review" / "SKILL.md").write_text(child, encoding="utf-8")


class ValidatorTests(unittest.TestCase):
    def test_valid_minimal_bundle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            write_bundle(root, core + "\n", REVIEW_TEMPLATE_MIN, CHILD_MIN)
            result = validator.validate(root)
            self.assertTrue(result["pass"], result)

    def test_missing_core_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "UX_STANDARD.md").write_text("UX-CORE-001\n", encoding="utf-8")
            (root / "UX_REVIEW_TEMPLATE.md").write_text("", encoding="utf-8")
            result = validator.validate(root)
            self.assertFalse(result["pass"])
            self.assertTrue(any("UX-CORE-010" in e for e in result["errors"]))

    def test_child_pointing_to_subfolder_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            write_bundle(root, core, REVIEW_TEMPLATE_MIN, CHILD_MIN + "\nLer `sdd/features/DEFINE_X.md`.")
            result = validator.validate(root)
            self.assertFalse(result["pass"])
            self.assertIn("SUBPASTA_SDD_NA_FILHA", result["errors"])

    def test_accented_phrasing_passes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            template = REVIEW_TEMPLATE_MIN.replace("Regra canonica", "Regra canônica")
            child = CHILD_MIN.replace("nao editar", "Não altera o UX_STANDARD.md")
            write_bundle(root, core, template, child)
            result = validator.validate(root)
            self.assertTrue(result["pass"], result)

    def test_empty_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_bundle(root, "", "", "")
            result = validator.validate(root)
            self.assertFalse(result["pass"])
            self.assertIn("PRINCIPIO_UNIVERSAL_AUSENTE:UX-CORE-001", result["errors"])
            self.assertIn("REGRA_DE_PASTA_AUSENTE", result["errors"])

    def test_cited_rule_id_is_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"| UX-CORE-{i:03d} | regra |" for i in range(1, 11))
            standard = core + "\n| UX-VIS-001 | regra |\n\n## Exceções\n| UX-VIS-001 | exceção aceita |\n"
            write_bundle(root, standard.replace("| UX-VIS-001 | exceção", "| Regra UX-VIS-001 | exceção"), REVIEW_TEMPLATE_MIN, CHILD_MIN)
            self.assertTrue(validator.validate(root)["pass"])
            write_bundle(root, core + "\n| UX-VIS-001 | a |\n| UX-VIS-001 | b |\n", REVIEW_TEMPLATE_MIN, CHILD_MIN)
            self.assertIn("REVISAR_IDS_REPETIDOS:UX-VIS-001", validator.validate(root)["errors"])

    def test_exception_row_in_template_format_is_not_a_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"| UX-CORE-{i:03d} | regra |" for i in range(1, 11))
            standard = core + "\n| UX-VIS-001 | regra |\n\n## Exceções aceitas\n\n| UX-VIS-001 | exceção | motivo |\n| UX-CORE-005 | exceção | motivo |\n\n## Histórico de revisões\n| UX-VIS-001 | alterada |\n"
            write_bundle(root, standard, REVIEW_TEMPLATE_MIN, CHILD_MIN)
            self.assertTrue(validator.validate(root)["pass"], validator.validate(root))

    def test_ux_review_above_the_project_is_not_used(self):
        with tempfile.TemporaryDirectory() as td:
            outside = Path(td)
            docs = outside / "projeto" / "sdd"
            docs.mkdir(parents=True)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            (docs / "UX_STANDARD.md").write_text(core, encoding="utf-8")
            (docs / "UX_REVIEW_TEMPLATE.md").write_text(REVIEW_TEMPLATE_MIN, encoding="utf-8")
            (outside / "ux-review").mkdir()
            (outside / "ux-review" / "SKILL.md").write_text(CHILD_MIN, encoding="utf-8")
            self.assertIn("UX_REVIEW_SKILL_AUSENTE", validator.validate(docs)["errors"])

    def test_child_without_existing_folder_fallback_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            write_bundle(root, core, REVIEW_TEMPLATE_MIN, CHILD_MIN.replace(" (ou `.claude/sdd/`)", ""))
            self.assertIn("REGRA_DE_PASTA_AUSENTE", validator.validate(root)["errors"])

    def test_any_subfolder_under_sdd_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            for caminho in ("sdd/feature/DEFINE_X.md", "sdd/ux.review/DEFINE_X.md"):
                write_bundle(root, core, REVIEW_TEMPLATE_MIN, CHILD_MIN + f" Ler {caminho}.")
                self.assertIn("SUBPASTA_SDD_NA_FILHA", validator.validate(root)["errors"], caminho)

    def test_agent_layout_finds_ux_review_in_project_root(self):
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            docs = project / "sdd"
            docs.mkdir()
            core = "\n".join(f"UX-CORE-{i:03d}" for i in range(1, 11))
            (docs / "UX_STANDARD.md").write_text(core, encoding="utf-8")
            (docs / "UX_REVIEW_TEMPLATE.md").write_text(REVIEW_TEMPLATE_MIN, encoding="utf-8")
            (project / "ux-review").mkdir()
            (project / "ux-review" / "SKILL.md").write_text(CHILD_MIN, encoding="utf-8")
            result = validator.validate(docs)
            self.assertTrue(result["pass"], result)

    def test_shipped_templates_pass_with_separate_skill_dir(self):
        with tempfile.TemporaryDirectory() as td:
            docs = Path(td) / "sdd"
            skill = Path(td) / "ux-review"
            docs.mkdir()
            skill.mkdir()
            assets = SKILL_ROOT / "assets"
            shutil.copy(assets / "UX_STANDARD_TEMPLATE.md", docs / "UX_STANDARD.md")
            shutil.copy(assets / "UX_REVIEW_TEMPLATE.md", docs / "UX_REVIEW_TEMPLATE.md")
            shutil.copy(assets / "UX_REVIEW_SKILL_TEMPLATE.md", skill / "SKILL.md")
            result = validator.validate(docs, skill)
            self.assertTrue(result["pass"], result)

    def test_bundle_without_lenses_passes_with_warnings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_bundle(root, CORE, REVIEW_TEMPLATE_MIN, CHILD_MIN)
            result = validator.validate(root)
            self.assertTrue(result["pass"], result)
            self.assertEqual(result["errors"], [])
            self.assertIn("LENTES_COGNITIVAS_AUSENTES:UX_REVIEW_TEMPLATE.md", result["warnings"])
            self.assertIn("LENTES_COGNITIVAS_AUSENTES:ux-review", result["warnings"])

    def test_shipped_templates_have_no_lens_warning(self):
        with tempfile.TemporaryDirectory() as td:
            docs = Path(td) / "sdd"
            skill = Path(td) / "ux-review"
            docs.mkdir()
            skill.mkdir()
            assets = SKILL_ROOT / "assets"
            shutil.copy(assets / "UX_STANDARD_TEMPLATE.md", docs / "UX_STANDARD.md")
            shutil.copy(assets / "UX_REVIEW_TEMPLATE.md", docs / "UX_REVIEW_TEMPLATE.md")
            shutil.copy(assets / "UX_REVIEW_SKILL_TEMPLATE.md", skill / "SKILL.md")
            result = validator.validate(docs, skill)
            self.assertTrue(result["pass"], result)
            self.assertEqual(result["warnings"], [])

    def test_lens_warning_never_enters_errors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_bundle(root, CORE.replace("UX-CORE-001", ""), REVIEW_TEMPLATE_MIN, CHILD_MIN)
            result = validator.validate(root)
            self.assertFalse(result["pass"])
            self.assertFalse(any(e.startswith("LENTES_") for e in result["errors"]), result)
            self.assertTrue(any(w.startswith("LENTES_COGNITIVAS_AUSENTES") for w in result["warnings"]))

    def test_cli_exits_zero_with_warnings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            write_bundle(root, CORE, REVIEW_TEMPLATE_MIN, CHILD_MIN)
            proc = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)],
                                  capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(json.loads(proc.stdout)["warnings"])


if __name__ == "__main__":
    unittest.main()
