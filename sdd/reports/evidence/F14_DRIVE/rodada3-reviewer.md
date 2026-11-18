**1. Veredito geral**

APROVADO COM RESSALVAS

O diff cumpre, pela leitura, os contratos de `sdd-drive.sh`, `sdd-archive.py`, guarda do avaliador, colheita e textos. A revisão não achou caminho que publique, que conte rodada errado ou que dê verde a um commit não testado. As ressalvas são dois defeitos MED no `deploy-do-sha.sh`, que afetam o que a release diz depois do push ou o limite de redisparo, e um LOW no archive. A aprovação vale para o código. A publicação ainda depende da prova do AT-038 e dos demais itens pendentes listados na parte 2.

**2. Conformidade com o DEFINE e o DESIGN**

Nada foi executado: "conforme" abaixo significa conforme pela leitura do diff.

| Item | Situação |
|---|---|
| AT-001 a AT-018 (drive) | Conforme. Verbos, ordem das ações, repetição, trava, impressão digital, orçamento, relatório, barreira e self-test batem com o DEFINE. |
| AT-019 a AT-021 (skill, parada sem subagente, 0b) | Conforme. |
| AT-022 a AT-026 (deploy) | Conforme nos desfechos declarados, com lacunas em R1 (run `cancelled` sem substituto listado) e R2 (falha do dispatch que não é recusa). |
| AT-027 e AT-031 (item 10, changelog, 15b) | Conforme. |
| AT-028 a AT-030 (archive) | Conforme, com a ressalva de R3. |
| AT-032 a AT-034 (guarda e colheita) | Conforme. |
| AT-035 a AT-037 (slots, docs, contratos anteriores) | Conforme no que o diff mostra. |
| AT-038 (agente real) | Não cumprido neste material: o BUILD_REPORT o marca `PENDENTE_PROVA`, e o log não veio no diff. |
| Verify Gate e critérios de sucesso | Não verificáveis aqui. O BUILD_REPORT cita verde em `52f0830`, mas a revisão real, o `--conferir`, o CI e a Release `v2.7.0` constam como pendentes. |

Divergências sem efeito prático, que não viraram achado:
- **Orçamento:** a Decision 3 do DESIGN diz que "todo verbo" para em `orcamento-rodadas`, mas `bloqueio`, `recibo` e `aguardar` não param. O código segue a lista do AT-012.
- **Frases fixas:** o AT-017 situa os literais em `tests/test_f14_drive_textos.py`, mas eles estão em `tests/test_drive.py` e são importados.
- **Documentação:** `--checar` entrou em `docs/verify-gate-contract.md`, e o par `docs/pt-BR/verify-gate-contract.md` não aparece no diff.
- **BUILD_REPORT:** ele cita DEFINE v1.6 e DESIGN v1.5, enquanto os documentos já estão em v1.8 e v1.7.

Limitações do material:
- `verify-gate.sh`, `sdd-fluxo.sh` e `sdd-release/SKILL.md` vieram só em trechos.
- As evidências (baseline, sabotagens, logs do gate) não vieram no diff.

**3. Achados**

**R1** — `sdd/bin/deploy-do-sha.sh:340`
- **Severidade e confiança:** MED · PLAUSIBLE
- **Defeito:** um run próprio `cancelled` ou `timed_out`, sem run mais novo na lista, sai 2 na primeira consulta, sem janela de espera e sem conferir se a ponta da branch já contém o commit.
- **Cenário de falha:** dois pushes seguidos num workflow com `cancel-in-progress` cancelam o run de X, e o run do commit seguinte ainda não aparece em `gh run list --branch`. O script imprime `🔴 não está no ar — … nenhum deploy mais novo contém X` e encerra, embora o substituto possa publicar X segundos depois. Sem a saída 4, a repetição prevista no item 10 também não acontece.
- **Premissa não verificada:** a demora real da listagem do GitHub. O próprio script já admite atraso na listagem por commit.

**R2** — `sdd/bin/deploy-do-sha.sh:376`
- **Severidade e confiança:** MED · CONFIRMED
- **Defeito:** qualquer falha de `gh workflow run`, inclusive `TimeoutExpired`, `OSError` ou HTTP 5xx, é tratada como recusa do GitHub, sai 2 e não grava a marca do redisparo.
- **Cenário de falha:**
  1. O dispatch passa dos 60 s depois de o GitHub tê-lo aceitado, ou devolve 502.
  2. O script diz que o GitHub recusou e que o workflow precisa de `workflow_dispatch`, o que é falso e contraria o Pattern 4 ("nunca desfecho").
  3. Se o script rodar de novo antes de o run novo ser listado, não há marca nem `workflow_dispatch` na lista, e ele dispara uma segunda vez, violando o limite de 1 redisparo por SHA (AT-024).

**R3** — `sdd/bin/sdd-archive.py:194`
- **Severidade e confiança:** LOW · PLAUSIBLE
- **Defeito:** só `.gitkeep` fica de fora da varredura, então arquivo de controle rastreado nas pastas de documento entra no lote `soltos` como se fosse report ou review.
- **Cenário de falha:** um projeto mantém `sdd/reports/.gitignore` sem mudança há mais de 60 dias. `--lote soltos --aplicar` o move para `sdd/archive/_REPORTS_<AAAA-MM>/.gitignore`. Depois do commit, as regras deixam de valer em `sdd/reports/`, e o que elas ignoravam aparece como não rastreado.
- **Premissa não verificada:** que projetos reais mantenham esse arquivo nessa pasta.

**4. Bloco de vereditos**

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/deploy-do-sha.sh","linha":340,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"Run próprio cancelled ou timed_out sem run mais novo listado sai 2 na primeira consulta, sem espera nem conferência da ponta, e pode negar um substituto prestes a publicar."}
{"achado":"R2","arquivo":"sdd/bin/deploy-do-sha.sh","linha":376,"severidade":"MED","confianca":"CONFIRMED","resumo":"Timeout ou erro 5xx em gh workflow run vira recusa com exit 2 e sem marca, com diagnóstico falso e risco de segundo redisparo do mesmo SHA."}
{"achado":"R3","arquivo":"sdd/bin/sdd-archive.py","linha":194,"severidade":"LOW","confianca":"PLAUSIBLE","resumo":"Só .gitkeep é excluído da varredura, então um .gitignore rastreado em sdd/reports pode ser movido no lote soltos e deixar de valer."}
VERDICTS>>>