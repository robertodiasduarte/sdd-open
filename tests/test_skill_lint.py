"""Contrato do sdd/bin/skill-lint.py (spec Agent Skills): name = pasta, description ≤ 1024.

Com --conversa, também a camada "Como falar com o aluno": seção, tabela de etapas, 5 partes,
references/como-falar.md quando a seção manda lê-lo e as perguntas de decisão dos exemplos (1
recomendada e primeira, "não sei", nunca "Outro", Próximo passo ≤ 100 caracteres). As fixtures de
sdd/fixtures/conversa/ reprovam uma regra cada; conversa-controle passa.

Exit 0 = todos válidos · 1 = algum inválido · 64 = uso.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/skill-lint.py"
FIXTURES = RAIZ / "sdd/fixtures/conversa"
# fixture → trecho que a mensagem de erro tem de trazer
REPROVAM = {
    "conversa-sem-secao": "Como falar com o aluno",
    "conversa-sem-como-falar": "references/como-falar.md, e o arquivo não existe",
    "conversa-sem-recomendado": "(recomendado)",
    "conversa-dois-recomendados": "(recomendado)",
    "conversa-sem-nao-sei": "não sei",
    "conversa-com-outro": "Outro",
}


def skill(name: str, description: str) -> str:
    return "---\nname: " + name + "\ndescription: " + description + "\nlicense: MIT\n---\n\n# Corpo\n"


class SkillLint(Sandbox):
    def lint(self, pasta: str, texto: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "skills/" + pasta + "/SKILL.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def test_as_16_skills_reais_passam(self):
        skills = sorted((RAIZ / ".agents/skills").glob("sdd-*/SKILL.md"))
        self.assertEqual(len(skills), 16, [s.parent.name for s in skills])
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, *skills], RAIZ)
        self.assertEqual(rc, 0, out + err)

    def test_skill_minima_valida(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "Faz uma coisa util."))
        self.assertEqual(rc, 0, out)

    def test_description_com_1024_caracteres_passa(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "a" * 1024))
        self.assertEqual(rc, 0, out)

    def test_description_com_1025_caracteres_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "a" * 1025))
        self.assertEqual(rc, 1, out)
        self.assertIn("RESULTADO: VERMELHO", out)

    def test_name_diferente_da_pasta_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-outro-nome", "Faz uma coisa util."))
        self.assertEqual(rc, 1, out)

    def test_sem_frontmatter_reprova(self):
        rc, out = self.lint("sdd-exemplo", "# Só corpo, sem frontmatter\n")
        self.assertEqual(rc, 1, out)

    def test_description_vazia_reprova(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", '""'))
        self.assertEqual(rc, 1, out)

    def test_as_16_skills_reais_passam_com_conversa(self):
        skills = sorted((RAIZ / ".agents/skills").glob("sdd-*/SKILL.md"))
        self.assertEqual(len(skills), 16)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversa", *skills], RAIZ)
        self.assertEqual(rc, 0, out + err)

    def test_sem_flag_skill_sem_secao_passa(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "Faz uma coisa util."))
        self.assertEqual(rc, 0, out)
        self.assertNotIn("Como falar", out)

    def test_flag_desconhecida_e_64(self):
        p = self.escreve(self.tmp, "skills/sdd-exemplo/SKILL.md", skill("sdd-exemplo", "Faz."))
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversas", p], self.tmp)
        self.assertEqual(rc, 64, out + err)

    def test_controle_passa_com_conversa(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversa",
                                  FIXTURES / "conversa-controle/SKILL.md"], RAIZ)
        self.assertEqual(rc, 0, out + err)

    def test_cada_fixture_reprova_pelo_seu_motivo(self):
        for nome, trecho in REPROVAM.items():
            with self.subTest(fixture=nome):
                rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversa",
                                          FIXTURES / nome / "SKILL.md"], RAIZ)
                self.assertEqual(rc, 1, out + err)
                self.assertIn(trecho, err)
                self.assertIn(nome, err)
                self.assertIn("RESULTADO: VERMELHO", err)

    def test_fixtures_passam_sem_conversa(self):
        # O frontmatter das fixtures é válido: elas reprovam só pela camada.
        for nome in ["conversa-controle", *REPROVAM]:
            with self.subTest(fixture=nome):
                rc, out, err = self.roda([PYTHON, "-B", SCRIPT, FIXTURES / nome / "SKILL.md"], RAIZ)
                self.assertEqual(rc, 0, out + err)

    def mutado(self, arquivo: str, de: str, para: str) -> tuple[int, str]:
        """Cópia do controle com uma troca em SKILL.md ou references/como-falar.md."""
        alvo = Path(tempfile.mkdtemp(dir=str(self.tmp))) / "conversa-controle"
        shutil.copytree(FIXTURES / "conversa-controle", alvo)
        p = alvo / arquivo
        texto = p.read_text(encoding="utf-8")
        self.assertIn(de, texto)
        p.write_text(texto.replace(de, para, 1), encoding="utf-8")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversa", alvo / "SKILL.md"], self.tmp)
        return rc, out + err

    def test_secao_repetida_reprova(self):
        rc, out = self.mutado("SKILL.md", "## Entrada", "## Como falar com o aluno\n\n## Entrada")
        self.assertEqual(rc, 1, out)
        self.assertIn("repetida", out)

    def test_secao_sem_tabela_de_etapas_reprova(self):
        rc, out = self.mutado("SKILL.md", "| Etapa |", "| Fase |")
        self.assertEqual(rc, 1, out)
        self.assertIn("Etapa", out)

    def test_secao_sem_uma_das_5_partes_reprova(self):
        rc, out = self.mutado("SKILL.md", "**Sua decisão**", "**Decisão**")
        self.assertEqual(rc, 1, out)
        self.assertIn("Sua decisão", out)

    def test_recomendada_fora_do_primeiro_lugar_reprova(self):
        alvo = self.tmp / "x"
        shutil.copytree(FIXTURES / "conversa-controle", alvo / "conversa-controle")
        p = alvo / "conversa-controle/references/como-falar.md"
        texto = p.read_text(encoding="utf-8")
        texto = texto.replace("- **sim** (recomendado) —", "- **sim** —", 1)
        texto = texto.replace("- **não** —", "- **não** (recomendado) —", 1)
        p.write_text(texto, encoding="utf-8")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--conversa",
                                  alvo / "conversa-controle/SKILL.md"], self.tmp)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("primeira", out + err)

    def test_proximo_passo_com_mais_de_100_caracteres_reprova(self):
        rc, out = self.mutado("references/como-falar.md", "**Próximo passo** — ",
                              "**Próximo passo** — " + "a" * 101 + " ")
        self.assertEqual(rc, 1, out)
        self.assertIn("100", out)

    def test_como_falar_sem_pergunta_de_decisao_reprova(self):
        rc, out = self.mutado("references/como-falar.md", "?**", "**")
        self.assertEqual(rc, 1, out)
        self.assertIn("nenhuma pergunta", out)

    def test_opcao_em_duas_linhas_nao_esconde_as_seguintes(self):
        # A opção que quebra em 2 linhas não pode encerrar a lista: o "não sei" vem depois dela.
        rc, out = self.mutado("references/como-falar.md", "as 12 linhas foram lidas sem erro.",
                              "as 12 linhas foram\n  lidas sem erro.")
        self.assertEqual(rc, 0, out)
        rc, out = self.mutado("references/como-falar.md", "- **não sei** —", "- **talvez** —")
        self.assertEqual(rc, 1, out)

    def test_opcoes_depois_de_linha_em_branco_ou_com_asterisco_sao_conferidas(self):
        # markdownlint põe linha em branco antes da lista; "*" também é marcador de lista.
        for marca in ("-", "*"):
            with self.subTest(marca=marca):
                rc, out = self.mutado("references/como-falar.md", "## Exemplo",
                                      "**Posso apagar a pasta?**\n\n" + marca + " **Outro** — você descreve.\n"
                                      + marca + " **sim** — apago.\n\n## Exemplo")
                self.assertEqual(rc, 1, out)
                self.assertIn("Posso apagar a pasta?", out)

    def test_pergunta_em_citacao_com_linha_vazia_e_conferida(self):
        rc, out = self.mutado("references/como-falar.md", "## Exemplo",
                              "> **Posso apagar a pasta?**\n>\n> - **Outro** — você descreve.\n"
                              "> - **sim** — apago.\n\n## Exemplo")
        self.assertEqual(rc, 1, out)
        self.assertIn("Posso apagar a pasta?", out)

    def test_outros_no_plural_reprova(self):
        rc, out = self.mutado("references/como-falar.md", "- **não** —", "- **Outros** —")
        self.assertEqual(rc, 1, out)

    def test_outro_com_complemento_reprova(self):
        rc, out = self.mutado("references/como-falar.md", "- **não** —", "- **Outro (descreva)** —")
        self.assertEqual(rc, 1, out)
        self.assertIn("Outro", out)

    def test_proximo_passo_com_dois_pontos_ou_em_citacao_tambem_tem_limite(self):
        for forma in ("**Próximo passo:** ", "> **Próximo passo** — "):
            with self.subTest(forma=forma):
                rc, out = self.mutado("references/como-falar.md", "## Exemplo",
                                      forma + "b" * 150 + "\n\n## Exemplo")
                self.assertEqual(rc, 1, out)
                self.assertIn("100", out)

    def test_secao_dentro_de_bloco_de_codigo_nao_conta(self):
        rc, out = self.mutado("SKILL.md", "## Entrada",
                              "```markdown\n## Como falar com o aluno\n```\n\n## Entrada")
        self.assertEqual(rc, 0, out)

    def test_sem_flag_mensagem_de_frontmatter_nao_muda(self):
        rc, out = self.lint("sdd-exemplo", skill("sdd-exemplo", "a" * 1025))
        self.assertEqual(rc, 1, out)
        self.assertIn("→ corrija o frontmatter apontado acima (spec: agentskills.io/specification)", out)

    def test_pergunta_aberta_sem_opcoes_nao_e_conferida(self):
        rc, out = self.mutado("references/como-falar.md", "## Exemplo",
                              "**Qual é o nome do cliente?** Responda com o nome, ou \"não sei\".\n\n## Exemplo")
        self.assertEqual(rc, 0, out)

    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.tmp)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
