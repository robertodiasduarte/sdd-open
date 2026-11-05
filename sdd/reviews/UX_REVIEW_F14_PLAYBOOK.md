# UX REVIEW: F14 Playbook, invariantes e sessão

> UX/CX review for `F14_PLAYBOOK` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F14_PLAYBOOK |
| **Date** | 2026-11-05 |
| **Author** | ux-review-command (sdd-ux-review 2.5.0) |
| **DEFINE** | [DEFINE_F14_PLAYBOOK.md](../features/DEFINE_F14_PLAYBOOK.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

Lidos antes: `UX_REVIEW_F12_CONTEXTO.md` e `UX_REVIEW_F13_UX_LLM.md`. Vêm deles:
- o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2);
- a marca com rótulo em toda pergunta de decisão (F9 U1);
- "a linha de aviso diz a consequência, não só o fato" (F10 U4);
- o susto depois de atualizar o pacote tem texto próprio (F12 U1, F13 U4);
- público: quem conduz uma feature no Open, em geral sem hábito de terminal (entrevista da F5, sem mudança).

---

## UX Summary

A interface da F14 é texto, lido no chat do agente ou no terminal, em 6 superfícies:
1. **a pergunta da curadoria** no fim da release, a única decisão que a pessoa toma aqui;
2. **o recibo** do que entrou sem pergunta;
3. **a parada do curador** em agente que não abre outra sessão sozinho, que acontece depois de a publicação terminar;
4. **as saídas do `playbook-curator.sh`**, que o agente traduz;
5. **a saída do `copiar-docs.sh`**, na abertura de uma frente;
6. **o molde do handoff** e `docs/playbook-curation.md` + PT.

O maior risco é o **"minha publicação travou?"**: a curadoria roda depois do push, e uma parada, uma falha de coleta ou uma trava de invariante lidas sem contexto parecem um deploy pela metade. O segundo é o **jargão**: delta, tombstone, promover e invariante chegam à pessoa na pergunta mais importante do passo.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Quem publica uma feature no Open e mantém o playbook do projeto; o agente roda os scripts e traduz |
| **User Goal** | Fechar a release sabendo quais lições foram contadas e decidir, em poucas respostas, o que muda nas regras |
| **Primary Pain** | Lista de mudanças em jargão, sem saber o que é contagem e o que é regra; medo de ter quebrado a publicação |
| **Business/CX Goal** | Playbook que melhora a cada release sem virar interrogatório; menos dúvida de suporte |
| **Device/Context** | Chat do agente ou terminal; fim de uma sessão longa, com a atenção já gasta no OK da publicação |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Acabou de dar o OK e viu a publicação no ar | Alívio; qualquer parada agora assusta | Toda mensagem da curadoria começa dizendo que a publicação já terminou (U2) |
| Entry | Ver o que a feature ensinou | Não saber o que é "curadoria" | Uma frase: "agora eu confiro o que esta feature ensinou para as próximas" (U4) |
| Core Action | Responder à pergunta | Jargão; lista longa | Um item por linha, em palavras simples, até 5 por vez (U1) |
| Feedback | Saber o que entrou sozinho | Achar que o agente mudou regra sem pedir | Recibo com o que foi contado e como desfazer (U6) |
| Recovery | Entender uma trava | "trava INV" sem saída | Causa, as 2 saídas e a opção única (U5) |
| Interrupção → Retomada | Fechar a janela na parada do curador | Perder a colheita | A pasta da colheita tem nome que a sessão seguinte refaz; a parada diz que a publicação não depende disso (U2) |
| Completion | Encerrar | Dúvida se ficou algo pendente | A ficha ganha a linha da curadoria com os números (U3) |
| Follow-up | Lembrar por que uma lição foi aposentada | Linha sem motivo | O motivo fica na linha de `## Tombstones` e o log da curadoria na pasta de evidência |

---

## UX/CX Findings

