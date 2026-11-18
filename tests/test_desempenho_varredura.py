"""Contrato de sdd/bin/desempenho-varredura.sh (F27, AT-001 a AT-006 e AT-010).

Cada caso é um repositório git temporário com a base em origin/main (uma ref local) e o que a mudança traz por cima.
As migrations e o código são sintéticos. Exit: 0 nada achado, nada novo ou sem banco · 1 avisos · 64 uso — nunca 2.
"""
from __future__ import annotations

import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/desempenho-varredura.sh"
SEGURANCA = RAIZ / "sdd/bin/seguranca-varredura.sh"
CATALOGO = RAIZ / ".agents/skills/sdd-desempenho-banco/references/CATALOGO_DESEMPENHO.md"
MIG = "supabase/migrations/"

# Uma migration que não acusa nada: chave primária, índice na chave estrangeira, política com select e com papel.
LIMPA = """create table pedidos (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users (id),
  total numeric
);
create index pedidos_user_id_idx on pedidos (user_id);
alter table pedidos enable row level security;
create policy "dono le" on pedidos for select to authenticated using ((select auth.uid()) = user_id);
"""


class Base(Sandbox):
    def projeto(self, arquivos: dict | None = None, base: bool = True):
        p = self.repo("app")
        self.escreve(p, "README.md", "# app\n")
        for rel, txt in (arquivos or {}).items():
            self.escreve(p, rel, txt)
        self.commit(p, "base")
        if base:
            self.git(p, "update-ref", "refs/remotes/origin/main", "HEAD")
        return p

    def varre(self, p, *extra: str, catalogo=CATALOGO) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, "--catalogo", catalogo, *extra], p)
        self.assertIn(rc, (0, 1, 64), "a varredura nunca sai 2 nem outro código: %d\n%s%s" % (rc, out, err))
        return rc, out + err

    def avisos(self, out: str, fid: str) -> list[str]:
        return [ln for ln in out.splitlines() if ln.startswith("⚠️ %s " % fid)]


