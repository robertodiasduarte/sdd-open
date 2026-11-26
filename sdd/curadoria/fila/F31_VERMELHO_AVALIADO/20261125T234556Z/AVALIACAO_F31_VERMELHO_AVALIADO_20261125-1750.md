<<<AVALIACAO
modo: veredito · ciclo: 3 · FEATURE: F31_VERMELHO_AVALIADO · commit avaliado: 13a9152 · Python 3.9.6 (bordas também no 3.15)
VEREDITO: PASS
(resumo fiel do bloco devolvido; sondas completas em evidence/F31_VERMELHO_AVALIADO/AVAL3-*.log)

| AT | Observado | Resultado |
|---|---|---|
| AT-001 | 35 de 35 | PASS |
| AT-002 | 38 de 39 (a divergente é A5, registrada) | PASS |
| AT-003 | 17 de 18 (a divergente é A3c, fora do DEFINE 1.2) | PASS |
| AT-004 | 9 de 9 | PASS |
| AT-005 | 33 de 34 (a divergente é O4, fora do contrato) | PASS |
| AT-006 | 3 de 3 textos | PASS |
| AT-007 | 11 de 11; 51 de 51 BUILD_REPORTs idênticos, 0 avisos | PASS |
| AT-008 | check-versions exit 0; 62 módulos em série, 0 vermelhos | PASS no medido |
| AT-009 | 21 de 21 | PASS |

NÃO REPETIDO (a pedido): suíte inteira e publish-gate. NÃO VERIFICADO: CI macOS/Linux/Windows. 10 de 10 sabotagens do avaliador pegas.
A1, A2, A3a, A3b, A4, B1, O1, O3 RESOLVIDOS; A3c e A5 REGISTRADOS. O que o conserto quebrou: nada encontrado.
DEFEITO CONTRA O CONTRATO: nenhum que bloqueie. OBSERVAÇÕES: O2 (dois logs de mesmo nome na própria feature: só o primeiro é lido), O4 (mesmo comando com acento em cp1252 e UTF-8 não forma grupo), O5 (o AT-009 não repete "com o antes aceito").
>>>
