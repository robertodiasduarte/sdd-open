"""Código fictício: fixture do self-test de sdd/bin/contexto-lint.sh. Não roda."""

PEDIDO_ITEM_COLUNAS = ("pedido_id", "produto_id", "quantidade")


def criar_pedido(itens):
    """Grava um pedido com os itens."""
    if not itens:
        raise ValueError("pedido sem item")
    return {"itens": list(itens)}


def cancelar_pedido(pedido):
    """Cancela um pedido ainda não entregue."""
    if pedido.get("entregue"):
        raise ValueError("pedido entregue não se cancela")
    pedido["cancelado"] = True
    return pedido
