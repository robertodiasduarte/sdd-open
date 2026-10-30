#!/usr/bin/env python3
"""sdd-avaliador-guard.py — guard do Claude Code (PreToolUse em Agent|Task), gerado pelo sdd-open.

O avaliador de contexto fresco só é despachado com a árvore COMMITADA: ele usa o terminal para provar
os critérios e pode restaurar arquivos do último commit — trabalho não commitado se perde. O open não
tem nome fixo de subagente para o avaliador; o sinal é a palavra "veredito" no brief que a sdd-build
manda (modo `veredito`). Com ela no prompt ou na descrição, este guard chama
`bash sdd/bin/avaliador-guard.sh` do projeto: exit 1 ⇒ nega o despacho com a lista de caminhos sujos e
o comando de commit; exit 0 ⇒ silêncio (um ⚠️ do script, como o bypass SDD_AVALIADOR_GUARD=off, vira
systemMessage); exit 2/64 ou erro interno ⇒ aviso "não conferido" e o despacho segue (falha aberta).

Fonte: bin/adapters/claude/ do pacote sdd-open; a cópia em .claude/hooks/ é regenerada pelo sync.
Python >= 3.9, só stdlib.
"""
import json
import os
import subprocess
import sys


def emitir(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def aviso(msg):
    emitir({"systemMessage": "⚠️ sdd-open: " + msg})


def negar(motivo):
    emitir({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": motivo,
    }})


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        aviso("payload do hook ilegível (%s) — despacho não conferido" % type(exc).__name__)
        return
    if payload.get("tool_name", "") not in ("Agent", "Task"):
        return
    entrada = payload.get("tool_input") or {}
    texto = "%s %s" % (entrada.get("prompt", ""), entrada.get("description", ""))
    if "veredito" not in texto.lower():
        return
    projeto = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    guard = os.path.join(projeto, "sdd", "bin", "avaliador-guard.sh")
    if not os.path.isfile(guard):
        aviso("sdd/bin/avaliador-guard.sh não encontrado em %s — despacho não conferido (rode init)" % projeto)
        return
    r = subprocess.run(["bash", guard], capture_output=True, text=True, cwd=projeto)
    saida = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        if "⚠️" in saida:
            emitir({"systemMessage": "⚠️ sdd-open: " + saida})
        return
    if r.returncode == 1:
        negar("🛑 sdd-open: despacho do avaliador negado — há trabalho não commitado:\n%s" % saida)
        return
    aviso("avaliador-guard.sh saiu %d — despacho não conferido" % r.returncode)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # falha aberta: hook quebrado não trava o despacho
        aviso("erro interno do guard (%s: %s) — despacho não conferido" % (type(exc).__name__, exc))
    sys.exit(0)
