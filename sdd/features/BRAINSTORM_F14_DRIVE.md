# BRAINSTORM: F14 Drive e orquestração

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F14_DRIVE (2ª entrega da F14; a 1ª foi a F14_PLAYBOOK, `v2.6.0`) |
| Date | 2026-11-05 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Leia e execute o prompt em sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md (sessão 12 da frente INCORPORAR_STARTER: F14_DRIVE, 2ª entrega da F14, Release v2.7.0). A chave da OpenRouter para a revisão adversarial real está em ~/.config/rdd-eval.env (OPENROUTER_API_KEY): só no ambiente, nunca em arquivo."

O prompt da sessão pede O1 (skill `sdd-drive` + `sdd/bin/sdd-drive.sh`), O2 (raio de impacto por superfície), O3 (`sdd/bin/deploy-do-sha.sh`), O4 (`sdd/bin/sdd-archive.py`), o slot `drive.max_rounds`, a saída da linha `sdd-drive` do roadmap e, antes disso, a curadoria `252d351` com os 5 achados da rodada 4.

**Context Gathered:**

Fatos conferidos nesta sessão:
- Worktree `sdd-open-f14-drive`, branch `feat/f14-drive`, nascida de `8a320e9` = tag `v2.6.0`; 18 skills, 1.411 testes no piso, `MANIFEST.txt` com 439 linhas (prompt da sessão).
- Tarefa 1 entregue: `aabc4a3` (curadoria) e `3331b6c` (R1 a R5 da rodada 4 e o teste do outro lado do R5). Sabotagens: 9 de 9 derrubam teste, inclusive a que estava viva (`sdd/reports/evidence/F14_DRIVE/sabotagens-tarefa1.log`).
- Fontes do privado lidas do `origin/main` dele (`a029cf455`), sem alterar nada: `.claude/commands/workflow/drive.md`, `.claude/sdd/workflows/sdd-driver.js` (233 linhas), `scripts/sdd-archive.py` (177), `scripts/release/deploy-do-sha.mjs` (338), `.claude/commands/release.md` (0b, 11, 15b).
- O driver do privado é um script da ferramenta `Workflow` do Claude Code, com `budget.remaining()`; nada disso existe fora do Claude Code. No privado, 1 rodada = 1 tarefa, com limite 8.
- O `sdd-fluxo.sh` já estabelece o padrão "script decide, agente faz": `despachar` sai 40 `AGUARDANDO_HUMANO` quando o agente não abre sessão fresca sozinho.
- O modo ralph (`.agents/skills/sdd-build/references/modos-e-retry.md`) já grava `sdd/reports/progress/PROGRESS_{F}.md`; a ação da volta é "faça a próxima tarefa pendente, commite atomicamente, atualize o PROGRESS, pare".
- O item 10 da `sdd-release` traz em texto a mesma lógica do `deploy-do-sha`: run do SHA na branch padrão, `cancelled` com substituto que contém o commit (`git merge-base --is-ancestor`), nunca `gh run rerun`, `gh workflow run --ref` só com `workflow_dispatch` no `on:`.
- `avaliador-guard.sh` sai 1 nesta worktree por causa dos documentos SDD que a regra deixa fora do commit; já tem `--permitir <prefixo>`.
- Codex CLI 0.163 conferido agora: `Your workspace is out of credits`. O caminho do Codex com modelo da OpenRouter está medido (`codex-via-openrouter`, memória).
- `.github/workflows/release.yml` não tem `workflow_dispatch`; `gh run list --commit` devolve também o run da tag, com `headBranch` = a tag (`v2.6.0`).

