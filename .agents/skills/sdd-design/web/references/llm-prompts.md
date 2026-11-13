# LLM Prompts no DESIGN

## Regra principal

Extrair `LLM Prompts: true|false` do Technical Context do DEFINE.

Se ausente, vazio ou ambíguo: perguntar antes de concluir o DESIGN.

## Rechecagem defensiva

Mesmo com `false`, procurar sinais no Brainstorm, DEFINE, UX Review e escopo técnico:
- system/user prompt;
- arquivos em `prompts/`;
- chamadas a provider/model de LLM;
- RAG, embeddings usados para geração;
- classifier/synthesizer baseado em LLM;
- chatbot/agente;
- geração automática de texto/relatório;
- processo que usa resposta do LLM como entrada de nova chamada.

Se houver sinal material incompatível com `false`, não ignorar.

Perguntar se:
1. o DEFINE deve continuar como `false` porque são falsos positivos;
2. o DESIGN deve registrar divergência e usar `true`;
3. o usuário pretende revisar o DEFINE antes.

## Quando false

- Não criar `## LLM Prompts`.
- Registrar no Revision History somente se houve divergência/resolução relevante.
- Não chamar skill de prompt engineering.

## Quando true

Inserir `## LLM Prompts` imediatamente após `## Code Patterns` e antes de `## Data Flow`.

### Inventory

| # | Path / Runtime | Type | Consumer | Output Shape |
|---|---|---|---|---|
| LP-001 | `path/or/service` | one-shot / loop | `consumer` | `schema/type` |

Cobrir:
- todo arquivo planejado sob `**/prompts/**`;
- todo serviço do File Manifest que chama LLM em runtime.

### Classificação

`one-shot`:
- uma chamada principal;
- a resposta não dispara novo ciclo de raciocínio/ação do mesmo processo.

`loop`:
- processo reason → act → observe → adjust;
- o LLM é chamado novamente com base em seu próprio output/observação anterior.

Na dúvida, perguntar.

### Contrato por prompt

Para cada item registrar:
- Purpose;
- Type;
- Consumer;
- Tone/Audience;
- Input shape;
- Output shape;
- Approved fallback;
- Reference material;
- Settled decisions: provider/model/version somente quando já decididos;
- Failure behavior.

Não inventar tone, fallback, provider, model ou schema.

Não escrever o prompt final nesta fase. O DESIGN compila o contrato para uso no Build.

## Cross-check

Antes de concluir:
- todo path `prompts/` do manifest aparece no inventory;
- todo runtime LLM conhecido aparece no inventory;
- todo inventory aponta para consumidor e output shape;
- cada item tem contrato;
- `loop`/`one-shot` foi classificado.
