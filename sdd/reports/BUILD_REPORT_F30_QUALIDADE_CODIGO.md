# BUILD REPORT: F30 — Qualidade do código gerado · fatia S2 (itens 2, 6, 7)

> Vermelho antes do verde conferido pelo `report-lint.py` (coluna `Antes`), sabotagem do gate numa cópia descartável
> (`sdd/bin/sabotagem.sh`) e o passo Refatorar entre Verificar e Marcar, ligado por padrão (`build.refatorar`).
> O relatório da S1 está na versão de `c4fa53c` (release v2.26.0).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO (fatia S2) |
| **Date** | 2026-11-24 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F30_QUALIDADE_CODIGO.md](../features/DEFINE_F30_QUALIDADE_CODIGO.md) (1.5) |
| **DESIGN** | [DESIGN_F30_QUALIDADE_CODIGO.md](../features/DESIGN_F30_QUALIDADE_CODIGO.md) (2.1) |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 15/15 do File Manifest |
| **Files Created** | 5 (`sabotagem.sh`, `disciplina-de-teste.md`, 3 módulos `tests/test_f30_*.py`) e este relatório |
| **Build Time** | uma sessão (24/11) |
| **Tests Passing** | 51 testes novos, todos escritos antes do código e gravados vermelhos (`AT-nnn.antes.log`); suíte inteira no Verify Gate |
| **Agents Used** | revisores externos do DESIGN e do código (openrouter `qwen/qwen3.7-plus`, codex, auditor claude), 2 agentes da medição de custo e o avaliador de contexto fresco |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate e testes novos | LM-001, LM-002 | ✔ tratado | os 3 módulos novos rodados antes do código: vermelhos avaliando (`AT-010.antes.log` a `AT-015.antes.log`); um `TypeError` do próprio teste no AT-012 foi consertado e o antes regravado; `test -f` dos 3 no gate |
| revisão sobre diff vazio | LM-003 | ✔ tratado | DEFINE e DESIGN commitados antes da revisão do DESIGN; código commitado antes da revisão do código |
| cópia sem `.git` | LM-006 | ✔ tratado | a sabotagem roda numa cópia de `git archive`; os testes conferem 0, 2, 3 e 64 exatos |
| sabotagem na árvore | LM-009 | ✔ tratado | nunca toca a árvore; hash (com `.git`) igual antes e depois em todos os 13 casos do `test_f30_sabotagem` |
| `subprocess` e Windows | LM-014, LM-029, LM-042 | ✔ tratado | `Sandbox.roda`, `BASH`, `caminho_bash` e `SEM_SYMLINK` de `tests/apoio.py` |
| saída UTF-8 do Python embutido | F16W2 | ✔ tratado | o `test_f16w2_saida` acusou o embutido do `sabotagem.sh` sem a troca de saída; corrigido em `5a5f361` |
| `[exit=` do log | LM-018 | ✔ tratado | logs por script `bash` com `rc=$?` sem pipe; o `sabotagem.sh` grava o mesmo formato |
| starter | LM-035 | ✔ tratado | `disciplina-de-teste.md` e `MODO_WEB.md` sem `sdd/bin/`; o `test_f30_textos_s2` gera o starter e confere |
| custo em tokens | LM-036 | ✔ tratado | o número vem do uso que o executor de agente reporta, não do registro local |
| MANIFEST | LM-037 | ✔ tratado | 5 arquivos novos no `MANIFEST.txt` no mesmo commit |
| teto de 500 linhas | LM-038 | ✔ tratado | `sdd-build` 370 → 380, `MODO_WEB.md` 488 → 489, `sdd-design` 318 → 326; `test_conversa` verde |
| contagem de perguntas | LM-044 | N.A. | nenhuma pergunta `[Dn]` nova |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `unittest discover` `Ran 0 tests` `python 3.9` `verify-gate` `test -f`
texto: No Python 3.9 (o /usr/bin/python3 do macOS), `unittest discover` sem nenhum teste que case o padrão sai 0 ("Ran 0 tests … OK"): um Verify Gate que só roda `discover -p 'test_fNN_*.py'` fica verde antes de o teste existir, e não prova nada (na F30 S1 isso foi medido antes do código).
Do instead: ao criar um módulo de teste da feature, acrescente `test -f tests/<módulo>.py` ao gate, antes do discover, no mesmo commit; confira o vermelho do gate na árvore de antes.
evidencia: sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md (Verify Gate e nota de baseline); sdd/reports/evidence/F30_QUALIDADE_CODIGO/AT-010.antes.log
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `vermelho antes` `antes.log` `TypeError` `baseline` `teste novo`
texto: O vermelho de um teste novo rodado antes do código pode vir de um defeito do próprio teste (na F30 S2, um `TypeError` de precedência entre `/` e `%` num `Path` no AT-012), e não da falta do comportamento: um antes assim prova só que o teste quebra.
Do instead: antes de gravar o `AT-nnn.antes.log`, leia as falhas: `FAIL` de asserção ou `ImportError` do módulo novo valem; `ERROR` dentro do próprio teste se conserta e o antes se grava de novo.
evidencia: sdd/reports/evidence/F30_QUALIDADE_CODIGO/AT-012.antes.log
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1–3 | `tests/test_f30_vermelho_antes.py`, `test_f30_sabotagem.py`, `test_f30_textos_s2.py` | (general) | ✅ | escritos antes do código; 24 + 13 + 11 testes |
| 4 | `sdd/bin/report-lint.py` | (general) | ✅ | coluna `Antes`, `ats_do_define`, classe `[vermelho antes]` |
| 5 | `sdd/bin/sabotagem.sh` | (general) | ✅ | 0/2/3/64; contenção do caminho; `trap` |
| 6 | `web/references/disciplina-de-teste.md` | (general) | ✅ | texto único, vai ao starter |
| 7–8 | `sdd-build/SKILL.md` e `web/MODO_WEB.md` | (general) | ✅ | versão 2.16.0 |
| 9–10 | `sdd-design/SKILL.md` (2.12.0) e `DESIGN_TEMPLATE.md` | (general) | ✅ | tabela de sabotagens |
| 11–12 | `BUILD_REPORT_TEMPLATE.md`, `fragments/EVIDENCIA.md` | (general) | ✅ | coluna `Antes`; também no molde do starter (`web/assets/`) |
| 13–15 | `config.example.yaml`, `docs/cli-conventions.md`, `MANIFEST.txt` | (general) | ✅ | |
| — | fora do manifest: versões fixas em 7 testes antigos e o recorte do Verificar no `test_f30_textos` | (general) | ✅ | consequência das versões novas e do passo 5 novo |

