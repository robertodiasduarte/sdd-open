# Catálogo de governança

> Fonte única dos itens que a revisão de governança confere num DEFINE de sistema financeiro, contábil
> ou fiscal. A pergunta que todo item responde: **daqui a cinco anos, um fiscal, um auditor ou um perito
> reconstrói o que aconteceu, quem fez e por quê — com prova de que nada foi alterado depois?**
>
> Regra de ouro dos testes: provar que a ação **proibida falha**. Teste que só confere que a
> funcionalidade existe passa sem provar nada.

## Como ler este catálogo

- **Tabela A** lista os itens. A coluna `base` aponta para a **Tabela B** (bases legais) ou traz `—`.
- **Tabela B** lista as bases legais. Só uma base com `status: confirmado` pode ser citada no relatório,
  e só pelo `texto_citavel` dela. Base `nao-confirmado` **não se cita**: o relatório usa a frase padrão
  do procedimento e fica com o fundamento técnico.
- `porte_min` diz a partir de que porte o item **se aplica** — no mínimo inegociável e nos de IA, obrigatório;
  na segunda camada, recomendado (veja o passo 3 do procedimento) —, lendo o `GOVERNANCA_PADRAO.md` do projeto:
  `todos` · `equipe` (campo `uso` = equipe ou clientes) · `multi_cnpj` (campo `multi_cnpj` = sim) ·
  `ia` (campo `ia_grava_sozinha` = sim, ou o DEFINE menciona IA que grava, classifica ou sugere lançamento).
  Abaixo do porte, o item é `N.A. por porte`, com o motivo.
- `pós-build` cita o item do checklist da skill `rdd-audita-schema` que prova o mesmo ponto no SQL já
  escrito. A revisão de governança acontece no papel, antes do Design; a auditoria de schema, depois do Build.
- Os nomes de tabela das provas (`lancamento`, `lancamento_linha`, `periodo`, `auditoria`, `aprovacao`,
  `documento`) são de referência: adapte aos nomes do DEFINE e **não mexa na inversão** do teste.

## Tabela A — itens

### Mínimo inegociável

| id | elemento | exigência | mecanismo de referência (Postgres) | gate negativo | base | sev | porte_min | pós-build |
|----|----------|-----------|------------------------------------|---------------|------|-----|-----------|-----------|
| G01 | Lançamento que não se apaga | Sem UPDATE nem DELETE em lançamento gravado; correção só por estorno ou complementação, com motivo | `REVOKE UPDATE, DELETE` do papel da aplicação **e** trigger que lança erro (o REVOKE não alcança o dono da tabela) | UPDATE e DELETE em lançamento gravado **falham** | B1, B2 | alta | todos | 5, 13 |
| G02 | Partidas dobradas no banco | Débito = crédito em cada lançamento | Constraint trigger `DEFERRABLE INITIALLY DEFERRED` que soma as linhas do lançamento | Lançamento desbalanceado **é rejeitado** | — | alta | todos | 14 |
| G03 | Fechamento de período | Competência fechada não aceita lançamento; reabrir é um evento com motivo e aprovador | Tabela `periodo` (competência, situação, quem fechou, quando) + trigger no lançamento | Lançar em período fechado **falha**; reabrir sem aprovador **falha** | — | alta | todos | 6 |
| G04 | Trilha de auditoria do negócio | Quem, quando (UTC), de onde, antes e depois, e **por quê** de cada ação que muda dado contábil | Tabela append-only escrita só por função `security definer`; o papel da aplicação não tem INSERT direto | Ação gera 1 linha na trilha; INSERT direto do cliente **falha** | — | alta | todos | 2 |
| G05 | Log forense de segurança | Acessos, falhas de login, **leituras** de dado sensível, exportações, uso do certificado digital | Log separado da trilha de negócio, retenção própria, cópia fora do banco | Exportar um relatório **gera** evento de leitura | — | média | equipe | — |
| G06 | Prova de que o log não foi editado | Mostrar que a trilha não foi alterada, nem por administrador | Hash encadeado por linha + âncora diária fora do sistema (armazenamento imutável, e-mail, repositório git) | Verificador recalcula a cadeia; alterar 1 linha **quebra** a verificação | — | média | equipe | — |
| G07 | Segregação de funções | Quem lança não aprova; acima da alçada, duas aprovações | Papéis + RLS; aprovação como entidade própria (quem cria ≠ quem aprova) | Mesmo usuário criar e aprovar **é rejeitado** | — | alta | equipe | 2 |
| G08 | Documento-fonte imutável | Todo lançamento aponta para a origem; o original fica guardado com hash | Storage sem sobrescrita + SHA-256 gravado na ingestão | Trocar o arquivo ou o hash de um documento já ligado **falha** | — | alta | todos | — |
| G09 | Aritmética exata | Nunca ponto flutuante em valor; regra de arredondamento e do centavo residual escrita | `numeric(18,2)` no valor; mais casas no cálculo intermediário; rateio com resíduo atribuído por regra | Nenhuma coluna de valor em `real`/`double precision`; rateio de 100 por 3 fecha em 100,00 | — | alta | todos | 1 |
| G10 | Importação idempotente | Reimportar o mesmo arquivo não duplica nada | UNIQUE na chave natural (identificador da transação no extrato, chave de acesso da nota de 44 dígitos) | Importar 2 vezes deixa a mesma contagem; a 2ª inserção da mesma chave **falha** | — | alta | todos | 4 |

