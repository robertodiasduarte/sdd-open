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
| **Lentes** | {N} recomendações · {M} alertas — não mudam o Status |

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
| Interrupção → Retomada | {Sair no meio preserva o que foi feito? Como a pessoa volta?} | {Emotion or risk} | {Autosave, "continuar", o que falta} |
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

**Teste do suporte:** {Algum estado dispara pergunta "isso é bug?" ou "como faço X?" no atendimento? Se sim, listar e marcar como MUST.}

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
[ ] Contraste MEDIDO nos pares reais (texto/fundo, acento/fundo) com sdd/bin/contraste.sh: ≥4.5:1 texto, ≥3:1 não-texto — listar os valores
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

> WCAG 2.2 AA. Sem superfície visual (linha de comando, arquivo gerado, serviço): escreva `N.A. — <motivo>`
> em 1 linha, no lugar da tabela. Com tela, preencha as 7 linhas. Veredito: `PASSA`, `REPROVA` ou `N.A.`, com
> motivo. Todo `REPROVA` vira 1 MUST em UX/CX Findings, com o critério e o par medido. Contraste medido com
> `bash sdd/bin/contraste.sh '<fg>' '<bg>' [alpha] [--piso 3]`, nos pares reais; projeto com 2 temas mede os 2,
> porque o número de um não transfere ao outro. As 2 linhas herdadas só se provam na tela pronta: vão para as
> Acceptance notes, sem veredito aqui.

| SC | Nível | Verificação | Evidência | Veredito |
|----|-------|-------------|-----------|----------|
| 1.4.3 | AA | Texto ≥4,5:1 (≥3:1 se ≥24 px, ou ≥18,66 px em negrito) | `#rrggbb sobre #rrggbb → N.NN:1`, por par e por tema | PASSA / REPROVA / N.A. |
| 1.4.11 | AA | Borda de controle, ícone e anel de foco ≥3:1 contra o fundo adjacente | `#rrggbb sobre #rrggbb → N.NN:1` | PASSA / REPROVA / N.A. |
| 1.4.1 | A | Estado dito também por texto, ícone ou posição, nunca só por cor | sinais listados | PASSA / REPROVA / N.A. |
| 2.4.7 | AA | Foco visível em todo controle | onde o foco aparece | PASSA / REPROVA / N.A. |
| 4.1.2 | A | Nome, papel e valor por controle (`aria-*`, `role`, `<label>`) | controle → atributo | PASSA / REPROVA / N.A. |
| 2.1.1 | A | Tab alcança e aciona todo controle, sem armadilha de foco | herdado → Acceptance notes | — |
| 2.5.8 | AA | Alvo ≥24×24 px; 44×44 px recomendado no mobile | herdado → Acceptance notes | — |

3.3.7 é nível A e 2.4.13 é AAA: não entram aqui, e nenhum dos 2 é critério AA.

### Responsiveness

| Concern | Requirement |
|---------|-------------|
| Mobile | {Layout, touch target, truncation, long content} |
| Long content | {Texto longo, listas grandes, dados parciais} |

---

## Lentes cognitivas (não bloqueiam)

> Lente nunca gera MUST, nunca rebaixa uma regra e não entra no cálculo do resultado (`Ready for Design`). Todo status diferente de `N.A.` exige evidência. Status: `OK` · `RECOMENDAÇÃO` (SHOULD ou COULD) · `ALERTA` · `N.A.`; lentes `N.A.` podem ir juntas numa linha, com o motivo. A linha Interrupção → Retomada da jornada é análise, não estado obrigatório.

| Lente | Status | Evidência |
|-------|--------|-----------|
| Alcance (Fitts) | OK / RECOMENDAÇÃO / ALERTA / N.A. | {Evidência} |
| Escolhas por passo (Hick-Hyman) | {Status} | {Evidência} |
| Retomada (Zeigarnik) | {Status} | {Evidência} |
| Convenção (Jakob) | {Status} | {Evidência} |
| Progresso real (Gradiente de meta) | {Status} | {Evidência} |
| Destaque único (Von Restorff) | {Status} | {Evidência} |
| Agrupamento (Miller) | {Status} | {Evidência} |
| Sinal de validação real | {Status} | {Métrica a observar depois da entrega} |

---

## Design Handoff

Concrete requirements for `/design`:

- {Requirement 1}
- {Requirement 2}
- {Requirement 3}
- {Gamification requirement or explicit reason not to include gamification}
- (lente {Lx}) {Recomendação SHOULD ou COULD de lente}
- Como medir depois: {sinal de validação real}

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
- [ ] **Self-Evident**: zero tooltip-muleta, zero helper text óbvio, zero cor conflitando com semântica — teste do estranho e teste do suporte aprovados
- [ ] 2.1.1 (herdado da tabela WCAG): Tab alcança e aciona todo controle, sem armadilha de foco — provado no relatório do Build
- [ ] 2.5.8 (herdado da tabela WCAG): alvo ≥24×24 px, 44×44 px recomendado no mobile — medido no relatório do Build

---

## Open UX Questions

- {Question 1}
- {Question 2}

If none, state: `None - ready for Design.`

Se o papel de alguma surface (destaque, operacional, sobreposição) não estiver claro, registre aqui a pergunta para o responsável. **Papel em aberto trava o Design:** o `sdd-design` pergunta antes de escrever, e não decide sozinho.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | ux-review-command | Initial UX review |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_{FEATURE_NAME}.md`
