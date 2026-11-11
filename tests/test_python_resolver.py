"""sdd/bin/lib/python.sh — o Python que roda vira `python3` (F16, AT-006).

No Windows, `python3` costuma ser o atalho da Microsoft Store (sai 9009 sem rodar nada) e o Python nativo é
`python` ou `py -3`. Cada caso roda um script de verdade que lê a biblioteca com `.`, num PATH montado só
com stubs e as ferramentas de que ela precisa: o Python desta máquina não entra por engano.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

LIB = RAIZ / "sdd/bin/lib/python.sh"
FERRAMENTAS = ("mktemp", "sed", "chmod", "dirname", "env", "cat", "xargs", "sh")
ATALHO = "#!/bin/sh\nexit 9009\n"            # o atalho da Store: existe, não roda
VELHO = "#!/bin/sh\nexit 1\n"                 # responde, mas a versão é menor que 3.9


def nativo(py: str = sys.executable, aceita_menos_3: bool = False) -> str:
    """Stub que chama o Python da suíte; com aceita_menos_3, engole o `-3` do `py -3`."""
    tira = '[ "$1" = -3 ] && shift\n' if aceita_menos_3 else ""
    return "#!/bin/sh\n%sexec '%s' \"$@\"\n" % (tira, py)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.ferr = self.tmp / "ferramentas"
        self.ferr.mkdir()
        for nome in FERRAMENTAS:
            real = shutil.which(nome)
            self.assertTrue(real, nome)
            self.stub(nome, "#!/bin/sh\nexec '%s' \"$@\"\n" % real, pasta=self.ferr)

    def stub(self, nome: str, corpo: str, pasta: Path | None = None) -> Path:
        p = (pasta or self.bin) / nome
        p.write_text(corpo, encoding="utf-8")
        p.chmod(0o755)
        return p

    def roda_script(self, corpo: str, **env: str) -> tuple[int, str, str]:
        script = self.tmp / "script.sh"
        script.write_text('. "%s"\n%s' % (LIB.as_posix(), corpo), encoding="utf-8")
        e = {k: v for k, v in self.env.items() if k not in ("SDD_PYTHON", "SDD_PYTHON_RESOLVIDO")}
        e.update(PATH=str(self.bin) + ":" + str(self.ferr), TMPDIR=str(self.tmp))
        e.update(env)
        return self.roda([BASH, script], self.tmp, e)


class Escolha(Base):
    def test_atalho_da_store_e_python_nativo_usa_o_python(self):
        self.stub("python3", ATALHO)
        self.stub("python", nativo())
        rc, out, err = self.roda_script("python3 -c 'print(\"rodou\")'\necho \"$SDD_PYTHON_RESOLVIDO\"\n")
        self.assertEqual(rc, 0, err)
        rodou, pasta = out.splitlines()
        self.assertEqual(rodou, "rodou")
        self.assertTrue(Path(pasta).is_dir(), pasta)            # o calço, não o nome python3
        self.assertNotIn("🛑", err)

    def test_atalho_e_so_py_usa_py_menos_3(self):
        self.stub("python3", ATALHO)
        self.stub("py", nativo(aceita_menos_3=True))
        rc, out, err = self.roda_script("python3 -c 'print(\"via py\")'\n")
        self.assertEqual((rc, out.strip()), (0, "via py"), err)

    def test_python3_velho_passa_ao_proximo(self):
        self.stub("python3", VELHO)
        self.stub("python", nativo())
        rc, out, err = self.roda_script("python3 -c 'import sys; print(sys.version_info >= (3, 9))'\n")
        self.assertEqual((rc, out.strip()), (0, "True"), err)

    def test_python3_que_serve_nao_muda_nada(self):
        self.stub("python3", nativo())
        rc, out, err = self.roda_script('echo "$SDD_PYTHON_RESOLVIDO"\necho "$PATH"\n')
        self.assertEqual(rc, 0, err)
        resolvido, path = out.splitlines()
        self.assertEqual(resolvido, "python3")
        self.assertEqual(path, str(self.bin) + ":" + str(self.ferr))   # o PATH de quem chamou, intacto

    def test_sdd_python_com_espaco_no_caminho(self):
        # rodada 1 da revisão, R2: o caminho era cortado na 1ª palavra e ignorado em silêncio
        pasta = self.tmp / "Program Files" / "Python 3"
        pasta.mkdir(parents=True)
        self.stub("python", nativo(), pasta=pasta)
        self.stub("python3", ATALHO)
        rc, out, err = self.roda_script("python3 -c 'print(\"escolhido\")'\n", SDD_PYTHON=str(pasta / "python"))
        self.assertEqual((rc, out.strip()), (0, "escolhido"), err)


class Parada(Base):
    """Na carga nada para (rodada 2, R2): só o script que precisa de Python pergunta, e a causa é a certa."""

    def test_so_o_atalho_a_carga_segue_e_a_guarda_diz_a_causa_uma_vez(self):
        self.stub("python3", ATALHO)
        rc, out, err = self.roda_script("echo SEGUIU\nsdd_python_pronto || echo FALTA\nsdd_python_pronto || echo FALTA\n")
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.split(), ["SEGUIU", "FALTA", "FALTA"])
        self.assertEqual(err.count("existe, mas não roda"), 1, err)        # uma vez por processo
        self.assertIn("atalho da Microsoft Store", err)

    def test_exigir_para_com_causa_e_conserto(self):
        self.stub("python3", ATALHO)
        rc, out, err = self.roda_script("sdd_python_exigir\necho SEGUIU\n")
        self.assertEqual(rc, 64, out + err)
        self.assertNotIn("SEGUIU", out)                                   # sem tentar seguir
        self.assertIn("o python3 deste computador existe, mas não roda", err)
        self.assertIn("precisa do Python 3.9 ou mais novo", err)
        self.assertIn("RESULTADO: PAROU\n→ instale o Python 3.9 ou mais novo (Windows: winget install", err)
        self.assertNotIn("Traceback", err)

    def test_python_velho_e_dito_pela_versao(self):
        # rodada 2, R3: o 3.8 que roda não é "não roda"; a mensagem diz a versão
        self.stub("python3", "#!/bin/sh\nprintf 3.8\n")
        rc, out, err = self.roda_script("sdd_python_exigir\n")
        self.assertEqual(rc, 64, err)
        self.assertIn("o python3 deste computador é o Python 3.8; o SDD Open precisa do 3.9 ou mais novo", err)
        self.assertNotIn("não roda", err)

    def test_so_python_2_e_dito_pela_versao(self):
        self.stub("python", "#!/bin/sh\nprintf 2.7\n")
        rc, out, err = self.roda_script("sdd_python_exigir\n")
        self.assertEqual(rc, 64, err)
        self.assertIn("o python deste computador é o Python 2.7", err)
        self.assertNotIn("python3 deste computador", err)

    def test_atalho_e_python_velho_tambem_para(self):
        # rodada 1, R1: com o último candidato ausente, o laço antigo deixava "py -3" escolhido sem existir
        self.stub("python3", ATALHO)
        self.stub("python", VELHO)
        rc, out, err = self.roda_script("sdd_python_exigir\necho SEGUIU\n")
        self.assertEqual(rc, 64, out + err)
        self.assertNotIn("SEGUIU", out)

    def test_nenhum_python_a_guarda_falha_calada_e_exigir_para(self):
        # cada script do pacote tem a sua mensagem de "python3 ausente": a guarda não fala por cima dela
        rc, out, err = self.roda_script("sdd_python_pronto || echo AUSENTE\necho SEGUIU\n")
        self.assertEqual(rc, 0, err)
        self.assertEqual(out.split(), ["AUSENTE", "SEGUIU"])
        self.assertEqual(err, "")
        rc, out, err = self.roda_script("sdd_python_exigir\n")
        self.assertEqual(rc, 64, err)
        self.assertIn("🛑 script.sh: precisa do Python 3.9 ou mais novo", err)

    def test_calco_que_nao_se_cria_e_dito(self):
        # rodada 2, R4: a falha do calço voltava 1 sem mensagem, e o script seguia com o atalho
        self.stub("python3", ATALHO)
        self.stub("python", nativo())
        rc, out, err = self.roda_script("sdd_python_pronto || echo FALTA\n", TMPDIR=str(self.tmp / "nao-existe"))
        self.assertEqual((rc, out.strip()), (0, "FALTA"), err)
        self.assertIn("não consegui criar o calço do Python na pasta temporária", err)


class Calco(Base):
    def setUp(self):
        super().setUp()
        self.stub("python3", ATALHO)
        self.stub("python", nativo())

    def test_vale_para_exec(self):
        # rodada 1, R3: `exec python3` (5 scripts do pacote) não enxerga função de bash
        rc, out, err = self.roda_script("exec python3 -c 'print(\"exec\")'\n")
        self.assertEqual((rc, out.strip()), (0, "exec"), err)

    def test_vale_para_env_e_xargs(self):
        rc, out, err = self.roda_script("env python3 -c 'print(\"env\")'\n"
                                        "printf 'pass\\n' | xargs python3 -c && echo xargs\n")
        self.assertEqual((rc, out.split()), (0, ["env", "xargs"]), err)

    def test_vale_para_bash_filho_sem_testar_de_novo(self):
        rc, out, err = self.roda_script("'%s' -c 'python3 -c \"print(1)\"; echo \"$SDD_PYTHON_RESOLVIDO\"'\n" % BASH)
        self.assertEqual(rc, 0, err)
        um, pasta = out.splitlines()
        self.assertEqual(um, "1")
        self.assertTrue((Path(pasta) / "python3").is_file())

    def test_cache_no_ambiente_e_usado_sem_testar(self):
        cache = self.tmp / "cache"
        cache.mkdir()
        self.stub("python3", "#!/bin/sh\necho do-cache\n", pasta=cache)
        rc, out, err = self.roda_script("python3\n", SDD_PYTHON_RESOLVIDO=str(cache))
        self.assertEqual((rc, out.strip()), (0, "do-cache"), err)


if __name__ == "__main__":
    import unittest
    unittest.main()
