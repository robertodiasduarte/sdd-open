# UX REVIEW: F5 Conhecimento do sdd-open

> UX/CX review for `F5_CONHECIMENTO` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F5_CONHECIMENTO |
| **Date** | 2026-10-29 |
| **Author** | ux-review-command (sdd-ux-review 2.2.0) |
| **DEFINE** | [DEFINE_F5_CONHECIMENTO.md](../features/DEFINE_F5_CONHECIMENTO.md) |
| **Status** | Ready for Design |
| **Lentes** | 3 recomendações · 1 alerta. Não mudam o Status |

---

## UX Summary

A interface da F5 é texto, em 4 superfícies:
- (1) a conversa da `sdd-kb` com o aluno;
- (2) a entrevista de público da `sdd-ux-review`;
- (3) a saída do `kb-dominios.py`, que o agente lê e traduz;
- (4) a saída do `gate.sh`, que o mantenedor e o aluno curioso leem no terminal.

O maior risco está na entrevista. Ela pergunta fatos ("quem usa?"), e o formato de decisão da F4 exige uma opção recomendada. Se uma pergunta de fato ganha `(recomendado)`, a skill passa a induzir a resposta. A recomendação mais forte é que as perguntas de fato sejam **abertas**, com exemplos no texto. A pergunta de decisão fica só no fim, para confirmar o que será gravado.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do open (contador, advogado, gestor), em geral sem git nem terminal; o agente é o intermediário de toda saída de script |
| **User Goal** | Ensinar o domínio à IA uma vez só; ter a revisão de UX partindo de um público real |
| **Primary Pain** | Reexplicar o contexto em toda conversa; um nome de domínio errado no DEFINE, que ninguém percebe; uma pergunta de público que ele não sabe responder em vocabulário de UX |
| **Business/CX Goal** | Confiança (a base diz de onde veio cada regra, e o aluno sabe que a revisão é dele) e menos retrabalho entre conversas |
| **Device/Context** | Terminal ou chat do agente, no desktop; uso pontual (montar a base) e recorrente (cada Define consulta a base) |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | "Cansei de explicar o Simples Nacional toda vez" | Frustração; não sabe que existe a `sdd-kb` | A descrição da skill reconhece a queixa ("precisa reexplicar as mesmas coisas") |
| Entry | Pede uma base | Medo de um processo longo | A 1ª resposta traz a identificação, o Status com 5 etapas e uma pergunta só (o perfil) |
| Core Action | Conta o que sabe; a skill separa entender × fazer e escreve | Insegurança sobre o que é "conceito" e "receita" | Glossário na 1ª vez; mostrar o arquivo proposto antes de gravar |
| Feedback | Saber se a base "está certa" | Ilusão de autoridade da IA | O validador roda e é traduzido (quantos arquivos, o que falta); o aviso de revisão do profissional, com os trechos críticos nomeados |
| Recovery | Validador reprova, ou o domínio citado no DEFINE não existe | "Quebrei alguma coisa?" | O `kb-dominios.py` diz qual nome falta, quais existem e o conserto; o agente traduz numa frase |
| Interrupção → Retomada | Para no meio da base | Base pela metade parecendo pronta | O `index.md` fica marcado como `PENDENTE DE REVISÃO`; o `--strict` impede o software de consumir |
| Completion | Base registrada no índice | Alívio | Como usar daqui em diante, em 2–3 linhas; Próximo passo ≤100 caracteres |
| Follow-up | Em cada Define, o "KB Domains" sai de `ls sdd/kb/` | Se não há base, um `nenhum` seco | O agente diz em 1 frase que não há base e que a `sdd-kb` cria uma (estado vazio útil) |

Jornada da entrevista (`sdd-ux-review`, passo 1): DEFINE sem público → 1 pergunta aberta por resposta (público; frequência, familiaridade, risco e dispositivo, só o que muda a UX; estágio; referência ou URL) → resumo em 3 camadas → pergunta de confirmação → gravação em `## User and Context`.

---

## UX/CX Findings

