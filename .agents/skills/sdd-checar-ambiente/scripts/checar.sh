#!/usr/bin/env bash
# checar.sh — diagnóstico read-only do ambiente para trabalhar com SDD neste repositório.
# Faz as verificações e imprime o relatório JÁ NO FORMATO FINAL (a skill só repassa):
#   🔴 Dado exposto        (senha ou certificado já salvo no git)
#   🔴 Impede o trabalho   (cada item com o comando que resolve)
#   ⚠️ Vale arrumar
#   ✅ resumo em uma linha
# Blocos vazios não aparecem. Ambiente saudável = só a linha ✅.
#
# Não instala, não configura, não grava nada. Roda em bash (macOS, Linux, Git Bash no Windows).
# Saídas de rede, as duas somente leitura e com teto de tempo:
#   - uma consulta anônima ao GitHub (3 s) para saber se o repositório é público — se falhar, nada é dito;
#   - um `git ls-remote` no origin (10 s), sem pedir senha, para saber se a credencial e a rede
#     alcançam o remoto e se ele já tem algum commit. Com askpass de editor definido, um 2º `ls-remote`
#     em paralelo, sem askpass e sem credencial, separa "janela de login esperando" de "rede parada".
# Uso: bash checar.sh            (de dentro da pasta do projeto)
#      bash checar.sh --frente   (pré-voo da sdd-new-session: só git, repositório, remoto e alcance;
#                                 todo achado vira 🔴 e a resposta diz que nada foi criado)
#      bash checar.sh --segredo  (só o bloco 🔴 Dado exposto, sem rede: o doctor do sdd-open chama este
#                                 modo; sai 1 com achado e 0 sem achado)
#      bash checar.sh --editor   (só a detecção de editor, sem git e sem rede: 1ª linha o comando, 2ª opcional
#                                 "dica: …"; sai 1 sem editor)
#      bash checar.sh --editores (todos os editores achados, "<nome><TAB><comando>" por linha; sai 1 sem nenhum. A
#                                 sdd-new-session usa a lista para perguntar o padrão na 1ª vez, com o slot editor vazio)
# No modo normal, o `gh auth status` (10 s) roda junto com o ls-remote quando o origin é do GitHub, e sozinho
# quando não há origin: gh ausente, deslogado ou sem resposta vira ⚠️, nunca 🔴.

set -u

MODO=normal
case "${1:-}" in
  --frente) MODO=frente ;;
  --segredo) MODO=segredo ;;
  --editor) MODO=editor ;;
  --editores) MODO=editores ;;
esac

EXPOSTO=""
IMPEDE=""
ARRUMAR_DADO=""   # ⚠️ de dado vem antes dos outros ⚠️ (ordem por consequência)
ARRUMAR=""
add_exposto() { EXPOSTO="${EXPOSTO}- $1"$'\n'"  $2"$'\n'; }
add_impede()  { IMPEDE="${IMPEDE}- $1"$'\n'"  $2"$'\n'; }
add_arrumar_dado() { ARRUMAR_DADO="${ARRUMAR_DADO}- $1"$'\n'"  $2"$'\n'; }
add_arrumar() { ARRUMAR="${ARRUMAR}- $1"$'\n'"  $2"$'\n'; }
# Achado de remoto: no pré-voo da frente impede; no diagnóstico geral, depende do caso.
add_remoto()  { if [ "${MODO}" = frente ]; then add_impede "$1" "$2"; else add_arrumar "$1" "$2"; fi; }
tem() { command -v "$1" >/dev/null 2>&1; }

# ── gh e instalação por sistema (F16) ────────────────────────────────────────
# Copiado igual em sdd-iniciar-repo/scripts/inventario.sh (as skills são instaladas sozinhas):
# tests/test_f16_textos.py compara o texto das duas cópias, de "# ── gh e instalação" até "# ── fim do gh".
# SDD_CHECAR_UNAME e SDD_CHECAR_GH existem para os testes; o padrão é o sistema e o `gh` do PATH.
sistema() {
  case "${SDD_CHECAR_UNAME:-$(uname -s 2>/dev/null)}" in
    Darwin) echo macos ;;
    MINGW*|MSYS*|CYGWIN*|Windows*) echo windows ;;
    *) echo linux ;;
  esac
}
instalar_gh() {
  case "$(sistema)" in
    macos) echo "brew install gh   (sem Homebrew: instalador em https://cli.github.com); depois feche e abra o terminal" ;;
    windows) echo "winget install --id GitHub.cli -e   (depois feche e abra o terminal)" ;;
    *) echo "siga https://github.com/cli/cli/blob/trunk/docs/install_linux.md   (depois feche e abra o terminal)" ;;
  esac
}
# ausente | deslogado | ok | sem resposta. Só lê (o gh consulta a API do GitHub), com teto de 10 s; a saída do
# gh nunca é repassada, só a classificação. Como no ls-remote do checar.sh: o gh roda num grupo de processos
# próprio (set -m) e o vigia mata o GRUPO, porque um filho vivo seguraria a saída depois do gh morto.
gh_estado() {
  local g="${SDD_CHECAR_GH:-gh}" s rc
  command -v "${g}" >/dev/null 2>&1 || { echo ausente; return 0; }
  s="$( ( set -m
          LC_ALL=C GH_PROMPT_DISABLED=1 "${g}" auth status --hostname github.com </dev/null 2>&1 & p=$!
          ( sleep 10; kill -KILL -- "-${p}" ) >/dev/null 2>&1 & w=$!
          wait "${p}"; r=$?
          kill -KILL -- "-${p}" 2>/dev/null
          kill -- "-${w}" 2>/dev/null
          echo "__rc=${r}" ) 2>/dev/null )"
  rc="$(printf '%s\n' "${s}" | sed -n 's/^__rc=//p' | tail -1)"
  if [ "${rc}" = 0 ]; then echo ok
  elif [ "${rc}" = 137 ] || printf '%s' "${s}" | grep -qiE 'error connecting|dial tcp|could not resolve|timeout|timed out'; then
    echo "sem resposta"
  else echo deslogado; fi
}
# ── fim do gh ────────────────────────────────────────────────────────────────

