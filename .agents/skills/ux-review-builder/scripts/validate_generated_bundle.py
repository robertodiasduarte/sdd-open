#!/usr/bin/env python3
"""Validate the three artifacts produced by ux-review-builder.

Structural validation only. It does not judge visual quality, accessibility compliance,
or correctness of project-specific UX decisions.

Output: {"pass", "errors", "warnings", "scope"}. Only errors fail; warnings never change pass or the
exit code. LENTES_COGNITIVAS_AUSENTES warns that a template or child skill predates 1.3.0 (no cognitive
lenses section) — older bundles keep passing.

--root  folder with UX_STANDARD.md and UX_REVIEW_TEMPLATE.md (the SDD folder, or the download folder)
--skill folder of the generated ux-review skill (default: the first ux-review folder found in
        the root or in the project root — the parent of sdd/, or of .claude/ for .claude/sdd/ —
        because the agent delivery puts the documents in the SDD folder and ux-review in the project root)
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

CORE_IDS = [f"UX-CORE-{i:03d}" for i in range(1, 11)]
RULE_ID_RE = re.compile(r"\bUX-[A-Z]+-[0-9]{3}\b")
# A rule is DEFINED where its ID opens a table row; the exceptions and history sections (and prose)
# only CITE it, so rows under those headings are not definitions.
RULE_DEF_RE = re.compile(r"^\|\s*(UX-[A-Z0-9]+-[0-9]{3})\s*\|")
CITATION_SECTIONS = ("excec", "historico")
# The method keeps every SDD document side by side in one folder: a child skill that points
# to a subfolder would never find the DEFINE nor be found by the Design phase.
SUBFOLDER_RE = re.compile(r"\b(features|architecture|templates|reviews)/|\bsdd/[^\s/`'\"]+/")
HARDCODED_PATH_RE = re.compile(r"\bsdd/")
LENS_MARKER = "lentes cognitivas"


def plain(text: str) -> str:
    """Lowercase without diacritics, so accented and plain-ASCII phrasing both match."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def defined_rule_ids(standard: str) -> list[str]:
    ids: list[str] = []
    citing = False
    for line in standard.splitlines():
        if line.startswith("#"):
            heading = plain(line.lstrip("#").strip())
            citing = heading.startswith(CITATION_SECTIONS)
            continue
        match = RULE_DEF_RE.match(line)
        if match and not citing:
            ids.append(match.group(1))
    return ids


def read(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"missing:{path.name}")
    return path.read_text(encoding="utf-8")


def validate(root: Path, skill_dir: Path | None = None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    standard_path = root / "UX_STANDARD.md"
    review_template_path = root / "UX_REVIEW_TEMPLATE.md"
    if skill_dir is None:
        # The project root is the parent of sdd/, or two levels up only for .claude/sdd/ — never beyond it.
        bases = [root, root.parent]
        if root.parent.name == ".claude":
            bases.append(root.parent.parent)
        skill_candidates = [d / "ux-review" / "SKILL.md" for d in bases]
    else:
        skill_candidates = [skill_dir / "SKILL.md"]
    skill_candidates.append(root / "SKILL_ux-review.md")
    skill_path = next((p for p in skill_candidates if p.is_file()), None)

    # None = missing; "" = present but empty — an empty file is checked (and fails), never skipped.
    try:
        standard = read(standard_path)
    except Exception:
        standard = None
        errors.append("UX_STANDARD_AUSENTE")
    try:
        review_template = read(review_template_path)
    except Exception:
        review_template = None
        errors.append("UX_REVIEW_TEMPLATE_AUSENTE")
    if skill_path is None:
        child_skill = None
        errors.append("UX_REVIEW_SKILL_AUSENTE")
    else:
        try:
            child_skill = read(skill_path)
        except Exception:
            child_skill = None
            errors.append("UX_REVIEW_SKILL_ILEGIVEL")

    if standard is not None:
        for core_id in CORE_IDS:
            if core_id not in standard:
                errors.append(f"PRINCIPIO_UNIVERSAL_AUSENTE:{core_id}")
        ids = defined_rule_ids(standard)
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        if duplicates:
            errors.append("REVISAR_IDS_REPETIDOS:" + ",".join(duplicates[:10]))
        if HARDCODED_PATH_RE.search(standard):
            errors.append("CAMINHO_HARDCODED_NO_STANDARD")

    if review_template is not None:
        required = [
            "Canonical Conformance", "UX/CX Findings", "Universal Principles Check",
            "Required States", "Accessibility and Responsiveness", "Design Handoff",
            "Gate Outcome", "Canonical Evolution Proposals"
        ]
        for item in required:
            if item not in review_template:
                errors.append("SECAO_TEMPLATE_AUSENTE:" + item)
        if "regra canonica" not in plain(review_template):
            errors.append("RASTREABILIDADE_CANONICA_AUSENTE")
        if "NAO AVALIAVEL" not in review_template:
            errors.append("STATUS_NAO_AVALIAVEL_AUSENTE")
        if "BLOCKED FOR DESIGN" not in review_template:
            errors.append("GATE_BLOQUEANTE_AUSENTE")
        if LENS_MARKER not in plain(review_template):
            warnings.append("LENTES_COGNITIVAS_AUSENTES:UX_REVIEW_TEMPLATE.md")

    if child_skill is not None:
        required_child = ["UX_STANDARD.md", "UX_REVIEW_TEMPLATE.md", "MUST", "NAO AVALIAVEL"]
        for item in required_child:
            if item not in child_skill:
                errors.append("CONTRATO_CHILD_AUSENTE:" + item)
        child_plain = plain(child_skill)
        if "`sdd/`" not in child_skill or "`.claude/sdd/`" not in child_skill or "sem subpastas" not in child_plain:
            errors.append("REGRA_DE_PASTA_AUSENTE")
        if SUBFOLDER_RE.search(child_skill):
            errors.append("SUBPASTA_SDD_NA_FILHA")
        if "nao altera" not in child_plain and "nao editar" not in child_plain:
            errors.append("PROTECAO_FONTE_CANONICA_AUSENTE")
        if LENS_MARKER not in child_plain:
            warnings.append("LENTES_COGNITIVAS_AUSENTES:ux-review")

    return {
        "pass": not errors,
        "errors": errors,
        "warnings": warnings,
        "scope": "estrutura dos tres artefatos; nao prova qualidade subjetiva ou conformidade externa",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--skill", type=Path, default=None)
    args = parser.parse_args()
    result = validate(args.root, args.skill)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["pass"] else 2


if __name__ == "__main__":
    sys.exit(main())
