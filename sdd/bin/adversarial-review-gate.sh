#!/usr/bin/env bash
# adversarial-review-gate.sh — gate offline da revisão adversarial: roda sdd/bin/adversarial-review.sh de verdade,
# com os 4 adapters REAIS de sdd/bin/adapters/, contra stubs que imitam a saída de cada engine
# (sdd/review/stubs/), e confere no META o que cada adapter extraiu: vereditos, engine e modelo, tokens, custo.
# Doc: docs/adversarial-review.md ("Offline gate").
#
# Por que existe: um formato de CLI que muda quebra a extração em silêncio, e só uma revisão paga mostraria.
# Este gate não usa rede nem crédito: proxies apontam para uma porta morta, a chave é falsa e gerada aqui, as CLIs
# claude/codex/gemini são stubs na frente do PATH e a OpenRouter é um servidor em 127.0.0.1.
#
# USO-INICIO
#   adversarial-review-gate.sh [-v]
#       -v   mostra, em cada asserção de campo, o valor lido no META
#       0 todas as asserções passaram · 2 alguma falhou (todas rodam; cada ❌ diz o que conferir)
#       3 o gate não conseguiu se isolar (stub ausente, registry sem as 4 engines, CLI real à frente do PATH
#         no shell que roda os adapters, servidor local que não subiu) — nenhuma engine foi chamada · 64 uso
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib · sem `timeout` (o teto é do Python).

set -u

BIN="$(cd "$(dirname "$0")" && pwd)"

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 adversarial-review-gate: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_GATE_BIN="$BIN" SDD_GATE_BASH="${BASH:-bash}" exec python3 -B - "$@" <<'PY'
import atexit, json, os, re, shutil, subprocess, sys, tempfile, time

BIN = os.environ.pop("SDD_GATE_BIN")
BASH = os.environ.pop("SDD_GATE_BASH") or "bash"
AR = os.path.join(BIN, "adversarial-review.sh")
REVIEW = os.path.normpath(os.path.join(BIN, "..", "review"))
STUBS = os.path.join(REVIEW, "stubs")
ADAPTERS = os.path.join(BIN, "adapters")
ENGINES = ("claude", "codex", "gemini", "openrouter")
CLIS = ("claude", "codex", "gemini")
TETO_EXECUCAO = 60          # segundos por execução de adversarial-review.sh

args = sys.argv[1:]
VERBOSE = False
for a in args:
    if a == "-v":
        VERBOSE = True
    else:
        print("🛑 adversarial-review-gate: argumento desconhecido: " + a, file=sys.stderr)
        print("RESULTADO: PAROU\n→ rode `adversarial-review-gate.sh --help` para ver o uso.", file=sys.stderr)
        sys.exit(64)

N = [0]
FALHAS = []
T0 = time.time()


def ok(rotulo, valor=None):
    N[0] += 1
    print("  ✅ %d. %s" % (N[0], rotulo))
    if VERBOSE and valor is not None:
        print("        lido: %s" % (valor,))


def falha(rotulo, motivo):
    N[0] += 1
    FALHAS.append(rotulo)
    print("  ❌ %d. %s" % (N[0], rotulo))
    print("        → %s" % motivo)


def confere(rotulo, obtido, esperado):
    if obtido == esperado:
        ok(rotulo, obtido)
    else:
        falha(rotulo, "lido %r, esperado %r" % (obtido, esperado))


def quebrado(motivo, seta):
    print("🛑 adversarial-review-gate: " + motivo, file=sys.stderr)
    print("RESULTADO: GATE QUEBRADO", file=sys.stderr)
    print("→ " + seta, file=sys.stderr)
    sys.exit(3)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def tsv(p, colunas):
    linhas = []
    for ln in (ler(p) or "").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        c = ln.split("\t")
        if len(c) == colunas:
            linhas.append([x.strip() for x in c])
    return linhas


# ── pré-voo: nada é chamado antes de o isolamento estar provado ──────────────────────────────────
for f in ["comum.py", "cenarios.tsv"] + [e + ".py" for e in ENGINES] + \
         ["respostas/revisor.md", "respostas/auditor-agree.md", "respostas/auditor-sem-bloco.md",
          "respostas/auditor-misto.md"]:
    if not os.path.isfile(os.path.join(STUBS, f)):
        quebrado("stub ausente: %s" % os.path.join(STUBS, f),
                 "reinstale sdd/review/stubs/ (rode o init do sdd-open) e rode o gate de novo.")
