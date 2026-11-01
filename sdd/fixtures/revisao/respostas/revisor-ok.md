**Veredito geral** — APROVADO COM RESSALVAS. Um defeito grave e um médio.

**Conformidade com o DEFINE e o DESIGN** — divergência no tratamento de entrada vazia.

**Achados**
- R1 `src/conta.sh:12` · HIGH · CONFIRMED · divisão por zero com lista vazia. Cenário: lista vazia → erro.
- R2 `src/conta.sh:30` · MED · PLAUSIBLE · arredondamento perde centavos. Cenário: 0,005 → 0,00.

<<<VERDICTS
{"achado":"R1","arquivo":"src/conta.sh","linha":12,"severidade":"HIGH","confianca":"CONFIRMED","resumo":"divisão por zero com lista vazia"}
{"achado":"R2","arquivo":"src/conta.sh","linha":30,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"arredondamento perde centavos"}
VERDICTS>>>
