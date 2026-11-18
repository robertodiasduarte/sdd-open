# BUILD REPORT: W0 — as 5 correções do porte (parâmetro P1)

> Fix sem BRAINSTORM/DEFINE/DESIGN (regra "Quando pular o SDD formal" da `sdd-release`); escopo na
> seção 3.1 de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | W0 |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM / DEFINE / DESIGN** | dispensados (fix; plano consolidado, seção 3.1) |
| **Status** | Complete |

Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1`, branch `feat/w0-m1`, commits `b1df8c8` (build) e `303cc87`
(notas da revisão de contexto fresco), sobre `1a54da5` = `v2.2.3`.

---

## Summary

| Defeito | Correção |
|---|---|
| 4.1 `sdd-iterate` nunca via clarificação aberta: o passo 4 só rodava `verify-gate.sh --print`, que é isento de marcador | passo 4 roda `--print` (parse: 0; 64 = bloco ruim) **e** o gate sem `--print` (5 = marcador ativo ⇒ voltar ao Define; 0/2/3/4 dizem do código e não contam aqui). `sdd-iterate` 2.0.0 → 2.0.1 |
| 4.2 "CONTEXTO de domínio / Step 1.5 do /define / slice 2" | linha e bullet saem do `DEFINE_TEMPLATE.md`; `config.example.yaml` perde os dois "(slice 2)" (o de `editor`/`worktree_base` vira "(sdd-new-session)") |
| 4.3 `/drive` citado sem existir | sai de `CLARIFY.md`, `DEFINE_TEMPLATE.md` e `VERIFY_GATE.md` |
| 4.4 guard `.githooks/claude-build-report-guard.py` citado sem existir | `EVIDENCIA.md` e `BUILD_REPORT_TEMPLATE.md` apontam `sdd/bin/report-lint.py`; os 13 "o hook" do `EVIDENCIA.md` viram "o lint"; a regra 4 dizia "falha ABERTO … `systemMessage`" (comportamento de hook do Claude Code) e passa a dizer a verdade do lint: falha fechado |
| 4.5 avaliador "não escreve em arquivo algum" × `AVAL-roteiro-3.log` | os dois briefs de `contexto-fresco.md`: não edita código nem documento; o único arquivo que cria, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`. `sdd-build` 2.1.0 → 2.1.1 |

---

## Files Changed

| # | Arquivo | Ação |
|---|---|---|
| 1 | `.agents/skills/sdd-iterate/SKILL.md` | Modificado (4.1, versão) |
| 2 | `.agents/skills/sdd-build/SKILL.md` | Modificado (versão) |
| 3 | `.agents/skills/sdd-build/references/contexto-fresco.md` | Modificado (4.5) |
| 4 | `sdd/templates/DEFINE_TEMPLATE.md` | Modificado (4.2, 4.3) |
| 5 | `sdd/config.example.yaml` | Modificado (4.2) |
| 6 | `sdd/templates/fragments/CLARIFY.md` | Modificado (4.3) |
| 7 | `sdd/templates/fragments/VERIFY_GATE.md` | Modificado (4.3) |
| 8 | `sdd/templates/fragments/EVIDENCIA.md` | Modificado (4.4) |
| 9 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modificado (4.4, "Step 1.5" → "passo 1.5 da `sdd-build`") |
| 10 | `sdd/templates/DESIGN_TEMPLATE.md` | Modificado ("Step 1.5 do `/build`" → "passo 1.5 da `sdd-build`") |
| 10b | `sdd/templates/fragments/EARS.md` | Modificado (revisão, nota 5: `/define` (Step 4.5) e `/bug-pipeline`) |
| 11 | `tests/test_correcoes_w0.py` | Novo (12 testes) |
| 12 | `tests/test_contrato_build_release.py` | Modificado (versão da `sdd-build` 2.1.1) |
| 13 | `MANIFEST.txt` | Modificado (+1 linha, `LC_ALL=C`) |

