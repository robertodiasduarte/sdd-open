#!/usr/bin/env bash
# sdd-fluxo.sh — decisores mecânicos do fluxo encadeado do SDD Open. Contrato de uso em
# sdd/templates/fragments/FLUXO_ENCADEADO.md.
#
# Por que existe: "este DESIGN precisa de revisão?", "o loop de review convergiu?" e "a fase seguinte
# pode começar sem perguntar?" eram decididos por leitura de prosa. Aqui viram exit code.
#
# USO-INICIO
#   sdd-fluxo.sh review-design <DESIGN.md>
#       0 EXIGIDO (≥ 3 arquivos novos no File Manifest, ou superfície de segurança: termo fixo,
#         glob de review.security_globs ou de layers.sql) · 1 DISPENSAVEL · 64 manifest ilegível
#         (quem chama RODA a revisão — default seguro — e registra o motivo)
#   sdd-fluxo.sh loop --review <dir> --ledger <arquivo> --rodada N[a] [--teto 3]
#                     [--avaliacao <AVALIACAO.md> --ciclo-avaliador K] [--recibo "nome AAAA-MM-DD"]
#                     [--log <arquivo>]
#       0 PRONTO · 10 CONTINUAR · 20 BLOQUEADO (D4 teto, D4 ciclos, D5 impasse de evidência)
#       30 AGUARDANDO_RECIBO · 64 entrada ausente ou ilegível — nunca PRONTO por omissão
#   sdd-fluxo.sh despachar <papel> <FEATURE> <brief.md>
#       40 AGUARDANDO_HUMANO: brief em sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md e a parada ⏸️ · 64
#   sdd-fluxo.sh seguir <fase> <DEFINE.md> <próxima> [--parar]
#       0 SEGUIR (linha de transição) · 1 PARAR (o motivo) · 64 uso ou flow.autonomous inválido
#   sdd-fluxo.sh estado
#       0 encadeamento ligado · 1 desligado · 64 flow.autonomous inválido
#   sdd-fluxo.sh --self-test
#       um cenário por exit sobre sdd/fixtures/fluxo/ e o do `| tee`; 0 quando todos batem
# USO-FIM
#
# Ledger do loop: 1 linha por achado, lida por CÉLULA — `| R1 | HIGH | APLICADA | rodada=2 | arquivo:linha |`.
# Toda saída que não é sucesso termina em `RESULTADO: <PALAVRA>` + `→ <o que fazer>`.
# ⚠️ bash 3.2 (o /bin/bash do macOS: nada além do que ele tem) · o núcleo de dados é Python 3.9 stdlib.

set -u

BIN="$(cd "$(dirname "$0")" && pwd)"
export SDD_FLUXO_BIN="$BIN"

uso() {
  [ -n "${1:-}" ] && echo "🛑 sdd-fluxo: ${1}" >&2
  sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//' >&2
  printf 'RESULTADO: ERRO DE USO\n→ rode com um dos verbos acima.\n' >&2
  exit 64
}

precisa_python() { # [$@ do loop]: com --log, o log também diz o 64 (nunca fica um log antigo no lugar)
  command -v python3 >/dev/null 2>&1 && return 0
  msg='🛑 sdd-fluxo: python3 não encontrado no PATH.'
  seta='→ instale o Python 3 (3.9 ou mais novo) e rode de novo.'
  echo "$msg" >&2
  printf 'RESULTADO: ERRO DE USO\n%s\n' "$seta" >&2
  log=""; tudo="$*"
  while [ $# -gt 0 ]; do [ "$1" = "--log" ] && [ $# -ge 2 ] && log="$2"; shift; done
  if [ -n "$log" ]; then
    mkdir -p "$(dirname "$log")" 2>/dev/null
    printf '$ sdd-fluxo.sh loop %s\n%s\nRESULTADO: ERRO DE USO\n%s\n[exit=64]\n' "$tudo" "$msg" "$seta" > "$log" 2>/dev/null
  fi
  exit 64
}

raiz() { git rev-parse --show-toplevel 2>/dev/null || pwd; }

# Lista explícita, sem faixa: no bash 3.2 com locale UTF-8, [A-Za-z] segue a ordenação do locale e aceita
# letra acentuada (avaliação, INTEGRAÇÃO).
LETRAS='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'
nome_ok() { case "$1" in ''|*[!"$LETRAS"]*) return 1 ;; esac; return 0; }

