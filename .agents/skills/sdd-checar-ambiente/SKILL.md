---
name: sdd-checar-ambiente
license: MIT
description: "Diagnostica, sem alterar nada, se este computador e este repositório estão prontos para trabalhar com SDD: repositório git, agente de código, identidade do git, acesso ao remoto (credencial, rede, repositório ainda vazio), o programa do GitHub para o terminal (gh) e o login nele, worktrees órfãs, dependências, editor (também fora do PATH) e dado exposto (senha, certificado A1 ou chave privada já salvos no git; .env fora do .gitignore; npm sem ignore-scripts; repositório público). Responde em uma linha quando está tudo certo e, quando não está, lista o que impede primeiro, cada item com o comando exato que resolve. Use quando o usuário pedir para checar o ambiente, antes de abrir a primeira frente de trabalho num projeto, ou quando algo estranho acontecer (commit que falha, comando não encontrado, worktree que sumiu)."
metadata:
  author: Roberto Dias Duarte
  version: "1.5.1"
  updated: "2026-11"
---

# Checar ambiente

Responder uma pergunta: **este ambiente está pronto para trabalhar com SDD aqui?** Em segundos, sem
mudar nada, dizendo o que consertar.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Verificar | Como executar e O que verificar |
| 2 | Explicar | Como reportar |

Aqui o relatório do `checar.sh` já é a tradução para o aluno: a resposta é o Status e, logo abaixo,
o relatório como veio, sem retraduzir. As outras partes valem na conversa que segue, quando o
aluno pergunta por um item.

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Como executar

**Com bash disponível** (macOS, Linux, ou Git Bash no Windows), rode o script que acompanha esta skill,
de dentro da pasta do projeto:

```bash
bash <pasta desta skill>/scripts/checar.sh
```

e **responda com a saída dele, exatamente como veio** — só o Status antes, sem frase depois, sem
comentário sobre o que foi ou não verificado, sem tradução. O script já faz todas as verificações abaixo
e já imprime o relatório no formato certo; o formato não depende de você. (A pasta desta skill é a que
contém este `SKILL.md`: `.claude/skills/sdd-checar-ambiente/` ou `.agents/skills/sdd-checar-ambiente/`,
no projeto ou na pasta global do agente.)

**Sem bash** (PowerShell puro), faça as verificações abaixo à mão e responda no mesmo formato do
script: blocos `🔴 Dado exposto`, `🔴 Impede o trabalho` e `⚠️ Vale arrumar` só se tiverem itens, e por
último a linha `✅ Pronto: repo …` (ou `✅ Repo …` quando houver problema). Checagem que passou ou não se
aplica não é mencionada fora dessa linha. Termine a linha ✅ com a identificação desta skill:
`sdd-checar-ambiente v1.5.1 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`
(o script faz isso sozinho, lendo a versão deste arquivo).

**Só o dado exposto** — `bash <pasta desta skill>/scripts/checar.sh --segredo` imprime apenas o bloco
`🔴 Dado exposto` (ou nada), sem rede, e sai 1 quando acha algo. É o que o `doctor` do sdd-open roda; o
pré-voo da `sdd-new-session` usa `--frente`.

**Só o editor** — `bash <pasta desta skill>/scripts/checar.sh --editor` imprime na 1ª linha o comando que abre
o editor deste computador (`code`, `cursor`… ou, com o app instalado e o comando fora do PATH, `open -a "<App>"`
no macOS e o caminho do `.cmd` no Windows) e, quando houver, na 2ª `dica: …`; sai 1 sem editor. Não usa git
nem rede. É o que a `sdd-new-session` roda com o slot `editor` vazio.

## Regras

