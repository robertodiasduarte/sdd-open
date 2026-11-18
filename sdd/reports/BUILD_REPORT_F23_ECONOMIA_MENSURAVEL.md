# BUILD REPORT: F23 Economia mensurável — fatia B1 (custo por fase e por feature)

> As skills de fase marcam início e fim no trace da feature; um leitor por agente devolve só os números das sessões
> locais; o `custo-feature.sh` soma por fase, revisão e total, em decimal, com n/d onde falta leitura, e produz a linha
> de base das frentes anteriores.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Date** | 2026-11-16 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F23_ECONOMIA_MENSURAVEL.md](../features/DEFINE_F23_ECONOMIA_MENSURAVEL.md) (v1.1) |
| **DESIGN** | [DESIGN_F23_ECONOMIA_MENSURAVEL.md](../features/DESIGN_F23_ECONOMIA_MENSURAVEL.md) (v1.1) |
| **Status** | Complete — Verify Gate verde em `ef217b9`; CI do PR #34 verde (18 de 18 jobs, run 43851918816) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 18/18 linhas do manifest, mais a troca do starter (`scripts/starter/trocas/sdd-brainstorm.md`) e os testes de versão de frentes anteriores |
| **Files Created** | 7 de código e doc (`marca-fase.sh`, `custo-feature.sh`, `sessao-claude.py`, `sessao-codex.py`, `precos-cache.tsv`, `MARCA_FASE.md`, `test_f23_custo.py`) e 12 de fixture |
| **Lines of Code** | ver `git diff --stat 8f944fc..HEAD` |
| **Build Time** | 2026-11-15 23:00 a 2026-11-16 05:10 |
| **Tests Passing** | Verify Gate exit 0 em `ef217b9`: 2.315 testes em 31 min, 3 pulados (`evidence/F23_ECONOMIA_MENSURAVEL/VERIFY-GATE-ef217b9.log`); partida: 2.277 na `v2.17.0`; `test_f23_custo.py` com 35 testes; CI do PR #34 verde em `ef217b9` (Ubuntu, piso do macOS e Windows) |
| **Agents Used** | 0 especialistas (build direto) |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 18 linhas de manifest, acopladas: o contador chama os leitores e lê o trace que a marca grava; os testes usam os quatro |
| Recomendação | default — um autor lembra os formatos entre os quatro scripts |
| Decisão do usuário | default, 2026-11-15 (pedido do Roberto: "execute o pipeline até o release") |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-15 sobre `8f944fc`, por superfície: jsonl, Decimal, precos,
MANIFEST, Windows, gerar-starter, starter, SKILL.md, versão, trace, META, ledger, UTF-8, fixture, exit 0, CRLF, python3,
git archive, sessão, review, skill, tsv, heredoc, bash.

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate que confere fiação | LM-001 | ✔ tratado | os testes executam os scripts com fixtures dos dois lados; mutante do agrupamento derrubado (`MUTANTE-AGRUPAR.log`) |
| asserção sem baseline | LM-002 | ✔ tratado | `BASELINE-VERMELHO.log` (33 falhas na árvore de `8f944fc`) e `REVISAO-R1-R5-VERMELHO.log` (5 de 5 vermelhos em `c32f48d`) |
| review do vazio | LM-003 | ✔ tratado | commit antes de cada rodada; o diff da revisão bate com `git diff --stat` mais os 3 documentos SDD |
| `git archive` | LM-006 | ✔ tratado | marca e contador caem para a pasta atual sem `.git`; o gate roda de `git archive HEAD` |
| 11 dígitos, `/Users/` no pacote | LM-012 | ✔ tratado — **mordeu** | o 1º gate (`67b002b`) ficou vermelho no publish-gate: `0,30000000000000004` num docstring e `/Users/x/…` nas fixtures; corrigido em `c32f48d` |
| `text=True` | LM-014 | ✔ tratado | os testes usam o `roda` do `apoio` |
| saída do Python | LM-015 | ✔ tratado | os 2 leitores e o Python embutido fazem `reconfigure` no início |
| fallback silencioso | LM-017 | ✔ tratado | leitor que falha vira `FALHOU` e n/d (R3 da revisão), com teste |
| `bash` do WSL | LM-029 | ✔ tratado | o contador chama os leitores por `sys.executable` |
| executor que mascara | LM-030 | ✔ tratado | `Sandbox` sem `PYTHONIOENCODING` |
| teto por sinal, PATH restrito, migration | LM-016, LM-034, LM-004 | N.A. | sem teto, sem PATH restrito, sem banco |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Sempre
sup: `starter` `gerar-starter` `sdd/bin` `trocas`
regra: Texto novo numa skill que o starter gera (a lista de `scripts/starter/lista.txt`) e que cita `sdd/bin/…` ou um fragmento de `sdd/templates/` derruba o gerador do starter ("o lint do init achou N citação(ões) a arquivo que só o init cria") e, com ele, 30 testes da suíte; na F23 isso só apareceu no 2º gate. **Do instead:** ao mexer numa skill da lista, rode `python3 -B -m unittest test_gerar_starter` antes do gate inteiro e, se o texto só vale com o `init` do Open, tire-o do starter por uma troca em `scripts/starter/trocas/<skill>.md`.
evidencia: sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/VERIFY-GATE-c32f48d.log
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Sempre
sup: `usage` `message.id` `cache_read_input_tokens` `token_count` `custo`
regra: Somar o `usage` do registro local do agente linha a linha infla o custo: o Claude Code grava uma linha por bloco de conteúdo e repete o `usage` da mesma mensagem (na F22, 1.064 linhas para 472 mensagens, até 13 repetições), e o Codex informa total acumulado, que se repete. **Do instead:** agrupe por `message.id` (maior valor de cada campo) no Claude e use a diferença entre totais consecutivos no Codex; o cache lido e o criado têm preço próprio (o criado, na validade que o agente usa).
evidencia: sdd/reports/evidence/F23_ECONOMIA_MENSURAVEL/MUTANTE-AGRUPAR.log
ficha: —
mordeu_antes: —
>>>
```

---

## Drift detectado

| # | Onde | O que divergiu do DESIGN | Decisão | Ação |
|---|---|---|---|---|
| 1 | `scripts/starter/trocas/sdd-brainstorm.md` | o manifest não previa troca do starter; o gerador recusa a marca na skill do starter | desvio aprovado (o DESIGN já dizia "regenerar o starter" e "nada direto no starter") | troca que tira o parágrafo da marca do starter |
| 2 | `.agents/skills/sdd-{build,define,design}/web/MODO_WEB.md`, `sdd-release/references/MODO_INICIANTE.md`, 8 testes de versão | o manifest não listava os arquivos de modo nem os testes que fixam a versão das skills | desvio aprovado (consequência do bump de versão) | versão nova nos 4 arquivos de modo e nos testes |

Varredura de prompt: `LLM Prompts: false`; nenhum arquivo do manifest é prompt de produção.

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `sdd/bin/marca-fase.sh` | 64 | (direct) | ✅ | AT-001; recusa controle por padrão + contagem de quebras |
| `sdd/bin/adapters/sessao-claude.py` | ~160 | (direct) | ✅ | AT-002; agrupa por `message.id`; subagentes; `realpath` |
| `sdd/bin/adapters/sessao-codex.py` | ~150 | (direct) | ✅ | AT-002, AT-006; diferença de totais; filtro de `cwd` |
| `sdd/bin/custo-feature.sh` | ~560 | (direct) | ✅ | AT-003 a AT-008 |
| `sdd/review/precos-cache.tsv` | 12 | (direct) | ✅ | só o cabeçalho (vendor-agnóstico) |
| `sdd/templates/fragments/MARCA_FASE.md` | 40 | (direct) | ✅ | dono único do porquê |
| `tests/test_f23_custo.py` | ~430 | (direct) | ✅ | 25 testes |
| `sdd/fixtures/custo/` (12 arquivos) | — | (direct) | ✅ | dados inventados; README |

---

## Verification Results

### Lint · Typecheck

N/A — o Open não tem `sdd/config.yaml` com `project.lint_cmd` nem `typecheck_cmd`; os lints do pacote rodaram à mão:
`skill-lint.py` nas 6 skills (✅), `check-versions.py` (PASS, 22 skills), `design-lint.py` no DESIGN (✅),
`ledger-revisao-lint.sh` no ledger (VERDE).

### Testes

```text
$ bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F23_ECONOMIA_MENSURAVEL.md   # HEAD ef217b9
Ran 2315 tests in 1888.976s
OK (skipped=3)
RESULTADO: VERDE
```

Gates anteriores, vermelhos e corrigidos: `67b002b` (publish-gate, LM-012), `c32f48d` (37 falhas: 30 do gerador do starter e a guarda da LM-015, achadas até a interrupção), `f5e2e31` (2 falhas da guarda da LM-015), `6b3a295`, `e451071` e `b606eca` (interrompidos: a revisão mudou o código antes do fim); `b494810` verde (2.311). CI do PR: vermelho em `b494810` só no Windows (quebra de linha em argumento não chega lá; teste separado em `b606eca`), verde em `ef217b9`.

**Status:** ✅ 2.315 Pass | 0 Fail

---

## Advisor Ledger

**Consulta:** delivery-review · 2026-11-15/16 · `sdd/bin/adversarial-review.sh` (pastas em `sdd/reports/reviews/`)
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F23_ECONOMIA_MENSURAVEL.md`
**Proveniência:** revisor claude (claude-opus-5-5, assinatura); auditor openrouter qwen/qwen3.7-plus; sem 2º revisor e
sem desempate (`--no-revisor2 --no-desempate`, como F16W2 e F22). Revisão do DESIGN: 1 rodada, no Advisor Ledger do DESIGN.

