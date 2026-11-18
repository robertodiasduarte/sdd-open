# BUILD REPORT: F12 Contexto, patterns e governança

> Implementation report for F12 Contexto, patterns e governança

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F12_CONTEXTO |
| **Date** | 2026-11-03 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F12_CONTEXTO.md` |
| **DEFINE** | `sdd/features/DEFINE_F12_CONTEXTO.md` (v1.4, 26 ATs) |
| **DESIGN** | `sdd/features/DESIGN_F12_CONTEXTO.md` (v1.2, 18 decisões, 87 linhas no manifest) |
| **Status** | Complete |

- **Branch:** `feat/f12-contexto`, sobre `9508ff0` (= `v2.3.1`).
- **Commits:** `fb77fa7` build · `a57fde6` avaliador ciclo 1 · `0f51ac9` avaliador ciclo 2 · `89702c4` revisão real, rodada 1 · `363d8bc` rodada 2 · `0ca09f9` rodada 3 (D4: 4ª rodada) · `d816f77` rodada 4 · `3ebeeea` rodada 5 · `96a97ec` snapshot fora do `.git` (achado pela prova no Codex) · `6b7633c` teto do macOS no CI. Escopo: `sdd/reports/evidence/F12_CONTEXTO/escopo.log` (90 arquivos: 50 novos, 40 alterados).
- **Fontes (só leitura):** `origin/main` do privado (`f70a7aba9`): `scripts/contexto-lint.sh`, `patterns-lint.sh`, `docs-extract-decisions.sh` (+ `lib/docs-extract-common.sh`), `governanca-fronteira.sh`, os agentes `cartografo-contexto.md` e `revisor-governanca.md`, `WORKFLOW_CONTRACTS.yaml` e as fixtures — portados e generalizados; nada copiado nas fixtures (domínio fictício de pedidos e estoque); o privado não foi alterado.
- **Revisões:** do DESIGN (`sdd/reviews/REVISAO_DESIGN_F12_CONTEXTO_20261103.md`, 16 notas no DESIGN v1.1 e no DEFINE v1.3); do build, ver `## Contrato de aceite (C2) e avaliador de contexto fresco (C1)` e `## Advisor Ledger`.
- **Governança deste DEFINE:** N.A., confirmada por um revisor fresco (triagem independente, nenhum arquivo gravado) antes do Design — a D5 aplicada à própria frente.

---

## Mode Selection

| Signal | Observation |
|---|---|
| Manifest files | 87 linhas (50 arquivos novos e 40 alterados ao fim, com 3 fixtures do ciclo 1 a mais) |
| Cross-file coupling | Alto: o passo 11 da skill, o `verify-gate.sh`, a fronteira, o validador do bloco, o brief e o yaml precisam dizer o mesmo |
| Security surface | Fronteira de escrita de agentes frescos; trava fail-closed do build (exit 5) |
| LLM prompt items | 0 (`LLM Prompts: false`: os briefs são orquestração do método, não prompt de produto) |
| Independent volume | Alto: 5 scripts novos, 3 skills, 3 templates, 35 fixtures, 7 módulos de teste |
| Context-rot risk | Alto: a F12 inteira, do brainstorm à release, numa sessão; mitigado por 2 ciclos do avaliador e 3 rodadas da revisão real |
| Runtime capabilities | default e subagente disponíveis |

**Recommendation:** default.

**User decision:** default — o Roberto pediu "grave o brainstorm e execute o define, ux-review, design, review do design, build, review do build"; o modo foi registrado, não perguntado, como nas F9–F11.

**Pre-build review:** Sim — revisão do DESIGN em contexto fresco, modo contrato (NEEDS_WORK: 2 HIGH, 7 MEDIUM, 7 LOW), aplicada no DESIGN v1.1 e no DEFINE v1.3 antes do código.

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 87/87 |
| **Files Created** | 50 |
| **Files Modified** | 40 |
| **Files Deleted** | 0 |
| **Verification Commands Run** | 9 Verify Gates, 10 baselines vermelhas, 5 sabotagens, 2 provas no Codex CLI (4 vezes), 5 revisões reais |
| **Verify Gate** | Green |
| **Execution Mode** | default |

