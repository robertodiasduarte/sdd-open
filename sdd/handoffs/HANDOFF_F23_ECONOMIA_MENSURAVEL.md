# HANDOFF: F23 Economia mensurável

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Objetivo** | O Open passa a medir o custo de cada fase e feature e a escolher modelo e cadeia de revisão por evidência; o aluno recebe o mesmo método para o produto que constrói. |
| **Status** | 🚢 fatia B1 publicada e fechada: `v2.18.0` (`main` = `ef217b9`, PR #34) e starter `v1.5.23` (PR #16 de lá), 2026-11-16; a próxima é a B3, com a curadoria da B1 no passo 0 |
| **Última sessão** | 2026-11-16 |
| **Branch / pasta** | `feat/f23-economia-mensuravel` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f23-economia-mensuravel` (nascida de `origin/main` em `8f944fc`) |
| **Artefatos** | `sdd/features/{ESCOPO,BRAINSTORM,DEFINE,DESIGN}_F23_ECONOMIA_MENSURAVEL.md` · `sdd/reports/BUILD_REPORT_F23_ECONOMIA_MENSURAVEL.md` · `sdd/reviews/LEDGER_REVISAO_F23_ECONOMIA_MENSURAVEL.md` · `sdd/releases/F23_ECONOMIA_MENSURAVEL/s1_v2.18.0.yaml` · `sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/` — todos sem commit nesta branch; vão para `docs/incorporar-starter` (worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16`) |
| **Verify Gate** | 🟢 0 em `ef217b9` (2.315 testes, 3 pulados) — `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23_ECONOMIA_MENSURAVEL.md` |

## Feito

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

1. ~~Conferir a Release~~ — feito: publicada em 2026-11-16T12:18:57Z (run 43858612673), `shasum -a 256 -c` OK (prefixo `a8965ca6ad25`), `VERSION` = `v2.18.0`.
2. ~~Custo final~~ — feito: `sdd/reports/CUSTO_F23_ECONOMIA_MENSURAVEL.md`, US$ 49,28 + n/d nominal (release US$ 14,16; revisão 8,21 + n/d em 7 rodadas); 8 voltas do gate, verde na 6ª.
3. ~~Starter~~ — feito: 7ª geração pela tag `v2.18.0` num clone limpo (branch `feat/f23-setima-geracao`, `4269afe`; 11 arquivos, só versões de 5 skills e `GERADO.txt`, nada da marca); `check-gerado` verde, 62 testes OK; PR https://github.com/robertodiasduarte/sdd-starter/pull/16, CI verde, fast-forward na `main` (`56d9487..4269afe`, OK do Roberto: "pode publicar o starter"); Release **`v1.5.23`** em 2026-11-16T12:26:33Z, 18 zips OK no `shasum -c`.
4. **Curadoria do playbook no passo 0 da B3** (decisão do Roberto, 2026-11-16): 2 candidatos no BUILD_REPORT (skill do starter que cita `sdd/bin`; `usage` repetido do registro de sessão), pelo item 17b da `sdd-release` (`bash sdd/bin/playbook-curator.sh --preparar F23_ECONOMIA_MENSURAVEL`).
5. ~~Fechamento nos documentos~~ — feito em 2026-11-16 na worktree `sdd-open-docs-f16`: documentos da frente, medição dos revisores (`sdd/reports/reviews-medicao/F23_ECONOMIA_MENSURAVEL/`), linha da F23 em "Estado das frentes" e Cronograma do plano; o ESCOPO foi sem a tabela da seção 5.
6. **Próxima fatia: B3** (cadeia de revisão pelos dados), com `sdd-define` a partir do BRAINSTORM (bloco 2).

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

- 🐛 Sessão do Codex com `session_meta` ilegível some da conta sem n/d (R1 da rodada 5).
- ✨ Mapa da linha de base só com features inválidas sai MEDIDO vazio, não 64 (R2 da rodada 5).
- ✨ Sessões concorrentes no mesmo projeto subcontam o tempo ativo (N1 da rodada 5).
- ✨ Registro ilegível fora da janela deixa o relatório parcial a mais (R3 da rodada 3).
- ✨ `cache_creation` não separa 5 min de 1 hora: o preço do cache criado é um só por modelo.

## Eventos

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

- 🟡 CONCERNS — 5 rodadas de revisão (4ª e 5ª acima do teto); 3 achados da 5ª como pendência; 2º revisor dispensado pelo Roberto (`review_externo` no ledger da release).

---

## Prompt de retomada

```text
Retomar a feature F23_ECONOMIA_MENSURAVEL (SDD Open). Responda sempre em português.

Contexto: a fatia B1 (custo por fase e por feature) foi publicada na v2.18.0 (main = ef217b9, PR #34). Starter v1.5.23 e
fechamento nos documentos feitos. A frente segue com as fatias B3, B2 e Grupo A.
Pasta: /Users/robertoduarte/rdd-worktrees/sdd-open-f23-economia-mensuravel · branch feat/f23-economia-mensuravel.
Leia primeiro: sdd/handoffs/HANDOFF_F23_ECONOMIA_MENSURAVEL.md (Falta e Decisões), depois
sdd/reports/BUILD_REPORT_F23_ECONOMIA_MENSURAVEL.md e sdd/features/BRAINSTORM_F23_ECONOMIA_MENSURAVEL.md.
Estado do gate: `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23_ECONOMIA_MENSURAVEL.md` saiu 0 em ef217b9 (2026-11-16).

Próxima ação: abrir a fatia B3 (cadeia de revisão pelos dados). Passo 0: a curadoria do playbook da B1
(`bash sdd/bin/playbook-curator.sh --preparar F23_ECONOMIA_MENSURAVEL`, item 17b da sdd-release); depois
`sdd-define` a partir do bloco 2 do BRAINSTORM, com a linha de base de
sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/LINHA-DE-BASE.log.
Não faça: editar o plano fora da worktree
sdd-open-docs-f16; corrigir direto no starter; pôr nome ou preço de modelo no pacote.
Landmines: o adversarial-review.sh leva os não rastreados para o diff (use .gitignore local que ignora a si mesmo e
tire antes do report-lint); `$` em regex Python aceita quebra final (use \Z); o qwen passa do teto com diff grande.
```

---

## Histórico de slices

### B1 custo por fase e por feature — 2026-11-16

- Define (10 ATs), DESIGN (9 decisões), build `67b002b..ef217b9`, 1 + 5 rodadas de revisão, Verify Gate e CI verdes, linha de base F4–F22.
- Publicada na `v2.18.0` (push atômico autorizado pelo Roberto). Veredito CONCERNS.

### Brainstorm, sessão 1 — 2026-11-15

- ESCOPO lido; 7 decisões da seção 8 fechadas; perfil de risco, amostras, abordagem A, YAGNI e 2 validações; BRAINSTORM gravado.
- Pausa para o Roberto embarcar; retomado na mesma sessão.
