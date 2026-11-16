#!/usr/bin/env bash
# eval-revisores.sh — custo e resultado de cada engine nas revisões adversariais que o projeto JÁ fez: lê as pastas
# EXTERNAL_REVIEW_*/ (META.txt + os arquivos de vereditos) e os ledgers da revisão (LEDGER_REVISAO_*.md) e imprime
# uma linha por papel + engine + modelo: rodadas, falhas por motivo, custo pago, custo nominal, achados, aplicados,
# com dano, falsos positivos, fora de escopo, sem classificar, custo por falha com dano e taxa de AGREE.
# Doc: docs/adversarial-review.md. Critério de dano: sdd/review/CRITERIO_DANO.md.
#
# Por que existe: escolher a cadeia de revisão por evidência, não por impressão. O script CONTA o que está
# registrado; não julga e não recomenda. Nunca chama engine e nunca usa rede: só lê arquivos.
#
# USO-INICIO
#   eval-revisores.sh [<pasta-das-revisões>] [--ledgers <pasta-ou-arquivo>] [--registry <registry.tsv>]
#                     [--precos <pasta>]
#       --precos: pasta com precos.tsv e precos-cache.tsv (fora do pacote); com ela, o papel por assinatura que
#                 não informa custo ganha o nominal estimado (≈), com o cache à parte (F23B3); sem ela, n/d
#       Cadeia por frente (F23B3): uma linha por ledger — rodadas, 2º revisor por risco e por raso, evitado pela
#                 regra (a regra antiga o chamaria) e o custo dele, dispensas à mão, escapes com dano e o aviso de
#                 revisar a regra quando houve escape numa frente com o 2º revisor dispensado pela regra
#       pasta: padrão review.output_dir do sdd/config.yaml da raiz git (sdd/reports/reviews se vazio)
#       --ledgers: padrão sdd/reviews da raiz git; numa pasta, lê os LEDGER_REVISAO_*.md
#       --registry: padrão review.registry do config, senão sdd/review/registry.tsv, senão o do pacote
#       pago    = custo numérico das chamadas de engine pay-per-token (o que saiu do saldo)
#       nominal = todo custo numérico, reportado ou estimado (≈), inclusive o de engine por assinatura
#       n/d     = chamada sem custo informado (assinatura sem valor, $?): nunca conta como zero
#       incerto = custo `US$ n + $?` (a engine estourou o tempo): o n entra na soma e a linha avisa
#       falhas  = chamadas com exit ≠ 0, por motivo; "trocada" = a engine prevista falhou e outra respondeu
#                 (o custo da tentativa que falhou fica na linha da engine que respondeu: o META.txt não o separa)
#       fora da conta = o que não entrou nos números, com o motivo (linha de ledger sem par, pasta ilegível…)
#       0 MEDIDO · 2 SEM DADOS (nenhuma pasta com META.txt legível, ou a pasta padrão ainda não existe)
#       64 uso, ou pasta/arquivo passado não existe
#       limites: o medidor soma o que o META.txt e o ledger dizem, sem conferir (rode o ledger-revisao-lint.sh
#       antes: um `sim` conta como dano mesmo sem `teste:`); papel sem engine ou sem exit no META.txt não ganha
#       linha (se tem custo, vai para fora da conta); arquivo de vereditos com linha cortada ou sem o campo
#       `achado` conta só as linhas inteiras; os valores
#       são somados exatos e arredondados só na hora de imprimir (4 casas; percentual, 1 casa)
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
  echo "🛑 eval-revisores: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_EVAL_BIN="$(cd "${_sdd_bin}" && { pwd -W 2>/dev/null || pwd; })"   # F16W2: sem dirname; no Windows, C:/… (o Python nativo lê)
export SDD_EVAL_BIN

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import json, os, re, subprocess, sys
from decimal import Decimal

BIN = os.environ["SDD_EVAL_BIN"]
PAPEIS = (("reviewer", "revisor", "reviewer.verdicts.jsonl"),
          ("revisor2", "2º revisor", "reviewer2.verdicts.jsonl"),
          ("auditor", "auditor", "auditor.verdicts.jsonl"),
          ("desempate", "desempate", None))
ORDEM = {nome: i for i, (_, nome, _) in enumerate(PAPEIS)}
MOTIVO = {65: "credencial", 67: "cota ou tempo", 68: "resposta inválida"}
TROCADA = "trocada por outra engine"
VEREDITOS = ("APLICADA", "REBATIDA_EVIDENCIA", "REBATIDA_ESCOPO")
PASTA = r"EXTERNAL_REVIEW_\d{8}-\d{6}(?:-\d+)?"
PASTA_RE = re.compile("^" + PASTA + "$")
SEM_ACHADOS_RE = re.compile(r"^\s*sem achados:\s*rodada=(?:\d+[a-z]?|D\d+)\s+(" + PASTA + r")\s*$")
CUSTO_RE = re.compile(r"^(≈)?\s*US\$\s*([0-9]{1,12}(?:[.,][0-9]{1,12})?)(\s*\+\s*\$\?)?$")
SEPARADOR_RE = re.compile(r"^:?-+:?$")
CABECALHO = ["achado", "sev", "veredito", "rodada", "evidência", "dano", "revisão"]
# Cerca como no CommonMark: abre com 3 ou mais crases ou tis e qualquer rótulo (```c#, ```sh title=x, ````);
# fecha com o mesmo caractere, em quantidade igual ou maior, sem rótulo. Código em linha (```x```) não abre.
CERCA_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SOLTA_RE = re.compile(r"^[\s>*\\\u200b\ufeff-]*")


