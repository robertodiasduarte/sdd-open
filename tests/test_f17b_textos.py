"""F17b (AT-004, AT-005, AT-007, parte do AT-010): os textos que a etapa 2 do starter gerado acrescenta ao Open."""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


class ModoIniciante(unittest.TestCase):
    """AT-004: a release curta (GitHub + Vercel), com 1 OK e sem token."""

    def setUp(self):
        self.m = ler(".agents/skills/sdd-release/references/MODO_INICIANTE.md")

    def test_um_ponto_de_aprovacao(self):
        self.assertIn("## Fase 2 — O único ponto de parada", self.m)
        self.assertEqual(len(re.findall(r"^\*\*Posso publicar\?\*\*", self.m, re.M)), 1)
        self.assertIn("**Nunca um segundo ponto de parada**", self.m)

    def test_nenhum_token(self):
        for proibido in ("vercel login", "VERCEL_TOKEN", "--with-token", "gh auth login", "cole o token",
                         "cole a chave", "vercel deploy"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, self.m)
        self.assertIn("Nenhum token é pedido", self.m)

    def test_confere_a_vercel_pelo_status_e_diz_a_url(self):
        self.assertIn('gh api "repos/{owner}/{repo}/commits/<SHA publicado>/status"', self.m)
        self.assertIn("startswith(\"Vercel\")", self.m)
        self.assertIn("environment_url", self.m)
        self.assertIn("gh pr checks", self.m)
        self.assertIn("vercel.com/docs/git/vercel-for-github", self.m)   # a fonte do que é inferência

    def test_falha_da_vercel_nao_refaz_o_deploy(self):
        self.assertIn("**Não\n     refaça o deploy por conta própria**", self.m)
        self.assertIn("nunca \"no ar\"", self.m)

    def test_o_caminho_do_workflow_continua(self):
        self.assertIn("gh run list --commit <SHA publicado>", self.m)
        self.assertIn("nunca `gh run rerun` de um run antigo", self.m)

    def test_sem_consultar_o_github_nunca_conclui_que_o_push_nao_publica(self):
        # revisão, rodada 1, R2: sem gh utilizável e sem vercel.json, o agente caía em "Nenhum" e dizia que o push não publica
        self.assertIn("nunca conclua \"Nenhum\"", self.m)
        self.assertIn("não confirmei: não consegui consultar o GitHub", self.m)

    def test_duas_fontes_independentes_para_saber_se_a_vercel_publica(self):
        # LM-024: o arquivo do projeto e o status do commit; a divergência tem resposta escrita
        self.assertIn("Só o arquivo ⇒", self.m)
        self.assertIn("Só o status ⇒", self.m)

    def test_o_open_aponta_o_modo_e_a_release_fica_no_teto(self):
        s = ler(".agents/skills/sdd-release/SKILL.md")
        self.assertIn("**Projeto sem `sdd/bin/`**", s)
        self.assertIn("`references/MODO_INICIANTE.md`", s)
        self.assertLessEqual(len(s.splitlines()), 500)

    def test_identificacao_do_modo_igual_a_do_skill_md(self):
        s = ler(".agents/skills/sdd-release/SKILL.md")
        ident = [ln for ln in s.splitlines() if ln.startswith("`sdd-release v")]
        self.assertEqual(len(ident), 1)
        self.assertEqual(self.m.count(ident[0]), 1)

    def test_description_do_modo_cabe_no_upload(self):
        desc = re.search(r'^description: "(.*)"$', self.m, re.M).group(1)
        self.assertLessEqual(len(desc), 1024)
        self.assertIn("## Como falar com o aluno", self.m)


