# Aplicar a migration no banco (passo 4b do Build)

Ler **só quando o File Manifest tem migration** — um item `*.sql`, uma pasta `migrations/` ou uma ação
descrita como migration. Sem migration no manifest, este arquivo não se aplica e o passo é pulado sem
mencionar banco.

O passo existe porque, sem ele, o Design lista a migration, o Build grava o `.sql` e a Release faz o
push do `.sql` — e **ninguém a executa no banco**. O Verify Gate então sai vermelho ou inconclusivo sem
dizer por quê, e o código vai para produção chamando uma coluna que não existe.

Quatro regras governam tudo abaixo:

1. **Descubra, não pergunte o que dá para descobrir.** Ferramenta, projeto e tipo de banco se leem da
   máquina; o aluno só decide o que é ambíguo.
2. **O aluno vê o destino e o SQL antes do único OK.** Nome **e** ref do projeto, nunca "o do config".
   Contas têm vários projetos (teste, curso, cliente) e aplicar no errado **não tem undo**.
3. **Exit 0 não é prova.** Migration aplicada é migration **lida de volta** do banco.
4. **Um passo por vez.** Aplicar, ler o resultado, provar, e só então o Verify Gate — nunca aplicar e
   rodar o gate na mesma leva: se a aplicação falhar ou voltar `declined`, o gate rodaria contra um
   banco sem a migration.

## 1. Descobrir (sem perguntar)

Nesta ordem, anotando o que encontrou:

**Ferramenta**
- `supabase --version` responde **e** `supabase db push --help` lista `--dry-run` ⇒ **CLI** (caminho
  preferido: tem prévia e `migration list`). CLI antiga, sem `--dry-run`: sugira atualizar; se não der, siga
  pelo **MCP** ou pelo **manual** (neles a prévia é o próprio bloco de confirmação) — não trave o passo.
- Há um MCP do Supabase na sessão (ferramentas `list_projects`, `apply_migration`, `execute_sql`,
  `list_migrations`) ⇒ **MCP**.
- Nenhum dos dois ⇒ **manual**: o aluno cola o SQL no SQL Editor do painel do Supabase, e você entrega o
  `select` de prova para ele rodar em seguida. O passo não fica inconclusivo por falta de ferramenta.
- Outra ferramenta de migration (Prisma, Flyway, Rails) ⇒ o mesmo protocolo com os comandos dela; o
  Supabase é o caminho provado aqui.

**Projeto** (ref = os 20 caracteres que aparecem na URL `https://<ref>.supabase.co`)
- `supabase/.temp/project-ref` — gravado pelo `supabase link`. ⚠️ O `project_id` do `supabase/config.toml`
  é o **nome local** dado pelo `supabase init`, não a ref: não o use como destino.
- `.env`: `SUPABASE_PROJECT_REF`, ou a ref dentro de `SUPABASE_URL`.
- MCP `list_projects` (devolve `id` = ref e `name`) ou `supabase projects list` (coluna REF; o ligado vem
  marcado com `●`).
- O **nome** sempre vem de `supabase projects list` / `list_projects`. Ref sem nome não serve para o aluno
  reconhecer o projeto.
- **Nenhum projeto** descoberto por arquivo ⇒ não escolha: liste os projetos da conta (nome + ref) e
  pergunte ao aluno qual é. Se a conta só tem um, ele é o candidato — mas ainda passa pela confirmação.

**Tipo de banco**
- `supabase status` responde ⇒ há banco **local** (`supabase start`); a migration pode ser testada nele
  primeiro. ⚠️ `supabase db reset` **apaga o banco local inteiro** e o recria do zero (todas as migrations
  + seed): os dados de teste que estavam lá somem. Só sugira com o aluno sabendo disso, e nunca contra o
  remoto; para testar sem perder dados locais, `supabase migration up` aplica só o que falta.
- Sem local, o remoto é o **único banco** do projeto — e conta como **produção**, mesmo que o aluno o
  chame de "teste". A confirmação diz isso.

**Divergência** — a parada que impede o estrago:
- A ref do `.temp/project-ref` ou do `.env` é diferente da ref em que a CLI/MCP está logada ou do único
  projeto listado? Ou há dois candidatos? ⇒ **pare antes de qualquer confirmação** e **mostre os dois**
  (nome + ref de cada): "O `supabase/.temp/project-ref` aponta para **A** (`ref…`); a CLI está ligada a
  **B** (`ref…`). Qual é o certo?". Não escolha; nada é aplicado até o aluno responder. Projetos
  diferentes em fontes diferentes é o sinal de que a máquina do aluno já apontou para o lugar errado uma
  vez.
