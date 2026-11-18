# Catálogo de desempenho do banco

> Fonte única das falhas que mais deixam lento um app com Supabase ou Postgres. Uma ficha serve a todas as fases:
> a **frase** previne (o agente a segue ao construir), o **at** vira teste de aceitação no Define, o **evitar** vira
> decisão no Design, o **padrao** alimenta a varredura da publicação e o **confira** é a prova à mão para quem não
> roda script. Quem lê este arquivo por máquina é só `sdd/bin/desempenho-varredura.sh`. Nada aqui bloqueia a
> publicação: desempenho degrada, não vaza.

## Como ler uma ficha

Cada item é um título `### Pnn — <falha>` seguido de exatamente 11 linhas, nesta ordem:

| Campo | O que diz | Valores |
|---|---|---|
| `stack` | onde a falha existe; o item só vale com essa stack no projeto | `todas` (qualquer Postgres) · `supabase` |
| `fase` | a fase em que evitar custa menos | `define` · `design` · `build` · `release` |
| `gravidade` | ordem dos avisos | `alta` · `media` · `baixa` |
| `gatilho` | o que no Define faz a ficha valer | `banco` · `lista` · `busca` · `conexao` · `lote` (separados por vírgula) |
| `padrao` | o que a varredura procura | `re:` + expressão entre crases · `regra:<nome>` · `só à mão` |
| `arquivos` | onde o padrão é procurado | globs separados por vírgula |
| `frase` | a regra que o agente segue ao construir | 1 frase |
| `evitar` | a decisão de design que fecha a falha | 1 a 2 frases |
| `at` | o teste de aceitação modelo, em EARS, com o lado negativo | 1 frase |
| `confira` | como conferir à mão, sem script | passos curtos |
| `ref` | referência pública | documentação da Supabase ou do PostgreSQL |

Dispensa de um achado da varredura: um comentário `sdd-desempenho-banco: aceito Pnn — <motivo>` na linha dele, ou
numa linha só de comentário logo acima. No fim de uma linha de código, vale só para aquela linha. Sem motivo, não vale.

## Itens

### P01 — Política que chama auth.uid() uma vez por linha
- stack: supabase
- fase: design
- gravidade: alta
- gatilho: banco
- padrao: regra:initplan
- arquivos: *.sql
- frase: Em toda política, chame `auth.uid()`, `auth.jwt()`, `auth.role()` e `current_setting()` dentro de `(select …)`, para o banco calcular o valor uma vez por consulta e não uma vez por linha.
- evitar: Escreva a condição como `(select auth.uid()) = <coluna do dono>` e crie o índice dessa coluna na mesma migration.
- at: When uma pessoa logada lista as próprias linhas de uma tabela grande, the system shall usar a política com `(select auth.uid())`; if a política chama `auth.uid()` sem o `select`, then a varredura shall avisar P01 com o arquivo e a linha.
- confira: No painel do banco, abra Advisors › Performance e procure "Auth RLS Initialization Plan"; ou leia cada política e confira se toda chamada a `auth.` ou a `current_setting(` está dentro de `(select …)`.
- ref: https://supabase.com/docs/guides/database/postgres/row-level-security#call-functions-with-select

### P02 — Coluna usada na política sem índice
- stack: supabase
- fase: design
- gravidade: media
- gatilho: banco
- padrao: regra:politica-sem-indice
- arquivos: *.sql
- frase: Toda coluna que a política compara com o usuário logado (dono da linha, empresa, equipe) tem índice, criado na mesma migration da política.
- evitar: Para cada política, crie `create index on <tabela> (<coluna do dono>)`; em tabela que já tem muitas linhas em produção, use `create index concurrently` numa migration só para ele, com o CLI atualizado.
- at: When uma pessoa logada lista as próprias linhas, the system shall achar as linhas pelo índice da coluna do dono; if a coluna da política não tem índice, then a varredura shall avisar P02.
- confira: Para cada política, anote a coluna comparada com o usuário; no painel, em Database › Indexes, confira que essa coluna tem um índice em que ela é a primeira.
- ref: https://supabase.com/docs/guides/database/postgres/row-level-security#add-indexes

