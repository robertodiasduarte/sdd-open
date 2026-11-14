#!/usr/bin/env python3
"""Série 3 do teste do iniciante do build (decisão do Roberto, 2026-11-14): o mesmo roteiro e os juízes de iniciante2.py,
mas pela API de chat da OpenRouter (modelo anthropic/claude-opus-5.5), sem Claude Code: o modelo não recebe pasta de
trabalho nem ferramenta. Uso: OPENROUTER_API_KEY=… iniciante_or.py <pasta da skill> <roteiro.json> <skill> <n> <log>
Sai 0 passou · 1 reprovou · 2 falha de execução. O log tem o custo de cada volta (usage.cost)."""
import importlib.util, json, os, sys, urllib.request
from pathlib import Path

aqui = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("juizes", aqui / "iniciante2.py")
j = importlib.util.module_from_spec(spec); spec.loader.exec_module(j)
MODELO = "anthropic/claude-opus-5.5"


def chamar(mensagens):
    corpo = json.dumps({"model": MODELO, "messages": mensagens, "max_tokens": 8000, "usage": {"include": True},
                        "provider": {"data_collection": "deny"}}).encode("utf-8")
    req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=corpo, method="POST",
                                 headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read().decode("utf-8"))
    return d["choices"][0]["message"]["content"] or "", float((d.get("usage") or {}).get("cost") or 0)


def main():
    skill_dir, roteiro, skill, n, log = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], Path(sys.argv[5])
    r = json.loads(roteiro.read_text(encoding="utf-8"))["skills"][skill]
    modo = r.get("modo", "documento")
    partes = ["=== arquivo da skill: %s ===\n%s" % (p.relative_to(skill_dir).as_posix(), p.read_text(encoding="utf-8"))
              for p in sorted(skill_dir.rglob("*.md")) if p.name != "CHANGELOG.md"]
    msgs = [{"role": "system", "content": "Skill instalada: %s. Conteúdo dos arquivos dela:\n\n%s" % (skill, "\n\n".join(partes))}]
    linhas = ["$ OPENROUTER_API_KEY=<chave> python3 -I iniciante_or.py <%s em %s> %s %s %s %s   # modelo %s, sem pasta, sem ferramenta"
              % (skill, skill_dir, roteiro.name, skill, n, log.name, MODELO)]
    respostas, entregue, custo, rc = [], False, 0.0, 2
    try:
        for i, volta in enumerate(r["voltas"], 1):
            msgs.append({"role": "user", "content": volta})
            txt, c = chamar(msgs)
            custo += c
            msgs.append({"role": "assistant", "content": txt})
            respostas.append(txt)
            linhas.append("\n----- volta %d — aluno -----\n%s\n----- volta %d — skill (%s, US$ %.4f) -----\n%s" % (i, volta, i, MODELO, c, txt))
            if j.entregou(modo, txt, r.get("marca", [])):
                entregue = True
                if modo == "documento":
                    break   # build (série 4, avaliador ciclo 2): todas as voltas rodam; o que vem depois também é julgado
        achados = j.julgar(modo, respostas, r.get("marca", []), entregue)
        linhas.append("\n===== veredito =====\nvoltas: %d · entregue: %s · custo: US$ %.4f" % (len(respostas), "sim" if entregue else "não", custo))
        linhas += ["❌ " + a for a in achados] or ["✅ nenhum achado"]
        linhas.append("RESULTADO: %s" % ("PASSOU" if not achados else "REPROVOU"))
        rc = 0 if not achados else 1
    except Exception as e:  # noqa: BLE001
        linhas.append("RESULTADO: FALHA DE EXECUÇÃO (%s)" % str(e)[:300])
    finally:
        linhas.append("rc=%d" % rc)
        log.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return rc


if __name__ == "__main__":
    sys.exit(main())