Inferências (a confirmar no Design):
- O estado do drive cabe num arquivo em `sdd/reports/progress/`, ao lado do `PROGRESS_{F}.md`.
- `--dry-run` não precisa rodar o `cmd` do gate: basta o `verify-gate.sh --print` e parar ali.
- A guarda do avaliador aceita **não rastreado** só nas pastas de documento de `sdd/`; arquivo rastreado modificado segue recusado.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `.agents/skills/sdd-drive/`, `sdd/bin/sdd-drive.sh`, `sdd/bin/deploy-do-sha.sh`, `sdd/bin/sdd-archive.py`, `.agents/skills/sdd-release/SKILL.md` (0b, 10, 11), `sdd/config.example.yaml`, `docs/` + `docs/pt-BR/`, `sdd/bin/avaliador-guard.sh`, `sdd/bin/playbook-curator.sh`, `tests/` | skill nova muda contagens de 18 para 19; todo arquivo novo entra no `MANIFEST.txt`; toda skill tocada sobe de versão |
| Relevant KB Domains | nenhum (`sdd/kb/` não existe neste repositório) | a linha de KB Domains do DEFINE fica `nenhum` |
| IaC Patterns | CI em `ubuntu-latest` e `macos-latest`; Release no push de `main` que toca `sdd/bin/**`, `.agents/skills/**`, `sdd/config.example.yaml` e outros; `testes` com teto de 25 min (17m41s na última) | piso Python 3.9 e bash 3.2; no Ubuntu sobra pouco: os testes novos precisam ser enxutos |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | Quanto do `sdd-drive` entra na `v2.7.0`? | inteiro (recomendada) | voltas com limite, `--resume`, tabela de motivos, DRIVE_REPORT e barreira; a linha do roadmap sai |
| 2 | O que conta como 1 rodada? | a passada inteira (recomendada) | 1 rodada = construir tudo o que falta, uma tarefa por sessão nova, e rodar o gate; `drive.max_rounds: 3` significa 3 tentativas de ficar verde, independe do tamanho da feature |
| 3 | Quais pendências entram? | só as 2 do drive (recomendada) | a guarda do avaliador e a contagem falsa da colheita (L10) entram; F5, F6, F7, a guarda de F9, L7, N-L9, N-L10 e o resto de N-L11 seguem abertas |
| 4 | Quem faz o 2º revisor e a prova fora do Claude, sem créditos do Codex? | DeepSeek pela OpenRouter (recomendada) | `--revisor2 openrouter:deepseek/deepseek-v4-pro` e `OR_MODELO=deepseek/deepseek-v4-pro`; o relatório diz qual modelo rodou; achado desse modelo é medido antes de virar conserto |
| 5 | Como o projeto informa o workflow e os passos passageiros do deploy? | 2 campos na config (recomendada) | slots `deploy.workflow` e `deploy.transient_steps`; sem passos listados, nunca redispara; sem workflow, a release passa o nome lido dos arquivos do projeto |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado, `.claude/dev-espec/progress/PROGRESS_PILOT_DRIVE.md` e `PROGRESS_F3_PILOT_RALPH.md` | 2 | formato real do progresso; trazem nomes da RDD |
| Output examples | nenhum `DRIVE_REPORT_*` publicado no privado | 0 | o formato do relatório nasce aqui, a partir do objeto de retorno do `sdd-driver.js` |
| Ground truth | privado, `scripts/release/deploy-do-sha.test.mjs` | 1 | os casos de decisão do `deploy-do-sha` (lista mínima de casos) |
| Related code | `sdd/bin/sdd-fluxo.sh`, `.agents/skills/sdd-release/scripts/deploy-espera-testes.py`, `scripts/sdd-archive.py` do privado | 3 | padrão bash com núcleo Python; leitura dos workflows; lotes do arquivamento |

**How samples will be used:**
- Os casos do privado viram a lista mínima dos testes, dos dois lados, reescritos sem nome nem dado da RDD.
- O Roberto respondeu que não há amostra adicional.

## Approaches Explored

### Approach A: Script decide, agente faz — Recomendada

**Description:** `sdd-drive.sh` guarda o estado, roda o Verify Gate, conta as rodadas e devolve a próxima ação com um motivo tabelado; quem executa a ação é o agente, com subagente, ou, sem ele, com a parada `exit 40` do `sdd-fluxo.sh despachar`.

**Pros:**
- Funciona nos 7 agentes e mantém as paradas de decisão D1 a D5.
- É o desenho do `sdd-fluxo.sh`, já provado no Codex; a verdade mora num script (regra 1 do 8.0).

