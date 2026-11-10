# BRAINSTORM: F19 — Custo e benefício dos modelos de revisão

> Sessão exploratória para fixar a intenção e o caminho antes dos requisitos

## Metadata

| Attribute | Value |
|---|---|
| Feature | F19_CUSTO_REVISORES |
| Date | 2026-11-10 |
| Author | brainstorm-agent (worktree `sdd-open-f21-f19`; a branch `feat/f19-custo-revisores` nasce de `origin/main` depois da `v2.9.0`) |
| Status | Ready for Define |

## Initial Idea

**Raw Input:** pedido do Roberto (2026-11-07): "avaliação de performance de modelos de revisão: custo e benefício: medir o custo do modelo e o que ele detectou de falha real que poderia causar dano à aplicação". Em 2026-11-10: fazer na mesma sessão da F21, depois da release dela.

**Context Gathered:**
- Fato: cada rodada do `sdd/bin/adversarial-review.sh` grava uma pasta `EXTERNAL_REVIEW_<quando>/` com `META.txt` (por papel: engine, modelo com o provedor, custo, tokens, segundos, exit, motivo, achados), `reviewer.verdicts.jsonl`, `reviewer2.verdicts.jsonl` (ids `R1@engine`), `auditor.verdicts.jsonl` (`AGREE`, `DISAGREE_EVIDENCE`, `DISAGREE_CONCERN`, `NOVO`) e `desempate.md` quando há.
- Fato: `sdd/bin/eval-agree.sh` já mede a taxa de AGREE por auditor, lendo só `META.txt` e `auditor.verdicts.jsonl`; exits 0 MEDIDO · 2 SEM DADOS · 64 uso; fixtures em `sdd/fixtures/revisao/eval/`.
- Fato (corrigido depois das perguntas, ainda em 2026-11-10): a decisão por achado (APLICADA, REBATIDA_EVIDENCIA, REBATIDA_ESCOPO) **existe** em ledger de 5 colunas, o que o `sdd-fluxo.sh loop --ledger` lê (`| R1@claude | HIGH | APLICADA | rodada=1 | evidência |`), nas frentes F10 a F14: `sdd/reports/evidence/{F}/ledger-review.md`, na branch de documentos (21 a 43 linhas de tabela cada). F15_SLOTS e F21 registraram só na tabela "Advisor Ledger" do BUILD_REPORT. Em nenhum deles há a marca de dano, e a pasta da rodada só aparece no texto do cabeçalho, não por linha. Na hora das perguntas eu disse ao Roberto que esse ledger nunca tinha sido gravado nas frentes reais: estava errado (procurei por `ledger` só nos arquivos de revisões guardados, não na evidência). As decisões 2 e 3 continuam valendo: o formato novo acrescenta as 2 células que faltam, e o retroativo passa a converter os ledgers que já existem em vez de transcrever texto livre.
- Fato: o custo do `META.txt` vem de 4 formas: `US$ n` reportado pela engine, `≈US$ n` estimado por `sdd/review/precos.tsv`, o literal `assinatura` (codex) e `$?` (desconhecido ou a chamada falhou). O `registry.tsv` diz a cobrança de cada engine (`assinatura`, `pay-per-token`, `desconhecida`). O claude é `assinatura` e reporta o custo de tabela.
- Fato (medido em 2026-11-10 sobre os 5 arquivos de revisões guardados fora do repositório): 21 rodadas únicas (F13: 6; F14 Playbook: 4; F14 Drive: 5 + 2 da v2.7.1; F15 Slots: 4), mais as 4 da F21 feitas nesta sessão. Revisor sempre claude (US$ 0,84 a US$ 3,76 por rodada, nominal). Auditor quase sempre qwen pela OpenRouter (US$ 0,027 a US$ 0,087 pagos). 2º revisor: codex (assinatura; falhou por cota em 2 das arquivadas e nas 3 da F21 em que foi acionado), deepseek (2 respostas, 3 falhas), glm (1 resposta, 1 falha), gemini (1 falha por credencial, exit 65). F10 a F12 não estão arquivadas.
- Fato: o repositório do pacote não tem `.gitignore` e a pasta `sdd/reports/reviews/` é ignorada só pelo `info/exclude` local.

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/eval-revisores.sh` e `sdd/bin/ledger-revisao-lint.sh` (novos), `sdd/review/CRITERIO_DANO.md` (novo), `sdd/templates/` (molde do ledger), `sdd/fixtures/revisao/`, `.agents/skills/sdd-build/` e `sdd-release/` (pedem o ledger), `docs/adversarial-review.md` + PT, `docs/cli-conventions.md`, `tests/`, `MANIFEST.txt` | produto do Open; release `v2.10.0` |
| Relevant KB Domains | nenhum | — |
| IaC Patterns | N/A; CI existente | — |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | O que conta como falha real com dano? | Aplicada + teste + efeito (recomendada): achado APLICADO, cujo conserto trouxe teste que falha no código antigo, e cujo cenário afeta dado, dinheiro, acesso, publicação ou disponibilidade; marca `sim`/`nao`/`?` por quem decide o achado, nunca por outro modelo; REBATIDA_EVIDENCIA = falso positivo; REBATIDA_ESCOPO não conta | critério escrito em `sdd/review/CRITERIO_DANO.md`; `sim` exige o teste citado |
| 2 | Onde fica a decisão por achado? | Arquivo de ledger por frente (recomendada): `sdd/reviews/LEDGER_REVISAO_{F}.md`, no git, com a coluna `dano` e a rodada | o medidor lê só o ledger e os `META.txt`; nada de interpretar texto livre (LM-005) |
| 3 | O relatório só informa ou sugere a cadeia? | Só informa (recomendada), com a amostra ao lado de cada taxa | trocar a cadeia é decisão da pessoa |
| 4 | Como tratar custo de assinatura? | Duas colunas, pago e nominal (recomendada) | custo por falha com dano nas duas bases |
| 5 | Até onde vai o retroativo? | F13 a F15 + F21, `dano` `?` (recomendada): transcrição à mão dos Advisor Ledgers; `sim` só onde o relatório cita o teste | ledgers retroativos e o relatório ficam na branch de documentos; F10 a F12 declaradas fora |
| 6 | Mede o repositório privado? | Não, fica para depois da F15 (recomendada) | o script fica pronto para rodar lá |

**Minimum Questions:** 3 (feitas 6)

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | 5 arquivos de revisões guardados fora do repositório (F13, F14 Playbook, F14 Drive, F14 Drive v2.7.1, F15 Slots) | 21 rodadas únicas | `META.txt` em todas; `auditor.verdicts.jsonl` em 18; `reviewer2.verdicts.jsonl` em 10; 5 rodadas aparecem em 2 arquivos (a v2.7.1 repete as do Drive) |
| Input files | `sdd/reports/reviews/EXTERNAL_REVIEW_20261110-*` da F21 | 4 completas | mais 1 interrompida por quem despachou, sem `META.txt` completo |
| Output examples | saída do `eval-agree.sh` | 1 | molde de tabela e de `RESULTADO:` |
| Ground truth | `sdd/reports/evidence/{F}/ledger-review.md` de F13, F14 Playbook e F14 Drive (5 colunas, branch de documentos); Advisor Ledger do BUILD_REPORT de F15_SLOTS e da F21 | 5 | fonte do retroativo: 3 conversões e 2 transcrições |
| Related code | `sdd/bin/eval-agree.sh`, `sdd/bin/sdd-fluxo.sh` (leitor do ledger), `sdd/fixtures/revisao/eval/` | 3 | reuso de formato e de fixtures |

**How samples will be used:**
- Os `META.txt` reais fixam os casos que as fixtures do pacote reproduzem com dados inventados: custo reportado, estimado, `assinatura`, `$?`, exit 65 e 67, 2º revisor ausente, o mesmo modelo por provedores diferentes.
- Nenhum arquivo real entra no pacote; o retroativo fica na branch de documentos.

## Approaches Explored

### Approach A: Script novo `eval-revisores.sh` — Recomendada

**Description:** script só de leitura, sem rede, ao lado do `eval-agree.sh`: lê as pastas `EXTERNAL_REVIEW_*` e os `LEDGER_REVISAO_*.md` e imprime uma linha por papel + engine + modelo. Lint do ledger em script próprio. Critério em `sdd/review/`.

**Pros:**
- não muda o contrato do `eval-agree.sh`;
- duas perguntas, dois scripts (o auditor audita? o revisor vale o que custa?).

**Cons:**
- 2 scripts a mais em `sdd/bin/`.

**Why Recommended:** conta o que está registrado, com fixtures dos dois lados, sem juiz.

### Approach B: Estender o `eval-agree.sh`

**Pros:** um script só. **Cons:** muda contrato com testes e documentação; mistura as duas perguntas.

### Approach C: Planilha manual

**Pros:** nenhum código. **Cons:** não se repete sozinho, sem teste.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | Roberto, 2026-11-10, na conversa: "A — Script novo eval-revisores.sh (Recomendado)" |
| Reasoning | contrato novo sem mexer no antigo |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | Critério de dano "aplicada + teste + efeito", marcado por quem decide | o plano; sem viés de juiz | severidade do revisor; sem exigir teste |
| 2 | `sdd/reviews/LEDGER_REVISAO_{F}.md`: `| achado | sev | veredito | dano | rodada | evidência |`; `achado` com `@engine`; `rodada` é a pasta `EXTERNAL_REVIEW_*`; `dano` `sim`/`nao`/`?`; `?` só em ledger marcado retroativo; `sim` exige o teste na evidência | fonte estruturada | ler o Advisor Ledger |
| 3 | `ledger-revisao-lint.sh` reprova linha sem `dano`; o formato de 5 colunas segue aceito pelo `sdd-fluxo.sh loop` | compatível | quebrar o leitor do loop |
| 4 | Uma linha por papel + engine + modelo com provedor; colunas: rodadas, falhas por motivo, pago, nominal, achados, aplicados, com dano, falsos positivos, sem classificar, custo por falha com dano (2 bases), taxa de AGREE; amostra ao lado de cada taxa | validado pelo Roberto (validação 1) | agrupar só por engine |
| 5 | Pago = soma dos custos das engines `pay-per-token`; nominal = soma de todo custo informado ou estimado; `assinatura` sem valor e `$?` contam como "n/d" e aparecem na amostra | pergunta 4 | uma coluna só |
| 6 | Só informa; nenhuma recomendação de cadeia | amostra pequena | sugerir |
| 7 | `sdd-build` e `sdd-release` passam a pedir o ledger no lugar da tabela solta | validado (validação 2); sem isso o lint não exige nada | deixar opcional |
| 8 | Retroativo F13 a F15 + F21 na branch de documentos; F10 a F12 declaradas fora; privado depois da F15 | perguntas 5 e 6 | só F21 |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| Sugestão automática de cadeia no `registry.tsv` | amostra pequena; decisão da pessoa | Yes |
| Medir o repositório privado | fora desta sessão | Yes |
| Saída em JSON ou CSV | ninguém consome ainda | Yes |
| Gráfico ou painel | idem | Yes |
| Reprocessar F10 a F12 | não arquivadas | No |
| Outro modelo classificando o dano | viés de juiz | No |
| Coluna de tempo por rodada | o `META.txt` já traz; fora do pedido | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Colunas e agrupamento do `eval-revisores.sh` | ✅ | "Está certo (Recomendado)" | No |
| Ledger por frente, lint, critério e as duas skills pedindo o arquivo | ✅ | "Está certo, pode gravar (Recomendado)" | No |

**Minimum Validations:** 2 (feitas 2)

## Suggested Requirements for /define

### Problem Statement (Draft)
Hoje a cadeia de revisão é escolhida por impressão: o custo de cada engine está espalhado em `META.txt` por rodada, a decisão por achado está em texto livre, e "falha real com dano" não tem critério escrito.

### Target Users (Draft)
| User | Pain Point |
|---|---|
| Quem paga a revisão | não sabe quanto cada engine custou nem o que ela achou que valia o conserto |
| Quem decide os achados | registra a decisão em tabela solta, que nenhuma ferramenta lê |
| Mantenedor do Open | não tem como dizer se o 2º revisor vale o que custa |

### Success Criteria (Draft)
- [ ] `eval-revisores.sh` sai 0 sem rede sobre as fixtures e imprime a tabela por papel, engine e modelo
- [ ] ledger novo sem `dano` reprova no lint; `sim` sem teste citado reprova; `?` fora de retroativo reprova
- [ ] os casos reais aparecem nas fixtures: mesmo modelo por 2 provedores com custo diferente; engine com exit 65; engine com exit 67; assinatura com nominal e pago zero; auditor que repete um NOVO rebatido
- [ ] relatório retroativo de F13 a F15 + F21 com a amostra por engine
- [ ] `publish-gate.sh` e o Verify Gate verdes

### Constraints Identified
- bash 3.2 + Python ≥ 3.9 stdlib; sem rede; só leitura.
- Nomes de engine são dado do `registry.tsv`, não texto de skill (P2).
- Nada de outro repositório entra aqui; fixtures com dados inventados.
- `git add` por caminho (lição da F21).

### Out of Scope (Confirmed)
- Repositório privado; F10 a F12; sugestão de cadeia; JSON/CSV; juiz por modelo.

## Session Summary

| Metric | Value |
|---|---|
| Questions Asked | 6 de descoberta (amostras: os arquivos de revisões guardados, indicados no pedido da sessão) |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 2 |
| Duration | ~20 min |

## Next Step

**Ready for:** `/sdd-define sdd/features/BRAINSTORM_F19_CUSTO_REVISORES.md`
