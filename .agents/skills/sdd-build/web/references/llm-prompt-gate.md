# LLM Prompt Gate durante Build

## Fonte

Ler:
- `LLM Prompts: true|false` no DEFINE;
- `## LLM Prompts` e inventory no DESIGN.

## Consistência inicial

`true` + sem inventory → STOP e corrigir Design.

`false` + inventory → STOP e resolver divergência.

## Drift detection

Mesmo quando `false`, considerar cheiro de runtime prompt:
- path sob `prompts/`;
- system/user prompt persistido;
- chamada chat/completions/responses;
- parâmetro `system`;
- serviço que passa instruções a um modelo;
- loop agente que reenvia output ao LLM.

Se cheiro existir e não estiver no inventory:
- não materializar silenciosamente;
- perguntar se é falso positivo ou drift real;
- drift real exige revisão do Design;
- falso positivo deve ser registrado.

## Inventory item

Para cada item listado no Design, ler:
- path/runtime;
- type (`one-shot` ou `loop`);
- consumer;
- input/output shape;
- decisões fechadas;
- referências.

Não reabrir provider/model/schema fechado.

## one-shot

Quando a skill de prompt engineering estiver disponível (`sdd-prompt-builder`, ou a que você tiver configurado):
- compilar contrato + referências;
- executá-la;
- tratar o resultado como input intermediário;
- materializar o prompt no path previsto;
- continuar a tarefa e verificar.

Se a skill não estiver disponível:
- não inventar o prompt final;
- bloquear o item afetado e pedir decisão/dependência ao usuário.

⛔ Calibre o sinal de drift pelo código real do projeto: se as chamadas de LLM passam por um
wrapper próprio, procurar só pelas assinaturas do SDK deixa o gate cego. Exclua arquivos de
teste, ou o gate acusa a cada build e passa a ser ignorado.

## loop

Quando a skill de loop-specification estiver disponível:
1. gerar LOOP_SPEC;
2. para cada estágio LLM, executar prompt engineering;
3. materializar harness + prompts conforme Design;
4. verificar.

Sem essa capacidade, não simular um loop spec “de cabeça”.

## Receipt no Build Report

Para cada item:
- inventory id;
- path;
- type;
- builder/skill usada;
- resultado;
- verificação.

Se `LLM Prompts=true`, todos os inventory items precisam de receipt para Build completo.

Se `false` e zero drift, a seção condicional pode ser omitida.
Se houver drift, registrar mesmo que o inventory executado esteja vazio.
