#!/usr/bin/env bash
# seguranca-varredura.sh — lê o catálogo da skill sdd-seguranca e procura, no repositório, as falhas de segurança
# que dá para achar por texto. Só lê: não usa rede, não executa nada do projeto, nunca imprime o trecho achado.
#
# Por que existe: as duas falhas mais caras de app feito com IA (chave secreta no código e tabela sem RLS) passam
# por qualquer revisão apressada; aqui elas param a publicação, e o resto vira aviso com a prova à mão.
# O catálogo (.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md) é a fonte única: este script é o
# único leitor dele, e serve também o bloco do AGENTS.md (init/sync), as regras do build e a lista do release.
#
# USO-INICIO
#   seguranca-varredura.sh [--raiz DIR] [--catalogo ARQ] [--base REF] [--saida ARQ]
#       varre os arquivos do repositório (rastreados e novos não ignorados, menos as pastas do SDD e dos agentes).
#       Bloqueia só o que a publicação acrescenta (diff da árvore contra --base; padrão origin/<project.default_branch>;
#       sem a base, tudo conta como novo). Achado em linha que já existia vira aviso "(já existia)".
#       0 NADA ACHADO · 1 AVISOS · 2 BLOQUEADO · 64 ERRO DE USO (opção, slot, catálogo ilegível, fora de git)
#   seguranca-varredura.sh --stack      a stack do projeto e de onde veio (slot security.stack ou detectada)
#   seguranca-varredura.sh --regras     as frases preventivas dos itens da stack (a sdd-build lê antes de construir)
#   seguranca-varredura.sh --checklist  a lista de conferência antes de publicar (os 5 de maior risco primeiro)
#   seguranca-varredura.sh --agents     só as linhas do bloco de segurança do AGENTS.md (o init/sync usa)
#       os 4 modos saem 0, ou 64 com a causa.
#   Dispensa de um achado: na linha dele, ou na de cima, `sdd-seguranca: aceito Snn — <motivo>` (motivo obrigatório).
#   Slots (sdd/config.yaml): security.stack (vazio = detectar; supabase, vercel, web, ou nenhuma) ·
#   security.max_warnings (vazio = 5): avisos na tela; a lista inteira vai para --saida.
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib.

set -u
# F16: o Python que roda vira python3 (no Windows, python ou py -3). Só builtins (o PATH pode não ter dirname); sem
# a biblioteca (projeto sincronizado antes dela, ou script copiado sozinho), vale a guarda de antes.
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }; fi

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! sdd_python_pronto; then
  echo "🛑 seguranca-varredura: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi lido.\n' >&2
  exit 64
fi

exec python3 -B - "$@" <<'PY'
import codecs, fnmatch, os, re, subprocess, sys

# Fim de linha sempre \n: no Windows o Python escreveria \r\n, e o bloco do AGENTS.md que o init monta com --agents nunca
# ficaria em dia (raio de impacto da F18/F20; o mesmo cuidado de sdd/bin/sdd-archive.py).
for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

CAMPOS = ["stack", "fase", "gravidade", "bloqueia", "agents", "gatilho", "padrao", "arquivos",
          "frase", "evitar", "at", "confira", "ref"]
DOMINIO = {
    "stack": {"todas", "supabase", "vercel", "web"},
    "fase": {"define", "design", "build", "release", "bancada"},
    "gravidade": {"alta", "media", "baixa"},
    "bloqueia": {"sim", "nao"},
    "agents": {"sim", "nao"},
}
GATILHOS = {"login", "rota-publica", "dado-de-terceiros", "upload", "ia", "banco", "sempre"}
REGRAS = {"regra:rls", "regra:definer"}
STACKS = ("supabase", "vercel", "web")
GRAV = {"alta": 0, "media": 1, "baixa": 2}
FASES = ("define", "design", "build", "release", "bancada")
FORA_PASTAS = (".agents/", ".claude/", ".cursor/", ".gemini/", ".codex/", ".kimi/", "sdd/", "node_modules/")
FORA_ARQ = {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}
MAX_BYTES = 1024 * 1024
CATALOGO_REL = ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"
PONTEIRO = ("- Antes de construir, rode `bash sdd/bin/seguranca-varredura.sh --regras` e siga as regras de "
            "segurança da stack deste projeto; a skill `sdd-seguranca` explica cada uma, tem a lista de conferência "
            "antes de publicar e o modo incidente (chave vazou, tabela ficou aberta).")
