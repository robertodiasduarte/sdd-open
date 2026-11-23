#!/usr/bin/env bash
# qualidade-regras.sh — lê o catálogo de qualidade da skill sdd-build e diz as regras de forma do código que valem neste
# projeto: as gerais e as da stack que ele usa. Só lê: não usa rede, não executa nada do projeto, não grava nada.
#
# Por que existe: o código feito por agente passa no teste com erro engolido, nome vago e helper duplicado; a regra
# escrita onde o agente lê antes de construir (o AGENTS.md e o passo de escrever da build) previne mais barato que o
# conserto. O catálogo (.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md) é a fonte única: este script é o
# único leitor dele, e serve o bloco do AGENTS.md (init/sync) e as regras da build.
#
# USO-INICIO
#   qualidade-regras.sh --stack     as stacks do projeto (python, js, ts, php, sql), detectadas pelos arquivos
#   qualidade-regras.sh --regras    as regras gerais e as da stack, mais os comandos de lint e de tipos do projeto
#                                   (a sdd-build lê antes de construir)
#   qualidade-regras.sh --agents    só as linhas do bloco de qualidade do AGENTS.md (o init/sync usa)
#   Opções: --raiz DIR (padrão: a raiz do git) · --catalogo ARQ (padrão: o catálogo da sdd-build do projeto).
#   Saída: 0, ou 64 com a causa (opção, catálogo ausente ou fora do formato, pasta inexistente).
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
  echo "🛑 qualidade-regras: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi lido.\n' >&2
  exit 64
fi

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import fnmatch, os, re, subprocess, sys

CAMPOS_REGRA = ["stack", "frase"]
CAMPOS_FERRAMENTA = ["detecta", "config", "lint", "tipos", "instalar"]
STACKS = ("python", "js", "ts", "php", "sql")
CATALOGO_REL = ".agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md"
# As pastas do SDD e dos agentes têm código do próprio método (scripts .py, .sh): não dizem a stack do projeto.
FORA_PASTAS = (".agents/", ".claude/", ".cursor/", ".gemini/", ".codex/", ".kimi/", "sdd/", "node_modules/", "vendor/",
               ".git/", ".venv/", "venv/")
PONTEIRO = ("- Antes de cada tarefa, rode `bash sdd/bin/qualidade-regras.sh --regras` e siga as regras de qualidade da "
            "stack deste projeto; o lint e a checagem de tipos do projeto (`project.lint_cmd` e "
            "`project.typecheck_cmd` em `sdd/config.yaml`) conferem o que dá para medir.")


def fim(rc, palavra, seta, para=sys.stdout):
    print("RESULTADO: %s" % palavra, file=para)
    print("→ %s" % seta, file=para)
    sys.exit(rc)


def uso(msg, seta="rode com --help para ver o uso; nada foi lido nem gravado."):
    print("🛑 qualidade-regras: %s" % msg, file=sys.stderr)
    fim(64, "ERRO DE USO", seta, sys.stderr)


# ── argumentos ─────────────────────────────────────────────────────────────
MODOS = ("--stack", "--regras", "--agents")
op = {"modo": None, "--raiz": None, "--catalogo": None}
args = sys.argv[1:]
i = 0
while i < len(args):
    a = args[i]
    if a in MODOS:
        if op["modo"]:
            uso("dois modos na mesma chamada: %s e %s" % (op["modo"], a))
        op["modo"] = a
        i += 1
    elif a in ("--raiz", "--catalogo"):
        if i + 1 >= len(args) or not args[i + 1]:
            uso("%s precisa de um valor" % a)
        op[a] = args[i + 1]
        i += 2
    else:
        uso("opção desconhecida: %s" % a)
if not op["modo"]:
    uso("diga o modo: --stack, --regras ou --agents")


def git(raiz, *a):
    try:
        r = subprocess.run(["git", "-C", raiz, "-c", "core.quotepath=off", "-c", "color.ui=never", *a],
                           capture_output=True)
    except OSError:
        return 127, b"", b""
    return r.returncode, r.stdout, r.stderr


if op["--raiz"]:
    RAIZ = os.path.abspath(op["--raiz"])
    if not os.path.isdir(RAIZ):
        uso("a pasta de --raiz não existe: %s" % op["--raiz"])
else:
    rc, out, _ = git(os.getcwd(), "rev-parse", "--show-toplevel")
    RAIZ = out.decode("utf-8", "replace").strip() if rc == 0 else os.getcwd()
CATALOGO = op["--catalogo"] or os.path.join(RAIZ, CATALOGO_REL)


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


# ── catálogo: uma gramática, um leitor ─────────────────────────────────────
def ilegivel(n, motivo):
    uso("catálogo fora do formato: %s:%d — %s" % (CATALOGO, n, motivo),
        "o catálogo vem do pacote: rode o upgrade do pacote (bash <pacote>/bin/sdd-open.sh upgrade).")


