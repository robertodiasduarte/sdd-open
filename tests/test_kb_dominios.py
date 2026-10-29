"""Contrato do sdd/bin/kb-dominios.py: o KB Domains do DEFINE só cita pastas de sdd/kb/, ou diz `nenhum`.

Cada caso monta um projeto temporário (<tmp>/sdd/features/DEFINE_X.md + <tmp>/sdd/kb/<domínio>/) e confere
o exit e a mensagem. Exit: 0 válido · 1 violação · 64 uso. Também confere o passo 10 da sdd-define e a
linha do DEFINE_TEMPLATE.md, que mandam rodar o lint.
"""
from __future__ import annotations

import os
import unittest

from apoio import PYTHON, RAIZ, Sandbox

LINT = RAIZ / "sdd/bin/kb-dominios.py"
DEFINE_SKILL = RAIZ / ".agents/skills/sdd-define/SKILL.md"
TEMPLATE = RAIZ / "sdd/templates/DEFINE_TEMPLATE.md"
MOLDE = """# DEFINE: X

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | src/ | — |
{linha}| **LLM Prompts** | false | — |

```text
| **KB Domains** | inventado | dentro de bloco de código não conta |
```
"""
RULE_MAP = """# RULE_MAP — gerado por `kb_normativo.py rule-map`. Não edite à mão.

| Regra | Vigência | Fonte (documento · localizador · degrau) | Status | Conflito com | Implementação | Teste | Sev. | Código |
|---|---|---|---|---|---|---|---|---|
| R-1 | 2026-01-01 → em vigor | Lei X · art. 5º \\| inciso II · lei-ordinaria | confirmado | — | src/r.py | tests/test_r.py::t | E | — |
| R-2 | 2026-01-01 → em vigor | Lei X · art. 6º · lei-ordinaria | confirmado | — | — | — | E | — |
"""


