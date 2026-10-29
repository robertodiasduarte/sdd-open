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

set -u

MODO=normal
case "${1:-}" in
  --frente) MODO=frente ;;
  --segredo) MODO=segredo ;;
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
  while IFS= read -r -d '' f; do
    b="$(basename "${f}" | tr '[:upper:]' '[:lower:]')"
    case "${b}" in
      .env.example|.env.sample) ;;
      .env|.env.*) exposto "${f}" "O arquivo de senhas" "Depois, troque as senhas e chaves que estão nele." ;;
      *.pfx|*.p12) exposto "${f}" "O certificado digital" "Depois, revogue o certificado com a autoridade certificadora e emita outro." ;;
    esac
  done < <(git -C "${RAIZ}" ls-files -z 2>/dev/null)
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
    s="$(alcance)"; wait; printf '%s\n' "${s}"
  )"
  [ -n "$(printf '%s\n' "${SAIDA}" | grep -x '__publico=1')" ] && PUBLICO=1
  SAIDA="$(printf '%s\n' "${SAIDA}" | grep -v -x '__publico=1')"
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
          if tem gh; then CMD="gh auth login"; else CMD="Instale o GitHub CLI (https://cli.github.com) e rode: gh auth login"; fi
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
          if tem gh; then CMD="Responda a janela do editor, ou rode: gh auth login"
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
EDITOR_ACHADO=""
for e in code cursor subl; do tem "${e}" && { EDITOR_ACHADO="${e}"; break; }; done
[ "${PUBLICO}" -eq 1 ] && REPO="${REPO} (público no GitHub)"
RESUMO="repo ${REPO}, branch ${BRANCH}, ${TXT_FRENTES}, ${AGENTES}${EDITOR_ACHADO:+, editor ${EDITOR_ACHADO}}"
relatorio "${RESUMO}"
exit 0
