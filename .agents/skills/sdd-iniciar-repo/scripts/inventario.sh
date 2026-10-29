#!/usr/bin/env bash
# inventario.sh — o que entraria no git desta pasta, antes de qualquer `git add`. Só lê.
# Imprime o relatório JÁ NO FORMATO FINAL (a skill repassa como veio):
#   🔴 Senhas e certificados   ⚠️ Planilhas   ⚠️ Arquivos grandes   ⚠️ Dependências
#   🔴 Já passaram pelo histórico (só com commits: publicar leva o histórico inteiro)
#   Proposta de .gitignore     (só as linhas que ainda faltam no .gitignore desta pasta)
#
# Não grava nada no projeto. Sem .git, a lista vem de um repositório descartável em mktemp -d, que
# só serve para o git aplicar o .gitignore existente; é apagado na saída.
# Uso: bash inventario.sh   (de dentro da pasta do projeto)
# Saída: 0 = relatório; 2 = pré-condição que impede (pasta sincronizada, pasta pessoal, dentro de um
# repositório maior, repositório numa subpasta, git ausente) — a mensagem diz o que fazer;
# 1 = não consegui listar os arquivos (nunca vira "nada sensível").

set -u
set -o pipefail

LIMITE_MB=50     # o GitHub avisa acima de 50 MB e recusa acima de 100 MB
MAX_ITENS=10     # itens por bloco; o resto vira "e mais N"
DEPS='(^|/)(node_modules|\.venv|venv)/'

parar() { printf '🔴 %s\n  %s\n' "$1" "$2"; exit 2; }
falhou() { printf '🔴 Não consegui listar os arquivos desta pasta (%s) — o inventário não está completo.\n  Rode de novo; se repetir, mostre esta mensagem.\n' "$1"; exit 1; }

# Mesma regra do checar.sh da sdd-checar-ambiente (cópia: cada skill é instalada sozinha).
pasta_sincronizada() {
  local p d real
  for p in "${PWD}/" "$(pwd -P)/"; do
    case "${p}" in
      */Library/Mobile\ Documents/*|*/iCloudDrive/*) echo "iCloud Drive"; return 0 ;;
      */Library/CloudStorage/OneDrive*|*/OneDrive/*|*/OneDrive\ -\ *) echo "OneDrive"; return 0 ;;
      */Library/CloudStorage/Dropbox*|*/Dropbox/*|*/Dropbox\ \(*) echo "Dropbox"; return 0 ;;
      */Library/CloudStorage/GoogleDrive*|*/Google\ Drive/*|*/My\ Drive/*|*/Meu\ Drive/*) echo "Google Drive"; return 0 ;;
      */Library/CloudStorage/*) echo "uma pasta sincronizada"; return 0 ;;
    esac
  done
  for d in Desktop Documents; do
    [ -L "${HOME}/Library/Mobile Documents/com~apple~CloudDocs/${d}" ] || continue
    real="$(cd "${HOME}/${d}" 2>/dev/null && pwd -P)" || continue
    case "$(pwd -P)/" in "${real}/"*) echo "iCloud Drive (${d})"; return 0 ;; esac
  done
  return 1
}

# ── pré-condições ────────────────────────────────────────────────────────────
command -v git >/dev/null 2>&1 || parar "O git não está instalado." \
  "Instale em https://git-scm.com/downloads, abra o terminal de novo e peça outra vez."
PROVEDOR="$(pasta_sincronizada)" && parar \
  "Esta pasta está dentro do ${PROVEDOR}, que sincroniza tudo o que muda — o .git se corrompe ou duplica com a sincronização." \
  "Mova o projeto para uma pasta fora da nuvem (ex.: ~/Projetos), pelo Finder ou Explorador de Arquivos, e abra o terminal lá."
AQUI="$(pwd -P)"
if [ "${AQUI}" = "$(cd "${HOME}" 2>/dev/null && pwd -P)" ] || [ "${AQUI}" = "/" ]; then
  parar "O terminal está na sua pasta pessoal, não na pasta de um projeto." \
        "cd <pasta do projeto>   (e abra o chat de novo lá dentro)"
fi
RAIZ="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "${RAIZ}" ]; then
  RAIZ="$(cd "${RAIZ}" && pwd -P)"
  [ "${RAIZ}" = "${AQUI}" ] || parar "Esta pasta está dentro do repositório ${RAIZ}, que já usa git." \
    "cd \"${RAIZ}\"   (e abra o chat de novo lá; se o projeto é só esta subpasta, mova-a para fora)"
  COM_GIT=1
else
  SUB="$(find . -mindepth 1 -maxdepth 3 \( -name node_modules -o -name .Trash -o -name Library \) -prune \
           -o -name .git -print 2>/dev/null | sed 's#/\.git$##' | LC_ALL=C sort | head -1)"
  [ -z "${SUB}" ] || parar "O projeto já tem git numa subpasta: ${SUB}." \
    "cd \"${SUB}\"   (e abra o chat de novo lá dentro)"
  COM_GIT=0
fi

# ── o que está ou entraria no git ────────────────────────────────────────────
TMPD=""
trap '[ -n "${TMPD}" ] && rm -rf "${TMPD}"' EXIT
# -z: sem ele o git põe entre aspas o caminho com " ou \ (mesmo com core.quotepath=off) e os filtros
# não reconhecem a extensão. Nome com quebra de linha fica partido (raro; vira dois itens).
if [ "${COM_GIT}" = 1 ]; then
  LISTA="$(git ls-files -z -co --exclude-standard 2>/dev/null | tr '\0' '\n')" || falhou "git ls-files"
else
  TMPD="$(mktemp -d 2>/dev/null)" && [ -d "${TMPD}" ] || falhou "mktemp"
  git init -q --bare "${TMPD}/g" >/dev/null 2>&1 || falhou "git init no temporário"
  LISTA="$(git --git-dir="${TMPD}/g" --work-tree=. ls-files -z -o --exclude-standard 2>/dev/null | tr '\0' '\n')" \
    || falhou "git ls-files"
fi
DEP_DIRS="$(printf '%s\n' "${LISTA}" | grep -E "${DEPS}" | sed -E 's#^((.*/)?(node_modules|\.venv|venv))/.*#\1/#' | LC_ALL=C sort -u)"
ARQS="$(printf '%s\n' "${LISTA}" | grep -Ev "${DEPS}" | grep -v '^$')"

