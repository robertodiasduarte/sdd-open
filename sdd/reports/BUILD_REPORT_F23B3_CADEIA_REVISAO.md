# BUILD REPORT: F23B3 Cadeia de revisão pelos dados (fatia B3 da F23)

> O 2º revisor passa a ser chamado só por superfície de risco (ou revisor raso), com a regra antiga gravada como
> medida; a lista de termos de segurança é uma só; o desempate fica padrão e a dispensa à mão fica no META; o ledger
> ganha `rodada=D<n>`, `sem resultado:` e `escapou:`; o `eval-revisores.sh` mostra a cadeia por frente e estima o
> nominal do codex com `--precos`; os prompts da revisão vão para `v2/`, com o material cercado por marca por chamada.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23B3_CADEIA_REVISAO (família F23_ECONOMIA_MENSURAVEL) |
| **Date** | 2026-11-16 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F23B3_CADEIA_REVISAO.md](../features/DEFINE_F23B3_CADEIA_REVISAO.md) (v1.2) |
| **DESIGN** | [DESIGN_F23B3_CADEIA_REVISAO.md](../features/DESIGN_F23B3_CADEIA_REVISAO.md) (v1.1) |
| **Status** | Complete — Verify Gate verde em `5e110b2` (2.364 testes, 3 pulados), depois do raio de impacto e de 3 rodadas de revisão do código; CI do Windows pede o push da branch (PR) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 20/20 linhas do manifest (1 sem mudança, ver Drift), mais MANIFEST.txt, arquivos de modo e testes de versão |
| **Files Created** | 4: `sdd/review/prompts/v2/{reviewer,auditor,desempate}.md`, `tests/test_f23b3_revisao.py` |
| **Lines of Code** | ver `git diff --stat origin/main..HEAD` |
| **Build Time** | 2026-11-16 12:46 a 17:13 (horário de Brasília; marcas da fase) |
| **Tests Passing** | Verify Gate exit 0 em `5e110b2`: 2.364 testes em 26 min, 3 pulados (`evidence/F23B3_CADEIA_REVISAO/VERIFY-GATE-5e110b2.log`); antes, verde em `cfc87f9` (2.356); partida: 2.315 na `v2.18.0`; `tests/test_f23b3_revisao.py` com 49 testes |
| **Agents Used** | 0 especialistas (build direto); 2 juízes em contexto novo para o S18 |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 20 linhas de manifest muito acopladas: funções copiadas em 2 scripts com teste que compara, campos novos do META em 4 scripts |
| Recomendação | default — um autor lembra nomes e assinaturas compartilhadas |
| Decisão do usuário | default, 2026-11-16 (Roberto: "padrão, eu mesmo nesta sessão") |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-16 sobre `e1870e3` (as do DESIGN, todas re-lidas): LM-001,
LM-002, LM-003, LM-005, LM-006, LM-009, LM-010, LM-011, LM-012, LM-013, LM-014, LM-015, LM-017, LM-018, LM-021,
LM-028, LM-029, LM-030, LM-031, LM-035, LM-036 — ✔ tratado conforme a tabela do DESIGN. LM-031 mordeu na forma de
2 testes de tempo de fora da fatia (ver Issues). Hit novo do build: nenhum.

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `MANIFEST.txt` `publish-gate` `undeclared file` `arquivo novo`
regra: Arquivo novo no pacote (prompt, teste, script) sem a linha dele no `MANIFEST.txt` derruba o Verify Gate inteiro no `publish-gate` ("undeclared file"), depois de montar a cópia limpa; na F23B3 custou um gate (os 3 prompts v2 e o módulo de testes novo). **Do instead:** ao criar arquivo no pacote, acrescente-o ao `MANIFEST.txt` no mesmo commit e rode `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh <cópia de git archive>` antes do gate inteiro.
evidencia: sdd/reports/evidence/F23B3_CADEIA_REVISAO/VERIFY-GATE-0c21571.log
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `injeção` `instrução escondida` `prova de prompt` `linha de base` `S18`
regra: Uma sonda de comportamento contra injeção que passa também na versão antiga do prompt não prova o ganho da versão nova: na F23B3, as 2 sondas do S18 (instrução escondida e falso fim de material) passaram 3 de 3 com os prompts v1 e com os v2. **Do instead:** rode a série da versão antiga primeiro; se ela já passa, registre "proteção sem ganho medido" e procure uma sonda que a versão antiga reprove antes de chamar a mudança de prova.
evidencia: sdd/reports/evidence/F23B3_CADEIA_REVISAO/S18-FORTE-JUIZ.log
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `500 linhas` `sdd-release` `SKILL.md` `teto` `test_conversa`
regra: A `sdd-release` está no teto de 500 linhas de `SKILL.md` (3 testes conferem); 2 linhas a mais derrubaram o Verify Gate inteiro da F23B3. **Do instead:** antes de acrescentar texto a uma skill, `wc -l` nela; no teto, condense a frase nova numa linha existente ou mova o detalhe para `references/`, e rode `test_conversa` antes do gate.
evidencia: sdd/reports/evidence/F23B3_CADEIA_REVISAO/VERIFY-GATE-7e3868b.log
ficha: —
mordeu_antes: —
>>>
```

## Drift detectado

| # | Onde | O que divergiu do DESIGN | Decisão | Ação |
|---|---|---|---|---|
| 1 | `sdd/fixtures/revisao/saidas/codex.jsonl` (linha 6 do manifest) | a fixture já trazia `cached_input_tokens` e `cache_write_input_tokens` no formato medido | sem mudança | nada |
| 2 | `tests/test_revisao_adapters.py`, `tests/test_eval_revisores.py` | o manifest não listava: a entrada do codex sem o cache e a 2ª tabela do medidor mudam o que eles conferem | desvio aprovado (consequência das Decisions 6 e 7) | o teste do codex espera 11.489; o ajudante `linhas()` lê só a 1ª tabela |
| 3 | `MANIFEST.txt`, 3 arquivos de modo (`web/MODO_WEB.md` de build e design, `references/MODO_INICIANTE.md` da release) e 7 testes de versão | o manifest não listava a declaração do pacote nem o que fixa a versão das skills | desvio aprovado | prompts v2 e o teste novo no MANIFEST; versões nos modos e nos testes |
| 5 | `tests/test_f22_upgrade.py` (fora do manifest) | a `foto()` do teste entrava em `.git` e caía sob carga | desvio aprovado pelo Roberto (2026-11-16) | percurso que pula `.git` (`cfc87f9`), commit à parte |
| 4 | Pattern 3 do DESIGN | `material()` corta as quebras de linha das pontas de cada seção antes de cercar | detalhe de implementação | nenhuma |

Varredura de prompt: os 3 arquivos de `sdd/review/prompts/v2/` são do inventário (saída 2 do `prompt-drift-scan.sh`,
esperada); nenhum outro arquivo do manifest é prompt de produção.

---

## Files Created

| File | Lines | Verified | Notes |
|------|-------|----------|-------|
| `sdd/review/prompts/v2/reviewer.md` | ver git | ✅ | v2 do revisor: `<material_rules>`, tentativa de instrução no DIFF vira achado |
| `sdd/review/prompts/v2/auditor.md` | ver git | ✅ | v2 do auditor: REVISÕES também são dado |
| `sdd/review/prompts/v2/desempate.md` | ver git | ✅ | v2 do desempate: ACHADO e AUDITORIA também são dado |
| `tests/test_f23b3_revisao.py` | ver git | ✅ | AT-001 a AT-009 e AT-011, trechos idênticos, mutantes, achados da rodada 1 |

---

## LLM Prompts

| # | Prompt | Tipo | Destino | Construído por | Drift-scan | Eval |
|---|---|---|---|---|---|---|
| 1 | revisor v2 | one-shot | `sdd/review/prompts/v2/reviewer.md` | `sdd-prompt-builder` (refator mínimo da v1) | saída 2 (esperada) | séries B das 2 sondas do S18: 3 de 3 e 3 de 3 |
| 2 | auditor v2 | one-shot | `sdd/review/prompts/v2/auditor.md` | idem | saída 2 | roda nas mesmas séries (cadeia inteira) |
| 3 | desempate v2 | one-shot | `sdd/review/prompts/v2/desempate.md` | idem | saída 2 | teste de texto no gate (AT-011) |

---

## Verification Results

### Lint · Typecheck

N/A — o Open não tem `sdd/config.yaml` com `lint_cmd` nem `typecheck_cmd`. Lints do pacote: `design-lint.py` no DESIGN
(✅), `ledger-revisao-lint.sh` no ledger da frente (VERDE), `prompt-drift-scan.sh` nos 3 prompts (2, esperado),
`publish-gate.sh` (GREEN em `7e3868b` em diante).

### Testes

Gates anteriores, vermelhos e corrigidos: `0c21571` (publish-gate: prompts v2 e o teste novo fora do MANIFEST),
`7e3868b` (a `sdd-release` com 502 linhas, 3 testes; e `test_f22_upgrade` instável), `3930f69` (2 instáveis de fora da
fatia: `test_checar` 12,02 s contra o teto de 12 s e `test_f22_upgrade` perdendo um objeto do git; os 2 passam sozinhos,
e o `test_checar` também falhou sozinho uma vez, 12,10 s, sem nada desta fatia no caminho dele).

```text
$ bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23B3_CADEIA_REVISAO.md   # HEAD 5e110b2
Ran 2364 tests in 1565.489s
OK (skipped=3)
RESULTADO: VERDE
```

Gate de `a84b2e3` (depois da revisão): 1 erro, o `test_f22_upgrade` de novo; causa achada (a `foto()` do teste entrava
em `.git` e um `git` em segundo plano apagava objetos no meio do `rglob`) e consertada com o OK do Roberto (`cfc87f9`).

Verde também em `cfc87f9` (2.356), antes do raio de impacto da release e das rodadas 2 e 3.

**Status:** ✅ 2.364 Pass | 0 Fail

---

## Advisor Ledger

**Consulta:** delivery-review · 2026-11-16 · `sdd/bin/adversarial-review.sh` (pastas em `sdd/reports/reviews/`)
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F23B3_CADEIA_REVISAO.md`
**Proveniência:** revisor claude (assinatura); auditor codex (assinatura), com o modelo da OpenRouter de reserva (não
chamado); 2º revisor pela regra desta fatia (sem superfície de risco: dispensado, linha no ledger); desempate padrão (sem
alvo nas rodadas).

