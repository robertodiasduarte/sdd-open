<!-- Language: **English** · [Português](pt-BR/quickstart.md) -->

# Quickstart

From zero to a blocking gate in about ten minutes — in the agent you already use.

## Your agent, in one line

| Agent | Install | Invoke a phase | What gets generated for it |
|---|---|---|---|
| **Claude Code** | `bash sdd-open/bin/sdd-open.sh init --vendors claude` | `/sdd-define …` | `CLAUDE.md` (one line: `@AGENTS.md`) + copies under `.claude/skills/` |
| **Codex CLI** | `… init --vendors codex` | ask by description or `$sdd-define` | **nothing** — reads `AGENTS.md` and `.agents/skills/` natively |
| **Gemini CLI** | `… init --vendors gemini` | `/sdd-define …` (skill) | `GEMINI.md` + `context.fileName` in `.gemini/settings.json`; skills via `.agents/skills/`. ⚠️ CLI 0.22.x defaults to retired models: pass `-m gemini-3.7-flash` (or current). A Workspace account with cached login needs `GOOGLE_CLOUD_PROJECT`; alternative: `GEMINI_API_KEY` + `"security":{"auth":{"selectedType":"gemini-api-key"}}` in `settings.json` |
| **Cursor** | `… init --vendors cursor` | `/sdd-define …` | copies under `.cursor/skills/` |
| **Kimi Code** | `… init --vendors kimi` | `/skill:sdd-define …` | **nothing** — reads `AGENTS.md` and `.agents/skills/` natively |
| **Grok Build** · **GLM via Claude Code** | `… init --vendors claude` | `/sdd-define …` | same as Claude Code (both read `CLAUDE.md` and `.claude/`) |

Several agents on one project: `--vendors claude,codex,gemini`.

> Skill bodies are written in **Brazilian Portuguese** (the language of the community this
> comes from). The mechanics — gate, exit codes, file layout — are language-neutral.

## Per agent

### Claude Code
`init --vendors claude`. Generates `CLAUDE.md` with the `@AGENTS.md` import line and copies the skills to
`.claude/skills/`. Invoke `/sdd-define …`. Claude Code hooks and subagents work normally with the skills.

### Codex CLI
`init --vendors codex`. Nothing is generated: Codex reads `AGENTS.md` and `.agents/skills/` natively.
Ask for the phase by description ("run the Define phase on …") or use `$sdd-define`. Proven headless on
2026-09-05: `codex exec -s workspace-write "…"` produced a DEFINE with a parseable gate in 154 s.

### Gemini CLI
`init --vendors gemini`. Generates `GEMINI.md` and adds `AGENTS.md` to `context.fileName` in
`.gemini/settings.json`; skills come from `.agents/skills/` (native alias). ⚠️ CLI 0.22.x defaults to
retired models: pass `-m gemini-3.7-flash` (or the current one). A Workspace account with cached login
needs `GOOGLE_CLOUD_PROJECT`; alternative: `GEMINI_API_KEY` +
`"security":{"auth":{"selectedType":"gemini-api-key"}}` in `.gemini/settings.json`. Proven headless on
2026-09-05: 64 s, and the agent closed with the stage-summary kanban.

### Cursor
`init --vendors cursor`. Copies the skills to `.cursor/skills/` (Cursor does not read `.agents/`).
AGENTS.md is read natively. Invoke `/sdd-define …`.

### Kimi Code
`init --vendors kimi`. Nothing is generated: it reads `AGENTS.md` and `.agents/skills/` (also
`.kimi/skills`). Invoke `/skill:sdd-define …`.

### Grok Build and GLM via Claude Code
`init --vendors claude`. Grok Build reads `CLAUDE.md`, `.claude/` and `AGENTS.md` with no configuration.
GLM runs inside Claude Code (`ANTHROPIC_BASE_URL` pointing at the provider) and inherits the same adapter.

> **In CI or a pipeline:** `init` and `sync` ask for confirmation and, without an interactive
> terminal, exit `RESULTADO: CANCELADO` writing nothing. Pass `--yes`.

## 0. Should you use the full workflow at all?

