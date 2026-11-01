# BUILD REPORT: F9 Fluxo encadeado e decisões

> Implementation report for F9 Fluxo encadeado e decisões

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F9_FLUXO |
| **Date** | 2026-10-31 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F9_FLUXO.md` |
| **DEFINE** | `sdd/features/DEFINE_F9_FLUXO.md` (v1.6) |
| **DESIGN** | `sdd/features/DESIGN_F9_FLUXO.md` (v1.1) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F9_FLUXO.md` (7 MUST de texto) |
| **Status** | Complete |

- **Branch:** `feat/f9-fluxo`, sobre `7c640eb` (= `v2.2.9`).
- **Commits:** `bb91c42` — build (88 linhas do manifest, 87 arquivos; a linha 35 não tinha o que mudar); `524f957` — notas do ciclo 1 da revisão de contexto fresco do build (1 HIGH, 2 MEDIUM, 12 LOW); `daf9c0f` — notas do ciclo 2 (1 HIGH, 1 MEDIUM, 4 LOW).
- **Escopo:** números do `git diff --shortstat v2.2.9 HEAD` em `sdd/reports/evidence/F9_FLUXO/escopo.log`.
- **Fontes (só leitura):** `origin/main` do repositório privado (`1b1c1d41b`): `scripts/sdd-fluxo.sh`, `scripts/sdd-decisoes-lint.sh`, `.claude/sdd/templates/fragments/FLUXO_ENCADEADO.md`, 2 `ledger-review.md` e o `archive/DOGFOOD_20260824/` (forma das fixtures). Nada foi alterado lá.
- **Revisões de contexto fresco:**
  - do DESIGN, antes do build: `sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md` (NEEDS_WORK: 3 HIGH, 2 MEDIUM, 10 LOW; as 15 aplicadas no DESIGN v1.1 e no DEFINE v1.3);
  - do build: ver `## Contrato de aceite (C2) e avaliador de contexto fresco (C1)`.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 88 linhas: 39 novos (2 scripts, 1 fragmento, 32 fixtures, 2 testes, 2 docs) e 49 alterados (15 `SKILL.md`, 15 exemplos de pergunta, fragmento, template, config, 7 testes, workflow, docs) |
| Cross-file coupling | Alto: as marcas e os rótulos são lidos do fragmento pelo lint; a linha de transição, o recibo e a parada do exit 40 aparecem no script, no fragmento e nas skills |
| Security surface | `despachar` grava um arquivo com nome validado (`^[A-Za-z0-9_-]+$`); nenhum script lê credencial; a evidência do Codex copia `auth.json` só para um `CODEX_HOME` temporário apagado no fim |
| LLM prompt items | None (`LLM Prompts: false`) |
| Independent volume | Médio (2 scripts + texto de 15 skills), com vocabulário comum |
| Context-rot risk | Alto: a sessão foi do brainstorm ao build. Mitigado pelos artefatos, pela revisão do DESIGN em contexto fresco (3 HIGH antes do código) e pelos rascunhos testados numa cópia descartável antes de entrar na worktree |
| Runtime capabilities | default e subagente disponíveis; briefs não oferecido |

**Recommendation:** default.

**User decision:** default. O Roberto pediu "grave o brainstorm, depois execute o define, ux-review, design, review do design, build, review do build"; o modo foi registrado, não perguntado.

**Pre-build review:** Sim, a revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 3 HIGH, 2 MEDIUM, 10 LOW; todas aplicadas antes do build; os 5 ajustes de contrato ACEITOS no DEFINE v1.3).

---

## Summary

