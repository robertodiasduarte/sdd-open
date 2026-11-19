#!/usr/bin/env bash
# guardar-chave.sh — grava a chave do OpenRouter no perfil do terminal, sem que ela apareça na tela, no histórico
# ou na conversa com o agente. Quem roda é o aluno, numa janela de terminal dele (nunca o agente).
#
# USO-INICIO
#   bash guardar-chave.sh     pede a chave (ela não aparece enquanto você cola) e grava no perfil do terminal:
#                             macOS com zsh ~/.zshrc · macOS com bash ~/.bash_profile · Linux e WSL ~/.bashrc
#   Exit: 0 gravada · 1 nada gravado (chave vazia ou com caractere inesperado) · 64 sem terminal, perfil que é um
#   atalho (repositório de configurações), ou Git Bash no Windows (lá a chave vai na janela "Variáveis de ambiente")
# USO-FIM
#
# Por que assim: um "export OPENROUTER_API_KEY=…" digitado fica no histórico do terminal; colado na conversa, fica
# na conversa. Aqui a chave é lida por read -s e escrita com o printf embutido do bash (sem processo novo, sem
# argumento visível). O perfil ganha uma cópia de segurança (<perfil>.sdd-antes) na 1ª vez, e as linhas antigas
# da chave saem antes da nova entrar. Só nos testes: SDD_REVISORES_SISTEMA (macos | linux | windows).
# ⚠️ bash 3.2.

set -u
case "${1:-}" in
  -h|--help) sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'; exit 0 ;;
  "") ;;
  *) echo "🛑 guardar-chave: este comando não recebe nada; a chave é pedida depois que ele começa."; exit 64 ;;
esac

sistema="${SDD_REVISORES_SISTEMA:-}"
if [ -z "${sistema}" ]; then
  case "$(uname -s 2>/dev/null)" in
    Darwin) sistema=macos ;;
    MINGW*|MSYS*|CYGWIN*) sistema=windows ;;
    *) sistema=linux ;;
  esac
fi
if [ "${sistema}" = windows ]; then
  echo "🛑 No Windows a chave não vai num arquivo: o editor e o agente só a enxergam pelas variáveis de ambiente da sua conta."
  echo "→ siga o passo a passo da skill: janela \"Variáveis de ambiente\" → Nova → nome OPENROUTER_API_KEY. Nada foi gravado."
  exit 64
fi
if [ ! -t 0 ]; then
  echo "🛑 Rode este comando numa janela de terminal sua, não pelo agente: a chave não pode passar pela conversa."
  echo "→ abra o Terminal, entre na pasta do projeto e rode o mesmo comando. Nada foi gravado."
  exit 64
fi

case "${SHELL:-}" in
  *zsh) perfil="${HOME}/.zshrc" ;;
  *) if [ "${sistema}" = macos ]; then
       # o bash de login do macOS lê só o 1º que existir destes três: criar um .bash_profile novo esconderia o .profile
       perfil="${HOME}/.bash_profile"
       for p in .bash_profile .bash_login .profile; do
         if [ -e "${HOME}/${p}" ]; then perfil="${HOME}/${p}"; break; fi
       done
     else perfil="${HOME}/.bashrc"; fi ;;
esac

if [ -L "${perfil}" ]; then
  echo "🛑 ${perfil} é um atalho para outro arquivo (em geral, um repositório de configurações): a chave iria parar lá e poderia ser publicada."
  echo "→ peça ao agente o caminho à mão do passo a passo da skill. Nada foi gravado."
  exit 64
fi

printf 'Cole a chave do OpenRouter e tecle Enter (ela não aparece enquanto você cola): '
IFS= read -rs K
printf '\n'
case "${K}" in
  "") echo "Nada foi gravado: a chave veio vazia."; exit 1 ;;
  *[!A-Za-z0-9_-]*)
    unset K
    echo "Nada foi gravado: a chave tem espaço, aspas ou outro caractere que uma chave do OpenRouter não tem."
    echo "→ copie a chave de novo (o botão de copiar da página) e rode este comando outra vez."
    exit 1 ;;
esac
case "${K}" in
  sk-or-*) ;;
  *) echo "⚠️ A chave não começa por sk-or-, como as do OpenRouter costumam começar; gravei assim mesmo. Se a próxima conferência disser que ela foi recusada, copie de novo." ;;
esac

if [ -f "${perfil}" ] && [ ! -f "${perfil}.sdd-antes" ]; then
  cp -p "${perfil}" "${perfil}.sdd-antes" || { unset K; echo "Nada foi gravado: não consegui copiar ${perfil}."; exit 1; }
fi
novo="${perfil}.sdd-novo.$$"
: > "${novo}" || { unset K; echo "Nada foi gravado: não consegui escrever ao lado de ${perfil}."; exit 1; }
chmod 600 "${novo}" 2>/dev/null   # o perfil passa a guardar a chave: só o dono lê
if [ -f "${perfil}" ]; then
  while IFS= read -r linha || [ -n "${linha}" ]; do
    case "${linha}" in
      "# OpenRouter — sdd-configurar-revisores") ;;
      *OPENROUTER_API_KEY=*) case "${linha#"${linha%%[![:space:]]*}"}" in
                               # a linha antiga vira o comando nulo (":"): num if/then, um bloco vazio quebraria o perfil
                               OPENROUTER_API_KEY=*|export\ OPENROUTER_API_KEY=*)
                                 printf '%s:  # chave antiga trocada pela sdd-configurar-revisores\n' "${linha%%[![:space:]]*}" >> "${novo}" ;;
                               *) printf '%s\n' "${linha}" >> "${novo}" ;;
                             esac ;;
      *) printf '%s\n' "${linha}" >> "${novo}" ;;
    esac
  done < "${perfil}"
fi
printf '# OpenRouter — sdd-configurar-revisores\nexport OPENROUTER_API_KEY='"'"'%s'"'"'\n' "${K}" >> "${novo}"
unset K
mv "${novo}" "${perfil}" || { rm -f "${novo}"; echo "Nada foi gravado: não consegui trocar ${perfil}."; exit 1; }

case "${perfil}" in "${HOME}"/*) mostra="~/${perfil#"${HOME}"/}" ;; *) mostra="${perfil}" ;; esac
echo "✅ Chave gravada em ${mostra} (o valor não foi mostrado)."
for outro in .zshrc .zprofile .zshenv .zshrc.local .bashrc .bash_profile .bash_login .profile .bashrc.local; do
  [ "${HOME}/${outro}" = "${perfil}" ] && continue
  if [ -f "${HOME}/${outro}" ] && grep -qE '^[[:space:]]*(export[[:space:]]+)?OPENROUTER_API_KEY=' "${HOME}/${outro}"; then
    echo "⚠️ ~/${outro} também tem uma linha da chave do OpenRouter: se for uma chave antiga, ela pode valer no lugar da nova. Apague essa linha à mão, num editor."
  fi
done
[ -f "${perfil}.sdd-antes" ] && echo "   A cópia do perfil de antes ficou em ${mostra}.sdd-antes."
echo "→ Agora feche e abra o agente (e o editor, se o agente roda dentro dele) e peça: continue a configuração dos revisores."
exit 0
