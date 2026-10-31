<!-- Language: **English** · [Português](pt-BR/chained-flow.md) -->

# Chained flow

Every question a skill asks carries the **class of the decision**, and a script (`sdd/bin/sdd-fluxo.sh`)
decides by exit code what used to be decided by reading prose: whether a DESIGN needs a review, whether
the review loop converged, whether the next phase may start without asking, and when to stop for a fresh
agent session. With the chain on, SDD moves on by itself while the gate is green and only stops when the
decision is yours.

## On and off

| | `flow.autonomous: false` (default) | `flow.autonomous: true` |
|---|---|---|
| End of each phase | the usual next step | when everything is ready, the next phase starts in the same session, after the transition line |
| `[auto · de rotina]` question | is asked | the recommended option wins and the decision goes to the **Decidi sozinho** receipt |
| `[D1]` to `[D5]` questions | are asked | are asked |
| Release | you ask for it | you ask for it: publishing cannot be undone and never starts by itself |

To turn it on, change `autonomous: false` to `true` in the `flow:` block of `sdd/config.yaml`. To stop once,
tell the skill "pare" (it passes `--parar`). To check: `bash sdd/bin/sdd-fluxo.sh estado` (`0` on · `1` off ·
`64` a value that is neither `true` nor `false`, treated as off).

## The marks

The labels are Portuguese on purpose: they are what the student reads in the answer.

| Mark | When | With the chain on |
|---|---|---|
| `[D1 · não se desfaz]` | publish, send, delete, buy, use a credential | asked |
| `[D2 · muda o produto]` | scope, business rule, text the person reads, an open question in the DEFINE | asked |
| `[D3 · muda a regra do método]` | playbook, gate, waiving a review | asked |
| `[D4 · limite de tentativas]` | the review loop did not converge (3 rounds or 2 evaluator cycles) | asked |
| `[D5 · provas em conflito]` | a serious finding refuted with evidence | asked |
| `[auto · de rotina]` | the recommendation settles it: execution mode, where to write, format | not asked |

The table belongs to `sdd/templates/fragments/PERGUNTA_DECISAO.md` (item 9).
`bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` checks that every
decision question has one mark with the right label, exactly one recommended option and it first,
"não sei", and no "Outro" option.

## The transition line and the receipt

```text
✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)
→ /sdd-design sdd/features/DEFINE_PAGAMENTOS.md
```

`sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` prints that line (exit `0`) only when the chain is on,
the phase document is `Ready for …`, the Verify Gate block is valid, the DEFINE has no open question and,
for the DESIGN, the required review is recorded in the Advisor Ledger with no open HIGH note. Otherwise it
exits `1` with the reason (`PARAR: …`) and the skill shows the next step. Before the line, the phase
summary carries the receipt (`**Decidi sozinho:**`, one line per decision: what, why, how to undo it).

## The stop for a fresh session (exit 40)

The build evaluator and the DESIGN reviewer need someone who has not seen the conversation. When the agent
opens that role by itself, it does. When it does not (or has that capability turned off), the skill writes
the brief and runs `sdd-fluxo.sh despachar <papel> <FEATURE> <brief>`, which copies the brief to
`sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md`, prints the ⏸️ stop with the steps and what to paste back,
and exits `40 AGUARDANDO_HUMANO`. Nothing is published; the original session goes on when you paste the
answer.

## The verbs

| Verb | Exits |
|---|---|
| `review-design <DESIGN>` | `0` EXIGIDO (≥ 3 new files in the File Manifest, or a security surface: fixed term, `review.security_globs` or `layers.sql`) · `1` DISPENSAVEL · `64` unreadable manifest (run the review anyway) |
| `loop --review <dir> --ledger <file> --rodada N` | `0` PRONTO · `10` CONTINUAR · `20` BLOQUEADO · `30` AGUARDANDO_RECIBO · `64` missing or unreadable input; record it with `--log`, never with `\| tee` |
| `despachar <papel> <FEATURE> <brief>` | `40` AGUARDANDO_HUMANO · `64` |
| `seguir <fase> <DEFINE> <próxima>` | `0` SEGUIR · `1` PARAR · `64` |
| `estado` | `0` on · `1` off · `64` invalid value |
| `--self-test` | `0` when every scenario matches |

`loop` decides the adversarial review after the build; the front that wires that review into the skills
is the one that calls it.

## Limit: a project that already had the package

In `sdd/bin/` and `sdd/templates/`, `init` only adds the files that are missing and never overwrites one
that exists; `sdd/fixtures/` is copied only on the first install. In a project installed before this
version, the two scripts and `FLUXO_ENCADEADO.md` arrive, but `sdd/fixtures/fluxo/` and
`sdd/fixtures/conversa/decisoes/` do not (the `--self-test` of both scripts exits `64` naming the folder),
and `sdd/templates/fragments/PERGUNTA_DECISAO.md` keeps the old item 9 (the lint exits `64`: marks table
missing). Copy those files from the package to get the marks and the self-tests.