### P03 — Chave estrangeira sem índice
- stack: todas
- fase: design
- gravidade: media
- gatilho: banco
- padrao: regra:fk-sem-indice
- arquivos: *.sql
- frase: Toda coluna que aponta para outra tabela (chave estrangeira) ganha um índice na mesma migration; o Postgres não cria esse índice sozinho.
- evitar: Logo depois de cada `references`, crie `create index on <tabela> (<coluna da chave>)`; em tabela que já tem muitas linhas em produção, `create index concurrently` numa migration só para ele, com o CLI atualizado, e confira depois que o índice ficou válido.
- at: When o app apaga ou busca pelo registro "pai", the system shall achar os registros "filhos" pelo índice da chave; if a chave estrangeira não tem índice, then a varredura shall avisar P03 com o arquivo e a linha.
- confira: No painel, abra Advisors › Performance (mostre também os de nível INFO) e procure "Unindexed foreign keys"; ou, para cada `references` das migrations, procure um `create index` cuja primeira coluna é a da chave.
- ref: https://supabase.com/docs/guides/database/database-advisors?lint=0001_unindexed_foreign_keys

### P04 — Tabela sem chave primária
- stack: todas
- fase: design
- gravidade: media
- gatilho: banco
- padrao: regra:sem-pk
- arquivos: *.sql
- frase: Toda tabela nasce com chave primária (`bigint generated always as identity` ou UUID ordenado no tempo); sem ela, atualizar, apagar e replicar ficam lentos.
- evitar: Ponha `id bigint generated always as identity primary key` (ou `uuid` gerado em ordem de tempo) em toda tabela nova; evite UUID aleatório como chave de tabela que cresce muito.
- at: When uma migration cria uma tabela, the system shall declarar a chave primária nela; if a tabela nasce sem chave primária, then a varredura shall avisar P04.
- confira: No painel, abra Advisors › Performance (com o nível INFO) e procure "No primary key"; ou leia cada `create table` e confira o `primary key`.
- ref: https://supabase.com/docs/guides/database/database-advisors?lint=0004_no_primary_key

### P05 — Duas políticas que liberam a mesma coisa
- stack: supabase
- fase: design
- gravidade: media
- gatilho: banco
- padrao: regra:permissivas
- arquivos: *.sql
- frase: Para cada tabela, cada papel e cada ação (ler, gravar, alterar, apagar) tem uma política permissiva só; condições diferentes se juntam com `or` na mesma política.
- evitar: Junte as políticas permissivas do mesmo papel e da mesma ação numa só, com as condições ligadas por `or`, e troque `for all` por políticas por ação quando ele se cruzar com outra.
- at: When uma pessoa lê uma tabela, the system shall avaliar uma política permissiva só por papel e por ação; if duas políticas permissivas cobrem o mesmo papel e a mesma ação, then a varredura shall avisar P05.
- confira: No painel, abra Advisors › Performance e procure "Multiple permissive policies"; ou liste as políticas de cada tabela e confira se duas sem `as restrictive` cobrem o mesmo papel e a mesma ação.
- ref: https://supabase.com/docs/guides/database/database-advisors?lint=0006_multiple_permissive_policies

### P06 — Política sem dizer para qual papel vale
- stack: supabase
- fase: design
- gravidade: baixa
- gatilho: banco
- padrao: regra:sem-papel
- arquivos: *.sql
- frase: Toda política diz para qual papel vale (`to authenticated`, `to anon`), para o banco nem avaliá-la nos outros papéis.
- evitar: Escreva `to authenticated` em toda política de usuário logado e `to anon` só onde o visitante sem login precisa ler.
- at: When um visitante sem login consulta a tabela, the system shall pular as políticas de usuário logado; if uma política não tem a cláusula `to`, then a varredura shall avisar P06.
- confira: Leia cada `create policy` das migrations e confira se tem `to <papel>` logo depois da ação.
- ref: https://supabase.com/docs/guides/database/postgres/row-level-security#specify-roles-in-your-policies

