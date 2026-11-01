# UX REVIEW: F9 Fluxo encadeado e decisões

> UX/CX review for `F9_FLUXO` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F9_FLUXO |
| **Date** | 2026-10-31 |
| **Author** | ux-review-command (sdd-ux-review 2.3.1) |
| **DEFINE** | [DEFINE_F9_FLUXO.md](../features/DEFINE_F9_FLUXO.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

Lidos antes, como manda o passo 1 (e como a própria F9 passa a mandar, item F11): `UX_REVIEW_F5_CONHECIMENTO.md`, `UX_REVIEW_F7_EVIDENCIA.md` e `UX_REVIEW_F8_HOOKS.md`. Vêm deles: o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2), "o aviso da mudança mora no produto" (F8, decisão 9) e "símbolo sempre com palavra, sem cor" (F8 U8, F7).

---

## UX Summary

A interface da F9 é texto, em 6 superfícies:
- (1) **a marca da classe** em cada pergunta de decisão, que o aluno passa a ver em toda skill;
- (2) **a linha de transição** que o `seguir` imprime quando a fase seguinte começa sem perguntar;
- (3) **o recibo "Decidi sozinho"** no resumo de etapa;
- (4) **a parada do exit 40** (sessão nova para o avaliador ou o revisor do DESIGN);
- (5) a saída do `review-design`, do `loop` e dos lints, lida pelo agente;
- (6) a subseção `### Fluxo encadeado` das skills, `FLUXO_ENCADEADO.md` e `docs/chained-flow.md`.

O maior risco está na única coisa que muda para **todos** com o slot desligado: a marca. `[D1]` antes da pergunta é um identificador técnico no lugar mais visível da resposta, o que contradiz o item 5 do próprio `PERGUNTA_DECISAO.md` ("identificadores só no fim, entre parênteses"). Um contador que lê `[D2] **Qual abordagem seguimos?**` manda print perguntando o que é D2 — o teste do suporte falha na primeira resposta. O segundo risco aparece com o slot ligado: o fluxo segue **sem perguntar**, e quem não sabe que ligou o encadeamento pensa que a skill pulou uma etapa. A linha de transição e o recibo são o produto do aviso.