# >>> linhas-especiais (a MESMA leitura está no ledger-revisao-lint.sh e no eval-revisores.sh; um teste compara)
# F23B3: as linhas fora da tabela que fecham a conta da frente. `rodada=D<n>` é a revisão do DESIGN.
RODADA_RE = re.compile(r"^rodada=(?:\d+[a-z]?|D\d+)\Z")
TRAVESSAO = r"\s*(?:—|–|-{1,2})\s*"
SEM_RESULTADO_RE = re.compile(r"^\s*sem resultado:\s*(rodada=(?:\d+[a-z]?|D\d+))\s+(" + PASTA + r")" + TRAVESSAO
                              + r"(\S.{2,}?)\s*\Z")
ESCAPOU_RE = re.compile(r"^\s*escapou:\s*commit=([0-9a-f]{7,40})\s*·\s*teste:\s*`?([^`·\s][^`·]*?)`?\s*·\s*"
                        r"dano=(\S+)" + TRAVESSAO + r"(\S.{2,}?)\s*\Z")
TESTE_ESCAPOU_RE = re.compile(r"^(?:[\w./-]+::[\w.:-]+|(?:\w+\.)*test_\w+(?:\.py)?(?:::[\w.:-]+)?|tests/[\w./-]+)\Z")
DANOS_ESCAPOU = ("dado", "dinheiro", "acesso", "publicação", "disponibilidade")
QUASE_RE = re.compile(r"^\s*[-*>]*\s*\**(sem resultado|escapou)\b", re.I)


def linha_especial(ln):
    """('sem resultado', rodada, pasta) · ('escapou', commit, teste, dano) · ('quase', motivo) · None."""
    m = SEM_RESULTADO_RE.match(ln)
    if m:
        return ("sem resultado", m.group(1), m.group(2))
    m = ESCAPOU_RE.match(ln)
    if m:
        if m.group(3) not in DANOS_ESCAPOU:
            return ("quase", "escape com dano `%s` fora de %s" % (m.group(3), ", ".join(DANOS_ESCAPOU)))
        if not TESTE_ESCAPOU_RE.match(m.group(2)):
            return ("quase", "escape com teste `%s` fora da forma test_…, arquivo::teste ou tests/…" % m.group(2))
        return ("escapou", m.group(1), m.group(2), m.group(3))
    q = QUASE_RE.match(ln)
    if q and q.group(1).lower() == "sem resultado":
        return ("quase", "rodada sem resultado se escreve `sem resultado: rodada=<N ou D<n>> "
                         "EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS> — <motivo>`")
    if q:
        return ("quase", "escape se escreve `escapou: commit=<sha> · teste: <nome> · dano=<dado, dinheiro, acesso, "
                         "publicação ou disponibilidade> — <onde apareceu>`")
    return None
# <<< linhas-especiais


# >>> nominal-estimado (a MESMA função está no eval-revisores.sh e no custo-feature.sh; um teste compara)
def nominal_estimado(meta, papel, precos, cache):
    """Decimal ou None: entrada×p_entrada + lido×p_lido + criado×p_criado + saída×p_saída, por milhão de tokens.

    Para papel cobrado por assinatura, que não informa custo (F23B3). O adaptador grava a entrada já sem o cache
    (significado da B1); campo `-` (inclusive o cache criado que ninguém mediu), modelo `-` ou preço ausente = None,
    que nunca vira zero. precos: (engine, modelo) → (entrada, saída); cache: (engine, modelo) → (lido, criado)."""
    eng = (meta.get(papel + "_engine_efetivo") or meta.get(papel + "_engine") or "").split(":", 1)[0]
    modelo = meta.get(papel + "_modelo", "-")
    num = [meta.get(papel + k, "-") for k in ("_tokens_entrada", "_tokens_cache_lido", "_tokens_cache_criado",
                                              "_tokens_saida")]
    if modelo in ("", "-", "n/d") or not all(re.match(r"^\d{1,12}\Z", x) for x in num):
        return None
    p, c = precos.get((eng, modelo)), cache.get((eng, modelo))
    ent, lido, criado, sai = (Decimal(x) for x in num)
    if p is None or ((lido or criado) and c is None):
        return None
    return (ent * p[0] + sai * p[1] + (lido * c[0] + criado * c[1] if c else 0)) / Decimal(1000000)
