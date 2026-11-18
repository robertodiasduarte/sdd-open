#!/usr/bin/env bash
# desempenho-diagnostico.sh — o diagnóstico do banco no ar da skill sdd-desempenho-banco: coleta, só com o OK da
# pessoa e só por uma lista fixa de comandos de leitura do Supabase CLI, e interpreta o resultado com as regras que
# evitam os falsos alarmes (índice "não usado" sem a idade das estatísticas, achado tratado como correção, consulta
# culpada quando a máquina é que está pequena). Nunca escreve no banco.
#
# USO-INICIO
#   desempenho-diagnostico.sh --ler <arquivo|pasta> [--estatisticas-desde AAAA-MM-DD] [--saida ARQ]
#       interpreta, sem rede e sem executar nada, a saída salva dos advisors (o get_advisors do MCP, gravado num
#       arquivo fora do projeto, ou o `supabase db advisors`) e do `supabase inspect db` (JSON).
#   desempenho-diagnostico.sh --coletar --consentimento [--estatisticas-desde AAAA-MM-DD] [--saida ARQ]
#       lê o banco no ar pelo projeto já ligado ao CLI (supabase link) e interpreta. Sem --consentimento, nada roda.
#       Nunca aceita string de conexão nem senha; a saída bruta fica numa pasta temporária, fora do projeto.
#   0 RELATÓRIO PRONTO · 64 ERRO DE USO (opção, consentimento, data, CLI ausente, arquivo ilegível)
#   --estatisticas-desde: desde quando as estatísticas contam (consulta 1 de CONSULTAS_DIAGNOSTICO.md); sem ela,
#   nenhum índice "não usado" é indicado para apagar; com menos de 30 dias, também não.
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
  echo "🛑 desempenho-diagnostico: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo; nada foi lido nem executado.\n' >&2
  exit 64
fi

erro() {   # causa e conserto, e sai 64 sem ter executado nada além do que já disse
  # a causa pode vir do CLI: a senha de uma string de conexão nunca chega à tela (revisão do DESIGN, R8)
  echo "🛑 desempenho-diagnostico: $1" \
    | sed -E 's#(postgres(ql)?://[^:/@ ]*:)[^ ]*@#\1***@#g; s#([Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Pp][Aa][Ss][Ss][Ww][Dd]|[Pp][Ww][Dd])=[^ ]*#\1=***#g' >&2
  printf 'RESULTADO: ERRO DE USO\n→ %s\n' "$2" >&2
  exit 64
}

