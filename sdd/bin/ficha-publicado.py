#!/usr/bin/env python3
"""ficha-publicado.py — escreve o bloco "Publicado" da ficha da feature a partir dos ledgers.

A ficha (sdd/handoffs/HANDOFF_<F>.md) e o ledger (sdd/releases/<F>/*.yaml) contavam a mesma publicação duas vezes,
escritas à mão. O ledger é a fonte; este script projeta uma linha por release na ficha, entre os marcadores, e não
toca mais nada. Rodar de novo dá o mesmo arquivo, byte a byte. O agente escreve na ficha só o que o ledger não diz:
"Falta", alertas e eventos.

Uso:
    python3 sdd/bin/ficha-publicado.py <FEATURE> [--ficha <arquivo>] [--releases <pasta>]
        --ficha     padrão sdd/handoffs/HANDOFF_<FEATURE>.md (criada com o mínimo se não existir)
        --releases  padrão sdd/releases/<FEATURE>

Linha: - <data> · <slice> · <versão> · <estado> · <veredito> · deploy <no-op|real> · trilha <curta|completa> · <sha>
(a mais recente no topo; o sha é o do commit que trouxe o ledger, `git log --diff-filter=A`; sem git, `sha n/d`).
Ledger ilegível: `- n/d (ledger ilegível: <arquivo>)`, e o exit é 2 (a ficha é gravada com as outras linhas).

Exit: 0 bloco gravado (ou já igual) · 1 nenhum ledger da feature (nada gravado) · 2 ledger ilegível ou ficha que não
dá para ler ou gravar · 64 uso. Python 3.9 stdlib.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

INI = "<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->"
FIM = "<!-- publicado:fim -->"
RE_INI = re.compile(r"<!-- publicado:inicio\b[^>]*-->")
RE_FEATURE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$")
RE_CHAVE = re.compile(r"^([a-z_]+):[ \t]*(.*?)[ \t]*$")
CAMPOS = ("data", "slice_id", "versao", "estado", "veredito", "deploy", "trilha")
USO = "uso: ficha-publicado.py <FEATURE> [--ficha <arquivo>] [--releases <pasta>]"


def fim(resultado, seta, canal=None):
    print("RESULTADO: " + resultado, file=canal or sys.stdout)
    print("→ " + seta, file=canal or sys.stdout)


def uso(motivo):
    print("🛑 ficha-publicado: " + motivo, file=sys.stderr)
    print(USO, file=sys.stderr)
    fim("PAROU", "corrija a chamada; nada foi gravado.", sys.stderr)
    return 64


def valor(v):
    """Escalar simples do ledger: sem o comentário, sem aspas. Aspas sem fechar ⇒ None (o ledger é ilegível)."""
    if v[:1] in ('"', "'"):
        q = v[0]
        j = v.find(q, 1)
        return v[1:j] if j > 0 else None
    return re.sub(r"\s+#.*$", "", v).strip()


def le_ledger(caminho):
    """dict com os campos de 1º nível, ou None se o arquivo não é um ledger legível."""
    try:
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
    except (OSError, UnicodeDecodeError):
        return None
    d = {}
    for ln in texto.splitlines():
        if not ln or ln[0] in " \t#-":
            continue
        m = RE_CHAVE.match(ln)
        if m:
            v = valor(m.group(2))
            if v is None:
                return None
            d[m.group(1)] = v
    if not d.get("feature_id") or not d.get("estado"):
        return None
    # um valor com quebra ou com "·" desmontaria a linha da ficha
    for k in CAMPOS:
        if k in d and ("·" in d[k] or "\n" in d[k] or "<!--" in d[k] or "-->" in d[k]):
            return None
    return d


def sha_do(caminho, raiz):
    try:
        r = subprocess.run(["git", "log", "--diff-filter=A", "--format=%h", "-1", "--", caminho], cwd=raiz,
                           capture_output=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                           timeout=60)
    except (OSError, subprocess.SubprocessError):
        return "sha n/d"
    s = r.stdout.strip() if r.returncode == 0 else ""
    return s if re.fullmatch(r"[0-9a-f]{7,12}", s) else "sha n/d"


def mostra(caminho, raiz):
    """Caminho relativo à raiz; fora dela, só o nome (um caminho de home na ficha iria para o git)."""
    rel = os.path.relpath(caminho, raiz)
    return os.path.basename(caminho) if rel.startswith("..") or os.path.isabs(rel) else rel.replace(os.sep, "/")


def linhas_do_bloco(pasta, raiz):
    itens, ilegiveis = [], []
    for nome in sorted(os.listdir(pasta)):
        caminho = os.path.join(pasta, nome)
        if not nome.endswith((".yaml", ".yml")) or not os.path.isfile(caminho):
            continue
        rel = mostra(caminho, raiz)
        d = le_ledger(caminho)
        if d is None:
            ilegiveis.append(rel)
            itens.append(("", nome, "- n/d (ledger ilegível: %s)" % rel))
            continue
        partes = [d.get("data") or "data n/d", d.get("slice_id") or "slice n/d"]
        if d.get("versao"):
            partes.append(d["versao"])
        partes += [d.get("estado"), d.get("veredito") or "veredito n/d",
                   "deploy " + (d.get("deploy") or "n/d"), "trilha " + (d.get("trilha") or "completa"),
                   sha_do(rel, raiz)]
        itens.append((d.get("data") or "", nome, "- " + " · ".join(partes)))
    # a mais recente no topo: data, depois o nome do arquivo (o ilegível, sem data, vai para o fim)
    itens.sort(key=lambda t: (t[0], t[1]), reverse=True)
    return [t[2] for t in itens], ilegiveis


def substitui_bloco(texto, linhas):
    bloco = INI + "\n" + "\n".join(linhas) + "\n" + FIM
    m = RE_INI.search(texto)
    if m and FIM in texto[m.end():]:
        b = texto.index(FIM, m.end()) + len(FIM)
        return texto[:m.start()] + bloco + texto[b:]
    secao = "## Publicado\n\n" + bloco + "\n\n"
    for ancora in ("\n## Feito", "\n## Falta"):
        i = texto.find(ancora)
        if i >= 0:
            return texto[:i + 1] + secao + texto[i + 1:]
    m = re.search(r"\n## (?!Ficha\b)", texto)
    if m:
        return texto[:m.start() + 1] + secao + texto[m.start() + 1:]
    return texto.rstrip("\n") + "\n\n" + secao.rstrip("\n") + "\n"


def ficha_minima(feature):
    return ("# HANDOFF: %s\n\n## Ficha\n\n| Attribute | Value |\n|-----------|-------|\n| **Feature** | %s |\n\n"
            "## Falta\n\n- nada registrado\n" % (feature, feature))


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if args else 64
    feature, args = args[0], args[1:]
    if not RE_FEATURE.match(feature):
        return uso("FEATURE inválida: '%s'" % feature)
    ficha = releases = None
    while args:
        if args[0] in ("--ficha", "--releases") and len(args) >= 2 and args[1]:
            if args[0] == "--ficha":
                ficha = args[1]
            else:
                releases = args[1]
            args = args[2:]
        else:
            return uso("opção desconhecida ou sem valor: " + args[0])
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, encoding="utf-8",
                           errors="replace", stdin=subprocess.DEVNULL, timeout=60)
        raiz = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()
    except (OSError, subprocess.SubprocessError):
        raiz = os.getcwd()
    ficha = os.path.abspath(ficha or os.path.join(raiz, "sdd", "handoffs", "HANDOFF_%s.md" % feature))
    releases = os.path.abspath(releases or os.path.join(raiz, "sdd", "releases", feature))
    if not os.path.isdir(releases) or not any(n.endswith((".yaml", ".yml")) for n in os.listdir(releases)):
        print("⚠️ nenhum ledger em %s" % mostra(releases, raiz), file=sys.stderr)
        fim("SEM LEDGER", "a ficha não mudou; o bloco Publicado só existe depois do 1º ledger da feature.")
        return 1
    linhas, ilegiveis = linhas_do_bloco(releases, raiz)
    try:
        if os.path.exists(ficha):
            with open(ficha, encoding="utf-8", newline="") as f:
                antes = f.read()
        else:
            antes = ficha_minima(feature)
        depois = substitui_bloco(antes, linhas)
        if depois != antes or not os.path.exists(ficha):
            os.makedirs(os.path.dirname(ficha), exist_ok=True)
            with open(ficha, "w", encoding="utf-8", newline="") as f:
                f.write(depois)
    except (OSError, UnicodeDecodeError) as e:
        print("🛑 não consegui ler ou gravar %s: %s" % (ficha, e), file=sys.stderr)
        fim("FALHOU", "confira a permissão e a codificação (UTF-8) da ficha; nada foi gravado.")
        return 2
    print("bloco Publicado: %d linha(s) em %s" % (len(linhas), mostra(ficha, raiz)))
    for rel in ilegiveis:
        print("🛑 ledger ilegível: %s (a linha dele diz n/d)" % rel, file=sys.stderr)
    if ilegiveis:
        fim("LEDGER ILEGÍVEL", "conserte o ledger citado e rode de novo; as outras linhas já estão na ficha.")
        return 2
    fim("GRAVADO", "escreva na ficha só o que o ledger não diz: Falta, alertas e eventos.")
    return 0


if __name__ == "__main__":
    # No Windows, o stdout num pipe (o Git Bash do aluno) é cp1252 e o print troca \n por \r\n (LM-015).
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv))
