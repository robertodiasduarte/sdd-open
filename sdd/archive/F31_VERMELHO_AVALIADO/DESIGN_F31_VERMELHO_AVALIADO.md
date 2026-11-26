# DESIGN: F31 — Vermelho avaliado

> O `report-lint.py` lê a contagem de casos do próprio AT nos logs que já confere e avisa quando ela não prova nada.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F31_VERMELHO_AVALIADO |
| **Date** | 2026-11-25 |
| **Author** | sdd-design v2.12.0 |
| **DEFINE** | [DEFINE_F31_VERMELHO_AVALIADO.md](./DEFINE_F31_VERMELHO_AVALIADO.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
BUILD_REPORT (tabela com `Antes`)          DEFINE (classe do AT)
            │                                     │
            ▼                                     ▼
        check_antes ──── problema_antes (F30 S2, violações; não muda)
            │
            │  só logs que passaram nela
            ▼
        avisos_casos ──► contagem_do_at(log, AT) ──► None | (pass, fail)
            │
            ▼
        warnings: zero casos · já passava · comando compartilhado sem contagem
```

Nenhuma violação nova: o exit do script vem só de `violations`.

---

## Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| `contagem_do_at` | Soma `PASS n · FAIL n` das linhas que começam pelo id exato | `re`, stdlib |
| `avisos_casos` | Decide o aviso por AT e por comando compartilhado | stdlib |
| Textos do método | Ensinam o formato a quem escreve o gate | Markdown |

---

## Key Decisions

### Decision 1: A contagem só gera aviso

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-25 |

**Context:** D2 do DEFINE. Há runner não medido em que o erro de carga pode sair como zero casos.

**Choice:** `avisos_casos` só acrescenta em `warnings`.

**Rationale:** Nenhum relatório aceito hoje muda de exit; o bloqueio entra depois de 5 relatórios sem alarme falso.

**Alternatives Rejected:**
1. Violação já - rejeitada porque trava build correto por formato ensinado agora.
2. Chave de config para ligar o bloqueio - rejeitada porque é opção sem uso medido.

**Consequences:**
- O aviso pode ser ignorado.
- Dá para medir o alarme falso sem custo para quem usa.

### Decision 2: A linha do AT começa pelo id

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-25 |

**Context:** Num log composto, outro AT pode ser citado no meio da linha de alguém.

**Choice:** Sem os códigos de cor, a linha é do AT quando o primeiro texto alfanumérico ASCII dela é o id exato; a contagem é a última da linha, como o método ensina (o título do caso pode citar outra). Letra acentuada antes do id passa como marca: é a folga que aceita a marca corrompida do Windows. Várias linhas do mesmo AT somam. A 1ª linha do log (`$ comando`) fica fora.

**Rationale:** É o formato que a `sdd-define` já pede (`AT-00N ✅/❌`), com a contagem no fim.

**Alternatives Rejected:**
1. Id em qualquer lugar - rejeitada porque a prosa de um teste viraria contagem (LM-028).
2. Ler a saída de cada runner - rejeitada porque é fora de escopo e não separa ATs.

**Consequences:**
- Quem usa outro formato só recebe o aviso do comando compartilhado.
- O leitor tem uma regra só.

### Decision 3: Entre PASS e FAIL vale qualquer separador curto

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-25 |

**Context:** No Windows, o `·` em cp1252 chega como U+FFFD, e o UTF-8 lido como cp1252 vira `Â·`.

**Choice:** De 1 a 6 caracteres que não sejam letra ou dígito ASCII.

**Rationale:** Cobre `·`, `,`, `|`, `/`, U+FFFD e `Â·` sem aceitar palavra no meio.

**Alternatives Rejected:**
1. Só `·` - rejeitada porque o mesmo log daria resultado diferente no Windows.

**Consequences:**
- O formato ensinado é um; o aceito é um pouco mais largo.

### Decision 4: O aviso de log sem contagem depende do comando repetido

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-25 |

**Context:** D1. Um AT só herda o vermelho de outro quando os dois usam o mesmo comando.

**Choice:** Entre os ATs novos `true` de ids distintos com o antes aceito, agrupar pela 1ª linha; grupo de 2 ou mais com algum log sem contagem dá 1 aviso, com os ids dos que estão sem.

**Rationale:** Medido nos 14 logs do Open: 0 avisos, contra 14 de avisar sempre.

**Alternatives Rejected:**
1. Avisar em todo log sem contagem - rejeitada porque acusa comando que é só do AT.

**Consequences:**
- Comando próprio com zero testes e sem contagem segue sem aviso.
- Limites aceitos (avaliador, ciclo 3): com dois logs de mesmo nome na feature, só o primeiro é lido (O2); o mesmo comando com acento gravado em encodings diferentes não forma grupo (O4); o aviso do antes exige o antes aceito também no AT-009 (O5).

### Decision 5: Módulo ausente conta em FAIL, no gate

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-11-25 |

**Context:** D3. O módulo que ainda não existe é vermelho válido.

**Choice:** O texto do método manda somar o erro de carga em FAIL; o lint não procura `ImportError`.

**Rationale:** Num log composto, o `ImportError` pode ser de outro AT: seria o mesmo defeito.

**Alternatives Rejected:**
1. Terceiro contador `ERRO n` - rejeitada porque `unittest` e `node --test` já contam a falha de carga.

**Consequences:**
- Gate que some com o erro de carga recebe um aviso que diz como consertar.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `tests/test_f31_vermelho_avaliado.py` | Create | AT-001 a AT-007 e AT-009, vermelhos antes | (general) | None |
| 2 | `sdd/bin/report-lint.py` | Modify | Leitor e avisos | (general) | 1 |
| 3 | `sdd/templates/fragments/EVIDENCIA.md` | Modify | Contrato do formato e dos avisos | (general) | 2 |
| 4 | `.agents/skills/sdd-build/web/references/disciplina-de-teste.md` | Modify | Ensina o formato (Open e starter) | (general) | 2 |
| 5 | `.agents/skills/sdd-define/SKILL.md` | Modify | Formato no gate composto; versão | (general) | 2 |
| 6 | `.agents/skills/sdd-define/web/MODO_WEB.md` | Modify | Versão | (general) | 5 |
| 7 | `.agents/skills/sdd-build/SKILL.md` | Modify | Versão | (general) | 4 |
| 8 | `.agents/skills/sdd-build/web/MODO_WEB.md` | Modify | Versão | (general) | 7 |
| 9 | `MANIFEST.txt` | Modify | Teste novo | (general) | 1 |
| 10 | `tests/test_contrato_build_release.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 11 | `tests/test_correcoes_w0.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 12 | `tests/test_f14_textos.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 13 | `tests/test_f15_slots_textos.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 14 | `tests/test_f18_f20_textos.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 15 | `tests/test_f19_textos.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |
| 16 | `tests/test_f27_textos.py` | Modify | Versão das skills fixada no teste | (general) | 5, 7 |

**Total Files:** 16

---

## Landmines aplicáveis

Varredura em 2026-11-25 por `report-lint`, `evidence`, `antes`, `MANIFEST`, `cp1252`, `Windows`, `aviso`, `SKILL.md`, `starter`.

| Landmine (⛔) | Fonte | Veredito | Como / Por quê |
|---------------|-------|----------|----------------|
| Gate que só confere fiação | LM-001 | ✔ tratado | Testes executam o lint com os dois lados; 3 sabotagens |
| Asserção que não avalia nada | LM-002 | ✔ tratado | Testes vermelhos antes do código, com log |
| Número de 11 dígitos no pacote | LM-012 | N.A. | Nenhum hash ou id de run |
| `subprocess` sem encoding | LM-014 | ✔ tratado | `Sandbox.roda` de `tests/apoio.py` |
| Aviso calado por `2>/dev/null` | LM-019 | N.A. | O aviso sai no stdout, sem marca de uma vez |
| Desacordo se mede | LM-021 | ✔ tratado | Achado sobre runner ou encoding se mede antes de decidir |
| Juiz por regex alargado | LM-028 | ✔ tratado | Decision 2: começo da linha e id exato |
| Suítes em paralelo | LM-031 | ✔ tratado | Uma suíte por vez |
| `sdd/bin/` em texto do starter | LM-035 | ✔ tratado | `disciplina-de-teste.md` não cita o script; `test_gerar_starter` antes do gate |
| Arquivo novo fora do `MANIFEST.txt` | LM-037 | ✔ tratado | Item 9 |
| Teto de 500 linhas | LM-038 | ✔ tratado | `sdd-define/SKILL.md` em 446 linhas, até 4 a mais |
| Plataforma por `os.name` | LM-042 | N.A. | O teste não pergunta a plataforma |
| Caminho, processo ou link no Windows | LM-016, LM-017, LM-030, LM-034 | N.A. | Sem processo novo, link nem PATH restrito |

---

## Contrato de aceite

N.A. (1 camada): só `sdd/bin` e textos do método; o repositório não tem `layers:` configurado.

---

## Code Patterns

candidato a pattern: nenhum (função pura de leitura de log, no molde de `ler_log_lint`).

### Pattern 1: Leitor da contagem

```python
COR_RE = re.compile(r"\x1b(?:\[[0-9;:]*[A-Za-z]|\([A-Z0-9])")
LINHA_AT_RE = re.compile(r"^[^A-Za-z0-9]*(AT-\d+[A-Za-z0-9_-]*)")
CASOS_RE = re.compile(r"\bPASS[ :=]*(\d{1,9})[^A-Za-z0-9]{1,6}FAIL[ :=]*(\d{1,9})(?!\d)")


def contagem_do_at(caminho, at):
    """(casos que passaram, casos que falharam) somados nas linhas do log que COMEÇAM pelo id exato; None sem contagem.
    Vale a última contagem da linha: o título do caso, antes dela, pode citar outra."""
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            linhas = f.read().split("\n")[1:]   # a 1ª é o `$ comando`
    except OSError:
        return None
    achadas = []
    for linha in linhas:
        linha = COR_RE.sub("", linha)
        dono = LINHA_AT_RE.match(linha)
        casos = CASOS_RE.findall(linha) if dono and dono.group(1) == at else []
        if casos:
            achadas.append((int(casos[-1][0]), int(casos[-1][1])))
    return (sum(p for p, _ in achadas), sum(f for _, f in achadas)) if achadas else None
```

---

## Data Flow

```text
1. check_antes classifica o AT e confere o antes (F30 S2)
   │
   ▼
2. antes aceito → contagem_do_at(antes) → zero casos / já passava
   │
   ▼
3. `AT-nnn.log` da feature citado (com o antes aceito ou não), em [exit=0] → contagem_do_at(final) → zero casos
   │
   ▼
4. comando repetido entre ATs novos, com log sem contagem → 1 aviso por comando
```

---

## Integration Points

| External System | Integration Type | Authentication |
|-----------------|-----------------|----------------|
| Hooks, `sdd-drive` e release | Leem o exit do `report-lint.py`, que não muda | N.A. |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | AT-001 a AT-005, AT-007, AT-009: o lint inteiro sobre relatório de sandbox | `tests/test_f31_vermelho_avaliado.py` | `unittest` | Cada AT com o lado que avisa e o que não avisa |
| Unit | AT-006: o exemplo de cada texto passa por `contagem_do_at` | o mesmo | `unittest` + `importlib` | 3 textos |
| Integration | AT-008 | a suíte inteira, `publish-gate`, `check-versions` | Verify Gate | exit 0 |
| Regressão | exit dos 51 BUILD_REPORTs antes e depois | log em `evidence/` | `report-lint.py` | 51 iguais, 0 avisos novos |

**Sabotagens** (a feature não toca dado, dinheiro, acesso, publicação nem disponibilidade; três assim mesmo):

| AT | Arquivo | Trocar | Por | O que o teste deve acusar |
|---|---|---|---|---|
| `AT-001` | `sdd/bin/report-lint.py` | `if casos == (0, 0):` | `if False:` | o aviso de zero casos some |
| `AT-002` | `sdd/bin/report-lint.py` | `dono.group(1) == at` | `dono.group(1).startswith(at)` | o id vizinho vira contagem do AT |
| `AT-003` | `sdd/bin/report-lint.py` | `if len(grupo) > 1` | `if len(grupo) > 0` | comando próprio passa a avisar |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Log ilegível | `None` (sem contagem); a ausência já é violação da F30 S2 | No |
| Byte fora de UTF-8 | `errors="replace"` | No |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| nenhuma | — | — | — |

---

## Segurança

1. **Onde mora cada segredo:** N.A. — nenhum segredo.
2. **Quem vê e quem muda cada tabela (RLS):** N.A. — sem banco.
3. **Credencial de cada agente ou integração:** N.A. — sem integração.
4. **Cabeçalhos e CORS do host:** N.A. — sem host.
5. **Itens aplicados no Define:** nenhum.

---

## Desempenho

- N.A. — sem banco.

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Avisos com o prefixo `[casos avaliados]`, para contar depois (D2) |

---

## Advisor Ledger

Revisão do DESIGN: dispensável (`sdd-fluxo.sh review-design`: 1 arquivo novo, sem superfície de segurança no manifest).

| # | Nota | Severidade | Veredito | Evidência |
|---|---|---|---|---|

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.2 | 2026-11-25 | build | Avaliador, ciclo 2 (B1): 7 testes com a versão fixa entram no manifest |
| 1.1 | 2026-11-25 | build | Avaliador, ciclo 1 (A1 a A5): última contagem, ids distintos, aviso do final sem depender do antes |
| 1.0 | 2026-11-25 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/sdd-build sdd/features/DESIGN_F31_VERMELHO_AVALIADO.md`
