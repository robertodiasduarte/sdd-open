"""F16W2, passo 0: a curadoria do playbook da F16W (decisões do Roberto, 2026-11-14).

Entram LM-029 (bash pelo nome cai no WSL), LM-030 (executor com PYTHONIOENCODING mascara a quebra do aluno) e
LM-031 (módulos de teste em paralelo derrubam testes de tempo); a LM-012 mordeu de novo (commit 4e76b39) e foi
promovida ao publish-gate, que já a barra. As 15 contagens "ajudou" (autodeclaradas) e as 3 sugestões de "mordeu"
(falsos positivos: linhas de veredito PASS) ficam de fora.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def linha(pb: str, lm: str) -> str:
    return next((ln for ln in pb.split("\n") if ln.startswith("- [%s]" % lm)), "")


class Curadoria(unittest.TestCase):
    def test_as_tres_licoes_da_f16w_estao_no_playbook(self):
        pb = ler("sdd/playbook.md")
        for lm, trecho in (("LM-029", "procura o programa em `System32` **antes** do `PATH`"),
                           ("LM-030", "Um executor de testes que põe `PYTHONIOENCODING=utf-8`"),
                           ("LM-031", "Rodar módulos de teste ao mesmo tempo")):
            with self.subTest(lm=lm):
                ln = linha(pb, lm)
                self.assertIn(trecho, ln)
                self.assertIn("**Do instead:**", ln)
                # nasceram em 2026-11-14 com ajudou=0; a curadoria da F16W2 + F22 (2026-11-15) já as contou
                m = re.search(r"ajudou=\d+ mordeu=\d+ · conf=(\d{4}-\d{2}-\d{2})", ln)
                self.assertIsNotNone(m, lm)
                self.assertGreaterEqual(m.group(1), "2026-11-14")   # a data só avança (texto ISO compara como data)

    def test_lm012_mordeu_e_foi_promovida(self):
        ln = linha(ler("sdd/playbook.md"), "LM-012")
        self.assertIn("mordeu=2", ln)
        self.assertIn("promovido_para: scripts/publish-gate-patterns.txt", ln)
        self.assertTrue((RAIZ / "scripts/publish-gate-patterns.txt").is_file())

    def test_as_contagens_ajudou_da_f16w_nao_foram_aplicadas(self):
        # só LM-012 e as 3 lições novas ganharam conf=2026-11-14 nesta curadoria (LM-027/028 são da F17c)
        pb = ler("sdd/playbook.md")
        # nenhuma outra lição ganhou a data desta curadoria (curadorias seguintes podem trocar a data destas por uma maior)
        datadas = set(re.findall(r"^- \[(LM-\d+)\] .*conf=2026-11-14", pb, re.M))
        self.assertLessEqual(datadas, {"LM-012", "LM-027", "LM-028", "LM-029", "LM-030", "LM-031"})


class CuradoriaF16W2F22(unittest.TestCase):
    """A curadoria da F16W2 + F22 (2026-11-15): 3 lições novas e o conselho da LM-015 refinado."""

    def test_as_tres_licoes_novas(self):
        pb = ler("sdd/playbook.md")
        for lm, trecho in (("LM-032", "Um calço posto no PATH para mudar COMO o Python"),
                           ("LM-033", "Saída de comando do git lida por máquina segue a configuração"),
                           ("LM-034", "o PATH de links simbólicos que um teste monta")):
            with self.subTest(lm=lm):
                ln = linha(pb, lm)
                self.assertIn(trecho, ln)
                self.assertIn("**Do instead:**", ln)
                m = re.search(r"ajudou=\d+ mordeu=\d+ · conf=(\d{4}-\d{2}-\d{2})", ln)
                self.assertIsNotNone(m, lm)
                self.assertGreaterEqual(m.group(1), "2026-11-15")

    def test_lm015_troca_a_saida_dentro_do_script(self):
        ln = linha(ler("sdd/playbook.md"), "LM-015")
        self.assertIn("reconfigure(encoding=\"utf-8\"", ln)
        self.assertIn("não vale quando o aluno roda o `.py` direto", ln)


if __name__ == "__main__":
    unittest.main()