- **Somente leitura.** Não instale, não configure, não conserte, não crie arquivo. Entregue o comando;
  quem roda é o usuário, depois de ver o que está autorizando. Saídas de rede, as duas só de leitura:
  uma consulta anônima ao GitHub, de até 3 segundos, para saber se o repositório é público (se falhar,
  não diga nada sobre isso); e uma consulta `ls-remote` ao remoto, de até 10 segundos, **sem pedir senha**,
  para saber se a credencial e a rede chegam lá e se ele já tem algum commit (com a janela de login de um
  editor presente, uma 2ª `ls-remote` em paralelo, sem janela e sem credencial, separa janela esperando de
  rede parada). No modo normal, uma 3ª, em paralelo com o `ls-remote` e também de até 10 segundos:
  `gh auth status --hostname github.com`, só quando o `origin` é do GitHub ou ainda não há `origin`.
- **Nunca deixe o git pedir senha no terminal**: o agente ficaria esperando uma resposta que ninguém vê.
  Todo comando que fala com o remoto roda com `GIT_TERMINAL_PROMPT=0 git …` no bash/zsh; no PowerShell,
  `$env:GIT_TERMINAL_PROMPT=0; git …`. A janela de login do editor (VS Code, Cursor) **não** é desligada:
  quem está logado no GitHub por ela alcança o remoto sem janela nenhuma.
- **Não invente problema.** Sem `.env.example` versionado, não reclame de `.env` ausente. Sem
  `package.json`, não fale de `node_modules` nem de npm. Sem `.env` na pasta, não fale de `.gitignore`.
  Repositório público, sozinho, não é problema. Um `.pem` com certificado público não é segredo. Um
  alarme falso ensina a ignorar todos os outros.
- **Ordene por consequência, não por categoria.** O que trava vem antes do que incomoda.
- **Descubra, não pergunte.** Tudo abaixo se descobre rodando comandos.
- **Funciona em qualquer shell.** Os comandos de `git` são iguais no bash, no zsh e no PowerShell. Para
  saber se um programa existe, use `command -v <nome>` no bash/zsh ou `Get-Command <nome>` no PowerShell.

## O que verificar, nesta ordem

**1. Onde estou**
- **Antes de tudo, a pasta está sincronizada?** Caminho com `Library/Mobile Documents`, `iCloudDrive`,
  `Library/CloudStorage`, `OneDrive`, `Dropbox`, `Google Drive`, `My Drive` ou `Meu Drive`; ou, no Mac com
  Mesa e Documentos no iCloud, a pasta fica em `~/Desktop` ou `~/Documents` e
  `~/Library/Mobile Documents/com~apple~CloudDocs/Desktop` (ou `Documents`) é um atalho (symlink) — o
  caminho em si não muda. Sincronizada ⇒ é o único achado: mover o projeto para fora da nuvem
  (`.git` e frentes se corrompem ou duplicam com a sincronização). Não siga para as outras checagens.
- `git rev-parse --show-toplevel` — é um repositório git? Se **não** for, esse é o achado mais
  importante, e diga **qual** é o caso, nesta ordem:
  1. a pasta é a pessoal (`~`) ou `/` ⇒ o terminal não está num projeto (não varra a pasta pessoal);
  2. há `.git` em subpasta até 3 níveis (fora de `node_modules`) ⇒ "o projeto está em `./X`": abrir lá
     (de 2 a 3, liste; mais que 3, diga quantas e pergunte qual);
  3. só arquivos do sistema (`.DS_Store`, `desktop.ini`, `Thumbs.db`) ou nada ⇒ ainda não há projeto:
     começar pela `sdd-brainstorm`;
  4. há arquivos e nenhum `.git` ⇒ "este projeto ainda não usa git": a skill `sdd-iniciar-repo` põe no
     git e num GitHub privado. Nunca responda só "`git init`" — publicar sem conferir antes leva planilha
     de cliente e certificado junto.
- Pasta, branch atual (`git branch --show-current`) e se há mudanças não commitadas (`git status --short`).

**2. Agentes disponíveis**
- `claude --version` e `codex --version` — registre a versão de cada um que existir.
- Qual deles está executando esta skill agora.