# ── editor (F16) ─────────────────────────────────────────────────────────────
# 1º que existir: no PATH, a lista abaixo; fora do PATH, o app no macOS (open -a) e o .cmd no Windows.
# SDD_CHECAR_EDITOR_PATH (padrão: o PATH) e SDD_APPS_DIRS (padrão: /Applications e ~/Applications) existem para
# os testes. Resultado em EDITOR_CMD (o comando, como a sdd-new-session o usa) e EDITOR_DICA (opcional).
EDITOR_CMD=""
EDITOR_DICA=""
editor_no_path() {   # $2 = o sistema, lido uma vez por quem chama (uname custa caro no Git Bash)
  local d IFS=:
  for d in ${SDD_CHECAR_EDITOR_PATH:-${PATH}}; do
    [ -n "${d}" ] || continue
    [ -f "${d}/$1" ] && [ -x "${d}/$1" ] && return 0
    if [ "$2" = windows ] && { [ -f "${d}/$1.cmd" ] || [ -f "${d}/$1.exe" ]; }; then return 0; fi
  done
  return 1
}
editor_achado() {
  local e d a c lad so IFS=:
  so="$(sistema)"
  for e in code cursor code-insiders windsurf zed subl idea pycharm webstorm; do
    editor_no_path "${e}" "${so}" && { EDITOR_CMD="${e}"; return 0; }
  done
  case "${so}" in
    macos)
      # A ordem da lista de apps manda, como a do PATH: o VS Code em ~/Applications vence o Zed em /Applications.
      for a in "Visual Studio Code" "Cursor" "Windsurf" "Zed" "Sublime Text"; do
        for d in ${SDD_APPS_DIRS:-/Applications:${HOME:-}/Applications}; do
          [ -d "${d}/${a}.app" ] || continue
          EDITOR_CMD="open -a \"${a}\""
          case "${a}" in
            "Visual Studio Code") c=code ;; Cursor) c=cursor ;; Windsurf) c=windsurf ;; *) c="" ;;
          esac
          [ -n "${c}" ] && EDITOR_DICA="para abrir pelo terminal com '${c}', no ${a}: Command Palette (Cmd+Shift+P) → Shell Command: Install '${c}' command in PATH"
          return 0
        done
      done ;;
    windows)
      lad="${LOCALAPPDATA:-}"
      [ -n "${lad}" ] && command -v cygpath >/dev/null 2>&1 && lad="$(cygpath -u "${lad}")"
      [ -n "${lad}" ] || return 1
      for a in "Microsoft VS Code/bin/code.cmd" "cursor/resources/app/bin/cursor.cmd"; do
        [ -f "${lad}/Programs/${a}" ] || continue
        EDITOR_CMD="\"${lad}/Programs/${a}\""
        EDITOR_DICA="o editor está instalado, mas o comando dele não está no PATH: reinstale marcando 'Add to PATH', ou use o caminho acima"
        return 0
      done ;;
  esac
  return 1
}

# Todos os editores achados, um por linha: "<nome>\t<comando>", na ordem da detecção (PATH, depois o app do macOS,
# depois o .cmd do Windows); o mesmo editor achado por dois caminhos sai uma vez, pelo 1º. A sdd-new-session usa a lista
# para perguntar o padrão na 1ª vez, em vez de escolher sozinha.
editor_nome() {
  case "$1" in
    code|"Visual Studio Code"|*/code.cmd) echo "VS Code" ;; cursor|Cursor|*/cursor.cmd) echo "Cursor" ;;
    code-insiders) echo "VS Code Insiders" ;; windsurf|Windsurf) echo "Windsurf" ;; zed|Zed) echo "Zed" ;;
    subl|"Sublime Text") echo "Sublime Text" ;; idea) echo "IntelliJ IDEA" ;; pycharm) echo "PyCharm" ;;
    webstorm) echo "WebStorm" ;; *) echo "$1" ;;
  esac
}
editores_lista() {
  local e d a n lad so vistos="|" IFS=:
  so="$(sistema)"
  for e in code cursor code-insiders windsurf zed subl idea pycharm webstorm; do
    editor_no_path "${e}" "${so}" || continue
    n="$(editor_nome "${e}")"
    case "${vistos}" in *"|${n}|"*) continue ;; esac
    vistos="${vistos}${n}|"; printf '%s\t%s\n' "${n}" "${e}"
  done
  case "${so}" in
    macos)
      for a in "Visual Studio Code" "Cursor" "Windsurf" "Zed" "Sublime Text"; do
        for d in ${SDD_APPS_DIRS:-/Applications:${HOME:-}/Applications}; do
          [ -d "${d}/${a}.app" ] || continue
          n="$(editor_nome "${a}")"
          case "${vistos}" in *"|${n}|"*) break ;; esac
          vistos="${vistos}${n}|"; printf '%s\topen -a "%s"\n' "${n}" "${a}"
          break
        done
      done ;;
    windows)
      lad="${LOCALAPPDATA:-}"
      [ -n "${lad}" ] && command -v cygpath >/dev/null 2>&1 && lad="$(cygpath -u "${lad}")"
      [ -n "${lad}" ] || return 0
      for a in "Microsoft VS Code/bin/code.cmd" "cursor/resources/app/bin/cursor.cmd"; do
        [ -f "${lad}/Programs/${a}" ] || continue
        n="$(editor_nome "${a}")"
        case "${vistos}" in *"|${n}|"*) continue ;; esac
        vistos="${vistos}${n}|"; printf '%s\t"%s"\n' "${n}" "${lad}/Programs/${a}"
      done ;;
  esac
}

