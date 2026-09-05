# UX REVIEW: {Feature Name}

> UX/CX review for `{FEATURE_NAME}` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | ux-review-command |
| **DEFINE** | [DEFINE_{FEATURE}.md](../features/DEFINE_{FEATURE}.md) |
| **Status** | Draft / Ready for Design / Needs Requirement Iteration |

---

## UX Summary

{2-4 sentences summarizing the experience goal, main user risk, and strongest recommendation.}

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | {Persona or role} |
| **User Goal** | {What they need to accomplish} |
| **Primary Pain** | {What currently frustrates or blocks them} |
| **Business/CX Goal** | {Trust, conversion, retention, support reduction, speed, clarity} |
| **Device/Context** | {Desktop/mobile/tablet, internal/external, urgent/calm, repeated/one-time} |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | {What happens before feature use} | {Emotion or risk} | {Expectation setting} |
| Entry | {How user enters} | {Emotion or risk} | {Navigation, CTA, context} |
| Core Action | {Primary task} | {Emotion or risk} | {Form, flow, controls} |
| Feedback | {What user needs to know} | {Emotion or risk} | {Status, validation, confirmation} |
| Recovery | {What happens when something fails} | {Emotion or risk} | {Error, retry, support, undo} |
| Completion | {How success is understood} | {Emotion or risk} | {Success message, next step} |
| Follow-up | {What happens after} | {Emotion or risk} | {Notification, history, support path} |

---

## UX/CX Findings

| Priority | Area | Finding | Recommendation |
|----------|------|---------|----------------|
| MUST | {Clarity/Efficiency/Confidence/Premium/Self-Evident/etc.} | {Issue or risk} | {What to change} |
| SHOULD | {Area} | {Issue or opportunity} | {What to change} |
| COULD | {Area} | {Nice-to-have} | {What to change} |
| WONT | {Area} | {Good idea excluded from this feature} | {Why excluded} |

---

## North Star Checks (Premium + Self-Evident)

Verificação explícita dos 2 princípios inviolaveis. Qualquer violação = MUST automático.

### Premium (padrão de qualidade percebida)

| Dimensão | Status | Evidência / Risco |
|----------|--------|-------------------|
| Hierarquia visual em 200ms | ✅ / ⚠️ / ❌ | {O olho sabe onde pousar primeiro?} |
| Densidade calibrada (respira) | ✅ / ⚠️ / ❌ | {Não parece "tela admin amontoada"?} |
| Tipografia com propósito (≤3 sizes/surface) | ✅ / ⚠️ / ❌ | {Pesos e tamanhos justificados?} |
| Movimento curto (150-250ms ease-out) | ✅ / ⚠️ / ❌ | {Zero bounces decorativos?} |
| Microinterações completas (hover/focus/active/disabled) | ✅ / ⚠️ / ❌ | {Nenhum estado esquecido?} |
| Surfaces do design system do projeto (quando houver) | ✅ / ⚠️ / ❌ | {Zero "card branco genérico"; cada surface tem papel semântico?} |
| Estados vazios como delight, não placeholder | ✅ / ⚠️ / ❌ | {Empty é oportunidade, não vergonha?} |
| Acabamento "shipada", não "MVP a polir" | ✅ / ⚠️ / ❌ | {Sensação de produto pronto?} |

### Self-Evident / Zero-Explanation

| Anti-padrão | Está presente? | Onde / como remover |
|-------------|----------------|---------------------|
| Tooltip-muleta (affordance só funciona com tooltip) | ❌ Sim / ✅ Não | {Surface e plano de refazer affordance} |
| Helper text explicando o óbvio | ❌ Sim / ✅ Não | {Texto e plano de remover} |
| Estado ambíguo (foi salvo/enviado/pendente?) | ❌ Sim / ✅ Não | {Surface e plano de tornar inequívoco} |
| Cor conflitando com semântica (rascunho em verde, etc) | ❌ Sim / ✅ Não | {Onde e qual a cor correta} |
| Onboarding/tour obrigatório | ❌ Sim / ✅ Não | {Por que removível} |
| Documentação como contrato de UX | ❌ Sim / ✅ Não | {Mover regra pra UI} |

**Teste do estranho:** {Resultado mental — usuário virgem completa a tarefa em silêncio? Onde hesitaria?}

**Teste do WhatsApp:** {Algum estado dispara pergunta "isso é bug?" ou "como faço X?" no atendimento? Se sim, listar e marcar como MUST.}

---

## Gamification Strategy

Use gamification whenever it can improve motivation, progress clarity, learning, completion, or confidence without manipulation.

| Opportunity | Recommended Mechanic | User Value | Guardrail | Priority |
|-------------|----------------------|------------|-----------|----------|
| {Where gamification could help} | {Progress/Milestone/Badge/Streak/Level/Challenge/Feedback/None} | {Why it helps the user} | {How to avoid pressure, shame, clutter, or dark patterns} | MUST/SHOULD/COULD/WONT |

If gamification is not appropriate, state why:

```text
Gamification decision: Not recommended because {reason}.
```

---

## 60/30/10 Visual Strategy

> Regra de atenção: **60%** da tela é fundo dominante (reduz carga cognitiva), **30%** são
> surfaces secundárias (destaque × operacional × sobreposição) e **10%** é acento — o que aponta
> para a próxima ação significativa. Se o projeto tem design system, **cite os tokens dele**; se
> não tem, proponha os 3 papéis abaixo e registre como candidato a design system.

