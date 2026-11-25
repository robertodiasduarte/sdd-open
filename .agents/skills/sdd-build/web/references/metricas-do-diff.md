# Métricas do diff — complexidade e duplicação, só aviso

Depois do teste verde, duas medidas dizem se o código novo ficou difícil de manter. Elas olham só o que a frente trouxe
(funções novas ou alteradas e trechos novos que repetem outro trecho do projeto). A métrica **só avisa**: o Build segue
com ou sem achado, e quem decide o que refatorar é a pessoa.

| Medida | Ferramenta | Avisa quando (chave em `qualidade`, no `sdd/config.yaml`) | Instalar (a pessoa roda, se quiser) |
|---|---|---|---|
| Complexidade: quantos caminhos a função tem | `lizard` | mais de 10 caminhos (`max_complexidade`), 60 linhas (`max_linhas`) ou 5 parâmetros (`max_parametros`) | `python3 -m pip install lizard` |
| Duplicação: o mesmo trecho em dois lugares | `jscpd` | 50 ou mais tokens iguais (`min_tokens`); token é cada palavra ou símbolo do código | `npm install -g jscpd` |

## Como medir

Com o SDD Open instalado pelo `init`, o script de métricas do SDD Open mede as duas e imprime a seção pronta. Sem ele,
com terminal: rode `lizard --csv <arquivos novos ou alterados>` e fique com as funções que a frente tocou; rode
`jscpd . --min-tokens 50 --min-lines 0` e fique com os pares em que um dos lados é da frente. Sem terminal, as duas medidas ficam
como não medido.

## A seção do BUILD_REPORT

`## Qualidade (avisos)`, com `### Complexidade` e `### Duplicação`. Cada uma termina num destes três estados:

- **a lista** dos avisos: arquivo e linhas, o valor e o limite;
- **nenhum aviso**, com quantas funções ou arquivos foram medidos;
- **não medido**, com a causa e o comando de instalar: `não medido: lizard ausente`. Ferramenta ausente, que falhou ou
  que devolveu saída estranha é sempre não medido: sem medida, o número de avisos é desconhecido.

Um comentário no código desliga a medida daquele trecho (`#lizard forgives`, `jscpd:ignore-start`): ao ver um no código
novo, conte à pessoa, porque a seção não o mostra.

## Como falar com a pessoa

Uma frase por medida. Com aviso: o que foi achado, onde e o que melhora se refatorar ("a função `fechar_mes` tem 15
caminhos; dividida em três, fica mais fácil de testar"). Um par repetido costuma ser uma função que já existia: ofereça
reusar a antiga. Com não medido: diga a ferramenta que falta e o comando, e siga; instalar é escolha da pessoa.
