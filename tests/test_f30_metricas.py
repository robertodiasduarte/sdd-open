"""F30 S3 — métricas no diff, só aviso (DEFINE_F30_QUALIDADE_CODIGO, AT-017 a AT-021).

AT-017: função de complexidade 15 e bloco duplicado no diff ⇒ a seção `## Qualidade (avisos)` com os dois, exit 0, árvore
idêntica. AT-018: ferramenta ausente, quebrada ou com saída ilegível ⇒ "não medido" com a causa, exit 0, nunca "0 achados".
AT-019: só o que tem linha no diff. AT-020: limites em `qualidade.*`. AT-021: o `report-lint.py` exige a seção quando o
config tem o mapa `qualidade:`.

As ferramentas falsas devolvem a saída real do lizard 1.26.1 e do jscpd 5.4.3 (o CI não as instala); com as reais no PATH,
a mesma fixture roda contra elas.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import unittest

from apoio import BASH, RAIZ, SEM_SYMLINK, Sandbox, path_restrito

SCRIPT = RAIZ / "sdd" / "bin" / "metricas-diff.sh"
LINT = RAIZ / "sdd" / "bin" / "report-lint.py"
FERRAMENTAS = ("bash", "sh", "git", "sed", "mktemp", "rm", "cat", "head", "tail", "tr", "grep", "dirname", "basename",
               "xargs", "mkdir", "find", "env", "uname")
GRANDE = ("def grande(a, b, c, d, e, f):\n    r = 0\n"
          + "".join("    if a == %d:\n        r += %d\n" % (i, i) for i in range(14)) + "    return r\n")
CSV_GRANDE = '31,15,132,6,31,"grande@1-31@./src/nova.py","./src/nova.py","grande","grande( a , b , c , d , e , f )",1,31\n'
NOTAS = ("def soma_notas(notas):\n    total = 0\n    quantidade = 0\n    for nota in notas:\n"
         "        if nota is None:\n            continue\n        total += nota['valor'] * nota['peso']\n"
         "        quantidade += nota['peso']\n    if quantidade == 0:\n        return 0\n"
         "    return round(total / quantidade, 2)\n")
CSV_NOTAS = '11,4,55,1,11,"soma_notas@1-11@./src/copia.py","./src/copia.py","soma_notas","soma_notas( notas )",1,11\n'
PROIBIDOS = ("0 achados", "zero achados", "nenhum aviso")


def par(a, b, linhas=11, tokens=58, ini=1, fim=11):
    return {"format": "python", "lines": linhas, "tokens": tokens, "fragment": "…", "kind": "exact",
            "firstFile": {"name": a, "start": ini, "end": fim}, "secondFile": {"name": b, "start": ini, "end": fim}}


def jscpd_json(*pares, sources=3) -> str:
    return json.dumps({"duplicates": list(pares), "statistics": {"total": {"sources": sources, "clones": len(pares)}}})


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.git(self.r, "checkout", "-q", "-b", "main")
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha"))
        self.escreve(self.r, "src/notas.py", NOTAS)
        self.commit(self.r)
        self.git(self.r, "checkout", "-q", "-b", "frente")
        self.tmpdir = self.tmp / "tmpdir"
        self.tmpdir.mkdir()
        self.falsas = self.tmp / "falsas"
        self.falsas.mkdir()
        self.chamadas = self.tmp / "chamadas.txt"
        self.env = dict(self.env, TMPDIR=str(self.tmpdir))

    def frente(self):
        """O diff do AT-017: uma função de complexidade 15 e uma cópia de soma_notas."""
        self.escreve(self.r, "src/nova.py", GRANDE)
        self.escreve(self.r, "src/copia.py", NOTAS)
        self.commit(self.r)

    def falsa(self, nome, corpo):
        p = self.falsas / nome
        p.write_text("#!/bin/sh\n" + corpo, encoding="utf-8")
        p.chmod(0o755)

    def lizard(self, csv=CSV_GRANDE + CSV_NOTAS, rc=0, erro=""):
        (self.tmp / "lizard.csv").write_text(csv, encoding="utf-8")
        self.falsa("lizard", 'printf "%%s\\n" "lizard $*" >> "%s"\n[ "$1" = --version ] && { echo 1.26.1; exit 0; }\n'
                   'cat "%s"\necho "%s" >&2\nexit %d\n' % (self.p(self.chamadas), self.p(self.tmp / "lizard.csv"), erro, rc))

    def jscpd(self, relatorio=None, rc=0, erro="", no_diff=None):
        if relatorio is None:
            relatorio = jscpd_json(par("src/copia.py", "src/notas.py"))
        (self.tmp / "jscpd.json").write_text(relatorio, encoding="utf-8")
        (self.tmp / "diff.json").write_text(no_diff if no_diff is not None else re.sub(r'"duplicates": \[.*\], "stat', '"duplicates": [], "stat', relatorio), encoding="utf-8")
        self.falsa("jscpd", 'printf "%%s\\n" "jscpd $*" >> "%s"\n[ "$1" = --version ] && { echo "jscpd 5.4.3"; exit 0; }\n'
                   'while [ $# -gt 0 ]; do [ "$1" = --output ] && out="$2"; shift; done\n'
                   'find . -type f >> "%s"\n'
                   'if [ "${PWD##*/}" = diff ]; then r="%s"; else r="%s"; fi\n'
                   'cat "$r" > "$out/jscpd-report.json"\necho "%s" >&2\nexit %d\n'
                   % (self.p(self.chamadas), self.p(self.chamadas), self.p(self.tmp / "diff.json"),
                      self.p(self.tmp / "jscpd.json"), erro, rc))

    @staticmethod
    def p(caminho):
        from apoio import caminho_bash
        return caminho_bash(caminho)

    def path(self):
        extra = {n: self.falsas / n for n in ("lizard", "jscpd") if (self.falsas / n).exists()}
        ausentes = [n for n in ("lizard", "jscpd", "npx") if n not in extra]
        pasta = self.tmp / "path"
        shutil.rmtree(str(pasta), ignore_errors=True)
        return path_restrito(pasta, FERRAMENTAS, ausentes=[a for a in ausentes if a != "npx"], extra=extra)

    def arvore(self):
        h = hashlib.sha256()
        for p in sorted(x for x in self.r.rglob("*") if x.is_file()):
            h.update(p.relative_to(self.r).as_posix().encode() + b"\0" + p.read_bytes())
        return h.hexdigest()

    def mede(self, *args, path=None, cwd=None):
        env = dict(self.env, PATH=path or self.path())
        self.git(self.r, "status", "--porcelain")   # o git atualiza o índice antes do hash, não no meio
        antes = self.arvore()
        rc, out, err = self.roda([BASH, SCRIPT, *args], cwd or self.r, env)
        self.assertEqual(self.arvore(), antes, "a árvore mudou\n" + out + err)
        self.assertEqual([x.name for x in self.tmpdir.iterdir() if not x.name.startswith("sdd-python.")], [],
                         "sobrou temporário")
        return rc, out, err

    def ok(self, *args, **kw):
        rc, out, err = self.mede(*args, **kw)
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(out.startswith("## Qualidade (avisos)\n"), out)
        self.assertIn("RESULTADO:", err)
        return out, err

    def parte(self, out, titulo):
        i = out.index("### " + titulo)
        j = out.find("\n### ", i + 1)
        return out[i:] if j < 0 else out[i:j]


class AT017Achados(Base):
    def test_os_dois_achados_exit_0(self):
        self.frente()
        self.lizard()
        self.jscpd()
        out, err = self.ok()
        c, d = self.parte(out, "Complexidade"), self.parte(out, "Duplicação")
        self.assertIn("`src/nova.py:1-31` `grande`: complexidade 15 (limite 10) · 6 parâmetros (limite 5)", c)
        self.assertNotIn("linhas (limite", c)
        self.assertNotIn("soma_notas", c)
        self.assertIn("2 funções", c)
        self.assertIn("`src/copia.py:1-11` repete `src/notas.py:1-11` (11 linhas, 58 tokens)", d)
        self.assertIn("RESULTADO: AVISOS", err)
        self.assertNotIn("não medido", out)

    def test_limite_do_jscpd_e_config_proprio(self):
        self.frente()
        self.escreve(self.r, ".jscpd.json", '{"threshold": 0, "minTokens": 9999}')
        self.lizard()
        self.jscpd()
        self.ok()
        chamada = self.chamadas.read_text(encoding="utf-8")
        self.assertRegex(chamada, r"jscpd .*--min-tokens 50 ")
        self.assertIn("--config ", chamada)
        self.assertNotIn("--config .jscpd.json", chamada)

    def test_medido_sem_aviso_diz_quantos_mediu(self):
        self.frente()
        self.lizard(CSV_NOTAS)
        self.jscpd(jscpd_json())
        out, err = self.ok()
        self.assertIn("nenhum aviso (1 função medida", out)
        self.assertIn("nenhum aviso (2 arquivos do diff lidos, de 2", out)
        self.assertIn("RESULTADO: NADA ACHADO", err)

    def test_teto_de_20_itens_o_pior_primeiro(self):
        self.escreve(self.r, "src/nova.py", "x = 1\n" * 100)
        self.commit(self.r)
        self.lizard("".join('1,%d,9,1,1,"f%d@%d-%d@./src/nova.py","./src/nova.py","f%d","f%d( )",%d,%d\n'
                            % (11 + i, i, i + 1, i + 1, i, i, i + 1, i + 1) for i in range(25)))
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        c = self.parte(out, "Complexidade")
        self.assertEqual(c.count("complexidade "), 20)
        self.assertIn("e mais 5", c)
        self.assertLess(c.index("`f24`"), c.index("`f23`"))

    def test_nome_com_crase_nao_abre_secao(self):
        self.frente()
        self.lizard(CSV_GRANDE.replace('"grande"', '"g`ra\n## Outra\nnde"'))
        self.jscpd()
        out, _ = self.ok()
        self.assertEqual([l for l in out.splitlines() if l.startswith("## ")], ["## Qualidade (avisos)"])

    @unittest.skipUnless(shutil.which("lizard") and shutil.which("jscpd"), "lizard e jscpd reais fora do PATH")
    def test_com_as_ferramentas_reais(self):
        self.frente()
        out, _ = self.ok(path=self.env["PATH"])
        self.assertIn("`grande`: complexidade 15 (limite 10) · 6 parâmetros (limite 5)", out)
        self.assertRegex(self.parte(out, "Duplicação"), r"src/(copia|notas)\.py:\d+-\d+` repete `src/(copia|notas)\.py")
        self.assertNotIn("velha", self.parte(out, "Complexidade"))


class AT018NaoMedido(Base):
    def nao_medido(self, texto, ferramenta):
        self.assertIn("não medido: " + ferramenta, texto)
        for p in PROIBIDOS:
            self.assertNotIn(p, texto)

    def test_as_duas_ausentes(self):
        self.frente()
        out, err = self.ok()
        self.nao_medido(out, "lizard ausente")
        self.nao_medido(out, "jscpd ausente")
        self.assertIn("python3 -m pip install lizard", out)
        self.assertIn("npm install -g jscpd", out)
        self.assertIn("RESULTADO: NÃO MEDIDO", err)

    def test_so_o_jscpd_ausente_mede_a_complexidade(self):
        self.frente()
        self.lizard()
        out, _ = self.ok()
        self.assertIn("complexidade 15", out)
        self.nao_medido(self.parte(out, "Duplicação"), "jscpd ausente")

    def test_so_o_lizard_ausente_mede_a_duplicacao(self):
        self.frente()
        self.jscpd()
        out, _ = self.ok()
        self.nao_medido(self.parte(out, "Complexidade"), "lizard ausente")
        self.assertIn("repete `src/notas.py", out)

    def test_ferramenta_que_falha(self):
        self.frente()
        self.lizard("", rc=1, erro="Traceback: quebrou")
        self.jscpd("{}", rc=2, erro="config ruim")
        out, _ = self.ok()
        self.nao_medido(out, "lizard falhou")
        self.nao_medido(out, "jscpd falhou")
        self.assertIn("quebrou", out)
        self.assertIn("config ruim", out)

    def test_saida_ilegivel(self):
        for csv in ("", "isto não é csv\n", '1,x,9,1,1,"a","./src/nova.py","f","f",1,1\n', CSV_GRANDE + "1,2\n",
                    CSV_GRANDE.replace("./src/nova.py", "./src/n\u00c3va.py")):
            for rel in ("", "não é json", "[]", '{"duplicates": 3}', jscpd_json(sources=0), '{"duplicates": []}',
                        jscpd_json({"firstFile": 1})):
                with self.subTest(csv=csv, rel=rel):
                    shutil.rmtree(str(self.r / "src"))
                    self.git(self.r, "checkout", "-q", "main", "--", "src")
                    self.frente()
                    self.lizard(csv)
                    self.jscpd(rel)
                    out, _ = self.ok()
                    self.nao_medido(self.parte(out, "Complexidade"), "")
                    self.nao_medido(self.parte(out, "Duplicação"), "")

    def test_jscpd_que_nao_grava_relatorio(self):
        self.frente()
        self.lizard()
        self.falsa("jscpd", "exit 0\n")
        out, _ = self.ok()
        self.nao_medido(self.parte(out, "Duplicação"), "jscpd")

    def test_jscpd_que_leu_o_projeto_mas_nao_o_diff(self):
        """Revisão do DESIGN, N1: ler o resto do projeto não prova que o código novo foi lido."""
        self.frente()
        self.lizard()
        self.jscpd(jscpd_json(sources=9), no_diff=jscpd_json(sources=0))
        out, _ = self.ok()
        self.nao_medido(self.parte(out, "Duplicação"), "jscpd não leu nenhum arquivo do diff")

    def test_nome_do_jscpd_em_outra_forma(self):
        """Revisão do código, rodada 1, N1: o nome que não casa não pode sumir calado."""
        self.frente()
        self.escreve(self.r, "src/Tela.vue", NOTAS)
        self.lizard()
        self.jscpd(jscpd_json(par("./src/copia.py", "src\\notas.py"), par("src/Tela.vue:javascript", "src/notas.py")))
        out, _ = self.ok()
        self.assertIn("`src/copia.py:1-11` repete `src/notas.py:1-11`", out)
        self.assertIn("`src/Tela.vue:1-11` repete", out)
        for ruim in ("/outro/lugar/copia.py", "src/sumiu.py", "../copia.py"):
            with self.subTest(nome=ruim):
                self.jscpd(jscpd_json(par(ruim, "src/notas.py")))
                out, _ = self.ok()
                self.nao_medido(self.parte(out, "Duplicação"), "jscpd devolveu saída que não entendi")

    def test_config_do_projeto_nao_chega_a_ferramenta(self):
        """Revisão do DESIGN, N2: nem .jscpd.json, nem a chave jscpd do package.json, nem o .gitignore."""
        self.frente()
        for nome in (".jscpd.json", "package.json", ".gitignore"):
            self.escreve(self.r, nome, "{}\n" if nome != ".gitignore" else "nada\n")
        self.lizard()
        self.jscpd()
        self.ok()
        visto = self.chamadas.read_text(encoding="utf-8")
        self.assertIn("./src/velha.py", visto)
        for nome in (".jscpd.json", "package.json", ".gitignore"):
            self.assertNotIn("./" + nome, visto)

    def test_nunca_usa_npx(self):
        fonte = SCRIPT.read_text(encoding="utf-8")
        codigo = [l for l in fonte.splitlines() if not l.lstrip().startswith("#")]
        self.assertFalse([l for l in codigo if "npx" in l])


class AT019SoODiff(Base):
    def test_funcao_intocada_fica_fora(self):
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha") + "\n\ndef pequena():\n    return 1\n")
        self.commit(self.r)
        self.lizard('31,15,132,6,31,"v","./src/velha.py","velha","velha( a )",1,31\n'
                    '2,1,5,0,2,"p","./src/velha.py","pequena","pequena( )",34,35\n')
        self.jscpd(jscpd_json(par("src/notas.py", "src/velha.py")))
        out, _ = self.ok()
        self.assertNotIn("`velha`", out)
        self.assertNotIn("repete", out)
        self.assertIn("1 função medida", out)

    def test_par_em_arquivo_do_diff_mas_fora_das_linhas(self):
        self.escreve(self.r, "src/notas.py", NOTAS + "\n\nX = 1\n")
        self.commit(self.r)
        self.lizard(CSV_NOTAS.replace("copia", "notas"))
        self.jscpd(jscpd_json(par("src/notas.py", "src/velha.py")))
        out, _ = self.ok()
        self.assertNotIn("repete", out)

    def test_nao_commitado_e_fora_do_indice_entram(self):
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha").replace("r = 0", "r = 1"))
        self.escreve(self.r, "src/nova é aqui.py", GRANDE)
        linha = '31,15,132,6,31,"v","./src/%s","%s","x",1,31\n'
        self.lizard(linha % ("velha.py", "velha") + linha % ("nova é aqui.py", "grande"))
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        self.assertIn("`src/velha.py:1-31` `velha`", out)
        self.assertIn("`src/nova é aqui.py:1-31` `grande`", out)
        self.assertIn("./src/nova é aqui.py", self.chamadas.read_text(encoding="utf-8"))

    def test_linha_so_apagada_conta_como_alterada(self):
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha").replace("        r += 3\n", "", 1))
        self.lizard('30,15,132,6,30,"v","./src/velha.py","velha","velha",1,30\n')
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        self.assertIn("`velha`", out)

    def test_apagar_o_que_vem_depois_nao_marca_a_funcao_anterior(self):
        """Revisão do DESIGN, N3: o git aponta o trecho apagado pela linha anterior a ele."""
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha") + "\n\ndef fim():\n    return 2\n")
        self.commit(self.r)
        self.git(self.r, "branch", "-q", "-f", "main", "frente")
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha"))
        self.lizard('31,15,132,6,31,"v","./src/velha.py","velha","velha",1,31\n')
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        self.assertNotIn("`velha`", out)

    def test_renomear_sem_mudar_nao_e_codigo_novo(self):
        self.git(self.r, "mv", "src/velha.py", "src/renomeada.py")
        self.commit(self.r)
        self.lizard()
        self.jscpd()
        out, _ = self.ok()
        self.assertEqual(out.count("não medido: nenhum arquivo de código no diff"), 2, out)
        self.assertFalse(self.chamadas.exists(), "sem código no diff, nenhuma ferramenta é chamada")

    def test_diff_sem_codigo(self):
        self.escreve(self.r, "LEIAME.md", "texto\n")
        self.escreve(self.r, "sdd/bin/x.py", GRANDE)
        self.escreve(self.r, ".agents/y.py", GRANDE)
        self.commit(self.r)
        out, err = self.ok()
        self.assertEqual(out.count("não medido: nenhum arquivo de código no diff"), 2, out)
        self.assertIn("RESULTADO: NÃO MEDIDO", err)

    def test_so_linguagem_fora_da_complexidade(self):
        self.escreve(self.r, "src/x.sh", "echo oi\n")
        self.escreve(self.r, "src/y.sh", "echo oi\n")
        self.lizard()
        self.jscpd(jscpd_json(par("src/x.sh", "src/y.sh", ini=1, fim=1)))
        out, _ = self.ok()
        c = self.parte(out, "Complexidade")
        self.assertIn("não medido", c)
        self.assertIn("linguagem sem suporte", c)
        self.assertIn("`src/x.sh:1-1` repete `src/y.sh:1-1`", out)

    def test_par_com_o_lado_do_diff_em_segundo(self):
        self.frente()
        self.lizard()
        self.jscpd(jscpd_json(par("src/notas.py", "src/copia.py"), par("src/copia.py", "src/notas.py")))
        out, _ = self.ok()
        self.assertEqual(out.count("repete"), 1, out)
        self.assertIn("`src/copia.py:1-11` repete `src/notas.py:1-11`", out)

    def test_nenhuma_funcao_do_diff(self):
        self.escreve(self.r, "src/const.py", "X = 1\n")
        self.lizard("")
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        c = self.parte(out, "Complexidade")
        self.assertIn("não medido: nenhuma função", c)
        for p in PROIBIDOS:
            self.assertNotIn(p, c)

    @unittest.skipIf(*SEM_SYMLINK)
    def test_link_simbolico_fica_fora(self):
        (self.r / "src" / "link.py").symlink_to(self.r / "src" / "velha.py")
        self.lizard()
        self.jscpd()
        out, _ = self.ok()
        self.assertIn("nenhum arquivo de código no diff", out)

    def test_base_remota_local_e_ausente(self):
        self.frente()
        self.git(self.r, "update-ref", "refs/remotes/origin/main", "main")
        self.git(self.r, "branch", "-q", "-D", "main")
        out, _ = self.ok()
        self.assertIn("origin/main", out)
        self.git(self.r, "update-ref", "-d", "refs/remotes/origin/main")
        rc, out, err = self.mede()
        self.assertEqual((rc, out), (64, ""))
        self.assertIn("--base", err)

    def test_gitattributes_menos_diff_nao_esconde_o_arquivo(self):
        self.escreve(self.r, ".gitattributes", "*.py -diff\n")
        self.escreve(self.r, "src/velha.py", GRANDE.replace("grande", "velha").replace("r = 0", "r = 1"))
        self.lizard('31,15,132,6,31,"v","./src/velha.py","velha","velha",1,31\n')
        self.jscpd(jscpd_json())
        out, _ = self.ok()
        self.assertIn("`velha`", out)

    def test_config_do_git_de_quem_roda_nao_muda_a_medida(self):
        self.frente()
        for k, v in (("color.ui", "always"), ("diff.noprefix", "true"), ("diff.external", "false"),
                     ("core.quotepath", "true"), ("diff.renames", "false"), ("diff.interHunkContext", "500")):
            self.git(self.r, "config", k, v)
        self.lizard()
        self.jscpd()
        out, _ = self.ok()
        self.assertIn("complexidade 15", out)


class AT020Limites(Base):
    def config(self, texto):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  name: x\n" + texto)

    def test_limites_do_config(self):
        self.frente()
        self.config("qualidade:\n  max_complexidade: 20\n  max_linhas: 30\n  max_parametros: 6\n  min_tokens: 80\n")
        self.lizard()
        self.jscpd()
        out, _ = self.ok()
        c = self.parte(out, "Complexidade")
        self.assertIn("`grande`: 31 linhas (limite 30)", c)
        self.assertNotIn("complexidade 15", c)
        self.assertNotIn("parâmetros (limite", c)
        self.assertRegex(self.chamadas.read_text(encoding="utf-8"), r"--min-tokens 80 ")

    def test_vazio_e_o_padrao(self):
        self.frente()
        self.config("qualidade:\n  max_complexidade: \"\"\n  max_linhas:   # comentário\n")
        self.lizard()
        self.jscpd()
        out, _ = self.ok()
        self.assertIn("complexidade 15 (limite 10) · 6 parâmetros (limite 5)", out)

    def test_invalido_64(self):
        for chave in ("max_complexidade", "max_linhas", "max_parametros", "min_tokens"):
            for valor in ("0", "-1", "dez", "1.5", "²"):
                with self.subTest(chave=chave, valor=valor):
                    self.config("qualidade:\n  %s: %s\n" % (chave, valor))
                    rc, out, err = self.mede()
                    self.assertEqual((rc, out), (64, ""))
                    self.assertIn("qualidade." + chave, err)

    def test_raiz_numa_subpasta(self):
        """Revisão do código, rodada 1, N2: no monorepo, o projeto é a subpasta de --raiz."""
        self.escreve(self.r, "app/sdd/config.yaml", "qualidade:\n  max_complexidade: 20\n  max_parametros: 5\n")
        self.escreve(self.r, "app/sdd/bin/x.py", GRANDE)
        self.escreve(self.r, "app/src/nova.py", GRANDE)
        self.escreve(self.r, "src/fora.py", GRANDE)
        self.commit(self.r)
        self.lizard(CSV_GRANDE)
        self.jscpd(jscpd_json())
        out, _ = self.ok("--raiz", "app")
        self.assertIn("`src/nova.py:1-31` `grande`: 6 parâmetros (limite 5)", out)
        self.assertNotIn("complexidade 15", out)
        chamada = [l for l in self.chamadas.read_text(encoding="utf-8").splitlines() if l.startswith("lizard --csv")]
        self.assertEqual(chamada, ["lizard --csv ./src/nova.py"])
        self.escreve(self.r, "app/sdd/config.yaml", "qualidade:\n  max_linhas: zero\n")
        self.assertEqual(self.mede("--raiz", "app")[0], 64)

    def test_uso_errado_64(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        for args, cwd in ((["--nada"], None), (["--base"], None), (["--base", "naoexiste"], None),
                          (["--base", "--x"], None), (["--raiz", str(self.tmp / "sumiu")], None), ([], fora)):
            with self.subTest(args=args):
                rc, out, err = self.mede(*args, cwd=cwd)
                self.assertEqual((rc, out), (64, ""), err)
                self.assertIn("RESULTADO:", err)

    def test_ajuda(self):
        rc, out, _ = self.mede("--help")
        self.assertEqual(rc, 0)
        self.assertIn("metricas-diff.sh", out)


RELATORIO = """# BUILD REPORT: FX