Peças: `sdd-define` 2.5.0 com o passo 1.5 (cartógrafo fresco: gerar/reusar/pular, até 2 domínios, não trava) e o passo 11 (governança em todo Define, inclusive com `--parar`; marcador gravado antes do despacho; a prova SQL ligada no próprio passo — D8); `verify-gate.sh` com o 2º motivo do exit 5 (GOVERNANÇA NÃO REVISADA, as 2 saídas, ordem marcador → linha → bloco); `sdd/bin/` com `contexto-lint.sh`, `patterns-lint.sh`, `governanca-fronteira.sh`, `governanca-bloco.py` e `docs-extract-decisions.sh`; briefs `cartografo.md` e `revisor.md`; `sdd-design` 2.4.0 (C2, C3, C4, C10, C11); `sdd/patterns/README.md`; `sdd/WORKFLOW_CONTRACTS.yaml`; `despachar` com texto por papel; docs EN/PT; o tema sai do roadmap. Testes: 894 → 992 no piso.

---

## Task Execution

| # | Manifest ID | Task | Executor | Status | Verification | Evidence |
|---:|---:|---|---|---|---|---|
| 1 | 1–17 | `contexto-lint.sh` e fixtures de contexto | direct | Complete | `--self-test`, `test_contexto_lint` | `sdd/reports/evidence/F12_CONTEXTO/at-contexto-lint.log` |
| 2 | 18–29, 48 | `patterns-lint.sh`, fixtures e README de patterns | direct | Complete | `--self-test`, `test_patterns_lint` | `sdd/reports/evidence/F12_CONTEXTO/at-patterns-lint.log` |
| 3 | 30, 65 | `governanca-fronteira.sh` | direct | Complete | `test_governanca_fronteira` | `sdd/reports/evidence/F12_CONTEXTO/at-fronteira.log` |
| 4 | 77, 78 | `governanca-bloco.py` | direct | Complete | `test_governanca_bloco` | `sdd/reports/evidence/F12_CONTEXTO/at-bloco.log` |
| 5 | 31, 66 | `docs-extract-decisions.sh` | direct | Complete | `test_docs_extract_decisions` | `sdd/reports/evidence/F12_CONTEXTO/at-extrator.log` |
| 6 | 32–41, 67, 79–81, 86 | `verify-gate.sh`, fixtures de DEFINE e testes com DEFINE em texto | direct | Complete | `test_governanca_gate`, `test_verify_gate`, `test_verify_gate_trace`, `test_gate_baseline` | `sdd/reports/evidence/F12_CONTEXTO/at-gate.log` |
| 7 | 42, 69 | `sdd-fluxo.sh despachar` por papel | direct | Complete | `test_fluxo.Despachar` | `sdd/reports/evidence/F12_CONTEXTO/at-despachar.log` |
| 8 | 43–47, 49–52, 68, 84, 85 | skills, briefs, templates e yaml | direct | Complete | `test_f12_textos`, `skill-lint`, `sdd-decisoes-lint` | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| 9 | 53, 54, 72, 73 | `init` e `release.yml` | direct | Complete | `test_sdd_open`, `test_release_workflow` | `sdd/reports/evidence/F12_CONTEXTO/at-init.log` |
| 10 | 55–62, 70, 71, 82, 83 | docs, roadmap, READMEs, guia | direct | Complete | `test_docs`, `test_decisoes_lint` | `sdd/reports/evidence/F12_CONTEXTO/at-docs.log` |
| 11 | 74–76, 87 | pinos de versão e `MANIFEST.txt` | direct | Complete | `check-versions`, `test_contrato_build_release`, `test_correcoes_w0` | `sdd/reports/evidence/F12_CONTEXTO/at-pacote.log` |

---

## Files Changed

