# HANDOFF: F30 — Qualidade do código gerado (Uncle Bob × Open)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Objetivo** | O código que o método gera segue Clean Code e TDD: lint e tipos a cada tarefa, regras de qualidade por stack, vermelho antes do verde, sabotagem do gate, refatorar depois do verde e métricas de forma no diff (só aviso) |
| **Status** | 🚢 S2 publicada na `v2.27.1` (2026-11-24, tag em `a6f1f5e`; a `v2.27.0` ficou sem Release) e starter **`v1.5.32`**; S1 na `v2.26.0`; S3 aberta |
| **Última sessão** | 2026-11-24 |
| **Branch / pasta** | S2: `s2-sdd-open-uncle-bob` · `/Users/robertoduarte/rdd-worktrees/s2-sdd-open-uncle-bob` (a `main` avançou direto para o HEAD da frente; a branch não existe no remoto). S1: `f30-sdd-open-uncle-bob` |
| **Artefatos** | `sdd/features/{AVALIACAO_F30_UNCLE_BOB,ESCOPO_F30_QUALIDADE_CODIGO,DEFINE_F30_QUALIDADE_CODIGO,DESIGN_F30_QUALIDADE_CODIGO}.md` · `sdd/reports/BUILD_REPORT_F30_QUALIDADE_CODIGO.md` · `sdd/reviews/{AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2035,AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2050,LEDGER_REVISAO_F30_QUALIDADE_CODIGO}.md` · `sdd/releases/F30_QUALIDADE_CODIGO/{s1_v2.26.0,s2_v2.27.0}.yaml` · `sdd/reviews/AVALIACAO_F30_QUALIDADE_CODIGO_20261124-{1225,1300}.md` · `sdd/reports/evidence/F30_QUALIDADE_CODIGO/` |
| **Verify Gate** | 🟢 S2: 0 em `d1b0c51` (2.870 testes, 4 pulados, 35,5 min); S1: 0 em `76827bf` — `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` |
| **Veredito das releases** | 🟡 S2 CONCERNS (6 avisos) · 🟡 S1 CONCERNS (4 avisos), em "Falta" |

## Publicado

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-24 · s2 · 2.27.1 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.27.1 posta à mão no commit a6f1f5e; a v2.27.0 ficou sem Release: o CI caiu na fatia 15/16 do Windows por um teste do link simbólico, corrigido) · trilha completa · d72f53f
- 2026-11-24 · s2 · 2.27.0 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.27.0 posta à mão no commit, como as minor anteriores) · trilha completa · 5e89137
- 2026-11-23 · s1 · 2.26.0 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.26.0 posta à mão no commit, como as minor anteriores) · trilha completa · c4fa53c
<!-- publicado:fim -->

## Falta

1. ✨ **S3 — métricas no diff, só aviso (itens 5, 8):** `sdd-iterate` no mesmo DEFINE (seção "Fatia S3"; D5: complexidade 10, 60 linhas, 5 parâmetros, `jscpd --min-tokens 50`, em `qualidade.*` do config; proposta S3-a e S3-b no ESCOPO §6). Ferramenta ausente = "não medido", nunca "0 achados".
2. ⚠️ Avisos da release S2 (não abortaram):
   - nota de atualização: relatório novo nasce com a coluna `Antes` e o `report-lint` cobra o `AT-nnn.antes.log` de cada AT de gate `test`/`cmd`; relatório antigo só recebe aviso;
   - 🐛 observações leves do avaliador (ciclo 2) no `report-lint.py`: O-A citação com `..` passa no `problema_do_log` (anterior à S2; vale também para a coluna Evidência — normalizar o caminho); O-B cabeçalho `**Antes**` ou `Antes/vermelho` não é reconhecido; O-C sem `AT-nnn.log` no disco o comando do antes não é comparado; O-D `N.A.` sem motivo aceito em `manual-ux`; O-E antes que é link simbólico para fora da feature é aceito;
   - 🐛 2 LOW da rodada 3 no `sabotagem.sh`: sem `lib/python.sh`, a falta de Python sai 3 sem a mensagem própria; `git archive | tar` sem `pipefail` (falha do archive vira 64 em vez de 3);
   - ✨ `upgrade` e `sync` não mesclam chaves do config: projeto já instalado fica sem a seção `build:` (ausente = Refatorar ligado);
   - ✨ exigir por máquina a sabotagem (`≥ 1 por feature`) no `report-lint` ficou fora da S2 (Fora da S2 do DEFINE);
   - custo das revisões da S2: US$ 3,32 (4 rodadas); saldo do OpenRouter antes: US$ 9,97.
3. ⚠️ Avisos da release S1 que seguem: o `doctor` não avisa de arquivo novo de `sdd/bin/` ausente num projeto atualizado só com `sync`; o item 5 da `sdd-release` não cita o log de lint entre as causas de abortar.
4. ✨ O clone local `~/rdd-public/sdd-starter` está atrasado (11ª geração) e tem `docs/guia-do-aluno.pt-BR.md` fora do git; a 15ª e a 16ª gerações foram feitas em clones limpos.
5. Curadoria: na fila (`sdd/curadoria/fila/F30_QUALIDADE_CODIGO/20261124T135615Z`, 13 deltas e 2 candidatos, entre eles o "discover vazio sai 0 no Python 3.9", agora com `Do instead:`). A fila passou do limite (6 entradas, 2 da F30): rodar o lote da `sdd-playbook`.

