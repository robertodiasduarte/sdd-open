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
- lint — "a conferência automática do formato do playbook".

Não fale em delta, curator, generator ou reflector sem traduzir: "a alteração proposta", "quem decide o
que entra", "quem usa o playbook", "quem aponta o que mordeu".

## Status desta skill, preenchido

`Playbook: ✅ 1 Leitura · ✅ 2 Candidato · ▶️ 3 Promoção`

## Exemplo — resposta completa, com decisão (etapa 3 — Promoção)

Situação: no fechamento de uma release, a armadilha LM-004 ("exit 0 não prova a migration") mordeu pela
2ª vez, mesmo registrada.

**Status** — `Playbook: ✅ 1 Leitura · ✅ 2 Candidato · ▶️ 3 Promoção`
(no Status: "Candidato" é a armadilha nova proposta; "Promoção" é trocar a regra escrita por algo que
barra sozinho.)

**O que foi feito** — Contei os registros desta release: a LM-004 mordeu de novo (a 2ª vez), e nenhum
candidato novo trouxe prova. O playbook não foi alterado.

**Agora: etapa 3 — Promoção** — Duas mordidas querem dizer que a regra escrita não bastou. A saída é um
mecanismo que barre o erro sem depender de alguém lembrar da regra.

**Sua decisão** — **Promovo a LM-004 para uma conferência automática no relatório do build?**
- **promover** (recomendado) — registro que ela vira conferência automática; a regra fica até a
  conferência ter um teste que falha sem ela (ref: LM-004).
- **manter escrita** — a regra continua só no texto, com a contagem em 2.
- **não sei** — mostro as 2 vezes em que ela mordeu, com o arquivo de cada uma.

**Próximo passo** — Com o seu OK, aplico só o aprovado e confiro o playbook com o lint.

Formato completo de pergunta e de parada: `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
