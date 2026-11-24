# HANDOFF: F30 — Qualidade do código gerado (Uncle Bob × Open)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Objetivo** | O código que o método gera segue Clean Code e TDD: lint e tipos a cada tarefa, regras de qualidade por stack, vermelho antes do verde, sabotagem do gate, refatorar depois do verde e métricas de forma no diff (só aviso) |
| **Status** | 🚢 S1 publicada na `v2.26.0` (2026-11-24, `main` = `c4fa53c`; Release conferida) e starter **`v1.5.31`**; S2 e S3 abertas |
| **Última sessão** | 2026-11-24 |
| **Branch / pasta** | `f30-sdd-open-uncle-bob` · `/Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob` (a `main` avançou direto para o HEAD da frente; a branch não existe no remoto) |
| **Artefatos** | `sdd/features/{AVALIACAO_F30_UNCLE_BOB,ESCOPO_F30_QUALIDADE_CODIGO,DEFINE_F30_QUALIDADE_CODIGO,DESIGN_F30_QUALIDADE_CODIGO}.md` · `sdd/reports/BUILD_REPORT_F30_QUALIDADE_CODIGO.md` · `sdd/reviews/{AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2035,AVALIACAO_F30_QUALIDADE_CODIGO_20261123-2050,LEDGER_REVISAO_F30_QUALIDADE_CODIGO}.md` · `sdd/releases/F30_QUALIDADE_CODIGO/s1_v2.26.0.yaml` · `sdd/reports/evidence/F30_QUALIDADE_CODIGO/` |
| **Verify Gate** | 🟢 0 em `76827bf` (2.819 testes, 4 pulados, 31 min) — `bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` |
| **Veredito da release S1** | 🟡 CONCERNS (4 avisos, em "Falta") |

## Publicado

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-23 · s1 · 2.26.0 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.26.0 posta à mão no commit, como as minor anteriores) · trilha completa · c4fa53c
<!-- publicado:fim -->

## Falta

1. ✨ **S2 — disciplina de teste (itens 2, 6, 7):** `sdd-iterate` no mesmo DEFINE (seção "Fatia S2"; proposta de AT no ESCOPO §6: S2-a vermelho antes do verde, S2-b sabotagem do gate numa cópia descartável com hash da árvore conferido, S2-c refatorar depois do verde). Medir no BUILD_REPORT o custo extra em tokens dos itens 2, 6 e 7. Segurança só no S2-b.
2. ✨ **S3 — métricas no diff, só aviso (itens 5, 8):** depois da S2. Ferramenta ausente = "não medido", nunca "0 achados".
3. ✨ O clone local `~/rdd-public/sdd-starter` está atrasado (11ª geração) e tem `docs/guia-do-aluno.pt-BR.md` fora do git; a 15ª geração foi feita num clone limpo. Atualize-o com `git -C ~/rdd-public/sdd-starter pull` quando decidir o que fazer com esse arquivo.
4. ⚠️ Avisos da release S1 (não abortaram):
   - nota de atualização: projeto com `lint_cmd`/`typecheck_cmd` cheio e BUILD_REPORT anterior à v2.26.0 passa a ser cobrado pelo `LINT.log`/`TIPOS.log` (o `report-lint` imprime o conserto);
   - 🐛 o `doctor` não avisa de arquivo novo de `sdd/bin/` ausente num projeto atualizado só com `sync` (anterior à F30);
   - ✨ o item 5 da `sdd-release` não cita o log de lint entre as causas de abortar (a tabela cobre; a skill está a 41 linhas do teto);
   - custo das revisões da S1: US$ 4,53 (6 rodadas).
5. Curadoria: na fila (`sdd/curadoria/fila/F30_QUALIDADE_CODIGO/20261124T090127Z`, 16 contagens e 7 sugestões). O candidato "discover vazio sai 0 no Python 3.9" foi rejeitado por não ter a linha `Do instead:`; reescrevê-lo no BUILD_REPORT da S2 se ainda valer. A fila está no limite (5 entradas): rodar o lote da `sdd-playbook`.

## Definition of Done

- [x] S1 publicada: o Verify Gate sai 0 e a release foi feita com 1 OK
- [x] Starter regenerado depois da S1 (`v1.5.31`)
- [ ] S2 publicada: S2-b com o hash da árvore igual antes e depois; custo extra em tokens dos itens 2, 6 e 7 no BUILD_REPORT
- [ ] S3 publicada: ferramenta ausente dá "não medido", nunca "0 achados"; métrica só avisa
- [ ] CI verde em cada release

## ⛔ Landmines desta feature

- **O Python 3.9 do sistema** (`/usr/bin/python3`) roda o `unittest discover` sem nenhum teste e sai 0. Por isso o gate tem `test -f` explícito de cada `tests/test_f30_*.py`. **Faça isto:** ao criar teste novo na S2/S3, acrescente o `test -f` no gate.
- **`sdd-build/web/MODO_WEB.md` tem 488 linhas** (teto 500, LM-038) e `sdd-build/SKILL.md` 370; `sdd-new-session/SKILL.md` 445. **Faça isto:** o texto novo da S2 vai para `references/`, com 1 linha de ponteiro na skill.
- **O repositório do Open não tem `sdd/config.yaml`**: a linha `lint: slot vazio` ausente é aviso, nunca violação (Decision 3).
- **Rodar a suíte inteira em paralelo com outra suíte inventa falha** (LM-031): pare o gate antigo antes de rodar outro.