Nada de `sdd/bin/`, `sdd/fixtures/`, `scripts/` ou `.github/` mudou (`evidence/W0/contratos-intactos.log`).

---

## Drift Detected

| Onde | O que | Decisão |
|---|---|---|
| `BUILD_REPORT_TEMPLATE.md:202`, `DESIGN_TEMPLATE.md:105` | o grep do gate da W0 (`Step 1\.5`) acha dois locais que o plano não listava; ali o "Step 1.5" é o passo 1.5 **da `sdd-build`** (contrato de aceite), que existe | reescrito como "passo 1.5 da `sdd-build`", o nome que a própria skill usa; o grep fica sem achado sem tirar promessa verdadeira |
| `BUILD_REPORT_TEMPLATE.md:205` | "O hook `build-report-guard` nega `PASS`/`NEEDS_WORK`" — fora do grep (sem o prefixo `claude-`), mesmo defeito da 4.4 | aponta o `report-lint.py`, que faz essa conferência (`check()`, `VERDICT_RE`) |
| texto pedido para a 4.5 | "sem Write/Edit em código" cita ferramentas de um agente só (P2) | escrito sem nome de ferramenta: "não edite código nem documento do projeto" |

---

## Verification Results

### Verify Gate

Sem DEFINE (fix): o critério é o da tarefa. `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh <cópia de git archive HEAD>`
→ exit 0, G1–G5 verdes (`evidence/W0/GATE.log`).

### Complementary Checks

| Check | Resultado | Evidência |
|---|---|---|
| Suíte no piso (Python 3.9.6, bash 3.2.57) | 316 testes OK | `evidence/W0/suite-piso.log` |
| `check-versions.py --base v2.2.3 --base-obrigatoria` | VERDE, 16 skills | `evidence/W0/check-versions.log` |
| `playbook-lint.sh --self-test` e `git diff v2.2.3 -- sdd/bin sdd/fixtures scripts .github` | 0 · vazio | `evidence/W0/contratos-intactos.log` |
| Baseline vermelho: `test_correcoes_w0` sobre `v2.2.3` | 9 de 12 FAIL (os 3 verdes conferem o script, que não mudou) | `evidence/W0/baseline.log` |
| Sabotagem: um defeito devolvido por correção (4.1 a 4.5) e as 3 mutações da revisão | 8 de 8 vermelhas com o nome do teste, verdes depois do `git checkout` | `evidence/W0/sabotagem.log` |

---

## Acceptance Test Verification

| ID | Critério | Resultado | Evidência |
|----|----------|-----------|-----------|
| AT-001 | `verify-gate.sh` na fixture de clarificação sai 0 com `--print` e 5 sem | true | `evidence/W0/W0-4.1-fixture.log` |
| AT-002 | As chamadas do passo 4 da `sdd-iterate`, executadas, acusam o marcador (5) e não acusam na fixture de controle | true | `evidence/W0/W0-testes.log` |
| AT-003 | `grep -rnE 'claude-build-report-guard\|/drive\|Step 1\.5\|slice 2' sdd/ .agents/` sem achado fora dos artefatos SDD | true | `evidence/W0/W0-grep.log` |
| AT-004 | Os briefs do avaliador só permitem criar `AVAL-*.log`, como o `EVIDENCIA.md` espera | true | `evidence/W0/W0-testes.log` |
| AT-005 | Suíte inteira verde no piso | true | `evidence/W0/suite-piso.log` |
| AT-006 | publish-gate em modo ci sobre `git archive HEAD` sai 0 | true | `evidence/W0/GATE.log` |
| AT-007 | `check-versions.py --base v2.2.3 --base-obrigatoria` sai 0 | true | `evidence/W0/check-versions.log` |

---

## Issues Encountered

- Nenhum na construção. A revisão de contexto fresco está em `## Revisão de contexto fresco`.

