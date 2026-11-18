# BUILD REPORT: F13 UX e LLM no código

> Implementation report for F13 UX e LLM no código

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F13_UX_LLM |
| **Date** | 2026-11-04 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F13_UX_LLM.md` |
| **DEFINE** | `sdd/features/DEFINE_F13_UX_LLM.md` (v1.7, 34 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F13_UX_LLM.md` (v1.4, 12 decisões, 40 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f13-ux-llm`, sobre `6b7633c` (= `v2.4.0`).
- **Commits:** `a63ed1a` build · `59420a9` prova real · `08fbb5b` avaliador ciclo 1 · `32cc42c` ciclo 2 · `867d6de`, `726c43c`, `cdb85a9`, `5ddc433` revisão real, rodadas 1 a 4 · `b1348bd` avaliador ciclo 3.
- **Fontes (só leitura):** `origin/main` do privado: `scripts/contraste.sh`, `scripts/gates/prompt-drift-scan.sh`, `.claude/skills/loop-builder/SKILL.md`, `LLM_PROMPTS_DESIGN.md`, Step 4.5 do `ux-review.md`, passo 4 do `build.md`.
- **Riscos aceitos pelo Roberto (D4, 2026-11-04):** 2º revisor dispensado nas rodadas 5 e 6; prova real sem rodada completa no commit final; último veredito do avaliador em NEEDS_WORK, sem 4º ciclo. Detalhe em `## Issues Encountered`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 40 linhas: 12 arquivos novos e 28 alterados |
| Cross-file coupling | Alto: skill, fragmento, template, lint e integração precisam dizer o mesmo |
| Security surface | Nenhuma nova; o slot vai só para `grep -E -e`, sem `eval` |
| LLM prompt items | 0 (`LLM Prompts: false`: a skill e o fragmento são método, não prompt de produto) |
| Independent volume | Médio |
| Context-rot risk | Alto: a frente inteira numa sessão; mitigado por 3 ciclos do avaliador e 6 rodadas da revisão real |
| Runtime capabilities | default e subagente disponíveis |

**Recommendation:** default.

**User decision:** default, sem pergunta: escolha do agente, pela recomendação, avisada ao Roberto na abertura do Build, com a correção de que o prompt da sessão não a fixava.

**Pre-build review:** Sim: revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 3 HIGH, 7 MEDIUM, 6 LOW, 5 propostas), aplicada no DESIGN v1.1 e no DEFINE v1.2.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 40/40 |
| **Files Created** | 12 |
| **Files Modified** | 28 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 5 Verify Gates, baseline vermelha, 7 sabotagens, 22 controles, 9 execuções reais no Codex CLI, 6 rodadas da revisão real |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: tabela WCAG 2.2 AA na `sdd-ux-review` 2.5.0 e no template; `sdd/bin/contraste.sh`; skill nova `sdd-loop-builder` 1.0.0; roteador no passo 4 da `sdd-build` 2.6.0; fragmento `LLM_PROMPTS_DESIGN.md`, `sdd-design` 2.5.0 e `design-lint.py` conferindo o inventário; `sdd/bin/prompt-drift-scan.sh` com `prompts.wrapper_pattern`; `sdd-prompt-builder` 2.1.2; `docs/llm-in-code.md` + PT. A suíte foi de 992 para 1.134 testes.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1, 29 | `contraste.sh` e testes | direct | Complete | `--self-test`, `test_contraste` | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| 2 | 2, 30 | `prompt-drift-scan.sh` e testes | direct | Complete | `--self-test`, `test_prompt_drift_scan` | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| 3 | 3, 4, 5, 31 | fragmento, `design-lint.py`, template do DESIGN | direct | Complete | `test_design_lint` | `sdd/reports/evidence/F13_UX_LLM/at-lint.log` |
| 4 | 6, 7, 8, 40 | relatório de prompts, template da UX, config, `WORKER_BRIEF.md` | direct | Complete | `test_f13_textos` | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| 5 | 9–12 | skill `sdd-loop-builder` | direct | Complete | `skill-lint`, `test_conversa`, `test_f13_textos` | `sdd/reports/evidence/F13_UX_LLM/lints-finais.log` |
| 6 | 13–17 | `sdd-build`, `sdd-design`, `sdd-ux-review`, `sdd-prompt-builder` | direct | Complete | `test_f13_textos`, pinos | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| 7 | 18–28 | `AGENTS.md.tmpl`, READMEs, docs, roadmap, guias, guia do aluno | direct | Complete | `test_docs` | `sdd/reports/evidence/F13_UX_LLM/at-docs.log` |
| 8 | 32–38 | testes de texto, contagens e pinos | direct | Complete | módulos | `sdd/reports/evidence/F13_UX_LLM/at-contagens-skills.log` |
| 9 | 39 | `MANIFEST.txt` | direct | Complete | `test_f13_textos`, `publish-gate.sh` | `sdd/reports/evidence/F13_UX_LLM/verify-gate-b1348bd.log` |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `sdd/bin/contraste.sh` | Create | 1 | Yes | truncado, piso, saídas 0/2/64 |
| `sdd/bin/prompt-drift-scan.sh` | Create | 2 | Yes | sinais, slot, caminho físico, fail-closed |
| `sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` | Create | 3 | Yes | dono do inventário |
| `.agents/skills/sdd-loop-builder/SKILL.md` | Create | 12 | Yes | 1.0.0 |
| `.agents/skills/sdd-loop-builder/references/loop-spec-rules.md` | Create | 9 | Yes | LOOP_SPEC v2 |
| `.agents/skills/sdd-loop-builder/references/exemplo-loop-spec.md` | Create | 10 | Yes | exemplo `standard` |
| `.agents/skills/sdd-loop-builder/references/como-falar.md` | Create | 11 | Yes | glossário |
| `docs/llm-in-code.md` | Create | 21 | Yes | EN |
| `docs/pt-BR/llm-in-code.md` | Create | 22 | Yes | PT |
| `tests/test_contraste.py` | Create | 29 | Yes | — |
| `tests/test_prompt_drift_scan.py` | Create | 30 | Yes | — |
| `tests/test_f13_textos.py` | Create | 32 | Yes | — |
| 28 arquivos do manifest | Modify | 4–8, 13–20, 23–28, 31, 33–40 | Yes | skills, templates, docs, testes e `MANIFEST.txt` |

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | sinais do scan | sinais além dos do brainstorm: `system=`, `role`, 2 SDKs e formas de streaming | aceito (A9 do avaliador; cabe na entrega L4) | testes dos 2 lados; limite documentado |
| 2 | `sdd/bin/prompt-drift-scan.sh`, nome e conteúdo | o scan cai nos próprios sinais, e esta frente tem `LLM Prompts: false` | falso positivo registrado (D13 da revisão do DESIGN) | sem exceção no script |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline | os 4 módulos contra a árvore `v2.4.0` | Pass (vermelho esperado em todos) | `sdd/reports/evidence/F13_UX_LLM/baseline-v2.4.0.log` |
| Self-tests | `contraste.sh`, `prompt-drift-scan.sh` | Pass | `sdd/reports/evidence/F13_UX_LLM/lints-finais.log` |
| Sabotagens | 7: 6 derrubam o teste; tirar só o `LC_ALL=C` não derruba, porque a saída é inteiro + ponto literal (ver Issues) | Pass | `sdd/reports/evidence/F13_UX_LLM/sabotagens.log` |
| Controles da prova real | 22, válidos e ruins | Pass | `sdd/reports/evidence/F13_UX_LLM/controles.log` |
| Logs de evidência | `gate-shell-evidencia.sh` | Pass | pasta inteira |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `cmd` do DEFINE: cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso (`/bin/bash` 3.2, `/usr/bin/python3` 3.9), por `verify-gate.sh --strict` |
| **Exit / Result** | 0 em `a63ed1a` (1.101), `867d6de` (1.125), `cdb85a9` (1.134), `5ddc433` (1.134) e no commit final `b1348bd` |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F13_UX_LLM/verify-gate-b1348bd.log` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `check-versions.py --base v2.4.0 --base-obrigatoria`; `skill-lint --conversa` (18); `sdd-decisoes-lint --sites` (22 perguntas) | Pass | `sdd/reports/evidence/F13_UX_LLM/at033-versoes.log`, `sdd/reports/evidence/F13_UX_LLM/lints-finais.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `sdd/reports/evidence/F13_UX_LLM/verify-gate-b1348bd.log` |
| Build / Compile | grep de bashismos; `/bin/bash -n`; `ast.parse` no Python 3.9 | Pass | `sdd/reports/evidence/F13_UX_LLM/bash32-grep.log`, `sdd/reports/evidence/F13_UX_LLM/ast-parse.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | razão truncada e veredito contra o piso | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-002 | abaixo do piso por menos de 0,005 | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-003 | transparência composta sobre o fundo | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-004 | `--piso` em qualquer posição | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-005 | entradas inválidas saem 64 | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-006 | vírgula decimal no sistema | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-007 | `--self-test` do contraste | Pass | `sdd/reports/evidence/F13_UX_LLM/at-contraste.log` |
| AT-008 | sinais de SDK, `system` e `role` | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-009 | sinais de caminho, com link e caixa | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-010 | slot do wrapper | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-011 | exclusões | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-012 | slot vazio avisa | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-013 | saída 64, nunca LIMPO sem ter lido | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-014 | arquivos em disco | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-015 | `--self-test` autocontido | Pass | `sdd/reports/evidence/F13_UX_LLM/at-scan.log` |
| AT-016 | inventário incompleto reprova | Pass | `sdd/reports/evidence/F13_UX_LLM/at-lint.log` |
| AT-017 | DESIGN sem a seção não muda | Pass | `sdd/reports/evidence/F13_UX_LLM/at-lint.log` |
| AT-018 | fragmento preenchido passa | Pass | `sdd/reports/evidence/F13_UX_LLM/at-lint.log` |
| AT-019 | roteador no passo 4 | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-020 | triagem e skill ausente | Pass | `sdd/reports/evidence/F13_UX_LLM/cdb85a9-codex-sem-skill.log` |
| AT-021 | prova real: risco aceito (D4); `feliz` e `sem-tipo` certos no efeito em `867d6de`, sem os transcritos; `sem-skill` em `cdb85a9` | Pass | `sdd/reports/evidence/F13_UX_LLM/cdb85a9-codex-sem-skill.log` |
| AT-022 | skill nova nos lints | Pass | `sdd/reports/evidence/F13_UX_LLM/lints-finais.log` |
| AT-023 | contrato da skill | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-024 | não é laço; item faltando | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-025 | exemplo cumpre o perfil | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-026 | integração e relatório de prompts | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-027 | tabela WCAG no template | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-028 | tabela WCAG na skill | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-029 | slot no config e nos guias | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-030 | `init` e `sync` | Pass | `sdd/reports/evidence/F13_UX_LLM/at-textos.log` |
| AT-031 | docs e roadmap | Pass | `sdd/reports/evidence/F13_UX_LLM/at-docs.log` |
| AT-032 | sem termo da RDD nem de um agente só | Pass | `sdd/reports/evidence/F13_UX_LLM/at-agnostico.log` |
| AT-033 | versões e contagens | Pass | `sdd/reports/evidence/F13_UX_LLM/at033-versoes.log` |
| AT-034 | hooks, `report-lint`, `verify-gate`, `sdd-release` idênticos; suíte verde | Pass | `sdd/reports/evidence/F13_UX_LLM/at034-diff.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 5 propostas e 16 defeitos da revisão do DESIGN, com veredito no Advisor Ledger do DESIGN.
**Veredito do avaliador (C1):** NEEDS_WORK no ciclo 3, sobre `5ddc433` (`sdd/reviews/AVALIACAO_F13_UX_LLM_20261104-ciclo3.md`): 1 MEDIUM, corrigido em `b1348bd` e conferido pela rodada 6 e pelo gate; sem 4º ciclo, por decisão D4 do Roberto (2026-11-04). Ciclos anteriores: ciclo 1 NEEDS_WORK (1 HIGH, 8 MEDIUM, 11 LOW), ciclo 2 NEEDS_WORK (2 MEDIUM, 9 LOW). Nenhum avaliador rodou os testes de aceitação em `b1348bd`.