**3. Git utilizável**
- `git --version`.
- `git config user.name` e `git config user.email`. Sem os dois, o primeiro commit falha com uma
  mensagem que não diz claramente o que fazer. O comando que resolve:
  `git config --global user.name "Seu Nome"` e `git config --global user.email "voce@example.com"`.
- `git remote -v` — há remoto? Qual é a branch principal dele (`GIT_TERMINAL_PROMPT=0 git remote show origin`,
  linha "HEAD branch")?
- **O remoto responde?** `GIT_TERMINAL_PROMPT=0 git ls-remote --heads origin` (PowerShell:
  `$env:GIT_TERMINAL_PROMPT=0; git ls-remote --heads origin`), com teto de 10 segundos. Leia o resultado:
  - lista de branches ⇒ tudo certo;
  - nada listado e nenhum erro ⇒ o repositório remoto ainda não tem nenhum commit (⚠️): o primeiro
    commit e `GIT_TERMINAL_PROMPT=0 git push -u origin <branch atual>`;
  - `could not read Username`, `Authentication failed`, `Permission denied (publickey)`,
    `Repository not found` ⇒ 🔴 credencial: no GitHub, "ou o endereço está errado, ou o repositório é
    privado e este computador não está logado"; o comando é `gh auth login` (sem `gh`: instalar em
    https://cli.github.com); alternativas, numa linha só: chave SSH ou o gerenciador de credenciais do git;
  - `Host key verification failed` ⇒ 🔴 este computador nunca confirmou a identidade do servidor por SSH:
    `ssh -T git@<host>` e responder `yes` — não é problema de login;
  - `Could not resolve host`, `timed out`, `Failed to connect` ou nenhuma resposta em 10 segundos ⇒ ⚠️ sem
    internet ou rede bloqueada — **não** fale em senha nem em login;
  - parou sem resposta e há janela de login de editor configurada (`GIT_ASKPASS`/`SSH_ASKPASS` definidos ou `core.askPass`) ⇒ `GIT_ASKPASS` sozinho não
    prova login (com a rede parada o git nem pede senha). Repita sem a janela e sem credencial guardada,
    também com teto de 10 s: `GIT_TERMINAL_PROMPT=0 GIT_ASKPASS= git -c credential.helper= -c core.askPass= ls-remote --heads origin`.
    Ela pediu login (`could not read Username`, `terminal prompts disabled`, `Permission denied (`) ⇒ 🔴 a
    janela de login do editor está esperando resposta: responder a janela, ou `gh auth login`; parou de
    novo ou deu erro de rede ⇒ ⚠️ sem internet ou rede bloqueada.

**4. Frentes de trabalho (worktrees)**
- `git worktree list` — a 1ª linha é o checkout principal, **não é frente**. Frentes abertas = as linhas
  seguintes. Só o checkout principal ⇒ "nenhuma frente aberta" (dizer "1 frente aberta" aqui descreve
  um estado que não existe).
- **Worktree órfã:** entrada da lista marcada `prunable`, ou cuja pasta não existe mais (alguém
  apagou a pasta à mão). Comando: `git worktree prune`.
- **Frente já integrada ainda aberta:** branch de uma worktree **que não é o checkout principal nem a
  própria branch principal** e que já está contida na principal
  (`git branch --merged origin/<principal>`) **e** que teve commit próprio (`git reflog show <branch>`
  tem alguma entrada `commit`). Branch contida na principal **sem** commit próprio é uma frente recém-
  aberta, não integrada — não sugira removê-la. Comando para a integrada: `git worktree remove <pasta>` e
  depois `git branch -d <branch>`.
- Se existir `sdd/config.yaml` no checkout principal (a primeira linha de
  `git worktree list --porcelain`), leia `project.default_branch` e `worktree_base`: eles dizem a branch
  principal e onde as frentes ficam. A branch do slot vale mais que a referência local `origin/HEAD` (ela
  envelhece) desde que exista no origin; se as duas discordam ⇒ ⚠️ com `git remote set-head origin -a`.

