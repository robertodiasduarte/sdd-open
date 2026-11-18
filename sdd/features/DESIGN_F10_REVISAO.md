# DESIGN: F10 Revisão adversarial — núcleo

> `sdd/bin/adversarial-review.sh` em bash 3.2 com o núcleo em Python stdlib embutido; um adapter por engine em `sdd/bin/adapters/` (`claude`, `codex`, `gemini`, `openrouter`), cada um com "disponível", "invocar" e "extrair"; `sdd/review/` com o registry de 9 colunas, os preços lidos ao vivo e 3 prompts de runtime; o `sdd-fluxo.sh loop` ganha 2º revisor, revisão rasa e desempate por delta; `sdd-build` passo 0, `sdd-design` e `sdd-release` 0a ligam o script; o `init` copia `sdd/review/`.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F10_REVISAO |
| **Date** | 2026-10-31 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F10_REVISAO.md` |
| **DEFINE** | `sdd/features/DEFINE_F10_REVISAO.md` (v1.3) |
| **UX REVIEW** | `sdd/reviews/UX_REVIEW_F10_REVISAO.md` (5 MUST, 2 SHOULD, 1 COULD) |
| **LLM Prompts** | true |
| **Status** | Ready for Build |

Fatos medidos nesta fase (2026-10-31, scratchpad, não versionados):
- `claude -p --output-format json --tools "" --safe-mode --no-session-persistence` com o prompt por stdin devolve o objeto com `result` (texto), `total_cost_usd`, `usage` (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`) e `modelUsage` (modelo → `costUSD`).
- `codex exec -s read-only --skip-git-repo-check --ephemeral --json -` emite JSONL: `item.completed` com `item.type = agent_message` e `item.text`; `turn.completed` com `usage.input_tokens` e `output_tokens`; sem custo.
- `gemini -o json` nesta máquina sai 41 com `error.type = ProjectIdRequiredError` (credencial de projeto ausente): é um caso real de AUTH.
- OpenRouter `POST /api/v1/chat/completions` com `provider.data_collection = deny` e `require_parameters = true` e `usage.include = true`: `qwen/qwen3.7-plus` respondeu via Alibaba com `usage.cost` 0.0001792; chave falsa → HTTP 401, corpo com `"code":401` e `User not found.`.
- `GET /api/v1/models`: `qwen/qwen3.7-plus` 0.32 / 1.28 e `deepseek/deepseek-v4-flash` 0.091 / 0.182 US$ por milhão de tokens (entrada / saída).

---

## Architecture Overview

```text
 skill (design · build 0 e 5c · release 0a)          sdd/config.yaml  review.* · layers.* · project.default_branch
            │                                                   │
            ▼                                                   ▼
 sdd/bin/adversarial-review.sh  ── bash 3.2: args, raiz, python3 ──▶ núcleo Python (heredoc)
            │                                                   │
            │   1 papéis ◀── sdd/review/registry.tsv (9 col.)    │   --conferir / --ledger (sem engine)
            │   2 diff congelado (merge-base + intent-to-add) ──▶ diff.patch + sha256
            │   3 contexto SDD (teto context_max_kb) ──────────▶ context-sdd.md
            │   4 pasta ignorada? (git check-ignore)            │
            │   5 revisor ──┐                                   │
            │   6 2º revisor (gatilhos) ─┤  bash -c 'source sdd/bin/adapters/<adapter>.sh; adapter_invocar …'
            │   7 auditor ──┤                ├─ claude.sh   (CLI)  ─┐
            │   8 desempate ┘                ├─ codex.sh    (CLI)  ─┤ saída bruta → adapter_extrair → JSON normalizado
            │                                ├─ gemini.sh   (CLI)  ─┤ (texto, tokens, modelo, custo)
            │                                └─ openrouter.sh (HTTPS, urllib, data_collection=deny)
            │   9 vereditos (<<<VERDICTS) · custo (precos.tsv) · convergência
            ▼
 <review.output_dir>/EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>/
   META.txt · diff.patch · context-sdd.md · reviewer.md · reviewer.verdicts.jsonl
   [reviewer2.md · reviewer2.verdicts.jsonl] · auditor.md · auditor.verdicts.jsonl · [desempate.md]
            │
            ▼
 sdd/bin/sdd-fluxo.sh loop  (delta: revisor2_* · rasa · desempate_*) → 0 / 10 / 20 / 30 / 64
 sdd-release 0a: --conferir → linha review_externo: … → ledger → --ledger antes do push
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| `adversarial-review.sh` (frente) | ler argumentos, achar a raiz, exigir `python3`, repassar ao núcleo | bash 3.2 | argv, cwd | exit 0/2/64–68 | `python3`, `git` |
| núcleo Python | papéis, diff, contexto, R9, chamadas, parse, custo, META, resumo, `--conferir`, `--ledger`, `--dry-run` | Python 3.9 stdlib por heredoc (molde do `sdd-fluxo.sh`) | registry, config, prompts, repositório | pasta da revisão, stdout | adapters |
| adapters | um por engine: `adapter_disponivel`, `adapter_invocar <modelo> <prompt> <saida>`, `adapter_extrair <saida>` | bash 3.2; extração em `python3 -B -c`; `openrouter` com `urllib` | prompt montado | saída bruta; JSON normalizado em 1 linha | CLI ou `OPENROUTER_API_KEY` |
| `sdd/review/registry.tsv` | engines, papéis, sinais de falha, teto | TSV de 9 colunas, comentário `#` | — | — | — |
| `sdd/review/precos.tsv` | tarifa pública por modelo | TSV de 6 colunas, fonte e data | — | — | — |
| `sdd/review/prompts/` | contratos de saída do revisor, do auditor e do desempate | Markdown, escrito pela skill de prompt | — | — | — |
| `sdd-fluxo.sh loop` (delta) | ler 2º revisor, rasa e desempate | núcleo Python existente | META, jsonl, ledger | exits 0/10/20/30/64 | — |
| skills e templates | ligar o script (R1, R12, R13) e a pergunta D3 | Markdown | — | — | script |

---

## Key Decisions

### Decision 1: Frente em bash 3.2, núcleo em Python embutido, um adapter por engine com 3 funções

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | BRAINSTORM (Abordagem A); plano 8.0 regras 3 e 6 |

**Context:** o privado é um script zsh de 991 linhas e um `adapters.sh` de 1.114 linhas com 87 referências RDD; o Open roda em bash 3.2 e Python 3.9.

**Choice:** `sdd/bin/adversarial-review.sh` com a frente em bash (como o `sdd-fluxo.sh`) e todo o resto num núcleo `python3 -B - "$@" <<'PY'`. Cada adapter é um arquivo `sdd/bin/adapters/<adapter>.sh` que define 4 funções (`adapter_disponivel`, `adapter_invocar`, `adapter_extrair`, `adapter_credencial`). O núcleo chama o adapter com o **bash da frente** (`os.environ["SDD_REVIEW_BASH"]`, exportado pela frente a partir de `$BASH`) por `<bash> -c 'source "$1"; shift; adapter_invocar "$@"' _ <adapter> <modelo> <prompt> <saida> <saida.err>` em `subprocess.Popen(start_new_session=True)`; no estouro de `timeout_s`, `os.killpg` mata o grupo inteiro (a CLI neta incluída) — o teto de tempo fica no Python (o macOS não tem `timeout`). O stderr da CLI vai para `<saida>.err`, nunca para o arquivo que o `adapter_extrair` lê. `adapter_extrair <saida>` imprime uma linha JSON com `texto`, `tokens_entrada`, `tokens_saida`, `modelo`, `custo_usd` (número ou nulo). O diretório dos adapters é `sdd/bin/adapters`, trocável só por `SDD_REVIEW_ADAPTERS` (testes).

**Rationale:** um vendor novo é uma linha no registry (+ um arquivo se for uma CLI nova); o parser de cada formato mora junto da chamada que o produz; o núcleo não conhece vendor nenhum.