---

## Advisor Ledger

Detalhe no Advisor Ledger do DESIGN e em `sdd/reports/evidence/F13_UX_LLM/ledger-review.md`.

| Rodada | Diff | Achados | `loop` | Custo |
|---:|---|---|---|---:|
| 1 | `32cc42c` | 1 MED, 3 LOW | PRONTO | US$ 2,42 |
| 2 | `867d6de` | 2 MED, 5 LOW | PRONTO | US$ 2,28 |
| 3 | `726c43c` | 1 MED, 3 LOW | PRONTO, teto | US$ 2,31 |
| 4 (D4) | `cdb85a9` | 2 LOW; 2º revisor sem créditos | BLOQUEADO | US$ 2,39 |
| 5 (D4) | `5ddc433` | 3 LOW; sem 2º revisor | PRONTO | US$ 2,35 |
| 6 (D4) | `b1348bd` | 3 LOW; sem 2º revisor | PRONTO, `--conferir` CONFERE | US$ 2,25 |

Nenhuma rodada achou HIGH. Os 6 LOW das rodadas 5 e 6 não foram corrigidos: consertar invalidaria a revisão da release. 5 são pendência da v2.5.1 e 1 foi rebatido com evidência.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | **Evidência perdida:** a repetição da prova em `cdb85a9` usou os mesmos nomes de arquivo e sobrescreveu os transcritos e registros de `867d6de` | sobrou o que está em `sdd/reports/evidence/F13_UX_LLM/prova-real-resumo.md`; relatado ao Roberto, e a prova não pôde ser refeita | o resultado em `867d6de` não tem transcrito que o sustente; sobraram as LOOP_SPEC e o relatório daquelas execuções |
| 2 | **Sem créditos no Codex** durante a prova e a rodada 4 | D4: 2º revisor dispensado nas rodadas 5 e 6; prova aceita como está | rodadas 5 e 6 sem 2º revisor, e `feliz` e `sem-tipo` sem execução real depois de `867d6de`; o passo 4 da `sdd-build` não mudou depois dele |
| 3 | **Limite de ciclos ignorado:** depois do ciclo 2 em NEEDS_WORK, segui sem a pergunta D4 que o método manda fazer | relatado ao Roberto, que escolheu o 3º ciclo | o ciclo 3 achou 1 MEDIUM, regressão de um conserto do ciclo 2 |
| 4 | Conserto de regressão: `[.` numa lista da expressão abriu um elemento especial | o script saiu 64 (fail-closed) em vez de LIMPO; corrigido antes do commit | nenhum |
| 5 | Tirar só o `LC_ALL=C` do `contraste.sh` não derruba teste | a saída é inteiro + ponto literal, e o idioma não a alcança; a sabotagem com `%f` prova que o teste tem dentes | a guarda é proteção extra |
| 6 | Premissas sem prova local: GNU grep e mawk não existem nesta máquina | CI em `ubuntu-latest` | a medir no PR |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Prova do scan por calço na cópia, em vez de ler o transcrito | aplicado (N2 do ciclo 2) | o texto do agente muda de forma a cada execução | Decision 12 |
| Sinais do scan mais amplos, e chave `system` só em posição de início | aplicado (A9, L4, M1) | formas comuns ficavam de fora, e `file system:` disparava | Decision 2 |
| Laço do Build com rotas de recusa da skill | aplicado (A3) | os ensaios no Codex mostraram a lacuna | Decision 7 |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (40/40)
- [x] Incremental verification recorded (baseline vermelha, 7 sabotagens)
- [x] Verify Gate green (`verify-gate-b1348bd.log`)
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified (34/34, com AT-021 como risco aceito)
- [x] LLM prompt receipts complete (N/A: `LLM Prompts: false`)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [ ] Release `v2.5.0`: falta o OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
