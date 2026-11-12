# Procedimento da revisão de governança

> Seis passos, sempre nesta ordem. O catálogo é `references/CATALOGO_GOVERNANCA.md`; o relatório segue
> `assets/GOVERNANCA_REVIEW_TEMPLATE.md`; o padrão do projeto segue `assets/GOVERNANCA_PADRAO_TEMPLATE.md`.
> Esta revisão recomenda; **quem decide e responde é o profissional**.

## Antes de começar

- Leia o DEFINE inteiro. Se não encontrar o arquivo, diga exatamente onde procurou e peça o caminho.
  Nunca invente o conteúdo de um DEFINE.
- Quem escreveu o Define não deve revisá-lo na mesma conversa: rode a revisão numa conversa nova, ou
  num subagente que receba só o DEFINE e esta skill.
- Fale com contador sênior: use o vocabulário do ofício (lançamento, estorno, competência, escrituração,
  conciliação) sem explicar o que ele já sabe.

## Passo 1 — Triagem por gatilhos

Procure no DEFINE estes temas — **pelo sentido, não só pela palavra** (sem diferenciar maiúsculas, singular ou plural):

`dinheiro` · `valor` · `preço` · `pagamento` · `cobrança` · `compra` · `boleto` · `fatura` · `saldo` · `lançamento` · `nota fiscal` / `NF` · `tributo` / `imposto` · `folha` · `dado pessoal` / `CPF` / `CNPJ`

- Palavra igual com outro sentido **não conta**: "imposto" do verbo impor ("o limite imposto pelo plano"),
  "NF" dentro de um código ou de outra palavra.
- O tema conta mesmo sem a palavra da lista: uma coluna `valor_bruto`, "o cliente pagou a mensalidade", "a fatura do
  cliente" tratam dinheiro.
- **Em dúvida, não é N.A.**: siga para o passo 2 — cada item sem relação com a feature sai `N.A.` com o motivo.
  N.A. indevido na triagem pula a revisão inteira; N.A. por item custa uma linha.

**Nenhum tema** ⇒ responda com **uma mensagem só**, sem criar arquivo nenhum, e encerre:

> Revisão de governança: **N.A.** — o Define não trata dinheiro, saldo, lançamento, nota fiscal, tributo,
> folha nem dado pessoal. Siga para a próxima fase.

**Um ou mais temas** ⇒ registre quais encontrou (e onde, por linha ou AT) e siga para o passo 2.

## Passo 2 — Padrão do projeto

Procure `GOVERNANCA_PADRAO.md` na **raiz da pasta do SDD do projeto** — o mesmo lugar onde a skill o grava na
primeira vez (a porta de cada kit diz qual é essa pasta). Nunca dentro de uma subpasta de features: o padrão é
um só por projeto.

- **Existe** ⇒ não repita as perguntas. Confirme em uma linha: "Usando o padrão do projeto: uso = …,
  multi_cnpj = …, IA grava sozinha = …, responsável técnico = …, guarda = …. Mudou alguma coisa?"
- **Não existe** ⇒ faça as cinco perguntas **numa mensagem só**, grave as respostas no template e siga:
  1. Quem vai usar o sistema? (só você · a equipe do escritório · clientes também)
  2. Há mais de um CNPJ no mesmo banco de dados? (sim · não)
  3. Alguma IA do sistema grava, classifica ou sugere lançamento sozinha? (sim · não)
  4. Quem responde tecnicamente pelo sistema? (nome e CRC)
  5. Por quanto tempo o dado tem de ser guardado? (padrão: até a prescrição)

O padrão vale para todas as features do projeto. Ele decide o `porte_min` de cada item do catálogo.

## Passo 3 — Item a item

Para **cada** item do catálogo, dê exatamente um veredito:

| Veredito | Quando | O que registrar |
|---|---|---|
| `já coberto` | O DEFINE já exige isso, com teste que prova a falha | a linha ou o AT do DEFINE |
| `lacuna` | O item se aplica e o DEFINE não exige, ou exige sem teste negativo | as 5 partes do passo 4 |
| `N.A.` | O item não se aplica a esta feature, ou está abaixo do `porte_min` | o motivo em uma frase (`N.A. por porte: uso = só você`) |
| `2ª camada` | Item G11–G16 não coberto (exceto G13 com `multi_cnpj = sim`), ou lacuna que o profissional decidiu adiar | uma linha |

Regras:

