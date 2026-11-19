# Como falar com o aluno — sdd-configurar-revisores

Quem chega aqui, em geral, ouviu de uma fase que "faltam os revisores" e não sabe o que é isso. A primeira resposta
dá o sentido antes de qualquer termo, diz quanto tempo leva e se custa. Cada resposta abre com o que já foi feito; a
volta depois da parada começa pelo que o diagnóstico mediu, nunca repete o caminho inteiro. Este arquivo dá as
palavras e os exemplos inteiros.

## Glossário (explique na primeira vez em que o termo aparecer)

- revisão adversarial — "uma outra IA lê o que foi construído e aponta problemas, e uma terceira confere essa
  leitura";
- engine — "o modelo de IA que faz a revisão, com o programa ou o serviço que o roda (claude, codex, gemini, ou um
  modelo do OpenRouter)";
- revisor — "a engine que lê a mudança e aponta problemas";
- auditor — "outra engine, que confere cada problema apontado; precisa ser diferente do revisor";
- OpenRouter — "um serviço pago por uso que dá acesso a vários modelos de IA com uma conta só";
- chave de API — "uma senha comprida que o OpenRouter cria para este computador usar a sua conta";
- variável de ambiente — "um valor que o terminal entrega a todo programa aberto nele; a chave mora numa delas";
- perfil do terminal — "o arquivo que o terminal lê toda vez que abre (`~/.zshrc` no Mac, `~/.bashrc` no Linux)";
- token — "um pedaço de palavra; o OpenRouter cobra por milhão deles, lidos e escritos";
- crédito — "o saldo em dólar que você põe no OpenRouter e que a revisão gasta";
- limite de gasto — "o teto que você põe na chave: passou dele, a chave para de funcionar";
- git config — "as preferências deste computador para este projeto; nunca vão para o GitHub".

Nunca diga o id do estado (R04, R13) nem o nome dele: diga a frase que o script imprimiu.

## Status desta skill, preenchido

`Revisores: ✅ 1 Conferir · ▶️ 2 Escolher · ⬜ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`

No caminho das CLIs que o aluno já tem, a etapa 3 é pulada: `Revisores: ✅ 1 Conferir · ✅ 2 Escolher · ➖ 3 Chave · ▶️ 4 Gravar · ⬜ 5 Provar`.

## Exemplo 1 — a primeira resposta, com decisão (etapa 2 — Escolher)

Situação: projeto sem revisores, um agente só, sem chave.

**Status** — `Revisores: ✅ 1 Conferir · ▶️ 2 Escolher · ⬜ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`
(no Status: "Conferir" foi a leitura deste computador; "Escolher" é decidir quem revisa.)

**O que foi feito** — Conferi este computador sem mudar nada. A revisão adversarial é uma outra IA lendo o que foi
construído, e uma terceira conferindo essa leitura; sem ela configurada, a publicação pede para seguir sem revisão.
Aqui ainda não há revisor nem auditor, e o único agente de IA instalado é o claude.

**Agora: etapa 2 — Escolher** — Leva uns 10 minutos, quase tudo no site do OpenRouter. O caminho recomendado custa
por uso, fora da sua assinatura: centavos de dólar por revisão no teto (digo o valor medido pela tabela do pacote).

**Sua decisão** — [D2 · muda o produto] **Como você quer configurar quem revisa e quem audita?**
- **OpenRouter** (recomendado) — dois modelos diferentes pelo mesmo serviço: um revisa, o outro audita. Mostro o
  passo a passo (conta, crédito, chave com limite) e paro quando for a sua vez no site.
- **uma engine só** — o claude revisa e audita a própria revisão; não custa nada a mais, e a auditoria tem os mesmos
  pontos cegos da revisão (fica registrado "diversidade: nenhuma").
- **agora não** — nada é gravado; na publicação, você vai precisar escrever o motivo de seguir sem revisão.
- **não sei** — explico a diferença entre revisor e auditor com o exemplo de um erro que um só não acharia.

**Próximo passo** — Com o OpenRouter, mostro o 1º bloco: conta e crédito, no navegador.

## Exemplo 2 — parada para reabrir o agente (etapa 3 — Chave)

**Status** — `Revisores: ✅ 1 Conferir · ✅ 2 Escolher · ⏸️ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`

