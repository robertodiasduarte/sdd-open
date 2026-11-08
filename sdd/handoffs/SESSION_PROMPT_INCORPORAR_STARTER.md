# Continuar: INCORPORAR_STARTER — sessão 15: v2.7.2 do Open (pré-requisito do merge da F15 fase 1)

Na sessão 14 (2026-11-08) a fase 1 da F15 foi instalada no repositório privado com o Open `v2.7.1`, na worktree
`/Users/robertoduarte/rdd-worktrees/f15-substituicao` (branch `feat/f15-substituicao`, commits `00ad127ce`, `50dc01e33`,
`fa38d1d98`, **fora do `main`**). A instalação achou 2 defeitos **genéricos** do Open; sem corrigi-los, a fase 1 não vai
ao `main` do privado e o `doctor` não sai ✅ sem ⚠️. Esta sessão os corrige no Open, com release própria (`v2.7.2`), e
reinstala no privado.

## Onde abrir esta sessão

Numa worktree nova do Open (a sessão fica presa à pasta onde nasce; nenhum `cd` muda isso):

```bash
O=/Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git -C "$O" fetch -q origin
git -C "$O" worktree add -b fix/guardas-pasta-e-gancho-encadeado /Users/robertoduarte/rdd-worktrees/sdd-open-v272 origin/main
```

Abra o agente em `/Users/robertoduarte/rdd-worktrees/sdd-open-v272`. Os passos 4 e 5 abaixo mexem no privado e precisam
de uma sessão aberta em `/Users/robertoduarte/rdd-worktrees/f15-substituicao`.

Leia, nesta ordem:

```bash
cat /Users/robertoduarte/rdd-worktrees/f15-substituicao/sdd/handoffs/HANDOFF_F15_SUBSTITUICAO.md   # Falta, Landmines, Eventos
O=/Users/robertoduarte/rdd-public/sdd-open
git -C "$O" show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md | sed -n 1,20p
```

## Os 2 defeitos (medidos em 2026-11-08 sobre a v2.7.1)

1. **Guardas de BUILD_REPORT casam pelo nome em qualquer pasta.** `bin/adapters/claude/sdd-report-guard.py`
   (`REPORT_RE` sobre o `basename`) e a regra `[REPORT]` de `sdd/hooks/pre-commit` (`case "$(basename "$f")"`) julgam
   qualquer `BUILD_REPORT_*.md`. Num projeto que tem outro fluxo com relatórios em outra pasta, o `report-lint` do Open
   reprova os relatórios de lá (medido: VERMELHO) e o guarda nega a gravação. Correção: agir só em `sdd/reports/` da
   raiz do projeto (o contrato do `report-lint.py` já é `sdd/reports/BUILD_REPORT_{FEATURE}.md`).
2. **O `doctor` avisa ⚠️ mesmo com o gancho encadeado.** Com `core.hooksPath` de outro gerenciador, o `doctor` manda
   acrescentar `bash sdd/hooks/pre-commit || exit 1` (`LINHA_ACRESCENTAR`) ao pre-commit de lá, e continua avisando
   depois de a linha estar lá (`hooks_estado` só reconhece `core.hooksPath` = `sdd/hooks`). Correção: pre-commit do
   `core.hooksPath` que contém a linha ⇒ ✅ "hooks encadeados"; sem a linha, o ⚠️ de hoje.

## Tarefa

1. Fluxo do Open para as 2 correções (DEFINE/DESIGN curtos aqui na `docs/incorporar-starter`, como F1–F14).
2. Teste dos 2 lados em `tests/`, **com caso-controle**: o mesmo relatório inválido negado em `sdd/reports/` e ignorado
   fora; `doctor` com a linha (✅) e sem ela (⚠️). Sabotar cada correção e ver o teste cair (na sessão 14, um caso
   "ignora o outro lado" sem controle passou com a correção removida).
3. `bash scripts/publish-gate.sh .` verde, revisão de contexto fresco, PR; push no `main` do Open **só com OK do
   Roberto citando "sdd-open"**; a Release `v2.7.2` sai sozinha; conferir o hash pelo `SHA256SUMS.txt`.
4. No privado (`/Users/robertoduarte/rdd-worktrees/f15-substituicao`): baixar o pacote `v2.7.2`,
   `bash <pacote>/bin/sdd-open.sh sync --vendors claude` (regera `.claude/hooks/sdd-report-guard.py`), copiar à mão
   `sdd/hooks/pre-commit` do pacote (o `sync` não reescreve arquivo do projeto), `bash <pacote>/bin/sdd-open.sh doctor`
   ⇒ ✅ sem ⚠️, `bash scripts/gates/test-build-report-guard.sh` ⇒ 86/86; commitar.
5. Perguntar ao Roberto se leva a fase 1 ao `main` do privado (rebase em `origin/main`; o push dispara o deploy do
   site, sem mudança no ar).

## O que não quebrar

- Específico da RDD não viaja para o Open (público): as correções são genéricas, com fixture própria.
- No privado: não trocar `core.hooksPath` (comum a todas as worktrees); não mover playbook, invariantes nem patterns
  (fonte única em `.claude/` até a fase 4).
- Todo comando remoto com `GIT_TERMINAL_PROMPT=0`; nunca `--force`.
- Fora de escopo: fase 2 (feature da prova), os 3 slots de smoke visual (decisão 4 da F15, release própria antes da
  fase 3), F16–F20.

## Fechar

`sdd-handoff` na ficha do privado (`sdd/handoffs/HANDOFF_F15_SUBSTITUICAO.md`) e, aqui, linha em Eventos e "Falta" do
`HANDOFF_INCORPORAR_STARTER.md` + este prompt para a sessão 16, sem trocar de branch em nenhuma worktree:

```bash
O=/Users/robertoduarte/rdd-public/sdd-open
T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git -C "$O" fetch -q origin docs/incorporar-starter
git -C "$O" worktree add -q --detach "$T" origin/docs/incorporar-starter
# edite "$T/sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md" e "$T/sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md"
git -C "$T" add sdd/handoffs && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 15" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
git -C "$O" worktree remove --force "$T"
```
