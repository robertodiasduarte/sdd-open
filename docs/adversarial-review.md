<!-- Language: **English** · [Português](pt-BR/adversarial-review.md) -->

# Adversarial review

`sdd/bin/adversarial-review.sh` asks one engine (the AI model that reviews) to **review** a frozen diff, and a
**different** engine to **audit** that review — the auditor does not review the code again, it gives a
verdict on each finding and points out what the review missed. Reviewer and auditor run in a chain, never
in parallel: two reviewers side by side find less than a reviewer followed by a critic.

A second reviewer and a tie-break join on their own when the diff asks for them. The output is a folder
that `sdd/bin/sdd-fluxo.sh loop` reads to decide whether the work goes on, gets fixed, or needs you.

## What you fill in

Two slots in `sdd/config.yaml` — `review.revisor1` and `review.auditor` —, with ids from `sdd/review/registry.tsv`:

```yaml
review:
  revisor1: claude                    # who reviews; a comma list is the chain (1st = default)
  auditor: openrouter:qwen/qwen3.7-plus  # who audits — must be another engine
```

The registry ships with `claude`, `codex` (always `-s read-only`), `gemini` and `openrouter`, one line each,
and **no default chain**: with the slots empty, the skill asks you. `openrouter:<model>` uses the
`openrouter` line with another model. A new engine is one line in the registry (plus one adapter in
`sdd/bin/adapters/` if it is a new CLI). Model names live in the registry and in `sdd/review/precos.tsv`.

The review folder (`review.output_dir`, default `sdd/reports/reviews`) must be ignored by git — the diff
and the engines' answers must not go into the repository:

```bash
printf '%s\n' 'sdd/reports/reviews/' >> "$(git rev-parse --git-common-dir)/info/exclude"
```

## Running it

```bash
bash sdd/bin/adversarial-review.sh --feature MY_FEATURE           # review the branch's diff
bash sdd/bin/adversarial-review.sh --feature MY_FEATURE --dry-run # see the plan, call nothing
```

- **Frozen diff:** from the merge-base with `origin/<default branch>`, with new untracked files included
  and the SDD artifact folders left out (they go in as context). Its `sha256` is in the `META.txt`.
- **SDD context:** BRAINSTORM, DEFINE, DESIGN and BUILD_REPORT of `--feature`, up to
  `review.context_max_kb` (180); the BRAINSTORM leaves first.
- **2nd reviewer** when the diff touches a security surface (`review.security_globs`, `layers.sql`, a path
  segment like `auth` or `token`), has 8+ files, 120+ KB, touches 2+ layers, or the reviewer was shallow
  (under 30 s with no findings). It is the first available engine of the registry that is neither the
  reviewer nor the auditor. Its failure never stops the chain: the auditor still runs, and the `loop` asks
  you to restore an engine or dispense it for that round.
- **Tie-break** when the auditor refutes a HIGH with evidence: an engine outside the finding's origin and
  the auditor decides `DECISAO:PROCEDE` or `DECISAO:REFUTADO`.

## Cost

Every role records its tokens and cost in the `META.txt`, plus a total. The cost is what the engine reports
(`US$`), else an estimate from `sdd/review/precos.tsv` (`≈US$`), else `assinatura` (included in a plan),
else `$?` — an unknown cost is never shown as 0. The price is the one of the model that answered: a
reported model other than the configured one without its own line in `precos.tsv` is `$?`. A call that hit
the time cap on a pay-per-token engine may have been billed without a report, so the role shows
`US$ x + $?`. Update `precos.tsv` from the provider's public price list,
with its URL and the date; never from memory.

## Privacy

- OpenRouter calls carry `provider.data_collection = "deny"` and `require_parameters = true`: only
  providers that do not retain or train on the data are used. The key comes only from
  `OPENROUTER_API_KEY` in the environment — never a file, never an argument.
- The CLIs run from an empty temporary folder, with the prompt on stdin and no write tool (`claude --tools ""
  --safe-mode`, `codex -s read-only`, `gemini --approval-mode default`). Read tools may remain; the prompt
  says none is needed.

## Exits and what to do

