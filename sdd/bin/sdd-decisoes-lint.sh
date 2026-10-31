#!/usr/bin/env bash
# sdd-decisoes-lint.sh — confere as perguntas de decisão das skills e dos fragmentos do SDD Open.
#
# Por que existe: o fluxo encadeado só para em decisão da pessoa (D1–D5); uma pergunta sem classe é
# uma parada que ninguém decidiu que existe, e uma marca sem o rótulo é jargão no lugar mais visível
# da resposta. Formato e marcas: sdd/templates/fragments/PERGUNTA_DECISAO.md (item 9, dono único).
#
# USO-INICIO
#   sdd-decisoes-lint.sh --sites <pasta|arquivo.md>…
#       Toda pergunta de decisão (negrito terminado em `?` seguido de opções `- **rótulo** — efeito`, na
#       linha do **Sua decisão**; blocos ```markdown contam, outros blocos cercados não) precisa de:
#       exatamente 1 marca `[<código> · <rótulo>]` logo antes da pergunta, com o rótulo da tabela do
#       item 9 · exatamente 1 opção (recomendado), a primeira · a opção **não sei** · nenhuma opção
#       **Outro** · nenhum identificador técnico (AT-n, LM-n, Dn, SHA) fora do `(ref: …)` final.
#   sdd-decisoes-lint.sh --self-test
#       as 4 fixtures de sdd/fixtures/conversa/decisoes/ reprovam pelo motivo certo e o controle passa.
# USO-FIM
#
# Exit: 0 ok · 2 violação (arquivo:linha — motivo) · 64 uso, caminho inexistente, tabela de marcas
# ausente ou nenhuma pergunta encontrada (nada conferido nunca é verde).
# ⚠️ bash 3.2 · o núcleo é Python 3.9 stdlib e importa o perguntas() de sdd/bin/skill-lint.py.

set -u

BIN="$(cd "$(dirname "$0")" && pwd)"
export SDD_LINT_BIN="$BIN"
export PERGUNTA_FRAG="${PERGUNTA_FRAG:-$BIN/../templates/fragments/PERGUNTA_DECISAO.md}"

uso() {
  [ -n "${1:-}" ] && echo "🛑 sdd-decisoes-lint: ${1}" >&2
  sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//' >&2
  printf 'RESULTADO: ERRO DE USO\n→ rode com --sites <pasta> ou --self-test.\n' >&2
  exit 64
}

precisa_python() {
  command -v python3 >/dev/null 2>&1 && return 0
  echo "🛑 sdd-decisoes-lint: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: ERRO DE USO\n→ instale o Python 3 (3.9 ou mais novo) e rode de novo.\n' >&2
  exit 64
}