class Padroes(Base):
    """AT-001: um par (acusa × não acusa) por ficha com padrão."""

    def par(self, fid, rel, acusa, nao_acusa, linha=None):
        supa = {"package.json": '{"dependencies": {"@supabase/supabase-js": "2"}}\n'}   # as fichas de código são de Supabase
        with self.subTest(ficha=fid, lado="acusa"):
            p = self.projeto(supa)
            self.escreve(p, rel, acusa)
            rc, out = self.varre(p)
            self.assertEqual(rc, 1, out)
            achados = self.avisos(out, fid)
            self.assertTrue(achados, out)
            if linha is not None:
                self.assertIn("%s:%d —" % (rel, linha), achados[0])
            self.assertIn("confira à mão:", out)
            self.assertIn("RESULTADO: AVISOS", out)
        self.tearDown(); self.setUp()
        with self.subTest(ficha=fid, lado="não acusa"):
            p = self.projeto(supa)
            self.escreve(p, rel, nao_acusa)
            rc, out = self.varre(p)
            self.assertEqual(self.avisos(out, fid), [], out)
        self.tearDown(); self.setUp()

    def test_p01_politica_sem_select(self):
        self.par("P01", MIG + "002.sql",
                 LIMPA.replace("using ((select auth.uid()) = user_id)", "using (auth.uid() = user_id)"),
                 LIMPA, linha=8)

    def test_p01_current_setting_e_jwt(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql", LIMPA + "create policy \"admin\" on pedidos for update to authenticated\n"
                     "  using ((auth.jwt() ->> 'papel') = 'admin');\n")
        rc, out = self.varre(p)
        self.assertIn("⚠️ P01 alta %s002.sql:10" % MIG, out)

    def test_p02_coluna_da_politica_sem_indice(self):
        self.par("P02", MIG + "002.sql",
                 LIMPA.replace("create index pedidos_user_id_idx on pedidos (user_id);\n", ""),
                 LIMPA)

    def test_p04_tabela_sem_chave_primaria(self):
        self.par("P04", MIG + "002.sql",
                 "create table log (msg text, criado_em timestamptz);\n",
                 "create table log (id bigint generated always as identity primary key, msg text);\n", linha=1)

    def test_p05_duas_permissivas(self):
        dupla = "create policy \"todos le\" on pedidos for select to authenticated using (true);\n"
        restr = "create policy \"so ativos\" on pedidos as restrictive for select to authenticated using (total > 0);\n"
        self.par("P05", MIG + "002.sql", LIMPA + dupla, LIMPA + restr, linha=9)

    def test_p06_politica_sem_papel(self):
        self.par("P06", MIG + "002.sql",
                 LIMPA.replace(" to authenticated using", " using"), LIMPA)

    def test_p07_indice_repetido(self):
        self.par("P07", MIG + "002.sql",
                 LIMPA + "create index pedidos_user_id_idx2 on pedidos (user_id);\n",
                 LIMPA + "create index pedidos_total_idx on pedidos (total);\n", linha=9)

    def test_p08_lista_sem_limite(self):
        self.par("P08", "src/lista.ts",
                 "const { data } = await supabase\n  .from('pedidos')\n  .select('id, total');\n",
                 "const { data } = await supabase\n  .from('pedidos')\n  .select('id, total')\n  .range(0, 19);\n", linha=2)

    def test_p10_contagem_exata(self):
        self.par("P10", "src/lista.ts",
                 "const r = await supabase.from('p').select('id', { count: 'exact' }).range(0, 9);\n",
                 "const r = await supabase.from('p').select('id', { count: 'planned' }).range(0, 9);\n", linha=1)

    def test_p13_http_sincrono_e_nao_o_pg_net(self):
        self.par("P13", MIG + "002.sql",
                 LIMPA + "create function avisa() returns trigger language plpgsql as $$\nbegin\n"
                 "  perform http_get('https://exemplo.invalid/x');\n  return new;\nend;\n$$;\n",
                 LIMPA + "create function avisa() returns trigger language plpgsql as $$\nbegin\n"
                 "  perform net.http_post(url := 'https://exemplo.invalid/x');\n  return new;\nend;\n$$;\n", linha=11)

    def test_p15_busca_por_trecho_e_vetor(self):
        self.par("P15", MIG + "002.sql",
                 LIMPA + "create view busca as select * from pedidos where cast(total as text) ilike '%9%';\n",
                 LIMPA + "create extension if not exists pg_trgm;\n"
                 "create index pedidos_total_trgm on pedidos using gin ((cast(total as text)) gin_trgm_ops);\n"
                 "create view busca as select * from pedidos where cast(total as text) ilike '%9%';\n", linha=9)
        self.par("P15", MIG + "002.sql",
                 LIMPA + "create table docs (id bigint generated always as identity primary key, embedding vector(3));\n",
                 LIMPA + "create table docs (id bigint generated always as identity primary key, embedding vector(3));\n"
                 "create index docs_emb on docs using hnsw (embedding vector_cosine_ops);\n", linha=9)

    def test_p16_tempo_limite_do_papel(self):
        self.par("P16", MIG + "002.sql",
                 LIMPA + "alter role authenticated set statement_timeout = '30s';\n",
                 LIMPA + "create function relatorio() returns void language sql set statement_timeout to '30s' as $$ select 1 $$;\n",
                 linha=9)

    def test_padrao_em_comentario_nao_acusa(self):
        p = self.projeto({"package.json": '{"dependencies": {"@supabase/supabase-js": "2"}}\n'})
        self.escreve(p, MIG + "002.sql", LIMPA + "-- antes era: alter role authenticated set statement_timeout = '30s';\n"
                     "/* create policy \"x\" on pedidos using (auth.uid() = user_id); */\n")
        self.escreve(p, "src/a.ts", "// const r = supabase.from('p').select('id', { count: 'exact' });\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: NADA ACHADO", out)

    def test_tag_com_digito_nao_corta_o_corpo_da_funcao(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql", LIMPA + "create function f() returns void language plpgsql as $fn1$\nbegin\n"
                     "  create temp table tmp (x int);\n  drop table tmp;\nend;\n$fn1$;\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P04"), [], out)

    def test_sem_achado_nada_achado(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA)
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: NADA ACHADO", out)


