# DESIGN: F16 — Ambiente agnóstico e proativo

> Como as 3 skills de entrada passam a descobrir `gh`, login e editor cedo, e como o pacote passa a rodar no Windows (Git Bash + Python nativo) medindo primeiro.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16_AMBIENTE |
| **Date** | 2026-11-10 |
| **Author** | design-agent |
| **DEFINE** | `sdd/features/DEFINE_F16_AMBIENTE.md` (v1.3) |
| **Status** | Ready for Build |
| **LLM Prompts** | false (re-check: nenhum provedor, prompt de produção ou caminho `**/prompts/**` no escopo) |

---

## Architecture Overview

```text
                         ┌────────────────────────── sdd-checar-ambiente/scripts/checar.sh ─────────────────────────┐
 aluno ─▶ checar.sh ───▶ │ 3. git/remoto ── alcance() [ls-remote, 10 s] ┐                                         │
  (normal)               │                  publico()  [curl, 3 s]      ├─ em paralelo: teto = o maior          │
                         │                  gh_estado() [gh auth, 10 s] ┘  (só normal; GitHub ou sem remoto)    │
                         │ editor_achado(): PATH ampliado → apps macOS (open -a) → %LOCALAPPDATA% (Windows)      │
                         │ resumo ✅ "…, editor <x>" · ⚠️ gh ausente / deslogado / sem resposta (com o comando)    │
                         └────────────────────────────────────────────────────────────────────────────────────────┘
 sdd-new-session ─▶ checar.sh --frente (sem gh, igual a hoje) ─▶ checar.sh --editor ─▶ comando do editor │ vazio
                                                                                        │                  │
                                                                              abre a frente        MODO TERMINAL
                                                                              aviso "janela nova"   (terminal novo → cd → agente)
 sdd-iniciar-repo ─▶ inventario.sh ─▶ … "gh: ausente|deslogado|ok|sem resposta" (gh_estado(), cópia idêntica)
                     Passo 0: aviso antecipado (instalar agora / depois) · Passo 6: checagem de retomada

 sdd/bin/*.sh · bin/sdd-open.sh · bin/lib/merge.sh
     └─ . sdd/bin/lib/python.sh ─▶ python3 serve? fica · senão SDD_PYTHON / python / py -3 ≥ 3.9 ─▶ calço python3 no PATH
                                    nenhum serve ⇒ PATH intacto; sdd_python_pronto falha com a causa (uma vez)
                                    a guarda de cada script (antes `command -v python3`) para do jeito dele, só quando precisa

 CI  release.yml:      testes (ubuntu) · testes-macos · testes-windows (fora do needs) ─▶ release needs [testes, testes-macos]
     publish-gate.yml: gate (ubuntu) · macOS · windows
     testes-windows:   windows-latest · shell: bash (Git Bash) · setup-python · SDD_TEST_BASH = bash do Git
                       publish-gate.sh (ci) + unittest discover · teto 90 min
```

---

## Components

| Componente | Onde | Responsabilidade |
|---|---|---|
| `gh_estado` | função em `checar.sh` e em `inventario.sh` (texto idêntico, teste compara) | `ausente` · `deslogado` · `ok` · `sem resposta`, com teto de 10 s |
| `sistema` / `instalar_gh` | função em `checar.sh` e em `inventario.sh` (texto idêntico) | o comando de instalação do sistema em uso (`SDD_CHECAR_UNAME` ou `uname -s`) |
| `editor_achado` | função em `checar.sh`; modo novo `--editor` | a detecção em 2 camadas do AT-003; pastas injetáveis (`SDD_APPS_DIRS`, `LOCALAPPDATA`) |
| resolvedor de Python | `sdd/bin/lib/python.sh` (novo) | AT-006; lido com `.` por todo script do pacote que chama `python3` |
| job `testes-windows` | `.github/workflows/release.yml` e `publish-gate.yml` | AT-007; informativo até a decisão do piso |
| constantes de pulo | `tests/apoio.py` (`SEM_SYMLINK`, `SEM_FCNTL`, `SEM_CHMOD`, `SEM_SINAL`, `SEM_POSIX_UID`) | AT-008; um motivo por recurso |
| texto das skills | `SKILL.md` das 3 skills | Passo 0 da iniciar-repo, modo terminal e aviso da new-session, tabela de instalação nas 3 |

---

## Key Decisions

### Decision 1: Medir primeiro, com o README já honesto

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o tamanho do trabalho no Windows só se conhece rodando a suíte lá (abordagem A do brainstorm).
**Choice:** o 1º commit traz só o job `testes-windows` informativo nos 2 workflows, o `.gitattributes` com `eol=lf`, as 4 frases do README/quickstart dizendo "Windows (Git Bash/WSL): sem teste automático ainda" e o teste de coerência (AT-007). Push e PR em rascunho. O log é agrupado por causa na tabela "Categorias do Windows" (abaixo), que é **atualizada neste DESIGN** (Revision History) com o que a medição mostrar.
**Rationale:** a promessa não provada sai no mesmo commit que começa a prova; o resto do Build se planeja com número.
**Alternatives Rejected:** 1. skills primeiro — deixa a incerteza para o fim · 2. medir sem corrigir a frase — o README continuaria afirmando o que não foi provado.
**Consequences:** PR em rascunho aberto a frente toda · o 1º run diz quantas rodadas o Windows pede.

