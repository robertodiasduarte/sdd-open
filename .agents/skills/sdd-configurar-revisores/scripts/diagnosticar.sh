#!/usr/bin/env bash
# diagnosticar.sh — o estado da revisão adversarial neste computador, para a skill sdd-configurar-revisores.
#
# USO-INICIO
#   bash diagnosticar.sh                      só lê: slots, git config, chave (existência), perfil, CLIs, tabelas
#   bash diagnosticar.sh --testar             o mesmo e, com a chave no ambiente, 2 consultas de leitura ao
#                                             OpenRouter (a chave e a lista pública de modelos), 10 s cada
#   bash diagnosticar.sh --gravar <revisor> <auditor>
#                                             grava git config --local sdd.revisor1 e sdd.auditor (nunca a chave)
#   bash diagnosticar.sh --marcar-reabertura  grava git config --local sdd.revisores.reabrir <data> (na parada)
#   bash diagnosticar.sh --estados            lista os estados que este script emite (id, nome, classe)
#   Saída: ESTADO: Rnn NOME · aluno: <frase> · passo: <próximo passo> · medidas · RESULTADO: · →
#   Exit: 0 PRONTO / CHAVE ACEITA / GRAVADO · 10 ESCOLHA · 20 PARADA · 30 CONSERTO · 40 TESTE FALHOU · 64 PAROU
# USO-FIM
#
# Segredo: a chave do OpenRouter só é lida dentro do Python, de os.environ, para o cabeçalho da consulta; nunca é
# impressa, gravada ou passada em argumento. O perfil do terminal é conferido com grep -q (só o código de saída).
# Da resposta do OpenRouter só se leem 4 campos (limit, limit_remaining, usage, is_free_tier) e os ids dos modelos;
# nenhum texto dela é impresso. Valores em dólar em decimal, truncados em centavos (G09).
# Só nos testes: SDD_REVISORES_OPENROUTER_URL (base da API), SDD_REVISORES_SISTEMA (windows), SDD_REVISORES_REG.
# ⚠️ bash 3.2 · núcleo em Python 3.9 stdlib.

set -u
case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

_raiz="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -n "${_raiz}" ] && [ -f "${_raiz}/sdd/bin/lib/python.sh" ]; then . "${_raiz}/sdd/bin/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi
if ! sdd_python_pronto; then
  echo "🛑 diagnosticar: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e peça de novo.\n' >&2
  exit 64
fi
export SDD_REVISORES_BASH="${BASH:-bash}"

exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import datetime, json, os, re, subprocess, sys, threading, time, urllib.error, urllib.request
from decimal import Decimal, ROUND_DOWN, ROUND_UP, InvalidOperation

BASH = os.environ.get("SDD_REVISORES_BASH") or "bash"
BASE_API = (os.environ.get("SDD_REVISORES_OPENROUTER_URL") or "https://openrouter.ai/api/v1").rstrip("/")
TETO_S = 10
CLASSE = {0: "PRONTO", 10: "ESCOLHA", 20: "PARADA", 30: "CONSERTO", 40: "TESTE FALHOU", 64: "PAROU"}

