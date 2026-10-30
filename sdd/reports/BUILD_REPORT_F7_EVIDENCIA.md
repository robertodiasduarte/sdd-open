# BUILD REPORT: F7 Evidência que não mente

> Implementation report for F7 Evidência que não mente

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F7_EVIDENCIA |
| **Date** | 2026-10-30 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F7_EVIDENCIA.md` |
| **DEFINE** | `sdd/features/DEFINE_F7_EVIDENCIA.md` (v1.5) |
| **DESIGN** | `sdd/features/DESIGN_F7_EVIDENCIA.md` (v1.3) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F7_EVIDENCIA.md` (8 MUST de texto de saída) |
| **Status** | Complete |

- **Branch:** `feat/f7-evidencia`, sobre `1c9bbc7` (= `v2.2.7`).
- **Commits:** `514324f` — build; `bed1f69` — notas do ciclo 1 da revisão de contexto fresco do build; `1d225e5` — notas do ciclo 2.
- **Escopo:** 39 arquivos do produto (25 novos, 14 alterados); números do `git diff --stat v2.2.7 HEAD` (`sdd/reports/evidence/F7_EVIDENCIA/escopo.log`).
- **Fontes (só leitura):** `origin/main` do repositório privado (`ecdab8d41`): `.githooks/claude-build-report-guard.py`, `claude-avaliador-guard.py`, `scripts/gates/avaliador-pendente-guard.sh`, `gate-baseline.sh`, `gate-shell-evidencia.sh`, `scripts/verify-gate.sh` e os testes deles. O checkout local do privado está atrás do `origin/main`; nada foi alterado lá.
- **Revisões de contexto fresco:**
  - do DESIGN, antes do build: `sdd/reviews/REVISAO_DESIGN_F7_EVIDENCIA_20261030.md`;
  - do build: `sdd/reviews/AVALIACAO_F7_EVIDENCIA_20261030-ciclo1.md` e `…-ciclo2.md` (o ciclo 2 caiu uma vez por ECONNRESET e foi retomado com o mesmo contexto).

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 38 linhas: 25 novos (4 scripts, 1 fragmento, 13 fixtures, 7 testes) e 13 alterados |
| Cross-file coupling | Alto: os 6 scripts compartilham o contrato de saída (`🛑`/`⚠️`, `RESULTADO:`, `→`), a leitura do `sdd/config.yaml` e as fixtures; as 2 skills citam os scripts pelo nome |
| Security surface | O `avaliador-guard.sh` protege trabalho não commitado; o `gate-baseline.sh` e o `test-baseline.sh` executam comandos que o build já executava. Nenhum segredo, nenhuma rede |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Médio (4 scripts novos independentes entre si), mas com convenção comum |
| Context-rot risk | Alto: a sessão foi do brainstorm ao build. Mitigado pelos artefatos, por 3 revisões de contexto fresco e por um teste de cada regra dos dois lados |
| Runtime capabilities | default e subagente disponíveis; briefs não oferecido |

**Recommendation:** default.

**User decision:** default. O Roberto pediu "execute o define, ux-review, design, review do design, build, review do build" em sequência; o modo foi registrado, não perguntado.

**Pre-build review:** Sim, a revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 2 HIGH, 4 MEDIUM, 8 LOW, todas aplicadas antes do build; os 5 ajustes de contrato ACEITOS no DEFINE v1.2).

---

## Summary

| Metric | Value |
|---|---|
| Scripts novos | 4: `gate-baseline.sh` (138 linhas), `gate-shell-evidencia.sh` (127), `avaliador-guard.sh` (113), `test-baseline.sh` (218) |
| Scripts alterados | `report-lint.py` (323 → 625 linhas; as 32 regras atuais intactas), `verify-gate.sh` (197 → 259; os 6 exits e a saída intactos) |
| Testes | 514 → 630 no piso (7 arquivos novos; 3 alterados nas versões fixadas e nos helpers) |
| Fixtures | 13 em `sdd/fixtures/evidencia/` (4 relatórios, 3 logs, 6 saídas de teste) |
| Skills | `sdd-build` 2.2.1 → 2.3.0; `sdd-release` 2.3.1 → 2.4.0 |
| Correções de P1 achadas no caminho | 1: o `verify-gate.sh` lia o DEFINE pelo caminho relativo depois de trocar de pasta, e falhava quando chamado de uma subpasta (defeito anterior à F7) |
| Release | `v2.2.8` automática (decisão do Roberto no brainstorm, contra a recomendação de `v2.3.0`) |

