# DESIGN: F15 Slots — smoke visual na release, teste do diff antes do OK e checagem de migration antes do apply

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F15_SLOTS |
| **Date** | 2026-11-09 |
| **Author** | design-agent (worktree `sdd-open-f15-slots`, base `9d8ac24` = `v2.7.2`) |
| **DEFINE** | [DEFINE_F15_SLOTS.md](./DEFINE_F15_SLOTS.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 sdd/config.yaml (do projeto)                       quem chama                      quando
 ┌──────────────────────────────┐
 │ smoke.before_ok_cmd     ""   │◄── sdd-release 6b  (--arvore <worktree landado>)     2 ⇒ FAIL-candidato no OK
 │ smoke.before_push_cmd   ""   │◄── sdd-release 7b  (depois do "sim", antes do push) só registra
 │ smoke.after_deploy_cmd  ""   │◄── sdd-release 10  (deploy confirmado; após fetch)  2 ⇒ pergunta D1
 │ schema.check_cmd        ""   │◄── sdd-build 4b §2b (antes da prévia/apply)         2|3|64 ⇒ não aplica
 └──────────────┬───────────────┘
                │ lido por
                ▼
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ sdd/bin/slot.sh <chave> [--feature F] [--base ref] [--commit sha] [--dir p]   │
 │                 [arquivo…]                                                    │
 │  1. chave ∈ lista fechada (4)          senão → 64                             │
 │  2. lê o valor (python3 stdlib)        aspas sem fechar / # / bash -n → 64    │
 │  3. vazio/ausente/sem config           → PULADO, exit 11                      │
 │  4. env: SDD_MOMENTO SDD_FEATURE SDD_BASE SDD_COMMIT SDD_ARVORE SDD_SLOT_DIR  │
 │     (mkdir; before_ok esvazia a pasta padrão)                                  │
 │  5. bash -c "<cmd> \"$@\"" slot <arquivos…>   (na raiz do repositório)        │
 │  6. 0 → OK · 2 → REPROVOU · 10 → NADA A MEDIR · outro/sinal → INCONCLUSIVO 3  │
 │     trap INT/TERM no próprio script → INCONCLUSIVO 3                           │
 └───────────────────────────────────────────────────────────────────────────────┘

 sdd-release 0a item 9 ──► sdd/bin/test-baseline.sh --touched
                              tocados = diff base...HEAD + não commitado + não rastreado
                              + teste ao lado de cada fonte tocada (mesma pasta, existente;
                                casado por prefixo de caminho ou segmento de módulo)
                              falha nova citando tocado ⇒ 🛑 exit 2 ⇒ ABORTA
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `sdd/bin/slot.sh` | executor único dos 4 slots: lê, roda, traduz o exit | bash 3.2 + python3 stdlib (só para ler o YAML) |
| `sdd/bin/test-baseline.sh --touched` | conta como do diff o teste ao lado da fonte alterada | bash 3.2 + python3 stdlib (bloco já existente) |
| `sdd-release` 2.9.0 | chama os 3 smokes e os testes do diff; o bloco do OK diz o resultado na linha Verificações | texto de skill |
| `sdd-build` 2.7.0 + `aplicar-migration.md` | checagem do SQL antes da prévia, fail-closed | texto de skill |
| `sdd/config.example.yaml` + docs | os 4 slots vazios, comentados; guia de adaptação EN/PT; tabela de exits | YAML e Markdown |

---

## Key Decisions

### Decision 1: Executor único com lista fechada de chaves

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o contrato de exit (vazio · 0 · 2 · 10 · outro) vale para os 4 slots; escrito em 2 skills, ele divergiria, e um teste de texto não prova comportamento (LM-001).

**Choice:** `sdd/bin/slot.sh` aceita só `smoke.before_ok_cmd`, `smoke.before_push_cmd`, `smoke.after_deploy_cmd`, `schema.check_cmd`; o `SDD_MOMENTO` sai da chave (`before_ok`, `before_push`, `after_deploy`, `schema_check`).

**Rationale:** um lugar só para o contrato, testado com scripts falsos; chave fora da lista é erro de chamada, não um slot que "pula".

**Alternatives Rejected:**
1. Executor genérico para qualquer `secao.chave` — rejeitada porque um erro de digitação viraria PULADO silencioso.
2. Só texto nas skills — rejeitada no brainstorm (abordagem B).

**Consequences:** slot novo no futuro = 1 linha na lista do script; ganhamos o erro de digitação pego na hora (64).

---

### Decision 2: Exits 0 · 2 · 3 · 10 · 11 · 64

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o contrato do projeto é 0/2/10; o executor precisa ainda dizer "pulado", "inconclusivo" e "chamada errada" sem colidir com eles.

**Choice:** 0 `OK` · 2 `REPROVOU` · 3 `INCONCLUSIVO` (exit do comando que não é 0, 2 nem 10, sinal, ou python3 ausente) · 10 `NADA A MEDIR` · 11 `PULADO` · 64 `ERRO DE USO`. O exit real do comando é sempre impresso.

**Rationale:** 3 já significa inconclusivo em `verify-gate.sh` e `test-baseline.sh`; 11 separa PULADO de OK lendo só o número (Clarifications do DEFINE).

**Alternatives Rejected:**
1. PULADO = 0 com `RESULTADO: PULADO` — rejeitada pelo Roberto no Define.
2. Repassar o exit cru — rejeitada porque 1 ou 127 passariam por "reprovou" ou "erro" ao gosto de quem lê.

**Consequences:** quem chama trata 6 códigos; ganhamos "nunca verde por omissão".

---

### Decision 3: Arquivos vão no fim do comando, por `"$@"`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o `schema.check_cmd` recebe os `.sql` do manifest (o gate de schema do privado é chamado assim); nome com espaço não pode quebrar.

**Choice:** `bash -c "${CMD} \"\$@\"" slot "$@"` na pasta onde o script foi chamado: os arquivos chegam como argumentos posicionais separados, no fim do comando. Antes de rodar, o comando montado passa por `bash -n -c` (erro de sintaxe ⇒ 64, nunca o 2 que o bash dá e que leríamos como REPROVOU), e um comentário `#` do shell no comando (quem decide é o próprio bash: o script define uma função com o comando, sem executá-la, e confere se o `"$@"` sobreviveu em `declare -f`; `a#b`, uma URL com `#/` e `a\ #b` rodam) ⇒ 64, porque os arquivos cairiam dentro dele. O comentário do config diz: uma linha só; com `|`, `;` ou `&&`, aponte para um script.

**Rationale:** é o jeito de o comando receber argumentos sem `eval` de texto do usuário; o shell do projeto continua sendo o `bash`.

**Alternatives Rejected:**
1. `SDD_ARQUIVOS` separado por nova linha — rejeitada porque o gate de schema do privado lê argumentos, e um nome com nova linha quebraria.
2. Placeholder `{arquivos}` no comando — rejeitada porque exige substituição de texto, com quoting frágil (LM-002).

**Consequences:** um comando com pipe recebe os arquivos no último elemento; registrado no comentário do config e no guia.

---

### Decision 4: Pasta comum derivada da pasta git comum

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** os 3 smokes rodam em chamadas separadas (variável de shell não passa de uma para a outra) e, no passo 5 da release, há um worktree temporário além da pasta da frente.

**Choice:** `SDD_SLOT_DIR` = `--dir`, ou `${TMPDIR:-/tmp}/sdd-slot-<12 hex>/<feature ou _sem-feature>`, com o hex de `git hash-object --stdin` sobre `(cd "$(git rev-parse --git-common-dir)" && pwd -P)` (caminho físico, igual em todas as worktrees, subpastas e caminhos com symlink; `--path-format` exigiria git 2.31, acima do piso 2.20); sem git, sobre o `pwd -P`. Criada com `mkdir -p` antes do comando; falha ⇒ 64. No momento `before_ok`, a pasta **padrão** é esvaziada antes (a 2ª release da mesma feature não lê o que a 1ª deixou); a de `--dir` nunca é apagada. `SDD_ARVORE` = `--arvore` ou a raiz do repositório: a pasta com a árvore do `SDD_COMMIT`, que o comando mede.

**Rationale:** a mesma pasta nas 3 chamadas de qualquer worktree, fora da árvore de trabalho (nada vai para o commit); mesmo desenho do `T=` da fronteira de escrita.

**Alternatives Rejected:**
1. Pasta dentro do repositório (`sdd/reports/smoke/`) — rejeitada porque screenshots iriam para o diff.
2. Derivar da raiz do worktree — rejeitada porque o worktree temporário do passo 5 teria outra pasta.

**Consequences:** a pasta sobrevive à release até o sistema limpar o `TMPDIR`; ganhamos estado comum sem o Open guardar estado.

---

### Decision 5: Leitura do slot por python3, com aspas YAML simples

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o config é YAML de 1 nível sem âncoras (cabeçalho do `config.example.yaml`); o comando vem entre aspas e pode ter `#`, `"` e `\`.

**Choice:** bloco python stdlib, como o de `test-baseline.sh:63-82`, generalizado: seção de topo `^<secao>:`, chave `^\s+<chave>:\s*(.*)$`; valor entre `"…"` (com `\\` e `\"`) ou `'…'` (com `''`), ou sem aspas (corta ` #`). Aspas abertas sem fechar ⇒ 64 com a linha. Sem python3 ⇒ 3.

**Rationale:** mesmo dialeto dos scripts vizinhos; nada de dependência nova.

**Alternatives Rejected:**
1. `awk`/`sed` — rejeitada porque aspas com escape quebram o `sed` (LM-002).
2. PyYAML — rejeitada porque não é stdlib.

**Consequences:** YAML com bloco multilinha (`|`) não é lido; o comentário do config pede uma linha só.

---

### Decision 6: Os 3 momentos da release

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o "antes do OK" precisa do código que vai subir; o "antes do push" mede a produção velha; o "depois do deploy" precisa do deploy confirmado.

**Choice:** item **6b** da FASE 1 (depois dos gates pré-push do item 6, antes do bloco do OK), chamado da pasta da frente (lá estão as dependências do projeto): `bash sdd/bin/slot.sh smoke.before_ok_cmd --feature {F} --base origin/{default_branch} --commit <SHA landado no passo 5> --arvore <worktree temporário do passo 5>`; o contrato diz que o comando mede `SDD_COMMIT`/`SDD_ARVORE`, não a pasta onde roda. 0 ⇒ ok; 2 ⇒ FAIL-candidato; 3 ⇒ aviso; 64 ⇒ aviso "erro de configuração"; 10 e 11 declarados. Item **7b** da FASE 2 (depois do "sim", antes do push 8): `smoke.before_push_cmd` com os mesmos argumentos; nenhum exit segura o push, todos vão para o relatório. Item **10**, depois de `GIT_TERMINAL_PROMPT=0 git fetch` (o SHA do merge do PR nasce no remoto):

| Situação do deploy | Smoke depois do deploy |
|---|---|
| `deploy-do-sha.sh` 0 (no ar) ou 3 (publicado, sem verificação) | roda com `--commit <SHA publicado>` |
| sem workflow, `deploy.cmd` saiu 0 | roda |
| `deploy-do-sha.sh` 2 ou 4, `deploy.cmd` ≠ 0, deploy pulado ou diff que não publica | não roda; o relatório diz por quê |

Resultado: 0 ⇒ ok; 2 ⇒ `[D1 · não se desfaz]` reverter · corrigir · seguir com motivo · não sei; 3 e 64 ⇒ pendência 🐛 na ficha, nunca ✅; 10 e 11 declarados.

**Rationale:** casa com o 6b/7b/10b do privado; o OK continua sendo uma pergunta só.

**Alternatives Rejected:**
1. Smoke antes do OK na FASE 0 — rejeitada porque o commit atômico e o landing ainda não existem; o smoke mediria a branch, não o que sobe.
2. Smoke depois do deploy sem esperar o `deploy-do-sha` — rejeitada porque mediria o código velho.

**Consequences:** a FASE 1 ganha 1 item e a FASE 2 ganha 1; ganhamos smoke sobre o SHA certo.

---

### Decision 7: O bloco do OK não ganha rótulo

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** `tests/test_contrato_build_release.py:43-56` fixa os 8 rótulos, a ordem e a pergunta única.

**Choice:** a linha `**Verificações:**` ganha `· testes do diff <ok | ok, N fora do diff | inconclusivo — WAIVABLE | pulado — test_cmd vazio> · smoke <ok | reprovou — FAIL-candidato | nada a medir | pulado — slot vazio | inconclusivo | erro de configuração>` (texto idêntico ao AT-009 do DEFINE v1.1); o exemplo do bloco em `references/como-falar.md` acompanha. A falha nova com 2 já abortou na 0a e não chega ao bloco.

**Rationale:** a informação entra sem mudar o contrato do bloco.

**Alternatives Rejected:**
1. Rótulo novo `**Smoke visual:**` — rejeitada porque quebraria o contrato da F3/F14.

**Consequences:** a linha Verificações fica mais longa; ganhamos zero mudança de forma.

---

### Decision 8: O teste ao lado é o arquivo que existe na mesma pasta

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** o `--touched` monta `tocs` só com nomes de teste (`test-baseline.sh:189-197`); o id da falha cita o arquivo em vitest, deno, pytest e unittest, não em Go nem em jest (`● Suite › teste`).

**Choice:** para cada caminho tocado que não é teste e não começa com `sdd/`: com extensão `.ts`, `.tsx`, `.js`, `.jsx`, `.mjs` ou `.cjs`, os candidatos `<pasta>/<nome>.test.<e>` e `<pasta>/<nome>.spec.<e>` para cada `<e>` da família; com `.py`, `<pasta>/test_<nome>.py` e `<pasta>/<nome>_test.py`. Só entra o candidato que **existe no disco**, numa lista própria (`vizinhos`), casada com âncora: o id **começa** pelo caminho do teste (vitest `src/foo.test.ts > …`, pytest `pkg/test_calc.py::…`, deno `src/foo.test.ts::…`, com ou sem `./`) ou, no unittest (id sem `/`), tem o módulo como segmento, `(^|\.)test_calc\.`. O teste tocado diretamente continua com o casamento por substring de hoje (não estreitar uma heurística que já existe, LM-005).

**Rationale:** é a regra do teste do diff do privado, generalizada às 2 famílias em que o id carrega o arquivo.

**Alternatives Rejected:**
1. Go pelo pacote — rejeitada pelo Roberto no Define.
2. Espelho `tests/` — fora de escopo no brainstorm.

**Consequences:** jest sem caminho no id e Go seguem "fora do diff" (limite declarado no cabeçalho do script); ganhamos o par fonte → teste nas famílias em que ele é verificável.

---

### Decision 9: Checagem de schema entre "já aplicada?" e a prévia

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** migration já aplicada não passa por apply; a prévia e o bloco de confirmação são o último ponto antes do banco.

**Choice:** seção nova `## 2b. Checagem do SQL (slot schema.check_cmd)` em `aplicar-migration.md`: só para as migrations que vão ser aplicadas; o log grava o exit do próprio `slot.sh`:

```bash
cmd='bash sdd/bin/slot.sh schema.check_cmd --feature {F} <arquivos>'
{ echo "\$ $cmd"; eval "$cmd"; echo "[exit=$?]"; } > sdd/reports/evidence/{F}/SCHEMA-CHECK.log 2>&1
```

0 segue; 10 segue e diz "nada a conferir"; 11 diz "checagem de schema pulada: slot vazio"; 2 não aplica, mostra a saída e volta ao SQL; 3 ou 64 não aplica e diz que o problema é da ferramenta ou do config. Se a prévia (§3) acrescentar migration pendente fora do manifest e a pessoa a incluir, a §2b roda de novo sobre ela antes do bloco (`SCHEMA-CHECK-2.log`). O bloco de confirmação ganha `**Checagem:** <ok | nada a conferir | pulada — slot vazio>`; o passo 4b da `sdd-build` cita a checagem.

**Rationale:** banco não tem undo (decisão 8 do brainstorm); a checagem vem antes de a pessoa ver o bloco, como a divergência de projeto.

**Alternatives Rejected:**
1. Checar dentro do bloco de confirmação — rejeitada porque 2 viraria uma segunda pergunta.

**Consequences:** uma chamada a mais no 4b; ganhamos o SQL conferido antes do único OK do banco.

---

### Decision 10: Documentos SDD na branch `docs/f15-slots`

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-09 |

**Context:** a `docs/incorporar-starter` está em uso na worktree `sdd-open-docs-f16`, que esta frente não toca.

**Choice:** os documentos desta frente ficam fora do commit do produto e vão para a branch `docs/f15-slots`, nascida de `origin/docs/incorporar-starter`, numa worktree temporária própria; o registro "reabertos por decisão do Roberto" entra no §8.2 do plano nessa branch. Push só com o OK.

**Rationale:** mesmo modelo da F21; nada da RDD em `main`.

**Alternatives Rejected:**
1. Commit na `docs/incorporar-starter` por plumbing — rejeitada porque deixaria a worktree da F16 atrás do próprio HEAD.

**Consequences:** um merge da `docs/f15-slots` na família fica para a frente que fechar a F15.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/slot.sh` | Create | executor dos 4 slots (Decisions 1–5) | (general) | None |
| 2 | `sdd/bin/test-baseline.sh` | Modify | teste ao lado da fonte no `--touched` (Decision 8); cabeçalho com o limite Go/jest | (general) | None |
| 3 | `sdd/config.example.yaml` | Modify | seções `smoke:` e `schema:` com os 4 slots `""` e comentários | (general) | 1 |
| 4 | `.agents/skills/sdd-release/SKILL.md` | Modify | 2.9.0: slots, 0a item 9, 0b, 0d, 6b, 7b, 10, Verificações, abortar, "por que" | (general) | 1, 2 |
| 5 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | a pergunta `[D1 · não se desfaz]` do smoke reprovado depois do deploy e o exemplo do bloco com a linha Verificações nova | (general) | 4 |
| 6 | `.agents/skills/sdd-build/references/aplicar-migration.md` | Modify | seção 2b e a linha Checagem do bloco (Decision 9) | (general) | 1 |
| 7 | `.agents/skills/sdd-build/SKILL.md` | Modify | 2.7.0: o 4b cita a checagem | (general) | 6 |
| 8 | `docs/adaptation-guide.md` | Modify | seção dos 4 slots | (general) | 3 |
| 9 | `docs/pt-BR/adaptation-guide.md` | Modify | a mesma seção em PT | (general) | 8 |
| 10 | `docs/cli-conventions.md` | Modify | linha do `slot.sh` na tabela de exits e as palavras do RESULTADO | (general) | 1 |
| 11 | `MANIFEST.txt` | Modify | `sdd/bin/slot.sh`, `tests/test_slot.py`, `tests/test_f15_slots_textos.py` | (general) | 1, 12, 14 |
| 12 | `tests/test_slot.py` | Create | AT-001 a AT-005 com scripts falsos e 2 worktrees | (general) | 1 |
| 13 | `tests/test_test_baseline.py` | Modify | AT-006 e AT-007 | (general) | 2 |
| 14 | `tests/test_f15_slots_textos.py` | Create | AT-008 a AT-011 (textos, config, docs, contratos, MANIFEST e a família de termos privados de `test_f12_textos.py` sobre a lista fixa dos arquivos tocados, sem o próprio teste) | (general) | 3, 4, 5, 6, 7, 8, 9, 10, 20 |
| 15 | `tests/test_contrato_build_release.py` | Modify | versões 2.9.0 / 2.7.0 | (general) | 4, 7 |
| 16 | `tests/test_correcoes_w0.py` | Modify | versão da `sdd-build` 2.7.0 | (general) | 7 |
| 17 | `tests/test_f14_textos.py` | Modify | versão da `sdd-release` 2.9.0 | (general) | 4 |
| 18 | `tests/test_f14_drive_textos.py` | Modify | versão da `sdd-release` 2.9.0 | (general) | 4 |
| 19 | `tests/test_f13_textos.py` | Modify | `smoke.`/`smoke:` saem da lista de proibidos do config (reabertos por decisão do Roberto); os outros cortados continuam proibidos | (general) | 3 |
| 20 | `sdd/WORKFLOW_CONTRACTS.yaml` | Modify | contrato `slot` (script, chaves, exits, variáveis, consumidores) | (general) | 1, 4, 7 |
| 21 | `tests/test_decisoes_lint.py` | Modify | contagem fixada de perguntas 25 → 26 (a pergunta D1 do smoke depois do deploy) | (general) | 5 |

**Total Files:** 21

---

## Landmines aplicáveis

Varredura rodada em 2026-11-09 (refeita na v1.1 com `heurística`) com `slot`, `smoke`, `schema`, `migration`, `test-baseline`, `touched`, `config`, `release`, `exit 0`, `baseline`, `verify-gate`, `asserção`, `review`, `untracked`; entradas abertas inteiras.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que só confere fiação fica verde com `if (true)` | `LM-001` | ✔ tratado | `tests/test_slot.py` executa o `slot.sh` com scripts falsos dos dois lados (0/2/10 e 1/7/127); sabotagens S1–S3 com mutante que derruba asserção nomeada |
| Asserção que não avalia nada sai `exit 0`; precisa de linha de base vermelha | `LM-002` | ✔ tratado | os testes novos rodam contra `9d8ac24` antes da mudança (log `BASELINE-RED.log`); o AT-006 já registra 0 → 2 |
| Review de "não commitado" com untracked ao lado revisa o vazio | `LM-003` | ✔ tratado | os documentos SDD ficam fora do commit; a revisão adversarial roda sobre commit com `--paths` e o `git diff --stat` é conferido contra a lista |
| Migration "aplicada" porque saiu `exit 0` | `LM-004` | ✔ tratado | a checagem 2b vem **antes** da prova por leitura e não a substitui; `exit 0` do `schema.check_cmd` só libera a prévia |
| Conserto que estreita uma heurística sobre texto livre abre o caso vizinho | `LM-005` | ✔ tratado | o casamento por substring do teste tocado direto não muda; os vizinhos novos usam âncora (Decision 8) e os 2 falsos positivos viram teste (AT-007) |
| Script que só roda dentro de git falha no gate sem `.git`; asserção "bloqueou" que aceita qualquer exit ≠ 0 | `LM-006` | ✔ tratado | `slot.sh` sem git cai para `pwd -P` (Decision 4) e o teste roda numa pasta sem `.git`; todo teste confere o exit **exato** (2, 3, 10, 11, 64), nunca `!= 0` |

---

## Contrato de aceite

N.A. (1 camada): o Open não tem `layers:` preenchido no próprio repositório; o manifest é script, texto de skill e teste.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1–18 | o Open não tem agentes especialistas; o Build trata direto |

**Agent Discovery:**
- Scanned: `.agents/`, `.claude/agents/` (inexistente no Open)
- Matched by: nenhum

---

## Code Patterns

Sem `sdd/patterns/` para a camada de scripts; candidato a pattern: `sdd/bin` (executor de slot).

### Pattern 1: Leitura do slot (python3 stdlib, dentro do `slot.sh`)

```python
import re, sys
secao, chave = sys.argv[1].split(".", 1)
try:
    linhas = open("sdd/config.yaml", encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    print("AUSENTE"); sys.exit(0)
dentro = False
for n, l in enumerate(linhas, 1):
    if l.lstrip().startswith("#") or not l.strip():
        continue  # comentário na coluna 0 não fecha a seção
    if re.match(r"^\S", l):
        dentro = l.split("#", 1)[0].strip() == secao + ":"
        continue
    m = re.match(r"^\s+" + re.escape(chave) + r":\s*(.*)$", l) if dentro else None
    if not m:
        continue
    v = m.group(1).strip()
    if v[:1] == '"':
        out, i = [], 1
        while i < len(v) and v[i] != '"':
            if v[i] == "\\" and i + 1 < len(v):
                i += 1
            out.append(v[i]); i += 1
        if i >= len(v):
            print("ASPAS %d" % n); sys.exit(0)
        v = "".join(out)
    elif v[:1] == "'":
        fim = re.match(r"'((?:[^']|'')*)'", v)
        if not fim:
            print("ASPAS %d" % n); sys.exit(0)
        v = fim.group(1).replace("''", "'")
    else:
        v = v.split(" #", 1)[0].strip()
    print("VALOR"); sys.stdout.write(v); sys.exit(0)
print("AUSENTE")
```

### Pattern 2: Rodar e traduzir o exit (bash 3.2)

```bash
trap 'printf "⚠️  slot.sh interrompido por sinal\nRESULTADO: INCONCLUSIVO\n→ rode de novo; isto não é verde.\n"; exit 3' INT TERM
bash -n -c "${CMD} \"\$@\"" 2>"${ERR}" || uso "o comando de ${CHAVE} tem erro de sintaxe: $(head -1 "${ERR}")"
echo "▶ ${CHAVE} (${MOMENTO}): ${CMD}"
SDD_MOMENTO="${MOMENTO}" SDD_FEATURE="${FEATURE}" SDD_BASE="${BASE_SHA}" SDD_COMMIT="${COMMIT_SHA}" \
SDD_ARVORE="${ARVORE}" SDD_SLOT_DIR="${DIR}" bash -c "${CMD} \"\$@\"" slot ${ARQS+"${ARQS[@]}"}
RC=$?
case "${RC}" in
  0)  printf 'RESULTADO: OK\n→ siga para o próximo passo.\n'; exit 0 ;;
  2)  printf 'RESULTADO: REPROVOU\n→ %s\n' "${ACAO_REPROVOU}"; exit 2 ;;
  10) printf 'RESULTADO: NADA A MEDIR\n→ diga que nada foi medido neste momento e siga.\n'; exit 10 ;;
  *)  [ "${RC}" -gt 128 ] && echo "⚠️  o comando morreu pelo sinal $((RC - 128))"
      echo "⚠️  ${CHAVE} saiu ${RC}, fora do contrato (0 ok · 2 reprovou · 10 nada a medir)"
      printf 'RESULTADO: INCONCLUSIVO\n→ confira a saída acima; isto não é verde.\n'; exit 3 ;;
