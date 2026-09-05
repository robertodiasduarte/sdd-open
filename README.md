<!-- Language: **English** · [Português](README.pt-BR.md) -->

# SDD Open by RDD

**Executable acceptance, not prose — in the agent you already use.**

Spec-Driven Development for **Claude Code, Codex CLI, Gemini CLI, Cursor, Kimi Code, Grok Build
and GLM via Claude Code**. One source (`.agents/skills/` + `AGENTS.md`), generated per-agent
adapters, and a mechanism the other frameworks lack: every spec carries a command with an exit
code that decides whether the phase is done.

```yaml
verify_gate:
  kind: test
  cmd: "npm test -- src/checkout/pricing.test.ts"
  pass_when: "exit 0"
```

That is not documentation. `sdd/bin/verify-gate.sh` runs the command, and the Build and Release
phases treat its result as blocking. Acceptance stops being a paragraph someone skims and
becomes something a machine executes.

## Install (2 commands)

```bash
git clone https://github.com/robertodiasduarte/sdd-open.git /tmp/sdd-open
cd my-project && bash /tmp/sdd-open/bin/sdd-open.sh init --vendors codex   # or claude, gemini, cursor, kimi
```

`init` shows the plan, asks for your confirmation, and ends with a per-agent diagnosis. Nothing
of yours is overwritten. [Full quickstart →](docs/quickstart.md)

## What ships

| Mechanism | What it does | Where |
|---|---|---|
| **Verify Gate** | acceptance as a command, with a six-state exit contract (`0/2/3/4/5/64`) — including *inconclusive* and *needs a human signature*, because "red or green" lies when a tool is missing or the criterion is aesthetic. Output always ends in `RESULTADO:` + what to do; `--strict` for CI | `sdd/bin/verify-gate.sh` · `sdd/templates/fragments/VERIFY_GATE.md` |
| **EARS grammar** | acceptance tests in fixed patterns (When / While / If–Then / Where / shall); the *unwanted* pattern forces you to name the failure mode before building | `fragments/EARS.md` |
| **Clarify protocol** | ambiguity becomes a marker in the spec, never an assumption; an active marker returns exit `5`, a distinct state no loop can "fix" by iterating the design | `fragments/CLARIFY.md` |
| **Graded release verdict** | PASS / CONCERNS / FAIL / WAIVED; a waiver is human-only, class-restricted, with a written reason | skill `sdd-release` |
| **Evidence contract** | in the build report a criterion only becomes `true` with an openable file or a dated human receipt — "should work" is `false` | `sdd/bin/report-lint.py` · `fragments/EVIDENCIA.md` |
| **Landmine playbook (ACE-lite)** | pitfalls with stable IDs, *helped/bit* counters, greppable surfaces and delta-only updates — a session proposes, the Release phase applies with human approval | `sdd/playbook.md` · `sdd/bin/playbook-lint.sh` · skill `sdd-playbook` |
| **Fresh-context evaluation** | whoever judges did not build: an agent without the build conversation proves each criterion by executing, never by reading the diff | skill `sdd-build` › `references/contexto-fresco.md` |
| **Second-vendor adversarial review** | fixed-format answer (verdict, ≤3 risks, fixes, what to ignore); every note is applied or rebutted in writing | `fragments/ADVISOR_CONSULT.md` |
| **Handoff by feature card** | one file per feature in the repository, with a self-contained resume prompt — no dependency on any agent's memory | skill `sdd-handoff` · `sdd/handoffs/` |

## The workflow

```text
/sdd-brainstorm → /sdd-define → /sdd-ux-review → /sdd-design → /sdd-build → /sdd-release
   (optional)         ↑            (if there is UI)    ↑            │             │
                      └──── /sdd-iterate corrects course ┘          │             │
                                                                     ▼             ▼
                                   the Verify Gate runs here — and again here — blocking both times
```

`sdd-handoff` and `sdd-playbook` are transversal: they close sessions and accumulate what bit.

## How the agent-agnosticism works

- **One source:** `.agents/skills/sdd-*/` — the [Agent Skills](https://agentskills.io) standard
  that Codex, Gemini CLI and Kimi Code read natively.
- **One contract:** `AGENTS.md` with a managed block (`<sdd-open-instructions>…`) that coexists
  with whatever you already had in the file.
- **Generated adapters**, never hand-maintained: `sdd-open.sh sync` writes `.claude/skills/`,
  `.cursor/skills/`, `CLAUDE.md`, `GEMINI.md` and `.gemini/settings.json` from the source, with a
  header that says so; `sync --check` detects when someone edited a copy.
- **User territory:** `sdd/` (specs, reports, handoffs, playbook, config) is never touched by `sync`.

Works on macOS, Linux and Windows (Git Bash/WSL): bash 3.2, zero zsh, zero symlinks.

## Documentation

- [Quickstart](docs/quickstart.md) ([PT](docs/pt-BR/quickstart.md)) — install, configure, first spec
- [CLI conventions](docs/cli-conventions.md) (PT) — command vocabulary and exit codes
- [Verify Gate contract](docs/verify-gate-contract.md) ([PT](docs/pt-BR/verify-gate-contract.md))
- [Adaptation guide](docs/adaptation-guide.md) ([PT](docs/pt-BR/adaptation-guide.md)) — config slots, landmines, worktrees
- [Comparison](docs/comparison.md) ([PT](docs/pt-BR/comparison.md)) — Spec-Kit, OpenSpec, BMAD, Kiro, Tessl

## The path

- **[sdd-starter](https://github.com/robertodiasduarte/sdd-starter)** — the on-ramp: skills for
  agents without a filesystem (claude.ai, ChatGPT). No executable gate.
- **SDD Open** — the highway: this repository. Skill names coincide on purpose; use one or the
  other per project.

## Language

Skills, templates and command messages are in **Brazilian Portuguese** — the language of the
community this comes from. The mechanics (gate, exit codes, layout) are language-neutral.
README and quickstart exist in English.

## Contributing, license and attribution

Releases are curated; open an issue before a PR — [CONTRIBUTING.md](CONTRIBUTING.md).
MIT — [LICENSE](LICENSE). The phase structure descends from Luan Moreno Maciel's **AgentSpec**;
what was added is listed in [NOTICE](NOTICE).
