#!/usr/bin/env bash
# papel-serie.sh — roda as séries de medição de um papel (curador, avaliador…) com teto de gasto e trava
# automática. Doc: docs/model-per-role.md. Desenho: DESIGN_F23B2_MODELO_POR_PAPEL (Decisions 4 a 6).
#
# Por que existe: escolher um modelo mais barato para um papel exige rodar o papel, nos casos do gabarito, com cada
# candidato e com repetição — e isso chama agente, que pode custar. Aqui a trava é código: antes de cada chamada o
# acumulado de TODA a pasta de medição é conferido contra o teto; n/d, cobrança desconhecida ou pay-per-token com
# teto pago zero param a série. Este script roda e conta; quem julga é o papel-medir.sh.
#
# USO-INICIO
#   papel-serie.sh <pasta da série> [--cmd <comando>] [--candidatos id1,id2] [--teto-s <segundos>] [--precos <pasta>]
#       A série mora numa pasta de medição: <medição>/teto.txt (teto_pago: 0.00 · teto_nominal: 200.00) vale para
#       todas as séries da pasta. Na série: serie.txt (papel · gabarito · repeticoes) e candidatos.tsv (id · modelo ·
#       cobranca, separados por TAB; a 1ª linha é a referência, o modelo atual).
#       Ordem: todas as execuções da referência; o papel-medir.sh --so-referencia confere a referência; só então os
#       candidatos (--candidatos escolhe quais), caso a caso, repetição a repetição.
#       --cmd: o comando do agente (padrão: papeis.serie_cmd do sdd/config.yaml). Roda por bash -c, na cópia do
#         caso, com SDD_MODELO, SDD_BRIEF (arquivo com o brief), SDD_PAPEL, SDD_CASO e SDD_REP; a saída padrão é a
#         resposta do papel. Use "$SDD_MODELO" entre aspas.
#       --teto-s: teto de tempo de cada execução (padrão 1800). --precos: repassado ao custo-feature.sh --execucao.
#       Cada execução roda numa cópia fora do projeto (git archive do commit do caso + entrada/, git sem remoto); o
#       projeto é fotografado antes e depois (governanca-fronteira.sh): escrita fora da cópia invalida a execução.
#       Com candidatos, o papel-medir.sh confere a série antes da 1ª chamada (papel sem pontuador ou gabarito sem o
#       que comparar ⇒ 64, nada chamado). Execução interrompida de outra série da pasta (sem custo medido) para a
#       série (20): retome aquela série primeiro.
#       0 COMPLETA · 20 PARADO PELO TETO · 21 FRONTEIRA (execução inválida) · 22 REFERÊNCIA FORA DA META · 64 uso
#         (também a referência que o papel-medir.sh não conferiu, com PARADA.txt)
#       Retomar = rodar o mesmo comando: o que tem meta.txt é pulado; a execução interrompida (inicio.txt sem
#       meta.txt) tem o custo medido e somado antes de ser refeita; o PARADA.txt anterior vai para paradas/.
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib. Só roda dentro de um repositório git.
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
  echo "🛑 papel-serie: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_PAPEL_SERIE_BIN="$(cd "${_sdd_bin}" && { pwd -W 2>/dev/null || pwd; })"
# LM-029: o comando do projeto roda pelo mesmo bash que roda este script (no Windows, "bash" pelo nome cai no WSL)
SDD_PAPEL_SERIE_BASH="${BASH:-bash}"
export SDD_PAPEL_SERIE_BIN SDD_PAPEL_SERIE_BASH

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # LM-015: saída em UTF-8 e "\n" também no Windows
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import hashlib, io, os, re, shutil, signal, subprocess, sys, tarfile, tempfile, time
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

BIN = os.environ["SDD_PAPEL_SERIE_BIN"]
BASH = os.environ.get("SDD_PAPEL_SERIE_BASH") or "bash"
# a MESMA regra do slot papeis.<papel> (sdd-fluxo.sh modelo): começa por letra ou número (R7 e R10 da revisão D1)
MODELO_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,79}\Z")
ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]{0,39}\Z")
CASO_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}\Z")
COMMIT_RE = re.compile(r"(-|[0-9a-f]{7,40})\Z")
COBRANCAS = ("assinatura", "pay-per-token", "desconhecida")
TOKENS = ("entrada", "saida", "cache_lido", "cache_criado")


