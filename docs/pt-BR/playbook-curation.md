<!-- Language: [English](../playbook-curation.md) · **Português** -->

# Curadoria do playbook e invariantes

Desde a v2.6.0, o último passo de uma release confere o que a feature ensinou ao projeto. Um script colhe, um
agente que não viu a conversa julga, um conferidor separa contagem de mudança de regra, e só a mudança de
regra vira pergunta. Um projeto que nunca registrou uma lição só vê uma linha: "esta feature não trouxe
lição nova nem contagem".

## Os três papéis

| Papel | Quem | O que faz |
|---|---|---|
| Colher | `sdd/bin/playbook-curator.sh --colher` | lê os documentos da feature e imprime uma linha por coisa a julgar |
| Julgar | o curador, um agente de contexto fresco (brief: `.agents/skills/sdd-playbook/references/curator.md`) | confere cada linha contra o `arquivo:linha` citado e devolve uma tabela; nunca escreve |
| Decidir | você | responde às mudanças de regra, um item por vez |

A curadoria roda **depois** do push. Ela nunca desfaz uma publicação, e toda mensagem dela diz que a
publicação já terminou.

## O que a colheita lê

`--preparar <FEATURE>` copia (nunca move) os documentos da feature para uma pasta de staging fora do projeto:
o DESIGN, o BUILD_REPORT, os `AVAL*-*.log` e a `AVALIACAO_*.md` do avaliador, o ledger da release e a ficha da
feature. Procura também em `sdd/archive/<FEATURE>/`. Depois, `--colher <staging> sdd/playbook.md` imprime:

| Linha | De onde vem |
|---|---|
| `DELTA LM-nnn ajudou+1` | linha da tabela de landmines (DESIGN ou BUILD_REPORT) cuja célula de veredito começa com ✔ |
| `DELTA LM-nnn mordeu+1` | linha cujo veredito começa com `mordeu`, ou linha de achado (❌, `NEEDS_WORK`, `FAIL`, `WAIVED`, `mordeu_antes:`) que cita a landmine |
| `SUGESTAO mordeu? LM-nnn` | linha de achado sem ID que contém um termo de `sup:` de uma landmine ativa; nunca é contagem sozinha |
| `CANDIDATO #n → LM-xxx` / `REJEITADO` | bloco de candidato do BUILD_REPORT ou da ficha; sem `evidencia:` é rejeitado |
| `PROMOVER? LM-nnn` | landmine ativa com `mordeu` de 2 para cima e ainda sem mecanismo |

Toda linha a julgar leva uma impressão digital (`fp=`). Depois de uma curadoria, essas linhas vão para
`sdd/releases/<FEATURE>/CURATOR-colhidos.txt`, ao lado do ledger; a próxima release da mesma feature as mostra como
`JA_JULGADO` e não conta de novo.

Com `--inv`, uma landmine que já mordeu e nunca foi classificada também aparece, como `INV_PENDENTE`. Exit `0` quer dizer que há o que julgar ou relatar, `1` que não há nada, e qualquer outro exit é **falha**,
nunca "nada a colher".

## O que entra sem pergunta, e o que não entra

O `--conferir-bloco` é o juiz da tabela do curador, uma linha para cada linha da colheita. Ele reprova a tabela quando falta uma linha da colheita,
quando o curador escreveu alguma coisa no projeto ou na pasta de staging (o staging é selado com `--selar`
antes do despacho, e o projeto é comparado pelo `governanca-fronteira.sh`), e quando uma contagem automática
não é **igual** a uma linha que o script colheu: a mesma landmine, o mesmo verbo, `+1`, o mesmo
`arquivo:linha`.

| Tipo | Entra |
|---|---|
| contagem que o script colheu, confirmada pelo curador | sem pergunta; vai para o recibo **Decidi sozinho** |
| lição nova (`ADD`), aposentadoria (`TOMBSTONE`), refino (`REFINE`), promoção, invariante, sugestão que o curador confirmou | só com a sua resposta, em pergunta marcada `[D3 · muda a regra do método]` |

As linhas aprovadas são aplicadas numa **cópia** (`--aplicar`); a cópia passa pelo lint do playbook, pela
conferência anti-collapse e pela trava das invariantes, e só então substitui o `sdd/playbook.md`. A mudança
vai num commit só dela (com os logs da curadoria, quando o projeto versiona a pasta de evidência). Enviar esse commit para a branch padrão é outra pergunta, marcada
`[D1 · não se desfaz]`: em muitos projetos, um push publica.

## A gramática do delta

```text
LM-020 ajudou+1
LM-016 mordeu+1
LM-004 promovido_para=<caminho do mecanismo>
ADD <seção> :: sup: `termo1` `termo2` :: regra. **Do instead:** ação. → ficha: — · promovido_para: —
TOMBSTONE LM-nnn :: motivo
REFINE LM-nnn :: novo texto. **Do instead:** ação.
```

`--aplicar <delta> <playbook>` valida o delta inteiro antes. Com uma linha inválida, imprime todos os erros,
não imprime nada em stdout e sai 2.

## Invariantes

A landmine diz "isto me mordeu". A invariante, em `sdd/invariants.md`, diz "isto nunca pode ser violado, e é
isto que vigia":

```text
- [INV-NNN] estado=ok|auto|humano origem=seed|LM-nnn[,LM-mmm] [check=<caminho>] :: <regra> · por quê: <texto> [· tarefa: … | · motivo: …]
```

- `ok`: um check roda sem alguém lembrar. `auto`: dá para automatizar, e a tarefa diz como. `humano`: exige
  julgamento, e o motivo diz por quê.
- Toda landmine ativa que já mordeu ao menos uma vez, ou que foi promovida, precisa estar classificada: como
  origem de uma invariante, ou em `## Descartados` com o motivo.
- `--validar-inv <playbook> <invariantes>` é a trava: reprova invariante com origem aposentada, landmine sem
  classificação, ID repetido e `check=` que não existe.
- Aposentar uma landmine que é origem de uma invariante é **uma** decisão, não duas: o `--cruzar` propõe a
  linha ajustada da invariante, e as duas vão na mesma opção. O `--aplicar-inv` grava as linhas aprovadas;
  ninguém edita o arquivo à mão.

Um projeto instalado antes da v2.6.0 recebe um `sdd/invariants.md` vazio. A primeira curadoria mostra cada lição
antiga ainda não classificada e pergunta sobre ela, uma vez; sem resposta, a trava segura e nada é aplicado. Sem o arquivo, a curadoria
pula o cruzamento e diz que pulou.

## O que ela não faz

- Não lê nada fora dos documentos da feature, e não colhe em subpastas.
- Não lê a conversa da sessão, só os arquivos.
- Não julga a qualidade de uma lição: isso é do curador, e seu.
- Não publica um catálogo de invariantes; o arquivo-fonte é o catálogo.
- Uma promoção aceita aqui só registra a decisão, como pendência. O mecanismo é uma correção própria, com um caso que falha
  sem ele.

Saídas e palavras de cada modo: [cli-conventions.md](../cli-conventions.md).
