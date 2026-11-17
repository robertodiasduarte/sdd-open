#!/usr/bin/env bash
# papel-medir.sh — pontua as execuções de uma série do papel-serie.sh contra o gabarito e aponta o modelo mais
# barato que bate a meta. Doc: docs/model-per-role.md. Desenho: DESIGN_F23B2_MODELO_POR_PAPEL (Decision 7).
#
# Por que existe: trocar o modelo de um papel por palpite arrisca o veredito que segura o build ou o delta que muda
# o playbook. Aqui a troca só é apontada quando o candidato bate a meta em TODAS as repetições de TODOS os casos e
# custa pelo menos --limiar % menos que a referência (o modelo atual). Este script só lê: não chama modelo nem rede.
#
# USO-INICIO
#   papel-medir.sh <pasta da série> [--limiar 30] [--saida <arquivo>|-] [--so-referencia]
#       lê serie.txt, candidatos.tsv (a 1ª linha é a referência), execucoes/<caso>/<candidato>/<rep>/{meta,saida}.txt,
#       PARADA.txt e o gabarito (<caso>/esperado.txt; no curador, também <caso>/playbook.md).
#       Meta do curador, por execução: contagens ajudou/mordeu com precisão e recall >= 0,9; >= 2/3 dos ADD/REFINE/
#         TOMBSTONE esperados (REFINE e TOMBSTONE pelo LM-nnn; ADD pela seção e 1 termo de sup: em comum); o delta
#         proposto (AUTO e ACEITAR) aceito pelo playbook-curator.sh --aplicar. promover e inv ficam fora da conta.
#       Meta do avaliador, por execução: VEREDITO igual; >= 90% dos ATs do gabarito com o mesmo resultado; 0 AT que é
#         FAIL no gabarito e PASS na execução. AT ausente conta como diferente, nunca como PASS.
#       Execução com rc diferente de 0 (o agente saiu com erro ou passou do --teto-s) fica fora da meta. Gabarito do
#         avaliador sem VEREDITO ou sem linha AT-nnn, ou caso sem esperado.txt (ou sem playbook.md no curador) ⇒ 64.
#       Ordem do veredito: PARCIAL se a referência está incompleta ou inválida · REFERÊNCIA FORA DA META · PARCIAL se
#         há PARADA.txt, candidato pela metade ou execução inválida · a escolha.
#       0 ESCOLHIDO: <id> · 1 SEM GANHO MEDIDO · 3 REFERÊNCIA FORA DA META · 4 PARCIAL · 64 uso
#       --so-referencia: confere só a referência (0 REFERÊNCIA NA META · 3 · 4) — o papel-serie.sh roda isto antes de
#         chamar qualquer candidato.
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
  echo "🛑 papel-medir: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_PAPEL_MEDIR_BIN="$(cd "${_sdd_bin}" && { pwd -W 2>/dev/null || pwd; })"
SDD_PAPEL_MEDIR_BASH="${BASH:-bash}"   # LM-029
export SDD_PAPEL_MEDIR_BIN SDD_PAPEL_MEDIR_BASH

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # LM-015: saída em UTF-8 e "\n" também no Windows
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import os, re, subprocess, sys, tempfile
from decimal import Decimal, InvalidOperation

BIN = os.environ["SDD_PAPEL_MEDIR_BIN"]
BASH = os.environ.get("SDD_PAPEL_MEDIR_BASH") or "bash"
PAPEIS_COM_PONTUADOR = ("curador", "avaliador")
CONTAGEM_RE = re.compile(r"(LM-\d{3,}) (ajudou|mordeu)\+1\Z")
MUDANCA_RE = re.compile(r"(REFINE|TOMBSTONE) (LM-\d{3,}) ::")
ADD_RE = re.compile(r"ADD (.+?) :: sup: (.+?) :: ")
AT_RE = re.compile(r"AT-\d{3}\Z")
# lista fechada (LM-005, LM-028): a 1ª palavra da célula, sem marcação; o resto é ILEGIVEL, nunca PASS
PALAVRAS = {"PASS": "PASS", "✅": "PASS", "PASSA": "PASS", "PASSOU": "PASS",
            "FAIL": "FAIL", "❌": "FAIL", "FALHA": "FAIL", "FALHOU": "FAIL", "NEEDS_WORK": "FAIL",
            "NAO_VERIFICADO": "NAO_VERIFICADO", "NÃO_VERIFICADO": "NAO_VERIFICADO"}


