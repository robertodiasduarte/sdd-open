---
name: sdd-checar-ambiente
license: MIT
description: "Diagnostica, sem alterar nada, se este computador e este repositório estão prontos para trabalhar com SDD: repositório git, agente de código, identidade do git, acesso ao remoto (credencial, rede, repositório ainda vazio), worktrees órfãs, dependências, editor e dado exposto (senha, certificado A1 ou chave privada já salvos no git; .env fora do .gitignore; npm sem ignore-scripts; repositório público). Responde em uma linha quando está tudo certo e, quando não está, lista o que impede primeiro, cada item com o comando exato que resolve. Use quando o usuário pedir para checar o ambiente, antes de abrir a primeira frente de trabalho num projeto, ou quando algo estranho acontecer (commit que falha, comando não encontrado, worktree que sumiu)."
metadata:
  author: Roberto Dias Duarte
  version: "1.3.0"
  updated: "2026-10"
---

# Checar ambiente

Responder uma pergunta: **este ambiente está pronto para trabalhar com SDD aqui?** Em segundos, sem
mudar nada, dizendo o que consertar.

## Como executar

**Com bash disponível** (macOS, Linux, ou Git Bash no Windows), rode o script que acompanha esta skill,
de dentro da pasta do projeto:

```bash
bash <pasta desta skill>/scripts/checar.sh
```

e **responda com a saída dele, exatamente como veio** — sem frase antes, sem frase depois, sem
comentário sobre o que foi ou não verificado, sem tradução. O script já faz todas as verificações abaixo
e já imprime o relatório no formato certo; o formato não depende de você. (A pasta desta skill é a que
contém este `SKILL.md`: `.claude/skills/sdd-checar-ambiente/` ou `.agents/skills/sdd-checar-ambiente/`,
no projeto ou na pasta global do agente.)

**Sem bash** (PowerShell puro), faça as verificações abaixo à mão e responda no mesmo formato do
script: blocos `🔴 Dado exposto`, `🔴 Impede o trabalho` e `⚠️ Vale arrumar` só se tiverem itens, e por
último a linha `✅ Pronto: repo …` (ou `✅ Repo …` quando houver problema). Checagem que passou ou não se
aplica não é mencionada fora dessa linha. Termine a linha ✅ com a identificação desta skill:
`sdd-checar-ambiente v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`
(o script faz isso sozinho, lendo a versão deste arquivo).

**Só o dado exposto** — `bash <pasta desta skill>/scripts/checar.sh --segredo` imprime apenas o bloco
`🔴 Dado exposto` (ou nada), sem rede, e sai 1 quando acha algo. É o que o `doctor` do sdd-open roda; o
pré-voo da `sdd-new-session` usa `--frente`.

## Regras

- **Somente leitura.** Não instale, não configure, não conserte, não crie arquivo. Entregue o comando;
  quem roda é o usuário, depois de ver o que está autorizando. Saídas de rede, as duas só de leitura:
  uma consulta anônima ao GitHub, de até 3 segundos, para saber se o repositório é público (se falhar,
  não diga nada sobre isso); e uma consulta `ls-remote` ao remoto, de até 10 segundos, **sem pedir senha**,
  para saber se a credencial e a rede chegam lá e se ele já tem algum commit (com a janela de login de um
  editor presente, uma 2ª `ls-remote` em paralelo, sem janela e sem credencial, separa janela esperando de
  rede parada).
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
  principal e onde as frentes ficam.

**5. Ferramentas do projeto**
- `package.json` presente e `node_modules` ausente ⇒ falta `npm install` (sem isso o primeiro
  comando do projeto falha com um erro que parece outra coisa); `composer.json` sem `vendor/`, idem —
  os dois são 🔴. `requirements.txt` sem ambiente virtual na pasta é ⚠️: as dependências podem estar
  instaladas fora dele.
- `.env.example` versionado e nenhum `.env` ⇒ falta a configuração local (copiar o exemplo e
  preencher).
- Editor no PATH: `code`, `cursor` ou `subl` (nesta ordem). **Sem editor não é problema** — não entra
  em 🔴 nem em ⚠️; se houver um, cite-o no resumo ✅.

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
   `✅ Pronto: repo meu-app, branch main, 2 frentes abertas, Claude Code 2.1 · sdd-checar-ambiente v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Se estiver tudo certo, a resposta inteira é **exatamente a linha ✅** — nenhuma frase antes nem
depois: nada de "Tudo limpo", de lista do que foi verificado ou de oferta de ajuda. Ambiente saudável
não merece parágrafo; quem quer detalhe pergunta.

## Exemplos

Saudável:

```text
✅ Pronto: repo meu-app, branch main, nenhuma frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

Com o certificado A1 salvo no git de um repositório público:

```text
🔴 Dado exposto
- O certificado digital certificados/empresa.pfx está salvo no git. Este repositório é público: o arquivo já está na internet.
  git rm --cached "certificados/empresa.pfx" && echo "certificados/empresa.pfx" >> .gitignore
  Depois, revogue o certificado com a autoridade certificadora e emita outro.

✅ Repo meu-app (público no GitHub), branch main, nenhuma frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

Com dois problemas:

```text
🔴 Impede o trabalho
- O git não tem e-mail configurado — o primeiro commit vai falhar.
  git config --global user.email "voce@example.com"

⚠️ Vale arrumar
- A frente ../meu-app-frentes/relatorio-mensal já foi integrada na main e continua aberta.
  git worktree remove ../meu-app-frentes/relatorio-mensal
  git branch -d relatorio-mensal

✅ Repo meu-app, branch main, 1 frente aberta, Claude Code 2.1 · sdd-checar-ambiente v1.3.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest
```

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