| File | Action | Manifest ID | Verified | Notes |
|---|---|---:|---|---|
| `sdd/bin/contexto-lint.sh` | Create | 17 | Yes | porte fiel; 7 seções genéricas; `--dominio`/`--playbook`; ref `origin/<branch padrão>`; camadas de `layers:`; ordem do cabeçalho; `superficies:` sem crase e casando arquivo; caminho relativo a subpasta |
| `sdd/bin/patterns-lint.sh` | Create | 29 | Yes | fixture verde com a data do dia; citação só `**Pattern:**` fora de cerca (lista e recuo valem); pattern não citado só avisa no `--design` |
| `sdd/bin/governanca-fronteira.sh` | Create | 30 | Yes | sha256 + `#HEAD`; `-uall`, `--ignored=traditional`; realpath; snapshot fora do worktree; shasum que falha recusa |
| `sdd/bin/governanca-bloco.py` | Create | 77 | Yes | validador do bloco `<<<GOVERNANCA` (achado M7 do DESIGN) |
| `sdd/bin/docs-extract-decisions.sh` | Create | 31 | Yes | um arquivo; lê o disco; data na mesma linha do Status (formato do template do Open) |
| `sdd/bin/verify-gate.sh`, `sdd/bin/sdd-fluxo.sh`, `sdd/bin/gate-baseline.sh` | Modify | 32, 42, 86 | Yes | 2º motivo do exit 5; parada por papel; texto do inconclusivo |
| `sdd/fixtures/contexto/` (17), `sdd/fixtures/patterns/` (11), `sdd/fixtures/DEFINE_FIXTURE_SEM_GOVERNANCA.md` | Create | 1–16, 18–28, 33 | Yes | domínio fictício; 3 fixtures do ciclo 1 a mais |
| 7 fixtures de DEFINE | Modify | 34–40 | Yes | linha `Governança` (a de governança fica `pendente`, de propósito) |
| `.agents/skills/sdd-define/SKILL.md` + `references/cartografo.md` + `references/como-falar.md` | Modify / Create | 43, 45, 46 | Yes | 2.5.0 |
| `.agents/skills/sdd-governanca/SKILL.md` + `references/revisor.md` | Modify / Create | 44, 47 | Yes | 2.4.0 |
| `.agents/skills/sdd-design/SKILL.md`, `sdd-build/SKILL.md`, `sdd-iterate/SKILL.md` | Modify | 51, 84, 85 | Yes | 2.4.0 · 2.5.1 · 2.2.1 |
| `sdd/templates/DEFINE_TEMPLATE.md`, `DESIGN_TEMPLATE.md`, `UX_REVIEW_TEMPLATE.md` | Modify | 41, 49, 50 | Yes | linhas novas; citação; papel em aberto trava |
| `sdd/patterns/README.md`, `sdd/WORKFLOW_CONTRACTS.yaml` | Create | 48, 52 | Yes | — |
| `bin/sdd-open.sh`, `.github/workflows/release.yml` | Modify | 53, 54 | Yes | `init` copia os 2 arquivos sem sobrescrever; filtro da release |
| `docs/context-and-governance.md` + PT; roadmap EN/PT; READMEs; `cli-conventions.md`; `verify-gate-contract.md` + PT; `guia-do-aluno.md` | Create / Modify | 55–62, 82, 83 | Yes | tema sai do roadmap (3 linhas) |
| 7 módulos de teste novos; 10 alterados | Create / Modify | 63–76, 78–81 | Yes | — |
| `MANIFEST.txt` | Modify | 87 | Yes | 353 → 403, igual ao `git ls-files` |

---

## Drift Detected

| # | Task / Path | Drift | Decision | Action |
|---:|---|---|---|---|
| 1 | `sdd/fixtures/contexto/cabecalho-fora-de-ordem.md`, `superficies-com-crase.md`, `superficies-sem-arquivo.md` | 3 fixtures fora do manifest v1.1 | aceito (achados L1 e M3 do avaliador, ciclo 1) | vermelhos novos no `--self-test` |
| 2 | `tests/test_correcoes_w0.py` | o padrão da W0 proibia "CONTEXTO de domínio", que a F12 recoloca de propósito | aceito (o plano manda recolocar) | o padrão continua proibindo a grafia do outro SDD |
| 3 | `tests/test_matriz_new_session.py` | item 76 sem mudança | registrado | o arquivo só fixa a versão da `sdd-new-session`, não tocada |

---

## Verification Results

### Incremental Verification

