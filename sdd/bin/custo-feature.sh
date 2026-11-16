#!/usr/bin/env bash
# custo-feature.sh — quanto uma feature custou, por fase: tokens, custo pago, custo nominal e tempo ativo das
# sessões do agente, mais o custo da revisão adversarial e as voltas do Verify Gate. Doc: docs/adversarial-review.md
# (seção custo-feature). Desenho: DESIGN_F23_ECONOMIA_MENSURAVEL (Decisions 1 a 9).
#
# Por que existe: sem o custo de cada fase registrado, nenhuma economia do processo se demonstra. O script lê as
# marcas de fase (marca-fase.sh) e as voltas do gate no trace da feature, os registros locais de cada agente pelos
# leitores sdd/bin/adapters/sessao-*.py (que devolvem só números) e os META.txt da revisão, e CONTA. Nunca chama
# modelo, nunca usa rede, nunca copia texto das sessões.
#
# USO-INICIO
#   custo-feature.sh <FEATURE> [--raiz <pasta>] [--saida <arquivo>|-] [--precos <pasta>] [--reviews <pasta>]
#                    [--ledgers <pasta>] [--registry <registry.tsv>]
#       grava <raiz>/sdd/reports/CUSTO_<FEATURE>.md (--saida - só imprime) com uma linha por fase, `sem fase`
#       (o que caiu entre a 1ª e a última marca fora de qualquer par início/fim), `revisão` e o total
#   custo-feature.sh --linha-de-base <mapa.tsv> [--saida <arquivo>|-] [--precos <pasta>] [--reviews <pasta>]
#                    [--registry <registry.tsv>]
#       mapa: 3 colunas separadas por TAB — feature · raiz (pasta das sessões daquela frente) · ledger (ou -);
#       imprime uma linha por feature: sessões (nominal, a sessão inteira, sem fase), revisão (nominal, ou n/d sem
#       META), rodadas de revisão e achados com dano (do ledger)
#       --raiz: padrão a raiz do repositório git (fora dele, a pasta atual)
#       --precos: pasta com precos.tsv e precos-cache.tsv; padrão a pasta do registry (a do projeto, senão a do pacote)
#       --reviews: padrão review.output_dir do sdd/config.yaml (sdd/reports/reviews) · --ledgers: padrão sdd/reviews
#       pago    = custo de agente ou engine pay-per-token (assinatura conta 0; cobrança desconhecida, n/d)
#       nominal = tokens × tarifa (entrada e saída da precos.tsv; cache lido e criado da precos-cache.tsv), mais o
#                 custo dos META.txt da revisão; somas exatas (decimal), arredondadas só na hora de imprimir
#       n/d     = sem registro ou sem preço: nunca conta como zero; o total vira `US$ x + n/d`
#       0 MEDIDO · 2 SEM DADOS (nenhuma marca, sessão nem revisão da feature) · 64 uso
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib.

set -u
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! sdd_python_pronto; then
  echo "🛑 custo-feature: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_CUSTO_BIN="$(cd "${_sdd_bin}" && { pwd -W 2>/dev/null || pwd; })"
export SDD_CUSTO_BIN

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # LM-015: saída em UTF-8 e "\n" também no Windows
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import json, os, re, subprocess, sys
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