def uso(msg, seta="rode `papel-serie.sh --help` para ver o uso."):
    print("🛑 papel-serie: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ " + seta, file=sys.stderr)
    sys.exit(64)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def grava(p, texto):
    """Grava por um arquivo temporário ao lado e troca de nome: quem lê nunca vê um meta.txt pela metade."""
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as h:
        h.write(texto)
    os.replace(tmp, p)


def chaves(texto):
    d = {}
    for ln in (texto or "").splitlines():
        if ":" in ln and not ln.lstrip().startswith("#"):
            k, v = ln.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def decimal(txt):
    try:
        v = Decimal(txt)
    except (InvalidOperation, TypeError, ValueError):
        return None
    return v if v.is_finite() and v >= 0 else None


def agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git(*a, cwd, binario=False):
    r = subprocess.run(["git", "-c", "color.ui=never", *a], cwd=cwd, capture_output=True)   # LM-033
    out = r.stdout if binario else r.stdout.decode("utf-8", "replace")
    return r.returncode, out, r.stderr.decode("utf-8", "replace")


# ── argumentos ──────────────────────────────────────────────────────────────────────────────────────
args = sys.argv[1:]
op = {"--cmd": None, "--candidatos": None, "--teto-s": "1800", "--precos": None}
serie = None
i = 0
while i < len(args):
    a = args[i]
    if a in op:
        if i + 1 >= len(args) or args[i + 1] == "":
            uso("%s pede um valor" % a)
        op[a] = args[i + 1]
        i += 2
        continue
    if a.startswith("-"):
        uso("opção desconhecida: " + a)
    if serie is not None:
        uso("argumento a mais: " + a)
    serie = a
    i += 1
if serie is None:
    uso("falta a pasta da série")
serie = os.path.realpath(serie)
if not os.path.isdir(serie):
    uso("a pasta da série não existe: %s" % serie)
if not re.match(r"[1-9][0-9]{0,4}\Z", op["--teto-s"]):
    uso("--teto-s pede um número inteiro de segundos (1 a 99999)")
TETO_S = int(op["--teto-s"])
medicao = os.path.dirname(serie)

rc, raiz, _ = git("rev-parse", "--show-toplevel", cwd=serie)
if rc != 0 or not raiz.strip():
    uso("a série precisa estar dentro de um repositório git (a cópia de cada caso sai de git archive)")
raiz = os.path.realpath(raiz.strip())

teto = chaves(ler(os.path.join(medicao, "teto.txt")))
TETO_PAGO, TETO_NOMINAL = decimal(teto.get("teto_pago")), decimal(teto.get("teto_nominal"))
if TETO_PAGO is None or TETO_NOMINAL is None:
    uso("%s/teto.txt precisa de teto_pago e teto_nominal em US$ (ex.: teto_pago: 0.00)" % medicao,
        "grave o teto da medição (vale para todas as séries da pasta) e rode de novo; nada rodou.")
cfg = chaves(ler(os.path.join(serie, "serie.txt")))
PAPEL = cfg.get("papel", "")
if not ID_RE.match(PAPEL):
    uso("serie.txt sem papel válido (ex.: papel: avaliador)")
if not re.match(r"[1-9]\Z|10\Z", cfg.get("repeticoes", "")):
    uso("serie.txt: repeticoes de 1 a 10")
REPS = int(cfg["repeticoes"])
gab = cfg.get("gabarito", "")
gab = os.path.realpath(gab if os.path.isabs(gab) else os.path.join(serie, gab)) if gab else ""
if not gab or not os.path.isdir(gab):
    uso("serie.txt: o gabarito não existe: %s" % (gab or "(vazio)"))