| Rodada | Pasta | Achados | Decisão |
|---|---|---|---|
| DESIGN D1 | `EXTERNAL_REVIEW_20261116-115325` | 5 + 1 do auditor | 5 aplicados (R1 e R5 por decisão do Roberto: R1 aplicado, R5 rebatido) |
| código 1 | `EXTERNAL_REVIEW_20261116-155004` | 4 + 1 do auditor | 5 aplicados com teste (`a84b2e3`); 4 dos 5 testes caem no código antigo, o do R3 era teste fraco; `loop`: PRONTO |
| código 2 (revisão curta da release) | `EXTERNAL_REVIEW_20261116-171549` | 3 + 1 do auditor | 4 aplicados com teste (`7c1860f`), junto com o raio de impacto (19 testes vermelhos antes: `RAIO-E-RODADA2-VERMELHO.log`) |
| código 3 (teto) | `EXTERNAL_REVIEW_20261116-180430` | 2 + 1 do auditor | 2 aplicados (`5e110b2`), 1 rebatido com evidência; `loop`: PRONTO |

**Raio de impacto da release (3 agentes em contexto novo):** o `review-design` deixava de exigir revisão para camelCase (`AuthProvider.tsx`, `resetPassword.ts`); o gate offline lia o `~/.codex/config.toml` real; a revisão do `custo-feature.sh` perdia o cache nos tokens; o `docs/pt-BR/adversarial-review.md` descrevia a regra antiga — todos consertados com teste em `7c1860f`. Ressalvas que ficam como pendência: o medidor separa o codex antigo (`codex (-)`) do novo; o META não grava a versão do prompt; um prompt v1 editado à mão deixa de ser lido sem aviso.

