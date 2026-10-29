#!/usr/bin/env python3
"""deploy-espera-testes.py — o deploy espera os testes? Lido dos workflows do GitHub Actions.

Responde ao campo "O deploy espera os testes?" do bloco do OK da sdd-release. Só lê arquivos de
<raiz>/.github/workflows/; não executa nada do workflow nem acessa a rede.

  SIM            exit 0  todo job que publica roda antes um passo de teste que bloqueia (no mesmo job)
                         ou tem `needs:` num job com esse passo
  NAO            exit 1  algum job publica sem isso: sem teste, ou o teste não segura nada
                         (`continue-on-error`, `|| true`, pipe sem pipefail, `set +e` com `exit 0` no
                         fim, `if: always()` no passo, no job ou num job do meio do `needs:`)
  NAO_SEI        exit 2  workflow_run, workflow reutilizável, workflow que não consegui ler, teste com
                         `if:` ou `set +e`, ou job com nome de publicar cujo passo não reconheci — a
                         skill diz "não consegui afirmar"
  NAO_SE_APLICA  exit 3  nenhum workflow publica (ou não há .github/workflows/)
                 exit 64 uso

Heurística, de propósito conservadora: o que ela não entende vira NAO_SEI, nunca SIM. Só stdlib,
Python >= 3.9. Uso:
    python3 .agents/skills/sdd-release/scripts/deploy-espera-testes.py [raiz]
"""
import os
import re
import sys

# ── mini-parser de YAML (o subconjunto que workflows usam) ───────────────────────────────────
KEY_RE = re.compile(r"""^("[^"]*"|'[^']*'|[^\s:"'#\-][^\s:]*|-[^\s:]+):(?:\s+(.*))?$""")
BLOCO_RE = re.compile(r"^[|>][-+0-9]*$")


class Ilegivel(Exception):
    pass


def sem_comentario(linha):
    q = None
    for i, ch in enumerate(linha):
        if q:
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "#" and (i == 0 or linha[i - 1] in " \t"):
            return linha[:i].rstrip()
    return linha.rstrip()


def escalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        return [escalar(x) for x in v[1:-1].split(",") if x.strip()]
    if v[:1] in ("&", "*"):
        raise Ilegivel("âncora ou alias não suportado")
    return v


class Parser:
    def __init__(self, texto):
        self.raw = [l for l in texto.expandtabs(2).splitlines()]
        self.raw = ["" if l.strip() in ("---", "...") else l for l in self.raw]
        self.i = 0

    def prox(self):
        while self.i < len(self.raw):
            c = sem_comentario(self.raw[self.i])
            if c.strip():
                return len(c) - len(c.lstrip()), c.strip()
            self.i += 1
        return None

    def valor_de_bloco(self, ind_pai):
        nx = self.prox()
        if nx is None or nx[0] < ind_pai:
            return None
        if nx[0] == ind_pai:  # lista no mesmo recuo da chave ("steps:\n- run: x") é válida
            return self.lista(nx[0]) if nx[1] == "-" or nx[1].startswith("- ") else None
        return self.lista(nx[0]) if nx[1] == "-" or nx[1].startswith("- ") else self.mapa(nx[0])

    def texto_de_bloco(self, ind):
        self.i += 1
        linhas = []
        while self.i < len(self.raw):
            r = self.raw[self.i]
            if r.strip() and len(r) - len(r.lstrip()) <= ind:
                break
            linhas.append(r)
            self.i += 1
        margem = min([len(l) - len(l.lstrip()) for l in linhas if l.strip()] or [0])
        return "\n".join(l[margem:] for l in linhas).strip("\n")

    def mapa(self, ind):
        d = {}
        while True:
            nx = self.prox()
            if nx is None or nx[0] < ind or nx[1] == "-" or nx[1].startswith("- "):
                return d
            if nx[0] > ind:
                raise Ilegivel("recuo inesperado na linha %d" % (self.i + 1))
            m = KEY_RE.match(nx[1])
            if not m:
                raise Ilegivel("linha %d não é chave: valor" % (self.i + 1))
            chave, val = escalar(m.group(1)), (m.group(2) or "").strip()
            if chave == "<<":
                raise Ilegivel("merge key não suportado")
            if not val:
                self.i += 1
                d[chave] = self.valor_de_bloco(ind)
            elif BLOCO_RE.match(val):
                d[chave] = self.texto_de_bloco(ind)
            else:
                self.i += 1
                partes = [val]
                while True:  # escalar que continua nas linhas mais recuadas
                    nx = self.prox()
                    if nx is None or nx[0] <= ind:
                        break
                    partes.append(nx[1])
                    self.i += 1
                d[chave] = escalar(" ".join(partes))

    def lista(self, ind):
        out = []
        while True:
            nx = self.prox()
            if nx is None or nx[0] < ind or not (nx[1] == "-" or nx[1].startswith("- ")):
                return out
            if nx[0] > ind:
                raise Ilegivel("recuo inesperado na linha %d" % (self.i + 1))
            resto = nx[1][1:].strip()
            if not resto:
                self.i += 1
                out.append(self.valor_de_bloco(ind + 1))
            elif KEY_RE.match(resto):
                r = self.raw[self.i]
                pos = r.index("-")
                self.raw[self.i] = r[:pos] + " " + r[pos + 1:]  # o item vira um mapa no recuo do conteúdo
                out.append(self.mapa(len(self.raw[self.i]) - len(self.raw[self.i].lstrip())))
            else:
                self.i += 1
                out.append(escalar(resto))


