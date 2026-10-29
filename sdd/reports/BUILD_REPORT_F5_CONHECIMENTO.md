# BUILD REPORT: F5 Conhecimento do sdd-open

> Implementation report for F5 Conhecimento do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F5_CONHECIMENTO |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F5_CONHECIMENTO.md` |
| **DEFINE** | `sdd/features/DEFINE_F5_CONHECIMENTO.md` (v1.4) |
| **DESIGN** | `sdd/features/DESIGN_F5_CONHECIMENTO.md` (v1.4) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F5_CONHECIMENTO.md` |
| **Status** | Complete |

- **Branch:** `feat/f5-conhecimento`, sobre `2fcdda1` (= `v2.2.5`).
- **Commits:**
  - `bafc63c` — build;
  - `7e5b25c` — teste do `rule-map --check`, achado pela sabotagem;
  - `0e0dba5` — notas do ciclo 1 da revisão de contexto fresco;
  - `7e19462` — notas do ciclo 2.
- **PR:** https://github.com/robertodiasduarte/sdd-open/pull/7 — CI do PR verde (`gate` e `Testes no piso (macOS)`, run 40969129265; `sdd/reports/evidence/F5_CONHECIMENTO/ci-pr.log`).
- **Release:** OK do Roberto ("release do sdd-open autorizado", sem versão ⇒ patch automático); push fast-forward `2fcdda1..7e19462` em `main`; run `release` 40970012304 com `testes` e `testes-macos` antes do `Publicar release` → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6, tag em `7e19462`; SHA-256 de `sdd-open-v2.2.6.tar.gz` `5dedf04b5046574c44664f3e1daa72af5877859ebb7bba35da58cab0e842a114`, `shasum -a 256 -c` OK (`sdd/reports/evidence/F5_CONHECIMENTO/release.log`).
- **Fonte do porte:** `/Users/robertoduarte/rdd-public/sdd-starter`, em `17c69c4`:
  - `skills/sdd-kb` 2.1.0;
  - `tests/test_sdd_kb_normativo.py`;
  - `tests/fixtures/kb_*`;
  - `skills/ux-review-builder/references/` (entrevista, catálogo e URL).
- **Revisões de contexto fresco:**
  - do DESIGN, antes do build: `sdd/reviews/REVISAO_DESIGN_F5_CONHECIMENTO_20261029.md`;
  - do build: `sdd/reviews/AVALIACAO_F5_CONHECIMENTO_20261029-ciclo1.md` e `…-ciclo2.md`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 25 linhas: 42 arquivos novos (36 da skill) e 8 alterados no produto, mais 3 scripts de evidência fora do commit |
| Cross-file coupling | Médio. O `gate.sh`, o `validate_kb.py` e os testes dividem as razões das mensagens. O `kb-dominios.py` lê o RULE_MAP que o `kb_normativo.py` gera |
| Security surface | Baixa. Os scripts só leem o que recebem e `sdd/kb/`; o gate escreve só em `mktemp -d` |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Baixo: o porte é cópia com adaptação |
| Context-rot risk | Médio: a sessão foi do brainstorm ao build, mitigado pelos artefatos e por 3 revisões de contexto fresco |
| Runtime capabilities | default e subagente disponíveis; o modo briefs não foi oferecido |

**Recommendation:** default.

**User decision:** default. O Roberto pediu a sequência define → ux-review → design → revisão do design → build → revisão do build sem pausas; o modo foi registrado, não perguntado.

**Pre-build review:** Sim, a revisão do DESIGN em contexto fresco que o Roberto pediu (NEEDS_WORK: 2 HIGH, 4 MEDIUM, 2 LOW, todas aplicadas antes do build; a H1 aplicada em parte).

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 25/25 |
| **Files Created** | 42 |
| **Files Modified** | 8 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | Suíte de base 1×; baselines vermelhas 3× (build, notas do ciclo 1, notas do ciclo 2); Verify Gate `--strict` 3× (`bafc63c`, `0e0dba5`, `7e19462`); `gerar-evidencia.sh` 3× (9 logs); sabotagem 4× (4 alvos); code points 2× |
| **Verify Gate** | Green |
| **Execution Mode** | default |

