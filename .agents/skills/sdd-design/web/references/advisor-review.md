# Advisor Review — Design pre-build

Usar somente quando houver uma revisão formal externa da arquitetura antes do Build.

## Request contract

Enviar uma pergunta focada por consulta.

Incluir:
- tipo: `plan-review`;
- tarefa e critérios de sucesso;
- UMA pergunta;
- material necessário do DESIGN.

Pedir resposta com no máximo 300 palavras e quatro blocos:
1. VERDICT;
2. TOP RISKS — máximo 3, ranqueados;
3. SPECIFIC FIXES;
4. WHAT TO IGNORE.

## Advisor Ledger

Toda nota de TOP RISKS/SPECIFIC FIXES deve receber disposição explícita no DESIGN:

| # | Note | Severity | Decision | Evidence |
|---|---|---|---|---|
| 1 | resumo | HIGH/MEDIUM/LOW | APPLIED/REBUTTED | evidência ou razão |

Nunca descartar nota silenciosamente.

Itens em WHAT TO IGNORE não precisam entrar no ledger.

Quando APPLIED, atualizar as seções afetadas do DESIGN antes do Build.
Quando REBUTTED, registrar uma razão objetiva em uma linha.