# <<< nominal-estimado


def linhas_uteis(texto):
    """As linhas do arquivo como (n, texto, dentro), e os avisos (n, motivo) de bloco que abriu e não fechou.
    `dentro` diz que a linha está num bloco cercado ou num comentário <!-- -->: ali as marcas de texto
    (`retroativo: sim`, `sem achados:`) não valem, mas uma linha de tabela é conferida do mesmo jeito, porque o
    `sdd-fluxo.sh loop` a lê. A mesma função está no ledger-revisao-lint.sh e no eval-revisores.sh."""
    linhas, avisos, cercado, comentario, onde = [], [], "", False, 0
    for n, ln in enumerate(texto.lstrip("﻿").split("\n"), 1):
        ln = ln.rstrip("\r")
        if comentario:
            linhas.append((n, ln, True))
            comentario = "-->" not in ln
            continue
        m = CERCA_RE.match(ln)
        if cercado:
            if m and m.group(1)[0] == cercado[0] and len(m.group(1)) >= len(cercado) and not m.group(2).strip():
                cercado = ""
            else:
                linhas.append((n, ln, True))
            continue
        if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
            cercado, onde = m.group(1), n
            continue
        if ln.lstrip().startswith("<!--"):
            comentario, onde = "-->" not in ln, n
            continue
        linhas.append((n, ln, False))
    if cercado:
        avisos.append((onde, "bloco cercado aberto e não fechado: as marcas de texto depois dele não valem"))
    if comentario:
        avisos.append((onde, "comentário <!-- aberto e não fechado: as marcas de texto depois dele não valem"))
    return linhas, avisos


def linha_solta(ln):
    """Uma linha que não começa por `|` mas tem forma de linha do ledger: a barra inicial atrás de citação, item de
    lista ou barra invertida, ou 4 ou mais barras verticais. Ela não é lida como tabela; por isso é acusada."""
    resto = SOLTA_RE.sub("", ln, count=1)
    return resto.startswith("|") or len(re.findall(r"(?<!\\)\|", ln)) >= 4


def para(motivo):
    print("🛑 eval-revisores: " + motivo, file=sys.stderr)
    print("RESULTADO: PAROU\n→ rode `eval-revisores.sh --help` para ver o uso.", file=sys.stderr)
    sys.exit(64)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def raiz_git():
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()
    except OSError:
        return os.getcwd()


def slot_review(raiz, chave):
    """Valor de review.<chave> no sdd/config.yaml da raiz, ou ''."""
    valor, no_bloco = "", False
    for ln in (ler(os.path.join(raiz, "sdd/config.yaml")) or "").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if re.match(r"^\S", ln):
            no_bloco = ln.split("#", 1)[0].strip() == "review:"
            continue
        m = re.match(r"^\s+" + re.escape(chave) + r"\s*:\s*(.*?)\s*$", ln)
        if no_bloco and m:
            valor = m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
    return valor


def listar(pasta):
    """Os nomes de uma pasta, em ordem; pasta que não se deixa ler é erro de uso, nunca traceback."""
    try:
        return sorted(os.listdir(pasta))
    except OSError as e:
        para("não consegui ler a pasta %s (%s)" % (pasta, e.strerror or "erro de leitura"))


def celulas(ln):
    """As células de uma linha de tabela, pelo mesmo corte do ledger-revisao-lint.sh."""
    c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)][1:]
    if c and c[-1] == "":
        c = c[:-1]
    return c


def rotulo(engine):
    """O rótulo que o adversarial-review.sh põe depois do @: o id da engine com : e / trocados por -."""
    return re.sub(r"[:/]", "-", engine)


for s in (sys.stdout, sys.stderr):   # a saída tem acento: nunca depende do locale de quem roda
    try:
        s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


LENDO = ["os argumentos"]   # o que estava sendo lido, para a mensagem de erro inesperado dizer onde


def inesperado(tipo, valor, tb):
    """Dado corrompido que nenhuma checagem previu vira 64 com a causa, nunca traceback."""
    print("🛑 eval-revisores: não consegui medir (%s: %s), lendo %s" % (tipo.__name__, str(valor)[:200], LENDO[0]),
          file=sys.stderr)
    print("RESULTADO: PAROU\n→ esse arquivo tem um valor que o script não sabe ler: corrija-o ou tire a pasta dele "
          "da medição, e rode de novo.", file=sys.stderr)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(64)


sys.excepthook = inesperado

# ── argumentos ──────────────────────────────────────────────────────────────────────────────────────
args, pasta_arg, ledgers_arg, registry_arg, precos_arg = sys.argv[1:], None, None, None, None
i = 0
while i < len(args):
    a = args[i]
    if a in ("--ledgers", "--registry", "--precos"):
        if i + 1 >= len(args) or args[i + 1].startswith("--") or not args[i + 1]:
            para("%s pede um caminho" % a)
        if a == "--ledgers":
            ledgers_arg = args[i + 1]
        elif a == "--precos":
            precos_arg = args[i + 1]
        else:
            registry_arg = args[i + 1]
        i += 2
        continue
    if a.startswith("-"):
        para("opção desconhecida: " + a)
    if pasta_arg is not None:
        para("argumento a mais: " + a)
    if not a:
        para("o caminho da pasta veio vazio")
    pasta_arg = a
    i += 1

