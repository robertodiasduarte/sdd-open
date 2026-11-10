# Como falar com o aluno — sdd-release

Quem chega à Release vai autorizar algo que não se desfaz: depois do push, a versão está publicada. A
seção "Como falar com o aluno" do `SKILL.md` dá o formato, e o item 7 da FASE 1 dá o bloco do OK; este
arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- release — "a fase em que o que foi construído é publicado, com um único OK seu";
- push — "o envio das versões salvas para o GitHub; aqui, é o que publica";
- deploy — "a instalação da versão nova no lugar onde as pessoas usam o sistema";
- workflow — "a lista de passos que o GitHub roda sozinho quando recebe um push";
- Verify Gate — "a conferência final combinada no DEFINE: um comando que diz passou ou não passou";
- landmine — "uma armadilha conhecida do projeto, registrada no playbook com um número";
- drift — "uma mudança que chegou em produção sem estar salva no histórico";
- veredito — "o resumo das conferências: PASS (tudo certo), CONCERNS (passou com ressalvas) ou FAIL";
- waiver — "a sua decisão registrada de publicar mesmo com um achado, com o motivo";
- ledger — "o registro, gravado junto com a versão, do que foi publicado e quando";
- migration — "um arquivo que muda a estrutura do banco de dados";
- curadoria — "conferir, depois de publicar, o que esta feature ensinou para as próximas";
- delta — "uma mudança de uma linha no playbook";
- aposentar (tombstone) — "tirar uma lição de uso, guardando o motivo";
- promover — "transformar a lição numa trava automática";
- invariante — "uma regra que nunca pode ser quebrada, com o teste que a vigia".

Não fale em merge, fast-forward, tag ou `--stat` sem traduzir: "juntar na linha principal", "sem
reescrever nada", "o nome da versão", "a lista dos arquivos que mudaram".

## Status desta skill, preenchido

`Release: ✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`

## Exemplo — resposta completa, com decisão (etapa 3 — Sua decisão)

Situação: a conferência de notas está pronta; todas as conferências passaram e o workflow do projeto só
publica depois que os testes passam.

**Status** — `Release: ✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`
(no Status: "Verificar" são as conferências antes de publicar; "Publicar" é o envio e a instalação.)

**O que foi feito** — Juntei as 4 versões salvas desta tarefa numa só e conferi: a conferência final, o
relatório, o lint e o playbook passaram. Nada foi enviado ao GitHub ainda.

**Agora: etapa 3 — Sua decisão** — Os campos abaixo já foram conferidos por mim; você só responde à
última linha. **sim** publica exatamente o descrito; **não** encerra sem publicar.

**O que sobe:** 5 arquivos — 3 novos (`conferir.py`, `exemplo.xml`, `tests/test_conferir.py`) e 2 alterados
(`README.md`, `sdd/playbook.md`).
**O que muda em produção:** a planilha de pagamentos passa a vir marcada com as notas recebidas.
**O push publica sozinho?** sim, o workflow `deploy.yml` publica ao receber o push na `main`.
**O deploy espera os testes?** sim — o job que publica só roda depois do job de testes.
**Banco:** sem migração nesta frente.
**Verificações:** Verify Gate 0 · report-lint ok · lint ok · landmines ok · drift pulado — slot vazio ·
testes do diff ok · smoke pulado — slot vazio
**Veredito:** 🟢 PASS
**Ledger:** `feature_id` conferencia-notas · `estado` shipado

**Posso finalizar (push + deploy + verificar)?**
- **sim** (recomendado) — publico os 5 arquivos acima: as 5 conferências passaram e o veredito é PASS.
- **não** — encerro sem publicar; tudo fica salvo nesta pasta.
- **não sei** — explico cada campo do bloco com o que ele quer dizer neste caso.

**Próximo passo** — Com o seu sim, publico e confiro o deploy; com o não, encerro aqui.

## Exemplo — antes do bloco, quando falta a revisão por outra engine (etapa 2 — Verificar)

Situação: o `adversarial-review.sh --conferir` saiu 2 — esta versão do código não tem revisão por outra
engine. A pergunta vem **antes** do bloco do OK, como uma pergunta própria; o bloco continua com uma só.

**Sua decisão** — [D3 · muda a regra do método] **Esta versão não tem revisão por outra engine. Como seguimos?**
- **rodar agora** (recomendado) — rodo o revisor e o auditor sobre o diff desta frente; leva em geral de 2 a
  15 minutos e mostro o custo no fim.
- **publicar sem revisão** — peço o motivo em uma frase; ele fica no registro da release.
- **não sei** — explico o que a revisão confere, com o último achado dela nesta frente, se houver.