**5. Ferramentas do projeto**
- `package.json` presente e `node_modules` ausente ⇒ falta `npm install` (sem isso o primeiro
  comando do projeto falha com um erro que parece outra coisa); `composer.json` sem `vendor/`, idem —
  os dois são 🔴. `requirements.txt` sem ambiente virtual na pasta é ⚠️: as dependências podem estar
  instaladas fora dele.
- `.env.example` versionado e nenhum `.env` ⇒ falta a configuração local (copiar o exemplo e
  preencher).
- **Programa do GitHub para o terminal (`gh`)**, só no modo normal e só com `origin` do GitHub ou sem
  `origin` (fora do GitHub, não fale dele; o `--frente` não fala dele): ausente ⇒ ⚠️ "O programa do GitHub
  para o terminal (gh) não está instalado — sem ele, publicar o projeto e logar no GitHub ficam manuais.", com
  o comando do sistema em uso (tabela abaixo); instalado e sem conta logada (`gh auth status` falha) ⇒ ⚠️ com
  `gh auth login`; sem resposta em 10 s ⇒ ⚠️ "não deu para conferir o login". **Nunca 🔴**: chave SSH e o
  gerenciador de credenciais continuam valendo. Se o remoto já recusou o acesso com `gh auth login` no 🔴, o
  aviso de login não se repete.
- **Editor**: o escolhido em `git config sdd.editor`, se houver (a `sdd-new-session` grava ali a escolha da
  pessoa); senão, o 1º que existir: no PATH, `code`, `cursor`, `code-insiders`, `windsurf`, `zed`, `subl`, `idea`,
  `pycharm`, `webstorm`; no macOS, fora do PATH, o app `Visual Studio Code`, `Cursor`, `Windsurf`, `Zed` ou
  `Sublime Text` em `/Applications` ou `~/Applications` (o comando vira `open -a "<App>"`); no Windows, fora do
  PATH, `code.cmd` ou `cursor.cmd` em `%LOCALAPPDATA%\Programs`. **Sem editor não é problema** — não entra
  em 🔴 nem em ⚠️; se houver um, cite-o no resumo ✅.

<!-- INSTALAR-INICIO -->
**Instalar o `git` e o `gh` (o programa do GitHub para o terminal)** — o comando do sistema em uso:

