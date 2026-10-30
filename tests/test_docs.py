"""Os documentos do pacote dizem o que o pacote faz, e cada link deles abre.

Lê direto da raiz (sem rede, sem sandbox). Sete grupos:
  Links           — todo link relativo de README*.md, CONTRIBUTING.md e docs/**/*.md aponta para arquivo
                    que existe, e toda #âncora casa com um título pela regra do GitHub;
  Guia            — docs/pt-BR/guia-do-aluno.md cobre as 17 skills, os 7 agentes e a instalação do open,
                    sem as premissas do sdd-starter (npx, 15 skills, sdd/ fora do git…);
  Quickstart      — a regra do método, "valide antes de seguir" por fase, a tabela "onde roda" no passo 4
                    e a atualização pelo doctor + init no passo 5;
  Roadmap         — os temas planejados e "Specs como deltas" em avaliação, sem data;
  Comparison      — "Specs como deltas" continua ❌ em avaliação na coluna do SDD Open;
  ReadmeEAgents   — README e AGENTS.md.tmpl citam as 17 skills, a KB e o OK único;
  PorQueCadaRegra — as 7 skills de fase e as 2 de terreno guardam o motivo das próprias regras.

As frases fixas ficam nas constantes abaixo: mudar a redação de uma delas é mudar a constante de propósito.
"""
from __future__ import annotations

import re
import tempfile
import unicodedata
import unittest
from pathlib import Path

from apoio import RAIZ

SKILLS = sorted(p.name for p in (RAIZ / ".agents/skills").iterdir() if (p / "SKILL.md").is_file())
AGENTES = ("Claude Code", "Codex CLI", "Gemini CLI", "Cursor", "Kimi Code", "Grok Build", "GLM")
PREPARO = ("sdd-checar-ambiente", "sdd-iniciar-repo", "sdd-higiene-dado", "sdd-new-session")
FASE = ("sdd-brainstorm", "sdd-define", "sdd-governanca", "sdd-ux-review", "sdd-design", "sdd-build",
        "sdd-release")
COM_SECAO = FASE + ("sdd-new-session", "sdd-iniciar-repo")

GUIA = RAIZ / "docs/pt-BR/guia-do-aluno.md"
# O que o guia do sdd-starter dizia e no open é falso.
PROIBIDO_NO_GUIA = ("npx skills", "15 skills", "ux-review-builder", "sdd-starter/releases",
                    "sdd/BRAINSTORM_", "sdd/DEFINE_", "sdd/DESIGN_", "sdd/BUILD_REPORT_", "sdd/HANDOFF_")
SDD_FORA_DO_GIT = re.compile(r"sdd/.{0,80}(não vai para o GitHub|fora do git)")

QUICKSTART = {
    "en": (RAIZ / "docs/quickstart.md",
           "never move on to the next phase with a document you have not read",
           "**Validate before moving on:**",
           "| You want… | Write in the Design | In the Build |"),
    "pt": (RAIZ / "docs/pt-BR/quickstart.md",
           "nunca siga para a próxima fase com um documento que você não leu",
           "**Valide antes de seguir:**",
           "| Você quer… | Escreva no Design | No Build |"),
}

ROADMAP = {
    "en": (RAIZ / "docs/roadmap.md", "[Português](pt-BR/roadmap.md)", "planned", "under evaluation",
           ("Hooks", "Chained", "Adversarial", "governance", "sdd-loop-builder", "reconciliation")),
    "pt": (RAIZ / "docs/pt-BR/roadmap.md", "[English](../roadmap.md)", "planejado", "em avaliação",
           ("Hooks", "encadeado", "adversarial", "governança", "sdd-loop-builder", "Reconciliação")),
}

COMPARISON = {
    "en": (RAIZ / "docs/comparison.md", "| Specs as deltas", "under evaluation"),
    "pt": (RAIZ / "docs/pt-BR/comparison.md", "| Specs como deltas", "em avaliação"),
}

README = {
    "en": (RAIZ / "README.md", "docs/roadmap.md", "single approval", "README.pt-BR.md"),
    "pt": (RAIZ / "README.pt-BR.md", "docs/pt-BR/roadmap.md", "um OK só", "README.md"),
}
AGENTS_TMPL = RAIZ / "AGENTS.md.tmpl"

TITULO_SECAO = re.compile(r"^## Por que cada regra existe( \(não apague sem ler\))?$", re.M)
ITEM_SECAO = re.compile(r"^- \*\*.+?\*\* — ")

CERCA = re.compile(r"^(```|~~~)")
CRASE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
TITULO = re.compile(r"^#+\s+(.*?)\s*#*\s*$")