if not os.path.isfile(AR):
    quebrado("script ausente: " + AR, "reinstale sdd/bin/ (rode o init do sdd-open).")
REG = {l[0]: l for l in tsv(os.path.join(REVIEW, "registry.tsv"), 9)}
for e in ENGINES:
    if e not in REG or not os.path.isfile(os.path.join(ADAPTERS, REG[e][1] + ".sh")):
        quebrado("o registry %s não tem a engine %s com adapter em %s" % (os.path.join(REVIEW, "registry.tsv"), e,
                                                                         ADAPTERS),
                 "o gate prova as 4 engines do pacote: restaure a linha (o registry do pacote vem com as 4).")
CEN = {(l[0], l[1]): l for l in tsv(os.path.join(STUBS, "cenarios.tsv"), 10)}
PRECOS = {(l[0], l[1]): (float(l[2]), float(l[3])) for l in tsv(os.path.join(REVIEW, "precos.tsv"), 6)
          if re.match(r"^[0-9.]+$", l[2]) and re.match(r"^[0-9.]+$", l[3])}

TMP = tempfile.mkdtemp(prefix="sdd-review-gate-")
atexit.register(shutil.rmtree, TMP, True)
TBIN = os.path.join(TMP, "bin")
os.makedirs(TBIN)
for e in CLIS:
    p = os.path.join(TBIN, e)
    with open(p, "w") as h:
        h.write('#!/bin/sh\nexec "%s" -B "%s" "$@"\n' % (sys.executable, os.path.join(STUBS, e + ".py")))
    os.chmod(p, 0o755)

CHAVE = "gate-%d-falsa" % os.getpid()
# Nada herdado que mude QUAL repositório o git usa: um hook numa worktree exporta GIT_DIR e GIT_INDEX_FILE, e o
# repositório descartável viraria o do usuário (commit na branch dele). Todo GIT_* sai; os que o gate precisa
# voltam abaixo, e GIT_CEILING_DIRECTORIES impede o git de subir para fora da pasta temporária.
BASE_ENV = {k: v for k, v in os.environ.items()
            if not k.startswith(("BASH_FUNC_", "GIT_", "SDD_REVIEW_", "SDD_STUB_")) and k not in ("BASH_ENV", "ENV")
            and k.lower() not in ("no_proxy",)}
BASE_ENV.update({
    "PATH": TBIN + os.pathsep + os.environ.get("PATH", ""),
    "http_proxy": "http://127.0.0.1:9", "https_proxy": "http://127.0.0.1:9",
    "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
    "no_proxy": "127.0.0.1,localhost", "NO_PROXY": "127.0.0.1,localhost",
    "OPENROUTER_API_KEY": CHAVE, "SDD_REVIEW_ESPERA": "0",
    "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
    "GIT_CEILING_DIRECTORIES": os.path.realpath(TMP),
    "GIT_AUTHOR_NAME": "gate", "GIT_AUTHOR_EMAIL": "gate@example.com",
    "GIT_COMMITTER_NAME": "gate", "GIT_COMMITTER_EMAIL": "gate@example.com",
})

# o adapter roda num `bash -c` novo: confere ali, com o ambiente exato, para onde cada CLI resolve
sonda = subprocess.run([BASH, "-c", 'for e in claude codex gemini; do printf "%s=%s\\n" "$e" "$(command -v "$e")"; done'],
                       env=BASE_ENV, capture_output=True, text=True)
for ln in sonda.stdout.splitlines():
    e, _, onde = ln.partition("=")
    if not onde.startswith(TBIN + os.sep):
        shutil.rmtree(TMP, ignore_errors=True)
        quebrado("no shell que roda os adapters, `%s` resolve para %r, não para o stub em %s" % (e, onde, TBIN),
                 "rode o gate num terminal sem função `%s` exportada e sem BASH_ENV que mude o PATH." % e)
if len(sonda.stdout.splitlines()) != len(CLIS):
    shutil.rmtree(TMP, ignore_errors=True)
    quebrado("a sonda do PATH não respondeu: %s" % (sonda.stderr.strip() or sonda.stdout.strip()),
             "confira o bash em uso (%s)." % BASH)

