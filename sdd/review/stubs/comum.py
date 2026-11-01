"""comum.py — fila de cenários e tabela dos stubs de engine do gate offline (sdd/bin/adversarial-review-gate.sh).

Cada stub (<engine>.py) imita a saída de UMA engine no formato dela. Quem pode ser chamado é a fila
SDD_STUB_<ENGINE> (ex.: SDD_STUB_CODEX=429,revisor): uma entrada por chamada, a última se repete. O estado de
cada chamada fica em SDD_STUB_ESTADO: <engine>.n (contador), <engine>.<n>.argv e <engine>.<n>.entrada.
Engine sem fila = chamada que o teste não previa: o nome vai para SDD_STUB_ESTADO/sentinela e o stub falha.
Nunca usa rede (o openrouter.py só escuta em 127.0.0.1). Python 3.9 stdlib.
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
COLUNAS = ("engine", "cenario", "resposta", "modelo", "custo", "tokens_entrada", "tokens_saida", "status", "falha",
           "fonte")


def cenarios():
    tab = {}
    with open(os.path.join(AQUI, "cenarios.tsv"), encoding="utf-8") as h:
        for ln in h:
            ln = ln.rstrip("\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            c = dict(zip(COLUNAS, ln.split("\t")))
            tab[(c["engine"], c["cenario"])] = c
    return tab


def proximo(engine, argv=(), entrada=b""):
    """Registra a chamada e devolve (n, cenário) — ou (n, None) quando a engine não tem fila (sentinela)."""
    est = os.environ.get("SDD_STUB_ESTADO") or ""
    fila = [c.strip() for c in (os.environ.get("SDD_STUB_" + engine.upper()) or "").split(",") if c.strip()]
    if not est:
        return 0, None
    os.makedirs(est, exist_ok=True)
    arq = os.path.join(est, engine + ".n")
    n = int(open(arq).read() or "0") + 1 if os.path.exists(arq) else 1
    with open(arq, "w") as h:
        h.write(str(n))
    with open(os.path.join(est, "%s.%d.argv" % (engine, n)), "w", encoding="utf-8") as h:
        h.write("\n".join(argv) + "\n")
    with open(os.path.join(est, "%s.%d.entrada" % (engine, n)), "wb") as h:
        h.write(entrada)
    if not fila:
        with open(os.path.join(est, "sentinela"), "a", encoding="utf-8") as h:
            h.write(engine + "\n")
        return n, None
    nome = fila[min(n, len(fila)) - 1]
    c = cenarios().get((engine, nome))
    if c is None:
        with open(os.path.join(est, "sentinela"), "a", encoding="utf-8") as h:
            h.write("%s (cenário desconhecido: %s)\n" % (engine, nome))
    return n, c


def texto(c):
    with open(os.path.join(AQUI, "respostas", c["resposta"]), encoding="utf-8") as h:
        return h.read()


def num(v):
    return None if v in ("", "-") else int(v)


def custo(v):
    return None if v in ("", "-") else float(v)
