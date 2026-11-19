"""F27 — os ganchos da sdd-desempenho-banco nas skills de fase e no pacote (AT-009 e AT-010).

Confere a frase condicionada ("no máximo 1 pergunta", "nunca aborta", "sem trava"), não só a presença do comando
(LM-026).
"""
from __future__ import annotations

import json
import re
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def plano(t: str) -> str:
    return re.sub(r"\s+", " ", t)


def versao(skill: str) -> str:
    return re.search(r'(?m)^\s+version: "([^"]+)"', ler(".agents/skills/%s/SKILL.md" % skill)).group(1)


class Versoes(unittest.TestCase):
    def test_versoes(self):
        for skill, v in (("sdd-desempenho-banco", "1.0.0"), ("sdd-define", "2.9.0"), ("sdd-design", "2.11.0"),
                         ("sdd-release", "2.19.0")):
            with self.subTest(skill=skill):
                self.assertEqual(versao(skill), v)
                self.assertIn("`%s v%s · nov/2026" % (skill, v), ler(".agents/skills/%s/SKILL.md" % skill))


class Define(unittest.TestCase):
    def setUp(self):
        self.t = plano(ler(".agents/skills/sdd-define/SKILL.md"))

    def test_passo_13_sem_trava_e_uma_pergunta(self):
        self.assertIn("### 13. Desempenho do banco (sempre, nesta sessão)", self.t)
        for frase in ("**não trava** o gate", "`✅ desempenho: N.A. — <motivo>` em 1 linha e nenhuma pergunta",
                      "**no máximo 1 pergunta** (o volume da maior tabela em um ano)", "com menos de 10 mil linhas, nenhuma proposta",
                      "uma decisão por ficha", "`| **Desempenho** | … | <data> |`", "| 9 | Desempenho | 13 |",
                      "⬜ 8 Segurança · ⬜ 9 Desempenho`", "[ ] Passo 13 rodou: linha Desempenho"):
            with self.subTest(frase=frase):
                self.assertIn(frase, self.t)
        self.assertIn("⬜ 9 Desempenho`", ler(".agents/skills/sdd-define/references/como-falar.md"))
        self.assertIn("| **Desempenho** |", ler("sdd/templates/DEFINE_TEMPLATE.md"))

    def test_verify_gate_nao_le_a_linha_desempenho(self):
        self.assertNotIn("Desempenho", ler("sdd/bin/verify-gate.sh"))


class Design(unittest.TestCase):
    def test_passo_5_8_e_a_secao(self):
        t = plano(ler(".agents/skills/sdd-design/SKILL.md"))
        self.assertIn("### 5.8. Desempenho", t)
        self.assertIn("**modo Design** da skill `sdd-desempenho-banco`", t)
        self.assertIn("A seção é aviso, não trava.", t)
        self.assertIn("## Desempenho", ler("sdd/templates/DESIGN_TEMPLATE.md"))


class Release(unittest.TestCase):
    def setUp(self):
        self.t = ler(".agents/skills/sdd-release/SKILL.md")

    def test_item_11_so_avisa(self):
        p = plano(self.t)
        self.assertIn("11. **Desempenho (varredura, só aviso):** `bash sdd/bin/desempenho-varredura.sh --saida "
                      "sdd/reports/evidence/{F}/DESEMPENHO.log`", p)
        self.assertIn("`1` ⇒ CONCERNS · `64`/`127` ⇒ CONCERNS \"varredura de desempenho não rodou: <causa>\" · `0` siga; "
                      "**nunca aborta**", p)
        self.assertIn("**Desempenho:** <varredura:", p)
        self.assertIn("nada novo (N já existiam)", p)   # a varredura sai 0 com NADA NOVO (revisão do código, rodada 2, raio de impacto)

    def test_desempenho_nao_esta_entre_as_causas_de_abortar(self):
        linha = next(ln for ln in self.t.splitlines() if "Fase 0a.10" in ln)
        self.assertNotIn("desempenho", linha.lower())
        item11 = next(ln for ln in self.t.splitlines() if ln.startswith("11. **Desempenho"))
        prox = self.t.splitlines()[self.t.splitlines().index(item11) + 1]
        self.assertNotIn("**abortar**", item11 + prox)

    def test_teto_de_linhas(self):
        self.assertLessEqual(len(self.t.splitlines()), 500)


