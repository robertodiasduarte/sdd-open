# BUILD REPORT: pendente

> Fixture do sdd-open (F7): passa com aviso no modo comum; `report-lint.py --pendente` sai 1 e a release aborta.

## Acceptance Test Verification

| ID | Critério (EARS) | Resultado | Evidência |
|----|-----------------|-----------|-----------|
| AT-001 | When the user saves, the system shall show the receipt | true | `evidence/pendente/AT-001.log` |
| AT-002 | If the file is empty, then the system shall refuse it | false | — |

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

avaliador: PENDENTE (o build travou no Verify Gate, exit 3, antes do passo 5d)