## Revisão de contexto fresco

Revisor sem a conversa, só leitura, sobre `b1df8c8`. Veredito **FIX FIRST**: 0 HIGH, 5 MEDIUM, 5 LOW.
Reproduziu 316 OK na cópia de `git archive`, 9 FAIL na `v2.2.3` e o publish-gate verde. Notas aplicadas em `303cc87`:

| # | Nota | Decisão |
|---|---|---|
| 1 | MEDIUM — `--print` não valida `kind`/`cmd` (dá 0 com `kind: tset`); o 64 da 2ª chamada ficava sem instrução | aplicada: o texto diz o que o `--print` confere; 64 = corrigir o bloco neste passe; 4 = manual-ux |
| 2 | MEDIUM — a 2ª chamada roda o `cmd` (smoke em produção, eval com custo) e a seta do vermelho puxa para código | aplicada: a seta não vale no iterate; smoke/eval ou `cmd` com efeito ⇒ procurar o marcador pela forma canônica do `CLARIFY.md`, sem rodar o gate. As duas chamadas ficam (pedido da tarefa) |
| 3 | MEDIUM — o teste passava com `build-report-guard` sem prefixo, a linha "CONTEXTO de domínio" e `/drive` em `docs/`/`AGENTS.md.tmpl` | aplicada: o padrão ganha os dois termos; a varredura segue o `MANIFEST.txt`; 3 sabotagens novas |
| 4 | MEDIUM — "o lint NEGA sempre": com cabeçalho em inglês o `report-lint.py` sai 0 sem conferir | aplicada no texto (o cabeçalho reconhecido é dito; `pass`/`verde` contam). Mudar o lint é contrato de `sdd/bin/` ⇒ pendência para a F7 (fail-closed) |
| 5 | MEDIUM — referências sem alvo: `/define` (Step 5.4/4.5), `/bug-pipeline`, "§6.3 do PLANO", `/adversarial-review`, `/build` × `/sdd-build`, `avaliador-fresco` | em parte: as 4 primeiras corrigidas (`CLARIFY.md`, `EARS.md`, `BUILD_REPORT_TEMPLATE.md`). Rebatidas: `/build`/`/define` são forma curta da fase, não citam algo inexistente (a F4 reescreve a camada); `avaliador-fresco` é nome de papel; `/adversarial-review` no `RESUMO_ETAPA.md` fica (Decisão 3: kanban intacto) e vai para a F10 |
| 6 | LOW — o teste varria `sdd/reviews/` local | aplicada com a 3 (MANIFEST) |
| 7 | LOW — "o hook" largo demais, split no título, lista vazia passando | aplicada; o teste do `--print` na fixture fica, como caracterização do gate |
| 8 | LOW — `AskUserQuestion` na linha reescrita do `DEFINE_TEMPLATE.md:91` | aplicada: "pelo protocolo de `fragments/CLARIFY.md`". O do `CLARIFY.md:45` fica para a F4 (item G) |
| 9 | LOW — comentário de `layers` sem o uso em migration | aplicada |
| 10 | LOW — "único arquivo que você pode criar" × sondas que geram cache | aplicada: "que você grava de propósito" |

## Pendências levadas adiante

- `CLARIFY.md:45` ainda diz `AskUserQuestion` (texto anterior à W0): o teste de agnosticismo da F4 (item G) pega.
- F7: `report-lint.py` sai 0 quando nenhuma tabela tem o cabeçalho reconhecido mas há linhas `AT-nnn` com `true` (nota 4) — fail-closed.
- F10: `RESUMO_ETAPA.md:4,49` cita `/adversarial-review`, que o pacote ainda não tem.

## Final Status

### Overall: COMPLETE

## Next Step

PR da branch `feat/w0-m1` → CI verde → OK do Roberto citando "sdd-open" → push fast-forward em `main` → Release `v2.2.4`.
