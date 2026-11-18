# BRAINSTORM: F15 Substituição do SDD privado pelo Open

> Sessão exploratória para fixar a intenção e o caminho antes dos requisitos

## Metadata

| Attribute | Value |
|---|---|
| Feature | F15_SUBSTITUICAO |
| Date | 2026-11-07 |
| Author | brainstorm-agent (sessão 13 da INCORPORAR_STARTER, worktree `sdd-open-f14-drive`) |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** quadro "F15 Substituição do SDD privado pelo Open (parâmetro P4)" de `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` (seção 8): "O repositório privado (`~/RDD/Wordpress`) passa a usar o Open instalado pelo `init`, e o SDD privado deixa de existir como código próprio." Pedido do Roberto para esta sessão: explicação para leigo, prós e contras, recomendação; a decisão é dele.

**Context Gathered:**
- Fato (plano, seção 0): o P4 só se fecha com `doctor` ✅ no privado, uma feature real do RDD de ponta a ponta pelo Open e as pastas do SDD privado fora do git. F7–F14 já levaram o mecanismo (`v2.2.8` a `v2.7.0`).
- Medido em `origin/main` do privado = `022c14aa7` (2026-11-07), só leitura: `.claude/commands/workflow` 8 arquivos; `.claude/agents` 12 papéis + 1 modelo; `sdd-public` 80; `scripts/` 244 itens no 1º nível; `.claude/kb/` 50 pastas; `.githooks/` com `pre-commit`, `pre-push` e 3 ganchos do Claude; `scripts/gates/` mistura scripts do método com dezenas de gates de feature do site; `scripts/port-to-public.sh`, `scripts/sdd-public-allowlist.tsv` e `scripts/gates/{gate-sdd-open-s1,gate-sdd-prompt-builder,audita-schema-gate}.sh` existem. O `/release` privado é `.claude/commands/release.md` (645 linhas), não `workflow/`.
- Medido: **29 frentes de feature abertas** em worktrees (31 linhas no `git worktree list`, com o checkout principal e uma sobra de release em `/tmp`).
- Medido: o checkout principal está 2.286 commits atrás de `origin/main`, com os mesmos 4 arquivos modificados da D7 (3 de KB e 1 partial do plugin).
- Medido: o repositório `robertodiasduarte/sdd-open` é **público**; a branch `docs/incorporar-starter` também.
- Inferência: frente antiga cujo `/release` monta a publicação a partir do `main` quebraria se os scripts do SDD privado sumissem do `main` antes de ela fechar.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | privado: `sdd/config.yaml`, `sdd/hooks/`, `sdd/bin/`, `.agents/skills/`, `AGENTS.md` (gerados pelo `init`); Open: `sdd-release` (3 slots novos de extensão) | a F15 tem execução no privado e uma entrega pequena no Open (o ponto de extensão), com release própria do Open |
| Relevant KB Domains | privado: `.claude/kb/` (50 pastas), fora do Open | só a KB que a feature da prova usar vai para `sdd/kb/` nesta frente |
| IaC Patterns | deploy por rsync (Hostinger) num workflow do GitHub Actions; Supabase (edge functions e migrations); `core.hooksPath = .githooks` | `deploy.cmd`, `deploy.workflow`, `test_cmd` (deno), `drift_check_cmd`, `layers` (edge/sql/wp-content); ganchos precisam conviver numa pasta só |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | O que acontece com as 29 frentes abertas durante a troca? | Convivência até o fim: o Open entra ao lado; frente nova nasce no Open, frente antiga termina no fluxo velho; o SDD privado só sai quando nenhuma frente aberta depender dele | a remoção vira a última fase; entra uma conferência de quais frentes ainda usam o fluxo velho; o `/release` antigo fica disponível como saída de emergência |
| 2 | Que tipo de feature faz a prova de ponta a ponta? | Uma feature nova, pequena, que toque pelo menos 2 camadas | prova deno, deploy e revisão com risco baixo; a migration só fica provada se uma das camadas for SQL; a feature concreta fica para o início da fase 2 |
| 3 | Onde moram os documentos SDD da F15? | Dividir: este brainstorm na branch `docs/` do Open; define, design, relatório de build e evidências da execução no privado, em `sdd/` | os gates do Open acham os documentos onde o código muda; detalhe de infraestrutura da RDD não vai para repositório público |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | N/A | 0 | — |
| Output examples | registro da release `v1.486.0` do privado (`.claude/sdd/releases/EXEMPLO_BAIXAR_NFSE_PAGINA/s1_1.486.0.yaml`, `origin/main`) | 1 | publicação de 2026-11-07, uma camada (plugin) |
| Ground truth | o mesmo registro | 1 | o que o `sdd-release` instalado precisa reproduzir: Verify Gate na pasta de publicação, drift do Supabase, revisão externa com 3 engines, avaliador, ledger de achados, bump do plugin, smoke visual opcional, conferência no ar por gate da feature |
| Related code | `.claude/commands/release.md` (passos 6b, 7b e 10b: `scripts/a11y/smoke-release.mjs derivar/antes/esperar/depois`) | 1 | forma do ponto de extensão do smoke visual |