| # | Priority | Finding | Fonte | Recommendation |
|---|----------|---------|-------|----------------|
| U1 | MUST | A pergunta da curadoria é a única decisão do passo e chega com os termos mais estranhos do método | privado `release.md` 17b, item 4; `PERGUNTA_DECISAO.md` | Um item por linha numerada, cada um com **o que aconteceu** e **o que muda se aceitar**, vindos da coluna de linguagem simples; o ID só no fim, como `(ref: LM-020)`. Resposta por número: `1 aceitar, 2 recusar`. Cada item tem `aceitar`, `recusar` e `não sei`, com a recomendada primeiro. Até 5 itens por pergunta; acima disso, em lotes. Marca `[D3 · muda a regra do método]` |
| U2 | MUST | A curadoria roda depois do push; uma parada ali parece deploy travado | teste do suporte; F10 U4 | A parada do curador abre com `A publicação já terminou e não depende deste passo.` e, em "O que não foi feito", `a curadoria do playbook ainda não foi aplicada; nada foi despublicado.` |
| U3 | MUST | `Curadoria: FALHOU (rc=2)` sozinho não diz a causa nem o que fazer | P4 do plano; F8 U2 | Para a pessoa: `Não consegui ler o playbook para a curadoria (<causa do script>). A publicação não foi afetada. → corrija <arquivo> e me peça a curadoria de novo.` A linha `Curadoria: FALHOU (rc=N)` fica na ficha, como registro |
| U4 | MUST | "0 deltas", "tombstone", "promover", "invariante" são jargão | princípio 2; camada de conversa | Glossário em `references/como-falar.md` da `sdd-release` e da `sdd-playbook`: curadoria = "conferir o que esta feature ensinou para as próximas"; delta = "uma mudança de uma linha no playbook"; aposentar (tombstone) = "tirar uma lição de uso, guardando o motivo"; promover = "transformar a lição numa trava automática"; invariante = "regra que nunca pode ser quebrada, com o teste que a vigia". "0 deltas" vira "esta feature não trouxe lição nova nem contagem" |
| U5 | MUST | Aposentar uma lição da qual uma invariante depende, em 2 perguntas separadas, permite aceitar metade e travar | privado, UX review do s3 (opção atômica) | Uma opção só: `aposentar o aviso sobre <tema> e ajustar a regra permanente que dependia dele, no mesmo passo`. A mensagem da trava nomeia a regra, a lição e as 2 saídas: aceitar o ajuste ou retirar a aposentadoria |
| U6 | MUST | Contagem aplicada sem pergunta, sem recibo, parece o agente mexendo em regra sozinho | F9 (recibo "Decidi sozinho") | Recibo com 1 linha por contagem em palavras simples (`o aviso sobre <tema> foi seguido e evitou o erro: contei +1`) e como desfazer: `para desfazer, reverta o commit da curadoria (<sha>)` |
| U7 | MUST | "Parecido, não copiado" sem motivo parece falha da cópia | privado `new-session.sh`; teste do suporte | `PARECIDO <arquivo> (feature '<x>' ≈ frente '<y>'): não copiei, porque o nome não é idêntico.` e o `→` final: `se algum for desta frente, copie para <pasta>/sdd/features/`. Nada a copiar não é erro: `RESULTADO: NADA A COPIAR` |
| U8 | MUST | No primeiro uso depois de atualizar, um projeto com lições antigas já "no universo" reprova na trava sem nada ter mudado nele | F12 U1, F13 U4 | Antes dos itens: `o registro de invariantes é novo na v2.6.0: <N> lição(ões) antiga(s) ainda não foram classificadas.` Cada uma vira um item da pergunta (virar regra permanente, ou descartar com motivo). Projeto sem `sdd/invariants.md`: `invariantes: arquivo ausente, cruzamento pulado` e a curadoria segue |
| U9 | SHOULD | `--aplicar` imprime o playbook em stdout; `RESULTADO:` ali corromperia o arquivo | `docs/cli-conventions.md` | Em `--aplicar`, veredito e `→` vão para stderr; nos outros modos, a última coisa do stdout é `RESULTADO:` + `→`, depois da linha de resumo que as máquinas leem |
| U10 | SHOULD | O molde do handoff ganha 6 seções; seção sem orientação vira campo vazio | N3; princípio 2 | Cada seção nova com 1 linha de orientação e 1 exemplo de forma: Eventos (linha nova, nunca sobrescrita), Recomendações, Veredito, Setup (como preparar a pasta para retomar), Tarefas (numeradas, com "Pronto quando"), Ship (o que publicar e o que limpar) |
| U11 | SHOULD | Sem página que explique o mecanismo | F6/F9/F10: o mecanismo vem com o documento | `docs/playbook-curation.md` + PT, com um exemplo de curadoria do início ao fim e a gramática das invariantes; `docs/cli-conventions.md` com as palavras novas |
| U12 | COULD | A pergunta de promoção repete a cada release enquanto a lição não virar trava | privado: pergunta obrigatória | O item diz o custo (`virar trava pede uma correção própria, com teste`) e que recusar agora faz a pergunta voltar na próxima release |
| U13 | WONT | Lista de jargão proibido conferida por script | corte YAGNI do brainstorm | O conferidor só exige a coluna de linguagem simples preenchida; a qualidade da frase é do brief |
| U14 | WONT | Saída colorida | `docs/cli-conventions.md` | Cor nunca carrega significado |