cmd_sites() {
  [ $# -gt 0 ] || uso "--sites exige ao menos uma pasta ou arquivo"
  python3 -B - "$@" <<'PY'
import importlib.util, os, re, sys
from pathlib import Path

BIN = os.environ["SDD_LINT_BIN"]
FRAG = os.environ["PERGUNTA_FRAG"]


def sai64(msg, seta):
    print("🛑 sdd-decisoes-lint: " + msg, file=sys.stderr)
    print("RESULTADO: ERRO DE USO\n→ " + seta, file=sys.stderr)
    sys.exit(64)


try:
    spec = importlib.util.spec_from_file_location("skill_lint", os.path.join(BIN, "skill-lint.py"))
    sl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sl)
    perguntas, sem_cerca, OUTRO = sl.perguntas, sl.sem_cerca, sl.OUTRO
except (OSError, AttributeError, ImportError, SyntaxError) as e:
    sai64("não consegui carregar sdd/bin/skill-lint.py: %s" % e, "reinstale sdd/bin/ do pacote (sdd-open.sh init).")

try:
    frag = open(FRAG, encoding="utf-8").read()
except (OSError, UnicodeDecodeError):
    frag = ""
ROTULOS = {m.group(1): m.group(2).strip() for m in
           re.finditer(r"^\s*\|\s*`\[(D[1-5]|auto) · ([^\]]+)\]`\s*\|", frag, re.M)}
if len(ROTULOS) != 6:
    sai64("tabela das 6 marcas não encontrada em %s (achei %d)" % (FRAG, len(ROTULOS)),
          "confira o item 9 de sdd/templates/fragments/PERGUNTA_DECISAO.md.")

MARCA = re.compile(r"\[(?:D\d+|auto)\b[^\]]*\]")
FORMA = re.compile(r"^\[(D[1-5]|auto) · ([^\]]+)\]$")
NUA = re.compile(r"^\[(D[1-5]|auto)\]$")
REF = re.compile(r"\(ref:[^)]*\)\s*\.?\s*$")
ID = re.compile(r"\b(?:AT|LM)-\d+\b|\bD\d+\b|\b(?=[0-9a-fA-F]*\d)(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{7,40}\b")
MD = re.compile(r"^```markdown[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)


def abre_markdown(texto):
    """Os blocos ```markdown são exemplos de resposta: viram texto (as cercas, linhas vazias)."""
    return MD.sub(lambda m: "\n" + m.group(1) + "\n", texto)


def linhas_como_o_parser(texto):
    return [ln[2:] if ln.startswith("> ") else ("" if ln.rstrip() == ">" else ln)
            for ln in sem_cerca(texto).splitlines()]


def confere(linha, pergunta, opcoes):
    erros = []
    marcas = MARCA.findall(linha)
    if not marcas:
        erros.append("sem marca de classe (escreva [<código> · <rótulo>] antes da pergunta)")
    elif len(marcas) > 1:
        erros.append("%d marcas (deve haver exatamente 1)" % len(marcas))
    else:
        m = FORMA.match(marcas[0])
        if not linha.split(pergunta, 1)[0].rstrip().endswith(marcas[0]):
            erros.append("marca fora do lugar (vem logo antes da pergunta em negrito)")
        elif NUA.match(marcas[0]):
            erros.append("marca sem o rótulo: %s" % marcas[0])
        elif not m:
            erros.append("marca desconhecida %s" % marcas[0])
        elif ROTULOS.get(m.group(1)) != m.group(2).strip():
            erros.append("rótulo '%s' diferente de '%s'" % (m.group(2).strip(), ROTULOS.get(m.group(1))))
    rec = [k for k, (r, resto) in enumerate(opcoes) if "(recomendado)" in (r + resto).lower()]
    if not rec:
        erros.append("nenhuma opção (recomendado)")
    elif len(rec) > 1:
        erros.append("%d opções (recomendado); deve haver exatamente 1" % len(rec))
    elif rec[0] != 0:
        erros.append("a opção (recomendado) não é a primeira")
    rotulos = [r.lower() for r, _ in opcoes]
    if "não sei" not in rotulos:
        erros.append("sem a opção **não sei**")
    if any(OUTRO.match(r) for r in rotulos):
        erros.append("tem a opção **Outro**: resposta fora das opções é tratada como dúvida")
    for trecho in [pergunta] + [r + " " + resto for r, resto in opcoes]:
        achado = ID.search(REF.sub("", MARCA.sub("", trecho)))
        if achado:
            erros.append("identificador técnico fora do (ref: …): %s" % achado.group(0))
            break
    return erros


arquivos = []
for a in sys.argv[1:]:
    p = Path(a)
    if p.is_dir():
        arquivos += sorted(p.rglob("*.md"))
    elif p.is_file():
        arquivos.append(p)
    else:
        sai64("caminho inexistente: " + a, "passe pastas ou arquivos .md que existem.")

total, com_pergunta, erros = 0, 0, []
for f in arquivos:
    try:
        texto = abre_markdown(f.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        sai64("não consegui ler %s: %s" % (f, e), "confira o arquivo.")
    linhas = linhas_como_o_parser(texto)
    achadas = [(n, q, o) for n, q, o in perguntas(texto) if "**Sua decisão**" in linhas[n - 1]]
    if achadas:
        com_pergunta += 1
    for n, q, o in achadas:
        total += 1
        for e in confere(linhas[n - 1], q, o):
            erros.append("🛑 %s:%d — %s" % (f, n, e))

if total == 0:
    sai64("nenhuma pergunta de decisão (linha com **Sua decisão**) em: " + " ".join(sys.argv[1:]),
          "nada conferido nunca é verde; confira os caminhos.")
if erros:
    print("\n".join(erros))
    print("RESULTADO: VERMELHO")
    print("→ corrija as perguntas acima (formato e marcas: sdd/templates/fragments/PERGUNTA_DECISAO.md, item 9).")
    sys.exit(2)
print("🟢 sdd-decisoes-lint --sites: %d pergunta(s) em %d arquivo(s), cada uma com a marca de classe e no formato."
      % (total, com_pergunta))
PY
}

cmd_self_test() {
  FX="$BIN/../fixtures/conversa/decisoes"
  [ -d "$FX" ] || { echo "🛑 sdd-decisoes-lint: fixtures ausentes: $FX" >&2; exit 64; }
  S="$BIN/sdd-decisoes-lint.sh"; FALHAS=0
  echo "sdd-decisoes-lint --self-test"
  for par in "sem-classe:sem marca de classe" "com-outro:tem a opção **Outro**" \
             "com-jargao:identificador técnico" "dois-recomendados:2 opções (recomendado)"; do
    fx="${par%%:*}"; motivo="${par#*:}"
    out="$(bash "$S" --sites "$FX/$fx.md" 2>&1)"; rc=$?
    n="$(printf '%s\n' "$out" | grep -c '^🛑')"
    if [ "$rc" = "2" ] && [ "$n" = "1" ] && printf '%s' "$out" | grep -qF -- "$motivo"; then
      echo "  ✅ ${fx} → exit 2 (${motivo})"
    else
      echo "  🛑 ${fx} → exit ${rc}, ${n} achado(s) (esperado 2, 1 achado: ${motivo})"
      printf '%s\n' "$out" | sed 's/^/      /'
      FALHAS=$((FALHAS + 1))
    fi
  done
  out="$(bash "$S" --sites "$FX/controle.md" 2>&1)"; rc=$?
  if [ "$rc" = "0" ]; then echo "  ✅ controle → exit 0"; else
    echo "  🛑 controle → exit ${rc} (esperado 0)"; printf '%s\n' "$out" | sed 's/^/      /'; FALHAS=$((FALHAS + 1)); fi
  if [ "$FALHAS" -eq 0 ]; then
    printf 'RESULTADO: VERDE\n→ as 4 fixtures reprovam pelo motivo certo e o controle passa.\n'
    exit 0
  fi
  printf 'RESULTADO: VERMELHO\n→ %s fixture(s) acima não bateram; o contrato do lint mudou.\n' "$FALHAS"
  exit 1
}

case "${1:-}" in
  --sites)     precisa_python; shift; cmd_sites "$@" ;;
  --self-test) precisa_python; cmd_self_test ;;
  *)           uso ;;
esac
