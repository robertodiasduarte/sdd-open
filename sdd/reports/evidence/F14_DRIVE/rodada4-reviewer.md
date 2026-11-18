## 1. Veredito geral

**APROVADO COM RESSALVAS**

Li os scripts e não encontrei defeito HIGH nem MED. A barreira de publicação, a contagem de rodadas, a impressão digital, a regra de redisparo e a proteção pela ficha estão corretas no código. Restam 5 achados LOW: 1 em que um `git fetch` falho vira erro de uso no `deploy-do-sha.sh`, 1 instrução que manda rodar o gate sem `--fundo`, 1 relatório com motivo velho, 1 lacuna de teste no AT-006 e 1 documento PT sem a seção nova. A ressalva maior está fora do código: o AT-038 segue `PENDENTE_PROVA`, e isso, com a revisão real, o CI e o OK da pessoa, ainda bloqueia a `v2.7.0`.

## 2. Conformidade com o DEFINE e o DESIGN

**Limitações do material**
- A revisão foi só por leitura, sem rodar nada. Os logs citados no BUILD_REPORT (`verify-gate-52f0830.log`, baseline, sabotagens, `AT-038.log`) não vieram no material.
- `verify-gate.sh`, `sdd-fluxo.sh`, `avaliador-guard.sh` e `playbook-curator.sh` chegaram só como hunks. `design-lint.py`, `report-lint.py` e `apoio.py` não vieram.

| Itens | Situação | Observação |
|---|---|---|
| AT-001 a AT-005, AT-007 a AT-018 | Conforme no código | Inclui ordem das ações, HEAD anterior ao gate, trava, orçamento, estado por forma inteira e barreira testada com `git` e `gh` de mentira. |
| AT-006 | Conforme em parte | A semeadura, a linha nova e o PROGRESS sem linhas estão cobertos. O caso "manifest sem linha" não tem asserção (R4). |
| AT-019 | Conforme, com 1 divergência | Nomes, exits e perguntas batem. A ação `COMMITAR` manda chamar `verificar` sem `--fundo` (R2). |
| AT-020, AT-021 | Conforme | `despachar executor-drive`, aviso das paradas e passo 0b na ordem pedida. |
| AT-022 a AT-026 | Conforme, com 1 ressalva | Filtros, substituto, redisparo único e ausência de `gh run rerun` estão corretos. O exit 64 também sai quando o fetch falhou (R1). |
| AT-027, AT-031, AT-035 | Conforme | Item 10, regra do changelog, 15b e slots. |
| AT-028 a AT-030 | Conforme | Simulação, `git mv` por lote e proteção pela ficha. |
| AT-032 a AT-034 | Conforme | O teste com `sdd/featuresx/a.md` indica que a guarda lista arquivo a arquivo. O filtro da colheita segue a forma exata da Decision 11. |
| AT-036 | Conforme | Documentos, roadmap, 19 skills e manifest. |
| AT-037 | Conforme nos hunks | `--checar` e `--drive` são aditivos. A prova completa depende da suíte, que não foi rodada aqui. |
| AT-038 | **Pendente** | O BUILD_REPORT registra `PENDENTE_PROVA`, e a evidência está fora do diff. |
| Verify Gate | Não verificável aqui | O BUILD_REPORT declara verde em `52f0830`, sem o log no material. |
| Success Criteria de CI, revisão real e Release | Pendentes | O próprio BUILD_REPORT os deixa em aberto. |
| Decisions 1 a 12 | Sem divergência material | O código segue o DESIGN v1.7, e os desvios conhecidos estão no Drift Detected. |

## 3. Achados

**R1** — `sdd/bin/deploy-do-sha.sh:258` · LOW · CONFIRMED
- **Defeito:** o exit do `git fetch` é ignorado na resolução do `--commit`, e uma falha de rede vira "commit não encontrado, nem depois de git fetch", com exit 64.
- **Cenário:** no caminho do PR, o SHA do merge ainda não está no clone e o fetch falha por rede ou credencial. O script sai 64 sem ter consultado o remoto, e o item 10 orienta a conferir o SHA ou o `sdd/bin/`. O certo seria "ainda não sei" (exit 4), como já ocorre quando o fetch estoura o tempo.

