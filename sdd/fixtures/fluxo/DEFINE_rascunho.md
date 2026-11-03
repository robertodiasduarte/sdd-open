# DEFINE: X

> Fixture do `sdd-fluxo.sh seguir`: DEFINE em rascunho (PARAR: não está pronto).

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | X |
| **Status** | Draft |

## Problem Statement

O relatório mensal soma o mês anterior.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — fixture do pacote, sem dinheiro, tributo, folha ou dado pessoal | exemplo |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "true"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

## Next Step

Execute o **SDD Design by RDD**.