Três achados centrais:
- **A marca leva o nome curto da classe junto** (`[D1 · não se desfaz]`), fixo por classe e conferido pelo lint.
- **A linha de transição diz por que não perguntou** (o encadeamento está ligado e onde) e o recibo diz como desfazer, em palavras do aluno.
- **Com o slot desligado, nada do encadeamento aparece**: o `PARAR` do `seguir` é para o agente; o aluno vê o Próximo passo de hoje.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do Bravo (contador), em geral sem git nem terminal; o agente roda as skills e o script e traduz o que aparece |
| **Secondary User** | Quem liga `flow.autonomous` (Roberto, alunos avançados); quem usa um agente sem subagente e precisa abrir uma sessão nova |
| **User Goal** | Responder só ao que é decisão dele e saber, ao fim de cada fase, o que foi decidido sem ele |
| **Primary Pain** | Perguntas que a recomendação resolveria; marca técnica sem explicação; fluxo que segue sem dizer por quê; parada para sessão nova sem saber o que trazer de volta |
| **Business/CX Goal** | Confiança: o automático é visível e reversível; o que é decisão da pessoa nunca é tomado por ela |
| **Device/Context** | Chat do agente ou terminal, desktop; a cada pergunta e a cada fim de fase |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Rodar uma fase como sempre | Rotina | Com o slot desligado, nada novo além da marca |
| Entry | Ler uma pergunta | "O que é D2?" | A marca diz em 2–4 palavras o tipo da decisão (`[D2 · muda o produto]`) |
| Core Action | Responder (slot desligado) ou deixar seguir (ligado) | Ligado: "por que não me perguntou?" | A linha de transição diz o que terminou, o que começa e que o encadeamento está ligado em `sdd/config.yaml` |
| Feedback | Ver o que foi decidido sem ele | "Posso confiar?" | O recibo: cada decisão com o porquê e como desfazer |
| Recovery | Discordar de uma decisão automática | "Dá para voltar?" | O "para desfazer:" do recibo é um passo concreto (rodar a fase de novo com `--parar`, trocar o valor no DESIGN) |
| Interrupção → Retomada | O agente precisa de uma sessão nova (exit 40) | "O que eu faço? O que trago de volta?" | A parada ⏸️ com o brief gravado, os passos numerados e **o que colar de volta** |
| Completion | Fim do encadeamento (build pronto) | Alívio; risco de achar que já publicou | A build **nunca** segue para a release: a linha diz que publicar é decisão dele |
| Follow-up | Desligar o encadeamento | "Como paro isso?" | `docs/chained-flow.md` e a linha de transição dizem: `flow.autonomous: false` ou "pare" para uma vez |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | `[D1]`…`[D5]` e `[auto]` crus antes da pergunta são jargão no lugar mais visível; contradizem o item 5 do `PERGUNTA_DECISAO.md` | Princípio 2; teste do suporte ("o que é D2?") | A marca leva um rótulo fixo por classe, separado por ` · `: `[D1 · não se desfaz]`, `[D2 · muda o produto]`, `[D3 · muda a regra do método]`, `[D4 · limite de tentativas]`, `[D5 · provas em conflito]`, `[auto · de rotina]`. A tabela do item 9 é a dona; o `sdd-decisoes-lint.sh` reprova marca sem o rótulo ou com rótulo diferente do da tabela |
| U2 | MUST | Com o slot ligado, a fase seguinte começa sem pergunta; sem dizer por quê, parece que a skill pulou uma etapa | Princípio 2 (estado ambíguo); F8 decisão 9 (o aviso mora no produto) | 1ª linha do `seguir`: `✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)` (≤ 100 caracteres, nomes de documento em maiúsculas, artigo certo: o DESIGN, o BUILD, a UX REVIEW, a GOVERNANÇA); 2ª linha `→ /sdd-<próxima> <arquivo>` para o agente |
| U3 | MUST | Com o slot desligado, a promessa é "nada muda"; repassar o `PARAR: encadeamento desligado` ao aluno é ruído novo em toda fase | DEFINE (critério "com `false`, nada muda"); princípio 1 | O `PARAR` é para o agente: com motivo "desligado", a skill mostra só o **Próximo passo** de hoje. Os outros motivos de parar (gate, marcador, release, `--parar`) com o slot **ligado** são ditos ao aluno em 1 frase |
| U4 | MUST | `sinal:` e `reverter:` do recibo do privado são palavras de quem escreveu o fluxo | Princípio 2; glossário da camada de conversa | Formato: `**Decidi sozinho:**` e uma linha por decisão: `- <decisão> — porque <o que decidiu> · para desfazer: <passo concreto>`. Bloco vazio ⇒ omitido |
| U5 | MUST | Na parada do exit 40, o aluno não sabe o que trazer de volta para a sessão de origem | Teste do suporte ("e agora, o que eu colo?"); F4 (formato ⏸️) | Os **Passos** terminam com o que copiar de volta, por papel: avaliador → o bloco `<<<AVALIACAO … >>>` inteiro, com a linha `VEREDITO: …` (revisto no ciclo 1 da revisão do build: a build grava o bloco verbatim e usa os achados no ciclo 2); revisor do DESIGN → o bloco final da resposta (`<<<…>>>`); outro papel → o bloco final. A frase final "Quando terminar, me peça de novo, eu continuo daqui." fica |
| U6 | MUST | Slot com valor inválido (ex.: `autonomous: sim`) sai 64; o aluno precisa saber que o encadeamento ficou desligado e como consertar | Princípio 1 (causa e conserto) | `⚠️ sdd-open: flow.autonomous = "sim" em sdd/config.yaml não é true nem false — encadeamento desligado.` + `→ troque por true (liga) ou false (desliga)` |
| U7 | MUST | A build nunca encadeia para a release; sem dizer, quem ligou o slot espera que publique | Princípio 2; D1 | Com o slot ligado, o `seguir … release` diz: `PARAR: publicar não se desfaz — é decisão sua (D1).` e o agente mostra o Próximo passo da release como pergunta `[D1 · não se desfaz]` |
| U8 | SHOULD | O `FLUXO_ENCADEADO.md` do privado tem a pergunta D4 do teto como prosa; quando a F10 ligar o `loop`, o agente vai improvisar | Continuidade | O fragmento traz a pergunta D4 completa, no formato (marca, recomendada primeiro, "não sei"): **mais 1 rodada com outra abordagem** · **aceitar e registrar como dívida** · **voltar ao DESIGN**; o `--sites` também confere os fragmentos (`sdd/templates/fragments`) |
| U9 | SHOULD | `review-design`, `loop` e os lints são lidos pelo agente; precisam do padrão do pacote para o agente traduzir sem inventar | `docs/cli-conventions.md` | `RESULTADO: <PALAVRA>` + `→` em toda saída que não é sucesso; `ESTADO:` no `loop` (contrato do privado) seguido de `RESULTADO:`; `🛑/⚠️/✅/🟢/ℹ️` sempre com palavra; sem cor |
| U10 | SHOULD | `docs/chained-flow.md` é o único lugar que explica tudo junto para quem quer ligar | Teste do estranho | Seções: o que muda ligado × desligado; como ligar e desligar (o slot e "pare"); a tabela das 6 marcas com o rótulo; os exits dos verbos; a parada do exit 40 com um exemplo; que a release nunca encadeia |
| U11 | COULD | O `doctor` não diz se o encadeamento está ligado | Continuidade | Linha `ℹ️ encadeamento: ligado|desligado (flow.autonomous em sdd/config.yaml)` |
| U12 | WONT | Contador de "decisões automáticas" por feature | Gamificação | Dispensado: medir o automático ensinaria a ligar o slot para "ganhar" velocidade |

