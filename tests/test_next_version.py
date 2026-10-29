"""Contrato do scripts/next-version.sh: TAG / NEW / BASE a partir das tags vX.Y.Z.

Exit 0 ok · 1 sem nenhuma tag vX.Y.Z · 64 fora de git. stdout carrega só as três linhas.
"""
from __future__ import annotations

import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "scripts/next-version.sh"


class NextVersion(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.commit(self.r, "primeiro")

    def tag(self, nome: str, anotada: bool = False) -> None:
        if anotada:
            self.git(self.r, "tag", "-a", nome, "-m", nome)
        else:
            self.git(self.r, "tag", nome)

    def proxima(self) -> tuple[int, dict, str]:
        rc, out, err = self.roda([BASH, SCRIPT], self.r)
        campos = dict(l.split("=", 1) for l in out.splitlines() if "=" in l)
        return rc, campos, out + err

    def test_soma_um_patch_na_ultima_tag(self):
        self.tag("v2.2.0", anotada=True)
        self.commit(self.r, "depois")
        rc, c, out = self.proxima()
        self.assertEqual(rc, 0, out)
        self.assertEqual(c, dict(TAG="v2.2.1", NEW="1", BASE="v2.2.0"))

    def test_ordena_por_versao_e_nao_por_texto(self):
        for t in ("v2.9.0", "v2.10.0", "v2.1.0"):
            self.tag(t)
            self.commit(self.r, t)
        rc, c, out = self.proxima()
        self.assertEqual(rc, 0, out)
        self.assertEqual(c["TAG"], "v2.10.1")
        self.assertEqual(c["BASE"], "v2.10.0")

    def test_ignora_tag_fora_do_padrao(self):
        self.tag("v1.0.0")
        self.commit(self.r, "x")
        self.tag("v9.0.0-rc1")
        self.tag("v10")
        self.commit(self.r, "y")
        rc, c, out = self.proxima()
        self.assertEqual(c["TAG"], "v1.0.1", out)

    def test_head_ja_com_tag_publica_essa_tag(self):
        self.tag("v2.2.0")
        self.commit(self.r, "minor")
        self.tag("v2.3.0", anotada=True)
        rc, c, out = self.proxima()
        self.assertEqual(rc, 0, out)
        self.assertEqual(c, dict(TAG="v2.3.0", NEW="0", BASE="v2.2.0"))

    def test_head_com_duas_tags_usa_a_maior(self):
        self.tag("v1.0.0")
        self.commit(self.r, "x")
        self.tag("v1.1.0")
        self.tag("v1.0.1")
        rc, c, out = self.proxima()
        self.assertEqual(c["TAG"], "v1.1.0", out)
        self.assertEqual(c["NEW"], "0")
        self.assertEqual(c["BASE"], "v1.0.1")

    def test_stdout_so_tem_as_tres_linhas(self):
        self.tag("v1.0.0")
        self.commit(self.r, "x")
        rc, out, err = self.roda([BASH, SCRIPT], self.r)
        self.assertEqual(out.splitlines(), ["TAG=v1.0.1", "NEW=1", "BASE=v1.0.0"])

    def test_sem_tag_e_1(self):
        rc, c, out = self.proxima()
        self.assertEqual(rc, 1, out)
        self.assertEqual(c, dict())
        self.assertIn("RESULTADO: SEM VERSÃO", out)

    def test_fora_de_git_e_64(self):
        solta = self.tmp / "sem-git"
        solta.mkdir()
        rc, out, err = self.roda([BASH, SCRIPT], solta)
        self.assertEqual(rc, 64, out + err)


if __name__ == "__main__":
    unittest.main()