DISPENSA = re.compile(r"sdd-seguranca:\s*aceito\s+(S\d\d)\s*(?:—|-)\s*(.*)$")
CREATE = re.compile(r"(?i)\bcreate\s+(?:unlogged\s+)?table\s+(?:if\s+not\s+exists\s+)?([\w.\"]+)")
RLS = re.compile(r"(?i)\balter\s+table\s+(?:if\s+exists\s+)?(?:only\s+)?([\w.\"]+)\s+enable\s+row\s+level\s+security")
DEFINER = re.compile(r"(?i)\bsecurity\s+definer\b")
FUNCAO = re.compile(r"(?i)\bcreate\s+(?:or\s+replace\s+)?function\s+([\w.\"]+)")
# revisão do código, N2: o revoke vale para a função que ele nomeia (ou para todas do esquema), não para o arquivo
REVOKE_FN = re.compile(r"(?i)\brevoke\b[^;]*?\bfunction\s+([\w.\"]+)[^;]*\bfrom\b[^;]*\banon\b")
REVOKE_TODAS = re.compile(r"(?i)\brevoke\b[^;]*\ball\s+functions\b[^;]*\bfrom\b[^;]*\banon\b")
# Só `from anon` fecha: no Supabase o papel anônimo recebe execute por grant próprio, que `from public` não tira.


def fim(rc, palavra, seta, para=sys.stdout):
    print("RESULTADO: %s" % palavra, file=para)
    print("→ %s" % seta, file=para)
    sys.exit(rc)


def uso(msg, seta="rode com --help para ver o uso; nada foi lido nem gravado."):
    print("🛑 seguranca-varredura: %s" % msg, file=sys.stderr)
    fim(64, "ERRO DE USO", seta, sys.stderr)


# ── argumentos ─────────────────────────────────────────────────────────────
MODOS = ("--stack", "--regras", "--checklist", "--agents")
op = {"modo": None, "--raiz": None, "--catalogo": None, "--base": None, "--saida": None}
args = sys.argv[1:]
i = 0
while i < len(args):
    a = args[i]
    if a in MODOS:
        if op["modo"]:
            uso("dois modos na mesma chamada: %s e %s" % (op["modo"], a))
        op["modo"] = a
        i += 1
    elif a in ("--raiz", "--catalogo", "--base", "--saida"):
        if i + 1 >= len(args) or not args[i + 1]:
            uso("%s precisa de um valor" % a)
        op[a] = args[i + 1]
        i += 2
    else:
        uso("opção desconhecida: %s" % a)
if op["modo"] and (op["--base"] or op["--saida"]):
    uso("--base e --saida valem só para a varredura, não para %s" % op["modo"])


def git(raiz, *a):
    try:
        r = subprocess.run(["git", "-C", raiz, "-c", "core.quotepath=off", *a], capture_output=True)
    except OSError:
        return 127, b"", b""
    return r.returncode, r.stdout, r.stderr


if op["--raiz"]:
    RAIZ = os.path.abspath(op["--raiz"])
    if not os.path.isdir(RAIZ):
        uso("a pasta de --raiz não existe: %s" % op["--raiz"])
else:
    rc, out, _ = git(os.getcwd(), "rev-parse", "--show-toplevel")
    if rc != 0:
        uso("esta pasta não está num repositório git", "rode dentro do projeto (ou passe --raiz <pasta do projeto>).")
    RAIZ = out.decode("utf-8", "replace").strip()
EH_GIT = git(RAIZ, "rev-parse", "--is-inside-work-tree")[0] == 0
if not op["modo"] and not EH_GIT:
    uso("a varredura precisa de um repositório git em %s" % RAIZ,
        "rode dentro do projeto com git (a sdd-iniciar-repo põe o projeto no git).")


