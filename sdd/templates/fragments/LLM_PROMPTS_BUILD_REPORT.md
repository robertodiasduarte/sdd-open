# Fragmento — Seção "LLM Prompts" do BUILD_REPORT

> Reusável. A fase Build cola esta seção no BUILD_REPORT quando o DEFINE tem `LLM Prompts: true`
> (o DESIGN, então, tem o inventário de prompts). Com `false`, a seção não existe — e o drift do
> passo 4 da `sdd-build` continua armado: prompt de produção que aparecer fora do inventário para o
> build e vira pergunta.

## Por que existe

O prompt de produção é código que ninguém compila. Sem registro do que foi gerado, de qual versão
substituiu qual e de como voltar atrás, a próxima mudança no prompt é feita no escuro e o
"funcionava ontem" não tem para onde voltar.

## Inventário executado

Uma linha por item do inventário "LLM Prompts" do DESIGN. Item do DESIGN sem linha aqui é item
não construído.

| # | Prompt (do inventário) | Arquivo | Tipo (one-shot · loop) | Gerado por | Status |
|---|---|---|---|---|---|
| 1 | <nome do DESIGN> | `<caminho>` | one-shot | `sdd-prompt-builder` (ou a skill de `prompts.builder_skill`) | criado · refatorado · bloqueado (motivo) |

N.A. quando: nunca, com `LLM Prompts: true` — o inventário do DESIGN tem pelo menos um item.

## Detalhe por prompt

Um bloco por linha do inventário:

- **Contrato do DESIGN cumprido:** tom, formato de saída, fallback, referências — o que foi
  aplicado e onde.
- **Evidência:** `evidence/{FEATURE}/PROMPT-nn.log` com a chamada real e a saída (1ª linha
  `$ comando`), ou o `AVALIACAO_{FEATURE}_*.md` do avaliador que a fez.
- **Modelo e parâmetros:** os do DESIGN; nenhuma decisão de provedor reaberta no build.

N.A. quando: o item ficou bloqueado — diga por quê na tabela acima.

## Drift

Prompts de produção encontrados no código e **fora** do inventário (o passo 4 da `sdd-build`
para o build e pergunta):

| Arquivo | Sinal | Decisão (iterar o DESIGN · falso positivo, com motivo) |
|---|---|---|
| `<caminho>` | `<o que o identificou>` | <decisão> |

N.A. quando: nenhum sinal encontrado — escreva "nenhum".

## Versionamento

| Prompt | Versão anterior | Versão nova | Onde a anterior fica |
|---|---|---|---|
| <nome> | <hash, tag ou "nova"> | <hash ou tag> | `<caminho ou commit>` |

N.A. quando: todos os prompts são novos — a coluna "Versão anterior" diz "nova".

## Rollback

Como voltar ao prompt anterior se a versão nova piorar em produção: o comando ou o passo, quem
pode fazer e em quanto tempo o efeito aparece.

N.A. quando: todos os prompts são novos e a feature pode ser desligada sem eles — diga como.
