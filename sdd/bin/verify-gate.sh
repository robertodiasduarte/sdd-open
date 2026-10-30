#!/usr/bin/env bash
# verify-gate.sh — roda o "Verify Gate" de um DEFINE como gate EXECUTÁVEL (pass/fail).
#
# O critério de aceite do DEFINE deixa de ser prosa e vira um COMANDO que as fases de build
# e release rodam e tratam como bloqueante. É o critério de parada de qualquer loop.
#
# O DEFINE carrega um bloco fenced ```yaml ... ``` precedido por `## Verify Gate` com as chaves:
#   kind            test | smoke | eval | typecheck | manual-ux
#   cmd             comando executável  (OU "N/A (manual-ux)")
#   pass_when       critério objetivo   (exit 0 | exit N | contains: TEXTO)
#   threshold       só p/ eval          (ex.: "recall >= 0.80")  — informativo aqui
#   manual_fallback só p/ manual-ux     (checklist humano)
#
# Uso:
#   sdd/bin/verify-gate.sh <DEFINE.md>            # roda o gate do DEFINE
#   sdd/bin/verify-gate.sh --print <DEFINE.md>    # só extrai/mostra o bloco (não roda)
#   sdd/bin/verify-gate.sh --strict <DEFINE.md>   # 3/4/5 saem ≠0 (para CI e pipelines com &&)
#   sdd/bin/verify-gate.sh --sem-define <FEATURE> # release sem DEFINE: só registra no trace e sai 0
#
# Trace (ligado por default; `--trace` é aceito e não muda nada): toda execução que não é --print,
# depois de achar a raiz do repositório, acrescenta 1 linha JSONL em ${SDD_TRACE_DIR:-sdd/traces}/<F>.jsonl
# com ts, feature, src (verify-gate | release), kind, exit (o original, antes do --strict) e define.
# Nunca muda o exit nem a saída; SDD_TRACE=off desliga. "Quantas voltas vermelhas levou a feature X"
# vira `grep -c '"exit":2' sdd/traces/X.jsonl`.
#
# Contrato de exit (INALTERADO pelo --strict, que só remapeia 3/4/5 → 1 no fim):
#   0  = VERDE (passou)              → build e release seguem
#   2  = VERMELHO (falhou)           → build e release ABORTAM
#   3  = INCONCLUSIVO (tool ausente ou ruído de infra) → o humano decide; NÃO é vermelho
#   4  = manual-ux: exige ASSINATURA HUMANA (não auto-passa)
#   5  = CLARIFICAR: DEFINE tem marcador ativo de ambiguidade → voltar ao Define
#   64 = erro de uso / bloco ausente ou malformado → DEFINE sem gate válido
#
# Toda saída termina em `RESULTADO: <PALAVRA>` + `→ <o que fazer>`. Sem --strict, um `&&`
# encadeado trata 3/4/5 como sucesso — por isso o quickstart e os exemplos de CI usam --strict.
#
# ⚠️ bash 3.2 · ${VAR} com chaves antes de não-ASCII.

set -uo pipefail

PRINT_ONLY=0
STRICT=0
SEM_DEFINE=0
while [ $# -gt 0 ]; do
  case "${1}" in
    --print)  PRINT_ONLY=1; shift ;;
    --strict) STRICT=1; shift ;;
    --trace)  shift ;;
    --sem-define) SEM_DEFINE=1; shift ;;
    *) break ;;
  esac
done

DEFINE="${1:-}"