raiz = raiz_git()
if pasta_arg is not None:
    pasta = os.path.abspath(pasta_arg)
    if not os.path.isdir(pasta):
        para("a pasta %s não existe" % pasta)
else:
    rel = slot_review(raiz, "output_dir") or "sdd/reports/reviews"
    pasta = rel if os.path.isabs(rel) else os.path.join(raiz, rel)

if ledgers_arg is not None:
    ledgers = os.path.abspath(ledgers_arg)
    if not os.path.exists(ledgers):
        para("o caminho de --ledgers não existe: %s" % ledgers)
else:
    ledgers = os.path.join(raiz, "sdd/reviews")

if registry_arg is not None:
    registry = os.path.abspath(registry_arg)
    if not os.path.isfile(registry):
        para("o arquivo de --registry não existe: %s" % registry)
else:
    rel = slot_review(raiz, "registry") or "sdd/review/registry.tsv"
    registry = rel if os.path.isabs(rel) else os.path.join(raiz, rel)
    if not os.path.isfile(registry):
        registry = os.path.normpath(os.path.join(BIN, "..", "review", "registry.tsv"))

# ── F23B3: tarifas para o nominal estimado de engine por assinatura (só com --precos; fora do pacote) ────
PRECOS_EST, CACHE_EST = {}, {}
if precos_arg is not None:
    dir_precos = os.path.abspath(precos_arg)
    if not os.path.isdir(dir_precos):
        para("a pasta de --precos não existe: %s" % dir_precos)
    for nome_tab, alvo in (("precos.tsv", PRECOS_EST), ("precos-cache.tsv", CACHE_EST)):
        for ln in (ler(os.path.join(dir_precos, nome_tab)) or "").splitlines():
            c = ln.split("\t")
            if ln.startswith("#") or len(c) < 4:
                continue
            try:
                alvo[(c[0].strip(), c[1].strip())] = (Decimal(c[2].strip()), Decimal(c[3].strip()))
            except ArithmeticError:
                continue   # preço ilegível = sem preço: o papel sai n/d, nunca zero

# ── registry: engine → cobrança ─────────────────────────────────────────────────────────────────────
cobranca = {}
for ln in (ler(registry) or "").splitlines():
    if not ln.strip() or ln.startswith("#"):
        continue
    c = ln.split("\t")
    if len(c) >= 4:
        cobranca[c[0]] = c[3]

# ── ledgers ─────────────────────────────────────────────────────────────────────────────────────────
# O arquivo é só do ledger: toda linha de tabela, fora de bloco cercado e de comentário, é o cabeçalho do molde ou
# um achado. Toda linha que não entra na conta vai para "fora da conta" com arquivo:linha e o motivo.
fora, linhas_ledger, n_ledgers, pastas_citadas, ditas_sem_achados = [], [], 0, set(), {}
ditas_sem_resultado, pastas_frente, escapes = {}, {}, {}   # F23B3: frente = o ledger (LEDGER_REVISAO_<frente>.md)
arquivos = []
if os.path.isdir(ledgers):
    arquivos = [os.path.join(ledgers, f) for f in listar(ledgers)
                if f.startswith("LEDGER_REVISAO_") and f.endswith(".md")]
elif os.path.isfile(ledgers):
    arquivos = [ledgers]
