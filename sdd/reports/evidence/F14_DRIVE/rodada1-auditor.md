### 1. Auditoria por achado

**R1@claude** — `sdd/bin/sdd-drive.sh:828` · HIGH · PLAUSIBLE
**Veredito:** DISAGREE_EVIDENCE
**Justificativa:** A revisão cita erroneamente a documentação. `docs/cli-conventions.md` afirma que o exit `3` é "inconclusivo" e que o `--strict` é o que remapeia `3/4/5 → 1`. Sem `--strict`, o exit permanece `3`. O código em `sdd-drive.sh:846` trata corretamente `rc in (3, 4, 5, 64)` como `gate-inconclusivo`, não como verde.

**R2@claude** — `sdd/bin/sdd-drive.sh:721` · MED · CONFIRMED
**Veredito:** DISAGREE_EVIDENCE
**Justificativa:** A Decision 4 do DESIGN estabelece explicitamente que "`--resume` não conta" para o teto de repetições. O código em `sdd-drive.sh:721` zera o contador de propósito (`st["repeticao"] = dict(chave="", n=0)`), alinhado à decisão de projeto de não penalizar a retomada após queda de sessão.

**R3@claude** — `sdd/bin/sdd-drive.sh:619` · MED · CONFIRMED
**Veredito:** AGREE
**Justificativa:** A Decision 3 exige que "a mesma lista [de documentos] vale para o que está sujo na árvore e para o `git diff` entre commits". Contudo, `so_documentos` e `proxima` consultam apenas o `git diff` entre commits, ignorando mudanças não commitadas na árvore de trabalho, o que pode levar a ações incorretas com código sujo.

**R4@claude** — `sdd/bin/sdd-drive.sh:716` · MED · CONFIRMED
**Veredito:** AGREE
**Justificativa:** O AT-011 e a Decision 5 determinam que a troca de gate deve ser registrada no relatório. O código em `cmd_resume` e `relatorio` grava apenas o `cmd` (`st["gate_cmd"]`), omitindo mudanças em `kind`, `pass_when`, `threshold` ou `manual_fallback`, mesmo que a impressão digital as capture.

**R5@claude** — `.agents/skills/sdd-drive/SKILL.md:90` · MED · PLAUSIBLE
**Veredito:** DISAGREE_CONCERN
**Justificativa:** A premissa de que `cmd_despachar` falharia ao copiar sobre o mesmo arquivo não pode ser verificada, pois a implementação de `cmd_despachar` no `sdd-fluxo.sh` não consta no diff fornecido.

**R6@claude** — `.agents/skills/sdd-release/SKILL.md:229` · MED · PLAUSIBLE
**Veredito:** DISAGREE_CONCERN
**Justificativa:** Não há evidência no diff de que outro passo da release faça o `git fetch` antes do item 10, mas também não há prova definitiva de que o clone local não conheça o SHA do merge no momento da verificação.

**R7@claude** — `sdd/bin/sdd-drive.sh:530` · MED · PLAUSIBLE
**Veredito:** DISAGREE_EVIDENCE
**Justificativa:** A documentação oficial do Python para `os.kill` especifica que, no Windows, se o sinal for `0`, a função verifica se o processo está vivo, não enviando `CTRL_C_EVENT`. O comportamento descrito na revisão é incorreto para a linguagem.

**R8@claude** — `sdd/bin/sdd-drive.sh:480` · LOW · CONFIRMED
**Veredito:** AGREE
**Justificativa:** O regex que extrai tarefas do `PROGRESS` não prevê anotações de erro na linha, o que pode fazer o script reconhecer o mesmo arquivo como uma nova tarefa pendente.

**R9@claude** — `sdd/bin/sdd-drive.sh:842` · LOW · CONFIRMED
**Veredito:** AGREE
**Justificativa:** O fim da execução do gate limpa `motivo` e `detalhe` no estado recarregado, o que apaga um eventual `bloqueio-humano` gravado por outra sessão enquanto o gate rodava em segundo plano.

