# DESIGN: NUMERADO

> Fixture do `sdd-fluxo.sh review-design`: título numerado com qualificador e as ações `NOVO`, `new` e
> `**Create**` (3 arquivos novos → EXIGIDO), como os DESIGNs reais escrevem.

## 3. File Manifest (fatia 1)

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/fechamento.py` | NOVO | fecha o mês | (general) | None |
| 2 | `src/abertura.py` | new | abre o mês | (general) | None |
| 3 | `tests/test_fechamento.py` | **Create** | testes | (general) | 1 |
| 4 | `src/relatorio/mensal.py` | `Modify` | usa o fechamento | (general) | 1 |

**Total Files:** 4

## 4. Code Patterns

Nenhum.
