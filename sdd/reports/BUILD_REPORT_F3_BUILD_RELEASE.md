# BUILD REPORT: F3 Build e Release do sdd-open

> Implementation report for F3 Build e Release do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F3_BUILD_RELEASE |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md` |
| **DEFINE** | `sdd/features/DEFINE_F3_BUILD_RELEASE.md` |
| **DESIGN** | `sdd/features/DESIGN_F3_BUILD_RELEASE.md` (v1.1) |
| **Status** | Complete |

Branch `feat/incorporar-starter`, commits `8c1a593` (build), `af8b0e3` (teste de contrato fora de git) e `1a54da5` (notas da revisão pós-build), sobre `41c6169` = `v2.2.2`. Fonte do porte: `/Users/robertoduarte/rdd-public/sdd-starter` em `17c69c4`; amostras de workflow em `/Users/robertoduarte/RDD/Wordpress/.github/workflows/`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 14 (4 novos, 10 alterados) |
| Cross-file coupling | High — lint → template → referência → `sdd-build`; script → `sdd-release` → teste de contrato; `MANIFEST.txt` tocado pelos novos |
| Security surface | Baixa — leitura de workflows e de relatórios; nenhum segredo, rede ou escrita fora do projeto; fixtures anonimizadas |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Baixo — cadeia de dependência quase linear |
| Context-rot risk | Médio — sessão longa (Brainstorm → Build); mitigado pelos artefatos e pela revisão de contexto fresco |
| Runtime capabilities | default e ralph (subagentes) disponíveis; briefs não oferecido |

**Recommendation:** default — dependências lineares e contexto das fontes já carregado; mesmo modo da F1 e da F2.

**User decision:** default (Roberto, 2026-10-29).

**Pre-build review:** No — Roberto escolheu "só pós-build": o DESIGN foi validado em 2 checkpoints do Brainstorm.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 14/14 |
| **Files Created** | 4 |
| **Files Modified** | 10 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 40 (gate 3×, suíte no piso 3×, 23 logs por AT, sabotagem 2×, baseline vermelho 4×, casos do revisor 3×, scripts contra os 2 repos reais 2×) |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Testes: 304 (242 de antes + 62 novos), 0 skip, verdes no `/usr/bin/python3` 3.9.6 com `/bin/bash` 3.2.57 e no `python3` 3.15 do PATH dentro do gate.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1 | Modify `sdd/bin/report-lint.py` | direct | Complete | `python3 -B -m unittest test_report_lint` | 32 OK; 14 antigos intactos |
| 2 | 2 | Modify `sdd/templates/BUILD_REPORT_TEMPLATE.md` | direct | Complete | `test_contrato_build_release.TemplateEPlaybook` | OK |
| 3 | 3 | Modify `sdd/templates/fragments/EVIDENCIA.md` | direct | Complete | leitura + publish-gate G5 | OK |
| 4 | 4 | Modify `sdd/playbook.md` (`LM-004`) | direct | Complete | `bash sdd/bin/playbook-lint.sh sdd/playbook.md` · `--self-test` | 0 · 0 |
| 5 | 5 | Create `.agents/skills/sdd-build/references/aplicar-migration.md` | direct | Complete | `test_contrato_build_release.SddBuild` | OK |
| 6 | 6 | Modify `.agents/skills/sdd-build/SKILL.md` (2.1.0) | direct | Complete | `skill-lint.py` · `SddBuild` | 0 · OK |
| 7 | 7 | Create `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` | direct | Complete | `test_deploy_espera_testes` + raiz do open (SIM) + Wordpress (NAO) | 29 OK |
| 8 | 8 | Modify `.agents/skills/sdd-release/SKILL.md` (2.2.0) | direct | Complete | `skill-lint.py` · `SddRelease` | 0 · OK |
| 9 | 9 | Modify `bin/sdd-open.sh` (`doctor`) | direct | Complete | `test_sdd_open -k doctor` | 8 OK |
| 10 | 10 | Modify `tests/test_report_lint.py` | direct | Complete | baseline vermelho contra o lint de `41c6169` | 17 FAIL → 0 |
| 11 | 11 | Create `tests/test_deploy_espera_testes.py` | direct | Complete | baseline vermelho dos testes da revisão contra o script de `af8b0e3` | 13 FAIL → 0 |
| 12 | 12 | Modify `tests/test_sdd_open.py` | direct | Complete | baseline vermelho contra o `sdd-open.sh` de `af8b0e3` | 1 FAIL → 0 |
| 13 | 13 | Create `tests/test_contrato_build_release.py` | direct | Complete | na cópia de `git archive` (sem `.git`) | 12 OK |
| 14 | 14 | Modify `MANIFEST.txt` | direct | Complete | `LC_ALL=C sort -c` · publish-gate G3 | 0 · verde |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `sdd/bin/report-lint.py` | Modify | 1 | Yes | +152/−16: `problema_do_log()` extraída sem mudar mensagens; `ler_layers_sql`, `migrations_listadas`, `linhas_migrations`, `prova_migration`, `check_migrations` |
| `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | 2 | Yes | Seção condicional de migrations depois de Files Created |
| `sdd/templates/fragments/EVIDENCIA.md` | Modify | 3 | Yes | Parágrafo "Migration aplicada" |
| `sdd/playbook.md` | Modify | 4 | Yes | `LM-004`, `promovido_para: sdd/bin/report-lint.py` |
| `.agents/skills/sdd-build/references/aplicar-migration.md` | Create | 5 | Yes | 206 linhas; sem `sdd/ambiente.md`; CNPJ literal virou `<valor de teste>`; seção 6 com log `MIG-nnn.log` ou recibo |
| `.agents/skills/sdd-build/SKILL.md` | Modify | 6 | Yes | 2.0.0 → 2.1.0; passo 4b |
| `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` | Create | 7 | Yes | 423 linhas, `100755`, só stdlib; mini-parser de YAML |
| `.agents/skills/sdd-release/SKILL.md` | Modify | 8 | Yes | 2.1.0 → 2.2.0; item 7 = bloco único do OK; 0a.5 e item 10 citam a regra e o script |
| `bin/sdd-open.sh` | Modify | 9 | Yes | `versao_skill`, `versao_menor`, bloco de atraso no `doctor` |
| `tests/test_report_lint.py` | Modify | 10 | Yes | Classe `Migrations` (18 testes); timestamp montado em tempo de execução (G2) |
| `tests/test_deploy_espera_testes.py` | Create | 11 | Yes | 29 testes; fixtures inline anonimizadas; `release.yml` real como SIM |
| `tests/test_sdd_open.py` | Modify | 12 | Yes | 3 testes de `doctor` |
| `tests/test_contrato_build_release.py` | Create | 13 | Yes | 12 testes de contrato |
| `MANIFEST.txt` | Modify | 14 | Yes | 110 → 114 linhas |