# --editores (F16): a lista inteira, sem git e sem rede. Sai 1 sem nenhum editor.
if [ "${MODO}" = editores ]; then
  L="$(editores_lista)"
  [ -n "${L}" ] || exit 1
  printf '%s\n' "${L}"
  exit 0
fi

# --editor (F16): só a detecção, sem git e sem rede. 1ª linha: o comando; 2ª, opcional: "dica: …". Sai 1 sem editor.
if [ "${MODO}" = editor ]; then
  editor_achado || exit 1
  printf '%s\n' "${EDITOR_CMD}"
  [ -n "${EDITOR_DICA}" ] && printf 'dica: %s\n' "${EDITOR_DICA}"
  exit 0
fi
# O pré-voo da frente sai 1 quando bloqueia (a skill para pelo código); o diagnóstico geral sai sempre 0.
# (O --segredo não passa por aqui: sai pelo próprio bloco, logo abaixo da definição de dado_exposto.)
sair() { if [ "${MODO}" = frente ] && [ -n "${IMPEDE}" ]; then exit 1; fi; exit 0; }

# Identificação desta skill, lida do SKILL.md ao lado (fonte única da versão).
SKILL_MD="$(cd "$(dirname "$0")/.." 2>/dev/null && pwd)/SKILL.md"
meta() { grep -m1 "^  $1:" "${SKILL_MD}" 2>/dev/null | sed 's/^[^:]*: *//; s/"//g'; }
VERSAO="$(meta version)"; ATUAL="$(meta updated)"
case "${ATUAL#*-}" in
  01) MES=jan ;; 02) MES=fev ;; 03) MES=mar ;; 04) MES=abr ;; 05) MES=mai ;; 06) MES=jun ;;
  07) MES=jul ;; 08) MES=ago ;; 09) MES=set ;; 10) MES=out ;; 11) MES=nov ;; 12) MES=dez ;; *) MES="" ;;
esac
IDENT=""
[ -n "${VERSAO}" ] && [ -n "${MES}" ] && IDENT=" · sdd-checar-ambiente v${VERSAO} · ${MES}/${ATUAL%%-*} · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest"

relatorio() {   # $1 = linha de resumo (sem o ✅)
  ARRUMAR="${ARRUMAR_DADO}${ARRUMAR}"
  if [ "${MODO}" = frente ]; then
    # Pré-voo: só o que impede abrir a frente. Bloqueio nunca termina em ✅ (pareceria liberado).
    if [ -n "${IMPEDE}" ]; then
      printf '🔴 Impede o trabalho\n%s\n' "${IMPEDE}"
      printf 'Nada foi criado. Depois de resolver, peça a frente de novo.\n'
    else
      printf '✅ Pronto para abrir a frente: %s%s\n' "$1" "${IDENT}"
    fi
    return
  fi
  [ -n "${EXPOSTO}" ] && printf '🔴 Dado exposto\n%s\n' "${EXPOSTO}"
  [ -n "${IMPEDE}" ] && printf '🔴 Impede o trabalho\n%s\n' "${IMPEDE}"
  [ -n "${ARRUMAR}" ] && printf '⚠️ Vale arrumar\n%s\n' "${ARRUMAR}"
  if [ -z "${EXPOSTO}" ] && [ -z "${IMPEDE}" ] && [ -z "${ARRUMAR}" ]; then
    printf '✅ Pronto: %s%s\n' "$1" "${IDENT}"
  else   # "✅ Repo …" (maiúscula; bash 3.2 não tem ${1^})
    printf '✅ %s%s%s\n' "$(printf '%s' "$1" | cut -c1 | tr '[:lower:]' '[:upper:]')" "$(printf '%s' "$1" | cut -c2-)" "${IDENT}"
  fi
}

# ── dado exposto (seção 6 do diagnóstico e o modo --segredo inteiro) ──────────
# Só olha o que o git já guarda (ls-files / grep --cached); não abre nada para escrita. Lê RAIZ e PUBLICO.
exposto() {   # $1 = caminho, $2 = o que é, $3 = medida que protege
  add_exposto "${2} ${1} está salvo no git. ${ONDE}" \
    "git rm --cached \"${1}\" && echo \"${1}\" >> .gitignore"$'\n'"  ${3}"
}
dado_exposto() {
  local f b
  if [ "${PUBLICO}" -eq 1 ]; then
    ONDE="Este repositório é público: o arquivo já está na internet."
  else
    ONDE="Tirar do git não apaga do histórico: se já houve push, quem tem acesso ao repositório tem o arquivo."
  fi
  # O pathspec (sem diferenciar maiúsculas) filtra no próprio git: o case abaixo roda só nos candidatos.
  # Com basename | tr em cada arquivo rastreado, 5 mil arquivos levavam 12 s — e o doctor roda isto em todo init.
  while IFS= read -r -d '' f; do
    b="$(basename "${f}" | tr '[:upper:]' '[:lower:]')"
    case "${b}" in
      .env.example|.env.sample) ;;
      .env|.env.*) exposto "${f}" "O arquivo de senhas" "Depois, troque as senhas e chaves que estão nele." ;;
      *.pfx|*.p12) exposto "${f}" "O certificado digital" "Depois, revogue o certificado com a autoridade certificadora e emita outro." ;;
    esac
  done < <(git -C "${RAIZ}" ls-files -z -- ':(glob,icase)**/.env' ':(glob,icase)**/.env.*' \
             ':(glob,icase)**/*.pfx' ':(glob,icase)**/*.p12' 2>/dev/null)
  # .pem só é segredo quando traz a chave privada; certificado público é comum e não alarma.
  while IFS= read -r -d '' f; do
    exposto "${f}" "A chave privada" "Depois, gere uma chave nova e descarte esta."
  done < <(git -C "${RAIZ}" grep --cached -l -z -I -e "PRIVATE KEY" -- '*.pem' '*.PEM' 2>/dev/null)
}