| ID | Critério | Resultado | Evidência |
|----|----------|-----------|-----------|
| AT-001 | x | false | — |

**Veredito do avaliador (C1):** N.A. (1 camada)

lint: slot vazio

%s
## Fim

ok
"""


class AT021ReportLint(Sandbox):
    def lint(self, secao, config="qualidade:\n  max_complexidade: 10\n"):
        r = self.tmp / "rl"
        if not r.exists():
            self.repo("rl")
        self.escreve(r, "sdd/config.yaml", "project:\n  name: x\n" + config)
        p = self.escreve(r, "sdd/reports/BUILD_REPORT_FX.md", RELATORIO % secao)
        rc, out, err = self.roda([sys.executable, LINT, p], r)
        return rc, out + err

    def test_secao_presente_passa_mesmo_com_achado(self):
        rc, s = self.lint("## Qualidade (avisos)\n\n- `a.py:1-9` `f`: complexidade 99 (limite 10)\n")
        self.assertEqual(rc, 0, s)
        rc, s = self.lint("## Qualidade (avisos)\n\n### Complexidade\n\n- não medido: lizard ausente\n")
        self.assertEqual(rc, 0, s)

    def test_sem_secao_com_o_mapa_reprova(self):
        for secao in ("", "## Qualidade (avisos)\n\n", "```\n## Qualidade (avisos)\n\nx\n```\n", "## Qualidade\n\nx\n",
                      "### Qualidade (avisos)\n\nx\n"):
            with self.subTest(secao=secao):
                rc, s = self.lint(secao)
                self.assertEqual(rc, 1, s)
                self.assertIn("[qualidade]", s)
                self.assertIn("metricas-diff.sh", s)

    def test_sem_o_mapa_so_avisa(self):
        for config in ("", "qualidades:\n  x: 1\n"):
            rc, s = self.lint("", config)
            self.assertEqual(rc, 0, s)
            self.assertIn("Qualidade (avisos)", s)

    def test_mapa_com_chaves_vazias_tambem_exige(self):
        rc, s = self.lint("", "qualidade:\n  max_complexidade: \"\"\n")
        self.assertEqual(rc, 1, s)


if __name__ == "__main__":
    unittest.main()
