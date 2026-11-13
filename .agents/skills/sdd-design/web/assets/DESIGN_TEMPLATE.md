# DESIGN: {Feature Name}

> Technical design for implementing {Feature Name}

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `{BRAINSTORM_FILE}` |
| **DEFINE** | `{DEFINE_FILE}` |
| **UX REVIEW** | `{UX_REVIEW_FILE or N/A}` |
| **LLM Prompts** | {true / false} |
| **Status** | {Draft / Needs Clarification / Ready for Build} |

---

## Architecture Overview

```text
{ASCII architecture diagram}
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| {component} | {responsibility} | {stack/pattern} | {inputs} | {outputs} | {dependencies} |

---

## Key Decisions

### Decision 1: {Decision Name}

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | {YYYY-MM-DD} |
| **Source** | {DEFINE / UX Review / technical clarification / project evidence} |

**Context:** {why this decision is needed}

**Choice:** {what will be done}

**Rationale:** {why this choice fits the requirements and project}

**Alternatives Rejected:**
1. {alternative} — {reason}
2. {alternative or N/A} — {reason}

**Consequences:**
- {trade-off accepted}
- {benefit gained}

{Repeat only for significant decisions.}

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `{real/path}` | Create / Modify / Delete | {purpose} | {agent or (general)} | None |
| 2 | `{real/path}` | Create / Modify / Delete | {purpose} | {agent or (general)} | 1 |

**Total Files:** {N}

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| {agent or (general)} | {manifest ids} | {evidence-based rationale} |

**Agent Discovery:** {scanned source and matching rule, or `Not available`}

---

## Code Patterns

### Pattern 1: {Pattern Name}

```{language}
{copy-paste-ready pattern, not full implementation}
```

### Pattern 2: {Pattern Name or N/A}

```{language}
{pattern or omit section when genuinely unnecessary}
```

---

{INSERT `## LLM Prompts` HERE ONLY WHEN LLM Prompts=true, following references/llm-prompts.md}

## Data Flow

```text
1. {step}
   │
   ▼
2. {step}
   │
   ▼
3. {step}
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| {system or None} | {REST / SDK / Queue / DB / N/A} | {method / N/A} | {in/out/bidirectional} | {behavior} |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit | {scope} | `{path}` | {tool} | {objective signal} |
| Integration | {scope} | `{path}` | {tool} | {objective signal} |
| E2E / Verify Gate | {scope} | `{path or N/A}` | {tool/method} | {signal from DEFINE} |

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| {error} | {signal} | {handling} | Yes / No / N/A | {log/metric/trace} |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `{key or N/A}` | {type} | {source/default} | Yes / No | {purpose} |

---

## Security Considerations

- {specific consideration and mitigation}
- {specific consideration and mitigation}
- {additional item or N/A}

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | {approach} | {what it diagnoses} |
| Metrics | {approach} | {what it measures} |
| Tracing | {approach or N/A} | {what it follows} |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| {MUST / AT-001} | {component/decision/file} | {test/gate} |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| {risk} | {impact} | {mitigation} | {residual} |

---

## Advisor Ledger

{Use only if a formal external design review occurred. Otherwise: `None — no formal external design review.`}

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | SDD Design by RDD | Initial version |

---

## Next Step

Execute o **SDD Build by RDD**.
