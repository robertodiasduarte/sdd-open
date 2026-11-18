"""AT-011 da F6: as 7 skills de fase não mudaram entre v2.2.6 e HEAD, além da seção nova e da versão.

Cópia do script da F5 (sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.py) com outra lista de
skills, outra base, nenhuma exceção e duas provas:
  1. extração — passos, itens numerados e comandos, sem a camada de conversa, a linha de identificação
     e a seção "Por que cada regra existe": a diferença tem de ser vazia;
  2. texto inteiro (M1 da revisão do DESIGN) — sem a seção nova e com a versão trocada por um marcador
     em `version:` e na linha de identificação, v2.2.6 e HEAD têm de ser iguais byte a byte. Pega regra
     em prosa, título sem número e linha de bloco sem comando, que a extração não vê.
Exit 0 = as duas provas passam nas 7; 1 = diferença (o log diz qual).
"""
import difflib
import re
import subprocess
import sys

BASE = "v2.2.6"
SKILLS = ("sdd-brainstorm", "sdd-define", "sdd-governanca", "sdd-ux-review", "sdd-design", "sdd-build",
          "sdd-release")
PASSO = re.compile(r"^(##|###|####) (\d|Passo \d|FASE \d)")
ITEM = re.compile(r"^\s*\d+[a-z]?\. \S.{0,58}")
CMD = re.compile(r"sdd/bin|\bgit |\bgh |\bbash |python3|scripts/")
CRASE = re.compile(r"`([^`\n]+)`")
SECAO_NOVA = re.compile(r"\n## Por que cada regra existe[^\n]*\n.*?(?=\n## )", re.S)


def mostra(ref, caminho):
    return subprocess.run(["git", "show", ref + ":" + caminho], capture_output=True, text=True,
                          check=True).stdout


def limpa(texto):
    texto = re.sub(r"\n## Como falar com o aluno\n.*?(?=\n## )", "\n", texto, flags=re.S)
    texto = SECAO_NOVA.sub("\n", texto)
    texto = re.sub(r"\nNa primeira resposta desta skill, comece com esta linha, uma vez só(?:, antes do Status)?:\n`[^`\n]+`\n",
                   "\n", texto)
    return texto


def normaliza(texto):
    texto = SECAO_NOVA.sub("", texto)  # a seção leva a própria linha em branco de antes
    texto = re.sub(r'(?m)^(  version: )"[0-9.]+"$', r'\1"VERSAO"', texto)
    return re.sub(r"(`sdd-[a-z-]+ v)[0-9.]+( ·)", r"\1VERSAO\2", texto)


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
        velho, novo = mostra(BASE, p), mostra("HEAD", p)
        antes, depois = extrai(velho), extrai(novo)
        dif = [d[:1] + " " + d[2:] for d in difflib.ndiff(antes, depois) if d[:1] in "+-"]
        texto = list(difflib.unified_diff(normaliza(velho).splitlines(), normaliza(novo).splitlines(),
                                          BASE, "HEAD", lineterm="", n=0))
        secao = SECAO_NOVA.search(novo)
        ok = not dif and not texto and secao is not None and SECAO_NOVA.search(velho) is None
        falhas += 0 if ok else 1
        print(("OK    " if ok else "FALHA ") + s + ": extração %d → %d linhas (%s) · texto normalizado %s · "
              "seção nova %s" % (len(antes), len(depois), "idêntica" if not dif else "%d diferença(s)" % len(dif),
                                 "igual" if not texto else "DIFERENTE", "presente" if secao else "AUSENTE"))
        for d in dif + texto[2:]:
            print("        " + d)
    print("skills: %d · com diferença: %d" % (len(SKILLS), falhas))
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