**Cons:**
- Em agente sem subagente, a pessoa abre cada sessão nova: mais lento. A tabela de degradação do plano aceita isso.

**Why Recommended:** é a única das três que mantém as paradas de decisão em todos os agentes sem depender da boa vontade do agente em seguir um texto.

### Approach B: Script chama os agentes

**Description:** o próprio script executa o programa do agente a cada volta, como a revisão adversarial faz com as engines do registry.

**Pros:**
- Roda de verdade sem ninguém olhando.

**Cons:**
- Exige o programa instalado e permissão de escrita liberada sem confirmação.
- No meio de um script não há onde fazer uma pergunta de decisão; quem usa agente sem linha de comando fica de fora.

### Approach C: Só texto na skill

**Description:** a skill descreve o laço e o agente segue; o script só confere o gate.

**Pros:**
- A menor quantidade de código.

**Cons:**
- Limite de rodadas, retomada e barreira dependem de o agente obedecer ao texto; quebra a regra 1 do 8.0; o plano pede o `sdd-drive.sh`.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-11-05, resposta "Script decide, agente faz (Recomendado)" |
| Reasoning | mantém as paradas de decisão nos 7 agentes e reaproveita o padrão já provado do `sdd-fluxo.sh` |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Drive inteiro na `v2.7.0` | fecha o item do plano; a F15 não herda buraco | sem `--resume`; só simulação |
| 2 | 1 rodada = passada inteira + gate; `drive.max_rounds: 3` | o número passa a significar tentativas de ficar verde; com 1 tarefa por rodada, 3 travaria qualquer feature com mais de 3 arquivos | 1 tarefa com limite 3; 1 tarefa com limite maior |
| 3 | Revisão do DESIGN, ao ficar vermelho, gasta a mesma rodada | um número só para a pessoa entender | contador próprio, como `MAX_DESIGN_REVS` do privado |
| 4 | Chamar o drive liga o encadeamento só naquela execução; D1 a D5 continuam perguntadas | o comando já é o opt-in; `flow.autonomous` no config não muda | exigir `flow.autonomous: true` |
| 5 | Depois do verde: avaliador de contexto fresco, BUILD_REPORT, DRIVE_REPORT e parada | a `sdd-release` exige tudo isso; o drive entrega pronto para ela, sem cruzar a barreira | parar logo no gate verde, como o privado |
| 6 | Só o script roda o gate; o agente que construiu nunca roda o gate que decide | regra do orquestrador do privado | deixar o resultado do agente decidir |
| 7 | `gate-inconclusivo` (exit 3) para e não gasta rodada | o privado anota e segue; aqui a pessoa resolve (a regra do modo ralph: `3` resolve) | continuar a próxima rodada |
| 8 | Slots `drive.max_rounds`, `deploy.workflow`, `deploy.transient_steps` | D11 + decisão desta sessão; sem passos listados, nunca redispara | só flags no comando; nunca redisparar |
| 9 | Item 10 da `sdd-release` passa a chamar `deploy-do-sha.sh` | a mesma lógica, não duas (quadro F14 do plano) | manter o texto ao lado do script |
| 10 | `sdd-archive.py` protege pela ficha `sdd/handoffs/HANDOFF_<F>.md` sem ✅ | a memória do Roberto não viaja; no Open a ficha mora no repositório | `--memoria` do privado |
| 11 | Só as 2 pendências que tocam o drive | cada conserto soma código à revisão paga; nas F12, F13 e F14 consertos trouxeram regressão | todas as 10; nenhuma |
| 12 | 2º revisor e prova com `deepseek/deepseek-v4-pro` pela OpenRouter | Codex sem créditos; caminho medido e aprovado | repor créditos; dispensar os 2 |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Limite de tokens (`drive.max_tokens`, `budget-floor`) | nenhum script lê o gasto do agente (D11) | Yes, quando houver leitor |
| Contador separado de revisões do DESIGN (`design-revs-exhausted`) | tudo gasta a mesma rodada | Yes |
| Modo paralelo `briefs` dentro do drive | o drive reaproveita só o ralph | Yes |
| Colheita de permissões (`/fewer-permission-prompts`) | é de um agente só (regra 10 do 8.0) | No, no pacote |
| Ponto de extensão do smoke visual (10b do privado) | é da F15 | Yes, na F15 |
| Testes colocados ao lado do módulo (`*.test.ts`) na passada 0b do privado | específico da RDD; a 0b do Open já pergunta pelo teste vizinho | No |
| 8 pendências de curadoria, lint e fronteira | ficam registradas no handoff; a revisão fica menor | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1: as 6 peças da entrega e o que fica de fora | Yes | "Confere (Recomendado)" | No |
| Checkpoint 2: as etapas de uma execução, os 8 motivos de parada, retomada, simulação e barreira | Yes | "Confere (Recomendado)" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

