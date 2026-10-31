# Como falar com o aluno — sdd-handoff

Quem pede um handoff costuma estar sem tempo ou sem contexto: vai parar e quer retomar depois sem perder
nada. A seção "Como falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um
exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- handoff — "o registro do que ficou pronto e do que falta, para a próxima conversa continuar sem
  depender desta";
- família da feature — "o assunto a que este trabalho pertence; uma ficha por assunto, com cada etapa
  nova no topo";
- ficha — "a tabela no topo do arquivo: objetivo, status, o que foi feito, o que falta, a conferência";
- slice — "um pedaço entregue da feature; cada um vira uma entrada datada no histórico da ficha";
- Definition of Done — "a lista do que precisa estar verdade para a feature contar como pronta";
- prompt de retomada — "o texto pronto para colar na próxima conversa, que funciona sozinho";
- ledger — "o registro, gravado na release, do que foi publicado e quando";
- worktree — "a pasta separada desta tarefa, que pode ser apagada quando ela termina";
- HANDOFF — "o documento desta skill, um por assunto".

Não fale em contexto, branch ou SHA sem traduzir: "o que esta conversa sabe", "a linha de versões
desta tarefa", "o código da versão salva".

## Status desta skill, preenchido

`Handoff: ✅ 1 Família · ✅ 2 Estado · ✅ 3 Ficha · ✅ 4 Prompt de retomada · ▶️ 5 Limpeza`

## Exemplo — resposta completa, com decisão (etapa 5 — Limpeza)

Situação: a feature de conferência de notas foi publicada; a ficha e o prompt estão gravados e a
conferência automática da ficha passou.

**Status** — `Handoff: ✅ 1 Família · ✅ 2 Estado · ✅ 3 Ficha · ✅ 4 Prompt de retomada · ▶️ 5 Limpeza`
(no Status: "Família" é o assunto da ficha; "Prompt de retomada" é o texto pronto para a próxima
conversa.)

**O que foi feito** — Atualizei a ficha que já existia para este assunto (não criei outra): 3 itens
feitos, 1 pendente (a nota que chega sem XML) e o prompt de retomada com os comandos colados. A
conferência automática da ficha passou.

**Agora: etapa 5 — Limpeza** — A feature já está publicada, então a pasta separada desta tarefa (a
worktree) não é mais necessária. Apagar a pasta não apaga nada do que foi publicado.

**Sua decisão** — [D1 · não se desfaz] **Posso te dar o comando para remover a pasta desta tarefa?**
- **sim** (recomendado) — mostro 1 comando, para rodar de fora desta pasta; tudo já está na versão
  publicada.
- **não** — a pasta fica; dá para remover depois.
- **não sei** — explico o que fica e o que sai quando a pasta é removida.

**Próximo passo** — Com a sua resposta, encerro; para continuar, cole o prompt numa conversa nova.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
