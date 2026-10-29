# Conferir a vigência antes de usar uma regra

> **Resolve:** decidir se uma regra desta base se aplica a uma nota, pela data de emissão.
> **Fonte:** prática de uso desta base; datas e páginas nas regras de `rules/`.
> **Vale para:** atemporal — o procedimento não muda; as datas vêm de cada regra

## Quando usar

- Antes de citar uma regra desta base para uma nota específica.
- Antes de um software consumir a base para validar notas.

## Quando NÃO usar

- Para descobrir a regra de um período fora da data-base: a base só responde até a data-base do `index.md`; depois dela, confira a fonte oficial.

## Passo a passo

1. Pegue a data de emissão da nota (`ide/dhEmi`), não a data de hoje.
2. No [RULE_MAP.md](../RULE_MAP.md), ache a regra pelo id e leia a coluna Vigência.
3. Confirme que a data de emissão está entre `de` e `ate` (ou depois de `de`, se a regra está em vigor).
4. Leia o Status: `confirmado` pode ser aplicado; `premissa` e `nao-confirmado` vão para o relatório com a ressalva escrita.
5. Se a regra tem "Conflito com", leia a seção Conflitos do `index.md` antes de concluir.
6. Se a data de emissão é posterior à data-base, confira a fonte do catálogo antes de usar.

## Como saber que deu certo

Você consegue dizer, para a nota, qual regra se aplica, em que página está escrita e com que status — sem depender de memória.

## Quando dá errado

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Duas regras parecem valer na mesma data | Uma delas deveria ter `ate` | Feche a mais antiga com `ate` e regere o RULE_MAP |
| A regra cita página que não bate | Versão nova da NT | Catalogue a versão nova com id novo e recapture o SHA |

## Relacionados

- [concepts/ano-teste-2026.md](../concepts/ano-teste-2026.md)