São 499 testes: 388 de antes e 111 novos (62 portados, 21 do `test_sdd_kb.py`, 22 do `test_kb_dominios.py` e 6 a mais no `test_conversa.py`). Ficam verdes no `/usr/bin/python3` 3.9.6 com `/bin/bash` 3.2.57.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 14–19 | Testes primeiro, vermelhos sem o código | build-agent | Complete | 33 FAIL e 74 ERROR em 152 testes antes do código | `sdd/reports/evidence/F5_CONHECIMENTO/baseline.log` |
| 2 | 1, 2, 3 | Porte do validador, do `kb_normativo.py` e dos assets; `--strict` com `teste`; sem `__pycache__` na skill | build-agent | Complete | 62 testes portados + `Strict` | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| 3 | 4 | `gate.sh` autossuficiente | build-agent | Complete | 4 aceitas, 12 rejeitadas pelo motivo certo | `sdd/reports/evidence/F5_CONHECIMENTO/gate-kb.log` |
| 4 | 5–8 | `SKILL.md`, `references/`, `como-falar.md` e `CHANGELOG.md` da `sdd-kb` | build-agent | Complete | `skill-lint --conversa` 17/17; `TextoDaSkill` | `sdd/reports/evidence/F5_CONHECIMENTO/skill-lint-conversa.log` |
| 5 | 9 | `sdd/bin/kb-dominios.py` | build-agent | Complete | `test_kb_dominios` | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| 6 | 10, 11 | `DEFINE_TEMPLATE.md` e o passo 10 da `sdd-define` | build-agent | Complete | `PassoDaDefine`; comandos intactos | `sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.log` |
| 7 | 12, 13 | Entrevista da `sdd-ux-review` | build-agent | Complete | `EntrevistaPublico` (5 testes + 1 de cobertura) | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| 8 | 20, 21, 25 | `cli-conventions.md`, `MANIFEST.txt` (+42, `LC_ALL=C`), `.gitattributes` | build-agent | Complete | G3 do publish-gate nos dois sentidos | `sdd/reports/evidence/F5_CONHECIMENTO/GATE.log` |
| 9 | 22–24 | Scripts de evidência e sabotagem | build-agent | Complete | 9 logs em 0; 4/4 sabotagens | `sdd/reports/evidence/F5_CONHECIMENTO/sabotagem.log` |

---

## Files Changed

| File | Lines | Agent | Verified | Notes |
|---|---:|---|---|---|
| `.agents/skills/sdd-kb/` (36 arquivos) | 336 no `SKILL.md` | build-agent | ✅ | Nova; porte do starter 2.1.0 → 2.2.0 |
| `.agents/skills/sdd-kb/scripts/validate_kb.py` | 36 linhas novas ou mudadas sobre o starter | build-agent | ✅ | `raiz_do_projeto`, `teste` no `--strict`, `dont_write_bytecode`, caminhos |
| `.agents/skills/sdd-kb/scripts/gate.sh` | 186 | build-agent | ✅ | Reescrito |
| `sdd/bin/kb-dominios.py` | 163 | build-agent | ✅ | Novo |
| `.agents/skills/sdd-define/SKILL.md` | +17 −3 | build-agent | ✅ | 2.3.0, frase do passo 3, passo 10, Quality Gate |
| `.agents/skills/sdd-ux-review/SKILL.md` · `references/entrevista-publico.md` | +4 −2 · 111 | build-agent | ✅ | 2.3.0; entrevista nova |
| `sdd/templates/DEFINE_TEMPLATE.md` | +1 −1 | build-agent | ✅ | KB Domains sem "ou equivalente" |
| `tests/test_sdd_kb_normativo.py` · `test_sdd_kb.py` · `test_kb_dominios.py` | — | build-agent | ✅ | Novos |
| `tests/test_conversa.py` · `test_skill_lint.py` · `test_matriz_new_session.py` | — | build-agent | ✅ | Mudanças de propósito: 16 → 17, `F4` + `sdd-kb`, `PORTADAS` + `sdd-kb` |
| `docs/cli-conventions.md` · `MANIFEST.txt` · `.gitattributes` | +13 −1 · +42 · 2 | build-agent | ✅ | — |