**How samples will be used:**
- O registro da `v1.486.0` é o gabarito da fase 3: cada linha dele (gate, drift, revisão, avaliador, smoke, versão) precisa de equivalente no `sdd-release` instalado, ou de um motivo registrado para não ter.
- Ele revelou 2 diferenças de regra, decididas abaixo: a pré-autorização ("release previamente autorizado quando tudo ok") e os vermelhos herdados de outras frentes no `main`.

## Approaches Explored

### Approach A: Por fases, a release por último — Recomendada

**Description:** fase 1 instala o Open e migra o conteúdo da RDD; fase 2 constrói a feature da prova pelo Open (brainstorm a build); fase 3 publica a mesma feature pelo `sdd-release` do Open; fase 4 remove o SDD privado quando nenhuma frente antiga depender dele.

**Pros:**
- cada fase termina verde antes da seguinte; o deploy, o passo de maior risco, entra com o resto provado;
- se a fase 3 falhar, a feature sai pelo `/release` antigo, que convive até a fase 4.

**Cons:**
- mais sessões: 4 a 5, mais a espera da fase 4.

**Why Recommended:** separa problema do Open, da migração e da feature; segue a sugestão do plano (define primeiro, release por último) e casa com a convivência escolhida na pergunta 1.

### Approach B: De uma vez

**Description:** instalar, migrar e levar a feature da prova até a release na mesma sequência, sem paradas de conferência; remoção no fim.

**Pros:**
- 2 a 3 sessões.

**Cons:**
- falha na release mistura causas, e a correção é feita com o site em jogo.

### Approach C: Em sombra

**Description:** a feature da prova roda pelos dois métodos ao mesmo tempo, fase por fase, comparando documentos e gates antes de desligar o privado.

**Pros:**
- mostra exatamente o que o Open faz de diferente.

