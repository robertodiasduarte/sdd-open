# BUILD REPORT: F17b — starter gerado, etapa 2

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17B_STARTER_ETAPA2 |
| **Date** | 2026-11-13 |
| **Author** | build-agent (worktree `sdd-open-f17b-starter-etapa2`, branch `feat/f17b-starter-etapa2`, de `d813954` = `v2.13.0`) |
| **DEFINE** | [DEFINE_F17B_STARTER_ETAPA2.md](../features/DEFINE_F17B_STARTER_ETAPA2.md) v1.1 |
| **DESIGN** | [DESIGN_F17B_STARTER_ETAPA2.md](../features/DESIGN_F17B_STARTER_ETAPA2.md) v1.1 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 16/16 linhas do manifest do DESIGN v1.1 |
| **Files Created** | 76 no pacote: `.agents/skills/ux-review-builder/` (19, porte da 1.4.0 do starter), `.agents/skills/sdd-release/references/MODO_INICIANTE.md`, `scripts/starter/modos.tsv`, `scripts/starter/raiz/{docs,exemplos,tests}/` (48, semente: o starter `v1.5.17`), 4 arquivos de trocas e 1 de molde, `tests/test_f17b_passo0.py`, `tests/test_f17b_textos.py` |
| **Commits** | passo 0: `ce281d7` · build: `99283ae`, `c8826b7` · revisão e raio de impacto: `1a71e1a`, `e583889` · avaliador: `1d8fc65`, `f9a0af1` |
| **Tests Passing** | exit 0 em `e583889`: 2.123 testes em 36 min, 1 pulado (`evidence/F17B_STARTER_ETAPA2/VERIFY-GATE-e583889.log`); partida: 2.090 em `d813954` |
| **Skills** | `sdd-brainstorm` 2.4.0, `sdd-handoff` 2.2.0, `sdd-governanca` 2.5.0, `sdd-release` 2.12.0, `sdd-ux-review` 2.6.0, `ux-review-builder` 1.5.0 (nova, 22ª), `sdd-new-session` 1.6.1, `sdd-seguranca` 1.0.2, `sdd-auditoria-harness` 1.2.2, `sdd-kb` 2.2.2; `check-versions.py --base v2.13.0` VERDE, 22 skills |

**Seleção de modo:** default (um autor; o gerador, os dados, as trocas e os testes são acoplados), com o pedido do Roberto de executar o pipeline inteiro.

**Revisão do DESIGN:** em contexto novo, 15 notas (4 HIGH), todas aplicadas (Advisor Ledger do DESIGN v1.1); 2 delas pediram decisão do Roberto: o `init` passa a copiar a `ux-review-builder` (nome mantido) e as geradas usam as pastas do Open, com os docs explicando.

