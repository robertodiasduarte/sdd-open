#!/usr/bin/env python3
"""Teste do iniciante (F17b, Decision 8): uma skill gerada, num `claude -p` sem ferramentas, pasta vazia, sem MCP,
em várias voltas pelo roteiro escrito antes. Uso: iniciante.py <pasta da skill gerada> <roteiro.json> <skill> <n> <log>
Sai 0 se passou, 1 se reprovou, 2 se falhou a execução."""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

skill_dir, roteiro, skill, n, log = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5])
cfg = json.loads(roteiro.read_text(encoding="utf-8"))
r = cfg["skills"][skill]
partes = []
for p in sorted(skill_dir.rglob("*")):
    if p.is_file() and p.suffix == ".md" and p.name != "CHANGELOG.md":
        partes.append("=== arquivo da skill: %s ===\n%s" % (p.relative_to(skill_dir).as_posix(), p.read_text(encoding="utf-8")))
sistema = "Skill instalada: %s. Conteúdo dos arquivos dela:\n\n%s" % (skill, "\n\n".join(partes))

COMANDO = re.compile(r"```(?:bash|sh|shell|zsh|powershell|console)|^\s*\$ |\b(?:rode|execute|rodar) `", re.M | re.I)
EXIGE = re.compile(r"verify-gate|handoff-lint|psql|prompt-drift|sdd/bin/", re.I)
GRAVOU = re.compile(r"(?<!n[ãa]o )\b(?:gravei|salvei|criei o arquivo)\b|arquivo (?:foi )?(?:gravado|salvo) em\b", re.I)
AVISO = re.compile(r"n[ãa]o (?:foi|foram) gravad|nada (?:foi|ficou) gravad|n[ãa]o gravei|n[ãa]o salvei|nada foi salvo|n[ãa]o foi salvo", re.I)

tmp = Path(tempfile.mkdtemp(prefix="iniciante-"))
vazio = tmp / "mcp.json"
vazio.write_text('{"mcpServers": {}}', encoding="utf-8")
sp = tmp / "sistema.md"
sp.write_text(sistema, encoding="utf-8")
cwd = tmp / "projeto-vazio"
cwd.mkdir()
base = ["claude", "-p", "--output-format", "json", "--tools", "", "--strict-mcp-config", "--mcp-config", str(vazio),
        "--setting-sources", "project", "--system-prompt-file", str(sp)]
ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
linhas = ["$ claude -p --output-format json --tools \"\" --strict-mcp-config --mcp-config <vazio> --setting-sources project "
          "--system-prompt-file <%s gerada + references> [--resume <sessão>] <volta do roteiro>   # %s, execução %s" % (skill, skill, n),
          "claude %s · pasta de trabalho vazia · roteiro %s" % (ver, roteiro.name)]
sessao, respostas, entregue, rc_final = None, [], False, 2
try:
    for i, volta in enumerate(r["voltas"], 1):
        cmd = base + (["--resume", sessao] if sessao else []) + [volta]
        p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", timeout=600,
                           stdin=subprocess.DEVNULL)
        if p.returncode != 0:
            linhas.append("volta %d: claude saiu %d: %s" % (i, p.returncode, (p.stderr or p.stdout)[-400:]))
            raise RuntimeError("claude falhou")
        d = json.loads(p.stdout)
        sessao = d.get("session_id") or sessao
        txt = d.get("result", "")
        respostas.append(txt)
        linhas.append("\n----- volta %d — aluno -----\n%s\n----- volta %d — skill (modelo %s) -----\n%s"
                      % (i, volta, i, ",".join(sorted((d.get("modelUsage") or {}).keys())) or "?", txt))
        if all(m in txt for m in r["marca"]) and AVISO.search(txt):
            entregue = True
            break
    tudo = "\n".join(respostas)
    achados = []
    if not entregue:
        achados.append("sem entrega do documento com o aviso de que nada foi gravado até a última volta")
    for nome, rx in (("pede comando", COMANDO), ("exige script/gate", EXIGE), ("diz que gravou", GRAVOU)):
        m = rx.search(tudo)
        if m:
            achados.append("%s: ...%s..." % (nome, tudo[max(0, m.start() - 60):m.end() + 40].replace("\n", " ")))
    linhas.append("\n===== veredito =====\nvoltas: %d · entregue: %s" % (len(respostas), "sim" if entregue else "não"))
    linhas += ["❌ " + a for a in achados] or ["✅ nenhum achado"]
    linhas.append("RESULTADO: %s" % ("PASSOU" if not achados else "REPROVOU"))
    rc_final = 0 if not achados else 1
except Exception as e:  # noqa: BLE001 — a falha de execução vai para o log, nunca vira "passou"
    linhas.append("RESULTADO: FALHA DE EXECUÇÃO (%s)" % e)
    rc_final = 2
finally:
    linhas.append("rc=%d" % rc_final)
    log.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    shutil.rmtree(tmp, ignore_errors=True)
sys.exit(rc_final)
