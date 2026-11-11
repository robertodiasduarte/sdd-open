# BUILD REPORT: F16 — Ambiente agnóstico e proativo

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16_AMBIENTE |
| **Date** | 2026-11-11 |
| **Author** | build-agent (worktree `sdd-open-f16-ambiente`, branch `feat/f16-ambiente`, de `36d0454` = `v2.10.1`) |
| **DEFINE** | [DEFINE_F16_AMBIENTE.md](../features/DEFINE_F16_AMBIENTE.md) v1.3 |
| **DESIGN** | [DESIGN_F16_AMBIENTE.md](../features/DESIGN_F16_AMBIENTE.md) v1.4 |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|---|---|
| **Tasks Completed** | 22/22 linhas do manifest (a 19, `test_matriz_new_session.py`, só confere: o contrato do `--frente` não mudou) |
| **Files Created** | 5 (`sdd/bin/lib/python.sh`, `tests/test_python_resolver.py`, `tests/test_windows.py`, `tests/test_f16_textos.py`, `.gitignore`) ; ~45 alterados |
| **Commits** | passo 0: `e632432` (curadoria), `f6241f4` (sobras da F19), `58d1bd2` (INV-002) · F16: `416c0d5` (job Windows e README), `3db9bfd` (resolvedor), `e375bad` (3 skills), `6c89cb8` e `2f556fb` (job no caminho do aluno), `30b5448` (versões fixadas), `0a68960` (marca de classe, UTF-8 nos testes), `d556851` (rodada 3 e avaliador ciclo 1), `28caf3a` (saída UTF-8 do Python) · na release: `1bf3b1f` (raio de impacto: o `python3` herdado), `c33ea5c` (teto do macOS 60 → 75), `9ab4541` (pergunta do editor, pedido do Roberto), `69b7f6b` (rodada 5: a escolha no git config) |
| **Tests Passing** | exit 0 em `69b7f6b` (o commit publicado): 1.941 testes em 34 min, 1 pulado (`evidence/F16_AMBIENTE/VERIFY-GATE-69b7f6b.log`; antes, em `28caf3a`, `1bf3b1f` e `c33ea5c`); a contagem subiu de 1.867 na partida |
| **Skills** | `sdd-checar-ambiente` 1.5.0, `sdd-iniciar-repo` 1.2.0, `sdd-new-session` 1.5.0 (`check-versions.py --base v2.10.1` VERDE) |

**Seleção de modo:** default (um autor; arquivos acoplados: o resolvedor e os 16 scripts que o leem, as 2 cópias do `gh_estado`, os 3 blocos de instalação). Escolhido sem perguntar ao Roberto, ao contrário do que a skill pede: registro honesto. Recomendação seria a mesma (empate ⇒ default).

**Revisão do DESIGN:** exigida (`sdd-fluxo.sh review-design` sai 0: 4 arquivos novos e uma linha em superfície de segurança); 2 rodadas antes do código, registradas no Advisor Ledger do DESIGN e no ledger da revisão.

---

## Landmines lidas no build

