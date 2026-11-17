# Model per role

[Português](pt-BR/model-per-role.md)

The roles SDD Open dispatches in a fresh context (curator, evaluator, DESIGN reviewer, cartographer, pilot executor)
run, by default, on the session model, which is usually the most expensive one. This document shows how to measure
whether a cheaper model gives the same result **in your project** and only then switch. The package carries the
method and the slot, never a model name or price.

## The slot

In `sdd/config.yaml`:

```yaml
papeis:
  curador: ""
  avaliador: ""
  revisao_design: ""
  cartografo: ""
  executor: ""
  serie_cmd: ""
```

Empty means the session model, which is the usual behavior. The value is the name **your** agent accepts for the
model, as opaque text: it starts with a letter or digit, then letters, digits and `. _ : / -`, up to 80 characters.
`bash sdd/bin/sdd-fluxo.sh modelo <role>` reads and validates the value. An invalid value exits 64 and nothing is
dispatched.

The dispatch ladder (`.agents/skills/sdd-build/references/contexto-fresco.md`) reads the slot before every dispatch:
- in a subagent, it passes the model when the agent lets you choose one;
- in a new session, the stop printed by `sdd-fluxo.sh despachar` says which model to open.

## What each role costs

The ladder marks the role with `marca-fase.sh inicio|fim papel-<role> <FEATURE>`. `custo-feature.sh <FEATURE>` shows
the role in a `↳ papel <name> · <models>` sub-row, right under the phases, with the number of runs, the tokens and
the nominal cost. The sub-row stays **out of the total**, because what it shows is already counted in the phase the
role ran in. The listed models come from the session log, not from what the dispatcher said.

## Measure before switching

### 1. The answer key

The answer key is a folder with one case per subfolder, taken from the project's history:

| File | Content |
|---|---|
| `caso.txt` | `papel:` (`curador` or `avaliador`), `commit:` (sha, or `-` for an empty folder), `origem:` where it came from and, optionally, `base:` (the tag or commit the non-regression tests compare against: the copy gets a commit with that tree, tagged with the same name, before the case) |
| `brief.md` | the role's brief from that time; `@COPIA@` becomes the path of the case copy |
| `entrada/` | files laid over the commit (that time's DEFINE and DESIGN, the curator's harvest…) |
| `esperado.txt` | curator: the accepted delta, in the `playbook-curator.sh --aplicar` grammar. Evaluator: `VEREDITO: <X>` and one `AT-nnn PASS\|FAIL\|NAO_VERIFICADO` line per AT |
| `playbook.md` | curator only: the playbook before the curation |

Use cases whose outcome was confirmed later: a `NEEDS_WORK` the next cycle fixed, a delta you accepted.

### 2. The series

```text
<measurement>/teto.txt            teto_pago: 0.00 · teto_nominal: 200.00   (one cap for every series in the folder)
<measurement>/<series>/serie.txt  papel: avaliador · gabarito: <folder> · repeticoes: 3
<measurement>/<series>/candidatos.tsv   id <TAB> model <TAB> billing  (1st line = the reference, the current model)
```

The billing is `assinatura` (subscription), `pay-per-token` or `desconhecida` (unknown). To run:

```bash
bash sdd/bin/papel-serie.sh <measurement>/<series> --cmd '<agent command>' [--candidatos id1,id2] [--precos <folder>]
```

The command runs through `bash -c`, inside the case copy, and its standard output is the role's answer. It gets
these variables: `SDD_MODELO`, `SDD_BRIEF` (the brief file), `SDD_PAPEL`, `SDD_CASO` and `SDD_REP`. Always quote
`"$SDD_MODELO"`. Examples that use the agent's sandbox, never with permissions turned off:

```bash
claude -p --model "$SDD_MODELO" < "$SDD_BRIEF"
codex exec -m "$SDD_MODELO" --sandbox workspace-write - < "$SDD_BRIEF"
```

`papel-serie.sh`:
- runs **the whole reference first** and checks it with `papel-medir.sh --so-referencia`. If the reference misses
  the target, it stops before calling any candidate (exit 22): the answer key or the target is wrong;
- **before every call**, adds up the spend of every series in the measurement folder and stops (exit 20) when:
  - the next run could go over the cap (the estimate is the highest cost of one run already recorded);
  - the running total has an n/d;
  - the candidate has unknown billing;
  - the candidate is pay-per-token and the paid cap is zero;
- runs each execution in a **copy outside the project**: `git archive` of the case commit, plus `entrada/`, in a git
  repository with no remote. It snapshots the project before and after: a write outside the copy, or a remote added
  to the copy, invalidates the run and stops the series (exit 21) without deleting anything. This covers the
  project, not the whole disk: the rest depends on the agent's sandbox;
- measures each run's cost with `custo-feature.sh --execucao <copy>`, the same reader and arithmetic as the
  per-feature cost.

To resume, run the same command:
- runs that already have `meta.txt` are skipped;
- an interrupted run has its cost added before it is redone;
- the previous `PARADA.txt` moves to `paradas/`.

Don't edit the project while a series runs: the before and after snapshots would see your edit as the agent's write.

### 3. The choice

```bash
bash sdd/bin/papel-medir.sh <measurement>/<series> [--limiar 30] [--saida <file>]
```

`papel-medir.sh` only reads. The curator meets the target when:
- the `ajudou`/`mordeu` counts have precision and recall of 0.9 or more;
- it finds 2 of every 3 expected `ADD`, `REFINE` and `TOMBSTONE`;
- the proposed delta passes `--aplicar`.

The evaluator meets the target when:
- its verdict matches the answer key;
- 90% or more of the ATs have the same result;
- no AT that fails in the answer key is given as passing. That is the serious error: letting a defect through.

Verdict order:

| Exit | Result | When |
|---|---|---|
| 4 | `PARCIAL` | the reference is incomplete or invalid |
| 3 | `REFERÊNCIA FORA DA META` | the reference is complete but misses the target |
| 4 | `PARCIAL` | there is a `PARADA.txt`, a half-run candidate or an invalid run |
| 0 | `ESCOLHIDO: <id>` | the candidate with the lowest median nominal cost meets the target in every run and costs `--limiar`% or less than the reference |
| 1 | `SEM GANHO MEDIDO` | no candidate meets the previous row |

A candidate with an n/d cost is never the cheapest. "No measured gain" leaves the slot empty and does not count as
savings.

## Third-party data

`meta.txt` holds only numbers and model names. `saida.txt` holds the role's answer. If a case carries client data,
keep the measurement folder out of git.
