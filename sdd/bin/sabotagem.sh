#!/usr/bin/env bash
# sabotagem.sh — prova que o teste de um AT pega o defeito: aplica a sabotagem declarada no DESIGN numa CÓPIA
# descartável do último commit e exige que o comando do AT fique vermelho com ela.
#
# A cópia é `git archive HEAD` numa pasta temporária, apagada ao sair (também por sinal). A árvore de trabalho só
# recebe o log: mudança não commitada nunca é tocada (LM-009). O comando roda primeiro na cópia LIMPA e precisa sair 0;
# senão o vermelho com a sabotagem não provaria nada.
#
# Uso:
#   bash sdd/bin/sabotagem.sh --feature <F> --at <AT-nnn> --arquivo <caminho> --trocar '<trecho>' --por '<trecho>' \
#        --cmd '<comando do AT>'
#     --arquivo  relativo à raiz do repositório, commitado; nunca absoluto, com `..` ou link simbólico
#     --trocar   trecho literal que aparece EXATAMENTE 1 vez no arquivo (no último commit)
#     --cmd      roda por `bash -c` na raiz da cópia (sem .git), com a entrada em /dev/null
#
# Exit:
#   0  = o teste pega o defeito: verde na cópia limpa, vermelho com a sabotagem
#   2  = o teste NÃO pega o defeito: verde também com a sabotagem
#   3  = INCONCLUSIVO: o comando já falha sem a sabotagem, não roda (126/127), o trecho não aparece exatamente 1 vez,
#        ou a cópia não pôde ser montada
#   64 = uso: argumento faltando ou inválido, fora de repositório git, arquivo fora do último commit, caminho que sai
#        da cópia
#
# Evidência (só em 0 e 2): sdd/reports/evidence/<F>/<AT>.sabotagem.log — 1ª linha `$ <cmd>`, as linhas `# sabotagem:`
# e `# sem a sabotagem: exit 0`, a saída da execução sabotada (últimas 200 linhas) e `[exit=<n>]` dela.
# ⚠️ bash 3.2 + python3 (stdlib) · a cópia não grava trace (SDD_TRACE=off).

set -uo pipefail
# F16: o Python que roda vira python3 (no Windows, python ou py -3). Só builtins; sem a biblioteca, a guarda de antes.
_sdd_0="${0//\\//}"   # caminho do Windows (C:\…\x.sh) vira C:/…/x.sh
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi   # F16W2: sem a biblioteca, ao menos o UTF-8

uso() {
  echo "🛑 sabotagem: ${1}" >&2
  echo "   uso: bash sdd/bin/sabotagem.sh --feature <F> --at <AT-nnn> --arquivo <caminho> --trocar '<trecho>' --por '<trecho>' --cmd '<comando>'" >&2
  printf 'RESULTADO: ERRO DE USO\n→ corrija a chamada (os valores vêm da tabela de sabotagens do DESIGN) e rode de novo.\n' >&2
  exit 64
}
inconclusivo() {
  echo "⚠️  sabotagem: ${1}"
  printf 'RESULTADO: INCONCLUSIVO\n→ %s\n' "${2:-corrija a declaração no DESIGN (sdd-iterate) ou o comando do AT e rode de novo; isto não prova nada.}"
  exit 3
}

FEATURE=""; AT=""; ARQUIVO=""; TROCAR=""; POR=""; CMD=""; TEM_TROCAR=""; TEM_POR=""
while [ $# -gt 0 ]; do
  case "${1}" in
    --feature) [ $# -ge 2 ] || uso "--feature exige um nome"; FEATURE="${2}"; shift 2 ;;
    --at)      [ $# -ge 2 ] || uso "--at exige o AT"; AT="${2}"; shift 2 ;;
    --arquivo) [ $# -ge 2 ] || uso "--arquivo exige um caminho"; ARQUIVO="${2}"; shift 2 ;;
    --trocar)  [ $# -ge 2 ] || uso "--trocar exige um trecho"; TROCAR="${2}"; TEM_TROCAR=1; shift 2 ;;
    --por)     [ $# -ge 2 ] || uso "--por exige um trecho"; POR="${2}"; TEM_POR=1; shift 2 ;;
    --cmd)     [ $# -ge 2 ] || uso "--cmd exige o comando do AT"; CMD="${2}"; shift 2 ;;
    -h|--help) sed -n '2,27p' "$0"; exit 64 ;;
    *)         uso "argumento desconhecido: ${1}" ;;
  esac
