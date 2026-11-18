#!/usr/bin/env bash
# desempenho-varredura.sh — lê o catálogo da skill sdd-desempenho-banco e procura, no repositório, o que deixa o banco
# lento e dá para achar por texto (política que chama auth.uid() por linha, chave estrangeira sem índice, lista sem
# limite…). Só lê: não usa rede, não executa nada do projeto. Nunca bloqueia: desempenho degrada, não vaza.
#
# Por que existe: a lentidão nasce na migration e na consulta, e só aparece quando a tabela cresce. Aqui ela vira
# aviso na publicação, com a prova à mão, enquanto corrigir ainda custa uma linha.
# O catálogo (.agents/skills/sdd-desempenho-banco/references/CATALOGO_DESEMPENHO.md) é a fonte única: este script é o
# único leitor dele. A stack vem da varredura de segurança (seguranca-varredura.sh --stack): uma detecção só.
#
# USO-INICIO
#   desempenho-varredura.sh [--raiz DIR] [--catalogo ARQ] [--base REF] [--saida ARQ] [--tudo]
#       varre os arquivos do repositório (rastreados e novos não ignorados, menos as pastas do SDD e dos agentes).
#       Mostra só o que a mudança traz: achado que a base (--base; padrão origin/<project.default_branch>) já tinha,
#       no mesmo arquivo e no mesmo texto de linha, vira uma linha de contagem (--tudo lista); sem a base, tudo é novo.
#       0 NADA ACHADO, NADA NOVO ou SEM BANCO · 1 AVISOS (CONCERNS na release) · 64 ERRO DE USO — nunca 2
#   Dispensa de um achado: na linha dele, ou numa linha só de comentário logo acima, `sdd-desempenho-banco: aceito Pnn —
#   <motivo>` (motivo com 3+ caracteres); no fim de uma linha de código, vale só para aquela linha.
#   Projeto sem banco (sem Supabase na stack e sem arquivo .sql fora das pastas do SDD): SEM BANCO, nada mais.
#   Na tela, os 5 avisos mais graves; a lista inteira vai para --saida.
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib.

set -u
# F16: o Python que roda vira python3 (no Windows, python ou py -3). Só builtins (o PATH pode não ter dirname); sem
# a biblioteca (projeto sincronizado antes dela, ou script copiado sozinho), vale a guarda de antes.
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi   # F16W2: sem a biblioteca, ao menos o UTF-8

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! sdd_python_pronto; then
  echo "🛑 desempenho-varredura: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi lido.\n' >&2
  exit 64
fi

# LM-029: o Python chama a varredura de segurança pelo mesmo bash que roda este script (no Windows, `bash` sem
# caminho cairia no do WSL).
export SDD_DESEMPENHO_BASH="${BASH:-bash}" SDD_DESEMPENHO_BIN="${_sdd_bin}"
exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import codecs, fnmatch, os, re, subprocess, sys

# Fim de linha sempre \n e saída em UTF-8, também no Windows (cp1252 e "\r\n" no pipe do Git Bash).
for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

def _inesperado(tipo, valor, _tb):
    """Erro que ninguém previu sai 64 com a causa, nunca 1 (que é AVISOS) nem 2 (revisão do DESIGN, N2)."""
    print("🛑 desempenho-varredura: erro inesperado (%s: %s)" % (tipo.__name__, str(valor)[:160]), file=sys.stderr)
    print("RESULTADO: ERRO DE USO", file=sys.stderr)
    print("→ rode de novo; se repetir, guarde esta mensagem; nada foi gravado.", file=sys.stderr)
    os._exit(64)


sys.excepthook = _inesperado
CAMPOS = ["stack", "fase", "gravidade", "gatilho", "padrao", "arquivos", "frase", "evitar", "at", "confira", "ref"]
DOMINIO = {
    "stack": {"todas", "supabase"},
    "fase": {"define", "design", "build", "release"},
    "gravidade": {"alta", "media", "baixa"},
}
GATILHOS = {"banco", "lista", "busca", "conexao", "lote"}
REGRAS = {"regra:initplan", "regra:politica-sem-indice", "regra:fk-sem-indice", "regra:sem-pk", "regra:permissivas",
          "regra:sem-papel", "regra:indice-duplicado", "regra:lista-sem-limite", "regra:busca"}
GRAV = {"alta": 0, "media": 1, "baixa": 2}
# As mesmas exclusões da varredura de segurança: as pastas do SDD e dos agentes citam os próprios padrões.
FORA_PASTAS = (".agents/", ".claude/", ".cursor/", ".gemini/", ".codex/", ".kimi/", "sdd/")
FORA_ARQ = {"AGENTS.md", "CLAUDE.md", "GEMINI.md"}
NUNCA = ("node_modules/",)
MAX_BYTES = 1024 * 1024
TETO = 5
CATALOGO_REL = ".agents/skills/sdd-desempenho-banco/references/CATALOGO_DESEMPENHO.md"
CAT_SEG_REL = ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"
DISPENSA = re.compile(r"sdd-desempenho-banco:\s*aceito\s+(P\d\d)\s*(?:—|-)\s*(.*)$")


def fim(rc, palavra, seta, para=sys.stdout):
    print("RESULTADO: %s" % palavra, file=para)
    print("→ %s" % seta, file=para)
    sys.exit(rc)


def uso(msg, seta="rode com --help para ver o uso; nada foi lido nem gravado."):
    print("🛑 desempenho-varredura: %s" % msg, file=sys.stderr)
    fim(64, "ERRO DE USO", seta, sys.stderr)


