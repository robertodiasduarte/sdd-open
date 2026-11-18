# BUILD REPORT: F16W — Windows, porte da suíte

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W_WINDOWS |
| **Date** | 2026-11-14 |
| **Author** | build-agent (worktree `sdd-open-f16w-windows`, branch `feat/f16w-windows`, de `97503a7` = `v2.15.0`) |
| **DEFINE** | [DEFINE_F16W_WINDOWS.md](../features/DEFINE_F16W_WINDOWS.md) v1.4 |
| **DESIGN** | [DESIGN_F16W_WINDOWS.md](../features/DESIGN_F16W_WINDOWS.md) v1.3 |
| **Status** | Complete — CONCERNS (Windows medido no PR #30; AT-004 e AT-005 abertos por decisão do Roberto) |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 13/14 linhas do manifest do DESIGN v1.3 (a 10, consertos acusados pela medição, vira a próxima frente por decisão do Roberto) |
| **Files Created** | 3 no pacote: `scripts/testes-por-modulo.py`, `tests/test_testes_por_modulo.py`, `tests/test_f16w_passo0.py` |
| **Commits** | passo 0: `0475445` · build: `614bb3d` (executor, fatias, vigia), `ce3a779` (unidade = classe, UTF-8, bash pelo caminho) · revisão, rodada 1: `9e2ad33` · avaliador, ciclo 1: `c65e658` · raio de impacto e avaliador, ciclo 2: `c9cde6e` · revisão, rodada 2: `e6c845a` · rodada 3: `103697e` · LM-012: `4e76b39` · teste de tempo: `491efa6` · piso e log sem CR: `ad32fe1` |
| **Tests Passing** | exit 0 em `491efa6`: 2.175 testes em 34 min, 1 pulado (`evidence/F16W_WINDOWS/VERIFY-GATE-491efa6.log`); partida: 2.151 em `97503a7` |
| **Skills** | `sdd-checar-ambiente` 1.5.2, `sdd-iniciar-repo` 1.2.1 (o vigia); `check-versions.py --base v2.15.0` VERDE, 22 skills |

**Seleção de modo:** default (um autor; executor, workflows e vigia acoplados pelos testes), com o pedido do Roberto de executar o pipeline inteiro.

**Passo 0:** curadoria da F17c (LM-027 e LM-028; as 12 contagens e as 2 sugestões ficaram de fora, decisões do Roberto);
série 6 do teste do iniciante do build web **3 de 3** por leitor novo (`INICIANTE-s6-leitura.md`, US$ 1,34); as 2 pendências
da F17b não entram (decisão do Roberto).

**Medição do Windows:** o Roberto decidiu **medir só no PR do fim** (sem push intermediário). O Build fez o que se acha e
se prova no Mac; o CI do PR traz a 1ª medição inteira, unidade a unidade, e com ela vem a pergunta do piso.

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 14 linhas de manifest; executor, workflows e testes de texto se referem uns aos outros |
| Recomendação | default |
| Decisão do usuário | default, 2026-11-14 (pedido do Roberto: pipeline inteiro, só as decisões dele) |

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | gate de fiação | ✔ tratado: o executor roda de verdade sobre uma pasta de testes falsa (verde, falha, pulo, import quebrado, neto pendurado); 6 sabotagens mortas |
| LM-002 | baseline vermelho | ✔ tratado: a guarda de UTF-8 reprova a árvore `ce3a779~1`; os testes do executor não existiam antes; o teste do workflow novo reprova o job antigo |
| LM-003 | commit antes de revisar | ✔ tratado: revisão sobre árvore commitada |
| LM-005 | heurística nova | ✔ tratado: o "rc ≠ 0 depois de 10 s vira corte" só vale com `/proc/$$/winpid` (Git Bash); fora dele, o rc de sempre |
| LM-006 | gate sem `.git` | ✔ tratado: o executor não usa git; a guarda lê o `MANIFEST.txt`, não o `git ls-files` |
| LM-009 | sabotagem que desfaz conserto | ✔ tratado: mutantes em cópia de `git archive` |
| LM-012 | 11 dígitos no pacote | ✔ tratado: nenhum id de run citado em arquivo do pacote |
| LM-013 | edição por corte | ✔ tratado: trocas exatas; contagem de `def test_` antes e depois em `test_checar` (85 → 85) e `test_slot` (25 → 25) |
| LM-014, LM-015 | decodificação no Windows | ✔ tratado: é parte do conserto (Decision 6) |
| LM-016 | vigia por grupo no Windows | ✔ tratado no código (Decision 4); a prova é o CI do PR |
| LM-017 | fallback silencioso | ✔ tratado: o ramo do `kill` vale fora do Windows; o teste dos 5 casos no Windows só passa em ≤ 12 s se o `taskkill` rodou |
| LM-018 | `PIPESTATUS` no zsh | ✔ tratado: logs por `scripts/evlog.sh` (bash, `rc=$?`) |
| LM-027 | `claude -p` não simula a web | ✔ tratado: série 6 pela API de chat da OpenRouter |
| LM-028 | juiz por regex | ✔ tratado: veredito da série 6 por leitor novo |

---

## Candidatos ao playbook

### Candidato 1

sup: `CreateProcess` `System32` `bash` `WSL` `subprocess`
regra: No Windows, `subprocess.run(["bash", …])` sem caminho procura o programa em `System32` **antes** do `PATH` (ordem do `CreateProcess`): com o WSL instalado, cai no `bash.exe` dele, não no do Git Bash do aluno; na F16W, o `sdd-fluxo.sh` fazia isso e o `sdd-drive.sh` não (passava o caminho por variável). **Do instead:** o Python chamado por um script bash recebe o caminho do bash que o roda (`SDD_<SCRIPT>_BASH="${BASH:-bash}"`) e chama por ele; nos testes, a constante `BASH` de `tests/apoio.py`.
evidencia: sdd/reports/evidence/F16W_WINDOWS/SABOTAGEM.log

### Candidato 2

sup: `PYTHONIOENCODING` `executor` `mascara` `ambiente do aluno` `Windows`
regra: Um executor de testes que põe `PYTHONIOENCODING=utf-8` no ambiente de cada teste para ler a saída sem erro faz verde, no Windows, o teste que chama um script que quebra no cp1252 do Git Bash do aluno: na F16W, o raio de impacto achou isso antes da 1ª medição (o `handoff-lint.py` imprime ✅ sem reconfigurar a saída). **Do instead:** quem roda os testes lê a saída deles em bytes, decodifica em UTF-8 com `errors="replace"` e entrega ao teste o ambiente do aluno, sem a variável (como o `Sandbox` de `tests/apoio.py`).
evidencia: sdd/reports/evidence/F16W_WINDOWS/RAIO-DE-IMPACTO.md

### Candidato 3

sup: `paralelo` `carga` `teste de tempo` `flaky` `teto`
regra: Rodar módulos de teste ao mesmo tempo para ganhar tempo derruba testes que medem tempo: na F16W, com 6 módulos juntos no Mac, 2 testes do `test_deploy_do_sha` caíram (um diferente em cada rodada) e passaram sozinhos, e o `test_sdd_open` passou de 900 s. **Do instead:** suíte com teste de teto ou de espera roda em série; paralelismo só entre máquinas (fatias em jobs separados), e um vermelho visto só com carga se confere rodando o módulo sozinho antes de virar conserto.
evidencia: sdd/reports/evidence/F16W_WINDOWS/MAC-BASE-resumo.tsv

---

## Files Created

| Arquivo | Para quê |
|---|---|
| `scripts/testes-por-modulo.py` | executor por unidade (classe de teste), fatias, teto que mata a árvore (AT-001, AT-002) |
| `tests/test_testes_por_modulo.py` | AT-001, AT-002 |
| `tests/test_f16w_passo0.py` | a curadoria do passo 0 |

Mudados: os 2 workflows (job `testes-windows` em 16 fatias), `checar.sh` e `inventario.sh` (o vigia), `test_checar.py` (5
pulos `SEM_SINAL` fora), `test_release_workflow.py`, `test_windows.py` (guarda de UTF-8), `test_slot.py`, 13 arquivos de produto
e 6 testes com UTF-8 (Decision 6), `sdd-fluxo.sh` (bash pelo caminho), os 2 guards do Claude Code (payload e saída em UTF-8/ASCII, conversa UTF-8 com o lint, o bash do Git), `test_claude_adapter.py`.

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh --strict sdd/features/DEFINE_F16W_WINDOWS.md`) | exit 0 em `491efa6`: 2.175 testes, 1 pulado; publish-gate GREEN na cópia de `git archive` (`VERIFY-GATE-491efa6.log`). Antes: `ce3a779` parou na governança e depois caiu num teste de tempo com carga; `103697e` barrado pela LM-012; `4e76b39` caiu de novo no teste de tempo (consertado em `491efa6`) |
| ATs no Mac | 5 logs, `[exit=0]` em `491efa6` (`AT-001.log`, `AT-002.log`, `AT-003.log`, `AT-004.log`, `AT-006.log`) |
| `check-versions.py --base v2.15.0` | VERDE, 22 skills |
| Sabotagens (`SABOTAGEM.log`, em `c65e658`) | 10 de 10 mortas: executor sem matar a árvore; fatias todas na 1ª; unidade de volta ao módulo; subprocess de texto sem `encoding`; vigia do `checar` sem corte; matriz com `fail-fast: true`; só o filho morto, não o grupo (A2 do avaliador: o mutante sobrevivia em `9e2ad33`); teto `nan`; classe grande inteira; `rc_do_vigia` sem o caso vizinho. O avaliador, ciclo 2, matou mais 6 próprios (`AVAL2-SABOTAGEM-executor.log`) |
| Linha de base no Mac (`MAC-BASE-resumo.tsv`, executor com 6 ao mesmo tempo) | 79 de 81 módulos verdes; `test_sdd_open` TETO (900 s) e 1 teste de tempo do `test_deploy_do_sha` com carga; os 2 verdes sozinhos — levou à unidade = classe e à execução em série |
| Raio de impacto (`RAIO-DE-IMPACTO.md`) | 4 superfícies; 2 quebras achadas e consertadas em `c9cde6e` (o guard mandava UTF-8 ao `report-lint --stdin`, que lia cp1252 no Windows; o executor punha `PYTHONIOENCODING` nas unidades e mascarava a quebra do aluno) |
| Windows real (CI do PR #30, `491efa6`) | 1ª medição inteira em 16 fatias (a mais longa ~18 min, teto 30): **460 unidades** (291 OK, 164 FALHOU, 5 TETO: 4 partes de `test_sdd_open.Projeto` e 1 de `test_claude_adapter.Projeto`); **2.076 testes**: 1.324 passam (~64%), 690 falhas, 48 erros, 14 pulados; 38 de 82 módulos inteiros verdes (`windows/MEDICAO-1-491efa6.md`, `windows/resumo-*.tsv`, `windows/MEDICAO-1-causas.txt`, `windows/logs-quebrados/`) |
| Caminho do aluno no Windows | verde, menos 3 casos do vigia: o ssh pendurado é cortado (3 dos 5 testes de rede passam, o `taskkill` vale); o askpass do editor pendurado (2) e o `gh` pendurado (1) ainda passam do teto |
| Causas das quebras (`windows/MEDICAO-1-causas.txt`) | ~156 por stdout cp1252 nos scripts Python do `sdd/bin` (defeito do produto: o ✅ derruba `design-lint`, `report-lint`… e o `drive` em cascata); ~148 exit code diferente (inclui o `gh` falso dos testes, que o Windows não executa, e o resolvedor de Python); ~116 asserção de texto; ~25 caminho `C:\` × `/c/` (fronteira da governança, `slot`); 3 JSON do `settings.json` com caminho Windows sem escape (defeito do produto); 4 `git commit` pendurado 120 s com os hooks |

---

## Segurança

N.A. (DEFINE). O `taskkill` só recebe o pid do Windows de um filho do próprio script; a action de artefato é fixada por SHA; o
token do job segue só leitura.

---

## Issues Encountered

- **O push para medir foi negado** (decisão do Roberto, depois da explicação): o porte ficou sem medição intermediária; o que a
  medição do PR acusar e não couber vira pendência com a tabela por unidade.
- **O `test_sdd_open` inteiro passou de 900 s no Mac com carga:** a unidade do executor virou a classe (Decision 2 revista).
- **O formato do `unittest` muda do 3.9 para o 3.11** (`(mod.Classe)` × `(mod.Classe.teste)`): o executor lê os dois.
- **O Verify Gate parou na 1ª vez** porque a linha Governança não tinha valor final: o passo 11 rodou com revisor novo (N.A.).
- **O gate de `ce3a779` caiu num teste de tempo** (`test_deploy_do_sha.Redisparo`) com o avaliador rodando 22 módulos ao mesmo
  tempo; o módulo passou 3 de 3 sozinho no piso. É a 3ª queda desse módulo com carga, sempre num teste diferente (candidato 2).
- **O teste de tempo do `test_deploy_do_sha` caiu 3 vezes** (uma por rodada carregada, sempre num teste diferente): o teto de
  1 s para várias consultas a um `gh` falso; teto de 30 s por padrão e 1 s só onde o teste espera o "ainda não sei" (`491efa6`).
  4 cópias simultâneas não reproduziram a queda, nem antes nem depois.
- **5 logs do avaliador gravaram o exit do `tail`/`tr`, não o do comando** (o `gate-shell-evidencia.sh` da release os
  acusou): preservados como `AVAL-AT-001-002-testes.aval.txt`, `AVAL2-AT-003-007-testes-texto.aval.txt`, `AVAL2-AT-004-mac.aval.txt`,
  `AVAL2-AT-005-curator.aval.txt` e `AVAL2-AT-008-deploy-do-sha-sozinho.aval.txt` (a evidência do avaliador não é editada; as
  AVALIACAO citam os nomes `.log` de antes). A prova dos ATs é dos logs `AT-*.log`, que gravam o exit do próprio comando.
- **LM-012 mordeu:** o teste do B3 tinha `1/100000000000` por extenso e o publish-gate do gate de `103697e` o barrou; montado em
  tempo de execução em `4e76b39`.

---

## Deviations from Design

| DESIGN v1.0 | O que foi feito | Por quê |
|---|---|---|
| unidade = módulo, peso por `def test_` | unidade = classe, peso pelo `unittest` | `test_sdd_open` estourou 900 s no Mac; o v1.1 registra |
| 8 fatias, `--teto-modulo` | 12 fatias, `--teto-unidade` | folga no teto de 30 min |
| `corta` decide pelo `sistema` | decide por `/proc/<pid>/winpid` legível | só existe no Git Bash/MSYS; sem `uname` por chamada |
| — | Decision 6 (UTF-8, bash pelo caminho, `test_slot`) | sem medição intermediária, as causas achadas por varredura |
| 12 fatias, unidade inteira | 16 fatias, classe em partes de até 8 (`Classe[ideN]`) | avaliador, ciclos 1 e 2: classes de 12 testes levaram 154 s no Mac (≈ 600 s no Windows) |
| executor põe `PYTHONIOENCODING` nas unidades | a unidade vê o ambiente do aluno | raio de impacto: o UTF-8 posto mascarava a quebra do aluno |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · ciclo 1 (`AVALIACAO_F16W_WINDOWS_20261114-1300.md`): NEEDS_WORK, 5 achados (A1 `nan`/`inf`, A2 neto morto não provado, A3 granularidade do `SECONDS`, A4 seleção vazia verde, A5 DEFINE com `--teto-modulo`), consertados em `c65e658` (A3 registrado em comentário) · ciclo 2 (`AVALIACAO_F16W_WINDOWS_20261114-1530.md`): PASS_PENDENTE_RECIBO, 4 achados leves (B1 documentos, B2 classe de 12 perto do teto, B3 N absurdo, B4 comentário), consertados em `c9cde6e`. Recibos: o CI do PR no Windows (AT-003 a AT-006), a decisão do piso (AT-007) e o Verify Gate inteiro do HEAD

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F16W_WINDOWS.md`.

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (`v2.15.0..ce3a779`, diff inteiro) | `EXTERNAL_REVIEW_20261114-121622` | claude + `openrouter` (qwen) | 2 médios, 1 leve | 3 aplicados (`9e2ad33`); o auditor discordou do R2, aplicado mesmo assim |
| 2 (`v2.15.0..c9cde6e`, diff inteiro) | `EXTERNAL_REVIEW_20261114-134503` | claude + qwen | 2 médios | 2 aplicados (`e6c845a`) |
| 3, a última (`v2.15.0..e6c845a`, diff inteiro) | `EXTERNAL_REVIEW_20261114-135448` | claude + qwen | 1 médio | aplicado (`103697e`); o auditor discordou por falta de contexto, conferido no arquivo; o conserto ficou sem revisor externo por dispensa do Roberto |

Sem `--paths` em nenhuma rodada; sem 2º revisor (`--no-revisor2`: codex sem cota) e sem desempate.

**Medidor dos revisores (`bash sdd/bin/eval-revisores.sh`, `evidence/F16W_WINDOWS/EVAL-REVISORES.log`):**

| Papel | Engine (modelo) | Cobrança | Rodadas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | AGREE |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 3 | 0.0000 | 3.9624 | 6 | 6 de 6 | 0 de 6 | — |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 3 | 0.0767 | 0.0767 | 0 | 0 | 0 | 66.7% (4 de 6) |

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.1) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | unidades por classe (partes de até 8), fatias estáveis e completas; linha por unidade; exits 0/1; `--saida`; stdout UTF-8 | true | `evidence/F16W_WINDOWS/AT-001.log` |
| AT-002 | teto mata a árvore (neto incluído) e segue; uso errado 64 | true | `evidence/F16W_WINDOWS/AT-002.log` |
| AT-003 | job em matriz de 16 fatias nos 2 workflows, igual, com artefato | true | `evidence/F16W_WINDOWS/AT-003.log` + `evidence/F16W_WINDOWS/windows/MEDICAO-1-491efa6.md` (as 16 fatias rodaram no CI do PR #30 e deixaram os artefatos) |
| AT-004 | vigia corta a árvore no Windows; 5 testes sem pulo | false | `evidence/F16W_WINDOWS/AT-004.log` (Mac) + `evidence/F16W_WINDOWS/windows/logs-quebrados/test_checar.TestRemoto_1de2.log`: no Windows, os 3 casos de ssh passam; o askpass (2) e o `gh` pendurado (1) não — pendência da próxima frente (decisão do Roberto) |
| AT-005 | 4 achados medidos no Windows | false | `evidence/F16W_WINDOWS/windows/MEDICAO-1-causas.txt`: medidos, os 4 quebram (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`); o CRLF do curator passa — destino: próxima frente (decisão do Roberto) |
| AT-006 | toda quebra com destino; pulo só por constante | true | `evidence/F16W_WINDOWS/AT-006.log` + `evidence/F16W_WINDOWS/windows/MEDICAO-1-causas.txt` (destino: pendência da próxima frente, com o OK do Roberto) |
| AT-007 | piso aplicado nos workflows e nas 4 frases | true | `evidence/F16W_WINDOWS/AT-007.log` (piso: informativo, a suíte inteira; as 4 frases com o número medido) |
| AT-008 | Ubuntu e macOS seguem verdes | true | `evidence/F16W_WINDOWS/VERIFY-GATE-491efa6.log` (macOS, piso) e o CI do PR #30 (gate Ubuntu e macOS verdes em `491efa6`) |

---

## Final Status

### Overall: ✅ COMPLETE — veredito CONCERNS (o Windows foi medido e ~64% dos testes passam; AT-004 e AT-005 abertos; o porte vira a próxima frente, decisão do Roberto)

---

## Next Step

**Ready for:** avaliador de contexto novo e revisão externa; depois `/sdd-release` (o CI do PR mede o Windows).
