#!/usr/bin/env bash
# adversarial-review.sh — revisão adversarial do SDD Open: uma engine REVISA um diff congelado, outra
# AUDITA a revisão (não revisa o código de novo); 2º revisor e desempate quando os gatilhos pedem.
# Doc: docs/adversarial-review.md. Engines: sdd/review/registry.tsv (sem cadeia padrão).
#
# Por que existe: revisor e crítico encadeados acham mais que dois revisores em paralelo, e uma revisão
# que não seguiu o formato não pode ser lida como "zero achados". Aqui cada falha vira um exit.
#
# USO-INICIO
#   adversarial-review.sh [<pasta>] [--reviewer ID[,ID…]] [--auditor ID[,ID…]] [--feature F]
#                         [--revisor2 ID | --no-revisor2] [--no-desempate] [--um-engine]
#                         [--base REF] [--paths "a b"] [--dry-run]
#       ID: engine do registry (review.registry) ou openrouter:<slug>. Sem flag, review.revisor1 e
#       review.auditor de sdd/config.yaml; a lista é a cadeia que o projeto escolhe (1º = padrão).
#       0 REVIEW COMPLETA · 64 uso, slot vazio, id desconhecido, diff vazio ou > 8 MB, pasta não ignorada
#       65 credencial (nunca troca de engine) · 66 CLI ausente · 67 auditor == revisor ou lista esgotada
#       68 resposta sem o bloco de vereditos (REVIEW INVÁLIDA — nunca "zero achados")
#   adversarial-review.sh --conferir [<pasta-da-revisão>] [--aceitar-sem-revisor2 "<motivo>"]
#       0 a revisão é desta versão do código (imprime a linha review_externo do ledger) · 2 não confere
#   adversarial-review.sh --ledger <ledger.yaml>
#       0 o ledger da release tem review_externo válido · 2 ausente ou não confere · 64 ilegível
# USO-FIM
#
# Saída: <review.output_dir>/EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>/ — META.txt, diff.patch, context-sdd.md,
# reviewer.md + reviewer.verdicts.jsonl, [reviewer2.*], auditor.md + auditor.verdicts.jsonl, [desempate.md].
# Lida por sdd/bin/sdd-fluxo.sh loop. Toda saída termina em `RESULTADO: <PALAVRA>` + `→ <o que fazer>`.
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib · sem `timeout` (o teto é do Python).

set -u

BIN="$(cd "$(dirname "$0")" && pwd)"
export SDD_REVIEW_BIN="$BIN"
export SDD_REVIEW_BASH="${BASH:-bash}"

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 adversarial-review: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

exec python3 -B - "$@" <<'PY'
import datetime, hashlib, json, os, re, shutil, signal, subprocess, sys, tempfile, time, fnmatch

BIN = os.environ["SDD_REVIEW_BIN"]
BASH = os.environ.get("SDD_REVIEW_BASH") or "bash"
ADAPTERS = os.environ.get("SDD_REVIEW_ADAPTERS") or os.path.join(BIN, "adapters")
PACOTE_REVIEW = os.path.normpath(os.path.join(BIN, "..", "review"))
ESPERA = int(os.environ.get("SDD_REVIEW_ESPERA") or "30")

# Limites do 2º revisor e do diff: constantes de propósito (decisão do brainstorm da F10). Mudar = 1 linha.
SEGUNDO_REVISOR_MIN_ARQUIVOS = 8      # arquivos no diff congelado
SEGUNDO_REVISOR_MIN_KB = 120          # wc -c do patch / 1024
SEGUNDO_REVISOR_MIN_CAMADAS = 2       # camadas de layers: tocadas
RASO_SEGUNDOS = 30                    # revisor abaixo disso, com 0 achados, conta como raso
DIFF_MAX_MB = 8                       # teto do diff congelado
TENTATIVAS_429 = 3                    # 1 chamada + 2 novas tentativas no limite passageiro
PASTAS_SDD = ("sdd/features", "sdd/reports", "sdd/reviews", "sdd/releases", "sdd/handoffs", "sdd/traces")
SEGMENTOS_SEGURANCA = {"auth", "login", "token", "tokens", "senha", "senhas", "password", "jwt"}
NOME_PAPEL = {"reviewer": "revisor", "revisor2": "2º revisor", "auditor": "auditor", "desempate": "desempate"}
VERBO_PAPEL = {"reviewer": "revisou", "revisor2": "revisou", "auditor": "auditou", "desempate": "desempatou"}

avisos = []


def sai(rc, palavra, motivo, seta, stream=sys.stderr):
    if motivo:
        print("🛑 adversarial-review: " + motivo, file=stream)
    print("RESULTADO: " + palavra, file=stream)
    print("→ " + seta, file=stream)
    sys.exit(rc)


def uso(motivo):
    sai(64, "PAROU", motivo, "rode `adversarial-review.sh --help` para ver o uso.")