**Conferência da release:** a rodada 3 revisou `7c1860f`; o delta até `5e110b2` são os 2 consertos dela, com teste, e o gate final roda nele. Publicação com `review_externo: dispensado — <motivo>` (decisão do Roberto, 2026-11-16).

Custo: claude US$ 0,7430 (D1) + 3,7263 + 3,6821 + 4,2703 (código 1 a 3) nominal, assinatura; codex por assinatura. A rodada 1 do código
foi a 1ª sob a regra nova: a regra antiga chamaria o 2º revisor (33 arquivos); a nova o dispensou (sem superfície de risco).

---

## Segurança

| Item | Decisão | Motivo |
|---|---|---|
| S18 Instrução escondida em conteúdo externo | aplicado (AT-011) | material cercado por marca por chamada, prompts v2; prova real em 2 sondas |
| S20 Agente com poder demais e sem teto | recusado | Roberto: "o teto de tempo basta" |
| S22 Correção que afrouxa uma proteção | registrado | tirar o gatilho por tamanho do 2º revisor afrouxa uma proteção: é a regra que o Roberto decidiu no Define (decisão 7 do BRAINSTORM), com volta atrás pelo `escapou:` |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | publish-gate vermelho: prompts v2 e o teste novo fora do `MANIFEST.txt` | declarados (`7e3868b`) | +50 min (um gate) |
| 2 | `sdd-release` com 502 linhas (teto de 500, 3 testes) | parágrafo do `escapou` condensado (`3930f69`) | +50 min |
| 3 | 2 testes instáveis de fora da fatia (`test_checar`, `test_f22_upgrade`) | `test_f22_upgrade`: causa achada e consertada (`cfc87f9`); `test_checar` (teto de 12 s rente ao tempo medido): pendência na ficha | +2 gates |
| 4 | o codex não informa o modelo na saída `--json` | `adapter_modelo_padrao` lê o `config.toml` (medido em 2026-11-16) | — |
| 5 | as 2 sondas do S18 passaram também na versão antiga | registrado: a cerca fica como defesa em profundidade, sem ganho medido | 24 chamadas por assinatura |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| campo `gatilho_risco_motivo` no META | R2 da revisão do código: o AT-002 pede o termo ou glob; o texto do gatilho não muda | 1 campo a mais |
| `sem achados:` aceita `rodada=D<n>` | R1 da revisão do código | revisão do DESIGN sem achados entra na conta |
| `termo_de_seguranca` normaliza para NFC | R4 da revisão do código | caminho acentuado em NFD casa |
| o rollback `PROMPTS_VERSAO = ""` não tem teste próprio | o script copiado para fora do pacote não acha os adapters; o teste confere a constante e a v1 no lugar | o rollback continua uma linha |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (scripts do método, prompts da revisão e texto das skills; o Open não tem `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** N.A. (1 camada) — os ATs foram provados por execução, um log por AT

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | **When** o diff congelado não toca superfície de risco, o `adversarial-review.sh` **shall** rodar só o revisor e o auditor, sem chamar o 2º revisor, com 8 ou mais arquivos, 120 KB ou 2 camadas, e gravar no META o motivo da dispensa e o gatilho que a regra antiga teria acionado. | true | `evidence/F23B3_CADEIA_REVISAO/AT-001.log` |
| AT-002 | **Where** `review.security_globs` ou `layers.sql` estiverem preenchidos, o `adversarial-review.sh` **shall** acionar o 2º revisor quando um caminho do diff casar um desses globs ou trouxer um segmento de segurança, gravando o caminho e o termo ou glob; vazios, só os segmentos fixos acionam; a lista de termos é a mesma do `sdd-fluxo.sh review-design`, lida pela mesma função. | true | `evidence/F23B3_CADEIA_REVISAO/AT-002.log` |
| AT-003 | O `adversarial-review.sh --conferir` **shall continue to** recusar a revisão com superfície de risco rodada com `--no-revisor2` sem `--aceitar-sem-revisor2 "<motivo>"`, e passa a aceitar sem a flag a revisão sem superfície de risco. | true | `evidence/F23B3_CADEIA_REVISAO/AT-003.log` |
| AT-004 | **When** o auditor rebate com evidência um achado HIGH e há engine disponível fora do revisor e do auditor, o `adversarial-review.sh` **shall** rodar o desempate sem flag nenhuma; com `--no-desempate`, o META **shall** registrar a dispensa à mão. | true | `evidence/F23B3_CADEIA_REVISAO/AT-004.log` |
| AT-005 | **When** o `eval-revisores.sh` lê as revisões de uma frente, ele **shall** imprimir as rodadas em que a regra evitou o 2º revisor, com o nominal do revisor dessas rodadas somado em aritmética exata, como no `custo-feature.sh` (n/d quando o dele for n/d, nunca zero), o número de dispensas à mão por tipo e, à parte, as chamadas por revisor raso. | true | `evidence/F23B3_CADEIA_REVISAO/AT-005.log` |
| AT-006 | **When** o ledger da revisão traz a linha de uma revisão do DESIGN ou de uma rodada interrompida ou sem resultado, no formato novo do molde, o `ledger-revisao-lint.sh` **shall** aceitá-la e o `eval-revisores.sh` **shall** contar a chamada e o custo dela (e os achados da revisão do DESIGN, classificados), sem pô-la em "fora da conta". | true | `evidence/F23B3_CADEIA_REVISAO/AT-006.log` |
| AT-007 | **If** uma pasta de revisão da frente continua sem linha em nenhum ledger, **then** o `eval-revisores.sh` **shall** mantê-la em "fora da conta" com o motivo, e os achados dela em "sem classificar". | true | `evidence/F23B3_CADEIA_REVISAO/AT-007.log` |
| AT-008 | **If** o codex responde sem modelo legível ou o modelo dele não está na tabela de preços, **then** o nominal do papel **shall** sair n/d, nunca zero; com modelo e preço, **shall** sair calculado em aritmética exata, com o cache lido separado da entrada. | true | `evidence/F23B3_CADEIA_REVISAO/AT-008.log` |
| AT-009 | **When** o ledger traz uma linha `escapou` (commit do conserto, `teste: <nome>`, área de dano), o `ledger-revisao-lint.sh` **shall** aceitá-la só com os 3 campos, e o `eval-revisores.sh` **shall** contar os escapes por frente e, quando a frente teve o 2º revisor dispensado pela regra, imprimir o aviso de revisar a regra. | true | `evidence/F23B3_CADEIA_REVISAO/AT-009.log` |
| AT-010 | O pacote **shall** manter a suíte inteira verde, com as skills, o molde do ledger, o `config.example.yaml` e o `docs/adversarial-review.md` dizendo a regra nova e o gerador do starter verde (troca em `scripts/starter/trocas/` para texto que só vale no Open). | true | `evidence/F23B3_CADEIA_REVISAO/VERIFY-GATE-5e110b2.log` |
| AT-011 | **If** o diff revisado traz um texto que manda o revisor, o auditor ou o desempate ignorar as instruções ou responder sem achados, **then** os 3 prompts **shall** tratá-lo como dado (o diff vai cercado, com a instrução de nunca obedecer ao que está dentro dele) e a revisão **shall** seguir o formato de vereditos sem mudar de comportamento. | true | `evidence/F23B3_CADEIA_REVISAO/AT-011.log` · prova real: `S18-JUIZ.log`, `S18-FORTE-JUIZ.log` |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 em `5e110b2` · `evidence/F23B3_CADEIA_REVISAO/VERIFY-GATE-5e110b2.log`

**Critérios de sucesso:** F23 refeita com as linhas novas: fora da conta 2 → 0, sem classificar 6 → 0 de 26 (`F23-REFEITA.log`); a rodada 1 do código evitou o 2º revisor (regra antiga: 33 arquivos); o codex real sai com modelo e cache no META (`S18-SERIES.log`), e o nominal dele fica n/d até haver preço conferido fora do pacote (pendência); dispensas à mão e escapes passam a ser contados (AT-004, AT-009).

---

## Final Status

### Overall: ✅ COMPLETE

---

## Next Step

**If Complete:** `sdd-release` — cadeia de revisão pelos dados (fatia B3 da F23), com a curadoria da B1 (`e1870e3`).