candidatos = []
for n, ln in enumerate((ler(os.path.join(serie, "candidatos.tsv")) or "").splitlines(), 1):
    if not ln.strip() or ln.startswith("#"):
        continue
    c = [x.strip() for x in ln.split("\t")]
    if len(c) != 3 or not ID_RE.match(c[0]) or not MODELO_RE.match(c[1]) or c[2] not in COBRANCAS:
        uso("candidatos.tsv:%d inválida (id · modelo · cobranca; o modelo começa por letra ou número e só tem "
            "letras, números e . _ : / -; cobranca: %s)" % (n, ", ".join(COBRANCAS)))
    if any(x["id"] == c[0] for x in candidatos):
        uso("candidatos.tsv:%d repete o id %s" % (n, c[0]))
    candidatos.append({"id": c[0], "modelo": c[1], "cobranca": c[2]})
if not candidatos:
    uso("candidatos.tsv vazio: a 1ª linha é a referência (o modelo atual)")
ref = candidatos[0]
escolhidos = candidatos[1:]
if op["--candidatos"]:
    pedidos = [x for x in op["--candidatos"].split(",") if x]
    ids = {c["id"] for c in candidatos[1:]}
    fora = [x for x in pedidos if x not in ids]
    if fora:
        uso("--candidatos fora do candidatos.tsv (ou é a referência, que roda sempre): " + ", ".join(fora))
    escolhidos = [c for c in candidatos[1:] if c["id"] in pedidos]

casos = []
for nome in sorted(os.listdir(gab)):
    cx = chaves(ler(os.path.join(gab, nome, "caso.txt")))
    if cx.get("papel") != PAPEL:
        continue
    if not CASO_RE.match(nome) or not COMMIT_RE.match(cx.get("commit", "")) \
            or ler(os.path.join(gab, nome, "brief.md")) is None:
        uso("caso %s inválido: caso.txt com commit (sha ou -) e brief.md legível" % nome)
    base = cx.get("base", "")
    if base and (not re.match(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,79}\Z", base) or ".." in base
                 or git("rev-parse", "--verify", "-q", base + "^{commit}", cwd=raiz)[0] != 0):
        uso("caso %s: base %s não é uma ref deste repositório" % (nome, base))
    casos.append({"nome": nome, "commit": cx["commit"], "base": base, "dir": os.path.join(gab, nome)})
if not casos:
    uso("o gabarito não tem caso do papel %s (caso.txt com papel: %s)" % (PAPEL, PAPEL))

cmd = op["--cmd"]
if cmd is None:
    cfgp = ler(os.path.join(raiz, "sdd", "config.yaml")) or ""
    dentro = False
    for ln in cfgp.splitlines():
        if ln and not ln[0].isspace() and not ln.startswith("#"):
            dentro = ln.split("#", 1)[0].strip() == "papeis:"
            continue
        m = re.match(r"^\s+serie_cmd:\s*(.*)$", ln) if dentro else None
        if m:
            v = m.group(1).strip()
            # R7 da revisão do código: string YAML entre aspas desfaz os escapes (\" e \\ nas duplas, '' nas simples)
            if len(v) >= 2 and v[0] == v[-1] == '"':
                cmd = re.sub(r'\\(["\\])', r"\1", v[1:-1])
            elif len(v) >= 2 and v[0] == v[-1] == "'":
                cmd = v[1:-1].replace("''", "'")
            else:
                cmd = v
if not cmd:
    uso("sem o comando do agente: passe --cmd ou preencha papeis.serie_cmd em sdd/config.yaml",
        "veja docs/model-per-role.md (um exemplo por agente); nada rodou.")


# ── acumulado da medição inteira (R1 da revisão D1) ──────────────────────────────────────────────────
def registros():
    """Todo meta.txt e interrompida-*.txt da pasta de medição: [(arquivo, dict)]."""
    out = []
    for raiz_d, dirs, arqs in os.walk(medicao):
        dirs.sort()
        for a in sorted(arqs):
            if a == "meta.txt" or (a.startswith("interrompida-") and a.endswith(".txt")):
                out.append((os.path.join(raiz_d, a), chaves(ler(os.path.join(raiz_d, a)))))
    return out


