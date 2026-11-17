# HANDOFF: F25 Skills duplicadas

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F25_SKILLS_DUPLICADAS |
| **Objetivo** | A `sdd-checar-ambiente` avisa quando o mesmo agente lê a mesma skill do SDD em dois lugares (global e no projeto), dizendo onde está cada cópia, a versão, a origem e qual roda; e, só com o sim do aluno ao plano mostrado, tira a cópia mais velha para uma lixeira, com um comando que desfaz. |
| **Status** | ✅ DoD fechado — publicado na `v2.22.0` (`main` = `304e60a`, PR #38, CI 18 de 18), 2026-11-17; Release conferida (`shasum -c` OK, prefixo `4550ce4a5ce3`, `VERSION` = `v2.22.0`); starter **`v1.5.26`** (10ª geração, PR #19 de lá, 18 zips OK no `shasum -c`) |
| **Última sessão** | 2026-11-17 |
| **Branch / pasta** | `feat/f25-skills-duplicadas` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f25-skills-duplicadas` (nascida de `origin/main` em `017f09a`, rebaseada sobre `2204a14`, v2.21.0) |
| **Artefatos** | `sdd/archive/F25_SKILLS_DUPLICADAS/{DEFINE,DESIGN,BUILD_REPORT,DRIVE_REPORT}_F25_SKILLS_DUPLICADAS.md` · `sdd/reviews/{UX_REVIEW,LEDGER_REVISAO}_F25_SKILLS_DUPLICADAS.md` · `sdd/reviews/AVALIACAO_F25_SKILLS_DUPLICADAS_20261117-1222.md` · `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/` (experimentos EXP-1 a 3, protótipo, ATs, gates, vermelhos da revisão) · `sdd/reports/reviews-medicao/F25_SKILLS_DUPLICADAS/` · `sdd/curadoria/fila/F25_SKILLS_DUPLICADAS/20261117T215105Z/` — todos na branch de documentos `docs/incorporar-starter` |
| **Verify Gate** | 🟢 0 em `c854f81` (2.540 testes, 4 pulados) — `bash sdd/bin/verify-gate.sh sdd/archive/F25_SKILLS_DUPLICADAS/DEFINE_F25_SKILLS_DUPLICADAS.md`; CI do PR #38: Linux e macOS verdes; Windows verde depois de `e35fc37` e `739eda7`, com a fatia 4 cancelada pelo runner na última rodada (passou nas 2 anteriores; o `release.yml` roda o Windows de novo antes de publicar) |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F25_SKILLS_DUPLICADAS` a partir de `sdd/releases/F25_SKILLS_DUPLICADAS/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-17 · s1 · 2.22.0 · shipado · CONCERNS · deploy real · trilha completa · 3e16413
<!-- publicado:fim -->

## Feito

- Tudo do ESCOPO (DC1 a DC4) e do DEFINE (AT-001 a AT-010) está na `v2.22.0`; a descrição e a prova estão no ledger da publicação.

## Falta

1. ~~Starter~~ — feito: 10ª geração pela tag `v2.22.0` num clone limpo (`4dbdea1`: `sdd-build` 2.13.0 e `sdd-checar-ambiente` 1.6.0); `check-gerado` VERDE, `publish-check` e `check-versions` PASS, testes OK; PR #19 de lá, CI verde, avanço direto da `main` (`9782444..4dbdea1`); Release **`v1.5.26`**, 18 zips OK.
2. Remover a worktree e a branch local da frente (comandos em Ship).
3. Curadoria: na fila (`20261117T215105Z`, 3 contagens e 3 candidatos); o lote da `sdd-playbook` julga sob demanda.
4. Smoke depois do deploy: pulado — slot vazio (o Open não tem `sdd/config.yaml`); a Release foi conferida à mão (`shasum -c`, `VERSION`, a skill nova no pacote).

## Definition of Done

- [x] AT-001 a AT-010 com log por AT (`sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-*.log`) e avaliador fresco PASS
- [x] Verify Gate verde em `c854f81`
- [x] Release `v2.22.0` conferida e starter `v1.5.26` publicado

## ⛔ Landmines desta feature

- O `npx skills remove <s> -g` apaga a pasta de mesmo nome que ele não instalou (`~/.claude/skills`, `~/.agents/skills`): toda saída pelo npx protege a outra cópia antes (EXP-3).
- Com `env -i`, o `HOME` de um script deixa de ser exportado e o `node` de um CLI cai na pasta pessoal real: `HOME` explícito na linha de cada comando; os npx de teste recusam HOME fora da pasta de teste.
- O gerador do starter troca a URL completa do Open pela do starter em todo arquivo: reconhecer a origem pelo trecho `<repositório>/releases/latest`, nunca pela URL inteira.
- No gawk (o awk do Git Bash), `or`, `and`, `xor` etc. são funções: nunca nomes de variável.
- No Git Bash, o git devolve `C:/…` e o bash `/c/…`: caminhos comparados ou mostrados lado a lado passam pelo bash (`cd … && pwd`).
- Documento commitado na branch de código reprova no `publish-gate` (`undeclared file`): documentos só na branch de documentos.

## Casos e testes em aberto

- ✨ Caminho com barra invertida passado ao awk por `-v` (passar por `ENVIRON`); não ocorre em macOS, Linux nem Git Bash (rodada 4, R3).
- ✨ A frase "Nada foi tirado" quando o npx tocou uma pasta fora do plano (a frase do erro já nomeia a pasta; trocar por "Nada do plano foi tirado") (rodada 4, R2).
- ✨ `CDPATH` exportado com o `checar.sh` chamado por caminho relativo sem `./` (padrão que já existia no arquivo; raio de impacto).
- ✨ "Para desfazer" impresso quando nada saiu (A2 do avaliador).
- ✨ Medir `$CLAUDE_CONFIG_DIR/skills` como pasta global do Claude Code (A-001 do DEFINE; o Claude Code exige login, e o HOME de teste não serve).

## Eventos

- 2026-11-17 — experimento 3: o `npx skills remove -g` apaga a cópia manual de mesmo nome; pergunta `[D2]` ao Roberto: "Proteger e usar o npx".
- 2026-11-17 — o protótipo do Design pegou 4 defeitos antes do build (hash dentro de repositório, falso negativo do `source`, motivo da trava sem grupo, `` `sync` `` no starter).
- 2026-11-17 — a `main` andou para a `v2.21.0` (F23 B2) durante a release: rebase limpo, a F25 sobe como `v2.22.0`.
- 2026-11-17 — revisão do código em 6 rodadas: o laço fechou na 3ª (0 graves); 4ª e 5ª com o OK do Roberto (D4); 7ª dispensada por ele (D4), com o `review_externo` dispensado e o motivo no ledger.
- 2026-11-17 — CI do Windows do PR #38: caminhos `C:\…` × `/c/…` no teste e na raiz do projeto; nome de pasta com aspas no teste.
- 2026-11-17 — o Roberto liberou seguir sem esperar a fatia 4 do Windows (cancelada pelo runner; o `release.yml` roda o Windows de novo).

## Recomendações

- Revisão de confirmação da versão final acha bordas novas a cada rodada no código de recuperação de falha; para a próxima frente com `--limpar` ou parecido, prever o teto de rodadas de confirmação no DESIGN.

## Veredito

- 🟡 CONCERNS — as pendências do ledger da publicação e dos "Casos e testes em aberto".

## Setup

1. `cd /Users/robertoduarte/rdd-public/sdd-open && git fetch origin` — a `main` em `304e60a` ou depois.

## Tarefas

1. **Remover a worktree e a branch local da frente** — Pronto quando: `git worktree list` não mostra a pasta da F25.

## Ship

- **Publicar:** feito (`v2.22.0`, PR #38, `304e60a`; starter `v1.5.26`).
- **Limpar:** `git worktree remove --force /Users/robertoduarte/rdd-worktrees/sdd-open-f25-skills-duplicadas` e `git branch -D feat/f25-skills-duplicadas` (o `--force` porque a pasta guarda as cópias de trabalho dos documentos, já commitadas aqui).

## Prompt de retomada

```text
Retomar a F25 (skills duplicadas) do SDD Open. Leia sdd/handoffs/HANDOFF_F25_SKILLS_DUPLICADAS.md na branch
docs/incorporar-starter (worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs). A F25 está publicada (v2.22.0 e starter
v1.5.26). Só falta limpar a worktree da frente (comandos em Ship) e, quando o Roberto pedir, o lote da curadoria julgar
a entrada da fila. Os "Casos e testes em aberto" são candidatos a uma próxima versão da sdd-checar-ambiente.
```
