# BUILD REPORT: F17c — starter gerado, etapa 3

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F17C_STARTER_ETAPA3 |
| **Date** | 2026-11-14 |
| **Author** | build-agent (worktree `sdd-open-f17c-starter-etapa3`, branch `feat/f17c-starter-etapa3`, de `e583889` = `v2.14.0`) |
| **DEFINE** | [DEFINE_F17C_STARTER_ETAPA3.md](../features/DEFINE_F17C_STARTER_ETAPA3.md) v1.3 |
| **DESIGN** | [DESIGN_F17C_STARTER_ETAPA3.md](../features/DESIGN_F17C_STARTER_ETAPA3.md) v1.1 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 15/15 linhas do manifest do DESIGN v1.1 |
| **Files Created** | 30 no pacote: `.agents/skills/sdd-{define,design,build}/web/**` (25: o texto da `v1.5.18` com a Decision 3), `.agents/skills/sdd-handoff/assets/HANDOFF_EXAMPLE.md`, `tests/test_f17c_passo0.py`, `tests/test_f17c_gerador.py`, `tests/test_f17c_textos.py` |
| **Commits** | passo 0: `53bba4a` · build: `1a40424`, `fc76456`, `01f8faf` · revisão, rodada 1: `e3b1244` · avaliador, ciclo 1: `72667a3` · ciclo 2: `81a4577`, `de6a423` · ciclo 3: `767a212` · ciclo 4: `e1f1b42` · revisão, rodada 2: `97503a7` |
| **Tests Passing** | exit 0 em `97503a7`: 2.151 testes em 40 min, 1 pulado (`evidence/F17C_STARTER_ETAPA3/VERIFY-GATE-97503a7.log`); partida: 2.123 em `e583889` |
| **Skills** | `sdd-define` 2.7.0, `sdd-design` 2.7.0, `sdd-build` 2.10.0, `ux-review-builder` 1.6.0, `sdd-engenharia-reversa-saas` 1.2.0, `sdd-handoff` 2.2.1; `check-versions.py --base v2.14.0` VERDE, 22 skills |

**Seleção de modo:** default (um autor; o gerador, os textos do modo e os testes são acoplados), com o pedido do Roberto de executar o pipeline inteiro.

**Revisão do DESIGN:** em contexto novo, 15 notas (4 HIGH), todas aplicadas (a 7 em parte); a nota 4 virou decisão do Roberto (as duas skills de pasta plana entram: Decision 9).

**Passo 0:** curadoria da F17b (LM-025, LM-026, 13 contagens; 2 sugestões recusadas) e o exemplo preenchido da ficha (`sdd-handoff` 2.2.1); o version gate contra a versão real do starter e o `--conferir` com `--paths` ficam pendentes (decisão do Roberto).

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 15 linhas de manifest, acopladas (gerador, `modos.tsv`, texto do modo, testes); nada paralelizável fora de texto |
| Recomendação | default — um autor mantém os nomes e as trocas coerentes |
| Decisão do usuário | default, 2026-11-13 (pedido do Roberto: pipeline inteiro, só as decisões dele) |

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | gate de fiação | ✔ tratado: o gerador roda numa réplica com tag; o teste do iniciante executa o comportamento; 6 sabotagens mortas |
| LM-002 | baseline vermelho | ✔ tratado: os testes novos vermelhos em `53bba4a` (`BASELINE-53bba4a.log`, 65 falhas); os juízes do iniciante com 13 casos (`INICIANTE-AUTOTESTE.log`) |
| LM-003 | commit antes de revisar | ✔ tratado: rodadas sobre árvore commitada |
| LM-009 | sabotagem que desfaz conserto | ✔ tratado: mutantes em cópia de `git archive` |
| LM-010 | 2º revisor pago | ✔ tratado: `--no-revisor2` |
| LM-011 | cenário nunca executado | ✔ tratado: teste do iniciante em 3 séries; o avaliador achou o juiz frouxo |
| LM-012 | CPF/CNPJ e 11 dígitos no pacote | ✔ tratado: valores de exemplo em prosa; o commit da cópia verbatim, que os tinha, foi desfeito antes de qualquer push |
| LM-013 | edição por corte | ✔ tratado: edições por troca exata com contagem |
| LM-022 | tag no arquivo gerado | ✔ tratado: o modo não leva tag |
| LM-023 | aceite que cala a linha | ✔ tratado: nenhum aceite novo |
| LM-026 | regex deixa passar a obrigação em prosa | ✔ tratado: o AT-005 confere também "quando executável" e o nome dos validadores; o AT-007 confere a frase inteira (avaliador, ciclo 1, achado 2) |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `claude -p` `--tools ""` `teste do iniciante` `pasta de trabalho` `web`
regra: `claude -p --tools ""` não simula a web: o Claude Code anuncia ao modelo o diretório de trabalho e uma pasta temporária gravável da sessão (medido mesmo com `/` como diretório), e o modelo passa a dizer "posso gravar aqui" sem ter ferramenta; na F17c, 3 das 6 execuções do build gerado reprovaram ou passaram por engano por isso. **Do instead:** para o comportamento "sem pasta" (web), chame o modelo pela API de chat (sem Claude Code), com o mesmo roteiro; use o `claude -p` só para o que não depende do ambiente.
evidencia: sdd/reports/evidence/F17C_STARTER_ETAPA3/INICIANTE-sdd-build-s2-g-1.log
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `juiz` `regex` `entrega` `alargar` `critério escrito antes`
regra: Um juiz por expressão regular de comportamento de LLM erra nos dois sentidos e cada ajuste depois de ver o resultado abre o caso vizinho: na F17c, o juiz do build foi ajustado 4 vezes; alargado para reconhecer uma resposta certa, passou a aprovar uma instrução ao aluno ("1. Abra a pasta …"); a negação por frase calou "não tenho pasta, mas implementei"; e o avaliador de contexto novo achou 9 furos lendo as conversas. **Do instead:** o juiz por regex é triagem, não veredito: um leitor em contexto novo julga as conversas pelo critério em prosa; todo ajuste do juiz entra com um caso que passa e um parecido que reprova no autoteste, e a negação vale por oração (vírgula, "mas"), não por frase.
evidencia: sdd/reviews/AVALIACAO_F17C_STARTER_ETAPA3_20261114-0140.md
ficha: —
mordeu_antes: —
>>>

