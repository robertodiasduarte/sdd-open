# Quickstart

> 🇧🇷 [Versão em Português](quickstart.pt-BR.md)

Get the SDD skills into your agent and run your first flow.

## 1. Install the skills

### Claude Code

```bash
npx skills add robertodiasduarte/sdd-starter -a claude-code -y
```

Installs the 18 skills into the project's `.claude/skills/`. Add `-g` to install once into `~/.claude/skills/` and have them everywhere.

### Codex

```bash
npx skills add robertodiasduarte/sdd-starter -a codex -y
```

Same command, different engine: installs into the project's `.agents/skills/` — the folder Codex reads, alongside `~/.codex/skills/`. With `-g`, installs into `~/.agents/skills/` and applies to every project (Codex reads that folder and `~/.codex/skills/` too).

### Both engines in the same project

```bash
npx skills add robertodiasduarte/sdd-starter -a claude-code,codex -y
```

The documents the skills produce live in `sdd/`, a single folder both engines can see: Brainstorm in `sdd/features/`, Handoff in `sdd/handoffs/`, governance reviews in `sdd/reviews/`; until the next generation, `sdd-define`, `sdd-design` and `sdd-build` save directly in `sdd/` and take the previous document from the path you give them. If the project already has `.claude/sdd/`, the skills keep using it. On the web there is no folder: each document comes out in the chat.

### Other agents, or no Node.js

The same command serves Cursor, Kimi, Gemini CLI and 70+ agents: change the name in `-a`. Without Node.js, download the `.zip` files from the latest Release and copy each skill folder into your agent's skills directory, keeping the folder intact.

**To update:** `npx skills update`.

For other agents, copy every skill folder under `skills/` (all 18) into whatever directory your agent reads skills/instructions from, keeping each folder intact.

### claude.ai (web)

1. Download the per-skill `.zip` files from the [latest Release](../../../releases/latest).
2. In claude.ai, open **Settings → Capabilities → Skills** and upload each zip.

### ChatGPT / OpenAI-based agents

ChatGPT installs skills natively (Business, Enterprise and Edu plans):

1. Open **Settings → Skills** (or go to `chatgpt.com/admin/skills`).
2. Click **+** and drop each `.zip` from the [latest Release](../../../releases/latest) — no need to unzip.
3. Set the access level and repeat for each skill. Then invoke them by name (`sdd-brainstorm`, `sdd-define`…).

**No admin access?** Create a Project, upload the skill's files (mainly `SKILL.md` and `references/`), and in the project instructions write: *"Follow the SKILL.md in this project's files."*

Each skill also ships an `agents/openai.yaml` with a display name and, for some phases, a `default_prompt` — used by agent platforms that read that format.

Menus change between product versions — if the paths above don't match your UI, the rule that doesn't change is: **give the agent the skill's files and tell it to follow `SKILL.md`**, which is where the method lives.

## 2. Run your first flow

The flow is the same in every tool. In each phase you **run a skill, get a document, and review it before moving on**.

> **The rule of the method:** never move to the next phase with a document you haven't read.
> Fixing a sentence now costs minutes; fixing it after the AI has written the app costs hours.

### Phase 1 — Brainstorm: sharpen the idea

```text
Use the sdd-brainstorm skill. I want to build [your idea — e.g. a personal expense tracker].
```

The agent interviews you (one question at a time), compares 2–3 approaches, and produces `BRAINSTORM_*.md`.

**Review before moving on:** is the idea described the way you meant it? Anything missing? Ask for the fix now.

### Phase 2 — Define: what the app must do

```text
Use the sdd-define skill. Write the project definition from the brainstorm document.
```

More questions (take your time), then `DEFINE_*.md` with the acceptance tests.

**Review before moving on:** is everything you expect there? Anything you don't want? Fix it before Design.

### Phase 3 — Design: the technical plan

This is where you declare **where the solution will run** — it decides the tool you use in Build:

| You want… | Write in the prompt | In Build, use |
|---|---|---|
| A website or web system | web application (SaaS) | Claude Code or Codex |
| An app without coding | Lovable application | Lovable connected to Claude or ChatGPT |
| A Windows program | Windows executable (.exe) | Claude Code or Codex |
| A Mac program | macOS application | Claude Code or Codex |

```text
Use the sdd-design skill. Design the project based on the brainstorm and define documents.
The application will use the [pick from the table above] architecture.
```

**Review before moving on:** this is the last cheap stop. After here, changes mean rewriting code.

### Phase 4 — Build: the AI writes the app

```text
Use the sdd-build skill. Build the application based on the brainstorm, define and design documents.
```

Run it in the tool the table pointed to, handing over all three documents.

**Review the result:** test the app and go back to the AI with anything that differs from the Design.

Each artifact ends with a **Next Step** line telling you exactly which skill to run next. Keep the documents — each one is the input of the next phase and the record of what you decided.

> **Note:** phases 1–3 work in any chat agent — no filesystem needed. Phase 4 (**Build**) requires an agent that can write code to your project (Claude Code, Codex, Cursor, Lovable, Base44, etc.).

## 3. Optional: validate artifacts locally

Skills that produce gated artifacts ship a structural validator:

```bash
python skills/sdd-define/scripts/validate_define.py DEFINE_MY_FEATURE.md
python skills/sdd-design/scripts/validate_design.py DESIGN_MY_FEATURE.md
python skills/sdd-build/scripts/validate_build_report.py BUILD_REPORT_MY_FEATURE.md
```

They check structure (required sections, EARS tests, Next Step handoff) and exit non-zero with a reason when something is missing.

## Where to go next

- [Workflow](workflow.md) — what each phase does and why the order matters.
- Want executable gates and CI enforcement? Graduate to [SpecGate](https://github.com/robertodiasduarte/specgate).