segredos()  { grep -Ei '(^|/)\.env(\.[^/]*)?$|\.(pfx|p12|pem|key)$' | grep -Eiv '(^|/)\.env\.(example|sample)$'; }
planilhas() { grep -Ei '\.(xlsx|xls|csv|ods)$'; }

SEGREDOS="$(printf '%s\n' "${ARQS}" | segredos)"
PLANILHAS="$(printf '%s\n' "${ARQS}" | planilhas)"
GRANDES=""
if [ -n "${ARQS}" ]; then
  GRANDES="$(find . \( -name .git -o -name node_modules -o -name .venv -o -name venv \) -prune \
               -o -type f -size +"${LIMITE_MB}"M -print 2>/dev/null | sed 's#^\./##' \
             | grep -Fx -f <(printf '%s\n' "${ARQS}") | LC_ALL=C sort)"
fi
HISTORICO=""
if [ "${COM_GIT}" = 1 ] && git rev-parse --verify -q HEAD >/dev/null 2>&1; then
  JA_PASSOU="$(git log --all --name-only --format= -z 2>/dev/null | tr '\0' '\n' | LC_ALL=C sort -u)" \
    || falhou "git log"
  JA_PASSOU="$(printf '%s\n' "${JA_PASSOU}" | grep -v '^$')"
  HISTORICO="$( { printf '%s\n' "${JA_PASSOU}" | segredos; printf '%s\n' "${JA_PASSOU}" | planilhas; } | grep -v '^$')"
fi

listar() {   # $1 = cabeçalho, $2 = itens (um por linha); bloco vazio não aparece
  [ -n "$2" ] || return 0
  local n
  n="$(printf '%s\n' "$2" | wc -l | tr -d ' ')"
  printf '%s\n' "$1"
  printf '%s\n' "$2" | head -"${MAX_ITENS}" | sed 's/^/- /'
  [ "${n}" -le "${MAX_ITENS}" ] || printf -- '- e mais %s\n' "$((n - MAX_ITENS))"
}

