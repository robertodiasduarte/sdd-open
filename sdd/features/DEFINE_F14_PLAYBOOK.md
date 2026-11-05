# DEFINE: F14 Playbook, invariantes e sessão

> A curadoria do playbook deixa de ser um parágrafo de instrução: um script colhe, um agente sem a conversa julga, um conferidor reprova tabela incompleta, a contagem com prova entra sozinha e a mudança de regra vira pergunta; nasce o registro de invariantes com trava; a frente nova recebe os documentos de papel da feature; o molde do handoff ganha as seções que o handoff real usa.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_PLAYBOOK |
| **Date** | 2026-11-05 |
| **Author** | SDD Define by RDD (sessão 11, Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

No Open, a curadoria do playbook é um parágrafo do passo 17b da `sdd-release`: o agente colhe à mão, nada distingue falha de coleta de "nada a colher", contagem e mudança de regra chegam misturadas à pessoa, e não existe registro de invariantes. A frente nova nasce sem os documentos SDD ainda não salvos no git, e o molde do handoff não tem as seções que o handoff real usa. O privado resolve os quatro, e o Open precisa fazê-lo para substituí-lo na F15.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem publica | roda a `sdd-release` até o passo da curadoria | responde a uma lista de deltas montada à mão, sem saber o que é contagem e o que muda a regra do método |
| Quem mantém o playbook de um projeto | lê e aprova as mudanças em `sdd/playbook.md` | lição que mordeu 2 vezes não vira trava; aposentar uma landmine pode deixar uma regra permanente sem origem |
| Quem abre uma frente | roda a `sdd-new-session` | BRAINSTORM, DEFINE e DESIGN escritos no checkout principal ficam invisíveis na pasta nova e são copiados à mão |
| Quem retoma uma feature | lê o handoff gerado do molde | o molde não tem eventos, recomendações, veredito, preparo, tarefas numeradas nem limpeza |
| O Roberto na F15 | troca o privado pelo Open | precisa do curator, das invariantes e do molde completo no Open para remover os do privado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/playbook-curator.sh --colher`: ajudou e mordeu de tabela, mordeu de achado, sugestão por termo de `sup:`, candidato ou rejeitado, pergunta de promoção, `--desde`, trace (P1) |
| **MUST** | `--aplicar`: valida o delta inteiro antes de editar; inválido sai 2 sem imprimir nada (P1) |
| **MUST** | `sdd/invariants.md` com gramática própria, `--cruzar` e a trava `--validar-inv` escritas no próprio script (C5) |
| **MUST** | Brief `sdd-playbook/references/curator.md`: agente que só lê, devolve o bloco de curadoria, registra contaminação; `--conferir-bloco` reprova linha da colheita ausente e aceite sem `arquivo:linha` (P2) |
| **MUST** | `sdd-release`, passo 17b: contagem com evidência aplicada sem pergunta; ADD, TOMBSTONE, PROMOVER e mudança em invariante numa pergunta `[D3 · muda a regra do método]` (P3) |
| **MUST** | Robustez do 17b: saída 2 ou 64 da colheita não é "0 deltas"; staging por cópia; evidência `CURATOR-*.log`; commit à parte com os IDs reconferidos contra a base (P4) |
| **MUST** | `sdd-new-session` copia os documentos de papel não salvos no git só com nome idêntico ao da frente, e lista os parecidos sem copiar (N1) |
| **MUST** | `sdd/templates/HANDOFF_TEMPLATE.md` com as 6 seções que faltam (N3) |
| **MUST** | A suíte não herda `SDD_TRACE` de quem a chama (🐛 da F12) |
| **MUST** | Revisão focada, em contexto fresco, da fronteira de escrita e da restauração do DEFINE (risco aceito na F12), com os achados MEDIUM corrigidos |
| **SHOULD** | Pendências LOW da F13 no `design-lint.py` e no `prompt-drift-scan.sh` |
| **SHOULD** | `docs/playbook-curation.md` + PT, README e guia do aluno com a curadoria |
| **SHOULD** | Prova num agente de fora do Claude: o despacho do curador com parada e o brief seguido sobre as fixtures |

---

## Success Criteria

- [ ] `SDD_TRACE=off bash sdd/bin/playbook-curator.sh --colher sdd/fixtures/playbook/curadoria sdd/fixtures/playbook/curadoria/playbook-base.md` sai 0 e imprime linhas `DELTA`, `SUGESTAO`, `CANDIDATO` ou `REJEITADO`, e, com `playbook-mordeu2.md`, `PROMOVER?`.
- [ ] `--aplicar` com ID inexistente sai 2 com stdout vazio; delta só de contadores atravessa `playbook-lint.sh --anti-collapse` com 0 alterados.
- [ ] `bash sdd/bin/playbook-curator.sh --validar-inv sdd/playbook.md sdd/invariants.md` sai 0 no pacote; TOMBSTONE de origem sem ajuste sai 2, e com o ajuste do `--cruzar` sai 0.
- [ ] `--conferir-bloco` sai 2 para cada um dos defeitos de bloco do AT-020 e 0 para o bloco de exemplo.
- [ ] `bash sdd/bin/playbook-curator.sh --self-test` sai 0, com os vermelhos antes dos verdes, sem gravar trace nem arquivo no repositório.
- [ ] `copiar-docs.sh` copia 1 documento de nome idêntico, lista 1 parecido e não sobrescreve destino existente.
- [ ] `SDD_TRACE=off SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_verify_gate_trace.py'` sai 0.
- [ ] Os scripts novos sem achado em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'`; baseline vermelha na `v2.5.0`; 1 sabotagem por script novo derruba o teste correspondente.
- [ ] `skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 nas 18 skills; `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` sai 0; `check-versions.py --base v2.5.0 --base-obrigatoria` sai 0.
- [ ] `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F14_PLAYBOOK.md` sai 0; CI verde em `ubuntu-latest` e `macos-latest` dentro dos tetos de 25 e 45 minutos.
- [ ] Revisão adversarial real com `loop` PRONTO e `--conferir` CONFERE no commit final; Release `v2.6.0` por tag, com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `playbook-curator.sh --colher <dir> <playbook>` reads a `DESIGN_*.md` or `BUILD_REPORT_*.md` whose section `## Landmines aplicáveis` or `## Landmines lidas no build` has a table, the script **shall** read it by its header: the ID from the `Fonte`, `LM-nnn` or `ID` column and the verdict from the `Veredito` or `Tratamento` column, and **shall** print `DELTA LM-nnn ajudou+1 · conf=<today> · evidencia=<file>:<line>` when that verdict starts with `✔`, `DELTA LM-nnn mordeu+1 …` when it starts with the word `mordeu`, at any length (also `**mordeu**`), and nothing otherwise; a bullet cited only in another column **shall not** get a count; a table without those columns **shall** count nothing and print `TABELA_SEM_CABECALHO <file>:<line>`; a row citing `LM-nnn` outside those 2 sections **shall not** produce a delta | test |
| AT-002 | Event-driven | **When** a line of `AVAL*-*.log`, `AVALIACAO_*.md`, `*.yaml`, `BUILD_REPORT_*.md` or `HANDOFF_*.md` in the directory carries a finding mark (`❌`, `NEEDS_WORK`, `FAIL` as a whole word, `WAIVED`, `mordeu_antes:`) and cites `LM-nnn`, the script **shall** print `DELTA LM-nnn mordeu+1 … evidencia=<file>:<line>`; a line that also has `✅`, a line inside those 2 landmines tables, and `FAIL` inside a longer identifier (`FORCE_FAIL`), **shall not** count | test |
| AT-003 | Event-driven | **When** a finding line cites no `LM-nnn` but contains a `sup:` term of an active bullet with 6 or more characters and not only digits, the script **shall** print `SUGESTAO mordeu? LM-nnn — termo …` with the file and line, and **shall not** print a `DELTA` for it | test |
| AT-004 | Event-driven | **When** a `BUILD_REPORT_*.md` or `HANDOFF_*.md` has a candidate block (opened by `<<<CANDIDATO_PLAYBOOK`, closed by `>>>`) with `secao`, `sup` in backticks, `regra` with `Do instead:` (inline or as its own key) and `evidencia`, the script **shall** print `CANDIDATO #n → LM-<max+1> · secao=… · sup=… · evidencia=…` followed by one `   delta: ADD …` line that joins indented continuations, numbering from the highest ID among active bullets and tombstones | test |
| AT-005 | Unwanted | **If** a candidate block lacks `evidencia`, names a section outside the active ones, has `sup` without a backtick term or has no `Do instead:`, **then** the script **shall** print `REJEITADO candidato em <file>:<line> — <motivo>` and **shall not** print a `CANDIDATO` for it | test |
| AT-006 | Event-driven | **When** the playbook has an active bullet with `mordeu` at or above 2 and `promovido_para: —`, the script **shall** print `PROMOVER? LM-nnn mordeu=N …` with a mechanism suggestion among the 3 destinations of the package (hook in `sdd/hooks/`, the command of `release.landmines_cmd`, an assertion in the Verify Gate), even when the directory yields no delta | test |
| AT-007 | Ubiquitous | `--colher` **shall** print one delta per bullet and kind per run, `IGNORADO LM-nnn` once for a cited ID that is not an active bullet, and the summary line `resumo: deltas=N (ajudou=A mordeu=M) candidatos=C rejeitados=R promocoes=P sugestoes=S` right before `RESULTADO:`; it **shall** exit 0 with at least 1 line of any of those kinds, including `IGNORADO`, `JA_COLHIDO` and `INV_PENDENTE`, 1 with none (stderr `0 deltas colhidos`), 2 when the playbook is missing, has no `[LM-nnn]` bullet or the `--inv` file is missing, and 64 on a usage error or a missing directory; any unexpected error, such as a file it cannot read, **shall** exit 2 with the cause and `RESULTADO: FALHA`, never 1 and never a traceback | test |
| AT-008 | Event-driven | **When** `--desde YYYY-MM-DD` is given and the date of a `DESIGN_*.md` or `BUILD_REPORT_*.md` is earlier, the script **shall** print `JA_COLHIDO <file> …` and no delta from that file; a malformed date **shall** exit 64 | test |
| AT-009 | Event-driven | **When** `--colher` ends, the script **shall** append one JSONL line per feature of the directory to the trace folder (`SDD_TRACE_DIR`, default `sdd/traces`) with `src` `curator`, `kind` `colher`, the exit and the 7 counters, with the feature name sanitized; with `SDD_TRACE=off`, or with no report or design in the directory, it **shall** write nothing | test |
| AT-010 | Ubiquitous | The curator **shall** accept as section names the list of `PLAYBOOK_SECTIONS`, with the same default list as `playbook-lint.sh`, and `Tombstones` **shall** never receive an `ADD` | test |
| AT-011 | Event-driven | **When** `--aplicar <delta> <playbook> [conf=YYYY-MM-DD]` receives a valid delta, the script **shall** print the new playbook on stdout and exit 0: counters added, `conf=` renewed on touched bullets, `promovido_para:` set, each `ADD` appended at the end of its section with the next ID (a section of the list that the playbook lacks **shall** be created in its place), each `TOMBSTONE` moved to `## Tombstones` as `- [LM-nnn] ☠ <date> :: <motivo>`, each `REFINE` replacing the text after `::`, continuation lines kept; the output **shall** pass `playbook-lint.sh`; a delta with only comments **shall** print the input unchanged; stdout **shall** hold only the playbook, with `RESULTADO:` and the `→` line on stderr | test |
| AT-012 | Unwanted | **If** any delta line is outside the grammar, cites an ID that is not an active bullet, adds to a section outside the list or to `Tombstones`, or is an `ADD` or `REFINE` without `Do instead:`, **then** `--aplicar` **shall** print each error with its line number on stderr, print nothing on stdout and exit 2 | test |
| AT-013 | Ubiquitous | A counters-only delta applied by `--aplicar` **shall** pass `playbook-lint.sh --anti-collapse <before> <after>` with 0 changed bullets | test |
| AT-014 | Ubiquitous | `sdd/invariants.md` **shall** ship with the grammar `- [INV-NNN] estado=ok\|auto\|humano origem=seed\|LM-nnn[,LM-mmm] [check=<path>] :: <regra> · por quê: <texto> [· tarefa: … \| · motivo: …]` under `## Invariantes`, an optional `## Descartados` with `- [LM-nnn] descartado :: <motivo>`, and `playbook-curator.sh --validar-inv sdd/playbook.md sdd/invariants.md` **shall** exit 0 on the package | test |
| AT-015 | Unwanted | **If** the pair has an invariant whose origin is a tombstone or does not exist, an active bullet with `mordeu` at or above 1 or a filled `promovido_para`, also on a continuation line, that is neither an origin nor discarded, a repeated `INV` or discard ID, a line outside the grammar below the first invariant, `estado=auto` without `· tarefa:`, `estado=humano` without `· motivo:`, `estado=ok` with neither `check=` nor an origin promoted to a file that exists, a `check=` path that does not exist, is absolute, leaves the root (also through a symbolic link) or is a folder (a path under `.github/` is legitimate), an empty `· tarefa:` or `· motivo:`, or a discarded bullet that is a tombstone, **then** `--validar-inv` **shall** print one `🔴 trava INV: …` line per defect naming the ID and the ways out, and exit 2; a missing file **shall** exit 2; when the only defects are unclassified bullets, the first line **shall** say that the invariants record is new in v2.6.0 and how many old lessons are still unclassified | test |
| AT-016 | Event-driven | **When** `--cruzar <delta\|-> <playbook> <invariants>` receives a delta that retires an origin, the script **shall** print `INV_AFETADA INV-nnn …`, one `   ajuste:` line with the full new invariant line (remaining origins; sole origin becomes `origem=seed`, with `check=` taken from the retired bullet's `promovido_para`; 2 retired origins of the same invariant give 1 adjustment) and `   ou: retirar o TOMBSTONE …`; for a retired discarded bullet, `INV_AFETADA descarte LM-nnn`; for a delta that puts a bullet in the universe (`mordeu` from 0, or `promovido_para`) without classification, `INV_PENDENTE LM-nnn` with proposal A (`INV-<max+1>`, sequential) and proposal B (discard); the summary line right before `RESULTADO:` **shall** be `resumo-inv: afetadas=N pendentes=M`, the exit 3 with any notice and 0 with none; `-` **shall** read the delta from stdin | test |
| AT-017 | Unwanted | **If** the delta given to `--cruzar` is invalid or the invariants file has no `## Invariantes` section, **then** the script **shall** exit 2 with stdout empty; **if** the sole origin has no `promovido_para` and the invariant is `estado=ok` without `check=`, **then** it **shall** print that `origem=seed` is not a valid way out instead of an adjustment | test |
| AT-018 | Event-driven | **When** a `TOMBSTONE` is applied by `--aplicar` and the `ajuste:` line printed by `--cruzar` replaces the invariant line, `--validar-inv` on the new pair **shall** exit 0; without the adjustment it **shall** exit 2 naming the invariant and the bullet | test |
| AT-019 | Event-driven | **When** `--colher` runs with `--inv <invariants>`, the script **shall** append `INV_PENDENTE` for each harvested `mordeu+1` that puts a bullet in the universe without classification and for each bullet already in the universe without classification, with the next IDs in proposal A; a bullet with neither **shall not** appear | test |
| AT-020 | Unwanted | **If** the block given to `--conferir-bloco <colheita> <bloco> <playbook> <selo> <comparar>` lacks the pair `<<<CURADORIA` and `>>>` or the table header, omits a harvest line (`DELTA`, `SUGESTAO`, `CANDIDATO`, `REJEITADO`, `PROMOVER?`, `IGNORADO`, `JA_COLHIDO`, `INV_PENDENTE`), covers a `DELTA` by the LM column and not by the delta cell, repeats a counter or a row number, has an LM column that is not the one ID of the delta, has `AUTO` on a row that is not `contador` or whose ID, verb, `+1` and evidence `file:line` are not exactly those of one `DELTA` line of the harvest, has `ACEITAR` without an evidence `file:line` that exists in the harvest directory, has a promotion row whose recommendation is not `PERGUNTA OBRIGATÓRIA`, has a plain-language cell empty or only a dash, cites the harvest itself as evidence, has `DESCARTAR` without the reason, lacks the `CONTAMINAÇÃO:` line or leaves it without `não` or `sim`, has a delta cell outside the grammar, or **if** the boundary output has `FORA:` or lacks `RESULTADO: SÓ O PERMITIDO MUDOU`, or any file of the staging folder, derived or not, differs from the seal printed by `--selar`, **then** the script **shall** print each defect and exit 2 | test |
| AT-021 | Event-driven | **When** the block is valid, `--conferir-bloco` **shall** print one `AUTO <delta>` line per counter row recommended `AUTO`, one `PERGUNTA <n> <tipo> <delta>` line per policy row (`add`, `tombstone`, `refine`, `promover`, `inv`) and per `sugestao` row accepted by the curator, a summary line `resumo-bloco: auto=N pergunta=M descartar=K nao_julgado=J contaminacao=sim\|nao`, and exit 0; a `mordeu` counter of a bullet with `INV_PENDENTE` in the harvest **shall** be printed as `PERGUNTA`, never `AUTO`; with `CONTAMINAÇÃO: sim` it **shall** also print an `AVISO` line | test |
| AT-022 | Event-driven | **When** `playbook-curator.sh --self-test` runs, it **shall** check the red cases before the green ones over `sdd/fixtures/playbook/curadoria/`, exit 0 when all match and exit 2 naming the case that failed, without writing a trace in the repository nor leaving a file behind | test |
| AT-023 | Ubiquitous | `.agents/skills/sdd-playbook/references/curator.md` **shall** state the 5 input fields, the prohibitions (never writes), the return block and the dispatch ladder; the fields, the row types and the recommendations **shall** be identical in the brief, in `playbook-curator.sh` and in `sdd/WORKFLOW_CONTRACTS.yaml`; `sdd-fluxo.sh despachar curador <F> <brief>` **shall** save the brief, print a stop containing `A publicação já terminou e não depende deste passo`, `<<<CURADORIA` and `a curadoria do playbook ainda não foi aplicada`, not containing `nada foi publicado` nor `começa a ler o DEFINE`, and exit 40; any other role **shall not** get the publication sentence | test |
| AT-024 | Ubiquitous | Step 17b of `.agents/skills/sdd-release/SKILL.md` **shall** state, in this order: staging by copy (`--preparar`; `--retomar` in a new session); harvest with the exit read (0 goes on; 1 registers `Curadoria: 0 deltas`; any other exit stops the step and registers `Curadoria: FALHOU (rc=N)`); brief, seal, boundary snapshot, dispatch with only the 5 fields, comparison; `--conferir-bloco` before any question, with one redispatch and then `Curadoria: FALHOU (bloco inválido)` with nothing applied; `AUTO` rows applied without a question and listed in the receipt; `PERGUNTA` rows in `[D3 · muda a regra do método]` questions, with the invariant adjustment in the same option and each rejected candidate told in words; `--aplicar` to a copy, then `playbook-lint.sh`, `--anti-collapse`, `--aplicar-inv` and `--validar-inv`, then the copy over the playbook; `CURATOR-colheita.log` and `CURATOR-delta.log` in the evidence folder and `CURATOR-colhidos.txt` next to the ledger; a separate commit with only the playbook, the invariants and the register, plus the 2 logs when the project versions its evidence folder; then one `[D1 · não se desfaz]` question about sending that commit to the default branch (yes lands it as in step 5, with the lint and `--validar-inv` run again on the landed base before the push; later keeps the commit on the feature branch and registers the command); the step **shall** give the person the cause and the fix of a failed harvest, saying that the publication was not affected, say in plain words when nothing was harvested, and say how to undo the receipt (revert the curation commit); a project without `sdd/invariants.md` **shall** have the crossing skipped and said; a resuming session **shall not** redo the seal or the snapshot; a redispatch after a write outside the boundary **shall** redo the baseline, or stop when the playbook or the invariants were touched; a lesson promotion accepted **shall** become a pending item, not a delta | test |
| AT-025 | Ubiquitous | The curation question example in `.agents/skills/sdd-release/references/como-falar.md` **shall** carry the mark `[D3 · muda a regra do método]`, numbered items in plain words with the ID only at the end as `(ref: …)`, at most 5 items per question, one single option for a retirement that changes an invariant, the recommended option first and `não sei`, and `skill-lint.py --conversa` and `sdd-decisoes-lint.sh --sites` **shall** exit 0 with the site count updated in `tests/test_decisoes_lint.py` | test |
| AT-026 | Event-driven | **When** `.agents/skills/sdd-new-session/scripts/copiar-docs.sh <principal> <frente> <slug>` runs, it **shall** copy from `sdd/features/` and `sdd/reviews/` of the main checkout each file not saved in git named `BRAINSTORM_`, `DEFINE_`, `DESIGN_`, `UX_REVIEW_` or `GOVERNANCA_REVIEW_` plus a feature whose lowercase hyphenated form without accents equals the slug, creating the destination folder when missing, print `COPIADO <path>` per file, end in `RESULTADO: <N> COPIADO(S)` or `RESULTADO: NADA A COPIAR` plus a `→` line, and exit 0 also when nothing matches | test |
| AT-027 | Unwanted | **If** the destination already exists, **then** the script **shall** print `JA_EXISTE <path>` and keep it; **if** the feature only starts with the slug or the slug with the feature, **then** it **shall** print `PARECIDO <path>` with both names and the reason (the name is not identical), copy nothing, and the `→` line **shall** say where to copy by hand; **if** the source or the destination folder is a symbolic link, **then** it **shall** print `IGNORADO <path>` and copy nothing; **if** a matching document is saved in git in the main checkout and absent in the front, **then** it **shall** print `NAO_COPIADO <path>` and the `→` line **shall** say how to bring it; a missing folder or argument **shall** exit 64 | test |
| AT-028 | Ubiquitous | `.agents/skills/sdd-new-session/SKILL.md` **shall** call `copiar-docs.sh` after the worktree exists and report copied and similar files in plain words | test |
| AT-029 | Ubiquitous | `sdd/templates/HANDOFF_TEMPLATE.md` **shall** have the sections `## Eventos`, `## Recomendações`, `## Veredito`, `## Setup`, `## Tarefas` (numbered) and `## Ship` (with cleanup), and the fixture `HANDOFF_COMPLETO.md`, with those 6 sections conferred by a test (the lint accepts extra sections and does not require them), **shall** pass `python3 sdd/bin/handoff-lint.py` | test |
| AT-030 | State-driven | **While** `SDD_TRACE=off` and `SDD_TRACE_DIR=<dir>` are set in the environment of whoever runs the suite, `python3 -B -m unittest discover -s tests -p 'test_verify_gate_trace.py'` and `… -p 'test_governanca_gate.py'` **shall** exit 0 and `<dir>` **shall** stay absent, because `tests/apoio.py` removes both from the base environment | test |
| AT-031 | Unwanted | **If** a DESIGN has a level-2 heading that starts as the prompts-section heading in the plural, carries extra words, and its body has the inventory subheading, a contract block or an inventory column, **then** `design-lint.py` **shall** exit 1 naming the heading instead of skipping the check; the same kind of heading over an unrelated body (a review of prompts, for example) **shall** still pass; a heading with a dotted numeric prefix (`5.5.`) **shall** be read as the section and checked; **if** the cells `Tom/audiência`, `Tipo de saída` or `Fallback aprovado` hold an unfilled placeholder in braces, also in backticks, **then** it **shall** exit 1 | test |
| AT-032 | Unwanted | **If** `prompts.wrapper_pattern` is a YAML flow list or the `prompts` key opens a flow mapping, **then** `prompt-drift-scan.sh` **shall** exit 64 saying which form it does not read, never treat the slot as empty; its `--self-test` **shall** have 1 case for each exit-64 reason | test |
| AT-033 | Event-driven | **When** the focused fresh-context review of `sdd/bin/governanca-fronteira.sh` and of the DEFINE restore in step 11 of `sdd-define` ends, its report **shall** exist in `sdd/reviews/`, and each HIGH or MEDIUM finding **shall** be applied with a two-sided test or rebutted with the reason in the build report | smoke |
| AT-034 | Event-driven | **When** `sdd-open.sh init` installs the package playbook, it **shall** install `sdd/invariants.md` as shipped; **when** the project already has its own playbook and no `sdd/invariants.md`, it **shall** install the file without any invariant line, because the shipped invariant cites a landmine of the package playbook; with the file present it **shall** keep it; `release.yml` **shall** list `sdd/invariants.md` among the paths that publish | test |
| AT-035 | Ubiquitous | `docs/playbook-curation.md` and `docs/pt-BR/playbook-curation.md` **shall** exist, be linked from the READMEs, and `tests/test_docs.py` **shall** pass with the roadmap still at 3 lines | test |
| AT-036 | Ubiquitous | The new scripts **shall** have no hit for `mapfile`, `declare -A` or uppercase expansion; `skill-lint.py --conversa` **shall** exit 0 on the 18 skills; `tests/test_agnostico.py` **shall** pass; `check-versions.py --base v2.5.0 --base-obrigatoria` **shall** exit 0 with `sdd-playbook`, `sdd-release`, `sdd-new-session` and each other touched skill bumped | test |
| AT-037 | Ubiquitous | `git diff --name-only v2.5.0 HEAD -- sdd/bin/verify-gate.sh sdd/bin/report-lint.py sdd/bin/adversarial-review.sh sdd/hooks` **shall** be empty | smoke |
| AT-038 | Event-driven | **When** an agent other than Claude Code follows step 17b with the condition "no subagent", the transcript **shall** show `sdd-fluxo.sh despachar curador` exiting 40 with the brief at its destination; **when** it follows the brief over the fixtures, the returned block **shall** pass `--conferir-bloco` and the write-boundary comparison **shall** show no write; controls that pass and that fail **shall** run without the agent | smoke |
| AT-040 | Ubiquitous | Every mode of `playbook-curator.sh` other than `--aplicar`, `--aplicar-inv` and `--selar`, whose stdout is a file, **shall** end stdout, or stderr on an error, with `RESULTADO:` plus a `→` line, after the summary line that machines read; no output **shall** depend on color | test |
| AT-041 | Event-driven | **When** `playbook-curator.sh --preparar <F>` runs, it **shall** create the staging folder under the temporary directory with a name derived from the project root and the feature, remove what a previous release left there, copy into it (regular files only, never a link, never moving the original) `DESIGN_<F>.md` and `BUILD_REPORT_<F>.md` (also from `sdd/archive/<F>/`), the `AVAL*-*.log` of the feature's evidence folder, `AVALIACAO_<F>_<8 digits>*.md` (`AVALIACAO_F1_2_…` is not of `F1`), the ledger `*.yaml` and `CURATOR-colhidos.txt` of the feature and `HANDOFF_<F>.md`, and print `staging: <dir>`; a feature with a similar longer name **shall not** be copied; with neither a DESIGN nor a BUILD_REPORT it **shall** exit 1; with `--retomar` it **shall** neither copy nor clean and **shall** say whether a harvest exists; a name outside the alphabet of `sdd-fluxo.sh despachar` **shall** exit 64 | test |
| AT-042 | Unwanted | **If** `playbook-lint.sh --anti-collapse` compares 2 playbooks where exactly 1 bullet changed content, section or became a tombstone, **then** it **shall** pass whatever the size of the playbook; with 2 or more changed and above 20%, it **shall** still block | test |
| AT-043 | Event-driven | **When** `--aplicar-inv <linhas> <invariantes>` receives invariant lines, discard lines and `REMOVER <id>` lines, it **shall** print on stdout the new file with the line of the same ID replaced, new ones appended to their section and removed ones gone, with `RESULTADO:` on stderr; a line outside the grammar, a `REMOVER` of an absent ID, or a line with an existing ID and a different rule (a new invariant with a repeated ID) **shall** exit 2 with stdout empty | test |
| AT-044 | Event-driven | **When** the harvest folder holds `CURATOR-colhidos.txt`, `--colher` **shall** skip every line whose fingerprint (file, kind, ID and line text; not the line number) is listed there and print `JA_JULGADO <n> linha(s)`; every source line of a counted bullet **shall** have its fingerprint on the printed line, so 2 lines of 1 lesson do not count in 2 releases; a new finding citing the same bullet **shall** still count; the same **shall** hold for suggestions and candidates | test |
| AT-045 | Unwanted | **If** between the 2 snapshots of `governanca-fronteira.sh` the branch, the index (`git add`, `--assume-unchanged`, `--skip-worktree`), the local config, `info/exclude` or a hook changed, **then** `--comparar` **shall** print `FORA:` naming it and exit 1, while `git status`, `git diff` and `git log` **shall** keep exit 0; a folder that git cannot open **shall** make `--snapshot` exit 64; a project root with `&` or `\|` **shall** list the exact path; **if** `governanca-bloco.py --comparar` reads `FORA:` or no `RESULTADO: SÓ O PERMITIDO MUDOU`, **then** it **shall** exit 2 whatever the block says; step 11 of `sdd-define` **shall** copy before removing when restoring the DEFINE, and a link placed in the intermediate name **shall not** receive the copy, and it **shall** tell a resuming session not to redo the copy and the snapshot | test |
| AT-039 | Ubiquitous | Each new test file **shall** fail on a copy of `v2.5.0`, and 1 sabotage per new script **shall** make its test fail, both with logs in the evidence folder | smoke |

---

## Clarifications

### Session 2026-11-05

- [x] (Scope) F14 em 2 entregas: esta é a 1ª (`F14_PLAYBOOK`, `v2.6.0`); a orquestração (`sdd-drive`, O2, O3, O4, slot `drive.max_rounds`) é a 2ª, com Define próprio (brainstorm, perguntas 1 a 3).
- [x] (Scope) Pendências LOW da F13 entram aqui (brainstorm, pergunta 5); AT-031 e AT-032.
- [x] (Constraints) Codex sem créditos: o 2º revisor da revisão real é outro modelo via OpenRouter; a prova do AT-038 espera o Roberto liberar um agente de fora do Claude (brainstorm, pergunta 4). Sem agente liberado na hora da prova, é pergunta `[D3 · muda a regra do método]`, não decisão do agente.
- [x] (Edge cases) Contagem com evidência entra sem pergunta; o resto é pergunta (brainstorm, bloco 2); AT-021 e AT-024.
- [x] (Data model) **Decisão do Define:** a trava das invariantes é escrita no `playbook-curator.sh` (abordagem A); o gerador de catálogo do privado não viaja.
- [x] (Data model) **Decisão do Define:** "universo" das invariantes = bullets ativos com `mordeu` ≥ 1 ou `promovido_para` preenchido, como no privado; o `sdd/invariants.md` do pacote nasce classificando a LM-004, que já tem `promovido_para`.
- [x] (Edge cases) **Decisão do Define:** `sdd/invariants.md` ausente no projeto não quebra a curadoria: o passo diz "invariantes: arquivo ausente, cruzamento pulado" e segue só com o playbook. Com o arquivo presente, a trava é obrigatória.
- [x] (Edge cases) **Decisão do Define:** as fontes de achado ganham `AVALIACAO_*.md` e `HANDOFF_*.md` (os relatórios do avaliador e a ficha do Open) no lugar da memória `project_handoff_*` do privado.
- [x] (Edge cases) **Decisão do Define:** quem decide o que é `AUTO` é o `--conferir-bloco`, não o texto da skill: só linha de contador que existe na colheita e tem `arquivo:linha` que abre no staging.
- [x] (Edge cases) **Decisão do Define:** o curador é provado só-leitura pelo `governanca-fronteira.sh` (snapshot antes, comparação depois), o mesmo mecanismo do revisor de governança; sem isso "nunca escreve" seria regra de texto.
- [x] (Edge cases) **Decisão do Define:** `copiar-docs.sh` copia também arquivo ignorado pelo git (o privado só via os não rastreados e não ignorados): na pasta nova o mesmo `.gitignore` vale, então nada vaza para o commit.
- [x] (UX flow) Interface desta feature: 2 scripts de linha de comando, texto de 4 skills, 1 molde e documentação; sem tela. A UX review roda sobre esse texto.
- [x] (Edge cases) **Decisão do Design:** o commit da curadoria só sai da máquina com uma pergunta D1 (no sdd-open, um push em `main` que toca `sdd/playbook.md` publica uma Release); o staging vira o modo `--preparar` (AT-041); o `--anti-collapse` ganha piso de 1 alterado, senão nenhuma promoção ou aposentadoria passa num playbook de até 4 bullets (AT-042).
- [x] (Done signal) **Revisão fresca do DESIGN, P5:** o `cmd` do gate fica como o prompt da sessão fixou (RECUSADA a mudança, como na F13); `check-versions` e AT-037 ficam com log no repositório, e o Build não fecha sem eles. A existência dos 6 arquivos de teste novos é conferida por teste.
- [x] (Data model) **Revisão fresca do DESIGN, D4:** contagem não pode dobrar entre 2 releases da mesma feature: o registro `CURATOR-colhidos.txt` guarda as impressões do que já foi julgado (AT-044); `--desde` fica disponível, mas o 17b não depende dele.
- [x] (Edge cases) **Revisão fresca do DESIGN, D2:** sugestão confirmada pelo curador vira pergunta, nunca entra sozinha; corrige a Decision 6 da v1.0 do DESIGN, que contrariava este DEFINE.
- [x] (Edge cases) **Revisão da fronteira, F4, F8 e parte de F3:** o conserto cobre branch, índice, `.git` e pasta ilegível (AT-045). F5, F6 e F7, LOW, ficam como limite ou pendência, com o motivo no BUILD_REPORT.
- [x] (Done signal) **Avaliador, ciclo 1 (`AVALIACAO_F14_PLAYBOOK_20261105-ciclo1.md`):** H1 a H4, M1 a M8 e L1 a L6, L8 e L9 aplicados com teste dos 2 lados. L7 (lista em bloco no slot) e L10 (log de sonda é colhido como achado) ficam como pendência, com o motivo no BUILD_REPORT.
- [x] (Constraints) **Avaliador, ciclo 1, M7:** no próprio sdd-open, `sdd/reports` fica fora do commit por regra; os `CURATOR-*` só entram no commit da curadoria em projeto que versiona a pasta de evidência.
- [x] (Done signal) **Avaliador, ciclo 2 (`AVALIACAO_F14_PLAYBOOK_20261105-ciclo2.md`):** N-H1, N-M1, N-M2, N-M3, N-L1 a N-L8 e parte de N-L11 aplicados com teste dos 2 lados. N-M3: o registro passa para `sdd/releases/<F>/`, ao lado do ledger, que o projeto sempre versiona; o limite fica para quem não versiona nem isso (é o caso do próprio sdd-open), e o texto diz. N-L9, N-L10 e o resto de N-L11 ficam como pendência.
- [x] (Data model) **Decisão D4 do Roberto, 2026-11-05: 3º ciclo focado.** Ele achou a 2ª regressão seguida na mesma regra (`AVALIACAO_F14_PLAYBOOK_20261105-ciclo3.md`): adivinhar a célula de veredito pelo conteúdo. A regra passa a ler o cabeçalho, como o oráculo do avaliador, que bateu nas 44 linhas reais; tabela sem as colunas não conta e é relatada. N3-M1, N3-M2, N3-M3, N3-L1, N3-L2, N3-L3, N3-L5, N3-L6, N3-L7 aplicados; N3-L4 fica como pendência.
- [x] (Constraints) **Decisão do Roberto, 2026-11-05 ("não consegue solução pelo Openrouter?"):** a prova do AT-038 poderia rodar no Codex CLI com modelo via OpenRouter (`CODEX_HOME` temporário). Depois disso, o Roberto repôs os créditos do Codex (confirmado com execução real): a prova usa o modelo próprio do Codex, e o 2º revisor volta a ser o Codex; o caminho via OpenRouter fica como reserva.
- [x] (Constraints) **Decisões do Roberto, 2026-11-05:** os créditos do Codex acabaram de novo na rodada 3 (conferido): o caminho de reserva foi usado. A prova do AT-038 e o 2º revisor da rodada 4 rodam com `deepseek/deepseek-v4-pro` pela OpenRouter; é o CLI do Codex, não o modelo da OpenAI. Depois da rodada 4: publicar sem 5ª rodada, com os 5 achados de Claude como primeira tarefa da F14_DRIVE.
- [x] (Done signal) **Revisão real, rodada 1:** 3 graves (2 defeitos), aplicados com teste; R2@claude (rc=1 do redirecionamento) aplicada mesmo com o auditor contra; R4@claude rebatida com evidência (`real1-repro-antes.log`: o script fixa `LC_ALL=C`). Ledger em `evidence/F14_PLAYBOOK/ledger-review.md`.
- [x] (UX flow) **UX review, 2026-11-05:** U1 a U9 aplicados nos ATs (v1.1); a curadoria roda depois do push, então toda parada e toda falha dizem que a publicação terminou.
- [x] (governança) Passo 11 rodado com revisor fresco em 2026-11-05: N.A.; fronteira e bloco conferidos (`governanca-fronteira.sh --comparar` 0, `governanca-bloco.py` 0).

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

- Skill `sdd-drive`, `sdd/bin/sdd-drive.sh`, slot `drive.max_rounds`, raio de impacto por superfície, `deploy-do-sha.sh`, `sdd-archive.py` e a linha `sdd-drive` do roadmap: 2ª entrega da F14.
- Catálogo de invariantes gerado em `docs/` com passo de CI.
- Hook de pre-commit para `sdd/invariants.md`: a trava roda na curadoria.
- Lista de jargão proibido na coluna de linguagem simples.
- Colheita de permissões de um agente só; leitura de memória fora do repositório.
- Alterar o repositório privado ou o sdd-starter; F15, F16 e F17.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Piso bash 3.2 e Python 3.9 stdlib; sem Node | núcleo do curator em Python embutido no script bash, como o `sdd-fluxo.sh`; sem `mapfile`, `declare -A` nem expansão em maiúsculas |
| Technical | Os testes rodam numa cópia de `git archive`, sem `.git` | o curator não exige repositório git; `copiar-docs.sh` exige e é testado com `git init` na sandbox |
| Technical | Delta-only nas skills existentes (regra 7 do 8.0) | `sdd-release` muda no 17b, no exemplo da pergunta e na lista de abortos; `sdd-new-session`, no passo de preparação |
| Technical | Padrão agnóstico (P2) e regra 10 do 8.0 | brief e skills sem nome de ferramenta de um agente só; a parada sem subagente usa o exit 40 |
| Technical | O bloco do OK da `sdd-release` mantém rótulos, ordem e uma pergunta só | a pergunta da curadoria é do passo 17b, depois do push, e não entra no bloco |
| Other | Específico da RDD não viaja (regra 4 do 8.0) | seções, caminhos e nomes do privado saem das fixtures e das sugestões |
| Other | `sdd/features`, `handoffs`, `reports`, `reviews` e `traces` nunca entram em commit da branch | o relatório da revisão da fronteira fica fora do commit |
| Other | Push em `main` só com OK citando "sdd-open"; review externo obrigatório | `v2.6.0` com `git push --atomic` |
| Resource | CI: tetos de 25 min (Ubuntu) e 45 min (macOS); hoje 14m18s e 28m33s | testes novos sem rede; sandbox só onde precisa de git |
| Timeline | 1ª entrega publicada antes de abrir a 2ª | a 2ª pode ficar para a sessão 12 |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/playbook-curator.sh`, `sdd/invariants.md`, `sdd/fixtures/playbook/curadoria/`, `.agents/skills/sdd-playbook/`, `.agents/skills/sdd-release/`, `.agents/skills/sdd-new-session/`, `sdd/templates/HANDOFF_TEMPLATE.md`, `sdd/bin/sdd-fluxo.sh`, `sdd/bin/design-lint.py`, `sdd/bin/prompt-drift-scan.sh`, `sdd/WORKFLOW_CONTRACTS.yaml`, `bin/sdd-open.sh`, `.github/workflows/release.yml`, `docs/`, `tests/` | pacote; o projeto do usuário recebe pelo `init`/`sync` |
| **KB Domains** | nenhum | o pacote não tem `sdd/kb/` próprio |
| **IaC Impact** | Modify existing | `release.yml` ganha `sdd/invariants.md` nos caminhos que publicam |
| **LLM Prompts** | false | o brief do curador é instrução do método para um agente de código, não prompt que roda em produção de um produto; nenhum provedor é chamado por código do pacote nesta frente |
| **CONTEXTO de domínio** | nenhum (pulado: sem `sdd/patterns/dominio.md`) | passo 1.5 do `sdd-define` |
| **Governança** | N.A. — o DEFINE trata só de ferramenta do método (curadoria do playbook, invariantes, cópia de documentos da frente, molde do handoff), sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha nem dado pessoal | revisor fresco, 2026-11-05 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O agente segue o 17b escrito e chama o `--conferir-bloco` antes de perguntar | a contagem inventada chegaria ao playbook; a trava teria de ir para um hook | no — AT-038 testa num agente real |
| A-002 | `governanca-fronteira.sh` serve ao curador sem mudança de interface (permitido = só o brief) | o 17b precisaria de um modo novo no script | no — a conferir no Design |
| A-003 | O `init` instala arquivo solto de `sdd/` pela mesma lista que instala `playbook.md` | `bin/sdd-open.sh` precisaria de caminho novo | yes — linha 553 de `bin/sdd-open.sh` lista `playbook.md` |
| A-004 | A suíte com os testes novos cabe nos tetos de 25 e 45 minutos | ajustar os tetos, como na F12 | no — medida no CI do PR |
| A-005 | O Roberto libera um agente de fora do Claude antes da etapa de revisão | a prova em outro agente vira pergunta D3 | no |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | dor, afetados e motivo presentes |
| Users | 3 | 5 usuários com dor específica |
| Goals | 3 | MUST e SHOULD por item do plano |
| Success | 2 | a maioria é saída exata; a prova real depende de um agente ainda não liberado |
| Scope | 3 | corte entre as 2 entregas confirmado pelo Roberto |
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
| 1.1 | 2026-11-05 | sdd-ux-review | U9 no AT-011; U8 no AT-015; U2 no AT-023; U3, U4 e U6 no AT-024; U1 e U5 no AT-025; U7 no AT-026 e AT-027; AT-040 novo |
| 1.7 | 2026-11-05 | revisão real, rodada 1 | saída de falha, `check=` por link e restauração nos ATs 7, 15 e 45 |
| 1.8 | 2026-11-05 | revisão real, rodada 4 | só registro: modelo da prova do AT-038 e decisão de publicar sem 5ª rodada; nenhum AT mudou |
| 1.6 | 2026-11-05 | avaliador, ciclo 3 | tabela lida pelo cabeçalho no AT-001; `check=` no AT-015; decisão da prova via OpenRouter |
| 1.5 | 2026-11-05 | avaliador, ciclo 2 | N-H1 no AT-001; N-M2 no AT-041; N-M3 no AT-024 |
| 1.4 | 2026-11-05 | avaliador, ciclo 1 | H1 a H4, M1 a M8, L1 a L6, L8 e L9 nos ATs |
| 1.3 | 2026-11-05 | revisões frescas | P1 a P5 e D1 a D11 do DESIGN e F1, F2, F3, F4, F8 e F9 da fronteira nos ATs; novos AT-043, AT-044 e AT-045 (`REVISAO_DESIGN_F14_PLAYBOOK_20261105.md`, `REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md`) |
| 1.2 | 2026-11-05 | sdd-design | `--preparar` (AT-041), piso do anti-collapse (AT-042), pergunta D1 do envio no AT-024 |

---

## Next Step

Execute o **SDD Design by RDD**.
