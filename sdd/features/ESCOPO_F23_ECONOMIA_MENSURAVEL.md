# ESCOPO — F23 Economia mensurável

- **Data:** 2026-11-15
- **Frente:** `feat/f23-economia-mensuravel`, pasta `~/rdd-worktrees/sdd-open-f23-economia-mensuravel`, nascida de `origin/main` em `8f944fc`.
- **O que é este arquivo:** as descobertas que deram origem à frente e o escopo que o Roberto fixou. É a entrada da `sdd-brainstorm`. Não é DEFINE: nada aqui tem teste de aceitação ainda.
- **Estado:** escopo fixado pelo Roberto em 2026-11-15; fatias e decisões abertas vão para o brainstorm.

## 1. Origem

O Roberto pediu a avaliação do estudo de caso *Modelos baratos em produção: quando o harness vale mais que o modelo* (`~/Downloads/Modelos baratos em produção.html`, novembro de 2026) e de como ele contribui com o SDD Open e com o starter.

O caso mede uma equipe de agentes de um escritório (triagem, agenda, pendências, contas a pagar, tesouraria e dois consultores tributários). Quatro modelos baratos rodaram em oito agentes, com 116 casos reais de resposta conhecida, o mesmo código e o mesmo prompt. Antes de trocar de modelo, cada erro foi corrigido na causa: contexto, prompt, skill, ferramenta ou formato. O teste inteiro custou US$ 8,20, com mais de 4.100 execuções.

Regras do teste que interessam ao Open:

- meta de acerto por agente (90%; 95% onde há dinheiro ou tributo);
- erro grave tem meta zero e é contado à parte do acerto;
- pedir conferência ao responsável conta como acerto;
- só o modelo muda entre as execuções;
- orçamento fechado, com trava automática.

## 2. O que a avaliação do caso concluiu

**Os números fecham.** O placar por modelo foi conferido contra a matriz agente × modelo: agentes na meta, erros graves e custo por mil tarefas batem.

**Ressalvas, que o método do Open precisa tratar:**

| Ressalva | Evidência no caso | Consequência para o Open |
|---|---|---|
| Amostra pequena | 12 a 17 casos por agente; um caso muda de 6 a 8 pontos | o relatório de medição declara o número de casos e as repetições |
| Regressões não comentadas | depois das correções, o Haiku caiu no CEO (93,3% → 90%, com 1 erro grave) e no PIS/COFINS (100% → 91,7%); o DeepSeek v4.1-flash caiu na Triagem e no Financeiro | toda mudança de prompt roda a medição em todos os modelos candidatos |
| Conferência sem limite | o CEO com o Haiku chegou a 90% com 10 conferências | o gabarito diz, caso a caso, onde a conferência é aceita |
| Afirmação sem medição | "conta de 4 a 40 vezes maior" com modelo maior; modelos maiores não entraram no teste | não entra no Open como fato |
| Ranking é foto | nomes e preços de modelo são de novembro de 2026 | só o método entra; o Open é agnóstico de vendor |

## 3. As lições do caso e a fundamentação em papers

Busca feita em 2026-11-15. Foram lidos resumos e trechos, não os PDFs inteiros: os números são os que os autores declaram.

| # | Lição | Base em papers | Entra na F23? |
|---|---|---|---|
| 1 | Contexto: o modelo não sabe a data nem a hora | fraca, só adjacente | não |
| 2 | Papéis: quem delega precisa da missão de cada destino | parcial | não |
| 3 | A descrição da ferramenta também é prompt | **forte** | **sim** |
| 4 | Regra que código confere não depende do prompt | **forte** | **sim** |
| 5 | Contrato de saída e a falha dele | parcial | não |
| 6 | Perguntar em vez de chutar | **forte** | **sim** |
| 7 | Medir antes de trocar de modelo | **forte** | **sim** |

**Decisão do Roberto (2026-11-15):** entram só as lições com fundamentação forte, ou seja, 3, 4, 6 e 7.

### 3.1 As quatro que entram