# ── despachar (bash puro) ────────────────────────────────────────────────────────────────────────
cmd_despachar() {
  [ $# -eq 3 ] || uso "despachar exige <papel> <FEATURE> <brief>"
  papel="$1"; feat="$2"; brief="$3"
  nome_ok "$papel" || uso "papel inválido: '$papel' (letras, números, - e _)"
  nome_ok "$feat" || uso "FEATURE inválida: '$feat' (letras, números, - e _)"
  if [ ! -r "$brief" ] || [ ! -s "$brief" ] || [ -d "$brief" ]; then
    echo "🛑 sdd-fluxo: brief ausente, vazio ou ilegível: $brief" >&2
    printf 'RESULTADO: ERRO DE USO\n→ grave o brief num arquivo e rode de novo; nada foi gravado em sdd/reports/briefs/.\n' >&2
    exit 64
  fi
  R="$(raiz)"
  rel="sdd/reports/briefs/BRIEF_${papel}_${feat}.md"
  mkdir -p "$R/sdd/reports/briefs" || exit 64
  if [ ! "$brief" -ef "$R/$rel" ]; then
    cp "$brief" "$R/$rel" || exit 64
  fi
  cmp -s "$brief" "$R/$rel" || { echo "🛑 sdd-fluxo: a cópia do brief não confere: $rel" >&2; exit 64; }
  if [ "$papel" = "avaliador" ]; then
    retorno='o bloco inteiro da resposta, de `<<<AVALIACAO` até `>>>` (com a linha `VEREDITO: …`)'
  else
    retorno='o bloco final da resposta (o que começa com <<<)'
  fi
  printf '⏸️ sdd-open: esta etapa precisa de uma sessão nova do agente (papel: %s).\n\n' "$papel"
  printf '**Por que parei:** a conferência precisa de alguém que não viu esta conversa, e este agente não abre essa sessão sozinho.\n'
  printf '**Onde:** numa janela nova do seu agente, na pasta %s.\n' "$R"
  printf '**Passos:**\n'
  printf '1. Abra uma sessão nova do agente nesta pasta → você vê o agente pronto, sem histórico.\n'
  printf '2. Cole o conteúdo de %s → o agente começa a ler o DEFINE.\n' "$rel"
  printf '3. Quando ele terminar, copie %s e cole aqui → é o que eu preciso para continuar.\n' "$retorno"
  printf '**O que não foi feito:** nada foi publicado e o relatório não foi gravado.\n'
  printf '**Brief:** %s\n' "$rel"
  printf '**Sessão nova:** abra o agente nesta pasta e cole o conteúdo do brief.\n\n'
  printf 'Quando terminar, me peça de novo, eu continuo daqui.\n'
  printf 'RESULTADO: AGUARDANDO_HUMANO\n→ quando a pessoa colar o retorno, continue do passo que parou.\n'
  exit 40
}

# ── núcleo de dados (Python 3.9 stdlib): review-design, loop, seguir, estado ─────────────────────
nucleo() {
  python3 -B - "$@" <<'PY'
import fnmatch, os, re, shlex, subprocess, sys

BIN = os.environ["SDD_FLUXO_BIN"]
verbo, args = sys.argv[1], sys.argv[2:]


def ler(caminho):
    try:
        with open(caminho, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def raiz_de(pasta):
    try:
        r = subprocess.run(["git", "-C", pasta, "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except OSError:
        pass
    return os.getcwd()


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


def erro_uso(msg, seta="rode `sdd-fluxo.sh` sem argumentos para ver o uso."):
    print("🛑 sdd-fluxo: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ " + seta, file=sys.stderr)
    sys.exit(64)


# ── estado ───────────────────────────────────────────────────────────────────────────────────────
def estado(raiz):
    """(rc, linha): 0 ligado · 1 desligado · 64 valor inválido."""
    v = slot(os.path.join(raiz, "sdd/config.yaml"), "flow", "autonomous")
    if v == "true":
        return 0, "encadeamento: ligado"
    if v in (None, "", "false"):
        return 1, "encadeamento: desligado"
    return 64, ('⚠️ sdd-open: flow.autonomous = "%s" em sdd/config.yaml não é true nem false — '
                "encadeamento desligado.\n→ troque por true (liga) ou false (desliga)" % v)


def cmd_estado():
    if args:
        erro_uso("estado não recebe argumentos")
    rc, linha = estado(raiz_de(os.getcwd()))
    print(linha)
    if rc == 64:
        print("RESULTADO: SLOT INVÁLIDO")
    sys.exit(rc)


# ── review-design ────────────────────────────────────────────────────────────────────────────────
TERMOS = re.compile(r"\bauth|\blogin\b|\btokens?\b|\bsenhas?\b|password|\bjwt\b|\bGRANT\b|rota p(?:ú|u)blica",
                    re.I)


def review_design(design):
    """(rc, linhas): 0 EXIGIDO · 1 DISPENSAVEL · 64 manifest ilegível."""
    texto = ler(design)

    def ilegivel(msg):
        return 64, ["🛑 sdd-fluxo: " + msg, "RESULTADO: MANIFEST ILEGÍVEL",
                    "→ rode a revisão do DESIGN mesmo assim (default seguro) e registre o motivo no Advisor Ledger."]

    if texto is None:
        return ilegivel("DESIGN ausente ou ilegível: " + design)
    # um File Manifest de exemplo dentro de bloco cercado não é o manifest do DESIGN
    texto = re.sub(r"^(```|~~~).*?^\1[^\n]*$", lambda c: "\n" * c.group(0).count("\n"), texto, flags=re.M | re.S)
    m = re.search(r"^##[ \t]+(?:\d+(?:\.\d+)*\.?[ \t]+)?File Manifest\b[^\n]*\n(.*?)(?=^## |\Z)",
                  texto, re.M | re.S | re.I)
    if not m:
        return ilegivel("DESIGN sem ## File Manifest: " + design)
    linhas = [ln for ln in m.group(1).split("\n") if re.match(r"^\|\s*\d+\s*\|", ln)]
    if not linhas:
        return ilegivel("## File Manifest sem linhas numeradas (| 1 | arquivo | Ação | …): " + design)

    def acao(ln):
        cel = ln.split("|")
        a = re.sub(r"[*`_]", "", cel[3] if len(cel) > 3 else "").lower()
        return re.match(r"^\s*(?:create|criar|novo|nova|new)\b", a) is not None

    novos = sum(1 for ln in linhas if acao(ln))
    raiz = raiz_de(os.path.dirname(os.path.abspath(design)))
    cfg = os.path.join(raiz, "sdd/config.yaml")
    globs = [g.strip() for g in (slot(cfg, "review", "security_globs") or "").split(",") if g.strip()]
    sql = (slot(cfg, "layers", "sql") or "").strip()
    if sql:
        globs.append(sql)

    seg, porque = 0, []
    for ln in linhas:
        cel = ln.split("|")
        caminhos = re.findall(r"`([^`]+)`", cel[2] if len(cel) > 2 else "")
        t = TERMOS.search(ln)
        g = next((g for g in globs for c in caminhos if fnmatch.fnmatch(c, g)), None)
        if t or g:
            seg += 1
            p = "termo " + t.group(0) if t else "glob " + g
            if p not in porque:
                porque.append(p)
    sinais = []
    if novos >= 3:
        sinais.append("%d arquivo(s) novo(s) (limiar 3)" % novos)
    if seg:
        sinais.append("%d linha(s) do manifest em superfície de segurança (%s)" % (seg, ", ".join(porque[:5])))
    if sinais:
        return 0, ["EXIGIDO: " + " · ".join(sinais)]
    return 1, ["DISPENSAVEL: %d arquivo(s) novo(s), sem superfície de segurança no manifest" % novos]


def cmd_review_design():
    if len(args) != 1:
        erro_uso("review-design exige <DESIGN.md>")
    rc, linhas = review_design(args[0])
    print("\n".join(linhas))
    sys.exit(rc)


# ── loop ─────────────────────────────────────────────────────────────────────────────────────────
import json


class _Tee:
    def __init__(self, real, buf):
        self.real, self.buf = real, buf

    def write(self, s):
        self.buf.append(s)
        return self.real.write(s)

    def flush(self):
        self.real.flush()


def cmd_loop():
    """Com --log, grava `$ comando`, toda a saída e `[exit=N]` em TODA saída, inclusive 64: um log antigo
    nunca fica no lugar com um exit que esta chamada não deu."""
    log = None
    if "--log" in args:
        k = args.index("--log")
        log = args[k + 1] if k + 1 < len(args) and not args[k + 1].startswith("--") else None
    if not log:
        _loop()
        return
    resto, j = [], 0
    while j < len(args):
        if args[j] == "--log":
            j += 2
            continue
        resto.append(args[j])
        j += 1
    buf, so, se = [], sys.stdout, sys.stderr
    sys.stdout, sys.stderr = _Tee(so, buf), _Tee(se, buf)
    rc = 0
    try:
        _loop()
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else (0 if e.code is None else 64)
    except Exception as e:  # erro interno também é 64, com o log regravado
        print("🛑 sdd-fluxo: erro interno no loop: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        print("RESULTADO: ENTRADA ILEGÍVEL\n→ confira os argumentos e as entradas; nada foi decidido.", file=sys.stderr)
        rc = 64
    finally:
        sys.stdout, sys.stderr = so, se
    try:
        pasta = os.path.dirname(log)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        with open(log, "w", encoding="utf-8") as h:
            h.write("$ sdd-fluxo.sh loop " + " ".join(shlex.quote(x) for x in resto) + "\n")
            h.write("".join(buf))
            h.write("[exit=%d]\n" % rc)
    except OSError as e:
        print("🛑 sdd-fluxo: não consegui gravar o --log: %s" % e, file=sys.stderr)
        print("RESULTADO: ERRO DE USO\n→ passe em --log um arquivo que dá para gravar; sem o log, a decisão não vale.",
              file=sys.stderr)
        rc = 64
    sys.exit(rc)


def recibo_valido(recibo):
    """`nome AAAA-MM-DD`: um nome e uma data que existe no calendário."""
    import datetime
    m = re.match(r"^(.*\S)\s+(\d{4}-\d{2}-\d{2})$", recibo.strip())
    if not m or not re.search(r"[^\d\s-]", m.group(1)):
        return False
    try:
        datetime.date(*(int(x) for x in m.group(2).split("-")))
    except ValueError:
        return False
    return True


def _loop():
    op = {"--review": "", "--ledger": "", "--rodada": "", "--teto": "3", "--avaliacao": "",
          "--ciclo-avaliador": "0", "--recibo": "", "--log": ""}
    i = 0
    while i < len(args):
        a = args[i]
        if a not in op:
            erro_uso("argumento inesperado: " + a)
        if i + 1 >= len(args):
            erro_uso(a + " exige um valor")
        op[a] = args[i + 1]
        i += 2
    review, ledger, rodada = op["--review"], op["--ledger"], op["--rodada"]
    teto, aval, ciclo, recibo = op["--teto"], op["--avaliacao"], op["--ciclo-avaliador"], op["--recibo"]
    if not review or not rodada:
        erro_uso("loop exige --review <dir> e --rodada N")
    if not re.match(r"^[0-9]+[a-z]?$", rodada) or not re.match(r"^[0-9]+$", teto) or not re.match(r"^[0-9]+$", ciclo):
        erro_uso("--rodada é inteiro com sufixo de lote opcional (5 ou 5a); --teto/--ciclo-avaliador são inteiros")
    teto, ciclo = int(teto), int(ciclo)

    def sai64(msg):
        print("🛑 sdd-fluxo: " + msg, file=sys.stderr)
        print("RESULTADO: ENTRADA ILEGÍVEL\n→ sem essa entrada não há como declarar PRONTO; refaça a revisão "
              "ou conserte o arquivo.", file=sys.stderr)
        sys.exit(64)

    meta_txt = ler(os.path.join(review, "META.txt"))
    if meta_txt is None:
        sai64(os.path.join(review, "META.txt") + " ausente — sem review não há como declarar PRONTO")
    led_txt = ""
    if ledger:
        led_txt = ler(ledger)
        if led_txt is None:
            sai64("ledger ilegível: " + ledger)
    aval_txt = None
    if aval:
        aval_txt = ler(aval)
        if aval_txt is None:
            sai64("avaliação ilegível: " + aval)

    def jsonl(caminho, tipo):
        t = ler(caminho)
        if t is None:
            sai64(caminho + " ausente — sem vereditos legíveis não há como declarar PRONTO")
        saida = []
        for n, ln in enumerate(t.split("\n"), 1):
            if not ln.strip():
                continue
            try:
                j = json.loads(ln)
            except ValueError:
                j = None
            ok = isinstance(j, dict) and isinstance(j.get("achado"), str) and j["achado"] != ""
            if ok and tipo == "revisor":
                ok = j.get("severidade") in ("HIGH", "MED", "LOW")
            if ok and tipo == "auditor":
                ok = j.get("veredito") in ("AGREE", "DISAGREE_EVIDENCE", "DISAGREE_CONCERN", "NOVO")
                if ok and j.get("veredito") == "NOVO":
                    ok = j.get("severidade") in ("HIGH", "MED", "LOW")
            if not ok:
                sai64("%s:%d linha inválida para %s — %s" % (caminho, n, tipo, ln))
            saida.append(j)
        return saida

    meta = {}
    for ln in meta_txt.split("\n"):
        m = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if m:
            meta[m.group(1)] = m.group(2)
    motivos, continuar_review, continuar_aval, aguarda_recibo = [], False, False, False

    # 1. review inválida (papel falhou) — refazer, conta como rodada
    rev_ec, aud_ec = meta.get("reviewer_exit", ""), meta.get("auditor_exit", "")
    if rev_ec != "0" or aud_ec != "0":
        motivos.append("review inválida (reviewer_exit=%s auditor_exit=%s) — refazer" % (rev_ec, aud_ec))
        continuar_review = True

    # 2. graves: HIGH do revisor (última linha por id) + NOVO HIGH do auditor (depois do dedup)
    grave, aud, todos = {}, {}, {}
    if not continuar_review:
        ult, ordem = {}, []
        for v in jsonl(os.path.join(review, "reviewer.verdicts.jsonl"), "revisor"):
            if v["achado"] not in ult:
                ordem.append(v["achado"])
            ult[v["achado"]] = v
        for id_ in ordem:
            todos[id_] = ult[id_]["severidade"]
            if ult[id_]["severidade"] == "HIGH":
                grave[id_] = True
        aud_sev = {}
        for v in jsonl(os.path.join(review, "auditor.verdicts.jsonl"), "auditor"):
            aud[v["achado"]] = v.get("veredito", "")
            aud_sev[v["achado"]] = v.get("severidade", "")
        for id_ in aud:
            if aud[id_] == "NOVO":
                todos.setdefault(id_, aud_sev[id_])
                if aud_sev[id_] == "HIGH":
                    grave[id_] = True

    def base_unica(id_):
        b = id_.split("@", 1)[0]
        if b == id_:
            return None
        return b if sum(1 for x in todos if x.split("@", 1)[0] == b) == 1 else None

    def veredito_aud(id_):
        if id_ in aud:
            return aud[id_]
        b = base_unica(id_)
        return aud.get(b) if b is not None else None

    # 3. ledger da RODADA, por célula: | achado | SEV | VEREDITO | rodada=N | evidência |
    led = {}
    for ln in led_txt.split("\n"):
        if not re.match(r"^\s*\|", ln):
            continue
        c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)][1:]
        if len(c) < 4 or c[3] != "rodada=" + rodada:
            continue
        if c[2] not in ("APLICADA", "REBATIDA_EVIDENCIA", "REBATIDA_ESCOPO") or c[1] != "HIGH":
            continue
        for id_ in grave:
            b = base_unica(id_)
            if c[0] == id_ or (b is not None and c[0] == b):
                led[id_] = c[2]

    # refutação do auditor sem veredito no ledger da rodada = impasse de evidência (D5)
    impasse = []
    for id_ in sorted(grave):
        if veredito_aud(id_) == "DISAGREE_EVIDENCE" and id_ not in led:
            impasse.append(id_)
    for id_ in impasse:
        del grave[id_]
    abertos, aplicadas, rebatidas = [], [], []
    for id_ in sorted(grave):
        s = led.get(id_, "")
        (aplicadas if s == "APLICADA" else rebatidas if s.startswith("REBATIDA_") else abertos).append(id_)
    if abertos:
        continuar_review = True
        motivos.append("grave(s) sem veredito no ledger: " + " ".join(abertos))
    if aplicadas:
        continuar_review = True
        motivos.append("grave(s) corrigido(s) — código mudou, exige nova review: " + " ".join(aplicadas))
    if rebatidas:
        motivos.append("grave(s) rebatido(s) no ledger: " + " ".join(rebatidas))

    # 4. avaliador: só a linha inteira `VEREDITO: X`; 0 ou 2 valores distintos = ambíguo
    if aval_txt is not None:
        vals = set(re.findall(r"^\s*VEREDITO:\s*(PASS_PENDENTE_RECIBO|NEEDS_WORK|PASS)\s*$", aval_txt, re.M))
        if len(vals) != 1:
            sai64("avaliação ilegível ou ambígua em %s (esperado 1 linha VEREDITO: X)" % aval)
        vered = vals.pop()
        if vered == "NEEDS_WORK":
            continuar_aval = True
            motivos.append("avaliador: NEEDS_WORK (ciclo %d)" % ciclo)
        elif vered == "PASS_PENDENTE_RECIBO":
            if recibo_valido(recibo):
                motivos.append("avaliador: recibo humano — " + recibo)
            else:
                aguarda_recibo = True
                motivos.append("avaliador: PASS_PENDENTE_RECIBO — aguardando o recibo humano do roteiro (não é decisão)")

    est, rc = "PRONTO", 0
    if aguarda_recibo:
        est, rc = "AGUARDANDO_RECIBO", 30
    if impasse:
        motivos.append("D5 impasse de evidência: grave(s) refutado(s) pelo auditor sem veredito no ledger: "
                       + " ".join(impasse))
    if continuar_review or continuar_aval:
        est, rc = "CONTINUAR", 10
    rodada_n = int(re.sub(r"[a-z]$", "", rodada))
    if continuar_review and rodada_n >= teto:
        est, rc = "BLOQUEADO", 20
        motivos.append("D4 teto: %d rodadas de review atingido" % teto)
    if continuar_aval and ciclo >= 2:
        est, rc = "BLOQUEADO", 20
        motivos.append("D4 ciclos: 2 ciclos NEEDS_WORK do avaliador")
    if impasse:
        est, rc = "BLOQUEADO", 20
    seta = {
        "PRONTO": "siga para o avaliador ou para a release.",
        "CONTINUAR": "corrija, rode o Verify Gate e a revisão de novo com --rodada %d." % (rodada_n + 1),
        "BLOQUEADO": "pare e faça a pergunta D4 ou D5 de sdd/templates/fragments/FLUXO_ENCADEADO.md.",
        "AGUARDANDO_RECIBO": "percorra o roteiro do avaliador e rode de novo com --recibo \"nome AAAA-MM-DD\".",
    }[est]
    saida = ["ESTADO: " + est, "rodada: %s de %d" % (rodada, teto), "graves_abertos: %d" % len(abertos),
             "aplicadas: %d" % len(aplicadas), "rebatidas: %d" % len(rebatidas)]
    saida += ["motivo: " + m for m in motivos]
    saida += ["RESULTADO: " + est, "→ " + seta]
    texto = "\n".join(saida) + "\n"
    sys.stdout.write(texto)
    sys.exit(rc)


# ── seguir ───────────────────────────────────────────────────────────────────────────────────────
DOC = {"define": ("DEFINE", "o", "pronto"), "governanca": ("GOVERNANÇA", "a", "pronta"),
       "ux-review": ("UX REVIEW", "a", "pronta"), "design": ("DESIGN", "o", "pronto"),
       "build": ("BUILD", "o", "pronto"), "release": ("RELEASE", "a", "pronta")}
PARES = {"define": ("governanca", "ux-review", "design"), "governanca": ("ux-review", "design"),
         "ux-review": ("design",), "design": ("build",), "build": ()}


def status_de(caminho):
    """Valor de `| **Status** | … |` do Metadata; "" sem a linha; None se o arquivo não existe."""
    t = ler(caminho)
    if t is None:
        return None
    m = re.search(r"^\|\s*\*{0,2}Status\*{0,2}\s*\|\s*([^|\n]*?)\s*\|", t, re.M)
    return m.group(1).strip() if m else ""


def ledger(texto):
    """[(nº, severidade, veredito)] das linhas de dados da tabela de `## Advisor Ledger`."""
    texto = re.sub(r"^(```|~~~).*?^\1[^\n]*$", lambda c: "\n" * c.group(0).count("\n"), texto or "", flags=re.M | re.S)
    m = re.search(r"^## Advisor Ledger[^\n]*\n(.*?)(?=^## |\Z)", texto, re.M | re.S)
    if not m:
        return []
    cab, saida = None, []
    for ln in m.group(1).split("\n"):
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if cab is None:
            cab = [x.lower() for x in c]
            continue
        if all(re.match(r"^:?-+:?$", x) for x in c if x):
            continue
        if not any(c):
            continue
        sev = next((c[k] for k, h in enumerate(cab) if h.startswith(("sev", "severidade", "severity")) and k < len(c)), None)
        ver = next((c[k] for k, h in enumerate(cab) if h.startswith(("veredito", "verdict")) and k < len(c)), "")
        saida.append((c[0], sev, ver))
    return saida


def cmd_seguir():
    parar = "--parar" in args
    pos = [a for a in args if a != "--parar"]
    if len(pos) != 3 or any(a.startswith("--") for a in pos):
        erro_uso("seguir exige <fase> <DEFINE.md> <próxima> [--parar]",
                 "trate o encadeamento como desligado e mostre o Próximo passo.")
    fase, define, prox = pos
    if fase not in PARES or (prox != "release" and prox not in PARES[fase]):
        erro_uso("par de fases inválido: %s → %s (válidos: define→governanca|ux-review|design, "
                 "governanca→ux-review|design, ux-review→design, design→build, qualquer→release)" % (fase, prox),
                 "trate o encadeamento como desligado e mostre o Próximo passo.")
    if ler(define) is None:
        erro_uso("DEFINE ausente ou ilegível: " + define,
                 "trate o encadeamento como desligado e mostre o Próximo passo.")
    raiz = raiz_de(os.path.dirname(os.path.abspath(define)))
    feat = re.sub(r"^DEFINE_|\.md$", "", os.path.basename(define))
    alvo = define
    if prox == "build":
        alvo = os.path.join(os.path.dirname(define), "DESIGN_%s.md" % feat)

    def para(motivo):
        print("PARAR: " + motivo)
        print("RESULTADO: PARAR")
        print("→ Próximo passo: /sdd-%s %s" % (prox, alvo))
        sys.exit(1)

    rc, linha = estado(raiz)
    if rc == 64:
        print(linha)
        print("RESULTADO: SLOT INVÁLIDO")
        sys.exit(64)
    if parar:
        para("pedido de parar nesta chamada (--parar)")
    if rc == 1:
        para("encadeamento desligado")
    if prox == "release":
        para("publicar não se desfaz — é decisão sua (D1)")
    design = os.path.join(os.path.dirname(define), "DESIGN_%s.md" % feat)
    artefato = {"define": define, "governanca": define, "design": design,
                "ux-review": os.path.join(raiz, "sdd/reviews/UX_REVIEW_%s.md" % feat)}[fase]
    st = status_de(artefato)
    fem = DOC[fase][1] == "a"
    if st is None:
        para("%s não %s: %s" % (DOC[fase][0], "encontrada" if fem else "encontrado", artefato))
    if not st.startswith("Ready for"):
        para("%s não está %s (Status: %s)" % (DOC[fase][0], DOC[fase][2], st or "ausente"))
    git = subprocess.run(["git", "-C", raiz, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if git.returncode != 0:
        para("a pasta não é um repositório git, e o verify-gate.sh precisa de um (rode git init)")
    r = subprocess.run(["bash", os.path.join(BIN, "verify-gate.sh"), "--print", os.path.abspath(define)],
                       cwd=raiz, capture_output=True, text=True)
    if r.returncode != 0:
        para("o Verify Gate do DEFINE não está válido (verify-gate.sh --print saiu %d)" % r.returncode)
    vazios = [c for c in ("kind", "cmd") if re.search(r"^" + c + r":\s*(<vazio>)?\s*$", r.stdout, re.M)]
    if vazios:
        para("Verify Gate sem kind ou cmd")
    dentro = False
    for ln in ler(define).splitlines():
        if re.match(r"^\s*```", ln):
            dentro = not dentro
            continue
        if not dentro and "[NEEDS CLARIFICATION:" in ln:
            para("o DEFINE tem marcador de clarificação aberto")
    if fase == "design":
        r = subprocess.run([sys.executable, "-B", os.path.join(BIN, "design-lint.py"), design],
                           capture_output=True, text=True)
        if r.returncode != 0:
            para("o DESIGN não passa no design-lint (saiu %d)" % r.returncode)
        if review_design(design)[0] in (0, 64):
            linhas = ledger(ler(design))
            if not linhas:
                para("revisão do DESIGN exigida e não registrada no Advisor Ledger")
            if any(sev is None for _, sev, _ in linhas):
                para("Advisor Ledger sem coluna de severidade (Severidade ou Severity): não dá para conferir HIGH aberto")
            abertos = [n for n, sev, ver in linhas if re.search(r"\bHIGH\b", re.sub(r"[*`_]", "", sev or "").upper())
                       and not re.match(r"^\W*(APLICADA|REBATIDA_|APPLIED|REBUTTED)", ver, re.I)]
            if abertos:
                para("HIGH aberto no Advisor Ledger: " + ", ".join(abertos))
    de, para_doc = DOC[fase], DOC[prox]
    print("✅ %s %s → seguindo para %s %s (encadeamento ligado em sdd/config.yaml)"
          % (de[0], de[2], para_doc[1], para_doc[0]))
    print("→ /sdd-%s %s" % (prox, alvo))
    sys.exit(0)


{"review-design": cmd_review_design, "loop": cmd_loop, "seguir": cmd_seguir, "estado": cmd_estado}[verbo]()
PY
}

# ── --self-test ──────────────────────────────────────────────────────────────────────────────────
FALHAS=0
cenario() { # cenario <nome> <exit esperado> <texto esperado> -- comando…
  nome="$1"; want="$2"; texto="$3"; shift 4
  out="$("$@" 2>&1)"; got=$?
  if [ "$got" = "$want" ] && printf '%s' "$out" | grep -qF -- "$texto"; then
    echo "  ✅ ${nome} → exit ${got}"
  else
    echo "  🛑 ${nome} → exit ${got} (esperado ${want}, com: ${texto})"
    printf '%s\n' "$out" | sed 's/^/      /'
    FALHAS=$((FALHAS + 1))
  fi
}

cmd_self_test() {
  FX="$BIN/../fixtures/fluxo"
  DF="$BIN/../fixtures"
  [ -d "$FX" ] || { echo "🛑 sdd-fluxo: fixtures ausentes: $FX" >&2; exit 64; }
  T="$(mktemp -d 2>/dev/null || mktemp -d -t sddfluxo)" || exit 64
  trap 'rm -rf "${T:?}"' EXIT
  S="$BIN/sdd-fluxo.sh"
  echo "sdd-fluxo --self-test"
  cenario "review-design EXIGIDO (3 novos)" 0 "EXIGIDO: 3 arquivo(s) novo(s)" -- bash "$S" review-design "$FX/DESIGN_novos.md"
  cenario "review-design EXIGIDO (segurança)" 0 "superfície de segurança" -- bash "$S" review-design "$FX/DESIGN_seguranca.md"
  cenario "review-design DISPENSAVEL" 1 "DISPENSAVEL: 2 arquivo(s) novo(s)" -- bash "$S" review-design "$FX/DESIGN_dispensavel.md"
  cenario "review-design manifest ilegível" 64 "RESULTADO: MANIFEST ILEGÍVEL" -- bash "$S" review-design "$FX/DESIGN_sem_manifest.md"
  cenario "loop PRONTO" 0 "ESTADO: PRONTO" -- bash "$S" loop --review "$FX/review-ok" --ledger "$FX/ledger-rebatida.md" --rodada 1 --avaliacao "$FX/AVALIACAO_pass.md" --ciclo-avaliador 1
  cenario "loop CONTINUAR (aplicada)" 10 "exige nova review" -- bash "$S" loop --review "$FX/review-ok" --ledger "$FX/ledger-aplicada.md" --rodada 1
  cenario "loop CONTINUAR (review inválida)" 10 "review inválida" -- bash "$S" loop --review "$FX/review-invalida" --rodada 1
  cenario "loop BLOQUEADO (D4 teto)" 20 "D4 teto" -- bash "$S" loop --review "$FX/review-ok" --rodada 3
  cenario "loop BLOQUEADO (D5 impasse)" 20 "D5 impasse" -- bash "$S" loop --review "$FX/review-impasse" --rodada 1
  cenario "loop AGUARDANDO_RECIBO" 30 "ESTADO: AGUARDANDO_RECIBO" -- bash "$S" loop --review "$FX/review-ok" --ledger "$FX/ledger-rebatida.md" --rodada 1 --avaliacao "$FX/AVALIACAO_recibo.md"
  cenario "loop avaliação ambígua" 64 "ambígua" -- bash "$S" loop --review "$FX/review-ok" --ledger "$FX/ledger-rebatida.md" --rodada 1 --avaliacao "$FX/AVALIACAO_ambigua.md"
  cenario "loop sem META" 64 "META.txt ausente" -- bash "$S" loop --review "$T" --rodada 1

  # `| tee` perde o exit: o pipeline sai 0 com o loop BLOQUEADO (20), e o log gravado assim é acusado
  mkdir -p "$T/ev-tee" "$T/ev-log"
  out="$(bash "$S" loop --review "$FX/review-impasse" --rodada 1 | tee "$T/tee.out")"; rc_pipe=$?
  printf '%s\n' "\$ bash sdd/bin/sdd-fluxo.sh loop --review review-impasse --rodada 1 | tee loop.out" "$out" "[exit=$rc_pipe]" > "$T/ev-tee/LOOP-rodada-1.log"
  cenario "| tee: exit do pipeline (0) ≠ exit do loop (20)" 0 "ESTADO: BLOQUEADO" -- grep -F "ESTADO: BLOQUEADO" "$T/tee.out"
  [ "$rc_pipe" = "0" ] || { echo "  🛑 | tee devolveu $rc_pipe, esperado 0"; FALHAS=$((FALHAS + 1)); }
  cenario "| tee: log acusado pelo gate-shell-evidencia" 2 "tee" -- bash "$BIN/gate-shell-evidencia.sh" "$T/ev-tee"
  bash "$S" loop --review "$FX/review-impasse" --rodada 1 --log "$T/ev-log/LOOP-rodada-1.log" >/dev/null 2>&1
  cenario "--log: exit real gravado" 0 "[exit=20]" -- grep -F "[exit=20]" "$T/ev-log/LOOP-rodada-1.log"
  cenario "--log: aceito pelo gate-shell-evidencia" 0 "" -- bash "$BIN/gate-shell-evidencia.sh" "$T/ev-log"

  # despachar e seguir/estado num repositório temporário (o verify-gate --print precisa de git)
  R="$T/repo"; mkdir -p "$R/sdd/features" && (cd "$R" && git init -q) || exit 64
  cp "$FX/DEFINE_pronto.md" "$R/sdd/features/DEFINE_X.md"
  cp "$FX/DEFINE_rascunho.md" "$R/sdd/features/DEFINE_R.md"
  cp "$FX/DEFINE_sem_kind.md" "$R/sdd/features/DEFINE_K.md"
  cp "$FX/DEFINE_pronto.md" "$R/sdd/features/DEFINE_M.md"
  printf '\n## Clarifications\n\n- %s o mês fecha no dia 1 ou no último dia útil?]\n' '[NEEDS CLARIFICATION:' >> "$R/sdd/features/DEFINE_M.md"
  cp "$FX/DESIGN_pronto.md" "$R/sdd/features/DESIGN_X.md"
  cp "$FX/DEFINE_pronto.md" "$R/sdd/features/DEFINE_V.md"
  cp "$FX/DESIGN_ledger_vazio.md" "$R/sdd/features/DESIGN_V.md"
  c() { sh -c 'cd "$1" && shift && bash "$@"' _ "$R" "$S" "$@"; }
  cenario "despachar AGUARDANDO_HUMANO" 40 "RESULTADO: AGUARDANDO_HUMANO" -- c despachar avaliador X "$FX/brief-avaliador.md"
  if cmp -s "$FX/brief-avaliador.md" "$R/sdd/reports/briefs/BRIEF_avaliador_X.md"; then echo "  ✅ despachar: brief gravado idêntico"
  else echo "  🛑 despachar: brief não gravado ou diferente"; FALHAS=$((FALHAS + 1)); fi
  cenario "despachar com o brief já no destino" 40 "AGUARDANDO_HUMANO" -- c despachar avaliador X sdd/reports/briefs/BRIEF_avaliador_X.md
  cenario "despachar sem brief" 64 "brief ausente" -- c despachar avaliador X nao-existe.md
  cenario "estado desligado (sem config)" 1 "encadeamento: desligado" -- c estado
  cenario "seguir PARAR (desligado)" 1 "PARAR: encadeamento desligado" -- c seguir define sdd/features/DEFINE_X.md design
  cp "$FX/config-autonomo.yaml" "$R/sdd/config.yaml"
  cenario "estado ligado" 0 "encadeamento: ligado" -- c estado
  cenario "seguir SEGUIR (define)" 0 "✅ DEFINE pronto → seguindo para o DESIGN" -- c seguir define sdd/features/DEFINE_X.md design
  cenario "seguir SEGUIR (design, revisão registrada)" 0 "✅ DESIGN pronto → seguindo para o BUILD" -- c seguir design sdd/features/DEFINE_X.md build
  cenario "seguir PARAR (DEFINE em rascunho)" 1 "não está pronto (Status: Draft)" -- c seguir define sdd/features/DEFINE_R.md design
  cenario "seguir PARAR (gate sem kind)" 1 "Verify Gate sem kind ou cmd" -- c seguir define sdd/features/DEFINE_K.md design
  cenario "seguir PARAR (marcador)" 1 "marcador de clarificação" -- c seguir define sdd/features/DEFINE_M.md design
  cenario "seguir PARAR (revisão do DESIGN não registrada)" 1 "não registrada no Advisor Ledger" -- c seguir design sdd/features/DEFINE_V.md build
  cenario "seguir PARAR (release é D1)" 1 "(D1)" -- c seguir build sdd/features/DEFINE_X.md release
  cenario "seguir par inválido" 64 "par de fases inválido" -- c seguir build sdd/features/DEFINE_X.md design
  printf 'flow:\n  autonomous: sim\n' > "$R/sdd/config.yaml"
  cenario "estado inválido" 64 'flow.autonomous = "sim"' -- c estado
  cenario "seguir slot inválido" 64 "troque por true" -- c seguir define sdd/features/DEFINE_X.md design

  if [ "$FALHAS" -eq 0 ]; then
    printf 'RESULTADO: VERDE\n→ todos os cenários bateram.\n'
    exit 0
  fi
  printf 'RESULTADO: VERMELHO\n→ %s cenário(s) acima não bateram; o contrato do sdd-fluxo.sh mudou.\n' "$FALHAS"
  exit 1
}

case "${1:-}" in
  review-design|seguir|estado) precisa_python; v="$1"; shift; nucleo "$v" "$@" ;;
  loop)        shift; precisa_python "$@"; nucleo loop "$@" ;;
  despachar)   precisa_python; shift; cmd_despachar "$@" ;;
  --self-test) precisa_python; cmd_self_test ;;
  *)           uso ;;
esac