| Metric | Value |
|---|---|
| Scripts novos | `sdd/bin/sdd-fluxo.sh` (bash 3.2 + Python stdlib embutido: `review-design`, `loop`, `despachar`, `seguir`, `estado`, `--self-test`) e `sdd/bin/sdd-decisoes-lint.sh` (`--sites`, `--self-test`) |
| Fragmentos | `FLUXO_ENCADEADO.md` (novo); `PERGUNTA_DECISAO.md` item 9 com a tabela das 6 marcas e o `estado` |
| Skills | 15 sobem de versão: 9 minor com a subseção `### Fluxo encadeado` (brainstorm 2.2.0, define 2.4.0, governanca 2.3.0, ux-review 2.4.0, design 2.2.0, build 2.4.0, iterate 2.2.0, release 2.5.0, new-session 1.3.0) e 6 patch só com a marca (auditoria-harness 1.1.1, checar-ambiente 1.4.1, handoff 2.1.1, kb 2.2.1, playbook 2.1.1, prompt-builder 2.1.1) |
| Itens do PORTE | F1 (encadeamento), F2 (classes + lint), F3 (recibo), F6 (`[auto]` no design, só com o encadeamento ligado), F7 (`sdd-fluxo.sh`), F8 (pontuação forte/fraco no define), F10 (tipos de entrada no brainstorm), F11 (UX reviews anteriores) |
| Slots | `flow.autonomous: false`, `review.security_globs: ""` |
| Testes | 683 → 744 no piso (`test_fluxo.py` 48, `test_decisoes_lint.py` 11, +2 em `test_docs`/`test_release_workflow`; `test_conversa` estendido; 5 pinos de versão) |
| Fixtures | 27 em `sdd/fixtures/fluxo/`, 5 em `sdd/fixtures/conversa/decisoes/` |
| Docs | `docs/chained-flow.md` + PT (novos), roadmap EN/PT sem a linha (5 linhas), READMEs, `cli-conventions.md`, seção Advisor Ledger no `DESIGN_TEMPLATE.md` |
| Release | `v2.2.10` automática (decisão do Roberto no brainstorm) |

---

## Task Execution

| # | Task | Status | Evidence |
|---|---|---|---|
| 1 | `sdd-fluxo.sh` (rascunho testado numa cópia do pacote, depois na worktree) | Done | `sdd/reports/evidence/F9_FLUXO/self-test-fluxo.log` |
| 2 | `sdd-decisoes-lint.sh` | Done | `sdd/reports/evidence/F9_FLUXO/self-test-decisoes-lint.log` |
| 3–4 | `PERGUNTA_DECISAO.md` item 9, `FLUXO_ENCADEADO.md` | Done | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| 5–30, 80–85 | Fixtures de `sdd/fixtures/fluxo/` e `conversa/decisoes/` | Done | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| 31, 86 | Slots no `config.example.yaml`; Advisor Ledger no template | Done | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| 32–64 | 15 skills: subseção, marcas, F6/F8/F10/F11, despacho, versões | Done | `sdd/reports/evidence/F9_FLUXO/decisoes-lint-sites.log` |
| 35 | `sdd-governanca/manifest.json` 2.3.0 | N/A | o arquivo não tem campo de versão (Drift 1) |
| 65–72, 87–88 | Workflow e testes tocados | Done | `sdd/reports/evidence/F9_FLUXO/testes-contratos-tocados.log` |
| 73–79 | Docs e `MANIFEST.txt` (234 → 273) | Done | `sdd/reports/evidence/F9_FLUXO/escopo.log` |

---

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `sdd/bin/sdd-fluxo.sh` | Created | os 5 verbos e o `--self-test` |
| `sdd/bin/sdd-decisoes-lint.sh` | Created | `--sites` e `--self-test` |
| `sdd/templates/fragments/FLUXO_ENCADEADO.md` | Created | contrato do encadeamento |
| `sdd/templates/fragments/PERGUNTA_DECISAO.md` | Modified | item 9 com as 6 marcas |
| `sdd/templates/DESIGN_TEMPLATE.md` | Modified | seção Advisor Ledger |
| `sdd/config.example.yaml` | Modified | `flow.autonomous`, `review.security_globs` |
| `sdd/fixtures/fluxo/*` (27), `sdd/fixtures/conversa/decisoes/*` (5) | Created | os dois lados de cada exit e motivo |
| `.agents/skills/*/SKILL.md` (15), `references/como-falar.md` (14), `entrevista-publico.md`, `contexto-fresco.md`, `sdd-kb/CHANGELOG.md` | Modified | subseção, marcas, itens do PORTE, versões |
| `tests/test_fluxo.py`, `tests/test_decisoes_lint.py` | Created | contratos |
| `tests/test_conversa.py`, `test_docs.py`, `test_release_workflow.py`, `test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_matriz_new_session.py` | Modified | tabela das marcas, roadmap, passo de CI, pinos de versão |
| `.github/workflows/publish-gate.yml` | Modified | passo "Decision classes and chained flow" |
| `docs/chained-flow.md`, `docs/pt-BR/chained-flow.md` | Created | o mecanismo |
| `docs/roadmap.md` + PT, `docs/cli-conventions.md`, `README.md`, `README.pt-BR.md`, `MANIFEST.txt` | Modified | linha removida, exits, links, 39 arquivos novos |