class ChaveEstrangeira(Base):
    """AT-002: P03 na linha da chave; índice na mesma migration ou noutra; composto com a chave em 2º lugar acusa."""

    def test_chave_sem_indice_na_linha_do_references(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + "create table itens (\n  id bigint generated always as identity primary key,\n"
                     "  pedido_id bigint references pedidos (id)\n);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ P03 media %s001.sql:11" % MIG, out)

    def test_foreign_key_de_tabela_e_de_alter(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + "create table itens (id bigint primary key, pedido_id bigint,\n"
                     "  foreign key (pedido_id) references pedidos (id));\n"
                     "alter table itens add column dono uuid references auth.users (id);\n")
        rc, out = self.varre(p)
        self.assertEqual(len(self.avisos(out, "P03")), 2, out)

    def test_indice_noutra_migration_cobre(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + "create table itens (id bigint primary key, pedido_id bigint references pedidos (id));\n")
        self.escreve(p, MIG + "002.sql", "create index itens_pedido_idx on itens (pedido_id);\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P03"), [], out)

    def test_composto_com_a_chave_em_segundo_acusa(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + "create table itens (id bigint primary key, qtd int, pedido_id bigint references pedidos (id));\n"
                     "create index itens_q on itens (qtd, pedido_id);\n")
        rc, out = self.varre(p)
        self.assertEqual(len(self.avisos(out, "P03")), 1, out)


class RevisaoDoCodigo(Base):
    """Revisão do código, rodada 1: cada teste caiu no script de antes do conserto (R2, N2) ou fixa o que N1 duvidou."""

    def test_r2_comentario_no_fim_ou_no_meio_da_linha_sql_nao_acusa(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql", LIMPA + "select 1; -- alter role authenticated set statement_timeout = '30s';\n"
                     "select 2; /* perform http_get('x') */ select 3;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_n2_ilike_dentro_de_texto_nao_e_busca(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql", LIMPA + "comment on table pedidos is 'busque com ilike ''%x'' na tela';\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P15"), [], out)

    def test_n1_aspas_escapadas_com_parenteses_nao_quebram_a_politica(self):
        com_select = LIMPA.replace("using ((select auth.uid()) = user_id)", "using (status <> 'a(''b' and (select auth.uid()) = user_id)").replace(
            "  total numeric\n", "  total numeric,\n  status text\n")
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", com_select)
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.tearDown(); self.setUp()
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", com_select.replace("(select auth.uid()) = user_id", "auth.uid() = user_id"))
        rc, out = self.varre(p)
        self.assertTrue(self.avisos(out, "P01"), out)


class RevisaoDoCodigo2(Base):
    """Revisão do código, rodada 2 (EXTERNAL_REVIEW_20261118-135108): cada teste cai no script de antes do conserto."""

    SUPA = {"package.json": '{"dependencies": {"@supabase/supabase-js": "2"}}\n'}

    def test_r1_politica_em_tabela_entre_aspas_duplas_acusa(self):
        # o formato do `supabase db diff`: on "public"."pedidos" — antes, o \\b depois da aspa descartava a política
        for on in ('"public"."pedidos"', '"pedidos"'):
            with self.subTest(on=on):
                p = self.projeto()
                self.escreve(p, MIG + "002.sql", LIMPA.replace('on pedidos for select', "on %s for select" % on)
                             .replace("using ((select auth.uid()) = user_id)", "using (auth.uid() = user_id)"))
                rc, out = self.varre(p)
                self.assertEqual(rc, 1, out)
                self.assertTrue(self.avisos(out, "P01"), out)
                self.tearDown(); self.setUp()

    def test_r3_chave_primaria_por_indice_nao_acusa_p04(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql",
                     'create table "public"."todos" ("id" bigint not null, "titulo" text);\n'
                     'create unique index todos_pkey on public.todos using btree (id);\n'
                     'alter table "public"."todos" add constraint "todos_pkey" PRIMARY KEY using index "todos_pkey";\n')
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P04"), [], out)

    def test_r4_politica_corrigida_em_migration_seguinte_some(self):
        sem_select = LIMPA.replace("using ((select auth.uid()) = user_id)", "using (auth.uid() = user_id)")
        consertos = {
            "drop e create": 'drop policy "dono le" on pedidos;\n'
                             'create policy "dono le" on pedidos for select to authenticated using ((select auth.uid()) = user_id);\n',
            "alter": 'alter policy "dono le" on pedidos using ((select auth.uid()) = user_id);\n',
        }
        for caso, conserto in consertos.items():
            with self.subTest(caso=caso):
                p = self.projeto()
                self.escreve(p, MIG + "003.sql", sem_select)
                self.escreve(p, MIG + "004.sql", conserto)
                rc, out = self.varre(p)
                self.assertEqual(self.avisos(out, "P01"), [], out)
                self.tearDown(); self.setUp()

    def test_r5_limite_da_consulta_seguinte_nao_esconde_a_lista(self):
        p = self.projeto(self.SUPA)
        self.escreve(p, "src/lista.ts",
                     "const { data } = await supabase.from('pedidos').select('*')\n"
                     "const { data: c } = await supabase.from('clientes').select('*').eq('id', id).single()\n")
        rc, out = self.varre(p)
        achados = self.avisos(out, "P08")
        self.assertEqual(len(achados), 1, out)
        self.assertIn("src/lista.ts:1 —", achados[0])