# O núcleo vai ao Python pela entrada padrão, como nos outros scripts de sdd/bin: por argumento, o Git Bash do
# Windows converteria trechos que parecem caminho.
nucleo() {
  cat <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import datetime, json, os, re, sys

for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

def _inesperado(tipo, valor, _tb):
    """Erro que ninguém previu sai 64 com a causa, nunca 1 nem um traceback (revisão do DESIGN, N2)."""
    print("🛑 desempenho-diagnostico: erro inesperado (%s: %s)" % (tipo.__name__, str(valor)[:160]), file=sys.stderr)
    print("RESULTADO: ERRO DE USO", file=sys.stderr)
    print("→ rode de novo; se repetir, guarde esta mensagem e o arquivo lido; nada foi escrito no banco.", file=sys.stderr)
    os._exit(64)


sys.excepthook = _inesperado
TETO = 5
GRAV = {"alta": 0, "media": 1, "baixa": 2}
# lint do advisor → (ficha, gravidade, título, passo que confirma). Os outros lints entram com "—" e o link do próprio.
LINTS = {
    "auth_rls_initplan": ("P01", "alta", "Política que chama auth.uid() uma vez por linha",
                          "leia a política (Authentication › Policies) e confira se a chamada está dentro de (select …)"),
    "unindexed_foreign_keys": ("P03", "media", "Chave estrangeira sem índice",
                               "confira em Database › Indexes que a coluna da chave não tem índice; priorize as tabelas grandes (consulta 9)"),
    "no_primary_key": ("P04", "media", "Tabela sem chave primária", "abra a tabela em Table Editor e confira a chave"),
    "multiple_permissive_policies": ("P05", "media", "Duas políticas que liberam a mesma coisa",
                                     "liste as políticas da tabela e confira o papel e a ação de cada uma"),
    "duplicate_index": ("P07", "baixa", "Índice repetido", "compare as colunas dos dois índices em Database › Indexes"),
}
PASSO_PADRAO = "abra o link do advisor e confira no painel antes de corrigir"
CONEXAO = re.compile(r"(?i)\b(postgres(?:ql)?://[^:/@\s]*:)\S*@")
SENHA_KV = re.compile(r"(?i)(password|passwd|pwd)(\s*=\s*)('[^']*'|\"[^\"]*\"|\S+)")   # também PGPASSWORD= (avaliador, ciclo 2)
NUMERO = re.compile(r"(?<![\w$.])(?:0[xX][0-9A-Fa-f_]+|\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?)(?![\w.])")   # 1e10, 1_000, 0x1F
CONTROLE = re.compile("[\x00-\x1f\x7f-\x9f\u2028\u2029]")   # C0, C1 e os separadores de linha do Unicode (D3, R3)


def fim(rc, palavra, seta, para=sys.stdout):
    print("RESULTADO: %s" % palavra, file=para)
    print("→ %s" % seta, file=para)
    sys.exit(rc)


def uso(msg, seta="rode com --help para ver o uso; nada foi lido nem executado."):
    print("🛑 desempenho-diagnostico: %s" % msg, file=sys.stderr)
    fim(64, "ERRO DE USO", seta, sys.stderr)


def senha_fora(t):
    """Senha nunca chega à tela nem ao arquivo: URL com senha e password=… (revisão do DESIGN, R6)."""
    t = CONEXAO.sub(r"\1***@", t)
    return SENHA_KV.sub(r"\1\2***", t)


def mascara_sql(t):
    """Um leitor só para comentário, texto, identificador e número (avaliador, ciclos 2 e 3): o apóstrofo dentro de um
    comentário ou de um nome entre aspas duplas não abre texto, o comentário pode ter outro dentro, e a barra invertida
    só escapa em E'...'. Comentário vira /*?*/, texto vira '?', $tag$...$tag$ vira $tag$?$tag$, número vira ?.
    Falha fechado: se sobrar aspa ou fim de comentário solto no resultado, o texto é cortado ali."""
    out, i, n, trecho = [], 0, len(t), []

    def solta():
        if trecho:
            out.append(NUMERO.sub("?", "".join(trecho)))
            del trecho[:]
    while i < n:
        c = t[i]
        if t.startswith("--", i):
            j = t.find("\n", i)
            solta(); out.append("/*?*/"); i = n if j < 0 else j
            continue
        if t.startswith("/*", i):
            nivel, j = 1, i + 2
            while j < n and nivel:
                if t.startswith("/*", j):
                    nivel, j = nivel + 1, j + 2
                elif t.startswith("*/", j):
                    nivel, j = nivel - 1, j + 2
                else:
                    j += 1
            solta(); out.append("/*?*/"); i = j
            continue
        m = re.match(r"\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$", t[i:]) if c == "$" else None
        if m:
            j = t.find(m.group(0), i + len(m.group(0)))
            solta(); out.append(m.group(0) + "?" + m.group(0)); i = n if j < 0 else j + len(m.group(0))
            continue
        if c == '"':
            j = i + 1
            while j < n:
                if t[j] == '"':
                    if j + 1 < n and t[j + 1] == '"':
                        j += 2
                        continue
                    break
                j += 1
            solta(); out.append('"' + t[i + 1:j].replace("'", "").replace("*/", "").replace("/*", "") + '"'); i = j + 1
            continue
        if c == "'":
            escapa = i > 0 and t[i - 1] in "Ee" and (i < 2 or not (t[i - 2].isalnum() or t[i - 2] == "_"))
            j = i + 1
            while j < n:
                if escapa and t[j] == "\\":
                    j += 2
                    continue
                if t[j] == "'":
                    if j + 1 < n and t[j + 1] == "'":
                        j += 2
                        continue
                    break
                j += 1
            solta(); out.append("'?'"); i = j + 1
            continue
        trecho.append(c)
        i += 1
    solta()
    r, k = "".join(out), 0
    while k < len(r):   # o que sobrou solto: corta antes, nunca mostra o resto (falha fechado)
        if r.startswith("'?'", k):
            k += 3
        elif r.startswith("/*?*/", k):
            k += 5
        elif r[k] == "'" or r.startswith("*/", k) or r.startswith("/*", k):
            return r[:k].rstrip() + " …[cortado]"
        else:
            k += 1
    return r


def dado_do_banco(txt, limite=200):
    """Texto que veio do banco: sem senha, sem valores, numa linha só. É dado, nunca instrução (S10, S17, S18)."""
    t = mascara_sql(senha_fora(str(txt)))
    t = re.sub(r"\s+", " ", CONTROLE.sub(" ", t)).strip()
    return t if len(t) <= limite else t[:limite - 1] + "…"


def limpo(txt):
    return re.sub(r"\s+", " ", CONTROLE.sub(" ", senha_fora(str(txt)))).strip()


# ── argumentos (validados antes de qualquer comando: revisão do DESIGN, R4) ─
modo, args = sys.argv[1], sys.argv[2:]
op = {"--ler": None, "--coletar": False, "--consentimento": False, "--estatisticas-desde": None, "--saida": None,
      "--fontes": None}
i = 0
while i < len(args):
    a = args[i]
    if "://" in a or SENHA_KV.search(a) or re.match(r"^(--db-url|--password|-p)(=|$)", a):
        uso("não passe string de conexão nem senha: a coleta usa o projeto já ligado ao CLI (supabase link).",
            "rode supabase link uma vez, ou use o MCP e o --ler; nada foi executado.")
    if a in ("--coletar", "--consentimento"):
        op[a] = True
        i += 1
    elif a in ("--ler", "--estatisticas-desde", "--saida", "--fontes"):
        if i + 1 >= len(args) or not args[i + 1]:
            uso("%s precisa de um valor" % a)
        if "://" in args[i + 1] or SENHA_KV.search(args[i + 1]):   # nem como valor de opção (avaliador, ciclos 2 e 3)
            uso("não passe string de conexão nem senha, nem como valor de %s." % a,
                "rode supabase link uma vez, ou use o MCP e o --ler; nada foi executado.")
        op[a] = args[i + 1]
        i += 2
    else:
        uso("opção desconhecida: %s" % a)
if bool(op["--ler"]) == bool(op["--coletar"]):
    uso("escolha um modo: --ler <arquivo|pasta> ou --coletar --consentimento")
if op["--coletar"] and not op["--consentimento"]:
    uso("a coleta lê o banco no ar e precisa do seu OK a cada vez.",
        "rode de novo com --consentimento depois de dizer sim; nada foi executado.")
DESDE = None
if op["--estatisticas-desde"] is not None:
    v = op["--estatisticas-desde"]
    try:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError
        DESDE = datetime.date(int(v[:4]), int(v[5:7]), int(v[8:10]))
    except ValueError:
        uso("--estatisticas-desde precisa de uma data AAAA-MM-DD válida: %s" % limpo(v)[:40],
            "use a data que a consulta 1 de CONSULTAS_DIAGNOSTICO.md mostrar; nada foi executado.")
    if DESDE > datetime.date.today():
        uso("--estatisticas-desde no futuro: %s" % v, "use a data que a consulta 1 mostrar; nada foi executado.")
if op["--ler"] is not None and not os.path.exists(op["--ler"]):
    uso("não achei %s" % limpo(op["--ler"]))
if modo == "validar":
    # o modo que o bash segue vem daqui, nunca de procurar "--coletar" no texto dos argumentos: um "--coletar" que é o
    # valor de --saida rodaria a coleta sem consentimento (revisão do código, rodada 1, R1)
    print("coletar" if op["--coletar"] else "ler")
    sys.exit(0)


# ── leitura do que foi salvo ───────────────────────────────────────────────
def arquivos(alvo):
    if os.path.isdir(alvo):
        return sorted(os.path.join(alvo, n) for n in os.listdir(alvo)
                      if n.endswith((".json", ".txt")) and not n.startswith("_"))
    return [alvo]


SUBCOMANDOS = ("db-stats", "index-stats", "table-stats", "outliers", "calls", "long-running-queries", "blocking", "locks",
               "bloat", "vacuum-stats", "role-stats")
CHAVES_LINT = ("categories", "facing", "remediation", "cache_key", "findings")


def e_lint(x):
    """Um lint do advisor tem `name` e ao menos uma chave que linha de `inspect db` não tem (avaliador, ciclo 1): sem
    isso, o índice `ix_bom` de um index-stats em lista virava "advisor: ix_bom"."""
    return isinstance(x, dict) and "name" in x and any(k in x for k in CHAVES_LINT)


def lints_de(dado):
    """Os formatos aceitos: lista de lints; {"lints": […]}; {"result"|"results": …}; o agrupado do MCP (findings)."""
    if isinstance(dado, dict):
        for k in ("lints", "results", "result", "data"):
            if k in dado:
                return lints_de(dado[k])
        return [dado] if e_lint(dado) else []
    if not isinstance(dado, list):
        return []
    out = []
    for x in dado:
        if not e_lint(x):
            continue
        if isinstance(x.get("findings"), list):
            for f in x["findings"]:
                y = dict(x)
                y.pop("findings", None)
                if isinstance(f, dict):
                    y.update(f)
                out.append(y)
        else:
            out.append(x)
    return out


def linhas_de(dado):
    if isinstance(dado, dict):
        for k in ("rows", "results", "result", "data"):
            if isinstance(dado.get(k), list):
                return dado[k]
    return dado if isinstance(dado, list) else []


lints, inspect, texto_cru, fontes = [], {}, [], 0
# O relatório nunca sai limpo sobre o que não leu (revisão do código, rodada 3, R1 e R2): comando da coleta que falhou,
# JSON que não é lint nem linhas do inspect db, linhas do inspect num arquivo com nome que não é de subcomando.
nao_reconhecidos, sem_nome, nao_lidos = [], [], []
if os.path.isdir(op["--ler"]):
    try:
        with open(os.path.join(op["--ler"], "_falhou.txt"), encoding="utf-8") as fh:
            nao_lidos = [re.sub(r"[^a-z-]", "", x.strip().lower())[:40] for x in fh if x.strip()]
    except OSError:
        pass
for arq in arquivos(op["--ler"]):
    nomearq = os.path.basename(arq)
    try:
        bruto = open(arq, encoding="utf-8", errors="replace").read()
    except OSError as e:
        uso("não deu para ler %s (%s)" % (nomearq, e))
    if not bruto.strip():
        continue
    fontes += 1
    if not arq.endswith(".json") and not bruto.lstrip().startswith(("[", "{")):
        texto_cru.append(nomearq)
        continue
    try:
        dado = json.loads(bruto)
    except ValueError as e:
        if op["--coletar"] or os.path.isdir(op["--ler"]):
            texto_cru.append(nomearq)
            continue
        uso("%s não é JSON legível (%s)" % (nomearq, str(e)[:80]),
            "grave a resposta inteira do advisor, como veio, e rode de novo.")
    sub = re.sub(r"\.(json|txt)$", "", nomearq)
    # o arquivo de um subcomando do inspect db (o nome que a coleta grava) nunca é lido como advisor
    ls = [] if sub in SUBCOMANDOS else lints_de(dado)
    if ls:
        lints.extend(ls)
        continue
    if not (isinstance(dado, list) or (isinstance(dado, dict) and
                                       any(isinstance(dado.get(k), list) for k in ("rows", "results", "result", "data")))):
        nao_reconhecidos.append(nomearq)   # ex.: a resposta de erro {"message": "Unauthorized"}, gravada como veio
        fontes -= 1
        continue
    rows = [r for r in linhas_de(dado) if isinstance(r, dict)]
    if rows and sub not in SUBCOMANDOS:
        sem_nome.append(nomearq)
        fontes -= 1
        continue
    if rows:
        inspect.setdefault(sub, []).extend(rows)


# ── regras de interpretação ────────────────────────────────────────────────
HOJE = datetime.date.today()
achados = []   # {"id", "grav", "titulo", "n", "passo", "dados": [texto do banco], "extra"}


def chave_ci(row, *nomes):
    for k, v in row.items():
        if k.lower() in nomes:
            return v
    return None


def regra_nao_usado(n, exemplos, origem):
    if DESDE is None:
        passo = ("idade das estatísticas desconhecida — não apague; descubra a data (consulta 1 de "
                 "CONSULTAS_DIAGNOSTICO.md ou o painel) e rode de novo com --estatisticas-desde")
    else:
        dias = (HOJE - DESDE).days
        if dias < 30:
            passo = "estatísticas de só %d dia(s) — não apague antes de 30; rode de novo depois" % dias
        else:
            passo = ("candidato a apagar, com estatísticas de %d dias: confirme que nenhuma consulta rara (fechamento do "
                     "mês) nem réplica usa o índice, e apague por migration pelo fluxo SDD; nunca apague índice único nem "
                     "de chave primária (eles garantem a regra mesmo sem uso)" % dias)
    achados.append({"id": "—", "grav": "baixa", "titulo": "Índice sem uso registrado (%s)" % origem, "n": n,
                    "passo": passo, "dados": exemplos})


por_nome = {}
for l in lints:
    por_nome.setdefault(str(l.get("name")), []).append(l)
for nome_lint, grupo in por_nome.items():
    exemplos = [dado_do_banco(x.get("detail") or "") for x in grupo if x.get("detail")]
    if nome_lint == "unused_index":
        regra_nao_usado(len(grupo), exemplos, "advisor")
        continue
    if nome_lint in LINTS:
        fid, grav, titulo, passo = LINTS[nome_lint]
    else:
        lv = str(grupo[0].get("level") or "").upper()
        fid, grav = "—", ("alta" if lv == "ERROR" else "media" if lv == "WARN" else "baixa")
        # Sem ficha, a linha do achado leva só o nome do lint (identificador); o título e o link do advisor vão para o
        # bloco de dado, como todo texto que veio de fora (revisão D3, R4).
        titulo = "advisor: " + (re.sub(r"[^a-z0-9_]", "", nome_lint.lower())[:60] or "sem nome")
        passo = PASSO_PADRAO + " (o link está no bloco de dado)"
        extra = [dado_do_banco(grupo[0].get(k) or "") for k in ("title", "remediation") if grupo[0].get(k)]
        exemplos = extra + exemplos
    achados.append({"id": fid, "grav": grav, "titulo": titulo, "n": len(grupo), "passo": passo, "dados": exemplos})

lentas = []
for sub in ("outliers", "calls"):
    for r in inspect.get(sub, []):
        q = chave_ci(r, "query", "statement")
        if q:
            lentas.append(dado_do_banco(q))
if lentas:
    achados.append({"id": "—", "grav": "media", "titulo": "Consultas que mais tomam tempo", "n": len(lentas),
                    "passo": "rode explain (verbose) de cada uma num banco de teste (consulta 10 de CONSULTAS_DIAGNOSTICO.md)",
                    "dados": lentas})
sem_uso = []
for r in inspect.get("index-stats", []):
    flag = chave_ci(r, "unused", "is_unused")
    scans = chave_ci(r, "idx_scan", "index_scans", "scans")
    nome_ix = str(chave_ci(r, "name", "index", "indice") or "").replace('"', "").lower()
    if re.search(r"_(?:pkey|key)$", nome_ix):
        continue   # o nome padrão da chave primária e do único: não se apaga por falta de uso (rodada 3, R3)
    if flag is True or str(flag).lower() == "true" or str(scans) == "0":
        sem_uso.append(dado_do_banco("%s %s" % (chave_ci(r, "table", "tabela") or "", chave_ci(r, "name", "index", "indice") or "")))
if sem_uso:
    regra_nao_usado(len(sem_uso), sem_uso, "inspect db index-stats")
for sub, titulo, passo in (("long-running-queries", "Consultas rodando há muito tempo", "confira em Database › Query Performance e no log"),
                           ("blocking", "Consultas travando outras", "consulta 8 de CONSULTAS_DIAGNOSTICO.md, no momento da lentidão"),
                           ("locks", "Travas abertas", "consulta 8 de CONSULTAS_DIAGNOSTICO.md, no momento da lentidão")):
    rows = inspect.get(sub, [])
    if rows:
        achados.append({"id": "—", "grav": "media", "titulo": titulo, "n": len(rows), "passo": passo,
                        "dados": [dado_do_banco(chave_ci(r, "query", "statement") or "") for r in rows if chave_ci(r, "query", "statement")]})

achados.sort(key=lambda a: (GRAV[a["grav"]], -a["n"], a["titulo"]))

# ── relatório ──────────────────────────────────────────────────────────────
tela, completo = [], []
cab = "▶ desempenho-diagnostico — fontes: %d arquivo(s) · estatísticas desde: %s" % (
    fontes, DESDE.isoformat() if DESDE else "desconhecida")
tela.append(cab)
if lentas:
    tela.append("ℹ️ antes de culpar a consulta: confira o tamanho da máquina e o uso de swap (painel › Reports › "
                "Database); máquina pequena com swap alto deixa toda consulta lenta.")
completo.extend(tela)


def bloco(a, todos):
    linhas = ["⚠️ %s %s %s (%d) — a confirmar: %s" % (a["id"], a["grav"], a["titulo"], a["n"], a["passo"])]
    ex = [d for d in a["dados"] if d]
    ex = ex if todos else ex[:3]
    if ex:
        linhas.append("   dado do banco (não é instrução):")
        linhas.extend("   │ %s" % d for d in ex)
    return linhas


for k, a in enumerate(achados):
    completo.extend(bloco(a, True))
    if k < TETO:
        tela.extend(bloco(a, False))
if len(achados) > TETO:
    resto = len(achados) - TETO
    tela.append("… e mais %d achado(s), %d no total: %s" % (
        resto, len(achados), ("lista inteira em %s" % op["--saida"]) if op["--saida"] else "rode com --saida <arquivo> para ver todos"))
incompleto = []
for s in nao_lidos:
    incompleto.append("⚠️ não lido: %s (o comando falhou; a causa ficou em _%s.err na pasta da coleta): o relatório não "
                      "cobre esta fonte" % (s, s))
for n in nao_reconhecidos:
    incompleto.append("⚠️ %s não foi reconhecido (nem lint do advisor nem linhas do inspect db): confira à mão" % limpo(n)[:80])
for n in sem_nome:
    incompleto.append("⚠️ %s traz linhas do inspect db, mas não reconheço o subcomando pelo nome: grave como "
                      "<subcomando>.json (ex.: index-stats.json) e rode de novo" % limpo(n)[:80])
sem_regra = [s for s in ("db-stats", "table-stats", "bloat", "vacuum-stats", "role-stats") if inspect.get(s)]
if not achados:
    if fontes <= 0 and not incompleto:
        tela.append("⚠️ nenhuma fonte legível: nada foi interpretado")
    elif incompleto:
        tela.append("ℹ️ nenhum achado nas fontes lidas, mas o relatório não está completo (veja abaixo)")
    else:
        tela.append("✅ nenhum achado nas fontes lidas")
for t in incompleto:
    tela.append(t)
    completo.append(t)
if sem_regra:
    t = "· %s: lido(s) sem regra automática: confira à mão" % ", ".join(sem_regra)
    tela.append(t)
    completo.append(t)
for nomearq in texto_cru:
    t = "· %s veio em texto: confira à mão (só o JSON é interpretado)" % nomearq
    tela.append(t)
    completo.append(t)
if op["--fontes"]:
    t = "· saída bruta da coleta em %s (fora do projeto; apague quando terminar)" % op["--fontes"]
    tela.append(t)
    completo.append(t)
print("\n".join(tela))
seta = ("nenhum achado é correção ainda: confirme cada um pelo passo indicado e leve a correção como migration pelo "
        "fluxo SDD (a skill não escreve no banco).")
completo.extend(["RESULTADO: RELATÓRIO PRONTO", "→ " + seta])
if op["--saida"]:
    try:
        d = os.path.dirname(os.path.abspath(op["--saida"]))
        os.makedirs(d, exist_ok=True)
        with open(op["--saida"], "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(completo) + "\n")
    except OSError as e:
        print("⚠️ não deu para gravar --saida (%s)" % limpo(str(e))[:120])
fim(0, "RELATÓRIO PRONTO", seta)
PY
}

# 1º, os argumentos: nenhum comando externo roda antes de eles passarem (consentimento, senha, data).
modo="$(nucleo | python3 -B - validar "$@")" || exit $?
modo="${modo%$'\r'}"   # o \r do Python no Windows
if [ "$modo" != "coletar" ]; then
  nucleo | python3 -B - interpretar "$@"
  exit $?
fi

# ── coleta: só a lista fixa, só leitura, alvo explícito ──────────────────
command -v supabase >/dev/null 2>&1 || erro "o Supabase CLI não está no PATH." \
  "use o MCP (get_advisors e as consultas de CONSULTAS_DIAGNOSTICO.md) com o --ler, ou o roteiro do painel; nada foi executado."
ver="$(supabase --version 2>/dev/null | sed -n 's/^[^0-9]*\([0-9][0-9]*\)\.\([0-9][0-9]*\).*/\1 \2/p' | head -n 1)"
case "$ver" in
  "") erro "não reconheci a versão do CLI (supabase --version)." "atualize o Supabase CLI e rode de novo; nada foi lido do banco." ;;
  [3-9]\ *|[1-9][0-9]\ *) alvo="--remote" ;;   # 3.x: o padrão virou o banco local; o projeto no ar é --remote
  *) alvo="--linked" ;;
