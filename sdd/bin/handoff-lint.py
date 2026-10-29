#!/usr/bin/env python3
"""handoff-lint.py — confere uma ficha de feature contra o mínimo de sdd/templates/HANDOFF_TEMPLATE.md.

Só stdlib, Python >= 3.9. Uso:
    python3 sdd/bin/handoff-lint.py <HANDOFF.md>     # exit 0 = válido · 1 = violações · 64 = uso

A próxima sessão começa sem memória desta: o que ela não achar escrito, não existe. Regras:
  - 1º título `# HANDOFF:`;
  - `## Ficha` com as linhas Objetivo, Status e Verify Gate;
  - `## Prompt de retomada` com um bloco de código (o prompt que se cola na sessão nova), salvo quando o
    Status da Ficha é ✅ (DoD fechado): sem continuação, a sdd-handoff deixa o prompt opcional;
  - `## Histórico de slices` com ≥1 `### <slice> — AAAA-MM-DD`;
  - nenhum placeholder: fora de código, `«…»`, nome em MAIÚSCULAS entre chaves ou prosa entre chaves;
    dentro de bloco de código, só `«…»` e MAIÚSCULAS entre chaves sem `$` antes (comando real com
    chaves, como `awk` ou `${HOME}`, passa);
  - nenhuma frase que dependa da conversa anterior ("como discutimos", "continue de onde paramos").
Seção a mais passa e `## Eventos` não é exigido: o template cresce sem reescrever este lint.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CRASE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"«[^»]*»|\{[A-Z][A-Z0-9_]{2,}\}|\{[^{}\n]*\s[^{}\n]*\}")
PLACEHOLDER_EM_CODIGO = re.compile(r"«[^»]*»|(?<!\$)\{[A-Z][A-Z0-9_]{2,}\}")
VAGO = re.compile(
    r"como (discutimos|discutido|combinamos|combinado|vimos antes|falamos|conversamos)"
    r"|conforme (conversamos|discutimos|combinado|falado)"
    r"|continu(ar|e) de onde paramos",
    re.I,
)
SLICE = re.compile(r"^### .+ [—-] \d{4}-\d{2}-\d{2}\s*$")
CAMPOS = ("Objetivo", "Status", "Verify Gate")


def intervalo(linhas: list, prefixo: str):
    """(início, fim) das linhas da seção `## <prefixo>…`, ou None. `linhas` já sem os blocos de código,
    para um `## ` dentro do prompt colado não encerrar a seção."""
    for i, ln in enumerate(linhas):
        if re.match(r"^## " + re.escape(prefixo) + r"\b", ln):
            fim = next((j for j in range(i + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
            return i + 1, fim
    return None


def secao(linhas: list, prefixo: str):
    faixa = intervalo(linhas, prefixo)
    return None if faixa is None else linhas[faixa[0]:faixa[1]]


def lint(texto: str) -> list:
    erros = []
    brutas = texto.splitlines()
    sem_cerca = CERCA.sub(lambda m: "\n" * m.group(0).count("\n"), texto)
    linhas = sem_cerca.splitlines()

    titulo = next((ln for ln in linhas if ln.startswith("# ")), "")
    if not titulo.startswith("# HANDOFF:"):
        erros.append("o 1º título não é '# HANDOFF: <feature>'")

    ficha = secao(linhas, "Ficha")
    fechada = False
    if ficha is None:
        erros.append("falta a seção ## Ficha")
    else:
        for campo in CAMPOS:
            if not any(re.match(r"^\|\s*\**" + re.escape(campo) + r"\**\s*\|", ln) for ln in ficha):
                erros.append(f"## Ficha sem a linha {campo}")
        status = next((ln for ln in ficha if re.match(r"^\|\s*\**Status\**\s*\|", ln)), "")
        celula = status.strip().strip("|").split("|")[1].strip() if status.count("|") >= 3 else ""
        fechada = celula.startswith("✅")  # o 1º símbolo da célula, como no template: "✅ DoD fechado"

    faixa = intervalo(linhas, "Prompt de retomada")
    cercas = 0 if faixa is None else sum(1 for ln in brutas[faixa[0]:faixa[1]] if ln.startswith(("```", "~~~")))
    if cercas < 2 and not (faixa is None and fechada):
        erros.append("## Prompt de retomada ausente ou sem o bloco de código que se cola na sessão nova"
                     " (só a ficha com Status ✅ dispensa o prompt)")

    historico = secao(linhas, "Histórico de slices")
    if historico is None or not any(SLICE.match(ln) for ln in historico):
        erros.append("## Histórico de slices sem nenhum '### <slice> — AAAA-MM-DD'")

    for n, ln in enumerate(CRASE.sub("", sem_cerca).splitlines(), 1):
        m = PLACEHOLDER.search(ln)
        if m:
            erros.append(f"linha {n}: placeholder do template sem preencher: {m.group(0)}")
        v = VAGO.search(ln)
        if v:
            erros.append(f"linha {n}: frase que depende da conversa anterior: '{v.group(0).lower()}'")
    for bloco in CERCA.finditer(texto):
        inicio = texto.count("\n", 0, bloco.start()) + 1
        for k, ln in enumerate(bloco.group(0).splitlines()):
            m = PLACEHOLDER_EM_CODIGO.search(ln)
            if m:
                erros.append(f"linha {inicio + k}: placeholder do template sem preencher: {m.group(0)}")
            v = VAGO.search(ln)
            if v:
                erros.append(f"linha {inicio + k}: frase que depende da conversa anterior: '{v.group(0).lower()}'")
    return erros


def main(argv: list) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_file():
        print("uso: handoff-lint.py <HANDOFF.md>", file=sys.stderr)
        return 64
    try:
        texto = Path(argv[1]).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"🛑 {argv[1]}: não consegui ler: {e}", file=sys.stderr)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ confira a permissão e a codificação (UTF-8) do arquivo e rode de novo", file=sys.stderr)
        return 1
    erros = lint(texto)
    for e in erros:
        print(f"🛑 {argv[1]}: {e}", file=sys.stderr)
    if erros:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ corrija a ficha nos pontos acima (molde: sdd/templates/HANDOFF_TEMPLATE.md) e rode de novo",
              file=sys.stderr)
        return 1
    print(f"✅ {argv[1]}: HANDOFF válido")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
