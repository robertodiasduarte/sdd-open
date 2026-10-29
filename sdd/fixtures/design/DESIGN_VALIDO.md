# DESIGN: Contador de linhas

> Fixture do `sdd/bin/design-lint.py`: DESIGN preenchido a partir de `sdd/templates/DESIGN_TEMPLATE.md`,
> que passa. Os testes trocam um trecho por vez para provar cada regra.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | CONTADOR_LINHAS |
| **Date** | 2026-10-29 |
| **DEFINE** | `sdd/features/DEFINE_CONTADOR_LINHAS.md` |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
arquivo.txt ──► conta.py ──► stdout ("12 linhas")
```

---

## Key Decisions

### Decision 1: Lint em Python

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** o projeto já tem Python 3.9 em todo lugar onde o contador roda.

**Choice:** um script só, `conta.py`, sem dependência.

**Rationale:** menos peças para instalar.

**Alternatives Rejected:**
1. Shell com `wc -l` - Rejected because a saída muda entre sistemas.

**Consequences:**
- Exige Python 3.9.

---

### Decision 2: Saída em uma linha

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-10-29 |

**Context:** quem lê a saída é uma pessoa no terminal.

**Choice:** imprimir só `N linhas`; o nome do arquivo vai no erro, como `arquivo {nome} ausente`.

**Rationale:** dá para ler sem rolar a tela.

**Alternatives Rejected:**
1. JSON - Rejected because ninguém consome a saída por programa.

**Consequences:**
- Mudar o formato depois exige versão nova.

---

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `conta.py` | Create | Lint | (general) | None |
| 2 | `exemplo.txt` | Create | Amostra com 12 linhas | (general) | None |
| 3 | `tests/test_conta.py` | Create | Conta a amostra e confere `12 linhas` | (general) | 1, 2 |

**Total Files:** 3

---

## Code Patterns

### Pattern 1: Entrada

```python
def conta(caminho: str) -> int:
    with open(caminho, encoding="utf-8") as f:
        return sum(1 for _ in f)

MENSAGEM = "arquivo {nome} ausente"  # chave dentro de código não é placeholder
```

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit | `conta()` | `tests/test_conta.py` | unittest | A amostra dá 12 |

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-10-29 | design-agent | Initial version |

---

## Next Step

Execute o **SDD Build by RDD**.
