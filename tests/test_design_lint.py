"""Contrato do sdd/bin/design-lint.py: o DESIGN segue o template do sdd-open.

Títulos de decisão `### Decision N: <nome>` em sequência sob `## Key Decisions` (outras ferramentas
leem esses títulos), File Manifest com `**Total Files:**` igual ao número de linhas, dependências que
apontam para linhas existentes e sem ciclo, nenhum placeholder fora de código. Cada caso vermelho é a
fixture válida com uma troca.

Exit 0 = válido · 1 = violações · 64 = uso.
"""
from __future__ import annotations

import re
import unittest

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/design-lint.py"
FIXTURE = RAIZ / "sdd/fixtures/design/DESIGN_VALIDO.md"
L, R = chr(0x7B), chr(0x7D)  # chaves: o próprio DESIGN da F4 não pode tê-las em prosa

# caso → (trecho da fixture, troca, trecho esperado na mensagem)
CASOS = {
    "sem_key_decisions": ("## Key Decisions", "## Decisions", "Key Decisions"),
    "decisao_em_portugues": ("### Decision 2: ", "### Decisão 2: ", "Decision N"),
    "decisao_fora_de_sequencia": ("### Decision 2: ", "### Decision 3: ", "sequência"),
    "titulo_sem_nome": ("### Decision 1: Lint em Python", "### Decision 1:", "Decision N"),
    "total_errado": ("**Total Files:** 3", "**Total Files:** 4", "Total Files"),
    "dependencia_inexistente": ("| (general) | 1, 2 |", "| (general) | 1, 9 |", "9"),
    "ciclo": ("| Create | Lint | (general) | None |", "| Create | Lint | (general) | 3 |", "ciclo"),
    "placeholder_em_prosa": ("**Context:** o projeto", "**Context:** " + L + "contexto da decisão" + R, "placeholder"),
    "placeholder_maiusculo": ("**Context:** o projeto", "**Context:** " + L + "FEATURE_NAME" + R + " o projeto", "placeholder"),
    "depende_de_si_mesma": ("| (general) | 1, 2 |", "| (general) | 3 |", "si mesma"),
}


class DesignLint(Sandbox):
    def lint(self, texto: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "DESIGN_X.md", texto)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def test_fixture_valida_passa(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, FIXTURE], RAIZ)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("✅", out)

    def test_placeholder_dentro_de_codigo_nao_conta(self):
        texto = FIXTURE.read_text(encoding="utf-8")
        self.assertIn("```", texto)
        self.assertRegex(texto, "`[^`\n]*" + "\\" + L)  # há chave dentro de crase simples na fixture

    def test_cada_mutacao_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        for nome, (de, para, trecho) in CASOS.items():
            with self.subTest(caso=nome):
                self.assertIn(de, base)
                rc, out = self.lint(base.replace(de, para, 1))
                self.assertEqual(rc, 1, out)
                self.assertIn(trecho, out)
                self.assertIn("RESULTADO: VERMELHO", out)

    def test_sem_nenhuma_decisao_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        sem = "\n".join(l for l in base.splitlines() if not l.startswith("### Decision ")) + "\n"
        rc, out = self.lint(sem)
        self.assertEqual(rc, 1, out)
        self.assertIn("nenhuma '### Decision N: <nome>'", out)

    def test_aspas_angulares_em_prosa_passam(self):
        # « » é aspa comum em português; o template do DESIGN só usa chaves como placeholder.
        base = FIXTURE.read_text(encoding="utf-8")
        rc, out = self.lint(base.replace("**Context:** o projeto", "**Context:** o «contador» do projeto", 1))
        self.assertEqual(rc, 0, out)

    def test_manifest_sem_linhas_reprova(self):
        base = FIXTURE.read_text(encoding="utf-8")
        linhas = [l for l in base.splitlines() if not l.startswith(("| 1 |", "| 2 |", "| 3 |"))]
        rc, out = self.lint("\n".join(linhas) + "\n")
        self.assertEqual(rc, 1, out)
        self.assertIn("File Manifest", out)

    def test_arquivo_ilegivel_sai_1_com_resultado(self):
        p = self.tmp / "X.md"
        p.write_bytes(bytes([0xFF, 0xFE, 0x80]))
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("não consegui ler", err)
        self.assertIn("RESULTADO: VERMELHO", err)
        self.assertNotIn("Traceback", err)

    def test_sem_argumento_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT], self.tmp)
        self.assertEqual(rc, 64, out + err)

    def test_arquivo_ausente_e_64(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, self.tmp / "nao-existe.md"], self.tmp)
        self.assertEqual(rc, 64, out + err)