**Cons:**
- trabalho dobrado; as duas releases não podem publicar o mesmo código, então a sombra para antes do deploy; 5 a 7 sessões.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A — por fases, a release por último |
| User Confirmation | Roberto, 2026-11-07, na conversa: "A — Por fases, a release por último (recomendada)" |
| Reasoning | menor risco para o site, cada fase com prova própria, e saída de emergência pelo `/release` antigo durante a convivência |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Convivência até o fim; remoção só sem frente antiga dependente, **sem data-limite** (não informada; a remoção espera a última frente fechar) | nada quebra no meio de uma frente | corte numa data; faxina das frentes antes |
| 2 | Prova com feature nova, pequena, de 2 camadas, escolhida no início da fase 2 | prova deno, deploy e revisão com risco baixo | 3 camadas de uma vez; recomeçar uma frente antiga no Open |
| 3 | Documentos divididos: brainstorm na branch `docs/` (pública); execução no privado, em `sdd/` | gates do Open precisam dos documentos no repositório do código; detalhe da RDD fora do público | tudo na `docs/`; tudo no privado |
| 4 | Abordagem A, por fases | ver Selected Approach | B de uma vez; C em sombra |
| 5 | Ponto de extensão do smoke visual: **3 slots genéricos** no `sdd/config.yaml` do Open, um por momento da release (antes do OK, antes do push, depois do deploy), com saídas combinadas 0 ok · 2 reprovou · 10 nada a medir; o privado aponta os 3 para `scripts/a11y/` | serve a qualquer projeto; preserva a medição de antes e depois do passo 6b/7b/10b de hoje | um slot só, depois do deploy |
| 6 | Autorização: o privado segue a regra do Open, **um OK por publicação** no bloco do OK; o Open não ganha pré-autorização | uma pergunta só por release já existe; pré-autorização mudaria a regra para todo usuário | slot de pré-autorização no Open |
| 7 | Vermelho herdado de outras frentes: usar a linha de base que o Open já tem (`gate-baseline.sh`); conferir na fase 1 se cobre os gates de feature | mecanismo existente, sem regra nova | mecanismo novo |
| 8 | D7: na fase 1, ler o diff dos 4 arquivos, guardá-los num patch fora do git, mostrar ao Roberto e, com o OK dele, sincronizar o checkout principal | nada se perde e o espelho volta a acompanhar o `origin/main` | deixar como está e nunca usar o checkout principal |
| 9 | Pasta de trabalho da execução: pelo `/new-session` do privado, worktree `~/rdd-worktrees/f15-substituicao`, branch `feat/f15-substituicao` a partir do `origin/main`, aberta só no começo da próxima sessão e com o OK do Roberto | o Open ainda não está instalado lá; é a ferramenta de hoje | `git worktree add` à mão |
| 10 | A ponte `sdd-public/` sai já na fase 1 (`sdd-public/`, `port-to-public.sh`, `sdd-public-allowlist.tsv`, `gate-sdd-open-s1.sh`, `gate-sdd-prompt-builder.sh`) | nenhuma frente usa (D9 do PORTE: aposentar) | esperar a fase 4 |
| 11 | Ganchos de commit numa pasta só durante a convivência: `sdd/hooks/` do Open chama as guardas do `.githooks/` | o git aceita uma pasta de ganchos por vez | duas pastas |
| 12 | As cópias `sdd-*` de `~/.claude/skills/` (e `anthropic-skills:sdd-*`) regeneradas do Open na fase 1 (D6) | os nomes colidem com as skills instaladas pelo `init` | manter as cópias do starter |
| 13 | Anexo C: `model:` por fase, `/fewer-permission-prompts` e a memória do Roberto somem do método sem substituto; landmines LM-nnn vão para o `sdd/playbook.md` do privado; patterns e invariantes, para os lugares do Open | o Open escolhe modelo fora do texto de skill; a memória continua memória | virar slot |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Mover os documentos antigos de `.claude/sdd/` para `sdd/` | só frente nova usa `sdd/`; mover a história não prova nada | Yes |
| Mover as 50 KBs para `sdd/kb/` | só a KB que a feature da prova usar; o resto na fase 4 ou depois, porque o `CLAUDE.md` e muitos documentos citam `.claude/kb/` | Yes |
| Buckets WARM/COOL e lentes por público em `sdd/contexto/` ou slot de UX | ficam onde estão, salvo se a feature da prova passar por revisão de UX | Yes |
| Medir custo e benefício dos revisores | é a F19 | Yes |
| Alerta e prevenção de segurança do e-book | são F18 e F20 | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: as 4 fases, o que cada uma entrega e o que fica de fora | Yes | "sim" | No |
| Checkpoint 2: ordem, dependências, falhas e as 5 decisões (smoke, autorização, vermelho herdado, D7, pasta de trabalho) | Yes | "todas A, como recomendado"; data-limite não informada | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O RDD mantém um SDD próprio (comandos, agentes, 26 scripts, ganchos e a ponte `sdd-public/`) ao lado do Open, que já tem o mesmo mecanismo; duas fontes divergem, e o privado deve passar a ser um usuário do Open instalado pelo `init`, sem quebrar as 29 frentes em andamento.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Roberto, que constrói o RDD com agentes | dois métodos para manter; correção feita num não chega ao outro |
| As frentes em andamento no privado | não podem quebrar no meio por causa da troca |
| Usuários do Open | o ponto de extensão da release precisa servir a qualquer projeto, não só ao RDD |

### Success Criteria (Draft)

- [ ] Fase 1: no privado, `bash bin/sdd-open.sh doctor` sai ✅ sem ⚠️; o `git commit` passa pelos ganchos do Open e do `.githooks/` numa pasta só; a ponte `sdd-public/` fora do git.
- [ ] Fase 2: a feature da prova (nova, pequena, 2 camadas) tem DEFINE, DESIGN e BUILD_REPORT em `sdd/` do privado, com Verify Gate verde, `report-lint` 0, avaliador e revisão adversarial (`--conferir` CONFERE).
- [ ] Fase 3: a mesma feature publica pelo `sdd-release` do Open com os 3 slots de extensão chamando `scripts/a11y/`, e `deploy-do-sha.sh` sai 0 sobre o commit publicado.
- [ ] Fase 4: com zero frente antiga dependente, `git ls-files .claude/commands/workflow .claude/agents scripts/sdd-fluxo.sh sdd-public` vazio; `CLAUDE.md` aponta para o `AGENTS.md`.
- [ ] No Open: os 3 slots de extensão com teste dos 2 lados e release própria; `publish-gate.sh` verde (nada da RDD no Open).
- [ ] Esforço: 4 a 5 sessões até a fase 3; a fase 4 depende das frentes antigas (sem data, TBD).

### Constraints Identified

- O privado é só leitura até o OK do Roberto; abrir a pasta de trabalho de lá é a primeira alteração.
- A `v2.7.1` do Open sai antes da fase 1.
- Específico da RDD não viaja para o Open (Anexo C); o repositório `sdd-open` e a branch `docs/` são públicos.
- O `/release` antigo continua disponível durante a convivência.
- A F18 e a F20 também tocam o `sdd-release`: não fazem par com a entrega do Open desta frente.

### Out of Scope (Confirmed)

- Mover documentos antigos de `.claude/sdd/` e as KBs que a prova não usar.
- Buckets WARM/COOL e lentes por público, salvo se a prova passar por UX.
- F16 a F20; regenerar o sdd-starter (F17).

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 3 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 5 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
