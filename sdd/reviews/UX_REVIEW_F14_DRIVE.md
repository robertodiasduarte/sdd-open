# UX REVIEW: F14 Drive e orquestração

> UX/CX review for `F14_DRIVE` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F14_DRIVE |
| **Date** | 2026-11-05 |
| **Author** | ux-review-command (sdd-ux-review 2.5.0) |
| **DEFINE** | [DEFINE_F14_DRIVE.md](../features/DEFINE_F14_DRIVE.md) |
| **Status** | Ready for Design |
| **Lentes** | 3 recomendações · 0 alertas. Não mudam o Status |

Lidos antes: `UX_REVIEW_F12_CONTEXTO.md`, `UX_REVIEW_F13_UX_LLM.md` e `UX_REVIEW_F14_PLAYBOOK.md`. Vêm deles:
- o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2);
- a marca com rótulo em toda pergunta de decisão (F9 U1);
- "a linha de aviso diz a consequência, não só o fato" (F10 U4);
- a parada diz o que **não** foi feito (F4; F14 U2);
- público: quem conduz uma feature no Open, em geral sem hábito de terminal (entrevista da F5, sem mudança).

---

## UX Summary

A interface da `F14_DRIVE` é texto, lido no chat do agente ou no terminal, em 7 superfícies:
1. **a linha de progresso** de cada ação do drive;
2. **as paradas do drive**, com os 12 motivos;
3. **as 2 perguntas** do drive: limite de rodadas e teste final alterado;
4. **a parada sem subagente**, que pede uma sessão nova a cada tarefa;
5. **o `DRIVE_REPORT`**;
6. **as frases do `deploy-do-sha.sh`**, no fim da release;
7. **a saída do `sdd-archive.py`** e `docs/drive.md` + PT.

O maior risco é o **"já publicou?"**: um piloto automático que termina com um verde parece ter terminado tudo. O segundo é o **"travou ou está trabalhando?"**, numa execução longa que não pergunta nada. O terceiro é o **"quebrou?"**, com o deploy demorando ou o limite de rodadas acabando.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Quem conduz uma feature no Open e pede para o piloto levar o DEFINE até perto da publicação; o agente roda os scripts e traduz |
| **User Goal** | Sair do DEFINE aprovado e voltar só para decidir, sabendo o que foi feito e o que falta |
| **Primary Pain** | Acompanhar cada volta à mão; não saber se uma parada é erro ou decisão; medo de algo ir ao ar sem o OK |
| **Business/CX Goal** | Menos interrupção sem perder o controle: autonomia que o aluno confia e sabe desfazer |
| **Device/Context** | Chat do agente ou terminal; a pessoa pode sair e voltar horas depois, às vezes em outra sessão |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Tem um DEFINE pronto | Medo de soltar o controle | Antes da 1ª ação, 1 frase: o que vai fazer, o limite de rodadas e que para antes de publicar (U1) |
| Entry | Chamar o drive | Recusa sem motivo claro | Motivo em palavras e o que fazer: branch, DEFINE, dúvida aberta (U2) |
| Core Action | Deixar rodar | "Travou?" | `rodada 1/3 · tarefa 4 de 12` em toda ação (U3) |
| Feedback | Ver o teste vermelho | Achar que falhou de vez | Vermelho é normal: diz quantas rodadas restam e o que vem agora (U3) |
| Recovery | Limite acabou; teste alterado | Não saber decidir | Pergunta com o que falhou, os efeitos e a recomendada (U4, U5) |
| Interrupção → Retomada | Sessão caiu ou voltou no dia seguinte | Perder o trabalho | `--resume` diz onde parou e o que já está pronto, e nada é refeito (U6) |
| Conclusão | Viu o verde | "Já publicou?" | `Nada foi publicado` na mesma frase do verde, com o próximo passo (U1) |
| Follow-up | Publicar e ver no ar | Deploy longo parece travado | Espera com tempo decorrido; "não concluído" nunca é dito como "falhou" (U7) |

---

## UX/CX Findings