---

## Drift Detected

Houve 3 drifts, todos registrados antes de seguir:

1. **Bloco comum da camada.** O DESIGN v1.1 tirava a regra "No fecho da fase…" da `sdd-kb`. No build se viu que ela está nas 14 skills, inclusive na `sdd-playbook`. Ela fica, e o bloco segue idêntico nas 15 (DESIGN v1.2, Decision 7).
2. **`__pycache__` dentro da skill.** O `validate_kb.py` importa o `kb_normativo.py` e criaria a pasta, que o `init` e o `sync` copiam. Entrou `sys.dont_write_bytecode = True` no validador e `-B` nos subprocessos dos testes portados. Fica dentro do manifest 2 e 14.
3. **Teste que faltava.** A sabotagem do `kb_normativo.py` não deixou nada vermelho. O `test_sdd_kb.RuleMapCheck` entrou em `7e5b25c`, dentro do manifest 15.

Nenhum arquivo fora do manifest e nenhum prompt de runtime.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | suíte inteira no piso em `2fcdda1` (cópia por `git archive`) | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/base-2fcdda1.log`: 388 OK |
| Baseline vermelha dos testes da F5 | os 6 módulos antes do código | Pass (vermelho esperado) | `sdd/reports/evidence/F5_CONHECIMENTO/baseline.log`: 33 FAIL, 74 ERROR |
| Baseline das notas do ciclo 1 | `test_sdd_kb`, `test_kb_dominios` e `test_conversa` contra o código de `7e5b25c` | Pass (vermelho esperado) | `sdd/reports/evidence/F5_CONHECIMENTO/baseline-notas.log`: 9 FAIL |
| Baseline das notas do ciclo 2 | `test_sdd_kb` e `test_kb_dominios` contra o código de `0e0dba5` | Pass (vermelho esperado) | `sdd/reports/evidence/F5_CONHECIMENTO/baseline-notas2.log`: 4 FAIL |
| Code points dos 50 arquivos que mudaram | Python com `unicodedata` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/codepoints.log`: 0 suspeitos |
| Comandos e passos `v2.2.5` × HEAD | `comandos-intactos.py` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.log` |
| Contratos byte a byte | `git diff --stat v2.2.5 HEAD` dos scripts, das fixtures e dos fragmentos + `playbook-lint --self-test` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/contratos-intactos.log` |
| Versões | `check-versions.py --base v2.2.5 --base-obrigatoria` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/check-versions.log` |
| O próprio DEFINE | `kb-dominios.py sdd/features/DEFINE_F5_CONHECIMENTO.md` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/kb-dominios-proprio.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F5_CONHECIMENTO.md`. O `cmd` faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo `ci` e a suíte no piso |
| **Exit / Result** | 0 em `bafc63c` (486 testes), `0e0dba5` (495) e `7e19462` (G1–G5 verdes; `Ran 499 tests … OK`) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F5_CONHECIMENTO/GATE.log` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` (17) | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/skill-lint-conversa.log` |
| Gate da KB | `bash .agents/skills/sdd-kb/scripts/gate.sh` no piso | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/gate-kb.log` |
| Typecheck | N/A (Python sem anotação verificada) | N/A | — |
| Tests | os 6 módulos da F5, `-v` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| Build / Compile | publish-gate em modo `ci`, dentro do gate | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/GATE.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | `skill-lint --conversa` nas 17 → 0; a `sdd-kb` com seção, bloco comum, identificação e fragmento | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/skill-lint-conversa.log` |
| AT-002 | `gate.sh` no pacote e numa cópia só da skill → 0, uma linha, 4/12 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/gate-kb.log` |
| AT-003 | Caso ruim aceito, bom rejeitado, outro motivo, âncora ausente, RULE_MAP derivado → 2 com a moldura | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-004 | Os 62 testes normativos portados | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-005 | `--strict`: implementação sem teste, teste inexistente ou fora da raiz → 2; teste presente → 0 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-006 | Sem `--strict`: exemplos passam, `teste` não é conferido, exits 0/2/64 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-007 | `nenhum`, nomes que existem, lista do RULE_MAP (com `\|`) → 0 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-008 | 7 casos do DEFINE + linha fora do Technical Context → 1 com `🛑`, `RESULTADO:` e `→` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-009 | Uso → 64; ilegível → 1 sem traceback | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-010 | Passo 10 da `sdd-define` e a linha do template | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-011 | Entrevista: ≥3 perguntas abertas, exatamente 1 de decisão, passo 1 da ux-review | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-012 | Nada de `openai.yaml`, `tests/`, `sdd-starter`, outro caminho de KB ou script sem prefixo | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |
| AT-013 | 388 testes de antes, contratos byte a byte, publish-gate `ci` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/GATE.log` |
| AT-014 | Comandos intactos na `sdd-define` (só o passo 10) e na `sdd-ux-review` (idêntica) | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/comandos-intactos.log` |
| AT-015 | `check-versions --base v2.2.5 --base-obrigatoria` → 0 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/check-versions.log` |
| AT-016 | 4 sabotagens vermelhas com o nome do teste e verdes depois do `git checkout` | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/sabotagem.log` |
| AT-017 | Gate da cópia do `init --vendors claude` → 2 com o caminho; da fonte → 0 | Pass | `sdd/reports/evidence/F5_CONHECIMENTO/testes-f5.log` |

