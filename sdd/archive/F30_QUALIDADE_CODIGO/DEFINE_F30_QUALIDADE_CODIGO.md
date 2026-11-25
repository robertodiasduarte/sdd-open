# DEFINE: F30 — Qualidade do código gerado (Uncle Bob × Open)

> O código que o método gera passa a seguir as boas práticas consagradas (Clean Code, TDD): lint e tipos a
> cada tarefa, regras de qualidade por stack, disciplina de teste e métricas de forma no diff — em 3 fatias
> publicáveis (S1, S2, S3).

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO |
| **Date** | 2026-11-23 |
| **Author** | Roberto Dias Duarte (decisões) · define-agent (redação) |
| **Status** | S1 publicada (v2.26.0) · S2 publicada (v2.27.3) · S3 Ready for Design |
| **Clarity Score** | 15/15 |

Entradas: `sdd/features/AVALIACAO_F30_UNCLE_BOB.md` (o porquê, as 15 propostas, a nota) e
`sdd/features/ESCOPO_F30_QUALIDADE_CODIGO.md` (achados com linha, os 8 itens, D1–D7). Sem brainstorm: os dois
documentos fazem esse papel. Um ciclo DEFINE → DESIGN → BUILD → RELEASE por fatia; este arquivo cresce por
`sdd-iterate`, não por arquivo novo.

---

## Problem Statement

O SDD Open prova que o código **faz** o que o aceite pede (Verify Gate, evidência), mas não cuida da **forma**
do código: o passo "Verificar" de cada tarefa do Build é uma frase genérica
(`.agents/skills/sdd-build/SKILL.md:188`), o `project.lint_cmd` só roda de fato na release, o projeto típico de
aluno nem tem linter, e o agente não recebe nenhuma regra de qualidade (só as de segurança, `{{SEGURANCA}}`).
O efeito é código que passa no gate com erro de estilo, de tipos e helper duplicado, descoberto só no fim.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Aluno iniciante (Open e Starter) | Constrói a 1ª feature com o agente, sem nunca ter usado terminal | Recebe código que "funciona" com erro de lint e de tipos que ele não sabe ver; o projeto dele nem tem linter |
| Aluno da Turma Bravo | Mantém um sistema real com o método | Código feito por agente recria helper que já existe e engole erro; o defeito aparece em manutenção |
| Roberto (mantenedor) | Ensina o método e defende a nota de aderência | Não pode dizer que o método segue Clean Code/TDD: nada no pacote cita nem mede isso |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | S1: lint e tipos rodam a cada tarefa do Build, com o slot cheio, e deixam evidência que o `report-lint.py` confere |
| **MUST** | S1: o AGENTS.md gerado traz as regras de qualidade da stack do projeto, e o Starter as traz no texto da build |
| **MUST** | S1: projeto sem linter recebe a sugestão do padrão da stack, sem nada instalado nem gravado sem o sim |
| **MUST** | S2: vermelho antes do verde, sabotagem do gate em cópia descartável e refatorar depois do verde (itens 2, 6, 7) |
| **SHOULD** | S3: duplicação e complexidade no diff, só aviso (itens 5, 8) |
| **COULD** | Medir a nota de aderência com projetos de exemplo (fora desta frente) |

---

## Success Criteria

