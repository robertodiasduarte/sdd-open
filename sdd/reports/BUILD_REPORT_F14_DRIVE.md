# BUILD REPORT: F14 Drive e orquestração

> Implementation report for F14 Drive e orquestração

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F14_DRIVE |
| **Date** | 2026-11-05 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F14_DRIVE.md` |
| **DEFINE** | `sdd/features/DEFINE_F14_DRIVE.md` (v1.9, 38 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F14_DRIVE.md` (v1.8, 12 decisões, 38 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f14-drive`, sobre `8a320e9` (= `v2.6.0`).
- **Commits:** `aabc4a3` curadoria da 1ª entrega · `3331b6c` os 5 achados da rodada 4 · `7f4f442` build · `f519661`, `8334159`, `079f5fa` varredura da W0 e contrato do gate · `58d0175`, `79ea6c0`, `68d2341`, `ff5c539` avaliador, ciclos 1 a 3 · `c9a35d9`, `52f0830`, `c5b0655`, `b0663d3` revisão real, rodadas 1 a 4. O commit final é `b0663d3`.
- **Fontes (só leitura):** `origin/main` do privado (`a029cf455`): `drive.md`, `sdd-driver.js`, `sdd-archive.py`, `deploy-do-sha.mjs`, `release.md`.
- **Decisões D4 do Roberto (2026-11-05 e 06):** 3º ciclo focado do avaliador; 4ª rodada da revisão real; 5ª rodada, com crédito reposto por ele; publicar `b0663d3` como está, com os 5 achados da rodada 5 como 1ª tarefa da próxima frente.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 38 linhas |
| Cross-file coupling | Alto: script, skill, contrato e documentos dizem o mesmo |

**Recommendation:** default.

**User decision:** "Uma sessão só (Recomendado)".

**Pre-build review:** Sim: revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 4 HIGH, 14 MEDIUM, 8 LOW, 5 propostas, todas aplicadas).

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 38/38 |
| **Files Created** | 12 |
| **Files Modified** | 26 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | Verify Gates, baseline vermelha, sabotagens, 3 ciclos do avaliador, revisão do DESIGN |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: `sdd/bin/sdd-drive.sh`; skill `sdd-drive` 1.0.0 com o brief do executor; `sdd/bin/deploy-do-sha.sh`; `sdd/bin/sdd-archive.py`; `sdd-release` 2.8.0 (0b, 10, 11, 15b e `references/raio-de-impacto.md`); slots `drive.max_rounds`, `deploy.workflow`, `deploy.transient_steps`; `verify-gate.sh --checar`; `sdd-fluxo.sh seguir --drive`; guarda do avaliador e filtro da colheita (L10); `docs/sdd-drive.md` + PT.

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|---|---|---|---|
| `sdd-drive.sh`, textos da skill | LM-001 | ✔ tratado | motivos com fixture dos 2 lados; barreira provada por efeito, com `git` e `gh` de mentira |
| testes novos, `--checar` | LM-002 | ✔ tratado | baseline vermelha na `v2.6.0`; 5 e 64 em teste antes do verde |
| guarda do avaliador | LM-003 | ✔ tratado | só não rastreado nas 4 pastas; revisão com tudo commitado |
| filtro da colheita | LM-005 | ✔ tratado | forma exata da linha, com o caso vizinho em teste; o resto fica para o curador julgar |
| `--self-test` | LM-006 | ✔ tratado | repositório próprio, em memória; roda na cópia de `git archive` |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `git diff --name-only` `--no-renames` `rename`
regra: `git diff --name-only` mostra só o nome novo de um rename: uma conferência de "só documento mudou" aceita código movido para a pasta de documento, e o commit que a própria ação pede apaga o sinal. **Do instead:** nessa conferência, passar `--no-renames`, com teste do rename sujo e do commitado, nos 2 sentidos.
evidencia: sdd/reviews/AVALIACAO_F14_DRIVE_20261105-ciclo2.md
>>>
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `HTTP 402` `limit_remaining` `/credits`
regra: O `limit_remaining` de uma chave da OpenRouter é o limite da chave, não o saldo da conta: um revisor caiu com HTTP 402 em 1 segundo, com "US$ 220 restantes", e a queda foi lida como passageira por 2 rodadas pagas. **Do instead:** antes de uma rodada, ler o saldo em `/api/v1/credits`; revisor que cai em segundos pede a mensagem do provedor antes de qualquer conclusão.
evidencia: sdd/reports/evidence/F14_DRIVE/real-rodada3.log
>>>
```

---

## Task Execution

Modo default. A tarefa 1 (curadoria e rodada 4) foi em 2 commits antes do brainstorm; o build, em `7f4f442`; cada ciclo do avaliador, em commit próprio.

---

## Files Changed

Os 38 itens do File Manifest do DESIGN, mais `docs/verify-gate-contract.md` (o `--checar`). `MANIFEST.txt` atualizado; `git ls-files` confere.

---

## Drift Detected

| Item | Drift | Decisão |
|---|---|---|
| `docs/drive.md` | a varredura da W0 proíbe o padrão do comando do privado em qualquer arquivo | renomeado `docs/sdd-drive.md`; a varredura ficou como está |
| `sdd/fixtures/drive/`, `sdd/fixtures/deploy/` | fixture em pasta nova não chega a quem atualiza | fixtures no script e nos testes (revisão do DESIGN, H3) |
| `--ours` do plano | o lado depende da operação (medido) | `git show origin/<branch>:CHANGELOG.md`; registrado no DEFINE |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline | os 4 arquivos de teste novos contra a árvore `v2.6.0` | Pass (vermelho esperado nos 4) | `sdd/reports/evidence/F14_DRIVE/baseline-v2.6.0.log` |
| Sabotagens tarefa 1 | R1 a R5 da rodada 4 | Pass (9 de 9) | `sdd/reports/evidence/F14_DRIVE/sabotagens-tarefa1.log` |
| Sabotagens | 67 em `b0663d3`: 64 derrubam teste; 3 vivas, explicadas em Issues | Pass, com 3 vivas conhecidas | `sdd/reports/evidence/F14_DRIVE/sabotagens-b0663d3.log`, `sdd/reports/evidence/F14_DRIVE/sabotagens-resto-b0663d3.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `cmd` do DEFINE: cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso (`/bin/bash` 3.2, `/usr/bin/python3` 3.9) |
| **Exit / Result** | 0 em `079f5fa` (1.558 testes); 2 em `68d2341` (publish-gate: literal de 11+ dígitos num teste); 0 em `ff5c539` (1.626), `52f0830` (1.646) e `b0663d3` (1.656) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `check-versions.py --base v2.6.0 --base-obrigatoria`; `skill-lint --conversa` (19); `sdd-decisoes-lint --sites` (25 + 2) | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | iniciar grava o estado e diz a 1ª ação | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-002 | recusas na entrada, vizinhos antigos | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-003 | simulação não executa nem grava | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-004 | limite: flag, slot, default | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-005 | próxima ação recalculada do disco | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-006 | PROGRESS semeado da 1ª tabela do manifest | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-007 | 3ª repetição para | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-008 | gate pelo script, HEAD de antes, --fundo e trava | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-009 | exits do gate sem gastar rodada | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-010 | COMMITAR e CORRIGIR | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-011 | impressão digital e aceite | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-012 | retomada e orçamento | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-013 | estado inválido por forma inteira | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-014 | concluir responde o mesmo que proximo | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-015 | DRIVE_REPORT em toda parada | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-016 | recibo, bloqueio, aguardar | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-017 | barreira por efeito, com git e gh de mentira | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-018 | self-test | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-019 | a skill segue o script | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-020 | parada sem subagente | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-021 | 0b por superfície | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-022 | run próprio verde, filtros | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-023 | substituto que contém o commit | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-024 | redisparo único, nunca rerun | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-025 | quando não repete | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-026 | exits 3, 4 e 64 | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-027 | item 10 chama o script | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-028 | simulação do archive | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-029 | git mv por lote | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-030 | proteção pela ficha | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-031 | changelog e 15b | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-032 | documento não rastreado não trava | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-033 | rastreado e fora das pastas seguem travando | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-034 | colheita sem eco nem diagnóstico | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-035 | slots | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-036 | docs, roadmap, 19 skills, manifest | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-037 | contratos anteriores | Pass | `sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log` |
| AT-038 | prova num agente de fora do Claude: Codex CLI 0.163 com `gpt-6.1-sol`, conta própria, em 3 sessões; parada 40, executor com commit, retomada até `gate-verde`, nenhum push | Pass | `sdd/reports/evidence/F14_DRIVE/AT-038.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 5 propostas e 26 defeitos da revisão do DESIGN, com veredito no Advisor Ledger do DESIGN (`sdd/reviews/REVISAO_DESIGN_F14_DRIVE_20261105.md`).
**Veredito do avaliador (C1):** NEEDS_WORK no ciclo 3, sobre `79ea6c0` (`sdd/reviews/AVALIACAO_F14_DRIVE_20261105-ciclo3.md`): 0 HIGH, 5 MEDIUM, 14 LOW, corrigidos em `68d2341`, menos os limites declarados. Ciclo 1: 1 HIGH, 9 MEDIUM, 16 LOW (`sdd/reviews/AVALIACAO_F14_DRIVE_20261105-ciclo1.md`). Ciclo 2: 1 HIGH, 4 MEDIUM, 16 LOW (`sdd/reviews/AVALIACAO_F14_DRIVE_20261105-ciclo2.md`). Nenhum avaliador rodou depois de `68d2341`; as rodadas da revisão real cobrem o resto.
**Revisão adversarial real:** 5 rodadas, com revisor claude e auditor `openrouter:qwen/qwen3.7-plus`. 2º revisor: `openrouter:deepseek/deepseek-v4-pro` na 1ª; caiu nas rodadas 2 e 3 com HTTP 402, porque o saldo da OpenRouter acabou; codex nas rodadas 4 e 5. A 4ª não vale como revisão completa: o auditor também caiu sem crédito. Na 5ª, `--conferir` CONFERE em `b0663d3`, e o `loop` sai BLOQUEADO no teto, com 1 HIGH levado à decisão D4 do Roberto (`sdd/reports/evidence/F14_DRIVE/real-rodada5.log`, `sdd/reports/evidence/F14_DRIVE/ledger-review.md`).

---

## Advisor Ledger

Ver o Advisor Ledger de `sdd/features/DESIGN_F14_DRIVE.md`: revisão do DESIGN, item por item. Ciclos do avaliador: os achados e o conserto estão nos commits e no histórico do DESIGN. Revisão adversarial real: `sdd/reports/evidence/F14_DRIVE/ledger-review.md`.

Ficam como pendência, por decisão D4 do Roberto, os 5 da rodada 5: trava de estado que vence com o dono vivo (HIGH), repetir o `deploy-do-sha.sh` sem teto total (MED), marca que sobra depois de 401, laço de CPU na trava que não se apaga, documento recente em sem classificação. Ficam também, com motivo: L1 (edição temporária durante o gate), L2 (`skip-worktree`), L3 (`BUILD_REPORT` velho), L6 (arquivo ignorado), L7 (gate morto por sinal), L8 em parte (gate órfão) e M5 em parte (`$ cmd` de várias linhas: o curador julga) do ciclo 3; os 4 primeiros estão em `docs/sdd-drive.md`, seção de limites. L14 do ciclo 3 (DEFINE com CRLF) é de `verify-gate.sh`, fora desta frente. Herdadas: F5, F6, F7, guarda de F9, L7, N-L9, N-L10, resto de N-L11 da 1ª entrega. Novo: `sdd-fluxo.sh` importa módulo da pasta do projeto (`json.py`), porque o núcleo roda com `python3 -B -`. Nada rodou em Windows, e o ramo `tasklist` do `sdd-drive.sh` não tem prova.

---

## Issues Encountered

1. A suíte reprovou em `7f4f442` pela varredura da W0: drift acima.
2. Duas sabotagens vivas na 1ª rodada: checagem redundante (removida) e self-test sem teste que o prove vermelho (teste novo).
3. Eu disse ao Roberto que o saldo da OpenRouter estava folgado (US$ 220) e que a queda do DeepSeek era passageira: US$ 220 era o limite da chave, e o saldo tinha acabado (HTTP 402). Corrigido na conversa; ele repôs US$ 10.
4. Sabotagens vivas em `b0663d3`: `pega_trava` e a impressão gravada no gate ficaram sem efeito próprio, cobertas pela trava de estado e pelo `--resume` que não grava com gate rodando (mutantes equivalentes); falta 1 teste: ficha aberta de slice sem nenhum documento com o nome do slice. Fica para a próxima frente: teste novo invalidaria o `--conferir`.
5. Em `gate-shell-evidencia.sh`, `AVAL-26` e `AVAL2-21` são acusados: são sondas do avaliador com formatador, fora do diff e sem AT que dependa delas.
6. Cada ciclo do avaliador achou defeito real: `gate-verde` em commit não testado (ciclo 1), rename commitado (ciclo 2, regressão do conserto do ciclo 1), submodule e estado editado (ciclo 3).

---

## Deviations from Design

Ver `## Drift Detected`.

---

## Blockers

Nenhum.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (38/38)
- [x] Incremental verification recorded (baseline vermelha, sabotagens)
- [x] Verify Gate green
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified: 38 de 38
- [x] LLM prompt receipts complete (N/A: `LLM Prompts: false`)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [ ] Release `v2.7.0`: falta o CI e o OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
