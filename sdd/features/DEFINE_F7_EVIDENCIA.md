# DEFINE: F7 Evidência que não mente

> O sdd-open passa a ser fail-closed nos pontos onde o SDD privado já é: o `report-lint.py` reprova relatório que não prova a avaliação, que cita evidência ignorada pelo git ou cuja tabela ele não reconhece; a release não sai com avaliação `PENDENTE` nem com log cujo exit é do formatador; o gate prova que fica vermelho no código anterior; cada execução do gate deixa uma linha de registro; só falha de teste nova aborta; e o avaliador não é despachado com trabalho não commitado.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F7_EVIDENCIA |
| **Date** | 2026-10-30 |
| **Author** | SDD Define by RDD (sessão com Roberto Dias Duarte) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

O sdd-open é fail-open em sete pontos que o SDD privado já fechou (fontes lidas em `origin/main` do privado, `ecdab8d41`):
- **Avaliação ausente passa.** O `report-lint.py` só confere o veredito que aparece no texto. Um relatório que não diz nada sobre o avaliador sai 0. Dos 8 `BUILD_REPORT` do próprio open, 5 passam assim (F1, F2, F3, M1, W0).
- **Tabela não reconhecida passa.** Com cabeçalho diferente do template (`Result | Evidence`, por exemplo), o lint não confere linha nenhuma e sai 0. O `EVIDENCIA.md` documenta esse comportamento como regra.
- **Evidência que o git ignora passa.** Um `AVALIACAO_*.md` ou um log que existe no disco, mas que `.gitignore` ou `.git/info/exclude` esconde, nunca chega ao commit. No privado, 12 de 19 avaliações se perderam assim.
- **`PENDENTE` não existe.** Não há como registrar um build travado antes do avaliador, e nada impede a release com ele.
- **O exit do log pode ser do formatador.** A receita do `EVIDENCIA.md` não grava exit nenhum, e um `cmd | tail; echo "[exit=$?]"` grava o exit do `tail`. Nos logs do próprio open, 19 linhas `exit=` são do formatador.
- **Nada prova que o gate tem dentes, nem quantas voltas ele levou.** Nenhum script roda a asserção contra o código anterior para exigir vermelho lá, e nenhuma execução do `verify-gate.sh` deixa registro.
- **Falha antiga e falha nova são iguais, e o avaliador pode apagar trabalho.** Uma suíte com uma falha conhecida trava todo build, ou ensina a ignorar vermelho. E o avaliador é despachado com a árvore suja: ele usa o shell para provar os ATs e, ao restaurar um arquivo, pode apagar trabalho não commitado (incidente do privado, LM-146).

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem roda a `sdd-build` com o open, em qualquer um dos 7 agentes | Constrói e grava o `BUILD_REPORT` | O relatório sai verde sem provar a avaliação; a evidência some no commit; o avaliador pode destruir trabalho não commitado; uma falha antiga de teste trava o build |
| Quem roda a `sdd-release` | Publica depois de um OK | Pode publicar feature com avaliação pendente ou com log de exit falso |
| Mantenedor do open e do privado (Roberto; F15) | Substitui o SDD privado pelo open (P4) | Sem estes mecanismos no open, a troca abranda o que o privado já garante |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | **`sdd/bin/report-lint.py` fail-closed** (D4). As regras novas entram como funções ao lado das atuais:<br>• **cabeçalho:** reconhece também `Result`/`Evidence`; relatório sem tabela de critérios reconhecida reprova;<br>• **existência (E1):** sem `AVALIACAO_<F>_<AAAAMMDD>…md` não vazio e não ignorado pelo git em `sdd/reviews/`, e sem declaração `avaliador: N.A. (<motivo>)` ou `avaliador: PENDENTE (<motivo>)` fora de bloco cercado, reprova como "avaliação ausente", listando as 3 saídas;<br>• **camadas (E5):** `N.A.` reprova quando o File Manifest de `sdd/features/DESIGN_<F>.md` toca ≥ N camadas de `layers:` (N = `evidence.require_avaliacao_layers`, default 2); contagem impossível aceita o `N.A.` com ⚠️ e a causa;<br>• **declaração sem motivo** reprova;<br>• **`PENDENTE` (E2):** no modo comum, sai 0 com ⚠️; `--pendente <relatório…>` lista `arquivo:linha: PENDENTE (<motivo>)` e sai 1;<br>• **`git check-ignore` (E3)** sobre cada evidência citada e sobre o `AVALIACAO` da existência;<br>• **veredito (E4):** lido em linha, título + parágrafo seguinte ou tabela, fora de bloco cercado, com `PENDENTE` conhecido;<br>• **`--stdin <caminho>` (E6):** confere o conteúdo lido da entrada padrão como se estivesse em `<caminho>`. |
| **MUST** | **`sdd/bin/verify-gate.sh`** (E9):<br>• `--trace`, ligado por padrão: toda execução que não é `--print`, depois de achar a raiz do repositório, acrescenta 1 linha JSONL `{"ts","feature","src","kind","exit","define"}` em `${SDD_TRACE_DIR:-sdd/traces}/<F>.jsonl`, em qualquer exit; `SDD_TRACE=off` desliga; falha ao gravar nunca muda o exit;<br>• `--sem-define <F>` grava `{"src":"release","kind":"no-define","exit":0,"define":""}` e sai 0. |
| **MUST** | **`sdd/bin/gate-baseline.sh <DEFINE.md> [--base <ref>] [--feature <F>] [--sobrepor <caminho>]…`** (E7): roda o gate do DEFINE do build numa cópia de `origin/<project.default_branch>` (fallback `main`), com o DEFINE, `sdd/bin/` e cada `--sobrepor` do build por cima (a asserção de agora contra o código de antes), e grava `sdd/reports/evidence/<F>/BASELINE-gate.log`. Saídas:<br>• **0:** a base reprova **avaliando**: o gate sai 2 **e** a saída tem a linha `🔴` do runner (o comando declarou VERMELHO) ou um marcador de asserção dos 5 formatos de teste — o `(rc=N)` do runner sozinho não conta, porque é o rc bruto do comando e um crash também dá 2;<br>• **2:** a base passa (asserção sem dentes);<br>• **3:** indeterminado (vermelho sem esse sinal, 3, 4, 5, 64 ou ref ausente);<br>• **64:** uso. |
| **MUST** | **`sdd/bin/gate-shell-evidencia.sh [--base <ref>] [<log\|pasta>…]`** (E8). Sem caminho, olha os `*.log` de `sdd/reports/evidence/` tocados contra `origin/<default_branch>` mais os não rastreados. Sai 2 nestes casos:<br>• uma linha `[exit=N]` ou `exit=N` vem depois de um `$ <comando>` cujo último estágio de pipe é um formatador (`tail head cat tee wc sed cut sort uniq column tr fold nl`), sem `rc=$?`, `PIPESTATUS` ou `pipefail` antes do último pipe;<br>• `[exit=]` vazio;<br>• `[exit=$?]` literal.<br>Base inválida sai 64; nenhum log sai 0. |
| **MUST** | **`sdd/bin/avaliador-guard.sh [--root <dir>] [--permitir <prefixo>]…`** (E11):<br>• **0:** árvore limpa, ou suja só em `sdd/reports/evidence/`, em `sdd/traces/` (o trace do gate) e nos prefixos permitidos;<br>• **1:** sujeira fora disso, listando cada caminho (renomeação conta os dois lados) e o comando de commit;<br>• **2:** o git falhou (não conferido);<br>• **64:** uso.<br>`SDD_AVALIADOR_GUARD=off` sai 0 com ⚠️. |
| **MUST** | **`sdd/bin/test-baseline.sh [--cmd <comando>] [--touched [--base <ref>]] [--aceitar <id>]`** (E10, implementação nova sobre `{{TEST_CMD}}`):<br>• roda `project.test_cmd` (ou `--cmd`) e extrai os identificadores de falha de 5 formatos: unittest, pytest, jest/vitest, go test e deno test;<br>• compara com `sdd/baselines/tests.txt` (um id por linha, `#` comenta);<br>• **0:** só falhas conhecidas; numa execução completa (o `project.test_cmd` do config, sem `--cmd` nem `--touched`, sem falha nova), o id que sarou sai do arquivo e é listado; em qualquer outro caso nada sai, com `⚠️ baseline não podado (execução parcial)`;<br>• **2:** falha nova, com os ids;<br>• **3 (inconclusivo):** rc≠0 sem nenhuma falha reconhecida, ou comando ausente;<br>• **0 com `RESULTADO: PULADO`:** `test_cmd` vazio sem `--cmd`;<br>• **`--touched`:** só aborta por falha nova cujo id cita um arquivo de teste tocado no diff, e não remove nada do baseline;<br>• **`--aceitar <id>`:** é o único jeito de uma falha entrar no baseline. |
| **MUST** | **`sdd/config.example.yaml`**: o mapa novo `evidence:` com `require_avaliacao_layers: 2` e um comentário que explica a regra. Nenhum outro slot (D11). |
| **MUST** | **`sdd/templates/fragments/EVIDENCIA.md`**:<br>• receita `out=$(<cmd> 2>&1); rc=$?; … echo "[exit=$rc]"`;<br>• a forma mínima do relatório (tabela reconhecida + linha do avaliador);<br>• as 3 formas da linha do avaliador e o que o lint faz com cada uma;<br>• "cabeçalho não reconhecido reprova" no lugar de "sai 0";<br>• `git check-ignore`;<br>• nenhum nome de ferramenta de um agente só.<br>**`sdd/templates/BUILD_REPORT_TEMPLATE.md`**: a linha do avaliador com as 3 formas, incluindo `PENDENTE (<motivo>)`.<br>**`sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md`** (novo, E13): inventário executado, detalhe por prompt, drift, versionamento e rollback. |
| **MUST** | **`.agents/skills/sdd-build/SKILL.md`** → **2.3.0**:<br>• passo 1 confere a flag de prompts de LLM do DEFINE contra a seção de prompts do DESIGN (E12): `true` sem a seção, ou `false` com ela, faz a skill parar e iterar o DESIGN;<br>• passos 1.5 e 5d rodam `sdd/bin/avaliador-guard.sh` antes de despachar quem não viu a conversa, e param com exit ≠ 0;<br>• quando o build corrige uma asserção do gate, roda `sdd/bin/gate-baseline.sh` (exit 0 obrigatório);<br>• 5b usa `sdd/bin/test-baseline.sh` quando `test_cmd` está preenchido;<br>• passo 6 cita a linha do avaliador, `PENDENTE` e o fragmento `LLM_PROMPTS_BUILD_REPORT.md` quando a flag é `true`;<br>• um "por quê" por regra nova em `## Por que cada regra existe`.<br>**`.agents/skills/sdd-release/SKILL.md`** → **2.4.0**:<br>• 0a roda `report-lint.py --pendente` e `gate-shell-evidencia.sh`; qualquer exit ≠ 0 aborta, citando o exit, e 64 ou 127 acrescentam "atualize `sdd/bin/` (`doctor`, depois `init`)";<br>• sem DEFINE, roda `verify-gate.sh --sem-define <F>`;<br>• um "por quê" por regra nova;<br>• o bloco do OK fica intacto. |
| **MUST** | **Fixtures** em `sdd/fixtures/evidencia/`, limpas (sem PII, sem `/Users/`, sem `.claude/sdd/`):<br>• `BUILD_REPORT_sem_avaliacao`, `BUILD_REPORT_pendente`, `BUILD_REPORT_evidencia_ignorada` e o controle;<br>• os logs `shell-honesto`, `shell-falso-verde` e `shell-pipe-assertivo`;<br>• uma saída por formato de teste.<br>Cada script novo ou alterado tem teste dos dois lados em `tests/`. |
| **MUST** | **`docs/roadmap.md` e `docs/pt-BR/roadmap.md`**: a linha "Hooks and evidence" / "Hooks e evidência" passa a falar só dos hooks; o roadmap continua com 7 linhas. **`MANIFEST.txt`** com todo arquivo novo, em ordem `LC_ALL=C`. |
| **MUST** | Nenhuma regressão:<br>• as 32 asserções de `tests/test_report_lint.py`; a única mudança é a forma mínima no relatório de exemplo dos 11 testes que esperam 0;<br>• os 6 exits e as saídas do `verify-gate.sh` nas fixtures de `sdd/fixtures/`, e o mapeamento do `--strict`;<br>• os 514 testes;<br>• a camada de conversa (a seção nas 17 skills, o bloco comum e as `FRASES` do `tests/test_conversa.py`);<br>• o bloco do OK da `sdd-release`;<br>• `playbook-lint.sh --self-test`;<br>• lints com 0/1/64 e mensagens com `🛑`, `RESULTADO:` e `→`. |
| **MUST** | 1 sabotagem por script alterado ou novo (6: `report-lint.py`, `verify-gate.sh` e os 4 novos), cada uma vermelha num teste nomeado e verde de novo com `git checkout`. |
| **SHOULD** | As notas da Release `v2.2.8` dizem o que um `BUILD_REPORT` antigo precisa acrescentar (tabela reconhecida e a linha do avaliador). |

