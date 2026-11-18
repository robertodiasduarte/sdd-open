# BUILD REPORT: F11 Revisão adversarial — gate offline

> Implementation report for F11 Revisão adversarial — gate offline

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F11_GATE |
| **Date** | 2026-11-01 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F10_REVISAO.md` (parte F11) |
| **DEFINE** | `sdd/features/DEFINE_F11_GATE.md` (v1.1, 27 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F11_GATE.md` (v1.1, 6 decisões, 34 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f11-gate`, sobre `248301d` (= `v2.3.0`).
- **Commits:** `84cf6b5` build · `468d605` eval-agree pela engine base · `a9813ff` avaliador ciclo 1 · `06e5a9d` avaliador ciclo 2 · `ab2f252` revisão real, rodada 1 · `9508ff0` rodada 2. Escopo: `sdd/reports/evidence/F11_GATE/escopo.log` (39 arquivos: 22 novos, 17 alterados).
- **Fontes (só leitura):** `origin/main` do privado: `scripts/adversarial-review-gate.sh` (695 l.), `scripts/adversarial-review/eval-agree.sh` (207 l.) e `stubs/` — lidos como contrato, nada copiado; o privado não foi alterado.
- **Revisões:** do DESIGN (`sdd/reviews/REVISAO_DESIGN_F11_GATE_20261101.md`, 12 notas no DESIGN v1.1/DEFINE v1.1); do build, ver `## Contrato de aceite (C2) e avaliador de contexto fresco (C1)` e `## Advisor Ledger`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 34 linhas (22 arquivos novos, 17 alterados ao fim, com o `auditor-misto.md` e a 5ª fixture do eval acrescentados no build) |
| Cross-file coupling | Médio: o gate lê o META de `adversarial-review.sh`, o registry, o `precos.tsv` e a tabela dos stubs |
| Security surface | Chave de API (falsa e gerada no gate; nunca em arquivo); isolamento de rede e do repositório do usuário |
| LLM prompt items | 0 (`LLM Prompts: false`: os stubs devolvem respostas fixas; os 3 prompts da F10 não mudam) |
| Independent volume | Médio: 1 gate + 1 eval + 5 stubs + 6 correções pontuais |
| Context-rot risk | Alto: release da F10 e F11 inteira na mesma sessão; mitigado pelas revisões de contexto fresco e pela revisão real |
| Runtime capabilities | default e subagente disponíveis |

**Recommendation:** default.

**User decision:** default — o Roberto pediu "comece f11" depois da release da F10, no mesmo encadeamento (define, design, revisão do design, build, revisão do build) que ele pediu para a F10; o modo foi registrado, não perguntado.

**Pre-build review:** Sim — revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 2 HIGH, 3 MEDIUM, 7 LOW), aplicada no DESIGN v1.1 e no DEFINE v1.1 antes do código.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 34/34 |
| **Files Created** | 22 |
| **Files Modified** | 17 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 5 Verify Gates, 6 baselines vermelhas, 11 sabotagens no gate, 3 revisões reais |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: `sdd/bin/adversarial-review-gate.sh` (bash 3.2 + núcleo Python 3.9; 103 asserções em ~7 s, exits 0/2/3/64); `sdd/review/stubs/` (um stub por engine — claude JSON, codex JSONL, gemini JSON, OpenRouter HTTP local —, `comum.py`, `cenarios.tsv` e 4 respostas); `sdd/bin/eval-agree.sh` (taxa de AGREE por auditor nas revisões já feitas); os 6 achados adiados da F10 em `adversarial-review.sh` e `adapters/gemini.sh`; teto de 30 min no `testes-macos`; docs EN/PT; a revisão adversarial sai do roadmap. Testes: 853 → 894 no piso.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 12–13, 22–23 | 6 achados adiados (#15, #17, #18) | direct | Complete | `test_revisao.F11Adiados`, `test_revisao_adapters` | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| 2 | 1–9 | stubs por engine, tabela e respostas | direct | Complete | o gate | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| 3 | 10, 20 | gate offline e seus testes | direct | Complete | `test_revisao_gate` | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| 4 | 11, 14–19, 21 | eval-agree, fixtures e testes | direct | Complete | `test_eval_agree` | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| 5 | 24–26 | teto do macOS na CI | direct | Complete | `test_release_workflow` | `sdd/reports/evidence/F11_GATE/teste-contratos.log` |
| 6 | 27–33 | docs, roadmap, init | direct | Complete | `test_docs`, `test_sdd_open` | `sdd/reports/evidence/F11_GATE/teste-contratos.log` |
| 7 | 34 | `MANIFEST.txt` | direct | Complete | suíte (`test_correcoes_w0`) | `sdd/reports/evidence/F11_GATE/verify-gate-final.log` |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `sdd/bin/adversarial-review-gate.sh` | Create | 10 | Yes | pré-voo (stubs, cenários, registry, PATH num bash filho, servidor), isolamento, anel, contrato, privacidade |
| `sdd/bin/eval-agree.sh` | Create | 11 | Yes | só lê arquivos; agrupa por engine base + modelo principal |
| `sdd/review/stubs/comum.py`, `claude.py`, `codex.py`, `gemini.py`, `openrouter.py`, `cenarios.tsv`, `respostas/*.md` (4) | Create | 1–9 | Yes | um stub por engine; falhas marcadas `sintético` |
| `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000001` a `-000005` (8 arquivos) | Create | 14–19 | Yes | a 5ª pasta (id com slug, outro provedor) entrou no build |
| `sdd/bin/adversarial-review.sh` | Modify | 12 | Yes | #15, #17a, #17b, #18a, #18b |
| `sdd/bin/adapters/gemini.sh` | Modify | 13 | Yes | #18c |
| `tests/test_revisao_gate.py`, `tests/test_eval_agree.py` | Create | 20–21 | Yes | 23 + 9 testes |
| `tests/test_revisao.py`, `tests/test_revisao_adapters.py`, `tests/test_release_workflow.py`, `tests/test_docs.py`, `tests/test_sdd_open.py` | Modify | 22–23, 26, 32–33 | Yes | `Custo.test_quatro_formas`: a tarifa passa a ser a do modelo reportado (AT-019) |
| `.github/workflows/release.yml`, `.github/workflows/publish-gate.yml` | Modify | 24–25 | Yes | `testes-macos` 30 min |
| `docs/adversarial-review.md` + PT, `docs/cli-conventions.md`, `docs/roadmap.md` + PT, `README.md`, `README.pt-BR.md` | Modify | 27–31 | Yes | gate offline e eval-agree; linha do roadmap removida |
| `MANIFEST.txt` | Modify | 34 | Yes | 331 → 353 |

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `sdd/review/stubs/respostas/auditor-misto.md` | arquivo fora do manifest v1.1 | aceito (achado M1 do avaliador, ciclo 1) | o gate confere DISAGREE_EVIDENCE, DISAGREE_CONCERN e NOVO |
| 2 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000005/` | 5ª pasta de fixture | aceito (LOW 4 da revisão do DESIGN) | prova que slug e provedor não partem o auditor |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline dos achados adiados | testes F11Adiados contra o código da v2.3.0 | Pass (6 vermelhos esperados) | `sdd/reports/evidence/F11_GATE/baseline-adiados.log` |
| Baseline da F11 inteira | testes novos e alterados na árvore `v2.3.0` | Pass (vermelho esperado em todos os grupos) | `sdd/reports/evidence/F11_GATE/baseline.log` |
| Baselines das correções | cada teste novo contra o commit anterior | Pass (vermelho esperado) | `baseline-aval1.log`, `baseline-aval1-eval.log`, `baseline-aval2.log`, `baseline-real1.log`, `baseline-real2.log` |
| Gate e sabotagens | `test_revisao_gate` (23 testes: 6 sabotagens do DEFINE, extração nula das 4 engines, credencial das 4, parser só-AGREE, severidade do NOVO, custo pelo modelUsage) | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| Logs de evidência | `gate-shell-evidencia.sh sdd/reports/evidence/F11_GATE` | Pass | pasta inteira (6 logs de sondas que terminavam num formatador viraram `.sonda.txt`, com nota) |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `cmd` do DEFINE: cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso (`/bin/bash` 3.2, `/usr/bin/python3` 3.9) |
| **Exit / Result** | 0 em `84cf6b5` (881), `a9813ff` (886), `06e5a9d` (888) e `9508ff0` (894, final) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F11_GATE/verify-gate-final.log` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `check-versions.py --base v2.3.0 --base-obrigatoria` (nenhuma skill tocada) | Pass | `sdd/reports/evidence/F11_GATE/check-versions.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `sdd/reports/evidence/F11_GATE/verify-gate-final.log` |
| Build / Compile | grep de bashismos nos 2 scripts novos; `bash -n`; `py_compile` dos stubs | Pass | `sdd/reports/evidence/F11_GATE/bash32-grep.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | gate ponta a ponta, uma linha por asserção, RESULTADO + → | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-002 | campos que discriminam por engine; ≈US$ calculado | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-003 | vereditos do auditor, inclusive DISAGREE e NOVO | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-004 | auditor sem bloco → 68 | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-005 | mesma identidade → 67; fallback para a do auditor → 67 | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-006 | credencial → 65 nas 4 engines, sem troca | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-007 | 429 → 2 chamadas na mesma engine (CLI e HTTP) | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-008 | cota → próxima da lista, META com fallback | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-009 | sentinela vazia e chamadas exatas por cenário | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-010 | proxies mortos, Bearer gerado, deny, chave fora dos arquivos | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-011 | sem isolamento → 3 antes de qualquer chamada; BASH_ENV, função exportada e GIT_DIR herdado neutralizados | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-012 | todas as asserções rodam; exit 2 | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-013 | `-v` mostra o valor lido | Pass | `sdd/reports/evidence/F11_GATE/gate-v.log` |
| AT-014 | tabela por auditor com os números da fixture | Pass | `sdd/reports/evidence/F11_GATE/eval-agree-fixture.log` |
| AT-015 | fora da conta, com o motivo | Pass | `sdd/reports/evidence/F11_GATE/eval-agree-fixture.log` |
| AT-016 | sem dados → 2; uso → 64 | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-017 | sem engine, sem rede | Pass | `sdd/reports/evidence/F11_GATE/verde-real2.log` |
| AT-018 | `--no-revisor2` com gatilho exige motivo no `--conferir` | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-019 | modelo reportado sem preço → `$?` | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-020 | tentativa que estourou o teto → `+ $?`; recusa não marca | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-021 | `--conferir` pula pasta sem META | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-022 | `--feature` sem documento avisa | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-023 | gemini com 2 modelos soma os tokens | Pass | `sdd/reports/evidence/F11_GATE/verde-adiados.log` |
| AT-024 | testes da F10 continuam, exceto o AT-019 | Pass | `sdd/reports/evidence/F11_GATE/verify-gate-final.log` |
| AT-025 | `testes-macos` com 30 min | Pass | `sdd/reports/evidence/F11_GATE/teste-contratos.log` |
| AT-026 | docs do gate e do eval-agree; roadmap sem a linha | Pass | `sdd/reports/evidence/F11_GATE/teste-contratos.log` |
| AT-027 | MANIFEST, grep bash 3.2, init leva os stubs | Pass | `sdd/reports/evidence/F11_GATE/teste-contratos.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 12 notas da revisão do DESIGN, aplicadas no DESIGN v1.1 e no DEFINE v1.1 (Advisor Ledger do DESIGN).
**Veredito do avaliador (C1):** NEEDS_WORK · ciclos: 2 · achados: 5 (ciclo 1: 1 MEDIUM, 4 LOW) + 2 (ciclo 2: 1 HIGH, 1 LOW) · `sdd/reviews/AVALIACAO_F11_GATE_20261101-ciclo2.md`

Os 7 achados foram aplicados (`a9813ff`, `06e5a9d`), cada um com teste vermelho no commit anterior (`baseline-aval1.log`, `baseline-aval1-eval.log`, `baseline-aval2.log`). O HIGH do ciclo 2 — o gate herdava `GIT_DIR` de um hook numa worktree e commitava no repositório do usuário — tem teste que monta exatamente esse cenário. Depois do ciclo 2, o código passou por 3 rodadas da revisão adversarial real, que não acharam HIGH; a última saiu PRONTO e é a revisão da release.

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F11_GATE_20261101.md`; as 12 notas no Advisor Ledger do DESIGN v1.1 (11 APPLIED, 1 em parte).

**Revisões do build:** avaliador de contexto fresco em 2 ciclos e a revisão adversarial real (claude → codex como 2º revisor → openrouter:qwen/qwen3.7-plus) em 3 rodadas (`sdd/reports/evidence/F11_GATE/ledger-review.md`); custo das 3 rodadas US$ 3,48 (US$ 3,40 nominais da assinatura do Claude e US$ 0,08 de OpenRouter).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | ciclo 1 | o gate não conferia DISAGREE nem NOVO | MEDIUM | APPLIED | `auditor-misto.md`; `test_aval1_m1_parser_que_so_aceita_agree_e_pego`; `a9813ff` |
| 2 | ciclo 1 | custo do claude igual em total e por modelo; credencial só no claude; eval-agree sem pasta = 64; sem git = traceback | LOW | APPLIED | `test_aval1_l1_…`, `test_aval1_l2_…`, `test_aval1_l3_…`, `test_aval1_l4_…`; `a9813ff` |
| 3 | ciclo 2 | o gate herdava `GIT_DIR`/`GIT_INDEX_FILE` de um hook e commitava no repositório do usuário | HIGH | APPLIED | todo `GIT_*` herdado sai, `GIT_CEILING_DIRECTORIES`, raiz conferida (exit 3); `test_aval2_h1_…`; `06e5a9d` |
| 4 | ciclo 2 | arquivo, linha e severidade do NOVO não conferidos | LOW | APPLIED | `test_aval2_l1_severidade_do_novo_e_conferida`; `06e5a9d` |
| 5 | ciclo 2 | o `init` copia as fixtures do eval | LOW | REBUTTED | comportamento do `init` desde a F1: fixtures são exemplos da 1ª instalação (`bin/sdd-open.sh:644`) |
| 6 | rodada 1 | gate rodado ~23 vezes na suíte; teto de 120 s asserido na CI; exit 3 depois de cenários; wrapper sem quoting | MEDIUM | APPLIED | `ab2f252`; ledger `rodada=1` |
| 7 | rodada 2 | servidor que não sobe dava 2; `auditor_exit` não conferido; comentário no `review:`; gemini com `+` | MEDIUM | APPLIED | `9508ff0`; ledger `rodada=2` |
| 8 | rodada 3 | agrupamento do eval-agree sem slug e pelo modelo principal (R1@claude LOW, R1@codex MED) | MEDIUM | REBUTTED | decisões registradas (DESIGN L4; rodada 2); o auditor refutou com evidência; ledger `rodada=3` |

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | `-v` do gate quebrava com valores em tupla | `"%s" % (valor,)` | encontrado pelo próprio teste antes do commit |
| 2 | 6 logs dos avaliadores terminavam num formatador | renomeados para `.sonda.txt` com nota; os ATs têm prova nos logs do build | nenhum |
| 3 | o avaliador do ciclo 1 gravou um `init-<pid>.out` na pasta temporária do sistema | registrado; não é arquivo do projeto | nenhum |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Ambiente dos filhos sem nenhum `GIT_*` herdado e com `GIT_CEILING_DIRECTORIES` | aplicado como achado HIGH do avaliador | um hook numa worktree exporta `GIT_DIR` | Decision 2 ganha a regra |
| Servidor da OpenRouter provado no pré-voo | aplicado como achado da revisão real | exit 3 só quando nada foi chamado | Decision 2 / Error Handling |
| eval-agree agrupa pela engine base e pelo modelo principal | aplicado (LOW 4 do DESIGN, `468d605`, rodada 2) | o mesmo auditor numa linha só | Decision 3 |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (34/34)
- [x] Incremental verification recorded (6 baselines vermelhas)
- [x] Verify Gate green (`verify-gate-final.log`, 894 testes)
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified (27/27)
- [x] LLM prompt receipts complete (N/A: `LLM Prompts: false`)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [ ] Release `v2.3.1`: OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
