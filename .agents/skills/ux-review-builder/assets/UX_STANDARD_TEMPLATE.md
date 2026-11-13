# UX STANDARD: {PROJECT_NAME}

> Fonte canônica de UX do projeto. Versão: {VERSION}. Idioma: {USER_LANGUAGE}.

## Metadata

| Campo | Valor |
|---|---|
| Projeto | {PROJECT_NAME} |
| Versão | {VERSION} |
| Data | {YYYY-MM-DD} |
| Responsável | {OWNER} |
| Status | Draft / Approved / Deprecated |
| Local | Pasta do SDD do projeto, ao lado do Define e do Design |
| Modo | Criação / Evolução |

## Como usar esta fonte canônica

- `DEFINE` define o que a feature precisa fazer.
- Este `UX_STANDARD` define como a experiência deve se comportar.
- `UX_REVIEW_TEMPLATE` define como documentar a revisão.
- A `ux-review` pode sugerir mudanças, mas não altera este arquivo automaticamente.

## Produto e contexto

{PRODUCT_CONTEXT}

## Usuários e contextos de uso

| Público | Objetivo | Frequência | Nível técnico | Dispositivo/contexto | Risco principal |
|---|---|---|---|---|---|
| {USER} | {GOAL} | {FREQUENCY} | {SKILL_LEVEL} | {CONTEXT} | {RISK} |

## Referências de experiência

| Referência | Tipo | Observado | Desejado pelo usuário | Decisão canônica |
|---|---|---|---|---|
| {REFERENCE} | Produto / URL / Material interno | {OBSERVED} | {DESIRED} | {CANONICAL_DECISION} |

## North Star da experiência

{NORTH_STAR}

## Princípios universais obrigatórios

| ID | Regra | Como verificar | Severidade-base | Origem | Estado |
|---|---|---|---|---|---|
| UX-CORE-001 | A tarefa principal deve ser compreendida sem manual, tour obrigatório ou tooltip-muleta. | Usuário novo identifica objetivo e próximo passo pela interface. | MUST | Universal | Active |
| UX-CORE-002 | Estados relevantes devem ser inequívocos. | Salvo, pendente, processando, concluído e erro não se confundem. | MUST | Universal | Active |
| UX-CORE-003 | A ação principal deve ser evidente em cada contexto. | Ação primária não compete visualmente com secundárias equivalentes. | MUST | Universal | Active |
| UX-CORE-004 | Erros previsíveis devem ser prevenidos e recuperáveis. | Erros acionáveis oferecem orientação, retry, undo ou alternativa adequada. | MUST | Universal | Active |
| UX-CORE-005 | Acessibilidade deve ser considerada desde o início. | Teclado, foco, labels, contraste, toque e sinais não dependentes apenas de cor são verificáveis. | MUST | Universal | Active |
| UX-CORE-006 | Responsividade deve preservar a tarefa. | Prioridade, ordem de leitura, legibilidade e capacidade de agir sobrevivem à mudança de viewport. | MUST | Universal | Active |
| UX-CORE-007 | Ações relevantes devem produzir feedback perceptível. | Usuário entende que o sistema recebeu, processou ou concluiu a ação. | MUST | Universal | Active |
| UX-CORE-008 | Intenções iguais devem usar padrões consistentes. | Mesma intenção usa linguagem, componente e comportamento equivalentes. | SHOULD | Universal | Active |
| UX-CORE-009 | Dark patterns são proibidos. | Não há consequência escondida, urgência falsa ou fricção deliberada para impedir escolha legítima. | MUST | Universal | Active |
| UX-CORE-010 | Estados de sistema fazem parte da feature. | Loading, empty, error, success, partial data, permission denied e disabled estão definidos quando aplicáveis. | MUST | Universal | Active |

## Princípios específicos do projeto

| ID | Regra | Como verificar | Severidade-base | Origem | Estado |
|---|---|---|---|---|---|
| {UX-FAMILY-001} | {RULE} | {CHECK} | MUST/SHOULD/COULD | Usuário / Referência confirmada / Material existente | Active |

## Hierarquia, densidade e visual

{VISUAL_GUIDANCE}

### Regras verificáveis

| ID | Regra | Como verificar | Severidade-base | Origem | Estado |
|---|---|---|---|---|---|
| UX-VIS-001 | {RULE} | {CHECK} | {PRIORITY} | {SOURCE} | Active |

## Cor, tokens e temas

Não inventar tokens. Registrar somente o sistema confirmado ou existente.

| ID | Papel semântico | Token/valor | Uso | Contraste/critério | Estado |
|---|---|---|---|---|---|
| UX-VIS-010 | {ROLE} | {TOKEN_OR_VALUE} | {USE} | {CHECK} | Active |

## Tipografia e espaçamento

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-VIS-020 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Navegação e arquitetura de informação

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-NAV-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Interação e feedback

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-INT-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Estados obrigatórios

| ID | Estado | Regra | Como verificar | Severidade-base |
|---|---|---|---|---|
| UX-STATE-001 | Loading | {RULE} | {CHECK} | MUST |
| UX-STATE-002 | Empty | {RULE} | {CHECK} | MUST |
| UX-STATE-003 | Error | {RULE} | {CHECK} | MUST |
| UX-STATE-004 | Success | {RULE} | {CHECK} | MUST |
| UX-STATE-005 | Partial Data | {RULE} | {CHECK} | MUST/SHOULD |
| UX-STATE-006 | Permission Denied | {RULE} | {CHECK} | MUST |
| UX-STATE-007 | Disabled | {RULE} | {CHECK} | SHOULD/MUST |

## Formulários e entrada de dados

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-FORM-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Tabelas, dashboards e dados

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-DATA-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Conteúdo, tom de voz e microcopy

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-COPY-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Acessibilidade

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-A11Y-001 | {RULE} | {CHECK} | MUST | Active |

## Responsividade

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-RESP-001 | {RULE} | {CHECK} | MUST/SHOULD | Active |

## Movimento e microinterações

| ID | Regra | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-MOTION-001 | {RULE} | {CHECK} | {PRIORITY} | Active |

## Gamificação

| ID | Regra/decisão | Como verificar | Severidade-base | Estado |
|---|---|---|---|---|
| UX-GAME-001 | {RULE_OR_SKIP} | {CHECK} | SHOULD/COULD/WONT | Active |

## Antipadrões proibidos

| ID | Antipadrão | Evidência de violação | Severidade-base |
|---|---|---|---|
| UX-ANTI-001 | {ANTI_PATTERN} | {VIOLATION_EVIDENCE} | MUST |

## Critérios globais de qualidade

{QUALITY_CRITERIA}

## Exceções aceitas

| Regra | Exceção | Motivo | Responsável | Data | Revisar em |
|---|---|---|---|---|---|
| {RULE_ID} | {EXCEPTION} | {REASON} | {OWNER} | {DATE} | {REVIEW_DATE} |

## Governança

- A `ux-review` pode sugerir mudanças, mas não altera este arquivo automaticamente.
- Toda mudança relevante exige aprovação explícita do responsável.
- IDs não são reutilizados para significados diferentes.
- Regras descontinuadas permanecem rastreáveis no histórico.

## Histórico de revisões

| Versão | Data | Responsável | Mudanças |
|---|---|---|---|
| 1.0.0 | {YYYY-MM-DD} | {OWNER} | Criação inicial |
