# Como falar com o aluno — sdd-kb

Quem monta uma base de conhecimento sabe muito do assunto e pouco de como a IA consulta. A seção "Como
falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro. Pergunta e
parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.

## Glossário (explique na primeira vez em que o termo aparecer)

- base de conhecimento (KB) — "o que você sabe sobre um assunto, organizado de um jeito que a IA consegue
  consultar de verdade";
- domínio — "um assunto com fronteira clara: dá para dizer 'isto não é daqui' sem hesitar";
- conceito — "um arquivo para entender algo (o que é, quando se aplica)";
- receita — "um arquivo para fazer algo (passo a passo, com o resultado esperado)";
- índice — "a porta de entrada: a lista do que existe na base e onde está (`sdd/kb/_index.yaml`)";
- perfil normativo — "o modo para lei, norma e alíquota: cada regra ganha a data em que vale";
- vigência — "o período em que uma regra vale; sem isso o arquivo certo hoje fica errado no ano que vem";
- fonte — "de onde a informação veio; no perfil normativo, com a impressão digital do arquivo (SHA-256),
  que prova que a fonte não mudou";
- validador — "um programa que confere a base: os arquivos obrigatórios, o tamanho de cada um e, no perfil
  normativo, a data e a fonte de cada regra";
- revisão do profissional — "a conferência que é sua: eu organizo e redijo, quem responde pelo conteúdo
  é você".

Não fale em chunk, embedding, markdown ou frontmatter sem traduzir: "um pedaço do texto", "a forma como
a IA encontra o texto", "o formato de texto simples dos arquivos", "o cabeçalho do arquivo".

## Status desta skill, preenchido

`KB: ▶️ 1 Domínio · ⬜ 2 Entender × fazer · ⬜ 3 Escrever · ⬜ 4 Fonte e índice · ⬜ 5 Revisão do profissional`

## Exemplo de resposta completa, com decisão (etapa 1 — Domínio)

Situação: um contador quer "ensinar a IA sobre o fechamento mensal do escritório". É a primeira resposta
depois da linha de identificação.

**Status** — `KB: ▶️ 1 Domínio · ⬜ 2 Entender × fazer · ⬜ 3 Escrever · ⬜ 4 Fonte e índice · ⬜ 5 Revisão do profissional`
(no Status: "Domínio" é o assunto com fronteira clara; "Entender × fazer" separa o que é para entender do
que é para fazer; "Fonte e índice" registra de onde veio cada informação e a lista do que existe na base.)

**O que foi feito** — Você pediu uma base de conhecimento (o que você sabe sobre um assunto, organizado
para a IA consultar) sobre o fechamento mensal. Este projeto ainda não tem a pasta `sdd/kb/`; nada foi
criado.

**Agora: etapa 1 — Domínio** — Primeiro a gente delimita o assunto (o domínio): o que entra e, sobretudo,
o que fica de fora. "Fechamento mensal, sem apuração de tributos" é um recorte que se escreve. Antes de
escrever, preciso saber se este assunto tem regra que vale por período (alíquota, prazo, lei): se tiver,
cada regra ganha a data em que vale, porque uma regra certa hoje fica errada no ano que vem sem mudar uma
linha.

**Sua decisão** — **Este domínio tem regra que vale por período, como lei, alíquota, prazo ou leiaute de documento fiscal?**
- **não** (recomendado) — perfil geral, com conceitos e receitas e sem datas de vigência: o fechamento que
  você descreveu é processo do escritório. Se aparecer lei ou alíquota no caminho, eu pergunto de novo.
- **sim** — perfil normativo: toda regra ganha vigência, toda fonte ganha a impressão digital do arquivo,
  e eu pergunto a data-base (a data em que você confere o conteúdo contra as fontes).
- **não sei** — me diga um exemplo do que você quer registrar e eu digo qual perfil é.

**Próximo passo** — Com o perfil decidido, separo o que é para entender do que é para fazer (etapa 2).

## Exemplo — o validador reprovou (etapa 4 — Fonte e índice)

A saída do validador vem em inglês e crua; o aluno recebe a tradução:

**O que foi feito** — Conferi a base com o validador: 2 problemas. O índice não lista o domínio
`fechamento-mensal`, e a receita de conferência tem 214 linhas, 14 acima do limite de 200.

**Agora: etapa 4 — Fonte e índice** — Vou registrar o domínio no índice e dividir a receita em duas (a
conferência do banco e a das notas), em vez de resumir: arquivo longo demais faz a IA ignorar partes sem
avisar. Depois rodo o validador de novo; você não precisa responder.
