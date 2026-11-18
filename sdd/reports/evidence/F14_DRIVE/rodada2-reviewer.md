## 1. Veredito geral

**REPROVADO**

O desenho e a maior parte dos contratos estão coerentes com o DEFINE e o DESIGN, e o `deploy-do-sha.sh` e o `sdd-archive.py` não mostraram defeito de correção. Porém, a trava de repetição (AT-007, Decision 4) falha no caminho que o próprio brief do executor manda seguir. A linha do `PROGRESS`, anotada a cada falha, entra na chave da contagem, e uma tarefa que nunca anda pode girar sem parar, sem nem gastar rodada. É quebra de contrato declarado num MUST. Os demais achados são menores, e o conserto de R1 é pontual.

## 2. Conformidade com o DEFINE e o DESIGN

**Limitações do material**
- Nada foi executado, por regra desta revisão, e `verify-gate.sh`, `sdd-fluxo.sh` e `report-lint.py` só aparecem em parte.
- O passo 4 da `sdd-release` está truncado no diff, o que limita a leitura de R3.

**Item a item**

| Item | Situação |
|---|---|
| Verify Gate | Não comprovado para este diff. O BUILD_REPORT cita DEFINE v1.6, DESIGN v1.5 e evidência em `ff5c539`, mas o diff já traz os consertos da "revisão real, rodada 1" (DEFINE v1.7, DESIGN v1.6). |
| AT-001 a AT-006, AT-008 a AT-018 | O diff entrega o prometido, com a ressalva de R4 sobre AT-005 e AT-010. |
| AT-007 | **Não cumprido** quando o executor anota o erro na linha da tarefa (R1). |
| AT-019 a AT-021, AT-027, AT-031, AT-035, AT-036 | Textos, slots e contagens conferem com o DEFINE. |
| AT-022 a AT-026 | A lógica confere, inclusive redisparo único, ausência de `gh run rerun` e exit 4 para "ainda não sei". O uso pelo item 10 tem a ressalva de R3. |
| AT-028 a AT-030 | Conferem. |
| AT-032 a AT-034 | Conferem. |
| AT-037 | As adições a `verify-gate.sh` e `sdd-fluxo.sh` são aditivas no trecho visível. |
| AT-038 | Pendente: o BUILD_REPORT o marca `PENDENTE_PROVA`, e a evidência não está no material. |
| DESIGN, Security Considerations | Diverge: "link que sai da raiz é recusado no estado e no relatório" não foi implementado (R2). |
| DESIGN, Error Handling | Possível divergência: DEFINE em bytes não UTF-8 deveria dar `define-invalido` (R6). |

## 3. Achados

**R1 — `sdd/bin/sdd-drive.sh:773` — HIGH — CONFIRMED**
- **Defeito:** a chave da repetição inclui o `detalhe`, que traz a linha inteira do `PROGRESS` com a anotação de erro, e por isso a contagem do AT-007 recomeça quando a anotação muda.
- **Cenário de falha:**
  1. O executor falha na tarefa `a` sem commit e, seguindo a regra 3 do brief, grava `- [ ] a — falhou X`.
  2. Na sessão seguinte, grava `- [ ] a — falhou Y`.
  3. Com o mesmo `HEAD`, `proximo` ou `--resume` responde `tarefa: 1 de 2 — a — falhou …` com texto diferente a cada volta, e o contador fica em `n=1`.
  4. `bloqueio-humano` nunca sai, e o laço não tem outro teto, porque nenhum gate roda e nenhuma rodada é gasta.

  `test_anotacao_de_erro_no_progress_nao_cria_tarefa` só confere o texto impresso, e nenhum teste combina anotação com repetição.

**R2 — `sdd/bin/sdd-drive.sh:154` — MED — CONFIRMED**
- **Defeito:** a promessa do DESIGN de recusar link que sai da raiz não existe, porque só o caminho do DEFINE passa por `realpath`.
- **Cenário de falha:**
  - Com `sdd/reports` apontando para fora do repositório, `iniciar` grava estado e relatório lá fora, sem recusa.
  - Com `DRIVE-gate-r1.log` como link quebrado, `os.path.exists` devolve falso e `open(..., "w")` cria o alvo externo com a saída do gate.

