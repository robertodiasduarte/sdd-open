"""Contrato do sdd/bin/contraste.sh (DEFINE F13 AT-001 a AT-007): razão WCAG truncada, com veredito.

Os oráculos foram calculados fora do script, em Python. Exit 0 PASSA · 2 REPROVA (ou self-test falhou) · 64 uso.
"""
from __future__ import annotations

import subprocess
import sys
import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/contraste.sh"


class Base(Sandbox):
    def medir(self, *args, env=None):
        return self.roda([BASH, SCRIPT, *args], self.tmp, env)


class Veredito(Base):
    def conferir(self, args, rc_esperado, linha):
        rc, out, err = self.medir(*args)
        self.assertEqual((rc, out.splitlines()[0]), (rc_esperado, linha), err)
        ultimas = out.splitlines()[-2:]
        self.assertTrue(ultimas[0].startswith("RESULTADO: "), out)
        self.assertTrue(ultimas[1].startswith("→ "), out)

    def test_piso_padrao(self):
        self.conferir(("#767676", "#ffffff"), 0, "4.54:1 PASSA (piso 4.5:1)")
        self.conferir(("#777777", "#ffffff"), 2, "4.47:1 REPROVA (piso 4.5:1)")
        self.conferir(("#000000", "#ffffff"), 0, "21.00:1 PASSA (piso 4.5:1)")

    def test_forma_curta_e_maiusculas(self):
        self.conferir(("#777", "#FFF"), 2, "4.47:1 REPROVA (piso 4.5:1)")

    def test_a_ordem_das_cores_nao_muda_a_razao(self):
        self.conferir(("#ffffff", "#767676"), 0, "4.54:1 PASSA (piso 4.5:1)")

    def test_truncado_nunca_arredondado(self):
        # Exato 4,4999996: arredondado, passaria.
        self.conferir(("#6c7b67", "#ffffff"), 2, "4.49:1 REPROVA (piso 4.5:1)")

    def test_exato_acima_do_piso_passa(self):
        # Exato 4,50003.
        self.conferir(("#71796f", "#ffffff"), 0, "4.50:1 PASSA (piso 4.5:1)")

    def test_transparencia_composta_sobre_o_fundo(self):
        self.conferir(("#000", "#fff", ".5"), 2, "3.97:1 REPROVA (piso 4.5:1)")
        self.conferir(("#000", "#fff", "0.5"), 2, "3.97:1 REPROVA (piso 4.5:1)")
        self.conferir(("#000", "#fff", "1"), 0, "21.00:1 PASSA (piso 4.5:1)")
        self.conferir(("#000", "#fff", "0"), 2, "1.00:1 REPROVA (piso 4.5:1)")

    def test_piso_em_qualquer_posicao(self):
        self.conferir(("#777777", "#ffffff", "--piso", "3"), 0, "4.47:1 PASSA (piso 3:1)")
        self.conferir(("--piso", "3", "#777777", "#ffffff"), 0, "4.47:1 PASSA (piso 3:1)")
        self.conferir(("#777777", "--piso", "3", "#ffffff"), 0, "4.47:1 PASSA (piso 3:1)")

    def test_piso_com_centesimos_comparados_em_inteiros(self):
        self.conferir(("#767676", "#ffffff", "--piso", "4.55"), 2, "4.54:1 REPROVA (piso 4.55:1)")
        self.conferir(("#767676", "#ffffff", "--piso", "4.54"), 0, "4.54:1 PASSA (piso 4.54:1)")
        # 08 quebraria a aritmética do bash, que lê base 8.
        self.conferir(("#767676", "#ffffff", "--piso", "4.08"), 0, "4.54:1 PASSA (piso 4.08:1)")