| # | Priority | Finding | Fonte | Recommendation |
|---|----------|---------|-------|----------------|
| U1 | MUST | Verde no fim de um piloto automático é lido como "está no ar" | teste do suporte | `gate-verde` sai com `O teste final passou e os relatórios estão prontos. Nada foi publicado.` e `→ revise os commits e, para publicar, chame a sdd-release.`; a skill abre com 1 frase: o que fará, `até N rodadas`, `paro antes de publicar` |
| U2 | MUST | Nome do motivo (`estado-invalido`, `branch-padrao`) é jargão | princípio 2; camada de conversa | Toda parada imprime `motivo: <nome>` e, na linha seguinte, a frase simples da tabela do Content Guidance; a skill repassa a frase, não o nome; glossário em `references/como-falar.md` |
| U3 | MUST | Execução longa sem pergunta parece travada; vermelho parece fim | L5; teste do estranho | Toda ação imprime `rodada: k/N` e, em `RODADA`, `tarefa: i de n — <arquivo>`; `CORRIGIR` diz `o teste final ficou vermelho (normal nesta etapa): restam R rodada(s)`, com o log |
| U4 | MUST | No limite de rodadas, "subir o limite" sem contexto vira chute | LM do método: D4 é da pessoa | Pergunta `[D4 · limite de tentativas]`: o que continuou falhando (do log), as rodadas gastas, e as opções **corrigir o DESIGN e seguir (recomendado)**, **dar mais 1 rodada**, **parar aqui**, **não sei** |
| U5 | MUST | `gate-alterado` é a parada mais estranha para quem não viu o agente mudar nada | decisão do Roberto | Pergunta `[D2 · muda o produto]`, com o comando de antes e o de agora em linhas separadas e o efeito: **voltar o comando antigo (recomendado)**, **aceitar o novo** (fica escrito no relatório), **não sei** |
| U6 | MUST | Quem volta numa sessão nova não sabe onde parou | L3 | `--resume` imprime `retomando: rodada k/N · x de n tarefas prontas · último teste final: <exit>` antes da ação, e `não gastei rodada` |
| U7 | MUST | Deploy que demora parece quebrado; "não concluí" lido como "falhou" assusta | teste do suporte; F10 U4 | ✅ só no ar; `⏳ <status> · 12/40 min · run <id>`; exit 4 diz `ainda não sei: o deploy não terminou em 40 min; isso não é falha` e o que fazer; 🔴 diz o run, o passo e por que não repetiu |
| U8 | MUST | Sem subagente, uma parada por tarefa é surpresa no meio do caminho | P2; F14 U2 | A 1ª parada avisa `esta execução tem n tarefas: sem subagente, são até n paradas; você pode parar e voltar quando quiser`; cada parada diz qual tarefa e o que **não** foi feito (`nada foi publicado`) |
| U9 | MUST | Faxina assusta: "vai apagar meus documentos?" | princípio 2 | `sdd-archive.py` sem `--aplicar` termina em `Nada foi movido.`; `--aplicar` diz `movi N arquivo(s) com git mv, nada foi apagado; revise e commite`; protegido sai com o porquê: `ficha aberta em HANDOFF_<F>.md` |
| U10 | SHOULD | `DRIVE_REPORT` sem veredito na 1ª linha obriga a ler a tabela | F9 U2 | 1ª seção com 1 frase: motivo em palavras, rodadas usadas e `Nada foi publicado.`; depois a tabela por rodada |
| U11 | SHOULD | Mecanismo sem página | F6/F9/F10: o mecanismo vem com o documento | `docs/drive.md` + PT, com uma execução de exemplo, a tabela de motivos e como desfazer |
| U12 | SHOULD | Guarda do avaliador que libera documento não rastreado, em silêncio, esconde que ele não está salvo | teste do suporte | `ℹ️ N documento(s) de sdd/ não rastreado(s) ficam fora do commit: eles não voltam se a pasta for limpa.` |
| U13 | COULD | A pessoa quer saber o que ficou no `[auto · de rotina]` | F9, recibo | Seção `Decidi sozinho` no `DRIVE_REPORT`, com o sinal e como desfazer |
| U14 | WONT | Notificação quando terminar | cada agente tem a sua | Sem canal comum entre os 7 agentes |
| U15 | WONT | Estimativa de tempo ou custo antes de rodar | nenhum script lê o gasto do agente (D11) | Número inventado seria pior que nenhum |
| U16 | WONT | Saída colorida | `docs/cli-conventions.md` | Cor nunca carrega significado |

