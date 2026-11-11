<!-- Language: **English** · [Português](pt-BR/security.md) -->

# Security built into the flow: `sdd-seguranca`

AI builds the happy path and forgets the lock. SDD Open asks for the lock in the phase where it costs least, from
one catalog of the 22 most common security failures of AI-built apps (table without row-level security, secret key
in the code, another user's record by id, open CORS, user HTML rendered raw, missing security headers, hidden
instructions in a document, an agent with too much power, and more). Each catalog item carries, in one place:

| Field | Used by |
|---|---|
| `frase` — the rule that prevents it | the `AGENTS.md` block (the 5 highest-risk items for your stack) and `sdd-build` |
| `at` — the acceptance test, with the negative side | the security step of `sdd-define` |
| `evitar` — the design decision that closes it | the `## Segurança` section of the DESIGN |
| `padrao` — what the scan looks for | `sdd/bin/seguranca-varredura.sh`, on every release |
| `confira` — how to check it by hand | anyone without a terminal (claude.ai, ChatGPT), and the pre-release checklist |

The catalog lives in `.agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md`. Its text is original; each item
cites a public reference (OWASP, CWE).

## Your stack decides what applies

An item only fires when its stack is in the project. The scan detects the stack (`supabase/` or `@supabase/` in
`package.json` ⇒ supabase; `vercel.json`, `.vercel/` or `vercel` in `package.json` ⇒ vercel; `package.json` or an
`.html` file ⇒ web); the `security.stack` slot in `sdd/config.yaml` overrides it (`nenhuma` = only items for every
stack). A project without Supabase never gets a Supabase rule.

## Phase by phase

| Phase | What happens |
|---|---|
| Always | `init` and `sync` write the 5 highest-risk rules of your stack into `AGENTS.md`, plus one line pointing to `sdd-seguranca` |
| Brainstorm | three questions — who can see, who can change, how much can someone ask — become a three-line risk profile |
| Define, step 12 | `sdd-seguranca` in Define mode: without login, public route, third-party data, upload, database or paid AI, it answers N.A. in one line; otherwise it proposes up to 5 items per round, one decision each (apply · refuse with reason · defer). Applied items become acceptance tests in the Verify Gate. It warns, it does not lock |
| Design | the `## Segurança` section: where each secret lives, who sees and changes each table, each agent's credential, host headers and CORS, and the "how to avoid" of each applied item as a decision. `design-lint.py` warns (exit 0) if it is missing |
| Build | `seguranca-varredura.sh --regras` before the first task; the BUILD_REPORT lists refused and deferred items once |
| Release | the scan on every release (item 10 of 0a) and the model pass 0c against the fixed checklist |
| Any time | incident mode: "the key leaked", "the table was open" — close the door first, then preserve evidence, size it, fix, notify, record |

## The scan

```text
bash sdd/bin/seguranca-varredura.sh [--base REF] [--saida FILE]
```

Read-only, no network, bash 3.2 + Python stdlib. It blocks only two things, and only when **this release adds them**
(diff of the working tree against `origin/<default branch>`; without that ref, everything counts as new):

- **S11** a literal secret (private key header followed by the key body, known key prefixes with a key body, a service-role key assigned a value);
  a variable read by name is not a secret, and the scan never prints the value;
- **S01** a table created in a migration with no `enable row level security` anywhere in the migrations (Supabase only).

Everything else is a warning with the item id, `file:line` and the manual check. The same finding on a line that already
existed is a warning marked `(já existia)`. The screen shows the `security.max_warnings` most severe (default 5); the
`--saida` file keeps the full list.

| Exit | Meaning |
|---|---|
| `0` | `RESULTADO: NADA ACHADO` |
| `1` | `RESULTADO: AVISOS` — CONCERNS in the release |
| `2` | `RESULTADO: BLOQUEADO` — NON_WAIVABLE in the release |
| `64` | `RESULTADO: ERRO DE USO` — option, slot, unreadable catalog, or not a git repository |

A false positive is waived on the line itself, with a reason: `sdd-seguranca: aceito S16 — <reason>` in a comment on
that line or the line above. Without a reason it does not count, and the scan says so. A real key is never waived: it
already leaked, and incident mode starts by rotating it.

Other modes read the same catalog: `--stack`, `--regras`, `--checklist`, `--agents`.
