# Critério de dano — quando um achado da revisão conta como falha real

> Lido por quem decide os achados da revisão adversarial (passo 5c da `sdd-build`, item 8 da 0a da
> `sdd-release`). É o dono único do critério: o ledger da revisão (`sdd/reviews/LEDGER_REVISAO_{F}.md`,
> molde em `sdd/templates/LEDGER_REVISAO_TEMPLATE.md`) guarda a marca, o `sdd/bin/ledger-revisao-lint.sh`
> confere a forma e o `sdd/bin/eval-revisores.sh` conta.

## Por que existe

"O revisor achou 12 coisas" não diz se a revisão valeu o que custou. O que interessa é quantas dessas
coisas eram **falha real que causaria dano** se fossem para produção. Sem critério escrito, cada frente
conta de um jeito, e a comparação entre engines vira impressão.

## A regra

Um achado é **falha com dano** (`dano` = `sim`) quando as três coisas são verdade:

1. **Foi aplicado.** O veredito dele no ledger é `APLICADA`: alguém mudou o código, o texto ou o teste
   por causa do achado.
2. **Há um teste que falha no código antigo.** O conserto veio com um teste (ou o achado apontou um
   teste que já existia e passou a falhar) que fica vermelho sem o conserto. O nome do teste vai na
   evidência, na forma `teste: <nome>`.
3. **O cenário afeta um destes cinco:**
   - **dado** — grava, apaga, mistura ou mostra dado errado (o relatório soma duas vezes; a exportação
     traz linha de outro cliente);
   - **dinheiro** — valor cobrado, pago, calculado ou informado errado;
   - **acesso** — alguém vê ou faz o que não podia, ou quem podia fica de fora;
   - **publicação** — vai para produção, para o pacote ou para o usuário algo que não devia ir (arquivo
     a mais, versão errada, publicação com o gate vermelho);
   - **disponibilidade** — o sistema cai, trava ou deixa de responder num caminho que as pessoas usam.

Faltou uma das três, a marca é `nao`.

## Os três valores

| `dano` | Quando | O lint exige |
|---|---|---|
| `sim` | as três condições acima | veredito `APLICADA` e `teste: <nome>` na evidência |
| `nao` | achado rebatido (com evidência ou por escopo), ou aplicado sem teste que falhe, ou aplicado em algo que não afeta nenhum dos cinco (texto de ajuda, comentário, nome) | — |
| `?` | **só no retroativo**: ledger de frente antiga, convertido depois, em que ninguém julgou o dano na hora | a linha `retroativo: sim` no topo do arquivo |

## Quem marca

Quem **decide o achado**: a pessoa, ou o agente que conduz a frente, na hora em que aplica ou rebate.
Nunca outro modelo chamado só para classificar: um modelo julgando o achado de outro modelo repete o
viés que a medida quer enxergar. Na dúvida entre `sim` e `nao`, a marca é `nao` e a evidência diz o
motivo da dúvida; inflar o número de falhas com dano engana quem vai escolher a cadeia de revisão.

## O que a medida chama de falso positivo

O achado com veredito `REBATIDA_EVIDENCIA`: o revisor (ou o auditor, num achado `NOVO`) afirmou um
defeito, e uma medição ou um `arquivo:linha` mostrou que não existe. `REBATIDA_ESCOPO` **não** é falso
positivo: o achado pode ser verdadeiro, só não é desta frente.

## Exemplos

| Achado | Veredito | `dano` | Por quê |
|---|---|---|---|
| o total do mês somava o estorno duas vezes; `teste: test_soma_do_mes` | `APLICADA` | `sim` | aplicado, com teste, afeta dado |
| a publicação seguia com o gate vermelho; `teste: test_publica_so_com_gate_verde` | `APLICADA` | `sim` | aplicado, com teste, afeta publicação |
| mensagem de erro sem a causa | `APLICADA` | `nao` | aplicado, mas não afeta nenhum dos cinco |
| condição de corrida num caminho real, consertada sem teste que a reproduza | `APLICADA` | `nao` | sem teste que falhe no código antigo; diga isso na evidência |
| "o comando sai 0 com erro" — medido: sai 64 | `REBATIDA_EVIDENCIA` | `nao` | falso positivo |
| melhoria de nome de variável | `REBATIDA_ESCOPO` | `nao` | fora desta frente |

## Limites

- A medida conta o que foi registrado. Achado que ninguém pôs no ledger aparece como "sem classificar".
- Poucas rodadas dão número instável: leia cada taxa com a amostra que o `eval-revisores.sh` põe ao lado.
- Um revisor que acha pouco numa frente pequena não é pior que um que acha muito numa frente grande:
  compare engines no mesmo papel e, de preferência, nas mesmas rodadas.
