# DEFINE: X

> Fixture do `sdd-fluxo.sh seguir`: bloco do Verify Gate sem kind e sem cmd (PARAR: o --print sai 0 mesmo assim).

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | X |
| **Status** | Ready for Design |

## Problem Statement

O relatório mensal soma o mês anterior.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Governança** | N.A. — fixture do pacote, sem dinheiro, tributo, folha ou dado pessoal | exemplo |

## Verify Gate

```yaml
verify_gate:
  pass_when: "exit 0"
```

## Next Step

Execute o **SDD Design by RDD**.
