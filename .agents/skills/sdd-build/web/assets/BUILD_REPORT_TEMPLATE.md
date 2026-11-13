# BUILD REPORT: {Feature Name}

> Implementation report for {Feature Name}

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | {FEATURE_NAME} |
| **Date** | {YYYY-MM-DD} |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `{BRAINSTORM_FILE}` |
| **DEFINE** | `{DEFINE_FILE}` |
| **DESIGN** | `{DESIGN_FILE}` |
| **Status** | {In Progress / Complete / Blocked} |

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | {N} |
| Cross-file coupling | {Low / Medium / High + evidence} |
| Security surface | {None / details} |
| LLM prompt items | {None / details} |
| Independent volume | {observation} |
| Context-rot risk | {observation} |
| Runtime capabilities | {default / ralph / briefs availability} |

**Recommendation:** {mode + concrete rationale}

**User decision:** {mode chosen}

**Pre-build review:** {Yes + receipt/ledger reference / No + reason / Not available}

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | {X}/{Y} |
| **Files Created** | {N} |
| **Files Modified** | {N} |
| **Files Deleted** | {N} |
| **Verification Commands Run** | {N} |
| **Verify Gate** | {Green / Manual receipt / Red / Inconclusive / Blocked} |
| **Execution Mode** | {default / ralph / briefs} |

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | {id} | {action + path} | {direct / agent / worker} | {Complete / Blocked} | `{command}` | {exit/result} |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `{path}` | {Create / Modify / Delete} | {id} | {Yes / No} | {notes} |

---

{INSERT `## Migrations aplicadas` HERE ONLY WHEN Files Changed lists *.sql or migrations/ — one row per migration; "já aplicada em <data>" counts as applied}

## Migrations aplicadas

| Arquivo | Projeto (nome · ref) | Aplicada em | Prova por leitura |
|---|---|---|---|
| `{path/to/migration.sql}` | {nome} · `{ref}` | {YYYY-MM-DD HH:MM (cli / mcp / manual) ou "já aplicada em …"} | {migration list: Remote ✓ · select em information_schema: … ✓ — ou "(b) entregue para o SQL Editor"} |

---

{INSERT `## Prompts Generated / Refactored` HERE ONLY WHEN LLM Prompts=true OR DRIFT WAS DETECTED}

## Drift Detected

{`No drift detected.` OR a table below}

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `{path}` | {description} | {false positive / revise spec / approved deviation} | {action} |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| {task} | `{command}` | {Pass / Fail} | {output summary} |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | {test / smoke / eval / typecheck / manual-ux} |
| **Command / Method** | `{cmd or manual checklist}` |
| **Exit / Result** | {exit code of the cmd (or runner) / human result} |
| **Status** | {Green / Red / Inconclusive / Manual receipt / Clarification pending / Invalid} |
| **Evidence** | {output or receipt reference} |

### Manual UX Receipt

{Use only for manual-ux. Otherwise `N/A`.}

| Attribute | Value |
|---|---|
| Validator | {name} |
| Date | {YYYY-MM-DD} |
| Result | {Pass / Fail} |
| Notes | {notes} |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `{command or N/A}` | {Pass / Fail / N/A} | {evidence} |
| Typecheck | `{command or N/A}` | {Pass / Fail / N/A} | {evidence} |
| Tests | `{command or N/A}` | {Pass / Fail / N/A} | {evidence} |
| Build / Compile | `{command or N/A}` | {Pass / Fail / N/A} | {evidence} |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | {from DEFINE} | {Pass / Fail / Blocked} | {command/test/result} |

---

## Advisor Ledger

{If no formal review: `None — no formal external review was executed.`}

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | {pre-build / post-build / conflict} | {note} | {HIGH / MEDIUM / LOW} | {APPLIED / REBUTTED} | {evidence/reason} |

---

## Issues Encountered

{`None.` OR table}

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | {issue} | {resolution} | {impact} |

---

## Deviations from Design

{`None.` OR table. Material architecture/spec drift should not be hidden here; it must have been resolved before continuing.}

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| {deviation} | {decision} | {reason} | {impact} |

---

## Blockers

{`None.` when Complete. For Blocked status, list every unresolved blocker.}

| Blocker | Required Action | Owner |
|---|---|---|
| {blocker} | {action} | {owner} |

---

## Final Status

### Overall: {COMPLETE / IN PROGRESS / BLOCKED}

- [ ] All File Manifest tasks completed
- [ ] Incremental verification recorded
- [ ] Verify Gate green or manual-ux receipt positive
- [ ] Complementary checks applicable pass
- [ ] Acceptance Tests verified
- [ ] LLM prompt receipts complete when required
- [ ] Drift decisions recorded
- [ ] Advisor findings disposed when applicable
- [ ] No unresolved blocker
- [ ] No TODO/FIXME used as unfinished implementation

---

{INCLUDE THE SECTION BELOW ONLY WHEN Overall=COMPLETE}

## Next Step

Execute o **SDD Handoff by RDD**.
