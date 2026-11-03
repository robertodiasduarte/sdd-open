# DEFINE: FIXTURE_SEM_GOVERNANCA

> Fixture do `verify-gate.sh` — idêntica à FIXTURE_CONTROLE **sem** a linha `Governança` no Technical
> Context, como um DEFINE escrito antes da v2.4.0. Serve para provar que o runner sai `5` com a mensagem
> GOVERNANÇA NÃO REVISADA e as 2 saídas, mesmo com o gate passando.

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