## Definition of Done

- [x] S1 publicada: o Verify Gate sai 0 e a release foi feita com 1 OK
- [x] Starter regenerado depois da S1 (`v1.5.31`)
- [x] S2 publicada (`v2.27.1`): S2-b com o hash da árvore igual antes e depois; custo extra em tokens dos itens 2, 6 e 7 no BUILD_REPORT (+4,4%, n=1)
- [x] Starter regenerado depois da S2 (`v1.5.32`)
- [ ] S3 publicada: ferramenta ausente dá "não medido", nunca "0 achados"; métrica só avisa
- [ ] CI verde em cada release

## ⛔ Landmines desta feature

- **O Python 3.9 do sistema** (`/usr/bin/python3`) roda o `unittest discover` sem nenhum teste e sai 0. Por isso o gate tem `test -f` explícito de cada `tests/test_f30_*.py`. **Faça isto:** ao criar teste novo na S2/S3, acrescente o `test -f` no gate.
- **`sdd-build/web/MODO_WEB.md` tem 488 linhas** (teto 500, LM-038) e `sdd-build/SKILL.md` 370; `sdd-new-session/SKILL.md` 445. **Faça isto:** o texto novo da S2 vai para `references/`, com 1 linha de ponteiro na skill.
- **O repositório do Open não tem `sdd/config.yaml`**: a linha `lint: slot vazio` ausente é aviso, nunca violação (Decision 3).
- **Rodar a suíte inteira em paralelo com outra suíte inventa falha** (LM-031): pare o gate antigo antes de rodar outro.

## Eventos

- 2026-11-24 — S2: DEFINE 1.5 (AT-010 a AT-016) e DESIGN 2.0/2.1 (Decisions 8 a 14); revisão do DESIGN (openrouter/qwen, codex 2º revisor, auditor claude): 1 MED aplicado.
- 2026-11-24 — Build da S2: testes antes do código com `AT-nnn.antes.log`; 2 sabotagens declaradas pegas; 3 rodadas de revisão do código (2 LOW rebatidos por escopo); avaliador fresco em 2 ciclos (ciclo 1 NEEDS_WORK pelo cache da execução limpa no `sabotagem.sh`, aplicado); raio de impacto em 2 superfícies (1 risco latente consertado); custo dos passos novos medido (+2.514 tokens, +4,4%).
- 2026-11-24 — Release da S2 com o OK do Roberto ("pode finalizar"): push atômico `main` + tag `v2.27.0` em `5e89137` (avanço direto, sem PR).
- 2026-11-24 — O CI da `v2.27.0` caiu na fatia 15/16 do Windows: o teste do link simbólico do `sabotagem.sh` esperava 64, e no Windows o link chega à cópia como arquivo comum (a proteção vale). Teste corrigido (`a6f1f5e`) e, com o OK do Roberto, publicada a `v2.27.1`; a tag `v2.27.0` fica no remoto sem Release.
- 2026-11-24 — starter: 16ª geração pela tag `v2.27.0` num clone limpo (`c56580d`; check-gerado VERDE, check-versions e publish-check PASS, testes, gate da KB e 19 zips), PR #25 com CI verde, avanço direto da `main`, Release `v1.5.32` (19 zips OK no `shasum -c`).
- 2026-11-23 — DEFINE 1.0 a 1.4 e DESIGN 1.0 a 1.2 (revisão do DESIGN com openrouter/qwen revisor e claude auditor; gemini sem login).
- 2026-11-23 — Build da S1: 5 rodadas de revisão do código (9 achados, 8 corrigidos, 1 rebatido por escopo), avaliador fresco em 2 ciclos (o 1º pediu a emenda do AT-006, PHP sem `php -l`), raio de impacto em 3 superfícies.
- 2026-11-24 — Release da S1 com o OK do Roberto ("pode finalizar"): push atômico `main` + tag `v2.26.0` em `c4fa53c` (avanço direto, sem PR; a `main` não tinha andado desde `4aa0cce`). Release conferida: runs 45361178679 (tag) e 45361178619 (`main`) verdes, publicada às 09:52 UTC; `shasum -c` OK, `VERSION` = `v2.26.0`, 782 arquivos = 782 linhas do `MANIFEST`, 0 documentos no pacote.
- 2026-11-24 — starter: 15ª geração pela tag `v2.26.0` num clone limpo (`41abba7`; check-gerado VERDE, check-versions e publish-check PASS, testes, gate da KB e 19 zips), PR #24 de lá com CI verde, avanço direto da `main`, Release `v1.5.31` (19 zips OK no `shasum -c`); branch `gen/v2.26.0` apagada.

## Recomendações