| Priority | Area | Finding | Recommendation |
|----------|------|---------|----------------|
| MUST | Self-Evident | Perguntas de fato (público, estágio, referência) com `(recomendado)` induzem a resposta, e a regra 3 do `PERGUNTA_DECISAO.md` exige exatamente uma recomendada em pergunta de **autorização** | Público, estágio e referência são **perguntas abertas** ("Responda com …, ou 'não sei'"), com exemplos no texto. A única pergunta com opções é a confirmação final ("Posso gravar este público em User and Context?"), com **sim** (recomendado) · **ajustar** · **não sei** |
| MUST | Clareza | O guia do builder oferece "outro" na pergunta de público, e o catálogo tem a linha "Outra referência" | Tirar o "outro" da pergunta, que agora é aberta e aceita qualquer resposta. No catálogo, a linha passa a "Uma referência sua". Nenhuma opção **Outro** escrita |
| MUST | Recuperação | Saída do lint que diz só "nome inválido" deixa o agente sem conserto | `kb-dominios.py` segue `docs/cli-conventions.md`: `🛑 KB Domains: 'x' não existe em sdd/kb/ (existem: a, b)` (até 10 nomes, "e mais N"), `RESULTADO: VERMELHO` e `→ corrija o KB Domains com nomes de 'ls sdd/kb/' ou escreva nenhum, e rode de novo`. Se `sdd/kb/` não existe: `→ rode a sdd-kb para criar a base, ou escreva nenhum` |
| MUST | Confiança | O `gate.sh` do starter fala inglês e com outra moldura (`FAIL:`/`PASS:`) | O `gate.sh` novo segue as convenções: uma linha `✅`/`🛑` por caso só quando falha (o sucesso não lista 15 linhas), `RESULTADO: VERDE` com as contagens ("3 aceitas, 12 rejeitadas") ou `RESULTADO: VERMELHO` com o caso, e `→` o conserto |
| MUST | Premium (CLI) | Erro sem conserto | Toda falha do `kb-dominios.py` e do `gate.sh` tem 2 linhas, a causa e o conserto. Arquivo ilegível: `🛑 <arquivo>: não consegui ler: …` + `→ confira a permissão e a codificação (UTF-8) …`, como o `design-lint` |
| SHOULD | Estado vazio | Projeto sem `sdd/kb/`: o Define grava `nenhum` sem dizer nada | A `sdd-define` diz, no "O que foi feito", que não há base de conhecimento e que a `sdd-kb` cria uma, em 1 frase e sem pergunta |
| SHOULD | Clareza | Os nomes de pasta (`simples-nacional-anexo-iii`) aparecem crus no DEFINE | Ao mostrar o "KB Domains", o agente usa o `name:` do `_index.yaml` ao lado do slug na 1ª vez |
| SHOULD | Confiança | `validate_kb.py` mantém as mensagens em inglês (porte) | O texto da `sdd-kb` manda traduzir (quantos, quais, o que preocupa), e o `docs/cli-conventions.md` registra a exceção: as mensagens são `PASS:`/`FAIL:`/`WARN:` e as saídas, 0/2/64 |
| COULD | Eficiência | Catálogo de 9 referências de uma vez | Mostrar o catálogo como tabela curta dentro da pergunta aberta; se o aluno disser "não sei", perguntar por sensações (sério/amigável, compacto/espaçoso) e sugerir 2 ou 3 para comparar |
| WONT | Clareza | Traduzir as ~60 mensagens do `validate_kb.py` para português | Reabriria um validador de 465 linhas já revisado, e os 62 testes conferem o texto das razões. O agente traduz, que é a regra da camada |
| WONT | Continuidade | Guardar o público num `sdd/ux/PUBLICO.md` do projeto | Decisão 5 do BRAINSTORM; a W5 traz a leitura de reviews anteriores |

---

## North Star Checks (Premium + Self-Evident)

### Premium (padrão de qualidade percebida)