---

## Seleção de modo

Sinais: 15 itens, um mantenedor, ambiente com subagentes. Recomendação: `default` (sequencial). Decisão: `default`,
pela autorização do Roberto em 24/11 de seguir o pipeline com as recomendações.

| Item | Valor |
|---|---|
| Refatorar | ligado (padrão): nos arquivos das tarefas, depois do verde; nenhuma refatoração mudou comportamento |

---

## Drift detectado

- O molde do BUILD_REPORT do starter (`sdd-build/web/assets/BUILD_REPORT_TEMPLATE.md`) não estava no manifest; ganhou
  a coluna `Antes` para o texto da disciplina valer também no starter.
- A versão da linha de identificação do `sdd-design/web/MODO_WEB.md` acompanhou a do `SKILL.md` (2.12.0), sem mudança de texto.

---

## Files Created

| File | Lines | Verified | Notes |
|------|-------|----------|-------|
| `sdd/bin/sabotagem.sh` | ~190 | ✅ | |
| `.agents/skills/sdd-build/web/references/disciplina-de-teste.md` | ~65 | ✅ | |
| `tests/test_f30_vermelho_antes.py` · `test_f30_sabotagem.py` · `test_f30_textos_s2.py` | — | ✅ | |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

O pacote não tem `sdd/config.yaml`: os slots `project.lint_cmd` e `project.typecheck_cmd` estão vazios.

lint: slot vazio

### Testes (`{{TEST_CMD}}`)

Ver o Verify Gate em Acceptance Test Verification.

---

## Custo dos passos novos (itens 2, 6 e 7)

Medido em 24/11 com a mesma tarefa de exemplo (`saca(saldo, valor)` em Python, 2 AT, numa pasta temporária fora do
repositório), feita por 2 agentes de contexto fresco do mesmo modelo (Claude Sonnet). Os tokens são os que o executor
de agente reportou no fim de cada um (LM-036).

