# HANDOFF: F30 — Qualidade do código gerado (Uncle Bob × Open)

> Ficha da feature — **1 arquivo por feature**, slices como subseções (mais recente no topo).

## Ficha

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Objetivo** | O código que o método gera segue Clean Code e TDD: lint e tipos a cada tarefa, regras de qualidade por stack, vermelho antes do verde, sabotagem do gate, refatorar depois do verde e métricas de forma no diff (só aviso) |
| **Status** | ✅ As 3 fatias publicadas: S3 na `v2.28.0` (2026-11-25, `33b5831`; Release conferida; o `publish-gate` da `main` caiu em `33b5831` e passou em `30b2904` e `e47c2ec`, ver Falta) e starter **`v1.5.33`**; S2 na `v2.27.3` (as tags `v2.27.0` a `v2.27.2` ficaram sem Release) e correções do `sdd-drive` na `v2.27.4` e na **`v2.28.1`** (2026-11-25, `699573e`; Release conferida); S1 na `v2.26.0` |
| **Última sessão** | 2026-11-25 |
| **Branch / pasta** | S3: `s3-open-sdd-unclebob` · `/Users/robertoduarte/rdd-worktrees/s3-open-sdd-unclebob` (PR #45 para o CI antes da tag; a `main` avançou direto). S2: `s2-sdd-open-uncle-bob` · `/Users/robertoduarte/rdd-worktrees/s2-sdd-open-uncle-bob` (PR #43 para o CI antes da tag; a `main` avançou direto para o HEAD da frente); correção do `sdd-drive`: `fix-sdd-drive-temporario`, na mesma pasta (PR #44). S1: `f30-sdd-open-uncle-bob` |
| **Artefatos** | arquivados em `sdd/archive/F30_QUALIDADE_CODIGO/` (DEFINE, DESIGN, ESCOPO e BUILD_REPORT) · `sdd/features/AVALIACAO_F30_UNCLE_BOB.md` · `sdd/reviews/` (5 avaliações `AVALIACAO_F30_QUALIDADE_CODIGO_*` e `LEDGER_REVISAO_F30_QUALIDADE_CODIGO.md`) · `sdd/releases/F30_QUALIDADE_CODIGO/` (um ledger por tag) · `sdd/reports/evidence/F30_QUALIDADE_CODIGO/` |
| **Verify Gate** | 🟢 S3: 0 em `cd70bed`, o código da `v2.28.0` (2.947 testes, 7 pulados); 🟢 S2: 0 em `2864d26`, o código da `v2.27.3` (2.880 testes, 4 pulados), e 0 em `2b015b4`, o código da `v2.27.4` (2.888 testes, 5 pulados); S1: 0 em `76827bf` — `bash sdd/bin/verify-gate.sh sdd/archive/F30_QUALIDADE_CODIGO/DEFINE_F30_QUALIDADE_CODIGO.md` |
| **Veredito das releases** | 🟡 S3 CONCERNS (6 avisos, no ledger) · 🟡 `v2.27.4` CONCERNS (5 avisos, no ledger) · 🟡 S2 CONCERNS (6 avisos) · 🟡 S1 CONCERNS (4 avisos), em "Falta" |

## Publicado

<!-- publicado:inicio (gerado por sdd/bin/ficha-publicado.py a partir de sdd/releases/; não edite à mão) -->
- 2026-11-25 · s3 · 2.28.1 · shipado · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.28.1 posta à mão no commit) · trilha completa · 699573e
- 2026-11-25 · s3 · 2.28.0 · shipado · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.28.0 posta à mão no commit) · trilha completa · 33b5831
- 2026-11-24 · s2 · 2.27.4 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.27.4 posta à mão no commit) · trilha completa · 7ab8a72
- 2026-11-24 · s2 · 2.27.3 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.27.3 posta à mão no commit; as tags v2.27.0, v2.27.1 e v2.27.2 ficaram sem Release, com o CI vermelho) · trilha completa · 682fc60
- 2026-11-24 · s2 · 2.27.2 · parcial · CONCERNS · deploy SEM RELEASE (o CI da tag caiu, teste do ln -s e teto de 30 min no Windows); release automática pelo workflow release.yml (tag v2.27.2 posta à mão no commit; as tags v2.27.0 e v2.27.1 ficaram sem Release, com o CI vermelho) · trilha completa · fb5c1c9
- 2026-11-24 · s2 · 2.27.1 · parcial · CONCERNS · deploy SEM RELEASE (o CI da tag caiu, maintenance.lock do git no macOS); release automática pelo workflow release.yml (tag v2.27.1 posta à mão no commit a6f1f5e; a v2.27.0 ficou sem Release: o CI caiu na fatia 15/16 do Windows por um teste do link simbólico, corrigido) · trilha completa · d72f53f
- 2026-11-24 · s2 · 2.27.0 · parcial · CONCERNS · deploy SEM RELEASE (o CI da tag caiu, teste do link simbólico no Windows); release automática pelo workflow release.yml (tag v2.27.0 posta à mão no commit, como as minor anteriores) · trilha completa · 5e89137
- 2026-11-23 · s1 · 2.26.0 · parcial · CONCERNS · deploy release automática pelo workflow release.yml (tag v2.26.0 posta à mão no commit, como as minor anteriores) · trilha completa · c4fa53c
<!-- publicado:fim -->

