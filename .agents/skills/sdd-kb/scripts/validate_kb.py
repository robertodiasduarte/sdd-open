#!/usr/bin/env python3
"""Structural and size lint for a knowledge-base domain folder.

Usage: python3 .agents/skills/sdd-kb/scripts/validate_kb.py <kb-domain-dir> [index-file] [--strict]

Checks the minimum viable KB (index + quick-reference + >=1 concept + >=1 pattern),
the per-type line limits, leftover template placeholders, and registration in the index.
Braces inside code (fenced blocks or `inline`) are examples — JSON, sets, template
expressions — and only an unmistakable {{UPPER_CASE}} token counts there.

Profile: `perfil: normativo | geral` in the domain's block of the index (absent = geral).
A `normativo` domain also needs a data-base, a "Conflitos entre fontes" section, the
"não é aconselhamento" notice, fontes/CATALOGO.md, at least one rules/*.md with vigência and
a catalogued source, a RULE_MAP.md generated from rules/, and — when present — tables by
vigência and test cases inside a rule's vigência. --strict also fails a normative KB still
marked PENDENTE DE REVISÃO and a rule whose `implementacao` has no `teste`, or whose `teste` file (the part
before the first ":") is missing from the project root — the folder above sdd/kb/ (run it before software
consumes the KB).

Exit codes: 0 pass, 2 fail, 64 usage error. WARN lines never change the exit code.
"""
import datetime as _dt
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # no __pycache__ inside the skill: init and sync copy the whole folder
sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_normativo as kn  # noqa: E402  (same folder; stdlib only)

LIMITS = {"quick_reference": 100, "concept": 150, "pattern": 200}

PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}|\{[A-Z][A-Z0-9_]{2,}\}|\{[^{}\n]*\s[^{}\n]*\}")
# Inside code (fenced block or `inline`), braces are examples: JSON, sets, template expressions.
# There only an unmistakable template token counts — {{UPPER_CASE}}.
CODE_PLACEHOLDER = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")


def fail(msg):
    print(f"FAIL: {msg}")
    return False


def warn(msg):
    print(f"WARN: {msg}")


def count_lines(path):
    return len(path.read_text(encoding="utf-8").splitlines())


def check_placeholders(path, ok):
    fence = None
    for num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = FENCE.match(line)
        if fence is None and m:
            fence = m.group(1)[0] * 3
            continue
        if fence is not None:
            if line.strip().startswith(fence):
                fence = None
                continue
            found = [x.group(0) for x in CODE_PLACEHOLDER.finditer(line)]
        else:
            codes = [x.group(0) for x in INLINE_CODE.finditer(line)]
            prose = INLINE_CODE.sub(" ", line)
            found = [x.group(0) for x in PLACEHOLDER.finditer(prose)]
            found += [x.group(0) for c in codes for x in CODE_PLACEHOLDER.finditer(c)]
        # The templates carry intentional guidance after a horizontal rule; still, a
        # published KB must not ship any placeholder at all.
        for token in found:
            ok = fail(
                f"{path.name}:{num}: unsubstituted placeholder {token!r} "
                "(if it is an example, not a gap, put it in `code`)"
            ) and ok
    return ok


def read_perfil(registry, name):
    """Value of `perfil:` inside the domain's block of the index, or None."""
    lines = registry.splitlines()
    for i, line in enumerate(lines):
        m = re.match(rf"^(\s+){re.escape(name)}\s*:\s*$", line)
        if not m:
            continue
        base = len(m.group(1))
        for nxt in lines[i + 1:]:
            if not nxt.strip() or nxt.lstrip().startswith("#"):
                continue
            if len(nxt) - len(nxt.lstrip()) <= base:
                break
            # `perfil: normativo  # comentário` is still normativo — a trailing comment must never
            # silently downgrade the domain to geral and skip every normative check (review A1).
            pm = re.match(r"^\s+perfil\s*:(.*)$", nxt)
            if pm:
                return re.sub(r"\s+#.*$", "", pm.group(1)).strip().strip("\"'")
        return None
    return None