### Segunda camada

| id | elemento | exigência | mecanismo de referência (Postgres) | gate negativo | base | sev | porte_min | pós-build |
|----|----------|-----------|------------------------------------|---------------|------|-----|-----------|-----------|
| G11 | Regra com vigência e memória de cálculo | Toda regra fiscal ou de cálculo tem `vigencia_inicio`/`vigencia_fim`; o resultado guarda a memória de cálculo | Tabela de regras por vigência; cálculo grava a regra e os insumos usados | Recalcular uma competência passada reproduz o mesmo valor | — | média | todos | 16 |
| G12 | Conciliação com totais de controle | Diferença vira pendência explícita, nunca ajuste silencioso | Totais de controle por lote; tabela de pendências | Lote com diferença **não fecha** sem pendência registrada | — | média | todos | — |
| G13 | Isolamento entre clientes | O dado de um CNPJ nunca aparece para o usuário de outro | RLS por empresa + chave estrangeira composta `(empresa_id, id)` | Usuário da empresa A **não lê** linha da empresa B (teste com 2 usuários) | — | alta | multi_cnpj | 2 |
| G14 | Retenção × proteção de dados | Guardar até a prescrição; o pedido de eliminação cede à obrigação legal (pseudonimizar em vez de apagar) | Prazo de guarda por tipo de documento; rotina de pseudonimização | Pedido de eliminação de dado sob guarda legal **não apaga** o registro contábil | B3, B4 | média | todos | — |
| G15 | Backup com restauração testada | Backup que nunca foi restaurado não é backup | Rotina de restauração periódica num ambiente separado | Restauração de teste recupera o último fechamento | — | média | equipe | — |
| G16 | Certificado digital e segredos | Certificado A1 e chaves fora do código e do banco em claro; todo uso vai ao log forense | Cofre de segredos; certificado cifrado; evento por uso | Procurar o certificado no repositório e no banco **não acha** | — | alta | todos | — |

### Quando há IA no sistema

| id | elemento | exigência | mecanismo de referência (Postgres) | gate negativo | base | sev | porte_min | pós-build |
|----|----------|-----------|------------------------------------|---------------|------|-----|-----------|-----------|
| G17 | IA sugere, humano confirma | Nada entra no razão sem aceite de uma pessoa | Sugestão em tabela própria; lançamento só por ação de usuário identificado | Gravação pela IA direto no razão **falha** | — | alta | ia | — |
| G18 | Registro da decisão da IA | Modelo, versão do prompt, confiança, quem aceitou, se editou antes de aceitar | Colunas na sugestão + na trilha (G04) | Sugestão aceita sem esses campos **é rejeitada** | — | média | ia | — |
| G19 | Taxa de correção | Medir quanto o humano corrige a IA, para detectar aceite sem leitura | Indicador por usuário e período | Relatório mostra a taxa por usuário | — | baixa | ia | — |
| G20 | Responsabilidade técnica | A responsabilidade é do profissional (CRC), não da ferramenta | Responsável técnico registrado no fechamento | Fechar período sem responsável técnico **falha** | — | média | ia | — |