def carregar(texto):
    p = Parser(texto)
    nx = p.prox()
    if nx is None:
        return {}
    d = p.mapa(nx[0])
    if p.prox() is not None:
        raise Ilegivel("conteúdo inesperado na linha %d" % (p.i + 1))
    return d


# ── o que é publicar, testar e segurar ───────────────────────────────────────────────────────
PUBLICA_RUN = re.compile(r"""(?x)(?:^|[\s;&|(])(?:
    rsync\s | scp\s | gh\s+release\s+(?:create|upload)\b | (?:npm|yarn|pnpm)\s+publish\b |
    twine\s+upload\b | cargo\s+publish\b | docker\s+push\b | git\s+push\b | (?:npx\s+)?vercel\b |
    netlify\s+deploy\b | firebase\s+deploy\b | wrangler\s+(?:deploy|publish)\b | fly(?:ctl)?\s+deploy\b |
    supabase\s+(?:functions\s+deploy|db\s+push)\b | kubectl\s+apply\b | helm\s+upgrade\b |
    aws\s+s3\s+sync\b | make\s+deploy\b | (?:npm|yarn|pnpm)\s+run\s+deploy\b | \./deploy)""")
PUBLICA_USES = re.compile(r"deploy|publish|gh-release|gh-pages|release-action|push-action", re.IGNORECASE)
# Instalar a ferramenta de teste não é testar: `pip install pytest` antes do deploy não segura nada.
INSTALA_RE = re.compile(r"""(?x)^(?:sudo\s+)?(?:
    (?:python\d*(?:\.\d+)?\s+-m\s+)?pip\d*\s+install | pipx\s+install | uv\s+(?:pip\s+install|add|sync) |
    poetry\s+(?:add|install) | (?:npm|pnpm|bun)\s+(?:i|install|ci|add)\b | yarn\s+add\b | yarn(?:\s+install)?\s*$ |
    apt(?:-get)?\s+install | brew\s+install | composer\s+(?:require|install) | gem\s+install |
    go\s+install | cargo\s+install | dotnet\s+tool\s+install)""")
# O que vem antes do comando de verdade: atribuição, $( de captura, sudo, npx, "python -B -m", "uv run"…
PREFIXO_RE = re.compile(r"""(?x)^(?:
    \w+=["']?\$\(\s* | \$\(\s* | \w+=\S*\s+ | env\s+ | sudo\s+ | time\s+ | xvfb-run(?:\s+-a)?\s+ |
    npx\s+ | bunx\s+ | (?:uv|poetry|pipenv|pdm|hatch)\s+run\s+ | bundle\s+exec\s+ |
    python\d*(?:\.\d+)?(?:\s+-[A-Za-z]+)*\s+-m\s+ )""")