# Markers are TOKENS, not "token + digit": "LC nº 123", "EC nº 132" and "a NT da SEFAZ" count
# (avaliador ciclo 1). LC/EC/NT are whole words — (?<!\w)/(?!\w) instead of \b, so a code or
# word that merely contains them ("EC2", "ECONOMIA", "NTFS") never counts.
NORMATIVE_MARKERS = {
    "LC": re.compile(r"(?<!\w)LC(?!\w)"),
    "art.": re.compile(r"(?<!\w)art\.", re.I),
    "NT": re.compile(r"(?<!\w)NT(?!\w)"),
    "vigência": re.compile(r"vig[êe]ncia", re.I),
    "alíquota": re.compile(r"al[íi]quota", re.I),
    "EC": re.compile(r"(?<!\w)EC(?!\w)"),
}


def warn_looks_normative(root):
    # errors="replace": this scan opens files the 1.0.1 never read (reference/, specs/…); a
    # Latin-1 file there must not turn a passing geral domain into a traceback (AT-003).
    text = "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in sorted(root.rglob("*.md")))
    found = sorted(k for k, rx in NORMATIVE_MARKERS.items() if rx.search(text))
    if len(found) >= 3:
        warn(
            f"parece normativo ({', '.join(found)}) — if its rules hold only for a period, "
            "register the domain with `perfil: normativo` in the index"
        )


def _date(v):
    return kn.valid_date(v)


def _load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (ValueError, OSError) as e:
        return None, f"{path.name}: invalid JSON ({e}) — fix the file"


def _s(v):
    """The value if it is a non-empty string, else None — membership tests never see a list."""
    return v if isinstance(v, str) and v else None


# Field → expected type. The frontmatter grammar admits lists and blocks anywhere, so a value of
# the wrong TYPE is reported here, by name, and replaced before anything compares it (review r1/r2:
# a list or a scalar in the wrong place used to end in a traceback instead of FAIL + exit 2).
RULE_SCALARS = ("regra", "titulo", "status", "implementacao", "teste", "severidade", "codigo")


def sanitize_rule(name, fm):
    ok = True
    for k in RULE_SCALARS:
        if fm.get(k) is not None and not isinstance(fm.get(k), str):
            ok = fail(f"{name}: {k} must be a single value, got {fm[k]!r}") and ok
            fm[k] = None
    for k, subs in (("vigencia", ("de", "ate")), ("fonte", ("id", "localizador"))):
        v = fm.get(k)
        if v is not None and not isinstance(v, dict):
            ok = fail(f"{name}: {k} must be a block with {' and '.join(subs)} (two-space indented lines), got {v!r}") and ok
            fm[k] = {}
        elif isinstance(v, dict):
            for sub in subs:
                if v.get(sub) is not None and not isinstance(v.get(sub), str):
                    ok = fail(f"{name}: {k}.{sub} must be a single value, got {v[sub]!r}") and ok
                    v[sub] = None
    cc = fm.get("conflito_com")
    if cc is not None and (not isinstance(cc, list) or not all(isinstance(x, str) for x in cc)):
        ok = fail(f"{name}: conflito_com must be a list of ids `[id, ...]`, got {cc!r}") and ok
        fm["conflito_com"] = []
    return ok


VAZIO = (None, "", "—", "-", "null")


def raiz_do_projeto(root):
    """<raiz>/sdd/kb/<slug> → <raiz>; anywhere else, the current directory (commands run from the root)."""
    r = root.resolve()
    if r.parent.name == "kb" and r.parent.parent.name == "sdd":
        return r.parents[2]
    return Path.cwd()