---

## North Star Checks (Premium + Self-Evident)

| Check | Status | Note |
|---|---|---|
| Hierarquia em 200 ms | OK com U2 | A 1ª linha da transição diz o que terminou e o que começa |
| Estado ambíguo | MUST U2, U3, U6 | "Por que não perguntou?", "ficou ligado?" respondidos na própria linha |
| Erro com causa e conserto | MUST U6, U9 | Valor inválido com o conserto; `RESULTADO:` + `→` |
| Um símbolo por significado | OK com U9 | `✅ ⚠️ 🛑 🟢 ⏸️ ℹ️`, sempre com palavra |
| Teste do estranho | OK com U1, U10 | A marca se explica sozinha; o doc explica o resto |
| Teste do suporte | OK com U1, U5, U7 | "o que é D2?", "o que eu colo?", "por que não publicou?" respondidos |

---

## Gamification Strategy

Dispensada (U12). O encadeamento é conveniência opcional; recompensar o automático empurraria o aluno a ligar o slot sem entender o que deixa de ver.

---

## 60/30/10 Visual Strategy

N.A.: texto de chat e de terminal, sem cor (F8 U14). A hierarquia vem da ordem (linha de transição → recibo → próxima fase; parada: Status ⏸️ → por que parei → onde → passos → o que não foi feito → brief) e dos símbolos.

---

## Surface Assignment

| Surface | Quem lê | Papel |
|---|---|---|
| Marca da classe nas perguntas | aluno | Dizer em 2–4 palavras que tipo de decisão é |
| Linha de transição (`seguir` 0) | aluno, via agente | Dizer que a próxima fase começou e por quê |
| Recibo "Decidi sozinho" | aluno | O que foi decidido sem ele e como desfazer |
| Parada do exit 40 | aluno, via agente | O que fazer, onde, e o que trazer de volta |
| Saída de `review-design`, `loop`, lints | agente | Decisão por exit, com `RESULTADO:` e motivo |
| Subseção das skills, `FLUXO_ENCADEADO.md`, `docs/chained-flow.md` | agente, aluno avançado | O contrato e a explicação completa |

---

## Interaction Requirements

- Com o slot desligado, toda pergunta continua sendo feita; a única diferença visível é a marca com o rótulo (U1, U3).
- Com o slot ligado, `[D1]`…`[D5]` continuam perguntadas; `[auto]` vira a recomendada e uma linha do recibo; a fase seguinte começa depois da linha de transição, sem pergunta.
- "Pare" (ou `--parar`) numa fase desliga o encadeamento só naquela chamada; a linha de transição e o doc dizem isso.
- A build nunca segue para a release, com o slot ligado ou não (U7).
- Na parada do exit 40, nada é publicado nem gravado no relatório; a sessão de origem retoma quando a pessoa cola o retorno (U5).

---

## Required States

| Estado | Superfície | O que aparece |
|---|---|---|
| Sucesso (segue) | `seguir` 0 | `✅ <DOC> pronto → seguindo para <o/a> <DOC> (encadeamento ligado em sdd/config.yaml)` + recibo, se houver |
| Desligado | `seguir` 1, motivo "desligado" | nada novo: o Próximo passo de hoje (U3) |
| Parado com o slot ligado | `seguir` 1, outro motivo | 1 frase com o motivo (gate, marcador, release = D1, `--parar`) + o Próximo passo |
| Erro de configuração | `seguir` 64 | `⚠️ sdd-open: flow.autonomous = "<v>" … encadeamento desligado.` + `→ troque por true ou false` (U6) |
| Aguardando a pessoa | `despachar` 40 | Parada ⏸️ com Brief, Sessão nova e o que trazer de volta (U5) |
| Aguardando recibo | `loop` 30 | `ESTADO: AGUARDANDO_RECIBO` (parada que não é decisão: percorrer o roteiro e assinar) |
| Bloqueado | `loop` 20 | `ESTADO: BLOQUEADO` + motivo com a classe; o agente faz a pergunta D4/D5 do fragmento (U8) |
| Vazio | recibo sem decisões | bloco omitido |

