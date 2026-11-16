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
- curadoria — "conferir o que esta feature ensinou para as próximas"; aqui só se colhe, e o julgamento vem
  depois, num lote;
- colheita — "a lista, feita por um script, do que esta feature ensinou: avisos que ajudaram, erros que se
  repetiram, lições novas";
- fila da curadoria — "a pasta onde as colheitas esperam o lote que as julga";
- commit de papel — "a versão salva só com documentos (a ficha, o changelog, a colheita), depois do deploy";
- ficha — "o arquivo da feature que diz o que já foi publicado e o que falta".

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
**O commit de papel publica?** não — o workflow ignora `sdd/**` e os `.md`, então a ficha e o changelog sobem sem
novo deploy.
**Banco:** sem migração nesta frente.
**Verificações:** Verify Gate 0 · report-lint ok · lint ok · landmines ok · drift pulado — slot vazio ·
testes do diff ok · smoke pulado — slot vazio
**Veredito:** 🟢 PASS
**Ledger:** `feature_id` conferencia-notas · `estado` shipado

**Posso finalizar (push + deploy + verificar + papel)?**
- **sim** (recomendado) — publico os 5 arquivos acima e, depois do deploy, envio o commit de papel: as 5
  conferências passaram e o veredito é PASS.
- **não** — encerro sem publicar; tudo fica salvo nesta pasta.
- **não sei** — explico cada campo do bloco com o que ele quer dizer neste caso.

**Próximo passo** — Com o seu sim, publico, confiro o deploy e envio o papel; com o não, encerro aqui.

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

## Depois do push — o que é cada etapa

Ao entrar na parte depois do push, diga **uma frase por etapa**: a coluna "Para que serve", e se é agora ou pode
esperar. A linha inteira, com "Sem ela", só quando a pessoa pedir ou responder "não sei". Nunca o número do passo.

| Etapa | Para que serve | Sem ela | Agora ou pode esperar |
|---|---|---|---|
| **Smoke antes do push** | tira uma foto de como o sistema está antes da versão nova, para comparar depois | não dá para dizer se algo piorou por causa desta versão | agora; nunca segura o envio |
| **Push** | envia a versão aprovada para o GitHub; em muitos projetos, é o que publica | nada chega a quem usa o sistema | agora: é o que você aprovou |
| **Deploy** | instala a versão nova onde as pessoas usam o sistema | o código fica no GitHub, mas ninguém o usa | agora |
| **Verificar** | confere que a versão no ar é exatamente a sua e que ela responde | um deploy que falhou parece pronto | agora; é a única etapa que pode pedir uma decisão sua |
| **Changelog** | escreve em uma frase o que mudou nesta versão | quem usa não fica sabendo o que mudou | agora; sobe junto com o papel |
| **Limpeza** | apaga a cópia temporária usada para juntar a versão | a pasta temporária fica ocupando espaço | agora; não muda nada publicado |
| **Colheita** | guarda o que esta feature ensinou, para ser julgado depois, junto com outras | a lição se perde quando a pasta da frente for apagada | colher é agora; julgar pode esperar o lote |
| **Ficha** | anota o que falta e os alertas; o que foi publicado sai do registro sozinho | a próxima sessão não sabe onde parou | agora |
| **Arquivamento** | guarda numa pasta à parte os documentos da feature que terminou | a pasta de trabalho fica cheia de feature encerrada | agora, só quando a feature terminou; se desfaz com um comando |
| **Commit de papel** | salva e envia, numa versão só, a ficha, o changelog, a colheita e o arquivamento | os documentos ficam só neste computador | agora; o seu sim já cobriu este envio |
| **Branch da frente** | apaga no GitHub a linha de trabalho que já entrou na principal | o GitHub acumula linhas de trabalho que ninguém usa | agora, só se já entrou na principal; se desfaz com um comando |
| **Relatório final** | resume o que foi publicado, o que fiz sozinho e como desfazer | você teria de abrir arquivo por arquivo | agora |

Exemplo da frase de abertura, no fluxo normal: "A publicação foi aprovada. Agora envio a versão (é o que publica),
confiro que ela está no ar e, depois, só papel: guardo a lição desta feature para julgar mais tarde, anoto o que falta
e salvo tudo numa versão só. Só paro se a conferência depois de publicar achar algo pior do que antes."

Quando a colheita falha, diga a causa, o conserto e que nada do que foi publicado mudou: "Não consegui
ler o caderno de armadilhas para guardar a lição desta feature (o arquivo `sdd/playbook.md` não tem nenhuma lição no
formato esperado). A publicação não foi afetada. A colheita ficou marcada na fila, e a próxima publicação colhe de
novo." Quando não há o que colher: "esta feature não trouxe lição nova nem contagem". Quando a fila passa de 5: uma
frase, sem pergunta: "Há 7 publicações esperando o julgamento das lições; quando puder, peça o lote da curadoria."

## Versão nova do SDD Open (FASE 0, item 0)

O `bash sdd/bin/versao-nova.sh` saiu 10: diga uma frase, com as 2 versões da linha que ele imprimiu, no relatório da
FASE 0 e no bloco do OK, e siga. Nunca é pergunta, nunca para nem muda o OK:

"Saiu a versão v2.18.0 do SDD Open (este projeto está na v2.17.0). Não precisa parar agora; quando quiser, peça ao
agente para atualizar."

Qualquer outro exit (em dia, sem rede, desligada) ou o script ausente: não diga nada sobre versão.