### Decision 2: Python resolvido por uma biblioteca lida com `.`, que põe um calço `python3` no PATH só quando precisa

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** 18 arquivos chamam `python3` (`bin/sdd-open.sh`, `bin/lib/merge.sh`, 14 de `sdd/bin/*.sh`, `sdd-kb/scripts/gate.sh` com `PYTHON`); 5 deles com `exec python3` (`adversarial-review.sh:47`, `adversarial-review-gate.sh:37`, `eval-revisores.sh:51`, `eval-agree.sh:33`, `ledger-revisao-lint.sh:53`), e 14 `.py` do pacote têm shebang de `python`. Só 1 dos 16 scripts tem `set -e`. No Windows, `python3` costuma ser o atalho da Store (sai 9009); o Python nativo é `python` ou `py -3`.
**Choice:** `sdd/bin/lib/python.sh` define `sdd_python_resolver` e o chama na carga:
1. `SDD_PYTHON_RESOLVIDO` no ambiente (`python3`, ou a pasta do calço) ⇒ só garante a pasta no PATH e volta (os processos filhos não testam de novo).
2. `SDD_PYTHON` definido ⇒ é testado como **uma palavra só, entre aspas** (caminho com espaço vale); serve ⇒ calço.
3. `python3` existe e roda com versão ≥ 3.9 ⇒ `SDD_PYTHON_RESOLVIDO=python3` e nada mais muda (o caminho de macOS e Linux).
4. Senão, `python`, depois `py -3`: o 1º que roda ⇒ **calço**: uma pasta de `mktemp -d` com um executável `python3` (`#!/bin/sh` + `exec <candidato entre aspas simples> "$@"`), posta à frente do PATH e exportada. O calço vale para `exec python3`, `env python3`, `xargs`, `timeout`, o shebang `#!/usr/bin/env python3` e os `bash -c` filhos.
5. Nenhum serve ⇒ o PATH fica como está e **nada para na carga** (rodada 2, R2: um `init --vendors codex` não precisa de Python e não pode parar por causa dele). A causa fica anotada: nenhum Python; um Python que existe e não roda (o atalho da Store); um Python mais velho que o 3.9, dito pela versão (R3); ou o calço que não pôde ser criado na pasta temporária (R4).
6. `sdd_python_pronto` entra no lugar de cada `command -v python3 >/dev/null 2>&1` dos scripts (21 guardas em 14 arquivos): volta 0 com um `python3` que serve e, senão, diz a causa uma vez por processo no stderr e volta 1. Cada script continua parando pelo seu próprio contrato de "python3 ausente" (mensagem, `RESULTADO:` e código), e só quando precisa de Python. `sdd_python_exigir` serve aos 2 scripts sem guarda própria (`docs-extract-decisions.sh`, antes do 1º uso; `governanca-fronteira.sh`, logo depois da carga, porque os 2 modos usam Python): a causa, `🛑 <script>: precisa do Python 3.9 ou mais novo.`, `RESULTADO: PAROU`, a seta com o conserto por sistema e `exit 64` (rodada 2, R1).
Cada script de `sdd/bin` ganha, logo depois do 1º `set -…`, a leitura da biblioteca só com builtins (o PATH pode não ter `dirname`) e com saída graciosa: sem o arquivo (projeto anterior a ele, ou script copiado sozinho, como fazem os testes), as duas funções voltam ao `command -v python3` de antes (`if [ -f … ]; then . …; else …; fi`, porque com `set -e` um `.` de arquivo ausente derruba o script antes do `||`); o `bin/sdd-open.sh` usa `${PKG}/sdd/bin/lib/python.sh` e o `bin/lib/merge.sh` herda as funções dele. O `sdd-kb/scripts/gate.sh` e o `checar.sh` (skills instaladas sozinhas) ficam fora: o `gate.sh` já aceita `PYTHON=`, e o `checar.sh` só cita `python3` numa mensagem. Nenhum código Python do pacote chama `python3` por `subprocess` (conferido: 0 ocorrências).
**Rationale:** uma linha por script, nenhuma chamada reescrita; o calço alcança toda forma de chamar `python3` que passa pelo PATH; no macOS e no Linux o caminho rápido não muda nada.
**Alternatives Rejected:** 1. função `python3` + `export -f` (versão 1.0 deste DESIGN) — `exec`, `env`, `xargs` e shebang não enxergam função de bash (rodada 1, R3) · 2. trocar cada `python3` por `"${PY}"` — ~60 linhas mexidas, e os `bash -c` filhos não veriam a variável · 3. parar na carga com exit 64 quando nada serve (v1.1) — parava também quem não precisa de Python, como o `init --vendors codex` num Windows com o atalho da Store (rodada 2, R2) · 4. pasta do calço com nome fixo em `/tmp` — outro usuário poderia criá-la antes; `mktemp -d` não tem esse risco · 5. exigir `python3` no Windows (alias manual) — o aluno não sabe fazer.
**Consequences:** uma chamada extra de Python por processo de topo (a variável exportada evita repetir nos filhos) · no Windows, uma pasta temporária pequena por processo de topo · skills soltas não ganham o resolvedor.