- [ ] S1: 100% dos BUILD_REPORTs com `lint_cmd` ou `typecheck_cmd` cheio e sem o log correspondente são reprovados pelo `report-lint.py` (exit 1); 0 reprovações com o log certo ou com os dois slots vazios e a linha declarada.
- [ ] S1: `init` e `sync` em 3 fixtures (Python, JS/TS, sem stack) geram exatamente 1 bloco `### Qualidade ao construir`, com as 6 regras gerais e, nas 2 primeiras, as da stack.
- [ ] S1: o `checar.sh` numa fixture sem linter imprime a sugestão da stack em ≤ 1 bloco e a árvore fica idêntica (hash antes = depois).
- [ ] S1: o starter gerado traz as regras de qualidade no texto da `sdd-build` e passa nos `grep` da F29 (0 ocorrências).
- [ ] S2: 100% dos AT de comportamento novo sem `AT-nnn.antes.log` vermelho do mesmo comando são reprovados (exit 1) num relatório com a coluna `Antes`; 0 reprovações nos relatórios sem a coluna.
- [ ] S2: o `sabotagem.sh` sai 0 quando o teste pega a sabotagem e 2 quando não pega, com o hash da árvore de trabalho igual antes e depois nos 2 casos.
- [ ] S2: o custo extra em tokens dos itens 2, 6 e 7 medido na mesma tarefa de exemplo, com e sem os passos novos, e registrado no BUILD_REPORT.
- [ ] S3: na fixture com complexidade 15 e um bloco duplicado, 2 de 2 achados na seção e exit 0; sem as ferramentas, 2 de 2 métricas como "não medido", exit 0 e 0 ocorrências de "0 achados".
- [ ] Todas as fatias: suíte inteira verde e CI 18 de 18.

---

## Fatia S1 — Qualidade por stack (itens 1, 3, 4)

### Acceptance Tests — S1

> EARS (keywords em inglês, corpo em PT-BR). "Slot cheio" = `project.lint_cmd` ou `project.typecheck_cmd` não
> vazio no `sdd/config.yaml` do projeto. Os logs seguem o contrato de evidência: 1ª linha `$ <comando>`, saída
> verbatim, última linha `[exit=<n>]`.

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-001 | Event-driven | **When** o `report-lint.py` confere um BUILD_REPORT de um projeto com `project.lint_cmd` cheio, the system **shall** exigir `sdd/reports/evidence/{F}/LINT.log` com a 1ª linha `$ <o comando do slot>` e a última `[exit=0]`, e, com `project.typecheck_cmd` cheio, o mesmo para `TIPOS.log`; log ausente, ignorado pelo git, de outro comando ou terminado em `[exit=` diferente de 0 ⇒ exit 1 com o conserto em 1 linha; a exceção é a dívida antiga: `[exit≠0]` com `LINT.antes.log`/`TIPOS.antes.log` do mesmo comando do slot também `[exit≠0]` ⇒ aviso, não violação | test |
| AT-002 | State-driven | **While** `project.lint_cmd` e `project.typecheck_cmd` estão vazios, the system **shall** aprovar o BUILD_REPORT (exit 0): com a linha `lint: slot vazio`, sem aviso; sem ela, com um aviso que nomeia a linha que falta, nunca com violação, e sem nunca bloquear o Build por falta de linter | test |
| AT-003 | Event-driven | **When** a tarefa do Build chega ao passo de verificar, the system **shall** mandar rodar `project.lint_cmd` e `project.typecheck_cmd` (os cheios) sobre os arquivos da tarefa, tratar erro como falha da escada de retry e, no fim do Build, gravar `LINT.log`/`TIPOS.log`; o texto da `sdd-build` nomeia os dois slots, os dois logs e a linha `lint: slot vazio` | test |
| AT-004 | Event-driven | **When** o `init` ou o `sync` gera o AGENTS.md num projeto Python ou JS/TS, the system **shall** escrever um bloco `### Qualidade ao construir` com as 6 regras gerais (em frase positiva) e as regras da stack, lidas de `.agents/skills/sdd-build/web/references/CATALOGO_QUALIDADE.md` pelo único leitor dele; sem stack reconhecida, só as gerais; rodar `sync` duas vezes deixa 1 bloco só | test |
| AT-005 | Unwanted | **If** o catálogo de qualidade não está no pacote, o Python não está pronto ou o leitor falha, **then** the system **shall** gerar o AGENTS.md com o ponteiro para as regras e um aviso com a causa (nunca o bloco vazio em silêncio), e o bloco de segurança fica como estava | test |
| AT-006 | Event-driven | **When** o `checar.sh` roda num projeto com stack reconhecida e sem linter ou checagem de tipos (sem config do linter e com os slots vazios), the system **shall** imprimir um aviso ⚠️ com o comando sugerido da stack (Python: `ruff check` e `mypy`; JS/TS: `eslint` e `tsc --noEmit`; PHP: `phpcs`, sem comando de tipos) e o comando de instalar, na voz da `como-falar.md`, sem instalar nada e sem gravar arquivo (hash da árvore antes = depois) | test |
| AT-007 | Event-driven | **When** a `sdd-new-session` acha `lint_cmd` e `typecheck_cmd` sem evidência, the system **shall** rodar `checar.sh --linter`, traduzir a sugestão na voz da `como-falar.md` (o que o linter confere) e perguntar (`[D2]`) se grava os comandos no `sdd/config.yaml` da frente, gravando só com o sim e sem instalar nada | test |
| AT-008 | Event-driven | **When** o `gerar-starter.py` gera o starter numa pasta temporária, the system **shall** levar as regras de qualidade e o passo de verificar com lint e tipos no texto da `sdd-build` do starter (que não tem AGENTS.md), sem citar `sdd/bin/…`, e o starter gerado **shall** passar nos `grep` da F29 (0 ocorrências de `Não cite nem resuma`, `comece com esta linha`, `versão atual: http`) | test |
| AT-009 | Non-regression | The system **shall continue to** passar a suíte inteira (`python3 -m unittest discover -s tests`), o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main`, com o bloco `### Segurança ao construir` do AGENTS.md igual ao de antes | test |