**Alternatives Rejected:**
1. Porte do zsh — o modificador `:A` do `$0` e o `print -u2` do zsh falham no bash 3.2; 87 refs a limpar.
2. Orquestrador inteiro em Python com adapters em módulos — contra o `sdd/bin/adapters/*.sh` do plano.

**Consequences:**
- o adapter `openrouter` usa `python3 -B -c` com `urllib` (sem `curl`, sem dependência nova);
- `adapter_credencial` dá o texto do `→` do exit 65 sem coluna nova no registry (revisão do DESIGN, M4);
- a extração de cada formato é testada sobre saídas reais neutralizadas em `sdd/fixtures/revisao/saidas/`.

### Decision 2: Registry de 9 colunas, papéis por slot ou flag, lista como cadeia do projeto, exclusão antes de chamar

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | BRAINSTORM decisões 1–3 e 5; DEFINE AT-001–AT-005 |

**Context:** sem cadeia de fábrica, alguém precisa dizer quem revisa e quem audita; a R7 ("quota avança") precisa de uma próxima.

**Choice:** colunas `engine · adapter · modelo · cobranca · papeis · timeout_s · sinal_auth · sinal_transitorio · sinal_persistente`; `modelo` `-` = padrão da CLI; `cobranca` em `assinatura | pay-per-token | desconhecida`; `papeis` em `revisor,auditor,desempate`. As 4 linhas de fábrica: `claude`, `codex`, `gemini` (modelo `-`) e `openrouter` (modelo `qwen/qwen3.7-plus`). Ordem de resolução: `--reviewer`/`--auditor` > `review.revisor1`/`review.auditor` > 64. Cada valor é uma lista por vírgula. `openrouter:<slug>` usa a linha `openrouter` com o modelo trocado. Exclusão: o 1º id do auditor igual ao 1º do revisor → 67 (sem `--um-engine`); durante a execução, um id do auditor igual ao revisor efetivo é pulado. `diversidade` = `nenhuma` (mesmo id), `modelo` (mesmo adapter, outro modelo), `vendor` (adapters diferentes).

**Rationale:** a lista é a cadeia que o projeto escolhe; a exclusão antes da 1ª chamada não gasta dinheiro num self-review.

**Alternatives Rejected:**
1. Slot `review.revisor2` — a 1ª linha elegível do registry basta (BRAINSTORM decisão 6).
2. Degradação automática para 1 engine — esconde o self-review; o flag deixa a escolha visível.

**Consequences:**
- o rótulo de um id com `:`/`/` no `@engine` troca cada caractere fora de `A-Za-z0-9._-` por `-` (`R1@openrouter-qwen-qwen3.7-plus`).

### Decision 3: Diff congelado por índice temporário com intent-to-add; artefatos SDD fora

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-006, AT-007, AT-025; landmine LM-003 |

**Context:** o diff tem de incluir arquivos novos não rastreados (LM-003: "revisa o vazio") sem tocar o índice do usuário, e o `diff_sha256` tem de sobreviver às linhas de ledger e de BUILD_REPORT gravadas depois da revisão.

**Choice:** `base` = `--base`, senão `origin/<project.default_branch>`, senão `<project.default_branch>`; `merge_base` = `git merge-base <base> HEAD`. Copia o índice achado por `git rev-parse --git-path index` (funciona em worktree, onde `.git` é arquivo; índice ausente = vazio) para um temporário (`GIT_INDEX_FILE`), roda `git add --intent-to-add` nos não rastreados de `git ls-files --others --exclude-standard`, e `git -c diff.noprefix=false diff --binary --no-color --no-ext-diff --no-renames --diff-algorithm=myers <merge_base> -- <pathspec>` (a config do usuário não muda os bytes). Pathspec: `--paths` quando dado; senão `.` com `:(exclude)` para `review.output_dir` e `sdd/features`, `sdd/reports`, `sdd/reviews`, `sdd/releases`, `sdd/handoffs`, `sdd/traces`; o `output_dir` sai sempre. O META grava `base`, `merge_base`, `head`, `paths` e `diff_sha256`. Vazio → 64; acima de `DIFF_MAX_MB = 8` → 64.

**Rationale:** o índice do usuário fica intacto; o `--conferir` recalcula com o mesmo `base`/`paths` e compara bytes.

**Alternatives Rejected:**
1. `git diff --no-index /dev/null <arquivo>` por não rastreado — ordem e cabeçalhos diferentes do diff normal; mais código.
2. Incluir os artefatos SDD — o sha256 mudaria a cada linha de ledger (DEFINE, Clarifications).

**Consequences:**
- a revisão do DESIGN usa `--paths "sdd/features/DEFINE_<F>.md sdd/features/DESIGN_<F>.md"`.

### Decision 4: Contexto, privacidade e invocação sem ferramenta

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-008–AT-010; UX U4, U5 |

**Context:** R4 (contexto com teto) e R9 (dado não vai para o git nem é retido pelo provedor).

**Choice:** contexto de `--feature`: BRAINSTORM, DEFINE, DESIGN, BUILD_REPORT, nessa ordem, cada um sob um título `## <arquivo>`; acima de `review.context_max_kb` (default 180), sai o BRAINSTORM; se ainda passa, corta o fim com a linha `[… cortado: teto de <n> KB …]`. Pasta: `git check-ignore -q <output_dir>/.sonda` ≠ 0 → 64 com a frase da U5 e o comando para `$(git rev-parse --git-common-dir)/info/exclude` (o `.git/info/exclude` literal falha em worktree). Invocação: `claude -p --output-format json --tools "" --safe-mode --no-session-persistence [--model M]`; `codex exec -s read-only --skip-git-repo-check --ephemeral --json [-m M] -`; `gemini -o json --approval-mode default [-m M]`; todos com o prompt por stdin e `cwd` numa pasta temporária vazia. `openrouter`: `POST <SDD_REVIEW_OPENROUTER_URL ou https://openrouter.ai/api/v1/chat/completions>` com `model`, `messages` (1 mensagem `user`), `provider` (`data_collection: deny`, `require_parameters: true`) e `usage` (`include: true`); a chave só de `OPENROUTER_API_KEY`.

**Rationale:** sem ferramenta de escrita e em pasta vazia, a engine recebe tudo inline e não precisa ler nada; `--safe-mode` desliga CLAUDE.md, skills e hooks do usuário. Ferramentas de leitura podem continuar (o `codex -s read-only` lê o sistema de arquivos; o `gemini` pede aprovação e, sem terminal, não a recebe): o prompt e o doc dizem "sem ferramenta de escrita", não "sem ferramenta".

**Alternatives Rejected:**
1. `--bare` no `claude` — exige chave de API e não serve a quem usa a assinatura.
2. `curl` no adapter `openrouter` — a chave apareceria no `ps`; o `urllib` lê do ambiente.

**Consequences:**
- a URL do OpenRouter é trocável por ambiente só para o teste do corpo da requisição (servidor local).

### Decision 5: Falha classificada só quando a chamada falhou; espera e lista

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-017–AT-019; registry do privado (sinais por ERE) |

**Context:** os sinais casam texto; uma revisão que cita "401" ou "quota" no conteúdo não pode virar falha.

**Choice:** uma chamada falhou quando o adapter sai ≠ 0, estoura `timeout_s` ou a extração não traz `texto`. Só então o núcleo casa, sobre a saída bruta + stderr, nesta ordem: `sinal_auth` (ou exit 65 do adapter, chave ausente) → 65, para tudo; exit 66 do adapter (CLI fora do `PATH`) → avança; `sinal_transitorio` → mais 2 tentativas com `SDD_REVIEW_ESPERA` s (default 30) e, esgotadas, conta como persistente; `sinal_persistente` ou timeout → avança. Lista esgotada → 67 (66 se todas as causas foram CLI ausente). Ordem dos papéis: revisor → 2º revisor → auditor → desempate. O revisor ≠ 0 para a cadeia. O 2º revisor que falha (65 e 66 incluídos) ou não tem engine (`revisor2_engine: indisponível`, `revisor2_exit: 67`) **não** para: registra, imprime ⚠️ e o auditor roda sobre o 1º revisor — como o privado (adversarial-review.sh:675–686); a dispensa é decisão do `loop` (Decision 9). Exit final: o do revisor ou, se ele foi 0, o do auditor; o 2º revisor e o desempate nunca mudam o exit (o desempate que falha deixa `desempate_decisao: -`, e o `loop` cai no D5).

