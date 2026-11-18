# BUILD REPORT: F23B2 Modelo por papel (fatia B2 da F23)

> Cada papel despachado em contexto fresco (curador, avaliador, revisor do DESIGN, cartógrafo, executor do piloto)
> ganha um slot de modelo em `papeis:` do `sdd/config.yaml`, lido e validado por `sdd-fluxo.sh modelo`; o
> `custo-feature.sh` mostra o custo de cada papel em sub-linhas fora do total e mede uma execução avulsa com
> `--execucao`; o `papel-serie.sh` roda séries de medição com teto, trava, cópia isolada e retomada; o
> `papel-medir.sh` pontua contra um gabarito tirado do histórico e escolhe o modelo mais barato que bate a meta, ou
> diz por que não escolheu. Prova: o curador mediu (sonnet, 64% mais barato, 12 de 12 na meta); o avaliador não
> calibrou (referência fora da meta), e o slot dele fica vazio.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23B2_MODELO_POR_PAPEL (família F23_ECONOMIA_MENSURAVEL) |
| **Date** | 2026-11-17 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F23B2_MODELO_POR_PAPEL.md](../features/DEFINE_F23B2_MODELO_POR_PAPEL.md) (v1.2) |
| **DESIGN** | [DESIGN_F23B2_MODELO_POR_PAPEL.md](../features/DESIGN_F23B2_MODELO_POR_PAPEL.md) (v1.2) |
| **Status** | Complete — Verify Gate verde em `c12a475` (2.491 testes, 3 pulados); 5 rodadas de revisão do código (4ª e 5ª com o OK do Roberto) e o raio de impacto da release; prova: curador medido, avaliador com a referência fora da meta (decisão do Roberto); CI do Windows pede o push da branch (PR) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 16/16 linhas do manifest, mais o modo web e os testes de versão da `sdd-build` (Drift 1) |
| **Files Created** | 22: `sdd/bin/papel-serie.sh`, `sdd/bin/papel-medir.sh`, `docs/model-per-role.md` e o pt-BR, `tests/test_f23b2_papeis.py`, 17 em `sdd/fixtures/f23b2/` |
| **Lines of Code** | `git diff --stat origin/main..HEAD`: 38 arquivos, +2.692 −20 |
| **Build Time** | 2026-11-16 21:06 a 2026-11-17 (horário de Brasília; marcas da fase), com as séries de medição |
| **Tests Passing** | Verify Gate exit 0 em `c12a475`: 2.491 testes em 27 min, 3 pulados (`evidence/F23B2_MODELO_POR_PAPEL/VERIFY-GATE-c12a475.log`); `tests/test_f23b2_papeis.py` com 56 testes; partida: 2.435 na `v2.20.0` |
| **Agents Used** | 0 especialistas (build direto); 2 agentes em contexto novo para montar e conferir casos do gabarito; as séries chamam o agente por `claude -p` (assinatura) |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 16 linhas de manifest; 2 scripts novos que dividem o leitor de custo da B1 e a regex do modelo com o `sdd-fluxo.sh` |
| Recomendação | default — um autor mantém a mesma regex e o mesmo leitor nos 3 scripts |
| Decisão do usuário | default [auto] (frente autônoma; a regra da frente manda decidir pela recomendada) |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-16 sobre `fb7ee82` (as 26 do DESIGN, todas re-lidas): LM-001,
LM-002, LM-003, LM-005, LM-006, LM-009, LM-010, LM-011, LM-012, LM-014, LM-015, LM-016, LM-017, LM-018, LM-021,
LM-028, LM-029, LM-030, LM-031, LM-033, LM-036, LM-037, LM-038 — ✔ tratado conforme a tabela do DESIGN; LM-013,
LM-024, LM-035 — N.A. (motivo no DESIGN). LM-002 deixou o baseline vermelho em `BASELINE-VERMELHO.log`. LM-011 (série
antiga primeiro) segurou a medição do avaliador: a referência saiu da meta e nenhum candidato foi chamado. LM-031
mordeu de leve: a suíte desta frente rodou em paralelo com o gate da F24 e ficou lenta, sem falhar. Hit novo do build:
nenhum.

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `papel-serie` `caixa de areia` `sandbox` `allowLocalBinding` `mktemp`
regra: Medir um papel por série num agente com caixa de areia mede outra coisa se a caixa de areia for mais fechada que a sessão em que o papel rodou de verdade: na F23B2, a 1ª execução do avaliador não abriu porta local (o gate do caso sobe stub) nem a pasta temporária do macOS (`mktemp -d`), e saiu quase toda NAO_VERIFICADO; mais 2 execuções seguiram sem o `/tmp`. **Do instead:** antes da série, rode o comando do Verify Gate de um caso dentro do comando da série e compare com a sessão real; libere na caixa de areia só o que faltar (porta local, pasta temporária), nunca as permissões inteiras.
evidencia: sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/MEDICAO-avaliador-tentativas.md
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `gabarito` `avaliador` `referência fora da meta` `papel-medir`
regra: Um caso de gabarito do avaliador tirado do histórico só calibra se a falha dele aparecer por execução direta, e mesmo assim o modelo de referência pode errar numa repetição: na F23B2, o caso F11 (falha achada por sabotagem) e o F21 (falha que um grep acha) saíram com o AT que falha dado como aprovado já na 1ª execução da referência. **Do instead:** escolha casos com falha observável por execução e, antes de rodar as 9 execuções, rode 1 da referência por caso; se ela já sai da meta, troque o caso ou redesenhe a meta antes de gastar o resto.
evidencia: sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/MEDICAO-avaliador-tentativas.md
ficha: —
mordeu_antes: LM-011
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `papel-serie` `retomada` `interrupção` `SIGKILL` `trava` `executor de agente`
regra: Um executor que lança agente em sessão própria e retoma depois de interrupção tem uma matriz de casos (Ctrl-C, SIGTERM, SIGKILL do executor com o agente vivo, duas séries na mesma pasta, retomada com outro modelo, interrompida que escreveu no projeto); na F23B2 a revisão achou um grave novo dessa matriz em cada uma das rodadas 1 a 4. **Do instead:** no DESIGN, escreva a matriz de interrupção e concorrência do executor, com um teste por célula, antes do 1º commit; use trava do sistema (flock), que some com o processo.
evidencia: sdd/reviews/LEDGER_REVISAO_F23B2_MODELO_POR_PAPEL.md
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `os.name` `test_windows` `apoio.py` `WINDOWS`
regra: Teste que pergunta a plataforma com `os.name` (ou `sys.platform`) derruba o Verify Gate inteiro no `test_windows.Pulos`; na F23B2 custou um gate de 26 minutos. **Do instead:** importe `WINDOWS` ou a constante `SEM_*` de `tests/apoio.py` e rode `test_windows` junto do módulo novo antes do gate.
evidencia: sdd/reports/evidence/F23B2_MODELO_POR_PAPEL/VERIFY-GATE-77ba5f7.log
ficha: —
mordeu_antes: —
>>>
```

## Drift detectado

| # | Onde | O que divergiu do DESIGN | Decisão | Ação |
|---|---|---|---|---|
| 1 | `.agents/skills/sdd-build/web/MODO_WEB.md` e 5 testes de versão | o manifest não listava o modo web nem os testes que fixam a versão da `sdd-build` | desvio aprovado (consequência da linha 7) | 2.13.0 no modo web e em `test_contrato_build_release`, `test_correcoes_w0`, `test_f15_slots_textos`, `test_f19_textos`, `test_f18_f20_textos` |
| 2 | `papel-medir.sh` (Decision 7) | com a série parada pela barreira (exit 22), o `PARADA.txt` fazia o medidor dizer PARCIAL em vez de "referência fora da meta" | [auto] referência incompleta → PARCIAL; fora da meta → 3; depois parada, meia série ou inválida → PARCIAL — porque a calibração vem antes do resto · para desfazer: voltar a ordem antiga em `parcial()` | DESIGN v1.1; teste `test_parcial_vem_antes_da_referencia…` |
| 3 | `caso.txt` (formato do gabarito) | campo opcional `base:` | [auto] a cópia ganha um commit com a árvore de `base:`, marcado com o mesmo nome, antes do caso — porque o teste de não regressão compara com a tag da versão anterior e o `git archive` não leva tags · para desfazer: tirar o campo | `ddd191a`, teste `test_base_vira_tag…`, docs |
| 4 | `gabarito/ava-*/brief.md` (fora do pacote) | o brief do avaliador da época pedia relatório livre; o medidor lê a tabela por AT | [auto] uma linha a mais no brief pedindo a tabela `\| AT-nnn \| … \| resultado \|` — porque sem ela o medidor não lê o resultado por AT; vale igual para a referência e os candidatos · para desfazer: tirar a linha e escrever um leitor de prosa (contra a Decision 7) | LLM Prompts continua `false`: o brief é dado de medição |
| 5 | casos do curador | o DESIGN citava a curadoria da F16W; os logs dela eram da F17C | [auto] trocado por F14 drive, F14 playbook, F23 e F23B3 — porque o gabarito tem de casar com a colheita que o curador leu · para desfazer: refazer o caso com o log da F16W | achado do agente de conferência |
| 6 | `papel-serie.sh` (Decision 5) | `entrada/` entrava no commit da cópia | [auto] `entrada/` vai por cima depois do commit, fora do git — porque o DEFINE e o DESIGN da época não estavam no git, e o publish-gate da cópia os acusava (achado falso na série real) · para desfazer: voltar a cópia antes do commit | `2c2fd37`, teste no `test_base_vira_tag…`, docs |
| 7 | Decision 4 | `--casos` não foi implementado | [auto] sai da Decision 4 (DESIGN v1.2) — porque a barreira exige a referência inteira e a retomada cobre o caso longo · para desfazer: filtro e barreira por caso | R2 da rodada 3 |
| 8 | gabarito do avaliador | o caso `ava-f11-gate-c1` saiu | [auto] trocado por `ava-f21-engenharia-reversa-c1` — porque a falha do F11 só aparecia por sabotagem e a referência não a repetiu (o DEFINE manda recalibrar antes de qualquer candidato) · para desfazer: devolver a pasta de `gabarito-descartado/` | o DEFINE do F21 foi reconstruído (a versão guardada tinha 1 linha mudada depois da avaliação) |
| 9 | comando da série (fora do pacote) | a caixa de areia do `claude -p` | [auto] porta local e `/var/folders` liberadas, o resto do disco bloqueado — porque a sessão em que o avaliador rodou de verdade tinha os dois · para desfazer: voltar ao `settings` só com `sandbox.enabled` | `/tmp` seguiu bloqueado (o publish-gate do caso grava lá) |
| 10 | prova do avaliador | o DEFINE pedia ≥ 3 casos medidos | decisão do Roberto (2026-11-17): registrar "referência fora da meta" e redesenhar a meta numa próxima fatia | slot do avaliador vazio; pendência na ficha |

Varredura de prompt: nenhum arquivo do manifest é prompt de produção.

Commits antes e depois do rebase sobre a `main` com a F24 (o ledger cita os de antes): `adfbef3`→`ce70fc9`,
`f512f0f`→`ddd191a`, `1fc9ce4`→`367c625`, `5706214`→`2c2fd37`, `e60222c`→`fd31760`, `7b84b5d`→`60094b1`,
`36cf144`→`77ba5f7`; depois, `1ec18a8` (o teste da trava sem `os.name`).

---

## Files Created

| File | Lines | Verified | Notes |
|------|-------|----------|-------|
| `sdd/bin/papel-serie.sh` | ver git | ✅ | executor das séries: teto e trava (flock), cópia isolada, fronteira (também na retomada), retomada, custo por execução |
| `sdd/bin/papel-medir.sh` | ver git | ✅ | medidor só de leitura: pontua curador e avaliador, valida o gabarito, escolhe ou diz por que não |
| `docs/model-per-role.md`, `docs/pt-BR/model-per-role.md` | ver git | ✅ | o método, sem nome nem preço de modelo |
| `sdd/fixtures/f23b2/` (17 arquivos) | ver git | ✅ | gabarito sintético, agente falso, preços de modelos fictícios |
| `tests/test_f23b2_papeis.py` | ver git | ✅ | 53 testes: AT-001 a AT-011 e os achados das 5 rodadas |

---

## LLM Prompts

N.A. — LLM Prompts `false` no DEFINE (re-check no DESIGN e no build: o executor manda o brief do caso; o pacote não
leva prompt novo).

---

## Verification Results

### Lint · Typecheck

N/A — o Open não tem `lint_cmd` nem `typecheck_cmd`. Lints do pacote: `design-lint.py` no DESIGN (✅),
`sdd-fluxo.sh --self-test` (VERDE), `check-versions.py --base origin/main` (VERDE depois do rebase),
`publish-gate.sh` numa cópia de `git archive` (GREEN), `ledger-revisao-lint.sh` no ledger da frente (VERDE). `gate-shell-evidencia.sh` nos logs desta frente (`evidence/F23B2_MODELO_POR_PAPEL/*.log`: VERDE); os logs do gabarito são entrada histórica de casos, copiada sem mudança (2 deles, da F14, gravam o exit de um `cut`/`sort`), e ficam de fora da conferência.

### Testes

Gate vermelho antes, corrigido: `77ba5f7` (`test_windows.Pulos`: `os.name` no teste da trava; `VERIFY-GATE-77ba5f7.log`).

```text
$ bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23B2_MODELO_POR_PAPEL.md   # HEAD c12a475
Ran 2491 tests in 1619.277s
OK (skipped=3)
RESULTADO: VERDE
```

**Status:** ✅ 2.491 Pass | 0 Fail

---

## Advisor Ledger

**Consulta:** delivery-review · 2026-11-16/17 · `sdd/bin/adversarial-review.sh` (pastas em `sdd/reports/reviews/`)
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F23B2_MODELO_POR_PAPEL.md`
**Proveniência:** revisor claude (assinatura); auditor codex (assinatura), com o modelo da OpenRouter de reserva (não
chamado: pago); 2º revisor pela regra da B3 (sem superfície de risco: dispensado em todas as rodadas, linha no ledger).

| Rodada | Pasta | Achados | Decisão |
|---|---|---|---|
| DESIGN D1 | `EXTERNAL_REVIEW_20261116-205900` | 11 + 1 do auditor | 10 aplicados, 2 rebatidos com evidência |
| código 1 | `EXTERNAL_REVIEW_20261116-230146` | 7 + 1 do auditor (2 graves) | 8 aplicados com teste (`367c625`); refeita cobrada em dobro confirmada |
| código 2 | `EXTERNAL_REVIEW_20261116-233506` | 4 + 2 do auditor (2 graves) | 6 aplicados com teste (`fd31760`) |
| código 3 (teto) | `EXTERNAL_REVIEW_20261116-235036` | 4 + 1 do auditor (1 grave) | 4 aplicados com teste (`60094b1`), 1 rebatido |
| código 4 (D4: Roberto) | `EXTERNAL_REVIEW_20261117-054829` | 5 + 2 do auditor (1 grave) | 6 aplicados com teste (`77ba5f7`), 1 rebatido |
| código 5 (D4: Roberto) | `EXTERNAL_REVIEW_20261117-065720` | 1 + 1 do auditor (0 graves) | 2 pendências, sem código novo (regra combinada); `loop`: PRONTO |

Cada rodada de código achou um caso de borda novo do executor das séries (interrupção, sinal, trava, retomada): é o
candidato ao playbook acima. Custo da revisão: claude US$ 1,4247 + 1,5297 + 1,6007 + 1,7298 + 1,9212 nominal
(assinatura) e US$ 0,9046 no DESIGN; codex por assinatura.

**Raio de impacto da release (3 agentes em contexto novo, um por superfície):** o `custo-feature.sh` sem consumidor
quebrado; o `despachar`/`modelo`/`papeis:` sem quebra no caminho normal (todos os leitores do config filtram pelo bloco);
as marcas `papel-*` com 2 consumidores quebrados e 1 condicional — a marca gravada no meio das fotos da fronteira
reprovava o cartógrafo, a governança e o curador do lote; o papel fora da janela das fases (o curador do lote, depois
da release) saía n/d com as mensagens descartadas; e, num projeto com o `sdd-fluxo.sh` antigo (editado, o upgrade o
mantém), o 64 do verbo desconhecido seria lido como slot inválido. Os 3 consertados com teste em `c12a475` (vermelhos
em `1ec18a8`: `RAIO-VERMELHO.log`). Ficam como pendência: a sub-linha do papel soma também as mensagens da sessão
principal na janela (o pedido do subagente e o fim, com o cache do contexto); o tempo ativo do papel sai 0h00m; a
parada não documenta o campo **Modelo:** em `PERGUNTA_DECISAO.md`; o `--execucao` com pasta inexistente sai 2.

**Conferência da release:** a rodada 5 revisou `77ba5f7`, já rebaseado na `main` com a F24; o delta até o HEAD são
`1ec18a8` (uma linha de teste: `os.name` → `WINDOWS`, para o `test_windows` passar) e `c12a475` (os 3 consertos do raio
de impacto, cada um com teste vermelho antes e verde depois). Depois, `4f2acb2`: no Windows a trava do `msvcrt` é obrigatória e, no byte 0, a foto do projeto não lia o arquivo da trava (toda série saía 64 no CI do PR #37); a trava passa a um byte além do fim do arquivo.

---

## Segurança

| Item | Decisão | Motivo |
|---|---|---|
| S20 Agente com poder demais e sem teto | aplicado (AT-008, AT-011) | teto pago e nominal com trava em código; cópia fora do projeto, sem remoto, com foto do projeto antes e depois (e na retomada); agente morto junto com a série; uma série por pasta |
| S18 Instrução escondida em conteúdo externo | recusado [auto] | o conteúdo das séries é o histórico do próprio Open, já publicado; os briefs não mudam (só a linha do formato, Drift 4) |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | os casos do avaliador falhavam na cópia: o teste de não regressão compara com a tag anterior, e o `git archive` não leva tags | campo `base:` (Drift 3) | um commit |
| 2 | o medidor dizia PARCIAL depois da barreira por causa do `PARADA.txt` | ordem do veredito (Drift 2) | — |
| 3 | a F24 em andamento na mesma base | build já; gate, suíte inteira e séries depois da F24 na `main`; rebase com 1 conflito (linha de versões) | espera |
| 4 | a 1ª série do avaliador rodou numa caixa de areia mais fechada que a sessão real, e com `entrada/` commitada | série descartada; Drifts 6 e 9 | US$ 5,21 nominal |
| 5 | a referência do avaliador saiu da meta em 2 casos | caso trocado uma vez (Drift 8); depois, decisão do Roberto (Drift 10) | US$ 9,03 nominal |
| 6 | 5 rodadas de revisão de código, 2 além do teto | D4 duas vezes ao Roberto (rodadas 4 e 5) | ~4 h |
| 7 | Verify Gate vermelho em `77ba5f7`: `test_windows` barra `os.name` no teste da trava | `1ec18a8` | um gate |
| 8 | raio de impacto: marca de papel no meio das fotos da fronteira, papel fora da janela das fases, 64 do script antigo | `c12a475`, com teste | um gate |
| 9 | CI do PR #37: no Windows, a trava obrigatória do `msvcrt` no byte 0 derrubava a foto do projeto (19 testes do executor e do medidor saíram 64) | `4f2acb2`, trava num byte além do fim; provado pelo CI | um CI |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| campo `base:` no `caso.txt` | Drift 3 | 1 campo opcional no formato do gabarito |
| ordem do veredito do medidor | Drift 2 | a calibração aparece antes da parada |
| `entrada/` fora do commit da cópia | Drift 6 | a cópia fica como o projeto estava na época |
| sem `--casos` | Drift 7 | DESIGN v1.2 |
| trava da pasta de medição, fronteira na retomada, agente morto com a série | rodadas 2 a 4 da revisão | o executor ficou maior que o desenhado; a matriz de interrupção virou candidato ao playbook |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (scripts do método, texto de uma skill, docs e testes; o Open não tem `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** N.A. (1 camada) — os ATs foram provados por execução, um log por AT

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | **Where** `papeis.<papel>` está preenchido no `sdd/config.yaml`, o `sdd-fluxo.sh despachar <papel>` **shall** dizer na parada qual modelo abrir na sessão nova, e o leitor do slot **shall** devolver o mesmo valor ao despacho por subagente; vazio ou ausente, a parada e o despacho **shall continue to** sair como hoje, sem linha de modelo. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-001.log` |
| AT-002 | **If** o valor de `papeis.<papel>` tem quebra de linha, espaço, aspas, caractere fora de letras, números, `.`, `_`, `:`, `/` e `-`, começa por algo que não seja letra ou número (um `-` viraria opção do agente), ou tem mais de 80 caracteres, **then** o leitor do slot **shall** sair 64 com a chave e o motivo, sem despachar nem repassar o valor. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-002.log` |
| AT-003 | **When** uma feature tem um papel despachado entre a marca de início e a de fim dele, o `custo-feature.sh` **shall** imprimir uma linha por papel (execuções, tokens, nominal, modelo) e manter o total da feature igual à soma das fases mais a revisão, sem somar o papel duas vezes. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-003.log` |
| AT-004 | **When** o medidor lê as execuções do curador e o gabarito, ele **shall** pontuar cada execução (precisão e recall das contagens; `ADD`/`REFINE` encontrados; delta aceito pelo `playbook-curator.sh --aplicar`) e marcar a execução como dentro ou fora da meta. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-004.log` |
| AT-005 | **When** o medidor lê as execuções do avaliador e o gabarito, ele **shall** comparar o veredito e o resultado por AT e marcar fora da meta toda execução que der como aprovado um AT que falha no gabarito, mesmo com o resto igual. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-005.log` |
| AT-006 | **When** o medidor tem as séries de um papel, ele **shall** escolher, entre os candidatos que batem a meta em todas as repetições de todos os casos, o de menor nominal mediano por execução, em aritmética exata; **shall** dizer "referência fora da meta" sem escolher ninguém quando a referência não bate a meta; e "sem ganho medido" quando nenhum candidato bate a meta ou nenhum fica ≥ 30% abaixo da referência. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-006.log` |
| AT-007 | **If** o custo de um candidato sai n/d (sem registro de sessão ou sem preço na tabela), **then** o medidor **shall** mostrá-lo como n/d, nunca como zero, e **shall** recusar escolhê-lo como o mais barato. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-007.log` |
| AT-008 | **If** a próxima execução pode levar o gasto acumulado da série acima do teto (pago ou nominal), ou o candidato tem cobrança pay-per-token ou desconhecida com teto pago zero, **then** o executor das séries **shall** parar antes de chamar o agente, gravar o motivo e o acumulado, e o medidor **shall** marcar o resultado como parcial, sem escolher vencedor. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-008.log` |
| AT-009 | **While** a pasta da série já tem execuções gravadas, o executor das séries **shall** retomar só as que faltam e somar ao acumulado o gasto das já gravadas, sem repetir nem recontar nenhuma. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-009.log` |
| AT-011 | **If** o agente de uma execução da série grava fora da cópia isolada do caso, ou a cópia tem remoto git configurado, **then** o executor das séries **shall** marcar a execução como inválida (fora da conta e da escolha), parar a série e gravar os caminhos tocados, sem apagar nada fora da cópia. | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-011.log` |
| AT-010 | O pacote **shall** manter a suíte inteira verde, sem nome nem preço de modelo em arquivo do pacote (os exemplos usam marcador), com os arquivos novos no `MANIFEST.txt`, as skills e docs dizendo o slot e o método, e o gerador do starter verde (troca em `scripts/starter/trocas/` para texto que só vale no Open). | true | `evidence/F23B2_MODELO_POR_PAPEL/AT-010.log` · gate: `evidence/F23B2_MODELO_POR_PAPEL/VERIFY-GATE-c12a475.log` |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 em `c12a475` · `evidence/F23B2_MODELO_POR_PAPEL/VERIFY-GATE-c12a475.log`

**Critérios de sucesso:**
- Gabarito: curador com 4 casos (F14 drive, F14 playbook, F23, F23B3) ✅; avaliador com 3 casos (F6 c1, F6 c2, F21) ✅,
  depois de trocar o F11 (Drift 8).
- Referência primeiro, 3 repetições: curador 12 de 12 na meta ✅; avaliador fora da meta na 1ª execução do F11 e do
  F21 ❌, e a barreira não chamou nenhum candidato (LM-011).
- Curador: **ESCOLHIDO sonnet**, 12 de 12 na meta, mediana US$ 0,32 contra US$ 0,90 da referência (queda de 64%); o
  haiku ficou em 7 de 12 (`MEDICAO-curador.md`). ✅
- Avaliador: **referência fora da meta**, slot vazio, sem economia contada; meta a redesenhar numa próxima fatia
  (decisão do Roberto, `MEDICAO-avaliador-tentativas.md`). ❌ registrado
- Teto: US$ 30,35 nominal de US$ 200,00; US$ 0 pago ✅.
- Suíte verde no macOS ✅ (gate acima); `testes-windows` no CI do PR: no CI do PR, na release.

---

## Final Status

### Overall: ✅ COMPLETE (prova parcial: o avaliador ficou com a referência fora da meta, registrado)

---

## Next Step

**If Complete:** `sdd-release` — modelo por papel (fatia B2 da F23), com o curador provado e o avaliador registrado
como referência fora da meta.
