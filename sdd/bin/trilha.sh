#!/usr/bin/env bash
# trilha.sh — diz se a publicação de uma feature vai pela trilha curta (conserto pequeno) ou pela completa.
# Lido pela sdd-release no pré-voo (FASE 0, item 0); o resultado vai para o ledger (`trilha:`), e a parte depois
# do push lê de lá: na trilha curta, a ficha tem poucas linhas.
#
# Por que existe: "conserto pequeno" decidido pelo agente vira o que ele quiser naquele dia; decidido por comando,
# dá a mesma resposta para quem publica e para quem confere depois.
#
# USO-INICIO
#   trilha.sh <FEATURE> [--base <ref>]
#       curta    = sem sdd/features/DEFINE_<FEATURE>.md nem sdd/archive/<FEATURE>/DEFINE_<FEATURE>.md, e o diff
#                  desde o merge-base com <base> (com o que ainda não foi commitado), fora dos documentos do SDD
#                  (sdd/features, reports, reviews, handoffs, releases, archive, curadoria, traces, contexto) e do
#                  CHANGELOG.md, com até 3 arquivos e até 100 linhas (adicionadas
#                  mais removidas), sem arquivo binário
#       completa = qualquer outro caso, com o motivo
#       --base: padrão origin/<project.default_branch> (sdd/config.yaml), ou origin/main sem o slot
#       0 TRILHA: curta · 1 TRILHA: completa · 2 o git falhou (base desconhecida, fora de um repositório)
#       64 uso
# USO-FIM
#
# ⚠️ bash 3.2 (o /bin/bash do macOS) · git · awk · sem Python.

set -u

LIM_ARQ=3
LIM_LIN=100

uso() {
  echo "🛑 trilha: $1" >&2
  printf 'RESULTADO: PAROU\n→ rode `trilha.sh --help` para ver o uso; nada foi decidido.\n' >&2
  exit 64
}

case "${1:-}" in
  -h|--help)
    sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'
    exit 0 ;;
esac

[ "$#" -ge 1 ] || uso "falta a <FEATURE>"
feature="$1"; shift
printf '%s' "${feature}" | LC_ALL=C grep -Eq '^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$' \
  && [ "$(printf '%s' "${feature}" | wc -l | tr -d ' ')" = "0" ] \
  || uso "FEATURE inválida: só A-Z, a-z, 0-9, _, . e -, começando por letra ou número, até 80 caracteres"
base=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --base) [ "$#" -ge 2 ] && [ -n "$2" ] || uso "--base exige uma ref"; base="$2"; shift 2 ;;
    *) uso "opção desconhecida: $1" ;;
  esac
done

falha() {
  echo "🛑 trilha: $1" >&2
  printf 'RESULTADO: GIT FALHOU\n→ %s\n' "$2"
  exit 2
}

raiz="$(git rev-parse --show-toplevel 2>/dev/null)" || falha "isto não é um repositório git" \
  "rode de dentro da pasta da frente; nada foi decidido."
cd "${raiz}" || falha "não consegui entrar em ${raiz}" "confira a permissão da pasta."