**Padrões considerados:**
- **While:** AT-002 (slots vazios).
- **If–Then:** AT-005 (catálogo, Python ou leitor fora). O `lint_cmd` que não aceita lista de arquivos é decisão
  do Design (cair para o repositório inteiro sem bloquear pelo que é antigo), não AT.
- **Where:** N.A. — não há flag de config nova na S1 (D1: os slots já existem).

### Fora da S1

- Instalar linter (D2: só propõe).
- Slot novo de tipos (D1: o `project.typecheck_cmd` já existe em `sdd/config.example.yaml:12`).
- Bloquear por código antigo: o lint do Build vale para os arquivos da tarefa.

---

## Fatia S2 — Disciplina de teste (itens 2, 6, 7)

### Acceptance Tests — S2

> "Comportamento novo" = AT `true` no BUILD_REPORT cuja linha no DEFINE tem o gate `kind` `test` ou `cmd` e não é
> `shall continue to` (D3). "Coluna `Antes`" = a coluna da tabela de critérios do BUILD_REPORT que cita o
> `AT-nnn.antes.log` (ou `N.A. (<motivo>)`). Os logs seguem o contrato de evidência (1ª linha `$ <comando>`, saída
> verbatim, última linha `[exit=<n>]`).

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-010 | Event-driven | **When** o `report-lint.py` confere um BUILD_REPORT cuja tabela de critérios tem a coluna `Antes`, the system **shall** exigir, para cada AT `true` de comportamento novo, `sdd/reports/evidence/{F}/AT-nnn.antes.log` citado na coluna, existente, não ignorado pelo git, com a 1ª linha igual à do `AT-nnn.log` e a última `[exit=<n>]` com `n` fora de 0, 126 e 127 (vermelho de verdade); ausente, verde, de outro comando, sem `[exit=` ou `N.A.` num AT de comportamento novo ⇒ exit 1 com o conserto em 1 linha | test |
| AT-011 | Unwanted | **If** o AT `true` é `shall continue to` (não-regressão), **then** the system **shall** exigir o `AT-nnn.antes.log` do mesmo comando com `[exit=0]` (verde antes) e reprovar (exit 1) o antes vermelho; AT com gate `manual-ux` (exit 4) ou de `kind` fora de `test`/`cmd` aceita `N.A. (<motivo>)` na coluna | test |
| AT-012 | State-driven | **While** a tabela de critérios do BUILD_REPORT não tem a coluna `Antes` (relatório anterior à S2), the system **shall** aprovar o relatório como antes, com 1 aviso que nomeia a coluna que falta, nunca com violação; sem o DEFINE da feature, o mesmo aviso com a causa | test |
| AT-013 | Event-driven | **When** o `sdd/bin/sabotagem.sh` roda com o AT, o comando, o arquivo e o trecho a trocar declarados no DESIGN, the system **shall** extrair `git archive HEAD` numa pasta temporária, rodar o comando na cópia limpa (precisa sair 0), aplicar a troca na cópia, rodar de novo e: vermelho com a sabotagem ⇒ exit 0 e `sdd/reports/evidence/{F}/AT-nnn.sabotagem.log`; verde com a sabotagem ⇒ exit 2 com "o teste não pega o defeito"; nos dois casos a cópia é apagada e, fora o próprio log, a árvore de trabalho fica idêntica (hash antes = depois) | test |
| AT-014 | Unwanted | **If** o trecho a trocar não aparece no arquivo, o caminho do arquivo sai da cópia (absoluto ou com `..`), o comando já falha na cópia limpa ou sai 126/127, **then** the system **shall** sair 3 (inconclusivo) ou 64 (uso) com a causa, sem gravar log de sucesso e com a árvore de trabalho idêntica | test |
| AT-015 | Event-driven | **When** a tarefa do Build passa pelos seus passos, the system **shall** ter no texto da `sdd-build` (Open) o vermelho antes do verde (`AT-nnn.antes.log` e a coluna `Antes`), a sabotagem declarada no DESIGN rodada pelo `sabotagem.sh` e o passo **Refatorar** entre Verificar e Marcar, ligado por padrão e pulado (dito no relatório) com `build.refatorar: false`; o `config.example.yaml` tem `build.refatorar`; o `BUILD_REPORT_TEMPLATE.md` tem a coluna `Antes`; a `sdd-design` pede a tabela de sabotagens na estratégia de testes (uma por AT de superfície de risco do `CRITERIO_DANO.md`, ≥ 1 por feature); o `MODO_WEB.md` e o starter levam o vermelho antes do verde e o refatorar sem citar `sdd/bin/…` | test |
| AT-016 | Non-regression | The system **shall continue to** passar a suíte inteira, o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main`, e a aprovar os BUILD_REPORTs sem a coluna `Antes` (o da S1 e os das fixtures) | test |

**Padrões considerados:**
- **Where:** o `build.refatorar: false` é a flag nova, mas o efeito é texto de skill (o agente pula o passo); fica
  dentro do AT-015, conferido por teste de texto.
- **While:** AT-012 (relatório anterior à S2).
- **If–Then:** AT-011 e AT-014.

### Fora da S2

- Exigir a sabotagem no `report-lint.py` (o `≥ 1 por feature` fica no texto da build e no DESIGN; conferir por
  máquina é candidato depois da S3).
- Mutação completa (Stryker, mutmut).
- Coluna `Antes` obrigatória em relatório antigo (AT-012: só aviso).

---

## Fatia S3 — Métricas no diff, só aviso (itens 5, 8)

### Acceptance Tests — S3

> "Diff" = o que a frente acrescentou ou mudou contra a base (o ponto comum com `origin/<project.default_branch>`),
> com o que ainda não foi commitado e os arquivos novos. "Função do diff" = função com ao menos uma linha no diff.
> "Seção" = o bloco `## Qualidade (avisos)`, impresso em stdout pelo `sdd/bin/metricas-diff.sh`. Limites do D5.

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|----|--------|-----------------|---------------|
| AT-017 | Event-driven | **When** o `sdd/bin/metricas-diff.sh` roda num projeto cujo diff traz uma função de complexidade 15 e um bloco duplicado, com `lizard` e `jscpd` no PATH, the system **shall** imprimir a seção com os dois achados (arquivo, linhas, valor e limite), sair 0 e deixar a árvore idêntica (hash antes = depois) | test |
| AT-018 | Unwanted | **If** `lizard` ou `jscpd` não está no PATH, sai com erro ou devolve saída que o script não entende, **then** the system **shall** escrever naquela métrica `não medido: <ferramenta> ausente` com o comando de instalar (ou `não medido: <ferramenta> falhou` com a causa), medir a outra normalmente, sair 0, nunca escrever "0 achados" nem "nenhum" para a métrica não medida e nunca instalar nada | test |
| AT-019 | State-driven | **While** uma função ou um par duplicado não tem nenhuma linha no diff, the system **shall** deixá-lo fora da seção; diff sem arquivo de código dá `não medido: nenhum arquivo de código no diff`; função do diff sem achado conta como medida | test |
| AT-020 | Where | **Where** `qualidade.max_complexidade`, `qualidade.max_linhas`, `qualidade.max_parametros` ou `qualidade.min_tokens` está no `sdd/config.yaml`, the system **shall** usar o valor; ausente ou vazio, o padrão 10, 60, 5 e 50; valor que não é inteiro ≥ 1 ⇒ exit 64 com a chave e o conserto | test |
| AT-021 | Event-driven | **When** o `report-lint.py` confere um BUILD_REPORT, the system **shall** exigir a seção `## Qualidade (avisos)` não vazia, fora de bloco cercado, se o `sdd/config.yaml` tem o mapa `qualidade:` (exit 1 com o conserto em 1 linha); sem o mapa (projeto anterior à S3), a falta dela é só aviso; achado na seção nunca reprova | test |
| AT-022 | Event-driven | **When** o Build termina as tarefas, the system **shall** ter no texto da `sdd-build` (Open) a chamada do `metricas-diff.sh` antes do relatório, com a seção colada no BUILD_REPORT; o `BUILD_REPORT_TEMPLATE.md` tem a seção, o `config.example.yaml` tem `qualidade:` com os 4 limites, a `EVIDENCIA.md` e o `cli-conventions.md` descrevem o contrato; o `MODO_WEB.md` e o starter levam o texto das métricas sem citar `sdd/bin/…` | test |
| AT-023 | Non-regression | The system **shall continue to** passar a suíte inteira, o `publish-gate` em modo CI sobre uma cópia de `git archive` e o `check-versions.py --base origin/main`, e a aprovar os BUILD_REPORTs sem a seção em projeto sem `qualidade:` | test |

