# BUILD REPORT: F24 Release enxuta — a parte depois do push

> A `sdd-release` só colhe e põe a colheita numa fila versionada; o lote da `sdd-playbook` julga depois, com as mesmas
> garantias. Depois do OK, um commit de papel só, sem pergunta além do smoke vermelho; a ficha cresce por acréscimo
> (bloco Publicado gerado do ledger); a trilha curta é decidida por comando; o aluno ouve, uma frase por etapa, o que é
> cada passo depois do push.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F24_RELEASE_ENXUTA |
| **Date** | 2026-11-16 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F24_RELEASE_ENXUTA.md](../features/DEFINE_F24_RELEASE_ENXUTA.md) (v1.4) |
| **DESIGN** | [DESIGN_F24_RELEASE_ENXUTA.md](../features/DESIGN_F24_RELEASE_ENXUTA.md) (v1.1) |
| **Status** | ✅ Complete — Verify Gate verde em `017f09a`; publicado na `v2.20.0` |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 25/25 linhas do manifest, mais a troca do starter (`scripts/starter/trocas/sdd-handoff.md` e `_moldes/HANDOFF_TEMPLATE.md`), a linha de versão do `MODO_INICIANTE.md` e os testes de versão de frentes anteriores |
| **Files Created** | 5 de código e doc (`ficha-publicado.py`, `trilha.sh`, `push-de-papel.py`, `lote.md`, `test_f24_release_enxuta.py`) e 13 de fixture |
| **Lines of Code** | ver `git diff --stat ef217b9..HEAD` |
| **Build Time** | 2026-11-16 22:20 a 2026-11-17 (com 5 rodadas de revisão do código) |
| **Tests Passing** | 2.435 de 2.435 (3 pulados) no Verify Gate em `017f09a`; 71 no módulo da F24; CI do PR #36 18 de 18 |
| **Agents Used** | 0 especialistas (build direto) |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 25 linhas de manifest, acopladas: a release chama os modos novos do curador, o lote usa os mesmos, e os testes de texto da F14 mudaram de lugar junto com o procedimento |
| Recomendação | default — um autor lembra os nomes entre skill, script e teste |
| Decisão do usuário | default, 2026-11-16 (pedido do Roberto: "execute o pipeline até o release. use o default para respostas") |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-16 sobre `ef217b9`, pelas superfícies do manifest (as do DESIGN
e mais `starter`, `gerar-starter`, `quotePath`, `ledger`), refeita sobre `fb7ee82` depois do rebase na F23B3 (o
playbook ganhou a LM-035 a LM-038 na curadoria dela).

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate que confere fiação | LM-001 | ✔ tratado | os scripts rodam com fixtures dos dois lados; mutante sem a proveniência derrubado (`MUTANTE-PROVENIENCIA.log`) |
| asserção sem baseline | LM-002 | ✔ tratado | o `cmd` chama o módulo da F24 pelo nome (vermelho na `main`); 8 testes da revisão vermelhos em `45bf1fe` (`REVISAO1-VERMELHO.log`) |
| número longo no pacote | LM-012 | ✔ tratado | nome de entrada `AAAAMMDDTHHMMSSZ`; SHA curto; publish-gate verde no gate |
| teste apagado por corte | LM-013 | ✔ tratado | `test_f14_textos.py`: 38 `def test_` antes e depois da troca do recorte |
| `subprocess` e saída no Windows | LM-014, LM-015 | ✔ tratado | `encoding="utf-8"` em todo `subprocess`; `reconfigure` em `ficha-publicado.py` e `push-de-papel.py` |
| fallback silencioso | LM-017 | ✔ tratado | `push-de-papel.py` sem o vizinho sai 64, nunca `NAO_PUBLICA` (`test_sem_o_vizinho_e_uso_nunca_nao_publica`) |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | os logs de evidência são gravados por `bash`, com `rc=$?` |
| `ls a b` | LM-025 | ✔ tratado | `trilha.sh` testa cada DEFINE com `[ -f ]` |
| teste de texto que deixa passar a obrigação em prosa | LM-026 | ✔ tratado | a parada única procura as frases de oferta, não só a marca `[D` |
| `bash` do WSL, executor que mascara | LM-029, LM-030 | ✔ tratado | o curador refaz a colheita por função; os testes usam o `apoio` |
| skill do starter que cita `sdd/bin/` | LM-035 | mordeu | a `sdd-handoff` e o molde da ficha citaram `sdd/bin/ficha-publicado.py`, e o gerador do starter recusou (24 testes de `test_gerar_starter`); conserto por troca do starter (`STARTER-LINT.log`) |
| arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | os 18 arquivos novos no `MANIFEST.txt`; publish-gate no gate |
| teto de 500 linhas da `SKILL.md` | LM-038 | ✔ tratado | `sdd-release` com 443 linhas (o 17b saiu) |
| OpenRouter que passa do teto | LM-010 | ✔ tratado | saldo conferido em `/credits` antes das rodadas; o qwen respondeu nas 2 rodadas completas |
| juiz por regex, PATH restrito, migration | LM-028, LM-034, LM-004 | N.A. | sem juiz de LLM, sem PATH restrito, sem banco |

