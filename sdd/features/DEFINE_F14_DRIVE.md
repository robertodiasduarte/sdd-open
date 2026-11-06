# DEFINE: F14 Drive e orquestração

> Um script conta as rodadas, roda o teste final e diz a próxima ação; o agente executa. O DEFINE vai até "pronto para publicar" e para na barreira. A release ganha o raio de impacto por superfície e a verificação do deploy num script só, e o passivo de documentos ganha uma faxina com simulação por padrão.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_DRIVE |
| **Date** | 2026-11-05 |
| **Author** | SDD Define by RDD (sessão 12, Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

No Open, levar um DEFINE até "pronto para publicar" depende de a pessoa chamar cada fase e de o agente lembrar o limite das voltas: nada conta as rodadas, nada retoma uma execução que caiu, nada confere se o teste final mudou no meio e nada barra por script o avanço para a publicação. Na `sdd-release`, a verificação do deploy é um texto que cada agente reinterpreta, o raio de impacto é uma passada única sobre o diff inteiro e o conflito de changelog não tem regra; e os documentos de features fechadas se acumulam sem faxina.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem constrói com o SDD Open | leva um DEFINE até a release | chama fase por fase e acompanha à mão cada volta de teste vermelho; se a sessão cai, perde o fio |
| Quem publica | roda a `sdd-release` | a verificação do deploy depende de o agente seguir um texto longo; o raio de impacto olha tudo de uma vez |
| Quem mantém um projeto antigo | cuida de `sdd/features/`, `sdd/reports/` e `sdd/reviews/` | os documentos de features fechadas se acumulam e atrapalham a busca |
| Quem usa um agente sem subagente | roda o mesmo fluxo em outro agente | o mecanismo do privado só existe no Claude Code |
| O Roberto, na F15 | troca o privado pelo Open | sem drive, `deploy-do-sha` e archive, o privado não pode ser substituído |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/sdd-drive.sh`: estado, próxima ação, Verify Gate rodado pelo script, orçamento de rodadas, retomada, 12 motivos de parada tabelados, DRIVE_REPORT e nenhum verbo que publique (O1) |
| **MUST** | Skill `.agents/skills/sdd-drive/` e slot `drive.max_rounds`, default 3, com 1 rodada = passada inteira + gate (O1, D11) |
| **MUST** | Impressão digital do bloco do Verify Gate: mudou no meio, para com `gate-alterado` e a pessoa decide |
| **MUST** | Raio de impacto por superfície na passada 0b da `sdd-release`: um subagente por superfície, sequencial sem subagente, citando as invariantes do módulo (O2) |
| **MUST** | `sdd/bin/deploy-do-sha.sh` sobre `gh run`: espera o run do SHA até 40 min, aceita substituto que contém o commit e redispara 1 vez em falha passageira; o item 10 da `sdd-release` passa a chamá-lo (O3) |
| **MUST** | Slots `deploy.workflow` e `deploy.transient_steps` |
| **MUST** | `sdd/bin/sdd-archive.py`: retroativo, simulação por padrão, `git mv` por lote, protege frente com ficha aberta (O4) |
| **MUST** | Regra do conflito de changelog na `sdd-release`: a versão da branch padrão, com a entrada nova no topo (O4) |
| **MUST** | `avaliador-guard.sh` aceita documento não rastreado nas pastas de documento de `sdd/`; continua recusando código e documento rastreado modificado |
| **MUST** | A colheita do `playbook-curator.sh` não conta a própria mensagem de erro nem o eco de comando de um log (L10) |
| **SHOULD** | `docs/sdd-drive.md` + PT, sem a linha `sdd-drive` no roadmap, README e guia do aluno com a 19ª skill |
| **SHOULD** | Prova num agente de fora do Claude: uma execução real do drive sobre um projeto pequeno, com o modelo declarado |

---

## Success Criteria

- [ ] `bash sdd/bin/sdd-drive.sh --dry-run <DEFINE>` sai 0 com `motivo: simulacao` e o bloco do gate, sem gravar arquivo; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` sai 0.
- [ ] `bash sdd/bin/sdd-drive.sh --self-test` sai 0, com um cenário para cada um dos 12 motivos e para cada exit (0, 2, 10, 20, 40, 64).
- [ ] Os testes de `deploy-do-sha.sh` cobrem os 7 desfechos sem rede, com `gh` de mentira e `git` real, e o registro do `gh` de mentira mostra zero `run rerun`.
- [ ] `sdd-archive.py` sem `--aplicar` deixa `git status --porcelain` igual antes e depois; `--aplicar` sem lote sai 64.
- [ ] Os scripts novos sem achado em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'`; baseline vermelha na `v2.6.0`; 1 sabotagem por script novo derruba o teste correspondente.
- [ ] `skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas 19 skills; `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` sai 0; `check-versions.py --base v2.6.0 --base-obrigatoria` sai 0.
- [ ] `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F14_DRIVE.md` sai 0; CI verde em `ubuntu-latest` e `macos-latest` dentro dos tetos de 25 e 45 minutos.
- [ ] Revisão adversarial real com `loop` PRONTO e `--conferir` CONFERE no commit final; Release `v2.7.0` por tag, com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `sdd-drive.sh iniciar <DEFINE> [--max N]` runs with all preconditions met, the script **shall** write the state to `sdd/reports/progress/DRIVE_<F>.json` with the DEFINE path, the fingerprint of the Verify Gate block, the starting commit, the limit and no gate run, print `ACAO: <ação>` and `rodada: 1/N` (the round is derived: red gates + 1, capped at N), and exit 10 | test |
| AT-002 | Unwanted | **If** `iniciar` or `--dry-run` runs on the default branch (the slot `project.default_branch`, or `origin/HEAD`) or on a detached `HEAD`, **then** the script **shall** stop with `motivo: branch-padrao` and exit 20; **if** the DEFINE has no valid gate block (`kind` outside the 5, or `cmd` empty or `N/A` in a kind that needs one; whether a command exists is only known by running it, and that is `gate-inconclusivo`), **then** `motivo: define-invalido` and exit 20; **if** `verify-gate.sh --checar` exits 5 (active clarification marker or no final `Governança` line), **then** `motivo: clarificacao-pendente` and exit 20; **if** the `verify-gate.sh` or `sdd-fluxo.sh` beside the script does not support `--checar` or `seguir --drive`, **then** it **shall** exit 2 with `RESULTADO: FALHA` naming the outdated file and how to update `sdd/bin/`, and **shall not** print `define-invalido`; in all these cases no state file **shall** be written | test |
| AT-003 | Event-driven | **When** `sdd-drive.sh --dry-run <DEFINE>` runs with all preconditions met, the script **shall** print the actions it would take, the `kind` and the `cmd` of the gate without running them, and `motivo: simulacao`, write no file and exit 0 | test |
| AT-004 | Ubiquitous | The limit **shall** come from `--max N`, else from `drive.max_rounds` of `sdd/config.yaml`, else `3`; a value that is not an integer from 1 up, in the flag or in the slot, **shall** exit 64 naming where it came from | test |
| AT-005 | Event-driven | **When** `sdd-drive.sh proximo <DEFINE>` runs, the script **shall** print exactly one action, recalculated from the disk, in this order: `ESPERAR` while a gate of this feature is running; `DESIGN` when the DESIGN does not exist or `sdd-fluxo.sh seguir design <DEFINE> build --drive` stops for a reason other than the review; `REVISAO_DESIGN` when it stops because the required review is not registered or has a `HIGH` open; `RODADA` with `tarefa: i de n — <arquivo>` for the next pending task while `PROGRESS_<F>.md` has a `- [ ]` line; `COMMITAR` while something outside the documents is uncommitted; `CORRIGIR` when the last gate is red and nothing but documents changed since; `AVALIAR_E_RELATAR` when the last gate is green with the current fingerprint and nothing but documents changed since; `VERIFICAR` otherwise; with `rodada: k/N` in every case; and exit 10; an exit 64 of `seguir` **shall** exit 2, never `DESIGN` | test |
| AT-006 | Event-driven | **When** `proximo` finds no `PROGRESS_<F>.md`, the script **shall** create it from the File Manifest of the DESIGN with one `- [ ] <arquivo>` line per row, and a manifest row later added to the DESIGN **shall** be appended as `- [ ]`; a manifest with no row fails `design-lint.py`, and the answer is `ACAO: DESIGN` with that reason; **if** the file has neither `- [ ]` nor `- [x]` lines, **then** it **shall** stop with `motivo: estado-invalido` and exit 20 | test |
| AT-007 | Unwanted | **If** `proximo` or `--resume` returns the same pending task with the same `HEAD` for the 3rd time, a count only a `--resume` after `bloqueio-humano` resets, **then** the script **shall** stop with `motivo: bloqueio-humano`, naming the task, and exit 20, keeping the state for `--resume` | test |
| AT-008 | Event-driven | **When** `sdd-drive.sh verificar <DEFINE>` runs and the next action is `VERIFICAR`, the script itself **shall** run `verify-gate.sh <DEFINE>`, save `$ cmd` as the first line, the output and the real `[exit=N]` in `sdd/reports/evidence/<F>/DRIVE-gate-r<k>.log`, with `k` numbering every run so that no log is overwritten, reload the state from the disk and record the exit together with the `HEAD` and the fingerprint read **before** the gate started, because what a gate proves is what existed when it began; exit 2 **shall** spend the round: below the limit it prints `ACAO: CORRIGIR` with the log path and how many rounds remain and exits 10, at the limit it stops with `motivo: orcamento-rodadas` and exit 20; `verificar --fundo` **shall** start the same run detached from the calling agent and print `ACAO: ESPERAR` at once, and a second `verificar` or a `proximo` while it runs **shall** print `ACAO: ESPERAR` and run no gate; a lock of a dead process **shall** be released | test |
| AT-009 | Event-driven | **When** the gate of `verificar` exits 0, the script **shall** print `ACAO: AVALIAR_E_RELATAR` and exit 10; exit 3 or any exit outside the gate contract **shall** stop with `motivo: gate-inconclusivo`, exit 4 with `motivo: manual-ux`, exit 5 with `motivo: clarificacao-pendente` and exit 64 with `motivo: define-invalido`, all with exit 20 and without spending a round | test |
| AT-010 | Unwanted | **If** `verificar` or `concluir` finds a tracked change or an untracked non-ignored file outside `sdd/features/`, `sdd/handoffs/`, `sdd/reports/`, `sdd/reviews/` and `sdd/traces/`, or a file there whose extension is not of a document (a `.sh` under `sdd/reports/` may be the gate), **then** the script **shall** not run the gate, **shall** list the files, print `ACAO: COMMITAR` and exit 10 without spending a round; **if** nothing but those folders changed since the last red gate, **then** it **shall** not run the gate nor spend a round and **shall** print `ACAO: CORRIGIR` | test |
| AT-011 | Unwanted | **If** the fingerprint of the Verify Gate block (`kind`, `cmd`, `pass_when`, `threshold`, `manual_fallback`) differs from the recorded one at `proximo`, `verificar`, `concluir` or `--resume`, **then** the script **shall** stop with `motivo: gate-alterado`, show the recorded and the current `cmd`, not run the gate and exit 20; `--resume --aceitar-gate-novo` **shall** record the new fingerprint and leave the change written in the DRIVE_REPORT, and gates run under another fingerprint **shall not** count as the last gate: `proximo` and `concluir` **shall** print `ACAO: VERIFICAR`, and `verificar` **shall** run the gate even with the same `HEAD` | test |
| AT-012 | State-driven | **When** `sdd-drive.sh --resume <DEFINE> [--max N]` runs with a valid state, the script **shall** print `retomando: rodada k/N · x de n tarefas prontas · último teste final: <exit>` and the next action without spending a round and exit 10; **while** the rounds used are at or above the limit, `proximo`, `verificar`, `concluir` and a `--resume` without a raise **shall** stop with `motivo: orcamento-rodadas` and exit 20 without running the gate, until `--resume --max N` raises the limit above the rounds used | test |
| AT-013 | Unwanted | **If** the state file is absent at `--resume`, `proximo`, `verificar`, `concluir`, `bloqueio`, `recibo` or `aguardar`, cannot be parsed, has any field in the wrong shape (never a traceback), or belongs to another DEFINE, **then** the script **shall** stop with `motivo: estado-invalido`, never guess, and exit 20; **if** `iniciar` finds a state file, **then** it **shall** refuse with the same reason, pointing to `--resume` and to the file to remove | test |
| AT-014 | Event-driven | **When** `sdd-drive.sh concluir <DEFINE>` runs, the last gate is green with the current fingerprint, `HEAD` is that commit or differs only under `sdd/features/`, `sdd/reports/`, `sdd/reviews/`, `sdd/handoffs/` or `sdd/traces/`, nothing is pending by AT-010, `proximo` would answer `AVALIAR_E_RELATAR`, and `report-lint.py` and `report-lint.py --pendente` exit 0 on `BUILD_REPORT_<F>.md`, the script **shall** stop with `motivo: gate-verde` and exit 0; a code change after the green **shall** print `ACAO: VERIFICAR`, and a failing report `ACAO: AVALIAR_E_RELATAR` with the lint lines, both with exit 10 | test |
| AT-015 | Event-driven | **When** the script reaches any stop reason of a running execution, which excludes `simulacao` and the refusal of a second `iniciar`, it **shall** rewrite `sdd/reports/DRIVE_REPORT_<F>.md` opening with one sentence with the plain phrase of the reason and the rounds used, then the reason, the rounds used and the limit, one row per gate run (round, commit, exit, log), the commits since the start, the gate changes accepted and the sentence that nothing was published | test |
| AT-016 | Event-driven | **When** `sdd-drive.sh recibo <DEFINE> "<texto>"` runs, the script **shall** add the text to the section `Decidi sozinho` of the DRIVE_REPORT and exit 0; **when** `sdd-drive.sh bloqueio <DEFINE> "<motivo>"` runs, the script **shall** stop with `motivo: bloqueio-humano` and the text, and exit 20; **when** `sdd-drive.sh aguardar <DEFINE> <papel> <brief>` runs, it **shall** call `sdd-fluxo.sh despachar`, repeat its stop, print the next pending task read from `PROGRESS_<F>.md`, record `motivo: aguardando-sessao` and exit 40, and `--resume` **shall** continue from the state; an exit of `despachar` other than 40 **shall** be repeated without recording that reason | test |
| AT-017 | State-driven | **While** every verb of `sdd-drive.sh` runs in a sandbox with `git` and `gh` shims that log their argv, the log **shall** contain no `push`, no `gh release` and no `gh workflow run`; the script **shall** have no verb that runs `{{DEPLOY_CMD}}` or the `sdd-release` skill; every stop **shall** print `motivo: <nome>` and, on the next line, the plain phrase of that reason, identical to the literals fixed in `tests/test_f14_drive_textos.py`, and `gate-verde` **shall** carry `Nada foi publicado.` with the arrow pointing to `sdd-release` | test |
| AT-018 | Event-driven | **When** `sdd-drive.sh --self-test` runs, it **shall** exercise the 12 stop reasons and the exits 0, 2, 10, 20, 40 and 64 over fixtures assembled by the script itself (a project that updates does not receive a new folder of `sdd/fixtures/`), with the red cases before the green ones, in a temporary repository, leaving nothing in the package, exit 0 when all match and exit 2 naming the case that failed | test |
| AT-019 | Ubiquitous | `.agents/skills/sdd-drive/SKILL.md` **shall** follow the script: each `ACAO:` mapped to who does it, fresh context per task by the ladder of `contexto-fresco.md`, the block `<<<RODADA` of the executor, the opening sentence with the limit and `paro antes de publicar`, how to run `verificar --fundo` and come back with `proximo` when the gate takes longer than the agent's command limit, the `[D4 · limite de tentativas]` question at `orcamento-rodadas` with what kept failing and the options fix the DESIGN (recommended), 1 more round, stop, `não sei`; the `[D2 · muda o produto]` question at `gate-alterado` with both commands and the options restore the old one (recommended), accept the new one, `não sei`; `[auto · de rotina]` following the recommended option during the run with a receipt in the DRIVE_REPORT, the other marks always asked, and a hard barrier sentence before `sdd-release`; the 12 reasons and the exits **shall** be identical in the skill, in the script, in `sdd/WORKFLOW_CONTRACTS.yaml` and in `docs/sdd-drive.md`; `skill-lint.py --conversa` **shall** exit 0 | test |
| AT-020 | Unwanted | **If** an agent has no subagent, **then** the skill **shall** record the brief `sdd/reports/briefs/BRIEF_executor-drive_<F>.md` and run `sdd-drive.sh aguardar`, and `sdd-fluxo.sh despachar executor-drive` **shall** print a stop that names the next task and the block `<<<RODADA` and contains `nada foi publicado`; the first stop of a run **shall** warn that there are up to n stops, one per task | test |
| AT-021 | Ubiquitous | The 0b pass of `sdd-release` **shall** state, in this order: list the changed surfaces from the diff (signature or return shape, column, route, permission, command, config slot); one fresh subagent per surface with the brief `references/raio-de-impacto.md`, in parallel when the agent has subagents and sequential in the same session when it has none; the brief **shall** ask for the unmodified consumers, the invariants of `sdd/invariants.md` that touch the module, and `arquivo:linha`; a diff with no surface **shall** be declared skipped; a project without `sdd/invariants.md` **shall** have that said | test |
| AT-022 | Event-driven | **When** `deploy-do-sha.sh --commit <sha> --workflow <arq>` finds a completed successful run of that workflow, on the default branch, with `event` `push` or `workflow_dispatch`, for that SHA, the script **shall** print `✅ no ar` with the run id and short SHA, the only form with ✅ besides the replacement of AT-023, and exit 0; a run of the same SHA on another branch or tag, or with another event such as `schedule`, **shall not** count; a run in progress **shall** be waited for, up to `--teto` seconds, default 2400, with `--intervalo` seconds between queries, default 15, and progress lines `⏳ <status> · m/M min · run <id>` on stderr at most once a minute or when the state changes | test |
| AT-023 | Event-driven | **When** the run of the SHA ended without `success` (`cancelled`, `failure`, `timed_out` or another) and a newer run of the same workflow, on the default branch, of a commit that contains it (`git merge-base --is-ancestor`) ended `success`, the script **shall** print `✅ no ar via substituto` naming both, and exit 0; **if** the query cannot tell whether a newer commit contains it (exit outside 0 and 1, after one `git fetch`), **then** it **shall** keep waiting and at the ceiling exit 4, never 0 and never 2 | test |
| AT-024 | Event-driven | **When** the run of the SHA ended `failure` in a step listed in `deploy.transient_steps` or `--transitorios`, the commit is still the tip of the default branch after `git fetch`, no newer run exists and no redispatch was made for that SHA (a mark in the common git folder, or a run with `event` `workflow_dispatch`), the script **shall** run `gh workflow run <arq> --ref <branch>` once, record the mark and keep waiting for the new run; with no new run listed after `--sem-run` seconds it **shall** exit 4, never 2; it **shall** never run `gh run rerun` | test |
| AT-025 | Unwanted | **If** the failed step is not in the list, the list is empty, the commit is no longer the tip, the fetch failed, a redispatch was already made, or the ceiling has passed, **then** the script **shall not** redispatch and **shall** print `🔴 falhou` with the run, the step and the reason, and exit 2; **if** GitHub refuses the dispatch, **then** it **shall** exit 2 saying that the workflow needs `workflow_dispatch` or a new push | test |
| AT-026 | Unwanted | **If** no run of the SHA is listed after `--sem-run` seconds, default 120, **then** the script **shall** exit 4 saying it did not find the run and never that there is nothing to verify; **if** the ceiling passes with a run unfinished, **then** it **shall** exit 4 naming it and saying that this is not a failure, and with the last query error when a query was failing; **if** `gh` or `git` is missing or `gh` has no login, **then** exit 3 with `inconclusivo`; a usage error, an unknown SHA or no workflow in the flag or the slot **shall** exit 64 | test |
| AT-027 | Ubiquitous | Item 10 of `sdd-release` **shall** call `bash sdd/bin/deploy-do-sha.sh`, map each of the exits 0, 2, 3, 4 and 64 to what to say, say how to wait in the background or repeat the call when the agent has no background, and keep the drift check, the smoke and the warning that a green run does not prove tests; the logic of `gh run list`, `merge-base` and the redispatch **shall** leave the skill text | test |
| AT-028 | Event-driven | **When** `sdd-archive.py` runs without `--aplicar` at the root of a repository, the script **shall** list per lot `com-ledger` (group with `sdd/releases/<F>/`, quiet for `--dias-a`, default 30), `sem-ledger` (group without it and with a document in `sdd/features/`, quiet for `--dias-b`, default 60) and `soltos` (report or review with no such group, quiet for `--dias-b`, destination `sdd/archive/_REPORTS_<AAAA-MM>/`), plus protected with the reason, recent, unclassified, subfolders and totals, end with `Nada foi movido.`, change nothing and exit 0 | test |
| AT-029 | Event-driven | **When** `--lote <nome> --aplicar` runs, the script **shall** run `git mv` only for tracked files of that lot, leave them staged without committing, say that it moved N files with `git mv`, that nothing was deleted and to review and commit, and exit 0; an untracked file **shall** be listed and skipped, an existing destination **shall** be warned about and skipped, and a failing `git mv` **shall** exit 2 | test |
| AT-030 | Unwanted | **If** the feature, whatever the case of its name or a lowercase slice suffix in the record's name, has `sdd/handoffs/HANDOFF_<F>.md` whose `Status` field does not start with `✅` (the same rule of `handoff-lint.py`), or its name or a document of its group, or a loose document, is cited in an open record, **then** the group **shall** be protected and **shall not** be moved; `sdd/releases/`, `sdd/archive/`, `sdd/reports/evidence/` and every subfolder **shall** never be moved; `--aplicar` without `--lote` **shall** exit 64 and running outside a repository or without `sdd/` **shall** exit 2 | test |
| AT-031 | Ubiquitous | The release **shall** state, at steps 5 and 11, the changelog conflict rule that does not depend on the side (`git show origin/<default_branch>:CHANGELOG.md > CHANGELOG.md`, then prepend the new entry) and, at step 15b, that the retroactive cleanup is `sdd-archive.py`, dry-run first | test |
| AT-032 | Event-driven | **When** `avaliador-guard.sh` runs, an untracked file under `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` or `sdd/reviews/` **shall not** make it exit 1, and the script **shall** say how many such documents stay out of the commit and that they do not come back if the folder is cleaned | test |
| AT-033 | Unwanted | **If** a tracked file under those folders changed, outside `sdd/reports/evidence/`, or an untracked file exists anywhere else, **then** `avaliador-guard.sh` **shall continue to** exit 1 listing it | test |
| AT-034 | Unwanted | **If** a line of a harvested log starts with `$ ` or is a shell trace (`+ `), or is a diagnostic of the curator or of `playbook-lint.sh` (`❌ delta linha N:`, `❌ invariantes linha N:`, `🔴 trava INV:`, `<arquivo>.md:<linha>: ❌ `), also after the `│` prefix of the gate, **then** `--colher` **shall not** count it as a finding, and a real finding line citing `LM-nnn` in the same log **shall continue to** produce `DELTA LM-nnn mordeu+1` | test |
| AT-035 | Ubiquitous | `sdd/config.example.yaml` **shall** carry `drive.max_rounds: 3`, `deploy.workflow: ""` and `deploy.transient_steps: ""` with comments; `drive.max_tokens` **shall not** exist; the slot `deploy.transient_steps` **shall** be read as a comma-separated list, empty meaning never redispatch | test |
| AT-036 | Ubiquitous | `docs/sdd-drive.md` and `docs/pt-BR/sdd-drive.md` **shall** exist and open from the README; the `sdd-drive` row **shall** leave `docs/roadmap.md` and its Portuguese version; README, guide and `AGENTS.md.tmpl` **shall** list 19 skills; every new file **shall** be in `MANIFEST.txt` | test |
| AT-037 | Ubiquitous | Scripts of the previous fronts **shall continue to** keep their exits and contracts, with `verify-gate.sh --checar` (exits 0, 5, 64, with `kind: xyz` and a non-executable `cmd` at 64 and `manual-ux` at 0, without running `cmd` nor writing a trace), the line `manual_fallback:` of `--print` and `sdd-fluxo.sh seguir … --drive` (which still stops at `release` with D1) as additions: `verify-gate.sh`, `sdd-fluxo.sh`, `report-lint.py`, `adversarial-review.sh`, `playbook-curator.sh` and `sdd/hooks/`; the OK block of `sdd-release` **shall continue to** keep its labels, order and single question | test |
| AT-038 | Event-driven | **When** a real agent outside Claude runs the skill over a small project with a fixture DEFINE, after the last fix, the transcript **shall** show `sdd-drive.sh iniciar`, a stop at exit 40 or a fresh context per task, `verificar` run through the script and the final `concluir` or a tabled stop, the report naming the model; the proof **shall** read the effect (state file, DRIVE_REPORT, commits when the sandbox allows them), never the text the agent wrote; this AT is proved by `sdd/reports/evidence/F14_DRIVE/AT-038.log`, outside the `cmd` of the gate, because it needs a real agent | test |

Considerados: While — `manual-ux` e a retomada cobrem o estado de espera; Where — a degradação sem subagente está em AT-020 e AT-021. Bugfix com `shall continue to` em AT-033, AT-034 e AT-037. O DEFINE passa de ~10 ATs porque a frente tem 4 mecanismos com contrato de exit, como as anteriores; cada AT é uma saída observável.

---

## Clarifications

### Session 2026-11-05

- Q: Quanto do `sdd-drive` entra? → A: inteiro.
- Q: O que conta como 1 rodada? → A: a passada inteira + gate; `drive.max_rounds: 3` são 3 tentativas de ficar verde.
- Q: Quais pendências entram? → A: só a guarda do avaliador e a L10; as outras 8 seguem registradas.
- Q: Quem faz o 2º revisor e a prova fora do Claude? → A: `deepseek/deepseek-v4-pro` pela OpenRouter; achado desse modelo é medido antes de virar conserto.
- Q: Como o projeto informa o workflow e os passos passageiros? → A: 2 slots, `deploy.workflow` e `deploy.transient_steps`.
- Nota: o plano diz `--ours`; a revisão mediu que esse lado depende da operação. O efeito pedido (a versão da branch padrão, com a entrada nova no topo) sai por `git show origin/<default_branch>:CHANGELOG.md`.
- Q: O que acontece se o bloco do gate mudar no meio? → A: para com `gate-alterado`, e a pessoa decide (`--resume --aceitar-gate-novo`).
- Nota: o checkpoint 2 mostrou 8 motivos; a tabela final tem 12. Os 4 a mais são `gate-alterado` (decisão acima), `simulacao`, `estado-invalido` e `branch-padrao`, que dão nome a comportamentos já aprovados. Aviso dado ao Roberto na pergunta do `gate-alterado`.
- Nota: a passada não tem teto de tarefas (o contra aceito na decisão da rodada), mas a mesma tarefa sem avançar para na 3ª vez (AT-007), o mesmo teto da escada de retry de `modos-e-retry.md`.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

---

## Out of Scope

- Limite de tokens (`drive.max_tokens`) e contador separado de revisões do DESIGN.
- Modo paralelo `briefs` dentro do drive; o drive reaproveita só o ralph.
- O script chamar o programa do agente: quem executa a ação é o agente.
- Ponto de extensão do smoke visual (F15); colheita de permissões de um agente só.
- As pendências L7, N-L9, N-L10, o resto de N-L11 e F5, F6, F7 e a guarda de F9 da fronteira.
- Alterar o repositório privado ou o sdd-starter; F15, F16 e F17.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Piso bash 3.2 e Python 3.9 stdlib; git >= 2.20 | núcleo em Python embutido no script bash; `%cs` do `git log` não vale (é do 2.21); nomes de arquivo por `-z`, sem quote |
| Technical | Os testes rodam numa cópia de `git archive`, sem `.git` | testes do drive e do archive montam repositório próprio na sandbox |
| Technical | Delta-only nas skills existentes (regra 7 do 8.0) | `sdd-release` muda em 0b, 10, 11 e 15b; os outros passos ficam |
| Technical | Padrão agnóstico (P2) e regra 10 do 8.0 | a skill não cita ferramenta de um agente só; sem subagente, a parada é o exit 40 |
| Technical | O bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só | o raio de impacto alimenta o Veredito, sem pergunta nova |
| Technical | `sdd-decisoes-lint.sh --sites` conta as perguntas | as perguntas novas do drive mudam a contagem em `tests/test_decisoes_lint.py` |
| Other | Específico da RDD não viaja (regra 4 do 8.0) | nomes de workflow, passos de SSH, memória e `dev-loop-executor` saem |
| Other | `sdd/features`, `handoffs`, `reports`, `reviews` e `traces` nunca entram em commit da branch | este repositório continua com os 4 de fora; o AT-032 deixa de exigir `--permitir` aqui |
| Other | Push em `main` só com OK citando "sdd-open"; review externo obrigatório | `v2.7.0` com `git push --atomic` |
| Resource | CI: tetos de 25 min (Ubuntu) e 45 min (macOS); hoje 17m41s e 29m22s | testes novos sem rede e sem gate caro; gate de fixture com `cmd: true` |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/sdd-drive.sh`, `sdd/bin/deploy-do-sha.sh`, `sdd/bin/sdd-archive.py`, `sdd/bin/avaliador-guard.sh`, `sdd/bin/playbook-curator.sh`, `sdd/bin/sdd-fluxo.sh`, `.agents/skills/sdd-drive/`, `.agents/skills/sdd-release/`, `sdd/config.example.yaml`, `sdd/WORKFLOW_CONTRACTS.yaml`, `docs/`, `tests/` | pacote; o projeto do usuário recebe pelo `init`/`sync` |
| **KB Domains** | nenhum | o pacote não tem `sdd/kb/` próprio |
| **IaC Impact** | None | os caminhos que publicam já cobrem o que muda; `release.yml` fica igual |
| **LLM Prompts** | false | os briefs são instrução do método para um agente de código; nenhum provedor é chamado por código do pacote nesta frente. Sinal de loop anotado: "até convergir" é a função do drive, e o laço é de script, não de modelo em produção |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | passo 1.5 do `sdd-define` |
| **Governança** | N.A. — o DEFINE trata só de ferramenta do método (drive, verificação de deploy, faxina de documentos do SDD), sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha nem dado pessoal | revisor fresco, 2026-11-05 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O agente segue a próxima ação do script em vez de improvisar | o limite de rodadas segue valendo pelo script, mas uma ação pode ser pulada | no — AT-038 testa num agente real |
| A-002 | `gh run list --commit <sha> --branch <b> --json …` filtra pela branch; o run de tag tem `headBranch` igual à tag | um run de tag contaria como da branch; o script filtra também pelo campo | yes — medido em `8a320e9` (run da tag com `headBranch: v2.6.0`) |
| A-003 | Uma feature sem subagente aceita 1 parada por tarefa | a execução fica lenta nesses agentes | yes — a tabela de degradação do plano aceita |
| A-004 | A suíte com os testes novos cabe nos tetos de 25 e 45 minutos | ajustar os tetos, como na F12 | no — medida no CI do PR |
| A-005 | O commit se prova no Codex com o git fora da pasta da sandbox | a prova fica sem o commit, e o relatório diz | no — a conferir na prova |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | dor, afetados e motivo presentes |
| Users | 3 | 5 usuários com dor específica |
| Goals | 3 | MUST e SHOULD por item do plano |
| Success | 2 | a maioria é saída exata; o tempo de CI só se mede no PR |
| Scope | 3 | cortes e 8 pendências confirmados pelo Roberto |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-05 | SDD Define by RDD | Initial version |
| 1.9 | 2026-11-06 | revisão real, rodada 4 | R4 de Claude no AT-006; 1 verbo por vez no estado, sem mudar AT |
| 1.8 | 2026-11-05 | revisão real, rodada 2 | sem mudança de AT: a repetição conta a posição da tarefa; `--resume` com gate rodando responde `ESPERAR`; `define-invalido` também para fora de UTF-8 |
| 1.7 | 2026-11-05 | revisão real, rodada 1 | R2 no AT-007; R3 no AT-005; R11 no AT-034; R1@deepseek no AT-002 |
| 1.6 | 2026-11-05 | avaliador, ciclo 3 | M2 no AT-010: só documento exige pasta e extensão de documento |
| 1.5 | 2026-11-05 | avaliador, ciclo 2 | L12 no AT-015: a recusa de um 2º `iniciar` não é parada da execução em curso |
| 1.4 | 2026-11-05 | avaliador, ciclo 1 | H1, M1 no AT-008; M4 no AT-013; M9 no AT-014; L10 no AT-018; M5 a M8 no AT-030 |
| 1.3 | 2026-11-05 | revisão do DESIGN | A1 a A5, H1 a H4, M1, M3 a M8, M9 a M14, L5 a L8 nos ATs (`REVISAO_DESIGN_F14_DRIVE_20261105.md`); ação `ESPERAR` e `verificar --fundo` |
| 1.2 | 2026-11-05 | sdd-design | `--checar` e `--drive` (AT-002, AT-037); `COMMITAR` sem contar relatórios e `CORRIGIR` sem commit novo (AT-010); verbo `recibo` (AT-016) |
| 1.1 | 2026-11-05 | sdd-ux-review | U1, U2 em AT-015 e AT-017; U3 em AT-005 e AT-008; U4, U5 em AT-019; U6 em AT-012; U7 em AT-022 e AT-026; U8 em AT-020; U9 em AT-028 e AT-029; U12 em AT-032 |

---

## Next Step

Execute o **SDD Design by RDD**.
