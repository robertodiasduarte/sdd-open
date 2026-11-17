# HANDOFF: F24 Release enxuta

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F24_RELEASE_ENXUTA |
| **Objetivo** | A parte da `sdd-release` depois do push fica curta: só colhe e enfileira a curadoria, um commit de papel coberto pelo OK, uma parada só (smoke vermelho), ficha por acréscimo, trilha curta por comando e cada etapa explicada ao aluno em uma frase. |
| **Status** | ✅ DoD fechado — publicado na `v2.20.0` (`main` = `017f09a`, PR #36), 2026-11-17; Release conferida (`shasum -c` OK, prefixo `5a8edb1eb45e`, `VERSION` = `v2.20.0`); starter **`v1.5.25`** (9ª geração, PR #18 de lá, 18 zips OK no `shasum -c`) |
| **Última sessão** | 2026-11-17 |
| **Branch / pasta** | `feat/f24-release-enxuta` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f24-release-enxuta` (nascida de `origin/main` em `ef217b9`, rebaseada sobre `fb7ee82`) |
| **Artefatos** | `sdd/archive/F24_RELEASE_ENXUTA/{DEFINE,DESIGN,BUILD_REPORT}_F24_RELEASE_ENXUTA.md` · `sdd/reviews/LEDGER_REVISAO_F24_RELEASE_ENXUTA.md` · `sdd/reports/CUSTO_F24_RELEASE_ENXUTA.md` · `sdd/reports/evidence/F24_RELEASE_ENXUTA/` · `sdd/reports/reviews-medicao/F24_RELEASE_ENXUTA/` · `sdd/curadoria/fila/F24_RELEASE_ENXUTA/20261117T095520Z/` — todos na branch de documentos `docs/incorporar-starter` |
| **Verify Gate** | 🟢 0 em `017f09a` (2.435 testes, 3 pulados) — `bash sdd/bin/verify-gate.sh sdd/archive/F24_RELEASE_ENXUTA/DEFINE_F24_RELEASE_ENXUTA.md`; CI do PR #36 18 de 18 |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F24_RELEASE_ENXUTA` a partir de `sdd/releases/F24_RELEASE_ENXUTA/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-17 · s1 · 2.20.0 · shipado · CONCERNS · deploy real · trilha completa · f910b0c
<!-- publicado:fim -->

## Feito

- Tudo do escopo (itens 1 a 6 do pedido) está na `v2.20.0`; a descrição e a prova estão no ledger da publicação.

## Falta

1. ~~Regerar o starter~~ — feito: 9ª geração pela tag `v2.20.0` num clone limpo (`9782444`, 7 arquivos: `sdd-handoff` 2.3.0 com o bloco Publicado e o molde, `sdd-release` 2.16.0 só na versão); `check-gerado` VERDE, `publish-check` e `check-versions` PASS, 17 + 62 testes; PR #18 de lá, CI verde, avanço direto da `main` (`df6ae1c..9782444`, OK do Roberto: "sim, pode regerar o starter"); Release **`v1.5.25`**, 18 zips OK.
2. **Definir o 1º lote da curadoria no Open:** aqui a fila fica na branch de documentos e o playbook na `main`; o lote precisa dos dois. A entrada `20261117T095520Z` (17 contagens, nenhuma regra nova) espera por ele. Colhida com o playbook da `main` (`fb7ee82`).
3. Remover a worktree e a branch local da frente (comandos em Ship).

## Definition of Done

- [x] AT-001 a AT-011 com log por AT em `017f09a`, todos exit 0
- [x] Verify Gate verde em `017f09a`
- [x] Release `v2.20.0` conferida

## ⛔ Landmines desta feature

- LM-035 mordeu: texto de skill que cita `sdd/bin/` quebra o gerador do starter; trocas em `scripts/starter/trocas/`.
- Dois gates gravando no mesmo log misturam as saídas: um log por SHA (`VERIFY-GATE-<sha>.log`).

## Casos e testes em aberto

- ✨ Teste de ponta a ponta do lote com um bloco de curador gravado (R2@claude da rodada 5).
- ✨ Leitor de YAML estrito no `ficha-publicado.py` (R4@codex da rodada 4a; hoje lê linhas `chave: valor`).

## Eventos

- 2026-11-16 — escopo de 6 itens numa fatia só; padrão novo para todos, lote sob demanda, limite da fila 5 (decisões do Roberto).
- 2026-11-16 — a F23B3 chegou à `main` no meio da 2ª rodada: rebase, `sdd-release` 2.16.0.
- 2026-11-16 — 4ª rodada acima do teto (OK do Roberto); 2026-11-17 — 5ª rodada corrigida sem 6ª (decisão do Roberto).

## Recomendações

- Antes do 1º lote no Open, decidir onde ele roda (worktree da `main` com a fila trazida da branch de documentos é o caminho mais curto).

## Veredito

- 🟡 CONCERNS — as 3 pendências do ledger da publicação (teste de ponta a ponta do lote, 1º lote no Open, leitor de YAML).

## Setup

1. `cd /Users/robertoduarte/rdd-public/sdd-open && git fetch origin` — a `main` em `017f09a` ou depois.

## Tarefas

1. **Definir e rodar o 1º lote da curadoria no Open** — Pronto quando: a entrada `20261117T095520Z` sai da fila com `--registrar` e as contagens estão no playbook da `main`.

## Ship

- **Publicar:** feito (`v2.20.0`).
- **Limpar:** `git worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f24-release-enxuta` e `git branch -D feat/f24-release-enxuta` (a branch remota já foi apagada, conferida por `git cherry`).

---

## Prompt de retomada

```text
Retomar a feature F24_RELEASE_ENXUTA (publicada na v2.20.0; DoD fechado).

Contexto: a sdd-release ficou curta depois do push (colheita enfileirada, commit de papel, uma parada só, ficha por
acréscimo, trilha curta). Starter v1.5.25 publicado. Falta definir o 1º lote da curadoria no Open.
Pasta: /Users/robertoduarte/rdd-public/sdd-open (main) · documentos em /Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16 (docs/incorporar-starter).
Leia primeiro: sdd/handoffs/HANDOFF_F24_RELEASE_ENXUTA.md e sdd/releases/F24_RELEASE_ENXUTA/s1_v2.20.0.yaml (branch de documentos).

Próxima ação: definir onde o 1º lote da curadoria roda no Open (a fila está na branch de documentos, o playbook na main).
Não faça: ajuste direto no starter (ele é gerado do Open); documento SDD na main.
Landmines: LM-035 (sdd/bin/ citado em skill que vai ao starter).
```
