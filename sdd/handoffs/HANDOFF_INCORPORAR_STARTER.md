# HANDOFF: INCORPORAR_STARTER

> Registro do que ficou pronto e do que vem depois. Um arquivo por feature — cada etapa nova entra como seção no topo, nunca como arquivo separado.

## Ficha da feature

| Campo | Valor |
|---|---|
| **Objetivo** | Fazer do sdd-open o único SDD do Roberto, sob 4 parâmetros fixados em 2026-10-29 (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 0): **P1** corrigir erros antes de construir por cima; **P2** manter o padrão agnóstico (7 agentes; o que depende de subagente degrada para parada manual); **P3** incorporar o que o sdd-starter faz melhor (F1–F6: camada "Como falar com o aluno", skills de terreno, migration provada por leitura, validadores de fase, versão/testes/release, sdd-kb, docs); **P4** levar para o Open o que o SDD privado faz e o Open não (F7–F14: evidência fail-closed, hooks, fluxo encadeado, revisão adversarial, contexto e governança, UX/LLM, playbook e drive) e então **substituir o SDD privado pelo Open** (F15). Sem abrandar o mecanismo do open (gate com seis estados, evidência, avaliador fresco, playbook, release com veredito). |
| **Status** | 🔨 em andamento |
| **Feito** | 2026-10-29 — avaliação do starter (`sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`) e abertura da worktree. 2026-10-29 — as 5 decisões do Roberto (ver `## Eventos`); **F1 Manutenção entregue**: 115 testes em `tests/`, `scripts/check-versions.py`, `scripts/next-version.sh`, `.github/workflows/release.yml`, 3 padrões de PII; merge em `main` (`f75fbdb`, PR #1) e **Release `v2.2.1`** publicada sozinha com `sdd-open-v2.2.1.tar.gz` + `SHA256SUMS.txt` (hash conferido). 2026-10-29 — **F2 Terreno entregue**: `sdd-checar-ambiente` 1.3.0 (`checar.sh --segredo`), `sdd-higiene-dado` 1.1.1, `sdd-iniciar-repo` 1.1.1 em `.agents/skills/`; `doctor` confere segredo salvo no git; `sdd-new-session` 1.1.0 (pré-voo por `checar.sh --frente`, tabela de tradução, descoberta gravada no config da frente); 242 testes; merge em `main` (`41c6169`, PR #2) e **Release `v2.2.2`** (hash conferido). 2026-10-29 — **F3 Build e Release entregue**: `sdd-build` 2.1.0 com `references/aplicar-migration.md`; `report-lint.py` reprova migration sem linha provada em `## Migrations aplicadas`; `sdd-release` 2.2.0 com o bloco único do OK e `scripts/deploy-espera-testes.py` (SIM/NAO/NAO_SEI/NAO_SE_APLICA); `doctor` avisa skill e `sdd/bin/` mais velhos que o pacote; `LM-004`; 304 testes; merge em `main` (`1a54da5`, PR #3) e **Release `v2.2.3`** (hash conferido). 2026-10-29 — **W0 entregue** (sessão 1, worktree `sdd-open-w0-m1`): `sdd-iterate` 2.0.1 vê clarificação aberta (`--print` + gate sem `--print`); templates sem contexto de domínio, `/drive`, guard inexistente e passos de outro SDD; `sdd-build` 2.1.1 (avaliador grava só `AVAL-*.log`); `tests/test_correcoes_w0.py`; 316 testes; merge em `main` (`303cc87`, PR #4) e **Release `v2.2.4`** (hash conferido). 2026-10-29 — **M1 entregue**: job `testes-macos` nos dois workflows (Python 3.9.6 e bash 3.2.57 afirmados, `release` espera por ele), `actions/checkout` v5.1.0 por SHA, passo "Skill integrity" em `.agents/skills/`; 326 testes; push em `main` (`dd27ef6`, PR #5), **sem Release** (só `.github/**` e `tests/`). 2026-10-29 — **F4 Conversa entregue** (sessão 2, worktree `sdd-open-f4-conversa`): camada "Como falar com o aluno" nas 13 skills nativas + `sdd-checar-ambiente` (seção, `references/como-falar.md`, Status com o nome da fase no lugar do banner, linha de identificação, bump minor); `sdd/templates/fragments/PERGUNTA_DECISAO.md`; `skill-lint.py --conversa` + 7 fixtures; `sdd/bin/design-lint.py` e `handoff-lint.py` (passo 8 da `sdd-design`, 3b da `sdd-handoff`); `tests/test_agnostico.py`; 388 testes; 2 ciclos de revisão de contexto fresco; push em `main` (`2fcdda1`, PR #6) e **Release `v2.2.5`** (hash conferido). 2026-10-29 — **F5 Conhecimento entregue** (sessão 3, worktree `sdd-open-f5-conhecimento`): `sdd-kb` 2.2.0 como 17ª skill (porte do starter 2.1.0; KB em `sdd/kb/` fixo; `validate_kb.py --strict` exige `teste` existente dentro da raiz; `gate.sh` autossuficiente, 4 aceitas e 12 rejeitadas pelo motivo certo, recusa a cópia do `sync`); `sdd/bin/kb-dominios.py` (KB Domains fechado em `ls sdd/kb/` ou `nenhum`, só no `## Technical Context`); `sdd-define` 2.3.0 (passo 10); `sdd-ux-review` 2.3.0 (entrevista de público no passo 1); 499 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco; push em `main` (`7e19462`, PR #7) e **Release `v2.2.6`** (hash conferido). 2026-10-30 — **F6 Docs entregue** (sessão 4, worktree `sdd-open-f6-docs`): `docs/pt-BR/guia-do-aluno.md` (só PT), `docs/roadmap.md` + PT, quickstarts com "valide antes de seguir" e o caminho de atualização corrigido (P1), `adaptation-guide` corrigido (P1), READMEs com as 17 skills, `AGENTS.md.tmpl` com preparo, KB e a regra 7 "um OK só", "Por que cada regra existe" nas 7 skills de fase (bump patch), `tests/test_docs.py`; 514 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco; push em `main` (`1c9bbc7`, PR #8) e **Release `v2.2.7`** (hash conferido). **P3 (starter) concluído.** 2026-10-30 — **F7 Evidência entregue** (sessão 5, worktree `sdd-open-f7-evidencia`): `report-lint.py` fail-closed (tabela reconhecida, avaliação ausente reprova, `N.A.` contra `layers:` com o slot `evidence.require_avaliacao_layers`, `PENDENTE` e `--pendente`, `git check-ignore`, veredito fora de bloco cercado, `--stdin`); `verify-gate.sh --trace`/`--sem-define`; `gate-baseline.sh`, `gate-shell-evidencia.sh`, `avaliador-guard.sh` e `test-baseline.sh` em `sdd/bin/`; `sdd-build` 2.3.0, `sdd-release` 2.4.0; 630 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco (0 HIGH); push em `main` (`1d225e5`, PR #9) e **Release `v2.2.8`** (hash conferido). 2026-10-31 — **F8 Hooks entregue** (sessão 6, worktree `sdd-open-f8-hooks`): `sdd/hooks/pre-commit` (dispatcher com H2–H6, `report-lint --stdin` do `BUILD_REPORT` staged e o alarme da higiene quando ligado; recusa única com classes, "Por que importa" e `RESULTADO: COMMIT RECUSADO`) e `pre-push` (aviso de base velha); `init` liga `core.hooksPath = sdd/hooks` com confirmação, `doctor` confere, slot `project.context_file_max_kb: 100`; `sdd-higiene-dado` 1.2.0 (modo `hooks`: `git config sdd.higieneDado on|off`, nada em `.git/`); adaptador do Claude Code da E6 (`init --vendors claude` gera `.claude/hooks/sdd-report-guard.py` e `sdd-avaliador-guard.py` e faz merge em `.claude/settings.json`); `docs/hooks.md` + PT; 683 testes; revisão do DESIGN e 2 ciclos de revisão do build em contexto fresco (0 HIGH aberto); push em `main` (`7c640eb`, PR #10) e **Release `v2.2.9`** (hash conferido). 2026-10-31 — **F9 Fluxo encadeado entregue** (sessão 7, worktree `sdd-open-f9-fluxo`): `sdd/bin/sdd-fluxo.sh` (bash 3.2 + Python stdlib: `review-design` 0/1/64, `loop` 0/10/20/30/64 com `--log` regravado em toda saída, `despachar` **40 AGUARDANDO_HUMANO** com o brief em `sdd/reports/briefs/BRIEF_<papel>_<F>.md`, `seguir` 0/1/64, `estado`, `--self-test`); `sdd/bin/sdd-decisoes-lint.sh` (`--sites`, `--self-test`); marcas `[D1 · não se desfaz]` … `[D5 · provas em conflito]` e `[auto · de rotina]` no item 9 do `PERGUNTA_DECISAO.md` e nas 17 perguntas de decisão (15 nas skills, 2 nos fragmentos); `FLUXO_ENCADEADO.md`; subseção `### Fluxo encadeado` nas 9 skills de fase; slots `flow.autonomous: false` e `review.security_globs: ""`; F6/F8/F10/F11 do PORTE; seção Advisor Ledger no `DESIGN_TEMPLATE.md`; `docs/chained-flow.md` + PT; 744 testes; provada no Codex CLI 0.163 (AT-030/AT-031); revisão do DESIGN e 2 ciclos do build em contexto fresco (21 achados aplicados); push em `main` (`daf9c0f`, PR #11) + correção do teto do `release.yml` (`89ac76f`, PR #12) e **Release `v2.2.10`** por tag (hash conferido). 2026-11-01 — **F10 Revisão adversarial entregue** (sessão 8, worktree `sdd-open-f10-revisao`): `sdd/bin/adversarial-review.sh` (revisor → auditor em cadeia sobre diff congelado com sha256; 2º revisor por gatilho e desempate; exits 0/64/65/66/67/68; `--conferir` e `--ledger`), 4 adapters em `sdd/bin/adapters/` (claude, codex `-s read-only`, gemini, openrouter com `data_collection: deny`), `sdd/review/{registry.tsv,precos.tsv,prompts/}` sem cadeia padrão, `loop` com 2º revisor/rasa/desempate, `sdd-release` 2.6.0 com review externo obrigatório (dispensa D3), `sdd-build` 2.5.0, `sdd-design` 2.3.0, 5 slots `review.*`; 853 testes; revisão do DESIGN, 2 ciclos do build e 4 revisões reais do próprio mecanismo; push em `main` (`248301d`, PR #13) e **Release `v2.3.0`** por tag (hash conferido). 2026-11-01 — **F11 gate offline entregue** (sessão 8, worktree `sdd-open-f11-gate`): `sdd/bin/adversarial-review-gate.sh` (103 asserções em ~7 s com os 4 adapters reais contra stubs por engine em `sdd/review/stubs/`; exits 0/2/3/64), `sdd/bin/eval-agree.sh` (taxa de AGREE por auditor nas revisões já feitas), os 6 achados adiados da F10, `testes-macos` com teto de 30 min, a revisão adversarial fora do roadmap; 894 testes; revisão do DESIGN, 2 ciclos do build e 3 revisões reais; push em `main` (`9508ff0`, PR #14) e **Release `v2.3.1`** automática (hash conferido). 2026-11-03 — **F12 Contexto, patterns e governança entregue** (sessão 9, worktree `sdd-open-f12-contexto`): `sdd-define` 2.5.0 com os passos 1.5 (cartógrafo) e 11 (governança em todo Define), `verify-gate.sh` com o 2º motivo do exit 5, `contexto-lint.sh`, `patterns-lint.sh`, `governanca-fronteira.sh`, `governanca-bloco.py`, `docs-extract-decisions.sh`, `sdd-design` 2.4.0, `sdd/patterns/README.md`, `sdd/WORKFLOW_CONTRACTS.yaml`; 992 testes; revisão do DESIGN, 2 ciclos do build, 5 revisões reais e 2 despachos provados no Codex; push em `main` (`6b7633c`, PR #15) e **Release `v2.4.0`** por tag (hash conferido). 2026-11-04 — **F13 UX e LLM entregue**: tabela WCAG na `sdd-ux-review` 2.5.0, `contraste.sh`, skill nova `sdd-loop-builder` 1.0.0 (18 skills), roteador no passo 4 da `sdd-build` 2.6.0, fragmento `LLM_PROMPTS_DESIGN.md` com o `design-lint.py` conferindo o inventário, `prompt-drift-scan.sh` com `prompts.wrapper_pattern`, `docs/llm-in-code.md`; 1.134 testes; revisão do DESIGN, 3 ciclos do avaliador, 6 revisões reais; push em `main` (`b1348bd`, PR #16) e **Release `v2.5.0`** por tag (hash conferido), com 3 riscos aceitos pelo Roberto (etapa F13). 2026-11-05 — **F14 Playbook, 1ª de 2 entregas**: `sdd/bin/playbook-curator.sh`, `sdd/invariants.md`, passo 17b da `sdd-release` 2.7.0, `sdd-playbook` 2.2.0, `copiar-docs.sh` na `sdd-new-session` 1.4.0, molde do handoff com 6 seções, fronteira de escrita com índice, branch e `.git`; 1.411 testes; `main` = `8a320e9` (PR #17) e **Release `v2.6.0`** (hash conferido). 2026-11-06 — **F14 Drive, 2ª de 2 entregas**: `sdd-drive` 1.0.0 (`sdd/bin/sdd-drive.sh`), raio de impacto na `sdd-release` 2.8.0, `sdd/bin/deploy-do-sha.sh`, `sdd/bin/sdd-archive.py`, slot `drive.max_rounds`; 19 skills, 1.656 testes; `main` = `b0663d3` (PR #18) e **Release `v2.7.0`** (hash conferido), com 3 riscos aceitos pelo Roberto (etapa F14 Drive). 2026-11-07 — **Sessão 13**: os 5 achados da rodada 5, o teste do slice e os 3 achados da rodada 6 consertados (`5a1e3fc`, `3d69536`, sobre a curadoria `b3526ae`; `sdd-release` 2.8.1); revisão real rodadas 6 e 7 (`--conferir` CONFERE sobre `3d69536`); "sdd-open autorizado": push `b0663d3..3d69536`, PR #19 MERGED, **Release `v2.7.1`** (hash conferido); brainstorm da F15 gravado (`sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md`); plano v1.6 com F18, F19 e F20. 2026-11-08 — **v2.7.2** (guardas de BUILD_REPORT e gancho encadeado). 2026-11-10 — **F15 Slots entregue** (L0 + L3 + L4 do inventário de saída): `sdd/bin/slot.sh`, slots `smoke.*` e `schema.check_cmd` reabertos, `sdd-release` 2.9.0 (testes do diff antes do OK, 3 smokes), `sdd-build` 2.7.0 (checagem de schema antes do apply), `test-baseline.sh --touched` com o teste ao lado da fonte; 1.717 testes; `main` = `45e27a9` (PR #21) e **Release `v2.8.0`** (hash conferido). |
| **Falta** | Estado de cada frente: seção **Estado das frentes** de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` (fonte única desde 2026-11-10). **F18 (onda 1) + F20 🔨 desde 2026-11-11** (worktree `sdd-open-f18-f20-seguranca`; ordem das próximas no **Cronograma recomendado** do plano). **F16 ✅ (`v2.11.0`, 2026-11-11)**: pendências na seção "2026-11-11 — F16" (curadoria de 5 candidatos, R1/R4 da rodada 4, o teto do `checar` no Windows); a **F16W** (porte da suíte ao Windows) entra no plano. **F21 ✅ (`v2.9.0`) e F19 ✅ (`v2.10.1`; a tag `v2.10.0` ficou sem Release), 2026-11-10**; a skill da F21 também está no starter (`v1.5.16`). Pendências que elas deixam (detalhe na seção de 2026-11-10 "F21 + F19"): curadoria de 5 candidatos ao playbook; 2 achados leves da F19 (coluna `Cobrança` na documentação do medidor; papel `indisponível` sem exit pulado sem aviso); `.gitignore` do pacote; 14 cenários de comportamento da F21 não executados; página `/sdd/` no privado (frente de lá); saldo da OpenRouter em US$ 0,07 e codex sem cota (a revisão com duas engines depende disso). **F15 Slots ✅ (`v2.8.0`, 2026-11-10)**: o privado sincroniza para a `v2.8.0` (`sdd-open.sh sync`) e liga os 4 slots antes da fase 3; curadoria `c2560fc` sobe na próxima release do Open. Antes: **F15, inventário de saída** (só leitura, no privado: cada arquivo do SDD privado que sai na fase 4 ganha destino — equivalente no Open, script do projeto por slot, abandonado com decisão, ou lacuna; lacuna vira trabalho no Open antes da fase 4), depois o OK do Roberto para levar a fase 1 ao `main` do privado, a fase 2 (feature da prova) e os 3 slots de smoke (release própria) antes da fase 3; **v2.7.2 publicada em 2026-11-08** e fase 1 concluída (`doctor` ✅ sem ⚠️ no privado) · **F16 Ambiente agnóstico e proativo** (no Open; independente; inclui os testes no Windows desde 2026-11-07) → **F17 Starter gerado a partir do Open** (Decisão 5) → **F18 Segurança embutida no fluxo** (incluída em 2026-11-07; onda 1 pode vir antes da F17) · **F19 Custo e benefício dos modelos de revisão** (incluída em 2026-11-07; independente, depois da F11) · **F20 Ações preventivas do e-book no Open e no starter** (incluída em 2026-11-07; brainstorm conjunto com a F18; chega ao starter pela F17) (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seções 8 e 9; agrupamento por sessão na seção 10) — cada uma como fluxo SDD completo numa worktree própria; os artefatos SDD desta família vivem na branch `docs/incorporar-starter`, nunca mesclada (a execução da F15 grava os dela no privado); `MANIFEST.txt` a cada arquivo novo; cada push em `main` que toca o produto publica uma Release sozinho. |
| **Verify Gate** | última frente (F16_AMBIENTE): `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F16_AMBIENTE.md` exit 0 em `69b7f6b` (1.941 testes; `evidence/F16_AMBIENTE/VERIFY-GATE-69b7f6b.log`) |
| **Pronto quando** | **P3 (starter):** (1) `bash scripts/publish-gate.sh .` sai 0 na worktree com os steps novos (testes unitários, check-versions, design-lint, handoff-lint, padrões de PII); (2) `python3 sdd/bin/skill-lint.py --conversa .agents/skills/sdd-*/SKILL.md` sai 0 e as 13 skills nativas (mais a `sdd-checar-ambiente`) têm a seção `## Como falar com o aluno` mais `references/como-falar.md` ✅ (F4); (3) existem `.agents/skills/sdd-checar-ambiente`, `sdd-higiene-dado`, `sdd-iniciar-repo` e `sdd-kb` com `tests/` passando ✅ (F5); (4) `sdd-build` tem `references/aplicar-migration.md` e `sdd/bin/report-lint.py` reprova migration listada sem prova por leitura ✅; (5) existe pelo menos uma Release no GitHub de `robertodiasduarte/sdd-open` com `SHA256SUMS.txt` ✅; (6) o item "Specs como deltas" do `docs/comparison.md` continua declarado como planejado, não como feito. **P1 (erros):** (7) `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` sem hit e `verify-gate.sh` sem `--print` sai 5 na fixture de clarificação (W0) ✅; toda nota HIGH/MEDIUM de revisão aplicada ou rebatida com motivo. **P2 (agnóstico):** (8) `tests/test_agnostico.py` verde (nenhum nome de ferramenta de um agente só em skills, templates, `AGENTS.md.tmpl` e playbook) ✅ (F4); CI verde em `ubuntu-latest` e `macos-latest` ✅ (M1); F9 provada no Codex CLI ✅ (`v2.2.10`; o Codex 0.163 abre subagente, o exit 40 foi exercitado com a condição "sem subagente" no prompt); F12 provada no Codex CLI ✅ (`v2.4.0`; os 2 despachos com `exited 40`, sobre `96a97ec`). **P4 (substituição):** (9) F7–F14 publicadas (F7 ✅ `v2.2.8`, F8 ✅ `v2.2.9`, F9 ✅ `v2.2.10`, F10 ✅ `v2.3.0`, F11 ✅ `v2.3.1`, F12 ✅ `v2.4.0`, F13 ✅ `v2.5.0`, F14 ✅ `v2.7.0`); (10) no repositório privado, `bash bin/sdd-open.sh doctor` sai ✅, uma feature real do RDD percorre o fluxo do Open de ponta a ponta e `git ls-files .claude/commands/workflow .claude/agents sdd-public` está vazio (F15). |

---

## Eventos

> Toda mudança de escopo, pausa ou replanejamento entra aqui como **linha nova**. Nunca reescreva o campo "Falta" sem registrar o porquê aqui — senão a decisão desaparece.

- 2026-10-29 — Frente criada a partir da avaliação do sdd-starter pedida pelo Roberto ("incluir no OPEN tudo de bom que tem no STARTER, inclusive o jeito de conversar com o aluno"). Nenhum código alterado ainda; só análise, documento e abertura da worktree.
- 2026-10-29 — Decisão 1 (Roberto): a fonte canônica de `sdd-governanca`, `sdd-auditoria-harness` e `sdd-prompt-builder` é o **open**. O starter deixa de editar as três; nada do starter é portado para elas.
- 2026-10-29 — Decisão 2 (Roberto): a camada "Como falar com o aluno" fica **sempre ligada**, sem toggle e sem slot novo em `sdd/config.yaml`.
- 2026-10-29 — Decisão 3 (Roberto): Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta em todas as skills; o banner `🧠 FASE` vira a primeira palavra do Status (`Define: ✅ 1 … · ▶️ 2 …`); o kanban `✅ 🏃 ⬜ ➖` de `sdd/templates/fragments/RESUMO_ETAPA.md` fica **intacto**, só no fechamento da fase.
- 2026-10-29 — Decisão 4 (Roberto): a descoberta de ambiente grava nos **slots existentes de `sdd/config.yaml`** (`project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd`); não existe `sdd/ambiente.md`. Achado sem slot (cenário de branching, arquivos locais) fica só na conversa.
- 2026-10-29 — Decisão 5 (Roberto, depois de pedir explicação): o sdd-starter passa a ser uma **distribuição gerada a partir de `.agents/skills/` do open**. Mantém repositório, instalação por `npx skills add` e zips por skill, porque é a única porta para quem usa claude.ai ou ChatGPT na web, sem terminal: 11 das 13 skills do open citam arquivos criados pelo `init` e não funcionam como zip. Leva só as skills que funcionam sozinhas, com o gate em modo "confira à mão" e um aviso de quando migrar para o open. Fica em frente própria, depois da F6; nada muda no starter nesta frente.
- 2026-10-29 — Brainstorm da F1 (`sdd/features/BRAINSTORM_F1_MANUTENCAO.md`) muda o escopo das frentes: F1 é rede de segurança (testes dos 5 scripts, `check-versions.py`, release, 3 padrões de PII). **Para a F4**: `design-lint.py`/`handoff-lint.py` (templates do open divergem do starter; reescrita, não porte) e `metadata.updated` + linha de identificação nas 13 skills. **Para a F2**: `doctor` com segredo no histórico (o `checar.sh` já faz). Release: Roberto escolheu **automática no push de `main`** (patch calculado da última tag), contra a recomendação de tag manual; tag manual `v*` também vira Release.
- 2026-10-29 — Build da F1: o `init` copia `sdd/fixtures/` para o projeto do usuário na 1ª instalação (`aplicar()` em `bin/sdd-open.sh`, linha 506) — a premissa "copia só templates, bin e playbook" do Brainstorm e do Design estava errada. `sdd/fixtures/**` entrou nos paths que disparam a Release (DEFINE v1.1, DESIGN v1.1). A decisão de `tests/` na raiz continua válida.
- 2026-10-29 — Revisão de contexto fresco do `release.yml` (veredito FIX FIRST, 5 notas) aplicada em `f75fbdb`: gatilho só em tags `vX.Y.Z`, `next-version.sh vX.Y.Z` publica a tag empurrada, HEAD atrás da última tag não publica, fila por ref, `permissions: contents: read` no `publish-gate.yml`. Parte "mover os checks inline para um script" recusada: mexeria em steps existentes.
- 2026-10-29 — Roberto: "ok, push no sdd-open". Push fast-forward `80d7887..f75fbdb` em `main`; PR #1 MERGED; run `release` 40876615567 publicou `v2.2.1` (inclui o `sdd-new-session` 1.0.0 que estava em `main` sem tag).
- 2026-10-29 — Brainstorm da F2 (`sdd/features/BRAINSTORM_F2_TERRENO.md`), 4 decisões do Roberto: testes portados em `tests/` na raiz (não dentro da skill: `init`/`sync` copiam a pasta inteira ao usuário); `doctor` chama um modo novo `checar.sh --segredo` (sem rede), sempre — sem `doctor --repo`; `sdd-new-session` com script + tabela + pré-voo à mão como fallback (PowerShell); descoberta grava no `sdd/config.yaml` **da frente** (não no checkout principal, que ficaria sujo e faria o `git pull` abortar depois do merge). Abordagem A (transplante com adaptação mínima).
- 2026-10-29 — Build da F2, drift aprovado pelo Roberto: `tests/test_skill_lint.py` fixava 13 skills; vira `test_as_16_skills_reais_passam` (DESIGN v1.1, item 22). Cada frente que acrescenta skill (F5: `sdd-kb`) atualiza esse número de propósito.
- 2026-10-29 — Revisão de contexto fresco do build da F2 (veredito FIX FIRST, 0 HIGH, 2 MEDIUM, 4 LOW): 5 aplicadas em `41c6169` (`test_alarme` isolado do gitconfig global; `--segredo` por pathspec, 11,7 s → 0,06 s com 5 mil arquivos; `SDD_TEST_BASH` nos testes portados; `doctor` não perde linha de nome com quebra; texto da `new-session`); 1 recusada (caminho relativo do `git rm --cached` rodado de subpasta — herdado, o `doctor` não é afetado).
- 2026-10-29 — Roberto: "OK, push no sdd-open — v2.2.2" (contra a alternativa de tag manual `v2.3.0`). Push fast-forward `f75fbdb..41c6169` em `main`; PR #2 MERGED; run `release` 40900694496 publicou `v2.2.2`.
- 2026-10-29 — Brainstorm da F3 (`sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md`), 4 decisões do Roberto: migration = glob fixo (`*.sql`, `migrations/`) **e** `layers.sql` quando preenchido; "o deploy espera os testes?" vira script com fixtures (`.agents/skills/sdd-release/scripts/deploy-espera-testes.py`), não só texto; instalação existente é avisada pelo `doctor` (versão de skill e `sdd/bin/*` diferente do pacote), sem verbo `upgrade`; prova de migration = log de `evidence/` ou `recibo:` (este em qualquer `kind`). Abordagem A (tudo numa release). No checkpoint 2, o script ganhou a 4ª saída `NAO_SE_APLICA`.
- 2026-10-29 — Build da F3: 1º Verify Gate vermelho em `8c1a593` — `test_contrato_build_release` rodava o `playbook-lint.sh` na raiz, e a cópia de `git archive` do gate não tem `.git`; corrigido em `af8b0e3` (sandbox com `git init`).
- 2026-10-29 — Revisão de contexto fresco do build da F3 (veredito FIX FIRST: 1 HIGH, 6 MEDIUM, 6 LOW; 23/23 ATs PASS): 11 SIM falsos do `deploy-espera-testes.py` reproduzidos e corrigidos em `1a54da5` (DESIGN v1.1, Decisão 4); `report-lint` aceita títulos `## 2. Arquivos …` e `## Fase A — Files …`; 10 notas aplicadas inteiras, 1 em parte (`— · —`), 2 rebatidas (escolhas do DESIGN/DEFINE).
- 2026-10-29 — Roberto: "push do sdd-open autorizado" (sem escolher versão ⇒ patch automático). Push fast-forward `41c6169..1a54da5` em `main`; PR #3 MERGED; run `release` 40915091971 publicou `v2.2.3`.
- 2026-10-29 — Roberto pediu para consolidar F4–F6 com o plano do porte privado → open (`/Users/robertoduarte/RDD/Wordpress/.claude/sdd/reports/PORTE_SDD_PRIVADO_PARA_OPEN_2026-10-29.md`, ondas W0–W5) e a revisão externa dele (`…/evidence/PORTE_SDD_OPEN/REVIEW-deepseek-2026-10-29.md`). Resultado em `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`: (1) os 5 defeitos da W0 conferidos na `v2.2.3`, com 2 locais a mais de `/drive` e 1 de "slice 2"; a W0 **toca** `sdd-iterate/SKILL.md` e `contexto-fresco.md`, ao contrário do que o porte diz, então a recomendação é W0 **antes** da F4, não em paralelo; (2) a F4 absorve do porte a linha de transição, o formato de pergunta (`PERGUNTA_DECISAO.md`), a parada ⏸️ que o `exit 40 AGUARDANDO_HUMANO` da W2 vai reusar, fixtures que reprovam no `skill-lint`, títulos de ADR fixos no `design-lint` e `handoff-lint` tolerante a seções extras; (3) a F5 pode levar "KB Domains" como lista fechada (pasta da KB); (4) a F6 ganha `docs/roadmap.md` com W1–W5. Cinco decisões pendentes (seção 5 do plano). Nada de código mudou; o porte (repo privado) não foi editado — 6 correções listadas na seção 6 do plano.
- 2026-10-29 — Roberto: "podemos criar a F7 (e outras) para incorporar as funcionalidades do SDD privado". As ondas W1–W5 do porte viram **F7–F14** desta frente, mais a manutenção M1 (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 8: entrega, decisões, dependências, atenção e "pronto quando" de cada uma; seção 9: mapa dos 77 itens do porte → frente). Escopo da frente INCORPORAR_STARTER passa a cobrir também o porte privado → open. Esforço estimado F7–F14: 29–36 dias de agente. Skills novas previstas: `sdd-loop-builder` (F13) e `sdd-drive` (F14) — `test_skill_lint.py` 16 → 17 (F5) → 18 → 19.
- 2026-10-29 — Auditoria de cobertura do plano contra o porte (pedida pelo Roberto): os 77 itens e as 5 notas da revisão externa já tinham frente, mas faltavam os 9 princípios do §3, ~60 detalhes técnicos (exits 67/68, tetos 180 KB/8 MB/100 KB, gatilhos do 2º revisor, flags do curator e do drive, regras do cartógrafo), 7 dos 23 slots do §6.2 e as fontes do Anexo A com linhas/refs. Entraram nas seções 8.0–8.3 e no mapa da seção 9 de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`. O plano passa a bastar sozinho, sem depender do porte (que mora no repo privado e já tem 6 fatos velhos).
- 2026-10-29 — Roberto fixou os **4 parâmetros de verificação** do programa (P1 corrigir erros · P2 manter o padrão agnóstico · P3 incorporar o que o starter faz melhor · P4 acabar com o SDD privado e substituí-lo pelo Open) e pediu a tabela de degradação por vendor e o teste de agnosticismo. Plano v1.3 (`PLANO_F4_F15_CONSOLIDADO.md`): seção 0 com os parâmetros e como cada um se prova; regra 10 e tabela de degradação em 8.0; item G da F4 (`tests/test_agnostico.py`); **F15 Substituição do SDD privado** como fim do programa (o caminho inverso §11 do porte deixa de existir); agrupamento por sessão na seção 10 (uma frente grande por sessão; pares só W0+M1 e F10+F11). A Ficha ganhou o objetivo novo e os critérios (7)–(10). **Versionamento dos artefatos SDD** (decisão do Roberto): branch `docs/incorporar-starter`, nunca mesclada em `main` (o CI só roda em `main` e PR; 9 arquivos têm caminhos `/Users/` que o G2 reprova e nada está no `MANIFEST.txt`), com tag anotada `docs-2026-10-29`. Prompt da sessão 1 (W0 + M1) em worktree limpa gravado em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`.
- 2026-10-29 — Sessão 1 (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1`, branch `feat/w0-m1`), W0: o grep do gate da W0 achava 2 locais a mais que o plano (`BUILD_REPORT_TEMPLATE.md:202`, `DESIGN_TEMPLATE.md:105`), onde "Step 1.5" é o passo 1.5 **real** da `sdd-build` (contrato de aceite) — viraram "passo 1.5 da `sdd-build`". O texto pedido para a 4.5 ("sem Write/Edit") citava ferramenta de um agente só (P2): virou "não edite código nem documento do projeto". Revisão de contexto fresco do `b1df8c8`: FIX FIRST, 0 HIGH, 5 MEDIUM, 5 LOW — aplicadas em `303cc87`, 3 rebatidas (`/build` como forma curta da fase; `avaliador-fresco` é nome de papel; `/adversarial-review` no `RESUMO_ETAPA.md` fica pela Decisão 3 e vai para a F10).
- 2026-10-29 — Roberto: "pode finalizar (push + deploy + verificar)" sem citar o repositório → push **recusado** pela regra; depois "ok \"sdd-open\"". Push fast-forward `1a54da5..303cc87` em `main`; PR #4 MERGED; run `release` 40926754472 publicou `v2.2.4`.
- 2026-10-29 — M1, decisão do Roberto (pergunta com 3 opções): o item "baseline da `sdd-auditoria-harness` no CI, falha com HIGH/CRITICAL" do plano não existe como ferramenta — o `collect_evidence.py` não lê `.agents/skills/` (só `.claude/skills/*/SKILL.md`), não tem severidade e sempre sai 0. Escolhida a **varredura inline no CI** (Unicode invisível e código remoto entregue a shell), contra "tirar da M1" e "rodar o collect_evidence como smoke".
- 2026-10-29 — Revisão de contexto fresco do `eac5484` (M1): FIX FIRST, 0 HIGH, 4 MEDIUM, 6 LOW — aplicadas em `dd27ef6` (varredura fail-closed com alvo vazio; piso **afirmado** e `python3` do PATH = piso; regex de código remoto e faixas Unicode ampliadas); 3 aceitas com motivo (escopo só `.agents/skills/`; texto que cita `curl … | sh` reprova; `release` preso ao runner macOS).
- 2026-10-29 — Roberto: "finalizar (push + deploy + verificar)" sem o repositório → recusado; depois "finalizar (push + deploy + verificar) sdd-open". Push fast-forward `303cc87..dd27ef6` em `main`; PR #5 MERGED; só o `publish-gate` roda (run 40931927983) — `.github/**` e `tests/` ficam fora dos `paths` do `release.yml`, então a M1 **não gera tag**; a última Release continua `v2.2.4`.
- 2026-10-29 — Brainstorm da F4 (`sdd/features/BRAINSTORM_F4_CONVERSA.md`), 7 decisões do Roberto, todas na opção recomendada: decisão 2 do plano = **"não sei" e "sem Outro"**, as duas; decisão 3 = a F4 **absorve A–F**; `skill-lint` ganha a flag **`--conversa`** (o padrão continua só frontmatter, porque o lint vai para o projeto do usuário); a **`sdd-checar-ambiente` entra** (14 skills, não 13); o `handoff-lint` confere o **template do open**, não o formato do starter (o item F do plano descrevia o do starter); `sdd-design` e `sdd-handoff` **rodam o lint** no próprio documento (2 exceções declaradas à regra "comandos não mudam"); `test_agnostico` reprova **nomes de ferramenta** e permite "subagente" como conceito, varrendo skills, templates, `AGENTS.md.tmpl` e playbook. Abordagem A (seção autocontida + `como-falar.md` + fragmento único, uma release).
- 2026-10-29 — Design da F4: a `sdd-checar-ambiente` manda repassar a saída do script "sem frase antes"; a exceção (d) passou a valer para toda resposta dela (Status antes do relatório, sem retraduzir). O lint da `sdd-handoff` virou o passo `3b` para não renumerar o passo 4. DEFINE v1.1.
- 2026-10-29 — Revisão de contexto fresco da F4, ciclo 1 sobre `4e77a1f`: NEEDS_WORK, 0 HIGH, 4 MEDIUM, 8 LOW (21/22 ATs PASS; o AT-022 depende do CI). Aplicadas em `fd94876` (L1 em parte: opção desconhecida no `skill-lint` continua 64). M3 mudou o contrato: ficha com Status ✅ dispensa o prompt de retomada, porque a `sdd-handoff` o declara opcional sem continuação (DEFINE v1.2, AT-012). Ciclo 2 sobre `fd94876`: **PASS**, 0 HIGH, 0 MEDIUM, 6 LOW — 5 aplicados e 1 em parte em `2fcdda1` (lista numerada, `__negrito__` e prosa entre pergunta e opções ficam fora do formato do DEFINE).
- 2026-10-29 — Roberto: "push sdd-open autorizado" (sem escolher versão ⇒ patch automático, contra a alternativa `v2.3.0` por tag manual). Push fast-forward `dd27ef6..2fcdda1` em `main`; PR #6 MERGED; run `release` 40952893409 com `testes` e `testes-macos` antes do `Publicar release` (20:57:35 → 20:57:37); publicou `v2.2.5`.
- 2026-10-29 — Brainstorm da F5 (`sdd/features/BRAINSTORM_F5_CONHECIMENTO.md`), 6 decisões do Roberto, todas na opção recomendada: decisão 4 do plano = **`sdd/kb/` fixo**, sem slot `project.kb_dir`; o item G vira **lint novo em `sdd/bin`** (`kb-dominios.py`), contra "modo no `validate_kb.py`" e "só texto"; o `gate.sh` fica **na skill, autossuficiente** (casos montados dos exemplos), contra "só no pacote"; RULE_MAP → Verify Gate = **arquivo existe + lint lista** (sem casar texto do `cmd`); entrevista do `ux-review-builder` **opcional, dentro do passo 1** da `sdd-ux-review`, gravada em `## User and Context`; amostras **só as do starter** (não a KB real `programa-irpf`). Abordagem A (transplante, uma release). O Roberto pediu define → ux-review → design → revisão do design → build → revisão do build em sequência.
- 2026-10-29 — Revisão do DESIGN em contexto fresco (modo contrato): NEEDS_WORK, 2 HIGH, 4 MEDIUM, 2 LOW, aplicadas antes do build. H1: a cópia que o `init --vendors claude` gera ganha 2 linhas `sdd-open:generated` em todo arquivo não-JSON, e o exemplo normativo reprovava lá (SHA-256 e RULE_MAP) — os textos passam a apontar `.agents/skills/sdd-kb/…`, o gate recusa a cópia gerada (AT-017 novo) e `.gitattributes` com `-text` só em `fontes/`. H2: o passo 10 sem bloco cercado, para o `comandos-intactos` bater. DESIGN v1.1, DEFINE v1.3.
- 2026-10-29 — Build da F5: a sabotagem do `kb_normativo.py` não deixou teste vermelho (o `rule-map --check` só tinha o lado verde) → `RuleMapCheck` em `7e5b25c`. Ciclo 1 da revisão do build sobre `7e5b25c`: NEEDS_WORK, 0 HIGH, 3 MEDIUM, 6 LOW, todos aplicados em `0e0dba5` (KB Domains só do `## Technical Context`; RULE_MAP do exemplo conferido antes dos casos; testes de caso bom rejeitado e de outro motivo; `teste` fora da raiz reprova). Ciclo 2 sobre `0e0dba5`: **PASS** (15/15 mutações reversas pegas), 3 LOW novos aplicados em `7e19462`.
- 2026-10-29 — Roberto: "release do sdd-open autorizado" (sem escolher versão ⇒ patch automático, contra a alternativa `v2.3.0` por tag manual). CI do PR #7 verde (run 40969129265: `gate` e `Testes no piso (macOS)`). Push fast-forward `2fcdda1..7e19462` em `main`; PR #7 MERGED; run `release` 40970012304 com `testes` e `testes-macos` antes do `Publicar release`; publicou `v2.2.6`.
- 2026-10-29 — Roberto perguntou se F6 e F7 cabem na mesma sessão. Recomendação: não. A regra do par (plano, seção 10) exige duas frentes pequenas que não toquem os mesmos arquivos: a F7 tem 13 itens (E1–E13), 5 scripts novos, `verify-gate.sh --trace` e 3 decisões (D4, D11, E6), ~3 dias no PORTE; a F6 adapta um guia de 494 linhas; as duas mexem na `sdd-build` e no `docs/roadmap.md`. Roberto: "prepare o prompt para F6. documente tudo. /sdd-new-session F6" — a F6 vai sozinha na sessão 4.
- 2026-10-29 — Frente F6 aberta com a `sdd-new-session` (starter 1.3.0, em `~/.claude/skills/`): worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`, branch `feat/f6-docs` nascida de `origin/main` = `7e19462`, nomes no padrão da família (não o `../sdd-open-frentes/<slug>` padrão da skill); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. A skill gravou `sdd/ambiente.md` no checkout principal (`/Users/robertoduarte/rdd-public/sdd-open`), não rastreado: é nota local da skill do starter, não do open (Decisão 4 da frente: o open usa os slots do `sdd/config.yaml`).
- 2026-10-29 — Brainstorm da F6 (`sdd/features/BRAINSTORM_F6_DOCS.md`), decisões do Roberto: guia do aluno **só em português** (`docs/pt-BR/guia-do-aluno.md`), roadmap em inglês e português; "Por que cada regra existe" nas **7 skills de fase**; Release **`v2.2.7` automática** (sem tag à mão); amostras: nenhuma; abordagem A (adaptação escrita à mão, uma Release só); os 2 checkpoints confirmados.
- 2026-10-29 — Revisão do DESIGN da F6 em contexto fresco (modo contrato): NEEDS_WORK, 3 HIGH, 4 MEDIUM, 3 LOW, aplicadas antes do build (DEFINE v1.1, DESIGN v1.1). H2 achou um P1 no produto publicado: o passo 5 dos quickstarts ensinava `git pull` + `sync`, que não atualiza skill nenhuma (o `init` não sobrescreve, o `sync` só regera adaptadores) — corrigido nos quickstarts e no guia. M4: a regra "um OK só" entrou como regra 7 do `AGENTS.md.tmpl`.
- 2026-10-29 — Revisão do build da F6, ciclo 1 sobre `963c47e`: NEEDS_WORK, 3 HIGH (o guia dizia que o alarme "registra e libera"; que a `sdd-design` devolve Define com dúvida; uma regra inventada no brainstorm), 3 MEDIUM, 6 LOW, todas aplicadas em `aaae1b4`. Ciclo 2 sobre `aaae1b4`: **PASS**, 6 LOW aplicados em `1c9bbc7`.
- 2026-10-30 — Roberto: "Push sdd-open autorizado". CI do PR #8 verde (run 40984992013: `gate` e `Testes no piso (macOS)`). Push fast-forward `7e19462..1c9bbc7` em `main`; PR #8 MERGED; run `release` 41025735985 com `testes` e `testes-macos` antes do `Publicar release`; publicou `v2.2.7`. Com a F6, os itens do P3 (F1–F6) estão entregues; o programa segue no P4 (F7–F15).
- 2026-10-30 — Frente F7 aberta com a `sdd-new-session` (starter 1.3.0): pré-voo verde; worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia`, branch `feat/f7-evidencia` nascida de `origin/main` = `1c9bbc7`, nomes no padrão da família (lidos de `sdd/ambiente.md` do checkout principal); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. O prompt da sessão 5 passou de "crie a worktree" para "confira a worktree".
- 2026-10-30 — Sessão 5 (F7): o checkout local do privado (`~/RDD/Wordpress`, `main`) está **atrás** do `origin/main` dele; 2 das 6 fontes da F7 não existiam no disco. Todas lidas por `git show origin/main:<arquivo>` (`ecdab8d41`); nada alterado no privado. Vale para as próximas frentes: ler as fontes do `origin/main` do privado.
- 2026-10-30 — Brainstorm da F7 (`sdd/features/BRAINSTORM_F7_EVIDENCIA.md`), 5 decisões do Roberto: **D4** = `report-lint` fail-closed sempre, com a forma mínima declarada (tabela reconhecida + linha do avaliador; as 32 asserções ficam, só os helpers dos 11 testes que esperam 0 mudam); **D11** = só o slot `evidence.require_avaliacao_layers: 2` (os 3 caminhos ficam fixos, como a KB); **E6** = regra na F7 (`report-lint.py --stdin`), adaptador `.claude/settings.json` **na F8**; versão **`v2.2.8` automática** (contra a recomendação de `v2.3.0` por tag); amostras = casos do privado + relatórios e logs do open. Abordagem A (porte por função, um ciclo).
- 2026-10-30 — Define da F7: correção de premissa do checkpoint 2 — os logs do open **não** dão 0 acusações no `gate-shell-evidencia.sh` (19 linhas, medidas; o `awk` do macOS ainda quebra com UTF-8 sem `LC_ALL=C`). No build, mais 3 linhas `exit=` vazias apareceram (22); os ciclos da revisão do build moveram o corpus para 21 e de volta para 22, com a lista exata em `sdd/reports/evidence/F7_EVIDENCIA/corpus-esperado.txt` (DEFINE v1.5).
- 2026-10-30 — Revisão do DESIGN da F7 em contexto fresco (modo contrato): NEEDS_WORK, 2 HIGH, 4 MEDIUM, 8 LOW, aplicadas antes do build (DESIGN v1.1, DEFINE v1.2). H1: o `(rc=N)` do `verify-gate.sh` é o rc bruto do comando (crash também sai 2) — o `gate-baseline.sh` só aceita `🔴` ou marcador de asserção. H2: o trace (`sdd/traces/`) faria o `avaliador-guard.sh` mandar commitar em todo build — `sdd/traces/` é permitido.
- 2026-10-30 — Build da F7: P1 achado e corrigido — o `verify-gate.sh` da `v2.2.7` não achava o DEFINE quando chamado de uma subpasta com caminho relativo. Revisão do build: ciclo 1 sobre `514324f` NEEDS_WORK (3 MEDIUM, 6 LOW), aplicados em `bed1f69`; ciclo 2 sobre `bed1f69` NEEDS_WORK (3 MEDIUM, 3 LOW, um deles regressão da correção do LOW-2 do ciclo 1), aplicados em `1d225e5`. 0 HIGH nos 3. O ciclo 2 caiu uma vez por ECONNRESET (rede por celular) e foi retomado com o mesmo contexto. Roberto: "seguir para a release sem 3º ciclo" (recomendado; a `sdd-build` limita a 2 ciclos).
- 2026-10-30 — Roberto: "finalizar (push + deploy + verificar) do sdd-open". CI do PR #9 verde (run 41126526373: `gate` e `Testes no piso (macOS)`). Push fast-forward `1c9bbc7..1d225e5` em `main`; PR #9 MERGED; run `release` 41133637690 (testes, testes no piso macOS, publicar) verde; publicou `v2.2.8`.
- 2026-10-30 — O plano (`PLANO_F4_F15_CONSOLIDADO.md`, quadro F8) ganhou o adaptador do Claude Code da E6, transferido da F7.
- 2026-10-30 — Prompt da sessão 6 (F8 Hooks) gravado em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`; a worktree `sdd-open-f8-hooks` **não** foi aberta (o prompt traz os comandos para criá-la de `origin/main` = `1d225e5`).
- 2026-10-30 — Roberto perguntou se F8 e F9 cabem na mesma sessão. Recomendação: não juntar (as duas são grandes — ~2 e 3–4 dias no PORTE —, ambas mexem em skills e `check-versions`, e a F9 depende da F8 publicada); começar a F9 na mesma sessão só depois da Release da F8, se sobrar contexto (regra do par, plano seção 10). Roberto: "/sdd-new-session F8 . documente. escreva o prompt para iniciar F8 em uma sessao nova" — a F8 vai sozinha na sessão 6.
- 2026-10-30 — Frente F8 aberta com a `sdd-new-session` (starter 1.3.0): pré-voo verde (`checar.sh --frente` 0); worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks`, branch `feat/f8-hooks` nascida de `origin/main` = `1d225e5`, nomes no padrão da família (lidos de `sdd/ambiente.md` do checkout principal, cenário B); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. O prompt da sessão 6 passou de "crie a worktree" para "confira a worktree". O `handoff-lint.py` do open reprova este handoff pelo molde (sem `Verify Gate` na ficha, sem `## Prompt de retomada` e sem `## Histórico de slices`) desde as sessões anteriores: o arquivo segue o molde da `sdd-handoff` do starter (`validate_handoff.py` PASS); fica registrado, sem mudança.
- 2026-10-30 — Brainstorm da F8 (`sdd/features/BRAINSTORM_F8_HOOKS.md`), decisões do Roberto, todas na opção recomendada: **D3** sim — hooks pelo `init`, dentro do plano, com confirmação; **D10** dispatcher em `sdd/hooks/pre-commit` que chama o `pre-commit.sh` da higiene quando ela está ligada (`git config sdd.higieneDado on`), e o `alarme.sh` reconhece `sdd/hooks` como seu; **D11** slot `project.context_file_max_kb` com default 100; **E6** merge em `.claude/settings.json` + 2 scripts gerados em `.claude/hooks/`, no mesmo ciclo; Release **`v2.2.9` automática**; `pre-push` só avisa base velha; o Define leva como requisito a linha do plano do `init`, a mensagem de recusa e a linha do `doctor`. O Roberto lembrou que o público é aluno do Bravo, contador: a recusa explica "Por que importa" e o conserto de cada classe, sem jargão. Abordagem A (dispatcher em bash, regras como funções, um ciclo).
- 2026-10-30 — Revisão do DESIGN da F8 em contexto fresco (modo contrato): NEEDS_WORK, 3 HIGH, 2 MEDIUM, 10 LOW — 14 aplicadas, 1 rebatida por escopo; contrato de aceite com 5 ajustes ACEITOS (DEFINE v1.2, DESIGN v1.1). H1: o `init` copia `sdd/fixtures/evidencia/BUILD_REPORT_*.md` para o projeto e os 4 reprovam no `report-lint` — o 1º commit depois do `init` seria recusado; a regra REPORT pula `sdd/fixtures/`. H2: `TestCopiaGerada` do `test_alarme.py` exigia o arquivo em `.git/hooks/` e necessariamente muda (reescrita para o modo hooks; 28 testes intactos). H3: `git rev-parse --git-path hooks/pre-commit` **segue o `core.hooksPath`** e o `desinstalar` apagaria o dispatcher — `alarme.sh` e `pre-commit.sh` passam a usar `--git-common-dir`. M1: o G1 do gate (gitleaks) varre `tests/` — credenciais de teste geradas em execução. M2: H6 recusa o commit do `init` em `main` com remoto — o `→` ensina `git switch -c`.
- 2026-10-30 — Build da F8 (`6a238d2`), 4 drifts registrados: o molde `sdd/templates/BUILD_REPORT_TEMPLATE.md` também casa `BUILD_REPORT_*.md` e o `init` o copia — `sdd/templates/` entrou na exceção do hook e do guard (DEFINE AT-013/AT-023); `AVISOS="$AVISOS⚠️…"` no bash 3.2 cola o byte não-ASCII ao nome da variável (o nome passou a ir entre chaves antes do emoji); um teste do `doctor` commita um `.p12` que o gitleaks (`pkcs12-file`) passa a recusar — commita com `--no-verify`, registrado no teste; `import os` faltando. Revisão do build: ciclo 1 sobre `6a238d2` NEEDS_WORK (1 MEDIUM: o `init` escrevia `.claude/settings.json` sem conferir a forma; 5 LOW), aplicados em `938ce47`; ciclo 2 sobre `938ce47` **PASS** (2 LOW: H3 olhava só a 1ª ocorrência; `sdd/hooks/` e `./sdd/hooks` como nosso), aplicados em `7c640eb`. 0 HIGH nos 3.
- 2026-10-31 — Roberto: "push sdd-open". CI do PR #10 verde (run 41154964749: `gate` e `Testes no piso (macOS)`). Push fast-forward `1d225e5..7c640eb` em `main`; PR #10 MERGED; runs `release` 41185402408 e `publish-gate` 41185402393 verdes; publicou `v2.2.9`.
- 2026-10-31 — Prompt da sessão 7 (F9 Fluxo encadeado) gravado em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`; a worktree `sdd-open-f9-fluxo` **não** foi aberta (o prompt traz os comandos para criá-la de `origin/main` = `7c640eb`).
- 2026-10-31 — Frente F9 aberta com a `sdd-new-session` (starter 1.3.0): pré-voo verde (`checar.sh --frente` 0); worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo`, branch `feat/f9-fluxo` nascida de `origin/main` = `7c640eb` (tag `v2.2.9`), nomes no padrão da família (lidos de `sdd/ambiente.md` do checkout principal, cenário B); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. O prompt da sessão 7 passou de "crie a worktree" para "confira a worktree". A worktree da sessão 6 (`sdd-open-f8-hooks`, branch já mesclada) continua no disco até a limpeza.
- 2026-10-31 — Sessão 7 (F9): o Codex CLI 0.163 está instalado nesta máquina; as fontes do privado foram lidas do `origin/main` dele (`1b1c1d41b`), sem alterar nada. `sdd-fluxo.sh` e `sdd-decisoes-lint.sh` do privado são zsh + perl: o porte virou bash 3.2 com o núcleo em Python stdlib embutido.
- 2026-10-31 — Brainstorm da F9 (`sdd/features/BRAINSTORM_F9_FLUXO.md`), 5 decisões do Roberto, todas na opção recomendada: **D1** = `flow.autonomous: false` por default (configurável); **D11** = slots `flow.autonomous` e `review.security_globs` com os 8 termos genéricos fixos no script e `layers.sql` contando como segurança; prova no Codex = **fixture no `--self-test` e execução real do `codex exec`**; a seção encadeada entra como **subseção `### Fluxo encadeado` dentro do `## Encerramento (obrigatório)`**, depois do Próximo passo; versão **`v2.2.10` automática**. Amostras: 2 ledgers e o DOGFOOD do privado, reescritos sem dado da RDD. Abordagem A (porte por mecanismo, um ciclo). O Roberto pediu define → ux-review → design → revisão do design → build → revisão do build em sequência.
- 2026-10-31 — Define/UX/Design da F9: a UX review pediu a marca **com rótulo fixo** por classe (`[D1 · não se desfaz]`; a marca crua era jargão no lugar mais visível) e a linha de transição dizendo por que não perguntou; o Design achou que o `verify-gate.sh --print` sai 64 fora de git, que a pergunta de decisão se identifica pela linha com `**Sua decisão**` (a heurística da `kb-protocol.md` e o OK da `sdd-release` ficam de fora; o OK é D1 por construção e contrato do `test_contrato_build_release`), e criou o verbo `estado`. A F6 (decidir sozinho no `sdd-design`) ficou **só com o encadeamento ligado** (regra 8 do 8.0). Revisão do DESIGN em contexto fresco: NEEDS_WORK, 3 HIGH (o `seguir` não lia o Status nem a revisão do DESIGN; AT-001 sobre `sdd/features/`, fora do `git archive`; `codex exec` sem `.git`), 2 MEDIUM, 10 LOW, todas aplicadas (DESIGN v1.1, DEFINE v1.3).
- 2026-10-31 — Build da F9 (`bb91c42`): **A-003 falsa** — com `--disable multi_agent`, o Codex 0.163 ainda abriu um colaborador e seguiu o degrau 1 da escada (`codex-despacho-subagente.log`); a prova do exit 40 pôs "sem subagente nem colaborador" no prompt (`codex-despacho-40.log`, PASS). A linha "Codex sem subagente" da tabela 8.0 do plano estava velha (corrigida no plano). Revisão do build: ciclo 1 sobre `bb91c42` NEEDS_WORK (1 HIGH: `loop --log` não regravava no 64; 2 MEDIUM; 12 LOW), aplicados em `524f957`; ciclo 2 sobre `524f957` NEEDS_WORK (1 HIGH de **regressão** da correção de um LOW: a faixa `[A-Za-z]` do `case` aceita letra acentuada no bash 3.2 com locale UTF-8; 1 MEDIUM; 4 LOW), aplicados em `daf9c0f`. O ciclo 2 caiu 2 vezes por rede (ENOTFOUND) e foi retomado com o mesmo contexto.
- 2026-10-31 — Roberto, à pergunta D4 sobre um 3º ciclo: "OK citando \"sdd-open\"" — seguir sem 3º ciclo e publicar. CI do PR #11 verde (run 41245908615). Push fast-forward `7c640eb..daf9c0f`; PR #11 MERGED; o run `release` 41246920990 **cancelou** o job de testes do Ubuntu no `timeout-minutes: 10` (744 testes ≈ 12 min) e **não publicou**. Roberto: "autorizado sdd-open" para corrigir o teto (25 min, `89ac76f`, PR #12 com CI verde) e publicar por tag: push `daf9c0f..89ac76f`, tag `v2.2.10` em `89ac76f`, run `release` 41251612805 verde; publicou `v2.2.10`.
- 2026-10-31 — Frente F10 aberta com a `sdd-new-session` (starter 1.3.0): pré-voo verde (`checar.sh --frente` 0); worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao`, branch `feat/f10-revisao` nascida de `origin/main` = `89ac76f` (tag `v2.2.10`), nomes no padrão da família (lidos de `sdd/ambiente.md` do checkout principal, cenário B); os artefatos SDD da branch `docs/incorporar-starter` já copiados para lá, fora do commit. O prompt da sessão 8 passou de "crie a worktree" para "confira a worktree".
- 2026-11-01 — Sessão 8: chave da OpenRouter em `~/.config/rdd-eval.env` (`OPENROUTER_API_KEY`), lida só para o ambiente do processo das revisões reais; nunca gravada. Fontes do privado lidas do `origin/main` dele, sem alterar nada.
- 2026-11-01 — Brainstorm da F10 (`sdd/features/BRAINSTORM_F10_REVISAO.md`, cobre também a F11), decisões do Roberto, todas na recomendada: **D2** = as 4 engines no registry, **sem cadeia padrão**; **D11** = 5 slots (`review.registry`, `revisor1`, `auditor`, `output_dir`, `context_max_kb`), o resto em constantes; **R1** = review externo **sempre** exigido na release, com dispensa registrada (D3); **F10 + F11 compromissadas** na sessão (regra do par); versão = **`v2.3.0` por tag** para a F10 e **`v2.3.1` automática** para a F11; amostras = as da tabela, generalizadas; abordagem A (reescrita pelo contrato, um adapter por engine); 2 checkpoints.
- 2026-11-01 — F10: revisão do DESIGN em contexto fresco (NEEDS_WORK, 1 HIGH, 5 MEDIUM, 13 LOW, aplicadas); build `7ecbc78`; revisão real AT-040 (8 achados aplicados, `6f4ee5b`); avaliador ciclo 1 (1 HIGH: 2º revisor sem engine dava PRONTO, `9846919`) e ciclo 2 (1 MEDIUM: índice copiado sem mtime perdia edição "racy", `486ed2e`); 3 rodadas da revisão real (claude + codex → openrouter:qwen): rodada 1 com 2 HIGH (`1975e7c`), rodada 2 com 1 HIGH (`248301d`), rodada 3 PRONTO com 4 MED e 3 LOW (6 adiados para a F11, 1 rebatido). Custo das 4 revisões reais ≈ US$ 9,57 (US$ 0,20 de OpenRouter).
- 2026-11-01 — Roberto, à pergunta D4 sobre um 3º ciclo do avaliador da F10: "ok sdd-open" → seguir sem 3º ciclo. CI do PR #13 verde (Ubuntu 12m50s, macOS 18m31s). Bloco do OK mostrado; Roberto: "ok para sdd-open". Push `89ac76f..248301d` em `main` + tag `v2.3.0` (`git push --atomic`); runs `release` 41294116610 (tag) e 41294117050 (main) verdes; publicou `v2.3.0`.
- 2026-11-01 — Roberto: "comece f11". Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f11-gate`, branch `feat/f11-gate` de `origin/main` = `248301d`, artefatos copiados da worktree da F10. DEFINE próprio (`DEFINE_F11_GATE.md`), decisões do Roberto: **`eval-agree` só lê revisões já feitas** (sem `--executar`) e o **`--no-revisor2` com gatilho exige motivo na release** (`--aceitar-sem-revisor2`), não na flag. UX review N.A. (saída no padrão `RESULTADO:` + `→` já revisado na F10).
- 2026-11-01 — F11: revisão do DESIGN em contexto fresco (NEEDS_WORK, 2 HIGH — `BASH_ENV`/função exportada faziam a CLI real ser chamada; o servidor da OpenRouter não via a fila por cenário —, 3 MEDIUM, 7 LOW, aplicadas); build `84cf6b5`; avaliador ciclo 1 (1 MEDIUM: gate só via AGREE; 4 LOW, `a9813ff`) e ciclo 2 (1 HIGH: o gate herdava `GIT_DIR` de um hook numa worktree e commitava no repositório do usuário; 1 LOW, `06e5a9d`); 3 rodadas da revisão real, 0 HIGH (rodada 1 `ab2f252`, rodada 2 `9508ff0`, rodada 3 PRONTO com 2 notas rebatidas com evidência). Custo das 3 rodadas US$ 3,48 (US$ 0,08 de OpenRouter). O `eval-agree` sobre as 4 revisões reais da F10: openrouter (qwen/qwen3.7-plus) com `taxa_agree` 81,2%.
- 2026-11-01 — CI do PR #14 verde (Ubuntu 12m53s, macOS 17m31s). Bloco do OK; Roberto: "Sim sdd-open". Push `248301d..9508ff0` em `main`; run `release` 41307505438 verde; publicou `v2.3.1`. Roberto: "prosiga" → handoff e gravação na branch `docs/`.
- 2026-11-01 — Roberto perguntou se F12 e F13 cabem numa sessão. Recomendação: não como compromisso — a F12 é a maior frente que falta (5–7 dias no PORTE, cartógrafo e revisor de governança provados no Codex com exit 40, exit 5 no Define), as duas mexem na `sdd-design`/`DESIGN_TEMPLATE.md` e no `check-versions`, e a F13 traz a skill nova `sdd-loop-builder` com decisões próprias (slots `smoke.*`/`prompts.*`, U3); no máximo F12 e, se sobrar folga, F13 depois da Release da F12 (regra do par). Roberto: "documente tudo. escreva o prompt para começar F12" — a sessão 9 faz a **F12**; a F13 fica para a sessão 10, salvo pedido do Roberto na própria sessão. Sessão 9 marcada na agenda do Roberto para 2026-11-04, 13:00.
- 2026-11-02 — Auditoria de leitura do sdd-starter (`17c69c4`, v1.5.15), pedida pelo Roberto: `git` é conferido no início da `sdd-checar-ambiente` e da `sdd-iniciar-repo`; o `gh` não. Na `sdd-checar-ambiente` ele só aparece quando o remoto já recusou o acesso; na `sdd-iniciar-repo`, só no Passo 6 (publicar). A `sdd-new-session` funciona sem IDE, mas o item 6 diz `code <pasta>`, perde VS Code/Cursor fora do `PATH` no macOS, tem lista fechada de editores e o aviso final presume janela nova. Roberto: "sdd-starter agnóstico e proativo. documente. vamos implementar" — primeiro foi aberta uma frente no starter (`feat/agnostico-proativo`) e, nesta família, a **F16** (a F15 já era a substituição do privado; Roberto escolheu F16). Repensado na mesma sessão: pela **Decisão 5** a fonte é o Open, então a F16 **implementa no Open**, e o starter recebe tudo pela nova **F17 Starter gerado a partir do Open** (a Decisão 5 não tinha número nem lugar na sequência). Roberto: o aluno do starter fica sem os ajustes até a F17 sair; sem remendo no starter. A frente do starter foi removida sem código (worktree e branch local; nunca houve push). Escopo da F16 com os achados em `origin/main` = `9508ff0` em `sdd/features/ESCOPO_F16_AMBIENTE.md`. Plano v1.4: quadros F16 e F17 na seção 8, sequência na seção 3, linhas na seção 10. Correção: as versões das 3 skills no `main` do Open são `checar-ambiente` 1.4.1, `iniciar-repo` 1.1.1, `new-session` 1.3.0 (as cópias desta branch `docs/` são antigas).
- 2026-11-03 — Sessão 9: F12 sozinha. Brainstorm com D5, D8, DEFINE antigo trava sempre, `schema.check_cmd` cai, uma Release só, `v2.4.0` por tag, todas na opção recomendada, menos a Release: o recomendado eram 2 e o Roberto escolheu 1. Pediu "grave o brainstorm e execute o define, ux-review, design, review do design, build, review do build".
- 2026-11-03 — Depois da rodada 3 (`loop` PRONTO, 8 achados sem HIGH), a recomendação foi publicar e corrigir num patch; o Roberto escolheu "corrigir agora e rodar a 4ª rodada" (D4). A rodada 4 achou 1 HIGH, regressão do conserto; à nova D4, "continue" foi lido como a opção recomendada (rodada 5). A rodada 5 achou mais 1 HIGH; à 3ª D4, "continue" foi lido como a opção recomendada (publicar com a revisão dispensada).
- 2026-11-03 — A prova no Codex sobre `3ebeeea` deu PASS falso: o snapshot estava no `.git`, só leitura na sandbox, e nenhum despacho aconteceu. Corrigido em `96a97ec` (pasta temporária) e no critério do `codex.sh`. O CI cancelou o macOS nos 30 min no PR #15; 2ª tentativa em 27m06s; teto de 45 min em `6b7633c`.
- 2026-11-03 — Roberto: "se tudo ok, release previamente autorizado"; sem o nome do repositório, a regra pediu a citação; "release ok sdd-open". Push `9508ff0..6b7633c` + tag `v2.4.0`; publicou `v2.4.0`.

- 2026-11-04 — Sessão 10: F13 sozinha. Brainstorm: U3 fora e `smoke.*` caem (vai para a F15); só `prompts.wrapper_pattern`; `v2.5.0` por tag; `#777777` é 4.47, truncado (o plano dizia 4.48, corrigido); abordagem A (porte enxuto), todas na opção recomendada. O Roberto pediu explicação para leigo, prós e contras e recomendação nas decisões seguintes.
- 2026-11-04 — A 3ª rodada da revisão real deu PRONTO no teto, com 1 MED e 3 LOW; D4 do Roberto: corrigir e rodar a 4ª. A conta do Codex ficou sem créditos no meio dela; D4: "dispensar o 2º revisor e aceitar a prova anterior" (contra a recomendação de repor os créditos).
- 2026-11-04 — Depois do ciclo 2 do avaliador em NEEDS_WORK, o agente seguiu sem a pergunta D4 que o método exige; reconheceu ao escrever o relatório e perguntou. D4: 3º ciclo. Ele achou 1 MEDIUM, regressão de um conserto do ciclo 2; "Confirmo" foi lido como a recomendada (consertar e rodar a 6ª, sem 4º ciclo).
- 2026-11-04 — A repetição da prova no Codex em `cdb85a9` sobrescreveu os transcritos de `867d6de` (mesmos nomes de arquivo). Relatado no bloco do OK; `prova-real-resumo.md` diz o que existe. Roberto: "Autorizado sdd-open". Push `6b7633c..b1348bd` + tag `v2.5.0`; publicou `v2.5.0`.

- 2026-11-05 — Sessão 11: F14 dividida em 2 entregas (decisão do Roberto no brainstorm); a `F14_DRIVE` sai na sessão 12. D11: só `drive.max_rounds`.
- 2026-11-05 — Ciclo 2 do avaliador em NEEDS_WORK: D4 do Roberto, 3º ciclo focado; depois dele, sem 4º ciclo, seguindo para a revisão paga e a prova real. "pode ir para quarta": revisão real até a 4ª rodada.
- 2026-11-05 — Os créditos do Codex, repostos pelo Roberto, serviram às rodadas 1 e 2 e acabaram na 3 (conferido). A rodada 4 e a prova usam `deepseek/deepseek-v4-pro` pela OpenRouter, caminho já escolhido por ele.
- 2026-11-05 — Rodada 4: 1 HIGH falso do DeepSeek, rebatido por medição, e 5 achados de Claude. Consertar exigiria 5ª rodada: D4 do Roberto, "A — Publicar como está", com os 5 como primeira tarefa da `F14_DRIVE`.
- 2026-11-05 — Roberto: "release previamente autorizado quando tudo ok", sem o nome do repositório, não valeu; "release autorizado sdd-open". Push `b1348bd..8a320e9` + tag `v2.6.0`; publicou `v2.6.0`.
- 2026-11-05 — Curadoria real: Roberto aceitou as 2 lições e deixou o envio para a próxima publicação; commit `252d351` fica na branch da frente.
- 2026-11-05 — Roberto: "encerre e limpe aqui". Revisões, trace e registro arquivados em `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_PLAYBOOK-revisoes-traces.tar.gz`; 3 arquivos da rodada 4 copiados para a evidência; worktree `sdd-open-f14-playbook` removida; branch local `feat/f14-playbook` mantida, por causa do `252d351`.
- 2026-11-05 — Sessão 12: curadoria da F14 Playbook levada como `aabc4a3` e os 5 achados da rodada 4 consertados em `3331b6c`. Brainstorm da `F14_DRIVE`: drive inteiro; rodada = passada inteira + gate; só as 2 pendências que tocam o drive; 2º revisor pelo DeepSeek na OpenRouter; `deploy.workflow` e `deploy.transient_steps`; "o script decide, o agente faz". No DEFINE: gate alterado durante a execução para e pergunta. No build: uma sessão só.
- 2026-11-05 — Avaliador, D4 do Roberto: 3º ciclo focado. Ciclo 3: 0 HIGH, 5 MEDIUM, 14 LOW, aplicados em `68d2341`.
- 2026-11-06 — **Erro do agente, corrigido com o Roberto:** disse que o saldo da OpenRouter estava folgado (US$ 220) e que a queda do DeepSeek era passageira. US$ 220 era o limite da chave; o saldo tinha acabado (HTTP 402). O Roberto repôs US$ 10; saldo depois da rodada 5, cerca de US$ 9,90. Virou a lição LM-008.
- 2026-11-06 — Revisão real: a rodada 4 achou 3 HIGH do Codex e ficou sem auditor por falta de crédito. D4 do Roberto: consertar, repor crédito e rodar a 5ª, acima do teto. A rodada 5 deu `--conferir` CONFERE, `loop` BLOQUEADO e 5 achados. D4 do Roberto: "Publicar como está", com os 5 como primeira tarefa da sessão seguinte.
- 2026-11-06 — Roberto: "Autorizado sdd-open". Push `8a320e9..b0663d3` + tag `v2.7.0`; publicou `v2.7.0`. PR #18 MERGED.
- 2026-11-06 — Curadoria real: Roberto aceitou as 2 lições (LM-007, LM-008) e deixou o envio para a próxima publicação; commit `b3526ae` fica na branch da frente.
- 2026-11-06 — Plano da sessão 13: a tarefa 1 e o brainstorm da F15 rodam na worktree do sdd-open, só lendo o privado; a execução da F15 fica para uma sessão aberta em worktree do privado, porque a sessão fica presa à pasta em que abriu. Fatos conferidos em `origin/main` do privado (`68c630d3f`) corrigem o plano: `audita-schema-gate.sh`, `gate-sdd-open-s1.sh` e `gate-sdd-prompt-builder.sh` estão em `scripts/gates/`; `.claude/kb/` tem 51 pastas, não 46.
- 2026-11-06 — Roberto pediu para documentar, retomar no domingo e, se possível, encerrar e limpar. Retomada marcada para 2026-11-08, com lembrete na Agenda Google às 09:00 (horário escolhido pelo agente, sem bloquear a agenda). Worktree `sdd-open-f14-drive` removida; branch local `feat/f14-drive` mantida, por causa do `b3526ae`. Volta pelo script `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/retomar-sessao13.sh`.
- 2026-11-07 — Roberto, numa sessão do repositório privado, depois de publicar o e-book *Construir com IA sem Deixar a Porta Aberta* (acervo RDD10+) e de pedir a avaliação de como alertar os alunos sobre esses riscos no sdd-starter: "podemos incluir isso ao final da frente?". Pela Decisão 5 a mudança é no Open. Plano v1.5: entra a **F18 Segurança embutida no fluxo** (seção 8, depois da F17; linha nova na seção 10), com a cobertura medida em `b0663d3`, três ondas (piso de alerta no `sdd-release`, alerta antecipado no brainstorm/define/design, prova no Verify Gate) e cinco decisões para o brainstorm dela. O campo "Falta" ganhou a F18 no fim da fila; a sessão 13 continua F14 → F15. A recomendação da avaliação é trazer a onda 1 para antes da F17, para o aluno do starter receber o alerta já na 1ª geração; a decisão fica para o brainstorm da F18.
- 2026-11-07 — Sessão 13, no meio da tarefa 1, Roberto: "incorpore na documentação da frente, após a última F, incluir: 1. avaliação de performance de modelos de revisão: custo e benefício [...] 2. incorporar no sdd-starter e no open ações preventivas citadas no ebook-seguranca-construir-com-ia". Plano v1.6: **F19 Custo e benefício dos modelos de revisão** (custo por engine e falhas reais com potencial de dano, medidas por `META.txt` e ledger, critério de dano e coluna `dano` a decidir) e **F20 Ações preventivas do e-book** (o "Como evitar" e as frases dos caps. 3–28 onde o agente constrói; a F18 só alerta). A F20 fica com brainstorm conjunto proposto com a F18 e chega ao starter pela F17 (Decisão 5); edição direta no starter fica como pergunta do brainstorm. O campo "Falta" ganhou as duas no fim da fila; a sessão 13 continua F14 → F15.
- 2026-11-07 — Sessão 13, tarefa 1: os 5 achados da rodada 5 e o teste do slice consertados em `5a1e3fc`. No R1@codex, a trava de estado do drive virou a do sistema operacional (`flock`), não "pid + checar se vive", porque a tomada por pid tem corrida própria (dois veem o dono morto e os dois tomam). D3 do Roberto: 1 rodada de revisão real (recomendada).
- 2026-11-07 — Rodada 6: PRONTO, 3 achados pequenos aceitos pelo auditor. D4 do Roberto: consertar e rodar a 7ª (recomendada); `3d69536`. Rodada 7: PRONTO, `--conferir` CONFERE; 2 achados rebatidos por medição; 1 real só no Windows nativo (sem `O_NOFOLLOW`). D4 do Roberto: publicar e deixar pendente (recomendada).
- 2026-11-07 — Sessão 13, tarefa 2: brainstorm da F15 com o Roberto, todas as recomendadas: convivência até o fim (sem data-limite), prova com feature nova de 2 camadas, documentos divididos (o `sdd-open` e a branch `docs/` são públicos), abordagem A por fases, 3 slots de extensão na release, OK por publicação, linha de base para vermelho herdado, D7 por patch com OK, worktree pelo `/new-session` do privado.
- 2026-11-07 — O Verify Gate de `3d69536` saiu vermelho uma vez por `test_duas_chamadas_juntas_repetem_uma_vez` (teto de 1 s) com a revisão rodando ao mesmo tempo; sozinho passou 5 de 5; log guardado como `verify-gate-3d69536-sob-carga.log`, gate repetido sem carga. PR #19 aberto; CI Ubuntu verde.
- 2026-11-07 — Roberto: "documente tudo. vou embarcar daqui a pouco". Sessão 13 fechada sem a `v2.7.1`: a publicação exige o OK dele citando "sdd-open" depois do bloco do OK, e fica para a sessão 14.
- 2026-11-07 — Roberto voltou antes de embarcar e pediu para continuar: sabotagens (9 de 10 derrubam teste; viva a do `samestat`), CI do PR #19 verde (Ubuntu 18m21s, macOS 38m35s), bloco do OK. "pode" não citava o repositório e não valeu; "sdd-open autorizado": push `b0663d3..3d69536` em `main`; run `release` 42437407177 e `publish-gate` 42437407206 verdes; **Release `v2.7.1`** em 2026-11-08T02:46:40Z, `shasum -a 256 -c` OK. Curadoria: 1 sugestão descartada, nada aplicado.
- 2026-11-08 — Roberto, pela `/sdd-new-session`: "escreva o prompt para iniciar a sessão subsequente [...] abra o cursor na worktree correta". Lido como o OK para a 1ª alteração no privado: worktree `/Users/robertoduarte/rdd-worktrees/f15-substituicao`, branch `feat/f15-substituicao`, criada pelo `scripts/new-session.sh` do privado (`RDD_EDITOR=cursor`) a partir do `origin/main`; aberta no Cursor; baseline de edges 465. Nada enviado ao remoto.
- 2026-11-08 — Roberto: "podemos encerrar e limpar aqui?". As 7 pastas `EXTERNAL_REVIEW_*`, o trace e `sdd/releases/` (ledgers e `CURATOR-colhidos.txt`) arquivados em `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_DRIVE-v2.7.1-revisoes-traces.tar.gz`; documentos conferidos por checksum contra a branch `docs/`; worktree `sdd-open-f14-drive` removida e branch local `feat/f14-drive` apagada (já no `main`). Ficam para o Roberto decidir: a worktree `sdd-open-docs-f16`, a branch local `feat/f14-playbook` e a branch remota `feat/f14-drive-v271`.
- 2026-11-07 — Roberto perguntou por que não há teste em Windows e pediu incluí-lo em alguma frente. Medido: o `README.md:89` promete Windows (Git Bash/WSL) e o CI só tem `ubuntu-latest` e `macos-latest`; nada do pacote rodou em Windows. Plano v1.7: entra na **F16** (item 5 da Entrega; `ESCOPO_F16_AMBIENTE.md` §3.5): job `testes-windows` primeiro informativo, depois a decisão entre Windows como piso testado ou README dizendo "sem teste automático"; a frase do README corrigida no 1º commit da F16.
- 2026-11-08 — Sessão 14 (F15 fase 1, no privado): Open v2.7.1 instalado pelo `init --vendors claude` (hash conferido), ponte `sdd-public/` removida, `sdd/config.yaml` preenchido, linha de base de testes pelo `test-baseline.sh` (o `gate-baseline.sh` prova dentes e não trata vermelho herdado: o prompt da sessão 14 citava o script errado). Decisões do Roberto que mudam o plano: ganchos ficam no gerenciador existente chamando o `sdd/hooks/pre-commit` (inverte a direção da decisão 9 do brainstorm: o `core.hooksPath` é comum a todas as worktrees, e as frentes antigas ficariam sem gancho); landmines, invariantes e patterns do privado seguem fonte única onde estão até a fase 4 (o lint do Open recusa as seções do privado e os LM-001 a LM-008 colidem). Achados 2 defeitos genéricos do Open, que viram a v2.7.2 antes do merge: guarda e pre-commit de BUILD_REPORT casam pelo nome em qualquer pasta; o `doctor` avisa ⚠️ mesmo com a linha encadeada que ele próprio pede.
- 2026-11-08 — Sessão 14, continuação: **v2.7.2** a partir da worktree `sdd-open-v272` (branch `fix/guardas-pasta-e-gancho-encadeado`, PR #20): guardas de BUILD_REPORT só em `sdd/reports/`; `doctor` reconhece o gancho encadeado (linha que começa pela chamada; `core.hooksPath` alheio, `.git/hooks` e husky v9 pelo desenho da pasta de stubs; `~/` expandido; limite declarado: lê texto, não executa). 11 sabotagens, todas mortas; Verify Gate em `9d8ac24` por `git archive`: 1.669 testes, exit 0 (`sdd/reports/evidence/V272_GUARDAS/`). Revisão real em 7 rodadas (claude + codex + qwen, ~US$ 2,4, 0 grave; ledger `V272_GUARDAS/ledger-review.md`); Roberto: "rodada 7 é a última" — veio limpa, PRONTO e CONFERE. CI do PR: Ubuntu 19m47s; macOS estourou o teto de 45 min na 1ª tentativa (cancelado) e passou em 36m46s na repetição. "SDD-open autorizado": push `3d69536..9d8ac24`, run `release` 42496413943 (macOS 42m35s, a 2,5 min do teto), Release `v2.7.2` em 2026-11-08T16:28:12Z, SHA-256 `05042aa6264826eee86cf8ce26ddee0ad980ac69fef2e388ea78394c71e36c8b` conferido. **Alerta para a F16:** o macOS do CI está no limite do teto de 45 min. Roberto pediu também um **inventário de saída** do privado antes da fase 4 ("para quando deletar o privado não perdermos nada").
- 2026-11-09 — Roberto, numa sessão do repositório privado: "há uma skill nova para o sdd-start e sdd-open: sdd-engenharia-reversa-saas-1.0.0.zip [...] ela pode (opcionalmente) ser usada antes do brainstorm. inclua uma frente para incluir essa skill nos 2 SDD e na pagina da plataforma que ensina a usar". Plano v1.8: **F21 Engenharia reversa de SaaS antes do Brainstorm** (seção 8, depois da F20; linha na seção 10). Skill lida inteira; 18 testes próprios verdes; zip SHA-256 `f5ffd2a7…52eb3`. Decisão aberta para o brainstorm: starter já nesta frente (skill nova, sem texto anterior para divergir) ou só pela F17.
- 2026-11-10 — Roberto, numa sessão do repositório privado: "ajuste a documentação para mantermos uma só fonte da verdade das frentes". Havia 3 worktrees com edições diferentes e sem commit do mesmo `PLANO_F4_F15_CONSOLIDADO.md`. Plano v1.9: a seção **Estado das frentes** do plano passa a ser a única lista de frentes com estado; ela só é editada na worktree `sdd-open-docs-f16` (checkout de `docs/incorporar-starter`), com commit e push na mesma sessão. Esta ficha continua guardando a narrativa por sessão, mas **o estado de cada frente se lê lá**. A F21 (plano v1.8), que só existia sem commit na worktree `sdd-open-docs-f21`, foi commitada; a worktree e a branch local `docs/f21-engenharia-reversa` saíram.
- 2026-11-10 — Roberto, numa sessão do repositório privado, depois da fase 3 da F15 (prova publicada no privado em v1.492.1): F21 + F19 numa sessão só (pequenas, sem arquivo em comum; F16 em sessão própria). Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19`, branch `feat/f21-engenharia-reversa` de `45e27a9`; a F19 nasce na mesma pasta depois da release da F21. A curadoria `c2560fc` e o ajuste "itens 1 a 6b" da `sdd-release` sobem com a release da F21. Prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`.

- 2026-11-09 — Roberto pediu as 3 lacunas genéricas do inventário de saída da F15 (L0 smoke, L3 testes do diff, L4 checagem de migration) numa release própria do Open. Brainstorm, Define e Design da F15_SLOTS numa frente só; `smoke.*` e `schema.check_cmd` **reabertos por decisão do Roberto** (§8.2 do plano). Documentos na branch nova `docs/f15-slots`, porque a `docs/incorporar-starter` está em uso na worktree `sdd-open-docs-f16`.
- 2026-11-10 — Build da F15_SLOTS: avaliador fresco em 2 ciclos (PASS), revisão paga em 4 rodadas (codex sem cota; auditor qwen; 2º revisor dispensado na rodada final por D3 do Roberto). Um erro do build: o script de sabotagem desfez consertos não commitados; restaurados de cópia, viraram a LM-009. Roberto: "finalizar (push + deploy + verificar) sdd-open"; PR #21, push `9d8ac24..45e27a9` + tag `v2.8.0`; **Release `v2.8.0`** em 2026-11-10T12:44:30Z (hash conferido). Curadoria `c2560fc` guardada para a próxima publicação (D1).
- 2026-11-10 — Sessão F21 + F19 (worktree `sdd-open-f21-f19`). **F21:** o Roberto escolheu o porte fiel da skill 1.0.0 mais a camada do Open, exemplo neutro, 3 cenários de comportamento executados 3 vezes cada, starter logo depois da release; 2º revisor dispensado; o teto do job macOS do CI subiu de 45 para 60 min junto da release (commit `9581740`, fora da revisão, decisão dele depois de um cancelamento em 45m03s com os testes verdes). **Release `v2.9.0`** em 2026-11-10T19:03:18Z (hash conferido). **Starter:** com OK próprio, PR #9 do `sdd-starter` e Release `v1.5.16`; desvio do combinado "igual arquivo a arquivo": 13 de 14 arquivos iguais, o `SKILL.md` difere em 1 linha (a de identificação aponta para as Releases de cada repositório, exigência do `check-versions.py` de cada um).
- 2026-11-10 — **F19:** decisões do Roberto: dano = aplicada + teste que falha no código antigo + efeito; um arquivo de ledger por frente; o medidor só informa; duas colunas (pago e nominal); retroativo de F13 a F15 e F21 com dano `?`; o privado fica para depois da F15; governança dispensada com 2 cuidados. Um fato errado meu no brainstorm (disse que não havia ledger estruturado; havia, de 5 colunas, de F10 a F14), corrigido nos 3 documentos. O auditor pago ficou sem saldo na rodada 2: o Roberto autorizou **uma engine só** (a mesma revisa e audita). **Teto passado por decisão dele:** 5 rodadas de revisão (teto 3) e 3 ciclos do avaliador (teto 2); o avaliador **não deu PASS** (último veredito NEEDS_WORK; os consertos entraram em `dcf95ac` e não foram reavaliados). A tag `v2.10.0` foi enviada e **ficou sem Release**: o job de testes do Ubuntu do `release.yml` estourou o teto de 25 min (suíte em ~26 min), sem teste vermelho; o Roberto escolheu subir o teto para 45 (commit `36d0454`, PR #24, fora da revisão) e publicar como **`v2.10.1`**, sem mover a tag. **Release `v2.10.1`** em 2026-11-10T22:25:29Z (hash conferido), veredito CONCERNS.
---
- 2026-11-10 — F16, passo 0 (Roberto): curadoria das F21/F19 decidida por candidato — aceitos LM-011, LM-012, LM-013; o do lint que escolhe a tabela refina a LM-005 (que vira a INV-002, estado ok); descartado o do `git add -A` (o `.gitignore` do pacote resolve).
- 2026-11-10 — F16, brainstorm (Roberto): o Windows entra inteiro na F16; push livre só na branch `feat/f16-ambiente` com PR em rascunho, para medir; `gh auth status` com remoto do GitHub e sem remoto; modo terminal fora da tabela de vendor; abordagem "medir primeiro".
- 2026-11-10 — F16, revisão (Roberto): rodada 1 do DESIGN com uma engine só (saldo US$ 0,07); a OpenRouter foi recarregada (US$ 20) e as seguintes tiveram claude + qwen.
- 2026-11-11 — F16, Windows (Roberto, regra de parada do brainstorm): a 1ª medição rodou 282 de ~1.900 testes em 90 min (156 quebras); o job passa a rodar só o caminho do aluno e o porte da suíte inteira vira a frente própria **F16W**. Piso decidido com os números finais: continua "sem teste automático".
- 2026-11-11 — F16, release (Roberto): rodadas 4 e 5 de revisão, de fecho, acima do teto (a 4ª depois de ele dispensar e voltar atrás); teto do job macOS de 60 para 75 min antes da tag.
- 2026-11-11 — F16, pedido do Roberto antes da release: a `sdd-new-session` pergunta o editor padrão na 1ª vez (ele usa o Cursor; as provas abriam o VS Code), e a escolha fica em `git config --local sdd.editor`, não no slot da frente.
- 2026-11-11 — **F16 publicada: Release `v2.11.0`** (`main` = `69b7f6b`), com "sdd-open autorizado".
- 2026-11-11 — Roberto: a próxima frente é a **F18 (onda 1) + F20**, com brainstorm conjunto, antes da F17 (o aluno do starter recebe alerta e prevenção já na 1ª geração). Aberta com a `sdd-new-session` 1.5.0: worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f18-f20-seguranca`, branch `feat/f18-f20-seguranca` de `69b7f6b`; editor padrão deste computador gravado em `git config sdd.editor` = `cursor` (escolha do Roberto). O **cronograma recomendado** passou a morar no plano, logo abaixo da tabela "Estado das frentes".

## 2026-11-11 — F16 Ambiente agnóstico e proativo (Release v2.11.0)

### O que foi feito

- **Passo 0 (sobras da F21 e da F19):** curadoria do playbook com uma decisão do Roberto por candidato (`e632432`: LM-011 cenário nunca executado, LM-012 SHA-256 inteiro barrado, LM-013 edição por corte; LM-005 refinada; INV-002 nova, vigiada pelo `ledger-revisao-lint.sh` depois do conserto `58d1bd2`); coluna `Cobrança` na documentação do medidor; papel `indisponível` sem exit em "fora da conta"; `.gitignore` do pacote (`f6241f4`).
- **F16, fluxo completo** (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f16-ambiente`, branch `feat/f16-ambiente`): `BRAINSTORM`, `DEFINE` (v1.6, 9 ATs), `DESIGN` (v1.6, 8 decisões), `BUILD_REPORT` de `F16_AMBIENTE`. Produto em 18 commits `36d0454..69b7f6b`:
  - `sdd-checar-ambiente` 1.5.0: `gh` ausente, deslogado ou sem resposta vira ⚠️ (nunca 🔴) com o comando do sistema; `gh auth status` em paralelo com o `ls-remote` (grupo de processos, teto 10 s), só no modo normal e com origin do GitHub ou sem origin; editor em 2 camadas; modos novos `--editor` e `--editores`.
  - `sdd-iniciar-repo` 1.2.0: Passo 0 avisa do `gh` e do login ("instalar agora / depois", `[auto · de rotina]`); `inventario.sh` imprime `gh: ausente|deslogado|ok|sem resposta` (cópia idêntica das funções, teste compara).
  - `sdd-new-session` 1.5.0: **pergunta o editor padrão uma vez** (pedido do Roberto: lista do `--editores`, `terminal:claude`, `terminal:codex`, dizer o comando) e grava em `git config --local sdd.editor`; slot `editor` cheio manda; modo terminal; aviso final em 2 formas.
  - Tabela de instalação (macOS/Windows/Linux × git/gh) igual nas 3 skills.
  - `sdd/bin/lib/python.sh`: o Python que roda vira `python3` (no Windows, `python` ou `py -3`; o atalho da Store é pulado), por um calço no PATH; as 21 guardas `command -v python3` viram `sdd_python_pronto`; `PYTHONIOENCODING=utf-8`.
  - Job `testes-windows` (Git Bash + Python nativo) nos 2 workflows, informativo, só com o caminho do aluno; README e quickstart: Windows "sem teste automático"; `.gitattributes` `eol=lf`; pulos de plataforma por constante de `tests/apoio.py`; teto do macOS 60 → 75.
- **Release:** PR https://github.com/robertodiasduarte/sdd-open/pull/25 (mesclado 2026-11-11T13:29:35Z); `git push --atomic` de `36d0454..69b7f6b` na `main` + tag `v2.11.0`; run `release` 43029601153 (main) success; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.11.0 em 2026-11-11T14:02:43Z; SHA-256 de `sdd-open-v2.11.0.tar.gz` `7c51606a24e805387d399c8a09d0624bfc4fad88a51098ea49c8253fc5c5d536`, `shasum -a 256 -c` OK (`evidence/F16_AMBIENTE/RELEASE-sha256.log`).

### Casos e testes em aberto

- **Verify Gate** em `69b7f6b`: exit 0, 1.941 testes (partida: 1.867). CI do PR verde nos 3 sistemas (macOS 43m57s, teto 75).
- **Windows:** caminho do aluno verde (144 testes, 136 ok, 8 pulados com motivo); a suíte inteira não foi provada (1ª medição: 282 de ~1.900 em 90 min, ~19 s por teste).
- **Revisão:** 5 rodadas no ledger `sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md` (22 linhas, 1 com dano: o laço do calço). A 1ª com uma engine só; a 4ª e a 5ª de fecho, acima do teto, por decisão do Roberto. O conserto de texto da 5ª (`69b7f6b`) ficou sem revisor externo, com dispensa no ledger da release. `eval-revisores.sh`: tabela no BUILD_REPORT (2ª frente com dano marcado).
- **Avaliador de contexto novo:** NEEDS_WORK no ciclo 1 (6 achados, resolvidos), PASS_PENDENTE_RECIBO no ciclo 2 (9 ATs PASS; recibo = a Release).
- **Raio de impacto da release:** 1 quebra achada e consertada (`1bf3b1f`): o `python3` herdado era aceito sem conferir o PATH do filho.
- **Sabotagens:** 4 de 4 mortas (`SABOTAGEM.log`); avaliador: 5 de 5 no ciclo 2.
- **Ledger da release:** `evidence/F16_AMBIENTE/ledger-s1_2.11.0.yaml` (CONCERNS).

### Pendências

**🐛 Bug fix:**
- **Teto do `checar.sh` no Windows:** o vigia não mata o grupo de processos no Git Bash; com ssh, askpass ou rede pendurados, o `checar.sh` e o pré-voo `--frente` podem passar de 60 s (5 testes pulados por `SEM_SINAL`). Prioridade da F16W.
- **Rodada 4, R1:** com uma `sdd-checar-ambiente` anterior à 1.5.0 instalada ao lado da `sdd-new-session` nova, `checar.sh --editores` cai no modo normal e sai 0: a lista viria errada (a skill deve conferir a versão ou o formato).

**✨ Feature improvement:**
- **Curadoria do playbook não feita:** 5 candidatos no `BUILD_REPORT_F16_AMBIENTE.md` (`text=True` sem encoding no Windows; Python do Windows num pipe escreve cp1252; vigia por grupo de processos não vale no Windows; fallback silencioso esconde o caminho errado; id de run com 11 dígitos, `mordeu_antes: LM-012`). Contagens a colher: LM-001/002/003/005/006/008/009/010/011/013 ajudou, LM-012 mordeu.
- **F16W:** porte da suíte inteira ao Windows, medindo módulo a módulo; 4 dos 5 achados guardados (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`) só são medidos lá; skills com `python3` no texto (o aluno no Windows digita o atalho).
- **Pequenos:** o aviso do Python repete no `doctor` (rodada 4, R4); o loop de deriva do `doctor` não compara `sdd/bin/lib/python.sh`; `governanca-fronteira.sh` exige Python antes do `--help`; `docs-extract-decisions.sh` sai 64 com `RESULTADO: PAROU`; o guia do aluno não cita a linha `gh:`; o resumo do `checar` mostra o editor detectado, não o do `git config`.
- **Modo terminal numa sessão real de agente:** não executado (LM-011); roteiro no ciclo 1 do avaliador.
- **Starter:** recebe a F16 pela F17 (sem remendo lá).

### Próximos passos

1. ✅ `v2.11.0` publicada.
2. Próxima frente pelo plano: **F17 Starter gerado a partir do Open** (depende da F16, agora pronta), ou a **F16W** (porte ao Windows) — confirmar com o Roberto; o passo 0 leva a curadoria dos 5 candidatos e os 2 🐛 (o R1 é pequeno; o teto do Windows é F16W).
3. No privado: `sdd-open.sh sync` para a `v2.11.0` quando quiser as skills novas (e o `init` de novo completa `sdd/bin/lib/python.sh`).

### Alertas — o que não quebrar

- **`sdd/bin/lib/python.sh` é lido por 14 scripts e pelo `sdd-open.sh`:** a leitura usa só builtins e tem saída graciosa (sem o arquivo, a guarda antiga); `SDD_PYTHON_RESOLVIDO` herdado só vale com `python3` no PATH do filho.
- **`gh_estado` e `sistema`/`instalar_gh` existem iguais em `checar.sh` e `inventario.sh`** (entre `# ── gh e instalação por sistema (F16)` e `# ── fim do gh`, no começo da linha): mudou num, mude no outro; `tests/test_f16_textos.py` compara.
- **O bloco `<!-- INSTALAR-INICIO -->…<!-- INSTALAR-FIM -->` é igual nas 3 skills de entrada.**
- **Pulo de plataforma só por constante de `tests/apoio.py`** (`SEM_*`, `SOU_ROOT`, `MACOS`): a varredura por tokens reprova `os.name`/`sys.platform`/`os.geteuid()` em outro arquivo.
- **Contagens fixadas em testes antigos:** versões das skills (`test_matriz_new_session`, `test_f14_textos`), perguntas do `sdd-decisoes-lint` (29 em 24 arquivos, `test_decisoes_lint`). Skill ou pergunta nova mexe nelas.
- **Número com 11 dígitos em arquivo do pacote é barrado pelo publish-gate** (id de run do CI incluso): cite o commit.
- **Tetos do CI:** Ubuntu ~26 min (teto 45), macOS 39 a 47 min (teto 75), Windows caminho do aluno ~4 min (teto 30). Olhe antes da tag.
- **O `sdd-open` é público**, inclusive a branch `docs/`.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `69b7f6b` = tag `v2.11.0`; branch remota `feat/f16-ambiente` (PR #25 MERGED).
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f16-ambiente` (branch `feat/f16-ambiente`): as revisões `sdd/reports/reviews/EXTERNAL_REVIEW_2026111*` ficam só nela.
- Documentos da frente nesta branch (`docs/incorporar-starter`): `sdd/features/{BRAINSTORM,DEFINE,DESIGN}_F16_AMBIENTE.md`, `sdd/reports/BUILD_REPORT_F16_AMBIENTE.md`, `sdd/reports/evidence/F16_AMBIENTE/` (logs do Windows em `windows/`), `sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md` e as 2 avaliações.

### Prompt de retomada

O mesmo de `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`:

```text
Executar a próxima frente do SDD Open: a F17 (Starter gerado a partir do Open) pelo plano, ou a F16W (porte da suíte ao
Windows) — pergunte ao Roberto qual antes de começar. Repo público robertodiasduarte/sdd-open, worktree nova de origin/main
69b7f6b (v2.11.0). Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do repositório privado) entra aqui.
O starter (robertodiasduarte/sdd-starter) pede OK próprio do Roberto: push em skills/** na main de lá publica Release sozinho.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes" (fonte única),
  a seção da frente escolhida (F17 ou F16W) e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de
  2026-11-10 e 2026-11-11 e a seção "2026-11-11 — F16 Ambiente agnóstico e proativo" (Pendências e Alertas)
- git show origin/docs/incorporar-starter:sdd/reports/BUILD_REPORT_F16_AMBIENTE.md → Windows (as 5 medições) e Candidatos
- o ## Sempre de sdd/playbook.md da worktree

0. Sobras da F16, na branch da frente nova (sobem com a release dela):
   a. Curadoria do playbook: 5 candidatos em sdd/reports/BUILD_REPORT_F16_AMBIENTE.md (blocos <<<CANDIDATO_PLAYBOOK, na
      branch de documentos), uma decisão do Roberto por candidato; colher as contagens com
      bash sdd/bin/playbook-curator.sh --colher <pasta com DESIGN, BUILD_REPORT e AVALIACAO da F16> sdd/playbook.md
      (LM-012 mordeu; lição que passa a ter mordeu ≥ 1 precisa de classificação em sdd/invariants.md: pergunte).
      Depois: bash sdd/bin/playbook-lint.sh sdd/playbook.md e o --validar-inv (exit 0), e rode tests/test_sdd_open.py (o init
      instala as invariantes: um check= que só existe no pacote reprova).
   b. Rodada 4, R1: com uma sdd-checar-ambiente anterior à 1.5.0 instalada, `checar.sh --editores` cai no modo normal e sai 0;
      a sdd-new-session deve conferir a versão da checar-ambiente (ou o formato "<nome><TAB><comando>") antes de usar a lista.
   c. Pequenos (decida com o Roberto se entram): aviso do Python repetido no doctor; o loop de deriva do doctor sem
      sdd/bin/lib/python.sh; governanca-fronteira.sh exige Python antes do --help; o resumo do checar mostra o editor
      detectado, não o do git config sdd.editor; o guia do aluno sem a linha gh: do inventário.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.11.0.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - F17: o starter é gerado a partir do Open; a 1ª geração exige comparar skill a skill antes (plano, seção da F17). As skills
     de entrada da v2.11.0 chegam ao starter por ela.
   - F16W: o 1º passo é medir módulo a módulo no windows-latest (Git Bash + Python nativo), com teto por módulo; prioridade:
     o teto do checar.sh no Windows (o vigia por grupo de processos não corta a rede pendurada; 5 testes pulados por SEM_SINAL).
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md e confere com bash sdd/bin/ledger-revisao-lint.sh; no fim,
     rode bash sdd/bin/eval-revisores.sh e guarde a tabela no relatório.

Revisão adversarial: saldo da OpenRouter em ~US$ 19,9 em 2026-11-11 (leia em /credits antes de cada rodada paga;
limit_remaining é o limite da chave, não o saldo). Cadeia que funcionou na F16: claude revisa, `openrouter` (qwen) audita,
--no-revisor2 (codex sem cota, gemini sem credencial; 2º revisor pago evitado pela LM-010) — registre a dispensa do 2º revisor
no --conferir. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY=
no ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir.
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto (na F16 foram 5 rodadas,
cada extra perguntada). Na release, rode o raio de impacto (0b) antes da última rodada: na F16 ele achou uma quebra.

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~26 min, teto 45; macOS 39 a 47 min, teto 75; Windows caminho
do aluno ~4 min, teto 30). Se a suíte crescer, olhe o teto ANTES da tag: tag com job cancelado fica sem Release e não se move.
Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Número com 11 dígitos em arquivo do pacote
(id de run do CI incluso) é barrado pelo publish-gate: cite o commit.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree de documentos da branch
docs/incorporar-starter), a linha da frente na tabela "Estado das frentes" do plano, os documentos da frente e este
SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.

Não faça:
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- nada no sdd-starter sem OK próprio do Roberto;
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Pulo de plataforma nos testes só por
constante de tests/apoio.py. gh_estado/instalar_gh existem iguais em checar.sh e inventario.sh; o bloco INSTALAR é igual nas 3
skills de entrada: mudou num, mude nos outros.
```

---

## 2026-11-10 — F21 Engenharia reversa (Release v2.9.0, starter v1.5.16) + F19 Custo dos revisores (Release v2.10.1)

### O que foi feito

- **F21, fluxo completo** (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19`): `BRAINSTORM`, `DEFINE` (v1.2, 10 ATs), `DESIGN` (v1.1) e `BUILD_REPORT` de `F21_ENGENHARIA_REVERSA`. Produto em 4 commits `45e27a9..9581740`: `6df152d` (curadoria da F15_SLOTS, cherry-pick de `c2560fc`), `99b1323` (`sdd-release` 2.9.1, "itens 1 a 6b"), `6a54790` (a frente: skill `sdd-engenharia-reversa-saas` 1.1.0 como 20ª skill, 13 arquivos, molde e lint do levantamento byte a byte com a 1.0.0; `tests/test_validate_reverse.py` e `tests/test_f21_textos.py`; linha `ER` no `AGENTS.md.tmpl`; README nos 2 idiomas; guia do aluno), `9581740` (teto do job macOS de 45 para 60 min).
- **F21, release:** PR https://github.com/robertodiasduarte/sdd-open/pull/22; push `45e27a9..9581740` + tag `v2.9.0`; runs `release` 42876588824 (main) e 42876587459 (tag) success; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.9.0 em 2026-11-10T19:03:18Z; SHA-256 de `sdd-open-v2.9.0.tar.gz` `72ad1bac37c8a59a17419e8f469fac322a96c6f7eaa7d8476721795b39afdfca`, `shasum -a 256 -c` OK (`evidence/F21_ENGENHARIA_REVERSA/RELEASE-sha256.log`).
- **F21, starter (OK próprio do Roberto):** PR https://github.com/robertodiasduarte/sdd-starter/pull/9 (merge `a82c972`), Release automática `v1.5.16` em 2026-11-10T19:38:17Z; `releases/latest/download/sdd-engenharia-reversa-saas.zip` responde 200 e confere com o `SHA256SUMS.txt`; comparação arquivo a arquivo com a tag `v2.9.0` em `evidence/F21_ENGENHARIA_REVERSA/STARTER-sha256.log` (13 iguais; `SKILL.md` com 1 linha diferente, a de identificação). Entrou também a linha da skill na tabela do README do starter (PT e EN).
- **F19, fluxo completo** (mesma worktree, branch `feat/f19-custo-revisores` de `9581740`): `BRAINSTORM`, `DEFINE` (v1.4, 9 ATs), `DESIGN` (v1.3), `BUILD_REPORT` de `F19_CUSTO_REVISORES`. Produto em 6 commits `9581740..dcf95ac`, 41 arquivos novos e 14 alterados: `sdd/bin/eval-revisores.sh` (exits 0 MEDIDO · 2 SEM DADOS · 64), `sdd/bin/ledger-revisao-lint.sh` (0 · 2 · 64), `sdd/review/CRITERIO_DANO.md`, `sdd/templates/LEDGER_REVISAO_TEMPLATE.md`, fixtures em `sdd/fixtures/revisao/`, 3 arquivos de teste, `sdd-build` 2.8.0 (passo 5c grava e confere o ledger), `sdd-release` 2.10.0 (0a item 8 confere o lint), documentação nos 2 idiomas, contratos.
- **F19, retroativo:** `sdd/reports/RETROATIVO_REVISORES_2026-11-10.md` (25 pastas de revisão, 6 ledgers) e os ledgers convertidos `sdd/reviews/LEDGER_REVISAO_{F13_UX_LLM,F14_PLAYBOOK,F14_DRIVE,F15_SLOTS,F21_ENGENHARIA_REVERSA}.md` (dano `?`, `retroativo: sim`); o da própria F19 é o primeiro gravado no formato novo (15 linhas, 3 com dano).
- **F19, release:** PR https://github.com/robertodiasduarte/sdd-open/pull/23 (CI: Ubuntu 26m15s, macOS 31m25s, verdes); push `9581740..dcf95ac` + tag `v2.10.0`, que **ficou sem Release** (runs `release` 42892986649 e 42892986454: job do Ubuntu cancelado pelo teto de 25 min aos 25m15s, sem teste vermelho; macOS verde). Conserto: PR https://github.com/robertodiasduarte/sdd-open/pull/24, commit `36d0454` (teto de 25 para 45 min e um teste que fixa o número), push `dcf95ac..36d0454` + tag `v2.10.1`; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.10.1 em 2026-11-10T22:25:29Z; SHA-256 de `sdd-open-v2.10.1.tar.gz` `e306c03425534fecc38cd2788554066fcb8e49122434bf49315de8486a41c78c`, `shasum -a 256 -c` OK (`evidence/F19_CUSTO_REVISORES/RELEASE-sha256.log`).

### Casos e testes em aberto

- **Verify Gate F21** em `6a54790`: exit 0, 1.765 testes. **Verify Gate F19** (`bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F19_CUSTO_REVISORES.md`) em `dcf95ac`: exit 0, 1.864 testes, 1 pulado (`evidence/F19_CUSTO_REVISORES/VERIFY-GATE.log`).
- **Sabotagens:** F21 4 de 4 mortas; F19 6 de 6 mortas (`SABOTAGEM.log` de cada pasta de evidência); linhas de base vermelhas em `BASELINE-vermelho.log`.
- **Avaliador de contexto novo:** F21 PASS no ciclo 2. **F19 sem PASS:** 3 ciclos (A1 a A6, B1 a B7, C1 a C5), o último NEEDS_WORK sobre `0d4a730`; os consertos (cerca como no CommonMark, regra das 4 barras dita na mensagem, na ajuda e no molde, limites declarados) entraram em `dcf95ac` e **não foram reavaliados**.
- **Revisão:** F21 em 4 rodadas com duas engines (`review_externo` no `ledger-s1_2.9.0.yaml`). F19 em 5 rodadas: 1 e 2 com revisor por assinatura e auditor pago (que falhou na 2 por saldo); 3, 4 e 5 com **uma engine só**; a 5 confere com `dcf95ac` (`EXTERNAL_REVIEW_20261110-162917`, sha256 `d333619ffd4e…`, `diversidade=nenhuma`). As pastas `sdd/reports/reviews/EXTERNAL_REVIEW_20261110-*` ficam só na worktree.
- **Ledgers de release:** `evidence/F21_ENGENHARIA_REVERSA/ledger-s1_2.9.0.yaml` (CONCERNS, estado `parcial` na hora da release; a etapa do starter fechou depois) e `evidence/F19_CUSTO_REVISORES/ledger-s1_2.10.1.yaml` (CONCERNS, 10 avisos).
- **Comportamento da F21:** 3 de 17 cenários executados (ER-08, ER-09 e 1 positivo), num agente só; 14 não executados, declarado no `manifest.json` da skill.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- **F19, rodada 5, R1 (leve):** a tabela de colunas da seção `eval-revisores` em `docs/adversarial-review.md` e `docs/pt-BR/adversarial-review.md` não lista a coluna `Cobrança`, que o script imprime.
- **F19, rodada 5, R2 (leve):** em `sdd/bin/eval-revisores.sh`, papel com engine `indisponível`, sem exit e sem custo no `META.txt`, é pulado sem aviso (o `continue` de exit ausente vem antes da checagem de `indisponível`). Não aparece nos dados reais: o `adversarial-review.sh` grava o exit.
- **F21:** `tests/test_f21_textos.py::test_o_teste_acusa_o_termo_proibido` é tautológico (achado leve da rodada 4, aceito e não aplicado; a prova negativa do AT-006 é a sabotagem M3).
- **Pacote sem `.gitignore`:** rodar a suíte sem `-B` grava `__pycache__` em `tests/` e `sdd/bin/`; `git add -A` já levou `.pyc` para um commit nesta sessão (barrado pelo gate, refeito).

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Curadoria do playbook não feita:** 3 candidatos no `BUILD_REPORT_F21_ENGENHARIA_REVERSA.md` (cenário escrito e nunca executado; `git add -A` com `.pyc`; SHA-256 inteiro barrado como número longo) e 2 no `BUILD_REPORT_F19_CUSTO_REVISORES.md` (lint que escolhe "a tabela que interessa" deixa linha sem conferir, mordeu a LM-005; edição por corte apaga testes sem erro). Cada um pede a decisão do Roberto e sobe com a próxima release, como a curadoria da F15_SLOTS subiu com a F21.
- **F19, limites declarados na ajuda:** o que vem depois de `-->` na mesma linha não é lido; o medidor conta `sim` sem conferir o teste (o lint confere a forma); arquivo de vereditos com linha cortada conta só as linhas inteiras.
- **F19, o que os números ainda não dizem:** as 6 frentes do retroativo têm dano `?`; só a F19 tem dano marcado (3 de 15). Custo por falha com dano só fica útil com mais frentes gravadas no formato novo.
- **Revisão com duas engines:** saldo da OpenRouter em US$ 0,0747 (a chamada do auditor não cabe); codex sem cota; gemini sem credencial. Sem recarga, a próxima frente repete a revisão de uma engine só.
- **Página `/sdd/` da F21:** frente própria no repositório privado; nada dela aqui.
- **Medir o privado com o `eval-revisores.sh`:** decisão do Roberto, depois da F15.

### Próximos passos

1. ✅ `v2.9.0` e `v2.10.1` publicadas (a tag `v2.10.0` existe, sem Release); skill da F21 no starter (`v1.5.16`).
2. Próxima frente do Open pelo plano: **F16 Ambiente agnóstico e proativo** (sessão própria), levando no passo 0 a curadoria dos 5 candidatos e os 2 achados leves da F19.
3. No privado: `sdd-open.sh sync` para a `v2.10.1` quando for usar o ledger da revisão e o medidor.

### Alertas — o que não quebrar

- **O arquivo `LEDGER_REVISAO_{F}.md` guarda só o ledger:** toda linha de tabela é conferida, inclusive dentro de comentário e de bloco cercado, porque o `sdd-fluxo.sh loop` as lê. Regra que tenta adivinhar "qual tabela é o ledger" regrediu 2 vezes nesta frente (LM-005).
- **`linhas_uteis` e `linha_solta`** existem iguais em `ledger-revisao-lint.sh` e `eval-revisores.sh`; um teste compara o texto: mudou num, mude no outro.
- **O id do achado no ledger é copiado do arquivo de vereditos** (`R1`, `N1`, `R1@engine`): o `loop` casa o id exato.
- **`git add` por caminho, suíte com `-B`** enquanto o pacote não tiver `.gitignore`. Sabotagem só em cópia de `git archive`.
- **Linha de identificação das skills difere entre Open e starter** (cada uma aponta para as Releases do seu repositório): cópia para o starter troca essa linha e mais nada.
- **Push em `skills/**` na `main` do starter publica Release sozinho** (`auto-release.yml`); o starter pede OK próprio.
- **Tetos do CI:** a suíte leva ~26 min no Ubuntu e 31 a 45 min no macOS; os tetos do `release.yml` são 45 e 60. Suíte maior pede olhar o teto antes da tag: tag enviada com job cancelado fica sem Release e não se move.
- **O `sdd-open` é público**, inclusive a branch `docs/`: nenhum caminho, projeto ou script do privado, nem nome de produto real de terceiro.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `36d0454` = tag `v2.10.1`; tag `v2.10.0` = `dcf95ac` (sem Release); tag `v2.9.0` = `9581740`; branches remotas `feat/f21-engenharia-reversa` (PR #22 MERGED) e `feat/f19-custo-revisores` (PR #23 MERGED).
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19` (branch `feat/f19-custo-revisores`); as revisões `sdd/reports/reviews/EXTERNAL_REVIEW_20261110-*` e os traces só nela.
- Starter: `https://github.com/robertodiasduarte/sdd-starter.git`, `main` = `a82c972`, Release `v1.5.16`. A cópia local `/Users/robertoduarte/rdd-public/sdd-starter` está atrás do remoto (não foi tocada; tem um arquivo não rastreado do Roberto).
- Documentos SDD das duas frentes nesta branch (`docs/incorporar-starter`): `sdd/features/*_F21_*` e `*_F19_*`, `sdd/reports/BUILD_REPORT_F21_*` e `_F19_*`, `sdd/reports/RETROATIVO_REVISORES_2026-11-10.md`, `sdd/reports/evidence/{F21_ENGENHARIA_REVERSA,F19_CUSTO_REVISORES}/`, `sdd/reviews/` (avaliações, revisões de DESIGN e 6 ledgers da revisão).

### Prompt de retomada

```text
Retomada da família INCORPORAR_STARTER no SDD Open (repositório público robertodiasduarte/sdd-open).
Leia primeiro, na branch docs/incorporar-starter (GIT_TERMINAL_PROMPT=0 git fetch -q origin; git show origin/docs/incorporar-starter:<arquivo>):
sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, seção "2026-11-10 — F21 Engenharia reversa … + F19 Custo dos revisores", e
sdd/features/PLANO_F4_F15_CONSOLIDADO.md, seção "Estado das frentes".
Onde paramos: v2.10.1 publicada em 2026-11-10 (main = 36d0454; a tag v2.10.0 ficou sem Release); antes dela a v2.9.0 (9581740) e a skill da F21 no starter (v1.5.16).
Verify Gate de sdd/features/DEFINE_F19_CUSTO_REVISORES.md saiu 0 em dcf95ac (1.864 testes).
Tarefas, na próxima frente do Open (pelo plano, a F16, em sessão própria; confirme com o Roberto):
1. Curadoria do playbook: 3 candidatos de sdd/reports/BUILD_REPORT_F21_ENGENHARIA_REVERSA.md e 2 de
   sdd/reports/BUILD_REPORT_F19_CUSTO_REVISORES.md, uma decisão do Roberto por candidato; sobe com a release da frente.
2. Dois consertos leves da F19: a coluna Cobrança na tabela de colunas de docs/adversarial-review.md e docs/pt-BR/adversarial-review.md;
   em sdd/bin/eval-revisores.sh, avisar em "fora da conta" o papel indisponível sem exit (com teste).
3. Criar o .gitignore do pacote (__pycache__, *.pyc, sdd/reports/reviews/, sdd/traces/) e conferir o MANIFEST e o publish-gate.
Alertas: push só com "sdd-open autorizado"; o starter pede OK próprio; nada do privado no repositório público; git add por caminho;
revisão com duas engines depende de saldo na OpenRouter (US$ 0,07 em 2026-11-10) ou de cota no codex.
Fluxo: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
```

---

## 2026-11-10 — F15 Slots: L0 + L3 + L4 do inventário de saída (entregue, Release v2.8.0)

### O que foi feito

- **Fluxo completo do Open** na worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f15-slots`, branch `feat/f15-slots` de `origin/main` = `9d8ac24` (`v2.7.2`): `BRAINSTORM_F15_SLOTS.md`, `DEFINE_F15_SLOTS.md` (v1.2, 11 ATs, governança N.A. por revisor fresco), `DESIGN_F15_SLOTS.md` (v1.5, 10 decisões, 21 arquivos), `BUILD_REPORT_F15_SLOTS.md`, evidência em `sdd/reports/evidence/F15_SLOTS/`, avaliações em `sdd/reviews/AVALIACAO_F15_SLOTS_*.md`.
- **Produto** (7 commits `9747f9b..45e27a9`, 21 arquivos): `sdd/bin/slot.sh` (novo; exits 0 OK · 2 REPROVOU · 3 INCONCLUSIVO · 10 NADA A MEDIR · 11 PULADO · 64 ERRO DE USO; `SDD_MOMENTO`, `SDD_FEATURE`, `SDD_BASE`, `SDD_COMMIT`, `SDD_ARVORE`, `SDD_SLOT_DIR`); slots `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd` e `schema.check_cmd` no `config.example.yaml` (**reabertos por decisão do Roberto**, registrado no §8.2 do plano); `sdd-release` 2.9.0 (0a item 9 = `test-baseline.sh --touched`; itens 6b, 7b e 10 = os 3 smokes; linha Verificações do OK); `sdd-build` 2.7.0 (`aplicar-migration.md` §2b, checagem antes da prévia, fail-closed); `test-baseline.sh --touched` conta o teste ao lado da fonte (TS/JS e Python; Go e jest fora, declarado).
- **Decisões do Roberto (2026-11-09/10):** nomes `smoke.*` + `schema.check_cmd`; exit 2 com peso por momento; smokes independentes com pasta comum; L3 aborta e L4 fail-closed; abordagem A (executor único); TS/JS e Python no teste ao lado; PULADO = 11; revisão do DESIGN por agente fresco; avaliador fresco mesmo com "1 camada"; revisão paga claude → codex (reserva qwen), 2º revisor pela OpenRouter, 4ª rodada como última, dispensa do 2º revisor da rodada 4; curadoria aceita (LM-009, LM-010) e guardada para a próxima publicação.
- **Release:** "finalizar (push + deploy + verificar) sdd-open"; PR https://github.com/robertodiasduarte/sdd-open/pull/21 (CI run 42808779792: Ubuntu 23m38s, macOS 27m40s, verdes); push `9d8ac24..45e27a9` em `main` + tag `v2.8.0`; run `release` 42812618626 (main) success, `publish-gate` 42812618548 success; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.8.0 publicada em 2026-11-10T12:44:30Z; SHA-256 de `sdd-open-v2.8.0.tar.gz` `b7e18019d24865ba7a46ca1453daf943bda8a8acd085795ddd25c3bea564c84c`, `shasum -a 256 -c` OK (`RELEASE-sha256.log`); `deploy-do-sha.sh` NO AR (`RELEASE-deploy-do-sha.log`).

### Casos e testes em aberto

- **Verify Gate** (`bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F15_SLOTS.md`) em `45e27a9`: exit 0, 1.717 testes, 1 pulado (`RELEASE-GATE-strict.log`).
- **Sabotagens:** 14 de 14 mortas (`SABOTAGENS.log`); linhas de base vermelhas por leva em `BASELINE-RED*.log`.
- **Avaliador fresco:** ciclo 1 NEEDS_WORK (flag seguida de flag; `#` no meio da palavra), ciclo 2 PASS.
- **Revisão paga, 4 rodadas** (`sdd/reports/reviews/EXTERNAL_REVIEW_20261110-*`, só nesta máquina): `review_externo: sdd/reports/reviews/EXTERNAL_REVIEW_20261110-070608 sha256=1fbc689e5bb84319e8206c0f277bbd521b7088f64ac1e11765cc80b71435c367 diversidade=vendor revisor2=dispensado — …`; N1 do auditor (`declare -f` preservaria comentário) rebatido por medição (`REVIEW-N1-declare-f.log`, `REVIEW-R4-medicoes.log`) e confirmado no bash do Ubuntu pelo CI.
- **Ledger:** `sdd/reports/evidence/F15_SLOTS/ledger-s1_2.8.0.yaml` (veredito CONCERNS, 4 avisos).
- **Run da tag** `42812618555` (mesma `v2.8.0`): estava em andamento no fechamento; a Release já existia pelo run da `main`.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- Nenhum defeito conhecido no produto da F15_SLOTS.
- **Gasto e cota:** codex sem cota nas 4 rodadas; gemini sem credencial; saldo da OpenRouter em US$ 0,74 (o deepseek cobrou ~US$ 1 sem responder; LM-010).

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Curadoria não enviada:** commit `c2560fc` (`chore(playbook): curadoria F15_SLOTS — 8 delta(s)`: LM-001 a LM-006 `ajudou+1`, LM-009 e LM-010 novos) na branch local `feat/f15-slots`, decisão D1 do Roberto: sobe com a próxima release do Open. Envio: `cd /Users/robertoduarte/rdd-worktrees/sdd-open-f15-slots && GIT_TERMINAL_PROMPT=0 git push origin feat/f15-slots` e levar o commit pela `sdd-release` da próxima frente (push na `main` que toca `sdd/playbook.md` publica sozinho).
- **Texto:** a tabela de etapas da `sdd-release` diz "FASE 1, itens 1 a 6" sem o 6b (raio de impacto); o recorte "release 0a item 8" de `tests/test_contrato_build_release.py:226` passou a incluir o item 9.
- **Limites declarados:** unittest conta módulo de mesmo nome em outro pacote; id relativo à subpasta conta homônimo em outra pasta (erram para o lado seguro); teste ao lado em Go fica fora.
- **No privado (fora do Open):** ligar os 4 slots aos scripts de lá e tratar o exit 2 do `contraste.sh`.

### Próximos passos

1. ✅ `v2.8.0` publicada (2026-11-10T12:44:30Z).
2. **No privado, antes da fase 3 da F15:** `bash bin/sdd-open.sh sync` para a `v2.8.0`; o `doctor` aponta `sdd/bin/*` e skills mais velhos que o pacote (apagar e rodar `init` para receber `test-baseline.sh`, `sdd-release` 2.9.0, `sdd-build` 2.7.0; o `slot.sh` novo o `init` completa sozinho); preencher os 4 slots no `sdd/config.yaml` de lá.
3. **F15 fases 2 a 4** (`BRAINSTORM_F15_SUBSTITUICAO.md`); depois F16 a F20 (plano, seção 8).

### Alertas — o que não quebrar

- **O bloco do OK** continua com os 8 rótulos e uma pergunta só; os resultados novos vão dentro da linha Verificações.
- **`slot.sh`:** o `bash -n` vem antes da checagem de comentário (que define uma função com o comando); tirar o `bash -n` deixa um comando escapar da função (`test_comando_nao_escapa_da_checagem`).
- **Sabotagem com `git checkout` só com árvore commitada** (LM-009).
- **O `sdd-open` é público**, inclusive a branch `docs/`: nenhum caminho, projeto ou script do privado.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `45e27a9` = tag `v2.8.0`; branch remota `feat/f15-slots` (PR #21 MERGED) em `45e27a9`.
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f15-slots` (branch `feat/f15-slots`, local à frente do remoto pelo `c2560fc`); revisões em `sdd/reports/reviews/EXTERNAL_REVIEW_20261110-*` só nela.
- Documentos SDD desta frente na branch `docs/f15-slots` (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f15-slots`), nascida de `origin/docs/incorporar-starter` = `297f070`; a `docs/incorporar-starter` não foi tocada (está em uso na `sdd-open-docs-f16`).

### Prompt de retomada

```text
Retomada da família INCORPORAR_STARTER no SDD Open (repositório público robertodiasduarte/sdd-open).
Leia primeiro sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, seção "2026-11-10 — F15 Slots", na branch docs/f15-slots
(GIT_TERMINAL_PROMPT=0 git fetch origin && git show origin/docs/f15-slots:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md).
Onde paramos: v2.8.0 publicada em 2026-11-10 (main = 45e27a9) com os slots smoke.* e schema.check_cmd, o sdd/bin/slot.sh
e os testes do diff na sdd-release; Verify Gate de sdd/features/DEFINE_F15_SLOTS.md saiu 0 em 45e27a9 (1.717 testes).
Tarefas:
1. Na próxima frente do Open, levar o commit c2560fc (curadoria F15_SLOTS, branch feat/f15-slots da worktree
   /Users/robertoduarte/rdd-worktrees/sdd-open-f15-slots) junto com a release dela (push na main que toca sdd/playbook.md publica).
2. Trocar "FASE 1, itens 1 a 6" por "itens 1 a 6b" na tabela de etapas da .agents/skills/sdd-release/SKILL.md (bump patch).
3. No privado, a F15 segue: sdd-open.sh sync para v2.8.0, ligar os 4 slots, fases 2 e 3 (BRAINSTORM_F15_SUBSTITUICAO.md).
Alertas: o bloco do OK não muda de rótulos; push só com "sdd-open autorizado"; nada do privado no repositório público.
Fluxo: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
```

---

## 2026-11-07 — Sessão 13: correções da v2.7.0 (entregue, Release v2.7.1) e brainstorm da F15

### O que foi feito

- **Worktree** `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, branch `feat/f14-drive`, recriada pelo script; a F18 (plano v1.5 e handoff) trazida da worktree `sdd-open-docs-f16`, base igual.
- **Commits** sobre `origin/main` = `b0663d3` (`v2.7.0`): `b3526ae` (curadoria da F14 Drive, já existia), `5a1e3fc` (rodada 5 e teste do slice), `3d69536` (rodada 6). Remota `feat/f14-drive-v271` → PR https://github.com/robertodiasduarte/sdd-open/pull/19.
- **Rodada 5:**
  - R1@codex HIGH: a trava de estado do `sdd/bin/sdd-drive.sh` é `flock` (`msvcrt` no Windows); some com o dono, nunca enquanto ele vive; o arquivo é apagado ainda sob a trava, com `samestat`;
  - R3@claude: nada apaga trava de outro processo; trava que não abre sai 2 com "apague";
  - R1@claude: item 10 da `sdd-release` (2.8.1) com teto de 8 chamadas e sem repetir "não achei nenhum run";
  - R2@claude: o 401 no disparo apaga a marca (`SemLogin`) antes de sair 3;
  - R4@claude: solto recente em "Recentes";
  - teste do slice: `test_ficha_de_slice_protege_sem_documento_com_o_nome_do_slice`; a mensagem cita a ficha real (`HANDOFF_G_s2.md`), defeito achado pelo teste.
- **Rodada 6:** `O_NOFOLLOW` na trava; teste que amarra a frase do item 10 ao `fim(4` do `deploy-do-sha.sh`; o teste do link pula no Windows.
- **Revisão real:** rodada 6 (US$ 0,86) e 7 (US$ 0,95), Claude + Codex + qwen; rodada 7 em `3d69536`: `loop` PRONTO, `--conferir` CONFERE, `review_externo: sdd/reports/reviews/EXTERNAL_REVIEW_20261107-133717 sha256=9a3ee072107b2542f581e95f6dafbd34c0874200ff397a367a78c400c69534d9 diversidade=vendor`. Ledger: `sdd/reports/evidence/F14_DRIVE/ledger-review.md` (linhas `rodada=6` e `rodada=7`).
- **Brainstorm da F15:** `sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md` (Handoff Ready; 13 decisões, 5 cortes YAGNI, 2 checkpoints).
- **Plano v1.6:** F19 (custo e benefício dos revisores) e F20 (ações preventivas do e-book), a pedido do Roberto; e-book em `/Users/robertoduarte/Downloads/ebook-seguranca-construir-com-ia/` (`INDICE.md`, `fonte.md`).

### Casos e testes em aberto

- **Testes novos**, cada um cai no código anterior: `test_trava_de_dono_vivo_nao_vence_pela_idade`, `test_trava_que_nao_abre_sai_2_sem_laco`, `test_trava_que_e_link_nao_cria_arquivo_fora` (`tests/test_drive.py`); `test_dispatch_sem_login_sai_3_e_nao_gasta_o_redisparo` (`test_deploy_do_sha.py`); `test_solto_recente_fica_e_nao_e_decisao_sua`, `test_ficha_de_slice_protege_sem_documento_com_o_nome_do_slice` (`test_sdd_archive.py`); `test_a_frase_que_para_a_repeticao_e_a_do_script` e as 2 asserções do item 10 (`test_f14_drive_textos.py`).
- **Verify Gate em `3d69536`:** 1ª vez vermelho por 1 teste de tempo sob carga, 1.663 testes (`sdd/reports/evidence/F14_DRIVE/verify-gate-3d69536-sob-carga.log`); 2ª vez, sem carga: **verde**, 1.663 testes, 1 pulado, 1.340 s, `[exit=0]` (`verify-gate-3d69536.log`).
- **CI do PR #19** (run 42398580503): Ubuntu ✅ 18m21s; macOS ✅ 38m35s (teto 45).
- **Sabotagens dos consertos novos** (`sabotagens-5a1e3fc.sh`, log `sabotagens-3d69536.log`): 10; 9 derrubam teste. Viva: "trava em arquivo que saiu do caminho vale" (o `samestat` só importa numa corrida de milissegundos entre abrir e travar, que teste de fora não força).
- **Release:** "sdd-open autorizado"; push `b0663d3..3d69536`; runs `release` 42437407177 e `publish-gate` 42437407206 verdes; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.7.1, publicada em 2026-11-08T02:46:40Z; SHA-256 de `sdd-open-v2.7.1.tar.gz` `5aa600aea17a9481d4ac215af574e9c2563adeaf6d6f58e99c6a7c58569930e3`, `shasum -a 256 -c` OK (`release-v2.7.1-sha256.log`); `deploy-do-sha.sh`: `✅ no ar — run 42437407177` (`deploy-do-sha-v2.7.1.log`). Veredito 🟡 CONCERNS com 4 avisos (abaixo). Curadoria: 1 proposto / 0 aplicados / 0 promoções (`CURATOR-colheita-v2.7.1.log`).
- **Gate offline da revisão:** 103 asserções verdes em `5a1e3fc` e `3d69536` (`adversarial-gate-*.log`).
- **Medições da rodada 7:** `r7-repro.sh` e `r7-repro-claude.log`.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- **R1@codex da rodada 7** (MED, risco aceito pelo Roberto, D4 de 2026-11-07): no Windows nativo, sem `O_NOFOLLOW`, um link no lugar de `DRIVE_<F>.estado.lock` faz o drive criar arquivo vazio fora do repositório. Conserto proposto: recusar link (`os.path.islink`) antes de abrir, no Windows.
- **Teste de tempo frágil:** `test_duas_chamadas_juntas_repetem_uma_vez` (`tests/test_deploy_do_sha.py`) usa `--teto 1` e falha sob carga. Mexer nele invalida a revisão da rodada 7: fica para a próxima frente que tocar o `deploy-do-sha`.
- **Herdadas da etapa F14 Drive:** do ciclo 3 do avaliador (L1, L2, L3, L6, L7, L8, L13, L14, M5 em parte); `sdd-fluxo.sh` sem `-I`; `AVAL-26` e `AVAL2-21`; fronteira F5, F6, F7, guarda da F9 e curadoria (L7, N-L9, N-L10, N-L11, N3-L4).
- **`handoff-lint` vermelho neste arquivo** (já no remoto antes da sessão 13): a família usa o formato antigo, com o prompt em `SESSION_PROMPT_INCORPORAR_STARTER.md`; o lint pede `Verify Gate` na ficha, prompt no corpo e histórico de slices.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Aviso do bloco do OK:** `gate-shell-evidencia` acusa `AVAL-26` e `AVAL2-21` (sondas antigas, declaradas no BUILD_REPORT, iguais na `v2.7.0`); sabotagem viva do `samestat`.
- **Branch remota `feat/f14-drive-v271`** (PR #19 MERGED) pode ser apagada: decisão do Roberto.
- **F15** fases 1 a 4 (brainstorm feito); **F16**, **F17**, **F18**, **F19**, **F20** (plano v1.6); **F21** (plano v1.8).
- **Tempo de CI:** Ubuntu 18m21s de 25 no PR #19; macOS 35m38s de 45 na F14. Sobra pouca margem.
- **Windows sem teste:** o `README.md:89` promete Windows (Git Bash/WSL), mas o CI nunca rodou lá; entra na F16 (`ESCOPO_F16_AMBIENTE.md` §3.5).

### Próximos passos

1. ✅ `v2.7.1` publicada (2026-11-08T02:46:40Z).
2. **Sessão 14: F15 fase 1 (instalar)**, numa worktree do privado aberta pelo `/new-session` de lá (`~/rdd-worktrees/f15-substituicao`, branch `feat/f15-substituicao`), com o OK do Roberto. Pronto quando: `bash bin/sdd-open.sh doctor` ✅ sem ⚠️ no privado, ganchos numa pasta só, `sdd-public/` fora do git.
3. **F15 fases 2 a 4** (`BRAINSTORM_F15_SUBSTITUICAO.md`, Success Criteria).
4. **F16 a F21** (plano, seção 8).

### Alertas — o que não quebrar

- **Trava de estado do drive:** nunca voltar à regra por idade; nada apaga a trava de outro processo; o arquivo só sai ainda sob a trava e com `samestat` (`tests/test_drive.py`, classe `EstadoSoUmPorVez`).
- **Revisão confere com o código:** qualquer mudança em `3d69536` invalida o `--conferir` da rodada 7; documento das pastas SDD fica fora do diff.
- **Rode gate e sabotagens sem outra carga:** testes de tempo caem com a máquina ocupada.
- **O `sdd-open` é público**, inclusive a branch `docs/`: detalhe de infraestrutura do privado vai para o privado.
- **Privado só leitura** até o OK do Roberto; abrir a worktree da F15 é a primeira alteração.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `3d69536` = tag `v2.7.1`; branch remota `feat/f14-drive-v271` (PR #19 MERGED) pode sair.
- Worktree `sdd-open-f14-drive` removida e branch local `feat/f14-drive` apagada em 2026-11-08 (já em `main`). Revisões, trace e ledgers: `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_DRIVE-v2.7.1-revisoes-traces.tar.gz`.
- Worktree da F15: `/Users/robertoduarte/rdd-worktrees/f15-substituicao`, branch `feat/f15-substituicao` (privado).
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16` ficou velha depois do envio da F18 para a `docs/`; removê-la é decisão do Roberto. A branch local `feat/f14-playbook` também pode sair.
- Os artefatos SDD estão na branch `docs/incorporar-starter`; as pastas `EXTERNAL_REVIEW_*` da sessão 13 ficam só nesta máquina, em `sdd/reports/reviews/`.

---

## 2026-11-06 — F14 Drive, entrega 2 de 2 (entregue, Release v2.7.0)

### O que foi feito

- **Fluxo SDD** (sessão 12, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, branch `feat/f14-drive`):
  - artefatos: `sdd/features/BRAINSTORM_F14_DRIVE.md`, `DEFINE_F14_DRIVE.md` (v1.9, 38 ATs), `DESIGN_F14_DRIVE.md` (v1.8, 12 decisões, 38 linhas no manifest), `sdd/reviews/UX_REVIEW_F14_DRIVE.md`, `sdd/reports/BUILD_REPORT_F14_DRIVE.md` (`report-lint` 0);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F14_DRIVE_20261105.md` (4 HIGH, 14 MEDIUM, 8 LOW, 5 propostas, tudo aplicado), `AVALIACAO_F14_DRIVE_20261105-ciclo1.md`, `-ciclo2.md`, `-ciclo3.md`; ledger da revisão real em `sdd/reports/evidence/F14_DRIVE/ledger-review.md`; registro da release em `release-ledger-v2.7.0.yaml` (mesma pasta);
  - commits sobre `8a320e9`: `aabc4a3` (curadoria da F14 Playbook, o antigo `252d351`), `3331b6c` (os 5 achados da rodada 4), `7f4f442` (build), `f519661`, `8334159`, `079f5fa`, `58d0175`, `79ea6c0`, `68d2341` (ciclos 1 a 3), `ff5c539`, `c9a35d9`, `52f0830`, `c5b0655`, `b0663d3` (consertos das rodadas 1 a 4); PR https://github.com/robertodiasduarte/sdd-open/pull/18 (MERGED).
- **Decisões do Roberto no brainstorm:** drive inteiro nesta entrega; rodada = passada inteira + gate, `drive.max_rounds` default 3; só as 2 pendências que tocam o drive (a guarda do avaliador e o log de sonda da curadoria); 2º revisor pelo DeepSeek na OpenRouter; 2 campos novos para o deploy (`deploy.workflow`, `deploy.transient_steps`); abordagem "o script decide, o agente faz"; gate alterado durante a execução para e pergunta; build numa sessão só.
- **`sdd-drive` 1.0.0** (`.agents/skills/sdd-drive/`, `sdd/bin/sdd-drive.sh`, `docs/sdd-drive.md` + PT): saídas 0/2/10/20/40/64; 12 motivos de parada (`gate-verde`, `simulacao`, `orcamento-rodadas`, `manual-ux`, `clarificacao-pendente`, `define-invalido`, `gate-inconclusivo`, `gate-alterado`, `bloqueio-humano`, `aguardando-sessao`, `estado-invalido`, `branch-padrao`); 8 ações (`ESPERAR`, `DESIGN`, `REVISAO_DESIGN`, `RODADA`, `CORRIGIR`, `COMMITAR`, `VERIFICAR`, `AVALIAR_E_RELATAR`). Só o script roda o gate que decide; o drive para antes do release e nunca publica. `verificar --fundo` sobrevive a gate longo; impressão digital do gate; trava do gate + trava de estado curta.
- **O2 raio de impacto** (`sdd-release` 2.8.0, passo 0b; `references/raio-de-impacto.md`), **O3** `sdd/bin/deploy-do-sha.sh` (o item 10 da `sdd-release` chama o script, a lógica é uma só), **O4** `sdd/bin/sdd-archive.py` (retroativo, com simulação; ficha aberta protege). Linha `sdd-drive` saiu do `docs/roadmap.md` + PT.
- **Também:** `verify-gate.sh --checar` e `manual_fallback:` no `--print`; `sdd-fluxo.sh seguir --drive` e `executor-drive`; `avaliador-guard.sh` distingue artefato não rastreado nas 4 pastas; `playbook-curator.sh` com `NAO_E_ACHADO`, saída LF, `exige_utf8`, `confere_pasta_exclusiva`; `copiar-docs.sh` com seta única (`sdd-new-session` 1.4.1); contratos `sdd_drive` e `raio_de_impacto` em `sdd/WORKFLOW_CONTRACTS.yaml`.
- **Release:** "Autorizado sdd-open". Push `8a320e9..b0663d3` em `main` + tag `v2.7.0`; runs `release` 42216757169 (main) e 42216757289 (tag) e `publish-gate` 42216757239 verdes; publicada em 2026-11-06T12:47:12Z; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.7.0; SHA-256 de `sdd-open-v2.7.0.tar.gz` `a3864d39c8e95f9f9999ab9f24df854ad4c547d3f8a7e65171c6415a1db2419c`, `shasum -a 256 -c` OK. `deploy-do-sha.sh` real sobre o próprio commit: `✅ no ar — run 42216757169` (`deploy-do-sha-v2.7.0.log`).
- **Curadoria:** 5 contagens automáticas (LM-001, 002, 003, 005, 006), 2 lições aceitas pelo Roberto (LM-007, `--no-renames`; LM-008, limite da chave da OpenRouter não é saldo) e 10 descartadas. Commit `b3526ae`, **só na branch local `feat/f14-drive`**, não enviado, por decisão do Roberto: um push em `main` que toca o playbook publica a `v2.7.1`.

### Casos e testes em aberto

- **Piso:** 1.656 testes, 1 pulado, `[exit=0]` em `b0663d3` (`sdd/reports/evidence/F14_DRIVE/verify-gate-b0663d3.log`); a base `8a320e9` tinha 1.411.
- **CI:** no PR #18, Ubuntu 20m35s (teto 25) e macOS 35m38s (teto 45). Sobra pouca margem.
- **Revisão real:** 5 rodadas, US$ 18,04, com a maior parte nominal da assinatura; 3 rodadas têm 1 papel sem custo medido (`real-rodada1` a `real-rodada5.log`). A última, `sdd/reports/reviews/EXTERNAL_REVIEW_20261106-072404`, é sobre `b0663d3`: `--conferir` CONFERE e `loop` BLOQUEADO no teto, publicada por D4. Os relatórios de cada rodada estão em `sdd/reports/evidence/F14_DRIVE/rodada<N>-reviewer.md`, `-reviewer2.md` e `-auditor.md`. As pastas `EXTERNAL_REVIEW_*`, o trace e o registro: `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_DRIVE-revisoes-traces.tar.gz`, só nesta máquina.
- **Rodada 1 a rodada 5, em uma linha cada:** 1 HIGH do DeepSeek rebatido por medição (`r1-repro.log`); 1 HIGH real, consertado; 0 HIGH; 3 HIGH de concorrência do Codex, auditor sem crédito, rodada inválida; 1 HIGH do Codex e 4 achados de Claude, levados à D4.
- **Prova do AT-038:** Codex CLI 0.163 com `gpt-6.1-sol`, a conta dele, 3 sessões (`codex-b0663d3-parada.log`, `-executor.log`, `-retomada.log`): 0 falhas; `motivo final: gate-verde`; o commit do agente valeu (git separado por `--separate-git-dir` + `--add-dir`); nenhum push.
- **Sabotagens em `b0663d3`:** 67; 64 derrubam teste. As 3 vivas: `pega_trava` e impressão gravada no gate (mutantes equivalentes); "archive: slice não protege" (falta 1 teste, listado abaixo). Logs `sabotagens-b0663d3.log` e `sabotagens-resto-b0663d3.log`.
- **Avaliador:** ciclo 1 (1 HIGH, 9 MEDIUM, 16 LOW), ciclo 2 (1 HIGH, 4 MEDIUM, 16 LOW; o HIGH era regressão do ciclo 1), ciclo 3 por D4 (0 HIGH, 5 MEDIUM, 14 LOW).
- **Não verificado:** nenhum avaliador rodou depois de `68d2341`; o ramo `tasklist` do `deploy-do-sha.sh` e `report-lint`, `sdd-archive` em Windows não têm prova, e nada rodou em Windows.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- **Os 5 achados da rodada 5, primeira tarefa da sessão 13** (`sdd/reports/evidence/F14_DRIVE/rodada5-reviewer.md` e `rodada5-reviewer2.md`; decisão D4 de 2026-11-06):
  - R1@codex HIGH, `sdd/bin/sdd-drive.sh:330`: a trava de estado vence aos 60 s com o dono vivo, e outro processo a toma. Conserto: pid na trava e checar se está vivo.
  - R1@claude MED, `.agents/skills/sdd-release/SKILL.md:231`: "`--teto 300` e repita enquanto sair 4" não tem teto total; o texto antigo dizia ~2 min sem run.
  - R2@claude LOW, `sdd/bin/deploy-do-sha.sh:130`: 401 no disparo sai 3 sem `desmarcar()`.
  - R3@claude LOW, `sdd/bin/sdd-drive.sh:333`: `except OSError: continue` sem sleep nem limite, laço de CPU.
  - R4@claude LOW, `sdd/bin/sdd-archive.py:258`: documento recente em "sem classificação".
- **Teste que falta:** ficha aberta de slice sem documento com o nome do slice (a sabotagem viva "archive: slice não protege").
- **Do ciclo 3 do avaliador:** L1 (edição temporária durante o gate), L2 (`skip-worktree`), L3 (`BUILD_REPORT` velho), L6 (arquivo ignorado), L7 (gate morto por sinal), L8 em parte (gate órfão), L13 em parte, L14 (DEFINE com CRLF em `verify-gate.sh`), M5 em parte (`$ cmd` de várias linhas: contagens falsas seguem na colheita; o curador sugeriu possível repetição de LM-005, em `NAO_JULGADO`). Do ciclo 1: L16 tratado sem teste próprio.
- **`sdd-fluxo.sh`** importa módulo da pasta do projeto (`json.py`), porque roda `python3 -B -` sem `-I`.
- **Evidência:** `AVAL-26` e `AVAL2-21` acusados no `gate-shell-evidencia.sh` (sondas fora do diff).
- **Herdadas:** fronteira F5, F6, F7 e a guarda de F9; curadoria L7, N-L9, N-L10, resto de N-L11, N3-L4 (etapas F14 Playbook, F13, F12 e F9).

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Riscos aceitos pelo Roberto (D4):** (1) publicar com os 5 achados acima, incluído 1 HIGH de concorrência; (2) `loop` BLOQUEADO no teto de rodadas; (3) nenhum avaliador depois de `68d2341`.
- **Tempo de CI:** Ubuntu 20m35s de 25; macOS 35m38s de 45. A próxima frente grande de testes pede dividir a suíte ou subir o teto, por decisão do Roberto.
- **Ponto de extensão do smoke visual (U3):** é da F15.
- **`CURATOR-colhidos.txt` segue fora do versionamento:** cópia em `sdd/reports/evidence/F14_DRIVE/CURATOR-colhidos.txt`.

### Próximos passos

1. **Sessão 13, tarefa 1** (domingo, 2026-11-08; prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, recriada por `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/retomar-sessao13.sh`: levar `b3526ae`, consertar os 5 achados e o teste que falta. Pronto quando: `gh release view v2.7.1 -R robertodiasduarte/sdd-open` mostra `SHA256SUMS.txt` e `shasum -a 256 -c` confere.
2. **F15, brainstorm**: `sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md`, com as decisões do quadro F15 respondidas pelo Roberto. Pronto quando: o Roberto confirmou a abordagem, inclusive se a migração é de uma vez ou por fase.
3. **F15, execução no repositório privado**, numa sessão aberta na worktree de lá. Pronto quando: o critério do quadro F15 (`doctor` ✅, feature real de ponta a ponta, as pastas do SDD privado fora do git).
4. **F16** e **F17** (plano, seção 8).

### Alertas — o que não quebrar

- **`--no-renames` e `--ignore-submodules=none`** nas conferências de diff do drive: sem eles, um rename commitado passou por "só documento" (HIGH do ciclo 2, `tests/test_drive.py`).
- **Saldo não é limite:** `limit_remaining` de uma chave da OpenRouter é o limite dela. Saldo: `GET /credits`. Confundir os 2 custou uma rodada (LM-008).
- **Conserto de concorrência pede teste dos 2 lados:** o HIGH da rodada 5 nasceu no conserto da rodada 4 (`b0663d3`, trava de estado).
- **O padrão `/drive` segue proibido no pacote:** a varredura da W0 reprova; por isso o documento se chama `docs/sdd-drive.md`.
- **`publish-gate`** reprova literal de 11+ dígitos em teste: monte o valor em execução (`ff5c539`).
- **Nunca `pkill -f` por padrão de comando:** atinge outra sessão com o mesmo comando; pare pelo pid.
- **Qualquer mudança no código invalida a revisão** (`--conferir` compara o sha do diff), mas os documentos das `PASTAS_SDD` ficam fora do diff.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `b0663d3` = tag `v2.7.0`.
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive` removida a pedido do Roberto (2026-11-06). A branch local `feat/f14-drive` fica em `b3526ae`. **O `b3526ae` só existe nessa branch local:** não a apague antes de levar o commit. Para recriar: `bash /Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/retomar-sessao13.sh`.
- A branch local `feat/f14-playbook` já pode sair: o `252d351` foi levado como `aabc4a3`. Não foi apagada; apagar é decisão do Roberto.
- Os artefatos SDD estão na branch `docs/incorporar-starter`.

---

## 2026-11-05 — F14 Playbook, entrega 1 de 2 (entregue, Release v2.6.0)

### O que foi feito

- **Fluxo SDD** (sessão 11, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-playbook`, branch `feat/f14-playbook`):
  - artefatos: `sdd/features/BRAINSTORM_F14_PLAYBOOK.md`, `DEFINE_F14_PLAYBOOK.md` (v1.8, 45 ATs), `DESIGN_F14_PLAYBOOK.md` (v1.5, 15 decisões, 61 linhas no manifest), `sdd/reviews/UX_REVIEW_F14_PLAYBOOK.md`, `sdd/reports/BUILD_REPORT_F14_PLAYBOOK.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F14_PLAYBOOK_20261105.md`, `REVISAO_FRONTEIRA_F14_PLAYBOOK_20261105.md`, `AVALIACAO_F14_PLAYBOOK_20261105-ciclo1.md`, `-ciclo2.md` e `-ciclo3.md`; ledger da revisão real em `sdd/reports/evidence/F14_PLAYBOOK/ledger-review.md`; registro da release em `release-ledger-v2.6.0.yaml` (mesma pasta);
  - commits `864fd8d` (build), `9b3dad1`, `17dc00c`, `eada1e2` (ciclos 1 a 3), `6cbfa33`, `0028ea4`, `8a320e9` (consertos das rodadas 1 a 3), sobre `b1348bd`; PR https://github.com/robertodiasduarte/sdd-open/pull/17 (MERGED).
- **Decisões do Roberto no brainstorm:** F14 em 2 entregas (`F14_PLAYBOOK` = `v2.6.0`, `F14_DRIVE` = `v2.7.0`); D11: só `drive.max_rounds`, default 3, na 2ª entrega, e `drive.max_tokens` cai; versão por tag; abordagem A (porte enxuto, com lock dentro do script); pendências LOW da F13 entram; amostras das fixtures do privado, reescritas de forma genérica.
- **`sdd/bin/playbook-curator.sh`:** `--preparar`, `--colher`, `--aplicar`, `--cruzar`, `--validar-inv`, `--aplicar-inv`, `--selar`, `--conferir-bloco`, `--self-test`. Tabela de landmines lida **pelo cabeçalho**; sem as colunas, `TABELA_SEM_CABECALHO`, sem contagem. Registro do já julgado por `fp=`.
- **`sdd-release` 2.7.0, passo 17b:** script colhe, agente fresco julga, conferidor separa `AUTO` de `PERGUNTA`, cópia conferida 3 vezes, commit à parte, envio em pergunta D1. Brief em `.agents/skills/sdd-playbook/references/curator.md`; contrato `curador` em `sdd/WORKFLOW_CONTRACTS.yaml`.
- **Também:** `sdd/invariants.md` e a trava; `.agents/skills/sdd-new-session/scripts/copiar-docs.sh`; `sdd/templates/HANDOFF_TEMPLATE.md` com 6 seções; `governanca-fronteira.sh` com `#REF`, `#INDICE`, `#GIT`; restauração do DEFINE na `sdd-define` 2.5.1; consertos em `design-lint.py`, `prompt-drift-scan.sh`, `playbook-lint.sh` (piso de 1 alterado), `tests/apoio.py` (o `SDD_TRACE` não vaza mais); `docs/playbook-curation.md` + PT.
- **Release:** "release autorizado sdd-open". Push atômico `b1348bd..8a320e9` em `main` + tag `v2.6.0` (`9e81627`); runs `release` 42080963332 (tag) e 42080963611 (main) e `publish-gate` 42080963388 verdes; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.6.0; SHA-256 de `sdd-open-v2.6.0.tar.gz` `32dfb8a82b7c16d1d90207043dc93525a56d873da0f4462828c16c762ed6a429`, `shasum -a 256 -c` OK (`sdd/reports/evidence/F14_PLAYBOOK/release-v2.6.0.sonda.txt`).
- **Primeira curadoria real:** 3 contagens automáticas e 2 lições aceitas pelo Roberto (LM-005, LM-006); o curador descartou 2 contagens falsas (log de sonda e termo coincidente), e a regra permanente que dependia da primeira caiu junto. Commit `252d351`, **só na branch local `feat/f14-playbook`**, não enviado, por decisão do Roberto: um push na `main` que toca o playbook publicaria a `v2.6.1`.

### Casos e testes em aberto

- **Piso:** 1.411 OK em `8a320e9` (`sdd/reports/evidence/F14_PLAYBOOK/verify-gate-8a320e9.log`); base `b1348bd` tinha 1.134.
- **CI:** no PR, Ubuntu 17m41s e macOS 29m22s (tetos 25 e 45).
- **Revisão real:** 4 rodadas, US$ 14,87 (`real-rodada1` a `real-rodada4.log`, na pasta de evidência). A última, `sdd/reports/reviews/EXTERNAL_REVIEW_20261105-132615`, é sobre `8a320e9`: `loop` PRONTO e `--conferir` CONFERE (`real-rodada4-fechamento.log`). A worktree da F14 foi removida; as 4 pastas `EXTERNAL_REVIEW_*`, o trace e o registro ficam em `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F14_PLAYBOOK-revisoes-traces.tar.gz`, só nesta máquina.
- **Prova do AT-038:** Codex CLI 0.163 com `deepseek/deepseek-v4-pro` pela OpenRouter, **não o modelo da OpenAI** (conta sem créditos). `codex-8a320e9-*`: bloco reprovado por crases escapadas; na retomada, o agente redespachou sozinho e o bloco novo passou. `codex-8a320e9-r2-*`: as 3 cláusulas passam, com o bloco aprovado na 1ª tentativa. O resumo da r2 sai `exit=1` só pela verificação de commit.
- **Sabotagens:** 27 em `8a320e9` (`sabotagens-8a320e9-r2.log`), 26 derrubam teste; 1 viva conhecida, a lista de salvos do `copiar-docs.sh`. O teste que a derruba está em `pendencia-r5-teste-lado2.patch`, conferido contra o mutante.
- **Não verificado:** o commit do item 8 do 17b nunca rodou fora do Claude (o sandbox do Codex deixa `.git` só leitura); nenhum avaliador rodou depois de `eada1e2`; R1 da rodada 4 (Windows) não foi medido; nada rodou em Windows.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- **Os 5 achados de Claude da rodada 4, primeira tarefa da `F14_DRIVE`** (`sdd/reports/evidence/F14_PLAYBOOK/rodada4-reviewer.md`; decisão D4):
  - R1 MED PLAUSIBLE, `sdd/bin/playbook-curator.sh:88`: sem `newline="\n"` no stdout, Python nativo do Windows grava `--aplicar` e `--aplicar-inv` em CRLF. Conserto: `_canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")`. O auditor discordou.
  - R2 LOW CONFIRMED, `playbook-curator.sh:161`: `ler()` com `errors="replace"` faz o `--aplicar` com delta real trocar byte inválido por U+FFFD sem aviso. Conserto: recusar com exit 2, em delta real; delta vazio segue preservando os bytes.
  - R3 LOW CONFIRMED, `copiar-docs.sh:138`: com `IGNORADO` e `PARECIDO` juntos, a seta omite para onde copiar à mão (AT-027). Veio do conserto de R6 da rodada 3. Conserto: seta única que junta os casos, sem cadeia de `elif`.
  - R4 LOW PLAUSIBLE, `.agents/skills/sdd-release/SKILL.md:314`: sem subagente, nada registra a reprovação anterior entre sessões. Conserto: brief com `conferencia:` já é 2ª tentativa. O auditor discordou.
  - R5 LOW PLAUSIBLE, `playbook-curator.sh:368`: `--preparar` aceita pasta de staging previsível já existente, sem conferir dono nem permissão. O auditor discordou.
- **Teste do outro lado do R5 da rodada 3:** `git apply sdd/reports/evidence/F14_PLAYBOOK/pendencia-r5-teste-lado2.patch` (`test_link_so_no_indice_nao_e_dito_como_salvo`).
- **Fronteira:** repositório aninhado que já existia (F5); só permissão em arquivo já sujo (F6); grafia do permitido (F7); a guarda por arquivo da retomada (F9), com a retomada ainda podendo lavar uma escrita.
- **Curadoria:** log de sonda colhido como achado real (L10): o curador real descartou o caso em `AVAL2-V2-aposentar-e-bordas.log:40`, mas a contagem falsa segue saindo da colheita; CRLF em delta real, `git branch` e `git tag` na fronteira, marcas de conflito no `--aplicar` e `NAO_JULGADO` no registro (N-L9, N-L10, resto de N-L11); `wrapper_pattern` em lista de bloco vira slot vazio (L7).
- **Prova:** em `codex-curadoria.sh`, a verificação de commit só reconhece a mensagem `index.lock': Operation not permitted`, e "o commit leva o playbook" olha o commit base quando não há commit novo. Corrija antes de reusar o script.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Riscos aceitos pelo Roberto (D4):** (1) publicar sem 5ª rodada, com os 5 achados acima; (2) último veredito do avaliador em NEEDS_WORK (ciclo 3), corrigido em `eada1e2`, sem 4º ciclo.
- **Rebatida a lembrar:** o único HIGH da rodada 4 (DeepSeek: "falta `--ignored`") é falso por medição (`deepseek-r1-repro.log`), e o auditor concordou sem medir. Achado de modelo barato pede medição antes de qualquer conserto.
- **Guarda do avaliador:** sai 1 com os artefatos que a regra deixa fora do commit (`guard-avaliador-864fd8d.log`); distinguir esses artefatos.
- **Registro:** em `sdd-open`, `git ls-files sdd/releases` vem vazio: `CURATOR-colhidos.txt` não é versionado (N3-L4). Cópia em `sdd/reports/evidence/F14_PLAYBOOK/CURATOR-colhidos.txt`; uma frente nova da mesma feature rejulgaria.
- **Pendências herdadas:** ver as etapas F13, F12 e F9.

### Próximos passos

1. **Sessão 12 — `F14_DRIVE`** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, de `origin/main` = `8a320e9`. Pronto quando: `252d351` e os 5 achados estão no commit; `sdd-drive.sh --dry-run` para no Verify Gate com motivo tabelado; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` 0; e a Release `v2.7.0` confere no `shasum -a 256 -c`.
2. **F15** (plano, seções 8 e 10), com o ponto de extensão do smoke visual.
3. **F16** e **F17** (plano, seção 8).

### Alertas — o que não quebrar

- **Contagem nunca entra sem o conferidor:** `AUTO` só em linha `contador` igual à colheita; regra, sempre pergunta (`tests/test_curadoria_bloco.py`, `test_playbook_curator.py`, `test_playbook_invariantes.py`).
- **Tabela pelo cabeçalho:** adivinhar a célula regrediu 2 vezes seguidas (L1 → N-H1 → N3-H1); não volte a heurística.
- **`#GIT`:** `branch.*` fica fora da medida do config comum; o resto conta (`tests/test_governanca_fronteira.py`).
- **Qualquer mudança no código invalida a revisão** (`--conferir` compara o sha do diff), inclusive só teste e arquivo editado sem commit: combine o conserto com a próxima rodada.
- **Evidência de prova real:** nunca repita o mesmo prefixo. Heredoc aninhado com o mesmo delimitador quebra o comando inteiro.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `8a320e9` = tag `v2.6.0`.
- Worktree `sdd-open-f14-playbook` removida a pedido do Roberto (2026-11-05). A branch local `feat/f14-playbook` fica em `252d351`, mesclada até `8a320e9`: **o `252d351` só existe nessa branch local**. Não apague a branch antes de levar o commit.
- Worktree da próxima sessão: `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive`, branch `feat/f14-drive`.
- Os artefatos SDD estão na branch `docs/incorporar-starter`.

---

## 2026-11-04 — F13 UX e LLM no código (entregue, Release v2.5.0)

### O que foi feito

- **Fluxo SDD** (sessão 10, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm`, branch `feat/f13-ux-llm`):
  - artefatos: `sdd/features/BRAINSTORM_F13_UX_LLM.md`, `DEFINE_F13_UX_LLM.md` (v1.7, 34 ATs), `DESIGN_F13_UX_LLM.md` (v1.4, 12 decisões, 40 linhas no manifest), `sdd/reviews/UX_REVIEW_F13_UX_LLM.md`, `sdd/reports/BUILD_REPORT_F13_UX_LLM.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F13_UX_LLM_20261104.md`, `AVALIACAO_F13_UX_LLM_20261104-ciclo1.md`, `-ciclo2.md` e `-ciclo3.md`; ledger da revisão real em `sdd/reports/evidence/F13_UX_LLM/ledger-review.md`; registro da release em `release-ledger-v2.5.0.yaml` (mesma pasta);
  - commits `a63ed1a` (build), `59420a9` (prova real), `08fbb5b`, `32cc42c` (ciclos 1 e 2), `867d6de`, `726c43c`, `cdb85a9`, `5ddc433` (rodadas 1 a 4), `b1348bd` (ciclo 3), sobre `6b7633c`; PR https://github.com/robertodiasduarte/sdd-open/pull/16 (MERGED).
- **Decisões do Roberto no brainstorm:** U3 fora e `smoke.*` caem; só `prompts.wrapper_pattern`; `v2.5.0` por tag; `#777777` = 4.47, truncado; abordagem A (porte enxuto: trava só onde a conta é exata); 2 checkpoints confirmados, com 5 diferenças em relação ao privado (saída 2 no REPROVA, 64 em caminho inexistente, self-test autocontido, número com ponto em qualquer idioma, exclusão de teste em várias linguagens).
- **`sdd/bin/contraste.sh`:** razão WCAG truncada, alpha composto em sRGB, `--piso`, saídas 0/2/64, centésimos inteiros (`#6c7b67` exato 4,4999996 → `4.49:1 REPROVA`).
- **`sdd/bin/prompt-drift-scan.sh`:** `--conteudo`, disco, `--self-test` autocontido (90 casos); sinais de pasta `prompts/`, nome com `prompt`, SDK (com fronteira nos 2 lados), `system` com literal, `role` de sistema, e o slot; caminho e raiz físicos; nunca conclui LIMPO sem ter lido (saída 64 em pasta, ilegível, entrada vazia, slot inválido, config que não se lê, `grep` ou `cat` que falham).
- **Skill `sdd-loop-builder` 1.0.0:** LOOP_SPEC v2 em português, com as marcas em inglês; perfil por risco e, entre os reversíveis, por quem julga; orçamento por estágio é desenho da skill, marcado como proposta; exemplo genérico `standard`.
- **`sdd-build` 2.6.0 (passo 4):** item no inventário vai direto ao roteador; o texto gerado passa pelo scan, onde 2 é o esperado; rotas de "item faltando" e "não é laço"; fora do inventário, 2 para e pergunta. **`sdd-design` 2.5.0** (5.5 copia o fragmento), **`sdd-ux-review` 2.5.0** (passo 4.5, tabela WCAG com o texto da norma), **`sdd-prompt-builder` 2.1.2**, `WORKER_BRIEF.md`, `design-lint.py`, config, `docs/llm-in-code.md` + PT, roadmap só com a `sdd-drive`, guia do aluno, READMEs; `MANIFEST.txt` 403 → 415.
- **Correções sobre o privado (P1):** 1.4.3 "inclusive desabilitado" e 2.4.7 "anel ≥3:1" vão além da norma e saíram; 2.5.8 cita as exceções; `action_space` sem perfil virou `standard+`; o perfil tinha 2 critérios de tamanho.
- **Release:** "Autorizado sdd-open". Push atômico `6b7633c..b1348bd` em `main` + tag `v2.5.0` (`1c58b77`); runs `release` 41930183324 (tag) e 41930183618 (main) verdes; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.5.0, nota com o aviso do `design-lint`; SHA-256 de `sdd-open-v2.5.0.tar.gz` `00a340380e098afc3dcc2fbd7e97b4b18dbaf4b918dd6eb36c6d910cec7023bf`, `shasum -a 256 -c` OK (`release-v2.5.0.sonda.txt`).

### Casos e testes em aberto

- **Piso:** 1.134 OK em `b1348bd` (`sdd/reports/evidence/F13_UX_LLM/verify-gate-b1348bd.log`); base `6b7633c` tinha 992.
- **CI:** Ubuntu 14m18s, macOS 28m33s (tetos 25 e 45). GNU grep e mawk só foram provados no CI, não localmente.
- **Revisão real:** 6 rodadas, US$ 14,00; a última é `sdd/reports/reviews/EXTERNAL_REVIEW_20261104-182724`, sobre `b1348bd`. A pasta é ignorada pelo git; a worktree da F13 foi removida, e as 6 rodadas e o trace ficam em `/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F13_UX_LLM-revisoes-traces.tar.gz`, só nesta máquina: `loop` PRONTO, `--conferir --aceitar-sem-revisor2` CONFERE. Sem HIGH em nenhuma.
- **Codex CLI 0.163:** 9 execuções reais, em 3 commits. `cdb85a9-codex-sem-skill.log` PASSA, com D2 à letra. `feliz` e `sem-tipo` deram certo no efeito em `867d6de`, mas os transcritos se perderam (`prova-real-resumo.md`). Conferência por efeito com calço: `confere_roteador.py`, `controles.sh` (22 controles).
- **Não verificado:** nenhum avaliador rodou os testes de aceitação em `b1348bd` (o ciclo 3 foi em `5ddc433`; o conserto dele foi conferido pela rodada 6 e pelo gate); `feliz` e `sem-tipo` não têm execução real depois de `867d6de`; a skill nunca especificou um laço de produção, só a amostra; o `prompt-drift-scan.sh` nunca rodou num projeto real com wrapper próprio.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- `design-lint.py`: títulos fora do padrão desligam a conferência sem aviso (`## 5.5. LLM Prompts`, `## LLM Prompts v2`, `## LLM Prompts do sistema`); chave sem preencher passa em `Tom/audiência`, `Tipo de saída` e `Fallback aprovado` (rodadas 5 e 6, ciclo 3 L3).
- `prompt-drift-scan.sh`: `wrapper_pattern: [a, b]` vira expressão sem aviso; `prompts: {` em várias linhas vira slot vazio, e o aviso diz vazio (rodadas 5 e 6). 2 motivos de saída 64 sem dente no self-test, cobertos em `tests/` (ciclo 3 L1).
- Herdado da F12: `SDD_TRACE=off` derruba 10 testes de trace (conserto: tirar a variável em `tests/apoio.py`).

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Riscos aceitos pelo Roberto (D4):** (1) 2º revisor dispensado nas rodadas 5 e 6, por falta de créditos no Codex; (2) prova real como acima; (3) último veredito do avaliador em NEEDS_WORK, sem 4º ciclo. Repetir `codex-roteador.sh` quando houver créditos fecha o (2).
- **Créditos do Codex:** sem eles, o 2º revisor falha (exit 67) e a prova real não roda; a F14 precisa dos 2.
- **Formas raras fora do scan, de propósito:** `String system = "x";`, `Role: "system"`; o doc diz que a busca não é exaustiva.
- **F15:** ponto de extensão no `sdd-release` para o smoke visual do privado (`scripts/a11y/`, passos 6b, 7b, 10b); quem chama o `contraste.sh` no privado trata a saída 2; o rigor maior da WCAG do privado vai para o playbook dele.
- **Pendências herdadas:** ver as etapas F12 e F9.

### Próximos passos

1. **Sessão 11 — F14 Playbook e orquestração** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): worktree `sdd-open-f14-playbook` de `origin/main` = `b1348bd` (tag `v2.5.0`). Pronto quando (plano, quadro F14): `playbook-curator.sh --colher` sobre `sdd/fixtures/playbook/` produz os 4 tipos de linha; `sdd-drive.sh --dry-run` para no Verify Gate com motivo tabelado; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` → 0; Release com o hash conferido.
2. **F15** (plano, seções 8 e 10), com o ponto de extensão acima.
3. **F16** e **F17** (plano, seção 8): independentes; a F16 não pareia com a F14.

### Alertas — o que não quebrar

- **Contrato do scan:** saídas 0/2/64 e "nunca LIMPO sem ter lido" (`tests/test_prompt_drift_scan.py`); ao restringir um sinal, teste os 2 lados: foi assim que o ciclo 2 regrediu `- role: "system"`.
- **Contrato do contraste:** truncado, saída 2 no REPROVA (`tests/test_contraste.py`). A sabotagem que tira só o `LC_ALL=C` não derruba teste, de propósito (`sabotagens.log`).
- **Evidência de prova real:** nunca repetir com o mesmo nome de arquivo; `erro_uso` dentro de `$( )` só sai da subshell; `[.` numa lista de expressão é erro; no zsh, `set -- $x` não divide palavras e `=====` num `echo` quebra o comando: os logs do `at-*` saíram vazios assim, e só o `report-lint` pegou.
- **2 ciclos do avaliador:** um 3º é pergunta D4, sempre, mesmo sem HIGH aberto.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `b1348bd` = tag `v2.5.0`.
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f13-ux-llm`, branch `feat/f13-ux-llm` em `b1348bd`, já mesclada.
- Os artefatos SDD estão na branch `docs/incorporar-starter`.

---

## 2026-11-03 — F12 Contexto, patterns e governança (entregue, Release v2.4.0)

### O que foi feito

- **Fluxo SDD** (sessão 9, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto`, branch `feat/f12-contexto`):
  - artefatos: `sdd/features/BRAINSTORM_F12_CONTEXTO.md`, `DEFINE_F12_CONTEXTO.md` (v1.4, 26 ATs), `DESIGN_F12_CONTEXTO.md` (v1.2, 18 decisões, 87 linhas no manifest), `sdd/reviews/UX_REVIEW_F12_CONTEXTO.md`, `sdd/reports/BUILD_REPORT_F12_CONTEXTO.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F12_CONTEXTO_20261103.md`, `AVALIACAO_F12_CONTEXTO_20261103-ciclo1.md` e `-ciclo2.md`; ledger da revisão real em `sdd/reports/evidence/F12_CONTEXTO/ledger-review.md`; registro da release em `release-ledger-v2.4.0.yaml` (mesma pasta);
  - commits `fb77fa7` (build), `a57fde6` (ciclo 1), `0f51ac9` (ciclo 2), `89702c4`, `363d8bc`, `0ca09f9`, `d816f77`, `3ebeeea` (rodadas 1 a 5), `96a97ec` (snapshot fora do `.git`), `6b7633c` (teto do macOS), sobre `9508ff0`; PR https://github.com/robertodiasduarte/sdd-open/pull/15 (MERGED).
- **Decisões do Roberto no brainstorm:** D5 = governança sempre no Define, N.A. registrado, inclusive com `--parar`; D8 = o `prova_script` é gravado e ligado ao `cmd` no próprio passo do Define; DEFINE sem a linha `Governança` trava sempre, com a saída explicada; `schema.check_cmd` cai; uma Release só; `v2.4.0` por tag; porte fiel com uma fronteira só para os dois agentes frescos; 4 cortes YAGNI (C5 vai para a F14, `dominio.md` não vem preenchido, extrator de ADR sob demanda, yaml conferido por teste).
- **`sdd-define` 2.5.0:** passo 1.5 (cartógrafo fresco: gerar/reusar/pular, até 2 domínios, um despacho por vez; não trava); passo 11 (o "Step 6.5" do PORTE, renumerado porque no Open o DEFINE só existe em disco no passo 9): marcador antes do despacho, cópia do DEFINE, fronteira, `governanca-bloco.py`, `PADRAO_AUSENTE` sem contar falha, uma pergunta D2 por lacuna, prova SQL no próprio passo, 2 saídas na 2ª falha. Status com a etapa 7 "Governança". Briefs `sdd-define/references/cartografo.md` e `sdd-governanca/references/revisor.md`.
- **`verify-gate.sh`:** 2º motivo do exit 5 (linha `| **Governança** | … |` no `## Technical Context`, fora de cerca ``` ou ~~~, com valor `N.A. — …`, `GOVERNANCA_REVIEW_…` ou `dispensada — …`; placeholder não passa), texto GOVERNANÇA NÃO REVISADA, 2 saídas e `→` próprio; ordem marcador → linha → bloco.
- **`sdd/bin/` novos:** `contexto-lint.sh` (lint, `--validade`, `--sugerir`, `--self-test`, 7 seções genéricas, exits 0/1/2/64); `patterns-lint.sh` (lint, `--design`, `--self-test`, limite de 90 dias, exits 0/2/64); `governanca-fronteira.sh` (`--snapshot`/`--comparar`, sha256 em Python, realpath, `#HEAD`, `#PERMITIDO`, exits 0/1/64); `governanca-bloco.py` (0/1/2/64); `docs-extract-decisions.sh` (0/2/64).
- **`sdd-design` 2.4.0:** C2, C3, C4, C10, C11. **`sdd-governanca` 2.4.0:** delta mínimo. **`sdd-build` 2.5.1, `sdd-iterate` 2.2.1:** o 2º motivo do exit 5. **`sdd-fluxo.sh despachar`:** texto por papel (`cartografo`, `revisor-governanca`).
- **Outros:** `sdd/patterns/README.md`, `sdd/WORKFLOW_CONTRACTS.yaml` (o `init` os copia sem sobrescrever), 3 templates, `release.yml` com os 2 caminhos novos e `testes-macos` com teto de 45 min nos 2 workflows; `docs/context-and-governance.md` + PT; roadmap com 3 linhas; READMEs e guia do aluno; `MANIFEST.txt` 353 → 403. Plano atualizado: C5 na F14, `schema.check_cmd` fora, F15 com `release.landmines_cmd`.
- **Defeitos herdados do privado, corrigidos (P1):** fixture verde do `patterns-lint` vencia em 90 dias; extrator de ADR não lia a data na linha do Status; fronteira não casava o permitido com `/var` × `/private/var`; âncora na linha 0; `wc -l` sem newline final.
- **Release:** "continue" à D4 (opção recomendada: dispensar a revisão dos últimos commits) e "release ok sdd-open", avisado de que o OK cobre a dispensa e os commits `96a97ec` e `6b7633c`. Push atômico `9508ff0..6b7633c` em `main` + tag `v2.4.0` (`46f6d47`); runs `release` 41734697736 (tag) e 41734699387 (main) verdes; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.4.0, nota com o aviso do exit 5; SHA-256 de `sdd-open-v2.4.0.tar.gz` `9561e03c63a0013e1f89b2a9892ecdce16f71176bc0b396ac582548838264944`, `shasum -a 256 -c` OK (`release-v2.4.0.log`).

### Casos e testes em aberto

- **Piso:** 992 OK em `6b7633c` (`sdd/reports/evidence/F12_CONTEXTO/verify-gate-6b7633c.log`); base `9508ff0` tinha 894.
- **CI:** no `6b7633c`, Ubuntu 14m27s e macOS 27m58s (teto 45). No `96a97ec`, Ubuntu 17m16s; macOS cancelado nos 30 min, depois 27m06s. A F11 levou 17m31s no macOS. Local, módulo a módulo: 838 s → 913 s (`tempos-por-modulo-*.sonda.txt`); sem travamento, mas a causa da alta no macOS não foi medida.
- **Codex CLI 0.163:** `codex-cartografo-40.log` (`exited 40` na linha 2359) e `codex-revisor-40.log` (linha 1059), ambos sobre `96a97ec`; o texto das skills não mudou em `6b7633c`.
- **Revisão real:** 5 rodadas, US$ 13,20; a última é `sdd/reports/reviews/EXTERNAL_REVIEW_20261103-164047`, sobre `d816f77`, só na worktree da F12 (pasta ignorada pelo git). A 3ª deu PRONTO; a 4ª e a 5ª trouxeram 1 HIGH cada, corrigidos.
- **Não verificado:** o caminho de volta do cartógrafo e do revisor com bloco colado depois de uma parada real (a fronteira, o bloco e o despacho têm teste cada um, e o ciclo 2 simulou o passo 11; a volta inteira, num projeto real, não); o `psql` da prova SQL contra um banco real; um cartógrafo fresco gerando um CONTEXTO num projeto real. O dogfood da governança sobre o próprio DEFINE (N.A.) usou a `sdd-governanca` 2.3.0 com um prompt à mão, não o passo 11.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- A suíte não isola `SDD_TRACE` do ambiente de quem a chama: rodar o gate com `SDD_TRACE=off` derruba 10 testes de trace (`verify-gate-a57fde6-com-SDD_TRACE-off.sonda.txt`). Conserto: tirar a variável em `tests/apoio.py`.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Risco aceito pelo Roberto:** `3ebeeea`, `96a97ec` e `6b7633c` não têm revisão externa própria (`--conferir` NÃO CONFERE; dispensa no `release-ledger-v2.4.0.yaml`). As rodadas 3, 4 e 5 acharam, cada uma, um defeito ligado à fronteira ou à restauração do DEFINE (a 3ª, um MED; a 4ª e a 5ª, HIGH): fazer uma revisão focada nisso na F14.
- **Limites declarados da fronteira:** arquivo ignorado fora de `sdd/` e escrita fora do worktree não são vistos; pasta temporária limpa na retomada sai 64 e conta como falha.
- **Tempo do macOS:** 27m58s, com variação de runner; `test_sdd_open` é o maior módulo (385 s). Medir por teste antes de a F13 e a F14 somarem mais.
- **Log do CI:** o `unittest` sem `-v` não mostra onde a suíte estava quando é cancelada.
- **Rebatidas, com motivo no ledger:** `DEFINE_FIXTURE_GOVERNANCA.md` fica `pendente` e sai 5 (é a entrada da revisão); títulos exatos do relatório no `governanca-bloco.py`.
- **C11** é regra de texto, sem script que confira o `UX_REVIEW`.
- **F15:** um CONTEXTO do privado precisa renomear 4 seções para passar no lint; a frase de `revisor-governanca.md:60` do privado precisa da correção da D8.
- **Pendências herdadas:** ver a etapa F9.

### Próximos passos

1. **Sessão 10 — F13 UX e LLM no código** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): worktree nova `sdd-open-f13-ux-llm` de `origin/main` = `6b7633c` (tag `v2.4.0`). Pronto quando (plano, quadro F13): `contraste.sh '#767676' '#ffffff'` → 4.54 PASSA e `'#777777'` → 4.48 REPROVA, com caso RGBA; `skill-lint.py .agents/skills/sdd-loop-builder/SKILL.md` → 0; `prompt-drift-scan.sh --self-test` → 0; Release com o hash conferido.
2. **F14** (com o C5, a revisão focada na fronteira e o isolamento do `SDD_TRACE`, se não vier antes) e **F15** (plano, seções 8 e 10).
3. **F16** e **F17** (plano, seção 8): independentes de F13–F15; a F16 não pareia com a F14.

### Alertas — o que não quebrar

- **Exit 5:** os 2 motivos, a ordem marcador → linha → bloco, a mensagem com as 2 saídas e o `--print` isento (`tests/test_governanca_gate.py`); uma só forma da linha, a da tabela.
- **Fronteira:** o permitido é resolvido no snapshot de antes e nunca depois; o snapshot fica fora do worktree e **nunca no `.git`**, que é só leitura na sandbox do Codex (`tests/test_governanca_fronteira.py`).
- **Campos:** seções, os 4 e os 5 campos, retornos e exits iguais no brief, no passo, no lint e no yaml (`tests/test_f12_textos.py`).
- **Prova no Codex:** exigir a linha ` exited 40 in `. O texto `AGUARDANDO_HUMANO` entra no log quando o agente lê o código-fonte e deu um PASS falso em `3ebeeea` (`codex-3ebeeea-falso-pass/`). O `codex.sh` da F9 tem o mesmo critério fraco: não copiar sem esse ajuste.
- **Gate:** não editar `sdd/bin/verify-gate.sh` enquanto ele roda (o bash lê o script aos pedaços) e não chamá-lo com `SDD_TRACE=off`.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `6b7633c` = tag `v2.4.0`.
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f12-contexto`, branch `feat/f12-contexto` em `6b7633c`, já mesclada.
- Os artefatos SDD estão na branch `docs/incorporar-starter`.

---

## 2026-11-01 — F11 Revisão adversarial: gate offline (entregue, Release v2.3.1)

### O que foi feito

- **Fluxo SDD** (sessão 8, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f11-gate`, branch `feat/f11-gate`):
  - artefatos: `sdd/features/DEFINE_F11_GATE.md` (v1.1, 27 ATs), `DESIGN_F11_GATE.md` (v1.1, 6 decisões, 34 linhas no manifest, Advisor Ledger com 12 notas), `sdd/reports/BUILD_REPORT_F11_GATE.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS); brainstorm = o da F10;
  - revisões: `sdd/reviews/REVISAO_DESIGN_F11_GATE_20261101.md`, `AVALIACAO_F11_GATE_20261101-ciclo1.md` e `…-ciclo2.md`; ledger da revisão real em `sdd/reports/evidence/F11_GATE/ledger-review.md`;
  - commits `84cf6b5` (build), `468d605` (eval-agree pela engine base), `a9813ff` (ciclo 1), `06e5a9d` (ciclo 2), `ab2f252` (rodada 1), `9508ff0` (rodada 2), sobre `248301d`; PR https://github.com/robertodiasduarte/sdd-open/pull/14 (MERGED).
- **`sdd/bin/adversarial-review-gate.sh`** (bash 3.2 + núcleo Python): roda o `adversarial-review.sh` real com os 4 adapters reais, num repositório descartável, contra stubs por engine; 103 asserções em ~7 s; exits 0 GATE VERDE · 2 GATE VERMELHO (todas rodam, cada ❌ com campo e valor lido) · 3 GATE QUEBRADO (sem isolamento; nada chamado) · 64; `-v` mostra o valor lido.
  - pré-voo: stubs e 19 cenários em `cenarios.tsv`, registry com as 4 engines, `command -v` num `/bin/bash -c` filho com o ambiente exato resolvendo para o `bin` do gate, servidor da OpenRouter subindo em ≤ 5 s;
  - isolamento: tira `BASH_ENV`, `ENV`, `BASH_FUNC_*`, todo `GIT_*` herdado, `SDD_REVIEW_*`/`SDD_STUB_*`; proxies em `127.0.0.1:9`, `no_proxy` só local, `GIT_CEILING_DIRECTORIES` na pasta temporária, raiz do repositório de teste conferida antes do commit, chave `gate-<pid>-falsa`;
  - anel claude→codex→gemini→openrouter→claude com só os campos que discriminam a extração; ≈US$ calculado do `precos.tsv` resolvido (tokens 1234567/234567); contrato 65 (4 engines), 67 (mesma engine e exclusão por fallback), 68, 429 (CLI e HTTP), cota, DISAGREE/NOVO com arquivo, linha e severidade; privacidade (Bearer, deny, chave fora dos arquivos).
- **`sdd/review/stubs/`**: `claude.py`, `codex.py`, `gemini.py`, `openrouter.py` (servidor por cenário; fora da fila = HTTP 599), `comum.py` (fila `SDD_STUB_<ENGINE>`, estado em `SDD_STUB_ESTADO`, sentinela), `cenarios.tsv` (10 colunas; falhas marcadas `sintético`), `respostas/` (revisor, auditor-agree, auditor-sem-bloco, auditor-misto). O gate gera os wrappers das CLIs com `shlex.quote` (o `init` não precisa preservar bit de execução).
- **`sdd/bin/eval-agree.sh`**: lê `EXTERNAL_REVIEW_*/META.txt` + `auditor.verdicts.jsonl`; tabela por auditor (engine base + modelo principal, sem ` via …`, sem `:<slug>`, sem `+…`); `taxa_agree = AGREE / (AGREE + DISAGREE_*)`; "fora da conta" com motivo; exits 0 MEDIDO · 2 SEM DADOS (inclusive sem a pasta padrão) · 64.
- **Achados adiados da F10:** #15 `--conferir` exige `--aceitar-sem-revisor2 "<motivo>"` quando o gatilho foi dispensado por `--no-revisor2`; #17 tarifa do modelo reportado (outro modelo sem preço = `$?`) e `+ $?` para tentativa que estourou o teto numa engine não-assinatura; #18 `--conferir` pula pasta sem META, `--feature` sem documento avisa, gemini soma tokens de todos os modelos.
- **CI e docs:** `testes-macos` com `timeout-minutes: 30` nos 2 workflows; `docs/adversarial-review.md` + PT com "Offline gate"/"Gate offline" e "eval-agree"; `docs/cli-conventions.md`; roadmap EN/PT sem a linha (4 temas); READMEs; `MANIFEST.txt` 331 → 353.
- **Release:** OK "Sim sdd-open"; run `release` 41307505438; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.3.1; SHA-256 de `sdd-open-v2.3.1.tar.gz` `def48c99e135bd394bb11f9673a87ca56476711d666f0923cbf246ce75ff8ecc`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** 894 OK em `9508ff0` (`sdd/reports/evidence/F11_GATE/verify-gate-final.log`); base `248301d` tinha 853. `tests/test_revisao_gate.py` 23 testes em ~110 s; `tests/test_eval_agree.py` 9.
- **CI:** Ubuntu 12m53s, macOS 17m31s (teto 30) no PR #14.
- **Revisão da release:** `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-083920` (sha256 `dbc16432b8edbff938656a0620196493bca5100383546140eac82a58fb43aafa`, `diversidade=vendor`), só na worktree da F11 (pasta ignorada pelo git).
- **Não verificado:** o texto de falha real das CLIs (as linhas de falha dos stubs são sintéticas); a cota real do gemini que vem junto com `429` (o `classe()` testa o transitório antes do persistente: 3 tentativas antes de trocar de engine) — caminho não exercitado.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Fora do escopo da F11, igual na v2.3.0:** codex (assinatura) que audita e sai 68 mostra custo `$?` em vez de `assinatura` (avaliador F11 ciclo 1, nota).
- **Gate:** prova as 4 engines do pacote, não engines acrescentadas pelo projeto; textos de falha sintéticos.
- **Pendências herdadas:** ver a etapa F9.

### Próximos passos

1. **Sessão 9 — F12 Contexto, patterns e governança** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): worktree nova `sdd-open-f12-contexto` de `origin/main` = `9508ff0` (tag `v2.3.1`). Pronto quando (plano, quadro F12): `contexto-lint.sh --self-test` e `patterns-lint.sh --self-test` → 0; DEFINE sem a linha `Governança` → `verify-gate.sh` exit 5; `governanca-fronteira.sh` detecta escrita fora do relatório; Release com o hash conferido.
2. **F13 → F14** e **F15** (plano, seções 8 e 10).
3. **F16 Ambiente agnóstico e proativo** (plano, seção 8; escopo em `sdd/features/ESCOPO_F16_AMBIENTE.md`): implementação no Open, independente de F12–F15; pequena, cabe antes da sessão 9 se o Roberto quiser. Não pareia com a F14 (ambas tocam a `sdd-new-session`).
4. **F17 Starter gerado a partir do Open** (Decisão 5): depois da F16; antes da 1ª geração, comparar skill a skill e trazer para o Open o que o starter tiver melhor.

### Alertas — o que não quebrar

- **Gate offline:** exits 0/2/3/64; o 3 só antes de qualquer chamada; o gate nunca usa rede, CLI real nem o repositório de quem o chama (`tests/test_revisao_gate.py`, inclusive `test_aval2_h1_…` e `test_bash_env_…`); `cenarios.tsv` é a fonte única do que o stub emite e do que o META deve dizer.
- **eval-agree:** só lê arquivos (`test_at017_so_le_arquivos` proíbe `urllib`, `socket`, `adapters/`).
- **CI:** `testes-macos` com 30 min; a suíte levou 17m31s no macOS.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `9508ff0` = tag `v2.3.1`.
- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f11-gate`, branch `feat/f11-gate` em `9508ff0`, já mesclada.
- Os artefatos SDD estão na branch `docs/incorporar-starter`.

---

## 2026-11-01 — F10 Revisão adversarial: núcleo (entregue, Release v2.3.0)

### O que foi feito

- **Fluxo SDD completo** (sessão 8, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao`, branch `feat/f10-revisao`):
  - artefatos: `sdd/features/BRAINSTORM_F10_REVISAO.md`, `DEFINE_F10_REVISAO.md` (v1.3, 41 ATs), `DESIGN_F10_REVISAO.md` (v1.1, 11 decisões, 86 linhas no manifest, Advisor Ledger), `sdd/reviews/UX_REVIEW_F10_REVISAO.md`, `sdd/reports/BUILD_REPORT_F10_REVISAO.md` (`report-lint` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F10_REVISAO_20261031.md` (1 HIGH, 5 MEDIUM, 13 LOW), `AVALIACAO_F10_REVISAO_20261101-ciclo1.md` e `…-ciclo2.md`; ledger da revisão real em `sdd/reports/evidence/F10_REVISAO/ledger-review.md`;
  - commits `7ecbc78`, `6f4ee5b`, `9846919`, `486ed2e`, `1975e7c`, `55a866d`, `248301d` sobre `89ac76f`; PR https://github.com/robertodiasduarte/sdd-open/pull/13 (MERGED).
- **`sdd/bin/adversarial-review.sh`** (bash 3.2 + núcleo Python 3.9): revisor → auditor em cadeia sobre o diff congelado (índice temporário com `copy2`, intent-to-add, opções do `git diff` fixadas, sha256, teto 8 MB); contexto SDD com teto `review.context_max_kb`; exclusão por identidade adapter + modelo (67); vereditos obrigatórios (68, auditoria parcial também); 2º revisor por gatilho (segurança, ≥ 8 arquivos, ≥ 120 KB, ≥ 2 camadas, raso < 30 s) e desempate de HIGH refutado; AUTH para tudo (65), 429 tenta 3 vezes, cota passa para a próxima; custo por papel (`US$` → `≈US$` → `assinatura` → `$?`, nunca 0); pasta da revisão precisa estar ignorada pelo git; `--conferir` (0/2) e `--ledger` (0/2/64).
- **Adapters e dados:** `sdd/bin/adapters/{claude,codex,gemini,openrouter}.sh` (4 funções cada; codex `-s read-only`; OpenRouter por `urllib` com `data_collection: deny` e `HTTP <código>` na 1ª linha do erro); `sdd/review/registry.tsv` (9 colunas, sem cadeia padrão), `precos.tsv` (qwen/qwen3.7-plus e deepseek/deepseek-v4-flash com URL e data), `prompts/{reviewer,auditor,desempate}.md`.
- **Fluxo e skills:** `sdd-fluxo.sh loop` lê `reviewer2.verdicts.jsonl`, revisão rasa e desempate (`DECISAO:REFUTADO` fecha, `PROCEDE` mantém aberto; dispensa do 2º revisor só com motivo); `sdd-release` 2.6.0 (0a item 8: `--conferir`, dispensa D3, campo `review_externo` no ledger, `--ledger` na pasta da frente), `sdd-build` 2.5.0 (passo 0 com `review-design`, 5c), `sdd-design` 2.3.0; `sdd/config.example.yaml` com 5 slots `review.*`; `init` copia `sdd/review/`, `doctor` compara os adapters; docs EN/PT.
- **Release:** OK "ok sdd-open" (D4 e push) e "ok para sdd-open"; push atômico de `main` + tag `v2.3.0`; https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.3.0; SHA-256 de `sdd-open-v2.3.0.tar.gz` `c7ac4059ab52b9c0c05b1b3058992de11464648c003dee7759c9a16767191142`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** 853 OK em `248301d`; base `89ac76f` tinha 744. 14/14 sabotagens.
- **Gemini nesta máquina:** a CLI falha com `ProjectIdRequiredError` (exit 41); as revisões reais usaram claude + codex → openrouter:qwen.
- **Medidas das CLIs** (base dos stubs da F11): `sdd/fixtures/revisao/saidas/` (claude JSON, codex JSONL, gemini JSON, openrouter JSON).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Os 6 achados adiados da rodada 3 (#15, #17, #18) — **entregues na F11**.
- O #16 (o 2º revisor automático exclui o adapter inteiro) ficou rebatido: outro modelo do mesmo adapter continua possível por `--revisor2`.

### Próximos passos

1. F11 — entregue na mesma sessão (etapa acima).

### Alertas — o que não quebrar

- **META** é contrato do `loop`, da release e dos docs: chaves `reviewer_*`, `revisor2_*`, `auditor_*`, `desempate_*`, `diff_sha256`, `diversidade`, `custo_total`; `--conferir` recalcula o diff com as mesmas opções.
- Identidade de engine = adapter + modelo (exclusão, diversidade, `--revisor2`).
- A chave da OpenRouter só no ambiente; a pasta da revisão ignorada pelo git (`$(git rev-parse --git-common-dir)/info/exclude`).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao`, branch `feat/f10-revisao` em `248301d`, já mesclada.

---

## 2026-10-31 — F9 Fluxo encadeado (entregue, Release v2.2.10)

### O que foi feito

- **Fluxo SDD completo** (sessão 7, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo`, branch `feat/f9-fluxo`):
  - artefatos: `sdd/features/BRAINSTORM_F9_FLUXO.md`, `DEFINE_F9_FLUXO.md` (v1.6, 33 ATs EARS, Clarity 14/15), `DESIGN_F9_FLUXO.md` (v1.1, 9 decisões, 88 linhas no manifest, Advisor Ledger com 15 notas), `sdd/reviews/UX_REVIEW_F9_FLUXO.md` (7 MUST de texto) e `sdd/reports/BUILD_REPORT_F9_FLUXO.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F9_FLUXO_20261031.md` (NEEDS_WORK, 3 HIGH, 2 MEDIUM, 10 LOW, aplicadas antes do build), `AVALIACAO_F9_FLUXO_20261031-ciclo1.md` (NEEDS_WORK, 1 HIGH, 2 MEDIUM, 12 LOW, sobre `bb91c42`) e `…-ciclo2.md` (NEEDS_WORK, 1 HIGH de regressão, 1 MEDIUM, 4 LOW, sobre `524f957`), todos aplicados (a metade "SHA só com dígitos" do LOW 14 do ciclo 1 foi rebatida: um número de 7 dígitos pode ser valor legítimo);
  - commits `bb91c42` (build, 87 arquivos), `524f957` (ciclo 1), `daf9c0f` (ciclo 2) e `89ac76f` (teto do `release.yml`), sobre `7c640eb`;
  - PRs https://github.com/robertodiasduarte/sdd-open/pull/11 e https://github.com/robertodiasduarte/sdd-open/pull/12 (MERGED).
- **`sdd/bin/sdd-fluxo.sh`** (bash 3.2, núcleo em `python3 -B` embutido por heredoc):
  - `review-design <DESIGN>` → 0 EXIGIDO (≥ 3 arquivos novos no File Manifest, termos fixos `auth`/`login`/`token`/`senha`/`password`/`jwt`/`GRANT`/rota pública, globs de `review.security_globs` e de `layers.sql`) · 1 DISPENSAVEL · 64 manifest ilegível (quem chama roda a revisão); ignora manifest em bloco cercado; nos 8 DESIGNs F1–F8 dá as contagens da fonte (13, 17, 4, 10, 17, 7, 25, 13);
  - `loop --review <dir> --ledger <arq> --rodada N [--teto 3] [--avaliacao <arq> --ciclo-avaliador K] [--recibo "nome AAAA-MM-DD"] [--log <arq>]` → 0 PRONTO · 10 CONTINUAR · 20 BLOQUEADO (D4 teto, D4 ciclos, D5) · 30 AGUARDANDO_RECIBO · 64; núcleo da fonte (review inválida, graves, ledger por célula com `rodada=N`, base única de `R1@engine`, avaliação de 1 linha `VEREDITO:`), sem o 2º revisor, o desempate, o revisor raso e o `auditor_exit 75` (F10); precedência 64 > 20 > 10 > 30 > 0 conferida contra a fonte em 3 casos de borda; `--log` regravado em toda saída, inclusive 64, erro interno e sem `python3`;
  - `despachar <papel> <FEATURE> <brief>` → **40 AGUARDANDO_HUMANO**: copia o brief para `sdd/reports/briefs/BRIEF_<papel>_<FEATURE>.md` (pula a cópia se já for esse arquivo), imprime a parada ⏸️ com os rótulos do `PERGUNTA_DECISAO.md` e o que colar de volta (avaliador: o bloco `<<<AVALIACAO … >>>` inteiro); nome por lista explícita de caracteres (sem faixa: no bash 3.2 com UTF-8, `[A-Za-z]` aceita acento);
  - `seguir <fase> <DEFINE> <próxima> [--parar]` → 0 SEGUIR (`✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)` + `→ /sdd-<próxima> <arquivo>`) · 1 PARAR (desligado, `--parar`, release = D1, Status do artefato fora de `Ready for`, sem git, gate sem kind/cmd, marcador aberto, `design-lint`, revisão do DESIGN sem linha, sem coluna de severidade ou com HIGH aberto no Advisor Ledger) · 64;
  - `estado` → 0 ligado · 1 desligado · 64 `flow.autonomous` inválido; `--self-test` com 33 cenários (um por exit e o do `| tee`), roda numa cópia sem `.git`.
- **`sdd/bin/sdd-decisoes-lint.sh`** (`--sites <pasta|arquivo…>` 0/2/64, `--self-test`): pergunta de decisão = achado do `perguntas()` do `skill-lint.py` na linha com `**Sua decisão**` (blocos ```` ```markdown ```` abertos); exige 1 marca `[<código> · <rótulo>]` com o rótulo lido da tabela do item 9, 1 recomendada e primeira, "não sei", sem "Outro" e sem AT-/LM-/Dn/SHA fora do `(ref: …)`; 4 fixtures em `sdd/fixtures/conversa/decisoes/` reprovam pelo motivo certo e o controle passa; passo novo no `publish-gate.yml`.
- **Marcas** (item 9 do `PERGUNTA_DECISAO.md`): `[D1 · não se desfaz]`, `[D2 · muda o produto]`, `[D3 · muda a regra do método]`, `[D4 · limite de tentativas]`, `[D5 · provas em conflito]` (perguntadas mesmo com o encadeamento ligado) e `[auto · de rotina]` (com o encadeamento ligado vale a recomendada e a decisão vai para o recibo "Decidi sozinho"); o OK da `sdd-release` não leva marca (D1 por construção). As 15 perguntas de exemplo das skills foram marcadas; a da `sdd-playbook` tirou `LM-004` do texto.
- **Skills** (15 sobem): brainstorm 2.2.0 (tabela de tipos de entrada), define 2.4.0 (pontuação forte/fraco do LLM Prompts), governanca 2.3.0, ux-review 2.4.0 (lê os `UX_REVIEW_*.md` anteriores), design 2.2.0 (F6 só com o encadeamento ligado; `despachar` e `review-design` na revisão do DESIGN), build 2.4.0 (`despachar` no 5d e no degrau 2 do `contexto-fresco.md`; exit 30 no `PASS_PENDENTE_RECIBO`), iterate 2.2.0, release 2.5.0, new-session 1.3.0 — todas com a subseção `### Fluxo encadeado` (bloco comum idêntico + 1 linha) — e auditoria-harness 1.1.1, checar-ambiente 1.4.1, handoff 2.1.1, kb 2.2.1, playbook 2.1.1, prompt-builder 2.1.1 (só a marca).
- **Fragmentos e config:** `sdd/templates/fragments/FLUXO_ENCADEADO.md` (ordem, `seguir`, linha de transição, recibo `- <decisão> — porque <…> · para desfazer: <…>`, paradas que não são decisão, teto do loop, pergunta D4 no formato); seção `## Advisor Ledger` no `sdd/templates/DESIGN_TEMPLATE.md`; `sdd/config.example.yaml` com `flow.autonomous: false` e `review.security_globs: ""`.
- **Docs e testes:** `docs/chained-flow.md` + `docs/pt-BR/chained-flow.md`, links nos READMEs, roadmap EN/PT sem a linha (5 linhas), `cli-conventions.md` com os exits; `tests/test_fluxo.py` (48) e `tests/test_decisoes_lint.py` (11), `test_conversa`, `test_docs`, `test_release_workflow` estendidos, 5 pinos de versão; 32 fixtures em `sdd/fixtures/fluxo/` e `conversa/decisoes/`; `MANIFEST.txt` 234 → 273. **744 testes** no piso.
- **Codex CLI 0.163 (P2):** `sdd/reports/evidence/F9_FLUXO/codex.sh` (cópia por `git archive` commitada, `CODEX_HOME` e `HOME` temporários só com o `auth.json`): AT-030 PASS (a `sdd-define` encadeada terminou em `✅ DEFINE pronto → seguindo para …`), AT-031 PASS (sem subagente, `sdd-fluxo.sh despachar` `exited 40` com o brief gravado).
- **Release:** OK "OK citando \"sdd-open\"" e "autorizado sdd-open" (2026-10-31); run `release` 41246920990 cancelado no teto de 10 min; correção `89ac76f`; tag `v2.2.10` em `89ac76f`; run 41251612805 verde → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.10; SHA-256 de `sdd-open-v2.2.10.tar.gz` `209e086bfd57f650da5f9b281732eaf9bb2ee350daf1978914c8a179aceb330a`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 744 OK em `daf9c0f` (Verify Gate) e no CI de `89ac76f`. A base `7c640eb` tinha 683.
- **Gate e versões:** `verify-gate.sh --strict sdd/features/DEFINE_F9_FLUXO.md` → 0 em `bb91c42` (735), `524f957` (741) e `daf9c0f` (744). `check-versions --base v2.2.9 --base-obrigatoria` VERDE (9 minor, 6 patch). `skill-lint --conversa` 17/17; `sdd-decisoes-lint --sites` 17 perguntas.
- **Evidência:** `gate-shell-evidencia.sh sdd/reports/evidence/F9_FLUXO` → 0 na pasta inteira, sondas dos avaliadores incluídas (a receita do `EVIDENCIA.md` foi passada nos briefs). 8/8 sabotagens; baselines vermelhas na `v2.2.9` e nos commits anteriores de cada ciclo.
- **Não verificado:** o encadeamento numa sessão real do Claude Code com `flow.autonomous: true` (provado no Codex e pelo `seguir` nos testes); o `loop` alimentado por uma revisão adversarial de verdade (não existe no Open antes da F10); as correções do ciclo 2 não passaram por um 3º avaliador (o Roberto escolheu seguir); os testes de locale rodam `pt_BR.UTF-8` no macOS, e no Ubuntu do CI o locale pode não existir (o bash cai para C e o teste continua valendo).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **F10 (+ F11) Revisão adversarial** (sessão 8): `sdd/bin/adversarial-review.sh` + adapters por engine + `sdd/review/registry.tsv`; acrescenta ao `loop` os campos do 2º revisor e do desempate (`revisor2_*`, `desempate_*`, raso, `auditor_exit 75`) como deltas; liga o `sdd-build` passo 0 ao `sdd-fluxo.sh review-design` (R13); o `RESUMO_ETAPA.md` cita `/adversarial-review`.
- **Lint de decisões:** pergunta escrita sem `**Sua decisão**` escapa do `--sites` (o `skill-lint --conversa` continua no `como-falar.md`); SHA só com dígitos ou só com letras não é pego (rebatido: pode ser valor legítimo).
- **Projeto que já tinha o pacote:** o `init` não copia `sdd/fixtures/` de novo nem sobrescreve o `PERGUNTA_DECISAO.md`: lá os 2 `--self-test` saem 64 e o lint de marcas sai 64 (tabela ausente) até copiar os arquivos (`docs/chained-flow.md`, "Limite").
- **CI:** a suíte leva ~12 min no Ubuntu e ~15 no macOS; os tetos agora são 25 e 20 (macOS). A próxima frente que crescer a suíte deve conferir o teto do job `testes-macos` (20).
- **Pendências herdadas:** `test-baseline.sh` com formatos além de 5 saem 3 e `--touched` só filtra por id com nome de arquivo (F7); `gate-shell-evidencia.sh` conservador com comando composto (F7); o sdd-starter como distribuição gerada do open (Decisão 5); o `handoff-lint.py` do open reprova este handoff pelo molde (registrado em 2026-10-30).

### Próximos passos

1. **Sessão 8 — F10 (+ F11) Revisão adversarial** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao` (branch `feat/f10-revisao`, de `origin/main` = `89ac76f`, com os artefatos SDD copiados). Pronto quando (plano, quadro F10): `review.auditor == review.revisor1` → exit 67; 1 engine só → ledger com `diversidade: nenhuma`; `sdd-release` sem `review_externo` no ledger aborta; review real `claude` + `openrouter:<modelo>` com tokens, custo ≠ 0 e sha256 do diff; Release com o hash conferido. F11 só depois da Release da F10.
2. **F12 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **Fluxo encadeado:** os exits do `sdd-fluxo.sh` (review-design 0/1/64, loop 0/10/20/30/64, despachar 40/64, seguir 0/1/64, estado 0/1/64) e o `--self-test` são contrato (`tests/test_fluxo.py`); o `--log` do `loop` é regravado em toda saída; nomes do `despachar` por lista explícita, nunca faixa `[A-Za-z]`. A F10 acrescenta ao `loop`, não reescreve: os 3 casos de borda (review inválida sem jsonl, NEEDS_WORK no teto, HIGH com recibo pendente) saem 10 como na fonte.
- **Marcas:** a tabela das 6 marcas no item 9 do `PERGUNTA_DECISAO.md` é a dona dos rótulos (o lint os lê dali); toda pergunta nova de decisão leva `[<código> · <rótulo>]` antes do negrito; o OK da `sdd-release` fica sem marca.
- **Subseção `### Fluxo encadeado`:** bloco comum byte a byte igual nas 9 skills de fase (`tests/test_fluxo.py::Subsecao`), dentro do `## Encerramento (obrigatório)`; "Por que cada regra existe" continua logo antes do Encerramento.
- **Codex CLI:** o 0.163 tem `multi_agent` estável e abre colaborador mesmo com `--disable multi_agent`; `codex exec` precisa de repositório git (a cópia do `git archive` tem de ser commitada) e `~/.codex/skills/` desta máquina tem cópias velhas das skills SDD (isolar com `CODEX_HOME` temporário e `--ignore-user-config`).
- **CI:** `release.yml` job `testes` com `timeout-minutes: 25` (`89ac76f`); um push que só toca `.github/` não publica Release — tag `vX.Y.Z` empurrada à mão publica.
- Demais alertas das etapas F8, F7, F6, F5, F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `89ac76f` = tag `v2.2.10`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.10.
- Worktree da sessão 7: `/Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo`, branch `feat/f9-fluxo` em `89ac76f`, já mesclada. A worktree de revisão `sdd-open-f9-aval` foi removida; a da sessão 6 (`sdd-open-f8-hooks`) já não aparece no `git worktree list`.
- O checkout principal `/Users/robertoduarte/rdd-public/sdd-open` está em `7c640eb` (`main` local atrás de `origin/main`); a worktree da F10 nasce de `origin/main` depois de `git fetch`.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f9-fluxo`.

---

## 2026-10-31 — F8 Hooks (entregue, Release v2.2.9)

### O que foi feito

- **Fluxo SDD completo** (sessão 6, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks`, branch `feat/f8-hooks`):
  - artefatos: `sdd/features/BRAINSTORM_F8_HOOKS.md`, `DEFINE_F8_HOOKS.md` (v1.4, 30 ATs EARS, Clarity 14/15), `DESIGN_F8_HOOKS.md` (v1.3, 8 decisões, 38 linhas no manifest, Advisor Ledger com 15 notas), `sdd/reviews/UX_REVIEW_F8_HOOKS.md` (a interface é a saída dos hooks e do `init`) e `sdd/reports/BUILD_REPORT_F8_HOOKS.md` (`report-lint` 0, `--pendente` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F8_HOOKS_20261030.md` (NEEDS_WORK, 3 HIGH, 2 MEDIUM, 10 LOW, aplicadas antes do build), `AVALIACAO_F8_HOOKS_20261030-ciclo1.md` (NEEDS_WORK, 1 MEDIUM, 5 LOW, sobre `6a238d2`) e `…-ciclo2.md` (PASS, 2 LOW, sobre `938ce47`), todos aplicados;
  - commits `6a238d2` (build), `938ce47` (ciclo 1) e `7c640eb` (ciclo 2), sobre `1d225e5`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/10 (MERGED); 39 arquivos (13 novos, 26 alterados), +2.244 / −88 linhas.
- **`sdd/hooks/pre-commit`** (272 linhas, bash 3.2, sem arrays): dispatcher com as regras como funções, todas rodam e a recusa é uma só — **H6** commit na `project.default_branch` quando `refs/remotes/origin/<branch>` existe → **H2** arquivo de contexto (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`) acima de `project.context_file_max_kb` (default 100) → **H5** byte NUL em arquivo de texto (UTF-16 com BOM pula) → **H3** credencial em texto claro em `.json/.yml/.yaml/.toml/.env*` (placeholder `${…}`, `{{…}}`, `<…>`, `***`, `changeme/example/xxx` e número de versão passam; toda ocorrência é olhada; `gitleaks protect --staged -v --redact` quando instalado) → **H4** `sdd/playbook.md` apagado/renomeado recusa e modificado passa pelo `playbook-lint.sh --anti-collapse` → **REPORT** `BUILD_REPORT_*.md` staged pelo `report-lint.py --stdin` (pula `sdd/fixtures/` e `sdd/templates/`) → **HIGIENE** `pre-commit.sh` da `sdd-higiene-dado` quando `git config sdd.higieneDado` = `on`. Saída: cabeçalho, uma classe por bloco com "Por que importa", `RESULTADO: COMMIT RECUSADO`, um `→ [classe]` por conserto e a linha final do `git commit --no-verify` com "Agente de IA: não use --no-verify sem o OK explícito da pessoa". Avisos (`⚠️  sdd-open:`) não recusam. Silêncio e exit 0 quando tudo passa.
- **`sdd/hooks/pre-push`** (36 linhas): avisa `<branch> está N commit(s) atrás de <remote>/<default>` e sai 0 sempre (`pre-push` só avisa; decisão do brainstorm).
- **`bin/sdd-open.sh`** (687 → 855 linhas): o plano do `init` ganha a linha `core.hooksPath = sdd/hooks — 5 regras + relatório + alarme passam a conferir cada commit (…); git commit --no-verify pula uma vez`; `aplicar` faz `chmod +x`, `git config core.hooksPath sdd/hooks` e migra o alarme antigo da higiene em `.git/hooks/` para `sdd.higieneDado on` (com aviso); estados `LIVRE | LIGADO | HIGIENE | OUTRO <descr>` (`OUTRO` = husky/lefthook/outro hooksPath: avisa e não mexe); `doctor` imprime `✅ hooks ligados (sdd/hooks: pre-commit com 5 regras + relatório + alarme da higiene on|off, pre-push)` ou um ⚠️ por causa; dica final `git switch -c sdd-open-init` quando o `init` roda na branch padrão com remoto; `hooks_path_e_nosso` aceita `sdd/hooks`, `sdd/hooks/`, `./sdd/hooks` e absoluto por `pwd -P`.
- **Adaptador do Claude Code (E6)**: `bin/adapters/claude/sdd-report-guard.py` (107 linhas; simula o conteúdo final de Write/Edit/MultiEdit e roda `report-lint.py --stdin`; nega com `permissionDecision: deny`; pula `sdd/fixtures/` e `sdd/templates/`; `SDD_REPORT_GUARD=off`) e `sdd-avaliador-guard.py` (71; dispara em despacho de Agent/Task com "veredito" e roda `avaliador-guard.sh`); falha aberta com `systemMessage`. O `init --vendors claude` copia os dois para `.claude/hooks/` e faz merge em `.claude/settings.json` (`merge_claude_settings` em `bin/lib/merge.sh`: `PreToolUse` com `Write|Edit|MultiEdit` timeout 10 e `Agent|Task`; presença pelo comando; outros hooks preservados; forma inválida → exit 66; python3 obrigatório → 64). `PreToolUse` mora **só** em `bin/adapters/claude/` e no que o `init` gera (`tests/test_agnostico.py` com `sdd/hooks` no escopo).
- **`sdd-higiene-dado` 1.2.0**: `alarme.sh` (82 → 136) com três modos — `arquivo` (sem hooksPath, grava `.git/hooks/pre-commit` como antes), `hooks` (`core.hooksPath` nosso + `MARCA_DISPATCHER` no dispatcher: `instalar` = `git config sdd.higieneDado on`, `desinstalar` = unset + remove só o arquivo antigo com a marca da skill, dispatcher nunca tocado) e `outro` (recusa, exit 2); `HOOK` por `--git-common-dir` (o `--git-path` seguia o hooksPath e apontava para o dispatcher); `pre-commit.sh` (120 → 129) troca a linha "Para desinstalar" por `alarme.sh desinstalar` quando há hooksPath (nunca `rm`). SKILL.md, manifest, evals, CHANGELOG e references atualizados.
- **Config e fixtures:** `sdd/config.example.yaml` com `project.context_file_max_kb: 100`; `sdd/fixtures/hooks/` (5: `config-placeholder.json`, `payload-write-build-report.json`, `payload-edit-build-report.json`, `payload-agent-veredito.json`, `settings-com-outros-hooks.json`); fixtures de CPF/CNPJ e credencial montadas em execução (o G1 do gate varre `tests/`).
- **Testes:** `tests/test_hooks.py` (23, novo), `tests/test_claude_adapter.py` (11, novo), `tests/test_sdd_open.py` (+ classe `Hooks`, 31), `tests/test_alarme.py` (36: `TestCopiaGerada` reescrita para o modo hooks, `TestModoHooks` nova, 28 intactos), `test_docs.py`, `test_bash32.py` (cobre `sdd/hooks/`), `test_agnostico.py`, `test_release_workflow.py`. `MANIFEST.txt` 221 → 234. **683 testes** no piso.
- **Docs e CI:** `docs/hooks.md` + `docs/pt-BR/hooks.md` (o que cada regra confere, o limite do `--no-verify`, a verdade continua no `report-lint` da release e no CI), links nos READMEs, roadmap EN/PT sem a linha "Hooks" (6 linhas), `docs/cli-conventions.md` (`COMMIT RECUSADO` e os exits dos hooks), célula da higiene no guia do aluno; `.github/workflows/release.yml` com `sdd/hooks/**` em `paths:` (entrou no manifest na revisão do DESIGN).
- **Evidência** em `sdd/reports/evidence/F8_HOOKS/`: `gerar-evidencia.sh` e `sabotagem.sh`; logs `GATE`, `baseline`, `baseline-ciclo1`, `baseline-ciclo2`, `bash32`, `check-versions`, `escopo`, `gitleaks-tests`, `init-em-projeto-real`, `linhas`, `sabotagem`, `shell-da-f8`, `shell-da-f8-pasta-inteira`, `skill-lint-conversa`, `testes-adaptador`, `testes-alarme`, `testes-hooks`, `testes-init`, `testes-lints-do-pacote`, `guard-antes-do-avaliador{,-design,-ciclo2}` e 108 `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "push sdd-open" (2026-10-31); push fast-forward `1d225e5..7c640eb`; runs `release` 41185402408 e `publish-gate` 41185402393 verdes → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.9, tag em `7c640eb`; SHA-256 de `sdd-open-v2.2.9.tar.gz` `b022f5529b9cac171cb38cef7d7277fd8e5e485a84d449e359b62ac07ae03f6b`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 683 OK em `7c640eb` (dentro do Verify Gate). A base `1d225e5` tinha 630.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F8_HOOKS.md` → 0 em `6a238d2`, `938ce47` e `7c640eb`. `check-versions --base v2.2.8 --base-obrigatoria` VERDE (só a `sdd-higiene-dado` subiu: 1.1.1 → 1.2.0). `skill-lint --conversa` 17/17.
- **Hooks de verdade:** num projeto temporário real, `init` + commit de controle passa em silêncio; as 5 fixtures H2–H6 são recusadas com a classe certa (`init-em-projeto-real.log`, `testes-hooks.log`); CPF/CNPJ com DV válido continua recusado pelo alarme chamado pelo dispatcher (`testes-alarme.log`); `gitleaks detect` em `tests/` e `sdd/fixtures/hooks/` sai 0 (`gitleaks-tests.log`).
- **Evidência:** `gate-shell-evidencia.sh sdd/reports/evidence/F8_HOOKS` → 0 acusações nos logs do build (`shell-da-f8.log`); a pasta inteira dá 62, todas em `AVAL*.log` (sondas dos avaliadores, não citadas como evidência; `shell-da-f8-pasta-inteira.log`, declarado).
- **Sabotagem:** 9/9 sobre `7c640eb` (uma por script alterado ou novo); baseline vermelha dos testes novos na `v2.2.8` (5 grupos), e dos testes de cada ciclo no commit anterior (7/7 e 3/3).
- **Conferência de fechamento** (inventário): o código roda (683 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0, `skill-lint --conversa` 17/17, 9 sabotagens, revisão sem HIGH aberto, `core.hooksPath` = `sdd/hooks` depois do `init`); as mudanças estão em `origin/main` e na tag `v2.2.9`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** o adaptador numa sessão real do Claude Code (só com os payloads das fixtures, pela linha de comando); os hooks no Windows (Git Bash) — o pacote só afirma o piso macOS/Ubuntu; o `OUTRO` com husky real (só com `core.hooksPath` apontando para outra pasta); as correções do ciclo 2 não passaram por um 3º avaliador (limite de 2 ciclos da `sdd-build`).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **F9 Fluxo encadeado** (sessão 7): `sdd/bin/sdd-fluxo.sh` com exits 0/10/20/30/**40 AGUARDANDO_HUMANO**/64, classes D1–D5 no item 9 reservado do `PERGUNTA_DECISAO.md` + `sdd/bin/sdd-decisoes-lint.sh`, `FLUXO_ENCADEADO.md`, seção "Encerramento" nas skills de fase; slots `flow.autonomous` e `review.security_globs` (D1, D11).
- **Hooks sem `sdd/config.yaml`:** o H2 usa o default 100 e o H6 não tem `default_branch` (pula) — este repositório mesmo não roda o `init` e fica sem hooks; aceito, porque o `init` é a porta de entrada do produto.
- **Sondas dos avaliadores:** os 62 `exit` de formatador em `AVAL*.log` mostram que os revisores ainda gravam `cmd | tail -1` como linha `$`; o brief do avaliador pode mandar seguir a receita do `EVIDENCIA.md`. Não é regra do pacote.
- **Riscos aceitos:** `git commit --no-verify` e `git cherry-pick` pulam o pre-commit — a verdade continua no `report-lint` da release e no CI (`docs/hooks.md`); o adaptador do Claude Code falha aberto (avisa, não nega) quando o `report-lint` não roda; H3 sem `gitleaks` instalado só tem a regex (placeholders passam, alta entropia sem chave conhecida passa); um teste do `doctor` commita `.p12` com `--no-verify` (drift 3); a `TestCopiaGerada` deixou de provar o arquivo em `.git/hooks/` da cópia gerada (passou a provar o modo hooks).
- **Pendências herdadas:** `test-baseline.sh` com formatos além de 5 saem 3 e `--touched` só filtra por id com nome de arquivo (F7); `gate-shell-evidencia.sh` conservador com comando composto (F7); `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10); o sdd-starter como distribuição gerada do open (Decisão 5) segue em frente própria; o `handoff-lint.py` do open reprova este handoff pelo molde (registrado em 2026-10-30).

### Próximos passos

1. **Sessão 7 — F9 Fluxo encadeado** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f9-fluxo` (branch `feat/f9-fluxo`, de `origin/main` = `7c640eb`, com os artefatos SDD copiados). Pronto quando (plano, quadro F9): `sdd-decisoes-lint.sh --sites .agents/skills` → 0; `sdd-fluxo.sh --self-test` → 0 com um cenário por exit e um que rejeita `| tee`; com `flow.autonomous: true`, a `sdd-define` sobre `sdd/fixtures/BRAINSTORM_EXEMPLO.md` termina com `✅ DEFINE pronto → seguindo para …`; no Codex CLI, um despacho de papel fresco para em `40 AGUARDANDO_HUMANO` com o brief gravado; Release publicada com o hash conferido.
2. **F10/F11 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **Hooks:** `sdd/hooks/pre-commit` recusa com `RESULTADO: COMMIT RECUSADO` e um `→ [classe]` por conserto; a regra REPORT **pula `sdd/fixtures/` e `sdd/templates/`** (o `init` copia os dois para o projeto; sem a exceção o 1º commit depois do `init` é recusado); o `pre-push` **nunca** recusa. `tests/test_hooks.py` (23) é o contrato; toda regra nova tem fixture e teste dos dois lados e passa em `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` (bash 3.2: nome da variável entre chaves antes de emoji).
- **`sdd-higiene-dado` em modo hooks:** `alarme.sh` e `pre-commit.sh` resolvem o arquivo antigo por `git rev-parse --git-common-dir`, nunca por `--git-path hooks/…` (segue o `core.hooksPath` e apontaria para o dispatcher); `desinstalar` nunca toca `sdd/hooks/pre-commit`; os 28 testes de `TestDeteccao`, `TestInstalacao` e `TestGeradores` ficam byte a byte.
- **`init`/`doctor`:** `OUTRO` (husky, lefthook, outro hooksPath) avisa e não mexe; o `init` nunca sobrescreve `.claude/settings.json` com forma inválida (exit 66) e exige `python3` para o merge (64); `sync` regenera `.claude/hooks/*.py` e o merge, não os hooks de git.
- **Padrão agnóstico (P2):** `PreToolUse`, `Agent|Task` e `MultiEdit` moram **só** em `bin/adapters/claude/` e no que o `init --vendors claude` gera; `tests/test_agnostico.py` varre também `sdd/hooks/`.
- **Neste repositório** o `init` não roda (sem `sdd/config.yaml`): `core.hooksPath` fica vazio e os commits da worktree não passam pelo dispatcher — o `publish-gate.sh` e o CI continuam sendo a verdade; o `report-lint` do `BUILD_REPORT` roda à mão na release.
- **Docs testados:** o roadmap conta 6 linhas (`tests/test_docs.py`); a linha da F9 é a próxima a sair.
- Demais alertas das etapas F7, F6, F5, F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `7c640eb` = tag `v2.2.9`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.9.
- Worktree da sessão 6: `/Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks`. A branch `feat/f8-hooks` está em `7c640eb`, já mesclada. A worktree de revisão `sdd-open-f8-aval` já foi removida; as da sessão 4 e 5 (`sdd-open-f6-docs`, `sdd-open-f7-evidencia`) também já não existem.
- O checkout principal `/Users/robertoduarte/rdd-public/sdd-open` está em `1c9bbc7` (`main` local atrás de `origin/main`); a worktree da F9 nasce de `origin/main` depois de `git fetch`, não da `main` local.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f8-hooks`.

---

## 2026-10-30 — F7 Evidência (entregue, Release v2.2.8)

### O que foi feito

- **Fluxo SDD completo** (sessão 5, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia`, branch `feat/f7-evidencia`):
  - artefatos: `sdd/features/BRAINSTORM_F7_EVIDENCIA.md`, `DEFINE_F7_EVIDENCIA.md` (v1.5, 30 ATs EARS, Clarity 14/15), `DESIGN_F7_EVIDENCIA.md` (v1.3, 8 decisões, 38 linhas no manifest), `sdd/reviews/UX_REVIEW_F7_EVIDENCIA.md` (8 MUST de texto de saída) e `sdd/reports/BUILD_REPORT_F7_EVIDENCIA.md` (`report-lint` 0 com as regras novas, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F7_EVIDENCIA_20261030.md` (NEEDS_WORK, 2 HIGH, 4 MEDIUM, 8 LOW, aplicadas antes do build), `AVALIACAO_F7_EVIDENCIA_20261030-ciclo1.md` (NEEDS_WORK, 3 MEDIUM, 6 LOW, sobre `514324f`) e `…-ciclo2.md` (NEEDS_WORK, 3 MEDIUM, 3 LOW, sobre `bed1f69`), todos aplicados;
  - commits `514324f` (build), `bed1f69` (ciclo 1) e `1d225e5` (ciclo 2), sobre `1c9bbc7`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/9 (MERGED); 39 arquivos (25 novos, 14 alterados).
- **`sdd/bin/report-lint.py`** (323 → 625 linhas): tabela de critérios reconhecida obrigatória (também `Result | Evidence`); **avaliação ausente reprova** (sem `AVALIACAO_<F>_<AAAAMMDD>…md` não vazio e não ignorado em `sdd/reviews/` e sem `avaliador: N.A. (<motivo>)`/`PENDENTE (<motivo>)`); `N.A.` reprova com ≥ N camadas do File Manifest em `layers:` (contagem impossível aceita com ⚠️); declaração sem motivo reprova; `PENDENTE` passa com ⚠️ e `--pendente` sai 1; `git check-ignore` em cada evidência; veredito em linha, título, parágrafo seguinte ou **linha** de tabela, fora de bloco cercado, com ou sem `(C1)`; `--stdin <caminho>` (para o adaptador da F8); classe por violação e uma linha `→` por classe. As 32 regras anteriores continuam.
- **`sdd/bin/verify-gate.sh`**: trace JSONL por execução em `${SDD_TRACE_DIR:-sdd/traces}/<F>.jsonl` (exit original, antes do `--strict`; `SDD_TRACE=off`; sem permissão não muda nada), `--trace` aceito, `--sem-define <F>` (diz se gravou). Saída idêntica à da `v2.2.7` nas 4 fixtures. **P1:** o DEFINE agora é lido pelo caminho absoluto (de uma subpasta o gate não achava o arquivo).
- **4 scripts novos em `sdd/bin/`** (bash 3.2, sem arrays):
  - `gate-baseline.sh <DEFINE> [--base] [--feature] [--sobrepor <caminho>]…`: exige vermelho **avaliando** na base (`🔴` ou marcador de asserção dos 5 formatos), 0/2/3/64, `BASELINE-gate.log`;
  - `gate-shell-evidencia.sh [--base] [<log|pasta>…]`: acusa exit de formatador (`|`, `|&`, `VAR=x`, `command`, `(`), `[exit=]`/`exit=` vazio e `$?` literal; modo diff com staged, modificados e não rastreados; `LC_ALL=C`;
  - `avaliador-guard.sh [--root] [--permitir <prefixo>]…`: permite `sdd/reports/evidence/` e `sdd/traces/`; 0/1/2/64; sugere o commit com só os caminhos que o git reconhece;
  - `test-baseline.sh [--cmd] [--touched [--base]] [--aceitar <id>]`: unittest, pytest, jest, vitest, go (inclusive `[build failed]` e pacote que falha sem `--- FAIL`), deno (cores ANSI removidas); `sdd/baselines/tests.txt`; poda só na execução completa; 0/2/3/64 e `PULADO`.
- **Skills:** `sdd-build` 2.3.0 (passo 1 com a flag `LLM Prompts`, guard no 1.5 e no 5d, `gate-baseline` quando o build corrige a asserção, `test-baseline` no 5b, linha do avaliador e fragmento LLM no 6, 5 "por quê" novos); `sdd-release` 2.4.0 (0a: `--sem-define`, `--pendente` e `gate-shell-evidencia` com "exit ≠ 0 aborta", 64/127 manda atualizar `sdd/bin/`; 3 "por quê" novos; bloco do OK intacto).
- **Templates e config:** `EVIDENCIA.md` (receita com `rc=$?` antes do pipe e `[exit=$rc]`, "A linha do avaliador", forma mínima, o que o lint nega, classes); `BUILD_REPORT_TEMPLATE.md` (`PENDENTE`, `layers:`); `fragments/LLM_PROMPTS_BUILD_REPORT.md` (novo, 5 partes); `config.example.yaml` com `evidence.require_avaliacao_layers: 2`.
- **Fixtures** em `sdd/fixtures/evidencia/` (13, escritas do zero com os casos dos testes do privado) e **7 testes novos** (`test_report_lint_evidencia`, `test_verify_gate_trace`, `test_gate_baseline`, `test_gate_shell_evidencia`, `test_avaliador_guard`, `test_test_baseline`, `test_bash32`). `MANIFEST.txt` +25.
- **Docs:** roadmap EN/PT com a linha "Hooks" (7 linhas); `docs/cli-conventions.md` com os exits e as palavras de `RESULTADO:` dos 4 scripts (fora do manifest, drift registrado).
- **Evidência** em `sdd/reports/evidence/F7_EVIDENCIA/`: `gerar-evidencia.sh` e `sabotagem.sh`; logs `GATE`, `relatorios-do-open`, `corpus-shell`, `corpus-shell-diff` (+ `corpus-esperado.txt`), `saidas-v2.2.7`, `check-versions`, `skill-lint-conversa`, `bash32`, `linhas`, `escopo`, `contratos-report-lint`, `baseline`, `baseline-ciclo1`, `baseline-ciclo2`, `shell-da-f7`, `sabotagem`, `testes-f7`, `testes-scripts-novos`, `testes-contratos`, `guard-antes-do-avaliador`, `ci-pr`, `release`, e os `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "finalizar (push + deploy + verificar) do sdd-open" (2026-10-30); push fast-forward `1c9bbc7..1d225e5`; run `release` 41133637690 e `publish-gate` 41133637778 verdes → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.8, tag em `1d225e5`; SHA-256 de `sdd-open-v2.2.8.tar.gz` `1fdf742b3068edf2a55526b6734b92251099d81095a627c284e67846464947de`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 630 OK em `1d225e5` (dentro do Verify Gate). A base `1c9bbc7` tinha 514.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F7_EVIDENCIA.md` → 0 em `514324f` (619), `bed1f69` (625) e `1d225e5` (630). `check-versions --base v2.2.7 --base-obrigatoria` VERDE. `skill-lint --conversa` 17/17; maior `SKILL.md` tocado 309 linhas.
- **Conferência de verdade:** nos 8 `BUILD_REPORT` do open, F1, F2, F3, M1 e W0 reprovam só por "avaliação ausente" e F4, F5, F6 passam (`relatorios-do-open.log`); nos 245 logs de evidência do open (sem `F7_EVIDENCIA/`), o `gate-shell-evidencia.sh` faz exatamente as 22 acusações de `corpus-esperado.txt` (19 de formatador, das quais ~8 são falsos positivos conservadores de comando composto, e 3 `exit=` vazios gravados pelo zsh).
- **Sabotagem:** 6/6 sobre `1d225e5` (uma por script alterado ou novo); baseline vermelha dos testes novos na `v2.2.7` e dos testes de cada ciclo no commit anterior.
- **Conferência de fechamento** (inventário): o código roda (630 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0 com as regras novas, `skill-lint --conversa` 17/17, 6 sabotagens, revisão sem HIGH aberto); as mudanças estão em `origin/main` e na tag `v2.2.8`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** o `test-baseline.sh` contra saídas reais de jest, vitest e pytest (só fixtures; unittest 3.9/3.13 e deno 2 reais foram conferidos pelos avaliadores); as correções do ciclo 2 não passaram por um 3º avaliador (decisão do Roberto); o fluxo num projeto real de usuário com `layers:` preenchido.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Adaptador do Claude Code da E6 → F8** (decisão do Roberto): `.claude/settings.json` gerado pelo `init --vendors claude` com PreToolUse em Write/Edit (simula o conteúdo final do Edit e chama `report-lint.py --stdin <caminho>`) e no despacho do avaliador (`avaliador-guard.sh`); falha aberta, mas avisa. Registrado no quadro F8 do plano.
- **Pre-commit chamando o `report-lint`** e os hooks de git (F8).
- **`test-baseline.sh`:** formatos além de 5 (rspec, phpunit, cargo) saem 3; `--touched` só filtra quando o id cita o arquivo de teste (go e jest não citam).
- **`gate-shell-evidencia.sh`:** conservador com comando composto (`… | tail -1 && outro`, `for … done`, `diff <(… | sort)`); ~8 dos 22 do corpus são desse tipo — o conserto é o mesmo (gravar o `rc` do que importa).
- **Riscos aceitos:** sem data de corte para relatório antigo — um `BUILD_REPORT` anterior sem a linha do avaliador reprova ao ser relintado (as notas da `v2.2.8` e o `EVIDENCIA.md` dizem o que acrescentar); o `doctor` não avisa script **novo** de `sdd/bin/` ausente numa instalação antiga (só o que difere) — a `sdd-build` manda rodar o `init`, que completa o que falta (F8 mexe no `doctor`).
- **Pendência herdada:** `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10); o sdd-starter como distribuição gerada do open (Decisão 5) segue em frente própria.

### Próximos passos

1. **Sessão 6 — F8 Hooks** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f8-hooks` (branch `feat/f8-hooks`, de `origin/main` = `1d225e5`, com os artefatos SDD copiados). Pronto quando: depois do `init`, `git config core.hooksPath` = `sdd/hooks`; o pre-commit bloqueia as 5 fixtures (H2–H6) e deixa passar o controle; o alarme da `sdd-higiene-dado` continua bloqueando CPF/CNPJ com DV válido; o `init --vendors claude` gera o adaptador da E6; Release publicada com o hash conferido.
2. **F9 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **`report-lint.py` agora é fail-closed:** todo `BUILD_REPORT` precisa da tabela reconhecida e da linha do avaliador (ou um `AVALIACAO_<F>_<AAAAMMDD>…md` em `sdd/reviews/`). Os testes `test_report_lint_evidencia` e o `relatorios-do-open.log` são o contrato.
- **Neste repositório, rode o `gate-shell-evidencia.sh` com o caminho da frente** (`sdd/reports/evidence/<F>`): a evidência das frentes anteriores fica não rastreada aqui e tem as 22 acusações conhecidas; o modo diff (sem argumentos) veria todas.
- **`avaliador-guard.sh` neste repositório:** use `--permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/`, nunca `--permitir sdd/` (liberaria `sdd/bin/`, `sdd/templates/`, `sdd/fixtures/`).
- **`sdd/traces/`** é criado em cada execução do gate na raiz e **nunca** entra em commit da branch de trabalho (como `sdd/features|handoffs|reports|reviews/`).
- **Logs de evidência:** gravar com `out=$(cmd 2>&1); rc=$?` e `[exit=$rc]`, sem formatador no último estágio do `$` — a própria F7 confere (`shell-da-f7.log`).
- Demais alertas das etapas F6, F5, F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `1d225e5` = tag `v2.2.8`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.8.
- Worktree da sessão 5: `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia`. A branch `feat/f7-evidencia` está em `1d225e5`, já mesclada. As worktrees de revisão `sdd-open-f7-aval` e `sdd-open-f7-aval2` já foram removidas.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f7-evidencia`. Resta também a worktree da sessão 4, `sdd-open-f6-docs` (já mesclada), e a antiga `sdd-open-incorporar-starter`, que não deve ser usada.

---

## 2026-10-30 — F6 Docs (entregue, Release v2.2.7)

### O que foi feito

- **Fluxo SDD completo** (sessão 4, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`, branch `feat/f6-docs`):
  - artefatos: `sdd/features/BRAINSTORM_F6_DOCS.md`, `DEFINE_F6_DOCS.md` (v1.1, 14 ATs EARS, Clarity 14/15), `DESIGN_F6_DOCS.md` (v1.1, 8 decisões, 26 linhas no manifest) e `sdd/reports/BUILD_REPORT_F6_DOCS.md` (`report-lint` 0, `validate_build_report` PASS);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F6_DOCS_20261029.md` (NEEDS_WORK, 3 HIGH, 4 MEDIUM, 3 LOW, aplicadas antes do build), `AVALIACAO_F6_DOCS_20261029-ciclo1.md` (NEEDS_WORK, 3 HIGH, 3 MEDIUM, 6 LOW, sobre `963c47e`) e `…-ciclo2.md` (**PASS**, 6 LOW, sobre `aaae1b4`);
  - commits `963c47e` (build), `aaae1b4` (ciclo 1) e `1c9bbc7` (ciclo 2), sobre `7e19462`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/8 (MERGED); 23 arquivos (4 novos, 19 alterados, +1394/−41).
- **`docs/pt-BR/guia-do-aluno.md`** (novo, ~690 linhas, só em português, decisão do Roberto): adaptado do guia do starter (`/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md`, não rastreado lá, só lido). 10 blocos, 17 fichas de skill, 7 agentes, `init --vendors … --dry-run` e `--yes`, `git init -b main`, caminho de atualização (`doctor` → apagar a skill ou o arquivo de `sdd/bin` não editado → `init --yes` → `sync --yes`), tabela dos exits do Verify Gate, glossário, FAQ do starter instalado global (o `doctor` não o vê).
- **`docs/roadmap.md` e `docs/pt-BR/roadmap.md`** (novos): 7 temas, 6 *planned*/planejado e "Specs as deltas"/"Specs como deltas" *under evaluation*/em avaliação, sem datas. O `comparison` (EN/PT) aponta para eles.
- **Quickstarts (EN/PT)**: passo 4 com a regra do método, 4 linhas "Validate before moving on:"/"Valide antes de seguir:", a tabela "Você quer… / Escreva no Design / No Build" e os 7 agentes; passo 5 corrigido (P1: `git pull` + `sync` não atualizava skill); "Coming from sdd-starter" diz que o `doctor` não vê instalação global.
- **`adaptation-guide` (EN/PT)**: P1 — 2 links quebrados e a frase de que um script de landmines vinha no pacote (o slot `release.landmines_cmd` sai vazio).
- **READMEs**: seção "As 17 skills"/"The 17 skills", linha da base de conhecimento, "um OK só", "prepare uma vez" + `sdd-new-session` por frente, links do roadmap e do guia.
- **`AGENTS.md.tmpl`**: linha "Antes" (4 skills de preparo), linha "KB" (`sdd-kb`), fase 1 cita `sdd/bin/kb-dominios.py`, regra 7 "**Publicar pede um OK só.**"; o marcador da lista de agentes que o `init` preenche ficou intacto.
- **"Por que cada regra existe"** nas 7 skills de fase, logo antes de `## Encerramento (obrigatório)`, passos intactos (`comandos-intactos.py`: extração + texto normalizado). Versões: brainstorm 2.1.1, define 2.3.1, governanca 2.2.1, ux-review 2.3.1, design 2.1.1, build 2.2.1, release 2.3.1.
- **`tests/test_docs.py`** (novo, 15 métodos): links relativos com âncora (regra do GitHub por `unicodedata`, caixa exata por `os.listdir`), guia (blocos, fichas, agentes, frases proibidas como "registra e libera"), quickstart, roadmap, `comparison` (só a célula do SDD Open), README e `AGENTS.md.tmpl`, seções "Por que". `MANIFEST.txt` +4.
- **Evidência** em `sdd/reports/evidence/F6_DOCS/`: scripts `gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`, `baseline-notas2.py`, `links-pr.sh`; logs `GATE`, `check-versions`, `comandos-intactos`, `contratos-intactos`, `codepoints`, `skill-lint-conversa`, `linhas`, `escopo`, `testes-f6`, `baseline`, `baseline-notas`, `baseline-notas2`, `sabotagem`, `links-pr`, `ci-pr`, `release`, e os `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "Push sdd-open autorizado" (2026-10-30); push fast-forward `7e19462..1c9bbc7`; run `release` 41025735985 (testes, testes no piso macOS, publicar) e `publish-gate` 41025736350 verdes → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.7, tag em `1c9bbc7`; SHA-256 de `sdd-open-v2.2.7.tar.gz` `6a3eaea3c996301af6c289d32fe88a1f49df65bd8c4b57eaf4b31c92b45ebb59`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 514 OK em `1c9bbc7` (dentro do Verify Gate). A base `7e19462` tinha 499.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F6_DOCS.md` → 0 em `963c47e`, `aaae1b4` e `1c9bbc7`. `check-versions --base v2.2.6 --base-obrigatoria` VERDE. `skill-lint --conversa` 17/17; maior `SKILL.md` com 376 linhas.
- **Âncoras no GitHub (A-002):** os 43 títulos do guia têm, na página renderizada da branch do PR, a mesma âncora que o `ancora()` do teste gera; as 10 do sumário abrem (`links-pr.log`).
- **Sabotagem:** 4/4 (link do sumário para âncora inexistente, seção "Por que" apagada da `sdd-build`, "Specs como deltas" ✅ na coluna do open, 1 palavra mudada no Quality Gate da `sdd-build` contra o `comandos-intactos.py`).
- **Conferência de fechamento** (inventário): o código roda (514 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0, `skill-lint --conversa` 17/17, ≤ 500 linhas por `SKILL.md`, teste de links, 1 sabotagem por script, revisão sem HIGH aberto); as mudanças estão em `origin/main` e na tag `v2.2.7`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** um aluno real seguindo o guia do zero num dos 7 agentes; os testes conferem só texto, links e âncoras.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência com um aluno real** (ou num agente, do zero): guia + quickstart num projeto vazio, até o primeiro Verify Gate verde. Junta-se às conferências pendentes da F4 (A-002) e da F5.
- **Roadmap a manter:** cada frente que entrega um tema tira a linha de `docs/roadmap.md` e `docs/pt-BR/roadmap.md` (a regra está no próprio texto: "A theme leaves this page when it ships"). A linha "Hooks and evidence" cobre F7 **e** F8: a F7 reescreve a linha só com o que falta (hooks), a F8 a remove. O `test_docs.Roadmap` conta 7 linhas: atualizar a contagem junto.
- **Guia do aluno só em português** (decisão do Roberto): o README em inglês aponta para ele como "Portuguese only".
- **Risco aceito:** o regex `FORA_DO_GIT` do `test_docs.py` tem autoteste com 7 redações de "a pasta sdd fica fora do git"; uma redação nova no guia pode precisar de mais uma alternativa.
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (**F7**, próxima); `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10); o sdd-starter como distribuição gerada do open (Decisão 5) é frente própria, agora desbloqueada.

### Próximos passos

1. **Sessão 5 — F7 Evidência** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f7-evidencia` (branch `feat/f7-evidencia`, de `origin/main` = `1c9bbc7`, com os artefatos SDD copiados). Pronto quando: `report-lint.py` reprova as fixtures `BUILD_REPORT_sem_avaliacao`, `…_pendente` e `…_evidencia_ignorada`; `gate-shell-evidencia.sh` acusa `| tail` sem `rc=$?`; `verify-gate.sh --trace` grava 1 linha JSONL por execução; Release publicada com o hash conferido.
2. **F8 → F14** e **F15** (plano, seções 8 e 10); a frente do sdd-starter gerado (Decisão 5) entra quando o Roberto quiser.

### Alertas — o que não quebrar

- **Os docs agora são contrato testado** (`tests/test_docs.py`): todo link relativo e âncora de `README*.md` e `docs/**` tem de abrir; renomear um título do guia quebra o sumário. O roadmap conta 7 linhas e "Specs como deltas" tem de ficar fora do ✅ na coluna do open.
- **"Por que cada regra existe"** nas 7 skills de fase fica logo antes de `## Encerramento (obrigatório)`; o `PorQueCadaRegra` confere a posição. Skill nova de fase precisa da seção.
- **`AGENTS.md.tmpl`**: rótulos "Antes", "KB" e a regra 7 estão testados (`ReadmeEAgents`).
- **Evidência:** `report-lint` só aceita `evidence/<FEATURE>/` com o nome exato do relatório.
- Demais alertas das etapas F5, F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `1c9bbc7` = tag `v2.2.7`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.7.
- Worktree da sessão 4: `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs`. A branch `feat/f6-docs` está em `1c9bbc7`, já mesclada. A worktree de revisão `sdd-open-f6-aval` já foi removida.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f6-docs`. As worktrees das sessões 1–3 já não existem; resta a antiga `sdd-open-incorporar-starter`, que não deve ser usada.

---

## 2026-10-29 — F5 Conhecimento (entregue, Release v2.2.6)

### O que foi feito

- **Fluxo SDD completo** (sessão 3, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento`, branch `feat/f5-conhecimento`):
  - artefatos: `sdd/features/BRAINSTORM_F5_CONHECIMENTO.md`, `DEFINE_F5_CONHECIMENTO.md` (v1.4, 17 ATs EARS, Clarity 14/15), `DESIGN_F5_CONHECIMENTO.md` (v1.4, 9 decisões, 25 linhas no manifest), `sdd/reviews/UX_REVIEW_F5_CONHECIMENTO.md` e `sdd/reports/BUILD_REPORT_F5_CONHECIMENTO.md` (`report-lint` 0);
  - revisões: `sdd/reviews/REVISAO_DESIGN_F5_CONHECIMENTO_20261029.md`, `AVALIACAO_F5_CONHECIMENTO_20261029-ciclo1.md` e `…-ciclo2.md`;
  - commits `bafc63c` (build), `7e5b25c` (teste achado pela sabotagem), `0e0dba5` (ciclo 1) e `7e19462` (ciclo 2), sobre `2fcdda1`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/7 (MERGED); 50 arquivos (42 novos e 8 alterados).
- **`.agents/skills/sdd-kb/` 2.2.0** (36 arquivos), portada de `sdd-starter/skills/sdd-kb` 2.1.0 (`17c69c4`):
  - sem `agents/openai.yaml`, sem `tests/` dentro e sem citar o starter (`PORTADAS` + `sdd-kb`);
  - KB em `sdd/kb/_index.yaml` + `sdd/kb/<slug>/`; todo comando e molde citado por `.agents/skills/sdd-kb/…`;
  - camada da F4 com o bloco comum idêntico ao das 14 (agora são 15 com o bloco); `como-falar.md` com a pergunta do perfil (**não** recomendado);
  - `validate_kb.py`: mensagens do starter em inglês, exits 0/2/64; `--strict` reprova `implementacao` sem `teste`, `teste` de arquivo ausente e `teste` fora da raiz (a pasta acima de `sdd/kb/`; contenção pela forma do caminho, então link simbólico dentro do projeto passa); `sys.dont_write_bytecode`;
  - `gate.sh` reescrito (bash 3.2): monta 16 casos em `mktemp -d` a partir dos exemplos (4 aceitas, 12 rejeitadas com a razão conferida), confere o RULE_MAP do exemplo antes dos casos, diferencia `kb_normativo.py` quebrado, recusa rodar de uma cópia com `sdd-open:generated`; saída `RESULTADO: VERDE — 4 aceitas, 12 rejeitadas pelo motivo certo, RULE_MAP do exemplo em dia`.
- **`sdd/bin/kb-dominios.py`** (0/1/64): lê a linha `| **KB Domains** |` do `## Technical Context`; `nenhum` sozinho ou nomes de pasta de `sdd/kb/` (sem ocultas); vermelho com `🛑` por problema, os nomes que existem (até 10 + "e mais N"), `RESULTADO:` e `→`; verde lista `<domínio>: <REGRA> → <teste>` dos RULE_MAP (pipe escapado tratado). Não importa a `sdd-kb`.
- **`sdd-define` 2.3.0**: frase no passo 3 (KB Domains de `ls sdd/kb/` ou `nenhum`, estado vazio em 1 frase, `name:` ao lado do slug), `### 10. Conferir o KB Domains` em prosa (sem bloco cercado), linha no Quality Gate; `DEFINE_TEMPLATE.md` sem "ou equivalente".
- **`sdd-ux-review` 2.3.0**: 1 frase no passo 1 e `references/entrevista-publico.md` (público, frequência e aparelho, estágio, referência e URL como perguntas abertas; catálogo com "Uma referência sua"; Observado × Desejado × Recomendado; só a confirmação "Posso gravar este público em User and Context?" tem opções). O `UX_REVIEW_TEMPLATE.md` não mudou; a tabela WCAG fica para a W5 (anotado no DESIGN, Decision 6).
- **Testes**: `tests/test_sdd_kb_normativo.py` (62, porte com `-B`), `test_sdd_kb.py` (21), `test_kb_dominios.py` (22), `test_conversa.py` (+6: `EntrevistaPublico`, 17 skills); `test_skill_lint.py` 16 → 17; `test_matriz_new_session.PORTADAS` + `sdd-kb`. `docs/cli-conventions.md` com as saídas novas e a exceção do `validate_kb.py`. `MANIFEST.txt` +42. `.gitattributes` novo.
- **Evidência** em `sdd/reports/evidence/F5_CONHECIMENTO/`: scripts `gerar-evidencia.sh`, `sabotagem.sh`, `comandos-intactos.py`; logs `GATE`, `base-2fcdda1`, `baseline`, `baseline-notas`, `baseline-notas2`, `check-versions`, `comandos-intactos`, `contratos-intactos`, `codepoints`, `gate-kb`, `skill-lint-conversa`, `kb-dominios-proprio`, `testes-f5`, `sabotagem`, `escopo`, `linhas`, `ci-pr`, `release`, e os `AVAL-DESIGN-*`, `AVAL-*` e `AVAL2-*` dos revisores.
- **Release**: OK "release do sdd-open autorizado"; push fast-forward `2fcdda1..7e19462`; run `release` 40970012304 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6, tag em `7e19462`; SHA-256 de `sdd-open-v2.2.6.tar.gz` `5dedf04b5046574c44664f3e1daa72af5877859ebb7bba35da58cab0e842a114`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 499 OK em `7e19462` (dentro do Verify Gate, 259 s). A base `2fcdda1` tinha 388.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F5_CONHECIMENTO.md` → 0 em `bafc63c`, `0e0dba5` e `7e19462`. `check-versions --base v2.2.5 --base-obrigatoria` VERDE (17 skills).
- **Baseline vermelha:** 33 FAIL + 74 ERROR em 152 testes antes do código; 9 FAIL das notas do ciclo 1 contra `7e5b25c`; 4 FAIL das notas do ciclo 2 contra `0e0dba5`.
- **Sabotagem:** 4/4 (validador sem a regra de `teste`, `rule-map --check` permissivo, `gate.sh` que aceita caso ruim, `kb-dominios.py` que aceita nome sem pasta) vermelhas com o nome do teste e verdes depois do `git checkout`.
- **Conferência de fechamento** (inventário): o código roda (499 no piso e no CI ubuntu + macOS); os critérios combinados passam (gate 0, `report-lint` 0, `skill-lint --conversa` 17/17, gate da KB, 1 sabotagem por script, revisão sem HIGH aberto); as mudanças estão em `origin/main` e na tag `v2.2.6`, e os artefatos SDD na branch `docs/incorporar-starter`; o que ficou de fora está nas pendências.
- **Não verificado:** um agente real conduzindo a `sdd-kb`, a entrevista de público e o passo 10 da `sdd-define`. Os testes conferem só o texto e os scripts.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência num agente real** (Codex CLI e Claude Code): `sdd-kb` num projeto vazio (cria `sdd/kb/`, roda o validador, traduz a saída), `sdd-define` com e sem `sdd/kb/` (passo 10), `sdd-ux-review` com DEFINE sem público (entrevista). Junta-se à pendência A-002 da F4.
- **README e `AGENTS.md.tmpl` não citam a `sdd-kb`** nem o `kb-dominios.py`: entra na F6 (plano 4.3), junto com as 3 skills da F2.
- **Risco aceito:** as mensagens do `validate_kb.py` e do `kb_normativo.py` ficam em inglês (`PASS:`/`FAIL:`/`WARN:`, exit 2): os 62 testes portados conferem o texto; a skill manda traduzir. Registrado em `docs/cli-conventions.md`.
- **Risco aceito:** o `kb-dominios.py` não exige o domínio registrado no `_index.yaml` (isso é do `validate_kb.py`) nem julga se o domínio é relevante para a feature.
- **Risco aceito:** DEFINE antigo com `KB Domains = N/A` reprova se alguém rodar o lint nele; a `sdd-define` só o roda no DEFINE que acabou de gravar.
- **Risco aceito:** o `.gitattributes` com `-text` só cobre `example-kb-normativo/fontes/` (o único lugar onde o byte importa: SHA-256).
- **Para a F9:** o bloco comum da camada está em **15** `SKILL.md` (as 14 da F4 + `sdd-kb`); trocar nas 15 e nas `FRASES` do `test_conversa`. A substituição em massa continua excluindo `sdd-iniciar-repo` e `sdd-higiene-dado`.
- **Para a W5 (item H):** a tabela WCAG 2.2 AA no `UX_REVIEW_TEMPLATE.md` e a leitura de `UX_REVIEW_*.md` anteriores.
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (F7); `RESUMO_ETAPA.md:4,49` cita `/adversarial-review` (F10).

### Próximos passos

1. **Sessão 4 — F6 Docs** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), na worktree já aberta `/Users/robertoduarte/rdd-worktrees/sdd-open-f6-docs` (branch `feat/f6-docs`, de `origin/main` = `7e19462`, com os artefatos SDD copiados). Pronto quando: `BRAINSTORM_F6_*.md` gravado; define, design, build e Release (ou push sem Release, se a F6 só tocar `docs/` e `README.md`) com o hash conferido quando houver Release.
2. **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **A `sdd-kb` agora é contrato testado:** `gate.sh` (4/12, linha única no verde), `TextoDaSkill` (nenhum caminho de fora, nenhum `scripts/validate_kb.py` sem `.agents/skills/sdd-kb/`, nenhum link relativo `](assets/`), `PORTADAS`, `EntrevistaPublico` (1 pergunta de decisão só). Mexer no exemplo normativo exige regerar o RULE_MAP e conferir as âncoras do `gate.sh`.
- **O `kb-dominios.py` lê só o `## Technical Context`**: renomear essa seção no `DEFINE_TEMPLATE.md` quebra o passo 10.
- **17 skills**: `test_skill_lint` e `test_conversa` contam; a F13 e a F14 sobem para 18 e 19 de propósito.
- **Evidência:** `report-lint` só aceita `evidence/<FEATURE>/` com o nome exato do relatório.
- Demais alertas das etapas F4, M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `7e19462` = tag `v2.2.6`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.6.
- Worktree da sessão 3: `/Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento`. A branch `feat/f5-conhecimento` está em `7e19462`, já mesclada.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f5-conhecimento && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f5-conhecimento`.

---

## 2026-10-29 — F4 Conversa (entregue, Release v2.2.5)

### O que foi feito

- **Fluxo SDD completo** (sessão 2, worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa`, branch `feat/f4-conversa`):
  - artefatos: `sdd/features/BRAINSTORM_F4_CONVERSA.md`, `DEFINE_F4_CONVERSA.md` (v1.2, 22 ATs EARS, Clarity 14/15), `DESIGN_F4_CONVERSA.md` (v1.1, 10 decisões, 36 linhas no manifest) e `sdd/reports/BUILD_REPORT_F4_CONVERSA.md` (`report-lint` 0);
  - commits `4e77a1f` (build), `fd94876` (ciclo 1) e `2fcdda1` (ciclo 2), sobre `dd27ef6`;
  - PR https://github.com/robertodiasduarte/sdd-open/pull/6 (MERGED); 62 arquivos (35 novos e 27 alterados).
- **As 14 skills** (bump minor): auditoria-harness 1.1.0, brainstorm 2.1.0, build 2.2.0, checar-ambiente 1.4.0, define 2.2.0, design 2.1.0, governanca 2.2.0, handoff 2.1.0, iterate 2.1.0, new-session 1.2.0, playbook 2.1.0, prompt-builder 2.1.0, release 2.3.0, ux-review 2.2.0. Cada uma tem:
  - a seção `## Como falar com o aluno`, logo antes do 1º `## `. Ela traz 3 linhas de abertura, a tabela `| Etapa | Nome para o aluno | Passos desta skill |` e o **bloco comum de regras**, igual nas 14: as 5 partes, o Status começando pelo nome da fase (`Build: ✅ 1 Plano · ▶️ 2 Modo · …`) e o Próximo passo ≤100 caracteres;
  - `references/como-falar.md`, com glossário, Status preenchido e ≥1 exemplo com decisão (recomendada primeiro, **não sei**, sem **Outro**);
  - a linha de identificação ("uma vez só, antes do Status") e `metadata.updated: "2026-10"`;
  - sai o `> Abra a resposta com o banner` das 9 que o tinham.

  Casos próprios:
  - `sdd-design` ganha o `### 8. Conferir`, com `design-lint`;
  - `sdd-handoff` ganha o `### 3b. Conferir a ficha`, com `handoff-lint`;
  - na `sdd-checar-ambiente`, o Status vem antes do relatório do script, e a identificação continua na linha ✅.
- **`sdd/templates/fragments/PERGUNTA_DECISAO.md`**: dono único do formato.
  - Pergunta: `(recomendado)` primeiro com o porquê, números, `(ref: …)`, **não sei**, nunca **Outro**, eco de 1 linha, `[Dn]` reservado.
  - Parada ⏸️: **Por que parei:**, **Onde:**, **Passos:**, **O que não foi feito:**, **Brief:** e **Sessão nova:** (que a F9 liga ao `exit 40`).
- **`sdd/bin/skill-lint.py --conversa`**: sem a flag, só frontmatter, com a mensagem da `v2.2.4`. Com a flag, confere:
  - a seção (fora de bloco de código), a coluna `Etapa`, as 5 partes e o `como-falar.md` quando a seção manda lê-lo;
  - em cada pergunta de decisão do `como-falar.md` (negrito com `?` + opções `-`/`*`, também depois de linha em branco, em citação ou quebradas em 2 linhas): exatamente 1 `(recomendado)`, e ela é a 1ª; **não sei**; nada que comece por Outro/Outra/Outros;
  - `**Próximo passo**` ≤100 caracteres.

  As 7 fixtures ficam em `sdd/fixtures/conversa/` (controle + 6 que reprovam). O CI (`publish-gate.yml`, passo "Skill frontmatter") roda com `--conversa`.
- **`sdd/bin/design-lint.py`** (0/1/64): `## Key Decisions` com `### Decision N: <nome>` em sequência; File Manifest com `**Total Files:**` = linhas; dependências que existem, sem autodependência e sem ciclo; placeholder entre chaves fora de código (aspas angulares passam). Arquivo ilegível sai 1 com `RESULTADO:`.
- **`sdd/bin/handoff-lint.py`** (0/1/64): confere o mínimo do `HANDOFF_TEMPLATE.md` do open:
  - `# HANDOFF:`;
  - Ficha com Objetivo, Status e Verify Gate;
  - `## Prompt de retomada` com bloco, delimitada sem os blocos (só a ficha cujo Status **começa** por ✅ dispensa o prompt);
  - `### … — AAAA-MM-DD` no histórico;
  - placeholder; frases que dependem da conversa anterior (a lista está na docstring do lint).

  Seção extra passa, e `## Eventos` é opcional.
- **`tests/test_agnostico.py`**: reprova `AskUserQuestion`, `TodoWrite`, `PreToolUse`, `PostToolUse`, `subagent_type`, `Task tool`/`Agent tool` (sem caixa) e `/model`.
  - Varre todo arquivo de texto de `.agents/skills/`, `sdd/templates/`, `AGENTS.md.tmpl` e `sdd/playbook.md`.
  - Texto não-UTF-8 é achado; binário é pulado.
  - `CLARIFY.md:45` e `BUILD_REPORT_TEMPLATE.md:75` foram reescritos.
- **Outros testes:**
  - novos: `tests/test_conversa.py` (identificação = versão nas 16, sem banner, bloco comum nas 14, fragmento, passos 8/3b), `test_design_lint.py` e `test_handoff_lint.py`;
  - `test_skill_lint.py`: 8 → 32 testes;
  - versões esperadas atualizadas em `test_correcoes_w0`, `test_contrato_build_release` e `test_matriz_new_session`;
  - `test_release_workflow` passa a esperar `--conversa`.
- **Evidência** em `sdd/reports/evidence/F4_CONVERSA/`:
  - scripts: `gerar-evidencia.sh`, `sabotagem.sh` e `comandos-intactos.py`;
  - logs: `GATE`, `suite-piso`, `testes-f4`, `baseline`, `baseline-notas`, `baseline-agnostico`, `comandos-intactos`, `contratos-intactos`, `design-lint-reais`, `skill-lint-conversa`, `check-versions`, `codepoints`, `ci-pr`, `release`, e os `AVAL-*`/`AVAL2-*` dos avaliadores;
  - vereditos: `sdd/reviews/AVALIACAO_F4_CONVERSA_20261029-ciclo1.md` e `…-ciclo2.md`.
- **Sabotagem** (6, em `2fcdda1`):
  - `skill-lint` sem "não sei";
  - `design-lint` sem ciclo;
  - `handoff-lint` sem placeholder no prompt;
  - `test_agnostico` sem `AskUserQuestion`;
  - `como-falar.md` da build sem "não sei";
  - banner de volta na define.

  As 6 ficaram vermelhas com o nome do teste e verdes depois do `git checkout`.
- **Release**:
  - o CI do PR (run 40951200708) deu `gate` e `Testes no piso (macOS)` verdes, com 388 testes, integridade "0 finding(s) in 57 file(s)" e o passo com `--conversa`;
  - o Roberto respondeu "push sdd-open autorizado". Houve push fast-forward `dd27ef6..2fcdda1`;
  - a run `release` 40952893409 rodou `testes` e `testes-macos` antes de publicar → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.5, tag em `2fcdda1`;
  - SHA-256 de `sdd-open-v2.2.5.tar.gz`: `4686f3dafcb9decfeea66308055f3a9123e1413c6c5e6831855a6073a859e053`, com `shasum -a 256 -c` OK.

### Casos e testes em aberto

- **Piso:** `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 388 OK em `2fcdda1` (202 s). A base `dd27ef6` tinha 326.
- **Gate e versões:** `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F4_CONVERSA.md` → 0 em `4e77a1f`, `fd94876` e `2fcdda1`. `check-versions --base v2.2.4 --base-obrigatoria` VERDE.
- **Baseline vermelha:**
  - os 9 módulos da F4, antes do código, deram 78 FAIL e 34 ERROR em 114 testes;
  - os testes das notas, contra os lints de `4e77a1f`, deram 10 FAIL;
  - o `test_agnostico` sobre `git archive v2.2.4` reprova `BUILD_REPORT_TEMPLATE.md:75: Task tool` e `CLARIFY.md:45: AskUserQuestion`.
- **Comandos e passos `v2.2.4` × HEAD nas 14:** só `+ passo ### 8. Conferir`/`+ cmd … design-lint.py …` (design) e `+ passo ### 3b. Conferir a ficha`/`+ cmd … handoff-lint.py …` (handoff).
- **Conferência de fechamento** (inventário):
  - o código roda: 388 testes no piso e no CI;
  - os critérios combinados passam: gate 0, `report-lint` 0, `test_agnostico` vermelho na `v2.2.4`, 1 sabotagem por script e revisão sem HIGH aberto;
  - as mudanças estão em `origin/main` e na tag `v2.2.5`, e os artefatos SDD na branch `docs/incorporar-starter`;
  - o que ficou de fora está nas pendências abaixo.
- **Não verificado:** a obediência de um agente real à camada (tom, ordem das 5 partes, leitura do `como-falar.md`). Os testes conferem só o texto escrito.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- **Conferência num agente real** (Codex CLI e Claude Code):
  - rodar `sdd-define`, `sdd-new-session` (num projeto sem git) e `sdd-release`;
  - ver o Status na 1ª linha, a identificação antes dele, a pergunta com `(recomendado)` e "não sei", e a parada ⏸️.

  É a pendência A-002 do DEFINE e não entra em gate.
- **Risco aceito:** o bloco comum de regras está copiado em 14 `SKILL.md`. O `test_conversa` segura 7 frases-chave; outra frase pode divergir. Quando a F9 reabrir as 13 skills, troque o bloco de uma vez, por substituição de texto.
- **Risco aceito:** o `skill-lint --conversa` não confere pergunta em lista numerada, com `__negrito__` ou com prosa entre a pergunta e as opções, porque ficam fora do formato do DEFINE (ciclo 2, LOW-2).
- **Risco aceito:** opção desconhecida no `skill-lint` (`--verbose`) sai 64. Na `v2.2.4`, ela virava caminho de arquivo e saía 1 (DESIGN, Decisão 2).
- **Pendência herdada:** o `report-lint.py` com cabeçalho não reconhecido continua fail-open (F7); `RESUMO_ETAPA.md:4,49` ainda cita `/adversarial-review` (F10).
- **Para a F5:** a `sdd-kb` nova precisa nascer com a seção e o `references/como-falar.md` no formato da F4, porque o CI roda `skill-lint --conversa` em toda `sdd-*`. O `test_conversa.F4` (14 nomes) e o `test_skill_lint` (16 → 17) mudam de propósito.

### Próximos passos

1. **Sessão 3 — F5 Conhecimento** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), numa worktree nova a partir de `origin/main` = `2fcdda1`. Pronto quando: `BRAINSTORM_F5_*.md` gravado com a decisão 4 do plano respondida pelo Roberto; depois define, design, build e Release com `SHA256SUMS.txt` conferido.
2. **F6 Docs**, depois **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **A camada é contrato testado:**
  - toda skill `sdd-*` precisa passar no `skill-lint --conversa`: seção, tabela `Etapa`, 5 partes e o `como-falar.md` com pergunta de decisão válida;
  - mudar uma das `FRASES` do bloco comum quebra o `test_conversa` nas 14;
  - mudar a versão de uma skill exige mudar a linha de identificação (`<nome> vX.Y.Z · `).
- **`PERGUNTA_DECISAO.md`** é o dono do formato. A W2/F9 preenche o `[Dn]` e liga o `exit 40` aos campos `Brief:`/`Sessão nova:`; não crie um 2º formato.
- **Os 2 lints novos** viajam para o projeto do usuário (`sdd/bin/`). O `handoff-lint` confere o template do **open**; o HANDOFF desta família está no formato do starter e reprova nele, o que é esperado.
- **Evidência:** o `report-lint` só aceita evidência em `evidence/<FEATURE>/`, com o nome exato do relatório (`F4_CONVERSA`, não `F4`).
- **A F4 não mexeu** em `sdd-iniciar-repo` nem `sdd-higiene-dado`. Uma substituição em massa nas skills tem de excluir as duas, ou elas sobem de versão.
- Demais alertas das etapas M1, W0 e F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `2fcdda1` = tag `v2.2.5`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.5.
- Worktree da sessão 2: `/Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa`. A branch `feat/f4-conversa` está em `2fcdda1`, já mesclada.
- Os artefatos SDD (`sdd/features|handoffs|reports|reviews`) estão gravados na branch `docs/incorporar-starter`.
- Limpeza, rodada de fora da pasta e só depois de gravar a branch `docs/`: `git -C /Users/robertoduarte/rdd-public/sdd-open worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f4-conversa && git -C /Users/robertoduarte/rdd-public/sdd-open branch -d feat/f4-conversa`.

---

## 2026-10-29 — M1 Manutenção do CI (entregue, sem Release)

### O que foi feito

- **Escopo** (plano, seção 8, "Manutenção M1"; parâmetro P2): só `.github/workflows/publish-gate.yml`, `.github/workflows/release.yml` e `tests/test_release_workflow.py`. Nenhuma skill mudou de versão. Commits `eac5484` (build) e `dd27ef6` (notas da revisão), sobre `303cc87` = `v2.2.4`; branch `feat/m1`, PR https://github.com/robertodiasduarte/sdd-open/pull/5 (MERGED).
- **Piso no robô**: job `testes-macos` (`macos-latest`, `timeout-minutes: 20`) nos dois workflows. O passo "Floor versions (asserted)" sai ≠0 se `/usr/bin/python3` não for 3.9 ou `/bin/bash` não for 3.2. Ele também põe `$RUNNER_TEMP/piso/python3` (`exec /usr/bin/python3 "$@"`) na frente do `PATH`, então os scripts que chamam `python3` (`bin/sdd-open.sh`, `bin/lib/merge.sh`) também rodam no piso. O job instala o gitleaks 8.30.1 darwin_arm64 (`curl -fsSL`, `gitleaks version`), para nenhuma classe ser pulada, e roda `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'`. No `release.yml`, o `release` passa a `needs: [testes, testes-macos]`.
- **Checkout**: `actions/checkout@11d5960a…` (v4.4.0, Node 20) → `actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5.1.0`, nos 3 `uses:`. É tag leve no commit, `using: node24`, conferida com `git ls-remote` e `gh api`.
- **Integridade das skills** (no lugar do "baseline da `sdd-auditoria-harness`", decisão do Roberto, ver `## Eventos`): passo "Skill integrity (invisible Unicode, remote code piped to a shell)" no job `gate` do `publish-gate.yml` e no job `testes` do `release.yml`. É um programa Python inline idêntico nos dois, com o argumento `.agents/skills`. Ele reprova:
  - Unicode invisível, bidi, de tag (U+E0000–E007F) ou seletor de variação (U+FE00–FE0E, U+E0100–E01EF), além de U+00AD, U+034F, U+061C, os fillers Hangul, U+180E, U+2028–202E e U+FFF9–FFFB;
  - `curl|wget … | sh/bash/zsh/dash/ksh/python/perl/ruby/node` (também com `sudo -E` e caminho absoluto), `base64 -d|-D|--decode … | sh`, `eval "$(curl…)"`, `bash <(curl…)`, `sh -c "$(curl…)"` e `source|. <(curl…)`;
  - arquivo não-UTF-8, e diretório ausente ou sem nenhum arquivo lido.

  O U+200D e o U+FE0F ficam de fora, porque montam emoji (55 usos de FE0F nas skills). As lacunas declaradas no comentário são `| tee x | sh`, pipe quebrado por `\` e PowerShell `iex`. Hoje dá 0 achados em 43 arquivos.
- **`tests/test_release_workflow.py`** 17 → 27 testes:
  - `PisoNoMacos`: job, piso afirmado, PATH, gitleaks, timeout e `needs`;
  - `IntegridadeDasSkills`: o programa é **extraído do workflow** e executado contra 19 amostras montadas com `chr()`, mais o controle com emoji ZWJ/FE0F e `| shasum`, o alvo vazio ou inexistente, o binário e as skills do `MANIFEST.txt`;
  - `test_checkout_e_o_v5_em_todo_job`.
- **Relatório**: `sdd/reports/BUILD_REPORT_M1.md` (`report-lint` 0). A evidência está em `sdd/reports/evidence/M1/`: `baseline.log`, `sabotagem.sh`/`.log`, `gerar-evidencia.sh`, `GATE.log`, `suite-piso.log`, `check-versions.log`, `deploy-espera-testes.log`, `checkout-v5.log`, `escopo.log`, `testes-m1.log` e `ci-pr5.log`.
- **Sabotagem** (8, em `dd27ef6`, revertidas com `git checkout`):
  - `release` sem `testes-macos` no `needs`;
  - job do piso em ubuntu;
  - um checkout de volta ao v4.4.0;
  - sem U+061C;
  - alvo vazio passando;
  - piso só impresso;
  - `source <(curl)` passando;
  - a varredura do gate sem `exit 1`.

  As 8 ficaram vermelhas com o nome do teste.
- **Publicação**: o Roberto respondeu "finalizar (push + deploy + verificar) sdd-open". Push fast-forward `303cc87..dd27ef6` em `main`. Só o `publish-gate` roda: run 40931927983 verde, com `gate` e `testes-macos` em success. Nenhuma run de `release.yml` em `dd27ef6`, então **não há tag nem Release** da M1 (`paths` do `release.yml`); a última Release continua `v2.2.4` (`evidence/M1/main-push.log`).

### Casos e testes em aberto

- CI do PR #5 (run 40929387392, `dd27ef6`): `gate` (ubuntu) 326 OK, com a varredura dando 0 achados em 43 arquivos; `testes-macos` 326 OK, 0 skip, `3.9.6 (default, May 22 2026, 11:13:45)` e `bash 3.2.57(1)-release` afirmados, `command -v python3` = `/Users/runner/work/_temp/piso/python3`. A suíte levou 219,8 s no macOS e 140 s no ubuntu.
- Piso local (Python 3.9.6, bash 3.2.57): 326 OK em 187,9 s. publish-gate ci 0; `check-versions --base v2.2.4` VERDE; `deploy-espera-testes.py .` SIM.
- Baseline: o `test_release_workflow` novo sobre `v2.2.4` dá 8 FAIL e 25 ERROR.
- Não verificado: a primeira run de `release.yml` com o `needs: [testes, testes-macos]` só acontece no próximo push que tocar os `paths` do produto (a F4); confira nela que o `release` esperou os dois jobs.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Varredura de integridade também em `AGENTS.md.tmpl`, `sdd/templates/**` e `sdd/playbook.md` (nota 5 da revisão; o escopo declarado da M1 era `.agents/skills/`).
- Risco aceito: um texto de skill que **alerta** contra `curl … | sh` escrito literalmente reprova. A regra é descrever sem o padrão literal.
- Risco aceito: o `release` depende do runner macOS. Uma falha só do macOS deixa aquele push sem Release até um re-run ou um próximo push nos `paths`; como o repositório é público, os minutos não custam.
- Risco aceito: se o `macos-latest` deixar de trazer Python 3.9, o job reprova e a Release trava. Isso é de propósito (o piso deixou de ser provado); a saída é decidir o piso novo ou fixar a imagem.
- O gitleaks do job Ubuntu (anterior à M1) usa `curl -sSL`, sem `-f` e sem checksum.

### Próximos passos

1. **Sessão 2 — F4 Conversa** (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`), numa worktree nova a partir de `origin/main` = `dd27ef6`. Pronto quando: o BRAINSTORM da F4 estiver gravado com as decisões 2 e 3 da seção 5 do plano respondidas pelo Roberto.
2. **F4 — define, design, build e release**, com o ciclo das F1–F3. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, CI verde em ubuntu **e** macOS, e a Release com `SHA256SUMS.txt` conferido.
3. **F5 → F6**, depois **F7 → F14** e **F15** (plano, seções 8 e 10).

### Alertas — o que não quebrar

- **O CI agora tem 3 portas novas.** Texto novo de skill (a F4 escreve muito) não pode trazer caractere invisível nem `curl … | sh` literal; emoji com ZWJ e com FE0F passa. Toda release espera o macOS (~4 min a mais). O piso de 3.9 e 3.2 é **afirmado**: código que só roda em Python ≥3.10 quebra no CI.
- **Testes com Unicode invisível** montam a amostra com `chr()`, nunca com o caractere literal. Na sessão 1, um `\u200b` digitado virou o caractere de verdade ao passar pelo agente: confira os bytes depois de escrever (`python3 -c` contando os code points).
- **A M1 não gera tag.** O `check-versions` da F4 compara com `v2.2.4`.
- Demais alertas da etapa W0 e da F3 continuam valendo.

### Onde está o trabalho

- Remoto `https://github.com/robertodiasduarte/sdd-open.git`, `main` = `dd27ef6`. Última Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.4.
- Worktree da sessão 1: `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1` (branches `feat/w0-m1` em `303cc87`, `feat/m1` em `dd27ef6`). Os artefatos SDD (`sdd/features|handoffs|reports`) estão gravados na branch `docs/incorporar-starter`.

---

## 2026-10-29 — W0 As 5 correções do porte (entregue, Release v2.2.4)

### O que foi feito

- **Escopo** (plano, seção 3.1; parâmetro P1): fix sem BRAINSTORM/DEFINE/DESIGN (regra "Quando pular o SDD formal" da `sdd-release`). Commits `b1df8c8` (build) e `303cc87` (notas da revisão), sobre `1a54da5` = `v2.2.3`; branch `feat/w0-m1`, PR https://github.com/robertodiasduarte/sdd-open/pull/4 (MERGED).
- **4.1** `.agents/skills/sdd-iterate/SKILL.md` 2.0.0 → 2.0.1. O passo 4 roda duas chamadas, nesta ordem:
  - `sdd/bin/verify-gate.sh --print <DEFINE>`: 0 = bloco presente, 64 = ausente. Não valida `kind`/`cmd` e é isento de marcador.
  - `sdd/bin/verify-gate.sh <DEFINE>`: 5 = voltar ao Define; 64 = corrigir o bloco; 0/2/3/4 não são deste passo, e a seta do vermelho não vale ali.

  Com `kind` smoke/eval ou `cmd` que grava, envia ou cobra, o passo procura o marcador pela forma canônica do `CLARIFY.md` em vez de rodar o gate.
- **4.2** sai a linha e o bullet "CONTEXTO de domínio" do `sdd/templates/DEFINE_TEMPLATE.md` (volta na F12). No `sdd/config.example.yaml`, os dois "(slice 2)" saem; o comentário de `layers` diz que `sql` também decide migration, e o de `editor`/`worktree_base` aponta a `sdd-new-session`.
- **4.3** sai `/drive` de `sdd/templates/fragments/CLARIFY.md`, `sdd/templates/DEFINE_TEMPLATE.md` e `sdd/templates/fragments/VERIFY_GATE.md` (a skill volta na F14).
- **4.4** `sdd/templates/fragments/EVIDENCIA.md` e `sdd/templates/BUILD_REPORT_TEMPLATE.md` apontam `sdd/bin/report-lint.py` (o guard `.githooks/claude-build-report-guard.py` volta na F7). O EVIDENCIA.md muda em quatro pontos:
  - os 13 "o hook" viram "o lint";
  - a regra 4 ("falha ABERTO … `systemMessage`") vira "falha FECHADO em erro interno";
  - passa a dizer que o lint acha a tabela pelo cabeçalho (coluna `Evid…` + `Resultado`/`Status`/`Passou`): cabeçalho em inglês sai 0 sem conferir;
  - `pass`/`verde` também contam como `true`.

  Ainda nos templates: "Step 1.5" vira "passo 1.5 da `sdd-build`" (`BUILD_REPORT_TEMPLATE.md`, `DESIGN_TEMPLATE.md`), e "§6.3 do PLANO" vira o `contexto-fresco.md`.
- **4.5** `.agents/skills/sdd-build/references/contexto-fresco.md` (com a `sdd-build` 2.1.0 → 2.1.1): os dois briefs dizem "Não edite código nem documento do projeto: o único arquivo que você grava de propósito, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`".
- **Vizinhos corrigidos pela revisão**: `CLARIFY.md` ("Lido pela `sdd-define` (passo 6)"), `sdd/templates/fragments/EARS.md` (sem `/define` (Step 4.5) e sem `/bug-pipeline`) e `DEFINE_TEMPLATE.md:91` (sem `AskUserQuestion`).
- **`tests/test_correcoes_w0.py`** (12 testes, novo no `MANIFEST.txt`): executa as chamadas **escritas** no passo 4 sobre `sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` (5) e `DEFINE_FIXTURE_CONTROLE.md` (≠5). Também varre todo arquivo do `MANIFEST.txt` atrás de `build-report-guard|/drive|Step 1\.5|slice 2|CONTEXTO de domínio|/bug-pipeline|`/define` \(Step`, e confere os briefs e as versões. `tests/test_contrato_build_release.py` passa a esperar a `sdd-build` 2.1.1.
- **Relatório**: `sdd/reports/BUILD_REPORT_W0.md` (`report-lint` 0, 7 ATs). A evidência está em `sdd/reports/evidence/W0/`: `baseline.log`, `sabotagem.sh`/`.log`, `gerar-evidencia.sh`, `W0-4.1-fixture.log`, `W0-testes.log`, `W0-grep.log`, `GATE.log`, `suite-piso.log`, `check-versions.log`, `contratos-intactos.log` e `release.log`.
- **Sabotagem** (8, em `303cc87`): passo 4 só com `--print`; "(slice 2)" de volta; `/drive` no `CLARIFY.md`; guard no `EVIDENCIA.md`; "O hook `build-report-guard`" no template; `/drive` no `AGENTS.md.tmpl`; aviso de smoke/eval removido; "Não escreva em arquivo algum". As 8 ficaram vermelhas e voltaram ao verde.
- **Release**: CI do PR #4 (run 40926042337) com 316 OK, publish-gate verde e check-versions VERDE. O Roberto respondeu "ok \"sdd-open\"". Push fast-forward `1a54da5..303cc87`, run `release` 40926754472 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.4, tag em `303cc87`, SHA-256 de `sdd-open-v2.2.4.tar.gz` `b8a0aab0d58b87050d80c68813c868f6a2d4f9784fe7130ad663efc63a555670`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 316 OK em `303cc87` (192 s).
- Baseline: o `test_correcoes_w0` sobre `v2.2.3` dá 9 FAIL de 12. Os 3 verdes caracterizam o `verify-gate.sh`, que não mudou.
- Contratos intactos: `git diff v2.2.3 HEAD -- sdd/bin/ sdd/fixtures/ scripts/ .github/` vazio; `playbook-lint.sh --self-test` 0.
- Conferência de fechamento (inventário):
  - o código roda: 316 testes no piso e no `ubuntu-latest`;
  - os critérios combinados passam: grep sem hit, fixture 0/5, publish-gate 0, check-versions 0, revisão sem HIGH aberta;
  - as mudanças estão em `origin/main` e na tag `v2.2.4`, e os artefatos SDD na branch `docs/incorporar-starter`;
  - o que ficou de fora está nas pendências abaixo.
- Não verificado: a obediência do agente ao passo 4 novo da `sdd-iterate` (só o texto e as chamadas escritas são testados).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- `sdd/bin/report-lint.py` sai 0 quando nenhuma tabela tem o cabeçalho reconhecido mas há linhas `AT-nnn` com `true` (nota 4 da revisão; reproduzido com `| ID | Criterion (EARS) | Result | Evidence |`). Hoje está só **documentado** no `EVIDENCIA.md`. A correção (fail-closed) muda o contrato de `sdd/bin/` e fica para a **F7**.

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- `sdd/templates/fragments/CLARIFY.md:45` ainda diz `AskUserQuestion`; o `tests/test_agnostico.py` da F4 (item G) pega.
- `sdd/templates/fragments/RESUMO_ETAPA.md:4,49` cita `/adversarial-review`, que o pacote não tem; fica para a F10 (a Decisão 3 manda deixar o kanban intacto).
- Templates citam `/build`, `/define`, `/design` (forma curta da fase) e não `/sdd-build`; a F4 reescreve a camada de conversa.

### Próximos passos

1. Ver a etapa M1, acima: a F4 Conversa é a próxima.

### Alertas — o que não quebrar

- O passo 4 da `sdd-iterate` e os briefs de `contexto-fresco.md` são conferidos por `tests/test_correcoes_w0.py`. Se a F4 reescrever essas skills, mantenha as duas chamadas `sdd/bin/verify-gate.sh … <DEFINE>` entre crases, o aviso de smoke/eval e a frase "o único arquivo que você grava de propósito, pelo shell, é `sdd/reports/evidence/{F}/AVAL-*.log`", ou atualize o teste de propósito.
- Nenhum arquivo do `MANIFEST.txt` pode citar `/drive`, `build-report-guard`, `CONTEXTO de domínio`, "Step 1.5", "slice 2", `/bug-pipeline` ou "`/define` (Step". Quando a F7, a F12 ou a F14 trouxer o mecanismo de volta, o teste muda junto.
- `sdd-iterate` 2.0.1 e `sdd-build` 2.1.1: o `check-versions` da F4 compara com `v2.2.4`.

### Onde está o trabalho

- Ver a etapa M1, acima (mesma worktree e mesmo remoto).

---

## 2026-10-29 — F3 Build e Release (entregue, Release v2.2.3)

### O que foi feito

- **Fluxo SDD da F3** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md` (abordagem A — tudo numa release; 15 decisões; 8 cortes YAGNI; 2 checkpoints), `sdd/features/DEFINE_F3_BUILD_RELEASE.md` (23 ATs EARS, Clarity 14/15, `verify-gate.sh --print` 0, `validate_define.py` PASS), `sdd/features/DESIGN_F3_BUILD_RELEASE.md` v1.1 (14 arquivos, 7 ADRs, `validate_design.py` PASS), `sdd/reports/BUILD_REPORT_F3_BUILD_RELEASE.md` (Complete; `report-lint.py` 0; `validate_build_report.py` PASS; evidência em `sdd/reports/evidence/F3_BUILD_RELEASE/`: `AT-001.log`…`AT-023.log`, `GATE.log`, `GATE-1-vermelho.log`, `baseline.log`, `suite-piso.log`, `release.log`, `sabotagem.sh`, `gerar-at.sh`).
- **Código em `main`** (commits `8c1a593` build, `af8b0e3` teste fora de git, `1a54da5` notas da revisão):
  - `sdd/bin/report-lint.py` — `problema_do_log()` extraída de `evidence_ok()` sem mudar mensagens; regra nova: migration (1º caminho entre crases de uma linha de tabela em seção `## Files…`/`## Arquivos…`/`…Manifest…`, também numerada ou com prefixo `… —`; termina em `.sql`, tem `migrations/` ou casa `layers.sql` do `sdd/config.yaml`; linha com Delete/Removido ignorada) exige linha em `## Migrations aplicadas` com o mesmo caminho, projeto `nome · ref`, data `AAAA-MM-DD` (ou "já aplicada em …") e prova = log de `evidence/<F>/` com `$ ` ou `recibo: nome AAAA-MM-DD`; "exit 0" e declaração reprovam. Relatório sem migration não muda.
  - `.agents/skills/sdd-release/scripts/deploy-espera-testes.py` (423 linhas, `100755`, só stdlib, mini-parser de YAML) — `SIM` 0 · `NAO` 1 · `NAO_SEI` 2 · `NAO_SE_APLICA` 3 · 64 uso; teste só em posição de comando (instalar `pytest` não é testar); `continue-on-error`, `|| true`, pipe sem pipefail, `set +e … exit 0`, `if: always()` no passo, no job ou num job do meio do `needs:` ⇒ NAO; `workflow_run`, reutilizável, teste com `if:`, `set +e`, job com nome de deploy não reconhecido, arquivo que não abre ⇒ NAO_SEI. Na raiz do sdd-open dá SIM; no `/Users/robertoduarte/RDD/Wordpress` dá NAO (`deploy-hostinger.yml · job deploy-production`, passo 'Sync theme patch').
  - `.agents/skills/sdd-release/SKILL.md` 2.1.0 → 2.2.0 — item 7 da FASE 1 = bloco único do OK (O que sobe · O que muda em produção · O push publica sozinho? · O deploy espera os testes? · Banco · Verificações · Veredito · Ledger · "Posso finalizar (push + deploy + verificar)?"); 0a.5 e item 10 citam a regra e o script.
  - `.agents/skills/sdd-build/SKILL.md` 2.0.0 → 2.1.0 (passo 4b) + `references/aplicar-migration.md` (206 linhas; porte do starter sem `sdd/ambiente.md`; CNPJ literal virou `<valor de teste>`; log `MIG-nnn.log` ou recibo).
  - `sdd/templates/BUILD_REPORT_TEMPLATE.md` (seção condicional `## Migrations aplicadas`), `sdd/templates/fragments/EVIDENCIA.md` (parágrafo "Migration aplicada"), `sdd/playbook.md` (`LM-004`, `promovido_para: sdd/bin/report-lint.py`).
  - `bin/sdd-open.sh` — `versao_skill()` (aspas simples, duplas ou nenhuma), `versao_menor()` (awk), e no `doctor`: ⚠️ `<skill> <vp> no projeto, <vq> no pacote — para receber: apague .agents/skills/<skill> e rode init (edições suas nela se perdem)`; ⚠️ `sdd/bin/<f> difere do pacote — se você não editou, apague e rode init`; ✅ `skills e sdd/bin/ em dia com o pacote`; exit 0.
  - `tests/` — `test_report_lint.py` (+18 em `Migrations`), `test_deploy_espera_testes.py` (29), `test_sdd_open.py` (+3 de `doctor`), `test_contrato_build_release.py` (12). Total **304**. `MANIFEST.txt` 110 → 114.
- **Nada de `sdd/bin/verify-gate.sh`, `sdd/fixtures/`, `scripts/publish-gate*` ou `.github/` mudou** (`git diff --stat v2.2.2 HEAD -- …` vazio, `evidence/F3_BUILD_RELEASE/AT-022.log`).
- **Sabotagem** (3, em `1a54da5`, revertidas com `git checkout`): `report-lint.py` sem a violação de linha ausente → `test_migration_sem_linha_reprova`, `test_migration_sem_a_secao_reprova` e mais 2 (+4 subtests); script sem `continue-on-error` do passo → `test_continue_on_error_no_passo_de_teste_nao_segura`; `doctor` sem o `cmp` → `test_doctor_avisa_sdd_bin_diferente_do_pacote`. Todas verdes depois.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/3 (CI run 40912938021: publish-gate verde, `Ran 304 tests`, check-versions VERDE) → OK do Roberto ("push do sdd-open autorizado") → push fast-forward → run 40915091971 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.3, tag em `1a54da5`, SHA-256 de `sdd-open-v2.2.3.tar.gz` `635e30050b83188f5965ffa5ddd09fac496973dc4a66d7bbd6391c9eb1ffd777`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F3_BUILD_RELEASE.md` → exit 0 em `1a54da5` (G1–G5 verdes na cópia de `git archive HEAD`, `Ran 304 tests … OK` no `python3` 3.15 do PATH). Log: `sdd/reports/evidence/F3_BUILD_RELEASE/GATE.log`.
- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'` → 304 OK em `1a54da5` (Python 3.9.6, bash 3.2.57), ~3,1 min; 129 s no CI.
- Casos do revisor: `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-open-incorporar-starter/b8371a83-c760-4658-af04-e6321f52e2df/scratchpad/de_casos.py` (15 workflows; some quando o `/private/tmp` for limpo) — depois de `1a54da5`, 0 SIM falso; casos 3, 6, 8 e 11 dão NAO_SEI onde o revisor esperava NAO (aceito: não afirma o que não sabe).
- Conferência de fechamento (inventário): o código roda (304 testes local no piso e no `ubuntu-latest`); os critérios combinados passam (gate `--strict` 0, `report-lint` 0, 23 ATs com log, 3 sabotagens); as mudanças estão em `origin/main` = `1a54da5` = tag `v2.2.3`, e os artefatos SDD em `sdd/features|reports|handoffs` desta worktree (não rastreados, de propósito); o que ficou de fora está nas pendências abaixo.
- Não verificado: a obediência do agente à `sdd-build` 2.1.0 e à `sdd-release` 2.2.0 (A-003 do DEFINE: só o contrato escrito é testado); o bloco do OK num projeto real com migration aplicada de verdade.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`.)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F4 Conversa — próxima (ver Próximos passos e o prompt de retomada).
- Risco aceito (nota 11 da revisão, rebatida): teste pgTAP em `*.sql` (`supabase/tests/*.sql`, `tests/security/*.sql`) listado nos arquivos do relatório passa a exigir linha em `## Migrations aplicadas`. Contorno hoje: não listar o teste como `.sql` na tabela de arquivos. Melhoria possível: excluir caminhos com segmento `tests/` — muda o contrato "`*.sql` = migration" do DEFINE, então pede decisão.
- Risco aceito (nota 10, em parte rebatida): o lint só vê o 1º caminho entre crases de cada linha e isenta a linha com uma célula "removido" em qualquer coluna (Decisão 1 do DESIGN; 1 linha afetada em 250 relatórios reais).
- Risco aceito: o `deploy-espera-testes.py` é heurística; o que ele não entende vira NAO_SEI (a skill então lê os workflows e escreve "não consegui afirmar"). Teste rodado por script próprio (`./ci.sh`) dá NAO_SEI.
- Para depois: o `doctor` avisa, mas o caminho para atualizar continua "apague e rode init" — um verbo `upgrade` com backup é redesenho da CLI (fora de escopo até aqui). Ligar `checar.sh --segredo` ao `release.landmines_cmd`; README e `AGENTS.md.tmpl` citando as 3 skills da F2 e o bloco do OK (F6).
- Carregados da F1/F2: trocar o pin `actions/checkout@11d5960a…` (v4.4.0, Node 20 depreciado) por SHA de v5 nos dois workflows; observar o CI no Ubuntu 26; tag manual e push de `main` no mesmo commit podem deixar duas tags (para minor/major, empurrar a tag depois da run de `main`); guia do aluno não rastreado em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, entrada da F6 — um `git clean` naquele checkout o apaga); `checar.sh` rodado de subpasta sugere `git rm --cached` com caminho relativo à raiz (nota 6 da F2).

### Próximos passos

0. **Sessão 1 em worktree limpa (prompt em `sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md`): W0 + M1.** A ordem da W0 antes da F4 ficou decidida com o agrupamento da seção 10 do plano. **Fazer a W0**: 5 correções da seção 3.1 do plano, cada skill tocada com bump (`sdd-iterate`, `sdd-build`) e teste em `tests/`. Pronto quando: `verify-gate.sh sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md` (sem `--print`) sai 5 por teste, e `grep -rnE 'claude-build-report-guard|/drive|Step 1\.5|slice 2' sdd/ .agents/` não acha nada; Release publicada.
1. **F4 Conversa — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F4_CONVERSA.md`, com o plano consolidado (seção 4.1, itens A–F) como entrada. Entradas: seção `## Como falar com o aluno` + `references/como-falar.md` nas 13 skills nativas (fonte no starter `17c69c4` para 7: brainstorm, build, define, design, handoff, new-session, release; escrever do zero para 6: auditoria-harness, governanca, iterate, playbook, prompt-builder, ux-review); `skill-lint.py` conferindo a seção; `design-lint.py` e `handoff-lint.py` em `sdd/bin/` (reescrita a partir de `skills/sdd-design/scripts/validate_design.py` e `skills/sdd-handoff/scripts/validate_handoff.py` do starter); `metadata.updated` + linha de identificação nas 13. Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F4 — define, design, build** com o mesmo `verify_gate` da F3; manifest com `MANIFEST.txt`; commit antes do gate; diff por skill provando que comandos e ordem dos passos não mudaram. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, 1 sabotagem por script alterado.
3. **F4 — release**: PR, CI verde, OK citando "sdd-open", push em `main`. Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e o hash confere.
4. **F5 → F6**, mesmo ciclo; depois **F7 → F14** na ordem da seção 8 do plano (F7 Evidência depende da W0; F8 de F7; F9 de F4 e F7; F10 de F9; F11 de F10; F12 de F7 e F9; F13 de F5 e F7; F14 de todas); por fim **F15** no repositório privado (parâmetro P4). M1 vai junto com a W0 na sessão 1.

### Alertas — o que não quebrar

- **A branch `docs/incorporar-starter` nunca vai para `main`**: ela carrega os artefatos SDD do desenvolvimento do próprio Open (caminhos `/Users/`, sem `MANIFEST.txt`); em `main` iriam para o pacote que o aluno baixa e o G2/G3 reprovariam. O CI não roda nela (só `main` e PR). Nunca abrir PR dela.
- **W0 × F4 tocam os mesmos arquivos** (`.agents/skills/sdd-iterate/SKILL.md`, `.agents/skills/sdd-build/references/contexto-fresco.md`, `sdd/templates/fragments/{CLARIFY,VERIFY_GATE,EVIDENCIA}.md`, `sdd/templates/{DEFINE,BUILD_REPORT}_TEMPLATE.md`): não rodar as duas em paralelo.
- **O `report-lint` agora lê arquivos e migrations**: qualquer mudança no template do BUILD_REPORT (F4 pode mexer) mantém `## Files…` e `## Migrations aplicadas` com as colunas Arquivo · Projeto (nome · ref) · Aplicada em · Prova por leitura; `tests/test_contrato_build_release.py` confere.
- **O bloco do OK da `sdd-release`** tem os rótulos e a ordem conferidos por `test_contrato_build_release.SddRelease` (uma pergunta só, na última linha). A camada de conversa da F4 entra **em volta** do bloco, sem renomear rótulo nem acrescentar pergunta.
- **Skill alterada sobe versão** (`sdd-build` 2.1.0, `sdd-release` 2.2.0, demais como em `.agents/skills/*/SKILL.md`): `check-versions.py --base v2.2.3 --base-obrigatoria`. Se o clone não tiver a tag: `GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.3`. A F4 muda as 13 ⇒ 13 bumps.
- **O `doctor` passa a avisar** projeto com skill mais velha que o pacote: depois da F4, toda instalação existente verá 13 avisos — é o comportamento esperado.
- **Literais do G2**: e-mail só em `example.com/.org/.net`; `git@host`, CPF, CNPJ, telefone e qualquer sequência de 11+ dígitos (timestamp de migration!) montados em tempo de execução; hosts em `.invalid`.
- **Testes que dependem de git** rodam numa sandbox com `git init` (`apoio.Sandbox.repo()`): a cópia do Verify Gate vem de `git archive` e não tem `.git`.
- **Modo de arquivo**: `bin/sdd-open.sh` e `sdd/bin/report-lint.py` são `100644` no índice; `deploy-espera-testes.py` é `100755`. Não fazer `chmod` em massa.
- Demais alertas continuam valendo (`GIT_TERMINAL_PROMPT=0`, push em `main` só com OK citando "sdd-open", `MANIFEST.txt` em `LC_ALL=C`, `python3 -B`, `git add` por nome, bash 3.2, sem zsh/symlink, `sync` idempotente, 16 skills em `tests/test_skill_lint.py`).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `1a54da5` = `origin/main` = tag `v2.2.3`. Não rastreados nela: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/` — **versionados na branch `docs/incorporar-starter`** (tag `docs-2026-10-29`), nunca mesclada em `main`; cada sessão nova os recupera com `git checkout docs/incorporar-starter -- sdd/features sdd/handoffs sdd/reports && git rm -r -q --cached sdd/features sdd/handoffs sdd/reports` e, ao fechar, grava a etapa nova lá (comandos no prompt de retomada).
- Plano do programa: `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` v1.3 (parâmetros P1–P4, F4–F15, slots, fontes, agrupamento por sessão).
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.3 · PR #3 merged.
- Fonte da F4: `/Users/robertoduarte/rdd-public/sdd-starter` (main `17c69c4`): `skills/*/SKILL.md` (seção `## Como falar com o aluno`), `skills/*/references/como-falar.md`, `sdd/DEFINE_LINGUAGEM_ALUNO.md` (193 linhas, os 10 itens da camada), `skills/sdd-design/scripts/validate_design.py` (212 linhas), `skills/sdd-handoff/scripts/validate_handoff.py` (94), `skills/sdd-handoff/scripts/gate.sh` (32).

---

## 2026-10-29 — F2 Terreno (entregue, Release v2.2.2)

### O que foi feito

- **Fluxo SDD da F2** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F2_TERRENO.md` (abordagem A — transplante com adaptação mínima; 15 decisões; 9 cortes YAGNI; 2 checkpoints), `sdd/features/DEFINE_F2_TERRENO.md` (21 ATs EARS, Clarity 14/15, `verify-gate.sh --print` 0 e `validate_define.py` PASS), `sdd/features/DESIGN_F2_TERRENO.md` v1.1 (22 arquivos, 7 ADRs, `validate_design.py` PASS), `sdd/reports/BUILD_REPORT_F2_TERRENO.md` (Complete; `report-lint.py` 0; `validate_build_report.py` PASS; evidência em `sdd/reports/evidence/F2_TERRENO/`: `AT-001.log`…`AT-021.log`, `suite-piso.log`, `release.log`, `sabotagem.sh`).
- **Código em `main`** (commits `4ee5470` build, `41c6169` notas da revisão):
  - `.agents/skills/sdd-checar-ambiente/` 1.3.0 — `SKILL.md` + `scripts/checar.sh`: porte do starter 1.2.0; `dado_exposto()` extraída da seção 6 e filtrada por pathspec `:(glob,icase)**/.env`, `**/.env.*`, `**/*.pfx`, `**/*.p12` + `grep --cached "PRIVATE KEY"` em `*.pem`; modo novo `--segredo` (só o bloco `🔴 Dado exposto`, sem rede, exit 1 com achado / 0 sem); `voce@example.com`; identificação aponta `sdd-open/releases/latest`.
  - `.agents/skills/sdd-higiene-dado/` 1.1.1 — `alarme.sh instalar` tira as linhas `sdd-open:generated` (o hook da cópia de `.claude/skills/` sai igual byte a byte ao da fonte); `pre-commit.sh`, `manifest.json`, `evals/cases.json`, `CHANGELOG.md` (entrada 1.1.1), 3 `references/` literais.
  - `.agents/skills/sdd-iniciar-repo/` 1.1.1 — `SKILL.md` + `scripts/inventario.sh`; `npx … sdd-starter` trocado pela `sdd-higiene-dado` que volta com o `init`.
  - Nenhuma das 3 tem `agents/openai.yaml` (o `doctor` usa esse arquivo para avisar "skills do sdd-starter detectadas").
  - `bin/sdd-open.sh` — fim de `doctor()`: roda o `.agents/skills/sdd-checar-ambiente/scripts/checar.sh --segredo` do pacote a partir da raiz do projeto; ⚠️ por achado (no stderr) com comando e medida; `✅ nenhum segredo salvo no git (…)`; ⚠️ "pacote incompleto" sem o script; continua exit 0 com `RESULTADO`.
  - `.agents/skills/sdd-new-session/SKILL.md` 1.0.0 → 1.1.0 (262 linhas): Passo 0 por `checar.sh --frente` (exit 1 para e traduz; exit 0 com `✅ Pronto para abrir a frente: repo <r>, principal <b>` segue; resto ⇒ pré-voo à mão); tabela "Como traduzir cada achado" com 17 trechos literais + "Qualquer outro achado"; Passo 1 descobre os 5 slots (`default_branch` cheio que diverge do remoto ⇒ para e pergunta; `test_cmd`/`lint_cmd` só com evidência literal: workflow > `package.json` > `Makefile`); Passo 2 item 6 grava só slot vazio no `sdd/config.yaml` da frente com `# descoberto por sdd-new-session (AAAA-MM-DD): <evidência>`, sem commit.
  - `tests/` — `test_checar.py` (53 portados + 4), `test_alarme.py` (28 + 1, git isolado), `test_inventario.py` (24), `test_matriz_new_session.py` (12: matriz script×tabela nos dois sentidos, contrato da `new-session`, portadas sem starter/`openai.yaml`/`tests/`), `test_sdd_open.py` (+5), `test_skill_lint.py` (16 skills). Total **242**.
  - `MANIFEST.txt` 93 → 110 linhas.
- **Nada de `sdd/`, `scripts/publish-gate*` ou `.github/` mudou**: `git diff v2.2.1 41c6169 -- sdd/ scripts/publish-gate.sh scripts/publish-gate-patterns.txt .github/` vazio.
- **Sabotagem** (5, em `41c6169`, revertidas com `git checkout`): `checar.sh` sem `*.p12` → `test_p12_e_env_variante` + `test_acusa_cada_tipo_e_sai_1`; `alarme.sh` sem o filtro → `test_hook_da_copia_gerada_sem_cabecalho_e_igual_ao_da_fonte`; `pre-commit.sh` aceita qualquer 2º DV de CPF → `test_digito_errado_nao_bloqueia`; `inventario.sh` `LIMITE_MB=500` → 4 testes; `doctor` sem `--segredo` → 2 testes. Todas verdes depois.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/2 (CI run 40899262016: publish-gate verde, `Ran 242 tests`, version gate VERDE com 16 skills) → OK do Roberto → push fast-forward → run 40900694496 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.2, tag em `41c6169`, SHA-256 de `sdd-open-v2.2.2.tar.gz` `fc7737a35c6252c428f6fd5614cc6d6a37560732e74345e3dea9ea3e3c8d164a`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F2_TERRENO.md` → exit 0 em `41c6169` (G1–G5 verdes na cópia de `git archive HEAD`, `Ran 242 tests … OK`). Log: `sdd/reports/evidence/F2_TERRENO/AT-001.log`.
- Piso: `SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py' -v` → 242 OK, 0 skip (Python 3.9.6, bash 3.2.57). Tempo da suíte ~2,9 min local, 131 s no CI; `test_checar.py` sozinho ~100 s (casos que esperam o teto de 10 s do `alcance`).
- Medição do `--segredo`: repo com 5.000 arquivos rastreados, 11,7 s antes da nota 2, 0,056 s depois; `test_repositorio_grande_continua_rapido` (3.000 arquivos, < 3 s) protege.
- Conferência de fechamento (inventário): o código roda (242 testes local no piso e no `ubuntu-latest` do CI); os critérios combinados passam (gate `--strict` 0, `report-lint` 0, 21 ATs com log, 5 sabotagens); as mudanças estão em `origin/main` = `41c6169` = tag `v2.2.2`, e os artefatos SDD em `sdd/features|reports|handoffs` desta worktree (não rastreados, de propósito); o que ficou de fora está nas pendências abaixo.
- Não verificado: a suíte com a rede de fato desligada (o isolamento vem dos servidores HTTP locais e de hosts `.invalid`); a obediência do agente à `sdd-new-session` (A-003 do DEFINE: só o contrato escrito é testado).

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`.)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F3 Build e Release — próxima (ver Próximos passos e o prompt de retomada).
- Risco aceito (nota 6 da revisão, recusada): `checar.sh` rodado de uma subpasta sugere `git rm --cached "<caminho relativo à raiz>"`, que falha a partir da subpasta. Herdado do starter; o `doctor` entra na raiz antes. Corrigir quando a saída do `checar.sh` puder mudar (os 57 testes conferem o texto).
- Risco aceito: `config.example.yaml` vem com `default_branch: main`; num remoto em `master`, a `new-session` 1.1.0 para e pergunta em toda frente até o usuário corrigir a linha.
- Risco aceito (decisão do Roberto no Brainstorm): `editor` e `worktree_base` descobertos vão para o `sdd/config.yaml` commitado (compartilhado); a skill declara a evidência ("`command -v code` neste computador", "padrão do sdd-open") e avisa que qualquer um corrige a linha.
- Ruído: `ResourceWarning: unclosed socket` dos servidores HTTP locais do `test_checar.py` portado (veio do starter; não é falha).
- Para depois: ligar `checar.sh --segredo` (sai 1 com achado) ou o `pre-commit.sh` ao `release.landmines_cmd`; `init` sem git oferecer a `sdd-iniciar-repo`; README e `AGENTS.md.tmpl` citando as 3 skills novas (F6).
- Carregados da F1: trocar o pin `actions/checkout@11d5960a…` (v4.4.0, Node 20 depreciado) por SHA de v5 nos dois workflows; observar o CI no Ubuntu 26; tag manual e push de `main` no mesmo commit podem deixar duas tags (para minor/major, empurrar a tag depois da run de `main`); guia do aluno não rastreado em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, entrada da F6 — um `git clean` naquele checkout o apaga).

### Próximos passos

1. **F3 Build e Release — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F3_BUILD_RELEASE.md`. Entradas: `references/aplicar-migration.md` do starter (195 linhas) → `.agents/skills/sdd-build/references/`; seção `## Migrations aplicadas` em `sdd/templates/BUILD_REPORT_TEMPLATE.md` + regra em `sdd/bin/report-lint.py`; bullet `LM-004` no `sdd/playbook.md`; bloco único do "go" da Fase 2 da `sdd-release` do starter (linhas 203–254 de `skills/sdd-release/SKILL.md`). Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F3 — define, design, build**: `DEFINE_F3_BUILD_RELEASE.md` com o mesmo `verify_gate` da F2; manifest com `MANIFEST.txt`; commit antes do gate. Pronto quando: `verify-gate.sh --strict` 0, `report-lint.py` 0, 1 sabotagem por script alterado.
3. **F3 — release**: PR, CI verde, OK citando "sdd-open", push em `main` → `v2.2.3` automática (ou tag manual depois da run). Pronto quando: `gh release view` mostra `SHA256SUMS.txt` e o hash confere.
4. **F4 → F5 → F6**, mesmo ciclo.

### Alertas — o que não quebrar

- **`sdd/` é território do usuário**: o `init` só completa arquivo que falta e nunca sobrescreve (`sdd_faltantes`/`aplicar()` em `bin/sdd-open.sh`). Mudança da F3 em `sdd/bin/report-lint.py`, `sdd/templates/` ou `sdd/playbook.md` só chega a instalação nova — decidir no Brainstorm da F3 se isso basta ou como avisar.
- **A F3 vai mexer em `sdd/`** pela primeira vez nesta frente: os seis exits do `verify-gate.sh`, as fixtures de `sdd/fixtures/` e os 242 testes ficam como estão; `report-lint.py` ganha regra sem perder nenhum contrato dos 14 testes de `tests/test_report_lint.py`.
- **Skill alterada sobe versão** (`sdd-build` 2.0.0, `sdd-release` 2.1.0 hoje): `check-versions.py --base v2.2.2 --base-obrigatoria` reprova no CI e na release. Se o clone local não tiver a tag: `GIT_TERMINAL_PROMPT=0 git fetch -q origin tag v2.2.2`.
- **Literais do G2**: e-mail só em `example.com/.org/.net`; `git@host`, CPF, CNPJ montados em tempo de execução; host de teste em `.invalid`.
- **Contagem de skills** em `tests/test_skill_lint.py` é 16; F3 não acrescenta skill.
- Demais alertas continuam valendo (`GIT_TERMINAL_PROMPT=0`, push em `main` só com OK citando "sdd-open", `MANIFEST.txt` em `LC_ALL=C`, `python3 -B`, `git add` por nome, bash 3.2, sem zsh/symlink, `sync` idempotente, a camada de conversa nas nativas é da F4).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `41c6169` = `origin/main` = tag `v2.2.2`. Não rastreados: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/`.
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.2 · PR #2 merged.
- Fonte da F3: `/Users/robertoduarte/rdd-public/sdd-starter` (main `17c69c4`): `skills/sdd-build/references/aplicar-migration.md`, `skills/sdd-release/SKILL.md` (Fase 2, linhas 203–254).

---

## 2026-10-29 — Decisões e F1 Manutenção (entregue, Release v2.2.1)

### O que foi feito

- **5 decisões do Roberto**, registradas em `## Eventos`: (1) fonte canônica de `sdd-governanca`, `sdd-auditoria-harness`, `sdd-prompt-builder` = open; (2) camada de conversa sempre ligada, sem toggle; (3) Status `✅ ▶️ ⬜ ⏸️ ➖` abre cada resposta, banner vira 1ª palavra do Status, kanban `✅ 🏃 ⬜ ➖` do `RESUMO_ETAPA.md` intacto; (4) descoberta grava nos slots de `sdd/config.yaml`, sem `sdd/ambiente.md`; (5) starter vira distribuição gerada de `.agents/skills/` do open, em frente própria depois da F6.
- **Fluxo SDD da F1** (artefatos não rastreados, nesta worktree): `sdd/features/BRAINSTORM_F1_MANUTENCAO.md` (abordagem A: `tests/` na raiz em unittest, 6 cortes YAGNI, 2 checkpoints), `sdd/features/DEFINE_F1_MANUTENCAO.md` v1.1 (26 ATs EARS, Clarity 14/15), `sdd/features/DESIGN_F1_MANUTENCAO.md` v1.1 (18 arquivos, 5 ADRs), `sdd/reports/BUILD_REPORT_F1_MANUTENCAO.md` (Complete; evidência em `sdd/reports/evidence/F1_MANUTENCAO/`).
- **Código em `main`** (commits `3db1686`, `9db642b`, `f75fbdb`):
  - `tests/apoio.py` (sandbox: git isolado, HOME falso, `PYTHON = sys.executable`, `SDD_TEST_BASH`) + 9 suítes: `test_verify_gate.py` (23), `test_report_lint.py` (14), `test_skill_lint.py` (8), `test_playbook_lint.py` (8), `test_sdd_open.py` (12), `test_check_versions.py` (16), `test_next_version.py` (12), `test_publish_gate_patterns.py` (5), `test_release_workflow.py` (17) = **115 testes**.
  - `scripts/check-versions.py` (versão X.Y.Z por skill, `manifest.json`/`evals/cases.json` coerentes, bump contra `--base`; exit 0/1/64).
  - `scripts/next-version.sh` (bash 3.2; imprime `TAG=`/`NEW=`/`BASE=`; aceita a tag empurrada como argumento; recusa HEAD que não descende da última tag).
  - `.github/workflows/release.yml` (push em `main` nos paths do produto ou tag `v[0-9]+.[0-9]+.[0-9]+`; job `testes` só leitura → job `release` com `needs` e `contents: write`; `git archive` + `sha256sum` + `gh release create`).
  - `.github/workflows/publish-gate.yml` (+ `permissions: contents: read`, `fetch-depth: 0`, steps "Unit tests" e "Version gate").
  - `scripts/publish-gate-patterns.txt` (+ CPF e CNPJ com pontuação, telefone BR sem `+55`).
  - `.agents/skills/sdd-auditoria-harness/SKILL.md` (+ `version: "1.0.0"`, só frontmatter); `CONTRIBUTING.md`; `MANIFEST.txt` (+13).
- **Nenhum script existente mudou**: `git diff 80d7887 -- sdd/fixtures sdd/bin bin scripts/publish-gate.sh` vazio.
- **Sabotagem** (uma por script, revertida com `git checkout`): 6 de 6 deixaram teste nomeado vermelho. A do `report-lint` (desligar "deve funcionar não é prova") só foi pega depois do teste novo `test_declaracao_nega_mesmo_com_log_valido_na_celula` — lacuna real fechada em `9db642b`.
- **Release**: PR https://github.com/robertodiasduarte/sdd-open/pull/1 (CI run 40875642307 verde, 115 testes no Linux, sem skip) → OK do Roberto → push fast-forward → run 40876615567 → https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.1 (Latest), tag em `f75fbdb`, SHA-256 do pacote `636f702580dca80c2c5ca3214af682cdf1a9434b4ea664048f3344d025d950f7`, `shasum -a 256 -c` OK.

### Casos e testes em aberto

- Verify Gate do DEFINE: `bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F1_MANUTENCAO.md` → exit 0 em `f75fbdb` (publish-gate G1–G5 verdes na cópia de `git archive HEAD`, 115 testes OK). Log em `sdd/reports/evidence/F1_MANUTENCAO/AT-001.log`.
- Suíte rodada local no `/usr/bin/python3` 3.9.6 e no `python3` 3.15, com `/bin/bash` 3.2.57; no CI, Python do `ubuntu-latest` com bash 5. Tempo: ~35 s (o `test_sdd_open.py` faz `init` em cada teste, ~22 s).
- `GateInteiro` em `test_publish_gate_patterns.py` é pulado onde não há `gitleaks`; no CI e nesta máquina (gitleaks 8.30.1) ele roda.
- Nenhum caso em aberto na F1.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` ainda apontam para `robertodiasduarte/specgate`; corrigir na próxima release do starter, com OK citando "sdd-starter".)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- F2 Terreno — próxima (ver Próximos passos e o prompt de retomada).
- `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (v4.4.0) roda em Node.js 20, que o GitHub marcou como depreciado (anotação nos runs 40876615494 e 40876615567). Trocar o pin por um SHA de release v5 nos dois workflows; `tests/test_release_workflow.py::test_actions_fixadas_por_sha` continua valendo.
- `ubuntu-latest` migra para Ubuntu 26 a partir de 19/10/2026 (anotação dos runs): observar o próximo CI.
- Risco aceito: com a fila por ref, um push de tag manual e um push de `main` no mesmo commit, quase ao mesmo tempo, podem deixar duas tags no commit (ex.: `v2.2.2` e `v2.3.0`). Recomendação para minor/major: empurrar a tag **depois** que a run de `main` terminar.
- Risco aceito: o job `testes` da release não repete os checks inline de fixtures/smoke do `publish-gate.yml` (a suíte cobre o mesmo contrato); mover tudo para um script fica para quando o `publish-gate.yml` puder mudar.
- Guia do aluno do starter: a worktree `sdd-starter-linguagem-aluno` foi removida, mas o arquivo sobreviveu **não rastreado** em `/Users/robertoduarte/rdd-public/sdd-starter/docs/guia-do-aluno.pt-BR.md` (494 linhas, conferido em 29/10). Entrada da F6; um `git clean` naquele checkout o apaga — copiar ou commitar no starter (com OK citando "sdd-starter") antes.

### Próximos passos

1. **F2 Terreno — brainstorm** com `sdd-brainstorm`, gravando `sdd/features/BRAINSTORM_F2_TERRENO.md`. Decisões a levar: onde moram os testes portados (`tests/` na raiz, como na F1, ou `.agents/skills/<skill>/tests/` como no starter — o `sync` copia a pasta da skill para o projeto do usuário e o CI só roda `-s tests`); como o `doctor` chama o `checar.sh` (`doctor --repo`); pré-voo `checar.sh --frente` e matriz de 12 achados na `sdd-new-session` 1.0.0 do open; descoberta que grava `project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd`. Pronto quando: abordagem confirmada, YAGNI, 2 checkpoints.
2. **F2 — define, design, build**: `DEFINE_F2_TERRENO.md` com `verify_gate` `kind: test` e o mesmo `cmd` da F1; manifest com `MANIFEST.txt`. Pronto quando: `verify-gate.sh --strict` sai 0, `report-lint.py` sai 0 e 1 sabotagem por script portado no BUILD_REPORT.
3. **F2 — release**: PR, CI verde, OK citando "sdd-open", push em `main` → Release automática (`v2.2.2`) ou tag manual `v2.3.0` empurrada depois da run de `main`. Pronto quando: `gh release view` mostra a Release com `SHA256SUMS.txt` e o hash confere.
4. **F3 → F4 → F5 → F6**, mesmo ciclo.

### Alertas — o que não quebrar

- **Push em `main` publica Release sozinho** quando toca `.agents/skills/**`, `bin/**`, `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/playbook.md`, `sdd/config.example.yaml` ou `AGENTS.md.tmpl`. Push em `main` só com OK explícito citando "sdd-open", depois de PR com CI verde.
- **Skill alterada sobe `metadata.version`**: `python3 scripts/check-versions.py --base v2.2.1 --base-obrigatoria` reprova no CI e na release.
- **Nenhum arquivo da árvore pode conter literal que case com `scripts/publish-gate-patterns.txt`**: os testes do starter que a F2 vai portar têm `git@github.com` (3 linhas), e-mails em `exemplo.invalid`/`exemplo.com` (16 — o gate só isenta `example.com/.org/.net`) e o CPF literal `000.000.000-00` em `skills/sdd-higiene-dado/tests/test_alarme.py:164`. Trocar para `example.com` e montar amostras por concatenação em tempo de execução (padrão de `tests/test_publish_gate_patterns.py`).
- **`python3 -B` sempre** e `git add` por nome de arquivo: o open não tem `.gitignore`, e um `__pycache__` ou um doc de `sdd/features/` commitado reprova o G3.
- Demais alertas da etapa anterior continuam valendo (`GIT_TERMINAL_PROMPT=0`, MANIFEST allowlist, bash 3.2, `skill-lint` ≤ 1024, `sync` idempotente, só a camada de conversa muda nas skills nativas na F4, árvore `sdd/features|reviews|reports|releases|handoffs`).

### Onde está o trabalho

- Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter`, branch `feat/incorporar-starter` em `f75fbdb` = `origin/main` = tag `v2.2.1`. Não rastreados: `sdd/features/`, `sdd/handoffs/`, `sdd/reports/`.
- Release: https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.2.1 · PR #1 merged.
- Fonte da F2: `/Users/robertoduarte/rdd-public/sdd-starter` (main em `17c69c4`): `skills/sdd-checar-ambiente` 1.2.0 (`scripts/checar.sh` 446 linhas, `tests/test_checar.py` 53 testes), `skills/sdd-higiene-dado` 1.1.0 (`scripts/alarme.sh` 79 + `scripts/pre-commit.sh` 120, `tests/test_alarme.py` 28, `evals/`, `manifest.json`, `CHANGELOG.md`, `references/`), `skills/sdd-iniciar-repo` 1.1.0 (`scripts/inventario.sh` 191, `tests/test_inventario.py` 24), `skills/sdd-new-session` 1.3.0 (pré-voo e matriz). Nenhum `grep -P`, `readlink -f`, `declare -A` ou `mapfile` nesses scripts.

---

## 2026-10-29 — Avaliação do starter e abertura da frente

### O que foi feito

- **Comparativo lado a lado** sdd-starter v1.5.15 (commit `17c69c4`, worktree `/Users/robertoduarte/rdd-worktrees/sdd-starter-linguagem-aluno`) × sdd-open commit `80d7887` (24/10/2026, `/Users/robertoduarte/rdd-public/sdd-open`). Números medidos: starter 15 skills, 4.532 linhas de SKILL.md, 2.977 linhas de scripts, 144 funções de teste em 6 suítes, release v1.5.15 publicada em 27/10 com 15 zips; open 13 skills, 1.721 linhas de SKILL.md, 1.993 linhas de scripts, 0 testes unitários, nenhuma Release no GitHub.
- **Três skills com o mesmo nome divergiram em todos os arquivos**: `sdd-governanca` (starter 1.0.1 × open 2.1.0), `sdd-auditoria-harness` (1.0.0 × sem versão no open), `sdd-prompt-builder` (1.0.0 × 2.0.0). Nas três, o open é o mais novo.
- **Avaliação profunda** gravada em `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md`: tabela de 17 componentes (o que faz bem · já existe no open? · entra como), anatomia dos 10 itens da camada "Como falar com o aluno" (fonte: `sdd/DEFINE_LINGUAGEM_ALUNO.md` do starter, Clarity 14/15), tabela de encaixe com o que o open já tem (banner `🧠 FASE`, `RESUMO_ETAPA.md` com kanban ✅ 🏃 ⬜ ➖, regra "só existe se N ≥ 1", scripts terminando em `RESULTADO:`), 5 decisões e 6 frentes com gate.
- **Fatos do open que condicionam o trabalho**, conferidos no código: `scripts/publish-gate.sh` G3 é allowlist por `MANIFEST.txt` — todo arquivo da árvore precisa estar declarado; `sdd/bin/skill-lint.py` exige `description` ≤ 1024 caracteres e avisa acima de 500 linhas; `.github/workflows/publish-gate.yml` roda gitleaks, fixtures do gate (exits 5/0/64 e `--strict`), self-test do playbook, skill-lint, smoke do gerador (init idempotente, `sync --check`) e proíbe zsh e symlink; o open não tem `.gitignore`.
- **Worktree aberta**: `git worktree add /Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter -b feat/incorporar-starter origin/main` → HEAD `80d7887`, branch rastreando `origin/main`. Pastas `sdd/features/` e `sdd/handoffs/` criadas, **não rastreadas**.

### Casos e testes em aberto

- Nenhum teste foi executado nesta sessão; o trabalho foi de leitura e análise. Os números de teste acima vêm de `grep -c "def test_"` nas 6 suítes do starter.
- Verificação pendente de duas afirmações da avaliação: (a) o starter diz que o `validate_design.py` cruza o inventário LLM com o manifest — conferido no código (`validate_design.py` linhas 174–186); (b) o open "não tem procedimento de migration" — conferido por grep em `.agents/skills/sdd-build/SKILL.md` e `sdd/config.example.yaml` (só `layers.sql` e `deploy.drift_check_cmd`).
- O guia do aluno do starter (`docs/guia-do-aluno.pt-BR.md`, 494 linhas) existe só na worktree `sdd-starter-linguagem-aluno`, sem commit; é entrada da F6 e pode sumir se aquela worktree for removida — copiar antes.

### Pendências

**🐛 Bug fix** — o que ficou quebrado, parcial ou com comportamento errado conhecido:

- nenhuma no sdd-open. (Fora desta frente, no starter: `README.md` e `docs/quickstart*.md` apontam para `robertodiasduarte/specgate`, repositório que não existe; o nome atual é sdd-open. Corrigir na próxima release do starter, com OK citando "sdd-starter".)

**✨ Feature improvement** — o que é incremento planejado, melhoria ou próxima etapa de escopo:

- Decisões 1–5 (ver próximos passos).
- F1 Manutenção: `tests/` para `bin/sdd-open.sh` (639 linhas), `sdd/bin/verify-gate.sh` (197), `report-lint.py`, `skill-lint.py`, `playbook-lint.sh`; `scripts/check-versions.py` portado e linha de identificação nas 13 skills; workflow de auto-release com 2 jobs e `SHA256SUMS.txt`; `sdd/bin/design-lint.py` e `handoff-lint.py` com `gate.sh` que aceita o exemplo e rejeita fixtures ruins; padrões de PII brasileira (CPF 11 dígitos, `+55`, e-mail pessoal) em `scripts/publish-gate-patterns.txt`; `doctor` conferindo segredo já no histórico (`git ls-files` para `.env`, `.pfx`, `.p12`, `.pem` com `PRIVATE KEY`).
- F2 Terreno: portar `sdd-checar-ambiente` 1.2.0 (`scripts/checar.sh` 446 linhas, 53 testes), `sdd-higiene-dado` 1.1.0 (`alarme.sh`, `pre-commit.sh` 120 linhas, 28 testes, evals 8 casos), `sdd-iniciar-repo` 1.1.0 (`inventario.sh` 191 linhas, 24 testes) para `.agents/skills/`, com a seção do aluno já nos símbolos decididos; `sdd-new-session` do open (1.0.0) ganha o pré-voo via `checar.sh --frente`, a matriz de 12 achados e a descoberta que preenche `project.default_branch`, `editor`, `worktree_base`, `project.test_cmd`, `project.lint_cmd` em `sdd/config.yaml`.
- F3 Build e Release: `references/aplicar-migration.md` do starter em `.agents/skills/sdd-build/references/`; seção `## Migrations aplicadas` em `sdd/templates/BUILD_REPORT_TEMPLATE.md` e regra em `sdd/bin/report-lint.py` (migration em Files Created sem linha arquivo · projeto nome e ref · data · prova por leitura ⇒ falha); bullet `LM-004` no `## Sempre` de `sdd/playbook.md` ("exit 0 não prova migration; prova é ler de volta"); bloco único do "go" na `sdd-release` com os campos do starter (O que sobe em palavras · O que muda em produção · O push publica sozinho? · O deploy espera os testes? lido de `.github/workflows/*`, `continue-on-error`/`|| true` contam como não · Banco · Verificações).
- F4 Conversa: seção `## Como falar com o aluno` curta (≈32 linhas, padrão do Grupo 2 do starter) mais `references/como-falar.md` (glossário · Status preenchido · exemplo completo) nas 13 skills do open, inclusive `sdd-governanca`, `sdd-prompt-builder`, `sdd-auditoria-harness`, `sdd-iterate`, `sdd-playbook`, `sdd-ux-review`; glossário dos termos do open (exits 0/2/3/4/5/64, landmine, ledger, drift, slot vazio, adaptador e sync, waiver, vendor, contexto fresco, iterate); `skill-lint.py` passa a exigir a seção e o arquivo; diff por skill no BUILD_REPORT provando que nenhum comando, condição ou ordem de passo mudou.
- F5 Conhecimento: portar `sdd-kb` 2.1.0 (`validate_kb.py`, `kb_normativo.py`, `gate.sh`, assets e exemplos) e ligar o `RULE_MAP.md` ao Verify Gate (coluna Teste = o `cmd` do gate); entrevista de público e referências do `ux-review-builder` como entrada opcional da `sdd-ux-review`.
- F6 Docs: "nunca siga para a próxima fase com um documento que você não leu" e a tabela onde-roda → ferramenta no `docs/pt-BR/quickstart.md`; guia do aluno adaptado ao open em `docs/pt-BR/`; seção "Por que cada regra existe" nas skills de fase.
- Risco aceito por ora: o modo `briefs`, o playbook ACE-lite e o veredito graduado ficam como estão; a camada de conversa não os remove, só os explica.

### Próximos passos

1. **Colher as 5 decisões do Roberto**, uma pergunta por vez, com recomendação primeiro — (1) fonte canônica das 3 skills compartilhadas = open; (2) camada de conversa ligada por padrão, sem toggle; (3) símbolos do Status unificados em `✅ ▶️ ⬜ ⏸️ ➖` e banner virando a primeira palavra do Status; (4) descoberta de ambiente grava nos slots de `sdd/config.yaml`, sem `sdd/ambiente.md`; (5) o starter vira distribuição gerada a partir do open. Pronto quando: as 5 respostas estão registradas em `## Eventos` deste arquivo.
2. **F1 Manutenção — brainstorm** com a skill `sdd-brainstorm`, entrada `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md` seção 3 linha F1, gravando `sdd/features/BRAINSTORM_F1_MANUTENCAO.md`. Pronto quando: o arquivo existe com abordagem confirmada, YAGNI e 2 checkpoints.
3. **F1 — define, design, build** nesta worktree: `sdd/features/DEFINE_F1_MANUTENCAO.md` com `verify_gate` `kind: test`, `cmd: "bash scripts/publish-gate.sh . && python3 -m unittest discover -s tests -p 'test_*.py'"`; `DESIGN_F1_MANUTENCAO.md` com manifest que inclui `MANIFEST.txt`; build em modo default. Pronto quando: `sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F1_MANUTENCAO.md` sai 0 e `sdd/reports/BUILD_REPORT_F1_MANUTENCAO.md` passa em `python3 sdd/bin/report-lint.py`.
4. **F1 — release**: PR de `feat/incorporar-starter` para `main`, CI `publish-gate` verde, push em `main` só com OK do Roberto citando "sdd-open". Pronto quando: a tag e a Release com `SHA256SUMS.txt` existem em `https://github.com/robertodiasduarte/sdd-open/releases`.
5. **F2 → F3 → F4 → F5 → F6**, cada uma repetindo os passos 2–4 com seu próprio `{F}` (`F2_TERRENO`, `F3_BUILD_RELEASE`, `F4_CONVERSA`, `F5_CONHECIMENTO`, `F6_DOCS`). F2 e F3 antes de F4 porque as skills portadas já chegam com a seção do aluno. Pronto quando: os 6 critérios da ficha estão satisfeitos.

### Alertas — o que não quebrar

- **Todo comando que fala com o remoto roda com `GIT_TERMINAL_PROMPT=0`** (`fetch`, `push`, `ls-remote`, `gh`). Nunca deixar o git pedir senha no terminal do agente.
- **Push em `main` só com OK explícito do Roberto nomeando "sdd-open"** no mesmo turno — mesma regra que vale para o sdd-starter. PR + CI verde antes.
- **`MANIFEST.txt` é allowlist**: `scripts/publish-gate.sh` G3 reprova qualquer arquivo da árvore que não esteja declarado. Cada arquivo novo (skill, teste, referência, workflow) entra no `MANIFEST.txt` no mesmo commit. Os documentos de trabalho em `sdd/features/` e `sdd/handoffs/` desta frente ficam **fora do commit** e reprovam o gate local — rodar o gate sobre uma cópia limpa (`git archive HEAD | tar -x -C <tmp>`) ou movê-los antes.
- **Compatibilidade declarada do open**: bash 3.2, sem `declare -A`, sem zsh, sem symlink, variável sempre entre chaves antes de texto não-ASCII; o CI reprova shebang zsh e symlink. Os scripts do starter (`checar.sh`, `alarme.sh`, `inventario.sh`) já rodam em bash 3.2 do macOS, mas o `grep -P` e o `readlink -f` não existem lá — conferir ao portar.
- **`skill-lint.py`**: `description` ≤ 1024 caracteres (medido no starter: `sdd-checar-ambiente` 766, `sdd-higiene-dado` 859, `sdd-iniciar-repo` 978, `sdd-kb` 911 — todas passam, mas a da `sdd-iniciar-repo` tem só 46 de folga), `name` igual à pasta, corpo ≤ 500 linhas de preferência.
- **`sync` precisa continuar idempotente** (smoke do CI: `init --yes` + `sync --yes` + `git status --porcelain` vazio + `sync --check`). Skills novas em `.agents/skills/` entram no `sync` automaticamente; conferir que o cabeçalho `sdd-open:generated` não quebra `tests/*.py` copiados.
- **Só a camada de conversa muda nas skills nativas do open** (F4): comandos, condições, ordem dos passos, slots do config e exits ficam idênticos, provado por diff.
- **O open continua com a árvore `sdd/features`, `reviews`, `reports`, `releases`, `handoffs`** — não adotar a pasta plana do starter.
- **Fora de escopo:** redesenhar a CLI `init/sync/doctor` ou o `config.yaml`; mexer no `verify-gate.sh` além de testes; alterar o sdd-starter nesta frente (exceto o que a decisão 5 determinar, em frente própria); modo `briefs`; curadoria do playbook além do `LM-004`; teste no Windows.

### Onde está o trabalho

- Worktree: `/Users/robertoduarte/rdd-worktrees/sdd-open-incorporar-starter` — branch `feat/incorporar-starter`, base `origin/main` em `80d7887`, remoto `https://github.com/robertodiasduarte/sdd-open.git`.
- Checkout principal do open: `/Users/robertoduarte/rdd-public/sdd-open` (não trabalhar nele).
- Avaliação de entrada: `sdd/features/AVALIACAO_STARTER_PARA_OPEN.md` nesta worktree (cópia de `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-starter-linguagem-aluno/d33e2c2a-ce4a-4569-9547-7611306204d2/scratchpad/avaliacao-starter-para-open.md`).
- Fonte do que vai ser portado: sdd-starter v1.5.15 — tag `v1.5.15` em `https://github.com/robertodiasduarte/sdd-starter`; localmente em `/Users/robertoduarte/rdd-worktrees/sdd-starter-linguagem-aluno` (commit `17c69c4`; pode ser removida — nesse caso `git -C /Users/robertoduarte/rdd-public/sdd-starter pull` e usar `main`). O guia do aluno (`docs/guia-do-aluno.pt-BR.md`) só existe nessa worktree, sem commit.
- Skills do fluxo SDD usadas nesta frente: as `sdd-*` globais em `/Users/robertoduarte/.claude/skills/` (starter v1.5.15); artefatos gravados no layout do open (`sdd/features/`, `sdd/reports/`, `sdd/handoffs/`), não rastreados.
