# Como falar com o aluno — sdd-desempenho-banco

Quem responde aqui constrói um app com IA e conhece o próprio negócio, não o vocabulário de banco de dados. A
seção "Como falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- índice — "um sumário que o banco mantém de uma coluna, para achar as linhas sem ler a tabela inteira";
- chave estrangeira — "a coluna que aponta para uma linha de outra tabela (o pedido aponta para o cliente)";
- chave primária — "a coluna que identifica cada linha de um jeito único";
- política (RLS) — "a regra do banco que decide quem vê e quem muda cada linha de uma tabela";
- paginação — "mostrar a lista aos pedaços (uma página por vez), em vez de trazer tudo";
- advisor — "o relatório automático do Supabase que aponta o que pode deixar o banco lento ou inseguro";
- migration — "o arquivo que muda a estrutura do banco (cria tabela, coluna, índice) e fica guardado no projeto";
- estatísticas do banco — "os contadores que o banco guarda de cada tabela e índice; zeram quando ele reinicia";
- swap — "quando a memória da máquina acaba e ela usa o disco no lugar: tudo fica lento";
- dispensa — "um comentário na linha do código dizendo por que um aviso não vale ali; sem motivo, não vale".

Não fale em InitPlan, seq scan, bloat ou pooler sem traduzir: "a regra calculada uma vez por consulta", "ler a
tabela inteira", "espaço ocupado por linhas apagadas", "o porteiro que reaproveita as conexões com o banco".

## Status desta skill, preenchido

`Desempenho: ✅ 1 Gatilhos · ✅ 2 Volume · ▶️ 3 Suas decisões · ⬜ 4 Gravar`

## Exemplo 1 — a pergunta de volume (etapa 2 — Volume)

**Status** — `Desempenho: ✅ 1 Gatilhos · ▶️ 2 Volume · ⬜ 3 Suas decisões · ⬜ 4 Gravar`

**O que foi feito** — O DEFINE cria a tabela de pedidos e uma tela que lista os pedidos do cliente. Isso é
banco e lista; nada foi alterado no DEFINE.

**Agora: etapa 2 — Volume** — O que muda o desempenho é o tamanho da tabela: com poucas linhas, quase tudo é
rápido; com muitas, a lista sem paginação e o índice esquecido aparecem. Uma pergunta só.

**Sua decisão** — [D2 · muda o produto] **Quantas linhas a tabela de pedidos terá daqui a um ano?** Responda com um número
aproximado (por exemplo, "uns 5 mil" ou "mais de 100 mil"). Se não souber, diga "não sei": eu sigo pelo lado
seguro e proponho os testes de paginação.

**Próximo passo** — Com o número, digo se entram testes de desempenho no DEFINE ou só decisões no Design.

## Exemplo 2 — resposta completa, com decisão (etapa 3 — Suas decisões)

Situação: o mesmo DEFINE; a pessoa respondeu "mais de 100 mil".

**Status** — `Desempenho: ✅ 1 Gatilhos · ✅ 2 Volume · ▶️ 3 Suas decisões · ⬜ 4 Gravar`
(no Status: "Volume" é quantas linhas a tabela terá; "Suas decisões" são os testes que entram no DEFINE.)

**O que foi feito** — Volume anotado: mais de 100 mil pedidos em um ano. Para lista com esse volume, o catálogo
tem 1 ficha da fase Define (P08, lista sem limite). Nada foi alterado no DEFINE.

**Agora: etapa 3 — Suas decisões** — Ficha 1 de 1. Hoje o DEFINE não diz quantos pedidos a tela mostra de cada
vez; sem limite, a tela traz todos, fica mais lenta a cada mês e, acima do teto do Supabase, corta a lista em
silêncio. Se aplicado, entra um teste: a tela pede no máximo uma página, e a varredura avisa lista sem limite.

**Sua decisão** — [D2 · muda o produto] **A lista de pedidos passa a mostrar uma página de cada vez?**
- **aplicar** (recomendado) — o teste da página entra no DEFINE e roda a cada build: é o que mais pesa quando a
  tabela cresce.
- **recusar** — não entra; preciso do seu motivo, que fica registrado no DEFINE e no relatório do build.
- **adiar** — fica para depois desta entrega, registrado como pendência no relatório do build.
- **não sei** — mostro o teste em duas linhas e o que acontece com a tela sem ele.

**Próximo passo** — Com a sua resposta, gravo a linha Desempenho no DEFINE e volto ao Define.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
