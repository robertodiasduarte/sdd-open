---
name: sdd-new-session
description: >-
  Abre uma frente de trabalho isolada do SDD Open: confere antes, pelo checar.sh da sdd-checar-ambiente
  (ou à mão, sem bash), se a pasta, o git, o repositório, o remoto e o acesso a ele estão no lugar (sem
  pedir senha e sem criar nada se algo faltar), cria uma git worktree fora da pasta do projeto com uma
  branch nova nascida da branch padrão ATUALIZADA do remoto, grava no sdd/config.yaml da frente os slots
  vazios que descobriu com evidência, e abre no editor. Use quando o usuário disser /sdd-new-session,
  "abrir uma frente", "nova sessão", "nova tarefa isolada" ou quiser começar uma feature/correção sem
  misturar com outra em andamento.
compatibility: Requer git >= 2.20 e um agente com acesso ao terminal (bash, zsh ou PowerShell). Branch padrão, editor, pasta das frentes, testes e checagem de sintaxe vêm de sdd/config.yaml; slot vazio é descoberto e gravado no config da frente, com a evidência.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "1.2.0"
  updated: "2026-10"
  fase: "0"
---

# sdd-new-session — abrir uma frente

Na primeira resposta desta skill, comece com esta linha, uma vez só:
`sdd-new-session v1.2.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Um comando, uma tarefa, um diretório: `git worktree` + branch nova nascida do estado **remoto atual**
da branch padrão. A outra ponta é a `sdd-release`.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Pré-voo | Passo 0 |
| 2 | Conhecer o repositório | Passo 1 (só na 1ª vez) |
| 3 | Criar a frente | Passo 2 |
| 4 | Abrir no editor | Passo 3 |

A tradução de cada achado do pré-voo está em "Como traduzir cada achado": ela vale como o "O que foi
feito" e a parada desta skill.

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Nova sessão: ✅ 1 Pré-voo · ▶️ 2 Conhecer o repositório · ⬜ 3 Criar a frente · ⬜ 4 Abrir no editor`
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

## Slots do config (`sdd/config.yaml`)

`project.default_branch` · `editor` · `worktree_base` · `project.test_cmd` · `project.lint_cmd`.
**Slot vazio = descobrir** (Passo 1). Com evidência (de onde o valor veio), ele é gravado no `sdd/config.yaml da
frente` (Passo 2, item 6) e declarado na resposta; sem evidência, fica vazio e a resposta diz isso.
Nunca adivinhe e nunca sobrescreva slot cheio: só slot vazio é gravado.

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
- **O git existe**: siga para o pré-voo. Ele também responde quando a pasta **não** é um repositório, e
  diz qual é o caso.

### Pré-voo pelo script (caminho principal)

Com bash, e com a skill `sdd-checar-ambiente` na mesma pasta de skills desta (`.agents/skills/`,
`.claude/skills/` ou `.cursor/skills/`), rode de dentro da pasta do projeto:

```bash
bash <pasta das skills>/sdd-checar-ambiente/scripts/checar.sh --frente
```

**Leia a saída; não a repasse ao usuário.** Pelo código de saída:

- **exit 1** (bloco `🔴 Impede o trabalho`) ⇒ **pare**. Para cada achado, responda pela tabela **Como
  traduzir cada achado** abaixo (a linha cujo trecho aparece na mensagem) e termine com *"Nada foi criado.
  Depois de resolver, peça a frente de novo."*
- **exit 0** com a linha `✅ Pronto para abrir a frente: repo <r>, principal <b>` ⇒ siga para o Passo 1;
  o `<b>` é a branch principal do remoto.
- **Qualquer outra coisa** — o script não existe, não há bash (PowerShell puro), ou saiu 0 **sem** essa
  linha (versão antiga, que não conhece o `--frente`) ⇒ faça o **Pré-voo à mão** abaixo.

### Pré-voo à mão (sem bash ou sem o script)