**Passo 0:** curadoria dos 3 candidatos da F17 (LM-022 a LM-024, decisão do Roberto) e os 7 pendentes da revisão da F17 (todos, decisão do Roberto), cada um com teste vermelho em `v2.13.0` (7 de 8; o 8º é a guarda do nome mais longo).

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | gate de fiação | ✔ tratado: o gerador roda num repositório com tag sobre uma réplica; o teste do iniciante executa o comportamento; 6 sabotagens mortas |
| LM-002 | baseline vermelho | ✔ tratado: os testes do passo 0 vermelhos em `v2.13.0`; os dos consertos conferidos contra o commit anterior |
| LM-003 | commit antes de revisar | ✔ tratado: as 3 rodadas sobre árvore commitada, `diff_sha256` em cada pasta |
| LM-009 | sabotagem que desfaz conserto | ✔ tratado: mutantes em cópia de `git archive` |
| LM-010 | 2º revisor pago e diff grande | ✔ tratado: `--no-revisor2`; `--paths` sem as cópias byte a byte do starter (dispensa com prova, decisão do Roberto) |
| LM-011 | cenário nunca executado | ✔ tratado: o teste do iniciante rodou (12 execuções) e achou um defeito de texto ("rode `/sdd-define`") |
| LM-013 | edição por corte | ✔ tratado: edições de teste por troca exata |
| LM-017 | fallback silencioso | ✔ tratado: a skill de modo falha alto (65) em todo caso |
| LM-018 | `PIPESTATUS` no zsh | ✔ tratado: logs por script bash com `rc=$?` |
| LM-022 | tag no arquivo gerado | ✔ tratado: a tag fica só no `GERADO.txt` da raiz |
| LM-023 | aceite que cala a linha | ✔ tratado: 14 aceites novos, cada um com o trecho exato |
| LM-024 | comparação contra si mesma | ✔ tratado: a Vercel se decide pelo status do commit; o arquivo é só pista; a divergência tem resposta escrita |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `ls` `exit` `glob` `doctor` `-f`
regra: `ls a b` sai ≠ 0 quando um dos caminhos não existe, mesmo com o outro presente: na F17b, o aviso do `doctor` que juntou `sdd-*/agents/openai.yaml` e `ux-review-builder/agents/openai.yaml` num `ls` só deixou de disparar também para o caso antigo, e só o teste do caso antigo acusou. **Do instead:** para saber se algum de vários arquivos existe, percorra os caminhos com `[ -f ]` num laço; mantenha um teste de cada caso que a condição cobre.
evidencia: sdd/reports/evidence/F17B_STARTER_ETAPA2/RAIO-DE-IMPACTO.md
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `regex` `comando` `prosa` `obrigação` `teste de texto`
regra: Um teste que procura comando por expressão regular ("bloco de shell", "rode `…`") deixa passar a mesma obrigação escrita em prosa ("aplicados viram AT + script em …"): na F17b, o checklist da governança exigia script sem a condição do Verify Gate, e só o avaliador de contexto novo achou. **Do instead:** quando o contrato é "não exigir X", confira também as linhas que dizem que X é obrigatório (checklist, molde, brief) e teste a frase condicionada, não só a ausência do comando.
evidencia: sdd/reviews/AVALIACAO_F17B_STARTER_ETAPA2_20261113-1549.md
ficha: —
mordeu_antes: —
>>>

---

## Files Created

