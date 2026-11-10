#!/usr/bin/env bash
# slot.sh — roda um slot de extensão do sdd/config.yaml com um contrato de saída só.
#
# Os 4 slots são comandos do próprio projeto que o método chama num momento certo:
#   smoke.before_ok_cmd     sdd-release, item 6b: antes do bloco do OK, sobre o commit que vai subir
#   smoke.before_push_cmd   sdd-release, item 7b: depois do "sim", antes do push (produção ainda velha)
#   smoke.after_deploy_cmd  sdd-release, item 10: depois do deploy confirmado
#   schema.check_cmd        sdd-build, passo 4b: os .sql que vão ser aplicados, antes da prévia
#
# Uso:
#   bash sdd/bin/slot.sh <chave> [--feature F] [--base ref] [--commit sha] [--arvore pasta] [--dir pasta] [arquivo…]
#
# O comando roda por `bash -c` na raiz do repositório, com os arquivos no FIM dele, um por argumento ("$@"),
# e com estas variáveis:
#   SDD_MOMENTO   before_ok | before_push | after_deploy | schema_check (vem da chave)
#   SDD_FEATURE   --feature (vazio se ausente)
#   SDD_BASE      SHA de --base; padrão origin/<project.default_branch> (vazio, com aviso, se não resolve)
#   SDD_COMMIT    SHA de --commit; padrão HEAD (vazio, com aviso, sem git)
#   SDD_ARVORE    --arvore; padrão a raiz do repositório: a pasta com a árvore do SDD_COMMIT, que o comando mede
#   SDD_SLOT_DIR  --dir; padrão uma pasta fora do repositório, a mesma em qualquer worktree para a mesma feature
#                 (os 3 smokes combinam por ela); no momento before_ok, a pasta padrão é esvaziada antes
#
# Exit: 0 OK · 2 REPROVOU · 3 INCONCLUSIVO (o comando saiu com outro código, morreu por sinal, ou este script foi
# interrompido) · 10 NADA A MEDIR · 11 PULADO (slot vazio, ausente ou sem sdd/config.yaml) · 64 ERRO DE USO
# (chave desconhecida, flag sem valor, ref que não resolve, aspas sem fechar, erro de sintaxe ou comentário #
# no comando). Nenhum caminho que não seja o 0 termina em silêncio.
# ⚠️ bash 3.2 + python3 (stdlib, só para ler o YAML). docs/adaptation-guide.md descreve o contrato para o projeto.

set -uo pipefail

uso() {
  echo "🛑 ${1}" >&2
  printf 'RESULTADO: ERRO DE USO\n→ %s\n' "${2:-uso: bash sdd/bin/slot.sh <chave> [--feature F] [--base ref] [--commit sha] [--arvore pasta] [--dir pasta] [arquivo…]}" >&2
  exit 64
}

CHAVE="${1:-}"
case "${CHAVE}" in
  smoke.before_ok_cmd)    MOMENTO="before_ok" ;;
  smoke.before_push_cmd)  MOMENTO="before_push" ;;
  smoke.after_deploy_cmd) MOMENTO="after_deploy" ;;
  schema.check_cmd)       MOMENTO="schema_check" ;;
  -h|--help)              sed -n '2,29p' "$0"; exit 64 ;;
  "")                     uso "falta a chave do slot" ;;
  *)                      uso "chave desconhecida: ${CHAVE}" "use uma destas: smoke.before_ok_cmd, smoke.before_push_cmd, smoke.after_deploy_cmd, schema.check_cmd" ;;
esac
shift

FEATURE=""; BASE=""; BASE_DADA=0; COMMIT="HEAD"; COMMIT_DADO=0; ARVORE=""; DIR=""
ARQS=()
while [ $# -gt 0 ]; do
  case "${1}" in
    --feature) [ $# -ge 2 ] && [ -n "${2}" ] || uso "--feature exige um nome"; FEATURE="${2}"; shift 2 ;;
    --base)    [ $# -ge 2 ] && [ -n "${2}" ] || uso "--base exige uma ref"; BASE="${2}"; BASE_DADA=1; shift 2 ;;
    --commit)  [ $# -ge 2 ] && [ -n "${2}" ] || uso "--commit exige um SHA"; COMMIT="${2}"; COMMIT_DADO=1; shift 2 ;;
    --arvore)  [ $# -ge 2 ] && [ -n "${2}" ] || uso "--arvore exige uma pasta"; ARVORE="${2}"; shift 2 ;;
    --dir)     [ $# -ge 2 ] && [ -n "${2}" ] || uso "--dir exige uma pasta"; DIR="${2}"; shift 2 ;;
    --)        shift; while [ $# -gt 0 ]; do ARQS+=("${1}"); shift; done ;;
    --*)       uso "opção desconhecida: ${1}" ;;
    *)         ARQS+=("${1}"); shift ;;
  esac
