#!/usr/bin/env python3
"""report-lint.py — contrato de evidência do BUILD_REPORT (default-FAIL).

Um critério de aceite só pode estar `true` no BUILD_REPORT se a célula de evidência apontar
para algo que este script consegue ABRIR e conferir:
  - `sdd/reports/evidence/{FEATURE}/AT-nnn.log` — 1ª linha `$ <comando>`, output verbatim, não vazio
  - `AVALIACAO_{FEATURE}_<ts>.md` em sdd/reviews/ — veredito de avaliador em contexto fresco
  - `recibo: <nome> YYYY-MM-DD` — só quando o Verify Gate do DEFINE é kind=manual-ux
"✅ por raciocínio", "deve funcionar", "provavelmente" são NEGADOS: declaração não é prova.

Migration listada nos arquivos do relatório (`*.sql`, pasta `migrations/` ou o glob de `layers.sql` do
sdd/config.yaml) exige a linha dela em `## Migrations aplicadas`: mesmo caminho, projeto `nome · ref`,
data AAAA-MM-DD e prova por leitura — log de evidence/{FEATURE}/ ou `recibo: nome AAAA-MM-DD`.
"exit 0" não prova migration: só ler de volta do banco prova.

Só stdlib. Uso:
    python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{FEATURE}.md     # exit 0 ok · 1 violações · 64 uso

A fase Build roda isto antes de declarar sucesso; um hook de pre-commit pode rodá-lo também.
Contrato completo: sdd/templates/fragments/EVIDENCIA.md
"""
import fnmatch
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
FILES_SEC_RE = re.compile(r"^##\s+(?:files\b|arquivos\b|.*manifest)", re.IGNORECASE)
MIG_SEC_RE = re.compile(r"^##\s+migrations aplicadas\b", re.IGNORECASE)
TICK_RE = re.compile(r"`([^`]+)`")
DELETE_CELLS = {"delete", "deleted", "removido", "removida", "excluído", "excluido", "excluída", "excluida"}
EXIT0_RE = re.compile(r"\bexit\s*(?:code\s*)?0\b", re.IGNORECASE)
DATA_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

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
        problema = problema_do_log(p, root, report_dir, feature)
        if problema:
            problems.append(problema)
            continue
        return True, ""
    return False, "; ".join(problems)


def problema_do_log(p, root, report_dir, feature):
    """None = log capturado da própria feature; senão, o motivo."""
    norm = p.replace("\\", "/")
    if f"evidence/{feature}/" not in norm or not norm.endswith((".log", ".txt")):
        return f"`{p}` fora de evidence/{feature}/*.log — só evidência da própria feature vale"
    found = next(
        (c for c in (os.path.join(report_dir, p), os.path.join(root, p), os.path.join(root, REPORTS_DIR, p)) if os.path.isfile(c)),
        None,
    )
    if not found:
        return f"`{p}` não existe"
    if os.path.getsize(found) == 0:
        return f"`{p}` está vazio"
    first = open(found, encoding="utf-8", errors="replace").readline()
    if not first.startswith("$ "):
        return f"`{p}` sem a 1ª linha `$ <comando>` (não é output capturado)"
    return None