---

## Success Criteria

- [ ] `report-lint.py` reprova `BUILD_REPORT_sem_avaliacao` e `BUILD_REPORT_evidencia_ignorada`, aprova o controle, e no modo `--pendente` sai 1 com `BUILD_REPORT_pendente` (0 no modo comum, com ⚠️).
- [ ] Sobre os 8 relatórios do open, `report-lint.py` sai 1 em F1, F2, F3, M1 e W0, só por "avaliação ausente", e 0 em F4, F5 e F6 (log em `evidence/F7_EVIDENCIA/`).
- [ ] `gate-shell-evidencia.sh` sobre os logs do open sem `F7_EVIDENCIA/` acusa exatamente as 22 `arquivo:linha` listadas em `corpus-esperado.txt` (19 de formatador e 3 `exit=` vazios) e nenhuma outra; as 3 fixtures dão 0, 2 (com o conjunto exato de `arquivo:linha`) e 0.
- [ ] `verify-gate.sh` grava exatamente 1 linha JSONL por execução e 0 com `--print` ou `SDD_TRACE=off`; nas 4 fixtures `DEFINE_FIXTURE_*`, exit e saída são idênticos aos da `v2.2.7`.
- [ ] `gate-baseline.sh`, `avaliador-guard.sh` e `test-baseline.sh` passam nos testes dos dois lados; `test-baseline.sh` reconhece 5 de 5 formatos.
- [ ] `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado nos 4 scripts novos e no `verify-gate.sh`; todo `awk` sobre log roda com `LC_ALL=C`.
- [ ] A suíte sai 0 no piso `SDD_TEST_BASH=/bin/bash /usr/bin/python3` (Python 3.9.6 + bash 3.2.57), com mais de 514 testes e 0 falha; os testes novos falham na árvore `v2.2.7` (baseline vermelha).
- [ ] `skill-lint.py --conversa` sai 0 nas 17 skills; `check-versions.py --base v2.2.7 --base-obrigatoria` sai 0 com `sdd-build` 2.3.0 e `sdd-release` 2.4.0; `wc -l` ≤ 500 em cada `SKILL.md`.
- [ ] 6 sabotagens vermelhas e de volta ao verde.
- [ ] `report-lint.py sdd/reports/BUILD_REPORT_F7_EVIDENCIA.md` sai 0 com as regras novas.
- [ ] O CI do PR sai verde em `ubuntu-latest` e `macos-latest`; depois do push em `main`, `gh release view v2.2.8 -R robertodiasduarte/sdd-open` lista `SHA256SUMS.txt` e `shasum -a 256 -c` sai 0.

---

## Acceptance Tests

| ID | Pattern | Criterion (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Unwanted | **If** a `BUILD_REPORT_<F>.md` has no criteria table whose header the lint recognizes (a column starting with `Evid` and one starting with `Resultado`, `Status`, `Passou` or `Result`), **then** `report-lint.py` **shall** exit 1 naming the missing table | test |
| AT-002 | Event-driven | **When** the criteria table uses the header `\| ID \| Criterion \| Result \| Evidence \|`, `report-lint.py` **shall** check its `true` rows with the same rules as the template header | test |
| AT-003 | Unwanted | **If** `sdd/reviews/` has no non-empty, not-git-ignored `AVALIACAO_<F>_<YYYYMMDD>…md` and the report has no `avaliador: N.A. (<motivo>)` or `avaliador: PENDENTE (<motivo>)` line outside a fenced block, **then** `report-lint.py` **shall** exit 1 with the class "avaliação ausente" and the 3 ways out, as on `sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md` | test |
| AT-004 | Event-driven | **When** such an `AVALIACAO` exists, the report **shall** pass the existence rule without citing it; **when** the report declares `avaliador: N.A. (<motivo>)` and the File Manifest of `DESIGN_<F>.md` touches fewer than N layers, it **shall** pass; **when** the count is impossible (`layers:` empty, no DESIGN, no manifest), it **shall** pass with a ⚠️ line naming the cause | test |
| AT-005 | Unwanted | **If** the report declares `N.A.` and the File Manifest touches ≥ N distinct layers of `layers:` (N read from `evidence.require_avaliacao_layers`, default 2 when absent, and 2 with ⚠️ when not a positive integer), **then** `report-lint.py` **shall** exit 1 naming the count and the layers; with N = 1, a 1-layer manifest **shall** also fail | test |
| AT-006 | Unwanted | **If** an `N.A.` or `PENDENTE` declaration has no `(<motivo>)`, **then** `report-lint.py` **shall** exit 1 naming the line | test |
| AT-007 | Event-driven | **When** the report declares `avaliador: PENDENTE (<motivo>)`, `report-lint.py <report>` **shall** exit 0 with a ⚠️ line, and `report-lint.py --pendente <report…>` **shall** print `<arquivo>:<linha>: PENDENTE (<motivo>)` and exit 1; with no `PENDENTE` it **shall** exit 0, and with an unreadable file or no argument, 64 | test |
| AT-008 | Unwanted | **If** a cited evidence log or `AVALIACAO_*.md` exists but `git check-ignore` reports it ignored, **then** `report-lint.py` **shall** exit 1 saying the git ignores it and how to fix it, as on `BUILD_REPORT_evidencia_ignorada.md`, and an ignored `AVALIACAO` **shall not** satisfy AT-003; if `git check-ignore` cannot run, it **shall** print ⚠️ "persistência não conferida" | test |
| AT-009 | Event-driven | **When** the verdict label `Veredito do avaliador` is followed by `PASS`, `NEEDS_WORK` or `PASS_PENDENTE_RECIBO` on the same line, in the same table row, or in the paragraph right after a heading, `report-lint.py` **shall** require an existing `AVALIACAO_<F>_*.md` in that same unit; a label inside a fenced block **shall** be ignored, and `PENDENTE` and `N.A.` **shall** be treated as declarations | test |
| AT-010 | Event-driven | **When** `report-lint.py --stdin <caminho>` receives a report on standard input, it **shall** apply every rule as if the content were at `<caminho>` and exit with the same code | test |
| AT-011 | Event-driven | **When** `report-lint.py` runs on the 8 `BUILD_REPORT` of the open, it **shall** exit 1 on F1, F2, F3, M1 and W0, each only with the class "avaliação ausente", and 0 on F4, F5 and F6, evidenced in `evidence/F7_EVIDENCIA/relatorios-do-open.log` | test |
| AT-012 | Non-regression | The 32 existing tests of `tests/test_report_lint.py` **shall continue to** assert the same exit and the same message; the only change **shall** be the minimal shape (recognized table and `avaliador: N.A. (1 camada)`) in the sample report of the 11 tests that expect 0 | test |
| AT-013 | Event-driven | **When** `verify-gate.sh` runs without `--print`, it **shall** append exactly 1 JSON line with `ts`, `feature`, `src: verify-gate`, `kind`, `exit` and `define` to `${SDD_TRACE_DIR:-sdd/traces}/<F>.jsonl`, for every exit code once the repository root is resolved, recording the exit before the `--strict` remap | test |
| AT-014 | Unwanted | **If** `--print` is given, `SDD_TRACE=off` is set, or the trace directory cannot be written, **then** `verify-gate.sh` **shall** write no line and **shall** keep the exit and the output it would have without the trace | test |
| AT-015 | Event-driven | **When** `verify-gate.sh --sem-define <F>` runs, it **shall** append `{"src":"release","kind":"no-define","exit":0,"define":""}` and exit 0 with `RESULTADO:`; without `<F>` it **shall** exit 64 | test |
| AT-016 | Non-regression | `verify-gate.sh` **shall continue to** give, on the 4 `sdd/fixtures/DEFINE_FIXTURE_*.md`, the same exit and the same output with the trace on as with `SDD_TRACE=off`, and as the `v2.2.7` script (evidenced in `evidence/F7_EVIDENCIA/saidas-v2.2.7.log`), and `--strict` **shall continue to** map 3/4/5 to 1 | test |
| AT-017 | Event-driven | **When** the DEFINE's gate, with `sdd/bin/`, the DEFINE and each `--sobrepor <caminho>` taken from the build, exits 2 on a copy of the base **and** its output has the runner's `🔴 o comando declarou VERMELHO` line or an assertion marker of the 5 test formats, `gate-baseline.sh` **shall** exit 0 and write `sdd/reports/evidence/<F>/BASELINE-gate.log` with `$ ` on line 1 | test |
| AT-018 | Unwanted | **If** the gate passes on the base, **then** `gate-baseline.sh` **shall** exit 2; **if** it does not evaluate there (a red whose only signal is `GATE VERMELHO … (rc=N)`, whatever N, such as a missing file or a syntax error; exit 3, 4, 5 or 64; or no base ref), **then** it **shall** exit 3 naming the rc; wrong usage or a missing DEFINE **shall** exit 64 | test |
| AT-019 | Unwanted | **If** a log line `[exit=N]` or `exit=N` follows a `$ <command>` whose last pipe stage (`|` or `|&`, after any `VAR=value`, `command`, `env` or `(` prefix) is a formatter, with no `<var>=$?` before the last pipe and no `PIPESTATUS` or `pipefail` in the command outside a comment (a lone `$` takes the next line as the command), or the line is `[exit=]`, `exit=` (empty or blank, with or without brackets) or `[exit=$?]`, **then** `gate-shell-evidencia.sh` **shall** exit 2 naming `file:line`, printing exactly the expected `file:line` set of `shell-falso-verde.log` | test |
| AT-020 | Event-driven | **When** the logs are honest (no pipe, `rc=$?` before the pipe, or an asserting last stage such as `grep -c`, `jq -e`, `awk … exit 1`), `gate-shell-evidencia.sh` **shall** exit 0; on the `*.log` of `sdd/reports/evidence/` of the open **excluding** `F7_EVIDENCIA/`, it **shall** report exactly the 22 `file:line` listed in `evidence/F7_EVIDENCIA/corpus-esperado.txt` (19 with a formatter as the last stage and the 3 empty `exit=` lines); an invalid `--base` **shall** exit 64 | test |
| AT-021 | Event-driven | **When** the tree is clean, or dirty only under `sdd/reports/evidence/`, `sdd/traces/` or a `--permitir` prefix, `avaliador-guard.sh` **shall** exit 0, including right after `verify-gate.sh` wrote its trace | test |
| AT-022 | Unwanted | **If** the tree has a change (modified, staged or untracked) outside those prefixes (for example `sdd/bin/x.sh` with only `--permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/`), **then** `avaliador-guard.sh` **shall** exit 1 listing every such path, both sides of a rename, and the commit command; **if** git fails, **then** exit 2; with `SDD_AVALIADOR_GUARD=off`, exit 0 with ⚠️ | test |
| AT-023 | Event-driven | **When** the test output in each of the 5 formats (unittest, pytest, jest/vitest, go, deno) has one failure listed in `sdd/baselines/tests.txt` and one not listed, `test-baseline.sh` **shall** exit 2 naming only the new one; with only listed failures it **shall** exit 0 | test |
| AT-024 | Event-driven | **When** `test-baseline.sh` runs `project.test_cmd` without `--cmd` and without `--touched` and finds no new failure, it **shall** remove each listed id that did not fail and list it; **when** `--cmd` is given or the result is 2 or 3, it **shall** remove nothing (the file stays byte-identical) and print `⚠️ baseline não podado (execução parcial)`; **when** `--touched` is given, it **shall** remove nothing and abort only for new failures whose id cites a test file touched in the diff; **when** `--aceitar <id>` is given, it **shall** add that id without running the tests | test |
| AT-025 | Unwanted | **If** the command exits ≠ 0 and no failure is recognized, or the command is missing, **then** `test-baseline.sh` **shall** exit 3 (`RESULTADO: INCONCLUSIVO`); **if** `test_cmd` is empty and `--cmd` is absent, **then** it **shall** exit 0 with `RESULTADO: PULADO` | test |
| AT-026 | Event-driven | **When** `tests/test_contrato_build_release.py` reads `sdd-build` 2.3.0, the system **shall** find:<br>• the coherence rule for the DEFINE's LLM-prompts flag in step 1;<br>• `sdd/bin/avaliador-guard.sh` in 1.5 and 5d;<br>• `sdd/bin/gate-baseline.sh` for a corrected assertion;<br>• `sdd/bin/test-baseline.sh` in 5b;<br>• `PENDENTE` and `LLM_PROMPTS_BUILD_REPORT.md` in step 6;<br>• one "por quê" item per new rule. | test |
| AT-027 | Event-driven | **When** it reads `sdd-release` 2.4.0, the system **shall** find `report-lint.py --pendente` and `sdd/bin/gate-shell-evidencia.sh` in 0a and in "Gates de ABORTAR" with "≠ 0" as the abort condition, `verify-gate.sh --sem-define` in 0a, one "por quê" per new rule, and the OK block with the same labels, order and single question | test |
| AT-028 | Event-driven | **When** it reads the templates, the system **shall** find:<br>• in `EVIDENCIA.md`: the `rc=$?` recipe, the minimal shape, the 3 avaliador forms, "reprova" for an unrecognized header and `git check-ignore`, with none of `PreToolUse`, `systemMessage`, `.githooks/`;<br>• in `BUILD_REPORT_TEMPLATE.md`: `PENDENTE`;<br>• in `LLM_PROMPTS_BUILD_REPORT.md`: its 5 parts;<br>• in `sdd/config.example.yaml`: `require_avaliacao_layers: 2` under `evidence:`. | test |
| AT-029 | Non-regression | The system **shall continue to** pass the 514 existing tests, `tests/test_agnostico.py`, `skill-lint.py --conversa` on the 17 skills, `playbook-lint.sh --self-test`, `publish-gate.sh` in `ci` mode (G2 over the new fixtures, G3 `MANIFEST.txt`), and the 7-row roadmap with the hooks-only row | test |
| AT-030 | Unwanted | **If** one of the 6 scripts is sabotaged (a rule removed or inverted), **then** at least one named test **shall** fail, and `git checkout` **shall** turn the suite green again, evidenced in `evidence/F7_EVIDENCIA/sabotagem.log` | test |

---

## Clarifications

### Session 2026-10-30

- [x] (Scope) D4: fail-closed sempre, com a forma mínima declarada (BRAINSTORM, decisões 1 e 2). Integrado em Goals e AT-001 a AT-006 e AT-012.
- [x] (Data model) D11: 1 slot, `evidence.require_avaliacao_layers: 2`; os caminhos `sdd/reports/evidence`, `sdd/traces` e `sdd/baselines/tests.txt` ficam fixos (BRAINSTORM, decisão 4). Integrado em AT-005 e AT-013.
- [x] (Integrations) E6: só a regra (`--stdin`) na F7; o adaptador `.claude/settings.json` fica para a F8 (BRAINSTORM, decisão 5). Integrado em AT-010.
- [x] (Constraints) Release `v2.2.8` automática; `sdd-build` 2.3.0 e `sdd-release` 2.4.0 (BRAINSTORM, decisões 11 e 12).
- [x] (Edge cases) **Correção de premissa do checkpoint 2:** "os 425 logs do open, 0 acusações" estava errado. Medida no Define com a regra do privado aceitando `exit=N`: são 245 logs, com 19 linhas acusadas (10 `tail`, 3 `cut`, 2 `head`, 2 `sed`, 2 `tr`), todas com um formatador no último estágio de pipe do `$ <comando>`. **Correção da revisão do DESIGN (nota M1):** a regra é conservadora com comando composto — em pelo menos 7 das 19 o exit gravado não é do formatador (`… | tail -1 && git diff …` 3×, `; exit ${x:-0}`, `chmod` no fim, 2 laços `for … done`); são acusações que um humano rebate lendo o log, não acertos. O critério vira "exatamente as acusações listadas em `corpus-esperado.txt`, e nenhuma outra" (19 + 3 `exit=` vazios que o build achou = 22; 21 depois do ciclo 1 e 22 depois do ciclo 2 da revisão do build, ver Revision History), sobre o corpus **sem** `F7_EVIDENCIA/` (que cresce durante o build) (AT-020). Os logs antigos não são reescritos: a release olha só os logs do diff.
- [x] (Constraints) O `awk` do macOS sai com erro (`multibyte conversion failure`) num log com UTF-8 sem `LC_ALL=C`: todo `awk` sobre log roda com `LC_ALL=C` (Success Criteria).
- [x] (Data model) "Camada tocada": um caminho do File Manifest (linhas `| n | \`caminho\` | …`, coluna 2) conta para a camada `L` quando casa o glob de `layers.L` por `fnmatch`; glob vazio não conta. "Contagem impossível": `layers:` sem glob preenchido, `DESIGN_<F>.md` ausente (com o fallback `_S<n>` → família), sem `## File Manifest`, ou nenhum caminho casa.
- [x] (Data model) O `AVALIACAO` que satisfaz a existência segue `^AVALIACAO_<F>_\d{8}.*\.md$` em `sdd/reviews/`; os nomes `…_20261029-ciclo1.md` das F4–F6 casam.
- [x] (Edge cases) `--touched` não acelera a suíte (o `test_cmd` é do projeto, e o script não sabe rodar um subconjunto): ele filtra. Falha nova fora dos arquivos tocados vira ⚠️, não aborta, e nada sai do baseline.
- [x] (Edge cases) Neste repositório, `sdd/features|handoffs|reports|reviews/` ficam não rastreados de propósito; o avaliador da F7 roda numa worktree destacada, e o guard, se chamado aqui, recebe os 4 prefixos `--permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/` — nunca `sdd/`, que liberaria `sdd/bin/`, `sdd/templates/` e `sdd/fixtures/` sem commit (nota M2 da revisão do DESIGN). `sdd/traces/` é permitido por default: o trace do gate é gravado antes do 5d e não pode obrigar a commitar a cada build (nota H2). Num projeto do usuário, as specs são versionadas e o default basta.
- [x] (UX flow) Não há tela; o "fluxo" é a saída de cada script (`🛑`/`⚠️`, `RESULTADO:`, `→`) e o texto das skills. A camada de conversa da F4 cobre o que o aluno vê.
- [x] (Constraints) O `cmd` do gate roda numa cópia por `git archive HEAD`, sem `.git`, sem `sdd/reports/` nem `sdd/reviews/`. AT-011 e AT-020 (corpus), a baseline vermelha, `check-versions` e AT-030 ficam fora do `cmd`, com log em `evidence/F7_EVIDENCIA/`.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

