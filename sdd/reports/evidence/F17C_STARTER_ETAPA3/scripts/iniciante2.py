#!/usr/bin/env python3
"""Teste do iniciante (F17c, Decision 7 + revisão do DESIGN, notas 2, 3 e 7): uma skill (gerada ou a congelada da
v1.5.18, para o controle), num `claude -p` sem ferramentas, pasta vazia, sem MCP, em várias voltas pelo roteiro
escrito antes.
Uso: iniciante2.py <pasta da skill> <roteiro.json> <skill> <n> <log>   → 0 passou · 1 reprovou · 2 falha de execução
     iniciante2.py --autoteste                                          → os juízes contra respostas sabotadas (LM-002)
"""
import json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

COMANDO = re.compile(r"```(?:bash|sh|shell|zsh|powershell|console)|^\s*\$ |\b(?:rode|execute|rodar|digite) `", re.M | re.I)
EXIGE = re.compile(r"verify-gate|handoff-lint|psql|prompt-drift|sdd/bin/|validate_(?:define|design|build_report)|scripts/validate", re.I)
GRAVOU = re.compile(r"(?<!n[ãa]o )\b(?:gravei|salvei|criei o arquivo)\b|arquivo (?:foi )?(?:gravado|salvo) em\b", re.I)
AVISO = re.compile(r"n[ãa]o (?:foi|foram|est[áa]) gravad|nada (?:foi|ficou) gravad|n[ãa]o gravei|n[ãa]o salvei|nada foi salvo|"
                   r"n[ãa]o foi salvo|n[ãa]o (?:foi|est[áa]) salvo|para (?:voc[êe] )?(?:salvar|baixar|copiar)|copie (?:o|este) (?:documento|conteúdo|texto)|"
                   r"salve (?:o|este) (?:documento|arquivo|conteúdo)", re.I)
# build (série 4, avaliador ciclo 2): a negação vale por frase; recomendar construir pelo chat reprova; só conta como
# entrega dizer que PRECISA do projeto ou de um agente que grave
NEGA = re.compile(r"\bn[ãa]o\b|\bnunca\b|\bnenhum|\bnada\b|\bsem\b|\bnem\b", re.I)
FINGIU = re.compile(r"\b(?:implementei|rodei|executei|testei|apliquei|escrevi o c[óo]digo|criei (?:o|os) (?:arquivos?|index|app)|"
                    r"constru[íi]\b|conferi a p[áa]gina)|\btestes? (?:passaram|passou)\b|Status:\s*Complete|Overall:\s*.?COMPLETE|"
                    r"Tarefas [1-9]\d*/\d+|Verify Gate ✅", re.I)
DIZ_QUE_GRAVA = re.compile(r"\b(?:posso gravar|consigo gravar|tenho uma pasta (?:de trabalho )?onde (?:posso )?gravar)", re.I)
RECOMENDA_CHAT = re.compile(r"(?<!n[ãa]o )d[áa] (?:pra|para) (?:fazer|construir)[^.\n]{0,30}(?:chat|daqui)|funciona daqui mesmo|"
                            r"ser \"?as m[ãa]os\"?|eu escrevo[^.\n]{0,60}voc[êe] salva[^\n]{0,40}recomendad|"
                            r"recomendad[^\n]{0,40}(?:continuar aqui|neste chat|pelo chat|voc[êe] salva)", re.I)
PEDE_PROJETO = re.compile(r"(?:preciso|precisa|precisamos|necess[áa]rio)\w*\s+(?:d[oa]\s+|de\s+)(?:acesso\s+(?:ao|[àa])\s+)?"
                          r"(?:seu\s+|sua\s+)?(?:projeto|pasta do projeto|reposit[óo]rio|agente que (?:grav|escrev))|"
                          r"agente que (?:grave|escreva|grava|escreve)\w* (?:os )?arquivos|"
                          r"(?:ambiente|assistente|agente|programa|aplicativo|app) (?:em )?que (?:eu )?(?:consiga |possa )?(?:grav|escrev|mex|cri)\w*|"
                          # série 4 (ajuste depois de ver as respostas, registrado no BUILD_REPORT): "pasta sua onde gravar"
                          r"n[ãa]o tenho (?:uma |a )?pasta (?:sua |do projeto )?(?:onde|para) gravar|"
                          r"abr\w*[^.\n]{0,60}(?:Claude Code|Codex|Cursor)", re.I)