def acumulado():
    ac = {"nominal": Decimal(0), "pago": Decimal(0), "nominal_nd": 0, "pago_nd": 0, "maior": Decimal(0)}
    for _, d in registros():
        for k in ("nominal", "pago"):
            v = decimal(d.get(k))
            if v is None:
                ac[k + "_nd"] += 1
            else:
                ac[k] += v
                if k == "nominal" and v > ac["maior"]:
                    ac["maior"] = v
    return ac


def pago_de(cand, nominal):
    if cand["cobranca"] == "assinatura":
        return Decimal(0)
    return nominal if cand["cobranca"] == "pay-per-token" else None


def pode_chamar(cand, ac):
    """(True, "") ou (False, motivo). Estimativa = o maior nominal de uma execução já gravada na medição."""
    est = ac["maior"]
    if cand["cobranca"] == "desconhecida":
        return False, "cobrança desconhecida (%s): o gasto não tem como ser conferido" % cand["id"]
    if cand["cobranca"] == "pay-per-token" and TETO_PAGO == 0:
        return False, "candidato pay-per-token (%s) com teto pago zero" % cand["id"]
    if ac["nominal_nd"] or ac["pago_nd"]:
        return False, "acumulado com n/d: o teto não se confere"
    if ac["nominal"] + est > TETO_NOMINAL:
        return False, "nominal %s + estimativa %s passaria do teto %s" % (ac["nominal"], est, TETO_NOMINAL)
    prox = est if cand["cobranca"] == "pay-per-token" else Decimal(0)
    if ac["pago"] + prox > TETO_PAGO:
        return False, "pago %s + estimativa %s passaria do teto %s" % (ac["pago"], prox, TETO_PAGO)
    return True, ""


def parada(rc, palavra, motivo, extra=()):
    ac = acumulado()
    nd = lambda k: (" + n/d" if ac[k + "_nd"] else "")
    texto = ["motivo: " + motivo, "quando: " + agora(),
             "acumulado_nominal: %s%s" % (ac["nominal"], nd("nominal")),
             "acumulado_pago: %s%s" % (ac["pago"], nd("pago")),
             "teto_nominal: %s" % TETO_NOMINAL, "teto_pago: %s" % TETO_PAGO] + list(extra)
    grava(os.path.join(serie, "PARADA.txt"), "\n".join(texto) + "\n")
    print("🛑 papel-serie: " + motivo)
    print("RESULTADO: " + palavra)
    print("→ nada mais foi chamado; o motivo e os acumulados estão em %s/PARADA.txt. Retome com o mesmo comando "
          "depois de resolver." % serie)
    sys.exit(rc)


def custo_execucao(copia):
    """chave=valor do custo-feature.sh --execucao: o mesmo leitor e a mesma conta da B1 (Decision 6)."""
    a = [BASH, os.path.join(BIN, "custo-feature.sh"), "--execucao", copia]
    if op["--precos"]:
        a += ["--precos", op["--precos"]]
    r = subprocess.run(a, capture_output=True, cwd=raiz)
    d = {}
    for ln in r.stdout.decode("utf-8", "replace").splitlines():
        if "=" in ln and not ln.startswith("RESULTADO"):
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip()
    if r.returncode != 0 or decimal(d.get("nominal")) is None:
        d["nominal"] = "n/d"
    return d


BASE = os.path.join(os.path.realpath(tempfile.gettempdir()),
                    "sdd-serie-" + hashlib.sha256(serie.encode("utf-8")).hexdigest()[:12])


# ── retomada: PARADA.txt anterior e execuções interrompidas (R4 e R6 da revisão D1) ─────────────────
if os.path.isfile(os.path.join(serie, "PARADA.txt")):
    os.makedirs(os.path.join(serie, "paradas"), exist_ok=True)
    os.replace(os.path.join(serie, "PARADA.txt"),
               os.path.join(serie, "paradas", datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + ".txt"))