| Dimensão | Status | Evidência / Risco |
|----------|--------|-------------------|
| Hierarquia visual em 200ms | ✅ | Status na 1ª linha, uma etapa por resposta; na CLI, a linha `RESULTADO:` no fim |
| Densidade calibrada (respira) | ⚠️ | O gate com 15 casos pode virar parede de texto → só a falha imprime caso (MUST 4) |
| Tipografia com propósito (≤3 sizes/surface) | N.A. | Texto em terminal/chat |
| Movimento curto (150-250ms ease-out) | N.A. | Sem animação |
| Microinterações completas (hover/focus/active/disabled) | N.A. | Sem controles visuais |
| Surfaces do design system do projeto (quando houver) | N.A. | Sem UI visual |
| Estados vazios como delight, não placeholder | ⚠️ | `sdd/kb/` ausente → SHOULD 1 (frase que aponta a `sdd-kb`) |
| Acabamento "shipada", não "MVP a polir" | ✅ | Mensagens com causa e conserto em todo script novo |

### Self-Evident / Zero-Explanation

| Anti-padrão | Está presente? | Onde / como remover |
|-------------|----------------|---------------------|
| Tooltip-muleta (affordance só funciona com tooltip) | ✅ Não | — |
| Helper text explicando o óbvio | ✅ Não | — |
| Estado ambíguo (foi salvo/enviado/pendente?) | ✅ Não | Base não revisada fica `PENDENTE DE REVISÃO`; a entrega sem arquivo diz "não foram gravados" (passo 8 do starter, mantido) |
| Cor conflitando com semântica (rascunho em verde, etc) | ✅ Não | `✅` só em sucesso real; o gate não imprime `✅` com `RESULTADO: VERMELHO` |
| Onboarding/tour obrigatório | ✅ Não | A entrevista é opcional e só roda sem público no DEFINE |
| Documentação como contrato de UX | ❌ Sim | O "KB Domains" dependia de o agente ler o template → o lint do passo 10 move a regra para uma checagem |

**Teste do estranho:** um aluno que nunca viu a `sdd-kb` chega à base registrada respondendo 1 pergunta por vez. Onde ele hesitaria: na palavra "receita" e em "perfil normativo", que o glossário cobre na 1ª vez. Na entrevista, ele hesitaria numa pergunta de público com opção "recomendada", e o MUST 1 remove isso.

**Teste do suporte:** "Por que meu DEFINE diz `nenhum` se eu tenho anotações?" → o SHOULD 1 responde na própria conversa. "O gate deu vermelho, quebrei?" → o MUST 4 diz qual caso e o conserto. Nenhum estado restante dispara pergunta.

---

## Gamification Strategy

```text
Gamification decision: Not recommended because a base de conhecimento é trabalho de responsabilidade técnica (o profissional responde pelo conteúdo); contador de progresso ou selo incentivaria "terminar" uma base não revisada. O progresso real já está no Status de 5 etapas.
```

---

## 60/30/10 Visual Strategy

N.A.: não há superfície visual. Os papéis equivalentes na CLI são a linha `RESULTADO:` (acento: a próxima ação vem logo depois, no `→`), as linhas `🛑`/`⚠️` (secundárias) e o resto da saída (dominante), como manda o `docs/cli-conventions.md`. Significado nunca só por cor: todo símbolo vem com palavra.

---

## Surface Assignment

| Surface (funcional) | Papel | Justificativa | Nova no design system? |
|---------------------|-------|---------------|------------------------|
| Resposta da `sdd-kb` no chat | operacional | Conversa de trabalho, 5 partes fixas da F4 | Não (reuso da camada) |
| Entrevista no passo 1 da `sdd-ux-review` | operacional | Coleta de fatos, uma pergunta por resposta | Não (reuso do `PERGUNTA_DECISAO.md`) |
| Saída do `kb-dominios.py` | operacional | Lida pelo agente; segue `cli-conventions` | Não |
| Saída do `gate.sh` | operacional | Lida pelo mantenedor; segue `cli-conventions` | Não |

---

## Interaction Requirements