**Lição 3 — descrição de ferramenta.**
- *Smell-Aware Evaluation of MCP Server Descriptions* (arXiv 2602.18914): padrão de qualidade com 18 categorias de defeito; num estudo controlado, defeitos de funcionalidade e de precisão foram os que mais mudaram a escolha da ferramenta; descrição dentro do padrão chegou a 72% de probabilidade de seleção, contra 20% da base.
- *MCP Tool Descriptions Are Smelly!* (arXiv 2602.14878): 97,1% de 856 descrições tinham ao menos um defeito; os mais comuns são limitação não declarada, falta de orientação de uso e parâmetro opaco.
- No caso: a ferramenta `balancete_entregar` fechava o mês, e um modelo a chamou quando só pediram para ver o balancete.

**Lição 4 — validação em código.**
- *AgentSpec* (arXiv 2503.18666): linguagem para declarar e impor restrições em tempo de execução, com sobrecarga de milissegundos.
- *Policy Compiler for Secure Agentic Systems* (arXiv 2602.16708): monitor que intercepta toda ação e bloqueia a violação antes de executar, independente do raciocínio do modelo.
- *Reason Less, Verify More* (arXiv 2607.07405) e *Agent-C* (arXiv 2512.23738) seguem a mesma linha.
- No caso: um modelo pôs "telefone não cadastrado" no campo do número de WhatsApp; a ferramenta passou a recusar o que não é telefone.

**Lição 6 — perguntar em vez de chutar.**
- *Why Language Models Hallucinate* (arXiv 2509.04664): avaliações por acerto premiam o chute; a pontuação deve deixar de punir a abstenção.
- *AbstentionBench* (arXiv 2506.09038, NeurIPS 2025): 20 conjuntos de dados; o ajuste para raciocínio piora a abstenção em 24% na média; um system prompt ajuda, mas não resolve.
- *Why Do Multi-Agent LLM Systems Fail?* (arXiv 2503.13657): "deixar de pedir esclarecimento" é 6,8% das falhas catalogadas.
- Consequência: a regra no prompt não basta. A medição precisa de gabarito por caso.

**Lição 7 — medir antes de trocar.**
- *AI Agents That Matter* (arXiv 2407.01502, TMLR 2025): toda avaliação de agente controla custo; resultado em curva de custo × acerto.
- *Holistic Agent Leaderboard* (arXiv 2510.11977, ICLR 2026): 21.730 execuções, 9 modelos, 9 benchmarks; os modelos mais caros raramente ficam na fronteira de custo × acerto.
- *Adding Error Bars to Evals* (arXiv 2411.00640): todo resultado traz o número de questões e o erro-padrão.
- *τ-bench* (arXiv 2406.12045): consistência em repetições (pass^k); o acerto cai rápido quando se exige acertar k vezes seguidas.
- *How good is your harness?* (ICML 2026): escolher o melhor harness rende ganho comparável a escolher o melhor modelo; o efeito do harness varia por modelo.
- *PromptBridge* (arXiv 2512.01420): prompt ajustado para um modelo costuma render bem menos em outro.
- *How Do AI Agents Spend Your Money?* (arXiv 2604.22750): o consumo de tokens na mesma tarefa varia muito entre modelos.
- *FrugalGPT* (arXiv 2305.05176) e *RouteLLM* (arXiv 2406.18665): modelo barato primeiro, modelo maior só quando preciso.

O que os papers acrescentam ao método do caso:

1. a escolha é por prompt, não por sistema;
2. a unidade medida é o par modelo e versão do prompt: trocar qualquer um dos dois exige medir de novo;
3. o custo medido é por tarefa concluída, contando as novas tentativas;
4. escalonar para um modelo maior é opção de desenho, ao lado da conferência humana.

### 3.2 As três que ficam fora

Registradas para não serem reabertas sem fato novo.

- **Lição 1 (data e hora).** Não foi achado paper que meça "injetar a data atual no prompt". Há benchmarks próximos: SPAN (arXiv 2511.09993), EvolveBench (ACL 2025) e LLMLagBench (arXiv 2511.12116).
- **Lição 2 (missão de cada destino).** MAST (arXiv 2503.13657) relata +9,4% de sucesso com melhor especificação de papéis, mas atribui o número de duas formas. Hong et al. (SIGDIAL 2024) mostram o peso da descrição de cada intenção. Um estudo de 2025 (arXiv 2501.12332) mostra que descrição ingênua vai mal com muitas categorias.
- **Lição 5 (falha de formato).** *Let Me Speak Freely?* (arXiv 2408.02442) confirma a falha de formato em modelo pequeno e o conserto por segunda chamada, mas também mostra que formato rígido piora o raciocínio. A `sdd-loop-builder` já prevê uma nova tentativa de JSON estrito.

