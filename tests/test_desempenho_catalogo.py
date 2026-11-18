"""O catálogo e as consultas da sdd-desempenho-banco (F27, AT-009 e AT-007).

O catálogo tem exatamente 17 fichas P01–P17 com os 11 campos na ordem; as consultas que a skill manda rodar pelo MCP
são todas só de leitura.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILL = RAIZ / ".agents/skills/sdd-desempenho-banco"
CATALOGO = SKILL / "references/CATALOGO_DESEMPENHO.md"
CONSULTAS = SKILL / "references/CONSULTAS_DIAGNOSTICO.md"
CAMPOS = ["stack", "fase", "gravidade", "gatilho", "padrao", "arquivos", "frase", "evitar", "at", "confira", "ref"]
ESCRITA = ("insert", "update", "delete", "merge", "alter", "create", "drop", "truncate", "grant", "revoke", "vacuum",
           "reindex", "cluster", "refresh", "pg_cancel_backend", "pg_terminate_backend", "copy", "call", "do", "lock")


def fichas():
    texto = CATALOGO.read_text(encoding="utf-8").split("## Itens", 1)[1]
    out = []
    for bloco in re.split(r"(?m)^### ", texto)[1:]:
        linhas = [ln for ln in bloco.splitlines() if ln.strip()]
        m = re.match(r"^(P\d\d) — (\S.*)$", linhas[0])
        campos = [re.match(r"^- ([a-z]+): (\S.*)$", ln) for ln in linhas[1:]]
        out.append((m.group(1) if m else linhas[0], [(c.group(1), c.group(2)) if c else (None, ln) for c, ln in zip(campos, linhas[1:])]))
    return out


def so_leitura(sql: str) -> list[str]:
    """As palavras de escrita fora de comentário e de texto entre aspas; `explain analyze` de escrita só vale dentro de
    begin … rollback. Devolve o que achou (vazio = só leitura)."""
    t = re.sub(r"--[^\n]*|/\*.*?\*/", " ", sql, flags=re.S)
    t = re.sub(r"'(?:[^']|'')*'", "''", t).lower()
    achou = []
    for cmd in [c.strip() for c in t.split(";") if c.strip()]:
        dentro = re.match(r"^(begin|commit|rollback)\b", cmd)
        if dentro:
            continue
        palavras = re.findall(r"[a-z_]+", cmd)
        if palavras[:1] == ["explain"]:
            if "analyze" in palavras and any(w in palavras for w in ("insert", "update", "delete", "merge")):
                if not (re.search(r"(?m)^\s*begin\s*;", sql.lower()) and re.search(r"(?m)rollback\s*;", sql.lower())):
                    achou.append("explain analyze de escrita fora de begin … rollback")
            continue
        if palavras[:1] not in (["select"], ["with"], ["show"]):
            achou.append("comando que não é leitura: %s" % (palavras[0] if palavras else "?"))
        achou += [w for w in palavras if w in ESCRITA and w not in ("do",)]
        if "analyze" in palavras:
            achou.append("analyze fora de explain")
    return achou


class Catalogo(unittest.TestCase):
    def test_17_fichas_com_os_11_campos_na_ordem(self):
        fs = fichas()
        self.assertEqual([f for f, _ in fs], ["P%02d" % k for k in range(1, 18)])
        for fid, campos in fs:
            with self.subTest(ficha=fid):
                self.assertEqual([c for c, _ in campos], CAMPOS)

    def test_dominios_e_sem_bloqueia_nem_agents(self):
        for fid, campos in fichas():
            c = dict(campos)
            with self.subTest(ficha=fid):
                self.assertIn(c["stack"], ("todas", "supabase"))
                self.assertIn(c["fase"], ("define", "design", "build", "release"))
                self.assertIn(c["gravidade"], ("alta", "media", "baixa"))
                self.assertTrue(set(g.strip() for g in c["gatilho"].split(",")) <= {"banco", "lista", "busca", "conexao", "lote"})
                self.assertTrue(c["padrao"] == "só à mão" or c["padrao"].startswith(("re:`", "regra:")), c["padrao"])
                self.assertTrue(c["ref"].startswith("https://"), c["ref"])
                self.assertRegex(c["at"], r"\b(When|While|If|Where)\b")
        self.assertNotIn("- bloqueia:", CATALOGO.read_text(encoding="utf-8"))
        self.assertNotIn("- agents:", CATALOGO.read_text(encoding="utf-8"))

    def test_fase_define_sao_as_tres_do_passo_do_define(self):
        self.assertEqual([f for f, cs in fichas() if dict(cs)["fase"] == "define"], ["P08", "P15", "P17"])

    def test_doze_com_padrao_e_cinco_so_a_mao(self):
        so_mao = [f for f, cs in fichas() if dict(cs)["padrao"] == "só à mão"]
        self.assertEqual(so_mao, ["P09", "P11", "P12", "P14", "P17"])

    def test_nada_do_repositorio_privado_nem_numero_longo(self):
        for arq in sorted(SKILL.rglob("*")):
            if arq.is_file():
                with self.subTest(arquivo=arq.name):
                    self.assertIsNone(re.search(r"\d{11,}", arq.read_text(encoding="utf-8")))


class Consultas(unittest.TestCase):
    def blocos(self):
        return re.findall(r"```sql\n(.*?)```", CONSULTAS.read_text(encoding="utf-8"), flags=re.S)

    def test_toda_consulta_e_so_leitura(self):
        blocos = self.blocos()
        self.assertGreaterEqual(len(blocos), 10)
        for k, sql in enumerate(blocos, 1):
            with self.subTest(bloco=k):
                self.assertEqual(so_leitura(sql), [], sql)

    def test_o_juiz_reprova_escrita(self):
        for ruim in ("delete from pedidos where id = 1;", "create index on t (x);", "vacuum pedidos;",
                     "select pg_terminate_backend(1);", "analyze pedidos;", "explain analyze update t set x = 1;",
                     "alter role anon set statement_timeout = '9s';"):
            with self.subTest(sql=ruim):
                self.assertTrue(so_leitura(ruim), ruim)
        self.assertEqual(so_leitura("begin;\nexplain (analyze) update t set x = 1;\nrollback;"), [])
        self.assertEqual(so_leitura("select 'delete' as texto; -- drop table x\nshow max_connections;"), [])

    def test_texto_de_consulta_sai_mascarado_no_sql(self):
        texto = CONSULTAS.read_text(encoding="utf-8")
        for bloco in self.blocos():
            if re.search(r"\bquery\b", bloco):
                with self.subTest(bloco=bloco[:40]):
                    self.assertIn("regexp_replace", bloco)
        self.assertNotIn("```sql\nbegin;", texto)

    # Revisão do código, rodada 2, R2: a máscara feita no SQL (consultas 3, 7 e 8, pelo MCP) falha fechada como a do
    # script. Cada caso vazava o nome antes do conserto (o mesmo desalinho que o avaliador achou no script, ciclos 2 e 3).
    # O teste roda as expressões do próprio arquivo, traduzidas para o re do Python (\m do Postgres vira \b(?=\w)); a
    # prova no Postgres 16 de verdade está em REVISAO-CODIGO-2-R2-POSTGRES.log.
    NOME = "NOMEX"
    CASOS = [
        r"select * from c /* it's hot */ where nome = 'NOMEX'",
        r"select * from c where dir = 'C:\' and nome = 'NOMEX'",
        r"""select "it's" from c where nome = 'NOMEX'""",
        r"""select * from "o'brien" where nome = 'NOMEX'""",
        r"select * from c /* a /* x */ it's */ where nome = 'NOMEX'",
        r"select * from c /* a /* x */ NOMEX */ where id = 1",
        r"select * from c where nome = 'NOMEX",
        r"select * from c where nome = E'it\'s NOMEX'",
        r"select * from c where v = $q$NOMEX$q$",
        r"select * from c where a = 1e10 and b = 0x1F and c = 1_000 and e = 'NOMEX'",
        r"select * from c where nome = 'it''s' and x = 'NOMEX'",
        r"select * from c where nome = 'NOMEX' -- it's",
        r"""select * from "x" where n = 'a"b' and m = 'NOMEX'""",
    ]
    GUARDA = re.compile(r"case when \w+\.cru ~ '((?:[^']|'')*)'\n\s+or regexp_replace\(\w+\.m, '((?:[^']|'')*)', '', 'g'\) ~ ''''")
    MASCARA = re.compile(r"regexp_replace\(regexp_replace\([\w.]+, '((?:[^']|'')*)', '''\?''', 'g'\), '((?:[^']|'')*)', '\?', 'g'\) as m\)")

    @staticmethod
    def regex_pg(texto_sql: str):
        """Um texto entre aspas do SQL ('' vira ') como regex do Python."""
        return re.compile(texto_sql.replace("''", "'").replace(r"\m", r"\b(?=\w)"))

    def test_r2_mascara_do_sql_falha_fechada(self):
        texto = CONSULTAS.read_text(encoding="utf-8")
        guardas, mascaras = self.GUARDA.findall(texto), self.MASCARA.findall(texto)
        self.assertEqual(len(guardas), 4, "consultas 3, 7 e 8 (duas colunas na 8) com a guarda")
        self.assertEqual(len(mascaras), 4)
        self.assertEqual(len(set(guardas)), 1, "a mesma guarda nas 4 colunas")
        self.assertEqual(len(set(mascaras)), 1)
        guarda, sobra = (self.regex_pg(x) for x in guardas[0])
        literal, numero = (self.regex_pg(x) for x in mascaras[0])

        def sai(q: str) -> str:
            m = numero.sub("?", literal.sub("'?'", q))
            return "[omitido]" if guarda.search(q) or "'" in sobra.sub("", m) else m[:200]

        for q in self.CASOS:
            with self.subTest(q=q):
                self.assertNotIn(self.NOME, sai(q))
        # a consulta comum (PostgREST põe aspas duplas em tudo) continua legível
        self.assertEqual(sai("""select "public"."p"."id" from "public"."p" where n = 'NOMEX' and id = 42"""),
                         """select "public"."p"."id" from "public"."p" where n = '?' and id = ?""")


if __name__ == "__main__":
    unittest.main()