done

if ! command -v python3 >/dev/null 2>&1; then
  echo "⚠️  python3 ausente: não consigo ler ${CHAVE} do sdd/config.yaml"
  printf 'RESULTADO: INCONCLUSIVO\n→ instale python3 >= 3.9 e rode de novo; isto não é verde.\n'
  exit 3
fi

GIT=0
if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then GIT=1; else ROOT="$(pwd -P)"; fi
cd "${ROOT}" || uso "não consegui entrar em ${ROOT}"
CONFIG="${ROOT}/sdd/config.yaml"

# Lê o valor: 1ª linha da saída = VALOR | AUSENTE | ASPAS <linha> | AMBIGUO; o resto é o valor.
LIDO="$(python3 -B - "${CHAVE}" "${CONFIG}" <<'PY'
import re, shlex, sys
secao, chave = sys.argv[1].split(".", 1)
try:
    linhas = open(sys.argv[2], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    print("AUSENTE"); sys.exit(0)
dentro = False
for n, l in enumerate(linhas, 1):
    if not l.strip() or l.lstrip().startswith("#"):
        continue  # linha vazia ou comentário (inclusive na coluna 0) não fecha a seção
    if re.match(r"^\S", l):
        dentro = l.split("#", 1)[0].strip() == secao + ":"
        continue
    m = re.match(r"^\s+" + re.escape(chave) + r":(.*)$", l) if dentro else None
    if not m:
        continue
    v = m.group(1).strip()
    if v[:1] == '"':
        out, i = [], 1
        while i < len(v) and v[i] != '"':
            if v[i] == "\\" and i + 1 < len(v):
                i += 1
            out.append(v[i]); i += 1
        if i >= len(v):
            print("ASPAS %d" % n); sys.exit(0)
        v = "".join(out)
    elif v[:1] == "'":
        fim = re.match(r"'((?:[^']|'')*)'", v)
        if not fim:
            print("ASPAS %d" % n); sys.exit(0)
        v = fim.group(1).replace("''", "'")
    else:
        v = re.split(r"\s#", v, 1)[0].strip()
    v = v.strip()
    if v:
        try:
            if shlex.split(v, comments=True) != shlex.split(v):
                print("COMENTARIO %d" % n); sys.exit(0)
        except ValueError:
            pass  # aspas do shell sem fechar: o bash -n abaixo diz onde
    print("VALOR")
    sys.stdout.write(v)
    sys.exit(0)
print("AUSENTE")
PY
)" || { echo "⚠️  não consegui ler ${CONFIG}"; printf 'RESULTADO: INCONCLUSIVO\n→ confira o arquivo e rode de novo; isto não é verde.\n'; exit 3; }

ESTADO="${LIDO%%$'\n'*}"
CMD=""; [ "${LIDO}" != "${ESTADO}" ] && CMD="${LIDO#*$'\n'}"
case "${ESTADO}" in
  "ASPAS "*)      uso "sdd/config.yaml, linha ${ESTADO#ASPAS }: o valor de ${CHAVE} abre aspas e não fecha" "feche as aspas do valor (uma linha só) e rode de novo" ;;
  "COMENTARIO "*) uso "sdd/config.yaml, linha ${ESTADO#COMENTARIO }: o comando de ${CHAVE} tem um comentário (#); os arquivos cairiam dentro dele" "tire o # do comando (o comentário vai numa linha própria do config) ou aponte para um script" ;;
esac
if [ "${ESTADO}" != "VALOR" ] || [ -z "${CMD}" ]; then
  if [ -f "${CONFIG}" ]; then echo "ℹ️  ${CHAVE} vazio: pulado (${CONFIG})"
  else echo "ℹ️  ${CHAVE} vazio: pulado (sem ${CONFIG})"; fi
  printf 'RESULTADO: PULADO\n→ diga que o passo foi pulado porque o slot está vazio; para usá-lo, preencha %s em sdd/config.yaml.\n' "${CHAVE}"
  exit 11
fi

ERRO="$(bash -n -c "${CMD} \"\$@\"" 2>&1)" || uso "o comando de ${CHAVE} tem erro de sintaxe: $(printf '%s' "${ERRO}" | head -1)" "corrija o comando em sdd/config.yaml (uma linha só; com |, ; ou &&, aponte para um script)"

# SHAs: a ref dada que não resolve é erro de chamada; o padrão que não resolve vira variável vazia, com aviso.
resolve() { git rev-parse --verify --quiet "${1}^{commit}" 2>/dev/null; }
BASE_SHA=""; COMMIT_SHA=""
if [ "${BASE_DADA}" = "1" ]; then
  BASE_SHA="$(resolve "${BASE}")" || uso "--base ${BASE} não resolve para um commit" "confira a ref (um git fetch traz as do remoto)"