class RevisaoDoCodigo3(Base):
    """Revisão do código, rodada 3 (EXTERNAL_REVIEW_20261118-141043): cada teste cai no script de antes do conserto."""

    def test_r4_apostrofo_em_comentario_dentro_da_funcao_nao_esconde_o_p13(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql",
                     LIMPA + "create function avisa() returns trigger language plpgsql as $$\nbegin\n"
                     "  -- get the user's profile\n"
                     "  perform http_get('https://exemplo.invalid/x');\n  return new;\nend;\n$$;\n")
        rc, out = self.varre(p)
        self.assertTrue(self.avisos(out, "P13"), out)
        self.tearDown(); self.setUp()
        p = self.projeto()
        self.escreve(p, MIG + "002.sql",
                     LIMPA + 'create policy "it\'s mine" on pedidos for select to authenticated using ((select auth.uid()) = user_id);\n'
                     "alter role authenticated set statement_timeout = '30s';\n")
        rc, out = self.varre(p)
        self.assertTrue(self.avisos(out, "P16"), out)

    def test_r5_o_mesmo_indice_declarado_de_novo_nao_e_repetido(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + "create index if not exists pedidos_total_idx on pedidos (total);\n")
        self.escreve(p, MIG + "005.sql", "create index if not exists pedidos_total_idx on pedidos (total);\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P07"), [], out)

    def test_n1_palavra_dentro_de_default_nao_vira_chave(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql",
                     "create table avisos (\n  id bigint primary key,\n  texto text default 'references x'\n);\n"
                     "create table rascunhos (\n  status text default 'primary key'\n);\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P03"), [], out)
        self.assertTrue([a for a in self.avisos(out, "P04") if "002.sql:5 —" in a], out)


class Legado(Base):
    """AT-003: o que a base já tinha vira uma linha; --tudo lista; índice apagado depois volta como novo."""

    def test_achado_antigo_vira_contagem_e_nada_novo(self):
        p = self.projeto({MIG + "001.sql": LIMPA + "create table log (msg text);\n"})
        self.escreve(p, MIG + "002.sql", "create index pedidos_total_idx on pedidos (total);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️ 1 achado(s) que já existiam — liste com --tudo", out)
        self.assertIn("RESULTADO: NADA NOVO", out)
        self.assertEqual(self.avisos(out, "P04"), [], out)

    def test_tudo_lista_os_antigos(self):
        p = self.projeto({MIG + "001.sql": LIMPA + "create table log (msg text);\n"})
        rc, out = self.varre(p, "--tudo")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ P04 media %s001.sql:9 — Tabela sem chave primária (já existia)" % MIG, out)

    def test_drop_index_novo_faz_a_chave_antiga_contar_como_nova(self):
        p = self.projeto({MIG + "001.sql": LIMPA})
        self.escreve(p, MIG + "002.sql", "drop index pedidos_user_id_idx;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ P03 media %s001.sql:3" % MIG, out)
        self.assertNotIn("(já existia)", out)

    def test_sem_base_tudo_e_novo(self):
        p = self.projeto({MIG + "001.sql": LIMPA + "create table log (msg text);\n"}, base=False)
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ base origin/main não existe: tudo conta como novo", out)