def uso(msg):
    print("🛑 papel-medir: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ rode `papel-medir.sh --help` para ver o uso.", file=sys.stderr)
    sys.exit(64)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


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


def mediana(vs):
    vs = sorted(vs)
    n = len(vs)
    return vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2


# ── argumentos ──────────────────────────────────────────────────────────────────────────────────────
args = sys.argv[1:]
op = {"--limiar": "30", "--saida": None}
so_ref = False
serie = None
i = 0
while i < len(args):
    a = args[i]
    if a == "--so-referencia":
        so_ref = True
        i += 1
        continue
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
if serie is None or not os.path.isdir(serie):
    uso("falta a pasta da série, ou ela não existe")
serie = os.path.realpath(serie)
if not re.match(r"[1-9][0-9]?\Z", op["--limiar"]):
    uso("--limiar pede um inteiro de 1 a 99 (por cento)")
LIMIAR = Decimal(op["--limiar"])

cfg = chaves(ler(os.path.join(serie, "serie.txt")))
PAPEL = cfg.get("papel", "")
if PAPEL not in PAPEIS_COM_PONTUADOR:
    uso("serie.txt: papel %s sem pontuador (há para: %s)" % (PAPEL or "(vazio)", ", ".join(PAPEIS_COM_PONTUADOR)))
if not re.match(r"[1-9]\Z|10\Z", cfg.get("repeticoes", "")):
    uso("serie.txt: repeticoes de 1 a 10")
REPS = int(cfg["repeticoes"])
gab = cfg.get("gabarito", "")
gab = os.path.realpath(gab if os.path.isabs(gab) else os.path.join(serie, gab)) if gab else ""
if not gab or not os.path.isdir(gab):
    uso("serie.txt: o gabarito não existe")
candidatos = []
for ln in (ler(os.path.join(serie, "candidatos.tsv")) or "").splitlines():
    if ln.strip() and not ln.startswith("#"):
        c = [x.strip() for x in ln.split("\t")]
        if len(c) != 3:
            uso("candidatos.tsv com linha fora do formato id · modelo · cobranca")
        candidatos.append({"id": c[0], "modelo": c[1]})
if not candidatos:
    uso("candidatos.tsv vazio")
casos = sorted(n for n in os.listdir(gab) if chaves(ler(os.path.join(gab, n, "caso.txt"))).get("papel") == PAPEL)
if not casos:
    uso("o gabarito não tem caso do papel %s" % PAPEL)
# N1 da revisão do código: um gabarito sem o que comparar aprovaria qualquer resposta (veredito None = None)
for n in casos:
    esp = ler(os.path.join(gab, n, "esperado.txt"))
    if esp is None:
        uso("caso %s sem esperado.txt legível" % n)
    if PAPEL == "avaliador":
        ats = [ln.split() for ln in esp.splitlines()]
        if not re.search(r"VEREDITO:\s*\**\s*[A-Z_]+", esp) or not any(
                len(c) == 2 and re.match(r"AT-\d{3}\Z", c[0]) and c[1] in ("PASS", "FAIL", "NAO_VERIFICADO")
                for c in ats):
            uso("caso %s: esperado.txt sem VEREDITO: <X> ou sem linha AT-nnn PASS|FAIL|NAO_VERIFICADO" % n)
    elif ler(os.path.join(gab, n, "playbook.md")) is None:
        uso("caso %s sem playbook.md legível (o playbook de antes da curadoria)" % n)


# ── leitura do bloco ────────────────────────────────────────────────────────────────────────────────
def ultimo_bloco(texto, nome):
    ini = (texto or "").rfind("<<<" + nome)
    if ini < 0:
        return None
    fim = texto.find("\n>>>", ini)
    return texto[ini:fim] if fim >= 0 else None


