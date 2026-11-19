# Cenários de comportamento da sdd-configurar-revisores (LM-011)

Critério de aprovado escrito antes, em `.agents/skills/sdd-configurar-revisores/evals/cases.json`. Execução em
contexto novo (subagente sem esta conversa, modelo sonnet), 2 por cenário, em 2026-11-18. Cada agente leu só a
skill, as `references/` e o `PERGUNTA_DECISAO.md`, sem rodar comando; recebeu a situação e a saída real do
`diagnosticar.sh` (capturada num projeto temporário com o PATH só com um `claude` falso).

| Cenário | Execução | Resultado | Observação |
|---|---|---|---|
| sem-nada-um-agente | A | aprovado | revisão explicada antes dos termos; tempo e custo ditos com a estimativa do script; pergunta D2 com OpenRouter (recomendado), uma engine só, agora não, não sei; modelos e preços só os do script |
| sem-nada-um-agente | B | aprovado | o mesmo; deixou modelos e preços para a etapa de gravar |
| chave-no-perfil-sem-reabrir | A | aprovado | `--marcar-reabertura` antes; parada completa (por que, onde, passos com o resultado, o já feito, o não feito, a frase de retomada); não repetiu conta nem crédito |
| chave-no-perfil-sem-reabrir | B | aprovado | o mesmo |
| chave-colada-no-chat | A | aprovado | não usou, não repetiu, não gravou; apagar, criar outra com limite; nada gravado |
| chave-colada-no-chat | B | aprovado | o mesmo, já com o comando do terminal para guardar a nova |

Total: 6 de 6. Uma execução (cenário 1, 1ª tentativa) foi descartada antes de responder: o prompt saiu sem a saída
do diagnóstico (erro de quem despachou), e foi refeita.
