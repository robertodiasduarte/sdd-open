---
name: sdd-new-session
description: >-
  Abre uma frente de trabalho isolada do SDD Open: confere antes se o git, o repositório, o remoto e o
  acesso a ele estão no lugar (sem pedir senha e sem criar nada se algo faltar), cria uma git worktree
  fora da pasta do projeto com uma branch nova nascida da branch padrão ATUALIZADA do remoto, e abre no
  editor. Use quando o usuário disser /sdd-new-session, "abrir uma frente", "nova sessão", "nova tarefa
  isolada" ou quiser começar uma feature/correção sem misturar com outra em andamento.
compatibility: Requer git >= 2.20 e um agente com acesso ao terminal (bash, zsh ou PowerShell). Branch padrão, editor e pasta das frentes vêm de sdd/config.yaml; slot vazio é descoberto e declarado.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "1.0.0"
  fase: "0"
---

# sdd-new-session — abrir uma frente

> Abra a resposta com o banner: `🧠 NEW-SESSION`.

Um comando, uma tarefa, um diretório: `git worktree` + branch nova nascida do estado **remoto atual**
da branch padrão. A outra ponta é a `sdd-release`.

## Slots do config (`sdd/config.yaml`)

`project.default_branch` · `editor` · `worktree_base`. **Slot vazio = descobrir e declarar** na resposta
("branch padrão: main, descoberta pelo remoto"), nunca adivinhar.

## Regra de todo comando que fala com o remoto

`fetch`, `push`, `pull`, `ls-remote` e `remote show` rodam **sem pedir senha**: `GIT_TERMINAL_PROMPT=0 git …`
no bash/zsh; no PowerShell, `$env:GIT_TERMINAL_PROMPT=0; git …`. Sem isso, um remoto que exige login faz o
git pedir a senha no terminal, e você fica esperando uma resposta que o usuário não vê. Ao usuário, mostre
só a forma do shell em uso. Se um desses comandos ficar parado, olhe se o editor (VS Code, Cursor) abriu
uma janela de login do GitHub — ela é um jeito legítimo de logar e não é desligada.

## Passo 0 — Confirme que dá para abrir a frente (antes de criar qualquer coisa)

Rode `git --version`. São 3 situações diferentes, com respostas diferentes:

- **A ferramenta não executa comando nenhum** (você está num aplicativo de chat, sem acesso ao computador
  do usuário): **pare** e diga que esta tarefa precisa de um agente com acesso ao terminal, aberto na pasta
  do projeto, com o comando de instalação atual do agente que você é.
- **O comando executa, mas o git não existe** (`git: command not found`; no PowerShell,
  `CommandNotFoundException` ou `'git' is not recognized`): **pare** e diga *"O git não está instalado
  neste computador."* com o link https://git-scm.com/downloads, e que depois de instalar é preciso fechar
  e abrir o terminal de novo. Não diga que você está num aplicativo de chat: você está no terminal.
- **O git existe, mas a pasta não é um repositório** (`git rev-parse --show-toplevel` falha): **pare** —
  provavelmente o terminal foi aberto na pasta errada (`cd <pasta do projeto>`), ou o projeto ainda não tem
  git (`git init`).

Depois, o **pré-voo do remoto**, nesta ordem, parando na primeira que falhar:

1. `git remote` vazio ⇒ *"O repositório não tem remoto — a frente nasce dele."* com
   `git remote add origin <url do repositório>`. Há remoto, mas nenhum chamado `origin` (um fork com só
   `upstream`, por exemplo) ⇒ *"O repositório tem remoto, mas nenhum chamado origin — a frente nasce do
   origin."* com `git remote rename <nome> origin` (ou `git remote add origin <url>`). Não é login.