---

## Drift Detected

| # | Drift | Decision |
|---|---|---|
| 1 | `sdd-governanca/manifest.json` não tem campo de versão (o DESIGN previa o bump) | Nada a mudar; `check-versions` verde |
| 2 | Com `--disable multi_agent`, o Codex 0.163 ainda abriu um colaborador (`collab: Wait`) e seguiu o degrau 1 da escada (A-003 falsa) | A 1ª execução ficou como `codex-despacho-subagente.log` (prova do degrau 1); a 2ª leva a condição "sem subagente nem colaborador" no prompt e exercita o degrau 2 (DEFINE v1.4) |
| 3 | O transcript do Codex escreve o exit do comando como `exited 40`, não `[exit=40]` | O AT-031 passa a ler o formato do transcript (DEFINE v1.4) |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Base antes de tocar em nada | suíte inteira no piso em `7c640eb` | Pass | 683 OK, `sdd/reports/evidence/F9_FLUXO/suite-base.log` |
| Baseline vermelha | os 2 testes novos na árvore `v2.2.9` | Pass (vermelho esperado) | `sdd/reports/evidence/F9_FLUXO/baseline.log` |
| Baseline das notas do ciclo 1 | os testes das correções contra `bb91c42` | Pass (vermelho esperado: 13 em `test_fluxo`, 1 em `test_decisoes_lint`) | `sdd/reports/evidence/F9_FLUXO/baseline-ciclo1.log` |
| Baseline das notas do ciclo 2 | os testes das correções contra `524f957` | Pass (vermelho esperado: 12 falhas em 4 testes) | `sdd/reports/evidence/F9_FLUXO/baseline-ciclo2.log` |
| `sdd-fluxo.sh`, verbo por verbo | `test_fluxo.py` (48) | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| `sdd-decisoes-lint.sh` | `test_decisoes_lint.py` (11) | Pass | `sdd/reports/evidence/F9_FLUXO/testes-decisoes-lint.log` |
| Contratos tocados | conversa, docs, contrato_build_release, correcoes_w0, matriz_new_session, release_workflow, agnóstico, bash32, skill_lint | Pass | `sdd/reports/evidence/F9_FLUXO/testes-contratos-tocados.log` |
| Verdade conhecida do `review-design` | porte × fonte nos 8 DESIGNs F1–F8 | Pass (8/8 iguais) | `sdd/reports/evidence/F9_FLUXO/review-design-8.log` |
| Diferencial do `loop` | 3 casos de borda, porte × fonte | Pass (10/10/10) | `sdd/reports/evidence/F9_FLUXO/loop-diferencial.log` |
| Evidência da F9 (logs do build) | `gate-shell-evidencia.sh` sem os `AVAL*` | Pass | `sdd/reports/evidence/F9_FLUXO/shell-da-f9.log` |
| Pasta inteira | `gate-shell-evidencia.sh sdd/reports/evidence/F9_FLUXO` | Pass | `sdd/reports/evidence/F9_FLUXO/shell-da-f9-pasta-inteira.log` |
| Guard antes de cada avaliador | `avaliador-guard.sh` com os 4 prefixos | Pass | `sdd/reports/evidence/F9_FLUXO/guard-antes-do-avaliador.log` |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F9_FLUXO.md`. O `cmd` faz a cópia por `git archive HEAD`, roda o `publish-gate.sh` em modo `ci` e a suíte no piso |
| **Exit / Result** | 0 em `bb91c42` (735 testes), `524f957` (741) e `daf9c0f` (`Ran 744 tests … OK`; publish-gate GREEN) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F9_FLUXO/GATE.log`, `GATE-ciclo1.log`, `GATE-ciclo2.log` |