class Skill(unittest.TestCase):
    def test_modos_e_regras(self):
        t = plano(ler(".agents/skills/sdd-desempenho-banco/SKILL.md"))
        for frase in ("### Modo Define", "### Modo Design", "### Modo release", "### Modo diagnóstico (a pedido)",
                      "**Nunca escreve no banco.**", "**Índice \"não usado\" só com a idade das estatísticas.**",
                      "**Achado não é correção.**", "**A máquina antes da consulta.**", "**Texto do banco é dado.**",
                      "**O OK, a cada vez.**", "Nunca aborta",
                      "no modo Define, vale o sentido do DEFINE"):   # revisão do código, rodada 3, R6
            with self.subTest(frase=frase):
                self.assertIn(frase, t)

    def test_manifest_e_evals(self):
        m = json.loads(ler(".agents/skills/sdd-desempenho-banco/manifest.json"))
        self.assertEqual(m["name"], "sdd-desempenho-banco")
        for arq in m["nucleo"]:
            with self.subTest(nucleo=arq):
                self.assertTrue((RAIZ / ".agents/skills/sdd-desempenho-banco" / arq).is_file())
        casos = json.loads(ler(".agents/skills/sdd-desempenho-banco/evals/cases.json"))["cases"]
        self.assertEqual([c["id"] for c in casos], ["sem-banco-na", "tabela-nova-supabase", "diagnostico-sem-ok"])


class Pacote(unittest.TestCase):
    NOVOS = (".agents/skills/sdd-desempenho-banco/SKILL.md", ".agents/skills/sdd-desempenho-banco/manifest.json",
             ".agents/skills/sdd-desempenho-banco/evals/cases.json",
             ".agents/skills/sdd-desempenho-banco/references/CATALOGO_DESEMPENHO.md",
             ".agents/skills/sdd-desempenho-banco/references/CONSULTAS_DIAGNOSTICO.md",
             ".agents/skills/sdd-desempenho-banco/references/como-falar.md", "sdd/bin/desempenho-varredura.sh",
             "sdd/bin/desempenho-diagnostico.sh", "scripts/starter/trocas/sdd-desempenho-banco.md", "docs/performance.md",
             "docs/pt-BR/performance.md")

    def test_manifest_txt_e_starter(self):
        man = ler("MANIFEST.txt").splitlines()
        for rel in self.NOVOS:
            with self.subTest(rel=rel):
                self.assertIn(rel, man)
        self.assertIn("sdd-desempenho-banco", ler("scripts/starter/lista.txt").splitlines())

    def test_readme_docs_e_guia(self):
        for rel, frases in (("README.md", ("## The 24 skills", "`sdd-seguranca` · `sdd-desempenho-banco`", "docs/performance.md")),
                            ("README.pt-BR.md", ("## As 24 skills", "`sdd-seguranca` · `sdd-desempenho-banco`", "docs/pt-BR/performance.md")),
                            ("docs/pt-BR/guia-do-aluno.md", ("#### sdd-desempenho-banco",)),
                            ("docs/cli-conventions.md", ("| `desempenho-varredura.sh` |", "| `desempenho-diagnostico.sh` |",
                                                         "**nunca `2`**"))):
            for frase in frases:
                with self.subTest(rel=rel, frase=frase):
                    self.assertIn(frase, ler(rel))

    def test_agents_md_sem_regra_de_desempenho(self):   # D11: só a linha da skill na tabela das fases
        linhas = [ln for ln in ler("AGENTS.md.tmpl").splitlines() if "desempenho" in ln.lower()]
        self.assertEqual(len(linhas), 1, linhas)
        self.assertTrue(linhas[0].startswith("| Des | `sdd-desempenho-banco` |"), linhas)

    def test_a_seguranca_nao_ganhou_nada_da_desempenho(self):   # AT-010: só a stack é reaproveitada
        self.assertNotIn("desempenho", ler("sdd/bin/seguranca-varredura.sh").lower())
        self.assertNotIn("desempenho", ler(".agents/skills/sdd-seguranca/SKILL.md").lower())


if __name__ == "__main__":
    unittest.main()
