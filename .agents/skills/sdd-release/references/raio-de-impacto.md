# Raio de impacto — brief do agente fresco de uma superfície

O bug que passa quase nunca está no diff: está no código **não modificado** que depende do que mudou. Você olha uma
superfície só e traça quem a consome. Quem despacha este brief é o passo 0b da `sdd-release`: um agente fresco por
superfície; sem subagente, a própria sessão percorre as superfícies em sequência, sem parada. Contrato de máquina:
`sdd/WORKFLOW_CONTRACTS.yaml` › `raio_de_impacto`.

## Entrada (só isto chega — 5 campos)

```text
superficie: <o que tem contrato: assinatura, retorno, coluna, rota, permissão, comando, slot> · antes: <o contrato na branch padrão> · depois: <o contrato no diff> · invariantes: sdd/invariants.md | ausente · worktree: <raiz>
```

## Processo

1. Procure os consumidores da superfície no projeto inteiro, inclusive nomes montados em texto. Só **leia**: você não edita nada.
2. Para cada consumidor **não modificado** no diff: ele continua funcionando com o `depois:`? Olhe também o teste vizinho do módulo.
3. Leia as invariantes de `invariantes:` cuja regra ou `check=` toca o módulo: alguma é violada? Com `ausente`, escreva `invariantes: ausente`.

## Retorno (a última coisa da resposta)

```text
<<<RAIO
superficie: <a do campo>
consumidor: <arquivo:linha> · ok | quebra — <por quê>
invariante: <INV-nnn> · ok | viola — <por quê>
>>>
```

Uma linha por consumidor e por invariante; sem nenhum, `consumidor: nenhum` ou `invariante: nenhuma`. Cite sempre `arquivo:linha`: o que você não localizou, diga que não localizou, nunca "ok".