FERRAMENTAS = {"pytest", "unittest", "jest", "vitest", "mocha", "phpunit", "rspec", "tox", "nox", "ctest"}
PAR_TESTE = re.compile(r"""(?x)^(?:(?:npm|yarn|pnpm|bun)\s+(?:run\s+)?test | (?:go|cargo|deno|dotnet|mvn|gradle|mix)\s+test |
    make\s+test | (?:\./)?gradlew\s+test)(?:\s|\)|$)""")
ENGOLE_RE = re.compile(r"\|\|\s*(?:true\b|:|exit\s+0\b|echo\b)")
PIPE_RE = re.compile(r"(?<!\|)\|(?!\|)")
SEMPRE_RE = re.compile(r"always\(\)|failure\(\)|!\s*cancelled\(\)")
IF_INOFENSIVO = re.compile(r"^\s*(?:\$\{\{\s*)?(?:always|success)\(\)\s*(?:\}\})?\s*$")
PARECE_PUBLICAR = re.compile(r"(?:deploy|publish|release)(?![\s_-]?(?:gate|check|lint|notes|drafter))", re.IGNORECASE)
NAO_PUBLICA_A_MAIN = {"pull_request", "pull_request_target", "workflow_call"}


def linhas_de_comando(run):
    """Linhas de run: que executam algo (sem echo/printf/comentário, que só falam de deploy)."""
    return [l.strip() for l in str(run or "").splitlines()
            if l.strip() and not re.match(r"^(?:echo|printf|#)\b|^#", l.strip())]


def comando_de_teste(linha):
    """True se algum comando da linha (entre && ; || |) É a ferramenta de teste — citá-la não conta."""
    if INSTALA_RE.match(linha):
        return False
    for seg in re.split(r"&&|\|\||;|\|", linha):
        s = seg.strip()
        m = PREFIXO_RE.match(s)
        while m and m.end():
            s = s[m.end():]
            m = PREFIXO_RE.match(s)
        if not s:
            continue
        if PAR_TESTE.match(s) or os.path.basename(s.split()[0]).strip("\"')") in FERRAMENTAS:
            return True
    return False


def verdade(v):
    return v is not None and str(v).strip().lower() not in ("false", "")


def nome_do_passo(st):
    if not isinstance(st, dict):
        return str(st)
    if st.get("name"):
        return str(st["name"])
    if st.get("uses"):
        return str(st["uses"])
    linhas = linhas_de_comando(st.get("run"))
    return linhas[0][:60] if linhas else "?"


def publica(st):
    if not isinstance(st, dict):
        return False
    if st.get("uses") and PUBLICA_USES.search(str(st["uses"])):
        return True
    return any(PUBLICA_RUN.search(l) for l in linhas_de_comando(st.get("run")))


def e_teste(st):
    return isinstance(st, dict) and any(comando_de_teste(l) for l in linhas_de_comando(st.get("run")))


def shell_de(st, job, shell_wf):
    d = job.get("defaults") if isinstance(job.get("defaults"), dict) else {}
    r = d.get("run") if isinstance(d.get("run"), dict) else {}
    return str(st.get("shell") or r.get("shell") or shell_wf or "")


def seguranca(st, job, shell_wf):
    """(None, "") = o teste vermelho para o job; ("NAO"|"NAO_SEI", motivo) = não dá para contar com ele."""
    if verdade(job.get("continue-on-error")):
        return "NAO", "o job tem continue-on-error"
    if verdade(st.get("continue-on-error")):
        return "NAO", "continue-on-error: %s" % st.get("continue-on-error")
    run = str(st.get("run") or "")
    testes = [l for l in linhas_de_comando(run) if comando_de_teste(l)]
    for l in testes:
        if ENGOLE_RE.search(l):
            return "NAO", "o comando de teste termina em `%s`" % ENGOLE_RE.search(l).group(0)
    # shell padrão do Actions é `bash -e {0}`, sem pipefail: `pytest | tee` vale o código do tee
    if any(PIPE_RE.search(l) for l in testes) and shell_de(st, job, shell_wf).strip() != "bash" \
            and "pipefail" not in run:
        return "NAO", "o teste passa por um pipe (|) sem pipefail: vale o código do último comando"
    linhas = [l.strip() for l in run.splitlines() if l.strip()]
    if re.search(r"\bset\s+[-+a-z]*\+e", run):
        if linhas and linhas[-1] == "exit 0":
            return "NAO", "roda com set +e e termina em exit 0"
        return "NAO_SEI", "roda com set +e: o código do teste pode não chegar ao fim do passo"
    cond = str(st.get("if") or "")
    if cond and not IF_INOFENSIVO.match(cond):
        return "NAO_SEI", "só roda com if: %s" % cond
    return None, ""