---

## Files Created

| Arquivo | Para quê |
|---|---|
| `.agents/skills/sdd-{define,design,build}/web/**` | o modo web (Decisions 1, 3) |
| `.agents/skills/sdd-handoff/assets/HANDOFF_EXAMPLE.md` | o exemplo preenchido da ficha (passo 0) |
| `tests/test_f17c_passo0.py`, `tests/test_f17c_gerador.py`, `tests/test_f17c_textos.py` | passo 0; AT-002, AT-003, AT-008, AT-009; AT-004 a AT-007 e AT-010 |

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh --strict sdd/features/DEFINE_F17C_STARTER_ETAPA3.md`) | exit 0 em `97503a7`: 2.151 testes, 1 pulado; publish-gate GREEN na cópia de `git archive` (`VERIFY-GATE-97503a7.log`) |
| `check-versions.py --base v2.14.0` | VERDE, 22 skills |
| ATs | 10 logs, um por AT, `rc=0` em `97503a7` (`AT-001.log` … `AT-010.log`) |
| Baseline vermelho (`BASELINE-53bba4a.log`) | os testes novos e mudados contra `53bba4a`: 54 testes, 56 falhas e 9 erros |
| Sabotagens (`SABOTAGEM-*.log`) | 6 de 6 mortas: pasta-base ignorada; sem a guarda de `..` no citado (o 1º caso sobrevivia pelo lint; o teste mudou); build web de volta a `sdd/` plano; validador de volta no checklist do design; molde sem "Drift detectado"; validador da builder aceitando subpasta errada |
| Geração de ensaio (clone do starter `v1.5.18`, tag local) | geração verde e as 9 checagens do CI do starter verdes (`scripts/ensaio.sh`, `scripts/checagens-starter.sh`) |
| Raio de impacto (`RAIO-DE-IMPACTO.md`) | 12 superfícies; 0 quebra em código não modificado; 1 mudança esperada (pacote da builder 1.5.0 reprova no validador novo até ser regerado) |

### Simplicidade do iniciante (critério de aceite do Roberto, fora do gate)

| Critério | Resultado | Evidência |
|---|---|---|
| Tabela de paradas, 0 parada nova sem OK | **0 paradas novas**; 3 exigências a menos (validador do define, do design e do relatório; `- banco:` em `sdd/ambiente.md`); a pergunta da pasta ativa da engenharia reversa fica mais rara | `PARADAS.md`, `PARADAS-diff-v1.5.18.log` |
| Teste do iniciante, define e design (`claude -p --tools ""`, roteiro e critério escritos antes) | define **3 de 3** (controle com a congelada: 2 de 3, a falha é limite do juiz de aviso, "Salve como"); design **3 de 3** (controle: 0 de 3, um deles citou o `validate_design.py` que a geração tirou); mediana de voltas gerada × congelada: define 2 × 2, design 3 × 7 | `INICIANTE-sdd-{define,design}-{g,c}-{1,2,3}.log` |
| Teste do iniciante, build | **não fechou 3 de 3 (CONCERNS, decisão do Roberto)**. Séries 1 e 2 (`claude -p`): o Claude Code anuncia uma pasta gravável e o modelo passa a dizer que pode gravar; série 3 (OpenRouter, sem pasta): honestas, mas as 3 recomendavam construir pelo chat (avaliador, ciclo 2); o texto mudou (`81a4577`: recomendar um agente que grave); série 4: na volta 1 recomendam o agente, depois de "só tenho este chat" passam ao chat — eu as dei por 3 de 3 com o juiz ajustado depois de ler só a volta 1, **errado**: o avaliador (ciclo 3) leu as conversas inteiras e deu 0 de 3; **decisão do Roberto:** "só tenho o chat" abre o caminho do chat com regras (`767a212`); **série 5**, julgada por um leitor novo pelo critério em prosa (o regex só faz triagem): **2 de 3** — a g-1 tomou "Ok" como autorização para começar e mostrou "Tarefas 1/2" antes do relato; o texto foi consertado (`e1f1b42`: o contador só sobe quando a tarefa termina; "ok" vago não autoriza; "você só tem o chat") e **não foi medido de novo** (decisão do Roberto: consertar e fechar CONCERNS). Nenhuma das 15 execuções afirmou ter gravado ou testado o que não fez. Custo pago: séries 3, 4 e 5, US$ 3,17 | `INICIANTE-sdd-build-*.log`, `INICIANTE-AUTOTESTE.log`, `INICIANTE-REJULGAMENTO-build.log`, `INICIANTE-roteiro.json`, `AVAL4-leitura.log` |

---

## Segurança

Itens recusados ou adiados no passo de segurança do Define: nenhum (N.A.: sem login, rota pública, dado de terceiros, upload, banco nem chamada paga na feature; o build gerado mantém a confirmação do projeto e a prova por leitura da migration da `v1.5.18`).

---

## Issues Encountered

- O texto congelado tinha CPF e CNPJ por extenso (um CNPJ de empresa real): o `publish-gate` do Open barra; o commit da cópia verbatim foi desfeito antes do push e os valores viraram prosa.
- O `xargs -I` não montou a linha de comando do rodador do iniciante (lotes com `wait` no lugar); a rede caiu numa rodada (`ENOTFOUND`) e as execuções foram refeitas.
- O `claude -p` anuncia ao modelo uma pasta gravável: o teste "sem pasta" do build precisou da API de chat (candidato ao playbook).
- O juiz do build foi alargado depois de ver a série 1 e passou a aprovar o caso errado (candidato ao playbook).

---

## Deviations from Design

| Item | Desvio | Motivo |
|---|---|---|
| Decision 7 | o teste do build roda pela OpenRouter na série 3 | o `claude -p` anuncia uma pasta gravável (decisão do Roberto) |
| Manifest | os testes do gerador em `tests/test_f17c_gerador.py`, separados dos de texto | tamanho; já registrado no DESIGN v1.1 |
| Decision 4 | a frase "não finja" passou a ser a mesma nas 3 e mais longa | avaliador, ciclo 1, achado 2 |
| Decision 3 | o build web ganhou o caminho sem o projeto: recomendar um agente que grave; "só tenho o chat" abre o caminho do chat com regras | avaliador, ciclos 2 a 4; decisões do Roberto |
| DEFINE | v1.2 (AT-007 isenta a UX pura) e v1.3 (critério do build web; veredito do teste do iniciante por leitor novo) | decisões do Roberto |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** NEEDS_WORK no último ciclo, fechado como CONCERNS por decisão do Roberto · ciclos: 4 (2 acima do teto, com o OK dele) · ciclo 1 (`AVALIACAO_F17C_STARTER_ETAPA3_20261114-0140.md`): NEEDS_WORK, 6 achados (AT-007 parcial, juiz do build frouxo, caminhos ambíguos, "validado", fragmento, evidência defasada), consertados em `72667a3` · ciclo 2 (`…-0300.md`): NEEDS_WORK, o build web recomendava o chat e o juiz tinha 9 furos; UX pura; decisões do Roberto em `81a4577` · ciclo 3 (`…-0430.md`): NEEDS_WORK, a série 4 dá 0 de 3 lida inteira; 14 furos novos no juiz; decisões do Roberto em `767a212` · ciclo 4 (`…-0530.md`, leitor da série 5): NEEDS_WORK, 2 de 3; consertado em `e1f1b42` sem nova medição (decisão do Roberto). Os ATs AT-001 a AT-010 passaram em todos os ciclos.

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F17C_STARTER_ETAPA3.md`.

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (`v2.14.0..fc76456`, diff inteiro) | `EXTERNAL_REVIEW_20261114-005631` | claude + `openrouter` (qwen) | 2 leves | 2 aplicados (`e3b1244`) |
| 2 (`v2.14.0..e1f1b42`, diff inteiro) | `EXTERNAL_REVIEW_20261114-082513` | claude + qwen | 1 médio, 1 leve | 2 aplicados (`97503a7`) |
| 3, a última (`v2.14.0..97503a7`, diff inteiro) | `EXTERNAL_REVIEW_20261114-083418` | claude + qwen | 0 do revisor; 1 novo do auditor (HIGH) | rebatido com evidência (o bloco `bash` está no `SKILL.md` do Open, que não vai ao starter) |

