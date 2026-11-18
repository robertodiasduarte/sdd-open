"""F26, bloco da marca (AT-008 a AT-010): as skills geradas para o starter dizem "SDD Starter" na descrição e na linha
de identificação; o teto de 1.024 caracteres para o gerador antes de gravar; as do Open não mudam de texto; o
checar.sh da F25 continua separando as duas origens. O Open e o starter de teste são os da base do test_gerar_starter
(repositórios temporários; nada aqui depende do .git do pacote)."""
from __future__ import annotations

import importlib.util
import json
import re
import sys

from apoio import BASH, RAIZ
from test_gerar_starter import LISTA, Base, arvore

PY = sys.executable
URL_STARTER = "https://github.com/robertodiasduarte/sdd-starter/releases/latest"
URL_OPEN = "https://github.com/robertodiasduarte/sdd-open/releases/latest"
MODOS = {ln.split("\t")[0] for ln in (RAIZ / "scripts/starter/modos.tsv").read_text(encoding="utf-8").splitlines()
         if ln.strip() and not ln.startswith("#")}


def descricao(texto: str) -> str:
    """Contada como o check-versions do starter conta (scripts/starter/raiz/scripts/check-versions.py)."""
    fm = re.match(r"\A---\n(.*?)\n---\n", texto, re.S).group(1).splitlines()
    for i, ln in enumerate(fm):
        if ln.startswith("description:"):
            v = ln[len("description:"):].strip()
            if v[:1] in ("|", ">"):
                return " ".join(x.strip() for x in fm[i + 1:] if x.startswith((" ", "\t")) and not re.match(r"^\S", x))
            if v.startswith('"'):
                return json.loads(v)
            return v.strip("'")
    return ""


def versao(texto: str) -> str:
    return re.search(r'^  version:\s*"([^"]+)"', texto, re.M).group(1)


