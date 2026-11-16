# Fixtures da F24 (release enxuta)

Usadas por `tests/test_f24_release_enxuta.py`. Dados sintéticos.

- `workflows/`: um workflow por arquivo, copiado sozinho para `.github/workflows/` de um projeto de teste, para o
  `push-de-papel.py` (o commit de papel publica?).
- `ledgers/`: 3 ledgers de uma feature, 1 deles ilegível, para o `ficha-publicado.py`.
- `ficha-curta.md` (passa no `handoff-lint.py --curta`) e `ficha-curta-longa.md` (21 linhas: reprova).