## Tabela B — bases legais

> ⛔ Nenhuma base abaixo pode ser citada enquanto estiver `nao-confirmado`. Para virar `confirmado`, a
> linha precisa de fonte oficial, data de captura, o trecho literal em `texto_citavel` e o recibo de quem
> responde pelo catálogo. Vigência e localizador são conferidos na fonte, nunca de memória.

| id | citação | degrau | vigência | fonte | captura | status | recibo | texto_citavel |
|----|---------|--------|----------|-------|---------|--------|--------|---------------|
| B1 | Código Civil, art. 1.183 (escrituração) | lei | a conferir | https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm | — | nao-confirmado | — | — |
| B2 | ITG 2000 (R1) — escrituração contábil, retificação de lançamento | ato técnico | a conferir | https://cfc.org.br/ | — | nao-confirmado | — | — |
| B3 | Código Tributário Nacional (CTN), art. 195, parágrafo único (conservação de livros) | lei | a conferir | https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm | — | nao-confirmado | — | — |
| B4 | Lei Geral de Proteção de Dados (LGPD), art. 16, I (conservação para obrigação legal) | lei | a conferir | https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm | — | nao-confirmado | — | — |

## Provas por item

> `prova_manual` é o roteiro que o profissional executa e marca. `prova_script`, quando existe, vem em uma
> de duas formas, e as duas saem `0` **só quando o sistema está certo**:
>
> - **`forma: negativa`** — tenta a ação proibida dentro de `begin … rollback`. Se o banco **aceitar**,
>   levanta `GOVERNANCA Gnn REPROVADA` (exit diferente de 0). Se o banco **recusar**, registra um aviso e
>   termina bem. Não ponha `!` nem `|| true` na frente: a inversão já está dentro do script.
> - **`forma: catalogo`** — só lê o catálogo do banco e levanta `GOVERNANCA Gnn REPROVADA` se achar o erro.
>
> Rodar com: `psql -v ON_ERROR_STOP=1 -f <arquivo>.sql` **contra um banco de desenvolvimento, de teste ou um
> branch — nunca contra produção**: mesmo dentro de `begin … rollback`, a tentativa trava a linha e dispara
> os triggers. Item sem `prova_script` se prova só pelo roteiro.
> Tabela vazia nunca passa: sem linha não há o que provar, e o script diz isso em vez de ficar verde.
> **Só conta como recusa o código que o mecanismo do item produz** — a lista branca de cada script:
> `P0001` (trigger com `raise exception`), `42501` (permissão negada), `23514` (CHECK), `23505` (UNIQUE, no G10).
> Qualquer outro erro — tabela ou coluna inexistente, NOT NULL ou chave estrangeira no INSERT de preparação,
> sintaxe — **não prova a regra**: o script sai `REPROVADA: a tentativa falhou por outro motivo`. Se o seu
> mecanismo recusa com outro código, acrescente esse código à lista do item; nunca troque por "qualquer erro".

### G01 — prova

Se o seu mecanismo for privilégio **por coluna** (e não trigger de linha), repita o UPDATE do script para
cada coluna do lançamento — o script de referência testa uma coluna porque o trigger recusa a linha inteira.

**prova_manual:** 1) abra um lançamento gravado; 2) tente alterar o valor; 3) tente excluir; 4) as duas
tentativas são recusadas com mensagem clara; 5) o estorno cria um lançamento novo, com motivo, apontando
para o original.

**prova_script** (`forma: negativa`):

