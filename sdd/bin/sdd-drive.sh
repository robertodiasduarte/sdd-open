#!/usr/bin/env bash
# sdd-drive.sh — leva um DEFINE até "pronto para publicar" e para na barreira. O script decide; quem executa
# cada ação é o agente (skill sdd-drive). Contrato em docs/sdd-drive.md e em sdd/WORKFLOW_CONTRACTS.yaml › sdd_drive.
#
# USO-INICIO
#   sdd-drive.sh iniciar <DEFINE.md> [--max N]        confere, grava o estado e diz a 1ª ação
#   sdd-drive.sh --dry-run <DEFINE.md> [--max N]      simulação: não executa nem grava nada
#   sdd-drive.sh --resume <DEFINE.md> [--max N] [--aceitar-gate-novo]   continua de onde parou
#   sdd-drive.sh proximo <DEFINE.md>                  a próxima ação, recalculada do disco
#   sdd-drive.sh verificar <DEFINE.md> [--fundo]      roda o Verify Gate (só o script roda o que decide); --fundo:
#                                                     destacado do agente, para gate maior que o limite de um comando
#   sdd-drive.sh concluir <DEFINE.md>                 confere gate e relatório; para em gate-verde
#   sdd-drive.sh bloqueio <DEFINE.md> "<motivo>"      a construção travou: para em bloqueio-humano
#   sdd-drive.sh aguardar <DEFINE.md> <papel> <brief> sem subagente: parada de sessão nova (exit 40)
#   sdd-drive.sh recibo <DEFINE.md> "<texto>"         anota uma decisão de rotina no DRIVE_REPORT
#   sdd-drive.sh --self-test
# USO-FIM
#
# Exit: 0 concluído (gate-verde, simulacao) · 10 continuar (ACAO: …) · 20 parada tabelada (motivo: …)
#       40 aguardando-sessao · 2 falha do próprio script · 64 uso.
# Motivos: gate-verde · simulacao · orcamento-rodadas · manual-ux · clarificacao-pendente · define-invalido ·
#          gate-inconclusivo · gate-alterado · bloqueio-humano · aguardando-sessao · estado-invalido · branch-padrao.
# Ações: ESPERAR · DESIGN · REVISAO_DESIGN · RODADA · CORRIGIR · COMMITAR · VERIFICAR · AVALIAR_E_RELATAR.
#
# ⛔ Barreira: este script não tem verbo nem caminho que publique. Publicar é decisão da pessoa, pela sdd-release.
# ⚠️ bash 3.2 (o /bin/bash do macOS) · o núcleo é Python 3.9 stdlib, lido do stdin: todo filho roda com stdin fechado.
#    -I tira a pasta do projeto do sys.path: um json.py do usuário não entra no lugar do módulo.

set -u

BIN="$(cd "$(dirname "$0")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 sdd-drive: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

SDD_DRIVE_BIN="$BIN" SDD_DRIVE_SELF="$0" SDD_DRIVE_BASH="${BASH:-bash}" python3 -I -B - ${1+"$@"} <<'PY'
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except Exception:
        pass

BIN = os.environ.get("SDD_DRIVE_BIN", ".")
SELF = os.environ.get("SDD_DRIVE_SELF", "sdd-drive.sh")
BASH = os.environ.get("SDD_DRIVE_BASH") or "bash"

# nome → (frase para a pessoa, exit, RESULTADO, seta). A tabela é contrato: test_f14_drive_textos a compara com a
# skill, o WORKFLOW_CONTRACTS e o docs/sdd-drive.md.
MOTIVOS = {
    "gate-verde": ("O teste final passou e os relatórios estão prontos. Nada foi publicado.", 0, "CONCLUIDO",
                   "revise os commits e, para publicar, chame a sdd-release; o piloto nunca publica."),
    "simulacao": ("Simulação: nada foi executado nem gravado.", 0, "CONCLUIDO",
                  "para executar de verdade, rode sdd-drive.sh iniciar com este DEFINE."),
    "orcamento-rodadas": ("O teste final continuou vermelho nas rodadas permitidas. Nada foi publicado.", 20, "PARADA",
                          "decida: corrigir o DESIGN e seguir, dar mais rodadas (--resume --max N) ou parar; publicar é só pela sdd-release."),
    "manual-ux": ("O teste final precisa da conferência de uma pessoa. Nada foi publicado.", 20, "PARADA",
                  "percorra o checklist do manual_fallback, assine no BUILD_REPORT e, para publicar, chame a sdd-release."),
    "clarificacao-pendente": ("O DEFINE ainda tem dúvida aberta ou a revisão de governança pendente.", 20, "PARADA",
                              "volte ao Define, resolva e use --resume (ou iniciar, se a execução ainda não começou); nada foi construído por cima da dúvida."),
    "define-invalido": ("O DEFINE não tem um teste final válido.", 20, "PARADA",
                        "corrija o bloco do Verify Gate pelo Define e use --resume (ou iniciar, se a execução ainda não começou)."),
    "gate-inconclusivo": ("O teste final não chegou ao fim: isso não é vermelho e não gastou rodada.", 20, "PARADA",
                          "instale o que faltou (veja o log) ou rode onde a ferramenta exista, e use --resume."),
    "gate-alterado": ("O comando do teste final mudou desde o início desta execução.", 20, "PARADA",
                      "volte o comando antigo ou, se a mudança é certa, aceite com --resume --aceitar-gate-novo; fica escrito no relatório."),
    "bloqueio-humano": ("A construção parou e precisa de você. Nada foi publicado.", 20, "PARADA",
                        "resolva o que está descrito acima e use --resume; o que já ficou pronto continua nos commits."),
    "aguardando-sessao": ("Esta etapa precisa de uma sessão nova do agente. Nada foi publicado.", 40, "AGUARDANDO_HUMANO",
                          "siga os passos acima; na volta, use --resume."),
    "estado-invalido": ("Não consegui ler onde a execução parou, e não vou adivinhar.", 20, "PARADA",
                        "confira o arquivo citado acima: use --resume se ele for desta execução, ou apague-o e rode iniciar."),
    "branch-padrao": ("O piloto não roda na branch principal: ele precisa de uma frente de trabalho própria.", 20, "PARADA",
                      "abra uma frente com a sdd-new-session e rode de novo lá."),
}
ACOES = {
    "ESPERAR": "espere o teste final terminar e chame proximo de novo; nenhuma rodada é gasta por esperar.",
    "DESIGN": "rode a fase Design sobre este DEFINE e chame proximo de novo.",
    "REVISAO_DESIGN": "rode a revisão de contexto fresco do DESIGN, registre no Advisor Ledger e chame proximo.",
    "RODADA": "despache o executor (references/executor.md) só para esta tarefa, em contexto fresco, e chame proximo.",
    "CORRIGIR": "leia o log, corrija o DESIGN ou reabra a tarefa no PROGRESS (- [ ]), commite e chame proximo.",
    "COMMITAR": "commite os arquivos listados e chame proximo; nenhuma rodada foi gasta.",
    "VERIFICAR": "chame sdd-drive.sh verificar: quem roda o teste final é o script.",
    "AVALIAR_E_RELATAR": "rode o avaliador de contexto fresco, grave o BUILD_REPORT e chame concluir.",
}
# Lista explícita, sem faixa: no bash e no Python com locale, [A-Za-z] não pega acento, mas a regra é a mesma do despachar.
LETRAS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
SO_DOCUMENTOS = ("sdd/features/", "sdd/reports/", "sdd/reviews/", "sdd/handoffs/", "sdd/traces/")
EXT_DOCUMENTO = (".md", ".log", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".csv", ".lock")
CAMPOS_ESTADO = ("versao", "feature", "define", "gate_sha", "gate_cmd", "inicio", "maximo", "gates", "trocas_gate", "recibos")
REPETICOES = 3
# A parada que veio do teste final vale até o --resume: com --fundo, quem a mostra é o proximo.
PARADAS_DO_GATE = ("gate-inconclusivo", "manual-ux", "clarificacao-pendente", "define-invalido")
USO = """uso:
  sdd-drive.sh iniciar <DEFINE.md> [--max N]
  sdd-drive.sh --dry-run <DEFINE.md> [--max N]
  sdd-drive.sh --resume <DEFINE.md> [--max N] [--aceitar-gate-novo]
  sdd-drive.sh proximo|concluir <DEFINE.md>
  sdd-drive.sh verificar <DEFINE.md> [--fundo]
  sdd-drive.sh bloqueio|recibo <DEFINE.md> "<texto>"
  sdd-drive.sh aguardar <DEFINE.md> <papel> <brief>
  sdd-drive.sh --self-test"""