---

## North Star Checks (Premium + Self-Evident)

Sem superfície visual: as dimensões visuais do bloco Premium são N.A.

| Critério | Status | Evidência |
|----------|--------|-----------|
| Erro com causa **e** conserto (Premium em CLI) | ✅ | U3, U5, U7, U8 |
| Um símbolo por significado, sempre com palavra | ✅ | `RESULTADO:` + `→`; 🔴 e 🟢 da trava sempre com "trava INV" |
| Tooltip-muleta / documentação como contrato | ✅ Não | A pergunta se decide sem abrir o playbook (U1); a doc só aprofunda |
| Estado ambíguo | ✅ Não, com U2 e U3 | Parada e falha dizem que a publicação terminou |
| Cor conflitando com semântica | N.A. | Sem cor |

**Teste do estranho:** quem nunca viu o playbook entende cada item da pergunta pela frase "o que aconteceu / o que muda"; hesitaria em "invariante", que o glossário traduz.

**Teste do suporte:** as 3 dúvidas prováveis ("minha publicação travou?", "o agente mudou regra sozinho?", "por que não copiou meu documento?") têm texto próprio (U2, U6, U7).

---

## Gamification Strategy

```text
Gamification decision: Not recommended because a curadoria é manutenção de regras ao fim de uma release; contadores ajudou/mordeu são medida do método, não placar da pessoa, e transformá-los em pontuação incentivaria inflar contagem.
```

---

## 60/30/10 Visual Strategy

N.A. — sem superfície visual: scripts de linha de comando, texto de skill, molde e documentação.

---

## Surface Assignment

N.A. — nenhuma surface visual proposta.

---

## Interaction Requirements

| Requirement | Why It Matters | Priority |
|-------------|----------------|----------|
| A pergunta da curadoria se decide sem abrir arquivo | Quem responde está no fim da sessão e não lê o playbook | MUST |
| Contagem nunca vira pergunta; mudança de regra nunca entra sem pergunta | Separa rotina de política | MUST |
| Toda mensagem depois do push diz que a publicação terminou | Evita o susto do deploy travado | MUST |
| Toda saída de script termina em `RESULTADO:` + `→` (stderr no `--aplicar`) | Um estado que não é sucesso nunca termina em silêncio | MUST |
| Gamificação dispensada | Ver a seção própria | WONT |

---

## Required States

| State | Required UX |
|-------|-------------|
| Loading | Antes do curador: `🧹 curadoria: julgando em contexto novo (alguns minutos); você não precisa responder` |
| Empty | Nada colhido: "esta feature não trouxe lição nova nem contagem" (U4); nada a copiar: `RESULTADO: NADA A COPIAR` (U7) |
| Error | Falha de coleta (U3); bloco do curador reprovado: o agente despacha de novo 1 vez sem perguntar e, se repetir, diz que a curadoria ficou para a próxima release |
| Success | Recibo (U6) e a linha da ficha `Curadoria: <n> propostos / <m> aplicados / <p> promoções` |
| Partial Data | Projeto sem `sdd/invariants.md`: cruzamento pulado e dito (U8) |
| Permission Denied | N.A. |
| Disabled | Agente sem subagente: parada com os passos (U2) |

---

## Content and Copy Guidance