class LegadoDeslocado(Base):
    """AT-003 (contrato, proposta 3): uma linha antiga que só mudou de lugar continua "já existia"."""

    def test_linha_deslocada_continua_antiga(self):
        p = self.projeto({MIG + "001.sql": LIMPA + "create table antiga (msg text);\n"})
        self.escreve(p, MIG + "001.sql", "-- comentário novo no topo\n-- e mais um\n" + LIMPA + "create table antiga (msg text);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️ 1 achado(s) que já existiam — liste com --tudo", out)
        self.assertIn("RESULTADO: NADA NOVO", out)


class Dispensa(Base):
    """AT-004: com o id certo e motivo de 3+ caracteres, sai dos avisos; senão, fica e avisa."""

    def caso(self, comentario):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", LIMPA + comentario + "\ncreate table log (msg text);\n")
        return self.varre(p)

    def test_dispensa_com_motivo(self):
        rc, out = self.caso("-- sdd-desempenho-banco: aceito P04 — tabela de log que nunca passa de 100 linhas")
        self.assertEqual(rc, 0, out)
        self.assertIn("✔ aceito P04 %s001.sql:10 — tabela de log que nunca passa de 100 linhas" % MIG, out)

    def test_dispensa_sem_motivo_curta_ou_de_outro_item_nao_vale(self):
        for marca in ("-- sdd-desempenho-banco: aceito P04 —", "-- sdd-desempenho-banco: aceito P04 — ok",
                      "-- sdd-desempenho-banco: aceito P07 — outro item qualquer"):
            with self.subTest(marca=marca):
                rc, out = self.caso(marca)
                self.assertEqual(rc, 1, out)
                self.assertTrue(self.avisos(out, "P04"), out)
                self.assertIn("dispensa sem motivo (ou de outro item) não vale", out)
            self.tearDown(); self.setUp()


class DispensaNoFimDaLinha(Base):
    """AT-004 (contrato, proposta 4): a dispensa no fim de uma linha de código vale só para ela."""

    def test_nao_esconde_a_linha_de_baixo(self):
        p = self.projeto()
        self.escreve(p, MIG + "002.sql", "create table log (msg text); -- sdd-desempenho-banco: aceito P04 — log pequeno de teste\n"
                     "create table t2 (x int);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ P04 media %s002.sql:2" % MIG, out)
        self.assertEqual(out.count("✔ aceito P04"), 1, out)
        self.assertIn("✔ aceito P04 %s002.sql:1" % MIG, out)


class Uso(Base):
    """AT-005: entrada inválida sai 64 com causa e conserto; teto de 5 na tela; --saida com tudo."""

    def test_opcao_desconhecida(self):
        p = self.projeto()
        rc, out = self.varre(p, "--bloquear")
        self.assertEqual(rc, 64, out)
        self.assertIn("RESULTADO: ERRO DE USO", out)
        self.assertIn("→", out)

    def test_catalogo_fora_da_gramatica(self):
        p = self.projeto({MIG + "001.sql": LIMPA})
        ruim = self.tmp / "catalogo.md"
        txt = CATALOGO.read_text(encoding="utf-8").replace("- stack: supabase\n- fase: design\n", "- fase: design\n- stack: supabase\n", 1)
        ruim.write_text(txt, encoding="utf-8")
        rc, out = self.varre(p, catalogo=ruim)
        self.assertEqual(rc, 64, out)
        self.assertIn("catálogo ilegível", out)

    def test_fora_de_git(self):
        pasta = self.tmp / "solta"
        pasta.mkdir()
        rc, out = self.varre(pasta, "--raiz", str(pasta))
        self.assertEqual(rc, 64, out)
        self.assertIn("repositório git", out)

    def test_teto_de_cinco_e_saida_com_tudo(self):
        p = self.projeto()
        self.escreve(p, MIG + "001.sql", "".join("create table t%d (x int);\n" % k for k in range(8)))
        log = self.tmp / "ev" / "DESEMPENHO.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 1, out)
        self.assertEqual(len(self.avisos(out, "P04")), 5, out)
        self.assertIn("… e mais 3 aviso(s): lista inteira em %s" % log, out)
        self.assertEqual(len([ln for ln in log.read_text(encoding="utf-8").splitlines() if ln.startswith("⚠️ P04")]), 8)