esac
maior="${ver%% *}"; menor="${ver#* }"
# molde explícito: o mktemp -d do macOS ignora o TMPDIR sem ele, e a guarda abaixo valeria só em outros sistemas
pasta="$(mktemp -d "${TMPDIR:-/tmp}/sdd-desempenho.XXXXXX" 2>/dev/null)" || erro "não consegui criar a pasta temporária." "confira o espaço em disco; nada foi lido do banco."
raiz="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
case "$(cd "$pasta" && pwd -P)/" in
  "$(cd "$raiz" && pwd -P)/"*) rmdir "$pasta" 2>/dev/null
     erro "a pasta temporária ($pasta) fica dentro do projeto." "aponte TMPDIR para fora do projeto e rode de novo; nada foi lido do banco." ;;
esac

ok=0
if [ "$maior" -gt 2 ] || { [ "$maior" -eq 2 ] && [ "$menor" -ge 81 ]; }; then
  if supabase db advisors --type performance --level info "$alvo" >"$pasta/advisors.json" 2>"$pasta/_advisors.err"; then ok=$((ok + 1)); else rm -f "$pasta/advisors.json"; echo advisors >>"$pasta/_falhou.txt"; fi
else
  echo "ℹ️ CLI anterior à 2.81: os advisors ficam de fora (use o MCP ou o painel para eles)."