| Arquivo | Para quê |
|---|---|
| `.agents/skills/ux-review-builder/**` | a 22ª skill do Open (Decision 6) |
| `.agents/skills/sdd-release/references/MODO_INICIANTE.md` | a release curta, GitHub + Vercel (Decision 3) |
| `scripts/starter/modos.tsv` | a regra "skill de modo" (Decision 2) |
| `scripts/starter/raiz/{docs,exemplos,tests}/**` | o que o starter tinha fora das skills, agora do gerador (Decision 7) |
| `scripts/starter/trocas/{sdd-brainstorm,sdd-handoff,sdd-governanca}.md`, `trocas/_moldes/{HANDOFF_TEMPLATE,BRAINSTORM_TEMPLATE}.md` | o que só existe no Open sai da cópia (Decisions 4, 5) |
| `tests/test_f17b_passo0.py`, `tests/test_f17b_textos.py` | passo 0; AT-004 a AT-007 |

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh --strict sdd/features/DEFINE_F17B_STARTER_ETAPA2.md`) | exit 0 em `e583889`: 2.123 testes, 1 pulado; publish-gate GREEN na cópia de `git archive` (`VERIFY-GATE-e583889.log`); a 1ª execução, em `99283ae`, caiu só na contagem de perguntas de decisão (31 em 26, com a builder), consertada em `c8826b7` |
| `check-versions.py --base v2.13.0` | VERDE, 22 skills |
| `skill-lint.py --conversa` nas 22 skills | ok |
| ATs | 10 logs, um por AT, todos `rc=0` em `e583889` (`AT-001.log` … `AT-010.log`) |
| Sabotagens (`SABOTAGEM-1d8fc65.log`) | 6 de 6 mortas: modo sem `compatibility`; `tests/` fora de `DONO_INTEIRO` no gerador e na trava; release copiada inteira; `init` sem a builder; lint sem a pasta sem barra |
| Geração de ensaio (clone do starter `v1.5.17`, tag local) | `ENSAIO-v1.5.17.log`: geração verde e as 9 checagens do CI do starter verdes (trava, publish-check, check-versions `--base v1.5.17`, py_compile, `bash -n`, testes das skills, testes da raiz, gate.sh da kb, package com 18 zips) |
| Raio de impacto (`RAIO-DE-IMPACTO.md`) | 7 superfícies; 1 quebra em código não modificado (o aviso do `doctor` sobre skills do starter), consertada com teste |

### Simplicidade do iniciante (critério de aceite do Roberto, fora do gate)

| Critério | Resultado | Evidência |
|---|---|---|
| Tabela de paradas, 0 parada nova sem OK | 3 paradas novas (perfil de risco no brainstorm; oferta de limpeza no handoff; pedir ao aluno que abra o endereço do deploy), as 3 com OK do Roberto em 2026-11-13; governança sem parada nova (o `PROCEDIMENTO.md` era igual ao da `v1.5.17`); 2 exigências a menos na release | `evidence/F17B_STARTER_ETAPA2/PARADAS.md` |
| Teste do iniciante, 3 de 3 por skill (`claude -p --tools ""`, pasta vazia, sem MCP, várias voltas, roteiro e critério escritos antes em `INICIANTE-roteiro.json`) | handoff 3 de 3 (`INICIANTE-sdd-handoff-{1,2,3}.log`); governança 3 de 3 e, depois do conserto do avaliador, 3 de 3 de novo (`INICIANTE-sdd-governanca-{1,2,3}.log`, `-s2-{1,2,3}.log`); brainstorm **2 de 3** na 1ª série (a execução 2 mandou "rode `/sdd-define …`", contado como comando pelo critério escrito antes), **o texto mudou** em `1a71e1a` (o próximo passo da brainstorm e da governança e o molde do BRAINSTORM pedem a skill, sem comando com barra) e a 2ª série deu 3 de 3 (`INICIANTE-sdd-brainstorm-s2-{1,2,3}.log`) | os logs citados |
| Release iniciante: 1 OK, sem token, só git e `gh` | `test_um_ponto_de_aprovacao`, `test_nenhum_token` | `AT-004.log` |

---

## Segurança

Itens recusados ou adiados no passo de segurança do Define: nenhum (N.A.: sem login, rota pública, dado de terceiros, upload, banco nem chamada paga; a release iniciante usa só o login que o `gh` e o git já têm).

---

## Issues Encountered

- O `init` e o `sync` do Open copiavam só pastas `sdd-*`: a `ux-review-builder` entraria no Open sem chegar a nenhum projeto (revisão do DESIGN, nota 1).
- A troca no molde `RESUMO_ETAPA` (o kanban do starter sem a etapa "review adversarial") mudou a cópia gerada de 2 skills da F17: o gerador pediu versão nova (a trava da F17 funcionando) e elas subiram patch.
- `ls a b` com um dos caminhos ausente sai ≠ 0: a 1ª versão do conserto do `doctor` calou o aviso antigo (candidato ao playbook).

---

## Deviations from Design

| Item | Desvio | Motivo |
|---|---|---|
| Decision 7 | só os 2 quickstarts mudaram em `docs/` (pastas e 18 skills); `exemplos/baixar-nfse` ficou como na `v1.5.17` | o kit é do build congelado, que grava em `sdd/` |
| Decision 3 | "Só o arquivo ⇒ não confirmei" e "sem consultar o GitHub, nunca 'Nenhum'" | revisão, rodada 1, R2 |
| Manifest | troca do molde `BRAINSTORM_TEMPLATE` a mais | teste do iniciante (o próximo passo sem comando com barra) |
| Revisão | as 3 rodadas com `--paths`, sem as cópias byte a byte do starter | dispensa do restante decidida pelo Roberto, com o `diff -rq` contra a `v1.5.17` (`REVISAO-COPIAS-v1.5.17.log`) |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · achados: 3 no ciclo 1 (NEEDS_WORK: 1 médio — o checklist da governança exigia script sem a condição; 2 baixos, catálogo e brief do revisor; consertados em `1d8fc65`), 2 baixos e 1 informativo no ciclo 2 (consertados em `f9a0af1`; o informativo é o recibo do teste do iniciante acima) · avaliações: `sdd/reviews/AVALIACAO_F17B_STARTER_ETAPA2_20261113-1549.md`, `sdd/reviews/AVALIACAO_F17B_STARTER_ETAPA2_20261113-1636.md`

O recibo pendente é o que o DEFINE põe fora do gate: a 2ª geração no clone real, PR, CI e Release do starter, CI do PR do Open nas 3 plataformas e a Release do Open. A tabela de paradas e o teste do iniciante já têm recibo (acima).

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F17B_STARTER_ETAPA2.md` (13 linhas, `ledger-revisao-lint.sh` VERDE).

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (`v2.13.0..c8826b7`, `--paths`) | `EXTERNAL_REVIEW_20261113-143814` | claude + `openrouter` (qwen) | 1 grave, 2 médios, 3 leves | 3 aplicados (1 com dano: a release dizia que o push não publica quando a Vercel publica), 3 rebatidos com evidência ou escopo |
| 2 (`v2.13.0..f9a0af1`, diff inteiro com `--paths`) | `EXTERNAL_REVIEW_20261113-160601` | claude + qwen | 2 médios, 1 leve | 1 aplicado, 2 rebatidos |
| 3, a última (`v2.13.0..e583889`) | `EXTERNAL_REVIEW_20261113-161527` | claude + qwen | 2 médios, 1 leve (repetidos da rodada 1) + 1 médio do auditor | 4 rebatidos com evidência ou escopo |

