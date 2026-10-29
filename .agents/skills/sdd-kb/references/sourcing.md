# Procedência: de onde veio o que está escrito

Referência de apoio da skill `sdd-kb`.

---

## O problema

Uma base de conhecimento é consultada justamente quando a pessoa **não sabe** — ou seja, no momento em que ela não tem como perceber que a informação está errada. Um erro num KB não é um erro isolado: ele é repetido com confiança, por você e pela IA, até alguém tropeçar nele na prática.

Por isso a procedência não é formalidade acadêmica. É o que permite verificar depois.

---

## As três origens

Todo conteúdo de KB vem de uma destas três, e cada uma se declara de um jeito:

| Origem | Como declarar | Cuidado |
|---|---|---|
| **Documentação oficial / norma** | Nome do documento e, quando houver, a versão ou data | Documentação muda. Registre a data em que você leu |
| **Prática própria** | "Prática do escritório", "como fazemos desde X" | É fonte legítima. Não disfarce de norma o que é hábito |
| **Terceiro** (curso, artigo, colega) | Diga qual, e se você confirmou | Sem confirmar, é ponto de partida, não conclusão |

---

## Em norma, a origem tem degrau

Em domínio normativo (`perfil: normativo`), "documentação oficial" é largo demais: a Emenda Constitucional e o artigo de blog não podem cair no mesmo balde. A escada, do degrau mais forte ao mais fraco:

| Degrau | O que entra |
|---|---|
| `constituicao` | Constituição e emendas constitucionais |
| `lei-complementar` | leis complementares |
| `lei-ordinaria` | leis ordinárias e medidas provisórias |
| `decreto` | decretos e regulamentos |
| `ato-normativo` | resoluções (inclusive CGSN), instruções normativas, portarias |
| `ato-tecnico` | notas técnicas, informes técnicos, manuais oficiais, atos conjuntos |
| `solucao-de-consulta` | respostas da administração tributária a consulta formal |
| `doutrina` | artigo, livro, curso, reportagem, parecer de terceiro |
| `pratica-propria` | o que o escritório faz e já verificou na prática |

Duas regras derivam da escada:

1. **Conflito se resolve citando os dois degraus, não escolhendo em silêncio.** Registre o conflito; diga o que a base adota e por quê.
2. **Regra sustentada só por `doutrina` ou `pratica-propria` não é `confirmado`.** É `nao-confirmado` até alguém achar o texto normativo — o validador reprova o contrário.

E uma que vale sempre: **a data do arquivo e o nome não provam vigência.** Um PDF chamado `nt-2025.002-v1.51.pdf`, baixado ontem, pode ser a versão de três meses atrás. O que prova qual texto foi lido é a versão declarada, a data de captura e o SHA-256 do arquivo — por isso eles moram no `fontes/CATALOGO.md`. Detalhes em [normativo.md](normativo.md).

---

## Marcar o que não foi verificado

Quando você escreve algo de que não tem certeza, **escreva junto que não tem certeza**. Uma frase basta:

> O prazo parece ser até o dia 10, mas não confirmei na norma — verificar antes de usar como referência.

Isso vale mais do que parece. Quem consultar depois — inclusive você, meses depois — vai saber exatamente onde pisar com cuidado. E a IA, ao consultar, tende a repassar a ressalva em vez de afirmar com confiança falsa.

O oposto é o cenário caro: a suposição escrita como fato. Ela não se distingue do resto e se propaga.

---

## O que não colocar no KB

- **Cópia de documentação pública.** O KB é o que **você aprendeu** sobre aquilo — o que confunde, o que dá errado, o que a documentação não diz. Se é só cópia, aponte para o original.
- **Dados de pessoas reais.** Nomes, documentos, telefones, e-mails, valores identificáveis. Exemplos são melhores fictícios: funcionam igual e não vazam nada.
- **Segredos.** Senhas, chaves, tokens. Um KB tende a ser compartilhado.
- **O que muda toda semana.** Se a informação tem validade curta, o KB vai estar errado na maior parte do tempo. Guarde o critério, não o valor volátil. (Valor que muda em datas conhecidas — alíquota, tabela, prazo — é outra coisa: use o perfil normativo, com vigência.)

---

## Manter atualizado

Cada arquivo tem uma data de revisão no topo. Ela responde a uma pergunta simples de quem consulta: "isto ainda vale?".

Quando você descobrir que algo mudou, corrija o arquivo **e** a data. Quando descobrir que algo estava errado, corrija e — se o erro chegou a orientar alguma decisão — vale registrar o que era, para que ninguém reintroduza a versão antiga por lembrança.