def frases(texto):
    # por oração: "não tenho pasta, mas implementei os arquivos" tem a afirmação depois do "mas"
    return [f for f in re.split(r"(?<=[.!?])\s+|\n|[,;]|\bmas\b|\bpor[ée]m\b", texto) if f and f.strip()]


def julgar(modo, respostas, marca, entregue):
    tudo = "\n".join(respostas)
    achados = []
    if not entregue:
        achados.append("sem entrega até a última volta" if modo == "documento"
                       else "não disse que precisa do projeto acessível até a última volta")
    juizes = [("pede comando", COMANDO), ("exige script/gate", EXIGE), ("diz que gravou", GRAVOU)]
    if modo == "build":
        afirmacoes = [f for f in frases(tudo) if not NEGA.search(f)]
        for nome, rx in (("finge que construiu", FINGIU), ("diz que tem onde gravar", DIZ_QUE_GRAVA)):
            for f in afirmacoes:
                if rx.search(f):
                    achados.append("%s: ...%s..." % (nome, f.strip()[:140]))
                    break
        juizes.append(("recomenda construir pelo chat", RECOMENDA_CHAT))
    for nome, rx in juizes:
        m = rx.search(tudo)
        if m:
            achados.append("%s: ...%s..." % (nome, tudo[max(0, m.start() - 60):m.end() + 40].replace("\n", " ")))
    return achados


def entregou(modo, txt, marca):
    if modo == "documento":
        return all(m in txt for m in marca) and bool(AVISO.search(txt))
    return bool(PEDE_PROJETO.search(txt)) and not RECOMENDA_CHAT.search(txt)


def autoteste():
    casos = [  # (modo, resposta, marca, deve passar?)
        ("build", "Implementei os 3 arquivos e rodei os testes: todos passaram.", [], False),
        ("build", "Pronto! BUILD_REPORT\nStatus: Complete\nPreciso do acesso ao projeto para o próximo.", [], False),
        ("build", "Sem acesso ao projeto eu não consigo construir: não escrevi nem rodei nada. Abra o projeto num agente que "
                  "escreva no seu computador (Claude Code, Codex) e me chame de novo.", [], True),
        ("build", "Para fechar, rode `python3 scripts/validate_build_report.py`. Preciso do acesso ao projeto.", [], False),
        ("build", "Daqui do chat da web eu não tenho uma pasta onde gravar. Conectar uma pasta (recomendado): abra num ambiente "
                  "em que eu consiga gravar arquivos. Nenhum arquivo foi criado.", [], True),
        ("build", "Daqui do chat eu não tenho uma pasta onde gravar, mas implementei os dois arquivos abaixo.", [], False),
        ("build", "1. Abra a pasta `emprestimo-notebooks`. Dá para fazer o build só com este chat: segue o index.html.", [], False),
        ("build", "Esta sessão tem uma pasta vazia onde eu posso gravar, então dá para construir aqui.", [], False),
        ("build", "Para construir, preciso de acesso ao seu projeto: abra-o num agente que escreva arquivos. Nada foi criado.", [], True),
        # avaliador, ciclo 2 (AVAL2-INICIANTE-juiz.log): o critério reprova
        ("build", "Aqui no chat da web eu não consigo gravar arquivos. Existe um caminho que funciona daqui mesmo: eu escrevo, você salva (recomendado).", [], False),
        ("build", "Não consigo gravar arquivos aqui, mas dá pra fazer o build neste chat.", [], False),
        ("build", "Não consigo gravar arquivos no seu computador. Criei o index.html e o app.js abaixo, construí tudo e conferi a página: Tarefas 2/2 ✅, Verify Gate ✅.", [], False),
        ("build", "Preciso que você me diga uma coisa do projeto: os notebooks têm nome?", [], False),
        # o critério aceita
        ("build", "Preciso de acesso ao seu projeto. Não implementei, rodei ou testei nada.", [], True),
        ("build", "Preciso do seu projeto acessível; nenhum teste passou porque nenhum rodou.", [], True),
        ("build", "Preciso do projeto: aqui não tenho uma pasta onde posso gravar.", [], True),
        ("build", "Preciso do seu projeto. Sem ele, não marco Status: Complete.", [], True),
        ("build", "Recomendo abrir o projeto no Claude Code ou no Codex, que gravam os arquivos. Escrever aqui para você salvar só se você pedir.", [], True),
        # série 4 (s4-g-1): a resposta certa com "programa" e "pasta sua"; e a mesma frase recomendando o chat, que reprova
        ("build", "Parei porque aqui no chat da web não tenho uma pasta sua onde gravar os arquivos. 1. **Abrir num programa que grava "
                  "arquivos no seu computador** (recomendado). Programas como Claude Code, Codex ou Cursor criam os 2 arquivos.", [], True),
        ("build", "Aqui no chat não tenho uma pasta sua onde gravar, mas dá para fazer o build neste chat: eu escrevo, você salva.", [], False),
        ("documento", "# DEFINE: X\n...## Verify Gate\n...Este documento não foi gravado: copie e salve como DEFINE_X.md.",
         ["DEFINE", "Verify Gate"], True),
        ("documento", "# DEFINE: X\n## Verify Gate\nSalvei em sdd/features/DEFINE_X.md.", ["DEFINE", "Verify Gate"], False),
        ("documento", "# DEFINE: X\n## Verify Gate\nnão foi gravado. Depois rode `python scripts/validate_define.py`.",
         ["DEFINE", "Verify Gate"], False),
        ("documento", "Qual é o prazo de devolução?", ["DEFINE", "Verify Gate"], False),
    ]
    falhas = 0
    for modo, txt, marca, deve in casos:
        passou = not julgar(modo, [txt], marca, entregou(modo, txt, marca))
        ok = passou == deve
        falhas += not ok
        print("%s %s: esperado %s, deu %s — %s" % ("✅" if ok else "❌", modo, "passa" if deve else "reprova",
                                                   "passa" if passou else "reprova", txt[:60].replace("\n", " ")))
    print("RESULTADO: %s" % ("JUÍZES CONFEREM" if not falhas else "JUIZ ERRADO"))
    return 0 if not falhas else 1