for raiz_d, dirs, arqs in os.walk(os.path.join(serie, "execucoes")):
    if "inicio.txt" in arqs and "meta.txt" not in arqs:
        ini = chaves(ler(os.path.join(raiz_d, "inicio.txt")))
        if ini.get("copia") and os.path.isdir(os.path.dirname(ini["copia"])) \
                and not os.path.isfile(os.path.join(os.path.dirname(ini["copia"]), "chamado.txt")):
            os.remove(os.path.join(raiz_d, "inicio.txt"))   # parou antes de chamar o agente (R3 da revisão do código)
            print("↻ execução que não chegou a chamar o agente descartada (%s)" % os.path.relpath(raiz_d, serie))
            continue
        d = custo_execucao(ini.get("copia", "")) if ini.get("copia") else {"nominal": "n/d"}
        cand = next((c for c in candidatos if c["id"] == ini.get("candidato")), None)
        nom = decimal(d.get("nominal"))
        pago = pago_de(cand, nom) if (cand and nom is not None) else None
        n = len([a for a in arqs if a.startswith("interrompida-")]) + 1
        grava(os.path.join(raiz_d, "interrompida-%d.txt" % n),
              "estado: interrompida\ninicio: %s\nnominal: %s\npago: %s\nmodelos: %s\n"
              % (ini.get("inicio", "?"), nom if nom is not None else "n/d", pago if pago is not None else "n/d",
                 d.get("modelos", "")))
        os.remove(os.path.join(raiz_d, "inicio.txt"))
        print("↻ execução interrompida medida (%s): nominal %s" % (os.path.relpath(raiz_d, serie),
                                                                   nom if nom is not None else "n/d"))


def interrompidas_sem_custo():
    """inicio.txt sem meta.txt em qualquer série da medição (R5 da revisão do código). As desta série já foram
    medidas acima; as de outra série ficariam fora do acumulado até ela ser retomada."""
    out = []
    for raiz_d, _, arqs in os.walk(medicao):
        if "inicio.txt" in arqs and "meta.txt" not in arqs:
            out.append("interrompida: " + os.path.relpath(raiz_d, medicao))
    return sorted(out)