# ── sdd/config.yaml: mapa de 1 nível (a mesma leitura do report-lint.py) ───
def ler_mapa(root, mapa):
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


SEC = ler_mapa(RAIZ, "security")
PROJ = ler_mapa(RAIZ, "project")
LAYERS = ler_mapa(RAIZ, "layers")


# ── catálogo: uma gramática, um leitor ─────────────────────────────────────
def ilegivel(caminho, n, motivo):
    uso("catálogo ilegível: %s:%d — %s" % (caminho, n, motivo),
        "o catálogo vem do pacote: apague .agents/skills/sdd-seguranca e rode o init de novo (o doctor aponta a skill velha).")


def ler_catalogo(caminho):
    try:
        linhas = open(caminho, encoding="utf-8").read().splitlines()
    except (OSError, UnicodeDecodeError):
        uso("catálogo ausente ou ilegível: %s" % caminho,
            "instale a skill sdd-seguranca (o init do pacote copia) ou passe --catalogo <arquivo>.")
    itens, atual, nas_fichas = [], None, False

    def fecha(f):
        if f is None:
            return
        if len(f["c"]) != len(CAMPOS):
            ilegivel(caminho, f["n"], "%s tem %d de %d campos (falta `%s`)" % (f["id"], len(f["c"]), len(CAMPOS), CAMPOS[len(f["c"])]))
        itens.append(f)

    for n, ln in enumerate(linhas, 1):
        if ln.startswith("## "):
            fecha(atual)
            atual = None
            nas_fichas = ln.strip() == "## Itens"
            continue
        if not nas_fichas:
            if re.match(r"^###\s+S\d", ln):
                ilegivel(caminho, n, "ficha fora da seção `## Itens`")
            continue
        if not ln.strip():
            continue
        m = re.match(r"^### (S\d\d) — (\S.*)$", ln)
        if m:
            fecha(atual)
            atual = {"id": m.group(1), "falha": m.group(2).strip(), "n": n, "c": {}}
            continue
        m = re.match(r"^- ([a-z]+): (\S.*)$", ln)
        if m and atual is not None:
            esperado = CAMPOS[len(atual["c"])] if len(atual["c"]) < len(CAMPOS) else None
            if m.group(1) != esperado:
                ilegivel(caminho, n, "campo `%s` fora da ordem em %s (esperado `%s`)" % (m.group(1), atual["id"], esperado or "fim da ficha"))
            atual["c"][m.group(1)] = m.group(2).strip()
            continue
        ilegivel(caminho, n, "linha fora da gramática da ficha (título `### Snn — <falha>` e 13 linhas `- campo: valor`)")
    fecha(atual)

    vistos = [f["id"] for f in itens]
    if not itens:
        ilegivel(caminho, len(linhas) or 1, "nenhuma ficha em `## Itens`")
    if vistos != ["S%02d" % k for k in range(1, len(itens) + 1)]:
        ilegivel(caminho, itens[0]["n"], "ids fora de sequência: %s" % ", ".join(vistos))
    for f in itens:
        c = f["c"]
        for campo, dom in DOMINIO.items():
            if c[campo] not in dom:
                ilegivel(caminho, f["n"], "%s: `%s` = `%s` (vale %s)" % (f["id"], campo, c[campo], ", ".join(sorted(dom))))
        gat = [g.strip() for g in c["gatilho"].split(",") if g.strip()]
        if not gat or any(g not in GATILHOS for g in gat):
            ilegivel(caminho, f["n"], "%s: gatilho `%s` fora da lista" % (f["id"], c["gatilho"]))
        f["gatilhos"] = gat
        p = c["padrao"]
        f["re"] = None
        if p.startswith("re:"):
            m = re.match(r"^re:`(.+)`$", p)
            if not m:
                ilegivel(caminho, f["n"], "%s: padrao `re:` sem a expressão entre crases" % f["id"])
            try:
                f["re"] = re.compile(m.group(1))
            except re.error as e:
                ilegivel(caminho, f["n"], "%s: expressão inválida (%s)" % (f["id"], e))
        elif p not in REGRAS and p != "só à mão":
            ilegivel(caminho, f["n"], "%s: padrao `%s` (vale re:`…`, regra:rls, regra:definer ou só à mão)" % (f["id"], p))
        if c["bloqueia"] == "sim" and p == "só à mão":
            ilegivel(caminho, f["n"], "%s: item que bloqueia precisa de padrão" % f["id"])
        f["globs"] = [g.strip() for g in c["arquivos"].split(",") if g.strip()]
        if not f["globs"]:
            ilegivel(caminho, f["n"], "%s: `arquivos` vazio" % f["id"])
    return itens


