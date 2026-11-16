# DESIGN: F23 Economia mensurável — fatia B1 (custo por fase e por feature)

> Technical design for implementing F23 Economia mensurável, fatia B1

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F23_ECONOMIA_MENSURAVEL |
| **Date** | 2026-11-15 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_F23_ECONOMIA_MENSURAVEL.md](./DEFINE_F23_ECONOMIA_MENSURAVEL.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
 skill de fase (brainstorm … release)
        │  início / fim
        ▼
 sdd/bin/marca-fase.sh ──► sdd/traces/<F>.jsonl ◄── sdd/bin/verify-gate.sh (já grava as voltas do gate)
                                  │  {"src":"fase","evento":"inicio|fim","fase":…,"ts":…}
                                  ▼
 sdd/bin/custo-feature.sh <F> ─────────────────────────────────────────────┐
   │ 1. lê as marcas e as voltas do gate em sdd/traces/<F>.jsonl          │
   │ 2. roda cada leitor sdd/bin/adapters/sessao-*.py --raiz <raiz>       │
   │        sessao-claude.py → ~/.claude/projects/<raiz-com-hífens>/*.jsonl (+ subagents/)
   │        sessao-codex.py  → ~/.codex/sessions/**/rollout-*.jsonl (session_meta.cwd == raiz)
   │      saída: JSONL só com números {t, tipo: msg|turno|ilegivel, modelo, entrada, saida, cache_lido, cache_criado}
   │ 3. lê os META.txt da revisão desta feature (review.output_dir)       │
   │ 4. preços: sdd/review/precos.tsv (entrada/saída) + precos-cache.tsv  │
   │    cobrança: sdd/review/registry.tsv (assinatura → pago 0)           │
   │ 5. soma em Decimal por fase, "sem fase", "revisão", total            │
   └──► sdd/reports/CUSTO_<F>.md  (ao lado do BUILD_REPORT)              │
                                                                          │
 custo-feature.sh --linha-de-base <mapa.tsv>  (feature · raiz · ledger) ─┘
   └──► uma linha por feature: sessões (nominal), revisão, rodadas de revisão, achados com dano
```

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `marca-fase.sh` | grava a marca de início ou fim de uma fase no trace da feature | bash 3.2 + `date -u` |
| `sessao-claude.py` | lê as sessões do Claude Code de uma pasta de projeto e devolve só números | Python 3.9 stdlib |
| `sessao-codex.py` | lê as sessões do Codex cuja pasta de trabalho é a raiz e devolve só números | Python 3.9 stdlib |
| `custo-feature.sh` | soma por fase e por feature, grava o relatório; modo de linha de base | bash 3.2 + Python 3.9 embutido (molde do `eval-revisores.sh`) |
| `precos-cache.tsv` | preço de cache lido e criado por (engine, modelo) | TSV de 6 colunas, só cabeçalho no pacote |
| Skills de fase | chamam `marca-fase.sh` no início e no fim; a release roda o contador | Markdown |

---

## Key Decisions

### Decision 1: As marcas vão no trace que o verify-gate já grava

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** O contador precisa das marcas de fase e das voltas do Verify Gate (o SHOULD do DEFINE). O `verify-gate.sh` já grava uma linha JSONL por execução em `${SDD_TRACE_DIR:-sdd/traces}/<F>.jsonl`, com `SDD_TRACE=off` para desligar.
**Choice:** O `marca-fase.sh` acrescenta ao mesmo arquivo uma linha `{"ts","feature","src":"fase","evento","fase"}`, respeita `SDD_TRACE_DIR` e `SDD_TRACE=off`, e nunca reescreve o arquivo.
**Rationale:** Um arquivo por feature com tudo o que o contador lê; a chave de desligar já existe e é conhecida; as linhas do verify-gate (`src` `verify-gate`/`release`) não mudam.
**Alternatives Rejected:** 1. Arquivo próprio `sdd/reports/custo/MARCAS_<F>.tsv` — rejeitada porque cria um 2º lugar para o mesmo tipo de dado. 2. Marca na conversa, lida do registro do agente — rejeitada porque só o Claude Code registra a skill chamada (decisão 4 do brainstorm).
**Consequences:** No pacote do Open, `sdd/traces/` está no `.gitignore`: o contador roda **antes** de a worktree sair (a release roda o contador; Decision 7). Ganha-se um formato só.

### Decision 2: Leitores de sessão em Python, em `sdd/bin/adapters/sessao-<agente>.py`

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** O DEFINE pede um adaptador por agente que devolva só números. Os adaptadores de `sdd/bin/adapters/*.sh` são das engines da revisão, com contrato próprio (`adapter_invocar`, `adapter_extrair`) lido pelo `registry.tsv`.
**Choice:** Um programa Python por agente, `sdd/bin/adapters/sessao-claude.py` e `sessao-codex.py`, com o contrato: `--raiz <pasta>` (obrigatório), `--dir <pasta de sessões>` (opcional, para testes e para `CLAUDE_CONFIG_DIR`/`CODEX_HOME`), saída JSONL em stdout, exit `0` LIDO, `2` SEM REGISTRO, `64` uso. O contador descobre os leitores por `sessao-*.py`: agente novo é um arquivo novo.
**Rationale:** Python lê JSONL com segurança e roda igual no Windows; ficar em `adapters/` mantém o `doctor` e o `upgrade` cobrindo os arquivos (`bin/sdd-open.sh:996` percorre `sdd/bin/adapters/*`) sem mexer no instalador; a extensão `.py` não colide com os `.sh` do registry.
**Alternatives Rejected:** 1. Pasta nova `sdd/bin/sessoes/` — rejeitada porque o `doctor` não a percorre e exigiria mexer no `bin/sdd-open.sh`. 2. Funções dentro do `custo-feature.sh` — rejeitada porque o DEFINE pede o adaptador testável sozinho (AT-002) e agente novo mexeria no contador.
**Consequences:** Os nomes do DEFINE (`sessao-claude.sh`) viram `.py` (Revision History do DEFINE). Os leitores seguem a LM-015: `reconfigure` de stdout e stderr no início.

### Decision 3: Cada leitor normaliza os tokens no mesmo significado

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** O Claude Code grava uma linha por bloco de conteúdo e repete o `usage` da mesma mensagem (na sessão da F22: 1.064 linhas com `usage` para 472 mensagens, até 13 repetições). No Claude, `input_tokens` não inclui o cache; no Codex, `input_tokens` inclui `cached_input_tokens`, e o `token_count` traz o total acumulado, que pode se repetir.
**Choice:** Saída única por mensagem: `entrada` (sem cache), `saida`, `cache_lido`, `cache_criado`. Claude: agrupa por `message.id` (sem id, `requestId`), maior valor por campo, horário da 1ª linha; subagentes de `<sessão>/subagents/*.jsonl` entram como mensagens, nunca como turnos. Codex: diferença entre `total_token_usage` consecutivos (diferença zero é descartada); `entrada = input − cached`, `cache_lido = cached`, `cache_criado = cache_write_input_tokens`; modelo do `turn_context` mais recente.
**Rationale:** A repetição do Claude infla o custo várias vezes se somada linha a linha; a diferença de totais é imune a evento repetido.
**Alternatives Rejected:** 1. Somar `last_token_usage` do Codex — rejeitada porque o evento pode se repetir com o mesmo valor. 2. Somar todas as linhas do Claude — rejeitada (infla).
**Consequences:** O teste tem fixtures com a repetição e com o evento duplicado.

### Decision 4: Turno e tempo ativo

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** O DEFINE fixou o tempo ativo como a soma, por turno, do intervalo entre a mensagem que dispara o turno e o último registro do agente nele.
**Choice:** Os leitores emitem `{"tipo":"turno","t":…}` no início de cada turno: no Claude, a linha `type: user` da sessão principal cujo conteúdo tem texto (não só `tool_result`) e sem `isMeta`; no Codex, o evento `task_started`. O contador fecha um turno no último `msg` antes do próximo `turno`, e recorta por janela de fase (o trecho de um turno dentro de cada fase conta para ela).
**Rationale:** Usa só horário, sem texto. A pausa humana entre turnos não conta.
**Alternatives Rejected:** 1. Relógio corrido entre as marcas — rejeitada no brainstorm (sessões param por dias).
**Consequences:** Uma resposta longa sem nova mensagem do agente conta só até o último registro dele.

### Decision 5: Janela da feature, fase e "sem fase"

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** Num projeto sem worktree por frente, as sessões da pasta trazem outras features.
**Choice:** Com marcas, a feature vai da 1ª à última marca dela; se a última fase ficou aberta, a janela vai até o fim da última sessão (R2 da revisão do DESIGN: a medição parcial durante o build conta o build até agora). Cada mensagem dentro de um par início/fim vai para a fase. Dentro da janela e fora de pares, vai para `sem fase`. Fora da janela, fica de fora. Uma fase aberta sem `fim` fecha na marca seguinte ou no fim da última sessão, com o aviso `fase sem fim: <fase>`. **Sem nenhuma marca** fora do modo de linha de base, a linha `sem fase` sai `n/d` com o aviso `nenhuma marca de fase: as sessões não foram atribuídas` (R6): um zero ali pareceria economia. No modo de linha de base, sem marcas, a sessão inteira da raiz conta.
**Rationale:** Não atribui a esta feature o custo de outra; o aviso deixa visível a marca esquecida.
**Alternatives Rejected:** 1. Todas as sessões da raiz sempre — rejeitada (mistura features no checkout principal).
**Consequences:** A marca de início do brainstorm só existe quando o nome da feature está decidido; a conversa antes dela fica fora da janela.

### Decision 6: Preço de cache num arquivo vizinho; a cobrança vem do registry

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** `precos.tsv` tem 6 colunas, e três leitores a conferem com exatamente 6 (`adversarial-review-gate.sh:152` usa `tsv(…, 6)`). O AT-010 exige que ela continue aceita.
**Choice:** Arquivo novo `sdd/review/precos-cache.tsv` com 6 colunas: `engine · modelo · usd_mtok_cache_lido · usd_mtok_cache_criado · fonte · conferido_em`. Entrada e saída continuam da `precos.tsv`. O pacote leva o arquivo só com o cabeçalho, sem nenhum preço de modelo (vendor-agnóstico). A pasta segue a regra do `adversarial-review.sh`: a do projeto, se existir; senão, a do pacote. `--precos <dir>` passa por cima, para medir com uma tabela fora do repositório. Pago: o registry diz a cobrança do agente (`claude` e `codex`: assinatura → pago 0; `pay-per-token` → pago = nominal; `desconhecida` → n/d).
**Rationale:** Não toca nenhum leitor existente; o mesmo par (engine, modelo) serve às duas tabelas.
**Alternatives Rejected:** 1. Ampliar a `precos.tsv` para 8 colunas — rejeitada porque quebra 3 leitores e as tabelas dos projetos.
**Consequences:** Sem preço na tabela do projeto, o nominal das sessões sai n/d. É honesto, e o relatório diz qual (engine, modelo) faltou.

### Decision 7: Relatório em `sdd/reports/CUSTO_<F>.md`, gravado pela release

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** O custo final inclui a release, e o trace do Open some com a worktree.
**Choice:** A `sdd-release`, no encerramento, grava a marca `fim release` e roda `custo-feature.sh <F>`, que grava `sdd/reports/CUSTO_<F>.md` (`--saida -` só imprime). A `sdd-build` cita o contador como medição parcial opcional.
**Rationale:** É o último momento com tudo no disco.
**Alternatives Rejected:** 1. Dentro do BUILD_REPORT — rejeitada no DEFINE (`report-lint.py` e o molde mudariam).
**Consequences:** Feature que para antes da release não tem o relatório final, mas pode rodar o contador à mão.

### Decision 8: Custo da revisão pelos META, sem conta em dobro

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** A revisão já tem custo nos META.txt; as chamadas rodam com `--no-session-persistence` (claude) e com a pasta de trabalho numa pasta temporária vazia (`adversarial-review.sh:593`), então o registro de sessão do projeto não as tem.
**Choice:** Uma pasta `EXTERNAL_REVIEW_*` é da feature quando o `docs_sdd` do META cita `DEFINE_<F>.md` ou o ledger `LEDGER_REVISAO_<F>.md` cita a pasta. Nominal: soma dos `*_custo` numéricos dos papéis (`reviewer`, `revisor2`, `auditor`, `desempate`), pela mesma regra do `custo_de` do `eval-revisores.sh` (`≈` estimado; `US$ n + $?` incerto; `assinatura`/`$?`/`n/d` sem custo). Pago: os da engine efetiva com cobrança `pay-per-token`. O `sessao-codex.py` só lê sessão com `cwd` igual à raiz.
**Rationale:** Uma fonte para a revisão; o filtro de pasta de trabalho barra a sessão da revisão.
**Alternatives Rejected:** 1. Chamar o `eval-revisores.sh` e ler a tabela impressa — rejeitada (saída humana, frágil). 2. Filtro por `branch` do META — rejeitada (a mesma branch revisa DESIGN e código de mais de uma feature às vezes).
**Consequences:** O teste confere que o nominal da revisão bate com o `eval-revisores.sh` sobre a mesma fixture.

### Decision 9: Linha de base por mapa, sessões separadas da revisão

| **Status** | Accepted | · | **Date** | 2026-11-15 |

**Context:** Das frentes F4 a F22 sobraram os registros de sessão (protegidos) e os ledgers (branch de documentos), mas quase nenhum META (o `sdd/reports/reviews/` é ignorado pelo git e sumiu com as worktrees); a revisão com claude não deixa sessão.
**Choice:** `custo-feature.sh --linha-de-base <mapa.tsv>`; o mapa tem 3 colunas: `feature · raiz · ledger` (`-` sem ledger). A saída tem uma linha por feature: `Sessões (nominal US$)` · `Revisão (nominal US$ ou n/d)` · `Rodadas de revisão` (rodadas distintas do ledger) · `Achados com dano` (`dano` = `sim`). Comparações da seção 6 usam a coluna `Sessões`, que existe dos dois lados.
**Rationale:** Compara igual com igual; o que falta aparece como n/d.
**Alternatives Rejected:** 1. Estimar a revisão das frentes antigas pela prosa dos BUILD_REPORTs — rejeitada (número inventado).
**Consequences:** O mapa das F4–F22 é dado do mantenedor, fora do pacote (ele traz caminhos `/Users/`).

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `sdd/bin/marca-fase.sh` | Create | grava a marca de início ou fim no trace (AT-001) | (general) | None |
| 2 | `sdd/bin/adapters/sessao-claude.py` | Create | leitor de sessões do Claude Code (AT-002, AT-007) | (general) | None |
| 3 | `sdd/bin/adapters/sessao-codex.py` | Create | leitor de sessões do Codex (AT-002, AT-006) | (general) | None |
| 4 | `sdd/review/precos-cache.tsv` | Create | preço de cache, só cabeçalho (AT-005) | (general) | None |
| 5 | `sdd/bin/custo-feature.sh` | Create | contador e linha de base (AT-003 a AT-008) | (general) | 1, 2, 3, 4 |
| 6 | `sdd/templates/fragments/MARCA_FASE.md` | Create | dono único do texto da marca (o porquê e o comando) | (general) | 1 |
| 7 | `.agents/skills/sdd-brainstorm/SKILL.md` | Modify | marca início e fim; versão 2.5.0 (AT-009) | (general) | 6 |
| 8 | `.agents/skills/sdd-define/SKILL.md` | Modify | marca início e fim; versão 2.8.0 (AT-009) | (general) | 6 |
| 9 | `.agents/skills/sdd-ux-review/SKILL.md` | Modify | marca início e fim; versão 2.7.0 (AT-009) | (general) | 6 |
| 10 | `.agents/skills/sdd-design/SKILL.md` | Modify | marca início e fim; versão 2.8.0 (AT-009) | (general) | 6 |
| 11 | `.agents/skills/sdd-build/SKILL.md` | Modify | marca início e fim; contador como medição parcial; versão 2.11.0 (AT-009) | (general) | 5, 6 |
| 12 | `.agents/skills/sdd-release/SKILL.md` | Modify | marca início e fim e roda o contador no encerramento, sem passar de 500 linhas; versão 2.14.0 (AT-009) | (general) | 5, 6 |
| 13 | `sdd/fixtures/custo/` | Create | sessões sintéticas (Claude com repetição e subagente; Codex com evento repetido e sessão de outra pasta), trace, META, ledger, preços (AT-001 a AT-008) | (general) | None |
| 14 | `tests/test_f23_custo.py` | Create | testes dos AT-001 a AT-010 | (general) | 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13 |
| 15 | `docs/adversarial-review.md` | Modify | seção do `custo-feature.sh` (EN) | (general) | 5 |
| 16 | `docs/pt-BR/adversarial-review.md` | Modify | seção do `custo-feature.sh` (PT) | (general) | 5 |
| 17 | `docs/cli-conventions.md` | Modify | exits do `marca-fase.sh`, do `custo-feature.sh` e dos leitores | (general) | 1, 2, 3, 5 |
| 18 | `MANIFEST.txt` | Modify | os arquivos novos do pacote | (general) | 1, 2, 3, 4, 5, 6, 13, 14 |

**Total Files:** 18

---

## Landmines aplicáveis

Varredura rodada em 2026-11-15 sobre: jsonl, Decimal, precos, MANIFEST, Windows, gerar-starter, starter, SKILL.md, versão, trace, META, ledger, UTF-8, fixture, exit 0, CRLF, python3, git archive, sessão, review, skill, tsv, heredoc, bash. Entradas abertas inteiras.

| LM | Veredito | Como |
|---|---|---|
| LM-001 (gate que confere fiação) | ✔ tratado | os testes EXECUTAM os scripts sobre fixtures dos dois lados (caso que soma e caso n/d, marca válida e recusada); AT-009 (texto) é o único teste de texto e é complementado pelos AT que rodam o script |
| LM-002 (asserção sem baseline vermelho) | ✔ tratado | o build roda o `test_f23_custo.py` contra a árvore antes dos scripts (vermelho: arquivos ausentes) e um mutante (somar as linhas repetidas do Claude) derruba a asserção do AT-003 |
| LM-003 (review do vazio) | ✔ tratado | commit antes de cada revisão; `git diff --stat` conferido contra a lista |
| LM-006 (só roda com `.git`) | ✔ tratado | `custo-feature.sh` e `marca-fase.sh` caem para a pasta atual sem `.git` (como o `verify-gate.sh`); o gate roda de `git archive` |
| LM-012 (11 dígitos no pacote) | ✔ tratado | fixtures usam ids curtos inventados; nenhum id de run ou hash inteiro |
| LM-014 (`text=True` no Windows) | ✔ tratado | o teste usa o `Sandbox` de `tests/apoio.py` (bytes → UTF-8) |
| LM-015 (saída do Python no Windows) | ✔ tratado | os 2 leitores e o Python embutido do contador fazem `reconfigure(encoding="utf-8", errors="replace", newline="\n")` no início |
| LM-016 (teto por sinal) | N.A. | nenhum teto de tempo |
| LM-017 (fallback silencioso) | ✔ tratado | o contador chama os leitores pelo caminho resolvido sem `dirname` (molde `_sdd_0` do `eval-revisores.sh`); um leitor que falha vira `ilegivel` com aviso, nunca some calado |
| LM-029 (`bash` no System32) | ✔ tratado | o Python embutido chama os leitores com `sys.executable`, não `bash`; os testes usam a constante `BASH` |
| LM-030 (executor mascara encoding) | ✔ tratado | testes pelo `Sandbox`, sem `PYTHONIOENCODING` no ambiente |
| LM-034 (PATH restrito no Windows) | N.A. | nenhum teste tira ferramenta do PATH |
| LM-004 (migration) | N.A. | sem banco |

---

## Contrato de aceite

N.A. (1 camada: scripts do método e o texto das skills; sem UI, banco ou serviço).

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| (general) | 1 a 18 | o repositório não tem agentes especialistas; a fase Build faz direto |

**Agent Discovery:**
- Scanned: `.claude/agents/`, `.codex/agents/` (inexistentes no Open)

---

## Code Patterns

Sem `sdd/patterns/` com camada para scripts; candidato a pattern: `sdd/bin` (script bash com Python embutido).

### Pattern 1: Cabeçalho de script com Python embutido (de `eval-revisores.sh`)

```bash
set -u
_sdd_0="${0//\\//}"
if [ "${_sdd_0%/*}" = "${_sdd_0}" ]; then _sdd_bin=.; else _sdd_bin="${_sdd_0%/*}"; fi
if [ -f "${_sdd_bin}/lib/python.sh" ]; then . "${_sdd_bin}/lib/python.sh"
else sdd_python_pronto() { command -v python3 >/dev/null 2>&1; }; sdd_python_exigir() { :; }
  export PYTHONIOENCODING="${PYTHONIOENCODING:-utf-8}"; fi
SDD_CUSTO_BIN="$(cd "${_sdd_bin}" && { pwd -W 2>/dev/null || pwd; })"; export SDD_CUSTO_BIN
exec python3 -B - "$@" <<'PY'
import sys as _sdd_sys
for _sdd_c in (_sdd_sys.stdout, _sdd_sys.stderr):
    try:
        _sdd_c.reconfigure(encoding="utf-8", errors="replace", newline="\n")
    except (AttributeError, ValueError):
        pass
PY
```

### Pattern 2: Marca (marca-fase.sh)

```bash
case "${evento}" in inicio|fim) ;; *) uso "evento é inicio ou fim" ;; esac
# grep testa linha a linha: um valor com quebra de linha passaria se UMA das linhas casasse (R1 da revisão do
# DESIGN). Por isso a contagem de quebras (wc -l) tem de ser 0, além do padrão.
printf '%s' "${fase}" | LC_ALL=C grep -Eq '^[a-z][a-z0-9-]{0,39}$' \
  && [ "$(printf '%s' "${fase}" | wc -l | tr -d ' ')" = "0" ] || uso "fase inválida (só a-z, 0-9 e -)"
printf '%s' "${feature}" | LC_ALL=C grep -Eq '^[A-Za-z0-9_.-]{1,80}$' \
  && [ "$(printf '%s' "${feature}" | wc -l | tr -d ' ')" = "0" ] || uso "feature inválida (sem espaço, tabulação ou quebra de linha)"
[ "${SDD_TRACE:-on}" = "off" ] && { echo "RESULTADO: DESLIGADO"; echo "→ SDD_TRACE=off: nenhuma marca gravada."; exit 0; }
printf '{"ts":"%s","feature":"%s","src":"fase","evento":"%s","fase":"%s"}\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${feature}" "${evento}" "${fase}" >> "${dir}/${feature}.jsonl"
```

Com o padrão e a contagem de quebras, o valor não tem aspas, barra invertida, espaço nem controle: a linha JSON não precisa de escape. O teste do AT-001 usa quebra de linha no meio e no fim do valor.

### Pattern 3: Leitor do Claude (núcleo)

```python
msgs = {}
for linha in arquivo:
    try:
        d = json.loads(linha)
    except ValueError:
        ilegiveis += 1; continue
    m = d.get("message") or {}
    if d.get("type") == "assistant" and isinstance(m.get("usage"), dict):
        chave = m.get("id") or d.get("requestId") or ("linha", n)
        u = m["usage"]
        atual = msgs.setdefault(chave, {"t": d.get("timestamp"), "modelo": m.get("model"), "entrada": 0, "saida": 0,
                                        "cache_lido": 0, "cache_criado": 0})
        for campo, fonte in (("entrada", "input_tokens"), ("saida", "output_tokens"),
                             ("cache_lido", "cache_read_input_tokens"), ("cache_criado", "cache_creation_input_tokens")):
            v = u.get(fonte)
            if isinstance(v, int) and v > atual[campo]:
                atual[campo] = v
```

O nome do modelo só sai se casar com `^[A-Za-z0-9._:/@-]{1,80}$`; senão sai `?` (S17).

---

## Data Flow

```text
<F> é sempre o feature_id inteiro, o mesmo de DEFINE_<F>.md (R3 da revisão do DESIGN): o verify-gate.sh já grava o
trace com esse nome (basename do DEFINE sem o prefixo DEFINE_), e a revisão casa pelo nome exato.

1. skill → marca-fase.sh inicio define F23_ECONOMIA_MENSURAVEL → sdd/traces/F23_ECONOMIA_MENSURAVEL.jsonl += {"src":"fase",…}
2. … sessões do agente acontecem (registros locais) …
3. sdd-release (encerramento) → marca-fase.sh fim release F23_ECONOMIA_MENSURAVEL → custo-feature.sh F23_ECONOMIA_MENSURAVEL
4. custo-feature.sh: traces → janelas; sessao-*.py → mensagens e turnos; META → revisão; preços → US$
5. → sdd/reports/CUSTO_F23_ECONOMIA_MENSURAVEL.md
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Registro local do Claude Code (`~/.claude/projects/`, ou `CLAUDE_CONFIG_DIR`) | leitura de arquivo | nenhuma |
| Registro local do Codex (`~/.codex/sessions/`, ou `CODEX_HOME`) | leitura de arquivo | nenhuma |

---

## Testing Strategy

| Tipo | Escopo | Ferramenta | Meta |
|---|---|---|---|
| Unit (script) | `marca-fase.sh`: linha gravada, append, recusa de controle/tab (exit 64, nada gravado), `SDD_TRACE=off`, sem `.git` | unittest + `Sandbox` | AT-001 |
| Unit (script) | `sessao-claude.py`: repetição por `message.id`, subagente, linha quebrada → `ilegivel`, texto/caminho/segredo com 0 ocorrência, modelo com `|` → `?` | unittest | AT-002, AT-004 |
| Unit (script) | `sessao-codex.py`: diferença de totais, evento repetido, sessão de outra pasta ignorada, `cached` fora da entrada | unittest | AT-002, AT-006 |
| Integração | `custo-feature.sh` sobre a fixture: cada célula da tabela afirmada (fases, sem fase, revisão, total, n/d, cache sem preço → n/d, fase sem fim → aviso) | unittest | AT-003, AT-004, AT-005, AT-007 |
| Integração | nominal da revisão = soma do `eval-revisores.sh` sobre a mesma pasta de META | unittest | AT-006 |
| Integração | `--linha-de-base` com mapa de 2 features | unittest | AT-008 |
| Texto | as 6 skills citam `marca-fase.sh inicio` e `… fim`; a release cita `custo-feature.sh`; nenhuma passa de 500 linhas; `gerar-starter.py` gera sem erro | unittest | AT-009 |
| Regressão | suíte inteira (`test_eval_revisores.py`, `test_revisao_gate.py`, `test_check_versions.py`, `test_gerar_starter.py`, `test_bash32.py`) | unittest | AT-010 |
| Mutante | somar as linhas repetidas do Claude em vez de agrupar → o teste do AT-003 fica vermelho | à mão, no BUILD_REPORT | LM-002 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Sessão ilegível (JSON quebrado, arquivo sumido) | leitor emite `{"tipo":"ilegivel"}`; a célula vira n/d; o relatório lista a contagem | No |
| Leitor sai ≠ 0 | o agente vira n/d com o motivo; os outros seguem | No |
| Modelo sem preço (entrada/saída ou cache) | aquela parte vira n/d; total `US$ x + n/d`; o relatório lista os pares (engine, modelo) sem preço | No |
| Fase sem `fim` | fecha na marca seguinte ou no fim da última sessão; aviso `fase sem fim` | No |
| Nenhuma marca e nenhuma sessão | `RESULTADO: SEM DADOS`, exit 2 | No |
| Argumento inválido | `RESULTADO: PAROU`, exit 64 | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `SDD_TRACE` | env | `on` | `off` desliga também as marcas |
| `SDD_TRACE_DIR` | env | `sdd/traces` | pasta do trace |
| `CLAUDE_CONFIG_DIR` / `CODEX_HOME` | env | `~/.claude` / `~/.codex` | onde os leitores procuram |
| `review.output_dir` | `sdd/config.yaml` | `sdd/reports/reviews` | pastas da revisão |

---

## Segurança

1. **Onde mora cada segredo:** N.A. — os scripts não usam segredo nem rede. O registro de sessão lido pode conter segredo colado na conversa: nada do texto sai (item 5).
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco. O relatório `CUSTO_<F>.md` e o trace são lidos por quem lê o repositório (no Open, público).
3. **Credencial de cada agente ou integração:** N.A. — os leitores só leem arquivos locais do usuário; nada é enviado.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** S17 (linha forjada) → o `marca-fase.sh` só aceita fase `^[a-z][a-z0-9-]{0,39}$` e feature `^[A-Za-z0-9_.-]{1,80}$` (exit 64, nada gravado), e o nome de modelo vindo do registro sai `?` fora de `^[A-Za-z0-9._:/@-]{1,80}$`; os campos do relatório são números ou esses nomes, então nenhuma célula carrega `|` ou quebra de linha. S10 (já atendido): os leitores devolvem só os campos numéricos, horários e o modelo; o texto das mensagens nunca é lido para fora do processo.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | o próprio relatório lista `fora da conta` (sessões ilegíveis, pares sem preço, fase sem fim) |
| Metrics | as colunas do relatório |
| Tracing | `sdd/traces/<F>.jsonl` |

---

## Advisor Ledger

Rodada 1 (2026-11-15, `EXTERNAL_REVIEW_20261115-233040`, `--paths` DEFINE + DESIGN): claude revisa (US$ 0,7441 nominal, assinatura), openrouter qwen/qwen3.7-plus audita (US$ 0,0185); o auditor concordou com R1 a R3 e discordou de R4 a R6.

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| R1 | validação por `grep` linha a linha aceita valor com quebra de linha e forja linha no trace | HIGH | APLICADA | Pattern 2 com a contagem de quebras (`wc -l` = 0); `sdd/bin/marca-fase.sh`; teste do AT-001 com `\n` no meio e no fim |
| R2 | janela termina na última marca: fase aberta nunca chega ao fim da sessão | MED | APLICADA | Decision 5: com fase aberta, a janela vai até o fim da última sessão |
| R3 | `<F>` ambíguo (F23 × F23_ECONOMIA_MENSURAVEL) | MED | APLICADA | Data Flow: `<F>` é o feature_id inteiro; `verify-gate.sh:146` deriva o trace do basename do DEFINE sem `DEFINE_` |
| R4 | pasta do Claude derivada trocando só `/` | MED | APLICADA | o leitor troca todo caractere fora de A-Z, a-z e 0-9 (`re.sub(r"[^A-Za-z0-9]", "-", …)`), conferido nas pastas reais (`com~apple~CloudDocs` → `com-apple-CloudDocs`, `BRAVO_RDD` → `BRAVO-RDD`, `Convenções` → `Conven--es`); a A-003 do DEFINE foi corrigida |
| R5 | DEFINE e DESIGN no diff reprovariam o publish-gate | MED | REBATIDA_EVIDENCIA | os artefatos SDD ficam sem commit nesta branch (DEFINE, Constraints › Process); o diff da revisão os leva porque o `adversarial-review.sh` inclui os não rastreados (`congelar`, `--intent-to-add`); o gate roda de `git archive HEAD`, que só leva o que foi commitado |
| R6 | sessões sem nenhuma marca podem dar total US$ 0 | LOW | APLICADA | Decision 5: sem marca, `sem fase` sai `n/d` com aviso; teste no AT-004 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-15 | design-agent | Initial version |
| 1.1 | 2026-11-15 | design-agent | Revisão do DESIGN, rodada 1: R1, R2, R3, R4 e R6 aplicados; R5 rebatido com evidência |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F23_ECONOMIA_MENSURAVEL.md`