| Surface | Guidance |
|---------|----------|
| Primary CTA | N.A.; o `→` começa por verbo |
| Helper Text | `--help` com 1 exemplo por modo |
| Error Copy | Causa + conserto, com o arquivo; "invariante" na 1ª vez: "regra que nunca pode ser quebrada" |
| Confirmation | O que foi contado, o que mudou e como desfazer |
| Empty State | Dizer que não houve lição, nunca "0 deltas" para a pessoa |

Saídas em português, frases curtas, como os outros scripts de `sdd/bin/`. No brief e nas skills, nunca o nome de uma ferramenta de um agente só (regra 10).

---

## Accessibility and Responsiveness

N.A. — sem superfície visual: nenhum critério WCAG da tabela se aplica (sem cor, foco, alvo de toque nem campo). Em CLI:

- Sem cor; todo símbolo com palavra.
- Linhas de status com até 100 caracteres, exceto caminho de arquivo e linha de delta, que ficam inteiros para colar.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|-------|--------|-----------|
| Alcance (Fitts) | N.A. | Sem alvo de clique |
| Escolhas por passo (Hick-Hyman) | RECOMENDAÇÃO | Até 5 itens por pergunta, 3 respostas por item, recomendada primeiro `(lente L2)` |
| Retomada (Zeigarnik) | RECOMENDAÇÃO | A pasta da colheita tem nome refazível; a sessão que retoma depois da parada acha a colheita sem colher de novo `(lente L3)` |
| Convenção (Jakob) | OK | Saídas 0/1/2/3/64 no padrão do `playbook-lint.sh`; `RESULTADO:` + `→` |
| Progresso real (Gradiente de meta) | OK | A linha da ficha traz os números medidos |
| Destaque único (Von Restorff) | ALERTA | A pergunta de promoção volta a cada release (U12); com 3 lições nessa situação, a pergunta útil se perde entre as repetidas. Fica registrado para a 2ª entrega ou depois: uma forma de adiar com data |
| Agrupamento (Miller) | OK | Itens em lotes de até 5, contagens fora da pergunta |
| Sinal de validação real | — | Quantas contagens o conferidor recusou por não estarem na colheita; fica para a F15, não como critério |

---

## Design Handoff

Concrete requirements for `/design`:

- **Pergunta da curadoria (U1, U5, U12):** exemplo em `sdd-release/references/como-falar.md` com item numerado, frase simples, `(ref: …)` no fim, opção única para aposentadoria que mexe em invariante, custo na promoção.
- **Parada do curador (U2):** texto próprio no `sdd-fluxo.sh despachar curador`.
- **Falha e vazio (U3, U4):** frases para a pessoa no 17b; glossário nas 2 skills.
- **Recibo (U6):** linha por contagem e o comando de desfazer.
- **`copiar-docs.sh` (U7):** linhas `COPIADO`, `JA_EXISTE`, `PARECIDO`, `IGNORADO`, e os 2 resultados.
- **Trava (U8):** frase da v2.6.0 antes dos itens; arquivo ausente pula e diz.
- **`playbook-curator.sh` (U9):** `RESULTADO:` + `→` em stdout, menos no `--aplicar`.
- **Molde do handoff (U10)** e **docs (U11)**.
- Gamificação dispensada.
- (lente L2) Lotes de até 5 itens.
- (lente L3) Pasta da colheita com nome refazível a partir da raiz do projeto e da feature.
- Como medir depois: contagens recusadas pelo conferidor, na F15.

Components likely needed:

- `playbook-curator.sh` com as mensagens acima.
- Caso `curador` no `sdd-fluxo.sh despachar`.
- `references/como-falar.md` da `sdd-release` e da `sdd-playbook`.

Acceptance notes:

- [ ] O DEFINE sobe para v1.1 com U2 no AT-023, U3 e U6 no AT-024, U1 e U5 no AT-025, U7 no AT-026 e AT-027, U8 no AT-015 e U9 no AT-011.
- [ ] Toda saída nova termina em `RESULTADO:` + `→`, conferida por teste.
- [ ] Sem cor e com símbolo sempre acompanhado de palavra.
- [ ] Gamificação dispensada, com o motivo registrado.
- [ ] **Premium**: em CLI, todo erro tem causa e conserto.
- [ ] **Self-Evident**: as 3 dúvidas do teste do suporte têm texto próprio.

---

## Open UX Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-05 | ux-review-command | Initial UX review |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F14_PLAYBOOK.md`