2º revisor dispensado nas 3 rodadas (`--no-revisor2`: codex sem cota; LM-010) e desempate dispensado (`--no-desempate`). O `--conferir` recusa a rodada 3 por ter usado `--paths`: o restante do diff (46 arquivos iguais byte a byte aos da `v1.5.17` publicada do starter, 2 JSON que só mudam a versão, a lista do `MANIFEST.txt`) tem dispensa do Roberto em 2026-11-13, com a prova `evidence/F17B_STARTER_ETAPA2/REVISAO-COPIAS-v1.5.17.log`.

**Medidor dos revisores (`bash sdd/bin/eval-revisores.sh`, `evidence/F17B_STARTER_ETAPA2/EVAL-REVISORES.log`):**

| Papel | Engine (modelo) | Cobrança | Rodadas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | AGREE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 3 | 0.0000 | 4.9179 | 12 | 4 de 12 | 1 de 12 | 5 de 12 | — |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 3 | 0.1344 | 0.1344 | 1 | 0 de 1 | 0 de 1 | 1 de 1 | 83.3% (10 de 12) |

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`; o `default_prompt` do `openai.yaml` é texto de botão).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.1) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | 15 geradas, `docs/`/`exemplos/`/`tests/` do gerador; congeladas e o resto byte a byte iguais; README 15 + 3 nos 2 idiomas | true | `evidence/F17B_STARTER_ETAPA2/AT-001.log` |
| AT-002 | a release sai só do modo: frontmatter, GENERATED, corpo do modo, "Quando migrar", só os arquivos citados | true | `evidence/F17B_STARTER_ETAPA2/AT-002.log` |
| AT-003 | modo quebrado ⇒ 65 sem gravar; a release crua reprova no lint | true | `evidence/F17B_STARTER_ETAPA2/AT-003.log` |
| AT-004 | release iniciante: 1 OK, sem token, Vercel pelo status e a URL, workflow mantido, falha sem redeploy, ponteiro no Open | true | `evidence/F17B_STARTER_ETAPA2/AT-004.log` |
| AT-005 | brainstorm, handoff e governança com o caminho sem terminal | true | `evidence/F17B_STARTER_ETAPA2/AT-005.log` |
| AT-006 | brainstorm e handoff geradas sem comando nem Verify Gate exigido; governança só no trecho condicionado | true | `evidence/F17B_STARTER_ETAPA2/AT-006.log` |
| AT-007 | `ux-review-builder` 1.5.0 no Open, 22 skills, `sdd-ux-review` lê o padrão | true | `evidence/F17B_STARTER_ETAPA2/AT-007.log` |
| AT-008 | as checagens do starter sobre a saída gerada; 1 byte em `docs/`/`exemplos/`/`tests/` ⇒ trava 1 | true | `evidence/F17B_STARTER_ETAPA2/AT-008.log` |
| AT-009 | versão que não sobe nas 5 novas ⇒ 65 antes de gravar | true | `evidence/F17B_STARTER_ETAPA2/AT-009.log` |
| AT-010 | 22 skills no lint, agnóstico e check-versions; release ≤ 500; o `init` não copia `scripts/starter/` | true | `evidence/F17B_STARTER_ETAPA2/AT-010.log` |

**Verify Gate:** exit 0 em `e583889`: 2.123 testes em 36 min, 1 pulado (`evidence/F17B_STARTER_ETAPA2/VERIFY-GATE-e583889.log`), com a máquina livre.

---

## Final Status

### Overall: ✅ COMPLETE

Recibo pendente (fora do gate, pela release): 2ª geração do starter pela tag publicada num clone limpo, PR com as 10 checagens, Release do starter; CI do PR do Open e Release do Open.

---

## Next Step

**Ready for:** `/sdd-release` da F17b (o Verify Gate roda de novo antes de publicar).
