<!-- Language: **English** · [Português](pt-BR/hooks.md) -->

# Git hooks

`init` installs two git hooks in the project, versioned under `sdd/hooks/`, and turns them on with your
confirmation (`core.hooksPath = sdd/hooks`). They run in every worktree of the project and in every one of
the seven supported agents, because they are plain `bash` + `git`.

- **`sdd/hooks/pre-commit`** checks every commit against 5 rules, the build report and the data-hygiene
  alarm. All rules run; the findings come out together, in one refusal. A clean commit is silent.
- **`sdd/hooks/pre-push`** only warns: when what you are pushing is behind `origin/<default branch>`, it
  says how many commits and what to do. It never blocks.

The plan line of `init` is the notice that the project starts refusing commits:

```text
+ core.hooksPath = sdd/hooks — 5 regras + relatório + alarme passam a conferir cada commit (teto do arquivo
  de contexto, credencial, playbook, byte NUL, branch padrão); git commit --no-verify pula uma vez (novo)
```

## What the pre-commit refuses

| Class | What it refuses | How to fix |
|---|---|---|
| **H6** | a commit directly on `project.default_branch` (default `main`) when `origin/<branch>` already exists. Without a remote the rule does not apply: a brand-new project commits on `main` normally | `git switch -c <name>` takes the staged work to a new branch; for the next feature, ask `sdd-new-session` |
| **H2** | a context file (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`, at any depth) above `project.context_file_max_kb` KB (empty = 100). That file enters the agent's context whole in every session | move the bulky content (changelog, history, dumps) to `docs/` or `sdd/`, or raise the slot in `sdd/config.yaml` |
| **H5** | a NUL byte in a text file (`.md`, `.sh`, `.py`, `.json`, `.yml`, … or no extension with a shebang). Git and grep then treat the file as binary and the diff disappears for reviewers. UTF-16 text (PowerShell, Excel exports) is recognized by its BOM and passes | write the escape (`\0`, `\x00`, `\u0000`) in the source |
| **H3** | a credential in clear text in `.json`, `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg`, `.conf` or `.env*` (`password`, `token`, `secret`, `key`… with a quoted value of 6+ characters). Placeholders pass: `${VAR}`, `{{ … }}`, `<…>`, `CHANGEME`, `example`, `***`. The message shows the key, never the value. When `gitleaks` is installed, `gitleaks protect --staged` runs too | replace the value with a placeholder, or `git restore --staged "<file>"` |
| **H4** | `sdd/playbook.md` deleted, renamed, or losing knowledge (an `[LM-nnn]` disappearing, or more than 20 % of the bullets rewritten at once — `playbook-lint.sh --anti-collapse`) | retire = move to `## Tombstones` keeping the ID; a big rewrite = 2 or more commits |
| **REPORT** | a `BUILD_REPORT_*.md` that fails `sdd/bin/report-lint.py` (checked on the staged content; the fixtures under `sdd/fixtures/` and the template under `sdd/templates/` are skipped) | add the criteria table and the evaluator line (`sdd/templates/fragments/EVIDENCIA.md`), or fix the cited evidence |
| **alarm** | when `git config sdd.higieneDado` is `on`: CPF/CNPJ with a valid check digit, `.env`, `.pfx`/`.p12`/`.pem` with a private key, a new spreadsheet — the `sdd-higiene-dado` alarm, called by the hook | the alarm's own message says what to do |

A refusal looks like this:

```text
sdd-open: commit recusado. Encontrei o que não pode entrar nesta versão:

  🛑 [H2] AGENTS.md: 204800 bytes (teto 100 KB)
  🛑 [H3] .vscode/sftp.json: credencial em texto claro (chave: password)

Por que importa:
  [H2] o arquivo de contexto entra inteiro em toda sessão do agente; acima do teto, estoura a janela antes do primeiro prompt
  [H3] o que entra no git fica no histórico e vai junto em todo push; depois disso, rotacionar a credencial é o único conserto

RESULTADO: COMMIT RECUSADO
→ [H2] mova o conteúdo volumoso (changelog, histórico, dumps) para docs/ ou sdd/; ou ajuste project.context_file_max_kb em sdd/config.yaml
→ [H3] troque o valor por um placeholder (${VAR}, CHANGEME, example) ou tire o arquivo desta versão: git restore --staged "<arquivo>"
→ se você conferiu e quer gravar mesmo assim, só desta vez: git commit --no-verify
  Agente de IA: não use --no-verify sem o OK explícito da pessoa.
```

Rules that depend on something optional degrade with a `⚠️` and let the commit through: `python3` missing
(the REPORT rule), `sdd/bin/playbook-lint.sh` or `sdd/bin/report-lint.py` missing (`init` completes `sdd/bin`),
`gitleaks` exiting with an unexpected code. Only `bash` and `git` are required to commit.

Note on REPORT: `report-lint.py` checks the cited evidence and the `AVALIACAO_*.md` **on disk**, not in the
index. A report staged with logs not yet added passes the hook; the Release phase checks it again.

## The limit: `--no-verify`

A client-side hook is skipped by `git commit --no-verify` (and by tools that commit without running hooks,
such as `git cherry-pick`). That is by design: after checking, a person may decide to record anyway. The truth
does not live in the hook: the Release phase runs `report-lint.py` again and the CI runs the publish gate.
An agent must never use `--no-verify` on its own; the last line of every refusal says so.

## The data-hygiene alarm

`sdd-higiene-dado` keeps its alarm in `.git/hooks/pre-commit` in a project without the hooks. In a project
with them, `alarme.sh instalar` only sets `git config sdd.higieneDado on` and the dispatcher calls the alarm
at the end of each commit; `desinstalar` unsets it. If the alarm was already installed when you ran `init`,
`init` migrates it (sets the config on and says so); the old file stays in `.git/hooks/`, inert, until
`desinstalar` removes it. Any other `core.hooksPath` (husky, lefthook) is still refused by the alarm.

## Another hook manager

If the project already has `core.hooksPath` (husky, lefthook) or a hand-written `.git/hooks/pre-commit`,
`init` does **not** touch it and does not turn the open's hooks on. It copies `sdd/hooks/` and prints the
line to add to the existing manager:

```sh
bash sdd/hooks/pre-commit || exit 1
```

`doctor` repeats that line as long as the hooks are not on.

## Turning off

```sh
git config --unset core.hooksPath
```

This is not sticky: the next `init` (which the guides recommend to receive new skills) sees the hooks off,
shows the plan line again and, with `--yes`, turns them back on. `doctor` tells you the state at any time:
`✅ hooks ligados (…)` or one `⚠️` per cause, with the command that fixes it (`rode init`,
`chmod +x sdd/hooks/pre-commit`, the line for another manager).

## In Claude Code

`init --vendors claude` also generates two guards in `.claude/hooks/` (copies of `bin/adapters/claude/` from
the package, marked `sdd-open:generated`; `sync` regenerates them and `sync --check` reports an edited copy)
and adds two entries to `hooks.PreToolUse` in `.claude/settings.json`, keeping every other key and entry:

- **`sdd-report-guard.py`** (Write, Edit, MultiEdit): before the agent writes a `BUILD_REPORT_*.md`, it
  simulates the resulting content and runs `sdd/bin/report-lint.py --stdin` on it. The write is denied with the
  lint's output when it fails; fixtures and the template are skipped.
- **`sdd-avaliador-guard.py`** (Agent, Task): when the dispatched prompt carries the word `veredito` (the
  fresh-context evaluator brief of `sdd-build`), it runs `sdd/bin/avaliador-guard.sh` and denies the dispatch
  while the tree has uncommitted work.

Both fail **open**: an unreadable payload, a missing script or an internal error becomes a
`⚠️ sdd-open: … não conferido` message and the action goes on. `SDD_REPORT_GUARD=off` and
`SDD_AVALIADOR_GUARD=off` disable them with a message (declare it in the BUILD_REPORT). Since this version the
`claude` vendor requires `python3`, like the `gemini` vendor already did; `init` checks it before writing
anything. The other six agents get the same truth from the pre-commit (REPORT rule) and from the Release phase.

## Exit codes

| Hook | Codes |
|---|---|
| `sdd/hooks/pre-commit` | `0` clean (silent, or `⚠️` for a skipped rule) · `1` refused, with every finding, `RESULTADO: COMMIT RECUSADO` and one `→` per class |
| `sdd/hooks/pre-push` | `0` always; `⚠️` when behind `origin/<default branch>` |

See also: [CLI conventions](cli-conventions.md) · [README](../README.md).