def fim(resultado, seta, canal=None):
    canal = canal or sys.stdout
    print("RESULTADO: " + resultado, file=canal)
    print("→ " + seta, file=canal)


def uso(motivo):
    print("🛑 sdd-drive: " + motivo, file=sys.stderr)
    print(USO, file=sys.stderr)
    fim("ERRO DE USO", "corrija a chamada e rode de novo; nada foi lido nem gravado.", sys.stderr)
    sys.exit(64)


def falha(motivo, seta="confira a causa acima e rode de novo; o estado anterior ficou como estava."):
    print("🛑 sdd-drive: " + motivo, file=sys.stderr)
    fim("FALHA", seta, sys.stderr)
    sys.exit(2)


def ler(caminho):
    with open(caminho, encoding="utf-8", errors="replace", newline="") as f:
        return f.read().replace("\r\n", "\n")


def roda(cmd, cwd, teto=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL, timeout=teto)


def git(raiz, *args):
    r = roda(["git", "-C", raiz] + list(args), raiz, 60)
    return r.returncode, r.stdout


def gravar_atomico(caminho, texto):
    pasta = os.path.dirname(caminho)
    try:
        os.makedirs(pasta, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=pasta, prefix=".drive-")
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(texto)
        os.replace(tmp, caminho)
    except OSError as e:
        falha("não consegui gravar %s: %s" % (caminho, e))


# ── o projeto ────────────────────────────────────────────────────────────────────────────────────
class Projeto:
    def __init__(self, define_arg):
        if not define_arg:
            uso("falta o DEFINE")
        cwd = os.getcwd()
        r = roda(["git", "rev-parse", "--show-toplevel"], cwd)
        if r.returncode != 0 or not r.stdout.strip():
            uso("este comando precisa de um repositório git")
        self.raiz = os.path.realpath(r.stdout.strip())
        nome = os.path.basename(define_arg)
        if not (nome.startswith("DEFINE_") and nome.endswith(".md")):
            uso("o DEFINE precisa se chamar DEFINE_<FEATURE>.md: " + define_arg)
        self.feature = nome[len("DEFINE_"):-len(".md")]
        if not self.feature or any(c not in LETRAS for c in self.feature):
            uso("FEATURE inválida: '%s' (letras, números, - e _)" % self.feature)
        abso = os.path.realpath(os.path.join(cwd, define_arg))
        if not (abso + os.sep).startswith(self.raiz + os.sep):
            uso("o DEFINE precisa estar dentro do repositório: " + define_arg)
        self.abs = abso
        self.define = os.path.relpath(abso, self.raiz).replace(os.sep, "/")
        self.pasta_doc = os.path.dirname(self.define)
        self.design = (self.pasta_doc + "/" if self.pasta_doc else "") + "DESIGN_%s.md" % self.feature
        self.progress = "sdd/reports/progress/PROGRESS_%s.md" % self.feature
        self.estado = "sdd/reports/progress/DRIVE_%s.json" % self.feature
        self.relatorio = "sdd/reports/DRIVE_REPORT_%s.md" % self.feature
        self.build_report = "sdd/reports/BUILD_REPORT_%s.md" % self.feature
        confere_dentro(self)

    def p(self, rel):
        return os.path.join(self.raiz, rel)

    def head(self):
        rc, out = git(self.raiz, "rev-parse", "HEAD")
        return out.strip() if rc == 0 else ""

    def slot(self, bloco, chave):
        """Valor de bloco.chave no sdd/config.yaml; None se o arquivo ou a chave não existem."""
        caminho = self.p("sdd/config.yaml")
        if not os.path.isfile(caminho):
            return None
        dentro = False
        for ln in ler(caminho).splitlines():
            if ln and not ln[0].isspace() and not ln.startswith("#"):
                dentro = ln.split("#", 1)[0].strip() == bloco + ":"
                continue
            m = re.match(r"^\s+" + re.escape(chave) + r":\s*(.*)$", ln) if dentro else None
            if m:
                return m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
        return None


def script_gate(p):
    return os.path.join(BIN, "verify-gate.sh")


def confere_vizinhos():
    """O init não troca script que já existe: numa atualização, este pode chegar ao lado de vizinhos velhos."""
    for arq, marca in (("verify-gate.sh", "--checar"), ("sdd-fluxo.sh", "--drive")):
        caminho = os.path.join(BIN, arq)
        if not os.path.isfile(caminho) or marca not in ler(caminho):
            falha("sdd/bin/%s é de uma versão anterior: não conhece %s." % (arq, marca),
                  "atualize sdd/bin/: rode o doctor e, para o que ele apontar, apague e rode o init.")


def impressao_digital(p):
    """(rc, sha, cmd) a partir do mesmo parser do gate: as linhas que o --print mostra."""
    rc, sha, cmd, _linhas = bloco_do_gate(p)
    return rc, sha, cmd


def bloco_do_gate(p):
    r = roda([BASH, script_gate(p), "--print", p.define], p.raiz)
    if r.returncode != 0:
        return r.returncode, "", "", []
    linhas = [ln for ln in r.stdout.split("\n") if re.match(r"^(kind|cmd|pass_when|threshold|manual_fallback):", ln)]
    cmd = next((ln.split(":", 1)[1].strip() for ln in linhas if ln.startswith("cmd:")), "")
    return 0, hashlib.sha256("\n".join(linhas).encode("utf-8")).hexdigest(), cmd, linhas


def checar(p):
    return roda([BASH, script_gate(p), "--checar", p.define], p.raiz).returncode


def limite(p, valor_flag):
    if valor_flag is not None:
        origem, valor = "--max", valor_flag
    else:
        valor = p.slot("drive", "max_rounds")
        origem = "drive.max_rounds em sdd/config.yaml"
        if valor is None or valor == "":
            return 3
    if not re.match(r"^[0-9]+$", valor) or int(valor) < 1:
        uso("%s precisa ser um inteiro a partir de 1: '%s'" % (origem, valor))
    return int(valor)


# ── estado ───────────────────────────────────────────────────────────────────────────────────────
def inteiro(v):
    return isinstance(v, int) and not isinstance(v, bool)


