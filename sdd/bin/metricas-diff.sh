#!/usr/bin/env bash
# metricas-diff.sh — complexidade e duplicação do código que a frente trouxe, só aviso (F30 S3).
#
# Por que existe: o código feito por agente passa no teste com função enorme e com helper que já existia recriado. Este
# script mede só o que o diff trouxe (base..árvore de trabalho, com os arquivos novos) e imprime a seção
# `## Qualidade (avisos)` do BUILD_REPORT. Nunca reprova: sai 0 sempre que rodou. Ferramenta ausente ou quebrada é
# "não medido", com a causa — nunca "nenhum aviso".
#
# USO-INICIO
#   bash sdd/bin/metricas-diff.sh [--raiz DIR] [--base REF]
#     --raiz  a pasta do projeto (padrão: a raiz do git)
#     --base  a referência de onde a frente nasceu (padrão: origin/<project.default_branch>, ou a branch local)
#   Ferramentas (opcionais, do PATH; nada é instalado): lizard (complexidade) e jscpd (duplicação).
#   Limites: qualidade.max_complexidade (10), max_linhas (60), max_parametros (5) e min_tokens (50) do sdd/config.yaml.
#   Saída: a seção em stdout; RESULTADO (AVISOS · NÃO MEDIDO · NADA ACHADO) e a seta em stderr.
#   Exit: 0 rodou · 64 uso (opção, fora de git, base que não resolve, limite inválido, Python ausente).
# USO-FIM
#
# As ferramentas rodam numa cópia temporária só dos arquivos de código: a árvore não muda, e o .jscpd.json, a chave jscpd
# do package.json e o .gitignore do projeto não mudam a medição. ⚠️ bash 3.2 · núcleo em Python 3.9 stdlib.

set -u
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi   # F16W2: sem a biblioteca, ao menos o UTF-8

uso() {
  echo "🛑 metricas-diff: ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ %s\n' "${2:-rode com --help para ver o uso; nada foi medido.}" >&2
  exit 64
}

RAIZ=""; BASE=""
while [ $# -gt 0 ]; do
  case "${1}" in
    -h|--help) sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'; exit 0 ;;
    --raiz|--base)
      case "${2:-}" in ""|-*) uso "${1} precisa de um valor" ;; esac
      if [ "${1}" = --raiz ]; then RAIZ="${2}"; else BASE="${2}"; fi
      shift 2 ;;
    *) uso "opção desconhecida: ${1}" ;;
  esac
done

if ! sdd_python_pronto; then
  echo "🛑 metricas-diff: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi medido.\n' >&2
  exit 64
fi
[ -z "${RAIZ}" ] || [ -d "${RAIZ}" ] || uso "a pasta de --raiz não existe: ${RAIZ}"
TOPO="$(git -C "${RAIZ:-.}" rev-parse --show-toplevel 2>/dev/null)" || uso "fora de um repositório git" "rode na pasta do projeto."
# com --raiz numa subpasta (monorepo), o projeto é ela: o config, o diff e a cópia são só dela
if [ -n "${RAIZ}" ]; then RAIZ="$(cd "${RAIZ}" && pwd)" || uso "não consegui entrar na pasta de --raiz"; else RAIZ="${TOPO}"; fi