done
[ -n "${FEATURE}" ] || uso "falta --feature"
[ -n "${AT}" ] || uso "falta --at"
[ -n "${ARQUIVO}" ] || uso "falta --arquivo"
[ -n "${TEM_TROCAR}" ] && [ -n "${TROCAR}" ] || uso "falta --trocar (um trecho não vazio)"
[ -n "${TEM_POR}" ] || uso "falta --por (pode ser vazio: --por '')"
[ -n "${CMD}" ] || uso "falta --cmd"
case "${FEATURE}" in *[!A-Za-z0-9._-]*|.*) uso "--feature só com letras, números, ponto, _ e -: ${FEATURE}" ;; esac
printf '%s' "${AT}" | grep -Eq '^AT-[0-9]+[A-Za-z0-9_-]*$' || uso "--at no formato AT-nnn: ${AT}"
ARQ_BARRA="${ARQUIVO//\\//}"
case "${ARQ_BARRA}" in
  /*|[A-Za-z]:*) uso "--arquivo tem de ser relativo à raiz do repositório: ${ARQUIVO}" ;;
esac
case "/${ARQ_BARRA}/" in
  */../*) uso "--arquivo não pode ter um componente '..': ${ARQUIVO}" ;;
esac
ARQUIVO="${ARQ_BARRA}"

sdd_python_exigir
RAIZ="$(git rev-parse --show-toplevel 2>/dev/null)" || uso "fora de um repositório git: rode na pasta do projeto"
cd "${RAIZ}" || uso "não consegui entrar em ${RAIZ}"
git cat-file -e "HEAD:${ARQUIVO}" 2>/dev/null \
  || uso "${ARQUIVO} não está no último commit: commite antes (a sabotagem roda numa cópia do último commit)"
if [ -n "$(git status --porcelain --untracked-files=no 2>/dev/null)" ]; then
  echo "⚠️  há mudança não commitada: a cópia é do último commit (HEAD), e a árvore de trabalho não é tocada."
fi

# ---- o destino do log: nem ele nem as pastas dele podem ser link simbólico (a gravação sairia da árvore) ----------
EVID="sdd/reports/evidence/${FEATURE}"
LOG="${EVID}/${AT}.sabotagem.log"
link_no_destino() {   # imprime o 1º link do caminho do log; vazio = nenhum
  local p
  for p in sdd sdd/reports sdd/reports/evidence "${EVID}" "${LOG}"; do
    if [ -L "${p}" ]; then printf '%s' "${p}"; return 0; fi
  done
}
elo="$(link_no_destino)"
[ -z "${elo}" ] || uso "${elo} é um link simbólico: o log sairia da árvore; troque-o por uma pasta ou um arquivo comum"

# ---- a cópia descartável ----------------------------------------------------------------------------
TRAB="$(mktemp -d "${TMPDIR:-/tmp}/sdd-sabotagem.XXXXXX" 2>/dev/null)" || inconclusivo "não consegui criar a pasta temporária"
limpa() { rm -rf "${TRAB}"; }
trap limpa EXIT
trap 'limpa; exit 130' INT
trap 'limpa; exit 143' TERM
trap 'limpa; exit 129' HUP
COPIA="${TRAB}/copia"
SAIDA="${TRAB}/saida.txt"
# Cópia nova do último commit. A execução sabotada ganha a sua (avaliador, ciclo 1, N1): um cache que a execução limpa
# deixasse na cópia (o __pycache__ do Python com a troca no mesmo segundo do commit, um build) esconderia a sabotagem.
monta_copia() {
  rm -rf "${COPIA}" && mkdir "${COPIA}" || inconclusivo "não consegui criar a cópia"
  git archive --format=tar HEAD 2>/dev/null | (cd "${COPIA}" && tar -xf -) || inconclusivo "git archive HEAD falhou"
}
monta_copia
ALVO="${COPIA}/${ARQUIVO}"

# conferir (contenção + o trecho exatamente 1 vez) e, depois, trocar: só na cópia
troca() {   # $1 = conferir | trocar
  python3 - "${1}" "${COPIA}" "${ALVO}" "${TROCAR}" "${POR}" <<'PY'
import sys as _sdd_sys  # F16W2: saída em UTF-8 e "\n" também no Windows (cp1252 e "\r\n" no pipe do Git Bash)
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
import os, sys
modo, copia, alvo, trocar, por = sys.argv[1:6]
raiz = os.path.realpath(copia)
p = os.path.normpath(alvo)
atual = raiz
for parte in os.path.relpath(p, copia).split(os.sep):
    atual = os.path.join(atual, parte)
    if os.path.islink(atual):
        print("link simbólico no caminho (%s): a troca sairia da cópia" % os.path.relpath(atual, raiz))
        sys.exit(20)
real = os.path.realpath(p)
if not real.startswith(raiz + os.sep):
    print("o caminho sai da cópia (%s)" % real)
    sys.exit(20)
if not os.path.isfile(real):
    print("não é um arquivo comum na cópia")
    sys.exit(20)
dado = open(real, "rb").read()
de, para = trocar.encode("utf-8"), por.encode("utf-8")
n = dado.count(de)
if n != 1:
    print("o trecho a trocar aparece %d vez(es) no arquivo, no último commit; declare um trecho que apareça exatamente 1 vez" % n)
    sys.exit(22)
if modo == "trocar":
    open(real, "wb").write(dado.replace(de, para, 1))
PY
}
msg="$(troca conferir)"; rc=$?
case "${rc}" in
  0) ;;
  20) uso "${ARQUIVO}: ${msg}" ;;
  22) inconclusivo "${ARQUIVO}: ${msg}" ;;
  *) inconclusivo "não consegui conferir ${ARQUIVO} na cópia (python saiu ${rc}): ${msg}" ;;
esac

roda_na_copia() { ( cd "${COPIA}" && SDD_TRACE=off bash -c "${CMD}" ) </dev/null >"${SAIDA}" 2>&1; }

echo "▶ cópia do último commit ($(git rev-parse --short HEAD)) · comando sem a sabotagem"
roda_na_copia; rc_limpo=$?
case "${rc_limpo}" in
  0) ;;
  126|127) inconclusivo "o comando nem rodou na cópia (exit ${rc_limpo}: não encontrado ou sem permissão)" \
             "confira o --cmd (ele roda na raiz da cópia, sem .git) e rode de novo." ;;
  *) tail -n 15 "${SAIDA}" | sed 's/^/   │ /'
     inconclusivo "o comando já falha sem a sabotagem (exit ${rc_limpo}): o vermelho dela não provaria nada" \
       "deixe o AT verde no último commit (commite o código) e rode de novo." ;;
esac

monta_copia
msg="$(troca trocar)"; rc=$?
[ "${rc}" = 0 ] || inconclusivo "a troca falhou na cópia (python saiu ${rc}): ${msg}"
echo "▶ sabotagem: ${ARQUIVO}: «${TROCAR}» → «${POR}»"
roda_na_copia; rc_sab=$?
case "${rc_sab}" in
  126|127) inconclusivo "com a sabotagem, o comando nem rodou (exit ${rc_sab})" ;;
esac

elo="$(link_no_destino)"   # o comando do AT rodou no meio: confere de novo na hora de gravar
[ -z "${elo}" ] || inconclusivo "${elo} virou um link simbólico enquanto o comando rodava: o log não foi gravado" \
  "veja o que o comando do AT faz com essa pasta e rode de novo."
mkdir -p "${EVID}" || inconclusivo "não consegui criar ${EVID}/"
{
  printf '$ %s\n' "${CMD}"
  printf '# sabotagem: %s: «%s» → «%s» (cópia de HEAD %s)\n' "${ARQUIVO}" "${TROCAR}" "${POR}" "$(git rev-parse --short HEAD)"
  printf '# sem a sabotagem: exit 0\n'
  tail -n 200 "${SAIDA}"
  # saída sem quebra de linha no fim: o [exit=] tem de ficar sozinho na última linha
  if [ -n "$(tail -c 1 "${SAIDA}" | tr -d '\n')" ]; then printf '\n'; fi
  printf '[exit=%s]\n' "${rc_sab}"
} > "${LOG}" || inconclusivo "não consegui gravar ${LOG}"
tail -n 15 "${SAIDA}" | sed 's/^/   │ /'

if [ "${rc_sab}" != 0 ]; then
  echo "✅ o teste pega o defeito: com a sabotagem, o comando saiu ${rc_sab}."
  printf 'RESULTADO: VERDE\n→ cite %s na evidência do %s.\n' "${LOG}" "${AT}"
  exit 0
fi
echo "🛑 o teste não pega o defeito: com a sabotagem declarada, o comando continuou verde."
printf 'RESULTADO: VERMELHO\n→ reforce a asserção do %s até ela acusar a sabotagem e rode de novo (a prova está em %s).\n' "${AT}" "${LOG}"
exit 2
