# BUILD REPORT: F10 Revisão adversarial — núcleo

> Implementation report for F10 Revisão adversarial — núcleo

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F10_REVISAO |
| **Date** | 2026-11-01 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F10_REVISAO.md` |
| **DEFINE** | `sdd/features/DEFINE_F10_REVISAO.md` (v1.3, 41 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F10_REVISAO.md` (v1.1, 11 decisões, 86 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f10-revisao`, sobre `89ac76f` (= `v2.2.10`).
- **Commits:** `7ecbc78` build · `6f4ee5b` revisão real (claude → openrouter) · `9846919` avaliador ciclo 1 · `486ed2e` avaliador ciclo 2 · `1975e7c` revisão real final, rodada 1 · `55a866d` teste do índice racy determinístico · `248301d` rodada 2. Escopo: `sdd/reports/evidence/F10_REVISAO/escopo.log` (83 arquivos tocados, 55 novos).
- **Fontes (só leitura):** `origin/main` do privado (`1b1c1d41b`): `scripts/adversarial-review.sh`, `adapters.sh`, `registry.tsv`, `precos.tsv`, `prompts/`, `sdd-fluxo.sh`, 315 `META.txt` e o `DOGFOOD_20260824/`. Nada foi alterado lá.
- **Revisões:** do DESIGN (`sdd/reviews/REVISAO_DESIGN_F10_REVISAO_20261031.md`, 19 notas aplicadas no DESIGN v1.1/DEFINE v1.3); do build, ver `## Contrato de aceite (C2) e avaliador de contexto fresco (C1)` e `## Advisor Ledger`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 86 linhas: 55 novos (script, 4 adapters, registry, preços, 3 prompts, 41 fixtures, 2 testes, 2 docs) e 31 alterados |
| Cross-file coupling | Alto: as chaves do META são lidas pelo `loop`, pela release (`--conferir`, `--ledger`) e pelos docs |
| Security surface | Chave de API (só ambiente, nunca arquivo); dado do diff enviado a terceiros (`data_collection: deny`, pasta ignorada pelo git) |
| LLM prompt items | 3 (`sdd/review/prompts/reviewer.md`, `auditor.md`, `desempate.md`) |
| Independent volume | Médio: 1 script grande + 4 adapters pequenos + texto de 3 skills |
| Context-rot risk | Alto: brainstorm ao build numa sessão; mitigado pelas revisões de contexto fresco e pela revisão adversarial real |
| Runtime capabilities | default e subagente disponíveis |

**Recommendation:** default.

**User decision:** default. O Roberto pediu "execute o define, design, review do design, build, review do build"; o modo foi registrado, não perguntado.

**Pre-build review:** Sim — revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 1 HIGH, 5 MEDIUM, 13 LOW), aplicada no DESIGN v1.1 e no DEFINE v1.3 antes do código.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 86/86 |
| **Files Created** | 55 (+3 de evidência fora do commit) |
| **Files Modified** | 31 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 7 Verify Gates, 16 grupos de evidência por AT, 14 sabotagens, 6 baselines, 4 revisões reais |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: `sdd/bin/adversarial-review.sh` (bash 3.2 + núcleo Python 3.9, 1.041 linhas antes das rodadas); 4 adapters em `sdd/bin/adapters/` (claude, codex, gemini, openrouter); `sdd/review/` com registry, preços e prompts; `sdd-fluxo.sh loop` com 2º revisor, revisão rasa e desempate; `sdd-release` 2.6.0 (review externo obrigatório com dispensa D3), `sdd-build` 2.5.0 (passo 0 e 5c), `sdd-design` 2.3.0; `init` copia `sdd/review/`; `docs/adversarial-review.md` + PT. Testes: 744 → 853 no piso.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1–2 | registry e preços | direct | Complete | `test_revisao.Registry` | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| 2 | 3–5 | 3 prompts (skill de prompt) | direct | Complete | `test_revisao.Prompts` | `sdd/reports/evidence/F10_REVISAO/AT-036.log` |
| 3 | 6–9 | 4 adapters | direct | Complete | `test_revisao_adapters` | `sdd/reports/evidence/F10_REVISAO/AT-010-020-adapters.log` |
| 4 | 10 | `adversarial-review.sh` | direct | Complete | `test_revisao` | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| 5 | 11 | `sdd-fluxo.sh loop` delta | direct | Complete | `test_fluxo` | `sdd/reports/evidence/F10_REVISAO/AT-028-031.log` |
| 6 | 12–49, 84–86 | fixtures, stub, CLIs falsas | direct | Complete | testes acima | `sdd/reports/evidence/F10_REVISAO/AT-017-019.log` |
| 7 | 50–58, 79 | testes novos e alterados | direct | Complete | suíte | `sdd/reports/evidence/F10_REVISAO/verify-gate-248301d.log` |
| 8 | 59–66 | skills e templates | direct | Complete | `test_contrato_build_release` | `sdd/reports/evidence/F10_REVISAO/AT-027-032-033-037.log` |
| 9 | 67–75, 80–83 | config, init, CI, docs, manifest | direct | Complete | `test_sdd_open`, `test_docs` | `sdd/reports/evidence/F10_REVISAO/AT-034-035.log` |
| 10 | 76–78 | evidência (fora do commit) | direct | Complete | `gate-shell-evidencia.sh` | `sdd/reports/evidence/F10_REVISAO/sabotagem.log` |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `sdd/bin/adversarial-review.sh` | Create | 10 | Yes | revisar, `--conferir`, `--ledger`, `--dry-run` |
| `sdd/bin/adapters/claude.sh`, `codex.sh`, `gemini.sh`, `openrouter.sh` | Create | 6–9 | Yes | 4 funções cada |
| `sdd/review/registry.tsv`, `precos.tsv`, `prompts/*.md` | Create | 1–5 | Yes | 4 engines, sem cadeia padrão |
| `sdd/bin/sdd-fluxo.sh` | Modify | 11 | Yes | `loop`: revisor2, rasa, desempate, dispensa com motivo |
| `sdd/fixtures/revisao/**` (25), `sdd/fixtures/fluxo/review-*` (19), `ledger-r2-dispensado.md` | Create | 12–49, 84–86 | Yes | stub, CLIs falsas, saídas medidas |
| `tests/test_revisao.py`, `tests/test_revisao_adapters.py` | Create | 50–51 | Yes | 101 testes |
| `tests/test_fluxo.py`, `test_decisoes_lint.py`, `test_bash32.py`, `test_release_workflow.py`, `test_sdd_open.py`, `test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_docs.py` | Modify | 52–58, 79 | Yes | contratos e pinos |
| `.agents/skills/sdd-release/SKILL.md`, `references/ledger.md`, `references/como-falar.md` | Modify | 59–61 | Yes | R1, pergunta D3 |
| `.agents/skills/sdd-build/SKILL.md`, `.agents/skills/sdd-design/SKILL.md` | Modify | 62–63 | Yes | R13, R12 |
| `sdd/templates/fragments/RESUMO_ETAPA.md`, `ADVISOR_CONSULT.md`, `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | 64–66 | Yes | o script no lugar do comando do privado |
| `sdd/config.example.yaml`, `bin/sdd-open.sh`, `.github/workflows/release.yml` | Modify | 67–69 | Yes | 5 slots; `init`/`doctor`; `sdd/review/**` |
| `docs/adversarial-review.md` + PT; `README.md`, `README.pt-BR.md`, `docs/cli-conventions.md`, `docs/adaptation-guide.md` + PT, `docs/chained-flow.md` + PT | Create/Modify | 70–74, 80–83 | Yes | doc do mecanismo |
| `MANIFEST.txt` | Modify | 75 | Yes | 273 → 331 |

---

## Prompts Generated / Refactored

| Inventory ID | Path | Type | Builder / Skill | Result | Verification |
|---|---|---|---|---|---|
| LP-001 | `sdd/review/prompts/reviewer.md` | one-shot | `sdd-prompt-builder` (regras de `references/prompt-building-rules.md`) | Created: goal, output_contract com o bloco `<<<VERDICTS`, workflow, contexto ausente, verificação | `test_revisao.Prompts`; 4 revisões reais devolveram o bloco válido (`real.log`, `real-final.log`, `real-rodada2.log`, `real-rodada3.log`) |
| LP-002 | `sdd/review/prompts/auditor.md` | one-shot | idem | Created: vereditos AGREE/DISAGREE_*/NOVO, um por achado recebido | idem; o auditor real deu veredito para todos os achados nas 4 execuções |
| LP-003 | `sdd/review/prompts/desempate.md` | one-shot | idem | Created: última linha `DECISAO:PROCEDE` ou `DECISAO:REFUTADO` | `test_revisao.Desempate` (stub); sem desempate real nas 4 execuções (nenhum HIGH refutado com evidência) |

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `sdd/review/registry.tsv` | `gemini` desta máquina sai 41 `ProjectIdRequiredError` | approved deviation | entra como caso real de AUTH nos sinais; a prova real usa `claude` + `codex` + `openrouter` |
| 2 | `sdd/bin/adversarial-review.sh` | a prova real dispara o 2º revisor por segurança (fixture `falha-auth.txt`, segmento `auth`) | false positive aceito | é o comportamento definido (segmento de caminho); o AT-040 usa `--no-revisor2`, as rodadas finais rodam com o `codex` como 2º revisor |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline vermelha da F10 | testes novos na árvore `v2.2.10` | Pass (vermelho esperado: 65 falhas, 28 erros) | `sdd/reports/evidence/F10_REVISAO/baseline.log` |
| Baseline das correções | testes de cada rodada contra o commit anterior | Pass (vermelho esperado em todas) | `baseline-revisao-real.log`, `baseline-ciclo1.log`, `baseline-ciclo2.log`, `baseline-rodada1.log`, `baseline-rodada2.log` |
| Evidência por AT | `gerar-evidencia.sh` (16 grupos) em `248301d` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` e demais |
| Sabotagem | `sabotagem.sh`, 14 mutações | Pass (14/14) | `sdd/reports/evidence/F10_REVISAO/sabotagem.log` |
| Logs de evidência | `gate-shell-evidencia.sh sdd/reports/evidence/F10_REVISAO` | Pass | pasta inteira (inclui os `AVAL*`) |
| Guard antes de cada avaliador | `avaliador-guard.sh` com os 4 prefixos | Pass | `guard-antes-do-avaliador.log`, `guard-antes-do-avaliador-ciclo2.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F10_REVISAO.md` (cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso) |
| **Exit / Result** | 0 em `7ecbc78` (819), `6f4ee5b` (826), `9846919` (833), `486ed2e` (838), `55a866d` (847) e `248301d` (`Ran 853 tests … OK`, publish-gate GREEN) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F10_REVISAO/verify-gate-248301d.log` |