**Padrões considerados:** todos os cinco; While em AT-019, Where em AT-020, If–Then em AT-018.

### Fora da S3

- Reprovar por métrica; tendência entre frentes; medir o repositório inteiro.
- Instalar `lizard` ou `jscpd` (D2: só o comando), inclusive por `npx`, que baixaria o pacote.
- Código do próprio método (`sdd/`, `.agents/` e pastas de agente) no projeto do aluno.

---

## Clarifications

### Session 2026-11-23

- [x] (escopo) D1 — Erro de lint ou de tipos no Build bloqueia ou avisa, e onde fica o comando de tipos? → **Bloqueia** com o slot cheio, pela escada de retry; tipos no slot **`project.typecheck_cmd`, que já existe** (o ESCOPO supunha slot novo; o passo 5b da `sdd-build` já o lê no fim do Build). Integrado em AT-001, AT-003.
- [x] (restrições) D2 — Projeto sem linter: instala ou propõe? → **Propõe** o comando exato; slot gravado só com o sim. Integrado em AT-006, AT-007.
- [x] (escopo) D3 — Vermelho antes do verde vale para quais ATs? → ATs `test`/`cmd` de comportamento novo; `shall continue to` exige verde antes; exit 4 fora. Integrado em AT-010, AT-011 (e AT-012 para o relatório anterior à S2).
- [x] (escopo) D4 — Sabotagem: quantas e quem escolhe? → Uma por AT de superfície de risco (critério do `CRITERIO_DANO.md`) e ≥ 1 por feature, **declaradas no DESIGN**. Integrado em AT-013, AT-014, AT-015.
- [x] (NFRs) D5 — Limites das métricas → complexidade 10, 60 linhas, 5 parâmetros, `jscpd --min-tokens 50`, em `qualidade.*` do config. Integrado em AT-020.
- [x] (integrações) D6 — Onde fica o catálogo? → Arquivo novo na skill da build (`web/references/CATALOGO_QUALIDADE.md`, para o starter receber; Decision 1 do DESIGN) e **script irmão novo** (não um modo do `seguranca-varredura.sh`: a taxonomia de stack é outra). Integrado em AT-004, AT-005.
- [x] (sinal de conclusão) D7 — Refatorar depois do verde vem ligado? → Ligado, `build.refatorar: false` desliga. Sai o "desligado no modo `lite`": a `sdd-build` não tem esse modo (o `lite` é perfil dos laços da `sdd-loop-builder`). Integrado em AT-015.

