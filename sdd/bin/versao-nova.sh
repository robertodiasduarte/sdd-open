#!/usr/bin/env bash
# versao-nova.sh — saiu versão nova do SDD Open? Uma consulta anônima, só de leitura, com teto de 5 s (F22).
#
#   bash sdd/bin/versao-nova.sh [--raiz <pasta do projeto>] [--atual <vX.Y.Z>] [--curto]
#
# A versão atual vem de --atual ou da linha "versao:" de sdd/open-instalado.txt da raiz (padrão: a pasta atual).
# A consulta é `git ls-remote --tags --refs` do repositório público, sem credencial, sem pergunta e sem mandar
# nada do projeto. Do que volta, só contam as tags vX.Y.Z exatas (o resto é ignorado e nunca executado).
#
# Saída: uma linha com símbolo e palavra. Com --curto, só o dado: a última versão (0 e 10), o motivo (20) ou onde
# a checagem foi desligada (30) — é o que o doctor usa para montar a linha dele.
# Exit: 0 em dia · 10 saiu versão nova · 20 não conferida (sem rede, recusa, teto, nenhuma versão, sem versão
# atual) · 30 desligada · 64 uso. Nunca escreve nada no projeto; nunca bloqueia quem chama.
#
# Desligar: SDD_OPEN_CHECK_UPDATES=0 no ambiente, ou no sdd/config.yaml:
#   open:
#     check_updates: false
# SDD_OPEN_REMOTO troca o endereço consultado (os testes apontam para um repositório local).
#
# ⚠️ bash 3.2. O teto não depende de o processo morrer (no Git Bash o sinal ao grupo não alcança o git.exe): a saída
# do git vai para um arquivo, e quem chama só espera o relógio próprio.

set -u

RAIZ="."; ATUAL=""; CURTO=""
uso() { printf '🛑 %s\nRESULTADO: ERRO DE USO\n→ uso: bash sdd/bin/versao-nova.sh [--raiz <pasta>] [--atual <vX.Y.Z>] [--curto]\n' "${1}" >&2; exit 64; }
while [ $# -gt 0 ]; do
  case "${1}" in
    --raiz) [ $# -ge 2 ] || uso "--raiz sem valor"; RAIZ="${2}"; shift 2 ;;
    --atual) [ $# -ge 2 ] || uso "--atual sem valor"; ATUAL="${2}"; shift 2 ;;
    --curto) CURTO=1; shift ;;
    -h|--help) sed -n '2,19p' "${0}" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) uso "opção desconhecida: ${1}" ;;
  esac
done

RE_VERSAO='^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+-g[0-9a-f]+)?$'
[ -z "${ATUAL}" ] || [[ "${ATUAL}" =~ ${RE_VERSAO} ]] || uso "versão atual inválida: ${ATUAL} (esperado vX.Y.Z)"

# diz SIMBOLO LINHA DADO EXIT: no modo --curto, só o DADO (o símbolo leva o espaço dele, como no say.sh)
diz() {
  if [ -n "${CURTO}" ]; then printf '%s\n' "${3}"; else printf '%s%s\n' "${1}" "${2}"; fi
  exit "${4}"
}
nao_conferida() { diz 'ℹ️  ' "versão nova: não conferida — ${1} (o resto do diagnóstico vale)" "${1}" 20; }

# Desligada: pela variável, ou pelo slot open.check_updates do config do projeto.
if [ "${SDD_OPEN_CHECK_UPDATES:-}" = "0" ]; then
  diz 'ℹ️  ' "versão nova: checagem desligada (SDD_OPEN_CHECK_UPDATES=0 no ambiente)" "SDD_OPEN_CHECK_UPDATES=0 no ambiente" 30
fi
if [ -f "${RAIZ}/sdd/config.yaml" ]; then
  slot="$(sed -n '/^open:/,/^[^[:space:]#]/ s/^[[:space:]]*check_updates:[[:space:]]*//p' "${RAIZ}/sdd/config.yaml" 2>/dev/null \
    | head -1 | sed 's/[[:space:]]*#.*$//' | tr -d "\"' \r")"
  case "${slot}" in
    false|False|FALSE|no|off|0)
      diz 'ℹ️  ' "versão nova: checagem desligada (open.check_updates: false em sdd/config.yaml)" \
          "open.check_updates: false em sdd/config.yaml" 30 ;;
  esac
fi