---

## North Star Checks (Premium + Self-Evident)

| Check | Pass/Fail | Notes |
|-------|-----------|-------|
| Hierarquia em 200 ms | Pass | `motivo:` + frase + `→` no fim de toda saída |
| Um símbolo por significado, sempre com palavra | Pass | ✅ no ar ou pronto · ⏳ esperando · 🔴 falhou · ⏸️ parada |
| Erro com causa e conserto | Pass | toda parada tem a frase e a seta (U2) |
| Teste do estranho | Pass com U1, U3 | completa a tarefa pedindo só a sdd-drive |
| Teste do suporte: "já publicou?" | Pass com U1 | a frase vem junto do verde |
| Teste do suporte: "travou?" | Pass com U3, U7 | a linha de progresso e o tempo decorrido respondem |
| Teste do suporte: "vai apagar?" | Pass com U9 | simulação por padrão e a frase no fim |
| Estado ambíguo | Pass com U7 | não concluído ≠ falhou, com exits diferentes |

---

## Gamification Strategy

Dispensada: a barra de progresso real (U3) já serve; ponto ou conquista num gate pioraria a leitura de uma parada séria.

---

## 60/30/10 Visual Strategy

N.A. — superfície só de texto, sem tela; hierarquia por ordem das linhas e por símbolo com palavra.

---

## Surface Assignment

| Surface | Conteúdo | Quem lê |
|---------|----------|---------|
| Saída dos scripts | ação ou motivo, frase, seta | o agente, que traduz |
| Chat | Status, frase, pergunta | a pessoa |
| `DRIVE_REPORT_<F>.md` | veredito, rodadas, commits, decisões | a pessoa, depois |
| `docs/drive.md` | como funciona | quem vai adotar |

---

## Interaction Requirements

| Interaction | Requirement |
|---|---|
| Chamar | `/sdd-drive sdd/features/DEFINE_<F>.md`, opcional `--max N`; a execução é o opt-in |
| Progresso | sem pergunta nas ações de rotina; uma linha por ação |
| Decidir | só D1 a D5; `[auto · de rotina]` vai para o recibo |
| Retomar | "continue o drive" numa sessão nova roda `--resume` |
| Desfazer | commits atômicos; a pessoa reverte; nada é publicado |

---

## Required States

| State | Comportamento |
|---|---|
| Loading | ação com `rodada: k/N`; deploy com tempo decorrido |
| Vazio | archive sem nada a mover: `Nada a mover.`, totais em 0, exit 0 |
| Erro | parada tabelada com frase e seta; script que não consegue gravar: exit 2 com a causa |
| Sucesso | `gate-verde` com `Nada foi publicado.`; `✅ no ar` |
| Parcial | `orcamento-rodadas` e `bloqueio-humano`: o que ficou pronto continua nos commits, dito na frase |
| Sem permissão | `gh` sem login: exit 3 inconclusivo, nunca "falhou"; dispatch recusado: exit 2 com o porquê |
| Desabilitado | `drive.max_rounds` inválido: exit 64 dizendo de onde veio; `deploy.transient_steps` vazio: "nunca repito sozinho" |

---

## Content and Copy Guidance

