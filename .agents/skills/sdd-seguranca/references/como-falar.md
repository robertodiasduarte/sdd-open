# Como falar com o aluno — sdd-seguranca

Quem responde aqui constrói um app com IA e conhece o próprio negócio, não o vocabulário de segurança. A
seção "Como falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- RLS (segurança por linha) — "a regra do banco que decide quem vê e quem muda cada linha de uma tabela";
- chave secreta — "a senha que o seu app usa para falar com um serviço (banco, pagamento, IA); quem a tem
  age em nome do app";
- chave pública — "a chave feita para ficar no navegador; sozinha, ela não abre nada que a RLS fecha";
- CORS — "a lista de sites que podem chamar a sua API pelo navegador";
- cabeçalhos de segurança — "instruções que o servidor manda junto com cada página para o navegador
  bloquear truques comuns";
- XSS — "quando um texto digitado por alguém vira código na tela de outra pessoa";
- prompt injection — "quando um documento lido pela IA traz uma ordem escondida e a IA obedece";
- stack — "as ferramentas em que o app foi feito (Supabase, Vercel, um site)";
- teste negativo — "um teste que tenta o que é proibido e só passa se for recusado";
- dispensa — "um comentário na linha do código dizendo por que um aviso não vale ali; sem motivo, não vale".

Não fale em grant, JWT, source map ou introspecção sem traduzir: "permissão do banco", "o crachá da sessão",
"o mapa do código-fonte", "o mapa que a API dá de si mesma".

## Status desta skill, preenchido

`Segurança: ✅ 1 Gatilhos · ✅ 2 Itens da stack · ▶️ 3 Suas decisões · ⬜ 4 Gravar`

## Exemplo — resposta completa, com decisão (etapa 3 — Suas decisões)

Situação: o DEFINE de um portal em que o cliente do escritório faz login e baixa as guias do mês, com Supabase.

**Status** — `Segurança: ✅ 1 Gatilhos · ✅ 2 Itens da stack · ▶️ 3 Suas decisões · ⬜ 4 Gravar`
(no Status: "Gatilhos" são o que o DEFINE tem de arriscado, como login e arquivo de cliente; "Itens da stack"
são as falhas que valem para o Supabase e para um site.)

**O que foi feito** — Achei 3 gatilhos no DEFINE: login, arquivo de cliente e banco. Para eles, o catálogo tem
6 itens; trago os 5 mais graves, um por vez. Nada foi alterado no DEFINE.

**Agora: etapa 3 — Suas decisões** — Item 1 de 5, gravidade alta. Hoje o DEFINE não diz quem vê cada guia; no
Supabase, uma tabela nasce aberta para quem tiver a chave pública, que fica no navegador de qualquer visitante.
Se aplicado, entra um teste de aceitação novo: o cliente de outra conta, e quem não fez login, recebem zero guias.

**Sua decisão** — [D2 · muda o produto] **Cada guia passa a ser vista só pelo cliente dono dela?**
- **aplicar** (recomendado) — o teste com duas contas entra no DEFINE e roda a cada build: é a falha que mais
  vaza dado de cliente.
- **recusar** — não entra; preciso do seu motivo, que fica registrado e aparece no relatório do build.
- **adiar** — fica para depois desta entrega e aparece no relatório do build como pendência.
- **não sei** — mostro o teste em duas linhas e como ele falharia hoje.

**Próximo passo** — Com a sua resposta, passo para o item 2 de 5.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