### Session 2026-11-24 (S2, iterate)

- [x] (escopo) Como o `report-lint.py` cobra o vermelho antes sem reprovar todo relatório antigo? → Pela coluna `Antes` da tabela de critérios: com ela, a cobrança é estrita; sem ela, aviso (AT-012). Mesmo molde da linha `lint: slot vazio` da S1 (Decision 3). Decidido pelo agente com a recomendação, dentro de D3.
- [x] (escopo) A sabotagem confere a cópia limpa antes? → Sim: vermelho com a sabotagem só prova algo se o comando passa sem ela (AT-013, AT-014). Decidido pelo agente.

### Session 2026-11-25 (S3, iterate)

- [x] (escopo) Quando a falta da seção reprova? → Com o mapa `qualidade:` no config (projeto criado ou atualizado para a S3); sem ele, aviso. O mesmo molde das Decisions 3 e 8 (AT-021). Decidido pelo agente com a recomendação, dentro do ESCOPO ("o `report-lint.py` exige só que a seção exista").
- [x] (escopo) Função "nova ou alterada"? → A que tem ao menos uma linha no diff; par duplicado, idem em pelo menos um dos lados (AT-019). Decidido pelo agente.
- [x] (restrições) Ferramenta que falha no meio? → "não medido" com a causa, exit 0: a métrica nunca segura o Build (AT-018). Decidido pelo agente.