### Decision 3: `gh_estado` em paralelo com o `ls-remote`, só no modo normal, e copiado igual no inventário

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** `gh auth status` consulta a rede para validar o token; o `checar.sh` já roda o `ls-remote` (10 s) e o `curl` (3 s) em paralelo; o `inventario.sh` é de outra skill (instalada sozinha).
**Choice:** `gh_estado` roda `LC_ALL=C GH_PROMPT_DISABLED=1 gh auth status --hostname github.com` em segundo plano, com vigia de 10 s (saída do vigia em `/dev/null`, para não segurar a substituição de comando). Classifica: sem `gh` ⇒ `ausente`; rc 0 ⇒ `ok`; morto pelo vigia, ou mensagem de rede (`error connecting`, `dial tcp`, `could not resolve`, `timeout`) ⇒ `sem resposta`; outro rc ≠ 0 ⇒ `deslogado`. No `checar.sh`, roda dentro do bloco paralelo do `ls-remote` quando a URL do origin é do GitHub (`SLUG` não vazio), e sozinho quando não há origin; com origin de outro serviço, não roda. Se o remoto já recusou o acesso (o 🔴 com `gh auth login`), o ⚠️ de login não se repete. As funções `gh_estado` e `instalar_gh` existem iguais nos 2 scripts; `tests/test_f16_textos.py` compara o texto (como a INV-002 faz com o ledger).
**Rationale:** o teto total continua 10 s; o mesmo contrato nas 2 skills sem dependência entre elas.
**Alternatives Rejected:** 1. `gh auth status` sem rede (só o arquivo de configuração) — o `gh` não tem esse modo estável · 2. uma 3ª skill de biblioteca — as skills são instaladas sozinhas (a F17 as gera como zip).
**Consequences:** duas cópias de ~30 linhas, vigiadas por teste · `sem resposta` é o 4º valor da linha `gh:` (o DEFINE v1.1 o acrescenta ao AT-004).

### Decision 4: A detecção de editor mora no `checar.sh`, com o modo `--editor`

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** hoje a detecção é texto da `sdd-new-session` (o agente roda `command -v`) e repetida no resumo do `checar.sh` (`code cursor subl`). A `sdd-new-session` já depende do `checar.sh` para o pré-voo.
**Choice:** `editor_achado` no `checar.sh` (uma fonte só); `bash checar.sh --editor` imprime na 1ª linha o comando (`code`, `open -a "Visual Studio Code"`, ou o caminho do `.cmd` entre aspas) e, quando houver, na 2ª `dica: <como pôr o comando no PATH>`; sai 0 com editor e 1 sem. Pastas: `SDD_APPS_DIRS` (padrão `/Applications:$HOME/Applications`), `LOCALAPPDATA` (o do Windows, convertido por `cygpath -u` quando existir), `SDD_CHECAR_UNAME` (padrão `uname -s`). A `sdd-new-session` passa a mandar rodar o `--editor` com o slot vazio (sem bash: `Get-Command` sobre a mesma lista, como hoje). O slot cheio é usado como está, inclusive com argumentos.
**Rationale:** uma regra testável, com as pastas falsas injetadas no teste; nenhum caminho de máquina real.
**Alternatives Rejected:** 1. script novo na `sdd-new-session` — o resumo do `checar.sh` teria a sua própria lista · 2. só texto na skill — o AT-003 não teria teste.
**Consequences:** o modo `--editor` é contrato novo do `checar.sh` (documentado no cabeçalho e no `SKILL.md`).
**Revisão (v1.5, pedido do Roberto antes da release):** a `sdd-new-session` não escolhe mais sozinha: com o slot vazio, roda `checar.sh --editores` (todos os achados, `<nome><TAB><comando>`, sem repetir o mesmo editor por dois caminhos) e pergunta uma vez (`[D2 · muda o produto]`): os editores achados (o 1º recomendado), `terminal:claude`, `terminal:codex`, dizer o meu comando, não sei; grava em `git config --local sdd.editor` (rodada 5, R1: no slot da frente, a pergunta voltava em cada frente até a integração). Ordem de leitura: slot cheio (fixa para o time) → `git config sdd.editor` (preferência deste computador) → pergunta. `terminal:<agente>` no slot = modo terminal com esse agente. O `--editor` e o resumo do modo normal continuam com o 1º achado. Motivo: no Mac do Roberto, as provas abriam o VS Code e ele usa o Cursor; o editor de quem trabalha é preferência, não detecção.

### Decision 5: Job Windows com Git Bash, Python do `setup-python` e `SDD_TEST_BASH` fixado

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o caso real do aluno é Git Bash + Python nativo; no `windows-latest`, o `bash.exe` do WSL pode vir antes no PATH do Python, e o checkout pode trocar o fim de linha.
**Choice:** `runs-on: windows-latest`, `defaults.run.shell: bash`, `timeout-minutes: 30` (era 90; ver Decision 8), sem `continue-on-error` (o `tests/test_release_workflow.py` proíbe mascarar falha: o job fica fora do `needs:` do `release`, então um vermelho aparece no run e não segura a Release); `actions/setup-python` (3.12) antes; o `SDD_TEST_BASH` recebe `$(cygpath -w "$(command -v bash)")` (o bash do Git); gitleaks Windows extraído com `python -m zipfile`; `.gitattributes` ganha `* text=auto eol=lf` na 1ª linha (os `-text` de hoje continuam valendo depois dela). No `publish-gate.yml`, um job irmão com os mesmos passos. O `needs:` do `release` não muda até a decisão do piso.
**Rationale:** mede o que o aluno usa; o `eol=lf` protege também quem clonar o Open no Windows.
**Alternatives Rejected:** 1. `shell: pwsh` — o pacote é bash · 2. WSL — o Ubuntu já cobre · 3. `core.autocrlf false` só no CI — não protege quem clona.
**Consequences:** o job deve ser o mais lento; o teto de 90 min é medido no 1º run e revisto antes da tag.