| Rodada | Pasta | Achados | Decisão |
|---|---|---|---|
| DESIGN 1 | `EXTERNAL_REVIEW_20261115-233040` | 6 (1 HIGH) | 5 aplicados, 1 rebatido com evidência (Advisor Ledger do DESIGN) |
| código 1 | `EXTERNAL_REVIEW_20261115-234206` | 5 (1 HIGH), sem auditor (qwen passou do teto de tempo) | 5 aplicados com teste (`822d170`) |
| código 2 | `EXTERNAL_REVIEW_20261116-004226` | 6 | 4 aplicados (`e451071`), 2 rebatidos com evidência |
| código 3 (teto) | `EXTERNAL_REVIEW_20261116-005125` | 4 + 1 do auditor | 3 aplicados (`b494810`), 1 por escopo, 1 rebatido com evidência |
| código 4 (acima do teto, OK do Roberto) | `EXTERNAL_REVIEW_20261116-072338` | 3, sem auditor (qwen passou do teto de novo) | 3 aplicados (`ef217b9`); uma 1ª tentativa sobre `b494810` foi interrompida antes de qualquer veredito |
| código 5 (acima do teto, OK do Roberto) | `EXTERNAL_REVIEW_20261116-075121` | 2 + 1 do auditor (codex) | 3 por escopo, pendências na ficha; nenhuma mudança depois |