# ---- trace: 1 linha por execução, gravada no EXIT, que nunca muda exit nem saída ------
SDD_TRACE_VAL="${SDD_TRACE:-on}"
SDD_TRACE_DIR_VAL="${SDD_TRACE_DIR:-sdd/traces}"
TRACE_RC=""
TRACE_FEATURE=""
TRACE_SRC="verify-gate"
TRACE_KIND=""
TRACE_DEFINE=""
json_esc() { printf '%s' "${1}" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'; }
trace_gravar() {
  rc="$?"
  [ -n "${TRACE_RC}" ] && rc="${TRACE_RC}"
  [ "${PRINT_ONLY}" = "1" ] && return 0
  [ "${SDD_TRACE_VAL}" = "off" ] && return 0
  [ -n "${TRACE_FEATURE}" ] || return 0
  mkdir -p "${SDD_TRACE_DIR_VAL}" 2>/dev/null || return 0
  printf '{"ts":"%s","feature":"%s","src":"%s","kind":"%s","exit":%s,"define":"%s"}\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${TRACE_FEATURE}" "${TRACE_SRC}" "$(json_esc "${TRACE_KIND}")" "${rc}" \
    "$(json_esc "${TRACE_DEFINE}")" 2>/dev/null >> "${SDD_TRACE_DIR_VAL}/${TRACE_FEATURE}.jsonl" || true
  return 0
}

# ---- veredito final: PALAVRA + ação; --strict remapeia 3/4/5 → 1 -------------------
finalizar() { # $1=exit original
  TRACE_RC="${1}"
  case "${1}" in
    0)  printf 'RESULTADO: VERDE\n→ siga para o próximo passo.\n' ;;
    2)  printf 'RESULTADO: VERMELHO\n→ corrija o que o comando acima apontou e rode de novo.\n' ;;
    3)  printf 'RESULTADO: INCONCLUSIVO\n→ instale a ferramenta ausente ou rode onde ela exista; com --strict isto conta como falha.\n' ;;
    4)  printf 'RESULTADO: ASSINATURA HUMANA\n→ percorra o checklist do manual_fallback e assine no BUILD_REPORT.\n' ;;
    5)  printf 'RESULTADO: CLARIFICAR\n→ resolva os marcadores de ambiguidade no DEFINE e volte ao Define.\n' ;;
    64) printf 'RESULTADO: SPEC INVÁLIDA\n→ o arquivo não existe, não está num repositório git, ou não tem um bloco Verify Gate válido (ver sdd/templates/fragments/VERIFY_GATE.md).\n' ;;
  esac
  if [ "${STRICT}" = "1" ]; then
    case "${1}" in 3|4|5) exit 1 ;; esac
  fi
  exit "${1}"
}

# ---- release sem DEFINE: só o registro no trace -------------------------------------
if [ "${SEM_DEFINE}" = "1" ]; then
  if [ -z "${DEFINE}" ]; then
    echo "🛑 uso: sdd/bin/verify-gate.sh --sem-define <FEATURE>" >&2
    finalizar 64
  fi
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "🛑 não é um repositório git" >&2; finalizar 64; }
  cd "${REPO_ROOT}" || finalizar 64
  TRACE_FEATURE="$(printf '%s' "${DEFINE}" | sed -E 's/[^A-Za-z0-9._-]/_/g')"
  TRACE_SRC="release"; TRACE_KIND="no-define"; TRACE_DEFINE=""
  trap trace_gravar EXIT
  if [ "${SDD_TRACE_VAL}" = "off" ]; then
    echo "ℹ️  ${TRACE_FEATURE}: release sem DEFINE — trace NÃO gravado (SDD_TRACE=off)"
  else
    echo "ℹ️  ${TRACE_FEATURE}: release sem DEFINE — trace no-define gravado (nenhum gate rodou)"
  fi
  finalizar 0
fi

