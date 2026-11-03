#!/usr/bin/env python3
"""governanca-bloco.py — confere o bloco <<<GOVERNANCA … >>> que o revisor fresco devolve ao passo 11 do
sdd-define, contra o relatório gravado e a saída da fronteira. Só stdlib, Python >= 3.9.

Uso:
    python3 sdd/bin/governanca-bloco.py <resposta.txt> --saida <caminho do relatório> [--comparar <saída.txt>]
      <resposta.txt>   a resposta do revisor (o último bloco <<<GOVERNANCA … >>> é o que vale)
      --saida          o `saida:` mandado ao revisor (caminho do relatório)
      --comparar       a saída de `governanca-fronteira.sh --comparar` (linhas MUDOU:/FORA:)

Confere: o par <<<GOVERNANCA / >>>; `resultado:` em NA | REVISADO | PADRAO_AUSENTE | FALHA; `motivo:` não vazio;
`relatorio:` igual ao --saida quando REVISADO e `—` nos outros; cada `lacuna:` com os 3 campos fixos
(`Gnn | alta|média|baixa | AT-0nn[, AT-0nn…]|—`) seguida de `muda:` e `porque:`; REVISADO ⇒ o relatório existe e o
conjunto de Gnn do bloco é igual ao dos títulos `### Gnn — ` de `## Lacunas`; com --comparar, REVISADO exige
`MUDOU: <saida>` e os outros resultados não podem ter mudado o relatório.

Exit: 0 bloco válido (NA, REVISADO ou PADRAO_AUSENTE) · 1 bloco válido com `resultado: FALHA` · 2 bloco inválido
(conta como falha: 1 redespacho) · 64 uso.
"""
from __future__ import annotations

import os
import re
import sys

RESULTADOS = ("NA", "REVISADO", "PADRAO_AUSENTE", "FALHA")
LACUNA = re.compile(r"^G\d+ \| (alta|média|baixa) \| (AT-\d{3}(, AT-\d{3})*|—)$")
TITULO = re.compile(r"^### (G\d+) — ")


def uso(msg: str) -> None:
    sys.stderr.write("🛑 " + msg + "\n" + __doc__.split("Confere:")[0])
    print("RESULTADO: ERRO DE USO\n→ chame com <resposta.txt> --saida <relatório> [--comparar <saída>].")
    sys.exit(64)


def ler(p: str) -> str:
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def mesmo(a: str, b: str) -> bool:
    return a == b or os.path.realpath(a) == os.path.realpath(b)


def bloco(texto: str):
    ini = texto.rfind("<<<GOVERNANCA")
    if ini < 0:
        return None
    fim = texto.find(">>>", ini)
    if fim < 0:
        return None
    return [l.strip() for l in texto[ini + len("<<<GOVERNANCA"):fim].splitlines() if l.strip()]


def lacunas_do_relatorio(p: str) -> set:
    dentro, ids = False, set()
    for l in ler(p).splitlines():
        if l.startswith("## "):
            dentro = l.strip() == "## Lacunas"
            continue
        m = TITULO.match(l) if dentro else None
        if m:
            ids.add(m.group(1))
    return ids