class Teto(Base):
    """AT-005 e AT-001 (contrato, proposta 1): ordem por gravidade, "confira" uma vez por ficha, --saida com tudo."""

    def test_ordem_por_gravidade_e_confira_uma_vez(self):
        p = self.projeto()
        corpo = LIMPA + "".join("create index pedidos_dup%d on pedidos (user_id);\n" % k for k in range(7))
        corpo += "create table log (msg text);\ncreate function f() returns void language sql as $$ select http_get('x') $$;\n"
        self.escreve(p, MIG + "002.sql", corpo)
        log = self.tmp / "ev" / "D.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 1, out)
        avisos = [ln for ln in out.splitlines() if ln.startswith("⚠️ P")]
        self.assertTrue(avisos[0].startswith("⚠️ P13 alta"), out)
        self.assertTrue(avisos[1].startswith("⚠️ P04 media"), out)
        self.assertEqual(len(avisos), 5, out)
        self.assertEqual(out.count("confira à mão:"), 3, out)
        self.assertEqual(log.read_text(encoding="utf-8").count("confira à mão:"), 3)

    def test_saida_traz_aceitos_e_os_que_ja_existiam(self):
        p = self.projeto({MIG + "001.sql": LIMPA + "create table velha (msg text);\n"})
        self.escreve(p, MIG + "002.sql", "-- sdd-desempenho-banco: aceito P04 — tabela de rascunho que some\ncreate table rascunho (x int);\n"
                     "create table nova (x int);\n")
        log = self.tmp / "ev" / "D.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 1, out)
        txt = log.read_text(encoding="utf-8")
        self.assertIn("✔ aceito P04 %s002.sql:2" % MIG, txt)
        self.assertIn("(já existia)", txt)
        self.assertIn("⚠️ P04 media %s002.sql:3" % MIG, txt)


class Stack(Base):
    """AT-006: sem banco, SEM BANCO em 2 linhas; a stack é a da varredura de segurança."""

    def test_sem_banco(self):
        p = self.projeto({"src/a.py": "print('oi')\n", "sdd/fixtures/x.sql": "create table t (x int);\n"})
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: SEM BANCO", out)
        self.assertLessEqual(len(out.strip().splitlines()), 2, out)

    def test_sem_banco_grava_a_saida(self):   # avaliador, ciclo 2, c: a release aponta --saida
        p = self.projeto({"src/a.py": "print('oi')\n"})
        log = self.tmp / "ev" / "DESEMPENHO.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: SEM BANCO", log.read_text(encoding="utf-8"))

    def test_postgres_sem_supabase_so_as_fichas_de_todas(self):
        p = self.projeto()
        self.escreve(p, "db/migrations/001.sql", "create table log (msg text);\n"
                     "create policy p on log using (auth.uid() is not null);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertTrue(self.avisos(out, "P04"), out)
        self.assertEqual(self.avisos(out, "P01") + self.avisos(out, "P06"), [], out)
        self.assertIn("stack: nenhuma (detectada)", out)

    def test_slot_da_seguranca_vale_para_as_duas(self):
        p = self.projeto({MIG + "001.sql": LIMPA.replace("(select auth.uid())", "auth.uid()")}, base=False)
        self.escreve(p, "sdd/config.yaml", "security:\n  stack: \"nenhuma\"\n")
        rc, out = self.varre(p)
        self.assertEqual(self.avisos(out, "P01"), [], out)
        self.assertIn("stack: nenhuma (slot security.stack)", out)
        rc2, out2, err2 = self.roda([BASH, SEGURANCA, "--stack", "--catalogo",
                                     RAIZ / ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"], p)
        self.assertIn("stack: nenhuma (slot security.stack)", out2 + err2)

    def test_slot_invalido_repassa_a_causa_da_seguranca(self):
        p = self.projeto({MIG + "001.sql": LIMPA})
        self.escreve(p, "sdd/config.yaml", "security:\n  stack: \"mongo\"\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 64, out)
        self.assertIn("detecção de stack", out)
        self.assertIn("mongo", out)


if __name__ == "__main__":
    unittest.main()