# ── repositório descartável com um diff real ─────────────────────────────────────────────────────
REPO = os.path.join(TMP, "repo")
os.makedirs(os.path.join(REPO, "src"))


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=REPO, env=BASE_ENV, capture_output=True, text=True)


git("init", "-q")
topo = git("rev-parse", "--show-toplevel").stdout.strip()
if os.path.realpath(topo or "/") != os.path.realpath(REPO):
    quebrado("o repositório de teste resolve para %r, não para %s" % (topo, REPO),
             "rode o gate fora de um hook do git, ou sem GIT_DIR/GIT_WORK_TREE no ambiente.")
git("checkout", "-q", "-b", "main")
with open(os.path.join(REPO, "src/calculo.py"), "w") as h:
    h.write("def calcula(xs):\n    return sum(xs)\n")
git("add", "src/calculo.py")
c = git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "base")
if c.returncode != 0:
    shutil.rmtree(TMP, ignore_errors=True)
    quebrado("não consegui criar o repositório de teste: " + (c.stderr.strip() or c.stdout.strip()),
             "confira o git instalado (git --version).")
git("checkout", "-q", "-b", "feat")
with open(os.path.join(REPO, "src/calculo.py"), "w") as h:
    h.write("def calcula(xs):\n    total = sum(xs)\n    return total / len(xs)\n")
with open(os.path.join(REPO, ".git/info/exclude"), "a") as h:
    h.write("sdd/reports/reviews/\n")
REVS = os.path.join(REPO, "sdd/reports/reviews")


def usd(v):
    return ("%.4f" if v == 0 or v >= 0.0001 else "%.6f") % v


def ler_meta(pasta):
    m = {}
    for ln in (ler(os.path.join(pasta, "META.txt")) or "").splitlines():
        r = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if r:
            m[r.group(1)] = r.group(2)
    return m


def jsonl(p):
    out = []
    for ln in (ler(p) or "").splitlines():
        try:
            out.append(json.loads(ln))
        except ValueError:
            out.append(None)
    return out


