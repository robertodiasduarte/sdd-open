# Cenários de comportamento da sdd-seguranca — resultado (2026-11-11, sobre 22c87da)

Critério escrito antes: `CENARIOS-criterio.md` (nesta pasta). 6 subagentes em contexto novo, cada um com uma cópia
própria do projeto de teste (a skill, o script, `lib/python.sh` e os 2 fragmentos), só o caminho e o pedido.

| Cenário | Execução | 1 | 2 | 3 | 4 | Veredito | Observação |
|---|---|---|---|---|---|---|---|
| 1 sem gatilho | 1 | ✅ N.A. em 1 linha com motivo | ✅ sem pergunta | ✅ nenhum item | ✅ 1 linha trocada (Segurança) | APROVADA | — |
| 1 sem gatilho | 2 | ✅ | ✅ | ✅ | ✅ 1 linha trocada | APROVADA | Status com ➖ nas etapas 2 e 3 |
| 1 sem gatilho | 3 | ✅ | ✅ | ✅ | ✅ 1 linha trocada | APROVADA | — |
| 2 login + Supabase | 1 | ✅ 5 gatilhos com o trecho | ✅ 5 itens, 1º S01 alta, stack supabase/web | ✅ 1 pergunta `[D2 · muda o produto]`, 4 opções | ✅ DEFINE intacto | APROVADA | — |
| 2 login + Supabase | 2 | ✅ | ✅ | ✅ | ✅ | APROVADA | avisou que o DEFINE de teste não tem Verify Gate e que pergunta na etapa 4 |
| 2 login + Supabase | 3 | ✅ | ✅ | ✅ | ✅ | APROVADA | idem |

Resultado: 6 de 6 aprovadas, numa série. Nenhuma correção de texto foi necessária, então não houve 2ª série.
Limite: as 6 execuções foram no mesmo agente (Claude); outros agentes não foram executados.
