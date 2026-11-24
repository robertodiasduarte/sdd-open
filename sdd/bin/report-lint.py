#!/usr/bin/env python3
"""report-lint.py — contrato de evidência do BUILD_REPORT (default-FAIL, fail-closed).

Um critério de aceite só pode estar `true` no BUILD_REPORT se a célula de evidência apontar
para algo que este script consegue ABRIR e conferir:
  - `sdd/reports/evidence/{FEATURE}/AT-nnn.log` — 1ª linha `$ <comando>`, output verbatim, não vazio
  - `AVALIACAO_{FEATURE}_<ts>.md` em sdd/reviews/ — veredito de avaliador em contexto fresco
  - `recibo: <nome> YYYY-MM-DD` — só quando o Verify Gate do DEFINE é kind=manual-ux
"✅ por raciocínio", "deve funcionar", "provavelmente" são NEGADOS: declaração não é prova.
Evidência que existe no disco mas o git IGNORA não vai para o commit: também é negada.

O relatório precisa provar a AVALIAÇÃO, não só citá-la quando aparece (ausência reprova):
  - `AVALIACAO_{FEATURE}_<AAAAMMDD>….md` não vazio e não ignorado em sdd/reviews/; ou
  - `avaliador: N.A. (<motivo>)` — negado quando o File Manifest do DESIGN toca ≥ N camadas de
    `layers:` (N = `evidence.require_avaliacao_layers` do sdd/config.yaml, default 2); ou
  - `avaliador: PENDENTE (<motivo>)` — o build travou antes do avaliador; passa aqui com aviso,
    e a fase Release aborta (`--pendente`).
E a tabela de critérios tem de ser reconhecida (colunas Resultado/Status/Passou/Result e Evidência).

Migration listada nos arquivos do relatório (`*.sql`, pasta `migrations/` ou o glob de `layers.sql` do
sdd/config.yaml) exige a linha dela em `## Migrations aplicadas`: mesmo caminho, projeto `nome · ref`,
data AAAA-MM-DD e prova por leitura — log de evidence/{FEATURE}/ ou `recibo: nome AAAA-MM-DD`.
"exit 0" não prova migration: só ler de volta do banco prova.

Lint e tipos (F30): com `project.lint_cmd` cheio no sdd/config.yaml, `evidence/{FEATURE}/LINT.log` é obrigatório; com
`project.typecheck_cmd` cheio, `TIPOS.log`. Cada um com a 1ª linha `$ <comando do slot>[ arquivos]`, não ignorado
pelo git e terminando em `[exit=0]` — ou em `[exit≠0]` com o `*.antes.log` do mesmo comando do slot também falhando
(dívida antiga: aviso; o de antes não tem os arquivos novos, então só o comando do slot precisa bater). Os dois vazios: a linha `lint: slot vazio` no relatório; sem ela, só aviso.

Vermelho antes do verde (F30 S2): numa tabela de critérios com a coluna `Antes`, o DEFINE da feature classifica cada AT
`true` — comportamento novo (gate `test`/`cmd`) exige `evidence/{FEATURE}/AT-nnn.antes.log` do mesmo comando do log da
evidência terminando em `[exit=n]`, n fora de 0, 126 e 127; `The system shall continue to` exige o antes `[exit=0]`;
gate de outro kind (inclusive `manual-ux`) aceita `N.A. (<motivo>)`. Tabela sem a coluna (relatório anterior): aviso.

Só stdlib. Uso:
    python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{FEATURE}.md     # exit 0 ok · 1 violações · 64 uso
    python3 sdd/bin/report-lint.py --stdin sdd/reports/BUILD_REPORT_{FEATURE}.md < conteudo.md
    python3 sdd/bin/report-lint.py --pendente sdd/reports/BUILD_REPORT_{FEATURE}.md …   # 1 se há PENDENTE

A fase Build roda isto antes de declarar sucesso; a fase Release roda os dois primeiros modos.
Contrato completo: sdd/templates/fragments/EVIDENCIA.md
"""
import fnmatch
import glob
import os
import re
import subprocess
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
# Veredito em qualquer forma: inline `**Veredito do avaliador (C1):** PASS`, título `## Veredito do
# avaliador (C1)` + parágrafo seguinte, ou tabela `| **Veredito do avaliador (C1)** | PASS |`. O valor é
# o 1º token de veredito depois do rótulo, no mesmo parágrafo ou no seguinte (quando o rótulo é título); numa
# tabela, só a linha do rótulo. Também valem `Veredito do avaliador:` e `## Veredito do avaliador` sem (C1).
VERDICT_LABEL_RE = re.compile(
    r"Veredito do avaliador \(C1\)|\*\*Veredito do avaliador:\*\*|\*\*Veredito do avaliador\*\*"
    r"|^#{1,6}[ \t]+Veredito do avaliador\b|^[ \t>*_-]*Veredito do avaliador:|\|[ \t]*Veredito do avaliador\b",
    re.IGNORECASE | re.MULTILINE,
)
VERDICT_VALUE_RE = re.compile(r"\b(PASS_PENDENTE_RECIBO|PENDENTE|PASS|NEEDS_WORK|N\.?A\.?)\b", re.IGNORECASE)
# Declaração sobre o avaliador, em linha própria; o tipo em CAIXA ALTA, para que "avaliador na rodada 1"
# não vire N.A. nem "avaliador pendente de recibo" vire PENDENTE.
DECL_RE = re.compile(
    r"^[ \t>*_|-]*(?:Veredito do )?avaliador(?: \(C1\))?[ \t*:|]*"
    r"(?P<tipo>(?-i:N\.A\.?|NA|PENDENTE))(?![A-Za-z_])[ \t*]*(?:\((?P<motivo>[^)\n]*)\))?",
    re.IGNORECASE | re.MULTILINE,
)
MANIFEST_RE = re.compile(
    r"^##[ \t]+(?:\d+(?:\.\d+)*\.?[ \t]+)?File Manifest\b[^\n]*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)
PARAGRAPH_END_RE = re.compile(r"\n[ \t]*\n")
FENCE_RE = re.compile(r"^[ \t]*(```|~~~)")
SPLIT_RE = re.compile(r"(?<!\\)\|")
# "## Files Created", "## 2. Arquivos criados", "## Fase A — Files Created/Modified", "## … Manifest …"
FILES_SEC_RE = re.compile(r"^##\s+(?:[\d.]+\s+|.*?[—–]\s*)?(?:files\b|arquivos\b)|^##\s+.*manifest", re.IGNORECASE)
MIG_SEC_RE = re.compile(r"^##\s+migrations aplicadas\b", re.IGNORECASE)
TICK_RE = re.compile(r"`([^`]+)`")
DELETE_CELLS = {"delete", "deleted", "removido", "removida", "excluído", "excluido", "excluída", "excluida"}
EXIT0_RE = re.compile(r"\bexit\s*(?:code\s*)?0\b", re.IGNORECASE)
DATA_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

FEATURES_DIR = "sdd/features"
REVIEWS_DIR = "sdd/reviews"
REPORTS_DIR = "sdd/reports"
CAMADAS_DEFAULT = 2

# Classes de violação: cada uma tem a sua linha `→` no fim da saída.
TABELA = "tabela"
EVIDENCIA = "evidência"
AUSENTE = "avaliação ausente"
DECLARACAO = "declaração"
MIGRATION = "migration"
LINT = "lint"
ANTES = "vermelho antes"
# F30: com o slot cheio, o build guarda a última execução do comando sobre os arquivos da tarefa neste log.
LOGS_LINT = (("lint_cmd", "LINT.log"), ("typecheck_cmd", "TIPOS.log"))
SLOT_VAZIO_RE = re.compile(r"^[ \t>*_|-]*`?lint: slot vazio`?", re.MULTILINE)
EXIT_FIM_RE = re.compile(r"^\[exit=(-?\d+)\]$")
NOVO, CONTINUA, FORA = "novo", "continua", "fora"
CONTINUA_RE = re.compile(r"^(?:the system shall continue to\b|non-regression\b|não-regressão\b)", re.IGNORECASE)
NA_RE = re.compile(r"^\s*N\.?A\.?(?:\s|\(|$)", re.IGNORECASE)
SEM_COLUNA_ANTES = ("a tabela de critérios não tem a coluna `Antes` (relatório anterior à v2.27.0): o vermelho antes do "
                    "verde não foi conferido")
IGNORADO_MSG = ("existe, mas o git o IGNORA (`git check-ignore -v` mostra a regra): não vai para o commit — "
                "remova a regra ou use `git add -f`")


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


def git_ignorado(root, caminho, warnings):
    """True se o git ignora o caminho (existe no disco, nunca entra no commit). Sem git: aviso, False."""
    try:
        r = subprocess.run(["git", "-C", root, "check-ignore", "-q", "--", caminho],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        warnings.append(f"`git check-ignore` indisponível ({type(exc).__name__}): persistência não conferida")
        return False
    if r.returncode == 0:
        return True
    if r.returncode != 1:
        warnings.append(f"`git check-ignore` saiu {r.returncode} (fora de um repositório git?): persistência não conferida")
    return False


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
            elif git_ignorado(root, found, warnings):
                problems.append(f"`{p}` {IGNORADO_MSG}")
            else:
                return True, ""
            continue
        problema = problema_do_log(p, root, report_dir, feature)
        if problema:
            problems.append(problema)
            continue
        if git_ignorado(root, caminho_do_log(p, root, report_dir), warnings):
            problems.append(f"`{p}` {IGNORADO_MSG}")
            continue
        return True, ""
    return False, "; ".join(problems)


def caminho_do_log(p, root, report_dir):
    return next(
        (c for c in (os.path.join(report_dir, p), os.path.join(root, p), os.path.join(root, REPORTS_DIR, p)) if os.path.isfile(c)),
        None,
    )


def problema_do_log(p, root, report_dir, feature):
    """None = log capturado da própria feature; senão, o motivo."""
    norm = p.replace("\\", "/")
    if f"evidence/{feature}/" not in norm or not norm.endswith((".log", ".txt")):
        return f"`{p}` fora de evidence/{feature}/*.log — só evidência da própria feature vale"
    found = caminho_do_log(p, root, report_dir)
    if not found:
        return f"`{p}` não existe"
    if os.path.getsize(found) == 0:
        return f"`{p}` está vazio"
    first = open(found, encoding="utf-8", errors="replace").readline()
    if not first.startswith("$ "):
        return f"`{p}` sem a 1ª linha `$ <comando>` (não é output capturado)"
    return None


def ler_mapa(root, mapa):
    """{chave: valor} do mapa de 1 nível `mapa:` do sdd/config.yaml ({} se config ausente)."""
    try:
        linhas = open(os.path.join(root, "sdd", "config.yaml"), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return {}
    dentro, valores = False, {}
    for linha in linhas:
        if re.match(r"^\S", linha):
            dentro = linha.split("#", 1)[0].strip() == mapa + ":"
            continue
        m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", linha) if dentro else None
        if m and m.group(1) not in valores:
            v = m.group(2).strip()
            if v[:1] in "\"'":
                v = v[1:].split(v[0], 1)[0].strip()
            else:
                v = v.split("#", 1)[0].strip()
            valores[m.group(1)] = v
    return valores


def ler_layers_sql(root):
    """Valor de `layers: sql:` do sdd/config.yaml, ou "" (config ausente ou slot vazio)."""
    return ler_mapa(root, "layers").get("sql", "")


def limite_camadas(root, warnings):
    """N de `evidence.require_avaliacao_layers` (default 2; valor inválido → 2 com aviso)."""
    v = ler_mapa(root, "evidence").get("require_avaliacao_layers", "")
    if v == "":
        return CAMADAS_DEFAULT
    if re.fullmatch(r"[1-9]\d*", v):
        return int(v)
    warnings.append(f"`evidence.require_avaliacao_layers: {v}` não é inteiro ≥ 1 — usei {CAMADAS_DEFAULT}")
    return CAMADAS_DEFAULT


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
        if len(partes) < 2 or any(x in ("", "—", "-") for x in partes):
            violations.append(f"migration `{mig}`: projeto sem `nome · ref` (`{projeto}`)")
        if not DATA_RE.search(data):
            violations.append(f"migration `{mig}`: sem data AAAA-MM-DD em \"Aplicada em\"")
        motivo = prova_migration(prova, root, report_dir, feature)
        if motivo:
            violations.append(f"migration `{mig}`: {motivo}")
    return violations


def strip_fences(content):
    """O interior de blocos ``` … ``` vira linha vazia (a numeração das linhas fica)."""
    out, fence, delim = [], False, None
    for line in content.split("\n"):
        m = FENCE_RE.match(line)
        if m and not fence:
            fence, delim = True, m.group(1)
            out.append("")
            continue
        if fence:
            out.append("")
            if line.strip().startswith(delim):
                fence, delim = False, None
            continue
        out.append(line)
    return "\n".join(out)


def verdicts_in(content):
    """(veredito, texto onde o AVALIACAO vale) para cada rótulo de veredito."""
    found = []
    for lm in VERDICT_LABEL_RE.finditer(content):
        inicio = content.rfind("\n", 0, lm.start()) + 1
        fim = content.find("\n", lm.end())
        fim = len(content) if fim < 0 else fim
        if content[inicio:fim].lstrip().startswith("|"):
            scope = content[lm.end():fim]  # numa tabela, a unidade é a linha do rótulo
        else:
            parts = PARAGRAPH_END_RE.split(content[lm.end():], 2)
            scope = parts[0]
            if not VERDICT_VALUE_RE.search(scope) and len(parts) > 1:
                scope = parts[0] + "\n\n" + parts[1]
        vm = VERDICT_VALUE_RE.search(scope)
        if vm:
            found.append((vm.group(1).upper(), scope))
    return found


def declaracoes(content):
    """[(tipo 'N.A.'|'PENDENTE', motivo, linha)] fora de bloco cercado."""
    limpo = strip_fences(content)
    out = []
    for m in DECL_RE.finditer(limpo):
        tipo = "PENDENTE" if m.group("tipo").upper() == "PENDENTE" else "N.A."
        out.append((tipo, (m.group("motivo") or "").strip(), limpo.count("\n", 0, m.start()) + 1))
    return out


def prova_avaliacao(root, feature, warnings):
    """(nome do AVALIACAO que prova | None, [os que existem mas o git ignora])."""
    pat = re.compile(r"^AVALIACAO_" + re.escape(feature) + r"_\d{8}.*\.md$")
    try:
        nomes = sorted(os.listdir(os.path.join(root, REVIEWS_DIR)))
    except OSError:
        return None, []
    ignorados = []
    for n in nomes:
        p = os.path.join(root, REVIEWS_DIR, n)
        if not (pat.match(n) and os.path.isfile(p) and os.path.getsize(p) > 0):
            continue
        if git_ignorado(root, p, warnings):
            ignorados.append(n)
            continue
        return n, []
    return None, ignorados


def design_da_feature(root, feature):
    base = re.sub(r"_S\d+[A-Za-z]?$", "", feature)
    for n in dict.fromkeys((feature, base)):
        if os.path.isfile(os.path.join(root, FEATURES_DIR, f"DESIGN_{n}.md")):
            return n
    return None


def camadas_do_design(root, feature):
    """(n, 'nomes, separados', causa). n=None quando não dá para contar; a causa vai no aviso."""
    globs = dict((k, v) for k, v in ler_mapa(root, "layers").items() if v)
    if not globs:
        return None, "", "`layers:` do sdd/config.yaml sem nenhum glob preenchido"
    nome = design_da_feature(root, feature)
    if nome is None:
        return None, "", f"DESIGN_{feature}.md não encontrado em {FEATURES_DIR}/"
    try:
        texto = open(os.path.join(root, FEATURES_DIR, f"DESIGN_{nome}.md"), encoding="utf-8", errors="replace").read()
    except OSError:
        return None, "", f"DESIGN_{nome}.md ilegível"
    m = MANIFEST_RE.search(texto)
    if not m:
        return None, "", f"DESIGN_{nome}.md sem `File Manifest`"
    linhas = [l for l in m.group(1).split("\n") if re.match(r"^\|\s*\d+\s*\|", l)]
    camadas = set()
    for l in linhas:
        cols = l.split("|")
        celula = cols[2] if len(cols) > 2 else ""
        for p in re.findall(r"`([^`]+)`", celula) or [celula]:
            p = p.strip()
            if p.startswith("./"):
                p = p[2:]
            for camada, g in globs.items():
                if fnmatch.fnmatchcase(p, g):
                    camadas.add(camada)
    if not camadas:
        return None, "", f"nenhum caminho do File Manifest de DESIGN_{nome}.md casa os globs de `layers:`"
    return len(camadas), ", ".join(sorted(camadas)), ""


def existencia_avaliacao(content, root, feature, warnings):
    """Ausência reprova: AVALIACAO que prova → declaração com motivo → N.A. contra as camadas."""
    nome, ignorados = prova_avaliacao(root, feature, warnings)
    if nome:
        return []
    decls = declaracoes(content)
    limite = limite_camadas(root, warnings)
    if not decls:
        if ignorados:
            return [(AUSENTE, f"`{REVIEWS_DIR}/{ignorados[0]}` {IGNORADO_MSG}: `git add -f {REVIEWS_DIR}/{ignorados[0]}`")]
        n, nomes, causa = camadas_do_design(root, feature)
        contagem = f"o manifest toca {n} ({nomes})" if n else f"contagem impossível: {causa}"
        return [(AUSENTE,
                 f"não há `AVALIACAO_{feature}_<AAAAMMDD-HHMM>.md` em {REVIEWS_DIR}/ (não vazio e não ignorado pelo git) "
                 "nem linha sobre o avaliador. Saídas, nesta ordem: (1) rode o avaliador de contexto fresco "
                 f"(passo 5d da `sdd-build`); (2) `avaliador: N.A. (<motivo>)`, só com menos de {limite} camadas — "
                 f"{contagem}; (3) `avaliador: PENDENTE (<motivo>)`, se o build travou antes do avaliador")]
    sem_motivo = [(tipo, linha) for tipo, motivo, linha in decls if not motivo]
    if sem_motivo:
        return [(DECLARACAO, f"`{tipo}` sem motivo (linha {linha}) — escreva `avaliador: {tipo} (<motivo>)`")
                for tipo, linha in sem_motivo]
    pendentes = [(motivo, linha) for tipo, motivo, linha in decls if tipo == "PENDENTE"]
    if pendentes:
        for motivo, linha in pendentes:
            warnings.append(f"PENDENTE: avaliação PENDENTE ({motivo}), linha {linha} — a release não sai enquanto esta linha existir")
        return []
    n, nomes, causa = camadas_do_design(root, feature)
    if n is None:
        warnings.append(f"N.A. aceito sem conferir camadas — {causa}; preencha `layers:` em sdd/config.yaml para a contagem valer")
        return []
    if n >= limite:
        return [(DECLARACAO,
                 f"`N.A.` não vale: o File Manifest de DESIGN_{design_da_feature(root, feature)}.md toca {n} camadas "
                 f"({nomes}), e o limite é {limite} (`evidence.require_avaliacao_layers`). Rode o avaliador, ou declare "
                 "`avaliador: PENDENTE (<motivo>)` se o build travou antes dele")]
    return []


def tabela_reconhecida(line):
    """{'result': i, 'evid': j} contados do FIM da linha, ou None se o cabeçalho não é de critérios."""
    if not (line.startswith("|") and "Evid" in line and ("Result" in line or "Status" in line or "Passou" in line)):
        return None
    cols = [c.lower() for c in split_row(line)]
    n = len(cols)
    r = next((i for i, c in enumerate(cols) if c.startswith(("resultado", "status", "passou", "result"))), None)
    e = next((i for i, c in enumerate(cols) if c.startswith("evid")), None)
    a = next((i for i, c in enumerate(cols) if c == "antes" or c.startswith("antes ")), None)
    if r is None or e is None:
        return None
    return {"result": n - r, "evid": n - e, "antes": None if a is None else n - a}


def ler_log_lint(caminho):
    """(1ª linha sem o `$ `, exit do fim) de um log de lint/tipos; None em cada parte que não está no formato."""
    try:
        cheias = [l.strip() for l in open(caminho, encoding="utf-8", errors="replace").read().split("\n") if l.strip()]
    except OSError:
        return None, None
    rodado = cheias[0][2:].strip() if cheias and cheias[0].startswith("$ ") else None
    fim = EXIT_FIM_RE.match(cheias[-1]) if len(cheias) > 1 else None
    return rodado, (fim.group(1) if fim else None)


def problema_log_lint(root, feature, nome, cmd, warnings):
    """O que falta no log de lint/tipos (texto), ou None quando ele prova o comando do slot verde (ou a dívida antiga,
    com aviso: o mesmo comando já falhava no log de antes do build)."""
    rel = f"{REPORTS_DIR}/evidence/{feature}/{nome}"
    caminho = os.path.join(root, rel)
    if not os.path.isfile(caminho):
        return f"`{rel}` não existe"
    if git_ignorado(root, caminho, warnings):
        return f"`{rel}` {IGNORADO_MSG}"
    rodado, rc = ler_log_lint(caminho)
    if rodado is None:
        return f"`{rel}`: a 1ª linha não é `$ <comando>`"
    if rodado != cmd and not rodado.startswith(cmd + " "):
        return f"`{rel}`: a 1ª linha roda `{rodado}`, não o comando do slot (`{cmd}`)"
    if rc is None:
        return f"`{rel}`: a última linha não é `[exit=<n>]` (grave o log por um script em bash, com rc=$?)"
    if rc == "0":
        return None
    rel_antes = rel[:-len(".log")] + ".antes.log"
    antes = os.path.join(root, rel_antes)
    if os.path.isfile(antes) and not git_ignorado(root, antes, warnings):
        rodado_antes, rc_antes = ler_log_lint(antes)
        mesmo_slot = rodado_antes is not None and (rodado_antes == cmd or rodado_antes.startswith(cmd + " "))
        # 126/127: a ferramenta nem rodou (não instalada, sem permissão), o que não prova dívida nenhuma
        if mesmo_slot and rc_antes not in (None, "0", "126", "127") and rc not in ("126", "127"):
            warnings.append(f"`{rel}` terminou em `[exit={rc}]`, e o mesmo comando já falhava antes do build "
                            f"(`{rel_antes}`, `[exit={rc_antes}]`): dívida antiga; confira que os erros são os de antes")
            return None
    return (f"`{rel}` terminou em `[exit={rc}]`: o comando acusa erro, e não há `{rel_antes}` do mesmo comando "
            "falhando antes do build")


def check_lint(content, root, feature, warnings):
    """F30: slot cheio exige o log verde do comando; os dois vazios pedem a linha `lint: slot vazio` (só aviso)."""
    projeto = ler_mapa(root, "project")
    cheios = [(slot, nome, projeto.get(slot, "").strip()) for slot, nome in LOGS_LINT if projeto.get(slot, "").strip()]
    if not cheios:
        if not SLOT_VAZIO_RE.search(strip_fences(content)):
            warnings.append("lint e tipos com o slot vazio (project.lint_cmd e project.typecheck_cmd), e o relatório "
                            "não diz isso: escreva a linha `lint: slot vazio`")
        return []
    violations = []
    for slot, nome, cmd in cheios:
        problema = problema_log_lint(root, feature, nome, cmd, warnings)
        if problema:
            violations.append((LINT, f"project.{slot} está cheio: {problema}"))
    return violations


def _sem_marcacao(celula):
    return re.sub(r"[*`]", "", celula).strip()


def ats_do_define(root, feature):
    """{AT-nnn: classe} das tabelas do DEFINE da feature, ou None sem DEFINE. A classe vem do kind (coluna com `kind`
    ou `Gate` no cabeçalho; sem ela, o kind do verify_gate) e do padrão do AT: uma célula que COMEÇA por
    `The system shall continue to` ou `Non-regression` (revisão do DESIGN, N1: citar a expressão no meio não conta)."""
    cands = glob.glob(os.path.join(root, FEATURES_DIR, f"DEFINE_{feature}.md"))
    if not cands:
        base = re.sub(r"_S\d+[A-Za-z]?$", "", feature)
        cands = glob.glob(os.path.join(root, FEATURES_DIR, f"DEFINE_{base}*.md"))
    if not cands:
        return None
    try:
        linhas = open(cands[0], encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return None
    padrao = define_gate_kind(root, feature) or ""
    ats, col_kind = {}, None
    for raw in linhas:
        line = raw.strip()
        if not line.startswith("|"):
            col_kind = None
            continue
        cells = split_row(line)
        if not AT_ROW_RE.match(line):
            if any(c.lower() == "id" for c in cells):
                col_kind = next((i for i, c in enumerate(cells) if "kind" in c.lower() or c.lower().startswith("gate")), None)
            continue
        kind = (_sem_marcacao(cells[col_kind]) if col_kind is not None and col_kind < len(cells) else padrao).lower()
        continua = any(CONTINUA_RE.match(_sem_marcacao(c)) for c in cells[1:])
        if not kind.startswith(("test", "cmd")):
            ats[cells[0]] = FORA
        else:
            ats[cells[0]] = CONTINUA if continua else NOVO
    return ats


def primeira_linha(caminho):
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            return f.readline().rstrip("\n")
    except OSError:
        return None


def problema_antes(at, classe, cell, evid, root, report_dir, feature, warnings):
    """O que falta na coluna `Antes` de um AT `true` (texto), ou None."""
    if classe == FORA:
        return None
    if NA_RE.match(cell):
        return f"`N.A.` não vale para um AT de gate `test`/`cmd` ({'shall continue to' if classe == CONTINUA else 'comportamento novo'})"
    nome = f"{at}.antes.log"
    paths = [p for p in PATH_RE.findall(cell) if os.path.basename(p.replace("\\", "/")) == nome]
    if not paths:
        return f"a coluna `Antes` não cita `evidence/{feature}/{nome}`"
    rel = paths[0]
    problema = problema_do_log(rel, root, report_dir, feature)
    if problema:
        return problema
    caminho = caminho_do_log(rel, root, report_dir)
    if git_ignorado(root, caminho, warnings):
        return f"`{rel}` {IGNORADO_MSG}"
    rodado, rc = ler_log_lint(caminho)
    if rc is None:
        return f"`{rel}`: a última linha não é `[exit=<n>]` (grave o log por um script em bash, com rc=$?)"
    if classe == NOVO and rc in ("0", "126", "127"):
        return f"`{rel}` terminou em `[exit={rc}]`: o antes de um AT de comportamento novo tem de falhar"
    if classe == CONTINUA and rc != "0":
        return f"`{rel}` terminou em `[exit={rc}]`: `shall continue to` exige o antes verde"
    logs = [p for p in PATH_RE.findall(evid) if p.endswith((".log", ".txt")) and caminho_do_log(p, root, report_dir)]
    depois = next((p for p in logs if os.path.basename(p.replace("\\", "/")) == f"{at}.log"), logs[0] if logs else None)
    if depois is None:   # evidência só pela avaliação: o `AT-nnn.log` do disco, se existe (avaliador, ciclo 1, O1)
        depois = f"{REPORTS_DIR}/evidence/{feature}/{at}.log" if caminho_do_log(f"{REPORTS_DIR}/evidence/{feature}/{at}.log", root, report_dir) else None
    if depois:
        cmd_depois = (primeira_linha(caminho_do_log(depois, root, report_dir)) or "")[2:].strip()
        if rodado != cmd_depois:
            return f"`{rel}` roda `{rodado}`, não o mesmo comando de `{depois}` (`{cmd_depois}`)"
    return None


def check_antes(linhas_at, root, report_dir, feature, warnings):
    """F30 S2: o vermelho antes do verde dos AT `true` de uma tabela com a coluna `Antes`."""
    if not linhas_at:
        return []
    ats = ats_do_define(root, feature)
    if ats is None:
        warnings.append(f"sem `{FEATURES_DIR}/DEFINE_{feature}.md`: o vermelho antes do verde não foi conferido")
        return []
    violations = []
    for at, cell, evid in linhas_at:
        if at not in ats:
            warnings.append(f"{at} não está no DEFINE_{feature}.md: o vermelho antes do verde dele não foi conferido")
            continue
        problema = problema_antes(at, ats[at], cell, evid, root, report_dir, feature, warnings)
        if problema:
            violations.append((ANTES, f"{at}: {problema}"))
    return violations


def check(content, root, report_dir, feature):
    violations, warnings = [], []
    gate_kind = define_gate_kind(root, feature)
    header, achou_tabela, com_antes, sem_antes = None, False, [], False
    for raw in content.splitlines():
        line = raw.strip()
        if line.startswith("|") and ("Evid" in line) and ("Result" in line or "Status" in line or "Passou" in line):
            header = tabela_reconhecida(line)
            achou_tabela = achou_tabela or header is not None
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
            violations.append((EVIDENCIA, f"{m.group(1)}: `{result}` sem evidência válida — {why}"))
        if header["antes"] is None:
            sem_antes = True
        elif len(cells) >= header["antes"]:
            com_antes.append((m.group(1), cells[len(cells) - header["antes"]], evid))
    if not achou_tabela:
        violations.append((TABELA, "nenhuma tabela de critérios reconhecida (uma coluna Resultado, Status, Passou ou "
                                   "Result e uma coluna Evidência): sem ela, nenhum critério é conferido"))

    for verdict, scope in verdicts_in(strip_fences(content)):
        if verdict.replace(".", "") in ("NA", "PENDENTE"):
            continue  # declarações: quem confere é existencia_avaliacao()
        refs = [p for p in PATH_RE.findall(scope) if os.path.basename(p).startswith(f"AVALIACAO_{feature}_")]
        found = [c for p in refs
                 for c in (os.path.join(root, p), os.path.join(root, REVIEWS_DIR, os.path.basename(p)))
                 if os.path.isfile(c)]
        if not found:
            violations.append((EVIDENCIA, f"Veredito do avaliador `{verdict}` sem `AVALIACAO_{feature}_*.md` existente em "
                                          f"{REVIEWS_DIR}/ (no mesmo parágrafo do veredito)"))
        elif all(git_ignorado(root, c, warnings) for c in found):
            violations.append((EVIDENCIA, f"Veredito do avaliador `{verdict}`: `{os.path.basename(found[0])}` {IGNORADO_MSG}"))
    violations += existencia_avaliacao(content, root, feature, warnings)
    violations += [(MIGRATION, v) for v in check_migrations(content, root, report_dir, feature)]
    violations += check_lint(content, root, feature, warnings)
    violations += check_antes(com_antes, root, report_dir, feature, warnings)
    if sem_antes:
        warnings.append(SEM_COLUNA_ANTES)
    return violations, warnings


def conserto(classe, feature):
    if classe == TABELA:
        return "use a tabela do template: `| ID | Critério | Resultado | Evidência |`."
    if classe == AUSENTE:
        return (f"rode o avaliador e grave `{REVIEWS_DIR}/AVALIACAO_{feature}_<AAAAMMDD-HHMM>.md`, ou escreva a linha "
                "`avaliador: N.A. (<motivo>)` / `avaliador: PENDENTE (<motivo>)` no relatório.")
    if classe == DECLARACAO:
        return "escreva `avaliador: N.A. (<motivo>)` só com menos camadas que o limite; senão rode o avaliador ou use `PENDENTE (<motivo>)`."
    if classe == MIGRATION:
        return ("migration: aplique e leia de volta (.agents/skills/sdd-build/references/aplicar-migration.md) e registre "
                "a linha em `## Migrations aplicadas`.")
    if classe == LINT:
        return (f"rode o comando do slot sobre os arquivos da tarefa até sair 0 e grave `evidence/{feature}/LINT.log` "
                "(ou `TIPOS.log`): 1ª linha `$ <comando>`, a saída e, no fim, `[exit=0]`.")
    if classe == ANTES:
        return (f"rode o comando do AT antes do código e grave `evidence/{feature}/AT-nnn.antes.log` (vermelho; `shall "
                "continue to`: verde), citado na coluna `Antes`; gate fora de `test`/`cmd`: `N.A. (<motivo>)`.")
    return (f"produza `evidence/{feature}/AT-nnn.log` (1ª linha `$ cmd`, output verbatim), cite "
            f"`AVALIACAO_{feature}_<ts>.md`, ou `recibo: nome YYYY-MM-DD` (só gate manual-ux) — ou mantenha `false`.")


def imprimir_avisos(warnings):
    vistos, ambiente = [], []
    for w in warnings:
        if w in vistos:
            continue
        vistos.append(w)
        if w.startswith("PENDENTE: "):
            print(f"⚠️  {w[len('PENDENTE: '):]}")
        elif "não conferida" in w:
            ambiente.append(w)
        else:
            print(f"⚠️  {w}")
    if ambiente:
        print("⚠️  não conferido: " + "; ".join(ambiente))


def cli_pendente(paths):
    if not paths:
        print("uso: report-lint.py --pendente sdd/reports/BUILD_REPORT_{FEATURE}.md …", file=sys.stderr)
        print("RESULTADO: ERRO DE USO", file=sys.stderr)
        return 64
    achados = []
    for p in paths:
        try:
            texto = open(p, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print(f"🛑 não consegui ler {p}: {e}", file=sys.stderr)
            print("RESULTADO: ERRO DE USO", file=sys.stderr)
            return 64
        achados += [f"{p}:{linha}: PENDENTE ({motivo})" for tipo, motivo, linha in declaracoes(texto) if tipo == "PENDENTE"]
    if achados:
        for a in achados:
            print(a)
        print("RESULTADO: VERMELHO")
        print("→ a release não sai com avaliação pendente: rode o avaliador e troque a linha pelo veredito.")
        return 1
    print(f"✅ nenhuma avaliação PENDENTE em {len(paths)} relatório(s)")
    print("RESULTADO: VERDE")
    print("→ siga para o próximo passo.")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[1] == "--pendente":
        return cli_pendente(argv[2:])
    stdin = len(argv) == 3 and argv[1] == "--stdin"
    if not stdin and (len(argv) != 2 or argv[1].startswith("--")):
        print("uso: report-lint.py [--stdin] sdd/reports/BUILD_REPORT_{FEATURE}.md | --pendente <relatório…>", file=sys.stderr)
        return 64
    path = argv[-1]
    rm = REPORT_RE.match(os.path.basename(path))
    if not rm:
        print(f"🛑 {path}: o nome precisa ser BUILD_REPORT_{{FEATURE}}.md", file=sys.stderr)
        return 64
    try:
        # F16W2: o stdin em bytes, decodificado em UTF-8 (no Windows, sys.stdin leria em cp1252); o fim de linha como
        # na leitura do arquivo em modo texto
        content = (sys.stdin.buffer.read().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n") if stdin
                   else open(path, encoding="utf-8").read())
    except (OSError, UnicodeDecodeError) as e:
        print(f"🛑 não consegui ler {path}: {e}", file=sys.stderr)
        return 64
    # F16W2: sem os.popen, que no Windows passa pelo cmd.exe (não conhece /dev/null e a raiz caía no cwd)
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, stdin=subprocess.DEVNULL)
        root = r.stdout.decode("utf-8", "replace").strip() if r.returncode == 0 else ""
    except OSError:
        root = ""
    root = root or os.getcwd()
    report_dir = os.path.dirname(os.path.abspath(path))
    feature = rm.group(1)
    violations, warnings = check(content, root, report_dir, feature)
    imprimir_avisos(warnings)
    if violations:
        classes = []
        for classe, texto in violations:
            print(f"🛑 [{classe}] {texto}", file=sys.stderr)
            if classe not in classes:
                classes.append(classe)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        for classe in classes:
            print("→ " + conserto(classe, feature), file=sys.stderr)
        return 1
    print(f"✅ {path}: todo `true` tem evidência abrível e a avaliação está provada ou declarada")
    print("RESULTADO: VERDE")
    if any(w.startswith("PENDENTE: ") for w in warnings):
        print("→ o relatório pode ser commitado; rode o avaliador quando o build destravar e troque a linha pelo veredito.")
    else:
        print("→ o relatório pode ser commitado.")
    return 0


if __name__ == "__main__":
    # F16W2: no Windows, o stdout num pipe (o Git Bash do aluno) é cp1252 e o print troca \n por \r\n: o ✅ e o "ç"
    # quebrariam o script, e o bash que captura a saída veria um \r a mais. Saída em UTF-8 e \n, sempre.
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv))