Se `git rev-parse --show-toplevel` falha, a pasta não é um repositório: **pare** — provavelmente o terminal
foi aberto na pasta errada (`cd <pasta do projeto>`), ou o projeto ainda não tem git (a skill
`sdd-iniciar-repo` põe o projeto no git e num GitHub privado).

Depois, o remoto, nesta ordem, parando na primeira que falhar:

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

### Como traduzir cada achado

O usuário recebe "Diga" e os passos — nunca o relatório do script nem a linha de erro do git. A 1ª coluna
é um trecho literal da mensagem do `checar.sh --frente`: a linha certa é a cujo trecho aparece no achado.

| Achado (trecho da mensagem) | Diga | Passos (um comando por passo, com o que esperar) |
|---|---|---|
| `Esta pasta está dentro do` | Esta pasta é sincronizada pela nuvem (o provedor vem na mensagem), e aqui o histórico do projeto se corrompe. | 1. Mover a pasta do projeto para fora da nuvem (ex.: `~/Projetos`) pelo Finder ou Explorador de Arquivos. 2. Abrir o terminal e o agente na pasta nova. |
| `O terminal está na sua pasta pessoal` | O terminal está aberto na sua pasta pessoal, não na pasta de um projeto. | 1. Abrir o agente de novo dentro da pasta do projeto. |
| `o terminal foi aberto uma pasta acima dele` | O projeto está na subpasta que a mensagem cita, um nível abaixo de onde o terminal foi aberto. | 1. Abrir o agente de novo dentro dessa subpasta. |
| `Há repositórios git nas subpastas` | Há mais de um projeto aqui dentro; preciso saber qual é o seu. | Pergunte, com uma opção por subpasta citada: **"Qual destas pastas é o seu projeto?"** — e diga como abrir o agente lá dentro. |
| `pastas com git aqui dentro` | Há várias pastas com projeto aqui dentro; preciso saber qual é a sua. | Pergunte: **"Qual é a pasta do seu projeto? Responda com o nome dela."** |
| `Ainda não há projeto nesta pasta` | Esta pasta está vazia: ainda não há projeto para abrir uma frente. | 1. Começar pela skill `sdd-brainstorm`; o git entra quando houver o que guardar. |
| `Este projeto ainda não usa git` | Este projeto ainda não usa git — e a frente nasce do git. | Ofereça a skill `sdd-iniciar-repo` (vem com o sdd-open): **"Posso pôr este projeto no git e num GitHub privado, conferindo antes o que não pode ir?"** — sim: siga a `sdd-iniciar-repo`; não: pare. |
| `O git não está instalado` | O git não está instalado neste computador. | 1. Instalar por https://git-scm.com/downloads. 2. Fechar e abrir o terminal. |
| `O repositório não tem remoto` | Este projeto ainda não tem uma cópia no GitHub — e a frente nasce dela. | Projeto ainda sem GitHub: a mesma oferta da `sdd-iniciar-repo` (ela retoma de onde o projeto parou). Repositório já existe no GitHub: 1. `git remote add origin <endereço>` (não mostra nada). |
| `nenhum chamado origin` | O projeto tem uma cópia remota com outro nome; a frente precisa que ela se chame origin. | 1. `git remote rename <nome> origin` (não mostra nada). |
| `ainda não tem nenhum commit` | A cópia no GitHub ainda está vazia; a frente nasce da primeira versão salva. | Já há versão salva neste computador: 1. `GIT_TERMINAL_PROMPT=0 git push -u origin <branch atual>` (mostra o envio). Sem nenhuma: 1. `git add <arquivos, pelo nome>`. 2. `git commit -m "primeira versão"`. 3. o mesmo envio. |
| `ainda não confirmou a identidade de` | Este computador nunca confirmou a identidade do servidor; não é problema de senha. | 1. `ssh -T git@<host>` (mostra a impressão digital e pergunta se confia). 2. No GitHub, conferir a impressão digital em https://docs.github.com/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints antes de responder `yes`. |
| `não deixou este computador ler` | O GitHub não deixou este computador ler o repositório: ou o endereço está errado, ou ele é privado e este computador não está logado. | 1. `gh auth login` (abre o navegador; entre com a conta do GitHub e volte). 2. Pedir a frente de novo. |
| `recusou o acesso deste computador` | O remoto (fora do GitHub) recusou o acesso deste computador — login ou permissão. | 1. Fazer o login daquele serviço (token ou chave SSH cadastrada nele); nunca `gh auth login`. |
| `Não consegui falar com` | Não consegui falar com o remoto agora: sem internet ou rede bloqueada — não é senha. | 1. Quando a conexão voltar, pedir a frente de novo. |
| `A janela de login do editor está esperando` | O seu editor abriu uma janela de login que está esperando a sua resposta. | 1. Responder a janela (ou `gh auth login`, para não depender dela). |
| `Não consegui ler o remoto:` | Não consegui ler a cópia do projeto por um motivo que não reconheço. | 1. `git remote -v` — conferir se o endereço do origin é o do seu repositório. 2. Pedir a frente de novo. |
| Qualquer outro achado | Não consegui conferir o projeto por um motivo que não reconheço. | 1. Pedir a frente de novo; se repetir, rodar a skill `sdd-checar-ambiente` para o diagnóstico completo. |

