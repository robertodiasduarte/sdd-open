# BRAINSTORM: F14 Playbook e orquestração

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F14_PLAYBOOK (1ª entrega da F14) · F14_DRIVE (2ª entrega, registrada aqui) |
| Date | 2026-11-05 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "Leia e execute o prompt em sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md (sessão 11 da frente INCORPORAR_STARTER: F14 Playbook e orquestração). A chave da OpenRouter para a revisão adversarial real está em ~/.config/rdd-eval.env (OPENROUTER_API_KEY): só no ambiente, nunca em arquivo."

O prompt da sessão pede a F14 do plano (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, quadro F14 e seção 8.1): C5, P1–P4, O1–O4, N1, N3, mais 2 itens do handoff (revisão focada na fronteira de escrita, isolamento de `SDD_TRACE`) e, se couberem, as pendências LOW da F13.

**Context Gathered:**

Fatos conferidos nesta sessão:
- Worktree `sdd-open-f14-playbook`, branch `feat/f14-playbook`, em `b1348bd` = tag `v2.5.0`; 18 skills, 1.134 testes no piso, `MANIFEST.txt` com 415 linhas (prompt da sessão).
- Fontes do privado lidas do `origin/main` dele (`88707b37d`), sem alterar nada: `scripts/playbook-curator.sh` (724 linhas), `.claude/agents/workflow/curator-playbook.md` (137), `.claude/commands/workflow/drive.md` (127), `.claude/sdd/workflows/sdd-driver.js` (233), `scripts/sdd-archive.py` (177), `scripts/new-session.sh` (208), `scripts/release/deploy-do-sha.mjs` (338), `.claude/invariants.md` (99), `.claude/commands/release.md` (passos 0b, 15b, 15c e 17b), `scripts/fixtures/curator/` (9 arquivos de teste, fora os `hook-input-*`).
- A trava `--validar-inv` do privado chama `scripts/docs-extract-invariants.sh`, que o Open não tem.
- O curator do privado é bash 3.2 com awk; usa intervalo `[0-9]{4}` dentro do awk (linha 425), forma que o mawk do Ubuntu pode não aceitar. O Open, desde a F9, põe o núcleo em Python stdlib embutido no script bash (`sdd/bin/sdd-fluxo.sh`).
- O `/drive` do privado é um script da ferramenta `Workflow` do Claude Code, com orçamento de tokens lido de `budget.remaining()`: nada disso existe fora do Claude Code.
- A `sdd-new-session` do Open é só texto (`SKILL.md` e `references/`), sem script.
- O `sdd/bin/playbook-lint.sh` do Open lê as seções de `PLAYBOOK_SECTIONS` (default: Sempre, Dados, Backend, Frontend, Infra / deploy, Reviews / harness, Domínio, Tombstones); o privado tem outras 8, fixas.
- `sdd/fixtures/playbook/` já tem 4 playbooks de teste do lint.
- O Codex CLI 0.163 responde `Your workspace is out of credits`; o Gemini CLI pede `GOOGLE_CLOUD_PROJECT`; o Grok CLI pede `grok login`. O `adversarial-review.sh` aceita `--revisor2 <engine>`.

