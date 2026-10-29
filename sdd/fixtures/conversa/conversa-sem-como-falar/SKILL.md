---
name: conversa-sem-como-falar
description: Fixture do skill-lint --conversa que reprova — a seção manda ler references/como-falar.md, e o arquivo não existe.
license: MIT
metadata:
  version: "1.0.0"
  updated: "2026-10"
---

# Conversa (controle)

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Ler | 1 |
| 2 | Gravar | 2 |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Exemplo: ✅ 1 Ler · ▶️ 2 Gravar`.
2. **O que foi feito** — frases curtas, sem saída de comando.
3. **Agora: etapa N — nome** — 2 a 4 frases.
4. **Sua decisão** — a pergunta em negrito e as opções com o efeito de cada uma.
5. **Próximo passo** — uma linha, até 100 caracteres.

## Entrada

Um arquivo de texto.

## Processo

### 1. Ler

Leia o arquivo.

### 2. Gravar

Grave o resultado.
