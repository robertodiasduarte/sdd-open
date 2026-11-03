"""sdd/bin/contexto-lint.sh (F12, C1): lint do CONTEXTO de domínio, --validade, --sugerir e --self-test.

Cada classe de erro tem fixture vermelha em sdd/fixtures/contexto/ e o teste exige a classe CERTA, não só
exit ≠ 0 (DEFINE F12 AT-001 a AT-004). A sabotagem tira uma checagem do script e o self-test tem de cair.
"""
from __future__ import annotations

import shutil

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/contexto-lint.sh"
FX = "sdd/fixtures/contexto"
DOM = ("--dominio", FX + "/dominio.md", "--playbook", FX + "/playbook.md")


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        for rel in (SCRIPT, "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md"):
            (self.r / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(str(RAIZ / rel), str(self.r / rel))
        shutil.copytree(str(RAIZ / FX), str(self.r / FX))
        self.commit(self.r)

    def lint(self, *args: str, script: str = SCRIPT) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, script, *args], self.r)
        return rc, out + err


class Lint(Base):
    def test_self_test_verde(self):
        rc, out = self.lint("--self-test")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_cada_fixture_vermelha_acusa_a_sua_classe(self):
        casos = {"sem-cabecalho": "cabecalho-ausente", "sem-secao": "secao-ausente",
                 "secao-fora-de-ordem": "secao-fora-de-ordem", "path-morto": "path-morto",
                 "linha-alem-do-fim": "path-morto", "sup-ausente": "sup-ausente",
                 "ctx-desconhecido": "ctx-desconhecido", "lm-morto": "lm-morto"}
        for fx, classe in casos.items():
            with self.subTest(fixture=fx):
                rc, out = self.lint(*DOM, FX + "/" + fx + ".md")
                self.assertEqual(rc, 2, out)
                self.assertIn("[" + classe + "]", out)
                self.assertIn("RESULTADO: VERMELHO", out)
                self.assertRegex(out, r"\n→ \S")

    def test_verde_com_aviso_de_superficie_e_pasta_pula_readme(self):
        rc, out = self.lint(*DOM, FX + "/valido-completo.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("[superficie-nao-cobre]", out)
        self.assertIn("app/estoque.sql", out)
        pasta = self.r / "ctx"
        pasta.mkdir()
        shutil.copy(str(self.r / FX / "valido-completo.md"), str(pasta / "pedidos.md"))
        (pasta / "README.md").write_text("# readme\n", encoding="utf-8")
        rc, out = self.lint(*DOM, "ctx")
        self.assertEqual(rc, 0, out)
        self.assertIn("1 CONTEXTO(s) OK", out)

    def test_uso_sai_64(self):
        for args in ((), ("--flag-que-nao-existe",), ("nao-existe.md",), ("--validade",), ("--dominio",),
                     ("--sugerir", FX + "/INPUT_FIXTURE_PEDIDOS.md", "--dir")):
            with self.subTest(args=args):
                rc, _ = self.lint(*args)
                self.assertEqual(rc, 64)

    def test_fora_de_um_repositorio_git_sai_64(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, _, _ = self.roda([BASH, str(self.r / SCRIPT), "x.md"], fora)
        self.assertEqual(rc, 64)


class Validade(Base):
    def test_ref_padrao_e_origin_da_branch_padrao_e_senao_a_local(self):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  default_branch: trunk\n")
        self.git(self.r, "branch", "trunk")
        sha = self.git(self.r, "rev-parse", "HEAD").strip()
        ctx = (self.r / FX / "validade-template.md").read_text(encoding="utf-8").replace("__SHA__", sha)
        self.escreve(self.r, "c.md", ctx.replace("superficies: a.md", "superficies: sdd/fixtures/contexto/app/pedidos.py"))
        rc, out = self.lint("--validade", "c.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("..trunk", out)
        self.git(self.r, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        rc, out = self.lint("--validade", "c.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("..origin/trunk", out)

    def test_vencido_sai_1_e_nomeia_o_arquivo(self):
        sha = self.git(self.r, "rev-parse", "HEAD").strip()
        ctx = (self.r / FX / "validade-template.md").read_text(encoding="utf-8").replace("__SHA__", sha)
        self.escreve(self.r, "c.md", ctx.replace("superficies: a.md", "superficies: sdd/fixtures/contexto/app/pedidos.py"))
        (self.r / FX / "app/pedidos.py").write_text("mudou\n", encoding="utf-8")
        self.commit(self.r)
        rc, out = self.lint("--validade", "c.md", "--ref", "HEAD")
        self.assertEqual(rc, 1, out)
        self.assertIn("CONTEXTO VENCIDO", out)
        self.assertIn("app/pedidos.py", out)
        self.assertIn("RESULTADO: VENCIDO", out)


class Sugerir(Base):
    def test_camadas_vem_de_layers_e_gerar(self):
        self.escreve(self.r, "sdd/config.yaml",
                     'project:\n  default_branch: main\nlayers:\n  api: "src/api/**"\n  ui: ""\n  sql: "db/migrations/**"\n')
        rc, out = self.lint("--dominio", FX + "/dominio.md", "--sugerir", FX + "/INPUT_FIXTURE_PEDIDOS.md",
                            "--dir", "sdd/contexto", "--ref", "HEAD")
        self.assertEqual(rc, 0, out)
        self.assertIn("camadas=1 (api)", out)
        self.assertRegex(out, r"(?m)^ctx:pedidos termos=\d+ .*estado=ausente")
        self.assertIn("recomendacao: gerar (ctx:pedidos ausente", out)
        self.assertIn("RESULTADO: GERAR", out)

    def test_sem_mapa_de_dominios_pula_e_sai_0(self):
        rc, out = self.lint("--sugerir", FX + "/INPUT_FIXTURE_PEDIDOS.md", "--ref", "HEAD")
        self.assertEqual(rc, 0, out)
        self.assertIn("recomendacao: pular (sem sdd/patterns/dominio.md)", out)

    def test_no_maximo_dois_dominios(self):
        dominio = (self.r / FX / "dominio.md").read_text(encoding="utf-8")
        extra = "".join("\n### ctx:extra%d\n\n**Âncoras:** `pedido_item` · `checkout_rapido`\nsup: `pedido_item`\n" % i
                        for i in range(3))
        self.escreve(self.r, "d.md", dominio.replace("## Checklist de conformidade", extra + "\n## Checklist de conformidade"))
        self.escreve(self.r, "in.md", "checkout e pedido_item e checkout_rapido\n")
        rc, out = self.lint("--dominio", "d.md", "--sugerir", "in.md", "--dir", "sdd/contexto", "--ref", "HEAD")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len([l for l in out.splitlines() if l.startswith("ctx:")]), 2, out)


class Sabotagem(Base):
    def test_sem_a_checagem_de_landmine_o_self_test_cai(self):
        texto = (self.r / SCRIPT).read_text(encoding="utf-8")
        self.assertIn('  checa_landmines    "${f}" "${nome}"\n', texto)
        sabotado = self.r / "sdd/bin/sabotado.sh"
        sabotado.write_text(texto.replace('  checa_landmines    "${f}" "${nome}"\n', ""), encoding="utf-8")
        rc, out = self.lint("--self-test", script="sdd/bin/sabotado.sh")
        self.assertEqual(rc, 2, out)
        self.assertIn("lm-morto", out)
