#!/usr/bin/env python3
"""Normative-profile helpers for sdd-kb: rule frontmatter, source catalog, RULE_MAP, SHA-256.

Usage:
  python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map <kb-domain-dir>          # (re)write RULE_MAP.md
  python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map [--check] <kb-domain-dir> # exit 2 if it drifted
                                  (--check also accepted after the directory)
  python3 .agents/skills/sdd-kb/scripts/kb_normativo.py sha <file>                        # SHA-256 + today's date

validate_kb.py imports this module, so the RULE_MAP it checks is the one this script writes.
Standard library only (Python 3.9+): the frontmatter is a closed subset of YAML, parsed here.

Exit codes: 0 ok, 2 fail, 64 usage error.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import re
import sys
from pathlib import Path

# Normative ladder, strongest first. A rule may be `confirmado` only when its source sits
# above `doutrina`: a news article or a course cannot confirm what the law says.
DEGRAUS = [
    "constituicao",
    "lei-complementar",
    "lei-ordinaria",
    "decreto",
    "ato-normativo",
    "ato-tecnico",
    "solucao-de-consulta",
    "doutrina",
    "pratica-propria",
]
NAO_CONFIRMAM = {"doutrina", "pratica-propria"}
STATUS = {"confirmado", "premissa", "nao-confirmado"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA = re.compile(r"^[0-9a-f]{64}$")
CATALOGO_COLS = ["id", "documento", "degrau", "versão", "origem", "capturado em", "arquivo", "sha-256"]
RULE_MAP_HEADER = "# RULE_MAP — gerado por `kb_normativo.py rule-map`. Não edite à mão."


def valid_date(v) -> bool:
    """AAAA-MM-DD that exists on the calendar: 2026-13-01 and 2026-02-30 are refused."""
    if not isinstance(v, str) or not DATE.match(v):
        return False
    try:
        _dt.date.fromisoformat(v)
        return True
    except ValueError:
        return False


class KBError(Exception):
    """A structural problem, already phrased as `<file>: <field> <problem> — <what to do>`."""


# ── frontmatter ────────────────────────────────────────────────────────────────

def _scalar(raw: str):
    v = raw.strip()
    if v in ("null", "~", ""):
        return None
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in inner.split(",")]
    return v


def parse_frontmatter(path: Path) -> dict:
    """Parse the leading `---` block. Grammar: `key: scalar`, one nesting level by two spaces,
    inline lists `[a, b]`, null/~, optional quotes, `#` comments on their own line."""
    # utf-8-sig: o Bloco de Notas do Windows grava "UTF-8 com BOM"; o BOM não é conteúdo (review r3).
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != "---":
        raise KBError(f"{path.name}: frontmatter missing — the file must start with a `---` block")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        raise KBError(f"{path.name}: frontmatter not closed — add the closing `---` line")
    data: dict = {}
    parent = None
    for num in range(1, end):
        line = lines[num]
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^( {0,2})([A-Za-z_][A-Za-z0-9_]*):(.*)$", line)
        if not m:
            raise KBError(
                f"{path.name}:{num + 1}: frontmatter line not understood {line.strip()!r} — "
                "use `key: value`, or two-space indented `key: value` under a parent key"
            )
        indent, key, rest = m.groups()
        alvo = data[parent] if indent and parent is not None else data
        if key in alvo:
            # Repetida, a última venceria em silêncio e o RULE_MAP mostraria o que o autor não vê no topo.
            raise KBError(f"{path.name}:{num + 1}: key {key!r} repeated — keep one, remove the other")
        if indent:
            if parent is None:
                raise KBError(f"{path.name}:{num + 1}: indented key {key!r} without a parent key")
            data[parent][key] = _scalar(rest)
        elif rest.strip() == "":
            parent = key
            data[key] = {}
        else:
            parent = None
            data[key] = _scalar(rest)
    # `key:` with nothing indented below is an empty value, not an empty block: null, never {}.
    for k, v in list(data.items()):
        if v == {}:
            data[k] = None
    return data


# ── catalog ────────────────────────────────────────────────────────────────────

def _row(line: str) -> list:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def read_catalogo(root: Path) -> dict:
    """fontes/CATALOGO.md → {id: {documento, degrau, versao, origem, capturado em, arquivo, sha-256}}."""
    path = root / "fontes" / "CATALOGO.md"
    if not path.is_file():
        raise KBError("fontes/CATALOGO.md: missing — a normative KB lists every source it cites there")
    rows = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip().startswith("|")]
    if len(rows) < 2:
        raise KBError("fontes/CATALOGO.md: no table found — use the CATALOGO_FONTES_TEMPLATE.md columns")
    header = [h.lower() for h in _row(rows[0])]
    if header != CATALOGO_COLS:
        raise KBError(
            f"fontes/CATALOGO.md: columns {header} — expected exactly {CATALOGO_COLS}"
        )
    out: dict = {}
    for line in rows[2:]:
        cells = _row(line)
        if len(cells) != len(CATALOGO_COLS):
            raise KBError(f"fontes/CATALOGO.md: row {line.strip()!r} has {len(cells)} cells, expected {len(CATALOGO_COLS)}")
        rec = dict(zip(CATALOGO_COLS, cells))
        sid = rec["id"].strip("`")
        if sid in out:
            raise KBError(f"fontes/CATALOGO.md: id {sid!r} repeated — each source has one id")
        out[sid] = rec
    if not out:
        raise KBError("fontes/CATALOGO.md: table has no sources")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ── rules ──────────────────────────────────────────────────────────────────────

def read_rules(root: Path) -> list:
    """rules/*.md → list of (path, frontmatter), sorted by rule id."""
    d = root / "rules"
    paths = sorted(d.glob("*.md")) if d.is_dir() else []
    out = [(p, parse_frontmatter(p)) for p in paths]
    return sorted(out, key=lambda pr: str(pr[1].get("regra") or pr[0].stem))


def _cell(v) -> str:
    if v is None or v == []:
        return "—"
    if isinstance(v, list):
        return ", ".join(str(x) for x in v).replace("|", "\\|")
    return str(v).replace("|", "\\|")


def render_rule_map(root: Path) -> str:
    catalogo = read_catalogo(root)
    lines = [
        RULE_MAP_HEADER,
        "",
        "| Regra | Vigência | Fonte (documento · localizador · degrau) | Status | Conflito com | Implementação | Teste | Sev. | Código |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for _path, fm in read_rules(root):
        vig = fm.get("vigencia") if isinstance(fm.get("vigencia"), dict) else {}
        fonte = fm.get("fonte") if isinstance(fm.get("fonte"), dict) else {}
        fid = fonte.get("id") if isinstance(fonte.get("id"), str) else None
        src = catalogo.get(fid, {}) if fid else {}
        fonte_txt = " · ".join(
            _cell(x) for x in (src.get("documento"), fonte.get("localizador"), src.get("degrau")) if x
        ) or "—"
        lines.append("| " + " | ".join([
            _cell(fm.get("regra")),
            f"{_cell(vig.get('de'))} → {_cell(vig.get('ate')) if vig.get('ate') else 'em vigor'}",
            fonte_txt,  # cada parte já passou por _cell (escapar de novo vira "\\\\|" e quebra a tabela)
            _cell(fm.get("status")),
            _cell(fm.get("conflito_com")),
            _cell(fm.get("implementacao")),
            _cell(fm.get("teste")),
            _cell(fm.get("severidade")),
            _cell(fm.get("codigo")),
        ]) + " |")
    return "\n".join(lines) + "\n"


# ── cli ────────────────────────────────────────────────────────────────────────

def main(argv: list) -> int:
    if len(argv) >= 2 and argv[0] == "sha" and len(argv) == 2:
        p = Path(argv[1])
        if not p.is_file():
            print(f"FAIL: not a file: {p}")
            return 64
        print(f"{sha256(p)}  capturado em {_dt.date.today().isoformat()}  {p.name}")
        return 0
    # `--check` may come before or after the directory (avaliador ciclo 1: validate_kb.py
    # already takes `--strict <dir>`, so `rule-map --check <dir>` must not be a usage error).
    rest = argv[1:]
    check = rest.count("--check") == 1
    dirs = [a for a in rest if a != "--check"]
    if (argv[:1] == ["rule-map"] and rest.count("--check") <= 1 and len(dirs) == 1
            and not dirs[0].startswith("-")):
        root = Path(dirs[0])
        try:
            text = render_rule_map(root)
        except KBError as e:
            print(f"FAIL: {e}")
            return 2
        target = root / "RULE_MAP.md"
        if check:
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                print("FAIL: RULE_MAP.md differs from rules/ — run `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map <domain>`")
                return 2
            print("PASS: RULE_MAP.md matches rules/")
            return 0
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}")
        return 0
    print(__doc__.split("\n\n")[1])
    return 64


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