| Task | Command / Method | Result | Evidence |
|---|---|---|---|
| Baseline da F12 | os 7 módulos novos contra a árvore `v2.3.1` | Pass (vermelho esperado em todos) | `sdd/reports/evidence/F12_CONTEXTO/baseline-v2.3.1.log` |
| Baselines das correções | cada teste novo contra o commit anterior | Pass (vermelho esperado) | `baseline-aval1.log`, `baseline-aval2.log`, `baseline-real1.log` a `baseline-real5.log`, `baseline-codex-sandbox.log`, `baseline-real3-alias.log`; guarda nova do yaml por mutação em `mutacao-exits-yaml.log` |
| Self-tests dos 2 lints | `--self-test` numa cópia commitada do HEAD | Pass | `sdd/reports/evidence/F12_CONTEXTO/self-tests.log` |
| Sabotagens | 5 (uma por script): a checagem removida faz o teste correspondente falhar | Pass | `sdd/reports/evidence/F12_CONTEXTO/sabotagens.log` |
| Logs de evidência | `gate-shell-evidencia.sh sdd/reports/evidence/F12_CONTEXTO` | Pass | pasta inteira (2 sondas minhas viraram `.sonda.txt`, com nota em Issues) |

### Verify Gate

| Attribute | Value |
|---|---|
| **Kind** | test |
| **Command / Method** | `cmd` do DEFINE: cópia por `git archive HEAD`, `publish-gate.sh` em modo `ci`, suíte no piso (`/bin/bash` 3.2, `/usr/bin/python3` 3.9), por `verify-gate.sh --strict` |
| **Exit / Result** | 0 em `0f51ac9` (966), `363d8bc` (978), `0ca09f9` (985), `d816f77` (988), `3ebeeea` (992), `96a97ec` (992) e no commit final `6b7633c` (992); o ciclo 2 do avaliador também rodou o `cmd` literal em `a57fde6` (960, exit 0) |
| **Status** | Green |
| **Evidence** | `sdd/reports/evidence/F12_CONTEXTO/verify-gate-6b7633c.log` |

### Complementary Checks

| Check | Command / Method | Status | Evidence |
|---|---|---|---|
| Lint | `check-versions.py --base v2.3.1 --base-obrigatoria`; `skill-lint --conversa` (17); `sdd-decisoes-lint --sites` (20 perguntas) | Pass | `check-versions.log`, `skill-lint.log`, `decisoes-lint.log` |
| Typecheck | N/A (bash e Python sem anotação verificada) | N/A | — |
| Tests | suíte inteira no piso | Pass | `sdd/reports/evidence/F12_CONTEXTO/verify-gate-6b7633c.log` |
| Build / Compile | grep de bashismos nos 6 scripts; `/bin/bash -n`; `ast.parse` no Python 3.9 | Pass | `sdd/reports/evidence/F12_CONTEXTO/bash32-grep.log` |

---

## Acceptance Test Verification

