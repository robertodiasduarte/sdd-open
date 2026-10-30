#!/usr/bin/env bash
# gate-shell-evidencia.sh — prova que o `[exit=N]` de um log de evidência é o exit do COMANDO, não do
# formatador que veio depois do pipe.
#
# `cmd | tail -5; echo "[exit=$?]"` grava o exit do `tail` (sempre 0): um teste que falhou vira evidência
# "verde". No zsh, `${PIPESTATUS[0]}` sai vazio e o log fica `[exit=]`, sem exit nenhum.
#
# Regra (por linha `[exit=N]` ou `exit=N`, olhando o último `$ <comando>` acima dela no mesmo log):
#   🛑 o comando tem `|` ou `|&` (`||` não conta), o último estágio é um FORMATADOR (tail head cat tee
#      wc sed cut sort uniq column tr fold nl, mesmo com `VAR=valor`, `command`, `env` ou `(` antes), não
#      há `<var>=$?` antes do último pipe nem `PIPESTATUS`/`pipefail` no comando (comentário não conta)
#      ⇒ o número gravado é do formatador. Um `$` sozinho na linha: o comando é a linha seguinte.
#   🛑 `[exit=]` vazio (com ou sem espaço, com ou sem colchete), ou `[exit=$?]` literal ⇒ não há exit.
#   ✅ `| grep -c X`, `| jq -e`, `| awk '…exit 1'` não são acusados: ali o último estágio É a asserção.
#   A regra é conservadora com comando composto (`… | tail -1 && outro`, `for … done`): acusa pelo
#   último pipe, mesmo quando o exit gravado veio de outro comando depois dele — confira o log.
#
# Uso:
#   sdd/bin/gate-shell-evidencia.sh                 # *.log de sdd/reports/evidence/ tocados contra
#                                                   # origin/<project.default_branch>, mais os staged, os
#                                                   # modificados e os não rastreados
#   sdd/bin/gate-shell-evidencia.sh --base <ref>    # idem, outra base
#   sdd/bin/gate-shell-evidencia.sh <log|pasta>…    # caminhos explícitos (pasta = todos os *.log dentro)
#
# Exit: 0 nenhum acusado · 2 ≥1 acusado (arquivo:linha) · 64 uso, caminho inexistente ou git que falha.
# ⚠️ bash 3.2 (sem arrays) · todo awk com LC_ALL=C (o awk do macOS falha com UTF-8).

set -uo pipefail

uso() {
  echo "🛑 ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ %s\n' "${2:-uso: sdd/bin/gate-shell-evidencia.sh [--base <ref>] [<log|pasta>…]}" >&2
  exit 64
}

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || ROOT=""
BASE=""; MODO="diff"
LISTA="$(mktemp 2>/dev/null || mktemp -t shellev)" || exit 64
ACHADOS="$(mktemp 2>/dev/null || mktemp -t shellev)" || exit 64
PROG="$(mktemp 2>/dev/null || mktemp -t shellev)" || exit 64
trap 'rm -f "${LISTA}" "${ACHADOS}" "${PROG}"' EXIT

while [ $# -gt 0 ]; do
  case "${1}" in
    --base) [ $# -ge 2 ] && [ -n "${2}" ] || uso "--base exige uma ref"; BASE="${2}"; shift 2 ;;
    -h|--help) sed -n '2,25p' "$0"; exit 64 ;;
    -*) uso "opção desconhecida: ${1}" ;;
    *)
      MODO="caminhos"
      if [ -d "${1}" ]; then find "${1}" -name '*.log' -type f >> "${LISTA}"
      elif [ -f "${1}" ]; then printf '%s\n' "${1}" >> "${LISTA}"
      else uso "não existe: ${1}"; fi
      shift ;;
  esac
done

if [ "${MODO}" = "diff" ]; then
  [ -n "${ROOT}" ] || uso "fora de um repositório git" "rode dentro do projeto, ou passe os logs."
  cd "${ROOT}" || exit 64
  if [ -z "${BASE}" ]; then
    DB="$(sed -n 's/^[[:space:]]*default_branch:[[:space:]]*//p' sdd/config.yaml 2>/dev/null | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d "\"' ")"
    BASE="origin/${DB:-main}"
  fi
  EVID="sdd/reports/evidence"
  git -c core.quotepath=false diff --name-only --diff-filter=AMR "${BASE}...HEAD" -- "${EVID}" > "${LISTA}" 2>/dev/null \
    || uso "git diff ${BASE}...HEAD falhou: sem escopo confiável, não avalio" "passe --base <ref> existente, ou os logs."
  git -c core.quotepath=false diff --name-only --diff-filter=AMR HEAD -- "${EVID}" >> "${LISTA}" 2>/dev/null
  git -c core.quotepath=false ls-files --others --exclude-standard -- "${EVID}" >> "${LISTA}" 2>/dev/null
