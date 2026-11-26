# HANDOFF: F31 — Vermelho avaliado

> Ficha da feature — **1 arquivo por feature**.

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F31_VERMELHO_AVALIADO |
| **Objetivo** | O `report-lint.py` avisa quando o log de um AT não prova o AT: zero casos avaliados na linha dele, AT que já passava antes, ou comando compartilhado sem contagem por AT |
| **Status** | ✅ Publicada na `v2.29.0` (2026-11-25, `1fd9bb1`; Release conferida) |
| **Última sessão** | 2026-11-25 |
| **Branch / pasta** | publicado pelo commit único da branch `f31-publicar` (PR #47); trabalho em `f31-vermelho-avaliado` · `/Users/robertoduarte/rdd-worktrees/f31-vermelho-avaliado` (só local: tem um commit com números do caso de origem, não enviar) |
| **Artefatos** | arquivados em `sdd/archive/F31_VERMELHO_AVALIADO/` (ESCOPO, DEFINE, DESIGN, BUILD_REPORT) · `sdd/reviews/` (3 avaliações e o ledger da revisão) · `sdd/releases/F31_VERMELHO_AVALIADO/unica_v2.29.0.yaml` · `sdd/reports/evidence/F31_VERMELHO_AVALIADO/` |
| **Verify Gate** | 🟢 0 em `7954c9d` (2.994 testes, 7 pulados), integrado à `v2.28.1`; CI 18 de 18 no PR #47 e os 3 runs da publicação verdes |
| **Veredito da release** | 🟡 CONCERNS (avisos em "Falta") |

## Publicado

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-25 · unica · 2.29.0 · shipado · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.29.0 posta à mão no commit) · trilha completa · 1fd9bb1
<!-- publicado:fim -->

## Falta

1. ✨ **Bloquear pela contagem** (D2): só depois de 5 relatórios com a linha `AT-nnn … (PASS n · FAIL n)`, de 2 projetos ou mais, com 0 alarmes falsos. Contar os avisos `[casos avaliados]` e os falsos até lá.
2. ✨ **Coluna `Antes` obrigatória em relatório novo** (D4): falta um jeito seguro de saber o que é "novo"; 46 dos 51 relatórios não têm a coluna.
3. 🐛 **`AT-nnn.log` final em `[exit≠0]` é aceito como `true`** pelo `report-lint.py` (0 casos nos 287 logs finais do repositório).
4. 🐛 Limites do leitor aceitos (avaliador, ciclo 3): dois logs de mesmo nome na feature, só o 1º é lido (O2); mesmo comando com acento em encodings diferentes não forma grupo (O4); o aviso do antes exige o antes aceito (O5).
5. ⚠️ O `playbook-curator.sh` pode tomar por achado uma linha verde sem marca `AT-001 … (PASS 2 · FAIL 0)` colada num log de avaliação (ruído, com julgamento humano no lote).
6. ⚠️ As avaliações dos ciclos 2 e 3 foram gravadas em resumo (sondas nos logs `AVAL2-*`/`AVAL3-*`); `lizard` e `jscpd` não estavam instalados (qualidade não medida).
7. **LM-002:** a promoção `promovido_para=sdd/bin/report-lint.py` no projeto de origem entra quando ele atualizar a cópia do Open para a `v2.29.0` ou mais nova. O que a máquina confere é só aviso.
8. ✨ Starter: gerar a 18ª geração pela tag `v2.29.0` (muda `disciplina-de-teste.md`, `sdd-define` e `sdd-build`), com OK próprio.
9. Custo: revisões US$ 1,25 (4 rodadas, codex na assinatura); avaliador em 3 ciclos (o 3º autorizado pelo Roberto).

Curadoria: na fila (`sdd/curadoria/fila/F31_VERMELHO_AVALIADO/20261125T234556Z`, 9 deltas, 1 candidato).

## Eventos

- 2026-11-25 — Define: o caso reproduziu (antes `[exit=2]` com `PASS 0 · FAIL 0` aceito); D1 a D5 com a recomendada, pela autorização do Roberto; governança N.A. (revisor fresco).
- 2026-11-25 — Build: 41 testes antes do código; 3 sabotagens pegas; avaliador NEEDS_WORK no ciclo 1 (leitor: primeira contagem, AT repetido, aviso do final) e no ciclo 2 (7 testes com a versão fixa), PASS no 3º.
- 2026-11-25 — Release com o OK do Roberto ("sim, pode finalizar e publicar a v2.29.0"): a `main` andou para a `v2.28.1` no meio (integrada, gate repetido); commit único sem os números do caso de origem; PR #47 com CI 18/18; push atômico `main` + tag; Release conferida (`shasum -c`, `VERSION`, 793 = 793 do `MANIFEST`).

## Prompt de retomada

```text
F31 publicada na v2.29.0 (sdd-open). Leia sdd/handoffs/HANDOFF_F31_VERMELHO_AVALIADO.md, seção Falta.
Próximo passo possível: o starter pela tag v2.29.0 num clone limpo (item 8), com OK próprio; ou medir os avisos
[casos avaliados] em projetos reais antes de propor o bloqueio (item 1). Não enviar a branch local
f31-vermelho-avaliado: ela tem um commit com números do caso de origem.
```