**R10@claude** — `sdd/bin/sdd-drive.sh:536` · LOW · CONFIRMED
**Veredito:** AGREE
**Justificativa:** A trava é criada vazia e o PID é escrito em seguida. Uma janela de corrida permite que um processo concorrente leia o arquivo vazio, considere a trava morta e a apague antes da escrita do PID.

**R11@claude** — `sdd/bin/playbook-curator.sh:100` · LOW · CONFIRMED
**Veredito:** AGREE
**Justificativa:** O regex `NAO_E_ACHADO` diverge do AT-034 ao descartar linhas com prefixo `+ ` e restringir o diagnóstico de erro a arquivos `.md`, o que pode ignorar achados reais ou contar diagnósticos de outros arquivos.

**R1@openrouter-deepseek-deepseek-v4-pro** — `sdd/bin/verify-gate.sh:258` · MED · PLAUSIBLE
**Veredito:** AGREE
**Justificativa:** O `--checar` valida apenas se o `cmd` está vazio ou começa com `N/A`, mas não verifica se o comando é de fato executável (ex: usando `command -v` ou `sh -n`). Um DEFINE com `cmd: "nao-existe"` passaria na checagem, violando o AT-002.

### 2. Achados novos

Não há achados novos de severidade HIGH ou MED que as revisões não tenham citado.

### 3. Bloco de vereditos

<<<VERDICTS
{"achado":"R1@claude","veredito":"DISAGREE_EVIDENCE","justificativa":"A documentação diz que o exit 3 é inconclusivo e o --strict remapeia para 1; o script trata o exit 3 corretamente como gate-inconclusivo."}
{"achado":"R2@claude","veredito":"DISAGREE_EVIDENCE","justificativa":"A Decision 4 estabelece explicitamente que '--resume não conta' para o contador de repetição, e o código zera o contador de propósito."}
{"achado":"R3@claude","veredito":"AGREE","justificativa":"A Decision 3 exige que a árvore suja seja considerada, mas 'so_documentos' e 'proxima' só consultam o 'git diff' entre commits."}
{"achado":"R4@claude","veredito":"AGREE","justificativa":"O AT-011 e a Decision 5 pedem que a troca seja registrada no relatório, mas 'cmd_resume' e 'relatorio' gravam apenas o 'cmd', omitindo outros campos do bloco."}
{"achado":"R5@claude","veredito":"DISAGREE_CONCERN","justificativa":"A implementação de 'cmd_despachar' não está no diff, então não há evidência para confirmar se a cópia sobre o mesmo arquivo falha."}
{"achado":"R6@claude","veredito":"DISAGREE_CONCERN","justificativa":"Não há evidência no diff de que outro passo faça o fetch antes do item 10, mas também não há prova de que o clone local não conheça o SHA do merge."}
{"achado":"R7@claude","veredito":"DISAGREE_EVIDENCE","justificativa":"A documentação do Python confirma que 'os.kill(pid, 0)' no Windows verifica se o processo está vivo, não envia CTRL_C_EVENT."}
{"achado":"R8@claude","veredito":"AGREE","justificativa":"O regex do PROGRESS não prevê anotações de erro, o que pode duplicar tarefas."}
{"achado":"R9@claude","veredito":"AGREE","justificativa":"O fim do gate limpa 'motivo' e 'detalhe', apagando um bloqueio gravado durante a execução."}
{"achado":"R10@claude","veredito":"AGREE","justificativa":"A trava é criada vazia e um processo concorrente pode apagá-la antes de o PID ser escrito."}
{"achado":"R11@claude","veredito":"AGREE","justificativa":"O filtro da colheita diverge do AT-034 ao descartar linhas com '+' e restringir o diagnóstico a arquivos .md."}
{"achado":"R1@openrouter-deepseek-deepseek-v4-pro","veredito":"AGREE","justificativa":"O '--checar' só valida se o 'cmd' está vazio ou é 'N/A', mas não verifica se o comando é de fato executável, violando o AT-002."}
VERDICTS>>>