CATALOGO = op["--catalogo"] or os.path.join(RAIZ, CATALOGO_REL)
ITENS = ler_catalogo(CATALOGO)


# ── arquivos do projeto ────────────────────────────────────────────────────
def lista_arquivos():
    if not EH_GIT:
        return []
    rc, out, err = git(RAIZ, "ls-files", "-co", "--exclude-standard", "-z")
    if rc != 0:
        uso("o git não listou os arquivos de %s (%s)" % (RAIZ, err.decode("utf-8", "replace").strip()[:200]))
    vistos, saida = set(), []
    for p in out.decode("utf-8", "replace").split("\0"):
        if not p or p in vistos:
            continue
        vistos.add(p)
        if p in FORA_ARQ or p.startswith(FORA_PASTAS) or not os.path.isfile(os.path.join(RAIZ, p)):
            continue
        saida.append(p)
    return sorted(saida)


ARQUIVOS = lista_arquivos()


# ── stack ──────────────────────────────────────────────────────────────────
def descobre_stack():
    slot = (SEC.get("stack") or "").strip()
    if slot:
        vals = [v.strip().lower() for v in slot.split(",") if v.strip()]
        if vals == ["nenhuma"]:
            return [], "slot security.stack"
        ruins = [v for v in vals if v not in STACKS]
        if ruins:
            uso("security.stack em sdd/config.yaml tem valor desconhecido: %s" % ", ".join(ruins),
                "use supabase, vercel e web (separados por vírgula), nenhuma, ou deixe vazio para detectar.")
        return [s for s in STACKS if s in vals], "slot security.stack"
    pkg = ""
    try:
        pkg = open(os.path.join(RAIZ, "package.json"), encoding="utf-8", errors="replace").read()
    except OSError:
        pass
    achou = []
    if os.path.isdir(os.path.join(RAIZ, "supabase")) or '"@supabase/' in pkg:
        achou.append("supabase")
    if os.path.isfile(os.path.join(RAIZ, "vercel.json")) or os.path.isdir(os.path.join(RAIZ, ".vercel")) or '"vercel"' in pkg:
        achou.append("vercel")
    if pkg or any(p.lower().endswith((".html", ".htm")) for p in ARQUIVOS):
        achou.append("web")
    return achou, "detectada"


STACK, ORIGEM = descobre_stack()
ATIVOS = [f for f in ITENS if f["c"]["stack"] == "todas" or f["c"]["stack"] in STACK]
TXT_STACK = "%s (%s)" % (", ".join(STACK) if STACK else "nenhuma", ORIGEM)

# ── modos de leitura do catálogo ───────────────────────────────────────────
if op["modo"] == "--stack":
    print("stack: %s" % TXT_STACK)
    fim(0, "OK", "os itens de outras stacks não disparam; para mudar, preencha security.stack em sdd/config.yaml.")
if op["modo"] == "--agents":
    for f in [f for f in ATIVOS if f["c"]["agents"] == "sim"][:5]:
        print("- %s" % f["c"]["frase"])
    print(PONTEIRO)
    sys.exit(0)
if op["modo"] == "--regras":
    print("Regras de segurança da stack deste projeto — stack: %s" % TXT_STACK)
    for f in sorted(ATIVOS, key=lambda f: (FASES.index(f["c"]["fase"]), f["id"])):
        print("- %s %s: %s" % (f["id"], f["falha"], f["c"]["frase"]))
    fim(0, "OK", "siga estas regras ao escrever o código; item aplicado no Define tem AT próprio no Verify Gate.")
