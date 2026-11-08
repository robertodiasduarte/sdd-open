# Continuar: INCORPORAR_STARTER — sessão 15: F15, inventário de saída do SDD privado

A `v2.7.2` do Open saiu em 2026-11-08 (https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.7.2, `main` = `9d8ac24`,
SHA-256 `05042aa6264826eee86cf8ce26ddee0ad980ac69fef2e388ea78394c71e36c8b`). Com ela, a **fase 1 da F15 está concluída** no
repositório privado: Open instalado, `doctor` ✅ sem ⚠️, na branch `feat/f15-substituicao` (ainda fora do `main` de lá).

Antes da fase 2, o Roberto pediu um **inventário de saída**: a prova de que, quando o SDD privado sair (fase 4), nada se perde.
É só leitura e roda **no privado**, porque é lá que estão os arquivos inventariados.

## Onde abrir esta sessão

Na worktree do privado, `/Users/robertoduarte/rdd-worktrees/f15-substituicao` (branch `feat/f15-substituicao`). O prompt
detalhado, com a lista de arquivos, os 4 destinos possíveis e onde gravar o resultado, está no fim da ficha da execução:

```bash
sed -n '/^## Prompt de retomada/,/^## Histórico de slices/p' /Users/robertoduarte/rdd-worktrees/f15-substituicao/sdd/handoffs/HANDOFF_F15_SUBSTITUICAO.md
```

## O que não quebrar

- O inventário não muda código nem remove arquivo.
- Lacuna achada vira trabalho **genérico** no Open (worktree do Open, release própria) ou slot no privado; nada da RDD no Open,
  que é público, inclusive esta branch.
- Levar a fase 1 ao `main` do privado só com OK explícito do Roberto (o push lá dispara o deploy do site).
- O macOS do CI do Open está a ~2,5 min do teto de 45 (`release` da v2.7.2: 42m35s): uma release nova pode estourar — se
  estourar, disparar o workflow de novo na ponta do `main`, nunca repetir run antigo. A margem é assunto da F16.

## Fechar

`sdd-handoff` na ficha do privado e, aqui, linha em Eventos e "Falta" do `HANDOFF_INCORPORAR_STARTER.md` + este prompt,
sem trocar de branch em nenhuma worktree:

```bash
O=/Users/robertoduarte/rdd-public/sdd-open
T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git -C "$O" fetch -q origin docs/incorporar-starter
git -C "$O" worktree add -q --detach "$T" origin/docs/incorporar-starter
# edite "$T/sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md" e "$T/sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md"
git -C "$T" add sdd/handoffs && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 15" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
git -C "$O" worktree remove --force "$T"
```