N=0; [ -n "${ARQS}" ] && N="$(printf '%s\n' "${ARQS}" | wc -l | tr -d ' ')"
if [ "${N}" = 1 ]; then QUANTOS="1 arquivo"; VERBO="entraria"; ESTA="está ou entraria"
else QUANTOS="${N} arquivos"; VERBO="entrariam"; ESTA="estão ou entrariam"; fi
[ "${COM_GIT}" = 1 ] && VERBO="${ESTA}"
printf 'Inventário de %s — %s %s no git.\n' "$(basename "${AQUI}")" "${QUANTOS}" "${VERBO}"
listar "🔴 Senhas e certificados (não podem ir para o git):" "${SEGREDOS}"
listar "⚠️ Planilhas (costumam ter dado de cliente; ninguém lê o conteúdo de .xlsx por você):" "${PLANILHAS}"
if [ -n "${GRANDES}" ]; then
  COM_TAMANHO="$(printf '%s\n' "${GRANDES}" | while IFS= read -r f; do
                   printf '%s (%s MB)\n' "${f}" "$(( $(wc -c < "${f}") / 1048576 ))"; done)"
  listar "⚠️ Arquivos grandes (mais de ${LIMITE_MB} MB; o GitHub recusa acima de 100 MB):" "${COM_TAMANHO}"
fi
listar "⚠️ Dependências (reinstaláveis; não vão para o git):" "${DEP_DIRS}"
listar "🔴 Já passaram pelo histórico do git (publicar leva o histórico inteiro, inclusive o que foi apagado depois):" "${HISTORICO}"
if [ -z "${SEGREDOS}${PLANILHAS}${GRANDES}${DEP_DIRS}${HISTORICO}" ]; then
  printf '✅ Nada sensível encontrado entre os arquivos.\n'
fi

# ── proposta de .gitignore (só o que falta) ──────────────────────────────────
PROPOSTA="# senhas e certificados
.env
.env.*
!.env.example
!.env.sample
*.pfx
*.p12
*.pem
*.key
# dependências (reinstaláveis)
node_modules/
.venv/
venv/
# arquivos do sistema
.DS_Store
Thumbs.db
desktop.ini"
if [ -n "${PLANILHAS}" ]; then
  PROPOSTA="${PROPOSTA}
# planilhas (se alguma for fictícia e precisar ir, tire a linha dela)
*.xlsx
*.xls
*.ods
*.csv"
fi
# Caminho literal no .gitignore: [ ] * ? \ são curinga, # ou ! no começo mudam o sentido e o espaço
# no fim é descartado.
literal() { sed 's/[][*?\\]/\\&/g; s/^[#!]/\\&/; s/ $/\\ /; s#^#/#'; }
if [ -n "${GRANDES}" ]; then
  PROPOSTA="${PROPOSTA}
# arquivos grandes
$(printf '%s\n' "${GRANDES}" | literal)"
fi
# O .gitignore compara maiúsculas e minúsculas como estão (core.ignoreCase=false no Linux): .PFX, .ENV
# ou .XLSX que os padrões acima não pegam entram pelo caminho.
FORA_DO_PADRAO="$(printf '%s\n' "${SEGREDOS}" "${PLANILHAS}" | grep -v '^$' \
  | grep -Ev '(^|/)\.env(\.[^/]*)?$|\.(pfx|p12|pem|key|xlsx|xls|ods|csv)$')"
if [ -n "${FORA_DO_PADRAO}" ]; then
  PROPOSTA="${PROPOSTA}
# mesmos tipos, com maiúsculas no nome
$(printf '%s\n' "${FORA_DO_PADRAO}" | literal)"
fi
ATUAL=""
[ -f .gitignore ] && ATUAL="$(tr -d '\r' < .gitignore)"
# Uma linha "!…" no .gitignore atual desfaz o que vem antes dela: aí nada é dado como já coberto, e a
# proposta inteira vai no fim, onde vence.
NEGA=0; printf '%s\n' "${ATUAL}" | grep -q '^!' && NEGA=1
# Sem `case` dentro de $( ): o bash 3.2 do macOS não interpreta o ")" do padrão.
FALTA="$(printf '%s\n' "${PROPOSTA}" | while IFS= read -r l; do
           if [ "${l#\#}" != "${l}" ] || [ "${NEGA}" = 1 ]; then printf '%s\n' "${l}"; continue; fi
           printf '%s\n' "${ATUAL}" | grep -Fxq -- "${l}" || printf '%s\n' "${l}"
         done | awk '/^#/ { c = $0; next } { if (c != "") { print c; c = "" } print }')"
if [ -n "${FALTA}" ]; then
  printf '\nProposta de .gitignore (linhas que faltam%s):\n%s\n' \
    "$([ -f .gitignore ] && printf ' no .gitignore atual')" "${FALTA}"
else
  printf '\nProposta de .gitignore: o .gitignore atual já cobre tudo.\n'
fi
exit 0