if op["modo"] == "--checklist":
    lista = [f for f in ATIVOS if f["c"]["fase"] != "bancada"]
    lista.sort(key=lambda f: (0 if f["c"]["agents"] == "sim" else 1, GRAV[f["c"]["gravidade"]], f["id"]))
    print("Conferência antes de publicar — stack: %s · %d item(ns), os de maior risco primeiro" % (TXT_STACK, len(lista)))
    for k, f in enumerate(lista, 1):
        print("%d. [%s] %s — confira: %s" % (k, f["id"], f["falha"], f["c"]["confira"]))
    fim(0, "OK", "marque cada item contra o diff e o app publicado; o que não der para conferir vira pergunta, nunca ✅.")


# ── varredura ──────────────────────────────────────────────────────────────
def base_e_novas():
    """(ref, existe, {arquivo: set(linhas acrescentadas)}). Sem a base, None no lugar do mapa: tudo é novo."""
    ref = op["--base"]
    if not ref:
        ref = "origin/" + ((PROJ.get("default_branch") or "").strip() or "main")
    if git(RAIZ, "rev-parse", "--verify", "--quiet", ref + "^{commit}")[0] != 0:
        return ref, False, None
    # --relative: com --raiz numa subpasta, os caminhos do diff ficam relativos a ela, como os do ls-files (R3).
    rc, out, err = git(RAIZ, "diff", "--no-color", "--no-ext-diff", "-U0", "--no-renames", "--relative",
                       "--src-prefix=a/", "--dst-prefix=b/", ref, "--")
    if rc != 0:
        uso("o git não comparou com %s (%s)" % (ref, err.decode("utf-8", "replace").strip()[:200]))
    novas, atual, cabecalho = {}, None, False
    for ln in out.decode("utf-8", "replace").splitlines():
        # O `+++` só é cabeçalho entre o `diff --git` e o 1º `@@`: dentro do hunk, "+++ x" é uma linha que começa
        # com "++" (R4). O git põe um TAB no fim do nome com espaço (R2) e aspas no nome com caractere especial.
        if ln.startswith("diff --git "):
            cabecalho, atual = True, None
            continue
        if cabecalho and ln.startswith("+++ "):
            alvo = ln[4:]
            if alvo.endswith("\t"):
                alvo = alvo[:-1]
            if len(alvo) >= 2 and alvo[0] == alvo[-1] == '"':
                alvo = codecs.escape_decode(alvo[1:-1].encode("utf-8"))[0].decode("utf-8", "replace")
            atual = alvo[2:] if alvo.startswith("b/") else None
            if atual is not None:
                novas.setdefault(atual, set())
            continue
        m = re.match(r"^@@ -\S+ \+(\d+)(?:,(\d+))? @@", ln)
        if m:
            cabecalho = False
        if m and atual is not None:
            ini, qtd = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
            novas[atual].update(range(ini, ini + qtd))
    rc, out, _ = git(RAIZ, "ls-files", "--others", "--exclude-standard", "-z")
    for p in out.decode("utf-8", "replace").split("\0"):
        if p:
            novas[p] = "tudo"
    return ref, True, novas