def ler(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def ancora(titulo: str) -> str:
    """A âncora que o GitHub gera para um título: minúsculas, só letra, marca, dígito, conector, espaço e
    hífen, espaço vira hífen. NFC primeiro, para o título em NFD dar a mesma âncora."""
    t = unicodedata.normalize("NFC", titulo.replace("`", "").strip()).lower()
    fica = [c for c in t
            if c in " -" or unicodedata.category(c)[0] in "LM" or unicodedata.category(c) in ("Nd", "Pc")]
    return "".join(fica).replace(" ", "-")


def linhas_fora_de_cerca(p: Path):
    dentro = False
    for n, ln in enumerate(ler(p).splitlines(), 1):
        if CERCA.match(ln.lstrip()):
            dentro = not dentro
            continue
        if not dentro:
            yield n, ln


def ancoras(p: Path) -> set:
    vistas, saida = dict(), set()
    for _, ln in linhas_fora_de_cerca(p):
        m = TITULO.match(ln)
        if m:
            base = ancora(m.group(1))
            k = vistas.get(base, 0)
            vistas[base] = k + 1
            saida.add(base if k == 0 else base + "-" + str(k))
    return saida


def docs() -> list:
    raiz = [RAIZ / n for n in ("README.md", "README.pt-BR.md", "CONTRIBUTING.md")]
    return [p for p in raiz if p.is_file()] + sorted((RAIZ / "docs").rglob("*.md"))


def links_quebrados(p: Path) -> list:
    saida = []
    for n, ln in linhas_fora_de_cerca(p):
        for alvo in LINK.findall(CRASE.sub("", ln)):
            if alvo.startswith(("http://", "https://", "mailto:")):
                continue
            caminho, _, anc = alvo.partition("#")
            destino = (p.parent / caminho) if caminho else p
            onde = "%s:%d → %s" % (p.relative_to(RAIZ), n, alvo)
            if not destino.exists():
                saida.append(onde + " (arquivo não existe)")
            elif anc and destino.suffix == ".md" and anc not in ancoras(destino):
                saida.append(onde + " (âncora não existe)")
    return saida


def trecho(texto: str, de: str) -> str:
    """Do título que começa por `de` até o próximo `## ` (o título de fora)."""
    linhas = texto.splitlines()
    ini = next((i for i, ln in enumerate(linhas) if ln.startswith(de)), None)
    if ini is None:
        return ""
    fim = next((j for j in range(ini + 1, len(linhas)) if linhas[j].startswith("## ")), len(linhas))
    return "\n".join(linhas[ini:fim])


def linhas_de_tabela(texto: str) -> list:
    return [ln for ln in texto.splitlines() if ln.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", ln)]


class Links(unittest.TestCase):
    def test_todo_link_relativo_abre(self):
        quebrados = []
        for p in docs():
            quebrados += links_quebrados(p)
        self.assertEqual(quebrados, [], "\n".join(quebrados))

    def test_ancora_segue_a_regra_do_github(self):
        casos = {
            "1. O que você precisa": "1-o-que-você-precisa",
            "6. Seu primeiro projeto, do zero à publicação": "6-seu-primeiro-projeto-do-zero-à-publicação",
            "A parada ⏸" + chr(0xFE0F): "a-parada-" + chr(0xFE0F),  # o seletor de variação fica
            "`sdd-kb` e o `kb-dominios.py`": "sdd-kb-e-o-kb-dominiospy",
            unicodedata.normalize("NFD", "Glossário"): "glossário",
        }
        for titulo, esperado in casos.items():
            with self.subTest(titulo=titulo):
                self.assertEqual(ancora(titulo), esperado)

    def test_o_teste_acusa_link_quebrado(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_text("# Título\n\n[ok](#título) [falta](b.md) [âncora](#outra)\n"
                         "```\n[dentro de bloco](nao-existe.md)\n```\n", encoding="utf-8")
            achados = [x.split("→", 1)[1].strip() for x in links_quebrados_fora_da_raiz(p)]
        self.assertEqual(achados, ["b.md (arquivo não existe)", "#outra (âncora não existe)"])


def links_quebrados_fora_da_raiz(p: Path) -> list:
    """links_quebrados() para um arquivo fora de RAIZ (o teste do próprio teste)."""
    saida = []
    for n, ln in linhas_fora_de_cerca(p):
        for alvo in LINK.findall(CRASE.sub("", ln)):
            caminho, _, anc = alvo.partition("#")
            destino = (p.parent / caminho) if caminho else p
            if not destino.exists():
                saida.append("%d → %s (arquivo não existe)" % (n, alvo))
            elif anc and destino.suffix == ".md" and anc not in ancoras(destino):
                saida.append("%d → %s (âncora não existe)" % (n, alvo))
    return saida


class Guia(unittest.TestCase):
    def setUp(self):
        self.assertTrue(GUIA.is_file(), "falta docs/pt-BR/guia-do-aluno.md")
        self.texto = ler(GUIA)

    def test_dez_blocos_numerados(self):
        for n in range(1, 11):
            with self.subTest(bloco=n):
                self.assertRegex(self.texto, r"(?m)^## %d\. \S" % n)

    def test_uma_ficha_por_skill(self):
        faltam = [s for s in SKILLS if not re.search(r"(?m)^#### %s\s*$" % re.escape(s), self.texto)]
        self.assertEqual(faltam, [], "skills sem ficha no catálogo")
        self.assertEqual(len(SKILLS), 17)

    def test_os_sete_agentes(self):
        self.assertEqual([a for a in AGENTES if a not in self.texto], [])

    def test_instalacao_e_atualizacao_do_open(self):
        for termo in ("init --vendors", "--yes", "python3", "doctor", "sdd-open/releases/latest"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)
        self.assertTrue(any("apague" in ln and "init" in ln for ln in self.texto.splitlines()),
                        "o guia não diz como receber uma skill nova: apagar a pasta e rodar init")

    def test_sem_as_premissas_do_starter(self):
        achados = [t for t in PROIBIDO_NO_GUIA if t in self.texto]
        achados += [m.group(0) for m in SDD_FORA_DO_GIT.finditer(self.texto)]
        self.assertEqual(achados, [])


class Quickstart(unittest.TestCase):
    def test_regra_validacoes_tabela_e_atualizacao(self):
        for lingua, (p, regra, valide, cabecalho) in QUICKSTART.items():
            texto = ler(p)
            passo4, passo5 = trecho(texto, "## 4."), trecho(texto, "## 5.")
            with self.subTest(lingua=lingua):
                self.assertIn(regra, texto)
                n = sum(1 for ln in texto.splitlines() if ln.lstrip("> ").startswith(valide))
                self.assertGreaterEqual(n, 4, "linhas '%s' em %s" % (valide, p.name))
                self.assertIn(cabecalho, passo4)
                self.assertEqual([a for a in AGENTES if a not in passo4], [], "agentes fora do passo 4")
                self.assertIn("doctor", passo5)
                self.assertIn("init", passo5)
                self.assertNotIn("Lovable", texto)


class Roadmap(unittest.TestCase):
    def test_temas_status_e_sem_data(self):
        for lingua, (p, cabecalho, planejado, avaliacao, temas) in ROADMAP.items():
            self.assertTrue(p.is_file(), "falta %s" % p.relative_to(RAIZ))
            texto = ler(p)
            linhas = linhas_de_tabela(texto)
            with self.subTest(lingua=lingua):
                self.assertIn(cabecalho, texto.splitlines()[0])
                for tema in temas:
                    achadas = [ln for ln in linhas if tema in ln]
                    self.assertTrue(achadas, "tema '%s' fora da tabela" % tema)
                    self.assertIn(planejado, achadas[0])
                deltas = [ln for ln in linhas if "deltas" in ln]
                self.assertTrue(deltas, "linha de deltas fora da tabela")
                self.assertIn(avaliacao, deltas[0])
                self.assertNotIn(planejado, deltas[0])
                self.assertIsNone(re.search(r"\b20\d\d\b", texto), "o roadmap não leva data")


class Comparison(unittest.TestCase):
    def test_deltas_continua_em_avaliacao_na_coluna_do_open(self):
        for lingua, (p, inicio, status) in COMPARISON.items():
            linhas = [ln for ln in ler(p).splitlines() if ln.startswith(inicio)]
            with self.subTest(lingua=lingua):
                self.assertEqual(len(linhas), 1, "linha '%s' em %s" % (inicio, p.name))
                celula = linhas[0].strip().strip("|").split("|")[-1]
                self.assertIn(status, celula)
                self.assertIn("❌", celula)
                self.assertNotIn("✅", celula)


class ReadmeEAgents(unittest.TestCase):
    def test_readme_cita_as_skills_a_kb_e_o_ok(self):
        for lingua, (p, roadmap, ok, outro) in README.items():
            texto = ler(p)
            with self.subTest(lingua=lingua):
                self.assertEqual([s for s in SKILLS if s not in texto], [])
                for termo in ("kb-dominios.py", "docs/pt-BR/guia-do-aluno.md", roadmap, ok, outro):
                    self.assertIn(termo, texto)

    def test_agents_tmpl(self):
        texto = ler(AGENTS_TMPL)
        for termo in PREPARO + ("sdd-kb", "sdd/bin/kb-dominios.py", "um OK só", "{{VENDORS}}"):
            with self.subTest(termo=termo):
                self.assertIn(termo, texto)


class PorQueCadaRegra(unittest.TestCase):
    def test_secao_com_itens(self):
        for s in COM_SECAO:
            texto = ler(RAIZ / ".agents/skills" / s / "SKILL.md")
            with self.subTest(skill=s):
                titulos = list(TITULO_SECAO.finditer(texto))
                self.assertEqual(len(titulos), 1, "título 'Por que cada regra existe'")
                resto = texto[titulos[0].end():]
                fim = re.search(r"(?m)^## ", resto)
                corpo = resto[:fim.start()] if fim else resto
                itens = [ln for ln in corpo.splitlines() if ITEM_SECAO.match(ln)]
                self.assertGreaterEqual(len(itens), 3, "itens '- **regra** — motivo'")
                if s in FASE:
                    self.assertTrue(fim and resto[fim.start():].startswith("## Encerramento (obrigatório)"),
                                    "a seção vem logo antes de '## Encerramento (obrigatório)'")


if __name__ == "__main__":
    unittest.main()
