# BRAINSTORM: F23 Economia mensurável

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Date** | 2026-11-15 |
| **Author** | brainstorm-agent |
| **Status** | Ready for Define (só a fatia B1; o fatiamento espera o OK do Roberto) |

---

## Initial Idea

**Raw Input:** escopo fixado pelo Roberto em 2026-11-15 em `sdd/features/ESCOPO_F23_ECONOMIA_MENSURAVEL.md`, nascido da avaliação de um estudo de caso de modelos baratos em produção. Grupo A (lições no produto do aluno): A1 descrição de ferramenta, A2 validação em código, A3 conferência como saída prevista, A4 modelo por evidência. Grupo B (economia do processo do Open): B1 custo por fase e por feature, B2 modelo por papel, B3 cadeia de revisão pelos dados. As lições 1, 2 e 5 do caso ficaram fora (ESCOPO §3.2) e não se reabrem sem fato novo.

**Context Gathered:**
- Só a revisão adversarial tem custo registrado hoje: `sdd/bin/eval-revisores.sh` (pago · nominal · n/d, n/d nunca zero), `sdd/review/precos.tsv` (só preço de entrada e saída), adaptadores em `sdd/bin/adapters/` (claude e openrouter reportam custo; codex e gemini só tokens).
- As fases (define, design, build, avaliador, curador) rodam em sessão interativa e não têm registro de custo. Os agentes deixam registro local por sessão: o Claude Code em `~/.claude/projects/<pasta>/<sessão>.jsonl` (campo `usage` por mensagem: entrada, saída, cache criado, cache lido) e subagentes em `<sessão>/subagents/*.jsonl`; o Codex em `~/.codex/sessions/AAAA/MM/DD/*.jsonl` (eventos `token_count`).
- Nesta sessão, uma mensagem leu 28.790 tokens de cache e 2 de entrada nova: cobrar cache como entrada infla o nominal várias vezes.
- `sdd/bin/sdd-fluxo.sh seguir` roda na troca de fase só com o encadeamento ligado; o registro do Claude Code marca a skill chamada, o do Codex não.
- O inventário de prompts (`sdd/templates/fragments/LLM_PROMPTS_DESIGN.md`) tem os tipos `one-shot` e `loop`; `sdd/bin/design-lint.py` confere colunas e campos. A seção `<tools>` de `.agents/skills/sdd-prompt-builder/references/prompt-building-rules.md` tem duas linhas.
- O starter tem um exemplo só (`scripts/starter/raiz/exemplos/baixar-nfse/`), sem prompt de modelo.
- Sobras herdadas do plano, conferidas: a curadoria da F16W2 já está em `origin/main` (`66362e0`); o `--conferir` ainda recusa revisão com `--paths` (`sdd/bin/adversarial-review.sh:421-424`) e o version gate contra a versão real do starter segue fora do Verify Gate. As duas que valem ficam fora da F23 (não mexem nos números desta frente).

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `sdd/bin/` (scripts), `sdd/bin/adapters/` (adaptadores de sessão), `sdd/review/precos.tsv`, skills de fase em `.agents/skills/`, `scripts/starter/` | B1 mexe nas skills de fase ⇒ regenerar o starter por `scripts/gerar-starter.py` |
| Relevant KB Domains | N/A | — |
| IaC Patterns | N/A | — |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Em que ordem entram as fatias? | B1 → B3 → B2 → Grupo A | B1 cria a régua; a economia aparece a partir da B3 |
| 2 | Qual a moeda da B1? (ESCOPO §8.3) | Gravar tokens, pago, nominal e tempo; nominal é o principal | mesmo vocabulário do `eval-revisores.sh`; o B3 soma revisão e fases sem converter |
| 3 | De onde sai o custo de uma fase? (§8.4) | Adaptador por agente lê o registro local; nominal = tokens × `precos.tsv` com cache à parte; sem registro legível = n/d | agnóstico de vendor; agente novo ganha um adaptador |
| 4 | Como dividir uma sessão entre fases? (nova) | Cada skill de fase grava marca de início e fim; trecho fora de marca = "sem fase" | funciona igual em qualquer agente; regenera o starter |
| 5 | O que a B3 faz com o 2º revisor? (§8.5) | Dispensa por classe de risco (superfície de risco do `sdd-fluxo.sh review-design` ou discordância revisor × auditor), registrada no ledger; volta atrás se o dano que escapou subir | maior economia de nominal com proteção onde o dano custa caro |
| 6 | Onde a descrição de ferramenta entra? (§8.1) | Linha própria no inventário, `Tipo=ferramenta`, com contrato | absorve o A2; o `design-lint.py` passa a conferir |
| 7 | Como o gabarito trata a conferência? (§8.2) | Cada caso: `responder`, `conferir` ou `tanto faz`; sem teto numérico | impede tanto conferir tudo quanto chutar onde devia conferir |
| 8 | Como o A4 chega ao starter? (§8.6) | Planilha-molde e passo a passo, sem terminal | o aluno sem terminal mede antes de trocar de modelo |
| 9 | O que fazer com os dados brutos do caso? (§8.7) | Condicional, sem bloquear | o Grupo A não depende de limpeza de dado de terceiro |

