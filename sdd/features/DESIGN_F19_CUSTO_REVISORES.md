# DESIGN: F19 — Custo e benefício dos modelos de revisão

> Dois scripts só de leitura (`eval-revisores.sh`, `ledger-revisao-lint.sh`), um formato de ledger de 7 colunas compatível com o que o `sdd-fluxo.sh loop` já lê, o critério de dano escrito e as duas skills de fase pedindo o ledger.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F19_CUSTO_REVISORES |
| **Date** | 2026-11-10 |
| **Author** | design-agent (worktree `sdd-open-f21-f19`; branch `feat/f19-custo-revisores`) |
| **DEFINE** | `sdd/features/DEFINE_F19_CUSTO_REVISORES.md` v1.2 |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
adversarial-review.sh (não muda)                      quem decide os achados
        │ grava, por rodada                                    │ grava, por frente
        ▼                                                      ▼
<review.output_dir>/EXTERNAL_REVIEW_<quando>/         sdd/reviews/LEDGER_REVISAO_{F}.md
   META.txt  (papel → engine, modelo, custo, exit)       | achado | sev | veredito | rodada | evidência | dano | revisão |
   reviewer.verdicts.jsonl · reviewer2.verdicts.jsonl          │                 │
   auditor.verdicts.jsonl                                      │                 └── ledger-revisao-lint.sh  (0 · 2 · 64)
        │                                                      │
        │                    sdd/review/registry.tsv           ├── sdd-fluxo.sh loop --ledger  (lê as 4 primeiras células; não muda)
        │                    (engine → cobrança)               │
        └──────────────┬───────────┴───────────────────────────┘
                       ▼
              eval-revisores.sh  (só lê; sem rede; 0 MEDIDO · 2 SEM DADOS · 64 uso)
                       ▼
   uma linha por papel + engine + modelo:
   rodadas · falhas por motivo · pago · nominal · achados · aplicados · com dano ·
   falsos positivos · fora de escopo · sem classificar · custo por dano (2 bases) · AGREE
