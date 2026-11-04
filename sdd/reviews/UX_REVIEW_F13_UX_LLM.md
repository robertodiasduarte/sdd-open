# UX REVIEW: F13 UX e LLM no código

> UX/CX review for `F13_UX_LLM` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F13_UX_LLM |
| **Date** | 2026-11-04 |
| **Author** | ux-review-command (sdd-ux-review 2.4.0) |
| **DEFINE** | [DEFINE_F13_UX_LLM.md](../features/DEFINE_F13_UX_LLM.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

Lidos antes: `UX_REVIEW_F10_REVISAO.md` e `UX_REVIEW_F12_CONTEXTO.md`. Vêm deles:
- o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2, via F12);
- "símbolo sempre com palavra, sem cor" (F8 U8);
- a marca com rótulo em toda pergunta de decisão (F9 U1);
- "a linha de aviso diz a consequência, não só o fato" (F10 U4);
- o susto depois de atualizar o pacote tem texto próprio (F12 U1).

---

## UX Summary

A interface da F13 é texto, lido no chat do agente ou no terminal, em 6 superfícies:
1. **a saída do `contraste.sh`**, lida pelo aluno na UX review;
2. **a saída do `prompt-drift-scan.sh`**, que o agente traduz durante o Build;
3. **a mensagem nova do `design-lint.py`**, que aparece num DESIGN em andamento logo depois de atualizar o pacote;
4. **a conversa da `sdd-loop-builder`**, com termos que o aluno nunca viu (LOOP_SPEC, perfil, estágio);
5. **o roteador no Build**, que encadeia skills sem parar;
6. **a tabela WCAG** no `UX_REVIEW` gerado, mais `docs/llm-in-code.md` + PT.

O maior risco é o **"isso é bug?"** em 3 pontos: `4.47` no script contra `4.48` numa calculadora online; um `rgba(...)` colado do navegador que sai 64; e o `design-lint` reprovando um DESIGN que passava na véspera. Cada um tem texto próprio abaixo.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Quem conduz uma feature no Open, em geral sem hábito de terminal; o agente roda os scripts e traduz |
| **User Goal** | Saber se a tela é legível; especificar um processo com IA em laço; não deixar prompt de produção passar sem planejamento |
| **Primary Pain** | Regra sem ferramenta ("contraste medido"), termos novos e mensagens sem conserto |
| **Business/CX Goal** | Menos dúvida de suporte; confiança de que o número é medido |
| **Device/Context** | Terminal ou chat do agente; uso ocasional, no meio de uma fase |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Chegar à acessibilidade na UX review, ou ao item de prompt no Build | Não saber que a ferramenta existe | A skill nomeia o comando na hora em que ele é preciso |
| Entry | Medir um par de cores; especificar um laço | Colar a cor no formato do navegador | Mensagem que ensina o formato aceito (U3) |
| Core Action | Rodar o script, ou responder à skill | Termo desconhecido | Glossário e exemplo em `como-falar.md` (U5) |
| Feedback | Ler o resultado | Número diferente do da calculadora | Veredito, piso e explicação do truncamento (U1, U7) |
| Recovery | Consertar | Mensagem sem conserto | Causa + `→` com o comando (U1 a U4) |
| Interrupção → Retomada | Parar no meio da especificação do laço | Perder o contrato já compilado | O DESIGN guarda o contrato; a skill recomeça dele |
| Completion | Saber que está pronto | Achar que o scan limpo prova mais do que prova | O aviso do slot vazio diz o que não foi visto (U2) |
| Follow-up | Lembrar por que o número está na tabela | Linha sem evidência | O par medido fica no `UX_REVIEW` (U8) |

---

## UX/CX Findings