- Na S3, o script de métricas só avisa: exit 0 sempre que rodou; ferramenta ausente vira a linha "não medido: <ferramenta> ausente" e o comando de instalar. Teste com fixture de complexidade 15 e um bloco duplicado, e outra sem `lizard`/`jscpd` no PATH (`path_restrito` de `tests/apoio.py`).
- Na S2, a sabotagem (S2-b) roda sobre `git archive HEAD` numa pasta temporária, nunca na árvore de trabalho; o teste compara o hash da árvore antes e depois (como o `Linter.arvore()` de `tests/test_f30_checar_linter.py`).
- Para medir o custo em tokens, registre no BUILD_REPORT os tokens de uma tarefa com e sem os passos novos, na mesma tarefa de exemplo.

---

## Prompt de retomada

```text
Retomar a feature F30_QUALIDADE_CODIGO do sdd-open, fatia S3 (métricas no diff, só aviso: itens 5, 8).

Contexto: a F30 faz o código gerado pelo método seguir Clean Code e TDD, em 3 fatias. S1 (lint e tipos no Build,
regras no AGENTS.md, linter sugerido) na v2.26.0; S2 (vermelho antes do verde no report-lint, sabotagem.sh,
passo Refatorar) na v2.27.1 (24/11); starter v1.5.32. Falta a S3.

Pasta: abrir uma frente nova com a sdd-new-session a partir de origin/main. Setup: git status limpo;
GIT_TERMINAL_PROMPT=0 git fetch origin main && git log --oneline HEAD..origin/main.

Leia primeiro: sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md; depois sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md
(seção "Fatia S3" e Clarification D5), sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md (§ Fatia S3, itens 5 e 8, e
S3-a, S3-b da tabela §6), sdd/features/DESIGN_F30_QUALIDADE_CODIGO.md e a seção "## Sempre" de sdd/playbook.md.

Pipeline: sdd-iterate (ATs da S3 em EARS, test -f de cada tests/test_f30_*.py novo no gate) → sdd-design com
revisão adversarial (openrouter/qwen revisor, claude auditor; chave em ~/.config/rdd-eval.env; saldo em /credits)
→ sdd-build (antes.log de cada AT novo na coluna Antes; sabotagem declarada no DESIGN pelo sabotagem.sh;
avaliador fresco; Verify Gate ~35 min só depois dos testes dirigidos) → sdd-release com 1 OK (minor, tag à mão,
push atômico main + tag) → starter num clone limpo (gerar-starter.py --tag) → PLANO e esta ficha.

Restrições: métrica só avisa (exit 0); ferramenta ausente = "não medido", nunca "0 achados"; nada instala sem o
sim (D2); texto novo de skill em frase positiva (F29); limites em qualidade.* do config (D5).

Landmines: sdd-build/SKILL.md 380 e web/MODO_WEB.md 489 de 500 linhas (LM-038): texto novo em references/;
arquivo novo no MANIFEST.txt (LM-037); sem sdd/bin/ em texto do starter (LM-035); versões fixas de skill em
testes antigos (grep a versão antes do gate); Python embutido em script .sh precisa da troca de saída UTF-8
(test_f16w2_saida); não rodar duas suítes em paralelo (LM-031). Pendências leves da S2 na ficha (O-A a O-E, R1, R2).
```

---

## Histórico de slices

### S2 — Disciplina de teste — 2026-11-24

- `report-lint.py`: coluna `Antes`; o DEFINE classifica o AT (1ª tabela; `shall continue to` pelo início da célula); antes vermelho do mesmo comando (fora de 0/126/127) no comportamento novo, verde na não-regressão; sem a coluna, aviso.
- `sdd/bin/sabotagem.sh`: cópia de `git archive HEAD`, cópia limpa conferida antes, cópia nova para a execução sabotada, trecho único, caminho contido; 0 pega · 2 não pega · 3 inconclusivo · 64 uso.
- Passo Refatorar (5) entre Verificar e Marcar, `build.refatorar: false` desliga; tabela de sabotagens no DESIGN; texto único `sdd-build/web/references/disciplina-de-teste.md`.
- Lição: o cache que uma execução deixa na cópia esconde a execução seguinte (o `__pycache__` no mesmo segundo do commit); cada execução comparada ganha a sua cópia.

### S1 — Qualidade por stack — 2026-11-23 a 2026-11-24

- Catálogo `CATALOGO_QUALIDADE.md` em `sdd-build/web/references/` (o starter o recebe sem mudar o gerador), lido por `sdd/bin/qualidade-regras.sh` (`--stack`, `--regras`, `--agents`).
- Bloco "Qualidade ao construir" no AGENTS.md (`init`/`sync`), com ponteiro e aviso quando o leitor falha.
- `report-lint.py` cobra `LINT.log`/`TIPOS.log` com o slot cheio; dívida antiga pelo log de antes do mesmo comando; exit 126/127 não conta como dívida.
- `checar.sh --linter` sugere o linter da stack; a `sdd-new-session` pergunta se grava o slot (D2), sem instalar nada.
- Lição: no Python 3.9 o discover vazio sai 0 — por isso o `test -f` no gate.