No Open, levar um DEFINE até "pronto para publicar" depende de a pessoa chamar cada fase e de o agente lembrar o limite das voltas: nada conta as rodadas, nada retoma uma execução que caiu e nada barra por script o avanço para a publicação. Na release, a verificação do deploy é um texto que o agente reinterpreta, o raio de impacto é uma passada única, e o passivo de documentos antigos não tem faxina.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Quem constrói com o SDD Open | precisa chamar fase por fase e acompanhar as voltas de teste vermelho |
| Quem publica com a `sdd-release` | a verificação do deploy depende do agente seguir um texto longo; o raio de impacto olha tudo de uma vez |
| Quem mantém um projeto antigo | documentos de features fechadas se acumulam em `sdd/features/`, `sdd/reports/` e `sdd/reviews/` |
| O Roberto, na F15 | sem drive, `deploy-do-sha` e archive, o privado não pode ser trocado pelo Open |

### Success Criteria (Draft)

- [ ] `sdd-drive.sh --dry-run` para no Verify Gate com motivo tabelado; `skill-lint.py .agents/skills/sdd-drive/SKILL.md` sai 0.
- [ ] Os 8 motivos de parada são produzidos em fixtures, cada um dos dois lados; `--resume` continua sem gastar rodada; estado corrompido ou de outro DEFINE para com motivo.
- [ ] Nenhum verbo do `sdd-drive.sh` publica, e um teste confere isso.
- [ ] `deploy-do-sha.sh` cobre próprio, substituto, sem substituto, falha passageira com redisparo único, teto e `gh` ausente, sem rede, com `gh` e `git` de mentira; o item 10 da `sdd-release` chama o script.
- [ ] `sdd-archive.py` sem `--aplicar` não muda nada; `--aplicar` exige lote, só usa `git mv` e protege a frente com ficha sem ✅.
- [ ] A guarda do avaliador aceita documento não rastreado e segue recusando código e documento rastreado modificado; a colheita não conta log de sonda.
- [ ] Todo script novo tem fixture, teste dos dois lados, baseline vermelha na `v2.6.0` e 1 sabotagem.
- [ ] Verify Gate `kind: test` de sempre verde; prova num agente de fora do Claude com o modelo declarado; Release `v2.7.0` com `SHA256SUMS.txt` conferido.

### Constraints Identified

- bash 3.2 e Python 3.9 stdlib; nada de `mapfile`, `declare -A` nem `${var^^}`.
- Texto de skill não cita ferramenta de um agente só (`tests/test_agnostico.py`).
- O drive nunca publica; push em `main` só com OK do Roberto citando "sdd-open".
- Específico da RDD não viaja: workflow, passos de SSH, caminhos e memória do privado saem.
- O repositório privado e o sdd-starter não são alterados.
- `sdd/features`, `handoffs`, `reports`, `reviews` e `traces` não entram em commit da branch de trabalho.
- A suíte precisa caber nos tetos de 25 e 45 minutos.

### Out of Scope (Confirmed)

- F15, F16, F17; regenerar o sdd-starter.
- Ponto de extensão do smoke visual.
- As 8 pendências que não tocam o drive.
- Limite de tokens e modo paralelo no drive.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 8 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
