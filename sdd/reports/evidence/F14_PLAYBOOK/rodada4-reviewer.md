**1. Veredito geral**

**APROVADO COM RESSALVAS**

A leitura do diff confirma os contratos centrais: colheita, aplicação, trava de invariantes, conferidor do bloco, fronteira de escrita, `copiar-docs.sh`, molde do handoff e consertos das pendências. Encontrei 5 defeitos, 1 MED e 4 LOW, todos fora do caminho principal e nenhum capaz de desfazer uma publicação ou deixar passar contagem inventada. As ressalvas são esses defeitos, o AT-038 ainda sem prova e o Verify Gate sem evidência no commit final.

**2. Conformidade com o DEFINE e o DESIGN**

**Limitações do material**
- O diff não traz o corpo de `anti_collapse`, o restante do `--comparar` da fronteira, o início de `despachar`, a função `aplicar` de `bin/sdd-open.sh` nem `sdd/playbook.md`. O que depende deles foi lido só pelo contrato e pelos testes.
- Não executei nada, porque a revisão é só de leitura. Os resultados de teste abaixo vêm do BUILD_REPORT.

| Item | Situação |
|---|---|
| AT-001 a AT-010 (colheita) | Cumpridos no código: leitura pelo cabeçalho, achados, sugestões, candidatos, promoção, saídas, `--desde` e trace. |
| AT-011 a AT-013, AT-042 (`--aplicar` e anti-collapse) | Cumpridos, inclusive stdout vazio em delta inválido e piso de 1 alterado. O R2 trata um caso de borda não previsto. |
| AT-014 a AT-019, AT-043 (invariantes) | Cumpridos: gramática, trava, `--cruzar`, `--aplicar-inv` e `--colher --inv`. |
| AT-020, AT-021 (conferidor) | Cumpridos: cobertura 1 para 1, `AUTO` por igualdade, selo, fronteira e `PERGUNTA` para contagem com `INV_PENDENTE`. |
| AT-022, AT-040, AT-041, AT-044 | Cumpridos no código. O R5 aponta uma lacuna de endurecimento no `--preparar`. |
| AT-023 a AT-025 (brief, contrato, 17b, exemplos) | O texto cumpre a ordem e as paradas. O limite de 1 redespacho não tem como ser conferido no caminho sem subagente (R4). |
| AT-026 a AT-028 (`copiar-docs.sh`) | Cumpridos, com 1 divergência na linha `→` do AT-027 (R3). |
| AT-029 a AT-032, AT-034 a AT-036 | Cumpridos no código e nos testes do diff. |
| AT-033 | O diff traz os consertos. O relatório fica fora do diff e só é citado pelo BUILD_REPORT. |
| AT-037 | O diff não toca `verify-gate.sh`, `report-lint.py`, `adversarial-review.sh` nem `sdd/hooks`. |
| AT-038 | Sem prova no material: o BUILD_REPORT marca `PENDENTE_PROVA`. O DESIGN prevê a execução depois do último conserto, então é pendência de entrega, não defeito do diff. |
| AT-039 | Só há citação de logs, que estão fora do diff. |
| AT-045 | Cumprido no código e nos testes do diff. |
| Verify Gate | Sem como confirmar neste diff. A evidência verde citada é de `eada1e2`, mas o diff traz consertos posteriores, das rodadas 1 a 3 da revisão real. O BUILD_REPORT também cita DEFINE v1.6 e DESIGN v1.4, enquanto os documentos estão em v1.7 e v1.5. |
| DESIGN × diff | Não achei divergência além das já registradas no ledger e no BUILD_REPORT. |

**3. Achados**

**R1** — `sdd/bin/playbook-curator.sh:88` · MED · PLAUSIBLE
- **Defeito:** o `reconfigure` do stdout não fixa `newline="\n"`, então um Python nativo do Windows grava `--aplicar` e `--aplicar-inv` com CRLF, embora o README declare suporte a Windows (Git Bash).
- **Cenário de falha:** com um `sdd/playbook.md` em LF e o delta `LM-001 ajudou+1`, o `novo.md` sai com todas as linhas em CRLF. A cópia por cima troca o fim de linha do arquivo inteiro num commit que deveria ser só de contagem.
- **Premissa não verificada:** o `python3` do Git Bash ser nativo do Windows e o `playbook-lint.sh` não normalizar CR. Se o lint não normalizar, o `--anti-collapse` veria todos os bullets como reescritos e bloquearia a curadoria.