def main(argv: list) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        uso("informe a resposta do revisor")
    resp, saida, comparar = argv[0], None, None
    i = 1
    while i < len(argv):
        if argv[i] in ("--saida", "--comparar") and i + 1 < len(argv):
            if argv[i] == "--saida":
                saida = argv[i + 1]
            else:
                comparar = argv[i + 1]
            i += 2
        else:
            uso("argumento desconhecido ou sem valor: " + argv[i])
    if saida is None:
        uso("--saida é obrigatório")
    if not os.path.isfile(resp) or (comparar is not None and not os.path.isfile(comparar)):
        uso("arquivo inexistente: " + (resp if not os.path.isfile(resp) else comparar))

    erros = []
    linhas = bloco(ler(resp))
    if linhas is None:
        erros.append("sem o par <<<GOVERNANCA / >>>")
        linhas = []
    campos, trios, k = {}, [], 0
    while k < len(linhas):
        chave, _, valor = linhas[k].partition(":")
        chave, valor = chave.strip(), valor.strip()
        if chave == "lacuna":
            muda = linhas[k + 1] if k + 1 < len(linhas) else ""
            porque = linhas[k + 2] if k + 2 < len(linhas) else ""
            if not LACUNA.match(valor):
                erros.append("lacuna sem os 3 campos fixos (Gnn | severidade | AT ou —): " + valor)
            if not (muda.startswith("muda:") and muda[5:].strip() and porque.startswith("porque:") and porque[7:].strip()):
                erros.append("lacuna " + valor.split(" ")[0] + " sem as linhas muda: e porque: logo depois")
            trios.append(valor.split(" ")[0])
            k += 3
            continue
        if chave in ("muda", "porque"):
            erros.append(chave + ": fora de um trio lacuna:/muda:/porque:")
        elif chave:
            campos.setdefault(chave, valor)
        k += 1

    if linhas == [] and not erros:
        erros.append("bloco <<<GOVERNANCA vazio")
    res = campos.get("resultado", "")
    if linhas and res not in RESULTADOS:
        erros.append("resultado fora de NA | REVISADO | PADRAO_AUSENTE | FALHA: '" + res + "'")
    if linhas and not campos.get("motivo"):
        erros.append("motivo: vazio")
    repetidas = sorted(g for g in set(trios) if trios.count(g) > 1)
    if repetidas:
        erros.append("lacuna repetida no bloco: " + ", ".join(repetidas) + " (cada Gnn aparece uma vez)")
    rel = campos.get("relatorio", "")
    if res == "REVISADO":
        if not mesmo(rel, saida):
            erros.append("REVISADO com relatorio: diferente do saida: ('" + rel + "' ≠ '" + saida + "')")
        if not os.path.isfile(saida):
            erros.append("REVISADO, mas o relatório não existe: " + saida)
        else:
            no_rel = lacunas_do_relatorio(saida)
            if set(trios) != no_rel:
                erros.append("as lacunas do bloco (" + ", ".join(sorted(set(trios))) + ") não batem com os títulos de ## Lacunas do relatório ("
                             + ", ".join(sorted(no_rel)) + ")")
    elif res in RESULTADOS:
        if rel not in ("—", "-", ""):
            erros.append(res + " com relatorio: preenchido ('" + rel + "'); esperado —")
        if trios:
            erros.append(res + " com linhas lacuna:")
    if comparar is not None and res in RESULTADOS:
        mudou = [l[len("MUDOU: "):].strip() for l in ler(comparar).splitlines() if l.startswith("MUDOU: ")]
        gravou = any(mesmo(m, saida) for m in mudou)
        if res == "REVISADO" and not gravou:
            erros.append("REVISADO, mas a fronteira não mostra MUDOU: " + saida)
        if res != "REVISADO" and gravou:
            erros.append(res + ", mas o revisor gravou o relatório (MUDOU: " + saida + ")")

    if erros or res not in RESULTADOS:
        if res not in RESULTADOS and not erros:
            erros.append("resultado ausente")
        for e in erros:
            print("  🛑 " + e)
        print("RESULTADO: BLOCO INVÁLIDO\n→ conte como falha da revisão: 1 redespacho fresco com os mesmos 5 campos.")
        return 2
    acao = {
        "NA": "escreva a linha | **Governança** | N.A. — <motivo> | … | e tire o marcador de governança.",
        "REVISADO": "pergunte uma lacuna por vez (" + str(len(trios)) + ") e aplique as escolhidas.",
        "PADRAO_AUSENTE": "pergunte os 5 campos do padrão do projeto, grave-o e despache de novo (não conta como falha).",
        "FALHA": "conte como falha da revisão: 1 redespacho fresco com os mesmos 5 campos.",
    }[res]
    print("✅ bloco <<<GOVERNANCA válido: resultado " + res + ", " + str(len(trios)) + " lacuna(s)")
    print("RESULTADO: " + res + "\n→ " + acao)
    return 1 if res == "FALHA" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
