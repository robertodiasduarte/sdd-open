#!/usr/bin/env python3
"""sdd-report-guard.py — guard do Claude Code (PreToolUse em Write|Edit|MultiEdit), gerado pelo sdd-open.

Antes de o agente gravar um BUILD_REPORT_*.md, simula o conteúdo final (Write: o content; Edit e
MultiEdit: aplica old_string → new_string ao arquivo atual) e o passa pelo sdd/bin/report-lint.py
--stdin do projeto. Exit 1 do lint ⇒ nega a gravação, com a saída do lint como razão. Exit 0 ⇒ silêncio.

Falha ABERTA, mas avisa: payload ilegível, lint ausente, exit ≥ 64 ou erro interno viram um
systemMessage "⚠️ sdd-open: … não conferido" e a escrita segue — um hook quebrado não pode travar o
agente; a verdade final é o report-lint da fase Release e o CI (docs/hooks.md). As fixtures de
sdd/fixtures/ (exemplos do que o lint nega) ficam fora. SDD_REPORT_GUARD=off desliga, com aviso
(declare no BUILD_REPORT).

Fonte: bin/adapters/claude/ do pacote sdd-open; a cópia em .claude/hooks/ é regenerada pelo sync.
Python >= 3.9, só stdlib.
"""
import json
import os
import re
import subprocess
import sys

REPORT_RE = re.compile(r"^BUILD_REPORT_.+\.md$")


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


def em_fixtures(caminho):
    """Fixtures (exemplos do que o lint nega) e o molde de sdd/templates/ não são relatórios."""
    normal = "/" + os.path.normpath(caminho).replace(os.sep, "/").strip("/") + "/"
    return "/sdd/fixtures/" in normal or "/sdd/templates/" in normal


def conteudo_resultante(tool, entrada, caminho):
    """O conteúdo que o arquivo TERÁ se a ferramenta rodar; None = a ferramenta não gravaria nada."""
    if tool == "Write":
        return entrada.get("content", "") or ""
    try:
        with open(caminho, encoding="utf-8") as fh:
            atual = fh.read()
    except OSError:
        return None  # Edit em arquivo inexistente falha na própria ferramenta: nada a conferir
    edits = entrada.get("edits") or [entrada]
    for e in edits:
        old, new = e.get("old_string", ""), e.get("new_string", "")
        if not old or old not in atual:
            return None  # a ferramenta devolve erro e não grava: não negar um fantasma
        atual = atual.replace(old, new) if e.get("replace_all") else atual.replace(old, new, 1)
    return atual


def main():
    if os.environ.get("SDD_REPORT_GUARD", "").lower() == "off":
        aviso("guard do BUILD_REPORT desligado (SDD_REPORT_GUARD=off) — declare isso no BUILD_REPORT")
        return
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:  # nunca em silêncio
        aviso("payload do hook ilegível (%s) — BUILD_REPORT não conferido" % type(exc).__name__)
        return
    tool = payload.get("tool_name", "")
    entrada = payload.get("tool_input") or {}
    caminho = entrada.get("file_path") or ""
    if tool not in ("Write", "Edit", "MultiEdit") or not REPORT_RE.match(os.path.basename(caminho)):
        return
    if em_fixtures(caminho):
        return
    projeto = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    lint = os.path.join(projeto, "sdd", "bin", "report-lint.py")
    if not os.path.isfile(lint):
        aviso("sdd/bin/report-lint.py não encontrado em %s — BUILD_REPORT não conferido (rode init)" % projeto)
        return
    conteudo = conteudo_resultante(tool, entrada, caminho)
    if conteudo is None:
        return
    r = subprocess.run([sys.executable or "python3", "-B", lint, "--stdin", caminho],
                       input=conteudo, capture_output=True, text=True, cwd=projeto)
    saida = (r.stdout + r.stderr).strip()
    if r.returncode == 0:
        return
    nome = os.path.basename(caminho)
    if r.returncode == 1:
        negar("🛑 sdd-open: gravação de %s negada — o relatório não passa no report-lint:\n%s" % (nome, saida))
        return
    aviso("report-lint saiu %d em %s — BUILD_REPORT não conferido" % (r.returncode, nome))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # falha aberta: hook quebrado não trava a escrita
        aviso("erro interno do guard (%s: %s) — BUILD_REPORT não conferido" % (type(exc).__name__, exc))
    sys.exit(0)