# ── argumentos ─────────────────────────────────────────────────────────────
op = {"--raiz": None, "--catalogo": None, "--base": None, "--saida": None, "--tudo": False}
args = sys.argv[1:]
i = 0
while i < len(args):
    a = args[i]
    if a == "--tudo":
        op["--tudo"] = True
        i += 1
    elif a in ("--raiz", "--catalogo", "--base", "--saida"):
        if i + 1 >= len(args) or not args[i + 1]:
            uso("%s precisa de um valor" % a)
        op[a] = args[i + 1]
        i += 2
    else:
        uso("opção desconhecida: %s" % a)


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
if git(RAIZ, "rev-parse", "--is-inside-work-tree")[0] != 0:
    uso("a varredura precisa de um repositório git em %s" % RAIZ,
        "rode dentro do projeto com git (a sdd-iniciar-repo põe o projeto no git).")


# ── sdd/config.yaml: mapa de 1 nível (a mesma leitura da varredura de segurança) ───
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


PROJ = ler_mapa(RAIZ, "project")


# ── catálogo: uma gramática, um leitor ─────────────────────────────────────
def ilegivel(caminho, n, motivo):
    uso("catálogo ilegível: %s:%d — %s" % (caminho, n, motivo),
        "o catálogo vem do pacote: rode o upgrade do pacote (bash <pacote>/bin/sdd-open.sh upgrade).")


def ler_catalogo(caminho):
    try:
        linhas = open(caminho, encoding="utf-8").read().splitlines()
    except (OSError, UnicodeDecodeError):
        uso("catálogo ausente ou ilegível: %s" % caminho,
            "instale a skill sdd-desempenho-banco (o init do pacote copia) ou passe --catalogo <arquivo>.")
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
            if re.match(r"^###\s+P\d", ln):
                ilegivel(caminho, n, "ficha fora da seção `## Itens`")
            continue
        if not ln.strip():
            continue
        m = re.match(r"^### (P\d\d) — (\S.*)$", ln)
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
        ilegivel(caminho, n, "linha fora da gramática da ficha (título `### Pnn — <falha>` e 11 linhas `- campo: valor`)")
    fecha(atual)

    vistos = [f["id"] for f in itens]
    if not itens:
        ilegivel(caminho, len(linhas) or 1, "nenhuma ficha em `## Itens`")
    if vistos != ["P%02d" % k for k in range(1, len(itens) + 1)]:
        ilegivel(caminho, itens[0]["n"], "ids fora de sequência: %s" % ", ".join(vistos))
    for f in itens:
        c = f["c"]
        for campo, dom in DOMINIO.items():
            if c[campo] not in dom:
                ilegivel(caminho, f["n"], "%s: `%s` = `%s` (vale %s)" % (f["id"], campo, c[campo], ", ".join(sorted(dom))))
        gat = [g.strip() for g in c["gatilho"].split(",") if g.strip()]
        if not gat or any(g not in GATILHOS for g in gat):
            ilegivel(caminho, f["n"], "%s: gatilho `%s` fora da lista" % (f["id"], c["gatilho"]))
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
            ilegivel(caminho, f["n"], "%s: padrao `%s` (vale re:`…`, uma regra:<nome> conhecida ou só à mão)" % (f["id"], p))
        f["globs"] = [g.strip() for g in c["arquivos"].split(",") if g.strip()]
        if not f["globs"]:
            ilegivel(caminho, f["n"], "%s: `arquivos` vazio" % f["id"])
    return itens


CATALOGO = op["--catalogo"] or os.path.join(RAIZ, CATALOGO_REL)
ITENS = ler_catalogo(CATALOGO)


# ── stack: a da varredura de segurança, nunca uma 2ª detecção ──────────────
def stack_da_seguranca():
    bin_ = os.environ.get("SDD_DESEMPENHO_BIN") or "."
    script = os.path.join(bin_, "seguranca-varredura.sh")
    if not os.path.isfile(script):
        uso("não achei a varredura de segurança ao lado deste script (%s): ela diz a stack do projeto" % script,
            "rode o upgrade do pacote; os dois scripts vêm juntos em sdd/bin/.")
    cmd = [os.environ.get("SDD_DESEMPENHO_BASH") or "bash", script, "--stack", "--raiz", RAIZ]
    # O catálogo da segurança do projeto; sem ele (pacote rodando sobre outra pasta), o do pacote deste script.
    no_pacote = os.path.normpath(os.path.join(os.path.abspath(bin_), "..", "..", CAT_SEG_REL))
    if not os.path.isfile(os.path.join(RAIZ, CAT_SEG_REL)) and os.path.isfile(no_pacote):
        cmd += ["--catalogo", no_pacote]
    try:
        r = subprocess.run(cmd, capture_output=True)
    except OSError as e:
        uso("não consegui rodar a varredura de segurança para saber a stack (%s)" % e)
    saida = r.stdout.decode("utf-8", "replace")
    m = re.search(r"^stack: (.*) \((detectada|slot security\.stack)\)\s*$", saida, re.M)
    if r.returncode != 0 or not m:
        erro = [ln for ln in r.stderr.decode("utf-8", "replace").splitlines() if ln.strip()]
        causa = erro[0].replace("🛑 seguranca-varredura: ", "") if erro else "saída sem a linha da stack"
        uso("a detecção de stack da varredura de segurança falhou: %s" % causa,
            (erro[-1][2:].strip() if erro and erro[-1].startswith("→") else "rode bash sdd/bin/seguranca-varredura.sh --stack e corrija o que ele disser."))
    lista = [] if m.group(1).strip() == "nenhuma" else [s.strip() for s in m.group(1).split(",") if s.strip()]
    return lista, "%s (%s)" % (m.group(1).strip(), m.group(2))