| Sistema | git | gh |
|---|---|---|
| macOS | `xcode-select --install` (ou `brew install git`) | `brew install gh` (sem Homebrew: o instalador em https://cli.github.com) |
| Windows | `winget install --id Git.Git -e` | `winget install --id GitHub.cli -e` |
| Linux | o gerenciador da distribuição (`sudo apt install git`) | https://github.com/cli/cli/blob/trunk/docs/install_linux.md |

Depois de instalar, feche e abra o terminal. Login no GitHub: `gh auth login` → **GitHub.com** → **HTTPS** →
**Yes** → **Login with a web browser**. O `gh` não é obrigatório: quem entra por chave SSH ou pelo gerenciador de
credenciais do git não precisa dele.
<!-- INSTALAR-FIM -->

**6. Dado de cliente e segredos** (o computador do escritório tem dado de cliente e certificado A1)
- **Já salvo no git** (`git ls-files`): `.env` ou `.env.*` (exceto `.env.example` e `.env.sample`),
  `.pfx`, `.p12`, e `.pem` que contém `PRIVATE KEY` (`git grep --cached -l "PRIVATE KEY" -- '*.pem'`).
  Cada um é 🔴 Dado exposto, com o comando `git rm --cached "<arquivo>" && echo "<arquivo>" >> .gitignore`
  **e** a medida que protege de fato: trocar as senhas (`.env`), revogar o certificado com a autoridade
  certificadora e emitir outro (`.pfx`/`.p12`), gerar chave nova (`.pem`). Tirar do git não apaga do
  histórico — diga isso.
- **Repositório público:** se o `origin` é do GitHub, consulte
  `https://api.github.com/repos/<dono>/<repo>` sem login (200 = público; privado responde 404), ou
  `gh repo view --json visibility`. Público aparece só no resumo ✅ ("repo x (público no GitHub)"); com
  dado exposto, o item diz que o arquivo já está na internet.
- **`.env` fora do `.gitignore`:** existe `.env` na pasta, não está rastreado, e `git check-ignore -q .env`
  falha ⇒ ⚠️, `echo ".env" >> .gitignore`.
- **npm sem `ignore-scripts`:** há `package.json`, o npm existe e `npm config get ignore-scripts` não é
  `true` ⇒ ⚠️, `npm config set ignore-scripts true`, avisando que um pacote que dependa de script de
  instalação volta com `npm rebuild <pacote> --ignore-scripts=false`.

**Pré-voo de uma frente nova.** A skill `sdd-new-session` roda `bash <pasta desta skill>/scripts/checar.sh --frente`:
só git, repositório, remoto e acesso ao remoto. Qualquer achado vira 🔴, o script sai com código 1 e a
última linha é "Nada foi criado. Depois de resolver, peça a frente de novo."; saudável, sai 0 com uma linha
`✅ Pronto para abrir a frente: …`.

Para um alarme que barra o próximo commit com dado de cliente, a skill é a `sdd-higiene-dado` (instala
com OK); esta aqui só diagnostica.

## Como reportar

Não entregue relatório longo: quem roda isto quer ser desbloqueado, não ler. Quatro blocos, nesta
ordem, **omitindo os vazios**:

1. **🔴 Dado exposto** — senha, certificado ou chave privada já salvos no git. Cada item com o comando
   e a medida que protege (trocar senha, revogar certificado).
2. **🔴 Impede o trabalho** — pasta sincronizada, não é repositório git (com o caso), git sem identidade, dependências faltando.
   Cada item com o **comando exato** que resolve, pronto para copiar.
3. **⚠️ Vale arrumar** — `.env` fora do `.gitignore`, npm sem `ignore-scripts` (estes primeiro),
   worktree órfã, frente integrada ainda aberta, `.env` ausente.
4. **✅ Resumo em uma linha**, terminando com a identificação desta skill — ex.:
   `✅ Pronto: repo meu-app, branch main, 2 frentes abertas, Claude Code 2.1 · sdd-checar-ambiente v1.5.1 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Se estiver tudo certo, a resposta inteira é **o Status e a linha ✅** — nenhuma outra frase antes nem
depois: nada de "Tudo limpo", de lista do que foi verificado ou de oferta de ajuda. Ambiente saudável
não merece parágrafo; quem quer detalhe pergunta.

## Exemplos

Saudável (a resposta inteira são estas duas linhas):

```text
Ambiente: ✅ 1 Verificar · ✅ 2 Explicar
✅ Pronto: repo meu-app, branch main, nenhuma frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.5.1 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

Com o certificado A1 salvo no git de um repositório público:

```text
Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar

🔴 Dado exposto
- O certificado digital certificados/empresa.pfx está salvo no git. Este repositório é público: o arquivo já está na internet.
  git rm --cached "certificados/empresa.pfx" && echo "certificados/empresa.pfx" >> .gitignore
  Depois, revogue o certificado com a autoridade certificadora e emita outro.

✅ Repo meu-app (público no GitHub), branch main, nenhuma frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.5.1 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

Com dois problemas:

```text
Ambiente: ✅ 1 Verificar · ▶️ 2 Explicar

🔴 Impede o trabalho
- O git não tem e-mail configurado — o primeiro commit vai falhar.
  git config --global user.email "voce@example.com"

⚠️ Vale arrumar
- A frente ../meu-app-frentes/relatorio-mensal já foi integrada na main e continua aberta.
  git worktree remove ../meu-app-frentes/relatorio-mensal
  git branch -d relatorio-mensal

✅ Repo meu-app, branch main, 1 frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.5.1 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