# --segredo: sem rede, sem agentes, sem frentes. Sem saber se o repositório é público, vale a frase
# "Tirar do git não apaga do histórico" (PUBLICO=0). Fora de um repositório não há o que dizer.
if [ "${MODO}" = segredo ]; then
  RAIZ="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [ -n "${RAIZ}" ] || exit 0
  PUBLICO=0
  dado_exposto
  [ -n "${EXPOSTO}" ] || exit 0
  printf '🔴 Dado exposto\n%s' "${EXPOSTO}"
  exit 1
fi

# ── 2. agentes (antes do git: vale mesmo fora de repositório) ─────────────────
AGENTES=""
if [ "${MODO}" = normal ]; then
  if tem claude; then AGENTES="Claude Code $(claude --version 2>/dev/null | head -1 | awk '{print $1}')"; fi
  if tem codex; then
    v="$(codex --version 2>/dev/null | head -1 | awk '{print $NF}')"
    AGENTES="${AGENTES:+${AGENTES}, }Codex ${v}"
  fi
  [ -n "${AGENTES}" ] || AGENTES="nenhum agente de código no terminal"
fi

# ── 1. onde estou ────────────────────────────────────────────────────────────
# Pasta sincronizada (iCloud, OneDrive, Dropbox, Google Drive): imprime o provedor e sai 0; senão 1.
# Só builtins (o teste do git fora do PATH não tem find). Segmento inteiro: "dropbox-sync/" não acusa.
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
  # Mesa e Documentos no iCloud: o caminho não muda (pwd -P continua ~/Documents); a evidência é o
  # symlink que o iCloud Drive cria para a pasta.
  for d in Desktop Documents; do
    [ -L "${HOME}/Library/Mobile Documents/com~apple~CloudDocs/${d}" ] || continue
    real="$(cd "${HOME}/${d}" 2>/dev/null && pwd -P)" || continue
    case "$(pwd -P)/" in "${real}/"*) echo "iCloud Drive (${d})"; return 0 ;; esac
  done
  return 1
}

# Pasta que não é repositório: qual é o caso (pasta pessoal, git numa subpasta, vazia, sem git).
onde_estou_sem_repo() {
  local aqui subs n lista
  aqui="$(pwd -P)"
  if [ "${aqui}" = "$(cd "${HOME}" 2>/dev/null && pwd -P)" ] || [ "${aqui}" = "/" ]; then
    add_impede "O terminal está na sua pasta pessoal, não na pasta de um projeto." \
               "cd <pasta do projeto>   (e abra o chat de novo lá dentro)"
    return
  fi
  # -mindepth 1, não 2: com 2 o -prune de ./node_modules nunca seria avaliado.
  subs="$(find . -mindepth 1 -maxdepth 3 \( -path ./.git -o -name node_modules -o -name .Trash -o -name Library \) -prune \
            -o -name .git -print 2>/dev/null | sed 's#/\.git$##' | LC_ALL=C sort)"
  if [ -n "${subs}" ]; then
    n="$(printf '%s\n' "${subs}" | wc -l | tr -d ' ')"
    lista="$(printf '%s\n' "${subs}" | head -3 | paste -sd, - | sed 's/,/, /g')"
    if [ "${n}" -eq 1 ]; then
      add_impede "O projeto está em ${subs} — o terminal foi aberto uma pasta acima dele." \
                 "cd \"${subs}\"   (e abra o chat de novo lá dentro)"
    elif [ "${n}" -le 3 ]; then
      add_impede "Há repositórios git nas subpastas ${lista} — o projeto é uma delas." \
                 "cd <uma delas>   (e abra o chat de novo lá dentro)"
    else
      add_impede "Há ${n} pastas com git aqui dentro (${lista}, …) — qual delas é o projeto?" \
                 "cd <pasta do projeto>   (e abra o chat de novo lá dentro)"
    fi
    return
  fi
  if [ -z "$(find . -mindepth 1 -maxdepth 1 ! -name .DS_Store ! -name desktop.ini ! -name Thumbs.db \
               ! -name .localized -print 2>/dev/null | head -1)" ]; then
    add_impede "Ainda não há projeto nesta pasta." \
               "comece pela skill sdd-brainstorm — o git entra quando houver o que guardar"
    return
  fi
  if [ -f "$(dirname "${SKILL_MD}")/../sdd-iniciar-repo/SKILL.md" ]; then
    add_impede "Este projeto ainda não usa git — e a frente nasce do git." \
               "use a skill sdd-iniciar-repo: põe o projeto no git e num GitHub privado, conferindo antes o que não pode ir"
  else
    add_impede "Este projeto ainda não usa git — e a frente nasce do git." \
               "git init, rode o init do sdd-open de novo (ele traz a skill sdd-iniciar-repo, que falta ao lado desta) e peça a sdd-iniciar-repo"
  fi
}