```sql
-- G01 — passa SÓ se o banco RECUSAR alterar e excluir lançamento gravado.
begin;
-- Preparação em bloco próprio: o papel LÊ as tabelas e há o que provar. Qualquer erro aqui reprova —
-- assim um 42501 no bloco da tentativa só pode vir da ESCRITA proibida, nunca da leitura.
do $$
begin
  if not has_table_privilege('lancamento', 'SELECT') then
    raise exception 'GOVERNANCA G01 REPROVADA: a preparacao falhou, este papel nao le lancamento — rode com um papel que leia a tabela';
  end if;
  if not exists (select 1 from lancamento) then
    raise exception 'GOVERNANCA G01 REPROVADA: lancamento vazia, nada a provar — grave 1 lancamento de teste';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G01 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
begin
  update lancamento set historico = historico where id = (select id from lancamento limit 1);
  raise exception 'GOVERNANCA G01 REPROVADA: UPDATE em lancamento foi aceito pelo banco';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('P0001', '42501') then
    raise exception 'GOVERNANCA G01 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G01 ok (update recusado): %', sqlerrm;
end $$;
do $$
begin
  delete from lancamento where id = (select id from lancamento limit 1);
  raise exception 'GOVERNANCA G01 REPROVADA: DELETE em lancamento foi aceito pelo banco';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('P0001', '42501') then
    raise exception 'GOVERNANCA G01 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G01 ok (delete recusado): %', sqlerrm;
end $$;
rollback;
```

### G02 — prova

**prova_manual:** 1) grave um lançamento com débito e crédito de 100,00 (tem de gravar); 2) monte outro só com
o débito de 100,00; 3) tente gravar; 4) a gravação é recusada e nada fica salvo.

**prova_script** (`forma: negativa`):

```sql
-- G02 — passa SÓ se o banco RECUSAR um lançamento desbalanceado.
begin;
-- Preparação com CONTROLE: um lançamento BALANCEADO tem de gravar. Se nem ele grava, o script não confere
-- com o schema (coluna obrigatória, CHECK alheio) e nada do que vem depois provaria a regra.
do $$
declare v_id bigint;
begin
  begin
    insert into lancamento (historico) values ('controle G02') returning id into v_id;
    insert into lancamento_linha (lancamento_id, natureza, valor) values (v_id, 'D', 100.00);
    insert into lancamento_linha (lancamento_id, natureza, valor) values (v_id, 'C', 100.00);
    set constraints all immediate;
    raise exception 'GOVERNANCA_CONTROLE_OK';
  exception when others then
    if sqlerrm <> 'GOVERNANCA_CONTROLE_OK' then
      raise exception 'GOVERNANCA G02 REPROVADA: a preparacao falhou, um lancamento balanceado nao grava (%): %', sqlstate, sqlerrm;
    end if;
  end;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G02 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
declare v_id bigint;
begin
  -- a MESMA linha que o controle gravou (D 100,00), sozinha: qualquer CHECK que deixou o controle passar
  -- deixa esta passar também — só o balanceamento pode recusá-la
  insert into lancamento (historico) values ('teste G02') returning id into v_id;
  insert into lancamento_linha (lancamento_id, natureza, valor) values (v_id, 'D', 100.00);
  set constraints all immediate;
  raise exception 'GOVERNANCA G02 REPROVADA: lancamento desbalanceado foi aceito';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('P0001', '23514') then
    raise exception 'GOVERNANCA G02 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G02 ok: %', sqlerrm;
end $$;
rollback;
```

### G03 — prova

**prova_manual:** 1) feche uma competência; 2) tente lançar nela; 3) a gravação é recusada; 4) tente
reabrir sem informar aprovador e motivo; 5) a reabertura é recusada.

**prova_script** (`forma: negativa`):

