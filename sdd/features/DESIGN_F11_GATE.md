# DESIGN: F11 Revisão adversarial — gate offline

> Technical design for implementing F11 Revisão adversarial — gate offline

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F11_GATE |
| **Date** | 2026-11-01 |
| **Author** | SDD Design by RDD |
| **BRAINSTORM** | `sdd/features/BRAINSTORM_F10_REVISAO.md` (parte F11) |
| **DEFINE** | `sdd/features/DEFINE_F11_GATE.md` |
| **UX REVIEW** | N/A — a interface é a saída de dois scripts no padrão `RESULTADO:` + `→` já revisado na F10 (`sdd/reviews/UX_REVIEW_F10_REVISAO.md`) |
| **LLM Prompts** | false |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 adversarial-review-gate.sh [-v]                       eval-agree.sh [<pasta>]
   │ (bash 3.2 → núcleo python3 -B)                       │ (bash 3.2 → núcleo python3 -B)
   ├─ pré-voo: stubs, registry com 4 engines ─✗→ exit 3   ├─ lê EXTERNAL_REVIEW_*/META.txt
   ├─ isola: PATH=<tmp>/bin:…, http(s)_proxy morto,       │      + auditor.verdicts.jsonl
   │         OPENROUTER_API_KEY gerada, ESPERA=0          ├─ agrupa por auditor (engine + modelo)
   ├─ sobe sdd/review/stubs/openrouter.py (127.0.0.1:0)   └─ tabela + "fora da conta" → exit 0 | 2 | 64
   ├─ repo git descartável com um diff real
   └─ para cada cenário:
        SDD_STUB_<ENGINE>=fila de cenários ─┐
        adversarial-review.sh --reviewer X --auditor Y   (adapters REAIS de sdd/bin/adapters/)
              │                              │
              ▼                              ▼
        <tmp>/bin/claude|codex|gemini  ──►  sdd/review/stubs/<engine>.py  (formato daquela engine)
        urllib → 127.0.0.1             ──►  sdd/review/stubs/openrouter.py (HTTP, formato da API)
              │                              │  lê sdd/review/stubs/cenarios.tsv + respostas/*.md
              ▼                              │  engine sem fila → sentinela + exit 99
        META.txt + *.verdicts.jsonl          │
              │                              │
              └──► asserções (valor esperado vem de cenarios.tsv) → ✅/❌ N. … → exit 0 | 2
```

---

## Components

| Component | Purpose | Technology / Pattern | Inputs | Outputs | Dependencies |
|---|---|---|---|---|---|
| Stubs por engine | imitar a saída de **cada** engine no formato medido na F10 | `claude.py`, `codex.py`, `gemini.py`, `openrouter.py` e `comum.py` em `sdd/review/stubs/`, Python 3.9 stdlib | prompt (stdin ou corpo HTTP), `SDD_STUB_<ENGINE>`, `SDD_STUB_ESTADO` | stdout/stderr/exit da CLI ou resposta HTTP; registro da chamada no estado | `cenarios.tsv`, `respostas/*.md` |
| Tabela de cenários | uma fonte para o que o stub emite **e** o que o META deve dizer | `sdd/review/stubs/cenarios.tsv` (TSV) | — | linhas por (engine, cenário) | — |
| Gate | rodar a revisão ponta a ponta e conferir campos | `sdd/bin/adversarial-review-gate.sh` (bash 3.2 + núcleo Python) | `-v` | linhas `✅/❌ N.`, `RESULTADO:`, exit 0/2/3/64 | stubs, `adversarial-review.sh`, adapters, registry do pacote |
| eval-agree | taxa de AGREE por auditor sem chamar engine | `sdd/bin/eval-agree.sh` (bash 3.2 + núcleo Python) | pasta de revisões (padrão `review.output_dir`) | tabela markdown, exit 0/2/64 | — |
| Deltas do núcleo | achados #15, #17, #18 | `sdd/bin/adversarial-review.sh`, `sdd/bin/adapters/gemini.sh` | — | — | — |

---

## Key Decisions

### Decision 1: Um stub por engine, em Python, com fila de cenários por engine

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | DEFINE (Goals 2; AT-002, AT-003, AT-009); PLANO §8 F11 "Atenção" (REVIEW achado 3) |

**Context:** o stub genérico da F10 (`stub.sh`) troca o adapter; a F11 precisa provar o adapter real, então o stub tem de ficar do outro lado: no lugar da CLI ou da API, devolvendo exatamente o formato daquela engine.

**Choice:**
- `sdd/review/stubs/<engine>.py` para claude (JSON único com `result`, `total_cost_usd`, `usage`, `modelUsage`), codex (JSONL `thread.started`, `item.completed`/`agent_message`, `turn.completed` com `usage`), gemini (JSON com `response` e `stats.models.<modelo>.tokens`) e openrouter (servidor HTTP em `127.0.0.1:0` que responde `choices`, `model`, `provider`, `usage.cost`); `comum.py` lê a fila e a tabela.
- **Um servidor do openrouter por cenário** que usa o openrouter (v1.1, ajuste 2): o gate o sobe com o ambiente daquele cenário (fila e estado), espera a porta escrita em `<estado>/openrouter.porta` (≤ 5 s) e o derruba no fim. Requisição sem entrada na fila ⇒ acrescenta `openrouter` à sentinela e responde **HTTP 599** com corpo `sentinela` (nenhum sinal do registry casa ⇒ falha persistente). Cada requisição grava `<estado>/openrouter.<n>.entrada` (corpo) e `.auth` (o header Authorization).
- As CLIs falsas **não** são arquivos do pacote: o gate grava em `<tmp>/bin/` wrappers de 2 linhas (`exec python3 -B <stubs>/<engine>.py "$@"`) e põe `<tmp>/bin` na frente do `PATH`. Assim o bit de execução não depende de como o `init` copiou `sdd/review/`.
- Fila: `SDD_STUB_<ENGINE>` (ex.: `SDD_STUB_CODEX=429,revisor`) é consumida uma entrada por chamada, com contador em `SDD_STUB_ESTADO/<engine>.n`; cada chamada grava `SDD_STUB_ESTADO/<engine>.<n>.argv` e `.entrada`. Engine sem fila ⇒ grava `<engine>` em `SDD_STUB_ESTADO/sentinela` e sai 99.
- Cenários de falha são **sintéticos** (marcados assim em `cenarios.tsv`, coluna `fonte`): emitem o texto que o registry classifica para aquela engine (auth, 429, cota): claude `authentication_error`, codex `401 Unauthorized`/`429 Too Many Requests`/`usage limit`, gemini `UNAUTHENTICATED`/`429`/`RESOURCE_EXHAUSTED`, openrouter HTTP 401/429/402 com o corpo JSON da API.

**Rationale:** Python já é requisito do pacote; um arquivo por engine segue a regra da F10 ("engine nova = 1 linha + 1 adapter"); a fila torna explícito quem pode ser chamado, e o resto cai na sentinela.

**Alternatives Rejected:**
1. Wrappers em `sh` versionados com bit de execução — o `init` copia com `cp`, e um bit perdido viraria "CLI não encontrada" em vez de um formato testado.
2. Escolher a resposta lendo o prompt (revisor vs. auditor) — acopla o stub ao texto dos prompts; uma reescrita do prompt quebraria o gate em silêncio.

**Consequences:**
- O gate testa as 4 funções reais de cada adapter (`disponivel`, `invocar`, `extrair`, `credencial`).
- A tabela de cenários precisa acompanhar uma mudança de formato medida numa CLI (documentado em `docs/adversarial-review.md`).

### Decision 2: O gate roda `adversarial-review.sh` de verdade e confere o META contra `cenarios.tsv`

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | DEFINE (AT-001–AT-013); Success Criteria |

**Context:** asserção de fiação (grep no código) não prova comportamento; o valor esperado não pode ser escrito duas vezes.

**Choice:**
- Repo descartável: `git init` em `mktemp -d`, um arquivo commitado e alterado (diff de 1 arquivo, sem segmento de segurança, abaixo dos limiares do 2º revisor), `.gitignore` com `sdd/reports/reviews/`, identidade `-c user.name=gate -c user.email=gate@example.com`. Sem `sdd/config.yaml`: as engines vêm por `--reviewer`/`--auditor` e o registry é o do pacote (`sdd/bin/../review/registry.tsv`).
- **Ambiente dos filhos** (v1.1, ajuste 1): `adversarial-review.sh` roda com `BASH_ENV` e `ENV` removidos e sem nenhuma variável `BASH_FUNC_*`; `GIT_CONFIG_GLOBAL=/dev/null` e `GIT_CONFIG_NOSYSTEM=1` (hooks, assinatura de commit e atributos do usuário fora).
- Respostas do revisor sempre com 2 achados (MED e LOW): 0 achados em < 30 s acionaria o revisor raso, e um HIGH refutado acionaria o desempate.
- Anel de 4 execuções para os campos por engine: claude→codex, codex→gemini, gemini→openrouter, openrouter→claude. Cada uma confere, do revisor e do auditor: `*_exit 0`, `*_engine_efetivo`, `reviewer_achados 2`, `auditor_vereditos 2`, as linhas dos `*.verdicts.jsonl` e **só os campos que discriminam** a extração daquela engine (v1.1, ajuste 3): claude `*_modelo` e `*_custo US$`; codex `*_tokens_entrada/saida` (o modelo fica `-` e o custo `assinatura`, conferidos mas não contados); gemini `*_modelo` e tokens (custo `$?`, idem); openrouter `*_modelo <slug> via <provedor>` e `*_custo US$`. O valor esperado vem da linha de `cenarios.tsv` (colunas `modelo`, `custo`, `tokens_entrada`, `tokens_saida`), que é o que o stub emite.
- Custo estimado (v1.1, ajuste 5): o cenário openrouter `sem-custo` reporta 1234567/234567 tokens; o gate calcula o `≈US$` esperado com a mesma regra do script sobre o `precos.tsv` e o `registry.tsv` que o script resolve (`<bin>/../review/`) — uma atualização legítima de preço não quebra o gate; trocar a tarifa consultada (sabotar o #17a) quebra.
- Contagem de chamadas por cenário: `<estado>/<engine>.n` igual ao esperado para cada engine da fila; sentinela vazia.
- Cenários de contrato: 68 (auditor `sem-bloco`), 67 (mesma engine nos dois papéis; o estado mostra 0 chamadas), 67 por exclusão (v1.1, ajuste 4: `--reviewer gemini,codex --auditor codex` com gemini `cota` ⇒ `auditor_exit 67`, `auditor_motivo` com `excluída`, `reviewer_engine_efetivo codex`, `codex.n == 1`), 65 (`--reviewer claude,codex` com claude `auth`: codex com 0 chamadas), 429 (`SDD_STUB_CODEX=429,revisor`: 2 chamadas, `reviewer_engine_efetivo codex`, exit 0), cota (`--reviewer gemini,claude` com gemini `cota`: `reviewer_fallback_usado sim`, efetivo claude), custo estimado (openrouter `sem-custo` ⇒ `≈US$`) e modelo sem preço (openrouter `modelo-sem-preco` ⇒ `$?`, AT-019).
- Isolamento (AT-009, AT-010): `http_proxy`/`https_proxy`/`HTTP_PROXY`/`HTTPS_PROXY=http://127.0.0.1:9`, `no_proxy=127.0.0.1,localhost`, `SDD_REVIEW_ESPERA=0`, `OPENROUTER_API_KEY=gate-<pid>-falsa` gerada na execução; no fim, a sentinela vazia e a chave ausente de todo arquivo das pastas `EXTERNAL_REVIEW_*`; o servidor recebeu `Authorization: Bearer <a chave gerada>` (prova de que a chave chegou) e o corpo tem `provider.data_collection == "deny"`.
- Pré-voo (AT-011), antes de qualquer chamada: os 4 `<engine>.py`, `comum.py` e `cenarios.tsv` existem; num `/bin/bash -c` filho com **exatamente** o ambiente que `adversarial-review.sh` recebe, `command -v claude|codex|gemini` imprime um caminho sob `<tmp>/bin` (função exportada ou `BASH_ENV` que reordene o `PATH` ⇒ exit 3 com o valor resolvido); o registry do pacote tem as 4 engines com adapter existente; o servidor do openrouter escreveu a porta em ≤ 5 s. Falhou ⇒ exit 3 nomeando o item.
- Cada asserção é independente: uma falha não interrompe as seguintes (AT-012). Exits: 0 todas passaram · 2 alguma falhou · 3 o gate não conseguiu se isolar · 64 uso.

**Rationale:** o META é o contrato que o `loop` e as pessoas leem; conferir o META é conferir o comportamento.

**Alternatives Rejected:**
1. Chamar `adapter_extrair` direto — já existe em `tests/test_revisao_adapters.py`; não prova o caminho adapter → núcleo → META.
2. Usar o registry do projeto do usuário — um registry editado mudaria os ids; o gate prova o pacote instalado.

**Consequences:**
- ~12 execuções do script; alvo ≤ 120 s no piso (A-003, medido no build).
- Um registry do projeto com engines próprias não é coberto (documentado).

### Decision 3: `eval-agree.sh` só lê revisões já feitas

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | DEFINE Clarifications (resposta do Roberto: "só ler revisões já feitas"); AT-014–AT-017 |

**Context:** a pergunta é "este auditor critica ou só concorda?"; o material já está nas pastas de revisão.

**Choice:**
- Pasta: o argumento, ou `review.output_dir` do `sdd/config.yaml` da raiz git (padrão `sdd/reports/reviews`). Pasta inexistente ou flag desconhecida ⇒ 64.
- Para cada `EXTERNAL_REVIEW_*` com `META.txt`: entra na conta se `auditor_exit 0` **e** `auditor.verdicts.jsonl` legível; senão vai para "fora da conta" com o motivo (`auditor_exit N`, `sem auditor.verdicts.jsonl`, `META ilegível`).
- Chave do auditor: `auditor_engine_efetivo` + ` (` + `auditor_modelo` sem o sufixo ` via <provedor>` + `)` (v1.1, LOW 4: o roteamento do OpenRouter não parte um auditor em várias linhas).
- Nunca importa `urllib`/`socket` nem lê `adapters/` (AT-017, conferido por teste).
- `taxa_agree = AGREE / (AGREE + DISAGREE_EVIDENCE + DISAGREE_CONCERN)` com 1 casa; `NOVO` em coluna própria (não é veredito sobre achado); denominador 0 ⇒ `n/a`.
- Saída: cabeçalho com quantas pastas leu, a tabela ordenada por auditor, a linha "fora da conta: N (…)" e `RESULTADO: MEDIDO` + `→ uma taxa_agree alta com poucos DISAGREE pode ser auditor complacente: compare com outra engine no papel de auditor`. Nenhuma revisão utilizável ⇒ `RESULTADO: SEM DADOS`, exit 2.

**Rationale:** custo zero, roda nas fixtures e na pasta real; a re-execução de auditores ficou fora (Clarifications).

**Alternatives Rejected:**
1. `--executar` (re-rodar auditores) — custo pago por caso; fora de escopo.
2. Taxa sobre todos os vereditos incluindo NOVO — mistura "concordou" com "achou algo novo".

**Consequences:**
- A taxa mede o comportamento nas revisões que o projeto rodou, com o viés de quais diffs foram revisados (dito no doc).

### Decision 4: Os 6 achados adiados da F10

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | BUILD_REPORT_F10 (#15, #17, #18); DEFINE AT-018–AT-023 |

**Choice:**
- **#15 (AT-018):** no `--conferir`, se `gatilho_2o_revisor` termina em `— dispensado por --no-revisor2`, exigir `--aceitar-sem-revisor2 "<motivo>"` (≥ 3 caracteres), com a mesma mensagem e o mesmo sufixo `revisor2=dispensado — <motivo>` do 2º revisor que falhou.
- **#17a (AT-019):** em `custo()`, o modelo reportado (sem o ` via <provedor>`) manda: se ele existe e é diferente do configurado, só a tarifa **dele** vale; sem tarifa ⇒ `$?` (ou `assinatura` quando a engine é de assinatura). Igual ao configurado ou não reportado ⇒ tarifa do configurado, como hoje.
- **#17b (AT-020):** em `papel()`, uma tentativa que estourou o teto de tempo numa engine com `cobranca ≠ assinatura` marca `reg["custo_incerto"]`; `custo()` acrescenta ` + $?` ao que souber (`US$ x + $?`, `≈US$ x + $?`, ou só `$?`). Recusa (auth, 429, cota) não marca. O total soma a parte conhecida e conta o papel em `(+ N papel(is) com custo $?)`.
- **#18a (AT-021):** a lista de candidatos do `--conferir` sem pasta exige `META.txt` não vazio.
- **#18b (AT-022):** `--feature F` sem nenhum dos 4 documentos ⇒ aviso `⚠️ --feature F: nenhum documento encontrado (sdd/features/BRAINSTORM_F.md, DEFINE_F.md, DESIGN_F.md, sdd/reports/BUILD_REPORT_F.md)`; a revisão segue.
- **#18c (AT-023):** `adapters/gemini.sh` soma `prompt` e `candidates` de todos os modelos de `stats.models` e reporta `modelo` como os nomes unidos por `+` (o de mais tokens primeiro).

**Rationale:** cada um fecha o achado sem mudar o uso publicado na v2.3.0.

**Alternatives Rejected:**
1. Exigir motivo na flag `--no-revisor2` — rejeitado pelo Roberto (quebra o uso).
2. Marcar `+ $?` em todo 429 — o 429 é recusado antes de processar; seria ruído.

**Consequences:**
- Um `custo` com ` + $?` é texto novo no META: `sdd-fluxo.sh loop` não lê custo (conferido), então não muda.

### Decision 5: CI, docs e roadmap por delta

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | DEFINE (AT-025–AT-027) |

**Choice:**
- `timeout-minutes: 30` no job `testes-macos` de `release.yml` e de `publish-gate.yml`; `tests/test_release_workflow.py` fixa 30 nos dois.
- `docs/adversarial-review.md` + PT: seção "Gate offline" (comando, o que prova, exits 0/2/3/64, como acrescentar o formato de uma engine nova) e seção "eval-agree" (o que é `taxa_agree`, o viés); `docs/cli-conventions.md` (+ PT, se houver a tabela) ganha as 2 linhas de exit.
- Linha "Adversarial review" sai de `docs/roadmap.md` e `docs/pt-BR/roadmap.md`; `tests/test_docs.py` tira `Adversarial`/`adversarial` da tupla do roadmap.
- `MANIFEST.txt` com os arquivos novos; o `init` já copia `sdd/review/**` (`find … review …`), então os stubs chegam ao projeto; `tests/test_sdd_open.py` confere que `sdd/review/stubs/cenarios.tsv` chega.

**Alternatives Rejected:**
1. Teto de 25 no macOS — 18m31s medidos + o gate deixariam ~5 min de folga; 30 dá margem para a variação do runner.

**Consequences:**
- O push de `main` toca `sdd/bin/**` e `sdd/review/**` ⇒ release `v2.3.1` automática.

### Decision 6: Provas — o gate dentro da suíte, sabotagem, baseline e a revisão real

| Attribute | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-11-01 |
| **Source** | DEFINE Success Criteria; playbook LM-001/LM-002; `sdd-release` R1 |

**Choice:**
- `tests/test_revisao_gate.py` roda o gate (exit 0; `-v` mostra valores; exit 3 sem stub, com um `claude` real à frente no `PATH` e com registry sem engine) e 5 sabotagens numa cópia de `sdd/` (custo do claude, tokens do codex, modelo do gemini, `usage.cost` do openrouter, exclusão de papéis): cada uma ⇒ exit 2 com o nome da asserção.
- `tests/test_eval_agree.py` sobre `sdd/fixtures/revisao/eval/` (4 pastas: 2 auditores contáveis, 1 `auditor_exit 68`, 1 sem jsonl) com os números exatos.
- `tests/test_revisao.py`/`test_revisao_adapters.py` com os 6 achados (vermelhos na v2.3.0).
- Baseline: os testes novos rodados contra `v2.3.0` ficam vermelhos; evidência em `sdd/reports/evidence/F11_GATE/`.
- Fim do build: revisão real (claude + codex → openrouter) sobre o diff final, `--conferir` CONFERE ⇒ `review_externo` da release.

**Consequences:**
- A suíte cresce em ~15–25 s no piso (o gate roda uma vez por teste que o chama; os testes de sabotagem copiam `sdd/` para `mktemp`).

---

## File Manifest

| # | File | Action | Purpose | Agent / Owner | Dependencies |
|---:|---|---|---|---|---|
| 1 | `sdd/review/stubs/cenarios.tsv` | Create | cenários por engine: resposta, modelo, custo, tokens, falha e o valor esperado no META (Decision 1, 2) | (general) | None |
| 2 | `sdd/review/stubs/respostas/revisor.md` | Create | resposta do revisor com 2 achados (R1 MED, R2 LOW) e o bloco `<<<VERDICTS` | (general) | None |
| 3 | `sdd/review/stubs/respostas/auditor-agree.md` | Create | auditoria com AGREE para R1 e R2 | (general) | 2 |
| 4 | `sdd/review/stubs/respostas/auditor-sem-bloco.md` | Create | auditoria sem o bloco (exit 68) | (general) | None |
| 5 | `sdd/review/stubs/comum.py` | Create | fila `SDD_STUB_<ENGINE>`, estado, sentinela, leitura de `cenarios.tsv` | (general) | 1 |
| 6 | `sdd/review/stubs/claude.py` | Create | formato JSON do `claude -p --output-format json` | (general) | 5 |
| 7 | `sdd/review/stubs/codex.py` | Create | JSONL do `codex exec --json` | (general) | 5 |
| 8 | `sdd/review/stubs/gemini.py` | Create | JSON do `gemini -o json` | (general) | 5 |
| 9 | `sdd/review/stubs/openrouter.py` | Create | servidor HTTP local com a resposta da API e o registro do corpo | (general) | 5 |
| 10 | `sdd/bin/adversarial-review-gate.sh` | Create | gate (Decision 2) | (general) | 1–9 |
| 11 | `sdd/bin/eval-agree.sh` | Create | taxa de AGREE (Decision 3) | (general) | None |
| 12 | `sdd/bin/adversarial-review.sh` | Modify | #15, #17a, #17b, #18a, #18b (Decision 4) | (general) | None |
| 13 | `sdd/bin/adapters/gemini.sh` | Modify | #18c (Decision 4) | (general) | None |
| 14 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000001/META.txt` | Create | auditor A contável | (general) | None |
| 15 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000001/auditor.verdicts.jsonl` | Create | vereditos do auditor A | (general) | 14 |
| 16 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000002/META.txt` | Create | auditor B contável | (general) | None |
| 17 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000002/auditor.verdicts.jsonl` | Create | vereditos do auditor B | (general) | 16 |
| 18 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000003/META.txt` | Create | `auditor_exit 68` (fora da conta) | (general) | None |
| 19 | `sdd/fixtures/revisao/eval/EXTERNAL_REVIEW_20260101-000004/META.txt` | Create | `auditor_exit 0` sem jsonl (fora da conta) | (general) | None |
| 20 | `tests/test_revisao_gate.py` | Create | gate, pré-voo, `-v`, 5 sabotagens | (general) | 10 |
| 21 | `tests/test_eval_agree.py` | Create | números exatos das fixtures, exits 2/64, sem rede | (general) | 11, 14–19 |
| 22 | `tests/test_revisao.py` | Modify | #15, #17a, #17b, #18a, #18b | (general) | 12 |
| 23 | `tests/test_revisao_adapters.py` | Modify | #18c | (general) | 13 |
| 24 | `.github/workflows/release.yml` | Modify | `testes-macos` 30 min | (general) | None |
| 25 | `.github/workflows/publish-gate.yml` | Modify | `testes-macos` 30 min | (general) | None |
| 26 | `tests/test_release_workflow.py` | Modify | fixa 30 nos dois workflows | (general) | 24, 25 |
| 27 | `docs/adversarial-review.md` | Modify | seções "Offline gate" e "eval-agree" | (general) | 10, 11 |
| 28 | `docs/pt-BR/adversarial-review.md` | Modify | "Gate offline" e "eval-agree" | (general) | 27 |
| 29 | `docs/cli-conventions.md` | Modify | exits do gate e do eval-agree | (general) | 10, 11 |
| 30 | `docs/roadmap.md` | Modify | tira a linha "Adversarial review" | (general) | None |
| 31 | `docs/pt-BR/roadmap.md` | Modify | tira a linha "Revisão adversarial" | (general) | None |
| 32 | `tests/test_docs.py` | Modify | roadmap sem `Adversarial`; links novos | (general) | 27–31 |
| 33 | `tests/test_sdd_open.py` | Modify | `init` leva `sdd/review/stubs/` | (general) | 1–9 |
| 34 | `MANIFEST.txt` | Modify | arquivos novos | (general) | 1–21 |

**Total Files:** 34

### Agent Assignment Rationale

| Agent / Owner | Files Assigned | Why |
|---|---|---|
| (general) | 1–34 | modo default (um agente), como na F10; sem catálogo de agentes no repositório |

**Agent Discovery:** Not available

---

## Landmines aplicáveis

| LM-nnn | Superfície | Tratamento |
|---|---|---|
| LM-001 | gate e testes | ✔ cada asserção confere o valor do META contra `cenarios.tsv`, não só o exit |
| LM-002 | testes novos | ✔ baseline vermelha na `v2.3.0` e 5 sabotagens |
| LM-003 | diff congelado | ✔ o gate usa um repo próprio; a revisão real roda sobre o commit final |
| LM-004 | — | N.A.: sem migration |

---

## Code Patterns

### Pattern 1: Fila de cenários (`comum.py`)

```python
def proximo(engine):
    est = os.environ.get("SDD_STUB_ESTADO") or ""
    fila = [c for c in (os.environ.get("SDD_STUB_" + engine.upper()) or "").split(",") if c]
    if not est or not fila:
        if est:
            open(os.path.join(est, "sentinela"), "a").write(engine + "\n")
        sys.exit(99)                                   # engine fora do teste: nunca responde
    arq = os.path.join(est, engine + ".n")
    n = int(open(arq).read()) + 1 if os.path.exists(arq) else 1
    open(arq, "w").write(str(n))
    return n, cenario(engine, fila[min(n, len(fila)) - 1])   # a última entrada se repete
```

### Pattern 2: Wrapper gerado pelo gate (`<tmp>/bin/<engine>`)

```sh
#!/bin/sh
exec python3 -B "/caminho/do/pacote/sdd/review/stubs/claude.py" "$@"
```

### Pattern 3: Asserção de campo no gate

```python
def campo(rotulo, meta, chave, esperado):
    v = meta.get(chave)
    if v == esperado:
        ok(rotulo, v)
    else:
        falha(rotulo, "%s = %r (esperado %r)" % (chave, v, esperado))
```

### Pattern 4: Custo com tentativa incerta (`custo()`)

```python
base = custo_sem_incerteza(reg)                    # US$ x | ≈US$ x | assinatura | $? | n/d
if reg.get("custo_incerto") and base not in ("$?", "n/d"):
    return base + " + $?"
return "$?" if reg.get("custo_incerto") else base
```

---

## Data Flow

```text
1. gate: pré-voo (stubs, registry, PATH, servidor) ─✗→ exit 3
   │
   ▼
2. repo descartável com diff de 1 arquivo; isolamento de rede e chave
   │
   ▼
3. por cenário: SDD_STUB_<ENGINE>=fila; SDD_STUB_ESTADO=<tmp>/estado-N
   adversarial-review.sh --reviewer X --auditor Y (adapters reais)
   │      └─ adapter → CLI falsa / urllib → stub da engine → formato da engine
   ▼
4. META.txt + *.verdicts.jsonl + estado (chamadas, sentinela, corpo HTTP)
   │
   ▼
5. asserções contra cenarios.tsv → ✅/❌; todas rodam
   │
   ▼
6. exit 0 (todas ✅) | 2 (alguma ❌); RESULTADO + →

eval-agree: pasta → META + auditor.verdicts.jsonl → agrupar por auditor → tabela → exit 0 | 2 | 64
```

---

## Integration Points

| External System | Integration Type | Authentication | Direction | Failure / Retry |
|---|---|---|---|---|
| Nenhum (o gate e o eval-agree não saem da máquina) | N/A | chave falsa gerada | N/A | proxy morto: qualquer tentativa de rede falha e vira ❌ |

---

## Testing Strategy

| Test Type | Scope / Requirement | Files | Tools | Pass Signal |
|---|---|---|---|---|
| Integration | gate ponta a ponta (AT-001–AT-013) | `tests/test_revisao_gate.py` | unittest + subprocess | exit 0; 5 sabotagens ⇒ exit 2 com o nome da asserção |
| Unit | eval-agree (AT-014–AT-017) | `tests/test_eval_agree.py` | unittest | números exatos; exits 2/64 |
| Unit | achados #15–#18 (AT-018–AT-023) | `tests/test_revisao.py`, `tests/test_revisao_adapters.py` | unittest + `stub.sh` | vermelhos na v2.3.0, verdes no fim |
| Contract | CI, docs, init (AT-025–AT-027) | `test_release_workflow.py`, `test_docs.py`, `test_sdd_open.py`, `test_bash32.py` | unittest | verde |
| E2E / Verify Gate | suíte inteira no piso | `tests/` | `cmd` do DEFINE | exit 0 |

---

## Error Handling

| Error Type | Detection | Handling Strategy | Retry? | Observability |
|---|---|---|---|---|
| stub ausente / CLI real à frente | pré-voo | exit 3 nomeando o item; nenhuma chamada | No | `🛑` + `RESULTADO: GATE QUEBRADO` |
| servidor do openrouter não sobe | porta não escrita em 5 s | exit 3 | No | idem |
| engine fora da fila chamada | sentinela | asserção de isolamento ❌ | No | nome da engine na linha `→` |
| asserção que falha | comparação | segue as demais; exit 2 | No | `❌ N.` + `→ chave = valor (esperado …)` |
| `adversarial-review.sh` que trava | `subprocess` com teto de 60 s por execução | ❌ das asserções daquela execução, segue | No | linha `→` com o tempo |
| gate lento | tempo total medido | a última linha antes do `RESULTADO:` diz `N asserções, M falhas em S s`; o teste da suíte confere ≤ 120 s só no piso local (evidência), não na CI | No | linha de total |
| eval-agree: pasta sem revisões | contagem | exit 2 | No | `RESULTADO: SEM DADOS` |

---

## Configuration

| Config Key | Type | Source / Default | Sensitive? | Description |
|---|---|---|---|---|
| `review.output_dir` | path | `sdd/config.yaml` / `sdd/reports/reviews` | No | pasta padrão do eval-agree |
| `SDD_STUB_<ENGINE>` | env | definido pelo gate | No | fila de cenários |
| `SDD_STUB_ESTADO` | env | definido pelo gate | No | contador, sentinela, registro |
| `OPENROUTER_API_KEY` | env | gerada pelo gate (`gate-<pid>-falsa`) | No (falsa) | nunca em arquivo |

---

## Security Considerations

- Nenhuma chave real: o gate sobrescreve `OPENROUTER_API_KEY` com valor falso gerado e confere que ele não aparece nas pastas de revisão.
- Nenhuma rede: proxies mortos + `no_proxy` só para `127.0.0.1`; a sentinela pega CLI real chamada por engano; o pré-voo recusa `PATH` com CLI real à frente.
- Os stubs não executam o que recebem: leem o prompt e devolvem texto fixo.

---

## Observability

- Uma linha por asserção (`✅ N. rótulo` / `❌ N. rótulo` + `→ …`), `-v` com o valor lido; total `N asserções, M falhas` antes do `RESULTADO:`.
- eval-agree: quantas pastas leu, quantas ficaram fora e por quê.

---

## Requirements Traceability

| Requirement | Decision | Files |
|---|---|---|
| AT-001–AT-013 | 1, 2 | 1–10, 20 |
| AT-014–AT-017 | 3 | 11, 14–19, 21 |
| AT-018–AT-023 | 4 | 12, 13, 22, 23 |
| AT-024 | 4, 6 | 22 (suíte da F10 inteira) |
| AT-025 | 5 | 24–26 |
| AT-026 | 5 | 27–32 |
| AT-027 | 5 | 33, 34 |

---

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| `urllib` ignora `no_proxy` para 127.0.0.1 (A-002, medida válida) | o gate sobrescreve `no_proxy`/`NO_PROXY`; teste: com os proxies do gate, uma requisição a um host externo falha com `ConnectionRefusedError` vinda de 127.0.0.1:9 (não `gaierror`) |
| texto real de falha das CLIs diverge do sintético (LOW 2); cota real do gemini junto com `429` faz 3 tentativas antes de trocar | linhas de falha marcadas `sintético` em `cenarios.tsv`; o caminho "cota com 429" fica registrado como não exercitado (docs) |
| o gate passa do teto do macOS | medir no build; o teto sobe para 30 |
| formato de CLI muda e o stub fica velho | `cenarios.tsv` documentado como o lugar do formato; a revisão real continua sendo a prova final |

---

## Advisor Ledger

Revisão de contexto fresco do DESIGN v1.0 (`sdd/reviews/REVISAO_DESIGN_F11_GATE_20261101.md`, modo `contrato`, 6 logs `AVAL-DESIGN-*.log`): NEEDS_WORK, 2 HIGH, 3 MEDIUM, 7 LOW.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| H1 | pré-voo no shell do gate; `bash -c` do adapter executa `BASH_ENV` e funções exportadas ⇒ CLI real chamada | HIGH | APLICADA (Decision 2: ambiente dos filhos sem `BASH_ENV`/`ENV`/`BASH_FUNC_*`, pré-voo num `/bin/bash -c` filho com o mesmo ambiente, contagem de chamadas; DEFINE AT-009, AT-011) | `AVAL-DESIGN-02-bashenv-bypass.log` |
| H2 | servidor do openrouter não vê fila/estado por cenário; "sai 99" não existe em HTTP | HIGH | APLICADA (Decision 1: um servidor por cenário, HTTP 599 `sentinela`) | `AVAL-DESIGN-06-fila-openrouter.log` |
| M1 | campos de custo/modelo de codex e gemini não discriminam a extração | MEDIUM | APLICADA (Decision 2: só campos que discriminam contam; teste de extração nula por engine; DEFINE AT-002, Success Criteria) | `AVAL-DESIGN-03-meta-discriminacao.log` |
| M2 | cenário 67 não protege a exclusão dentro de `papel()` | MEDIUM | APLICADA (cenário de fallback para a identidade do auditor; DEFINE AT-005) | `AVAL-DESIGN-05-sabotagem-exclusao.log` |
| M3 | `≈US$` fixo no TSV quebra com preço novo e não vê a tarifa com poucos tokens | MEDIUM | APLICADA (esperado calculado do `precos.tsv` resolvido; tokens 1234567/234567) | `AVAL-DESIGN-04-openrouter-precos.log` |
| L1 | sonda `example.invalid` não discrimina; A-002 medida | LOW | APLICADA (Risks; DEFINE A-002 = yes) | `AVAL-DESIGN-01-urllib-proxy.log` |
| L2 | textos de falha não medidos; cota do gemini com 429 | LOW | APLICADA em parte: marcados `sintético`; o caminho cota+429 fica registrado como não exercitado — REBATIDA_ESCOPO para medi-los (exigiria provocar falha real paga) | — |
| L3 | asserir o Bearer recebido | LOW | APLICADA (Decision 2; DEFINE AT-010) | `AVAL-DESIGN-04-openrouter-precos.log` |
| L4 | ` via <provedor>` parte o auditor no eval-agree | LOW | APLICADA (Decision 3; DEFINE AT-014) | — |
| L5 | AT-017 sem verificação | LOW | APLICADA (DEFINE AT-017) | — |
| L6 | redação do codex/gemini no AT-002 | LOW | APLICADA (DEFINE AT-002) | — |
| L7 | estouro do tempo total | LOW | APLICADA (Error Handling: teto 60 s por execução, total na saída) | — |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-01 | SDD Design by RDD | Initial version |
| 1.1 | 2026-11-01 | SDD Design by RDD | revisão de contexto fresco: 2 HIGH, 3 MEDIUM e 7 LOW (Advisor Ledger) |

---

## Next Step

Execute o **SDD Build by RDD**.