Os 17 ATs também foram provados por execução pelo avaliador do ciclo 1 (AT-003 e AT-008 com os achados M1–M3, depois resolvidos). O ciclo 2 deu PASS: `sdd/reviews/AVALIACAO_F5_CONHECIMENTO_20261029-ciclo2.md`.

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F5_CONHECIMENTO_20261029.md`. As 8 notas estão no Advisor Ledger do DESIGN v1.1: todas APPLIED, a H1 em parte (o `.gitattributes` só cobre `fontes/`).

**Veredito do avaliador:** NEEDS_WORK — ciclo 1 sobre `7e5b25c`, `sdd/reviews/AVALIACAO_F5_CONHECIMENTO_20261029-ciclo1.md`.

Revisão pós-build por avaliador em contexto fresco, numa worktree destacada. Resultado: 0 HIGH, 3 MEDIUM, 6 LOW. Cada nota foi reproduzida, e o teste correspondente ficou vermelho antes da correção (`baseline-notas.log`).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| M1 | post-build | `kb-dominios.py` lia a linha KB Domains do arquivo inteiro | MEDIUM | APPLIED | Só o `## Technical Context` conta: `test_linha_fora_do_technical_context_nao_conta`, `test_nenhum_em_outra_secao_nao_esconde_o_technical_context`; DEFINE v1.4 (AT-008). `0e0dba5` |
| M2 | post-build | O RULE_MAP derivado do exemplo caía como "caso bom REJEITADO" | MEDIUM | APPLIED | O gate confere o RULE_MAP antes dos casos: `test_rule_map_derivado_do_exemplo_aponta_o_rule_map` |
| M3 | post-build | 2 dos 5 gatilhos do AT-003 sem teste | MEDIUM | APPLIED | `test_caso_bom_rejeitado_e_vermelho`, `test_rejeitado_por_outro_motivo_e_vermelho` |
| L1 | post-build | A saída do caso anterior vazava para a falha | LOW | APPLIED | `projeto()` apaga `$T/saida`; assert no `test_ancora_ausente…` |
| L2 | post-build | `sdd/kb` ilegível dava traceback | LOW | APPLIED | `test_sdd_kb_ilegivel_e_1_sem_traceback` |
| L3 | post-build | `--strict` aceitava `teste` fora da raiz | LOW | APPLIED | `test_teste_fora_da_raiz_reprova`; DEFINE v1.4 (AT-005) |
| L4 | post-build | Regex do texto da skill com caixa e sem `./`/`../` | LOW | APPLIED | sem caixa (`re.I`) e com um ou mais prefixos `./`/`../` no `TextoDaSkill` |
| L5 | post-build | `≥3 abertas` não conferia quais | LOW | APPLIED | `test_perguntas_de_fato_sao_abertas` por pergunta; `test_pergunta_so_o_que_muda_a_experiencia` |
| L6 | post-build | A linha `🛑` da cópia gerada sem o caminho | LOW | APPLIED | `$0` na mensagem; assert no `test_recusa_a_copia_gerada_pelo_init` |

