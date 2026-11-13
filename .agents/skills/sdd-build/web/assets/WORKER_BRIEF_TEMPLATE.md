## SUBTASK

{one line: action + exact file, copied from File Manifest}

## INPUTS

- Design contract: {relevant design excerpt}
- Current file/import context: {inline contents or concise exact excerpts}
- Applicable project conventions: {rules}
- CLOSED DECISIONS: {names, routes, schemas, provider/model, contracts that must not be reopened}

## ACCEPTANCE CRITERIA

1. {functional criterion for this item}
2. Verification passes: `{real command}`
3. No file outside `{exact path}` is modified by this worker.

## OUTPUT FORMAT

- Write only to `{exact path}`.
- No TODOs or speculative improvements.
- If an input is missing/contradictory, prefix result with `INPUT GAP: {one line}`.
- Return concise status + verification evidence.

## GUIDELINES

- Surgical change only.
- No speculative abstraction.
- Preserve existing style.
- Evidence before Complete.