for arq in arquivos:
    LENDO[0] = arq
    texto = ler(arq)
    nome_arq = os.path.basename(arq)
    if texto is None:
        fora.append((nome_arq, "ledger ilegível"))
        continue
    n_ledgers += 1
    frente = re.sub(r"^LEDGER_REVISAO_|\.md$", "", nome_arq)
    da_frente = pastas_frente.setdefault(frente, set())
    escapes.setdefault(frente, 0)
    uteis, abertos = linhas_uteis(texto)
    for n, motivo in abertos:
        fora.append(("%s:%d" % (nome_arq, n), motivo))
    for n, ln, dentro in uteis:
        if not re.match(r"^\s*\|", ln):
            if dentro:
                continue   # texto de exemplo ou de comentário: só linha de tabela conta ali dentro
            m = SEM_ACHADOS_RE.match(ln)
            e = None if m else linha_especial(ln)
            if m:
                pastas_citadas.add(m.group(1))
                da_frente.add(m.group(1))
                ditas_sem_achados.setdefault(m.group(1), "%s:%d" % (nome_arq, n))
            elif e and e[0] == "sem resultado":
                pastas_citadas.add(e[2])
                da_frente.add(e[2])
                ditas_sem_resultado.setdefault(e[2], "%s:%d" % (nome_arq, n))
            elif e and e[0] == "escapou":
                escapes[frente] += 1
            elif e:
                fora.append(("%s:%d" % (nome_arq, n), e[1] + ": a linha não foi lida"))
            elif linha_solta(ln):
                fora.append(("%s:%d" % (nome_arq, n), "linha com forma de linha do ledger fora da tabela (não começa "
                                                     "por `|`): não foi lida. Em texto corrido, escape cada "
                                                     "barra com `\\|` ou use um bloco cercado"))
            continue
        c = celulas(ln)
        if not c or all(SEPARADOR_RE.match(x) for x in c):
            continue
        nomes = [x.strip("*` ").lower() for x in c]
        if nomes == CABECALHO:
            continue
        if nomes[0] == "achado" or nomes[0].startswith("achado "):
            fora.append(("%s:%d" % (nome_arq, n), "cabeçalho fora do molde (ou linha cuja 1ª célula começa por "
                                                 "`achado`): não foi lida como achado"))
            continue
        onde = "%s:%d" % (nome_arq, n)
        if len(c) != 7:
            fora.append((onde, "linha com %d célula(s), o ledger tem 7 (rode o ledger-revisao-lint.sh)" % len(c)))
        elif c[2] not in VEREDITOS:
            fora.append((onde, "veredito `%s` fora da lista" % c[2]))
        elif not PASTA_RE.match(c[6]):
            fora.append((onde, "revisão `%s` não é uma pasta EXTERNAL_REVIEW_*" % c[6]))
        elif c[5] not in ("sim", "nao", "?"):
            fora.append((onde, "dano `%s` fora de sim, nao, ?" % c[5]))
        else:
            pastas_citadas.add(c[6])
            da_frente.add(c[6])
            linhas_ledger.append({"pasta": c[6], "id": c[0], "veredito": c[2], "dano": c[5], "onde": onde,
                                  "usada": False, "motivo": ""})


def ids_do(arquivo, so_novo=False):
    """Ids de achado de um arquivo de vereditos, na ordem, sem repetir. None se o arquivo não existe."""
    texto = ler(arquivo)
    if texto is None:
        return None
    ids = []
    for ln in texto.splitlines():
        try:
            v = json.loads(ln) or {}
        except ValueError:
            continue
        if not isinstance(v, dict) or not isinstance(v.get("achado"), str) or not v["achado"]:
            continue   # linha sem id de texto não é um achado
        if so_novo and v.get("veredito") != "NOVO":
            continue
        if v["achado"] not in ids:
            ids.append(v["achado"])
    return ids


def custo_de(valor):
    """(Decimal ou None, estimado?, incerto?) de um campo *_custo do META.

    `US$ n` reportado · `≈US$ n` estimado pela tabela de preços · `US$ n + $?` a engine estourou o tempo e o
    resto é desconhecido · `assinatura`, `$?`, `n/d` → sem custo informado (None), que nunca vira zero."""
    m = CUSTO_RE.match((valor or "").strip())
    if not m:
        return None, False, False
    return Decimal(m.group(2).replace(",", ".")), bool(m.group(1)), bool(m.group(3))


def linha_de(por, nome, engine, modelo):
    base = engine.split(":", 1)[0]
    if modelo in ("", "-", "n/d"):
        modelo = engine.split(":", 1)[1] if ":" in engine else "-"
    return por.setdefault((nome, "%s (%s)" % (base, modelo)), {
        "rodadas": 0, "falhas": {}, "pago": Decimal(0), "nominal": Decimal(0), "estimado": False, "chamadas": 0,
        "sem_custo": 0, "incerto": 0, "achados": 0, "aplicados": 0, "dano": 0, "fp": 0, "escopo": 0,
        "sem_class": 0, "agree": 0, "dis": 0, "cobranca": cobranca.get(base, "desconhecida")})