2. Com janela de login do editor configurada (`GIT_ASKPASS` ou `SSH_ASKPASS` definidos, ou `git config core.askPass` não vazio — o terminal de VS Code ou Cursor), comece por um diagnóstico: a mesma consulta
   sem a janela e sem credencial guardada, que não pede nada a ninguém, com teto de 10 segundos —
   `GIT_TERMINAL_PROMPT=0 GIT_ASKPASS= GCM_INTERACTIVE=never GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=8" git -c credential.helper= -c core.askPass= ls-remote --heads origin`
   (PowerShell: `$a=$env:GIT_ASKPASS; try { $env:GIT_TERMINAL_PROMPT=0; $env:GIT_ASKPASS=''; $env:GCM_INTERACTIVE='never'; git -c credential.helper= -c core.askPass= ls-remote --heads origin } finally { $env:GIT_ASKPASS=$a }`).
   Parado ou erro de rede ⇒ é rede (veja abaixo), não janela: `GIT_ASKPASS` definido não prova login
   nenhum — com a rede parada o git nem chega a pedir senha. Qualquer outra resposta ⇒ o remoto respondeu;
   siga. Depois (ou direto, sem `GIT_ASKPASS`), a consulta de verdade, com a janela do editor ligada (quem
   está logado por ela passa): `GIT_TERMINAL_PROMPT=0 GCM_INTERACTIVE=never GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=8" git ls-remote --heads origin`
   (o `GIT_SSH_COMMAND` só se o usuário não tiver ssh próprio configurado — `GIT_SSH_COMMAND`, `GIT_SSH` ou
   `core.sshCommand`; com ele, o ssh não fica parado pedindo a frase-senha da chave nem a confirmação do host)
   (PowerShell: `$env:GIT_TERMINAL_PROMPT=0; $env:GCM_INTERACTIVE='never'; git ls-remote --heads origin` —
   o `GCM_INTERACTIVE` impede a janela do gerenciador de credenciais do Windows, sem desligar a credencial
   já guardada). Passou de 10 segundos sem resposta?
   Interrompa e veja quem está esperando. Leia o resultado:
   - `could not read Username`, `Authentication failed`, `Permission denied (publickey)`,
     `Repository not found` ⇒ *"O GitHub não deixou este computador ler o repositório: ou o endereço está
     errado, ou o repositório é privado e este computador não está logado no GitHub."* com `gh auth login`
     (sem `gh`: instalar em https://cli.github.com); alternativas, numa linha só: chave SSH ou o
     gerenciador de credenciais do git. Remoto fora do GitHub (GitLab, Bitbucket…) ⇒ *"O remoto `<host>`
     recusou o acesso deste computador (login ou permissão)."* — o remédio é o login daquele serviço, nunca
     `gh auth login`.
   - `Host key verification failed` ⇒ este computador nunca confirmou a identidade do servidor por SSH:
     `ssh -T git@<host>` e responder `yes`. Não é problema de login.
   - Parado **depois de o diagnóstico ter pedido login** (`could not read Username`,
     `terminal prompts disabled`, `Permission denied (`) ⇒ *"A janela de login do editor está esperando
     resposta."*: responder a janela, ou `gh auth login` para não depender dela. Nunca diga "sem internet"
     nesse caso.
   - Diagnóstico parado, parado sem prova de pedido de login, `Could not resolve host`, `timed out`,
     `Failed to connect` ⇒ *"Não consegui falar
     com `<host>` agora (sem internet ou rede bloqueada)."* — **não** fale em senha nem em login.
   - Qualquer outra mensagem ⇒ *"Não consegui ler o remoto:"* com a 1ª linha do erro, como veio, e
     `git remote -v` para conferir o endereço. Não chute a causa.
3. Nenhuma branch listada ⇒ *"O repositório remoto ainda não tem nenhum commit — a frente nasce dele."*
   com o primeiro commit (`git add <arquivos>` e `git commit -m "primeiro commit"`) e
   `GIT_TERMINAL_PROMPT=0 git push -u origin <branch atual>`.

Qualquer parada do Passo 0 termina com *"Nada foi criado. Depois de resolver, peça a frente de novo."*
Pré-voo saudável não vira relatório: uma linha (`✅ Pronto para abrir a frente: repo <r>, padrão <b>`) e
siga.

⛔ Não invente uma frente assumindo como o projeto é. Uma frente criada a partir de suposição falha na
primeira vez que for usada, e o usuário não vai saber por quê.

## Passo 1 — Branch padrão, pasta das frentes e editor

- **Branch padrão** — `project.default_branch`; vazio ⇒ a "HEAD branch" de
  `GIT_TERMINAL_PROMPT=0 git remote show origin`. Não é "a branch em que estou agora".
- **Pasta das frentes** — `worktree_base`; vazio ⇒ `../<nome-do-repo>-frentes`. Fora do repositório:
  dentro dele, a worktree apareceria como arquivo não rastreado em todas as outras frentes.
- **Editor** — `editor`; vazio ⇒ o primeiro que existir de `code`, `cursor`, `subl` (`command -v <nome>`
  no bash/zsh, `Get-Command <nome>` no PowerShell).
- **Preparação** — `package.json` versionado com `node_modules` no `.gitignore` ⇒ `npm install` na pasta
  nova; mesma lógica para `requirements.txt` e `composer.json`. `.env` no `.gitignore` com `.env.example`
  versionado ⇒ copiar o `.env` do checkout principal.

## Passo 2 — Crie a frente

1. **Slug** do nome da tarefa: minúsculas, hífens, sem acento ("Relatório mensal" → `relatorio-mensal`).
2. **Aborte se a branch ou a pasta já existirem** (`git show-ref --verify refs/heads/<slug>`,
   `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin <slug>`, e a pasta `<pasta das frentes>/<slug>`).
   Não invente outro nome: peça outro ao usuário. Nada pode ter sido criado antes desta checagem.
3. `GIT_TERMINAL_PROMPT=0 git fetch origin "+refs/heads/<padrão>:refs/remotes/origin/<padrão>"` (refspec
   explícito: num clone de uma branch só, o fetch só com o nome da branch não atualiza `origin/<padrão>`) e
   `git worktree add <pasta das frentes>/<slug> -b <slug> origin/<padrão>` — a partir do estado **remoto**,
   não do local, que pode estar atrasado.
4. Na pasta nova: a preparação, se houver; os arquivos locais (`.env`), copiados do checkout principal.
5. Abra no editor. **Sem editor, não aborte**: a frente já está pronta; mostre o caminho.

**O que esta skill NÃO faz:** não commita, não faz push, não apaga, não integra. Só cria. Fechar a frente
é da `sdd-release`.

## Passo 3 — Responda

1. **Caminho** da pasta e **nome da branch**.
2. **Como encerrar**: a `sdd-release` de dentro da pasta nova; à mão, depois de integrar,
   `git worktree remove "<pasta>"` e `git branch -d <slug>`.
3. Slots descobertos (vazios no `sdd/config.yaml`) e onde fixá-los.
4. **Última linha, destacada:** `⚠️ Continue na janela nova. Esta sessão do agente continua presa à pasta
   onde foi aberta — nenhum cd muda isso.`

## Por que cada regra existe

- **O pré-voo vem antes de qualquer criação** — sem remoto, com o remoto vazio ou sem login, o
  `git worktree add … origin/<padrão>` falha no meio; parar antes, dizendo a causa e que nada foi criado, é
  o que permite simplesmente pedir de novo.
- **Git ausente não é "você está no app de chat"** — o diagnóstico errado manda instalar o agente que já
  está instalado.
- **Nenhum comando de rede pede senha** — o pedido de senha aparece no terminal do agente, não na tela do
  usuário; o agente trava sem que ninguém veja.
- **A branch nasce de `origin/<padrão>` atualizada** — nascer da branch atual herda trabalho pela metade
  de outra tarefa.
- **A sessão do agente não migra** — abrir a pasta nova abre outra janela; sem o aviso final, a frente
  inteira acaba sendo feita no lugar errado.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-new-session`.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