def celulas(ln):
    """Células de uma linha de tabela markdown; `\\|` é barra dentro da célula."""
    partes = re.split(r"(?<!\\)\|", ln.strip())
    return [p.strip().replace("\\|", "|") for p in partes[1:-1]]


def tabela(bloco):
    """[{coluna: valor}] da 1ª tabela do bloco com cabeçalho; linhas com outra contagem de células ficam fora."""
    cab, linhas = None, []
    for ln in bloco.splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = celulas(ln)
        if cab is None:
            cab = [x.lower() for x in c]
            continue
        if all(re.match(r":?-{2,}:?\Z", x) for x in c if x):
            continue
        if len(c) == len(cab):
            linhas.append(dict(zip(cab, c)))
    return cab or [], linhas


# ── curador ─────────────────────────────────────────────────────────────────────────────────────────
def delta_partes(linhas):
    cont, refs, adds = set(), set(), []
    for d in linhas:
        d = d.strip().strip("`")
        m = CONTAGEM_RE.match(d)
        if m:
            cont.add((m.group(1), m.group(2)))
            continue
        m = MUDANCA_RE.match(d)
        if m:
            refs.add((m.group(1), m.group(2)))
            continue
        m = ADD_RE.match(d)
        if m:
            adds.append((m.group(1).strip().lower(), set(re.findall(r"`([^`]+)`", m.group(2)))))
    return cont, refs, adds


def pontua_curador(caso, saida):
    bloco = ultimo_bloco(saida, "CURADORIA")
    if bloco is None:
        return False, "sem bloco <<<CURADORIA"
    cab, linhas = tabela(bloco)
    col_rec = next((c for c in cab if c.startswith("recomenda")), None)
    if "tipo" not in cab or "delta" not in cab or col_rec is None:
        return False, "tabela do bloco sem as colunas Tipo, Delta e Recomendação"
    propostos = [l["delta"] for l in linhas if l["tipo"].lower() not in ("promover", "inv")
                 and re.match(r"(AUTO|ACEITAR)\b", l[col_rec].strip())]
    esperado = [l for l in (ler(os.path.join(gab, caso, "esperado.txt")) or "").splitlines()
                if l.strip() and not l.lstrip().startswith("#") and "promovido_para=" not in l]
    pc, pr, pa = delta_partes(propostos)
    ec, er, ea = delta_partes(esperado)
    inter = len(pc & ec)
    prec = Decimal(inter) / len(pc) if pc else Decimal(1)
    rec = Decimal(inter) / len(ec) if ec else Decimal(1)
    achados = len(pr & er) + sum(1 for s, sup in ea if any(ps == s and (psup & sup) for ps, psup in pa))
    total_mud = len(er) + len(ea)
    mud = Decimal(achados) / total_mud if total_mud else Decimal(1)
    with tempfile.TemporaryDirectory() as td:   # o --aplicar escreve só no stdout; o gabarito nunca é escrito
        arq = os.path.join(td, "delta.txt")
        with open(arq, "w", encoding="utf-8", newline="\n") as h:
            h.write("\n".join(d.strip().strip("`") for d in propostos) + "\n")
        r = subprocess.run([BASH, os.path.join(BIN, "playbook-curator.sh"), "--aplicar", arq,
                            os.path.join(gab, caso, "playbook.md")], capture_output=True)
    motivos = []
    if prec < Decimal("0.9") or rec < Decimal("0.9"):
        motivos.append("contagens: precisão %s, recall %s" % (round(prec, 2), round(rec, 2)))
    if mud * 3 < 2:
        motivos.append("ADD/REFINE/TOMBSTONE: %d de %d" % (achados, total_mud))
    if r.returncode != 0:
        motivos.append("o --aplicar recusou o delta (exit %d)" % r.returncode)
    return (not motivos), "; ".join(motivos)


