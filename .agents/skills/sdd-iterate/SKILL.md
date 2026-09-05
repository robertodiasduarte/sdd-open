---
name: sdd-iterate
description: Atualiza um documento de fase do SDD Open (BRAINSTORM, DEFINE ou DESIGN) quando o requisito ou o desenho muda no meio do caminho — edita in-place com histórico, mantém o Verify Gate coerente e pergunta antes de cascatear para o documento seguinte. Use quando o usuário disser /sdd-iterate, "mudou o requisito", "o design não funciona assim", ou quando o Verify Gate vermelho apontar premissa errada na spec.
compatibility: Requer bash >= 3.2 e git >= 2.20.
license: MIT
metadata:
  author: RDD
  version: "2.0.0"
  fase: "cross"
---

# sdd-iterate — mudança de rumo entre fases

> Abra a resposta com o banner: `🔁 ITERATE (cross-phase)`.

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
   `## Verify Gate` no mesmo passe e rodar `sdd/bin/verify-gate.sh --print <DEFINE>` — tem que
   continuar parseável e sem marcador ativo (exit ≠5). Mudança de escopo sem gate
   correspondente é DEFINE mentindo.
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