## Falta

1. 🐛 **Testes de tempo no Windows, intermitentes (a causa está em aberto).** Na publicação da `v2.28.1` (`699573e`) o run da tag passou e publicou, mas:
   - `release` da `main` (45693022443), fatia 9: o `git add -A` do `setUp` passou de 120 s (`test_doctor_com_pacote_sem_checar_avisa_e_sai_0`); o teste seguinte também travou, 113,6 s num `sdd-open.sh` (vizinhos: 22 a 26 s). Já tinha caído igual em `33b5831` (45634528055, fatia 7). Normal medido: 4 a 10 s em máquina folgada, até 28,8 s na suíte. Indício de máquina parada por minutos, ainda sem causa; o limite segue em 120 s. `tests/apoio.py` anota todo comando acima de 10 s (`⏱`) no log da unidade: use-o para medir;
   - `publish-gate` da `main` (45693022449), fatia 6: `test_checar.TestRemoto.test_rede_pendurada`, 21,7 s contra limite de 14 s.
   - ✅ a queda do `sdd-drive` (fatia 2 de 45634528055) tem causa provada e conserto na `v2.28.1` (item 5).
   - ⚠️ Avisos da release S3: estão no ledger `s3_v2.28.0.yaml` (nota de atualização, avaliador antes dos consertos, unidades diferentes no Windows só com teste de texto, ferramentas falsas no CI).
   - 🐛 pendências leves da S3: `jscpd` sem o campo `tokens` sai "0 tokens" (LOW da rodada 20); nome de arquivo com aspas derruba a complexidade (dito como não medido); causa imprecisa quando o `lizard` sai vazio; seção só com `---` conta como preenchida; a `sdd-release` não cita a falta da seção entre as causas de abortar; com `.vue`, não dá para saber quais arquivos o `jscpd` leu.
2. ⚠️ Avisos da release S2 (não abortaram):
   - nota de atualização: relatório novo nasce com a coluna `Antes` e o `report-lint` cobra o `AT-nnn.antes.log` de cada AT de gate `test`/`cmd`; relatório antigo só recebe aviso;
   - 🐛 observações leves do avaliador (ciclo 2) no `report-lint.py`: O-A citação com `..` passa no `problema_do_log` (anterior à S2; vale também para a coluna Evidência — normalizar o caminho); O-B cabeçalho `**Antes**` ou `Antes/vermelho` não é reconhecido; O-C sem `AT-nnn.log` no disco o comando do antes não é comparado; O-D `N.A.` sem motivo aceito em `manual-ux`; O-E antes que é link simbólico para fora da feature é aceito;
   - 🐛 1 LOW da rodada 3 no `sabotagem.sh`: sem `lib/python.sh`, a falta de Python sai 3 sem a mensagem própria (o `pipefail` foi aplicado em `79f64c5`);
   - ✨ `upgrade` e `sync` não mesclam chaves do config: projeto já instalado fica sem a seção `build:` (ausente = Refatorar ligado);
   - ✨ exigir por máquina a sabotagem (`≥ 1 por feature`) no `report-lint` ficou fora da S2 (Fora da S2 do DEFINE);
   - custo das revisões da S2: US$ 11,86 (10 rodadas, com a do DESIGN), fora uma revisão interrompida sem custo medido; mais US$ 0,11 na `v2.27.4`;
   - o avaliador fresco julgou `e65531f`, antes dos consertos das rodadas 6 e 7.
