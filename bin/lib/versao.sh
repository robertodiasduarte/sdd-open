#!/usr/bin/env bash
# versao.sh — a versão do pacote, os arquivos que ele instala e a impressão (sha256) de cada um (F22).
# Carregado pelo sdd-open.sh. Só lê; quem escreve o registro é o sdd-open.sh.
#
# ⚠️ bash 3.2 · sem declare -A · ${VAR} com chaves antes de não-ASCII.

# As entradas de sdd/ que o init completa (sdd_faltantes) e que o registro cobre: uma lista só, lida pelas duas.
SDD_ENTRADAS_PACOTE="templates bin hooks review patterns playbook.md invariants.md WORKFLOW_CONTRACTS.yaml"
SDD_REMOTO_PADRAO="https://github.com/robertodiasduarte/sdd-open.git"
SDD_RELEASES_URL="https://github.com/robertodiasduarte/sdd-open/releases"
REGISTRO_REL="sdd/open-instalado.txt"

_RE_VERSAO='^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+-g[0-9a-f]+)?$'
_RE_VERSAO_EXATA='^v[0-9]+\.[0-9]+\.[0-9]+$'

versao_valida() { [[ "${1}" =~ ${_RE_VERSAO} ]]; }          # vX.Y.Z ou vX.Y.Z-N-g<sha>
versao_exata() { [[ "${1}" =~ ${_RE_VERSAO_EXATA} ]]; }     # só vX.Y.Z (nome de tag aceito)

# versao_do_pacote PASTA → VERSAO_PKG (vX.Y.Z… ou "desconhecida") e VERSAO_FONTE (carimbo | describe | pasta |
# desconhecida). Ordem: o VERSION carimbado pelo git archive; o git describe, só quando PASTA é a raiz de um clone
# (um pacote extraído dentro de outro repositório não herda a versão dele); o nome sdd-open-vX.Y.Z da pasta.
versao_do_pacote() {
  local d="${1%/}" v="" top base
  VERSAO_PKG=desconhecida; VERSAO_FONTE=desconhecida
  if [ -f "${d}/VERSION" ]; then
    IFS= read -r v < "${d}/VERSION" || :
    v="${v%$'\r'}"
    if versao_valida "${v}"; then VERSAO_PKG="${v}"; VERSAO_FONTE=carimbo; return 0; fi
  fi
  top="$(git -C "${d}" rev-parse --show-toplevel 2>/dev/null)" || top=""
  if [ -n "${top}" ] && [ "${top}" -ef "${d}" ]; then
    v="$(git -C "${d}" describe --tags --match 'v[0-9]*' 2>/dev/null)" || v=""
    if versao_valida "${v}"; then VERSAO_PKG="${v}"; VERSAO_FONTE=describe; return 0; fi
  fi
  base="${d##*/}"
  case "${base}" in
    sdd-open-v*) v="${base#sdd-open-}"
                 if versao_valida "${v}"; then VERSAO_PKG="${v}"; VERSAO_FONTE=pasta; return 0; fi ;;
  esac
  return 0
}

# versao_chave vX.Y.Z[-N-g…] → chave de 36 dígitos que ordena como a versão ("-N-g" vale um pouco depois de vX.Y.Z).
versao_chave() {
  local v="${1#v}" r x y z n=0
  r="${v%%-*}"
  case "${v}" in *-*) n="${v#*-}"; n="${n%%-*}" ;; esac
  x="${r%%.*}"; r="${r#*.}"; y="${r%%.*}"; z="${r#*.}"
  printf '%09d%09d%09d%09d' "$((10#${x}))" "$((10#${y}))" "$((10#${z}))" "$((10#${n}))"
}

# versao_pacote_menor A B → 0 se A < B. As duas precisam ser versões válidas.
versao_pacote_menor() {
  local LC_ALL=C a b
  a="$(versao_chave "${1}")"; b="$(versao_chave "${2}")"
  [[ "${a}" < "${b}" ]]
}

