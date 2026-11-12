#!/usr/bin/env python3
"""Trava do que o sdd-open gera neste repositório: nada gerado se edita aqui.

O sdd-open (https://github.com/robertodiasduarte/sdd-open) gera, de uma tag publicada, parte deste repositório:
as skills que têm `skills/<nome>/GERADO.txt`, o README.md, scripts/ e .github/workflows/. Quem quer mudar um
desses arquivos muda no sdd-open e gera de novo; mudança feita aqui some na geração seguinte, e esta trava a
recusa antes disso.

Confere:
  - GERADO.txt da raiz: cada arquivo listado existe e tem o sha256 listado (inclui o GERADO.txt de cada skill
    gerada: apagar uma skill gerada inteira aparece como "falta"); scripts/ e .github/workflows/ não têm arquivo
    a mais; sem o GERADO.txt da raiz, falha;
  - skills/<nome>/GERADO.txt: cada arquivo listado existe e tem o sha256 listado, e a pasta não tem arquivo
    a mais (fora o próprio GERADO.txt, .DS_Store e __pycache__/).

Formato de cada GERADO.txt: linhas "# …" de comentário e "<sha256>  <caminho relativo à pasta do arquivo>",
o mesmo do `shasum -a 256`.

Uso: python3 scripts/check-gerado.py [raiz]      (padrão: a pasta acima deste script)
Exit: 0 tudo igual · 1 arquivo gerado mudou, falta ou sobra · 64 GERADO.txt ilegível. Só biblioteca padrão, sem rede.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

LINHA = re.compile(r"^([0-9a-f]{64})  (\S.*)$")
IGNORA = {"GERADO.txt", ".DS_Store"}
DONO_INTEIRO = ("scripts", ".github/workflows")


class Ilegivel(Exception):
    pass


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ler_lista(arq: Path) -> dict[str, str]:
    lista: dict[str, str] = {}
    for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip() or linha.startswith("#"):
            continue
        m = LINHA.match(linha)
        if not m or m.group(2).startswith("/") or ".." in Path(m.group(2)).parts:
            raise Ilegivel("%s:%d: linha fora do formato '<sha256>  <caminho relativo>'" % (arq, n))
        lista[m.group(2)] = m.group(1)
    if not lista:
        raise Ilegivel("%s: nenhum arquivo listado" % arq)
    return lista


def conferir(base: Path, lista: dict[str, str], rotulo: str) -> list[str]:
    erros = []
    for rel, esperado in sorted(lista.items()):
        p = base / rel
        if not p.is_file():
            erros.append("%s%s: falta" % (rotulo, rel))
        elif sha(p) != esperado:
            erros.append("%s%s: mudou" % (rotulo, rel))
    return erros


def sobras(pasta: Path, lista: dict[str, str], rotulo: str) -> list[str]:
    erros = []
    for p in sorted(pasta.rglob("*")):
        if not p.is_file() or p.name in IGNORA or "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        rel = p.relative_to(pasta).as_posix()
        if rel not in lista:
            erros.append("%s%s: sobra" % (rotulo, rel))
    return erros


def main(argv: list[str]) -> int:
    raiz = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    erros: list[str] = []
    try:
        topo = raiz / "GERADO.txt"
        if not topo.is_file():
            erros.append("GERADO.txt: falta (a geração do sdd-open grava este arquivo na raiz)")
        else:
            lista_raiz = ler_lista(topo)
            erros += conferir(raiz, lista_raiz, "")
            # scripts/ e .github/workflows/ são inteiros do gerador: arquivo a mais lá também é mudança feita aqui
            for pasta in DONO_INTEIRO:
                if (raiz / pasta).is_dir():
                    sub = {k[len(pasta) + 1:]: v for k, v in lista_raiz.items() if k.startswith(pasta + "/")}
                    erros += sobras(raiz / pasta, sub, pasta + "/")
        skills = sorted(p.parent for p in (raiz / "skills").glob("*/GERADO.txt"))
        for pasta in skills:
            lista = ler_lista(pasta / "GERADO.txt")
            rotulo = "skills/%s/" % pasta.name
            erros += conferir(pasta, lista, rotulo) + sobras(pasta, lista, rotulo)
    except (Ilegivel, OSError, UnicodeDecodeError) as e:
        print("🛑 %s" % e)
        print("RESULTADO: ERRO DE LEITURA")
        print("→ gere de novo pelo sdd-open (python3 scripts/gerar-starter.py --tag <vX.Y.Z> <este repositório>).")
        return 64
    if erros:
        for e in erros:
            print("🛑 %s" % e)
        print("RESULTADO: ARQUIVO GERADO MUDOU AQUI")
        print("→ desfaça a mudança aqui; para mudar de verdade, mude no sdd-open e gere de novo.")
        return 1
    print("✅ %d skill(s) gerada(s) e a infra conferidas: tudo igual ao que o sdd-open gerou" % len(skills))
    print("RESULTADO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
