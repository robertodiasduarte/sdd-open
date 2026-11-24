"""A suíte desliga a manutenção automática do git (tests/apoio.py).

O `git commit` dispara `git maintenance run --auto --detach`: o maintenance.lock aparece e some em segundo plano e muda o
hash da pasta no meio do teste (CI macOS da v2.27.1; suspeita no da v2.27.2). A trava vale também para a fixture que tem
gitconfig próprio (F25), porque vem do ambiente do processo.
"""
from __future__ import annotations

import os
import unittest

from apoio import Sandbox


class SemManutencaoAutomatica(Sandbox):
    def trace_do_commit(self, env: dict) -> str:
        r = self.repo()
        self.escreve(r, "a.txt", "a\n")
        self.git(r, "add", "-A")
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "c"], r, dict(env, GIT_TRACE="1"))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("commit", err)   # o trace saiu: ausência de "maintenance" quer dizer alguma coisa
        return err

    def test_sandbox(self):
        self.assertNotIn("maintenance run", self.trace_do_commit(self.env))

    def test_gitconfig_proprio(self):
        cfg = self.escreve(self.tmp, "gitconfig-proprio", "[init]\n\tdefaultBranch = main\n")
        env = dict(os.environ, GIT_CONFIG_GLOBAL=str(cfg), GIT_CONFIG_NOSYSTEM="1",
                   **{k: v for k, v in self.env.items() if k.startswith(("GIT_AUTHOR", "GIT_COMMITTER"))})
        self.assertNotIn("maintenance run", self.trace_do_commit(env))


if __name__ == "__main__":
    unittest.main()
