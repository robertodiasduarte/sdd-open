# Como falar com o aluno — sdd-governanca

Quem responde aqui é o profissional responsável (contador, auditor, perito), que conhece a regra do
negócio e não o vocabulário de software. A seção "Como falar com o aluno" do `SKILL.md` dá o formato;
este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- governança — "a garantia de que, anos depois, dá para reconstruir o que aconteceu, quem fez e por quê,
  com prova de que nada foi alterado";
- lacuna — "um ponto em que o DEFINE ainda não exige essa garantia";
- trilha de auditoria — "o registro de cada mudança: o que era, o que ficou, quem mudou e quando";
- imutável — "gravado uma vez e nunca mais alterado; correção vira um lançamento novo, não uma edição";
- severidade — "o tamanho do risco: alta, média ou baixa";
- requisito EARS — "uma frase do tipo 'se alguém tentar X, o sistema recusa', que vira prova depois";
- prova por script — "um teste que tenta a ação proibida num banco de teste e só passa se o banco recusar";
- riscos aceitos — "a lista do que você decidiu não exigir, com o seu motivo";
- 2ª camada — "o que fica para depois, sem prazo, fora desta entrega".

Não fale em trigger, constraint, rollback ou RLS sem traduzir: "uma regra que o banco aplica sozinho",
"uma trava do banco", "desfazer a tentativa", "quem pode ver cada linha".

## Status desta skill, preenchido

`Governança: ✅ 1 Triagem · ✅ 2 Padrão do projeto · ✅ 3 Item a item · ✅ 4 Relatório · ▶️ 5 Suas decisões · ⬜ 6 Aplicar no DEFINE`

## Exemplo — resposta completa, com decisão (etapa 5 — Suas decisões)

Situação: o DEFINE de um módulo de lançamentos contábeis tem 3 lacunas; esta é a 1ª.

**Status** — `Governança: ✅ 1 Triagem · ✅ 2 Padrão do projeto · ✅ 3 Item a item · ✅ 4 Relatório · ▶️ 5 Suas decisões · ⬜ 6 Aplicar no DEFINE`
(no Status: "Item a item" é a conferência de cada exigência do catálogo; "Aplicar no DEFINE" é escrever
no documento o que você decidir.)

**O que foi feito** — Conferi o DEFINE contra 12 itens do catálogo: 9 já estão atendidos, 3 são lacunas.
O relatório está gravado. Nada foi alterado no DEFINE.

**Agora: etapa 5 — Suas decisões** — Lacuna 1 de 3, severidade alta. Hoje o DEFINE deixa o analista
corrigir o valor de um lançamento já gravado; numa fiscalização, não haveria como provar o valor
original. Se aplicada, a correção passa a ser um lançamento novo de estorno, e o teste de aceitação 4
muda de "o analista edita o valor" para "o analista lança o estorno".

**Sua decisão** — **O lançamento gravado passa a ser imutável?**
- **aplicar** (recomendado) — o requisito entra no DEFINE e o teste 4 é reescrito: é a garantia que um
  fiscal pede primeiro.
- **recusar** — não entra; preciso do seu motivo, que vai para os riscos aceitos com o seu nome e a data.
- **adiar** — vai para a 2ª camada, fora desta entrega.
- **não sei** — mostro o teste 4 antes e depois, lado a lado.

**Próximo passo** — Com a sua resposta, passo para a lacuna 2 de 3.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