### Manual UX Receipt

AT-030 e AT-031 são execuções reais do Codex CLI 0.163 numa cópia commitada, com `CODEX_HOME` e `HOME` temporários (só o `auth.json`): validado por SDD Build by RDD em 2026-10-31, resultado **PASS** nos dois (`codex-define-autonomo.log`, `codex-despacho-40.log`; o critério e a conferência estão no fim de cada log).

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `skill-lint.py --conversa` (17) | Pass | `sdd/reports/evidence/F9_FLUXO/skill-lint-conversa.log` |
| Classes | `sdd-decisoes-lint.sh --sites .agents/skills sdd/templates/fragments` (17 perguntas) | Pass | `sdd/reports/evidence/F9_FLUXO/decisoes-lint-sites.log` |
| Versões | `check-versions.py --base v2.2.9 --base-obrigatoria` | Pass | `sdd/reports/evidence/F9_FLUXO/check-versions.log` |
| bash 3.2 | `grep` de bashismos nos 2 scripts, sem achado nem em comentário | Pass | `sdd/reports/evidence/F9_FLUXO/bash32.log` |
| Tamanho | `wc -l` | Pass | `sdd/reports/evidence/F9_FLUXO/linhas.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Sabotagem | `sabotagem.sh`, 8 mutações (2 do ciclo 2) | Pass | `sdd/reports/evidence/F9_FLUXO/sabotagem.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | `review-design` EXIGIDO por ≥ 3 novos (fixtures rastreadas); 8 DESIGNs reais = fonte | Pass | `sdd/reports/evidence/F9_FLUXO/review-design-8.log` |
| AT-002 | Termo fixo, glob do slot e `layers.sql` exigem | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-003 | DISPENSAVEL sai 1 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-004 | Manifest ilegível sai 64 com o default seguro | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-005 | `loop` PRONTO | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-006 | CONTINUAR por cada causa; precedência da fonte | Pass | `sdd/reports/evidence/F9_FLUXO/loop-diferencial.log` |
| AT-007 | BLOQUEADO D4 teto, D4 ciclos, D5 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-008 | AGUARDANDO_RECIBO e recibo com data | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-009 | Entrada ausente ou malformada sai 64, nunca 0 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-010 | `--log` com o exit real; `\| tee` acusado | Pass | `sdd/reports/evidence/F9_FLUXO/self-test-fluxo.log` |
| AT-011 | `despachar` 40 com o brief, os rótulos e o retorno | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-012 | `despachar` 64 sem gravar nada | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-013 | `seguir` 0 com a linha de transição e a concordância | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-014 | `seguir` 1 por cada motivo | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-015 | `seguir` 64 e slot inválido | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-016 | Sem `python3`, 64 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-017 | `--self-test` numa cópia sem `.git` | Pass | `sdd/reports/evidence/F9_FLUXO/self-test-fluxo.log` |
| AT-018 | `--sites` verde: 15 nas skills, 2 nos fragmentos | Pass | `sdd/reports/evidence/F9_FLUXO/decisoes-lint-sites.log` |
| AT-019 | Cada regra reprova pelo motivo certo | Pass | `sdd/reports/evidence/F9_FLUXO/testes-decisoes-lint.log` |
| AT-020 | 64 sem caminho, sem pergunta, sem tabela | Pass | `sdd/reports/evidence/F9_FLUXO/testes-decisoes-lint.log` |
| AT-021 | `--self-test` do lint | Pass | `sdd/reports/evidence/F9_FLUXO/self-test-decisoes-lint.log` |
| AT-022 | Item 9 com as 6 marcas e o `estado` | Pass | `sdd/reports/evidence/F9_FLUXO/testes-contratos-tocados.log` |
| AT-023 | `FLUXO_ENCADEADO.md` com o contrato | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-024 | Subseção igual nas 9, dentro do Encerramento | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-025 | Os 2 slots com default | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-026 | Despacho com exit 40 nas 3 skills | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-027 | F6, F8, F10, F11 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |
| AT-028 | Passo de CI; `check-versions` | Pass | `sdd/reports/evidence/F9_FLUXO/check-versions.log` |
| AT-029 | 683 anteriores, publish-gate ci, contratos | Pass | `sdd/reports/evidence/F9_FLUXO/GATE.log` |
| AT-030 | Codex: `sdd-define` encadeada termina na linha de transição | Pass | `sdd/reports/evidence/F9_FLUXO/codex-define-autonomo.log` |
| AT-031 | Codex sem subagente: despacho sai 40 com o brief gravado | Pass | `sdd/reports/evidence/F9_FLUXO/codex-despacho-40.log` |
| AT-032 | 6 sabotagens; testes novos vermelhos na `v2.2.9` | Pass | `sdd/reports/evidence/F9_FLUXO/sabotagem.log` |
| AT-033 | `estado` 0/1/64 | Pass | `sdd/reports/evidence/F9_FLUXO/testes-fluxo.log` |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** contagem impossível neste repositório (sem `sdd/config.yaml`); o avaliador roda mesmo assim.
**Contrato de aceite (passo 1.5 da `sdd-build`):** 5 propostas / 5 aceitas — `## Contrato de aceite` do DESIGN.
**Veredito do avaliador (C1):** NEEDS_WORK · ciclos: 2 · achados: 15 (ciclo 1: 1 HIGH, 2 MEDIUM, 12 LOW) + 6 (ciclo 2: 1 HIGH, 1 MEDIUM, 4 LOW) · `AVALIACAO_F9_FLUXO_20261031-ciclo2.md`