# id: (nome, exit, frase do aluno, próximo passo). A tabela do SKILL.md tem uma linha por id (teste de paridade).
ESTADOS = {
    "R01": ("SEM_REVISAO", 64,
            "Esta pasta não é um projeto com a revisão adversarial do SDD Open (falta sdd/bin/adversarial-review.sh, "
            "ou não é um repositório git): não há revisores para configurar aqui.",
            "Abra o agente na pasta do projeto; se o SDD Open não está instalado, rode o init dele (guia do aluno, "
            "seção 2)."),
    "R02": ("PRONTO", 0,
            "Os revisores estão configurados e as engines estão disponíveis neste computador.",
            "Nada a fazer: o plano da revisão aparece com adversarial-review.sh --dry-run."),
    "R03": ("VAZIO_COM_CLIS", 10,
            "Ainda não há revisor nem auditor, e este computador já tem {n} agentes de IA instalados ({clis}); "
            "servem se estiverem logados e com cota.",
            "Escolha: usar os que você já tem (sem custo extra), o OpenRouter (pago por uso), ou uma engine só."),
    "R04": ("VAZIO_SEM_CHAVE", 10,
            "Ainda não há revisor nem auditor, e este computador tem {n} agente(s) de IA para isso ({clis}): o "
            "caminho é o OpenRouter, um serviço pago por uso que dá acesso a vários modelos de IA.",
            "Escolha: OpenRouter (passo a passo, uns 10 minutos), uma engine só, ou agora não."),
    "R05": ("CHAVE_NO_PERFIL", 20,
            "A chave do OpenRouter está gravada em {perfil}, mas este agente foi aberto antes dela e ainda não a "
            "enxerga.",
            "Feche e abra o agente (e o editor, se o agente roda dentro dele); depois peça de novo."),
    "R06": ("REABRIU_SEM_CHAVE", 20,
            "A chave está gravada em {perfil}, mas continua fora deste agente mesmo depois da parada para reabrir.",
            "Abra um terminal novo, entre na pasta do projeto e abra o agente por ali (não pelo ícone); no Windows, "
            "saia da sua conta e entre de novo. Depois peça de novo."),
    "R07": ("CHAVE_SEM_SLOTS", 10,
            "A chave do OpenRouter chegou a este agente; falta escolher os dois modelos.",
            "Veja o par sugerido, o preço e o que sai do computador, e diga se posso gravar."),
    "R08": ("SLOTS_SEM_CHAVE", 20,
            "A revisão deste projeto usa o OpenRouter ({ids}), e a chave dele não está neste agente.",
            "Siga só os passos da chave (criar com limite de gasto e guardar); os modelos já estão escolhidos."),
    "R09": ("CLI_AUSENTE", 20,
            "A engine {id}, escolhida para {papel}, não está instalada neste computador.",
            "{troca}"),
    "R10": ("UM_SLOT", 10,
            "Falta o {falta}: o {tem} já é {id}.",
            "Escolha o {falta}; precisa ser outra engine ou outro modelo."),
    "R11": ("MESMA_ENGINE", 30,
            "Revisor e auditor são a mesma engine ({id}): ninguém audita a própria revisão.",
            "Escolha outro modelo ou outra engine para auditar."),
    "R12": ("ID_DESCONHECIDO", 30,
            "O nome {id} ({origem}) não está na lista de engines do projeto.",
            "Troque por um destes: {ordem}, ou openrouter:<modelo>."),
    "R13": ("CHAVE_ACEITA", 0,
            "O OpenRouter aceitou a chave: limite de US$ {limite}, restam US$ {resta}.",
            "{seguir}"),
    "R14": ("SEM_LIMITE", 0,
            "O OpenRouter aceitou a chave, mas ela não tem limite de gasto: um erro pode gastar mais que o previsto.",
            "Ponha um limite na chave, na página de chaves do OpenRouter, e siga. {seguir}"),
    "R15": ("CHAVE_RECUSADA", 40,
            "O OpenRouter recusou esta chave: ela foi copiada pela metade, apagada ou revogada ({codigo}).",
            "Crie outra chave e guarde de novo; nada foi gravado no projeto."),
    "R16": ("SEM_CREDITO", 40,
            "A conta do OpenRouter ainda não tem crédito: a revisão pararia na primeira chamada.",
            "Ponha crédito na página de créditos do OpenRouter e peça de novo; nada foi gravado."),
    "R17": ("LIMITE_ESGOTADO", 40,
            "O limite de gasto desta chave acabou (restam US$ {resta}).",
            "Aumente o limite da chave, ou crie outra, e peça de novo; nada foi gravado."),
    "R18": ("MUITAS_CHAMADAS", 40,
            "O OpenRouter pediu para esperar: muitas chamadas agora (429).",
            "Espere 1 minuto e peça de novo; nada foi gravado."),
    "R19": ("SEM_INTERNET", 40,
            "Não consegui falar com o OpenRouter em %d segundos: sem internet ou rede bloqueada." % TETO_S,
            "Confira a internet e peça de novo; nada foi gravado."),
    "R20": ("SERVICO_FORA", 40,
            "O OpenRouter respondeu com um erro do lado dele, ou com uma resposta que não reconheço.",
            "Tente de novo em alguns minutos; nada foi gravado."),
    "R21": ("MODELO_INEXISTENTE", 40,
            "O modelo {modelo} não está na lista pública do OpenRouter.",
            "Atualize o SDD Open (upgrade), ou diga outro modelo (o preço fica desconhecido no relatório); nada foi "
            "gravado."),
}