### P07 — Índice repetido
- stack: todas
- fase: build
- gravidade: baixa
- gatilho: banco
- padrao: regra:indice-duplicado
- arquivos: *.sql
- frase: Antes de criar um índice, confira se a tabela já tem um com as mesmas colunas; índice repetido só deixa toda gravação mais lenta.
- evitar: Mantenha um índice só por lista de colunas e apague o repetido numa migration.
- at: When uma migration cria um índice, the system shall criar só índice com colunas que a tabela ainda não indexa; if dois índices da tabela têm as mesmas colunas, then a varredura shall avisar P07.
- confira: No painel, abra Advisors › Performance e procure "Duplicate index"; ou compare os `create index` de cada tabela.
- ref: https://supabase.com/docs/guides/database/database-advisors?lint=0009_duplicate_index

### P08 — Lista sem limite
- stack: supabase
- fase: define
- gravidade: media
- gatilho: lista
- padrao: regra:lista-sem-limite
- arquivos: *.js, *.jsx, *.ts, *.tsx, *.mjs, *.cjs, *.vue, *.svelte, *.astro
- frase: Toda tela que lista registros pede uma página de cada vez (`.range()` ou `.limit()`), ordenada por uma coluna com índice; nunca a tabela inteira.
- evitar: Defina o tamanho da página e pagine pela última linha vista (`where (created_at, id) < (…)`), não por `offset` alto; lembre que a API devolve no máximo o teto de linhas do projeto e corta o resto em silêncio.
- at: When a tela de listagem carrega, the system shall pedir no máximo uma página de registros; if a consulta da lista não tem limite nem paginação, then a varredura shall avisar P08.
- confira: Abra a tela, as ferramentas do navegador e a aba de rede; na chamada da listagem, a URL deve trazer `limit` ou o cabeçalho `Range`; com milhares de registros, a resposta deve trazer só uma página.
- ref: https://supabase.com/docs/reference/javascript/range

### P09 — Consulta que confia só na política para filtrar
- stack: supabase
- fase: build
- gravidade: baixa
- gatilho: lista
- padrao: só à mão
- arquivos: *.js, *.jsx, *.ts, *.tsx, *.mjs, *.cjs, *.vue, *.svelte, *.astro
- frase: Quando a tela mostra só os registros do usuário, a consulta repete o filtro (`.eq('user_id', id)`) mesmo que a política já filtre: o banco usa o índice em vez de testar a política linha por linha.
- evitar: Em toda consulta de "meus registros", acrescente o filtro do dono com a mesma coluna da política.
- at: When a tela de "meus registros" carrega, the system shall filtrar pela coluna do dono na própria consulta, além da política.
- confira: Para cada tela de "meus registros", leia a consulta: ela deve trazer o filtro do dono (`.eq(…)`) com a coluna da política.
- ref: https://supabase.com/docs/guides/database/postgres/row-level-security#add-filters-to-every-query

### P10 — Contagem exata em lista
- stack: supabase
- fase: build
- gravidade: baixa
- gatilho: lista
- padrao: re:`count:\s*['"]exact['"]`
- arquivos: *.js, *.jsx, *.ts, *.tsx, *.mjs, *.cjs, *.vue, *.svelte, *.astro
- frase: Em lista paginada, peça a contagem estimada (`count: 'planned'` ou `'estimated'`); a exata percorre a tabela inteira a cada página.
- evitar: Use `count: 'estimated'` para mostrar o total da paginação e deixe a contagem exata para relatório que precisa dela.
- at: When a lista paginada mostra o total de registros, the system shall pedir a contagem estimada; if a consulta pede `count: 'exact'`, then a varredura shall avisar P10.
- confira: Procure `count:` no código das listas; `'exact'` em lista que cresce é o aviso.
- ref: https://supabase.com/docs/reference/javascript/select

