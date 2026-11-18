**1. Veredito geral**

**APROVADO COM RESSALVAS**

O diff entrega as peças prometidas, e os caminhos centrais do drive, do `deploy-do-sha.sh` e do `sdd-archive.py` batem com o contrato na leitura. Não encontrei publicação indevida nem falso "no ar". Não há HIGH confirmado. Há 1 HIGH plausível, que se confere em minutos e precisa ser descartado antes da tag: o gate roda sem `--strict`, e um texto do próprio pacote diz que o exit 3 devolve 0. Há 3 MED confirmados: o teto de repetição não vale sem subagente, `proximo` ignora a árvore suja e o aceite de gate novo não registra o que mudou. O AT-038 segue pendente.

**2. Conformidade com o DEFINE e o DESIGN**

Limitações do material:
- `finalizar` e a checagem de marcador do `verify-gate.sh`, `cmd_despachar`, `tests/apoio.py` e os logs de evidência não vieram no diff.
- O verde do Verify Gate e o CI não podem ser confirmados aqui; só há o relato do BUILD_REPORT (exit 0 em `ff5c539`).

| Item | Situação |
|---|---|
| AT-001 a AT-004 | Conforme na leitura |
| AT-005 | Diverge com árvore suja (R3) |
| AT-006 | Conforme, salvo a tarefa duplicada em R8 |
| AT-007 | Cumprido com subagente; não vale no caminho sem subagente (R2) |
| AT-008 | Conforme no caminho comum; há corrida estreita na trava (R10) e dependência de plataforma (R7) |
| AT-009 | Conforme com gate de mentira; o caminho real do exit 3 depende da premissa de R1 |
| AT-010 | Conforme em `verificar` e `concluir` |
| AT-011 | Para corretamente, mas o relatório não registra troca fora do `cmd` (R4) |
| AT-012 a AT-019 | Conforme na leitura; em AT-016, `bloqueio` feito durante o gate se perde (R9) |
| AT-020 | O caminho escrito na skill não é o testado (R5) |
| AT-021 | Conforme |
| AT-022 a AT-026 | Conforme na leitura do `deploy-do-sha.sh` |
| AT-027 | Conforme no texto; lacuna no caminho do PR (R6) |
| AT-028 a AT-033 | Conforme na leitura |
| AT-034 | Implementação diverge da forma fixada no DEFINE e no DESIGN (R11) |
| AT-035 a AT-037 | Conforme na leitura do diff |
| AT-038 | Não cumprido ainda: `PENDENTE_PROVA` no BUILD_REPORT |
| Verify Gate | Bloco do DEFINE inalterado no material; resultado não verificável aqui |
| Critérios de release | Prova real, CI e Release `v2.7.0` seguem abertos, como o próprio BUILD_REPORT declara |

**3. Achados**

**R1** — `sdd/bin/sdd-drive.sh:828` · HIGH · PLAUSIBLE
- **Defeito:** `verificar` roda o gate sem `--strict` e trata exit 0 como verde, enquanto `docs/cli-conventions.md` diz que o exit 3 "devolve `0`… sem `--strict`".
- **Cenário:** o `cmd` depende de uma ferramenta ausente, o gate fica inconclusivo e o `verify-gate.sh` sai 0. O log recebe `[exit=0]`, e o fluxo segue por `AVALIAR_E_RELATAR` até `gate-verde`.
- **Premissa não verificada:** o `finalizar` não está no diff, e a mesma tabela da documentação diz `3`, então o texto pode só estar velho. O self-test com manual-ux espera exit 4 do gate real, o que enfraquece a suspeita.
- **Cobertura:** nem os testes nem o self-test passam pelo caminho real, porque os stubs e o patch fazem `exit 3` direto.