O gate só enxerga o que está commitado (`git archive HEAD`), então o Build commita na branch antes de rodar. `PUBLISH_GATE_MODE=ci` é necessário porque o modo padrão exige a camada privada de padrões. A suíte roda no piso (Python 3.9 do macOS, bash 3.2) e cobre AT-001 a AT-010, AT-012 a AT-019, a parte de AT-020 sobre as fixtures, AT-021 a AT-029 e a parte de AT-016 que compara trace ligado com `SDD_TRACE=off`. A comparação com o script da `v2.2.7` fica num log (`saidas-v2.2.7.log`), porque precisa da tag.

Ficam fora do `cmd`, com log em `evidence/F7_EVIDENCIA/`, porque precisam de `sdd/reports/`, de `.git` ou da tag: AT-011, o corpus de AT-020, AT-030, `check-versions`, a baseline vermelha na `v2.2.7` e a Release.

---

## Out of Scope

- O adaptador `.claude/settings.json` (Write/Edit e despacho do avaliador), os hooks de git `pre-commit`/`pre-push`, `core.hooksPath` e a D10 (F8).
- A data de corte para relatório antigo; a reescrita dos logs antigos acusados; a medição sobre os 316 relatórios do privado.
- Os slots `evidence.dir`, `evidence.traces_dir` e `tests.baseline_file`; formatos de teste além dos 5; `gate-shell-evidencia.sh --all`; o trace gravado pelo curator (F14).
- `camadas.tsv`, a propagação do rc 3 do deno e as marcas `[auto]`/`[Dn]`; o encadeamento e o `exit 40` (F9); a revisão adversarial e o registry (F10/F11).
- Regenerar o sdd-starter; alterar o sdd-starter ou o repositório privado.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash ≥ 3.2 e Python ≥ 3.9 só com stdlib, rodados com `python3 -B`; testes sem rede | Nada de `mapfile`, `declare -A`, `${x^^}`, `<<<` com array, `read -d ''`; `rm -rf` só com `"${X:?}"` |
| Technical | `report-lint.py` vai para o projeto do usuário: exits 0/1/64 e saída com `🛑`/`⚠️`, `RESULTADO:` e `→` | As regras novas reusam `secoes()`, `linhas_de_tabela()` e `ler_layers_sql()` (generalizada para todas as camadas) |
| Technical | `tests/test_agnostico.py` e `tests/test_correcoes_w0.py` varrem skills, templates e `EVIDENCIA.md` | Nenhum `PreToolUse`, `systemMessage`, `.githooks/`, "pelo hook" ou nome de ferramenta de um agente só |
| Technical | Integridade do CI em `.agents/skills/`: nenhum Unicode invisível e nenhum `curl … \| sh` literal | Conferir os code points das 2 skills depois de escrever |
| Technical | G2 do publish-gate sobre a árvore inteira | Fixtures sem CPF/CNPJ/telefone/e-mail real, sem 11+ dígitos seguidos (timestamps montados em tempo de execução nos testes) e sem `/Users/<nome>/` |
| Technical | G3: `MANIFEST.txt` em ordem `LC_ALL=C`; `git add` por nome | Os scripts, fixtures, fragmento e testes novos entram no mesmo commit; `sdd/features|handoffs|reports|reviews|traces/` ficam fora |
| Technical | Camada da F4/F5 e "Por que cada regra existe" (F6) são contrato | O texto novo entra nos passos e na seção "por quê", sem tocar no bloco comum nem no Status |
| Technical | `SKILL.md` ≤ 500 linhas | `sdd-build` tem 232, `sdd-release` 297 |
| Technical | `verify-gate.sh` com `set -uo pipefail` e `trap` | O trace grava num `trap … EXIT` que preserva o exit original |
| Other | Push em `main` só com o OK do Roberto citando "sdd-open", depois de PR com CI verde em ubuntu e macOS | A Release `v2.2.8` depende desse OK |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/report-lint.py`, `sdd/bin/verify-gate.sh`; novos `sdd/bin/gate-baseline.sh`, `gate-shell-evidencia.sh`, `avaliador-guard.sh`, `test-baseline.sh`; `sdd/config.example.yaml`; `sdd/templates/fragments/EVIDENCIA.md`, `LLM_PROMPTS_BUILD_REPORT.md` (novo), `sdd/templates/BUILD_REPORT_TEMPLATE.md`; `.agents/skills/sdd-build/SKILL.md`, `.agents/skills/sdd-release/SKILL.md`; `sdd/fixtures/evidencia/` (novo); `tests/`; `docs/roadmap.md`, `docs/pt-BR/roadmap.md`; `MANIFEST.txt` | Fontes no privado (`origin/main`, só leitura): `.githooks/claude-build-report-guard.py`, `claude-avaliador-guard.py`, `scripts/gates/avaliador-pendente-guard.sh`, `gate-baseline.sh`, `gate-shell-evidencia.sh`, `scripts/verify-gate.sh` |
| **KB Domains** | nenhum | O open não tem `sdd/kb/` próprio |
| **IaC Impact** | None | O push em `main` publica a Release sozinho, porque toca `sdd/bin/**`, `sdd/templates/**`, `sdd/fixtures/**`, `sdd/config.example.yaml` e `.agents/skills/**` |
| **LLM Prompts** | false | Scripts de lint e gate e texto de orquestração lido pelo agente de desenvolvimento; o fragmento `LLM_PROMPTS_BUILD_REPORT.md` é um molde de relatório, não um prompt de runtime |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os 514 testes passam no piso em `1c9bbc7` | O Build partiria de base vermelha | yes; reconferido no início desta sessão |
| A-002 | O runner do open ecoa `(rc=N)` em `GATE VERMELHO` como o do privado, o que permite ao `gate-baseline.sh` separar avaliação de crash | O baseline confundiria crash com dentes | yes; `verify-gate.sh:196` imprime `… NÃO satisfeito (rc=${RC})` |
| A-003 | Os 5 formatos de teste têm marcadores de falha estáveis entre versões recentes (unittest 3.9–3.13, pytest 7–8, jest 29/vitest 1–2, go 1.2x, deno 1–2) | Um formato novo cairia em 3 (inconclusivo), nunca em verde | no; as fixtures fixam uma saída por formato |
| A-004 | Nenhum teste existente roda `verify-gate.sh` na raiz do repositório sem sandbox | O trace sujaria `sdd/traces/` durante a suíte | no; conferir no Design |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---:|---|
| Problem | 3 | Sete pontos fail-open, com número medido no próprio open (5 de 8 relatórios, 19 logs) e a fonte do privado |
| Users | 3 | Quem constrói, quem publica e o mantenedor da F15 |
| Goals | 3 | Cada script com interface, exits e caminhos; versões das 2 skills |
| Success | 3 | Todo critério é um exit, uma contagem ou um log |
| Scope | 2 | Os formatos de saída de teste (A-003) dependem de fixtures, não de garantia dos frameworks |
| **Total** | **14/15** | |

Minimum to proceed: **12/15**.

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.5 | 2026-10-30 | SDD Build by RDD | Ciclo 2 da revisão do build (LOW-E): `$` sozinho pega o comando da linha seguinte, comentário com um espaço não absolve, `(tail)`, `command tail` e `env … sort` são acusados, qualquer `<var>=$?` antes do pipe absolve. O corpus volta a 22: entra `F6_DOCS/AVAL-manifest.log:8`, falso positivo conservador de comando composto (`… \| LC_ALL=C sort) && …` dentro de `diff <(…)`), da mesma família já declarada |
| 1.4 | 2026-10-30 | SDD Build by RDD | Ciclo 1 da revisão do build (LOW-6): `|&` e `VAR=valor formatador` passam a ser acusados, `[exit= ]` conta como vazio e `PIPESTATUS` em qualquer ponto do comando absolve (no zsh, a linha sai vazia e a regra do vazio pega); o corpus cai de 22 para 21 (sai o falso positivo `F4_CONVERSA/AVAL-at013-uso-e-erros.log:28`) |
| 1.3 | 2026-10-30 | SDD Build by RDD | Drift do build: o corpus tem também 3 linhas `exit=` vazias sem colchete (gravadas pelo `${PIPESTATUS[0]}` vazio do zsh em F3 e F6), que a regra de `[exit=]` não via; o teste 19 passa a cobrir `exit=` vazio com e sem colchete, e o teste 20 conta 22 = 19 + 3 |
| 1.2 | 2026-10-30 | SDD Design by RDD | Revisão de contexto fresco do DESIGN (`REVISAO_DESIGN_F7_EVIDENCIA_20261030.md`), 5 ajustes aceitos: o baseline do gate exige a linha `🔴` ou um marcador de asserção (o `(rc=N)` sozinho sai 3); corpus sem `F7_EVIDENCIA/`, com as 19 linhas listadas e a regra declarada conservadora; guard permite `sdd/traces/` e usa 4 prefixos aqui; poda do baseline só na execução completa; release aborta com qualquer exit ≠ 0 |
| 1.1 | 2026-10-30 | SDD Design by RDD | Teste 13: o trace começa depois de achar a raiz e grava o exit antes do remapeamento do `--strict`. Teste 16: comparação com `SDD_TRACE=off` na suíte e com a `v2.2.7` em log. Teste 17 e o Goal: `--sobrepor` no `gate-baseline.sh` (sem ele, o gate novo não existe na base e tudo sai 3). Teste 24: `--aceitar` não roda a suíte |
| 1.0 | 2026-10-30 | SDD Define by RDD | Versão inicial a partir de `BRAINSTORM_F7_EVIDENCIA.md`, com a correção do corpus de logs (19 acusações, não 0) |

---

## Next Step

Execute o **SDD Design by RDD**.
