# Cenários de comportamento do modo Define — sdd-desempenho-banco (F27)

Critério escrito antes, em `.agents/skills/sdd-desempenho-banco/evals/cases.json` (casos `sem-banco-na` e
`tabela-nova-supabase`). Cada execução: um agente novo, sem esta conversa, com o mesmo brief (ler SKILL.md,
como-falar.md e o catálogo; ler o DEFINE sintético; escrever só a 1ª resposta ao aluno; não gravar nada). Os DEFINEs
sintéticos: um script local que soma horas de um CSV (sem banco) e a tela "Meus pedidos" com tabela nova no Supabase.
Julgamento: leitura de cada resposta contra o critério (LM-028: não por regex). 2026-11-17.

| Execução | Caso | Critério | Veredito |
|---|---|---|---|
| sem-banco 1 | sem-banco-na | N.A. em 1 linha com motivo · nenhuma pergunta · só a linha Desempenho · nenhuma ficha proposta | aprovado |
| sem-banco 2 | sem-banco-na | idem | aprovado |
| sem-banco 3 | sem-banco-na | idem | aprovado |
| tabela-nova 1 | tabela-nova-supabase | gatilhos banco e lista com o trecho · 1 pergunta de volume aberta com "não sei" · nada decidido nem gravado antes da resposta | aprovado |
| tabela-nova 2 | tabela-nova-supabase | idem | aprovado |
| tabela-nova 3 | tabela-nova-supabase | idem | aprovado |

Resultado: 3 de 3 em cada cenário. Os 3 agentes do cenário com tabela apontaram, sem combinar, a mesma divergência:
o exemplo 1 de `references/como-falar.md` (a pergunta de volume) vinha sem a marca de classe que
`sdd/templates/fragments/PERGUNTA_DECISAO.md` exige; os 3 usaram `[D2 · muda o produto]`. Corrigido no exemplo.
Observação (não reprova): as respostas sem banco puseram a etapa 4 como ▶️ e não ✅, porque a simulação não gravava.