if [ -z "${base}" ]; then
  padrao=""
  if [ -f sdd/config.yaml ]; then
    # 1 nível de mapa: project: … default_branch: x (o mesmo parser simples dos outros scripts de sdd/bin)
    padrao="$(awk '/^[^ #][^:]*:/{sec=$1} sec=="project:" && /^[ ]+default_branch:/{sub(/^[ ]+default_branch:[ ]*/,""); gsub(/["\047]/,""); sub(/[ ]+#.*$/,""); print; exit}' sdd/config.yaml)"
  fi
  base="origin/${padrao:-main}"
fi
git rev-parse --verify -q "${base}^{commit}" >/dev/null 2>&1 || falha "a base ${base} não existe neste repositório" \
  "rode GIT_TERMINAL_PROMPT=0 git fetch e tente de novo, ou passe --base <ref>; nada foi decidido."

# Um DEFINE é sinal de SDD formal: a trilha é a completa, seja qual for o tamanho do diff. Um caminho de cada vez
# (`[ -f ]`): um `ls a b` sairia ≠ 0 com só um dos dois presente (LM-025).
for d in "sdd/features/DEFINE_${feature}.md" "sdd/archive/${feature}/DEFINE_${feature}.md"; do
  if [ -f "${d}" ]; then
    printf 'TRILHA: completa (a feature tem DEFINE: %s)\n' "${d}"
    printf 'RESULTADO: COMPLETA\n→ grave trilha: completa no ledger.\n'
    exit 1
  fi
done

mb="$(git merge-base "${base}" HEAD 2>/dev/null)" || falha "${base} e HEAD não têm histórico em comum" \
  "confira a base; nada foi decidido."
# Contra o ponto em que a frente nasceu, com a pasta como está: o que ainda não foi commitado também conta (a
# release mede antes do commit atômico). Arquivo novo ainda fora do git entra pelo --no-index.
numstat="$(git -c core.quotePath=false diff --numstat "${mb}" 2>/dev/null)" || falha "git diff ${mb} falhou" \
  "confira o repositório; nada foi decidido."
# core.quotePath=false: com o padrão, um nome acentuado sai entre aspas e escapado, e o arquivo sumiria da conta
novos="$(git -c core.quotePath=false ls-files --others --exclude-standard 2>/dev/null)"
if [ -n "${novos}" ]; then
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    linha="$(git -c core.quotePath=false diff --no-index --numstat -- /dev/null "${f}" 2>/dev/null | head -n 1)"
    # arquivo que o git não conseguiu medir conta como binário: na dúvida, a trilha é a completa
    [ -n "${linha}" ] || linha="$(printf -- '-\t-\t%s' "${f}")"
    numstat="${numstat}
$(printf '%s' "${linha}" | awk -F '\t' -v p="${f}" '{print $1 "\t" $2 "\t" p}')"
  done <<EOF
${novos}
EOF
fi
# numstat: adicionadas<TAB>removidas<TAB>caminho ("-" nas duas colunas = binário). Renomeação: "a => b" ou
# "pasta/{a => b}" conta como 1 arquivo, pelo caminho novo.
resumo="$(printf '%s\n' "${numstat}" | awk -F '\t' '
  NF < 3 { next }
  {
    p = $3
    if (p ~ /\{.* => .*\}/) { pre = p; sub(/\{.*$/, "", pre); pos = p; sub(/^.*\}/, "", pos); meio = p
      sub(/^[^{]*\{[^}]* => /, "", meio); sub(/\}.*$/, "", meio); p = pre meio pos; gsub(/\/\//, "/", p) }
    else if (p ~ / => /) { sub(/^.* => /, "", p) }
    if (p ~ /^sdd\/(features|reports|reviews|handoffs|releases|archive|curadoria|traces|contexto)\// || p == "CHANGELOG.md") next
    arq++
    if ($1 == "-" || $2 == "-") bin++
    else lin += $1 + $2
  }
  END { printf "%d %d %d\n", arq, lin, bin }')"
set -- ${resumo}
arq="${1:-0}"; lin="${2:-0}"; bin="${3:-0}"

motivo=""
[ "${bin}" -eq 0 ] || motivo="o diff tem ${bin} arquivo(s) binário(s)"
[ -n "${motivo}" ] || [ "${arq}" -le "${LIM_ARQ}" ] || motivo="o diff tem ${arq} arquivos (o limite é ${LIM_ARQ})"
[ -n "${motivo}" ] || [ "${lin}" -le "${LIM_LIN}" ] || motivo="o diff tem ${lin} linhas mudadas (o limite é ${LIM_LIN})"

if [ -n "${motivo}" ]; then
  printf 'TRILHA: completa (%s, fora dos documentos do SDD e do CHANGELOG.md)\n' "${motivo}"
  printf 'RESULTADO: COMPLETA\n→ grave trilha: completa no ledger.\n'
  exit 1
fi
printf 'TRILHA: curta (sem DEFINE; %s arquivo(s) e %s linha(s) mudadas fora dos documentos do SDD e do CHANGELOG.md, contra %s)\n' \
  "${arq}" "${lin}" "${base}"
printf 'RESULTADO: CURTA\n→ grave trilha: curta no ledger; depois do push, a ficha é a curta.\n'
exit 0