STACK, TXT_STACK = stack_da_seguranca()
ATIVOS = [f for f in ITENS if f["c"]["stack"] == "todas" or f["c"]["stack"] in STACK]
POR_ID = {f["id"]: f for f in ATIVOS}


# ── arquivos do projeto ────────────────────────────────────────────────────
def fora_do_codigo(p):
    return p in FORA_ARQ or p.startswith(FORA_PASTAS) or p.startswith(NUNCA)


def lista_arquivos():
    rc, out, err = git(RAIZ, "ls-files", "-co", "--exclude-standard", "-z")
    if rc != 0:
        uso("o git não listou os arquivos de %s (%s)" % (RAIZ, err.decode("utf-8", "replace").strip()[:200]))
    vistos, saida = set(), []
    for p in out.decode("utf-8", "replace").split("\0"):
        if not p or p in vistos:
            continue
        vistos.add(p)
        if fora_do_codigo(p) or not os.path.isfile(os.path.join(RAIZ, p)):
            continue
        saida.append(p)
    return sorted(saida)


ARQUIVOS = lista_arquivos()
if "supabase" not in STACK and not any(p.lower().endswith(".sql") for p in ARQUIVOS):
    seta = "nada a conferir: o projeto não tem banco (sem Supabase na stack e sem arquivo .sql)."
    if op["--saida"]:   # a release aponta --saida: a evidência existe mesmo sem banco (avaliador, ciclo 2, c)
        try:
            os.makedirs(os.path.dirname(os.path.abspath(op["--saida"])), exist_ok=True)
            with open(op["--saida"], "w", encoding="utf-8", newline="\n") as fh:
                fh.write("RESULTADO: SEM BANCO\n→ %s\n" % seta)
        except OSError:
            pass
    fim(0, "SEM BANCO", seta)


# ── base: o mesmo projeto como estava em origin/<branch padrão>, para separar o novo do que já existia ───
def base_textos():
    """(ref, existe, {arquivo: texto}) da base. Sem a base, None: tudo é novo. Um achado é novo quando a base não
    tinha o mesmo achado (item, arquivo e texto da linha): assim, um índice apagado por uma migration nova faz o
    aviso na linha antiga da chave contar como novo (revisão do DESIGN, R1)."""
    ref = op["--base"]
    if not ref:
        ref = "origin/" + ((PROJ.get("default_branch") or "").strip() or "main")
    if git(RAIZ, "rev-parse", "--verify", "--quiet", ref + "^{commit}")[0] != 0:
        return ref, False, None
    rc, out, err = git(RAIZ, "ls-tree", "-r", "-z", "--name-only", "--full-tree", ref)
    if rc != 0:
        uso("o git não listou %s (%s)" % (ref, err.decode("utf-8", "replace").strip()[:200]))
    prefixo = git(RAIZ, "rev-parse", "--show-prefix")[1].decode("utf-8", "replace").strip()
    nomes = []
    for q in out.decode("utf-8", "replace").split("\0"):
        if not q or (prefixo and not q.startswith(prefixo)):
            continue
        rel = q[len(prefixo):]
        if not fora_do_codigo(rel) and "\n" not in q:
            nomes.append((rel, q))
    base = {}
    if not nomes:
        return ref, True, base
    pedido = "".join("%s:%s\n" % (ref, q) for _rel, q in nomes).encode("utf-8")
    try:
        r = subprocess.run(["git", "-C", RAIZ, "cat-file", "--batch"], input=pedido, capture_output=True)
    except OSError as e:
        uso("o git não leu a base %s (%s)" % (ref, e))
    dado, k = r.stdout, 0
    for rel, _q in nomes:
        fim_cab = dado.find(b"\n", k)
        if fim_cab < 0:
            break
        cab = dado[k:fim_cab].split()
        k = fim_cab + 1
        if len(cab) < 3 or cab[-1] == b"missing":
            continue
        tam = int(cab[2])
        corpo = dado[k:k + tam]
        k += tam + 1
        if tam <= MAX_BYTES and b"\0" not in corpo[:8192]:
            base[rel] = corpo.decode("utf-8", "replace").replace("\r\n", "\n")
    return ref, True, base


# ── leitura dos arquivos ───────────────────────────────────────────────────
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
    textos[p] = dado.decode("utf-8", "replace").replace("\r\n", "\n")


def casa(p, globs):
    nome = p.rsplit("/", 1)[-1]
    return any(g == "*" or fnmatch.fnmatch(p, g) or fnmatch.fnmatch(nome, g) for g in globs)


def linha_de(t, pos):
    return t.count("\n", 0, pos) + 1


def comentado(linha, col, sql):
    """A linha COMEÇA por um marcador de comentário que ainda está aberto no achado (a regra da segurança)."""
    antes = linha[:col].lstrip()
    if sql:
        return antes.startswith("--")
    if antes.startswith("<!--"):
        return "-->" not in antes
    if antes.startswith("/*"):
        return "*/" not in antes
    return antes.startswith(("//", "#", "*"))