| # | Priority | Finding | Fonte | Recommendation |
|---|----------|---------|-------|----------------|
| U1 | MUST | Um REPROVA sem o piso nem o conserto não diz o que fazer; e a linha final de todo comando do pacote é `RESULTADO:` + `→` (`docs/cli-conventions.md`) | teste do suporte; convenção do pacote | 1ª linha `4.47:1 REPROVA (piso 4.5:1)`, depois `RESULTADO: REPROVA` e `→ escureça o primeiro plano ou clareie o fundo até 4.5:1; texto grande, borda e ícone usam --piso 3`. PASSA: `4.54:1 PASSA (piso 4.5:1)`, `RESULTADO: PASSA`, `→ anote o par e o número na tabela da UX review`. A 1ª linha continua fácil de ler por um script |
| U2 | MUST | "Limpo" com o slot vazio parece garantia, e foi assim que o gate do privado ficou cego por 4 meses | privado, histórico do scan; F10 U4 | `⚠️ prompts.wrapper_pattern vazio: procurei só os sinais genéricos; se o projeto chama a IA por uma função própria, esta varredura não a vê.` + `→ preencha o slot em sdd/config.yaml (ex.: systemPrompt:) ou ignore se o projeto usa o SDK direto`. Em DRIFT: `<caminho> :: <sinal em palavras>`, `RESULTADO: DRIFT` e `→ se é prompt de produção, inventarie no DESIGN; se não é, registre o falso positivo no relatório` |
| U3 | MUST | O `rgba(...)` colado do navegador é o erro mais provável do `contraste.sh`; "cor inválida" não ajuda | decisão do brainstorm (corte do `rgba`); teste do suporte | `🛑 cor não reconhecida: rgba(0,0,0,.5). Aceito #rgb ou #rrggbb.` + `RESULTADO: ERRO DE USO` + `→ a transparência vai como 3º valor: contraste.sh '#000000' '#ffffff' .5`. Toda saída 64 dos 2 scripts tem causa e conserto; a do caminho inexistente diz `confira o caminho do manifest ou use --conteudo para arquivo novo` |
| U4 | MUST | Um DESIGN que passava na véspera reprova no `design-lint` sem nada ter mudado nele | F12 U1 | Antes dos itens: `🛑 <arquivo>: a seção de prompts mudou na v2.5.0 e este inventário está no formato antigo.` Cada falta numa linha (`falta a coluna Versão no inventário`, `Prompt 2 sem o campo Eval mínimo pré-ship`), `RESULTADO: VERMELHO` e `→ copie as colunas de sdd/templates/fragments/LLM_PROMPTS_DESIGN.md; nada no código precisa mudar` |
| U5 | MUST | "LOOP_SPEC", "perfil", "estágio" e "verificador" são estranhos para quem usa a skill | princípio 2; camada de conversa | `references/como-falar.md` com glossário: LOOP_SPEC = "a ficha do processo: o que ele faz, como confere o resultado e quando para"; perfil = "o nível de cuidado, escolhido pelo estrago que um erro pode causar"; estágio = "cada passo do processo; alguns são IA, outros são código"; verificador = "quem confere o resultado sem ter gerado o resultado". Nunca "loop agêntico" sem traduzir |
| U6 | MUST | O roteador pede várias skills seguidas; o agente que para ao receber o bloco de texto deixa o aluno sem saber que precisa pedir "continue" | privado `build.md`, passo 2; AT-019 | A `sdd-build` manda seguir no mesmo turno e uma linha de andamento: `🔁 item em laço: especificação e <n> prompts (<nome>)`. Bloqueio: `🛑 não encontrei a skill <nome>; este item ficou de fora e nada foi improvisado.` + a pergunta `[D2 · muda o produto]` do Build |
| U7 | SHOULD | `4.47` no script e `4.48` numa calculadora online parecem defeito | decisão do brainstorm | `--help` e `docs/llm-in-code.md`: "o resultado é truncado de propósito: calculadoras costumam arredondar, e 4,496 arredondado apareceria como 4.50 e passaria" |
| U8 | SHOULD | A tabela WCAG pode virar "PASSA" sem evidência | princípio 2 | Evidência obrigatória por linha: `#rrggbb sobre #rrggbb → N.NN:1` em contraste; lista de sinais em 1.4.1; controle → atributo em 4.1.2. `N.A.` exige motivo. Projeto com 2 temas mede os 2, porque o número de um não transfere ao outro |
| U9 | SHOULD | Sem página que explique os mecanismos | F6/F9/F10: o mecanismo vem com o seu documento | `docs/llm-in-code.md` + PT; `docs/cli-conventions.md` com os 2 scripts e as palavras `PASSA`, `REPROVA`, `DRIFT`, `LIMPO` |
| U10 | COULD | Quem pede um laço que não é laço pode achar que a skill recusou | teste do estranho | Mensagem da saída sem laço: "isto é uma chamada única: nenhuma resposta da IA decide o passo seguinte. A `sdd-prompt-builder` resolve com menos trabalho" |
| U11 | WONT | Aceitar `rgba(...)` | decisão do Roberto | U3 ensina o formato aceito; volta se a dúvida aparecer em uso |
| U12 | WONT | Saída colorida no terminal | `docs/cli-conventions.md` | Cor nunca carrega significado |