# ── avaliador ───────────────────────────────────────────────────────────────────────────────────────
def resultado(celula):
    palavras = re.sub(r"[*`]", "", celula).strip().upper().split()
    if not palavras:
        return "ILEGIVEL"
    p0 = palavras[0].strip(".,:;")
    if p0 in ("NÃO", "NAO") and len(palavras) > 1 and palavras[1].strip(".,:;") == "VERIFICADO":
        return "NAO_VERIFICADO"
    return PALAVRAS.get(p0, "ILEGIVEL")


def veredito(texto):
    m = re.search(r"VEREDITO:\s*\**\s*([A-Z_]+)", texto or "")
    return m.group(1) if m else None


def pontua_avaliador(caso, saida):
    bloco = ultimo_bloco(saida, "AVALIACAO")
    if bloco is None:
        return False, "sem bloco <<<AVALIACAO"
    esp_txt = ler(os.path.join(gab, caso, "esperado.txt")) or ""
    esp_v = veredito(esp_txt)
    esp = {}
    for ln in esp_txt.splitlines():
        c = ln.split()
        if len(c) == 2 and AT_RE.match(c[0]):
            esp[c[0]] = c[1]
    got = {}
    for ln in bloco.splitlines():
        if ln.strip().startswith("|"):
            c = celulas(ln)
            if c and AT_RE.match(c[0]) and c[0] not in got:
                ultimo = next((x for x in reversed(c[1:]) if x), "")
                got[c[0]] = resultado(ultimo)
    v = veredito(bloco)
    iguais = sum(1 for at, r in esp.items() if got.get(at) == r)
    falso_pass = [at for at, r in esp.items() if r == "FAIL" and got.get(at) == "PASS"]
    motivos = []
    if v != esp_v:
        motivos.append("veredito %s, esperado %s" % (v or "ilegível", esp_v))
    if esp and Decimal(iguais) / len(esp) < Decimal("0.9"):
        motivos.append("ATs iguais: %d de %d" % (iguais, len(esp)))
    if falso_pass:
        motivos.append("AT que falha dado como aprovado: " + ", ".join(falso_pass))
    return (not motivos), "; ".join(motivos)


PONTUA = {"curador": pontua_curador, "avaliador": pontua_avaliador}


# ── as séries ───────────────────────────────────────────────────────────────────────────────────────
def series_de(cand):
    """[{caso, rep, estado, na_meta, motivo, nominal}] das execuções gravadas, e quantas faltam."""
    out, faltam = [], 0
    for caso in casos:
        for rep in range(1, REPS + 1):
            pasta = os.path.join(serie, "execucoes", caso, cand["id"], str(rep))
            meta = chaves(ler(os.path.join(pasta, "meta.txt")))
            if not meta:
                faltam += 1
                continue
            e = {"caso": caso, "rep": rep, "estado": meta.get("estado", "?"), "nominal": decimal(meta.get("nominal"))}
            if e["estado"] != "ok":
                e.update(na_meta=False, motivo="execução %s" % e["estado"])
            elif meta.get("rc", "") != "0":
                # R2 da revisão do código: agente que saiu ≠ 0 ou passou do --teto-s (124) fica fora da meta
                e.update(na_meta=False, motivo="o agente saiu %s" % (meta.get("rc") or "sem rc"))
            else:
                e["na_meta"], e["motivo"] = PONTUA[PAPEL](caso, ler(os.path.join(pasta, "saida.txt")) or "")
            out.append(e)
    return out, faltam


linhas_rel = []
p = linhas_rel.append


def fecha(rc, palavra, seta):
    p("RESULTADO: " + palavra)
    p("→ " + seta)
    texto = "\n".join(linhas_rel) + "\n"
    if op["--saida"] and op["--saida"] != "-":
        with open(op["--saida"], "w", encoding="utf-8", newline="\n") as h:
            h.write(texto)
    sys.stdout.write(texto)
    sys.exit(rc)


p("# Medição — %s (papel %s)" % (os.path.basename(serie), PAPEL))
p("")
p("Gabarito: %d caso(s) × %d repetição(ões). Referência: %s. Limiar de ganho: %s%%." % (
    len(casos), REPS, candidatos[0]["id"], LIMIAR))
