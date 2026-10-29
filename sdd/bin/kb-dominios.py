#!/usr/bin/env python3
"""kb-dominios.py — o KB Domains do DEFINE só cita pastas de sdd/kb/, ou diz `nenhum`.

Só stdlib, Python >= 3.9. Uso:
    python3 sdd/bin/kb-dominios.py <DEFINE.md>     # exit 0 = válido · 1 = violações · 64 = uso

Regras:
  - Lê a 1ª linha `| **KB Domains** | <valor> | … |` fora de bloco cercado. Sem ela, vermelho.
  - O valor é `nenhum`, sozinho, ou uma lista de nomes separados por vírgula (crases, um prefixo
    `sdd/kb/` e a `/` final são tolerados). Vazio, chaves de placeholder, `N/A`, `—`, `-` e `TBD`
    não são lista: o DEFINE diz `nenhum` explicitamente.
  - Cada nome existe como pasta em <raiz>/sdd/kb/ (sem as ocultas; o _index.yaml é arquivo e não conta).
    A raiz é a pasta acima de sdd/features/ quando o DEFINE está lá; senão, o diretório corrente.
  - Válido: para cada domínio citado que tem RULE_MAP.md (perfil normativo), lista `<domínio>: <REGRA> →
    <teste>` das regras com teste, para a sdd-define pô-los no cmd do Verify Gate.
Não importa nada da skill sdd-kb: funciona mesmo sem ela instalada. O registro do domínio no _index.yaml
é conferido pelo validate_kb.py da skill, não aqui.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CERCA = re.compile(r"^(```|~~~).*?^\1[^\n]*$", re.M | re.S)
LINHA = re.compile(r"^\|\s*\*\*KB Domains\*\*\s*\|([^|]*)\|")
NAO_LISTA = ("", "n/a", "na", "—", "-", "tbd")
CELULA = re.compile(r"(?<!\\)\|")
MAX_NOMES = 10


def raiz_do_projeto(define: Path) -> Path:
    d = define.resolve().parent
    if d.name == "features" and d.parent.name == "sdd":
        return d.parent.parent
    return Path.cwd()


def valor_do_campo(texto: str):
    """O valor da célula KB Domains (sem crases nem espaço nas pontas), ou None sem a linha."""
    for ln in CERCA.sub(lambda m: "\n" * m.group(0).count("\n"), texto).splitlines():
        m = LINHA.match(ln)
        if m:
            return m.group(1).replace("`", "").strip()
    return None


def itens(valor: str) -> list:
    saida = []
    for item in valor.split(","):
        item = item.strip()
        if item.startswith("sdd/kb/"):
            item = item[len("sdd/kb/"):]
        item = item.rstrip("/")
        if item:
            saida.append(item)
    return saida


def lista_curta(nomes: list) -> str:
    if not nomes:
        return "a pasta está vazia"
    if len(nomes) <= MAX_NOMES:
        return "existem: " + ", ".join(nomes)
    return "existem: %s e mais %d" % (", ".join(nomes[:MAX_NOMES]), len(nomes) - MAX_NOMES)


def testes_do_rule_map(rule_map: Path) -> list:
    """[(regra, teste)] das linhas com a coluna Teste preenchida; o `\\|` de uma célula volta a `|`."""
    def celulas(ln):
        return [c.strip().replace("\\|", "|") for c in CELULA.split(ln.strip().strip("|"))]

    cabecalho, saida = None, []
    for ln in rule_map.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("|"):
            continue
        cels = celulas(ln)
        if cabecalho is None:
            cabecalho = cels
            continue
        if set("".join(cels)) <= set("-: "):
            continue  # linha separadora |---|
        if "Teste" not in cabecalho or len(cels) != len(cabecalho):
            continue
        teste = cels[cabecalho.index("Teste")]
        if teste and teste != "—":
            saida.append((cels[0], teste))
    return saida


def lint(define: Path, texto: str):
    """(erros, conserto, linhas de sucesso)."""
    conserto = "corrija o KB Domains com nomes de 'ls sdd/kb/' ou escreva nenhum, e rode de novo"
    valor = valor_do_campo(texto)
    if valor is None:
        return ["falta a linha **KB Domains** no Technical Context"], conserto, []
    nomes = itens(valor)
    if not nomes or valor.lower() in NAO_LISTA or "{" in valor or "}" in valor:
        return ["KB Domains: '%s' não é lista de domínios" % valor], conserto, []
    if any(n.lower() == "nenhum" for n in nomes):
        if len(nomes) > 1:
            return ["KB Domains: 'nenhum' vem sozinho"], conserto, []
        return [], conserto, ["✅ %s: KB Domains válido (nenhum)" % define]

    kb = raiz_do_projeto(define) / "sdd" / "kb"
    if not kb.is_dir():
        return ["KB Domains: sdd/kb/ não existe"], "rode a sdd-kb para criar a base, ou escreva nenhum", []
    existentes = sorted(p.name for p in kb.iterdir() if p.is_dir() and not p.name.startswith("."))
    erros = ["KB Domains: '%s' não existe em sdd/kb/ (%s)" % (n, lista_curta(existentes))
             for n in nomes if n not in existentes]
    if erros:
        return erros, conserto, []

    linhas = ["✅ %s: KB Domains válido (%s)" % (define, ", ".join(nomes))]
    for n in nomes:
        rm = kb / n / "RULE_MAP.md"
        if not rm.is_file():
            continue
        try:
            linhas += ["  %s: %s → %s" % (n, regra, teste) for regra, teste in testes_do_rule_map(rm)]
        except (OSError, UnicodeDecodeError) as e:
            linhas.append("⚠️ %s/RULE_MAP.md: não consegui ler (%s)" % (n, e))
    return [], conserto, linhas


def main(argv: list) -> int:
    if len(argv) != 2 or argv[1].startswith("-") or not Path(argv[1]).is_file():
        print("uso: kb-dominios.py <DEFINE.md>", file=sys.stderr)
        return 64
    define = Path(argv[1])
    try:
        texto = define.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"🛑 {define}: não consegui ler: {e}", file=sys.stderr)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print("→ confira a permissão e a codificação (UTF-8) do arquivo e rode de novo", file=sys.stderr)
        return 1
    erros, conserto, linhas = lint(define, texto)
    if erros:
        for e in erros:
            print(f"🛑 {define}: {e}", file=sys.stderr)
        print("RESULTADO: VERMELHO", file=sys.stderr)
        print(f"→ {conserto}", file=sys.stderr)
        return 1
    for ln in linhas:
        print(ln)
    print("RESULTADO: VERDE")
    if any(ln.startswith("  ") for ln in linhas):
        print("→ ponha estes testes no cmd do Verify Gate, ou registre no DEFINE por que não")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