---

## North Star Checks (Premium + Self-Evident)

Sem superfície visual: as dimensões visuais do bloco Premium são N.A.

| Critério | Status | Evidência |
|----------|--------|-----------|
| Erro com causa **e** conserto (Premium em CLI) | ✅ | U1, U2, U3, U4 |
| Um símbolo por significado, sempre com palavra | ✅ | `RESULTADO:` + `→`; 🔁 só no roteador |
| Tooltip-muleta / documentação como contrato | ✅ Não | A mensagem ensina na hora; a doc só aprofunda (U7) |
| Estado ambíguo | ✅ Não, com U2 | "Limpo" sempre diz o que não foi visto, quando o slot está vazio |
| Cor conflitando com semântica | N.A. | Sem cor |

**Teste do estranho:** quem nunca viu a skill entende, pelo glossário, o que é a ficha do processo e por que há perfis. Hesitaria em "wrapper"; a mensagem do U2 diz "uma função própria".

**Teste do suporte:** os 3 "isso é bug?" do resumo têm texto próprio (U3, U4, U7).

---

## Gamification Strategy

```text
Gamification decision: Not recommended because a feature é de verificação e especificação, com uso ocasional; progresso e conquista não ajudam a medir uma cor nem a especificar um laço.
```

---

## 60/30/10 Visual Strategy

N.A. — sem superfície visual: scripts de linha de comando, texto de skill e documentação.

---

## Surface Assignment

N.A. — nenhuma surface visual proposta.

---

## Interaction Requirements

| Requirement | Why It Matters | Priority |
|-------------|----------------|----------|
| Toda saída dos 2 scripts termina em `RESULTADO:` + `→` | Um estado que não é sucesso nunca termina em silêncio | MUST |
| A 1ª linha do `contraste.sh` e o exit bastam para um script | O gate não precisa interpretar prosa | MUST |
| O roteador não pede "continue" | Parar no meio deixa o item pela metade | MUST |
| Gamificação dispensada | Ver a seção própria | WONT |

---

## Required States

| State | Required UX |
|-------|-------------|
| Loading | N.A. nos scripts (instantâneos). Roteador: linha 🔁 (U6) |
| Empty | Slot vazio: aviso do U2. `--conteudo` sem entrada: 64, com `→ passe o texto pela entrada padrão; arquivo vazio não precisa de varredura` |
| Error | U3 e U4 |
| Success | `RESULTADO: PASSA` ou `LIMPO`, com o `→` do próximo passo |
| Partial Data | Slot vazio é o caso parcial do scan (U2). `Tipo` ausente: a triagem é registrada no relatório |
| Permission Denied | N.A. |
| Disabled | Skill ausente: U6 |

---

## Content and Copy Guidance

| Surface | Guidance |
|---------|----------|
| Primary CTA | N.A.; o `→` começa por verbo |
| Helper Text | `--help` com 1 exemplo por uso e a frase do truncamento |
| Error Copy | Causa + conserto, com o comando; "wrapper" na 1ª vez: "uma função própria que chama a IA" |
| Confirmation | O que foi medido e o que fazer com o número |
| Empty State | Dizer o que não foi visto, nunca só "limpo" |

