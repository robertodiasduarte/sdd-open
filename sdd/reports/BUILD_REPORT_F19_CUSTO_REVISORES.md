# BUILD REPORT: F19 — Custo e benefício dos modelos de revisão

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F19_CUSTO_REVISORES |
| **Date** | 2026-11-10 |
| **Author** | build-agent (worktree `sdd-open-f21-f19`, branch `feat/f19-custo-revisores`, de `9581740` = `v2.9.0`) |
| **DEFINE** | [DEFINE_F19_CUSTO_REVISORES.md](../features/DEFINE_F19_CUSTO_REVISORES.md) v1.4 |
| **DESIGN** | [DESIGN_F19_CUSTO_REVISORES.md](../features/DESIGN_F19_CUSTO_REVISORES.md) v1.3 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 20/20 linhas do manifest |
| **Files Created** | 41 (2 scripts, critério, molde, 31 arquivos de fixtures, 3 testes, 1 fixture do loop e mais 2 fixtures do lint) ; 14 alterados |
| **Commits** | `52b6dab` (F19) · `b7c967e` (revisão, rodada 1) · `e2e79a2` (rodada 2) · `661ef65` (avaliador, ciclo 1) · `0d4a730` (rodada 3 e avaliador, ciclo 2) · `dcf95ac` (rodada 4 e avaliador, ciclo 3) |
| **Tests Passing** | 1.864 testes verdes em `dcf95ac` (`evidence/F19_CUSTO_REVISORES/VERIFY-GATE.log`) |
| **Skills** | `sdd-build` 2.8.0, `sdd-release` 2.10.0 (`check-versions.py --base v2.8.0` PASS) |