### Decision 6: Pulo por recurso com constante única; defeito do pacote ganha conserto com teste

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** a suíte já tem `skipIf(os.name == "nt", "fcntl")` e `os.geteuid()` sem guarda num decorador (`tests/test_prompt_drift_scan.py:323`), que quebra a importação do módulo no Windows.
**Choice:** `tests/apoio.py` define tuplas `(condição, motivo)`: `SEM_SYMLINK` (sem permissão para criar link: detectado tentando criar um num temporário), `SEM_FCNTL`, `SEM_CHMOD` (bit de execução não vale), `SEM_SINAL`, `SEM_POSIX_UID` (`os.geteuid` ausente); uso `@unittest.skipIf(*SEM_SYMLINK)`. `tests/test_windows.py` varre `tests/*.py` e reprova `skipIf`/`skipUnless` com `os.name` ou motivo literal de plataforma fora de `apoio.py`. Cada quebra do log é classificada na tabela de categorias: **recurso ausente** ⇒ constante; **defeito do pacote** (caminho com `\`, CRLF, `python3`, `/tmp` fixo, `bash` errado) ⇒ conserto com teste que roda nos 3 sistemas.
**Rationale:** o motivo de cada pulo é um só e procurável; nada é pulado por conveniência.
**Alternatives Rejected:** 1. pular módulos inteiros no Windows — esconderia defeito · 2. `expectedFailure` — mede menos que o pulo com motivo.
**Consequences:** os `skipIf` existentes de plataforma migram para as constantes.

### Decision 7: Tabela de instalação única, repetida nas 3 skills e conferida por teste

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** cada skill é instalada sozinha; a `sdd-iniciar-repo` hoje só diz "baixe o instalador" no Mac e nada no Linux.
**Choice:** o bloco entre `<!-- INSTALAR-INICIO -->` e `<!-- INSTALAR-FIM -->`, igual byte a byte nos 3 `SKILL.md`: a tabela macOS · Windows · Linux × `git` · `gh` do escopo §3.4, "depois de instalar, feche e abra o terminal" e o login `gh auth login` → GitHub.com → HTTPS → Yes → Login with a web browser. `tests/test_f16_textos.py` compara os 3 blocos e confere que os comandos do `instalar_gh` dos scripts estão no bloco.
**Rationale:** uma fonte por cópia, sem deriva.
**Alternatives Rejected:** 1. arquivo em `references/` compartilhado — não existe entre skills · 2. só um link — o aluno fica sem o comando.
**Consequences:** mudar a tabela é mudar 3 arquivos e 2 scripts no mesmo commit; o teste acusa o esquecido.

---

### Decision 8: O job Windows roda o caminho do aluno; a suíte inteira é a frente F16W

| **Status** | Accepted | · | **Date** | 2026-11-11 |

**Context:** a 1ª medição (PR #25, run 42938720292, commit `416c0d5`) rodou a suíte inteira e foi cancelada no teto de 90 min com 282 de ~1.900 testes feitos (~19 s por teste, contra ~1 s no macOS): 126 passaram, 145 falharam, 11 com erro; 19 tracebacks de `UnicodeDecodeError` (texto lido com a codificação do Windows). O publish-gate e a checagem "Git Bash + Python nativo" passaram. É a regra de parada do brainstorm (decisão 7).
**Choice:** decisão do Roberto em 2026-11-11: o job roda `python -B -m unittest -v test_checar test_inventario test_python_resolver test_windows test_f16_textos` de dentro de `tests/`, com `PYTHONUNBUFFERED=1` e teto de 30 min, fora do `needs:` da release; o porte da suíte inteira vira a frente F16W, que começa medindo módulo a módulo.
**Rationale:** a suíte inteira levaria ~10 h por rodada; o caminho do aluno (as 3 skills desta frente e o resolvedor) é o que esta frente muda e o que cabe medir aqui.
**Alternatives Rejected:** 1. tudo nesta frente — tamanho de vários dias, a F17 esperando · 2. mais uma rodada só de medição, módulo a módulo — ~3 h de CI antes de decidir.
**Consequences:** o README continua "sem teste automático" no Windows; 4 dos 5 achados guardados (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`) ficam medidos só na F16W; o do CRLF roda aqui.

## Categorias do Windows (a atualizar com a medição)