### Segurança

- S3: o `metricas-diff.sh` roda duas ferramentas locais do PATH sobre arquivos do projeto, sem rede, sem instalar e sem gravar na árvore (a saída temporária fica numa pasta de `mktemp`, apagada ao sair). O `jscpd` recebe um config próprio vazio, para o `.jscpd.json` do projeto não mudar a medição. Nomes de arquivo e de função entram na seção sem quebra de linha nem crase.
- S1: N.A. — scripts locais que só leem o projeto (o `checar.sh` não instala nem grava); sem login, rota, dado de terceiros ou chamada paga. A fatia S2 trata a única superfície (sabotagem em cópia descartável).
- S2: a superfície é o `sabotagem.sh`, que roda um comando do projeto e troca texto num arquivo. Ele roda na cópia de `git archive HEAD` numa pasta temporária, recusa caminho absoluto ou com `..` (AT-014), apaga a cópia ao sair (também por sinal) e deixa a árvore de trabalho idêntica, fora o log (AT-013, hash conferido no teste). O comando vem do DESIGN do próprio projeto, como o do Verify Gate: nenhum dado de terceiros, rede ou chamada paga.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "! grep -rlE 'Não cite nem resuma|comece com esta linha|versão atual: http' .agents/skills && /usr/bin/python3 scripts/check-versions.py --base origin/main && T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && test -f tests/test_f30_report_lint.py && test -f tests/test_f30_textos.py && test -f tests/test_f30_agents_qualidade.py && test -f tests/test_f30_checar_linter.py && test -f tests/test_f30_starter.py && test -f tests/test_f30_vermelho_antes.py && test -f tests/test_f30_sabotagem.py && test -f tests/test_f30_textos_s2.py && test -f tests/test_f30_metricas.py && test -f tests/test_f30_textos_s3.py && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_f30_*.py' && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 e AT-002 em `tests/test_f30_report_lint.py`; AT-003 em `tests/test_f30_textos.py`; AT-004 e
AT-005 em `tests/test_f30_agents_qualidade.py` (init/sync em fixtures Python, JS e sem stack; catálogo ausente);
AT-006 em `tests/test_f30_checar_linter.py` (hash da árvore antes e depois); AT-007 em `tests/test_f30_textos.py`;
AT-008 em `tests/test_f30_starter.py` (gera o starter numa pasta temporária) e no `grep` do gate; AT-009 na
suíte inteira, no `publish-gate` e no `check-versions.py`. S2: AT-010 a AT-012 em `tests/test_f30_vermelho_antes.py`;
AT-013 e AT-014 em `tests/test_f30_sabotagem.py` (repositório git temporário; hash da árvore antes e depois); AT-015 em
`tests/test_f30_textos_s2.py` (inclui o starter gerado numa pasta temporária); AT-016 na suíte inteira, no
`publish-gate` e no `check-versions.py`. S3: AT-017 a AT-021 em `tests/test_f30_metricas.py` (fixture de complexidade
15 e bloco duplicado; PATH restrito sem as ferramentas; hash da árvore); AT-022 em `tests/test_f30_textos_s3.py` (inclui
o starter gerado); AT-023 na suíte, no `publish-gate` e no `check-versions.py`. O gate roda sobre o que está commitado (`git archive
HEAD`). Baseline vermelho: os 5 `test -f` da S1 (os 3 da S2 e os 2 da S3) saem 1 antes do código. Eles existem porque, no Python 3.9 do sistema, o `discover` sem nenhum teste sai 0 (medido em 2026-11-23: "Ran 0 tests … OK"), e assim não provaria nada (LM-002).

