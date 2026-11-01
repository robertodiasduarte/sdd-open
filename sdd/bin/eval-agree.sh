#!/usr/bin/env bash
# eval-agree.sh — taxa de AGREE de cada auditor nas revisões adversariais que o projeto JÁ fez: lê as pastas
# EXTERNAL_REVIEW_*/ (META.txt + auditor.verdicts.jsonl) e conta, por auditor (engine e modelo), quantas vezes ele
# concordou, discordou com evidência, discordou por preocupação e achou algo novo. Doc: docs/adversarial-review.md.
#
# Por que existe: um auditor que só concorda não audita. A taxa sai daqui; o julgamento é de quem lê. Este script
# nunca chama engine e nunca usa rede: só lê arquivos.
#
# USO-INICIO
#   eval-agree.sh [<pasta-das-revisões>]
#       padrão: review.output_dir do sdd/config.yaml da raiz git (sdd/reports/reviews se vazio)
#       taxa_agree = AGREE / (AGREE + DISAGREE_EVIDENCE + DISAGREE_CONCERN), 1 casa; NOVO fica em coluna própria
#       0 MEDIDO · 2 SEM DADOS (nenhuma revisão com auditoria completa, ou a pasta padrão ainda não existe)
#       64 uso, ou a pasta passada não existe
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · núcleo em Python 3.9 stdlib.

set -u

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 eval-agree: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: PAROU\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
fi

exec python3 -B - "$@" <<'PY'
import json, os, re, subprocess, sys

TIPOS = ("AGREE", "DISAGREE_EVIDENCE", "DISAGREE_CONCERN", "NOVO")


def para(motivo):
    print("🛑 eval-agree: " + motivo, file=sys.stderr)
    print("RESULTADO: PAROU\n→ rode `eval-agree.sh --help` para ver o uso.", file=sys.stderr)
    sys.exit(64)


def ler(p):
    try:
        with open(p, encoding="utf-8") as h:
            return h.read()
    except (OSError, UnicodeDecodeError):
        return None


args = sys.argv[1:]
if len(args) > 1:
    para("argumento a mais: " + args[1])
if args and args[0].startswith("-"):
    para("opção desconhecida: " + args[0])

if args:
    pasta = os.path.abspath(args[0])
else:
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
        raiz = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else os.getcwd()
    except OSError:
        raiz = os.getcwd()   # sem git no PATH: a pasta atual é a raiz
    rel = "sdd/reports/reviews"
    no_bloco = False
    for ln in (ler(os.path.join(raiz, "sdd/config.yaml")) or "").splitlines():
        if re.match(r"^\S", ln):
            no_bloco = ln.split("#", 1)[0].strip() == "review:"
            continue
        m = re.match(r"^\s+output_dir\s*:\s*(.*?)\s*$", ln)
        if no_bloco and m:
            v = m.group(1).split(" #", 1)[0].strip().strip('"').strip("'")
            if v:
                rel = v
    pasta = rel if os.path.isabs(rel) else os.path.join(raiz, rel)
if not os.path.isdir(pasta) and args:
    para("a pasta %s não existe" % pasta)
# a pasta padrão ainda não existe num projeto que nunca rodou uma revisão: é "sem dados", não erro de uso

por, fora, lidas = {}, [], 0
for d in sorted(os.listdir(pasta) if os.path.isdir(pasta) else []):
    if not d.startswith("EXTERNAL_REVIEW_") or not os.path.isdir(os.path.join(pasta, d)):
        continue
    lidas += 1
    meta = {}
    for ln in (ler(os.path.join(pasta, d, "META.txt")) or "").splitlines():
        m = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if m:
            meta[m.group(1)] = m.group(2)
    if not meta:
        fora.append((d, "META ilegível"))
        continue
    if meta.get("auditor_exit") != "0":
        fora.append((d, "auditor_exit %s" % meta.get("auditor_exit", "-")))
        continue
    texto = ler(os.path.join(pasta, d, "auditor.verdicts.jsonl"))
    if texto is None:
        fora.append((d, "sem auditor.verdicts.jsonl"))
        continue
    # o mesmo auditor numa linha só: nem o slug no id (openrouter:<modelo>) nem o provedor que a OpenRouter
    # escolheu (" via …") partem a conta — a linha é engine base + modelo que respondeu
    quem = "%s (%s)" % (meta.get("auditor_engine_efetivo", "-").split(":", 1)[0],
                        meta.get("auditor_modelo", "-").split(" via ", 1)[0])
    c = por.setdefault(quem, {"revisoes": 0, **{t: 0 for t in TIPOS}})
    c["revisoes"] += 1
    for ln in texto.splitlines():
        try:
            v = (json.loads(ln) or {}).get("veredito")
        except (ValueError, AttributeError):
            continue
        if v in TIPOS:
            c[v] += 1

print("eval-agree — taxa de AGREE por auditor (%d pasta(s) lida(s) em %s)" % (lidas, pasta))
if not por:
    if fora:
        print("fora da conta: %d (%s)" % (len(fora), "; ".join("%s: %s" % x for x in fora)))
    print("RESULTADO: SEM DADOS")
    print("→ nenhuma revisão com auditoria completa nesta pasta: rode adversarial-review.sh e meça de novo.")
    sys.exit(2)
print("")
print("| Auditor | Revisões | Vereditos | AGREE | DISAGREE_EVIDENCE | DISAGREE_CONCERN | NOVO | taxa_agree |")
print("|---|---:|---:|---:|---:|---:|---:|---:|")
for quem in sorted(por):
    c = por[quem]
    base = c["AGREE"] + c["DISAGREE_EVIDENCE"] + c["DISAGREE_CONCERN"]
    taxa = ("%.1f%%" % (100.0 * c["AGREE"] / base)) if base else "n/a"
    print("| %s | %d | %d | %d | %d | %d | %d | %s |" % (quem, c["revisoes"], base + c["NOVO"], c["AGREE"],
                                                         c["DISAGREE_EVIDENCE"], c["DISAGREE_CONCERN"], c["NOVO"], taxa))
print("")
print("fora da conta: %d%s" % (len(fora), (" (" + "; ".join("%s: %s" % x for x in fora) + ")") if fora else ""))
print("RESULTADO: MEDIDO")
print("→ uma taxa_agree alta com poucos DISAGREE pode ser auditor complacente: compare com outra engine no papel de "
      "auditor.")
PY
