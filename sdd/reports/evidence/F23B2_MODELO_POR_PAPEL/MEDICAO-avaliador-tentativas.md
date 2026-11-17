# Avaliador — as 3 tentativas da série de referência

Teto da medição: pago US$ 0,00 · nominal US$ 200,00 (pasta inteira, com o curador). Agente: `claude -p` por assinatura,
com caixa de areia. Referência: `claude-opus-5-5`. Nenhum candidato chegou a rodar: a barreira de calibração exige a
referência na meta em todas as repetições, e ela saiu da meta na 1ª execução de cada caso de NEEDS_WORK testado.

| # | Caso | Montagem | Execução | Segundos | Nominal US$ | Resultado |
|---|---|---|---|---:|---:|---|
| 1 | `ava-f11-gate-c1` | caixa de areia sem porta local e sem a pasta temporária; `entrada/` commitada | rep 1 | 647 | 3,3510762 | descartada: o gate do caso sobe stub local; quase tudo NAO_VERIFICADO, e um achado falso do publish-gate (DEFINE/DESIGN no commit) |
| 1 | `ava-f11-gate-c1` | idem | rep 2 (parada à mão) | — | 1,8609540 | interrompida, custo somado |
| 2 | `ava-f11-gate-c1` | porta local e `/var/folders` liberadas; `entrada/` fora do commit (`2c2fd37`) | rep 1 | 1.317 | 4,7371338 | fora da meta: veredito PASS_PENDENTE_RECIBO (esperado NEEDS_WORK), AT-003 dado como aprovado |
| 2 | `ava-f11-gate-c1` | idem | rep 2 (parada à mão) | — | 0,8064068 | interrompida, custo somado |
| 3 | `ava-f21-engenharia-reversa-c1` | idem, `--teto-s 3600` | rep 1 | 2.562 | 2,9737824 | fora da meta: veredito PASS_PENDENTE_RECIBO, AT-006 dado como aprovado |
| 3 | `ava-f21-engenharia-reversa-c1` | idem | rep 2 (parada à mão) | — | 0,5173608 | interrompida, custo somado |

Soma do avaliador: US$ 14,2467140 nominal. Com o curador (US$ 16,10200585): **US$ 30,34871985 nominal, US$ 0 pago**.

## Por que a referência saiu da meta

- **F11 (AT-003):** a falha histórica só apareceu por sabotagem (mutante no leitor de vereditos do auditor que deixava o
  gate verde). A referência, rodada do zero, não fez essa sonda. Caso trocado (`gabarito-descartado/README.md`).
- **F21 (AT-006):** a falha histórica é a dependência citada como "SDD Brainstorm" / "SDD Define" em
  `COMO_FUNCIONA.md:19` e `cases.json:57`; um `grep -rnE "SDD Brainstorm|SDD Define"` a acha. A referência procurou só a
  forma "SDD Brainstorm by RDD" e não achou (`avaliador-referencia/ava-f21-engenharia-reversa-c1-opus-1.txt`, linha
  do AT-006). Conferência rasa do próprio modelo de referência, não defeito da montagem.
- Nas duas, o veredito foi PASS_PENDENTE_RECIBO porque o comando do Verify Gate do caso não fecha dentro da caixa de
  areia (o publish-gate grava em `/tmp`, que segue bloqueado).

## Decisão

Roberto, 2026-11-17: registrar o avaliador como **referência fora da meta**, com o slot vazio, e redesenhar a meta dele
numa próxima fatia (por exemplo, taxa de detecção do AT que falha ao longo das repetições). Nada de mudar a meta depois
de ver os dados.
