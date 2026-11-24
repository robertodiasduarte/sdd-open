# Disciplina de teste — vermelho antes do verde, sabotagem e refatorar

Três práticas que fazem o teste provar alguma coisa. Valem para cada tarefa do Build, nesta ordem: o vermelho antes
de escrever o código, o verde depois, a refatoração com o verde mantido e, no fim, a sabotagem que confere que o teste
pega o defeito.

## 1. Vermelho antes do verde

Um teste que já passa antes do código existir não prova o código. Por isso, antes de escrever o código de um critério
de aceite (AT), rode o comando dele e veja falhar:

1. escreva (ou ajuste) o teste do AT primeiro;
2. rode o comando do AT e grave a saída em `sdd/reports/evidence/{F}/AT-nnn.antes.log`, no mesmo formato da evidência:
   1ª linha `$ <comando>`, a saída, e `[exit=<n>]` no fim;
3. confira que ele falhou **avaliando**: uma asserção que não bate, ou o módulo novo que ainda não existe. Exit 126 ou
   127 (comando não encontrado, sem permissão) não conta: a ferramenta nem rodou;
4. escreva o código e rode **o mesmo comando** de novo: agora verde, em `AT-nnn.log`.

Quando o teste falha por um defeito do próprio teste (erro de digitação, fixture quebrada), conserte o teste e grave o
antes de novo: o vermelho que vale é o que mede a falta do comportamento.

Os dois casos à parte:

- **`shall continue to`** (não-regressão): o comportamento já existe, então o antes é **verde**, com o mesmo comando.
  É a prova de que a mudança não quebrou o que funcionava.
- **Assinatura humana** (gate `manual-ux`, exit 4) e gate de outro tipo que não `test`/`cmd` (smoke, eval): não há
  comando a rodar antes; a coluna `Antes` do relatório diz `N.A. (<motivo>)`.

No BUILD_REPORT, a tabela de critérios tem a coluna `Antes`, com o `AT-nnn.antes.log` de cada AT de comportamento novo.

## 2. Sabotagem: o teste pega o defeito?

Um teste verde ainda pode ser fraco: passa com o código certo e também com o errado. A sabotagem confere isso
estragando de propósito o trecho que o AT protege, numa **cópia descartável** do último commit, e esperando vermelho.

- **Quem escolhe a sabotagem é o DESIGN**, na tabela de sabotagens da estratégia de testes: uma por AT de superfície
  de risco (dado, dinheiro, acesso, publicação, disponibilidade, o mesmo critério do `CRITERIO_DANO.md` da revisão) e
  pelo menos uma por feature. Declarada antes, o construtor não escolhe a sabotagem fácil.
- **Cada linha** diz o AT, o arquivo, o trecho a trocar (que aparece exatamente 1 vez) e o que entra no lugar.
- **A cópia** é o último commit extraído numa pasta temporária; a pasta de trabalho fica como estava, e a cópia é
  apagada no fim. Commite antes de sabotar.
- **Resultado:** vermelho com a sabotagem é o teste pegando o defeito, e o log vai para
  `sdd/reports/evidence/{F}/AT-nnn.sabotagem.log`; verde com a sabotagem é teste fraco: reforce a asserção, como
  falha da tarefa.

No SDD Open com o `init`, o script de sabotagem do SDD Open faz a cópia, confere que o comando passa sem a sabotagem e
grava o log.

## 3. Refatorar depois do verde

Com o teste, o lint e os tipos verdes, melhore a forma **só dos arquivos da tarefa**, pelas regras do catálogo de
qualidade: nome que diz o que a coisa é, duplicação dentro dos arquivos, função que faz mais de uma coisa. Depois rode
de novo o teste do arquivo, o lint e os tipos: a refatoração só fica se tudo continuar verde; vermelho, desfaça-a.

O código vizinho que a tarefa não tocou fica como está: a mudança continua cirúrgica.

O passo vem ligado. Para economizar tokens, `build.refatorar: false` no `sdd/config.yaml` o pula, e o BUILD_REPORT diz
isso numa linha própria: `refatorar: desligado`.