BIN = os.environ["SDD_CUSTO_BIN"]
PACOTE_REVIEW = os.path.normpath(os.path.join(BIN, "..", "review"))
# \Z, não $: o $ do Python aceita uma quebra de linha no fim (R2 da rodada 4)
FEATURE_RE = re.compile(r"^[A-Za-z0-9_.-]{1,80}\Z")
MODELO_RE = re.compile(r"^[A-Za-z0-9._:/@-]{1,80}\Z")
PASTA_RE = re.compile(r"^EXTERNAL_REVIEW_\d{8}-\d{6}(?:-\d+)?\Z")
PASTA_NO_TEXTO = re.compile(r"EXTERNAL_REVIEW_\d{8}-\d{6}(?:-\d+)?")
CUSTO_RE = re.compile(r"^(≈)?\s*US\$\s*([0-9]{1,12}(?:[.,][0-9]{1,12})?)(\s*\+\s*\$\?)?$")
RODADA_RE = re.compile(r"^rodada=(\d+[a-z]?)\Z")
SEM_ACHADOS_RE = re.compile(r"^\s*sem achados:\s*rodada=(\d+[a-z]?)\s+(EXTERNAL_REVIEW_\S+)\s*$")
PAPEIS = ("reviewer", "revisor2", "auditor", "desempate")
TOKENS = ("entrada", "saida", "cache_lido", "cache_criado")
MILHAO = Decimal(1000000)


def para(motivo):
    print("🛑 custo-feature: " + motivo, file=sys.stderr)
    print("RESULTADO: PAROU\n→ rode `custo-feature.sh --help` para ver o uso.", file=sys.stderr)
    sys.exit(64)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def raiz_git():
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()
    except OSError:
        return os.getcwd()


def slot_review(raiz, chave):
    """Valor de review.<chave> no sdd/config.yaml da raiz, ou '' (a mesma leitura do eval-revisores.sh)."""
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


def instante(t):
    if not isinstance(t, str) or not t:
        return None
    try:
        d = datetime.fromisoformat(t[:-1] + "+00:00" if t.endswith("Z") else t)
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def decimal(txt):
    try:
        v = Decimal(txt.strip().replace(",", "."))
    except (InvalidOperation, AttributeError):
        return None
    return v if v.is_finite() and v >= 0 else None


def tsv(caminho, colunas):
    for ln in (ler(caminho) or "").splitlines():
        if not ln.strip() or ln.startswith("#"):
            continue
        c = ln.split("\t")
        if len(c) == colunas:
            yield [x.strip() for x in c]


# ── argumentos ──────────────────────────────────────────────────────────────────────────────────────
args = sys.argv[1:]
op = {"--raiz": None, "--saida": None, "--precos": None, "--reviews": None, "--ledgers": None, "--registry": None,
      "--linha-de-base": None}
feature = None
i = 0
while i < len(args):
    a = args[i]
    if a in op:
        if i + 1 >= len(args) or args[i + 1] == "" or (args[i + 1].startswith("--") and args[i + 1] != "-"):
            para("%s pede um valor" % a)
        op[a] = args[i + 1]
        i += 2
        continue
    if a.startswith("-"):
        para("opção desconhecida: " + a)
    if feature is not None:
        para("argumento a mais: " + a)
    feature = a
    i += 1
if op["--linha-de-base"] is None:
    if feature is None:
        para("falta a FEATURE (ou --linha-de-base <mapa.tsv>)")
    if not FEATURE_RE.match(feature):
        para("FEATURE inválida: só A-Z, a-z, 0-9, _, . e -, até 80 caracteres")
elif feature is not None:
    para("--linha-de-base não leva FEATURE")

raiz = os.path.abspath(op["--raiz"]) if op["--raiz"] else raiz_git()
if not os.path.isdir(raiz):
    para("a pasta de --raiz não existe: %s" % raiz)


def caminho(valor, padrao, base):
    v = valor or padrao
    return v if os.path.isabs(v) else os.path.join(base, v)


registry = caminho(op["--registry"], slot_review(raiz, "registry") or "sdd/review/registry.tsv", raiz)
if op["--registry"] and not os.path.isfile(registry):
    para("o arquivo de --registry não existe: %s" % registry)
if not os.path.isfile(registry):
    registry = os.path.join(PACOTE_REVIEW, "registry.tsv")
dir_precos = os.path.abspath(op["--precos"]) if op["--precos"] else os.path.dirname(registry)
if op["--precos"] and not os.path.isdir(dir_precos):
    para("a pasta de --precos não existe: %s" % dir_precos)