# A versão atual: --atual, ou o registro do projeto.
if [ -z "${ATUAL}" ] && [ -f "${RAIZ}/sdd/open-instalado.txt" ]; then
  ATUAL="$(sed -n 's/^versao:[[:space:]]*\([^[:space:]]*\).*$/\1/p' "${RAIZ}/sdd/open-instalado.txt" | head -1 | tr -d '\r')"
fi
if [ -z "${ATUAL}" ]; then
  nao_conferida "este projeto ainda não tem o registro de versão; o doctor diz como fazer o 1º upgrade"
fi
[[ "${ATUAL}" =~ ${RE_VERSAO} ]] || uso "versão atual inválida: ${ATUAL} (esperado vX.Y.Z)"

REMOTO="${SDD_OPEN_REMOTO:-https://github.com/robertodiasduarte/sdd-open.git}"

# corta PID...: o grupo de cada pid, ou a árvore dele no Windows (taskkill pelo winpid), como o checar.sh.
corta() {
  local p w
  for p in "$@"; do
    [ -n "${p}" ] || continue
    if [ -r "/proc/${p}/winpid" ]; then
      w="$(cat "/proc/${p}/winpid" 2>/dev/null)"
      [ -n "${w}" ] && MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' taskkill /F /T /PID "${w}" >/dev/null 2>&1
    else
      kill -KILL -- "-${p}" 2>/dev/null || kill -KILL "${p}" 2>/dev/null
    fi
  done
  return 0
}

s="$(mktemp -d 2>/dev/null)" || nao_conferida "sem pasta temporária para a consulta"
# O git vai a 2º plano DENTRO do subshell com set -m: vira líder do próprio grupo, e o pid dele fica no arquivo.
# O subshell inteiro solta a entrada e a saída de quem chamou: um processo que sobreviva ao corte não segura o pipe.
( set -m
  GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never LC_ALL=C git -c credential.helper= ls-remote --tags --refs "${REMOTO}" \
    </dev/null >"${s}/out" 2>"${s}/err" &
  echo "$!" > "${s}/pid"
  wait "$!"; echo "$?" > "${s}/rc.tmp" && mv "${s}/rc.tmp" "${s}/rc" ) </dev/null >/dev/null 2>&1 &
sub=$!
disown "${sub}" 2>/dev/null || :   # sem o aviso "Killed" do bash quando o corte acontece
i=0
while [ ! -s "${s}/rc" ] && [ "${i}" -lt 25 ]; do sleep 0.2; i=$((i + 1)); done
if [ ! -s "${s}/rc" ]; then
  corta "$(cat "${s}/pid" 2>/dev/null)" "${sub}"
  rm -rf "${s}" 2>/dev/null
  nao_conferida "sem resposta em 5 s"
fi
rc="$(cat "${s}/rc")"
if [ "${rc}" != "0" ]; then
  if grep -qiE 'could not resolve|unable to access|failed to connect|connection (timed out|refused)|network is unreachable' \
       "${s}/err" 2>/dev/null; then motivo="não alcancei o endereço (sem internet?)"
  else motivo="o endereço recusou a consulta"; fi
  rm -rf "${s}" 2>/dev/null
  nao_conferida "${motivo}"
fi
# Só "<sha> TAB refs/tags/vX.Y.Z" exatos; a maior por comparação numérica campo a campo.
maior="$(sed -n 's#^[0-9a-f]*[[:space:]][[:space:]]*refs/tags/\(v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\)$#\1#p' "${s}/out" \
  | awk -F'[v.]' '{ k = sprintf("%09d%09d%09d", $2, $3, $4); if (k > m) { m = k; v = $0 } } END { print v }')"
rm -rf "${s}" 2>/dev/null
[ -n "${maior}" ] || nao_conferida "nenhuma versão na lista"

# Compara só vX.Y.Z; "vX.Y.Z-N-g<sha>" (um clone depois da tag) vale como vX.Y.Z para isto: a tag seguinte é maior.
base="${ATUAL%%-*}"
chave() { local r="${1#v}" x y z; x="${r%%.*}"; r="${r#*.}"; y="${r%%.*}"; z="${r#*.}"
  printf '%09d%09d%09d' "$((10#${x}))" "$((10#${y}))" "$((10#${z}))"; }
if [[ "$(chave "${base}")" < "$(chave "${maior}")" ]]; then
  diz '⚠️  ' "saiu a ${maior} (este projeto está na ${base})" "${maior}" 10
fi
diz '✅ ' "versão: em dia — a última publicada é ${maior}" "${maior}" 0
