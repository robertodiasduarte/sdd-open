#!/usr/bin/env python3
"""check-versions.py — every skill carries its own version, and a changed skill must bump it.

A skill is copied into other projects by `init` and `sync` (and, later, packaged on its own): the
version in its frontmatter is how someone tells that their copy is old. This gate keeps that
number from lying.

Checks, for each .agents/skills/<name>/SKILL.md under --root:
  1. metadata.version exists and is X.Y.Z;
  2. manifest.json and evals/cases.json, when present and carrying a "version", match it;
  3. with --base REF: a skill whose folder changed since REF has a version greater than the one
     it had in REF (a new skill, or one without a version in REF, passes).

Usage:
  python3 scripts/check-versions.py                                # structural checks only
  python3 scripts/check-versions.py --base v2.2.0                  # plus the bump check
  python3 scripts/check-versions.py --base v2.2.0 --base-obrigatoria
      # release: a base that does not resolve is a FAIL, never "structural checks only"

Exit: 0 = PASS · 1 = FAIL · 64 = usage. Standard library only; Python >= 3.9.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
VERSION = re.compile(r"^  version:\s*\"?([^\"\n]*)\"?\s*$", re.M)
SKILLS = ".agents/skills"


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print("check-versions: " + message, file=sys.stderr)
        sys.exit(64)


def version_of(text: str) -> str | None:
    fm = FRONTMATTER.match(text)
    if not fm:
        return None
    m = VERSION.search(fm.group(1))
    return m.group(1).strip() if m else None


def semver(v: str) -> tuple[int, int, int]:
    a, b, c = SEMVER.match(v).groups()  # type: ignore[union-attr]
    return int(a), int(b), int(c)


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True)


def check_skill(root: Path, d: Path, base: str | None) -> list[str]:
    name = d.name
    v = version_of((d / "SKILL.md").read_text(encoding="utf-8"))
    if not v or not SEMVER.match(v):
        return [name + ": metadata.version ausente ou fora de X.Y.Z (" + repr(v) + ")"]
    erros: list[str] = []
    for extra in ("manifest.json", "evals/cases.json"):
        p = d / extra
        if not p.is_file():
            continue
        try:
            got = json.loads(p.read_text(encoding="utf-8")).get("version")
        except (ValueError, AttributeError) as e:
            erros.append(name + ": " + extra + " não é um objeto JSON legível (" + str(e) + ")")
            continue
        if got is not None and got != v:
            erros.append(name + ": " + extra + " tem version " + repr(got) + ", SKILL.md tem " + repr(v))
    if base:
        pasta = SKILLS + "/" + name + "/"
        if git(root, "diff", "--name-only", base, "--", pasta).stdout.strip():
            old = git(root, "show", base + ":" + pasta + "SKILL.md")
            ov = version_of(old.stdout) if old.returncode == 0 else None
            if ov and SEMVER.match(ov) and semver(v) <= semver(ov):
                erros.append(name + ": a skill mudou desde " + base + " e a versão não subiu (" + ov + " -> " + v + ")")
    return erros


def main(argv: list[str]) -> int:
    ap = Parser(prog="check-versions.py")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                    help="raiz do repositório a inspecionar (default: este pacote)")
    ap.add_argument("--base", help="ref git para comparar (ex.: a última tag v*)")
    ap.add_argument("--base-obrigatoria", action="store_true",
                    help="base ausente ou que não resolve a um commit reprova")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    base = a.base
    if a.base_obrigatoria and not base:
        print("FAIL: --base-obrigatoria sem --base")
        print("RESULTADO: VERMELHO\n→ passe --base com a última tag publicada.")
        return 1
    if base and git(root, "rev-parse", "--verify", "--quiet", base + "^{commit}").returncode != 0:
        if a.base_obrigatoria:
            # Sem base, o gate de bump não roda: a release sairia com uma versão velha e conteúdo novo.
            print("FAIL: base " + repr(base) + " indisponível — sem ela não dá para saber o que mudou desde a última release.")
            print("RESULTADO: VERMELHO\n→ faça checkout com o histórico e as tags (fetch-depth: 0) e rode de novo.")
            return 1
        print("check-versions: base " + repr(base) + " indisponível; só as checagens estruturais.")
        base = None
    dirs = sorted(p.parent for p in (root / SKILLS).glob("*/SKILL.md"))
    if not dirs:
        print("FAIL: nenhuma skill em " + str(root / SKILLS))
        print("RESULTADO: VERMELHO\n→ rode na raiz do sdd-open ou passe --root.")
        return 1
    erros: list[str] = []
    for d in dirs:
        erros += check_skill(root, d, base)
    if erros:
        for e in erros:
            print("FAIL: " + e)
        print("RESULTADO: VERMELHO")
        print("→ skill alterada sobe metadata.version; manifest.json e evals/cases.json acompanham.")
        return 1
    comparadas = ", comparadas a " + base if base else ""
    print("PASS: check-versions — " + str(len(dirs)) + " skills com versão coerente" + comparadas + ".")
    print("RESULTADO: VERDE\n→ siga para o próximo passo.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