Nada de `sdd/bin/verify-gate.sh`, `sdd/fixtures/`, `scripts/publish-gate*` ou `.github/` mudou (`evidence/F3_BUILD_RELEASE/AT-022.log`). Esta feature não tem migration de banco, então o relatório não precisa da seção de migrations.

---

## Drift Detected

No drift detected. Nenhum arquivo fora do manifest; nenhum prompt de runtime. As mudanças de comportamento vindas da revisão estão em Deviations from Design e no DESIGN v1.1.

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline antes de tocar no código | `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` em `41c6169` | Pass | `evidence/F3_BUILD_RELEASE/baseline.log`: 242 OK |
| Regra de migration discrimina | testes `Migrations` contra o `report-lint.py` de `41c6169` | Pass | 17 FAIL no lint antigo, 0 no novo |
| Script contra repositórios reais | `deploy-espera-testes.py .` · `… /Users/robertoduarte/RDD/Wordpress` | Pass | `SIM` (needs: testes → 'Unit tests') · `NAO` (deploy-hostinger.yml · job deploy-production, passo 'Sync theme patch') |
| Casos do revisor | `scratchpad/de_casos.py` (15 casos) depois de `1a54da5` | Pass | 0 SIM falso; 1, 2, 4, 5, 7, 9 → NAO; 3, 6, 8, 10, 11 → NAO_SEI |
| `doctor` no bash 3.2 | `versao_skill` com aspas simples, duplas e sem aspas | Pass | `2.0.0`, `2.1.0`, `1.4.2` |
| Versões | `python3 -B scripts/check-versions.py --base v2.2.2 --base-obrigatoria` | Pass | `evidence/F3_BUILD_RELEASE/AT-021.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F3_BUILD_RELEASE.md` |
| **Exit / Result** | 0 em `1a54da5` (G1–G5 verdes, `Ran 304 tests … OK`) |
| **Status** | Green |
| **Evidence** | `evidence/F3_BUILD_RELEASE/GATE.log`; a 1ª rodada (`8c1a593`) saiu vermelha — `GATE-1-vermelho.log`, ver Issues |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` (no publish-gate e em `test_skill_lint`) | Pass | `evidence/F3_BUILD_RELEASE/AT-022.log` |
| Typecheck | N/A (Python sem anotação verificada; bash sem typecheck) | N/A | — |
| Tests | `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` | Pass | `evidence/F3_BUILD_RELEASE/suite-piso.log` |
| Build / Compile | `bash -n` dos `.sh` e publish-gate em modo ci | Pass | `evidence/F3_BUILD_RELEASE/AT-020.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | Migration com linha válida (nome · ref, data, log `$ `) → exit 0 | Pass | `evidence/F3_BUILD_RELEASE/AT-001.log` |
| AT-002 | Migration sem linha (ou sem a seção) → 🛑 com o caminho; títulos numerados e com prefixo contam | Pass | `evidence/F3_BUILD_RELEASE/AT-002.log` |
| AT-003 | Prova vazia, declarativa, "exit 0", log inexistente/de outra feature/sem `$ ` → exit 1 | Pass | `evidence/F3_BUILD_RELEASE/AT-003.log` |
| AT-004 | Projeto sem `nome · ref` (inclusive `— · —`) ou sem data → exit 1 | Pass | `evidence/F3_BUILD_RELEASE/AT-004.log` |
| AT-005 | Recibo vale com gate `test`; "já aplicada em" vale como data | Pass | `evidence/F3_BUILD_RELEASE/AT-005.log` |
| AT-006 | `layers.sql` preenchido conta; vazio usa só o glob fixo | Pass | `evidence/F3_BUILD_RELEASE/AT-006.log` |
| AT-007 | Ação Delete e relatório sem migration não exigem a seção | Pass | `evidence/F3_BUILD_RELEASE/AT-007.log` |
| AT-008 | Os 14 contratos antigos do `report-lint` continuam verdes | Pass | `evidence/F3_BUILD_RELEASE/AT-008.log` |
| AT-009 | `release.yml` do open → SIM por `needs:` | Pass | `evidence/F3_BUILD_RELEASE/AT-009.log` |
| AT-010 | Workflow real que publica sem teste → NAO com arquivo e job; instalar ferramenta de teste não é testar | Pass | `evidence/F3_BUILD_RELEASE/AT-010.log` |
| AT-011 | `continue-on-error`, `\|\| true`, `set +e … exit 0`, pipe sem pipefail, `if: always()` (passo, job, job do meio) → NAO | Pass | `evidence/F3_BUILD_RELEASE/AT-011.log` |
| AT-012 | `continue-on-error` só fora do teste + lint → SIM; lint sozinho não é teste | Pass | `evidence/F3_BUILD_RELEASE/AT-012.log` |
| AT-013 | `workflow_run`, reutilizável, YAML ilegível, teste com `if:`, `set +e`, job "deploy" não reconhecido → NAO_SEI | Pass | `evidence/F3_BUILD_RELEASE/AT-013.log` |
| AT-014 | Sem workflows / só testa / só PR → NAO_SE_APLICA; argumento inválido → 64 | Pass | `evidence/F3_BUILD_RELEASE/AT-014.log` |
| AT-015 | `doctor` com skill mais velha → ⚠️ com as duas versões e o remédio, exit 0 | Pass | `evidence/F3_BUILD_RELEASE/AT-015.log` |
| AT-016 | `doctor` com `sdd/bin/` diferente → ⚠️; em dia → ✅; `RESULTADO:` e exit 0 | Pass | `evidence/F3_BUILD_RELEASE/AT-016.log` |
| AT-017 | Contrato escrito da `sdd-release` 2.2.0 (bloco, script, uma pergunta) | Pass | `evidence/F3_BUILD_RELEASE/AT-017.log` |
| AT-018 | Contrato escrito da `sdd-build` 2.1.0 e da referência | Pass | `evidence/F3_BUILD_RELEASE/AT-018.log` |
| AT-019 | Template com a seção; `LM-004` no `## Sempre` e playbook válido | Pass | `evidence/F3_BUILD_RELEASE/AT-019.log` |
| AT-020 | publish-gate em modo ci verde na árvore da F3 | Pass | `evidence/F3_BUILD_RELEASE/AT-020.log` |
| AT-021 | `check-versions --base v2.2.2 --base-obrigatoria` → 0 | Pass | `evidence/F3_BUILD_RELEASE/AT-021.log` |
| AT-022 | Não regressão: diff vazio em verify-gate/fixtures/publish-gate/.github; 59 testes de verify-gate, skill-lint, playbook-lint e CLI | Pass | `evidence/F3_BUILD_RELEASE/AT-022.log` |
| AT-023 | 3 sabotagens com teste nomeado vermelho e verde depois do `git checkout` | Pass | `evidence/F3_BUILD_RELEASE/AT-023.log` |