| Motivo | Frase para a pessoa |
|---|---|
| `gate-verde` | O teste final passou e os relatórios estão prontos. Nada foi publicado. |
| `simulacao` | Simulação: nada foi executado nem gravado. |
| `orcamento-rodadas` | O teste final continuou vermelho nas N rodadas permitidas. Nada foi publicado. |
| `manual-ux` | O teste final precisa da conferência de uma pessoa. Nada foi publicado. |
| `clarificacao-pendente` | O DEFINE ainda tem dúvida aberta ou a revisão de governança pendente. |
| `define-invalido` | O DEFINE não tem um teste final válido. |
| `gate-inconclusivo` | O teste final não chegou ao fim: isso não é vermelho e não gastou rodada. |
| `gate-alterado` | O comando do teste final mudou desde o início desta execução. |
| `bloqueio-humano` | A construção parou e precisa de você. Nada foi publicado. |
| `aguardando-sessao` | Esta etapa precisa de uma sessão nova do agente. Nada foi publicado. |
| `estado-invalido` | Não consegui ler onde a execução parou, e não vou adivinhar. |
| `branch-padrao` | O piloto não roda na branch principal: ele precisa de uma frente de trabalho própria. |

Glossário de `references/como-falar.md`: drive = "o piloto que constrói e confere sozinho até o teste final passar"; rodada = "uma passada construindo o que falta, mais o teste final"; teste final = Verify Gate; frente = worktree.

---

## Accessibility and Responsiveness

N.A. para WCAG — sem superfície visual: a saída é texto, sem cor; o símbolo vem sempre com palavra (leitor de tela lê a palavra). Linhas de progresso espaçadas: 1 por minuto ou quando o estado muda (`--intervalo` não vira ruído).

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|-------|--------|-----------|
| Alcance (Fitts) | N.A. | Sem alvo de clique |
| Escolhas por passo (Hick-Hyman) | OK | 2 perguntas no drive, 3 opções e "não sei" |
| Retomada (Zeigarnik) | RECOMENDAÇÃO | `--resume` mostra o que falta e o estado vem do disco, sem depender da conversa `(lente L3)` |
| Convenção (Jakob) | OK | Exits 0/10/20/40/64 no padrão do `sdd-fluxo.sh`; `RESULTADO:` + `→` |
| Progresso real (Gradiente de meta) | RECOMENDAÇÃO | `tarefa: i de n` lido do `PROGRESS`, nunca estimado `(lente L5)` |
| Destaque único (Von Restorff) | RECOMENDAÇÃO | A frase do motivo é a última antes da seta; detalhe vai para o log `(lente L6)` |
| Agrupamento (Miller) | OK | Archive por lote, com totais |
| Sinal de validação real | — | Quantas execuções chegaram a `gate-verde` sem parada não tabelada, na F15; não é critério |

---

## Design Handoff

Concrete requirements for `/design`:

- **Frases dos 12 motivos (U1, U2):** tabela única no script, conferida por teste contra `docs/drive.md`.
- **Progresso (U3):** `rodada: k/N` e `tarefa: i de n — <arquivo>`.
- **Perguntas (U4, U5):** `references/como-falar.md` da `sdd-drive`, com as marcas e os efeitos.
- **Retomada (U6):** linha `retomando:` no `--resume`.
- **`deploy-do-sha.sh` (U7):** 1 frase por desfecho, progresso em stderr.
- **Parada sem subagente (U8):** caso `executor-drive` no `sdd-fluxo.sh despachar`, aviso das n paradas na skill.
- **`sdd-archive.py` (U9):** frases finais e o porquê de cada protegido.
- **`DRIVE_REPORT` (U10, U13)**, **docs (U11)**, **guarda (U12)**.
- Gamificação dispensada.
- (lente L3) Estado no disco. (lente L5) Progresso do `PROGRESS`. (lente L6) Frase por último.
- Como medir depois: execuções que chegaram ao verde, na F15.

Components likely needed:

- Tabela de motivos no núcleo Python de `sdd-drive.sh`.
- Caso `executor-drive` no `sdd-fluxo.sh despachar`.
- `references/como-falar.md` da `sdd-drive`.

Acceptance notes:

- [ ] O DEFINE sobe para v1.1 com U1 e U2 em AT-015 e AT-019, U3 em AT-005 e AT-008, U4 e U5 em AT-019, U6 em AT-012, U7 em AT-022 e AT-026, U8 em AT-020, U9 em AT-028 e AT-029 e U12 em AT-032.
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

**Ready for:** `/sdd-design sdd/features/DEFINE_F14_DRIVE.md`