```sql
-- G03 — passa SÓ se o banco RECUSAR lançamento em competência fechada.
begin;
-- Preparação em bloco próprio: o papel LÊ as tabelas e há o que provar. Qualquer erro aqui reprova —
-- assim um 42501 no bloco da tentativa só pode vir da ESCRITA proibida, nunca da leitura.
do $$
begin
  if not has_table_privilege('periodo', 'SELECT') then
    raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou, este papel nao le periodo — rode com um papel que leia a tabela';
  end if;
  if not has_table_privilege('lancamento', 'INSERT') then
    raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou, este papel nao insere em lancamento — rode o gate com o papel que a aplicacao usa para gravar';
  end if;
  if exists (select 1 from pg_attribute a
              where a.attrelid = 'lancamento'::regclass and a.attnum > 0 and not a.attisdropped and a.attidentity = ''
                and pg_get_serial_sequence('lancamento', a.attname) is not null
                and not has_sequence_privilege(current_user, pg_get_serial_sequence('lancamento', a.attname), 'USAGE')) then
    raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou, o papel nao usa a sequencia do id de lancamento — a tentativa falharia pela sequencia, nao pela regra';
  end if;
  if not exists (select 1 from periodo where situacao = 'fechado') then
    raise exception 'GOVERNANCA G03 REPROVADA: nenhuma competencia fechada para testar, nada a provar';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
-- Controle: o MESMO insert numa competência ABERTA tem de gravar (e é desfeito). Senão CHECK, RLS ou coluna
-- obrigatória alheios ao fechamento recusariam a tentativa no lugar da regra. Usa a competência aberta mais
-- recente de `periodo`; sem nenhuma, o mês seguinte ao último fechado (ajuste se o seu modelo exigir outra).
do $$
declare v_aberta date;
begin
  select competencia into v_aberta from periodo where situacao <> 'fechado' order by competencia desc limit 1;
  v_aberta := coalesce(v_aberta, ((select max(competencia) from periodo where situacao = 'fechado') + interval '1 month')::date);
  begin
    insert into lancamento (historico, competencia) values ('controle G03', v_aberta);
    raise exception 'GOVERNANCA_CONTROLE_OK';
  exception when others then
    if sqlerrm <> 'GOVERNANCA_CONTROLE_OK' then
      raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou, o mesmo lancamento numa competencia aberta nao grava (%): %', sqlstate, sqlerrm;
    end if;
  end;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G03 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
declare v_comp date;
begin
  select competencia into v_comp from periodo where situacao = 'fechado' limit 1;
  insert into lancamento (historico, competencia) values ('teste G03', v_comp);
  raise exception 'GOVERNANCA G03 REPROVADA: lancamento em competencia fechada foi aceito';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('P0001', '23514', '42501') then
    raise exception 'GOVERNANCA G03 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G03 ok: %', sqlerrm;
end $$;
rollback;
```

### G04 — prova

**prova_manual:** 1) faça um estorno pela aplicação; 2) confira 1 linha nova na trilha com quem, quando
(UTC), antes, depois e motivo; 3) tente inserir, alterar e apagar linhas da trilha direto pelo cliente; 4) as
três tentativas são recusadas.

O script prova a metade **negativa** (o cliente não insere, não altera, não apaga). A metade **positiva** —
cada ação de negócio gera 1 linha na trilha — não se prova por SQL sem conhecer a aplicação: os passos 1 e 2 do
`prova_manual` ficam no AT mesmo quando o script existe.

**prova_script** (`forma: negativa` — troque `papel_da_aplicacao` pelo papel que o app usa):

```sql
-- G04 — passa SÓ se o papel da aplicação NÃO conseguir inserir, alterar nem apagar a trilha.
begin;
do $$
begin
  if has_table_privilege('papel_da_aplicacao', 'auditoria', 'INSERT') then
    if exists (select 1 from pg_attribute a
                where a.attrelid = 'auditoria'::regclass and a.attnum > 0 and not a.attisdropped and a.attidentity = ''
                  and pg_get_serial_sequence('auditoria', a.attname) is not null
                  and not has_sequence_privilege('papel_da_aplicacao', pg_get_serial_sequence('auditoria', a.attname), 'USAGE')) then
      raise exception 'GOVERNANCA G04 REPROVADA: a preparacao falhou, o papel nao usa a sequencia do id de auditoria — a tentativa falharia pela sequencia, nao pela regra';
    end if;
  end if;
  if not exists (select 1 from auditoria) then
    raise exception 'GOVERNANCA G04 REPROVADA: trilha vazia, nada a provar — grave 1 evento de teste';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G04 REPROVADA: a preparacao falhou, a trilha nao confere com o schema (%): %', sqlstate, sqlerrm;
end $$;
set local role papel_da_aplicacao;
do $$
begin
  insert into auditoria (acao, motivo) values ('teste G04', 'escrita direta');
  raise exception 'GOVERNANCA G04 REPROVADA: o cliente escreveu direto na trilha de auditoria';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('42501', 'P0001') then
    raise exception 'GOVERNANCA G04 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G04 ok (insert recusado): %', sqlerrm;
end $$;
do $$
begin
  update auditoria set motivo = 'alterado';
  raise exception 'GOVERNANCA G04 REPROVADA: o cliente alterou a trilha de auditoria';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('42501', 'P0001') then
    raise exception 'GOVERNANCA G04 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G04 ok (update recusado): %', sqlerrm;
end $$;
do $$
begin
  delete from auditoria;
  raise exception 'GOVERNANCA G04 REPROVADA: o cliente apagou a trilha de auditoria';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('42501', 'P0001') then
    raise exception 'GOVERNANCA G04 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G04 ok (delete recusado): %', sqlerrm;
end $$;
rollback;
```

