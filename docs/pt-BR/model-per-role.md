# Modelo por papel

[English](../model-per-role.md)

Os papéis que o SDD Open despacha em contexto fresco (curador, avaliador, revisor do DESIGN, cartógrafo, executor do
piloto) rodam, por padrão, no modelo da sessão, que costuma ser o mais caro. Este documento mostra como medir se um
modelo mais barato dá o mesmo resultado **no seu projeto** e, só então, trocar. O pacote leva o método e o slot,
nunca nome nem preço de modelo.

## O slot

Em `sdd/config.yaml`:

```yaml
papeis:
  curador: ""
  avaliador: ""
  revisao_design: ""
  cartografo: ""
  executor: ""
  serie_cmd: ""
```

Vazio é o modelo da sessão, o comportamento de sempre. O valor é o nome que o **seu** agente aceita para o modelo,
como texto opaco: começa por letra ou número, depois letras, números e `. _ : / -`, até 80 caracteres.
`bash sdd/bin/sdd-fluxo.sh modelo <papel>` lê e valida o valor. Um valor inválido sai 64 e nada é despachado.

A escada de despacho (`.agents/skills/sdd-build/references/contexto-fresco.md`) lê o slot antes de cada despacho:
- num subagente, passa o modelo quando o agente deixa escolher;
- numa sessão nova, a parada do `sdd-fluxo.sh despachar` diz qual modelo abrir.

## Quanto cada papel custa

A escada marca o papel com `marca-fase.sh inicio|fim papel-<papel> <FEATURE>`. O `custo-feature.sh <FEATURE>` mostra
o papel numa sub-linha `↳ papel <nome> · <modelos>`, logo abaixo das fases, com o número de execuções, os tokens e o
nominal. A sub-linha fica **fora do total**, porque o que ela mostra já está na fase em que o papel rodou. Os modelos
listados vêm do registro da sessão, não da palavra de quem despachou.

## Medir antes de trocar

### 1. O gabarito

O gabarito é uma pasta com um caso por subpasta, tirado do histórico do projeto:

| Arquivo | Conteúdo |
|---|---|
| `caso.txt` | `papel:` (`curador` ou `avaliador`), `commit:` (sha, ou `-` para pasta vazia), `origem:` de onde veio e, opcional, `base:` (a tag ou o commit com que os testes de não regressão comparam: a cópia ganha um commit com essa árvore, marcado com o mesmo nome, antes do caso) |
| `brief.md` | o brief do papel daquela época; `@COPIA@` vira o caminho da cópia do caso |
| `entrada/` | arquivos postos por cima do commit e deixados fora do git, como estavam no projeto (o DEFINE e o DESIGN da época, a colheita do curador…) |
| `esperado.txt` | curador: o delta aceito, na gramática do `playbook-curator.sh --aplicar`. Avaliador: `VEREDITO: <X>` e uma linha `AT-nnn PASS\|FAIL\|NAO_VERIFICADO` por AT |
| `playbook.md` | só no curador: o playbook de antes da curadoria |

Use casos cujo resultado foi confirmado depois: um `NEEDS_WORK` que o ciclo seguinte consertou, um delta que você
aceitou.

### 2. A série

```text
<medição>/teto.txt          teto_pago: 0.00 · teto_nominal: 200.00   (vale para todas as séries da pasta)
<medição>/<série>/serie.txt  papel: avaliador · gabarito: <pasta> · repeticoes: 3
<medição>/<série>/candidatos.tsv   id <TAB> modelo <TAB> cobranca  (1ª linha = a referência, o modelo atual)
```

A `cobranca` é `assinatura`, `pay-per-token` ou `desconhecida`. Para rodar:

```bash
bash sdd/bin/papel-serie.sh <medição>/<série> --cmd '<comando do agente>' [--candidatos id1,id2] [--precos <pasta>]
```

O comando roda por `bash -c`, dentro da cópia do caso, e a saída padrão dele é a resposta do papel. Ele recebe estas
variáveis: `SDD_MODELO`, `SDD_BRIEF` (o arquivo do brief), `SDD_PAPEL`, `SDD_CASO` e `SDD_REP`. Escreve
`"$SDD_MODELO"` sempre entre aspas. Exemplos com a caixa de areia do agente, nunca com as permissões desligadas:

```bash
claude -p --model "$SDD_MODELO" < "$SDD_BRIEF"
codex exec -m "$SDD_MODELO" --sandbox workspace-write - < "$SDD_BRIEF"
```

O `papel-serie.sh`:
- com candidatos, pede ao `papel-medir.sh` que confira a série antes da 1ª chamada: papel sem pontuador, ou caso
  sem o que comparar (sem `esperado.txt`, gabarito do avaliador sem veredito ou sem linha de AT, caso do curador sem
  `playbook.md`), sai 64 e nada é chamado;
- roda **toda a referência primeiro** e confere a referência com o `papel-medir.sh --so-referencia`. Se ela não bate
  a meta, para sem chamar nenhum candidato (exit 22): o gabarito ou a meta está errado;
- **antes de cada chamada**, soma o gasto de todas as séries da pasta de medição e para (exit 20) quando:
  - a próxima execução pode passar do teto (a estimativa é o maior custo de uma execução já gravada);
  - o acumulado tem n/d;
  - outra série da pasta tem execução interrompida com o custo ainda não medido (retome aquela série primeiro);
  - o candidato tem cobrança desconhecida;
  - o candidato é pay-per-token e o teto pago é zero;
- roda cada execução numa **cópia fora do projeto**: `git archive` do commit do caso, commitado, mais `entrada/` fora do commit, num git sem
  remoto. Fotografa o projeto antes e depois: escrita fora da cópia, ou um remoto na cópia, invalida a execução e
  para a série (exit 21), sem apagar nada. Isso cobre o projeto, não o disco inteiro: o resto depende da caixa de
  areia do agente;
- mede o custo de cada execução pelo `custo-feature.sh --execucao <cópia>`, o mesmo leitor e a mesma conta do custo
  por feature.

Para retomar, rode o mesmo comando:
- o que já tem `meta.txt` é pulado;
- a execução interrompida tem o custo somado antes de ser refeita, numa pasta de cópia nova (o registro de sessão
  do agente é por pasta, então a refeita não é cobrada duas vezes);
- o `PARADA.txt` anterior vai para `paradas/`.

Não mexa no projeto enquanto a série roda: a foto de antes e depois veria a sua edição como escrita do agente.

### 3. A escolha

```bash
bash sdd/bin/papel-medir.sh <medição>/<série> [--limiar 30] [--saida <arquivo>]
```

O `papel-medir.sh` só lê. O curador fica na meta quando:
- as contagens `ajudou`/`mordeu` têm precisão e recall de 0,9 ou mais;
- encontra 2 de cada 3 `ADD`, `REFINE` e `TOMBSTONE` esperados;
- o delta proposto passa no `--aplicar`.

Execução cujo comando saiu diferente de 0 (erro, ou o teto de tempo `--teto-s`) fica fora da meta nos dois papéis.

O avaliador fica na meta quando:
- o veredito é igual ao do gabarito;
- 90% ou mais dos ATs têm o mesmo resultado;
- nenhum AT que falha no gabarito é dado como aprovado. Esse é o erro grave: deixar passar defeito.

Ordem do veredito:

| Exit | Resultado | Quando |
|---|---|---|
| 4 | `PARCIAL` | a referência está incompleta ou inválida |
| 3 | `REFERÊNCIA FORA DA META` | a referência está completa, mas não bate a meta |
| 4 | `PARCIAL` | há `PARADA.txt`, candidato pela metade ou execução inválida |
| 0 | `ESCOLHIDO: <id>` | o candidato de menor nominal mediano bate a meta em todas as execuções e custa `--limiar`% ou menos que a referência |
| 1 | `SEM GANHO MEDIDO` | nenhum candidato atende o item anterior |

Candidato com custo n/d nunca é o mais barato. "Sem ganho medido" deixa o slot vazio e não conta como economia.

## Dado de terceiros

O `meta.txt` guarda só números e nomes de modelo. A `saida.txt` guarda a resposta do papel. Se o caso tem dado de
cliente, mantenha a pasta de medição fora do git.
