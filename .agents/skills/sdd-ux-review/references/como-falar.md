# Como falar com o aluno — sdd-ux-review

Quem chega ao UX review sabe o que o sistema deve fazer e quase nunca pensou em quem vai usá-lo nem em
como essa pessoa entende a tela. A seção "Como falar com o aluno" do `SKILL.md` dá o formato; este
arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- UX / experiência — "como a pessoa entende e usa o que o sistema mostra: tela, mensagem, arquivo gerado";
- jornada — "o caminho da pessoa: antes de usar, a entrada, a ação principal, o retorno e a recuperação
  de um erro";
- estado — "cada situação que a tela precisa mostrar: carregando, vazio, erro, deu certo";
- MUST / SHOULD / COULD / WONT — "o que impede a pessoa de conseguir, o que atrapalha, o que seria bom e
  o que fica de fora, com o motivo";
- lente — "um ponto de vista de como as pessoas pensam (atenção, memória); sugere, nunca obriga";
- 60/30/10 — "a proporção de cores: a de fundo, a das áreas de apoio e a de destaque";
- copy — "o texto que aparece para a pessoa: botões, mensagens, avisos".

Não fale em CTA, affordance, onboarding ou empty state sem traduzir: "o botão principal", "o que mostra
que dá para clicar", "a primeira vez", "a tela sem nada ainda".

## Status desta skill, preenchido

`UX review: ✅ 1 Contexto · ✅ 2 Jornada · ✅ 3 Qualidade · ▶️ 4 Prioridades · ⬜ 5 Gravar`

## Exemplo — resposta completa, com decisão (etapa 4 — Prioridades)

Situação: a conferência de notas gera uma planilha marcada; a jornada mostrou que, sem nenhum XML na
pasta, a pessoa recebe a planilha sem marca nenhuma e acha que todas as notas faltam.

**Status** — `UX review: ✅ 1 Contexto · ✅ 2 Jornada · ✅ 3 Qualidade · ▶️ 4 Prioridades · ⬜ 5 Gravar`
(no Status: "Jornada" é o caminho da pessoa do começo ao fim; "Prioridades" é separar o que impede do
que só atrapalha.)

**O que foi feito** — Segui a jornada de quem confere as notas do mês: 5 pontos de contato, 7 achados,
2 deles de clareza.

**Agora: etapa 4 — Prioridades** — Um achado muda o resultado para a pessoa: com a pasta vazia, a
planilha sai igual a "nenhuma nota chegou", e ela pode cobrar 40 fornecedores sem motivo.

**Sua decisão** — **A mensagem "nenhum XML encontrado na pasta" entra como MUST?**
- **MUST** (recomendado) — o Design é obrigado a tratar a pasta vazia: sem isso, a pessoa tira a
  conclusão errada.
- **SHOULD** — entra como importante, mas o Design pode deixar para depois.
- **WONT** — fica de fora, com o motivo registrado.
- **não sei** — mostro a planilha que sai hoje com a pasta vazia.

**Próximo passo** — Com as prioridades fechadas, gravo o UX review para o Design.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
