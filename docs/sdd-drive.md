<!-- Language: **English** · [Português](pt-BR/sdd-drive.md) -->

# Driving a feature: `sdd-drive`

`sdd-drive` takes one approved DEFINE to "ready to publish" by itself: it designs, builds one task per fresh session,
runs the final test, fixes and repeats up to a round limit, and **stops before publishing**. You come back only for the
decisions that are yours.

```text
/sdd-drive sdd/features/DEFINE_REPORTS.md
```

## The script decides, the agent executes

`sdd/bin/sdd-drive.sh` keeps the state, runs the Verify Gate, counts the rounds and says the next action. It never calls an
agent, so the same mechanism runs in all seven supported agents. An agent without subagents stops once per task and asks
for a new session; slower, never broken.

A **round** is one whole pass: build everything that is left, then run the final test. A red final test spends one round,
and `drive.max_rounds` (default 3, `--max N` overrides) is how many attempts to turn green you allow. Within a round there
is no ceiling on tasks, but the same task that does not move stops at the 3rd attempt.

## A run, from start to finish

```text
$ sdd-drive.sh iniciar sdd/features/DEFINE_REPORTS.md
ACAO: RODADA
rodada: 1/3
tarefa: 1 de 12 — src/report.py
…
$ sdd-drive.sh verificar sdd/features/DEFINE_REPORTS.md --fundo
ACAO: ESPERAR
…
$ sdd-drive.sh proximo sdd/features/DEFINE_REPORTS.md
ACAO: CORRIGIR
rodada: 2/3
o teste final ficou vermelho (normal nesta etapa): restam 2 rodada(s) · log: sdd/reports/evidence/REPORTS/DRIVE-gate-r1.log
…
$ sdd-drive.sh concluir sdd/features/DEFINE_REPORTS.md
motivo: gate-verde
O teste final passou e os relatórios estão prontos. Nada foi publicado.
```

| Verb | What it does |
|---|---|
| `iniciar <DEFINE> [--max N]` | checks the preconditions, writes the state, says the first action |
| `--dry-run <DEFINE> [--max N]` | shows the plan; runs nothing and writes nothing |
| `--resume <DEFINE> [--max N] [--aceitar-gate-novo]` | continues from the disk, without spending a round |
| `proximo <DEFINE>` | the next action, recalculated from the disk |
| `verificar <DEFINE> [--fundo]` | runs the final test; `--fundo` detaches it, for a test longer than the agent's command limit |
| `concluir <DEFINE>` | checks the last green and the build report, and stops at `gate-verde` |
| `bloqueio <DEFINE> "<reason>"` | the build is stuck and needs a person |
| `aguardar <DEFINE> <role> <brief>` | no subagent: the stop that asks for a new session |
| `recibo <DEFINE> "<text>"` | notes a routine decision in the report |

The actions are `ESPERAR`, `DESIGN`, `REVISAO_DESIGN`, `RODADA`, `CORRIGIR`, `COMMITAR`, `VERIFICAR` and `AVALIAR_E_RELATAR`; the
skill says who does each one.

## Stop reasons

| `motivo:` | Exit | What the person reads |
|---|---|---|
| `gate-verde` | 0 | O teste final passou e os relatórios estão prontos. Nada foi publicado. |
| `simulacao` | 0 | Simulação: nada foi executado nem gravado. |
| `orcamento-rodadas` | 20 | O teste final continuou vermelho nas rodadas permitidas. Nada foi publicado. |
| `manual-ux` | 20 | O teste final precisa da conferência de uma pessoa. Nada foi publicado. |
| `clarificacao-pendente` | 20 | O DEFINE ainda tem dúvida aberta ou a revisão de governança pendente. |
| `define-invalido` | 20 | O DEFINE não tem um teste final válido. |
| `gate-inconclusivo` | 20 | O teste final não chegou ao fim: isso não é vermelho e não gastou rodada. |
| `gate-alterado` | 20 | O comando do teste final mudou desde o início desta execução. |
| `bloqueio-humano` | 20 | A construção parou e precisa de você. Nada foi publicado. |
| `aguardando-sessao` | 40 | Esta etapa precisa de uma sessão nova do agente. Nada foi publicado. |
| `estado-invalido` | 20 | Não consegui ler onde a execução parou, e não vou adivinhar. |
| `branch-padrao` | 20 | O piloto não roda na branch principal: ele precisa de uma frente de trabalho própria. |

Exit 10 means "continue" (with an `ACAO:` line), exit 2 is a failure of the script itself (it could not write, or `sdd/bin/` is
outdated), exit 64 is a wrong call.

## What protects you

- **The hard barrier.** No verb publishes. Green is not "live": publishing is `sdd-release`, with your approval.
- **Only the script runs the deciding test.** The agent that built it does not get to report its own green.
- **The fingerprint of the Verify Gate.** If the command of the final test changes during the run, the run stops with
  `gate-alterado` and you decide. A green from the old command never counts after you accept a new one. This does not protect
  against a test weakened inside the command: that is the job of the fresh-context evaluator and of the review.
- **Commit or nothing.** A change outside the document folders (`sdd/features/`, `sdd/reports/`, `sdd/reviews/`, `sdd/handoffs/`,
  `sdd/traces/`) stops the final test with `ACAO: COMMITAR`, so the green belongs to a commit.
- **Decisions stay yours.** Calling the drive turns chaining on for that run only: `[auto · de rotina]` follows the recommended
  option and lands in the `Decidi sozinho` section of the report; D1 to D5 are always asked.

What it leaves behind: `sdd/reports/DRIVE_REPORT_<F>.md`, `sdd/reports/progress/DRIVE_<F>.json` and
`sdd/reports/evidence/<F>/DRIVE-gate-r<k>.log`. To start over, delete the state file.

## Also in this delivery

- **`sdd/bin/deploy-do-sha.sh`** answers "is this commit live?" for `sdd-release`: the run of the publishing workflow on the default
  branch, or a newer green run that contains the commit. A failure in a step listed in `deploy.transient_steps` repeats once, at
  the tip of the branch, and only if the commit still is the tip; it never uses `gh run rerun`. Exits: `0` live · `2` not live ·
  `3` no `gh` or `git`, or no login · `4` still unknown, which is not a failure · `64` usage.
- **`sdd/bin/sdd-archive.py`** cleans up the documents of closed features: a dry run by default, `git mv` of one lot per commit
  (`--lote com-ledger|sem-ledger|soltos --aplicar`), nothing deleted, and a feature whose record `HANDOFF_<F>.md` is still open stays where it is.