PROVEDOR="$(pasta_sincronizada)" && {
  add_impede "Esta pasta está dentro do ${PROVEDOR}, que sincroniza tudo o que muda — e o .git e as frentes se corrompem ou duplicam com a sincronização." \
             "mova o projeto para uma pasta fora da nuvem (ex.: ~/Projetos), pelo Finder ou Explorador de Arquivos, e abra o terminal lá"
  relatorio "pasta $(basename "$(pwd)")${AGENTES:+, ${AGENTES}}"; sair
}
if ! tem git; then
  add_impede "O git não está instalado — sem ele não há frentes nem publicação." \
             "Instale em https://git-scm.com/downloads e abra o terminal de novo."
  relatorio "${AGENTES}"; sair
fi
RAIZ="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -z "${RAIZ}" ]; then
  onde_estou_sem_repo
  relatorio "pasta $(basename "$(pwd)")${AGENTES:+, ${AGENTES}}"; sair
fi
# sed, não awk '{print $2}': caminho com espaço ("Ana Silva/Projetos/…") quebraria no 1º espaço.
REPO="$(basename "$(git worktree list --porcelain | sed -n 's/^worktree //p' | head -1)")"
BRANCH="$(git branch --show-current 2>/dev/null)"; BRANCH="${BRANCH:-HEAD destacado}"

# ── 3. git utilizável ────────────────────────────────────────────────────────
if [ "${MODO}" = normal ]; then
  [ -n "$(git config user.name 2>/dev/null)" ] || add_impede \
    "O git não tem nome configurado — o primeiro commit vai falhar." \
    "git config --global user.name \"Seu Nome\""
  [ -n "$(git config user.email 2>/dev/null)" ] || add_impede \
    "O git não tem e-mail configurado — o primeiro commit vai falhar." \
    "git config --global user.email \"voce@example.com\""
fi

# Alcance do origin, somente leitura: `ls-remote` não muda nada. Sem prompt de senha (o agente
# travaria esperando uma resposta que ninguém vê) e com teto de 10 s. O ls-remote roda num grupo de
# processos próprio (set -m) e o vigia mata o GRUPO: matar só o git deixaria um neto (ssh com
# ProxyCommand) segurando a saída — medido, o neto terminava com rc 0 e parecia sucesso.
# Imprime a saída do git e, na última linha, __rc=<código>.
#
# Askpass de editor (VS Code/Cursor) presente: "parado no teto" tem duas causas que o tempo sozinho não
# separa — a janela de login esperando resposta, ou a rede que não responde (aí o askpass nem é chamado).
# Uma 2ª consulta, em paralelo e só de diagnóstico, roda SEM askpass e SEM credencial guardada (não pede
# nada a ninguém nem lê senha): se o remoto respondeu a ela pedindo login, a rede está boa e quem segura
# a 1ª é a janela (__login=0). A 1ª consulta continua com o askpass do usuário — quem está logado pelo
# editor alcança o remoto. Nada é gravado: o veredito volta pelo código de saída.
TEM_ASKPASS=""
[ -n "${GIT_ASKPASS:-}${SSH_ASKPASS:-}$(git config core.askPass 2>/dev/null)" ] && TEM_ASKPASS=1
PEDIU_LOGIN='terminal prompts disabled|could not read (username|password)|permission denied \('
alcance() {
  local ssh_cmd=""
  if [ -z "${GIT_SSH_COMMAND:-}" ] && [ -z "${GIT_SSH:-}" ] && [ -z "$(git config core.sshCommand 2>/dev/null)" ]; then
    ssh_cmd="ssh -o BatchMode=yes -o ConnectTimeout=8"
  fi
  ( set -m
    # LC_ALL/LANGUAGE=C: a classificação lê as mensagens do git em inglês; traduzidas, credencial recusada
    # viraria "Não consegui ler o remoto" e a janela do editor viraria "sem internet".
    export GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never LC_ALL=C LANGUAGE=C
    [ -n "${ssh_cmd}" ] && export GIT_SSH_COMMAND="${ssh_cmd}"
    git -c http.lowSpeedLimit=1 -c http.lowSpeedTime=8 ls-remote --heads origin </dev/null 2>&1 &
    p=$!
    q=""
    if [ -n "${TEM_ASKPASS}" ]; then
      # GIT_ASKPASS vazio desliga também o core.askPass e o SSH_ASKPASS (prompt.c); credential.helper
      # vazio zera a lista de helpers. Só esta consulta; a de cima segue intacta.
      ( unset SSH_ASKPASS; export GIT_ASKPASS="" SSH_ASKPASS_REQUIRE=never
        git -c core.askPass= -c credential.helper= -c http.lowSpeedLimit=1 -c http.lowSpeedTime=8 \
          ls-remote --heads origin </dev/null 2>&1 | grep -q -i -E "${PEDIU_LOGIN}" ) >/dev/null 2>&1 &
      q=$!
    fi
    # TERM no grupo e, 1 s depois, KILL: um descendente que ignora o TERM seguraria o teto.
    ( sleep 10; kill -TERM -- "-${p}" ${q:+"-${q}"}; sleep 1; kill -KILL -- "-${p}" ${q:+"-${q}"} ) >/dev/null 2>&1 &
    w=$!
    wait "${p}"; rc=$?
    if [ -n "${q}" ]; then
      if [ "${rc}" = 143 ] || [ "${rc}" = 137 ]; then
        wait "${q}"; echo "__login=$?"   # o vigia já cortou as duas: não estica o teto
      else
        kill -TERM -- "-${q}"            # a consulta de verdade terminou: o diagnóstico sobra
      fi
    fi
    # O git já saiu, mas um descendente que ignorou o TERM ainda seguraria a saída: KILL nos grupos antes de
    # cancelar o vigia (só os grupos desta consulta; ao término normal eles já estão vazios).
    kill -KILL -- "-${p}" ${q:+"-${q}"} 2>/dev/null
    # O vigia também tem grupo próprio (set -m): matar só o subshell deixava o `sleep` dele órfão.
    kill -- "-${w}" 2>/dev/null
    echo "__rc=${rc}" ) 2>/dev/null
}