if [ -z "${DEFINE}" ] || [ ! -f "${DEFINE}" ]; then
  echo "🛑 uso: sdd/bin/verify-gate.sh [--print] [--strict] <DEFINE.md> | --sem-define <FEATURE>" >&2
  echo "   (arquivo não encontrado: '${DEFINE:-<vazio>}')" >&2
  finalizar 64
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "🛑 não é um repositório git — o gate resolve caminhos a partir da raiz do repo" >&2; finalizar 64; }
# O caminho do DEFINE relativo à raiz é calculado ANTES do cd (o -f acima é relativo a quem chamou).
DEFINE_ABS="$(cd "$(dirname "${DEFINE}")" 2>/dev/null && pwd -P)/$(basename "${DEFINE}")"
RAIZ_ABS="$(cd "${REPO_ROOT}" 2>/dev/null && pwd -P)"
case "${DEFINE_ABS}" in
  "${RAIZ_ABS}"/*) TRACE_DEFINE="${DEFINE_ABS#"${RAIZ_ABS}"/}" ;;
  *) TRACE_DEFINE="$(basename "${DEFINE}")" ;;
esac
TRACE_FEATURE="$(basename "${DEFINE}" .md | sed -E 's/^DEFINE_//; s/[^A-Za-z0-9._-]/_/g')"
cd "${REPO_ROOT}" || finalizar 64
trap trace_gravar EXIT

# ---- clarificação pendente: DEFINE com dúvida ABERTA não roda gate (exit 5) ---------
# Forma ativa canônica: colchete + "NEEDS CLARIFICATION" + dois-pontos (fragments/CLARIFY.md).
# Menções documentais vivem em code fence ou sem colchetes — o scan remove blocos ``` antes.
# --print é isento (uso de autoria durante a redação do DEFINE).
if [ "${PRINT_ONLY}" -eq 0 ]; then
  PENDENTES="$(awk '/^[[:space:]]*```/{f=!f;next} !f{print NR": "$0}' "${DEFINE_ABS}" | grep '\[NEEDS CLARIFICATION:' || true)"
  if [ -n "${PENDENTES}" ]; then
    echo "🛑 CLARIFICAÇÃO PENDENTE (exit 5) — '${DEFINE}' tem marcador(es) ativo(s) de ambiguidade:" >&2
    printf '%s\n' "${PENDENTES}" | sed 's/^/   │ /' >&2
    echo "   Resolva pelo protocolo (sdd/templates/fragments/CLARIFY.md): ≤5 perguntas," >&2
    echo "   resposta integrada NO CORPO da spec, registro em '## Clarifications'." >&2
    finalizar 5
  fi
fi

# ---- extrair o bloco fenced ```yaml que segue '## Verify Gate' --------------------
BLOCK="$(awk '
  /^##[[:space:]]+Verify Gate/ { insec=1; next }
  insec && /^##[[:space:]]/    { insec=0 }
  insec                        { print }
' "${DEFINE_ABS}" | awk '
  /^```/ { fence = !fence; if (fence) next; else exit }
  fence  { print }
')"

if [ -z "$(printf '%s' "${BLOCK}" | tr -d '[:space:]')" ]; then
  echo "🛑 '${DEFINE}' não tem um bloco '## Verify Gate' com fence \`\`\`yaml … \`\`\`." >&2
  finalizar 64
fi

field() {
  printf '%s\n' "${BLOCK}" \
    | grep -E "^[[:space:]]*${1}:" \
    | head -1 \
    | sed -E "s/^[[:space:]]*${1}:[[:space:]]*//; s/^\"//; s/\"$//; s/[[:space:]]+$//"
}

KIND="$(field kind)"
TRACE_KIND="${KIND}"
CMD="$(field cmd)"
PASS_WHEN="$(field pass_when)"
THRESHOLD="$(field threshold)"

if [ "${PRINT_ONLY}" -eq 1 ]; then
  echo "── Verify Gate de ${DEFINE} ──"
  echo "kind:       ${KIND:-<vazio>}"
  echo "cmd:        ${CMD:-<vazio>}"
  echo "pass_when:  ${PASS_WHEN:-<vazio>}"
  echo "threshold:  ${THRESHOLD:-—}"
  exit 0
fi

if [ -z "${KIND}" ]; then
  echo "🛑 Verify Gate sem 'kind' em '${DEFINE}'." >&2
  finalizar 64
fi

case "${KIND}" in
  test|smoke|eval|typecheck|manual-ux) ;;
  *) echo "🛑 kind inválido: '${KIND}' (use test|smoke|eval|typecheck|manual-ux)" >&2; finalizar 64 ;;
esac

