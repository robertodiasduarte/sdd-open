# Design Protocol

## Objetivo

Converter Brainstorm + DEFINE em uma especificação técnica pronta para Build, preservando requisitos já validados e resolvendo somente decisões técnicas que ainda bloqueiam implementação.

## State machine

`LOAD_INPUTS`
→ `EXTRACT`
→ `TECH_CONTEXT`
→ `CLARIFY`
→ `ARCHITECT`
→ `DECIDE`
→ `FILE_MANIFEST`
→ `CODE_PATTERNS`
→ `LLM_CHECK`
→ `DATA_FLOW`
→ `TESTING`
→ `OPERABILITY`
→ `CROSS_CHECK`
→ `VALIDATE`
→ `SAVE_DESIGN`
→ `HANDOFF_TO_BUILD`

Voltar ao estado afetado quando uma resposta do usuário mudar uma decisão anterior.

## Responsabilidades das fontes

### Brainstorm
Usar para:
- intenção original;
- abordagem escolhida;
- alternativas exploradas;
- YAGNI;
- decisões e hipóteses iniciais.

Não usar Brainstorm para sobrepor requisitos que o DEFINE refinou.

### DEFINE
Tratar como fonte principal de:
- comportamento;
- escopo;
- constraints;
- Acceptance Tests;
- Success Criteria;
- Verify Gate;
- Technical Context;
- `LLM Prompts`.

### UX Review
Quando fornecido, usar para:
- estados de interface;
- comportamento perceptível;
- constraints de UX/CX;
- decisões de fluxo que impactem arquitetura.

### Código/projeto
Usar como evidência de:
- stack;
- paths;
- padrões existentes;
- infraestrutura;
- convenções;
- testes;
- agentes especializados.

Nunca afirmar inspeção que não ocorreu.

## Política de perguntas

Perguntar somente quando uma lacuna mudar:
- arquitetura;
- contrato;
- persistência;
- integração;
- segurança;
- testabilidade;
- File Manifest;
- runtime LLM.

Preferir uma pergunta principal por interação.

Quando houver alternativas:
1. mostrar 2–4;
2. colocar a recomendada primeiro;
3. explicar o trade-off em uma linha;
4. aceitar resposta aberta.

Não perguntar preferência cosmética sem impacto técnico.

## Gate de contexto técnico

Antes de fechar File Manifest, ter evidência suficiente sobre:
- stack;
- estrutura;
- arquivos/módulos existentes relevantes;
- convenção de testes;
- configuração/deployment relevante.

Para greenfield, confirmação explícita de stack e convenção base pode substituir inspeção.

## Gate arquitetural

O DESIGN final precisa:
- ter diagrama legível;
- ter fronteiras de componentes;
- documentar decisões significativas;
- evitar dependência circular;
- cobrir fluxo de dados e integrações;
- planejar falhas;
- mapear testes;
- cobrir segurança e observabilidade.

## Gate de decisão

Uma decisão significativa deve responder:
- por que decidir;
- o que foi escolhido;
- por que;
- o que foi rejeitado;
- qual consequência foi aceita.

Se uma decisão já veio fechada do DEFINE, não fabricar debate; indicar sua origem e documentar impacto técnico.

## Gate do File Manifest

Todo item deve ter:
- path;
- Create/Modify/Delete;
- purpose;
- owner/agent;
- dependencies.

Incluir testes e artefatos auxiliares necessários ao Build.

A graph de dependências deve ser acíclica.

## Gate de snippets

Snippets devem:
- usar stack confirmada;
- ser pequenos;
- servir como padrão;
- não implementar a feature inteira;
- poder ser copiados sem depender de pseudo-APIs inventadas.

Quando um detalhe de API não for conhecido, usar pseudocode explícito ou perguntar, em vez de fingir uma chamada real.

## Gate de operabilidade

Cobrir:
- erros;
- configuration;
- security;
- observability.

Design pronto para Build não pode depender de “resolver depois” um comportamento que mude arquitetura.

## Gate de conclusão

Marcar `Ready for Build` somente quando:
- inputs obrigatórios foram lidos;
- decisões bloqueantes estão fechadas;
- manifest está completo;
- cross-check passa;
- a releitura contra o checklist de qualidade passou;
- não há placeholders/TBD;
- handoff final está correto.

## Handoff

Finalizar somente com:

```markdown
## Next Step

Execute o **SDD Build by RDD**.
```