**R3 — `.agents/skills/sdd-release/SKILL.md:227` — MED — PLAUSIBLE**
- **Defeito:** o item 10 não passa `--transitorios` nem `--repo`, então o script lê `deploy.transient_steps` do `sdd/config.yaml` da pasta atual.
- **Cenário de falha:** se o item 10 roda no worktree temporário e o `sdd/config.yaml` não existe lá, uma falha em passo passageiro configurado sai 2 com "deploy.transient_steps está vazio", sem redisparo.
- **Premissas não verificáveis:** a pasta em que o item 10 roda e se o arquivo é rastreado. O trecho do passo 4 está truncado, mas cita algo "ignorado pelo git" que não existe nesse worktree.

**R4 — `sdd/bin/sdd-drive.sh:881` — LOW — CONFIRMED**
- **Defeito:** depois do gate, o `detalhe` de `proxima` é trocado por uma frase fixa, o que perde a lista de `COMMITAR` e a linha `tarefa:` de `RODADA`.
- **Cenário de falha:** um gate verde em primeiro plano deixa `coverage.xml` não ignorado. O script imprime `ACAO: COMMITAR` com "há código novo depois de quando ele começou", sem listar o arquivo, embora a ação peça para commitar "os arquivos listados". O ramo do exit 2 tem a mesma perda quando a ação não é `CORRIGIR`.

**R5 — `sdd/bin/sdd-drive.sh:743` — LOW — CONFIRMED**
- **Defeito:** `--resume` lê o estado, roda subprocessos e o regrava sem trava, e essa escrita pode apagar um gate registrado nesse intervalo.
- **Cenário de falha:** a sessão cai durante `verificar --fundo`, e a nova sessão chama `--resume`. Se o gate termina entre a leitura e a escrita, o registro some. Um vermelho deixa de gastar rodada, e um verde precisa rodar de novo.

**R6 — `sdd/bin/sdd-drive.sh:659` — LOW — PLAUSIBLE**
- **Defeito:** nenhuma conferência visível no diff transforma DEFINE não UTF-8 em `define-invalido`, como pede o Error Handling do DESIGN.
- **Cenário de falha:** um DEFINE em Latin-1 com bloco de gate válido passa por `iniciar`, porque a saída é decodificada com `errors="replace"`.
- **Premissa não verificável:** que o trecho de `verify-gate.sh` fora do diff também não recuse esses bytes.

## 4. Bloco de vereditos

<<<VERDICTS
{"achado":"R1","arquivo":"sdd/bin/sdd-drive.sh","linha":773,"severidade":"HIGH","confianca":"CONFIRMED","resumo":"A anotação de erro do PROGRESS entra na chave da repetição e impede a parada do AT-007."}
{"achado":"R2","arquivo":"sdd/bin/sdd-drive.sh","linha":154,"severidade":"MED","confianca":"CONFIRMED","resumo":"A recusa de link que sai da raiz, prometida no DESIGN, não foi implementada para estado, relatório e log."}
{"achado":"R3","arquivo":".agents/skills/sdd-release/SKILL.md","linha":227,"severidade":"MED","confianca":"PLAUSIBLE","resumo":"O item 10 depende do sdd/config.yaml da pasta atual e pode perder os passos passageiros no worktree temporário."}
{"achado":"R4","arquivo":"sdd/bin/sdd-drive.sh","linha":881,"severidade":"LOW","confianca":"CONFIRMED","resumo":"Depois do gate, a frase fixa substitui o detalhe da próxima ação e perde a lista de COMMITAR e a tarefa de RODADA."}
{"achado":"R5","arquivo":"sdd/bin/sdd-drive.sh","linha":743,"severidade":"LOW","confianca":"CONFIRMED","resumo":"O --resume regrava estado lido antes dos subprocessos e pode apagar um gate registrado nesse intervalo."}
{"achado":"R6","arquivo":"sdd/bin/sdd-drive.sh","linha":659,"severidade":"LOW","confianca":"PLAUSIBLE","resumo":"DEFINE em bytes não UTF-8 pode seguir adiante em vez de parar em define-invalido como pede o DESIGN."}
VERDICTS>>>