**Rationale:** credencial errada nunca é "tente a próxima" (o privado chama isso de NUNCA fallback); 429 é passageiro.

**Alternatives Rejected:**
1. Casar os sinais sempre — falso AUTH com revisão que cita 401.
2. Fallback em AUTH — esconde credencial quebrada.

**Consequences:**
- os 3 sinais de fábrica cobrem o que foi medido (401 do OpenRouter, `ProjectIdRequiredError` do Gemini) e as frases públicas de limite de cada CLI;
- um `gemini` sem credencial escolhido como 2º revisor não derruba a revisão (revisão do DESIGN, H1).

### Decision 6: 2º revisor por gatilho em constantes nomeadas; desempate de um alvo

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-014–AT-016; BRAINSTORM decisões 2 e 6 |

**Context:** R6, com os limites fora do config (pergunta 2 do brainstorm).

**Choice:** constantes no topo do núcleo: `SEGUNDO_REVISOR_MIN_ARQUIVOS = 8`, `SEGUNDO_REVISOR_MIN_KB = 120`, `SEGUNDO_REVISOR_MIN_CAMADAS = 2`, `RASO_SEGUNDOS = 30`, `DIFF_MAX_MB = 8`. Segurança: caminho do diff que casa `review.security_globs`, `layers.sql` (`fnmatch`) ou que tem um segmento (quebrado em `/`, `.`, `_`, `-`) igual a `auth`, `login`, `token(s)`, `senha(s)`, `password` ou `jwt` — por segmento, para `author.md` não contar. Camadas: globs de `layers:` com valor não vazio. Raso: revisor com `< 30 s` **e** 0 achados. O 2º revisor: `--revisor2` ou a 1ª linha do registry com `revisor` em `papeis`, disponível, e fora do conjunto (revisor efetivo, 1º id do auditor); nenhuma → `revisor2_engine: indisponível`. Desempate: no 1º HIGH (ordem do jsonl) com `DISAGREE_EVIDENCE` — casando o id do auditor pelo id completo ou pela base única, e gravando em `desempate_alvo` o id **como está no jsonl do revisor** —, engine com `desempate` em `papeis`, disponível, fora do conjunto (origem, auditor efetivo); saída exige uma linha `DECISAO:PROCEDE` ou `DECISAO:REFUTADO`.

**Rationale:** formato do privado (`desempate_alvo`, `DECISAO:…` exato), que o `loop` da fonte já sabe ler.

**Alternatives Rejected:**
1. Desempate de todos os HIGH refutados — mais chamadas; o privado mediu 15 desempates em 315 revisões.

**Consequences:**
- com 2 revisores, os ids são reescritos com `@<engine>` nos jsonl e no texto que vai ao auditor.

### Decision 7: META compatível com o privado, custo em 4 formas, resumo para pessoas

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-020–AT-024, AT-041; UX U1, U2, U4, U6 |

**Context:** o `loop` e quem lê os 315 META do privado esperam as mesmas chaves.

**Choice:** `chave : valor` alinhado, uma por linha, com `protocolo`, `base`, `merge_base`, `head`, `paths`, `diff_sha256`, `diff`, `contexto`, `docs_sdd`, `contexto_cortado`, `diversidade` e, por papel (`reviewer`, `revisor2`, `auditor`, `desempate`), `_engine_default`, `_engine_efetivo`, `_fallback_usado`, `_motivo`, `_exit`, `_segundos`, `_achados`/`_vereditos`, `_tokens_entrada`, `_tokens_saida`, `_tokens_total`, `_modelo`, `_custo`; mais `revisor1_raso`, `gatilho_2o_revisor`, `convergencia_1o_passe` com os motivos fixos `n/a (auditor não rodou)`, `n/a (auditor falhou)`, `n/a (revisor1 raso: 0 achados em <n>s)` e `n/a (2º revisor raso: 0 achados em <n>s)`, `desempate_alvo`, `desempate_decisao`, `convergencia_1o_passe`, `custo_total`, `quando`. Custo: `custo_usd` do adapter → `US$ 0.0061`; senão tarifa do `precos.tsv` × tokens → `≈US$ 0.0100`; senão `cobranca = assinatura` → `assinatura`; senão `$?`. O resumo traduz: `US$ 0,0061`, `≈ US$ 0,01 (estimado)`, `incluído na assinatura`, `custo desconhecido`. Saída: ⚠️ primeiro, `▶ <papel>: <engine> (<modelo>) — até <n> min` ao começar cada papel, e no fim `RESULTADO:` + o resumo + `→`.

**Rationale:** máquina lê o META; pessoa lê o resumo.

**Alternatives Rejected:**
1. META em JSON — quebraria o `loop` da F9 e a leitura dos 315 do privado.

**Consequences:**
- `custo_total` soma `US$` e `≈US$` e diz quantos papéis ficaram `$?`.

### Decision 8: `--conferir` e `--ledger`: a release prova que a revisão é desta versão

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-025–AT-027; BRAINSTORM decisão 4; UX U3, U8 |

**Context:** "sem `review_externo` no ledger aborta" precisa ser um exit, não leitura de prosa.

**Choice:** `--conferir [<pasta>]` (default: a pasta `EXTERNAL_REVIEW_*` mais nova do `output_dir`) recalcula o diff com o `base` e os `paths` do META e exige o mesmo `diff_sha256`, `reviewer_exit 0`, `auditor_exit 0` e, se `revisor2_engine ≠ -`, `revisor2_exit 0`; imprime a linha `✅` e `review_externo: <pasta> sha256=<hex> diversidade=<v>` (0) ou o motivo (2). `--ledger <arquivo>` aceita `review_externo: dispensado — <motivo>` (motivo com 3+ caracteres) ou `review_externo: <pasta> sha256=<hex>…` com o `META.txt` da pasta e o mesmo hex (0); ausente ou malformado → 2; ilegível → 64. Na `sdd-release`: 0a item 8 roda `--conferir`; exit 2 → a pergunta D3 (UX U3), antes do bloco do OK; a fase 1, passo 3, grava a linha; logo depois do commit atômico (passo 4) e **antes** do passo 5 (que roda num worktree temporário sem a pasta da revisão, ignorada pelo git), `--ledger` roda **na pasta da frente** e aborta em ≠ 0. `--ledger` resolve `<pasta>` contra a raiz do repositório atual; pasta ausente → 2 com "rode na pasta da frente". `--conferir` aceita `revisor2_exit ≠ 0` só com `--aceitar-sem-revisor2 "<motivo>"` (o motivo vai para a linha do ledger). As duas saídas terminam em `RESULTADO:` + `→`.

**Rationale:** dois exits separam "a revisão é deste código" de "o ledger registrou".

**Alternatives Rejected:**
1. Conferir pelo `head` do META — qualquer commit de documentação invalidaria a revisão.

**Consequences:**
- a pergunta D3 é a 16ª pergunta de decisão das skills (`sdd-decisoes-lint --sites`).

### Decision 9: `loop` por delta — revisor2, rasa, desempate

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-028–AT-031; fonte `scripts/sdd-fluxo.sh` do privado, linhas 95–215 |

**Context:** o `loop` da F9 ignora as chaves novas; ele não pode mudar para META sem elas.