| Execução | Passos | Tokens | Chamadas de ferramenta | Tempo |
|---|---|---|---|---|
| A | Escrever, Verificar, Marcar (os de antes) | 56.739 | 2 | 12,6 s |
| B | teste primeiro, vermelho antes com log, Escrever, Verificar, Refatorar, sabotagem declarada, Marcar | 59.253 | 4 | 20,2 s |
| **Diferença** | | **+2.514 (+4,4%)** | +2 | +7,6 s |

Os dois terminaram verdes; o B gravou o antes vermelho (`[exit=1]`) e a sabotagem saiu 0 (o teste pegou o defeito);
a refatoração não mudou nada (o código já estava limpo). Leitura: a maior parte dos tokens é o contexto fixo do agente;
os passos novos acrescentam ~2,5 mil tokens numa tarefa de 2 AT. É n=1: o número é instável e cresce com o número de
AT e de sabotagens declaradas; a sabotagem em si custa tempo (2 execuções do comando), não tokens.

---

## Segurança

O `sabotagem.sh` é a única superfície (DEFINE § Segurança, S2): troca só na cópia de `git archive HEAD` numa pasta de
`mktemp -d`; recusa caminho absoluto, com `..`, link simbólico e caminho real fora da cópia (64); apaga a cópia por
`trap`; a árvore recebe só o log. Conferido pelo `test_f30_sabotagem` (hash da árvore, inclusive `.git`, e o `TMPDIR`
vazio em todos os casos) e pela sabotagem declarada do AT-013 (`AT-013.sabotagem.log`).

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | A revisão do DESIGN achou 1 MED (N1): `shall continue to` em qualquer lugar da linha classificaria o AT-011 como não-regressão | aplicado antes do código (Decision 9, DESIGN 2.1), com teste | — |
| 2 | O antes do AT-012 tinha um `TypeError` do próprio teste | consertado e regravado; candidato ao playbook acima | ~2 min |
| 4 | O avaliador (ciclo 1) achou o N1 do `sabotagem.sh` | cópia nova para a execução sabotada (`monta_copia`), com teste; ciclo 2 conferiu | ~15 min |
| 3 | Os testes vizinhos acusaram 10 falhas: versões fixas, o recorte do Verificar e o Python embutido sem saída UTF-8 | corrigidas em `5a5f361`; os 127 testes desses módulos verdes | ~5 min |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| A sabotagem do AT-013 foi trocada depois do código (DESIGN 2.2) | a declarada era pega pelo exit 64 da checagem de caminho, sem chegar ao hash da árvore; a nova é pega pela asserção do hash | a declaração deixou de ser anterior ao código neste AT |
| A cópia e a saída ficam numa pasta só de `mktemp -d` (`<pasta>/copia`, `<pasta>/saida.txt`), não a cópia direto no `mktemp` | a saída do comando não pode ficar dentro da cópia que ele lê; uma pasta e um `trap` apagam as duas | nenhum |
| O `trap` de `INT`/`TERM`/`HUP` apaga e sai 130/143/129 | sair no sinal, em vez de seguir rodando depois da limpeza | nenhum |

---

## Raio de impacto (adiantado da release, 0b)

2 agentes frescos, só leitura, com o brief `sdd-release/references/raio-de-impacto.md`. Nenhum consumidor quebrado e
nenhuma invariante violada (INV-001 e INV-002 não tocam os módulos).

| Superfície | Consumidores lidos | Resultado | Tratado |
|---|---|---|---|
| `report-lint.py` (coluna `Antes`, classe nova, aviso) e a tabela de critérios | `sdd-report-guard.py`, pre-commit, `sdd-drive.sh`, `sdd-release` 0a.5, `gate-shell-evidencia.sh`, `playbook-curator.sh`, fixtures de evidência, 6 módulos de teste; relatórios reais antigos (VERDE com o aviso) | ok | risco latente: um AT repetido numa 2ª tabela do DEFINE reclassificava o AT — vale a 1ª (teste novo); o conserto `[tabela]` e o exemplo da `EVIDENCIA.md` ganharam a coluna (`a5c02ca`) |
| `build.refatorar` no config, passos 5/6 da tarefa, versões 2.16.0/2.12.0, `disciplina-de-teste.md` no starter | `init`/`upgrade`/`sync` (não mesclam chaves: ausente = ligado), `ler_mapa`, `slot.sh`, hooks, `checar.sh`, check-versions do Open e do starter, gerador do starter (GERADO, check-gerado VERDE, lint VERDE) | ok | lacunas de texto: a linha `refatorar: desligado` sem seção no molde do starter (a disciplina diz "numa linha própria"); o `WORKER_BRIEF` ganhou o vermelho antes e o refatorar |

