# DEFINE: {Feature Name}

> {One-sentence description}

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | {author} |
| **Status** | {Draft / In Progress / Needs Clarification / Ready for Design} |
| **Clarity Score** | {X}/15 |

---

## Problem Statement

{Specific pain point, affected user and impact in 1–2 sentences.}

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| {User 1} | {Role} | {Pain point} |
| {User 2 or N/A} | {Role or N/A} | {Pain point or N/A} |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | {Non-negotiable MVP goal} |
| **MUST** | {Another critical goal if applicable} |
| **SHOULD** | {Important but deferrable goal} |
| **COULD** | {Nice-to-have, cut first} |

---

## Success Criteria

- [ ] {Measurable criterion with numeric/observable target}
- [ ] {Measurable criterion with numeric/observable target}
- [ ] {Additional criterion if applicable}

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** {trigger}, the system **shall** {response} | test |
| AT-002 | Unwanted | **If** {undesired trigger}, **then** the system **shall** {handling} | test / smoke |
| AT-003 | State-driven | **While** {state}, the system **shall** {response} | test |
| AT-00N | Non-regression (bugfix only) | The system **shall continue to** {existing behavior} | test |

Remove rows that are not applicable, except that an Unwanted row is required whenever a plausible undesired trigger exists and a Non-regression row is required for bugfixes.

---

## Clarifications

### Session {YYYY-MM-DD}

- [x] ({category}) {question} → {answer}; integrated into {section}

If no clarification was necessary, write:
`None — Brainstorm supplied sufficient validated detail.`

---

## Verify Gate

```yaml
verify_gate:
  kind: {test | smoke | eval | typecheck | manual-ux}
  cmd: "{real executable command, or N/A (manual-ux)}"
  pass_when: "{exit 0 | exit N | contains: TEXT | checklist signed}"
  threshold: "{numeric eval target or —}"
  manual_fallback: "{human checklist for manual-ux or —}"
```

---

## Out of Scope

- {Explicit exclusion}
- {Deferred item}
- {Additional exclusion if applicable}

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | {constraint or N/A} | {impact} |
| Timeline | {constraint or N/A} | {impact} |
| Resource | {constraint or N/A} | {impact} |
| Other | {constraint or N/A} | {impact} |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | {path / layer / TBD} | {reason or limitation} |
| **KB Domains** | {domains / N/A} | {patterns to consult} |
| **IaC Impact** | {New resources / Modify existing / None / TBD} | {impact} |
| **LLM Prompts** | {true / false} | {justification} |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | {assumption or None} | {impact} | {yes/no} |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | {0-3} | {reason} |
| Users | {0-3} | {reason} |
| Goals | {0-3} | {reason} |
| Success | {0-3} | {reason} |
| Scope | {0-3} | {reason} |
| **Total** | **{X}/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

{Only non-blocking questions. If none: `None - ready for Design.`}

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | {YYYY-MM-DD} | SDD Define by RDD | Initial version |

---

## Next Step

Execute o **SDD Design by RDD**.
