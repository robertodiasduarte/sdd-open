# Como falar com o aluno — sdd-auditoria-harness

Quem pede a auditoria quer saber se o seu conjunto de skills, comandos e regras do agente está em ordem,
sem que nada seja mudado. A seção "Como falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá
as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- harness — "o conjunto de skills, comandos, regras e ganchos que o agente usa neste projeto";
- somente leitura — "eu só olho; a única coisa que gravo é o relatório, num arquivo novo";
- SDD principal — "o fluxo de trabalho oficial do projeto, que serve de régua para o resto";
- achado — "um item que pede atenção: duplicado, ambíguo, em conflito, abandonado ou sem uso";
- vitalidade — "se o item ainda é usado: quando foi citado ou mudou pela última vez";
- manter / aposentar / fundir / esclarecer / arquivar / reduzir — "as ações que eu posso sugerir; quem
  decide e faz é você, depois";
- hook — "um gancho que roda sozinho antes ou depois de uma ação do agente".

Não fale em grep, frontmatter ou settings sem traduzir: "a busca no texto", "o cabeçalho da skill",
"o arquivo de configuração do agente".

## Status desta skill, preenchido

`Auditoria: ✅ 1 Segurança · ✅ 2 SDD principal · ✅ 3 Inventário · ✅ 4 Achados · ▶️ 5 Relatório`

## Exemplo — resposta completa, com decisão (etapa 5 — Relatório)

Situação: a auditoria terminou; o relatório de hoje já existe na pasta, de uma auditoria feita de manhã.

**Status** — `Auditoria: ✅ 1 Segurança · ✅ 2 SDD principal · ✅ 3 Inventário · ✅ 4 Achados · ▶️ 5 Relatório`
(no Status: "Inventário" é a lista de tudo o que o agente usa; "Achados" são os itens que pedem atenção.)

**O que foi feito** — Li 31 itens: 18 skills, 9 comandos e 4 ganchos. Achei 6 pontos de atenção: 2 em
conflito, 3 sem uso há meses e 1 duplicado. Nada foi mudado.

**Agora: etapa 5 — Relatório** — O arquivo do relatório de hoje já existe, e eu não sobrescrevo o que
já está gravado.

**Sua decisão** — [auto · de rotina] **Onde gravo o relatório desta auditoria?**
- **arquivo novo com "-2" no nome** (recomendado) — o relatório da manhã fica intacto, e os dois podem
  ser comparados.
- **só aqui na conversa** — mostro o resumo e nada é gravado.
- **não sei** — explico o que tem em cada um dos dois relatórios.

**Próximo passo** — Com a sua resposta, gravo (ou mostro) o relatório e confiro o resultado.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