### P11 — Uma consulta por item dentro de um laço
- stack: todas
- fase: build
- gravidade: media
- gatilho: lista
- padrao: só à mão
- arquivos: *.js, *.jsx, *.ts, *.tsx, *.mjs, *.cjs, *.vue, *.svelte, *.astro, *.sql
- frase: Nunca faça uma consulta por item dentro de um laço; busque todos de uma vez com `in (…)` ou trazendo a tabela relacionada na mesma consulta.
- evitar: Troque o laço com `await` por uma consulta só, com `.in('id', ids)` ou com a tabela relacionada no `select`.
- at: When a tela mostra uma lista com dados de outra tabela, the system shall fazer um número fixo de consultas, que não cresce com o tamanho da lista.
- confira: Abra a tela com a aba de rede aberta: se o número de chamadas cresce com o número de itens da lista, há consulta dentro de laço.
- ref: https://supabase.com/docs/guides/database/joins-and-nesting

### P12 — Função que roda uma vez por linha
- stack: todas
- fase: design
- gravidade: media
- gatilho: banco
- padrao: só à mão
- arquivos: *.sql
- frase: Função chamada no `where` ou numa política é simples o bastante para o banco incorporá-la à consulta (`language sql`, sem `security definer`, sem `set`); se não puder ser, o resultado dela entra por `(select …)`.
- evitar: Para conferir papel ou empresa do usuário, use uma função `security definer` num esquema que a API não expõe, chamada dentro de `(select …)`; prove com o plano da consulta.
- at: When a consulta filtra por uma função, the system shall avaliá-la uma vez por consulta; if o plano mostra a função no filtro de cada linha, then a correção shall entrar antes de publicar.
- confira: Rode `explain (verbose) <a consulta>` num banco de teste: o nome da função não pode aparecer na linha `Filter:` de uma varredura de tabela.
- ref: https://supabase.com/docs/guides/database/postgres/row-level-security#use-security-definer-functions

### P13 — Chamada HTTP que segura o banco
- stack: todas
- fase: design
- gravidade: alta
- gatilho: banco
- padrao: re:`(?i)(?<![\w.])(?:extensions\.)?http(?:_get|_post|_put|_patch|_delete|_head)?\s*\(`
- arquivos: *.sql
- frase: Nenhuma função, gatilho ou transação espera uma chamada HTTP; o que precisa avisar outro sistema usa fila ou o `pg_net` (assíncrono).
- evitar: Troque a extensão `http` (síncrona) por `net.http_post` do `pg_net` ou por uma fila processada fora da transação.
- at: When um registro é gravado e outro sistema precisa saber, the system shall gravar sem esperar a resposta desse sistema; if uma função do banco chama a extensão `http`, then a varredura shall avisar P13.
- confira: Procure `http_get(`, `http_post(` e `http(` nas migrations; `net.http_post(` não é o problema.
- ref: https://supabase.com/docs/guides/database/extensions/pg_net

### P14 — Função na nuvem conectando do jeito errado
- stack: supabase
- fase: design
- gravidade: alta
- gatilho: conexao
- padrao: só à mão
- arquivos: *.js, *.ts, *.mjs, *.cjs, *.env.example, *.toml
- frase: Função serverless ou edge que fala com o banco direto usa o pooler em modo transaction (porta 6543) com prepared statement desligado (`prepare: false`); servidor que fica ligado pode usar o pool da própria biblioteca.
- evitar: Na variável de ambiente da função, use a string do pooler em modo transaction e desligue o prepared statement no driver; some as conexões de tudo e deixe folga abaixo do máximo do tamanho da máquina.
- at: When muitas funções rodam ao mesmo tempo, the system shall conectar pelo pooler em modo transaction; if uma função abre conexão direta na porta 5432, then a correção shall entrar antes de publicar.
- confira: No painel, abra Connect e compare com a variável da função: serverless e edge usam a porta 6543 (transaction); no código, o driver tem `prepare: false`.
- ref: https://supabase.com/docs/guides/database/connecting-to-postgres

