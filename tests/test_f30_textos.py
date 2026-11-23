"""F30 S1 — o texto das skills (DEFINE_F30_QUALIDADE_CODIGO, AT-003 e AT-007).

AT-003: o passo de verificar da sdd-build nomeia os 2 slots, os arquivos da tarefa, a escada de retry, os logs (de antes
e do fim) e a linha `lint: slot vazio`; o passo anterior lê as regras de qualidade. O modo web (o SKILL.md do starter)
traz as regras e o lint do projeto, sem `sdd/bin/` (LM-035).
AT-007: a sdd-new-session roda `checar.sh --linter`, pergunta [D2] e grava só com o sim, sem instalar.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILLS = RAIZ / ".agents" / "skills"
BUILD = SKILLS / "sdd-build" / "SKILL.md"
WEB = SKILLS / "sdd-build" / "web" / "MODO_WEB.md"
SESSAO = SKILLS / "sdd-new-session" / "SKILL.md"
CHECAR = SKILLS / "sdd-checar-ambiente" / "SKILL.md"


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


def plano(t: str) -> str:
    return re.sub(r"\s+", " ", t)


class AT003Build(unittest.TestCase):
    def passo_4(self) -> str:
        t = ler(BUILD)
        return plano(t[t.index("### 4. Executar cada tarefa"):t.index("### 4b. Migration")])

    def test_verificar_nomeia_slots_arquivos_logs_e_slot_vazio(self):
        p = self.passo_4()
        verificar = p[p.index("4. **Verificar:**"):p.index("5. **Marcar**")]
        for trecho in ("`project.lint_cmd` sobre os arquivos da tarefa", "`project.typecheck_cmd` como está",
                       "falha da tarefa e segue a escada", "`sdd/reports/evidence/{F}/LINT.log` e `TIPOS.log`",
                       "[exit=<rc>]", "a mesma 1ª linha do log de antes", "`lint: slot vazio`", "sem bloquear"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, verificar)

    def test_antes_da_1a_tarefa_le_as_regras_e_grava_o_log_de_antes(self):
        p = self.passo_4()
        self.assertIn("`bash sdd/bin/qualidade-regras.sh --regras`", p)
        self.assertIn("`sdd/reports/evidence/{F}/LINT.antes.log` (ou `TIPOS.antes.log`)", p)
        self.assertIn("3. **Escrever** seguindo os Code Patterns e as regras de qualidade.", p)
        self.assertLess(p.index("qualidade-regras.sh --regras"), p.index("4. **Verificar:**"))

    def test_modo_web_traz_as_regras_e_o_lint_do_projeto(self):
        t = plano(ler(WEB))
        self.assertIn("[references/CATALOGO_QUALIDADE.md](references/CATALOGO_QUALIDADE.md)", t)
        for regra in ("erro tratado ou propagado", "nome que diz o que é", "só o código que roda",
                      "reusar a função que já existe antes de criar outra", "constante com nome", "uma coisa por função"):
            with self.subTest(regra=regra):
                self.assertIn(regra, t)
        self.assertIn("`project.lint_cmd` e `project.typecheck_cmd`", t)
        self.assertIn("sem instalar", t)
        self.assertNotIn("sdd/bin/", ler(WEB))

    def test_teto_de_linhas(self):
        for p in (BUILD, WEB, SESSAO, CHECAR):
            with self.subTest(arquivo=p.name):
                self.assertLessEqual(len(ler(p).splitlines()), 500)


class AT007NovaSessao(unittest.TestCase):
    def bloco(self) -> str:
        t = ler(SESSAO)
        i = t.index("- **Lint e tipos sem evidência**")
        return plano(t[i:t.index("- **Preparação**", i)])

    def test_roda_o_modo_linter_e_pergunta_d2(self):
        b = self.bloco()
        self.assertIn("checar.sh --linter", b)
        self.assertIn("[D2 · muda o produto] **Gravo os comandos de lint e de tipos", b)
        for opcao in ("**gravar** (recomendado)", "**agora não**", "**não sei**"):
            with self.subTest(opcao=opcao):
                self.assertIn(opcao, b)

    def test_grava_so_com_sim_e_nunca_instala(self):
        b = self.bloco()
        self.assertIn("nunca instala a ferramenta", b)
        self.assertIn("anterior à 1.8.0", b)   # checar antigo, sem o modo: nada a sugerir

    def test_checar_ambiente_documenta_o_aviso_e_o_modo(self):
        t = plano(ler(CHECAR))
        self.assertIn("**Linter e tipos**", t)
        self.assertIn("`--linter`", t)
        self.assertIn("É sugestão", t)

    def test_frase_positiva_sem_os_padroes_da_f29(self):
        for p in (BUILD, WEB, SESSAO, CHECAR, SKILLS / "sdd-build/web/references/CATALOGO_QUALIDADE.md"):
            t = ler(p)
            with self.subTest(arquivo=p.name):
                for padrao in ("Não cite nem resuma", "comece com esta linha", "versão atual: http"):
                    self.assertNotIn(padrao, t)


if __name__ == "__main__":
    unittest.main()