class Marca(Base):
    def setUp(self):
        super().setUp()
        # AT-001 (o lado do gerador): documentos no Open de teste não chegam ao starter, porque a tag é lida pelo
        # git archive e a trava 1 os tira dele
        self.copia(".gitattributes", self.open)
        self.escreve(self.open, "sdd/features/DEFINE_DOC_F26.md", "# DEFINE de teste\n")
        self.escreve(self.open, "sdd/reports/evidence/DOC_F26/AT-001.log", "$ true\n[exit=0]\n")
        self.commit(self.open, "documentos")
        self.git(self.open, "tag", "-f", self.TAG)

    def test_at008_descricao_e_linha_com_a_marca_nas_18(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(len(LISTA), 19)   # F27: + sdd-desempenho-banco
        for skill in LISTA:
            with self.subTest(skill=skill):
                s = (self.starter / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                d = descricao(s)
                self.assertIn("SDD Starter", d[:60])
                self.assertNotIn("SDD Open", d)
                self.assertLessEqual(len(d), 1024)
                linha = "`%s v%s · SDD Starter · nov/2026 · versão atual: %s`" % (skill, versao(s), URL_STARTER)
                self.assertEqual(s.count(linha), 1, linha)
                self.assertEqual(len(re.findall(r"^`%s v" % re.escape(skill), s, re.M)), 1)

    def test_at008_where_skill_de_modo_e_sem_modo(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(MODOS, {"sdd-define", "sdd-design", "sdd-build", "sdd-release"})
        for skill in ("sdd-define", "sdd-release"):   # de modo: a descrição do modo não cita o Open, ganha o prefixo
            with self.subTest(skill=skill):
                d = descricao((self.starter / "skills" / skill / "SKILL.md").read_text(encoding="utf-8"))
                self.assertTrue(d.startswith("SDD Starter — "), d[:40])
        # sem modo, com "SDD Open" no começo: troca no lugar, sem prefixo
        d = descricao((self.starter / "skills/sdd-brainstorm/SKILL.md").read_text(encoding="utf-8"))
        self.assertTrue(d.startswith("Fase 0 do SDD Starter — "), d[:40])
        # sem modo, com "SDD Open" depois do caractere 49 (sdd-handoff): prefixo e troca das outras
        d = descricao((self.starter / "skills/sdd-handoff/SKILL.md").read_text(encoding="utf-8"))
        self.assertTrue(d.startswith("SDD Starter — "), d[:40])
        self.assertNotIn("SDD Open", d)

    def test_at001_documentos_do_open_nao_chegam_ao_starter(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        nomes = " ".join(arvore(self.starter))
        self.assertNotIn("DEFINE_DOC_F26", nomes)
        self.assertNotIn("DOC_F26", nomes)

    def test_at008_check_versions_do_starter_aceita_a_nova_e_recusa_a_antiga(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        rc, out, err = self.roda([PY, "-B", "scripts/check-versions.py"], self.starter)
        self.assertEqual(rc, 0, out + err)
        s = self.starter / "skills/sdd-kb/SKILL.md"
        t = s.read_text(encoding="utf-8")
        s.write_text(t.replace(" · SDD Starter · ", " · ", 1), encoding="utf-8")   # a linha antiga
        rc, out, err = self.roda([PY, "-B", "scripts/check-versions.py"], self.starter)
        self.assertNotEqual(rc, 0, out + err)
        self.assertIn("sdd-kb", out + err)
        s.write_text(t.replace("SDD Starter — ", "", 1), encoding="utf-8")         # a descrição sem a marca
        rc, out, err = self.roda([PY, "-B", "scripts/check-versions.py"], self.starter)
        self.assertNotEqual(rc, 0, out + err)
        self.assertIn("SDD Starter", out + err)

    def test_at008_descricao_entre_aspas_simples_ou_sem_aspas(self):
        # revisão do código, R5: a marca entra dentro das aspas simples (antes, ficava antes da aspa e a aspa virava texto)
        spec = importlib.util.spec_from_file_location("gerar_starter_f26", str(RAIZ / "scripts/gerar-starter.py"))
        g = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(g)
        for nome, linha, esperada in (
                ("aspas simples", "description: 'Faz algo útil: em uma linha.'",
                 "description: 'SDD Starter — Faz algo útil: em uma linha.'"),
                ("aspas duplas", 'description: "Faz algo útil."', 'description: "SDD Starter — Faz algo útil."'),
                ("sem aspas", "description: Faz algo útil.", "description: SDD Starter — Faz algo útil.")):
            with self.subTest(caso=nome):
                novo = g.marcar("---\nname: x\n%s\n---\n`x v1.0.0 · nov/2026 · versão atual: %s`\n" % (linha, URL_STARTER), "x")
                self.assertIn("\n%s\n" % esperada, novo)
                fm = novo.split("\n---\n", 1)[0][4:].split("\n")
                self.assertTrue(g.descricao_do(fm)[2].startswith("SDD Starter — Faz algo útil"))

    def test_at009_descricao_acima_do_teto_sai_65_sem_gravar(self):
        s = self.open / ".agents/skills/sdd-iniciar-repo/SKILL.md"
        t = s.read_text(encoding="utf-8")
        d = descricao(t)
        self.assertNotIn("SDD Open", d)   # esta ganha o prefixo de 14 caracteres
        crescida = d + " " + "x" * (1024 - len(d) - 14)   # 1.011 + 14 de prefixo = 1.025
        s.write_text(t.replace(json.dumps(d, ensure_ascii=False), json.dumps(crescida, ensure_ascii=False), 1),
                     encoding="utf-8")
        self.assertEqual(len(descricao(s.read_text(encoding="utf-8"))), 1011)
        self.commit(self.open, "descrição no limite")
        self.git(self.open, "tag", "-f", self.TAG)
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.assertEqual(rc, 65, out + err)
        self.assertIn("sdd-iniciar-repo", out + err)
        self.assertIn("1025 caracteres", out + err)
        self.assertEqual(arvore(self.starter), antes)

    def test_at010_cada_skill_da_lista_cabe_no_teto_com_a_marca(self):
        # a medida no Open de hoje: nenhuma descrição passa do teto depois da marca (a sdd-checar-ambiente encolheu)
        for skill in LISTA:
            with self.subTest(skill=skill):
                d = descricao((RAIZ / ".agents/skills" / skill / "SKILL.md").read_text(encoding="utf-8"))
                self.assertLessEqual(len(d) + (0 if 0 <= d.find("SDD Open") <= 49 else 14) + 3 * d.count("SDD Open"),
                                     1024)


class OpenSemMarca(Base):
    def test_at010_open_sem_sdd_starter(self):
        for skill in LISTA:
            with self.subTest(skill=skill):
                s = (RAIZ / ".agents/skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertNotIn("SDD Starter", descricao(s))
                linha = [ln for ln in s.splitlines() if ln.startswith("`%s v" % skill)]
                self.assertEqual(len(linha), 1)
                self.assertNotIn("SDD Starter", linha[0])
                self.assertIn(URL_OPEN, linha[0])

    def test_at010_checar_separa_as_duas_origens_com_a_linha_marcada(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        dup = RAIZ / ".agents/skills/sdd-checar-ambiente/scripts/duplicadas.sh"
        prog = 'source "$1"; dup_meta "$2"'
        for arq, origem in ((self.starter / "skills/sdd-define/SKILL.md", "starter"),
                            (RAIZ / ".agents/skills/sdd-define/SKILL.md", "open")):
            with self.subTest(origem=origem):
                rc, out, err = self.roda([BASH, "-c", prog, "x", dup, arq], self.tmp)
                self.assertEqual(rc, 0, out + err)
                self.assertTrue(out.strip().endswith("\t" + origem), repr(out))

    def test_at010_gerador_recusa_copia_que_mudou_sem_versao_maior(self):
        # o starter de teste passa a ter a sdd-kb na MESMA versão do Open: a cópia gerada muda (a marca) e a versão
        # não sobe; o gerador recusa, como exige o version gate do starter (LM-022)
        v = versao((RAIZ / ".agents/skills/sdd-kb/SKILL.md").read_text(encoding="utf-8"))
        t = (self.starter / "skills/sdd-kb/SKILL.md").read_text(encoding="utf-8")
        (self.starter / "skills/sdd-kb/SKILL.md").write_text(re.sub(r'version: "[^"]+"', 'version: "%s"' % v, t),
                                                             encoding="utf-8")
        self.commit(self.starter, "kb na versão do Open")
        rc, out, err = self.gerar()
        self.assertNotEqual(rc, 0, out + err)
        self.assertIn("sdd-kb", out + err)
        self.assertIn("versão não subiu", out + err)