# Host do remoto, para as mensagens (https://h/…, ssh://[u@]h[:p]/…, u@h:…). Outro formato ⇒ vazio.
host_de() {
  printf '%s' "$1" | sed -n -E 's#^[a-z+]+://([^@/]+@)?([^/:]+).*#\2#p; s#^[^@/]+@([^:/]+):.*#\1#p' | head -1
}

PRINCIPAL=""
URL_ORIGIN=""
if [ -z "$(git remote 2>/dev/null)" ]; then
  add_remoto "O repositório não tem remoto — nada que você fizer sai desta máquina, e as frentes nascem dele." \
             "git remote add origin <url do repositório>   (projeto ainda sem repositório no GitHub? a skill sdd-iniciar-repo cria um privado e envia)"
elif [ -z "$(git config --get remote.origin.url 2>/dev/null)" ]; then
  # Há remoto, mas não o origin: as frentes e a publicação usam origin/<principal>.
  add_remoto "O repositório tem remoto, mas nenhum chamado origin — as frentes nascem do origin." \
             "git remote rename $(git remote | head -1) origin   (ou: git remote add origin <url do repositório>)"
else
  PRINCIPAL="$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')"
  if [ -z "${PRINCIPAL}" ]; then
    for b in main master; do git show-ref --verify --quiet "refs/remotes/origin/${b}" && { PRINCIPAL="${b}"; break; }; done
  fi
  # A URL crua (git config), não a de `git remote get-url`, que já aplica os insteadOf.
  URL_ORIGIN="$(git config --get remote.origin.url 2>/dev/null)"
fi

# Repositório público? Só GitHub; consulta anônima (repo privado responde 404 sem login).
# Público sozinho não é problema: só aparece no resumo, e agrava o 🔴 Dado exposto.
# Roda EM PARALELO com o ls-remote (abaixo): em sequência, rede parada somava 3 s ao teto de 10 s.
# Imprime __publico=1 quando é público; nada quando não é ou quando a consulta falha.
PUBLICO=0
GH=""   # estado do gh (F16): só no modo normal, com origin do GitHub ou sem origin
SLUG="$(printf '%s' "${URL_ORIGIN}" \
  | sed -n -E 's#^(https?://([^@/]+@)?|ssh://([^@/]+@)?|git@)github\.com[:/]([^/]+/[^/]+)$#\4#p' | sed 's#\.git$##; s#/$##')"
