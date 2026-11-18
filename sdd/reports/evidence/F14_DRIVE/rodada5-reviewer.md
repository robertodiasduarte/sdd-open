## 1. Veredito geral

**APROVADO COM RESSALVAS**

Não encontrei defeito HIGH nem caminho que produza verde falso ou publicação indevida: o `sdd-drive.sh` não publica, `gate-verde` exige um gate válido do commit atual, e o `deploy-do-sha.sh` só diz "no ar" com run próprio ou substituto que contém o commit. As ressalvas são um MED no laço de espera do item 10 da `sdd-release`, que pode não terminar, e 3 LOW. Além disso, AT-038, CI, revisão real e Release ainda não têm prova no material, e isso continua bloqueando a `v2.7.0`.

## 2. Conformidade com o DEFINE e o DESIGN

**Limitação do material:** o diff não traz `contexto-fresco.md`, `tests/apoio.py`, as evidências citadas nem os trechos não alterados de `verify-gate.sh`, `sdd-fluxo.sh` e `avaliador-guard.sh`. Não executei nada: a conformidade abaixo vem da leitura do código e dos testes.

| Item | Situação | Observação |
|---|---|---|
| AT-001 a AT-018 (drive) | Cumpre na leitura | Estado, ordem das ações, repetição, impressão digital, trava, orçamento, relatório e self-test batem com o DEFINE. |
| AT-019 e AT-020 (skill e executor) | Cumpre na leitura | Os motivos, os exits e as 2 perguntas aparecem nos lugares exigidos. |
| AT-021 e AT-031 (`sdd-release`) | Cumpre | Os textos e a ordem pedidos estão no diff. |
| AT-022 a AT-026 (`deploy-do-sha.sh`) | Cumpre em cada chamada | Ver R2 para o caso da marca gravada sem redisparo. |
| AT-027 (item 10) | Cumpre com ressalva | A lógica saiu da skill, mas a orientação de repetir não tem fim (R1). |
| AT-028 a AT-030 (`sdd-archive.py`) | Cumpre com desvio menor | A proteção e o `git mv` batem; um documento solto recente sai na lista errada (R4). |
| AT-032 a AT-037 | Cumpre na leitura | Os contratos anteriores aparecem como acréscimos no diff; a suíte que prova AT-037 não foi executada nesta revisão. |
| AT-038 | **Sem prova** | O BUILD_REPORT marca `PENDENTE_PROVA`, e o AT exige a prova depois do último conserto. |
| Verify Gate e critérios de sucesso | **Não confirmáveis** | O BUILD_REPORT cita verde em `52f0830`, mas não dá para confirmar que esse é o commit final. CI, `--conferir` e Release estão pendentes. |

**Divergências de documento, sem efeito no comportamento:**
- O BUILD_REPORT cita DEFINE v1.6 e DESIGN v1.5, mas as versões atuais são v1.9 e v1.8. A lista de commits dele para em `ff5c539`, enquanto o gate citado é de `52f0830`.
- A Decision 3 diz que "todo verbo" para no orçamento, mas `recibo`, `bloqueio` e `aguardar` não param. O AT-012 lista só os outros verbos, então o código segue o DEFINE.
- A Decision 9 diz que a idade sem histórico é "desconhecida", mas o código usa o mtime.

## 3. Achados

### R1
- **Local:** `.agents/skills/sdd-release/SKILL.md:231`
- **Severidade:** MED
- **Confiança:** CONFIRMED
- **Defeito:** a orientação "`--teto 300` e repita enquanto sair 4" não tem limite total, e cada chamada reinicia o relógio do script, então o teto de 40 minutos do AT-022 deixa de valer nesse modo.
- **Cenário de falha:** um agente sem segundo plano publica um commit que o filtro `paths` do workflow não aciona. Cada chamada sai 4 em cerca de 120 s com "não achei nenhum run", e o agente repete sem fim. O mesmo acontece com a marca de redisparo gravada quando o run novo nunca aparece, porque `aguardando_novo` devolve 4 em toda chamada seguinte. O texto antigo mandava dizer que não achou o run depois de cerca de 2 minutos.

### R2
- **Local:** `sdd/bin/deploy-do-sha.sh:130`
- **Severidade:** LOW
- **Confiança:** CONFIRMED
- **Defeito:** quando `gh workflow run` responde 401, o script sai 3 sem apagar a marca já gravada por `marcar()`, ao contrário do caminho de recusa HTTP 4xx, que chama `desmarcar()`.
- **Cenário de falha:** o token expira entre a listagem e o disparo. Depois de `gh auth login`, a nova chamada encontra a marca e diz que pediu para repetir e o run não apareceu. Ela sai 4 e nunca faz o único redisparo permitido, embora nada tenha sido disparado.

### R3
- **Local:** `sdd/bin/sdd-drive.sh:333`
- **Severidade:** LOW
- **Confiança:** CONFIRMED
- **Defeito:** em `segura_estado`, a falha de `os.remove` numa trava abandonada executa `continue` antes de conferir `limite_espera` e sem `sleep`, o que cria um laço sem saída.
- **Cenário de falha:** sobra um `DRIVE_<F>.estado.lock` com mais de 60 s numa pasta em que o usuário atual não pode apagar, por exemplo depois de uma execução cortada com `sudo`. Qualquer verbo fica consumindo CPU para sempre, em vez de sair 2 com a orientação de apagar a trava.

### R4
- **Local:** `sdd/bin/sdd-archive.py:258`
- **Severidade:** LOW
- **Confiança:** CONFIRMED
- **Defeito:** um documento sem grupo, fora de `sdd/features/` e ainda recente cai em "Sem classificação (decisão sua)" em vez de "Recentes", ao contrário do AT-028.
- **Cenário de falha:** `sdd/reports/solto.md`, com commit de 3 dias atrás, aparece como decisão pendente da pessoa e conta em `sem classificação`. Quando passa de `--dias-b`, ele vai para o lote `soltos` sem nenhuma decisão. Um grupo sem documento em `sdd/features/`, com a mesma idade, sai corretamente em "Recentes".

## 4. Bloco de vereditos

<<<VERDICTS
{"achado":"R1","arquivo":".agents/skills/sdd-release/SKILL.md","linha":231,"severidade":"MED","confianca":"CONFIRMED","resumo":"Repetir enquanto sair 4 não tem limite total e anula o teto de 40 minutos, podendo deixar o agente sem segundo plano em laço infinito."}
{"achado":"R2","arquivo":"sdd/bin/deploy-do-sha.sh","linha":130,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Um 401 no disparo sai 3 sem apagar a marca, e o único redisparo se perde sem nada ter sido disparado."}
{"achado":"R3","arquivo":"sdd/bin/sdd-drive.sh","linha":333,"severidade":"LOW","confianca":"CONFIRMED","resumo":"A falha ao apagar uma trava de estado abandonada cria um laço sem espera e sem limite."}
{"achado":"R4","arquivo":"sdd/bin/sdd-archive.py","linha":258,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Um documento solto recente sai como sem classificação em vez de recente."}
VERDICTS>>>