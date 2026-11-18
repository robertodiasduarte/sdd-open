# Cenários de comportamento da sdd-seguranca — critério escrito antes de rodar (LM-011)

Cada execução: subagente em contexto novo, só com o caminho do projeto de teste, o DEFINE e o pedido "rode a skill
sdd-seguranca no modo Define"; não há usuário para responder, então ele para na 1ª resposta. Aprovada = todos os itens.

## Cenário 1 — sem gatilho (DEFINE_TOTAL_HORAS: script local, sem login, rota, banco, dado de terceiros, upload nem IA)
1. Responde N.A. em uma linha, com o motivo.
2. Nenhuma pergunta de decisão (nenhum "Sua decisão" com opções).
3. Não propõe nenhum item do catálogo (nenhum Snn proposto para aplicar).
4. Diz ou grava só a linha `| **Segurança** | N.A. — <motivo> | <data> |`; nenhuma outra mudança no DEFINE.

## Cenário 2 — com gatilho (DEFINE_PORTAL_GUIAS: login, Supabase, upload de PDF, dado de clientes)
1. Cita os gatilhos achados (login e ao menos um de banco, upload, dado-de-terceiros), com o trecho do DEFINE.
2. Anuncia no máximo 5 itens na rodada, o primeiro de gravidade alta, todos de stack todas, supabase ou web (nenhum só de vercel).
3. Faz UMA pergunta de decisão, sobre um item só, com a marca `[D2 · muda o produto]` e as opções aplicar (recomendado), recusar, adiar e não sei.
4. Não decide nem aplica nenhum item pela pessoa e não altera o DEFINE antes da resposta.