### P15 — Busca sem o índice certo
- stack: todas
- fase: define
- gravidade: media
- gatilho: busca
- padrao: regra:busca
- arquivos: *.sql, *.js, *.jsx, *.ts, *.tsx, *.mjs, *.cjs, *.vue, *.svelte, *.astro
- frase: Busca por pedaço de texto usa índice de trigramas (`gin_trgm_ops`), busca em JSON usa índice GIN e coluna de vetor usa índice HNSW; sem eles, toda busca lê a tabela inteira.
- evitar: Para cada busca da feature, decida o tipo de índice na mesma migration da coluna: `pg_trgm` com GIN para `ilike '%…%'`, GIN para JSONB, `using hnsw` para `vector`.
- at: When a pessoa busca por um trecho de texto numa tabela grande, the system shall usar o índice da busca; if a busca não tem índice do tipo certo, then a varredura shall avisar P15.
- confira: Para cada busca, ache a coluna e procure, nas migrations, um índice `using gin (… gin_trgm_ops)`, `using gin` (JSONB) ou `using hnsw` (vetor) nela.
- ref: https://supabase.com/docs/guides/database/postgres/indexes

### P16 — Tempo limite aumentado para esconder consulta lenta
- stack: supabase
- fase: build
- gravidade: media
- gatilho: banco
- padrao: re:`(?i)\balter\s+role\s+"?(?:anon|authenticated|authenticator)"?\s+set\s+statement_timeout\b`
- arquivos: *.sql
- frase: Não aumente o tempo limite dos papéis do app (`anon` 3 s, `authenticated` 8 s): consulta que estoura o limite pede índice ou paginação; se uma função precisa de mais tempo, o limite vai só nela.
- evitar: Ache a consulta lenta e corrija com índice ou paginação; se uma operação longa é legítima, ponha `set statement_timeout` na definição daquela função.
- at: When uma consulta do app passa do tempo limite do papel, the system shall devolver o erro de tempo esgotado sem mudar o limite do papel; if uma migration aumenta o limite de `anon`, `authenticated` ou `authenticator`, then a varredura shall avisar P16.
- confira: Procure `statement_timeout` nas migrations; `alter role anon`, `authenticated` ou `authenticator` com ele é o aviso.
- ref: https://supabase.com/docs/guides/database/postgres/timeouts

### P17 — Carga pesada contra o banco de produção
- stack: todas
- fase: define
- gravidade: alta
- gatilho: lote
- padrao: só à mão
- arquivos: *.sql, *.js, *.ts, *.py
- frase: Teste de carga, avaliação em lote, importação grande e correção de dados em massa nunca rodam contra o banco de produção em horário de uso; rodam em cópia, ou em produção em lotes pequenos, numa janela combinada.
- evitar: Para cada carga da feature, defina onde roda (cópia, branch ou produção), o tamanho do lote, a pausa entre lotes e a janela; num plano pequeno, o banco pode congelar sem nenhum erro.
- at: When a importação ou a correção em lote roda, the system shall processar em lotes de tamanho fixo com pausa entre eles; if o lote estoura o tempo ou a memória, then the system shall parar e dizer em que lote parou, sem refazer o que já foi gravado.
- confira: Antes de rodar uma carga, escreva onde ela roda, o tamanho do lote e a janela; durante, acompanhe no painel o uso de CPU, memória e swap e pare se o swap subir.
- ref: https://supabase.com/docs/guides/platform/compute-and-disk
