# Ledger da revisão — EXEMPLO (fixture do eval-revisores)

Dados inventados. Os ids são os do arquivo de vereditos de cada rodada: sem rótulo nas rodadas de um revisor só
(o rótulo da engine, quando escrito, tem de ser o de quem revisou), com rótulo na rodada 5, que teve dois. As duas últimas
linhas ficam fora da conta de propósito: rótulo que não é o de quem revisou, e achado que a revisão não tem.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | HIGH | APLICADA | rodada=1 | teste: `test_soma_do_mes` · o total do mês somava o estorno duas vezes | sim | EXTERNAL_REVIEW_20260201-000001 |
| R2 | MED | APLICADA | rodada=1 | mensagem de erro sem a causa | nao | EXTERNAL_REVIEW_20260201-000001 |
| R3 | LOW | REBATIDA_EVIDENCIA | rodada=1 | `src/a.py:10` já trata o caso vazio | nao | EXTERNAL_REVIEW_20260201-000001 |
| R1 | MED | APLICADA | rodada=2 | teste: `test_acesso_negado_sem_perfil` · a rota respondia sem checar o perfil | sim | EXTERNAL_REVIEW_20260201-000002 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=2 | melhoria de nome; fica para outra frente | nao | EXTERNAL_REVIEW_20260201-000002 |
| N1 | HIGH | REBATIDA_EVIDENCIA | rodada=2 | medido: o comando sai 64, não 0 | nao | EXTERNAL_REVIEW_20260201-000002 |
| R1@claude | MED | APLICADA | rodada=3 | texto da ajuda corrigido | nao | EXTERNAL_REVIEW_20260201-000003 |
| N1@openrouter | HIGH | REBATIDA_EVIDENCIA | rodada=3 | o mesmo ponto da rodada 2, repetido; mesma medição | nao | EXTERNAL_REVIEW_20260201-000003 |
| R1@claude | MED | APLICADA | rodada=5 | comentário desatualizado | nao | EXTERNAL_REVIEW_20260201-000005 |
| R2@claude | HIGH | APLICADA | rodada=5 | teste: `test_exporta_sem_dado_de_outro_cliente` · a exportação trazia linhas de outro cliente | sim | EXTERNAL_REVIEW_20260201-000005 |
| R1@codex | HIGH | APLICADA | rodada=5 | teste: `test_publica_so_com_gate_verde` · a publicação seguia com o gate vermelho | sim | EXTERNAL_REVIEW_20260201-000005 |
| R1@codex | LOW | APLICADA | rodada=4 | rótulo errado: na rodada 4 quem revisou foi outra engine | nao | EXTERNAL_REVIEW_20260201-000004 |
| R9@claude | LOW | APLICADA | rodada=5 | linha que aponta um achado que a revisão não tem | nao | EXTERNAL_REVIEW_20260201-000005 |

sem achados: rodada=7 EXTERNAL_REVIEW_20260201-000007