## Eventos

- 2026-11-23 — DEFINE 1.0 a 1.4 e DESIGN 1.0 a 1.2 (revisão do DESIGN com openrouter/qwen revisor e claude auditor; gemini sem login).
- 2026-11-23 — Build da S1: 5 rodadas de revisão do código (9 achados, 8 corrigidos, 1 rebatido por escopo), avaliador fresco em 2 ciclos (o 1º pediu a emenda do AT-006, PHP sem `php -l`), raio de impacto em 3 superfícies.
- 2026-11-24 — Release da S1 com o OK do Roberto ("pode finalizar"): push atômico `main` + tag `v2.26.0` em `c4fa53c` (avanço direto, sem PR; a `main` não tinha andado desde `4aa0cce`). Release conferida: runs 45361178679 (tag) e 45361178619 (`main`) verdes, publicada às 09:52 UTC; `shasum -c` OK, `VERSION` = `v2.26.0`, 782 arquivos = 782 linhas do `MANIFEST`, 0 documentos no pacote.
- 2026-11-24 — starter: 15ª geração pela tag `v2.26.0` num clone limpo (`41abba7`; check-gerado VERDE, check-versions e publish-check PASS, testes, gate da KB e 19 zips), PR #24 de lá com CI verde, avanço direto da `main`, Release `v1.5.31` (19 zips OK no `shasum -c`); branch `gen/v2.26.0` apagada.

## Recomendações

- Na S2, a sabotagem (S2-b) roda sobre `git archive HEAD` numa pasta temporária, nunca na árvore de trabalho; o teste compara o hash da árvore antes e depois (como o `Linter.arvore()` de `tests/test_f30_checar_linter.py`).
- Para medir o custo em tokens, registre no BUILD_REPORT os tokens de uma tarefa com e sem os passos novos, na mesma tarefa de exemplo.

---

## Prompt de retomada

```text
Retomar a feature F30_QUALIDADE_CODIGO do sdd-open (frente f30-sdd-open-uncle-bob), fatia S2.

Contexto: a F30 faz o código gerado pelo método seguir Clean Code e TDD (itens 1–8 de
sdd/features/AVALIACAO_F30_UNCLE_BOB.md), em 3 fatias. A S1 (lint e tipos no Build, regras de qualidade no
AGENTS.md, linter sugerido) está publicada na v2.26.0 (main = c4fa53c, 2026-11-24). Falta a S2 (itens 2, 6, 7:
vermelho antes do verde, sabotagem do gate, refatorar depois do verde) e a S3 (itens 5, 8: métricas no diff, só aviso).

Pasta: /Users/robertoduarte/rdd-worktrees/f30-sdd-open-uncle-bob · branch f30-sdd-open-uncle-bob.
Setup: git status limpo; GIT_TERMINAL_PROMPT=0 git fetch origin main && git log --oneline HEAD..origin/main
(se listar commits, git rebase origin/main).
Leia primeiro: sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md, depois sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md
(seções "Fatia S2" e Clarifications: D3, D4, D7) e sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md §6 (S2-a, S2-b, S2-c).
Leia "## Sempre" de sdd/playbook.md.

Próxima ação: sdd-iterate no DEFINE para escrever os ATs da S2 em EARS e estender o Verify Gate (test -f de cada
tests/test_f30_*.py novo); depois sdd-design (S2), sdd-build, sdd-release com 1 OK, geração do starter num clone
limpo do sdd-starter (scripts/gerar-starter.py --tag <tag>; starter atual v1.5.31), a linha da F30 em sdd/features/PLANO_F4_F15_CONSOLIDADO.md e esta ficha.

Restrições: só bloqueia o objetivo (teste e erro de lint/tipos com slot cheio); métrica só avisa; nada instala no
projeto do aluno sem o sim (D2); texto novo de skill em frase positiva, sem banner e sem "não cite" (F29); a
sabotagem roda numa cópia descartável e a árvore de trabalho fica idêntica (hash conferido no teste); medir e
registrar no BUILD_REPORT o custo extra em tokens dos itens 2, 6 e 7; segurança só no S2-b.

Landmines: MODO_WEB.md 488/500 linhas (LM-038); arquivo novo no MANIFEST.txt (LM-037); pergunta [D2] nova sobe a
contagem do test_decisoes_lint (hoje 41 em 31 arquivos, LM-044); o /usr/bin/python3 3.9 roda discover vazio com
exit 0; não rodar duas suítes em paralelo (LM-031); dado medido no repositório privado não vai para documento do Open.
```

---

## Histórico de slices

### S1 — Qualidade por stack — 2026-11-23 a 2026-11-24

- Catálogo `CATALOGO_QUALIDADE.md` em `sdd-build/web/references/` (o starter o recebe sem mudar o gerador), lido por `sdd/bin/qualidade-regras.sh` (`--stack`, `--regras`, `--agents`).
- Bloco "Qualidade ao construir" no AGENTS.md (`init`/`sync`), com ponteiro e aviso quando o leitor falha.
- `report-lint.py` cobra `LINT.log`/`TIPOS.log` com o slot cheio; dívida antiga pelo log de antes do mesmo comando; exit 126/127 não conta como dívida.
- `checar.sh --linter` sugere o linter da stack; a `sdd-new-session` pergunta se grava o slot (D2), sem instalar nada.
- Lição: no Python 3.9 o discover vazio sai 0 — por isso o `test -f` no gate.
