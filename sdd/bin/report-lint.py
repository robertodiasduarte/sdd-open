#!/usr/bin/env python3
"""report-lint.py — contrato de evidência do BUILD_REPORT (default-FAIL).

Um critério de aceite só pode estar `true` no BUILD_REPORT se a célula de evidência apontar
para algo que este script consegue ABRIR e conferir:
  - `sdd/reports/evidence/{FEATURE}/AT-nnn.log` — 1ª linha `$ <comando>`, output verbatim, não vazio
  - `AVALIACAO_{FEATURE}_<ts>.md` em sdd/reviews/ — veredito de avaliador em contexto fresco
  - `recibo: <nome> YYYY-MM-DD` — só quando o Verify Gate do DEFINE é kind=manual-ux
"✅ por raciocínio", "deve funcionar", "provavelmente" são NEGADOS: declaração não é prova.

Só stdlib. Uso:
    python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{FEATURE}.md     # exit 0 ok · 1 violações · 64 uso

A fase Build roda isto antes de declarar sucesso; um hook de pre-commit pode rodá-lo também.
Contrato completo: sdd/templates/fragments/EVIDENCIA.md
"""
import glob
import os
import re
import sys

REPORT_RE = re.compile(r"^BUILD_REPORT_(.+)\.md$")
AT_ROW_RE = re.compile(r"^\|\s*(AT-\d+[A-Za-z0-9_-]*)\s*(?<!\\)\|")
TRUE_RE = re.compile(r"^\s*(?:true\b|✅|pass(?:ed)?\b|verde\b)", re.IGNORECASE)
RECIBO_RE = re.compile(r"recibo:\s*\S+.*\b\d{4}-\d{2}-\d{2}\b", re.IGNORECASE)
FAKE_RE = re.compile(
    r"por racioc[ií]nio|by reasoning|by inspection|deve funcionar|provavelmente|should work",
    re.IGNORECASE,
)
PATH_RE = re.compile(r"`([^`]+\.(?:log|txt|md))`")
VERDICT_RE = re.compile(
    r"\*\*Veredito do avaliador(?: \(C1\))?:\*\*\s*(PASS_PENDENTE_RECIBO|PASS|NEEDS_WORK|N\.?A\.?)\b([^\n]*)",
    re.IGNORECASE,
)
SPLIT_RE = re.compile(r"(?<!\\)\|")

FEATURES_DIR = "sdd/features"
REVIEWS_DIR = "sdd/reviews"
REPORTS_DIR = "sdd/reports"


def split_row(line):
    return [c.strip() for c in SPLIT_RE.split(line.strip().strip("|"))]


def define_gate_kind(root, feature):
    cands = glob.glob(os.path.join(root, FEATURES_DIR, f"DEFINE_{feature}.md"))
    if not cands:
        base = re.sub(r"_S\d+[A-Za-z]?$", "", feature)
        cands = glob.glob(os.path.join(root, FEATURES_DIR, f"DEFINE_{base}*.md"))
    for c in cands:
        try:
            m = re.search(r"^\s*kind:\s*([a-z-]+)", open(c, encoding="utf-8", errors="replace").read(), re.MULTILINE)
            if m:
                return m.group(1)
        except OSError:
            pass
    return None


def evidence_ok(cell, root, report_dir, feature, gate_kind, warnings):
    if FAKE_RE.search(cell):
        return False, "evidência declarativa ('por raciocínio'/'deve funcionar') não é prova"
    if RECIBO_RE.search(cell):
        if gate_kind is None:
            warnings.append(f"recibo aceito sem DEFINE_{feature}.md localizável (kind do gate desconhecido)")
            return True, ""
        if gate_kind == "manual-ux":
            return True, ""
        return False, f"recibo humano só vale em gate manual-ux (o DEFINE da feature tem kind={gate_kind})"
    paths = PATH_RE.findall(cell)
    if not paths:
        return False, "sem arquivo de evidência, AVALIACAO_*.md ou recibo humano"
    problems = []
    for p in paths:
        base = os.path.basename(p)
        if base.startswith("AVALIACAO_"):
            if not base.startswith(f"AVALIACAO_{feature}_"):
                problems.append(f"`{p}` não é avaliação desta feature ({feature})")
                continue
            found = next((c for c in (os.path.join(root, p), os.path.join(root, REVIEWS_DIR, base)) if os.path.isfile(c)), None)
            if not found:
                problems.append(f"`{p}` não existe em {REVIEWS_DIR}/")
            elif os.path.getsize(found) == 0:
                problems.append(f"`{p}` está vazio")
            else:
                return True, ""
            continue
        norm = p.replace("\\", "/")
        if f"evidence/{feature}/" not in norm or not norm.endswith((".log", ".txt")):
            problems.append(f"`{p}` fora de evidence/{feature}/*.log — só evidência da própria feature vale")
            continue
        found = next(
            (c for c in (os.path.join(report_dir, p), os.path.join(root, p), os.path.join(root, REPORTS_DIR, p)) if os.path.isfile(c)),
            None,
        )
        if not found:
            problems.append(f"`{p}` não existe")
            continue
        if os.path.getsize(found) == 0:
            problems.append(f"`{p}` está vazio")
            continue
        first = open(found, encoding="utf-8", errors="replace").readline()
        if not first.startswith("$ "):
            problems.append(f"`{p}` sem a 1ª linha `$ <comando>` (não é output capturado)")
            continue
        return True, ""
    return False, "; ".join(problems)