reviews = caminho(op["--reviews"], slot_review(raiz, "output_dir") or "sdd/reports/reviews", raiz)
if op["--reviews"] and not os.path.isdir(reviews):
    para("a pasta de --reviews não existe: %s" % reviews)
ledgers = caminho(op["--ledgers"], "sdd/reviews", raiz)
if op["--ledgers"] and not os.path.isdir(ledgers):
    para("a pasta de --ledgers não existe: %s" % ledgers)

COBRANCA = {c[0]: c[3] for c in tsv(registry, 9)}


def tabela_precos(nome):
    arq = os.path.join(dir_precos, nome)
    if not os.path.isfile(arq) and not op["--precos"]:
        arq = os.path.join(PACOTE_REVIEW, nome)
    t = {}
    for c in tsv(arq, 6):
        a, b = decimal(c[2]), decimal(c[3])
        if a is not None and b is not None:
            t[(c[0], c[1])] = (a, b)
    return t


PRECOS = tabela_precos("precos.tsv")
PRECOS_CACHE = tabela_precos("precos-cache.tsv")
FORA = []
SEM_PRECO = set()
ILEGIVEIS = [0]   # registros ilegíveis da última leitura de sessões


def marca_nd(conta):
    """Uma parte do custo desta linha não pôde ser lida: n/d nos dois custos, nunca zero (AT-004)."""
    conta["itens"] += 1
    conta["nominal_nd"] += 1
    conta["pago_nd"] += 1


# ── somador ─────────────────────────────────────────────────────────────────────────────────────────
def conta_nova():
    return {"execucoes": 0, "tokens": dict.fromkeys(TOKENS, 0), "nominal": Decimal(0), "pago": Decimal(0),
            "nominal_nd": 0, "pago_nd": 0, "itens": 0, "segundos": Decimal(0), "estimado": False}


def custo_msg(engine, m):
    """(nominal ou None, pago ou None) de uma mensagem da sessão: tokens × tarifa; parte sem preço = None."""
    nominal = Decimal(0)
    p = PRECOS.get((engine, m["modelo"]))
    if m["entrada"] or m["saida"]:
        if p is None:
            SEM_PRECO.add("%s · %s (entrada e saída, precos.tsv)" % (engine, m["modelo"]))
            nominal = None
        else:
            nominal += (Decimal(m["entrada"]) * p[0] + Decimal(m["saida"]) * p[1]) / MILHAO
    if m["cache_lido"] or m["cache_criado"]:
        c = PRECOS_CACHE.get((engine, m["modelo"]))
        if c is None:
            SEM_PRECO.add("%s · %s (cache, precos-cache.tsv)" % (engine, m["modelo"]))
            nominal = None
        elif nominal is not None:
            nominal += (Decimal(m["cache_lido"]) * c[0] + Decimal(m["cache_criado"]) * c[1]) / MILHAO
    cob = COBRANCA.get(engine, "desconhecida")
    if cob == "assinatura":
        pago = Decimal(0)
    elif cob == "pay-per-token":
        pago = nominal
    else:
        pago = None
    return nominal, pago


def soma(conta, nominal, pago):
    conta["itens"] += 1
    if nominal is None:
        conta["nominal_nd"] += 1
    else:
        conta["nominal"] += nominal
    if pago is None:
        conta["pago_nd"] += 1
    else:
        conta["pago"] += pago


def numero(valor):
    """4 casas; custo menor que 0,0001 sai com 6, para não virar 0.0000 (a regra do eval-revisores.sh)."""
    if Decimal(0) < valor < Decimal("0.000001"):
        return "<0.000001"
    casas = "0.000001" if Decimal(0) < valor < Decimal("0.0001") else "0.0001"
    return str(valor.quantize(Decimal(casas)))


def dinheiro(conta, chave):
    nd = conta[chave + "_nd"]
    if conta["itens"] == 0:
        return "0.0000"
    if nd == conta["itens"]:
        return "n/d"
    txt = ("≈" if conta["estimado"] and chave == "nominal" else "") + numero(conta[chave])
    return txt + (" + n/d" if nd else "")


