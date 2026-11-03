"""sdd/bin/patterns-lint.sh (F12, C3): lint dos patterns do projeto, --design e --self-test.

DEFINE F12 AT-004, AT-014 e AT-015. A fixture verde leva a data do dia (não envelhece); a sabotagem faz a
idade parar de bloquear no regime --design e o self-test tem de cair.
"""
from __future__ import annotations

import datetime
import shutil

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/patterns-lint.sh"
PB = ("--playbook", "sdd/fixtures/contexto/playbook.md")


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        (self.r / "sdd/bin").mkdir(parents=True)
        shutil.copy(str(RAIZ / SCRIPT), str(self.r / SCRIPT))
        shutil.copy(str(RAIZ / "sdd/bin/contexto-lint.sh"), str(self.r / "sdd/bin/contexto-lint.sh"))
        shutil.copytree(str(RAIZ / "sdd/fixtures/patterns"), str(self.r / "sdd/fixtures/patterns"))
        shutil.copytree(str(RAIZ / "sdd/fixtures/contexto"), str(self.r / "sdd/fixtures/contexto"))
        shutil.copytree(str(RAIZ / "sdd/patterns"), str(self.r / "sdd/patterns"))
        self.commit(self.r)

    def lint(self, *args: str, script: str = SCRIPT) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, script, *args], self.r)
        return rc, out + err

    def verde(self, destino) -> None:
        hoje = datetime.date.today().isoformat()
        texto = (self.r / "sdd/fixtures/patterns/valido-completo.md").read_text(encoding="utf-8")
        destino.write_text(texto.replace("__HOJE__", hoje), encoding="utf-8")


class Lint(Base):
    def test_self_test_verde(self):
        rc, out = self.lint("--self-test")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_pasta_do_pacote_e_pasta_com_patterns_reais(self):
        rc, out = self.lint("sdd/patterns")
        self.assertEqual(rc, 0, out)
        p = self.r / "pat"
        p.mkdir()
        self.verde(p / "pedidos.md")
        shutil.copy(str(self.r / "sdd/fixtures/contexto/dominio.md"), str(p / "dominio.md"))
        (p / "README.md").write_text("# só texto, sem as 6 seções\n", encoding="utf-8")
        rc, out = self.lint(*PB, "pat")
        self.assertEqual(rc, 0, out)
        self.assertIn("2 pattern(s) OK", out)

    def test_classes_vermelhas(self):
        casos = {"sem-secao": "secao-ausente", "secao-fora-de-ordem": "secao-fora-de-ordem",
                 "path-morto": "path-morto", "lm-morto": "lm-morto", "linha-alem-do-fim": "path-morto",
                 "linha-alem-do-fim-basename": "path-morto"}
        hoje = datetime.date.today().isoformat()
        for fx, classe in casos.items():
            with self.subTest(fixture=fx):
                p = self.r / ("solo-" + fx)
                p.mkdir()
                t = (self.r / "sdd/fixtures/patterns" / (fx + ".md")).read_text(encoding="utf-8")
                (p / "x.md").write_text(t.replace("__HOJE__", hoje), encoding="utf-8")
                rc, out = self.lint(*PB, p.name)
                self.assertEqual(rc, 2, out)
                self.assertIn("[" + classe + "]", out)

    def test_design_vencido_citado_bloqueia_com_data_dias_e_limite(self):
        p = self.r / "venc"
        p.mkdir()
        shutil.copy(str(self.r / "sdd/fixtures/patterns/valido-vencido.md"), str(p / "pedidos.md"))
        rc, out = self.lint(*PB, "--design", "sdd/fixtures/patterns/DESIGN_FIXTURE_CITA_PEDIDOS.md", "venc")
        self.assertEqual(rc, 2, out)
        self.assertIn("[validado-vencido]", out)
        self.assertIn("validado em 2020-01-01", out)
        self.assertIn("o limite é 90", out)

    def test_design_nao_citado_so_avisa(self):
        p = self.r / "vnc"
        p.mkdir()
        self.verde(p / "pedidos.md")
        shutil.copy(str(self.r / "sdd/fixtures/patterns/valido-vencido.md"), str(p / "estoque.md"))
        rc, out = self.lint(*PB, "--design", "sdd/fixtures/patterns/DESIGN_FIXTURE_CITA_PEDIDOS.md", "vnc")
        self.assertEqual(rc, 0, out)
        self.assertIn("não citado no DESIGN, não bloqueia", out)

    def test_uso(self):
        for args in ((), ("--flag",), ("nao-existe",), ("--design", "nao-existe.md"), ("--playbook",)):
            with self.subTest(args=args):
                rc, _ = self.lint(*args)
                self.assertEqual(rc, 64)