As opções vêm logo depois da última linha do bloco: continua sendo uma pergunta só. Formato completo de
pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.

## Exemplo — o smoke reprovou depois do deploy (etapa 4 — Publicar)

Situação: o deploy está no ar e o comando do slot `smoke.after_deploy_cmd` saiu 2. O código já está em
produção: a pergunta é o que fazer agora, não se publica. Diga o que o smoke viu, nas palavras dele, e onde está
o detalhe (a saída do comando, a pasta que ele cita).

**Sua decisão** — [D1 · não se desfaz] **A conferência depois da publicação achou a página de pedidos pior do que antes. O que fazemos?**
- **reverter** (recomendado) — desfaço a mudança com um commit novo e publico por este mesmo caminho, com o
  seu OK; a produção volta ao que era em alguns minutos.
- **corrigir** — a versão nova fica no ar; volto ao build para consertar, e isto vira pendência na ficha.
- **seguir com motivo** — é um falso alarme (por exemplo, conteúdo que mudou sozinho); peço o motivo em uma
  frase, e ele fica na ficha.
- **não sei** — mostro o que o smoke mediu antes e depois, tela por tela.

## Exemplo — a curadoria, depois de publicar (etapa 4 — Publicar)

Situação: a publicação terminou. A colheita trouxe 2 contagens com prova, 1 lição nova e 1 lição que já
mordeu 2 vezes. Toda mensagem daqui para a frente diz que a publicação já terminou: uma parada depois do
push, sem isso, parece deploy travado.

**Status** — `Release: ✅ 1 Onde estou · ✅ 2 Verificar · ✅ 3 Sua decisão · ▶️ 4 Publicar`

**O que foi feito** — A publicação terminou e está no ar; o que vem agora não mexe nela. Conferi o que
esta feature ensinou para as próximas (a curadoria: as lições do caderno de armadilhas do projeto).

**Decidi sozinho** (contagem com prova não muda regra; para desfazer, reverta o commit da curadoria):
- o aviso sobre o envio sem o segredo foi seguido no desenho e evitou o erro: contei +1;
- o erro do preflight aconteceu de novo, mesmo com o aviso: contei +1.

**Agora: etapa 4 — Publicar** — Duas mudanças nas regras do projeto dependem de você. Responda pelos
números, por exemplo "1 aceitar, 2 recusar".

**Sua decisão** — 1. [D3 · muda a regra do método] **Guardo a lição nova sobre o relatório que saiu sem as notas canceladas?**
- **aceitar** (recomendado) — entra no caderno e avisa toda sessão que mexer no relatório; a prova está
  no relatório do build (ref: LM-023).
- **recusar** — a lição não entra; o que aconteceu fica só no histórico desta feature.
- **não sei** — mostro o trecho do relatório do build em que isso aconteceu.

**Sua decisão** — 2. [D3 · muda a regra do método] **Transformo em trava automática o aviso que já falhou 2 vezes?**
- **aceitar** (recomendado) — registro que ele vira uma conferência automática; isso pede uma correção
  própria, com teste, numa próxima tarefa (ref: LM-004).
- **recusar** — o aviso continua só escrito, e esta pergunta volta na próxima publicação.
- **não sei** — mostro as 2 vezes em que o erro aconteceu, com o arquivo de cada uma.

**Próximo passo** — Aplico só o que você aceitar, confiro o caderno e pergunto se envio essa mudança.

Aposentar uma lição da qual uma regra permanente depende é **uma opção só**, nunca duas: "aposentar o
aviso sobre o envio e ajustar a regra permanente que dependia dele, no mesmo passo".

Depois de aplicar, o envio é outra decisão, porque o push pode publicar:

**Sua decisão** — [D1 · não se desfaz] **Posso enviar o commit da curadoria para a branch padrão?**
- **sim** (recomendado) — envio só o caderno de armadilhas e os registros desta conferência; neste projeto,
  esse push não publica nada, porque o workflow só roda quando o código muda.
- **deixar para a próxima publicação** — a mudança fica salva nesta pasta e sobe junto com a próxima.
- **não sei** — explico o que este envio muda e o que acontece se ele ficar para depois.

Quando a colheita falha, diga a causa, o conserto e que nada do que foi publicado mudou: "Não consegui
ler o caderno de armadilhas para a curadoria (o arquivo `sdd/playbook.md` não tem nenhuma lição no
formato esperado). A publicação não foi afetada. Corrija o arquivo e me peça a curadoria de novo." Quando
não há o que colher: "esta feature não trouxe lição nova nem contagem".
