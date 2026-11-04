<!-- Language: **English** · [Português](pt-BR/llm-in-code.md) -->

# LLM in the code, and measured contrast

Since v2.5.0, the method has four pieces for software that calls a language model in production, and one for
accessibility. None of them applies to a project that has no prompt and no screen: they stay out of the way.

## A process in a loop: `sdd-loop-builder`

A single call and a process are different things. The deciding question: **does the process re-prompt the model
from its own previous output?** If it does, it is a loop: it can repeat the same mistake, spend without limit or
declare itself done without checking.

The `sdd-loop-builder` skill writes the process card, a **LOOP_SPEC v2**, before any code exists:

| What it fixes | Why |
|---|---|
| **Profile by risk** (`lite`, `standard`, `high-risk`): external or irreversible effects are `high-risk`; among reversible ones, `lite` is one LLM stage checked by an exit code | A local, simple loop does not need the full card; one that sends an email does |
| **Control state** | Every retry, budget and stop rule reads from it |
| **Independent verifier** | Whoever generated the text does not judge it |
| **Stop rules**, including the failure of the verifier itself | A broken verifier is never "done" |
| **Budget per stage**, applied before each action | A single ceiling truncates one stage and wastes another |
| **Stage table, LLM × code** | Whatever can be deterministic is code; the model proposes, the code decides |

The skill does not write the stage prompts. It gives each one a one-line output contract, and the prompt skill
writes it. Without ground truth, the card says so instead of inventing a number.

## The inventory in the Design

When the DEFINE says `LLM Prompts: true`, the Design copies the section from
`sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`: one row per production prompt, with `Tipo`, `Versão`,
`Completeness` and `Refator de?`, and one contract block per row, with `Autônomo?`, `Verification interna` and
`Eval mínimo pré-ship`. `sdd/bin/design-lint.py` rejects a missing column or field.

**After updating the package**, a DESIGN in progress with the old inventory fails `design-lint.py` once. It is not a
defect in the design and no code has to change: copy the columns and fields from the fragment.

## The router in the Build

Step 4 of `sdd-build`, for a file in the inventory:

- `Tipo=one-shot` goes to the skill in `prompts.builder_skill`;
- `Tipo=loop` goes to `sdd-loop-builder` first, then to the prompt skill once per LLM stage, all in the same turn;
- no `Tipo` (an old DESIGN): the deciding question above; in doubt, `loop`, recorded in the report;
- a missing skill blocks that item, never improvised.

A loop row has `<process folder>/LOOP_SPEC.md` as its destination, and each LLM stage writes to the file named in
the stage table. Those files count as inventoried.

## The drift scan: `prompt-drift-scan.sh`

Before writing a file, the Build asks: does this smell like a production prompt?

```bash
printf '%s' "$TEXT" | bash sdd/bin/prompt-drift-scan.sh --conteudo src/agent/run.ts
bash sdd/bin/prompt-drift-scan.sh src/agent/run.ts     # files already on disk
bash sdd/bin/prompt-drift-scan.sh --self-test
```

It looks for a `prompts/` folder, a file name with `prompt` (except `.md`), a direct SDK call (`messages.create`,
`messages.stream`, `chat.completions`, `responses.create`, `generateContent` and their streaming forms), `system` with fixed text, a system `role` and, the signal
that matters most, **the parameter of your own LLM function**:

```yaml
prompts:
  wrapper_pattern: "systemPrompt:"     # or "callLLM\\(": inside double quotes the backslash is doubled
```

The script adds "followed by fixed text" to that expression, so a parameter that receives an imported name does not
fire: that prompt lives in the imported file. **Left empty, the scan is partly blind**, and it says so on every run:
a project that calls the model through its own function is invisible to a search for SDK signatures.

| Exit | Result | What to do |
|---|---|---|
| `0` | `LIMPO` | write the file |
| `2` | `DRIFT` | in the inventory, this is expected and the file is written; outside it, the Build stops: iterate the Design, or record a false positive |
| `64` | `ERRO DE USO` | a wrong call, a path that cannot be read or an invalid slot; never treated as clean |

Test files do not fire, in the usual conventions: `a.test.x`, `a.spec.x`, `a_test.x`, `a_spec.x`, `test_a.x`, `ATest.x`,
`ATests.x` and the folders `tests/`, `test/`, `spec/`, `__tests__/`. The content of a `.md` outside `prompts/` is not
evaluated. **Limits:** the search covers common forms, line by line, and is not exhaustive: fixed text on the line after the
parameter, an SDK outside the list and text built from a variable do not fire. For those, use the slot. Without git, the root
is the current folder. A `system: "linux"` in a YAML file does fire: record it as a false positive.

## Measured contrast: `contraste.sh`

```bash
bash sdd/bin/contraste.sh '#767676' '#ffffff'            # 4.54:1 PASSA (piso 4.5:1), exit 0
bash sdd/bin/contraste.sh '#777777' '#ffffff'            # 4.47:1 REPROVA (piso 4.5:1), exit 2
bash sdd/bin/contraste.sh '#000000' '#ffffff' .5         # transparency as the 3rd value: composed over the background
bash sdd/bin/contraste.sh '#777777' '#ffffff' --piso 3   # large text, border, icon
```

**Quote the colors:** without quotes, `#` starts a shell comment and the colors never reach the command. Accepted forms
are `#rgb` and `#rrggbb`; `rgba(...)` exits 64 and shows the 3rd-value form.

**The result is truncated on purpose.** Online calculators usually round, so one may show 4.48 where this shows 4.47. A
4.496 rounded would appear as 4.50 and pass; truncated, it shows 4.49 and fails the 4.5 floor.

## The WCAG table in the UX review

`sdd-ux-review` fills 7 rows, WCAG 2.2 AA, whenever the feature has a visual surface; without one, a single line
`N.A. — <reason>`.

| Criterion | Level | Verdict |
|---|---|---|
| 1.4.3 text contrast | AA | `PASSA`, `REPROVA` or `N.A.` |
| 1.4.11 non-text contrast, including the focus ring | AA | `PASSA`, `REPROVA` or `N.A.` |
| 1.4.1 meaning not by color alone | A | `PASSA`, `REPROVA` or `N.A.` |
| 2.4.7 visible focus | AA | `PASSA`, `REPROVA` or `N.A.` |
| 4.1.2 name, role and value | A | `PASSA`, `REPROVA` or `N.A.` |
| 2.1.1 keyboard | A | inherited: goes to the acceptance notes |
| 2.5.8 target size | AA | inherited: goes to the acceptance notes |

Every `REPROVA` becomes one MUST, with the criterion and the measured pair. The two inherited rows can only be proved on
the finished screen. The table follows the text of the standard; a project that wants more keeps that rule in its own
playbook. 3.3.7 is level A and 2.4.13 is AAA: neither is an AA criterion, and neither is in the table.
