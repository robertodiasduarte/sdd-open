# Continuar: INCORPORAR_STARTER — sessão 14: F15 Substituição do SDD privado, fase 1 (instalar o Open no privado)

A `v2.7.1` do Open saiu em 2026-11-08 (https://github.com/robertodiasduarte/sdd-open/releases/tag/v2.7.1, `main` = `3d69536`). Esta sessão começa a **F15**: o repositório privado (`/Users/robertoduarte/RDD/Wordpress`, remoto `robertodiasduarte/wordpressrdd`) passa a usar o Open instalado pelo `init`. É a primeira sessão que **altera o privado**.

## Onde abrir esta sessão (2 passos)

A sessão fica presa à pasta em que abriu: nenhum `cd` muda isso.

1. **Abrir a pasta de trabalho da F15** (decisão do Roberto no brainstorm: pelo `/new-session` do próprio privado, com o OK dele). Se ainda não existe `/Users/robertoduarte/rdd-worktrees/f15-substituicao`:
   - confira com `git -C /Users/robertoduarte/RDD/Wordpress worktree list | grep f15-substituicao` (vazio = não existe);
   - peça ao Roberto o OK para criá-la; com o OK, numa sessão aberta em `/Users/robertoduarte/RDD/Wordpress`, rode `/new-session f15-substituicao` (branch `feat/f15-substituicao` a partir do `origin/main` atualizado);
   - pare aqui e peça ao Roberto para abrir o agente na pasta nova e colar este mesmo prompt.
2. **Já dentro dela**, confira:

```bash
git rev-parse --show-toplevel        # esperado: /Users/robertoduarte/rdd-worktrees/f15-substituicao
git branch --show-current            # esperado: feat/f15-substituicao
GIT_TERMINAL_PROMPT=0 git fetch -q origin && git log --oneline -1 origin/main
git status --short | head -5         # esperado: vazio
```

Leia, nesta ordem (os documentos da família estão no Open, branch pública `docs/incorporar-starter`):

```bash
O=/Users/robertoduarte/rdd-public/sdd-open
GIT_TERMINAL_PROMPT=0 git -C "$O" fetch -q origin docs/incorporar-starter
git -C "$O" show origin/docs/incorporar-starter:sdd/features/BRAINSTORM_F15_SUBSTITUICAO.md
git -C "$O" show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md   # quadro "F15", seção 8
git -C "$O" show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  # Ficha, Eventos, etapa do topo
```

## Onde paramos

- **Open:** `v2.7.1` publicada, hash conferido (`5aa600aea17a9481d4ac215af574e9c2563adeaf6d6f58e99c6a7c58569930e3`). 19 skills, 1.663 testes. CI: Ubuntu 18m21s (teto 25), macOS 38m35s (teto 45).
- **F15:** brainstorm feito com o Roberto em 2026-11-07, todas as recomendadas. Abordagem **A, por fases, release por último**: fase 1 instalar · fase 2 a feature da prova (brainstorm a build) pelo Open · fase 3 publicar a mesma feature pelo `sdd-release` do Open · fase 4 remover o SDD privado quando nenhuma frente antiga depender dele. 4 a 5 sessões até a fase 3.
- **Privado** medido em `origin/main` = `022c14aa7` (2026-11-07; refaça): 29 frentes de feature abertas em worktrees; `.claude/commands/workflow` 8 arquivos; `.claude/agents` 12 papéis + 1 modelo; `sdd-public` 80; `scripts/` 244 itens (em `scripts/gates/`, os do método misturados com dezenas de gates de feature); `.claude/kb/` 50 pastas; `.githooks/` com `pre-commit`, `pre-push` e 3 ganchos do Claude; `/release` em `.claude/commands/release.md`; os documentos SDD em `.claude/sdd/`. O checkout principal está 2.286 commits atrás, com 4 arquivos modificados (D7): `.claude/kb/_index.yaml`, `.claude/kb/anatomia-harness-claude-code/concepts/agents-md-portabilidade.md`, `.claude/kb/anatomia-harness-claude-code/index.md`, `wp-content/plugins/rdd-plataforma/templates/partials/anatomia/n2.php`.
- **Gabarito da release** (o que o `sdd-release` instalado precisa reproduzir): `.claude/sdd/releases/EXEMPLO_BAIXAR_NFSE_PAGINA/s1_1.486.0.yaml` no privado.

## Decisões já tomadas, não reabrir (`BRAINSTORM_F15_SUBSTITUICAO.md`, Key Decisions)

1. Convivência até o fim, sem data-limite: o SDD privado só sai quando nenhuma frente aberta depender dele; frente nova nasce no Open; o `/release` antigo fica como saída de emergência.
2. Prova com uma feature **nova, pequena, de 2 camadas**, escolhida no começo da fase 2.
3. Documentos divididos: o brainstorm na branch `docs/` do Open (pública); define, design, relatório e evidências da execução **no privado**, em `sdd/`. Detalhe de infraestrutura da RDD nunca vai para o Open.
4. Ponto de extensão do smoke visual: **3 slots genéricos** no `sdd/config.yaml` do Open (antes do OK, antes do push, depois do deploy; saídas 0 ok · 2 reprovou · 10 nada a medir). É uma entrega **no Open**, com release própria, antes da fase 3.
5. Autorização: um OK por publicação no bloco do OK; o Open não ganha pré-autorização.
6. Vermelho herdado de outras frentes: a linha de base do Open (`gate-baseline.sh`); conferir na fase 1 se cobre os gates de feature.
7. D7: ler o diff dos 4 arquivos, guardá-los num patch fora do git, mostrar ao Roberto e, com o OK dele, sincronizar o checkout principal.
8. A ponte `sdd-public/` sai na fase 1 (`sdd-public/`, `scripts/port-to-public.sh`, `scripts/sdd-public-allowlist.tsv`, `scripts/gates/gate-sdd-open-s1.sh`, `scripts/gates/gate-sdd-prompt-builder.sh`).
9. Ganchos numa pasta só durante a convivência: o `sdd/hooks/` do Open chama as guardas do `.githooks/`.
10. As cópias `~/.claude/skills/sdd-*` (e `anthropic-skills:sdd-*` na conta claude.ai) regeneradas a partir do Open na fase 1.
11. Do Anexo C, somem: `model:` por fase, `/fewer-permission-prompts`, a memória do Roberto como slot. Landmines LM-nnn → `sdd/playbook.md` do privado; patterns e invariantes → `sdd/patterns/` e `sdd/invariants.md`.
12. Fica de fora: mover os documentos antigos de `.claude/sdd/`; as KBs que a prova não usar; buckets WARM/COOL e lentes por público, salvo se a prova passar por UX.

## Tarefa: fase 1, instalar

Rode como um fluxo SDD do Open **dentro do privado** (os documentos em `sdd/` do privado). Antes de cada alteração, diga o que vai mudar; mostre o plano do `init` ao Roberto antes de aplicar.

1. **D7:** leia o diff dos 4 arquivos do checkout principal, sem tocar; proponha o destino; com o OK, patch fora do git e sync do checkout.
2. **Instalar:** a partir do Open em `v2.7.1` (`git -C /Users/robertoduarte/rdd-public/sdd-open fetch -q origin && git -C /Users/robertoduarte/rdd-public/sdd-open checkout -q v2.7.1`, ou o `.tar.gz` da Release conferido pelo `SHA256SUMS.txt`), rode primeiro `bash <open>/bin/sdd-open.sh init --vendors claude --dry-run` e mostre o plano: o privado **já tem `CLAUDE.md`** e `core.hooksPath = .githooks`; nada deles pode ser sobrescrito sem OK. Depois, o `init` de verdade.
3. **`sdd/config.yaml`:** `project.test_cmd` (deno), `deploy.cmd` e `deploy.workflow` (rsync Hostinger pelo GitHub Actions), `deploy.drift_check_cmd` (`scripts/audit-supabase-drift.sh`), `release.landmines_cmd` (`scripts/release-landmines.sh`, com o gate de schema por migration, hoje `scripts/gates/audita-schema-gate.sh`), `layers` (edge/sql/wp-content), `review.*`. Cada valor tirado do `/release` de hoje (`.claude/commands/release.md`), não inventado.
4. **Ganchos** numa pasta só (decisão 9), com teste dos 2 lados: um commit que a guarda antiga recusa continua recusado.
5. **Ponte `sdd-public/` fora** (decisão 8) e **cópias `~/.claude/skills/sdd-*` regeneradas** (decisão 10): esta última mexe fora do repositório: só com OK.
6. **Conteúdo da RDD** nos lugares do Open (decisão 11).
7. **Linha de base:** conferir se o `gate-baseline.sh` cobre os gates de feature vermelhos herdados (decisão 6); se não cobrir, é ajuste no Open, com release própria.

Pronto quando: no privado, `bash bin/sdd-open.sh doctor` sai ✅ sem ⚠️; um `git commit` passa pelas guardas do Open e do `.githooks/`; `git ls-files sdd-public scripts/port-to-public.sh` vazio; as 29 frentes antigas continuam com o `/workflow:*` e o `/release` funcionando (conferir que nada do que elas usam foi removido).

## O que não quebrar

- **As frentes abertas do privado:** nada que o `/workflow:*`, o `/release` e os scripts do SDD privado usam sai antes da fase 4.
- **Produção:** a fase 1 não publica nada no site; o deploy só na fase 3, com OK.
- **Push:** todo comando remoto com `GIT_TERMINAL_PROMPT=0`; push no `main` do privado só com OK explícito do Roberto; push no `main` do Open só com OK citando "sdd-open"; nunca `--force`.
- **Público × privado:** o `sdd-open` e a branch `docs/incorporar-starter` são públicos; detalhe de infraestrutura e dado da RDD ficam no privado.
- **Específico da RDD não viaja para o Open:** mudança no Open (os 3 slots da decisão 4, ajuste da linha de base) é genérica, com teste dos 2 lados, numa worktree do Open, com release própria.
- **Saldo da OpenRouter:** US$ 7,89 em 2026-11-07; `limit_remaining` é o limite da chave, não o saldo (`GET https://openrouter.ai/api/v1/credits`).
- **Fora de escopo nesta sessão:** fases 2 a 4; F16 a F20.

## Fechar

Ao terminar, rode a `sdd-handoff`. A ficha da execução da F15 fica no privado (`sdd/handoffs/HANDOFF_F15_SUBSTITUICAO.md`); o handoff da família (`HANDOFF_INCORPORAR_STARTER.md`, branch `docs/incorporar-starter` do Open) ganha uma linha em Eventos e o campo "Falta" atualizado, gravados pelo molde abaixo, sem trocar de branch em nenhuma worktree:

```bash
O=/Users/robertoduarte/rdd-public/sdd-open
T=$(mktemp -d) && GIT_TERMINAL_PROMPT=0 git -C "$O" fetch -q origin docs/incorporar-starter
git -C "$O" worktree add -q --detach "$T" origin/docs/incorporar-starter
# edite "$T/sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md" e "$T/sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md"
git -C "$T" add sdd/handoffs && git -C "$T" commit -q -m "docs(incorporar-starter): sessão 14" && GIT_TERMINAL_PROMPT=0 git -C "$T" push -q origin HEAD:docs/incorporar-starter
git -C "$O" worktree remove --force "$T"
```