esac
```

(`${ARQS+"${ARQS[@]}"}` evita o "unbound variable" do bash 3.2 com `set -u` e array vazio.)

### Pattern 3: Configuration Structure

```yaml
# Smoke visual na release (sdd/bin/slot.sh; docs/adaptation-guide.md). Um comando por momento; vazio =
# o momento é pulado e a release diz que pulou. O comando sai 0 ok · 2 reprovou · 10 nada a medir;
# qualquer outro exit é inconclusivo, nunca verde. Recebe SDD_MOMENTO, SDD_FEATURE, SDD_BASE, SDD_COMMIT
# SDD_ARVORE (a árvore a medir) e SDD_SLOT_DIR (pasta comum aos 3 momentos, fora do repositório).
# Uma linha só, sem comentário (#) no comando; com |, ; ou &&, aponte para um script.
smoke:
  # Antes do OK, sobre o commit que vai subir: 2 vira FAIL-candidato no bloco do OK.
  before_ok_cmd: ""
  # Depois do "sim", antes do push (a produção ainda tem o código velho): só registra, nunca segura o push.
  before_push_cmd: ""
  # Depois do deploy confirmado: 2 para a release com a pergunta reverter, corrigir ou seguir com motivo.
  after_deploy_cmd: ""

# Checagem das migrations antes de aplicar (passo 4b do build). Recebe os .sql como argumentos, no fim do
# comando. 0 ok · 2 reprovou · 10 nada a conferir; 2 ou qualquer exit fora disso = a migration não é aplicada.
schema:
  check_cmd: ""