def ler_layers_sql(root):
    """Valor de `layers: sql:` do sdd/config.yaml, ou "" (config ausente ou slot vazio)."""
    try:
        linhas = open(os.path.join(root, "sdd", "config.yaml"), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return ""
    dentro = False
    for linha in linhas:
        if re.match(r"^\S", linha):
            dentro = linha.split("#", 1)[0].strip() == "layers:"
            continue
        m = re.match(r"^\s+sql:\s*(.*)$", linha) if dentro else None
        if m:
            v = m.group(1).strip()
            if v[:1] in "\"'":
                return v[1:].split(v[0], 1)[0].strip()
            return v.split("#", 1)[0].strip()
    return ""


def e_migration(caminho, layers_sql):
    if caminho.endswith("/"):
        return False
    if caminho.endswith(".sql") or re.search(r"(?:^|/)migrations/", caminho):
        return True
    return bool(layers_sql) and fnmatch.fnmatchcase(caminho, layers_sql)


def secoes(content, titulo_re):
    """Linhas de cada seção `## ` cujo título casa titulo_re (até o próximo `## `)."""
    todas, atual = [], None
    for raw in content.splitlines():
        if raw.startswith("## "):
            atual = [] if titulo_re.match(raw) else None
            if atual is not None:
                todas.append(atual)
            continue
        if atual is not None:
            atual.append(raw.strip())
    return todas


def linhas_de_tabela(linhas):
    return [split_row(l) for l in linhas if l.startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", l)]


def migrations_listadas(content, layers_sql):
    vistas = []
    for sec in secoes(content, FILES_SEC_RE):
        for cells in linhas_de_tabela(sec):
            if any(c.strip("`* ").lower() in DELETE_CELLS for c in cells):
                continue
            m = TICK_RE.search("|".join(cells))
            if m and e_migration(m.group(1).strip(), layers_sql) and m.group(1).strip() not in vistas:
                vistas.append(m.group(1).strip())
    return vistas


def linhas_migrations(content):
    """{caminho: (projeto, data, prova)} da seção `## Migrations aplicadas`."""
    regs = {}
    for sec in secoes(content, MIG_SEC_RE):
        rows = linhas_de_tabela(sec)
        if not rows:
            continue
        cab = [c.lower() for c in rows[0]]
        def col(prefixos, reserva):
            return next((i for i, c in enumerate(cab) if c.startswith(prefixos)), reserva)
        ia, ip = col(("arquivo", "file"), 0), col(("projeto", "project"), 1)
        id_, iv = col(("aplicada", "applied", "data", "date"), 2), col(("prova", "proof"), 3)
        for cells in rows[1:]:
            cells = cells + [""] * (4 - len(cells))
            m = TICK_RE.search(cells[ia]) if ia < len(cells) else None
            if m:
                pega = lambda i: cells[i] if i < len(cells) else ""
                regs[m.group(1).strip()] = (pega(ip), pega(id_), pega(iv))
    return regs


def prova_migration(cell, root, report_dir, feature):
    """None = prova por leitura aceita; senão, o motivo."""
    if cell.strip() in ("", "—", "-"):
        return "prova por leitura vazia"
    if EXIT0_RE.search(cell):
        return "exit 0 não prova migration — leia de volta do banco (migration list, select)"
    if FAKE_RE.search(cell):
        return "declaração não é prova"
    if RECIBO_RE.search(cell):
        return None
    problemas = [problema_do_log(p, root, report_dir, feature) for p in PATH_RE.findall(cell)]
    if any(x is None for x in problemas):
        return None
    return "; ".join(x for x in problemas if x) or f"sem log de evidence/{feature}/ nem `recibo: nome AAAA-MM-DD`"


def check_migrations(content, root, report_dir, feature):
    violations = []
    regs = linhas_migrations(content)
    for mig in migrations_listadas(content, ler_layers_sql(root)):
        if mig not in regs:
            violations.append(f"migration `{mig}` sem linha em `## Migrations aplicadas` (mesmo caminho) — aplicada onde? provada como?")
            continue
        projeto, data, prova = regs[mig]
        partes = [x.strip(" `") for x in projeto.split("·")]
        if len(partes) < 2 or not all(partes):
            violations.append(f"migration `{mig}`: projeto sem `nome · ref` (`{projeto}`)")
        if not DATA_RE.search(data):
            violations.append(f"migration `{mig}`: sem data AAAA-MM-DD em \"Aplicada em\"")
        motivo = prova_migration(prova, root, report_dir, feature)
        if motivo:
            violations.append(f"migration `{mig}`: {motivo}")
    return violations


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
    violations += check_migrations(content, root, report_dir, feature)
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
        if any(v.startswith("migration `") for v in violations):
            print("→ migration: aplique e leia de volta (.agents/skills/sdd-build/references/aplicar-migration.md) e registre "
                  "a linha em `## Migrations aplicadas`.", file=sys.stderr)
        return 1
    print(f"✅ {path}: todo `true` tem evidência abrível")
    print("RESULTADO: VERDE")
    print("→ o relatório pode ser commitado.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
