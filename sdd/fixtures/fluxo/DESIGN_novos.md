# DESIGN: NOVOS

> Fixture do sdd-fluxo.sh review-design (3 arquivos novos, sem superfície de segurança → EXIGIDO).

## File Manifest

| # | File | Action | Purpose | Agent | Dependencies |
|---|------|--------|---------|-------|--------------|
| 1 | `src/relatorio/mensal.py` | Create | gera o relatório | (general) | None |
| 2 | `src/relatorio/anual.py` | **Create** | gera o anual | (general) | None |
| 3 | `tests/test_relatorio.py` | criar | testes | (general) | 1, 2 |
| 4 | `README.md` | Modify | documenta | (general) | None |

**Total Files:** 4

## Next Step

fixture