| ID | Scenario | Status | Evidence |
|---|---|---|---|
| AT-001 | lint do CONTEXTO, 7 classes estáveis, RESULTADO + → | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-contexto-lint.log` |
| AT-002 | `--validade` 0/1/2 e ref `origin/<branch padrão>` | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-contexto-lint.log` |
| AT-003 | `--sugerir`: até 2 domínios, camadas, 1 recomendação; sem mapa ⇒ pular | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-contexto-lint.log` |
| AT-004 | self-tests: vermelhos antes dos verdes, classe certa | Pass | `sdd/reports/evidence/F12_CONTEXTO/self-tests.log` |
| AT-005 | fronteira: FORA em todo caso (sujo, pasta nova, ignorado, apagado, acento, commit, link) | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-fronteira.log` |
| AT-006 | fronteira não verificada ⇒ 64 | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-fronteira.log` |
| AT-007 | `despachar cartografo` e `revisor-governanca` ⇒ 40 com texto por papel | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-despachar.log` |
| AT-008 | passo 1.5 no texto da skill e do brief | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-009 | passo 11: trava antes do despacho, cópia, fronteira, bloco, 2 saídas | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-010 | lacunas: pergunta D2 por lacuna; prova SQL ligada no passo (D8) | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-011 | `PADRAO_AUSENTE` sem contar falha; snapshot refeito | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-012 | 2º motivo do exit 5, texto e → próprios, placeholder, cerca ``` e ~~~ | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-gate.log` |
| AT-013 | exits mantidos; ordem marcador → linha → bloco | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-gate.log` |
| AT-014 | `patterns-lint`, `--design` citado × não citado, data, dias e limite | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-patterns-lint.log` |
| AT-015 | README pulado; pacote e pasta com 2 patterns ⇒ 0 | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-patterns-lint.log` |
| AT-016 | `sdd-design`: C2, C3, C4, C10 | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-017 | C11: papel de surface em aberto trava, só na tabela de Surface Assignment | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-018 | índice de ADR, sufixo b, órfãos, conservação | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-extrator.log` |
| AT-019 | `WORKFLOW_CONTRACTS.yaml` contra scripts, briefs e lint | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-020 | Codex CLI: os 2 despachos ⇒ exit 40, brief na cópia, verify-gate 5 com as 2 saídas | Pass | `sdd/reports/evidence/F12_CONTEXTO/codex-revisor-40.log` |
| AT-021 | `init` copia sem sobrescrever; MANIFEST; `release.yml` | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-init.log` |
| AT-022 | docs EN/PT, roadmap sem a linha, READMEs | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-docs.log` |
| AT-023 | nada específico da RDD; nenhum nome de ferramenta de um agente só | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-textos.log` |
| AT-024 | versões, skill-lint, decisoes-lint | Pass | `sdd/reports/evidence/F12_CONTEXTO/check-versions.log` |
| AT-025 | suíte F1–F11 continua verde | Pass | `sdd/reports/evidence/F12_CONTEXTO/verify-gate-6b7633c.log` |
| AT-026 | `governanca-bloco.py` 0/1/2/64 | Pass | `sdd/reports/evidence/F12_CONTEXTO/at-bloco.log` |

O AT-020 tem dois recibos, `codex-cartografo-40.log` (AT-020a) e `codex-revisor-40.log` (AT-020b), ambos sobre o commit final `96a97ec`, com a linha `exited 40` do transcript do Codex; as execuções anteriores ficaram em `codex-fb77fa7/`, `codex-0f51ac9/` e `codex-3ebeeea-falso-pass/` (ver Issues).

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** este repositório não tem `sdd/config.yaml`; o avaliador rodou mesmo assim.
**Contrato de aceite:** 16 notas da revisão do DESIGN, aplicadas no DESIGN v1.1 e no DEFINE v1.3 (Advisor Ledger do DESIGN).
avaliador: PASS · ciclos: 2 · `sdd/reviews/AVALIACAO_F12_CONTEXTO_20261103-ciclo2.md`
**Veredito do avaliador (C1):** ciclo 1 NEEDS_WORK (3 MEDIUM, 6 LOW; `sdd/reviews/AVALIACAO_F12_CONTEXTO_20261103-ciclo1.md`) · ciclo 2 PASS (7 LOW).

Os 9 achados do ciclo 1 foram aplicados em `a57fde6` e os 7 LOW do ciclo 2 em `0f51ac9`, cada um com teste vermelho no commit anterior (`baseline-aval1.log`, `baseline-aval2.log`). Depois do ciclo 2, o código passou por 5 rodadas da revisão adversarial real (`## Advisor Ledger`).

---

## Advisor Ledger

**Revisão do DESIGN (pré-build):** NEEDS_WORK, `sdd/reviews/REVISAO_DESIGN_F12_CONTEXTO_20261103.md`; as 16 notas no Advisor Ledger do DESIGN v1.1 (15 APPLIED, 1 em parte).

**Revisões do build:** avaliador de contexto fresco em 2 ciclos e a revisão adversarial real (claude → codex como 2º revisor → openrouter:qwen/qwen3.7-plus) em 5 rodadas, as 2 acima do teto por decisão D4 do Roberto (`sdd/reports/evidence/F12_CONTEXTO/ledger-review.md`); custo das 5 rodadas US$ 13,20 (US$ 12,91 nominais da assinatura do Claude e US$ 0,29 de OpenRouter).