| Categoria | Sinal no log | Tratamento | Teste |
|---|---|---|---|
| `python3` é o atalho da Store | exit 9009, "Python was not found" | Decision 2 | `tests/test_python_resolver.py` |
| bash errado (WSL) | `/bin/bash: … not found`, `wsl` | Decision 5 (`SDD_TEST_BASH`) | o job |
| fim de linha | `$'\r': command not found` | Decision 5 (`.gitattributes`) | o job + `test_windows.py` confere a linha |
| API POSIX em teste | `AttributeError: … geteuid`, `fcntl` | Decision 6 (`SEM_POSIX_UID`, `SEM_FCNTL`) | `test_windows.py` |
| link simbólico | `OSError: [WinError 1314]` | `SEM_SYMLINK` | `test_windows.py` |
| bit de execução | stub sem permissão de execução | `SEM_CHMOD` ou stub com shebang lido pelo bash | por caso |
| caminho com `\` ou `C:` | comparação de caminho falha | conserto com teste | por caso |
| os 5 achados guardados | CRLF no stdout do curator; ramo `tasklist`; `report-lint`; `sdd-archive`; trava sem `O_NOFOLLOW` | medido; conserto ou rebate com o log | `test_windows.py` lista o teste de cada um |

Regra de parada (DEFINE, Constraints): se a 1ª medição trouxer centenas de quebras fora destas categorias, o Build para e leva os números ao Roberto.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|---|---|---|---|---|
| 1 | `README.md`, `README.pt-BR.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md` | Modify | frase de Windows: "sem teste automático ainda" (AT-007, ramo "não foi") | (general) | None |
| 2 | `.gitattributes` | Modify | `* text=auto eol=lf` na 1ª linha (Decision 5) | (general) | None |
| 3 | `.github/workflows/release.yml` | Modify | job `testes-windows` informativo, fora do `needs:` | (general) | 2 |
| 4 | `.github/workflows/publish-gate.yml` | Modify | job Windows irmão | (general) | 2 |
| 5 | `tests/test_release_workflow.py` | Modify | AT-007: os 2 jobs, os passos, o teto, e a coerência com as 4 frases; AT-009: `needs:` e tetos de Ubuntu/macOS | (general) | 1, 3, 4 |
| 6 | `tests/apoio.py` | Modify | constantes `SEM_*` (Decision 6) | (general) | None |
| 7 | `tests/test_windows.py` | Create | AT-008: varredura dos `skipIf`; os testes dos 5 achados guardados; `.gitattributes` | (general) | 2, 6 |
| 8 | `sdd/bin/lib/python.sh` | Create | resolvedor (Decision 2) | (general) | None |
| 9 | os 16 scripts que chamam `python3` (as 21 guardas `command -v python3` viram `sdd_python_pronto`) (`bin/sdd-open.sh`, `bin/lib/merge.sh`, `sdd/bin/{adversarial-review,adversarial-review-gate,deploy-do-sha,docs-extract-decisions,eval-agree,eval-revisores,governanca-fronteira,ledger-revisao-lint,playbook-curator,sdd-decisoes-lint,sdd-drive,sdd-fluxo,slot,test-baseline}.sh`) | Modify | 1 linha que lê o resolvedor | (general) | 8 |
| 10 | `tests/test_python_resolver.py` | Create | AT-006: stubs `python3` que sai 9009, `python` válido, `py -3`, versão 3.8, nenhum, `SDD_PYTHON` com espaço no caminho; o calço visto por `exec`, `env python3` e um `bash -c` filho; parada na carga com exit 64 | (general) | 8, 9 |
| 11 | `tests/*.py` apontados pela medição | Modify | `skipIf(*SEM_…)` e consertos por categoria | (general) | 6, 7 |
| 12 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Modify | `gh_estado`, `instalar_gh`, `editor_achado`, modo `--editor` (Decisions 3 e 4) | (general) | None |
| 13 | `.agents/skills/sdd-checar-ambiente/SKILL.md` | Modify | 1.5.0: `gh` e login como ⚠️, `--editor`, bloco de instalação | (general) | 12 |
| 14 | `tests/test_checar.py` | Modify | AT-001 a AT-003; `Base` põe um `gh` stub logado no PATH por padrão | (general) | 12 |
| 15 | `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh` | Modify | linha `gh:` (cópia de `gh_estado`) | (general) | 12 |
| 16 | `.agents/skills/sdd-iniciar-repo/SKILL.md` | Modify | 1.2.0: Passo 0 com o aviso antecipado; Passo 6 com o bloco de instalação | (general) | 15 |
| 17 | `tests/test_inventario.py` | Modify | AT-004: os 4 valores da linha `gh:` por stub | (general) | 15 |
| 18 | `.agents/skills/sdd-new-session/SKILL.md` | Modify | 1.5.0: `--editor`, slot com argumentos, modo terminal, aviso final em 2 formas, bloco de instalação | (general) | 12 |
| 19 | `tests/test_matriz_new_session.py` | Verify | AT-009: o contrato do `--frente` não mudou, e o teste existente segue verde; o `--frente` sem `gh` está em `tests/test_checar.py` e o modo terminal e os 2 avisos em `tests/test_f16_textos.py` (Build, v1.3) | (general) | 12, 18 |
| 20 | `tests/test_f16_textos.py` | Create | AT-004/AT-005: blocos de instalação iguais nos 3 `SKILL.md`; `gh_estado`/`instalar_gh` iguais nos 2 scripts; Passo 0 com "instalar agora" e "depois" | (general) | 12, 13, 15, 16, 18 |
| 21 | `MANIFEST.txt` | Modify | `sdd/bin/lib/python.sh`, `tests/test_windows.py`, `tests/test_python_resolver.py`, `tests/test_f16_textos.py` | (general) | 7, 8, 10, 20 |
| 22 | `tests/test_sdd_open.py` | Modify | `init` e `sync` levam `sdd/bin/lib/python.sh` ao projeto, e um script instalado roda com ele (rodada 1, R5) | (general) | 8, 9 |

**Total Files:** 22

Ordem do Build: 1–7 (1º commit, push, PR em rascunho, medição) → 8–11 e 22 (Python e categorias, em rodadas de push) → 12–20 (skills, em paralelo com as rodadas) → 21.

---

## Landmines aplicáveis

Varredura rodada em 2026-11-10 sobre: checar, gh, editor, python3, workflow, windows, skipIf, README, git archive, chmod, symlink, CRLF, gitattributes, teto, timeout, stub, sabotagem, mutante, baseline, verify-gate, git add, publish-gate, sha256, corte por âncora, edição por script, heurística, evals, cenário comportamental, self-test.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| Gate que só confere fiação | LM-001 | ✔ tratado | os testes rodam `checar.sh`, `inventario.sh` e o resolvedor com stubs dos dois lados (com e sem `gh`, logado e deslogado, Python válido e atalho); 4 sabotagens |
| Asserção que não avalia nada | LM-002 | ✔ tratado | linha de base vermelha em `36d0454` para cada teste novo |
| Review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada; `git diff --stat` conferido contra a lista |
| Migration por exit 0 | LM-004 | N.A. | sem banco |
| Heurística sobre texto livre | LM-005 | ✔ tratado | a classificação do `gh auth status` usa o rc primeiro e só separa "sem resposta" por mensagem de rede; o teste fixa os 4 casos; as cópias de `gh_estado` têm teste de identidade, como a INV-002 |
| Script que só roda com `.git` | LM-006 | ✔ tratado | o resolvedor e o `--editor` não usam git; gate em cópia de `git archive`; o job Windows roda sobre o checkout e o `publish-gate` sobre a árvore |
| `limit_remaining` não é saldo | LM-008 | ✔ tratado | antes da 1ª rodada de revisão, o saldo é lido em `/credits` e a escolha vai ao Roberto |
| Sabotagem com `git checkout` | LM-009 | ✔ tratado | mutantes em cópia de `git archive`, com os consertos já commitados |
| Engine paga que estoura o teto | LM-010 | ✔ tratado | com saldo baixo, a revisão não usa 2º revisor pago |
| Cenário de comportamento nunca executado | LM-011 | ✔ tratado | a prova manual neste Mac (`open -a "Visual Studio Code"` abrindo a frente) e o modo terminal da `sdd-new-session` rodados de verdade, com critério escrito antes, registrados em `evidence/` |
| SHA-256 inteiro barrado pelo gate | LM-012 | ✔ tratado | nenhum hash inteiro em texto do pacote; nos documentos, prefixo de 12 |
| Edição por corte apaga testes | LM-013 | ✔ tratado | toda edição de teste por script confere `grep -c "def test_"` antes e depois |

---

## Contrato de aceite

N.A. (1 camada): scripts de terminal, texto de skill e workflows; nenhuma API entre camadas.

---

## Code Patterns

### Pattern 1: `gh_estado` (cópia idêntica em `checar.sh` e `inventario.sh`)

O código vive nos 2 scripts, entre `# ── gh e instalação por sistema (F16)` e `# ── fim do gh` (no começo da linha), e
`tests/test_f16_textos.py` compara as duas cópias. O desenho: `gh auth status --hostname github.com` em segundo
plano, num grupo de processos próprio (`set -m`), com um vigia de 10 s que mata o **grupo** (um filho vivo do `gh`
seguraria a saída depois do `gh` morto, como já acontecia no `ls-remote`); rc 0 ⇒ `ok`; morto pelo vigia ou mensagem
de rede ⇒ `sem resposta`; outro rc ⇒ `deslogado`; sem o comando ⇒ `ausente`.

candidato a pattern: shell (consulta de rede com teto, em grupo de processos).

### Pattern 2: o resolvedor (`sdd/bin/lib/python.sh`)

O código vive no arquivo (v1.2, depois das rodadas 1 e 2), não neste documento: um esqueleto aqui divergiria dele. A forma de uso:

```bash
set -u
. "$(dirname "$0")/lib/python.sh"   # F16: o Python que roda vira python3 (no Windows, python ou py -3)
if ! sdd_python_pronto; then        # antes: if ! command -v python3 >/dev/null 2>&1; then
  echo "🛑 <script>: python3 não encontrado no PATH." >&2
  printf 'RESULTADO: …\n→ …\n' >&2
  exit 64
fi
exec python3 -B - "$@" <<'PY'       # o calço vale também para exec, env, xargs e shebang
```

Cada candidato é testado no seu próprio `if`, sem variável de laço que sobra (rodada 1, R1); `SDD_PYTHON` é sempre uma palavra entre aspas (R2); a versão é lida com `sys.stdout.write("%d.%d" % sys.version_info[:2])`, que roda também no Python 2 (rodada 2, R3).

### Pattern 3: pulo por recurso

```python
# tests/apoio.py
SEM_FCNTL = (os.name == "nt", "fcntl: o Windows não tem a trava POSIX")
# no teste
@unittest.skipIf(*SEM_FCNTL)
def test_trava_concorrente(self): ...
```

---

## Data Flow

1. `checar.sh` (normal) → bloco paralelo: `alcance` + `publico` + `gh_estado` → classifica → `relatorio` (⚠️ do `gh` em `ARRUMAR`; editor no resumo).
2. `sdd-new-session` → `checar.sh --frente` (sem `gh`) → cria a frente → slot `editor` cheio? usa como está : `checar.sh --editor` → abre, ou modo terminal → aviso final da forma certa.
3. `sdd-iniciar-repo` Passo 0 → `inventario.sh` → linha `gh:` → aviso antecipado (instalar agora / depois) → … → Passo 6 confere de novo.
4. Script do pacote → `. lib/python.sh` → `python3` que roda (o do sistema, ou o calço no PATH) → o resto do script sem mudança; nenhum serve ⇒ a guarda do script (`sdd_python_pronto`) diz a causa e o script para pelo próprio contrato.
5. Push → `testes-windows` → log → categorias → consertos → push.

---

## Integration Points

| Sistema | Como | Falha tratada |
|---|---|---|
| `gh` (CLI do GitHub) | `gh auth status --hostname github.com` | ausente, deslogado, sem resposta (teto 10 s) |
| GitHub Actions `windows-latest` | `shell: bash`, `setup-python` | job informativo: não segura a Release |
| Python do sistema | `python3`, `python`, `py -3` | atalho da Store, versão < 3.9, nenhum |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| Unidade (script) | `checar.sh`: `gh` ausente/logado/deslogado/sem resposta × remoto GitHub/sem remoto/outro serviço × normal/`--frente`; `--editor` com PATH, apps falsos e `LOCALAPPDATA` falso | `tests/test_checar.py` | AT-001, AT-002, AT-003 |
| Unidade (script) | `inventario.sh`: 4 valores | `tests/test_inventario.py` | AT-004 |
| Unidade (script) | resolvedor: 9009, 3.8, `python`, `py -3`, nenhum, `SDD_PYTHON`, `bash -c` filho | `tests/test_python_resolver.py` | AT-006 |
| Texto | 3 blocos de instalação iguais, 2 cópias de função iguais, Passo 0, modo terminal, avisos | `tests/test_f16_textos.py`, `tests/test_matriz_new_session.py`, `tests/test_agnostico.py` | AT-004, AT-005 |
| Workflow | 2 jobs Windows, passos, teto, `needs:` e coerência com as 4 frases | `tests/test_release_workflow.py` | AT-007, AT-009 |
| Plataforma | varredura de `skipIf`, os 5 achados, `.gitattributes` | `tests/test_windows.py` | AT-008 |
| Regressão | suíte inteira, `SDD_TEST_BASH=/bin/bash`, em cópia de `git archive` | Verify Gate | AT-009 |
| CI real | `testes-windows` verde num run do PR, com a contagem | GitHub Actions + `evidence/` | critério de sucesso |
| Manual | `open -a "Visual Studio Code"` abrindo a frente neste Mac; modo terminal com PATH sem editor | sessão real, critério escrito antes (LM-011) | AT-003, AT-005 |
| Sabotagem | (1) `gh` ausente vira ✅; (2) `open -a` some; (3) o atalho da Store é aceito; (4) README afirma suporte com o job informativo | cópia de `git archive` | 4 de 4 mortas |

---

## Error Handling

| Caso | Comportamento |
|---|---|
| `gh auth status` sem resposta em 10 s | ⚠️ "não deu para conferir o login do gh agora", rc inalterado |
| remoto já recusou com `gh auth login` | o ⚠️ de login não se repete |
| nenhum Python serve | a carga segue; a guarda `sdd_python_pronto` diz a causa (não roda, versão X.Y, calço) e o script para pelo próprio contrato; sem guarda própria, `sdd_python_exigir` sai 64 com `RESULTADO: PAROU` |
| nenhum Python instalado | nada muda: cada script já tem a sua mensagem |
| `--editor` sem editor | sai 1, saída vazia: a skill responde em modo terminal |
| job Windows vermelho | informativo: a Release segue; o relatório registra |

---

## Configuration

| Variável | Padrão | Uso |
|---|---|---|
| `SDD_PYTHON` | — | força o interpretador (entra primeiro na lista) |
| `SDD_PYTHON_RESOLVIDO` | — | cache exportado pelo resolvedor: `python3` ou a pasta do calço |
| `SDD_APPS_DIRS` | `/Applications:$HOME/Applications` | pastas de apps do macOS (teste) |
| `SDD_CHECAR_UNAME` | `uname -s` | sistema (teste) |
| `LOCALAPPDATA` | o do Windows | `%LOCALAPPDATA%\Programs` |

---

## Security Considerations

- `checar.sh` e `inventario.sh` continuam só leitura; `gh auth status` não imprime o token (o `--show-token` nunca é usado) e a saída dele não é repassada ao aluno, só a classificação.
- O resolvedor nunca usa `eval`: o calço chama o candidato por nome fixo da lista (`python`, `py -3`) ou o valor de `SDD_PYTHON` entre aspas simples escapadas; a pasta do calço vem de `mktemp -d` (nome imprevisível, do próprio usuário), nunca de um nome fixo em `/tmp`.
- O job Windows tem `permissions: contents: read`, como os outros de teste.

---

## Observability

O relatório da frente registra, do run do Windows: total de testes, pulados por constante (contagem por motivo), falhas por categoria em cada rodada, tempo do job e o id de cada run.

---

## Advisor Ledger

Rodada 2 (`EXTERNAL_REVIEW_20261110-221917`): claude revisou e `openrouter` (qwen) auditou, `diversidade: vendor`. Ledger completo (7 colunas, com a marca de dano): `sdd/reviews/LEDGER_REVISAO_F16_AMBIENTE.md`. Rodada 1 com uma engine só (`--um-engine`: claude revisou e auditou, `diversidade: nenhuma`), por decisão do Roberto com o saldo da OpenRouter em US$ 0,07; a OpenRouter foi recarregada durante a rodada (US$ 20,07), e as rodadas seguintes usam claude + `openrouter` (qwen) como auditor.

| Nota | Fonte | Veredito | Evidência |
|---|---|---|---|
| R1 (HIGH) laço do Pattern 2 deixa `c="py -3"` sem `py` | rodada 1, revisor; auditor AGREE | APLICADA | Pattern 2 reescrito: um `if` por candidato, sem variável de laço; teste "nenhum roda" e "nenhum existe" em `tests/test_python_resolver.py` |
| R2 (MED) `SDD_PYTHON` com espaço cortado | rodada 1, revisor; auditor AGREE | APLICADA | `SDD_PYTHON` testado entre aspas como uma palavra; teste com caminho com espaço |
| R3 (MED) função não cobre `exec`, `env`, shebang | rodada 1, revisor; auditor DISAGREE_CONCERN | APLICADA | confirmado no código: 5 scripts com `exec python3` (`sdd/bin/adversarial-review.sh:47` e mais 4); Decision 2 passa a usar o calço no PATH |
| R4 (MED) `python3()` com rc 127 não para o script | rodada 1, revisor; auditor DISAGREE_CONCERN | APLICADA | confirmado: só 1 dos 16 scripts tem `set -e`; o resolvedor para na carga com exit 64 |
| R5 (MED) `init`/`sync` podem não levar `lib/` | rodada 1, revisor; auditor DISAGREE_CONCERN | APLICADA | a cópia já é recursiva (`bin/sdd-open.sh:589`, `find … -type f`), mas faltava a prova: manifest 22 acrescenta o teste |
| R1 (MED) sem nenhum Python, a carga volta calada e 2 scripts não têm guarda | rodada 2, revisor; auditor (qwen) AGREE | APLICADA | conferido: 14 dos 16 scripts têm guarda própria; `docs-extract-decisions.sh` e `governanca-fronteira.sh` ganham `sdd_python_exigir`; teste `test_nenhum_python_a_guarda_falha_calada_e_exigir_para` |
| R2 (MED) a parada na carga atinge quem não precisa de Python | rodada 2, revisor; auditor AGREE | APLICADA | confirmado: `bin/sdd-open.sh` só usa Python nos vendors claude e gemini; a carga nunca para e a guarda `sdd_python_pronto` substitui as 21 `command -v python3`; teste `test_so_o_atalho_a_carga_segue_e_a_guarda_diz_a_causa_uma_vez` |
| R3 (LOW) a mensagem diz "não roda" para o 3.8 ou o 2.7 | rodada 2, revisor; auditor AGREE | APLICADA | a causa diz a versão; testes `test_python_velho_e_dito_pela_versao` e `test_so_python_2_e_dito_pela_versao` |
| R4 (LOW) calço que não se cria volta calado | rodada 2, revisor; auditor AGREE | APLICADA | o motivo "não consegui criar o calço" fica anotado e a guarda o diz; teste `test_calco_que_nao_se_cria_e_dito` |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-10 | design-agent | Initial version |
| 1.1 | 2026-11-10 | design-agent | revisão do DESIGN, rodada 1 (`EXTERNAL_REVIEW_20261110-221223`, uma engine): Decision 2 troca a função `python3` exportada por um calço no PATH (cobre `exec`, `env`, shebang) e para na carga quando o Python existe e não roda; Pattern 2 reescrito (R1, R2); manifest 22 (teste de `init`/`sync` com `sdd/bin/lib/`); cabeçalho cita o DEFINE v1.1 |
| 1.6 | 2026-11-11 | design-agent | rodada 5 (R1, R2): a escolha do editor vai para `git config --local sdd.editor`; a opção recomendada fala da ordem da detecção |
| 1.5 | 2026-11-11 | design-agent | Decision 4 revista: a `sdd-new-session` pergunta o editor padrão uma vez (modo `--editores` no `checar.sh`; slot `terminal:<agente>`) |
| 1.4 | 2026-11-11 | design-agent | Decision 8 (1ª medição do Windows e decisão do Roberto): o job roda o caminho do aluno, teto de 30 min; o porte da suíte é a F16W; Decision 5 aponta o teto novo |
| 1.3 | 2026-11-11 | design-agent | Build: a leitura da biblioteca ganhou a saída graciosa (208 testes caíram sem ela: script copiado sozinho, PATH sem `dirname`, `set -e` com `.` de arquivo ausente); `gh_estado` roda num grupo de processos e o vigia mata o grupo (o teste do teto pegou o filho que segurava a saída por 30 s); `test_matriz_new_session.py` só confere; sem `instalar_git` |
| 1.2 | 2026-11-10 | design-agent | rodada 2 (`EXTERNAL_REVIEW_20261110-221917`, claude + qwen): Decision 2 deixa de parar na carga; `sdd_python_pronto` substitui as 21 guardas `command -v python3` e diz a causa certa (não roda, versão, calço); `sdd_python_exigir` nos 2 scripts sem guarda; Pattern 2 aponta para o arquivo. Decision 5 sem `continue-on-error` (o `tests/test_release_workflow.py` o proíbe; fora do `needs:` basta), achado do build |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F16_AMBIENTE.md`