def preenchido(fragmento: str) -> str:
    """O fragmento como a fase Design o deixa: da seção em diante, com as chaves trocadas."""
    secao = fragmento[fragmento.index("## LLM Prompts"):]
    return re.sub(L + "[^" + L + R + "\n]*" + R, "x", secao)


class Prompts(Sandbox):
    """DEFINE F13 AT-016 a AT-018: o inventário de prompts, só quando a seção existe."""

    def setUp(self):
        super().setUp()
        self.base = FIXTURE.read_text(encoding="utf-8")
        self.secao = preenchido((RAIZ / "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md").read_text(encoding="utf-8"))

    def lint(self, secao: str) -> tuple[int, str]:
        p = self.escreve(self.tmp, "DESIGN_X.md", self.base + "\n" + secao)
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        return rc, out + err

    def reprova(self, secao: str, trecho: str):
        rc, out = self.lint(secao)
        self.assertEqual(rc, 1, out)
        self.assertIn(trecho, out)
        self.assertIn("mudou na v2.5.0", out)
        self.assertLess(out.index("mudou na v2.5.0"), out.index(trecho))
        self.assertIn("RESULTADO: VERMELHO", out)
        self.assertIn("LLM_PROMPTS_DESIGN.md", out.splitlines()[-1])
        self.assertRegex(out.splitlines()[-1], "^→ ")

    def test_fragmento_preenchido_passa(self):
        rc, out = self.lint(self.secao)
        self.assertEqual(rc, 0, out)

    def test_sem_a_secao_nada_muda(self):
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, FIXTURE], RAIZ)
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("v2.5.0", out + err)

    def test_secao_so_dentro_de_cerca_nao_conta(self):
        rc, out = self.lint("```text\n## LLM Prompts\nexemplo\n```\n")
        self.assertEqual(rc, 0, out)

    def test_cada_coluna_faltando(self):
        for coluna in ("Tipo", "Versão", "Completeness", "Refator de?"):
            with self.subTest(coluna=coluna):
                i = self.secao.index("| # | Nome |")
                j = self.secao.index("\n", i)
                cabecalho = self.secao[i:j]
                self.assertIn("| " + coluna + " |", cabecalho)
                sem = self.secao[:i] + cabecalho.replace("| " + coluna + " |", "| Outra |") + self.secao[j:]
                self.reprova(sem, "falta a coluna " + coluna)

    def test_cada_campo_faltando(self):
        for campo in ("Autônomo?", "Verification interna", "Eval mínimo pré-ship"):
            with self.subTest(campo=campo):
                linhas = [ln for ln in self.secao.splitlines() if not ln.startswith("| **" + campo + "**")]
                self.reprova("\n".join(linhas) + "\n", "Prompt 1 sem o campo " + campo)

    def test_campo_sem_valor(self):
        linhas = ["| **Autônomo?** |  |" if ln.startswith("| **Autônomo?**") else ln for ln in self.secao.splitlines()]
        self.reprova("\n".join(linhas) + "\n", "Prompt 1 sem o campo Autônomo?")

    def test_tipo_invalido(self):
        self.reprova(self.secao.replace("| one-shot | `x` |", "| outro | `x` |", 1), "Tipo 'outro'")
        self.reprova(self.secao.replace("| one-shot | `x` |", "| one-shot ou loop | `x` |", 1), "Tipo 'one-shot ou loop'")

    def test_tipo_com_crases_e_loop_valem(self):
        self.assertEqual(self.lint(self.secao.replace("| one-shot | `x` |", "| `loop` | `x` |", 1))[0], 0)

    def test_sem_linha_de_dados(self):
        linhas = [ln for ln in self.secao.splitlines() if not ln.startswith("| 1 | x |")]
        self.reprova("\n".join(linhas) + "\n", "nenhuma linha de prompt")

    def test_numero_de_blocos_diferente_do_de_linhas(self):
        i = self.secao.index("| 1 | x |")
        j = self.secao.index("\n", i)
        duas = self.secao[:j + 1] + self.secao[i:j].replace("| 1 |", "| 2 |", 1) + "\n" + self.secao[j + 1:]
        self.reprova(duas, "2 linha(s) no inventário e 1 bloco(s)")

    def test_campos_que_a_skill_do_laco_exige_em_tipo_loop(self):
        loop = self.secao.replace("| one-shot | `x` |", "| loop | `x` |", 1)
        self.assertEqual(self.lint(loop)[0], 0, "o fragmento já traz as 3 linhas")
        for campo in ("Intenção", "Perfil de risco dos efeitos", "Ground truth disponível"):
            with self.subTest(campo=campo):
                linhas = [ln for ln in loop.splitlines() if not ln.startswith("| **" + campo + "**")]
                self.reprova("\n".join(linhas) + "\n", "Prompt 1 sem o campo " + campo)
        # one-shot não precisa delas.
        linhas = [ln for ln in self.secao.splitlines() if not ln.startswith("| **Intenção**")]
        self.assertEqual(self.lint("\n".join(linhas) + "\n")[0], 0)

    def test_campo_com_traco_e_vazio(self):
        for valor in ("—", "–", "-", "---", "`—`", "**—**"):
            with self.subTest(valor=valor):
                linhas = ["| **Autônomo?** | %s |" % valor if ln.startswith("| **Autônomo?**") else ln
                          for ln in self.secao.splitlines()]
                self.reprova("\n".join(linhas) + "\n", "Prompt 1 sem o campo Autônomo?")

    def test_variacoes_do_titulo_nao_desligam_a_conferencia(self):
        for titulo in ("##  LLM Prompts", "## LLM Prompts (v1)", "## LLM Prompts: 1", "## LLM prompts", "## LLM Prompt",
                       "## 5. LLM Prompts", "## **LLM Prompts**", "## LLM Prompts — inventário", "## LLM Prompts - v1"):
            with self.subTest(titulo=titulo):
                self.reprova(titulo + "\n\nnada\n", "falta o subtítulo ### Inventário")

    def test_outra_secao_que_so_comeca_igual_nao_e_a_de_prompts(self):
        for titulo in ("## LLM Prompt Injection", "## LLM Prompt-Injection", "## LLM Prompts-Review", "## LLM Prompts Review",
                       "## LLM Promptness", "### LLM Prompts"):
            with self.subTest(titulo=titulo):
                rc, out = self.lint(titulo + "\n\nriscos\n")
                self.assertEqual(rc, 0, out)

    def test_titulo_com_palavras_a_mais_e_inventario_no_corpo_reprova(self):
        # AT-031: antes, o lint pulava a conferência em silêncio; com a seção de verdade, ele diz o título.
        for titulo in ("## LLM Prompts v2", "## LLM Prompts do sistema", "## LLM prompts de produção"):
            for corpo in ("### Inventário\n\n| # | Nome |\n", "#### Prompt 1: x\n", "| Tipo | Completeness |\n|---|---|\n"):
                with self.subTest(titulo=titulo, corpo=corpo):
                    rc, out = self.lint(titulo + "\n\n" + corpo)
                    self.assertEqual(rc, 1, out)
                    self.assertIn("tem palavras a mais", out)
                    self.assertIn(titulo, out)

    def test_titulo_com_palavras_a_mais_e_outro_assunto_passa(self):
        for titulo in ("## LLM Prompts Review", "## LLM Prompts v2", "## LLM prompts de produção"):
            with self.subTest(titulo=titulo):
                rc, out = self.lint(titulo + "\n\nriscos, sem nenhuma tabela\n")
                self.assertEqual(rc, 0, out)

    def test_prefixo_numerado_de_varios_niveis_e_conferido(self):
        for titulo in ("## 5.5. LLM Prompts", "## 5.5 LLM Prompts", "## 5. LLM Prompts"):
            with self.subTest(titulo=titulo):
                rc, out = self.lint(titulo + "\n\nsem inventário\n")
                self.assertEqual(rc, 1, out)
                self.assertIn("falta o subtítulo ### Inventário", out)

    def test_chave_sem_preencher_nos_3_campos_do_contrato(self):
        for campo in ("Tom/audiência", "Tipo de saída", "Fallback aprovado"):
            for valor in ("{tom}", "`{tom}`"):
                with self.subTest(campo=campo, valor=valor):
                    texto = re.sub(r"(?m)^(#### Prompt 1:.*\n(?:.*\n)*?)(\| \*\*Autônomo\?\*\*)",
                                   lambda m: m.group(1) + "| **%s** | %s |\n" % (campo, valor) + m.group(2), self.secao, count=1)
                    self.assertNotEqual(texto, self.secao)
                    rc, out = self.lint(texto)
                    self.assertEqual(rc, 1, out)
                    self.assertIn("com %s sem preencher" % campo, out)

    def test_json_preenchido_nao_e_chave_sem_preencher(self):
        # R2@claude da rodada 3
        import re as _re
        texto = _re.sub(r"(?m)^(#### Prompt 1:.*\n(?:.*\n)*?)(\| \*\*Autônomo\?\*\*)",
                        lambda m: m.group(1) + '| **Tipo de saída** | JSON `{"nota": 0}` |\n' + m.group(2), self.secao, count=1)
        self.assertNotEqual(texto, self.secao)
        rc, out = self.lint(texto)
        self.assertEqual(rc, 0, out)

    def test_so_a_primeira_tabela_do_inventario_conta(self):
        i = self.secao.index("### Contrato por prompt")
        com_outra = self.secao[:i] + "Legenda:\n\n| Sigla | Sentido |\n|---|---|\n| v1 | versão 1 |\n\n" + self.secao[i:]
        rc, out = self.lint(com_outra)
        self.assertEqual(rc, 0, out)

    def test_tabela_sem_as_colunas_seguida_da_certa_reprova(self):
        i = self.secao.index("| # | Nome |")
        com_outra = self.secao[:i] + "| Sigla | Sentido |\n|---|---|\n| v1 | versão 1 |\n\n" + self.secao[i:]
        self.reprova(com_outra, "falta a coluna Tipo")

    def test_o_que_esta_entre_chaves_nunca_passa(self):
        # O lint geral ignora o que está entre crases, e chave sem espaço nem maiúscula: aqui, em nenhum dos 2 casos.
        fragmento = (RAIZ / "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md").read_text(encoding="utf-8")
        cru = fragmento[fragmento.index("## LLM Prompts"):]
        rc, out = self.lint(cru)
        self.assertEqual(rc, 1, out)
        self.assertIn("linha 1 do inventário com o que está entre chaves", out)
        self.assertIn("Prompt 1 com Autônomo? sem preencher", out)
        for de, para in (("`x`", "`" + L + "caminho do arquivo" + R + "`"), ("| x |", "| " + L + "nome" + R + " |")):
            with self.subTest(de=de):
                linhas = [ln.replace(de, para, 1) if ln.startswith("| 1 | x |") else ln for ln in self.secao.splitlines()]
                self.reprova("\n".join(linhas) + "\n", "entre chaves sem preencher")

    def test_erro_de_prompt_e_de_manifest_juntos(self):
        p = self.escreve(self.tmp, "DESIGN_Y.md", self.base.replace("**Total Files:** 3", "**Total Files:** 4", 1)
                         + "\n## LLM Prompts\n\nnada\n")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, p], self.tmp)
        self.assertEqual(rc, 1)
        self.assertIn("corrija também os outros pontos", (out + err).splitlines()[-1])

    def test_formato_antigo_real_reprova_com_a_frase(self):
        antigo = ("## LLM Prompts\n\n### Inventory\n\n| Nome | Tipo |\n|---|---|\n| a | one-shot |\n\n"
                  "### Contract\n\n| Campo | Valor |\n|---|---|\n| Tom | x |\n")
        self.reprova(antigo, "falta o subtítulo ### Inventário")