# ── pastas ──────────────────────────────────────────────────────────────────────────────────────────
por, lidas, sem_ledger, metas = {}, 0, [], {}
for d in (listar(pasta) if os.path.isdir(pasta) else []):
    caminho = os.path.join(pasta, d)
    if not d.startswith("EXTERNAL_REVIEW_") or not os.path.isdir(caminho):
        continue
    LENDO[0] = caminho
    meta = {}
    for ln in (ler(os.path.join(caminho, "META.txt")) or "").splitlines():
        m = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if m:
            meta[m.group(1)] = m.group(2)
    if not meta.get("reviewer_engine_efetivo"):
        fora.append((d, "META ilegível ou incompleto"))
        continue
    lidas += 1
    metas[d] = meta
    do_ledger = [x for x in linhas_ledger if x["pasta"] == d]
    if d not in pastas_citadas:
        sem_ledger.append(d)
    ids_papel, engine_papel = {}, {}
    for chave, nome, arq in PAPEIS:
        if arq:
            ids_papel[chave] = ids_do(os.path.join(caminho, arq), so_novo=(chave == "auditor"))
    for dita, rotulo_dito in ((ditas_sem_achados, "sem achados"), (ditas_sem_resultado, "sem resultado")):
        if d in dita:
            n_ids = sum(len(lista or []) for lista in ids_papel.values())
            if n_ids:
                fora.append((dita[d], "o ledger diz `%s` para %s, mas a revisão tem %d achado(s): eles ficam em "
                                      "sem classificar" % (rotulo_dito, d, n_ids)))
    bases = {}   # id sem o rótulo → papéis que têm um id com essa base nesta pasta
    for p2, lista in ids_papel.items():
        for x in (lista or []):
            bases.setdefault(x.split("@", 1)[0], set()).add(p2)
    for chave, nome, arq in PAPEIS:
        if chave == "desempate":
            engine = meta.get("desempate_engine", "")
        else:
            engine = meta.get(chave + "_engine_efetivo") or meta.get(chave + "_engine") or ""
        saida = meta.get(chave + "_exit", "")
        if engine in ("", "-"):
            if meta.get(chave + "_custo", "") not in ("", "-", "n/d"):
                bruto = meta[chave + "_custo"]
                fora.append((d, "%s: sem engine no META.txt e com custo `%s`; a chamada e o custo dela não foram "
                             "contados" % (nome, bruto[:40] + ("…" if len(bruto) > 40 else ""))))
            continue   # o papel não rodou nesta pasta
        if engine == "indisponível":   # antes do exit: com ou sem exit gravado, o papel não chamou engine
            fora.append((d, "%s indisponível: nenhuma engine foi chamada" % nome))
            continue
        if saida in ("", "-"):
            if meta.get(chave + "_custo", "") not in ("", "-", "n/d"):
                fora.append((d, "%s (%s): sem exit no META.txt e com custo `%s`; a chamada e o custo dela não foram "
                             "contados" % (nome, engine, meta[chave + "_custo"])))
            continue   # o papel não rodou nesta pasta
        if not re.match(r"^-?\d{1,6}$", saida):
            fora.append((d, "%s (%s): exit `%s` ilegível no META.txt; a chamada e o custo dela não foram contados"
                         % (nome, engine, saida[:40] + ("…" if len(saida) > 40 else ""))))
            continue
        # a engine prevista falhou e outra respondeu: a falha é da prevista
        prevista = meta.get(chave + "_engine_default", "")
        if meta.get(chave + "_fallback_usado") == "sim" and prevista not in ("", "-", engine):
            f = linha_de(por, nome, prevista, "")
            f["falhas"][TROCADA] = f["falhas"].get(TROCADA, 0) + 1
        c = linha_de(por, nome, engine, meta.get(chave + "_modelo", ""))
        c["chamadas"] += 1
        bruto = (meta.get(chave + "_custo") or "").strip()
        valor, estimado, incerto = custo_de(bruto)
        if valor is None and bruto == "assinatura" and PRECOS_EST:
            v = nominal_estimado(meta, chave, PRECOS_EST, CACHE_EST)   # F23B3: com --precos
            if v is not None:
                valor, estimado = v, True
        if valor is None:
            c["sem_custo"] += 1
            if "US$" in bruto:   # tem cara de valor e não é um: avisa, em vez de virar "n/d" calado
                fora.append((d, "%s (%s): custo `%s` ilegível, contado como sem custo informado"
                             % (nome, engine, bruto[:40] + ("…" if len(bruto) > 40 else ""))))
        else:
            c["nominal"] += valor
            c["estimado"] = c["estimado"] or estimado
            c["incerto"] += 1 if incerto else 0
            if c["cobranca"] == "pay-per-token":
                c["pago"] += valor
        if int(saida) != 0:
            motivo = MOTIVO.get(int(saida), "outro")
            c["falhas"][motivo] = c["falhas"].get(motivo, 0) + 1
            continue
        c["rodadas"] += 1
        if chave == "auditor":
            for ln in (ler(os.path.join(caminho, arq)) or "").splitlines():
                try:
                    v = (json.loads(ln) or {}).get("veredito")
                except (ValueError, AttributeError):
                    continue
                if v == "AGREE":
                    c["agree"] += 1
                elif v in ("DISAGREE_EVIDENCE", "DISAGREE_CONCERN"):
                    c["dis"] += 1
        if arq and ids_papel.get(chave) is None:
            fora.append((d, "%s respondeu (exit 0) e a pasta não tem %s: contado com 0 achados" % (nome, arq)))
        ids = ids_papel.get(chave) or []
        c["achados"] += len(ids)
        aceitos = (rotulo(engine), engine, engine.split(":", 1)[0])   # o rótulo do script, o id cru, a engine base
        consumidos, classificados = {}, set()
        for x in do_ledger:
            if x["usada"]:
                continue
            alvo = None
            if x["id"] in ids:
                alvo = x["id"]
            else:
                # id com rótulo no ledger e sem rótulo no arquivo de vereditos (rodada de um revisor só, ou NOVO
                # do auditor): casa pela base quando ela é de um papel só e o rótulo é o da engine deste papel
                b, _, rot = x["id"].partition("@")
                if rot and bases.get(b) == {chave} and b in ids:
                    if rot in aceitos:
                        alvo = b
                    else:
                        x["motivo"] = "o rótulo @%s não é o da engine que respondeu como %s (%s)" % (rot, nome, engine)
                elif not rot:
                    # o sentido inverso, que o loop também aceita: ledger sem rótulo, arquivo com rótulo. Só casa
                    # quando um único achado da pasta tem essa base; com dois revisores (R2@a e R2@b) é ambíguo
                    donos = [y for lista in ids_papel.values() for y in (lista or []) if y.split("@", 1)[0] == b]
                    if len(donos) == 1 and donos[0] in ids:
                        alvo = donos[0]
                    elif len(donos) > 1 and any(y in ids for y in donos):
                        x["motivo"] = "sem rótulo e ambíguo: a revisão tem %s; copie o id com o @engine" % ", ".join(donos)
            if alvo is None:
                continue
            x["usada"] = True
            if alvo in consumidos:
                x["motivo"] = "repetido (1ª vez em %s)" % consumidos[alvo]
                fora.append((x["onde"], "achado %s %s" % (x["id"], x["motivo"])))
                continue
            consumidos[alvo] = x["onde"]
            if x["veredito"] == "APLICADA":
                c["aplicados"] += 1
            elif x["veredito"] == "REBATIDA_EVIDENCIA":
                c["fp"] += 1
            else:
                c["escopo"] += 1
            if x["dano"] == "sim" and x["veredito"] == "APLICADA":
                c["dano"] += 1
            elif x["dano"] == "sim":
                fora.append((x["onde"], "achado %s: dano = sim com veredito %s não conta como falha com dano"
                             % (x["id"], x["veredito"])))
            if x["dano"] in ("sim", "nao"):
                classificados.add(alvo)
        c["sem_class"] += len(ids) - len(classificados)