def check_normativo(root, concepts, patterns, strict):
    """Returns (ok, summary). Every FAIL names the file, the field and what to do."""
    ok = True
    projeto = raiz_do_projeto(root)
    index = root / "index.md"
    text = index.read_text(encoding="utf-8") if index.is_file() else ""

    m = re.search(r"\*\*Data-base:\*\*\s*(\d{4}-\d{2}-\d{2})", text)
    if m and not kn.valid_date(m.group(1)):
        ok = fail(f"index.md: Data-base {m.group(1)!r} is not a real calendar date") and ok
        m = None
    elif not m:
        ok = fail("index.md: Data-base missing — add `> **Data-base:** AAAA-MM-DD` (the date the content was checked against the sources)") and ok
    else:
        try:
            age = (_dt.date.today() - _dt.date.fromisoformat(m.group(1))).days
            if age > 365:
                warn(f"index.md: Data-base {m.group(1)} is {age} days old — recheck the sources and update it")
        except ValueError:
            ok = fail(f"index.md: Data-base {m.group(1)!r} is not a valid date") and ok
    if not re.search(r"^##\s+Conflitos entre fontes\s*$", text, re.M):
        ok = fail("index.md: section `## Conflitos entre fontes` missing — list each conflict, or state that none is registered up to the data-base") and ok
    if not re.search(r"não é aconselhamento", text, re.I):
        ok = fail("index.md: responsibility notice missing — the index must say the base \"não é aconselhamento tributário\" (see INDEX_NORMATIVO_TEMPLATE.md)") and ok
    # Quem revisou é obrigatório no normativo, e a pendência vale em QUALQUER linha do index fora de
    # código: "> **Situação:** PENDENTE DE REVISÃO" também é base não revisada (review r3, A1 HIGH).
    # Na linha do revisor, o valor que COMEÇA com "pendente" é pendência; "…itens pendentes" depois
    # de uma assinatura, ou "revisora independente", não (review r2 e r3).
    prosa = re.sub(r"^\s*(```|~~~).*?^\s*\1[^\n]*$", "", text, flags=re.M | re.S)  # blocos cercados
    prosa = re.sub(r"`[^`\n]*`", "", prosa)
    # [ \t]* e não \s*: o valor do revisor é o resto DESTA linha — um "Revisado por:" vazio não pode
    # pegar o título da linha seguinte como assinatura (review rodada 4, A1).
    revisor = re.search(r"Revisado por:\**[ \t]*(.*)$", prosa, re.M)
    if not revisor or not revisor.group(1).strip():
        ok = fail("index.md: `> **Revisado por:**` missing — name and registration of the reviewer, or PENDENTE DE REVISÃO") and ok
    pendente = (revisor and re.match(r"pendente", revisor.group(1).strip(), re.I)) or \
        re.search(r"pendente\s+de\s+revis[ãa]o", prosa, re.I)
    if pendente:
        if strict:
            ok = fail("index.md: base marked PENDENTE DE REVISÃO — --strict refuses an unreviewed normative KB; the professional reviews and signs first") and ok
        else:
            warn("index.md: PENDENTE DE REVISÃO — do not let software consume this KB before review (validate with --strict)")

    for path in concepts + patterns:
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:15])
        if not re.search(r"(\*\*)?Vale para:(\*\*)?", head):
            ok = fail(f"{path.parent.name}/{path.name}: `> **Vale para:**` missing in the header — state the period (or `atemporal`) this text holds for") and ok

    try:
        catalogo = kn.read_catalogo(root)
    except kn.KBError as e:
        return fail(str(e)) and False, "no catalog"
    for sid, rec in catalogo.items():
        if rec["degrau"] not in kn.DEGRAUS:
            ok = fail(f"fontes/CATALOGO.md: {sid}: degrau {rec['degrau']!r} unknown — use one of {', '.join(kn.DEGRAUS)}") and ok
        if not _date(rec["capturado em"]):
            ok = fail(f"fontes/CATALOGO.md: {sid}: capturado em {rec['capturado em']!r} — use AAAA-MM-DD (the date you got the file, not the file's own date)") and ok
        arq, sha = rec["arquivo"].strip("`"), rec["sha-256"].strip("`")
        if sha != "—" and not kn.SHA.match(sha):
            ok = fail(f"fontes/CATALOGO.md: {sid}: sha-256 {sha!r} is not 64 hex chars — run `kb_normativo.py sha <file>`") and ok
        if arq != "—":
            f = root / "fontes" / arq
            if not f.is_file():
                ok = fail(f"fontes/CATALOGO.md: {sid}: file listed in CATALOGO not found: fontes/{arq} — add it or write `—` in Arquivo") and ok
            elif not kn.SHA.match(sha):
                ok = fail(f"fontes/CATALOGO.md: {sid}: fontes/{arq} has no sha-256 — run `kb_normativo.py sha fontes/{arq}`") and ok
            elif kn.sha256(f) != sha:
                ok = fail(f"fontes/CATALOGO.md: {sid}: SHA-256 of fontes/{arq} differs from the catalog — the file changed; recatalog it as a new version") and ok

    try:
        rules = kn.read_rules(root)
    except kn.KBError as e:
        return fail(f"rules/{e}") and False, "rules unreadable"
    if not rules:
        ok = fail("rules/: no rule found — a normative KB needs at least one rules/*.md (RULE_TEMPLATE.md)") and ok
    for path, fm in rules:
        ok = sanitize_rule(f"rules/{path.name}", fm) and ok
    ids = {}
    for path, fm in rules:
        name = f"rules/{path.name}"
        rid = fm.get("regra")
        if not rid or not isinstance(rid, str):
            ok = fail(f"{name}: regra missing — give the rule a stable id (never reuse or renumber)") and ok
            continue
        if rid in ids:
            ok = fail(f"{name}: regra {rid!r} repeated (also in {ids[rid]})") and ok
        ids[rid] = name
        vig = fm.get("vigencia")
        if not isinstance(vig, dict) or not _date(vig.get("de")):
            ok = fail(f"{name}: vigencia.de missing or not AAAA-MM-DD — every rule says from when it holds") and ok
        elif vig.get("ate") is not None and (not _date(vig.get("ate")) or vig["ate"] < vig["de"]):
            ok = fail(f"{name}: vigencia.ate {vig.get('ate')!r} is not a date on/after vigencia.de {vig['de']} — use null while in force") and ok
            vig["ate"] = None  # already reported; never compared again (a list here would raise)
        fonte = fm.get("fonte")
        if not isinstance(fonte, dict) or _s(fonte.get("id")) not in catalogo:
            got = fonte.get("id") if isinstance(fonte, dict) else None
            ok = fail(f"{name}: fonte.id {got!r} not in fontes/CATALOGO.md — catalog the source first") and ok
        else:
            if not fonte.get("localizador"):
                ok = fail(f"{name}: fonte.localizador missing — page, article or section where the rule is written") and ok
            if fm.get("status") == "confirmado" and catalogo[fonte["id"]]["degrau"] in kn.NAO_CONFIRMAM:
                ok = fail(f"{name}: status confirmado rests on a {catalogo[fonte['id']]['degrau']} source ({fonte['id']}) — confirm it in a normative source or mark it nao-confirmado") and ok
        if fm.get("status") not in kn.STATUS:
            ok = fail(f"{name}: status {fm.get('status')!r} — use one of {', '.join(sorted(kn.STATUS))}") and ok
        if strict:
            # Software consumes the KB only through rules that point to a real test (RULE_MAP → Verify Gate).
            impl, teste = _s(fm.get("implementacao")), _s(fm.get("teste"))
            impl = None if impl in VAZIO else impl
            teste = None if teste in VAZIO else teste
            if impl and not teste:
                ok = fail(f"{name}: implementacao {impl!r} has no teste — --strict requires the test the Verify Gate runs (RULE_TEMPLATE.md)") and ok
            elif teste:
                arquivo = teste.split(":", 1)[0].strip()
                alvo = (projeto / arquivo).resolve()
                if Path(arquivo).is_absolute() or projeto.resolve() not in alvo.parents:
                    ok = fail(f"{name}: teste {teste!r}: {arquivo} is outside the project root {projeto} — use a path relative to it") and ok
                elif not alvo.is_file():
                    ok = fail(f"{name}: teste {teste!r}: {arquivo} not found from the project root {projeto}") and ok
    known = set(ids) | set(catalogo)
    com_conflito = []
    for path, fm in rules:
        cc = fm.get("conflito_com") or []
        for c in cc:
            if c not in known:
                ok = fail(f"rules/{path.name}: conflito_com {c!r} is neither a rule nor a catalogued source") and ok
        if cc and fm.get("regra"):
            com_conflito.append(fm["regra"])
    sec = re.search(r"^##\s+Conflitos entre fontes\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    for rid in com_conflito:
        if sec and not re.search(rf"(?<![\w-]){re.escape(rid)}(?![\w-])", sec.group(1)):
            ok = fail(f"index.md: rule {rid} has conflito_com but is not explained under `## Conflitos entre fontes`") and ok

    n_tab = 0
    series = {}
    tdir = root / "tabelas"
    for d in sorted(p for p in tdir.iterdir() if p.is_dir()) if tdir.is_dir() else []:
        if not kn.valid_date(d.name):
            ok = fail(f"tabelas/{d.name}/: folder name must be the start date AAAA-MM-DD (a real calendar date)") and ok
            continue
        for f in sorted(d.glob("*.json")):
            n_tab += 1
            data, err = _load_json(f)
            if err:
                ok = fail(f"tabelas/{d.name}/{err}") and ok
                continue
            vig = data.get("vigencia") if isinstance(data, dict) else None
            if isinstance(vig, dict) and vig.get("ate") is not None and not isinstance(vig.get("ate"), str):
                ok = fail(f"tabelas/{d.name}/{f.name}: vigencia.ate {vig.get('ate')!r} is not a date on/after {d.name}") and ok
                continue
            if not isinstance(vig, dict) or vig.get("de") != d.name:
                got = vig.get("de") if isinstance(vig, dict) else None
                ok = fail(f"tabelas/{d.name}/{f.name}: vigencia.de {got!r} differs from the folder {d.name} — the folder is the start date") and ok
                continue
            if vig.get("ate") is not None and (not _date(vig.get("ate")) or vig["ate"] < vig["de"]):
                ok = fail(f"tabelas/{d.name}/{f.name}: vigencia.ate {vig.get('ate')!r} is not a date on/after {vig['de']}") and ok
                continue
            fonte = data.get("fonte") if isinstance(data, dict) else None
            if not isinstance(fonte, dict) or _s(fonte.get("id")) not in catalogo:
                ok = fail(f"tabelas/{d.name}/{f.name}: fonte.id not in fontes/CATALOGO.md") and ok
            series.setdefault(f.name, []).append((vig["de"], vig.get("ate"), d.name))
    for fname, periods in series.items():
        periods.sort()
        for (de1, ate1, d1), (de2, _a2, d2) in zip(periods, periods[1:]):
            if ate1 is None or ate1 >= de2:
                ok = fail(f"tabelas/{d1}/{fname}: overlaps tabelas/{d2}/{fname} — close it with vigencia.ate before {de2}") and ok

    n_casos = 0
    cdir = root / "casos"
    rule_vig = {fm.get("regra"): (fm.get("vigencia") if isinstance(fm.get("vigencia"), dict) else {})
                for _p, fm in rules if _s(fm.get("regra"))}
    for f in sorted(cdir.glob("*.json")) if cdir.is_dir() else []:
        n_casos += 1
        data, err = _load_json(f)
        if err:
            ok = fail(f"casos/{err}") and ok
            continue
        if not isinstance(data, dict) or data.get("id") != f.stem:
            ok = fail(f"casos/{f.name}: id must equal the file name ({f.stem!r})") and ok
            continue
        rid = _s(data.get("regra"))
        if rid not in rule_vig:
            ok = fail(f"casos/{f.name}: regra {rid!r} does not exist in rules/") and ok
            continue
        if "esperado" not in data:
            ok = fail(f"casos/{f.name}: esperado missing — a case states the expected result") and ok
        cfonte = data.get("fonte")
        if cfonte is not None and (not isinstance(cfonte, dict) or _s(cfonte.get("id")) not in catalogo):
            got = cfonte.get("id") if isinstance(cfonte, dict) else cfonte
            ok = fail(f"casos/{f.name}: fonte.id {got!r} not in fontes/CATALOGO.md — catalog the source of the expected result") and ok
        fato, vig = data.get("data_fato"), rule_vig[rid] or {}
        if not _date(fato):
            ok = fail(f"casos/{f.name}: data_fato {fato!r} — use AAAA-MM-DD (the date of the taxable event / document)") and ok
        elif _date(vig.get("de")) and (fato < vig["de"] or (_date(vig.get("ate")) and fato > vig["ate"])):
            ok = fail(f"casos/{f.name}: data_fato {fato} is outside the vigência of {rid} ({vig['de']} → {vig.get('ate') or 'em vigor'})") and ok

    try:
        expected = kn.render_rule_map(root)
        rm = root / "RULE_MAP.md"
        if not rm.is_file() or rm.read_text(encoding="utf-8") != expected:
            ok = fail("RULE_MAP.md: missing or differs from rules/ — run `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map <domain>` (never edit it by hand)") and ok
    except kn.KBError as e:
        ok = fail(str(e)) and ok

    summary = f"normativo: {len(rules)} rule(s), {len(catalogo)} source(s), {n_tab} table(s), {n_casos} case(s)"
    return ok, summary


def main():
    argv = sys.argv[1:]
    strict = "--strict" in argv
    args = [a for a in argv if a != "--strict"]
    if len(args) not in (1, 2) or any(a.startswith("--") for a in args):
        print("Usage: python3 .agents/skills/sdd-kb/scripts/validate_kb.py <kb-domain-dir> [index-file] [--strict]")
        return 64

    root = Path(args[0])
    if not root.is_dir():
        print(f"FAIL: not a directory: {root}")
        return 64

    ok = True

    index = root / "index.md"
    quick = root / "quick-reference.md"

    if not index.is_file():
        ok = fail("missing index.md (the entry point)") and ok
    if not quick.is_file():
        ok = fail("missing quick-reference.md") and ok

    concepts = sorted((root / "concepts").glob("*.md")) if (root / "concepts").is_dir() else []
    patterns = sorted((root / "patterns").glob("*.md")) if (root / "patterns").is_dir() else []

    if not concepts:
        ok = fail("no concept found — a KB needs at least one concepts/*.md") and ok
    if not patterns:
        ok = fail("no pattern found — a KB needs at least one patterns/*.md") and ok

    if quick.is_file():
        n = count_lines(quick)
        if n > LIMITS["quick_reference"]:
            ok = fail(
                f"quick-reference.md has {n} lines, limit is {LIMITS['quick_reference']}"
            ) and ok
        ok = check_placeholders(quick, ok)

    if index.is_file():
        ok = check_placeholders(index, ok)

    for path in concepts:
        n = count_lines(path)
        if n > LIMITS["concept"]:
            ok = fail(
                f"concepts/{path.name} has {n} lines, limit is {LIMITS['concept']}"
            ) and ok
        ok = check_placeholders(path, ok)

    for path in patterns:
        n = count_lines(path)
        if n > LIMITS["pattern"]:
            ok = fail(
                f"patterns/{path.name} has {n} lines, limit is {LIMITS['pattern']}"
            ) and ok
        ok = check_placeholders(path, ok)

    # Registration: a KB that exists on disk but not in the index is invisible.
    index_file = Path(args[1]) if len(args) == 2 else root.parent / "_index.yaml"
    perfil = None
    if not index_file.is_file():
        ok = fail(
            f"index file not found: {index_file} — register the domain "
            "(create it from KB_INDEX_TEMPLATE.yaml on the first run)"
        ) and ok
    else:
        registry = index_file.read_text(encoding="utf-8")
        if not re.search(rf"^\s+{re.escape(root.name)}\s*:", registry, re.M):
            ok = fail(
                f"domain {root.name!r} is not registered in {index_file.name} "
                "— an unregistered KB is invisible to whoever consults the index"
            ) and ok
        perfil = read_perfil(registry, root.name)

    summary = ""
    if perfil not in (None, "geral", "normativo"):
        ok = fail(
            f"{index_file.name}: perfil {perfil!r} for {root.name!r} — use `normativo` or `geral`"
        ) and ok
    elif perfil == "normativo":
        try:
            nok, nsum = check_normativo(root, concepts, patterns, strict)
        except Exception as e:  # noqa: BLE001 — a lint must answer FAIL + exit 2, never a traceback
            nok, nsum = fail(
                f"normative check stopped on unexpected content ({type(e).__name__}: {e}) — "
                "check field types against RULE_TEMPLATE.md and report this message"
            ), "aborted"
        ok = nok and ok
        summary = f"; {nsum}"
    else:
        warn_looks_normative(root)

    if ok:
        print(
            f"PASS: KB lint passed ({len(concepts)} concept(s), {len(patterns)} pattern(s){summary})"
        )
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