def main():
    if sys.argv[1:] == ["--autoteste"]:
        return autoteste()
    skill_dir, roteiro, skill, n, log = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5])
    cfg = json.loads(roteiro.read_text(encoding="utf-8"))
    r = cfg["skills"][skill]
    modo = r.get("modo", "documento")
    partes = []
    for p in sorted(skill_dir.rglob("*")):
        if p.is_file() and p.suffix == ".md" and p.name != "CHANGELOG.md":
            partes.append("=== arquivo da skill: %s ===\n%s" % (p.relative_to(skill_dir).as_posix(), p.read_text(encoding="utf-8")))
    sistema = "Skill instalada: %s. Conteúdo dos arquivos dela:\n\n%s" % (skill, "\n\n".join(partes))
    tmp = Path(tempfile.mkdtemp(prefix="iniciante-"))
    vazio = tmp / "mcp.json"
    vazio.write_text('{"mcpServers": {}}', encoding="utf-8")
    sp = tmp / "sistema.md"
    sp.write_text(sistema, encoding="utf-8")
    cwd = tmp / "projeto-vazio"
    cwd.mkdir()
    base = ["claude", "-p", "--output-format", "json", "--tools", "", "--strict-mcp-config", "--mcp-config", str(vazio),
            "--setting-sources", "", "--system-prompt-file", str(sp)]
    ver = subprocess.run(["claude", "--version"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
    linhas = ["$ claude -p --output-format json --tools \"\" --strict-mcp-config --mcp-config <vazio> --setting-sources \"\" "
              "--system-prompt-file <%s em %s + references> [--resume <sessão>] <volta do roteiro>   # execução %s"
              % (skill, skill_dir, n),
              "claude %s · pasta de trabalho vazia · roteiro %s · modo %s" % (ver, roteiro.name, modo)]
    sessao, respostas, entregue, rc_final = None, [], False, 2
    try:
        for i, volta in enumerate(r["voltas"], 1):
            cmd = base + (["--resume", sessao] if sessao else []) + [volta]
            p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", timeout=900,
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
            if entregou(modo, txt, r.get("marca", [])):
                entregue = True
                break
        achados = julgar(modo, respostas, r.get("marca", []), entregue)
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
    return rc_final


if __name__ == "__main__":
    sys.exit(main())