for x in linhas_ledger:
    if not x["usada"]:
        fora.append((x["onde"], x["motivo"] and "achado %s: %s" % (x["id"], x["motivo"])
                     or "achado %s não está em %s" % (x["id"], x["pasta"])))
if sem_ledger and not n_ledgers:
    fora.append(("ledgers", "nenhum ledger lido: os achados das %d pasta(s) ficam em sem classificar" % len(sem_ledger)))
else:
    for d in sem_ledger:
        fora.append((d, "sem linha em nenhum ledger: os achados dela ficam em sem classificar"))

LENDO[0] = "a tabela já somada (erro ao imprimir)"
print("eval-revisores — custo e resultado por papel, engine e modelo (%d pasta(s) lida(s) em %s; %d ledger(s))"
      % (lidas, pasta, n_ledgers))
if not por:
    if fora:
        print("fora da conta: %d (%s)" % (len(fora), "; ".join("%s: %s" % x for x in fora)))
    print("RESULTADO: SEM DADOS")
    print("→ nenhuma revisão com META.txt legível nesta pasta: rode adversarial-review.sh e meça de novo.")
    sys.exit(2)


def numero(valor):
    """4 casas; custo menor que 0,0001 sai com 6, para não virar 0.0000."""
    if Decimal(0) < valor < Decimal("0.000001"):
        return "<0.000001"   # custo que existe nunca aparece como zero
    casas = "0.000001" if Decimal(0) < valor < Decimal("0.0001") else "0.0001"
    return str(valor.quantize(Decimal(casas)))


def ressalva(c):
    partes = []
    if c["sem_custo"]:
        partes.append("n/d em %d de %d" % (c["sem_custo"], c["chamadas"]))
    if c["incerto"]:
        partes.append("incerto em %d de %d" % (c["incerto"], c["chamadas"]))
    return (" (" + ", ".join(partes) + ")") if partes else ""


def dinheiro(valor, c):
    if c["chamadas"] == c["sem_custo"]:
        return "n/d"
    return ("≈" if c["estimado"] else "") + numero(valor) + ressalva(c)


def por_dano(valor, c):
    if not c["dano"] or c["chamadas"] == c["sem_custo"]:
        return "—"
    return ("≈" if c["estimado"] else "") + numero(valor / c["dano"]) + (" (parcial)" if ressalva(c) else "")


print("")
print("| Papel | Engine (modelo) | Cobrança | Rodadas | Falhas | Pago US$ | Nominal US$ | Achados | Aplicados | "
      "Com dano | Falsos positivos | Fora de escopo | Sem classificar | Pago por dano | Nominal por dano | AGREE |")
