# HANDOFF: F26 Documentos na main e marca do SDD Starter

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).
> Vive no repositório (`sdd/handoffs/HANDOFF_{FEATURE}.md`), não na memória de nenhum agente:
> viaja com o projeto e qualquer agente, em qualquer máquina, retoma daqui.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F26_DOCS_NA_MAIN |
| **Objetivo** | Os documentos das frentes saem da branch `docs/incorporar-starter` e passam a morar na `main`, no PR de cada frente, com duas travas que os seguram fora do pacote, varredura própria e a evidência bruta fora do git; as skills geradas para o starter ganham a marca "SDD Starter" (bloco separado, pedido do Roberto) |
| **Status** | ✅ DoD fechado — publicado na `v2.23.0` (`main` = `8d47908`, PR #39, CI 18 de 18), 2026-11-18; Release conferida (`shasum -c` OK, `VERSION` = `v2.23.0`, 751 arquivos = 751 linhas do `MANIFEST`, 0 documentos no pacote); tag `arquivo/docs-incorporar-starter` = `511d6fa` no remoto e `--pode-aposentar` PODE |
| **Última sessão** | 2026-11-18 |
| **Branch / pasta** | `feat/f26-docs-na-main` · `/Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main` (nascida de `origin/main` em `304e60a`; entrou na `main` num commit só); a história detalhada fica nas branches locais `f26-historia` e `f26-reserva-antes-da-remigracao` |
| **Artefatos** | `sdd/archive/F26_DOCS_NA_MAIN/{DEFINE,DESIGN,BUILD_REPORT}_F26_DOCS_NA_MAIN.md` · `sdd/reviews/{GOVERNANCA_REVIEW,LEDGER_REVISAO}_F26_DOCS_NA_MAIN.md` · `sdd/reviews/AVALIACAO_F26_DOCS_NA_MAIN_20261118-{0753,0856}.md` · `sdd/reports/evidence/F26_DOCS_NA_MAIN/` · `sdd/reports/evidence/LOTE_20261118/` · `sdd/reports/MIGRACAO_DOCS_F26.tsv` · `sdd/releases/F26_DOCS_NA_MAIN/s1_v2.23.0.yaml` |
| **Verify Gate** | 🟢 0 em `4ccb0ef` (2.586 testes, 4 pulados), e a mesma suíte verde num clone com os documentos; CI do PR #39 verde em Linux, macOS e Windows (16 fatias) |

## Publicado

> Gerado por `python3 sdd/bin/ficha-publicado.py F26_DOCS_NA_MAIN` a partir de `sdd/releases/F26_DOCS_NA_MAIN/`:
> uma linha por release, a mais recente no topo. Não edite à mão; o que o ledger já diz não se repete nas outras seções.

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-18 · s1 · 2.23.0 · shipado · CONCERNS · deploy real · trilha completa · 8d47908
<!-- publicado:fim -->

## Feito

- Tudo do DEFINE (AT-001 a AT-012) está na `v2.23.0`; a descrição e a prova estão no ledger da publicação.
- Curadoria: 2 lotes julgados antes da migração (F23B2 e F25; LM-039 a LM-044), fila vazia na migração.
- Migração: 2.866 documentos iguais e 1 ajustado na `main`; 399 (bruto, 6 reprovados pela varredura, 1 acima de 256 KB) só na tag de arquivo.

## Falta

1. **Starter:** regerar pela tag `v2.23.0` num clone limpo do sdd-starter (as 18 skills com a marca). Push, PR e merge lá pedem o OK do Roberto.
2. **Branch e worktree de documentos:** apagar `docs/incorporar-starter` (remoto e local) e a worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-docs` depois de o Roberto conferir a `main`. A tag `arquivo/docs-incorporar-starter` fica. Antes de apagar: `python3 -B scripts/docs-migracao.py --pode-aposentar arquivo/docs-incorporar-starter` (PODE em 2026-11-18).
3. **Branch da frente:** apagar `feat/f26-docs-na-main` do remoto (integrada: a `main` é o mesmo commit); a branch local, as branches `f26-historia` e `f26-reserva-antes-da-remigracao` e a worktree saem de fora dela, com o OK do Roberto.
4. Curadoria: na fila (`sdd/curadoria/fila/F26_DOCS_NA_MAIN/20261118T140442Z`, 24 contagens e 6 candidatos); o próximo lote da `sdd-playbook` julga.
5. Smoke depois do deploy: pulado — slot vazio (o Open não tem `sdd/config.yaml`); a Release foi conferida à mão.

## Definition of Done

- [x] AT-001 a AT-012 com log por AT (`sdd/reports/evidence/F26_DOCS_NA_MAIN/AT-*.log`) e avaliador fresco PASS_PENDENTE_RECIBO (ciclo 2), com os recibos fechados na publicação: CI do PR nos 3 sistemas, push da branch de documentos e da tag de arquivo (`--pode-aposentar` PODE), bruto (SEM BRUTO)
- [x] Verify Gate verde em `4ccb0ef` e a suíte num clone com os documentos
- [x] Release `v2.23.0` conferida
- [ ] Starter regerado (item 1 de Falta)

## ⛔ Landmines desta feature

- Numa lista de permissão do `.gitattributes`, cada pasta liberada pede 2 linhas (`pasta -export-ignore` e `pasta/** -export-ignore`); só a do conteúdo tira a pasta inteira do `git archive`, calado.
- Regex de e-mail sem teto tem custo quadrático em linha longa: quantificadores com teto e só a linha com `@`.
- O `tar` do macOS põe `._<nome>` no pacote (`COPYFILE_DISABLE=1`) e grava nome acentuado decomposto (NFD): compare listas em NFC.
- Evidência gravada no Windows tem CRLF: `sdd/reports/evidence/** -text`, senão o blob muda ao migrar.
- O gate numa cópia de `git archive` não vê teste que percorre o checkout: com documentos na `main`, rode a suíte também num clone.
- Número de 11 dígitos em comentário de código vai para o pacote e o G2 barra (LM-012): o exemplo de CPF se descreve, não se escreve.
- A migração de uma vez só fecha com a origem parada: outra sessão gravou na branch de documentos depois da 1ª tag; o Roberto congelou a branch e a migração foi refeita no último commit.

## Casos e testes em aberto

- ✨ A7 (avaliador): `--padrao` com `--ref` não olha o histórico da tag (só o `--texto` olha); o CONTRIBUTING manda o `--texto`.
- ✨ A8 (avaliador): a `sdd-release` não diz o que fazer com o exit 2 (NÃO CONFERIDO) da varredura dos documentos; o certo é abortar.
- ✨ Item 7 da `sdd-release` (exit dos logs) sobre o diff inteiro acusa 85 logs antigos que vieram da tag e não podem mudar: escopo do item para a evidência da frente.
- ✨ R8 e N1 da revisão do código ficaram rebatidos (evidência e escopo), sem conserto.

## Eventos

- 2026-11-17 — Roberto pediu a marca "SDD Starter" nas skills do starter como bloco separado dentro da F26.
- 2026-11-18 — lotes da curadoria: o 1º julgou F23B2 e F25 (5 regras aceitas); a entrada recusada da F25 saiu pela colheita nova, julgada num 2º lote (2 aceitas, 2 recusadas, entre elas uma contagem dupla do LM-037).
- 2026-11-18 — revisão do código: 8 aplicadas, 2 rebatidas; o 2º revisor (gemini) sem credencial, dispensado pelo Roberto.
- 2026-11-18 — avaliador fresco: ciclo 1 NEEDS_WORK (2 falhas que deixariam o CI vermelho, 4 de segurança); ciclo 2 PASS_PENDENTE_RECIBO.
- 2026-11-18 — outra sessão gravou na branch de documentos depois da 1ª tag; Roberto congelou a branch até a F26 entrar na `main` e a migração foi refeita em `511d6fa`.
- 2026-11-18 — publicação: PR #39 (18 de 18), `main` = `8d47908`, tag `v2.23.0` por push atômico, Release às 14:57 UTC; branch de documentos e tag de arquivo enviadas; `--pode-aposentar` PODE.

## Recomendações

- Frente que põe no repositório arquivos fora do pacote: o Verify Gate roda numa cópia e num clone.
- Depois de cada commit de código, o publish-gate sobre o pacote (o G2 pega número em comentário).

## Veredito

- 🟡 CONCERNS — revisão externa dispensada com motivo no ledger; as pendências de "Casos e testes em aberto".

## Setup

1. `cd /Users/robertoduarte/rdd-public/sdd-open && git fetch origin` — a `main` em `8d47908` ou depois.

## Tarefas

1. Os itens 1 a 3 de Falta, cada um com o OK do Roberto.

## Ship

- **Publicar:** feito (`v2.23.0`, PR #39, `8d47908`).
- **Limpar:** pendente (itens 2 e 3 de Falta).

## Prompt de retomada

```text
Retomar a F26 (documentos na main) do SDD Open. Leia sdd/handoffs/HANDOFF_F26_DOCS_NA_MAIN.md na main
(git -C /Users/robertoduarte/rdd-public/sdd-open fetch origin; a ficha está na main desde a F26). A F26 está
publicada (v2.23.0). Falta: regerar o starter pela tag v2.23.0 (OK do Roberto no sdd-starter), apagar a branch
docs/incorporar-starter e a worktree sdd-open-docs depois de o Roberto conferir a main (rode antes o --pode-aposentar),
e limpar a branch e a worktree da frente. Responda em português; publicar ou apagar pede o OK do Roberto.
```
