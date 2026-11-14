#!/usr/bin/env python3
"""Roda a suíte de tests/ módulo a módulo, por classe de teste, cada uma num processo próprio, com teto, tempo e contagem.

F16W: no Windows (Git Bash + Python nativo) a suíte inteira não cabe num job só, e um módulo pendurado comia o
teto do job inteiro sem dizer qual era. Aqui a unidade é a classe de teste (`modulo.Classe`, lida pelo próprio
unittest, que vê também os testes herdados): cada uma tem o seu teto, a sua linha no relatório e a sua saída
guardada, e um módulo grande (test_sdd_open) se espalha por várias fatias. Módulo que nem importa vira uma unidade
inteira, para o erro aparecer. A suíte se divide em fatias estáveis (--fatia I/N) para rodar em jobs paralelos.

Uso (de quem mantém o pacote; o `init` não copia scripts/ para o projeto do aluno):
  python3 scripts/testes-por-modulo.py [--fatia I/N] [--teto-unidade S] [--paralelo K] [--saida DIR]
                                       [--so a,b] [--pasta DIR] [--lista]
  --fatia I/N       roda só a fatia I de N (1 ≤ I ≤ N); as fatias saem do nº de testes de cada unidade, sempre iguais
  --teto-unidade S  segundos por unidade (padrão 900); estourou ⇒ ela é morta, com os filhos, e conta como TETO
  --paralelo K      unidades ao mesmo tempo (padrão 1)
  --saida DIR       grava a saída inteira de cada unidade em DIR/<unidade>.log e o resumo em DIR/resumo.tsv
  --so a,b          só estes módulos (test_x) ou unidades (test_x.Classe), sem fatiar
  --pasta DIR       a pasta dos testes (padrão: tests/ ao lado deste script)
  --lista           só imprime as unidades da fatia, uma por linha, e sai 0
Exit: 0 todas as unidades verdes · 1 alguma falhou, deu erro ou bateu no teto · 64 uso.
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
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NO_WINDOWS = os.name == "nt"
RAN = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s", re.M)
FINAL = re.compile(r"^(OK|FAILED)(?: \(([^)]*)\))?\s*$", re.M)
QUEDA = re.compile(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", re.M)


def uso(msg: str) -> int:
    print("🛑 testes-por-modulo: " + msg, file=sys.stderr)
    print((__doc__ or "").split("Uso", 1)[1].split("Exit:", 1)[0].rstrip(), file=sys.stderr)
    print("RESULTADO: ERRO DE USO", file=sys.stderr)
    return 64


def _folhas(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _folhas(t)
        else:
            yield t


def unidades(pasta: Path) -> list:
    """(unidade, nº de testes), em ordem de nome. Unidade = `modulo.Classe` pelo id dos testes; a classe herdada de
    outro módulo conta uma vez só, no módulo dela. Módulo que não importa = o próprio módulo, peso 1."""
    sys.path.insert(0, str(pasta))
    cont = {}
    for p in sorted(pasta.glob("test_*.py")):
        try:
            ids = [t.id() for t in _folhas(unittest.defaultTestLoader.loadTestsFromName(p.stem))]
        except Exception:  # noqa: BLE001 — o processo do módulo mostra o erro
            ids = None
        if ids is None or any(i.startswith("unittest.") for i in ids):
            cont[p.stem] = 1
            continue
        for i in ids:
            k = i.rsplit(".", 1)[0]
            cont[k] = cont.get(k, 0) + 1
    return sorted(cont.items())


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
    return "%-44s %-6s testes=%-4d falhas=%-3d erros=%-3d pulados=%-3d %7.1fs" % (
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
            elif a == "--teto-unidade":
                teto = float(next(it))
                if teto <= 0:
                    return uso("--teto-unidade espera segundos > 0")
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
    if not any(pasta.glob("test_*.py")):
        return uso("nenhum test_*.py em %s" % pasta)
    todos = unidades(pasta)
    nomes = [u for u, _ in todos]
    if so is not None:
        fora = [x for x in so if not any(u == x or u.startswith(x + ".") for u in nomes)]
        if fora:
            return uso("módulo ou unidade inexistente: %s" % ", ".join(fora))
        escolhidos = [u for u in nomes if any(u == x or u.startswith(x + ".") for x in so)]
    else:
        escolhidos = fatiar(todos, n)[fatia - 1]
    if lista:
        print("\n".join(escolhidos))
        return 0

    pesos = dict(todos)
    print("fatia %d/%d: %d unidade(s), %d teste(s); teto por unidade %ds; paralelo %d"
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
        cab = "unidade\testado\ttestes\tfalhas\terros\tpulados\tsegundos\n"
        (saida / "resumo.tsv").write_text(cab + "".join(
            "%s\t%s\t%d\t%d\t%d\t%d\t%.1f\n" % (c["nome"], c["estado"], c["testes"], c["falhas"], c["erros"],
                                                c["pulados"], c["segundos"]) for c in feitos), encoding="utf-8")
    print("total: %d unidade(s), %d teste(s): %d falha(s), %d erro(s), %d pulado(s) em %.1fs"
          % (len(feitos), tot["testes"], tot["falhas"], tot["erros"], tot["pulados"], time.monotonic() - inicio))
    if ruins:
        print("unidades com problema: " + ", ".join("%s (%s)" % (c["nome"], c["estado"]) for c in ruins))
        print("RESULTADO: VERMELHO")
        return 1
    print("RESULTADO: VERDE")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