if __name__ == "__main__":
    unittest.main()


class AvisoDeSeguranca(Sandbox):
    """F18/F20: DEFINE com item de segurança aplicado e DESIGN sem a seção ## Segurança ⇒ ⚠️, exit 0."""

    DEFINE = "# DEFINE: X\n\n| Aspect | Value | Notes |\n|---|---|---|\n| **Segurança** | %s | 2026-11-11 |\n"
    SECAO = "\n## Segurança\n\n1. **Onde mora cada segredo:** a chave do banco na variável de ambiente do servidor.\n"

    def roda_lint(self, linha_define: str, com_secao: bool):
        pasta = self.tmp / "features"
        pasta.mkdir(exist_ok=True)
        design = pasta / "DESIGN_X.md"
        texto = FIXTURE.read_text(encoding="utf-8")
        design.write_text(texto + (self.SECAO if com_secao else ""), encoding="utf-8")
        if linha_define is not None:
            (pasta / "DEFINE_X.md").write_text(self.DEFINE % linha_define, encoding="utf-8")
        return self.roda([PYTHON, "-B", SCRIPT, design], RAIZ)

    def test_aplicado_sem_secao_avisa_e_passa(self):
        rc, out, err = self.roda_lint("2 aplicados (S01, S07) · 0 recusados · 1 adiado (S13)", False)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("o DEFINE tem 2 item(ns) de segurança aplicado(s)", out)
        self.assertIn("DESIGN válido", out)

    def test_com_secao_ou_sem_aplicado_nao_avisa(self):
        for linha, secao in (("2 aplicados (S01, S07)", True), ("0 aplicados · 1 recusado (S13)", False),
                             ("N.A. — script local sem login", False), (None, False)):
            with self.subTest(linha=linha, secao=secao):
                rc, out, err = self.roda_lint(linha, secao)
                self.assertEqual(rc, 0, out + err)
                self.assertNotIn("⚠️", out + err)