| Fonte | Superfície | Veredito |
|---|---|---|
| LM-001 | testes que rodam os scripts com stubs dos dois lados | ✔ tratado: `checar.sh`, `inventario.sh` e o resolvedor rodam de verdade; 4 sabotagens mortas |
| LM-002 | linha de base vermelha | ✔ tratado: `BASELINE-vermelho-W1.log`, `-W2.log`, `-rodada3.log`; e a asserção de contagem que pegou o teste vazio do `test_f16_textos` |
| LM-003 | commit antes de cada revisão | ✔ tratado: as 3 rodadas sobre árvore commitada; `diff_sha256` no ledger |
| LM-005 | heurística sobre texto livre | ✔ tratado: a varredura de pulos lê os tokens do Python (texto entre aspas não conta); as cópias do `gh_estado` têm teste de identidade |
| LM-006 | script que só roda com `.git` | ✔ tratado: o Verify Gate e as sabotagens rodam em cópia de `git archive`; o `--editor` não usa git (teste fora de repositório) |
| LM-008 | `limit_remaining` não é saldo | ✔ tratado: saldo lido em `/credits` antes de cada rodada paga (US$ 0,07 na 1ª; US$ 20,07 depois da recarga) |
| LM-009 | sabotagem com `git checkout` | ✔ tratado: mutantes em cópia de `git archive`, com os consertos commitados |
| LM-010 | engine paga que estoura o teto | ✔ tratado: sem 2º revisor pago (`--no-revisor2`) |
| LM-011 | cenário de comportamento nunca executado | ✔ tratado em parte: a prova manual do `open -a "Visual Studio Code"` rodou neste Mac (`MANUAL-mac-open-a.log`); o modo terminal da `sdd-new-session` numa sessão real **não** rodou (fica em pendências) |
| LM-012 | número longo barrado pelo `publish-gate` | mordeu: o id de um run do CI (11 dígitos) num comentário dos workflows; o Verify Gate de `6c89cb8` saiu vermelho por isso (`VERIFY-GATE-6c89cb8.log`), conserto em `2f556fb` |
| LM-013 | edição por corte apaga testes | ✔ tratado: contagem de `def test_` antes e depois de cada edição por script; uma queda (7 → 6 no `test_windows.py`) era um literal `"def test_"` de uma asserção antiga, nenhum teste sumiu |

---

## Candidatos ao playbook

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `text=True` `subprocess` `encoding` `cp1252` `Windows`
regra: No Windows, `subprocess.run(..., text=True)` sem `encoding` decodifica a saída com a codificação do sistema (cp1252): o "✅ Pronto" de um script bash chega embaralhado e o teste falha com a saída certa (no job do caminho do aluno, 81 de 136 quebras tinham essa causa). **Do instead:** todo `subprocess` de teste que lê texto passa `encoding="utf-8", errors="replace"`, como o `tests/apoio.py` já fazia.
evidencia: sdd/reports/evidence/F16_AMBIENTE/windows/run-2f556fb-caminho-do-aluno.log
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `PYTHONIOENCODING` `pipe` `Git Bash` `stdout`
regra: O Python do Windows, com a saída num pipe (o Git Bash do aluno é um pipe), escreve em cp1252: o "ç" e o ✅ dos scripts de `sdd/bin` saem trocados ou com erro de codificação, e nada no macOS ou no Linux mostra isso. **Do instead:** quem chama Python por bash exporta `PYTHONIOENCODING=utf-8` (sem passar por cima de um valor que já exista), como faz `sdd/bin/lib/python.sh`, e um teste imprime "ação" pelo Python e confere em UTF-8.
evidencia: sdd/reports/evidence/F16_AMBIENTE/windows/run-d556851-caminho-do-aluno.log
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `set -m` `kill -- -` `grupo de processos` `teto` `Windows`
regra: O vigia de teto que mata um grupo de processos (`set -m` + `kill -- -<pgid>`) não corta nada no Git Bash do Windows: o `checar.sh` com a rede pendurada passou de 60 s nos 5 testes de rede, onde o teto é 10 s. **Do instead:** teto de tempo que precisa valer no Windows não depende de sinal para grupo; até existir um que valha, o teste fica pulado por `SEM_SINAL` e o defeito fica registrado como pendência, nunca como verde.
evidencia: sdd/reports/evidence/F16_AMBIENTE/windows/run-0a68960-caminho-do-aluno.log
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `fallback` `degradação graciosa` `${0%/*}` `caminho do Windows`
regra: Uma saída graciosa ("sem a biblioteca, vale a guarda antiga") esconde o caminho errado que a ativou: chamado com caminho do Windows (`C:\…\x.sh`), o script não achava `/` no `$0`, caía calado na guarda antiga e o resolvedor nem era lido; os testes locais, com `/`, nunca passavam por ali. **Do instead:** todo fallback silencioso ganha um teste que chama o caminho real pela forma que a plataforma usa (aqui, o job do Windows) e confere que o caminho principal rodou, não só que o resultado saiu.
evidencia: sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md
ficha: —
mordeu_antes: —
>>>