print("|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for quem in sorted(por, key=lambda q: (ORDEM[q[0]], q[1])):
    c = por[quem]
    falhas = "0"
    if c["falhas"]:
        falhas = "%d (%s)" % (sum(c["falhas"].values()),
                              ", ".join("%d %s" % (c["falhas"][m], m) for m in sorted(c["falhas"])))
    if c["cobranca"] == "pay-per-token":
        pago, pago_dano = dinheiro(c["pago"], c), por_dano(c["pago"], c)
    elif c["cobranca"] == "assinatura":
        pago, pago_dano = "0.0000", ("0.0000" if c["dano"] else "—")
    else:
        pago, pago_dano = "n/d", "—"
    agree = "—"
    if quem[0] == "auditor":
        total = c["agree"] + c["dis"]
        agree = ("%.1f%% (%d de %d)" % (100.0 * c["agree"] / total, c["agree"], total)) if total else "n/a"

    def de(n):
        return "%d de %d" % (n, c["achados"]) if c["achados"] else "0"

    print("| %s | %s | %s | %d | %s | %s | %s | %d | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        quem[0], quem[1], c["cobranca"], c["rodadas"], falhas, pago, dinheiro(c["nominal"], c), c["achados"],
        de(c["aplicados"]), de(c["dano"]), de(c["fp"]), de(c["escopo"]), de(c["sem_class"]), pago_dano,
        por_dano(c["nominal"], c), agree))
# ── F23B3: a cadeia por frente — 2º revisor por risco e por raso, evitado pela regra, dispensas à mão, escapes ──
SEM_RISCO = "diff sem gatilho de risco — 1 revisor"
avisos_regra = []
if any(pastas_frente.get(f) for f in pastas_frente):
    print("")
    print("Cadeia por frente (o 2º revisor só por risco ou revisor raso; evitado = a regra antiga o chamaria):")
    print("")
    print("| Frente | Rodadas | 2º revisor por risco | 2º revisor por raso | Evitado pela regra | Custo evitado US$ | "
          "Dispensas à mão | Escapes com dano |")
    print("|---|---:|---:|---:|---:|---:|---|---:|")
    for frente in sorted(pastas_frente):
        ms = [metas[d] for d in sorted(pastas_frente[frente]) if d in metas]
        if not ms and not escapes.get(frente):
            continue
        risco = sum(1 for m in ms if m.get("gatilho_2o_revisor", "").startswith("segurança"))
        raso = sum(1 for m in ms if m.get("gatilho_2o_revisor", "").startswith("revisor1 raso"))
        pela_regra = [m for m in ms if "gatilho_regra_antiga" in m and m.get("gatilho_2o_revisor") == SEM_RISCO]
        evitadas = [m for m in pela_regra if m["gatilho_regra_antiga"] not in ("", "-")]
        soma, sem_valor = Decimal(0), False
        for m in evitadas:
            v, _, incerto = custo_de((m.get("reviewer_custo") or "").strip())
            if incerto:
                sem_valor = True   # `US$ x + $?`: o x entra, o resto é desconhecido (N1 da rodada 1)
            if v is None and (m.get("reviewer_custo") or "").strip() == "assinatura" and PRECOS_EST:
                v = nominal_estimado(m, "reviewer", PRECOS_EST, CACHE_EST)
            if v is None:
                sem_valor = True
            else:
                soma += v
        if not evitadas:
            custo = "—"
        elif sem_valor and soma == 0:
            custo = "n/d"
        else:
            custo = numero(soma) + (" + n/d" if sem_valor else "")
        r2_mao = sum(1 for m in ms if "--no-revisor2" in m.get("dispensas_a_mao", "").split()
                     or ("dispensas_a_mao" not in m and m.get("gatilho_2o_revisor", "").endswith(
                         "dispensado por --no-revisor2")))
        des_mao = sum(1 for m in ms if "--no-desempate" in m.get("dispensas_a_mao", "").split())
        des_nd = any("dispensas_a_mao" not in m for m in ms)
        dispensas = "revisor2 %d · desempate %d%s" % (r2_mao, des_mao, " + n/d" if des_nd else "")
        n_esc = escapes.get(frente, 0)
        print("| %s | %d | %d | %d | %d | %s | %s | %d |" % (frente, len(ms), risco, raso, len(evitadas), custo,
                                                          dispensas, n_esc))
        if n_esc and pela_regra:
            avisos_regra.append("⚠️ %s: %d escape(s) com dano com o 2º revisor dispensado pela regra — revise a regra %s"
                                % (frente, n_esc, "(volta atrás ou o caminho entra na superfície de risco)" if evitadas
                                   else "(o caminho entra na superfície de risco?)"))
    for a in avisos_regra:
        print(a)
print("")
print("fora da conta: %d%s" % (len(fora), (" (" + "; ".join("%s: %s" % x for x in fora) + ")") if fora else ""))
print("RESULTADO: MEDIDO")
print("→ leia cada taxa com a amostra ao lado: poucas rodadas dão número instável. O script conta o que está "
      "registrado; trocar a cadeia de revisão é decisão de quem lê.")
PY