```

---

## Data Flow

```text
1. release 0a.9   test-baseline.sh --touched ─► VERDE/PULADO (0) │ VERMELHO (2: aborta) │ INCONCLUSIVO (3: WAIVABLE)
2. release 5      landa no worktree temporário ─► SHA landado
3. release 6b     slot.sh smoke.before_ok_cmd --commit <landado> ─► Verificações + Veredito (2 = FAIL-candidato)
4. release 7      bloco do OK ─► "sim"
5. release 7b     slot.sh smoke.before_push_cmd ─► registro (nunca segura)
6. release 8–10   push → deploy → deploy-do-sha (0|3) → slot.sh smoke.after_deploy_cmd --commit <publicado>
                  2 ⇒ [D1] reverter · corrigir · seguir com motivo · não sei
7. build 4b §2b   slot.sh schema.check_cmd <.sql> ─► SCHEMA-CHECK.log ─► 0/10/11 segue · 2/3/64 não aplica
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| comando do projeto em cada slot | processo filho (`bash -c`) | o do ambiente do agente; o executor não lê segredo |
| git | `rev-parse` (common dir, SHAs) | nenhuma |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit (processo) | AT-001: 0/2/10 e a linha `→`; arquivos com espaço chegam separados | `tests/test_slot.py` | unittest + `Sandbox` | os 3 exits do contrato |
| Unit (negativo) | AT-002: 1, 7, 127 e sinal (`kill -TERM $$` no comando) ⇒ 3 com o exit real; TERM no próprio `slot.sh` ⇒ 3 | `tests/test_slot.py` | unittest | 4 casos |
| Unit (matriz) | AT-003: `""`, chave ausente, seção ausente, comentário na coluna 0 entre a seção e a chave (lê a chave), sem `sdd/config.yaml` ⇒ 11, nada roda | `tests/test_slot.py` | unittest | 4 casos |
| Unit (uso) | AT-004: chave fora da lista, flag sem valor, aspas YAML sem fechar, comando `| x`, aspa do shell sem fechar, `# comentário`, `--commit` inexistente ⇒ 64, nada roda | `tests/test_slot.py` | unittest | 3 casos |
| Unit (estado) | AT-005: o script falso grava `env` + argv; 2 worktrees, uma subpasta e um caminho com symlink dão a mesma `SDD_SLOT_DIR`; `before_ok` esvazia a pasta padrão e não a de `--dir`; sem `.git` funciona com `SDD_COMMIT` vazio | `tests/test_slot.py` | unittest + git | 5 variáveis, 2 worktrees, sem git |
| Unit (regressão vermelha) | AT-006: `src/foo.ts`→`foo.test.ts` (vitest), `src/bar.tsx`→`bar.spec.tsx` (vitest), `pkg/calc.py`→`test_calc.py` (unittest) ⇒ 2 | `tests/test_test_baseline.py` | unittest | 3 casos, base vermelha em `9d8ac24` |
| Unit (não regressão) | AT-007: teste sem relação, Go, `lib/foo.test.ts` com `src/foo.ts` alterado, `other.test_calc_total` com `pkg/calc.py` alterado ⇒ 0 "fora do diff"; teste tocado direto ⇒ 2 | `tests/test_test_baseline.py` | unittest | 4 casos + os 14 testes existentes |
| Texto | AT-008 a AT-011: release (itens 9, 0b, 0d, 6b, 7b, 10, abortar), Verificações, aplicar-migration §2b, 4b, config, docs, MANIFEST, grep anti-RDD | `tests/test_f15_slots_textos.py` | unittest | 1 teste por AT, mais o grep |
| Contrato | AT-009: rótulos, ordem, pergunta única | `tests/test_contrato_build_release.py` | unittest | sem mudança além da versão |
| Gate | suíte inteira numa cópia sem `.git` | Verify Gate do DEFINE | `git archive` + `publish-gate.sh` + unittest (bash 3.2, Python 3.9) | exit 0 |
| Sabotagem | S1 `slot.sh`: `*)` sai 0 ⇒ cai `test_saida_fora_do_contrato_e_inconclusivo`; S2 `test-baseline.sh`: sem o laço dos candidatos ⇒ cai `test_touched_conta_teste_ao_lado_da_fonte`; S3 `slot.sh`: sem `"$@"` ⇒ cai `test_schema_recebe_os_arquivos_como_argumentos`; S4 `aplicar-migration.md` sem a §2b ⇒ cai `test_aplicar_migration_checa_antes_da_previa` | `sdd/reports/evidence/F15_SLOTS/SABOTAGENS.log` | mutante + `git checkout` | 4 de 4 derrubam teste nomeado |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| slot vazio, ausente, sem config | PULADO (11), nada roda, diz o caminho do config | No |
| comando sai fora do contrato / sinal / não encontrado | INCONCLUSIVO (3) com o exit real | No |
| chave desconhecida, flag sem valor, aspas sem fechar, `--base`/`--commit` dado e inexistente, `mkdir` falha | ERRO DE USO (64) com causa e conserto | No |
| `--base` padrão inexistente (sem remoto) | `⚠️ SDD_BASE vazio: origin/<branch> não existe` e segue | No |
| `HEAD` não resolve (cópia sem git) | `⚠️ SDD_COMMIT vazio: sem git` e segue | No |
| erro de sintaxe no comando, ou `#` do shell nele | ERRO DE USO (64) antes de rodar, com a 1ª linha do `bash -n` | No |
| INT/TERM no próprio `slot.sh` | INCONCLUSIVO (3) pelo `trap` | No |
| python3 ausente | INCONCLUSIVO (3), "instale python3 ≥ 3.9" | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `smoke.before_ok_cmd` | string | `""` | smoke antes do OK, sobre o commit landado |
| `smoke.before_push_cmd` | string | `""` | smoke depois do "sim", antes do push |
| `smoke.after_deploy_cmd` | string | `""` | smoke depois do deploy confirmado |
| `schema.check_cmd` | string | `""` | checagem dos `.sql` antes do apply |

