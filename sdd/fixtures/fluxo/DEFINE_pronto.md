# DEFINE: X

> Fixture do `sdd-fluxo.sh seguir`: DEFINE pronto, com gate válido (SEGUIR quando o encadeamento está ligado).

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | X |
| **Status** | Ready for Design |

## Problem Statement

O relatório mensal soma o mês anterior.

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