### G05 — prova

**prova_manual:** 1) exporte um relatório com dado sensível; 2) confira o evento de leitura no log
forense (quem, quando, o quê); 3) confira que esse log fica fora da trilha de negócio e tem cópia fora
do banco.

### G06 — prova

**prova_manual:** 1) rode o verificador da cadeia: resultado íntegro; 2) num ambiente de teste, altere
1 linha antiga da trilha; 3) rode o verificador de novo: ele aponta a linha quebrada; 4) confira que a
âncora do dia está fora do sistema.

### G07 — prova

**prova_manual:** 1) crie um lançamento acima da alçada com o usuário A; 2) tente aprovar com o mesmo
usuário A; 3) é recusado; 4) aprove com B e depois com C: só então o lançamento é efetivado.

**prova_script** (`forma: negativa`):

```sql
-- G07 — passa SÓ se o banco RECUSAR a aprovação feita por quem criou o lançamento.
begin;
-- Preparação em bloco próprio: o papel LÊ as tabelas e há o que provar. Qualquer erro aqui reprova —
-- assim um 42501 no bloco da tentativa só pode vir da ESCRITA proibida, nunca da leitura.
do $$
begin
  if not has_table_privilege('lancamento', 'SELECT') then
    raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou, este papel nao le lancamento — rode com um papel que leia a tabela';
  end if;
  if not has_table_privilege('aprovacao', 'INSERT') then
    raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou, este papel nao insere em aprovacao — rode o gate com o papel que a aplicacao usa para gravar';
  end if;
  if exists (select 1 from pg_attribute a
              where a.attrelid = 'aprovacao'::regclass and a.attnum > 0 and not a.attisdropped and a.attidentity = ''
                and pg_get_serial_sequence('aprovacao', a.attname) is not null
                and not has_sequence_privilege(current_user, pg_get_serial_sequence('aprovacao', a.attname), 'USAGE')) then
    raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou, o papel nao usa a sequencia do id de aprovacao — a tentativa falharia pela sequencia, nao pela regra';
  end if;
  if not exists (select 1 from lancamento where criado_por is not null) then
    raise exception 'GOVERNANCA G07 REPROVADA: nenhum lancamento com autor, nada a provar — grave 1 lancamento de teste com autor';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
-- Controle: a aprovação por OUTRO usuário tem de gravar (e é desfeita, para não virar a 2ª aprovação). Senão CHECK, RLS ou coluna obrigatória alheios à
-- segregação recusariam a tentativa no lugar da regra. Se aprovador_id tiver chave estrangeira para uma tabela
-- de usuários, troque o gen_random_uuid() pelo id de um usuário real que não seja o autor.
do $$
declare v_id bigint; v_autor uuid; v_outro uuid;
begin
  select id, criado_por into v_id, v_autor from lancamento where criado_por is not null limit 1;
  select aprovador_id into v_outro from aprovacao where aprovador_id is distinct from v_autor and aprovador_id is not null limit 1;
  begin
    insert into aprovacao (lancamento_id, aprovador_id) values (v_id, coalesce(v_outro, gen_random_uuid()));
    raise exception 'GOVERNANCA_CONTROLE_OK';
  exception when others then
    if sqlerrm <> 'GOVERNANCA_CONTROLE_OK' then
      raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou, a aprovacao por outro usuario nao grava (%): %', sqlstate, sqlerrm;
    end if;
  end;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G07 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
declare v_id bigint; v_autor uuid;
begin
  select id, criado_por into v_id, v_autor from lancamento where criado_por is not null limit 1;
  insert into aprovacao (lancamento_id, aprovador_id) values (v_id, v_autor);
  raise exception 'GOVERNANCA G07 REPROVADA: o autor aprovou o proprio lancamento';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  -- 42501 NÃO é prova aqui: com RLS de identidade (aprovador_id = id da sessão) a recusa vem de "a sessão não
  -- é o autor", não da segregação. Se a sua segregação é por RLS, rode como o AUTOR e acrescente '42501'.
  if sqlstate not in ('P0001', '23514') then
    raise exception 'GOVERNANCA G07 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G07 ok: %', sqlerrm;
end $$;
rollback;
```

