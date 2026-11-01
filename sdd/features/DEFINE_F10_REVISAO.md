# DEFINE: F10 Revisão adversarial — núcleo

> O sdd-open passa a ter `sdd/bin/adversarial-review.sh`: uma engine do registry revisa o diff congelado, outra audita a revisão, com 2º revisor e desempate quando os gatilhos pedem, exclusão de papéis, falha classificada, custo por papel e privacidade; o `sdd-fluxo.sh loop` lê a saída inteira, o `sdd-build` liga a revisão do DESIGN no passo 0 e a `sdd-release` não publica sem `review_externo` no ledger.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F10_REVISAO |
| **Date** | 2026-10-31 |
| **Author** | SDD Define by RDD |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open não tem revisão adversarial: a revisão por um segundo vendor existe só no SDD privado, com engines e cadeias fixas da RDD, num script zsh com 87 referências RDD nos adapters; a `sdd-release` do Open publica sem nenhum review externo (no privado, quando era opcional, só 13 de 84 features tiveram review), e o `sdd-fluxo.sh loop` da F9 não tem uma revisão real para consumir nem lê 2º revisor, revisão rasa e desempate.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem usa o Open em qualquer dos 7 agentes | dono da feature | não tem como pedir a uma engine de outro vendor que revise o diff e a outra que audite a revisão, com custo, tokens e proveniência registrados |
| O Roberto, na troca do privado pelo Open (F15) | mantenedor | o mecanismo das 315 revisões do privado precisa existir no Open sem as cadeias da RDD |
| `sdd-release` e `sdd-fluxo.sh loop` | consumidores | sem saída de review para conferir, a release segue sem review e o loop não tem insumo real |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/adversarial-review.sh` com revisor → auditor sobre um diff congelado com sha256, papéis lidos de `sdd/review/registry.tsv` e dos slots, exclusão de papéis (exit 67) e vereditos obrigatórios (exit 68) |
| **MUST** | Um adapter por engine em `sdd/bin/adapters/` (`claude`, `codex`, `gemini`, `openrouter`), com tokens e custo por papel; custo desconhecido é `$?`, nunca 0 |
| **MUST** | Falha classificada (AUTH 65 sem troca, CLI ausente 66, 429 com nova tentativa, quota avança na lista, lista esgotada 67) e privacidade (pasta ignorada pelo git, `data_collection: deny`) |
| **MUST** | `sdd-release` aborta sem `review_externo` no ledger; aceita a review desta frente (mesmo `diff_sha256`) ou a dispensa D3 com motivo |
| **MUST** | `sdd-fluxo.sh loop` lê 2º revisor, revisão rasa e desempate por delta, sem mudar o que a F9 já decide |
| **MUST** | Prova real: revisor `claude` e auditor `openrouter:<slug>` sobre o diff da própria F10, com tokens, custo ≠ 0 e `diff_sha256`, lida pelo `loop` |
| **SHOULD** | 2º revisor condicional (segurança, ≥ 8 arquivos, ≥ 120 KB, ≥ 2 camadas, revisor raso) e desempate de HIGH refutado com evidência |
| **SHOULD** | `sdd-design` com revisor → auditor em cadeia (R12) e `sdd-build` passo 0 com `review-design` (R13) |
| **COULD** | `--dry-run` com o plano dos papéis e o tamanho do diff, sem chamar engine |

---

## Success Criteria

- [ ] Com stubs (sem rede): `auditor == revisor1` sai 67 sem chamar engine; auditor sem bloco de vereditos sai 68 com o META gravado; `--um-engine` grava `diversidade: nenhuma`; AUTH sai 65 sem chamar a 2ª engine da lista; 429 faz 3 chamadas no total; quota avança para a 2ª da lista; lista esgotada sai 67.
- [ ] `output_dir` não ignorado sai 64; diff vazio sai 64; diff acima de 8 MB sai 64; contexto acima de `review.context_max_kb` corta o BRAINSTORM primeiro e o META registra o corte.
- [ ] `--conferir` sai 0 sobre a review do HEAD atual e 2 depois de 1 byte mudado em arquivo do diff; `--ledger` sai 2 sem `review_externo`, 0 com `dispensado — <motivo>` e 0 com `<pasta> sha256=<hex>` que confere.
- [ ] `sdd-fluxo.sh loop` dá o exit esperado nas fixtures novas (2º revisor indisponível 20, 2º revisor falhou 10, rasa 10, desempate REFUTADO fecha, PROCEDE mantém) e os 48 testes de `tests/test_fluxo.py` continuam verdes.
- [ ] Review real `claude` + `openrouter:<slug>`: META com `diff_sha256` de 64 hex, tokens de entrada e saída > 0 nos 2 papéis, `auditor_custo` em `US$` > 0 e `diversidade: vendor`; `sdd-fluxo.sh loop` sobre a pasta sai 0, 10 ou 20 (nunca 64).
- [ ] Todo script novo sem `mapfile`/`declare -A`/`${X^^}`, com fixture e teste dos dois lados; 1 sabotagem por script novo ou alterado reprova pelo menos um teste nomeado; testes novos vermelhos na `v2.2.10`.
- [ ] `skill-lint --conversa` 17/17; `sdd-decisoes-lint --sites .agents/skills` 16 perguntas e `sdd/templates/fragments` 2; `check-versions --base v2.2.10 --base-obrigatoria` verde; Verify Gate `--strict` 0; revisão de contexto fresco sem HIGH aberto; Release `v2.3.0` com `SHA256SUMS.txt` conferido.
- [ ] Tempo de cada papel e custo por review: sem meta (TBD); medidos e registrados no BUILD_REPORT.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `sdd/review/registry.tsv` is read, it **shall** hold one TAB-separated line per engine with the columns `engine`, `adapter`, `modelo`, `cobranca`, `papeis`, `timeout_s`, `sinal_auth`, `sinal_transitorio`, `sinal_persistente`, in that order, a commented header describing each, and exactly the 4 engines `claude`, `codex`, `gemini`, `openrouter`; `codex` **shall** be invoked read-only (`-s read-only`), and no line, comment or script **shall** define a default chain | test |
| AT-002 | Event-driven | **When** `adversarial-review.sh` resolves a role, it **shall** take the ids from `--reviewer`/`--auditor` or, when absent, from `review.revisor1`/`review.auditor` of `sdd/config.yaml`; each value is one id or a comma-separated list (the chain the project configures, first = default); an id `openrouter:<slug>` **shall** use the `openrouter` line with `<slug>` as model | test |
| AT-003 | Unwanted | **If** a role has no id (flag and slot empty), an id is not in the registry, the registry is unreadable or a line has a column count other than 9, **then** the script **shall** exit 64 naming the slot or the id and the valid ids, without calling any engine | test |
| AT-004 | Unwanted | **If** the effective auditor list's first id equals the reviewer's first id (`review.auditor == review.revisor1`) and `--um-engine` is absent, **then** the script **shall** exit 67 with `RESULTADO: PAROU` and the `→` of AT-023 for exclusion, without calling any engine and without creating the output folder | test |
| AT-005 | Event-driven | **When** `--um-engine` is given, the same engine **shall** run reviewer and auditor in separate calls, the META **shall** have `diversidade: nenhuma`, and the output **shall** start with `⚠️ a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos da revisão`; otherwise `diversidade` **shall** be `vendor` when the two adapters differ and `modelo` when the adapter is the same with another model | test |
| AT-006 | Event-driven | **When** the script freezes the diff, it **shall** diff the merge-base of `--base` (default `origin/<project.default_branch>`, else the local branch) and the working tree, locate the index with `git rev-parse --git-path index` (works in a linked worktree; an absent index counts as empty), include untracked files through a temporary copy of it, pin `-c diff.noprefix=false --no-renames --diff-algorithm=myers` so the user's git config cannot change the bytes, exclude `review.output_dir` and the SDD artifact folders (`sdd/features`, `sdd/reports`, `sdd/reviews`, `sdd/releases`, `sdd/handoffs`, `sdd/traces`) unless `--paths` names them, restrict to `--paths` when given, write `diff.patch`, and record its sha256 as `diff_sha256` (64 hex) in the META | test |
| AT-007 | Unwanted | **If** the frozen diff is empty or larger than 8 MB (constant `DIFF_MAX_MB`), or `--base` resolves to no commit, **then** the script **shall** exit 64 saying which (an empty diff would review nothing) and call no engine | test |
| AT-008 | Event-driven | **When** `--feature <F>` is given, the script **shall** inject, in this order, the `BRAINSTORM_<F>.md`, `DEFINE_<F>.md`, `DESIGN_<F>.md` of `sdd/features/` and `BUILD_REPORT_<F>.md` of `sdd/reports/` that exist into `context-sdd.md`; above `review.context_max_kb` (default 180) it **shall** drop the BRAINSTORM first and then cut the remainder with a marker, and the META **shall** list `docs_sdd`, `contexto` (KB and count) and `contexto_cortado`; without `--feature` it **shall** run with `docs_sdd: -` and the line `⚠️ sem --feature: a revisão não leu BRAINSTORM, DEFINE nem DESIGN, e decisões já documentadas podem voltar como achado` | test |
| AT-009 | Unwanted | **If** `review.output_dir` (default `sdd/reports/reviews`) is not ignored by git (`git check-ignore`), **then** the script **shall** exit 64 before calling any engine, printing `🛑 a pasta <dir> não está ignorada pelo git: o diff e as respostas das engines iriam para o repositório.` and `→ rode: printf '%s\n' '<dir>/' >> "$(git rev-parse --git-common-dir)/info/exclude"` (valid in a linked worktree too) | test |
| AT-010 | Event-driven | **When** an adapter is sourced, it **shall** define `adapter_disponivel`, `adapter_invocar`, `adapter_extrair` and `adapter_credencial` (one line saying where the credential lives, e.g. `OPENROUTER_API_KEY no ambiente`); **when** the `openrouter` adapter calls the API, the request body **shall** carry `provider` with `data_collection: "deny"` and `require_parameters: true` and ask for usage accounting; the key **shall** come only from `OPENROUTER_API_KEY` in the environment; the `claude`, `codex` and `gemini` adapters **shall** run their CLI with the prompt on stdin, from a temporary folder, with no write tool (read tools may remain; the prompt says no tool is needed): `claude -p --output-format json --tools "" --safe-mode --no-session-persistence`, `codex exec -s read-only --skip-git-repo-check --ephemeral --json -`, `gemini -o json --approval-mode default`; a test **shall** put fake `claude`, `codex` and `gemini` on `PATH` that record argv, cwd and stdin and assert those exact flags, an empty temporary cwd and the prompt on stdin; the CLI's stderr **shall** go to a separate file, never mixed into the parsed output; the API URL **shall** be overridable only by `SDD_REVIEW_OPENROUTER_URL` (tests) | test |
| AT-011 | Event-driven | **When** a reviewer answers, the script **shall** write `reviewer.md` with the raw answer and `reviewer.verdicts.jsonl` with one line per object of the `<<<VERDICTS` … `VERDICTS>>>` block (keys `achado`, `arquivo`, `linha`, `severidade` HIGH/MED/LOW, `confianca`, `resumo`); an empty block **shall** count as zero findings | test |
| AT-012 | Unwanted | **If** a reviewer or auditor answer has no `<<<VERDICTS` block, or a line inside it is not a JSON object with the required keys, **then** that role's exit in the META **shall** be 68 with the motive, it **shall** never be read as zero findings, and the script **shall** exit 68 | test |
| AT-013 | Event-driven | **When** the auditor runs, it **shall** receive the diff, the context and the reviews, and the script **shall** write `auditor.md` and `auditor.verdicts.jsonl` with `achado` and `veredito` in AGREE/DISAGREE_EVIDENCE/DISAGREE_CONCERN/NOVO (`NOVO` with `severidade`), readable by `sdd-fluxo.sh loop` without change | test |
| AT-014 | Event-driven | **When** the reviewer finishes, the script **shall** call a 2nd reviewer if any trigger holds — a diff path matching `review.security_globs`, `layers.sql` or a path segment (split on `/`, `.`, `_`, `-`) equal to `auth`, `login`, `token(s)`, `senha(s)`, `password` or `jwt` (`author.md` does not count); 8 or more files; 120 KB or more of patch (`wc -c` / 1024); 2 or more `layers:` touched; or a shallow reviewer (under 30 s with 0 findings) — recording `gatilho_2o_revisor` with the value and the limit (`9 arquivos (limiar 8)`), or `diff sem gatilho de risco — 1 revisor`; the limits **shall** be named constants in the script; `--no-revisor2` **shall** skip it and record why | test |
| AT-015 | Event-driven | **When** a 2nd reviewer is triggered, its engine **shall** be `--revisor2` or the first registry line with the `revisor` role that is available (CLI on `PATH` or key in the environment) and is neither the effective reviewer nor the auditor; with none, the META **shall** have `revisor2_engine: indisponível` and `revisor2_exit: 67`; when it is called and fails with any exit (65 and 66 included), the META **shall** record that `revisor2_exit`, the output **shall** carry a ⚠️ line, and the auditor **shall** still run over the 1st reviewer — a 2nd-reviewer failure never stops the chain; with two reviewers, the ids in the jsonl files **shall** carry `@<engine>` (`R1@claude`) | test |
| AT-016 | Event-driven | **When** the auditor answers `DISAGREE_EVIDENCE` on a HIGH and `--no-desempate` is absent, the script **shall** call a tie-break engine outside {origin of the finding, auditor} on the first such HIGH and record `desempate_alvo` (the id as written in the reviewer's jsonl, even when the auditor used the base id), `desempate_engine` and `desempate_decisao` (`DECISAO:PROCEDE` or `DECISAO:REFUTADO`); with no eligible engine it **shall** record `desempate_engine: indisponível` | test |
| AT-017 | Event-driven | **When** a call fails (adapter exit other than 0, timeout, or no answer text extracted — the signals are never matched against a successful answer) and its raw output or stderr matches the registry `sinal_auth`, or the adapter exits 65 (key absent), the role **shall** stop with exit 65 and the script **shall** exit 65 without calling the next id of the list (a credential failure is never fallback) | test |
| AT-018 | Event-driven | **When** a failed call's output matches `sinal_transitorio` (429), the script **shall** call the same engine again up to 2 more times, waiting `SDD_REVIEW_ESPERA` seconds (default 30) between calls, and only then treat it as persistent | test |
| AT-019 | Event-driven | **When** a failed call's output matches `sinal_persistente` (quota or billing), the call times out (`timeout_s`), or the CLI is not on `PATH` (66), the script **shall** advance to the next id of the list, recording `<papel>_engine_default`, `<papel>_engine_efetivo`, `<papel>_fallback_usado: sim` and `<papel>_motivo`, and print `⚠️ o <papel> previsto (<a>) falhou (<motivo>); quem <revisou|auditou> foi <b>`; with the list exhausted the role exit **shall** be 67 (66 when the only cause was a missing CLI) and the script **shall** exit with it | test |
| AT-020 | Event-driven | **When** a role ends, the META **shall** record `<papel>_tokens_entrada`, `_saida`, `_total`, `_modelo`, `_segundos` and `_custo`, with `_custo` from the engine's own report (`US$ x`), else an estimate from `sdd/review/precos.tsv` (`≈US$ x`), else `assinatura` when the registry says so, else `$?` — never `0` or `US$ 0` for an unknown cost; and `custo_total`; the printed summary **shall** say `US$ 0,0061`, `≈ US$ 0,01 (estimado)`, `incluído na assinatura` or `custo desconhecido` for those 4 forms, and how many roles have an unknown cost | test |
| AT-021 | Event-driven | **When** `sdd/review/precos.tsv` is read, each line **shall** have `engine`, `modelo`, `usd_mtok_entrada`, `usd_mtok_saida`, `fonte` and `conferido_em`, `fonte` being an `https://` URL of the provider's public price list (for OpenRouter, `https://openrouter.ai/api/v1/models`) and `conferido_em` an ISO date; a model absent from the file **shall** produce `$?` | test |
| AT-022 | Event-driven | **When** the run completes, the META **shall** record `convergencia_1o_passe` as `sim` (every finding AGREE, no NOVO), `nao`, or `n/a (<motivo>)` when the auditor did not run, failed or a reviewer was shallow; the motive texts **shall** be `n/a (auditor não rodou)`, `n/a (auditor falhou)`, `n/a (revisor1 raso: 0 achados em <n>s)` and `n/a (2º revisor raso: 0 achados em <n>s)`; the script **shall** exit 0 whenever the reviewer and the auditor ended 0, whatever the findings and whatever the 2nd reviewer did, and otherwise with the exit of the first of those two that did not; a failed tie-break **shall** leave `desempate_decisao: -` and not change the exit | test |
| AT-023 | Event-driven | **When** the script finishes, it **shall** print, after any ⚠️ lines (fallback, same engine, no context, and `⚠️ o revisor terminou em <n> s sem achados: isso não conta como revisão`), one `RESULTADO:` line — `REVIEW COMPLETA` (exit 0), `REVIEW INVÁLIDA` (68, naming the role and saying `a engine respondeu fora do formato; isto não é zero achados`) or `PAROU` (64–67) —, with a ⚠️ `o 2º revisor (<engine>) <falhou (<motivo>) | não tinha engine disponível>: a revisão vale só com a dispensa registrada no ledger` when that happened, then the folder, `diff_sha256`, the engine and model per role, `diversidade`, the findings per severity in words (`2 graves, 1 médio, 0 leves`, never for an invalid review) and the cost per role and total, and end with one `→` line: on 65 `confira a credencial de <engine> (<saída de adapter_credencial>); a revisão não troca de engine por falha de credencial`, on 67 by exclusion `escolha outra engine para auditar (review.auditor) ou rode com --um-engine`, on 67 by exhausted list `acrescente outra engine à lista ou tente mais tarde` | test |
| AT-024 | Event-driven | **When** `--dry-run` is given, the script **shall** freeze the diff and the context, print the roles with the chosen engines, the triggers, the sizes and the sha256, call no engine, and exit 0 | test |
| AT-025 | Event-driven | **When** `adversarial-review.sh --conferir [<pasta>] [--aceitar-sem-revisor2 "<motivo>"]` runs, it **shall** recompute the frozen diff with the base and paths recorded in that review's META (default: the newest review folder in `review.output_dir`) and exit 0 printing `✅ a revisão <pasta> é desta versão do código (sha256 igual).`, `review_externo: <pasta> sha256=<hex> diversidade=<valor>` (plus ` revisor2=dispensado — <motivo>` when used) and `RESULTADO: CONFERE` + `→`, when the sha256 matches, `reviewer_exit` and `auditor_exit` are 0 and `revisor2_exit` is 0 or `-` (or not 0 with `--aceitar-sem-revisor2` and a motive of 3+ characters); otherwise it **shall** exit 2 with `RESULTADO: NÃO CONFERE` and a `→` saying why (sha256 differs, role failed, 2nd reviewer without dispensation, no review) | test |
| AT-026 | Event-driven | **When** `adversarial-review.sh --ledger <arquivo.yaml>` runs, it **shall** resolve `<pasta>` against the repository root of the current directory and exit 0 (`RESULTADO: LEDGER OK`) if the ledger has a `review_externo:` line that is either `dispensado — <motivo>` with a motive of 3+ characters or `<pasta> sha256=<hex>` whose `META.txt` exists with the same `diff_sha256`; it **shall** exit 2 naming the problem when the line is absent or malformed, or when the folder does not exist here (`a pasta <pasta> não existe aqui: rode na pasta da frente`), and 64 when the file is unreadable; a test **shall** run it from a 2nd worktree | test |
| AT-027 | Event-driven | **When** `sdd-release` runs phase 0a, it **shall** run `--conferir`; with exit 2 it **shall** ask, before the OK block, `**Sua decisão** — [D3 · muda a regra do método] **Esta versão não tem revisão por outra engine. Como seguimos?**` with **rodar agora** (recomendado; runs the review over this front's diff, usually 2 to 15 minutes, cost shown at the end), **publicar sem revisão** (asks for a one-sentence motive that goes to the release record) and **não sei**, written in `references/como-falar.md` of `sdd-release`; in phase 1 the ledger (step 3) **shall** get the `review_externo:` line and `--ledger` **shall** run in the front's folder right after the atomic commit (step 4) and before landing (step 5), aborting on any exit other than 0; the OK block **shall continue to** have one question only | test |
| AT-028 | Event-driven | **When** `sdd-fluxo.sh loop` reads a META whose `revisor2_engine` is not `-`: with `revisor2_exit` 65 or 66 or the engine `indisponível` and no ledger line `revisor2: dispensado rodada=N — <motivo>` it **shall** exit 20 (D3); with another non-zero exit it **shall** exit 10 (redo); with `revisor2_exit` absent it **shall** exit 64; with the dispensation line it **shall** record it as a `motivo:` and decide on the rest | test |
| AT-029 | Event-driven | **When** `loop` reads `convergencia_1o_passe` starting with `n/a (revisor1 raso` or `n/a (2º revisor raso`, or `revisor1_raso: sim` with no 2nd reviewer, it **shall** exit 10 with `review rasa` (never 0); when the 2nd reviewer ran with exit 0 it **shall** read `reviewer2.verdicts.jsonl` too and exit 64 if the same id appears in both files | test |
| AT-030 | Event-driven | **When** a HIGH has `DISAGREE_EVIDENCE` from the auditor and no ledger verdict, `loop` **shall** close it when it is `desempate_alvo` with `desempate_decisao` exactly `DECISAO:REFUTADO`, keep it open (not an impasse) when it is `DECISAO:PROCEDE`, and **shall continue to** exit 20 with D5 otherwise | test |
| AT-031 | Non-regression | The system **shall continue to** give the same exit and output as v2.2.10 for every `loop` fixture of `sdd/fixtures/fluxo/` (no `revisor2_*`, `desempate_*` or `revisor1_raso` keys), including the 3 edge cases (invalid review without jsonl, NEEDS_WORK on the ceiling, HIGH with pending receipt), and `sdd-fluxo.sh --self-test` **shall** exit 0 | test |
| AT-032 | Event-driven | **When** `sdd-build` starts, a step 0 **shall** run `bash sdd/bin/sdd-fluxo.sh review-design <DESIGN>`; on 0 (required) with no DESIGN review row in the Advisor Ledger it **shall** run the DESIGN review (reviewer then auditor, `adversarial-review.sh --paths` over the DEFINE and the DESIGN) before task 1; on 1 it **shall** record it as dispensable; on 64 it **shall** run it and record why | test |
| AT-033 | Event-driven | **When** `sdd-design` "Review adversarial do DESIGN" and `sdd-build` 5c are read, they **shall** tell the agent to run `bash sdd/bin/adversarial-review.sh` (reviewer, then auditor, never in parallel), feed `sdd-fluxo.sh loop` with the folder, and record each finding in the Advisor Ledger; 5c **shall** say the release requires the review; no engine name (`claude`, `codex`, `gemini`, `openrouter`, case-insensitive) **shall** appear in the sections the F10 adds or changes (sdd-design "Review adversarial do DESIGN", sdd-build 0 and 5c, sdd-release 0a item 8 and phase 1 steps 3–4, the D3 question in `como-falar.md`), asserted in `tests/test_contrato_build_release.py` | test |
| AT-034 | Event-driven | **When** `sdd/config.example.yaml` is read, `review:` **shall** have `registry: sdd/review/registry.tsv`, `revisor1: ""`, `auditor: ""`, `output_dir: sdd/reports/reviews`, `context_max_kb: 180` and `security_globs: ""`, each with a comment saying what it changes and its unit; `vendors` **shall** be gone from `review:` | test |
| AT-035 | Event-driven | **When** `bin/sdd-open.sh init` runs, it **shall** copy `sdd/review/` (registry, prices, prompts) and `sdd/bin/adapters/` as it copies `sdd/bin/`, completing what is missing and never overwriting an edited file; `doctor` **shall** also flag an outdated file under `sdd/bin/adapters/` | test |
| AT-036 | Event-driven | **When** `sdd/review/prompts/reviewer.md`, `auditor.md` and `desempate.md` are read, each **shall** name no vendor, state that the material comes inline and no tool is needed (engines run without write tools), and fix the output contract parsed by the script (the `<<<VERDICTS` block, or the `DECISAO:` line for the tie-break) | test |
| AT-037 | Event-driven | **When** `RESUMO_ETAPA.md`, `ADVISOR_CONSULT.md` and `BUILD_REPORT_TEMPLATE.md` are read, they **shall** name `sdd/bin/adversarial-review.sh` and `review.output_dir` instead of `/adversarial-review` and `sdd/reviews/EXTERNAL_REVIEW_*` | test |
| AT-038 | Non-regression | The system **shall continue to** pass the 744 existing tests, `verify-gate.sh`, `report-lint.py`, the F8 hooks, `skill-lint.py --conversa` on the 17 skills, `playbook-lint.sh --self-test`, the release OK block contract and `publish-gate.sh` in `ci` mode; `tests/test_bash32.py` **shall** scan the new scripts and adapters | test |
| AT-039 | Unwanted | **If** `adversarial-review.sh` or the changed `sdd-fluxo.sh` is sabotaged (exclusion, verdict parsing, failure class, cost fallback, `--conferir`, the 2nd reviewer or the tie-break rule removed or inverted), **then** at least one named test **shall** fail and `git checkout` **shall** turn the suite green again (`evidence/F10_REVISAO/sabotagem.log`); the new tests **shall** fail on the `v2.2.10` tree (`evidence/F10_REVISAO/baseline.log`) | test |
| AT-040 | Event-driven | **When** `evidence/F10_REVISAO/real.sh` adds the output folder to `$(git rev-parse --git-common-dir)/info/exclude` and runs `adversarial-review.sh --reviewer claude --auditor openrouter:<slug> --no-revisor2 --feature F10_REVISAO` over the F10 commit with `OPENROUTER_API_KEY` from the environment, the AT **shall** pass if and only if the META has a 64-hex `diff_sha256`, `reviewer_tokens_entrada` and `auditor_tokens_entrada` above 0, `auditor_custo` `US$` above 0, `diversidade: vendor`, and `sdd-fluxo.sh loop` over the folder exits 0, 10 or 20 (`evidence/F10_REVISAO/real.log`) | manual-ux |
| AT-041 | Event-driven | **When** a role starts, the script **shall** print `▶ <papel>: <engine> (<modelo>) — até <n> min` with `n` from the registry `timeout_s`; and `docs/adversarial-review.md` and `docs/pt-BR/adversarial-review.md` **shall** exist, be linked from the READMEs, and explain the 2 slots to fill, cost, privacy, `--um-engine`, the release dispensation and a table of the exits with the fix of each (`tests/test_docs.py`); `docs/adaptation-guide.md` (+ PT) **shall** say model names live in `sdd/review/registry.tsv` and `precos.tsv`; the roadmap row "Adversarial review" **shall continue to** be *planned* until the F11 | test |

---

## Clarifications

### Session 2026-10-31

- [x] (Scope) As 5 decisões do BRAINSTORM entram como estão: registry com 4 engines sem cadeia padrão (AT-001); 5 slots + constantes (AT-014, AT-034); R1 sempre com dispensa D3 (AT-025–AT-027); F10 + F11 nesta sessão, a F11 com DEFINE próprio depois da Release da F10; `v2.3.0` por tag.
- [x] (Data model) **Achado do Define:** `sdd/config.example.yaml` já tem `review.vendors` (anterior à F9), sem consumidor no código. Ele é substituído por `revisor1`/`auditor` + registry e sai do exemplo (AT-034); o `init` nunca reescreve um `config.yaml` existente, então um projeto antigo fica com a linha sem efeito.
- [x] (Data model) **Achado do Define:** o diff congelado exclui as pastas de artefatos SDD (AT-006). Eles já entram como contexto (R4), e incluí-los mudaria o `diff_sha256` a cada linha de ledger ou de BUILD_REPORT gravada depois da revisão — a release nunca conferiria (AT-025). `--paths` explícito inclui o que nomear (é como a revisão do DESIGN funciona, AT-032).
- [x] (Edge cases) "1 engine só" é explícito (`--um-engine`), não automático: `auditor == revisor1` sem o flag é 67 (R5), com ele é `diversidade: nenhuma` (AT-004/AT-005), conciliando o 67 do plano com a degradação com aviso do brainstorm do Open.
- [x] (Edge cases) O desempate segue o formato do privado (um `desempate_alvo` por execução, `DECISAO:REFUTADO`/`DECISAO:PROCEDE` exatos); outro HIGH refutado na mesma rodada continua D5 no `loop` (AT-016, AT-030).
- [x] (Edge cases) 2º revisor indisponível (65, 66 ou `indisponível`) sem dispensa no ledger é 20 (D3), como o "estrutural" do privado; falha passageira é 10 (AT-028).
- [x] (Integrations) `sdd/review/` é pasta nova: o `init` passa a copiá-la (AT-035) e a release automática passa a disparar em `sdd/review/**` (detalhe do DESIGN).
- [x] (Terminology) Papéis no META com os nomes do privado (`reviewer_*`, `revisor2_*`, `auditor_*`, `desempate_*`), mais `diversidade` e `custo_total`.
- [x] (UX flow) Não há tela: a interface é a saída do script (⚠️, resumo, `RESULTADO:`/`→`), a pergunta D3 de dispensa da release e o texto das skills; a `sdd-ux-review` revisa esse texto.
- [x] (NFRs) Tempo e custo por papel sem meta: medidos na prova real e registrados no BUILD_REPORT.
- [x] (Done signal) O AT-040 é uma execução real paga (Claude e OpenRouter), fora do `cmd` do gate: `manual-ux` na tabela, com o log como recibo. O `check-versions --base v2.2.10` roda no CI e em `evidence/F10_REVISAO/check-versions.log` (a cópia do `git archive` não tem `.git`).
- [x] (UX flow) **UX review (`sdd/reviews/UX_REVIEW_F10_REVISAO.md`), 5 MUST e 2 SHOULD integrados:** palavras do `RESULTADO` e o `→` por exit (U1, AT-023, AT-004); custo em palavras no resumo, contrato de máquina no META (U2, AT-020); texto da pergunta D3 de dispensa (U3, AT-027); linhas ⚠️ com a consequência (U4, AT-005, AT-008, AT-019, AT-023); parada da pasta não ignorada com o porquê e o comando (U5, AT-009); linha `▶` por papel e `docs/adversarial-review.md` + PT (U6/U7, AT-041); a linha `✅` do `--conferir` (U8, AT-025).
- [x] (Constraints) **Revisão de contexto fresco do DESIGN (`sdd/reviews/REVISAO_DESIGN_F10_REVISAO_20261031.md`, NEEDS_WORK: 1 HIGH, 5 MEDIUM, 13 LOW), tudo aplicado:** o 2º revisor que falha não para a cadeia e o exit vem só do revisor e do auditor (AT-015, AT-022, AT-023, AT-025); `--ledger` na pasta da frente antes do passo 5 (AT-026, AT-027); índice e exclude por `git rev-parse` em worktree (AT-006, AT-009); `adapter_credencial` (AT-010, AT-023); asserts de texto e binários falsos (AT-010, AT-033); LOW: textos da convergência, alvo do desempate, config do diff fixada, segmento de caminho, `RESULTADO:` no `--conferir`/`--ledger`, fonte por URL, docs e doctor.
- [x] (Constraints) Versões: `sdd-release`, `sdd-build`, `sdd-design` sobem minor; demais skills tocadas, patch.

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

- Engine "de sessão", `auditor_exit 75`, `consumir-auditor-sessao.sh`, `--revisor2-arquivo`, `--preparar`/`--out` de reuso.
- `saude_cadeia` entre execuções (aviso após 3 quedas PERSISTENTE).
- `init` editando o `.gitignore` do projeto.
- Gate offline com stub por formato de engine e `eval-agree.sh` (F11, DEFINE próprio).
- Cadeias fixas e engines da RDD (grok, kimi, deepseek, qwen, muse-spark); F12–F15; alterar o sdd-starter ou o privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python 3.9 stdlib; nada de `mapfile`, `declare -A`, `${X^^}` | núcleo em `python3 -B` embutido, como o `sdd-fluxo.sh` |
| Technical | chave de API só por ambiente; nunca em arquivo, stub ou log; o G1 (gitleaks) varre `tests/` e fixtures | stubs com valor gerado em execução ou obviamente falso |
| Technical | nomes de engine só no registry e em `sdd/bin/adapters/` (regra 10 do 8.0) | skills dizem "engine do registry" |
| Technical | delta-only nas skills; o `loop` cresce por delta; o bloco do OK da release mantém uma pergunta só | ATs 027, 028–031 |
| Timeline | F11 depois da Release da F10, na mesma sessão | o DEFINE da F11 é outro arquivo |
| Resource | CI com tetos de 25 (Ubuntu) e 20 min (macOS); suíte em ~15 min no macOS | testes novos com stubs locais, sem espera real (`SDD_REVIEW_ESPERA=0`) |
| Other | repositório privado só leitura; nada da RDD viaja; publish-gate reprova e-mail, CPF/CNPJ e caminho `/Users/<nome>/` | fixtures reescritas a partir das 315 amostras |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/adversarial-review.sh`, `sdd/bin/adapters/`, `sdd/review/`, `sdd/bin/sdd-fluxo.sh` (delta), `.agents/skills/sdd-design`, `sdd-build`, `sdd-release`, `sdd/templates/`, `sdd/config.example.yaml`, `bin/sdd-open.sh`, `docs/`, `tests/`, `sdd/fixtures/revisao/` | toda peça nova no `MANIFEST.txt` |
| **KB Domains** | N/A | fontes do privado lidas só como contrato (plano 8.3) |
| **IaC Impact** | Modify existing | `.github/workflows/release.yml` passa a disparar em `sdd/review/**` |
| **LLM Prompts** | true | sinal forte: a feature cria 3 prompts de runtime (`sdd/review/prompts/reviewer.md`, `auditor.md`, `desempate.md`) enviados a LLMs pelos adapters; o DESIGN inventaria e o Build os escreve pela skill de prompt |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | `claude -p --output-format json` reporta tokens e `total_cost_usd`; a OpenRouter devolve `usage.cost` com a contabilidade pedida | o custo cai para `≈US$` ou `$?` (honesto, mas a prova real exige `US$` no auditor OpenRouter) | no (conferir no DESIGN) |
| A-002 | as 3 CLIs aceitam o prompt por stdin e têm modo sem ferramenta de escrita | o adapter usa arquivo temporário e documenta a limitação | no (conferir no DESIGN) |
| A-003 | a chave de `~/.config/rdd-eval.env` cobre a prova real (saldo ~US$ 246 em 2026-10-31) | a prova real fica pendente | yes |
| A-004 | os testes com stubs cabem no teto de 20 min do `testes-macos` | ajustar o teto do CI | no |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | dor medida no privado (13 de 84) e ausência no Open |
| Users | 3 | 3 consumidores nomeados |
| Goals | 3 | MUST/SHOULD/COULD ligados aos ATs |
| Success | 2 | tempo e custo por papel sem meta (TBD declarado) |
| Scope | 3 | cortes YAGNI e F11 explícitos |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-31 | SDD Define by RDD | Initial version |
| 1.3 | 2026-10-31 | SDD Design by RDD | Revisão de contexto fresco do DESIGN: AT-006, 009, 010, 014–016, 021–023, 025–027, 033, 035, 036, 040, 041 |
| 1.2 | 2026-10-31 | SDD Design by RDD | Contrato de aceite (DESIGN): sinais só na chamada que falhou (AT-017–019); exit e RESULTADO com 2º revisor e desempate (AT-022/023); `--conferir` com o 2º revisor (AT-025); flags concretas e URL de teste (AT-010) |
| 1.1 | 2026-10-31 | SDD Define by RDD | UX review: U1–U8 em AT-004, 005, 008, 009, 019, 020, 023, 025, 027; AT-041 novo |

---

## Next Step

Execute o **SDD Design by RDD**.