def duracao(seg):
    s = int(seg)
    return "%dh%02dm%02ds" % (s // 3600, s % 3600 // 60, s % 60)


# ── sessões: os leitores ────────────────────────────────────────────────────────────────────────────
def leitores():
    pasta = os.path.join(BIN, "adapters")
    try:
        nomes = sorted(n for n in os.listdir(pasta) if n.startswith("sessao-") and n.endswith(".py"))
    except OSError:
        nomes = []
    return [(n[len("sessao-"):-len(".py")], os.path.join(pasta, n)) for n in nomes]


def ler_sessoes(raiz_sessoes):
    """{agente: [registros]}, o estado de cada leitor (LIDO, SEM REGISTRO, FALHOU) e quantos registros ilegíveis
    vieram. Leitor que falha fica None: o custo dele é n/d, nunca zero."""
    dados, estado, ILEGIVEIS[0] = {}, {}, 0
    for agente, prog in leitores():
        try:
            r = subprocess.run([sys.executable, "-B", prog, "--raiz", raiz_sessoes], capture_output=True)
        except OSError as e:
            estado[agente] = "FALHOU (%s)" % (e.strerror or "erro")
            FORA.append(("leitor " + agente, "não rodou: o agente fica n/d"))
            dados[agente] = None
            continue
        if r.returncode == 2:
            estado[agente] = "SEM REGISTRO"
            continue
        if r.returncode != 0:
            estado[agente] = "FALHOU (exit %d)" % r.returncode
            FORA.append(("leitor " + agente, "saiu %d: o agente fica n/d" % r.returncode))
            dados[agente] = None
            continue
        regs = []
        for ln in r.stdout.decode("utf-8", "replace").splitlines():
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            if not isinstance(d, dict):
                continue
            if d.get("tipo") == "ilegivel":
                FORA.append(("sessão de " + agente, "%s linha(s) ilegível(is) fora da conta" % d.get("n")))
                ILEGIVEIS[0] += 1
                continue
            t = instante(d.get("t"))
            if t is None or d.get("tipo") not in ("msg", "turno"):
                continue
            if d["tipo"] == "msg":
                m = {k: (d.get(k) if isinstance(d.get(k), int) and d.get(k) >= 0 else 0) for k in TOKENS}
                m["modelo"] = d.get("modelo") if isinstance(d.get("modelo"), str) and MODELO_RE.match(d["modelo"]) else "?"
                m["t"], m["tipo"] = t, "msg"
                regs.append(m)
            else:
                regs.append({"tipo": "turno", "t": t})
        regs.sort(key=lambda x: (x["t"], 0 if x["tipo"] == "turno" else 1))
        estado[agente] = "LIDO"
        dados[agente] = regs
    return dados, estado


def turnos(regs):
    """Intervalos ativos: do início de cada turno ao último registro do agente antes do próximo turno."""
    spans, inicio, ultimo = [], None, None
    for r in regs:
        if r["tipo"] == "turno":
            if inicio is not None and ultimo is not None and ultimo > inicio:
                spans.append((inicio, ultimo))
            inicio, ultimo = r["t"], None
        elif inicio is not None:
            ultimo = r["t"]
    if inicio is not None and ultimo is not None and ultimo > inicio:
        spans.append((inicio, ultimo))
    return spans


def segundos_em(spans, a, b):
    tot = Decimal(0)
    for x, y in spans:
        ini, fim = max(x, a), min(y, b)
        if fim > ini:
            tot += Decimal(str((fim - ini).total_seconds()))
    return tot


# ── revisão: META.txt ───────────────────────────────────────────────────────────────────────────────
def meta_de(pasta):
    m = {}
    for ln in (ler(os.path.join(pasta, "META.txt")) or "").splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            m[k.strip()] = v.strip()
    return m


def custo_de(valor):
    """(Decimal ou None, estimado?, incerto?) de um campo *_custo, pela regra do eval-revisores.sh: `US$ n + $?` é n mais
    uma parte desconhecida (a engine estourou o tempo), que nunca vira zero (R1 da rodada 2)."""
    mt = CUSTO_RE.match((valor or "").strip())
    if not mt:
        return None, False, False
    return Decimal(mt.group(2).replace(",", ".")), bool(mt.group(1)), bool(mt.group(3))


def ledger_info(arq):
    """(pastas citadas, rodadas distintas, achados com dano) de um LEDGER_REVISAO_*.md; None se ilegível."""
    texto = ler(arq)
    if texto is None:
        return None
    pastas, rodadas, dano = set(), set(), 0
    for ln in texto.splitlines():
        mt = SEM_ACHADOS_RE.match(ln)
        if mt:
            rodadas.add(mt.group(1))
            pastas.add(mt.group(2))
            continue
        if not ln.lstrip().startswith("|"):
            continue
        c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)][1:]
        if c and c[-1] == "":
            c = c[:-1]
        if len(c) != 7:
            continue
        mr = RODADA_RE.match(c[3])
        if not mr:
            continue
        rodadas.add(mr.group(1))
        if PASTA_RE.match(c[6]):
            pastas.add(c[6])
        if c[5] == "sim":
            dano += 1
    return pastas, rodadas, dano