Qualquer parada do Passo 0 termina com *"Nada foi criado. Depois de resolver, peça a frente de novo."*
Pré-voo saudável não vira relatório: uma linha (`✅ Pronto para abrir a frente: repo <r>, principal <b>`) e
siga.

⛔ Não invente uma frente assumindo como o projeto é. Uma frente criada a partir de suposição falha na
primeira vez que for usada, e o usuário não vai saber por quê.

## Passo 1 — Descubra os slots (não pergunte o que dá para descobrir)

Leia o `sdd/config.yaml` do checkout principal. Para cada slot, guarde o valor e, se veio de descoberta,
a evidência — ela vai para o Passo 2, item 6.

- **Branch padrão** — a "HEAD branch" de `GIT_TERMINAL_PROMPT=0 git remote show origin` (ou o `principal`
  da linha ✅ do pré-voo). Não é "a branch em que estou agora".
  - `project.default_branch` vazio ⇒ use a do remoto (evidência: `git remote show origin`).
  - Cheio e igual à do remoto ⇒ siga.
  - Cheio e **diverge** da do remoto (o exemplo do config vem com `main`; o remoto pode ser `master`) ⇒
    **pare e pergunte** qual vale, com as duas opções e o efeito de cada uma. Nada foi criado; slot cheio
    nunca é sobrescrito. A resposta vale para esta frente (é dela que a frente nasce); o slot só muda se o
    usuário pedir, e aí no config da frente, com a evidência.