| Requirement | Why It Matters | Priority |
|-------------|----------------|----------|
| Uma pergunta por resposta na `sdd-kb` e na entrevista | Aluno sem vocabulário de UX ou de KB decide melhor uma coisa por vez | MUST |
| Perguntas de fato abertas; só a confirmação final tem opções, com a recomendada primeiro | Não induzir a resposta; o formato da F4 continua valendo onde há decisão | MUST |
| `kb-dominios.py` com causa, nomes existentes e conserto | O agente corrige sem adivinhar | MUST |
| `gate.sh` silencioso no sucesso, com contagens; falha nomeia o caso | Leitura em 1 linha | MUST |
| Base não revisada marcada no `index.md`; aviso de revisão nomeando os trechos críticos | Confiança honesta: a IA organiza, o profissional responde | MUST (já na skill portada) |
| Gamificação | Ver decisão acima | WONT |

---

## Required States

| State | Required UX |
|-------|-------------|
| Loading | Antes do validador ou do gate, o agente diz o que vai rodar e que o aluno não precisa responder (regra da camada) |
| Empty | Sem `sdd/kb/`: a `sdd-kb` cria o índice sem tratar como erro; a `sdd-define` grava `nenhum` e diz em 1 frase que a `sdd-kb` cria uma base |
| Error | `kb-dominios.py`: `🛑` + nomes existentes + `→` conserto. `gate.sh`: `🛑` com o caso + `RESULTADO: VERMELHO` + `→`. Validador: `FAIL:` traduzido pelo agente |
| Success | `✅ … KB Domains válido` (lint); `RESULTADO: VERDE — 3 aceitas, 12 rejeitadas` (gate); base registrada + como usar (skill) |
| Partial Data | Base escrita e não revisada: `PENDENTE DE REVISÃO` no `index.md`; o `--strict` reprova antes de um software consumir |
| Permission Denied | Sem acesso ao sistema de arquivos: a `sdd-kb` entrega os arquivos no chat, diz que não gravou, dá a estrutura e o que fazer (passo 8 do starter, mantido) |
| Disabled | Projeto sem a `sdd-kb` instalada: o `kb-dominios.py` continua funcionando, porque não depende dela |

---

## Content and Copy Guidance

| Surface | Guidance |
|---------|----------|
| Primary CTA | Pergunta de confirmação com verbo e efeito: "**sim** (recomendado) — gravo o público em User and Context e sigo para a jornada" |
| Helper Text | Glossário só na 1ª vez: domínio, conceito, receita, índice, perfil normativo, vigência, fonte, revisão do profissional; na entrevista: estágio, referência, "observado × desejado × recomendado" |
| Error Copy | Causa + conserto: "'simples' não existe em sdd/kb/ (existem: simples-nacional, folha)" / "→ corrija o KB Domains …" |
| Confirmation | "Gravei a base em `sdd/kb/simples-nacional/` e registrei no índice. Revise cada arquivo antes de usar para valer." |
| Empty State | "Este projeto ainda não tem base de conhecimento; o KB Domains ficou como nenhum. A sdd-kb cria uma quando você quiser." |

---

## Accessibility and Responsiveness

| Concern | Requirement |
|---------|-------------|
| Keyboard | N.A. (texto) |
| Contrast (**medir nos pares reais**, no tema padrão primeiro) | N.A.: sem cor própria; o terminal do usuário define o tema |
| Screen Reader | Todo símbolo com palavra (`🛑` + causa, `RESULTADO: VERDE`); nenhuma informação só em emoji; nenhum caractere invisível (integridade do CI) |
| Mobile | Linhas de saída sem depender de largura; a lista de nomes existentes é truncada em 10 + "e mais N" |
| Non-color Cues | Símbolo + palavra em toda linha de estado |

