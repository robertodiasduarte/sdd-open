### Auditoria por achado

**R1** — `sdd/bin/deploy-do-sha.sh:340`
**Veredito:** AGREE
**Justificativa:** O código em `sdd/bin/deploy-do-sha.sh:340` mostra que, se o run próprio termina com `conclusion` diferente de `success` e `failure` (ex. `cancelled` ou `timed_out`) e não há runs mais novos listados, o script cai no bloco `elif conc != "failure":` e chama `fim(2, ...)`, encerrando imediatamente com exit 2. Isso ignora a possibilidade de atraso na listagem do GitHub para o run substituto, contrariando a premissa de "ainda não sei" (exit 4) quando não há certeza, e pode levar a release a reportar falha prematuramente.

**R2** — `sdd/bin/deploy-do-sha.sh:376`
**Veredito:** AGREE
**Justificativa:** O bloco `try/except` em `sdd/bin/deploy-do-sha.sh:376` captura `ConsultaFalhou` (que inclui `TimeoutExpired` e `OSError`) e trata qualquer erro como recusa do GitHub, saindo com exit 2 e sem gravar a marca de redisparo (`d.marcar()`). Isso viola o Pattern 4 ("nunca desfecho") e o AT-024, pois uma falha de rede ou timeout pode levar a um segundo redisparo indevido do mesmo SHA em execuções subsequentes.

**R3** — `sdd/bin/sdd-archive.py:194`
**Veredito:** AGREE
**Justificativa:** O código em `sdd/bin/sdd-archive.py:194` exclui apenas `.gitkeep` da varredura (`if nome == ".gitkeep" or not os.path.isfile(p): continue`). Arquivos de controle rastreados, como `.gitignore` ou `.DS_Store`, presentes nas pastas de documento por mais de 60 dias, serão classificados como `soltos` e movidos para o archive, podendo quebrar regras de exclusão locais, conforme o cenário descrito.

### Achados novos

Não há achados novos de severidade HIGH ou MED que as revisões tenham deixado passar. O código está em estrita conformidade com o DEFINE e o DESIGN, e os cenários de borda (como a trava em modo `--fundo`, a impressão digital do gate e a proteção por ficha no archive) estão devidamente cobertos por testes e lógica defensiva.

<<<VERDICTS
{"achado":"R1","veredito":"AGREE","justificativa":"Run próprio cancelled/timed_out sem substituto listado sai 2 imediatamente, sem esperar a listagem do GitHub, contrariando a lógica de incerteza (exit 4)."}
{"achado":"R2","veredito":"AGREE","justificativa":"Timeout ou erro de rede em gh workflow run é tratado como recusa (exit 2) sem gravar a marca, risking um segundo redisparo indevido do mesmo SHA."}
{"achado":"R3","veredito":"AGREE","justificativa":"Apenas .gitkeep é excluído da varredura; arquivos de controle rastreados como .gitignore podem ser movidos no lote soltos, quebrando regras locais."}
VERDICTS>>>