# ── uma execução ────────────────────────────────────────────────────────────────────────────────────
def executar(cand, caso, rep):
    pasta = os.path.join(serie, "execucoes", caso["nome"], cand["id"], str(rep))
    if os.path.isfile(os.path.join(pasta, "meta.txt")):
        return
    pend = interrompidas_sem_custo()
    if pend:
        parada(20, "PARADO PELO TETO", "execução interrompida sem custo medido em outra série da medição: o "
               "acumulado não se confere; retome aquela série primeiro", pend[:20])
    ok, motivo = pode_chamar(cand, acumulado())
    if not ok:
        parada(20, "PARADO PELO TETO", motivo,
               ["seguinte: %s · %s · repetição %d" % (caso["nome"], cand["id"], rep)])
    # R1 da revisão do código: cada tentativa ganha um caminho próprio; o registro de sessão do agente é por pasta, e
    # uma refeita no mesmo caminho somaria a sessão da interrompida (já contada no interrompida-N.txt)
    trab = os.path.join(BASE, "%s-%s-%d-%s" % (caso["nome"], cand["id"], rep, os.urandom(4).hex()))
    shutil.rmtree(trab, ignore_errors=True)
    copia = os.path.join(trab, "copia")
    os.makedirs(copia)

    def extrai(ref):
        rc, tar, err = git("archive", "--format=tar", ref, cwd=raiz, binario=True)
        if rc != 0:
            uso("git archive %s falhou (caso %s): %s" % (ref, caso["nome"], err.strip()))
        with tarfile.open(fileobj=io.BytesIO(tar)) as t:
            t.extractall(copia)

    def git_copia(*a):
        rc, _, err = git(*a, cwd=copia)
        if rc != 0:
            uso("não consegui preparar a cópia do caso %s (git %s): %s" % (caso["nome"], a[0], err.strip()))

    commit_cp = ["-c", "user.name=sdd-serie", "-c", "user.email=sdd-serie@localhost", "-c", "commit.gpgsign=false",
                 "commit", "-q", "--allow-empty", "-m"]
    git_copia("init", "-q")
    if caso["base"]:
        # o teste de não regressão compara com a versão base (ex.: a tag v2.2.6): a cópia ganha um 1º commit com a
        # árvore da base, marcado com o mesmo nome, e o caso por cima — ainda sem remoto
        extrai(caso["base"])
        git_copia("add", "-A")
        git_copia(*commit_cp, "base %s" % caso["base"])
        git_copia("tag", caso["base"])
        git_copia("rm", "-rq", "--ignore-unmatch", ".")
    if caso["commit"] != "-":
        extrai(caso["commit"])
    git_copia("add", "-A")
    git_copia(*commit_cp, "caso %s" % caso["nome"])
    # entrada/ vai por cima DEPOIS do commit, sem entrar no git: os documentos da época (DEFINE, DESIGN, colheita)
    # não estavam no commit; commitados, o publish-gate da cópia os acusaria como arquivo não declarado
    entrada = os.path.join(caso["dir"], "entrada")
    if os.path.isdir(entrada):
        shutil.copytree(entrada, copia, dirs_exist_ok=True)
    brief = os.path.join(trab, "brief.md")
    with open(brief, "w", encoding="utf-8", newline="\n") as h:
        h.write(ler(os.path.join(caso["dir"], "brief.md")).replace("@COPIA@", copia))
    # o inicio.txt mora no projeto: vem antes da foto de antes, senão a fronteira o veria como escrita do agente
    ini = os.path.join(pasta, "inicio.txt")
    grava(ini, "copia: %s\ncandidato: %s\ninicio: %s\n" % (copia, cand["id"], agora()))
    fr = os.path.join(BIN, "governanca-fronteira.sh")
    nada = os.path.join(raiz, ".sdd-serie-nenhum-arquivo-permitido")
    if subprocess.run([BASH, fr, "--snapshot", raiz, os.path.join(trab, "antes"), nada],
                      capture_output=True).returncode != 0:
        os.remove(ini)   # R3 da revisão do código: nada foi chamado, então não há interrompida a medir
        uso("o snapshot do projeto falhou: a fronteira não se confere e nada foi chamado")
    remoto_antes = git("remote", cwd=copia)[1].strip()
    # R3: o marcador fica fora do projeto, ao lado da cópia; sem ele, um inicio.txt sem meta.txt é uma execução que
    # parou antes de chamar o agente (Ctrl-C na montagem), e a retomada o descarta sem medir
    grava(os.path.join(trab, "chamado.txt"), agora() + "\n")
    env = dict(os.environ, SDD_MODELO=cand["modelo"], SDD_BRIEF=brief, SDD_PAPEL=PAPEL, SDD_CASO=caso["nome"],
               SDD_REP=str(rep))
    t0 = time.monotonic()
    saida_tmp = os.path.join(trab, "saida.txt")   # fora do projeto até o --comparar (R5 da revisão D1)
    with open(saida_tmp, "wb") as out, open(os.path.join(trab, "stderr.txt"), "wb") as errf:
        p = subprocess.Popen([BASH, "-c", cmd], cwd=copia, env=env, stdout=out, stderr=errf,
                             stdin=subprocess.DEVNULL, start_new_session=(os.name != "nt"))
        try:
            rc_cmd = p.wait(timeout=TETO_S)
        except subprocess.TimeoutExpired:
            # LM-016: o teto vale pelo timeout do Python; o grupo inteiro só cai onde há sinal POSIX
            try:
                os.killpg(p.pid, signal.SIGKILL) if os.name != "nt" else p.kill()
            except OSError:
                p.kill()
            p.wait()
            rc_cmd = 124
    seg = int(time.monotonic() - t0)
    subprocess.run([BASH, fr, "--snapshot", raiz, os.path.join(trab, "depois"), nada], capture_output=True)
    cmp = subprocess.run([BASH, fr, "--comparar", os.path.join(trab, "antes"), os.path.join(trab, "depois"), nada],
                         capture_output=True)
    fora = [ln for ln in cmp.stdout.decode("utf-8", "replace").splitlines() if ln.startswith("FORA:")]
    remoto = remoto_antes or git("remote", cwd=copia)[1].strip()
    d = custo_execucao(copia)
    nom = decimal(d.get("nominal"))
    pago = pago_de(cand, nom) if nom is not None else None
    base_meta = ["papel: " + PAPEL, "caso: " + caso["nome"], "candidato: " + cand["id"], "modelo: " + cand["modelo"],
                 "cobranca: " + cand["cobranca"], "repeticao: %d" % rep, "rc: %d" % rc_cmd, "segundos: %d" % seg,
                 "nominal: %s" % (nom if nom is not None else "n/d"), "pago: %s" % (pago if pago is not None else "n/d"),
                 "modelos: " + d.get("modelos", "")] + ["%s: %s" % (k, d.get(k, "0")) for k in TOKENS]
    if cmp.returncode not in (0, 1) or fora or remoto:
        motivo = ("a cópia ganhou remoto git" if remoto else
                  "o agente gravou fora da cópia" if fora else "a fronteira não se conferiu (exit %d)" % cmp.returncode)
        grava(os.path.join(pasta, "meta.txt"), "\n".join(["estado: invalida", "motivo: " + motivo] + base_meta) + "\n")
        os.remove(os.path.join(pasta, "inicio.txt"))
        parada(21, "FRONTEIRA", motivo + " — execução inválida, fora da conta e da escolha (cópia mantida em %s)" % trab,
               fora[:50] + (["remoto: " + remoto.replace("\n", ", ")] if remoto else []))
    shutil.move(saida_tmp, os.path.join(pasta, "saida.txt"))
    grava(os.path.join(pasta, "meta.txt"), "\n".join(["estado: ok"] + base_meta) + "\n")
    os.remove(os.path.join(pasta, "inicio.txt"))
    shutil.rmtree(trab, ignore_errors=True)
    ac = acumulado()
    print("▶ %s · %s · rep %d · rc %d · %ds · nominal %s · acumulado %s%s" % (
        caso["nome"], cand["id"], rep, rc_cmd, seg, nom if nom is not None else "n/d", ac["nominal"],
        " + n/d" if ac["nominal_nd"] else ""))