3. ⚠️ Avisos da release S1 que seguem: o `doctor` não avisa de arquivo novo de `sdd/bin/` ausente num projeto atualizado só com `sync`; o item 5 da `sdd-release` não cita o log de lint entre as causas de abortar.
4. ✨ O clone local `~/rdd-public/sdd-starter` está atrasado (11ª geração) e tem `docs/guia-do-aluno.pt-BR.md` fora do git; as gerações 15ª a 17ª foram feitas em clones limpos.
5. ✅ **`sdd-drive.sh`, falha intermitente: consertada na `v2.28.1`.** No Windows, quem larga a trava a apaga, e abri-la naquele instante dá errno 13; o verbo saía 2. Agora espera até 5 s. Prova em 6 máquinas Windows: 47 de 48 vermelhas sem o conserto, 0 de 48 com ele. Que foi isso no run 45634528055 é inferência: a saída daquele run foi descartada.
6. ✨ A divisão das fatias do Windows é por número de testes, não por tempo: a fatia 4 levou 30 min no PR (teto 45). Dividir por tempo medido.
7. Curadoria: o lote de 2026-11-25 foi enviado na `v2.28.1` (7 entradas, 103 contagens, 16 lições, LM-045 a LM-060). Fila nova: 1 entrada da F30 (0 deltas). A pasta `~/rdd-worktrees/lote-curadoria-20261125` e a branch local já podem ser apagadas (perguntar ao Roberto).
8. ⚠️ Avisos da `v2.28.1` (ledger `s3_v2.28.1.yaml`): codex raso na rodada 21 e sem 2º revisor na 22; a revisão adversarial deixa de ler `sdd/curadoria/` (decisão do Roberto); o CI não rodou sobre os commits de papel antes da tag.

## Definition of Done

- [x] S1 publicada: o Verify Gate sai 0 e a release foi feita com 1 OK
- [x] Starter regenerado depois da S1 (`v1.5.31`)
- [x] S2 publicada (`v2.27.3`): S2-b com o hash da árvore igual antes e depois; custo extra em tokens dos itens 2, 6 e 7 no BUILD_REPORT (+4,4%, n=1)
- [x] Starter regenerado depois da S2 (`v1.5.32`)
- [x] S3 publicada (`v2.28.0`): ferramenta ausente dá "não medido", nunca "0 achados"; métrica só avisa
- [x] Starter regenerado depois da S3 (`v1.5.33`)
- [ ] CI verde em cada release (na S3, os 2 runs `release` verdes e o `publish-gate` da `main` vermelho, item 1 de Falta; S1 e S2: verde no run da tag; na S2, o run da `main` em `682fc60` caiu na fatia 5, corrigido na `v2.27.4`, com os 3 runs verdes em `7ab8a72`)

## ⛔ Landmines desta feature

- **O Python 3.9 do sistema** (`/usr/bin/python3`) roda o `unittest discover` sem nenhum teste e sai 0. Por isso o gate tem `test -f` explícito de cada `tests/test_f30_*.py`. **Faça isto:** ao criar teste novo na S2/S3, acrescente o `test -f` no gate.
- **`sdd-build/web/MODO_WEB.md` tem 488 linhas** (teto 500, LM-038) e `sdd-build/SKILL.md` 370; `sdd-new-session/SKILL.md` 445. **Faça isto:** o texto novo da S2 vai para `references/`, com 1 linha de ponteiro na skill.
- **O repositório do Open não tem `sdd/config.yaml`**: a linha `lint: slot vazio` ausente é aviso, nunca violação (Decision 3).
- **Rodar a suíte inteira em paralelo com outra suíte inventa falha** (LM-031): pare o gate antigo antes de rodar outro.

## Eventos