Nota para a W5 (item H): o `UX_REVIEW_TEMPLATE.md` vai ganhar a tabela WCAG 2.2 AA. Esta revisão não fixa critério de contraste nem de alvo que a contradiga.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|-------|--------|-----------|
| Escolhas por passo (Hick-Hyman) | RECOMENDAÇÃO | O catálogo tem 9 referências numa pergunta; o COULD de Eficiência (tabela curta e, no "não sei", 2 ou 3 para comparar) |
| Retomada (Zeigarnik) | OK | A base interrompida fica `PENDENTE DE REVISÃO` no `index.md`, e a volta parte do índice e do Status |
| Progresso real (Gradiente de meta) | OK | Status de 5 etapas vindo do estado real (✅ concluída, não visitada) |
| Destaque único (Von Restorff) | RECOMENDAÇÃO | No gate, só a falha ganha linha própria; no sucesso, uma linha `RESULTADO:` (MUST 4 já cobre a regra; a lente reforça) |
| Convenção (Jakob) | ALERTA | Aplicar ao pé da letra a convenção do starter (`FAIL:`/`PASS:` em inglês) no `gate.sh` quebraria a convenção do open (`cli-conventions`); a convenção que vale é a do pacote onde o script mora |
| Sinal de validação real | RECOMENDAÇÃO | Depois da entrega, contar quantos DEFINE novos saem com `nenhum` × domínio real, e quantas vezes o `kb-dominios.py` reprova no 1º run (alvo: cair com o uso) |
| Alcance (Fitts), Agrupamento (Miller) | N.A. | Sem alvo de clique nem formulário |

---

## Design Handoff

Concrete requirements for `/design`:

- **Entrevista** (`references/entrevista-publico.md`):
  - público, estágio e referência são **perguntas abertas**, com exemplos no texto e a saída "não sei";
  - a única pergunta com opções é a confirmação final, em `PERGUNTA_DECISAO.md`, com **sim** (recomendado), **ajustar** e **não sei**;
  - sem "outro";
  - a linha do catálogo passa a "Uma referência sua".
- **`kb-dominios.py`** segue `docs/cli-conventions.md`:
  - `🛑` por problema, com os nomes que existem (até 10, depois "e mais N");
  - `RESULTADO: VERDE|VERMELHO` e `→` com o conserto;
  - quando `sdd/kb/` não existe, o conserto aponta a `sdd-kb` ou `nenhum`;
  - no sucesso: `✅ <arquivo>: KB Domains válido`, mais as linhas `<domínio>: <REGRA> → <teste>`.
- **`gate.sh`** segue `cli-conventions`:
  - é silencioso no sucesso, com `RESULTADO: VERDE — 3 aceitas, 12 rejeitadas`;
  - na falha, imprime `🛑 <caso>: …`, `RESULTADO: VERMELHO` e `→`;
  - não tem nenhuma mensagem em inglês.
- **`validate_kb.py`** mantém as mensagens do starter (WONT traduzir). A `sdd-kb` manda traduzir a saída, e o `docs/cli-conventions.md` registra a exceção (`PASS:`/`FAIL:`/`WARN:`, 0/2/64).
- **`sdd-define`**:
  - sem `sdd/kb/`, grava `nenhum` e diz numa frase que a `sdd-kb` cria uma base;
  - ao mostrar um domínio pela 1ª vez, põe o `name:` do `_index.yaml` ao lado do nome da pasta.
- **Gamificação**: não incluir (ver a decisão).
- (lente L2) O catálogo vai como tabela curta. No "não sei", sugerir 2 ou 3 referências para comparar.
- (lente L6) No gate, só a falha ganha linha própria.
- **Como medir depois**: a proporção de DEFINE com `nenhum` × domínio real, e as reprovações do `kb-dominios.py` no 1º run.

Components likely needed:

- `references/entrevista-publico.md` (sdd-ux-review)
- moldura de saída comum do `kb-dominios.py` e do `gate.sh`
- `references/como-falar.md` da `sdd-kb`, no formato da F4

Acceptance notes:

- [ ] Nenhuma pergunta de fato com `(recomendado)` na entrevista; a confirmação final passa no checador de perguntas do `skill-lint --conversa`
- [ ] Toda falha de `kb-dominios.py` e `gate.sh` tem causa e conserto, e termina em `RESULTADO:`
- [ ] 60/30/10: N.A. (texto); símbolo sempre com palavra
- [ ] Gamificação dispensada com motivo
- [ ] **Premium**: os estados vazio, erro, sucesso e parcial têm frase pronta (ver Required States)
- [ ] **Self-Evident**: o "KB Domains" é conferido por lint, não por leitura do template; teste do estranho e do suporte aprovados

---

## Open UX Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-10-29 | ux-review-command | Initial UX review |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F5_CONHECIMENTO.md`