`--conferir` CONFERE em `ef217b9` (`EXTERNAL_REVIEW_20261116-075121`), com o 2º revisor dispensado pelo Roberto (cadeia combinada
para o Open, como na F16W2 e na F22). Custo das rodadas: claude por assinatura (~US$ 8,2 nominal nas 6 do código e do DESIGN);
qwen ~US$ 0,09 pagos; codex por assinatura.

---

## Segurança

| Item | Decisão | Motivo |
|---|---|---|
| nenhum | — | S17 aplicado (AT-001, AT-002); S10 já atendido pelo AT-002; nenhum recusado ou adiado |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | publish-gate vermelho no 1º gate (LM-012: número longo e `/Users/` nas fixtures) | fixtures e docstring trocados (`c32f48d`) | +30 min (um gate) |
| 2 | 30 falhas do gerador do starter (a marca citava `sdd/bin` na `sdd-brainstorm` do starter) | troca do starter (`f5e2e31`) | +30 min |
| 3 | o auditor (qwen) passou do teto de tempo na rodada 1 da revisão do código | os 5 achados conferidos à mão, com teste; rodada 2 com auditor | +15 min |
| 4 | o script de revisão leva os não rastreados para o diff (ESCOPO com tabela privada) | `.gitignore` local que ignora a si mesmo em `sdd/handoffs`, `sdd/reviews`, `sdd/reports/evidence` e para o ESCOPO | — |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| leitores de sessão em `.py` em vez de `.sh` | Decision 2 do DESIGN | nomes do DEFINE corrigidos na v1.1 |
| n/d em toda linha da janela quando há registro ilegível ou leitor que falha | R2 e R3 da revisão do código: não se sabe a que fase a parte perdida pertencia | o relatório fica parcial em vez de subestimar |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (scripts do método e o texto das skills; o Open não tem `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** N.A. (1 camada) — os ATs foram provados por execução: um log por AT (`evidence/F23_ECONOMIA_MENSURAVEL/AT-nnn.log`) sobre `ef217b9`

---

## Acceptance Test Verification

| ID | Critério (EARS, verbatim do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | **When** uma skill de fase chama `sdd/bin/marca-fase.sh inicio <fase> <FEATURE>` e depois `… fim <fase> <FEATURE>`, the system **shall** acrescentar uma linha por chamada (evento, fase, feature, horário UTC em ISO 8601) ao arquivo de marcas da feature, sem apagar as linhas anteriores; **If** a fase ou a feature trouxer tabulação, quebra de linha ou outro caractere de controle, **then** o script **shall** recusar com exit 64 sem gravar nada | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-001.log` |
| AT-002 | The leitores de sessão `sdd/bin/adapters/sessao-claude.py` e `sessao-codex.py` **shall** devolver, por mensagem do agente (sessão principal e subagentes), só horário, modelo e tokens de entrada, saída, cache criado e cache lido — nenhum texto de conversa, caminho de arquivo ou argumento de ferramenta (fixture com texto, caminho e segredo fictício: 0 ocorrências na saída); um nome de modelo fora de `[A-Za-z0-9._:/@-]{1,80}` (com `|`, quebra de linha ou controle) **shall** sair como `?`, para não forjar linha no relatório | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-002.log` |
| AT-003 | **When** `sdd/bin/custo-feature.sh <FEATURE>` roda sobre marcas e sessões, the system **shall** gravar `sdd/reports/CUSTO_<FEATURE>.md` com uma linha por fase (execuções, tokens, pago, nominal, tempo ativo), uma linha `sem fase` para o trecho fora de qualquer par de marcas, uma linha `revisão` e o total, batendo com a conta à mão da fixture; as somas **shall** ser exatas (decimal, nunca ponto flutuante) e arredondadas só na hora de imprimir | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-003.log` |
| AT-004 | **If** o registro de uma sessão não é legível (arquivo ausente, linha JSON quebrada, agente sem adaptador) ou o modelo não tem preço, **then** the system **shall** mostrar `n/d` naquela célula, somar o total como `US$ x + n/d` e nunca contar o valor como 0 | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-004.log` |
| AT-005 | The contador **shall** precificar tokens de cache lido e cache criado pelo preço de cache do modelo, separado do preço de entrada; **If** o modelo não tem preço de cache, **then** a parte de cache **shall** sair `n/d` em vez de cobrada como entrada | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-005.log` |
| AT-006 | **If** uma chamada da revisão adversarial também deixar sessão no registro local, **then** the system **shall** contar o custo dessa chamada uma vez só (pela linha `revisão`, lida dos META.txt) | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-006.log` |
| AT-007 | **While** uma sessão cobre várias fases, the system **shall** atribuir cada mensagem à fase cujo par início/fim contém o horário dela, e uma fase aberta sem `fim` **shall** fechar no horário da marca seguinte ou no fim da sessão, com o aviso `fase sem fim` | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-007.log` |
| AT-008 | **When** `custo-feature.sh --linha-de-base <mapa>` roda com um mapa feature → pastas de sessão e ledgers, the system **shall** imprimir uma linha por feature com custo nominal (ou n/d), rodadas de revisão e achados com dano, sem dividir por fase | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-008.log` |
| AT-009 | The skills de fase (`sdd-brainstorm`, `sdd-define`, `sdd-ux-review`, `sdd-design`, `sdd-build`, `sdd-release`) **shall** mandar chamar `marca-fase.sh` no início e no fim, e o starter gerado **shall** sair por `scripts/gerar-starter.py` sem edição à mão | true | `evidence/F23_ECONOMIA_MENSURAVEL/AT-009.log` |
| AT-010 | The system **shall continue to** aceitar o `precos.tsv` de 6 colunas e o formato atual dos META.txt e ledgers: `eval-revisores.sh`, `adversarial-review.sh`, `adversarial-review-gate.sh` e toda a suíte passam como hoje, no macOS e no Windows | true | `evidence/F23_ECONOMIA_MENSURAVEL/VERIFY-GATE-ef217b9.log` |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 em `ef217b9` · `evidence/F23_ECONOMIA_MENSURAVEL/VERIFY-GATE-ef217b9.log`

**Linha de base (critério de sucesso 3):** `evidence/F23_ECONOMIA_MENSURAVEL/linha-de-base/LINHA-DE-BASE.log` — 24
linhas (W0_M1, F4 a F22), 21 com custo nominal das sessões (US$ 15,39 a US$ 182,65 por frente); F11, F16W2 e F19 ficam
n/d porque as sessões delas estão na pasta de outra frente. Revisão: só a F12 tem META guardado (US$ 13,20 + n/d). Tarifas
em `linha-de-base/precos/`, fora do pacote, da referência oficial (cache de 2026-11-03); o cache criado com validade de
1 hora (2× a entrada), a que o Claude Code usa.

---

## Final Status

### Overall: ✅ COMPLETE

---

## Next Step

**If Complete:** `sdd-release` — custo por fase e por feature (fatia B1 da F23), minor `v2.18.0`; starter regenerado.