fi
LC_ALL=C sort -u -o "${LISTA}" "${LISTA}"

cat > "${PROG}" <<'AWK'
FNR == 1 { cmd = ""; cmdraw = ""; proxima = 0 }
proxima == 1 && $0 !~ /^[ \t]*$/ { cmdraw = "$ " $0; cmd = $0; proxima = 0; next }
/^\$[ \t]*$/ { proxima = 1; cmd = ""; cmdraw = ""; next }
/^\$ / { cmdraw = $0; cmd = $0; sub(/^\$ /, "", cmd); next }
/^\[?exit=/ {
  if ($0 ~ /^\[?exit=\$\?\]?/) {
    printf("🛑 %s:%d — `%s` literal: o exit nunca foi expandido\n", FILENAME, FNR, $0); next
  }
  if ($0 ~ /^\[?exit=[ \t]*\]?[ \t]*$/) {
    printf("🛑 %s:%d — `%s` vazio: não há exit nenhum aqui (no zsh, ${PIPESTATUS[0]} sai vazio)\n", FILENAME, FNR, $0); next
  }
  if (cmd == "") next
  c = cmd
  sub(/[ \t]+#.*$/, "", c)
  if (c ~ /pipefail/ || c ~ /PIPESTATUS/) next
  gsub(/\|\|/, "\001", c)
  gsub(/\|&/, "|", c)
  n = split(c, parts, "|")
  if (n < 2) next
  lp = 0; rest = c
  while ((k = index(rest, "|")) > 0) { lp += k; rest = substr(rest, k + 1) }
  antes = substr(c, 1, lp - 1); if (antes ~ /[A-Za-z_][A-Za-z0-9_]*=\$\?/) next
  last = parts[n]; sub(/^[ \t]+/, "", last); sub(/[ \t]+$/, "", last)
  gsub(/^[({ \t]+/, "", last)
  nt = split(last, tk, /[ \t]+/); j = 1
  while (j < nt && (tk[j] ~ /^[A-Za-z_][A-Za-z0-9_]*=/ || tk[j] ~ /^(command|builtin|exec|env|nice|time|stdbuf|-[A-Za-z]+)$/)) j++
  t = tk[j]; sub(/^.*\//, "", t); sub(/[)};]+$/, "", t)
  if (t ~ /^(tail|head|cat|tee|wc|sed|cut|sort|uniq|column|tr|fold|nl)$/) {
    show = cmdraw; if (length(show) > 110) show = substr(show, 1, 107) "..."
    printf("🛑 %s:%d — o número gravado (%s) é o exit de `%s`, não do seu comando\n", FILENAME, FNR, $0, t)
    printf("      %s\n", show)
  }
}
AWK

N_LOGS=0
while IFS= read -r f; do
  case "${f}" in *.log) ;; *) continue ;; esac
  [ -f "${f}" ] || continue
  N_LOGS=$((N_LOGS + 1))
  LC_ALL=C awk -f "${PROG}" "${f}" >> "${ACHADOS}"
done < "${LISTA}"

if [ "${N_LOGS}" -eq 0 ]; then
  echo "ℹ️  nenhum *.log no escopo (${MODO}): nada a conferir."
  printf 'RESULTADO: VERDE\n→ siga para o próximo passo.\n'
  exit 0
fi
BAD="$(grep -c '^🛑' "${ACHADOS}" || true)"
if [ "${BAD:-0}" -gt 0 ]; then
  cat "${ACHADOS}"
  echo "🛑 ${BAD} linha(s) de exit que não provam o comando, em ${N_LOGS} log(s)."
  printf '%s\n' 'RESULTADO: VERMELHO'
  printf '%s\n' '→ refaça o log gravando o exit antes de formatar: out=$(cmd 2>&1); rc=$?; printf '"'"'%s\n'"'"' "$out" | tail -n 200; echo "[exit=$rc]"'
  exit 2
fi
echo "✅ ${N_LOGS} log(s) sem exit de formatador."
printf 'RESULTADO: VERDE\n→ siga para o próximo passo.\n'
exit 0