---

## Out of Scope

- Itens 9 a 15 da avaliação: dimensão de manutenibilidade na revisão (reavaliar depois da S3), código morto,
  cobertura no diff, hook de formatação, regra de dependência da *Clean Architecture* (opção futura da Turma
  Bravo), mutação completa, checklist SOLID.
- Instalar ferramenta no projeto do aluno sem o sim dele.
- Medir a nota de aderência (candidata a frente seguinte).

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Technical | Só bloqueia o que é objetivo: teste e erro de lint ou de tipos com o slot cheio; métrica só avisa; ferramenta ausente é "não medido" | Nenhum gate subjetivo; slot vazio nunca reprova o Build |
| Technical | Texto novo de skill em frase positiva, sem banner e sem "não cite" (F29) | Grep da F29 no gate (AT-008) |
| Technical | SKILL.md ≤ 500 linhas (LM-038); `sdd-build/SKILL.md` tem 357 e `sdd-build/web/MODO_WEB.md` (que vira o SKILL.md do starter) tem 484 | Regras do starter vão para `web/references/`, citadas pelo modo |
| Technical | Texto de skill da `scripts/starter/lista.txt` não cita `sdd/bin/…` (LM-035) | O starter recebe as regras como texto, não pelo script |
| Technical | Arquivo novo no pacote entra no `MANIFEST.txt` no mesmo commit (LM-037); bash 3.2 e Git Bash (F16W); `subprocess` de teste com `encoding="utf-8"` (LM-014); plataforma pelas constantes de `tests/apoio.py` (LM-042) | Checklist do Design |
| Resource | Starter regenerado a cada fatia publicada, em `~/rdd-public/sdd-starter` | Passo da release |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `.agents/skills/sdd-build/` (SKILL.md, `references/`, `web/`), `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, `.agents/skills/sdd-new-session/`, `AGENTS.md.tmpl`, `bin/sdd-open.sh`, `sdd/bin/report-lint.py`, `sdd/bin/` (script irmão novo; na S2, `sabotagem.sh`), `.agents/skills/sdd-design/`, `sdd/config.example.yaml`, `scripts/gerar-starter.py`, `tests/` | É o pacote do método; o aluno recebe pelo `init`/`sync` e pelo starter |
| **KB Domains** | nenhum | O repositório não tem `sdd/kb/`; a `sdd-kb` cria uma base quando houver domínio a catalogar |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | Muda texto de skill (instrução ao agente de desenvolvimento), não prompt que roda em produção; nenhum sinal forte |
| **CONTEXTO de domínio** | nenhum (pulado: sem mapa de domínios em `sdd/patterns/dominio.md`; os achados com linha do ESCOPO §2 fazem esse papel) | — |
| **Governança** | N.A. — não trata dinheiro, saldo, tributo, folha nem dado pessoal (texto de skill e scripts do método); N.A. decidido pelo Roberto no escopo da frente | 2026-11-23 |
| **Segurança** | S1: N.A. — sem login, rota, dado de terceiros ou chamada paga. S2: só o `sabotagem.sh` (cópia descartável, caminho contido, árvore intacta). S3: ferramentas locais só de leitura (Clarifications § Segurança) | 2026-11-25 |
| **Desempenho** | N.A. — sem banco | 2026-11-23 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | O molde `{{SEGURANCA}}` (`bin/sdd-open.sh:446-470`) serve para `{{QUALIDADE}}` sem mexer no da segurança | Refatorar a geração do AGENTS.md; risco para AT-009 | [x] lido em 2026-11-23 |
| A-002 | O `sdd-build/web/MODO_WEB.md` é a fonte do SKILL.md da build no starter e pode citar `references/…` da pasta `web/` | As regras não chegam ao starter (AT-008) | [x] `scripts/gerar-starter.py:333-357` |
| A-003 | Detectar a stack por arquivo (`pyproject.toml`/`requirements.txt`/`*.py`, `package.json`/`tsconfig.json`, `composer.json`/`*.php`) basta para sugerir o linter | Sugestão errada; o aluno recusa | [ ] Design |
| A-004 | O `lint_cmd` dos projetos aceita lista de arquivos na maioria dos casos | Cair para o repositório inteiro, sem bloquear pelo que é antigo (Design) | [ ] Design |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Achados com arquivo e linha no ESCOPO §2 |
| Users | 3 | 3 personas com dor própria |
| Goals | 3 | MUST/SHOULD por fatia |
| Success | 3 | Contagens e exit codes |
| Scope | 3 | S1, S2 e S3 com ATs (AT-001 a AT-023) |
| **Total** | **15/15** | |

---

## Open Questions

None for S3 — ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-23 | define-agent | S1 (itens 1, 3, 4) com D1–D7 decididas; S2 e S3 reservadas |
| 1.6 | 2026-11-25 | iterate | S3 (itens 5, 8): AT-017 a AT-023, Clarifications da S3, `test -f` dos 2 testes novos no gate. Aditiva: S1 e S2 não mudam |
| 1.5 | 2026-11-24 | iterate | S2 (itens 2, 6, 7): AT-010 a AT-016, Clarifications da S2, segurança do `sabotagem.sh`, `test -f` dos 3 testes novos no gate. Aditiva: a S1 não muda |
| 1.4 | 2026-11-23 | build | AT-006: PHP sem `php -l` (achado 1 do avaliador, ciclo 1). O `php -l` confere um arquivo por chamada e não tem modo de projeto inteiro: no slot de tipos, que roda como está (Decision 4), ele leria a entrada padrão e travaria o Build. Fica o `phpcs` |
| 1.3 | 2026-11-23 | build | AT-007: a tradução fica no passo dos slots da new-session, não na tabela do `--frente` (Decision 6: o `--frente` não fala de linter) |
| 1.2 | 2026-11-23 | design-agent | AT-001: exceção da dívida antiga pelo log de antes (revisão do DESIGN, N1) |
| 1.1 | 2026-11-23 | design-agent | AT-002: sem a linha `lint: slot vazio` é aviso, não violação (o repositório e as fixtures não têm config; Decision 3 do DESIGN). AT-004: catálogo em `sdd-build/web/references/` (Decision 1) |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md` (S3). UX Review pulado: sem tela; o
texto ao aluno segue as `references/como-falar.md` das skills tocadas.
