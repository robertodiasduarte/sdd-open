# BRAINSTORM: F10 + F11 Revisão adversarial (núcleo e gate offline)

> Exploratory session to clarify intent and approach before requirements capture

## Metadata

| Attribute | Value |
|---|---|
| Feature | F10_REVISAO (inclui a F11, gate offline, na mesma sessão e depois da Release da F10) |
| Date | 2026-10-31 |
| Author | brainstorm-agent |
| Status | Handoff Ready |

## Initial Idea

**Raw Input:** "leia e execute sdd/handoffs/SESSION_PROMPT_INCORPORAR_STARTER.md. a chave do openrouter esta em robertoduadte/.config" — o prompt de sessão pede a F10 (R1–R10, R12, R13 do PORTE §5.4) do brainstorm à release e, se sobrar folga, a F11 (R11): `sdd/bin/adversarial-review.sh` + um adapter por engine + `sdd/review/{registry.tsv,precos.tsv,prompts/}`; deltas no `sdd-fluxo.sh loop`, `sdd-design`, `sdd-build` e `sdd-release`; depois `adversarial-review-gate.sh`, stubs por engine e `eval-agree.sh`.

**Context Gathered:**
- Fato (conferido): worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f10-revisao`, branch `feat/f10-revisao` em `89ac76f` = `origin/main` = tag `v2.2.10`; artefatos SDD fora do commit; handoff igual ao da branch `docs/incorporar-starter`.
- Fato (conferido): `claude` 2.1.314, `codex-cli` 0.163.0 e `gemini` 0.22.2 instalados.
- Fato (fornecido + conferido): `OPENROUTER_API_KEY` em `~/.config/rdd-eval.env`; `GET /api/v1/key` autentica (conta paga, ~US$ 246 de saldo). Uso só como variável de ambiente carregada na hora; nunca em arquivo do repositório.
- Fato (conferido): este repositório não tem `.gitignore` e o `bin/sdd-open.sh` não o edita.
- Fato (conferido): a `sdd-release` do Open não cita review externo; o `RESUMO_ETAPA.md` e o `BUILD_REPORT_TEMPLATE.md` citam `/adversarial-review` (comando do privado).
- Fato (conferido): `sdd-fluxo.sh loop` (F9) lê `META.txt` (`reviewer_exit`, `auditor_exit`), `reviewer.verdicts.jsonl` (`achado`, `severidade`) e `auditor.verdicts.jsonl` (`veredito` AGREE/DISAGREE_EVIDENCE/DISAGREE_CONCERN/NOVO); sem 2º revisor, raso e desempate.
- Fato (conferido, privado `origin/main` = `1b1c1d41b`, só leitura): `scripts/adversarial-review.sh` é zsh (`${0:A}`, `print -u2`); exits do `adapters.sh` 64 engine desconhecido · 65 AUTH · 66 launcher · 67 cadeia esgotada · 68 vereditos ausentes · 75 aguarda sessão; `registry.tsv` com 13 colunas e cadeias fixas no `adapters.sh`; regra da release do privado: review de 2º vendor obrigatório com dispensa D3 registrada como `review_externo: dispensado — <motivo>` (antes, opcional, só 13 de 84 features de setembro tiveram review).
- Inferência: a degradação "1 engine só" do privado (`diversidade=nenhuma`, BRAINSTORM_SDD_OPEN_BY_RDD) e o exit 67 para `auditor == revisor1` convivem se a degradação for explícita (`--um-engine`).

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|---|---|---|
| Likely Location | `sdd/bin/adversarial-review.sh`, `sdd/bin/adapters/claude.sh`, `codex.sh`, `gemini.sh`, `openrouter.sh`, `sdd/review/registry.tsv`, `sdd/review/precos.tsv`, `sdd/review/prompts/`, `sdd/review/stubs/` (F11), `sdd/bin/adversarial-review-gate.sh` e `sdd/bin/eval-agree.sh` (F11); deltas em `sdd/bin/sdd-fluxo.sh`, `.agents/skills/sdd-design`, `sdd-build`, `sdd-release`, `sdd/templates/fragments/RESUMO_ETAPA.md`, `ADVISOR_CONSULT.md`, `sdd/config.example.yaml`, `docs/` | toda peça nova entra no `MANIFEST.txt`; skills tocadas sobem de versão com os pinos dos testes |
| Relevant KB Domains | N/A (o Open não tem KB deste tema); fontes no privado listadas no plano 8.3 | o que é RDD não viaja (regra 4 do 8.0) |
| IaC Patterns | bash 3.2 + `python3 -B` stdlib embutido por heredoc (molde do `sdd-fluxo.sh`); CI Ubuntu e macOS com tetos de 25 e 20 min | `grep -nE 'mapfile|declare -A|\$\{[a-zA-Z_]+\^\^'` sem achado; suíte maior pode estourar o teto do `testes-macos` |

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|---|---|---|
| 1 | [D2] Quais engines o `registry.tsv` traz de fábrica? | as 4 — `claude`, `codex` (`-s read-only`), `gemini`, `openrouter:<slug>` — sem cadeia padrão | quem revisa e quem audita vem do config ou de pergunta da skill; nenhuma cadeia fixa no script |
| 2 | [D3] Quais `review.*` viram slot? | 5 slots: `review.registry`, `review.revisor1`, `review.auditor`, `review.output_dir`, `review.context_max_kb`; constantes comentadas: `second_reviewer_min_files` 8, `second_reviewer_min_diff_kb` 120, `second_reviewer_min_layers` 2, `shallow_review_secs` 30, `diff_max_mb` 8 | 5 slots e 5 testes a menos; mudar uma constante é 1 linha |
| 3 | [D3] Quando a `sdd-release` exige o review externo (R1)? | sempre, com dispensa registrada | sem `review_externo` no ledger a release aborta na 0a; 3 saídas válidas (review desta frente, loop do build no mesmo HEAD, dispensa D3 antes do bloco do OK) |
| 4 | [auto] Só a F10 ou também a F11 nesta sessão? | F10 + F11 compromissadas | as duas em sequência; a F11 só abre depois da Release da F10 publicada e conferida (regra do par) |
| 5 | [D1] Versão da Release? | `v2.3.0` por tag para a F10; F11 `v2.3.1` automática | tag no HEAD empurrada junto com `main` (o `next-version.sh` publica exatamente essa tag, uma vez) |
| 6 | Prova real do critério de pronto (sem pergunta: resolvida pela mensagem inicial) | `claude` + `openrouter:<slug>` com a chave de `~/.config/rdd-eval.env` | relatório com tokens, custo ≠ 0 e sha256 do diff, consumido pelo `loop` |

## Sample Data Inventory

| Type | Location | Count | Notes |
|---|---|---:|---|
| Input files | privado `origin/main`: `scripts/adversarial-review/prompts/reviewer.md`, `auditor.md` | 2 | contrato do bloco `<<<VERDICTS`; reescritos, nunca copiados |
| Output examples | privado `origin/main`: `**/EXTERNAL_REVIEW_*/META.txt` | 315 | `auditor_exit` 0 em 281, 67 em 17, 68 em 11; 2º revisor por segurança 85, ≥ 8 arquivos 16, 2 camadas 5; desempate 15 (todos REFUTADO); convergência `nao` 218, `sim` 46, `n/a` 40; custo pay-per-token US$ 0,003–0,28 por papel |
| Ground truth | privado `.claude/sdd/archive/DOGFOOD_20260824/` (META com `auditor_exit 68`, `reviewer.verdicts.jsonl` de 7 achados); `evidence/*/ledger-review.md` | 1 + 69 | formato do ledger por célula com `R1@engine` e `rodada=N` |
| Related code | privado `scripts/adversarial-review.sh` (991 l.), `adapters.sh` (1.114 l.), `stubs/` (18), `eval-agree.sh` (207 l.), `adversarial-review-gate.sh` (695 l.); Open `sdd/bin/sdd-fluxo.sh` e `sdd/fixtures/fluxo/review-ok`, `review-invalida`, `review-impasse` | 6 + 3 | leitura do contrato; implementação nova |

**How samples will be used:**
- Uma seleção dos 315 META (ok, fallback, 67, 68, raso, AUTH, 429) vira fixture do Open **reescrita**: caminhos, engines e nomes da RDD trocados por exemplos neutros; nada copiado byte a byte (regra 4 e publish-gate).
- As chaves do META do Open são as mesmas do privado (mais `diversidade`), para o `loop` e a leitura humana não mudarem.
- Os stubs da F11 reproduzem o formato de saída de cada engine (resposta simulada daquele engine), com asserts sobre veredito, proveniência e custo extraídos.

## Approaches Explored

### Approach A: Reescrita pelo contrato, no molde do `sdd-fluxo.sh` — Recommended

**Description:** `adversarial-review.sh` em bash 3.2 com núcleo `python3 -B` embutido (seleção de papéis pelo registry, exclusão, gatilhos, parser do `<<<VERDICTS`, META, convergência, custo); um `sdd/bin/adapters/<engine>.sh` por engine com duas funções ("invocar" e "extrair tokens/custo"); `openrouter.sh` chama a API por `python3` urllib com `data_collection: deny`; META com as chaves do privado.

**Pros:**
- padrão já provado no piso (bash 3.2, Python 3.9) e no CI dos dois sistemas pela F9;
- um arquivo por engine: vendor novo = 1 linha no registry (+ 1 adapter só se for uma CLI nova);
- o `loop` e as pessoas leem o META igual ao do privado.

**Cons:**
- escrever do zero, sem colar código do privado;
- a F11 precisa de um stub por formato de engine para provar os adapters.

**Why Recommended:** cumpre a regra "um arquivo por engine", tira as 87 refs RDD por construção e mantém o padrão de `sdd/bin/`.

### Approach B: Porte literal do privado

**Description:** converter o `adversarial-review.sh` de zsh para bash e limpar o `adapters.sh` de 1.114 linhas.

**Pros:**
- começa mais rápido; o comportamento já foi usado 315 vezes.

**Cons:**
- construções só do zsh falham no bash 3.2;
- 87 refs RDD para tirar uma a uma; continua um arquivo único, contra a regra do plano.

### Approach C: Orquestrador inteiro em Python

**Description:** `adversarial-review.py` só com stdlib, adapters como módulos Python, um `.sh` fino de entrada.

**Pros:**
- testes e HTTP mais simples.

**Cons:**
- foge do que o plano fixou (`sdd/bin/adapters/*.sh`) e do padrão bash + núcleo Python de `sdd/bin/`.

## Selected Approach

| Attribute | Value |
|---|---|
| Chosen | Approach A |
| User Confirmation | 2026-10-31, resposta "A" na etapa 4 |
| Reasoning | padrão provado na F9, um adapter por engine, META compatível com o consumidor |

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|---|---|---|
| 1 | registry com `claude`, `codex` (`-s read-only`), `gemini`, `openrouter` (uso `openrouter:<slug>`), sem cadeia padrão | serve aos 7 agentes sem impor vendor | só as 2 da prova; as 4 com cadeia padrão |
| 2 | slots `review.registry`, `review.revisor1`, `review.auditor`, `review.output_dir`, `review.context_max_kb`; o resto constante comentada | só o que é escolha do projeto vira slot | os 10 do plano; só os 3 de engine |
| 3 | `review.revisor1` e `review.auditor` aceitam lista separada por vírgula (a cadeia que o projeto configura) | dá sentido ao "quota avança" da R7 sem cadeia de fábrica | 1 id só, sem fallback |
| 4 | R1: review externo sempre exigido na `sdd-release`, com dispensa D3 registrada antes do bloco do OK; `--conferir <pasta>` recalcula o `diff_sha256` do HEAD sem chamar engine | "opcional" deu 13 de 84 no privado; o bloco do OK tem uma pergunta só (contrato) | só quando o `review-design` exige; nunca obrigatório |
| 5 | `auditor == revisor1` → exit 67 com a dica `--um-engine`; com `--um-engine`, a mesma engine faz os dois papéis em chamadas separadas e o META/ledger marca `diversidade: nenhuma` com aviso | self-review silencioso é falso-verde; 1 engine só degrada com aviso, nunca pula | degradação automática |
| 6 | 2º revisor: `--revisor2` ou a 1ª engine do registry com papel de revisor fora de {revisor1, auditor}; nenhuma elegível → `revisor2_engine: indisponível` e o `loop` pede a dispensa D3 | sem slot novo; o registry é editável | slot `review.revisor2` |
| 7 | custo por papel: valor da engine → `≈US$` pelo `precos.tsv` → `assinatura` → `$?`; nunca 0; `precos.tsv` só com preço lido da API ao vivo, com fonte e data | R10; nunca precificar de memória | custo 0 quando desconhecido |
| 8 | R9: `output_dir` fora do `git check-ignore` → 64 com a linha exata para o `.git/info/exclude`; OpenRouter com `data_collection: deny` e `require_parameters: true`; CLIs sem ferramenta de escrita; prompt por stdin | privacidade e ARG_MAX | `init` editar o `.gitignore` |
| 9 | F10 + F11 nesta sessão; Release `v2.3.0` por tag (F10) e `v2.3.1` automática (F11) | a R1 muda o comportamento de toda release | `v2.2.11` automática |
| 10 | prova real com revisor `claude` e auditor `openrouter:<slug>` sobre o diff da própria F10; o slug sai do `/models` ao vivo no design | critério de pronto do quadro F10 | `claude` + `codex` com OpenRouter só em stub |

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed/Deferred | Can Add Later? |
|---|---|---|
| engine de classe "sessão", `auditor_exit 75`, `consumir-auditor-sessao.sh`, `--revisor2-arquivo` | no Open o Claude entra como `claude -p` no registry; o papel fresco "de sessão" já é o avaliador da F7/F9; o `loop` não ganha o caso 75 (exit ≠ 0 continua "review inválida") | Yes |
| `--preparar` / `--out` (reusar o diff de outra execução) | só servia ao modo de sessão | Yes |
| `saude_cadeia` (aviso após 3 quedas PERSISTENTE, 2ª metade da R8) | exige estado entre execuções; a 1ª metade (`convergencia: n/a`) fica | Yes |
| stubs de grok/kimi, cadeias fixas e notas históricas do registry | específicos da RDD (regra 4) | No |
| `init` editar o `.gitignore` do projeto | o script recusa e imprime a linha que resolve | Yes |
| slots `second_reviewer_*`, `shallow_review_secs`, `diff_max_mb` | viram constantes comentadas (pergunta 2) | Yes |

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---|---|---|---|
| Checkpoint 1 — conceito, peças da F10 e da F11, lista como cadeia configurável, 5 cortes YAGNI | Yes | "sim" | No |
| Checkpoint 2 — fluxo (papéis, diff congelado, contexto, R9, revisor, 2º revisor, auditor, desempate, META), falhas e exits 64–68, `--um-engine`, `--conferir` na release, R12/R13, prova real | Yes | "sim" | No |

## Suggested Requirements for /define

### Problem Statement (Draft)

O Open não tem revisão adversarial: o review de 2º vendor existe só no SDD privado, com cadeias e engines fixas da RDD, e a `sdd-release` do Open publica sem nenhum review externo; o `sdd-fluxo.sh loop` da F9 não tem uma revisão real para consumir.

### Target Users (Draft)

| User | Pain Point |
|---|---|
| quem usa o Open em qualquer dos 7 agentes | não tem como pedir a uma engine de outro vendor que revise o diff e a outra que audite a revisão, com custo e proveniência registrados |
| o Roberto, na troca do privado pelo Open (F15) | o mecanismo do privado (315 revisões) precisa existir no Open sem as cadeias da RDD |
| a `sdd-release` e o `sdd-fluxo.sh loop` | sem saída de review para conferir, a release segue sem review e o loop não tem insumo real |

### Success Criteria (Draft)

- [ ] `review.auditor == review.revisor1` → exit 67; auditor sem veredito → exit 68 (stub).
- [ ] `--um-engine` → META e ledger com `diversidade: nenhuma` e aviso no topo da saída.
- [ ] `sdd-release` sem `review_externo` no ledger aborta na 0a; com `dispensado — <motivo>` ou META de `diff_sha256` igual ao do HEAD, segue.
- [ ] review real `claude` + `openrouter:<slug>` produz `META.txt` com tokens, custo ≠ 0 (ou `$?` declarado) e `diff_sha256`, e `sdd-fluxo.sh loop` lê a saída.
- [ ] AUTH → 65 sem trocar de engine; 429 → 2 novas tentativas na mesma engine; quota → próxima da lista; lista esgotada → 67 (stubs).
- [ ] `output_dir` não ignorado → 64; diff vazio ou acima de 8 MB → 64; contexto acima de 180 KB corta o BRAINSTORM primeiro.
- [ ] todo script novo sem `mapfile`/`declare -A`/`${X^^}`, com fixture, teste dos dois lados e 1 sabotagem; suíte inteira verde no piso (`/bin/bash`, `/usr/bin/python3`).
- [ ] `skill-lint --conversa` 0 nas 17 skills e `sdd-decisoes-lint --sites` 0 (a contagem de perguntas muda com a pergunta D3 de dispensa).
- [ ] F11: `adversarial-review-gate.sh` → 0 sem rede, com asserts de veredito, proveniência e custo por engine; `eval-agree.sh` roda sobre as fixtures.
- [ ] Releases `v2.3.0` (F10) e `v2.3.1` (F11) com `SHA256SUMS.txt` conferido.
- [ ] Tempo de cada papel e custo por review: TBD (sem meta fixada; medido e registrado no BUILD_REPORT).

### Constraints Identified

- bash 3.2 e Python 3.9 stdlib; CI Ubuntu e macOS com tetos de 25 e 20 min.
- chave de API nunca em arquivo, nem em stub (valor gerado em execução ou obviamente falso); G1 (gitleaks) varre `tests/` e `sdd/review/stubs/`.
- nomes de engine só no `registry.tsv` e em `sdd/bin/adapters/`, nunca em texto de skill (`tests/test_agnostico.py`, regra 10).
- delta-only nas skills; toda pergunta nova com marca `[<código> · <rótulo>]`; o bloco do OK da `sdd-release` mantém uma pergunta só.
- `loop` cresce por delta: os exits e os 3 casos de borda da F9 continuam.
- repositório privado só leitura; nada da RDD viaja.

### Out of Scope (Confirmed)

- engine de sessão, exit 75 e reuso de diff (`--preparar`/`--out`).
- `saude_cadeia` entre execuções.
- `init` editando `.gitignore`.
- F12–F15, cartógrafo, curator, `/drive`; alterar o sdd-starter ou o privado.

## Session Summary

| Metric | Value |
|---|---:|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 6 |
| Validations Completed | 2 |

## Next Step

Execute o **SDD Define by RDD**.
