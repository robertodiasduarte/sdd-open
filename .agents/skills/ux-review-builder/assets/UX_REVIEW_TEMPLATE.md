# UX REVIEW: {FEATURE_NAME}

> Revisão UX/CX depois do Define e antes do Design, baseada na fonte canônica do projeto. Gravar na pasta do SDD, ao lado do DEFINE.

## Metadata

| Atributo | Valor |
|---|---|
| Feature | {FEATURE_NAME} |
| Data | {YYYY-MM-DD} |
| Autor | ux-review |
| DEFINE | {DEFINE_PATH} |
| UX_STANDARD | {UX_STANDARD_PATH} |
| UX_STANDARD Version | {UX_STANDARD_VERSION} |
| Status | Draft / Ready for Design / Blocked for Design |

## UX Summary

{Resumo de 2-4 frases com objetivo da experiência, maior risco e recomendação principal.}

## Sources and Evidence

| Fonte | Papel | Versão/estado | Evidência usada |
|---|---|---|---|
| DEFINE | Requisitos funcionais | {VERSION} | {EVIDENCE} |
| UX_STANDARD | Fonte canônica | {VERSION} | {RULE_IDS} |
| {OPTIONAL_SOURCE} | Contexto adicional | {STATE} | {EVIDENCE} |

## User and Context

| Campo | Valor |
|---|---|
| Usuário principal | {PERSONA_OR_ROLE} |
| Objetivo do usuário | {USER_GOAL} |
| Dor principal | {PAIN} |
| Objetivo de negócio/CX | {BUSINESS_GOAL} |
| Dispositivo/contexto | {DEVICE_CONTEXT} |

## Journey Map

| Etapa | Intenção | Emoção/Risco | Fricção | Necessidade da interface | Recuperação |
|---|---|---|---|---|---|
| Before | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Entry | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Core Action | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Feedback | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Recovery | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Interrupção → Retomada | {Sair no meio preserva o que foi feito? Como a pessoa volta?} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Completion | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |
| Follow-up | {TEXT} | {TEXT} | {TEXT} | {TEXT} | {TEXT} |

## Canonical Conformance

| Regra canônica | Status | Evidência | Observação |
|---|---|---|---|
| {UX-ID} | CONFORME / MUST / SHOULD / COULD / WONT / NAO AVALIAVEL | {EVIDENCE} | {NOTE} |

## UX/CX Findings

| Prioridade | Regra canônica | Área | Finding | Evidência | Recomendação |
|---|---|---|---|---|---|
| MUST | {UX-ID} | {AREA} | {RISK} | {EVIDENCE} | {ACTION} |
| SHOULD | {UX-ID} | {AREA} | {OPPORTUNITY} | {EVIDENCE} | {ACTION} |
| COULD | {UX-ID_OR_NA} | {AREA} | {POLISH} | {EVIDENCE} | {ACTION} |
| WONT | {UX-ID_OR_NA} | {AREA} | {EXCLUDED_IDEA} | {EVIDENCE} | {WHY} |

## Universal Principles Check

| ID | Princípio | Status | Evidência/Risco |
|---|---|---|---|
| UX-CORE-001 | Autoexplicativo | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-002 | Estado inequívoco | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-003 | Ação principal evidente | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-004 | Prevenção e recuperação | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-005 | Acessibilidade por padrão | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-006 | Responsividade real | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-007 | Feedback imediato | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-008 | Consistência | CONFORME / SHOULD / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-009 | Sem dark patterns | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |
| UX-CORE-010 | Acabamento completo | CONFORME / MUST / NAO AVALIAVEL | {EVIDENCE} |

## Project North Star Checks

| Regra | Status | Evidência/Risco |
|---|---|---|
| {PROJECT_RULE_ID} | CONFORME / MUST / SHOULD / NAO AVALIAVEL | {EVIDENCE} |

## Visual System Review

Validar somente o sistema definido no `UX_STANDARD.md`. Não introduzir tokens, temas, cores, buckets ou ratios de outro projeto.

| Regra | Papel | Evidência | Status | Recomendação |
|---|---|---|---|---|
| {UX-VIS-ID} | {ROLE} | {EVIDENCE} | {STATUS} | {ACTION} |

## Interaction Requirements

| Regra | Requisito | Motivo | Prioridade |
|---|---|---|---|
| {UX-INT-ID} | {REQUIREMENT} | {WHY} | MUST/SHOULD/COULD |

## Required States

| Estado | Regra canônica | UX requerida | Status |
|---|---|---|---|
| Loading | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Empty | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Error | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Success | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Partial Data | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Permission Denied | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |
| Disabled | {UX-STATE-ID} | {REQUIREMENT} | {STATUS} |

## Content and Copy Guidance