**Minimum Questions:** 3 (to ensure clarity before proceeding)

---

## Perfil de risco

> As 3 perguntas de segurança, uma linha cada ("não sei" vale). O passo de segurança do Define lê esta seção para
> saber se há login, dado de terceiros, rota pública, envio de arquivo ou chamada paga.

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | O relatório de custo e o BUILD_REPORT são lidos por quem acessa o repositório (no Open, **público**) ⇒ o adaptador extrai só números (tokens, horários, modelo, custo), nunca texto da conversa, caminho de arquivo ou argumento de ferramenta. O registro de sessão lido contém a conversa inteira (pode ter dado de cliente e segredo). A planilha do A4 fica com o aluno. |
| Quem pode mudar? | Os registros de sessão são do agente: o adaptador só lê, nunca grava. As marcas são escritas pelas skills numa pasta do projeto. A `precos.tsv` e a regra de dispensa do 2º revisor só mudam por commit revisado. |
| Quanto alguém pode pedir? | B1, B3 e B2 (na parte de contar) não chamam modelo nem rede. A medição paga do A4 e da B2 (rodar modelos candidatos) tem teto de gasto fechado com trava automática, rodada pelo projeto, não pelo script. |

---

## Sample Data Inventory

> Samples improve LLM accuracy through in-context learning and few-shot prompting.

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | `~/.claude/projects/-Users-robertoduarte-rdd-worktrees-sdd-open-*/` | 23 frentes (F4 a F23), 1 a 3 sessões principais cada, mais `subagents/` | JSONL com `usage` por mensagem; o mais antigo de 2026-10-29 (F4, 6 MB). Protegidos: `cleanupPeriodDays: 365` em `~/.claude/settings.json` (2026-11-15, OK do Roberto) |
| Input files | `~/.codex/sessions/` | 4 sessões | eventos `token_count`; linha de base do Codex rala |
| Ground truth | BUILD_REPORTs e ledgers da worktree de documentos (`/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16`) e das frentes | 10+ features | rodadas até o gate verde e achados com dano por feature |
| Related code | `sdd/bin/eval-revisores.sh`, `sdd/bin/adapters/*.sh`, `sdd/review/precos.tsv` | 1 contador, 4 adaptadores | padrão a repetir: o script lê arquivos e conta, não chama nem julga |

**How samples will be used:**

- Linha de base da seção 6 do ESCOPO: custo nominal por feature da F4 à F22, somando as sessões inteiras (sem divisão por fase).
- Fixtures dos adaptadores: trechos reais **anonimizados** (só os campos numéricos e horários), nunca o texto da conversa.
- Prova da B1: refazer à mão a conta de uma frente e bater com o contador; o nominal da revisão bate com o `eval-revisores.sh` nas rodadas em comum.

---

## Approaches Explored

### Approach A: Contador próprio, no molde da revisão ⭐ Recommended

**Description:** `sdd/bin/marca-fase.sh` (chamado pelas skills de fase no início e no fim: fase, feature, horário); adaptadores `sessao-claude.sh` e `sessao-codex.sh` (leem sessão principal e subagentes, devolvem só números); `sdd/bin/custo-feature.sh` (só conta: por fase e por feature, mais o custo da revisão lido dos META sem contar em dobro; grava a seção de custo junto do BUILD_REPORT; modo de linha de base por feature); coluna de preço do cache na `precos.tsv`.

**Pros:**
- Agnóstico de vendor; repete um padrão que já funciona (`eval-revisores.sh` + adaptadores).
- Testável com fixtures; não chama modelo nem rede.
- B3 e B2 só leem o que ele grava.

**Cons:**
- Mexe nas skills de fase ⇒ regenerar o starter.
- 3 scripts e 2 adaptadores novos.

**Why Recommended:** cada peça faz uma coisa só e o formato já é conhecido de quem mantém a revisão.

---

### Approach B: Ampliar o `eval-revisores.sh`

