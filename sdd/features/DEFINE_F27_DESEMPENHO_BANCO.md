# DEFINE: F27 — desempenho do banco (`sdd-desempenho-banco`)

> Uma skill nova, no molde da `sdd-seguranca`, com um catálogo de 17 fichas de desempenho de banco (Supabase e Postgres), uma varredura estática que só avisa e nunca bloqueia, os modos Define, Design e release automáticos (só leem o repositório) e um diagnóstico do banco no ar a pedido, só de leitura e com consentimento a cada execução.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F27_DESEMPENHO_BANCO |
| **Date** | 2026-11-17 |
| **Author** | define-agent (worktree `sdd-open-f27-db-performance`; branch `feat/f27-db-performance`, de `origin/main` `2204a14` = `v2.21.0`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F27_DESEMPENHO_BANCO.md` (fechado em 2026-11-17; abordagem A, decisões D1–D13) |

---

## Problem Statement

O aluno que constrói com IA e Supabase publica migrations e consultas que ficam lentas quando a tabela cresce (política RLS que chama `auth.uid()` uma vez por linha, chave estrangeira sem índice, lista sem limite, contagem exata) e, quando o app fica lento, não sabe por onde começar nem como olhar o banco sem arriscar mexer nele: nenhuma das 22 skills do SDD Open fala de índice, `EXPLAIN`, advisor, consulta lenta ou pooler, e o Define, o Design e a `sdd-release` não perguntam nem conferem nada disso.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Aluno iniciante com Supabase (plano Free ou Nano) | percorre o fluxo e publica com a `sdd-release` | escreve a política e a chave estrangeira do jeito que a IA sugeriu; descobre a lentidão em produção, sem saber o que olhar |
| Aluno com o app lento já no ar | pede ajuda ao agente | não sabe ler o advisor nem o `inspect db`; corre o risco de apagar índice "não usado" ou de rodar teste de carga contra produção |
| Aluno que usa o agente na web, sem terminal | lê as skills e confere à mão | precisa de cada ficha na forma "confira à mão" e do roteiro do painel |
| Aluno sem banco (script, CLI, site estático) | usa o mesmo pacote | pergunta de banco que não se aplica é ruído e custo de contexto |
| Mantenedor do Open | mantém o pacote público e agnóstico | a skill não pode bloquear publicação, escrever no banco nem trazer número ou nome do repositório privado |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | skill nova `sdd-desempenho-banco` 1.0.0 em `.agents/skills/sdd-desempenho-banco/`: `SKILL.md` com "Como falar com o aluno", `manifest.json`, `references/CATALOGO_DESEMPENHO.md` (fichas P01–P17), `references/como-falar.md`, `evals/cases.json`; modos Define, Design, release (varredura) e diagnóstico a pedido |
| **MUST** | `sdd/bin/desempenho-varredura.sh`: só leitura, sem rede, padrões lidos do catálogo, stack pela detecção da segurança, dispensa por comentário com motivo, teto de avisos na tela; exit `0` · `1` · `64`, nunca `2` |
| **MUST** | `sdd/bin/desempenho-diagnostico.sh`: coleta pelo Supabase CLI só com `--consentimento` e só pela lista fixa de comandos de leitura; interpreta a saída salva (advisor e `inspect db`) com as regras D7; mascara literais |
| **MUST** | ganchos: `sdd-define` (passo de desempenho, sem trava), `sdd-design` (seção `## Desempenho`), `sdd-release` (varredura no 0a como aviso), `MANIFEST.txt`, `scripts/starter/lista.txt` (a skill chega ao starter pelo gerador), README, README.pt-BR, docs e `docs/cli-conventions.md` |
| **MUST** | nunca escreve no banco (D6); a correção sai como migration proposta para o fluxo SDD |
| **MUST** | texto próprio; fixtures sintéticas; nenhum número ou nome medido no repositório privado |
| **SHOULD** | cenários de comportamento do modo Define em contexto novo (LM-011): 2 cenários × 3 execuções |
| **COULD** | agendamento do diagnóstico (fora: D8; só a linha apontando o monitor oficial) |

---

## Success Criteria

- [ ] Migration com `using (auth.uid() = user_id)` ⇒ `desempenho-varredura.sh` sai 1 com `P01 … <arquivo>:<linha>`; a mesma política com `(select auth.uid())` ⇒ sai 0.
- [ ] `references <tabela>(id)` sem índice na coluna ⇒ P03; com `create index … (<coluna>)` na mesma migration ou em outra ⇒ nada.
- [ ] Toda ficha com padrão tem 1 caso que acusa e 1 que não acusa nos testes (ao menos 12 pares).
- [ ] Em todos os casos dos testes da varredura, o exit fica em {0, 1, 64}: zero saídas `2`.
- [ ] Projeto sem banco ⇒ exit 0 em no máximo 2 linhas; no Define, N.A. em 1 linha sem pergunta.
- [ ] Coleta sem `--consentimento` ⇒ 0 chamadas registradas pelo `supabase` falso; com consentimento ⇒ 100% das chamadas na lista fixa de leitura.
- [ ] "Índice não usado" com estatísticas de menos de 30 dias ou de idade desconhecida ⇒ 0 recomendações de apagar.
- [ ] Diagnóstico com senha numa string de conexão ⇒ 0 senhas no relatório; com texto de consulta que traz instrução ao agente ⇒ a recomendação é a mesma da fixture sem a instrução.
- [ ] Linha de base vermelha: os testes novos falham em `2204a14` (`v2.21.0`).
- [ ] Sabotagens: ao menos 5 mutantes (varredura sai 2; dispensa sem motivo aceita; ficha de Supabase dispara sem Supabase; coleta roda sem consentimento; índice "não usado" recomendado para apagar sem idade) derrubam, cada um, um teste nomeado.
- [ ] Verify Gate numa cópia de `git archive` sai 0, com a suíte inteira; a contagem de testes só sobe a partir da medida em `2204a14` (o Build registra os dois números).
- [ ] CI do PR verde nos 3 sistemas (Ubuntu, macOS e Windows com Git Bash e Python nativo).
- [ ] Pacote montado contém a skill e os 2 scripts (`MANIFEST.txt`) e nenhum documento da frente.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `sdd/bin/desempenho-varredura.sh` acha, numa linha acrescentada de um arquivo coberto pela ficha, o padrão de uma ficha com padrão (no mínimo P01: política com `auth.uid()`, `auth.jwt()` ou `current_setting(` fora de um `(select …)`), o script **shall** sair 1 e imprimir, por achado, `⚠️ Pnn <gravidade> <arquivo>:<linha>`, e o "confira à mão" da ficha uma vez por item; cada padrão **shall** ter um caso que não acusa (ex.: a mesma política com `(select auth.uid())`, `count: 'planned'`, o padrão dentro de comentário de documentação); sem achado, **shall** sair 0 com `RESULTADO: NADA ACHADO` | test |
| AT-002 | Unwanted | **If** uma migration acrescentada declara chave estrangeira (`references <tabela>` na coluna, ou `foreign key (<coluna>) references …`) e nenhuma migration da árvore, a mesma ou outra, cria índice cuja 1ª coluna é a coluna da chave, **then** a varredura **shall** acusar `⚠️ P03 <gravidade> <arquivo>:<linha da chave>`; com esse índice, **shall** não acusar; com um índice composto em que a coluna da chave não é a 1ª, **shall** acusar | test |
| AT-003 | State-driven | **While** a base (`origin/<project.default_branch>`, ou `--base <ref>`) já tinha o mesmo achado (a mesma ficha, no mesmo arquivo, no mesmo texto de linha), a varredura **shall** não listá-lo nem contá-lo para o exit 1 (um achado que a base não tinha, como a chave antiga que perdeu o índice por um `drop index` novo, conta como novo), e **shall** imprimir uma linha `ℹ️ <n> achado(s) que já existiam — liste com --tudo`; **when** recebe `--tudo`, **shall** listar também esses, marcados `(já existia)`; **if** a base não existe, **then** **shall** contar toda linha rastreada como acrescentada e dizer isso numa linha | test |
| AT-004 | Optional feature | **Where** a linha do achado, ou a linha imediatamente acima quando ela é só comentário, traz `sdd-desempenho-banco: aceito Pnn — <motivo>` com o id do achado e motivo com 3 ou mais caracteres, a varredura **shall** tirar o achado dos avisos e listá-lo uma vez como `✔ aceito Pnn <arquivo>:<linha> — <motivo>`; **if** o motivo está vazio, é curto demais ou o id não casa, **then** **shall** manter o achado e acrescentar o aviso de que a dispensa sem motivo (ou de outro item) não vale; a dispensa no fim de uma linha de código **shall** valer só para o achado dessa linha | test |
| AT-005 | Unwanted | **If** a varredura recebe opção desconhecida, slot inválido, catálogo ilegível ou roda fora de um repositório git, **then** **shall** sair 64 com a causa e o conserto em 2 linhas; em nenhuma entrada **shall** sair 2; **if** há mais de 5 avisos, **then** **shall** mostrar os 5 mais graves (alta, media, baixa; empate pelo id), com o "confira à mão" de cada ficha uma vez na tela e uma vez no `--saida`, e a linha `… e mais <k> aviso(s): lista inteira em <arquivo>`; **when** recebe `--saida <arquivo>`, **shall** gravar ali a lista inteira (avisos, aceitos e os que já existiam) | test |
| AT-006 | State-driven | **While** o projeto não tem banco (a stack não inclui `supabase` e não há `.sql` rastreado fora das pastas do SDD e dos agentes), a varredura **shall** sair 0 com `RESULTADO: SEM BANCO` em no máximo 2 linhas; a stack **shall** vir de `seguranca-varredura.sh --stack` (o slot `security.stack` passa por cima), sem uma 2ª detecção; **while** a stack não inclui `supabase`, as fichas de stack `supabase` **shall** não disparar | test |
| AT-007 | Unwanted | **If** `sdd/bin/desempenho-diagnostico.sh` é chamado para coletar sem `--consentimento`, **then** **shall** sair 64 sem executar nenhum comando externo (um `supabase` falso no PATH, que registra cada chamada, fica com o registro vazio); **when** coleta com `--consentimento`, **shall** chamar só os comandos da lista fixa de leitura (subcomandos de `supabase inspect db` e o de advisors que o Design confirmar), nunca outro; e toda consulta SQL que a skill manda o agente rodar pelo MCP **shall** estar em `references/` e ser só de leitura (o teste reprova `insert`, `update`, `delete`, `merge`, `alter`, `create`, `drop`, `truncate`, `grant`, `revoke`, `vacuum`, `reindex`, `cluster`, `refresh`, `analyze` fora de `explain`, `pg_cancel_backend`, `pg_terminate_backend`, e `explain analyze` de escrita fora de `begin … rollback`) | test |
| AT-008 | Event-driven | **When** `desempenho-diagnostico.sh --ler <arquivo>` interpreta uma saída salva de advisor ou de `inspect db` (fixtures sintéticas), o relatório **shall**: recomendar apagar um índice "não usado" só com `--estatisticas-desde <data>` de 30 dias ou mais antes da execução, e, sem ela ou com menos, dizer que a idade das estatísticas é desconhecida ou curta e não recomendar apagar; marcar cada achado como "a confirmar", com o passo que confirma (log, `EXPLAIN` ou o painel), antes de qualquer correção; com consulta lenta na entrada, trazer antes de tudo a linha que manda conferir o tamanho da máquina e o swap; trocar por `?` os literais de texto e de número do texto das consultas; e mostrar no máximo 5 achados, do mais grave (nenhum `baixa` na tela enquanto um `media` ficar fora), com o total | test |
| AT-009 | Event-driven | **When** as skills e o pacote são lidos pelos testes, **shall** valer: o catálogo tem exatamente 17 fichas P01–P17, cada uma com o título e os 11 campos `stack`, `fase`, `gravidade`, `gatilho`, `padrao`, `arquivos`, `frase`, `evitar`, `at`, `confira`, `ref`, na ordem que o DESIGN fixar, sem `bloqueia` nem `agents`; a `sdd-desempenho-banco` tem os modos Define, Design, release e diagnóstico, "Como falar com o aluno", `manifest.json` e `evals/cases.json`; a `sdd-define` tem um passo de desempenho, rodado pela própria sessão e sem trava, que responde N.A. em 1 linha sem banco, faz no máximo 1 pergunta de volume, não propõe AT quando a resposta é menos de 10 mil linhas em um ano e, com mais ou com "não sei", propõe até 3 fichas da fase `define`, uma decisão por item, e grava a linha `\| **Desempenho** \| … \|` no Technical Context; o `DESIGN_TEMPLATE` e a `sdd-design` têm a seção `## Desempenho` com as decisões das fichas da fase `design`; a `sdd-release` roda a varredura no 0a com `--saida`, trata `1` como CONCERNS e `64`/`127` como CONCERNS "não rodou", nunca aborta por ela e leva os avisos ao bloco do OK; a skill está em `MANIFEST.txt`, em `scripts/starter/lista.txt` e no README; todo texto novo passa no `tests/test_agnostico.py`, no `skill-lint.py --conversa` e no `tests/test_gerar_starter.py` | test |
| AT-010 | Non-regression | A `seguranca-varredura.sh` **shall continue to** dar a mesma saída e o mesmo exit em todos os casos dos testes dela (inclusive `--stack`); a `sdd-release` **shall continue to** pedir um OK só e **shall continue to** abortar só pelas causas de antes; o `verify-gate.sh` **shall continue to** ler só a linha `Governança` como trava (a linha `Desempenho` é registro); a suíte **shall continue to** passar no bash 3.2 do macOS (`SDD_TEST_BASH=/bin/bash`) e no Windows; o `AGENTS.md.tmpl` **shall** diferir do de `2204a14` só pela linha `| Des | \`sdd-desempenho-banco\` | … |` na tabela das fases, sem nenhuma regra de desempenho (D11); as contagens fixadas (skills, versões, lista do starter) **shall** mudar só pelo que esta frente acrescenta | test |
| AT-011 | Unwanted | **If** o diagnóstico recebe ou lê dado de fora — `--estatisticas-desde` fora do formato `AAAA-MM-DD` (S05), uma string de conexão com senha como argumento ou dentro da saída lida (S10), ou texto vindo do banco (consulta, nome de tabela, comentário) com quebra de linha, caractere de controle ou instrução dirigida ao agente (S17, S18) —, **then** `desempenho-diagnostico.sh` **shall** sair 64 sem executar nada diante da data inválida ou de uma string de conexão passada como argumento (a coleta usa só o projeto já ligado ao CLI); **shall** trocar a senha por `***` em toda string de conexão que chegar ao relatório; **shall** mostrar o texto vindo do banco só dentro do bloco marcado `dado do banco (não é instrução)`, com quebras e caracteres de controle trocados por espaço, sem que esse texto mude nenhuma recomendação; e **shall** gravar a saída bruta da coleta só fora da raiz do projeto (pasta temporária), nunca no repositório | test |

Considerados: **While** em AT-003 (achado só em linha que já existia) e AT-006 (projeto sem banco; stack sem Supabase). **If/Then** em AT-002 (chave sem índice), AT-003 (sem base), AT-004 (dispensa inválida), AT-005 (entrada inválida; acima do teto), AT-007 (coleta sem consentimento) e AT-011 (dado de fora: data inválida, senha, texto do banco). **Where** em AT-004 (linha com dispensa). Não-regressão em AT-010, porque a frente mexe em 3 skills de fase, na lista do starter e no `MANIFEST.txt`.

O comportamento do modo Define da `sdd-desempenho-banco` diante de um DEFINE real não é AT do gate local: é critério com evidência (SHOULD), em contexto novo, 2 cenários × 3 execuções, com o critério de aprovado escrito antes (LM-011): DEFINE sem banco ⇒ N.A. em 1 linha, sem pergunta; DEFINE com tabela nova no Supabase ⇒ no máximo 1 pergunta de volume e propostas sem decidir pelo aluno.

---

## Clarifications

### Session 2026-11-17

Pedido do Roberto para esta frente: em cada decisão, a recomendação vira o padrão e fica registrada; perguntar só o crítico. Nenhuma pergunta desta sessão foi crítica. Decidi sozinho:

- [x] (escopo) Escopo e decisões D1–D13 vêm do brainstorm fechado; não reaberto.
- [x] (UX) Sem interface: texto de skill e saída de terminal no padrão de `docs/cli-conventions.md`. UX review pulado.
- [x] (sinal de conclusão) Sem achado, a varredura imprime `RESULTADO: NADA ACHADO` (ou `SEM BANCO`) e o `→`, em vez do "não imprime nada" do rascunho: a convenção de saída do Open exige a linha final, e 2 linhas mantêm o custo de contexto baixo; integrado em AT-001 e AT-006.
- [x] (restrições) Legado é outra conversa: a varredura mostra só o que a mudança acrescenta (base `origin/<project.default_branch>`, como a segurança) e resume o que já existia numa linha, com `--tudo` para ver; integrado em AT-003. Motivo: num projeto com anos de migrations, centenas de avisos antigos esconderiam o novo.
- [x] (NFR) Teto fixo de 5 avisos na tela, lista inteira em `--saida`; sem slot novo de configuração (YAGNI); integrado em AT-005.
- [x] (integrações) Um script para o diagnóstico, `desempenho-diagnostico.sh`, separado da varredura: a varredura continua sem rede; o diagnóstico coleta (só com `--consentimento`, lista fixa de comandos de leitura do CLI) e interpreta a saída salva, inclusive a do MCP, que o agente grava num arquivo; isso torna o consentimento, a leitura e as regras D7 testáveis sem banco; integrado em AT-007 e AT-008.
- [x] (dados) A idade das estatísticas entra por `--estatisticas-desde <data>` (o agente lê no MCP ou o aluno no painel); 30 dias é o mínimo para recomendar apagar índice "não usado"; sem a data, nunca recomenda; integrado em AT-008.
- [x] (NFR) No Define, o limite de volume para propor AT é 10 mil linhas em um ano: abaixo disso, as fichas viram só decisões do Design; integrado em AT-009.
- [x] (restrições) A varredura nunca aborta a publicação: até o `64`/`127` vira CONCERNS "não rodou" na `sdd-release` (D4: desempenho degrada, não vaza); integrado em AT-009.
- [x] (restrições) Verify Gate: a cópia de `git archive` tira as pastas de documentos da frente (`sdd/features`, `sdd/handoffs`, `sdd/reports`, `sdd/reviews`, `sdd/releases`, `sdd/contexto`) antes do `publish-gate`. Motivo: até a F26 publicar o `export-ignore`, os documentos desta branch (D12) fariam o G3 reprovar; nenhuma dessas pastas está no `MANIFEST.txt`, e o gate do CI fica como está (não se mexe em proteção). Depois do rebase sobre a F26, o Build confere se o `git archive` já os exclui e simplifica o comando.
- [x] (terminologia) "Chave estrangeira" (P03) é a coluna que aponta para outra tabela; "índice cobre a chave" quando a 1ª coluna do índice é a coluna da chave.

### Segurança

- [x] (segurança) Stack do repositório: nenhuma (detectada); valem só os itens de stack `todas`. Gatilhos pelo sentido: `banco` (o diagnóstico lê o banco do aluno; a varredura lê migrations), `dado-de-terceiros` (o texto das consultas pode trazer dado dos clientes do aluno), `ia` (o agente roda as consultas pelo MCP).
- [x] (segurança) S20 Agente com poder demais e sem teto — já atendido pelo AT-007 (só a lista fixa de comandos e de SQL de leitura; nunca escreve).
- [x] (segurança) S05, S10, S17 e S18 — aplicados (recomendação aceita como padrão, pedido do Roberto); integrados em AT-011. Inclui o ponto do revisor de governança: a saída bruta da coleta fica fora do repositório.

### Session 2026-11-17 (governança)

- [x] (governança) dispensada — o revisor fresco achou só o tema dado pessoal (literais do texto das consultas do banco do aluno, lidos pelo diagnóstico) e devolveu PADRAO_AUSENTE: o SDD Open não tem `sdd/GOVERNANCA_PADRAO.md`. Decisão do Roberto: o Open é um pacote de skills, não guarda dado pessoal nem contábil; o texto de consulta é mascarado e a saída bruta fica fora do repositório (segurança S10, S17, S18, aplicados no passo 12). Fronteira conferida: só o permitido mudou, nenhum arquivo gravado.

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && rm -rf $T/sdd/features $T/sdd/handoffs $T/sdd/reports $T/sdd/reviews $T/sdd/releases $T/sdd/contexto && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 a AT-006 no teste da varredura (repositórios git temporários com base e diff, migrations e código sintéticos, casos que acusam e que não acusam); AT-007, AT-008 e AT-011 no teste do diagnóstico (`supabase` falso no PATH que registra as chamadas, fixtures sintéticas de advisor e de `inspect db`, inclusive uma com senha numa string de conexão e uma com texto de consulta que traz quebra de linha e instrução ao agente, a lista de SQL de `references/`); AT-009 no teste do catálogo, no teste de textos da frente, em `tests/test_agnostico.py`, `tests/test_skill_lint.py` e `tests/test_gerar_starter.py`; AT-010 na suíte inteira (inclusive `tests/test_seguranca_varredura.py` e `tests/test_bash32.py`).

---

## Out of Scope

- Agendamento ou monitor contínuo (D8): só uma linha apontando o "Performance monitor" oficial como passo avançado.
- Corrigir legado em massa; a skill prioriza e propõe, não sai corrigindo.
- Escrever no banco de qualquer forma (criar índice, cancelar sessão, mudar configuração).
- Desempenho de front-end, de edge function (cold start) ou de Storage; teste de carga.
- Outros bancos além de Postgres/Supabase (MySQL, Mongo): N.A.
- Frase de desempenho no `AGENTS.md` (D11).
- Mudar a `sdd-seguranca` ou a `seguranca-varredura.sh` além de chamar o `--stack` dela.
- Tornar a varredura bloqueante; mudar o `verify-gate.sh`, a trava da governança ou o `publish-gate`.
- Editar o starter direto (ele recebe pelo gerador, F17) e mexer na F25 ou na F26.

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python 3.9 stdlib; script novo de `sdd/bin` lê `sdd/bin/lib/python.sh` com a guarda `sdd_python_pronto`; chamado sempre com `bash` | `tests/test_bash32.py`, `tests/test_python_resolver.py` |
| Technical | a varredura só lê e nunca usa rede; o diagnóstico só usa rede na coleta com consentimento, e nunca escreve no banco | AT-001 a AT-008 |
| Windows | teste que pergunta a plataforma usa as constantes de `tests/apoio.py`, nunca `os.name`; `subprocess` de teste com `encoding="utf-8"` (LM-014); a suíte passa no Git Bash com Python nativo | `tests/test_windows.py`, CI do PR |
| Agnóstico | texto novo sem nome de ferramenta de um agente só; cada ficha com "confira à mão" | `tests/test_agnostico.py` |
| Público | nada do repositório privado da RDD (número, nome de tabela, projeto); número com 11 ou mais dígitos barrado (LM-012); fixtures sintéticas | `publish-gate.sh` |
| Pacote | todo arquivo novo do pacote entra no `MANIFEST.txt` no mesmo commit (LM-037); skill da lista do starter roda `test_gerar_starter.py` antes do gate (LM-035) | `publish-gate.sh`, `tests/test_gerar_starter.py` |
| Skills | skill tocada sobe `metadata.version`; skill nova muda as contagens fixadas | `scripts/check-versions.py --base v2.21.0` |
| Fila | Release só depois de F25 e F26 publicadas, com rebase na `origin/main` e o gate de novo (D13) | release |
| Processo | `git add` por caminho; suíte com `-B`; sabotagem só em cópia de `git archive` (LM-009) | build |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `.agents/skills/sdd-desempenho-banco/` (nova), `.agents/skills/{sdd-define,sdd-design,sdd-release}/` (e o `web/` delas, se o Design achar o texto espelhado), `sdd/bin/desempenho-varredura.sh`, `sdd/bin/desempenho-diagnostico.sh`, `sdd/templates/DESIGN_TEMPLATE.md`, `scripts/starter/lista.txt`, `MANIFEST.txt`, `README.md`, `README.pt-BR.md`, `docs/` (novo guia e `cli-conventions.md`), `tests/` | produto do Open |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a pesquisa do brainstorm vira as `references/` da skill |
| **IaC Impact** | None | — |
| **LLM Prompts** | false | nenhum prompt de produção; "agente", "MCP" e o "Performance monitor" aparecem como ferramenta do aluno, não como código do pacote que chama modelo |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | dispensada — o SDD Open é um pacote de skills, não guarda dado pessoal nem contábil; o texto de consulta do banco do aluno é mascarado e fica fora do repositório (segurança S10, S17, S18) | Roberto Dias Duarte, 2026-11-17 |
| **Segurança** | 4 aplicados (S05, S10, S17, S18) · 0 recusados · 0 adiados | 2026-11-17 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | Os padrões por texto acham o caso comum sem falso positivo frequente (P02, P08, P09 são heurísticas) | o aluno aprende a ignorar o aviso; o Design pode passar a ficha para "só à mão" quando o par negativo não se sustenta | [ ] |
| A-002 | O Supabase CLI tem um comando de leitura para os advisors além do `inspect db` | a coleta fica só com o `inspect db`, e os advisors entram pelo MCP ou pelo painel (salvos num arquivo para o `--ler`); o Design confere no `--help` e na documentação | [x] `supabase db advisors` desde a 2.81.0 (DESIGN, Decision 10) |
| A-003 | O Supabase CLI aplica cada migration numa transação | `create index concurrently` falharia dentro dela; o Design confere antes de a ficha recomendar `concurrently` (ponto do brainstorm) | [x] sim; até a 2.108 falha, da 2.109 em diante roda à parte (DESIGN, Decision 10) |
| A-004 | A detecção de stack da segurança basta para a desempenho (supabase ou não) | uma 2ª detecção seria duplicação; o Design define o que é "projeto com banco" a partir dela e dos `.sql` | [x] DESIGN, Decisions 2 e 3 |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | lacuna medida (nenhuma das 22 skills fala de desempenho) e as falhas nomeadas |
| Users | 3 | 5 papéis, inclusive o sem banco e o da web |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | casos, sabotagens e cenários nomeados, com números |
| Scope | 2 | skill nova + 2 scripts + 3 skills de fase numa frente; a release depende da F25 e da F26 |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-17 | define-agent | Initial version |
| 1.5 | 2026-11-17 | build-agent | Contrato de aceite (5 propostas, todas aceitas): AT-004 (dispensa no fim de linha de código vale só para ela), AT-005 (ordem e "confira" uma vez), AT-008 (do mais grave), AT-010 (só a linha da skill no `AGENTS.md.tmpl`); AT-003 ganhou o teste da linha deslocada |
| 1.4 | 2026-11-17 | design-agent | Revisão do DESIGN, rodada D3, R2: AT-003 diz "achado que a base já tinha", como a Decision 5 |
| 1.3 | 2026-11-17 | design-agent | Revisão do DESIGN, rodada D2, R5: AT-004 diz o motivo mínimo (3 caracteres), como a Decision 1 |
| 1.2 | 2026-11-17 | design-agent | DESIGN, Decision 3: AT-006 olha `.sql` em qualquer pasta fora das do SDD e dos agentes (Postgres sem Supabase); A-002, A-003 e A-004 validadas (Decisions 2, 3 e 10) |
| 1.1 | 2026-11-17 | define-agent | Governança dispensada pelo Roberto (PADRAO_AUSENTE, motivo no Technical Context); segurança: S05, S10, S17, S18 aplicados em AT-011 |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F27_DESEMPENHO_BANCO.md` — UX review pulado: a feature não tem interface (texto de skill, scripts de terminal).