**Seleção de modo:** direto, por esta sessão ([auto · de rotina]): os dois scripts foram prototipados fora do repositório sobre as 25 rodadas reais antes da branch existir, e o conjunto foi ensaiado numa cópia de `git archive`. Revisão do DESIGN em contexto novo antes do código: veredito NÃO PRONTO, 17 notas aplicadas.

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|---|---|---|---|
| testes dos 2 scripts | LM-001 | ✔ tratado | cada célula da tabela afirmada sobre fixtures dos dois lados; 6 mutantes mortos (`SABOTAGEM.log`) |
| testes novos | LM-002 | ✔ tratado | `BASELINE-vermelho.log`: os 4 arquivos de teste falham na árvore de antes da frente |
| revisão | LM-003 | ✔ tratado | commit antes de cada rodada; `git add` por caminho, conferido por `git diff --cached --name-only` |
| regra "qual tabela é o ledger" | LM-005 | ✔ tratado, **mordeu** | a heurística regrediu 2 vezes (rodada 1 da revisão; ciclo 1 do avaliador); na 2ª saiu, trocada pela regra "o arquivo é só do ledger" |
| gate sem `.git` | LM-006 | ✔ tratado | Verify Gate em cópia de `git archive`; os scripts aceitam caminho por argumento |
| sabotagem | LM-009 | ✔ tratado | mutantes só em cópia de `git archive HEAD` |
| engine paga | LM-010 | ✔ tratado | saldo lido antes da rodada 1 (US$ 0,1084); na rodada 2 o auditor pago falhou em 2 s por saldo; rodadas 3, 4 e 5 com uma engine só, decisão do Roberto |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `ledger` `lint` `tabela` `markdown` `heurística`
regra: Um lint que decide por conta própria qual parte de um arquivo Markdown é "a tabela que interessa" deixa linha sem conferir: na F19 a regra de escolher a tabela do ledger regrediu 2 vezes (linha depois de linha em branco; id entre crases), e depois dela uma linha sem a barra inicial ainda passava. **Do instead:** o arquivo conferido guarda uma coisa só e toda linha com forma de dado é conferida ou acusada, inclusive fora da tabela; dois scripts que leem o mesmo arquivo usam a mesma função, com teste que compara o texto das duas cópias.
evidencia: sdd/reviews/AVALIACAO_F19_CUSTO_REVISORES_20261110-ciclo2.md
ficha: —
mordeu_antes: LM-005
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `edição por script` `testes removidos` `corte por âncora`
regra: Editar um arquivo de teste cortando "do teste A até o teste B" por âncora apaga os testes que estavam no meio sem nenhum erro: na F19 três testes sumiram assim, a suíte continuou verde, e o ledger da revisão seguiu citando dois deles como prova. **Do instead:** depois de uma edição por corte, compare a lista de testes de antes e de depois (`grep -c "def test_"`), e trate teste citado em ledger ou relatório como contrato: se o nome some, o registro mente.
evidencia: sdd/reports/evidence/F19_CUSTO_REVISORES/AVAL-c2-61-testes-citados-no-ledger-da-F19.log
ficha: —
mordeu_antes: —
>>>
```

---

## Files Created

| # | File | Ação | Verificado |
|---|---|---|---|
| 1 | `sdd/bin/eval-revisores.sh` | criado | `tests/test_eval_revisores.py` |
| 2 | `sdd/bin/ledger-revisao-lint.sh` | criado | `tests/test_ledger_revisao_lint.py` |
| 3–4 | `sdd/review/CRITERIO_DANO.md`, `sdd/templates/LEDGER_REVISAO_TEMPLATE.md` | criados | `tests/test_f19_textos.py` |
| 5–7 | `sdd/fixtures/revisao/custo/` (7 pastas, ledger de exemplo, registry), `sdd/fixtures/revisao/ledger/` (11 arquivos), `sdd/fixtures/fluxo/ledger-7-colunas.md` | criados | os 3 testes novos e `tests/test_fluxo.py` |
| 8–11 | `tests/test_eval_revisores.py`, `tests/test_ledger_revisao_lint.py`, `tests/test_f19_textos.py`; `tests/test_fluxo.py` (2 casos novos) | criados / alterado | Verify Gate |
| 12–14 | `.agents/skills/sdd-build/SKILL.md` (5c, 2.8.0), `.agents/skills/sdd-release/SKILL.md` (0a item 8, 2.10.0), `sdd/templates/BUILD_REPORT_TEMPLATE.md` | alterados | `tests/test_f19_textos.py`, `skill-lint.py --conversa` |
| 15–18 | `docs/adversarial-review.md`, `docs/pt-BR/adversarial-review.md`, `docs/cli-conventions.md`, `sdd/WORKFLOW_CONTRACTS.yaml` | alterados | `tests/test_f19_textos.py`, `tests/test_docs.py` |
| 19 | 5 testes que fixam as versões das 2 skills | alterados | Verify Gate |
| 20 | `MANIFEST.txt` | +41 linhas | `publish-gate.sh` no Verify Gate |

---

## Verification Results

| Verificação | Resultado | Evidência |
|---|---|---|
| Verify Gate (`publish-gate` + suíte inteira em cópia de `git archive`, Python 3.9.6, bash 3.2) | exit 0, 1.864 testes, em `dcf95ac` | `evidence/F19_CUSTO_REVISORES/VERIFY-GATE.log` |
| Linha de base vermelha | os 4 arquivos de teste falham antes da frente | `evidence/F19_CUSTO_REVISORES/BASELINE-vermelho.log` |
| 6 sabotagens em cópia de `git archive` | 6 de 6 mortas por teste nomeado (a 1ª versão de uma era equivalente e foi trocada) | `evidence/F19_CUSTO_REVISORES/SABOTAGEM.log` |
| Medidor sobre dados reais | 25 pastas, 6 ledgers; somas e contagens refeitas à parte pelo avaliador, com `Decimal`, e iguais | `sdd/reports/RETROATIVO_REVISORES_2026-11-10.md`; `AVAL-c1-02`, `AVAL-c2-03` |
| Checks do projeto (`test_cmd`, `lint_cmd`) | pulados: o repositório do pacote não tem `sdd/config.yaml`; a suíte é o gate | — |

---

## Issues Encountered

| # | Problema | Resolução |
|---|---|---|
| 1 | **fato errado no brainstorm:** eu disse ao Roberto que a decisão por achado nunca tinha sido gravada de forma estruturada; os ledgers de 5 colunas de F10 a F14 existem em `sdd/reports/evidence/{F}/ledger-review.md` | corrigido no BRAINSTORM, no DEFINE e no DESIGN no mesmo dia; as decisões continuaram valendo e o retroativo passou a converter esses ledgers |
| 2 | o DESIGN v1.0 exigia `@engine` no id e não previa rodada sem achados: nenhum arquivo passaria no lint e no loop ao mesmo tempo | revisão do DESIGN (2 HIGH); ids copiados do arquivo de vereditos, linha `sem achados:` |
| 3 | a regra de escolher "a tabela do ledger" regrediu 2 vezes | regra estrutural (DEFINE v1.2) e, no ciclo 2, linha com forma de ledger fora da tabela também é acusada (v1.3) |
| 4 | **erro do build:** uma edição por corte removeu 3 testes do lint sem eu perceber; o ledger da revisão citava 2 deles | achado pelo avaliador (ciclo 2, B6); os 3 voltaram |
| 5 | o auditor pago falhou na rodada 2 (saldo de US$ 0,07 não cobre a chamada) | rodadas 3, 4 e 5 com uma engine só, declarado; decisão do Roberto |
| 7 | o teto do método (3 rodadas, 2 ciclos) foi passado: 5 rodadas e 3 ciclos, cada extra por decisão do Roberto | os achados de cada volta eram variações do mesmo ponto (linha do ledger que escapava da conferência); a rodada 5 fechou com 2 leves, registrados como pendência |
| 9 | 4 logs do avaliador (ciclos 2 e 3) gravaram o exit do formatador depois do pipe, ou exit vazio: o `gate-shell-evidencia.sh` os acusou | viraram `*.aval.txt` com uma nota no topo e deixaram de valer como prova de exit; nenhum AT os citava (os ATs citam `AT-00N.log` e o `VERIFY-GATE.log`) |
| 8 | o lint pulava linha de tabela dentro de comentário e de bloco cercado, e o `loop` as lê (rodada 4, R3) | as duas ferramentas conferem toda linha de tabela; cerca reconhecida como no CommonMark (ciclo 3, C1) |
| 6 | a governança não deu N.A. (o medidor soma dinheiro) e o projeto não tem padrão | dispensa do Roberto com 2 cuidados aplicados: aritmética decimal exata e "sem custo informado nunca é zero" |

---

## Deviations from Design

| Desvio | Motivo |
|---|---|
| a tabela do medidor tem a coluna `Cobrança`, que o DESIGN não listava | sem ela não se entende por que o pago de uma linha é `0.0000` ou `n/d` |
| os scripts têm mais regras que o DESIGN v1.2 (linha fora da tabela, cerca só de linha inteira, guarda contra traceback, avisos de exit ausente e de rebatida marcada `sim`) | achados da revisão (5 rodadas) e do avaliador (3 ciclos); o aceite está no DEFINE v1.4 |
| a branch nasceu de `9581740` local antes do push da `v2.9.0` | adiantar o trabalho enquanto o CI da F21 rodava; o push foi fast-forward para o mesmo commit, então a base é `origin/main` |

**Drift detectado:** nenhum arquivo fora do manifest (`git diff --name-status origin/main HEAD`: 41 novos e 14 alterados).

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o repositório do pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** NEEDS_WORK · ciclos: 3 · achados: 6 no ciclo 1 (A1 a A6), 7 no ciclo 2 (B1 a B7), 6 no ciclo 3 (C1, C1b e C2 pediam conserto; C3 a C5 eram limites a declarar) · `AVALIACAO_F19_CUSTO_REVISORES_20261110-ciclo3.md` (ciclos 1 e 2: `AVALIACAO_F19_CUSTO_REVISORES_20261110-ciclo1.md`, `AVALIACAO_F19_CUSTO_REVISORES_20261110-ciclo2.md`)

O avaliador não chegou a dar PASS: o último veredito (ciclo 3, sobre `0d4a730`) é NEEDS_WORK. Os consertos que ele pediu entraram em `dcf95ac` (cerca como no CommonMark; a regra das 4 barras dita na mensagem, na ajuda e no molde; limites declarados na ajuda dos dois scripts) e **não foram reavaliados por ele**: o que os cobre é o Verify Gate, os testes novos (`test_cerca_segue_o_commonmark` nos dois arquivos, `test_a_mensagem_da_linha_solta_diz_como_escrever_texto_com_barras`, `test_papel_sem_engine_e_com_custo_vai_para_fora_da_conta`) e a rodada 5 da revisão, de uma engine só. O teto era de 2 ciclos; o 3º foi decisão do Roberto, e ele escolheu fechar com a rodada 5 em vez de um 4º ciclo.

---

## Advisor Ledger

**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F19_CUSTO_REVISORES.md` (15 linhas, 5 rodadas; `ledger-revisao-lint.sh` verde; é o primeiro ledger gravado no formato desta frente)

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 | `EXTERNAL_REVIEW_20261110-145510` | revisor por assinatura, auditor pago | 4 do revisor, 1 novo do auditor | 4 aplicados (2 com dano), 1 rebatido com evidência |
| 2 | `EXTERNAL_REVIEW_20261110-150330` | revisor; o auditor pago falhou por saldo | 3 | 3 aplicados |
| 3 | `EXTERNAL_REVIEW_20261110-152824` | uma engine só | 2 | 1 aplicado, 1 rebatido com evidência |
| 4 | `EXTERNAL_REVIEW_20261110-160021` | uma engine só | 3 | 3 aplicados (1 com dano) |
| 5 | `EXTERNAL_REVIEW_20261110-162917` | uma engine só | 2 leves | pendência registrada (fora do escopo do fecho) |

