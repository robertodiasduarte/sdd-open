#!/usr/bin/env python3
"""Roda a suíte de tests/ módulo a módulo, cada um num processo próprio, com tempo, contagem e teto por módulo.

F16W: no Windows (Git Bash + Python nativo) a suíte inteira não cabe num job só, e um módulo pendurado comia o
teto do job inteiro sem dizer qual era. Aqui cada módulo tem o seu teto, a sua linha no relatório e a sua saída
guardada; a suíte se divide em fatias estáveis (--fatia I/N) para rodar em jobs paralelos.

Uso (de quem mantém o pacote; o `init` não copia scripts/ para o projeto do aluno):
  python3 scripts/testes-por-modulo.py [--fatia I/N] [--teto-modulo S] [--paralelo K] [--saida DIR]
                                       [--so m1,m2] [--pasta DIR] [--lista]
  --fatia I/N      roda só a fatia I de N (1 ≤ I ≤ N); as fatias saem do nº de testes de cada módulo, sempre iguais
  --teto-modulo S  segundos por módulo (padrão 900); estourou ⇒ o módulo é morto, com os filhos, e conta como TETO
  --paralelo K     módulos ao mesmo tempo (padrão 1)
  --saida DIR      grava a saída inteira de cada módulo em DIR/<módulo>.log e o resumo em DIR/resumo.tsv
  --so m1,m2       só estes módulos (nome sem .py), sem fatiar
  --pasta DIR      a pasta dos testes (padrão: tests/ ao lado deste script)
  --lista          só imprime os módulos da fatia, um por linha, e sai 0
Exit: 0 todos os módulos verdes · 1 algum módulo falhou, deu erro ou bateu no teto · 64 uso.
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NO_WINDOWS = os.name == "nt"
DEF_TESTE = re.compile(r"^\s+def test_\w*\(", re.M)
RAN = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s", re.M)
FINAL = re.compile(r"^(OK|FAILED)(?: \(([^)]*)\))?\s*$", re.M)
QUEDA = re.compile(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", re.M)


def uso(msg: str) -> int:
    print("🛑 testes-por-modulo: " + msg, file=sys.stderr)
    print((__doc__ or "").split("Uso", 1)[1].split("Exit:", 1)[0].rstrip(), file=sys.stderr)
    print("RESULTADO: ERRO DE USO", file=sys.stderr)
    return 64


def modulos(pasta: Path) -> list:
    """(nome, nº de testes) de cada tests/test_*.py, em ordem de nome."""
    return [(p.stem, len(DEF_TESTE.findall(p.read_text(encoding="utf-8"))))
            for p in sorted(pasta.glob("test_*.py"))]


def fatiar(mods: list, n: int) -> list:
    """N listas de nomes. Maior primeiro, cada um na fatia mais leve (empate: a de menor índice): estável."""
    cargas = [0] * n
    fatias = [[] for _ in range(n)]
    for nome, peso in sorted(mods, key=lambda m: (-m[1], m[0])):
        i = min(range(n), key=lambda k: (cargas[k], k))
        fatias[i].append(nome)
        cargas[i] += max(peso, 1)
    return [sorted(f) for f in fatias]


def contar(saida: str) -> dict:
    """Lê o fim de `python -m unittest -v`: testes, falhas, erros, pulados e os nomes que caíram."""
    c = {"testes": 0, "falhas": 0, "erros": 0, "pulados": 0, "final": "", "quedas": []}
    m = RAN.findall(saida)
    if m:
        c["testes"] = int(m[-1][0])
    f = FINAL.findall(saida)
    if f:
        c["final"] = f[-1][0]
        for parte in (f[-1][1] or "").split(","):
            k, _, v = parte.strip().partition("=")
            if v.isdigit():
                chave = {"failures": "falhas", "errors": "erros", "skipped": "pulados"}.get(k)
                if chave:
                    c[chave] += int(v)
    for t, nome, cls in QUEDA.findall(saida):
        # Python 3.9: "(modulo.Classe)"; 3.11+: "(modulo.Classe.teste)"
        if cls.endswith("." + nome):
            cls = cls[: -len(nome) - 1]
        c["quedas"].append("%s %s.%s" % (t, cls.rsplit(".", 1)[-1], nome))
    return c


def matar_arvore(p: subprocess.Popen) -> None:
    """Mata o processo e os filhos. No Windows, sinal de grupo não existe: taskkill /T leva a árvore (LM-016)."""
    try:
        if NO_WINDOWS:
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL, timeout=60)
        else:
            os.killpg(p.pid, signal.SIGKILL)
    except Exception:  # noqa: BLE001 — já morto, ou sem taskkill: o kill abaixo ainda tenta
        pass
    try:
        p.kill()
    except Exception:  # noqa: BLE001
        pass


def rodar(nome: str, pasta: Path, teto: float) -> dict:
    """Roda um módulo. A saída vai para um arquivo, não para um pipe: um neto vivo segurando o pipe prenderia
    a leitura além do teto (o mesmo defeito do vigia do checar.sh no Windows)."""
    env = dict(os.environ, PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    inicio = time.monotonic()
    with tempfile.TemporaryFile() as out:
        extra = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if NO_WINDOWS else {"start_new_session": True}
        p = subprocess.Popen([sys.executable, "-B", "-m", "unittest", "-v", nome], cwd=str(pasta), env=env,
                             stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT, **extra)
        estourou = False
        try:
            rc = p.wait(timeout=teto)
        except subprocess.TimeoutExpired:
            estourou = True
            matar_arvore(p)
            try:
                rc = p.wait(timeout=60)
            except subprocess.TimeoutExpired:
                rc = -9
        out.seek(0)
        texto = out.read().decode("utf-8", errors="replace")
    c = contar(texto)
    c.update(nome=nome, rc=rc, segundos=time.monotonic() - inicio, saida=texto)
    if estourou:
        c["estado"] = "TETO"
    elif rc == 0 and c["final"] == "OK":
        c["estado"] = "OK"
    elif c["final"] == "FAILED":
        c["estado"] = "FALHOU"
    else:
        c["estado"] = "ERRO"   # não chegou ao resumo do unittest (import quebrado, processo morto)
    return c


def linha(c: dict) -> str:
    return "%-30s %-6s testes=%-4d falhas=%-3d erros=%-3d pulados=%-3d %7.1fs" % (
        c["nome"], c["estado"], c["testes"], c["falhas"], c["erros"], c["pulados"], c["segundos"])


def main(argv: list) -> int:
    fatia, n, teto, paralelo, saida, so, pasta, lista = 1, 1, 900.0, 1, None, None, RAIZ / "tests", False
    it = iter(argv)
    try:
        for a in it:
            if a == "--fatia":
                v = next(it)
                m = re.fullmatch(r"(\d+)/(\d+)", v)
                if not m or not 1 <= int(m.group(1)) <= int(m.group(2)):
                    return uso("--fatia espera I/N com 1 ≤ I ≤ N, veio %r" % v)
                fatia, n = int(m.group(1)), int(m.group(2))
            elif a == "--teto-modulo":
                teto = float(next(it))
                if teto <= 0:
                    return uso("--teto-modulo espera segundos > 0")
            elif a == "--paralelo":
                paralelo = int(next(it))
                if paralelo < 1:
                    return uso("--paralelo espera um inteiro ≥ 1")
            elif a == "--saida":
                saida = Path(next(it))
            elif a == "--so":
                so = [x for x in next(it).split(",") if x]
            elif a == "--pasta":
                pasta = Path(next(it))
            elif a == "--lista":
                lista = True
            else:
                return uso("argumento desconhecido: %s" % a)
    except StopIteration:
        return uso("falta o valor de %s" % a)
    except ValueError:
        return uso("valor que não é número em %s" % a)
    if not pasta.is_dir():
        return uso("pasta de testes não existe: %s" % pasta)
    todos = modulos(pasta)
    if not todos:
        return uso("nenhum test_*.py em %s" % pasta)
    nomes = {m[0] for m in todos}
    if so is not None:
        fora = [x for x in so if x not in nomes]
        if fora:
            return uso("módulo inexistente: %s" % ", ".join(fora))
        escolhidos = sorted(set(so))
    else:
        escolhidos = fatiar(todos, n)[fatia - 1]
    if lista:
        print("\n".join(escolhidos))
        return 0

    pesos = dict(todos)
    print("fatia %d/%d: %d módulo(s), %d teste(s) declarados; teto por módulo %ds; paralelo %d"
          % (fatia, n, len(escolhidos), sum(pesos[x] for x in escolhidos), teto, paralelo), flush=True)
    if saida:
        saida.mkdir(parents=True, exist_ok=True)
    trava = threading.Lock()
    feitos = []

    def um(nome):
        c = rodar(nome, pasta, teto)
        with trava:
            feitos.append(c)
            print(linha(c), flush=True)
            for q in c["quedas"]:
                print("    " + q, flush=True)
            if c["estado"] in ("TETO", "ERRO"):
                for ult in c["saida"].strip().splitlines()[-8:]:
                    print("    | " + ult, flush=True)
            if saida:
                (saida / (nome + ".log")).write_text(c["saida"], encoding="utf-8")

    inicio = time.monotonic()
    with ThreadPoolExecutor(max_workers=paralelo) as ex:
        list(ex.map(um, escolhidos))
    feitos.sort(key=lambda c: c["nome"])
    tot = {k: sum(c[k] for c in feitos) for k in ("testes", "falhas", "erros", "pulados")}
    ruins = [c for c in feitos if c["estado"] != "OK"]
    if saida:
        cab = "modulo\testado\ttestes\tfalhas\terros\tpulados\tsegundos\n"
        (saida / "resumo.tsv").write_text(cab + "".join(
            "%s\t%s\t%d\t%d\t%d\t%d\t%.1f\n" % (c["nome"], c["estado"], c["testes"], c["falhas"], c["erros"],
                                                c["pulados"], c["segundos"]) for c in feitos), encoding="utf-8")
    print("total: %d módulo(s), %d teste(s): %d falha(s), %d erro(s), %d pulado(s) em %.1fs"
          % (len(feitos), tot["testes"], tot["falhas"], tot["erros"], tot["pulados"], time.monotonic() - inicio))
    if ruins:
        print("módulos com problema: " + ", ".join("%s (%s)" % (c["nome"], c["estado"]) for c in ruins))
        print("RESULTADO: VERMELHO")
        return 1
    print("RESULTADO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