---

## Blockers (if any)

A `v2.27.0` e a `v2.27.1` ficaram como tag sem Release: o CI caiu por 2 defeitos de teste do `test_f30_sabotagem` (link simbólico no Windows; `maintenance.lock` do git no macOS). A `v2.27.1` subiu sem a revisão repetida depois da mudança do teste (`--conferir`: NÃO CONFERE). Corrigidos para a `v2.27.2`, que também ficou sem Release: o `ln -s` do teste não criou link no Git Bash (fatia 2), a fatia 4 do Windows foi cancelada no teto de 30 min (4 unidades lentas juntas, todas verdes no outro run) e o `test_f25_skills_duplicadas` caiu no macOS de um dos 2 runs (causa inferida: a manutenção automática do git; mecanismo reproduzido). Na `v2.27.3`: link criado pelo Python, suíte sem a manutenção automática (`tests/apoio.py`, `tests/test_apoio_git.py`), teto de 45 min, e o CI inteiro no PR #43 antes da tag.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO (sobre `e65531f`; depois dele mudaram o `report-lint.py` no raio de impacto e 2 testes) · ciclos: 2 · achados: ciclo 1 NEEDS_WORK por 1 MED (N1: a execução sabotada reusava a cópia da limpa, e o `__pycache__` escondia a sabotagem quando ela caía no mesmo segundo do commit; aplicado com teste determinístico) e 2 observações aplicadas (O1, O2); ciclo 2 com os 3 conferidos e 5 observações leves (O-A a O-E) que ficam como pendência na ficha; o recibo é o Verify Gate abaixo · `AVALIACAO_F30_QUALIDADE_CODIGO_20261124-1300.md` (ciclo 1: `AVALIACAO_F30_QUALIDADE_CODIGO_20261124-1225.md`)

---

## Acceptance Test Verification

| ID | Critério (EARS, resumido do DEFINE) | Antes | Resultado | Evidência |
|----|-------------------------------------|-------|-----------|-----------|
| AT-010 | When o `report-lint` confere um relatório com a coluna `Antes`, shall exigir o `AT-nnn.antes.log` vermelho do mesmo comando em cada AT novo | `evidence/F30_QUALIDADE_CODIGO/AT-010.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-010.log` · `evidence/F30_QUALIDADE_CODIGO/AT-010.sabotagem.log` |
| AT-011 | If o AT é `shall continue to`, then shall exigir o antes verde; `manual-ux` e outros kinds aceitam `N.A.` | `evidence/F30_QUALIDADE_CODIGO/AT-011.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-011.log` |
| AT-012 | While a tabela não tem a coluna `Antes`, shall aprovar com 1 aviso; sem DEFINE, aviso com a causa | `evidence/F30_QUALIDADE_CODIGO/AT-012.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-012.log` |
| AT-013 | When o `sabotagem.sh` roda, shall dar 0 com o teste que pega e 2 com o que não pega, com a árvore idêntica fora o log | `evidence/F30_QUALIDADE_CODIGO/AT-013.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-013.log` · `evidence/F30_QUALIDADE_CODIGO/AT-013.sabotagem.log` |
| AT-014 | If o trecho não casa 1 vez, o caminho sai da cópia, o comando já falha ou não roda, then shall sair 3 ou 64 sem log | `evidence/F30_QUALIDADE_CODIGO/AT-014.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-014.log` |
| AT-015 | When a tarefa passa pelos passos, os textos shall ter o vermelho antes, a sabotagem, o Refatorar e `build.refatorar`, também no starter sem `sdd/bin/` | `evidence/F30_QUALIDADE_CODIGO/AT-015.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-015.log` |
| AT-016 | The system shall continue to aprovar os relatórios sem a coluna `Antes` (o da S1) e passar a suíte, o `publish-gate` e o `check-versions` | `evidence/F30_QUALIDADE_CODIGO/AT-016.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-016.log` |

