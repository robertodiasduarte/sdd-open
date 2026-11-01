# DEFINE: F11 Revisão adversarial — gate offline

> Um gate que roda a revisão adversarial inteira sem rede, com os adapters de verdade e uma imitação da saída de cada engine, e confere veredito, proveniência e custo extraídos; mais o `eval-agree.sh`, que mede a taxa de AGREE de cada auditor nas revisões já feitas, e os 6 achados adiados da F10.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F11_GATE |
| **Date** | 2026-11-01 |
| **Author** | SDD Define by RDD (sessão 8, Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

A F10 (v2.3.0) publicou `adversarial-review.sh` e 4 adapters, mas os testes ponta a ponta usam um adapter de teste (`stub.sh`): nada prova, sem rede e sem gastar token, que os adapters **reais** de claude, codex, gemini e openrouter levam o veredito, o modelo e o custo de cada engine até o META, e quem adota o pacote não tem um comando que confirme isso na própria máquina. Também não há como saber se um auditor só concorda (taxa de AGREE alta = crítica que não critica), e 6 achados da última revisão real da F10 ficaram adiados para esta frente.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem adota o sdd-open | roda a revisão adversarial no próprio projeto | não tem como conferir, sem gastar crédito, que a instalação lê direito a saída de cada engine; um formato de CLI que muda quebra a extração em silêncio |
| Mantenedor do sdd-open | mantém `sdd/bin/adapters/` e o registry | um adapter que deixa de extrair custo ou modelo só aparece numa revisão paga; não sabe qual auditor é complacente |
| Quem publica uma release | aprova o OK da `sdd-release` | uma revisão com o 2º revisor dispensado por flag passa no `--conferir` sem motivo registrado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | `sdd/bin/adversarial-review-gate.sh`: roda `adversarial-review.sh` ponta a ponta com os 4 adapters reais e stubs por engine, sem rede, e confere por engine os campos extraídos (vereditos, engine e modelo, custo), não só o exit |
| **MUST** | `sdd/review/stubs/`: uma imitação por engine, no formato medido de cada CLI/API (claude JSON, codex JSONL, gemini JSON, openrouter HTTP local), com cenários de sucesso e de falha |
| **MUST** | O gate cobre o contrato: exclusão de papéis (67), resposta sem vereditos (68), credencial (65) sem trocar de engine, 429 com novas tentativas na mesma engine, cota para a próxima da lista, nenhuma engine fora do teste chamada, nenhuma credencial nos artefatos |
| **MUST** | `sdd/bin/eval-agree.sh`: lê as pastas `EXTERNAL_REVIEW_*` já feitas e dá, por auditor (adapter + modelo), vereditos por tipo e a taxa de AGREE; nunca chama engine |
| **MUST** | `--conferir` recusa a revisão com 2º revisor exigido e dispensado por `--no-revisor2` até `--aceitar-sem-revisor2 "<motivo>"` (achado #15) |
| **SHOULD** | Custo honesto: modelo reportado sem preço vira `$?`; tentativa sem custo conhecido aparece no custo do papel (achado #17) |
| **SHOULD** | `--conferir` sem pasta escolhe a mais nova **com** META; `--feature` sem nenhum documento avisa; gemini com mais de um modelo soma os tokens (achado #18) |
| **SHOULD** | CI: teto do job `testes-macos` de 20 para 30 minutos em `release.yml` e `publish-gate.yml` |
| **SHOULD** | Docs: `docs/adversarial-review.md` (+ PT) explica o gate e o `eval-agree`; a linha "Adversarial review" sai do roadmap EN/PT |
| **COULD** | `-v` no gate mostra, por asserção, o valor extraído |

---

## Success Criteria

- [ ] `adversarial-review-gate.sh` sai 0 numa máquina sem rede (proxy apontado para porta morta), com asserções de campo **que discriminam** (o valor esperado difere do que o META mostra quando o `adapter_extrair` daquela engine devolve tudo nulo): claude custo `US$` e modelo; codex tokens de entrada e saída; gemini modelo e tokens; openrouter custo `US$` e modelo `… via …` (≥ 8 no total), mais as asserções de contrato do MUST.
- [ ] Para cada engine, uma cópia do adapter com `adapter_extrair` todo nulo faz o gate sair 2 nomeando uma asserção daquela engine.
- [ ] Sabotagem: cada uma de ≥ 5 quebras (extração de custo do claude, de tokens do codex — a CLI não informa o modelo —, de modelo do gemini, de `usage.cost` do openrouter, exclusão de papéis) faz o gate sair 2 nomeando a asserção que caiu.
- [ ] `eval-agree.sh` sobre a fixture de revisões dá os números conhecidos da fixture (contagem exata por tipo e taxa com 1 casa decimal).
- [ ] O gate roda em ≤ 120 s no piso local (bash 3.2, Python 3.9) e o job `testes-macos` termina em ≤ 25 min sob o teto de 30.
- [ ] Verify Gate verde (suíte inteira no piso), CI verde em Ubuntu e macOS.
- [ ] Release `v2.3.1` automática com `SHA256SUMS.txt` conferido por `shasum -a 256 -c`.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `adversarial-review-gate.sh` runs with no argument, it **shall** build a throw-away git repo with a real diff, run `adversarial-review.sh` against it through the 4 real adapters with the stubs of `sdd/review/stubs/` and print one line per assertion (`✅ N. …` or `❌ N. …` + `→ <o que conferir>`) ending in `RESULTADO:` + `→`; exit 0 when all pass | test |
| AT-002 | Event-driven | **When** each engine (claude, codex, gemini, openrouter) answers as reviewer through its stub, the gate **shall** assert in META/`reviewer.verdicts.jsonl` the verdict count of the stub answer and the fields that engine reports: claude model and cost `US$` from `total_cost_usd`; codex input/output tokens from `turn.completed` (model `-`, the CLI does not report it; cost `assinatura`); gemini model and tokens from `stats.models` (cost `$?`: no price); openrouter model `<slug> via <provedor>` and cost `US$` from `usage.cost`; **when** the openrouter stub omits `usage.cost`, the expected `≈US$` **shall** be computed from the `precos.tsv` and `registry.tsv` that `adversarial-review.sh` resolves and from stub tokens ≥ 10^6 input and ≥ 10^5 output | test |
| AT-003 | Event-driven | **When** each engine answers as auditor, the gate **shall** assert the AGREE/DISAGREE/NOVO verdicts parsed into `auditor.verdicts.jsonl` and `auditor_exit 0` | test |
| AT-004 | Unwanted | **If** the auditor stub answers without the `<<<VERDICTS` block, **then** the gate **shall** assert exit 68 and that no "zero achados" is recorded | test |
| AT-005 | Unwanted | **If** reviewer and auditor resolve to the same engine identity (adapter + model), **then** the gate **shall** assert exit 67 and 0 calls; **and if** the reviewer falls back to the auditor's identity (`--reviewer gemini,codex --auditor codex`, gemini answering quota), **then** it **shall** assert `auditor_exit 67`, `auditor_motivo` containing `excluída`, `reviewer_engine_efetivo codex` and 1 call to codex | test |
| AT-006 | Unwanted | **If** a stub answers with that engine's credential failure, **then** the gate **shall** assert exit 65 and that the next engine of the list was never called | test |
| AT-007 | Unwanted | **If** a stub answers 429 once and then succeeds, **then** the gate **shall** assert 2 calls to the same engine, no change of engine and exit 0 | test |
| AT-008 | Unwanted | **If** a stub answers quota exhausted, **then** the gate **shall** assert the next engine of the list ran and META records the fallback | test |
| AT-009 | State-driven | **While** the gate runs, every engine with no queue entry **shall** append its name to the sentinel and fail (CLI stubs exit 99; the openrouter stub answers HTTP 599 with body `sentinela`); the gate **shall** assert, per scenario, the sentinel empty and each queued engine called exactly the expected number of times | test |
| AT-010 | State-driven | **While** the gate runs, `http_proxy`/`https_proxy` **shall** point to a dead local port, `OPENROUTER_API_KEY` **shall** be a low-entropy value generated in the run, the openrouter URL **shall** be a local server, and the gate **shall** assert the openrouter stub received `Authorization: Bearer <that value>` and `provider.data_collection: deny`, and that the value appears in no file of the review folders | test |
| AT-011 | Unwanted | **If** the gate cannot isolate itself (stub missing; registry without the 4 engines; or, in a child `/bin/bash -c` started with the exact environment passed to `adversarial-review.sh` — `BASH_ENV` and `ENV` unset, no `BASH_FUNC_*` —, `command -v claude|codex|gemini` not resolving under the gate's `bin`), **then** it **shall** exit 3 naming what failed and the resolved value, before any call — never run against a real engine | test |
| AT-012 | Event-driven | **When** one assertion fails, the gate **shall** continue the others and exit 2, listing every failed assertion | test |
| AT-013 | Event-driven | **When** `adversarial-review-gate.sh -v` runs, it **shall** also print the extracted value of each field assertion | test |
| AT-014 | Event-driven | **When** `eval-agree.sh [<pasta>]` runs (default `review.output_dir`), it **shall** read every `EXTERNAL_REVIEW_*/META.txt` + `auditor.verdicts.jsonl` and print a table per auditor (engine + model from META, without the ` via <provedor>` suffix): reviews, verdicts, AGREE, DISAGREE_EVIDENCE, DISAGREE_CONCERN, NOVO and `taxa_agree` with 1 decimal; exit 0 | test |
| AT-015 | Unwanted | **If** a review has `auditor_exit ≠ 0` or no `auditor.verdicts.jsonl`, **then** `eval-agree.sh` **shall** leave it out of the rates and count it in a "fora da conta" line with the reason | test |
| AT-016 | Unwanted | **If** no usable review exists, **then** `eval-agree.sh` **shall** exit 2 saying how many folders it read; bad usage exits 64 | test |
| AT-017 | State-driven | **While** `eval-agree.sh` runs, it **shall** call no engine and open no network connection (verified by a run with dead proxies and a `PATH` with no engine CLI, and by `eval-agree.sh` containing no `urllib`, `socket` nor `adapters/`) | test |
| AT-018 | Unwanted | **If** META records a 2nd-reviewer trigger dispensed by `--no-revisor2`, **then** `--conferir` **shall** exit 2 unless `--aceitar-sem-revisor2 "<motivo>"` is given, and then print `review_externo: … revisor2=dispensado — <motivo>` | test |
| AT-019 | Unwanted | **If** the model an engine reports has no price in `precos.tsv` and differs from the configured one, **then** the role cost **shall** be `$?`, never the tariff of the configured model | test |
| AT-020 | Unwanted | **If** a role had an attempt that hit the time cap on an engine not billed by subscription (the engine may have processed and billed without reporting), **then** the role cost **shall** show what is known followed by `+ $?`; a refused attempt (auth, 429, quota) **shall continue to** add nothing | test |
| AT-021 | Event-driven | **When** `--conferir` runs with no folder, it **shall** pick the newest `EXTERNAL_REVIEW_*` that has a `META.txt`, skipping folders without one | test |
| AT-022 | Unwanted | **If** `--feature F` finds none of the SDD documents of F, **then** the script **shall** print a warning naming the 4 paths it looked for and continue | test |
| AT-023 | Event-driven | **When** gemini reports more than one model in `stats.models`, the adapter **shall** sum the tokens of all of them and report every model | test |
| AT-024 | Non-regression | `adversarial-review.sh`, `--conferir`, `--ledger` and `sdd-fluxo.sh loop` **shall continue to** pass the F10 tests unchanged except for the 6 deferred findings above | test |
| AT-025 | Event-driven | **When** the workflows run, `testes-macos` **shall** have `timeout-minutes: 30` in `release.yml` and `publish-gate.yml` (`tests/test_release_workflow.py`) | test |
| AT-026 | Event-driven | **When** the docs are read, `docs/adversarial-review.md` and `docs/pt-BR/adversarial-review.md` **shall** explain the gate (command, what it proves, exits 0/2/3/64) and `eval-agree.sh` (what `taxa_agree` means), and the roadmap row "Adversarial review" **shall** be gone from EN and PT with the count in `tests/test_docs.py` updated | test |
| AT-027 | Event-driven | **When** the package is built, `MANIFEST.txt` **shall** list every new file, the new scripts **shall** pass the bash 3.2 grep (`mapfile`, `declare -A`, `${x^^}`) and `sdd-open.sh init` **shall** copy `sdd/review/stubs/` with the rest of `sdd/review/` | test |

---

## Clarifications

### Session 2026-11-01

- [x] (Integrations) O `eval-agree.sh` chama engines? → **só lê revisões já feitas** (conta os `auditor.verdicts.jsonl` das pastas `EXTERNAL_REVIEW_*`; sem custo, sem rede, roda sobre as fixtures); integrado em Goals, AT-014–AT-017 e Out of Scope.
- [x] (Scope) 2º revisor exigido e dispensado por `--no-revisor2` → **a release pede motivo**: o `--conferir` recusa até `--aceitar-sem-revisor2 "<motivo>"`; o uso do script não muda; integrado em AT-018.
- [x] (Scope) Achados #17 e #18 da rodada 3 da F10 → correções sem escolha (decididas no Define): AT-019–AT-023.
- [x] (Done signal) Versão → `v2.3.1` automática (decidida no brainstorm da F10).

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

- `eval-agree.sh` re-rodar auditores sobre revisões antigas (`--executar`): custa uma chamada paga por caso; fica para quando houver demanda.
- Gate com rede ou com engine real (isso é a revisão real, já coberta pelo `adversarial-review.sh`).
- Alerta automático de "auditor complacente" por limiar de `taxa_agree`: o número sai; o julgamento é humano.
- Stubs de engines fora do registry (grok, kimi e outras do privado).
- `doctor` rodar o gate.
- Exigir motivo na própria flag `--no-revisor2` (quebraria o uso publicado na v2.3.0).
- F12–F14 (cartógrafo, curator, `/drive`); alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | Piso bash 3.2 + Python 3.9 stdlib; sem `timeout`, sem `mapfile`/`declare -A` | gate em bash com núcleo Python por heredoc, como o `adversarial-review.sh` |
| Technical | Nada de rede: o servidor do openrouter é local (`SDD_REVIEW_OPENROUTER_URL`), as CLIs são scripts no `PATH` do gate | o gate nunca toca engine real; injeção que falha = exit 3 |
| Technical | Chave de API nunca em arquivo nem em stub | valor gerado na execução, de baixa entropia |
| Technical | Reescrita pelo contrato: nada copiado do privado | asserções novas sobre o contrato do Open |
| Resource | CI macOS levou 18m31s no PR da F10 | teto sobe para 30; o gate entra no job sem passar de 25 min |
| Other | `sdd/features|handoffs|reports|reviews|traces/` fora do commit; `git add` por nome | — |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/adversarial-review-gate.sh`, `sdd/bin/eval-agree.sh`, `sdd/review/stubs/**`, deltas em `sdd/bin/adversarial-review.sh`, `sdd/bin/adapters/gemini.sh`, `.github/workflows/*.yml`, `docs/**`, `tests/**`, `MANIFEST.txt` | `release.yml` já publica `sdd/review/**` e `sdd/bin/**` ⇒ patch automático `v2.3.1` |
| **KB Domains** | N/A | contrato em `docs/adversarial-review.md` e no cabeçalho `USO-INICIO` do script |
| **IaC Impact** | Modify existing | 2 workflows: só o `timeout-minutes` do macOS |
| **LLM Prompts** | false | o gate e o `eval-agree` não escrevem nem mudam prompt; usam os 3 prompts da F10 como estão, e os stubs devolvem respostas fixas |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | As saídas medidas na F10 (`sdd/fixtures/revisao/saidas/`) são o formato atual de cada CLI | o stub imita um formato velho; o gate passa e a revisão real falha | yes (medidas em 2026-10-31) |
| A-002 | `urllib` respeita `http_proxy`/`https_proxy` e `no_proxy=127.0.0.1` deixa só o servidor local; o gate sobrescreve o `no_proxy` minúsculo | um adapter poderia sair para a rede no gate | yes (`AVAL-DESIGN-01-urllib-proxy.log`, Python 3.9.6) |
| A-003 | O gate cabe em ≤ 120 s no piso | o job macOS passa de 25 min | no (medir no build) |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | lacuna concreta: E2E só com `stub.sh`, sem prova dos adapters reais |
| Users | 3 | 3 papéis com dor própria |
| Goals | 3 | MUST/SHOULD/COULD fechados; 2 decisões respondidas |
| Success | 3 | contagem de asserções, sabotagens, tempo e release |
| Scope | 2 | o formato dos cenários dos stubs fica para o Design |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-01 | SDD Define by RDD | Initial version |
| 1.1 | 2026-11-01 | SDD Define by RDD | revisão de contexto fresco do DESIGN (`sdd/reviews/REVISAO_DESIGN_F11_GATE_20261101.md`): AT-002 só com campos que discriminam e ≈US$ calculado; AT-005 com fallback para a identidade do auditor; AT-009 sentinela HTTP 599 e contagem de chamadas; AT-010 Bearer e deny; AT-011 BASH_ENV/BASH_FUNC; AT-014 sem ` via`; AT-017 verificável; A-002 medida |

---

## Next Step

Execute o **SDD Design by RDD**.