| Exit | `RESULTADO:` | Meaning | What to do |
|---|---|---|---|
| 0 | REVIEW COMPLETA | reviewer and auditor answered in format | `bash sdd/bin/sdd-fluxo.sh loop --review <folder> …` |
| 64 | PAROU | usage, empty slot, unknown id, empty diff, diff above 8 MB, folder not ignored | the line after `→` |
| 65 | PAROU | credential failure — the review **never** switches engine on it | fix the credential the `→` names |
| 66 | PAROU | CLI not on `PATH`, and no other engine in the list | install it or add an engine to the list |
| 67 | PAROU | auditor = reviewer, or every engine of the list out of quota | pick another auditor, `--um-engine`, or add an engine |
| 68 | REVIEW INVÁLIDA | an answer without the verdict block — **never** "zero findings" | run again; if it repeats, swap that engine |

A 429 (rate limit) is retried twice on the same engine; quota, billing and timeouts move to the next engine
of the list, with a ⚠️ line saying who answered instead.

## Only one engine

`--um-engine` lets the same engine review and audit, in separate calls. The `META.txt` and the release
ledger record `diversidade: nenhuma`, and the output warns: the audit has the same blind spots as the review.
Weaker, but honest — and never silent.

## In the release

`sdd-release` requires an external review of **this** version of the code:

```bash
bash sdd/bin/adversarial-review.sh --conferir    # 0: prints the review_externo line for the ledger
bash sdd/bin/adversarial-review.sh --ledger sdd/releases/<F>/<file>.yaml   # 0: the ledger has it
```

`--conferir` recomputes the diff and compares the `sha256`. Without a matching review, the release asks you
— before the single OK — whether to run the review now or publish without it, with a written reason that
goes into the ledger as `review_externo: dispensado — <reason>`. `--ledger` runs in the feature's folder
right after the release commit: the review folder is ignored by git and only exists there.

When the diff called for a 2nd reviewer and the review ran with `--no-revisor2`, `--conferir` does not
accept it alone: add `--aceitar-sem-revisor2 "<reason>"`, and the reason goes into the ledger line as
`revisor2=dispensado — <reason>`.

## Offline gate

```bash
bash sdd/bin/adversarial-review-gate.sh       # -v also prints the value read in each check
```

It runs the review end to end with the **real** adapters, against stubs that answer in the format of each
engine (`sdd/review/stubs/`: a JSON like `claude -p`, the JSONL of `codex exec`, the JSON of `gemini -o json`
and a local HTTP server shaped like the OpenRouter API). It checks in `META.txt` what each adapter extracted —
verdicts, engine and model, tokens, cost — and the contract (exits 65, 67, 68; 429 retried on the same engine;
quota moving to the next one; no engine called outside the script of each scenario; the key never in a file).
No network and no credit: proxies point to a dead port, the key is fake and generated in the run, and the
CLIs on the `PATH` of the adapters are the stubs (an exported function or a `BASH_ENV` cannot swap them).

| Exit | `RESULTADO:` | Meaning |
|---|---|---|
| 0 | GATE VERDE | every check passed |
| 2 | GATE VERMELHO | some check failed; each ❌ names the field and the value read |
| 3 | GATE QUEBRADO | the gate could not isolate itself (missing stub, registry without the 4 engines, real CLI first in the adapters' shell); nothing was called |
| 64 | PAROU | usage |

The gate proves the package's 4 engines (`sdd/review/registry.tsv` next to `sdd/bin/`), not engines you
added. The failure texts of the stubs are synthetic (marked in `cenarios.tsv`): a CLI that changes its error
message is caught by the real review, not here. A CLI that changes its output format: update its
`<engine>.py` and its lines in `cenarios.tsv`.

## eval-agree

```bash
bash sdd/bin/eval-agree.sh [<reviews folder>]   # default: review.output_dir
```

It reads the reviews already made (`EXTERNAL_REVIEW_*/META.txt` and `auditor.verdicts.jsonl`) and prints, per
auditor (engine and model), how many verdicts were AGREE, DISAGREE_EVIDENCE, DISAGREE_CONCERN and NOVO, and
`taxa_agree` = AGREE / (AGREE + DISAGREE_EVIDENCE + DISAGREE_CONCERN). An auditor that almost always agrees
may not be auditing: compare it with another engine as auditor. The rate reflects the diffs this project
reviewed, not a benchmark. It never calls an engine. Exits: `0` MEDIDO · `2` SEM DADOS · `64` usage.

## Limits

- The engines see only the diff and the SDD context: they do not see production, the database or a
  deployment that happened outside git.
- A project that installed the package before this version gets `sdd/review/` and `sdd/bin/adapters/` from
  `init` (it completes what is missing), but keeps its old `sdd/config.yaml`: add the `review.*` slots by
  hand from `sdd/config.example.yaml`.