def ler(caminho):
    try:
        with open(caminho, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def git(raiz, *args, env=None, binario=False):
    r = subprocess.run(["git", "-C", raiz] + list(args), capture_output=True, env=env)
    out = r.stdout if binario else r.stdout.decode("utf-8", "replace")
    return r.returncode, out, r.stderr.decode("utf-8", "replace")


def slot(caminho, bloco, chave):
    """Valor de bloco.chave num YAML de 1 nível; None se o arquivo ou a chave não existem."""
    texto = ler(caminho)
    if texto is None:
        return None
    dentro = False
    for ln in texto.splitlines():
        if ln and not ln[0].isspace() and not ln.startswith("#"):
            dentro = ln.split("#", 1)[0].strip() == bloco + ":"
            continue
        m = re.match(r"^\s+" + re.escape(chave) + r":\s*(.*)$", ln) if dentro else None
        if m:
            return m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
    return None


def bloco_inteiro(caminho, bloco):
    texto, dentro, saida = ler(caminho) or "", False, {}
    for ln in texto.splitlines():
        if ln and not ln[0].isspace() and not ln.startswith("#"):
            dentro = ln.split("#", 1)[0].strip() == bloco + ":"
            continue
        m = re.match(r"^\s+([A-Za-z0-9_.-]+):\s*(.*)$", ln) if dentro else None
        if m:
            saida[m.group(1)] = m.group(2).split(" #", 1)[0].strip().strip('"').strip("'")
    return saida


# ── argumentos ───────────────────────────────────────────────────────────────────────────────────
args = sys.argv[1:]
op = {"--reviewer": None, "--auditor": None, "--feature": None, "--revisor2": None, "--base": None,
      "--paths": None, "--conferir": None, "--ledger": None, "--aceitar-sem-revisor2": None}
flags = {"--no-revisor2": False, "--no-desempate": False, "--um-engine": False, "--dry-run": False}
pasta, modo, i = None, "revisar", 0
while i < len(args):
    a = args[i]
    if a in flags:
        flags[a] = True
    elif a == "--conferir":
        modo = "conferir"
        if i + 1 < len(args) and not args[i + 1].startswith("--"):
            op["--conferir"] = args[i + 1]
            i += 1
    elif a in op:
        if i + 1 >= len(args):
            uso("%s sem valor" % a)
        op[a] = args[i + 1]
        i += 1
        if a == "--ledger":
            modo = "ledger"
    elif a.startswith("-"):
        uso("opção desconhecida: " + a)
    elif pasta is None:
        pasta = a
    else:
        uso("argumento a mais: " + a)
    i += 1

if modo == "ledger":
    caminho = op["--ledger"]
    texto = ler(caminho)
    if texto is None:
        sai(64, "PAROU", "ledger ilegível: " + caminho, "confira o caminho do ledger da release.")
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    raiz = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()
    m = re.search(r"(?m)^\s*review_externo:\s*(.*?)\s*$", texto)
    if not m:
        sai(2, "LEDGER SEM REVIEW", "o ledger %s não tem a linha review_externo:" % caminho,
            "rode adversarial-review.sh --conferir e copie a linha que ele imprime, ou registre a dispensa "
            "(review_externo: dispensado — <motivo>) depois da pergunta D3.", sys.stdout)
    v = m.group(1).strip().strip('"').strip("'")
    d = re.match(r"^dispensado\s*(?:—|–|-{1,2})\s*(.+)$", v)
    if d:
        if len(d.group(1).strip()) >= 3:
            print("✅ review_externo: dispensado, com motivo registrado.")
            print("RESULTADO: LEDGER OK\n→ siga para o passo seguinte da release.")
            sys.exit(0)
        sai(2, "LEDGER SEM REVIEW", "a dispensa do review externo está sem motivo",
            "escreva o motivo em uma frase depois de 'dispensado —'.", sys.stdout)
    r2 = re.match(r"^(\S+)\s+sha256=([0-9a-f]{64})\b", v)
    if not r2:
        sai(2, "LEDGER SEM REVIEW", "review_externo malformado: " + v,
            "use a linha exata que adversarial-review.sh --conferir imprime.", sys.stdout)
    p = r2.group(1) if os.path.isabs(r2.group(1)) else os.path.join(raiz, r2.group(1))
    meta = ler(os.path.join(p, "META.txt"))
    if meta is None:
        sai(2, "LEDGER SEM REVIEW", "a pasta %s não existe aqui: rode na pasta da frente" % r2.group(1),
            "rode --ledger na pasta da frente (a pasta da revisão é ignorada pelo git e não viaja com o commit).",
            sys.stdout)
    hm = re.search(r"(?m)^diff_sha256\s*:\s*([0-9a-f]{64})\s*$", meta)
    if not hm or hm.group(1) != r2.group(2):
        sai(2, "LEDGER SEM REVIEW", "o sha256 do ledger não é o do META de " + r2.group(1),
            "rode --conferir de novo e copie a linha que ele imprimir.", sys.stdout)
    print("✅ review_externo: a revisão %s está registrada com o sha256 do META." % r2.group(1))
    print("RESULTADO: LEDGER OK\n→ siga para o passo seguinte da release.")
    sys.exit(0)

# ── raiz, config, registry ───────────────────────────────────────────────────────────────────────
alvo = os.path.abspath(pasta or os.getcwd())
rc, raiz, _ = git(alvo, "rev-parse", "--show-toplevel")
if rc != 0 or not raiz.strip():
    uso("%s não é um repositório git" % alvo)
raiz = raiz.strip()
cfg = os.path.join(raiz, "sdd/config.yaml")


def caminho_cfg(chave, padrao):
    v = slot(cfg, "review", chave)
    return v if v else padrao


saida_rel = caminho_cfg("output_dir", "sdd/reports/reviews").rstrip("/")
saida_abs = saida_rel if os.path.isabs(saida_rel) else os.path.join(raiz, saida_rel)

registry = caminho_cfg("registry", "sdd/review/registry.tsv")
registry = registry if os.path.isabs(registry) else os.path.join(raiz, registry)
if not os.path.isfile(registry) and not slot(cfg, "review", "registry"):
    registry = os.path.join(PACOTE_REVIEW, "registry.tsv")
dir_reg = os.path.dirname(registry)
prompts_dir = os.path.join(dir_reg, "prompts")
if not os.path.isdir(prompts_dir):
    prompts_dir = os.path.join(PACOTE_REVIEW, "prompts")
precos_arq = os.path.join(dir_reg, "precos.tsv")
if not os.path.isfile(precos_arq):
    precos_arq = os.path.join(PACOTE_REVIEW, "precos.tsv")

COLUNAS = ("engine", "adapter", "modelo", "cobranca", "papeis", "timeout_s", "sinal_auth",
           "sinal_transitorio", "sinal_persistente")


def ler_registry():
    texto = ler(registry)
    if texto is None:
        uso("registry ilegível: " + registry)
    linhas, ordem = {}, []
    for n, ln in enumerate(texto.splitlines(), 1):
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        c = ln.split("\t")
        if len(c) != len(COLUNAS):
            uso("%s:%d tem %d colunas (esperado %d, separadas por TAB)" % (registry, n, len(c), len(COLUNAS)))
        d = dict(zip(COLUNAS, [x.strip() for x in c]))
        try:
            d["timeout_s"] = int(d["timeout_s"])
            for s in ("sinal_auth", "sinal_transitorio", "sinal_persistente"):
                re.compile(d[s])
        except (ValueError, re.error) as e:
            uso("%s:%d inválida: %s" % (registry, n, e))
        d["papeis"] = [p.strip() for p in d["papeis"].split(",") if p.strip()]
        linhas[d["engine"]] = d
        ordem.append(d["engine"])
    return linhas, ordem


REG, ORDEM = ler_registry()


def resolve(id_, papel):
    base, slug = id_, None
    if ":" in id_:
        base, slug = id_.split(":", 1)
    if base not in REG:
        uso("engine desconhecida: '%s' — válidas: %s (registry: %s; engine nova = 1 linha)"
            % (id_, ", ".join(ORDEM), os.path.relpath(registry, raiz)))
    d = dict(REG[base])
    d["id"] = id_
    if slug:
        d["modelo"] = slug
    if not os.path.isfile(os.path.join(ADAPTERS, d["adapter"] + ".sh")):
        uso("adapter ausente: %s.sh em %s" % (d["adapter"], ADAPTERS))
    papel_reg = "revisor" if papel in ("reviewer", "revisor2") else papel
    if papel_reg not in d["papeis"]:
        uso("a engine %s não tem o papel %s no registry" % (id_, papel_reg))
    return d


def lista(flag, chave, papel):
    v = op[flag] if op[flag] is not None else (slot(cfg, "review", chave) or "")
    ids = [x.strip() for x in v.split(",") if x.strip()]
    return [resolve(x, papel) for x in ids]


def base_id(id_):
    return (id_ or "").split(":", 1)[0]


def rotulo(id_):
    return re.sub(r"[^A-Za-z0-9._-]", "-", id_)


def diversidade(a, b):
    if a["id"] == b["id"]:
        return "nenhuma"
    return "modelo" if a["adapter"] == b["adapter"] else "vendor"


# ── diff congelado ───────────────────────────────────────────────────────────────────────────────
def resolve_base(base):
    if base:
        if git(raiz, "rev-parse", "--verify", "--quiet", base + "^{commit}")[0] != 0:
            uso("--base %s não resolve para um commit" % base)
        return base
    db = slot(cfg, "project", "default_branch") or "main"
    for cand in ("origin/" + db, db):
        if git(raiz, "rev-parse", "--verify", "--quiet", cand + "^{commit}")[0] == 0:
            return cand
    uso("nem origin/%s nem %s existem: passe --base <ref>" % (db, db))


def congelar(base, paths):
    rc, mb, err = git(raiz, "merge-base", base, "HEAD")
    if rc != 0:
        uso("sem merge-base entre %s e HEAD: %s" % (base, err.strip()))
    mb = mb.strip()
    excl = [":(exclude)" + saida_rel] if not os.path.isabs(saida_rel) else []
    if paths:
        spec = paths.split() + excl
    else:
        spec = ["."] + excl + [":(exclude)" + p for p in PASTAS_SDD]
    tmp = tempfile.mkdtemp(prefix="sdd-review-idx-")
    try:
        idx = git(raiz, "rev-parse", "--git-path", "index")[1].strip()
        idx = idx if os.path.isabs(idx) else os.path.join(raiz, idx)
        tidx = os.path.join(tmp, "index")
        if os.path.isfile(idx):
            # copy2 preserva o mtime: com mtime novo o git perde a checagem de índice "racy" e uma edição do
            # mesmo tamanho, feita no mesmo segundo do commit, some do diff
            shutil.copy2(idx, tidx)
        env = dict(os.environ, GIT_INDEX_FILE=tidx)
        _, novos, _ = git(raiz, "ls-files", "--others", "--exclude-standard", "-z", "--", *spec, env=env)
        nomes = [n for n in novos.split("\0") if n]
        for k in range(0, len(nomes), 200):
            git(raiz, "add", "--intent-to-add", "--", *nomes[k:k + 200], env=env)
        rc, patch, err = git(raiz, "-c", "core.quotepath=true", "diff", "--binary", "--no-color", "--no-ext-diff",
                             "--no-renames", "--diff-algorithm=myers", "--src-prefix=a/", "--dst-prefix=b/",
                             "-U3", "--inter-hunk-context=0", "-O/dev/null", "--no-textconv",
                             mb, "--", *spec, env=env, binario=True)
        if rc != 0:
            uso("git diff falhou: " + err.strip())
        # os nomes vêm do git com -z, nunca do cabeçalho do patch: um caminho com acento, espaço ou aspas sai
        # entre aspas no cabeçalho e escaparia dos gatilhos de segurança e da contagem de arquivos
        _, nomes_z, _ = git(raiz, "diff", "--name-only", "-z", "--no-renames", "-O/dev/null", mb, "--", *spec, env=env)
        arquivos = [n for n in nomes_z.split("\0") if n]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return mb, patch, arquivos


# ── --conferir ───────────────────────────────────────────────────────────────────────────────────
def ler_meta(texto):
    meta = {}
    for ln in (texto or "").splitlines():
        m = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if m:
            meta[m.group(1)] = m.group(2)
    return meta


if modo == "conferir":
    def nao(motivo, seta):
        sai(2, "NÃO CONFERE", motivo, seta, sys.stdout)
    p = op["--conferir"]
    if p:
        dirrev = p if os.path.isabs(p) else os.path.join(raiz, p)
    else:
        cands = sorted(d for d in (os.listdir(saida_abs) if os.path.isdir(saida_abs) else [])
                       if d.startswith("EXTERNAL_REVIEW_")
                       and ler_meta(ler(os.path.join(saida_abs, d, "META.txt"))).get("paths", "-") in ("", "-"))
        if not cands:
            nao("nenhuma revisão em %s" % saida_rel, "rode adversarial-review.sh nesta frente, ou registre a dispensa (pergunta D3).")
        dirrev = os.path.join(saida_abs, cands[-1])
    meta = ler_meta(ler(os.path.join(dirrev, "META.txt")))
    rel = os.path.relpath(dirrev, raiz)
    if not meta:
        nao("%s/META.txt ausente" % rel, "aponte a pasta de uma revisão (EXTERNAL_REVIEW_…).")
    paths = meta.get("paths", "-")
    if paths not in ("", "-"):
        nao("a revisão %s cobre só --paths %s, não o diff inteiro desta frente" % (rel, paths),
            "rode a revisão sem --paths (a da release revisa o código, não só o DESIGN).")
    _, patch, _ = congelar(meta.get("base") or resolve_base(None), None if paths in ("", "-") else paths)
    sha = hashlib.sha256(patch).hexdigest()
    if sha != meta.get("diff_sha256"):
        nao("o código mudou depois da revisão %s (sha256 diferente)" % rel, "rode a revisão de novo sobre esta versão.")
    if meta.get("reviewer_exit") != "0" or meta.get("auditor_exit") != "0":
        nao("a revisão %s não completou (reviewer_exit=%s, auditor_exit=%s)" % (
            rel, meta.get("reviewer_exit"), meta.get("auditor_exit")), "rode a revisão de novo.")
    conv = meta.get("convergencia_1o_passe", "")
    if conv.startswith("n/a (revisor1 raso") or conv.startswith("n/a (2º revisor raso") or \
            (meta.get("revisor1_raso") == "sim" and meta.get("revisor2_exit", "-") != "0"):
        nao("a revisão %s foi rasa (%s): não conta como revisão" % (rel, conv or "revisor1_raso: sim"),
            "rode a revisão de novo, com outra engine se preciso.")
    r2 = meta.get("revisor2_exit", "-")
    extra = ""
    if r2 not in ("0", "-", ""):
        mot = (op["--aceitar-sem-revisor2"] or "").strip()
        if len(mot) < 3:
            nao("o 2º revisor foi acionado e não deu resultado (revisor2_exit=%s)" % r2,
                "rode de novo com outra engine (--revisor2) ou registre a dispensa com --aceitar-sem-revisor2 \"<motivo>\".")
        extra = " revisor2=dispensado — " + mot
    print("✅ a revisão %s é desta versão do código (sha256 igual)." % rel)
    print("review_externo: %s sha256=%s diversidade=%s%s" % (rel, sha, meta.get("diversidade", "-"), extra))
    print("RESULTADO: CONFERE\n→ copie a linha review_externo para o ledger da release.")
    sys.exit(0)

# ── revisar: papéis ──────────────────────────────────────────────────────────────────────────────
revisores = lista("--reviewer", "revisor1", "reviewer")
if not revisores:
    uso("nenhum revisor: preencha review.revisor1 em sdd/config.yaml ou passe --reviewer (válidas: %s)" % ", ".join(ORDEM))
auditores = lista("--auditor", "auditor", "auditor")
if not auditores and flags["--um-engine"]:
    auditores = [resolve(r["id"], "auditor") for r in revisores]
if not auditores:
    uso("nenhum auditor: preencha review.auditor em sdd/config.yaml ou passe --auditor (válidas: %s)" % ", ".join(ORDEM))
if auditores[0]["id"] == revisores[0]["id"] and not flags["--um-engine"]:
    sai(67, "PAROU", "o auditor (%s) é a mesma engine do revisor: ninguém audita a própria revisão" % auditores[0]["id"],
        "escolha outra engine para auditar (review.auditor) ou rode com --um-engine")
if flags["--no-revisor2"] and op["--revisor2"]:
    uso("--revisor2 e --no-revisor2 juntos")
r2_forcado = resolve(op["--revisor2"], "revisor2") if op["--revisor2"] else None

try:
    max_kb = int(caminho_cfg("context_max_kb", "180"))
    assert max_kb > 0
except (ValueError, AssertionError):
    uso("review.context_max_kb precisa ser um inteiro positivo (KB)")

base = resolve_base(op["--base"])
mb, patch, arqs = congelar(base, op["--paths"])
if not patch.strip():
    uso("o diff contra %s está vazio: a revisão não teria o que revisar" % base)
if len(patch) > DIFF_MAX_MB * 1024 * 1024:
    uso("o diff tem %d KB, acima do teto de %d MB: use --paths para revisar por partes" % (len(patch) // 1024, DIFF_MAX_MB))
sha = hashlib.sha256(patch).hexdigest()
head = git(raiz, "rev-parse", "HEAD")[1].strip()

# ── contexto SDD ─────────────────────────────────────────────────────────────────────────────────
docs, ctx_txt, cortado = [], "", "-"
F = op["--feature"]
if F:
    for d, nome in (("sdd/features", "BRAINSTORM_%s.md"), ("sdd/features", "DEFINE_%s.md"),
                    ("sdd/features", "DESIGN_%s.md"), ("sdd/reports", "BUILD_REPORT_%s.md")):
        t = ler(os.path.join(raiz, d, nome % F))
        if t is not None:
            docs.append((nome % F, t))
    def junta(ds):
        return "".join("### %s\n\n%s\n\n" % (n, t) for n, t in ds)
    teto = max_kb * 1024
    ctx_txt = junta(docs)
    if len(ctx_txt.encode("utf-8")) > teto and docs and docs[0][0].startswith("BRAINSTORM"):
        docs = docs[1:]
        cortado = "BRAINSTORM"
        ctx_txt = junta(docs)
    if len(ctx_txt.encode("utf-8")) > teto:
        marca = "\n[… cortado: teto de %d KB do contexto SDD (review.context_max_kb) …]\n" % max_kb
        ctx_txt = ctx_txt.encode("utf-8")[:teto - len(marca.encode("utf-8"))].decode("utf-8", "ignore") + marca
        cortado = (cortado + " + " if cortado != "-" else "") + "corte em %d KB" % max_kb
else:
    avisos.append("⚠️ sem --feature: a revisão não leu BRAINSTORM, DEFINE nem DESIGN, e decisões já documentadas "
                  "podem voltar como achado")

# ── pasta da revisão ignorada pelo git (R9) ──────────────────────────────────────────────────────
if not os.path.isabs(saida_rel) or os.path.commonpath([os.path.abspath(saida_abs), raiz]) == raiz:
    relsaida = os.path.relpath(saida_abs, raiz)
    if git(raiz, "check-ignore", "-q", relsaida + "/.sonda")[0] != 0:
        print("🛑 a pasta %s não está ignorada pelo git: o diff e as respostas das engines iriam para o "
              "repositório." % relsaida, file=sys.stderr)
        print("RESULTADO: PAROU", file=sys.stderr)
        print("→ rode: printf '%%s\\n' '%s/' >> \"$(git rev-parse --git-common-dir)/info/exclude\"" % relsaida,
              file=sys.stderr)
        sys.exit(64)


# ── gatilhos do 2º revisor (parte que não depende da resposta) ───────────────────────────────────
def gatilho_estatico():
    globs = [g.strip() for g in (slot(cfg, "review", "security_globs") or "").split(",") if g.strip()]
    camadas = {k: v for k, v in bloco_inteiro(cfg, "layers").items() if v}
    if camadas.get("sql"):
        globs.append(camadas["sql"])
    for a in arqs:
        segs = set(re.split(r"[/._-]+", a.lower()))
        if segs & SEGMENTOS_SEGURANCA or any(fnmatch.fnmatch(a, g) for g in globs):
            return "segurança (%s)" % a
    if len(arqs) >= SEGUNDO_REVISOR_MIN_ARQUIVOS:
        return "%d arquivos (limiar %d)" % (len(arqs), SEGUNDO_REVISOR_MIN_ARQUIVOS)
    if len(patch) // 1024 >= SEGUNDO_REVISOR_MIN_KB:
        return "%d KB (limiar %d)" % (len(patch) // 1024, SEGUNDO_REVISOR_MIN_KB)
    tocadas = {k for k, g in camadas.items() for a in arqs if fnmatch.fnmatch(a, g)}
    if len(tocadas) >= SEGUNDO_REVISOR_MIN_CAMADAS:
        return "%d camadas (limiar %d)" % (len(tocadas), SEGUNDO_REVISOR_MIN_CAMADAS)
    return None


gat = gatilho_estatico()


def disponivel(d):
    r = subprocess.run([BASH, "-c", 'source "$1"; adapter_disponivel "$2"', "_",
                        os.path.join(ADAPTERS, d["adapter"] + ".sh"), d["modelo"]],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


if flags["--dry-run"]:
    print("Plano (nada foi enviado a nenhuma engine):")
    print("  revisor : " + ", ".join("%s (%s)" % (d["id"], d["modelo"]) for d in revisores))
    print("  auditor : " + ", ".join("%s (%s)" % (d["id"], d["modelo"]) for d in auditores))
    print("  diversidade: " + diversidade(revisores[0], auditores[0]))
    print("  2º revisor: " + ("dispensado (--no-revisor2)" if flags["--no-revisor2"] else
                              (gat or "sem gatilho no diff (o revisor raso ainda pode acionar)")))
    print("  diff: %d arquivo(s), %d KB, base %s, merge-base %s" % (len(arqs), len(patch) // 1024, base, mb[:12]))
    print("  diff_sha256: " + sha)
    print("  contexto: %d documento(s) SDD, %d KB%s" % (len(docs), len(ctx_txt.encode("utf-8")) // 1024,
                                                       "" if cortado == "-" else ", cortado: " + cortado))
    for a in avisos:
        print(a)
    print("RESULTADO: PLANO\n→ rode sem --dry-run para revisar.")
    sys.exit(0)

quando = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
dirrev = os.path.join(saida_abs, "EXTERNAL_REVIEW_" + quando)
k = 2
while os.path.exists(dirrev):
    dirrev = os.path.join(saida_abs, "EXTERNAL_REVIEW_%s-%d" % (quando, k))
    k += 1
os.makedirs(dirrev)
rel_rev = os.path.relpath(dirrev, raiz)
open(os.path.join(dirrev, "diff.patch"), "wb").write(patch)
open(os.path.join(dirrev, "context-sdd.md"), "w", encoding="utf-8").write(ctx_txt)
TMP = tempfile.mkdtemp(prefix="sdd-review-")
VAZIA = os.path.join(TMP, "cwd")
os.makedirs(VAZIA)
diff_txt = patch.decode("utf-8", "replace")


def prompt_de(nome):
    t = ler(os.path.join(prompts_dir, nome + ".md"))
    if t is None:
        uso("prompt ausente: %s/%s.md" % (prompts_dir, nome))
    return re.sub(r"^\s*<!--.*?-->\s*", "", t, flags=re.S)


def material(extra=""):
    return ("\n\n## CONTEXTO SDD\n\n" + (ctx_txt or "(nenhum documento SDD foi fornecido)\n")
            + "\n\n## DIFF\n\n" + diff_txt + extra)


# ── chamada de um papel ──────────────────────────────────────────────────────────────────────────
def adapter_cmd(d, funcao, *a):
    return [BASH, "-c", 'f="$1"; shift; source "$f"; ' + funcao + ' "$@"', "_",
            os.path.join(ADAPTERS, d["adapter"] + ".sh")] + list(a)


def invocar(d, prompt, saida):
    p = subprocess.Popen(adapter_cmd(d, "adapter_invocar", d["modelo"], prompt, saida, saida + ".err"),
                         cwd=VAZIA, stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        return p.wait(timeout=d["timeout_s"]), False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except OSError:
            pass
        p.wait()
        return 124, True


def extrair(d, saida):
    r = subprocess.run(adapter_cmd(d, "adapter_extrair", saida), capture_output=True, text=True)
    try:
        j = json.loads(r.stdout.strip().splitlines()[-1])
        return j if isinstance(j, dict) else {}
    except (ValueError, IndexError):
        return {}


def credencial(d):
    r = subprocess.run(adapter_cmd(d, "adapter_credencial"), capture_output=True, text=True)
    return r.stdout.strip() or "a credencial da engine"


def classe(rc, timeout, texto, bruto, d):
    if rc == 0 and not timeout and texto:
        return "ok"
    if rc == 65 or re.search(d["sinal_auth"], bruto):
        return "auth"
    if rc == 66:
        return "launcher"
    if timeout:
        return "timeout"
    if re.search(d["sinal_transitorio"], bruto):
        return "transitorio"
    return "persistente"


def papel(nome, cands, prompt_txt, excluir=()):
    """Roda o papel na lista de engines; devolve o registro do META."""
    reg = {"engine_default": cands[0]["id"] if cands else "-", "engine_efetivo": "-", "fallback_usado": "nao",
           "motivo": "-", "exit": "-", "segundos": 0, "texto": "", "tokens_entrada": None, "tokens_saida": None,
           "modelo": None, "custo_usd": None, "linha": None, "credencial": None}
    arq_p = os.path.join(TMP, nome + "-prompt.md")
    open(arq_p, "w", encoding="utf-8").write(prompt_txt)
    causas, motivos, ultimo = [], [], None
    for d in cands:
        if d["id"] in excluir:
            motivos.append("%s excluída (já tem outro papel nesta revisão)" % d["id"])
            causas.append("exclusao")
            continue
        ultimo = d
        print("▶ %s: %s (%s) — até %d min" % (NOME_PAPEL[nome], d["id"], d["modelo"], max(1, d["timeout_s"] // 60)),
              flush=True)
        tent = 0
        while True:
            tent += 1
            saida = os.path.join(TMP, "%s-%s-%d.out" % (nome, rotulo(d["id"]), tent))
            t_cham = time.time()
            rc, tmo = invocar(d, arq_p, saida)
            reg["segundos"] = int(round(time.time() - t_cham))
            ext = extrair(d, saida) if rc == 0 and not tmo else {}
            texto = ext.get("texto") or ""
            bruto = (ler(saida) or "") + "\n" + (ler(saida + ".err") or "")
            c = classe(rc, tmo, texto, bruto, d)
            if c == "transitorio" and tent < TENTATIVAS_429:
                time.sleep(ESPERA)
                continue
            break
        if c == "ok":
            reg.update(ext)
            reg.update({"engine_efetivo": d["id"], "exit": "0", "linha": d,
                        "fallback_usado": "sim" if d["id"] != reg["engine_default"] else "nao"})
            if reg["fallback_usado"] == "sim":
                reg["motivo"] = "; ".join(motivos)
            break
        if c == "auth":
            reg.update({"engine_efetivo": d["id"], "exit": "65", "linha": d, "credencial": credencial(d),
                        "motivo": "falha de credencial em %s" % d["id"]})
            break
        mot = {"launcher": "CLI de %s fora do PATH", "timeout": "%s passou do teto de tempo",
               "transitorio": "%s seguiu no limite passageiro (429) depois de 3 tentativas",
               "persistente": "%s falhou (cota, cobrança ou erro)"}[c] % d["id"]
        motivos.append(mot)
        causas.append(c)
    else:
        reg["exit"] = "66" if causas and all(x == "launcher" for x in causas) else "67"
        reg["motivo"] = "; ".join(motivos) or "nenhuma engine na lista"
        if ultimo is not None:
            # a última engine tentada fica registrada: com "-", o loop leria "não houve este papel"
            reg["engine_efetivo"] = ultimo["id"]
            reg["fallback_usado"] = "sim" if ultimo["id"] != reg["engine_default"] else "nao"
    if reg["fallback_usado"] == "sim" and reg["exit"] == "0":
        avisos.append("⚠️ o %s previsto (%s) falhou (%s); quem %s foi %s" % (
            NOME_PAPEL[nome], reg["engine_default"], reg["motivo"], VERBO_PAPEL[nome], reg["engine_efetivo"]))
    return reg


def bloco(texto):
    """Linhas JSON do último bloco <<<VERDICTS … VERDICTS>>>; None se ausente."""
    ls = texto.splitlines()
    ini = [k for k, l in enumerate(ls) if l.strip() == "<<<VERDICTS"]
    if not ini:
        return None
    fim = [k for k, l in enumerate(ls) if l.strip() == "VERDICTS>>>" and k > ini[-1]]
    if not fim:
        return None
    return [l.strip() for l in ls[ini[-1] + 1:fim[0]] if l.strip() and not l.strip().startswith("```")]


CHAVES_REV = ("achado", "arquivo", "linha", "severidade", "confianca", "resumo")


def vereditos_revisor(texto):
    ls = bloco(texto)
    if ls is None:
        return None, "bloco <<<VERDICTS ausente ou malformado"
    out = []
    for l in ls:
        try:
            j = json.loads(l)
        except ValueError:
            return None, "linha do bloco não é JSON: " + l[:80]
        if not isinstance(j, dict) or any(k not in j for k in CHAVES_REV) or not str(j["achado"]).strip():
            return None, "linha do bloco sem as chaves obrigatórias: " + l[:80]
        j["achado"] = str(j["achado"]).strip()
        s = str(j["severidade"]).upper()
        s = "MED" if s == "MEDIUM" else s
        if s not in ("HIGH", "MED", "LOW"):
            return None, "severidade inválida: " + l[:80]
        j["severidade"] = s
        out.append(j)
    return out, None


def vereditos_auditor(texto):
    ls = bloco(texto)
    if ls is None:
        return None, "bloco <<<VERDICTS ausente ou malformado"
    out = []
    for l in ls:
        try:
            j = json.loads(l)
        except ValueError:
            return None, "linha do bloco não é JSON: " + l[:80]
        if isinstance(j, dict) and "achado" in j:
            j["achado"] = str(j["achado"]).strip()
        ok = isinstance(j, dict) and j.get("achado", "") != "" and \
            j.get("veredito") in ("AGREE", "DISAGREE_EVIDENCE", "DISAGREE_CONCERN", "NOVO")
        if ok and j["veredito"] == "NOVO":
            s = str(j.get("severidade", "")).upper()
            j["severidade"] = "MED" if s == "MEDIUM" else s
            ok = j["severidade"] in ("HIGH", "MED", "LOW")
        if not ok:
            return None, "linha do bloco inválida para o auditor: " + l[:80]
        out.append(j)
    return out, None


def grava(nome, linhas):
    with open(os.path.join(dirrev, nome), "w", encoding="utf-8") as h:
        for j in linhas:
            h.write(json.dumps(j, ensure_ascii=False) + "\n")


PRECOS = {}
for ln in (ler(precos_arq) or "").splitlines():
    c = ln.split("\t")
    if ln.startswith("#") or len(c) != 6:
        continue
    try:
        PRECOS[(c[0].strip(), c[1].strip())] = (float(c[2]), float(c[3]))
    except ValueError:
        pass


def usd(v):
    """4 casas; abaixo de 0,0001, 6 casas — um custo conhecido nunca aparece como 0,0000."""
    return ("%.4f" if v == 0 or v >= 0.0001 else "%.6f") % v


def custo(reg):
    d = reg["linha"]
    if d is None or reg["exit"] in ("-",):
        return "n/d"
    if isinstance(reg["custo_usd"], (int, float)):
        return "US$ " + usd(reg["custo_usd"])
    t = PRECOS.get((d["engine"], d["modelo"]))
    if t and isinstance(reg["tokens_entrada"], int) and isinstance(reg["tokens_saida"], int):
        return "≈US$ " + usd((reg["tokens_entrada"] * t[0] + reg["tokens_saida"] * t[1]) / 1e6)
    return "assinatura" if d["cobranca"] == "assinatura" else "$?"


# ── revisor ──────────────────────────────────────────────────────────────────────────────────────
meta_extra = {}
rev = papel("reviewer", revisores, prompt_de("reviewer") + material())
rev_v, aud_v, r2_v = [], [], []
if rev["exit"] == "0":
    open(os.path.join(dirrev, "reviewer.md"), "w", encoding="utf-8").write(rev["texto"])
    rev_v, erro = vereditos_revisor(rev["texto"])
    if rev_v is None:
        rev.update({"exit": "68", "motivo": "%s: %s" % (rev["engine_efetivo"], erro)})
        rev_v = []
rev["achados"] = len(rev_v)
raso1 = rev["exit"] == "0" and rev["segundos"] < RASO_SEGUNDOS and not rev_v

# ── 2º revisor ───────────────────────────────────────────────────────────────────────────────────
r2 = None
gat2 = gat or ("revisor1 raso (%ds, 0 achados)" % rev["segundos"] if raso1 else None)
if rev["exit"] != "0":
    gatilho = "-"
elif flags["--no-revisor2"]:
    gatilho = (gat2 + " — dispensado por --no-revisor2") if gat2 else "diff sem gatilho de risco — 1 revisor"
elif gat2:
    gatilho = gat2
    excl = {base_id(rev["engine_efetivo"]), base_id(auditores[0]["id"])}
    if r2_forcado:
        cand = [r2_forcado]
    else:
        cand = [resolve(e, "revisor2") for e in ORDEM if "revisor" in REG[e]["papeis"] and e not in excl]
        cand = [d for d in cand if disponivel(d)][:1]
    if not cand:
        r2 = {"engine_efetivo": "indisponível", "engine_default": "-", "exit": "67", "segundos": 0, "achados": 0,
              "motivo": "nenhuma engine disponível fora do revisor e do auditor", "linha": None,
              "fallback_usado": "nao", "tokens_entrada": None, "tokens_saida": None, "modelo": None}
        avisos.append("⚠️ o 2º revisor (nenhuma engine) não tinha engine disponível: a revisão vale só com a "
                      "dispensa registrada no ledger")
    else:
        r2 = papel("revisor2", cand, prompt_de("reviewer") + material())
        r2_v = []
        if r2["exit"] == "0":
            open(os.path.join(dirrev, "reviewer2.md"), "w", encoding="utf-8").write(r2["texto"])
            r2_v, erro = vereditos_revisor(r2["texto"])
            if r2_v is None:
                r2.update({"exit": "68", "motivo": "%s: %s" % (r2["engine_efetivo"], erro)})
                r2_v = []
        r2["achados"] = len(r2_v)
        if r2["exit"] != "0":
            avisos.append("⚠️ o 2º revisor (%s) falhou (%s): a revisão vale só com a dispensa registrada no ledger"
                          % (r2["engine_efetivo"], r2["motivo"]))
else:
    gatilho = "diff sem gatilho de risco — 1 revisor"

dois = r2 is not None and r2["exit"] == "0"
if dois:
    for j in rev_v:
        j["achado"] = "%s@%s" % (j["achado"], rotulo(rev["engine_efetivo"]))
    for j in r2_v:
        j["achado"] = "%s@%s" % (j["achado"], rotulo(r2["engine_efetivo"]))
if rev["exit"] == "0":
    grava("reviewer.verdicts.jsonl", rev_v)
if dois:
    grava("reviewer2.verdicts.jsonl", r2_v)
raso2 = dois and r2["segundos"] < RASO_SEGUNDOS and not r2_v

# ── auditor ──────────────────────────────────────────────────────────────────────────────────────
aud = None
origem = {}
if rev["exit"] == "0":
    blocos = [(rev, rev_v, "reviewer.md")] + ([(r2, r2_v, "reviewer2.md")] if dois else [])
    rv = ""
    for r, vs, _ in blocos:
        for j in vs:
            origem[j["achado"]] = r["engine_efetivo"]
        rv += "\n\n### Revisão de %s\n\nCite os achados desta revisão por estes identificadores: %s\n\n%s\n" % (
            r["engine_efetivo"], ", ".join(j["achado"] for j in vs) or "(nenhum achado)", r["texto"])
        if dois:
            rv += "\nAchados desta revisão, com os identificadores a citar:\n" + "\n".join(
                json.dumps(j, ensure_ascii=False) for j in vs) + "\n"
    excl = set() if flags["--um-engine"] else {rev["engine_efetivo"]} | ({r2["engine_efetivo"]} if dois else set())
    aud = papel("auditor", auditores, prompt_de("auditor") + material("\n\n## REVISÕES\n" + rv), excluir=excl)
    if aud["exit"] == "0":
        open(os.path.join(dirrev, "auditor.md"), "w", encoding="utf-8").write(aud["texto"])
        aud_v, erro = vereditos_auditor(aud["texto"])
        if aud_v is None:
            aud.update({"exit": "68", "motivo": "%s: %s" % (aud["engine_efetivo"], erro)})
            aud_v = []
        grava("auditor.verdicts.jsonl", aud_v)
    aud["vereditos"] = len(aud_v)

todos_rev = rev_v + (r2_v if dois else [])


def veredito_de(id_):
    por_id = {j["achado"]: j["veredito"] for j in aud_v}
    if id_ in por_id:
        return por_id[id_]
    b = id_.split("@", 1)[0]
    if b != id_ and sum(1 for x in todos_rev if x["achado"].split("@", 1)[0] == b) == 1:
        return por_id.get(b)
    return None


# ── desempate ────────────────────────────────────────────────────────────────────────────────────
des = {"alvo": "-", "engine": "-", "decisao": "-", "reg": None}
if aud is not None and aud["exit"] == "0" and not flags["--no-desempate"]:
    alvo = next((j for j in todos_rev if j["severidade"] == "HIGH" and veredito_de(j["achado"]) == "DISAGREE_EVIDENCE"),
                None)
    if alvo:
        des["alvo"] = alvo["achado"]
        excl = {base_id(origem.get(alvo["achado"])), base_id(aud["engine_efetivo"])}
        cand = [resolve(e, "desempate") for e in ORDEM if "desempate" in REG[e]["papeis"] and e not in excl]
        cand = [d for d in cand if disponivel(d)][:1]
        if not cand:
            des["engine"] = "indisponível"
        else:
            just = next((j for j in aud_v if j["achado"] in (alvo["achado"], alvo["achado"].split("@", 1)[0])), {})
            extra = ("\n\n## ACHADO\n\n" + json.dumps(alvo, ensure_ascii=False)
                     + "\n\n## AUDITORIA DO ACHADO\n\n" + json.dumps(just, ensure_ascii=False) + "\n")
            dr = papel("desempate", cand, prompt_de("desempate") + material(extra))
            des["engine"], des["reg"] = dr["engine_efetivo"], dr
            if dr["exit"] == "0":
                open(os.path.join(dirrev, "desempate.md"), "w", encoding="utf-8").write(dr["texto"])
                ult = [l.strip() for l in dr["texto"].splitlines() if l.strip()]
                if ult and ult[-1] in ("DECISAO:PROCEDE", "DECISAO:REFUTADO"):
                    des["decisao"] = ult[-1]
                else:
                    dr["exit"] = "68"
            if des["decisao"] == "-":
                avisos.append("⚠️ o desempate (%s) não decidiu: o achado %s fica para uma pessoa (D5)" % (
                    des["engine"], des["alvo"]))

# ── convergência, diversidade, custo ────────────────────────────────────────────────────────────
if aud is None:
    conv = "n/a (auditor não rodou)"
elif aud["exit"] != "0":
    conv = "n/a (auditor falhou)"
elif raso2:
    conv = "n/a (2º revisor raso: 0 achados em %ds)" % r2["segundos"]
elif raso1 and not dois:
    conv = "n/a (revisor1 raso: 0 achados em %ds)" % rev["segundos"]
else:
    novos = [j for j in aud_v if j["veredito"] == "NOVO"]
    conv = "sim" if not novos and all(veredito_de(j["achado"]) == "AGREE" for j in todos_rev) else "nao"
if raso1:
    avisos.append("⚠️ o revisor terminou em %d s sem achados: isso não conta como revisão" % rev["segundos"])

if aud is not None and aud["exit"] == "0" and rev["linha"] and aud["linha"]:
    div = diversidade(rev["linha"], aud["linha"])
else:
    div = "-"
if div == "nenhuma":
    avisos.insert(0, "⚠️ a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos da revisão")


def n(v):
    return str(v) if isinstance(v, int) else "n/d"


papeis_meta = [("reviewer", rev), ("revisor2", r2), ("auditor", aud), ("desempate", des["reg"])]
custos = {}
for nome, r in papeis_meta:
    custos[nome] = custo(r) if r else "n/d"

soma, estimado, desconhecidos = 0.0, False, 0
for nome, r in papeis_meta:
    c = custos[nome]
    if c.startswith("US$ "):
        soma += float(c[4:])
    elif c.startswith("≈US$ "):
        soma += float(c[5:])
        estimado = True
    elif c == "$?":
        desconhecidos += 1
# o total só vira número quando algum papel tem número; senão diz o que se sabe (assinatura) ou $? — nunca 0
numericos = sum(1 for nome, r in papeis_meta if custos[nome].startswith(("US$ ", "≈US$ ")))
if numericos:
    custo_total = ("≈US$ " if estimado else "US$ ") + usd(soma)
elif "assinatura" in custos.values():
    custo_total = "assinatura"
else:
    custo_total = "$?" if desconhecidos else "n/d"
conhecidos = custo_total != "$?"
if desconhecidos and conhecidos:
    custo_total += " (+ %d papel(is) com custo $?)" % desconhecidos

# ── META ─────────────────────────────────────────────────────────────────────────────────────────
M = [("worktree", raiz), ("branch", git(raiz, "rev-parse", "--abbrev-ref", "HEAD")[1].strip()),
     ("protocolo", "cadeia REVISOR → AUDITOR; paralelo não existe"),
     ("base", base), ("merge_base", mb), ("head", head), ("paths", op["--paths"] or "-"),
     ("diff_sha256", sha), ("diff", "%dKB (%d arquivo(s))" % (len(patch) // 1024, len(arqs))),
     ("contexto", "%dKB (%d doc SDD)" % (len(ctx_txt.encode("utf-8")) // 1024, len(docs))),
     ("docs_sdd", ", ".join(nm for nm, _ in docs) or "-"), ("contexto_cortado", cortado),
     ("diversidade", div)]


def bloco_papel(pref, r, extra):
    if r is None:
        return [(pref + "_engine", "-")] if pref == "revisor2" else []
    linhas = [(pref + "_engine_default", r.get("engine_default", "-")),
              (pref + "_engine_efetivo", r.get("engine_efetivo", "-")),
              (pref + "_fallback_usado", r.get("fallback_usado", "nao")),
              (pref + "_motivo", r.get("motivo", "-")), (pref + "_exit", r.get("exit", "-")),
              (pref + "_segundos", str(r.get("segundos", 0)))] + extra
    te, ts = r.get("tokens_entrada"), r.get("tokens_saida")
    tot = te + ts if isinstance(te, int) and isinstance(ts, int) else None
    linhas += [(pref + "_tokens_entrada", n(te)), (pref + "_tokens_saida", n(ts)), (pref + "_tokens_total", n(tot)),
               (pref + "_modelo", r.get("modelo") or ((r.get("linha") or {}).get("modelo")) or "n/d"),
               (pref + "_custo", custos[pref])]
    if pref == "revisor2":
        linhas.insert(0, ("revisor2_engine", r.get("engine_efetivo", "-")))
    return linhas


M += bloco_papel("reviewer", rev, [("reviewer_achados", str(rev.get("achados", 0)))])
M += [("revisor1_raso", "sim" if raso1 else "nao"), ("gatilho_2o_revisor", gatilho)]
M += bloco_papel("revisor2", r2, [("revisor2_achados", str(r2.get("achados", 0)))] if r2 else [])
M += bloco_papel("auditor", aud, [("auditor_vereditos", str(aud.get("vereditos", 0)))]) if aud else \
    [("auditor_exit", "-")]
M += [("convergencia_1o_passe", conv), ("desempate_alvo", des["alvo"]), ("desempate_engine", des["engine"]),
      ("desempate_decisao", des["decisao"])]
if des["reg"]:
    M += [x for x in bloco_papel("desempate", des["reg"], []) if not x[0].startswith("desempate_engine")]
M += [("custo_total", custo_total), ("quando", quando)]
larg = max(len(k) for k, _ in M)
with open(os.path.join(dirrev, "META.txt"), "w", encoding="utf-8") as h:
    for k_, v in M:
        h.write("%s : %s\n" % (k_.ljust(larg), v))
shutil.rmtree(TMP, ignore_errors=True)

# ── resumo ───────────────────────────────────────────────────────────────────────────────────────
ec = rev["exit"] if rev["exit"] != "0" else (aud["exit"] if aud else "0")
for a in avisos:
    print(a)
if ec == "0":
    print("RESULTADO: REVIEW COMPLETA")
elif ec == "68":
    quem = rev if rev["exit"] == "68" else aud
    nomep = "revisor" if quem is rev else "auditor"
    print("RESULTADO: REVIEW INVÁLIDA")
    print("%s (%s): a engine respondeu fora do formato; isto não é zero achados" % (nomep, quem["engine_efetivo"]))
else:
    print("RESULTADO: PAROU")
    quem = rev if rev["exit"] != "0" else aud
    print("%s: %s" % (NOME_PAPEL["reviewer" if quem is rev else "auditor"], quem["motivo"]))


def humano(c):
    if c.startswith("US$ "):
        return "US$ " + c[4:].replace(".", ",")
    if c.startswith("≈US$ "):
        return "≈ US$ " + c[5:].replace(".", ",") + " (estimado)"
    return {"assinatura": "incluído na assinatura", "$?": "custo desconhecido"}.get(c, c)


def contagem(vs):
    def p(k, s, pl):
        return "%d %s" % (k, s if k == 1 else pl)
    h = sum(1 for j in vs if j.get("severidade") == "HIGH")
    m_ = sum(1 for j in vs if j.get("severidade") == "MED")
    l_ = sum(1 for j in vs if j.get("severidade") == "LOW")
    return "%s, %s, %s" % (p(h, "grave", "graves"), p(m_, "médio", "médios"), p(l_, "leve", "leves"))


print("pasta: " + rel_rev)
print("diff_sha256: " + sha)
for nome, r in papeis_meta:
    if r and r.get("engine_efetivo") not in (None, "-"):
        if r.get("exit") not in ("0", None):
            print("%s: falhou (exit %s) — última engine tentada: %s" % (NOME_PAPEL[nome], r["exit"], r["engine_efetivo"]))
            continue
        print("%s: %s (%s)%s — %s" % (NOME_PAPEL[nome], r["engine_efetivo"], r.get("modelo") or
                                       (r.get("linha") or {}).get("modelo") or "n/d",
                                       " (troca de engine)" if r.get("fallback_usado") == "sim" else "",
                                       humano(custos[nome])))
print("diversidade: " + div)
if ec == "0":
    novos = [j for j in aud_v if j["veredito"] == "NOVO"]
    print("achados: " + contagem(todos_rev) + (" (+ %d novo(s) do auditor)" % len(novos) if novos else ""))
print("custo total: " + humano(custo_total.split(" (+")[0]) + (" (+ %d papel(is) com custo desconhecido)" % desconhecidos
                                                              if desconhecidos and conhecidos else ""))
if ec == "0":
    print("→ rode: bash sdd/bin/sdd-fluxo.sh loop --review %s --ledger <ledger da revisão> --rodada <N>" % rel_rev)
elif ec == "65":
    quem = rev if rev["exit"] == "65" else aud
    print("→ confira a credencial de %s (%s); a revisão não troca de engine por falha de credencial" % (
        quem["engine_efetivo"], quem["credencial"]))
elif ec == "66":
    print("→ instale a CLI da engine ou acrescente outra engine à lista (review.revisor1 / review.auditor)")
elif ec == "67":
    quem = rev if rev["exit"] == "67" else aud
    if "excluída" in quem["motivo"] and all("excluída" in x for x in quem["motivo"].split("; ")):
        print("→ escolha outra engine para auditar (review.auditor) ou rode com --um-engine")
    else:
        print("→ acrescente outra engine à lista ou tente mais tarde")
else:
    print("→ rode de novo; se repetir, troque a engine do %s" % ("revisor" if rev["exit"] == "68" else "auditor"))
sys.exit(int(ec))
PY