Saídas em português, frases curtas, como os outros scripts de `sdd/bin/`. Na skill, nunca o nome de uma ferramenta de um agente só (regra 10).

---

## Accessibility and Responsiveness

N.A. — sem superfície visual: a tabela WCAG que esta feature entrega não se aplica a ela mesma. Em CLI:

- Sem cor; todo símbolo com palavra.
- Linhas de status com até 100 caracteres, exceto caminho de arquivo, que fica inteiro numa linha para colar.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|-------|--------|-----------|
| Alcance (Fitts) | N.A. | Sem alvo de clique |
| Escolhas por passo (Hick-Hyman) | OK | A skill nova recomenda o perfil pelo estrago do erro; o aluno não escolhe entre seções |
| Retomada (Zeigarnik) | RECOMENDAÇÃO | O contrato já está no DESIGN; a skill recomeça dele sem perguntar de novo `(lente L3)` |
| Convenção (Jakob) | OK | Saídas 0/2/64 e `RESULTADO:` + `→`, como os outros scripts |
| Progresso real (Gradiente de meta) | RECOMENDAÇÃO | A linha 🔁 diz quantos prompts restam, medidos da tabela de estágios `(lente L5)` |
| Destaque único (Von Restorff) | ALERTA | O aviso do slot vazio aparece em toda varredura; se o Build varre 20 arquivos, são 20 avisos. Um por execução do Build basta no que o agente repassa ao aluno |
| Agrupamento (Miller) | N.A. | Tabela WCAG já agrupada por critério, 7 linhas fixas |
| Sinal de validação real | — | Quantos DRIFT viraram inventário e quantos foram falso positivo; fica para a F15, não como critério |

---

## Design Handoff

Concrete requirements for `/design`:

- **`contraste.sh` (U1, U3, U7):** 1ª linha, `RESULTADO:`, `→`; `--help` com a frase do truncamento; saída 64 com causa e conserto, e o caso `rgba(...)` citando o 3º valor.
- **`prompt-drift-scan.sh` (U2, U3):** linha por achado, aviso do slot vazio em `⚠️`, `→` nos 2 resultados; a skill diz para repassar o aviso uma vez por Build (alerta L6).
- **`design-lint.py` (U4):** frase da v2.5.0 antes dos itens, um item por linha, `→` para o fragmento.
- **`sdd-loop-builder` (U5, U10):** `references/como-falar.md` com o glossário e a frase da saída sem laço.
- **`sdd-build` (U6):** linha 🔁, seguir no mesmo turno, 🛑 + pergunta `[D2 · muda o produto]` para skill ausente.
- **Tabela WCAG (U8):** evidência por linha e temas medidos.
- **Docs (U7, U9):** `docs/llm-in-code.md` + PT e `docs/cli-conventions.md`.
- Gamificação dispensada.
- (lente L3) A skill recomeça do contrato no DESIGN.
- (lente L5) A linha 🔁 traz a contagem real.
- Como medir depois: quantos DRIFT viraram inventário e quantos foram falso positivo, na F15.

Components likely needed:

- `contraste.sh` e `prompt-drift-scan.sh` com as mensagens acima.
- Fragmento `LLM_PROMPTS_DESIGN.md`.
- `references/como-falar.md` da skill nova.

Acceptance notes:

- [ ] O DEFINE sobe para v1.1 com U1 no AT-001, U2 no AT-012, U3 no AT-005 e AT-013, U4 no AT-016 e U6 no AT-019 e AT-020.
- [ ] Toda saída nova termina em `RESULTADO:` + `→`, conferida por teste.
- [ ] Sem cor e com símbolo sempre acompanhado de palavra.
- [ ] Gamificação dispensada, com o motivo registrado.
- [ ] **Premium**: em CLI, todo erro tem causa e conserto.
- [ ] **Self-Evident**: os 3 "isso é bug?" do resumo têm texto próprio.

---

## Open UX Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-04 | ux-review-command | Initial UX review |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F13_UX_LLM.md`