### G08 — prova

**prova_manual:** 1) abra um lançamento e siga o link até o documento de origem; 2) confira o hash
gravado contra o arquivo baixado; 3) tente substituir o arquivo ou o hash; 4) é recusado.

**prova_script** (`forma: negativa`):

```sql
-- G08 — passa SÓ se o banco RECUSAR trocar o hash de um documento já ligado a lançamento.
begin;
-- Preparação em bloco próprio: o papel LÊ as tabelas e há o que provar. Qualquer erro aqui reprova —
-- assim um 42501 no bloco da tentativa só pode vir da ESCRITA proibida, nunca da leitura.
do $$
begin
  if not has_table_privilege('lancamento', 'SELECT') then
    raise exception 'GOVERNANCA G08 REPROVADA: a preparacao falhou, este papel nao le lancamento — rode com um papel que leia a tabela';
  end if;
  if not has_table_privilege('documento', 'SELECT') then
    raise exception 'GOVERNANCA G08 REPROVADA: a preparacao falhou, este papel nao le documento — rode com um papel que leia a tabela';
  end if;
  if not exists (select 1 from lancamento where documento_id is not null) then
    raise exception 'GOVERNANCA G08 REPROVADA: nenhum lancamento ligado a documento, nada a provar';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G08 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
begin
  update documento set sha256 = encode(sha256(convert_to('troca', 'UTF8')), 'hex') where id = (select documento_id from lancamento where documento_id is not null limit 1);
  raise exception 'GOVERNANCA G08 REPROVADA: o hash do documento-fonte foi alterado';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('P0001', '42501') then
    raise exception 'GOVERNANCA G08 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  raise notice 'G08 ok: %', sqlerrm;
end $$;
rollback;
```

### G09 — prova

**prova_manual:** 1) faça um rateio de 100,00 em 3 partes; 2) confira que as partes somam 100,00 e que
o centavo residual foi para a parte que a regra escrita manda; 3) confira na estrutura do banco que
nenhuma coluna de valor é de ponto flutuante.

**prova_script** (`forma: catalogo`):

```sql
-- G09 — passa SÓ se nenhuma coluna de VALOR (pelo nome) for de ponto flutuante, em qualquer schema do usuário.
begin;
do $$
declare v_col text;
begin
  -- pg_catalog, não information_schema: a view esconde as tabelas a que este papel não tem acesso
  if not exists (select 1 from pg_class c join pg_namespace n on n.oid = c.relnamespace
                  where c.relkind in ('r', 'p') and n.nspname not in ('pg_catalog', 'information_schema')
                    and n.nspname not like 'pg\_%') then
    raise exception 'GOVERNANCA G09 REPROVADA: nenhuma tabela do usuario, nada a provar';
  end if;
  -- colunas de VALOR: acrescente ao padrao os nomes que o seu schema usa para dinheiro
  select string_agg(n.nspname || '.' || c.relname || '.' || a.attname, ', ') into v_col
    from pg_attribute a
    join pg_class c on c.oid = a.attrelid and c.relkind in ('r', 'p')
    join pg_namespace n on n.oid = c.relnamespace
   where n.nspname not in ('pg_catalog', 'information_schema') and n.nspname not like 'pg\_%'
     and a.attnum > 0 and not a.attisdropped
     -- tipo-base, em qualquer profundidade: domínio sobre domínio sobre double precision também é ponto flutuante
     and exists (with recursive cadeia(t) as (
                   select a.atttypid
                   union all
                   select ty.typbasetype from pg_type ty join cadeia on ty.oid = cadeia.t where ty.typbasetype <> 0)
                 select 1 from cadeia where t in ('real'::regtype, 'double precision'::regtype))
     and a.attname ~* '(valor|preco|saldo|total|montante|debito|credito|juros|multa|desconto|aliquota|imposto|tributo|tarifa|salario)';
  if v_col is not null then
    raise exception 'GOVERNANCA G09 REPROVADA: ponto flutuante em %', v_col;
  end if;
  raise notice 'G09 ok: nenhuma coluna de valor em real/double precision';
end $$;
rollback;
```