def passos(job):
    st = job.get("steps")
    return [s for s in st if isinstance(s, dict)] if isinstance(st, list) else []


def needs(job):
    n = job.get("needs")
    if isinstance(n, list):
        return [str(x) for x in n]
    return [str(n)] if n else []


def gatilhos(wf):
    on = wf.get("on", wf.get("true"))
    if isinstance(on, dict):
        return set(on)
    if isinstance(on, list):
        return set(str(x) for x in on)
    return {str(on)} if on else set()


def avaliar_job(arq, jid, job, jobs, wf_run, shell_wf):
    """('SIM'|'NAO'|'NAO_SEI', frase) para um job que publica."""
    rotulo = "%s · job %s" % (arq, jid)
    sts = passos(job)
    pubs = [i for i, s in enumerate(sts) if publica(s)]
    pub = sts[pubs[0]]
    if wf_run:
        return "NAO_SEI", "%s roda por workflow_run: o teste está em outro workflow que não leio daqui" % rotulo
    # if: always() em QUALQUER passo que publica o faz rodar com teste vermelho
    sempre = ["o passo '%s' publica com if: %s" % (nome_do_passo(sts[i]), sts[i].get("if"))
              for i in pubs if SEMPRE_RE.search(str(sts[i].get("if") or ""))]
    seguro, nao, nao_sei = None, [], []

    def pesa(s, dono, de_quem):
        nivel, motivo = seguranca(s, dono, shell_wf)
        if nivel:
            (nao if nivel == "NAO" else nao_sei).append("o passo '%s'%s não segura: %s" % (nome_do_passo(s), de_quem, motivo))
        return nivel is None

    for s in sts[:pubs[0]]:
        if e_teste(s) and pesa(s, job, "") and not seguro:
            seguro = "o passo '%s' testa antes de '%s'" % (nome_do_passo(s), nome_do_passo(pub))
    if not seguro:
        if SEMPRE_RE.search(str(job.get("if") or "")):
            sempre.append("o job publica com if: %s" % job.get("if"))
        vistos, fila = set(), needs(job)
        while fila and not seguro:  # needs transitivo
            dep = fila.pop(0)
            if dep in vistos:
                continue
            vistos.add(dep)
            dj = jobs.get(dep)
            if not isinstance(dj, dict):
                nao_sei.append("needs: %s não existe neste workflow" % dep)
                continue
            if dj.get("uses"):
                nao_sei.append("needs: %s chama o workflow reutilizável %s" % (dep, dj.get("uses")))
                continue
            for s in passos(dj):
                if e_teste(s) and pesa(s, dj, " do job " + dep):
                    seguro = "needs: %s, que testa no passo '%s'" % (dep, nome_do_passo(s))
                    break
            if not seguro and SEMPRE_RE.search(str(dj.get("if") or "")):
                sempre.append("needs: %s roda com if: %s — segue mesmo com teste vermelho antes dele" % (dep, dj.get("if")))
            elif not seguro:
                fila.extend(needs(dj))
    if sempre:
        return "NAO", "%s publica mesmo com teste vermelho: %s" % (rotulo, "; ".join(sempre))
    if seguro:
        return "SIM", "%s: %s" % (rotulo, seguro)
    if nao:
        return "NAO", "%s publica (passo '%s'), mas %s" % (rotulo, nome_do_passo(pub), "; ".join(nao))
    if nao_sei:
        return "NAO_SEI", "%s: %s" % (rotulo, "; ".join(nao_sei))
    parecidos = [nome_do_passo(s) for s in sts[:pubs[0]] if re.search(r"test", nome_do_passo(s), re.IGNORECASE)]
    if parecidos:
        return "NAO_SEI", "%s: o passo '%s' parece teste, mas não reconheci o comando" % (rotulo, parecidos[0])
    return "NAO", "%s publica (passo '%s') sem passo de teste antes e sem needs: num job com teste" % (
        rotulo, nome_do_passo(pub))


