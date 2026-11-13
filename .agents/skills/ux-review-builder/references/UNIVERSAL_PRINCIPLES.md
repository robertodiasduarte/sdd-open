# Princípios universais obrigatórios

Todo `UX_STANDARD.md` gerado contém estes dez princípios como piso de qualidade. O projeto pode acrescentar regras mais estritas, mas não remover silenciosamente este núcleo.

| ID | Princípio | Regra verificável mínima |
|---|---|---|
| UX-CORE-001 | Autoexplicativo | A tarefa principal pode ser compreendida sem manual, tour obrigatório ou tooltip como muleta. |
| UX-CORE-002 | Estado inequívoco | Salvo, pendente, processando, concluído, falhou e demais estados relevantes são distinguíveis sem ambiguidade. |
| UX-CORE-003 | Ação principal evidente | Em cada contexto, o próximo passo importante é perceptível e não compete com ações secundárias equivalentes. |
| UX-CORE-004 | Prevenção e recuperação de erros | Erros previsíveis são prevenidos quando razoável, e todo erro acionável oferece caminho de recuperação. |
| UX-CORE-005 | Acessibilidade por padrão | Fluxo por teclado, foco, rótulos, contraste, alvos de toque e sinais que não dependem só de cor são considerados desde o início. |
| UX-CORE-006 | Responsividade real | Mudanças de tamanho de tela preservam prioridade, legibilidade, ordem de leitura e a capacidade de concluir a tarefa. |
| UX-CORE-007 | Feedback imediato | Ações relevantes produzem resposta perceptível do sistema em tempo e forma adequados ao contexto. |
| UX-CORE-008 | Consistência | Intenções iguais usam linguagem, componentes, estados e comportamentos equivalentes em todo o produto. |
| UX-CORE-009 | Sem dark patterns | Não esconder consequências, induzir por confusão, criar urgência falsa ou dificultar deliberadamente escolhas legítimas. |
| UX-CORE-010 | Acabamento completo | Loading, empty, error, success, partial data, permission denied e disabled fazem parte da feature e têm comportamento definido. |

## Uso no gate

Uma violação comprovada de um princípio universal usa a severidade-base registrada no `UX_STANDARD.md`: `MUST` em todos, exceto `UX-CORE-008` (Consistência), que nasce em `SHOULD`. O projeto pode endurecer essa severidade, nunca afrouxar as demais. Se o responsável aceitar uma exceção, registrar o aceite explicitamente, sem marcar a regra como conforme.
