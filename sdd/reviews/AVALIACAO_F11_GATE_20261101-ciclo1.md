# AVALIAÇÃO F11_GATE — contexto fresco, modo veredito, ciclo 1

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), sobre `468d605`.
> Evidências: `sdd/reports/evidence/F11_GATE/AVAL1-*.log` (35) e 5 `AVAL1-*.sonda.txt` — logs que terminavam num
> formatador e por isso não provam o comando (gate-shell-evidencia); os ATs deles (004, 019, 020) estão provados
> em `verde-adiados.log`, `gate-v.log` e `teste-gate.log`. Correções no commit seguinte, com teste vermelho antes.

```text
<<<AVALIACAO
FEATURE: F11_GATE · ciclo 1 · modo veredito · HEAD 468d605 (feat/f11-gate)
Veredito: NEEDS_WORK — 1 MEDIUM e 4 LOW. Os demais ATs provados por execução: Verify Gate inteiro (881 OK), gate (90
asserções, 5 s), as 5 sabotagens do DEFINE e as 4 extrações nulas pegas, isolamento resistente a ambiente hostil.

| AT | Resultado |
|---|---|
| 001, 002, 004–027, Verify Gate | PASS (AT-024: só Custo.test_quatro_formas muda, que é o AT-019) |
| 003 | FALHA PARCIAL (M1) |

Sabotagens extras pegas: tokens de saída do codex, exclusão por excl e por mesma engine, 429 sem retry, auth como
persistente, data_collection allow. Registry customizado (outros modelos): gate VERDE.
Não verificado localmente: CI Ubuntu/macOS, macOS ≤ 25 min, release v2.3.1.

ACHADOS
- M1 · MEDIUM · AT-003: o gate não confere DISAGREE_EVIDENCE, DISAGREE_CONCERN nem NOVO (o auditor dos stubs só dá
  AGREE); sabotar vereditos_auditor para aceitar só AGREE deixa o gate VERDE (AVAL1-15). Correção: resposta de
  auditor com um veredito de cada tipo (NOVO com arquivo, linha, severidade) e asserção da lista exata no jsonl.
- L1 · LOW · AT-002: o custo do claude vem igual em total_cost_usd e modelUsage.costUSD; um adapter que lê de
  modelUsage passa (AVAL1-19). Correção: valores diferentes no stub.
- L2 · LOW · AT-006: a falha de credencial só é provada no claude; um sinal_auth quebrado no openrouter, codex ou
  gemini não é pego (AVAL1-37).
- L3 · LOW · AT-016: eval-agree sem argumento num projeto recém-instalado (sem a pasta de revisões) sai 64 em vez
  de 2 SEM DADOS (AVAL1-32).
- L4 · LOW: eval-agree sem argumento e sem git no PATH morre com traceback FileNotFoundError e exit 1 (AVAL1-29).
Notas: fora do escopo (igual na v2.3.0): codex de assinatura que audita e sai 68 mostra custo $? (AVAL1-35).
Arquivo fora do mktemp gravado pelo avaliador: init-<pid>.out na pasta temporária do sistema (saída do init).
>>>
```