<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `publish-gate` `[0-9]{11,}` `run id` `workflow`
regra: O id de um run do GitHub Actions tem 11 dígitos e é barrado pelo `publish-gate` como número longo, como o SHA-256 da LM-012: citado num comentário dos workflows, derrubou o Verify Gate inteiro em 2 s. **Do instead:** em texto que vai para o pacote, cite o commit (7 caracteres) ou o PR, nunca o id do run; o id fica nos documentos SDD, fora do pacote.
evidencia: sdd/reports/evidence/F16_AMBIENTE/VERIFY-GATE-6c89cb8.log
ficha: —
mordeu_antes: LM-012
>>>

---

## Files Created

| Arquivo | O que é |
|---|---|
| `sdd/bin/lib/python.sh` | resolvedor: `python3`, `SDD_PYTHON`, `python`, `py -3`; calço no PATH; `sdd_python_pronto` e `sdd_python_exigir`; `PYTHONIOENCODING=utf-8` |
| `tests/test_python_resolver.py` | 23 casos: escolha, parada com a causa certa, calço (`exec`, `env`, `xargs`, `bash -c`), limpeza, saída UTF-8, rodada 3 |
| `tests/test_windows.py` | varredura de pulos por tokens, os 5 achados guardados, `.gitattributes`, stdout do curator em bytes |
| `tests/test_f16_textos.py` | blocos de instalação iguais nas 3 skills, cópias do `gh_estado` iguais, versões, Passo 0, modo terminal, avisos |
| `.gitignore` | `__pycache__/`, `*.pyc`, `sdd/reports/reviews/`, `sdd/traces/` (passo 0) |