- 2026-11-25 — `v2.28.1` (correção do `sdd-drive` e lote da curadoria), com o OK do Roberto ("sim, publica a v2.28.1"): causa medida numa branch de diagnóstico do Windows (já apagada), CI 18/18 no PR #46 e Verify Gate 0 em `8f79b76` (2.953 testes, 7 pulados), push atômico `main` + tag em `699573e`. Release conferida: run `release` da tag 45693021629 verde, publicada às 21:13 UTC; `shasum -c` OK, `VERSION` = `v2.28.1`, 792 = 792 no `MANIFEST`, 2 scripts iguais aos da tag. Os runs da `main` (45693022443 e 45693022449) caíram em 1 fatia cada (Falta, item 1), fora do `sdd-drive`.
- 2026-11-25 — starter: a geração de teste pela `v2.28.1` num clone limpo só muda a linha da tag no `GERADO.txt`; a `v1.5.33` segue valendo, sem geração nova.
- 2026-11-25 — `publish-gate` do commit de papel `30b2904` (45659227692): verde, 18 de 18 jobs. O do `e47c2ec` (45668336879), a ponta da `main`, também: 18 de 18. O mesmo código caiu em `33b5831` e passou nos dois: falha intermitente, em conserto na branch `fix-sdd-drive-recibos`.
- 2026-11-25 — Lote da curadoria julgado (7 entradas, blocos válidos, fronteira limpa); envio adiado pelo Roberto. Faxina com o OK dele: branches remotas `s3-open-sdd-unclebob` (`cd70bed`) e `gen/v2.28.0` do starter (`f455e1b`) apagadas, as duas já na `main`; o PR #26 do starter ficou CLOSED, não MERGED.
- 2026-11-25 — Release da S3 com o OK do Roberto ("sim, publica a v2.28.0"): CI inteiro verde no PR #45 (18/18, `cd70bed`), `--conferir` repetido (CONFERE), push atômico `main` + tag em `33b5831`. Release conferida: runs `release` 45634526448 (tag) e 45634528110 (`main`) verdes, publicada às 15:21 UTC pelo run da `main`; `shasum -c` OK, `VERSION` = `v2.28.0`, 792 arquivos = 792 linhas do `MANIFEST`, nenhum faltando, `metricas-diff.sh` igual ao da tag. O `publish-gate` 45634528055 caiu (item 1 de Falta) e o Roberto mandou seguir.
- 2026-11-25 — starter: 17ª geração pela tag `v2.28.0` num clone limpo (`f455e1b`; check-gerado VERDE, check-versions e publish-check PASS, testes, gate da KB e 19 zips), PR #26 de lá com CI verde, avanço direto da `main`. O Auto Release (45650576956) caiu no envio dos arquivos durante um incidente do GitHub (rascunho com 9 arquivos, sem tag); com o OK do Roberto, tag `v1.5.33` posta à mão depois do incidente: run 45658965189 verde, rascunho reaproveitado, 19 zips OK no `shasum -c` e iguais ao commit.
- 2026-11-24 — S2: DEFINE 1.5 (AT-010 a AT-016) e DESIGN 2.0/2.1 (Decisions 8 a 14); revisão do DESIGN (openrouter/qwen, codex 2º revisor, auditor claude): 1 MED aplicado.
- 2026-11-24 — Build da S2: testes antes do código com `AT-nnn.antes.log`; 2 sabotagens declaradas pegas; 3 rodadas de revisão do código (2 LOW rebatidos por escopo); avaliador fresco em 2 ciclos (ciclo 1 NEEDS_WORK pelo cache da execução limpa no `sabotagem.sh`, aplicado); raio de impacto em 2 superfícies (1 risco latente consertado); custo dos passos novos medido (+2.514 tokens, +4,4%).
- 2026-11-24 — Release da S2 com o OK do Roberto ("pode finalizar"): push atômico `main` + tag `v2.27.0` em `5e89137` (avanço direto, sem PR).
- 2026-11-24 — O CI da `v2.27.0` caiu na fatia 15/16 do Windows: o teste do link simbólico do `sabotagem.sh` esperava 64, e no Windows o link chega à cópia como arquivo comum (a proteção vale). Teste corrigido (`a6f1f5e`) e, com o OK do Roberto, publicada a `v2.27.1`; a tag `v2.27.0` fica no remoto sem Release.
- 2026-11-24 — A `v2.27.1` também ficou sem Release: no macOS, o hash da árvore do teste leu o `maintenance.lock` do git, que sumiu (`a242a71` desliga a manutenção na fixture). Ela subiu sem repetir o `--conferir` (NÃO CONFERE), e a ficha a deu por publicada antes da Release.
- 2026-11-24 — A `v2.27.2` ficou sem Release: o `ln -s` do teste não criou link no Git Bash, a fatia 4 do Windows bateu no teto de 30 min e o `test_f25_skills_duplicadas` caiu no macOS de um dos 2 runs (causa inferida: manutenção automática do git).
- 2026-11-24 — `v2.27.3`, com o OK do Roberto ("confere o gate e o CI e publica a v2.27.3"): CI inteiro verde no PR #43 (18/18, `2864d26`), rodada 9 sem achados, push atômico `main` + tag em `682fc60`. O 1º run do PR caiu por `tests/test_apoio_git.py` fora do `MANIFEST` (LM-037). Release conferida: run 45476586630 verde, publicada às 21:04 UTC, `shasum -c` OK, `VERSION` = `v2.27.3`, nenhum arquivo do `MANIFEST` faltando.
- 2026-11-24 — starter: a geração de teste pela `v2.27.3` num clone limpo só muda a linha da tag no `GERADO.txt`; a `v1.5.32` segue valendo, sem geração nova.
- 2026-11-24 — `v2.27.4` (correção do `sdd-drive`), com o OK do Roberto ("confere o gate e o CI e publica a v2.27.4"): CI inteiro verde no PR #44 (`2b015b4`), 8 testes novos (5 vermelhos antes do conserto; os 8 sem pulos no Windows), push atômico `main` + tag em `7ab8a72`. Release conferida: runs 45497174125 (tag), 45497174232 e 45497174431 (`main`) verdes; publicada às 22:57 UTC; `shasum -c` OK, `VERSION` = `v2.27.4`, 788 arquivos = 788 linhas do `MANIFEST`, `sdd-drive.sh` igual ao da tag; o run da `main` não criou outra versão.
- 2026-11-24 — starter: a geração de teste pela `v2.27.4` num clone limpo só muda a linha da tag no `GERADO.txt`; a `v1.5.32` segue valendo, sem geração nova.
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
Investigar os 2 testes de tempo do Windows que caem às vezes (sdd-open), pendência da F30. Contexto: Open v2.28.1 e starter
v1.5.33 publicados; o sdd-drive está consertado. O publish-gate e o release da main caíram em 699573e, 1 teste em cada um.