---

## Security Considerations

- O executor roda um comando que o próprio projeto escreveu no seu config, com os mesmos privilégios do agente; não lê nem imprime segredo.
- Os arquivos vão como argumentos (`"$@"`), nunca interpolados no texto do comando: nome de arquivo não vira código.
- A pasta comum fica no `TMPDIR` do usuário, fora do repositório: screenshot não entra em commit.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | saída do comando repassada; `▶ <chave> (<momento>): <cmd>` antes; `RESULTADO:` + `→` depois |
| Metrics | — |
| Tracing | o log `SCHEMA-CHECK.log` em `evidence/`; os resultados dos smokes no relatório final e na ficha |

---

## Advisor Ledger

Revisão de contexto fresco (agente sem a conversa, escolha D3 do Roberto: revisão paga só no diff do build), 2026-11-09: 20 notas (4 HIGH, 7 MEDIUM, 9 LOW), veredito CORRIGIR ANTES DO BUILD; todas aplicadas na v1.1.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | `test_f13_textos.py:297` proíbe `smoke.`/`smoke:` no config | HIGH | APLICADA | manifest #19 |
| 2 | ref de projeto privado no critério anti-RDD vazaria para o público | HIGH | APLICADA | DEFINE v1.1 Success Criteria e AT-011; termo privado só no `PUBLISH_GATE_EXTRA_PATTERNS` |
| 3 | erro de sintaxe do comando sai 2 = REPROVOU | HIGH | APLICADA | Decision 3 (`bash -n`), AT-004 |
| 4 | smoke antes do OK mede a branch, não o SHA landado | HIGH | APLICADA | Decision 6 (`--arvore <worktree temporário>`), AT-005 `SDD_ARVORE`, AT-008 |
| 5 | smoke depois do deploy sem gatilho sem workflow / com deploy pulado; 10/11/64 sem ação | MEDIUM | APLICADA | Decision 6, tabela do item 10; AT-008 |
| 6 | SHA do merge do PR não existe localmente ⇒ 64 | MEDIUM | APLICADA | Decision 6 (`git fetch` antes), AT-008 |
| 7 | `git-common-dir` relativo × físico | MEDIUM | APLICADA | Decision 4 (`cd … && pwd -P`), AT-005 com subpasta e symlink |
| 8 | casamento por substring dá falso positivo/negativo | MEDIUM | APLICADA | Decision 8 (âncora só para os vizinhos), AT-006/AT-007, LM-005 na tabela |
| 9 | migration que a prévia acrescenta passa sem checagem | MEDIUM | APLICADA | Decision 9 (2ª checagem antes do bloco), AT-010 |
| 10 | grep "no diff" não roda sem `.git` | MEDIUM | APLICADA | AT-011 lista fixa, no padrão `SemRDD.ARQUIVOS` de `test_f12_textos.py:191` |
| 11 | texto da linha Verificações diverge entre DEFINE e DESIGN; exemplo do `como-falar.md` | MEDIUM | APLICADA | Decision 7 = AT-009 v1.1; manifest #5 |
| 12 | comentário na coluna 0 fecha a seção ⇒ PULADO calado | LOW | APLICADA | Pattern 1, AT-003 |
| 13 | `#` no comando engole os arquivos | LOW | APLICADA | Decision 3 (`shlex` com `comments=True`), AT-004 |
| 14 | exit 64 dos smokes sem ação | LOW | APLICADA | Decision 6, AT-008 |
| 15 | sinal no próprio `slot.sh` sai 130/143 | LOW | APLICADA | Pattern 2 (`trap`), AT-002 |
| 16 | `SDD_COMMIT` sem git | LOW | APLICADA | Error Handling, AT-005 |
| 17 | item 9 em paralelo com o Verify Gate dá falha falsa | LOW | APLICADA | AT-008 (depois do item 4, em sequência) |
| 18 | comando do log e ação de 3/64 na §2b | LOW | APLICADA | Decision 9 (bloco colado), AT-010 |
| 19 | A-001 não validada, linha errada | LOW | APLICADA | DEFINE v1.1 A-001 `bin/sdd-open.sh:587-593` |
| 20 | pasta comum vaza entre releases da mesma feature | LOW | APLICADA | Decision 4 (`before_ok` esvazia a pasta padrão), AT-005 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-09 | design-agent | Initial version |
| 1.1 | 2026-11-09 | design-agent | 20 notas da revisão fresca aplicadas (Advisor Ledger); manifest 18 → 20 |
| 1.2 | 2026-11-09 | design-agent | avaliação ciclo 1: valor de flag que começa com `--` ⇒ 64; o `shlex` (que via comentário no meio da palavra) trocado por uma varredura com a regra do bash; `tests/test_decisoes_lint.py` (contagem 25 → 26) entrou no manifest (21) |
| 1.3 | 2026-11-10 | design-agent | revisão claude (R1–R3) e avaliação ciclo 2: o `trap` vem logo depois das flags; o `before_ok` esvazia a pasta padrão mesmo com o slot vazio; o id relativo à subpasta do runner conta como do vizinho; o comentário do shell é decidido pelo próprio bash (`declare -f` de uma função com o comando), não por varredura em Python; texto depois das aspas YAML sai 64; `maxsplit=1` |
| 1.4 | 2026-11-10 | design-agent | revisão paga rodada 2 (R1, R2): comando que termina em `;`, `&`, `|` ou `&&` sai 64 (o exit seria o do `"$@"` vazio); arquivo, `--arvore` e `--dir` relativos valem a partir de onde o script foi chamado; N1 do auditor rebatido por medição (`evidence/F15_SLOTS/REVIEW-N1-declare-f.log`) |
| 1.5 | 2026-11-10 | design-agent | revisão paga rodada 3: a checagem de separador não ancora no fim da linha (o `declare -f` põe `2>&1`, `>` e `<` depois do `"$@"`); `-h` só com o cabeçalho; o teste anti-termos cobre os 21 arquivos, com isenções nomeadas |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F15_SLOTS.md`