Sem `--paths` em nenhuma rodada: o `--conferir` CONFERE a rodada 3 (`evidence/F17C_STARTER_ETAPA3/REVISAO-CONFERIR.log`), com o 2º
revisor dispensado (`--no-revisor2`: codex sem cota; LM-010) e o motivo registrado (`--aceitar-sem-revisor2`). Desempate dispensado.

**Medidor dos revisores (`bash sdd/bin/eval-revisores.sh`, `evidence/F17C_STARTER_ETAPA3/EVAL-REVISORES.log`):**

| Papel | Engine (modelo) | Cobrança | Rodadas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | AGREE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 3 | 0.0000 | 5.6579 | 4 | 4 de 4 | 0 de 4 | 0 de 4 | — |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 3 | 0.1574 | 0.1574 | 1 | 0 de 1 | 0 de 1 | 1 de 1 | 100.0% (4 de 4) |

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`; o `default_prompt` do `openai.yaml` é texto de botão).

---

**Verify Gate:** exit 0 em `97503a7` (`evidence/F17C_STARTER_ETAPA3/VERIFY-GATE-97503a7.log`).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.1) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | 18 geradas, nenhuma congelada; README e quickstart nos 2 idiomas sem validador; exemplo com as pastas novas | true | `evidence/F17C_STARTER_ETAPA3/AT-001.log` |
| AT-002 | define, design e build saem só do modo web, com os arquivos de `web/` e nada do caminho do Open | true | `evidence/F17C_STARTER_ETAPA3/AT-002.log` |
| AT-003 | modo quebrado ⇒ 65 sem gravar; a cópia crua reprova no lint | true | `evidence/F17C_STARTER_ETAPA3/AT-003.log` |
| AT-004 | pastas do Open, entrega no chat, handoffs coerentes, sem `sdd.config.yaml` e `- banco:` | true | `evidence/F17C_STARTER_ETAPA3/AT-004.log` |
| AT-005 | define e design sem comando ao aluno; nenhum validador; build lê a saída do comando | true | `evidence/F17C_STARTER_ETAPA3/AT-005.log` |
| AT-006 | molde do relatório com Seleção de modo e Drift; moldes sem sobras | true | `evidence/F17C_STARTER_ETAPA3/AT-006.log` |
| AT-007 | "não finja" nas 3; a pergunta da 1ª vez do Verify Gate no define | true | `evidence/F17C_STARTER_ETAPA3/AT-007.log` |
| AT-008 | as checagens do starter sobre a saída; 1 byte no build gerado ⇒ trava 1 | true | `evidence/F17C_STARTER_ETAPA3/AT-008.log` |
| AT-009 | versão que não sobe nas 3 ⇒ 65 antes de gravar | true | `evidence/F17C_STARTER_ETAPA3/AT-009.log` |
| AT-010 | 22 skills nos lints; linha do modo condicionada; as 15 da F17b iguais salvo as decididas; o `init` não copia `scripts/starter/` | true | `evidence/F17C_STARTER_ETAPA3/AT-010.log` |

---

## Final Status

### Overall: ✅ COMPLETE — veredito CONCERNS (o teste do iniciante do build fechou 2 de 3 na série 5, com o texto consertado depois e sem nova medição; o avaliador acabou em NEEDS_WORK no 4º ciclo, 2 acima do teto; decisões do Roberto)

Recibo (fora do gate, pela release), cumprido em 2026-11-14: CI do PR #29 do Open verde (Ubuntu 31m56s, macOS 50m52s, Windows 4m56s); `git push --atomic` de `e583889..97503a7` na `main` + tag `v2.15.0`; Release `v2.15.0` em 14:03:38Z, SHA-256 do tar.gz `a0ad37b9759e…` conferido (`RELEASE-sha256.log`); 3ª geração pela tag num clone limpo do starter (`7c7a207`, 48 arquivos; as 9 checagens verdes, `STARTER-GERACAO-v2.15.0.log`, `STARTER-CHECAGENS-v2.15.0.log`); PR #12 do starter com CI verde e fast-forward na `main` (push, PR e integração rodados pelo Roberto); Release `v1.5.19` do starter em 14:14:46Z, 18 zips `OK` no `SHA256SUMS.txt` (`STARTER-RELEASE-v1.5.19-sha256.log`).

---

## Next Step

**Ready for:** `/sdd-release` da F17c (o Verify Gate roda de novo antes de publicar).