**R2** — `sdd/bin/sdd-drive.sh:721` · MED · CONFIRMED
- **Defeito:** `--resume` zera o contador de repetição, e o caminho sem subagente sempre volta por `--resume`, então o teto da 3ª repetição nunca dispara ali.
- **Cenário:** o executor falha sem commit e sem `[x]`, e o ciclo vira `aguardar` (exit 40), sessão nova, `--resume`, que imprime a mesma `RODADA`. O contador nunca chega a 3, e `bloqueio-humano` nunca aparece.

**R3** — `sdd/bin/sdd-drive.sh:619` · MED · CONFIRMED
- **Defeito:** `proxima` compara só commits e ignora a árvore suja, embora a Decision 3 aplique "só documentos" também ao que está sujo.
- **Cenário com verde:** depois do verde, `src/a.py` é editado sem commit, e `proximo` responde `AVALIAR_E_RELATAR` em vez de `VERIFICAR`. O avaliador e o relatório rodam sobre código não provado, até o `concluir` barrar com `COMMITAR`.
- **Cenário com vermelho:** o conserto ainda sem commit recebe `CORRIGIR` repetido e chega a `bloqueio-humano` na 3ª chamada.

**R4** — `sdd/bin/sdd-drive.sh:716` · MED · CONFIRMED
- **Defeito:** a troca aceita grava apenas o `cmd`, embora a impressão digital cubra também `kind`, `pass_when`, `threshold` e `manual_fallback`.
- **Cenário:** `threshold` cai de `0.9` para `0.1` e a pessoa aceita com `--aceitar-gate-novo`. O relatório registra "de `x` para `x`", sem dizer o que enfraqueceu, contra o AT-011 e a Decision 5.

**R5** — `.agents/skills/sdd-drive/SKILL.md:90` · MED · PLAUSIBLE
- **Defeito:** a skill grava o brief no caminho de destino do `despachar` e passa esse mesmo caminho como origem, caso que os testes não exercitam (usam `brief.md`).
- **Cenário:** sem subagente, se o `despachar` copiar com `cp`, a cópia sobre o mesmo arquivo falha. `aguardar` repete o erro em vez do exit 40, e nenhuma tarefa é despachada nesse caminho.
- **Premissa não verificada:** a implementação de `cmd_despachar` não veio no diff.

**R6** — `.agents/skills/sdd-release/SKILL.md:229` · MED · PLAUSIBLE
- **Defeito:** o item 10 manda usar o SHA do merge no caminho do PR, sem buscá-lo antes, e o script recusa SHA desconhecido com exit 64.
- **Cenário:** o PR é mesclado no GitHub e o clone local ainda não conhece o merge. O script sai 64 com `commit não encontrado`, e a tabela orienta rodar o `doctor` e o `init`, o que não resolve. O deploy fica sem verificação.
- **Premissa não verificada:** o material não mostra se outro passo faz o fetch antes do item 10.

**R7** — `sdd/bin/sdd-drive.sh:530` · MED · PLAUSIBLE
- **Defeito:** a detecção de gate vivo usa `os.kill(pid, 0)`, que no Python nativo do Windows significa enviar `CTRL_C_EVENT`, não testar o processo.
- **Cenário:** no Git Bash com Python nativo, a chamada pode falhar e a trava é apagada com o gate vivo, abrindo um segundo gate, ou pode interromper o próprio gate. Além disso, `start_new_session` não destaca o processo nessa plataforma.
- **Premissa não verificada:** o comportamento nesse ambiente, que o DESIGN considera suportado, não é coberto pelo CI declarado.

**R8** — `sdd/bin/sdd-drive.sh:480` · LOW · CONFIRMED
- **Defeito:** a conferência do manifest só aceita certos separadores depois do nome, mas o brief do executor manda anotar o erro na linha sem fixar o formato.
- **Cenário:** com `- [ ] a: erro X`, o script não reconhece `a` e acrescenta outro `- [ ] a`. O total de tarefas cresce e surge uma tarefa fantasma.