**Choice:** três blocos novos no núcleo do `loop`, todos guardados por `revisor2_engine`, `revisor1_raso`, `convergencia_1o_passe` ou `desempate_alvo` presentes no META: (1b) 2º revisor sem resultado: `revisor2_exit` ausente → 64; 65/66 ou `indisponível` sem a linha própria `revisor2: dispensado rodada=N — <motivo>` no ledger → BLOQUEADO (20, motivo D3); outro ≠ 0 → CONTINUAR (10); com a dispensa → `motivo:` e segue. (1c) rasa → 10. (2) com o 2º revisor ok, lê `reviewer2.verdicts.jsonl`; id repetido nos 2 arquivos → 64. (3) `DISAGREE_EVIDENCE` em HIGH sem veredito no ledger: alvo com `DECISAO:REFUTADO` exato → fecha; `DECISAO:PROCEDE` → continua grave, sem impasse; senão D5 como hoje. Precedência: 64 > 20 > 10 > 30 > 0, inalterada.

**Rationale:** é o delta da fonte, sem o 75 (corte YAGNI).

**Alternatives Rejected:**
1. Reescrever o `loop` — quebraria os 48 testes da F9.

**Consequences:**
- as fixtures da F9 continuam dando o mesmo exit e a mesma saída (AT-031).

### Decision 10: Skills, config, init, CI e docs por delta

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-027, AT-032–AT-037, AT-041; regra 7 do 8.0 |

**Context:** R1, R12 e R13 ligam o script ao fluxo sem reescrever as skills.

**Choice:**
- `sdd-design` 2.3.0 — "Review adversarial do DESIGN": rodar o script com `--paths` sobre DEFINE + DESIGN e `--feature`, revisor e depois auditor, nunca em paralelo; `--um-engine` com uma engine só; `despachar` continua para o caso sem engine.
- `sdd-build` 2.5.0 — `### 0. Revisão do DESIGN` antes do passo 1 (`review-design` 0/1/64) e 5c com o script + `loop`, dizendo que a release exige a revisão.
- `sdd-release` 2.6.0 — 0a item 8, passo 3 (linha do ledger), passo 6 (`--ledger`), a pergunta D3 em `references/como-falar.md` e o campo no `references/ledger.md`.
- `config.example.yaml` — 5 slots + `security_globs`; sai `vendors`.
- `bin/sdd-open.sh` — `sdd_faltantes` passa a listar `review` (copia `sdd/review/`; `sdd/bin/adapters/` já vem com `bin`); o `doctor` compara também `sdd/bin/adapters/*`.
- `release.yml` — `sdd/review/**` nos `paths`.
- `docs/adversarial-review.md` + PT, links nos READMEs e `cli-conventions.md` com os exits; `docs/adaptation-guide.md` + PT dizem que os nomes de modelo moram no registry e no `precos.tsv`; `docs/chained-flow.md` + PT apontam o `loop` para o script; o roadmap mantém "Adversarial review" *planned* até a F11.

**Rationale:** cada skill ganha a chamada e o motivo, nada mais.

**Alternatives Rejected:**
1. Nome de engine no texto das skills — reprova a regra 10.

**Consequences:**
- pinos de versão em `test_contrato_build_release.py` e `test_correcoes_w0.py`; `check-versions --base v2.2.10`: 3 minor.

### Decision 11: Provas — stubs locais, saídas reais neutralizadas, sabotagem, baseline e a execução real

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-10-31 |
| **Source** | DEFINE AT-038–AT-040; plano 8.0 regra 6 |

**Context:** os testes rodam sem rede no piso e no CI; a prova real é paga.

**Choice:** adapter de teste `sdd/fixtures/revisao/adapters/stub.sh` lido por `SDD_REVIEW_ADAPTERS`, com o `modelo` do registry de teste nomeando a resposta em `sdd/fixtures/revisao/respostas/`; respostas de falha com sequência (`429` e depois ok) contadas num arquivo de estado em `SDD_REVIEW_STUB_ESTADO`; `SDD_REVIEW_ESPERA=0`. A extração dos 4 adapters reais é testada sobre `sdd/fixtures/revisao/saidas/` (formatos medidos acima, com ids e textos trocados). O corpo da requisição do `openrouter` é capturado por um `http.server` local no teste. Evidência fora do commit em `sdd/reports/evidence/F10_REVISAO/`: `gerar-evidencia.sh`, `sabotagem.sh` (7 sabotagens), `baseline.log` (testes novos na árvore `v2.2.10`) e `real.sh` (AT-040, revisor `claude`, auditor `openrouter:qwen/qwen3.7-plus`).

A base do `test_revisao` tira `OPENROUTER_API_KEY` do ambiente, põe no `PATH` só uma pasta sem `claude`/`codex`/`gemini` (mais `git`, `python3`, `bash`) e fixa `SDD_REVIEW_OPENROUTER_URL=http://127.0.0.1:9/`: um defeito na exclusão nunca gasta dinheiro. Os 3 adapters de CLI são exercitados com binários falsos que gravam argv, cwd e stdin (só o contrato de invocação; o stub por formato é a F11). Um teste roda o `sdd-fluxo.sh loop` sobre as pastas que o stub gera (2º revisor ok, indisponível, falhou, raso, desempate REFUTADO e PROCEDE). Fixtures com `diff_sha256` usam hex só de letras (`a…f`) ou valor gerado em execução (o publish-gate reprova 11+ dígitos). Casos de worktree (AT-006, AT-009, AT-026) rodam dentro de `git worktree add`.

**Rationale:** chave de API nunca em arquivo (G1): o teste usa um valor gerado em execução.

**Alternatives Rejected:**
1. Stub por formato de engine com binário falso no `PATH` — é a F11.