p("")
avaliar = candidatos[:1] if so_ref else candidatos
dados = {c["id"]: series_de(c) for c in avaliar}
p("| Candidato | Modelo | Na meta | Mediana nominal US$ | Queda × referência |")
p("|---|---|---:|---:|---:|")
ref_id = candidatos[0]["id"]


def med(ex):
    vs = [e["nominal"] for e in ex if e["estado"] == "ok"]
    return mediana(vs) if vs and all(v is not None for v in vs) else None


med_ref = med(dados[ref_id][0])
for c in avaliar:
    ex, falt = dados[c["id"]]
    m = med(ex)
    queda = ("%s%%" % round((1 - m / med_ref) * 100, 1)) if (m is not None and med_ref) else "—"
    p("| %s | %s | %d de %d%s | %s | %s |" % (c["id"], c["modelo"], sum(1 for e in ex if e["na_meta"]), len(ex),
                                            " (faltam %d)" % falt if falt else "",
                                            m if m is not None else ("n/d" if ex else "—"), queda))
fora = [(c["id"], e) for c in avaliar for e in dados[c["id"]][0] if not e["na_meta"]]
if fora:
    p("")
    p("Fora da meta:")
    for cid, e in fora:
        p("- %s · %s · rep %d — %s" % (cid, e["caso"], e["rep"], e["motivo"]))
p("")

# Ordem (R2 da revisão D1): uma referência incompleta ou inválida é PARCIAL, nunca "fora da meta"; uma referência
# completa e fora da meta é dita mesmo com a série parada (o papel-serie.sh para exatamente por isso, exit 22); e
# nenhum vencedor sai de série parada, incompleta ou com execução inválida.
ex_ref, falt_ref = dados[ref_id]


def parcial(ids, parada):
    invalidas = [cid for cid in ids if any(e["estado"] == "invalida" for e in dados[cid][0])]
    incompletos = [cid for cid in ids if dados[cid][1] and (cid == ref_id or dados[cid][0])]
    if parada or invalidas or incompletos:
        motivo = "; ".join(x for x in ["série parada (PARADA.txt)" if parada else "",
                                       "execução inválida em " + ", ".join(invalidas) if invalidas else "",
                                       "execuções faltando em " + ", ".join(incompletos) if incompletos else ""] if x)
        fecha(4, "PARCIAL", motivo + ": nenhum vencedor; retome a série com o papel-serie.sh e meça de novo.")


# 1. a referência precisa estar inteira e válida
parcial([ref_id], False)
# 2. a referência
if not ex_ref or not all(e["na_meta"] for e in ex_ref):
    fecha(3, "REFERÊNCIA FORA DA META", "o modelo atual não bate a meta no gabarito: recalibre o gabarito ou a meta "
          "antes de qualquer candidato (série antiga primeiro, LM-011).")
if so_ref:
    fecha(0, "REFERÊNCIA NA META", "os candidatos podem rodar.")
# 3. série parada, candidato pela metade ou execução inválida: sem vencedor
parcial([c["id"] for c in candidatos], os.path.isfile(os.path.join(serie, "PARADA.txt")))
# 3. a escolha
if med_ref is None:
    fecha(1, "SEM GANHO MEDIDO", "a referência tem custo n/d: sem a mediana dela, nenhuma queda se mede.")
ok = []
for c in candidatos[1:]:
    ex, _ = dados[c["id"]]
    m = med(ex)
    if ex and all(e["na_meta"] for e in ex) and m is not None:   # sem execução, ou com n/d, não concorre
        ok.append((m, c["id"]))
if ok:
    m, cid = min(ok)
    if m <= med_ref * (1 - LIMIAR / 100):
        fecha(0, "ESCOLHIDO: " + cid, "mediana %s contra %s da referência; preencha o slot do papel com o modelo de %s "
              "(escolha local: o pacote não leva nome de modelo)." % (m, med_ref, cid))
fecha(1, "SEM GANHO MEDIDO", "nenhum candidato bate a meta em todas as execuções com queda de %s%% ou mais; o slot "
      "fica vazio e isso não conta como economia." % LIMIAR)
PY