def executa(nome, filas, *flags):
    """Roda um cenário: devolve (rc, saída, META, pasta, estado)."""
    est = os.path.join(TMP, "estado-" + nome)
    os.makedirs(est)
    env = dict(BASE_ENV, SDD_STUB_ESTADO=est)
    for e, f in filas.items():
        env["SDD_STUB_" + e.upper()] = f
    srv = subprocess.Popen([sys.executable, "-B", os.path.join(STUBS, "openrouter.py")], env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    porta_arq = os.path.join(est, "openrouter.porta")
    for _ in range(100):
        if os.path.exists(porta_arq) or srv.poll() is not None:
            break
        time.sleep(0.05)
    if not os.path.exists(porta_arq):
        srv.kill()
        srv.wait()
        shutil.rmtree(TMP, ignore_errors=True)
        quebrado("o stub da OpenRouter não subiu em 5 s (127.0.0.1)", "confira se o Python pode abrir porta local.")
    env["SDD_REVIEW_OPENROUTER_URL"] = "http://127.0.0.1:%s/api/v1/chat/completions" % open(porta_arq).read().strip()
    antes = set(os.listdir(REVS)) if os.path.isdir(REVS) else set()
    try:
        r = subprocess.run([BASH, AR, "--base", "main"] + list(flags), cwd=REPO, env=env, capture_output=True,
                           text=True, timeout=TETO_EXECUCAO, stdin=subprocess.DEVNULL)
        rc, saida = r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        rc, saida = None, "passou de %d s" % TETO_EXECUCAO
    finally:
        srv.terminate()
        try:
            srv.wait(timeout=5)
        except subprocess.TimeoutExpired:
            srv.kill()
            srv.wait()
    novas = sorted((set(os.listdir(REVS)) if os.path.isdir(REVS) else set()) - antes)
    pasta = os.path.join(REVS, novas[-1]) if novas else None
    return rc, saida, (ler_meta(pasta) if pasta else {}), pasta, est


def chamadas(est, e):
    t = ler(os.path.join(est, e + ".n"))
    return int(t) if t and t.strip().isdigit() else 0


def isolamento(rotulo, est, esperadas):
    sent = (ler(os.path.join(est, "sentinela")) or "").split()
    if sent:
        falha("%s: nenhuma engine fora do roteiro foi chamada" % rotulo, "chamadas fora da fila: " + ", ".join(sent))
    else:
        ok("%s: nenhuma engine fora do roteiro foi chamada" % rotulo)
    obtido = {e: chamadas(est, e) for e in ENGINES if chamadas(est, e) or e in esperadas}
    confere("%s: chamadas por engine" % rotulo, obtido, esperadas)


def esperado(e, cen):
    c = CEN.get((e, cen))
    if c is None:
        quebrado("cenarios.tsv sem a linha %s/%s" % (e, cen), "restaure sdd/review/stubs/cenarios.tsv do pacote.")
    return {"modelo": c[3], "custo": c[4], "te": c[5], "ts": c[6]}


def custo_estimado(e, modelo_rep, te, ts):
    """A mesma regra do script: tarifa do modelo reportado (ou do configurado, quando iguais), sobre o precos.tsv
    que o script resolve. Sem tarifa: $? (ou assinatura)."""
    conf = REG[e][2]
    t = PRECOS.get((e, modelo_rep if modelo_rep and modelo_rep != conf else conf))
    if t:
        return "≈US$ " + usd((int(te) * t[0] + int(ts) * t[1]) / 1e6)
    return "assinatura" if REG[e][3] == "assinatura" else "$?"


def campos(pref, e, cen, m, nota=""):
    """Asserções que discriminam a extração do adapter de `e` (com extração nula, o META mostraria outro valor)."""
    x = esperado(e, cen)
    rot = "%s (%s%s)" % (e, {"reviewer": "revisor", "auditor": "auditor"}[pref], nota)
    confere(rot + ": engine efetiva", m.get(pref + "_engine_efetivo"), e)
    if e == "claude":
        confere(rot + ": modelo de modelUsage", m.get(pref + "_modelo"), x["modelo"])
        confere(rot + ": custo de total_cost_usd", m.get(pref + "_custo"), "US$ " + usd(float(x["custo"])))
    elif e == "codex":
        confere(rot + ": tokens de turn.completed", (m.get(pref + "_tokens_entrada"), m.get(pref + "_tokens_saida")),
                (x["te"], x["ts"]))
        confere(rot + ": modelo e custo (a CLI não reporta)", (m.get(pref + "_modelo"), m.get(pref + "_custo")),
                (REG["codex"][2], "assinatura" if REG["codex"][3] == "assinatura" else "$?"))
    elif e == "gemini":
        confere(rot + ": modelo de stats.models", m.get(pref + "_modelo"), x["modelo"])
        confere(rot + ": tokens de stats.models", (m.get(pref + "_tokens_entrada"), m.get(pref + "_tokens_saida")),
                (x["te"], x["ts"]))
        confere(rot + ": custo sem tarifa", m.get(pref + "_custo"), custo_estimado("gemini", x["modelo"], x["te"], x["ts"]))
    elif e == "openrouter":
        confere(rot + ": modelo e provedor", m.get(pref + "_modelo"), x["modelo"] + " via StubProvider")
        if x["custo"] != "-":
            confere(rot + ": custo de usage.cost", m.get(pref + "_custo"), "US$ " + usd(float(x["custo"])))
        else:
            confere(rot + ": custo estimado pelo precos.tsv", m.get(pref + "_custo"),
                    custo_estimado("openrouter", x["modelo"], x["te"], x["ts"]))


def vereditos(rot, pasta):
    rv = jsonl(os.path.join(pasta, "reviewer.verdicts.jsonl")) if pasta else []
    av = jsonl(os.path.join(pasta, "auditor.verdicts.jsonl")) if pasta else []
    confere(rot + ": achados do revisor no jsonl", [(j or {}).get("achado") for j in rv], ["R1", "R2"])
    confere(rot + ": vereditos do auditor no jsonl", [((j or {}).get("achado"), (j or {}).get("veredito")) for j in av],
            [("R1", "AGREE"), ("R2", "AGREE")])


# ── 1. anel: cada engine revisa e audita, pelo adapter real ──────────────────────────────────────
print("── Gate offline da revisão adversarial (sem rede, sem crédito) ──")
print("Engines por stub: %s · registry: %s" % (", ".join(ENGINES), os.path.join(REVIEW, "registry.tsv")))
ANEL = (("claude", "codex"), ("codex", "gemini"), ("gemini", "openrouter"), ("openrouter", "claude"))
bearer_ok, deny_ok = [], []
for rv, au in ANEL:
    rot = "%s → %s" % (rv, au)
    filas = {rv: "revisor", au: "auditor"}
    rc, saida, m, pasta, est = executa("anel-%s-%s" % (rv, au), filas, "--reviewer", rv, "--auditor", au,
                                       "--no-revisor2")
    print("▸ %s" % rot)
    confere(rot + ": exit", rc, 0)
    if rc != 0:
        print("        saída: " + " | ".join(saida.strip().splitlines()[-3:]))
    confere(rot + ": achados e vereditos no META", (m.get("reviewer_achados"), m.get("auditor_vereditos")), ("2", "2"))
    vereditos(rot, pasta)
    campos("reviewer", rv, "revisor", m)
    campos("auditor", au, "auditor", m)
    isolamento(rot, est, {rv: 1, au: 1})
    if "openrouter" in (rv, au):
        bearer_ok.append((ler(os.path.join(est, "openrouter.1.auth")) or "") == "Bearer " + CHAVE)
        try:
            corpo = json.loads(ler(os.path.join(est, "openrouter.1.entrada")) or "{}")
        except ValueError:
            corpo = {}
        deny_ok.append((corpo.get("provider") or {}).get("data_collection") == "deny")

# ── 2. custo estimado e modelo sem preço (openrouter sem usage.cost) ─────────────────────────────
print("▸ custo sem usage.cost")
for cen in ("sem-custo", "modelo-sem-preco"):
    rc, saida, m, pasta, est = executa("custo-" + cen, {"openrouter": cen, "claude": "auditor"},
                                       "--reviewer", "openrouter", "--auditor", "claude", "--no-revisor2")
    confere("openrouter %s: exit" % cen, rc, 0)
    campos("reviewer", "openrouter", cen, m, ", " + cen)
    isolamento("openrouter %s" % cen, est, {"openrouter": 1, "claude": 1})

# ── 3. contrato ──────────────────────────────────────────────────────────────────────────────────
print("▸ contrato")
rc, saida, m, pasta, est = executa("68", {"claude": "revisor", "codex": "auditor-sem-bloco"},
                                   "--reviewer", "claude", "--auditor", "codex", "--no-revisor2")
confere("auditor sem o bloco de vereditos: exit 68", rc, 68)
confere("auditor sem o bloco: auditor_exit e nenhum auditor.verdicts.jsonl",
        (m.get("auditor_exit"), bool(pasta) and os.path.exists(os.path.join(pasta, "auditor.verdicts.jsonl"))),
        ("68", False))
confere("auditor sem o bloco: a saída diz REVIEW INVÁLIDA, não zero achados", "RESULTADO: REVIEW INVÁLIDA" in saida, True)
isolamento("68", est, {"claude": 1, "codex": 1})

rc, saida, m, pasta, est = executa("67-mesma", {"claude": "revisor"}, "--reviewer", "claude", "--auditor", "claude")
confere("mesma engine revisa e audita: exit 67", rc, 67)
isolamento("67 (mesma engine)", est, {})

rc, saida, m, pasta, est = executa("67-exclusao", {"gemini": "cota", "codex": "revisor"},
                                   "--reviewer", "gemini,codex", "--auditor", "codex", "--no-revisor2")
confere("revisor caiu na engine do auditor: exit 67", rc, 67)
confere("revisor caiu na engine do auditor: auditor excluído, revisor efetivo codex",
        (m.get("auditor_exit"), "excluída" in m.get("auditor_motivo", ""), m.get("reviewer_engine_efetivo")),
        ("67", True, "codex"))
isolamento("67 (exclusão)", est, {"gemini": 1, "codex": 1})

rc, saida, m, pasta, est = executa("misto", {"claude": "revisor", "gemini": "auditor-misto"},
                                   "--reviewer", "claude", "--auditor", "gemini", "--no-revisor2")
confere("auditor com DISAGREE e NOVO: exit 0", rc, 0)
confere("auditor com DISAGREE e NOVO: jsonl (achado, veredito, arquivo, linha, severidade)",
        [tuple((j or {}).get(k) for k in ("achado", "veredito", "arquivo", "linha", "severidade")) for j in
         (jsonl(os.path.join(pasta, "auditor.verdicts.jsonl")) if pasta else [])],
        [("R1", "DISAGREE_EVIDENCE", None, None, None), ("R2", "DISAGREE_CONCERN", None, None, None),
         ("N1", "NOVO", "src/calculo.py", 2, "LOW")])
confere("auditor com DISAGREE e NOVO: META (vereditos, convergência, sem desempate em MED)",
        (m.get("auditor_vereditos"), m.get("convergencia_1o_passe"), m.get("desempate_alvo")), ("3", "nao", "-"))
isolamento("vereditos mistos", est, {"claude": 1, "gemini": 1})

# a falha de credencial de CADA engine para tudo (exit 65) e nunca passa para a próxima da lista
PROXIMA = {"claude": ("codex", "gemini"), "codex": ("claude", "gemini"), "gemini": ("claude", "codex"),
           "openrouter": ("claude", "codex")}
for e in ENGINES:
    prox, aud = PROXIMA[e]
    rc, saida, m, pasta, est = executa("65-" + e, {e: "auth"}, "--reviewer", e + "," + prox, "--auditor", aud)
    confere("falha de credencial (%s): exit 65 e parou nela" % e, (rc, m.get("reviewer_engine_efetivo")), (65, e))
    isolamento("falha de credencial (%s): sem troca de engine" % e, est, {e: 1})

rc, saida, m, pasta, est = executa("429-cli", {"codex": "429,revisor", "openrouter": "auditor"},
                                   "--reviewer", "codex", "--auditor", "openrouter", "--no-revisor2")
confere("429 no codex: exit 0 na mesma engine", (rc, m.get("reviewer_engine_efetivo"), m.get("reviewer_fallback_usado")),
        (0, "codex", "nao"))
isolamento("429 (codex)", est, {"codex": 2, "openrouter": 1})

rc, saida, m, pasta, est = executa("429-http", {"claude": "revisor", "openrouter": "429,auditor"},
                                   "--reviewer", "claude", "--auditor", "openrouter", "--no-revisor2")
confere("429 HTTP na OpenRouter: exit 0 na mesma engine", (rc, m.get("auditor_engine_efetivo")), (0, "openrouter"))
isolamento("429 (openrouter)", est, {"claude": 1, "openrouter": 2})

rc, saida, m, pasta, est = executa("cota", {"gemini": "cota", "claude": "revisor", "codex": "auditor"},
                                   "--reviewer", "gemini,claude", "--auditor", "codex", "--no-revisor2")
confere("cota no gemini: a próxima engine da lista revisou",
        (rc, m.get("reviewer_engine_efetivo"), m.get("reviewer_fallback_usado")), (0, "claude", "sim"))
isolamento("cota (gemini → claude)", est, {"gemini": 1, "claude": 1, "codex": 1})

# ── 4. privacidade ───────────────────────────────────────────────────────────────────────────────
print("▸ privacidade")
confere("a OpenRouter recebeu Authorization: Bearer <chave gerada>", bool(bearer_ok) and all(bearer_ok), True)
confere("a OpenRouter recebeu provider.data_collection = deny", bool(deny_ok) and all(deny_ok), True)
vaz = []
for raiz_, _, arqs in os.walk(REVS):
    for a in arqs:
        try:
            if CHAVE.encode() in open(os.path.join(raiz_, a), "rb").read():
                vaz.append(os.path.relpath(os.path.join(raiz_, a), REVS))
        except OSError:
            pass
if vaz:
    falha("a chave não aparece em nenhum arquivo das revisões", "aparece em: " + ", ".join(vaz[:5]))
else:
    ok("a chave não aparece em nenhum arquivo das revisões")

shutil.rmtree(TMP, ignore_errors=True)
seg = int(round(time.time() - T0))
print("%d asserções, %d falha(s) em %d s" % (N[0], len(FALHAS), seg))
if FALHAS:
    print("RESULTADO: GATE VERMELHO")
    print("→ cada ❌ acima diz o campo e o valor lido; o adapter da engine citada não extrai mais o que a CLI devolve "
          "(ou o script mudou de comportamento). Corrija e rode o gate de novo.")
    sys.exit(2)
print("RESULTADO: GATE VERDE")
print("→ os 4 adapters leem a saída das engines e a revisão segue o contrato; a revisão real continua sendo a "
      "prova contra a CLI de hoje.")
PY
