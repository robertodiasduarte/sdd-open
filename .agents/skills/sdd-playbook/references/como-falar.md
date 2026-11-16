# Como falar com o aluno — sdd-playbook

O playbook trabalha quase sempre em silêncio: a leitura do início de sessão não gera resposta. Ele fala
com o aluno quando há um candidato a registrar ou uma promoção a decidir. A seção "Como falar com o
aluno" do `SKILL.md` dá o formato; este arquivo dá as palavras e um exemplo inteiro.

## Glossário (explique na primeira vez em que o termo aparecer)

- playbook — "o caderno do projeto com as armadilhas que já morderam e o que fazer em vez disso";
- landmine (LM-nnn) — "uma armadilha registrada, com um número fixo para ser citada";
- candidato — "uma armadilha nova proposta por uma sessão, com a prova de que aconteceu; só entra com o
  seu OK";
- mordeu / ajudou — "as contagens de cada armadilha: quantas vezes causou problema mesmo registrada, e
  quantas vezes evitou um";
- promoção — "trocar uma regra escrita que não bastou por um mecanismo que barra sozinho (uma conferência
  automática, um teste)";
- tombstone — "a marca de uma regra aposentada, que fica registrada para ninguém reescrevê-la";
- lint — "a conferência automática do formato do playbook";
- curadoria — "conferir o que as features publicadas ensinaram para as próximas"; a publicação só colhe, e o
  lote julga;
- lote — "o julgamento, de uma vez, das colheitas que esperam na fila";
- fila — "a pasta onde as colheitas das publicações esperam o lote";
- delta — "uma mudança de uma linha no playbook";
- aposentar — "tirar uma lição de uso, guardando o motivo" (é o tombstone);
- invariante — "uma regra que nunca pode ser quebrada, com o teste que a vigia".

Não fale em delta, curator, generator ou reflector sem traduzir: "a alteração proposta", "quem decide o
que entra", "quem usa o playbook", "quem aponta o que mordeu". "0 deltas" para o aluno é "esta feature
não trouxe lição nova nem contagem".

## Status desta skill, preenchido

`Playbook: ✅ 1 Leitura · ✅ 2 Candidato · ▶️ 3 Promoção · ⬜ 4 Lote`

## Exemplo — resposta completa, com decisão (etapa 3 — Promoção)

Situação: no fechamento de uma release, a armadilha LM-004 ("exit 0 não prova a migration") mordeu pela
2ª vez, mesmo registrada.

**Status** — `Playbook: ✅ 1 Leitura · ✅ 2 Candidato · ▶️ 3 Promoção · ⬜ 4 Lote`
(no Status: "Candidato" é a armadilha nova proposta; "Promoção" é trocar a regra escrita por algo que
barra sozinho.)

**O que foi feito** — Contei os registros desta release: a LM-004 mordeu de novo (a 2ª vez), e nenhum
candidato novo trouxe prova. O playbook não foi alterado.

**Agora: etapa 3 — Promoção** — Duas mordidas querem dizer que a regra escrita não bastou. A saída é um
mecanismo que barre o erro sem depender de alguém lembrar da regra.

**Sua decisão** — [D3 · muda a regra do método] **Promovo a regra que mordeu 2 vezes para uma conferência automática no relatório do build?**
- **promover** (recomendado) — registro que ela vira conferência automática; a regra fica até a
  conferência ter um teste que falha sem ela (ref: LM-004).
- **manter escrita** — a regra continua só no texto, com a contagem em 2.
- **não sei** — mostro as 2 vezes em que ela mordeu, com o arquivo de cada uma.

**Próximo passo** — Com o seu OK, aplico só o aprovado e confiro o playbook com o lint.

## Exemplo — o lote da curadoria (etapa 4 — Lote)

Situação: a pessoa pediu o lote. A fila tinha 3 publicações; os julgamentos trouxeram 2 contagens com prova,
1 lição nova e 1 lição que já mordeu 2 vezes. O lote roda numa frente própria, fora de qualquer publicação.

**Status** — `Playbook: ✅ 1 Leitura · ➖ 2 Candidato · ➖ 3 Promoção · ▶️ 4 Lote`

**O que foi feito** — Julguei as 3 publicações que esperavam na fila (a curadoria: as lições do caderno de
armadilhas do projeto), cada uma por um agente novo, e conferi cada julgamento por script.

**Decidi sozinho** (contagem com prova não muda regra; para desfazer, reverta o commit do lote):
- o aviso sobre o envio sem o segredo foi seguido no desenho e evitou o erro: contei +1;
- o erro do preflight aconteceu de novo, mesmo com o aviso: contei +1.

**Agora: etapa 4 — Lote** — Duas mudanças nas regras do projeto dependem de você. Responda pelos
números, por exemplo "1 aceitar, 2 recusar".

**Sua decisão** — 1. [D3 · muda a regra do método] **Guardo a lição nova sobre o relatório que saiu sem as notas canceladas?**
- **aceitar** (recomendado) — entra no caderno e avisa toda sessão que mexer no relatório; a prova está
  no relatório do build (ref: o candidato do relatório do build).
- **recusar** — a lição não entra; o que aconteceu fica só no histórico desta feature.
- **não sei** — mostro o trecho do relatório do build em que isso aconteceu.

**Sua decisão** — 2. [D3 · muda a regra do método] **Transformo em trava automática o aviso que já falhou 2 vezes?**
- **aceitar** (recomendado) — registro que ele vira uma conferência automática; isso pede uma correção
  própria, com teste, numa próxima tarefa (ref: a lição da migration que sai `exit 0` sem estar no banco).
- **recusar** — o aviso continua só escrito, e esta pergunta volta na próxima publicação.
- **não sei** — mostro as 2 vezes em que o erro aconteceu, com o arquivo de cada uma.

**Próximo passo** — Aplico só o que você aceitar, confiro o caderno e pergunto se envio essa mudança.

Aposentar uma lição da qual uma regra permanente depende é **uma opção só**, nunca duas: "aposentar o
aviso sobre o envio e ajustar a regra permanente que dependia dele, no mesmo passo".

Depois de aplicar, o envio é outra decisão, porque o push pode publicar:

**Sua decisão** — [D1 · não se desfaz] **Posso enviar o commit do lote para a branch padrão?**
- **sim** (recomendado) — envio só o caderno de armadilhas e os registros desta conferência; neste projeto,
  esse push não publica nada, porque o workflow só roda quando o código muda.
- **deixar para depois** — a mudança fica salva nesta pasta; as publicações continuam na fila até o envio.
- **não sei** — explico o que este envio muda e o que acontece se ele ficar para depois.

Quando uma publicação da fila é recusada (a colheita guardada não bate com os documentos dela, ou a pasta foi
mexida depois de salva), diga isso em uma frase, que nada dela foi aplicado e como refazer: "A colheita da
publicação de 12/11 não bate com os documentos guardados com ela; não julguei nada dela, e ela continua na fila.
Para refazer, a colheita precisa rodar de novo numa pasta com os documentos dessa feature."

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
