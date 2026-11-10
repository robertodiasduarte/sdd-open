# Ledger da revisão — fixture do lint (controle.md)

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | HIGH | APLICADA | rodada=1 | teste: `test_soma_do_mes` · o total somava o estorno duas vezes | sim | EXTERNAL_REVIEW_20260201-000001 |
| R3 | LOW | APLICADA | rodada=1 | id sem rótulo, como numa rodada de um revisor só | nao | EXTERNAL_REVIEW_20260201-000001 |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=1 | fora desta frente | nao | EXTERNAL_REVIEW_20260201-000001 |
| N1@openrouter:qwen/q-plus | MED | REBATIDA_EVIDENCIA | rodada=2a | célula com barra escapada: `a \| b` | nao | EXTERNAL_REVIEW_20260201-000002 |

sem achados: rodada=3 EXTERNAL_REVIEW_20260201-000003

```text
Bloco cercado com texto de exemplo, sem linha de tabela: não é conferido.
retroativo: sim
```
