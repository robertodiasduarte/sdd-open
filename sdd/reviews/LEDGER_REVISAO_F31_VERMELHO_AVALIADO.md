# Ledger da revisão — F31_VERMELHO_AVALIADO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Revisão do DESIGN: dispensável (`sdd-fluxo.sh review-design`: 1 arquivo novo, sem superfície de segurança).

Revisão do código, rodada 1 (`27e42dc`, base `origin/main`): revisor `codex` (`gpt-6.1-sol`), auditor `claude`
(`claude-opus-5-5`); `diversidade: vendor`; US$ 0,32. Nenhum achado.

revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 9 arquivos (limiar 8))
sem achados: rodada=1 EXTERNAL_REVIEW_20261125-153341

Revisão do código, rodada 2 (base `origin/main`, depois dos consertos do avaliador, ciclo 1): revisor `codex`
(`gpt-6.1-sol`), auditor `claude` (`claude-opus-5-5`); `diversidade: vendor`; US$ 0,31.

revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 9 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_EVIDENCIA | rodada=2 | `imprimir_avisos` (`sdd/bin/report-lint.py`, fora do diff) não repete aviso igual; medido: 2 logs zerados em 2 tabelas dão 2 avisos, um por log (`evidence/F31_VERMELHO_AVALIADO/R1-duas-tabelas.log`) | nao | EXTERNAL_REVIEW_20261125-155001 |

Revisão do código, rodada 3 (depois do avaliador, ciclo 2; o commit saiu sem o conserto dos testes de versão): revisor `codex`
(`gpt-6.1-sol`), auditor `claude` (`claude-opus-5-5`); `diversidade: vendor`; US$ 0,31.

revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 9 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | os 7 testes com a versão fixa foram atualizados no commit seguinte; 7 de 7 verdes | nao | EXTERNAL_REVIEW_20261125-160822 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=3 | `imprimir_avisos` não repete aviso igual; agora com teste: `test_mesmo_at_em_duas_tabelas_da_um_aviso_por_log` (verde sem mudar o lint) | nao | EXTERNAL_REVIEW_20261125-160822 |

Revisão do código, rodada 4 (16 arquivos): revisor `codex` (`gpt-6.1-sol`), auditor `claude` (`claude-opus-5-5`);
`diversidade: vendor`; US$ 0,31. Nenhum achado.

revisor2: dispensado rodada=4 — sem superfície de risco (regra antiga: 16 arquivos (limiar 8))
sem achados: rodada=4 EXTERNAL_REVIEW_20261125-161052
