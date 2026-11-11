"""Contrato de sdd/bin/seguranca-varredura.sh (F18/F20, AT-001 a AT-006).

Cada caso é um repositório git temporário com a base em origin/main (uma ref local) e o que a publicação
acrescenta por cima. As chaves falsas são montadas em tempo de execução: o pacote não carrega texto com forma
de segredo. Exit: 0 nada achado · 1 avisos · 2 bloqueado · 64 uso.
"""
from __future__ import annotations

import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/seguranca-varredura.sh"
CATALOGO = RAIZ / ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"

# Chaves falsas, nos 7 formatos que S11 reconhece (montadas por partes).
SEGREDOS = {
    "chave privada": "-----BEGIN " + "RSA PRIVATE KEY-----",
    "sk-": "s" + "k-" + "a1B2c3D4" * 5,
    "sk_live_": "s" + "k_live_" + "Z9y8X7w6" * 2,
    "ghp_": "gh" + "p_" + "A1b2C3d4E5" * 3 + "xyz",
    "github_pat_": "github" + "_pat_" + "Q" * 34,
    "AKIA": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
    "service role": "SUPABASE_SERVICE_ROLE_KEY=" + "ey" + "JhbGciOiJIUzI1NiJ9.abc",
}


class Base(Sandbox):
    def projeto(self, arquivos: dict | None = None, base: bool = True) -> "Path":
        p = self.repo("app")
        self.escreve(p, "README.md", "# app\n")
        for rel, txt in (arquivos or {}).items():
            self.escreve(p, rel, txt)
        self.commit(p, "base")
        if base:
            self.git(p, "update-ref", "refs/remotes/origin/main", "HEAD")
        return p

    def varre(self, p, *extra: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, SCRIPT, "--catalogo", CATALOGO, *extra], p)
        return rc, out + err

    def stack(self, p, valor: str) -> None:
        self.escreve(p, "sdd/config.yaml", "project:\n  default_branch: main\nsecurity:\n  stack: \"%s\"\n" % valor)


