# HANDOFF: F28 Revisores pelo OpenRouter (skill sdd-configurar-revisores)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F28_REVISORES_OPENROUTER |
| **Objetivo** | Skill nova `sdd-configurar-revisores`: o aluno nunca fica sem próximo passo para configurar quem revisa e quem audita na revisão adversarial (CLIs que ele tem, OpenRouter com dois modelos, ou uma engine só), a chave nunca passa pela conversa, e a prova não gasta |
| **Status** | ✅ DoD fechado — publicado na `v2.25.0` (`main` = `f50f244`, PR #41, CI 18 de 18), 2026-11-19; starter **`v1.5.29`** (13ª geração, PR #22 de lá, 19 zips OK no `shasum -c`); Release conferida (`shasum -c` OK, `VERSION` = `v2.25.0`, 775 arquivos = 775 linhas do `MANIFEST`, 0 documentos no pacote; publicada às 10:50 UTC pelo run da `main` 44500503857) |
| **Última sessão** | 2026-11-19 |
| **Branch / pasta** | `feat/f28-revisores-openrouter` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter` (nascida de `origin/main` em `eaeb874`; entrou na `main` em 2 commits, o da frente e o conserto do `test_f17_textos`); a história detalhada fica na branch local `backup/f28-historia` |
| **Artefatos** | `sdd/archive/F28_REVISORES_OPENROUTER/{DEFINE,DESIGN,BUILD_REPORT}_F28_REVISORES_OPENROUTER.md` · `sdd/reviews/{GOVERNANCA_REVIEW,UX_REVIEW,LEDGER_REVISAO}_F28_REVISORES_OPENROUTER.md` · `sdd/reviews/AVALIACAO_F28_REVISORES_OPENROUTER_20261118-2207.md` · `sdd/releases/F28_REVISORES_OPENROUTER/s1_v2.25.0.yaml` · `sdd/reports/evidence/F28_REVISORES_OPENROUTER/` |
| **Verify Gate** | 🟢 0 em `016e591` (2.754 testes, 4 pulados; o código é o mesmo de `d03337f`); CI do PR #41 verde em Linux, macOS e Windows (16 fatias) em `f50f244` |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F28_REVISORES_OPENROUTER` a partir de `sdd/releases/F28_REVISORES_OPENROUTER/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-19 · s1 · 2.25.0 · shipado · CONCERNS · deploy real · trilha completa · d03337f
<!-- publicado:fim -->

## Feito

- Tudo do DEFINE (AT-001 a AT-010) está na `v2.25.0`; a descrição e a prova estão no ledger da publicação.
- Curadoria: na fila (`sdd/curadoria/fila/F28_REVISORES_OPENROUTER/20261119T095433Z`, 14 contagens e 4 candidatos); o próximo lote da `sdd-playbook` julga.

## Falta

1. ~~Limpeza~~ — feita em 2026-11-19, com o OK do Roberto: as branches remotas `feat/f28-revisores-openrouter` (Open) e `gen/v2.25.0` (starter), integradas (`git cherry` sem `+`), apagadas; logo depois deste commit, de fora da pasta, `git worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter` e `git branch -D feat/f28-revisores-openrouter backup/f28-historia`.
2. Smoke depois do deploy: pulado — slot vazio (o Open não tem `sdd/config.yaml`); a Release foi conferida à mão.
3. 🐛 O run da tag `v2.25.0` (44500504242) caiu numa fatia de Windows: `test_alarme.TestCopiaGerada.test_copia_gerada_liga_o_alarme_nos_hooks_do_projeto` com erro em 230 s (cara de teto de subprocesso sob carga). A Release já tinha saído pelo run da `main`; o mesmo commit passou nas 16 fatias do CI do PR; a F28 não toca no alarme nem no `init`. Não foi reexecutado (o run publicaria de novo uma tag existente). Medir se repete no próximo PR.

## Definition of Done

- [x] AT-001 a AT-010 com log por AT (`sdd/reports/evidence/F28_REVISORES_OPENROUTER/AT-*.log`) e avaliador fresco PASS_PENDENTE_RECIBO (ciclo 1), com o recibo fechado na publicação: CI do PR #41 nos 3 sistemas
- [x] Verify Gate verde em `016e591`
- [x] Release `v2.25.0` conferida
- [x] Starter `v1.5.29` publicado

## ⛔ Landmines desta feature

- Texto de cenário ou fixture com a forma de chave (`sk-or-v1-…` longo) bloqueia a varredura S11 da release: descreva a chave, não a escreva.
- As seções de revisão das skills de fase não nomeiam provedor ("OpenRouter"): `test_contrato_build_release` e `test_f19_textos` reprovam.
- A troca do starter (`scripts/starter/trocas/<skill>.md`) copia o texto do Open à letra: toda mudança no trecho exige refazer a troca (a rodada 3 pegou; o gerador pararia).
- Python embutido em script precisa do bloco de saída padrão com os nomes `_sdd_sys`/`_sdd_c` (`test_f16w2_saida`).
- `urllib` segue redirect e repassa o `Authorization`: chamada com chave usa um opener sem redirect.
- Log de evidência de comando em segundo plano: grave fora de `sdd/reports/evidence/` e copie no fim (um `git add` no meio commita o log pela metade).
- Documento arquivado (`sdd/archive/`) não é pacote: o `test_f17_textos` lia a pasta e quebrou o CI da `main` depois do papel da F27 (consertado aqui).

## Casos e testes em aberto

- ✨ O caminho do Windows (janela de variáveis do usuário, herança pelo Git Bash e pelo editor) não foi testado num Windows; os nomes da janela vêm de fonte não oficial.
- ✨ Os rótulos dos botões das páginas logadas do OpenRouter não estão na documentação; conferir numa conta e datar no `PASSO_A_PASSO.md`.
- ✨ Quem escolhe "uma engine só" continua vendo o aviso de revisores não configurados no `checar` (não há onde gravar a escolha sem afrouxar a regra auditor ≠ revisor; decisão do Roberto se quiser mudar).
- ✨ O glossário da `sdd-checar-ambiente` não traduz "revisão adversarial" nem "OpenRouter".
- ✨ O `SKILL.md` da `sdd-checar-ambiente` gerado no starter fica com 3 linhas em branco seguidas no lugar do item 8.
- ✨ A leitura do slot pelo `git config --get` também enxerga o global (benigno; a skill grava só o local); documentar ou usar `--local`.
- ✨ Cenários de conversa rodados só num agente (o que construiu a skill); rodar noutro.
- ✨ Revisão de toda a frente com uma IA só (`diversidade: nenhuma`): o codex está sem créditos e o gemini sem credencial nesta máquina.

## Eventos

- 2026-11-18 — frente aberta e registrada no plano; Define (governança REVISADO: G09 aplicada, G16 risco aceito; segurança S10, S17, S18, S20), UX review (13 MUST), Design (revisão D1 sem auditor e D2 com 9 notas aplicadas).
- 2026-11-18 — Build: skill, scripts, ganchos, docs; linha de base vermelha e 7 sabotagens; cenários 6 de 6; revisão do código em 3 rodadas (6, 5 e 2 achados, 0 graves, cada um com teste vermelho antes); avaliador PASS_PENDENTE_RECIBO (2 achados corrigidos); 1º gate vermelho (`test_f16w2_saida`), 2º verde.
- 2026-11-19 — release: D3 do Roberto (publicar com a dispensa da revisão da versão final); PR #41, 1º CI vermelho pelo `test_f17_textos` (arquivo de `sdd/archive/` da F27), conserto, 2º CI 18 de 18; `main` = `f50f244` e tag `v2.25.0` por push atômico.
- 2026-11-19 — starter: 13ª geração pela tag `v2.25.0` num clone limpo (`246f621`; check-gerado VERDE, check-versions e publish-check PASS, testes, gate da KB e 19 zips), PR #22 de lá, avanço direto da `main`, Release `v1.5.29` (19 zips OK).
- 2026-11-19 — frente encerrada: ficha final, branches remotas apagadas, worktree e branches locais removidas.
- 2026-11-19 — Release `v2.25.0` conferida; o run da tag caiu numa fatia de Windows (`test_alarme`, pendência 3 de "Falta").

## Recomendações

- Ao mexer em texto de uma skill do starter, rode o `test_gerar_starter` depois de cada rodada de consertos, não só uma vez.
- Antes do PR, rode o `test_f17_textos` e os textos de frentes antigas na árvore de trabalho (o gate usa a cópia de `git archive`, o CI usa o checkout).

## Veredito

- 🟡 CONCERNS — revisão externa da versão final dispensada com motivo no ledger (D3); revisão com uma IA só; caminho do Windows não testado num Windows.

## Setup

1. `cd /Users/robertoduarte/rdd-public/sdd-open && git fetch origin` — a `main` em `f50f244` ou depois.

## Tarefas

1. Nenhuma: a frente está encerrada. As pendências ✨ de "Casos e testes em aberto" ficam para uma frente futura.

## Ship

- **Publicar:** feito (`v2.25.0`, PR #41, `f50f244`; starter `v1.5.29`, PR #22).
- **Limpar:** feito (branches remotas no Open e no starter, worktree e branches locais).

## Prompt de retomada

```text
Retomar a F28 (revisores pelo OpenRouter) do SDD Open. Leia sdd/handoffs/HANDOFF_F28_REVISORES_OPENROUTER.md na
main (git -C /Users/robertoduarte/rdd-public/sdd-open fetch origin). A F28 está publicada (v2.25.0, PR #41; starter
v1.5.29). A frente está encerrada, com a limpeza feita. O que sobra são as pendências ✨ e 🐛 de "Falta" e de
"Casos e testes em aberto", para uma frente futura. Responda em português; publicar ou apagar pede o OK do Roberto.
```