### Manual UX Receipt

AT-040 é uma execução real paga, fora do `cmd` do gate: `real.sh` sobre `7ecbc78` com revisor `claude` e auditor `openrouter:qwen/qwen3.7-plus`. Validado por SDD Build by RDD em 2026-10-31, resultado **PASS** (`sdd/reports/evidence/F10_REVISAO/real.log`, `real-conferir.log`). As 3 rodadas seguintes (com o `codex` como 2º revisor) repetem a prova sobre o código final (`real-rodada3.log`: sha256 `77c64178…`, `loop` PRONTO, `--conferir` CONFERE).

| Attribute | Value |
|---|---|
| Validator | SDD Build by RDD (execução scriptada; recibo do Roberto pendente no OK da release) |
| Date | 2026-10-31 |
| Result | Pass |
| Notes | tokens de entrada 161.519 (claude) e 110.530 (qwen); custo US$ 2,4538 (nominal da assinatura) e US$ 0,0458; `diversidade: vendor` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `skill-lint.py --conversa` (17) e `sdd-decisoes-lint.sh --sites` (16 + 2) | Pass | `skill-lint-conversa.log`, `decisoes-lint.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `verify-gate-248301d.log` |
| Build / Compile | `check-versions.py --base v2.2.10 --base-obrigatoria`; `grep` de bashismos | Pass | `check-versions.log`, `bash32-grep.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | registry com 4 engines, 9 colunas, sem cadeia | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| AT-002 | papéis por flag ou slot; lista; `openrouter:<slug>` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| AT-003 | sem id, id desconhecido, registry ruim → 64 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| AT-004 | auditor = revisor (adapter + modelo) → 67 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| AT-005 | `--um-engine` → nenhuma, aviso primeiro | Pass | `sdd/reports/evidence/F10_REVISAO/AT-001-005.log` |
| AT-006 | diff congelado, não rastreados, worktree, config do usuário | Pass | `sdd/reports/evidence/F10_REVISAO/AT-006-007-024.log` |
| AT-007 | diff vazio, > 8 MB, base inválida → 64 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-006-007-024.log` |
| AT-008 | contexto SDD, teto, BRAINSTORM sai primeiro | Pass | `sdd/reports/evidence/F10_REVISAO/AT-008-009.log` |
| AT-009 | pasta não ignorada → 64 com o comando | Pass | `sdd/reports/evidence/F10_REVISAO/AT-008-009.log` |
| AT-010 | 4 funções, flags exatas, stdin, cwd vazio, corpo OpenRouter | Pass | `sdd/reports/evidence/F10_REVISAO/AT-010-020-adapters.log` |
| AT-011 | `reviewer.md` + jsonl; bloco vazio = 0 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| AT-012 | sem bloco ou linha inválida → 68 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| AT-013 | auditor recebe tudo; jsonl lido pelo `loop` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| AT-014 | gatilhos do 2º revisor e constantes | Pass | `sdd/reports/evidence/F10_REVISAO/AT-014-015.log` |
| AT-015 | escolha, indisponível/67, falha não para a cadeia, `@engine` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-014-015.log` |
| AT-016 | desempate fora de origem e auditor | Pass | `sdd/reports/evidence/F10_REVISAO/AT-016.log` |
| AT-017 | credencial → 65 sem a próxima | Pass | `sdd/reports/evidence/F10_REVISAO/AT-017-019.log` |
| AT-018 | 429 → 2 novas tentativas | Pass | `sdd/reports/evidence/F10_REVISAO/AT-017-019.log` |
| AT-019 | cota, tempo, CLI ausente → próxima; 67/66 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-017-019.log` |
| AT-020 | custo em 4 formas, nunca 0 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-020-021.log` |
| AT-021 | `precos.tsv` com fonte e data | Pass | `sdd/reports/evidence/F10_REVISAO/AT-020-021.log` |
| AT-022 | convergência e exit | Pass | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| AT-023 | resumo, `RESULTADO`, `→` por exit | Pass | `sdd/reports/evidence/F10_REVISAO/AT-011-013-022-023-041.log` |
| AT-024 | `--dry-run` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-006-007-024.log` |
| AT-025 | `--conferir` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-025-026.log` |
| AT-026 | `--ledger`, inclusive de outra worktree | Pass | `sdd/reports/evidence/F10_REVISAO/AT-025-026.log` |
| AT-027 | release: 0a, D3, passos 3–4, um OK | Pass | `sdd/reports/evidence/F10_REVISAO/AT-027-032-033-037.log` |
| AT-028 | `loop`: 2º revisor indisponível/falho/dispensado | Pass | `sdd/reports/evidence/F10_REVISAO/AT-028-031.log` |
| AT-029 | `loop`: rasa e 2 revisores | Pass | `sdd/reports/evidence/F10_REVISAO/AT-028-031.log` |
| AT-030 | `loop`: desempate | Pass | `sdd/reports/evidence/F10_REVISAO/AT-028-031.log` |
| AT-031 | `loop`: não regressão da F9 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-028-031.log` |
| AT-032 | `sdd-build` passo 0 | Pass | `sdd/reports/evidence/F10_REVISAO/AT-027-032-033-037.log` |
| AT-033 | design e 5c, sem nome de engine | Pass | `sdd/reports/evidence/F10_REVISAO/AT-027-032-033-037.log` |
| AT-034 | slots no `config.example.yaml` | Pass | `sdd/reports/evidence/F10_REVISAO/AT-034-035.log` |
| AT-035 | `init` copia, `doctor` avisa | Pass | `sdd/reports/evidence/F10_REVISAO/AT-034-035.log` |
| AT-036 | prompts sem vendor, com contrato | Pass | `sdd/reports/evidence/F10_REVISAO/AT-036.log` |
| AT-037 | templates citam o script | Pass | `sdd/reports/evidence/F10_REVISAO/AT-027-032-033-037.log` |
| AT-038 | não regressão da suíte e dos lints | Pass | `sdd/reports/evidence/F10_REVISAO/verify-gate-248301d.log` |
| AT-039 | sabotagem e baseline | Pass | `sdd/reports/evidence/F10_REVISAO/sabotagem.log` |
| AT-040 | revisão real `claude` + `openrouter` | Pass | `sdd/reports/evidence/F10_REVISAO/real.log` |
| AT-041 | linha ▶ e docs | Pass | `sdd/reports/evidence/F10_REVISAO/AT-041-docs.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 4 ajustes no Design + 19 notas da revisão do DESIGN, todos aceitos (DESIGN `## Contrato de aceite`).
**Veredito do avaliador (C1):** NEEDS_WORK · ciclos: 2 · achados: 5 (ciclo 1: 1 HIGH, 4 LOW) + 5 (ciclo 2: 1 MEDIUM, 4 LOW) · `sdd/reviews/AVALIACAO_F10_REVISAO_20261101-ciclo2.md`

