# Como falar com o aluno — sdd-drive

Quem pede o piloto quer voltar só para decidir. O risco é achar que verde é "no ar", que uma execução longa travou ou
que uma parada é erro. Este arquivo dá as palavras, as 2 perguntas e um exemplo inteiro. O formato de pergunta e de parada é o
de `sdd/templates/fragments/PERGUNTA_DECISAO.md`.

## Glossário (explique na primeira vez em que o termo aparecer)

- drive, piloto — "constrói e confere sozinho até o teste final passar, e para antes de publicar";
- rodada — "uma passada construindo o que falta, mais o teste final";
- teste final (Verify Gate) — "o comando escrito no DEFINE que diz se a feature está pronta";
- frente — "uma cópia de trabalho separada, para não mexer no que está no ar";
- sessão nova — "uma janela nova do seu agente, sem a conversa daqui, para quem faz a tarefa não trazer as hipóteses desta";
- executor — "o agente que faz uma tarefa só e sai";
- relatório do piloto (`DRIVE_REPORT`) — "o que aconteceu em cada rodada, com os commits".

## Status desta skill, preenchido

`Drive: ✅ 1 Conferir · ✅ 2 Desenhar · ▶️ 3 Construir (rodada 1/3 · tarefa 4 de 12) · ⬜ 4 Teste final · ⬜ 5 Relatório`

## A pergunta do limite de rodadas

**Sua decisão** — [D4 · limite de tentativas] **O teste final continuou vermelho nas 3 rodadas. O que falha é o cálculo do relatório mensal. O que eu faço?**
- **corrigir o DESIGN e seguir** (recomendado) — 3 tentativas sem verde sugerem que o desenho está errado, e não a tarefa; eu reviso o DESIGN com você e dou mais 1 rodada.
- **dar mais 1 rodada** — tento de novo sem mudar o desenho; serve se o último conserto chegou perto.
- **parar aqui** — o que está pronto fica nos commits, e nada é publicado.
- **não sei** — mostro o trecho do teste que falha e o que mudou entre as rodadas.

## A pergunta do teste final alterado

**Sua decisão** — [D2 · muda o produto] **O comando do teste final mudou durante a execução: era `npm test` e agora é `npm test -- --bail`. Qual vale?**
- **voltar o comando antigo** (recomendado) — o verde continua significando o teste que você aprovou.
- **aceitar o novo** — continua com o comando novo; a troca fica escrita no relatório.
- **não sei** — explico o que mudou entre os 2 comandos e o que deixaria de ser testado.

## Exemplo de resposta completa

Situação: a segunda rodada terminou verde, os relatórios estão prontos, e o `concluir` saiu `gate-verde`.

**Status** — `Drive: ✅ 1 Conferir · ✅ 2 Desenhar · ✅ 3 Construir · ✅ 4 Teste final · ✅ 5 Relatório`

**O que foi feito** — Construí as 12 tarefas em 2 rodadas: a 1ª ficou vermelha no cálculo do relatório, e a 2ª passou. O
avaliador sem esta conversa aprovou.

**Agora: etapa 5 — Relatório** — O teste final passou e os relatórios estão prontos. Nada foi publicado: isso continua
sendo decisão sua.

**Próximo passo** — Para publicar, peça a `sdd-release`; ela mostra o que sobe e pede o seu OK.