```

---

## Components

| Component | Purpose | Technology |
|---|---|---|
| `sdd/bin/eval-revisores.sh` | junta custo e resultado por papel, engine e modelo | bash 3.2 + Python ≥ 3.9 stdlib (`decimal`) |
| `sdd/bin/ledger-revisao-lint.sh` | confere o ledger de 7 colunas | bash 3.2 + Python ≥ 3.9 stdlib |
| `sdd/review/CRITERIO_DANO.md` | o que é falha real com dano e quem marca | Markdown |
| `sdd/templates/LEDGER_REVISAO_TEMPLATE.md` | molde do ledger por frente | Markdown |
| `sdd/fixtures/revisao/custo/`, `sdd/fixtures/revisao/ledger/` | os 5 casos reais com dados inventados; controle e 6 reprovações | arquivos de texto |
| `sdd-build` 5c, `sdd-release` 0a item 8 | pedem o ledger e o lint | Markdown |

---

## Key Decisions

### Decision 1: Ledger de 7 colunas cujas 5 primeiras são as do loop

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o `sdd-fluxo.sh loop --ledger` lê cada linha por célula e exige `c[3] == "rodada=N"`; as células depois da 4ª não são lidas.
**Choice:** `| achado | sev | veredito | rodada | evidência | dano | revisão |`. As 5 primeiras ficam como o loop já documenta; `dano` (`sim`, `nao`, `?`) e `revisão` (a pasta `EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>`) vêm no fim. Um arquivo por frente, `sdd/reviews/LEDGER_REVISAO_{F}.md`, com todas as rodadas; a linha `retroativo: sim` no topo libera o `?`.
**Rationale:** o loop não muda (AT-007); o mesmo arquivo serve ao loop, ao lint e ao medidor.
**Alternatives Rejected:** 1. `dano` antes de `rodada` (ordem mostrada no brainstorm) — quebraria o loop · 2. um arquivo por rodada — o medidor teria de casar arquivos por nome · 3. YAML — o loop lê tabela.
**Consequences:** o id do achado é único por pasta de revisão, não por arquivo; o lint confere a dupla (revisão, achado), inclusive entre os arquivos passados juntos. O id é **copiado do arquivo de vereditos** da rodada: `R1` e `N1` numa rodada de um revisor só, `R1@claude` quando houve dois (é assim que o `adversarial-review.sh` grava, e o loop só casa id exato ou a base sem rótulo). Rodada em que a revisão não achou nada é uma linha fora da tabela, `sem achados: rodada=<N> EXTERNAL_REVIEW_…`: o lint a conta como conferida e o medidor não avisa a pasta como "sem ledger".

### Decision 2: O lint é script próprio, não um modo do loop

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o loop decide se segue; o lint decide se o registro está completo. São perguntas diferentes e o loop tem 60 fixtures de contrato.
**Choice:** `sdd/bin/ledger-revisao-lint.sh <arquivo>…`, exits 0 ok · 2 violação com `arquivo:linha — motivo` · 64 uso, arquivo ilegível, ou arquivo sem linha de dados e sem linha `sem achados:`. **O arquivo é só do ledger** (v1.2): toda linha de tabela, fora de bloco cercado e de comentário `<!-- -->`, é o cabeçalho do molde (que pode se repetir entre rodadas) ou uma linha de dados; outra tabela no arquivo reprova. A v1.1 dizia "só a tabela cujo cabeçalho começa por `achado`": essa escolha de tabela era uma heurística sobre texto livre e regrediu duas vezes (revisão adversarial, rodada 1; avaliador, ciclo 1), deixando linha sem conferir; pela LM-005, na 2ª regressão a heurística saiu. Regras: cabeçalho do molde; 7 células; formato de cada uma (`achado` = `R<n>` ou `N<n>` com `@engine` opcional; pasta com `-<n>` opcional); `dano = sim` só com `APLICADA` e com `teste:` seguido de um nome com forma de teste (`test_…`, `arquivo::teste`, `tests/…`), sem diferença de caixa em `teste:`; `dano = ?` só em arquivo com a linha `retroativo: sim` sozinha, fora de cerca (as quase-formas, como negrito, citação ou maiúscula, reprovam dizendo a forma certa); dupla (revisão, achado) sem repetição, no arquivo e entre os arquivos passados. Todos os arquivos são lidos antes de conferir.
**Rationale:** "nada conferido nunca é verde" (mesma regra do `sdd-decisoes-lint.sh`); mensagens com o conserto.
**Alternatives Rejected:** 1. `loop --lint` — mistura contratos.
**Consequences:** o lint não confere se o teste citado existe nem se a pasta existe: quem liga ledger e pastas é o medidor ("fora da conta").

### Decision 3: Uma linha por papel + engine base + modelo como o META registra

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o Roberto quer ver o mesmo modelo custando diferente conforme o provedor. O `eval-agree.sh` junta os provedores numa linha; aqui é o contrário.
**Choice:** chave = (papel, `engine base (modelo)`), em que engine base é o id sem o slug (`openrouter:x/y` → `openrouter`) e modelo é o campo `<papel>_modelo` inteiro (com ` via <provedor>`); quando o META traz `-`, `n/d` ou vazio (a chamada falhou antes de responder), o modelo é o slug do id, ou `-`. Papéis lidos pelos prefixos `reviewer`, `revisor2`, `auditor`, `desempate`; o papel só conta numa pasta se tem engine e `<papel>_exit` numérico.
**Rationale:** validação 1 do brainstorm; falha sem provedor conhecido fica em linha própria, o que é verdade (não se sabe qual provedor falhou).
**Alternatives Rejected:** 1. juntar provedores — esconde o caso pedido · 2. agrupar só por engine — mistura modelos.
**Consequences:** mais linhas com amostra 1; a amostra vai ao lado de cada número. Papel com `engine_efetivo` = `indisponível` (nenhuma engine chamada) não vira linha: vai para "fora da conta". Quando `<papel>_fallback_usado` é `sim`, a engine de `<papel>_engine_default` ganha uma falha `trocada por outra engine` na linha dela (modelo `-`). **Limite declarado:** o `META.txt` não separa o custo da tentativa que falhou antes da troca; ele fica na linha da engine que respondeu.

### Decision 4: Pago pela cobrança do registry; nominal por todo custo numérico; decimal exato

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** o campo `<papel>_custo` vem como `US$ n`, `≈US$ n`, `US$ n + $?` (tempo esgotado em engine que não é assinatura), `assinatura`, `$?` ou `n/d`. O claude é `assinatura` no registry e reporta o valor de tabela.
**Choice:** nominal soma todo custo numérico; pago soma só quando a cobrança da engine base no `registry.tsv` é `pay-per-token`; engine `assinatura` mostra pago `0.0000`; engine `desconhecida` ou fora do registry mostra pago `n/d`. Chamada sem número conta em "n/d em N de M" e nunca vira zero; linha em que nenhuma chamada tem número mostra `n/d`. De `US$ n + $?` o `n` entra na soma e a linha avisa `incerto em N de M`. Somas com `decimal.Decimal` e saída com 4 casas, ou 6 quando o valor é menor que 0,0001. O `≈` e a ressalva valem nas 4 colunas de dinheiro (no custo por dano a ressalva vira `(parcial)`). Chamada com exit ≠ 0 e custo numérico entra nas somas (engine cobrada sem responder). Custo por falha com dano = soma ÷ `com dano`, `—` quando não há dano ou não há custo.
**Rationale:** perguntas 4 do brainstorm e os dois cuidados da dispensa de governança (aritmética exata; ausência não é zero).
**Alternatives Rejected:** 1. `float` — 0.1 + 0.2 imprime errado em soma longa · 2. tratar `assinatura` como zero no nominal — esconde o custo.
**Consequences:** o registry é lido de `--registry`, do slot `review.registry`, de `sdd/review/registry.tsv` do projeto ou do pacote, nessa ordem.

### Decision 5: Ligação ledger → papel pela pasta e pelo id, com "fora da conta"

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** nas rodadas com um revisor só, o arquivo de vereditos traz `R1`; com dois, `R1@claude` e `R1@codex`; o auditor traz `N1` sem engine. O ledger copia o id do arquivo; ledgers antigos às vezes acrescentaram o rótulo por conta própria.
**Choice:** para cada pasta, os ids de cada papel vêm do arquivo de vereditos dele (`NOVO` para o auditor). Uma linha do ledger casa com o id exato; ou, sem o rótulo, com o id de mesma base quando essa base pertence a um papel só naquela pasta. Quando o ledger traz rótulo e o arquivo não, o rótulo tem de ser o da engine que respondeu naquele papel (o id da engine com `:` e `/` trocados por `-`, ou a engine base); senão a linha vai para "fora da conta". Um achado conta uma vez: a segunda linha para o mesmo achado, em qualquer veredito e em qualquer arquivo, vai para "fora da conta" como repetida. Vão para "fora da conta", com `arquivo:linha` ou pasta e o motivo, e não entram nos números: linha de dados fora do formato, linha que não casa, linha repetida, pasta com `META.txt` ilegível, papel indisponível. Pasta sem linha em nenhum ledger **conta** (rodadas, custo, achados em "sem classificar") e é avisada; sem nenhum ledger lido, o aviso é um só. `sem classificar` = achados do papel sem linha, mais linhas com `dano = ?`.
**Rationale:** mesma regra de base única que o loop usa (`base_unica`); nada é contado por adivinhação.
**Alternatives Rejected:** 1. confiar no `@engine` do ledger para achar o papel — a engine pode ter dois papéis na mesma rodada.
**Consequences:** um `R1@codex` no ledger numa rodada em que só o claude revisou fica fora da conta, com o motivo; o medidor usa o mesmo corte de célula do lint.

### Decision 6: Fixtures inventadas que reproduzem os 5 casos reais, com números fixados nos testes

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** LM-001 e LM-002; o repositório é público.
**Choice:** `sdd/fixtures/revisao/custo/` com 5 pastas `EXTERNAL_REVIEW_20260201-00000N` e `LEDGER_REVISAO_EXEMPLO.md`: (1) revisor por assinatura com custo de tabela, auditor pago pelo provedor A; (2) mesmo auditor pelo provedor B, mais caro, com um `NOVO` rebatido; (3) o mesmo `NOVO` repetido e rebatido de novo; 2º revisor que falha por cota (exit 67) depois de cobrado; (4) 2º revisor que falha por credencial (exit 65), auditor com `$?`; (5) 2º revisor por assinatura sem valor (`assinatura`) com um achado aplicado com dano; (6) `META.txt` vazio; (7) revisão sem achados, com o 2º revisor `indisponível`. A rodada 3 traz o custo `US$ n + $?` e a 4 traz a troca de engine do auditor. O ledger de exemplo usa os ids como estão nos arquivos de vereditos e tem 2 linhas que ficam fora da conta de propósito. Os testes afirmam cada célula da tabela esperada; as formas do custo, a repetição e as linhas fora do formato são testadas com pastas temporárias.
**Rationale:** cada coluna tem um caso que a preenche e um que a deixa vazia.
**Alternatives Rejected:** 1. reaproveitar `sdd/fixtures/revisao/eval/` — são do `eval-agree` e não têm custo.
**Consequences:** 5 pastas novas no pacote; o `init` as leva como exemplo.

### Decision 7: As duas skills pedem o arquivo; o Advisor Ledger do relatório aponta para ele

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** validação 2 do brainstorm: sem a skill pedir, o lint não exige nada.
**Choice:** `sdd-build` 5c: depois de cada rodada, gravar as linhas em `sdd/reviews/LEDGER_REVISAO_{F}.md` pelo molde, rodar `bash sdd/bin/ledger-revisao-lint.sh`, e passar o arquivo ao `loop --ledger`; a marca `dano` é de quem decide o achado, pelo `sdd/review/CRITERIO_DANO.md`. `sdd-release` 0a item 8: com revisão feita, o lint do ledger sai 0, senão **abortar** (dispensa de revisão dispensa o ledger); revisão que não achou nada registra a linha `sem achados:` de cada rodada, que o lint aceita. `BUILD_REPORT_TEMPLATE.md`: o Advisor Ledger ganha a linha "ledger da revisão: `sdd/reviews/LEDGER_REVISAO_{F}.md`". Bumps: `sdd-build` 2.8.0, `sdd-release` 2.10.0.
**Rationale:** o registro nasce no momento da decisão.
**Alternatives Rejected:** 1. só documentar — fica opcional.
**Consequences:** os testes que fixam as versões das duas skills mudam de propósito; nenhum rótulo do bloco do OK muda.

### Decision 8: O retroativo é documento, fora do pacote

| **Status** | Accepted | · | **Date** | 2026-11-10 |

**Context:** pergunta 5 do brainstorm.
**Choice:** na branch de documentos: `sdd/reviews/LEDGER_REVISAO_{F13_UX_LLM,F14_PLAYBOOK,F14_DRIVE,F15_SLOTS,F21_ENGENHARIA_REVERSA}.md` (os 4 primeiros com `retroativo: sim`: F13, F14 Playbook e F14 Drive convertidos dos `ledger-review.md` de 5 colunas que já existem na evidência, com a pasta de cada rodada tirada do cabeçalho deles; F15_SLOTS transcrito do Advisor Ledger do relatório; `dano = sim` só onde a evidência cita o teste, o resto `?`; linha com veredito composto, como "APLICADA em parte", vira a parte principal, com a ressalva na evidência) e `sdd/reports/RETROATIVO_REVISORES_2026-11-10.md` com a saída do script sobre as 25 pastas, a amostra por engine e os limites. As pastas `EXTERNAL_REVIEW_*` continuam fora do git.
**Rationale:** dados reais não entram no pacote; a conta é a mesma das fixtures.
**Alternatives Rejected:** 1. levar as pastas reais para o repositório — tamanho e conteúdo de revisão.
**Consequences:** o relatório cita onde as pastas ficaram guardadas pelo nome do arquivo, sem caminho de máquina.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|---|---|---|---|---|
| 1 | `sdd/bin/eval-revisores.sh` | Create | o medidor | (general) | None |
| 2 | `sdd/bin/ledger-revisao-lint.sh` | Create | o lint do ledger | (general) | None |
| 3 | `sdd/review/CRITERIO_DANO.md` | Create | critério, quem marca, exemplos | (general) | None |
| 4 | `sdd/templates/LEDGER_REVISAO_TEMPLATE.md` | Create | molde de 7 colunas | (general) | 3 |
| 5 | `sdd/fixtures/revisao/custo/` (7 pastas `EXTERNAL_REVIEW_*`, `LEDGER_REVISAO_EXEMPLO.md`, `registry.tsv`) | Create | os casos reais com dados inventados | (general) | None |
| 6 | `sdd/fixtures/revisao/ledger/` (`controle.md`, `retroativo.md`, `so-sem-achados.md`, `sem-linhas.md` e 7 reprovações) | Create | fixtures do lint | (general) | None |
| 7 | `sdd/fixtures/fluxo/ledger-7-colunas.md` | Create | o ledger novo lido pelo loop | (general) | None |
| 8 | `tests/test_eval_revisores.py` | Create | AT-001 a AT-005 | (general) | 1, 5 |
| 9 | `tests/test_ledger_revisao_lint.py` | Create | AT-006 | (general) | 2, 6 |
| 10 | `tests/test_fluxo.py` | Modify | AT-007: o ledger de 7 colunas com ids rotulados e com ids sem rótulo | (general) | 7 |
| 11 | `tests/test_f19_textos.py` | Create | AT-008 e AT-009 | (general) | 3, 4, 12, 13, 14, 15, 16, 17, 18 |
| 12 | `.agents/skills/sdd-build/SKILL.md` | Modify | 5c pede o ledger e o lint; 2.8.0 | (general) | 2, 4 |
| 13 | `.agents/skills/sdd-release/SKILL.md` | Modify | 0a item 8 confere o lint do ledger; 2.10.0 | (general) | 2 |
| 14 | `sdd/templates/BUILD_REPORT_TEMPLATE.md` | Modify | Advisor Ledger aponta o arquivo | (general) | 4 |
| 15 | `docs/adversarial-review.md` | Modify | seção do medidor e do ledger | (general) | 1, 2 |
| 16 | `docs/pt-BR/adversarial-review.md` | Modify | idem em PT | (general) | 1, 2 |
| 17 | `docs/cli-conventions.md` | Modify | linhas dos 2 scripts | (general) | 1, 2 |
| 18 | `sdd/WORKFLOW_CONTRACTS.yaml` | Modify | contratos `eval_revisores` e `ledger_revisao` | (general) | 1, 2 |
| 19 | `tests/test_contrato_build_release.py`, `tests/test_f14_drive_textos.py`, `tests/test_f14_textos.py`, `tests/test_f15_slots_textos.py`, `tests/test_correcoes_w0.py` | Modify | versões novas das 2 skills, inclusive a linha de identificação de cada uma | (general) | 12, 13 |
| 20 | `MANIFEST.txt` | Modify | arquivos novos | (general) | 8, 9, 11 |

**Total Files:** 20

Outro arquivo que liste scripts de `sdd/bin/` ou fixe versão de skill e apareça vermelho na suíte entra como drift no BUILD_REPORT.

---

## Landmines aplicáveis

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---|---|---|---|
| Gate que só confere fiação | LM-001 | ✔ tratado | os testes rodam os 2 scripts sobre fixtures dos dois lados e afirmam cada célula; 3 sabotagens |
| Asserção que não avalia nada | LM-002 | ✔ tratado | linha de base vermelha em `origin/main`; "sem linha de dados" é 64 no lint e 2 no medidor |
| Review sobre diff vazio | LM-003 | ✔ tratado | commit antes de cada rodada |
| Migration por exit 0 | LM-004 | N.A. | sem banco |
| Heurística sobre texto livre | LM-005 | ✔ tratado | motivo de existir do ledger: o medidor não interpreta o Advisor Ledger do relatório |
| Script que só roda com `.git` | LM-006 | ✔ tratado | os 2 scripts aceitam caminho por argumento; sem git, a pasta atual é a raiz; gate em cópia de `git archive` |
| `limit_remaining` não é saldo | LM-008 | N.A. | o script não consulta saldo nem rede |
| Sabotagem com `git checkout` | LM-009 | ✔ tratado | mutantes em cópia de `git archive` |
| Engine paga que estoura o teto | LM-010 | ✔ tratado | é o caso (3) das fixtures: falha com custo entra no pago; na revisão desta frente, só claude + qwen, sem 2º revisor pago |

Varredura rodada em 2026-11-10 pelos termos `review`, `OpenRouter`, `saldo`, `exit 0`, `heurística`, `git archive`, `git checkout`, `verify-gate`, `ledger`.

---

## Contrato de aceite

N.A. (1 camada): o repositório do pacote não declara `layers:`.

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|---|---|---|
| (general) | 1–20 | sem especialista no harness |

**Agent Discovery:** o repositório do pacote não tem diretório de agentes.

---

## Code Patterns

### Pattern 1: Cabeçalho e uso (igual ao `eval-agree.sh`)

```bash
# USO-INICIO
#   eval-revisores.sh [<pasta-das-revisões>] [--ledgers <pasta-ou-arquivo>] [--registry <registry.tsv>]
#       0 MEDIDO · 2 SEM DADOS · 64 uso, ou pasta/arquivo passado não existe
# USO-FIM
set -u
case "${1:-}" in -h|--help) sed -n '/^# USO-INICIO$/,/^# USO-FIM$/p' "$0" | sed '1d;$d;s/^# \{0,1\}//'; exit 0 ;; esac
exec python3 -B - "$@" <<'PY'
```

### Pattern 2: Custo em decimal, ausência nunca é zero

```python
CUSTO_RE = re.compile(r"^(≈)?\s*US\$\s*([0-9]+(?:[.,][0-9]+)?)$")
def custo_de(valor):
    m = CUSTO_RE.match((valor or "").strip())
    if not m:
        return None, False                      # assinatura, $?, n/d: sem custo informado
    return Decimal(m.group(2).replace(",", ".")), bool(m.group(1))
