#!/usr/bin/env python3
"""sdd-archive.py — faxina RETROATIVA dos documentos de features fechadas (sdd/features, sdd/reports, sdd/reviews).

O passo 15b da sdd-release arquiva só a feature que acabou de fechar; o passivo é esta operação separada e deliberada.
Tudo é `git mv`: o histórico fica (`git log --follow`). Nunca apaga, nunca commita, nunca toca sdd/releases/,
sdd/archive/ nem subpasta nenhuma (sdd/reports/evidence/ inclusive).

Lotes (uma feature = grupo pelo nome depois do prefixo BRAINSTORM_, DEFINE_, DESIGN_, BUILD_REPORT_, UX_REVIEW_ …):
  com-ledger  o grupo tem sdd/releases/<F>/, quieto há --dias-a (30)        → sdd/archive/<F>/
  sem-ledger  sem ledger, com documento em sdd/features/, quieto há --dias-b (60) → sdd/archive/<F>/
  soltos      report ou review sem esse grupo, quieto há --dias-b           → sdd/archive/_REPORTS_<AAAA-MM>/
"Quieto" = dias desde o último commit do arquivo mais recente do grupo. Protegido = HANDOFF_<F>.md sem ✅ no Status da
ficha, ou nome da feature ou de um documento do grupo citado numa ficha aberta.

Uso:
  sdd-archive.py                          # simulação (o padrão): lista por lote e totais; nada muda
  sdd-archive.py --lote soltos --aplicar  # git mv de 1 lote, staged, para 1 commit por lote
  sdd-archive.py --dias-a 30 --dias-b 60 [--hoje AAAA-MM-DD]
Exit: 0 ok · 2 fora de um repositório, sem sdd/, ou git mv falhou · 64 uso. Python 3.9 stdlib; git >= 2.20.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import os
import re
import subprocess
import sys
import unicodedata

PASTAS = ("features", "reports", "reviews")
# O mais longo primeiro: com FIX antes de FIX_REPORT, FIX_REPORT_F14 viraria a feature REPORT_F14 e escaparia da ficha aberta.
PREFIXOS = "|".join(sorted(("BRAINSTORM", "DEFINE", "DESIGN", "UX_REVIEW", "GOVERNANCA_REVIEW", "BUILD_REPORT", "DRIVE_REPORT", "AVALIACAO",
                            "REVISAO_DESIGN", "REVISAO", "RUNBOOK", "PLANO", "SPEC", "EVIDENCIA", "RELEASE", "CHECKLIST", "ANALISE", "AUDITORIA",
                            "PROPOSTA", "BUILD_PLAN", "FIX", "FIX_REPORT", "SMOKE"), key=len, reverse=True))
SUFIXOS = r"(?:_FIX\d*|_AUDITORIA.*|_\d{4}-\d{2}-\d{2}.*|_\d{8}.*)?"
# Só o slice minúsculo (_s2, _s3b) sai do nome; _V2 e _S4 maiúsculos são nome de feature.
RX = re.compile(r"^(?:" + PREFIXOS + r")_([A-Za-z0-9][A-Za-z0-9_-]*?)(?:_s\d+[a-z]?)?" + SUFIXOS + r"\.md$")
RX_INTEIRO = re.compile(r"^(?:" + PREFIXOS + r")_([A-Za-z0-9][A-Za-z0-9_-]*?)" + SUFIXOS + r"\.md$")
LOTES = ("com-ledger", "sem-ledger", "soltos")


def git(*args):
    return subprocess.run(["git"] + list(args), capture_output=True, stdin=subprocess.DEVNULL)


def texto(b):
    return b.decode("utf-8", "surrogateescape")


def nfc(s):
    """macOS pode devolver o nome decomposto; o git, composto: comparar sempre na mesma forma."""
    return unicodedata.normalize("NFC", s)


def fim(resultado, seta):
    print("RESULTADO: " + resultado)
    print("→ " + seta)


def erro(msg, seta, codigo):
    print("🛑 sdd-archive: " + msg, file=sys.stderr)
    print("RESULTADO: " + ("FALHA" if codigo == 2 else "ERRO DE USO"), file=sys.stderr)
    print("→ " + seta, file=sys.stderr)
    return codigo


def grupo(nome):
    m = RX.match(nome)
    if not m:
        return None, None
    f = RX_INTEIRO.match(nome)
    return m.group(1), (f.group(1) if f else m.group(1))


def data_de(s):
    try:
        return datetime.date.fromisoformat(s)
    except ValueError:
        return None


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.exit(erro(message, "rode --help para ver o uso; nada foi movido.", 64))


def fichas():
    """As fichas abertas: feature → texto."""
    abertas = {}
    pasta = "sdd/handoffs"
    if not os.path.isdir(pasta):
        return abertas
    for nome in sorted(os.listdir(pasta)):
        m = re.match(r"^HANDOFF_(.+)\.md$", nome)
        if not m:
            continue
        with open(os.path.join(pasta, nome), encoding="utf-8", errors="replace") as f:
            corpo = f.read()
        s = re.search(r"^\|\s*\*{0,2}Status\*{0,2}\s*\|\s*([^|\n]*)\|", corpo, re.M)
        if s and s.group(1).strip().startswith("✅"):  # a mesma regra do handoff-lint.py
            continue
        abertas[m.group(1)] = corpo
        # ficha de um slice (HANDOFF_G_s2) protege a feature inteira
        abertas.setdefault(re.sub(r"_s\d+[a-z]?$", "", m.group(1)), corpo)
    return abertas


def main():
    for canal in (sys.stdout, sys.stderr):
        try:
            canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except Exception:
            pass
    ap = Parser(description="Faxina retroativa dos documentos do SDD; simulação por padrão.")
    ap.add_argument("--lote", choices=LOTES)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--dias-a", type=int, default=30)
    ap.add_argument("--dias-b", type=int, default=60)
    ap.add_argument("--hoje", default=None)
    a = ap.parse_args()
    if a.aplicar and not a.lote:
        return erro("--aplicar exige --lote: 1 lote por commit.", "escolha com-ledger, sem-ledger ou soltos; nada foi movido.", 64)
    hoje = datetime.date.today()
    if a.hoje:
        hoje = data_de(a.hoje)
        if hoje is None:
            return erro("--hoje precisa ser AAAA-MM-DD", "corrija e rode de novo; nada foi movido.", 64)
    if a.dias_a < 0 or a.dias_b < 0:
        return erro("--dias-a e --dias-b não podem ser negativos", "corrija e rode de novo; nada foi movido.", 64)
    r = git("rev-parse", "--show-toplevel")
    if r.returncode != 0:
        return erro("esta pasta não é um repositório git.", "rode na raiz do projeto; nada foi movido.", 2)
    os.chdir(texto(r.stdout).strip())
    if not os.path.isdir("sdd"):
        return erro("não achei a pasta sdd/ neste repositório.", "rode no projeto que usa o SDD; nada foi movido.", 2)

    # último commit por arquivo, numa chamada só; -z para nome com acento ou espaço chegar inteiro
    ultimo, atual = {}, None
    r = git("log", "--date=short", "--format=%cd", "--name-only", "--no-renames", "-z", "--", "sdd/features", "sdd/reports", "sdd/reviews")
    for pedaco in texto(r.stdout).split("\0"):
        for ln in pedaco.split("\n"):
            ln = ln.strip("\r")
            if not ln:
                continue
            if data_de(ln):
                atual = ln
            elif nfc(ln) not in ultimo:
                ultimo[nfc(ln)] = atual
    r = git("ls-files", "-z", "--", "sdd/features", "sdd/reports", "sdd/reviews")
    rastreados = set(nfc(p) for p in texto(r.stdout).split("\0") if p)

    r = git("status", "--porcelain", "-z", "--untracked-files=all", "--", "sdd/features", "sdd/reports", "sdd/reviews")
    sujos = set(nfc(reg[3:]) for reg in texto(r.stdout).split("\0") if len(reg) > 3 and not reg.startswith("??"))

    def data_real(p):
        """Sujo é atividade de agora, qualquer que seja o mtime. Sem commit com data (não rastreado, ou só num merge), vale a edição."""
        if nfc(p) in sujos:
            return hoje
        d = data_de(ultimo.get(nfc(p)) or "")
        if d:
            return d
        try:
            return datetime.date.fromtimestamp(os.path.getmtime(p))
        except OSError:
            return None

    def idade(p):
        d = data_real(p)
        return (hoje - d).days if d else 10 ** 6

    def mes_de(p):
        d = data_real(p)
        return d.isoformat()[:7] if d else "0000-00"

    abertas = fichas()
    citado = "\n".join(abertas.values())
    ledger = set(d for d in os.listdir("sdd/releases") if os.path.isdir(os.path.join("sdd/releases", d))) if os.path.isdir("sdd/releases") else set()

    grupos, nomes, sem_grupo, subpastas = collections.defaultdict(list), collections.defaultdict(set), [], []
    for sub in PASTAS:
        base = os.path.join("sdd", sub)
        if not os.path.isdir(base):
            continue
        for nome in sorted(os.listdir(base)):
            p = base + "/" + nome
            if os.path.isdir(p):
                subpastas.append(p)
                continue
            if nome == ".gitkeep" or not os.path.isfile(p):
                continue
            g, inteiro = grupo(nome)
            if g:
                grupos[g].append(p)
                nomes[g].update((g, inteiro))
            else:
                sem_grupo.append(p)

    def ficha_do_nome(nome):
        """A ficha aberta cujo nome aparece no nome do arquivo, como palavra inteira, em qualquer caixa: `F1` não casa `F14`,
        e REVISAO_FRONTEIRA_F14_DRIVE_20261105.md é da F14_DRIVE. Proteger demais é o lado seguro."""
        for n in sorted(abertas):
            if re.search(r"(?<![^\W_])" + re.escape(nfc(n)) + r"(?![^\W_])", nfc(nome), re.I):
                return n
        return ""

    def protecao(g, arquivos):
        for p in arquivos:
            n = ficha_do_nome(os.path.splitext(os.path.basename(p))[0])
            if n:
                return "ficha aberta em HANDOFF_%s.md" % n
        for n in sorted(nomes[g]):
            if re.search(r"(?<![A-Z0-9_])" + re.escape(n) + r"(?![A-Z0-9_])", citado):
                return "citada numa ficha aberta"
        for p in arquivos:
            if os.path.basename(p) in citado:
                return "documento citado numa ficha aberta"
        return ""

    lotes = dict((L, []) for L in LOTES)
    protegidos, recentes, nao_class = [], [], []
    for g, arquivos in sorted(grupos.items()):
        q = min(idade(p) for p in arquivos)
        pq = protecao(g, arquivos)
        if pq:
            protegidos.append((g, len(arquivos), pq))
            continue
        com_ledger = sorted(nomes[g] & ledger)
        if com_ledger:
            if q >= a.dias_a:
                lotes["com-ledger"] += [(p, "sdd/archive/%s/%s" % (com_ledger[0], os.path.basename(p))) for p in arquivos]
            else:
                recentes.append((g, len(arquivos), q, a.dias_a))
        elif any("/features/" in p for p in arquivos):
            if q >= a.dias_b:
                lotes["sem-ledger"] += [(p, "sdd/archive/%s/%s" % (g, os.path.basename(p))) for p in arquivos]
            else:
                recentes.append((g, len(arquivos), q, a.dias_b))
        elif q >= a.dias_b:
            for p in arquivos:
                lotes["soltos"].append((p, "sdd/archive/_REPORTS_%s/%s" % (mes_de(p), os.path.basename(p))))
        else:
            recentes.append((g, len(arquivos), q, a.dias_b))
    for p in sem_grupo:
        n = ficha_do_nome(os.path.splitext(os.path.basename(p))[0])
        if n:
            protegidos.append((os.path.basename(p), 1, "ficha aberta em HANDOFF_%s.md" % n))
        elif os.path.basename(p) in citado or p in citado:
            protegidos.append((os.path.basename(p), 1, "documento citado numa ficha aberta"))
        elif "/features/" not in p and idade(p) >= a.dias_b:
            lotes["soltos"].append((p, "sdd/archive/_REPORTS_%s/%s" % (mes_de(p), os.path.basename(p))))
        else:
            nao_class.append(p)

    for L in ([a.lote] if a.lote else LOTES):
        print("\n== Lote %s: %d arquivo(s) ==" % (L, len(lotes[L])))
        for src, dst in lotes[L]:
            print("  %s  →  %s%s" % (src, dst, "" if nfc(src) in rastreados else "  ⚠️ não rastreado: pulo"))
    if not a.lote:
        print("\n== Protegidos: %d grupo(s) ==" % len(protegidos))
        for g, n, pq in protegidos:
            print("  %s (%d documento(s)): %s" % (g, n, pq))
        print("\n== Recentes (ficam): %d grupo(s) ==" % len(recentes))
        for g, n, q, lim in recentes:
            print("  %s (%d documento(s), quieto há %d dia(s), limite %d)" % (g, n, q, lim))
        print("\n== Sem classificação (decisão sua): %d ==" % len(nao_class))
        for p in nao_class:
            print("  " + p)
        print("\n== Subpastas (ficam): %d ==" % len(subpastas))
        for p in subpastas:
            print("  %s/" % p)
    print("\nTOTAIS: " + " · ".join("%s=%d" % (L, len(lotes[L])) for L in LOTES)
          + " · protegidos=%d · recentes=%d · sem classificação=%d · subpastas=%d" % (len(protegidos), len(recentes), len(nao_class), len(subpastas)))
    if not a.aplicar:
        print("Nada foi movido.")
        fim("SIMULACAO", "para mover, rode com --lote <nome> --aplicar, um lote por vez.")
        return 0

    movidos = 0
    for src, dst in lotes[a.lote]:
        if nfc(src) not in rastreados:
            continue
        if os.path.exists(dst):
            print("⚠️ destino já existe, pulei: %s" % dst, file=sys.stderr)
            continue
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
        except OSError as e:
            return erro("não consegui criar a pasta de %s: %s" % (dst, e), "os anteriores ficam staged; confira e rode de novo.", 2)
        r = git("mv", "--", src, dst)
        if r.returncode != 0:
            return erro("git mv falhou em %s: %s" % (src, texto(r.stderr).strip()), "os anteriores ficam staged; confira e rode de novo.", 2)
        movidos += 1
    print("✅ movi %d arquivo(s) com git mv; nada foi apagado." % movidos)
    fim("MOVIDO", "revise com git status e commite este lote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