# instalaveis PACOTE → os caminhos (relativos à raiz) do MANIFEST.txt que o init instala no projeto: os arquivos das
# skills do pacote (sdd-* e ux-review-builder) e os de sdd/ sob SDD_ENTRADAS_PACOTE. Só os que existem no pacote.
instalaveis() {
  local p="${1%/}" l e ok
  [ -f "${p}/MANIFEST.txt" ] || return 1
  while IFS= read -r l || [ -n "${l}" ]; do
    l="${l%$'\r'}"
    case "${l}" in
      .agents/skills/sdd-*/*|.agents/skills/ux-review-builder/*) ok=1 ;;
      sdd/*) ok=""
             for e in ${SDD_ENTRADAS_PACOTE}; do
               case "${l}" in "sdd/${e}"|"sdd/${e}/"*) ok=1; break ;; esac
             done ;;
      *) ok="" ;;
    esac
    [ -n "${ok}" ] && [ -f "${p}/${l}" ] && printf '%s\n' "${l}"
  done < "${p}/MANIFEST.txt"
  return 0
}

tem_sha256() { command -v sha256sum >/dev/null 2>&1 || command -v shasum >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; }

# impressoes BASE → stdin: caminhos relativos a BASE, um por linha · stdout: "<sha256>  <caminho>", na mesma ordem.
# Uma chamada só para a lista inteira (no Git Bash cada processo custa 10 a 20 ms). O sha256sum do Git Bash pode
# marcar o arquivo binário com "*" antes do caminho: a saída é normalizada para dois espaços. 2 = sem ferramenta.
impressoes() {
  local base="${1}" lista
  lista="$(cat)"
  [ -n "${lista}" ] || return 0
  if command -v sha256sum >/dev/null 2>&1; then
    (cd "${base}" && printf '%s\n' "${lista}" | tr '\n' '\0' | xargs -0 sha256sum --)
  elif command -v shasum >/dev/null 2>&1; then
    (cd "${base}" && printf '%s\n' "${lista}" | tr '\n' '\0' | xargs -0 shasum -a 256 --)
  elif command -v python3 >/dev/null 2>&1; then
    (cd "${base}" && printf '%s\n' "${lista}" | python3 -I -c 'import hashlib,sys
for l in sys.stdin.buffer.read().decode("utf-8").split("\n"):
    if l:
        with open(l, "rb") as f:
            sys.stdout.buffer.write((hashlib.sha256(f.read()).hexdigest() + "  " + l + "\n").encode("utf-8"))')
  else
    return 2
  fi | registro_normaliza
}

# sha256_entrada → stdin: o conteúdo · stdout: só o sha256 (64 hex). Para a 2ª impressão, sem o \r, de poucos arquivos.
sha256_entrada() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum | cut -c1-64
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 | cut -c1-64
  elif command -v python3 >/dev/null 2>&1; then
    python3 -I -c 'import hashlib,sys; sys.stdout.write(hashlib.sha256(sys.stdin.buffer.read()).hexdigest() + "\n")'
  else return 2; fi
}

# registro_normaliza → stdin: linhas "<sha> <marca><caminho>" (marca " " ou "*") · stdout: "<sha>  <caminho>".
registro_normaliza() { sed 's/^\([0-9a-f]\{64\}\) [ *]/\1  /'; }

# registro_versao ARQUIVO → a versão da linha "versao:" do registro (vazio se não houver ou se for inválida).
registro_versao() {
  local v
  [ -f "${1}" ] || return 0
  v="$(sed -n 's/^versao:[[:space:]]*\([^[:space:]]*\).*$/\1/p' "${1}" | head -1)"
  v="${v%$'\r'}"
  versao_valida "${v}" && printf '%s\n' "${v}"
  return 0
}

# registro_impressoes ARQUIVO → só as linhas "<sha>  <caminho>" do registro, normalizadas.
registro_impressoes() { tr -d '\r' < "${1}" | grep -E '^[0-9a-f]{64} [ *]' | registro_normaliza; }

# registro_escrever DESTINO VERSAO ← stdin: as impressões. Escreve num .sddtmp e troca com mv (nunca pela metade).
registro_escrever() {
  local dest="${1}" v="${2}"
  {
    printf '# Registro do SDD Open: a versão instalada e a impressão (sha256) de cada arquivo que veio do pacote.\n'
    printf '# Gravado pelo init (1ª instalação) e pelo upgrade. Não edite; apagar faz o próximo upgrade pedir --de.\n'
    printf 'versao: %s\n' "${v}"
    cat
  } > "${dest}.sddtmp" && mv "${dest}.sddtmp" "${dest}"
}
