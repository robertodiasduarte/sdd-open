# Como falar com o aluno — sdd-build

Quem chega ao Build vai ver o sistema sendo construído e não sabe o que esperar da tela. A seção "Como
falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e dois exemplos inteiros.

## Glossário (explique na primeira vez em que o termo aparecer)

- build — "a fase em que o que foi desenhado é construído de verdade, arquivo por arquivo";
- plano — "a lista de tarefas, na ordem em que uma depende da outra";
- tarefa — "cada arquivo da lista do design, criado ou alterado, com uma conferência no fim";
- modo de execução — "como as tarefas rodam: uma a uma nesta conversa (default), cada uma numa conversa
  limpa (ralph), ou várias ao mesmo tempo (briefs)";
- drift — "quando o que precisa ser construído se afasta do que foi desenhado; eu paro e pergunto";
- verificação incremental — "a conferência feita logo depois de cada tarefa, antes de ir para a próxima";
- Verify Gate — "a conferência final combinada no DEFINE: um comando que roda e diz passou ou não passou;
  sem passar, o build não termina";
- migration — "um arquivo que muda a estrutura do banco de dados; precisa ser aplicado no banco e
  provado por leitura";
- relatório (BUILD_REPORT) — "o documento desta fase, com a prova de cada conferência".

Não fale em exit code, retry ladder, typecheck ou commit sem traduzir: "o resultado do comando (passou
ou falhou)", "as tentativas de correção", "a conferência dos tipos", "uma versão salva".

## Status desta skill, preenchido

`Build: ✅ 1 Plano · ▶️ 2 Modo · ⬜ 3 Tarefas 0/5 · ⬜ 4 Verify Gate · ⬜ 5 Relatório`

## Exemplo 1 — resposta completa, com decisão (etapa 2 — Modo)

Situação: os três documentos foram lidos, o plano tem 5 tarefas e o aluno precisa escolher o modo.

**Status** — `Build: ✅ 1 Plano · ▶️ 2 Modo · ⬜ 3 Tarefas 0/5 · ⬜ 4 Verify Gate · ⬜ 5 Relatório`
(no Status: "Tarefas 0/5" é o contador das tarefas feitas, que só sobe quando a tarefa termina; "Verify Gate" é a conferência final combinada
no DEFINE, um comando que diz passou ou não passou; "Relatório" é o documento com a prova de cada
conferência.)

**O que foi feito** — Li o brainstorm, o DEFINE e o DESIGN e conferi a pasta do projeto: os 5 arquivos da
lista do design existem ou têm onde ser criados. Montei o plano — a lista das 5 tarefas, na ordem em que
uma depende da outra. Nenhum arquivo foi alterado.

**Agora: etapa 2 — Modo** — Antes de alterar qualquer arquivo, você escolhe como as tarefas rodam (o modo
de execução). Para este caso eu recomendo rodar uma de cada vez nesta conversa: são 5 arquivos que
dependem uns dos outros e assim eu mantenho tudo na cabeça. Nada vai para a internet em nenhum dos modos;
cada tarefa termina com uma conferência.

**Sua decisão** — [auto · de rotina] **Como as tarefas devem rodar?**
- **default** (recomendado) — uma tarefa de cada vez, nesta conversa; eu aviso antes de cada uma e volto
  com o resultado.
- **ralph** — cada tarefa numa conversa limpa; mais isolamento, um pouco mais lento, e eu te mostro o
  resultado de cada uma do mesmo jeito.
- **briefs** — várias tarefas ao mesmo tempo; não está disponível neste ambiente, então eu seguiria no
  default.
- **não sei** — eu explico a diferença com a tarefa 1 como exemplo.

**Próximo passo** — Com o modo escolhido, começo a tarefa 1 de 5 e te aviso antes de cada uma.

## Exemplo 2 — resposta sem decisão, antes de trabalho demorado (etapa 3 — Tarefas)

Situação: o aluno escolheu o modo default; a tarefa 1 terminou e a tarefa 2 vai começar.

**Status** — `Build: ✅ 1 Plano · ✅ 2 Modo · ▶️ 3 Tarefas 2/5 · ⬜ 4 Verify Gate · ⬜ 5 Relatório`

**O que foi feito** — Você escolheu o modo **default**. Tarefa 1 de 5 concluída: o leitor de PDFs que já
existia passou a devolver o número da nota e o CNPJ; a conferência dessa tarefa rodou e passou (12 PDFs
da amostra lidos, 0 erros).

**Agora: etapa 3 — Tarefas 2/5** — Vou construir o arquivo que monta a planilha a partir do que o leitor
devolve. Isso leva alguns minutos: vou escrever o arquivo e rodar a conferência dele. Você não precisa
responder nada agora; eu volto quando a tarefa terminar, com o resultado. Nenhum arquivo seu é alterado —
só os previstos na lista do design.

**Próximo passo** — Tarefa 2 concluída e conferida ⇒ tarefa 3 (marcar duplicidades). Se a conferência
falhar, eu mostro o que falhou e as opções.