class Aval1(Base):
    def test_m2_orientacao_do_template_e_exemplo_em_cerca_nao_sao_citacao(self):
        shutil.copy(str(RAIZ / "sdd/templates/DESIGN_TEMPLATE.md"), str(self.r / "D.md"))
        with open(self.r / "D.md", "a", encoding="utf-8") as f:
            f.write("\n```markdown\n**Pattern:** `patterns/exemplo.md §Esqueleto` (validado_em 2026-11-03)\n```\n")
        rc, out = self.lint(*PB, "--design", "D.md", "sdd/patterns")
        self.assertEqual(rc, 0, out)
        self.assertIn("nenhum pattern citado", out)

    def test_aval2_citacao_em_lista_conta_e_cerca_til_nao(self):
        p = self.r / "venc2"
        p.mkdir()
        shutil.copy(str(self.r / "sdd/fixtures/patterns/valido-vencido.md"), str(p / "pedidos.md"))
        cit = "**Pattern:** `patterns/pedidos.md §Esqueleto` (validado_em 2020-01-01)"
        for forma in ("- " + cit, "  " + cit, "1. " + cit):
            with self.subTest(forma=forma):
                self.escreve(self.r, "D.md", "## Code Patterns\n\n" + forma + "\n")
                rc, out = self.lint(*PB, "--design", "D.md", "venc2")
                self.assertEqual(rc, 2, out)
                self.assertIn("[validado-vencido]", out)
        self.escreve(self.r, "D.md", "## Code Patterns\n\n~~~markdown\n" + cit + "\n~~~\n")
        rc, out = self.lint(*PB, "--design", "D.md", "venc2")
        self.assertEqual(rc, 0, out)

    def test_l4_caminho_relativo_de_uma_subpasta(self):
        p = self.r / "sdd/pat"
        p.mkdir()
        self.verde(p / "pedidos.md")
        rc, out, err = self.roda([BASH, "bin/patterns-lint.sh", "--playbook", "fixtures/contexto/playbook.md", "pat"], self.r / "sdd")
        self.assertEqual(rc, 0, out + err)


class Real1(Base):
    def test_r4_ancora_na_linha_zero_e_path_morto(self):
        p = self.r / "zero"
        p.mkdir()
        self.verde(p / "pedidos.md")
        t = (p / "pedidos.md").read_text(encoding="utf-8").replace("app/pedidos.py:6", "app/pedidos.py:0")
        (p / "pedidos.md").write_text(t, encoding="utf-8")
        rc, out = self.lint(*PB, "zero")
        self.assertEqual(rc, 2, out)
        self.assertIn("[path-morto]", out)


class Sabotagem(Base):
    def test_idade_que_nao_bloqueia_no_design_derruba_o_self_test(self):
        texto = (self.r / SCRIPT).read_text(encoding="utf-8")
        alvo = 'erro "validado-vencido" "${nome}: citado no DESIGN'
        self.assertIn(alvo, texto)
        (self.r / "sdd/bin/sabotado.sh").write_text(texto.replace(alvo, 'aviso "${nome}: citado no DESIGN'), encoding="utf-8")
        rc, out = self.lint("--self-test", script="sdd/bin/sabotado.sh")
        self.assertEqual(rc, 2, out)
        self.assertIn("vencido CITADO", out)
