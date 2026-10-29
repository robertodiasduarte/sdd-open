# Como falar com o aluno — sdd-iterate

Quem chama o iterate mudou de ideia no meio do caminho e quer saber o que a mudança mexe. A seção "Como
falar com o aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- iterate — "a mudança feita no próprio documento da fase, sem começar outro do zero";
- documento a jusante — "o que foi feito a partir deste: o DESIGN depende do DEFINE, o código depende do
  DESIGN";
- cascata — "levar a mudança para os documentos que dependem deste";
- histórico de revisões — "a tabela no fim do documento que diz o que mudou, quando e por quê";
- Verify Gate — "a conferência final combinada no DEFINE: um comando que diz passou ou não passou";
- exit 5 / 64 — "o código com que a conferência termina: 5 tem dúvida aberta (volta para o Define), 64 o
  bloco da conferência está mal escrito";
- landmine — "uma armadilha conhecida do projeto, registrada no playbook com um número".

Não fale em patch, diff ou in-place sem traduzir: "a alteração", "o que mudou, linha a linha", "no
mesmo arquivo".

## Status desta skill, preenchido

`Iterate: ✅ 1 Ler · ✅ 2 Classificar · ✅ 3 Aplicar · ▶️ 4 Cascata · ⬜ 5 Fechar`

## Exemplo — resposta completa, com decisão (etapa 4 — Cascata)

Situação: o aluno pediu para a conferência de notas aceitar também notas de serviço; o DEFINE foi
alterado e o DESIGN já existia.

**Status** — `Iterate: ✅ 1 Ler · ✅ 2 Classificar · ✅ 3 Aplicar · ▶️ 4 Cascata · ⬜ 5 Fechar`
(no Status: "Cascata" é levar a mudança para os documentos que dependem deste.)

**O que foi feito** — Mudei o DEFINE no próprio arquivo: 1 objetivo novo, 2 testes de aceitação novos e
uma linha no histórico de revisões. A conferência do DEFINE não achou dúvida aberta.

**Agora: etapa 4 — Cascata** — O DESIGN foi feito antes desta mudança e não sabe das notas de serviço:
o leitor de XML dele lê só um formato.

**Sua decisão** — **O que faço com o DESIGN?**
- **atualizo agora** (recomendado) — acrescento o 2º formato ao leitor e 1 arquivo ao manifest; sem isso,
  o build constrói só metade do pedido.
- **só o DEFINE** — paro aqui; você cuida do DESIGN depois.
- **mostro antes** — mostro as 3 linhas que mudariam no DESIGN e pergunto de novo.
- **não sei** — explico o que acontece no build se o DESIGN ficar como está.

**Próximo passo** — Com a sua resposta, confiro o playbook e fecho com o que mudou.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