**Verify Gate (`bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md`):** exit 0 em `2864d26`, o código da `v2.27.3` (`evidence/F30_QUALIDADE_CODIGO/GATE_S2_2864d26.log`: 113 testes `test_f30_*` e a suíte inteira, 2.880 testes, OK, 4 pulados). Uma execução em `b161357` saiu vermelha (arquivo de teste novo fora do `MANIFEST.txt`, LM-037), corrigida. Antes, exit 0 em `cb35651`, o código da `v2.27.2` (`evidence/F30_QUALIDADE_CODIGO/GATE_S2_cb35651.log`: 113 testes `test_f30_*` e a suíte inteira, 2.878 testes, OK, 4 pulados). Antes, exit 0 em `d1b0c51` (código da `v2.27.0`; commit na 2ª linha do log), `evidence/F30_QUALIDADE_CODIGO/GATE_S2_d1b0c51.log`: grep da F29 vazio, `check-versions` VERDE, `publish-gate` em modo CI verde sobre a cópia de `git archive`, os 8 `test -f`, os `test_f30_*` (105 testes) e a suíte inteira, 2.870 testes, OK (4 pulados), com `/bin/bash` 3.2 e `/usr/bin/python3` 3.9, em 35,5 min. Um gate em `491bd2d` foi interrompido de propósito: os consertos do raio de impacto mudaram o código antes de ele terminar.

---

## Advisor Ledger

O ledger completo está em `sdd/reviews/LEDGER_REVISAO_F30_QUALIDADE_CODIGO.md` (seção S2; o `ledger-revisao-lint.sh`
dá VERDE). Resumo da S2:

| Rodada | Commit | Achados | Decisão |
|---|---|---|---|
| D2 (DESIGN) | `f2d01d1` | 1 MED do auditor (classe `continua` por qualquer ocorrência na linha) | APLICADA (DESIGN 2.1) |
| 1 (código) | `b4c9f55` | nenhum (o auditor conferiu os pontos de risco e descartou 3 LOW já decididos) | — |
| 2 (código) | `e65531f` | nenhum (depois do conserto do ciclo 1 do avaliador) | — |
| 3 (código) | `d734b18` | 2 LOW no `sabotagem.sh` (sem a biblioteca, falta de Python sai como inconclusivo; `git archive \| tar` sem `pipefail`) | 2 REBATIDA_ESCOPO na hora; o `pipefail` foi aplicado na rodada 6. A justificativa "nunca um falso pega" estava errada: a rodada 7 achou um caso |
| 4 e 5 (código) | `ea3bc55` | nenhum; recusadas como rasas | não contam |
| 6 (S2 inteira, codex) | `ea3bc55` | 1 HIGH (log seguia link simbólico) e 1 MED (`[exit=]` grudado) | 2 APLICADA |
| 7 (S2 inteira, codex) | `aee8d67` | 1 HIGH (hard link), 2 MED (HEAD resolvido 2 vezes; WORKER_BRIEF) | 3 APLICADA |
| 8 (S2 inteira, codex) | `cb35651` | nenhum | CONFERE |
| 9 (S2 inteira, codex) | `2864d26` | nenhum | CONFERE |

Revisores: openrouter `qwen/qwen3.7-plus` (0 achados próprios nas 2 rodadas), codex `gpt-6.1-sol` como 2º revisor no
DESIGN, auditor claude; `diversidade: vendor`. Custo: US$ 0,67 (DESIGN) + 0,88 + 0,89 + 0,88 + 0,42 + 0,42 + 1,89 + 1,91 + 1,93 + 1,97 (código) = US$ 11,86, fora uma revisão interrompida sem custo medido. Nas rodadas 6 a 9, codex `gpt-6.1-sol` revisou a S2 inteira.

---

## Final Status

### Overall: ✅ COMPLETE

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] Testes novos vermelhos antes do código (com log) e verdes depois
- [x] 2 sabotagens declaradas no DESIGN pegas pelos testes
- [x] Verify Gate verde no código que sobe (`2864d26`)
- [x] No blocking issues
- [x] Acceptance tests verified — 7 de 7 com log e antes
- [x] Avaliador de contexto fresco com `AVALIACAO_*.md` persistido

---

## Next Step

**Ready for:** `/sdd-release F30_QUALIDADE_CODIGO`
