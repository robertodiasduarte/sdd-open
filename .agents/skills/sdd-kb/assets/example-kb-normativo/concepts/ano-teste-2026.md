# Ano-teste de 2026

> **O que é:** o ano em que CBS e IBS aparecem na NF-e com alíquotas de referência baixas, convivendo com os tributos que vão substituir, para testar leiaute, emissão e apuração.
> **Fonte:** NT 2025.002-RTC v1.51 (p. 42, 45, 47 e 49), capturada em 2026-09-27 — ver [fontes/CATALOGO.md](../fontes/CATALOGO.md).
> **Vale para:** 2026-01-01 a 2026-12-31 (as datas de exigência do grupo por CRT seguem as regras citadas)

## Por que isto existe

Trocar cinco tributos por três exige que emissores, SEFAZ e contribuintes provem que o novo leiaute funciona antes de ele pesar no caixa. O ano-teste cria esse período: os campos novos são preenchidos e validados, com alíquotas que não alteram a carga.

## Como funciona

Duas coisas mudam em datas diferentes, e é aí que mora o erro. A **exigência do grupo `IBSCBS`** depende do CRT do emitente: para o regime normal (CRT 3), a NT fixa homologação em 2026-07-01 e produção em 2026-08-03 (regra UB12-10-CRT3). As **alíquotas de referência** valem o ano inteiro de 2026 (regra ALIQ-REF-2026). Uma nota de CRT 3 emitida em julho de 2026 em produção, portanto, já tem alíquota de referência definida, mas ainda não é rejeitada pela ausência do grupo.

## O que costuma ser confundido

| Isto | Não é isto |
|---|---|
| CBS 0,90% e IBS da UF 0,10% em 2026, pela NT | "0,1% de cada", como circulou em reportagens — ver Conflitos no index |
| Exigência por CRT e por ambiente | Uma data única para todos os emitentes |

## Quando isto importa na prática

Ao validar nota de 2026, a pergunta certa é dupla: o grupo era exigido para este CRT nesta data? E a alíquota informada é a de referência do ano? As duas respostas vêm de regras diferentes, com vigências diferentes.

## Relacionados

- [patterns/conferir-vigencia-antes-de-usar.md](../patterns/conferir-vigencia-antes-de-usar.md)