def revisao(feat, ledger_arq):
    conta = conta_nova()
    citadas = set()
    if ledger_arq and os.path.isfile(ledger_arq):
        info = ledger_info(ledger_arq)
        if info:
            citadas = info[0]
        else:   # R3 da rodada 4: ledger que existe e não se lê — as revisões que só ele citava ficam n/d
            FORA.append(("revisão", "ledger ilegível: %s" % os.path.basename(ledger_arq)))
            marca_nd(conta)
    try:
        nomes = sorted(n for n in os.listdir(reviews) if PASTA_RE.match(n))
    except OSError:
        nomes = []
    alvo = "DEFINE_%s.md" % feat
    for n in sorted(citadas - set(nomes)):   # R1 da rodada 3: pasta citada pelo ledger e ausente do disco
        FORA.append(("revisão", "%s citada pelo ledger e ausente de %s" % (n, os.path.basename(reviews))))
        marca_nd(conta)
    for n in nomes:
        meta = meta_de(os.path.join(reviews, n))
        if not meta:   # R1 da rodada 4: META ausente ou ilegível numa pasta citada pelo ledger — n/d, nunca zero
            if n in citadas:
                FORA.append(("revisão", "%s sem META.txt legível" % n))
                conta["execucoes"] += 1
                marca_nd(conta)
            continue
        # R4 da revisão do código: aceita nome solto ou caminho, separado por vírgula, ponto e vírgula ou espaço
        docs = [os.path.basename(x.replace("\\", "/")) for x in re.split(r"[,;\s]+", meta.get("docs_sdd", "")) if x]
        if alvo not in docs and n not in citadas:
            continue
        conta["execucoes"] += 1
        for papel in PAPEIS:
            engine = meta.get(papel + "_engine_efetivo") or meta.get(papel + "_engine") or ""
            bruto = meta.get(papel + "_custo", "")
            if not engine or engine == "-":
                continue
            if bruto in ("", "-"):   # R4 da rodada 3: o papel rodou e o custo não foi gravado — n/d, nunca zero
                marca_nd(conta)
                continue
            for k, campo in (("entrada", "_tokens_entrada"), ("saida", "_tokens_saida")):
                v = meta.get(papel + campo, "")
                if v.isdigit():
                    conta["tokens"][k] += int(v)
            seg = decimal(meta.get(papel + "_segundos", ""))
            if seg is not None:
                conta["segundos"] += seg
            nominal, estimado, incerto = custo_de(bruto)
            conta["estimado"] = conta["estimado"] or estimado
            cob = COBRANCA.get(engine.split(":", 1)[0], "desconhecida")
            pago = Decimal(0) if cob == "assinatura" else (nominal if cob == "pay-per-token" else None)
            soma(conta, nominal, pago)
            if incerto:
                marca_nd(conta)
    return conta


