# DEFINE: F9 Fluxo encadeado e decisões

> O sdd-open passa a marcar cada pergunta com a classe da decisão, a decidir por exit code se um DESIGN precisa de revisão, se o loop de review convergiu e se a fase seguinte pode ser chamada, a parar com `exit 40 AGUARDANDO_HUMANO` e o brief gravado quando o agente não abre um papel fresco sozinho, e — só com `flow.autonomous: true` — a encadear as fases com o gate verde, registrando o que decidiu sozinho.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F9_FLUXO |
| **Date** | 2026-10-31 |
| **Author** | SDD Define by RDD |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open para no fim de cada fase e pergunta tudo do mesmo jeito: não distingue a decisão que é da pessoa (publicar, mudar o produto, mudar a política, teto estourado, impasse de evidência) da que a opção recomendada resolve, e não tem como seguir para a fase seguinte quando o gate da anterior está verde. Se um DESIGN precisa de revisão de contexto fresco e se o loop de review convergiu são decididos por leitura de prosa, sem exit code. E quando o agente não abre um papel fresco sozinho, a parada para a sessão nova é só texto: não há código de saída, nem brief gravado num lugar fixo, nem formato garantido. Sem isso, o fluxo do SDD privado não roda no Open (P4) e a degradação por vendor não é provada (P2).

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno do Bravo (contador) | roda as skills de fase em qualquer um dos 7 agentes | responde a perguntas que a recomendação resolveria e não sabe quais são decisões dele de verdade |
| Quem liga `flow.autonomous` (Roberto, F15) | conduz uma feature do brainstorm ao build | precisa que o fluxo siga sozinho com o gate verde, pare só em D1–D5 e diga o que decidiu sozinho |
| Quem usa um agente sem subagente (ou com ele desligado) | despacha o avaliador ou o revisor do DESIGN | a parada para a sessão nova não tem exit nem brief num lugar fixo |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/sdd-fluxo.sh` (bash 3.2 com o núcleo em `python3 -B` embutido): `review-design <DESIGN>` (0 EXIGIDO / 1 DISPENSAVEL / 64); `loop` (0 PRONTO / 10 CONTINUAR / 20 BLOQUEADO / 30 AGUARDANDO_RECIBO / 64) com `--log`; `despachar <papel> <FEATURE> <brief>` (40 AGUARDANDO_HUMANO / 64); `seguir <fase> <DEFINE> <próxima> [--parar]` (0 SEGUIR / 1 PARAR / 64); `estado` (0 ligado / 1 desligado / 64); `--self-test` |
| **MUST** | `sdd/bin/sdd-decisoes-lint.sh --sites <pasta|arquivo…>` (0/2/64) e `--self-test`, com o parser de perguntas do `skill-lint.py` |
| **MUST** | Item 9 do `sdd/templates/fragments/PERGUNTA_DECISAO.md` com as marcas `[D1]`…`[D5]` e `[auto]`; a pergunta de exemplo do fragmento e as 15 de `.agents/skills/*/references/como-falar.md` marcadas |
| **MUST** | `sdd/templates/fragments/FLUXO_ENCADEADO.md`: ordem das fases, quando seguir (`seguir`), linha de transição, recibo "Decidi sozinho", paradas que não são decisão (30, 40, credencial), teto do loop, `--parar` |
| **MUST** | Subseção `### Fluxo encadeado` dentro do `## Encerramento (obrigatório)` das 9 skills, depois do Próximo passo, com o bloco comum idêntico e 1 linha própria |
| **MUST** | Slots `flow.autonomous: false` e `review.security_globs: ""` em `sdd/config.example.yaml`, com comentário |
| **MUST** | `sdd-build` 5d, `references/contexto-fresco.md` (degrau 2, sessão nova) e a revisão do DESIGN da `sdd-design` chamam `sdd-fluxo.sh despachar` quando o agente não abre papel fresco sozinho, e param |
| **MUST** | Itens do PORTE nas skills: F6 (`sdd-design` passo 1, `[auto]` registrado), F8 (`sdd-define` passo 7, pontuação forte/fraco), F10 (`sdd-brainstorm` passo 1, tipos de entrada), F11 (`sdd-ux-review` passo 1, `UX_REVIEW_*.md` anteriores) |
| **MUST** | O CI (`.github/workflows/publish-gate.yml`) roda `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` e os 2 `--self-test`; fixtures em `sdd/fixtures/fluxo/` e `sdd/fixtures/conversa/decisoes/`; testes dos dois lados; `MANIFEST.txt` com todo arquivo novo |
| **MUST** | Prova no Codex CLI: 2 execuções reais do `codex exec` numa cópia temporária, com o log em `evidence/F9_FLUXO/` |
| **SHOULD** | `docs/chained-flow.md` + `docs/pt-BR/chained-flow.md` (o mecanismo), links nos READMEs; roadmap EN/PT sem a linha "Chained flow" (5 linhas); `docs/cli-conventions.md` com os exits dos 2 scripts |
| **COULD** | O `doctor` mostra se o encadeamento está ligado |

---

## Success Criteria

- [ ] `review-design` sobre os 8 DESIGNs F1–F8 sai 0 (EXIGIDO) nos 8, com a contagem de arquivos novos igual à do privado medida antes do porte (13, 17, 4, 10, 17, 7, 25, 13); a fixture com 2 arquivos novos e sem superfície de segurança sai 1; manifest ilegível sai 64.
- [ ] `loop` dá o exit esperado nas fixtures de `sdd/fixtures/fluxo/`: 0, 10 (4 causas), 20 (D4 teto, D4 ciclos, D5), 30 e 64 (7 causas); nenhuma entrada ausente ou malformada sai 0.
- [ ] `despachar` sai 40, grava `sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md` idêntico ao brief de entrada e imprime os 6 rótulos da parada ⏸️, `RESULTADO: AGUARDANDO_HUMANO` e `→`.
- [ ] `seguir` sai 0 com `✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)` só com `flow.autonomous: true`, `verify-gate --print` 0 e zero marcador; sai 1 com o motivo nos 6 casos de parada; sai 64 com o slot inválido.
- [ ] `sdd-fluxo.sh --self-test` sai 0 com 1 cenário por exit (0/1/10/20/30/40/64) e o do `| tee` (log reprovado no `gate-shell-evidencia.sh`); `sdd-decisoes-lint.sh --self-test` sai 0 com as 4 fixtures reprovadas pelo motivo certo e o controle aceito; `--sites .agents/skills` sai 0 com 15 perguntas e `--sites sdd/templates/fragments` com 2.
- [ ] Toda marca tem o rótulo fixo da classe (`[D1 · não se desfaz]` …); o recibo usa `— porque … · para desfazer: …`.
- [ ] As 9 skills têm a subseção com o bloco comum byte a byte igual; `skill-lint --conversa` 17/17; `check-versions --base v2.2.9 --base-obrigatoria` verde (9 minor, 6 patch).
- [ ] `codex exec` real: a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md` com o slot ligado termina com a linha `✅ DEFINE pronto → seguindo para …`; a `sdd-build` 5d com `--disable multi_agent` termina em `[exit=40]` com o brief gravado; nos dois logs, a skill lida é a da cópia.
- [ ] `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado nos 2 scripts; 1 sabotagem por script novo ou alterado; testes novos vermelhos na `v2.2.9`; Verify Gate `--strict` 0; revisão de contexto fresco sem HIGH aberto; Release `v2.2.10` com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `sdd-fluxo.sh review-design <DESIGN>` reads a `## [N.] File Manifest` section (optional number and trailing qualifier in the title) whose numbered rows (`\| N \| … \|`) have 3 or more rows whose action cell, lowercased and stripped of `*`, `` ` `` and `_`, starts with `create`, `criar`, `novo`, `nova` or `new` (`Modify` does not count), the system **shall** print `EXIGIDO: <n> arquivo(s) novo(s) (limiar 3)` and exit 0; the test **shall** run over tracked fixtures `sdd/fixtures/fluxo/DESIGN_*.md` with known counts that reproduce those extraction cases, and the ground truth of the 8 DESIGNs `DESIGN_F1_*` … `DESIGN_F8_*` (13, 17, 4, 10, 17, 7, 25, 13, untracked) **shall** be evidence in `evidence/F9_FLUXO/review-design-8.log` with one line `porte=<n> fonte=<n>` per DESIGN, all equal | test |
| AT-002 | Event-driven | **When** a manifest row contains one of the 8 fixed terms (`auth`, `login`, `token(s)`, `senha(s)`, `password`, `jwt`, `GRANT`, `rota pública`/`publica`, case-insensitive, word-bounded as in the source) or a path matching a glob of `review.security_globs` (comma-separated) or of `layers.sql` in `sdd/config.yaml`, `review-design` **shall** print `EXIGIDO` naming that signal and exit 0, even with fewer than 3 new files | test |
| AT-003 | Event-driven | **When** no signal of AT-001/AT-002 is present, `review-design` **shall** print `DISPENSAVEL: <n> arquivo(s) novo(s), sem superfície de segurança no manifest` and exit 1 | test |
| AT-004 | Unwanted | **If** the DESIGN is unreadable, has no `File Manifest` section, or the section has no numbered row, **then** `review-design` **shall** exit 64 with `RESULTADO:` and a `→` saying the caller runs the review (safe default) and records why | test |
| AT-005 | Event-driven | **When** `sdd-fluxo.sh loop --review <dir> --ledger <arq> --rodada N` reads a `META.txt` with `reviewer_exit: 0` and `auditor_exit: 0`, and every HIGH (from `reviewer.verdicts.jsonl`, plus any `NOVO` with `severidade: HIGH` in `auditor.verdicts.jsonl`, the last line per id winning) has a `REBATIDA_EVIDENCIA` or `REBATIDA_ESCOPO` cell in a ledger row marked `rodada=N` whose severity cell is `HIGH`, and the optional `--avaliacao` has exactly one `VEREDITO: PASS` line, the system **shall** print `ESTADO: PRONTO` with `rodada`, `graves_abertos`, `aplicadas`, `rebatidas` and exit 0 | test |
| AT-006 | Event-driven | **When** a HIGH has no ledger row for `rodada=N`, or its row is `APLICADA` (code changed, a new review is needed), or `reviewer_exit`/`auditor_exit` is not 0 (invalid review, e.g. 68), or the evaluation says `VEREDITO: NEEDS_WORK` with `--ciclo-avaliador` below 2, `loop` **shall** print `ESTADO: CONTINUAR` with one `motivo:` per cause and exit 10; a row of another `rodada`, a row whose severity cell is `MED`, or a justification cell quoting another verdict **shall not** close the HIGH; with `reviewer_exit`/`auditor_exit` ≠ 0 the jsonl files **shall not** be read (exit 10 even when they are missing), and an open HIGH with `PASS_PENDENTE_RECIBO` and no receipt **shall** exit 10 (precedence 64 > 20 > 10 > 30 > 0, as in the source) | test |
| AT-007 | Event-driven | **When** CONTINUAR comes from the review (invalid review, open HIGH or APLICADA) and the numeric part of `--rodada` is at or above `--teto` (default 3), or NEEDS_WORK comes with `--ciclo-avaliador` 2 or more (NEEDS_WORK with cycle 1 on the ceiling round stays 10), or a HIGH has `DISAGREE_EVIDENCE` from the auditor and no ledger verdict for the round, `loop` **shall** print `ESTADO: BLOQUEADO` with a `motivo:` naming the class (`D4` teto, `D4` ciclos, `D5` impasse de evidência) and exit 20 | test |
| AT-008 | Event-driven | **When** the evaluation says `VEREDITO: PASS_PENDENTE_RECIBO` and `--recibo` is absent or is not a name followed by a calendar-valid `AAAA-MM-DD` date, `loop` **shall** print `ESTADO: AGUARDANDO_RECIBO` and exit 30; with `--recibo "<nome> <AAAA-MM-DD>"` it **shall** record `motivo: avaliador: recibo humano — <recibo>` and decide as if PASS | test |
| AT-009 | Unwanted | **If** `META.txt`, `reviewer.verdicts.jsonl` or `auditor.verdicts.jsonl` is missing, a jsonl line is not a JSON object with a non-empty `achado` (reviewer: `severidade` in HIGH/MED/LOW; auditor: `veredito` in AGREE/DISAGREE_EVIDENCE/DISAGREE_CONCERN/NOVO, and `NOVO` with a severity), the ledger or the evaluation is unreadable, the evaluation has zero or two distinct `VEREDITO:` lines, `--rodada` is not `N` or `Na`, `--teto`/`--ciclo-avaliador` is not an integer, or an option has no value, **then** `loop` **shall** exit 64 naming the input, and **shall never** exit 0 and `tests/test_fluxo.py` **shall** compare the port with the source on these 3 edge cases (A invalid review without jsonl, B NEEDS_WORK on the ceiling round, C open HIGH with pending receipt: 10, 10, 10), evidenced in `evidence/F9_FLUXO/loop-diferencial.log` | test |
| AT-010 | Event-driven | **When** `loop` gets `--log <arquivo>`, the system **shall**, on every exit including 64, write to that file (creating its folder) the line `$ sdd-fluxo.sh loop <args>`, the full output and a final `[exit=N]` with the real exit, and still print the output and exit N, so an old log never stays with an exit this call did not give; `gate-shell-evidencia.sh` **shall** accept that file, and **shall** flag (exit 2) a log whose `$` line pipes `sdd-fluxo.sh loop` into `tee` | test |
| AT-011 | Event-driven | **When** `sdd-fluxo.sh despachar <papel> <FEATURE> <brief>` runs with `papel` and `FEATURE` matching `^[A-Za-z0-9_-]+$` and a non-empty readable brief, the system **shall** create `sdd/reports/briefs/` if missing, write `sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md` byte-identical to the brief (when the brief already is that file, by relative or absolute path, the copy is skipped and the file is left untouched), print the ⏸️ stop with the labels **Por que parei:**, **Onde:**, **Passos:** (numbered), **O que não foi feito:**, **Brief:** (the written path) and **Sessão nova:**, with a last step naming what to paste back (`avaliador` → the whole `<<<AVALIACAO … >>>` block, with its `VEREDITO: …` line, which the build stores verbatim; any other role → the final `<<<…>>>` block of the answer), then `Quando terminar, me peça de novo, eu continuo daqui.`, `RESULTADO: AGUARDANDO_HUMANO` and a `→`, and exit 40 | test |
| AT-012 | Unwanted | **If** `despachar` gets a missing, empty or unreadable brief, an invalid `papel` or `FEATURE`, or fewer than 3 arguments, **then** it **shall** exit 64 and write nothing under `sdd/reports/briefs/` | test |
| AT-013 | Event-driven | **When** `sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` runs with a valid pair (`define` → `governanca`, `ux-review` or `design`; `governanca` → `ux-review` or `design`; `ux-review` → `design`; `design` → `build`), the repository's `sdd/config.yaml` has `flow:` → `autonomous: true`, the Metadata **Status** of the phase artifact (the DEFINE for `define` and `governanca`, `sdd/reviews/UX_REVIEW_<F>.md` for `ux-review`, `DESIGN_<F>.md` for `design`) starts with `Ready for`, the folder is a git repository, `verify-gate.sh --print <DEFINE>` exits 0 with neither `kind:` nor `cmd:` empty, the DEFINE has no active clarification marker outside code fences (the same form that makes `verify-gate.sh` exit 5), and, for `fase` = `design`, the DESIGN passes `design-lint.py` and — when `review-design` exits 0 or 64 — its `## Advisor Ledger` has at least one data row, a severity column (`Severidade`, `Severity` or `Sev`) and every HIGH row's verdict starts with `APLICADA` or `REBATIDA_`, the system **shall** print as its first line `✅ <DOC> <pronto/pronta> → seguindo para <o/a> <DOC> (encadeamento ligado em sdd/config.yaml)` — documents in capitals with the right agreement (o DEFINE pronto, a GOVERNANÇA pronta, a UX REVIEW pronta, o DESIGN pronto), at most 100 characters —, as its second line `→ /sdd-<próxima> <arquivo>`, and exit 0 | test |
| AT-014 | Event-driven | **When** `flow.autonomous` is `false`, empty or absent, `sdd/config.yaml` is absent, `--parar` is given, the phase artifact is missing or its Status does not start with `Ready for` (motivo `<DOC> não está pronto (Status: <valor>)`), `verify-gate.sh --print` exits non-zero or shows `kind:`/`cmd:` empty (`Verify Gate sem kind ou cmd`), an active marker is present, the DESIGN fails `design-lint.py`, the folder is not a git repository (`a pasta não é um repositório git…`), the DESIGN review is required and has no ledger row (`revisão do DESIGN exigida e não registrada no Advisor Ledger`) or no severity column (`Advisor Ledger sem coluna de severidade…`), a HIGH row of the ledger is not closed (`HIGH aberto no Advisor Ledger: <#>`), or `próxima` is `release` from any phase, `build` included (always: publishing is D1), `seguir` **shall** print `PARAR: <motivo>` and `→ Próximo passo: /sdd-<próxima> <arquivo>` and exit 1; the motivo for `release` **shall** be `publicar não se desfaz — é decisão sua (D1)`, and for an off chain `encadeamento desligado` (the skill does not relay that one to the user) | test |
| AT-015 | Unwanted | **If** `flow.autonomous` has a value other than `true`, `false` or empty, or the pair is outside AT-013 and is not `<fase> → release` (with `fase` in `define`, `governanca`, `ux-review`, `design`, `build`), or the DEFINE is unreadable, **then** `seguir` **shall** exit 64; for the slot value it **shall** print `⚠️ sdd-open: flow.autonomous = "<valor>" em sdd/config.yaml não é true nem false — encadeamento desligado.` and `→ troque por true (liga) ou false (desliga)` | test |
| AT-016 | Unwanted | **If** `python3` is not on `PATH`, **then** every verb of `sdd-fluxo.sh` and of `sdd-decisoes-lint.sh` **shall** exit 64 naming `python3`; an unknown verb or no argument **shall** print the usage and exit 64 | test |
| AT-017 | Event-driven | **When** `sdd-fluxo.sh --self-test` runs (with no `.git` available, as in the gate's `git archive` copy), it **shall** run at least one scenario per exit (`review-design` 0/1/64, `loop` 0/10/20/30/64, `despachar` 40/64, `seguir` 0/1/64, `estado` 0/1/64) over `sdd/fixtures/fluxo/` in a temporary directory, plus one that runs `loop … \| tee` on a BLOQUEADO fixture and shows the pipeline exit (0) differs from the real one (20) and that `gate-shell-evidencia.sh` flags the resulting log; print one `✅`/`🛑` line per scenario and exit 0 only when all match | test |
| AT-018 | Event-driven | **When** `sdd-decisoes-lint.sh --sites <pasta>` runs, it **shall** collect every decision question — a hit of the `perguntas()` of `skill-lint.py`, with ```` ```markdown ```` fences opened, whose line contains `**Sua decisão**` — of every `.md` under the folder, and, when each has exactly one mark `[<código> · <rótulo>]` immediately before the bold question, with `<código>` in `D1`…`D5` or `auto` and `<rótulo>` equal to the one of item 9 of `PERGUNTA_DECISAO.md` (read from the fragment, single owner), exactly one `(recomendado)` option and it first, a **não sei** option, no **Outro** option, and no technical identifier (`AT-\d+`, `LM-\d+`, `D\d+` outside a mark, hex SHA of 7+ characters) outside a final `(ref: …)`, print `🟢 … <n> pergunta(s) em <m> arquivo(s)` and exit 0; on `.agents/skills` it **shall** find 15 questions (14 `references/como-falar.md` and `sdd-ux-review/references/entrevista-publico.md`), and on `sdd/templates/fragments` 2 (`PERGUNTA_DECISAO.md` and `FLUXO_ENCADEADO.md`) | test |
| AT-019 | Unwanted | **If** any question breaks a rule of AT-018, **then** `--sites` **shall** print one `🛑 <arquivo>:<linha> — <motivo>` per break (motivos: `sem marca de classe`, `<k> marcas`, `marca fora do lugar`, `marca sem o rótulo`, `marca desconhecida <x>`, `rótulo <x> diferente de <y>`, `nenhuma opção (recomendado)`, `<k> opções (recomendado)`, `a opção (recomendado) não é a primeira`, `sem a opção **não sei**`, `tem a opção **Outro**`, `identificador técnico fora do (ref: …): <x>` — the same wording as `skill-lint.py --conversa` where both check the same rule), `RESULTADO: VERMELHO` and a `→` to `PERGUNTA_DECISAO.md`, and exit 2 | test |
| AT-020 | Unwanted | **If** a path given to `--sites` does not exist or is unreadable, or all the given paths together hold zero decision questions, **then** the lint **shall** exit 64 (nothing checked is never green) | test |
| AT-021 | Event-driven | **When** `sdd-decisoes-lint.sh --self-test` runs, it **shall** lint the 4 fixtures of `sdd/fixtures/conversa/decisoes/` (`sem-classe`, `com-outro`, `com-jargao`, `dois-recomendados`), expect exit 2 with the matching `motivo` for each, lint `controle.md` and expect exit 0, and exit 0 only when all 5 match | test |
| AT-022 | Event-driven | **When** `PERGUNTA_DECISAO.md` is read, item 9 **shall** list the 6 marks with their fixed labels — `[D1 · não se desfaz]`, `[D2 · muda o produto]`, `[D3 · muda a regra do método]`, `[D4 · limite de tentativas]`, `[D5 · provas em conflito]`, `[auto · de rotina]` —, each with what it means and whether it is asked with `flow.autonomous: true` (`D1`…`D5` yes; `auto` no: the recommended option wins and goes to the receipt), and the string `[Dn]`, the rule to run `sdd-fluxo.sh estado` before the first `auto` question of a session, and that the OK question of `sdd-release` (`Posso finalizar…?`, a contract) carries no mark because it is D1 by construction; items 1–8, the ⏸️ block and its labels **shall** stay; the example questions of the fragment, the open-question example included, **shall** carry a mark (the lint checks only questions with options) | test |
| AT-023 | Event-driven | **When** `FLUXO_ENCADEADO.md` is read, it **shall** hold the phase order, the `seguir` contract, the transition line, the receipt format `**Decidi sozinho:**` / `- <decisão> — porque <…> · para desfazer: <…>` (omitted when empty), the D4 ceiling question written in the format (3 exits + **não sei**), the stops that are not decisions (exit 30, exit 40, missing credential), the loop ceiling (3 rounds, 2 evaluator cycles) and `--parar`; `tests/test_agnostico.py` **shall** pass over it | test |
| AT-024 | Event-driven | **When** the 9 skills with `## Encerramento (obrigatório)` are read, each **shall** have, inside that section and after its `**Próximo passo:**`, a `### Fluxo encadeado` subsection whose common block is byte-identical in the 9 and one own line (define, governanca, ux-review, design and build name where they chain; brainstorm, iterate, new-session and release say why they do not); `## Por que cada regra existe` **shall continue to** come right before the Encerramento | test |
| AT-025 | Event-driven | **When** `sdd/config.example.yaml` is read, it **shall** have `flow:` with `autonomous: false` and `review:` with `security_globs: ""`, each with a comment saying what it changes and the default; the config parser rules of the file header **shall** still hold | test |
| AT-026 | Event-driven | **When** the agent cannot open a fresh role by itself, `sdd-build` 5d, `references/contexto-fresco.md` (step 2) and the DESIGN review of `sdd-design` **shall** tell it to run `bash sdd/bin/sdd-fluxo.sh despachar <papel> <F> <brief>` and stop on exit 40; the texts **shall** say "papel fresco"/"sessão nova" and no single-agent tool name | test |
| AT-027 | Event-driven | **When** the 4 skills are read: `sdd-design` step 1 **shall**, with `flow.autonomous: true`, turn an absent LLM flag into `true` (conservative), let a `false` re-check with hits decide `true` and accept the verifiability proposal without asking, recording each as an `[auto]` line in the DESIGN — and with the chain off **shall continue to** ask, the question marked `[auto · de rotina]`; `sdd-define` step 7 **shall** score 1 strong signal → `true`, 2 weak → `true`, 1 weak → `true` with a note, loop signals → "candidato a loop"; `sdd-brainstorm` step 1 **shall** have the table of input types (vague idea → "conte mais"; feature → question the need; comparison → what is gained and lost); `sdd-ux-review` step 1 **shall** read the previous `sdd/reviews/UX_REVIEW_*.md` | test |
| AT-028 | Event-driven | **When** the `gate` job of `.github/workflows/publish-gate.yml` runs, it **shall** have a step that runs `bash sdd/bin/sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments`, `bash sdd/bin/sdd-decisoes-lint.sh --self-test` and `bash sdd/bin/sdd-fluxo.sh --self-test` (asserted by `tests/test_release_workflow.py`); `scripts/check-versions.py --base v2.2.9 --base-obrigatoria` **shall** pass with the 9 skills of AT-024 at a new minor and the other 6 marked skills at a new patch | test |
| AT-029 | Non-regression | The system **shall continue to** pass the 683 existing tests, `verify-gate.sh` (6 exits, fixtures, same output with and without trace), `report-lint.py`, the F8 hooks (`test_hooks`, `test_claude_adapter`, `test_alarme`), `skill-lint.py --conversa` on the 17 skills (the 7 `sdd/fixtures/conversa/` fixtures failing for the same reason), `playbook-lint.sh --self-test`, the release OK block, and `publish-gate.sh` in `ci` mode; `tests/test_bash32.py` **shall** scan both new scripts and `tests/test_docs.py` **shall** count 5 roadmap rows with no "Chained flow" row | test |
| AT-030 | Event-driven | **When** `evidence/F9_FLUXO/codex.sh` copies the repository by `git archive HEAD`, runs `git init -q`, `git add -A` and `git commit -q` in the copy (identity at example.com), writes `sdd/config.yaml` with `flow.autonomous: true`, uses a `CODEX_HOME` without `skills/`, and runs `codex exec` with a prompt to run `sdd-define` on `sdd/fixtures/BRAINSTORM_EXEMPLO.md` answering every D1–D5 question with the recommended option, the AT **shall** pass if and only if `evidence/F9_FLUXO/codex-define-autonomo.log` holds a line starting `✅ DEFINE pronto → seguindo para ` and a line starting `→ /sdd-`, and the log shows the skill read from the copy's `.agents/skills/`; otherwise it is FAIL (❌ in the BUILD_REPORT) | manual-ux |
| AT-031 | Event-driven | **When** `codex.sh` runs `codex exec` (with `--disable multi_agent` and a prompt stating that no subagent or collaborator is available) in a committed copy whose `sdd/config.yaml` has 2 or more `layers` globs touched by a built feature of fixture, with a prompt to run `sdd-build` step 5d, the AT **shall** pass if and only if `evidence/F9_FLUXO/codex-despacho-40.log` shows the `sdd-fluxo.sh despachar` call exiting 40 (`exited 40` in the Codex transcript) and `RESULTADO: AGUARDANDO_HUMANO` and records that `sdd/reports/briefs/BRIEF_avaliador_<F>.md` exists in the copy (`test -f`); otherwise it is FAIL | manual-ux |
| AT-032 | Unwanted | **If** one of the scripts `sdd-fluxo.sh` (in `review-design`, `loop` and `seguir`) or `sdd-decisoes-lint.sh` (in the mark and in the label rule) is sabotaged (a rule removed or inverted), **then** at least one named test **shall** fail and `git checkout` **shall** turn the suite green again (`evidence/F9_FLUXO/sabotagem.log`); the new tests **shall** fail on the `v2.2.9` tree (`evidence/F9_FLUXO/baseline.log`) | test |
| AT-033 | Event-driven | **When** `sdd-fluxo.sh estado` runs, the system **shall** print `encadeamento: ligado` and exit 0 when `flow.autonomous` is `true`, print `encadeamento: desligado` and exit 1 when it is `false`, empty, absent or `sdd/config.yaml` is absent, and print the ⚠️ line of AT-015 and exit 64 for any other value | test |

---

## Clarifications

### Session 2026-10-31

- [x] (Scope) D1: `flow.autonomous: false` por default; ligado, `seguir` decide e a próxima fase roda na mesma sessão (BRAINSTORM, decisões 1, 10 e 11). Integrado em AT-013 a AT-015 e AT-024.
- [x] (Data model) D11: slots `flow.autonomous` e `review.security_globs`; os 8 termos genéricos fixos; `layers.sql` conta (BRAINSTORM, decisão 2). Integrado em AT-002 e AT-025.
- [x] (Terminology) Marcas `[D1]`…`[D5]` (perguntadas mesmo com o encadeamento ligado) e `[auto]` (só sem ele); uma marca por pergunta, antes do negrito (BRAINSTORM, decisão 3). Integrado em AT-018 a AT-022.
- [x] (Edge cases) **Achado do Define, premissa corrigida:** o Codex CLI 0.163 tem `multi_agent` estável e ligado — ele abre subagente; o `references/contexto-fresco.md` do Open já o lista no degrau 1. A linha "Codex sem subagente" da tabela de degradação do plano (8.0) está velha. A prova do exit 40 (AT-031) roda o Codex com `--disable multi_agent`, o caso real de "agente que não abre papel fresco sozinho". O exit 40 não é por vendor: é o degrau 2 (sessão nova) da escada que o Open já tem.
- [x] (Data model) **Achado do Define:** o nome do brief segue a convenção que o Open já usa no degrau 2 — `sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md` —, no lugar do `<FEATURE>-<papel>-<data>.md` do brainstorm (decisão 9). Um despacho novo do mesmo papel sobrescreve o anterior; a saída diz o caminho.
- [x] (Integrations) **Achado do Define:** `~/.codex/skills/` desta máquina tem cópias antigas de `sdd-brainstorm`, `sdd-build`, `sdd-define`, `sdd-design`, `sdd-handoff`. As execuções reais (AT-030/AT-031) usam um `CODEX_HOME` temporário só com a autenticação e a configuração, sem `skills/` — é a versão desta frente da regra "nenhuma skill de fora do pacote foi carregada" (plano, preâmbulo da seção 8).
- [x] (Scope) **Achado do Define:** `docs/roadmap.md` e PT têm a linha "Chained flow" (*planned*). A F9 a remove nas 2 línguas (5 linhas) e, pela regra da própria página ("o mecanismo vem com o seu documento"), entrega `docs/chained-flow.md` + PT.
- [x] (Edge cases) Ground truth do `review-design` medida antes do porte, rodando a fonte do privado (cópia no scratchpad, só leitura) sobre os 8 DESIGNs: 8/8 EXIGIDO por arquivo novo (13, 17, 4, 10, 17, 7, 25, 13); só a F5 tinha linha de segurança pela regex da RDD. Integrado em AT-001.
- [x] (Edge cases) O `loop` mantém do privado: id com sufixo `@engine` fechado pelo id completo ou pela base quando ela é única; rodada com sufixo de letra (`5a`) aceita no argumento, o teto conta o número. Corta: os campos `revisor2_*`, `desempate_*`, revisor raso e `auditor_exit 75` (F10). Sem o desempate, todo `DISAGREE_EVIDENCE` sobre HIGH sem veredito do ledger é D5.
- [x] (UX flow) Não há tela: a interface é a saída do `sdd-fluxo.sh` (linha de transição, `ESTADO:`, a parada do exit 40), a marca nas perguntas e a subseção das skills. A `sdd-ux-review` revisa esse texto.
- [x] (Constraints) O `seguir` lê o `sdd/config.yaml` da raiz do repositório (`git rev-parse --show-toplevel`; sem git, a pasta atual); quem decide se encadeia é o script, não o agente lendo o config.
- [x] (Constraints) Versões: as 9 skills com a subseção sobem minor; as 6 só com a marca (`auditoria-harness`, `checar-ambiente`, `handoff`, `kb`, `playbook`, `prompt-builder`) sobem patch; `sdd-higiene-dado` e `sdd-iniciar-repo` não têm pergunta de exemplo e não mudam.
- [x] (UX flow) **UX review (`sdd/reviews/UX_REVIEW_F9_FLUXO.md`), 7 MUST integrados:** marca com rótulo fixo por classe (U1, AT-018/019/022); linha de transição que diz por que não perguntou (U2, AT-013); `PARAR` por slot desligado não é repassado (U3, AT-014, AT-024); recibo com `porque`/`para desfazer` (U4, AT-023); a parada do exit 40 diz o que trazer de volta (U5, AT-011); mensagem do slot inválido (U6, AT-015); release sempre PARAR com a frase do D1 (U7, AT-014). SHOULD U8 (pergunta D4 no fragmento e `--sites` sobre os fragmentos) integrado em AT-023/AT-028.
- [x] (Scope) **F6 só com o encadeamento ligado** (refina a decisão 13 do brainstorm pela regra 8 do 8.0: "sem autonomia, D1–D5 entra só como formato de pergunta"): com o slot desligado, a `sdd-design` continua perguntando, com a marca `[auto · de rotina]`; ligada, decide pelo lado conservador e registra `[auto]` no DESIGN. Integrado em AT-027.
- [x] (Constraints) **Design, 5 ajustes (DESIGN v1.0, Contrato de aceite):** o passo de CI vai para o `publish-gate.yml` (o `publish-gate.sh` não roda lint de skill), AT-028; pergunta de decisão = linha com `**Sua decisão**`, com os blocos ```` ```markdown ```` abertos — `.agents/skills` dá 15 (14 `como-falar.md` + `entrevista-publico.md`; a do OK da `sdd-release` fica de fora, contrato do `test_contrato_build_release`), os fragmentos dão 2, AT-018/AT-022; verbo `estado` para a pergunta `[auto]` no meio da fase, AT-033; A-004 era falsa (`--print` sai 64 fora de git), o `--self-test` monta `git init`; a `kb-protocol.md` tem uma heurística em negrito com opções que não é pergunta ao aluno (sem `**Sua decisão**`, fica de fora sem mudar).
- [x] (Constraints) **Revisão de contexto fresco do DESIGN (`sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md`), 5 ajustes ACEITOS:** o `seguir` lê o Status do artefato da fase, recusa gate sem kind/cmd, confere a revisão do DESIGN no Advisor Ledger e aceita `build → release` sempre como PARAR (AT-013–AT-015); o AT-001 roda sobre fixtures rastreadas e a verdade dos 8 DESIGNs vira evidência (AT-001); o `codex.sh` commita a cópia, liga `layers` e tem critério de falha (AT-030/AT-031); `despachar` com o brief já no destino (AT-011); a precedência do `loop` é a da fonte, com teste diferencial (AT-006/AT-007). LOW: concordância pronta/pronto, motivos com a redação do `skill-lint`, zero perguntas no total, pergunta aberta com marca, pinos de versão nos testes.
- [x] (Constraints) **Revisão do build, ciclo 1 (`sdd/reviews/AVALIACAO_F9_FLUXO_20261031-ciclo1.md`, NEEDS_WORK: 1 HIGH, 2 MEDIUM, 12 LOW):** `--log` regravado em toda saída (AT-010); Advisor Ledger sem coluna de severidade e pasta sem git param o `seguir` (AT-013/AT-014); o retorno do avaliador no exit 40 é o bloco `<<<AVALIACAO … >>>` inteiro (AT-011, revê a U5 da UX review); recibo com nome e data que existe (AT-008). LOW de texto e robustez nos fragmentos, nas skills e no lint; a classificação das perguntas da `sdd-design` (D2) e da `sdd-iterate` (auto) ficou como implementada, com o DESIGN corrigido.
- [x] (Constraints) **Revisão do build, ciclo 2 (`sdd/reviews/AVALIACAO_F9_FLUXO_20261031-ciclo2.md`, NEEDS_WORK: 1 HIGH, 1 MEDIUM, 4 LOW):** nome com letra acentuada recusado em qualquer locale (AT-012: a faixa `[A-Za-z]` do `case` seguia o locale UTF-8); severidade formatada (`**HIGH**`, crases, emoji) conta como HIGH (AT-014); o `--log` é regravado também com erro interno, com o arquivo que não grava (64) e sem `python3` (AT-010, AT-016); Advisor Ledger de exemplo em bloco cercado não conta (AT-013). Sem 3º ciclo: a `sdd-build` limita a 2.
- [x] (Done signal) AT-030 e AT-031 são execuções de um agente real, fora do `cmd` do gate (custam a conta do Codex e não são determinísticas): `kind: manual-ux` na tabela, com o log como recibo; o `cmd` do gate cobre os outros ATs, menos o `check-versions --base v2.2.9` do AT-028 (a cópia do `git archive` não tem `.git`: roda no CI e em `evidence/F9_FLUXO/check-versions.log`) e o AT-032 (evidência).

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

- Os 8 cortes YAGNI do brainstorm: campos do 2º revisor, desempate, revisor raso, lotes e `auditor_exit 75` no `loop` (F10); `--curadoria` (F14); denylist de jargão da RDD; parada "espelho → worktree"; recibo no `BUILD_REPORT`; `sdd-build` passo 0 chamando `review-design` (R13 da F10); verbo de retomada depois do exit 40; detecção automática de subagente.
- Revisão adversarial, registry, adapters por engine e 2º revisor (F10/F11); `RESUMO_ETAPA.md` com `/adversarial-review` (F10).
- Cartógrafo, curator, `/drive` e `drive.*` (F12–F14).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash ≥ 3.2 e Python ≥ 3.9 só com stdlib, `python3 -B`; testes sem rede | Nada de `mapfile`, `declare -A`, `${x^^}`; nome da variável entre chaves antes de emoji; `rm -rf` só com `"${X:?}"` |
| Technical | P2 (`tests/test_agnostico.py`): nenhum nome de ferramenta de um agente só em `.agents/skills/`, `sdd/templates/`, `sdd/hooks/`, `AGENTS.md.tmpl` e `sdd/playbook.md` | O texto fala em "papel fresco" e "sessão nova"; `multi_agent` e `CODEX_HOME` só no log da evidência |
| Technical | `verify-gate.sh` (6 exits, fixtures, saída idêntica com e sem trace) não muda: o `seguir` o chama com `--print` | O marcador é procurado pelo `seguir` com a mesma forma ativa do gate (a mesma regex do gate, fora de bloco cercado) |
| Technical | `skill-lint.py` não muda de comportamento; o `sdd-decisoes-lint.sh` importa o `perguntas()` dele | As 7 fixtures de `sdd/fixtures/conversa/` reprovam pelo mesmo motivo |
| Technical | Camada de conversa (bloco comum em 15 `SKILL.md`, seção nas 17, `FRASES` do `test_conversa`), "Por que cada regra existe" logo antes do Encerramento, rodapé intacto | A subseção entra dentro do Encerramento; a marca entra só no exemplo de `como-falar.md` |
| Technical | Publish-gate G1 (gitleaks), G2 (`publish-gate-patterns.txt`: `/Users/<nome>/`, e-mail fora de `example.*`, CPF, CNPJ, telefone, 11+ dígitos), G3 (`MANIFEST.txt` `LC_ALL=C`) | Fixtures reescritas sem dado do privado; `git add` por nome |
| Technical | `report-lint` fail-closed, hooks da F8, bloco do OK da `sdd-release` intactos | A `sdd-release` ganha só a subseção e a marca |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open", depois de PR com CI verde em ubuntu e macOS | A Release `v2.2.10` depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | novos: `sdd/bin/sdd-fluxo.sh`, `sdd/bin/sdd-decisoes-lint.sh`, `sdd/templates/fragments/FLUXO_ENCADEADO.md`, `sdd/fixtures/fluxo/`, `sdd/fixtures/conversa/decisoes/`, `docs/chained-flow.md`, `docs/pt-BR/chained-flow.md`, `tests/test_fluxo.py`, `tests/test_decisoes_lint.py`; alterados: `sdd/templates/fragments/PERGUNTA_DECISAO.md`, `sdd/config.example.yaml`, 15 `SKILL.md`, 14 `references/como-falar.md`, `sdd-ux-review/references/entrevista-publico.md`, `sdd-build/references/contexto-fresco.md`, `sdd-governanca/manifest.json`, `sdd-kb/CHANGELOG.md`, `.github/workflows/publish-gate.yml`, `docs/roadmap.md` + PT, `docs/cli-conventions.md`, `README.md`, `README.pt-BR.md`, `tests/{test_conversa,test_docs,test_contrato_build_release,test_release_workflow}.py`, `MANIFEST.txt` | Fontes no privado (`origin/main` `1b1c1d41b`, só leitura): `scripts/sdd-fluxo.sh`, `scripts/sdd-decisoes-lint.sh`, `.claude/sdd/templates/fragments/FLUXO_ENCADEADO.md` |
| **KB Domains** | nenhum | O open não tem `sdd/kb/` próprio |
| **IaC Impact** | None | O push em `main` publica a Release sozinho (`sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/config.example.yaml`, `.agents/skills/**`) |
| **LLM Prompts** | false | Scripts de decisão, lint e texto de skill; nenhum texto vai para um LLM em runtime de produto (o brief do avaliador é orquestração SDD, não prompt de produção) |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 683 testes passam no piso em `7c640eb` | O Build partiria de base vermelha | no; conferido no início do Build |
| A-002 | O `codex exec` lê `.agents/skills/` e `AGENTS.md` da pasta onde roda e aceita `CODEX_HOME` para isolar a configuração | As execuções reais não carregariam a skill da cópia | parcial: `bin/lib/vendors.sh` declara a leitura nativa; `CODEX_HOME` conferido no Build |
| A-003 | `codex exec --disable multi_agent` impede o agente de abrir subagente | a execução real com o despacho não exercitaria o degrau 2 | **no** (medido no Build): com a flag, o Codex 0.163 ainda abriu um colaborador (`collab: Wait`) e seguiu o degrau 1 (`codex-despacho-subagente.log`); a condição "sem subagente" passou para o prompt (`codex-despacho-40.log`) |
| A-004 | `verify-gate.sh --print` funciona sem `.git` (cópia do `git archive`) | O `--self-test` do `seguir` falharia dentro do gate | **no** (medido no Design: sai 64 fora de git); o `--self-test` monta um repositório temporário com `git init -q` |
| A-005 | O `gate-shell-evidencia.sh` acusa `\| tee` como último estágio sem `rc=$?` | o caso do `tee` no `--log` e no `--self-test` precisaria de outra prova | yes; `tee` está na lista de formatadores (`sdd/bin/gate-shell-evidencia.sh:100`) |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Três decisões por prosa e uma parada sem exit, com as fontes lidas |
| Users | 3 | Aluno contador, quem liga o encadeamento, quem usa agente sem subagente |
| Goals | 3 | Cada verbo com os exits e cada skill com o que muda |
| Success | 3 | Todo critério é um exit, uma linha de saída ou um arquivo |
| Scope | 2 | O comportamento do Codex com `CODEX_HOME` e `--disable multi_agent` (A-002, A-003) só se confirma na execução |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.6 | 2026-10-31 | SDD Build by RDD | Ciclo 2 da revisão do build: 6 achados aplicados sem mudar o texto dos testes (locale, severidade formatada, log em toda saída, Ledger cercado) |
| 1.5 | 2026-10-31 | SDD Build by RDD | Ciclo 1 da revisão do build: testes 8, 10, 11, 13 e 14 mais estritos (log em toda saída, retorno do avaliador, git, coluna de severidade, recibo válido) |
| 1.4 | 2026-10-31 | SDD Build by RDD | Execução real no Codex (teste 31): a condição "sem subagente" vai no prompt (A-003 falsa: `--disable multi_agent` não tira o colaborador do Codex 0.163) e o exit do despacho é lido no formato do transcript do Codex (`exited 40`) |
| 1.3 | 2026-10-31 | SDD Design by RDD | Revisão de contexto fresco do DESIGN: 3 HIGH, 2 MEDIUM e 10 LOW aplicados (AT-001, AT-006, AT-007, AT-011, AT-013–AT-015, AT-019, AT-020, AT-022, AT-030, AT-031) |
| 1.2 | 2026-10-31 | SDD Design by RDD | 5 ajustes do Design: CI no `publish-gate.yml` (AT-028), pergunta = linha com Sua decisão e contagem 15 + 2 (AT-018), OK da release sem marca (AT-022), verbo `estado` (AT-033), A-004 falsa; sabotagem por verbo (AT-032) |
| 1.1 | 2026-10-31 | SDD UX Review by RDD | 7 MUST e 1 SHOULD da UX review (marca com rótulo, linha de transição, `PARAR` desligado silencioso, recibo, retorno do exit 40, slot inválido, release D1, pergunta D4 e `--sites` nos fragmentos); F6 só com o encadeamento ligado |
| 1.0 | 2026-10-31 | SDD Define by RDD | Versão inicial a partir de `BRAINSTORM_F9_FLUXO.md`, com 5 achados (Codex com subagente, nome do brief, `CODEX_HOME`, roadmap, ground truth do `review-design`) |

---

## Next Step

Execute o **SDD Design by RDD**.