Depois das notas, o Verify Gate rodou de novo em `0e0dba5` e ficou verde, com 495 testes.

**Veredito do avaliador:** PASS — ciclo 2 sobre `0e0dba5`, `sdd/reviews/AVALIACAO_F5_CONHECIMENTO_20261029-ciclo2.md`.

O 2º avaliador reproduziu os 9 achados contra o commit (todos RESOLVIDO) e desfez cada correção numa cópia (15 de 15 mutações reversas pegas). Achou 3 LOW novos, todos nas correções e todos fechando em vermelho.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| LOW-1 | post-build (ciclo 2) | Pasta de domínio ilegível dava traceback; BOM antes de `## Technical Context` escondia a seção | LOW | APPLIED | `test_dominio_ilegivel_nao_da_traceback`, `test_bom_no_inicio_nao_esconde_a_secao`. `7e19462` |
| LOW-2 | post-build (ciclo 2) | `kb_normativo.py` quebrado aparecia como "RULE_MAP não bate" | LOW | APPLIED | `test_kb_normativo_quebrado_tem_diagnostico_proprio` |
| LOW-3 | post-build (ciclo 2) | Link simbólico dentro do projeto para fora reprovava como "fora da raiz" | LOW | APPLIED | Contenção pela forma do caminho (`normpath`): `test_link_dentro_do_projeto_para_fora_passa` |

Depois do ciclo 2, o Verify Gate rodou em `7e19462` e ficou verde, com 499 testes. As notas LOW do ciclo 2 não abriram um ciclo 3, como na F4.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | A pergunta do `como-falar.md` do starter, quebrada em 2 linhas, não é vista pelo `skill-lint` | A pergunta em negrito fica numa linha só | Nenhum: achado antes do commit |
| 2 | O exemplo normativo vem `PENDENTE DE REVISÃO`, e o caso positivo do `--strict` reprovaria | A cópia do caso troca a linha do revisor; o gate passou a 4 aceitas (DEFINE v1.2) | +1 caso aceito |
| 3 | O validador genérico da skill de design varre chaves e a sigla de "a definir" até em código | O DESIGN descreve as linhas com chaves em prosa | Nenhum: o `design-lint` do open e o validador saem 0 |
| 4 | A sabotagem do `kb_normativo.py` não deixou nenhum teste vermelho | Teste novo `RuleMapCheck` (`7e5b25c`) | +1 commit |
| 5 | Uma verificação rápida rodada sem `-B` criou `sdd/bin/__pycache__` | Apagado antes do commit; tudo roda com `-B` | Nenhum |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Decision 7: a regra "No fecho da fase…" fica no bloco da `sdd-kb` (DESIGN v1.2) | Correção de build, registrada no DESIGN | O bloco é idêntico nas 14 | O bloco comum fica igual nas 15 |
| Decisions 2, 3 e 4 ajustadas pelas notas dos ciclos 1 e 2 (DESIGN v1.3 e v1.4; DEFINE v1.4) | Revisões de contexto fresco pedidas pelo Roberto; nenhuma decisão do Brainstorm reaberta | 3 MEDIUM e 9 LOW reproduzidos | Lint por seção, o RULE_MAP conferido primeiro, contenção do `teste` |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed
- [x] Incremental verification recorded
- [x] Verify Gate green or manual-ux receipt positive
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified
- [x] LLM prompt receipts complete when required
- [x] Drift decisions recorded
- [x] Advisor findings disposed when applicable
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation

---

## Next Step

Execute o **SDD Handoff by RDD**.
