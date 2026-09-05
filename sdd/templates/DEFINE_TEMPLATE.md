# DEFINE: {Feature Name}

> One-sentence description of what we're building

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | {author} |
| **Status** | {Draft / In Progress / Needs Clarification / Ready for Design} |
| **Clarity Score** | {X}/15 |

---

## Problem Statement

{1-2 sentences describing the pain point we're solving. Be specific about who has the problem and what the impact is.}

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| {User 1} | {Their role} | {What frustrates them} |
| {User 2} | {Their role} | {What frustrates them} |

---

## Goals

What success looks like (prioritized):

| Priority | Goal |
|----------|------|
| **MUST** | {Primary goal - non-negotiable for MVP} |
| **MUST** | {Another critical goal} |
| **SHOULD** | {Important but can defer if timeline tight} |
| **COULD** | {Nice-to-have if time permits} |

**Priority Guide:**
- **MUST** = MVP fails without this
- **SHOULD** = Important, but workaround exists
- **COULD** = Nice-to-have, cut first if needed

---

## Success Criteria

Measurable outcomes (must include numbers):

- [ ] {Metric 1: e.g., "Handle 1000 requests per minute"}
- [ ] {Metric 2: e.g., "Achieve 99.9% uptime"}
- [ ] {Metric 3: e.g., "Response time under 200ms"}

---

## Acceptance Tests

> Gramática **EARS** obrigatória em DEFINE novo/retocado (keywords em inglês, corpo em PT-BR) —
> padrões, exemplos e mapa padrão→`kind` de gate em
> [`fragments/EARS.md`](fragments/EARS.md). Regras que o `/define` recusa se faltarem:
> ≥1 AT **If/Then** (unwanted) quando houver gatilho indesejado plausível; padrões
> **While/If-Then/Where** considerados (AT presente ou N.A. justificado — estado não lido ·
> erro silencioso · flag de config são as 3 classes que mais mordem); em **bugfix**,
> ≥1 cláusula **shall continue to** (não-regressão). Máx ~10 ATs. Cada AT mapeia no
> `## Verify Gate` pela coluna `Gate (kind)`. ⛔ UX visual NÃO vira AT EARS (é `manual-ux`).

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** {trigger}, the system **shall** {response} | test |
| AT-002 | Unwanted | **If** {gatilho indesejado}, **then** the system **shall** {tratamento} | test/smoke negativo |
| AT-003 | State-driven | **While** {estado}, the system **shall** {response} | test |
| AT-00N | Non-regression (bugfix) | The system **shall continue to** {comportamento existente} | test |

---

## Clarifications

> **Regra de honestidade:** ambiguidade não vira suposição — vira marcador ativo no lugar
> exato da dúvida, na forma canônica abaixo (protocolo completo, 9 categorias e convenção de
> menção em [`fragments/CLARIFY.md`](fragments/CLARIFY.md)):
>
> ```
> [NEEDS CLARIFICATION: <pergunta específica>]
> ```
>
> Enquanto houver marcador ativo, `sdd/bin/verify-gate.sh` devolve **exit 5** e
> `/build`/a fase Release/`/drive` param. Resolver via AskUserQuestion (≤5 por rodada),
> integrar a resposta NO CORPO da spec e logar abaixo.

### Session {YYYY-MM-DD}

- [x] ({categoria}) {pergunta} → {resposta}; integrado em {seção}

---

## Verify Gate

> **Gate executável de aceite (pass/fail).** `/build` (Step 5) e a fase Release (Fase 0a) rodam isto via
> `sdd/bin/verify-gate.sh` e tratam como **BLOQUEANTE** — não é prosa, é comando.
> Habilitador da F1 (loop engineering): o critério de parada de qualquer loop.
> Taxonomia completa: [`fragments/VERIFY_GATE.md`](fragments/VERIFY_GATE.md).

```yaml
verify_gate:
  kind: test
  cmd: "npm test -- src/{modulo}.test.ts"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

**Preencher exatamente um bloco** (substitua o exemplo acima pelo gate real da feature):

- `kind`: `test` | `smoke` | `eval` | `typecheck` | `manual-ux`
- `cmd`: comando executável; em `manual-ux` use `"N/A (manual-ux)"`
- `pass_when`: `exit 0` (default) | `exit N` | `contains: TEXTO`
- `threshold`: só `eval` (ex.: `"recall >= 0.80"` — limiar embutido no `cmd`)
- `manual_fallback`: só `manual-ux` — checklist humano assinado no BUILD_REPORT

**Regras:** `manual-ux` é gate HUMANO (não finge automação). Smoke 403 do WAF×runner =
inconclusivo, não vermelho (rode na origem via SSH). Nenhum gate cruza o a fase Release.

Rodar localmente: `sdd/bin/verify-gate.sh sdd/features/DEFINE_{FEATURE_NAME}.md`

---

## Out of Scope

Explicitly NOT included in this feature:

- {Item 1: What we're NOT doing}
- {Item 2: What's deferred to future}
- {Item 3: What's explicitly excluded}

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | {e.g., "Must use existing database schema"} | {How this affects design} |
| Timeline | {e.g., "Must ship by Q1"} | {How this affects scope} |
| Resource | {e.g., "No additional infrastructure budget"} | {How this affects approach} |

---

## Technical Context

> Essential context for Design phase - prevents misplaced files and missed infrastructure needs.

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | {src/ \| functions/ \| gen/ \| deploy/ \| custom path} | {Why this location} |
| **KB Domains** | {bases de conhecimento do projeto a consultar (nomes de pasta em `sdd/kb/` ou equivalente), ou `nenhum` explícito} | {Which patterns to consult} |
| **IaC Impact** | {New resources \| Modify existing \| None \| TBD} | {Terraform/Terragrunt changes needed} |
| **LLM Prompts** | {true \| false} | {Set true se a feature cria/edita prompts runtime — system prompts, passes de pipeline, classificadores. Quando true, a fase Design inventaria cada prompt e a fase Build trata cada um como entregável com contrato próprio.} |
| **CONTEXTO de domínio** | {contexto/<slug>.md · sha <7 hex> · válido em <YYYY-MM-DD> \| nenhum (motivo)} | {Gerado/reusado/pulado no Step 1.5 do /define (mapa do domínio gerado em contexto limpo — slice 2 do SDD Open); a fase Design lê e grepa o `sup:` dele} |

**Why This Matters:**

- **Location** → Design phase uses correct project structure, prevents misplaced files
- **KB Domains** → a fase Design puxa os padrões certos da base de conhecimento do projeto
- **IaC Impact** → Triggers infrastructure planning, avoids "works locally" failures
- **LLM Prompts** → Gate condicional para a etapa de engenharia de prompts; evita overhead em features sem LLM
- **CONTEXTO de domínio** → o DESIGN nasce sabendo tabelas/RPCs/edges/regras vigentes do domínio (`arquivo:linha`), não inferindo do input; válido enquanto `git diff <sha>..origin/main -- <superfícies>` for vazio

**LLM Prompts — gatilhos para marcar `true`:**

A feature provavelmente envolve prompts runtime se aparecer qualquer um dos sinais abaixo (literal no texto da feature ou inferido do escopo):

- Palavras: `LLM`, `GPT`, `Claude`, `Anthropic`, `OpenAI`, `Gemini`, `Vercel AI`
- Conceitos: `system prompt`, `user prompt`, `prompt`, `embeddings`, `RAG`, `vector search`, `completion`, `classificador`, `sintetizador`, `pass de pipeline`
- Paths: `**/prompts/**`, arquivos de template de prompt, código que chama `messages.create` / `chat.completions`
- Atores do produto que conversam com o usuário ou classificam texto (chatbot, assistente, indexador)

Em dúvida, marcar `true` e justificar em **Notes**. Reverter para `false` durante a fase Design só se a heurística confirmar que nenhum arquivo do manifest contém prompt runtime.

---

## Assumptions

Assumptions that if wrong could invalidate the design:

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | {e.g., "Database can handle expected load"} | {Would need caching layer} | [ ] |
| A-002 | {e.g., "Request volume stays under 1000/hour"} | {Would need rate limiting} | [ ] |
| A-003 | {e.g., "Users have modern browsers"} | {Would need polyfills for legacy support} | [ ] |

**Note:** Validate critical assumptions before DESIGN phase. Unvalidated assumptions become risks.

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | {0-3} | {Why this score} |
| Users | {0-3} | {Why this score} |
| Goals | {0-3} | {Why this score} |
| Success | {0-3} | {Why this score} |
| Scope | {0-3} | {Why this score} |
| **Total** | **{X}/15** | |

**Scoring Guide:**
- 0 = Missing entirely
- 1 = Vague or incomplete
- 2 = Clear but missing details
- 3 = Crystal clear, actionable

**Minimum to proceed: 12/15**

---

## Open Questions

{List any remaining questions that need answers before Design phase. If none, state "None - ready for Design."}

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {YYYY-MM-DD} | define-agent | Initial version |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_{FEATURE_NAME}.md`
