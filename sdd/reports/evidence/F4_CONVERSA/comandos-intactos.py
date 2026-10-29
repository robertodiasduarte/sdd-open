"""AT-018 da F4: comandos e ordem dos passos das 14 skills não mudaram entre v2.2.4 e HEAD.

Para cada SKILL.md, de `git show v2.2.4:<arquivo>` e de `git show HEAD:<arquivo>`, tira a seção
"Como falar com o aluno" e a linha de identificação (as adições declaradas) e extrai, em ordem:
  passo  — títulos `##`/`###`/`####` que começam por número, "Passo N" ou "FASE N";
  item   — itens de lista numerada (os primeiros 60 caracteres: `1. **Landmines:** …`);
  cmd    — trechos entre crases, e linhas de bloco cercado, que citam sdd/bin, git, gh, bash, python3
           ou scripts/.
A diferença (difflib) tem de ser exatamente a lista EXCECOES. Exit 0 = só exceções; 1 = diferença
não declarada (o log diz qual).
"""
import difflib
import re
import subprocess
import sys

SKILLS = ("sdd-auditoria-harness", "sdd-brainstorm", "sdd-build", "sdd-checar-ambiente", "sdd-define",
          "sdd-design", "sdd-governanca", "sdd-handoff", "sdd-iterate", "sdd-new-session", "sdd-playbook",
          "sdd-prompt-builder", "sdd-release", "sdd-ux-review")
EXCECOES = {
    "sdd-design": ["+ passo ### 8. Conferir",
                   "+ cmd python3 sdd/bin/design-lint.py sdd/features/DESIGN_{FEATURE}.md"],
    "sdd-handoff": ["+ passo ### 3b. Conferir a ficha",
                    "+ cmd python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_{FEATURE}.md"],
}
PASSO = re.compile(r"^(##|###|####) (\d|Passo \d|FASE \d)")
ITEM = re.compile(r"^\s*\d+[a-z]?\. \S.{0,58}")
CMD = re.compile(r"sdd/bin|\bgit |\bgh |\bbash |python3|scripts/")
CRASE = re.compile(r"`([^`\n]+)`")


def mostra(ref, caminho):
    return subprocess.run(["git", "show", ref + ":" + caminho], capture_output=True, text=True,
                          check=True).stdout


def limpa(texto):
    texto = re.sub(r"\n## Como falar com o aluno\n.*?(?=\n## )", "\n", texto, flags=re.S)
    texto = re.sub(r"\nNa primeira resposta desta skill, comece com esta linha, uma vez só(?:, antes do Status)?:\n`[^`\n]+`\n",
                   "\n", texto)
    return texto


def extrai(texto):
    saida, cerca = [], False
    for ln in limpa(texto).splitlines():
        if ln.lstrip().startswith(("```", "~~~")):
            cerca = not cerca
            continue
        if cerca:
            if CMD.search(ln):
                saida.append("cmd " + ln.strip())
            continue
        if PASSO.match(ln):
            saida.append("passo " + ln.strip())
        m = ITEM.match(ln)
        if m:
            saida.append("item " + m.group(0).strip())
        saida += ["cmd " + c for c in CRASE.findall(ln) if CMD.search(c)]
    return saida


def main():
    falhas = 0
    for s in SKILLS:
        p = ".agents/skills/" + s + "/SKILL.md"
        antes, depois = extrai(mostra("v2.2.4", p)), extrai(mostra("HEAD", p))
        dif = [d[:1] + " " + d[2:] for d in difflib.ndiff(antes, depois) if d[:1] in "+-"]
        esperado = EXCECOES.get(s, [])
        ok = dif == esperado
        falhas += 0 if ok else 1
        print(("OK    " if ok else "FALHA ") + s + f": {len(antes)} → {len(depois)} linhas extraídas "
              f"(passos, itens numerados e comandos), "
              + ("idêntico" if not dif else f"{len(dif)} diferença(s)"))
        for d in dif:
            print("        " + d + ("" if d in esperado else "   ← NÃO DECLARADA"))
        for e in esperado:
            if e not in dif:
                print("        exceção declarada e ausente: " + e)
    print(f"skills: {len(SKILLS)} · com diferença não declarada: {falhas}")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