class SemTerminal(unittest.TestCase):
    """AT-005: brainstorm, handoff e governança com o caminho sem terminal."""

    def secao(self, skill: str) -> str:
        s = ler(".agents/skills/%s/SKILL.md" % skill)
        ini = s.index("## Sem terminal")
        return s[ini:s.index("\n## ", ini + 5)]

    def test_brainstorm(self):
        b = self.secao("sdd-brainstorm")
        for trecho in ("Entregue o documento inteiro no chat", "nada foi gravado", "Nunca diga que gravou",
                       "(fornecido)", "(observado)", "(inferido)", "Não sobrescreva em silêncio",
                       "YAGNI com zero cortes vale"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, b)

    def test_handoff(self):
        h = self.secao("sdd-handoff")
        for trecho in ("**continuar**", "**entregar**", "não bloqueia", "🐛 bug fix", "✨ melhoria",
                       "\"nenhuma\" escrito", "**não foi gravado**", "não tem linha Verify Gate na ficha"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, h)

    def test_governanca(self):
        g = self.secao("sdd-governanca")
        for trecho in ("**Quando não usar:**", "**Prova sem script:**", "`prova_manual`", "Nenhum script é pedido",
                       "**Onde entregar:**", "nada foi gravado"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, g)
        s = ler(".agents/skills/sdd-governanca/SKILL.md")
        self.assertIn("**Com Verify Gate por comando no DEFINE, a prova de cada lacuna aplicada é um script.**", s)
        self.assertNotIn("**Nesta porta, a prova de cada lacuna aplicada é um script.**", s)
        # avaliador, ciclo 1, A1 e A3: o checklist e o brief do revisor também condicionam o script ao gate
        self.assertIn("com Verify Gate por comando, também o script em", s)
        self.assertNotIn("[ ] Aplicados viram AT no DEFINE + script", s)
        # avaliador, ciclo 2, achado 1: o procedimento e o molde do relatório também condicionam o script
        self.assertIn("com Verify Gate por\n   comando no DEFINE, também o `prova_script`",
                      ler(".agents/skills/sdd-governanca/references/PROCEDIMENTO.md"))
        self.assertIn("com Verify Gate por comando no DEFINE, também a prova_script",
                      ler(".agents/skills/sdd-governanca/assets/GOVERNANCA_REVIEW_TEMPLATE.md"))
        rev = ler(".agents/skills/sdd-governanca/references/revisor.md")
        self.assertIn("o `prova_manual` sempre; com Verify Gate por comando no DEFINE", rev)


class CaminhoCurto(unittest.TestCase):
    """Avaliador, ciclo 2, achado 2: a forma curta `fragments/X.md` não é reescrita pelo gerador e aponta o nada no starter."""

    def test_skills_geradas_citam_o_molde_pelo_caminho_inteiro(self):
        lista = [ln.strip() for ln in ler("scripts/starter/lista.txt").splitlines() if ln.strip() and not ln.startswith("#")]
        for skill in lista:
            for p in sorted((RAIZ / ".agents/skills" / skill).rglob("*.md")):
                if p.name == "CHANGELOG.md":
                    continue
                with self.subTest(arquivo=str(p.relative_to(RAIZ))):
                    self.assertIsNone(re.search(r"(?<![\w/])fragments/[A-Z_]+\.md", p.read_text(encoding="utf-8")))


class UxReviewBuilder(unittest.TestCase):
    """AT-007: a 22ª skill do Open e a sdd-ux-review lendo o padrão do projeto."""

    def test_a_skill_mora_no_open(self):
        s = ler(".agents/skills/ux-review-builder/SKILL.md")
        self.assertIn('version: "1.5.0"', s)
        self.assertIn("`ux-review-builder v1.5.0 · nov/2026 · versão atual: "
                      "https://github.com/robertodiasduarte/sdd-open/releases/latest`", s)
        self.assertIn("## Como falar com o aluno", s)
        self.assertTrue((RAIZ / ".agents/skills/ux-review-builder/references/como-falar.md").is_file())
        self.assertFalse((RAIZ / ".agents/skills/ux-review-builder/agents").exists())
        self.assertIn("`sdd/UX_STANDARD.md`", s)

    def test_a_tabela_do_gerador_tem_o_botao(self):
        tsv = ler("scripts/starter/openai.tsv")
        self.assertIn("ux-review-builder\tUX Review Builder\t", tsv)

    def test_sdd_ux_review_le_o_padrao(self):
        s = ler(".agents/skills/sdd-ux-review/SKILL.md")
        self.assertIn("Se existir `sdd/UX_STANDARD.md`", s)
        self.assertIn("nunca troca silenciosa do padrão", s)


if __name__ == "__main__":
    unittest.main()