Alterados (principais): `checar.sh` e `SKILL.md` da `sdd-checar-ambiente`; `inventario.sh` e `SKILL.md` da `sdd-iniciar-repo`; `SKILL.md`
da `sdd-new-session`; 14 scripts de `sdd/bin` e `bin/sdd-open.sh` (leitura do resolvedor, guardas); os 2 workflows (job Windows);
README e quickstart nos 2 idiomas; `.gitattributes`; `tests/apoio.py` (constantes de pulo, `caminho_bash`, `caminho_nativo`);
`test_checar.py`, `test_inventario.py`, `test_release_workflow.py`, `test_sdd_open.py` e os testes com pulo de plataforma; `MANIFEST.txt`.

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F16_AMBIENTE.md`) | exit 0 em `69b7f6b` (o commit publicado): 1.941 testes em 34 min, 1 pulado (`evidence/F16_AMBIENTE/VERIFY-GATE-69b7f6b.log`; antes, em `28caf3a`, `1bf3b1f` e `c33ea5c`); a contagem subiu de 1.867 na partida |
| `publish-gate.sh` (ci) em cópia de `git archive` | exit 0 em cada push |
| `check-versions.py --base v2.10.1` | VERDE |
| `skill-lint.py --conversa` nas 20 skills | ok |
| `sdd-decisoes-lint.sh --sites` | 30 perguntas em 25 arquivos, todas marcadas |
| Sabotagens (`SABOTAGEM.log`) | 4 de 4 mortas: gh ausente vira ok; o app do macOS some; o atalho da Store é aceito; o README afirma o Windows |
| Prova manual neste Mac (`MANUAL-mac-open-a.log`) | `open -a "Visual Studio Code"` abriu a pasta da frente, exit 0, processo em 1 s |
| CI do PR #25, Ubuntu e macOS | run de `28caf3a` no PR #25: `gate` (Ubuntu) verde em 19m38s, Windows (caminho do aluno) verde em 4m37s, macOS (piso) verde em 47m19s, teto 60 |

**Windows (Git Bash + Python nativo), o que a frente mediu:**

| Medição | Commit | Escopo | Resultado |
|---|---|---|---|
| 1ª | `416c0d5` | suíte inteira | cancelada no teto de 90 min com 282 de ~1.900 testes feitos (~19 s por teste): 126 ok, 145 falhas, 11 erros; o publish-gate passou |
| 2ª | `2f556fb` | caminho do aluno (5 módulos) | 136 testes em 9,4 min: 63 ok, 47 falhas, 34 erros (81 por decodificação cp1252 nos testes) |
| 3ª | `0a68960` | caminho do aluno | 136 testes: 116 ok, 11 falhas, 9 erros |
| 4ª | `d556851` | caminho do aluno | 143 testes em 4,1 min: 131 ok, 8 pulados, 4 falhas (3 de caminho no teste, 1 de saída cp1252 do Python, defeito do produto) |
| 5ª | `28caf3a` | caminho do aluno | **144 testes em 4,0 min: 136 ok, 8 pulados com motivo, 0 falhas** (`windows/run-28caf3a-caminho-do-aluno.log`) |

Pulados no Windows, cada um por constante de `tests/apoio.py`: 5 testes de rede pendurada do `checar` (`SEM_SINAL`: o vigia não mata
o grupo de processos lá — defeito do produto, pendência para a F16W) e 3 do inventário com nome de arquivo com aspas ou terminado em
espaço (`SEM_NOME_ESPECIAL`: o Windows não aceita esses nomes).

---

## Issues Encountered

- **208 testes caíram** quando os scripts passaram a ler a biblioteca: testes que copiam um script sozinho, PATH sem `dirname`, e
  `set -e` com `.` de arquivo ausente. A leitura passou a usar só builtins, com `if [ -f … ]` e a guarda antiga como saída graciosa.
- **O `gh_estado` não respeitava o teto:** o teste com o `gh` pendurado esperou 30 s, porque o filho do processo morto segurava a
  saída. Passou a rodar num grupo de processos, como o `ls-remote` do `checar.sh`.
- **INV-002 apontava um vigia que só existe no pacote** (`tests/test_eval_revisores.py`): o `init` recusava instalar as invariantes
  num projeto. O vigia passou a ser `sdd/bin/ledger-revisao-lint.sh` (`58d1bd2`).
- **O teste de identidade das cópias do `gh_estado` não comparava nada:** o cabeçalho citava o marcador de fim no meio do texto. A
  asserção de que o bloco tem as funções pegou; o marcador passou a ser lido no começo da linha.
- **O Windows inteiro não cabe nesta frente:** a 1ª medição bateu a regra de parada do brainstorm, e o Roberto decidiu (2026-11-11):
  o job roda o caminho do aluno; o porte da suíte é a frente F16W.
- **Um log do avaliador (ciclo 1) gravou o exit do `head`, não o do comando:** o `gate-shell-evidencia.sh` da release o acusou;
  ele foi preservado como `AVAL-AT003-manual-mac.aval.txt`, como a F19 fez com os dela (a evidência do avaliador não é editada). A prova manual do AT-003
  é `MANUAL-mac-open-a.log`, que grava o exit do próprio comando.
- **O raio de impacto da release achou uma quebra (0b, guarda de Python):** o resolvedor aceitava `SDD_PYTHON_RESOLVIDO=python3`
  herdado sem conferir o PATH do filho; debaixo do `test-baseline.sh`, do `verify-gate.sh` (pelo `sdd-drive`) e do `slot.sh`, os testes
  "sem python3" saíam 127 em vez de 64. Conserto em `1bf3b1f` (o valor herdado só vale com `command -v python3`; o `Sandbox` não herda
  a variável), com linha de base vermelha (`BASELINE-vermelho-raio.log`); evidência em `RAIO-de-impacto.md`.
- **O `gh run view --log` não entrega log com o run em andamento:** os logs do Windows vieram de `gh api …/actions/jobs/<id>/logs`.

---

## Deviations from Design

| DESIGN | O que foi feito | Por quê |
|---|---|---|
| Decision 5: `continue-on-error: true` | sem `continue-on-error`; o job fica só fora do `needs:` | `tests/test_release_workflow.py` proíbe mascarar falha, e fora do `needs:` já não segura a Release (DESIGN v1.2) |
| Decision 5: suíte inteira, teto 90 min | caminho do aluno, teto 30 min | 1ª medição e decisão do Roberto (Decision 8, DESIGN v1.4) |
| Decision 2 v1.1: parar na carga | a carga nunca para; `sdd_python_pronto` nas guardas | rodada 2, R2 (DESIGN v1.2) |
| Components: `instalar_git` | não feito | a mensagem de git ausente do `checar.sh` já existia e ficou |
| Manifest 19: modificar `test_matriz_new_session.py` | só a versão fixada | o contrato do `--frente` não mudou; o modo terminal está em `test_f16_textos.py` |
| Decision 4: a `sdd-new-session` escolhe o 1º editor achado | pergunta o padrão na 1ª vez (`checar.sh --editores`; `terminal:claude`, `terminal:codex`) e grava em `git config --local sdd.editor` | pedido do Roberto antes da release; a rodada 5 levou a resposta do slot para o `git config` (DESIGN v1.5 e v1.6) |
| — | `PYTHONIOENCODING=utf-8` no resolvedor | medido no Windows (4ª medição), não estava no DESIGN |
| — | `${0//\\//}` antes de achar a pasta do script | medido no Windows: chamado com caminho `C:\…`, a carga caía calada na guarda antiga |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o repositório do pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 2 · achados: 6 no ciclo 1 (NEEDS_WORK: 1 alto, 2 médios, 3 baixos, todos resolvidos), 2 baixos no ciclo 2 · `AVALIACAO_F16_AMBIENTE_20261111-0905-ciclo2.md` (ciclo 1: `AVALIACAO_F16_AMBIENTE_20261111-0520-ciclo1.md`)

O ciclo 2 provou os 9 ATs por execução (PASS em cada um) e matou 5 mutantes próprios. Os 3 recibos que ele pediu não são de AT:
(1) o job macOS do run de `28caf3a`, em andamento na hora dele: verde em 47m19s (teto 60: folga de 12 min, conferida de novo antes da tag); (2) este relatório com a contagem do Windows: está na
tabela "Windows" acima; (3) a Release com o `SHA256SUMS.txt`: critério de sucesso, da `sdd-release`.

Os 2 achados do ciclo 2: **A** — o pulo `SEM_SINAL` esconde um defeito do pacote, não só um recurso ausente: no Windows, um ssh ou
askpass pendurado pode passar do teto no `checar.sh` e no pré-voo `--frente`; está nas pendências como 🐛 e vai para o escopo da F16W
como defeito conhecido. **B** — a limpeza do calço apaga pela idade da pasta, sem conferir se o processo dono ainda vive: um processo
de mais de 24 h que chame `python3` depois disso perderia o calço; limite declarado (raro: só o `sdd-drive` em laço chegaria lá).

---

## Advisor Ledger

**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md` (22 linhas, 5 rodadas; `ledger-revisao-lint.sh` verde; loop: PRONTO na rodada 3 de 3 e nas de fecho)

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (DESIGN) | `EXTERNAL_REVIEW_20261110-221223` | uma engine só (claude revisou e auditou), saldo da OpenRouter em US$ 0,07 | 1 grave, 4 médios | 5 aplicados |
| 2 (DESIGN) | `EXTERNAL_REVIEW_20261110-221917` | claude + `openrouter` (qwen), depois da recarga | 2 médios, 2 leves | 4 aplicados |
| 3 (código, diff inteiro) | `EXTERNAL_REVIEW_20261111-044013` | claude + `openrouter` (qwen) | 4 médios, 3 leves | 7 aplicados (1 com dano: R1, o laço do calço) |
| 4 (fecho, acima do teto, decisão do Roberto) | `EXTERNAL_REVIEW_20261111-071016` | claude + `openrouter` (qwen), sobre `1bf3b1f` | 3 médios, 1 leve; 0 graves | 2 rebatidos com evidência (R2, R3), 2 pendências (R1, R4) |
| 5 (só o delta desde a 4, decisão do Roberto) | `EXTERNAL_REVIEW_20261111-084600` | claude + `openrouter` (qwen), `--base 1bf3b1f`, sobre `9ab4541` | 1 médio, 1 leve | 2 aplicados por decisão do Roberto (`69b7f6b`): a escolha do editor no `git config`, o texto da opção recomendada |

Na release, a rodada 4 de fecho cobriu tudo até `1bf3b1f` (`--conferir` CONFERE com o 2º revisor dispensado: codex sem cota, gemini sem credencial, 2º revisor pago evitado pela LM-010); depois dela, o teto do macOS (`c33ea5c`) e o ajuste do editor (`9ab4541`), cobertos pela rodada 5 (só o delta); depois da 5, só o conserto de texto dos achados dela (`69b7f6b`), registrado como dispensa no ledger da release. Antes da rodada 4, não tinham passado por revisão externa (vieram depois da rodada 3): os consertos dos 7 achados da rodada 3, os do ciclo 1 do
avaliador, o `${0//\\//}` e o `PYTHONIOENCODING`, os dois achados medidos no Windows. Quem os cobre: os testes novos com linha de
base vermelha, o job Windows e o ciclo 2 do avaliador.

**Medidor (`bash sdd/bin/eval-revisores.sh`), 2ª frente com dano marcado:** `evidence/F16_AMBIENTE/EVAL-REVISORES.log` (exit 0 MEDIDO, 3 pastas, 1 ledger, fora da conta: 0)

| Papel | Engine (modelo) | Cobrança | Rodadas | Falhas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | Fora de escopo | Sem classificar | Pago por dano | Nominal por dano | AGREE |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-opus-5-5) | assinatura | 3 | 0 | 0.0000 | 3.3038 | 16 | 16 de 16 | 1 de 16 | 0 de 16 | 0 de 16 | 0 de 16 | 0.0000 | 3.3038 | — |
| auditor | claude (claude-opus-5-5) | assinatura | 1 | 0 | 0.0000 | 0.6528 | 0 | 0 | 0 | 0 | 0 | 0 | — | — | 40.0% (2 de 5) |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 2 | 0 | 0.0596 | 0.0596 | 0 | 0 | 0 | 0 | 0 | 0 | — | — | 100.0% (11 de 11) |

Leitura, com a amostra pequena que o medidor avisa: o revisor (por assinatura) achou os 16 aplicados, 1 com dano; o auditor pago
custou US$ 0,06 nas 2 rodadas e concordou com tudo (11 de 11); a mesma engine auditando a si mesma concordou com 2 de 5 na rodada 1.

---

## Drift detectado

Nenhum: a frente não tem prompt de produção (`LLM Prompts: false`; re-check sem provedor, `prompt` de runtime nem `**/prompts/**`).

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE v1.3) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | `checar.sh` sem `gh` ⇒ ⚠️ com o comando do sistema e rc 0; `--frente` não cita o `gh` | true | `evidence/F16_AMBIENTE/AT-001.log` |
| AT-002 | `gh auth status` com teto; deslogado ⇒ ⚠️ `gh auth login`; teto ⇒ "não deu para conferir"; fora do GitHub, nada | true | `evidence/F16_AMBIENTE/AT-002.log` |
| AT-003 | detecção de editor em 2 camadas, `open -a` no macOS, `.cmd` no Windows, resumo cita o editor | true | `evidence/F16_AMBIENTE/AT-003.log` |
| AT-004 | `inventario.sh` imprime 1 linha `gh:` com 4 valores; Passo 0 avisa sem parar; Passo 6 retoma | true | `evidence/F16_AMBIENTE/AT-004.log` |
| AT-005 | pergunta o editor padrão uma vez e grava no `git config`; modo terminal (também por `terminal:<agente>`), aviso final em 2 formas, slot como está, tabela de instalação igual, agnóstico | true | `evidence/F16_AMBIENTE/AT-005.log` |
| AT-006 | o 1º Python que roda e é ≥ 3.9; atalho da Store pulado; nenhum ⇒ a causa certa, sem traceback | true | `evidence/F16_AMBIENTE/AT-006.log` |
| AT-007 | job `testes-windows` nos 2 workflows, caminho do aluno, fora do `needs:`; as 4 frases dizem "sem teste automático" | true | `evidence/F16_AMBIENTE/AT-007.log` |
| AT-008 | pulo por recurso só pela constante; os 5 achados guardados com o teste de cada um | true | `evidence/F16_AMBIENTE/AT-008.log` |
| AT-009 | shall continue to: `--frente` e a matriz, jobs Ubuntu/macOS e tetos, `init`, suíte no bash 3.2 | true | `evidence/F16_AMBIENTE/AT-009.log` |

