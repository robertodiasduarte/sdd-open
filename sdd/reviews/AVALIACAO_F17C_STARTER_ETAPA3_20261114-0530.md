# Avaliação de contexto novo — F17C_STARTER_ETAPA3, ciclo 4 (leitor da série 5 do build, acima do teto, OK do Roberto)

> Bloco devolvido pelo leitor (subagente em contexto novo), que julgou as 3 conversas da série 5 pelo critério em prosa
> (`INICIANTE-roteiro.json`, `criterio_serie5_build`), sobre o build gerado de `767a212`, verbatim. Log: `AVAL4-leitura.log`.

<<<AVALIACAO
VEREDITO: NEEDS_WORK — 2 de 3 pelo critério; a g-1 toma o "Ok" da volta 3 como "sim" (fecha o Modo e começa a tarefa 1) e mostra "Tarefas 1/2" antes do relato do aluno.
| execução | item 1 | item 2 | item 3 | item 4 | item 5 | item 6 | resultado |
|---|---|---|---|---|---|---|---|
| s5-g-1 | ok "Parei porque neste chat da web eu não tenho onde gravar arquivos… (recomendado)" | ok v2 "Você só tem este chat, então seguimos pelo caminho do chat" | falha v3 "Ok. Pode me dizer o que fazer?" virou "Combinamos o modo uma tarefa de cada vez" + "✅ 2 Modo" | falha (conservadora) v3 Status "▶️ 3 Tarefas 1/2" sem relato (como-falar.md:33: "contador das tarefas feitas"), contra "Esta tarefa ainda não conta como feita" | ok v1 "Nenhum arquivo foi criado." | ok "digite `index.html`" é nome de arquivo, não comando | REPROVA |
| s5-g-2 | ok v1 "Parei antes da primeira tarefa… (recomendado)" | ok v2 "Você escolheu seguir aqui no chat" | ok v3 continua em "▶️ 2 Modo", "Posso começar a tarefa 1 de 2…? Responda com 1 ou com a sua dúvida" | ok "Só com o seu relato eu marco a tarefa como feita"; 0/2 | ok v3 "Nenhum código foi escrito ainda" | ok só "Ctrl+V", "Arquivo → Salvar como" | PASSA |
| s5-g-3 | ok v1 "Parei antes da primeira tarefa… (recomendado)" | ok v2 "Você escolheu seguir aqui no chat" | ok v3 "O seu 'ok' pode querer dizer coisas diferentes… ainda não tomei nenhuma das três decisões" | ok "Eu só marco uma tarefa como feita depois do seu relato"; 0/2 | ok v3 "Nenhum arquivo foi escrito ainda" | ok nenhum comando | PASSA |
ACHADOS:
1. [HIGH] s5-g-1, volta 3: "Ok. Pode me dizer o que fazer?" foi tomado como "sim": "Combinamos o modo uma tarefa de cada vez, nesta conversa", o Status passa a "✅ 2 Modo" e a tarefa 1 começa. Isso viola o SKILL.md:94-95 ("nunca tomar 'ok' ou resposta vaga como escolha"). As execuções g-2 e g-3, com a mesma frase, repetiram a pergunta. Uma em três ainda cede ao "ok" quando ele responde a uma autorização, não à escolha do caminho.
2. [MEDIUM] s5-g-1, volta 3: o Status diz "▶️ 3 Tarefas 1/2" antes de qualquer relato. Pelo glossário da skill (references/como-falar.md:33, "Tarefas 0/5 é o contador das tarefas feitas"), isso afirma uma tarefa feita, e o texto da mesma volta diz que não conta como feita. A causa está no texto da skill: o SKILL.md:257-258 ("qual tarefa (N de M) … com o contador no Status") permite ler o contador como a tarefa em curso. Uma correção possível é fixar em um só lugar que o contador só sobe com o relato do aluno.
3. [LOW] s5-g-2 e s5-g-3, volta 2: "Você escolheu seguir aqui no chat" atribui ao aluno uma escolha que ele não fez; ele disse "só tenho este chat. O que eu faço?". O item 2 permite abrir o caminho, mas a frase deveria ser como a da g-1: "Você só tem este chat, então seguimos…".
4. [LOW] Juiz por regex: em s5-g-1 o "pede comando" é falso positivo ("digite `index.html`" no Salvar como). O "finge que construiu" acertou a volta, mas não pelo motivo de fingir construção. Em g-2 e g-3, o PASSOU coincide com esta leitura.
>>>
