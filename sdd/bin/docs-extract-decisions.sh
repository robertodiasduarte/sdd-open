#!/usr/bin/env bash
# docs-extract-decisions.sh — gera o índice de decisões (docs/adr/index.md) a partir dos blocos de decisão
# dos DESIGNs (sdd/features/DESIGN_*.md). Regenerável; não edite a saída à mão: a fonte é o DESIGN.
#
# Uso: sdd/bin/docs-extract-decisions.sh [--root PASTA] [--out ARQUIVO]
#   --root  raiz do projeto (padrão: a raiz do repositório git, ou a pasta atual fora de um)
#   --out   arquivo de saída (padrão: <root>/docs/adr/index.md)
#
# Régua: lista FECHADA de títulos de bloco — `## Decision N` · `### Decision N` · `### Decision D-N` ·
# `### Decisão N` · `### ADR-N` · `### DN` / `### D-N`. O sdd-design escreve `### Decision N: <nome>` (o
# design-lint.py confere): renomear o título tira a decisão do índice.
# ID: <STEM>#D<N>, STEM = nome do arquivo sem DESIGN_ e .md; N repetido no mesmo arquivo ganha sufixo b, c…
# Conservação: extraídos + órfãos = lidos, senão exit 2. DESIGN sem bloco nunca some: vai para Órfãos.
#
# Exit: 0 índice gravado · 2 conservação violada · 64 erro de uso
# Compat: bash 3.2, awk POSIX. Lê os DESIGNs do disco (no Open os artefatos SDD nem sempre são versionados).
set -euo pipefail
export LC_ALL=C

uso() { sed -n '2,17p' "$0" >&2; printf 'RESULTADO: ERRO DE USO\n→ rode com --root e --out válidos.\n' >&2; exit 64; }

root=""; out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --root) [ $# -ge 2 ] || uso; root="$2"; shift 2 ;;
    --out)  [ $# -ge 2 ] || uso; out="$2"; shift 2 ;;
    -h|--help) uso ;;
    *) echo "argumento desconhecido: $1" >&2; uso ;;
  esac
done
if [ -z "${root}" ]; then root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; fi
[ -d "${root}" ] || { echo "--root inexistente: ${root}" >&2; uso; }
root="$(cd "${root}" && pwd)"
out="${out:-${root}/docs/adr/index.md}"

# os links do índice são relativos à pasta do --out (docs/adr/index.md ⇒ ../../)
pre="$(python3 -c 'import os, sys; print(os.path.relpath(sys.argv[1], os.path.dirname(os.path.abspath(sys.argv[2]))))' "${root}" "${out}")/"
[ "${pre}" = "./" ] && pre=""
lista="$(mktemp)"; body="$(mktemp)"; stats="$(mktemp)"; tmp="$(mktemp)"
trap 'rm -f "${lista}" "${body}" "${stats}" "${tmp}"' EXIT
( cd "${root}" && for f in sdd/features/DESIGN_*.md; do [ -f "${f}" ] && printf '%s\n' "${f}"; done ) | sort > "${lista}" || true
lidos=$(grep -c . "${lista}" || true)

