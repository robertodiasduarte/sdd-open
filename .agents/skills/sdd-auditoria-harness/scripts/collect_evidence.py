#!/usr/bin/env python3
"""
Coleta evidências read-only do harness SDD e imprime JSON em stdout.

Não cria, edita, remove, renomeia ou move arquivos.
Não usa rede.
Não executa shell=True.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Iterable

TEXT_SUFFIXES = {
    ".md", ".json", ".jsonc", ".yaml", ".yml", ".txt", ".toml",
    ".py", ".sh", ".js", ".ts", ".tsx", ".jsx"
}
MAX_TEXT_BYTES = 2_000_000

PROCESS_DIR_NAMES = {
    "sdd", "spec", "specs", "playbook", "playbooks", "notes",
    "memory", "memories", "reports", "report", "logs", "log"
}

PATH_PATTERNS = [
    re.compile(r"\(([^)\n]+)\)"),              # markdown link target
    re.compile(r"`([^`\n]+)`"),                # inline code
    re.compile(r'["\']([^"\']+/[^"\']+)["\']') # quoted path-like string
]

URL_RE = re.compile(r"^[a-z]+://", re.I)
PLACEHOLDER_RE = re.compile(r"[<$>{}*?]")

def within(child: Path, root: Path) -> bool:
    try:
        child.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False

def safe_files(base: Path) -> Iterable[Path]:
    if not base.exists():
        return
    if base.is_file():
        if within(base, base.parent) and not base.is_symlink():
            yield base
        return
    for p in base.rglob("*"):
        if p.is_file() and not p.is_symlink() and within(p, base):
            yield p

def read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_TEXT_BYTES:
            return None
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != "SKILL.md":
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()

def classify(path: Path, root: Path) -> str:
    r = rel(path, root)
    if r.endswith("CLAUDE.md"):
        return "fonte-de-verdade"
    if r.startswith(".claude/commands/"):
        return "comando"
    if r.startswith(".claude/agents/"):
        return "agente"
    if r.startswith(".claude/skills/") and r.endswith("/SKILL.md"):
        return "skill"
    if r in {".claude/settings.json", ".claude/settings.local.json"}:
        return "settings"
    if r.startswith(".claude/scripts/") or r.startswith("scripts/"):
        return "script"
    return "doc-processo"

def declared_purpose(text: str | None) -> str:
    if not text:
        return "não extraído"
    lines = [x.strip() for x in text.splitlines()]
    for line in lines:
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip().strip("\"'")[:240]
    for line in lines:
        if line and not line.startswith(("#", "---", "<")):
            return line[:240]
    for line in lines:
        if line.startswith("#"):
            return line.lstrip("#").strip()[:240]
    return "não extraído"

def language_origin(text: str | None, rpath: str) -> dict:
    if not text:
        return {"idioma": "indeterminado", "origem_aparente": "indeterminada"}
    low = text.lower()
    pt_hits = sum(low.count(w) for w in [" para ", " quando ", " arquivo", " relatório", "fase ", "não "])
    en_hits = sum(low.count(w) for w in [" the ", " when ", " file", " report", " phase ", " do not "])
    idioma = "pt-BR" if pt_hits > en_hits else ("en" if en_hits > pt_hits else "misto/indeterminado")
    origin = "indeterminada"
    cues = ("template", "boilerplate", "example", "exemplo", "sample", "starter")
    if any(cue in low for cue in cues) or any(cue in rpath.lower() for cue in cues):
        origin = "possível template/exemplo; requer confirmação humana"
    return {"idioma": idioma, "origem_aparente": origin}

def git_last_change(root: Path, path: Path) -> str | None:
    try:
        cp = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", rel(path, root)],
            cwd=root, capture_output=True, text=True, timeout=15, check=False
        )
        value = cp.stdout.strip()
        return value or None
    except Exception:
        return None

def candidate_roots(root: Path) -> list[Path]:
    out = []
    for p in [
        root / ".claude" / "sdd",
        root / "sdd",
        root / "specs",
        root / ".specs",
        root / "playbook",
        root / "playbooks",
        root / "notes",
        root / "memory",
        root / ".memory",
        root / "reports",
        root / "logs",
    ]:
        if p.exists():
            out.append(p)
    return out

def collect_inventory(root: Path) -> list[Path]:
    items: set[Path] = set()

    for p in root.rglob("CLAUDE.md"):
        if p.is_file() and not p.is_symlink() and within(p, root):
            items.add(p)

    patterns = [
        ".claude/commands/**/*.md",
        ".claude/agents/**/*.md",
        ".claude/skills/*/SKILL.md",
        ".claude/scripts/**/*",
    ]
    for pattern in patterns:
        for p in root.glob(pattern):
            if p.is_file() and not p.is_symlink() and within(p, root):
                items.add(p)

    for name in [".claude/settings.json", ".claude/settings.local.json"]:
        p = root / name
        if p.is_file() and not p.is_symlink():
            items.add(p)

    for base in candidate_roots(root):
        for p in safe_files(base):
            if read_text(p) is not None:
                items.add(p)

    # Descobre scripts referenciados textualmente pelo harness já encontrado.
    script_ref_re = re.compile(r"(?<![\w.-])((?:\.claude/scripts|scripts)/[A-Za-z0-9_./-]+)")
    for p in list(items):
        text = read_text(p)
        if not text:
            continue
        for m in script_ref_re.finditer(text):
            candidate = (root / m.group(1)).resolve()
            if within(candidate, root) and candidate.is_file() and not candidate.is_symlink():
                items.add(candidate)

    return sorted(items, key=lambda p: rel(p, root))

def reference_needles(path: Path, root: Path, text: str | None) -> set[str]:
    rpath = rel(path, root)
    needles = {rpath, path.name}
    stem = path.stem
    if "/commands/" in f"/{rpath}":
        needles.add("/" + stem)
    if text:
        m = re.search(r"(?m)^name:\s*['\"]?([^'\"\n]+)", text)
        if m:
            needles.add(m.group(1).strip())
    return {n for n in needles if len(n) >= 3}

def find_inbound_refs(target: Path, root: Path, corpus: dict[Path, str | None]) -> list[str]:
    needles = reference_needles(target, root, corpus.get(target))
    refs = []
    for p, text in corpus.items():
        if p == target or not text:
            continue
        if any(n in text for n in needles):
            refs.append(rel(p, root))
    return sorted(set(refs))

def looks_like_local_path(value: str) -> bool:
    value = value.strip().strip("'\"")
    if not value or URL_RE.match(value):
        return False
    if "\n" in value or len(value) > 240:
        return False
    if PLACEHOLDER_RE.search(value):
        return False
    if value.startswith(("/", "~")):
        return False
    if "/" not in value and not re.search(r"\.[A-Za-z0-9]{1,8}$", value):
        return False
    if " " in value and "/" not in value:
        return False
    return True

def missing_path_mentions(path: Path, root: Path, text: str | None) -> list[dict]:
    if not text:
        return []
    out = []
    seen = set()
    for regex in PATH_PATTERNS:
        for m in regex.finditer(text):
            value = m.group(1).strip()
            # markdown URLs may have title after a space; keep first token only
            if value.startswith("<") and value.endswith(">"):
                value = value[1:-1]
            if not looks_like_local_path(value):
                continue
            clean = value.split("#", 1)[0]
            candidate = (root / clean).resolve()
            if not within(candidate, root):
                continue
            if candidate.exists():
                continue
            line = text.count("\n", 0, m.start()) + 1
            key = (clean, line)
            if key in seen:
                continue
            seen.add(key)
            out.append({"path": clean, "line": line})
    return out[:100]

def execution_evidence(target: Path, root: Path, corpus: dict[Path, str | None]) -> list[str]:
    rpath = rel(target, root)
    needles = reference_needles(target, root, corpus.get(target))
    hits = []
    for p, text in corpus.items():
        if p == target or not text:
            continue
        parts = {x.lower() for x in p.parts}
        if not parts.intersection({"reports", "report", "logs", "log"}):
            continue
        if any(n in text for n in needles):
            hits.append(rel(p, root))
    return sorted(set(hits))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo_root", help="Raiz do repositório a auditar")
    args = ap.parse_args()

    root = Path(args.repo_root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit("ERRO: repo_root não é um diretório.")
    if root.is_symlink():
        raise SystemExit("ERRO: repo_root não pode ser symlink.")

    items = collect_inventory(root)
    corpus = {p: read_text(p) for p in items}

    evidence = []
    for p in items:
        text = corpus[p]
        lo = language_origin(text, rel(p, root))
        inbound = find_inbound_refs(p, root, corpus)
        evidence.append({
            "path": rel(p, root),
            "type": classify(p, root),
            "declared_purpose": declared_purpose(text),
            "language": lo["idioma"],
            "origin_apparent": lo["origem_aparente"],
            "inbound_reference_count": len(inbound),
            "inbound_reference_files": inbound,
            "last_git_change": git_last_change(root, p),
            "execution_evidence_files": execution_evidence(p, root, corpus),
            "missing_path_candidates": missing_path_mentions(p, root, text),
            "note": "missing_path_candidates são candidatos; valide contexto antes de acusar deriva."
        })

    result = {
        "repo_root": str(root),
        "read_only": True,
        "inventory_count": len(evidence),
        "items": evidence,
        "cautions": [
            "Zero referências não prova desuso por si só.",
            "Paths com contexto dinâmico podem gerar falso positivo; validar antes do relatório.",
            "Origem aparente de template é heurística, não conclusão.",
            "O script não cria nem altera arquivos; saída somente em stdout."
        ]
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
