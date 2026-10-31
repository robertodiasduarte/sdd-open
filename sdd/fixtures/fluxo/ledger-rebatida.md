# Ledger da revisão pós-build — fixture (rodada 1)

| achado | sev | veredito | rodada | evidência / motivo |
|---|---|---|---|---|
| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=1 | tests/test_relatorio.py:22 já cobre; não é APLICADA |
| R1 | HIGH | APLICADA | rodada=2 | linha de outra rodada: o decisor ignora |
| R2@rev | MED | APLICADA | rodada=1 | MED não fecha nem abre grave |
