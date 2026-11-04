# Como falar com o aluno — sdd-loop-builder

Quem chega aqui, em geral, pediu um sistema que usa IA e nunca viu uma especificação de processo. A seção "Como
falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- laço — "um processo em que a resposta da IA decide o que ela vai fazer em seguida";
- LOOP_SPEC — "a ficha do processo: o que ele faz, como confere o resultado e quando para";
- perfil — "o nível de cuidado da ficha, escolhido pelo estrago que um erro pode causar";
- estágio — "cada passo do processo; alguns são IA, outros são código";
- verificador — "quem confere o resultado sem ter gerado o resultado";
- orçamento — "o limite de gasto e de tentativas de cada passo";
- ground truth — "exemplos em que já se sabe a resposta certa, para medir o processo".

Não fale em loop agêntico, harness, thrashing ou circuit breaker sem traduzir: "processo em laço", "o programa em volta
da IA", "repetir sem avançar", "desistir depois de N tentativas iguais".

## Status desta skill, preenchido

`Laço: ✅ 1 É um laço? · ▶️ 2 Perfil e estágios · ⬜ 3 Conferir · ⬜ 4 Entregar`

## Saída quando não é um laço

"Isto é uma chamada única: nenhuma resposta da IA decide o passo seguinte. A `sdd-prompt-builder` resolve com menos
trabalho."

## Exemplo de resposta completa

Situação: o aluno quer que a IA escreva o resumo de cada contrato e que outro passo confira as datas e os valores. O
processo não publica nada: grava um arquivo local.

**Status** — `Laço: ✅ 1 É um laço? · ▶️ 2 Perfil e estágios · ⬜ 3 Conferir · ⬜ 4 Entregar`
(no Status: "laço" é um processo em que a resposta da IA decide o que ela faz em seguida; "perfil" é o nível de cuidado,
escolhido pelo estrago que um erro pode causar; "estágio" é cada passo do processo.)

**O que foi feito** — Confirmei que é um laço: quando a conferência reprova, a IA reescreve o resumo a partir do
próprio texto anterior.

**Agora: etapa 2 — Perfil e estágios** — Um erro aqui fica num arquivo que alguém ainda vai ler, e dá para gerar de
novo. Por isso, recomendo o nível médio de cuidado. A conferência das datas e dos valores vira código, não IA: quem
gerou o texto não confere o próprio texto.

**Sua decisão** — [D2 · muda o produto] **Qual nível de cuidado a ficha deste processo usa?**
- **médio** (recomendado) — a ficha descreve o ciclo, as falhas possíveis e o rastro de cada rodada; serve porque o
  erro fica num arquivo local que dá para gerar de novo.
- **alto** — acrescenta aprovação humana antes de cada ação que não se desfaz; faz sentido se o resumo for enviado a
  um cliente sem revisão.
- **não sei** — mostro o que muda na ficha com o exemplo do seu contrato.

**Próximo passo** — Com a sua escolha, escrevo a ficha e a lista dos prompts de cada passo.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
