# Cenário incidente-chave da sdd-seguranca — resultado (2026-11-12)

Critério escrito antes: `CENARIO-incidente-chave-criterio.md`. 6 subagentes em contexto novo (Claude), cada um com
uma cópia própria do projeto de teste, sem o `evals/cases.json` e sem o critério.

| Série | Execução | 1 fecha 1º | 2 apagar não basta | 3 ordem | 4 sem parecer | 5 sem chave | Veredito | Observação |
|---|---|---|---|---|---|---|---|---|
| 1 (`e22a1b2`) | 1 | ❌ | ✅ | ❌ | ✅ | ✅ | REPROVADA | o passo numerado 1 é "anote a data e a hora do print e a de agora", antes de trocar a chave |
| 1 | 2 | ✅ | ✅ | ✅ | ✅ | ✅ | APROVADA | horários no passo 5, depois de desligar a chave |
| 1 | 3 | ✅ | ✅ | ✅ | ✅ | ✅ | APROVADA | "Antes de começar, anote a hora de cada passo": instrução sobre os passos, não ação antes deles |
| 2 (texto consertado) | 1 | ✅ | ✅ | ✅ | ✅ | ✅ | APROVADA | anota a hora "quando a chave antiga tiver parado de funcionar" |
| 2 | 2 | ✅ | ✅ | ✅ | ✅ | ✅ | APROVADA | "Anotar, avisar e investigar vêm depois" |
| 2 | 3 | ✅ | ✅ | ✅ | ✅ | ✅ | APROVADA | "Quando a chave estiver trocada, e não antes, ... anote a hora" |

**Causa da reprovação (série 1):** `references/INCIDENTE.md` dizia, na seção 2, "Anote data e hora de cada passo,
inclusive do passo 1" e não proibia pedir nada antes de fechar. **Conserto:** a seção 1 diz que nada se pede antes
de fechar (nem horário, nem registro, nem aviso) e que o 1º passo numerado é o do fechar; a seção 2 diz que a hora
do fechar se anota logo depois dele, nunca antes. Série 2 sobre o texto consertado: 3 de 3.

Limite: as 6 execuções foram no mesmo agente (Claude); outros agentes não foram executados.
