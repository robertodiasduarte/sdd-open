---
name: sdd-iterate
description: Atualiza um documento de fase do SDD Open (BRAINSTORM, DEFINE ou DESIGN) quando o requisito ou o desenho muda no meio do caminho — edita in-place com histórico, mantém o Verify Gate coerente e pergunta antes de cascatear para o documento seguinte. Use quando o usuário disser /sdd-iterate, "mudou o requisito", "o design não funciona assim", ou quando o Verify Gate vermelho apontar premissa errada na spec.
compatibility: Requer bash >= 3.2 e git >= 2.20.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.1.0"
  updated: "2026-10"
  fase: "cross"
---

# sdd-iterate — mudança de rumo entre fases

Na primeira resposta desta skill, comece com esta linha, uma vez só:
`sdd-iterate v2.1.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Ler | 1 |
| 2 | Classificar | 2 |
| 3 | Aplicar | 3 e 4 |
| 4 | Cascata | 5 |
| 5 | Fechar | 6 e 7 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Iterate: ✅ 1 Ler · ✅ 2 Classificar · ▶️ 3 Aplicar · ⬜ 4 Cascata · ⬜ 5 Fechar`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Entrada

`/sdd-iterate <doc-de-fase> "<o que muda e por quê>"`

```
/sdd-iterate sdd/features/DEFINE_X.md "aceitar .csv além de .xlsx na importação"
/sdd-iterate sdd/features/DESIGN_X.md "a API não pode ler o bucket; passar o texto no payload"
```

## Quando iterar × quando abrir um Define novo

| Situação | Ação |
|---|---|
| <30% do doc muda · adiciona/ajusta requisito · muda restrição | `/sdd-iterate` |
| Verify Gate vermelho (exit 2) apontou premissa errada no DEFINE/DESIGN | `/sdd-iterate` — é o caminho oficial |
| >50% diferente · problema diferente · usuário-alvo diferente | novo `/sdd-define` |
| Mudar **código** no meio do build por causa de premissa | ⛔ não: iterar o DESIGN primeiro, depois o build — rastreabilidade |

## Processo

1. **Ler** `AGENTS.md`, o doc alvo e o irmão a jusante (DEFINE → DESIGN; DESIGN →
   BUILD_REPORT se existir). Identificar a fase pelo prefixo do arquivo.
2. **Classificar a mudança:** aditiva (baixo impacto) · modificadora (médio) · remoção
   (médio) · arquitetural (alto — pode exigir DESIGN novo em vez de patch).
3. **Aplicar no doc alvo** — in-place, **nunca** criar `_v2`. Registrar em `## Revision History`
   (versão · data · "iterate" · o que mudou e por quê, 1 linha).
4. **Verify Gate (só DEFINE):** se a mudança toca critério de aceite, atualizar o bloco
   `## Verify Gate` no mesmo passe e rodar as duas chamadas, nesta ordem:
   - `sdd/bin/verify-gate.sh --print <DEFINE>` — mostra o bloco que o gate leu (exit 0) ou acusa
     bloco ausente (64). Não valida `kind` nem `cmd` e é isento de marcador: sozinho, nunca vê
     dúvida aberta.
   - `sdd/bin/verify-gate.sh <DEFINE>` — exit 5 = marcador ativo de ambiguidade: parar e voltar
     ao Define. 64 = bloco inválido (`kind` ou `cmd`): corrigir o `## Verify Gate` neste passe.
     Sem marcador, o gate **roda o `cmd`**: 0, 2 e 3 dizem do código, que pode nem existir
     ainda, e 4 é gate manual-ux — nenhum deles é deste passo, e a seta `→` do vermelho não vale
     aqui (o iterate não mexe em código).
     ⚠️ Com `kind` `smoke` ou `eval`, ou `cmd` que grava, envia ou cobra, não rode esta chamada:
     procure o marcador fora de bloco de código, na forma canônica de
     `sdd/templates/fragments/CLARIFY.md` — achou, pare e volte ao Define.

   Mudança de escopo sem gate correspondente é DEFINE mentindo.
5. **Cascata:** DEFINE alterado → o DESIGN ainda vale? DESIGN alterado → há código construído
   que fica órfão? Se sim, **perguntar**: (a) atualizo o doc a jusante agora · (b) só este,
   você cuida do resto · (c) mostro o diff antes. Nunca cascatear em silêncio.
6. **Playbook:** `sdd/bin/playbook-lint.sh --grep <superfície tocada> sdd/playbook.md` —
   landmine que casa entra como nota no doc, não como suposição.
7. **Fechar** com o resumo de etapa: o que mudou, o que cascateou, próximo comando.

## Saída

| Artefato | Onde |
|---|---|
| Doc alterado (mesmo arquivo, história dentro dele) | mesmo path da entrada |
| Doc a jusante (se cascateou com OK) | `sdd/features/` ou `sdd/reports/` |

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é a fase
do documento alterado.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