# Só curl (vem com macOS, Linux e o Git for Windows): ele tem teto de 3 s. O `gh repo view` não tem
# teto e seguraria o diagnóstico inteiro; sem curl, a visibilidade fica desconhecida e nada é dito.
publico() {
  if tem curl; then
    [ "$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "${SDD_CHECAR_GITHUB_API:-https://api.github.com}/repos/${SLUG}" 2>/dev/null)" = "200" ] && echo "__publico=1"
  fi
}

if [ -n "${URL_ORIGIN}" ]; then
  # A consulta à API vai para o fundo; a saída do ls-remote é guardada e só impressa depois do wait, para
  # as duas não se misturarem no meio de uma linha. Teto total = o maior dos dois, não a soma.
  SAIDA="$(
    [ -n "${SLUG}" ] && [ "${MODO}" = normal ] && { publico </dev/null & }
    [ -n "${SLUG}" ] && [ "${MODO}" = normal ] && { echo "__gh=$(gh_estado)" </dev/null & }
    s="$(alcance)"; wait; printf '%s\n' "${s}"
  )"
  [ -n "$(printf '%s\n' "${SAIDA}" | grep -x '__publico=1')" ] && PUBLICO=1
  GH="$(printf '%s\n' "${SAIDA}" | sed -n 's/^__gh=//p' | tail -1)"
  SAIDA="$(printf '%s\n' "${SAIDA}" | grep -v -x '__publico=1' | grep -v '^__gh=')"
  RC="$(printf '%s\n' "${SAIDA}" | sed -n 's/^__rc=//p' | tail -1)"
  # Só as refs contam: stderr chega junto (avisos de redirecionamento ou de host novo não são refs).
  REFS="$(printf '%s\n' "${SAIDA}" | grep -E "^[0-9a-f]{40}"$'\t'"refs/heads/" || true)"
  LOGIN="$(printf '%s\n' "${SAIDA}" | sed -n 's/^__login=//p' | tail -1)"
  ERRO="$(printf '%s\n' "${SAIDA}" | grep -v -E '^__(rc|login)=' | grep -v -E "^[0-9a-f]{40}"$'\t' || true)"
  ERRO_MIN="$(printf '%s' "${ERRO}" | tr '[:upper:]' '[:lower:]')"
  HOST="$(host_de "${URL_ORIGIN}")"
  ONDE_HOST="${HOST:-o remoto}"
  if [ "${RC}" = "0" ]; then
    if [ -z "${REFS}" ]; then
      if git rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
        PRIMEIRO="GIT_TERMINAL_PROMPT=0 git push -u origin ${BRANCH}"
      else
        PRIMEIRO="git add <arquivos do projeto> && git commit -m \"primeiro commit\" && GIT_TERMINAL_PROMPT=0 git push -u origin ${BRANCH}"
      fi
      add_remoto "O repositório remoto ainda não tem nenhum commit — as frentes nascem dele." "${PRIMEIRO}"
    elif [ -z "${PRINCIPAL}" ]; then
      for b in main master; do
        printf '%s\n' "${REFS}" | grep -q "refs/heads/${b}\$" && { PRINCIPAL="${b}"; break; }
      done
      [ -n "${PRINCIPAL}" ] || PRINCIPAL="$(printf '%s\n' "${REFS}" | head -1 | sed 's#.*refs/heads/##')"
    fi
  else
    case "${ERRO_MIN}" in
      *"host key verification failed"*|*"remote host identification has changed"*)
        CMD="ssh -T git@${ONDE_HOST}   (responda yes quando ele perguntar)"
        [ "${HOST}" = "github.com" ] && CMD="${CMD}"$'\n'"  Confira a impressão digital em https://docs.github.com/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints"
        add_impede "Este computador ainda não confirmou a identidade de ${ONDE_HOST} para SSH." "${CMD}" ;;
      *"could not read username"*|*"could not read password"*|*"authentication failed"*|*"terminal prompts disabled"*|*"permission denied (publickey"*|*"repository not found"*|*"returned error: 403"*)
        if [ -n "${SLUG}" ]; then
          if tem "${SDD_CHECAR_GH:-gh}"; then CMD="gh auth login"; else CMD="Instale o GitHub CLI (https://cli.github.com) e rode: gh auth login"; fi
          CMD="${CMD}"$'\n'"  Alternativas: chave SSH (ssh-keygen e cadastrar a chave pública no GitHub) ou o gerenciador de credenciais do git."
        else
          # Fora do GitHub, gh auth login não resolve: o login é o do próprio serviço.
          CMD="Faça login em ${ONDE_HOST} do jeito desse serviço (token de acesso ou chave SSH cadastrada nele) e rode de novo."
        fi
        if [ -n "${SLUG}" ] && [ "${PUBLICO}" -eq 1 ]; then
          MSG="O GitHub não deixou este computador ler ${SLUG}: confira o endereço do remoto e a sua permissão no repositório."
        elif [ -n "${SLUG}" ]; then
          MSG="O GitHub não deixou este computador ler ${SLUG}: ou o endereço está errado, ou o repositório é privado e este computador não está logado no GitHub."
        else
          MSG="O remoto ${ONDE_HOST} recusou o acesso deste computador (login ou permissão)."
        fi
        add_impede "${MSG}" "${CMD}" ;;
      *"could not resolve host"*|*"operation too slow"*|*"timed out"*|*"failed to connect"*|*"connection refused"*|*"network is unreachable"*|*"connect to host"*)
        add_remoto "Não consegui falar com ${ONDE_HOST} agora (sem internet ou rede bloqueada)." \
                   "Quando a conexão voltar, rode de novo — sem o remoto não dá para abrir frente nem publicar." ;;
      *)
        if { [ "${RC}" = "143" ] || [ "${RC}" = "137" ]; } && [ "${LOGIN}" = "0" ]; then
          # O askpass do editor (VS Code/Cursor) não é desligado: quem está logado no GitHub por ele alcança
          # o remoto sem janela nenhuma. O vigia cortou E o remoto, consultado sem askpass, pediu login: a
          # janela ficou esperando. Askpass definido sozinho não prova isso (rede parada nem o chama).
          if tem "${SDD_CHECAR_GH:-gh}"; then CMD="Responda a janela do editor, ou rode: gh auth login"
          else CMD="Responda a janela do editor, ou instale o GitHub CLI (https://cli.github.com) e rode: gh auth login"; fi
          add_impede "A janela de login do editor está esperando resposta (o git pediu usuário e senha para ${ONDE_HOST})." "${CMD}"
        elif [ "${RC}" = "143" ] || [ "${RC}" = "137" ] || [ -z "${ERRO}" ]; then
          # Morto pelo vigia (ou sem nenhuma mensagem): o remoto não respondeu dentro do teto.
          add_remoto "Não consegui falar com ${ONDE_HOST} agora (sem internet ou rede bloqueada)." \
                     "Quando a conexão voltar, rode de novo — sem o remoto não dá para abrir frente nem publicar."
        else
          add_remoto "Não consegui ler o remoto: $(printf '%s\n' "${ERRO}" | grep -v '^[[:space:]]*$' | head -1)" \
                     "git remote -v   (confira o endereço do origin)"
        fi ;;
    esac
  fi
fi

