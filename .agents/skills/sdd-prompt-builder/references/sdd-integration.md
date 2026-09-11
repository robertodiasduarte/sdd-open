# Integração com o fluxo SDD

Consultar este arquivo sempre que a skill for chamada pelas fases Design/Build.

## Contrato de entrada da fase Build

O caller deve compilar e fornecer, para cada prompt do inventário `LLM Prompts`:

1. Linha do inventário:
   - nome;
   - arquivo de destino;
   - versão;
   - provider/modelo;
   - input source;
   - output consumer;
   - requisito de completude;
   - referência de refator, quando houver.

2. Bloco `Contrato por prompt` completo:
   - tom/audiência;
   - output type;
   - fallback aprovado;
   - execução autônoma ou interativa;
   - verificação interna;
   - eval mínimo.

3. Material de referência literal:
   - conteúdo bruto de schema, regra, trecho de UX ou outro material;
   - não receber somente ponteiros como `[arquivo:linha]` quando o conteúdo for necessário
     para construir o prompt.

4. Decisões já fechadas:
   - provider;
   - modelo;
   - output format;
   - demais decisões que a skill não deve reabrir.

Se qualquer bloco obrigatório estiver ausente, não improvisar. O caller deve atualizar o DESIGN
antes da geração.

## Drift detection — ancore nos sinais do SEU projeto

Mesmo quando o DEFINE indicar `LLM Prompts: false`, tratar como drift se a fase Build for
escrever algo que caia em um destes sinais:

| Categoria | Sinal |
|---|---|
| Path | `**/prompts/**` · arquivos de template compartilhados · módulos com `prompt` no nome |
| Conteúdo | o parâmetro de system prompt do seu wrapper de LLM **recebendo um literal** |
| Conteúdo | chamada direta ao SDK do provider (`messages.create`, `chat.completions`) |

⛔ **Calibre os sinais pelo código real do projeto, não por uma lista genérica.** Se o seu
projeto centraliza as chamadas num wrapper (`callLLM`, `askModel`, um client próprio), o sinal
que importa é **o parâmetro desse wrapper**, e procurar só pelas assinaturas do SDK deixa o
gate cego. Vale o inverso também: se nada centraliza, as assinaturas do SDK são o sinal.

Duas exclusões evitam que o gate vire lobo e seja ignorado:

- **arquivos de teste** — literal em fixture de teste não é prompt de produção;
- **parâmetro recebendo identificador importado** — o prompt mora no arquivo importado, que já
  é pego pelo sinal de path.

Quando o sinal existir e o arquivo não estiver no inventário:

1. não gerar o prompt diretamente;
2. sinalizar que o DESIGN precisa registrar o inventário de LLM Prompts;
3. retomar a skill somente depois que o caller fornecer o contrato compilado.

## Prompt único × processo iterativo

A coluna `Tipo` do inventário decide o caminho:

| Tipo | Quando | Quem constrói |
|---|---|---|
| `one-shot` | chamada única: system prompt, classificador, sintetizador, passe único | esta skill, direto |
| `loop` | processo iterativo que re-prompta o modelo com base na própria saída anterior | primeiro a especificação do loop; depois **um prompt por estágio**, cada um por esta skill |

Sinal decisivo: *o processo re-prompta o modelo com base na própria saída anterior?* Sim →
`loop`.

## Saída para o caller

Retornar somente o conteúdo do prompt dentro de um TXT BLOCK.

O caller é responsável por:

- escolher o path exato a partir do inventário;
- embrulhar o texto na forma que a linguagem do projeto pedir (constante exportada, arquivo de
  template, entrada de configuração) e gravar no destino;
- criar nova versão `v{N+1}/` ao refatorar prompt em produção, sem editar a versão existente
  in-place;
- registrar no relatório de build: nome, arquivo, versão nova, versão anterior, seções geradas
  e status de eval.

### Onde entra o dado da requisição

⛔ **O input concreto (o documento, a transcrição, a mensagem do usuário) vai na mensagem do
usuário, nunca no system prompt.** O system é genérico e reusável entre requisições; o user é
por requisição. Prompt com dado embutido impede reuso e desperdiça cache de prompt.

## Versionamento

- Refator de prompt que já atendeu ao menos uma requisição real ⇒ **nova pasta `v{N+1}/`**;
  edit in-place proibido (histórico, teste A/B e rollback dependem disso).
- ⛔ **O prompt vivo é o que o código importa, não o de maior número.** Antes de editar,
  procure o import real: um rollback anterior pode ter deixado a versão mais alta órfã enquanto
  o código serve a anterior.
- Rollback = mudar uma linha de import.

## Limite de responsabilidade

Esta skill não deve ler DEFINE, DESIGN ou relatório de build diretamente se o fluxo já atribuir
essa curadoria ao caller. Receber o contexto compilado e produzir o prompt operacional. Fora do
fluxo SDD, aceitar uso manual/ad hoc normalmente.
