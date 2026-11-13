---
description: "Fecha uma frente de trabalho e a leva para produção com UM ponto de aprovação: verifica sozinha o que vai subir (sintaxe, testes, segredo no diff, base desatualizada), mostra uma vez o que exatamente vai para produção e se o push publica sozinho (inclusive pela Vercel ligada ao GitHub), e só depois do OK do usuário commita, integra, publica e confere. Use de dentro da pasta da frente quando o usuário disser 'release', 'publicar', 'subir para produção', 'fechar a frente' ou 'integrar'. É a outra ponta da skill sdd-new-session."
compatibility: "Requer git; para conferir o deploy, o gh (GitHub CLI) com o login que você já tem. Nenhum token é pedido."
---

# Release — fechar a frente com um OK

Na primeira resposta desta skill, comece com esta linha, uma vez só:
`sdd-release v2.12.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Verificar o que vai subir, mostrar **uma vez** o que vai para produção e — só depois do OK — integrar e
publicar.

## As duas regras que governam esta skill

1. **Não pergunte o que dá para descobrir.** Investigue e decida; pergunte só o ambíguo, com
   recomendação. No fim, liste o que assumiu ("assumi X porque Y").
2. **Simples não é sem rede de proteção.** Um passo a mais custa trinta segundos; uma publicação errada
   custa o fim de semana. O que se corta é **burocracia** (changelog elaborado, versionamento novo,
   relatório longo). **Nunca** o que impede publicar algo quebrado, e nunca o momento em que o usuário vê
   e aprova o que vai subir.

## Como falar com o aluno

Quem usa esta skill, em geral, nunca publicou nada pelo terminal. Cada resposta é uma etapa explicada,
não um relatório técnico.

**As 4 etapas, sempre com estes nomes:**

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Onde estou | Passo 0 (só lê) |
| 2 | Verificar | Passo 1 e Fase 1 (só lê; nada é publicado) |
| 3 | Sua decisão | Fase 2 — o único ponto de parada |
| 4 | Publicar | Fase 3 |

**Toda resposta tem estas partes, nesta ordem** (pule a que não tiver conteúdo):

1. **Status** — uma linha: `✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`
   (✅ concluída — não só visitada; ▶️ a de agora; ⬜ por fazer; ⏸️ parada; ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em **Agora**.
2. **O que foi feito** — em frases curtas, o resultado da etapa anterior, sem saída de comando. Registre
   a escolha do aluno: *"Você respondeu **sim**: …"*.
3. **Agora: etapa N — nome** — o que esta etapa faz e por quê, em 2 a 4 frases, como para alguém que nunca
   viu um terminal. Se for alterar algo, diga **em passos numerados** o que vai fazer e o que **não** vai
   acontecer ainda. Antes de algo demorado (testes, sintaxe, conferir o deploy), diga em uma frase o que
   vai rodar e que o aluno não precisa responder.
4. **Sua decisão** — nesta skill só existe uma: a última linha do bloco da Fase 2, com a moldura descrita
   lá (os campos foram conferidos por você; **sim** publica o que está descrito; **não** encerra sem
   publicar; no destino ambíguo do Passo 1, `develop` ou `main` também são respostas válidas e escolhem o
   destino). Resposta que não casa com as respostas previstas (uma dúvida, "acho que sim") ⇒ responda a
   dúvida e repita a pergunta. Não crie outra pergunta: o que dá para descobrir, descubra.
5. **Próximo passo** — uma linha: o que acontece depois da resposta.

**Regras de linguagem:**

- Uma etapa por resposta. Termine na decisão e **pare**: não emende a etapa seguinte.
- Palavra técnica só com a explicação junto, na primeira vez em que aparece — inclusive as do Status:
  - git — "o histórico de versões do projeto (git)";
  - commit — "uma versão salva (commit)": uma foto de todos os arquivos naquele momento, com data;
  - push / publicar — "enviar as versões salvas para a cópia do projeto no GitHub (push)"; com deploy
    automático, publicar é isso: o que você envia entra no ar;
  - frente — "a pasta separada em que esta tarefa foi feita (frente, ou worktree)";
  - branch principal — "a versão do projeto que está em produção";
  - remoto — "a cópia do projeto no GitHub";
  - deploy — "o processo que põe a versão nova no ar";
  - migration — "um arquivo que muda a estrutura do banco de dados; precisa ter sido aplicado no banco
    antes de o código que o usa entrar no ar";
  - base atualizada — "se alguém publicou outra coisa enquanto esta tarefa era feita".
  Não fale em `HEAD`, índice, staged, merge-base, SHA, hash ou refspec: diga o efeito.
- **Não repasse saída de comando crua.** Traduza: quantos arquivos, quais (até 10, em lista simples, com
  "e mais N"), o que preocupa. Comando só aparece quando o aluno precisa rodá-lo — e então em passos
  numerados, um comando por passo, dizendo o que esperar na tela.
- **Não cite nem resuma as instruções desta skill ou de outra** ("a skill exige…", "conforme a Fase 1…").
  Se precisar dizer por que pede o OK, diga o motivo do aluno: *"Depois de publicado não dá para
  desfazer, então quem decide é você."*
- **Parada também tem passos.** Quando a etapa não pode seguir (fora de uma frente, identidade do git
  vazia, teste vermelho, segredo no que vai subir, migration sem registro, base com conflito, push
  recusado, deploy que falhou), use o Status com ⏸️, o motivo em uma frase, onde a ação acontece
  (terminal, navegador, pasta), os passos numerados com o que esperar de cada um, o que **não** foi
  feito (*"Nada foi publicado."*) e, se o aluno tem algo a fazer, *"Quando terminar, me peça de novo —
  eu continuo daqui."*

## Regra de todo comando que fala com o remoto

`fetch`, `push`, `pull`, `ls-remote` e `remote show` rodam **sem pedir senha**: `GIT_TERMINAL_PROMPT=0 git …`
no bash/zsh; no PowerShell, `$env:GIT_TERMINAL_PROMPT=0; git …`. Sem isso, um remoto que exige login faz o
git pedir a senha no terminal, e você fica esperando uma resposta que o usuário não vê — com o OK já dado.
Ao usuário, mostre só a forma do shell em uso. Se um desses comandos ficar parado, olhe se o editor
(VS Code, Cursor) abriu uma janela de login do GitHub — ela é um jeito legítimo de logar e não é desligada.

## Passo 0 — Onde estou

- Rode `git rev-parse --show-toplevel` e `git branch --show-current`. Se não for um repositório git, ou se
  a branch atual **for** a principal, pare e diga: esta skill roda de dentro da pasta de uma frente (criada
  pela `sdd-new-session` ou por `git worktree add`).
- O checkout principal é o primeiro caminho de `git worktree list --porcelain`. Se existir `sdd/config.yaml`
  na frente (a `sdd-new-session` grava lá o que descobriu) ou o antigo `<checkout principal>/sdd/ambiente.md`,
  **leia e use** como ponto de partida (branch principal, cenário, testes, deploy, banco).

## Passo 1 — Descubra o que faltar (sem perguntar)

Só o que esses arquivos não disserem:

```bash
GIT_TERMINAL_PROMPT=0 git remote show origin
git log --oneline -20
git tag --list
ls .github/workflows/
```

E leia: `README.md`, `package.json` (seção `scripts`), `Makefile`, `.github/workflows/*`, `CLAUDE.md`,
`AGENTS.md`.

- **Branch principal** — a "HEAD branch" do remoto.
- **Como o código chega em produção** — a descoberta mais importante. Seja honesto:
  - **Deploy automático**: um workflow dispara em push na principal ⇒ **o push É o deploy**.
  - **Deploy automático pela Vercel** (o projeto foi ligado à Vercel pelo GitHub): **o push na principal É o
    deploy de produção**, e cada push de outra branch ou PR ganha um preview (uma cópia de teste, com endereço
    próprio). O sinal que vale é um status com nome começando por `Vercel` no último commit da principal
    (`gh api "repos/{owner}/{repo}/commits/<último commit da principal>/status" --jq '.statuses[].context'`);
    `vercel.json` ou a pasta `.vercel/` no projeto são só pista (a ligação pelo GitHub não precisa de nenhum dos
    dois). Só o status ⇒ a Vercel publica. Só o arquivo ⇒ diga que o projeto tem configuração da Vercel mas o
    GitHub não mostra deploy dela (a ligação pode estar desligada): no bloco do OK, "o push publica sozinho?"
    fica "não confirmei".
  - **Deploy manual**: há um comando de publicação (`npm run deploy`, `make deploy`, um script).
  - **Nenhum**: o repositório só guarda código ⇒ "release" = integrar na principal, sem fingir que publicou.
- **Testes** (`npm test`, `pytest`, um job de CI) e **checagem de sintaxe** para os arquivos tocados
  (`node --check`, `php -l`, `python -m py_compile`, `tsc --noEmit`).
- **Versionamento** (tags `v*`, `version` no `package.json`, `CHANGELOG.md`). Se não houver nada disso,
  não invente: projeto sem versão não ganha versão junto com a release.
- **Cenário** (o mesmo da `sdd-new-session`): commits diretos na principal ⇒ **A, Trunk-Based**
  (termina em push na principal); merges de PR ⇒ **B, GitHub Flow** (termina em PR para a principal);
  tags de versão **e** branches `release/*` ou `hotfix/*` ⇒ **C, GitFlow** (termina em PR para `develop`) —
  o mesmo critério da `sdd-new-session`. Na dúvida entre A e B, A. Se existir `develop` no remoto mas o
  critério de C não fechar, **não decida sozinha**: a última linha do bloco do OK vira
  "**Posso publicar na `<recomendada>`?** (responda `develop` ou `main` para trocar)" — continua sendo
  uma pergunta só. **O destino respondido vira o `<alvo>` da Fase 3**: `develop` ⇒ a frente segue o
  caminho do cenário C (push da branch + PR para `develop`), nunca o push direto na principal.
- **Branch de integração** — onde esta frente entra: a principal nos cenários A e B, `develop` no C. Daqui
  em diante, `<alvo>` é ela. Comparar ou integrar uma frente do cenário C contra a principal levaria para
  produção o que ainda está em desenvolvimento.

Não grave arquivo de ambiente: o que você descobriu vale para esta release. A chave `banco` de um
`sdd/ambiente.md` antigo (gravada pela `sdd-build` ao aplicar a migration) continua sendo lida.

## Fase 1 — Verificar (sozinha, sem perguntar)

Tudo aqui é local e reversível. Nesta ordem, **parando na primeira falha**:

0. **Identidade do git.** `git config user.name` e `git config user.email` — os dois preenchidos. Faltou
   algum? Pare aqui, com os comandos `git config --global user.name "Seu Nome"` e
   `git config --global user.email "voce@example.com"`: o commit da Fase 3 falharia **depois** do OK, e o
   usuário teria aprovado algo que não sobe.
1. **O que exatamente vai subir** — inclusive o que ainda não foi commitado:
   - `git status --short --untracked-files=all` — arquivos modificados e **novos** (`??`, um por arquivo,
     nunca a pasta inteira agrupada) em relação ao último commit. **Esta
     é a lista do commit** da Fase 3, inclusive um arquivo que foi commitado e depois desfeito na pasta
     (ele some do resumo abaixo, mas precisa entrar no commit para o desfazer valer).
   - `git diff --stat $(git merge-base origin/<alvo> HEAD)` — compara a base da frente com a
     **pasta de trabalho**: cobre os commits da frente **e** as mudanças ainda não commitadas.
   - Não use só `git diff origin/<principal>...HEAD`: ele ignora o que não foi commitado, e numa frente
     sem commit mostraria um resumo vazio — o usuário aprovaria algo diferente do que sobe.
   - Arquivo que não pertence a esta frente? **Pare e mostre** — não decida sozinha o que fica de fora.
     Exceção que não é da frente e nunca entra no commit: pastas de skills não versionadas
     (`.claude/skills/…`, `.agents/skills/…`) — a `sdd-new-session` as copia para a frente funcionar.
   - Algo **staged** com versão diferente da pasta (o mesmo arquivo em `git diff --cached --name-only` e
     em `git diff --name-only`)? **Pare e mostre**: qual das duas versões sobe é decisão do usuário, e
     nenhuma das duas pode ser descartada sem ele ver.
   - **Impressão digital do que vai subir** — guarde `git rev-parse HEAD` (fixa o histórico que o push
     vai enviar), o resultado de `git diff <base> | shasum`, o de `git diff --cached | shasum` (o que já
     está staged) e o `shasum` de cada arquivo novo (`??`) — no PowerShell, `Get-FileHash` —, onde
     `<base>` é `$(git merge-base origin/<alvo> HEAD)`. É o que o OK aprova; a Fase 3 confere antes de
     commitar. Um commit reescrito depois do OK muda o `HEAD` mesmo que o conteúdo final seja igual.
2. **Migration e banco andam juntos.** Se o que vai subir (o diff e os arquivos novos do item 1) tem
   `*.sql` ou algo em `migrations/`, a migration precisa constar **aplicada**: a seção `## Migrations
   aplicadas` do BUILD_REPORT da frente, com aquele arquivo (ou "já aplicada em <data>") e o projeto do banco.
   Falta? **Pare aqui, antes do bloco do OK**, dizendo o que falta e o caminho: a migration se aplica pelo passo
   "Aplicar a migration" da `sdd-build` (descobre o projeto, confirma nome e ref, aplica, prova por leitura e
   grava o registro). O inverso também para: migration registrada
   como aplicada **sem** o `.sql` no que sobe (o arquivo ficou de fora do commit) ⇒ `git add` do arquivo e
   rode a `sdd-release` de novo. Publicar código que chama uma coluna que o banco não tem, ou um banco que
   mudou sem o arquivo no repositório, são os dois jeitos de git e banco divergirem.
3. **Sintaxe** dos arquivos tocados, com a ferramenta do Passo 1.
4. **Testes**, se existirem. Vermelho **para tudo**: aprovar um diff com teste quebrado transforma o OK em
   carimbo.
5. **Segredo vazando** — em tudo o que vai subir, não no repositório inteiro: o diff dos arquivos
   modificados **e o conteúdo inteiro de cada arquivo novo** (`??` do `git status`), que não aparece no
   `git diff` mas será commitado. Procure chave de API, token, senha, `.env` sendo versionado por engano:
   atribuições como `API_KEY=`, `SECRET=`, `PASSWORD=`, `TOKEN=` com valor literal, prefixos de chave de
   provedor e blocos `PRIVATE KEY`. **E também no histórico da frente** (`git log -p <base>..HEAD`): uma
   chave que entrou num commit e saiu no seguinte some do diff agregado, mas o push envia os dois
   commits. Achou no histórico? Pare: reescrever histórico é decisão do usuário, nunca desta skill.
   Uma chave publicada não se despublica, nem apagando o commit depois.
6. **A base andou?** `GIT_TERMINAL_PROMPT=0 git fetch origin <alvo>` e `git rev-list --count HEAD..origin/<alvo>`. **Não
   integre agora**: um `git merge` aqui criaria commit antes do OK (e recusaria a pasta com mudanças não
   commitadas). Só registre: "a base andou N commits" vai no bloco do OK, e a Fase 3 integra a base
   atualizada e **roda os testes de novo antes de qualquer push**.

Se qualquer item falhar: **pare, diga qual falhou, com arquivo e motivo, e não siga.** Não conserte sozinha
e não peça OK "mesmo assim". Nessa resposta **não mencione o bloco do OK nem a pergunta "Posso publicar"**,
nem como passo futuro: termine com o que precisa ser corrigido e "depois, rode a `sdd-release` de novo".
Quem lê a pergunta no fim da resposta entende que o OK está sendo pedido.

## Fase 2 — O único ponto de parada

Antes do bloco, o **Agora** da resposta diz, em duas frases, como se responde: *"Os campos abaixo já
foram conferidos por mim; você só responde à última linha. **sim** publica exatamente o que está
descrito; **não** encerra sem publicar — nada sai daqui."* Depois, mostre **um bloco só, neste formato**
(preencha; não acrescente perguntas):

```markdown
**O que sobe**
<quantos arquivos mudam e quais, pelo nome, em palavras — traduzido do resumo comparativo da Fase 1 (o
--stat contra a base, que inclui o que já foi commitado na frente), mais os arquivos novos marcados como
novos; até 10 nomes, "e mais N"; nunca a saída do --stat colada. O git status da Fase 1 é a lista do que
ainda precisa entrar no commit, não o que sobe>

**O que muda em produção:** <uma frase, em português — "muda o cálculo do relatório mensal da tela
inicial", não "altera handler.js">

**O push publica sozinho?** <sim, o workflow X publica ao receber o push na main | sim, a Vercel publica
ao receber o push na main (num PR, só o preview) | não confirmei: <o que viu> | não: <por quê>>

**O deploy espera os testes?** <sim — os testes rodam no mesmo job, antes da publicação (ou: o job de
publicação tem `needs:` no de testes) | não — o workflow X publica sem esperar os testes do Y: um teste
vermelho não impede a publicação | não — a Vercel publica sem esperar os testes do GitHub: quem os rodou foi
esta verificação, antes do OK | não se aplica: o push não publica>

**Banco:** <migration `<arquivo>` aplicada em `<projeto nome (ref)>` em <data> | sem migração nesta frente>

**Verificações:** sintaxe <ok|pulada: motivo> · testes <ok|pulados: motivo> · segredo <nenhum, no
diff e nos arquivos novos> · base <atualizada | andou N commits: será integrada e testada de novo antes do push>

<só se não houver revisor humano:> Antes de responder, vale pedir à IA uma revisão do próprio código:
"isso quebra algo que já funcionava, expõe alguma senha, tem erro óbvio?"

**Posso publicar?**   ← ou "Posso publicar na <alvo>?", no único caso do destino ambíguo (Passo 1)
```

- Verificação ausente dita como ausente é informação; em silêncio, é falsa segurança.
- **"Banco:"** vem do registro conferido no item 2 da Fase 1 (`## Migrations aplicadas` do BUILD_REPORT) —
  é afirmação, não pergunta. Frente sem `.sql` escreve "sem
  migração nesta frente".
- **"O deploy espera os testes?"** se descobre lendo `.github/workflows/*`: os testes estão no mesmo job,
  antes do passo que publica, ou o job que publica tem `needs:` apontando para o de testes? Um step de
  teste com `continue-on-error: true`, `|| true` ou que termina sempre em `exit 0` **não** segura nada —
  conta como "não". É afirmação, não pergunta: você preenche, o usuário não responde.
- **A única pergunta do bloco é a última linha, "Posso publicar?"** (ou "Posso publicar na `<alvo>`?", se o
  destino ficou ambíguo no Passo 1). As linhas com `?` antes dela são rótulos que você preenche — "uma
  pergunta" conta pedidos de resposta, não sinais de interrogação. A sugestão de revisão
  é uma frase, não uma pergunta — transformá-la em "quer que eu revise antes?" cria um segundo ponto
  de parada, e duas paradas viram carimbo.
- Se algo ficou ambíguo (qual arquivo pertence à frente), diga **dentro deste mesmo bloco**, antes da
  última linha — nunca pare duas vezes.
- **Sem o OK, termine aqui**: nada de commit, merge ou push.

## Fase 3 — Publicar (só depois do OK)

1. **A pasta ainda é a que foi aprovada?** Recalcule a impressão digital da Fase 1. Diferente ⇒ algo mudou
   depois do OK: **pare**, mostre o que mudou e peça um OK novo — nunca commite o que não foi visto.
2. **Commit com os arquivos nomeados** um a um — exatamente os da lista do `git status` da Fase 1,
   nenhum outro. **Não resete o índice** (apagaria versão staged que não está na pasta). Depois do
   `git add`, `git diff --cached --name-only` tem de ser exatamente essa lista — se aparecer outro
   arquivo staged, pare antes do commit. Depois do commit, `git status --short` vazio — exceto as pastas
   de skills não versionadas, que ficam de fora de propósito.
   Nunca `git add -A`, nunca `git add -u`: com duas frentes abertas na mesma máquina, eles arrastam o
   trabalho da outra.
3. **Base atualizada, testada de novo.** Se a base andou: `GIT_TERMINAL_PROMPT=0 git fetch origin <alvo>`,
   `git merge origin/<alvo>` **na frente**, e rode os testes de novo. Conflito ou teste vermelho: **pare
   antes de qualquer push**, diga o que quebrou — nada foi publicado.
4. **Integrar pelo cenário, sempre a partir da frente:**
   - A (Trunk-Based, `<alvo>` = principal): `GIT_TERMINAL_PROMPT=0 git push origin HEAD:<principal>`. O push sai **da frente**, que contém exatamente
     o que foi aprovado mais a base remota — nunca do checkout principal, onde um commit local que ninguém
     aprovou iria junto. Recusado porque a base andou (`non-fast-forward`/`fetch first`)? Volte ao
     item 3 (nunca force). Recusado por permissão (`403`, `Permission denied`, `could not read Username`)
     ou por branch protegida (`protected branch`, `GH006`)? Pare e diga o que conferir, nesta ordem:
     `gh auth status` (está logado, e com a conta certa?); o seu papel no repositório (publicar exige
     permissão de escrita); e se a principal é protegida — aí o caminho é o do cenário B (push da branch +
     PR), não insistir no push direto.
   - B (GitHub Flow): `GIT_TERMINAL_PROMPT=0 git push -u origin <branch-da-frente>` e abra o PR para a
     principal (`gh pr create`, se houver `gh`; sem ele, o próprio push acima imprime o link para abrir o
     PR no navegador) — **e pare aí**. A integração é o merge do PR, depois da revisão.
   - C (GitFlow): `GIT_TERMINAL_PROMPT=0 git push -u origin <branch-da-frente>` e abra o PR para `develop`
     (mesmo caminho do B, com ou sem `gh`) — **e pare aí**. A frente não vai direto para a principal.
5. **Deploy manual, se houver, só a partir da principal já integrada e atualizada** — nunca da branch da
   frente não publicada. O deploy roda numa árvore **idêntica ao que foi publicado**: no cenário A, a
   própria frente logo depois do push aceito — confira `git status --porcelain` vazio e
   `git rev-parse HEAD` igual a `git rev-parse origin/<principal>` (após `GIT_TERMINAL_PROMPT=0 git fetch`); se não bater,
   pare. Nunca do checkout principal, que pode ter mudança local ou commit que ninguém aprovou. Nos
   cenários B e C, entregue o comando de deploy para rodar **depois que o PR for integrado**; não o
   execute antes. (Com deploy automático, o próprio push na principal já publica.)
6. **Confirme que funcionou — pelo commit que você publicou, não pelo último run.** Não diga "publicado"
   porque o comando não deu erro. Com deploy por workflow e `gh` disponível:
   - `gh run list --commit <SHA publicado> --branch <principal> --json databaseId,status,conclusion,workflowName,event`
     (igual no PowerShell). Olhe o run **do workflow que publica**, na principal (`event` = `push`, ou
     `workflow_dispatch` quando foi o redisparo manual do item abaixo) — não o mais recente da lista geral (com dois pushes seguidos, é de outro commit) nem um run do mesmo SHA em
     outra branch ou de PR, que pode ter pulado o deploy.
   - `completed` + `success` ⇒ "No ar: o deploy do seu commit `<sha curto>` terminou (run N)".
   - `queued` ou `in_progress` ⇒ espere e olhe de novo; ainda não está no ar.
   - Lista vazia ⇒ o GitHub ainda não registrou o run: espere alguns segundos e consulte de novo; vazia depois
     de ~2 min ⇒ diga que não achou o run do commit — nunca "nada a verificar". Nos cenários B e C, o SHA que
     chega à principal é o do merge do PR: consulte por ele.
   - `cancelled` ⇒ com fila, um push mais novo pode ter substituído o seu. `GIT_TERMINAL_PROMPT=0 git fetch
     origin <principal>`, depois
     `gh run list --workflow <arquivo do workflow> --branch <principal> --limit 20 --json databaseId,headSha,status,conclusion,createdAt`.
     Só vale um run `success` criado depois do seu **e** de um commit que contém o seu
     (`git merge-base --is-ancestor <seu SHA> <SHA dele>` sai 0) ⇒ "Seu commit `<sha>` foi incluído no
     deploy de `<sha dele>` (run N)". Sai 1 = aquele run **não** contém o seu commit (procure outro ou espere);
     qualquer outro código (commit não encontrado) = "não consegui confirmar" — nunca "não foi incluído".
   - `failure` ⇒ diga o que falhou. Para repetir o deploy, **nunca `gh run rerun` de um run antigo**: com
     fila, ele roda depois do push mais novo e copia código velho por cima. Redispare na ponta
     (`gh workflow run <arquivo> --ref <principal>`, se o workflow aceita disparo manual) ou com um push novo.
   - Verde não prova teste: se o step de teste tem `continue-on-error`, `|| true` ou termina sempre em
     `exit 0`, diga "o deploy terminou, mas o workflow não roda testes antes de publicar" — sem ✅.
   **Com a Vercel**, o deploy não é um workflow: ele aparece no GitHub como um status do commit e como um
   deployment (o que esta skill sabe disso vem da documentação da Vercel, vercel.com/docs/git/vercel-for-github;
   se o seu GitHub mostrar outra coisa, diga o que viu). Pelo SHA publicado:
   - `gh api "repos/{owner}/{repo}/commits/<SHA publicado>/status" --jq '.statuses[] | select(.context | startswith("Vercel")) | [.state, .target_url] | @tsv'`
   - `success` ⇒ pegue o endereço: `gh api "repos/{owner}/{repo}/deployments?sha=<SHA publicado>" --jq '.[0].id'`
     e `gh api "repos/{owner}/{repo}/deployments/<id>/statuses" --jq '.[0].environment_url'` ⇒ "No ar: o deploy
     do seu commit `<sha curto>` terminou na Vercel — <endereço>". Esse é o endereço **deste deploy**; o domínio
     do site, se o projeto tiver um, passa a mostrar a mesma versão. Abra o endereço (ou peça ao aluno para
     abrir) e diga se a página respondeu.
   - `pending` ⇒ ainda publicando: consulte de novo a cada ~30 s, até 10 min; passou disso, diga que continua
     publicando e dê o link do status (o `target_url`) — sem dizer "no ar".
   - `failure` ou `error` ⇒ diga que o deploy da Vercel falhou e dê o link do status, onde está o erro. **Não
     refaça o deploy por conta própria**: corrigir e publicar de novo é uma frente nova.
   - Nenhum status da Vercel depois de ~2 min ⇒ diga que não achou o deploy da Vercel para este commit (a
     ligação pode estar desligada, ou a Vercel decidiu não construir) — nunca "no ar".
   - Nos cenários B e C, o PR ganha um preview: `gh pr checks <número do PR>` mostra o check da Vercel, e o
     endereço do preview está no comentário da Vercel no PR (`gh pr view <número do PR> --comments`). Produção
     só muda depois do merge: confira então pelo SHA do merge, como acima.
   Há URL? Veja se responde. Sem `gh` ou sem como confirmar? Diga isso: "publicado, sem verificação
   automática disponível" é honesto; "✅ tudo certo" sem ter olhado, não é.
7. **Checkout principal e limpeza**, entregues como comandos (de dentro da worktree ela não consegue se
   remover): no checkout principal, `GIT_TERMINAL_PROMPT=0 git pull --ff-only` — se recusar, a principal local tem commits que
   não foram publicados, e isso é dito, não resolvido por você; depois `git worktree remove "<pasta>"` (com aspas: o caminho pode ter espaço) e
   `git branch -d <branch>` (o `-d` minúsculo só apaga o que já foi integrado). Nos cenários B e C, a
   limpeza vem depois do merge do PR.

Resposta final: o Status todo ✅ e três linhas — o que subiu, onde está, o que falta.

## O que NÃO entra nesta skill (e por quê)

- **Changelog elaborado** — se o projeto já tem `CHANGELOG.md`, uma linha. Se não tem, não crie.
- **Versionamento novo** — projeto que não versiona hoje não começa a versionar aqui.
- **Relatório final longo** — três linhas.
- **Nunca `--force`**, em nenhuma hipótese. Push recusado significa que a base andou: busque e integre,
  nunca force por cima do trabalho de outra pessoa (ou do seu de ontem).
- **Nunca um segundo ponto de parada** — duas paradas viram carimbo: a pessoa para de ler.

## Por que cada regra existe

- **O OK vem antes do push**: com deploy automático, depois do push não há "antes" para onde voltar.
- **O `git add` nomeia arquivos**: com duas frentes abertas, o `-A` publica a que nem terminou.
- **A base é conferida antes e integrada depois do OK**: se outra frente entrou primeiro, os testes
  passaram contra um estado que já não existe — mas integrar antes do OK criaria um commit que ninguém
  aprovou. Por isso: medir na Fase 1, integrar e testar de novo na Fase 3, antes do push.
- **O push sai da frente, não do checkout principal**: lá pode haver commit local que não passou pelo OK.
- **O resumo cobre o não commitado**: o commit acontece depois do OK, então o que se aprova tem de incluir
  o que ainda está só na pasta.
- **A identidade é conferida antes do OK**: o commit só acontece na Fase 3; sem nome e e-mail ele falha
  depois que o usuário já aprovou.
- **Migration no commit e migration aplicada andam juntas**: o push publica o código, não o banco. Sem a
  conferência, um deploy automático põe no ar código que chama uma coluna que não existe — e o bloco do OK
  teria dito "o push publica sozinho? sim" como se isso bastasse.
- **A Vercel é conferida pelo status do commit, não por um workflow**: ela publica sem passar pelo GitHub
  Actions; procurar um workflow que não existe faria a skill dizer "não achei o deploy" de algo que está no ar.
- **Nenhum token, nunca**: o `gh` usa o login que já existe; pedir ou colar token no chat é o jeito mais comum de
  uma chave vazar.
- **O deploy é conferido pelo SHA**: com dois pushes seguidos, o "último run" é de outro commit, e um
  run verde de outro commit não diz nada sobre o seu.
- **Nunca `gh run rerun` de deploy antigo**: o rerun usa o commit daquele run — com fila, ele roda depois
  do push mais novo e publica código velho por cima.
- **A skill roda de dentro da frente** e não consegue remover a própria worktree no fim — a limpeza é do
  checkout principal.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