| Share | Papel | Token do projeto (se houver) | UX Rationale |
|-------|-------|------------------------------|--------------|
| **60% Dominant** | fundo da viewport | `{--bg}` | reduz carga cognitiva; nunca compete com o conteúdo |
| **30% Secondary — destaque** | surfaces aspiracionais ({listar quais}) | `{--surface-hero}` | 1ª impressão, próxima ação, progresso |
| **30% Secondary — operacional** | listas longas, tabelas, painéis densos ({listar quais}) | `{--surface-neutral}` | denso e sóbrio; container tem cor, itens são flat |
| **30% Fallback** | modais, popovers, tooltips | `{--bg-card}` | sobreposição sem voz própria |
| **10% Accent** | CTA primário, link ativo, status | `{--accent}`, status | sinais semânticos; **não** propor hue novo por feature |

**Color Guardrails:**

```text
[ ] Cada surface proposta tem papel atribuído (destaque / operacional / sobreposição) com justificativa
[ ] CTA primário é UM só por tela e usa o token de CTA do projeto — nunca uma cor inventada para a feature
[ ] Telas operacionais (admin, gestão, listas longas) NUNCA usam surface de destaque
[ ] Status (sucesso/aviso/erro) preservam a semântica universal: rascunho NUNCA verde+✅, erro NUNCA verde
[ ] Contraste MEDIDO nos pares reais (texto/fundo, acento/fundo): ≥4.5:1 texto, ≥3:1 não-texto — listar os valores
[ ] Significado nunca depende só de cor (ícone + texto + cor — 3 sinais)
```

---

## Surface Assignment

Cada surface UI proposta nesta feature recebe um papel. Se o projeto tem matriz de surfaces
canônica, consulte-a e registre se a surface é nova ou reuso.

| Surface (funcional) | Papel | Justificativa | Nova no design system? |
|---------------------|-------|---------------|------------------------|
| {Nome da surface, ex: "Hero do dashboard"} | destaque / operacional / sobreposição | {Aspiracional? Operacional? Sobreposição?} | Sim / Não (reuso) |
| ... | ... | ... | ... |

**Regras a respeitar:**

- ✅ CTAs em surface de destaque usam o token de CTA-sobre-destaque do projeto, nunca o acento cru
- ✅ Telas de gestão/admin são sempre operacionais, nunca destaque
- ✅ Modais/popovers/tooltips usam a surface de sobreposição
- ✅ Listas longas: cor só no container; itens flat
- ✅ Acentos e cores de status do projeto são intocáveis

---

## Interaction Requirements

| Requirement | Why It Matters | Priority |
|-------------|----------------|----------|
| {Interaction requirement} | {User/CX reason} | MUST/SHOULD/COULD |
| {Gamification requirement or explicit skip} | {Motivation/progress reason or why not applicable} | MUST/SHOULD/COULD/WONT |

---

## Required States

| State | Required UX |
|-------|-------------|
| Loading | {Skeleton, spinner, progress, expected wait copy} |
| Empty | {What user sees before data exists} |
| Error | {Readable error, recovery path, retry/support} |
| Success | {Confirmation and next step} |
| Partial Data | {How incomplete data is shown} |
| Permission Denied | {Access explanation and next action} |
| Disabled | {Why unavailable and how to enable} |

---

## Content and Copy Guidance

| Surface | Guidance |
|---------|----------|
| Primary CTA | {Verb-first, user outcome, concise} |
| Helper Text | {What uncertainty to resolve} |
| Error Copy | {Specific, human, actionable} |
| Confirmation | {What happened and what user can do next} |
| Empty State | {Explain value and first action} |

---

## Accessibility and Responsiveness

| Concern | Requirement |
|---------|-------------|
| Keyboard | {Focus order, shortcuts, escape behavior} |
| Contrast (**medir nos pares reais**, no tema padrão primeiro) | Texto sobre fundo ≥4.5:1 (AA); acento sobre fundo ≥4.5:1 quando é texto/link; badges e bordas ≥3:1 (não-texto). Se o projeto tem 2 temas, cada um é um design system completo: número de um NÃO transfere para o outro. Medir via DevTools/calculadora de contraste — listar os valores na resposta. |
| Screen Reader | {Labels, roles, announcements} |
| Mobile | {Layout, touch target, truncation, long content} |
| Non-color Cues | {Icons, text, shape, position} |

---

## Design Handoff

Concrete requirements for `/design`:

- {Requirement 1}
- {Requirement 2}
- {Requirement 3}
- {Gamification requirement or explicit reason not to include gamification}

Components likely needed:

- {Component 1}
- {Component 2}
- {Component 3}

Acceptance notes:

- [ ] {UX acceptance note}
- [ ] {CX acceptance note}
- [ ] {60/30/10 visual hierarchy note}
- [ ] {Gamification acceptance note or explicit skip rationale}
- [ ] **Premium**: cada estado (loading/empty/error/success/disabled) tem acabamento "shipada", não "MVP a polir"
- [ ] **Self-Evident**: zero tooltip-muleta, zero helper text óbvio, zero cor conflitando com semântica — teste do estranho e teste do WhatsApp aprovados

---

## Open UX Questions

- {Question 1}
- {Question 2}

If none, state: `None - ready for Design.`

**Trigger especial:** se você NÃO consegue determinar o bucket de alguma surface proposta, listar aqui — essa pergunta DEVE bloquear o avanço para /design até ser resolvida (não passar a decisão pra /design):

- "Surface X: hero (aspiracional) ou neutral (operacional)? Pendente decisão do humano responsável."

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | ux-review-command | Initial UX review |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_{FEATURE_NAME}.md`
