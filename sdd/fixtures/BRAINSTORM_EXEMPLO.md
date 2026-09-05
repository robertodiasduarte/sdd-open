# BRAINSTORM: CONCILIADOR_EXTRATO

> Exemplo pronto para o primeiro teste do SDD Open. Use-o como entrada da fase Define
> (`/sdd-define sdd/fixtures/BRAINSTORM_EXEMPLO.md`) e confira se o DEFINE gerado passa em
> `sdd/bin/verify-gate.sh --print`. Pode ser apagado depois.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | CONCILIADOR_EXTRATO |
| **Date** | 2026-09-05 |
| **Status** | Ready for Define |

## Initial Idea

**Raw Input:** "Quero uma ferramenta de linha de comando que leia um extrato bancário em CSV e
um razão contábil em CSV e aponte os lançamentos que não batem: presentes em um lado e
ausentes no outro, ou com valor diferente."

**Context Gathered:**
- Extratos vêm em CSV com colunas `data`, `descricao`, `valor`; o razão em CSV com `data`,
  `historico`, `debito`, `credito`.
- O casamento é por data e valor absoluto; descrição não é confiável.
- Volume típico: até 5.000 linhas por arquivo.

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Quem usa? | O próprio contador, uma vez por mês | Não precisa de interface gráfica |
| 2 | O que é "bater"? | Mesma data e mesmo valor absoluto | Regra de casamento fechada |
| 3 | E os duplicados? | Dois lançamentos iguais no mesmo dia são legítimos | Casar por multiplicidade, não por conjunto |

## Approaches Explored

### Approach A: Script único em Python com saída em CSV ⭐ Recommended

**Pros:** roda em qualquer máquina com Python; saída abre em planilha.
**Cons:** sem interface; o contador precisa do terminal.

### Approach B: Planilha com fórmulas

**Why not recommended:** quebra acima de algumas centenas de linhas e não é reprodutível.

## Selected Approach

Approach A.

## Suggested Requirements for /define

### Problem Statement (Draft)
O contador gasta horas comparando extrato e razão à mão e deixa passar diferenças de valor.

### Success Criteria (Draft)
- [ ] Dois CSVs de 5.000 linhas processados em menos de 5 segundos.
- [ ] Toda divergência listada com o lado de origem e o motivo (ausente ou valor diferente).
- [ ] Duplicados legítimos não aparecem como divergência.

### Out of Scope (Confirmed)
- Importar direto do banco; corrigir lançamentos; interface gráfica.

## Next Step

**Ready for:** `/sdd-define sdd/fixtures/BRAINSTORM_EXEMPLO.md`
