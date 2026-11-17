# Fixtures do modelo por papel (F23B2)

Dados inventados para `tests/test_f23b2_papeis.py`. Nenhum é sessão, curadoria ou avaliação real, e nenhum nome
é de modelo de verdade (`modelo-caro`, `modelo-medio`, `modelo-barato`).

- `agente-falso.sh`: faz o papel do agente no `papel-serie.sh`. Anota a chamada em `$FALSO_LOG`, grava uma sessão só
  com números na pasta que o leitor do Claude Code deriva da cópia (1.000 tokens de entrada e 100.000 de saída) e
  imprime a resposta de `respostas/<modelo>/<caso>.txt`. `FALSO_MODO` liga os desvios: `grava-projeto` (escreve no
  projeto), `remoto` (põe um remoto git na cópia), `dorme` (passa do teto de tempo), `sem-sessao` (não grava sessão), `sessao-e-dorme` (grava a sessão,
  anota o PID em `$FALSO_PID` e fica parado até ser morto). Cada chamada grava um arquivo de sessão próprio, como o
  agente de verdade. `FALSO_SAI=<modelo>` faz o agente responder e sair 1 nesse modelo.
- `precos/`: tarifas inventadas (US$ por milhão de tokens). Uma execução custa 1,001 no `modelo-caro`, 0,801 no
  `modelo-medio` e 0,2005 no `modelo-barato`.
- `gabarito/c1` (curador): o delta aceito tem 2 contagens e 1 `ADD`; `playbook.md` é o de antes.
- `gabarito/a1` (avaliador): `NEEDS_WORK`, com o AT-002 falhando.
- `respostas/`: o caro e o médio acertam o avaliador; o barato dá o AT-002 como aprovado (o erro grave). No curador,
  o caro e o barato acertam; o médio descarta o `ADD`.