class Segredo(Base):
    def test_segredo_novo_bloqueia_com_arquivo_e_linha(self):
        for nome, valor in SEGREDOS.items():
            with self.subTest(formato=nome):
                p = self.projeto()
                self.escreve(p, "src/cliente.ts", "const a = 1;\nconst k = \"%s\";\n" % valor)
                rc, out = self.varre(p)
                self.assertEqual(rc, 2, out)
                self.assertIn("🛑 S11 alta src/cliente.ts:2", out)
                self.assertIn("confira à mão:", out)
                self.assertIn("RESULTADO: BLOQUEADO", out)
                self.tearDown(); self.setUp()

    def test_valor_do_segredo_nunca_aparece_na_saida(self):
        p = self.projeto()
        valor = SEGREDOS["sk_live_"]
        self.escreve(p, "src/pagar.js", "stripe(\"%s\")\n" % valor)
        log = self.tmp / "ev" / "SEGURANCA.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 2, out)
        self.assertNotIn(valor, out)
        self.assertNotIn(valor, log.read_text(encoding="utf-8"))
        self.assertIn("🛑 S11", log.read_text(encoding="utf-8"))

    def test_leitura_pelo_nome_nao_e_segredo(self):
        p = self.projeto()
        self.escreve(p, "src/a.ts", "const k = process.env.OPENAI_API_KEY;\nconst s = Deno.env.get(\"SUPABASE_SERVICE_ROLE_KEY\");\n")
        self.escreve(p, "src/b.py", "import os\nk = os.environ[\"STRIPE_KEY\"]\nx = \"sk-curta\"\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: NADA ACHADO", out)

    def test_segredo_que_ja_existia_vira_aviso(self):
        p = self.projeto({"src/velho.ts": "const k = \"%s\";\n" % SEGREDOS["sk-"]})
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ S11 alta src/velho.ts:1", out)
        self.assertIn("(já existia)", out)
        self.assertNotIn("🛑", out)

    def test_sem_base_tudo_conta_como_novo(self):
        p = self.projeto({"src/velho.ts": "const k = \"%s\";\n" % SEGREDOS["ghp_"]}, base=False)
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("⚠️ base origin/main não existe: tudo conta como novo", out)

    def test_base_por_opcao_e_branch_padrao_do_config(self):
        p = self.projeto({"src/velho.ts": "const k = \"%s\";\n" % SEGREDOS["AKIA"]}, base=False)
        rc, out = self.varre(p, "--base", "HEAD")
        self.assertEqual(rc, 1, out)
        self.assertIn("base: HEAD", out)
        self.git(p, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        self.escreve(p, "sdd/config.yaml", "project:\n  default_branch: trunk\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("base: origin/trunk", out)

    def test_arquivo_novo_nao_rastreado_conta_inteiro(self):
        p = self.projeto()
        self.escreve(p, "config/chaves.txt", "x\n%s\n" % SEGREDOS["chave privada"])
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("config/chaves.txt:2", out)

    def test_linha_alterada_num_arquivo_antigo_conta_como_nova(self):
        p = self.projeto({"src/a.ts": "um\ndois\ntres\n"})
        self.escreve(p, "src/a.ts", "um\nconst k = \"%s\";\ntres\n" % SEGREDOS["github_pat_"])
        self.commit(p, "na branch")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("src/a.ts:2", out)


class RevisaoDoDesign(Base):
    """Rodada 1 da revisão do DESIGN (R1, R2, R4, R8, R9, R10): cada teste caiu no script de antes do conserto."""

    def test_r1_identificador_kebab_com_sk_nao_e_segredo(self):
        p = self.projeto()
        self.escreve(p, "src/a.css", ".sk-fading-circle-spinner-container-large { }\n.task-manager-dashboard-v2-wide { }\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_r2_o_mais_grave_vem_antes_mesmo_que_ja_existisse(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}\n",
                          "src/velho.ts": "const k = \"%s\";\n" % SEGREDOS["AKIA"]})
        self.escreve(p, "sdd/config.yaml", "security:\n  max_warnings: 2\n")
        self.escreve(p, "src/novo.ts", "db.select('*');\nstorage.getPublicUrl(a);\nstorage.getPublicUrl(b);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        mostrados = [ln for ln in out.splitlines() if ln.startswith("⚠️ S")]
        self.assertEqual(len(mostrados), 2, out)
        self.assertTrue(mostrados[0].startswith("⚠️ S11 alta src/velho.ts:1"), out)

    def test_r4_motivo_da_dispensa_nunca_leva_o_segredo(self):
        valor = SEGREDOS["sk_live_"]
        for linha in ("/* sdd-seguranca: aceito S11 — chave de teste */ const k = \"%s\";" % valor,
                      "<!-- sdd-seguranca: aceito S11 — chave de teste --> <meta content=\"%s\">" % valor,
                      "k = \"%s\"  # sdd-seguranca: aceito S11 — chave de teste %s" % (valor, valor)):
            with self.subTest(linha=linha[:30]):
                p = self.projeto()
                self.escreve(p, "src/x.html", linha + "\n")
                log = self.tmp / "s.log"
                rc, out = self.varre(p, "--saida", str(log))
                self.assertNotIn(valor, out)
                self.assertNotIn(valor, log.read_text(encoding="utf-8"))
                self.assertIn("✔ aceito S11 src/x.html:1 — chave de teste", out)
                self.tearDown(); self.setUp()

    def test_r8_nome_com_acento_e_diff_sem_prefixo(self):
        p = self.projeto({"src/configuração.js": "um\n"})
        self.git(p, "config", "diff.noprefix", "true")
        self.escreve(p, "src/configuração.js", "um\nconst k = \"%s\";\n" % SEGREDOS["ghp_"])
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S11 alta src/configuração.js:2", out)

    def test_r9_palavras_chave_em_maiusculas(self):
        p = self.projeto({"supabase/config.toml": ""})
        self.escreve(p, "supabase/migrations/0002.sql", "CREATE TABLE PUBLIC.Pedidos (id int);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.escreve(p, "supabase/migrations/0003.sql", "ALTER TABLE pedidos ENABLE ROW LEVEL SECURITY;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_r10_revoke_so_de_public_nao_basta(self):
        p = self.projeto({"supabase/config.toml": ""})
        self.escreve(p, "supabase/migrations/0002.sql",
                     "create function f() returns int language sql security definer as $$ select 1 $$;\n"
                     "revoke execute on function f() from public;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ S03 alta supabase/migrations/0002.sql:1", out)


class RevisaoDoCodigo(Base):
    """Rodada 2 da revisão (código): cada teste caiu no script de antes do conserto."""

    def test_r1_rls_comentado_nao_conta(self):
        for comentario in ("-- alter table clientes enable row level security; -- TODO",
                           "/* alter table clientes\n   enable row level security; */"):
            with self.subTest(comentario=comentario[:12]):
                p = self.projeto({"supabase/config.toml": ""})
                self.escreve(p, "supabase/migrations/0002.sql", "create table clientes (id uuid primary key);\n" + comentario + "\n")
                rc, out = self.varre(p)
                self.assertEqual(rc, 2, out)
                self.assertIn("🛑 S01 alta supabase/migrations/0002.sql:1", out)
                self.tearDown(); self.setUp()

    def test_r2_nome_com_espaco_commitado_na_branch(self):
        p = self.projeto({"src/minha config.js": "um\n"})
        self.escreve(p, "src/minha config.js", "um\nconst k = \"%s\";\n" % SEGREDOS["sk_live_"])
        self.commit(p, "na branch")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S11 alta src/minha config.js:2", out)

    def test_r3_raiz_numa_subpasta(self):
        p = self.projeto({"app/src/k.ts": "um\n"})
        self.escreve(p, "app/src/k.ts", "um\nconst k = \"%s\";\n" % SEGREDOS["ghp_"])
        self.commit(p, "na branch")
        rc, out = self.varre(p, "--raiz", str(p / "app"))
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S11 alta src/k.ts:2", out)

    def test_r4_linha_que_comeca_com_mais_mais_nao_e_cabecalho(self):
        p = self.projeto({"src/a.txt": "".join("linha %d\n" % k for k in range(30))})
        linhas = ["linha %d" % k for k in range(30)]
        linhas.insert(2, "++ nota")
        linhas.insert(25, "k = \"%s\"" % SEGREDOS["ghp_"])
        self.escreve(p, "src/a.txt", "\n".join(linhas) + "\n")
        self.commit(p, "na branch")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S11 alta src/a.txt:26", out)

    def test_r5_marca_de_outro_item_na_linha_nao_esconde_a_de_cima(self):
        p = self.projeto({"package.json": "{}\n"})
        self.escreve(p, "src/c.js", "// sdd-seguranca: aceito S16 — expressão fixa da planilha\n"
                     "el.innerHTML = eval(x) // sdd-seguranca: aceito S12 — html sanitizado antes\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("✔ aceito S16 src/c.js:2 — expressão fixa da planilha", out)
        self.assertIn("✔ aceito S12 src/c.js:2 — html sanitizado antes", out)

    def test_n1_tabela_em_bloco_comentado_nao_conta(self):
        p = self.projeto({"supabase/config.toml": ""})
        self.escreve(p, "supabase/migrations/0002.sql", "/*\ncreate table rascunho (id int);\n*/\nselect 1;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_n2_revoke_de_uma_funcao_nao_cobre_a_outra(self):
        p = self.projeto({"supabase/config.toml": ""})
        self.escreve(p, "supabase/migrations/0002.sql",
                     "create function a() returns int language sql security definer as $$ select 1 $$;\n"
                     "revoke execute on function a() from anon;\n"
                     "create or replace function public.b() returns int language sql\n  security definer as $$ select 2 $$;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ S03 alta supabase/migrations/0002.sql:4", out)
        self.assertNotIn("0002.sql:1", out)


class Rls(Base):
    def supa(self, **kw) -> "Path":
        return self.projeto({"supabase/config.toml": "[api]\n", **kw})

    def test_tabela_nova_sem_rls_bloqueia(self):
        p = self.supa()
        self.escreve(p, "supabase/migrations/0002_clientes.sql",
                     "-- clientes\ncreate table if not exists public.\"Clientes\" (\n  id uuid primary key\n);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S01 alta supabase/migrations/0002_clientes.sql:2", out)

    def test_rls_em_outra_migracao_libera(self):
        p = self.supa(**{"supabase/migrations/0001.sql": "create table guias (id int);\n"})
        self.escreve(p, "supabase/migrations/0002.sql", "alter table only public.guias\n  enable row level security;\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_tabela_antiga_sem_rls_vira_aviso(self):
        p = self.supa(**{"supabase/migrations/0001.sql": "create table guias (id int);\n"})
        rc, out = self.varre(p)
        self.assertEqual(rc, 1, out)
        self.assertIn("⚠️ S01 alta supabase/migrations/0001.sql:1 — Tabela sem RLS (já existia)", out)

    def test_outro_schema_e_comentario_nao_contam(self):
        p = self.supa()
        self.escreve(p, "supabase/migrations/0002.sql",
                     "create table private.segredos (id int);\n-- create table rascunho (id int);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_sem_supabase_s01_nao_avalia(self):
        p = self.projeto({"package.json": "{\"name\": \"app\"}\n"})
        self.escreve(p, "db/migrations/0001.sql", "create table clientes (id int);\n")
        self.escreve(p, "sdd/config.yaml", "layers:\n  sql: \"db/migrations/**\"\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("S01", out)

    def test_camada_sql_do_config_vale_com_supabase(self):
        p = self.supa()
        self.escreve(p, "db/0001.sql", "create table clientes (id int);\n")
        self.escreve(p, "sdd/config.yaml", "layers:\n  sql: \"db/*.sql\"\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("🛑 S01 alta db/0001.sql:1", out)


class Avisos(Base):
    CASOS = {
        "S02": ("src/lista.ts", "const r = await db.from('c').select('*');\n"),
        "S03": ("supabase/migrations/0002.sql", "create function f() returns int\nlanguage sql security definer as $$ select 1 $$;\n"),
        "S04": ("src/arquivo.ts", "const u = storage.from('nf').getPublicUrl(caminho);\n"),
        "S12": ("src/Comentario.tsx", "<div dangerouslySetInnerHTML={{ __html: texto }} />\n"),
        "S14": ("supabase/functions/api/index.ts", "headers: { 'Access-Control-Allow-Origin': '*' }\n"),
        "S15": ("next.config.js", "module.exports = { productionBrowserSourceMaps: true }\n"),
        "S16": ("src/calc.js", "const r = eval(formula);\n"),
    }
    PARES = {
        "S02": ("src/lista.ts", "const r = await db.from('c').select('id, nome');\n"),
        "S03": ("supabase/migrations/0002.sql",
                "create function f() returns int\nlanguage sql security definer as $$ select 1 $$;\n"
                "revoke execute on function f() from anon, public;\n"),
        "S04": ("src/arquivo.ts", "const u = await storage.from('nf').createSignedUrl(caminho, 60);\n"),
        "S12": ("src/Comentario.tsx", "el.textContent = texto;\nif (el.innerHTML === '') {}\n"),
        "S14": ("supabase/functions/api/index.ts", "headers: { 'Access-Control-Allow-Origin': 'https://app.example.com' }\n"),
        "S15": ("next.config.js", "module.exports = { productionBrowserSourceMaps: false }\n"),
        "S16": ("src/calc.py", "model.eval()\nretrieval(x)\ndados = json.loads(texto)\n# eval(formula) no comentário\n"),
    }

    def test_os_sete_padroes_avisam_com_a_prova(self):
        for item, (rel, txt) in self.CASOS.items():
            with self.subTest(item=item):
                p = self.projeto({"supabase/config.toml": "[api]\n", "package.json": "{}\n"})
                self.escreve(p, rel, txt)
                rc, out = self.varre(p)
                self.assertEqual(rc, 1, out)
                self.assertIn("⚠️ %s " % item, out)
                self.assertIn(rel + ":", out)
                self.assertIn("confira à mão:", out)
                self.assertIn("RESULTADO: AVISOS", out)
                self.tearDown(); self.setUp()

    def test_os_pares_nao_avisam(self):
        for item, (rel, txt) in self.PARES.items():
            with self.subTest(item=item):
                p = self.projeto({"supabase/config.toml": "[api]\n", "package.json": "{}\n"})
                self.escreve(p, rel, txt)
                rc, out = self.varre(p)
                self.assertEqual(rc, 0, out)
                self.tearDown(); self.setUp()

    def test_variantes_de_html_e_cors(self):
        casos = {
            "src/a.vue": "<p v-html=\"corpo\"></p>\n",
            "src/b.js": "el.innerHTML = corpo;\n",
            "vercel.json": "{\"headers\": [{\"key\": \"Access-Control-Allow-Origin\", \"value\": \"*\"}]}\n",
            "api/c.js": "app.use(cors({ origin: '*' }))\n",
            "src/d.js": "const f = new Function('return 1');\n",
            "src/e.js": "fetch('https://x.example.com', { headers: { 'Access-Control-Allow-Origin': '*' } })\n",
        }
        for rel, txt in casos.items():
            with self.subTest(arquivo=rel):
                p = self.projeto({"package.json": "{}\n"})
                self.escreve(p, rel, txt)
                rc, out = self.varre(p)
                self.assertEqual(rc, 1, out)
                self.assertIn(rel + ":1", out)
                self.tearDown(); self.setUp()


class Teto(Base):
    def oito(self, p) -> None:
        linhas = ["const r%d = eval(x%d);" % (k, k) for k in range(4)]
        linhas += ["db.from('t').select('*');", "storage.getPublicUrl(a);", "storage.getPublicUrl(b);", "db.select(\"*\")"]
        self.escreve(p, "src/muitos.ts", "\n".join(linhas) + "\n")

    def test_oito_avisos_mostram_cinco_e_o_resto_vai_para_o_arquivo(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}\n"})
        self.oito(p)
        log = self.tmp / "SEG.log"
        rc, out = self.varre(p, "--saida", str(log))
        self.assertEqual(rc, 1, out)
        self.assertEqual(out.count("⚠️ S"), 5, out)
        self.assertIn("… e mais 3 aviso(s): lista inteira em %s" % log, out)
        self.assertEqual(log.read_text(encoding="utf-8").count("⚠️ S"), 8)
        # o mais grave primeiro: os 4 eval (alta) antes dos médios
        self.assertLess(out.index("⚠️ S16"), out.index("⚠️ S02"))

    def test_sem_saida_diz_como_ver_todos(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}\n"})
        self.oito(p)
        rc, out = self.varre(p)
        self.assertIn("… e mais 3 aviso(s): rode com --saida <arquivo> para ver todos", out)

    def test_slot_muda_o_teto_e_bloqueio_nao_entra_na_conta(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}\n"})
        self.oito(p)
        self.escreve(p, "src/k.ts", "\n".join("k%d = \"%s%d\"" % (n, SEGREDOS["sk-"], n) for n in range(3)) + "\n")
        self.escreve(p, "sdd/config.yaml", "security:\n  max_warnings: 2\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 2, out)
        self.assertEqual(out.count("🛑 S11"), 3, out)
        self.assertEqual(out.count("⚠️ S"), 2, out)
        self.assertIn("… e mais 6 aviso(s)", out)

    def test_teto_invalido_avisa_e_usa_cinco(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}\n"})
        self.oito(p)
        self.escreve(p, "sdd/config.yaml", "security:\n  max_warnings: muitos\n")
        rc, out = self.varre(p)
        self.assertIn("security.max_warnings inválido", out)
        self.assertEqual(out.count("⚠️ S"), 5, out)


class Dispensa(Base):
    def test_dispensa_com_motivo_tira_o_achado(self):
        p = self.projeto({"package.json": "{}\n"})
        self.escreve(p, "src/c.js", "// sdd-seguranca: aceito S16 — expressão fixa da planilha de teste\nconst r = eval('1+1');\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("✔ aceito S16 src/c.js:2 — expressão fixa da planilha de teste", out)

    def test_dispensa_tira_o_bloqueio_e_vale_na_propria_linha(self):
        p = self.projeto()
        self.escreve(p, "tests/caso.py", "k = \"%s\"  # sdd-seguranca: aceito S11 - chave falsa de teste\n" % SEGREDOS["sk-"])
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("✔ aceito S11 tests/caso.py:1", out)

    def test_dispensa_sem_motivo_ou_de_outro_item_nao_vale(self):
        for marca in ("// sdd-seguranca: aceito S16 —", "// sdd-seguranca: aceito S16 — ok",
                      "// sdd-seguranca: aceito S12 — motivo de outro item"):
            with self.subTest(marca=marca):
                p = self.projeto({"package.json": "{}\n"})
                self.escreve(p, "src/c.js", marca + "\nconst r = eval(x);\n")
                rc, out = self.varre(p)
                self.assertEqual(rc, 1, out)
                self.assertIn("⚠️ dispensa sem motivo (ou de outro item) não vale: src/c.js:2 (S16)", out)
                self.assertIn("⚠️ S16 alta src/c.js:2", out)
                self.tearDown(); self.setUp()


class Stack(Base):
    def test_deteccao(self):
        casos = (
            ({"supabase/config.toml": ""}, "stack: supabase (detectada)"),
            ({"package.json": "{\"dependencies\": {\"@supabase/supabase-js\": \"2\"}}"}, "stack: supabase, web (detectada)"),
            ({"vercel.json": "{}"}, "stack: vercel (detectada)"),
            ({"package.json": "{\"devDependencies\": {\"vercel\": \"1\"}}"}, "stack: vercel, web (detectada)"),
            ({"public/index.html": "<html></html>"}, "stack: web (detectada)"),
            ({}, "stack: nenhuma (detectada)"),
        )
        for arquivos, esperado in casos:
            with self.subTest(esperado=esperado, arquivos=list(arquivos)):
                p = self.projeto(arquivos)
                rc, out = self.varre(p, "--stack")
                self.assertEqual(rc, 0, out)
                self.assertIn(esperado, out)
                self.tearDown(); self.setUp()

    def test_slot_passa_por_cima_e_nenhuma(self):
        p = self.projeto({"supabase/config.toml": ""})
        self.stack(p, "web, vercel")
        rc, out = self.varre(p, "--stack")
        self.assertIn("stack: vercel, web (slot security.stack)", out)
        self.stack(p, "nenhuma")
        rc, out = self.varre(p, "--stack")
        self.assertIn("stack: nenhuma (slot security.stack)", out)

    def test_slot_com_valor_desconhecido_e_uso(self):
        p = self.projeto()
        self.stack(p, "supabase, firebase")
        rc, out = self.varre(p, "--stack")
        self.assertEqual(rc, 64, out)
        self.assertIn("firebase", out)

    def test_item_de_supabase_nao_dispara_sem_supabase(self):
        p = self.projeto({"package.json": "{}\n"})
        self.escreve(p, "src/l.ts", "db.select('*');\nstorage.getPublicUrl(a);\n")
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        rc, out = self.varre(p, "--regras")
        self.assertNotIn("S01 ", out)
        self.assertIn("S12 ", out)

    def test_checklist_comeca_pelos_de_maior_risco_e_ignora_a_bancada(self):
        p = self.projeto({"supabase/config.toml": "", "vercel.json": "{}", "package.json": "{}"})
        rc, out = self.varre(p, "--checklist")
        self.assertEqual(rc, 0, out)
        ids = [ln.split("[", 1)[1][:3] for ln in out.splitlines() if ln[:1].isdigit()]
        self.assertEqual(len(ids), 20, out)
        self.assertEqual(sorted(ids[:5]), ["S01", "S07", "S08", "S11", "S13"])
        self.assertNotIn("S21", ids)
        self.assertNotIn("S22", ids)

    def test_agents_traz_as_frases_da_stack_e_o_ponteiro(self):
        p = self.projeto({"supabase/config.toml": "", "package.json": "{}"})
        rc, out = self.varre(p, "--agents")
        self.assertEqual(rc, 0, out)
        linhas = out.strip().splitlines()
        self.assertEqual(len(linhas), 6, out)
        self.assertTrue(all(ln.startswith("- ") for ln in linhas))
        self.assertIn("RLS", out)
        self.assertIn("seguranca-varredura.sh --regras", linhas[-1])
        p2 = self.repo("cli")
        rc, out = self.varre(p2, "--agents")
        self.assertEqual(len(out.strip().splitlines()), 2, out)
        self.assertNotIn("RLS", out)


class Uso(Base):
    def test_arquivos_do_sdd_e_dos_agentes_nao_sao_varridos(self):
        p = self.projeto()
        for rel in (".agents/skills/x/SKILL.md", "sdd/features/DEFINE_X.md", "AGENTS.md", ".claude/skills/y.md",
                    "node_modules/z/index.js"):
            self.escreve(p, rel, "k = \"%s\"\n" % SEGREDOS["sk-"])
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)

    def test_binario_e_pulado(self):
        p = self.projeto()
        (p / "logo.png").write_bytes(b"\x89PNG\x00\x00" + SEGREDOS["sk-"].encode())
        rc, out = self.varre(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("1 pulado(s)", out)

    def test_fora_de_git_e_64(self):
        solta = self.tmp / "solta"
        solta.mkdir()
        rc, out = self.varre(solta)
        self.assertEqual(rc, 64, out)
        self.assertIn("repositório git", out)

    def test_opcao_desconhecida_e_modo_com_base_sao_uso(self):
        p = self.projeto()
        for args in (("--rapido",), ("--regras", "--base", "HEAD"), ("--stack", "--agents")):
            with self.subTest(args=args):
                rc, out = self.varre(p, *args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)

    def test_catalogo_ilegivel_diz_arquivo_e_linha(self):
        p = self.projeto()
        texto = CATALOGO.read_text(encoding="utf-8")
        trocado = texto.replace("- fase: define\n- gravidade: alta", "- gravidade: alta\n- fase: define", 1)
        ruim = self.escreve(p, "cat.md", trocado)
        rc, out, err = self.roda([BASH, SCRIPT, "--catalogo", ruim, "--stack"], p)
        self.assertEqual(rc, 64, out + err)
        self.assertRegex(err, r"catálogo ilegível: .*cat\.md:\d+ — campo `gravidade` fora da ordem em S01")

    def test_catalogo_ausente_e_64_e_o_padrao_e_o_da_skill_instalada(self):
        p = self.projeto()
        rc, out, err = self.roda([BASH, SCRIPT, "--stack"], p)
        self.assertEqual(rc, 64, out + err)
        self.assertIn("catálogo ausente", err)
        self.copia(".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md", p)
        rc, out, err = self.roda([BASH, SCRIPT, "--stack"], p)
        self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    unittest.main()
