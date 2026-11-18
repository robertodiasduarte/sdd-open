### 1. Auditoria por achado

**R1** — **AGREE**. A chave da repetição em `sdd/bin/sdd-drive.sh:773` inclui o `detalhe`, que contém a linha do `PROGRESS` com a anotação de erro. Isso faz o contador resetar a cada anotação diferente, impedindo a parada do AT-007.

**R2** — **AGREE**. O DESIGN promete recusar links que saem da raiz para estado e relatório, mas `sdd/bin/sdd-drive.sh:154` só verifica o `DEFINE`. Se `sdd/reports/` for um symlink para fora, os arquivos serão gravados fora do repositório.

**R3** — **DISAGREE_CONCERN**. O item 10 da `sdd-release` roda após o push (passo 9), não no worktree temporário do passo 5 (que é limpo no passo 12). O agente geralmente está na frente original, onde o `sdd/config.yaml` existe. A premissa de que roda no worktree temporário não é sustentada pelo contexto.

**R4** — **AGREE**. Em `sdd/bin/sdd-drive.sh:881`, o `detalhe` da próxima ação é sobrescrito por uma frase fixa após o gate, perdendo a lista de arquivos do `COMMITAR` ou a tarefa do `RODADA`.

**R5** — **DISAGREE_EVIDENCE**. O `verificar` recarrega o estado do disco após o gate (`st = carrega(p)` em `sdd/bin/sdd-drive.sh:943`), então não perde o que foi gravado por um `--resume` concorrente.

**R6** — **AGREE**. A função `ler` em `sdd/bin/sdd-drive.sh:659` usa `errors="replace"`, permitindo que DEFINEs não UTF-8 passem sem gerar `define-invalido`, contrariando o Error Handling do DESIGN.

### 2. Achados novos

**N1** — `sdd/bin/deploy-do-sha.sh:165` — **MED** — A função `contem` não verifica o `returncode` do `git fetch` antes de confiar no `git merge-base`. Se o `fetch` falhar, o `merge-base` pode retornar 1 (não ancestral) com o clone desatualizado, fazendo o script concluir "não contém" e falhar o deploy (exit 2), violando o AT-023 e o DESIGN ("Ancestral desconhecido fica em espera").

### 3. Bloco de vereditos

<<<VERDICTS
{"achado":"R1","veredito":"AGREE","justificativa":"A chave da repetição inclui o detalhe com a anotação do PROGRESS, resetando o contador e impedindo a parada do AT-007."}
{"achado":"R2","veredito":"AGREE","justificativa":"O código só verifica o realpath do DEFINE, permitindo que symlinks em sdd/reports/ gravem estado e relatório fora do repositório."}
{"achado":"R3","veredito":"DISAGREE_CONCERN","justificativa":"O item 10 roda após o push, não no worktree temporário do passo 5; a premissa de que o config.yaml não estará disponível não é sustentada."}
{"achado":"R4","veredito":"AGREE","justificativa":"A frase fixa sobrescreve o detalhe da próxima ação, perdendo a lista de arquivos do COMMITAR e a tarefa do RODADA."}
{"achado":"R5","veredito":"DISAGREE_EVIDENCE","justificativa":"O verificar recarrega o estado do disco após o gate (st = carrega(p)), não perdendo o que foi gravado por um --resume concorrente."}
{"achado":"R6","veredito":"AGREE","justificativa":"A função ler usa errors='replace', permitindo que DEFINEs não UTF-8 passem sem gerar define-invalido."}
{"achado":"N1","veredito":"NOVO","severidade":"MED","arquivo":"sdd/bin/deploy-do-sha.sh","linha":165,"resumo":"A função contem não verifica o returncode do git fetch antes de confiar no merge-base, podendo concluir 'não contém' e falhar o deploy quando o fetch falha."}
VERDICTS>>>