# gh (F16): sem origin, a consulta roda sozinha (quem ainda vai publicar precisa saber cedo); origin fora do
# GitHub, não roda. Nunca 🔴: SSH e o gerenciador de credenciais continuam valendo. Se o remoto já recusou com
# "gh auth login" no 🔴, o aviso não se repete.
if [ "${MODO}" = normal ] && [ -z "${URL_ORIGIN}" ]; then GH="$(gh_estado)"; fi
if [ "${MODO}" = normal ]; then
  case "${IMPEDE}" in
    *"gh auth login"*) ;;
    *) case "${GH}" in
         ausente) add_arrumar "O programa do GitHub para o terminal (gh) não está instalado — sem ele, publicar o projeto e logar no GitHub ficam manuais." \
                              "$(instalar_gh)" ;;
         deslogado) add_arrumar "O gh está instalado, mas nenhuma conta do GitHub está logada nele — publicar o projeto vai pedir esse login." \
                                "gh auth login   (GitHub.com → HTTPS → Yes → Login with a web browser)" ;;
         "sem resposta") add_arrumar "Não deu para conferir o login do gh no GitHub agora (o GitHub não respondeu em 10 s)." \
                                     "Rode de novo quando a conexão voltar; para ver na hora: gh auth status" ;;
       esac ;;
  esac
fi

if [ "${MODO}" = frente ]; then
  relatorio "repo ${REPO}, principal ${PRINCIPAL:-a descobrir}"
  sair
fi

# ── 4. frentes (worktrees) ───────────────────────────────────────────────────
# A 1ª entrada de `git worktree list` é o checkout principal — NÃO é frente.
FRENTES=0
PRIMEIRA=1
wt=""; br=""; prunable=0
fecha_entrada() {
  if [ -n "${wt}" ]; then
    if [ "${PRIMEIRA}" -eq 1 ]; then
      PRIMEIRA=0
    else
      FRENTES=$((FRENTES + 1))
      if [ "${prunable}" -eq 1 ] || [ ! -d "${wt}" ]; then
        add_arrumar "A frente ${wt} não existe mais no disco (a pasta foi apagada à mão)." "git worktree prune"
      elif [ -n "${br}" ] && [ -n "${PRINCIPAL}" ] && [ "${br}" != "${PRINCIPAL}" ] \
           && git merge-base --is-ancestor "${br}" "origin/${PRINCIPAL}" 2>/dev/null \
           && git reflog show --format='%gs' "refs/heads/${br}" 2>/dev/null | grep -q '^commit'; then
        add_arrumar "A frente ${wt} (branch ${br}) já foi integrada na ${PRINCIPAL} e continua aberta." \
                    "git worktree remove \"${wt}\" && git branch -d ${br}"
      fi
    fi
  fi
  wt=""; br=""; prunable=0
}
while IFS= read -r l; do
  case "${l}" in
    "worktree "*) fecha_entrada; wt="${l#worktree }" ;;
    "branch refs/heads/"*) br="${l#branch refs/heads/}" ;;
    prunable*) prunable=1 ;;
  esac
done < <(git worktree list --porcelain)
fecha_entrada

# ── 5. ferramentas do projeto (na raiz desta pasta de trabalho) ──────────────
if [ -f "${RAIZ}/package.json" ] && [ ! -d "${RAIZ}/node_modules" ]; then
  add_impede "As dependências do projeto não estão instaladas (package.json sem node_modules)." "npm install"
fi
if [ -f "${RAIZ}/composer.json" ] && [ ! -d "${RAIZ}/vendor" ]; then
  add_impede "As dependências PHP não estão instaladas (composer.json sem vendor/)." "composer install"
fi
if [ -f "${RAIZ}/requirements.txt" ] && [ ! -d "${RAIZ}/.venv" ] && [ ! -d "${RAIZ}/venv" ]; then
  add_arrumar "requirements.txt sem ambiente virtual nesta pasta (as dependências podem estar instaladas fora dele)." \
              "python3 -m venv .venv && .venv/bin/pip install -r requirements.txt   (Windows: .venv\\Scripts\\pip)"
fi
if [ -f "${RAIZ}/.env.example" ] && [ ! -f "${RAIZ}/.env" ] \
   && [ -n "$(git -C "${RAIZ}" ls-files .env.example 2>/dev/null)" ]; then
  add_arrumar "O projeto espera um .env (há .env.example) e ele não existe nesta pasta." "cp .env.example .env   (e preencha)"
fi

# ── 6. dado de cliente e segredos ────────────────────────────────────────────
dado_exposto

if [ -f "${RAIZ}/.env" ] && [ -z "$(git -C "${RAIZ}" ls-files .env 2>/dev/null)" ] \
   && ! git -C "${RAIZ}" check-ignore -q .env 2>/dev/null; then
  add_arrumar_dado "O .env desta pasta não está no .gitignore — o próximo \"git add .\" leva suas senhas para o git." \
                   "echo \".env\" >> .gitignore"
fi
if [ -f "${RAIZ}/package.json" ] && tem npm \
   && [ "$(cd "${RAIZ}" && npm config get ignore-scripts 2>/dev/null)" != "true" ]; then
  add_arrumar_dado "O npm roda os scripts de instalação de qualquer pacote baixado — é por onde entram pacotes maliciosos." \
                   "npm config set ignore-scripts true   (se um pacote parar de funcionar: npm rebuild <pacote> --ignore-scripts=false)"
fi

# ── resumo ───────────────────────────────────────────────────────────────────
case "${FRENTES}" in
  0) TXT_FRENTES="nenhuma frente aberta" ;;
  1) TXT_FRENTES="1 frente aberta" ;;
  *) TXT_FRENTES="${FRENTES} frentes abertas" ;;
esac
editor_achado
EDITOR_ACHADO="${EDITOR_CMD}"
[ "${PUBLICO}" -eq 1 ] && REPO="${REPO} (público no GitHub)"
RESUMO="repo ${REPO}, branch ${BRANCH}, ${TXT_FRENTES}, ${AGENTES}${EDITOR_ACHADO:+, editor ${EDITOR_ACHADO}}"
relatorio "${RESUMO}"
exit 0