### G10 — prova

**prova_manual:** 1) importe um extrato; 2) anote a contagem de lançamentos; 3) importe o mesmo arquivo
de novo; 4) a contagem não muda e a tela diz que nada novo foi importado.

**prova_script** (`forma: negativa` — troque `chave_natural` pela coluna que identifica a transação):

```sql
-- G10 — passa SÓ se o banco RECUSAR a 2ª inserção da mesma chave natural.
begin;
-- Preparação em bloco próprio: o papel LÊ as tabelas e há o que provar. Qualquer erro aqui reprova —
-- assim um 42501 no bloco da tentativa só pode vir da ESCRITA proibida, nunca da leitura.
do $$
begin
  if not has_table_privilege('lancamento', 'SELECT') then
    raise exception 'GOVERNANCA G10 REPROVADA: a preparacao falhou, este papel nao le lancamento — rode com um papel que leia a tabela';
  end if;
  if not exists (select 1 from lancamento where chave_natural is not null) then
    raise exception 'GOVERNANCA G10 REPROVADA: nenhum lancamento com chave natural, nada a provar';
  end if;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G10 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
-- Controle: um lançamento com chave NOVA tem de gravar — prova que id, sequência e colunas obrigatórias não
-- recusam por conta própria a inserção da tentativa.
do $$
begin
  begin
    insert into lancamento (historico, chave_natural) values ('controle G10', 'controle-g10-' || txid_current());
    raise exception 'GOVERNANCA_CONTROLE_OK';
  exception when others then
    if sqlerrm <> 'GOVERNANCA_CONTROLE_OK' then
      raise exception 'GOVERNANCA G10 REPROVADA: a preparacao falhou, um lancamento com chave nova nao grava (%): %', sqlstate, sqlerrm;
    end if;
  end;
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  raise exception 'GOVERNANCA G10 REPROVADA: a preparacao falhou (%): %', sqlstate, sqlerrm;
end $$;
do $$
declare v_cons text;
begin
  insert into lancamento (historico, chave_natural)
  select 'teste G10', chave_natural from lancamento where chave_natural is not null limit 1;
  -- UNIQUE DEFERRABLE só confere no commit: força a conferência AGORA, dentro deste bloco
  set constraints all immediate;
  raise exception 'GOVERNANCA G10 REPROVADA: chave natural repetida foi aceita';
exception when others then
  if sqlerrm like 'GOVERNANCA G%' then raise; end if;
  if sqlstate not in ('23505') then
    raise exception 'GOVERNANCA G10 REPROVADA: a tentativa falhou por outro motivo, nao pela regra (%): %', sqlstate, sqlerrm;
  end if;
  get stacked diagnostics v_cons = constraint_name;
  -- o índice violado tem de CONTER a chave natural: conflito na PK ou em outra UNIQUE não prova nada
  -- só as colunas de CHAVE do índice (as do INCLUDE não participam da unicidade); por definição de cada
  -- coluna, vale também UNIQUE por expressão, como lower(chave_natural); e o índice é DESTA tabela ou de uma
  -- partição dela — um homônimo em outro schema não prova nada
  if not exists (select 1 from pg_index i join pg_class ic on ic.oid = i.indexrelid
                   cross join generate_series(1, i.indnkeyatts) k
                  where ic.relname = v_cons
                    and i.indrelid in (select 'lancamento'::regclass
                                       union select relid from pg_partition_tree('lancamento'::regclass))
                    and pg_get_indexdef(i.indexrelid, k, true) ~* '\mchave_natural\M') then
    raise exception 'GOVERNANCA G10 REPROVADA: o conflito foi em % , que nao contem a chave natural', v_cons;
  end if;
  raise notice 'G10 ok: %', sqlerrm;
end $$;
rollback;
```

### G11 a G20 — prova

Itens da segunda camada e de IA se provam pelo roteiro da coluna `gate negativo` da Tabela A, escrito como
`prova_manual` no requisito: 3 a 5 passos, cada um com o resultado esperado.