- G01–G10 recebem `já coberto`, `lacuna` ou `N.A.` — nunca `2ª camada` direto, só por adiamento.
- G11–G16 (segunda camada) **nunca saem `lacuna` por padrão**: não cobertos e com o porte atingido, saem
  `2ª camada` (recomendado); abaixo do porte, `N.A. por porte`. **Única exceção:** G13 com `multi_cnpj = sim`
  sai `lacuna` se o DEFINE não cobre — dado de um CNPJ aparecendo para outro é inegociável quando existe.
- G17–G20 só se aplicam com `porte_min: ia`; sem IA, são `N.A.` com o motivo.
- "Já coberto" exige prova: um requisito que diz "o sistema deve ter trilha de auditoria" sem dizer o que
  é recusado não cobre G04 — é `lacuna` com a parte que falta.

## Passo 4 — O relatório

Grave o relatório pelo template. Ele abre com a **cobertura em uma linha** e cada lacuna tem, **nesta ordem**:

1. **O que muda no app** — uma frase que o profissional entende sem abrir o catálogo
   ("lançamento gravado não se edita; corrige-se por estorno com motivo").
2. **Por quê** — o fundamento técnico do item, com as suas palavras, e no fim o campo **Base legal:**, que
   fecha o parágrafo com **exatamente um** destes três textos, sem nada acrescentado:
   - base `confirmado` na Tabela B ⇒ o `texto_citavel` dela;
   - base `nao-confirmado` ⇒ `**Base legal:** ainda não confirmada no catálogo — confira na fonte antes de citar.`
   - item sem base no catálogo (coluna `base` = `—`) ⇒
     `**Base legal:** o catálogo não aponta base legal para este item — o fundamento técnico vale por si.`

   O campo aparece uma vez por lacuna. O fundamento técnico vem **antes** dele, nunca dentro. Nunca cite
   lei, decreto, norma, artigo, parágrafo ou inciso que não seja o `texto_citavel` de uma base `confirmado`
   — nem de memória, nem "aproximadamente", nem em outro lugar do relatório.
3. **Requisito (EARS)** — no padrão Unwanted: **If** {ação proibida}, **then** the system **shall** {recusar …}.
4. **Como provar** — o `prova_manual` do item adaptado aos nomes do DEFINE; quando a forma de entrega pede
   script, o `prova_script` adaptado, **sem mexer na inversão**.
5. **Severidade** — a do catálogo (`alta` · `média` · `baixa`).

## Passo 5 — Decisão por item

Pergunte **uma lacuna por vez**. Cada pergunta traz o que muda no app e a severidade e, quando um AT do DEFINE
contradiz o requisito (ex.: "o analista corrige o valor de um lançamento gravado" × lançamento que não se apaga),
mostra esse AT **antes e depois** da reescrita. Oferece três saídas:

- **Aplicar** — o requisito entra no DEFINE.
- **Recusar** — o requisito não entra; **o motivo é obrigatório**. Recusa sem motivo: repita a pergunta
  pedindo o motivo e não grave nada. A recusa vai para *Riscos aceitos* com quem, quando e por quê.
- **Adiar** — o requisito vai para a *2ª camada*, sem prazo, e não entra no DEFINE agora.

Nunca ofereça "aplicar todos". Nunca aplique sem a resposta do profissional.

## Passo 6 — Aplicar no DEFINE

Para cada lacuna aplicada:

- **reescreva primeiro o AT que contradiz o requisito** (o "antes e depois" que o profissional aprovou no passo 5) —
  nunca deixe no DEFINE um AT que permite o que o AT novo proíbe. Se a reescrita mudar o que a feature faz além
  do que a pergunta mostrou, pare e pergunte de novo;
- acrescente um AT novo em `## Acceptance Tests` com o próximo número livre, o padrão EARS do requisito e
  a prova na coluna do gate;
- registre a mudança no histórico de revisões do DEFINE;
- recalcule o Clarity Score e anote antes e depois.

O relatório fecha com a seção *Aplicado no DEFINE* (lacuna → AT novo, e o AT reescrito quando houve) e com as duas linhas fixas:

> A skill recomenda; o profissional decide e responde.
>
> No Build, o passo *Aplicar a migration* da `sdd-build` prova por leitura (`information_schema`,
> `pg_policies`, `pg_trigger`) que o SQL criou o que estes itens exigem: os itens com `prova pós-build = sim`
> no catálogo têm o que conferir no banco depois de aplicada a migration.