Leia primeiro: sdd/handoffs/HANDOFF_F30_QUALIDADE_CODIGO.md (Falta, item 1) e a seção "## Sempre" de sdd/playbook.md. Pasta:
frente nova pela sdd-new-session a partir de origin/main, em ~/rdd-worktrees. Setup: git status limpo; GIT_TERMINAL_PROMPT=0
git fetch origin main && git log --oneline HEAD..origin/main.

1. Evidência: gh run download 45693022443 -n testes-windows-fatia-9 e gh run download 45693022449 -n testes-windows-fatia-6
   (os artefatos duram 14 dias); compare com 45634528055, fatia 7.
2. git add -A do Projeto.setUp (tests/test_sdd_open.py): passou de 120 s 2 vezes, e o comando seguinte, que não é do git,
   também travou. Ache o que para a máquina (antivírus, disco, rajada) antes de mexer em limite; as linhas ⏱ do log medem.
3. test_checar.TestRemoto.test_rede_pendurada: 21,7 s contra 14 s. Meça a partida do script e o teto real da rede em separado.

Restrições: nunca --force; nunca mover tag publicada; nunca gh run rerun de run antigo; não rodar duas suítes em paralelo
(LM-031); não subir limite sem medida. Falar em português, para leigo, com recomendação.
```

---

## Histórico de slices

### S3 — Métricas no diff, só aviso — 2026-11-25

- `sdd/bin/metricas-diff.sh`: `lizard` e `jscpd` numa cópia temporária, só o que a frente trouxe; exit 0 sempre que mediu, 64 uso; ferramenta ausente ou com saída estranha é "não medido", com a causa e o comando de instalar.
- `report-lint.py` exige `## Qualidade (avisos)` quando o config tem `qualidade:`; o conteúdo nunca reprova. `sdd-build` 2.17.0, referência `metricas-do-diff.md`.
- `pre-commit`: `LC_ALL=C grep -F` para não perder linhas do lint no Git Bash.
- Lições: só `--min-lines 0` faz o `jscpd` pegar trecho de 1 linha (medido; antes eu tinha afirmado `1` sem medir); um commit verde na tag pode cair no `publish-gate` por teste intermitente.

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
