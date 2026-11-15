# BUILD REPORT: F16W2 — Windows, porte das quebras

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W2_WINDOWS |
| **Date** | 2026-11-14 |
| **Author** | build-agent (worktree `sdd-open-f16w-windows`, branch `feat/f16w2-windows`, de `ad32fe1` = `v2.16.0`) |
| **DEFINE** | [DEFINE_F16W2_WINDOWS.md](../features/DEFINE_F16W2_WINDOWS.md) v1.2 |
| **DESIGN** | [DESIGN_F16W2_WINDOWS.md](../features/DESIGN_F16W2_WINDOWS.md) v1.2 |
| **Status** | Complete — PASS no Windows (CI do PR #31: 2.219 testes, 0 falha); piso aplicado (o job no `needs:` da release, decisão do Roberto) |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 13/13 linhas do manifest do DESIGN |
| **Files Created** | 5 testes: `tests/test_f16w2_{passo0,saida,processos,caminhos,render}.py` |
| **Commits** | passo 0: `10dc298` · build: `c8e24b3` (saída UTF-8), `899386c` (calço, revisto depois), `fb87554` (pre-commit e init), `7f19bc6` (caminhos), `ba49f57` (vigia), `8a5a746` (autotestes), `c4c8536` (arnês), `1219b62` (versões), `696e94d` (MANIFEST), `9e07810` (render) · raio de impacto e rodada 1: `cb08ead`, `e68bc88` · gate: `a0ee4a5`, `3ba89de` · sabotagens: `50e74a4` · avaliador, ciclo 1: `452c1a3` · rodada 2: `bff7459` · avaliador, ciclo 2: `9f6c3f5` · rodadas de medição no PR #31: `9815d27`, `4ac2b74`, `50afa50` (piso), `c2690d5` |
| **Tests Passing** | Verify Gate exit 0 em `452c1a3`: 2.219 testes em 25 min, 2 pulados (`evidence/F16W2_WINDOWS/VERIFY-GATE-452c1a3.log`); partida: 2.176 em `ad32fe1` |
| **Skills** | `sdd-auditoria-harness` 1.2.3, `sdd-checar-ambiente` 1.5.3, `sdd-higiene-dado` 1.2.1, `sdd-iniciar-repo` 1.2.2, `sdd-kb` 2.2.3, `sdd-release` 2.12.1, `ux-review-builder` 1.6.1; `check-versions.py --base v2.16.0` VERDE, 22 skills |

**Seleção de modo:** default (um autor; as causas se cruzam nos mesmos scripts e no arnês), com o pedido do Roberto de
executar o pipeline inteiro.

**Passo 0:** curadoria da F16W pelo `playbook-curator.sh --colher` (LM-029, LM-030, LM-031 novas; LM-012 mordeu e foi
promovida ao publish-gate; as 15 contagens "ajudou" e as 3 sugestões ficaram de fora, decisões do Roberto), `10dc298`.

**Medição do Windows:** o Roberto decidiu **medir só no PR do fim** (de novo nesta frente). O build se guiou pela releitura
dos 169 logs da 1ª medição (4 leituras independentes, `evidence/F16W2_WINDOWS/DIAGNOSTICO.md`) e pela emulação local: no
Mac, `PYTHONUTF8=0 LC_ALL=en_US.ISO8859-1` (ou `PYTHONIOENCODING=cp1252`) reproduz o cp1252 do Windows.

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 13 linhas de manifest; as causas tocam os mesmos scripts e o mesmo `tests/apoio.py` |
| Recomendação | default |
| Decisão do usuário | default, 2026-11-14 (pedido do Roberto: pipeline inteiro, só as decisões dele) |

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | testes de fiação | ✔ tratado: os testes novos rodam os scripts de verdade (lints com cp1252, hook com 600 arquivos, init com armadilha no PATH, vigia com gh falso); 13 sabotagens mortas |
| LM-002 | baseline vermelho | ✔ tratado: cada teste novo rodou contra o código anterior e caiu (`AT-001-baseline-vermelho.log`, `AT-002-…`, `AT-004-baseline-hook-antigo.log`, `AT-005-baseline-vigia-antigo.log`, `RAIO-hook-baseline-vermelho.log`) |
| LM-003 | commit antes de revisar | ✔ tratado: revisão e avaliador sobre árvore commitada (`avaliador-guard.sh` verde) |
| LM-005 | heurística nova | ✔ tratado: a heurística do relógio do vigia (`rc_do_vigia`) saiu; o corte é anunciado pela marca, com o caso vizinho testado |
| LM-006 | gate sem `.git` | ✔ tratado: os testes novos criam o próprio repositório; o render lê as funções do arquivo, sem git |
| LM-012 | 11 dígitos no pacote | ✔ tratado: CPF e CNPJ dos testes montados em execução (`test_alarme.cpf`) |
| LM-013 | edição por corte | ✔ tratado: contagem de `def test_` antes e depois em todo módulo tocado (só `test_checar` mudou, +1 de propósito) |
| LM-014 | `text=True` sem encoding | ✔ tratado: `errors="replace"` onde a saída cp1252 virava `None` |
| LM-015 | `PYTHONIOENCODING` no pipe | ✔ tratado: a troca vai no próprio script (`reconfigure`), que vale também com `-I` e na chamada direta |
| LM-016 | vigia no Windows | ✔ tratado: a marca do vigia não depende do exit do processo cortado |
| LM-017 | fallback silencioso | ✔ tratado: sem arquivo temporário, a saída do checar volta ao caminho de antes (testado com `mktemp` que falha) |
| LM-018 | `PIPESTATUS` no zsh | ✔ tratado: logs por `evlog.sh` (bash, `rc=$?`) |
| LM-029 | "bash" pelo nome | ✔ tratado: o PATH restrito nunca usa a System32; `test_windows.py` segue barrando |
| LM-030 | executor com `PYTHONIOENCODING` | ✔ tratado: o executor segue sem a variável; o teste da saída a põe de propósito (`cp1252`) |
| LM-031 | teste de tempo com carga | ✔ tratado: a prova de lentidão é contagem, não relógio; uma queda do `test_deploy_do_sha` com carga passou sozinha |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `calço` `PATH` `-X utf8` `vaza` `comando do aluno`
regra: Um calço posto no PATH para consertar o modo do Python dos scripts do pacote (`-X utf8`, `| tr -d '\r'`) vaza para todo
  filho que chama `python3`, inclusive o comando de teste do próprio projeto: na F16W2, o pytest do aluno passaria a rodar em
  modo UTF-8, com resultado diferente de quando roda direto, e a saída byte a byte do curador perderia o `\r`.
Do instead: o conserto do modo vai no próprio programa (a troca da saída no início dele); o calço no PATH só troca QUAL
  Python roda (`exec`), nunca COMO.
evidencia: sdd/features/DESIGN_F16W2_WINDOWS.md
ficha: F16W2_WINDOWS
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `git grep` `color.ui` `--no-color` `config do usuário` `parse`
regra: Saída de comando do git lida por máquina segue a configuração de quem roda: com `color.ui=always`, o `git grep -l`
  embrulha cada nome em códigos ANSI mesmo indo para arquivo, e na F16W2 o hook novo deixaria passar todo byte NUL.
Do instead: o script que lê a saída do git passa `--no-color` e `-c color.ui=never` (e o que mais a saída lida dependa, como
  `core.quotePath` com `-z`), e um teste roda com a config hostil ligada.
evidencia: sdd/reports/evidence/F16W2_WINDOWS/RAIO-hook-baseline-vermelho.log
ficha: F16W2_WINDOWS
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `link simbólico` `PATH restrito` `DLL` `Windows` `dirname vazio`
regra: No Windows, o executável chamado por um link simbólico não acha as DLLs que moram ao lado do original (msys-2.0.dll,
  python3xx.dll): o `command -v dirname` acha o link e o `$(dirname x)` devolve vazio; na F16W, ~105 quedas da revisão vinham
  do PATH de links que os testes montavam para "tirar" uma ferramenta.
Do instead: PATH restrito pelo ajudante `path_restrito` de `tests/apoio.py` (no Windows, as pastas de verdade das
  ferramentas; o nome que o teste quer ausente é conferido e, se a pasta o traz, o teste é pulado por constante).
evidencia: sdd/reports/evidence/F16W2_WINDOWS/DIAGNOSTICO.md
ficha: F16W2_WINDOWS
>>>

---

## Files Created

| Arquivo | Para quê |
|---|---|
| `tests/test_f16w2_passo0.py` | a curadoria da F16W (passo 0) |
| `tests/test_f16w2_saida.py` | AT-001/AT-002: guarda dos `.py` e dos programas embutidos; os scripts com stdout cp1252; o stdin do `report-lint` |
| `tests/test_f16w2_processos.py` | AT-004: contagem por armadilha no PATH (commit de 600 arquivos, init) e as recusas do hook |
| `tests/test_f16w2_caminhos.py` | AT-003: o `slot.sh` com um python3 que escreve `\r\n` |
| `tests/test_f16w2_render.py` | AT-004: a renderização do init nos 24 casos de borda, byte a byte como na `v2.16.0` |
| `sdd/reports/evidence/F16W2_WINDOWS/DIAGNOSTICO.md` | as causas das quebras, com arquivo:linha (documento SDD, fora do pacote) |

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh sdd/features/DEFINE_F16W2_WINDOWS.md`) | exit 0 em `452c1a3`: 2.219 testes, 2 pulados; publish-gate verde na cópia de `git archive` (`VERIFY-GATE-452c1a3.log`). Antes: `1219b62` barrado pelo publish-gate (teste fora do `MANIFEST.txt`); `696e94d` caiu em 11 testes de texto que fixam versão e no SHA de origem da F21 (`a0ee4a5`); `50e74a4` caiu num teste de texto dos imports do `eval-revisores` (`3ba89de`) |
| ATs no Mac | 7 logs, `[exit=0]` em `3ba89de` (`AT-001.log` a `AT-007.log`) |
| Linha de base vermelha | `AT-001-baseline-vermelho.log` (28 quedas), `AT-002-baseline-vermelho.log`, `AT-004-baseline-hook-antigo.log` (contagem vermelha: 8.030 e 5.037; recusas verdes nos 2 hooks), `AT-005-baseline-vigia-antigo.log` ("ok" em vez de "sem resposta"), `RAIO-hook-baseline-vermelho.log` (cor e nome não-UTF-8), `A1-ntpath-baseline-vermelho.log` (7 quedas, as do Windows) |
| Emulação do cp1252 no Mac | os módulos dos lints com `PYTHONUTF8=0 LC_ALL=en_US.ISO8859-1`: de 114 quedas (4 módulos, em `ad32fe1`) a 0 (306 testes, 12 módulos) |
| Contagem de processos | commit de 629 arquivos depois do `init`: 5.651 → 21 programas (21 s → 0,7 s no Mac); `init` com os 5 vendors: 9.360 → 1.373 (28 s → 8 s), as mesmas 803 cópias byte a byte e nos bits de execução; 24 casos de borda da renderização iguais à `v2.16.0` |
| Sabotagens (`SABOTAGEM.log`, `SABOTAGEM-2.log`) | 13 de 13 mortas (2 sobreviveram na 1ª passada, S9 e S13, e viraram testes que as matam em `50e74a4`) |
| `check-versions.py --base v2.16.0` | VERDE, 22 skills |
| Raio de impacto (6 superfícies, agentes novos) | 4 quebras reais, consertadas: o calço do Python vazava para o comando de teste do aluno, segurava o progresso e tirava o `\r` de saída byte a byte (Decision 2 revista); o checar perdia a saída sem `TMPDIR` gravável; o hook novo deixava passar NUL com `color.ui=always` e nome com byte não-UTF-8; o `acha()` do deploy-do-sha mudava a busca fora do Windows. Notas aplicadas: `chmod a-x` da cópia que já existia |
| Windows real (CI do PR #31, 6 medições: `windows/MEDICAO-{2,3,4,6}-*.md`) | `9f6c3f5`: 484 unidades, 2.219 testes, 33 falhas, 9 erros, 0 no teto (~97%) · `9815d27`: 8 falhas · `4ac2b74`: 4 falhas · `50afa50`: 4 falhas (uma linha vizinha do mesmo teste) · **`c2690d5`: 484 de 484 unidades OK, 2.219 testes, 0 falha, 0 erro, 31 pulados por constante; a fatia mais longa ~14 min** (antes: 1.324 de 2.076 passando, ~64%, 5 no teto). Ubuntu e macOS verdes no mesmo run |
| Piso (decisão do Roberto, 2026-11-15) | `testes-windows` no `needs:` do job `release` (`release.yml`); as 4 frases dizem que o Windows é testado a cada release desde a v2.16.1 |

---

## Segurança

N.A. (DEFINE). O vigia só corta a árvore que o próprio script criou, e a marca dele mora numa pasta própria; o `pre-commit`
mais rápido mantém as mesmas recusas (testado nos dois hooks); o `acha()` do deploy-do-sha só aceita extensões que o
Windows executa. Risco aceito: no Windows, um `gh.bat` posto pelo próprio usuário antes no PATH roda pelo `cmd.exe`.

---

## Issues Encountered

- **A causa (2) do prompt não era do produto:** o `settings.json` sai de `json.dump`; o JSON inválido era do ajudante
  `payload()` do teste.
- **A Decision 2 mudou no build:** o calço com `-X utf8` e `tr -d '\r'` vazava para o comando do aluno (raio de impacto);
  virou a troca da saída em cada Python embutido (DESIGN v1.2, DEFINE v1.2).
- **A governança não saiu N.A.:** o revisor novo achou o tema no `pre-commit` (CPF/CNPJ, certificado); o Roberto dispensou
  e as recusas viraram teste negativo no AT-004 (DEFINE v1.1).
- **Testes de tempo com carga (LM-031):** o `test_deploy_do_sha` caiu uma vez com o gate rodando ao lado e passou sozinho.
- **Um arquivo congelado:** o `validate_reverse.py` da F21 é conferido por SHA-256 ao pacote de origem e ficou de fora da
  troca da saída (DEFINE v1.3, avaliador A2).

---

## Deviations from Design

| Item | DESIGN | Build | Por quê |
|---|---|---|---|
| Decision 2 | calço sempre no Windows, `-X utf8` e `tr -d '\r'` | troca da saída em cada Python embutido; calço transparente | raio de impacto: o calço vazava para o comando do aluno (DESIGN v1.2) |
| Pre-commit (H5) | um `git grep` do índice | o `git grep` só com mais de 40 candidatos | revisão, rodada 1, R1: commit pequeno em repositório grande |
| AT-001 | todo `.py` com `__main__` | menos o `validate_reverse.py` congelado da F21 | SHA-256 de origem (DEFINE v1.3) |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · ciclo 1 (`AVALIACAO_F16W2_WINDOWS_20261114-2303.md`): NEEDS_WORK, 4 achados (A1 o teste no Mac com `ntpath` do AT-003 não existia, A2 a exceção do arquivo congelado sem registro, A3 comentário velho, A4 `\r` em 3 `python3 -c` do `sdd-open.sh`), consertados em `452c1a3` e no DEFINE v1.3 · ciclo 2 (`AVALIACAO_F16W2_WINDOWS_20261115-0011.md`): PASS_PENDENTE_RECIBO, 2 achados leves (A1 a frase da exceção no DEFINE, A2 4 vizinhos que só aceitavam caminho absoluto com `/`), consertados no DEFINE e em `9f6c3f5`. Recibos: o CI do PR no Windows e no Ubuntu (AT-003, AT-005 a AT-009) e a decisão do piso (AT-008)

---

## Advisor Ledger

Ledger completo: `sdd/reviews/LEDGER_REVISAO_F16W2_WINDOWS.md`.

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (`v2.16.0..696e94d`, diff inteiro) | `EXTERNAL_REVIEW_20261114-213217` | claude + `openrouter` (qwen) | 4 médios, 1 leve + 1 do auditor | 3 aplicados (`e68bc88`), R3, R5 e N1 rebatidos com evidência ou escopo |
| 2 (`v2.16.0..452c1a3`, diff inteiro) | `EXTERNAL_REVIEW_20261114-230738` | claude + qwen | 1 médio, 3 leves | 4 aplicados (`bff7459`) |
| 3 (`v2.16.0..50afa50`, diff inteiro) | `EXTERNAL_REVIEW_20261115-030620` | claude; o qwen estourou o tempo | 1 médio, 1 leve | R2 aplicado (`c2690d5`), R1 rebatido; sem auditor, não completou |
| 4, acima do teto (`v2.16.0..c2690d5`, diff inteiro) | `EXTERNAL_REVIEW_20261115-040405` | claude + qwen | 1 médio | rebatido com evidência; `--conferir` CONFERE (2º revisor dispensado: codex sem cota) |

Sem `--paths` em nenhuma rodada; sem 2º revisor (`--no-revisor2`: codex sem cota) e sem desempate. O raio de impacto rodou
antes da rodada 2.

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.3) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | saída dos scripts Python em UTF-8 e `\n`, com cp1252 no ambiente | true | `evidence/F16W2_WINDOWS/AT-001.log` |
| AT-002 | todo Python embutido escreve UTF-8 e `\n`; reserva exporta `PYTHONIOENCODING`; calço transparente | true | `evidence/F16W2_WINDOWS/AT-002.log` |
| AT-003 | caminhos numa forma só; raiz do git sem `cmd.exe` | true | `evidence/F16W2_WINDOWS/AT-003.log` + `evidence/F16W2_WINDOWS/A1-ntpath-baseline-vermelho.log` (Windows real: CI do PR) |
| AT-004 | hook com ≤ 3 programas por arquivo, init com ≤ metade; as mesmas recusas | true | `evidence/F16W2_WINDOWS/AT-004.log` |
| AT-005 | vigia anuncia o corte, ≤ 12 s, `gh_estado` igual nos 2 scripts | true | `evidence/F16W2_WINDOWS/AT-005.log` (Windows real: CI do PR) |
| AT-006 | arnês no Windows; pulos só por constante | true | `evidence/F16W2_WINDOWS/AT-006.log` (Windows real: CI do PR) |
| AT-007 | autotestes sem nome proibido nem sobra; trava-link recusada | true | `evidence/F16W2_WINDOWS/AT-007.log` |
| AT-008 | medição no CI do PR; piso e frases | true | `evidence/F16W2_WINDOWS/AT-008.log` (a tabela de `c2690d5`: 0 falha, 0 no teto; o piso no `needs:` e as frases conferidos por `test_release_workflow`) |
| AT-009 | Ubuntu e macOS seguem verdes | true | `evidence/F16W2_WINDOWS/VERIFY-GATE-452c1a3.log` (macOS, piso; Ubuntu: CI do PR) |

---

## Final Status

### Overall: ✅ COMPLETE — veredito PASS no CI (Windows, Ubuntu e macOS verdes no PR #31); revisão em 4 rodadas (a 4ª acima do teto, decisão do Roberto) e 4 rodadas de medição no PR (2 acima do limite, decisões do Roberto)

---

## Next Step

**Ready for:** publicação da `v2.16.1` (fast-forward da `main`), depois o starter gerado pela tag.