Inferências (a confirmar no Design):
- A conferência das invariantes cabe dentro do próprio `playbook-curator.sh` (gramática, origem aposentada, pendente sem classificação, ID duplicado), sem gerador de catálogo.
- O papel `curador` precisa entrar na lista explícita de nomes do `sdd-fluxo.sh despachar`.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/playbook-curator.sh`, `sdd/invariants.md`, `sdd/fixtures/playbook/`, `.agents/skills/sdd-playbook/`, `.agents/skills/sdd-release/SKILL.md` (passo 17b), `.agents/skills/sdd-new-session/`, `sdd/templates/HANDOFF_TEMPLATE.md`, `tests/` | toda skill tocada sobe de versão; todo arquivo novo entra no `MANIFEST.txt`; os pinos de versão de 3 testes mudam |
| Relevant KB Domains | nenhum (`sdd/kb/` não existe neste repositório) | a linha de KB Domains do DEFINE fica `nenhum` |
| IaC Patterns | CI em `ubuntu-latest` e `macos-latest`; Release automática no push de `main` que toca `sdd/bin/**`, `.agents/skills/**`, `sdd/templates/**`, `sdd/fixtures/**` | piso Python 3.9 e bash 3.2; a suíte maior precisa caber nos tetos de 25 e 45 minutos |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | A F14 sai em uma entrega ou em duas? | 2 entregas em sequência (recomendada) | 1ª: playbook, sessão e consertos (este brainstorm, `F14_PLAYBOOK`); 2ª: orquestração (`F14_DRIVE`), com Define próprio, só depois da Release da 1ª |
| 2 | Quais ajustes o `sdd-drive` ganha em `sdd/config.yaml` (D11)? | só `drive.max_rounds`, default 3 (recomendada) | `drive.max_tokens` cai: nenhum script do pacote lê o gasto do agente. O slot entra na 2ª entrega, junto do leitor dele |
| 3 | Que número de versão? | número do meio por tag (recomendada) | `v2.6.0` na 1ª entrega e `v2.7.0` na 2ª; push atômico de `main` com a tag |
| 4 | O Codex está sem créditos: como ficam o 2º revisor e a prova em outro agente? | troco o revisor; o Roberto libera um agente (recomendada) | 2º revisor = outro modelo via OpenRouter (`--revisor2`); a prova em agente de fora do Claude espera créditos do Codex, `grok login` ou o `GOOGLE_CLOUD_PROJECT` do Gemini; o agente avisa antes da etapa de revisão |
| 5 | As pendências LOW da F13 entram? | entram as duas (recomendada) | `design-lint.py` (títulos fora do padrão, 3 campos sem preencher) e `prompt-drift-scan.sh` (2 formas do slot, 2 motivos de saída 64 sem dente no self-test) entram na 1ª entrega |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado, `scripts/fixtures/curator/` (lido por `git show`) | 9 | DESIGN, BUILD_REPORT e log do avaliador de teste, 5 playbooks, 1 arquivo de invariantes, 1 delta; trazem nomes da RDD |
| Output examples | privado, self-test do `playbook-curator.sh` | 46 | casos com a saída esperada, vermelhos antes dos verdes |
| Ground truth | privado, `.claude/invariants.md` | 65 | invariantes reais; só referência de formato, não viajam |
| Related code | `sdd/bin/playbook-lint.sh`, `sdd/bin/sdd-fluxo.sh`, `sdd/fixtures/playbook/` | 3 | gramática do playbook, padrão bash com núcleo Python, fixtures existentes |

**How samples will be used:**
- As fixtures do privado são reescritas em versão genérica (seções do Open, sem nome de tabela, de projeto ou de pessoa da RDD) e gravadas em `sdd/fixtures/playbook/`.
- Os casos do self-test do privado viram a lista mínima de casos do self-test e dos testes de `tests/`, dos dois lados.
- O Roberto respondeu que não há amostra adicional.

## Approaches Explored

### Approach A: Porte enxuto com trava própria — Recomendada

**Description:** `playbook-curator.sh` com `--colher`, `--aplicar`, `--cruzar` e `--validar-inv`; `sdd/invariants.md` com a gramática do privado; a conferência das invariantes mora dentro do próprio script; o curador é um brief em `sdd-playbook/references/`, despachado em contexto fresco pela escada que o pacote já tem.

**Pros:**
- A trava que impede aposentar uma landmine da qual uma invariante depende funciona sem ferramenta extra.
- Cabe numa entrega; o leitor das invariantes (o curator) nasce junto com o arquivo.

**Cons:**
- A trava é código novo, não porte: pede teste dos dois lados e sabotagem própria.
- Sem catálogo publicado em `docs/`: quem quer ler as invariantes abre `sdd/invariants.md`.

**Why Recommended:** entrega o mecanismo inteiro (colher, julgar, perguntar, aplicar, travar) com a menor superfície nova; o que fica fora é só apresentação.

### Approach B: Porte integral

**Description:** tudo da A, mais o gerador de catálogo (`docs-extract-invariants.sh`), o arquivo gerado em `docs/` e o passo de CI que o confere, como no privado.

**Pros:**
- Igual ao privado: a F15 troca sem adaptar.

**Cons:**
- Um gerador e um passo de CI a mais para um arquivo que nasce com poucas linhas; quase dobra a entrega.

### Approach C: Sem invariantes

**Description:** só a colheita, o brief e a curadoria na release; C5 adiado de novo.

**Pros:**
- A menor das três.

**Cons:**
- Adia pela 2ª vez o que a F12 já adiou; a F15 precisa das invariantes para substituir o privado.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-11-05, resposta "A. Porte enxuto com trava própria (Recomendado)" |
| Reasoning | mecanismo completo com a menor superfície nova; o catálogo gerado pode vir depois sem mudar a gramática |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | F14 em 2 entregas: `F14_PLAYBOOK` (`v2.6.0`) e `F14_DRIVE` (`v2.7.0`) | cada revisão lê metade do código; a F13, menor, levou 6 rodadas | 1 entrega só |
| 2 | 1ª entrega = C5, P1, P2, P3, P4, N1, N3, isolamento de `SDD_TRACE`, pendências LOW da F13, revisão focada na fronteira de escrita, 1 página de documentação | é a metade que não depende da skill nova | deixar N1 e N3 para a 2ª |
| 3 | 2ª entrega = O1 (skill `sdd-drive` e `sdd/bin/sdd-drive.sh`), O2, O3, O4 e o slot `drive.max_rounds` | O3 e o item 10 da `sdd-release` são a mesma lógica; a contagem de skills vai a 19 só aí | O2 na 1ª entrega (tocaria o mesmo passo da release duas vezes) |
| 4 | D11: só `drive.max_rounds`, default 3; `drive.max_tokens` cai | slot sem leitor é texto morto | os dois slots; nenhum slot |
| 5 | Versão por tag, número do meio em cada entrega | cada uma traz comando novo para quem instala | automática; mista |
| 6 | 2º revisor por outro modelo via OpenRouter; prova em agente de fora do Claude depende de o Roberto liberar um | Codex sem créditos | esperar os créditos; dispensar a prova |
| 7 | Contagem com evidência entra sem pergunta; ADD, TOMBSTONE, PROMOVER e mudança em invariante são pergunta `[D3 · muda a regra do método]` | contagem não é política (P3 do plano); confirmado no bloco 2 | perguntar também as contagens |
| 8 | Amostras: fixtures do privado reescritas em versão genérica | o Roberto não tem amostra adicional | usar uma curadoria real do privado |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Catálogo de invariantes gerado em `docs/` com passo de CI | apresentação de um arquivo que nasce pequeno; a trava não depende dele | Yes |
| Slot `drive.max_tokens` | nenhum script lê o gasto de tokens do agente | Yes, quando houver leitor |
| Lista de jargão proibido na coluna de linguagem simples (`--curadoria` do privado) | a lista é do vocabulário da RDD; fica só a conferência de que a coluna existe e não está vazia | Yes |
| Colheita de permissões do passo 15c do privado | é de um agente só (regra 10 do 8.0) | No, no pacote |
| Leitura da memória `project_handoff_*` | no Open a ficha é `sdd/handoffs/HANDOFF_<F>.md`, dentro do repositório | N/A |
| Sugestão de mecanismo com caminhos do privado (`.githooks/`, `release-landmines.sh`) | viram os 3 destinos do Open: hook de `sdd/hooks/`, comando de `release.landmines_cmd`, asserção no Verify Gate | N/A |
| Baseline de edge functions e abertura de editor do `new-session.sh` | específico da RDD; o editor a skill do Open já trata | No |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Bloco 1: as 8 peças da entrega do playbook e o que fica fora | Yes | "Confere (Recomendado)" | No |
| Bloco 2: os 6 passos da curadoria na release, com as paradas e as falhas | Yes | "Confere (Recomendado)" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

No Open, a curadoria do playbook é um parágrafo de instrução na `sdd-release`: nada colhe os contadores de forma repetível, nada impede que uma falha de coleta seja lida como "nada a colher", e não existe registro de invariantes; além disso, a frente nova nasce sem os documentos SDD que ainda não foram salvos no git, e o molde do handoff não tem as seções que o handoff real usa.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| Quem publica com a `sdd-release` | responde a uma lista de deltas montada à mão pelo agente, sem saber o que foi contado e o que é mudança de regra |
| Quem mantém o playbook de um projeto | lição que mordeu 2 vezes não vira trava; aposentar uma landmine pode deixar uma regra permanente sem origem |
| Quem abre uma frente com a `sdd-new-session` | os documentos das fases de papel ficam no checkout principal e precisam ser copiados à mão |
| O Roberto, na F15 | sem curator, invariantes e molde de handoff completo, o privado não pode ser trocado pelo Open |

### Success Criteria (Draft)

- [ ] `bash sdd/bin/playbook-curator.sh --colher sdd/fixtures/playbook/<staging> <playbook>` imprime os 4 tipos de linha: `DELTA`, `CANDIDATO` ou `REJEITADO`, `SUGESTAO` e `PROMOVER?` (critério de pronto do plano).
- [ ] `--aplicar` com delta inválido sai 2 e não imprime nada em stdout.
- [ ] Falha de coleta (saída 2 ou 64) nunca é registrada como "0 deltas" pelo passo da release.
- [ ] `--validar-inv` reprova TOMBSTONE de landmine que é origem de invariante sem o ajuste, e aprova com o ajuste proposto pelo `--cruzar`.
- [ ] A `sdd-new-session` copia só documento com nome idêntico ao da frente e lista os parecidos sem copiar.
- [ ] `python3 sdd/bin/handoff-lint.py` aceita o `HANDOFF_TEMPLATE.md` novo.
- [ ] A suíte passa com `SDD_TRACE=off` no ambiente de quem a chama.
- [ ] Todo script novo tem self-test ou fixture, teste dos dois lados, baseline vermelha na `v2.5.0` e 1 sabotagem.
- [ ] Verify Gate `kind: test` de sempre verde; Release `v2.6.0` com `SHA256SUMS.txt` conferido.

### Constraints Identified

- bash 3.2 e Python 3.9 stdlib; nada de `mapfile`, `declare -A` nem `${var^^}`.
- Texto de skill não cita ferramenta de um agente só (`tests/test_agnostico.py`).
- O curador nunca escreve; quem aplica é a release, depois do OK.
- Específico da RDD não viaja: seções, caminhos e nomes do privado saem.
- O repositório privado e o sdd-starter não são alterados.
- `sdd/features`, `handoffs`, `reports`, `reviews` e `traces` não entram em commit da branch de trabalho.
- Push em `main` só com OK do Roberto citando "sdd-open".

### Out of Scope (Confirmed)

- Tudo da 2ª entrega: skill `sdd-drive`, `sdd-drive.sh`, slot `drive.max_rounds`, raio de impacto por superfície, `deploy-do-sha.sh`, `sdd-archive.py`, a linha `sdd-drive` do roadmap.
- Catálogo gerado de invariantes.
- F15, F16 e F17; regenerar o sdd-starter.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 9 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