---

## Content and Copy Guidance

- Português, frases curtas; rótulo da marca em minúsculas, 2–4 palavras, igual em toda skill (U1).
- O motivo antes do código: "publicar não se desfaz — é decisão sua (D1)", não "D1: release".
- Nomes de documento em maiúsculas na linha de transição (DEFINE, DESIGN, UX REVIEW, GOVERNANÇA, BUILD), com o artigo certo.
- "papel fresco" e "sessão nova", nunca o nome da ferramenta de um agente (P2).
- Comando só quando a pessoa precisa rodá-lo; na parada, um por passo, com o que esperar.

---

## Accessibility and Responsiveness

- Sem cor; todo símbolo com palavra.
- Linha de transição ≤ 100 caracteres (cabe no chat estreito e no terminal de 100 colunas).
- Caminho do brief inteiro, numa linha, para colar.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | Sem alvo de clique |
| L2 Escolhas por passo | RECOMENDAÇÃO | A pergunta D4 do teto tem 3 saídas + "não sei"; não acrescentar uma 4ª saída de trabalho `(lente L2)` |
| L3 Retomada | OK com U5 | A parada do exit 40 diz o que trazer de volta; a sessão de origem continua de onde parou |
| L4 Convenção | OK | Linha de transição e recibo seguem o formato do resumo de etapa que o aluno já conhece |
| L5 Progresso real | OK | O encadeamento só segue com o artefato da fase em `Ready for …` e o bloco do gate válido (`seguir` lê o Status e roda `verify-gate.sh --print`), nunca por estimativa; o gate que executa continua sendo o do build e da release |
| L6 Destaque único | ALERTA | Com o slot ligado, o fim de fase acumula resumo de etapa, recibo e linha de transição; a linha de transição vem por último, logo antes da fase seguinte, para não competir com o recibo |
| L7 Agrupamento | RECOMENDAÇÃO | No recibo, uma linha por decisão na ordem em que foram tomadas; mais de 5 ⇒ agrupar por fase `(lente L7)` |
| S Sinal de validação real | — | `grep -c '"exit":2' sdd/traces/<F>.jsonl` já conta voltas vermelhas (F7); o sinal do encadeamento seria quantas features chegaram ao build sem nenhuma pergunta `[auto]` desfeita — fica como pergunta ao Roberto na F15, não como critério |

---

## Design Handoff

- **Marca (U1):** tabela de 6 marcas com rótulo no item 9 do `PERGUNTA_DECISAO.md`; formato `[<código> · <rótulo>]` antes da pergunta em negrito; o lint confere código e rótulo contra a tabela (lida do fragmento, dono único) e o `[Dn]` continua no texto do item.
- **Linha de transição (U2, U7):** texto exato do `seguir`, com o nome do documento e o artigo; release sempre PARAR com a frase do D1.
- **Desligado (U3):** a subseção das skills diz ao agente que o motivo "desligado" não é repassado.
- **Recibo (U4):** formato `- <decisão> — porque <…> · para desfazer: <…>` em `FLUXO_ENCADEADO.md`.
- **Exit 40 (U5):** `despachar` imprime os passos com o que trazer de volta por papel.
- **Erro de slot (U6):** texto exato da linha ⚠️ e do `→`.
- **Fragmento (U8):** a pergunta D4 do teto escrita no formato; `--sites` também sobre `sdd/templates/fragments`.
- **Saída dos scripts (U9):** `RESULTADO:` + `→`; `ESTADO:` no `loop`.
- **Docs (U10):** `docs/chained-flow.md` + PT com as 6 seções.
- **Recomendações de lente:** L2 (3 saídas na D4), L7 (recibo em ordem), alerta L6 (linha de transição por último).
- **Como medir depois:** sinal S como pergunta para a F15.
- **Notas de aceite:** os testes conferem a marca com o rótulo (AT-018/AT-019/AT-022), a linha de transição exata (AT-013), o formato do recibo (AT-023), os passos da parada (AT-011) e a mensagem do slot inválido (AT-015) — o DEFINE sobe para v1.1 com esses textos.

---

## Open UX Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-31 | ux-review-command | Versão inicial |

---

## Next Step

`/sdd-design sdd/features/DEFINE_F9_FLUXO.md`
