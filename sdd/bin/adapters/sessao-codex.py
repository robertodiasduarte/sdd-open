#!/usr/bin/env python3
"""sessao-codex.py — leitor das sessões do Codex de um projeto, para o custo-feature.sh.

Lê os registros locais do agente (<codex>/sessions/AAAA/MM/DD/rollout-*.jsonl) e usa só as sessões cuja pasta de
trabalho (`session_meta.cwd`) é a raiz pedida: a revisão adversarial roda o codex numa pasta temporária vazia, e
por isso a sessão dela nunca entra aqui (o custo da revisão vem dos META.txt). Devolve SÓ NÚMEROS: horário,
modelo e tokens. Nenhum texto de conversa, caminho de arquivo ou argumento de ferramenta sai daqui.

Uso:
  sessao-codex.py --raiz <pasta do projeto> [--dir <pasta sessions>]
    --dir: padrão $CODEX_HOME/sessions, ou ~/.codex/sessions
Saída (stdout, uma linha JSON por registro, em ordem de horário):
  {"tipo":"msg","t":"<ISO>","modelo":"<nome ou ?>","entrada":n,"saida":n,"cache_lido":n,"cache_criado":n}
  {"tipo":"turno","t":"<ISO>"}            início de um turno (evento task_started)
  {"tipo":"ilegivel","n":n}               linhas que não são JSON (por arquivo com problema)
Exit: 0 LIDO · 2 SEM REGISTRO (nenhuma sessão com esta pasta de trabalho) · 64 uso

Regras (DESIGN_F23, Decision 3): o evento token_count traz o total acumulado da sessão e pode se repetir; cada
mensagem é a diferença entre dois totais consecutivos (diferença zero é descartada). No Codex, `input_tokens`
inclui `cached_input_tokens`: entrada = input − cached; cache_lido = cached; cache_criado =
cache_write_input_tokens. O modelo é o do turn_context mais recente.
"""
import sys as _sdd_sys  # LM-015: saída em UTF-8 e "\n" também no Windows

for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass

import json
import os
import re
import sys
from datetime import datetime, timezone

MODELO_RE = re.compile(r"^[A-Za-z0-9._:/@-]{1,80}$")
CHAVES = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens")


def uso(motivo):
    print("🛑 sessao-codex: " + motivo, file=sys.stderr)
    print("RESULTADO: PAROU\n→ uso: sessao-codex.py --raiz <pasta do projeto> [--dir <pasta sessions>]", file=sys.stderr)
    sys.exit(64)


def args(argv):
    op = {"--raiz": None, "--dir": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__.strip())
            sys.exit(0)
        if a not in op or i + 1 >= len(argv):
            uso("argumento desconhecido ou sem valor: %s" % a)
        op[a] = argv[i + 1]
        i += 2
    if not op["--raiz"]:
        uso("falta --raiz")
    return op


def instante(t):
    if not isinstance(t, str) or not t:
        return None
    try:
        d = datetime.fromisoformat(t[:-1] + "+00:00" if t.endswith("Z") else t)
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def mesma_pasta(a, b):
    def norm(p):
        return os.path.normcase(os.path.realpath(p.replace("\\", "/"))).rstrip("/\\")   # caminho físico (R5)
    return isinstance(a, str) and bool(a) and norm(a) == norm(b)


def numero(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else 0


def ler(caminho, raiz, saida, ilegiveis):
    linhas, ruins = [], 0
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            for linha in f:
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    d = json.loads(linha)
                except ValueError:
                    ruins += 1
                    continue
                if isinstance(d, dict):
                    linhas.append(d)
                else:
                    ruins += 1
    except OSError:
        ilegiveis.append(1)
        return False
    meta = next((d for d in linhas if d.get("type") == "session_meta"), None)
    if meta is None or not mesma_pasta((meta.get("payload") or {}).get("cwd"), raiz):
        return False
    if ruins:
        ilegiveis.append(ruins)
    modelo, antes = "?", dict.fromkeys(CHAVES, 0)
    for d in linhas:
        p = d.get("payload") if isinstance(d.get("payload"), dict) else {}
        t = d.get("timestamp")
        if d.get("type") == "turn_context":
            m = p.get("model")
            modelo = m if isinstance(m, str) and MODELO_RE.match(m) else "?"
            continue
        if d.get("type") != "event_msg" or instante(t) is None:
            continue
        if p.get("type") == "task_started":
            saida.append({"tipo": "turno", "t": t})
        elif p.get("type") == "token_count":
            total = ((p.get("info") or {}).get("total_token_usage")) if isinstance(p.get("info"), dict) else None
            if not isinstance(total, dict):
                continue
            agora = {k: numero(total.get(k)) for k in CHAVES}
            delta = {k: agora[k] - antes[k] for k in CHAVES}
            if any(v < 0 for v in delta.values()):   # total que voltou atrás: recomeça a contagem daqui
                antes = agora
                continue
            antes = agora
            if not any(delta.values()):
                continue
            lido = min(delta["cached_input_tokens"], delta["input_tokens"])
            saida.append({"tipo": "msg", "t": t, "modelo": modelo,
                          "entrada": delta["input_tokens"] - lido, "saida": delta["output_tokens"],
                          "cache_lido": lido, "cache_criado": delta["cache_write_input_tokens"]})
    return True


def main():
    op = args(sys.argv[1:])
    base = op["--dir"] or os.path.join(os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex"),
                                       "sessions")
    arquivos = []
    if os.path.isdir(base):
        for d, _, nomes in os.walk(base):
            arquivos += [os.path.join(d, n) for n in nomes if n.startswith("rollout-") and n.endswith(".jsonl")]
    saida, ilegiveis, achou = [], [], False
    for a in sorted(arquivos):
        achou = ler(a, op["--raiz"], saida, ilegiveis) or achou
    if not achou:
        print("RESULTADO: SEM REGISTRO\n→ nenhuma sessão do Codex com esta pasta de trabalho.", file=sys.stderr)
        sys.exit(2)
    saida.sort(key=lambda r: (instante(r["t"]), 0 if r["tipo"] == "turno" else 1))
    for r in saida:
        print(json.dumps(r, ensure_ascii=False, sort_keys=True))
    for n in ilegiveis:
        print(json.dumps({"tipo": "ilegivel", "n": n}, sort_keys=True))
    sys.exit(0)


if __name__ == "__main__":
    main()