TRAB="$(mktemp -d "${TMPDIR:-/tmp}/sdd-metricas.XXXXXX" 2>/dev/null)" || uso "não consegui criar a pasta temporária" "confira o TMPDIR e rode de novo."
case "${TRAB}" in /*|[A-Za-z]:*) ;; *) TRAB="${PWD}/${TRAB}" ;; esac   # TMPDIR relativo
limpa() { cd / && rm -rf "${TRAB}"; }
trap limpa EXIT
trap 'limpa; exit 130' INT
trap 'limpa; exit 143' TERM
trap 'limpa; exit 129' HUP

cat > "${TRAB}/nucleo.py" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import csv, json, os, re, subprocess, sys

LIMITES = {"max_complexidade": 10, "max_linhas": 60, "max_parametros": 5, "min_tokens": 50}
COM_COMPLEXIDADE = set("py js jsx mjs cjs ts tsx vue php java cs c cc cpp cxx h hpp go rb rs swift kt kts scala lua m mm "
                       "dart".split())
SO_DUPLICACAO = set("sh bash sql".split())
# As pastas do método e de terceiros não são código do projeto (a lista do qualidade-regras.sh). As 5 últimas valem em
# qualquer profundidade.
FORA_RAIZ = (".agents/", ".claude/", ".cursor/", ".gemini/", ".codex/", ".kimi/", "sdd/")
FORA_QUALQUER = ("node_modules", "vendor", ".git", ".venv", "venv")
MAX_BYTES = 5 * 1024 * 1024
MAX_ITENS = 20
COLUNAS_LIZARD = 11
INSTALAR = {"lizard": "python3 -m pip install lizard", "jscpd": "npm install -g jscpd"}


class Uso(Exception):
    """Chamada que não dá para atender: exit 64, com a causa e o conserto."""

    def __init__(self, causa, conserto="confira a pasta do projeto e rode de novo"):
        super().__init__(causa)
        self.conserto = conserto


# ── git e config ───────────────────────────────────────────────────────────
def git(raiz, *args):
    r = subprocess.run(["git", "-C", raiz, "-c", "core.quotepath=off", "-c", "color.ui=never", *args],
                       capture_output=True, stdin=subprocess.DEVNULL)
    return r.returncode, r.stdout


def git_ok(raiz, *args):
    rc, saida = git(raiz, *args)
    if rc != 0:
        raise Uso("o git falhou (git %s)" % args[0])
    return saida


def nomes_z(saida):
    return [os.fsdecode(p) for p in saida.split(b"\0") if p]


def ler_mapa(raiz, mapa):
    """{chave: valor} do mapa de 1 nível do sdd/config.yaml (o mesmo formato que o report-lint.py lê)."""
    try:
        with open(os.path.join(raiz, "sdd", "config.yaml"), encoding="utf-8", errors="replace") as f:
            linhas = f.read().splitlines()
    except OSError:
        return {}
    dentro, valores = False, {}
    for linha in linhas:
        if re.match(r"^\S", linha):
            if not linha.startswith("#"):
                dentro = linha.split("#", 1)[0].strip() == mapa + ":"
            continue
        m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", linha) if dentro else None
        if m:
            v = m.group(2).strip()
            v = v[1:].split(v[0], 1)[0] if v[:1] in ("'", '"') else v.split("#", 1)[0]
            valores.setdefault(m.group(1), v.strip())
    return valores


def ler_linha_unica(raiz, mapa):
    """O que vem depois de `mapa:` na mesma linha (a forma `mapa: {…}`, que o leitor de mapas não entende)."""
    m = re.search(r"(?m)^%s:[ \t]*([^#\r\n]*)" % mapa, ler(os.path.join(raiz, "sdd"), "config.yaml"))
    return m.group(1).strip() if m else ""


def ler_limites(raiz):
    if ler_linha_unica(raiz, "qualidade") not in ("", "{}"):
        raise Uso("qualidade: numa linha só no sdd/config.yaml não é lido", "escreva uma chave por linha, recuada, abaixo de qualidade:")
    mapa, limites = ler_mapa(raiz, "qualidade"), {}
    for chave, padrao in LIMITES.items():
        valor = mapa.get(chave, "")
        if valor and not re.match(r"^[0-9]{1,9}$", valor) or valor and int(valor) < 1:
            raise Uso("qualidade.%s no sdd/config.yaml não é um inteiro maior que zero: %s" % (chave, limpo(valor)),
                      "escreva um inteiro maior que zero em qualidade.%s, ou deixe vazio para o padrão (%d)" % (chave, padrao))
        limites[chave] = int(valor) if valor else padrao
    return limites


def achar_base(raiz, pedida):
    """(nome da referência, commit comum). Sem --base: o remoto da branch padrão e, sem ele, a branch local."""
    branch = ler_mapa(raiz, "project").get("default_branch") or "main"
    for ref in ([pedida] if pedida else ["origin/" + branch, branch]):
        if git(raiz, "rev-parse", "--verify", "--quiet", ref + "^{commit}")[0] != 0:
            continue   # só a referência que não existe dá lugar à próxima
        rc, saida = git(raiz, "merge-base", "HEAD", ref)
        if rc == 0 and saida.strip():
            return ref, saida.decode("ascii").strip()
        raise Uso("%s e a frente não têm um commit em comum" % ref, "passe de onde a frente nasceu: --base REF")
    raise Uso("não achei o ponto de partida da frente (%s)" % (pedida or "origin/%s nem %s" % (branch, branch)),
              "passe de onde a frente nasceu: --base REF")


# ── o diff ─────────────────────────────────────────────────────────────────
def extensao(arq):
    return os.path.splitext(arq)[1][1:].lower()


def e_codigo(arq):
    partes = arq.split("/")[:-1]
    return (extensao(arq) in COM_COMPLEXIDADE | SO_DUPLICACAO and not arq.startswith(FORA_RAIZ)
            and not any(p in FORA_QUALQUER for p in partes))


def legivel(raiz, arq):
    p = os.path.join(raiz, arq)
    return os.path.isfile(p) and not os.path.islink(p)


def mudados(raiz, base):
    """[(nome antigo, nome novo)] do que mudou ou entrou, com a detecção de renomeação ligada."""
    campos = nomes_z(git_ok(raiz, "diff", "--no-color", "--relative", "--name-status", "-z", "-M", "--no-ext-diff", base, "--"))
    pares, i = [], 0
    while i < len(campos):
        renomeado = campos[i][:1] in "RC"
        antigo, novo = campos[i + 1], campos[i + 2 if renomeado else i + 1]
        if campos[i][:1] != "D":
            pares.append((antigo, novo))
        i += 3 if renomeado else 2
    return pares


def trechos(raiz, base, antigo, novo):
    """(intervalos acrescentados ou mudados, linhas depois das quais algo foi só apagado) de um arquivo."""
    saida = git_ok(raiz, "--literal-pathspecs", "diff", "--no-color", "--relative", "-U0", "--inter-hunk-context=0", "-M", "--text", "--no-ext-diff",
                   "--no-textconv", base, "--", *sorted({antigo, novo}))
    novos, apagados = [], []
    for m in re.finditer(rb"(?m)^@@ -\S+ \+(\d+)(?:,(\d+))? @@", saida):
        inicio, n = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        if n:
            novos.append((inicio, inicio + n - 1))
        else:
            apagados.append(inicio)
    return novos, apagados


def linhas_do_diff(raiz, base):
    """{arquivo de código: os trechos dele que mudaram}; arquivo fora do índice é novo inteiro."""
    diff = {}
    for antigo, novo in mudados(raiz, base):
        if e_codigo(novo) and legivel(raiz, novo):
            mudou = trechos(raiz, base, antigo, novo)
            if any(mudou):
                diff[novo] = mudou
    for arq in nomes_z(git_ok(raiz, "ls-files", "-o", "--exclude-standard", "-z")):
        if e_codigo(arq) and legivel(raiz, arq):
            diff[arq] = ([(1, sys.maxsize)], [])
    return diff


def toca_o_diff(diff, arq, ini, fim):
    novos, apagados = diff.get(arq, ((), ()))
    # o git aponta o trecho apagado pela linha anterior a ele: na última linha do intervalo, ele fica depois, fora
    return any(a <= fim and b >= ini for a, b in novos) or any(ini <= c < fim for c in apagados)


# ── 1ª passada: a cópia que as ferramentas leem ────────────────────────────
def ler_codigo(raiz, arq):
    """Os bytes em UTF-8 (o jscpd pula calado o que não é), ou None quando não dá para medir: grande ou sem leitura."""
    p = os.path.join(raiz, arq)
    try:
        if os.path.getsize(p) > MAX_BYTES:
            return None
        with open(p, "rb") as f:
            dado = f.read()
    except OSError:
        return None
    try:
        dado.decode("utf-8")
        return dado
    except UnicodeDecodeError:
        return dado.decode("latin-1").encode("utf-8")


def copiar(dado, arq, destino):
    alvo = os.path.join(destino, arq)
    os.makedirs(os.path.dirname(alvo), exist_ok=True)
    with open(alvo, "wb") as f:
        f.write(dado)


def montar_copias(raiz, trab, diff):
    """trab/arvore = o código do projeto; trab/diff = só o do diff. Devolve os arquivos que não dá para medir."""
    for pasta in ("arvore", "diff"):
        os.makedirs(os.path.join(trab, pasta))
    fora = []
    for arq in sorted(set(nomes_z(git_ok(raiz, "ls-files", "-z"))) | set(diff)):
        if not e_codigo(arq) or not legivel(raiz, arq):
            continue
        dado = ler_codigo(raiz, arq)
        if dado is None:
            fora.append(arq)
            continue
        copiar(dado, arq, os.path.join(trab, "arvore"))
        if arq in diff:
            copiar(dado, arq, os.path.join(trab, "diff"))
    return fora


def preparar(raiz, trab, pedida):
    limites = ler_limites(raiz)
    ref, base = achar_base(raiz, pedida)
    diff = linhas_do_diff(raiz, base)
    proprio = os.path.relpath(os.path.realpath(trab), os.path.realpath(raiz)).replace(os.sep, "/") + "/"
    diff = {a: t for a, t in diff.items() if not a.startswith(proprio)}   # TMPDIR dentro do projeto
    fora = montar_copias(raiz, trab, diff)
    medidos = sorted(set(diff) - set(fora))
    do_lizard = [a for a in medidos if extensao(a) in COM_COMPLEXIDADE]
    with open(os.path.join(trab, "lizard.lista"), "wb") as f:
        f.write(b"".join(os.fsencode("./" + arq) + b"\0" for arq in do_lizard))
    with open(os.path.join(trab, "jscpd.vazio.json"), "w", encoding="utf-8") as f:
        f.write("{}")
    with open(os.path.join(trab, "plano.json"), "w", encoding="utf-8") as f:
        json.dump({"ref": ref, "base": base, "limites": limites, "diff": diff, "medidos": medidos, "fora": fora}, f)
    print("%d %d %d" % (limites["min_tokens"], len(do_lizard), len(medidos)))


# ── 2ª passada: a seção ────────────────────────────────────────────────────
def limpo(texto):
    """Nome do projeto numa linha só e sem crase: não abre seção nem fecha o código do Markdown."""
    return re.sub(r"[\x00-\x1f\x7f`\u2028\u2029]+", " ", texto).encode("utf-8", "replace").decode("utf-8")


def contar(n, um, muitos):
    return "%d %s" % (n, um if n == 1 else muitos)


def ler(trab, nome):
    try:
        with open(os.path.join(trab, nome), encoding="utf-8", errors="replace", newline="") as f:
            return f.read()
    except OSError:
        return ""


def problema_da_ferramenta(trab, nome, estado):
    """None quando a ferramenta rodou e saiu 0; senão o motivo do "não medido"."""
    if estado == "ausente":
        return "%s ausente (não está no PATH) — para medir, instale com `%s` e rode de novo" % (nome, INSTALAR[nome])
    if estado != "0":
        erro = (ler(trab, nome + ".err").strip() or ler(trab, nome + ".out").strip() or "sem mensagem").splitlines()[-1]
        return "%s falhou (exit %s: %s)" % (nome, estado, limpo(erro)[:200])
    return None


def funcoes_do_lizard(texto, pedidos):
    """[(arquivo, nome, complexidade, linhas, parâmetros, início, fim)]; ValueError se a saída não é a esperada."""
    funcoes = []
    for linha in csv.reader(texto.splitlines(keepends=True)):
        if not linha or linha[0] == "NLOC":
            continue
        if len(linha) != COLUNAS_LIZARD:
            raise ValueError("linha com %d colunas" % len(linha))
        arq = linha[6].replace("\\", "/")
        arq = arq[2:] if arq.startswith("./") else arq
        if arq not in pedidos:   # nome que voltou trocado (acento, barra) perderia a função calado
            raise ValueError("arquivo que não pedi: %s" % arq)
        funcoes.append((arq, linha[7], int(linha[1]), int(linha[4]), int(linha[3]),
                        int(linha[9]), int(linha[10])))
    return funcoes


def excessos(funcao, limites):
    medidas = (("complexidade %d", funcao[2], "max_complexidade"), ("%d linhas", funcao[3], "max_linhas"),
               ("%d parâmetros", funcao[4], "max_parametros"))
    return [(valor / limites[chave], (texto + " (limite %d)") % (valor, limites[chave]))
            for texto, valor, chave in medidas if valor > limites[chave]]


def itens_com_teto(itens):
    return ["- " + i for i in itens[:MAX_ITENS]] + (["- e mais %d" % (len(itens) - MAX_ITENS)]
                                                   if len(itens) > MAX_ITENS else [])


def ler_lizard(plano, trab, estado):
    """(funções do diff, None) ou (None, o motivo do "não medido")."""
    if not any(extensao(a) in COM_COMPLEXIDADE for a in plano["medidos"]):
        return None, "nenhum arquivo do diff com linguagem que o lizard mede"
    problema = problema_da_ferramenta(trab, "lizard", estado)
    if problema:
        return None, problema
    try:
        todas = funcoes_do_lizard(ler(trab, "lizard.out"), set(plano["medidos"]))
    except (ValueError, csv.Error) as e:
        return None, "lizard devolveu saída que não entendi (%s)" % limpo(str(e))[:120]
    funcoes = []
    for f in todas:
        if not toca_o_diff(plano["diff"], f[0], f[5], f[6]):
            continue
        funcoes.append(f)
    return (funcoes, None) if funcoes else (None, "nenhuma função nova ou alterada encontrada no diff")


def avisos_de_complexidade(funcoes, limites):
    avisos = []
    for f in funcoes:
        passou = excessos(f, limites)
        if passou:
            avisos.append((-max(p for p, _ in passou), f[0], f[5], "`%s:%d-%d` `%s`: %s" % (
                limpo(f[0]), f[5], f[6], limpo(f[1]), " · ".join(t for _, t in passou))))
    return [a[3] for a in sorted(avisos)]


def medir_complexidade(plano, trab, estado):
    """(linhas da parte, tem aviso, mediu)."""
    sem_suporte = [a for a in plano["medidos"] if extensao(a) not in COM_COMPLEXIDADE]
    nota = ["- fora da medição de complexidade (linguagem sem suporte): " + contar(len(sem_suporte), "arquivo", "arquivos")
            ] if sem_suporte else []
    funcoes, motivo = ler_lizard(plano, trab, estado)
    if motivo:
        return ["- não medido: " + motivo] + nota, False, False
    avisos = avisos_de_complexidade(funcoes, plano["limites"])
    medidas = contar(len(funcoes), "função medida no diff", "funções medidas no diff")
    if not avisos:
        return ["- nenhum aviso (%s)" % medidas] + nota, False, True
    return ["- %s, %d acima do limite:" % (medidas, len(avisos))] + itens_com_teto(avisos) + nota, True, True


def nome_do_jscpd(nome, copia):
    """O nome como o diff o conhece. ValueError se não é um arquivo da cópia: o par sumiria calado."""
    nome = nome.replace("\\", "/")
    for inicio in (copia, os.path.realpath(copia)):
        inicio = inicio.replace("\\", "/").rstrip("/") + "/"
        if nome.startswith(inicio):
            nome = nome[len(inicio):]
    nome = nome[2:] if nome.startswith("./") else nome
    sem_formato = nome.rsplit(":", 1)[0]   # bloco embutido: src/Tela.vue:javascript
    for candidato in (nome, sem_formato):
        if not os.path.isabs(candidato) and os.path.isfile(os.path.join(copia, candidato)):
            return candidato
    raise ValueError("arquivo que não pedi: %s" % nome)


def relatorio_do_jscpd(trab, pasta):
    """(pares, arquivos lidos); ValueError se não é o relatório esperado."""
    texto, copia = ler(trab, "saida-%s/jscpd-report.json" % pasta), os.path.join(trab, pasta)
    try:
        dados = json.loads(texto)
    except RecursionError:
        raise ValueError("relatório aninhado demais")
    try:
        pares, lidos = dados["duplicates"], dados["statistics"]["total"]["sources"]
        if not isinstance(pares, list) or not isinstance(lidos, int):
            raise TypeError("tipos")
        return [(nome_do_jscpd(p["firstFile"]["name"], copia), int(p["firstFile"]["start"]), int(p["firstFile"]["end"]),
                 nome_do_jscpd(p["secondFile"]["name"], copia), int(p["secondFile"]["start"]), int(p["secondFile"]["end"]),
                 int(p["lines"]), int(p.get("tokens", 0))) for p in pares], lidos
    except (KeyError, TypeError, AttributeError, OverflowError) as e:
        raise ValueError("campo ausente ou de outro tipo: %s" % e)


def avisos_de_duplicacao(diff, pares):
    vistos, avisos = set(), []
    for a, a1, a2, b, b1, b2, linhas, tokens in pares:
        if not toca_o_diff(diff, a, a1, a2):   # o lado do diff vem primeiro
            a, a1, a2, b, b1, b2 = b, b1, b2, a, a1, a2
        chave = frozenset(((a, a1, a2), (b, b1, b2)))
        if chave in vistos or not toca_o_diff(diff, a, a1, a2) or not (e_codigo(a) and e_codigo(b)):
            continue
        vistos.add(chave)
        avisos.append((-linhas, a, a1, "`%s:%d-%d` repete `%s:%d-%d` (%d linhas, %d tokens)"
                       % (limpo(a), a1, a2, limpo(b), b1, b2, linhas, tokens)))
    return [a[3] for a in sorted(avisos)]


def medir_duplicacao(plano, trab, estado):
    """(linhas da parte, tem aviso, mediu)."""
    if not plano["medidos"]:
        return ["- não medido: nenhum arquivo do diff dentro do tamanho que o jscpd lê"], False, False
    problema = problema_da_ferramenta(trab, "jscpd", estado)
    if problema:
        return ["- não medido: " + problema], False, False
    try:
        _, do_diff = relatorio_do_jscpd(trab, "diff")
        pares, lidos = relatorio_do_jscpd(trab, "arvore")
    except ValueError as e:
        return ["- não medido: jscpd devolveu saída que não entendi (%s)" % limpo(str(e))[:120]], False, False
    # a prova é por arquivo do diff: ler o resto do projeto não prova que o código novo foi lido
    if do_diff < 1 or lidos < 1:
        return ["- não medido: jscpd não leu nenhum arquivo do diff (todos com menos de %d tokens, ou linguagem que ele "
                "não reconhece)" % plano["limites"]["min_tokens"]], False, False
    lidos_do_diff = min(do_diff, len(plano["medidos"]))   # o jscpd conta de novo o bloco embutido (.vue)
    total = len(plano["medidos"])
    cobertura = "%d de %s do diff" % (lidos_do_diff, contar(total, "arquivo", "arquivos"))
    if lidos_do_diff < total:
        cobertura += "; o jscpd não leu %d: menor que %d tokens, ou que ele não reconhece" % (
            total - lidos_do_diff, plano["limites"]["min_tokens"])
    avisos = avisos_de_duplicacao(plano["diff"], pares)
    if not avisos:
        return ["- nenhum aviso (%s)" % cobertura], False, True
    return ["- %s; %s:" % (cobertura, contar(len(avisos), "trecho repetido", "trechos repetidos"))
            ] + itens_com_teto(avisos), True, True


def secao(trab, estado_lizard, estado_jscpd):
    with open(os.path.join(trab, "plano.json"), encoding="utf-8") as f:
        plano = json.load(f)
    if plano["diff"]:
        partes = [("Complexidade", medir_complexidade(plano, trab, estado_lizard)),
                  ("Duplicação", medir_duplicacao(plano, trab, estado_jscpd))]
    else:
        vazio = (["- não medido: nenhum arquivo de código no diff"], False, False)
        partes = [("Complexidade", vazio), ("Duplicação", vazio)]
    print("## Qualidade (avisos)\n")
    print("> Só o código novo ou alterado desde `%s` (%s). Aviso: não reprova.\n" % (limpo(plano["ref"]), plano["base"][:7]))
    for titulo, (linhas, _, _) in partes:
        print("### %s\n\n%s\n" % (titulo, "\n".join(linhas)))
    if plano["fora"]:
        print("- não medido: %s (acima de 5 MB ou sem permissão de leitura), nem como par de comparação: %s\n" % (
            contar(len(plano["fora"]), "arquivo", "arquivos"), ", ".join("`%s`" % limpo(a) for a in plano["fora"][:3])))
    tem_aviso, mediu_tudo = any(p[1][1] for p in partes), all(p[1][2] for p in partes) and not plano["fora"]
    palavra = "AVISOS" if tem_aviso else "NADA ACHADO" if mediu_tudo else "NÃO MEDIDO"
    print("RESULTADO: %s\n→ cole a seção no BUILD_REPORT; ela avisa e não reprova." % palavra, file=sys.stderr)


try:
    if sys.argv[1] == "preparar":
        preparar(*sys.argv[2:5])
    else:
        secao(*sys.argv[2:5])
except (Uso, OSError) as e:
    print("🛑 metricas-diff: %s" % limpo(str(e)), file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ %s; nada foi medido." % getattr(e, "conserto", "confira a pasta e rode de novo"),
          file=sys.stderr)
    sys.exit(64)
PY

PLANO="$(python3 -B "${TRAB}/nucleo.py" preparar "${RAIZ}" "${TRAB}" "${BASE}")" || exit 64
read -r MIN_TOKENS N_LIZARD N_JSCPD <<EOF
${PLANO}
EOF

E_LIZARD="sem-alvo"; E_JSCPD="sem-alvo"
if [ "${N_LIZARD}" -gt 0 ]; then
  E_LIZARD="ausente"
  if command -v lizard >/dev/null 2>&1; then
    ( cd "${TRAB}/arvore" && PYTHONUTF8=1 xargs -0 -n 50 lizard --csv < "${TRAB}/lizard.lista" ) >"${TRAB}/lizard.out" 2>"${TRAB}/lizard.err"
    E_LIZARD=$?
  fi
fi
roda_jscpd() {   # $1 = a pasta da cópia (diff ou arvore). Teto alto: o jscpd pula calado o arquivo acima do padrão dele
  mkdir "${TRAB}/saida-${1}" && ( cd "${TRAB}/${1}" && jscpd . --min-tokens "${MIN_TOKENS}" --max-lines 1000000 --max-size 6mb \
    --reporters json --output "${TRAB}/saida-${1}" --config "${TRAB}/jscpd.vazio.json" --silent ) \
    </dev/null >"${TRAB}/jscpd.out" 2>"${TRAB}/jscpd.err"
}
if [ "${N_JSCPD}" -gt 0 ]; then
  E_JSCPD="ausente"
  if command -v jscpd >/dev/null 2>&1; then
    roda_jscpd diff; E_JSCPD=$?
    if [ "${E_JSCPD}" = 0 ]; then roda_jscpd arvore; E_JSCPD=$?; fi
  fi
fi

python3 -B "${TRAB}/nucleo.py" secao "${TRAB}" "${E_LIZARD}" "${E_JSCPD}"