**Description:** o contador da revisão passa a ler também as sessões de fase.

**Pros:**
- Uma ferramenta só.

**Cons:**
- Já tem 9 colunas e regras de ledger; misturar sessão de fase com rodada de revisão deixa os dois mais difíceis de testar e um erro num quebra o outro.

---

### Approach C: Hook de fim de sessão do agente

**Description:** um hook do agente grava o custo ao fim de cada sessão.

**Pros:**
- Automático, sem marca.

**Cons:**
- Existe só num agente: fere a regra de vendor-agnóstico; não divide sessão entre fases.

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A |
| **User Confirmation** | 2026-11-15, Roberto |
| **Reasoning** | segue o padrão da revisão e entrega à B3 e à B2 dados prontos para ler |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | Fatias B1 → B3 → B2 → Grupo A | sem custo registrado nenhuma economia se demonstra | B3 primeiro (prova parcial); Grupo A primeiro (ensina medir sem o Open medir) |
| 2 | Nominal como número principal; grava tokens, pago e tempo | com assinatura o pago é ~0; token não se compara entre modelos | tempo ou tokens como principal |
| 3 | Adaptador por agente lendo registro local; n/d nunca zero | agnóstico; lacuna visível em vez de economia falsa | anotação à mão; estimativa por tamanho de arquivo |
| 4 | Cache com preço próprio | cache lido como entrada infla o nominal várias vezes | cobrar cache como entrada |
| 5 | Marca de início e fim gravada por cada skill de fase | divide sessão entre fases em qualquer agente | marca de skill do agente (só Claude Code); sessão inteira na 1ª fase |
| 6 | Tempo = tempo ativo do agente (soma das respostas) | sessões ficam paradas por horas ou dias | relógio corrido entre marcas |
| 7 | 2º revisor dispensado por classe de risco, com volta atrás pelo dano | maior economia de nominal; com poucas rodadas medidas, zero achado com dano ainda é compatível com uma taxa real alta (regra de três), então não se dispensa sempre | sempre rodar num modelo mais barato (espera a B2) |
| 8 | Descrição de ferramenta = linha `Tipo=ferramenta` no inventário, com contrato e validação em código dos argumentos | a descrição é prompt (papers da lição 3); absorve o A2; o lint confere | material de referência da linha do prompt; só regra na `<tools>` |
| 9 | Gabarito por caso: `responder` · `conferir` · `tanto faz`; responder num `conferir` com dinheiro ou tributo = erro grave; sem teto | evita os dois atalhos (conferir tudo e chutar) | aceita/não aceita + teto; só teto |
| 10 | A4 no starter = planilha-molde sem terminal | o aluno do starter não usa terminal | caso completo já (bloqueado por dados); A4 só no Open |
| 11 | Caso como exemplo só se os dados chegarem limpos; senão 3 casos ilustrativos marcados | não bloquear a frente com limpeza de dado de terceiro | dados agora como amostra; nunca exemplo |
| 12 | Linha de base F4–F22 pelos registros de sessão, protegidos com `cleanupPeriodDays: 365` | a comparação da seção 6 fica possível já, sem esperar dez frentes novas | só BUILD_REPORTs e ledgers; régua começando na F23 |
| 13 | Sobras `--conferir` com `--paths` e version gate do starter ficam fora da F23 | não mexem nos números desta frente | levá-las no passo 0 |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Adaptador do gemini, do Cursor e de outros agentes | sem registro local em uso aqui; ficam n/d | Yes, quando um agente for usado numa frente |
| Divisão por fase nas frentes F4 a F22 | a seção 6 compara por feature; cortar por horário de commit seria palpite | Yes, se a B2 precisar de histórico por papel |
| Separar tempo de espera humana do tempo do agente | a B1 grava tempo ativo do agente | Yes |
| Cota da assinatura | o nominal já mostra a economia | Yes, se o provedor publicar a cota legível |
| Painel ou gráfico | relatório em texto basta para 10 linhas | Yes |
| Alerta de orçamento durante a sessão | a B1 só mede depois; o teto vale para a medição paga do A4 e da B2 | Yes, na B2 |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Perfil de risco (3 respostas propostas) | ✅ | ok | No |
| YAGNI (fica × sai) | ✅ | ok | No |
| Bloco 1 — o que a B1 entrega | ✅ | ok | No |
| Bloco 2 — B3, B2 e Grupo A e a prova de cada fatia | ✅ | ok | No |

**Minimum Validations:** 2 (to ensure alignment)

---

## Prova de economia por fatia

