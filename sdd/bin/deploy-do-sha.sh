#!/usr/bin/env bash
# deploy-do-sha.sh — "o deploy deste commit está no ar?". É a verificação do item 10 da sdd-release, num lugar só.
#
# Regra: vale o run do workflow que publica, na branch padrão, do commit perguntado; ou um run mais novo, verde, de um
# commit que contém o perguntado (substituto, quando um push tomou o lugar na fila). Falha em passo declarado como
# passageiro repete 1 vez, por gh workflow run na ponta da branch, só se o commit ainda é a ponta e não há nada mais
# novo. Nunca gh run rerun: o rerun refaz um commit antigo, e, se um push chegar no meio, publica código velho por cima
# do novo. "Ainda não sei" nunca vira verde nem "não contém".
#
# USO-INICIO
#   deploy-do-sha.sh --commit <sha> [--workflow <arquivo>] [--branch <b>] [--repo <dir>] [--teto 2400] [--intervalo 15]
#                    [--sem-run 120] [--transitorios "passo a,passo b"]
# USO-FIM
#   --workflow vem de deploy.workflow; --transitorios, de deploy.transient_steps (vazio = nunca repete), em sdd/config.yaml.
#   --branch vem de project.default_branch; vazio, de origin/HEAD; sem nenhum, main.
#   Só contam runs com event push ou workflow_dispatch: um schedule verde no mesmo SHA não publicou nada.
#
# Exit: 0 no ar (próprio ou substituto) · 2 não está no ar · 3 gh ou git ausente, ou gh sem login · 4 ainda não sei
#       (não terminou no teto, ou nenhum run em --sem-run segundos) · 64 uso, commit desconhecido ou sem workflow.
# ⚠️ bash 3.2 · o núcleo é Python 3.9 stdlib, lido do stdin: todo filho roda com stdin fechado.

set -u

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 deploy-do-sha: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

python3 -I -B - ${1+"$@"} <<'PY'
from __future__ import annotations

import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

for _canal in (sys.stdout, sys.stderr):
    try:
        _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except Exception:
        pass

CAMPOS = "databaseId,headSha,headBranch,status,conclusion,createdAt,workflowName,event"
LIMITE_CMD = 60
USO = ("uso: deploy-do-sha.sh --commit <sha> [--workflow <arquivo>] [--branch <b>] [--repo <dir>] [--teto 2400] "
       "[--intervalo 15] [--sem-run 120] [--transitorios \"passo a,passo b\"]")


def fim(exitc, frase, resultado, seta):
    print(frase)
    print("RESULTADO: " + resultado)
    print("→ " + seta)
    sys.exit(exitc)