def sem_comentarios_sql(t):
    """O texto com `-- …` e `/* … */` trocados por espaços, mantendo as quebras de linha (R1, N1)."""
    def branco(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    return re.sub(r"/\*.*?\*/|--[^\n]*", branco, t, flags=re.S)


def linha_de(t, pos):
    return t.count("\n", 0, pos) + 1


def nome_funcao(bruto):
    n = bruto.replace('"', "").lower()
    return n[len("public."):] if n.startswith("public.") else n


def casa(p, globs):
    nome = p.rsplit("/", 1)[-1]
    return any(g == "*" or fnmatch.fnmatch(p, g) or fnmatch.fnmatch(nome, g) for g in globs)


def nome_tabela(bruto):
    n = bruto.replace('"', "").lower()
    if n.startswith("public."):
        n = n[len("public."):]
    return None if "." in n else n


def comentado(linha, col, sql):
    """O achado está depois de um marcador de comentário na mesma linha (`https://` não conta)."""
    antes = linha[:col]
    if sql:
        return "--" in antes
    return bool(re.search(r"(^|\s)(//|#|<!--)", antes)) or antes.lstrip().startswith(("*", "/*"))


ref, base_ok, NOVAS = base_e_novas()
textos, pulados = {}, []
for p in ARQUIVOS:
    caminho = os.path.join(RAIZ, p)
    try:
        if os.path.getsize(caminho) > MAX_BYTES:
            pulados.append((p, "maior que 1 MB"))
            continue
        dado = open(caminho, "rb").read()
    except OSError:
        pulados.append((p, "não deu para ler"))
        continue
    if b"\0" in dado[:8192]:
        pulados.append((p, "binário"))
        continue
    textos[p] = dado.decode("utf-8", "replace")

achados = []   # (item, arquivo, linha)
sql_globs = [g for g in re.split(r"[,\s]+", (LAYERS.get("sql") or "")) if g]
for f in ATIVOS:
    padrao = f["c"]["padrao"]
    if f["re"] is not None:
        for p, t in textos.items():
            if not casa(p, f["globs"]):
                continue
            for n, ln in enumerate(t.split("\n"), 1):
                m = f["re"].search(ln)
                if m and not (f["id"] != "S11" and comentado(ln, m.start(), p.endswith(".sql"))):
                    achados.append((f, p, n))
    elif padrao in REGRAS:
        migr = {p: sem_comentarios_sql(t) for p, t in textos.items()
                if p.endswith(".sql") and (casa(p, f["globs"]) or (sql_globs and casa(p, sql_globs)))}
        if padrao == "regra:rls":
            com_rls = {nome_tabela(m.group(1)) for t in migr.values() for m in RLS.finditer(t)} - {None}
            for p, t in migr.items():
                for m in CREATE.finditer(t):
                    nm = nome_tabela(m.group(1))
                    if nm and nm not in com_rls:
                        achados.append((f, p, linha_de(t, m.start())))
        else:
            todas = any(REVOKE_TODAS.search(t) for t in migr.values())
            revogadas = {nome_funcao(m.group(1)) for t in migr.values() for m in REVOKE_FN.finditer(t)}
            for p, t in migr.items():
                funcoes = list(FUNCAO.finditer(t))
                for m in DEFINER.finditer(t):
                    antes = [fn for fn in funcoes if fn.start() < m.start()]
                    nome = nome_funcao(antes[-1].group(1)) if antes else None
                    if todas or (nome is not None and nome in revogadas):
                        continue
                    achados.append((f, p, linha_de(t, m.start())))


SEGREDO_RES = [f["re"] for f in ITENS if f["c"]["bloqueia"] == "sim" and f["re"] is not None]


def limpa_motivo(bruto):
    """O motivo termina no fim do comentário e nunca carrega um segredo (revisão do DESIGN, R4)."""
    m = re.split(r"\*/|-->", bruto, 1)[0]
    for r in SEGREDO_RES:
        m = r.sub("[…]", m)
    m = m.strip()
    return m if len(m) <= 160 else m[:157] + "…"


def nova(p, n):
    if NOVAS is None:
        return True
    linhas = NOVAS.get(p)
    return linhas == "tudo" or (bool(linhas) and n in linhas)


bloqueios, avisos, aceitos, dispensas_ruins = [], [], [], []
for f, p, n in achados:
    linhas = textos[p].split("\n")
    # A marca do próprio item, na linha do achado ou na de cima; marca de outro item não esconde a dele (R5).
    marcas = [m for k in (n, n - 1) if 1 <= k <= len(linhas)
              for m in [DISPENSA.search(linhas[k - 1])] if m]
    do_item = [m for m in marcas if m.group(1) == f["id"]]
    if do_item:
        motivo = limpa_motivo(do_item[0].group(2))
        if len(re.sub(r"\s", "", motivo)) >= 3:
            aceitos.append((f, p, n, motivo))
            continue
    if marcas:
        dispensas_ruins.append((f, p, n))
    e_nova = nova(p, n)
    if f["c"]["bloqueia"] == "sim" and e_nova:
        bloqueios.append((f, p, n))
    else:
        avisos.append((f, p, n, e_nova))

try:
    teto = int((SEC.get("max_warnings") or "5").strip())
    teto_ruim = teto < 1
except ValueError:
    teto, teto_ruim = 5, True
if teto_ruim:
    teto = 5

bloqueios.sort(key=lambda a: (a[0]["id"], a[1], a[2]))
avisos.sort(key=lambda a: (GRAV[a[0]["c"]["gravidade"]], 0 if a[3] else 1, a[0]["id"], a[1], a[2]))


def linha_achado(sim, f, p, n, extra=""):
    return "%s %s %s %s:%d — %s%s" % (sim, f["id"], f["c"]["gravidade"], p, n, f["falha"], extra)


saida = []
cab = "▶ seguranca-varredura — stack: %s · base: %s · %d arquivo(s) varrido(s), %d pulado(s)" % (
    TXT_STACK, ref, len(textos), len(pulados))
saida.append(cab)
if not base_ok:
    saida.append("⚠️ base %s não existe: tudo conta como novo (sem remoto ou sem a branch padrão)" % ref)
if teto_ruim:
    saida.append("⚠️ security.max_warnings inválido em sdd/config.yaml (%s): usando 5" % SEC.get("max_warnings"))
print("\n".join(saida))
completo = list(saida)
na_tela, no_arquivo = set(), set()


def mostra(texto_linha, f, tela):
    """A linha do achado; a prova à mão vai uma vez por item, na tela e no arquivo."""
    c = "   confira à mão: %s" % f["c"]["confira"]
    completo.append(texto_linha)
    if f["id"] not in no_arquivo:
        completo.append(c)
        no_arquivo.add(f["id"])
    if tela:
        print(texto_linha)
        if f["id"] not in na_tela:
            print(c)
            na_tela.add(f["id"])


for f, p, n in bloqueios:
    mostra(linha_achado("🛑", f, p, n, " (bloqueia: novo nesta publicação)"), f, True)
for k, (f, p, n, e_nova) in enumerate(avisos):
    mostra(linha_achado("⚠️", f, p, n, "" if e_nova else " (já existia)"), f, k < teto)
if len(avisos) > teto:
    resto = len(avisos) - teto
    if op["--saida"]:
        print("… e mais %d aviso(s): lista inteira em %s" % (resto, op["--saida"]))
    else:
        print("… e mais %d aviso(s): rode com --saida <arquivo> para ver todos" % resto)
for f, p, n in dispensas_ruins:
    t = "⚠️ dispensa sem motivo (ou de outro item) não vale: %s:%d (%s)" % (p, n, f["id"])
    print(t)
    completo.append(t)
for f, p, n, motivo in aceitos:
    t = "✔ aceito %s %s:%d — %s" % (f["id"], p, n, motivo)
    print(t)
    completo.append(t)
for p, motivo in pulados:
    completo.append("· pulado %s (%s)" % (p, motivo))

if bloqueios:
    rc, palavra, seta = 2, "BLOQUEADO", ("tire o segredo do código (se era real, ele vazou: troque-o) ou ligue a RLS na tabela, "
                                         "e rode de novo; achado falso leva a dispensa na linha, com motivo.")
elif avisos:
    rc, palavra, seta = 1, "AVISOS", ("confira cada aviso pela prova à mão; o que for falso positivo leva a dispensa na linha, "
                                       "com motivo.")
else:
    rc, palavra, seta = 0, "NADA ACHADO", ("siga; a varredura só acha o que dá para ver por texto: a conferência à mão "
                                            "(--checklist) continua.")
completo.append("RESULTADO: %s" % palavra)
if op["--saida"]:
    try:
        d = os.path.dirname(os.path.abspath(op["--saida"]))
        os.makedirs(d, exist_ok=True)
        with open(op["--saida"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(completo) + "\n")
    except OSError as e:
        print("⚠️ não deu para gravar --saida %s (%s)" % (op["--saida"], e))
fim(rc, palavra, seta)
PY
