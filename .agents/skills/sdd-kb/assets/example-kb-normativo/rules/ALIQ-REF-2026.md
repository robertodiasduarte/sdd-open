---
regra: ALIQ-REF-2026
titulo: Alíquotas de referência do ano-teste — CBS 0,90%, IBS da UF 0,10%, IBS do município 0,00%
vigencia:
  de: 2026-01-01
  ate: 2026-12-31
fonte:
  id: NT2025002-151
  localizador: p. 45, 47 e 49, regras UB18-10, UB37-10 e UB56-10
status: confirmado
conflito_com: [REPORT-2026]
implementacao: null
teste: null
severidade: E
codigo: "1026 / 1036 / 1037"
---

# ALIQ-REF-2026 — alíquotas de referência de 2026

## O que a regra diz

Em 2026, as alíquotas informadas nos grupos `gIBSUF`, `gIBSMun` e `gCBS` seguem a referência do ano: 0,10%, 0,00% e 0,90%. Item com `cClassTrib` de tributação regular (`ind_gTribRegular = 1`) informa zero.

## Como esta base aplica

Valores na tabela [tabelas/2026-01-01/aliquotas-referencia.json](../tabelas/2026-01-01/aliquotas-referencia.json). A regra se encerra em 2026-12-31; a alíquota de 2027 em diante é outra regra, ainda não registrada.
