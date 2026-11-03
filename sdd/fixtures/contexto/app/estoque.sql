-- Código fictício: fixture do self-test de sdd/bin/contexto-lint.sh.
create table estoque_saldo (produto_id int primary key, quantidade int not null check (quantidade >= 0));
create table reserva_estoque (pedido_id int, produto_id int, quantidade int not null);