medidas = []


def sai(rc_estado, extra=None, rc=None):
    nome, codigo, aluno, passo = ESTADOS[rc_estado]
    v = dict(extra or {})
    print("ESTADO: %s %s" % (rc_estado, nome))
    print("aluno: " + aluno.format(**v))
    print("passo: " + passo.format(**v).strip())
    for m in medidas:
        print(m)
    codigo = codigo if rc is None else rc
    palavra = CLASSE[codigo]
    if rc_estado in ("R13", "R14"):
        palavra = "CHAVE ACEITA"
    print("RESULTADO: " + palavra)
    print("→ repasse ao aluno a frase e o passo acima; nunca o id do estado.")
    sys.exit(codigo)


def parou(motivo, seta):
    print("🛑 diagnosticar: " + motivo)
    print("RESULTADO: PAROU")
    print("→ " + seta)
    sys.exit(64)


def git(*a):
    r = subprocess.run(["git"] + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout.strip()


def ler(caminho):
    try:
        with open(caminho, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


def slot(caminho, bloco, chave):
    """O MESMO leitor do adversarial-review.sh (um teste compara os dois): valor de bloco.chave num YAML de 1 nível."""
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


# ── argumentos ──────────────────────────────────────────────────────────────────────────────────
args = sys.argv[1:]
modo = "diagnostico"
gravar = None
if args == ["--estados"]:
    for k in sorted(ESTADOS):
        print("%s %s %d" % (k, ESTADOS[k][0], ESTADOS[k][1]))
    sys.exit(0)
if args == ["--testar"]:
    modo = "testar"
elif args == ["--marcar-reabertura"]:
    modo = "marcar"
elif len(args) == 3 and args[0] == "--gravar":
    modo, gravar = "gravar", (args[1].strip(), args[2].strip())
elif args:
    parou("uso: " + " ".join(args), "rode diagnosticar.sh --help para ver o uso.")

rc, raiz = git("rev-parse", "--show-toplevel")
if rc != 0 or not raiz or not os.path.isfile(os.path.join(raiz, "sdd/bin/adversarial-review.sh")):
    sai("R01")
cfg = os.path.join(raiz, "sdd/config.yaml")
reg_rel = slot(cfg, "review", "registry") or "sdd/review/registry.tsv"
registry = reg_rel if os.path.isabs(reg_rel) else os.path.join(raiz, reg_rel)
texto_reg = ler(registry)
if texto_reg is None:
    parou("a lista de engines (%s) não existe ou não abre" % reg_rel,
          "rode o init do SDD Open neste projeto: ele completa o que falta em sdd/.")
REG, ORDEM = {}, []
for ln in texto_reg.splitlines():
    if not ln.strip() or ln.lstrip().startswith("#"):
        continue
    c = [x.strip() for x in ln.split("\t")]
    if len(c) == 9:
        REG[c[0]] = {"engine": c[0], "adapter": c[1], "modelo": c[2], "cobranca": c[3]}
        ORDEM.append(c[0])
ADAPTERS = os.path.join(raiz, "sdd/bin/adapters")

PRECOS = {}
for ln in (ler(os.path.join(os.path.dirname(registry), "precos.tsv")) or "").splitlines():
    if not ln.strip() or ln.lstrip().startswith("#"):
        continue
    c = [x.strip() for x in ln.split("\t")]
    if len(c) == 6:
        try:
            PRECOS[(c[0], c[1])] = (Decimal(c[2]), Decimal(c[3]), c[5])
        except InvalidOperation:
            pass


def resolve(id_):
    base, _, modelo = id_.partition(":")
    if base not in REG:
        return None
    d = dict(REG[base])
    d["id"] = id_
    if modelo:
        d["modelo"] = modelo
    return d


def ident(d):
    return (d["adapter"], d["modelo"])


def disponivel(d):
    r = subprocess.run([BASH, "-c", 'source "$1"; adapter_disponivel "$2"', "_",
                        os.path.join(ADAPTERS, d["adapter"] + ".sh"), d["modelo"]],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return r.returncode == 0


def ler_lista(chave):
    """(ids, origem): o slot do sdd/config.yaml (escolha do time), senão o git config deste computador."""
    v, origem = slot(cfg, "review", chave) or "", "sdd/config.yaml"
    if not v.strip():
        v = git("-C", raiz, "config", "--get", "sdd." + chave)[1]
        origem = "este computador (git config sdd.%s)" % chave if v else "-"
    return [x.strip() for x in v.split(",") if x.strip()], origem


def centavos(v):
    return v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def br(v):
    return str(v).replace(".", ",")


PERFIS = (".zshrc", ".zprofile", ".zshenv", ".zshrc.local", ".bashrc", ".bash_profile", ".bash_login", ".profile",
          ".bashrc.local")


PERFIS_DO_SHELL = {"zsh": (".zshrc", ".zprofile", ".zshenv", ".zshrc.local"),
                   "bash": (".bashrc", ".bash_profile", ".bash_login", ".profile", ".bashrc.local")}
OUTROS = []


def perfil_com_chave():
    """Onde a chave está gravada, sem ler o valor: o nome do arquivo do perfil, 'variáveis do Windows' ou None."""
    padrao = re.compile(r"^[ \t]*(export[ \t]+)?OPENROUTER_API_KEY=")
    casa = os.environ.get("HOME") or os.path.expanduser("~")
    shell = os.path.basename(os.environ.get("SHELL") or "")
    lidos = PERFIS_DO_SHELL.get(shell, PERFIS)   # só o que o shell do aluno lê: uma chave noutro perfil não chega
    for nome in PERFIS:
        t = ler(os.path.join(casa, nome))
        if t and any(padrao.match(ln) for ln in t.splitlines()):
            if nome in lidos:
                return "~/" + nome
            OUTROS.append("~/" + nome)
    sistema = os.environ.get("SDD_REVISORES_SISTEMA") or ("windows" if os.name == "nt" or
                                                          re.match(r"(MINGW|MSYS|CYGWIN)", os.environ.get("MSYSTEM", "") or "")
                                                          else "")
    if sistema == "windows":
        reg = os.environ.get("SDD_REVISORES_REG") or "reg"
        env = dict(os.environ, MSYS2_ARG_CONV_EXCL="*", MSYS_NO_PATHCONV="1")
        try:
            r = subprocess.run([reg, "query", "HKCU\\Environment", "/v", "OPENROUTER_API_KEY"], env=env,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if r.returncode == 0:
                return "variáveis de ambiente do Windows"
        except OSError:
            pass
    return None


# ── gravar e marcar ─────────────────────────────────────────────────────────────────────────────
if modo == "marcar":
    if git("-C", raiz, "config", "--local", "sdd.revisores.reabrir", datetime.date.today().isoformat())[0] != 0:
        parou("não consegui gravar a marca da parada no git config", "siga sem a marca: a skill pergunta na volta.")
    print("MARCADO: parada para reabrir o agente (git config sdd.revisores.reabrir)")
    print("RESULTADO: MARCADO\n→ mostre a parada ao aluno.")
    sys.exit(0)

if modo == "gravar":
    r, a = gravar
    for id_, origem in ((r, "revisor pedido"), (a, "auditor pedido")):
        if not id_ or resolve(id_) is None:
            sai("R12", {"id": id_ or "(vazio)", "origem": origem, "ordem": ", ".join(ORDEM)})
    if ident(resolve(r)) == ident(resolve(a)):
        sai("R11", {"id": r})
    for chave, v in (("revisor1", r), ("auditor", a)):
        if git("-C", raiz, "config", "--local", "sdd." + chave, v)[0] != 0:
            print("🛑 não consegui gravar sdd.%s no git config deste computador." % chave)
            print("RESULTADO: CONSERTO")
            print("→ à mão, na pasta do projeto: git config --local sdd.%s '%s'" % (chave, v))
            sys.exit(30)
    git("-C", raiz, "config", "--local", "--unset", "sdd.revisores.reabrir")
    lidos = (git("-C", raiz, "config", "--get", "sdd.revisor1")[1], git("-C", raiz, "config", "--get", "sdd.auditor")[1])
    print("GRAVADO: revisor %s · auditor %s (git config deste computador, lidos de volta)" % lidos)
    for chave in ("revisor1", "auditor"):
        if (slot(cfg, "review", chave) or "").strip():
            print("⚠️ o sdd/config.yaml do projeto já escolhe review.%s, e ele vence o que gravei aqui." % chave)
    print("RESULTADO: GRAVADO\n→ siga para a prova: diagnosticar.sh --testar e adversarial-review.sh --dry-run.")
    sys.exit(0 if lidos == (r, a) else 30)

# ── estado ──────────────────────────────────────────────────────────────────────────────────────
rev, origem_rev = ler_lista("revisor1")
aud, origem_aud = ler_lista("auditor")
chave_ok = bool(os.environ.get("OPENROUTER_API_KEY"))
perfil = None if chave_ok else perfil_com_chave()
clis = [e for e in ORDEM if REG[e]["adapter"] != "openrouter" and disponivel(dict(REG[e], id=e))]
usa_or = any((x.split(":", 1)[0] in REG and REG[x.split(":", 1)[0]]["adapter"] == "openrouter") for x in rev + aud)
vazios = not rev and not aud

medidas.append("revisor: %s (origem: %s)" % (", ".join(rev) or "—", origem_rev))
medidas.append("auditor: %s (origem: %s)" % (", ".join(aud) or "—", origem_aud))
medidas.append("chave do OpenRouter neste agente: " + ("presente" if chave_ok else "ausente"))
if not chave_ok:
    medidas.append("chave gravada no perfil: " + (perfil or "não achei"))
    for o in OUTROS:
        medidas.append("⚠️ há uma linha da chave em %s, que o seu shell não lê: grave de novo pelo guardar-chave.sh" % o)
medidas.append("agentes de IA disponíveis: " + (", ".join(clis) or "nenhum"))


def par_sugerido():
    """(revisor, auditor) do OpenRouter: o modelo do registry e o 1º outro modelo openrouter do precos.tsv."""
    linha = next((REG[e] for e in ORDEM if REG[e]["adapter"] == "openrouter"), None)
    if not linha:
        return None
    a = linha["modelo"]
    b = next((m for (e, m) in PRECOS if e == linha["engine"] and m != a), None)
    return (linha["engine"] + ":" + a, linha["engine"] + ":" + b) if b else None


def mede_par(par, rotulo="par sugerido"):
    """Preço e estimativa de (revisor, auditor) do OpenRouter; um papel None (engine que não é do OpenRouter) não
    entra na conta. Com os slots no OpenRouter, mede o par configurado, não o sugerido (avaliador, achado 2)."""
    if not par:
        medidas.append("par sugerido: o pacote não tem dois modelos do OpenRouter com preço (diga o seu modelo)")
        return
    medidas.append("%s: revisor %s · auditor %s" % (rotulo, par[0] or "(fora do OpenRouter)",
                                                     par[1] or "(fora do OpenRouter)"))
    kb = slot(cfg, "review", "context_max_kb") or "180"
    try:
        kb = Decimal(int(kb))
    except ValueError:
        kb = Decimal(180)
    ent_r = (kb + 60) * 1024 / 4
    contas, datas, total = [], set(), Decimal(0)
    for id_, ent, sai_ in ((par[0], ent_r, Decimal(8000)), (par[1], ent_r + 8000, Decimal(4000))):
        if not id_:
            continue
        d = resolve(id_)
        e, m = d["engine"], d["modelo"]
        p = PRECOS.get((e, m))
        if not p:
            contas.append("%s: preço desconhecido" % m)
            total = None
            continue
        contas.append("%s: US$ %s / %s" % (m, br(p[0]), br(p[1])))
        datas.add(p[2])
        if total is not None:
            total += (ent * p[0] + sai_ * p[1]) / Decimal(1000000)
    medidas.append("preço por milhão de tokens (entrada / saída): %s (sdd/review/precos.tsv, conferido em %s)"
                   % ("; ".join(contas), ", ".join(sorted(datas)) or "—"))
    if total is not None:
        teto = total.quantize(Decimal("0.01"), rounding=ROUND_UP)
        medidas.append("estimativa por revisão: " + ("menos de US$ 0,01" if total < Decimal("0.01") else
                       "até ≈ US$ %s" % br(teto)) + " (no teto do contexto; a maioria custa menos)")


def do_openrouter(ids):
    d = resolve(ids[0]) if ids else None
    return ids[0] if d and d["adapter"] == "openrouter" else None


if usa_or:
    mede_par((do_openrouter(rev), do_openrouter(aud)), "par configurado")
elif vazios:
    mede_par(par_sugerido())

# ordem de precedência (DESIGN, Decision 8, com as notas da revisão D1)
for lista_ids, origem in ((rev, origem_rev), (aud, origem_aud)):
    for x in lista_ids:
        if resolve(x) is None:
            sai("R12", {"id": x, "origem": origem, "ordem": ", ".join(ORDEM)})
if rev and aud and ident(resolve(rev[0])) == ident(resolve(aud[0])):
    sai("R11", {"id": rev[0]})
if not chave_ok and perfil and (vazios or usa_or or not (rev and aud)):
    marca = git("-C", raiz, "config", "--get", "sdd.revisores.reabrir")[1]
    try:   # a marca vale 1 dia: uma parada antiga, de outra tentativa, não muda a frase de hoje
        recente = (datetime.date.today() - datetime.date.fromisoformat(marca)).days <= 1
    except ValueError:
        recente = False
    sai("R06" if recente else "R05", {"perfil": perfil})
if usa_or and not chave_ok:
    sai("R08", {"ids": ", ".join(x for x in rev + aud if x.startswith("openrouter"))})
if rev or aud:
    if not (rev and aud):
        tem, falta, id_ = ("revisor", "auditor", rev[0]) if rev else ("auditor", "revisor", aud[0])
        sai("R10", {"tem": tem, "falta": falta, "id": id_})
    for papel_, lista_ids, origem in (("revisor", rev, origem_rev), ("auditor", aud, origem_aud)):
        d = resolve(lista_ids[0])
        if d["adapter"] != "openrouter" and not disponivel(d):
            troca = ("Instale a CLI dela; a escolha é do projeto (sdd/config.yaml) e vence a deste computador: para "
                     "trocar, fale com quem cuida do projeto." if origem == "sdd/config.yaml" else
                     "Instale a CLI dela, ou troque a engine pela pergunta da skill (a escolha é deste computador).")
            sai("R09", {"id": d["id"], "papel": papel_, "origem": origem, "troca": troca})
    estado = "R02"
elif len(clis) >= 2:
    estado = "R03"
elif chave_ok:
    estado = "R07"
else:
    estado = "R04"

if modo == "diagnostico" or not chave_ok or (estado == "R02" and not usa_or):
    # revisores só em CLIs: a prova não depende do OpenRouter, e uma chave antiga no ambiente não pode derrubá-la
    sai(estado, {"n": len(clis), "clis": ", ".join(clis) or "nenhum"})

# ── --testar: 2 consultas de leitura ────────────────────────────────────────────────────────────


def consulta(caminho, com_chave):
    """(status, json) com o teto de TETO_S para a chamada inteira: a leitura roda numa thread, e o prazo é do relógio."""
    res = []
    def roda():
        try:
            res.append(_consulta(caminho, com_chave))
        except Exception:                  # http.client.HTTPException e afins: resposta que não reconheço (R20),
            res.append((0, None))          # sem traceback (que poderia trazer texto da resposta)
    t = threading.Thread(target=roda, daemon=True)
    t.start()
    t.join(TETO_S)
    return res[0] if res else (None, None)


class _SemRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None                         # o 3xx sobe como HTTPError e vira R20


SEM_REDIRECT = urllib.request.build_opener(_SemRedirect)


def _consulta(caminho, com_chave):
    h = {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]} if com_chave else {}
    req = urllib.request.Request(BASE_API + caminho, headers=h, method="GET")
    prazo = time.monotonic() + TETO_S        # o teto vale para a chamada inteira, não por operação do socket
    try:
        with SEM_REDIRECT.open(req, timeout=TETO_S) as r:   # 3xx não é seguido: a chave nunca vai a outro endereço
            pedacos = []
            while True:
                if time.monotonic() > prazo:
                    return None, None
                p = r.read1(65536) if hasattr(r, "read1") else r.read(65536)   # o que já chegou, sem esperar 64 KB
                if not p:
                    break
                pedacos.append(p)
            corpo = b"".join(pedacos)
    except urllib.error.HTTPError as e:
        return e.code, None                 # o corpo do erro nunca é lido
    except (OSError, ValueError):
        return None, None                   # rede, teto de tempo
    try:
        return 200, json.loads(corpo.decode("utf-8", "replace"), parse_float=Decimal, parse_int=Decimal)
    except ValueError:
        return 200, "ilegível"


seguir = ("Siga para a prova do plano." if not vazios else "Siga para escolher os modelos e gravar.")
st, j = consulta("/key", True)
if st is None:
    sai("R19")
if st in (401, 403):
    sai("R15", {"codigo": st})
if st == 402:
    sai("R16")
if st == 429:
    sai("R18")
if st != 200 or not isinstance(j, dict) or not isinstance(j.get("data"), dict):
    sai("R20")
d = j["data"]
if d.get("is_free_tier") is True:
    sai("R16")
limite, resta = d.get("limit"), d.get("limit_remaining")
if isinstance(resta, Decimal) and centavos(resta) <= 0:
    sai("R17", {"resta": br(centavos(resta))})
ids_or = [x for x in rev + aud if resolve(x) and resolve(x)["adapter"] == "openrouter"] or list(par_sugerido() or ())
modelos = [resolve(x)["modelo"] for x in ids_or]   # "openrouter" sem :modelo vale o modelo do registry
if modelos:
    st, jm = consulta("/models", False)
    if st is None:
        sai("R19")
    if st == 429:
        sai("R18")
    if st == 402:
        sai("R16")
    if st != 200 or not isinstance(jm, dict) or not isinstance(jm.get("data"), list):
        sai("R20")
    ids = {m.get("id") for m in jm["data"] if isinstance(m, dict)}
    for m in modelos:
        if m not in ids:
            sai("R21", {"modelo": m})
if not isinstance(limite, Decimal):
    sai("R14", {"seguir": seguir})
sai("R13", {"limite": br(centavos(limite)), "resta": br(centavos(resta)) if isinstance(resta, Decimal) else "—",
            "seguir": seguir})
PY
