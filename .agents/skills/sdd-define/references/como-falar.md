# Como falar com o aluno — sdd-define

Quem chega ao Define traz um brainstorm e nenhum vocabulário de requisitos. A seção "Como falar com o
aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- requisito — "uma frase que diz o que o sistema precisa fazer, de um jeito que dê para conferir depois";
- MUST / SHOULD / COULD — "o que é obrigatório, o que é importante mas pode esperar, e o que seria bom
  ter";
- critério de sucesso — "como a gente vai saber que deu certo: um número ou algo que dá para observar";
- teste de aceitação — "uma frase do tipo 'quando acontece X, o sistema faz Y', que vira a prova de que
  o requisito foi atendido";
- EARS — "o jeito padronizado de escrever essas frases (quando…, se…, enquanto…); as palavras ficam em
  inglês porque é uma convenção";
- Clarity Score — "uma nota de 0 a 15 que mede se o documento está claro o bastante para seguir";
- marcador de dúvida — "uma marca no texto onde ainda falta uma resposta sua; com ela, nada segue";
- Verify Gate — "a conferência final: um comando que roda e diz passou ou não passou";
- exit 0 / 2 / 3 / 4 / 5 / 64 — "o código com que a conferência termina: 0 passou, 2 falhou, 3 não deu
  para saber, 4 precisa da sua assinatura, 5 tem dúvida aberta, 64 o documento está mal escrito";
- LLM — "um modelo de linguagem, como o que você está usando agora";
- DEFINE — "o documento desta fase; a próxima (Design) parte dele".

Não fale em stakeholder, NFR, edge case ou data model sem traduzir: "quem é afetado", "exigência de
velocidade ou segurança", "caso raro", "que informações o sistema guarda".

## Status desta skill, preenchido

`Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ✅ 3 Testes de aceitação · ▶️ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar`

## Exemplo — resposta completa, com decisão (etapa 4 — Perguntas)

Situação: o DEFINE da conferência de notas fiscais tem 6 testes de aceitação; falta decidir o que fazer
com nota que aparece duas vezes.

**Status** — `Define: ✅ 1 Ler o brainstorm · ✅ 2 Requisitos · ✅ 3 Testes de aceitação · ▶️ 4 Perguntas · ⬜ 5 Verify Gate · ⬜ 6 Gravar`
(no Status: "Verify Gate" é a conferência final, um comando que diz passou ou não passou.)

**O que foi feito** — Escrevi os 4 objetivos e os 6 testes de aceitação, frases do tipo "quando chega
uma nota, o sistema marca a linha da planilha". Ficou 1 ponto sem resposta, marcado no texto.

**Agora: etapa 4 — Perguntas** — Uma nota pode chegar duas vezes (o fornecedor reenvia o e-mail). Sem
essa resposta, a conferência final não tem como saber o que é certo.

**Sua decisão** — **O que fazer com uma nota que chega duas vezes?**
- **marcar uma vez e avisar** (recomendado) — a linha é marcada só na 1ª, e a 2ª vai para uma lista de
  repetidas: nas amostras, 2 de 40 notas vieram repetidas.
- **ignorar a repetida** — marca uma vez e não avisa; mais simples, mas você não fica sabendo.
- **marcar as duas** — a planilha fica com a linha duplicada.
- **não sei** — mostro o que cada opção faz com as 2 notas repetidas da amostra.

**Próximo passo** — Com a sua resposta, escrevo a conferência final (o Verify Gate).

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