**R9** — `sdd/bin/sdd-drive.sh:842` · LOW · CONFIRMED
- **Defeito:** ao terminar, o gate limpa `motivo` e `detalhe` no estado recarregado, apagando um bloqueio gravado enquanto ele rodava.
- **Cenário:** com `verificar --fundo` em andamento, a pessoa roda `bloqueio`. Quando o gate termina, `proximo` segue normalmente sem exigir `--resume`, e no caso verde o relatório continua dizendo `bloqueio-humano`.

**R10** — `sdd/bin/sdd-drive.sh:536` · LOW · CONFIRMED
- **Defeito:** a trava é criada vazia e preenchida depois, e `gate_rodando` trata arquivo vazio como trava morta e o apaga.
- **Cenário:** um `proximo` ou `verificar` concorrente lê nessa janela estreita e remove a trava recém-criada. Outro `verificar` pode então rodar um segundo gate, contra o AT-008.

**R11** — `sdd/bin/playbook-curator.sh:100` · LOW · CONFIRMED
- **Defeito:** o filtro diverge do AT-034 e da Decision 11: acrescenta `+ ` e restringe o diagnóstico `<arquivo>:<linha>: ❌ ` a arquivos `.md`.
- **Cenário:** um achado real como `+ ❌ repetiu LM-002` deixa de produzir `DELTA LM-002 mordeu+1`. Já um diagnóstico `/tmp/x.yaml:3: ❌ LM-001` passa a contar como achado.

**4. Bloco de vereditos**

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/sdd-drive.sh","linha":828,"severidade":"HIGH","confianca":"PLAUSIBLE","resumo":"O gate roda sem --strict e exit 0 vale como verde, enquanto a documentação diz que o exit 3 devolve 0 sem --strict."}
{"achado":"R2","arquivo":"sdd/bin/sdd-drive.sh","linha":721,"severidade":"MED","confianca":"CONFIRMED","resumo":"O --resume zera o contador de repetição e anula o teto da 3ª repetição no caminho sem subagente."}
{"achado":"R3","arquivo":"sdd/bin/sdd-drive.sh","linha":619,"severidade":"MED","confianca":"CONFIRMED","resumo":"A próxima ação ignora a árvore suja e responde AVALIAR_E_RELATAR ou CORRIGIR com código sem commit."}
{"achado":"R4","arquivo":"sdd/bin/sdd-drive.sh","linha":716,"severidade":"MED","confianca":"CONFIRMED","resumo":"O aceite de gate novo registra só o cmd e omite mudanças nos outros campos do bloco."}
{"achado":"R5","arquivo":".agents/skills/sdd-drive/SKILL.md","linha":90,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"A skill passa ao despachar o mesmo caminho como origem e destino do brief, caso não testado que pode falhar na cópia."}
{"achado":"R6","arquivo":".agents/skills/sdd-release/SKILL.md","linha":229,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"No caminho do PR, o SHA do merge pode não existir no clone local, e o exit 64 traz orientação que não resolve."}
{"achado":"R7","arquivo":"sdd/bin/sdd-drive.sh","linha":530,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"O os.kill com sinal 0 não testa processo no Python nativo do Windows e pode liberar a trava ou interromper o gate."}
{"achado":"R8","arquivo":"sdd/bin/sdd-drive.sh","linha":480,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Uma anotação de erro em formato não previsto no PROGRESS cria uma tarefa duplicada."}
{"achado":"R9","arquivo":"sdd/bin/sdd-drive.sh","linha":842,"severidade":"LOW","confianca":"CONFIRMED","resumo":"O fim do gate apaga um bloqueio gravado enquanto ele rodava."}
{"achado":"R10","arquivo":"sdd/bin/sdd-drive.sh","linha":536,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Uma trava recém-criada e ainda vazia pode ser apagada por um processo concorrente, permitindo um segundo gate."}
{"achado":"R11","arquivo":"sdd/bin/playbook-curator.sh","linha":100,"severidade":"LOW","confianca":"CONFIRMED","resumo":"O filtro da colheita diverge do AT-034: descarta linhas com prefixo + e conta diagnóstico de arquivo que não é md."}
VERDICTS>>>