# Ledger da revisão — F23B3_CADEIA_REVISAO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Gravado em
> `sdd/reviews/LEDGER_REVISAO_{FEATURE}.md` logo depois de cada rodada (passo 5c da `sdd-build`).
> Conferido por `bash sdd/bin/ledger-revisao-lint.sh`; lido por `bash sdd/bin/sdd-fluxo.sh loop --ledger`
> (as 4 primeiras células) e por `bash sdd/bin/eval-revisores.sh` (todas). Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Cadeia desta frente (decisão do Roberto, 2026-11-16): claude revisa; codex audita, com o modelo da OpenRouter de reserva
(`--auditor codex,openrouter`). O 2º revisor segue a regra desta própria fatia: só com superfície de risco.

Revisão do DESIGN, rodada D1 (`EXTERNAL_REVIEW_20261116-115325`, `--paths` DEFINE + DESIGN): claude US$ 0,7430 nominal,
codex sem estouro. Gravada aqui no formato que a F23B3 cria (as mesmas notas estão no Advisor Ledger do DESIGN).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=D1 | DESIGN Decision 2 e Pattern 1: termos em português e gerais (decisão do Roberto) | nao | EXTERNAL_REVIEW_20261116-115325 |
| R2 | MED | APLICADA | rodada=D1 | DESIGN Decision 8 e Pattern 3: uma marca por chamada | nao | EXTERNAL_REVIEW_20261116-115325 |
| R3 | MED | APLICADA | rodada=D1 | DESIGN Decision 7: cache criado > 0 sai n/d | nao | EXTERNAL_REVIEW_20261116-115325 |
| R4 | LOW | APLICADA | rodada=D1 | DESIGN Decision 7: entrada sem o cache no adaptador | nao | EXTERNAL_REVIEW_20261116-115325 |
| R5 | LOW | REBATIDA_ESCOPO | rodada=D1 | decisão do Roberto: token fica (num app com login é credencial) | nao | EXTERNAL_REVIEW_20261116-115325 |
| N1 | MED | APLICADA | rodada=D1 | DESIGN Decision 6: aviso de escape também em frente pequena | nao | EXTERNAL_REVIEW_20261116-115325 |

Rodada 1 do código (diff `origin/main..3930f69`, 33 arquivos, 156 KB): claude US$ 3,7263 nominal (assinatura), codex
audita sem estouro; o auditor concordou com R1, rebateu R2 com o DESIGN, pediu prova em R3 e R4 e trouxe N1. 4 dos 5
testes novos caem no código de `3930f69` (`evidence/F23B3_CADEIA_REVISAO/REVISAO-R1-VERMELHO.log`); o do R3 passa nele,
como esperado: R3 era teste fraco, não defeito (o `loop` já lia a linha D1; ele só conta linha HIGH, e o teste antigo não
provava nada). `sdd-fluxo.sh loop --rodada 1`: PRONTO.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 33 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=1 | teste: `test_r1_revisao_do_design_sem_achados` · `sem achados:` aceita rodada=D<n> no lint, no eval e no custo-feature; a revisão do DESIGN sem achados saía em "fora da conta" (com aviso, não calada) | nao | EXTERNAL_REVIEW_20261116-155004 |
| R2 | LOW | APLICADA | rodada=1 | teste: `test_r2_o_meta_grava_o_termo_ou_glob_que_casou` · campo `gatilho_risco_motivo` (termo ou glob), sem mudar o texto que o `--conferir` lê | nao | EXTERNAL_REVIEW_20261116-155004 |
| R3 | LOW | APLICADA | rodada=1 | teste: `test_loop_aceita_rodada_d1` · compara ledger com e sem a linha D1 (graves_abertos 0 × 1) | nao | EXTERNAL_REVIEW_20261116-155004 |
| R4 | LOW | APLICADA | rodada=1 | teste: `test_r4_caminho_em_nfd_casa_o_termo_acentuado` · NFC antes de casar, nas 2 cópias | nao | EXTERNAL_REVIEW_20261116-155004 |
| N1 | MED | APLICADA | rodada=1 | teste: `test_n1_custo_incerto_na_rodada_evitada_vira_mais_nd` · o custo evitado com `US$ x + $?` mostrava só x, como se fosse o custo inteiro | sim | EXTERNAL_REVIEW_20261116-155004 |

Rodada 2 do código, a revisão curta da release (diff `origin/main..cfc87f9`): claude US$ 3,6821 nominal, codex audita sem
estouro e concorda com R1 a R3; trouxe N1. Junto, o raio de impacto da release (3 agentes em contexto novo) achou 2
consumidores quebrados e 1 doc: o `review-design` deixava de exigir revisão para camelCase (`AuthProvider.tsx`,
`resetPassword.ts`), o gate offline lia o `~/.codex/config.toml` real (2 falhas na máquina de quem usa o codex), a linha
"revisão" do `custo-feature.sh` perdia o cache nos tokens, e o `docs/pt-BR/adversarial-review.md` descrevia a regra antiga.
Todos consertados no mesmo commit, com teste (`evidence/F23B3_CADEIA_REVISAO/RAIO-E-RODADA2-VERMELHO.log`: 19 vermelhos
antes do conserto).

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 33 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_r1_rodada2_a_marca_e_a_ultima_linha_do_prompt` · `montar()` põe a marca depois do material, como os prompts dizem | nao | EXTERNAL_REVIEW_20261116-171549 |
| R2 | LOW | APLICADA | rodada=2 | teste: `test_r2_rodada2_o_desempate_v2_tem_verificacao` · `<verification>` no prompt v2 do desempate | nao | EXTERNAL_REVIEW_20261116-171549 |
| R3 | LOW | APLICADA | rodada=2 | teste: `test_r3_rodada2_sem_resultado_com_travessao_colado_entra_no_custo` · a regex do `custo-feature.sh` aceita o travessão colado, como a do lint | sim | EXTERNAL_REVIEW_20261116-171549 |
| N1 | MED | APLICADA | rodada=2 | teste: `test_n1_rodada2_dispensado_a_mao_nao_conta_como_chamado_por_risco` · a tabela por frente contava chamada que não aconteceu | sim | EXTERNAL_REVIEW_20261116-171549 |

Rodada 3 do código (diff `origin/main..7c1860f`, 36 arquivos): claude US$ 4,2703 nominal, codex audita sem estouro;
concordou com R1, pediu prova em R2, trouxe N1. Teto do método (3 rodadas) atingido nesta rodada.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 36 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=3 | `unittest.main()` movido para o fim de `tests/test_f23b3_revisao.py` (rodado direto, o módulo omitia a classe `Raio`); conferido com `python3 -B tests/test_f23b3_revisao.py` | nao | EXTERNAL_REVIEW_20261116-180430 |
| R2 | LOW | REBATIDA_EVIDENCIA | rodada=3 | `sdd/bin/custo-feature.sh:202-211`: `tabela_precos()` devolve `{(engine, modelo): (Decimal, Decimal)}`, a forma que `nominal_estimado()` lê | nao | EXTERNAL_REVIEW_20261116-180430 |
| N1 | MED | APLICADA | rodada=3 | teste: `test_n1_rodada3_sem_engine_disponivel_nao_conta_como_chamado` · conta só com engine escolhida (falha conta, `indisponível` não) | sim | EXTERNAL_REVIEW_20261116-180430 |
