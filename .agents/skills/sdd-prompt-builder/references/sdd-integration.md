# Integração com o fluxo SDD

Consultar este arquivo sempre que a skill for chamada pela fase Build; a fase Design só inventaria, sem chamar skill de prompt.

## Contrato de entrada da fase Build

O caller deve compilar e fornecer, para cada prompt do inventário `LLM Prompts`
(`sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`):

1. Linha do inventário:
   - Nome;
   - Arquivo de destino;
   - Versão;
   - Provedor/Modelo;
   - Origem da entrada;
   - Consumidor da saída;
   - Material de referência;
   - Completeness;
   - Refator de?.

2. Bloco `Contrato por prompt` completo:
   - Tom/audiência;
   - Tipo de saída;
   - Fallback aprovado;
   - Autônomo?;
   - Verification interna;
   - Eval mínimo pré-ship.

   Estágio LLM de uma LOOP_SPEC não tem linha própria: o contrato dele é o bloco da linha `Tipo=loop` mais a
   linha do estágio na tabela de estágios e o contrato de saída dele em PROMPTS PENDENTES.

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

Mesmo quando o DEFINE indicar `LLM Prompts: false`, a fase Build passa por
`bash sdd/bin/prompt-drift-scan.sh --conteudo <caminho>` o que vai gravar fora do inventário. Sinais do script:

| Categoria | Sinal |
|---|---|
| Path | pasta `prompts/` em qualquer profundidade · nome com `prompt` (exceto `.md`) |
| Conteúdo | o parâmetro do wrapper de LLM do projeto (`prompts.wrapper_pattern`) **recebendo um literal** |
| Conteúdo | chamada direta ao SDK do provider (`messages.create`, `chat.completions`, `responses.create`, `generateContent` e as formas de streaming) · `system` com literal, em `:` ou `=` · `role` de sistema |

⛔ **Calibre os sinais pelo código real do projeto, não por uma lista genérica.** Se o seu
projeto centraliza as chamadas num wrapper (`callLLM`, `askModel`, um client próprio), preencha
`prompts.wrapper_pattern` com a expressão do parâmetro desse wrapper: procurar só pelas assinaturas
do SDK deixa o gate cego, e o script avisa enquanto o slot estiver vazio.

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
| `loop` | processo iterativo que re-prompta o modelo com base na própria saída anterior | primeiro a `sdd-loop-builder` (a LOOP_SPEC); depois **um prompt por estágio LLM**, cada um por esta skill |

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
  e status de eval; num item `loop`, 1 entrada pela LOOP_SPEC e 1 por estágio.

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