**Verify Gate:** exit 0 em `69b7f6b` (o commit publicado): 1.941 testes em 34 min, 1 pulado (`evidence/F16_AMBIENTE/VERIFY-GATE-69b7f6b.log`; antes, em `28caf3a`, `1bf3b1f` e `c33ea5c`); a contagem subiu de 1.867 na partida

---

## Final Status

### Overall: ✅ COMPLETE

- [x] 22 linhas do manifest
- [x] Verify Gate verde, linhas de base vermelhas, 4 sabotagens mortas
- [x] ATs com evidência abrível
- [x] revisão: 5 rodadas (a 1ª com uma engine só; a 4ª e a 5ª, de fecho, acima do teto por decisão do Roberto), loop PRONTO
- [x] avaliador de contexto novo: PASS_PENDENTE_RECIBO no ciclo 2 (o último do teto), todos os ATs PASS; recibos acima
- [x] Pronto para a `sdd-release`, com as ressalvas abaixo

**Pendências que saem desta frente:**
- 🐛 **Teto do `ls-remote` no Windows (defeito do pacote, avaliador ciclo 2, achado A):** o vigia não mata o grupo de processos no
  Git Bash; o `checar.sh` e o pré-voo `--frente`, com ssh, askpass ou rede pendurados, podem passar de 60 s (5 testes pulados por
  `SEM_SINAL`). Prioridade da F16W.
