# Retry Ladder e Advisor

## Retry ladder por critério

### Primeira falha
Corrigir no mesmo contexto somente erro local/trivial:
- typo;
- import;
- lint;
- pequena incompatibilidade evidente.

### Segunda falha
Reexecutar como tarefa fresca.

FIX brief contém somente:
1. critério de aceitação que falhou, preservado textualmente;
2. saída de erro relevante;
3. inputs mínimos necessários;
4. instrução para tratar como tarefa nova e não assumir que a tentativa anterior estava quase certa.

Não carregar a justificativa da tentativa anterior.

Se o runtime não oferece fresh dispatch, reduzir deliberadamente o contexto ao FIX brief e registrar a limitação.

### Terceira falha
STOP.

Registrar blocker no Build Report.
Nunca relaxar o critério para fabricar green.

## Advisor / revisão externa

Usar apenas quando ferramenta de revisão por modelo/agente independente estiver realmente disponível e o usuário aceitar.

### Pre-build
Recomendar YES para:
- arquitetura nova com >=3 arquivos;
- security surface;
- public/cached route.

Recomendar NO para 1–2 arquivos triviais sem contract change.

### Post-build
Recomendar YES para:
- security diff;
- public/cached route;
- lógica cross-file sutil;
- ralph/briefs.

### Request contract
Uma consulta = uma pergunta focada.

Incluir:
- TYPE;
- tarefa + critérios de sucesso;
- uma pergunta;
- material necessário.

Pedir resposta curta com:
1. VERDICT;
2. TOP RISKS (máx. 3);
3. SPECIFIC FIXES;
4. WHAT TO IGNORE.

## Advisor Ledger

Toda nota acionável recebe:
- APPLIED; ou
- REBUTTED.

Nunca sumir com finding.

Se finding HIGH for aplicado depois do gate, rerodar Verify Gate antes de Complete.