| Regra | Surface | Orientação |
|---|---|---|
| {UX-COPY-ID} | Primary CTA | {GUIDANCE} |
| {UX-COPY-ID} | Error Copy | {GUIDANCE} |
| {UX-COPY-ID} | Confirmation | {GUIDANCE} |
| {UX-COPY-ID} | Empty State | {GUIDANCE} |

## Accessibility and Responsiveness

| Regra | Preocupação | Requisito | Evidência/Medição |
|---|---|---|---|
| {UX-A11Y-ID} | Keyboard/Focus | {REQUIREMENT} | {EVIDENCE} |
| {UX-A11Y-ID} | Contrast | {REQUIREMENT} | {MEASURED_OR_NOT_EVALUABLE} |
| {UX-A11Y-ID} | Screen Reader/Labels | {REQUIREMENT} | {EVIDENCE} |
| {UX-RESP-ID} | Mobile/Responsive | {REQUIREMENT} | {EVIDENCE} |
| {UX-A11Y-ID} | Non-color cues | {REQUIREMENT} | {EVIDENCE} |

## Gamification Strategy

| Regra | Oportunidade | Mecânica | Valor para usuário | Guardrail | Prioridade |
|---|---|---|---|---|---|
| {UX-GAME-ID_OR_NA} | {OPPORTUNITY} | {MECHANIC_OR_NONE} | {VALUE} | {GUARDRAIL} | MUST/SHOULD/COULD/WONT |

Se não for apropriada: `Gamification decision: Not recommended because {reason}.`

## Lentes cognitivas (não bloqueiam)

> Lente nunca gera MUST, nunca rebaixa uma regra e não entra no cálculo do resultado (`READY/BLOCKED FOR DESIGN`). Todo status diferente de `N.A.` exige evidência. Status: `OK` · `RECOMENDAÇÃO` (SHOULD ou COULD) · `ALERTA` · `N.A.`; lentes `N.A.` podem ir juntas numa linha, com o motivo. A linha Interrupção → Retomada da jornada é análise, não estado obrigatório.

| Lente | Status | Evidência |
|---|---|---|
| Alcance (Fitts) | OK / RECOMENDAÇÃO / ALERTA / N.A. | {EVIDENCE} |
| Escolhas por passo (Hick-Hyman) | {STATUS} | {EVIDENCE} |
| Retomada (Zeigarnik) | {STATUS} | {EVIDENCE} |
| Convenção (Jakob) | {STATUS} | {EVIDENCE} |
| Progresso real (Gradiente de meta) | {STATUS} | {EVIDENCE} |
| Destaque único (Von Restorff) | {STATUS} | {EVIDENCE} |
| Agrupamento (Miller) | {STATUS} | {EVIDENCE} |
| Sinal de validação real | {STATUS} | {METRIC_TO_WATCH_AFTER_DELIVERY} |

## Design Handoff

### UX requirements
- {REQUIREMENT}

### Components likely needed
- {COMPONENT}

### State requirements
- {STATE_REQUIREMENT}

### Copy guidance
- {COPY_REQUIREMENT}

### Visual guidance
- {VISUAL_REQUIREMENT_FROM_UX_STANDARD}

### Accessibility/responsiveness
- {A11Y_RESP_REQUIREMENT}

### Cognitive lenses
- (lente {Lx}) {SHOULD_OR_COULD_RECOMMENDATION}
- Como medir depois: {VALIDATION_SIGNAL}

### Acceptance notes
- [ ] {ACCEPTANCE_NOTE}

## Canonical Evolution Proposals

Apenas sugestões. Não editar `UX_STANDARD.md` neste fluxo.

| Regra afetada/nova | Problema observado | Mudança proposta | Motivo | Bloqueia esta feature? |
|---|---|---|---|---|
| {UX-ID_OR_NEW} | {ISSUE} | {PROPOSAL} | {WHY} | Yes/No |

## Gate Outcome

**Resultado:** READY FOR DESIGN / BLOCKED FOR DESIGN

**MUST abertos:** {COUNT}

**MUST aceitos explicitamente como exceção:** {COUNT}

**Lentes cognitivas:** {N} RECOMENDAÇÃO · {M} ALERTA — não mudam o resultado.

Regra: qualquer MUST não resolvido ou não aceito explicitamente mantém `BLOCKED FOR DESIGN`.

## Open UX Questions

- {QUESTION}

Se nenhuma: `None - ready for Design.`

## Revision History

| Versão | Data | Autor | Mudanças |
|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | ux-review | Initial UX review |

## Next Step

Se `READY FOR DESIGN`: executar o Design usando esta revisão como handoff.

Se `BLOCKED FOR DESIGN`: resolver ou aceitar explicitamente os MUST antes do Design.
