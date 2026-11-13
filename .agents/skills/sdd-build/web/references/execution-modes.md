# Execution Modes

## Princípio

A skill recomenda; o usuário decide antes da primeira alteração de código.

Oferecer apenas modos que o runtime atual consegue executar de verdade.

## Sinais

| Sinal | Como medir | Tendência |
|---|---|---|
| Arquivos | linhas do File Manifest | <=6 favorece default; >=10 favorece ralph/briefs |
| Acoplamento | schemas/helpers/imports/contratos compartilhados | alto favorece default |
| Segurança | authz/auth gates/migrations com lógica | default/ralph; excluir briefs baratos |
| LLM prompts | flag + inventory | default/ralph; excluir briefs baratos |
| Independência | componentes sem dependência e paths disjuntos | ralph; briefs se volume alto e seguro |
| Context-rot | manifest grande + lógica extensa | ralph |
| Paralelismo | waves independentes | briefs quando suportado |

Empate → recomendar `default`.

## default

Loop sequencial no mesmo contexto.

Usar quando:
- poucos arquivos;
- alto acoplamento;
- nomes/contratos compartilhados;
- coerência cross-file importa mais que contexto limpo.

Vantagens:
- coerência;
- menor custo de re-leitura.

Risco:
- contexto cresce em Build longo.

## ralph

Um contexto/execução fresca por tarefa.

Somente oferecer se houver capacidade real de respawn/subagente/fresh task.

Usar quando:
- muitos itens relativamente independentes;
- Build longo/interrompível;
- contexto pode degradar;
- granularidade por tarefa ajuda.

Preservar progresso em `PROGRESS_{FEATURE}.md` usando [assets/PROGRESS_TEMPLATE.md](../assets/PROGRESS_TEMPLATE.md) quando o runtime permitir filesystem.

Se não houver fresh context real, não chamar execução de `ralph`.

## briefs — experimental

Workers stateless por wave de dependência.

Somente oferecer se houver dispatch paralelo real.

Usar apenas quando existir volume paralelo relevante depois de excluir:
- LLM prompt items;
- autorização/auth gates;
- migrations com lógica;
- outros itens de segurança sensíveis.

Compilar cada worker com [assets/WORKER_BRIEF_TEMPLATE.md](../assets/WORKER_BRIEF_TEMPLATE.md).

Regras:
- worker recebe somente o brief;
- inputs precisam ser completos e inline;
- path collision separa waves;
- orchestrator faz verificação;
- `INPUT GAP` significa brief ruim, não falha do worker;
- Verify Gate final permanece no orchestrator.

## Pergunta ao usuário

Apresentar:
1. recomendação;
2. principal sinal;
3. opções realmente disponíveis.

Exemplo de forma, não texto obrigatório:

`Recomendo default: 5 arquivos com schema e service compartilhados tornam coerência cross-file mais importante. Você prefere (a) default [recomendado] ou (b) ralph? briefs não está disponível neste runtime.`

Registrar decisão no Build Report.