def ler_catalogo():
    try:
        linhas = open(CATALOGO, encoding="utf-8").read().splitlines()
    except (OSError, UnicodeDecodeError):
        uso("catálogo ausente ou ilegível: %s" % CATALOGO,
            "instale a skill sdd-build (o init do pacote copia) ou passe --catalogo <arquivo>.")
    regras, ferramentas, secao, atual = [], {}, None, None

    def fecha(n):
        if atual is None:
            return
        esperados = CAMPOS_REGRA if atual["tipo"] == "regra" else CAMPOS_FERRAMENTA
        if list(atual["c"]) != esperados:
            ilegivel(atual["n"], "a ficha %s tem os campos %s; esperado %s, nesta ordem"
                     % (atual["id"], ", ".join(atual["c"]) or "nenhum", ", ".join(esperados)))
        if atual["tipo"] == "regra":
            if atual["c"]["stack"] not in ("todas",) + STACKS:
                ilegivel(atual["n"], "stack desconhecida em %s: %s" % (atual["id"], atual["c"]["stack"]))
            regras.append(atual)
        else:
            ferramentas[atual["id"]] = atual["c"]

    for n, linha in enumerate(linhas, 1):
        if linha.startswith("## "):
            fecha(n)
            atual = None
            secao = linha[3:].strip()
            continue
        if linha.startswith("### ") and secao in ("Regras", "Ferramentas por stack"):
            fecha(n)
            titulo = linha[4:].strip()
            if secao == "Regras":
                m = re.match(r"^(Q\d\d) — (.+)$", titulo)
                if not m:
                    ilegivel(n, "título de regra fora do formato `### Qnn — <regra>`: %s" % titulo)
                atual = {"tipo": "regra", "id": m.group(1), "nome": m.group(2), "n": n, "c": {}}
            else:
                if titulo not in STACKS:
                    ilegivel(n, "stack desconhecida em Ferramentas por stack: %s" % titulo)
                atual = {"tipo": "ferramenta", "id": titulo, "n": n, "c": {}}
            continue
        if atual is not None:
            m = re.match(r"^- ([a-z]+): (.+)$", linha)
            if m:
                if m.group(1) in atual["c"]:
                    ilegivel(n, "campo %s repetido em %s" % (m.group(1), atual["id"]))
                atual["c"][m.group(1)] = m.group(2).strip()
            elif linha.strip():
                ilegivel(n, "linha fora de um campo `- nome: valor` em %s" % atual["id"])
    fecha(len(linhas))
    if not any(r["c"]["stack"] == "todas" for r in regras):
        ilegivel(1, "nenhuma regra com stack: todas")
    return regras, ferramentas


REGRAS, FERRAMENTAS = ler_catalogo()


# ── arquivos e stack ───────────────────────────────────────────────────────
def lista_arquivos():
    rc, out, _ = git(RAIZ, "ls-files", "-co", "--exclude-standard", "-z")
    if rc == 0:
        nomes = [p for p in out.decode("utf-8", "replace").split("\0") if p]
    else:  # fora do git: a pasta, até 3 níveis
        nomes = []
        for base, pastas, arqs in os.walk(RAIZ):
            rel = os.path.relpath(base, RAIZ)
            prof = 0 if rel == "." else rel.count(os.sep) + 1
            pastas[:] = [] if prof >= 3 else [p for p in pastas if not (p + "/").startswith(FORA_PASTAS)]
            nomes += [a if rel == "." else os.path.join(rel, a).replace(os.sep, "/") for a in arqs]
    return sorted(p for p in set(nomes) if not p.startswith(FORA_PASTAS))


ARQUIVOS = lista_arquivos()


def detecta(sinais):
    for s in [x.strip() for x in sinais.split(",") if x.strip()]:
        if s.startswith("*."):
            if any(fnmatch.fnmatch(os.path.basename(p), s) for p in ARQUIVOS):
                return True
        elif os.path.isfile(os.path.join(RAIZ, s)):
            return True
    return False


STACK = [s for s in STACKS if s in FERRAMENTAS and detecta(FERRAMENTAS[s]["detecta"])]
TXT_STACK = ", ".join(STACK) if STACK else "nenhuma reconhecida"
ATIVAS = [r for r in REGRAS if r["c"]["stack"] == "todas" or r["c"]["stack"] in STACK]

# ── modos ──────────────────────────────────────────────────────────────────
if op["modo"] == "--stack":
    print("stack: %s" % TXT_STACK)
    fim(0, "OK", "as regras de outras stacks não valem aqui; a stack vem dos arquivos do projeto.")
if op["modo"] == "--agents":
    for r in ATIVAS:
        print("- %s" % r["c"]["frase"])
    print(PONTEIRO)
    sys.exit(0)
# --regras
print("Regras de qualidade deste projeto — stack: %s" % TXT_STACK)
for r in ATIVAS:
    print("- %s %s: %s" % (r["id"], r["nome"], r["c"]["frase"]))
PROJ = ler_mapa(RAIZ, "project")
for slot, nome in (("lint_cmd", "lint"), ("typecheck_cmd", "tipos")):
    cmd = PROJ.get(slot, "").strip()
    if cmd:
        print("%s: `%s` (project.%s) — rode sobre os arquivos da tarefa; erro é falha da tarefa" % (nome, cmd, slot))
    else:
        print("%s: slot vazio (project.%s) — escreva `lint: slot vazio` no BUILD_REPORT" % (nome, slot))
fim(0, "OK", "siga estas regras ao escrever o código; o lint e os tipos do projeto conferem o que dá para medir.")
PY
