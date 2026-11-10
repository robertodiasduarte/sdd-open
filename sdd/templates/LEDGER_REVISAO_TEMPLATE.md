# Ledger da revisão — {FEATURE}

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Gravado em
> `sdd/reviews/LEDGER_REVISAO_{FEATURE}.md` logo depois de cada rodada (passo 5c da `sdd-build`).
> Conferido por `bash sdd/bin/ledger-revisao-lint.sh`; lido por `bash sdd/bin/sdd-fluxo.sh loop --ledger`
> (as 4 primeiras células) e por `bash sdd/bin/eval-revisores.sh` (todas). Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

{Engines de cada papel, quantas rodadas, e o que ficou decidido fora da tabela (dispensa do 2º revisor, teto de rodadas).}

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|

<!--
Como preencher (o lint confere; apague este comentário se quiser):

Uma linha por achado, por exemplo:
  R1 · HIGH · APLICADA · rodada=1 · teste: `test_soma_do_mes` · o total somava o estorno duas vezes · sim · EXTERNAL_REVIEW_20260201-000001

- Este arquivo guarda só o ledger: não ponha outra tabela aqui (o lint confere toda linha de tabela como achado).
  O cabeçalho pode se repetir entre as rodadas; texto corrido entre as tabelas pode.
- 7 células por linha; uma barra vertical dentro de célula se escreve com a barra invertida antes dela.
- achado: copie o id do arquivo de vereditos da rodada (`reviewer.verdicts.jsonl`, `reviewer2.verdicts.jsonl`,
  `auditor.verdicts.jsonl`), como está: `R1` e `N1` numa rodada de um revisor só; `R1@claude`, `R1@codex` quando houve dois.
  Não acrescente rótulo que o arquivo não tem: o `sdd-fluxo.sh loop` casa o id exato.
- rodada: `rodada=<N>`, o mesmo N passado ao `loop --rodada`.
- evidência: arquivo:linha, commit ou medição; com dano = sim, comece por `teste: <nome do teste que falha no código antigo>`.
- dano: `sim` só com veredito APLICADA e o teste citado; senão `nao`. O valor `?` só existe em ledger de frente
  antiga convertido depois, com a linha `retroativo: sim` sozinha acima da tabela.
- revisão: a pasta que o `adversarial-review.sh` imprimiu em `pasta:`, só o nome (EXTERNAL_REVIEW_AAAAMMDD-HHMMSS).
- rodada em que a revisão não achou nada: uma linha fora da tabela, no formato
  sem achados: rodada=<N> EXTERNAL_REVIEW_AAAAMMDD-HHMMSS
- o mesmo achado não se repete na mesma revisão; em revisões diferentes, sim (cada rodada tem os seus ids).
-->