**R2** — `sdd/bin/playbook-curator.sh:161` · LOW · CONFIRMED
- **Defeito:** `ler()` usa `errors="replace"`, e o `--aplicar` com delta real grava o texto já com os bytes inválidos trocados por U+FFFD. Só o caminho de delta vazio preserva os bytes.
- **Cenário de falha:** um playbook com um `ç` em Latin-1 no bullet `LM-007` recebe o delta `LM-001 ajudou+1`. A saída corrompe o texto do `LM-007` sem aviso e retorna exit 0, embora o delta nem cite esse bullet. Se só esse bullet contar como alterado, o novo piso do anti-collapse também deixa passar.

**R3** — `.agents/skills/sdd-new-session/scripts/copiar-docs.sh:138` · LOW · CONFIRMED
- **Defeito:** a precedência da linha `→` esconde a orientação do `PARECIDO` quando também há `IGNORADO`, contrariando o AT-027.
- **Cenário de falha:** com `DEFINE_RELATORIO_MENSAL_V2.md` parecido e `DESIGN_RELATORIO_MENSAL.md` sendo link no checkout principal, a seta fala só das linhas `IGNORADO`. Ela não menciona o parecido nem diz para onde copiar à mão.

**R4** — `.agents/skills/sdd-release/SKILL.md:314` · LOW · PLAUSIBLE
- **Defeito:** o limite de 1 redespacho depende da memória da sessão, e o caminho sem subagente troca de sessão a cada exit 40 sem instrução nem marcador que registre a reprovação anterior.
- **Cenário de falha:** o bloco é reprovado, o agente despacha de novo e para no exit 40. A sessão seguinte roda `--retomar`, que só informa se a colheita existe. Se o bloco for reprovado de novo, essa sessão pode tratá-lo como 1ª reprovação e redespachar, sem chegar a `Curadoria: FALHOU (bloco inválido)`.
- **Premissa não verificada:** o agente novo não inferir a tentativa anterior pelo campo `conferencia:` do brief, porque o texto não manda fazer essa leitura.

**R5** — `sdd/bin/playbook-curator.sh:368` · LOW · PLAUSIBLE
- **Defeito:** o `--preparar` aceita uma pasta de staging já existente com nome previsível, conferindo só se é link, sem verificar o dono nem as permissões.
- **Cenário de falha:** em máquina compartilhada com `/tmp` comum, outro usuário cria antes `sdd-curadoria-<hash>/<F>` com modo 777 e planta `AVAL-x.log` com `❌ LM-004` antes do selo. A colheita conta o arquivo como evidência legítima, e o selo aceita o que já estava lá. Se o curador confirmar a linha, a contagem pode entrar como `AUTO`.
- **Premissa não verificada:** a máquina ser multiusuário e não ter `TMPDIR` exclusivo por usuário.

**4. Bloco de vereditos**

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/playbook-curator.sh","linha":88,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"Sem newline fixo no stdout, Python nativo do Windows grava --aplicar e --aplicar-inv em CRLF e altera o arquivo inteiro."}
{"achado":"R2","arquivo":"sdd/bin/playbook-curator.sh","linha":161,"severidade":"LOW","confianca":"CONFIRMED","resumo":"ler() com errors=replace faz o --aplicar com delta real trocar bytes inválidos por U+FFFD sem aviso."}
{"achado":"R3","arquivo":".agents/skills/sdd-new-session/scripts/copiar-docs.sh","linha":138,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Com IGNORADO e PARECIDO juntos, a linha de seta não diz onde copiar à mão, contrariando o AT-027."}
{"achado":"R4","arquivo":".agents/skills/sdd-release/SKILL.md","linha":314,"severidade":"LOW","confianca":"PLAUSIBLE","resumo":"No caminho sem subagente, nada registra a reprovação anterior entre sessões, e o limite de 1 redespacho pode não valer."}
{"achado":"R5","arquivo":"sdd/bin/playbook-curator.sh","linha":368,"severidade":"LOW","confianca":"PLAUSIBLE","resumo":"O --preparar aceita pasta de staging previsível já existente sem conferir dono nem permissões, permitindo evidência plantada antes do selo."}
VERDICTS>>>