- **Depois da escolha, alinhe o vínculo antes de qualquer prévia:** `supabase link --project-ref <ref
  escolhida>` e confira que `supabase/.temp/project-ref` passou a conter exatamente essa ref (e que
  `supabase projects list` marca ● nela). O `--linked` de todos os comandos seguintes aponta para o vínculo,
  não para a resposta do aluno: sem religar, a prévia e o push iriam para o projeto antigo mesmo com a
  confirmação feita para o novo. Vínculo diferente da ref aprovada ⇒ pare.

**Registro** — o que você descobriu (ferramenta, projeto nome + ref, local ou remoto único) vai
para o bloco de confirmação da seção 4 e, depois, para a linha da migration em `## Migrations
aplicadas` do BUILD_REPORT. Não há arquivo de ambiente à parte: é dessa linha que a `sdd-release` tira
o campo "Banco:" do bloco do OK.

## 2. Já está aplicada?

Antes de propor qualquer coisa:

- CLI: `supabase migration list --linked` — a versão (o timestamp do nome do arquivo) aparece na coluna
  **Remote**? Então já foi aplicada.
- MCP: `list_migrations(project_id)` devolve a versão.
- Manual (sem histórico de migrations para ler): só conta como já aplicada com o registro do aluno ("rodei
  este arquivo em <data>") **ou** quando **todos** os efeitos específicos desta migration já estão no banco
  (a coluna nova existe, o valor novo está lá, o objeto removido não está). A existência de uma tabela que
  já existia antes **não** prova nada — um `UPDATE` ou um `ALTER` pendente deixa o objeto no lugar e o
  efeito da migration ausente.

Já aplicada ⇒ **não reaplicar**. Registre na seção `## Migrations aplicadas` do BUILD_REPORT a linha com
"já aplicada em <data>" (a data que a lista mostrar) e siga para a prova (seção 5) — aplicada não é o
mesmo que aplicada **neste** projeto.

## 3. Prévia

- **CLI:** `supabase db push --linked --dry-run` imprime o que seria aplicado. ⛔ O `db push` aplica
  **todas as migrations pendentes** da pasta `supabase/migrations/`, não só a do manifest. Leia a lista:
  - só a(s) migration(s) do manifest ⇒ siga;
  - há migration pendente **fora do manifest** desta feature ⇒ **pare antes do bloco de confirmação** e
    mostre ao aluno o arquivo e o SQL dela. Ela não é desta frente: o aluno decide se ela entra na
    confirmação (e então é mostrada inteira, como as outras) ou se sai da pasta antes do push. Nunca
    aplique SQL que o aluno não viu.
- **MCP:** `apply_migration` não tem dry-run — a prévia **é** o bloco de confirmação. Ele aplica só o que
  você enviar.
- **Manual:** idem.

## 4. A confirmação — uma parada só

Mostre **um bloco**, neste formato, e espere a resposta. Não há segunda pergunta depois dele.

```markdown
**Migration:** `supabase/migrations/20261025_cliente_cnpj.sql` (14 linhas)
**Destino:** projeto **Curso RDD10** (ref `abcdefghijklmnopqrst`) — remoto, **único banco do projeto ⇒ é produção**
**Ferramenta:** `supabase db push --linked` — dry-run: 1 migration pendente (esta; nenhuma outra fora do manifest)
⛔ **Atenção:** o SQL tem `ALTER TABLE cliente DROP COLUMN telefone` — apaga dados; **não há undo**.

```sql
<conteúdo inteiro do arquivo>
```

**Posso aplicar neste projeto?**
```

Regras do bloco:

- **Nome e ref** do projeto, sempre os dois. Local ou remoto. Se é o único banco, dizer que é produção.
- **SQL inteiro**, nunca resumo — um bloco `sql` por migration que a prévia listou.
- A linha ⛔ entra quando o SQL (sem comentários, sem diferenciar maiúsculas) contém `DROP TABLE`,
  `DROP SCHEMA`, `DROP FUNCTION`, `DROP VIEW`, `DROP POLICY`, `DROP TRIGGER`, `DROP TYPE`, `DROP INDEX`,
  `ALTER TABLE … DROP COLUMN`, `TRUNCATE`, ou `DELETE`/`UPDATE` sem `WHERE` no mesmo comando — e também quando o destino é o único
  banco do projeto. Diga o que ela faz com os dados ("apaga a coluna e o que havia nela").
- A frase **não há undo** fica, mesmo sem DDL destrutivo: coluna nova também não se desfaz sozinha.
- É a única pergunta do passo. A escolha do modo de execução (passo 3b da skill) aconteceu antes e é outra
  coisa; a divergência de projeto (seção 1) para **antes** deste bloco, não dentro dele.

Resposta diferente de um sim claro ⇒ não aplique; volte ao que o aluno pediu.

## 5. Aplicar e provar

**Aplicar**
- CLI: antes, `supabase/.temp/project-ref` tem de ser **a mesma ref do bloco de confirmação** (é para onde o
  `--linked` manda) — diferente ⇒ pare e religue. Depois, `supabase db push --linked`. Pediu senha? É a senha do banco do `supabase link`
  (`SUPABASE_DB_PASSWORD` evita o prompt) — nunca invente. `project not linked` ⇒
  `supabase link --project-ref <a ref confirmada>` e repita.
- MCP: `apply_migration(project_id, name, query)` com o **arquivo inteiro** como `query` — nunca um trecho
  editado, nunca o SQL "limpo": o que entrar no banco tem de ser o que está no repositório. Voltou
  `{"status":"declined"}`? É a confirmação de comando destrutivo do **servidor** Supabase (DROP, DELETE),
  não uma permissão sua. **Nunca reescreva a migration** para escapar dela — entregue o arquivo para o
  aluno rodar no SQL Editor e siga para a prova.
- Manual: entregue o caminho e o conteúdo do arquivo; peça "rodei" antes de provar.

**Provar por leitura** — em dois níveis; o relatório diz qual você obteve:

- (a) **Versão registrada:** `supabase migration list --linked` mostra a versão em Remote, ou MCP
  `list_migrations` a devolve. É o histórico de migrations do projeto.
- (b) **Objeto vivo:** um `select` por objeto que a migration cria ou altera, via MCP `execute_sql` ou
  colado no SQL Editor:

```sql
select table_name  from information_schema.tables  where table_schema = 'public' and table_name = 'cliente';
select column_name, data_type from information_schema.columns where table_name = 'cliente' and column_name = 'cnpj';
select proname     from pg_proc     where proname = 'fn_cliente_valida_cnpj';
select policyname  from pg_policies where tablename = 'cliente';
```

  A prova é do **efeito da migration**, não da existência de um objeto: migration que **cria** ⇒ o `select`
  tem de achar (linha vazia = não aplicada); migration que **remove** (`DROP`, `DELETE`) ⇒ o `select` tem de
  voltar vazio (**ausência esperada** = aplicada; a linha ainda lá = não aplicada); migration que **altera**
  dado ⇒ ler o valor novo. Resultado contrário ao efeito esperado = **não aplicada** (projeto errado ou SQL
  sem efeito): volte à descoberta do projeto. O `exit 0` do comando **não prova** nada: só a leitura prova.

- **Função com lógica** (PL/pgSQL): o banco só valida nomes de coluna na **primeira execução**. Uma
  chamada de teste dentro de transação, desfeita em seguida, com um valor de teste que a regra aceita
  (nunca o documento de um cliente real):
  `begin; select fn_cliente_valida_cnpj('<valor de teste>'); rollback;`

Só CLI, sem MCP ⇒ (a) é obrigatório e (b) vai como `select` pronto para o SQL Editor; escreva isso na
célula de prova.

## 6. Registrar

Salve a leitura de volta como evidência, com o comando na 1ª linha (o mesmo formato dos logs de AT,
`sdd/templates/fragments/EVIDENCIA.md`):

```bash
cmd='supabase migration list --linked'
{ echo "\$ $cmd"; eval "$cmd" 2>&1 | tail -n 200; } > sdd/reports/evidence/{FEATURE}/MIG-001.log
```

O `select` da prova (b) feito pelo MCP entra no mesmo log, com uma linha `$ execute_sql: <select>` antes
do resultado. No BUILD_REPORT, a seção `## Migrations aplicadas` (o template a traz como condicional;
o `sdd/bin/report-lint.py` a exige quando a tabela de arquivos lista `*.sql`, `migrations/` ou o glob
de `layers.sql`) ganha uma linha por migration, com o **mesmo caminho** da tabela de arquivos:

```markdown
| Arquivo | Projeto (nome · ref) | Aplicada em | Prova por leitura |
|---|---|---|---|
| `supabase/migrations/20261025_cliente_cnpj.sql` | Curso RDD10 · `abcdefghijklmnopqrst` | 2026-10-25 14:32 (cli) | `evidence/{FEATURE}/MIG-001.log` (migration list: Remote ✓ · columns: cnpj text ✓) |
```

- Já estava aplicada ⇒ `Aplicada em` = "já aplicada em <data>".
- Modo manual (o aluno rodou o `select` no SQL Editor e disse o resultado) ⇒ a prova é
  `recibo: <nome do aluno> AAAA-MM-DD`, com o que ele viu ("coluna cnpj apareceu").
- `exit 0`, "aplicada com sucesso" ou "deve estar lá" na célula ⇒ o `report-lint` reprova: não é leitura.

Depois disto — e só depois — o Verify Gate (passo 5a da skill). Se ele sair 2 ou 3, a primeira hipótese é
"migration não aplicada ou aplicada em outro projeto": repita a seção 5 antes de mexer em código.