---

## Candidatos ao playbook

Nenhum candidato nesta build. A lição do starter que cita `sdd/bin/` mordeu de novo, mas já virou a LM-035 na
curadoria da F23B3 (publicada na `main` durante esta frente): ela vai como `mordeu` na tabela acima, não como
candidato repetido.

---

## Drift detectado

| # | Onde | O que divergiu do DESIGN | Decisão | Ação |
|---|---|---|---|---|
| 1 | `scripts/starter/trocas/sdd-handoff.md`, `_moldes/HANDOFF_TEMPLATE.md` | o manifest não previa troca do starter; o gerador recusa `sdd/bin/` na `sdd-handoff` e no molde | desvio aprovado (o DESIGN diz "nada direto no starter") | trocas que dizem, no starter, "o que foi publicado vai uma vez só, na seção Publicado" |
| 2 | `references/MODO_INICIANTE.md` e 6 testes de versão | a linha de identificação do modo segue a versão da skill; os testes fixam versões | desvio aprovado (consequência do bump) | só a linha de versão: 2.16.0, porque a F23B3 publicou a 2.15.0 da `sdd-release` durante esta frente |
| 3 | item 11 (Changelog) e 12 (Limpeza) ficaram na FASE 2 | o DESIGN os punha na FASE 3; `test_f15_slots_textos` e `test_f14_drive_textos` recortam o item 10 até o item 11 dentro da FASE 2 | desvio aprovado (a ordem dos passos não muda) | a FASE 3 começa na Colheita |
| 4 | `--self-test` do curador | o manifest pedia casos novos no self-test | desvio aprovado (DESIGN v1.1) | os casos da fila estão em `tests/test_f24_release_enxuta.py` |

Varredura de prompt: `LLM Prompts: false`; nenhum arquivo do manifest é prompt de produção (o brief do curador é
instrução do método).

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `sdd/bin/trilha.sh` | ~140 | (direct) | ✅ | AT-009; conta o não commitado; `core.quotePath=false` |
| `sdd/bin/ficha-publicado.py` | ~190 | (direct) | ✅ | AT-008; idempotente; ledger ilegível ⇒ n/d e exit 2 |
| `.agents/skills/sdd-release/scripts/push-de-papel.py` | ~190 | (direct) | ✅ | AT-006; reusa o parser do `deploy-espera-testes.py` |
| `.agents/skills/sdd-playbook/references/lote.md` | ~140 | (direct) | ✅ | AT-003, AT-004; o 17b mudado de lugar |
| `tests/test_f24_release_enxuta.py` | ~600 | (direct) | ✅ | AT-001 a AT-011 e os 8 testes da revisão |
| `sdd/fixtures/f24/` (13 arquivos) | — | (direct) | ✅ | workflows, ledgers, fichas curtas; README |

---

## Verification Results

### Lint · Typecheck

N/A — o Open não tem `sdd/config.yaml` com `lint_cmd` nem `typecheck_cmd`. Os lints do pacote rodaram à mão:
`skill-lint.py` nas 3 skills mudadas (✅), `check-versions.py` (VERDE), `design-lint.py` no DESIGN (✅),
`ledger-revisao-lint.sh` no ledger da revisão (VERDE), `playbook-curator.sh --self-test` (OK).

### Testes

Verify Gate (o `cmd` do DEFINE, sobre `git archive HEAD`) em `017f09a`: publish-gate em modo `ci` VERDE, módulo da F24
71 OK, suíte inteira 2.435 OK (3 pulados), `RESULTADO: VERDE [exit=0]` —
`sdd/reports/evidence/F24_RELEASE_ENXUTA/VERIFY-GATE-017f09a.log`. Gate anterior, em `60e4839` (antes da rodada 5):
2.427 OK (`VERIFY-GATE-60e4839.log`). Um teste vermelho → verde por achado aplicado em cada rodada
(`REVISAO1-VERMELHO.log` a `REVISAO5-VERMELHO-60e4839.log`, e `REVISAO5-VERDE.log`). Os 11 logs por AT foram refeitos em
`017f09a`, todos com exit 0. CI do PR #36 em `017f09a`: 18 de 18 (Ubuntu, macOS e as 16 fatias do Windows).

---

## Advisor Ledger