# ── trace: marcas e voltas do gate ──────────────────────────────────────────────────────────────────
def ler_trace(feat):
    d = os.environ.get("SDD_TRACE_DIR") or "sdd/traces"
    arq = os.path.join(d if os.path.isabs(d) else os.path.join(raiz, d), feat + ".jsonl")
    marcas, gate = [], []
    for n, ln in enumerate((ler(arq) or "").splitlines(), 1):
        try:
            x = json.loads(ln)
        except ValueError:
            FORA.append(("trace:%d" % n, "linha ilegível"))
            continue
        if not isinstance(x, dict) or x.get("feature") != feat:
            continue
        t = instante(x.get("ts"))
        if t is None:
            continue
        if x.get("src") == "fase" and x.get("evento") in ("inicio", "fim") and isinstance(x.get("fase"), str) \
                and re.match(r"^[a-z][a-z0-9-]{0,39}\Z", x["fase"]):
            marcas.append((t, n, x["evento"], x["fase"]))
        elif x.get("src") in ("verify-gate", "release") and isinstance(x.get("exit"), int):
            gate.append((t, n, x["exit"]))
    marcas.sort()
    gate.sort()
    return marcas, gate


def intervalos(marcas, fim_sessoes):
    """[(fase, ini, fim)] sem sobreposição, e a janela (1ª marca, última marca ou fecho)."""
    ivs, aberta = [], None
    for t, _, evento, fase in marcas:
        if evento == "inicio":
            if aberta is not None:
                FORA.append(("marca", "fase sem fim: %s (fechada no início de %s)" % (aberta[0], fase)))
                ivs.append((aberta[0], aberta[1], t))
            aberta = (fase, t)
        else:
            if aberta is not None and aberta[0] == fase:
                ivs.append((fase, aberta[1], t))
                aberta = None
            else:
                FORA.append(("marca", "fim sem início: %s" % fase))
    fim_janela = marcas[-1][0] if marcas else None
    if aberta is not None:
        fecho = max(fim_sessoes, aberta[1]) if fim_sessoes else aberta[1]
        FORA.append(("marca", "fase sem fim: %s (fechada no fim da última sessão)" % aberta[0]))
        ivs.append((aberta[0], aberta[1], fecho))
        fim_janela = max(fim_janela, fecho)
    return ivs, (marcas[0][0], fim_janela) if marcas else None


def acumula(conta, agente, m):
    for k in TOKENS:
        conta["tokens"][k] += m[k]
    nominal, pago = custo_msg(agente, m)
    soma(conta, nominal, pago)