| The change is… | Do this |
|---|---|
| describable in one sentence, small blast radius | skip the phases; talk to the model, run your tests |
| a bug fix with a known cause | `/sdd-define` (a bug spec needs one `shall continue to`) then `/sdd-build` |
| new behaviour, several files, expensive to get wrong | the full workflow below |

## 1. Install

```bash
git clone https://github.com/robertodiasduarte/sdd-open.git /tmp/sdd-open
cd my-project             # must be a git repository
bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex --dry-run    # shows the plan, writes nothing
bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex              # asks for confirmation, applies
```

`init` prints a plan (`+` create · `~` update block · `=` already correct) and only writes after
your `y`. Nothing of yours is overwritten: if you already have an `AGENTS.md`, only the block
between `<sdd-open-instructions>` and `</sdd-open-instructions>` belongs to it. When done,
`doctor` runs by itself and says, per agent, what was generated and what is native.

Requirements: `bash ≥ 3.2`, `git`. `python3` only for the Gemini adapter and the validators.
On Windows, use Git Bash or WSL.

## 2. Point the config at your project

Edit `sdd/config.yaml`:

```yaml
project:
  test_cmd: "npm test"
  typecheck_cmd: "tsc --noEmit"
layers:
  api: "src/api/**"
  ui: "src/ui/**"
deploy:
  cmd: "./deploy.sh production"
```

An empty slot means "skip this step and say so" — never "guess a command".

## 3. Verify the install

```bash
sdd/bin/verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md;             echo "exit=$?"  # 0
sdd/bin/verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md;  echo "exit=$?"  # 5
```

`0` and `5` prove the runner and the exit contract work. If the second returns `0`, ambiguity
detection is broken — do not proceed; silent assumptions are exactly what it exists to catch.

Every run ends with `RESULTADO: <WORD>` and a `→` line saying what to do next. In CI and in
`&&` pipelines use `--strict`: inconclusive, pending signature and clarification stop counting
as success.

## 4. Your first spec

Ask your agent for the Define phase on the example that ships with the install:

```text
/sdd-define sdd/fixtures/BRAINSTORM_EXEMPLO.md
```

The agent will push back in three ways, all deliberate:

- **Acceptance tests in EARS.** Not "the discount should work" but
  *"**When** the customer applies a valid code, the system **shall** recompute the total in
  <500 ms"*. The *unwanted* pattern forces you to name the failure mode before building.
- **Ambiguity becomes a marker.** Where the spec does not know, the agent writes
  `[NEEDS CLARIFICATION: …]` in the exact spot — and the gate returns `5` until you answer.
- **The gate is a command.** The DEFINE only leaves with a `## Verify Gate` block that
  `sdd/bin/verify-gate.sh --print` parses without error.

Then: `/sdd-design`, `/sdd-build` (the gate is the stop condition) and `/sdd-release` (one
human approval before anything ships).

## 5. When the package updates

```bash
cd /tmp/sdd-open && git pull
cd my-project && bash /tmp/sdd-open/bin/sdd-open.sh sync --check   # what drifted?
bash /tmp/sdd-open/bin/sdd-open.sh sync                            # regenerate the adapters
```

`sync` **never** writes inside `sdd/` — your specs, reports, handoffs and playbook are yours.
Files under `.claude/skills/`, `.cursor/skills/`, `CLAUDE.md` and `GEMINI.md` are generated:
edit `.agents/skills/` and run `sync`; edits to them are overwritten (each file's header says so).

## Diagnose any time

```bash
bash /tmp/sdd-open/bin/sdd-open.sh doctor
```

Shows bash/git/python3, what is installed and, per agent, whether the adapter was generated,
whether the agent reads `.agents/skills/` natively, and whether its CLI is on the PATH.

## Coming from sdd-starter?

[sdd-starter](https://github.com/robertodiasduarte/sdd-starter) is the on-ramp (skills for
agents without a filesystem, such as claude.ai and ChatGPT); SDD Open is the highway. Skill
names coincide on purpose: use **one or the other** per project. `doctor` warns if it finds both.