**R2** — `.agents/skills/sdd-drive/SKILL.md:80` · LOW · CONFIRMED
- **Defeito:** a ação `COMMITAR` manda chamar `verificar` sem `--fundo`, na skill e na seta do script (`sdd/bin/sdd-drive.sh:97`), embora a ação `VERIFICAR` use `--fundo` por causa do limite de comando do agente.
- **Cenário:** depois de commitar, o agente chama `verificar` num projeto com gate de 17 minutos, e o gate roda em primeiro plano. Se o agente corta o comando no limite dele, o resultado se perde. Se o gate ficar órfão, ele pode rodar junto com o seguinte, o limite que `docs/sdd-drive.md` declara.

**R3** — `sdd/bin/sdd-drive.sh:970` · LOW · CONFIRMED
- **Defeito:** `recibo` reescreve o relatório com `st["motivo"]`, mas uma parada resolvida sem `--resume` nunca limpa esse campo.
- **Cenário:** `proximo` para em `clarificacao-pendente`, a pessoa resolve o DEFINE e o `proximo` seguinte continua normalmente. Um `recibo` feito depois grava no `DRIVE_REPORT` a frase "O DEFINE ainda tem dúvida aberta…" e `| Motivo | clarificacao-pendente |` com a execução em andamento. O mesmo vale para `gate-alterado` depois de restaurar o comando antigo.

**R4** — `tests/test_drive.py:362` · LOW · PLAUSIBLE
- **Defeito:** o caso "manifest sem linha" do AT-006 não tem asserção: o teste ignora o resultado do `iniciar` e troca o DESIGN antes de conferir, e o self-test também não cobre o caso.
- **Cenário:** com um DESIGN sem linhas no File Manifest, o AT-006 exige `estado-invalido`. Se o `design-lint.py` reprovar esse DESIGN, o `seguir` para antes de `tarefas()` e o script responde `ACAO: DESIGN`, sem que nenhum teste acuse. Premissa não verificada: o comportamento do `design-lint.py` com manifest vazio, que não veio no material.

**R5** — `docs/verify-gate-contract.md:74` · LOW · CONFIRMED
- **Defeito:** a seção do `--checar` entrou só no documento em inglês, e `docs/pt-BR/verify-gate-contract.md` não está no diff.
- **Cenário:** quem lê o contrato em português não encontra a opção nem seus exits `0`, `5` e `64`, embora `sdd-drive` dependa dela na entrada.

## 4. Bloco de vereditos

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/deploy-do-sha.sh","linha":258,"severidade":"LOW","confianca":"CONFIRMED","resumo":"git fetch que falha na resolução do commit vira exit 64 de commit desconhecido, em vez de exit 4."}
{"achado":"R2","arquivo":".agents/skills/sdd-drive/SKILL.md","linha":80,"severidade":"LOW","confianca":"CONFIRMED","resumo":"A ação COMMITAR manda chamar verificar sem --fundo, e um gate longo pode ser cortado pelo limite de comando do agente."}
{"achado":"R3","arquivo":"sdd/bin/sdd-drive.sh","linha":970,"severidade":"LOW","confianca":"CONFIRMED","resumo":"recibo reescreve o DRIVE_REPORT com um motivo de parada já resolvida, porque proximo não limpa esse campo."}
{"achado":"R4","arquivo":"tests/test_drive.py","linha":362,"severidade":"LOW","confianca":"PLAUSIBLE","resumo":"O caso de manifest sem linha do AT-006 não tem asserção, e o script pode responder DESIGN em vez de estado-invalido."}
{"achado":"R5","arquivo":"docs/verify-gate-contract.md","linha":74,"severidade":"LOW","confianca":"CONFIRMED","resumo":"A seção do --checar entrou só em inglês, sem a versão em docs/pt-BR/verify-gate-contract.md."}
VERDICTS>>>