Os 10 achados foram aplicados (`9846919`, `486ed2e`), cada um com teste vermelho no commit anterior (`baseline-ciclo1.log`, `baseline-ciclo2.log`) e sabotagem dos de maior peso. Depois do ciclo 2, o código passou por mais 3 rodadas da revisão adversarial real (claude → codex → qwen), que acharam e corrigiram 3 HIGH a mais (ver `## Advisor Ledger`); a última saiu PRONTO. Um 3º ciclo do avaliador é decisão do Roberto (`[D4 · limite de tentativas]`).

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F10_REVISAO_20261031.md`; as 19 notas no Advisor Ledger do DESIGN v1.1 (18 APPLIED, 1 em parte).

**Revisões do build:** avaliador de contexto fresco em 2 ciclos (worktrees destacadas, sem relatório nem diff) e a revisão adversarial real do próprio mecanismo: AT-040 sobre `7ecbc78` e o loop final de 3 rodadas (`sdd/reports/evidence/F10_REVISAO/ledger-review.md`), custo total das 4 execuções ≈ US$ 9,57 (US$ 9,37 nominais da assinatura do Claude e US$ 0,20 de OpenRouter).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | real AT-040 | `--conferir` aceitava revisão só de `--paths` | MEDIUM | APPLIED | `test_r1_conferir_recusa_revisao_so_de_paths_e_o_padrao_a_pula`; `6f4ee5b` |
| 2 | real AT-040 | `--conferir` aceitava revisão rasa | MEDIUM | APPLIED | `test_r2_conferir_recusa_revisao_rasa` |
| 3 | real AT-040 | caminho com acento escapava dos gatilhos | MEDIUM | APPLIED | nomes por `git diff --name-only -z`; `test_r3_…` |
| 4 | real AT-040 | segundos incluíam esperas; 68 gravava jsonl; achado não textual; custo 0,0000; testes depois do `main()` | LOW | APPLIED | `test_r4_…`–`test_r7_…`; `6f4ee5b` |
| 5 | ciclo 1 | 2º revisor/desempate sem engine efetiva → `loop` PRONTO | HIGH | APPLIED | `test_1_segundo_revisor_sem_cli_bloqueia_o_loop_d3`; `9846919` |
| 6 | ciclo 1 | custo todo desconhecido = 0; `diff.context`; `docs_sdd` com BRAINSTORM cortado; diversidade sem auditoria | LOW | APPLIED | `AvaliadorCiclo1`; `9846919` |
| 7 | ciclo 2 | índice copiado sem mtime perdia a checagem "racy" | MEDIUM | APPLIED | `copy2`; teste determinístico (`55a866d`); sabotagem |
| 8 | ciclo 2 | `orderFile`/textconv; lista esgotada sem fallback; dispensa sem motivo; comentário do slot | LOW | APPLIED | `AvaliadorCiclo2`, `test_dispensa_sem_motivo_nao_vale`; `486ed2e` |
| 9 | rodada 1 | auditoria parcial aceita (R1@codex) | HIGH | APPLIED | 68 sem veredito para algum achado; `test_r1_codex_auditoria_parcial_e_68`; `1975e7c` |
| 10 | rodada 1 | `--revisor2` contornava a exclusão (R2@codex) | HIGH | APPLIED | identidade = adapter + modelo; `test_r2_codex_…` |
| 11 | rodada 1 | 6 MED e 4 LOW (identidade, candidatos, diff, custo, NOVO, aviso) | MEDIUM | APPLIED | `RevisaoFinal`; ledger `rodada=1` |
| 12 | rodada 1 | N2 `layers.sql` "fixo"; `core.autocrlf` | MEDIUM | REBUTTED | `layers.sql` já entra quando o slot tem valor; `autocrlf` é do checkout (ledger) |
| 13 | rodada 2 | linha com crases e conteúdo sumia do bloco (R1@codex) | HIGH | APPLIED | `test_r1_codex_linha_com_crases_e_conteudo_e_68_e_cerca_sozinha_passa`; `248301d` |
| 14 | rodada 2 | 5 MED e 1 LOW (sinais `401`, `git add -N`, 2º revisor, HTTP sem corpo, custo acumulado, `killpg`) | MEDIUM | APPLIED | `RevisaoRodada2`, `test_openrouter_401_sem_corpo_e_auth` |
| 15 | rodada 3 | `--no-revisor2` com gatilho aceito sem motivo no ledger (R1@claude; o auditor discordou) | MEDIUM | REBUTTED (adiado para a F11) | é escolha explícita registrada no META (`dispensado por --no-revisor2`); exigir motivo é endurecimento a decidir na F11 |
| 16 | rodada 3 | seleção automática exclui o adapter inteiro (R1@codex) | MEDIUM | REBUTTED | Decision 6: o 2º revisor automático prefere outra engine; outro modelo do mesmo adapter continua possível por `--revisor2` |
| 17 | rodada 3 | tarifa do modelo configurado quando o reportado não tem preço (R2@codex); custo de tentativas sem custo conhecido não sinalizado (R3@codex) | MEDIUM | REBUTTED (adiado para a F11) | estimativa marcada `≈`; transparência de tentativas a fechar com os stubs por engine da F11 |
| 18 | rodada 3 | `--conferir` pega pasta sem META; `--feature` sem nenhum doc não avisa; gemini com mais de um modelo | LOW | REBUTTED (adiado para a F11) | sem efeito na release (a pasta sem META não confere e a release pergunta D3); ficam como pendência |

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | O `gemini` desta máquina não autentica (`ProjectIdRequiredError`) | Drift 1; prova real com `claude`, `codex` e `openrouter` | nenhum no produto |
| 2 | 22 `ResourceWarning` de socket no 1º gate | `server_close` nos servidores HTTP de teste | zero avisos desde `6f4ee5b` |
| 3 | `test_3`/teste do índice "racy" instáveis por relógio de 1 s | arquivo nascido 100 s no passado; 5/5 verde e 5/5 vermelho sob sabotagem | `55a866d` |
| 4 | Log de escopo terminava em `wc` | refeito sem formatador no fim | `escopo.log` |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Identidade de engine passou de id para adapter + modelo | aplicado como achado HIGH da revisão real | `openrouter` e `openrouter:<mesmo modelo>` escapavam da exclusão | DESIGN Decision 2 lido como "id ou adapter + modelo" |
| Auditoria parcial vira 68 | aplicado como achado HIGH | plano 8.1 R2: "exit 68 se faltar veredito" | AT-012 ganha o caso |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (86/86)
- [x] Incremental verification recorded (6 baselines, 16 grupos por AT)
- [x] Verify Gate green (`verify-gate-248301d.log`, 853 testes)
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified (41/41; AT-040 por execução real paga)
- [x] LLM prompt receipts complete (LP-001–LP-003)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo; 7 da rodada 3 adiados para a F11)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [ ] 3º ciclo do avaliador: pergunta `[D4 · limite de tentativas]` ao Roberto
- [ ] Release `v2.3.0`: OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
