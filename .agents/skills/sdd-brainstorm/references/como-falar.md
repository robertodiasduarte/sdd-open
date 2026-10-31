# Como falar com o aluno — sdd-brainstorm

Quem pede um brainstorm, em geral, tem uma ideia e nenhum vocabulário de software. A seção "Como falar
com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- brainstorm — "a conversa em que a gente entende o problema antes de decidir como resolver";
- abordagem — "um jeito de resolver o problema; eu mostro duas ou três e recomendo uma";
- amostra — "um exemplo real do que entra e do que deve sair: uma planilha, um e-mail, um relatório";
- dado verificado — "um exemplo em que já se sabe a resposta certa, para conferir depois";
- YAGNI — "a regra de deixar de fora o que não é necessário agora; a gente anota para depois";
- validação incremental — "uma parada para você confirmar que entendi certo antes de eu seguir";
- requisito — "uma frase que diz o que o sistema precisa fazer; é o que a próxima fase (Define) escreve";
- fase — "cada etapa do método: brainstorm, define, design, build, release".

Não fale em MVP, stakeholder, trade-off ou escopo sem traduzir: "o mínimo que resolve", "quem é
afetado", "o que se ganha e o que se perde", "o que entra e o que fica de fora".

## Status desta skill, preenchido

`Brainstorm: ✅ 1 Entender · ✅ 2 Perguntas · ✅ 3 Amostras · ▶️ 4 Abordagens · ⬜ 5 Validar · ⬜ 6 Gravar`

## Exemplo — resposta completa, com decisão (etapa 4 — Abordagens)

Situação: o aluno quer conferir as notas fiscais recebidas por e-mail contra a planilha de pagamentos.
Já respondeu 3 perguntas e mandou 2 amostras (um XML de nota e a planilha de outubro).

**Status** — `Brainstorm: ✅ 1 Entender · ✅ 2 Perguntas · ✅ 3 Amostras · ▶️ 4 Abordagens · ⬜ 5 Validar · ⬜ 6 Gravar`
(no Status: "Abordagens" é o momento em que eu mostro os jeitos possíveis de resolver; "Validar" é a
parada para você confirmar que entendi certo.)

**O que foi feito** — Li as 2 amostras: o XML tem número, CNPJ do emitente e valor; a planilha tem as
mesmas três colunas com outros nomes. Nenhum arquivo foi criado ainda.

**Agora: etapa 4 — Abordagens** — Há três jeitos de resolver. Recomendo começar pelo mais simples, porque
as duas amostras já trazem os três campos que precisam bater.

**Sua decisão** — [D2 · muda o produto] **Qual abordagem seguimos?**
- **planilha de conferência** (recomendado) — um script lê os XMLs de uma pasta e marca na planilha o que
  bateu; você baixa os anexos à mão. Menos peças, pronto em 1 fase de build.
- **leitura direta do e-mail** — o sistema busca os anexos sozinho; exige dar acesso à caixa de e-mail.
- **painel na web** — uma página para conferir; o triplo de trabalho, para o mesmo resultado.
- **não sei** — explico a diferença com a nota da amostra como exemplo.

**Próximo passo** — Com a abordagem escolhida, separo o que fica para depois (YAGNI).

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
