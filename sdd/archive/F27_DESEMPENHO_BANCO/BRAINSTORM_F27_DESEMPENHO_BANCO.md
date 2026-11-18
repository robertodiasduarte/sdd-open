# BRAINSTORM: F27 Desempenho do banco (`sdd-desempenho-banco`)

> Sessão exploratória para fixar intenção e abordagem antes do Define. Fechada em 2026-11-17 com o Roberto;
> as decisões abaixo valem como default e o Define parte delas.

## Metadata

| Atributo | Valor |
|---|---|
| **Feature** | F27_DESEMPENHO_BANCO |
| **Skill nova** | `sdd-desempenho-banco` (nome decidido pelo Roberto em 2026-11-17) |
| **Data** | 2026-11-17 |
| **Autor** | brainstorm-agent (sessão aberta no repositório privado, que consome o SDD Open) |
| **Status** | Ready for Define |
| **Frente** | worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance` · branch `feat/f27-db-performance` (nasceu de `origin/main` em `2204a14`, `v2.21.0`) |
| **Fila** | publica **depois** da F25 (`feat/f25-skills-duplicadas`, em finalização) e da F26 (`feat/f26-docs-na-main`, na fila) |

---

## Ideia inicial

**Pedido do Roberto (17/11):** "Avalie o sdd-open. Seria possível criar uma skill para avaliação de performance do
banco de dados, no caso, Supabase? Ela entraria por acionamento do aluno, ou de forma automática?" Em seguida:
"pesquise sobre boas práticas de performance do Supabase", e a ordem de abrir a frente com o brainstorm fechado e
rodar o pipeline até a release.

**Contexto levantado:**
- O SDD Open não fala de desempenho de banco em nenhuma das 22 skills: nenhuma menção a índice, `EXPLAIN`, advisors,
  consulta lenta ou pooler.
- A segurança tem a cobertura completa e é o molde: a `sdd-seguranca` traz um catálogo de fichas
  (`references/CATALOGO_SEGURANCA.md`, 13 campos por ficha), uma varredura determinística (`sdd/bin/seguranca-varredura.sh`,
  só leitura e sem rede, com `--stack`, `--regras` e `--checklist`), um modo Define chamado pela `sdd-define`, uma lista
  fixa na 0c da `sdd-release`, a varredura no passo 10 da release e um modo incidente.
- A `rdd-audita-schema` (skill avulsa pública, fora do Open) confere **modelagem**: tipos, constraints, duplicidade e
  multiempresa. Não cobre desempenho, e não deve ser misturada com esta frente.
- O aluno típico do Open nunca usou terminal nem git. O banco dele, quando há, é quase sempre Supabase no plano
  Free ou Nano.

**Contexto técnico observado (para o Define):**

| Aspecto | Observação | Implicação |
|---|---|---|
| Onde mora | `.agents/skills/sdd-desempenho-banco/` (SKILL.md, manifest.json, references/, evals/) + `sdd/bin/desempenho-varredura.sh` | mesmo desenho da `sdd-seguranca`; reaproveitar a detecção de stack dela (`--stack` / slot `security.stack`) em vez de duplicar |
| Pontos de contato | `sdd-define` (passo de banco), `sdd-design` (seção de decisões), `sdd-release` (varredura como aviso), `MANIFEST.txt`, gerador do starter, guia do aluno, README | a F26 também mexe em `MANIFEST.txt` e na `sdd-release`: conflito esperado no rebase |
| Domínios de KB | nenhum em `sdd/kb/` | a pesquisa abaixo vira as `references/` da skill |
| Testes | `tests/test_*.py` (unittest, Python 3.9), suíte também no Windows (Git Bash + Python nativo) | fixtures sintéticas de migration e código, nunca dado real |

---

## Pesquisa (2026-11-17)

Fontes: o guia oficial `supabase-postgres-best-practices` (34 regras, mantido pela Supabase) e a documentação da
Supabase (links no fim). As medições de RLS são do repositório público RLS-Performance, citadas pela própria documentação.

### 1. RLS é o lugar onde o Supabase mais perde desempenho

| Prática | Medido pela Supabase |
|---|---|
| Índice na coluna usada pela política (ex.: `user_id`) | 171 ms → menos de 0,1 ms |
| Função dentro de `select`: `(select auth.uid()) = user_id`. Vira InitPlan, avaliada uma vez por consulta, não uma por linha | 179 ms → 9 ms; `is_admin()` com JOIN: 11 s → 7 ms |
| Função `security definer` (em schema não exposto) para checar papel | 178 s → 12 ms |
| Política sem JOIN com a tabela de origem: `team_id in (select team_id from team_user where user_id = (select auth.uid()))` | 9 s → 20 ms |
| `to authenticated` na política, para o `anon` nem avaliar | 170 ms → menos de 0,1 ms |
| Repetir o filtro no cliente (`.eq('user_id', id)`), mesmo que a política já filtre | 171 ms → 9 ms |

Ressalvas oficiais: o truque do `select` só vale quando o resultado da função não depende da linha; a função
`security definer` nunca fica num schema exposto pela API. Há um advisor para várias políticas permissivas do mesmo papel
e da mesma ação, porque todas são avaliadas em toda consulta.

### 2. Consultas e índices
- Índice nas colunas de `WHERE` e `JOIN`, e em toda chave estrangeira. O Postgres não cria esse índice sozinho.
- Tipo certo de índice:
  - parcial (`where deleted_at is null`);
  - composto, com a coluna de igualdade primeiro;
  - covering (`include`);
  - GIN para JSONB e busca textual (`tsvector`);
  - HNSW para pgvector.
- `create index` comum trava a gravação na tabela; o `concurrently` não trava, mas não roda dentro de transação.
  [O Design confere como as migrations do Supabase CLI rodam antes de recomendar.]
- Paginação por cursor (`where (created_at, id) > (…)`), não por `offset`: o offset lê e descarta as linhas puladas.
- Sem N+1: buscar em lote com `in (…)` ou pelo embed do PostgREST, nunca uma consulta por item num laço.
- Contagem exata (`count: 'exact'`) em tabela grande custa caro; `planned` ou `estimated` bastam para paginação.
- O `index_advisor` (extensão) sugere `CREATE INDEX` para uma consulta, mas só índice B-tree de uma coluna.

### 3. Conexões
- Serverless ou edge usa o Supavisor em modo transaction (porta 6543). Servidor persistente pode usar o pool da
  própria biblioteca. O PgBouncer dedicado (planos pagos) fica na máquina do banco, com menos latência.
- O modo transaction não aceita prepared statement nomeado: é preciso desligar no driver (`prepare: false` no postgres.js).
- Conexões diretas + Supavisor + PgBouncer ficam abaixo do `max_connections` do tamanho de máquina, com folga, porque
  Auth, Storage e PostgREST tiram conexões do mesmo total.
- O Auth tem teto próprio de conexões. Em valor absoluto, aumentar a máquina não acelera o Auth; há advisor para isso
  (`auth_db_connections_absolute`).

### 4. Transações, travas e tempo limite
- Transação curta, sem chamada HTTP dentro; fila com `for update skip locked`.
- Tempo limite padrão por papel: `anon` 3 s, `authenticated` 8 s, `postgres` 2 min (o cliente tem teto configurável
  de 60 s). Ajuste por função com `set statement_timeout` na definição. Aumentar o tempo do papel esconde a consulta lenta.

### 5. Schema e manutenção
- Toda tabela com chave primária (`bigint identity` ou UUIDv7; UUIDv4 aleatório fragmenta o índice).
- Constraint em tabela grande: `NOT VALID`, depois `VALIDATE`.
- Autovacuum e `ANALYZE` em dia; bloat (espaço de linhas mortas) vigiado.

### 6. Ferramentas oficiais de diagnóstico (todas de leitura)

| Ferramenta | O que dá |
|---|---|
| Performance Advisor: painel, MCP `get_advisors`, CLI `supabase db advisors`, Management API | checagens determinísticas sobre o schema vivo (lints do projeto `splinter`): `unindexed_foreign_keys`, `auth_rls_initplan`, `no_primary_key`, `unused_index`, `multiple_permissive_policies`, `duplicate_index`, `auth_db_connections_absolute` |
| `supabase inspect db …` | `outliers`, `seq-scans`, `unused-indexes`, `index-usage`, `cache-hit`, `bloat`, `vacuum-stats`, `blocking`, `locks`, `long-running-queries`, `role-connections`, `table-sizes` |
| Query Performance (painel) + `pg_stat_statements` | consultas mais chamadas, mais lentas e de maior tempo total; guarda só as últimas 5.000 |
| `.explain()` do supabase-js | plano pela API. Exige `pgrst.db_plan_enabled`, que a documentação proíbe em produção |
| "Performance monitor" (documentação, seção *Hire an agent*) | prompt pronto de agente que roda a cada hora pelo MCP com `read_only=true`. Não cria índice nem cancela sessão; só reporta, com plano de verificação |

A documentação diz que um achado do advisor não é a correção: é preciso confirmá-lo com log antes de agir. Para o
monitor, o conselho é rodar a pedido primeiro e só depois agendar. A Supabase também deixa explícito que índices,
filtros, conexões e o tamanho da máquina são responsabilidade do cliente (*Shared Responsibility Model*).

### 7. O que um projeto real mostrou (medido no repositório privado; sem números aqui)
O advisor rodado num projeto Supabase de produção com anos de migrations trouxe volume alto de quatro checagens:
`auth_rls_initplan`, `unindexed_foreign_keys`, `unused_index` e `multiple_permissive_policies`. Disso saem três lições
para a skill:
- **`initplan` e chave estrangeira sem índice nascem na migration.** Dá para pegar lendo o SQL, sem banco, antes de
  publicar.
- **"Índice não usado" é falso alarme em potencial.** O contador zera a cada reinício ou reset de estatísticas; sem
  saber há quanto tempo as estatísticas acumulam, a recomendação de apagar é perigosa.
- **Legado é outra conversa.** A skill trata o que a migration nova introduz e, no diagnóstico, prioriza; não manda
  corrigir centenas de itens de uma vez.

Lições do mesmo projeto privado que viram fichas genéricas (sem nome de tabela nem número):
- **Função SQL chamada no `WHERE` ou na política.** Quando a função tem `FROM`, `SECURITY DEFINER` ou `SET`, o planner
  não a incorpora à consulta e ela roda uma vez por linha. A prova é o `EXPLAIN (VERBOSE)`: o nome da função não pode
  aparecer em `Filter:`.
- **Carga pesada contra produção.** Avaliação em lote, teste de carga ou backfill em horário de uso, num plano pequeno,
  levaram o banco ao swap. O sintoma foi congelamento sem erro nenhum no Postgres.
- **O PostgREST devolve no máximo `max_rows` linhas.** Lista que passa do teto é cortada em silêncio.

---

## Perguntas e respostas

| # | Pergunta | Resposta | Impacto |
|---|---|---|---|
| 1 | Dá para ter uma skill de desempenho de banco no Open? | Sim; o molde é a `sdd-seguranca` | skill nova + catálogo + varredura, mesmo formato |
| 2 | Ela entra por acionamento do aluno ou de forma automática? | **Os dois, em camadas.** Automática onde só lê o repositório (Define, Design, Release); a pedido quando olha o banco no ar (diagnóstico, checkup) | dois mundos de verificação: estático (sem rede) e ao vivo (com consentimento) |
| 3 | O automático bloqueia a publicação, como a segurança? | **Não.** Só avisa (CONCERNS) | desempenho degrada, não vaza; bloquear iniciante por chave sem índice em tabela de 50 linhas é atrito |
| 4 | O ao vivo pode rodar sozinho, agendado? | **Não na v1.** A pedido, com consentimento por execução; o agendamento fica como dica avançada, apontando para o monitor oficial | sem credencial guardada e sem leitura de produção sem ninguém pedir |
| 5 | Nome? | `sdd-desempenho-banco` (Roberto, 17/11) | padrão em português das skills do aluno |
| 6 | Stack? | Supabase primeiro; fichas genéricas de Postgres valem para Postgres puro; sem banco ⇒ N.A. em 1 linha | reaproveita a detecção de stack da segurança |

---

## Perfil de risco

| Pergunta | Resposta |
|---|---|
| Quem pode ver? | O relatório do diagnóstico ao vivo pode trazer texto de consulta (`pg_stat_statements`) e nomes de tabela do aluno; fica só com ele, na máquina dele. O texto de consulta pode carregar dado pessoal: a skill agrega e mascara literais antes de mostrar |
| Quem pode mudar? | Ninguém, pela skill. Ela **nunca escreve** no banco: não cria índice, não cancela sessão, não altera configuração. A correção sai como migration proposta, que segue o caminho normal do SDD |
| Quanto alguém pode pedir? | O ao vivo faz poucas consultas de catálogo e de estatística, sem varrer tabela de dado. Nunca roda `EXPLAIN ANALYZE` de escrita fora de `BEGIN … ROLLBACK`, e nunca roda teste de carga |

---

## Amostras

| Tipo | Onde | Quantas | Notas |
|---|---|---|---|
| Migrations sintéticas, cada uma com um padrão (positivo e negativo) | `tests/fixtures/` (o Design fixa a pasta) | 1 par por ficha estática | nenhum SQL copiado de projeto real |
| Código cliente sintético (supabase-js) | idem | 1 par por ficha de código | `.select()` sem limite, `count: 'exact'`, laço com `await` |
| Saída de advisor e de `inspect db` | fixture JSON/texto sintético | 2 a 3 | para o modo diagnóstico interpretar sem rede nos testes |
| Código relacionado | `sdd/bin/seguranca-varredura.sh`, `.agents/skills/sdd-seguranca/` | — | padrão de catálogo, dispensa por comentário e códigos de saída |

---

## Abordagens exploradas

### Abordagem A: skill nova no molde da `sdd-seguranca` ⭐ Recomendada

Catálogo próprio de fichas Pnn, uma varredura estática própria e quatro modos: Define, Design, varredura de release e
diagnóstico a pedido.

**Prós:**
- Mesmo formato que o aluno e o agente já conhecem: ficha, varredura, dispensa por comentário, `confira` à mão.
- Desempenho fica fora do caminho que bloqueia: aviso, não NON_WAIVABLE.
- Reaproveita a detecção de stack e o padrão de testes.

**Contras:**
- Mais uma skill no pacote, e mais um passo no Define e na Release, com o custo de contexto que a F23 tenta conter.
  Mitigação: N.A. em 1 linha sem gatilho, e a varredura só imprime quando acha algo.

### Abordagem B: capítulo de desempenho dentro da `sdd-seguranca`

**Prós:** nenhuma skill nova; um passo só no Define e na Release.

**Contras:** mistura o que bloqueia com o que só avisa; a skill e o catálogo de segurança, já grandes, ficam maiores;
e quem quer só o diagnóstico de lentidão entra pela porta da segurança. Rejeitada.

### Abordagem C: estender a `rdd-audita-schema`

**Prós:** ela já tem modo feature, modo projeto e consulta de catálogo só de leitura.

**Contras:** é skill avulsa, fora do Open e do starter, e com outro público (curso de modelagem). Não chega ao aluno
do SDD. Rejeitada; pode virar irmã depois, com link.

---

## Decisões (recomendação aceita como default)

| # | Decisão | Default | Por quê |
|---|---|---|---|
| D1 | Onde | Abordagem A: skill nova no Open, que chega ao starter pelo gerador (F17) | a regra do programa: ajuste de skill do aluno nasce no Open |
| D2 | Nome | `sdd-desempenho-banco` | decidido pelo Roberto |
| D3 | Acionamento | automático no Define, no Design e na Release (só leitura do repositório); a pedido no diagnóstico e no checkup ao vivo | resposta à pergunta 2 |
| D4 | Bloqueio | a varredura nunca bloqueia: exit `0` nada · `1` avisos (CONCERNS) · `64` uso inválido; nenhuma ficha com `bloqueia: sim` | resposta à pergunta 3 |
| D5 | Ao vivo | só com consentimento por execução; MCP do Supabase em modo leitura (`get_advisors`, `execute_sql` de leitura) ou CLI (`supabase db advisors`, `supabase inspect db`), conforme o que o agente tiver; sem nenhum dos dois, o roteiro à mão no painel (Advisors, Query Performance) | a skill funciona até sem terminal, como a segurança |
| D6 | Nunca escreve | não cria índice, não cancela sessão, não altera configuração; a correção sai como migration proposta para o fluxo SDD | o aluno não perde o controle do banco |
| D7 | Interpretação | regras escritas na skill: índice "não usado" só com a idade das estatísticas conhecida; achado confirmado em log ou `EXPLAIN` antes de virar correção; perguntar o tamanho da máquina antes de culpar a consulta | evita os falsos alarmes vistos no projeto real |
| D8 | Agendamento | fora da v1; uma linha apontando para o "Performance monitor" oficial, como passo avançado | YAGNI; credencial e leitura de produção sem pedido |
| D9 | Define | o gatilho `banco` que já existe dispara; no máximo 1 pergunta ("quantas linhas essa tabela terá em um ano?"); propõe ATs só das fichas com gatilho; senão, N.A. em 1 linha | conter o custo de pergunta e contexto (F23) |
| D10 | Design | a `sdd-design` traz as decisões de desempenho das fichas da fase `design`: índice por chave estrangeira e por coluna de política, `(select auth.uid())`, `to <papel>`, paginação | é onde o custo é menor |
| D11 | `AGENTS.md` | **não** entra frase de desempenho no `AGENTS.md` na v1 | o arquivo é lido em toda sessão; o Design já cobre. Reavaliar com dado |
| D12 | Documentos da frente | os documentos da F27 ficam na branch da frente (`sdd/features/`, `sdd/handoffs/`…), o estado-alvo da F26; só a linha da F27 na tabela "Estado das frentes" vai para a branch de documentos | evita migrar duas vezes; se a F26 publicar com outra regra, a F27 se adapta no rebase |
| D13 | Ordem | Define, Design e Build podem correr já; a Release só depois de F25 e F26 publicadas, com rebase na `origin/main` e o gate de novo | as duas mexem no `MANIFEST.txt` e a F26 na `sdd-release` e no empacotamento |

---

## Rascunho do catálogo (o Define fecha a lista; o Design fecha o `padrao` de cada uma)

Mesmos campos da segurança, sem `bloqueia` (sempre aviso) e sem `agents` (D11). Os campos são `stack`, `fase`,
`gravidade`, `gatilho`, `padrao`, `arquivos`, `frase`, `evitar`, `at`, `confira` e `ref`. Na coluna "Estático?",
"sim" quer dizer que a varredura sem rede pega.

| Id | Falha | Stack | Estático? | Advisor equivalente |
|---|---|---|---|---|
| P01 | Política RLS chama `auth.uid()`, `auth.jwt()` ou `current_setting()` fora de `(select …)` | supabase | sim | `auth_rls_initplan` |
| P02 | Coluna comparada na política sem índice | supabase | sim (heurística) | — |
| P03 | Chave estrangeira sem índice | todas (Postgres) | sim | `unindexed_foreign_keys` |
| P04 | Tabela sem chave primária | todas (Postgres) | sim | `no_primary_key` |
| P05 | Duas ou mais políticas permissivas para o mesmo papel e a mesma ação | supabase | sim | `multiple_permissive_policies` |
| P06 | Política sem `to <papel>` | supabase | sim | — |
| P07 | Índice duplicado | todas (Postgres) | sim | `duplicate_index` |
| P08 | Lista sem limite nem paginação (`.select()` sem `.range()`/`.limit()`; `offset` profundo) | supabase | sim (heurística) | — |
| P09 | Consulta que confia só na RLS, sem filtro no cliente | supabase | sim (heurística) | — |
| P10 | `count: 'exact'` em lista | supabase | sim | — |
| P11 | N+1: consulta dentro de laço | todas | só à mão (ou heurística fraca) | — |
| P12 | Função SQL no `WHERE` ou na política que roda por linha (não incorporada) | todas (Postgres) | só à mão (`EXPLAIN (VERBOSE)`) | — |
| P13 | Chamada HTTP ou trabalho lento dentro de transação, trigger ou função | todas (Postgres) | sim (heurística: `http_`, `net.http_` em trigger) | — |
| P14 | Serverless ou edge conectando direto (5432) ou com prepared statement no modo transaction | supabase | sim (heurística) | — |
| P15 | Busca `ilike '%…%'` sem trigram; JSONB sem GIN; coluna `vector` sem índice HNSW | todas (Postgres) | sim (heurística) | — |
| P16 | Tempo limite aumentado no papel `anon`/`authenticated` para esconder consulta lenta | supabase | sim | — |
| P17 | Carga pesada contra produção (teste de carga, avaliação em lote, backfill) sem janela combinada | todas | só à mão (fase release/bancada) | — |

Regras do modo diagnóstico (não são fichas): idade das estatísticas antes de "índice não usado"; tamanho da máquina e
swap antes de culpar consulta; "achado não é correção"; nunca `EXPLAIN ANALYZE` de escrita fora de `BEGIN … ROLLBACK`;
`.explain()` do supabase-js só fora de produção.

---

## Fora do escopo (YAGNI)

- Agendamento ou monitor contínuo (D8).
- Corrigir legado em massa; a skill prioriza e propõe, não sai corrigindo.
- Desempenho de front-end, de edge function (cold start) ou de Storage.
- Teste de carga.
- Outros bancos além de Postgres/Supabase (MySQL, Mongo): N.A.
- Mudar a `sdd-seguranca` além do mínimo para reaproveitar a detecção de stack.

---

## Rascunho de critérios de aceite (o Define escreve em EARS com o lado negativo)

1. Uma migration com uma política `using (auth.uid() = user_id)` faz a varredura sair `1` com `P01 arquivo:linha`; a
   mesma política com `(select auth.uid())` sai `0`.
2. `references x(id)` sem índice na coluna gera P03; com `create index … (x_id)` na mesma migration ou numa anterior,
   não gera.
3. A varredura nunca sai `2`; o comentário `sdd-desempenho-banco: aceito Pnn — <motivo>` dispensa o achado, e sem
   motivo não vale.
4. Projeto sem banco: a skill responde N.A. em 1 linha no Define e a varredura sai `0` sem imprimir nada.
5. A `sdd-release` roda a varredura e mostra os avisos no bloco do OK sem abortar.
6. No modo diagnóstico, sem consentimento a skill não se conecta a nada; com consentimento, ela só emite consultas de
   leitura (teste com MCP ou CLI falso que registra os comandos).
7. Diante de "índice não usado" com estatísticas de idade desconhecida ou curta, o relatório não recomenda apagar.
8. Os testes passam no macOS, no Linux e no Windows (Git Bash + Python nativo); o pacote montado contém a skill e o
   script (`MANIFEST.txt`) e nenhum documento da frente.

---

## Riscos

| Risco | Mitigação |
|---|---|
| Heurística de regex com falso positivo (P02, P08, P09) irrita e o aluno passa a ignorar | gravidade baixa; dispensa por comentário; testes com casos negativos; na dúvida, ficha "só à mão" |
| Conflito com a F26 (`MANIFEST.txt`, `sdd-release`, empacotamento) | D13: a release espera a F26; rebase e gate de novo |
| Custo de contexto (mais um passo em Define e Release) | N.A. em 1 linha; varredura silenciosa sem achado; D11 |
| Diagnóstico ao vivo expor dado pessoal em texto de consulta | agregar e mascarar literais; nada sai da máquina do aluno |
| Recomendação que piora: apagar índice "não usado", `concurrently` em migration transacional | D7 e a nota do `concurrently` para o Design conferir |

---

## Fontes

- Row Level Security, recomendações de desempenho: https://supabase.com/docs/guides/database/postgres/row-level-security#rls-performance-recommendations
- Row Level Security performance: https://supabase.com/docs/guides/database/postgres/row-level-security-performance
- Advisors: https://supabase.com/docs/guides/observability/advisors · lints (splinter): https://supabase.github.io/splinter/
- Inspect the database: https://supabase.com/docs/guides/observability/inspect
- index_advisor: https://supabase.com/docs/guides/database/extensions/index_advisor · índices: https://supabase.com/docs/guides/database/postgres/indexes
- Connection pooling and limits: https://supabase.com/docs/guides/database/connecting-to-postgres/pooling-and-limits
- Timeouts: https://supabase.com/docs/guides/database/postgres/timeouts
- Performance monitor (agente): https://supabase.com/docs/guides/observability/automate-with-agents/performance
- Shared Responsibility Model: https://supabase.com/docs/guides/deployment/shared-responsibility-model
- Guia `supabase-postgres-best-practices` (Supabase, 34 regras): https://github.com/supabase/agent-skills

## Próximo passo

`sdd-define` na janela da frente, pelo prompt `sdd/handoffs/SESSION_PROMPT_F27_DESEMPENHO_BANCO.md`.