def avaliar(raiz):
    pasta = os.path.join(raiz, ".github", "workflows")
    arqs = sorted(f for f in os.listdir(pasta) if f.endswith((".yml", ".yaml"))) if os.path.isdir(pasta) else []
    achados = []
    for arq in arqs:
        try:
            with open(os.path.join(pasta, arq), encoding="utf-8", errors="replace") as fh:
                wf = carregar(fh.read())
        except (Ilegivel, OSError) as e:
            achados.append(("NAO_SEI", "não consegui ler %s (%s)" % (arq, e)))
            continue
        if not isinstance(wf, dict):
            achados.append(("NAO_SEI", "não consegui ler %s" % arq))
            continue
        g = gatilhos(wf)
        if g and not (g - NAO_PUBLICA_A_MAIN):
            continue  # só PR ou só chamado por outro workflow (quem chama é que é avaliado)
        jobs = wf.get("jobs") if isinstance(wf.get("jobs"), dict) else {}
        d = wf.get("defaults") if isinstance(wf.get("defaults"), dict) else {}
        shell_wf = d.get("run", {}).get("shell") if isinstance(d.get("run"), dict) else None
        reconhecidos, suspeitos = 0, []
        for jid, job in jobs.items():
            if not isinstance(job, dict):
                continue
            if job.get("uses"):
                achados.append(("NAO_SEI", "%s · job %s chama o workflow reutilizável %s: não leio o que ele faz"
                                % (arq, jid, job["uses"])))
            elif any(publica(s) for s in passos(job)):
                reconhecidos += 1
                achados.append(avaliar_job(arq, jid, job, jobs, "workflow_run" in g, shell_wf))
            elif any(PARECE_PUBLICAR.search(n) for n in (jid, str(job.get("name") or ""))):
                suspeitos.append(jid)
        if not reconhecidos and not suspeitos and PARECE_PUBLICAR.search(arq + " " + str(wf.get("name") or "")):
            suspeitos.append("(nenhum)" if not jobs else ", ".join(jobs))
        for jid in suspeitos:  # nome de publicar sem passo reconhecido: não dá para dizer SIM por cima dele
            achados.append(("NAO_SEI", "%s · job %s: o nome fala em publicar, mas não reconheci o passo que publica"
                            % (arq, jid)))
    for res in ("NAO", "NAO_SEI"):
        sel = [f for r, f in achados if r == res]
        if sel:
            return res, sel, achados
    if achados:
        return "SIM", [f for _, f in achados], achados
    return "NAO_SE_APLICA", [], []


def main(argv):
    if len(argv) > 2 or (len(argv) == 2 and argv[1] in ("-h", "--help")):
        print("uso: deploy-espera-testes.py [raiz do projeto]", file=sys.stderr)
        return 64
    raiz = argv[1] if len(argv) == 2 else "."
    if not os.path.isdir(raiz):
        print("🛑 %s não é uma pasta" % raiz, file=sys.stderr)
        print("uso: deploy-espera-testes.py [raiz do projeto]", file=sys.stderr)
        return 64
    res, frases, todos = avaliar(raiz)
    for r, f in todos:
        print({"SIM": "✅", "NAO": "🛑", "NAO_SEI": "❓"}[r] + " " + f)
    detalhe = "; ".join(frases)
    if res == "SIM":
        resposta = "sim — " + detalhe
    elif res == "NAO":
        resposta = "não — " + detalhe + ": um teste vermelho não impede a publicação"
    elif res == "NAO_SEI":
        resposta = "não consegui afirmar — " + detalhe
    else:
        resposta = "não se aplica: nenhum workflow em .github/workflows/ publica"
    print("RESULTADO: " + res)
    print("→ O deploy espera os testes? " + resposta)
    return {"SIM": 0, "NAO": 1, "NAO_SEI": 2, "NAO_SE_APLICA": 3}[res]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
