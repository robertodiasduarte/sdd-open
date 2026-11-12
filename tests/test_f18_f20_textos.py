"""F18/F20 (AT-009): onde a segurança encosta em cada fase, nos textos das skills e dos templates."""
from __future__ import annotations

import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def skill(nome: str) -> str:
    return ler(".agents/skills/%s/SKILL.md" % nome)


class Versoes(unittest.TestCase):
    def test_versoes_e_linha_de_identificacao(self):
        for nome, versao in (("sdd-seguranca", "1.0.1"), ("sdd-brainstorm", "2.3.1"), ("sdd-define", "2.6.1"),
                             ("sdd-design", "2.6.0"), ("sdd-build", "2.9.1"), ("sdd-release", "2.11.1")):
            texto = skill(nome)
            with self.subTest(skill=nome):
                self.assertIn('version: "%s"' % versao, texto)
                self.assertIn("`%s v%s · nov/2026" % (nome, versao), texto)


class Seguranca(unittest.TestCase):
    def setUp(self):
        self.texto = skill("sdd-seguranca")

    def test_quatro_modos(self):
        for termo in ("### Modo Define", "### Modo checklist antes de publicar", "### Modo app publicado",
                      "### Modo incidente", "references/INCIDENTE.md"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_na_em_uma_linha_e_ate_5_por_rodada(self):
        for termo in ("**Nenhum gatilho** ⇒", "`✅ segurança: N.A. — <motivo>`", "Até **5 por rodada**",
                      "Nunca \"aplicar todos\"", "**aplicar** (recomendado), **recusar** (com motivo), **adiar**, **não sei**"):
            with self.subTest(termo=termo):
                self.assertIn(termo, self.texto)

    def test_linha_seguranca_e_registro_sem_trava(self):
        self.assertIn("`| **Segurança** | <a> aplicados (Snn, …) · <r> recusados (Snn, …) · <d> adiados (Snn, …) | <data> |`",
                      self.texto)
        self.assertIn("A linha é registro, não trava", self.texto)

    def test_incidente_fecha_a_porta_primeiro(self):
        inc = ler(".agents/skills/sdd-seguranca/references/INCIDENTE.md")
        self.assertLess(inc.index("## 1. Fechar a porta"), inc.index("## 2. Preservar a evidência"))
        self.assertIn("Apagar o arquivo **não** basta", inc)
        self.assertIn("não** é parecer jurídico", inc)


class Fases(unittest.TestCase):
    def test_brainstorm_pergunta_o_perfil_de_risco(self):
        t = skill("sdd-brainstorm")
        self.assertIn("**Quem pode ver cada dado? Quem pode mudar? Quanto alguém pode pedir?**", t)
        self.assertIn("## Perfil de risco", ler("sdd/templates/BRAINSTORM_TEMPLATE.md"))

    def test_define_tem_o_passo_12_sem_trava(self):
        t = skill("sdd-define")
        for termo in ("### 12. Segurança (sempre, nesta sessão)", "**não trava** o gate", "| 8 | Segurança | 12 |",
                      "### Segurança` de `## Clarifications`"):
            with self.subTest(termo=termo):
                self.assertIn(termo, t)
        self.assertIn("| **Segurança** | {pendente — o passo 12 escreve:", ler("sdd/templates/DEFINE_TEMPLATE.md"))

    def test_design_tem_a_secao_com_os_5_itens(self):
        self.assertIn("### 5.7. Segurança", skill("sdd-design"))
        tmpl = ler("sdd/templates/DESIGN_TEMPLATE.md")
        self.assertNotIn("## Security Considerations", tmpl)
        for item in ("1. **Onde mora cada segredo:**", "2. **Quem vê e quem muda cada tabela (RLS):**",
                     "3. **Credencial de cada agente ou integração:**", "4. **Cabeçalhos e CORS do host:**",
                     "5. **Itens aplicados no Define:**"):
            with self.subTest(item=item):
                self.assertIn(item, tmpl)

    def test_build_le_as_regras_e_relata_recusados_e_adiados(self):
        t = skill("sdd-build")
        self.assertIn("`bash sdd/bin/seguranca-varredura.sh --regras`", t)
        self.assertIn("Segurança (os itens recusados e adiados", t)
        self.assertIn("## Segurança", ler("sdd/templates/BUILD_REPORT_TEMPLATE.md"))

    def test_release_varre_em_toda_publicacao(self):
        t = skill("sdd-release")
        for termo in ("10. **Segurança (varredura, em toda publicação):**",
                      "`bash sdd/bin/seguranca-varredura.sh --saida sdd/reports/evidence/{F}/SEGURANCA.log`",
                      "**0c. Segurança (modelo — em toda publicação, com a lista fixa).**",
                      "`bash sdd/bin/seguranca-varredura.sh --checklist`",
                      "bloqueio da varredura de segurança (S01, S11)", "**Segurança:** <varredura:",
                      "`/sdd-seguranca app <URL>`", "Fase 0a.10: varredura de segurança `2` · `64`"):
            with self.subTest(termo=termo):
                self.assertIn(termo, t)
        self.assertNotIn("só se o diff toca auth, dados, permissões, rota pública", t)
        ref = ler(".agents/skills/sdd-release/references/seguranca.md")
        for termo in ("## 0a, item 10 — varredura (em toda publicação)", "Segurança real", "## 0c — passada do modelo",
                      "**cumprido**, **não cumprido** (com `arquivo:linha`) ou **não se aplica a este diff**",
                      "Chave real nunca se dispensa", "modo incidente da `sdd-seguranca`"):
            with self.subTest(termo=termo):
                self.assertIn(termo.replace("Segurança real", "**já vazou**"), ref)

    def test_agents_tmpl_tem_a_secao_e_a_skill(self):
        t = ler("AGENTS.md.tmpl")
        self.assertIn("### Segurança ao construir", t)
        self.assertIn("\n{{SEGURANCA}}\n", t)
        self.assertIn("`sdd-seguranca`", t)


if __name__ == "__main__":
    unittest.main()
