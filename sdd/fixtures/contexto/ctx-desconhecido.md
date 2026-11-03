# CONTEXTO: pedidos

ctx: ctx:faturamento
gerado_em: 2026-11-03
sha: 0123456789abcdef0123456789abcdef01234567
superficies: sdd/fixtures/contexto/app/pedidos.py
sup: `pedido_item` `checkout`

> Fixture VERMELHA (ctx-desconhecido: ctx:faturamento não está no mapa) do self-test de `sdd/bin/contexto-lint.sh`: o `sha:` é só formato (a validade real é
> provada num repositório temporário). As âncoras apontam para arquivos da fixture.

## Escopo

O pedido do cliente, do carrinho à entrega. Mapa em `sdd/fixtures/contexto/dominio.md:13`. CONTAMINAÇÃO: não.

## Dados

| Dado | Campos-chave | Origem (arquivo:linha) |
|---|---|---|
| `pedido_item` | `pedido_id`, `produto_id`, `quantidade` | `sdd/fixtures/contexto/app/pedidos.py:3` |

## Operações

| Operação | O que faz | Origem (arquivo:linha) |
|---|---|---|
| `criar_pedido()` | grava um pedido com os itens | `sdd/fixtures/contexto/app/pedidos.py:6` |
| `cancelar_pedido()` | cancela pedido ainda não entregue | `sdd/fixtures/contexto/app/pedidos.py:13` |

## Interfaces

| Interface | Tipo | Chama |
|---|---|---|
| `/pedidos` | rota | `criar_pedido()` (`sdd/fixtures/contexto/app/pedidos.py:6`) |

## Regras vigentes

- Pedido sem item é recusado — `sdd/fixtures/contexto/app/pedidos.py:8`
- Pedido entregue não se cancela — `sdd/fixtures/contexto/app/pedidos.py:15`
- O saldo de estoque nunca fica negativo — `sdd/fixtures/contexto/app/estoque.sql:2`

## Landmines

- `checkout` → [LM-001] — fixture ativa
- `pedido_item` → [LM-001] — fixture ativa

## Histórico SDD

- `sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md`