Sabotagens (AT-023, rodadas em `1a54da5`, script em `evidence/F3_BUILD_RELEASE/sabotagem.sh`, `sed` por padrão):

| Script | Quebra | Teste que ficou vermelho | Depois do `git checkout` |
|---|---|---|---|
| `sdd/bin/report-lint.py` | migration sem linha em `## Migrations aplicadas` vira `pass` | `test_migration_sem_linha_reprova`, `test_migration_sem_a_secao_reprova` e mais 2 (+4 subtests de títulos) | 32 OK |
| `deploy-espera-testes.py` | `continue-on-error` do passo de teste deixa de contar | `test_continue_on_error_no_passo_de_teste_nao_segura` | 29 OK |
| `bin/sdd-open.sh` | `doctor` deixa de comparar `sdd/bin/` (`cmp` → `continue`) | `test_doctor_avisa_sdd_bin_diferente_do_pacote` | 20 OK |

---

## Advisor Ledger

Revisão pós-build por avaliador de contexto fresco (subagente sem a conversa do build), sobre `af8b0e3`. Veredito: **FIX FIRST** — 1 HIGH, 6 MEDIUM, 6 LOW; 23 de 23 ATs PASS. Os casos de reprodução dele (`scratchpad/de_casos.py`, `rl_casos.py`) foram rodados aqui antes de cada decisão.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | post-build | Linha que só cita a ferramenta (`pip install … pytest`, `npm install --save-dev jest`, `make test-deps`) contava como teste ⇒ SIM falso | HIGH | APPLIED | Reproduzido (casos 1, 2, 11 → SIM). `comando_de_teste()`: ferramenta em posição de comando, linha de instalação descartada. `test_instalar_a_ferramenta_de_teste_nao_e_testar`, `test_alvo_de_make_que_comeca_com_test_nao_e_teste` vermelhos no script antigo. Commit `1a54da5` |
| 2 | post-build | `if:` do passo de teste ignorado (teste só em PR antes do deploy ⇒ SIM) | MEDIUM | APPLIED | Caso 3 reproduzido. Teste com `if:` que não seja `always()`/`success()` ⇒ NAO_SEI. `test_teste_com_if_nao_garante_e_nao_sei` |
| 3 | post-build | Só o `if:` do 1º passo que publica era conferido | MEDIUM | APPLIED | Caso 4 reproduzido. Todo passo que publica é conferido. `test_if_always_em_qualquer_passo_que_publica_nao_segura` |
| 4 | post-build | `if: always()` num job do meio do `needs:` ignorado | MEDIUM | APPLIED | Caso 5 reproduzido. A busca não atravessa job com `always()` sem teste próprio. `test_if_always_num_job_do_meio_do_needs_nao_segura` |
| 5 | post-build | Um SIM escondia publicador não reconhecido (deploy por ssh, `docker/build-push-action`) | MEDIUM | APPLIED | Casos 8 e 9 reproduzidos. `push-action` publica; job com nome de deploy/publish/release sem passo reconhecido ⇒ NAO_SEI. `test_job_com_nome_de_deploy_nao_reconhecido_impede_o_sim`, `test_acao_que_faz_push_de_imagem_publica` |
| 6 | post-build | `set +e` sem `exit 0` final e `pytest \| tee` sem pipefail ⇒ SIM | MEDIUM/LOW | APPLIED | Casos 6, 7 reproduzidos. `set +e` ⇒ NAO_SEI; pipe sem `shell: bash`/`pipefail` ⇒ NAO. `test_set_e_sem_exit_0_no_fim_e_nao_sei`, `test_pipe_sem_pipefail_nao_segura_e_shell_bash_segura` |
| 7 | post-build | Workflow só com `workflow_call` avaliado sozinho ⇒ NAO onde o AT-013 pede NAO_SEI | LOW | APPLIED | Caso 10 reproduzido. Só-`workflow_call` não é avaliado; quem chama dá NAO_SEI. `test_workflow_so_de_workflow_call_e_avaliado_por_quem_chama` |
| 8 | post-build | `OSError` (pasta `.yml`, symlink quebrado) dava traceback com exit 1, sem `RESULTADO:` | LOW | APPLIED | `except (Ilegivel, OSError)`. `test_arquivo_que_nao_abre_e_nao_sei_com_resultado` vermelho no script antigo |
| 9 | post-build | `report-lint` não via `## 2. Arquivos criados …` nem `## Fase A — Files …` (relatórios reais com 3 migrations cada passavam) | MEDIUM | APPLIED | `FILES_SEC_RE` aceita número ou prefixo com travessão. `test_titulos_reais_numerados_ou_com_prefixo_contam` vermelho no lint antigo |
| 10 | post-build | Escolhas contornáveis: caminho sem crases, 2º caminho na linha, célula "removido" em qualquer coluna, projeto `— · —` | LOW | APPLIED (só `— · —`) / REBUTTED (resto) | `— · —` reprova: `test_projeto_so_com_travessoes_reprova`. O resto é a Decisão 1 do DESIGN (1º token entre crases; ação em qualquer célula) e o próprio revisor mediu 1 linha afetada em 250 relatórios reais |
| 11 | post-build | "exit 0" entre parênteses com log válido reprova; teste pgTAP `*.sql` vira migration | LOW | REBUTTED | Contrato do DEFINE: "exit 0" na célula é negado mesmo com log (como declaração em `test_declaracao_nega_mesmo_com_log_valido_na_celula`); `*.sql` = migration é a decisão 1 do Brainstorm. pgTAP fica como pendência |
| 12 | post-build | A referência prometia que "aplicada com sucesso"/"deve estar lá" reprovam, e não reprovam | LOW | APPLIED | Texto corrigido: só `exit 0` e declaração reprovam; o lint não lê o log |
| 13 | post-build | `doctor` lia `version: '2.0.0'` (aspas simples) como "sem versão" | LOW | APPLIED | `versao_skill` aceita aspas simples; `test_doctor_em_dia_com_o_pacote` vermelho no `sdd-open.sh` antigo |