def forma_ok(st):
    """A forma inteira: estado que abre mas não fecha viraria traceback ou rodada contada errado adiante."""
    if not isinstance(st, dict) or any(k not in st for k in CAMPOS_ESTADO):
        return False
    if st["versao"] != 2 or not all(isinstance(st[k], str) for k in ("feature", "define", "gate_sha", "gate_cmd", "inicio")) \
            or not inteiro(st["maximo"]) or st["maximo"] < 1:
        return False
    if not isinstance(st.get("motivo", ""), str) or not isinstance(st.get("parada_gate", ""), str):
        return False
    if st.get("motivo", "") not in MOTIVOS and st.get("motivo", "") != "":
        return False
    if st.get("parada_gate", "") not in PARADAS_DO_GATE and st.get("parada_gate", "") != "":
        return False
    linhas = st.get("gate_linhas", [])
    if not isinstance(st.get("detalhe", ""), str) or not isinstance(linhas, list) or not all(isinstance(x, str) for x in linhas):
        return False
    if not (isinstance(st["gates"], list) and isinstance(st["trocas_gate"], list) and isinstance(st["recibos"], list)):
        return False
    for g in st["gates"]:
        if not isinstance(g, dict) or not all(inteiro(g.get(k)) for k in ("n", "rodada", "exit")) \
                or not all(isinstance(g.get(k), str) for k in ("commit", "log", "impressao")) \
                or not re.match(r"^[0-9a-f]{7,64}$", g["commit"]):
            return False
    for t in st["trocas_gate"]:
        if not isinstance(t, dict) or not all(isinstance(t.get(k), str) for k in ("de", "para", "data")) \
                or not isinstance(t.get("campos", []), list) or not all(isinstance(c, str) for c in t.get("campos", [])):
            return False
    if not all(isinstance(r, str) for r in st["recibos"]):
        return False
    rep = st.get("repeticao", dict(chave="", n=0))
    return isinstance(rep, dict) and isinstance(rep.get("chave"), str) and inteiro(rep.get("n"))


def confere_dentro(p):
    """Link que sai do repositório levaria estado, relatório e log para fora: recusa antes de gravar qualquer coisa."""
    for rel in ("sdd/reports", "sdd/reports/progress", "sdd/reports/evidence", "sdd/reports/evidence/" + p.feature):
        alvo = os.path.realpath(p.p(rel))
        if not (alvo + os.sep).startswith(p.raiz + os.sep):
            falha("%s aponta para fora do repositório (%s)." % (rel, alvo), "troque o link por uma pasta do projeto e rode de novo.")


_ESTADO_PEGO = None
ESPERA_ESTADO = 70
ESTADO_ABANDONADO = 60


def segura_estado(p):
    """Um verbo por vez lê-altera-grava: sem isto, um recibo gravado com uma cópia antiga apagaria o gate que terminou
    no meio. É curta (nunca durante o gate); a de um processo morto vence em ESTADO_ABANDONADO segundos."""
    global _ESTADO_PEGO
    if _ESTADO_PEGO:
        return
    caminho = p.p("sdd/reports/progress/DRIVE_%s.estado.lock" % p.feature)
    limite_espera = time.time() + ESPERA_ESTADO
    while True:
        try:
            os.makedirs(os.path.dirname(caminho), exist_ok=True)
            os.close(os.open(caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644))
            _ESTADO_PEGO = caminho
            return
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(caminho) > ESTADO_ABANDONADO:
                    os.remove(caminho)
                    continue
            except OSError:
                continue
        except OSError as e:
            falha("não consegui gravar %s: %s" % (caminho, e))
        if time.time() > limite_espera:
            falha("outro comando do drive está com o estado há mais de %d s." % ESPERA_ESTADO,
                  "espere e rode de novo; se não houver nenhum rodando, apague %s." % os.path.relpath(caminho, p.raiz))
        time.sleep(0.05)


def larga_estado():
    global _ESTADO_PEGO
    if _ESTADO_PEGO:
        try:
            os.remove(_ESTADO_PEGO)
        except OSError:
            pass
        _ESTADO_PEGO = None


def le_estado(p):
    """(estado, defeito). estado None quando não dá para confiar no arquivo."""
    caminho = p.p(p.estado)
    if not os.path.isfile(caminho):
        return None, "não há estado em %s" % p.estado
    try:
        st = json.loads(ler(caminho))
    except ValueError as e:
        return None, "%s não é um JSON legível: %s" % (p.estado, e)
    if not forma_ok(st):
        return None, "%s não tem os campos esperados" % p.estado
    if st["define"] != p.define or st["feature"] != p.feature:
        return None, "%s é de outro DEFINE (%s)" % (p.estado, st["define"])
    return st, ""


def grava_estado(p, st):
    gravar_atomico(p.p(p.estado), json.dumps(st, ensure_ascii=False, indent=1) + "\n")


def vermelhos(st):
    return sum(1 for g in st["gates"] if g["exit"] == 2)


def ultimo_valido(p, st):
    """O último gate, se foi rodado com a impressão digital atual e o log confirma o exit: gate de outro comando, ou
    linha de estado sem o log dela, não prova nada. Isso barra edição descuidada; forja deliberada é limite declarado."""
    if not st["gates"] or st["gates"][-1].get("impressao") != st["gate_sha"]:
        return None
    g = st["gates"][-1]
    try:
        confirma = ler(p.p(g["log"])).rstrip("\n").split("\n")[-1] == "[exit=%d]" % g["exit"]
    except OSError:
        return None
    return g if confirma else None


def rodada_atual(st):
    return min(vermelhos(st) + 1, st["maximo"])


def relatorio(p, st, motivo, extra=""):
    usadas = vermelhos(st)
    if motivo:
        frase = MOTIVOS[motivo][0]
    else:
        frase = "Execução em andamento. Nada foi publicado."
    lin = ["# DRIVE_REPORT: " + st["feature"], "",
           "%s Rodadas vermelhas: %d de %d." % (frase, usadas, st["maximo"]), "",
           "| Campo | Valor |", "|---|---|",
           "| Motivo | %s |" % (motivo or "em andamento"),
           "| DEFINE | `%s` |" % st["define"],
           "| Commit inicial | `%s` |" % st["inicio"][:12],
           "| Teste final | `%s` |" % st["gate_cmd"].replace("|", "\\|")]
    extra = extra or st.get("detalhe") or ""
    if extra:
        lin += ["", extra]
    lin += ["", "## Testes finais", "", "| # | Rodada | Commit | Exit | Log |", "|---|---|---|---|---|"]
    for g in st["gates"]:
        lin.append("| %d | %d | `%s` | %d | `%s` |" % (g["n"], g["rodada"], g["commit"][:12], g["exit"], g["log"]))
    if not st["gates"]:
        lin.append("| — | — | — | — | nenhum teste final rodou |")
    rc, out = git(p.raiz, "log", "--format=%h %s", st["inicio"] + "..HEAD") if st["inicio"] else (1, "")
    lin += ["", "## Commits desde o início", ""]
    lin += ["- " + c for c in out.splitlines()] if rc == 0 and out.strip() else ["Nenhum."]
    lin += ["", "## Teste final alterado", ""]
    lin += ["- de `%s` para `%s`, aceito em %s; agora: %s" % (t["de"], t["para"], t["data"], " · ".join(" ".join(c.split()) for c in t.get("campos") or []))
            for t in st["trocas_gate"]] or ["Nenhuma troca."]
    lin += ["", "## Decidi sozinho", ""]
    lin += ["- " + t for t in st["recibos"]] or ["Nada."]
    lin += ["", "Nada foi publicado: publicar é decisão da pessoa, pela sdd-release.", ""]
    gravar_atomico(p.p(p.relatorio), "\n".join(lin))


def parada(p, st, motivo, extra=""):
    if st is not None:
        st["motivo"], st["detalhe"] = motivo, extra
        grava_estado(p, st)
        relatorio(p, st, motivo, extra)
    print("motivo: " + motivo)
    print(MOTIVOS[motivo][0])
    if extra:
        print(extra)
    fim(MOTIVOS[motivo][2], MOTIVOS[motivo][3])
    sys.exit(MOTIVOS[motivo][1])


def acao(p, st, nome, detalhe=""):
    print("ACAO: " + nome)
    print("rodada: %d/%d" % (rodada_atual(st), st["maximo"]))
    if detalhe:
        print(detalhe)
    fim("CONTINUAR", ACOES[nome])
    sys.exit(10)


def carrega(p):
    segura_estado(p)
    st, defeito = le_estado(p)
    if st is None:
        parada(p, None, "estado-invalido", defeito)
    return st


