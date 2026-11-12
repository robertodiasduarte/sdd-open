<!-- Language: **English** · [Português](pt-BR/context-and-governance.md) -->

# Context and governance

Since v2.4.0, `sdd-define` runs two reviews by a **fresh agent** — one that did not see the conversation
that wrote the spec — and `sdd-design` reads what they leave behind:

1. **Define step 1.5, domain context.** Before writing the spec, a *cartographer* reads the code of the domain
   the feature touches and writes `sdd/contexto/<slug>.md`: the data, operations, interfaces and the rules
   the code already enforces, each one with `file:line`. It **helps, never blocks**: if it fails twice, the
   Define goes on without it.
2. **Define step 11, governance.** After the DEFINE is saved, a *reviewer* compares it with the governance
   catalog of `sdd-governanca` (entries that cannot be deleted, audit trail, period close, exact
   arithmetic…). It runs on **every** Define: with no money, tax, payroll or personal data, it answers
   N.A. in one line. It **blocks**: until it closes, `verify-gate.sh` exits 5 and build and release stop.

Both agents may write exactly one file. `sdd/bin/governanca-fronteira.sh` takes a sha256 snapshot of every
file in the repository before and after the dispatch and reports any other write (`FORA:`). Agents that
cannot open a fresh session themselves stop with `⏸️` and exit 40 (`sdd-fluxo.sh despachar`): you open a
new session, paste the brief, and paste the `<<<CONTEXTO` or `<<<GOVERNANCA` block back.

## After upgrading: the exit 5 on an existing DEFINE

A DEFINE written before v2.4.0 has no `Governança` row, so its build stops once with:

```text
🛑 GOVERNANÇA NÃO REVISADA (exit 5) — … não tem a linha Governança com um valor final
RESULTADO: CLARIFICAR
```

Two ways out:

1. In a new agent session, ask: *"run only steps 11 (Governança) and 12 (Segurança) of sdd-define on sdd/features/DEFINE_X.md"*.
   Do not rerun the whole Define: it would rewrite the spec.
2. Or dispense it, with a reason, in the `## Technical Context` table (an old DEFINE without that section gets
   it, with the `| Aspect | Value | Notes |` header):

   ```markdown
   | **Governança** | dispensada — <reason> | <your name, date> |
   ```

   If the DEFINE also has the "governança não rodou" marker (step 11 failed twice), replace it with
   `- [x] (governança) dispensada — <reason>`: while the marker is there, the gate stays at 5.

The final values the gate accepts are `N.A. — <reason>`, `GOVERNANCA_REVIEW_<F>.md · …` and
`dispensada — <reason>`. `pendente` and `falhou` keep exit 5.

## The domain map and patterns

The cartographer only runs when the project has a domain map, `sdd/patterns/dominio.md`; without it,
step 1.5 says "skipped" and the Define goes on. The map and the project patterns (the skeleton you copy
for a new operation, screen or migration) live in `sdd/patterns/`; the format is in
[`sdd/patterns/README.md`](../sdd/patterns/README.md). The Design cites a pattern as
`**Pattern:** \`patterns/<x>.md §Esqueleto\` (validado_em YYYY-MM-DD)`, and a cited pattern older than 90
days or with a dead anchor fails the Design.

## Scripts

| Script | What it does | Exits |
|---|---|---|
| `sdd/bin/contexto-lint.sh` | lints a CONTEXTO (header, 7 sections, `file:line` anchors, live `LM-nnn`, known `ctx:`); `--validade` (still valid against `origin/<default branch>`?); `--sugerir` (generate, reuse or skip, at most 2 domains); `--self-test` | `0` ok · `1` expired (`--validade`) · `2` invalid · `64` usage |
| `sdd/bin/patterns-lint.sh` | lints the patterns folder; `--design <DESIGN>` blocks a cited pattern that is stale or has a dead anchor; `--self-test` | `0` · `2` · `64` |
| `sdd/bin/governanca-fronteira.sh` | `--snapshot` / `--comparar`: proves a fresh agent wrote only the allowed file | `0` only allowed · `1` `FORA:` · `64` unverified |
| `sdd/bin/governanca-bloco.py` | checks the `<<<GOVERNANCA` block the reviewer returns against the report and the boundary | `0` valid · `1` `resultado: FALHA` · `2` invalid block · `64` |
| `sdd/bin/docs-extract-decisions.sh` | builds `docs/adr/index.md` from the `### Decision N:` titles of the DESIGNs, with orphans | `0` · `2` conservation broken · `64` |

The `--self-test` of the two lints needs `sdd/fixtures/contexto/` and `sdd/fixtures/patterns/`. `init` copies
`sdd/fixtures/` only on the first install: in a project installed before v2.4.0, copy those two folders
from the package (without them, the self-test exits 64 naming the folder).

The machine contract of the three handoffs (gate, cartographer, reviewer) is in
[`sdd/WORKFLOW_CONTRACTS.yaml`](../sdd/WORKFLOW_CONTRACTS.yaml).
