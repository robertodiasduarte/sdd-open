# DEFINE: FIXTURE_CONTROLE

> Fixture do `verify-gate.sh` — idêntica à FIXTURE_NEEDS_CLARIFICATION **sem** o marcador
> de ambiguidade. Serve para provar que o runner sai `0` quando o DEFINE está limpo e o gate
> passa. Se este arquivo devolver algo diferente de `0`, o runner está quebrado.

## Problem Statement

O envio de notificação usa a fila do provedor e precisa respeitar o teto de mensagens por minuto.

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "true"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```