Regra comum: cada fatia é medida pelos três números da seção 6 do ESCOPO contra a linha de base da B1 (custo nominal por feature · rodadas até o Verify Gate verde · achados com dano que escaparam). **Se o terceiro subir, a fatia volta atrás**, mesmo com o custo menor.

| Fatia | O que entra | Prova |
|---|---|---|
| B1 | marcas por fase, adaptadores de sessão, contador, coluna de cache, linha de base F4–F22 | conta de uma frente refeita à mão bate com o contador; nominal da revisão bate com o `eval-revisores.sh`; a F23 sai com custo por fase |
| B3 | fechar as linhas fora da conta do `eval-revisores.sh`; 2º revisor só com superfície de risco ou discordância; dispensa no ledger | nominal da revisão cai nas frentes seguintes sem achado com dano a mais; no privado, a cadeia da RDD decidida pelos mesmos dados |
| B2 | campo de modelo por papel no `sdd/config.yaml` (cartógrafo, revisão do design, executor, avaliador, curador); gabarito do histórico (achados dos ledgers, deltas do curador, vereditos do avaliador); o mais barato que bate a meta, com repetições e teto de gasto | nominal do papel cai e o resultado no gabarito fica na meta; curador e cartógrafo primeiro |
| Grupo A | A1+A2 `Tipo=ferramenta`; A3 gabarito `responder`/`conferir`/`tanto faz`; A4 protocolo (script no Open, planilha no starter) | `design-lint` recusa ferramenta sem contrato; a planilha refaz a conta de um exemplo e bate com o script |

---

## Suggested Requirements for /define

Escopo do Define: **só a fatia B1**. As outras fatias têm Define próprio depois.

### Problem Statement (Draft)
O Open não registra o custo das fases nem das features (só o da revisão), então nenhuma economia do próprio processo pode ser demonstrada nem comparada com as features anteriores.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Mantenedor do Open (Roberto) | decide cadeia de revisão e modelo por impressão; não sabe quanto cada fase custa |
| Quem usa o Open num projeto | não vê o custo nominal da feature que construiu, nem por fase |

### Success Criteria (Draft)
- [ ] Toda skill de fase grava marca de início e de fim (fase, feature, horário); um trecho de sessão fora de marca aparece como "sem fase".
- [ ] Os adaptadores de sessão do Claude Code e do Codex leem a sessão principal e os subagentes e devolvem só números (tokens de entrada, saída, cache criado, cache lido; horários; modelo; custo reportado); uma fixture com texto de conversa prova que nenhum texto sai.
- [ ] O contador grava, junto do BUILD_REPORT, uma tabela por fase com tokens, pago, nominal, tempo ativo e rodadas, mais o custo da revisão lido dos META, sem contar em dobro.
- [ ] Sem registro legível, o valor é n/d e nunca entra na soma como zero.
- [ ] `precos.tsv` tem preço de cache; o nominal de uma fixture com cache bate com a conta à mão.
- [ ] O modo de linha de base produz uma linha por feature da F4 à F22 (custo nominal, rodadas até o gate verde, achados com dano).
- [ ] A conta de uma frente refeita à mão bate com o contador; o nominal da revisão bate com o `eval-revisores.sh` nas rodadas em comum.
- [ ] A suíte fica verde no macOS e no Windows (job `testes-windows`).

### Constraints Identified
- Vendor-agnóstico: só o método entra no Open, nunca nome nem preço de modelo.
- O contador não chama modelo nem rede; só lê arquivos.
- Nada é corrigido direto no starter: regenerar por `scripts/gerar-starter.py` e `scripts/starter/lista.txt`.
- bash 3.2 (macOS) e Python 3.9 stdlib, como o resto de `sdd/bin/`.
- Verificar no Design se as chamadas da revisão deixam sessão no registro local (risco de contar em dobro).
- Ler a seção "Sempre" de `sdd/playbook.md` e rodar `sdd/bin/playbook-lint.sh --grep <termo> sdd/playbook.md` por superfície antes de codar.

### Out of Scope (Confirmed)
- B3, B2 e Grupo A (fatias seguintes, Define próprio).
- Lições 1, 2 e 5 do caso (ESCOPO §3.2).
- Itens da tabela YAGNI acima.
- Sobras `--conferir` com `--paths` e version gate do starter.

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 9 de descoberta + perfil de risco + amostras |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 4 |
| Duration | 1 sessão, com pausa (2026-11-15) |

---

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F23_ECONOMIA_MENSURAVEL.md` (depois do OK do Roberto sobre o fatiamento)