```

### Pattern 3: Linha do ledger por célula

```python
c = [x.strip() for x in re.split(r"(?<!\\)\|", ln)][1:]
if c and c[-1] == "":
    c = c[:-1]
achado, sev, veredito, rodada, evidencia, dano, pasta = c   # depois de conferir len(c) == 7
```

candidato a pattern: nenhum.

---

## Data Flow

```text
1. por pasta EXTERNAL_REVIEW_*: META.txt → para cada papel: engine, modelo, custo, exit
2. exit ≠ 0 → falha por motivo (o custo, se houver, entra nas somas)
3. exit = 0 → rodada; ids do arquivo de vereditos do papel = achados
4. linhas do ledger daquela pasta → aplicados, falsos positivos, fora de escopo, com dano, sem classificar
5. auditor: AGREE ÷ (AGREE + DISAGREE_*)
6. imprime a tabela, "fora da conta", RESULTADO e a seta
```

---

## Integration Points

| External System | Integration Type | Notes |
|---|---|---|
| `adversarial-review.sh` | leitura do que ele grava | sem mudança nele |
| `sdd-fluxo.sh loop` | lê o mesmo ledger | sem mudança nele (AT-007) |
| `registry.tsv` | leitura da coluna cobrança | — |

---

## Testing Strategy

| Test Type | Scope | Tool | Coverage Goal |
|---|---|---|---|
| Unit | AT-001 a AT-005: tabela inteira sobre as 5 pastas; soma decimal; n/d; falhas por motivo; fora da conta; SEM DADOS; uso; sem módulo de rede no script; roda fora de git | `tests/test_eval_revisores.py` | cada célula afirmada |
| Unit | AT-006: controle 0, retroativo 0, 6 reprovações com o motivo, uso 64 | `tests/test_ledger_revisao_lint.py` | 1 motivo por fixture |
| Não-regressão | AT-007: loop fecha HIGH com o ledger de 7 colunas; `test_eval_agree.py` e `test_revisao.py` verdes | `tests/test_fluxo.py` + suíte | — |
| Texto | AT-008: critério, molde, 2 skills, 3 docs, contratos, MANIFEST, versões | `tests/test_f19_textos.py` | — |
| Integração | AT-009: `init` num projeto novo leva os 4 arquivos; medidor sai 2 SEM DADOS | `tests/test_f19_textos.py` | 1 projeto |
| Linha de base | os testes novos falham em `origin/main` | cópia de `git archive` | log |
| Sabotagem | 3 mutantes em cópia de `git archive` | script temporário | teste nomeado |
| Gate | Verify Gate do DEFINE | `verify-gate.sh --strict` | exit 0 |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|---|---|---|
| pasta ou arquivo passado não existe | 64 com causa e conserto | — |
| nenhuma pasta com META legível | 2 SEM DADOS | — |
| linha do ledger sem pasta ou achado correspondente | "fora da conta", segue | — |
| custo sem número | conta como n/d | — |
| registry ausente | cobrança `desconhecida` em todas; pago `n/d` | — |

---

## Configuration

Nenhuma chave nova. Lidas: `review.output_dir` e `review.registry`, que já existem.

---

## Security Considerations

- Só leitura: os scripts não escrevem arquivo, não chamam engine e não abrem rede (teste confere a ausência de `socket`, `urllib`, `http`, `curl`).
- Fixtures com dados inventados; nenhum nome de projeto, caminho de máquina ou chave.
- O ledger guarda decisões e nomes de teste; o lint não executa nada do que lê.

---

## Observability

A própria saída: tabela, "fora da conta" com o motivo de cada exclusão, `RESULTADO:`.

---

## Advisor Ledger

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|
| 1 | o lint exigia `@engine` no id; o `adversarial-review.sh` só rotula com 2 revisores e o loop só casa id exato ou a base: nenhum arquivo passava nos dois | HIGH | APLICADA | Decision 1; DEFINE v1.1, AT-006 e AT-007; `sdd/bin/sdd-fluxo.sh` (`base_unica`) |
| 2 | rodada sem achados dava 64 no lint e abortaria a release | HIGH | APLICADA | linha `sem achados:` (Decision 1, 2 e 7) |
| 3 | custo `US$ n + $?` era lido como sem custo | MED | APLICADA | Decision 4 |
| 4 | engine que falhou antes da troca não aparecia em falhas | MED | APLICADA | Decision 3 (`trocada por outra engine`; limite do custo declarado) |
| 5 | 2º revisor `indisponível` virava linha de engine com falha por cota | MED | APLICADA | Decision 3 |
| 6 | o medidor descartava linhas do ledger em silêncio | MED | APLICADA | Decision 5; DEFINE v1.1, AT-005 |
| 7 | a mesma dupla (revisão, achado) em 2 ledgers contava em dobro | MED | APLICADA | Decision 5 (medidor) e Decision 2 (lint entre arquivos) |
| 8 | o lint não conhecia bloco cercado nem outra tabela; quase-formas de `retroativo: sim` passavam sem aviso | MED | APLICADA | Decision 2 |
| 9 | rótulo `@engine` do ledger não era conferido contra quem revisou | LOW | APLICADA | Decision 5 |
| 10 | pasta com sufixo de colisão (`-2`) era recusada | LOW | APLICADA | Decision 2; AT-006 |
| 11 | `≈` só no nominal; custo por dano sem ressalva; valor abaixo de 0,0001 virava 0.0000 | LOW | APLICADA | Decision 4 |
| 12 | "pasta sem linha em nenhum ledger": DESIGN e protótipo diziam coisas diferentes | LOW | APLICADA | Decision 5: conta e avisa |
| 13 | "nome de pasta repetido" não tem como acontecer com uma pasta só | LOW | APLICADA | frase retirada do DEFINE e do DESIGN |
| 14 | faltava `tests/test_correcoes_w0.py`, que fixa a versão da `sdd-build` | MED | APLICADA | manifest 19 |
| 15 | `teste:` aceitava qualquer palavra e era sensível a caixa | LOW | APLICADA | Decision 2 |
| 16 | cabeçalho fora do molde virava 6 violações de dado | LOW | APLICADA | Decision 2: uma mensagem só |
| 17 | violações de um arquivo se perdiam quando o seguinte era ilegível | LOW | APLICADA | Decision 2: todos lidos antes |
| 18 | (pós-build) a nota 8 pedia ignorar outras tabelas; a regra que escolhia a tabela regrediu 2 vezes | HIGH | APLICADA | Decision 2, v1.2: o arquivo é só do ledger; `sdd/reviews/AVALIACAO_F19_CUSTO_REVISORES_20261110-ciclo1.md`, A1 |

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-10 | design-agent | Initial version |
| 1.2 | 2026-11-10 | design-agent | Decision 2: o arquivo é só do ledger (sai a escolha de tabela); medidor avisa exit ilegível, papel sem arquivo de vereditos, `dano` fora da lista e `sem achados` contraditório |
| 1.3 | 2026-11-10 | design-agent | Decision 2, depois da rodada 4 da revisão e do ciclo 3 do avaliador: a linha de tabela é conferida também dentro de bloco cercado e de comentário, porque o `sdd-fluxo.sh loop` a lê (ali só as marcas de texto deixam de valer); a cerca se reconhece como no CommonMark; onde este documento diz "fora de bloco cercado e de comentário" para linha de tabela, vale esta linha |
| 1.1 | 2026-11-10 | design-agent | revisão de contexto fresco (veredito NÃO PRONTO): 17 notas, 2 HIGH, todas aplicadas; ids copiados do arquivo de vereditos, linha `sem achados:`, falha por troca de engine, nada some em silêncio |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F19_CUSTO_REVISORES.md`