## 4. Escopo fixado

Decisão do Roberto em 2026-11-15. São sete itens em dois grupos.

### Grupo A — lições no produto que o aluno constrói

| Item | Onde o Open está hoje | O que entra |
|---|---|---|
| A1. Descrição de ferramenta (lição 3) | a seção `<tools>` de `prompt-building-rules.md` tem duas linhas e manda mencionar "de forma breve" o que está resolvido na API; o inventário de `LLM_PROMPTS_DESIGN.md` só lista prompts | o nome é o verbo do efeito; a descrição diz o efeito; a irreversível aponta a alternativa de só leitura |
| A2. Validação em código (lição 4) | a `sdd-seguranca` tem o item "agente com poder demais"; a `sdd-loop-builder` exige `NEEDS_APPROVAL` em ação irreversível; o contrato por prompt do DESIGN não tem campo para isso | argumento de ferramenta com efeito externo é validado em código, declarado no contrato do DESIGN |
| A3. Conferência como saída prevista (lição 6) | `<missing_context_rules>` diz "em execução autônoma, não fazer perguntas"; o contrato tem "Autônomo? sim ou não" | "preciso que o responsável confira" vira valor previsto da saída, com gatilhos e forma; o gabarito diz onde ela é aceita |
| A4. Modelo por evidência (lição 7) | a coluna `Provedor/Modelo` do inventário é preenchida sem método; o atributo "Eval mínimo pré-ship" pede só "comando e amostras"; o gate `eval` da `sdd-define` diz "limiar embutido no comando" | protocolo: casos com resposta conhecida, meta por prompt, erro grave com meta zero, repetições, custo por tarefa, teto de gasto, e o modelo mais barato que bate a meta |

### Grupo B — economia do próprio processo do Open

| Item | Onde o Open está hoje | O que entra |
|---|---|---|
| B1. Custo por fase e por feature | só os revisores têm custo registrado (F19: `eval-revisores.sh`, `eval-agree.sh`, `sdd/review/registry.tsv`, `precos.tsv`); as sessões de define, design, build, avaliador, executor do piloto e curador não têm registro | tokens, custo nominal, tempo e rodadas por fase, gravados junto do BUILD_REPORT |
| B2. Modelo por papel | cartógrafo, revisão do design, executor, avaliador e curador rodam no modelo da sessão; `sdd/config.example.yaml` não tem slot de modelo para eles; `contexto-fresco.md` não orienta a escolha | slot de modelo por papel, escolhido pelo método da lição 7, com gabarito tirado do histórico |
| B3. Cadeia de revisão pelos dados | os slots `review.revisor1` e `review.auditor` são preenchidos por decisão de quem usa; o `eval-revisores.sh` conta e não recomenda | regra de decisão a partir dos dados já gravados; no repositório privado, a decisão da cadeia da RDD |

## 5. Ponto de partida medido (B3)

A medição de partida da B3 foi feita com o `eval-revisores.sh` em 2026-11-15, só leitura, sobre as revisões de um
repositório privado. A tabela e a leitura dela saíram deste arquivo por decisão do Roberto (2026-11-16): são dados de
lá, e esta branch de documentos é pública. O que vale para o método: a cadeia de revisão se decide pelo
`eval-revisores.sh` e, desde a `v2.18.0`, também pelo `custo-feature.sh` (fatia B1).

## 6. Como saber se a frente funcionou

Três números por feature publicada, comparados com as dez anteriores:

1. custo nominal total da feature;
2. rodadas até o Verify Gate ficar verde;
3. achados com dano que escaparam para produção.

Se o terceiro subir, a economia não valeu.

## 7. Recomendações para o brainstorm

São recomendações, não decisões.

