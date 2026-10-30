# BUILD REPORT: sem_avaliacao

> Fixture do sdd-open (F7): reprova por avaliação ausente — nenhum `AVALIACAO_sem_avaliacao_*.md` e nenhuma linha sobre o avaliador.

## Acceptance Test Verification

| ID | Critério (EARS) | Resultado | Evidência |
|----|-----------------|-----------|-----------|
| AT-001 | When the user saves, the system shall show the receipt | true | `evidence/sem_avaliacao/AT-001.log` |
| AT-002 | If the file is empty, then the system shall refuse it | false | — |

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 2 (api, ui)