| # | Phase | Note | Severity | Decision | Evidence |
|---:|---|---|---|---|---|
| 1 | ciclo 1 | fronteira cega a commit do agente; citação de pattern por menção; `superficies:` que nunca vence | MEDIUM | APPLIED | `a57fde6`; `baseline-aval1.log` |
| 2 | ciclo 1 | ordem do cabeçalho; marcador esconde dúvida; linha com recuo; caminho relativo; ordem brief → snapshot; Gnn repetido | LOW | APPLIED | `a57fde6`; `baseline-aval1.log` |
| 3 | ciclo 2 | citação em lista; cerca ~~~; árvore limpa; briefs sem "não commite"; 2 dúvidas na mesma linha; recibo do Codex anterior ao texto final; self-test antes do 1º commit | LOW | APPLIED | `0f51ac9`; `baseline-aval2.log`; Codex rodado de novo |
| 4 | rodada 1 | `rm` do snapshot antes de validar o destino; shasum que falha vira hash vazio | HIGH | APPLIED | `89702c4`; `test_r1_…`, `test_r2_…` em `baseline-real1.log` |
| 5 | rodada 1 | redespacho após PADRAO_AUSENTE; arquivo apagado ⇒ VENCIDO; âncora na linha 0; âncora curta; diagrama; data da iterate | MEDIUM | APPLIED | `89702c4`; ledger `rodada=1` |
| 6 | rodada 1 | pino do `test_matriz_new_session`; fixture de governança `pendente` | MEDIUM | REBUTTED | o arquivo não fixa skill tocada; a fixture é entrada da revisão (o auditor refutou a 2ª nas rodadas 2 e 3) |
| 7 | rodada 2 | linha Governança dentro de cerca `~~~` liberava o gate | HIGH | APPLIED | `363d8bc`; `test_real2_linha_em_cerca_til_nao_vale` em `baseline-real2.log` |
| 8 | rodada 2 | link de arquivo permitido; pattern não citado bloqueava; superfície vazia/binária; bloco vazio; redespacho do cartógrafo | MEDIUM | APPLIED | `363d8bc`; ledger `rodada=2` |
| 9 | rodada 3 | caminho de `$T` perdido numa sessão nova; alias de link do permitido; `wc -l` sem newline final; redespacho com lint anexado; teste do yaml sem os exits; `sup:` com crases vazias | MEDIUM | APPLIED | D4 do Roberto: "corrigir agora e rodar a 4ª rodada"; `0ca09f9`; `baseline-real3.log`, `baseline-real3-alias.log`, `mutacao-exits-yaml.log` |
| 10 | rodada 4 | resolver o permitido depois do despacho deixava um link criado no permitido autorizar escrita noutro arquivo (regressão do item 9) | HIGH | APPLIED | `d816f77`; `baseline-real4.log` |
| 11 | rodada 4 | import relativo como âncora; citação com ponto no nome; dispensa sem a seção | MEDIUM | APPLIED | `d816f77`; ledger `rodada=4` |
| 12 | rodada 5 | a restauração do DEFINE seguia link | HIGH | APPLIED | `3ebeeea`; `baseline-real5.log` |
| 13 | rodada 5 | título em cerca `~~~` contava como seção nos 2 lints; links do índice com `--out` | MEDIUM | APPLIED | `3ebeeea`; ledger `rodada=5` |
| 14 | rodada 5 | títulos exatos do relatório no validador | MEDIUM | REBUTTED | o auditor refutou com evidência: o `revisor.md` manda copiar o template à letra |

**Fechamento da revisão:** a rodada 5 revisou `d816f77`; `3ebeeea` traz os consertos dela, `96a97ec` o conserto da sandbox e `6b7633c` o teto do CI, sem revisão externa própria (`--conferir` NÃO CONFERE). Depois de 5 rodadas, cada uma das 3 últimas com 1 HIGH mais estreito, o Roberto respondeu "continue" à pergunta D4, cuja opção recomendada é publicar com a revisão dispensada, e depois "release ok sdd-open", avisado de que o OK cobre a dispensa e os commits `96a97ec` e `6b7633c`; registro em `sdd/reports/evidence/F12_CONTEXTO/release-ledger-v2.4.0.yaml`. Pendência para a F14: revisão focada na fronteira.

---

## Issues Encountered

