# Pattern: modelo de domínio (fixture)

> Fixture do self-test de `sdd/bin/contexto-lint.sh`: um mapa de domínios fictício (pedidos, estoque).

## Quando se aplica

Toda feature que toca pedidos ou estoque.

## Esqueleto

### ctx:pedidos

**Faz:** o pedido do cliente, do carrinho à entrega.
**Âncoras:** `pedido` · `pedido_item` · `sdd/fixtures/contexto/app/pedidos.py` · `/pedidos`
sup: `pedido_item` `checkout`

### ctx:estoque

**Faz:** quanto há de cada produto e o que está reservado.
**Âncoras:** `estoque_saldo` · `reserva_estoque` · `sdd/fixtures/contexto/app/estoque.sql`
sup: `estoque_saldo` `reserva_estoque`

## Checklist de conformidade

- [ ] todo bloco tem **Faz:**, **Âncoras:** e sup:

## Exemplos canônicos

| Arquivo | Por que |
|---|---|
| `sdd/fixtures/contexto/app/pedidos.py` | existe no repositório |

## Landmines

- [LM-001] — fixture

## Validado em

2026-11-03 · fixture · self-test