Depois das notas, o Verify Gate rodou de novo em `1a54da5`: verde, 304 testes.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | Timestamp de migration de 14 dígitos nos testes casa o padrão de 11+ dígitos seguidos do G2 | Montado em tempo de execução (`TS = "2026" + "1029" + "120000"`) | Nenhum — achado antes do commit |
| 2 | 1º gate vermelho em `8c1a593`: `test_lm_004_no_sempre_e_playbook_valido` rodava o `playbook-lint.sh` na raiz, e a cópia do gate (`git archive`) não tem `.git` (exit 64 "não é um repo git") | Lint rodado numa sandbox com `git init` (`af8b0e3`); conferido numa cópia de `git archive` | +1 ciclo de gate |
| 3 | `FONTE_PKG_SKILLS` só existe no `init`; o `doctor` saía com "unbound variable" | `$PKG/.agents/skills` direto no `doctor` | Nenhum — achado na verificação incremental |
| 4 | O sinal "nome fala em publicar" pegou o "Run publish gate" do próprio open e o job `testes` do `release.yml` | Só id/nome do job; nome do workflow só sem job reconhecido; exclui `…-gate`/`-check`/`-lint` | Nenhum — achado antes do commit das notas |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Decisão 4 endurecida (teste em posição de comando, `if:` em todos os passos que publicam e nos jobs do meio, pipe sem pipefail, `set +e`, `if:` no teste, nomes de deploy não reconhecidos, `workflow_call`, `OSError`) — DESIGN v1.1 | Revisão de contexto fresco escolhida pelo Roberto; notas aplicadas sem mudar o contrato do DEFINE | 11 SIM falsos reproduzidos; o DEFINE (AT-011, AT-013) e a docstring prometiam "na dúvida, NAO_SEI, nunca SIM" | Mais casos caem em NAO_SEI; o agente lê os workflows e escreve "não consegui afirmar" |
| Decisão 1: títulos numerados e com prefixo — DESIGN v1.1 | idem | Relatórios reais do Wordpress com 3 migrations passavam sem prova | Nenhum relatório real a mais reprova por engano |

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
