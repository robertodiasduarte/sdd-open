# HANDOFF: F23 Economia mensurável

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Objetivo** | O Open passa a medir o custo de cada fase e feature e a escolher modelo e cadeia de revisão por evidência; o aluno recebe o mesmo método para o produto que constrói. |
| **Status** | 🚢 fatia B3 publicada: `v2.19.0` (`main` = `5e110b2`, PR #35; curadoria da B3 em `fb7ee82` na `main`), 2026-11-16; B1 em `v2.18.0`. Falta gerar o starter (OK à parte) e as fatias B2 e Grupo A |
| **Última sessão** | 2026-11-16 |
| **Branch / pasta** | B3: `feat/f23b3-cadeia-revisao` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f23b3-cadeia-revisao` (nascida de `origin/main` em `ef217b9`); a da B1 já foi removida |
| **Artefatos** | B1: `sdd/features/{ESCOPO,BRAINSTORM,DEFINE,DESIGN}_F23_ECONOMIA_MENSURAVEL.md` e afins · B3: `sdd/features/{DEFINE,DESIGN}_F23B3_CADEIA_REVISAO.md`, `sdd/reports/{BUILD_REPORT,CUSTO}_F23B3_CADEIA_REVISAO.md`, `sdd/reviews/LEDGER_REVISAO_F23B3_CADEIA_REVISAO.md`, `sdd/releases/F23B3_CADEIA_REVISAO/b3_v2.19.0.yaml`, `sdd/reports/evidence/F23B3_CADEIA_REVISAO/`, `sdd/reports/reviews-medicao/F23B3_CADEIA_REVISAO/` — todos na branch de documentos `docs/incorporar-starter` |
| **Verify Gate** | 🟢 0 em `5e110b2` (2.364 testes, 3 pulados) — `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23B3_CADEIA_REVISAO.md`; CI do PR #35 18 de 18; release `v2.19.0` 23:00 UTC, `shasum -c` OK (prefixo `359945f08eab`) |

## Feito

- **Fatia B3 publicada na `v2.19.0`** (`ef217b9..5e110b2`, 11 commits, mais a curadoria `fb7ee82`): 2º revisor só por superfície de risco (lista única de termos, português, camelCase) ou revisor raso, com a regra antiga como medida; desempate padrão e dispensa à mão no META; ledger com `rodada=D<n>`, `sem resultado:` e `escapou:`; `eval-revisores.sh` com a cadeia por frente e `--precos`; codex com modelo padrão e cache no META; prompts em `sdd/review/prompts/v2/` com o material cercado; skills build 2.12.0, design 2.9.0, release 2.15.0. Custo da fatia: US$ 65,57 + n/d nominal (`CUSTO_F23B3_CADEIA_REVISAO.md`).
- **Prova da B3:** na própria B3, 3 rodadas de código sem 2º revisor pela regra (a antiga o chamaria por 33 a 36 arquivos), US$ 11,68 de nominal estimado evitado, 0 dispensa à mão do 2º revisor, 0 escape, fora da conta 0 (`reviews-medicao/F23B3_CADEIA_REVISAO/EVAL-REVISORES.log`); F23 refeita: fora da conta 2 → 0, sem classificar 6 → 0. S18 em 2 sondas reais: série B 3 de 3, mas a v1 também passou (sem ganho medido).
- **Fatia B1 publicada na `v2.18.0`** (`8f944fc..ef217b9`, 9 commits): `sdd/bin/marca-fase.sh`, `sdd/bin/custo-feature.sh`, `sdd/bin/adapters/sessao-claude.py` e `sessao-codex.py`, `sdd/review/precos-cache.tsv`, `sdd/templates/fragments/MARCA_FASE.md`, 6 skills de fase (brainstorm 2.5.0, define 2.8.0, ux-review 2.7.0, design 2.8.0, build 2.11.0, release 2.14.0), troca do starter na `sdd-brainstorm`, docs, `tests/test_f23_custo.py` (35 testes).
- **Prova:** Verify Gate verde em `ef217b9`; CI do PR #34 18 de 18 (run 43851918816); baseline vermelho, mutante do agrupamento derrubado e um teste vermelho→verde por achado de revisão (`evidence/F23_ECONOMIA_MENSURAVEL/`).
- **Revisão:** 1 rodada do DESIGN e 5 do código (4ª e 5ª acima do teto, decisões do Roberto); `--conferir` CONFERE em `ef217b9` (`EXTERNAL_REVIEW_20261116-075121`), 2º revisor dispensado pelo Roberto (cadeia do Open).
- **Linha de base F4–F22** (critério de sucesso 3): `evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/LINHA-DE-BASE.log` — 21 frentes com custo de sessões, de US$ 15,39 a US$ 182,65; F11, F16W2 e F19 n/d (sessões em pasta de outra frente); revisão das frentes antigas n/d (META sumiu com as worktrees), só a F12 tem US$ 13,20 + n/d. Tarifas em `linha-de-base/precos/` (fora do pacote).
- **Custo da própria F23** até o build (marcas reconstituídas do registro da sessão, campo `origem`): brainstorm US$ 3,85 · define 2,73 · design 3,53 · build 16,05 · revisão 4,86 + n/d — total US$ 31,03 + n/d nominal.
- `cleanupPeriodDays: 365` em `~/.claude/settings.json` (OK do Roberto, 2026-11-15).

## Decisões tomadas (Roberto, 2026-11-15)

| # | Decisão | Resposta |
|---|---|---|
| D-fatia | Ordem das fatias | **B1 → B3 → B2 → Grupo A**. A B1 só mede (cria a régua); a economia aparece a partir da B3. |
| ESCOPO-3 | Moeda da B1 | Gravar **tokens, pago, nominal e tempo**; **nominal** é o número principal. Mesmo vocabulário do `eval-revisores.sh` (pago · nominal · n/d, n/d nunca zero). |
| ESCOPO-4 | Origem do custo de uma fase | **Adaptador por agente lê o registro local da sessão** (Claude Code: `~/.claude/projects/<pasta>/<sessão>.jsonl`, `usage` por mensagem; Codex: `~/.codex/sessions/AAAA/MM/DD/*.jsonl`, eventos `token_count`). Nominal = tokens × `sdd/review/precos.tsv`, **cache cobrado à parte**; sem registro legível = n/d. |
| nova | Divisão do custo de uma sessão entre fases | **Cada skill de fase grava marca de início e fim** (fase, feature, horário) por um script pequeno; o adaptador corta o registro pelos horários; trecho fora de marca = "sem fase". Mexe nas skills de fase ⇒ regenerar o starter. |
| ESCOPO-5 | 2º revisor (B3) | **Dispensar por classe de risco**: roda só com superfície de risco (mesma lista do `sdd-fluxo.sh review-design`: termo de segurança, `security_globs`, `layers.sql`) ou com discordância revisor × auditor; dispensa registrada no ledger com motivo; a regra volta atrás se "achados com dano que escaparam" (seção 6) subir. Fechar antes as linhas que o `eval-revisores.sh` deixa fora da conta. |
| ESCOPO-1 | Descrição de ferramenta (A1) | **Linha própria no inventário, `Tipo=ferramenta`**, com contrato: nome = verbo do efeito, efeito e reversibilidade, alternativa só leitura quando irreversível, argumentos com efeito externo e a validação em código de cada um (absorve o A2). `design-lint.py` passa a conferir. |
| ESCOPO-2 | Conferência no gabarito (A3) | **Cada caso diz `responder`, `conferir` ou `tanto faz`**. Conferir num `responder` = erro simples; responder num `conferir` = erro, **grave** se o contrato marca dinheiro ou tributo. Sem teto numérico; relatório mostra a taxa de conferência ao lado do acerto. |
| ESCOPO-7 | Dados brutos do caso | **Condicional, sem bloquear**: se existirem limpos quando o Grupo A chegar ao Design, o caso entra como exemplo; senão, 3 casos ilustrativos e o caso só citado como origem, sem os números virarem fato. |
| ESCOPO-6 | A4 no starter | **Planilha-molde + passo a passo, sem terminal** (casos com o esperado, resultado por modelo e repetição, contagem por fórmula: acerto, erro grave, taxa de conferência, custo por tarefa). O caso entra como 2º exemplo só se os dados brutos limpos chegarem; senão, 3 casos ilustrativos marcados como tal. |

## Falta

1. **Starter:** gerar de novo pela tag `v2.19.0` (os arquivos de modo da build, design e release mudaram de versão); pede OK à parte ("pode publicar o starter").
2. **Próxima fatia: B2** (modelo por papel), com `sdd-define` a partir do bloco 2 do BRAINSTORM; a economia maior está nas sessões (US$ 65 nesta fatia contra US$ 12 de revisão).
3. **Pendências da B3** (Casos e testes em aberto): preço do modelo do codex conferido na fonte, fora do pacote; `test_checar` instável; versão do prompt no META; aviso de prompt v1 editado.
4. ~~Curadoria da B1~~ — `e1870e3` (LM-035, LM-036); ~~curadoria da B3~~ — `fb7ee82` na `main` (20 contagens, LM-037, refine da LM-011, LM-038).

## Definition of Done

- [x] BRAINSTORM gravado com as 7 decisões da seção 8 do ESCOPO e a prova por fatia.
- [x] Fatia B1 publicada, com Verify Gate e CI verdes.
- [x] Linha de base das features anteriores (≥ 15 linhas com custo).
- [x] Tabela da seção 5 do ESCOPO: saiu do arquivo (decisão do Roberto, 2026-11-16).
- [ ] Fatias B3, B2 e Grupo A.

## ⛔ Landmines desta feature

- **Somar o `usage` linha a linha infla o custo:** o Claude Code repete a mesma mensagem até 13 vezes; agrupe por `message.id` (candidato ao playbook).
- **Skill do starter que cita `sdd/bin/`** derruba o gerador e 30 testes; rode `test_gerar_starter` antes do gate (candidato ao playbook).
- **O `$` do Python aceita "nome\n"**: use `\Z` em padrão que valida entrada (R2 da rodada 4).
- **Argumento com quebra de linha não chega no Windows**: teste desse caso precisa de `SEM_ARGV_COM_QUEBRA`.
- **A revisão leva os não rastreados para o diff**: o ESCOPO (tabela privada) ficou fora por um `.gitignore` local que ignora a si mesmo; tire-o antes do `report-lint`, que reprova evidência ignorada.
- **Cache criado do Claude Code é de 1 hora** (2× a entrada): a tabela de preço precisa da validade certa.
- **O qwen passa do teto de tempo com diff de ~150 KB** (2 de 4 rodadas); o codex auditou a 5ª.

## Casos e testes em aberto

- 🐛 `test_checar.TestRemoto.test_rede_pendurada_inteira_api_e_remoto`: teto de 12 s rente ao tempo medido (12,02 e 12,10 s), cai até sozinho (B3).
- ✨ Nominal do codex n/d nas rodadas reais: falta o preço do modelo, conferido na fonte, em `linha-de-base/precos/` (B3).
- ✨ O META não grava a versão do prompt: o medidor mistura v1 e v2; o codex antigo (`codex (-)`) e o novo saem em linhas separadas (raio de impacto da B3).
- ✨ Prompt v1 editado à mão deixa de ser lido sem aviso depois do upgrade (raio de impacto da B3).
- ✨ Promoção possível: o Verify Gate rodar o `publish-gate` e o `test_conversa` antes da suíte (LM-037, LM-038).
- 🐛 Sessão do Codex com `session_meta` ilegível some da conta sem n/d (R1 da rodada 5).
- ✨ Mapa da linha de base só com features inválidas sai MEDIDO vazio, não 64 (R2 da rodada 5).
- ✨ Sessões concorrentes no mesmo projeto subcontam o tempo ativo (N1 da rodada 5).
- ✨ Registro ilegível fora da janela deixa o relatório parcial a mais (R3 da rodada 3).
- ✨ `cache_creation` não separa 5 min de 1 hora: o preço do cache criado é um só por modelo.

## Eventos

- 2026-11-16 — B3: passo 0 (curadoria da B1, `e1870e3`); Define com 7 decisões do Roberto (prova trocada, discordância = desempate, auditor codex local, dano que escapa pela linha `escapou`, raso continua, governança dispensada, S18 aplicado e S20 recusado); Design com pasta `v2/` e lista ampliada; build com 3 gates vermelhos (MANIFEST, teto de 500 linhas, `foto()` da F22 consertada com OK do Roberto) e verde em `5e110b2`; raio de impacto achou camelCase e o gate offline; 3 rodadas de revisão + dispensa escrita do delta (Roberto); push autorizado ("sim, pode publicar"): `v2.19.0`; curadoria da B3 enviada à `main` ("Enviar agora").
- 2026-11-16 — 4ª rodada (OK do Roberto) sobre `b606eca`: 3 achados aplicados com teste (`ef217b9`), sem auditor (qwen passou do teto pela 2ª vez); a revisão não confere a versão final. CI do Windows pegou 1 teste que não vale lá (quebra de linha em argumento), consertado em `b606eca`. Parado na decisão da 5ª rodada.
- 2026-11-16 — Roberto: "execute o pipeline até o release" (lido como OK do fatiamento). Define da B1 (10 ATs; governança dispensada pelo Roberto como na F19; S17 aplicado), DESIGN (9 decisões; revisão do DESIGN em 1 rodada), build em `67b002b..b494810`, 3 rodadas de revisão do código (17 aplicados), Verify Gate verde em `b494810`, linha de base F4–F22 (`evidence/…/linha-de-base/LINHA-DE-BASE.log`), `cleanupPeriodDays: 365` em `~/.claude/settings.json`. Branch publicada e PR #34 aberto para o CI. Marcas da F23 antes do script reconstituídas do registro da sessão (campo `origem`).
- 2026-11-15 — Escopo fixado pelo Roberto (Grupo A: A1–A4; Grupo B: B1–B3). Lições 1, 2 e 5 fora (ESCOPO §3.2).
- 2026-11-15 — Brainstorm iniciado; 6 decisões tomadas; pausado antes da decisão 7 porque o Roberto ia embarcar.
- 2026-11-15 — Decisão 7 respondida (condicional, sem bloquear); as 7 da seção 8 estão fechadas. Próxima: perfil de risco.
- 2026-11-15 — Perfil de risco confirmado ("ok"): (1) ver: relatório de custo é público no Open ⇒ o adaptador extrai só números (tokens, horários, modelo, custo), nunca texto da conversa, caminho ou argumento de ferramenta; planilha do A4 fica com o aluno. (2) mudar: o adaptador só lê os registros do agente; marcas gravadas pelas skills numa pasta do projeto; preços e regra do 2º revisor só por commit revisado. (3) pedir: B1/B3/B2 não chamam modelo; medição paga do A4 e da B2 com teto de gasto fechado e trava automática, rodada pelo projeto. Próxima: amostras.
- 2026-11-15 — Achado: há registro local do Claude Code de todas as frentes F4 a F23 (`~/.claude/projects/-Users-robertoduarte-rdd-worktrees-sdd-open-*/`, 1 a 3 sessões cada, o mais antigo de 2026-10-29); o Codex tem só 4 sessões. `cleanupPeriodDays` não está configurado (padrão de 30 dias) ⇒ os da F4 a F7 podem sumir a partir de ~2026-11-28.
- 2026-11-15 — Amostra decidida (Roberto): registros de sessão F4–F22 + BUILD_REPORTs + ledgers ancoram a linha de base. Protegidos: `"cleanupPeriodDays": 365` gravado em `~/.claude/settings.json` (com OK do Roberto). Próxima: abordagens.
- 2026-11-15 — Abordagem A (contador próprio: `marca-fase.sh`, adaptadores `sessao-claude.sh`/`sessao-codex.sh` lendo sessão principal + `subagents/`, `custo-feature.sh` somando também os META da revisão sem contar em dobro, coluna de cache em `precos.tsv`, modo linha de base F4–F22 por feature). YAGNI ok: fora adaptador gemini/Cursor, divisão por fase retroativa, tempo de espera humana (grava tempo ativo do agente), cota de assinatura, painel, alerta de orçamento em sessão. Próxima: validação.
- 2026-11-15 — Validações (bloco 1: B1; bloco 2: B3, B2, Grupo A e prova por fatia) confirmadas; BRAINSTORM gravado. Itens 2 a 6 de "Falta" feitos; falta o item 7 (OK do fatiamento) e as tarefas 3 e 4. ATENÇÃO: o prompt de retomada abaixo é anterior a isto; na retomada, ir direto ao OK do fatiamento e ao `sdd-define` da B1.
- 2026-11-16 — 5ª rodada com o codex auditando (OK do Roberto); dispensa do 2º revisor registrada pelo Roberto; **push autorizado** ("push autorizado ssd-open"): `main` e tag `v2.18.0` em `ef217b9` por `git push --atomic`; PR #34 MERGED; Release conferida.
- 2026-11-16 — Roberto: "pode publicar o starter" ⇒ starter `v1.5.23` (PR #16 de lá, fast-forward).
- 2026-11-16 — Roberto: curadoria do playbook da B1 no passo 0 da B3.
- 2026-11-16 — Roberto: a tabela da seção 5 do ESCOPO sai do arquivo (dado do privado; a frase do BRAINSTORM que citava o número também saiu); fechamento feito na branch de documentos.

## Recomendações

- Fazer a curadoria antes de abrir a B3: os 2 candidatos são de superfícies que a B3 e a B2 tocam de novo (skills de fase, leitores de sessão).
- Na B3, usar a linha de base: o 2º revisor custa uma ordem de grandeza menos que as sessões, então a economia maior pode estar no modelo por papel (B2).

## Veredito

- B1: 🟡 CONCERNS (5 rodadas, 2 acima do teto).
- B3: 🟡 CONCERNS — 3 rodadas (teto) e dispensa escrita do delta da 3ª; cerca do S18 sem ganho medido; codex sem preço; `test_checar` instável.

---

## Prompt de retomada

```text
Retomar a feature F23_ECONOMIA_MENSURAVEL (SDD Open), fatia B2 (modelo por papel). Responda sempre em português.

Contexto: B1 publicada na v2.18.0 e B3 na v2.19.0 (main = fb7ee82 com a curadoria da B3). A B3 tirou o 2º revisor do
caminho quando não há risco; na própria B3 a revisão custou US$ 12 contra US$ 53 das sessões: a economia maior é a B2.
Abra uma frente nova com a sdd-new-session (feature_id F23B2_MODELO_POR_PAPEL), nascida de origin/main.
Leia primeiro: sdd/handoffs/HANDOFF_F23_ECONOMIA_MENSURAVEL.md (Falta, Decisões, Casos e testes em aberto), o bloco 2
do sdd/features/BRAINSTORM_F23_ECONOMIA_MENSURAVEL.md (B2: slot de modelo por papel; gabarito do histórico; o mais barato
que bate a meta, com repetições e teto de gasto), e a seção Sempre de sdd/playbook.md (LM-037 e LM-038 são novas).
Antes: o starter da v2.19.0 ainda não foi gerado (OK à parte do Roberto).
Não faça: editar o plano fora da worktree sdd-open-docs-f16; corrigir direto no starter; pôr nome ou preço de modelo
no pacote; número medido no repositório privado em documento do Open.
Landmines: MANIFEST.txt para todo arquivo novo do pacote (LM-037); sdd-release no teto de 500 linhas (LM-038);
prova de prompt com a série da versão antiga primeiro (LM-011); o qwen passa do teto com diff grande (o codex audita).
```

---

## Histórico de slices

### B3 cadeia de revisão pelos dados — 2026-11-16

- Publicada na `v2.19.0` (PR #35, push atômico autorizado pelo Roberto); curadoria `fb7ee82` na `main`. Veredito CONCERNS.
- feature_id `F23B3_CADEIA_REVISAO`; worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f23b3-cadeia-revisao`, branch `feat/f23b3-cadeia-revisao`, nascida de `origin/main` em `ef217b9`.
- Passo 0: curadoria da B1 aplicada (`e1870e3`).
- Define: `sdd/features/DEFINE_F23B3_CADEIA_REVISAO.md` v1.1, Ready for Design, 11 ATs, gate igual ao da B1. Decisões do Roberto (2026-11-16): prova trocada (chamadas do 2º revisor evitadas com custo, zero dispensa à mão, escape com dano caso a caso); discordância = desempate existente ligado por padrão; auditor desta frente = codex e depois o modelo da OpenRouter (escolha local, fora do pacote) e fim do n/d do codex; dano que escapa = linha `escapou` no ledger da frente de origem, revisão da regra caso a caso, sem linha de base; revisor raso continua acionando, registrado à parte; governança dispensada como na B1 (o 1º bloco foi invalidado por um `verify-gate.sh` desta sessão no segundo do snapshot); S18 aplicado (AT-011, os 3 prompts da revisão cercam o diff), S20 recusado ("o teto de tempo basta").
- Achado do Define: desde a F16 o 2º revisor foi dispensado à mão em 11 de 12 frentes (falta de engine); a regra por tamanho o acionava em toda revisão de código da F22 e da F23 (41 a 44 arquivos).
- Design: `sdd/features/DESIGN_F23B3_CADEIA_REVISAO.md` v1.1, Ready for Build, 10 decisões, 20 arquivos. Decisões do Roberto: prompts da revisão em `sdd/review/prompts/v2/` (o script aponta para ela); lista de termos de segurança ampliada com português e termos gerais, mantendo `token`. Revisão D1 (`EXTERNAL_REVIEW_20261116-115325`, claude revisa, codex audita, sem estouro): R1 a R4 e N1 aplicados, R5 rebatido; as linhas `rodada=D1` vão ao ledger depois do build. DEFINE v1.2: o META da 5ª rodada da F23 não tem o modelo do codex, a prova do nominal vai para fixture e 1ª rodada real.
- Build: `e1870e3..cfc87f9` (8 commits), Verify Gate verde em `cfc87f9` (2.356 testes, 3 pulados), BUILD_REPORT `sdd/reports/BUILD_REPORT_F23B3_CADEIA_REVISAO.md` (report-lint verde). Revisão do código: 1 rodada (`EXTERNAL_REVIEW_20261116-155004`, 1 revisor pela regra nova, regra antiga 33 arquivos), 5 achados aplicados com teste (`a84b2e3`), `loop` PRONTO; ledger `sdd/reviews/LEDGER_REVISAO_F23B3_CADEIA_REVISAO.md` com as linhas D1. Prova S18: 2 sondas reais, série B 3 de 3 nas duas, mas a série A (v1) também passou: a cerca fica sem ganho medido. F23 refeita: fora da conta 2 → 0, sem classificar 6 → 0. Conserto de teste da F22 (`cfc87f9`, a `foto()` do upgrade não entra em `.git`), com OK do Roberto.
- Pendências da B3: preço do modelo do codex conferido na fonte (fora do pacote) para o nominal real; `test_checar` com teto de 12 s rente ao tempo medido (instável); a revisão do código não confere `cfc87f9` (o `--conferir` da release vai perguntar: rodada curta ou dispensa); CI do Windows exige push (PR); 3 candidatos ao playbook no BUILD_REPORT.
- Próximo: `/sdd-release` da B3 (com a curadoria `e1870e3`), depois do OK do Roberto.

### B1 custo por fase e por feature — 2026-11-16

- Define (10 ATs), DESIGN (9 decisões), build `67b002b..ef217b9`, 1 + 5 rodadas de revisão, Verify Gate e CI verdes, linha de base F4–F22.
- Publicada na `v2.18.0` (push atômico autorizado pelo Roberto). Veredito CONCERNS.

### Brainstorm, sessão 1 — 2026-11-15

- ESCOPO lido; 7 decisões da seção 8 fechadas; perfil de risco, amostras, abordagem A, YAGNI e 2 validações; BRAINSTORM gravado.
- Pausa para o Roberto embarcar; retomado na mesma sessão.
