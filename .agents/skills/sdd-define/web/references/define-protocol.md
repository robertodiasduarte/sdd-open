# Define Protocol

## Purpose

Converter um Brainstorm pré-validado em um DEFINE verificável, fazendo apenas as clarificações necessárias para que requisitos, métricas, acceptance tests, escopo e gate de verificação fiquem suficientemente claros.

## State machine

`LOAD_BRAINSTORM`
→ `EXTRACT`
→ `DRAFT`
→ `SCORE`
→ `CLARIFY`
→ `EARS`
→ `VERIFY_GATE`
→ `QUALITY_GATE`
→ `SAVE_DEFINE`
→ `HANDOFF_TO_DESIGN`

Voltar a estados anteriores sempre que uma resposta do usuário invalidar uma decisão já registrada.

## Source precedence

1. Resposta explícita mais recente do usuário.
2. Decisão validada no Brainstorm.
3. Fato explicitamente descrito no Brainstorm.
4. Contexto adicional fornecido pelo usuário.
5. Inferência — somente se rotulada e não usada para fechar gate sem confirmação.

Nunca promover hipótese a requisito definitivo sem confirmação quando ela mudar comportamento, escopo, métrica ou teste.

## Extraction map

| DEFINE | Prioridade de origem no Brainstorm |
|---|---|
| Problem Statement | Initial Idea, Discovery, Suggested Requirements |
| Target Users | Discovery, Suggested Requirements |
| Goals | Selected Approach, Key Decisions, Suggested Requirements |
| Success Criteria | Suggested Requirements, Incremental Validations |
| Acceptance Tests | requisitos + comportamentos + edge cases confirmados |
| Out of Scope | YAGNI, rejected approaches, explicit exclusions |
| Constraints | Key Decisions, limitations, dependencies |
| Technical Context | project context explícito, approach, dependencies |
| Assumptions | hipóteses declaradas ainda não validadas |

## Clarification behavior

- Não repetir perguntas já respondidas no Brainstorm.
- Perguntar apenas quando a resposta alterar o documento de forma material.
- Prioridade: arquitetura/contratos externos → escopo → métricas/done signal → edge cases → demais gaps.
- Preferir uma pergunta por interação.
- Nunca exceder 5 perguntas por rodada.
- Recomendar opção quando houver base para isso, mas deixar o usuário decidir.
- Integrar a resposta no corpo; o log de Clarifications é registro, não substituto da correção do requisito.

## Clarity gate

Pontuar Problem, Users, Goals, Success e Scope de 0 a 3.

`READY` requer total >= 12/15.

Uma pontuação alta não compensa:
- acceptance test não verificável;
- ambiguidade bloqueante;
- Verify Gate ausente;
- métrica inventada.

## EARS gate

Todo novo ou revisado Acceptance Test deve seguir `references/EARS.md`.

Bloquear conclusão quando:
- teste não contém padrão EARS;
- há trigger indesejado plausível sem If/Then;
- bugfix não contém não-regressão;
- critério depende de adjetivo não mensurado.

## Ambiguity gate

Aplicar `references/CLARIFY.md`.

Varrer:
- scope;
- data model;
- UX flow;
- NFRs;
- integrations;
- edge cases;
- constraints;
- terminology;
- done signal.

O documento pronto deve ter zero ambiguidades bloqueantes.

## Verify gate

Aplicar `references/VERIFY_GATE.md`.

Escolher exatamente um kind:
- test;
- smoke;
- eval;
- typecheck;
- manual-ux.

Nunca inventar um `cmd` específico do projeto.

Quando o comando não estiver disponível, abrir clarificação com a pergunta da caixa "Se é a sua primeira vez" de `VERIFY_GATE.md`: existe um comando que devolve 0 quando funciona? `manual-ux` é válido quando a natureza do valor é humana/visual ou quando o aluno responde que não existe comando — nunca sem fazer a pergunta, salvo na UX pura (aparência, que nenhum comando julga).

## Completion gate

O DEFINE está pronto somente quando:
- Clarity >= 12/15;
- Problem, Users, Goals, Success e Scope estão claros;
- EARS passa;
- ambiguidades bloqueantes = 0;
- LLM Prompts é literal true/false;
- Verify Gate está completo;
- Out of Scope está explícito;
- a releitura contra o checklist de qualidade passou.

## Final handoff

O documento final termina somente com:

```markdown
## Next Step

Execute o **SDD Design by RDD**.
```

Nada deve ser acrescentado depois.