| # | Issue | Resolution | Impact |
|---:|---|---|---|
| 1 | 1º Verify Gate saiu 2 com erro de sintaxe: editei o `verify-gate.sh` enquanto o gate rodava a partir dele | log renomeado para `.sonda.txt`; o gate foi refeito sem edição no meio | nenhum no produto |
| 2 | 2º Verify Gate saiu 2: eu o chamei com `SDD_TRACE=off`, e os testes de trace herdaram a variável | log renomeado para `.sonda.txt`; o gate foi refeito sem a variável (966 OK) | nenhum no produto; a suíte não isola `SDD_TRACE` do ambiente de quem a chama (registrado para a F14) |
| 3 | `py_compile` numa evidência deixou `sdd/bin/__pycache__/` | apagado antes do commit; a evidência passou a usar `ast.parse` | nenhum (não entrou em commit) |
| 4 | o extrator de ADR do privado não lia a data no formato do template do Open (`Status` e `Date` na mesma linha) | corrigido no build | P1 |
| 5 | a fixture verde do `patterns-lint` do privado vencia sozinha depois de 90 dias | `__HOJE__` trocado no self-test | P1 |
| 6 | a fronteira do privado não casava o permitido quando a raiz passava por link (`/var` × `/private/var` no macOS) | realpath, resolvido no snapshot de antes | P1 |
| 7 | as evidências por AT foram gravadas primeiro sobre `363d8bc`, antes das rodadas 3 a 5 | refeitas sobre `96a97ec` | nenhum |
| 8 | o conserto da rodada 3 pôs o snapshot no `.git`, que é só leitura na sandbox do Codex: na execução sobre `3ebeeea` nenhum despacho aconteceu | snapshot na pasta temporária, com nome derivado da raiz; a exceção do `.git` saiu; `96a97ec` | defeito de P2 que as 5 rodadas de revisão não viram; só a execução real o mostrou |
| 10 | CI do PR #15: o job macOS foi cancelado no teto de 30 min; a 2ª tentativa do mesmo commit levou 27m06s | medido módulo a módulo: a suíte local cresceu só 9% (`tempos-por-modulo-*.sonda.txt`), sem travamento; teto de 45 min (`6b7633c`) | sem o conserto, a release podia não publicar |
| 9 | o `codex.sh` deu PASS falso nessa execução: exigia só o texto `AGUARDANDO_HUMANO` (que entra no log quando o agente lê o código-fonte) e o arquivo do brief | passou a exigir a linha ` exited 40 in `, que discrimina (0 no log falso, 1 nos bons); log guardado em `codex-3ebeeea-falso-pass/` | a prova foi refeita sobre `96a97ec` |

---

## Deviations from Design

| Deviation | User Decision | Reason | Impact |
|---|---|---|---|
| Snapshot com a linha `#HEAD` e FORA para os arquivos de um commit do agente | aplicado (M1 do avaliador, ciclo 1) | um commit limpa a árvore | Decision 4 |
| `superficies:` sem crase e com cada pathspec casando um arquivo versionado; `--validade` confere o diff antes | aplicado (M3 do ciclo 1, R3/R4@codex) | senão o mapa nunca vence | Decision 2 / 3 |
| Pattern não citado no `--design` só avisa em todo defeito | aplicado (R3@codex, rodada 2) | o contrato fala de DESIGN sem citação ⇒ 0 | Decision 9 |
| Snapshot em Python com realpath, `#HEAD`, `#PERMITIDO` e na pasta temporária com nome derivado da raiz (caminho fixo para a retomada) | aplicado (M1 do ciclo 1, rodadas 3 e 4, prova no Codex) | um commit limpa a árvore; o permitido não pode ser resolvido depois do despacho; uma sessão nova precisa achar o snapshot; o `.git` é só leitura na sandbox | Decision 4 |
| Brief gravado antes do snapshot; redespacho refaz brief e snapshot | aplicado (L5 do ciclo 1, R1@claude rodada 2) | o brief não pode virar FORA | Decision 5 |

---

## Blockers

None.

---

## Final Status

### Overall: COMPLETE

- [x] All File Manifest tasks completed (87/87)
- [x] Incremental verification recorded (5 baselines vermelhas)
- [x] Verify Gate green (`verify-gate-6b7633c.log`)
- [x] Complementary checks applicable pass
- [x] Acceptance Tests verified (26/26)
- [x] LLM prompt receipts complete (N/A: `LLM Prompts: false`)
- [x] Drift decisions recorded
- [x] Advisor findings disposed (APPLIED ou REBUTTED com motivo)
- [x] No unresolved blocker
- [x] No TODO/FIXME used as unfinished implementation
- [x] Dispensa da revisão externa dos últimos commits: OK do Roberto ("release ok sdd-open")
- [x] Release `v2.4.0`: OK do Roberto citando "sdd-open"

---

## Next Step

Execute o **SDD Handoff by RDD**.
