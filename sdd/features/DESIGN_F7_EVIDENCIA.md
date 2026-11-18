# DESIGN: F7 Evidência que não mente

> Porte por função, um ciclo, uma Release. O `report-lint.py` ganha regras novas como funções ao lado das 32 que já tem: tabela reconhecida, existência da avaliação, camadas, declaração com motivo, `PENDENTE`, `git check-ignore`, veredito fora de bloco cercado, `--stdin` e `--pendente`. O `verify-gate.sh` ganha o trace e o `--sem-define`, sem mudar uma linha da saída. Quatro scripts novos entram em `sdd/bin/`: três portados do privado quase sem mudança (`gate-baseline.sh`, `gate-shell-evidencia.sh`, `avaliador-guard.sh`) e um escrito do zero (`test-baseline.sh`). A `sdd-build` e a `sdd-release` ligam os mecanismos.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F7_EVIDENCIA |
| **Date** | 2026-10-30 |
| **Author** | SDD Design by RDD (sessão com Roberto Dias Duarte) |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F7_EVIDENCIA.md` |
| **DEFINE** | `sdd/features/DEFINE_F7_EVIDENCIA.md` (v1.2) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F7_EVIDENCIA.md` (8 MUST de texto de saída, U1–U8) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
                     sdd/config.yaml (layers:, evidence.require_avaliacao_layers, project.*)
                                │
   sdd-build ───────────────────┼──────────────────────────────────────── sdd-release (0a)
     │ 1    flag LLM (texto)    │                                            │
     │ 1.5  avaliador-guard.sh ─┤                                            │
     │ 5a   verify-gate.sh ─────┼──► sdd/traces/<F>.jsonl (1 linha/execução) │
     │ 5a+  gate-baseline.sh ───┤      (cópia da base + DEFINE, sdd/bin,     │
     │                          │       --sobrepor do build)                 │
     │ 5b   test-baseline.sh ───┼──► sdd/baselines/tests.txt                 │
     │ 5d   avaliador-guard.sh ─┤                                            │
     │ 6    report-lint.py ─────┼──► lê BUILD_REPORT, DESIGN (File Manifest), ┤ report-lint.py --pendente
     │                          │    sdd/reviews/AVALIACAO_*, git check-ignore ┤ gate-shell-evidencia.sh
     │                          │                                            ┤ verify-gate.sh --sem-define
     ▼                          ▼                                            ▼
  BUILD_REPORT_<F>.md      sdd/reports/evidence/<F>/*.log               aborta ou segue para o OK
  (linha do avaliador)     (BASELINE-gate.log, [exit=N])

   F8 (fora): adaptador do Claude Code chama report-lint.py --stdin e avaliador-guard.sh
```

---

## Components

| Component | Purpose | Location | Dependencies |
|-----------|---------|----------|--------------|
| `report-lint.py` | Contrato de evidência e de avaliação do BUILD_REPORT, fail-closed | `sdd/bin/report-lint.py` | `sdd/config.yaml`, `sdd/features/DESIGN_<F>.md`, `sdd/reviews/`, git |
| `verify-gate.sh` | Gate executável + trace JSONL + `--sem-define` | `sdd/bin/verify-gate.sh` | git, `date` |
| `gate-baseline.sh` | Prova que a asserção fica vermelha no código anterior | `sdd/bin/gate-baseline.sh` | `verify-gate.sh`, git, `tar` |
| `gate-shell-evidencia.sh` | Acusa `[exit=N]` que é exit do formatador | `sdd/bin/gate-shell-evidencia.sh` | git, `awk` com `LC_ALL=C` |
| `avaliador-guard.sh` | Nega despachar o avaliador com árvore suja | `sdd/bin/avaliador-guard.sh` | git |
| `test-baseline.sh` | Só falha nova de teste aborta | `sdd/bin/test-baseline.sh` | `project.test_cmd`, python3 (parser embutido), git (só `--touched`) |
| Slot `evidence.require_avaliacao_layers` | N do limite de camadas | `sdd/config.example.yaml` | — |
| Fragmentos e template | Contrato escrito da evidência e da linha do avaliador; molde LLM Prompts do relatório | `sdd/templates/` | — |
| `sdd-build` 2.3.0 · `sdd-release` 2.4.0 | Ligam os mecanismos nos passos | `.agents/skills/` | os scripts acima |
| Fixtures e testes | Os dois lados de cada regra | `sdd/fixtures/evidencia/`, `tests/` | `tests/apoio.py` |

---

## Key Decisions

### Decision 1: `report-lint.py` — regras novas como funções, classes e uma linha `→` por classe

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** D4 (fail-closed sempre, com a forma mínima declarada) e as 32 asserções que não mudam. A fonte é `claude-build-report-guard.py` do privado (541 linhas): `DECL_RE`, `strip_fences`, `verdicts_in`, `prova_avaliacao`, `camadas_do_design`, `existencia_avaliacao`, `git_ignored`, `cli_pendente`. A UX review pede uma classe por violação e uma orientação por classe (U1), com `PENDENTE` sem ambiguidade (U2) e o conserto da contagem impossível (U3).

**Choice:**
- **Funções novas** ao lado das atuais, com os nomes do privado onde o comportamento é o mesmo: `strip_fences`, `verdicts_in`, `declaracoes`, `prova_avaliacao`, `git_ignorado`, `ler_layers` (generaliza `ler_layers_sql`, que continua existindo e passa a chamar a nova), `limite_camadas`, `camadas_do_design`, `existencia_avaliacao`, `tabela_reconhecida`, `cli_pendente`.
- **Ordem do `check()`:** tabela → linhas `true` (como hoje, com `git check-ignore` depois de achar o arquivo) → vereditos (agora via `verdicts_in(strip_fences(content))`, que substitui o laço de `VERDICT_RE`) → existência → migrations (intacto).
- **Violação é uma tupla `(classe, texto)`.** As classes são `tabela`, `evidência`, `avaliação ausente`, `declaração` e `migration`. A saída é `🛑 [classe] texto`, e depois de `RESULTADO: VERMELHO` vem uma linha `→` por classe presente, na ordem de primeira aparição (lente L7). O texto das violações atuais não muda (as asserções são por substring), e o `→` de evidência e o de migration são os de hoje, palavra por palavra.
- **Avisos** saem em stdout como `⚠️ …`. Os de ambiente (contagem impossível, `check-ignore` indisponível) vão numa linha só, `⚠️ não conferido: …; …` (alerta L6). `PENDENTE` tem linha própria (U2): `⚠️ avaliação PENDENTE (<motivo>) — a release não sai enquanto esta linha existir`. Com `PENDENTE`, o `→` do verde vira "o relatório pode ser commitado; rode o avaliador quando o build destravar e troque a linha pelo veredito".
- **Tabela reconhecida:** uma linha `|` com uma coluna que começa com `evid` e outra que começa com `resultado`, `status`, `passou` ou `result` (caixa ignorada). Sem nenhuma no relatório → `[tabela] nenhuma tabela de critérios reconhecida (colunas Resultado e Evidência)`, com `→` "use a tabela do template: `| ID | Critério | Resultado | Evidência |`".
- **Declaração** (`DECL_RE` do privado, portado): o tipo em caixa alta (`N.A.`, `NA`, `PENDENTE`) por grupo `(?-i:…)`, em linha própria, depois de `avaliador`/`Veredito do avaliador (C1)` com `:`/`**`/`|` no meio, motivo entre parênteses. Fora de bloco cercado.
- **Existência:** vale um `AVALIACAO_<F>_\d8.*\.md` em `sdd/reviews/`, não vazio e não ignorado. Sem ele e sem declaração, a mensagem lista as 3 saídas na ordem (lente L2): (1) rode o avaliador (passo 5d da `sdd-build`); (2) `avaliador: N.A. (<motivo>)` só com menos de N camadas (a contagem atual entre parênteses); (3) `avaliador: PENDENTE (<motivo>)` se o build travou antes do 5d. Se existe um `AVALIACAO` mas o git o ignora, a mensagem diz isso e mostra o `git add -f`.
- **Camadas:** os caminhos da seção File Manifest (linhas `| n | …`, coluna 2, cada trecho entre crases) contam para `L` quando `fnmatch.fnmatchcase(caminho, glob)` casa algum glob preenchido de `layers:`. O DESIGN é `DESIGN_<F>.md` ou, num slice `_S<n>` sem DESIGN próprio, o da família (mesmo fallback do `define_gate_kind`). `N` vem de `evidence.require_avaliacao_layers`: ausente vira 2; valor que não é inteiro ≥ 1 vira 2 com ⚠️.
- **Modos de linha de comando:** `report-lint.py <relatório>` (como hoje); `report-lint.py --stdin <caminho>` (conteúdo da entrada padrão, nome e pasta tirados de `<caminho>`); `report-lint.py --pendente <relatório…>`. Os exits são os de sempre, 0/1/64; `--pendente` sai 1 quando acha, 64 com arquivo ilegível ou sem argumento.

**Rationale:** as funções do privado já passaram por 3 revisões externas (kimi, codex, fable) e um porte fiel é mais barato de auditar na F15. Classe por violação resolve U1 sem mudar o texto que as 32 asserções conferem.

**Alternatives Rejected:**
1. Reescrever o `check()` como lista de regras plugáveis: muda mais linhas do que as regras novas pedem (regra 7 do PORTE: delta-only).
2. Reprovar `N.A.` sem contagem: travaria todo projeto com `layers:` vazio, que é o default do `config.example.yaml`.
3. Data de corte (`CORTE_AVALIACAO`): YAGNI do BRAINSTORM.

**Consequences:**
- Um `BUILD_REPORT` antigo sem a linha do avaliador reprova ao atualizar (as notas da `v2.2.8` dizem o que acrescentar).
- `ler_layers_sql()` continua com a mesma assinatura (as migrations não mudam).
- O `report-lint.py` passa a chamar `git check-ignore`: fora de um repositório git, ⚠️ "persistência não conferida".

### Decision 2: `verify-gate.sh` — trace num `trap EXIT` que não toca a saída

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E9; os 6 exits e a saída nas fixtures ficam idênticos (AT-016). O privado instala o `trap` antes de saber o exit e grava a feature a partir do argumento.

**Choice:**
- O `define` relativo à raiz é calculado **antes** do `cd "$REPO_ROOT"` (o `-f` da linha 62 é relativo ao cwd de quem chamou): caminho absoluto do DEFINE pelo `cd "$(dirname …)" && pwd -P`, e só depois o recorte pela raiz.
- O `trap 'trace_gravar' EXIT` entra **depois** do `cd "$REPO_ROOT"`. Erros de uso anteriores (arquivo inexistente, fora de git) não gravam nada. `trace_gravar` começa por `[ "$PRINT_ONLY" = 1 ] && return 0`, porque o `--print` sai pelo `exit 0` da linha 119, depois do `trap`.
- `finalizar()` guarda o exit **original** em `TRACE_RC` antes do remapeamento do `--strict`; o `trap` usa `TRACE_RC` se definido e `$?` se não. O `--print` não grava.
- Os campos são `ts` (UTC, `date -u +%Y-%m-%dT%H:%M:%SZ`), `feature` (basename do DEFINE sem `DEFINE_` e `.md`, só `[A-Za-z0-9._-]`), `src` (`verify-gate` ou `release`), `kind`, `exit` e `define` (relativo à raiz; fora dela, só o basename; `\` e `"` escapados).
- A pasta é `$SDD_TRACE_DIR`, ou `sdd/traces` relativo à raiz. `mkdir -p` e o append ficam sob `|| true` e com stderr descartado. `SDD_TRACE=off` desliga.
- `--trace` é aceito e não faz nada (é o default, e assim a documentação do plano não mente). `--sem-define <F>` não lê arquivo nenhum: exige `<F>` (64 sem ele), resolve a raiz, grava `src: release`, `kind: no-define`, `exit: 0`, `define: ""`, imprime `ℹ️ <F>: release sem DEFINE — trace no-define gravado (nenhum gate rodou)` (ou `NÃO gravado (SDD_TRACE=off)`) e chama `finalizar 0`.
- A linha de uso passa a citar `--sem-define <FEATURE>`.

**Rationale:** gravar o exit original preserva a pergunta que o trace responde ("quantas voltas vermelhas"); com o `--strict` remapeado, 3, 4 e 5 virariam 1 e se misturariam. Instalar o `trap` depois da raiz evita gravar trace no diretório de quem chamou errado.

**Alternatives Rejected:**
1. Trace opt-in (`--trace` liga): o plano pede ligado por default; sem default, o registro some exatamente quando importa.
2. Ler `evidence.traces_dir` do config: D11 recusou o slot.

**Consequences:**
- Cada execução do gate numa worktree deste repositório cria `sdd/traces/<F>.jsonl`, não rastreado, que **nunca** entra em commit da branch de trabalho.
- Num projeto do usuário, o trace também fica não rastreado até o commit da feature; por isso o `avaliador-guard.sh` permite `sdd/traces/` (Decision 5).
- Os testes do `verify-gate` rodam em sandbox (conferido: nenhum teste roda o script na raiz), então a suíte não suja o repositório.

### Decision 3: `gate-baseline.sh` — porte com `--sobrepor` e veredito de avaliação mais estrito

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E7. O privado sobrepõe `scripts/` inteiro na cópia da base, porque é lá que os gates da RDD moram. No open, o gate pode chamar qualquer caminho. O privado também aceita como "avaliou" uma saída com `FAIL`, e isso casa `FAILED (errors=1)` de um `ImportError` (crash, não avaliação).

**Choice:**
- Cópia por `git archive <base> | tar -x` num `mktemp -d`, com `trap` de limpeza (`rm -rf` com a variável protegida por `:?`, nunca vazia).
- **Por cima da base vêm o DEFINE do build, `sdd/bin/` do build e cada `--sobrepor <caminho>`** (arquivo ou pasta, relativo à raiz; inexistente → 64). A cópia vira repositório com `git init` e um commit feito com `-c user.name=… -c user.email=… -c commit.gpgsign=false -c core.hooksPath=/dev/null` e `--no-verify`, sem tocar no config de ninguém (assinatura e hooks globais de quem roda não podem transformar todo baseline em 3).
- A base é `--base <ref>` ou `origin/<default_branch>`, depois `<default_branch>`. O `default_branch` vem de `project.default_branch` do `sdd/config.yaml` (fallback `main`). Ref ausente ou inválida → 3.
- O gate roda com `SDD_TRACE=off`, para não gravar trace da cópia.
- **"Avaliou" quando** o gate sai 2 **e** a saída tem o `🔴` do runner ("o comando declarou VERMELHO", que só aparece quando o próprio comando imprimiu `RESULTADO: VERMELHO` ou `GATE VERMELHO`) **ou** um marcador de asserção dos 5 formatos: `FAILED (failures=` (unittest), `= N failed` (pytest), `--- FAIL:` (go), `Tests: N failed` (jest), `failed` na linha `Test Files`/`Tests` (vitest), `FAILED |` (deno). **O `(rc=N)` do runner não conta**: no open ele é o rc bruto do comando (`verify-gate.sh:146-147`, `:196`), e `grep` em arquivo ausente ou erro de sintaxe também dão `(rc=2)` (medido na revisão, `AVAL-DESIGN-gate-baseline-rc2.log`). Vermelho sem um desses sinais sai 3, nomeando o rc.
- **Evidência:** `sdd/reports/evidence/<F>/BASELINE-gate.log`, com 1ª linha `$ bash sdd/bin/gate-baseline.sh …`, 2ª `# base=<ref> (<sha curto>) · exit_do_gate=<rc>` e até 200 linhas da saída.
- Saídas no contrato U5: 0 `✅ … RESULTADO: VERDE`; 2 `🛑 … sem dentes … RESULTADO: VERMELHO` com o `→` do U9; 3 `⚠️ … RESULTADO: INCONCLUSIVO`; 64 `🛑 uso … RESULTADO: ERRO DE USO`.

**Rationale:** sem `--sobrepor`, o caso para o qual o script existe (o build corrigiu a asserção) sai sempre 3, porque o gate novo não está na base. O critério por sinal de asserção impede o falso "tem dentes" de um crash (import, arquivo ausente, sintaxe).

**Alternatives Rejected:**
1. Sobrepor tudo o que o build mudou: aí a base vira o build e o vermelho nunca aparece.
2. Manter o `FAIL` genérico do privado: aceita crash como dente.
3. Aceitar `(rc=2)` como avaliação, como no privado: lá o rc é de um gate que segue a convenção 2/3; aqui é o rc de qualquer comando.

**Consequences:** a `sdd-build` passa a dizer quais caminhos sobrepor (o script do gate e as fixtures dele). O gate da própria F7 não é provado por este script (o `cmd` roda a suíte do HEAD da cópia): a baseline da F7 é rodar os testes novos contra a `v2.2.7`.

### Decision 4: `gate-shell-evidencia.sh` — porte com `exit=N`, `LC_ALL=C` e sem arrays vazios

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E8. O privado usa `PATHS+=()`, `LOGS+=()`, `read -d ''` e a expansão do array inteiro de logs; em bash 3.2 com `set -u`, a expansão de um array vazio aborta. O `awk` do macOS falha com UTF-8 (medido no Define). Os logs do open terminam em `exit=N`, sem colchetes.

**Choice:**
- O script começa por `cd "$(git rev-parse --show-toplevel)"` (64 fora de git no modo diff): `git diff --name-only` devolve caminhos relativos à raiz e `ls-files` relativos ao cwd.
- A lista de logs vai para um arquivo temporário (uma linha por caminho). A diferença usa `git -c core.quotepath=false diff --name-only --diff-filter=AMR <base>...HEAD -- sdd/reports/evidence` mais `git ls-files --others --exclude-standard`, e o `awk` roda uma vez por log.
- Os achados vão para outro arquivo temporário; o total sai de `grep -c`.
- O programa `awk` é o do privado, com estas mudanças:
  - roda com `LC_ALL=C`;
  - casa `^\[?exit=`;
  - `[exit=]` e `[exit=$?]` acusam com e sem colchete;
  - mensagens com `🛑`, e o comando truncado em 110 caracteres.
- Cada achado sai em duas linhas: "`arquivo:linha` — o número gravado é o exit de `tail`, não do seu comando" e o comando (U6). O `→` final traz a receita do `EVIDENCIA.md`.
- Sem argumento, olha o diff contra `origin/<default_branch>` (`--base` troca). Com caminhos, cada pasta vira `find <pasta> -name '*.log'`, em ordem `LC_ALL=C sort`. Caminho inexistente → 64; `git diff` que falha → 64.

**Rationale:** a regra do privado é a mesma. O que muda é o que quebra no piso do open: bash 3.2, `awk` do macOS e o formato `exit=N`.

**Alternatives Rejected:**
1. Reescrever em Python: perde a fidelidade ao privado sem ganho de regra.
2. Exigir só `[exit=N]`: os 19 acertos do corpus ficariam invisíveis e o formato dos 245 logs do open não seria lido.

**Consequences:**
- Neste repositório, a evidência de todas as frentes fica não rastreada, então o modo diff veria as pastas F1–F6. Aqui o script roda com o caminho da frente (`sdd/reports/evidence/F7_EVIDENCIA`).
- A regra é conservadora com comando composto (`&&`, `;`, `for … done`): acusa quando o último estágio de pipe é formatador, mesmo que o exit gravado venha de outro comando depois dele. No corpus do open, pelo menos 7 das 19 acusações são desse tipo; o conserto é o mesmo (gravar o `rc` do que importa), e a mensagem não afirma mais do que a regra mede.
- Num projeto do usuário, a evidência é versionada e o modo diff basta.

### Decision 5: `avaliador-guard.sh` — porte do hook do privado como script com exits

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E11. O hook do privado (88 linhas) é fail-open, porque hook quebrado não pode travar todo despacho. No open, o script é chamado de forma explícita pela skill, e o "não consegui conferir" tem de parar a skill (UX: nunca verde silencioso).

**Choice:**
- `git -C <root> -c core.quotepath=false status --porcelain --untracked-files=all`. Em `R`/`C`, os dois lados de `antigo -> novo` contam.
- São permitidos `sdd/reports/evidence/`, `sdd/traces/` (o trace que o gate do 5a grava antes do 5d) e cada `--permitir <prefixo>`.
- Exits:
  - **0** limpo: `✅ … RESULTADO: VERDE`;
  - **1** sujo: `🛑` + motivo do U7 + um caminho por linha + o comando `git -C <root> add <caminhos> && git -C <root> commit -m "wip(build): congelado para o avaliador"`, e `RESULTADO: VERMELHO`;
  - **2** o git falhou: `⚠️ não consegui conferir … RESULTADO: INCONCLUSIVO`;
  - **64** uso.
- `SDD_AVALIADOR_GUARD=off` sai 0 com `⚠️ guard desligado — declare no BUILD_REPORT`.

**Rationale:** o comando de commit usa `add` com os caminhos, não `-A`, pela regra da `sdd-release` (`git add` por nome).

**Alternatives Rejected:**
1. Fail-open como o hook: a skill trataria "não conferi" como "pode despachar".
2. Ignorar arquivo não rastreado: arquivo novo do build é exatamente o que se perde com um `git clean` ou com um checkout que o avaliador tente.

**Consequences:** neste repositório, `sdd/features|handoffs|reports|reviews/` ficam não rastreados de propósito; a revisão da F7 roda numa worktree destacada e, se o guard for chamado aqui, recebe os 4 prefixos `--permitir sdd/features/ --permitir sdd/handoffs/ --permitir sdd/reports/ --permitir sdd/reviews/` — nunca `sdd/`, que liberaria os entregáveis em `sdd/bin/`, `sdd/templates/` e `sdd/fixtures/`.

### Decision 6: `test-baseline.sh` — bash que roda, Python embutido que lê 5 formatos

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E10 é implementação nova. O `deno-test-gate.sh` do privado não porta (16 referências à RDD). Ler a saída de 5 formatos em `awk` de bash 3.2 seria frágil.

**Choice:**
- O bash lê `project.test_cmd` do `sdd/config.yaml` (por `sed`, como o `config_vendors` do `bin/sdd-open.sh`, com aspas tiradas) ou usa `--cmd`. Roda `bash -c "$CMD"` com a saída num arquivo temporário e grava o rc.
- Um bloco `python3 -B - <args> <<'PY'` faz o resto: extrai os ids, compara, reescreve o baseline e imprime.
- **Ids por formato** (as fixtures fixam cada um):

| Formato | Linha | Id |
|---|---|---|
| unittest | `FAIL: test_x (mod.Classe)` / `ERROR: …` (3.9–3.10) ou `… (mod.Classe.test_x)` (3.11+) | `mod.Classe.test_x` |
| pytest | `FAILED caminho::teste - …` / `ERROR caminho::teste` | `caminho::teste` |
| jest | `● Suite › teste` | `Suite › teste` |
| vitest | ` FAIL  arquivo > suite > teste` | `arquivo > suite > teste` |
| go | `--- FAIL: TestX` | `TestX` |
| deno | `nome => ./arquivo.ts:12:6` (bloco de falhas) | `arquivo.ts::nome` |

- **Decisão por caso:**

| Caso | Exit | Saída |
|---|---|---|
| rc = 127 ou `command not found` | 3 | `RESULTADO: INCONCLUSIVO` |
| rc ≠ 0 e nenhum id reconhecido | 3 | `RESULTADO: INCONCLUSIVO` |
| algum id fora do baseline | 2 | os ids sob `🛑 nova:` |
| só ids do baseline | 0 | `RESULTADO: VERDE` |
| `test_cmd` vazio e sem `--cmd` | 0 | `RESULTADO: PULADO` |

- **Baseline:** `sdd/baselines/tests.txt`, um id por linha; `#` e linhas vazias são preservados. Arquivo ausente = vazio.
- **Execução completa** = o `project.test_cmd` do config, sem `--cmd` e sem `--touched`, com resultado 0 (nenhuma falha nova). Só nela cada id do baseline que não falhou sai do arquivo (escrita por arquivo temporário + `mv`) e é listado sob `✅ sarou — removido do baseline (commite sdd/baselines/tests.txt)`. Com `--cmd`, ou com resultado 2 ou 3, nada sai e a saída traz `⚠️ baseline não podado (execução parcial)`: uma suíte interrompida ou um subconjunto não podem "curar" o que não rodou.
- **`--touched [--base <ref>]`:** o conjunto tocado é o diff `<base>...HEAD` mais o modificado e o não rastreado. Falha nova cujo id não contém nem o caminho nem o nome-base sem extensão de um arquivo tocado vira `⚠️ fora do diff` e não aborta. Nada sai do baseline.
- **`--aceitar <id>`:** acrescenta a linha (cria o arquivo e a pasta se preciso), imprime `✅ aceito` e sai 0, sem rodar a suíte.
- As 3 listas têm rótulo (U8). A falha nova traz "aceitar é decisão sua: `bash sdd/bin/test-baseline.sh --aceitar '<id>'`".

**Rationale:** bash para rodar e Python para ler segue o piso do open (bash 3.2 + Python 3.9 stdlib) e deixa o parser testável pelas fixtures.

**Alternatives Rejected:**
1. Slot de regex por projeto: D11 aprovou um slot só.
2. Aceitar falha nova sozinho: transforma o baseline em lixeira de vermelho.
3. `--touched` rodando só os testes tocados: o script não conhece o runner do projeto.

**Consequences:** um formato fora dos 5 sai 3, nunca verde (A-003 do DEFINE). Uma suíte com ids instáveis entre execuções (com tempo, endereço de memória) vê "falha nova" a cada volta; a correção é estabilizar o id no próprio teste.

### Decision 7: Skills, fragmentos, template, config e roadmap — o texto que liga os mecanismos

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** E12, E13, U10 e os contratos de texto (`test_contrato_build_release.py`, `test_correcoes_w0.py`, `test_agnostico.py`, `test_conversa.py`, `test_docs.py`). Delta-only (regra 7 do PORTE).

**Choice:**
- **`sdd-build` 2.3.0** (frontmatter e linha de identificação):
  - **passo 1** ganha um parágrafo: "Confira a flag `LLM Prompts` do DEFINE contra o DESIGN: `true` sem a seção de LLM Prompts no DESIGN, ou `false` com ela, ⇒ pare e itere o DESIGN; o drift do passo 4 continua armado nos dois casos";
  - **1.5** e **5d** ganham a frase "Antes de despachar, rode `bash sdd/bin/avaliador-guard.sh`; exit ≠ 0 ⇒ commite o que ele listar (exit 1) ou pare (exit 2) — sem isso, o avaliador pode restaurar arquivos e apagar o que não foi commitado";
  - **5a** ganha a linha "Se o build corrigiu uma asserção do gate, rode `bash sdd/bin/gate-baseline.sh sdd/features/DEFINE_<F>.md --sobrepor <script do gate>` e exija exit 0";
  - **5b** passa a dizer "o comando de teste do config via `bash sdd/bin/test-baseline.sh` (só falha nova aborta; `--aceitar` é decisão do usuário)";
  - **6** cita a linha do avaliador nas 3 formas (`AVALIACAO`, `avaliador: N.A. (<motivo>)`, `avaliador: PENDENTE (<motivo>)`) e "flag `LLM Prompts: true` ⇒ seção do relatório no molde `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md`";
  - a 1ª linha do Quality Gate ganha "guard antes do despacho";
  - **"Por que cada regra existe"** ganha 4 itens: guard, baseline do gate, falha nova de teste, linha do avaliador;
  - script de `sdd/bin/` ausente ⇒ "rode o `init` de novo: ele completa o que falta".
- **`sdd-release` 2.4.0**:
  - **0a.4:** "sem DEFINE" passa a rodar `bash sdd/bin/verify-gate.sh --sem-define <F>`;
  - **0a.5:** soma `python3 sdd/bin/report-lint.py --pendente sdd/reports/BUILD_REPORT_<F>.md` (exit ≠ 0 ⇒ abortar, citando o exit e o `arquivo:linha`);
  - **0a.7 (novo):** `bash sdd/bin/gate-shell-evidencia.sh` (exit ≠ 0 ⇒ abortar);
  - nos dois, 64 ou 127 acrescentam "atualize `sdd/bin/`: rode o `doctor` e, para o que ele apontar, apague e rode o `init`" (o `init` nunca sobrescreve `sdd/bin/*`, `bin/sdd-open.sh:603`, e um `report-lint.py` antigo responde 64 a `--pendente`);
  - "Gates de ABORTAR" ganha `report-lint --pendente ≠ 0` e `gate-shell-evidencia ≠ 0`;
  - 2 itens novos em "Por que cada regra existe";
  - o bloco do OK (item 7 da Fase 1) não muda.
- **`EVIDENCIA.md`:**
  - a receita passa a capturar a saída numa variável (`out=$(eval "$cmd" 2>&1); rc=$?`), gravar `$ <cmd>`, as últimas 200 linhas de `$out` e, por fim, `[exit=$rc]` (o `rc` é capturado antes de qualquer pipe; funciona em zsh e bash; texto exato no Pattern 5);
  - seção nova "A linha do avaliador" (3 formas, o que o lint faz com cada uma, N de `layers:`);
  - "cabeçalho em inglês não é reconhecido… sai 0" vira "`Result | Evidence` também é reconhecido; tabela não reconhecida reprova";
  - "O que o lint NEGA" ganha avaliação ausente, `N.A.` com ≥ N camadas, declaração sem motivo e "evidência que o git ignora";
  - regra de ouro 4 sem "só vale com a tabela no cabeçalho do template";
  - nenhuma palavra proibida pelo `test_correcoes_w0`.
- **`BUILD_REPORT_TEMPLATE.md`:** o gate de ativação cita `layers:` (sai a lista `sql · edge · front · scripts · harness`, que é da RDD); o veredito aceita `PENDENTE (<motivo>)`; e a nota cita "avaliação ausente reprova".
- **`LLM_PROMPTS_BUILD_REPORT.md`:** 5 seções (Inventário executado, Detalhe por prompt, Drift, Versionamento, Rollback), cada uma com tabela e "N.A. quando".
- **`config.example.yaml`:** mapa `evidence:` depois de `layers:`, com `require_avaliacao_layers: 2` e 3 linhas de comentário.
- **Roadmap EN/PT, linha 15:** passa a "**Hooks** — `pre-commit` and `pre-push` hooks that `init` installs with your confirmation; the build-report check before writing, in agents that support it" (PT espelhado). A palavra-chave "Hooks" que o `test_docs` confere fica.

**Rationale:** cada mudança de texto aponta para um script que faz a regra; nenhuma regra fica só no texto, exceto a E12, que é leitura de dois documentos que a skill já lê (BRAINSTORM, decisão 9).

**Alternatives Rejected:**
1. Mexer em `references/contexto-fresco.md`: o despacho está no 1.5 e no 5d do `SKILL.md`, e uma frase basta.
2. Um passo novo numerado na `sdd-build`: renumerar quebraria referências ("passo 1.5", "5d") em 4 arquivos.

**Consequences:** `test_contrato_build_release.py` e `test_correcoes_w0.py` atualizam as versões fixadas (2.3.0 e 2.4.0) junto com as asserções novas.

### Decision 8: Fixtures, testes, evidência e sabotagem

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-30 |

**Context:** regra 6 do PORTE (fixture e teste dos dois lados), AT-011, AT-016, AT-020 e AT-030; publish-gate G2 sobre as fixtures; o gate não vê `sdd/reports/`.

**Choice:**
- **Fixtures** em `sdd/fixtures/evidencia/`:
  - 4 relatórios: `BUILD_REPORT_controle.md`, `BUILD_REPORT_sem_avaliacao.md`, `BUILD_REPORT_pendente.md` e `BUILD_REPORT_evidencia_ignorada.md`. Os testes copiam cada um para `sdd/reports/` de um sandbox e montam ao redor o `AVALIACAO`, o log e o `.gitignore`;
  - 3 logs: `shell-honesto.log`, `shell-falso-verde.log` e `shell-pipe-assertivo.log`, escritos do zero com os casos do privado;
  - 6 saídas de teste: `testes-unittest.txt`, `testes-pytest.txt`, `testes-jest.txt`, `testes-vitest.txt`, `testes-go.txt` e `testes-deno.txt`. Cada uma tem 1 falha conhecida e 1 nova, e ids e números curtos (sem 11+ dígitos).
- **Testes novos:**
  - `test_report_lint_evidencia.py`, `test_verify_gate_trace.py`, `test_gate_baseline.py`, `test_gate_shell_evidencia.py`, `test_avaliador_guard.py` e `test_test_baseline.py`;
  - `test_bash32.py` varre as linhas sem comentário de `sdd/bin/*.sh` à procura de `mapfile`, `declare -A` e as expansões de caixa (`^^` e `,,` dentro de chaves).
- **Testes mudados:**
  - `test_report_lint.py`: só os helpers `lint()` das 2 classes ganham `CABECALHO` (classe `Migrations`) e `"avaliador: N.A. (1 camada)\n"` (as duas classes);
  - `test_contrato_build_release.py`: versões + AT-026/AT-027/AT-028;
  - `test_correcoes_w0.py`: versão da `sdd-build`.
- **Evidência** em `sdd/reports/evidence/F7_EVIDENCIA/`, no molde da F6. `gerar-evidencia.sh` roda no piso com `/bin/bash`, grava `[exit=$rc]` com `rc` capturado antes do pipe e produz:

| Log | O que contém |
|---|---|
| `GATE` | o Verify Gate |
| `relatorios-do-open` | AT-011: os 8 relatórios, com a classe de cada violação |
| `corpus-shell` | AT-020: as 19 `arquivo:linha` sobre os logs sem `F7_EVIDENCIA/`, com o `diff` contra a lista da revisão |
| `saidas-v2.2.7` | AT-016: `git show v2.2.7:sdd/bin/verify-gate.sh` × o novo, com `SDD_TRACE=off`, nas 4 fixtures (`diff` vazio) |
| `check-versions` | as versões contra a `v2.2.7` |
| `skill-lint-conversa` | as 17 skills |
| `bash32` | o `grep` de bashismos |
| `baseline` | os testes novos copiados para `git archive v2.2.7` (vermelhos) |
| `escopo` | o que mudou |
| `sabotagem` | 6 sabotagens em `sabotagem.sh` |

- **As 6 sabotagens**, uma por script: remover a regra de existência no `report-lint.py`; apagar a linha do `trap` no `verify-gate.sh`; trocar `exit 2` por `exit 0` no "sem dentes" do `gate-baseline.sh`; tirar `tail` da lista de formatadores do `gate-shell-evidencia.sh`; ignorar não rastreados no `avaliador-guard.sh`; tratar todo id como conhecido no `test-baseline.sh`.

**Rationale:** fixtures do pacote mostram ao usuário (o `init` as copia na 1ª instalação) o que cada regra reprova; o sandbox monta o resto, que depende de git.

**Alternatives Rejected:**
1. Fixtures copiadas do privado: carregam `.claude/sdd/` e nomes de feature da RDD.
2. Estender `test_report_lint.py` com as regras novas: misturaria contrato antigo e novo no mesmo arquivo; o diff dele fica só nos helpers.

**Consequences:** `MANIFEST.txt` ganha 25 linhas (4 scripts, 1 fragmento, 13 fixtures e 7 testes), em ordem `LC_ALL=C`. O teste da fixture `shell-falso-verde.log` compara o conjunto exato de `arquivo:linha`, não só o exit (a sabotagem "tirar `tail`" fica vermelha mesmo com `head` presente).

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/report-lint.py` | Modify | D4, E1–E6 e `--pendente` (Decision 1) | (general) | None |
| 2 | `sdd/bin/verify-gate.sh` | Modify | `--trace` e `--sem-define` (Decision 2) | (general) | None |
| 3 | `sdd/bin/gate-baseline.sh` | Create | E7 (Decision 3) | (general) | 2 |
| 4 | `sdd/bin/gate-shell-evidencia.sh` | Create | E8 (Decision 4) | (general) | None |
| 5 | `sdd/bin/avaliador-guard.sh` | Create | E11 (Decision 5) | (general) | None |
| 6 | `sdd/bin/test-baseline.sh` | Create | E10 (Decision 6) | (general) | None |
| 7 | `sdd/config.example.yaml` | Modify | slot `evidence.require_avaliacao_layers` | (general) | None |
| 8 | `sdd/templates/fragments/EVIDENCIA.md` | Modify | receita `rc=$?`, linha do avaliador, fail-closed | (general) | 1, 4 |
| 9 | `sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md` | Create | E13 | (general) | None |
| 10 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | linha do avaliador com `PENDENTE`, `layers:` | (general) | 1 |
| 11 | `.agents/skills/sdd-build/SKILL.md` | Modify | 2.3.0: E12, guard, baseline do gate, test-baseline, linha do avaliador, "por quê" | (general) | 3, 5, 6, 9 |
| 12 | `.agents/skills/sdd-release/SKILL.md` | Modify | 2.4.0: `--pendente`, `gate-shell-evidencia`, `--sem-define`, "por quê" | (general) | 1, 2, 4 |
| 13 | `sdd/fixtures/evidencia/BUILD_REPORT_controle.md` | Create | relatório que passa (com `AVALIACAO` montado pelo teste) | (general) | 1 |
| 14 | `sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md` | Create | avaliação ausente | (general) | 1 |
| 15 | `sdd/fixtures/evidencia/BUILD_REPORT_pendente.md` | Create | `avaliador: PENDENTE (motivo)` | (general) | 1 |
| 16 | `sdd/fixtures/evidencia/BUILD_REPORT_evidencia_ignorada.md` | Create | cita log que o teste põe no `.gitignore` | (general) | 1 |
| 17 | `sdd/fixtures/evidencia/shell-honesto.log` | Create | `rc=$?` antes do pipe, sem pipe | (general) | 4 |
| 18 | `sdd/fixtures/evidencia/shell-falso-verde.log` | Create | `\| tail` + `[exit=0]`, `[exit=]`, `exit=0` | (general) | 4 |
| 19 | `sdd/fixtures/evidencia/shell-pipe-assertivo.log` | Create | `\| grep -c`, `\| jq -e` | (general) | 4 |
| 20 | `sdd/fixtures/evidencia/testes-unittest.txt` | Create | saída unittest (3.9 e 3.11+) | (general) | 6 |
| 21 | `sdd/fixtures/evidencia/testes-pytest.txt` | Create | saída pytest | (general) | 6 |
| 22 | `sdd/fixtures/evidencia/testes-jest.txt` | Create | saída jest | (general) | 6 |
| 23 | `sdd/fixtures/evidencia/testes-vitest.txt` | Create | saída vitest | (general) | 6 |
| 24 | `sdd/fixtures/evidencia/testes-go.txt` | Create | saída go test | (general) | 6 |
| 25 | `sdd/fixtures/evidencia/testes-deno.txt` | Create | saída deno test | (general) | 6 |
| 26 | `tests/test_report_lint.py` | Modify | forma mínima nos 2 helpers (AT-012) | (general) | 1 |
| 27 | `tests/test_report_lint_evidencia.py` | Create | AT-001 a AT-010 | (general) | 1, 13, 14, 15, 16 |
| 28 | `tests/test_verify_gate_trace.py` | Create | AT-013 a AT-016 | (general) | 2 |
| 29 | `tests/test_gate_baseline.py` | Create | AT-017, AT-018 | (general) | 3 |
| 30 | `tests/test_gate_shell_evidencia.py` | Create | AT-019, AT-020 (fixtures) | (general) | 4, 17, 18, 19 |
| 31 | `tests/test_avaliador_guard.py` | Create | AT-021, AT-022 | (general) | 5 |
| 32 | `tests/test_test_baseline.py` | Create | AT-023 a AT-025 | (general) | 6, 20, 21, 22, 23, 24, 25 |
| 33 | `tests/test_contrato_build_release.py` | Modify | versões, AT-026 a AT-028 | (general) | 7, 8, 9, 10, 11, 12 |
| 34 | `tests/test_correcoes_w0.py` | Modify | versão fixada da `sdd-build` | (general) | 11 |
| 35 | `tests/test_bash32.py` | Create | bashismos em `sdd/bin/*.sh` | (general) | 2, 3, 4, 5, 6 |
| 36 | `docs/roadmap.md` | Modify | linha só com hooks | (general) | None |
| 37 | `docs/pt-BR/roadmap.md` | Modify | linha só com hooks | (general) | None |
| 38 | `MANIFEST.txt` | Modify | 25 arquivos novos, `LC_ALL=C` | (general) | 3, 4, 5, 6, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 35 |

**Total Files:** 38

Agent Discovery: Not available (um agente faz o build, modo default).

---

## Landmines aplicáveis

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-002 | todo teste novo | Cada teste afirma o motivo (classe/texto), não só o exit; a baseline roda os testes novos na `v2.2.7` |
| LM-003 | revisão de contexto fresco | Commit antes de cada revisão; o avaliador roda numa worktree destacada do commit |
| LM-004 | — | N.A.: sem migration |

---

## Contrato de aceite

Negociado em 2026-10-30 com a revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F7_EVIDENCIA_20261030.md`, modo `contrato`). Os 5 ajustes foram **ACEITOS** e aplicados no DEFINE v1.2:

| # | Alvo | Classe | Decisão |
|---|---|---|---|
| 1 | AT-017/AT-018 | estado sem critério | ACEITA — "avaliou" exige `🔴` do runner ou marcador de asserção; `(rc=N)` sozinho sai 3 |
| 2 | AT-020 | não verificável + premissa falsa | ACEITA — corpus sem `F7_EVIDENCIA/`, as 19 `arquivo:linha` listadas, regra declarada conservadora; fixture compara o conjunto exato |
| 3 | AT-021/AT-022 | efeito não observável | ACEITA — `sdd/traces/` permitido; 4 prefixos aqui, nunca `sdd/` |
| 4 | AT-024 | estado sem critério | ACEITA — poda só na execução completa; senão `⚠️ baseline não podado` e arquivo idêntico |
| 5 | AT-027 | estado sem critério (fail-open) | ACEITA — qualquer exit ≠ 0 aborta a 0a; 64/127 mandam atualizar `sdd/bin/` |

---

## Agent Assignment Rationale

| Agent | Files | Why |
|---|---|---|
| (general) | 1–38 | Modo default: os scripts compartilham convenções de saída (`🛑`, `RESULTADO:`, `→`), a leitura do `sdd/config.yaml` e as fixtures; um autor mantém os nomes coerentes |

---

## Code Patterns

### Pattern 1: Violação com classe e `→` por classe (`report-lint.py`)

```python
TABELA, EVIDENCIA, AUSENTE, DECLARACAO, MIGRATION = (
    "tabela", "evidência", "avaliação ausente", "declaração", "migration")
CONSERTO = dict(
    tabela="use a tabela do template: `| ID | Critério | Resultado | Evidência |`.",
    declaracao="escreva `avaliador: N.A. (<motivo>)` ou `avaliador: PENDENTE (<motivo>)`, com o motivo.",
)


def imprimir(violacoes, feature):
    vistas = []
    for classe, texto in violacoes:
        print("🛑 [%s] %s" % (classe, texto), file=sys.stderr)
        if classe not in vistas:
            vistas.append(classe)
    print("RESULTADO: VERMELHO", file=sys.stderr)
    for classe in vistas:
        print("→ " + conserto(classe, feature), file=sys.stderr)
```

### Pattern 2: Trace sem tocar a saída (`verify-gate.sh`, bash 3.2)

```bash
TRACE_RC=""
trace_gravar() {
  rc="$?"
  [ -n "$TRACE_RC" ] && rc="$TRACE_RC"
  [ "$PRINT_ONLY" = 1 ] && return 0
  [ "$SDD_TRACE_VAL" = "off" ] && return 0
  dir="$SDD_TRACE_DIR_VAL"
  mkdir -p "$dir" 2>/dev/null || return 0
  printf '%s\n' "$(trace_linha "$rc")" >> "$dir/$TRACE_FEATURE.jsonl" 2>/dev/null || true
  return 0
}
# depois do cd "$REPO_ROOT": trap trace_gravar EXIT
# em finalizar(): TRACE_RC="$1" antes de qualquer exit
```

`trace_linha` monta o JSON com `printf` e as chaves literais escapadas, como no privado; `SDD_TRACE_VAL` e `SDD_TRACE_DIR_VAL` recebem os defaults (`on`, `sdd/traces`) uma vez, no início, para não depender de `set -u` dentro do `trap`.

### Pattern 3: Lista de arquivos sem array (bash 3.2, `gate-shell-evidencia.sh`)

```bash
cd "$(git rev-parse --show-toplevel)" || exit 64
LISTA="$(mktemp)"; ACHADOS="$(mktemp)"
trap 'rm -f "$LISTA" "$ACHADOS"' EXIT
git -c core.quotepath=false diff --name-only --diff-filter=AMR "$BASE...HEAD" -- "$EVID" > "$LISTA" || exit 64
git -c core.quotepath=false ls-files --others --exclude-standard -- "$EVID" >> "$LISTA"
LC_ALL=C sort -u -o "$LISTA" "$LISTA"
while IFS= read -r f; do
  case "$f" in *.log) [ -f "$f" ] && LC_ALL=C awk -f "$PROG" "$f" >> "$ACHADOS" ;; esac
done < "$LISTA"
n="$(grep -c '^🛑' "$ACHADOS" || true)"
```

### Pattern 4: Saída de todo script novo (UX U4/U5)

```text
🛑 <regra em palavras>                  (bloqueia; uma linha por item)
⚠️ <aviso>                              (não bloqueia)
✅ <o que passou>
RESULTADO: VERDE | VERMELHO | INCONCLUSIVO | PULADO | ERRO DE USO
→ <o que fazer, no imperativo, com o comando pronto>
```

### Pattern 5: Receita de evidência com `rc` honesto (`EVIDENCIA.md`)

```bash
mkdir -p sdd/reports/evidence/<FEATURE>
cmd='npm test -- src/x.test.ts'
out=$(eval "$cmd" 2>&1); rc=$?
log=sdd/reports/evidence/<FEATURE>/AT-001.log
printf '$ %s\n' "$cmd" > "$log"
printf '%s\n' "$out" | tail -n 200 >> "$log"
printf '[exit=%s]\n' "$rc" >> "$log"
```

---

## Data Flow

```text
1. Build termina as tarefas → commit na branch.
2. sdd-build 5a: verify-gate.sh DEFINE → exit + 1 linha em sdd/traces/<F>.jsonl.
   Se o build corrigiu a asserção: gate-baseline.sh DEFINE --sobrepor <gate> → cópia da base
   + DEFINE + sdd/bin + sobreposições → verify-gate na cópia (SDD_TRACE=off) → 0/2/3 +
   evidence/<F>/BASELINE-gate.log.
3. sdd-build 5b: test-baseline.sh → roda test_cmd → ids → compara com sdd/baselines/tests.txt
   → 0 (remove os que sararam) · 2 (novas) · 3 · PULADO.
4. sdd-build 1.5 e 5d: avaliador-guard.sh → 0 despacha · 1 commita o listado e repete · 2 para.
   O avaliador grava sdd/reviews/AVALIACAO_<F>_<ts>.md.
5. sdd-build 6: report-lint.py BUILD_REPORT → tabela → true com evidência (check-ignore) →
   vereditos fora de fence → existência (AVALIACAO ou declaração; N.A. × camadas do manifest)
   → migrations → 0 ou 1 com classes.
6. sdd-release 0a: verify-gate --strict (ou --sem-define) · report-lint · report-lint --pendente
   · gate-shell-evidencia (diff) → qualquer bloqueio aborta antes do OK.
Erro principal: script ausente (instalação antiga) → 127 → a skill manda rodar init, que
completa o que falta em sdd/.
```

---

## Integration Points

| Sistema | Tipo | Direção | Falha |
|---|---|---|---|
| git (`check-ignore`, `status`, `diff`, `archive`, `ls-files`) | CLI local | leitura | `report-lint`: ⚠️ não conferido · `avaliador-guard`: exit 2 · `gate-shell-evidencia`: 64 · `gate-baseline`: 3 · `test-baseline --touched`: 64 |
| `project.test_cmd` do usuário | processo | executa | 127/"not found" → 3; rc ≠ 0 sem id → 3 |
| `sdd/config.yaml` | arquivo | leitura | ausente → defaults (`layers:` vazio, N = 2, `default_branch` = main, `test_cmd` vazio) |
| Adaptador do Claude Code | — | — | Fora: F8 (chamará `report-lint.py --stdin` e `avaliador-guard.sh`) |

Sem rede, credencial ou serviço externo.

---

## Testing Strategy

| Camada | O que | Onde | ATs |
|---|---|---|---|
| Unit/contrato (sandbox git por teste, `tests/apoio.py`) | cada regra dos dois lados | os 7 testes novos + 3 alterados | AT-001 a AT-010, AT-012 a AT-028 |
| Piso | suíte com `SDD_TEST_BASH=/bin/bash /usr/bin/python3` | Verify Gate | todos os do `cmd` |
| CI | Ubuntu + macOS (Python 3.9.6, bash 3.2.57) | PR | AT-029 |
| Corpus real | 8 relatórios e 245 logs do open | `evidence/F7_EVIDENCIA/` | AT-011, AT-020 |
| Regressão de saída | `v2.2.7` × novo, `SDD_TRACE=off` | `saidas-v2.2.7.log` | AT-016 |
| Baseline vermelha | testes novos na árvore `v2.2.7` | `baseline.log` | LM-002 |
| Sabotagem | 6 mutações | `sabotagem.log` | AT-030 |
| Revisão de contexto fresco | DESIGN (contrato) e build (veredito) | `sdd/reviews/` | todos |

---

## Error Handling

| Situação | Comportamento |
|---|---|
| `report-lint.py` sem argumento, nome fora de `BUILD_REPORT_<F>.md`, arquivo ilegível | 64 (como hoje); `--pendente` sem arquivo ou ilegível → 64 |
| Exceção interna no `report-lint.py` | sai ≠ 0 com traceback (regra de ouro 4: falha fechado) |
| `--stdin` com entrada vazia | o conteúdo vazio é conferido: reprova por tabela e avaliação ausentes |
| `verify-gate.sh` sem permissão em `sdd/traces/` | nada gravado; exit e saída intactos |
| `gate-baseline.sh` com `--sobrepor` inexistente | 64 antes de copiar |
| `gate-shell-evidencia.sh` com base inválida | 64 ("sem escopo confiável, não avalio") |
| `avaliador-guard.sh` fora de repositório git | 2 |
| `test-baseline.sh` com baseline sem permissão de escrita | 3 com a causa; nada é removido em silêncio |
| `test-baseline.sh --touched` sem base válida | 64 |

---

## Configuration

| Chave | Default | Quem lê | Observação |
|---|---|---|---|
| `evidence.require_avaliacao_layers` | `2` | `report-lint.py` | inteiro ≥ 1; outro valor → 2 com ⚠️ |
| `layers.*` | `""` | `report-lint.py` (todas as camadas; `sql` também nas migrations) | glob por camada |
| `project.default_branch` | `main` | `gate-baseline.sh`, `gate-shell-evidencia.sh`, `test-baseline.sh --touched` | já existe |
| `project.test_cmd` | `""` | `test-baseline.sh` | já existe; vazio = PULADO |
| `SDD_TRACE` / `SDD_TRACE_DIR` | `on` / `sdd/traces` | `verify-gate.sh` | ambiente, não slot (D11) |
| `SDD_AVALIADOR_GUARD` | — | `avaliador-guard.sh` | `off` = bypass declarado |

Nenhum segredo.

---

## Security Considerations

- **`avaliador-guard.sh` existe para proteger trabalho**: lista também não rastreados e os dois lados de renomeação; nunca roda `git add -A` por conta própria — só imprime o comando, com os caminhos.
- **`gate-baseline.sh` executa o `cmd` do DEFINE numa cópia**: é o mesmo comando que o `verify-gate.sh` já executa no build; nada novo ganha permissão. A limpeza usa `rm -rf` com a variável protegida por `:?`.
- **`test-baseline.sh` executa `project.test_cmd`**: o mesmo que a `sdd-build` 5b já roda.
- **Fixtures limpas**: sem e-mail fora de `example.com`, CPF, CNPJ, telefone, 11+ dígitos ou `/Users/`; o publish-gate G2 confere.
- **Trace sem caminho de máquina**: `define` fora da raiz vira basename.

---

## Observability

- `sdd/traces/<F>.jsonl`: `grep -c '"exit":2' sdd/traces/<F>.jsonl` dá as voltas vermelhas da feature; `"src":"release"` separa releases sem DEFINE (sinal S da UX review).
- `sdd/reports/evidence/<F>/BASELINE-gate.log`: prova de dentes por feature.
- A 0a da `sdd-release` cita `arquivo:linha` de cada `PENDENTE` e log acusado.

---

## Requirements Traceability

| Requirement | Design | Files |
|---|---|---|
| AT-001, AT-002 | Decision 1 (tabela) | 1, 27 |
| AT-003, AT-004, AT-005, AT-006 | Decision 1 (existência, camadas, declaração) | 1, 7, 14, 27 |
| AT-007 | Decision 1 (`PENDENTE`, `--pendente`) | 1, 15, 27 |
| AT-008 | Decision 1 (`git check-ignore`) | 1, 16, 27 |
| AT-009 | Decision 1 (`verdicts_in` + `strip_fences`) | 1, 27 |
| AT-010 | Decision 1 (`--stdin`) | 1, 27 |
| AT-011 | Decision 8 (corpus) | 1 |
| AT-012 | Decision 8 (helpers) | 26 |
| AT-013, AT-014, AT-015, AT-016 | Decision 2 | 2, 28 |
| AT-017, AT-018 | Decision 3 | 3, 29 |
| AT-019, AT-020 | Decision 4 | 4, 17, 18, 19, 30 |
| AT-021, AT-022 | Decision 5 | 5, 31 |
| AT-023, AT-024, AT-025 | Decision 6 | 6, 20–25, 32 |
| AT-026, AT-027 | Decision 7 (skills) | 11, 12, 33, 34 |
| AT-028 | Decision 7 (templates, config) | 7, 8, 9, 10, 33 |
| AT-029 | Decision 7 (roadmap), Decision 8 | 35, 36, 37, 38 |
| AT-030 | Decision 8 (sabotagem) | 1–6 |
| MUST UX U1–U8 | Decisions 1, 3, 4, 5, 6; Pattern 1 e 4 | 1, 3, 4, 5, 6 |

---

## Risks and Mitigations

| Risco | Mitigação |
|---|---|
| Uma das 32 asserções do `report-lint` muda sem querer | O diff de `tests/test_report_lint.py` fica só nos 2 helpers; o `escopo.log` mostra |
| O `trap` do `verify-gate.sh` muda o exit (bash 3.2 com `set -u`) | `trace_gravar` termina em `return 0` e não reatribui o exit; `test_verify_gate_trace` compara exit e saída com `SDD_TRACE=off` nas 4 fixtures e em `--strict` |
| Formato de teste real diferente da fixture | Sai 3, nunca verde (A-003); uma fixture nova por formato cobre o caso |
| `awk` do macOS e UTF-8 | `LC_ALL=C` em todo `awk` sobre log; CI em macOS |
| Release 0a deste repositório acusa os 19 logs antigos | Os logs são não rastreados aqui; o script roda com o caminho `sdd/reports/evidence/F7_EVIDENCIA` |
| Instalação antiga sem os scripts novos | A skill diz "rode o `init`" (completa `sdd/`); o `doctor` não muda nesta frente (F8 mexe no `bin/`) |
| `SKILL.md` passa de 500 linhas | `sdd-build` 232 e `sdd-release` 297 hoje; o acréscimo previsto é de ~25 e ~12 linhas |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F7_EVIDENCIA_20261030.md`): NEEDS_WORK, 2 HIGH, 4 MEDIUM, 8 LOW.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| H1 | `(rc=N)` do runner é o rc bruto; crash sai 2 | HIGH | APLICADA (Decision 3, AT-017/018) | `AVAL-DESIGN-gate-baseline-rc2.log`; `verify-gate.sh:196` |
| H2 | trace não rastreado faz o guard sair 1 em todo build | HIGH | APLICADA (Decisions 2 e 5, AT-021) | `sdd-build` 5a antes do 5d |
| M1 | 7 das 19 acusações não são exit de formatador; corpus móvel | MEDIUM | APLICADA (Decision 4, Clarification e AT-020 do DEFINE) | `AVAL-DESIGN-corpus-shell.log` |
| M2 | `--permitir sdd/` libera os entregáveis | MEDIUM | APLICADA (Decision 5) | `AVAL-DESIGN-guard-prefixos.log` |
| M3 | "execução completa" indefinida | MEDIUM | APLICADA (Decision 6, AT-024) | — |
| M4 | release 0a fail-open em 64/127 | MEDIUM | APLICADA (Decision 7, AT-027) | `report-lint.py --pendente` atual sai 64 |
| L1 | `--print` gravaria trace | LOW | APLICADA (Decision 2, Pattern 2) | `verify-gate.sh:119` |
| L2 | MANIFEST 22 × 25 | LOW | APLICADA (Decision 8, linha 38) | contagem do manifest |
| L3 | `sdd-release` tem 297 linhas | LOW | APLICADA (DEFINE e Risks) | `wc -l` |
| L4 | "camada das 15 skills" × 17 | LOW | APLICADA (DEFINE: seção nas 17, bloco comum do `test_conversa`) | `grep -l '## Como falar com o aluno'` = 17 |
| L5 | gpgsign/hooksPath globais no commit da cópia | LOW | APLICADA (Decision 3) | — |
| L6 | `diff` × `ls-files` com cwd diferente | LOW | APLICADA (Decision 4, Pattern 3) | — |
| L7 | DEFINE cita "saída gravada da v2.2.7" no gate | LOW | APLICADA (parágrafo do Verify Gate do DEFINE) | — |
| L8 | `define` precisa ser resolvido antes do `cd` | LOW | APLICADA (Decision 2) | `verify-gate.sh:62`, `:69` |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.3 | 2026-10-30 | SDD Build by RDD | Ciclo 2 da revisão do build (`AVALIACAO_F7_EVIDENCIA_20261030-ciclo2.md`): pacote go que falha sem `--- FAIL` vira `package failed: <pacote>` (linhas de resumo com TAB) e cores ANSI saem antes dos regex (Decision 6); o guard sugere só `commit` quando não há caminho para o `add` (Decision 5); `**Veredito do avaliador**:` e `| Veredito do avaliador |` reconhecidos (Decision 1); `$` sozinho, comentário de 1 espaço, `(tail)`, `command`/`env`, `<var>=$?` no gate-shell (Decision 4); `--sem-define` diz se gravou (Decision 2) |
| 1.2 | 2026-10-30 | SDD Build by RDD | Ciclo 1 da revisão do build (`AVALIACAO_F7_EVIDENCIA_20261030-ciclo1.md`): trace com `2>/dev/null` antes do `>>` (Decision 2); modo diff do `gate-shell-evidencia.sh` com staged e modificados, `|&`, `VAR=valor` antes do formatador, `[exit= ]` e `PIPESTATUS` em qualquer ponto (Decision 4); o commit do guard leva `add -A --` só com caminhos que o git reconhece (Decision 5); `[build failed]`/`[setup failed]` do go viram falha (Decision 6); rótulo do veredito sem `(C1)` e unidade = linha numa tabela (Decision 1); 2 "por quê" a mais (Decision 7) |
| 1.1 | 2026-10-30 | SDD Design by RDD | Revisão de contexto fresco do DESIGN: 14 notas aplicadas (Advisor Ledger); Contrato de aceite com 5 ajustes ACEITOS; DEFINE v1.2 |
| 1.0 | 2026-10-30 | SDD Design by RDD | Versão inicial |

---

## Next Step

Execute o **SDD Build by RDD**.
