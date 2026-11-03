# Pattern: criar pedido (fixture)

> Fixture VERMELHA (secao-fora-de-ordem) do self-test de `sdd/bin/patterns-lint.sh`: 6 seções na ordem, âncoras reais, LM
> ativo e data de hoje (o self-test troca o marcador da seção "Validado em" pela data do dia).

## Quando se aplica

Toda operação nova que grava um pedido.

## Esqueleto

```python
# ← sdd/fixtures/contexto/app/pedidos.py:6
def criar_pedido(itens):
    if not itens:
        raise ValueError("pedido sem item")
```

## Exemplos canônicos

| Arquivo | Por que |
|---|---|
| `sdd/fixtures/contexto/app/pedidos.py` | existe no repositório |

## Checklist de conformidade

- [ ] recusa pedido sem item

## Landmines

- [LM-001] — fixture ativa

## Validado em

__HOJE__ · fixture · self-test