---

## Task Execution

| # | Task | Status | Notes |
|---|---|---|---|
| 1 | `sdd/bin/report-lint.py` | Done | Funções novas ao lado; classe por violação e `→` por classe (UX U1) |
| 2 | `sdd/bin/verify-gate.sh` | Done | Trace no `trap EXIT` depois da raiz, exit original, `--sem-define`; o DEFINE lido pelo caminho absoluto (P1) |
| 3 | `sdd/bin/gate-baseline.sh` | Done | `--sobrepor`; "avaliou" só com `🔴` ou marcador de asserção (nota H1 do DESIGN) |
| 4 | `sdd/bin/gate-shell-evidencia.sh` | Done | Sem arrays, `LC_ALL=C`, `exit=N` sem colchete |
| 5 | `sdd/bin/avaliador-guard.sh` | Done | Permite `sdd/reports/evidence/` e `sdd/traces/` (nota H2 do DESIGN) |
| 6 | `sdd/bin/test-baseline.sh` | Done | Bash roda, Python embutido lê os 5 formatos; poda só na execução completa |
| 7 | `sdd/config.example.yaml` | Done | `evidence.require_avaliacao_layers: 2` |
| 8–10 | `EVIDENCIA.md`, `LLM_PROMPTS_BUILD_REPORT.md`, `BUILD_REPORT_TEMPLATE.md` | Done | Receita com `rc=$?`, a linha do avaliador, a forma mínima |
| 11–12 | `sdd-build` 2.3.0 e `sdd-release` 2.4.0 | Done | Passos 1, 1.5, 5a, 5b, 5d e 6; 0a.4, 0a.5 e 0a.7; 6 + 2 "por quê" |
| 13–25 | Fixtures | Done | Escritas do zero com os casos dos testes do privado |
| 26–35 | Testes | Done | Cada regra dos dois lados; `test_bash32.py` |
| 36–37 | Roadmaps | Done | A linha passou a "Hooks"; 7 linhas |
| 38 | `MANIFEST.txt` | Done | +25 linhas, ordem `LC_ALL=C` |