- **Fatiar.** Sete itens não cabem numa sessão. Ordem sugerida: B1 primeiro, porque sem custo registrado nenhuma economia se demonstra; depois B3, que usa só dado já gravado; depois B2; por fim o Grupo A.
- **B1 agnóstico de vendor.** O custo da sessão vem do registro de cada agente. Um adaptador por agente, como os de `bin/adapters/` da revisão.
- **B2 com gabarito do histórico.** Achados classificados nos ledgers, deltas do curador aceitos ou recusados, vereditos do avaliador. Curador e cartógrafo são os primeiros candidatos a modelo menor.
- **A4 conta, não chama.** Seguir o padrão do `eval-revisores.sh`: o script lê arquivos de resultado e conta; quem roda os modelos é o projeto.

## 8. Decisões abertas

1. **A1:** as definições de ferramenta entram no inventário de `LLM_PROMPTS_DESIGN.md` como material de referência da linha do prompt?
2. **A3:** como o gabarito marca onde a conferência é aceita, e há teto de conferências por agente?
3. **B1:** a moeda é custo nominal, tokens ou tempo? Com assinatura, o custo pago é perto de zero.
4. **B1:** de onde sai o custo quando o agente não registra tokens?
5. **B3:** o 2º revisor é dispensado por classe de risco da mudança, ou trocado de modelo?
6. **Starter:** o protocolo A4 precisa de versão sem terminal (planilha de casos e conferência à mão). O caso entra como segundo exemplo, ao lado do `baixar-nfse`?
7. **Dados do caso:** o HTML é um resumo. Para virar exemplo, faltam os casos e as execuções brutas, com os dados do escritório limpos.

## 9. Pendências de registro

- A linha da F23 na tabela *Estado das frentes* do plano ainda não existe. Ela só é editada na worktree `~/rdd-worktrees/sdd-open-docs-f16` (branch `docs/incorporar-starter`), com commit e push na mesma sessão.
- Toda frente deixa a suíte verde também no Windows (regra desde a `v2.16.1`).
- A tabela da seção 5, com dados de um repositório privado, saiu do arquivo antes do commit (decisão do Roberto, 2026-11-16).

## 10. Fontes

- Smell-Aware Evaluation of MCP Server Descriptions — https://arxiv.org/abs/2602.18914
- MCP Tool Descriptions Are Smelly! — https://arxiv.org/abs/2602.14878
- AgentSpec — https://arxiv.org/abs/2503.18666
- Policy Compiler for Secure Agentic Systems — https://arxiv.org/abs/2602.16708
- Reason Less, Verify More — https://huggingface.co/papers/2607.07405
- Agent-C — https://arxiv.org/abs/2512.23738
- Why Language Models Hallucinate — https://arxiv.org/abs/2509.04664
- AbstentionBench — https://arxiv.org/abs/2506.09038
- Why Do Multi-Agent LLM Systems Fail? — https://arxiv.org/abs/2503.13657
- AI Agents That Matter — https://arxiv.org/abs/2407.01502
- Holistic Agent Leaderboard — https://arxiv.org/abs/2510.11977
- Adding Error Bars to Evals — https://arxiv.org/abs/2411.00640
- τ-bench — https://arxiv.org/abs/2406.12045
- How good is your harness? — https://icml.cc/virtual/2026/68323
- Stop Comparing LLM Agents Without Disclosing the Harness — https://arxiv.org/abs/2605.23950
- PromptBridge — https://arxiv.org/abs/2512.01420
- How Do AI Agents Spend Your Money? — https://arxiv.org/abs/2604.22750
- FrugalGPT — https://arxiv.org/abs/2305.05176
- RouteLLM — https://arxiv.org/abs/2406.18665
- Small Language Models are the Future of Agentic AI — https://arxiv.org/abs/2506.02153
- SPAN — https://arxiv.org/abs/2511.09993
- LLMLagBench — https://arxiv.org/abs/2511.12116
- Hong et al., SIGDIAL 2024 — https://aclanthology.org/2024.sigdial-1.39
- Automatic Labelling with Open-source LLMs — https://arxiv.org/abs/2501.12332
- Let Me Speak Freely? — https://arxiv.org/abs/2408.02442
- JSONSchemaBench — https://arxiv.org/abs/2501.10868