- **Pasta das frentes** — `worktree_base`; vazio ⇒ `../<nome-do-repo>-frentes` (evidência: "padrão do
  sdd-open"). Fora do repositório: dentro dele, a worktree apareceria como arquivo não rastreado em todas as
  outras frentes.
- **Editor** — `editor`; vazio ⇒ o primeiro que existir de `code`, `cursor`, `subl` (`command -v <nome>`
  no bash/zsh, `Get-Command <nome>` no PowerShell; evidência: "`command -v code` neste computador"). O config
  é compartilhado: diga na resposta que é a preferência deste computador e que qualquer um corrige a linha.
- **Testes e checagem de sintaxe** — `project.test_cmd` e `project.lint_cmd`, só com **evidência literal**,
  nesta ordem (a primeira fonte que tiver o comando vence):
  1. o comando que um workflow de `.github/workflows/` roda num step de teste (ou de lint), copiado do
     `run:` como está;
  2. `scripts.test` do `package.json` ⇒ `npm test` — exceto o placeholder do npm
     (`echo "Error: no test specified" && exit 1`); `scripts.lint` ⇒ `npm run lint`;
  3. alvo `test:` (ou `lint:`) do `Makefile` ⇒ `make test` (`make lint`).

  Duas fontes diferentes no mesmo nível (dois workflows com comandos diferentes, por exemplo) ou nenhuma
  ⇒ o slot fica vazio e a resposta diz por quê. O `test_cmd` alimenta os gates `kind: test`: um chute
  roda a coisa errada.
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
6. **Grave os slots descobertos no `sdd/config.yaml da frente`** (`<pasta das frentes>/<slug>/sdd/config.yaml`),
   nunca no do checkout principal: lá o arquivo ficaria modificado, a frente não o veria, e o `git pull`
   depois da integração abortaria. Regras:
   - só slot vazio (`""` ou sem valor) recebe valor; slot cheio fica como está;
   - na linha de cima do slot, a evidência: `# descoberto por sdd-new-session (AAAA-MM-DD): <evidência>`;
   - mesma chave, mesma indentação; nada mais do arquivo muda; **não commite** — o valor vai para a branch
     padrão junto com a feature.

   ```yaml
   project:
     # descoberto por sdd-new-session (2026-10-29): .github/workflows/ci.yml, step "Unit tests"
     test_cmd: "python3 -m unittest discover -s tests"
   ```

   A frente não tem `sdd/config.yaml` (o `sdd/` não está versionado na branch padrão) ⇒ **não grave**;
   diga os valores descobertos e que, para as frentes herdarem, o `sdd/config.yaml` precisa ser commitado
   na branch padrão.

**O que esta skill NÃO faz:** não commita, não faz push, não apaga, não integra. Só cria. Fechar a frente
é da `sdd-release`.

## Passo 3 — Responda

1. **Caminho** da pasta e **nome da branch**.
2. **Como encerrar**: a `sdd-release` de dentro da pasta nova; à mão, depois de integrar,
   `git worktree remove "<pasta>"` e `git branch -d <slug>`.
3. **Slots gravados** no `sdd/config.yaml` da frente, cada um com o valor e a evidência; slots que ficaram
   vazios e por quê. Avise que eles chegam à branch padrão junto com a feature.
4. **Última linha, destacada:** `⚠️ Continue na janela nova. Esta sessão do agente continua presa à pasta
   onde foi aberta — nenhum cd muda isso.`

## Por que cada regra existe

- **O pré-voo vem antes de qualquer criação** — sem remoto, com o remoto vazio ou sem login, o
  `git worktree add … origin/<padrão>` falha no meio; parar antes, dizendo a causa e que nada foi criado, é
  o que permite simplesmente pedir de novo.
- **O pré-voo é um script, com tradução numa tabela** — o script decide o caso do mesmo jeito sempre; a
  tabela diz ao usuário o que fazer sem colar saída crua. Um teste do sdd-open confere que toda mensagem do
  script tem linha na tabela. Sem bash, o caminho à mão continua valendo.
- **Git ausente não é "você está no app de chat"** — o diagnóstico errado manda instalar o agente que já
  está instalado.
- **Nenhum comando de rede pede senha** — o pedido de senha aparece no terminal do agente, não na tela do
  usuário; o agente trava sem que ninguém veja.
- **A branch nasce de `origin/<padrão>` atualizada** — nascer da branch atual herda trabalho pela metade
  de outra tarefa.
- **Branch padrão que diverge do remoto para tudo** — o `fetch` de `origin/<padrão>` falharia no meio da
  criação, ou a frente nasceria da branch errada.
- **Slot só com evidência literal, e só o vazio** — um comando de teste chutado faz o Verify Gate rodar a
  coisa errada; sobrescrever um slot cheio apaga uma decisão do usuário.
- **Grava na frente, não no checkout principal** — o principal ficaria com o config modificado, a frente
  não veria o valor, e o `git pull` depois da integração abortaria.
- **A sessão do agente não migra** — abrir a pasta nova abre outra janela; sem o aviso final, a frente
  inteira acaba sendo feita no lugar errado.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-new-session`.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
