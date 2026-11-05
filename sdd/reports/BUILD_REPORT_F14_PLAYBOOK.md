# BUILD REPORT: F14 Playbook, invariantes e sessão

> Implementation report for F14 Playbook, invariantes e sessão

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_PLAYBOOK |
| **Date** | 2026-11-05 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F14_PLAYBOOK.md` |
| **DEFINE** | `sdd/features/DEFINE_F14_PLAYBOOK.md` (v1.8, 45 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F14_PLAYBOOK.md` (v1.5, 15 decisões, 61 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f14-playbook`, sobre `b1348bd` (= `v2.5.0`).
- **Commits:** `864fd8d` build · `9b3dad1` avaliador ciclo 1 · `17dc00c` ciclo 2 · `eada1e2` ciclo 3 · `6cbfa33` revisão real, rodada 1 · `0028ea4` rodada 2 · `8a320e9` rodada 3 (commit final da entrega; a rodada 4 revisou este commit e não gerou mudança de código).
- **Fontes (só leitura):** `origin/main` do privado (`88707b37d`): `playbook-curator.sh`, `curator-playbook.md`, `release.md` (17b), `new-session.sh`, `invariants.md`, `scripts/fixtures/curator/`.
- **Entrega:** 1ª de 2 da F14, decisão do Roberto no brainstorm. A orquestração (`sdd-drive`, O2, O3, O4) é a 2ª.
- **Decisões D4 do Roberto (2026-11-05):** 3º ciclo focado do avaliador; sem 4º ciclo, seguindo para a revisão paga e a prova real; revisão real autorizada até a 4ª rodada ("pode ir para quarta", lido assim e dito a ele). O último veredito do avaliador fica NEEDS_WORK, com os achados corrigidos em `eada1e2`. Depois da rodada 4: publicar sem 5ª rodada, com os 5 achados de Claude como primeira tarefa da F14_DRIVE ("A — Publicar como está").

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 61 linhas: 24 arquivos novos e 37 alterados |
| Cross-file coupling | Alto: script, brief, passo 17b, contrato e fixtures precisam dizer o mesmo |
| Security surface | Fronteira de escrita do agente fresco; nenhuma credencial lida ou gravada |
| LLM prompt items | 0 (`LLM Prompts: false`: o brief é método, não prompt de produto) |
| Independent volume | Médio |
| Context-rot risk | Alto: mitigado por 3 ciclos do avaliador |
| Runtime capabilities | default e subagente disponíveis |

**Recommendation:** default.

**User decision:** default, sem pergunta: escolha do agente, pela recomendação.

**Pre-build review:** Sim: revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 2 HIGH, 9 MEDIUM, 6 LOW, 5 propostas), que voltou com o build já em andamento e foi aplicada antes do 1º commit (DESIGN v1.1, DEFINE v1.3).

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 61/61 |
| **Files Created** | 24 |
| **Files Modified** | 37 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 6 Verify Gates, baseline vermelha, sabotagens por commit, 3 ciclos do avaliador, revisão focada da fronteira, 4 rodadas da revisão real, 2 execuções da prova em agente de fora do Claude |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: `sdd/bin/playbook-curator.sh` (8 modos e self-test); `sdd/invariants.md`; brief do curador (`sdd-playbook` 2.2.0); passo 17b da `sdd-release` 2.7.0; `copiar-docs.sh` na `sdd-new-session` 1.4.0; molde do handoff com 6 seções (`sdd-handoff` 2.1.2); fronteira de escrita com índice, branch e `.git`, e restauração do DEFINE (`sdd-define` 2.5.1); consertos em `design-lint.py`, `prompt-drift-scan.sh`, `playbook-lint.sh` e `tests/apoio.py`; `docs/playbook-curation.md` + PT.

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|---|---|---|---|
| `playbook-curator.sh`, `copiar-docs.sh` | LM-001 | ✔ tratado | fixtures dos 2 lados; sabotagens por script; o efeito do 17b foi seguido à letra por 3 avaliadores |
| testes novos | LM-002 | ✔ tratado | baseline vermelha na `v2.5.0` |
| revisão real e `ls-files` | LM-003 | ✔ tratado | revisão roda com tudo commitado; `copiar-docs.sh` lê os não salvos por `ls-files --others` |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `heurística` `regressão` `conserto`
regra: Conserto que estreita uma heurística sobre texto livre abre o vizinho: nos ciclos 1, 2 e 3 do avaliador da F14, cada ajuste da regra que adivinhava a célula de veredito criou o defeito seguinte. **Do instead:** na 2ª regressão da mesma regra, pare de ajustar: troque a heurística por uma fonte estruturada (o cabeçalho da tabela) e recuse o que não tiver essa fonte.
evidencia: sdd/reviews/AVALIACAO_F14_PLAYBOOK_20261105-ciclo3.md
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `verify-gate` `git archive` `self-test`
regra: Script que só roda dentro de um repositório git passa no teste local e falha no gate, que roda numa cópia sem `.git`; e uma asserção de "bloqueou" que aceita qualquer exit diferente de 0 fica verde quando a ferramenta nem rodou. **Do instead:** rode o self-test novo numa cópia sem `.git` antes do gate, e confira o exit exato do que deve reprovar.
evidencia: sdd/reports/evidence/F14_PLAYBOOK/verify-gate-864fd8d.log
ficha: —
mordeu_antes: —
>>>
```

---

## Task Execution

Modo default, em 4 commits. As revisões frescas voltaram com o build em andamento; o que elas pediram foi aplicado antes do 1º commit e registrado no Advisor Ledger do DESIGN.

---

## Files Changed

Os 61 itens do File Manifest do DESIGN, mais os 2 arquivos de teste e os 3 de fixture que os consertos pediram dentro dos mesmos módulos. `MANIFEST.txt` com 439 linhas, igual a `git ls-files`.

---

## Drift Detected

| Item | Decisão | Motivo |
|---|---|---|
| `governanca-fronteira.sh`, `governanca-bloco.py`, `sdd-define`, 3 testes | manifest 54 a 59 | achados da revisão focada (Decision 12) |
| `docs/hooks.md` + PT | manifest 60, 61 | o piso do anti-collapse muda o que eles dizem |
| Modos `--preparar`, `--selar` e `--aplicar-inv` | Decisions 3, 5, 6 | revisão do DESIGN: D5, D6, D7 e D8 |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline | os 6 arquivos de teste novos contra a árvore `v2.5.0` | Pass (vermelho esperado nos 6) | `sdd/reports/evidence/F14_PLAYBOOK/baseline-9b3dad1.log` |
| Self-test | `playbook-curator.sh --self-test` | Pass | `sdd/reports/evidence/F14_PLAYBOOK/self-test-8a320e9.log` |
| Colheita | os 4 tipos de linha sobre as fixtures | Pass | `sdd/reports/evidence/F14_PLAYBOOK/colher-fixtures-8a320e9.log` |
| Sabotagens | 27 no commit final: 26 derrubam teste; 1 viva conhecida, com o teste que a derruba guardado para a F14_DRIVE (`sdd/reports/evidence/F14_PLAYBOOK/pendencia-r5-teste-lado2.patch`) | Pass | `sdd/reports/evidence/F14_PLAYBOOK/sabotagens-8a320e9-r2.log` |
| Tabelas reais | 30 documentos reais, 0 tabelas sem cabeçalho | Pass | `sdd/reports/evidence/F14_PLAYBOOK/tabelas-reais-8a320e9.log` |
| Logs de evidência | `gate-shell-evidencia.sh` | Pass | pasta inteira |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `cmd` do DEFINE: cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso (`/bin/bash` 3.2, `/usr/bin/python3` 3.9), por `verify-gate.sh --strict` |
| **Exit / Result** | 2 em `864fd8d` (1 falha, ver Issues), 0 em `9b3dad1` (1.356), `17dc00c` (1.372), `eada1e2` (1.382), `6cbfa33` (1.397) e no commit final `8a320e9` (1.411). `0028ea4` foi parado no meio, por ter sido superado |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `check-versions.py --base v2.5.0 --base-obrigatoria`; `skill-lint --conversa` (18); `sdd-decisoes-lint --sites` (25 perguntas) | Pass | `sdd/reports/evidence/F14_PLAYBOOK/at036-versoes-8a320e9.log`, `sdd/reports/evidence/F14_PLAYBOOK/at036-skill-lint-8a320e9.log`, `sdd/reports/evidence/F14_PLAYBOOK/at036-decisoes-8a320e9.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| Build / Compile | grep de bashismos; `/bin/bash -n` | Pass | `sdd/reports/evidence/F14_PLAYBOOK/bash32-8a320e9.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | tabela de landmines lida pelo cabeçalho | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-002 | achado com ID vira mordeu | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-003 | termo de sup vira sugestão | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-004 | candidato com evidência | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-005 | candidato rejeitado com motivo | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-006 | pergunta de promoção | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-007 | saídas e resumo da colheita | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-008 | --desde | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-009 | trace da colheita | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-010 | seções de PLAYBOOK_SECTIONS | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-011 | --aplicar válido | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-012 | --aplicar inválido, stdout vazio | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-013 | só contadores atravessa o anti-collapse | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-014 | par do pacote passa na trava | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-015 | cada defeito sai 2 | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-016 | --cruzar | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-017 | --cruzar inválido | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-018 | o ajuste do --cruzar destrava | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-019 | --colher --inv | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-020 | bloco reprovado por cada defeito | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-021 | bloco válido: AUTO e PERGUNTA | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-022 | self-test sem residuo | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-023 | brief, contrato e parada do curador | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-024 | texto do passo 17b | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-025 | pergunta D3 no como-falar | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-026 | copiar-docs, nome idêntico | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-027 | copiar-docs, o que não copia | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-028 | sdd-new-session chama o script | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-029 | molde do handoff com 6 seções | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-030 | suíte sem herdar SDD_TRACE | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-031 | design-lint: títulos e chaves | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-032 | drift scan: formas do slot | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-033 | revisão focada da fronteira | Pass | `sdd/reports/evidence/F14_PLAYBOOK/at033-8a320e9.log` |
| AT-034 | init instala as invariantes | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-035 | docs nos 2 idiomas | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-036 | piso, skill-lint, versões | Pass | `sdd/reports/evidence/F14_PLAYBOOK/bash32-8a320e9.log`, `sdd/reports/evidence/F14_PLAYBOOK/at036-skill-lint-8a320e9.log`, `sdd/reports/evidence/F14_PLAYBOOK/at036-versoes-8a320e9.log`, `sdd/reports/evidence/F14_PLAYBOOK/at036-decisoes-8a320e9.log` |
| AT-037 | gate, report-lint, revisão e hooks sem diff | Pass | `sdd/reports/evidence/F14_PLAYBOOK/at037-8a320e9.log` |
| AT-038 | prova em agente de fora do Claude: Codex CLI 0.163 com `deepseek/deepseek-v4-pro` pela OpenRouter, não o modelo da OpenAI | Pass | `sdd/reports/evidence/F14_PLAYBOOK/codex-8a320e9-r2-despacho.log`, `sdd/reports/evidence/F14_PLAYBOOK/codex-8a320e9-r2-curador.log`, `sdd/reports/evidence/F14_PLAYBOOK/codex-8a320e9-r2-resumo.log` |
| AT-039 | baseline e sabotagens | Pass | `sdd/reports/evidence/F14_PLAYBOOK/baseline-9b3dad1.log`, `sdd/reports/evidence/F14_PLAYBOOK/sabotagens-8a320e9-r2.log` |
| AT-040 | RESULTADO e seta | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-041 | --preparar | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-042 | piso do anti-collapse | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-043 | --aplicar-inv | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-044 | registro do já julgado | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |
| AT-045 | fronteira, bloco e restauração | Pass | `sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 5 propostas e 17 defeitos da revisão do DESIGN, com veredito no Advisor Ledger do DESIGN.
**Revisão adversarial real:** 4 rodadas, com revisor claude e auditor `openrouter:qwen/qwen3.7-plus`; 2º revisor codex nas rodadas 1 e 2 e `openrouter:deepseek/deepseek-v4-pro` na 4ª (a conta do Codex ficou sem créditos, conferido; na 3ª ele falhou). Ledger: `sdd/reports/evidence/F14_PLAYBOOK/ledger-review.md`. Rodada 4, sobre `8a320e9`: loop PRONTO e `--conferir` CONFERE (`sdd/reports/evidence/F14_PLAYBOOK/real-rodada4-fechamento.log`). O único HIGH da rodada 4, do DeepSeek, foi rebatido por medição, embora o auditor tenha concordado com ele: `sdd/reports/evidence/F14_PLAYBOOK/deepseek-r1-repro.log`.
**Veredito do avaliador (C1):** NEEDS_WORK no ciclo 3, sobre `17dc00c` (`sdd/reviews/AVALIACAO_F14_PLAYBOOK_20261105-ciclo3.md`): 1 HIGH, 3 MEDIUM, 7 LOW, corrigidos em `eada1e2`, sem 4º ciclo, por decisão D4 do Roberto; a conferência fica com a revisão real e a prova no Codex. Ciclos anteriores: `sdd/reviews/AVALIACAO_F14_PLAYBOOK_20261105-ciclo1.md`, `sdd/reviews/AVALIACAO_F14_PLAYBOOK_20261105-ciclo2.md`.

---

## Advisor Ledger

Ver o Advisor Ledger de `sdd/features/DESIGN_F14_PLAYBOOK.md` (v1.5): revisão do DESIGN, revisão da fronteira e os 3 ciclos do avaliador, item por item.

Ficam como pendência, com motivo: F5, F6, F7 e a guarda de F9 (fronteira); L7, L10, N-L9, N-L10, resto de N-L11, N3-L4; R1 a R5 da rodada 4, por decisão D4 do Roberto, como primeira tarefa da F14_DRIVE.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | **Gate vermelho em `864fd8d`:** o self-test chamava o `playbook-lint.sh`, que exige git, e o gate roda numa cópia sem `.git`; o mesmo caso escondia um falso verde (aceitar qualquer exit como "bloqueou") | self-test com repositório temporário; exit exato; teste numa cópia sem `.git` | nenhum depois do conserto |
| 2 | **2 regressões seguidas na mesma regra:** o conserto de L1 criou N-H1, e o de N-H1 criou N3-H1 | a heurística virou leitura pelo cabeçalho; tabela sem as colunas não conta e é relatada | a reação foi trocar a causa; ninguém de fora conferiu ainda, além da revisão real |
| 3 | **`git add .` por engano** antes do 1º commit: os artefatos de `sdd/` entraram no índice | `git reset -q`, sem commit; `git add` por lista, conferida | nenhum; relatado ao Roberto na hora |
| 4 | **Guarda do avaliador em exit 1**, com o despacho na mesma leva: 101 arquivos, todos artefatos que a regra do projeto deixa fora do commit | registrado em `sdd/reports/evidence/F14_PLAYBOOK/guard-avaliador-864fd8d.log`; o avaliador foi proibido de restaurar arquivo | a guarda não distingue esses artefatos; pendência para a 2ª entrega |
| 5 | **`rc=0` do Codex lido como crédito reposto:** era o processo encerrado esperando entrada | conferido com o stdin fechado: seguia sem créditos | nenhum |
| 6 | **Sem créditos no Codex** no início da sessão e de novo a partir da rodada 3 | medido que o CLI roda com modelo via OpenRouter; o Roberto repôs os créditos, que serviram às rodadas 1 e 2 | a rodada 4 e a prova usam `deepseek/deepseek-v4-pro` pela OpenRouter: é o CLI do Codex, não o modelo da OpenAI |
| 8 | **Conserto que reabriu a regra:** o R6 da rodada 3 criou o R3 da rodada 4 (a seta esconde o PARECIDO quando há IGNORADO) | pendência da F14_DRIVE, por decisão D4 | caso raro; a linha PARECIDO continua saindo |
| 9 | **HIGH falso com auditor de acordo:** o DeepSeek disse que `ls-files --others` não lista ignorado, e o auditor concordou sem medir | medido num repositório real; a correção proposta daria `fatal` | quem decide é a medição; o caso vai ao bloco de OK |
| 10 | **Prova do AT-038, 1ª execução (`codex-8a320e9-*`):** o curador devolveu crases escapadas e o conferidor reprovou o bloco, como devia; na retomada, o agente redespachou sozinho e o bloco novo passou. 2 reprovações eram do critério da prova, não do agente | critério do despacho trocado por leitura do bloco `exec`, com controles dos 2 lados; prova repetida com outro nome (`codex-8a320e9-r2-*`), sem apagar a 1ª | as 3 cláusulas do AT-038 passam na 2ª execução, com o bloco aprovado na 1ª tentativa dela |
| 11 | **Commit da retomada NÃO PROVADO neste agente:** o sandbox `workspace-write` do Codex deixa `.git` só leitura. Nas 2 execuções, o agente aplicou o que devia, parou no commit e, na 2ª, entregou os comandos à pessoa. O resumo da 2ª sai `exit=1` por isso, e "o commit leva o playbook" lá é ✅ vazio: olhou o commit base | o AT-038 não pede commit; fica declarado, sem contar como passou | o commit do item 8 do 17b não foi visto rodar fora do Claude |
| 7 | **Log do avaliador colhido como achado:** `AVAL2-V2-aposentar-e-bordas.log:40` gera contagem falsa na colheita real desta feature | pendência L10; na curadoria da F14, essa linha leva DESCARTAR | a conferir na curadoria |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Decision 2: a tabela passa a ser lida pelo cabeçalho | aplicado (N3-H1) | adivinhar a célula regrediu 2 vezes | tabela sem as colunas não conta |
| Decision 6: sugestão confirmada vira pergunta | aplicado (D2 da revisão) | contrariava o DEFINE | 1 pergunta a mais quando houver |
| Decision 11: lista de pendências ampliada para a fronteira | aplicado (Decision 12) | achados da revisão focada | 8 arquivos a mais |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (61/61)
- [x] Incremental verification recorded (baseline vermelha, sabotagens)
- [x] Verify Gate green
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified: 45 de 45; o commit do 17b não foi visto rodar fora do Claude (Issue 11)
- [x] LLM prompt receipts complete (N/A: `LLM Prompts: false`)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [ ] Release `v2.6.0`: falta o CI e o OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
