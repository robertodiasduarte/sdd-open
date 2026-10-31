"""Contrato entre o checar.sh --frente e a sdd-new-session, e o que as skills portadas do starter não trazem.

O pré-voo da sdd-new-session roda o checar.sh --frente e traduz cada achado pela tabela "Como traduzir
cada achado". Script e tabela moram em arquivos diferentes: este teste acusa a mensagem de bloqueio nova
sem linha na tabela e a linha cujo trecho não aparece mais em mensagem nenhuma. A 1ª coluna da tabela
traz, entre crases, um trecho literal (sem variável) da mensagem do script.

A sdd-new-session é texto lido pelo agente: o teste confere o contrato escrito (as regras estão lá), não
a obediência do agente.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILLS = RAIZ / ".agents/skills"
CHECAR = SKILLS / "sdd-checar-ambiente/scripts/checar.sh"
SESSAO = SKILLS / "sdd-new-session/SKILL.md"
PORTADAS = ("sdd-checar-ambiente", "sdd-higiene-dado", "sdd-iniciar-repo", "sdd-kb")
MSG = re.compile(r'(?:add_(?:impede|remoto)\s+|MSG=)"((?:[^"\\]|\\.)*)"')


def mensagens_do_frente() -> list[str]:
    """Mensagens de bloqueio que o --frente pode emitir: seções 1 a 3 do checar.sh, menos a identidade
    do git (só no modo normal). Os comentários-marcador fazem parte do contrato."""
    texto = CHECAR.read_text(encoding="utf-8")
    ini, fim = texto.index("# ── 1. onde estou"), texto.index("# ── 4. frentes")
    regiao = texto[ini:fim]
    a, b = regiao.index("# ── 3. git utilizável"), regiao.index("# Alcance do origin")
    # add_impede "${MSG}" é só a variável: o texto vem das atribuições MSG="…", que já entram na lista.
    return [m for m in MSG.findall(regiao[:a] + regiao[b:]) if not re.fullmatch(r"\$\{\w+\}", m)]


def trechos_da_tabela() -> list[str]:
    secao = SESSAO.read_text(encoding="utf-8").split("### Como traduzir cada achado", 1)[1]
    secao = re.split(r"\n#{2,3} ", secao, 1)[0]
    linhas = [l for l in secao.splitlines() if l.startswith("|") and not l.startswith("|---")]
    return [m for l in linhas[1:] for m in re.findall(r"`([^`]+)`", l.split("|")[1])]


class Matriz(unittest.TestCase):
    def test_o_script_tem_as_mensagens_esperadas(self):
        # Controle: se a extração quebrar (marcador renomeado), o teste de cobertura passaria vazio.
        msgs = mensagens_do_frente()
        self.assertGreaterEqual(len(msgs), 15, msgs)
        self.assertFalse(any("nome configurado" in m or "e-mail configurado" in m for m in msgs),
                         "identidade do git é do modo normal e não pode entrar na matriz do --frente")

    def test_toda_mensagem_de_bloqueio_tem_linha_na_tabela(self):
        trechos = trechos_da_tabela()
        sem_linha = [m for m in mensagens_do_frente() if not any(t in m for t in trechos)]
        self.assertEqual(sem_linha, [], "mensagem do checar.sh --frente sem tradução na sdd-new-session")

    def test_todo_trecho_da_tabela_existe_no_script(self):
        msgs = mensagens_do_frente()
        orfaos = [t for t in trechos_da_tabela() if not any(t in m for m in msgs)]
        self.assertEqual(orfaos, [], "linha da tabela cujo trecho não aparece em mensagem do script")

    def test_trechos_sao_literais_e_longos(self):
        for t in trechos_da_tabela():
            with self.subTest(trecho=t):
                self.assertGreaterEqual(len(t), 12)
                self.assertNotIn("$", t)


class ContratoDaNewSession(unittest.TestCase):
    def setUp(self):
        self.texto = SESSAO.read_text(encoding="utf-8")

    def test_versao(self):
        self.assertIn('version: "1.3.0"', self.texto)

    def test_pre_voo_pelo_script_com_os_dois_exits_e_o_fallback(self):
        for frase in ("checar.sh --frente", "**exit 1**", "**exit 0** com a linha `✅ Pronto para abrir a frente",
                      "### Pré-voo à mão (sem bash ou sem o script)", "Nada foi criado."):
            with self.subTest(frase=frase):
                self.assertIn(frase, self.texto)

    def test_descoberta_grava_so_slot_vazio_na_frente_com_evidencia(self):
        for frase in ("sdd/config.yaml da", "só slot vazio", "# descoberto por sdd-new-session (AAAA-MM-DD):",
                      "**não commite**", "nunca no do checkout principal", "**não grave**"):
            with self.subTest(frase=frase):
                self.assertIn(frase, self.texto)

    def test_default_branch_divergente_para(self):
        self.assertIsNotNone(re.search(r"Cheio e \*\*diverge\*\* da do remoto.{0,200}?\*\*pare e pergunte\*\*",
                                       self.texto, re.S), "a regra do default_branch divergente sumiu")

    def test_test_e_lint_so_com_evidencia_literal_na_ordem(self):
        self.assertIn("**evidência literal**", self.texto)
        i = self.texto.index(".github/workflows/")
        j = self.texto.index("`scripts.test` do `package.json`")
        k = self.texto.index("alvo `test:`")
        self.assertLess(i, j)
        self.assertLess(j, k)
        self.assertIn('echo "Error: no test specified" && exit 1', self.texto)


class Portadas(unittest.TestCase):
    """As 4 skills vindas do sdd-starter não citam o starter nem trazem o que o doctor usa para detectá-lo."""

    def test_sem_agents_openai_yaml(self):
        # O doctor avisa "skills do sdd-starter detectadas" quando acha agents/openai.yaml.
        for s in PORTADAS:
            with self.subTest(skill=s):
                self.assertTrue((SKILLS / s / "SKILL.md").is_file())
                self.assertEqual(list((SKILLS / s).rglob("openai.yaml")), [])

    def test_sem_referencia_ao_starter(self):
        proibidos = ("sdd-starter", "npx skills add", "sdd/ambiente.md")
        achados = []
        for s in PORTADAS:
            for f in sorted((SKILLS / s).rglob("*")):
                if f.is_file():
                    texto = f.read_text(encoding="utf-8")
                    achados += [f"{f.relative_to(RAIZ)}: {p}" for p in proibidos if p in texto]
        self.assertEqual(achados, [])

    def test_sem_pasta_tests_na_skill(self):
        # Os testes ficam em tests/ na raiz: dentro da skill, o init e o sync os levariam ao usuário.
        for s in PORTADAS:
            with self.subTest(skill=s):
                self.assertFalse((SKILLS / s / "tests").exists())


if __name__ == "__main__":
    unittest.main()
