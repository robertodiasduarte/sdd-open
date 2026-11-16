#!/usr/bin/env python3
"""sessao-claude.py — leitor das sessões do Claude Code de um projeto, para o custo-feature.sh.

Lê os registros locais do agente (um JSONL por sessão em <config>/projects/<raiz com cada caractere fora de
A-Z, a-z e 0-9 trocado por ->/, e os subagentes em <sessão>/subagents/*.jsonl) e devolve SÓ NÚMEROS: horário,
modelo e tokens. Nenhum texto de conversa, caminho de arquivo ou argumento de ferramenta sai daqui: o relatório
que usa esta saída é público em muitos projetos, e o registro lido guarda a conversa inteira.

Uso:
  sessao-claude.py --raiz <pasta do projeto> [--dir <pasta das sessões>]
    --dir: padrão $CLAUDE_CONFIG_DIR/projects/<raiz convertida>, ou ~/.claude/projects/<raiz convertida>
Saída (stdout, uma linha JSON por registro, em ordem de horário):
  {"tipo":"msg","t":"<ISO>","modelo":"<nome ou ?>","entrada":n,"saida":n,"cache_lido":n,"cache_criado":n}
  {"tipo":"turno","t":"<ISO>"}            início de um turno da sessão principal (mensagem de quem usa)
  {"tipo":"ilegivel","n":n}               linhas que não são JSON (por arquivo com problema)
Exit: 0 LIDO · 2 SEM REGISTRO (a pasta não existe ou não tem sessão) · 64 uso

Regras (DESIGN_F23, Decisions 3 e 4): o Claude Code grava uma linha por bloco de conteúdo e repete o `usage` da
mesma mensagem; as linhas são agrupadas por `message.id` (sem id, `requestId`), com o maior valor de cada campo
e o horário da 1ª linha. `entrada` não inclui o cache (no Claude, `input_tokens` já vem sem ele). Subagente conta
mensagens, nunca turnos.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

MODELO_RE = re.compile(r"^[A-Za-z0-9._:/@-]{1,80}\Z")   # \Z: o $ aceitaria "nome\n" (R2 da rodada 4)
CAMPOS = (("entrada", "input_tokens"), ("saida", "output_tokens"),
          ("cache_lido", "cache_read_input_tokens"), ("cache_criado", "cache_creation_input_tokens"))


def uso(motivo):
    print("🛑 sessao-claude: " + motivo, file=sys.stderr)
    print("RESULTADO: PAROU\n→ uso: sessao-claude.py --raiz <pasta do projeto> [--dir <pasta das sessões>]",
          file=sys.stderr)
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


def pasta_padrao(raiz):
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    # realpath: o agente grava o caminho físico (no macOS, /tmp vira /private/tmp; R5 da revisão do código)
    nome = re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(raiz).replace("\\", "/"))
    return os.path.join(base, "projects", nome)


def instante(t):
    """O horário ISO 8601 como datetime em UTC, ou None (horário ilegível não entra na conta)."""
    if not isinstance(t, str) or not t:
        return None
    try:
        d = datetime.fromisoformat(t[:-1] + "+00:00" if t.endswith("Z") else t)
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def modelo_de(valor):
    return valor if isinstance(valor, str) and MODELO_RE.match(valor) else "?"


def numero(v):
    return v if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else 0


def eh_turno(d):
    """Linha `user` da sessão principal escrita por quem usa: tem texto (não só resultado de ferramenta)."""
    if d.get("type") != "user" or d.get("isMeta") or d.get("isSidechain"):
        return False
    c = (d.get("message") or {}).get("content")
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        return any(isinstance(b, dict) and b.get("type") == "text" for b in c)
    return False


def ler(caminho, principal, msgs, turnos, ilegiveis):
    ruins = 0
    try:
        f = open(caminho, encoding="utf-8", errors="replace")
    except OSError:
        ilegiveis.append(1)
        return
    with f:
        for n, linha in enumerate(f, 1):
            linha = linha.strip()
            if not linha:
                continue
            try:
                d = json.loads(linha)
            except ValueError:
                ruins += 1
                continue
            if not isinstance(d, dict):
                ruins += 1
                continue
            t = d.get("timestamp")
            if instante(t) is None:
                continue
            if principal and eh_turno(d):
                turnos.append(t)
            m = d.get("message") if isinstance(d.get("message"), dict) else {}
            if d.get("type") != "assistant" or not isinstance(m.get("usage"), dict):
                continue
            chave = m.get("id") or d.get("requestId") or ("%s:%d" % (caminho, n))
            atual = msgs.get(chave)
            if atual is None:
                atual = msgs[chave] = {"tipo": "msg", "t": t, "modelo": modelo_de(m.get("model")),
                                       "entrada": 0, "saida": 0, "cache_lido": 0, "cache_criado": 0}
            for campo, fonte in CAMPOS:
                v = numero(m["usage"].get(fonte))
                if v > atual[campo]:
                    atual[campo] = v
    if ruins:
        ilegiveis.append(ruins)


def main():
    op = args(sys.argv[1:])
    pasta = op["--dir"] or pasta_padrao(op["--raiz"])
    if not os.path.isdir(pasta):
        print("RESULTADO: SEM REGISTRO\n→ nenhuma sessão do Claude Code para esta pasta.", file=sys.stderr)
        sys.exit(2)
    sessoes = sorted(x for x in os.listdir(pasta) if x.endswith(".jsonl"))
    if not sessoes:
        print("RESULTADO: SEM REGISTRO\n→ nenhuma sessão do Claude Code para esta pasta.", file=sys.stderr)
        sys.exit(2)
    msgs, turnos, ilegiveis = {}, [], []
    for s in sessoes:
        ler(os.path.join(pasta, s), True, msgs, turnos, ilegiveis)
        sub = os.path.join(pasta, s[:-len(".jsonl")], "subagents")
        if os.path.isdir(sub):
            for a in sorted(os.listdir(sub)):
                if a.endswith(".jsonl"):
                    ler(os.path.join(sub, a), False, msgs, turnos, ilegiveis)
    saida = list(msgs.values()) + [{"tipo": "turno", "t": t} for t in turnos]
    saida.sort(key=lambda r: (instante(r["t"]), 0 if r["tipo"] == "turno" else 1))
    for r in saida:
        print(json.dumps(r, ensure_ascii=False, sort_keys=True))
    for n in ilegiveis:
        print(json.dumps({"tipo": "ilegivel", "n": n}, sort_keys=True))
    sys.exit(0)


if __name__ == "__main__":
    # LM-015 (F16W2): no Windows, o stdout num pipe é cp1252 e o print troca \n por \r\n; saída em UTF-8 e \n, sempre.
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    main()