**Por que parei:** o agente só enxerga a chave se for aberto depois de ela ser gravada.

**Onde:** no terminal (ou no editor, se o agente roda dentro dele).

**Passos:**
1. Feche a janela do terminal em que o agente está → o agente fecha.
2. Abra um terminal novo e entre na pasta do projeto → o prompt mostra o nome da pasta.
3. Abra o agente de novo → ele começa sem histórico.
4. Peça: "continue a configuração dos revisores" → eu confiro se a chave chegou.

Agente dentro do editor: feche o editor por completo (no Mac, ⌘Q) e abra de novo, em vez dos passos 1 a 3.

**O que já foi feito:** conta e crédito no OpenRouter, a chave criada com limite e gravada no seu perfil do terminal.
**O que não foi feito:** nada foi gravado no projeto, e nenhum modelo foi escolhido ainda.

Quando terminar, me peça de novo, eu continuo daqui.

## Exemplo 3 — a volta e o OK de gravar (etapa 4 — Gravar)

**Status** — `Revisores: ✅ 1 Conferir · ✅ 2 Escolher · ✅ 3 Chave · ▶️ 4 Gravar · ⬜ 5 Provar`

**O que foi feito** — A chave chegou: o OpenRouter respondeu que ela vale, com limite de US$ 5,00 e US$ 5,00
restantes. Nada foi gasto nessa conferência.

**Agora: etapa 4 — Gravar** — O par sugerido e o preço vêm da tabela do pacote (com a data da conferência). Antes do
seu OK, 4 coisas: cada revisão custa por uso, até a estimativa que mostrei (centavos de dólar no teto); é cobrança do OpenRouter, fora de qualquer
assinatura; o que sai do computador é a mudança do código e os documentos desta frente; e só entram provedores que
não guardam nem treinam com esse conteúdo. Se o projeto tem dado de cliente, a skill `sdd-higiene-dado` impede que
ele entre nos commits e, com isso, na revisão.

**Sua decisão** — [D1 · não se desfaz] **Posso gravar estes dois modelos como revisor e auditor deste computador?**
- **sim** (recomendado) — gravo os dois nas preferências deste computador (não vão para o GitHub) e rodo a prova: a
  chave, os valores lidos de volta e o plano da revisão, sem gastar.
- **trocar os modelos** — você diz os dois modelos (do OpenRouter, diferentes entre si); o preço deles fica desconhecido no
  relatório.
- **não** — nada é gravado; a configuração fica parada aqui, e a chave continua no seu perfil.
- **não sei** — mostro o que uma revisão faz com o seu código, passo a passo, antes de decidir.

**Próximo passo** — Com o seu sim, gravo e mostro a prova em 3 linhas.

## Exemplo 4 — chave colada na conversa

**Status** — `Revisores: ✅ 1 Conferir · ✅ 2 Escolher · ⏸️ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`

**Por que parei:** não vou usar esta chave: ela ficou nesta conversa, e o histórico do agente guarda o texto.

**Onde:** no navegador, na página de chaves do OpenRouter.

**Passos:**
1. Abra `https://openrouter.ai/settings/keys` → você vê a chave na lista, pelo nome.
2. Apague (ou desative) essa chave → ela some da lista ou aparece desativada.
3. Crie outra, com limite, e guarde pelo comando do terminal → a chave não aparece em lugar nenhum.

**O que não foi feito:** nada foi gravado, e a chave colada não foi usada nem repetida.

Quando terminar, me peça de novo, eu continuo daqui.

## Exemplo 5 — a prova (etapa 5 — Provar)

**Status** — `Revisores: ✅ 1 Conferir · ✅ 2 Escolher · ✅ 3 Chave · ✅ 4 Gravar · ✅ 5 Provar`

**O que foi feito** —
- ✅ chave aceita pelo OpenRouter: limite de US$ 5,00, restam US$ 5,00;
- ✅ revisor e auditor gravados neste computador e lidos de volta;
- ✅ plano da revisão: dois modelos diferentes (diversidade de modelo); o 2º revisor, quando a mudança mexer em
  login ou senha, é o claude; o desempate também.

Pronto: a revisão roda quando a fase pedir, e o custo de cada uma aparece no relatório dela.

**Próximo passo** — Volte à fase em que você estava; ela já encontra os revisores.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