Os 21 achados foram aplicados (`524f957` e `daf9c0f`), menos a metade "só dígitos" do LOW 14 do ciclo 1 (rebatida), cada um com teste dos dois lados e baseline vermelha no commit anterior (`baseline-ciclo1.log`, `baseline-ciclo2.log`). O HIGH do ciclo 2 foi uma regressão introduzida pela correção de um LOW do ciclo 1 (a faixa `[A-Za-z]` do `case` segue o locale UTF-8), coberta agora por teste nos locales C, en_US.UTF-8 e pt_BR.UTF-8 e por uma sabotagem. As correções do ciclo 2 **não** passaram por um 3º avaliador: a `sdd-build` limita a 2 ciclos, e a decisão de abrir um 3º é do Roberto (ver Final Status).

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md`. As 15 notas estão no Advisor Ledger do DESIGN v1.1, todas APPLIED.

**Revisão do build (pós-build):** avaliador em contexto fresco, numa worktree destacada, com o guard verde antes de cada despacho (`guard-antes-do-avaliador.log`, `guard-antes-do-avaliador-ciclo2.log`). Ciclo 1 sobre `bb91c42`: `sdd/reviews/AVALIACAO_F9_FLUXO_20261031-ciclo1.md` (NEEDS_WORK; 31 ATs PASS, AT-010 FAIL, AT-030/031 NAO_VERIFICADO por brief).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | ciclo 1 | `loop --log` não regravava o log no exit 64; o log antigo ficava como prova falsa | HIGH | APPLIED | `cmd_loop` captura stdout/stderr e grava em toda saída, criando a pasta; `test_log_e_regravado_mesmo_quando_sai_64_e_cria_a_pasta`. `524f957` |
| 2 | ciclo 1 | `seguir design` seguia com HIGH aberto num Ledger sem coluna de severidade reconhecida | MEDIUM | APPLIED | `Sev` reconhecida; sem coluna, PARAR; `test_ledger_sem_coluna_de_severidade_para`. `524f957` |
| 3 | ciclo 1 | O exit 40 pedia de volta só a linha `VEREDITO`, mas a build grava o bloco inteiro e usa os achados no ciclo 2 | MEDIUM | APPLIED | retorno do avaliador = bloco `<<<AVALIACAO … >>>` no script, no 5d e no degrau 2; DEFINE AT-011 e UX U5 revistos. `524f957` |
| 4 | ciclo 1 | `review-design` lia File Manifest de exemplo em bloco cercado | LOW | APPLIED | cercas viram linhas vazias antes da busca; `test_manifest_de_exemplo_em_bloco_cercado_nao_conta`. `524f957` |
| 5 | ciclo 1 | `despachar` aceitava nome com quebra de linha | LOW | APPLIED | `nome_ok` por `case`; 2 casos novos em `test_erros_saem_64_e_nada_e_gravado`. `524f957` |
| 6 | ciclo 1 | Caminho do `--log` no fragmento sem `sdd/reports/`; pasta ausente sem log | LOW | APPLIED | fragmento corrigido; `--log` cria a pasta. `524f957` |
| 7 | ciclo 1 | Contrato do `seguir` no fragmento sem Status, kind/cmd e Ledger | LOW | APPLIED | `FLUXO_ENCADEADO.md` completo; `test_fluxo_encadeado_tem_o_contrato`. `524f957` |
| 8 | ciclo 1 | Exemplo da parada ⏸️ com o brief em outro lugar | LOW | APPLIED | `sdd/reports/briefs/BRIEF_avaliador_PAGAMENTOS.md`. `524f957` |
| 9 | ciclo 1 | Passo 1 da `sdd-design` citava "proposta de verificabilidade do avaliador", inexistente; sem dizer a marca com o encadeamento desligado | LOW | APPLIED | "ajustes do contrato de aceite da revisão do DESIGN"; desligado, perguntas com `[auto · de rotina]`. `524f957` |
| 10 | ciclo 1 | `--recibo` com só a data ou com data inexistente | LOW | APPLIED | `recibo_valido` (nome + data do calendário); `test_recibo_exige_nome_e_data_que_existe`. `524f957` |
| 11 | ciclo 1 | `contexto-fresco.md` dizia "sem recibo, tratar como NEEDS_WORK" | LOW | APPLIED | linha do `PASS_PENDENTE_RECIBO` com o exit 30. `524f957` |
| 12 | ciclo 1 | Fora de git, o motivo culpava o Verify Gate | LOW | APPLIED | PARAR "a pasta não é um repositório git…"; `test_fora_de_git_o_motivo_e_o_git`. `524f957` |
| 13 | ciclo 1 | Concordância dos motivos ("UX REVIEW não encontrado") | LOW | APPLIED | `test_motivo_com_a_concordancia_do_documento`. `524f957` |
| 14 | ciclo 1 | Lint não pegava SHA em maiúsculas nem só com dígitos | LOW | APPLIED em parte | maiúsculas pegas (caso novo em `test_cada_regra_reprova_pelo_motivo_certo`); só dígitos REBUTTED: um número de 7 dígitos pode ser um valor legítimo na pergunta, e a regra 5 fala de identificador, não de número. `524f957` |
| 15 | ciclo 1 | Classificação das perguntas da `sdd-design` e da `sdd-iterate` trocada entre o DESIGN e o código | LOW | APPLIED | DESIGN corrigido para o implementado (design D2: onde a pessoa guarda os dados muda o produto; iterate auto: atualizar o DESIGN junto é rotina) |
| N1 | ciclo 2 | `despachar` aceitava nome com letra acentuada em locale UTF-8 (regressão do ciclo 1: a faixa `[A-Za-z]` do `case` segue a ordenação do locale no bash 3.2) | HIGH | APPLIED | lista explícita de caracteres, sem faixa; `test_nome_acentuado_sai_64_em_locale_utf8` (C, en_US.UTF-8, pt_BR.UTF-8); sabotagem. `daf9c0f` |
| N2 | ciclo 2 | `seguir design` não via HIGH escrito `**HIGH**`, entre crases ou com emoji | MEDIUM | APPLIED | célula limpa de `*`, crase e `_`, `\bHIGH\b`; `test_severidade_formatada_e_ledger_de_exemplo_cercado`; sabotagem. `daf9c0f` |
| N3 | ciclo 2 | `--teto ²` passava no `isdigit()` e quebrava com traceback; log antigo ficava; `--log` que não grava saía 0 | LOW | APPLIED | inteiro por regex; erro interno vira 64 com o log regravado; log que não grava é 64; `test_erro_interno_e_log_que_nao_grava_saem_64`. `daf9c0f` |
| N4 | ciclo 2 | Sem `python3`, o `--log` antigo ficava no lugar | LOW | APPLIED | `precisa_python` grava o log do 64; caso novo em `test_sem_python3_todo_verbo_sai_64`. `daf9c0f` |
| N5 | ciclo 2 | `ledger()` lia um Advisor Ledger de exemplo em bloco cercado | LOW | APPLIED | cercas viram linhas vazias antes da busca; mesmo teste do N2. `daf9c0f` |
| N6 | ciclo 2 | Passo 1 da `sdd-design` citava o modo `contrato` sem dizer onde ele está | LOW | APPLIED | aponta `sdd-build/references/contexto-fresco.md`. `daf9c0f` |

---

## Issues Encountered

| Issue | Resolution |
|---|---|
| `verify-gate.sh --print` sai 64 fora de um repositório git (medido no Design) | O `--self-test` do `seguir` monta um repositório temporário com `git init -q` |
| `cp X X` sai 1 no macOS: o brief já no destino faria o despacho falhar (achado da revisão do DESIGN) | `[ "$BRIEF" -ef "$DESTINO" ]` pula a cópia; teste com caminho relativo e absoluto, mtime intacto |
| A substituição do Advisor Ledger no DESIGN casou com a 1ª ocorrência do título, citado no texto da Decision 5 | Âncora com quebra de linha (`\n## Advisor Ledger\n`); nada chegou a ser gravado com o recorte errado |
| O `grep` de bashismo acusava um comentário que citava a palavra `mapfile` | Comentário reescrito; 0 achados |