class ErroDeUso(Base):
    def conferir(self, *args, trecho="", fixar=""):
        rc, out, err = self.medir(*args)
        self.assertEqual(rc, 64, out + err)
        self.assertEqual(out, "", "razão ou texto na saída padrão: " + out)
        self.assertIn("RESULTADO: ERRO DE USO", err)
        self.assertRegex(err.splitlines()[-1], r"^→ ")
        if trecho:
            self.assertIn(trecho, err)

    def test_sem_argumento_explica_as_aspas(self):
        self.conferir(trecho="comentário no shell")

    def test_cor_invalida(self):
        for cor in ("#zzz", "#12345", "777777", "#1234567", ""):
            with self.subTest(cor=cor):
                self.conferir(cor, "#ffffff", trecho="cor não reconhecida")
        self.conferir("#ffffff", "#zzz", trecho="cor não reconhecida")

    def test_rgba_ensina_o_terceiro_valor(self):
        for cor in ("rgba(0,0,0,.5)", "RGBA(0,0,0,.5)", "#00000080"):
            with self.subTest(cor=cor):
                self.conferir(cor, "#fff", trecho="3º valor")

    def test_quantidade_de_valores(self):
        self.conferir("#000", trecho="faltam cores")
        self.conferir("#000", "#fff", ".5", ".5", trecho="valores demais")

    def test_alpha_fora_de_0_a_1(self):
        for a in ("2", "1.5", "abc", "1,5"):
            with self.subTest(alpha=a):
                self.conferir("#000", "#fff", a, trecho="transparência")

    def test_piso_invalido(self):
        self.conferir("#000", "#fff", "--piso", trecho="sem valor")
        for p in ("0", "0.00", "4.555", "abc", "-1"):
            with self.subTest(piso=p):
                self.conferir("#000", "#fff", "--piso", p, trecho="piso inválido")

    def test_opcao_desconhecida(self):
        self.conferir("#000", "#fff", "--nada", trecho="opção desconhecida")


class Ajuda(Base):
    def test_help_sai_zero_e_explica_o_truncamento(self):
        rc, out, _ = self.medir("--help")
        self.assertEqual(rc, 0)
        self.assertIn("truncado de propósito", out)
        self.assertIn("--piso 3", out)


class Locale(Base):
    def test_virgula_decimal_no_sistema_nao_muda_nada(self):
        env = dict(self.env, LC_ALL="pt_BR.UTF-8")
        sonda = subprocess.run(["awk", "BEGIN{printf \"%.1f\", .5}"], env=env, capture_output=True, text=True)
        if sonda.stdout != "0,5":
            # No macOS, o piso que este teste existe para cobrir, pular seria perder o teste em silêncio.
            self.assertNotEqual(sys.platform, "darwin", "macOS sem pt_BR com vírgula no awk")
            self.skipTest("este sistema não tem pt_BR com vírgula no awk (saída: %r)" % sonda.stdout)
        rc, out, _ = self.medir("#000", "#fff", ".5", env=env)
        self.assertEqual((rc, out.splitlines()[0]), (2, "3.97:1 REPROVA (piso 4.5:1)"))
        rc, out, _ = self.medir("#767676", "#ffffff", "--piso", "4.5", env=env)
        self.assertEqual((rc, out.splitlines()[0]), (0, "4.54:1 PASSA (piso 4.5:1)"))


class AutoTeste(Base):
    def test_cdpath_nao_quebra(self):
        # Só o caminho relativo passa pelo cd "$(dirname "$0")" que o CDPATH desvia.
        rc, _, err = self.roda([BASH, "sdd/bin/contraste.sh", "--self-test"], RAIZ, dict(self.env, CDPATH="."))
        self.assertEqual(rc, 0, err)

    def test_verde_por_caminho_absoluto_e_relativo(self):
        rc, out, err = self.medir("--self-test")
        self.assertEqual(rc, 0, err)
        self.assertIn("RESULTADO: VERDE", out)
        rc, out, err = self.roda([BASH, "sdd/bin/contraste.sh", "--self-test"], RAIZ)
        self.assertEqual(rc, 0, err)

    def test_vermelho_quando_a_conta_e_sabotada(self):
        copia = self.tmp / "contraste.sh"
        copia.write_text(SCRIPT.read_text(encoding="utf-8").replace("* 100 + 1e-9)", "* 100 + 0.5)"), encoding="utf-8")
        rc, _, err = self.roda([BASH, copia, "--self-test"], self.tmp)
        self.assertEqual(rc, 2)
        self.assertIn("#6c7b67", err)
        self.assertIn("RESULTADO: VERMELHO", err)


if __name__ == "__main__":
    unittest.main()