---

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `sdd/bin/report-lint.py` | Modified | D4 fail-closed, E1–E6, `--pendente`, `--stdin` |
| `sdd/bin/verify-gate.sh` | Modified | E9: `--trace`, `--sem-define`; leitura do DEFINE pelo caminho absoluto |
| `sdd/bin/gate-baseline.sh` | Created | E7 |
| `sdd/bin/gate-shell-evidencia.sh` | Created | E8 |
| `sdd/bin/avaliador-guard.sh` | Created | E11 |
| `sdd/bin/test-baseline.sh` | Created | E10 |
| `sdd/config.example.yaml` | Modified | Slot `evidence.require_avaliacao_layers` |
| `sdd/templates/fragments/EVIDENCIA.md` | Modified | Receita, linha do avaliador, o que o lint nega |
| `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md` | Created | E13 |
| `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modified | `PENDENTE`, `layers:` |
| `.agents/skills/sdd-build/SKILL.md` | Modified | 2.3.0 |
| `.agents/skills/sdd-release/SKILL.md` | Modified | 2.4.0 |
| `sdd/fixtures/evidencia/` (13 arquivos) | Created | Os dois lados de cada regra |
| `tests/test_report_lint_evidencia.py`, `test_verify_gate_trace.py`, `test_gate_baseline.py`, `test_gate_shell_evidencia.py`, `test_avaliador_guard.py`, `test_test_baseline.py`, `test_bash32.py` | Created | Testes das regras novas |
| `tests/test_report_lint.py` | Modified | Só os 2 helpers: a forma mínima (AT-012) |
| `tests/test_contrato_build_release.py`, `tests/test_correcoes_w0.py` | Modified | Versões fixadas; contratos de texto F7 |
| `docs/roadmap.md`, `docs/pt-BR/roadmap.md` | Modified | Linha só com os hooks |
| `docs/cli-conventions.md` | Modified | Fora do manifest (drift 3): exits e palavras dos 4 scripts novos |
| `MANIFEST.txt` | Modified | 25 arquivos novos |

---

## Drift Detected

| # | Drift | Decisão |
|---|---|---|
| 1 | O corpus de logs do open tinha 3 linhas `exit=` vazias sem colchete (gravadas pelo `PIPESTATUS` vazio do zsh), que a regra de `[exit=]` não via | A regra passou a cobrir `exit=` vazio com e sem colchete; corpus 22 = 19 + 3 (DEFINE v1.3) |
| 2 | O `--touched` do `test-baseline.sh` dava por tocado qualquer arquivo cujo nome-base aparecesse no id (o próprio `tests.txt`) | Só arquivo de teste pelo nome (`test_*`, `*_test.*`, `*.test.*`, `*.spec.*`), fora de `sdd/` |
| 3 | `docs/cli-conventions.md` lista as palavras de `RESULTADO:` e os exits de cada script | Atualizado com os 4 scripts novos, fora do manifest (documentação; nenhum contrato muda) |
| 4 | O `verify-gate.sh` de `v2.2.7` falhava quando chamado de uma subpasta com caminho relativo | Corrigido (P1): a leitura usa o caminho absoluto, as mensagens mantêm o que a pessoa digitou |
| 5 | Ciclo 1 (LOW-6): `\|&`, `VAR=valor sort` e `[exit= ]` escapavam; `PIPESTATUS` depois do pipe era acusado | Regra ampliada; corpus 22 → 21 (sai um falso positivo de F4); DEFINE v1.4 |
| 6 | Ciclo 2 (LOW-E): `$` sozinho, comentário de 1 espaço, `(tail)`, `command tail` | Regra ampliada; corpus 21 → 22 (entra `F6_DOCS/AVAL-manifest.log:8`, falso positivo conservador de comando composto); DEFINE v1.5 |

Nenhum prompt de runtime.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | suíte inteira no piso em `1c9bbc7` | Pass | 514 OK (A-001; rodado no início da sessão e pela revisão do DESIGN, `AVAL-DESIGN-suite-base.log`) |
| Baseline vermelha | os 7 testes novos, com as fixtures, na árvore `v2.2.7` | Pass (vermelho esperado) | `sdd/reports/evidence/F7_EVIDENCIA/baseline.log` |
| Baseline das notas do ciclo 1 | os testes corrigidos contra `514324f` | Pass (vermelho esperado) | `sdd/reports/evidence/F7_EVIDENCIA/baseline-ciclo1.log` |
| Baseline das notas do ciclo 2 | os testes corrigidos contra `bed1f69` | Pass (vermelho esperado) | `sdd/reports/evidence/F7_EVIDENCIA/baseline-ciclo2.log` |
| Os 8 relatórios do open | `report-lint.py` em cada um | Pass | `sdd/reports/evidence/F7_EVIDENCIA/relatorios-do-open.log` |
| Corpus de logs | `gate-shell-evidencia.sh` sem `F7_EVIDENCIA/`, `diff` contra `corpus-esperado.txt` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/corpus-shell-diff.log` |
| Saída do gate | `v2.2.7` × novo, trace ligado e desligado, 4 fixtures × 3 modos | Pass | `sdd/reports/evidence/F7_EVIDENCIA/saidas-v2.2.7.log` |
| Contratos do `report-lint` | `git diff v2.2.7 HEAD -- tests/test_report_lint.py` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/contratos-report-lint.log` |
| Evidência da própria F7 | `gate-shell-evidencia.sh sdd/reports/evidence/F7_EVIDENCIA` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/shell-da-f7.log` |
| Guard antes de cada avaliador | `avaliador-guard.sh` com os 4 prefixos | Pass | `sdd/reports/evidence/F7_EVIDENCIA/guard-antes-do-avaliador.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F7_EVIDENCIA.md`. O `cmd` faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo `ci` e a suíte no piso |
| **Exit / Result** | 0 em `514324f` (619 testes), `bed1f69` (625) e `1d225e5` (`Ran 630 tests … OK`; G1–G5 verdes) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F7_EVIDENCIA/GATE.log` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` (17) | Pass | `sdd/reports/evidence/F7_EVIDENCIA/skill-lint-conversa.log` |
| Versões | `check-versions.py --base v2.2.7 --base-obrigatoria` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/check-versions.log` |
| bash 3.2 | `grep` de bashismos fora de comentário em `sdd/bin/*.sh` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/bash32.log` |
| Tamanho | `wc -l` (maior `SKILL.md` tocado: 309) | Pass | `sdd/reports/evidence/F7_EVIDENCIA/linhas.log` |
| Typecheck | N/A (Python sem anotação verificada, bash) | N/A | — |
| Tests | os módulos tocados, `-v` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log`, `testes-scripts-novos.log`, `testes-contratos.log` |
| Sabotagem | `sabotagem.sh`, 6 mutações | Pass | `sdd/reports/evidence/F7_EVIDENCIA/sabotagem.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | Sem tabela reconhecida reprova nomeando a tabela | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-002 | Cabeçalho `Result \| Evidence` é conferido | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-003 | Avaliação ausente reprova com as 3 saídas | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-004 | AVALIACAO não citado prova; `N.A.` abaixo do limite passa; contagem impossível passa com ⚠️ | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-005 | `N.A.` com ≥ N camadas reprova; N do slot; N inválido vira 2 com ⚠️ | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-006 | Declaração sem motivo reprova | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-007 | `PENDENTE`: 0 com ⚠️; `--pendente` 1 com `arquivo:linha`; 64 em uso | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-008 | Evidência ignorada pelo git reprova; sem git, ⚠️ | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-009 | Veredito em linha, título ou linha de tabela; bloco cercado não conta | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-010 | `--stdin` confere como o arquivo | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-011 | Os 8 relatórios do open: 5 reprovam só por avaliação ausente, 3 passam | Pass | `sdd/reports/evidence/F7_EVIDENCIA/relatorios-do-open.log` |
| AT-012 | As 32 asserções intactas; só a forma mínima nos helpers | Pass | `sdd/reports/evidence/F7_EVIDENCIA/contratos-report-lint.log` |
| AT-013 | 1 linha JSONL por execução, exit original | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-014 | `--print`, `SDD_TRACE=off` e trace sem permissão não mudam exit nem saída | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-015 | `--sem-define` grava `release/no-define` e sai 0; 64 sem feature | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-f7.log` |
| AT-016 | Saída idêntica com e sem trace e à `v2.2.7`; `--strict` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/saidas-v2.2.7.log` |
| AT-017 | A base reprova avaliando → 0 e `BASELINE-gate.log` | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-018 | A base passa → 2; crash ou sem avaliar → 3; uso → 64 | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-019 | Exit de formatador, vazio ou literal → 2 com o conjunto exato | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-020 | Logs honestos → 0; corpus do open → as 22 esperadas; base inválida → 64 | Pass | `sdd/reports/evidence/F7_EVIDENCIA/corpus-shell-diff.log` |
| AT-021 | Árvore limpa, evidência, trace e prefixos permitidos → 0 | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-022 | Sujo → 1 com cada caminho e o commit que funciona; git falha → 2; off → 0 ⚠️ | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-023 | 5 formatos: só a falha nova aborta | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-024 | Poda só na execução completa; `--touched`; `--aceitar` sem rodar | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-025 | Não reconhecido ou ausente → 3; `test_cmd` vazio → PULADO | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-scripts-novos.log` |
| AT-026 | `sdd-build` 2.3.0 com os passos e os 5 "por quê" | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-contratos.log` |
| AT-027 | `sdd-release` 2.4.0: `--pendente` e gate-shell com ≠ 0, `--sem-define`, 3 "por quê", bloco do OK intacto | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-contratos.log` |
| AT-028 | `EVIDENCIA.md`, template, fragmento LLM e slot | Pass | `sdd/reports/evidence/F7_EVIDENCIA/testes-contratos.log` |
| AT-029 | 514 testes anteriores, agnóstico, 17 skills, publish-gate ci, roadmap | Pass | `sdd/reports/evidence/F7_EVIDENCIA/GATE.log` |
| AT-030 | 6 sabotagens vermelhas e restauradas | Pass | `sdd/reports/evidence/F7_EVIDENCIA/sabotagem.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** contagem impossível neste repositório (sem `sdd/config.yaml`); o avaliador rodou mesmo assim (2 ciclos).
**Contrato de aceite (passo 1.5 da `sdd-build`):** 5 propostas / 5 aceitas — `## Contrato de aceite` do DESIGN.
**Veredito do avaliador (C1):** NEEDS_WORK · ciclos: 2 · achados: 9 (ciclo 1) + 6 (ciclo 2), 0 HIGH em ambos · `AVALIACAO_F7_EVIDENCIA_20261030-ciclo2.md`

Os 15 achados foram aplicados (`bed1f69` e `1d225e5`), cada um com teste dos dois lados e baseline vermelha no commit anterior (`baseline-ciclo1.log`, `baseline-ciclo2.log`). As correções do ciclo 2 **não** passaram por um 3º avaliador: a `sdd-build` limita a 2 ciclos, e a decisão de abrir um 3º é do Roberto (ver Final Status).

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F7_EVIDENCIA_20261030.md`. As 14 notas estão no Advisor Ledger do DESIGN v1.1: todas APPLIED.

**Revisão do build (pós-build):** 2 ciclos de avaliador em contexto fresco, cada um numa worktree destacada, com o guard verde antes do despacho (`guard-antes-do-avaliador.log`).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| M1 | ciclo 1 | trace não gravável mudava o stderr do gate | MEDIUM | APPLIED | `2>/dev/null` antes do `>>`; `test_trace_sem_permissao_nao_muda_a_saida`. `bed1f69` |
| M2 | ciclo 1 | modo diff do gate-shell não via staged nem modificado | MEDIUM | APPLIED | `git diff HEAD` no escopo; `test_staged_e_rastreado_modificado_tambem_entram`. `bed1f69` |
| M3 | ciclo 1 | go `[build failed]` mascarado e baseline podado | MEDIUM | APPLIED | id `build failed: <pacote>`; `test_pacote_go_que_nao_compila_nao_e_mascarado`. `bed1f69` |
| L1 | ciclo 1 | rótulos sem `(C1)`; unidade da tabela | LOW | APPLIED | `VERDICT_LABEL_RE` e escopo por linha; `test_rotulos_sem_c1`. `bed1f69` |
| L2 | ciclo 1 | commit sugerido falhava com renomeação | LOW | APPLIED | `add -A --` com os caminhos que o git reconhece; `test_o_commit_sugerido_funciona_com_renomeacao`. `bed1f69` |
| L3 | ciclo 1 | 2 regras novas sem "por quê" | LOW | APPLIED | itens nas 2 skills e nos testes de contrato. `bed1f69` |
| L4 | ciclo 1 | `sabotagem.log` ausente na cópia avaliada | LOW | REBUTTED | o log é gerado na worktree do build depois do commit e existe (`sabotagem.log`); o avaliador reproduziu 6/6 numa cópia |
| L5 | ciclo 1 | `--aceitar` rodando o teste sem imprimir não era pego | LOW | APPLIED | marcador `rodou.txt` no teste. `bed1f69` |
| L6 | ciclo 1 | `\|&`, `VAR=x sort`, `[exit= ]`, `PIPESTATUS` depois do pipe | LOW | APPLIED | regra ampliada; corpus 22 → 21; `test_bordas_do_pipe`. `bed1f69` |
| MA | ciclo 2 | pacote go que falha sem `--- FAIL` (timeout) mascarado e podado | MEDIUM | APPLIED | `package failed: <pacote>` (linhas de resumo com TAB); `test_pacote_go_sem_linha_de_teste_tambem_falha`. `1d225e5` |
| MB | ciclo 2 | deno real colorido não reconhecido | MEDIUM | APPLIED | cores ANSI removidas antes dos regex; `test_saida_colorida_e_lida`. `1d225e5` |
| MC | ciclo 2 | só remoção staged: o commit sugerido virava `git add -A` sem caminho (regressão do L2) | MEDIUM | APPLIED | só `commit` quando não há caminho; `test_so_remocao_staged_sugere_commit_sem_add`. `1d225e5` |
| LD | ciclo 2 | `**Veredito do avaliador**:` e `\| Veredito do avaliador \|` não reconhecidos | LOW | APPLIED | `test_rotulos_em_negrito_e_em_tabela_sem_c1`. `1d225e5` |
| LE | ciclo 2 | `$` sozinho, comentário de 1 espaço, `(tail)`, `command tail`; `r=$?` acusado | LOW | APPLIED | regra ampliada; corpus 21 → 22 (entra 1 falso positivo conservador de comando composto); `test_bordas_do_pipe`. `1d225e5` |
| LF | ciclo 2 | `--sem-define` dizia "gravado" sem gravar | LOW | APPLIED | grava antes de falar; `test_sem_permissao_diz_que_nao_gravou`. `1d225e5` |

Contagem de achados: DESIGN 14, build ciclo 1 9, ciclo 2 6 (0 HIGH nos 3).

---

## Issues Encountered

| Issue | Resolution |
|---|---|
| O checkout local do privado está atrás do `origin/main`: 2 das 6 fontes não existiam no disco | Lidas por `git show origin/main:<arquivo>`; as linhas batem com o plano |
| O `awk` do macOS sai com `multibyte conversion failure` num log com UTF-8 | Todo `awk` sobre log com `LC_ALL=C`; teste com log acentuado |
| Duas sondas de teste (`echo FAILED (failures=1)` sem aspas) passavam pelo motivo errado: o erro de sintaxe repetia o comando com o marcador | Aspas e `assertNotIn("syntax error")` (LM-002) |
| A fixture "honesto" tinha `pipefail` só num comentário, que a regra ignora de propósito | Fixture corrigida (`set -o pipefail;` no comando) |
| A própria evidência da F7 seria acusada (`| tr`, `| sed`, depois `| LC_ALL=C sort`) | Comandos do `gerar-evidencia.sh` reescritos sem formatador no último estágio; `shell-da-f7.log` com 0 |
| Um `rm -rf` com variável foi barrado pela checagem de segurança do agente | Contornado sem apagar nada (o log foi sobrescrito); nenhuma remoção pendente |

---

## Deviations from Design

| Deviation | Reason |
|---|---|
| `docs/cli-conventions.md` alterado, fora do manifest | Drift 3 |
| `gate-shell-evidencia.sh`: `PIPESTATUS` em qualquer ponto absolve (o DESIGN dizia "antes do último pipe") | Ciclo 1, LOW-6: no bash é honesto; no zsh a linha sai vazia e a regra do vazio pega |
| `test-baseline.sh`: `[build failed]`/`[setup failed]` do go viram falha | Ciclo 1, MEDIUM-3 |
| `avaliador-guard.sh`: o commit sugerido leva `add -A --` só com os caminhos que o git reconhece | Ciclo 1, LOW-2 |

---

## Blockers

Nenhum.

---

## Final Status

### Overall: COMPLETE

- Verify Gate `--strict` verde em `514324f`, `bed1f69` e `1d225e5` (`GATE.log`); `report-lint` (regras novas) e `validate_build_report` rodados sobre este arquivo.
- 6/6 sabotagens vermelhas e restauradas sobre `1d225e5` (`sabotagem.log`); evidência da própria F7 com 0 acusações no `gate-shell-evidencia.sh` (`shell-da-f7.log`).
- Avaliador de contexto fresco: 2 ciclos, NEEDS_WORK nos dois, **0 HIGH**; os 15 achados aplicados. Critério do prompt da sessão ("a revisão de contexto fresco terminou sem HIGH aberto"): atendido. As correções do ciclo 2 não passaram por um 3º ciclo (decisão pendente do Roberto).
- PR: https://github.com/robertodiasduarte/sdd-open/pull/9 (MERGED), CI verde em `ubuntu-latest` e `macos-latest` (run 41126526373, `ci-pr.log`).
- Release: bloco do OK apresentado; OK do Roberto citando "sdd-open" em 2026-10-30 ("finalizar (push + deploy + verificar) do sdd-open"), depois da decisão de seguir sem 3º ciclo do avaliador; push fast-forward `1c9bbc7..1d225e5` em `main`. Run `release` 41133637690 verde (testes, testes no piso macOS, publicar) e `publish-gate` 41133637778 verde; `v2.2.8` aponta para `1d225e5` com `sdd-open-v2.2.8.tar.gz` (SHA-256 `1fdf742b3068edf2a55526b6734b92251099d81095a627c284e67846464947de`) e `SHA256SUMS.txt`, e `shasum -a 256 -c` dá OK (`release.log`).

---

## Next Step

Execute o **SDD Handoff by RDD**.