# ── modo feature ────────────────────────────────────────────────────────────────────────────────────
def modo_feature():
    marcas, gate = ler_trace(feature)
    dados, estado = ler_sessoes(raiz)
    regs_todos = [r for v in dados.values() if v for r in v]
    fim_sessoes = max((r["t"] for r in regs_todos), default=None)
    ivs, janela = intervalos(marcas, fim_sessoes)
    ordem, contas = [], {}
    for fase, _, _ in ivs:
        if fase not in contas:
            ordem.append(fase)
            contas[fase] = conta_nova()
        contas[fase]["execucoes"] += 1
    sem_fase = conta_nova()
    for agente, regs in dados.items():
        if regs is None:
            continue
        for m in regs:
            if m["tipo"] != "msg" or janela is None or not (janela[0] <= m["t"] <= janela[1]):
                continue
            alvo = next((contas[f] for f, a, b in ivs if a <= m["t"] <= b), sem_fase)
            acumula(alvo, agente, m)
        spans = turnos(regs)
        if janela is not None:
            dentro = Decimal(0)
            for f, a, b in ivs:
                s = segundos_em(spans, a, b)
                contas[f]["segundos"] += s
                dentro += s
            sem_fase["segundos"] += segundos_em(spans, janela[0], janela[1]) - dentro
    # AT-004 e R1 a R3 da revisão do código: o que não foi lido vira n/d, nunca zero.
    falhou = any(regs is None for regs in dados.values())
    if janela is not None and (falhou or ILEGIVEIS[0]):
        # leitor que falhou ou registro ilegível: não se sabe a que fase pertencia, então toda linha da janela é parcial
        for c in [contas[f] for f in ordem] + [sem_fase]:
            marca_nd(c)
    if janela is not None and not falhou and all(c["itens"] == 0 for c in [contas[f] for f in ordem] + [sem_fase]):
        # R2 da rodada 3: nenhuma mensagem lida na janela inteira (agente sem leitor): o trecho sem fase também não foi medido
        marca_nd(sem_fase)
    for f in ordem:
        if contas[f]["itens"] == 0:   # fase marcada sem nenhuma mensagem lida: agente sem leitor ou sem registro
            FORA.append(("fase", "nenhuma mensagem lida em %s: agente sem leitor ou sem registro" % f))
            marca_nd(contas[f])
    rev = revisao(feature, os.path.join(ledgers, "LEDGER_REVISAO_%s.md" % feature))
    tem_sessao = any(r["tipo"] == "msg" for r in regs_todos)
    if not marcas and (tem_sessao or falhou):   # R6 do DESIGN e R4 da rodada 2: sem marca, zero pareceria economia
        FORA.append(("marca", "nenhuma marca de fase: as sessões não foram atribuídas"))
        marca_nd(sem_fase)
    if not marcas and not rev["execucoes"] and not gate and not tem_sessao:
        print("RESULTADO: SEM DADOS")
        print("→ nenhuma marca de fase, sessão, revisão ou volta do gate de %s: as skills de fase gravam as marcas "
              "com marca-fase.sh." % feature)
        sys.exit(2)
    total = conta_nova()
    for c in [contas[f] for f in ordem] + [sem_fase, rev]:
        for k in TOKENS:
            total["tokens"][k] += c["tokens"][k]
        for k in ("nominal", "pago"):
            total[k] += c[k]
        if c is not rev:   # R5 da rodada 2: a revisão em primeiro plano já está dentro do turno do agente
            total["segundos"] += c["segundos"]
        for k in ("nominal_nd", "pago_nd", "itens", "execucoes"):
            total[k] += c[k]
        total["estimado"] = total["estimado"] or c["estimado"]
    linhas = ["# Custo — %s" % feature, "",
              "> Gerado por `sdd/bin/custo-feature.sh` em %s. Só números: nenhum texto das sessões. Valores em US$; "
              "`n/d` = sem registro ou sem preço, nunca zero. O tempo ativo do total é o das sessões (o da revisão fica na "
              "linha dela)." % datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
              "",
              "| Fase | Execuções | Entrada | Saída | Cache lido | Cache criado | Pago US$ | Nominal US$ | Tempo ativo |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]

    def linha(nome, c):
        t = c["tokens"]
        return "| %s | %d | %d | %d | %d | %d | %s | %s | %s |" % (
            nome, c["execucoes"], t["entrada"], t["saida"], t["cache_lido"], t["cache_criado"],
            dinheiro(c, "pago"), dinheiro(c, "nominal"), duracao(c["segundos"]))
    for f in ordem:
        linhas.append(linha(f, contas[f]))
    linhas.append(linha("sem fase", sem_fase))
    linhas.append(linha("revisão", rev))
    linhas.append(linha("**total**", total))
    linhas.append("")
    if gate:
        verde = next((k for k, g in enumerate(gate, 1) if g[2] == 0), None)
        linhas.append("Voltas do Verify Gate: %d (%s)." % (len(gate), "verde na %dª" % verde if verde else "nenhuma verde"))
    else:
        linhas.append("Voltas do Verify Gate: 0 (nenhuma no trace).")
    linhas.append("Leitores de sessão: " + (" · ".join("%s %s" % (a, estado[a]) for a in sorted(estado)) or "nenhum") + ".")
    fora = FORA + [("sem preço", p) for p in sorted(SEM_PRECO)]
    linhas.append("Fora da conta: %d%s" % (len(fora), (" (" + "; ".join("%s: %s" % x for x in fora) + ")") if fora else "") + ".")
    texto = "\n".join(linhas) + "\n"
    publica(texto, os.path.join(raiz, "sdd", "reports", "CUSTO_%s.md" % feature))


def publica(texto, padrao):
    destino = op["--saida"] or padrao
    if destino == "-":
        sys.stdout.write(texto)
    else:
        destino = os.path.abspath(destino)
        try:
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with open(destino, "w", encoding="utf-8", newline="\n") as h:
                h.write(texto)
        except OSError as e:
            para("não consegui gravar %s (%s)" % (destino, e.strerror or "erro"))
        sys.stdout.write(texto)
        print("gravado: %s" % destino)
    print("RESULTADO: MEDIDO")
    print("→ compare o nominal com o das features anteriores (--linha-de-base); n/d é lacuna, nunca economia.")
    sys.exit(0)


# ── modo linha de base ──────────────────────────────────────────────────────────────────────────────
def modo_linha_de_base():
    mapa = op["--linha-de-base"]
    if not os.path.isfile(mapa):
        para("o mapa não existe: %s" % mapa)
    linhas_mapa = list(tsv(mapa, 3))
    if not linhas_mapa:
        para("o mapa não tem nenhuma linha válida (3 colunas separadas por TAB: feature · raiz · ledger)")
    linhas = ["# Linha de base — custo por feature", "",
              "> Gerado por `sdd/bin/custo-feature.sh --linha-de-base`. Sessões: o registro inteiro da pasta, sem "
              "divisão por fase. Revisão: META.txt achados (n/d sem eles). `n/d` nunca é zero.", "",
              "| Feature | Sessões nominal US$ | Revisão nominal US$ | Rodadas de revisão | Achados com dano |",
              "|---|---:|---:|---:|---:|"]
    for feat, raiz_f, ledger in linhas_mapa:
        if not FEATURE_RE.match(feat):
            FORA.append(("mapa", "feature inválida: %s" % feat[:40]))
            continue
        dados, _ = ler_sessoes(raiz_f)
        sess = conta_nova()
        if ILEGIVEIS[0]:
            marca_nd(sess)
        for agente, regs in dados.items():
            if regs is None:
                marca_nd(sess)
                continue
            for m in regs:
                if m["tipo"] == "msg":
                    acumula(sess, agente, m)
        sessoes = dinheiro(sess, "nominal") if sess["itens"] else "n/d"
        led = None if ledger in ("", "-") else ledger
        rev = revisao(feat, led)
        revis = dinheiro(rev, "nominal") if rev["execucoes"] else "n/d"
        info = ledger_info(led) if led else None
        if led and info is None:
            FORA.append((feat, "ledger ilegível ou ausente: %s" % os.path.basename(led)))
        rodadas = str(len(info[1])) if info else "—"
        dano = str(info[2]) if info else "—"
        linhas.append("| %s | %s | %s | %s | %s |" % (feat, sessoes, revis, rodadas, dano))
    fora = FORA + [("sem preço", p) for p in sorted(SEM_PRECO)]
    linhas += ["", "Fora da conta: %d%s" % (len(fora), (" (" + "; ".join("%s: %s" % x for x in fora) + ")") if fora else "") + "."]
    publica("\n".join(linhas) + "\n", "-")


if op["--linha-de-base"] is not None:
    modo_linha_de_base()
else:
    modo_feature()
PY
