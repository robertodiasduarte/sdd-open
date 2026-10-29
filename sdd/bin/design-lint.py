#!/usr/bin/env python3
"""design-lint.py — confere um DESIGN contra o template do sdd-open (sdd/templates/DESIGN_TEMPLATE.md).

Só stdlib, Python >= 3.9. Uso:
    python3 sdd/bin/design-lint.py <DESIGN.md>     # exit 0 = válido · 1 = violações · 64 = uso

Regras:
  - `## Key Decisions` presente, com ≥1 decisão; todo título `###` dentro dela é
    `### Decision N: <nome>`, com N = 1, 2, 3… em ordem. Outras ferramentas leem esses títulos:
    renomear (`### Decisão 1`, `### ADR-1`) quebra quem lê.
  - `## File Manifest` com ≥1 linha de dados (`| 1 | …`), `**Total Files:** N` igual ao número de
    linhas, e a última coluna (Dependencies) citando só linhas que existem, sem a própria linha e sem
    ciclo (`None`, `—` e vazio = sem dependência). Ciclo deixa o build sem ordem possível.
  - Nenhum placeholder do template fora de código: `«…»`, nome em MAIÚSCULAS entre chaves, ou
    prosa entre chaves. Bloco cercado por ``` e trecho entre crases não contam.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
CRASE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"«[^»]*»|\{[A-Z][A-Z0-9_]{2,}\}|\{[^{}\n]*\s[^{}\n]*\}")
DECISAO = re.compile(r"^### Decision (\d+): \S")
LINHA_MANIFEST = re.compile(r"^\|\s*(\d+)\s*\|")
TOTAL = re.compile(r"\*\*Total Files:\*\*\s*(\d+)")


def secao(linhas: list, titulo: str):
    """Linhas do título `## <titulo>` até o próximo `## `; None se o título não existe."""
    for i, ln in enumerate(linhas):
        if ln.strip() == "## " + titulo:
            fim = next((j for j in range(i + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
            return linhas[i + 1:fim]
    return None


def ciclo(deps: dict):
    """Uma linha que participa de ciclo, ou None."""
    estado = {}

    def visita(n):
        estado[n] = 1
        for d in deps.get(n, ()):
            if estado.get(d) == 1:
                return d
            if d not in estado:
                achou = visita(d)
                if achou is not None:
                    return achou
        estado[n] = 2
        return None

    for n in sorted(deps):
        if n not in estado:
            achou = visita(n)
            if achou is not None:
                return achou
    return None


def lint(texto: str) -> list:
    erros = []
    linhas = CERCA.sub("", texto).splitlines()

    decisoes = secao(linhas, "Key Decisions")
    if decisoes is None:
        erros.append("falta a seção ## Key Decisions")
    else:
        numeros = []
        for ln in decisoes:
            if ln.startswith("### "):
                m = DECISAO.match(ln)
                if m:
                    numeros.append(int(m.group(1)))
                else:
                    erros.append(f"título fora do padrão '### Decision N: <nome>': {ln.strip()}")
        if not numeros and not any(ln.startswith("### ") for ln in decisoes):
            erros.append("## Key Decisions sem nenhuma '### Decision N: <nome>'")
        if numeros and numeros != list(range(1, len(numeros) + 1)):
            erros.append(f"decisões fora de sequência: {numeros} (esperado 1..{len(numeros)})")

    manifest = secao(linhas, "File Manifest")
    if manifest is None:
        erros.append("falta a seção ## File Manifest")
    else:
        deps = {}
        for ln in manifest:
            m = LINHA_MANIFEST.match(ln)
            if m:
                celulas = [c.strip() for c in ln.strip().strip("|").split("|")]
                deps[int(m.group(1))] = [int(x) for x in re.findall(r"\d+", celulas[-1])] if len(celulas) > 1 else []
        if not deps:
            erros.append("## File Manifest sem nenhuma linha de arquivo")
        total = TOTAL.search("\n".join(manifest))
        if not total:
            erros.append("## File Manifest sem a linha **Total Files:** N")
        elif deps and int(total.group(1)) != len(deps):
            erros.append(f"**Total Files:** {total.group(1)}, mas o manifest tem {len(deps)} linhas")
        for n, ds in sorted(deps.items()):
            for d in ds:
                if d == n:
                    erros.append(f"linha {n} do manifest depende de si mesma")
                elif d not in deps:
                    erros.append(f"linha {n} do manifest depende da linha {d}, que não existe")
        validas = {n: [d for d in ds if d in deps and d != n] for n, ds in deps.items()}
        c = ciclo(validas)
        if c is not None:
            erros.append(f"dependências do manifest formam ciclo (passa pela linha {c})")

    for n, ln in enumerate(CRASE.sub("", CERCA.sub(lambda m: "\n" * m.group(0).count("\n"), texto)).splitlines(), 1):
        m = PLACEHOLDER.search(ln)
        if m:
            erros.append(f"linha {n}: placeholder do template sem preencher: {m.group(0)}")
    return erros


def main(argv: list) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_file():
        print("uso: design-lint.py <DESIGN.md>", file=sys.stderr)
        return 64
    try:
        texto = Path(argv[1]).read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        print(f"🛑 {argv[1]}: não consegui ler: {e}", file=sys.stderr)
        return 1
    erros = lint(texto)
    for e in erros:
        print(f"🛑 {argv[1]}: {e}", file=sys.stderr)
    if erros:
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ corrija o DESIGN nos pontos acima (molde: sdd/templates/DESIGN_TEMPLATE.md) e rode de novo",
              file=sys.stderr)
        return 1
    print(f"✅ {argv[1]}: DESIGN válido")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