elif [ "${GIT}" = "1" ]; then
  DB="$(sed -n 's/^[[:space:]]*default_branch:[[:space:]]*//p' "${CONFIG}" 2>/dev/null | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d "\"' ")"
  BASE="origin/${DB:-main}"
  BASE_SHA="$(resolve "${BASE}")" || { BASE_SHA=""; echo "⚠️  SDD_BASE vazio: ${BASE} não existe neste repositório"; }
else
  echo "⚠️  SDD_BASE vazio: sem git"
fi
if [ "${COMMIT_DADO}" = "1" ]; then
  COMMIT_SHA="$(resolve "${COMMIT}")" || uso "--commit ${COMMIT} não resolve para um commit" "confira o SHA; se ele nasceu no remoto (merge de PR), rode GIT_TERMINAL_PROMPT=0 git fetch antes"
elif [ "${GIT}" = "1" ]; then
  COMMIT_SHA="$(resolve HEAD)" || { COMMIT_SHA=""; echo "⚠️  SDD_COMMIT vazio: o repositório ainda não tem commit"; }
else
  echo "⚠️  SDD_COMMIT vazio: sem git"
fi
[ -n "${ARVORE}" ] || ARVORE="${ROOT}"

# Pasta comum: derivada do caminho físico da pasta git comum (igual em toda worktree, subpasta ou symlink).
if [ -z "${DIR}" ]; then
  if [ "${GIT}" = "1" ]; then
    COMUM="$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)" || COMUM="${ROOT}"
  else
    COMUM="${ROOT}"
  fi
  HASH="$(printf '%s' "${COMUM}" | git hash-object --stdin 2>/dev/null | cut -c1-12)"
  [ -n "${HASH}" ] || HASH="$(printf '%s' "${COMUM}" | cksum | tr -c '0-9\n' '_' | cut -c1-12)"
  NOME="${FEATURE:-_sem-feature}"
  case "${NOME}" in */*|.|..) uso "--feature não pode ter / nem ser . ou .." ;; esac
  DIR="${TMPDIR:-/tmp}"; DIR="${DIR%/}/sdd-slot-${HASH}/${NOME}"
  if [ "${MOMENTO}" = "before_ok" ] && [ -d "${DIR}" ]; then
    rm -rf "${DIR}" || uso "não consegui esvaziar ${DIR}" "apague a pasta à mão e rode de novo"
  fi
fi
mkdir -p "${DIR}" 2>/dev/null || uso "não consegui criar a pasta comum ${DIR}" "passe --dir <pasta gravável> ou confira o TMPDIR"

trap 'echo "⚠️  slot.sh interrompido por sinal"; printf "RESULTADO: INCONCLUSIVO\n→ rode de novo; isto não é verde.\n"; exit 3' INT TERM

echo "▶ ${CHAVE} (${MOMENTO}): ${CMD}"
SDD_MOMENTO="${MOMENTO}" SDD_FEATURE="${FEATURE}" SDD_BASE="${BASE_SHA}" SDD_COMMIT="${COMMIT_SHA}" \
SDD_ARVORE="${ARVORE}" SDD_SLOT_DIR="${DIR}" bash -c "${CMD} \"\$@\"" slot ${ARQS[@]+"${ARQS[@]}"}
RC=$?

case "${RC}" in
  0)
    printf 'RESULTADO: OK\n→ siga para o próximo passo.\n'; exit 0 ;;
  2)
    case "${MOMENTO}" in
      before_ok)    ACAO="leve ao bloco do OK como FAIL-candidato: corrigir ou WAIVED com motivo." ;;
      before_push)  ACAO="registre no relatório; isto não segura o push." ;;
      after_deploy) ACAO="pare e pergunte: reverter, corrigir ou seguir com motivo." ;;
      *)            ACAO="não aplique a migration: corrija o SQL e rode de novo." ;;
    esac
    printf 'RESULTADO: REPROVOU\n→ %s\n' "${ACAO}"; exit 2 ;;
  10)
    printf 'RESULTADO: NADA A MEDIR\n→ diga que nada foi medido neste momento e siga.\n'; exit 10 ;;
  *)
    if [ "${RC}" -gt 128 ]; then echo "⚠️  o comando de ${CHAVE} morreu pelo sinal $((RC - 128)) (saiu ${RC})"
    else echo "⚠️  o comando de ${CHAVE} saiu ${RC}, fora do contrato (0 ok · 2 reprovou · 10 nada a medir)"; fi
    printf 'RESULTADO: INCONCLUSIVO\n→ confira a saída acima; isto não é verde.\n'; exit 3 ;;
esac