# ---- manual-ux: NÃO auto-passa; é gate humano explícito ----------------------------
if [ "${KIND}" = "manual-ux" ]; then
  echo "🧑‍🎨 Verify Gate kind=manual-ux — exige ASSINATURA HUMANA (não automatizável)."
  echo "   Checklist (manual_fallback) deve ser percorrido e assinado no BUILD_REPORT."
  finalizar 4
fi

if [ -z "${CMD}" ] || [ "${CMD#N/A}" != "${CMD}" ]; then
  echo "🛑 kind=${KIND} exige 'cmd' executável (recebido: '${CMD:-<vazio>}')." >&2
  finalizar 64
fi

# ---- rodar o comando ---------------------------------------------------------------
echo "▶ Verify Gate [${KIND}]: ${CMD}"
OUT="$(bash -c "${CMD}" 2>&1)"
RC=$?
printf '%s\n' "${OUT}" | sed 's/^/   │ /'

# ---- ruído de infra: smoke + 403 (WAF × IP do runner) não é regressão ---------------
if [ "${KIND}" = "smoke" ] && printf '%s' "${OUT}" | grep -qE '(^|[^0-9])403([^0-9]|$)'; then
  if ! printf '%s' "${PASS_WHEN}" | grep -qiE '403'; then
    echo "⚠️  smoke recebeu 403 e o esperado NÃO era 403 → provável bloqueio de rede ao runner, não regressão."
    echo "    Rode o smoke de onde a rota é alcançável."
    finalizar 3
  fi
fi

# ---- ferramenta ausente = inconclusivo, não vermelho ---------------------------------
# Só quando o gate NÃO emitiu veredito próprio: um gate que declarou VERMELHO é vermelho,
# mesmo com ruído de ambiente na saída (um gate que não consegue ficar vermelho não é gate).
if [ "${RC}" -eq 127 ] || { printf '%s' "${OUT}" | grep -qiE 'command not found|: not found' \
     && ! printf '%s' "${OUT}" | grep -qE 'GATE (VERDE|VERMELHO)|RESULTADO: (VERDE|VERMELHO)'; }; then
  echo "⚠️  ferramenta ausente ao rodar o gate (rc=${RC}) — INCONCLUSIVO, não trava por falta de tool."
  finalizar 3
fi
if printf '%s' "${OUT}" | grep -qE 'GATE VERMELHO|RESULTADO: VERMELHO'; then
  echo "🔴 o comando declarou VERMELHO — ruído de ambiente não mascara veredito."
  finalizar 2
fi
# Comando que DECLARA inconclusivo (rc=3 + 'INCONCLUSIVO' na saída) propaga, em vez de virar
# falso vermelho no pass_when.
if [ "${RC}" -eq 3 ] && printf '%s' "${OUT}" | grep -qi 'INCONCLUSIVO'; then
  echo "⚠️  o comando declarou INCONCLUSIVO (rc=3) — propagando; rode onde a dependência exista."
  finalizar 3
fi

# ---- avaliar pass_when --------------------------------------------------------------
PASS_WHEN="${PASS_WHEN:-exit 0}"
passou=0
case "${PASS_WHEN}" in
  exit\ *)
    want="$(printf '%s' "${PASS_WHEN}" | sed -E 's/^exit[[:space:]]+//')"
    [ "${RC}" = "${want}" ] && passou=1 ;;
  contains:*)
    needle="$(printf '%s' "${PASS_WHEN}" | sed -E 's/^contains:[[:space:]]*//')"
    printf '%s' "${OUT}" | grep -qF "${needle}" && passou=1 ;;
  *)
    [ "${RC}" -eq 0 ] && passou=1 ;;
esac

if [ "${passou}" -eq 1 ]; then
  echo "✅ GATE VERDE (${KIND}) — pass_when: '${PASS_WHEN}' satisfeito (rc=${RC})."
  finalizar 0
fi
echo "🛑 GATE VERMELHO (${KIND}) — pass_when: '${PASS_WHEN}' NÃO satisfeito (rc=${RC})." >&2
finalizar 2