def branch_proibida(p):
    """O motivo de não rodar nesta branch, ou "". Vale no início e em toda volta: a frente pode mudar no meio."""
    rc, atual = git(p.raiz, "symbolic-ref", "--quiet", "--short", "HEAD")
    if rc != 0:
        return "O repositório está com HEAD destacado, fora de qualquer branch."
    padroes = set()
    slot = p.slot("project", "default_branch")
    if slot:
        padroes.add(slot)
    rc, remoto = git(p.raiz, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if rc == 0 and remoto.strip():
        padroes.add(remoto.strip().replace("refs/remotes/origin/", "", 1))
    if atual.strip() in (padroes or {"main", "master"}):
        return "Branch atual: %s." % atual.strip()
    return ""


def define_em_utf8(p):
    try:
        with open(p.abs, "rb") as f:
            f.read().decode("utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    return True


def confere_gate(p, st):
    motivo = branch_proibida(p)
    if motivo:
        parada(p, st, "branch-padrao", motivo)
    if not define_em_utf8(p):
        parada(p, st, "define-invalido", "%s não está em UTF-8, ou não pôde ser lido." % p.define)
    rc, sha, cmd, linhas = bloco_do_gate(p)
    if rc != 0:
        parada(p, st, "define-invalido", "verify-gate.sh --print saiu %d." % rc)
    if sha != st["gate_sha"]:
        extra = "antes: %s\nagora: %s" % (st["gate_cmd"], cmd)
        if cmd == st["gate_cmd"]:  # o comando é o mesmo: o que mudou foi outro campo do bloco
            antes = st.get("gate_linhas") or []
            extra += "\nO comando é igual; mudou outro campo do bloco:\n" + "\n".join("   " + ln for ln in linhas if ln not in antes)
        parada(p, st, "gate-alterado", extra)
    rc = checar(p)
    if rc == 5:
        parada(p, st, "clarificacao-pendente")
    if rc == 64:
        parada(p, st, "define-invalido", "verify-gate.sh --checar saiu 64.")
    if rc != 0:
        falha("verify-gate.sh --checar saiu %d" % rc)


# ── tarefas ──────────────────────────────────────────────────────────────────────────────────────
def linhas_do_manifest(p):
    texto = ler(p.p(p.design))
    m = re.search(r"^## File Manifest[^\n]*\n(.*?)(?=^## |\Z)", texto, re.M | re.S)
    if not m:
        return []
    col, saida = None, []
    for ln in m.group(1).split("\n"):
        if not ln.strip().startswith("|"):
            if col is not None:
                break  # só a 1ª tabela é o manifest: as de baixo (Agent Assignment…) não são tarefa
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if col is None:
            col = next((k for k, h in enumerate(c) if h.lower() in ("file", "arquivo")), None)
            if col is None:
                return []
            continue
        if all(re.match(r"^:?-+:?$", x) for x in c if x) or col >= len(c):
            continue
        crase = re.search(r"`([^`]+)`", c[col])
        nome = crase.group(1) if crase else c[col]
        if nome:
            saida.append(nome)
    return saida


def tarefas(p, st):
    """(pendentes, total). Semeia o PROGRESS do manifest na 1ª vez; PROGRESS sem linhas é estado inválido."""
    caminho = p.p(p.progress)
    if not os.path.isfile(caminho):
        itens = linhas_do_manifest(p)
        if not itens:
            parada(p, st, "estado-invalido", "o File Manifest de %s não tem nenhuma linha de arquivo." % p.design)
        gravar_atomico(caminho, "# PROGRESS: %s\n\n" % p.feature + "".join("- [ ] %s\n" % i for i in itens))
    elif tem_design(p):
        # linha nova do manifest (o DESIGN cresceu num CORRIGIR) vira tarefa pendente
        texto = ler(caminho)
        ja = re.findall(r"(?m)^- \[(?: |x|X)\] (.+)$", texto)
        ja = [j.replace("`", "") for j in ja]
        novos = [i for i in linhas_do_manifest(p) if not any(re.match(re.escape(i) + r"(\s+[·—(-]|[:;,]\s|\s*$)", j) for j in ja)]
        if ja and novos:
            gravar_atomico(caminho, texto.rstrip("\n") + "\n" + "".join("- [ ] %s\n" % i for i in novos))
    pend, total = [], 0
    for ln in ler(caminho).split("\n"):
        m = re.match(r"^- \[( |x|X)\] (.+)$", ln)
        if m:
            total += 1
            if m.group(1) == " ":
                pend.append(m.group(2).strip())
    if total == 0:
        parada(p, st, "estado-invalido", "%s não tem linhas '- [ ]' nem '- [x]'; apague-o para recriar do File Manifest." % p.progress)
    return pend, total


def tem_design(p):
    return os.path.isfile(p.p(p.design))


def seguir_design(p):
    r = roda([BASH, os.path.join(BIN, "sdd-fluxo.sh"), "seguir", "design", p.define, "build", "--drive"], p.raiz)
    m = re.search(r"^PARAR: (.+)$", r.stdout, re.M)
    revisao = re.search(r"^DRIVE_ACAO: REVISAO_DESIGN$", r.stdout, re.M) is not None
    return r.returncode, m is not None, revisao, (m.group(1) if m else (r.stdout + r.stderr).strip()[:300])


def e_documento(caminho):
    """Pasta de documento E extensão de documento: um .sh em sdd/reports/ pode ser o gate, e aí conta como código."""
    return caminho.startswith(SO_DOCUMENTOS) and caminho.lower().endswith(EXT_DOCUMENTO)


def so_documentos(p, de, ate):
    # --no-renames: um rename mostra os 2 nomes, e tirar código do lugar não é "só documento"
    # --ignore-submodules=none: o ignore do .gitmodules viaja com o repositório, e o ponteiro novo é código novo
    rc, out = git(p.raiz, "diff", "--name-only", "--no-renames", "--ignore-submodules=none", "-z", de, ate)
    if rc != 0:
        return False
    return all(e_documento(a) for a in out.split("\0") if a)


def trava(p):
    return p.p("sdd/reports/progress/DRIVE_%s.lock" % p.feature)


def gate_rodando(p):
    """pid vivo na trava; trava de processo morto se libera (o agente pode ter sido cortado no meio do gate)."""
    try:
        pid = int(ler(trava(p)).strip())
        if pid <= 0:
            raise ValueError("pid inválido")
        if os.name == "nt":  # no Python nativo do Windows, o sinal 0 é CTRL_C_EVENT: interromperia o gate
            if str(pid) not in roda(["tasklist", "/FI", "PID eq %d" % pid, "/NH"], p.raiz, 60).stdout:
                raise ValueError("processo morto")
            return pid
        os.kill(pid, 0)
        return pid
    except PermissionError:
        return pid
    except (OSError, ValueError, OverflowError):
        try:
            os.remove(trava(p))
        except OSError:
            pass
        return 0


def msg_rodando(p, pid):
    return "O teste final está rodando (processo %d). Se não há teste nenhum rodando, apague %s." % (pid, os.path.relpath(trava(p), p.raiz))


def pega_trava(p):
    # Atômica, já com o pid: entre criar vazia e preencher, outro processo a tomaria por trava morta e a apagaria.
    tmp = "%s.%d" % (trava(p), os.getpid())
    try:
        os.makedirs(os.path.dirname(trava(p)), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        os.link(tmp, trava(p))
    except FileExistsError:
        return False
    except OSError as e:
        falha("não consegui gravar %s: %s" % (trava(p), e))
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass
    return True


def trava_herdada(p):
    """Só o filho do --fundo herda a trava: a variável sozinha, no ambiente de quem chama, não abre nada."""
    if os.environ.get("SDD_DRIVE_TRAVA_HERDADA") != "1":
        return False
    for _ in range(40):  # o pai grava o pid do filho logo depois de abri-lo
        try:
            # o pid do filho é o do bash que roda este script; o Python é filho dele
            if ler(trava(p)).strip() in (str(os.getpid()), str(os.getppid())):
                return True
        except OSError:
            return False
        time.sleep(0.05)
    return False


def solta_trava(p):
    """Só a trava de quem está soltando: se a nossa se perdeu e outro gate pegou, a dele fica."""
    try:
        if ler(trava(p)).strip() in (str(os.getpid()), str(os.getppid())):
            os.remove(trava(p))
    except OSError:
        pass


def fora_dos_documentos(p):
    """O que o verde não provaria: mudança rastreada, ou arquivo novo não ignorado, fora das pastas de documento."""
    rc, out = git(p.raiz, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none", "-z")
    if rc != 0:
        falha("git status falhou em " + p.raiz)
    saida, itens, k = [], out.split("\0"), 0
    while k < len(itens):
        reg = itens[k]
        k += 1
        if len(reg) < 4:
            continue
        if reg[0] in "RC" or reg[1] in "RC":  # rename: o nome antigo vem no campo seguinte, e tirar código do lugar também é mudança de código
            if k < len(itens) and not e_documento(itens[k]):
                saida.append(itens[k])
            k += 1
        if not e_documento(reg[3:]):
            saida.append(reg[3:])
    return saida


def proxima(p, st):
    pid = gate_rodando(p)
    if pid:
        return "ESPERAR", msg_rodando(p, pid)
    if not tem_design(p):
        return "DESIGN", ""
    rc, parou, revisao, motivo = seguir_design(p)
    if rc not in (0, 1) or (rc == 1 and not parou):
        falha("sdd-fluxo.sh seguir saiu %d: %s" % (rc, motivo))
    if rc != 0:
        return ("REVISAO_DESIGN" if revisao else "DESIGN"), motivo
    pend, total = tarefas(p, st)
    if pend:
        return "RODADA", "tarefa: %d de %d — %s" % (total - len(pend) + 1, total, pend[0])
    sujos = fora_dos_documentos(p)
    if sujos:  # o verde e o vermelho falam de um commit: código sem commit não está em nenhum dos 2
        return "COMMITAR", lista_sujos(sujos)
    head = p.head()
    ult = ultimo_valido(p, st)
    if ult and (ult["commit"] == head or so_documentos(p, ult["commit"], head)):
        if ult["exit"] == 2:
            r = st["maximo"] - vermelhos(st)
            return "CORRIGIR", "o teste final ficou vermelho (normal nesta etapa): restam %d rodada(s) · log: %s" % (r, ult["log"])
        if ult["exit"] == 0:
            return "AVALIAR_E_RELATAR", ""
    return "VERIFICAR", ""


# ── verbos ───────────────────────────────────────────────────────────────────────────────────────
def separa_max(args):
    valor, resto, k = None, [], 0
    while k < len(args):
        if args[k] == "--max":
            if k + 1 >= len(args):
                uso("--max exige um número")
            valor = args[k + 1]
            k += 2
            continue
        resto.append(args[k])
        k += 1
    return valor, resto


def precondicoes(p):
    motivo = branch_proibida(p)
    if motivo:
        parada(p, None, "branch-padrao", motivo)
    if not os.path.isfile(p.abs):
        parada(p, None, "define-invalido", "Arquivo não encontrado: %s." % p.define)
    if not define_em_utf8(p):
        parada(p, None, "define-invalido", "%s não está em UTF-8." % p.define)
    rc = checar(p)
    if rc == 5:
        parada(p, None, "clarificacao-pendente")
    if rc == 64:
        parada(p, None, "define-invalido", "verify-gate.sh --checar saiu 64 para %s." % p.define)
    if rc != 0:
        falha("verify-gate.sh --checar saiu %d" % rc)


def cmd_dry_run(args):
    flag, resto = separa_max(args)
    if len(resto) != 1:
        uso("--dry-run exige <DEFINE.md> [--max N]")
    p = Projeto(resto[0])
    maximo = limite(p, flag)
    precondicoes(p)
    rc, _sha, cmd = impressao_digital(p)
    if rc != 0:
        parada(p, None, "define-invalido", "verify-gate.sh --print saiu %d." % rc)
    r = roda([BASH, script_gate(p), "--print", p.define], p.raiz)
    kind = re.search(r"^kind:\s*(.*)$", r.stdout, re.M)
    print("Simulação de %s, com até %d rodada(s). Eu faria, nesta ordem:" % (p.define, maximo))
    print("  1. " + ("reaproveitar %s" % p.design if tem_design(p) else "escrever %s" % p.design) + ", com a revisão se ela for exigida;")
    print("  2. construir o que falta, uma tarefa por sessão nova, com 1 commit por tarefa;")
    print("  3. rodar o teste final (Verify Gate) e, se vermelho, corrigir e voltar ao passo 2;")
    print("  4. com o verde, avaliador e relatórios; e parar antes de publicar.")
    print("kind: " + (kind.group(1).strip() if kind else ""))
    print("cmd: " + cmd)
    parada(p, None, "simulacao")


def cmd_iniciar(args):
    flag, resto = separa_max(args)
    if len(resto) != 1:
        uso("iniciar exige <DEFINE.md> [--max N]")
    p = Projeto(resto[0])
    maximo = limite(p, flag)
    precondicoes(p)
    segura_estado(p)
    if os.path.exists(p.p(p.estado)):
        parada(p, None, "estado-invalido", "Já existe uma execução em %s: use --resume, ou apague o arquivo para recomeçar." % p.estado)
    rc, sha, cmd, linhas = bloco_do_gate(p)
    if rc != 0:
        parada(p, None, "define-invalido", "verify-gate.sh --print saiu %d." % rc)
    head = p.head()
    if not head:
        falha("o repositório ainda não tem commit", "faça o 1º commit e rode de novo.")
    st = dict(versao=2, feature=p.feature, define=p.define, gate_sha=sha, gate_cmd=cmd, inicio=head, maximo=maximo, gate_linhas=linhas,
              gates=[], trocas_gate=[], recibos=[], repeticao=dict(chave="", n=0), motivo="", detalhe="", parada_gate="", avisou_paradas=False)
    grava_estado(p, st)
    nome, detalhe = proxima(p, st)
    acao(p, st, nome, detalhe)


def cmd_resume(args):
    flag, resto = separa_max(args)
    aceitar = "--aceitar-gate-novo" in resto
    resto = [a for a in resto if a != "--aceitar-gate-novo"]
    if len(resto) != 1:
        uso("--resume exige <DEFINE.md> [--max N] [--aceitar-gate-novo]")
    p = Projeto(resto[0])
    novo_max = limite(p, flag) if flag is not None else None
    st = carrega(p)
    pid = gate_rodando(p)
    if pid:  # nada se grava com o gate rodando: o fim dele traria um estado que esta escrita apagaria
        acao(p, st, "ESPERAR", msg_rodando(p, pid))
    if novo_max is not None:
        st["maximo"] = novo_max
    if aceitar:
        rc, sha, cmd, linhas = bloco_do_gate(p)
        if rc == 0 and sha != st["gate_sha"]:
            mudou = [ln for ln in linhas if ln not in (st.get("gate_linhas") or [])]
            st["trocas_gate"].append(dict(de=st["gate_cmd"], para=cmd, data=datetime.date.today().isoformat(), campos=mudou))
            st["gate_sha"], st["gate_cmd"], st["gate_linhas"] = sha, cmd, linhas
            grava_estado(p, st)
            relatorio(p, st, st.get("motivo") or "")
    confere_gate(p, st)
    # Só a pessoa que resolveu um bloqueio zera a conta: sem subagente, toda volta passa por aqui, e a tarefa que não
    # anda precisa chegar à 3ª repetição do mesmo jeito.
    if st.get("motivo") == "bloqueio-humano":
        st["repeticao"] = dict(chave="", n=0)
    st["motivo"], st["detalhe"], st["parada_gate"] = "", "", ""
    grava_estado(p, st)
    if vermelhos(st) >= st["maximo"]:
        parada(p, st, "orcamento-rodadas", "Rodadas vermelhas: %d de %d. Sem subir o limite (--max), não há o que retomar." % (vermelhos(st), st["maximo"]))
    pronto = ""
    if os.path.isfile(p.p(p.progress)):
        total = re.findall(r"(?m)^- \[( |x|X)\] ", ler(p.p(p.progress)))
        pronto = "%d de %d" % (sum(1 for t in total if t != " "), len(total))
    ultimo = str(st["gates"][-1]["exit"]) if st["gates"] else "nenhum"
    print("retomando: rodada %d/%d · %s tarefas prontas · último teste final: %s · não gastei rodada"
          % (rodada_atual(st), st["maximo"], pronto or "0 de 0", ultimo))
    nome, detalhe = proxima(p, st)
    conta_repeticao(p, st, nome, detalhe)
    acao(p, st, nome, detalhe)


def um_define(verbo, args):
    if len(args) != 1:
        uso("%s exige <DEFINE.md>" % verbo)
    return Projeto(args[0])


def barra_orcamento(p, st):
    if vermelhos(st) >= st["maximo"]:
        parada(p, st, "orcamento-rodadas", "Rodadas vermelhas: %d de %d." % (vermelhos(st), st["maximo"]))


def conta_repeticao(p, st, nome, detalhe):
    if nome == "ESPERAR":
        return
    sha_design = hashlib.sha256(ler(p.p(p.design)).encode("utf-8")).hexdigest() if tem_design(p) else ""
    # Na tarefa, conta a posição e não o texto: a anotação de erro muda a cada volta sem que nada tenha andado.
    identidade = re.sub(r" — .*$", "", detalhe, flags=re.S) if nome == "RODADA" else detalhe
    chave = "|".join((nome, identidade, p.head(), sha_design))
    rep = st.get("repeticao") or dict(chave="", n=0)
    rep = dict(chave=chave, n=rep["n"] + 1 if rep.get("chave") == chave else 1)
    st["repeticao"] = rep
    grava_estado(p, st)
    if rep["n"] >= REPETICOES:
        parada(p, st, "bloqueio-humano", "A ação %s não avançou em %d tentativas. %s" % (nome, REPETICOES, detalhe))


def parada_guardada(p, st):
    if st.get("parada_gate") in PARADAS_DO_GATE:
        ult = st["gates"][-1] if st["gates"] else None
        parada(p, st, st["parada_gate"], "log: " + ult["log"] if ult else "")
    if st.get("motivo") == "bloqueio-humano":  # a saída é o --resume, depois de resolver
        parada(p, st, "bloqueio-humano", st.get("detalhe") or "")


def cmd_proximo(args):
    p = um_define("proximo", args)
    st = carrega(p)
    pid = gate_rodando(p)
    if pid:
        acao(p, st, "ESPERAR", msg_rodando(p, pid))
    parada_guardada(p, st)
    confere_gate(p, st)
    barra_orcamento(p, st)
    nome, detalhe = proxima(p, st)
    st["motivo"], st["detalhe"] = "", ""  # a parada anterior já foi resolvida: chegou até aqui
    conta_repeticao(p, st, nome, detalhe)
    grava_estado(p, st)
    acao(p, st, nome, detalhe)


def lista_sujos(sujos):
    return "\n".join("   - " + a for a in sujos[:10]) + ("\n   e mais %d" % (len(sujos) - 10) if len(sujos) > 10 else "")


def cmd_verificar(args):
    fundo = "--fundo" in args
    p = um_define("verificar", [a for a in args if a != "--fundo"])
    st = carrega(p)
    herdada = trava_herdada(p)
    pid = gate_rodando(p)
    if pid and not herdada:
        acao(p, st, "ESPERAR", msg_rodando(p, pid))
    if not herdada:
        parada_guardada(p, st)
    confere_gate(p, st)
    barra_orcamento(p, st)
    sujos = fora_dos_documentos(p)
    if sujos:
        if herdada:
            solta_trava(p)
        acao(p, st, "COMMITAR", lista_sujos(sujos))
    if not herdada:
        nome, detalhe = proxima(p, st)
        if nome != "VERIFICAR":
            acao(p, st, nome, detalhe)
        if not pega_trava(p):
            acao(p, st, "ESPERAR", "Outro teste final acabou de começar.")
    if fundo:
        registro = "sdd/reports/progress/DRIVE_%s.fundo.log" % p.feature
        with open(p.p(registro), "a", encoding="utf-8") as f:
            filho = subprocess.Popen([BASH, os.path.abspath(SELF), "verificar", p.define], cwd=p.raiz, stdin=subprocess.DEVNULL, stdout=f,
                                     stderr=subprocess.STDOUT, start_new_session=True, env=dict(os.environ, SDD_DRIVE_TRAVA_HERDADA="1"))
        with open(trava(p), "w", encoding="utf-8") as f:
            f.write(str(filho.pid))
        acao(p, st, "ESPERAR", "O teste final foi para o fundo (processo %d); a saída do script fica em %s." % (filho.pid, registro))
    n = len(st["gates"]) + 1
    log = "sdd/reports/evidence/%s/DRIVE-gate-r%d.log" % (p.feature, n)
    while os.path.lexists(p.p(log)):  # log cortado de uma execução morta não é sobrescrito; link também não é seguido
        n += 1
        log = "sdd/reports/evidence/%s/DRIVE-gate-r%d.log" % (p.feature, n)
    # O que o gate prova é o que existia quando ele começou: um commit ou uma troca de comando no meio não ganham esse verde.
    commit_testado, impressao_testada = p.head(), st["gate_sha"]
    larga_estado()  # o gate pode levar muitos minutos, e recibo e proximo não esperam por ele
    env_gate = dict(os.environ)
    env_gate.pop("SDD_DRIVE_TRAVA_HERDADA", None)  # a suíte de um projeto pode exercitar este mesmo script
    try:
        os.makedirs(os.path.dirname(p.p(log)), exist_ok=True)
        print("▶ rodando o teste final; isso pode levar alguns minutos.", file=sys.stderr)
        sys.stderr.flush()
        with open(p.p(log), "w", encoding="utf-8") as f:
            f.write("$ verify-gate.sh %s\n" % p.define)
            f.flush()
            r = subprocess.run([BASH, script_gate(p), p.define], cwd=p.raiz, stdout=f, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, env=env_gate)
            f.write("[exit=%d]\n" % r.returncode)
    except OSError as e:
        solta_trava(p)
        falha("não consegui rodar o teste final: %s" % e)
    except KeyboardInterrupt:
        solta_trava(p)
        falha("o teste final foi interrompido; nenhuma rodada foi gasta.", "chame verificar de novo.")
    rc = r.returncode
    st = carrega(p)  # um recibo ou uma retomada pode ter gravado enquanto o gate rodava
    rodada = rodada_atual(st)
    st["gates"].append(dict(n=n, rodada=rodada, commit=commit_testado, exit=rc, log=log, impressao=impressao_testada))
    st["repeticao"] = dict(chave="", n=0)
    bloqueado = st.get("motivo") == "bloqueio-humano"  # gravado enquanto o gate rodava: a saída continua sendo o --resume
    st["parada_gate"] = ""
    if not bloqueado:
        st["motivo"], st["detalhe"] = "", ""
    if rc in (3, 4, 5, 64) or rc not in (0, 2):
        st["parada_gate"] = {4: "manual-ux", 5: "clarificacao-pendente", 64: "define-invalido"}.get(rc, "gate-inconclusivo")
    grava_estado(p, st)
    solta_trava(p)
    if bloqueado:
        parada(p, st, "bloqueio-humano", st.get("detalhe") or "")
    if rc == 0:
        nome, detalhe = proxima(p, st)
        frase = ("O teste final passou (log: %s). Ainda não publiquei nada." % log if nome == "AVALIAR_E_RELATAR"
                 else "O teste final passou, mas há código novo depois de quando ele começou (log: %s)." % log)
        acao(p, st, nome, frase + ("\n" + detalhe if detalhe else ""))
    if rc == 2:
        if vermelhos(st) >= st["maximo"]:
            parada(p, st, "orcamento-rodadas", "Rodadas vermelhas: %d de %d · log: %s" % (vermelhos(st), st["maximo"], log))
        nome, detalhe = proxima(p, st)
        if nome != "CORRIGIR":
            detalhe = ("O teste final ficou vermelho e gastou 1 rodada (log: %s); há commit novo depois de quando ele começou." % log
                       + ("\n" + detalhe if detalhe else ""))
        acao(p, st, nome, detalhe)
    if rc == 4:
        parada(p, st, "manual-ux", "log: " + log)
    if rc == 5:
        parada(p, st, "clarificacao-pendente", "log: " + log)
    if rc == 64:
        parada(p, st, "define-invalido", "log: " + log)
    parada(p, st, "gate-inconclusivo", "O teste final saiu %d · log: %s" % (rc, log))


def cmd_concluir(args):
    p = um_define("concluir", args)
    st = carrega(p)
    parada_guardada(p, st)
    confere_gate(p, st)
    barra_orcamento(p, st)
    sujos = fora_dos_documentos(p)
    if sujos:
        acao(p, st, "COMMITAR", lista_sujos(sujos))
    # concluir e proximo respondem a mesma coisa: tarefa reaberta, DESIGN sumido ou código novo não viram verde.
    nome, detalhe = proxima(p, st)
    if nome != "AVALIAR_E_RELATAR":
        ult = ultimo_valido(p, st)
        if nome == "VERIFICAR" and ult and ult["exit"] == 0:
            detalhe = "Há código novo depois do último teste final verde (%s)." % ult["commit"][:12]
        acao(p, st, nome, detalhe)
    if not os.path.isfile(p.p(p.build_report)):
        acao(p, st, "AVALIAR_E_RELATAR", "Falta %s." % p.build_report)
    lint = os.path.join(BIN, "report-lint.py")
    for extra in ([], ["--pendente"]):
        r = roda([sys.executable, "-B", lint] + extra + [p.build_report], p.raiz)
        if r.returncode != 0:
            acao(p, st, "AVALIAR_E_RELATAR", "report-lint.py %ssaiu %d:\n%s" % (" ".join(extra) + " " if extra else "", r.returncode,
                                                                                 (r.stdout + r.stderr).strip()[-1500:]))
    parada(p, st, "gate-verde", "Rodadas vermelhas: %d de %d." % (vermelhos(st), st["maximo"]))


def cmd_bloqueio(args):
    if len(args) != 2 or not args[1].strip():
        uso("bloqueio exige <DEFINE.md> \"<motivo>\"")
    p = Projeto(args[0])
    st = carrega(p)
    parada(p, st, "bloqueio-humano", args[1].strip())


def cmd_recibo(args):
    if len(args) != 2 or not args[1].strip():
        uso("recibo exige <DEFINE.md> \"<texto>\"")
    p = Projeto(args[0])
    st = carrega(p)
    st["recibos"].append(" ".join(args[1].split()))
    grava_estado(p, st)
    relatorio(p, st, st.get("motivo") or "")
    print("✅ anotado em %s (Decidi sozinho)." % p.relatorio)
    fim("RECIBO GRAVADO", "siga a próxima ação.")
    return 0


def cmd_aguardar(args):
    if len(args) != 3:
        uso("aguardar exige <DEFINE.md> <papel> <brief>")
    p = Projeto(args[0])
    st = carrega(p)
    r = roda([BASH, os.path.join(BIN, "sdd-fluxo.sh"), "despachar", args[1], p.feature, args[2]], p.raiz)
    print(r.stdout, end="")
    print(r.stderr, end="", file=sys.stderr)
    if r.returncode != 40:
        sys.exit(r.returncode)
    if os.path.isfile(p.p(p.progress)):
        prox = re.search(r"(?m)^- \[ \] (.+)$", ler(p.p(p.progress)))
        if prox:
            print("tarefa: " + prox.group(1).strip())
    if not st.get("avisou_paradas"):
        total = 0
        if os.path.isfile(p.p(p.progress)):
            total = len(re.findall(r"(?m)^- \[( |x|X)\] ", ler(p.p(p.progress))))
        print("Esta execução tem %d tarefa(s): sem subagente, são até %d parada(s), uma por tarefa; você pode parar e voltar quando quiser." % (total, total))
        st["avisou_paradas"] = True
    parada(p, st, "aguardando-sessao")


# ── self-test ────────────────────────────────────────────────────────────────────────────────────
FIXTURE_DEFINE = """# DEFINE: FIXTURE

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — fixture do self-test | self-test |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "test -f .verde"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```
"""
FIXTURE_DESIGN = """# DESIGN: FIXTURE

## Metadata

| Attribute | Value |
|---|---|
| **Status** | Ready for Build |

## Key Decisions

### Decision 1: fixture

Sem decisão real: é o self-test.

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `a` | Modify | a | (general) | None |
| 2 | `b` | Modify | b | (general) | None |

**Total Files:** 2
"""


def cmd_self_test(args):
    if args:
        uso("--self-test não aceita argumentos")
    for arq in ("verify-gate.sh", "sdd-fluxo.sh", "design-lint.py"):
        if not os.path.isfile(os.path.join(BIN, arq)):
            falha("script ausente em sdd/bin/: " + arq, "atualize sdd/bin/: rode o doctor e, para o que ele apontar, apague e rode o init.")
    tmp = tempfile.mkdtemp(prefix="sdd-drive-")
    falhas = []
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@example.com", GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull, GIT_CEILING_DIRECTORIES=tmp,
               SDD_TRACE="off")
    for chave in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "SDD_DRIVE_TRAVA_HERDADA"):
        env.pop(chave, None)

    def sh(cwd, *cmd):
        return subprocess.run(list(cmd), cwd=cwd, env=env, capture_output=True, encoding="utf-8", errors="replace",
                              stdin=subprocess.DEVNULL)

    def grava(r, rel, texto):
        os.makedirs(os.path.dirname(os.path.join(r, rel)), exist_ok=True)
        with open(os.path.join(r, rel), "w", encoding="utf-8") as f:
            f.write(texto)

    def monta(nome, branch="frente", define=FIXTURE_DEFINE, ignora=True):
        r = os.path.join(tmp, nome)
        os.makedirs(os.path.join(r, "sdd/bin"))
        for arq in ("verify-gate.sh", "sdd-fluxo.sh", "design-lint.py"):
            shutil.copy(os.path.join(BIN, arq), os.path.join(r, "sdd/bin", arq))
        shutil.copy(SELF, os.path.join(r, "sdd/bin/sdd-drive.sh"))
        grava(r, "sdd/bin/report-lint.py", "import sys\nsys.exit(0)\n")
        grava(r, "sdd/features/DEFINE_FIXTURE.md", define)
        grava(r, "sdd/features/DESIGN_FIXTURE.md", FIXTURE_DESIGN)
        grava(r, ".gitignore", ".verde\n")
        sh(r, "git", "init", "-q")
        sh(r, "git", "symbolic-ref", "HEAD", "refs/heads/" + branch)
        sh(r, "git", "add", "-A")
        sh(r, "git", "commit", "-q", "-m", "base")
        return r

    def drive(r, *args):
        return sh(r, BASH, "sdd/bin/sdd-drive.sh", *args)

    def espera(nome, res, rc, texto):
        ok = res.returncode == rc and re.search(texto, res.stdout + res.stderr)
        print(("  ✅ " if ok else "  🛑 ") + nome)
        if not ok:
            falhas.append(nome)

    D = "sdd/features/DEFINE_FIXTURE.md"

    def tudo_feito(r):
        grava(r, "sdd/reports/progress/PROGRESS_FIXTURE.md", "- [x] a\n- [x] b\n")

    try:
        # vermelhos antes dos verdes
        r = monta("u")
        espera("uso sem argumentos ⇒ 64", drive(r), 64, "ERRO DE USO")
        espera("--max inválido ⇒ 64", drive(r, "iniciar", D, "--max", "0"), 64, "inteiro a partir de 1")
        espera("branch padrão ⇒ branch-padrao", drive(monta("p", branch="main"), "iniciar", D), 20, "motivo: branch-padrao")
        espera("DEFINE sem bloco ⇒ define-invalido", drive(monta("i", define=FIXTURE_DEFINE.split("## Verify Gate")[0]), "iniciar", D), 20,
               "motivo: define-invalido")
        marcador = "[NEEDS " + "CLARIFICATION: qual?]"
        espera("marcador ativo ⇒ clarificacao-pendente", drive(monta("c", define=FIXTURE_DEFINE + "\n" + marcador + "\n"), "iniciar", D), 20,
               "motivo: clarificacao-pendente")
        espera("sem estado ⇒ estado-invalido", drive(r, "proximo", D), 20, "motivo: estado-invalido")

        r = monta("x")
        grava(r, "sdd/reports", "um arquivo no lugar da pasta\n")
        espera("não consegue gravar ⇒ 2", drive(r, "iniciar", D), 2, "RESULTADO: FALHA")

        r = monta("s")
        espera("simulação ⇒ simulacao", drive(r, "--dry-run", D), 0, "motivo: simulacao")
        if os.path.exists(os.path.join(r, "sdd/reports")):
            falhas.append("a simulação gravou arquivo")
        espera("iniciar ⇒ ação", drive(r, "iniciar", D), 10, "ACAO: RODADA")
        espera("iniciar de novo ⇒ estado-invalido", drive(r, "iniciar", D), 20, "motivo: estado-invalido")
        drive(r, "proximo", D)
        drive(r, "proximo", D)
        espera("3ª repetição ⇒ bloqueio-humano", drive(r, "proximo", D), 20, "motivo: bloqueio-humano")
        espera("resume ⇒ 10", drive(r, "--resume", D), 10, "retomando: rodada 1/3")
        espera("bloqueio ⇒ bloqueio-humano", drive(r, "bloqueio", D, "travou"), 20, "travou")
        grava(r, "brief.md", "x\n")
        espera("aguardar ⇒ aguardando-sessao", drive(r, "aguardar", D, "executor-drive", "brief.md"), 40, "motivo: aguardando-sessao")

        r = monta("a")
        drive(r, "iniciar", D, "--max", "2")
        grava(r, D, FIXTURE_DEFINE.replace("test -f .verde", "true"))
        espera("gate mudou ⇒ gate-alterado", drive(r, "proximo", D), 20, "motivo: gate-alterado")
        espera("gate mudou continua parado", drive(r, "--resume", D), 20, "motivo: gate-alterado")
        espera("aceitar o gate novo", drive(r, "--resume", D, "--aceitar-gate-novo"), 10, "ACAO:")

        r = monta("o")
        drive(r, "iniciar", D, "--max", "1")
        tudo_feito(r)
        espera("vermelho no limite ⇒ orcamento-rodadas", drive(r, "verificar", D), 20, "motivo: orcamento-rodadas")
        espera("o limite segue valendo", drive(r, "proximo", D), 20, "motivo: orcamento-rodadas")

        r = monta("m", define=FIXTURE_DEFINE.replace("kind: test", "kind: manual-ux").replace("test -f .verde", "N/A (manual-ux)"))
        drive(r, "iniciar", D)
        tudo_feito(r)
        espera("manual-ux ⇒ manual-ux", drive(r, "verificar", D), 20, "motivo: manual-ux")

        r = monta("n")
        drive(r, "iniciar", D)
        tudo_feito(r)
        original = ler(os.path.join(r, "sdd/bin/verify-gate.sh"))
        grava(r, "sdd/bin/verify-gate.sh", original.replace('DEFINE="${1:-}"', 'DEFINE="${1:-}"\n[ "${PRINT_ONLY}" = 0 ] && [ "${CHECAR}" = 0 ] && exit 3', 1))
        sh(r, "git", "add", "-A")
        sh(r, "git", "commit", "-q", "-m", "gate de mentira")
        espera("gate inconclusivo ⇒ gate-inconclusivo", drive(r, "verificar", D), 20, "motivo: gate-inconclusivo")

        # o caminho verde, inteiro
        r = monta("v")
        espera("verde: iniciar", drive(r, "iniciar", D), 10, "tarefa: 1 de 2")
        tudo_feito(r)
        espera("verde: vermelho gasta rodada", drive(r, "verificar", D), 10, "ACAO: CORRIGIR")
        espera("verde: sem commit novo não roda de novo", drive(r, "verificar", D), 10, "ACAO: CORRIGIR")
        grava(r, "codigo.txt", "x\n")
        espera("verde: arquivo novo ⇒ COMMITAR", drive(r, "verificar", D), 10, "ACAO: COMMITAR")
        sh(r, "git", "add", "codigo.txt")
        sh(r, "git", "commit", "-q", "-m", "conserto")
        grava(r, ".verde", "")
        espera("verde: gate 0 ⇒ avaliar", drive(r, "verificar", D), 10, "ACAO: AVALIAR_E_RELATAR")
        espera("verde: sem relatório não conclui", drive(r, "concluir", D), 10, "Falta sdd/reports/BUILD_REPORT_FIXTURE.md")
        grava(r, "sdd/reports/BUILD_REPORT_FIXTURE.md", "x\n")
        espera("verde: concluir ⇒ gate-verde", drive(r, "concluir", D), 0, "motivo: gate-verde")
        rel = os.path.join(r, "sdd/reports/DRIVE_REPORT_FIXTURE.md")
        if not (os.path.isfile(rel) and "gate-verde" in ler(rel)):
            falhas.append("o DRIVE_REPORT não saiu com o motivo")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if falhas:
        print("🛑 self-test: %d caso(s) falharam: %s" % (len(falhas), "; ".join(falhas)))
        fim("FALHA", "o script não cumpre o contrato: corrija antes de usar.")
        return 2
    print("✅ self-test: todos os casos passaram.")
    fim("VERDE", "o script está conforme o contrato.")
    return 0


def main():
    args = sys.argv[1:]
    if not args:
        uso("falta o verbo")
    verbo, resto = args[0], args[1:]
    tabela = {"iniciar": cmd_iniciar, "--dry-run": cmd_dry_run, "--resume": cmd_resume, "proximo": cmd_proximo,
              "verificar": cmd_verificar, "concluir": cmd_concluir, "bloqueio": cmd_bloqueio, "recibo": cmd_recibo,
              "aguardar": cmd_aguardar, "--self-test": cmd_self_test}
    if verbo not in tabela:
        uso("verbo desconhecido: " + verbo)
    if verbo != "--self-test":
        confere_vizinhos()
    return tabela[verbo](resto)


try:
    try:
        rc_main = main()
    finally:
        larga_estado()
    sys.exit(rc_main)
except subprocess.TimeoutExpired as e:
    falha("um comando passou do tempo: %s" % (e.cmd,))
except OSError as e:
    falha("erro de sistema: %s" % e)
except Exception as e:  # nunca um traceback, nunca exit 1: a quem lê, isso não diria o que fazer
    falha("erro inesperado: %s: %s" % (type(e).__name__, e))
PY
