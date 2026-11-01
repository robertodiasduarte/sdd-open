**Veredito geral** — APROVADO COM RESSALVAS. Resposta fixa do stub do gate offline (sdd/review/stubs/).

**Achados**
- R1 `src/calculo.py:3` · MED · PLAUSIBLE · a média não trata lista vazia. Cenário: lista vazia → erro.
- R2 `src/calculo.py:1` · LOW · CONFIRMED · nome de função pouco claro.

<<<VERDICTS
{"achado":"R1","arquivo":"src/calculo.py","linha":3,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"a média não trata lista vazia"}
{"achado":"R2","arquivo":"src/calculo.py","linha":1,"severidade":"LOW","confianca":"CONFIRMED","resumo":"nome de função pouco claro"}
VERDICTS>>>