fi
for s in db-stats index-stats table-stats outliers calls long-running-queries blocking locks bloat vacuum-stats role-stats; do
  if supabase inspect db "$s" "$alvo" --output-format json >"$pasta/$s.json" 2>"$pasta/_$s.err"; then
    ok=$((ok + 1))
  else
    rm -f "$pasta/$s.json"
    if supabase inspect db "$s" "$alvo" >"$pasta/$s.txt" 2>>"$pasta/_$s.err"; then ok=$((ok + 1)); else rm -f "$pasta/$s.txt"; echo "$s" >>"$pasta/_falhou.txt"; fi
  fi
done
if [ "$ok" -eq 0 ]; then
  causa="$(cat "$pasta"/_*.err 2>/dev/null | sed -n '/[^[:space:]]/{p;q;}')"
  erro "nenhum comando do CLI leu o banco (${causa:-sem mensagem})." \
    "confira se o projeto está ligado (supabase link) e se o CLI está logado (supabase login); a saída ficou em $pasta."
fi
resto=()
for a in "$@"; do case "$a" in --coletar|--consentimento) ;; *) resto+=("$a") ;; esac; done
nucleo | python3 -B - interpretar --ler "$pasta" --fontes "$pasta" ${resto[@]+"${resto[@]}"}
exit $?