---

## Deviations from Design

| Deviation | Reason |
|---|---|
| Linha 35 do manifest (`manifest.json` da governança) sem mudança | Drift 1 |
| AT-031 com a condição "sem subagente" no prompt | Drift 2 |

---

## Blockers

Nenhum.

---

## Final Status

### Overall: COMPLETE

- [x] Todas as tarefas do manifest concluídas (87/88; a 35 não tinha o que mudar)
- [x] Verify Gate verde (`GATE.log`)
- [x] Testes novos vermelhos na base (`baseline.log`, `baseline-ciclo1.log`, `baseline-ciclo2.log`) e 8 sabotagens com dentes (`sabotagem.log`)
- [x] Nenhum TODO/FIXME como implementação pendente
- [x] Execuções reais no Codex CLI: AT-030 e AT-031 PASS
- [x] Avaliador de contexto fresco do build, ciclo 1: NEEDS_WORK (1 HIGH, 2 MEDIUM, 12 LOW), aplicado em `524f957`
- [x] Ciclo 2 sobre `524f957`: NEEDS_WORK (1 HIGH de regressão, 1 MEDIUM, 4 LOW), aplicado em `daf9c0f`; `AVALIACAO_F9_FLUXO_20261031-ciclo2.md` persistido
- [x] 3º ciclo do avaliador: o Roberto escolheu seguir sem ele (pergunta D4, resposta "OK citando sdd-open", 2026-10-31)
- [x] Release `v2.2.10` (2026-10-31): PR #11 com CI verde em ubuntu e macOS (run 41245908615), push fast-forward `7c640eb..daf9c0f` em `main`; o run `release` 41246920990 **cancelou** o job de testes do Ubuntu no `timeout-minutes: 10` (744 testes levam ~12 min) e não publicou. Correção `89ac76f` (teto 25 min no `release.yml`), PR #12 com CI verde, OK do Roberto ("autorizado sdd-open"), push `daf9c0f..89ac76f` e tag `v2.2.10` em `89ac76f`; run `release` 41251612805 verde nos 3 jobs → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.10; `sdd-open-v2.2.10.tar.gz` SHA-256 `209e086bfd57f650da5f9b281732eaf9bb2ee350daf1978914c8a179aceb330a` conferido com `shasum -a 256 -c`

---

## Next Step

Execute o **SDD Handoff by RDD**.