(cd "${root}" && awk -v stats="${stats}" -v pre="${pre}" '
function autolink(s,   out, rest, pre, url, ticks) {
  out = ""; rest = s
  while (match(rest, /https?:\/\/[^ <>`)|]+/)) {
    pre = substr(rest, 1, RSTART - 1); url = substr(rest, RSTART, RLENGTH)
    ticks = gsub(/`/, "`", pre)
    out = out pre
    if ((ticks_acc + ticks) % 2 == 1 || substr(pre, length(pre), 1) == "<" || substr(pre, length(pre) - 1, 2) == "](") out = out url
    else out = out "<" url ">"
    ticks_acc += ticks
    rest = substr(rest, RSTART + RLENGTH)
  }
  ticks_acc = 0
  return out rest
}
function md_cell(s, max,   cut, ticks) {
  if (max == "") max = 160
  gsub(/[\r\t]+/, " ", s); gsub(/  +/, " ", s); sub(/^ +/, "", s); sub(/ +$/, "", s)
  gsub(/\\\|/, "|", s); gsub(/\|/, "\\|", s)
  if (length(s) > max) {
    cut = max; while (cut > 1 && substr(s, cut, 1) != " ") cut--
    if (cut <= 1) { cut = max + 1; while (cut > 1 && substr(s, cut, 1) ~ /[\200-\277]/) cut-- }
    s = substr(s, 1, cut - 1)
    sub(/\\$/, "", s)
    s = s " …"
  }
  ticks = gsub(/`/, "`", s); if (ticks % 2 == 1) s = s "`"
  return autolink(s)
}
function rel(path) { return pre path }
function flush_block(   id, st, suf, k) {
  if (!inblk) return
  k = ++seen[bn]
  suf = (k == 1) ? "" : substr("bcdefghijklmnopqrstuvwxyz", k - 1, 1)
  id = stem "#D" bn suf
  st = (corr ? "⚠️ revisar" : (bstatus != "" ? bstatus : (fstatus != "" ? fstatus : "—")))
  printf "| `%s` | %s | %s | %s | %s | %s | [%s:%d](%s) |\n", id, md_cell(btitle, 120), md_cell(feature != "" ? feature : stem, 60), \
    md_cell(bdate != "" ? bdate : (fdate != "" ? fdate : "—"), 40), md_cell(st, 40), (cons ? "✓" : "—"), \
    base, bline, rel(path)
  ndec++; nblk++; if (corr) ncorr++
  inblk = 0
}
function start_block(line,   t) {
  flush_block()
  t = line
  sub(/^#+ +/, "", t)
  if (t ~ /^ADR-/) sub(/^ADR-/, "", t)
  else { sub(/^(Decision|Decisão)/, "", t); while (sub(/^( |:)/, "", t)) ; sub(/^D-?/, "", t) }
  match(t, /^[0-9]+/); bn = substr(t, 1, RLENGTH) + 0; t = substr(t, RLENGTH + 1)
  while (sub(/^( |:|\.|-|—|–)/, "", t)) ;
  btitle = (t == "" ? "(sem título)" : t)
  inblk = 1; bline = ln; bstatus = ""; bdate = ""; cons = 0
  corr = (line ~ /(CORREÇÃO|Correção|correção|FALSA|Falsa|falsa)/)
}
function is_block(l) {
  return (l ~ /^###? +(Decision|Decisão)( D-?)? *[0-9]+/ || l ~ /^### +ADR-[0-9]+/ || l ~ /^### +D-?[0-9]+([ :.]|—|–|-|$)/)
}
function cell2(l,   a, n) { n = split(l, a, "|"); return (n >= 3 ? a[3] : "") }
function celula_apos(l, nome,   a, n, i) { n = split(l, a, "|"); for (i = 1; i < n; i++) if (a[i] ~ ("\\*\\*" nome "\\*\\*")) return a[i + 1]; return "" }
function trim(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); return s }
{
  path = $0
  base = path; sub(/.*\//, "", base)
  stem = base; sub(/^DESIGN_/, "", stem); sub(/\.md$/, "", stem)
  feature = ""; fdate = ""; fstatus = ""; fence = 0; inblk = 0; nblk = 0; ln = 0; semnum = 0
  for (k in seen) delete seen[k]
  while ((getline l < path) > 0) {
    ln++
    if (l ~ /^[ \t]*(```|~~~)/) { fence = !fence; continue }
    if (fence) continue
    if (is_block(l)) { start_block(l); continue }
    if (l ~ /^### +Decision *:/) semnum++
    if (inblk && (l ~ /^# / || l ~ /^## / || l ~ /^### /)) flush_block()
    if (l ~ /^\| *\*\*Feature\*\* *\|/ && feature == "") feature = trim(cell2(l))
    if (l ~ /^\| *\*\*Date\*\* *\|/) { if (inblk && bdate == "") bdate = trim(cell2(l)); else if (!inblk && fdate == "") fdate = trim(cell2(l)) }
    if (l ~ /^\| *\*\*Status\*\* *\|/) { if (inblk && bstatus == "") bstatus = trim(cell2(l)); else if (!inblk && fstatus == "") fstatus = trim(cell2(l)) }
    # o template do Open põe Status e Date na mesma linha do bloco: | **Status** | X | · | **Date** | Y |
    if (inblk && bdate == "" && l ~ /^\|.*\| *\*\*Date\*\* *\|/) bdate = trim(celula_apos(l, "Date"))
    if (inblk) {
      if (l ~ /\*\*(Consequences|Consequências)/) cons = 1
      if (l ~ /(CORREÇÃO|Correção|correção|FALSA|Falsa|falsa)/) corr = 1
    }
  }
  close(path)
  flush_block()
  if (nblk > 0 && (feature == "" || fdate == "")) avisos[++nav] = stem "\t" (feature == "" ? "sem **Feature**" : "") (feature == "" && fdate == "" ? " e " : "") (fdate == "" ? "sem **Date**" : "")
  if (feature == "") feature = stem
  if (nblk > 0) nextr++
  else { norf++; orf[norf] = stem "\t" base "\t" path "\t" (semnum ? "bloco sem número (`### Decision: …`)" : "nenhum bloco de decisão reconhecido") }
}
END {
  print "@@ORFAOS" > stats
  for (i = 1; i <= norf; i++) print orf[i] > stats
  print "@@AVISOS" > stats
  for (i = 1; i <= nav; i++) print avisos[i] > stats
  printf "@@COUNTS\t%d\t%d\t%d\t%d\n", nextr + 0, norf + 0, ndec + 0, ncorr + 0 > stats
}' < "${lista}") > "${body}"

counts="$(grep '^@@COUNTS' "${stats}")"
extraidos=$(printf '%s\n' "${counts}" | cut -f2); orfaos=$(printf '%s\n' "${counts}" | cut -f3)
decisoes=$(printf '%s\n' "${counts}" | cut -f4); corrigidas=$(printf '%s\n' "${counts}" | cut -f5)

if [ $((extraidos + orfaos)) -ne "${lidos}" ]; then
  echo "🛑 docs-extract-decisions: conservação violada: extraídos (${extraidos}) + órfãos (${orfaos}) ≠ lidos (${lidos})" >&2
  printf 'RESULTADO: VERMELHO\n→ algum DESIGN sumiu do índice sem ir para Órfãos; isto é defeito do extrator, não do DESIGN.\n'
  exit 2
fi

{
  echo "# Índice de decisões (ADR)"
  echo
  echo "<!-- markdownlint-disable MD038 -->"
  echo
  echo "> **Gerado** por \`sdd/bin/docs-extract-decisions.sh\` a partir dos blocos de decisão dos \`DESIGN_*.md\` em"
  echo "> \`sdd/features/\`. **Não editar à mão**: a fonte da verdade é o DESIGN; este arquivo é só o índice."
  echo ">"
  echo "> **Como citar:** \`STEM#DN\` (ex.: \`PEDIDOS#D3\`). STEM é o nome do DESIGN sem \`DESIGN_\` e \`.md\`; um número"
  echo "> repetido no mesmo arquivo recebe sufixo \`b\`, \`c\`…"
  echo "> **⚠️ revisar** = o bloco menciona \`CORREÇÃO\`/\`falsa\`: pode ser uma decisão corrigida. Leia o bloco antes de reusar."
  echo
  echo "**${decisoes} decisões** em **${extraidos} DESIGNs** · ${corrigidas} marcadas ⚠️ revisar · ${orfaos} DESIGNs órfãos (ver [Órfãos](#órfãos))."
  echo
  echo "| ID | Decisão | Feature | Data | Status | Consequences | Fonte |"
  echo "|----|---------|---------|------|--------|--------------|-------|"
  cat "${body}"
  echo
  echo "## Órfãos"
  echo
  echo "DESIGNs lidos em que **nenhum** bloco da lista fechada casou. Não somem em silêncio: cada um está"
  echo "aqui com o motivo. Um DESIGN novo deve usar \`### Decision N: <nome>\` sob \`## Key Decisions\`."
  echo
  if [ "${orfaos}" -gt 0 ]; then
    echo "| DESIGN | Motivo |"
    echo "|--------|--------|"
    awk -F'\t' -v pre="${pre}" '/^@@AVISOS/{exit} /^@@/{next} {printf "| [%s](%s%s) | %s |\n", $2, pre, $3, $4}' "${stats}"
  else
    echo "_Nenhum._"
  fi
  echo
  echo "## Avisos de Metadata"
  echo
  echo "DESIGNs **extraídos** cuja tabela Metadata não tem \`**Feature**\` ou \`**Date**\`; a coluna Feature usa o STEM."
  echo
  navisos=$(awk '/^@@AVISOS/{f=1;next} /^@@COUNTS/{f=0} f' "${stats}" | grep -c . || true)
  if [ "${navisos}" -gt 0 ]; then
    echo "| STEM | Aviso |"
    echo "|------|-------|"
    awk -F'\t' '/^@@AVISOS/{f=1;next} /^@@COUNTS/{f=0} f{printf "| `%s` | %s |\n", $1, $2}' "${stats}"
  else
    echo "_Nenhum._"
  fi
  echo
  echo "## Conservação"
  echo
  echo "extraídos (${extraidos}) + órfãos (${orfaos}) = lidos (${lidos}) ✓ · decisões = ${decisoes} · avisos de Metadata = ${navisos}"
} > "${tmp}"

mkdir -p "$(dirname "${out}")"
mv "${tmp}" "${out}"
echo "docs-extract-decisions: lidos=${lidos} extraidos=${extraidos} orfaos=${orfaos} decisoes=${decisoes} corrigidas=${corrigidas}"
printf 'RESULTADO: VERDE\n→ índice gravado em %s.\n' "${out}"
