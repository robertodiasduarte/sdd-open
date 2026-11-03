# DEFINE: FIXTURE_NEEDS_CLARIFICATION

> Fixture do `verify-gate.sh`. O bloco de gate abaixo é VÁLIDO de propósito (cmd `true`):
> sem a checagem do marcador, este arquivo sairia `0`. O runner correto devolve **`5`**
> (clarificação pendente) e NÃO roda o `cmd` — ambiguidade aberta não vira gate verde.

## Problem Statement

O envio usa a fila do provedor [NEEDS CLARIFICATION: qual classe de throttle se aplica — lote com 120s ou interativo sem espera?] e precisa respeitar o teto.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — fixture do pacote, sem dinheiro, tributo, folha ou dado pessoal | o exit 5 desta fixture vem do marcador |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "true"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```