def check(content, root, report_dir, feature):
    violations, warnings = [], []
    gate_kind = define_gate_kind(root, feature)
    header = None
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("|") and ("Evid" in line) and ("Resultado" in line or "Status" in line or "Passou" in line):
            cols = [c.lower() for c in split_row(line)]
            n = len(cols)
            r = next((i for i, c in enumerate(cols) if c.startswith(("resultado", "status", "passou"))), None)
            e = next((i for i, c in enumerate(cols) if c.startswith("evid")), None)
            header = None if r is None or e is None else {"result": n - r, "evid": n - e}
            continue
        m = AT_ROW_RE.match(line)
        if not m or not header:
            continue
        cells = split_row(line)
        if len(cells) < max(header["result"], header["evid"]):
            continue
        result = cells[len(cells) - header["result"]]
        evid = cells[len(cells) - header["evid"]]
        if not TRUE_RE.match(result):
            continue
        ok, why = evidence_ok(evid, root, report_dir, feature, gate_kind, warnings)
        if not ok:
            violations.append(f"{m.group(1)}: `{result}` sem evidência válida — {why}")

    for vm in VERDICT_RE.finditer(content):
        verdict, rest = vm.group(1).upper(), vm.group(2)
        if verdict.replace(".", "") == "NA":
            continue
        refs = [p for p in PATH_RE.findall(rest) if os.path.basename(p).startswith(f"AVALIACAO_{feature}_")]
        exists = any(
            os.path.isfile(c)
            for p in refs
            for c in (os.path.join(root, p), os.path.join(root, REVIEWS_DIR, os.path.basename(p)))
        )
        if not exists:
            violations.append(f"Veredito do avaliador `{verdict}` sem `AVALIACAO_{feature}_*.md` existente em {REVIEWS_DIR}/")
    return violations, warnings


def main(argv):
    if len(argv) != 2:
        print("uso: report-lint.py sdd/reports/BUILD_REPORT_{FEATURE}.md", file=sys.stderr)
        return 64
    path = argv[1]
    rm = REPORT_RE.match(os.path.basename(path))
    if not rm:
        print(f"🛑 {path}: o nome precisa ser BUILD_REPORT_{{FEATURE}}.md", file=sys.stderr)
        return 64
    try:
        content = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"🛑 não consegui ler {path}: {e}", file=sys.stderr)
        return 64
    root = os.popen("git rev-parse --show-toplevel 2>/dev/null").read().strip() or os.getcwd()
    report_dir = os.path.dirname(os.path.abspath(path))
    violations, warnings = check(content, root, report_dir, rm.group(1))
    for w in warnings:
        print(f"⚠️  {w}")
    if violations:
        for v in violations:
            print(f"🛑 {v}", file=sys.stderr)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print(f"→ produza `evidence/{rm.group(1)}/AT-nnn.log` (1ª linha `$ cmd`, output verbatim), cite "
              f"`AVALIACAO_{rm.group(1)}_<ts>.md`, ou `recibo: nome YYYY-MM-DD` (só gate manual-ux) — ou mantenha `false`.",
              file=sys.stderr)
        return 1
    print(f"✅ {path}: todo `true` tem evidência abrível")
    print("RESULTADO: VERDE")
    print("→ o relatório pode ser commitado.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
