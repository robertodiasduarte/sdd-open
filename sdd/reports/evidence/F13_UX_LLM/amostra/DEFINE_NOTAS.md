# DEFINE: Notas de versão

> Um processo que escreve as notas de versão a partir dos commits e confere cada item.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | NOTAS |
| **Status** | Ready for Design |
| **Clarity Score** | 13/15 |

## Problem Statement

As notas de versão são escritas à mão e citam mudanças que não existem.

## Goals

| Priority | Goal |
|---|---|
| **MUST** | Gerar NOTAS.md com um item por mudança visível, cada um com o hash do commit |

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** o processo termina, todo item de NOTAS.md **shall** citar um commit do intervalo | test |

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "python3 -B -m unittest discover -s tests"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `src/notas/` | — |
| **LLM Prompts** | true | o processo chama um modelo |
| **Governança** | N.A. — sem dinheiro, tributo nem dado pessoal | amostra |

## Next Step

Execute o **SDD Design by RDD**.
