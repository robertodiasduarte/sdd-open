<!-- Language: **English** · [Português](pt-BR/playbook-curation.md) -->

# Playbook curation and invariants

Since v2.6.0, the last step of a release checks what the feature taught the project. A script harvests, an
agent that did not see the conversation judges, a checker separates counting from rule changes, and only
the rule changes become a question. A project that never registered a lesson only meets one line: "this
feature brought no new lesson and no count".

## The three roles

| Role | Who | What it does |
|---|---|---|
| Harvest | `sdd/bin/playbook-curator.sh --colher` | reads the feature's documents and prints one line per thing to judge |
| Judge | the curator, a fresh-context agent (brief: `.agents/skills/sdd-playbook/references/curator.md`) | checks each line against the cited `file:line` and returns a table; it never writes |
| Decide | you | answer the rule changes, one item at a time |

The curation runs **after** the push. It never undoes a publication, and every message in it says the
publication has already finished.

## What the harvest reads

`--preparar <FEATURE>` copies (never moves) the feature's documents to a staging folder outside the project:
the DESIGN, the BUILD_REPORT, the evaluator's `AVAL*-*.log` and `AVALIACAO_*.md`, the release ledger and the
feature's handoff. It also looks in `sdd/archive/<FEATURE>/`. Then `--colher <staging> sdd/playbook.md` prints:

| Line | Where it comes from |
|---|---|
| `DELTA LM-nnn ajudou+1` | a row of the landmines table (DESIGN or BUILD_REPORT) whose verdict cell starts with ✔ |
| `DELTA LM-nnn mordeu+1` | a row whose verdict starts with `mordeu`, or a finding line (❌, `NEEDS_WORK`, `FAIL`, `WAIVED`, `mordeu_antes:`) that cites the landmine |
| `SUGESTAO mordeu? LM-nnn` | a finding line with no ID that contains a `sup:` term of an active landmine; never a count by itself |
| `CANDIDATO #n → LM-xxx` / `REJEITADO` | a candidate block of the BUILD_REPORT or of the handoff; without `evidencia:` it is rejected |
| `PROMOVER? LM-nnn` | an active landmine with `mordeu` at 2 or more and no mechanism yet |

Every line to judge carries a fingerprint (`fp=`). After a curation, those lines go to
`sdd/reports/evidence/<FEATURE>/CURATOR-colhidos.txt`; the next release of the same feature shows them as
`JA_JULGADO` and does not count them again.

With `--inv`, a landmine that already bit and was never classified also shows up, as `INV_PENDENTE`. Exit `0` means there is something to judge or report, `1` means nothing at all, and any other exit is a
**failure**, never "nothing to harvest".

## What enters without a question, and what does not

`--conferir-bloco` is the judge of the curator's table, one row per harvest line. It rejects the table when a harvest line is missing,
when the curator wrote anything in the project or in the staging folder (the staging is sealed with
`--selar` before the dispatch, and the project is compared with `governanca-fronteira.sh`), and when an
automatic count is not **equal** to a line the script harvested: same landmine, same verb, `+1`, same
`file:line`.

| Kind | Enters |
|---|---|
| a count the script harvested, confirmed by the curator | without a question; it goes to the **Decidi sozinho** receipt |
| a new lesson (`ADD`), a retirement (`TOMBSTONE`), a rewording (`REFINE`), a promotion, an invariant, a suggestion the curator confirmed | only with your answer, question marked `[D3 · muda a regra do método]` |

The approved lines are applied to a **copy** (`--aplicar`), the copy passes the playbook lint, the
anti-collapse check and the invariants lock, and only then replaces `sdd/playbook.md`. The change goes in a
commit of its own (with the curation logs, when the project versions its evidence folder). Sending that commit to the default branch is another question, marked
`[D1 · não se desfaz]`: in many projects a push publishes.

## The delta grammar

```text
LM-020 ajudou+1
LM-016 mordeu+1
LM-004 promovido_para=<path of the mechanism>
ADD <section> :: sup: `term1` `term2` :: rule. **Do instead:** action. → ficha: — · promovido_para: —
TOMBSTONE LM-nnn :: reason
REFINE LM-nnn :: new text. **Do instead:** action.
```

`--aplicar <delta> <playbook>` validates the whole delta first. With one invalid line it prints every error,
prints nothing on stdout and exits 2.

## Invariants

A landmine says "this bit me". An invariant, in `sdd/invariants.md`, says "this can never be violated, and
this is what watches it":

```text
- [INV-NNN] estado=ok|auto|humano origem=seed|LM-nnn[,LM-mmm] [check=<path>] :: <rule> · por quê: <text> [· tarefa: … | · motivo: …]
```

- `ok`: a check runs without anyone remembering. `auto`: it can be automated, and the task says how.
  `humano`: it needs judgment, and the reason says why.
- Every active landmine that has bitten at least once, or that was promoted, must be classified: as the
  origin of an invariant, or under `## Descartados` with the reason.
- `--validar-inv <playbook> <invariants>` is the lock: it rejects an invariant whose origin was retired, an
  unclassified landmine, a repeated ID and a `check=` that does not exist.
- Retiring a landmine that is the origin of an invariant is **one** decision, not two: `--cruzar` proposes the
  adjusted invariant line, and both go in the same option. `--aplicar-inv` writes the approved lines; nobody
  edits the file by hand.

A project installed before v2.6.0 receives an empty `sdd/invariants.md`. The first curation then shows each old
lesson that is not classified yet and asks about it, once; without an answer, the lock holds and nothing is applied. Without the file, the curation skips the
crossing and says so.

## What it does not do

- It does not read anything outside the feature's documents, and it does not harvest recursively.
- It does not read the transcript of the session, only the files.
- It does not judge the quality of a lesson: that is the curator's job, and yours.
- It does not publish a catalog of invariants; the source file is the catalog.
- A promotion accepted here only registers the decision, as a pending item. The mechanism is a fix of its own, with a case that
  fails without it.

Exit codes and the words each mode prints: [cli-conventions.md](cli-conventions.md).