def uso(motivo):
    print("🛑 deploy-do-sha: " + motivo, file=sys.stderr)
    print(USO, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ corrija a chamada e rode de novo; nada foi consultado.", file=sys.stderr)
    sys.exit(64)


def curto(sha):
    return (sha or "")[:7] or "—"


def args_de(argv):
    a = {}
    k = 0
    validas = ("--commit", "--workflow", "--branch", "--repo", "--teto", "--intervalo", "--sem-run", "--transitorios")
    while k < len(argv):
        if argv[k] not in validas:
            uso("opção desconhecida: " + argv[k])
        if k + 1 >= len(argv):
            uso(argv[k] + " exige um valor")
        a[argv[k][2:]] = argv[k + 1]
        k += 2
    return a


def numero(a, nome, padrao):
    txt = a.get(nome, padrao)
    if not re.match(r"^[0-9]+$", str(txt)):
        uso("--%s precisa ser um número inteiro de segundos: '%s'" % (nome, txt))
    return int(txt)


def slot(raiz, bloco, chave):
    caminho = os.path.join(raiz, "sdd/config.yaml")
    if not os.path.isfile(caminho):
        return ""
    dentro = False
    with open(caminho, encoding="utf-8", errors="replace") as f:
        for ln in f.read().splitlines():
            if ln and not ln[0].isspace() and not ln.startswith("#"):
                dentro = ln.split("#", 1)[0].strip() == bloco + ":"
                continue
            m = re.match(r"^\s+" + re.escape(chave) + r":\s*(.*)$", ln) if dentro else None
            if m:
                return m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
    return ""


def roda(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                          timeout=LIMITE_CMD, env=dict(os.environ, GIT_TERMINAL_PROMPT="0"))


class ConsultaFalhou(Exception):
    pass


class Deploy:
    def __init__(self, repo, x, workflow, branch, transitorios):
        self.repo, self.x, self.workflow, self.branch, self.transitorios = repo, x, workflow, branch, transitorios
        self.ultimo_fetch = 0.0

    def gh(self, *args):
        try:
            r = roda(["gh"] + list(args), self.repo)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ConsultaFalhou(str(e))
        if r.returncode != 0:
            texto = (r.stderr or r.stdout).strip()
            if re.search(r"auth login|not logged|HTTP 401", texto):
                fim(3, "⚠️ inconclusivo — o gh não está logado (%s)." % texto.split("\n")[0], "INCONCLUSIVO",
                    "rode gh auth login e repita; não concluí nada sobre o deploy.")
            raise ConsultaFalhou(texto.split("\n")[0] if texto else "gh saiu %d" % r.returncode)
        return r.stdout

    def lista(self, *filtro):
        try:
            saida = self.gh("run", "list", "--workflow", self.workflow, "--branch", self.branch, "--limit", "50", "--json", CAMPOS, *filtro)
        except ConsultaFalhou as e:
            if re.search(r"could not find any workflows|^HTTP 404", str(e), re.I):
                uso("o GitHub não conhece o workflow '%s': %s" % (self.workflow, e))
            raise
        try:
            runs = json.loads(saida or "[]")
        except ValueError as e:
            raise ConsultaFalhou("resposta do gh ilegível: %s" % e)
        if not isinstance(runs, list):
            raise ConsultaFalhou("resposta do gh ilegível")
        # Run de tag ou de outra branch com o mesmo SHA não responde pelo deploy; sem o campo, também fica de fora.
        return [r for r in runs if isinstance(r, dict) and r.get("headBranch") == self.branch
                and r.get("event") in ("push", "workflow_dispatch")]

    def passos_falhos(self, run_id):
        """Todos os passos que falharam: um passageiro no job 1 não esconde um real no job 2. [] se a resposta não diz.
        Consulta que falha sobe como ConsultaFalhou: quem chama tenta de novo, em vez de concluir sem saber."""
        try:
            dados = json.loads(self.gh("run", "view", str(run_id), "--json", "jobs") or "[]")
        except ValueError:
            return []
        saida = []
        for job in (dados.get("jobs") or []) if isinstance(dados, dict) else []:
            if not isinstance(job, dict):
                continue
            achados = [q.get("name") for q in (job.get("steps") or []) if isinstance(q, dict) and q.get("conclusion") == "failure"]
            if not achados and job.get("conclusion") in ("failure", "timed_out", "cancelled"):
                achados = ["job %s" % job.get("name")]  # job falho sem passo falho nunca é passageiro
            saida += achados
        return saida

    def git(self, *args):
        try:
            return roda(["git", "-C", self.repo] + list(args), self.repo)
        except (OSError, subprocess.TimeoutExpired):
            return None

    def contem(self, y):
        """True, False ou None (não dá para saber agora: o clone ainda não conhece o commit)."""
        r = self.git("merge-base", "--is-ancestor", self.x, y)
        if r is not None and r.returncode in (0, 1):
            return r.returncode == 0
        if time.time() - self.ultimo_fetch >= 60:
            self.ultimo_fetch = time.time()
            self.git("fetch", "-q", "origin", self.branch)
            r = self.git("merge-base", "--is-ancestor", self.x, y)
            if r is not None and r.returncode in (0, 1):
                return r.returncode == 0
        return None

    def ponta(self):
        r = self.git("fetch", "-q", "origin", self.branch)
        if r is None or r.returncode != 0:
            return None
        r = self.git("rev-parse", "origin/" + self.branch)
        return r.stdout.strip() if r is not None and r.returncode == 0 else None

    def marca(self):
        # na pasta comum do git: o limite de 1 redisparo vale por commit, e não por worktree
        r = self.git("rev-parse", "--git-common-dir")
        if r is None or r.returncode != 0 or not r.stdout.strip():
            return None
        return os.path.join(self.repo, r.stdout.strip(), "deploy-do-sha", "redisparado-" + self.x)

    def ja_marcado(self):
        m = self.marca()
        return bool(m) and os.path.exists(m)

    def desmarcar(self):
        m = self.marca()
        try:
            if m:
                os.remove(m)
        except OSError:
            pass

    def marcar(self):
        """True se esta chamada ficou com o redisparo; False se outra já ficou (criação exclusiva: 2 chamadas juntas não repetem 2 vezes)."""
        m = self.marca()
        try:
            if not m:
                raise OSError("git rev-parse --git-path falhou")
            os.makedirs(os.path.dirname(m), exist_ok=True)
            with open(m, "x", encoding="utf-8") as f:
                f.write(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")
        except FileExistsError:
            return False
        except OSError as e:
            print("⚠️ a marca local do redisparo não gravou (%s); o run por workflow_dispatch segue contando." % e, file=sys.stderr)
        return True


def mais_novo_que(r, p):
    a, b = r.get("createdAt") or "", p.get("createdAt") or ""
    return a > b or (a == b and (r.get("databaseId") or 0) > (p.get("databaseId") or 0))


def o_mais_novo(runs):
    atual = runs[0]
    for r in runs[1:]:
        if mais_novo_que(r, atual):
            atual = r
    return atual


def main():
    a = args_de(sys.argv[1:])
    if not a.get("commit"):
        uso("falta --commit <sha>")
    teto, intervalo, sem_run = numero(a, "teto", 2400), numero(a, "intervalo", 15), numero(a, "sem-run", 120)
    for prog in ("git", "gh"):
        if not shutil.which(prog):
            fim(3, "⚠️ inconclusivo — %s não está instalado." % prog, "INCONCLUSIVO",
                "publicado, sem verificação automática: confira o deploy à mão; não concluí nada sobre ele.")
    base = os.path.abspath(a.get("repo", "."))
    if not os.path.isdir(base):
        uso("pasta não encontrada: " + base)
    r = roda(["git", "-C", base, "rev-parse", "--show-toplevel"], base)
    if r.returncode != 0:
        uso("%s não é um repositório git" % base)
    repo = r.stdout.strip()
    r = roda(["git", "-C", repo, "rev-parse", "--verify", a["commit"] + "^{commit}"], repo)
    if r.returncode != 0:  # o merge de um PR nasce no remoto: o clone pode ainda não conhecer
        busca = roda(["git", "-C", repo, "fetch", "-q", "origin"], repo)
        if busca.returncode != 0:
            fim(4, "⏳ ainda não sei — o clone não conhece %s, e o git fetch falhou: %s" % (a["commit"], (busca.stderr or "").strip().split("\n")[0]),
                "AINDA NAO SEI", "confira a rede e o acesso ao remoto e rode de novo; não concluí nada sobre o deploy.")
        r = roda(["git", "-C", repo, "rev-parse", "--verify", a["commit"] + "^{commit}"], repo)
    if r.returncode != 0:
        uso("commit não encontrado, nem depois de git fetch: %s" % a["commit"])
    x = r.stdout.strip()
    workflow = a.get("workflow") or slot(repo, "deploy", "workflow")
    if not workflow:
        uso("falta o workflow: passe --workflow <arquivo> ou preencha deploy.workflow em sdd/config.yaml")
    branch = a.get("branch") or slot(repo, "project", "default_branch")
    if not branch:
        r = roda(["git", "-C", repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], repo)
        branch = r.stdout.strip().replace("refs/remotes/origin/", "", 1) if r.returncode == 0 else ""
    branch = branch or "main"
    bruto = a["transitorios"] if "transitorios" in a else slot(repo, "deploy", "transient_steps")
    transitorios = [t.strip() for t in bruto.split(",") if t.strip()]
    d = Deploy(repo, x, workflow, branch, transitorios)
    inicio = time.time()
    ja_redisparou = d.ja_marcado()
    pela_marca = ja_redisparou
    origem = "este script" if ja_redisparou else ""
    id_falho = None
    repetido_em = inicio
    ultimo_estado, ultimo_aviso = "", 0.0
    alvo_run = "—"
    ultimo_erro = ""

    def espera(status, run):
        nonlocal ultimo_estado, ultimo_aviso, alvo_run
        alvo_run = run
        agora = time.time()
        estado = "%s|%s" % (status, run)
        if estado != ultimo_estado or agora - ultimo_aviso >= 60:
            print("⏳ %s · %d/%d min · run %s" % (status, int((agora - inicio) / 60), int(teto / 60), run), file=sys.stderr)
            ultimo_estado, ultimo_aviso = estado, agora

    while True:
        tempo = time.time() - inicio
        try:
            meus = [r for r in d.lista("--commit", x) if r.get("headSha") == x]
            da_branch = None
            if not meus or (o_mais_novo(meus).get("status") == "completed" and o_mais_novo(meus).get("conclusion") != "success"):
                da_branch = d.lista()
                ids = set(r.get("databaseId") for r in meus)
                # a listagem por commit pode atrasar: run deste SHA que só aparece na branch também é dele
                meus = meus + [r for r in da_branch if r.get("headSha") == x and r.get("databaseId") not in ids]
            if not meus:
                if tempo >= sem_run:
                    fim(4, "⏳ ainda não sei — não achei nenhum run de %s no workflow %s em %d s; isso não diz que não há o que verificar."
                        % (curto(x), workflow, sem_run), "AINDA NAO SEI",
                        "confira se este push aciona o workflow (paths, branch) e repita; não concluí nada sobre o deploy.")
                espera("nenhum run listado ainda", "—")
            else:
                proprio = o_mais_novo(meus)
                alvo_run = proprio.get("databaseId")
                if proprio.get("status") != "completed":
                    espera(proprio.get("status") or "sem status", alvo_run)
                elif proprio.get("conclusion") == "success":
                    fim(0, "✅ no ar — run %s (SHA %s)" % (alvo_run, curto(x)), "NO AR", "siga para o próximo passo da publicação.")
                else:
                    if not ja_redisparou and any(r.get("event") == "workflow_dispatch" for r in meus):
                        ja_redisparou, origem = True, "workflow_dispatch"
                    novos = [r for r in (da_branch or []) if isinstance(r.get("headSha"), str) and r.get("headSha") != x and mais_novo_que(r, proprio)]
                    descendentes, incertos = [], []
                    for r in novos:
                        c = d.contem(r.get("headSha"))
                        if c is True:
                            descendentes.append(r)
                        elif c is None:
                            incertos.append(r)
                    verdes = [r for r in descendentes if r.get("status") == "completed" and r.get("conclusion") == "success"]
                    andando = [r for r in descendentes if r.get("status") != "completed"]
                    conc = proprio.get("conclusion") or "sem conclusão"
                    if verdes:
                        y = o_mais_novo(verdes)
                        fim(0, "✅ no ar via substituto — o run %s do seu SHA %s saiu %s, e o run %s, de %s, que contém o seu, terminou bem."
                            % (alvo_run, curto(x), conc, y.get("databaseId"), curto(y.get("headSha"))), "NO AR",
                            "siga para o próximo passo da publicação.")
                    aguardando_novo = not novos and proprio.get("event") != "workflow_dispatch" and (
                        proprio.get("databaseId") == id_falho or (pela_marca and id_falho is None))
                    if andando:
                        y = o_mais_novo(andando)
                        espera("%s (substituto %s)" % (y.get("status"), curto(y.get("headSha"))), y.get("databaseId"))
                    elif aguardando_novo:
                        if time.time() - repetido_em >= sem_run:
                            fim(4, "⏳ ainda não sei — pedi para repetir o deploy, e o run novo não apareceu em %d s; isso não é falha." % sem_run,
                                "AINDA NAO SEI", "rode de novo para continuar esperando; não repito de novo.")
                        espera("repetido, aguardando o run novo aparecer", alvo_run)
                    elif incertos:
                        y = o_mais_novo(incertos)
                        espera("aguardando o clone conhecer %s para saber se contém o seu" % curto(y.get("headSha")), y.get("databaseId"))
                    elif conc != "failure" and not novos and time.time() - inicio < sem_run:
                        # cancelado por um push mais novo: o run dele pode ainda não estar na lista
                        espera("%s; aguardando um deploy mais novo aparecer" % conc, alvo_run)
                    elif conc != "failure":
                        ruins = [r for r in descendentes if r.get("status") == "completed"]
                        if ruins:
                            y = o_mais_novo(ruins)
                            motivo = "o run %s saiu %s, e o substituto %s (run %s), que contém o seu, terminou %s" % (
                                alvo_run, conc, curto(y.get("headSha")), y.get("databaseId"), y.get("conclusion"))
                        else:
                            motivo = "o run %s saiu %s, e nenhum deploy mais novo contém %s" % (alvo_run, conc, curto(x))
                        fim(2, "🔴 não está no ar — " + motivo, "NAO ESTA NO AR", "abra o run citado; para repetir, um push novo ou gh workflow run na ponta, nunca gh run rerun.")
                    else:
                        passos = d.passos_falhos(alvo_run)
                        real = [q for q in passos if q not in transitorios]
                        passo = (real or passos or [None])[0]
                        trecho = "🔴 falhou — run %s%s" % (alvo_run, ' ("%s")' % passo if passo else "")
                        seta = "abra o run citado; para repetir, um push novo ou gh workflow run na ponta, nunca gh run rerun."
                        if novos:
                            y = o_mais_novo(novos)
                            fim(2, "%s; não repeti: já existe deploy mais novo, de %s (run %s, %s), que não publicou o seu." % (
                                trecho, curto(y.get("headSha")), y.get("databaseId"), y.get("conclusion") or y.get("status")), "FALHOU", seta)
                        if ja_redisparou:
                            fim(2, "%s; não repeti: este commit já foi repetido 1 vez (%s)." % (trecho, origem), "FALHOU", seta)
                        if not transitorios:
                            fim(2, "%s; não repeti: deploy.transient_steps está vazio, e aí eu nunca repito sozinho." % trecho, "FALHOU", seta)
                        if not passos:
                            fim(2, "%s; não repeti: a resposta do GitHub não diz qual passo falhou." % trecho, "FALHOU", seta)
                        if real:
                            fim(2, "%s; não repeti: este passo não está em deploy.transient_steps." % trecho, "FALHOU", seta)
                        ponta = d.ponta()
                        if not ponta:
                            fim(2, "%s; não repeti: não consegui confirmar a ponta de %s (git fetch falhou)." % (trecho, branch), "FALHOU", seta)
                        if ponta != x:
                            fim(2, "%s; não repeti: %s não é mais a ponta de %s (agora %s)." % (trecho, curto(x), branch, curto(ponta)), "FALHOU", seta)
                        if time.time() - inicio >= teto:
                            fim(2, "%s; não repeti: o teto de %d min já passou, e repetir é decisão sua." % (trecho, int(teto / 60)), "FALHOU", seta)
                        # a marca vem antes do disparo: um corte aqui não pode virar uma 2ª repetição
                        if d.marcar():
                            print('🔁 o passo "%s" é passageiro e %s é a ponta: repetindo o deploy na ponta de %s (1 vez).' % (passo, curto(x), branch), file=sys.stderr)
                            try:
                                d.gh("workflow", "run", workflow, "--ref", branch)
                            except ConsultaFalhou as e:
                                if re.search(r"HTTP 4\d\d", str(e)):
                                    d.desmarcar()  # o GitHub respondeu que não: nada foi repetido
                                    fim(2, "%s; tentei repetir e o GitHub recusou: %s. O workflow precisa de workflow_dispatch no on:; sem isso, um push novo." % (trecho, e), "FALHOU", seta)
                                # sem resposta clara, o pedido pode ter chegado: espera o run novo, e não pede de novo
                                print("⚠️ o pedido de repetir não teve resposta clara (%s); não peço de novo." % e, file=sys.stderr)
                        else:
                            print("⏳ outra chamada acabou de repetir este deploy; só espero o run novo.", file=sys.stderr)
                        ja_redisparou, origem, id_falho = True, "este script", alvo_run
                        repetido_em = time.time()
            ultimo_erro = ""
        except ConsultaFalhou as e:
            ultimo_erro = str(e)
            espera("consulta falhou (%s), tentando de novo" % e, alvo_run)
        if time.time() - inicio >= teto:
            fim(4, "⏳ ainda não sei — o deploy não terminou em %d min (run %s); isso não é falha.%s" % (
                int(teto / 60), alvo_run, " Último erro de consulta: %s." % ultimo_erro if ultimo_erro else ""), "AINDA NAO SEI",
                "rode de novo para continuar esperando, ou abra o run citado; nada foi repetido por causa disso.")
        time.sleep(intervalo)


try:
    main()
except subprocess.TimeoutExpired as e:
    print("🛑 deploy-do-sha: um comando passou do tempo: %s" % (e.cmd,), file=sys.stderr)
    print("RESULTADO: AINDA NAO SEI\n→ rode de novo; não concluí nada sobre o deploy.")
    sys.exit(4)
except Exception as e:  # resposta inesperada do gh nunca vira verde nem traceback
    print("🛑 deploy-do-sha: resposta inesperada: %s: %s" % (type(e).__name__, e), file=sys.stderr)
    print("RESULTADO: AINDA NAO SEI\n→ abra o run no GitHub e confira à mão; não concluí nada sobre o deploy.")
    sys.exit(4)
PY