- **Limpeza do calço pela idade (avaliador ciclo 2, achado B):** processo de mais de 24 h perderia o calço; limite declarado.
- **F16W, porte da suíte inteira ao Windows:** a 1ª medição é o ponto de partida (282 de ~1.900 em 90 min); 4 dos 5 achados guardados
  (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`) só são medidos lá.
- **Piso do Windows:** decidido pelo Roberto em 2026-11-11, com estes números: continua "sem teste automático" até a F16W.
- **Modo terminal da `sdd-new-session` numa sessão real:** não executado (LM-011); o roteiro está no ciclo 1 do avaliador.
- **Rodada 4, R1:** com uma `sdd-checar-ambiente` anterior à 1.5.0 instalada, `checar.sh --editor` cai no modo normal e a 1ª linha
  do diagnóstico iria para o slot `editor`; a `sdd-new-session` deve conferir a versão (ou o formato da linha).
- **Rodada 4, R4 e raio de impacto, pontos menores:** o aviso "dito uma vez" pode repetir no `doctor`; o loop de deriva do `doctor`
  não compara `sdd/bin/lib/python.sh`; `governanca-fronteira.sh` chama `sdd_python_exigir` antes do `case` de uso (sem Python, até
  `--help` sai 64); `docs-extract-decisions.sh` sai 64 com `RESULTADO: PAROU` em vez de `ERRO DE USO`; o guia do aluno não cita a
  linha `gh:` do inventário.
- **Skills com `python3` no texto** (`python3 sdd/bin/skill-lint.py …`): no Windows o aluno digita o atalho da Store; o resolvedor só vale
  para os scripts. Fica para a F16W.

---

## Next Step

**If Complete:** `/sdd-release F16_AMBIENTE` — bump minor do pacote (`v2.11.0`: 3 skills com funcionalidade nova)