# ── SQL: comandos sem comentário, cortados fora de aspas e de $tag$ ─────────
def sem_comentarios_sql(t):
    """`-- …` e `/* … */` viram espaço, mantendo as quebras de linha e as posições; aspas e $tag$ são respeitadas."""
    out, i, n = list(t), 0, len(t)
    while i < n:
        c = t[i]
        if c in ("'", '"'):
            j = i + 1
            while j < n:
                if t[j] == c:
                    if j + 1 < n and t[j + 1] == c:
                        j += 2
                        continue
                    break
                j += 1
            i = j + 1
            continue
        if c == "$":
            m = re.match(r"\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$", t[i:])
            if m:
                fecha = t.find(m.group(0), i + len(m.group(0)))
                i = n if fecha < 0 else fecha + len(m.group(0))
                continue
        if t.startswith("--", i):
            j = t.find("\n", i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = " "
            i = j
            continue
        if t.startswith("/*", i):
            j = t.find("*/", i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                if out[k] != "\n":
                    out[k] = " "
            i = j
            continue
        i += 1
    return "".join(out)


def comandos_sql(t):
    """[(posição de início, texto)] de um texto já sem comentários; `;` só corta fora de aspas e de $tag$."""
    cmds, ini, i, n = [], 0, 0, len(t)
    while i < n:
        c = t[i]
        if c in ("'", '"'):
            j = i + 1
            while j < n:
                if t[j] == c:
                    if j + 1 < n and t[j + 1] == c:
                        j += 2
                        continue
                    break
                j += 1
            i = j + 1
            continue
        if c == "$":
            m = re.match(r"\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$", t[i:])
            if m:
                fecha = t.find(m.group(0), i + len(m.group(0)))
                i = n if fecha < 0 else fecha + len(m.group(0))
                continue
        if c == ";":
            cmds.append((ini, t[ini:i]))
            ini = i + 1
        i += 1
    if t[ini:].strip():
        cmds.append((ini, t[ini:]))
    # posição do 1º caractere não branco de cada comando
    saida = []
    for pos, txt in cmds:
        k = len(txt) - len(txt.lstrip())
        if txt.strip():
            saida.append((pos + k, txt.strip()))
    return saida


def trechos_entre_aspas(t):
    """[(início, fim)] dos textos entre aspas simples (com '' dentro). Corpo $tag$…$tag$ não conta: é código da função.
    Identificador entre aspas duplas e comentário (o que sobra dentro do corpo de uma função, que o sem_comentarios_sql
    não toca) são pulados: um apóstrofo neles desalinhava os pares até o fim do arquivo (revisão do código, rodada 3, R4)."""
    out, i, n = [], 0, len(t)
    while i < n:
        c = t[i]
        if c == '"':
            j = i + 1
            while j < n:
                if t[j] == '"':
                    if j + 1 < n and t[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            i = j + 1
            continue
        if t.startswith("--", i):
            j = t.find("\n", i)
            i = n if j < 0 else j
            continue
        if t.startswith("/*", i):
            j = t.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if c == "'":
            j = i + 1
            while j < n:
                if t[j] == "'":
                    if j + 1 < n and t[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            out.append((i, j))
            i = j + 1
            continue
        i += 1
    return out


def dentro(trechos, pos):
    return any(a < pos <= b for a, b in trechos)


IDENT = r'(?:"[^"]+"|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]+"|[A-Za-z_][\w$]*))?'


def nome(bruto):
    n = re.sub(r"\s*\.\s*", ".", bruto.strip()).replace('"', "").lower()
    return n[len("public."):] if n.startswith("public.") else n


def ultimo(bruto):
    return nome(bruto).rsplit(".", 1)[-1]


def fecha_parenteses(t, abre):
    """Posição do `)` que fecha o `(` em `abre` (fora de aspas), ou -1."""
    nivel, i, n = 0, abre, len(t)
    while i < n:
        c = t[i]
        if c in ("'", '"'):
            j = t.find(c, i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
            if nivel == 0:
                return i
        i += 1
    return -1


def partes(t, inicio=0):
    """Os elementos separados por vírgula no nível 0: [(posição relativa, texto)]."""
    out, nivel, ini, i, n = [], 0, 0, 0, len(t)
    while i < n:
        c = t[i]
        if c in ("'", '"'):
            j = t.find(c, i + 1)
            i = n if j < 0 else j + 1
            continue
        if c == "(":
            nivel += 1
        elif c == ")":
            nivel -= 1
        elif c == "," and nivel == 0:
            out.append((inicio + ini, t[ini:i]))
            ini = i + 1
        i += 1
    out.append((inicio + ini, t[ini:]))
    return [(p + len(x) - len(x.lstrip()), x.strip()) for p, x in out if x.strip()]


def colunas(lista):
    """`a, "B" desc, lower(c) text_pattern_ops` → ['a', 'b', 'lower(c)']."""
    cols = []
    for _p, x in partes(lista):
        x = re.sub(r"(?i)\s+(asc|desc|nulls\s+(first|last))\b.*$", "", x).strip()
        m = re.match(r'^("[^"]+"|[A-Za-z_][\w$]*)(\s+[\w.]+)?$', x)
        cols.append(m.group(1).replace('"', "").lower() if m else re.sub(r"\s+", "", x.lower()))
    return cols


# ── o modelo do banco, montado das migrations na ordem do caminho ──────────
CREATE_TABLE = re.compile(r"(?is)^create\s+(?:(?:global|local)\s+)?(?:temp(?:orary)?\s+|unlogged\s+)?table\s+"
                          r"(?:if\s+not\s+exists\s+)?(" + IDENT + r")\s*(.*)$")
ALTER_TABLE = re.compile(r"(?is)^alter\s+table\s+(?:if\s+exists\s+)?(?:only\s+)?(" + IDENT + r")\s+(.*)$")
DROP_TABLE = re.compile(r"(?is)^drop\s+table\s+(?:if\s+exists\s+)?(.*?)(?:\s+(?:cascade|restrict))?$")
CREATE_INDEX = re.compile(r"(?is)^create\s+(unique\s+)?index\s+(?:concurrently\s+)?(?:if\s+not\s+exists\s+)?"
                          r"(?:(?!on\b)(" + IDENT + r")\s+)?on\s+(?:only\s+)?(" + IDENT + r")\s*"
                          r"(?:using\s+(\w+)\s*)?\(")
DROP_INDEX = re.compile(r"(?is)^drop\s+index\s+(?:concurrently\s+)?(?:if\s+exists\s+)?(.*?)(?:\s+(?:cascade|restrict))?$")
# (?![\w$"]) e não \b: com o nome entre aspas (on "public"."pedidos", o formato do `supabase db diff`), não há fronteira de
# palavra depois da aspa, e o \b descartava a política inteira (revisão do código, rodada 2, R1)
CREATE_POLICY = re.compile(r"(?is)^create\s+policy\s+(\"[^\"]+\"|[A-Za-z_][\w$]*)\s+on\s+(" + IDENT + r")(?![\w$\"])(.*)$")
ALTER_POLICY = re.compile(r"(?is)^alter\s+policy\s+(\"[^\"]+\"|[A-Za-z_][\w$]*)\s+on\s+(" + IDENT + r")(?![\w$\"])(.*)$")
DROP_POLICY = re.compile(r"(?is)^drop\s+policy\s+(?:if\s+exists\s+)?(\"[^\"]+\"|[A-Za-z_][\w$]*)\s+on\s+(" + IDENT + r")")
REFERENCES = re.compile(r"(?i)\breferences\b")
VETOR = re.compile(r"(?i)^(?:extensions\.)?vector\s*\(")
AUTH = re.compile(r"(?i)\bauth\s*\.\s*(?:uid|jwt|role)\s*\(\s*\)|\bcurrent_setting\s*\(")
ANTES_SELECT = re.compile(r"(?i)\(\s*select\s*$")
UID_COL = [re.compile(r"(?i)(?:\(\s*select\s+)?auth\s*\.\s*uid\s*\(\s*\)\s*\)?\s*=\s*(" + IDENT + r")"),
           re.compile(r"(?i)(" + IDENT + r")\s*=\s*\(?\s*(?:select\s+)?auth\s*\.\s*uid\s*\(\s*\)")]
ILIKE_SQL = re.compile(r"(?i)(?:\bilike\b|~~\*)\s*'%")
TRGM = re.compile(r"(?i)\bg(?:in|ist)_trgm_ops\b")

def analisar(textos):
    """[(item, arquivo, linha)] de um conjunto de arquivos: o modelo do banco (migrations na ordem do caminho),
    as regras, o código e os padrões por linha. Roda na árvore de agora e na da base."""
    tabelas = {}      # nome → {"onde": (p, n), "pk": bool, "pula": bool}
    indices = []      # {"nome", "tabela", "cols", "metodo", "where", "onde", "explicito"}
    chaves = []       # {"tabela", "cols", "onde"}
    politicas = {}    # (tabela, nome) → {"cmd", "papeis", "permissiva", "onde", "expr"}
    vetores = []      # {"tabela", "col", "onde"}
    initplan = []     # (tabela, política, p, n): a política sai daqui quando é apagada ou trocada (rodada 2, R4)
    ilikes = []       # (p, n)
    tem_trgm = False
    SQL = sorted(p for p in textos if p.lower().endswith(".sql"))

    def coluna_def(tabela, txt, pos, p, t):
        """Uma definição de coluna (`nome tipo … references …`)."""
        m = re.match(r'^("[^"]+"|[A-Za-z_][\w$]*)\s+(.*)$', txt, re.S)
        if not m:
            return
        col, resto = m.group(1).replace('"', "").lower(), m.group(2)
        # texto entre aspas vira espaço (mesmo tamanho, as posições valem): `default 'references x'` não é chave estrangeira
        # nem `default 'primary key'` é chave primária (revisão do código, rodada 3, N1)
        resto = re.sub(r"'(?:[^']|'')*'", lambda q: "'" + " " * (len(q.group(0)) - 2) + "'", resto)
        if re.search(r"(?i)\bprimary\s+key\b", resto):
            tabelas.setdefault(tabela, {"onde": None, "pk": False, "pula": False})["pk"] = True
            indices.append({"nome": None, "tabela": tabela, "cols": [col], "metodo": "btree", "where": "", "onde": None, "explicito": False})
        elif re.search(r"(?i)\bunique\b", resto):
            indices.append({"nome": None, "tabela": tabela, "cols": [col], "metodo": "btree", "where": "", "onde": None, "explicito": False})
        r = REFERENCES.search(resto)
        if r:
            chaves.append({"tabela": tabela, "cols": [col], "onde": (p, linha_de(t, pos + m.start(2) + r.start()))})
        if VETOR.match(resto.strip()):
            vetores.append({"tabela": tabela, "col": col, "onde": (p, linha_de(t, pos))})


    def restricao(tabela, txt, pos, p, t):
        """Uma restrição de tabela: primary key, unique, foreign key. Devolve True se era uma."""
        m = re.match(r"(?is)^(?:constraint\s+(?:\"[^\"]+\"|[\w$]+)\s+)?(primary\s+key|unique|foreign\s+key|check|exclude)\b\s*(.*)$", txt)
        if not m:
            return False
        tipo, resto = re.sub(r"\s+", " ", m.group(1).lower()), m.group(2)
        abre = resto.find("(")
        fecha = fecha_parenteses(resto, abre) if abre >= 0 else -1
        cols = colunas(resto[abre + 1:fecha]) if fecha > abre >= 0 else []
        if tipo == "primary key" and not cols and re.match(r"(?is)^using\s+index\b", resto.strip()):
            # `primary key using index <nome>` (o formato do `supabase db diff`): o índice já foi criado antes, com as
            # colunas; a tabela tem chave primária (revisão do código, rodada 2, R3)
            tabelas.setdefault(tabela, {"onde": None, "pk": False, "pula": False})["pk"] = True
        if tipo == "primary key" and cols:
            tabelas.setdefault(tabela, {"onde": None, "pk": False, "pula": False})["pk"] = True
            indices.append({"nome": None, "tabela": tabela, "cols": cols, "metodo": "btree", "where": "", "onde": None, "explicito": False})
        elif tipo == "unique" and cols:
            indices.append({"nome": None, "tabela": tabela, "cols": cols, "metodo": "btree", "where": "", "onde": None, "explicito": False})
        elif tipo == "foreign key" and cols:
            r = REFERENCES.search(resto)
            n = linha_de(t, pos + m.start(2) + (r.start() if r else 0))
            chaves.append({"tabela": tabela, "cols": cols, "onde": (p, n)})
        return True


    def politica(cm, pos, p, t, alter=False):
        tabela, nome_pol, resto = nome(cm.group(2)), cm.group(1).replace('"', "").lower(), cm.group(3)
        base = pos + cm.start(3)
        # As expressões de using e with check, para P01 e P02.
        exprs = []
        for e in re.finditer(r"(?i)\b(?:using|with\s+check)\s*\(", resto):
            abre = e.end() - 1
            fecha = fecha_parenteses(resto, abre)
            if fecha > abre:
                exprs.append((base + abre, resto[abre:fecha + 1]))
        if exprs:
            # a expressão nova substitui a de antes: o aviso da versão anterior da política não fica
            initplan[:] = [x for x in initplan if (x[0], x[1]) != (tabela, nome_pol)]
        for epos, etxt in exprs:
            for a in AUTH.finditer(etxt):
                if not ANTES_SELECT.search(etxt[:a.start()]):
                    initplan.append((tabela, nome_pol, p, linha_de(t, epos + a.start())))
        if alter:
            pol = politicas.get((tabela, nome_pol))
            if pol is not None and exprs:
                pol["expr"] = [x for _q, x in exprs]
            return
        cab = resto
        for corte in (re.search(r"(?i)\busing\b", resto), re.search(r"(?i)\bwith\s+check\b", resto)):
            if corte and corte.start() < len(cab):
                cab = resto[:corte.start()]
        perm = not re.search(r"(?i)\bas\s+restrictive\b", cab)
        mc = re.search(r"(?i)\bfor\s+(all|select|insert|update|delete)\b", cab)
        mt = re.search(r"(?i)\bto\s+(.+)$", cab, re.S)
        papeis = {x.strip().replace('"', "").lower() for x in mt.group(1).split(",") if x.strip()} if mt else set()
        politicas[(tabela, nome_pol)] = {"cmd": mc.group(1).lower() if mc else "all", "papeis": papeis, "permissiva": perm,
                                         "onde": (p, linha_de(t, pos)), "expr": [x for _q, x in exprs]}


    for p in SQL:
        t = sem_comentarios_sql(textos[p])
        if TRGM.search(t):
            tem_trgm = True
        for m in ILIKE_SQL.finditer(t):
            ilikes.append((p, linha_de(t, m.start())))
        for pos, c in comandos_sql(t):
            m = CREATE_TABLE.match(c)
            if m:
                tabela, resto = nome(m.group(1)), m.group(2)
                info = tabelas.setdefault(tabela, {"onde": None, "pk": False, "pula": False})
                info.update({"onde": (p, linha_de(t, pos)), "pk": False,
                             "pula": bool(re.match(r"(?is)^(partition\s+of|of\s|as\s|as$)", resto.strip()))})
                abre = resto.find("(")
                if info["pula"] or abre < 0:
                    continue
                fecha = fecha_parenteses(resto, abre)
                corpo = resto[abre + 1:fecha] if fecha > abre else resto[abre + 1:]
                ini = pos + m.start(2) + abre + 1
                for epos, el in partes(corpo, ini):
                    if re.match(r"(?i)^like\b", el):
                        info["pula"] = True
                    elif not restricao(tabela, el, epos, p, t):
                        coluna_def(tabela, el, epos, p, t)
                continue
            m = ALTER_TABLE.match(c)
            if m:
                tabela = nome(m.group(1))
                ini = pos + m.start(2)
                for epos, acao in partes(m.group(2), ini):
                    a = re.match(r"(?is)^add\s+(?:column\s+)?(?:if\s+not\s+exists\s+)?(.*)$", acao)
                    if not a:
                        continue
                    corpo = a.group(1)
                    cpos = epos + a.start(1)
                    if not restricao(tabela, corpo, cpos, p, t) and not re.match(r"(?i)^constraint\b", corpo):
                        coluna_def(tabela, corpo, cpos, p, t)
                continue
            m = DROP_TABLE.match(c)
            if m:
                for _q, x in partes(m.group(1)):
                    tn = nome(x)
                    tabelas.pop(tn, None)
                    indices[:] = [ix for ix in indices if ix["tabela"] != tn]
                    chaves[:] = [k for k in chaves if k["tabela"] != tn]
                    vetores[:] = [v for v in vetores if v["tabela"] != tn]
                    for chave in [k for k in politicas if k[0] == tn]:
                        politicas.pop(chave)
                    initplan[:] = [x for x in initplan if x[0] != tn]
                continue
            m = CREATE_INDEX.match(c)
            if m:
                abre = m.end() - 1
                fecha = fecha_parenteses(c, abre)
                cols = colunas(c[abre + 1:fecha]) if fecha > abre else []
                depois = c[fecha + 1:] if fecha > abre else ""
                mw = re.search(r"(?is)\bwhere\b(.*)$", depois)
                indices.append({"nome": ultimo(m.group(2)) if m.group(2) else None, "tabela": nome(m.group(3)), "cols": cols,
                                "metodo": (m.group(4) or "btree").lower(), "where": re.sub(r"\s+", " ", mw.group(1).strip().lower()) if mw else "",
                                "onde": (p, linha_de(t, pos)), "explicito": True})
                continue
            m = DROP_INDEX.match(c)
            if m:
                nomes = {ultimo(x) for _q, x in partes(m.group(1))}
                indices[:] = [ix for ix in indices if ix["nome"] not in nomes]
                continue
            m = CREATE_POLICY.match(c)
            if m:
                politica(m, pos, p, t)
                continue
            m = ALTER_POLICY.match(c)
            if m:
                politica(m, pos, p, t, alter=True)
                continue
            m = DROP_POLICY.match(c)
            if m:
                chave = (nome(m.group(2)), m.group(1).replace('"', "").lower())
                politicas.pop(chave, None)
                initplan[:] = [x for x in initplan if (x[0], x[1]) != chave]


    def coberto(tabela, cols):
        """Algum índice da tabela tem as k primeiras colunas iguais (como conjunto) às k colunas pedidas."""
        k = len(cols)
        return any(ix["tabela"] == tabela and len(ix["cols"]) >= k and set(ix["cols"][:k]) == set(cols) for ix in indices)


    achados = []   # (item, arquivo, linha)


    def acha(regra, onde):
        for f in ATIVOS:
            if f["c"]["padrao"] == regra and onde:
                achados.append((f, onde[0], onde[1]))


    for _tab, _pol, ip, n in initplan:
        acha("regra:initplan", (ip, n))
    for (tabela, _n), pol in sorted(politicas.items(), key=lambda kv: kv[1]["onde"]):
        vistas = set()
        for expr in pol["expr"]:
            for rx in UID_COL:
                for m in rx.finditer(expr):
                    col = ultimo(m.group(1))
                    if col in ("select", "auth") or col in vistas:
                        continue
                    vistas.add(col)
                    if not coberto(tabela, [col]):
                        acha("regra:politica-sem-indice", pol["onde"])
        if not pol["papeis"]:
            acha("regra:sem-papel", pol["onde"])
    for k in chaves:
        if not coberto(k["tabela"], k["cols"]):
            acha("regra:fk-sem-indice", k["onde"])
    for tabela, info in sorted(tabelas.items()):
        if info["onde"] and not info["pk"] and not info["pula"]:
            acha("regra:sem-pk", info["onde"])
    por_tabela = {}
    for (tabela, _n), pol in sorted(politicas.items(), key=lambda kv: kv[1]["onde"]):
        if pol["permissiva"]:
            por_tabela.setdefault(tabela, []).append(pol)
    for tabela, lista in por_tabela.items():
        for j, b in enumerate(lista):
            for a in lista[:j]:
                cmd_cruza = a["cmd"] == b["cmd"] or "all" in (a["cmd"], b["cmd"])
                pa, pb = a["papeis"] or {"public"}, b["papeis"] or {"public"}
                papel_cruza = bool(pa & pb) or "public" in pa or "public" in pb
                if cmd_cruza and papel_cruza:
                    acha("regra:permissivas", b["onde"])
                    break
    vistos_ix = {}
    for ix in indices:
        chave = (ix["tabela"], ix["metodo"], tuple(ix["cols"]), ix["where"])
        # o mesmo nome é o mesmo índice declarado de novo (`if not exists` repetido, dump ao lado das migrations), não
        # um índice repetido (revisão do código, rodada 3, R5)
        mesmo = ix["nome"] is not None and ix["nome"] in vistos_ix.get(chave, set())
        if chave in vistos_ix and ix["explicito"] and not mesmo:
            acha("regra:indice-duplicado", ix["onde"])
        vistos_ix.setdefault(chave, set()).add(ix["nome"])
    for v in vetores:
        if not any(ix["tabela"] == v["tabela"] and ix["metodo"] in ("hnsw", "ivfflat") and v["col"] in ix["cols"] for ix in indices):
            acha("regra:busca", v["onde"])
    if not tem_trgm:
        for onde in ilikes:
            acha("regra:busca", onde)

    # Código: listas sem limite (P08) e busca por pedaço de texto (P15).
    FROM = re.compile(r"\.from\(\s*['\"`]")
    LIMITE = re.compile(r"\.(?:range|limit|single|maybeSingle|insert|update|upsert|delete)\(|head:\s*true")
    ILIKE_JS = re.compile(r"\.ilike\(\s*['\"`][^'\"`]*['\"`]\s*,\s*['\"`]%")
    regra_lista = [f for f in ATIVOS if f["c"]["padrao"] == "regra:lista-sem-limite"]
    regra_busca = [f for f in ATIVOS if f["c"]["padrao"] == "regra:busca"]
    for p, t in textos.items():
        if p.lower().endswith(".sql"):
            continue
        linhas = t.split("\n")
        for f in regra_lista:
            if not casa(p, f["globs"]):
                continue
            for m in FROM.finditer(t):
                n = linha_de(t, m.start())
                if comentado(linhas[n - 1], m.start() - (t.rfind("\n", 0, m.start()) + 1), False):
                    continue
                fim_cmd = t.find(";", m.end())
                # sem `;` (o estilo da documentação do supabase-js), a janela para na próxima consulta: o limite dela não
                # vale para esta (revisão do código, rodada 2, R5)
                prox = FROM.search(t, m.end())
                fim = min(x for x in (fim_cmd, prox.start() if prox else -1, len(t)) if x >= 0)
                janela = t[m.start(): fim]
                janela = "\n".join(janela.split("\n")[:12])
                if ".select(" in janela and not LIMITE.search(janela):
                    achados.append((f, p, n))
        for f in regra_busca:
            if tem_trgm or not casa(p, f["globs"]):
                continue
            for m in ILIKE_JS.finditer(t):
                n = linha_de(t, m.start())
                if not comentado(linhas[n - 1], m.start() - (t.rfind("\n", 0, m.start()) + 1), False):
                    achados.append((f, p, n))

    # Padrões por linha (re:`…`).
    for f in ATIVOS:
        if f["re"] is None:
            continue
        for p, t in textos.items():
            if not casa(p, f["globs"]):
                continue
            sql = p.lower().endswith(".sql")
            # no SQL, o padrão roda sobre o texto sem comentários (posições preservadas) e fora de texto entre aspas: o
            # `-- …` no fim da linha e o `/* … */` não acusam (revisão do código, rodada 1, R2)
            base = sem_comentarios_sql(t) if sql else t
            literais = trechos_entre_aspas(base) if sql else []
            inicio, cruas = 0, t.split("\n")
            for n, ln in enumerate(base.split("\n"), 1):
                for m in f["re"].finditer(ln):
                    if sql and dentro(literais, inicio + m.start()):
                        continue
                    if not comentado(cruas[n - 1], m.start(), sql):
                        achados.append((f, p, n))
                    break
                inicio += len(ln) + 1


    return achados


# ── dispensa, novo × já existia, saída ─────────────────────────────────────
def so_comentario(linha):
    """A linha não tem código: só um comentário (SQL, JS/TS, shell, HTML)."""
    return linha.lstrip().startswith(("--", "//", "#", "/*", "*", "<!--"))


def limpa_motivo(bruto):
    m = re.split(r"\*/|-->", bruto, maxsplit=1)[0].strip()
    return m if len(m) <= 160 else m[:157] + "…"


def chave(fid, p, n, txts):
    linhas = txts[p].split("\n")
    return (fid, p, re.sub(r"\s+", " ", linhas[n - 1].strip()) if 1 <= n <= len(linhas) else "")


achados = analisar(textos)
ref, base_ok, BASE = base_textos()
na_base = {}
if BASE is not None:
    for fid, p, n in sorted(set((f["id"], p, n) for f, p, n in analisar(BASE))):
        k = chave(fid, p, n, BASE)
        na_base[k] = na_base.get(k, 0) + 1

unicos = sorted(set((f["id"], p, n) for f, p, n in achados), key=lambda a: (a[1], a[2], a[0]))
novos, antigos, aceitos, dispensas_ruins = [], [], [], []
for fid, p, n in unicos:
    f = POR_ID[fid]
    linhas = textos[p].split("\n")
    # A marca na própria linha vale para ela; a da linha de cima só vale quando aquela linha é só comentário (contrato
    # de aceite, proposta 4): um comentário no fim de uma linha de código não esconde o aviso da linha de baixo.
    marcas = [m for m in [DISPENSA.search(linhas[n - 1])] if m] if 1 <= n <= len(linhas) else []
    if 2 <= n <= len(linhas) + 1 and so_comentario(linhas[n - 2]):
        marcas += [m for m in [DISPENSA.search(linhas[n - 2])] if m]
    do_item = [m for m in marcas if m.group(1) == fid]
    if do_item:
        motivo = limpa_motivo(do_item[0].group(2))
        if len(re.sub(r"\s", "", motivo)) >= 3:
            aceitos.append((f, p, n, motivo))
            continue
    if marcas:
        dispensas_ruins.append((f, p, n))
    k = chave(fid, p, n, textos)
    if BASE is not None and na_base.get(k, 0) > 0:
        na_base[k] -= 1
        antigos.append((f, p, n))
    else:
        novos.append((f, p, n))

ordem = lambda a: (GRAV[a[0]["c"]["gravidade"]], a[0]["id"], a[1], a[2])
novos.sort(key=ordem)
antigos.sort(key=ordem)

saida = ["▶ desempenho-varredura — stack: %s · base: %s · %d arquivo(s) varrido(s), %d pulado(s)" % (
    TXT_STACK, ref, len(textos), len(pulados))]
if not base_ok:
    saida.append("⚠️ base %s não existe: tudo conta como novo (sem remoto ou sem a branch padrão)" % ref)
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


def linha_achado(f, p, n, extra=""):
    return "⚠️ %s %s %s:%d — %s%s" % (f["id"], f["c"]["gravidade"], p, n, f["falha"], extra)


lista = [(a, "") for a in novos] + [(a, " (já existia)") for a in antigos]
na_tela_lista = lista if op["--tudo"] else [(a, e) for a, e in lista if not e]
mostrados = 0
for (f, p, n), extra in lista:
    tela = (f, p, n) in [x for x, _e in na_tela_lista] and mostrados < TETO
    if tela:
        mostrados += 1
    mostra(linha_achado(f, p, n, extra), f, tela)
resto = len(na_tela_lista) - mostrados
if resto > 0:
    if op["--saida"]:
        print("… e mais %d aviso(s): lista inteira em %s" % (resto, op["--saida"]))
    else:
        print("… e mais %d aviso(s): rode com --saida <arquivo> para ver todos" % resto)
if antigos and not op["--tudo"]:
    t = "ℹ️ %d achado(s) que já existiam — liste com --tudo" % len(antigos)
    print(t)
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

if novos:
    rc, palavra, seta = 1, "AVISOS", ("confira cada aviso pela prova à mão; o que for falso positivo leva a dispensa na linha, "
                                       "com motivo. Nada aqui bloqueia a publicação.")
elif antigos:
    rc, palavra, seta = 0, "NADA NOVO", ("siga; o que já existia é outra conversa: o diagnóstico da sdd-desempenho-banco "
                                          "ajuda a priorizar.")
else:
    rc, palavra, seta = 0, "NADA ACHADO", ("siga; a varredura só acha o que dá para ver por texto: as fichas só à mão estão "
                                            "na skill sdd-desempenho-banco.")
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
