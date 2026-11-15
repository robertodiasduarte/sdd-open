"""F16W2, AT-003: as formas de caminho e de fim de linha do Windows nos scripts que a 1ª medição acusou.

O Windows de verdade (C:\\ × /c/ × /tmp/, o \\r do print do Python) só o CI do PR mostra; aqui fica o que dá para
simular em qualquer sistema: o valor literal "C:\\…" e um python3 que escreve "\\r\\n" como o do Windows.
"""
from __future__ import annotations

import sys

from apoio import BASH, Sandbox, caminho_bash


class SlotComCr(Sandbox):
    """O slot.sh lia "VALOR\\r" e dizia que o slot estava vazio (39 quedas no Windows). Sem o calço (script copiado
    sozinho, sem lib/python.sh), a rede local do próprio slot tira o \\r."""

    def test_valor_com_cr_e_lido_e_roda(self):
        r = self.repo()
        self.copia("sdd/bin/slot.sh", r)
        self.escreve(r, "sdd/config.yaml", 'smoke:\n  before_ok_cmd: "echo rodou-o-slot"\n')
        self.commit(r, "base")
        falso = self.tmp / "py"
        falso.mkdir()
        py = falso / "python3"
        # awk, não sed: o sed BSD antigo troca "\\r" pela letra r (revisão, rodada 1, R4)
        py.write_text("#!/bin/sh\n'%s' \"$@\" | awk '{printf \"%%s\\r\\n\", $0}'\n" % caminho_bash(sys.executable),
                      encoding="utf-8")
        py.chmod(0o755)
        env = dict(self.env, PATH=caminho_bash(falso) + ":" + self.env["PATH"], TMPDIR=str(self.tmp))
        rc, out, err = self.roda([BASH, "sdd/bin/slot.sh", "smoke.before_ok_cmd"], r, env=env)
        self.assertNotIn("vazio: pulado", out + err)
        self.assertIn("rodou-o-slot", out + err)
        self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    import unittest
    unittest.main()