class KbDominios(Sandbox):
    def projeto(self, valor, dominios=("fiscal", "folha"), kb=True):
        linha = "" if valor is None else "| **KB Domains** | %s | padrões |\n" % valor
        define = self.escreve(self.tmp, "sdd/features/DEFINE_X.md", MOLDE.replace("{linha}", linha))
        if kb:
            (self.tmp / "sdd/kb").mkdir(parents=True, exist_ok=True)
            self.escreve(self.tmp, "sdd/kb/_index.yaml", "version: \"1.0\"\n")
            (self.tmp / "sdd/kb/.oculta").mkdir(exist_ok=True)
            for d in dominios:
                (self.tmp / "sdd/kb" / d).mkdir(exist_ok=True)
        return define

    def lint(self, define, cwd=None):
        rc, out, err = self.roda([PYTHON, "-B", LINT, define], cwd or self.tmp)
        return rc, out, err

    # verdes ----------------------------------------------------------------
    def test_nenhum_passa(self):
        rc, out, err = self.lint(self.projeto("nenhum", kb=False))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("KB Domains válido (nenhum)", out)
        self.assertIn("RESULTADO: VERDE", out)

    def test_nomes_que_existem_passam(self):
        rc, out, err = self.lint(self.projeto("`fiscal`, folha"))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("KB Domains válido (fiscal, folha)", out)

    def test_prefixo_sdd_kb_e_barra_final_sao_tolerados(self):
        rc, out, err = self.lint(self.projeto("sdd/kb/fiscal/"))
        self.assertEqual(rc, 0, out + err)

    def test_raiz_vem_do_define_e_nao_do_diretorio_corrente(self):
        define = self.projeto("fiscal")
        outro = self.tmp / "outro"
        outro.mkdir()
        rc, out, err = self.lint(define, cwd=outro)
        self.assertEqual(rc, 0, out + err)

    def test_lista_os_testes_do_rule_map_com_pipe_escapado(self):
        define = self.projeto("fiscal")
        self.escreve(self.tmp, "sdd/kb/fiscal/RULE_MAP.md", RULE_MAP)
        rc, out, err = self.lint(define)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("fiscal: R-1 → tests/test_r.py::t", out)
        self.assertNotIn("R-2 →", out)
        self.assertNotIn("src/r.py", out)
        linhas = out.strip().splitlines()
        self.assertEqual(linhas[-2], "RESULTADO: VERDE")
        self.assertTrue(linhas[-1].startswith("→ ponha estes testes no cmd do Verify Gate"), out)

    # vermelhos -------------------------------------------------------------
    def vermelho(self, define, trecho):
        rc, out, err = self.lint(define)
        self.assertEqual(rc, 1, out + err)
        self.assertIn(trecho, err)
        self.assertIn("RESULTADO: VERMELHO", err)
        self.assertRegex(err, r"(?m)^→ ")
        return err

    def test_linha_ausente(self):
        self.vermelho(self.projeto(None), "falta a linha **KB Domains**")

    def test_linha_fora_do_technical_context_nao_conta(self):
        define = self.projeto("fiscal")
        texto = define.read_text(encoding="utf-8")
        sem = texto.replace("| **KB Domains** | fiscal | padrões |\n", "")
        define.write_text(sem.replace("# DEFINE: X\n", "# DEFINE: X\n\n## Goals\n\n| **KB Domains** | fiscal | x |\n", 1),
                          encoding="utf-8")
        self.vermelho(define, "falta a linha **KB Domains**")

    def test_nenhum_em_outra_secao_nao_esconde_o_technical_context(self):
        define = self.projeto("inexistente")
        texto = define.read_text(encoding="utf-8")
        define.write_text(texto.replace("# DEFINE: X\n", "# DEFINE: X\n\n## Goals\n\n| **KB Domains** | nenhum | x |\n", 1),
                          encoding="utf-8")
        self.vermelho(define, "'inexistente' não existe em sdd/kb/")

    def test_valor_vazio(self):
        self.vermelho(self.projeto(" "), "não é lista de domínios")

    def test_placeholder(self):
        self.vermelho(self.projeto("{bases de conhecimento do projeto}"), "não é lista de domínios")

    def test_na_reprova(self):
        for valor in ("N/A", "—", "TBD"):
            with self.subTest(valor=valor):
                self.vermelho(self.projeto(valor), "não é lista de domínios")

    def test_nenhum_com_nome(self):
        self.vermelho(self.projeto("nenhum, fiscal"), "'nenhum' vem sozinho")

    def test_nome_sem_pasta_lista_os_que_existem(self):
        err = self.vermelho(self.projeto("fiscall"), "'fiscall' não existe em sdd/kb/ (existem: fiscal, folha)")
        self.assertNotIn(".oculta", err)
        self.assertNotIn("_index.yaml", err)

    def test_lista_de_existentes_truncada_em_10(self):
        nomes = ["d%02d" % i for i in range(13)]
        err = self.vermelho(self.projeto("x", dominios=nomes), "não existe em sdd/kb/")
        self.assertIn("d09 e mais 3)", err)
        self.assertNotIn("d10", err)

    def test_sdd_kb_ausente(self):
        err = self.vermelho(self.projeto("fiscal", kb=False), "sdd/kb/ não existe")
        self.assertIn("→ rode a sdd-kb para criar a base, ou escreva nenhum", err)

    # uso -------------------------------------------------------------------
    def test_uso_errado_e_64(self):
        for args in ([], [self.tmp / "nao-existe.md"], ["--xyz"]):
            with self.subTest(args=args):
                rc, out, err = self.roda([PYTHON, "-B", LINT, *args], self.tmp)
                self.assertEqual(rc, 64, out + err)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root lê pasta sem permissão")
    def test_sdd_kb_ilegivel_e_1_sem_traceback(self):
        define = self.projeto("fiscal")
        kb = self.tmp / "sdd/kb"
        kb.chmod(0)
        try:
            rc, out, err = self.lint(define)
        finally:
            kb.chmod(0o755)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("não consegui ler sdd/kb/", err)
        self.assertIn("RESULTADO: VERMELHO", err)
        self.assertNotIn("Traceback", out + err)

    def test_arquivo_ilegivel_e_1_sem_traceback(self):
        p = self.tmp / "sdd/features/DEFINE_X.md"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"\xff\xfe| **KB Domains** | x |\n")
        self.assertEqual(p.read_bytes()[:2], b"\xff\xfe")
        rc, out, err = self.lint(p)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("não consegui ler", err)
        self.assertNotIn("Traceback", out + err)


class PassoDaDefine(unittest.TestCase):
    def test_passo_10_roda_o_lint(self):
        texto = DEFINE_SKILL.read_text(encoding="utf-8")
        passo = texto.split("### 10. Conferir o KB Domains", 1)
        self.assertEqual(len(passo), 2, "falta o passo ### 10. Conferir o KB Domains")
        corpo = passo[1].split("\n## ", 1)[0]
        self.assertIn("`python3 sdd/bin/kb-dominios.py sdd/features/DEFINE_{FEATURE}.md`", corpo)
        self.assertNotIn("```", corpo)
        self.assertIn("Verify Gate", corpo)
        self.assertIn("ls sdd/kb/", texto)
        self.assertLess(texto.index("### 9. Gravar"), texto.index("### 10. Conferir o KB Domains"))

    def test_template_sem_ou_equivalente(self):
        linha = [l for l in TEMPLATE.read_text(encoding="utf-8").splitlines() if l.startswith("| **KB Domains**")]
        self.assertEqual(len(linha), 1)
        self.assertIn("ls sdd/kb/", linha[0])
        self.assertIn("`nenhum`", linha[0])
        self.assertNotIn("ou equivalente", linha[0])


if __name__ == "__main__":
    unittest.main()
