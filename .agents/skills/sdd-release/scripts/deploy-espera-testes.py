#!/usr/bin/env python3
"""deploy-espera-testes.py — o deploy espera os testes? Lido dos workflows do GitHub Actions.

Responde ao campo "O deploy espera os testes?" do bloco do OK da sdd-release. Só lê arquivos de
<raiz>/.github/workflows/; não executa nada do workflow nem acessa a rede.

  SIM            exit 0  todo job que publica roda antes um passo de teste que bloqueia (no mesmo job)
                         ou tem `needs:` num job com esse passo
  NAO            exit 1  algum job publica sem isso: sem teste, ou o teste não segura nada
                         (`continue-on-error`, `|| true`, `set +e` com `exit 0` no fim, `if: always()`)
  NAO_SEI        exit 2  workflow_run, workflow reutilizável, workflow que não consegui ler, ou
                         publicação/teste que não reconheci — a skill diz "não consegui afirmar"
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
PUBLICA_USES = re.compile(r"deploy|publish|gh-release|gh-pages|release-action", re.IGNORECASE)
TESTE_RUN = re.compile(r"""(?x)(?:^|[\s;&|(/])(?:
    pytest | unittest | jest | vitest | mocha | phpunit | rspec | tox | ctest |
    (?:npm|yarn|pnpm|bun)\s+(?:run\s+)?test | (?:go|cargo|deno|dotnet|mvn|gradle|mix)\s+test |
    make\s+test | (?:\./)?gradlew\s+test)\b""")
ENGOLE_RE = re.compile(r"\|\|\s*(?:true\b|:|exit\s+0\b|echo\b)")
SEMPRE_RE = re.compile(r"always\(\)|failure\(\)|!\s*cancelled\(\)")
PARECE_PUBLICAR = re.compile(r"deploy|publish|release", re.IGNORECASE)
SO_PR = {"pull_request", "pull_request_target"}


def linhas_de_comando(run):
    """Linhas de run: que executam algo (sem echo/printf/comentário, que só falam de deploy)."""
    return [l.strip() for l in str(run or "").splitlines()
            if l.strip() and not re.match(r"^(?:echo|printf|#)\b|^#", l.strip())]


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
    return isinstance(st, dict) and any(TESTE_RUN.search(l) for l in linhas_de_comando(st.get("run")))


def por_que_nao_segura(st, job):
    """None = o passo de teste vermelho para o job; senão, o motivo."""
    if verdade(job.get("continue-on-error")):
        return "o job tem continue-on-error"
    if verdade(st.get("continue-on-error")):
        return "continue-on-error: %s" % st.get("continue-on-error")
    run = str(st.get("run") or "")
    for l in linhas_de_comando(run):
        if TESTE_RUN.search(l) and ENGOLE_RE.search(l):
            return "o comando de teste termina em `%s`" % ENGOLE_RE.search(l).group(0)
    linhas = [l.strip() for l in run.splitlines() if l.strip()]
    if re.search(r"\bset\s+[-+a-z]*\+e", run) and linhas and linhas[-1] == "exit 0":
        return "roda com set +e e termina em exit 0"
    return None


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


def avaliar_job(arq, jid, job, jobs, wf_run):
    """('SIM'|'NAO'|'NAO_SEI', frase) para um job que publica."""
    rotulo = "%s · job %s" % (arq, jid)
    sts = passos(job)
    i_pub = next(i for i, s in enumerate(sts) if publica(s))
    pub = sts[i_pub]
    if wf_run:
        return "NAO_SEI", "%s roda por workflow_run: o teste está em outro workflow que não leio daqui" % rotulo
    antes = [s for s in sts[:i_pub] if e_teste(s)]
    seguros = [s for s in antes if not por_que_nao_segura(s, job)]
    if seguros and not SEMPRE_RE.search(str(pub.get("if") or "")):
        return "SIM", "%s: o passo '%s' testa antes de '%s'" % (rotulo, nome_do_passo(seguros[0]), nome_do_passo(pub))
    if SEMPRE_RE.search(str(job.get("if") or "")):
        return "NAO", "%s publica com if: %s — roda mesmo com teste vermelho" % (rotulo, job.get("if"))
    # needs (transitivo)
    vistos, fila, problemas, nao_sei = set(), needs(job), [], []
    while fila:
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
        for s in passos(dj):
            if e_teste(s):
                motivo = por_que_nao_segura(s, dj)
                if not motivo:
                    return "SIM", "%s: needs: %s, que testa no passo '%s'" % (rotulo, dep, nome_do_passo(s))
                problemas.append("o passo '%s' do job %s não segura: %s" % (nome_do_passo(s), dep, motivo))
        fila.extend(needs(dj))
    for s in antes:
        problemas.append("o passo '%s' não segura: %s" % (nome_do_passo(s), por_que_nao_segura(s, job)))
    if seguros:  # havia teste que segura, mas o passo que publica tem if: always()
        problemas.append("o passo '%s' publica com if: %s" % (nome_do_passo(pub), pub.get("if")))
    if problemas:
        return "NAO", "%s publica (passo '%s'), mas %s" % (rotulo, nome_do_passo(pub), "; ".join(problemas))
    if nao_sei:
        return "NAO_SEI", "%s: %s" % (rotulo, "; ".join(nao_sei))
    parecidos = [nome_do_passo(s) for s in sts[:i_pub] if re.search(r"test", nome_do_passo(s), re.IGNORECASE)]
    if parecidos:
        return "NAO_SEI", "%s: o passo '%s' parece teste, mas não reconheci o comando" % (rotulo, parecidos[0])
    return "NAO", "%s publica (passo '%s') sem passo de teste antes e sem needs: num job com teste" % (
        rotulo, nome_do_passo(pub))


def avaliar(raiz):
    pasta = os.path.join(raiz, ".github", "workflows")
    arqs = sorted(f for f in os.listdir(pasta) if f.endswith((".yml", ".yaml"))) if os.path.isdir(pasta) else []
    achados, suspeitos = [], []
    for arq in arqs:
        try:
            wf = carregar(open(os.path.join(pasta, arq), encoding="utf-8", errors="replace").read())
        except Ilegivel as e:
            achados.append(("NAO_SEI", "não consegui ler %s (%s)" % (arq, e)))
            continue
        if not isinstance(wf, dict):
            achados.append(("NAO_SEI", "não consegui ler %s" % arq))
            continue
        g = gatilhos(wf)
        if g and not (g - SO_PR):
            continue  # só roda em pull request: não publica a branch padrão
        jobs = wf.get("jobs") if isinstance(wf.get("jobs"), dict) else {}
        nomes = [arq, str(wf.get("name") or "")]
        for jid, job in jobs.items():
            if not isinstance(job, dict):
                continue
            nomes += [jid, str(job.get("name") or "")] + [nome_do_passo(s) for s in passos(job)]
            if job.get("uses"):
                achados.append(("NAO_SEI", "%s · job %s chama o workflow reutilizável %s: não leio o que ele faz"
                                 % (arq, jid, job["uses"])))
            elif any(publica(s) for s in passos(job)):
                achados.append(avaliar_job(arq, jid, job, jobs, "workflow_run" in g))
        if any(PARECE_PUBLICAR.search(n) for n in nomes):
            suspeitos.append(arq)
    for res in ("NAO", "NAO_SEI"):
        sel = [f for r, f in achados if r == res]
        if sel:
            return res, sel, achados
    if achados:
        return "SIM", [f for _, f in achados], achados
    if suspeitos:
        frase = "o nome de %s fala em publicar, mas não reconheci nenhum passo que publica" % ", ".join(suspeitos)
        return "NAO_SEI", [frase], [("NAO_SEI", frase)]
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
