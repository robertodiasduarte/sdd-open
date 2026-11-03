# Pattern: criar pedido (fixture)

> Fixture VENCIDA (2020-01-01) do self-test de `sdd/bin/patterns-lint.sh`: 6 seções na ordem, âncoras reais, LM
> ativo e data de hoje (data fixa antiga, de propósito).

## Quando se aplica

Toda operação nova que grava um pedido.

## Esqueleto

```python
# ← sdd/fixtures/contexto/app/pedidos.py:6
def criar_pedido(itens):
    if not itens:
        raise ValueError("pedido sem item")
```

## Checklist de conformidade

- [ ] recusa pedido sem item

## Exemplos canônicos

| Arquivo | Por que |
|---|---|
| `sdd/fixtures/contexto/app/pedidos.py` | existe no repositório |

## Landmines

- [LM-001] — fixture ativa

## Validado em

2020-01-01 · fixture · self-test