**Consequences:**
- a suíte cresce ~70 testes; todos locais e com espera 0.

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/review/registry.tsv` | Create | 4 engines, 9 colunas, cabeçalho comentado (Decision 2) | (general) | None |
| 2 | `sdd/review/precos.tsv` | Create | `qwen/qwen3.7-plus` e `deepseek/deepseek-v4-flash` com fonte e data (Decision 7) | (general) | None |
| 3 | `sdd/review/prompts/reviewer.md` | Create | LP-001 | (general) | None |
| 4 | `sdd/review/prompts/auditor.md` | Create | LP-002 | (general) | 3 |
| 5 | `sdd/review/prompts/desempate.md` | Create | LP-003 | (general) | 4 |
| 6 | `sdd/bin/adapters/claude.sh` | Create | CLI `claude -p`, extração de `result`/`usage`/`total_cost_usd` (Decisions 1, 4) | (general) | None |
| 7 | `sdd/bin/adapters/codex.sh` | Create | `codex exec -s read-only --json`, extração do JSONL | (general) | None |
| 8 | `sdd/bin/adapters/gemini.sh` | Create | `gemini -o json`, extração de `response`/`stats` | (general) | None |
| 9 | `sdd/bin/adapters/openrouter.sh` | Create | `urllib`, `data_collection: deny`, `usage.cost` | (general) | None |
| 10 | `sdd/bin/adversarial-review.sh` | Create | frente + núcleo (Decisions 1–8) | (general) | 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| 11 | `sdd/bin/sdd-fluxo.sh` | Modify | delta do `loop` (Decision 9); USO com as chaves novas | (general) | None |
| 12 | `sdd/fixtures/revisao/adapters/stub.sh` | Create | adapter de teste (Decision 11) | (general) | None |
| 13 | `sdd/fixtures/revisao/registry-stub.tsv` | Create | engines `stub-a`, `stub-b`, `stub-c`, `stub-d` com papéis e sinais | (general) | 12 |
| 14 | `sdd/fixtures/revisao/respostas/revisor-ok.md` | Create | 1 HIGH (`R1`) + 1 MED (`R2`) no bloco | (general) | None |
| 15 | `sdd/fixtures/revisao/respostas/revisor-vazio.md` | Create | bloco vazio (0 achados) | (general) | None |
| 16 | `sdd/fixtures/revisao/respostas/revisor-sem-bloco.md` | Create | prosa sem bloco → 68 | (general) | None |
| 17 | `sdd/fixtures/revisao/respostas/auditor-agree.md` | Create | AGREE em `R1` e `R2` | (general) | None |
| 18 | `sdd/fixtures/revisao/respostas/auditor-refuta-high.md` | Create | `DISAGREE_EVIDENCE` em `R1` | (general) | None |
| 19 | `sdd/fixtures/revisao/respostas/auditor-sem-bloco.md` | Create | prosa sem bloco → 68 | (general) | None |
| 20 | `sdd/fixtures/revisao/respostas/desempate-refutado.md` | Create | `DECISAO:REFUTADO` | (general) | None |
| 21 | `sdd/fixtures/revisao/respostas/falha-auth.txt` | Create | texto do 401 (valor falso, sem chave) | (general) | None |
| 22 | `sdd/fixtures/revisao/respostas/falha-429.txt` | Create | texto do 429 | (general) | None |
| 23 | `sdd/fixtures/revisao/respostas/falha-quota.txt` | Create | texto de crédito esgotado | (general) | None |
| 24 | `sdd/fixtures/revisao/saidas/claude.json` | Create | formato medido do `claude -p` | (general) | None |
| 25 | `sdd/fixtures/revisao/saidas/codex.jsonl` | Create | formato medido do `codex exec --json` | (general) | None |
| 26 | `sdd/fixtures/revisao/saidas/gemini.json` | Create | formato documentado do `gemini -o json` | (general) | None |
| 27 | `sdd/fixtures/revisao/saidas/openrouter.json` | Create | formato medido do OpenRouter | (general) | None |
| 28 | `sdd/fixtures/fluxo/review-r2-indisponivel/META.txt` | Create | `revisor2_engine: indisponível`, `revisor2_exit: 67`, auditor 0 (o estado que o script produz) | (general) | None |
| 29 | `sdd/fixtures/fluxo/review-r2-indisponivel/reviewer.verdicts.jsonl` | Create | 1 MED | (general) | None |
| 30 | `sdd/fixtures/fluxo/review-r2-indisponivel/auditor.verdicts.jsonl` | Create | AGREE | (general) | None |
| 31 | `sdd/fixtures/fluxo/review-r2-falhou/META.txt` | Create | `revisor2_exit: 68`, auditor 0 | (general) | None |
| 32 | `sdd/fixtures/fluxo/review-r2-falhou/reviewer.verdicts.jsonl` | Create | 1 MED | (general) | None |
| 33 | `sdd/fixtures/fluxo/review-r2-falhou/auditor.verdicts.jsonl` | Create | AGREE | (general) | None |
| 34 | `sdd/fixtures/fluxo/review-rasa/META.txt` | Create | `revisor1_raso: sim`, `revisor2_engine: -` | (general) | None |
| 35 | `sdd/fixtures/fluxo/review-rasa/reviewer.verdicts.jsonl` | Create | vazio | (general) | None |
| 36 | `sdd/fixtures/fluxo/review-rasa/auditor.verdicts.jsonl` | Create | vazio | (general) | None |
| 37 | `sdd/fixtures/fluxo/review-desempate-refutado/META.txt` | Create | `desempate_alvo: R1`, `DECISAO:REFUTADO` | (general) | None |
| 38 | `sdd/fixtures/fluxo/review-desempate-refutado/reviewer.verdicts.jsonl` | Create | 1 HIGH | (general) | None |
| 39 | `sdd/fixtures/fluxo/review-desempate-refutado/auditor.verdicts.jsonl` | Create | `DISAGREE_EVIDENCE` | (general) | None |
| 40 | `sdd/fixtures/fluxo/review-desempate-procede/META.txt` | Create | `DECISAO:PROCEDE` | (general) | None |
| 41 | `sdd/fixtures/fluxo/review-desempate-procede/reviewer.verdicts.jsonl` | Create | 1 HIGH | (general) | None |
| 42 | `sdd/fixtures/fluxo/review-desempate-procede/auditor.verdicts.jsonl` | Create | `DISAGREE_EVIDENCE` | (general) | None |
| 43 | `sdd/fixtures/fluxo/review-2-revisores/META.txt` | Create | 2º revisor ok | (general) | None |
| 44 | `sdd/fixtures/fluxo/review-2-revisores/reviewer.verdicts.jsonl` | Create | `R1@stub-a` MED | (general) | None |
| 45 | `sdd/fixtures/fluxo/review-2-revisores/reviewer2.verdicts.jsonl` | Create | `R1@stub-c` HIGH | (general) | None |
| 46 | `sdd/fixtures/fluxo/review-2-revisores/auditor.verdicts.jsonl` | Create | AGREE nos 2 | (general) | None |
| 47 | `sdd/fixtures/fluxo/ledger-r2-dispensado.md` | Create | linha própria `revisor2: dispensado rodada=1 — …` | (general) | None |
| 48 | `sdd/fixtures/revisao/ledger-sem-review.yaml` | Create | ledger de release sem `review_externo` → 2 | (general) | None |
| 49 | `sdd/fixtures/revisao/ledger-dispensado.yaml` | Create | `review_externo: dispensado — <motivo>` → 0 | (general) | None |
| 50 | `tests/test_revisao.py` | Create | AT-001–AT-009, AT-011–AT-026, AT-041 com o stub | (general) | 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 48, 49 |
| 51 | `tests/test_revisao_adapters.py` | Create | AT-010, AT-020 sobre as saídas reais, o corpo HTTP e os binários falsos | (general) | 6, 7, 8, 9, 24, 25, 26, 27, 84, 85, 86 |
| 52 | `tests/test_fluxo.py` | Modify | AT-028–AT-031 | (general) | 11, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47 |
| 53 | `tests/test_decisoes_lint.py` | Modify | 16 perguntas em 16 arquivos | (general) | 61 |
| 54 | `tests/test_bash32.py` | Modify | varre `sdd/bin/adapters/*.sh`; `adversarial-review.sh` em `NOVOS` | (general) | 10 |
| 55 | `tests/test_release_workflow.py` | Modify | `sdd/review/**` nos `paths` | (general) | 69 |
| 56 | `tests/test_sdd_open.py` | Modify | `init` copia `sdd/review/` e os adapters, sem sobrescrever (AT-035) | (general) | 68 |
| 57 | `tests/test_contrato_build_release.py` | Modify | pinos release 2.6.0 e build 2.5.0; textos de AT-027, AT-032, AT-033 (sem nome de engine nas seções novas), AT-036, AT-037 | (general) | 59, 62, 63 |
| 58 | `tests/test_correcoes_w0.py` | Modify | pino build 2.5.0 | (general) | 62 |
| 59 | `.agents/skills/sdd-release/SKILL.md` | Modify | 0a item 8, passos 3 e 6, versão 2.6.0 (Decision 8) | (general) | 10 |
| 60 | `.agents/skills/sdd-release/references/ledger.md` | Modify | campo `review_externo` no esquema | (general) | None |
| 61 | `.agents/skills/sdd-release/references/como-falar.md` | Modify | pergunta D3 (UX U3) | (general) | None |
| 62 | `.agents/skills/sdd-build/SKILL.md` | Modify | passo 0 e 5c, versão 2.5.0 | (general) | 10 |
| 63 | `.agents/skills/sdd-design/SKILL.md` | Modify | review adversarial do DESIGN, versão 2.3.0 | (general) | 10 |
| 64 | `sdd/templates/fragments/RESUMO_ETAPA.md` | Modify | script e `review.output_dir` | (general) | None |
| 65 | `sdd/templates/fragments/ADVISOR_CONSULT.md` | Modify | script como a ferramenta | (general) | None |
| 66 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | `ferramenta: sdd/bin/adversarial-review.sh` | (general) | None |
| 67 | `sdd/config.example.yaml` | Modify | 5 slots, sem `vendors` (AT-034) | (general) | None |
| 68 | `bin/sdd-open.sh` | Modify | `sdd_faltantes` com `review`; `doctor` com `sdd/bin/adapters/*` | (general) | None |
| 69 | `.github/workflows/release.yml` | Modify | `sdd/review/**` | (general) | None |
| 70 | `docs/adversarial-review.md` | Create | AT-041, UX U7 | (general) | 10 |
| 71 | `docs/pt-BR/adversarial-review.md` | Create | idem, PT | (general) | 70 |
| 72 | `README.md` | Modify | link | (general) | 70 |
| 73 | `README.pt-BR.md` | Modify | link | (general) | 71 |
| 74 | `docs/cli-conventions.md` | Modify | exits 2/64–68 do script | (general) | 10 |
| 75 | `MANIFEST.txt` | Modify | todo arquivo novo, `LC_ALL=C` | (general) | 1, 10, 12, 50, 70 |
| 76 | `sdd/reports/evidence/F10_REVISAO/gerar-evidencia.sh` | Create | logs de cada AT (fora do commit) | (general) | 10, 11 |
| 77 | `sdd/reports/evidence/F10_REVISAO/sabotagem.sh` | Create | 7 sabotagens (AT-039) | (general) | 50, 52 |
| 78 | `sdd/reports/evidence/F10_REVISAO/real.sh` | Create | AT-040 | (general) | 10 |
| 79 | `tests/test_docs.py` | Modify | AT-041: o doc existe, tem os links e as seções | (general) | 70, 71 |
| 80 | `docs/adaptation-guide.md` | Modify | nomes de modelo no registry e no `precos.tsv` | (general) | 1, 2 |
| 81 | `docs/pt-BR/adaptation-guide.md` | Modify | idem, PT | (general) | 80 |
| 82 | `docs/chained-flow.md` | Modify | o `loop` lê a saída do script | (general) | 10 |
| 83 | `docs/pt-BR/chained-flow.md` | Modify | idem, PT | (general) | 82 |
| 84 | `sdd/fixtures/revisao/bin/claude` | Create | binário falso que grava argv, cwd e stdin (AT-010) | (general) | None |
| 85 | `sdd/fixtures/revisao/bin/codex` | Create | idem | (general) | None |
| 86 | `sdd/fixtures/revisao/bin/gemini` | Create | idem | (general) | None |

**Total Files:** 86

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–86 | Um autor mantém os nomes das chaves do META, dos exits e das frases iguais no script, nas skills, nos docs e nos testes |

**Agent Discovery:** Not available (um agente faz o build, modo default).

---

## Landmines aplicáveis

O playbook do pacote tem 4 landmines; 3 se aplicam:

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | testes do script | ✔ tratado: cada teste confere a linha do META e da saída, não só o exit |
| LM-002 | testes novos | ✔ tratado: baseline vermelha na `v2.2.10` e 7 sabotagens (AT-039) |
| LM-003 | diff congelado | ✔ tratado: intent-to-add em índice temporário inclui os não rastreados (Decision 3); commit antes de cada revisão de contexto fresco |
| LM-004 | — | N.A.: sem migration |

---

## Contrato de aceite

Ajustes no DEFINE feitos durante o Design (DEFINE v1.2):

| # | Alvo | Classe | Decisão |
|---|---|---|---|
| 1 | AT-017–AT-019 | aceite falso (um texto de revisão que cita "401" viraria AUTH) | os sinais só valem quando a chamada falhou (Decision 5) |
| 2 | AT-022, AT-023 | estado sem critério (2º revisor e desempate que falham) | 2º revisor que falha → exit dele e `REVIEW INVÁLIDA`; desempate que falha não muda o exit |
| 3 | AT-025 | gate não cobre AT (`--conferir` aceitava 2º revisor falho) | exige `revisor2_exit 0` quando houve 2º revisor |
| 4 | AT-010 | não-verificável ("the equivalent flag") | flags concretas por CLI e a URL trocável por ambiente para o teste do corpo |
| 5 | DEFINE v1.3 | revisão de contexto fresco (Advisor Ledger) | 2º revisor não para a cadeia; `--ledger` antes do passo 5; worktree; `adapter_credencial`; binários falsos e asserts de texto; 13 LOW |

---

## Code Patterns

### Pattern 1: Interface de um adapter (bash 3.2)

```bash
# sdd/bin/adapters/<adapter>.sh — sourced pelo núcleo; nunca executado sozinho.
# adapter_disponivel           → 0 se a engine pode ser chamada (CLI no PATH ou chave no ambiente)
# adapter_invocar M PROMPT OUT → grava a saída bruta em OUT; 0 ok · 65 sem credencial · 66 CLI ausente
# adapter_extrair OUT          → 1 linha JSON: texto, tokens_entrada, tokens_saida, modelo, custo_usd
# adapter_credencial           → 1 linha: onde a credencial vive (vai no → do exit 65)
adapter_disponivel() {
  command -v claude >/dev/null 2>&1
}
adapter_credencial() {
  echo "login da CLI: rode claude e faça login"
}
adapter_invocar() {
  modelo="$1"; prompt="$2"; out="$3"; err="$4"
  command -v claude >/dev/null 2>&1 || return 66
  set -- -p --output-format json --tools "" --safe-mode --no-session-persistence
  [ "$modelo" = "-" ] || set -- "$@" --model "$modelo"
  claude "$@" < "$prompt" > "$out" 2> "$err"
}
```

### Pattern 2: Chamada do adapter pelo núcleo (Python, teto de tempo no `subprocess`)

```python
def invocar(adapter, modelo, prompt, saida, teto):
    arq = os.path.join(ADAPTERS, adapter + ".sh")
    cmd = [BASH, "-c", 'source "$1"; shift; adapter_invocar "$@"', "_", arq, modelo, prompt,
           saida, saida + ".err"]
    p = subprocess.Popen(cmd, cwd=VAZIA, stdin=subprocess.DEVNULL, start_new_session=True)
    try:
        return p.wait(timeout=teto), False
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        return 124, True
```

### Pattern 3: Classificação só da chamada que falhou

```python
def classe(rc, timeout, texto, bruto, linha):
    # bruto = saída + stderr da chamada; só é lido quando a chamada falhou
    if rc == 0 and not timeout and texto:
        return "ok"
    if rc == 65 or re.search(linha["sinal_auth"], bruto):
        return "auth"
    if rc == 66:
        return "launcher"
    if re.search(linha["sinal_transitorio"], bruto):
        return "transitorio"
    return "persistente"
```

### Pattern 4: Linha do META e custo em 4 formas

```python
def custo(meta_papel, linha, precos, tok_in, tok_out, custo_usd):
    if custo_usd is not None:
        return "US$ %.4f" % custo_usd
    tarifa = precos.get((linha["engine"], meta_papel["modelo"]))
    if tarifa:
        return "≈US$ %.4f" % ((tok_in * tarifa[0] + tok_out * tarifa[1]) / 1e6)
    return "assinatura" if linha["cobranca"] == "assinatura" else "$?"
```

---

## LLM Prompts

### Inventory

| # | Path / Runtime | Type | Consumer | Output Shape |
|---|---|---|---|---|
| LP-001 | `sdd/review/prompts/reviewer.md` | one-shot | `adversarial-review.sh` (revisor e 2º revisor) | Markdown em 4 partes + bloco `<<<VERDICTS` com 1 JSON por linha (`achado`, `arquivo`, `linha`, `severidade`, `confianca`, `resumo`) |
| LP-002 | `sdd/review/prompts/auditor.md` | one-shot | `adversarial-review.sh` (auditor) | Markdown + bloco `<<<VERDICTS` (`achado`, `veredito`, `justificativa`; `NOVO` com `severidade`, `arquivo`, `linha`, `resumo`) |
| LP-003 | `sdd/review/prompts/desempate.md` | one-shot | `adversarial-review.sh` (desempate) | Markdown + última linha `DECISAO:PROCEDE` ou `DECISAO:REFUTADO` |

Nenhum é `loop`: cada papel é uma chamada; a resposta de um vira **material** do seguinte, sem que o mesmo papel seja chamado de novo sobre a própria saída (a nova tentativa do 429 repete a mesma entrada).

### Contrato por prompt

| Campo | LP-001 revisor | LP-002 auditor | LP-003 desempate |
|---|---|---|---|
| Purpose | revisar o diff congelado contra o contexto SDD | auditar a revisão (não revisar o código de novo) | decidir um HIGH refutado com evidência |
| Type | one-shot | one-shot | one-shot |
| Consumer | parser do bloco no núcleo; o `loop` | idem | `desempate_decisao` no META; o `loop` |
| Tone/Audience | revisor sênior para o autor sênior, português do Brasil | auditor cético | juiz de uma questão |
| Input shape | prompt + `## CONTEXTO SDD` + `## DIFF` | prompt + contexto + diff + `## REVISÕES` | prompt + contexto + diff + o achado + a auditoria dele |
| Output shape | Inventory LP-001 | Inventory LP-002 | Inventory LP-003 |
| Approved fallback | bloco vazio quando não há achado; nunca omitir o bloco | idem | sem decisão possível → `DECISAO:PROCEDE` (o grave continua aberto: o lado seguro) |
| Reference material | escalas HIGH/MED/LOW e CONFIRMED/PLAUSIBLE; contrato do `ADVISOR_CONSULT.md` | definições dos 4 vereditos | definições de PROCEDE e REFUTADO |
| Settled decisions | sem vendor no texto (o mesmo prompt vai às 4 engines); sem ferramenta; material inline | idem | idem |
| Failure behavior | sem bloco → papel 68 | sem bloco → 68 | sem linha `DECISAO:` → `desempate_decisao: -` (D5 no `loop`) |

Os textos finais saem no Build pela skill `sdd-prompt-builder` (slot `prompts.builder_skill`), a partir destes contratos.

---

## Data Flow

```text
1. args + slots → papéis (64 sem id / id fora do registry; 67 auditor == revisor sem --um-engine)
   │
   ▼
2. base + merge-base + índice temporário (intent-to-add) → diff.patch, sha256 (64 vazio / > 8 MB)
   │
   ▼
3. --feature → context-sdd.md (teto context_max_kb; BRAINSTORM sai primeiro)
   │
   ▼
4. git check-ignore <output_dir> (64 com a linha do exclude) → mkdir EXTERNAL_REVIEW_<ts>
   │                                                    (--dry-run imprime o plano e sai 0 aqui)
   ▼
5. revisor: ▶ linha → adapter_invocar → classe (ok / 65 para / 429 repete / avança) → extrair → parse
   │   reviewer.md + reviewer.verdicts.jsonl (68 sem bloco: para)
   ▼
6. gatilhos → 2º revisor (ou indisponível) → reviewer2.* com @engine
   │
   ▼
7. auditor (exclusão aplicada) → auditor.md + auditor.verdicts.jsonl (68 sem bloco)
   │
   ▼
8. HIGH com DISAGREE_EVIDENCE → desempate → DECISAO
   │
   ▼
9. custo por papel, convergência, META.txt → resumo (⚠️, RESULTADO, →) → exit
   │
   ▼
10. skill: sdd-fluxo.sh loop --review <pasta> → ledger · release: --conferir → ledger → --ledger
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| CLI `claude` | processo, stdin → JSON | login da CLI (assinatura) ou chave da própria CLI | out/in | AUTH → 65; 429 → 2 novas tentativas; quota/timeout → próxima da lista |
| CLI `codex` | processo, stdin → JSONL | login da CLI | out/in | idem |
| CLI `gemini` | processo, stdin → JSON | login da CLI ou projeto Google | out/in | `ProjectIdRequiredError` → 65 |
| OpenRouter | HTTPS REST, `urllib` | `OPENROUTER_API_KEY` (ambiente) | out/in | 401/403 → 65; 429 → repete; 402/crédito → próxima |
| git | processo | — | local | base inexistente → 64 |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Unit | extração dos 4 formatos e corpo HTTP (AT-010, AT-020) | `tests/test_revisao_adapters.py` | unittest + `http.server` local | campos extraídos iguais aos esperados; corpo com `data_collection: deny` |
| Integration | script inteiro com o stub em repo git temporário (AT-001–AT-009, AT-011–AT-026, AT-041) | `tests/test_revisao.py` | unittest + `apoio.Sandbox` | exit, linhas do META e da saída |
| Integration | `loop` delta e não-regressão (AT-028–AT-031) | `tests/test_fluxo.py` | unittest | exit e `motivo:` |
| Integration | init, release.yml, skills, bash 3.2, lint de decisões (AT-027, AT-032–AT-035, AT-037, AT-038) | testes existentes estendidos | unittest | asserts de texto e de cópia |
| E2E / Verify Gate | suíte inteira na cópia do `git archive` + publish-gate | `cmd` do DEFINE | `verify-gate.sh --strict` | exit 0 |
| Manual | revisão real `claude` + `openrouter:qwen/qwen3.7-plus` (AT-040) | `sdd/reports/evidence/F10_REVISAO/real.sh` | bash | META com tokens, `US$` > 0, sha256; `loop` ≠ 64 |
| Sabotagem | 7 regras invertidas (AT-039) | `sabotagem.sh` | bash | teste nomeado vermelho e verde depois do `git checkout` |

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| uso / id / slot vazio | parse dos args e do registry | 64 + ids válidos | No | `RESULTADO: PAROU` + `→` |
| self-review | 1º id auditor == 1º id revisor | 67 antes de chamar | No | `→` com `--um-engine` |
| diff vazio, > 8 MB, base sem commit | tamanho / `merge-base` | 64 | No | motivo na saída |
| pasta não ignorada | `git check-ignore` | 64 + comando | No | frase da U5 |
| credencial | exit 65 ou `sinal_auth` na chamada falha | 65, para | No | `→` com `auth_check` do registry |
| 429 | `sinal_transitorio` | mesma engine, 2 vezes, espera | Yes | `<papel>_motivo` |
| quota, timeout, CLI ausente | `sinal_persistente` / `TimeoutExpired` / 66 | próxima da lista; esgotada → 67/66 | No (avança) | ⚠️ de troca; `_fallback_usado: sim` |
| resposta fora do formato | bloco ausente ou JSON inválido | papel 68; nunca "zero achados" | No | `REVIEW INVÁLIDA` |
| `python3` ausente | `command -v` na frente | 64 | No | mensagem |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `review.registry` | caminho | `sdd/review/registry.tsv` | No | engines |
| `review.revisor1` | lista de ids | `""` (pergunta) | No | revisor e reservas |
| `review.auditor` | lista de ids | `""` (pergunta) | No | auditor e reservas; ≠ revisor |
| `review.output_dir` | caminho | `sdd/reports/reviews` | No | precisa estar ignorado pelo git |
| `review.context_max_kb` | inteiro, KB | `180` | No | teto do contexto SDD |
| `review.security_globs` | globs por vírgula | `""` | No | já existe (F9); gatilho do 2º revisor |
| `OPENROUTER_API_KEY` | ambiente | — | Yes | só ambiente; nunca arquivo |
| `SDD_REVIEW_ESPERA` | ambiente, s | `30` | No | espera do 429 (testes: 0) |
| `SDD_REVIEW_ADAPTERS`, `SDD_REVIEW_OPENROUTER_URL`, `SDD_REVIEW_STUB_ESTADO` | ambiente | — | No | só testes |

---

## Security Considerations

- Chave só de `OPENROUTER_API_KEY` lida pelo `urllib` dentro do processo Python; nunca em argumento (`ps`), log, META ou fixture; os testes usam um valor gerado em execução.
- `data_collection: deny` e `require_parameters: true` em toda chamada ao OpenRouter; com nenhum provedor elegível a chamada falha (persistente), nunca cai num provedor que retém dado.
- Engines rodam sem ferramenta de escrita (`--tools ""`, `-s read-only`, `--approval-mode default`) numa pasta temporária vazia; `--safe-mode` desliga CLAUDE.md e skills do usuário.
- A pasta da revisão precisa estar ignorada pelo git: diff e respostas não entram em commit.
- O prompt vai por stdin (diff grande estoura o `ARG_MAX` por argumento).

---

## Observability

| Aspect | Implementation | Signal / Why |
|---|---|---|
| Logging | `META.txt` por execução; `▶` por papel; ⚠️ no topo | proveniência (default × efetivo), motivo, tempo |
| Metrics | tokens e custo por papel e `custo_total` | custo da revisão (sem meta: DEFINE) |
| Tracing | `diff_sha256` + `base`/`merge_base`/`head` | `--conferir` liga a revisão à versão publicada |

---

## Requirements Traceability

| Requirement / AT | Design Element | Test / Gate |
|---|---|---|
| AT-001–AT-005 | Decision 2; linhas 1, 10, 13 | `test_revisao.py` |
| AT-006, AT-007 | Decision 3 | `test_revisao.py` |
| AT-008, AT-009 | Decision 4 | `test_revisao.py` |
| AT-010 | Decision 4; linhas 6–9 | `test_revisao_adapters.py` |
| AT-011–AT-013, AT-036 | Decision 7; LP-001–LP-003 | `test_revisao.py`, `test_contrato_build_release.py` |
| AT-014–AT-016 | Decision 6 | `test_revisao.py` |
| AT-017–AT-019 | Decision 5 | `test_revisao.py` |
| AT-020, AT-021 | Decision 7; linha 2 | `test_revisao.py`, `test_revisao_adapters.py` |
| AT-022–AT-024, AT-041 | Decision 7 | `test_revisao.py`, `test_docs.py` |
| AT-025–AT-027 | Decision 8 | `test_revisao.py`, `test_contrato_build_release.py`, `test_decisoes_lint.py` |
| AT-028–AT-031 | Decision 9 | `test_fluxo.py` |
| AT-032–AT-035, AT-037 | Decision 10 | `test_contrato_build_release.py`, `test_sdd_open.py`, `test_fluxo.py` |
| AT-038, AT-039 | Decision 11 | suíte inteira; `sabotagem.sh`; `baseline.log` |
| AT-040 | Decision 11 | `real.sh` → `real.log` |

---

## Risks and Mitigations

| Risk | Impact | Mitigation | Residual Risk |
|---|---|---|---|
| CLI muda o formato JSON numa versão nova | custo/tokens viram `n/d`, texto vazio vira falha | extração tolerante (chave ausente → nulo); fixture do formato medido; F11 cobre por engine | formato novo exige atualizar o adapter |
| `claude --safe-mode` some ou muda | engine leria CLAUDE.md do usuário | `cwd` vazio; flag conferida no teste por argv | baixo |
| suíte maior estoura o teto do macOS (20 min) | release não sai | stubs locais, espera 0; medir no CI do PR | ajustar o teto no `release.yml` se passar de 18 min |
| sinal de AUTH casa texto normal de erro transitório | falso 65 | sinais ancorados em códigos e frases medidas | baixo |
| custo da prova real | dinheiro | um diff só, auditor de US$ 0,32/1,28 | centavos |

---

## Advisor Ledger

Preenchido pela revisão de contexto fresco do DESIGN, antes do build. Toda nota recebe APLICADA, REBATIDA_EVIDENCIA (com arquivo:linha) ou REBATIDA_ESCOPO.

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F10_REVISAO_20261031.md`, modo `contrato`, 8 logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 1 HIGH, 5 MEDIUM, 13 LOW (o revisor numerou 5 ajustes; o 5º tinha 2 itens, aqui M4).

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| H1 | 2º revisor que falha ou sem engine parava a cadeia; o auditor não rodava e a dispensa do `loop` nunca chegava a PRONTO; fixtures 28–33 em estado impossível | HIGH | APLICADA (Decision 5; DEFINE AT-015, AT-022, AT-023, AT-025; fixtures 28, 31; teste do `loop` sobre as pastas do stub, Decision 11) | `AVAL-DESIGN-loop.log`; privado `adversarial-review.sh:675–686` |
| M1 | `--ledger` no passo 6 roda no worktree temporário sem a pasta ignorada: release abortaria sempre | MEDIUM | APLICADA (Decision 8; DEFINE AT-026, AT-027) | `AVAL-DESIGN-ledger-worktree.log` |
| M2 | `.git/index` e `.git/info/exclude` literais falham em worktree | MEDIUM | APLICADA (Decisions 3, 4; DEFINE AT-006, AT-009; testes em `git worktree add`) | `AVAL-DESIGN-diff-congelado.log`, `AVAL-DESIGN-checkignore.log` |
| M3 | `→` do 65 cita `auth_check`, que o registry de 9 colunas não tem | MEDIUM | APLICADA (`adapter_credencial`, Decision 1; DEFINE AT-010, AT-023) | DEFINE:66, 88 |
| M4 | AT-033 sem assert (o `test_agnostico` não vê nome de engine) e AT-010 sem execução dos 3 adapters de CLI | MEDIUM | APLICADA (assert por seção em `test_contrato_build_release.py`; binários falsos, linhas 84–86) | `tests/test_agnostico.py:16–20` |
| L1 | timeout deixa a CLI neta viva | LOW | APLICADA (Pattern 2: `start_new_session` + `killpg`) | `AVAL-DESIGN-adapter.log` |
| L2 | adapter roda no `bash` do PATH | LOW | APLICADA (Decision 1: bash da frente) | — |
| L3 | stderr misturado ao JSON | LOW | APLICADA (Pattern 1: `<saida>.err`) | — |
| L4 | `apoio.py` herda `OPENROUTER_API_KEY` | LOW | APLICADA (Decision 11: ambiente do `test_revisao` sem chave, sem CLIs, URL morta) | `tests/apoio.py:35` |
| L5 | sha256 real com 11+ dígitos reprova o publish-gate | LOW | APLICADA (Decision 11: hex só de letras ou gerado) | `AVAL-DESIGN-ledger-worktree.log` |
| L6 | "sem ferramenta" é falso para leitura | LOW | APLICADA (Decision 4; DEFINE AT-010, AT-036) | `AVAL-DESIGN-flags-cli.log` |
| L7 | textos do `n/a (…)` não fixados | LOW | APLICADA (Decision 7; DEFINE AT-022) | — |
| L8 | `desempate_alvo` com id de base | LOW | APLICADA (Decision 6; DEFINE AT-016) | — |
| L9 | config do usuário muda os bytes do diff | LOW | APLICADA (Decision 3) | — |
| L10 | AT-040 dispara o 2º revisor; pasta não ignorada | LOW | APLICADA (DEFINE AT-040: `--no-revisor2` e exclude) | — |
| L11 | `test_docs.py` e docs fora do manifest | LOW | APLICADA (linhas 79–83; roadmap *planned* até a F11) | `docs/adaptation-guide.md:92`, `docs/chained-flow.md:75` |
| L12 | `RESULTADO:` no `--conferir`/`--ledger`; AT-021 não testável; doctor sem adapters | LOW | APLICADA (DEFINE AT-021, AT-025, AT-026, AT-035) | `bin/sdd-open.sh:774` |
| L13 | `TERMOS` duplicado; `\bauth` casa `author` | LOW | APLICADA em parte: segmento de caminho no 2º revisor (Decision 6); o regex do `review-design` (manifest em prosa) fica como está — REBATIDA_ESCOPO para a duplicação: são entradas diferentes (linha de tabela × caminho) | — |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.1 | 2026-10-31 | SDD Design by RDD | Revisão de contexto fresco: 1 HIGH, 5 MEDIUM, 13 LOW aplicados (Decisions 1, 3–8, 10, 11; Patterns 1–3; manifest 78 → 86; Advisor Ledger) |
| 1.0 | 2026-10-31 | SDD Design by RDD | Versão inicial a partir do BRAINSTORM, do DEFINE v1.2 e da UX review |

---

## Next Step

Execute o **SDD Build by RDD**.
