# HANDOFF: F27 Desempenho do banco (skill sdd-desempenho-banco)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F27_DESEMPENHO_BANCO |
| **Objetivo** | Skill nova `sdd-desempenho-banco`: o que deixa o banco lento (Supabase/Postgres), do Define à publicação, e o diagnóstico do banco no ar a pedido, só de leitura; só avisa, nunca trava uma fase nem escreve no banco |
| **Status** | ✅ DoD fechado — publicado na `v2.24.0` (`main` = `c318aad`, PR #40, CI 18 de 18), 2026-11-18; starter **`v1.5.28`** (12ª geração, PR #21 de lá, 19 zips OK); Release conferida (`shasum -c` OK, `VERSION` = `v2.24.0`, 766 arquivos = 766 linhas do `MANIFEST`, 0 documentos no pacote; publicada às 20:28 UTC, run 44382607599) |
| **Última sessão** | 2026-11-18 |
| **Branch / pasta** | `feat/f27-db-performance` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance` (nascida de `origin/main` em `2204a14`, rebase sobre `456c69b`; entrou na `main` num commit só); a história detalhada fica nas tags locais `f27-antes-do-rebase` e `f27-antes-do-squash` |
| **Artefatos** | `sdd/archive/F27_DESEMPENHO_BANCO/{BRAINSTORM,DEFINE,DESIGN,BUILD_REPORT}_F27_DESEMPENHO_BANCO.md` · `sdd/reviews/LEDGER_REVISAO_F27_DESEMPENHO_BANCO.md` · `sdd/reviews/AVALIACAO_F27_DESEMPENHO_BANCO_20261117-{2008,2020,2059,2108}.md` · `sdd/releases/F27_DESEMPENHO_BANCO/s1_v2.24.0.yaml` · `sdd/reports/evidence/F27_DESEMPENHO_BANCO/` |
| **Verify Gate** | 🟢 0 em `8bdfe14` (2.686 testes, 4 pulados; o código é o mesmo de `c318aad`); CI do PR #40 verde em Linux, macOS e Windows (16 fatias) |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F27_DESEMPENHO_BANCO` a partir de `sdd/releases/F27_DESEMPENHO_BANCO/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-18 · s1 · 2.24.0 · shipado · CONCERNS · deploy real · trilha completa · c318aad
<!-- publicado:fim -->

## Feito

- Tudo do DEFINE (AT-001 a AT-011) está na `v2.24.0`; a descrição e a prova estão no ledger da publicação.
- Curadoria: na fila (`sdd/curadoria/fila/F27_DESEMPENHO_BANCO/20261118T194044Z`, 20 contagens e 3 candidatos); o próximo lote da `sdd-playbook` julga.

## Falta

1. ~~Starter~~ — feito em 2026-11-18, com o OK do Roberto: 12ª geração pela tag `v2.24.0` num clone limpo (`6b3ba9f`); `check-gerado` VERDE, `publish-check` e `check-versions` PASS (19 skills), testes, gate da KB e 19 zips OK; PR #21 de lá, CI verde, avanço direto da `main` (`bc2894e..6b3ba9f`); Release **`v1.5.28`**, 19 zips OK no `shasum -c`. A branch `gen/v2.24.0` do starter foi apagada (integrada).
2. Branch da frente: a remota `feat/f27-db-performance` sai depois do commit de papel (integrada: `git cherry` sem `+`). Falta, de fora desta pasta e com o OK do Roberto: `git worktree remove /Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance`, `git branch -D feat/f27-db-performance` e `git tag -d f27-antes-do-rebase f27-antes-do-squash`.
3. Smoke depois do deploy: pulado — slot vazio (o Open não tem `sdd/config.yaml`); a Release foi conferida à mão.

## Definition of Done

- [x] AT-001 a AT-011 com log por AT (`sdd/reports/evidence/F27_DESEMPENHO_BANCO/AT-*.log`) e avaliador fresco PASS_PENDENTE_RECIBO (ciclo 4), com o recibo fechado na publicação: CI do PR #40 nos 3 sistemas
- [x] Verify Gate verde em `8bdfe14`, depois do rebase sobre `v2.23.0` e das rodadas 2 e 3 da revisão do código
- [x] Release `v2.24.0` conferida
- [x] Starter `v1.5.28` publicado

## ⛔ Landmines desta feature

- Máscara de texto do banco por regex se desalinha: comentário (inclusive aninhado), identificador entre aspas duplas, `E'…\'…'`, `$tag$` e texto cortado no meio abrem um "literal" falso e soltam o valor seguinte. A máscara falha fechada: o que ela não lê com segurança vira `[omitido]`/`…[cortado]`, no script e no SQL.
- O `mktemp -d` do macOS ignora o `TMPDIR` sem molde: use `mktemp -d "${TMPDIR:-/tmp}/nome.XXXXXX"`.
- Script novo com Python embutido precisa do bloco de saída UTF-8 do F16W2 (`test_f16w2_saida`) e de string sem escape inválido (Python 3.12+ avisa em toda execução).
- `\b` depois de um nome entre aspas duplas não casa (`on "public"."pedidos"`, o formato do `supabase db diff`): use `(?![\w$"])`.
- Relatório que só lista o que achou sai "limpo" quando não leu a fonte: comando que falhou, JSON não reconhecido e arquivo vazio têm de aparecer.
- Rebase sobre uma frente que subiu a mesma skill: a versão que as duas escolheram pode coincidir (a F26 usou a `sdd-release` 2.17.0) — o `check-versions --base <tag nova>` acusa.

## Casos e testes em aberto

- ✨ O1 (avaliador): nome entre aspas duplas sem fechar sai inteiro no diagnóstico (é identificador, não valor de cliente).
- ✨ O2 (avaliador): string de conexão `chave=valor` sem senha vira nome de arquivo no `--saida`; a URL sem senha é recusada.
- ✨ O3 (avaliador): a dispensa com motivo curto avisa uma vez por ficha da mesma linha.
- ✨ Raio de impacto: o molde do modo web do Design (o que o starter usa) não tem `## Segurança` nem `## Desempenho`; o exemplo do bloco do OK em `sdd-release/references/como-falar.md` não tem as linhas Segurança e Desempenho; no `DEFINE_TEMPLATE`, o bullet Desempenho vem antes do Segurança.
- ✨ Na cópia do starter, a mensagem que a consulta mostra quando omite o texto (consultas 3, 7 e 8) diz "leia pelo script", e o starter não tem o script; mudar no Open para uma frase neutra (ex.: "leia pelo painel ou pelo script do SDD Open") e gerar de novo.
- ✨ `test_deploy_do_sha.Redisparo.test_slots_preenchem_workflow_passos_e_branch` (teto de 1 minuto) falhou uma vez sob carga num gate e passou 5 de 5 sozinho.

## Eventos

- 2026-11-17 — Define (governança dispensada pelo Roberto), Design (3 rodadas de revisão) e Build; avaliador fresco em 4 ciclos (3º e 4º com o OK do Roberto) até PASS_PENDENTE_RECIBO.
- 2026-11-18 — F25 (`v2.22.0`) e F26 (`v2.23.0`) publicadas; rebase sobre `456c69b` (conflitos só de versão e uma linha do `MANIFEST.txt`); `sdd-release` para 2.18.0.
- 2026-11-18 — raio de impacto em 4 superfícies, sem quebra; 3 textos do starter corrigidos.
- 2026-11-18 — revisão do código, rodadas 2 e 3: 12 achados, 0 graves, todos aplicados com teste vermelho antes; a máscara do SQL das consultas 3, 7 e 8 provada num Postgres 16 local. A revisão da versão final foi dispensada pelo Roberto (D3), com o motivo no ledger.
- 2026-11-18 — starter: 12ª geração pela tag `v2.24.0`, PR #21 de lá, Release `v1.5.28` (19 zips).
- 2026-11-18 — publicação: PR #40 (18 de 18), `main` = `c318aad`, tag `v2.24.0` por push atômico, Release às 20:28 UTC; sem evidência bruta para anexar.

## Recomendações

- Máscara de dado de terceiros: falhe fechada e prove com o motor real (aqui, o Postgres local) além do teste em Python.
- Rebase depois de outra frente: rode o `check-versions --base <tag nova>` antes da suíte.

## Veredito

- 🟡 CONCERNS — revisão externa da versão final dispensada com motivo no ledger; as pendências de "Casos e testes em aberto".

## Setup

1. `cd /Users/robertoduarte/rdd-public/sdd-open && git fetch origin` — a `main` em `c318aad` ou depois.

## Tarefas

1. O item 2 de Falta, com o OK do Roberto.

## Ship

- **Publicar:** feito (`v2.24.0`, PR #40, `c318aad`; starter `v1.5.28`, PR #21).
- **Limpar:** branch remota depois do commit de papel; falta a worktree, a branch local e as tags locais da frente (item 2 de Falta).

## Prompt de retomada

```text
Retomar a F27 (desempenho do banco) do SDD Open. Leia sdd/handoffs/HANDOFF_F27_DESEMPENHO_BANCO.md na main
(git -C /Users/robertoduarte/rdd-public/sdd-open fetch origin). A F27 está publicada (v2.24.0, PR #40; starter
v1.5.28). Falta só limpar a worktree, a branch local e as tags locais da frente (item 2 de Falta). Responda em
português; apagar pede o OK do Roberto.
```
