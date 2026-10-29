# Como falar com o aluno — sdd-prompt-builder

Quem pede um prompt quer que um modelo de linguagem faça uma tarefa do sistema sozinho, sempre do mesmo
jeito. A seção "Como falar com o aluno" do `SKILL.md` dá o formato da conversa; o prompt entregue, dentro
do TXT BLOCK, é para o modelo e não segue esta moldura. Este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- prompt — "o texto de instrução que o sistema manda para o modelo de linguagem toda vez que roda";
- modelo de linguagem (LLM) — "o programa que lê o prompt e escreve a resposta";
- contrato de saída — "o formato exato que a resposta do modelo precisa ter, para o sistema conseguir
  usar";
- fallback — "o que o modelo responde quando falta informação, em vez de inventar";
- contexto ausente — "quando a informação de que o modelo precisa não veio junto";
- fórmula — "a conta escrita por extenso, com cada parte nomeada, para o modelo não errar o cálculo";
- runtime — "a hora em que o sistema está rodando de verdade, sem ninguém olhando".

Não fale em token, few-shot, temperature ou schema sem traduzir: "o tamanho do texto", "exemplos dentro
do prompt", "o quanto a resposta varia", "o formato das informações".

## Status desta skill, preenchido

`Prompt: ✅ 1 Objetivo e contrato · ▶️ 2 Regras · ⬜ 3 Conferir · ⬜ 4 Entregar`

## Exemplo — resposta completa, com decisão (etapa 1 — Objetivo e contrato)

Situação: o aluno quer um prompt que leia o corpo de um e-mail de fornecedor e diga se ele traz uma nota
fiscal, e o pedido não diz o que o sistema faz com a resposta.

**Status** — `Prompt: ▶️ 1 Objetivo e contrato · ⬜ 2 Regras · ⬜ 3 Conferir · ⬜ 4 Entregar`
(no Status: "contrato" é o formato exato da resposta do modelo; "Conferir" é revisar o prompt contra a
lista de qualidade antes de entregar.)

**O que foi feito** — Li o pedido e os 3 e-mails de exemplo: 2 trazem nota anexada, 1 só fala do
pagamento.

**Agora: etapa 1 — Objetivo e contrato** — Antes das regras, preciso saber em que formato a resposta
sai, porque é o sistema, não uma pessoa, que vai ler o que o modelo responder.

**Sua decisão** — **Em que formato o modelo responde?**
- **sim ou não, em uma palavra** (recomendado) — o sistema só precisa separar os e-mails: é o formato
  com menos jeito de sair errado.
- **sim ou não, com o motivo** — uma linha a mais, útil para conferir os casos duvidosos.
- **os dados da nota** — número, emitente e valor; é outra tarefa, maior.
- **não sei** — mostro como cada formato fica com os 3 e-mails de exemplo.

**Próximo passo** — Com o formato escolhido, escrevo as regras e o que fazer quando faltar informação.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