`--conferir` em `dcf95ac`: CONFERE (`sha256` do diff igual ao da rodada 5), `diversidade=nenhuma`, 2º revisor dispensado. O que isso quer dizer: da rodada 3 em diante quem auditou foi a mesma engine que revisou, então a auditoria tem os mesmos pontos cegos da revisão.

**Pendências que saem desta frente:** (1) a coluna `Cobrança` falta na tabela de colunas da seção do medidor, nos 2 documentos (rodada 5, R1); (2) papel `indisponível` sem exit e sem custo no `META.txt` é pulado sem aviso (rodada 5, R2); (3) o que vem depois de `-->` na mesma linha não é lido, e o medidor conta `sim` sem conferir o teste: limites declarados na ajuda (ciclo 3, C3 a C5).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.4) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | When o medidor roda sobre as revisões ⇒ tabela por papel, engine e modelo, exit 0 MEDIDO | true | `evidence/F19_CUSTO_REVISORES/AT-001.log` |
| AT-002 | custo pago e nominal em soma decimal exata; sem custo informado nunca vira zero; estimado e incerto marcados | true | `evidence/F19_CUSTO_REVISORES/AT-002.log` |
| AT-003 | achados cruzados com o ledger: aplicados, com dano, falsos positivos, fora de escopo, sem classificar | true | `evidence/F19_CUSTO_REVISORES/AT-003.log` |
| AT-004 | While a chamada falhou ⇒ conta em falhas, com o custo; engine trocada ganha a falha; "fora da conta" diz o motivo | true | `evidence/F19_CUSTO_REVISORES/AT-004.log` |
| AT-005 | If não há dados ⇒ exit 2 SEM DADOS; uso errado ⇒ 64; linha fora do formato nunca some em silêncio | true | `evidence/F19_CUSTO_REVISORES/AT-005.log` |
| AT-006 | lint do ledger: toda linha de tabela conferida (também em cerca e comentário), 7 células, dano com teste, exits 0 · 2 · 64 | true | `evidence/F19_CUSTO_REVISORES/AT-006.log` |
| AT-007 | shall continue to: o `loop` fecha com o ledger de 7 colunas como com o de 5; `eval-agree` verde | true | `evidence/F19_CUSTO_REVISORES/AT-007.log` |
| AT-008 | critério de dano, molde, texto do build (gravar, lint, loop) e da release (conferir o lint), documentos nos 2 idiomas, contratos | true | `evidence/F19_CUSTO_REVISORES/AT-008.log` |
| AT-009 | When `init --vendors claude --yes` ⇒ os 4 arquivos chegam iguais e o medidor roda no projeto | true | `evidence/F19_CUSTO_REVISORES/AT-009.log` |

**Verify Gate (`sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F19_CUSTO_REVISORES.md`):** exit 0 em `dcf95ac` (1.864 testes) · `evidence/F19_CUSTO_REVISORES/VERIFY-GATE.log`

---

## Final Status

### Overall: ✅ COMPLETE

- [x] 20 linhas do manifest
- [x] Verify Gate verde, linha de base vermelha, 6 sabotagens mortas
- [x] ATs com evidência abrível
- [x] revisão: 5 rodadas, a última confere com o commit final (uma engine só, declarado)
- [ ] avaliador de contexto novo: sem PASS (NEEDS_WORK no ciclo 3; consertos aplicados e não reavaliados, decisão do Roberto)
- [x] Pronto para a `sdd-release`, com as ressalvas acima no bloco do OK

---

## Next Step

**If Complete:** `/sdd-release F19_CUSTO_REVISORES` — bump minor do pacote (`v2.10.0`)

**Depois do build (2026-11-10):** a tag `v2.10.0` foi enviada em `dcf95ac` e ficou sem Release: o job de testes do Ubuntu do `release.yml` foi cancelado pelo teto de 25 min, sem teste vermelho. Por decisão do Roberto, o commit `36d0454` subiu o teto para 45 min e a frente saiu como `v2.10.1`.