# ── a série: referência inteira, a barreira de calibração (N1), os candidatos ───────────────────────
print("papel-serie: %s · papel %s · %d caso(s) · %d repetição(ões) · referência %s · candidatos %s"
      % (os.path.basename(serie), PAPEL, len(casos), REPS, ref["id"], ", ".join(c["id"] for c in escolhidos) or "—"))
MEDIR = [BASH, os.path.join(BIN, "papel-medir.sh"), serie, "--so-referencia"]


def linhas_de(r):
    return (r.stdout + r.stderr).decode("utf-8", "replace").strip().splitlines()


if escolhidos:
    # R6 da revisão do código: antes de qualquer chamada, o medidor tem de aceitar a série (papel com pontuador,
    # gabarito com o que comparar); senão a referência seria paga para nada
    r = subprocess.run(MEDIR, capture_output=True)
    if r.returncode == 64:
        uso("o papel-medir.sh recusa esta série, e nada foi chamado: " + " | ".join(linhas_de(r)[:3]),
            "corrija o serie.txt ou o gabarito e rode de novo.")
for caso in casos:
    for rep in range(1, REPS + 1):
        executar(ref, caso, rep)
if escolhidos:
    r = subprocess.run(MEDIR, capture_output=True)
    if r.returncode == 3:
        parada(22, "REFERÊNCIA FORA DA META",
               "a referência não passou na conferência do papel-medir.sh (exit 3): nenhum candidato foi chamado",
               linhas_de(r)[-20:])
    if r.returncode != 0:
        parada(64, "REFERÊNCIA NÃO CONFERIDA",
               "o papel-medir.sh não conferiu a referência (exit %d): nenhum candidato foi chamado" % r.returncode,
               linhas_de(r)[-20:])
    for cand in escolhidos:
        for caso in casos:
            for rep in range(1, REPS + 1):
                executar(cand, caso, rep)
ac = acumulado()
print("RESULTADO: COMPLETA")
print("→ acumulado da medição: nominal %s%s · pago %s%s. Rode papel-medir.sh %s para a escolha."
      % (ac["nominal"], " + n/d" if ac["nominal_nd"] else "", ac["pago"], " + n/d" if ac["pago_nd"] else "", serie))
sys.exit(0)
PY
