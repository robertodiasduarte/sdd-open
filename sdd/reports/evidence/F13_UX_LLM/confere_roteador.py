#!/usr/bin/env python3
"""Confere por EFEITO uma execução do roteador. Uso: confere_roteador.py feliz|sem-skill|sem-tipo <cópia> <transcript> <scanlog>
Exit 0 passa · 1 reprova. O scan é provado pelo registro do calço, não pelo texto; a leitura das skills, por comando executado com sucesso."""
import re, subprocess, sys
from pathlib import Path

modo, copia, log, scanlog = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
texto = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
linhas = texto.splitlines()
comandos, atual, saidas = [], None, None  # (texto, status, saída)
for ln in linhas:
    if atual is not None:
        m = re.match(r"^ (succeeded|exited (\d+)) in ", ln)
        if m:
            comandos.append(["\n".join(atual), int(m.group(2) or 0), ""])
            atual, saidas = None, []
        else:
            atual.append(ln)
    elif ln.strip() == "exec":
        if saidas is not None:
            comandos[-1][2] = "\n".join(saidas)
        atual, saidas = [], None
    elif ln.strip() == "codex":
        if saidas is not None:
            comandos[-1][2] = "\n".join(saidas)
        saidas = None
    elif saidas is not None:
        saidas.append(ln)
if saidas is not None and comandos:
    comandos[-1][2] = "\n".join(saidas)
ultima = max((i for i, ln in enumerate(linhas) if ln.strip() == "codex"), default=None)
mensagem_final = "\n".join(linhas[ultima + 1:]) if ultima is not None else ""
erros = []
# O leitor abre o comando (depois de -lc ' ou de ; && |), para "echo cat x" não contar.
LE = r"(?:-lc\s+['\"]|[;&|\n]\s*)(?:cat|sed|awk|rg|grep|head|tail|less|nl)\b[^\n;|&]*"


def leitura(caminho, marca):
    # Num comando composto, o status é o do último: a prova é o conteúdo do arquivo na saída.
    for i, (c, st, saida) in enumerate(comandos):
        m = re.search(LE + re.escape(caminho), c)
        if m and (marca in saida):
            return (i, m.end())
    return None


scan = scanlog.read_text(encoding="utf-8", errors="replace").splitlines() if scanlog.is_file() else []
spec = copia / "src/notas/LOOP_SPEC.md"
pasta = copia / "src/notas"
prompts = sorted(p for p in pasta.rglob("*") if p.is_file() and p.name != "LOOP_SPEC.md") if pasta.is_dir() else []

if modo == "sem-skill":
    if spec.exists() or prompts:
        erros.append("sem a skill, nada podia ser gravado no destino: %s" % [str(p) for p in ([spec] if spec.exists() else []) + prompts])
    if "[D2 · muda o produto]" not in mensagem_final:
        erros.append("a mensagem final não traz [D2 · muda o produto]")
else:
    if not spec.is_file() or '<LOOP_SPEC v="2"' not in spec.read_text(encoding="utf-8", errors="replace"):
        erros.append('falta src/notas/LOOP_SPEC.md com <LOOP_SPEC v="2"')
    else:
        estagios = [ln for ln in spec.read_text(encoding="utf-8", errors="replace").splitlines() if re.match(r"^\|\s*\d+\s*\|", ln)]
        llm = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in estagios if re.search(r"\|\s*`?LLM`?\s*\|", ln)]
        if not llm:
            erros.append("a tabela de estágios não tem linha LLM")
        for cels in llm:
            alvo = copia / cels[-1].strip("`")
            if not alvo.is_file() or len(alvo.read_text(encoding="utf-8", errors="replace").strip()) < 40:
                erros.append("estágio LLM %s sem prompt de verdade em %s" % (cels[1], cels[-1]))
        if len(prompts) != len(llm):
            erros.append("%d arquivo(s) de prompt para %d estágio(s) LLM" % (len(prompts), len(llm)))
        for p in [spec] + prompts:
            rel = str(p.relative_to(copia))
            chamadas = [ln.split("\t") for ln in scan if "--conteudo" in ln and (" " + rel + "\t" in ln or ln.split("\t")[0].endswith("/" + rel))]
            if not chamadas:
                erros.append("sem chamada real de prompt-drift-scan.sh --conteudo para %s" % rel)
            elif not any(c[1] in ("rc=0", "rc=2") and c[2] == "existia=0" for c in chamadas):
                erros.append("sem varredura válida de %s antes de ele existir: %s" % (rel, [c[1:] for c in chamadas]))
    i_loop = leitura("sdd-loop-builder/SKILL.md", "name: sdd-loop-builder")
    i_prompt = leitura("sdd-prompt-builder/", "sdd-prompt-builder")
    if i_loop is None:
        erros.append("o transcript não mostra a leitura de sdd-loop-builder/SKILL.md como comando")
    if i_prompt is None:
        erros.append("o transcript não mostra a leitura de sdd-prompt-builder como comando")
    if i_loop is not None and i_prompt is not None and i_loop > i_prompt:
        erros.append("leu a skill de prompt antes da skill do laço")
    if modo == "sem-tipo":
        rel = copia / "sdd/reports/BUILD_REPORT_NOTAS.md"
        corpo = rel.read_text(encoding="utf-8", errors="replace") if rel.is_file() else ""
        if not any(re.search(r"triagem", ln, re.I) and re.search(r"\bloop\b", ln) and not re.search(r"nenhuma triagem|triagem não foi|sem triagem", ln, re.I) for ln in corpo.splitlines()):
            erros.append("o relatório não registra a triagem com o resultado loop")
if (copia / ".git").exists():
    st = subprocess.run(["git", "-C", str(copia), "status", "--porcelain", "-uall"], capture_output=True, text=True).stdout
    outros = [ln[3:] for ln in st.splitlines() if not (ln[3:].startswith("src/notas/") or ln[3:] == "sdd/reports/BUILD_REPORT_NOTAS.md")]
    if outros:
        erros.append("gravou fora do esperado: %s" % outros[:8])

for e in erros:
    print("🛑 " + e)
print("RESULTADO: " + ("REPROVA" if erros else "PASSA"))
sys.exit(1 if erros else 0)