**Consulta:** delivery-review · 2026-11-16 · `sdd/bin/adversarial-review.sh` (pastas em `sdd/reports/reviews/`)
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F24_RELEASE_ENXUTA.md`
**Proveniência:** revisor claude (claude-opus-5-5, assinatura); 2º revisor codex (assinatura, gatilho de tamanho);
auditor openrouter qwen/qwen3.7-plus. Revisão do DESIGN: 1 rodada, no Advisor Ledger do DESIGN.

| Rodada | Pasta | Achados | Decisão |
|---|---|---|---|
| DESIGN 1 | `EXTERNAL_REVIEW_20261116-191150` | 6 + 1 do auditor (2 HIGH) | 5 aplicados, 2 rebatidos (Advisor Ledger do DESIGN) |
| código 1 | `EXTERNAL_REVIEW_20261116-193502` | 14 (4 HIGH) | 13 aplicados com teste (`55ca3fc`), 1 rebatido com evidência |
| código 2 | `EXTERNAL_REVIEW_20261116-195427` | — | sem resultado: interrompida pelo rebase sobre a F23B3 |
| código 2 (refeita) | `EXTERNAL_REVIEW_20261116-202240` | 5 | 5 aplicados com teste |
| código 3 | `EXTERNAL_REVIEW_20261116-203629` | 6 | 5 aplicados, 1 rebatido por escopo |
| código 4 | `EXTERNAL_REVIEW_20261116-210442` | 9 (1 HIGH) | 9 aplicados (1 pelo texto do DEFINE, v1.4); o auditor passou do teto: rodada refeita como 4a (acima do teto, OK do Roberto) |
| código 4a | `EXTERNAL_REVIEW_20261116-214955` | 9 (2 HIGH) | 7 aplicados, 2 rebatidos |
| código 5 | `EXTERNAL_REVIEW_20261116-220949` | 10 (3 HIGH) | 8 aplicados com teste em `017f09a`, 1 rebatido com evidência (N1), 1 rebatido por escopo (pendência ✨); sem 6ª rodada, por decisão do Roberto (2026-11-17) |

---

## Segurança

| Item | Decisão | Motivo |
|---|---|---|
| nenhum | — | o Define aplicou S18 (AT-010) e não recusou nem adiou item |

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | 1º Verify Gate vermelho: o `cmd` rodava `tests.test_f24_release_enxuta` da raiz, e o `apoio` mora em `tests/` | `cmd` corrigido no DEFINE (v1.2) | +35 min |
| 2 | gerador do starter recusou `sdd/bin/` na `sdd-handoff` e no molde | trocas do starter (Drift 1); candidato ao playbook | +10 min |
| 3 | colheita só de promoção pendente entupiria a fila (estado do playbook, não da publicação) | não entra na fila; o lote a pergunta pelas entradas com conteúdo | +10 min |
| 4 | a F23B3 chegou à `main` no meio da 2ª rodada da revisão do código | rodada 2 interrompida (`sem resultado` no ledger); rebase sobre `fb7ee82` com 4 conflitos mecânicos (`MANIFEST.txt` e 3 testes de versão); `sdd-release` 2.16.0; LM-035 registrada como `mordeu`; o ledger da revisão no molde novo (`rodada=D1`) | +30 min |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| trilha exclui só os documentos do SDD, não `sdd/` inteiro | `sdd/bin/` é código no próprio Open | registrado no DESIGN v1.1 e no AT-009 |
| Changelog e Limpeza na FASE 2 | testes de frentes anteriores recortam o item 10 até o 11 | nenhum (mesma ordem) |

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (scripts do método e texto das skills; sem `sdd/config.yaml`, nenhuma camada de `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** N.A. (1 camada)
avaliador: N.A. (1 camada)

---

## Acceptance Test Verification

| AT | Critério | Passou | Evidência |
|----|----------|--------|-----------|
| AT-001 | a release só colhe; colheita que falha fica marcada na fila | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-001.log` |
| AT-002 | cada impressão conta uma vez, entre publicações sem lote | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-002.log` |
| AT-003 | lote: curador, conferidor, AUTO e PERGUNTA; IDs seguidos num `--aplicar` só | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-003.log` |
| AT-004 | bloco reprovado e escrita do curador isolam a entrada; evidência ausente por linha; envio com D1 | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-004.log` |
| AT-005 | fila acima de 5 ⇒ 1 linha, sem pergunta | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-005.log` |
| AT-006 | commit de papel único, OK diz se publica (PUBLICA/NAO_PUBLICA/NAO_SEI) | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-006.log` |
| AT-007 | uma parada só depois do OK; branch remota só se ancestral; arquivamento por `estado: shipado` | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-007.log` |
| AT-008 | bloco Publicado gerado do ledger, idempotente; ledger ilegível ⇒ n/d | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-008.log` |
| AT-009 | trilha curta por comando (7 casos); ficha curta ≤ 20 linhas | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-009.log` |
| AT-010 | entrada plantada, mexida ou fabricada é recusada | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-010.log` |
| AT-011 | tabela "Depois do push" × etapas; não-regressão (itens 8 a 10, self-test, suíte, starter) | true | `sdd/reports/evidence/F24_RELEASE_ENXUTA/AT-011.log` |

---

## Final Status

✅ Complete. Verify Gate verde em `017f09a` (2.435 testes); 11 de 11 ATs com evidência; revisão do código em 5 rodadas
(4ª e 5ª acima do teto, com o OK do Roberto), sem 6ª rodada por decisão dele; publicado na `v2.20.0`.

---

## Next Step

**Ready for:** `/sdd-release F24 release enxuta`
