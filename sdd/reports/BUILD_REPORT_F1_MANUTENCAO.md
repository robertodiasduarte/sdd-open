# BUILD REPORT: F1 Manutenção do sdd-open

> Implementation report for F1 Manutenção do sdd-open

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F1_MANUTENCAO |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F1_MANUTENCAO.md` |
| **DEFINE** | `sdd/features/DEFINE_F1_MANUTENCAO.md` (v1.1) |
| **DESIGN** | `sdd/features/DESIGN_F1_MANUTENCAO.md` (v1.1) |
| **Status** | Complete |

Branch `feat/incorporar-starter`, base `80d7887`; commits `3db1686` (build), `9db642b` (teste que a sabotagem pediu), `f75fbdb` (achados da revisão). Worktree `sdd-open-incorporar-starter`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 18 |
| Cross-file coupling | High — 9 suítes dependem do mesmo `tests/apoio.py` e das mesmas convenções (sem literal de PII, `python3 -B`, bash 3.2) |
| Security surface | Workflow com `contents: write` e padrões do gate anti-vazamento |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Baixo: os testes são independentes entre si, mas todos dependem do helper |
| Context-rot risk | Médio: 18 arquivos, contexto único suficiente |
| Runtime capabilities | default disponível; ralph possível via subagente; briefs não usado |

**Recommendation:** default — o acoplamento pelo helper comum e as convenções pesam mais que contexto limpo por tarefa.

**User decision:** default (Roberto, 2026-10-29).

**Pre-build review:** No — Roberto escolheu revisão pós-build só na superfície de escrita (`release.yml` + `next-version.sh`).

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 18/18 |
| **Files Created** | 13 |
| **Files Modified** | 5 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 31 (suítes por arquivo, suíte inteira no 3.9 e no 3.15, `bash -n`, check-versions, next-version no repo real, 6 sabotagens com reversão, Verify Gate 2×) |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Suíte final: **115 testes** em 9 arquivos, verdes no Python 3.9.6 (`/usr/bin/python3`) e no 3.15, com o `/bin/bash` 3.2.57 do macOS.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1 | Create `tests/apoio.py` | direct | Complete | importado pelas 9 suítes | todas rodam |
| 2 | 2 | Create `tests/test_verify_gate.py` | direct | Complete | `unittest -p test_verify_gate.py` | 23 OK |
| 3 | 3 | Create `tests/test_report_lint.py` | direct | Complete | `unittest -p test_report_lint.py` | 14 OK |
| 4 | 4 | Create `tests/test_skill_lint.py` | direct | Complete | `unittest -p test_skill_lint.py` | 8 OK |
| 5 | 5 | Create `tests/test_playbook_lint.py` | direct | Complete | `unittest -p test_playbook_lint.py` | 8 OK |
| 6 | 6 | Create `tests/test_sdd_open.py` | direct | Complete | `unittest -p test_sdd_open.py` | 12 OK (1ª rodada: 1 falha por premissa errada, corrigida) |
| 7 | 7 | Create `scripts/check-versions.py` | direct | Complete | `check-versions.py --base v2.2.0 --base-obrigatoria` | vermelho antes da tarefa 13, verde depois |
| 8 | 8 | Create `tests/test_check_versions.py` | direct | Complete | `unittest -p test_check_versions.py` | 16 OK |
| 9 | 9 | Create `scripts/next-version.sh` | direct | Complete | `/bin/bash scripts/next-version.sh` no repo real | `TAG=v2.2.1 NEW=1 BASE=v2.2.0` |
| 10 | 10 | Create `tests/test_next_version.py` | direct | Complete | `unittest -p test_next_version.py` | 12 OK |
| 11 | 11 | Modify `scripts/publish-gate-patterns.txt` | direct | Complete | grep dos 3 padrões em `git ls-files` | 0 hits |
| 12 | 12 | Create `tests/test_publish_gate_patterns.py` | direct | Complete | `unittest -p test_publish_gate_patterns.py` | 5 OK |
| 13 | 13 | Modify `.agents/skills/sdd-auditoria-harness/SKILL.md` | direct | Complete | `check-versions.py` + `skill-lint.py` | verde |
| 14 | 14 | Create `.github/workflows/release.yml` | direct | Complete | `test_release_workflow.py` + revisão fresca | 17 OK |
| 15 | 15 | Create `tests/test_release_workflow.py` | direct | Complete | `unittest -p test_release_workflow.py` | 17 OK |
| 16 | 16 | Modify `.github/workflows/publish-gate.yml` | direct | Complete | `test_release_workflow.py` (classe PublishGate) | OK |
| 17 | 17 | Modify `CONTRIBUTING.md` | direct | Complete | G5 do publish-gate | verde |
| 18 | 18 | Modify `MANIFEST.txt` | direct | Complete | G3 do publish-gate na cópia limpa | "tree and manifest match in both directions" |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `tests/apoio.py` | Create | 1 | Yes | `PYTHON = sys.executable`; `SDD_TEST_BASH` escolhe o bash |
| `tests/test_verify_gate.py` | Create | 2 | Yes | 6 exits, `--print`, `--strict`, `contains:`, 403, veredito declarado, fixtures canônicas |
| `tests/test_report_lint.py` | Create | 3 | Yes | inclui o caso que a sabotagem exigiu |
| `tests/test_skill_lint.py` | Create | 4 | Yes | limite 1024 testado nas duas bordas |
| `tests/test_playbook_lint.py` | Create | 5 | Yes | fixtures + `--anti-collapse` + `--self-test` |
| `tests/test_sdd_open.py` | Create | 6 | Yes | init, init 2×, sync, `--check`, AGENTS.md, doctor |
| `scripts/check-versions.py` | Create | 7 | Yes | 0/1/64; `--root`, `--base`, `--base-obrigatoria` |
| `tests/test_check_versions.py` | Create | 8 | Yes | repos com tag real |
| `scripts/next-version.sh` | Create | 9 | Yes | bash 3.2; tag empurrada como argumento; recusa HEAD atrás da última tag |
| `tests/test_next_version.py` | Create | 10 | Yes | ordem por versão, tag no HEAD, rc, re-run velho |
| `scripts/publish-gate-patterns.txt` | Modify | 11 | Yes | +3 ERE |
| `tests/test_publish_gate_patterns.py` | Create | 12 | Yes | amostras concatenadas em runtime |
| `.agents/skills/sdd-auditoria-harness/SKILL.md` | Modify | 13 | Yes | só `version: "1.0.0"` no frontmatter |
| `.github/workflows/release.yml` | Create | 14 | Yes | 2 jobs; publicação real conferida só depois do merge |
| `tests/test_release_workflow.py` | Create | 15 | Yes | leitura estática dos dois workflows |
| `.github/workflows/publish-gate.yml` | Modify | 16 | Yes | `permissions`, `fetch-depth: 0`, 2 steps; steps existentes intocados |
| `CONTRIBUTING.md` | Modify | 17 | Yes | testes, bump de versão, Release com hash |
| `MANIFEST.txt` | Modify | 18 | Yes | +13 linhas, ordem C mantida |

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `tests/test_sdd_open.py` | Brainstorm e Design diziam que o `init` copia só `sdd/templates`, `sdd/bin` e `sdd/playbook.md`; o `aplicar()` de `bin/sdd-open.sh` também copia `sdd/fixtures/` na 1ª instalação, de propósito | revise spec (premissa corrigida; decisão de `tests/` na raiz continua válida) | teste afirma o comportamento real; `sdd/fixtures/**` entrou nos paths do produto; DEFINE v1.1 e DESIGN v1.1 |
| 2 | `scripts/next-version.sh`, `.github/workflows/*.yml` | Revisão pós-build achou 5 falhas de desenho na release | approved deviation (dentro da intenção do DESIGN) | ver Advisor Ledger; DESIGN v1.1 |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Suíte por arquivo | `/usr/bin/python3 -B -m unittest discover -s tests -p test_<arquivo>.py -v` | Pass | `evidence/F1_MANUTENCAO/suite-*.log` (9 arquivos) |
| Suíte inteira, Python 3.9.6 | `/usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` | Pass | 115 testes OK |
| Suíte inteira, Python 3.15 | `python3 -B -m unittest discover -s tests -p 'test_*.py'` | Pass | 106 testes OK antes da revisão; 115 dentro do Verify Gate final |
| Sintaxe shell | `bash -n` em todo `*.sh` | Pass | nenhuma falha |
| Versões | `/usr/bin/python3 -B scripts/check-versions.py --base v2.2.0 --base-obrigatoria` | Pass | 13 skills coerentes |
| Próxima versão | `/bin/bash scripts/next-version.sh` | Pass | `TAG=v2.2.1 NEW=1 BASE=v2.2.0` |
| Sabotagem | `sdd/reports/evidence/F1_MANUTENCAO/sabotagem.sh` | Pass | 6 de 6 vermelhos nomeados, 6 de 6 verdes após `git checkout` |
| Não regressão | `git diff --stat 80d7887 -- sdd/fixtures sdd/bin bin scripts/publish-gate.sh` | Pass | saída vazia |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F1_MANUTENCAO.md` (cmd: `git archive HEAD` em mktemp → `publish-gate.sh` modo ci → `unittest discover` na cópia) |
| **Exit / Result** | 0 |
| **Status** | Green |
| **Evidence** | `evidence/F1_MANUTENCAO/AT-001.log` — HEAD `f75fbdb`; G1–G5 verdes; 115 testes OK; `RESULTADO: VERDE` |

### Manual UX Receipt

N/A

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md` | Pass | `test_as_13_skills_reais_passam` |
| Typecheck | N/A | N/A | projeto sem typecheck |
| Tests | suíte inteira em 3.9 e 3.15 | Pass | ver Incremental Verification |
| Build / Compile | `bash -n` e smoke do gerador (`test_sdd_open.py`) | Pass | `suite-sdd_open.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | Suíte na cópia limpa, sem rede e sem gitconfig de quem roda | Pass | `evidence/F1_MANUTENCAO/AT-001.log` |
| AT-002 | verify-gate: exits 0, 2, 3, 4, 5, 64 | Pass | `evidence/F1_MANUTENCAO/suite-verify_gate.log` |
| AT-003 | `--strict` mapeia 3/4/5 para 1 e preserva 0/2/64 | Pass | `evidence/F1_MANUTENCAO/suite-verify_gate.log` |
| AT-004 | `--print` sai 0 mesmo com marcador | Pass | `evidence/F1_MANUTENCAO/suite-verify_gate.log` |
| AT-005 | `contains:` presente 0, ausente 2 | Pass | `evidence/F1_MANUTENCAO/suite-verify_gate.log` |
| AT-006 | report-lint aceita log, avaliação e recibo em manual-ux | Pass | `evidence/F1_MANUTENCAO/suite-report_lint.log` |
| AT-007 | report-lint nega declaração, arquivo ausente, log vazio; sem argumento 64 | Pass | `evidence/F1_MANUTENCAO/suite-report_lint.log` |
| AT-008 | skill-lint reprova sem frontmatter, name ≠ pasta, description > 1024 | Pass | `evidence/F1_MANUTENCAO/suite-skill_lint.log` |
| AT-009 | skill-lint sai 0 nas 13 skills reais | Pass | `evidence/F1_MANUTENCAO/suite-skill_lint.log` |
| AT-010 | playbook-lint: fixtures, `--anti-collapse`, `--self-test` | Pass | `evidence/F1_MANUTENCAO/suite-playbook_lint.log` |
| AT-011 | sdd-open: verbo, opção e init fora de git saem 64 | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-012 | init cria a estrutura e sai 0 | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-013 | sync idempotente e `--check` em dia | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-014 | `--check` acusa cópia gerada editada | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-015 | sync preserva texto do usuário no AGENTS.md | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-016 | doctor termina em RESULTADO e sai 0 | Pass | `evidence/F1_MANUTENCAO/suite-sdd_open.log` |
| AT-017 | check-versions passa com versões coerentes e bump | Pass | `evidence/F1_MANUTENCAO/suite-check_versions.log` |
| AT-018 | check-versions reprova sem bump, versão ausente/malformada, manifest divergente | Pass | `evidence/F1_MANUTENCAO/suite-check_versions.log` |
| AT-019 | base obrigatória que não resolve reprova | Pass | `evidence/F1_MANUTENCAO/suite-check_versions.log` |
| AT-020 | CPF, CNPJ e telefone BR pegos; datas e versões não | Pass | `evidence/F1_MANUTENCAO/suite-publish_gate_patterns.log` |
| AT-021 | next-version soma um patch, ordem por versão | Pass | `evidence/F1_MANUTENCAO/suite-next_version.log` |
| AT-022 | HEAD já com tag publica essa tag | Pass | `evidence/F1_MANUTENCAO/suite-next_version.log` |
| AT-023 | release só depois dos testes; escrita só no job release | Pass | `evidence/F1_MANUTENCAO/suite-release_workflow.log` |
| AT-024 | Release publicada com tarball e SHA256SUMS que confere (pós-merge, run 40876615567 → `v2.2.1` em `f75fbdb`) | Pass | `evidence/F1_MANUTENCAO/AT-024.log` |
| AT-025 | Fixtures 5/0/64 e scripts existentes intocados | Pass | `evidence/F1_MANUTENCAO/nao-regressao.log` |
| AT-026 | Sabotagem deixa teste nomeado vermelho e a reversão volta ao verde | Pass | `evidence/F1_MANUTENCAO/AT-026.log` |

Sabotagens (AT-026), uma por script, todas revertidas com `git checkout`:

| Script | Sabotagem | Teste que ficou vermelho |
|---|---|---|
| `sdd/bin/verify-gate.sh:82` | marcador ativo sai 2 em vez de 5 | `test_5_marcador_ativo_fora_de_fence`, `test_strict_remapeia_3_4_5_para_1`, `test_fixtures_canonicas` |
| `sdd/bin/report-lint.py:62` | "deve funcionar" deixa de ser negado | `test_declaracao_nega_mesmo_com_log_valido_na_celula` |
| `sdd/bin/skill-lint.py:98` | limite 1024 → 2048 | `test_description_com_1025_caracteres_reprova` |
| `sdd/bin/playbook-lint.sh:159` | formato inválido sai 0 | `test_fixture_invalida_reprova_com_2`, `test_self_test_passa` |
| `bin/sdd-open.sh:342` | cópia desatualizada não conta como divergente | `test_check_acusa_copia_gerada_editada_a_mao` |
| `scripts/check-versions.py:83` | `<=` vira `<` (mesma versão passa) | `test_skill_mudada_sem_bump_reprova` |

---

## Advisor Ledger

Revisão pós-build em contexto fresco (subagente sem a conversa de construção), escopo `release.yml`, `next-version.sh`, steps novos do `publish-gate.yml`. Veredito: FIX FIRST.

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | post-build | Push de tag não-semver (`v2.3.0-rc1`) ou commit com duas tags publicava outra versão | HIGH | APPLIED | gatilho `v[0-9]+.[0-9]+.[0-9]+`; `next-version.sh vX.Y.Z` publica a tag empurrada; testes `test_tag_pedida_*`, `test_so_tag_vxyz_dispara` |
| 2 | post-build | Re-run de commit antigo publicava conteúdo velho como latest + 1 | MEDIUM | APPLIED | `git merge-base --is-ancestor` quando NEW=1; `test_head_que_nao_descende_da_ultima_tag_e_1` |
| 3 | post-build | Grupo único de fila: push de main cancelava run pendente de tag | MEDIUM | APPLIED | `group: release-` + ref; `test_fila_por_ref_sem_cancelar` |
| 4 | post-build | `publish-gate.yml` sem `permissions:` | LOW | APPLIED | `permissions: contents: read`; `PublishGate.test_token_so_le` |
| 5 | post-build | Job `testes` da release roda menos checks que o publish-gate | LOW | APPLIED em parte | copiado o step de sintaxe/zsh/symlink; os demais checks inline já são cobertos pela suíte. REBUTTED a parte "mover para script": mexeria nos steps existentes do `publish-gate.yml`, que esta frente mantém intocados |

Verify Gate repetido depois das correções: verde em `f75fbdb` (`AT-001.log`).

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | Sabotagem do `report-lint` passaria verde: célula com "deve funcionar" e sem caminho reprovava por outro motivo | teste novo isola a regra (`9db642b`); sabotagem refeita e pega | lacuna real de cobertura fechada |
| 2 | `test_sem_plantio_o_g2_nao_acusa` acusava a própria linha verde "no forbidden pattern matched" | assert passou a procurar `pattern matched:` | só no teste |
| 3 | Testes de workflow liam os comentários que citam `continue-on-error` e `contents: write` | asserts aplicados só às linhas de YAML | só no teste |
| 4 | Subprocessos Python usavam o `python3` do PATH (3.15) mesmo com a suíte no 3.9 | `PYTHON = sys.executable` | a rodada no 3.9 agora testa os linters no 3.9 |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| `sdd/fixtures/**` nos paths que disparam a Release | Registrada (DEFINE v1.1) | o `init` entrega as fixtures ao usuário | mudar fixture também publica |
| `next-version.sh` com argumento opcional e regra de ancestralidade; fila por ref; step extra no job `testes`; `permissions` no `publish-gate.yml` | Escolha do Roberto por revisão pós-build; notas aplicadas | Advisor Ledger 1–5 | release mais restrita, mesmo fluxo |
| `tests/apoio.py` com `SDD_TEST_BASH` e `PYTHON = sys.executable` | Sem pergunta (detalhe de teste) | cobrir o piso bash 3.2 e Python 3.9 de verdade | nenhum no produto |

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
- [x] Acceptance Tests verified (AT-024 conferido depois do merge: Release `v2.2.1`, `shasum -a 256 -c` OK)
- [x] LLM prompt receipts complete when required
- [x] Drift decisions recorded
- [x] Advisor findings disposed when applicable
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation

---

## Next Step

Execute o **SDD Handoff by RDD**.
