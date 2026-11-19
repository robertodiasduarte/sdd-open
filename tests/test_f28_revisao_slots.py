"""F28 — adversarial-review.sh: a escolha deste computador (git config), a origem e o --dry-run sem diff.

AT-005: a flag vence o slot do sdd/config.yaml, que vence o git config (sdd.revisor1, sdd.auditor); o plano diz a
origem; dois modelos do OpenRouter dão diversidade "modelo"; o mesmo modelo nos dois continua 67.
AT-006: o --dry-run mostra as engines (com a disponibilidade e os papéis extras) mesmo sem diff e sem base, e sai 0;
a revisão real sem diff continua 64.
Coerência: o diagnosticar.sh da skill e o --dry-run resolvem os mesmos ids com a mesma origem.

Sem rede e sem engine de verdade: os stubs de sdd/fixtures/revisao (como o tests/test_revisao.py) ou os adapters
reais com o PATH sem claude, codex e gemini e a chave do OpenRouter como texto de fixture.
"""
from __future__ import annotations

import os
import re
import shutil
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox, path_restrito

AR = RAIZ / "sdd/bin/adversarial-review.sh"
DIAG = RAIZ / ".agents/skills/sdd-configurar-revisores/scripts/diagnosticar.sh"
FXR = RAIZ / "sdd/fixtures/revisao"
REG_STUB = FXR / "registry-stub.tsv"
FERRAMENTAS = ("git", "bash", "sh", "cp", "ls", "grep", "tr", "cat", "mkdir", "sleep", "dirname", "sed", "env",
               "rm", "printf", "wc", "head", "tail", "awk", "uname")
CHAVE_FIXTURE = "fixture-nao-e-chave-" + "ab12"
CLI_FALSA = "#!/bin/sh\nexit 0\n"


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.env.pop("OPENROUTER_API_KEY", None)
        self.env = dict(self.env, SDD_REVIEW_ESPERA="0", SDD_REVIEW_OPENROUTER_URL="http://127.0.0.1:9/")
        self.path_sem_cli = path_restrito(self.tmp / "bin", FERRAMENTAS, ausentes=("claude", "codex", "gemini"))

    def env_stub(self) -> dict:
        return dict(self.env, PATH=self.path_sem_cli, SDD_REVIEW_ADAPTERS=str(FXR / "adapters"))

    def env_real(self, chave: bool = False, clis=()) -> dict:
        pasta = self.tmp / ("bin-cli-" + "-".join(clis) if clis else "bin")
        falsas = {}
        for c in clis:
            f = self.tmp / "falsas" / c
            f.parent.mkdir(exist_ok=True)
            f.write_text(CLI_FALSA, encoding="utf-8")
            f.chmod(0o755)
            falsas[c] = f
        path = self.path_sem_cli if not clis else path_restrito(pasta, FERRAMENTAS, extra=falsas)
        e = dict(self.env, PATH=path)
        if chave:
            e["OPENROUTER_API_KEY"] = CHAVE_FIXTURE
        return e

    def projeto(self, cfg: str = "", registry=REG_STUB, com_diff: bool = True, pacote: bool = False) -> Path:
        self.n_repo = getattr(self, "n_repo", 0) + 1
        r = self.repo("repo%d" % self.n_repo)
        self.git(r, "checkout", "-q", "-b", "main")
        self.escreve(r, "src/conta.sh", "a\n")
        if pacote:   # o que o diagnóstico precisa do projeto: a revisão, os adapters e as tabelas
            for rel in ("sdd/bin/adversarial-review.sh", "sdd/bin/lib", "sdd/bin/adapters", "sdd/review/registry.tsv",
                        "sdd/review/precos.tsv"):
                self.copia(rel, r)
        self.escreve(r, "sdd/config.yaml", "review:\n%s%s" % (
            "" if pacote else "  registry: %s\n" % registry, cfg))
        self.commit(r, "base")
        self.git(r, "checkout", "-q", "-b", "feat")
        if com_diff:
            self.escreve(r, "src/conta.sh", "a\nb\n")
        with open(r / ".git/info/exclude", "a", encoding="utf-8") as h:
            h.write("sdd/reports/reviews/\n")
        return r

    def ar(self, r: Path, *args, env=None):
        rc, out, err = self.roda([BASH, AR, *args], r, env or self.env_stub())
        return rc, out + err

    def diag(self, r: Path, *args, env=None):
        rc, out, err = self.roda([BASH, DIAG, *args], r, env or self.env_real())
        return rc, out + err


class Origem(Base):
    """AT-005."""

    def test_git_config_vale_com_o_slot_vazio_e_o_plano_diz_a_origem(self):
        r = self.projeto()
        self.git(r, "config", "--local", "sdd.revisor1", "stub-a")
        self.git(r, "config", "--local", "sdd.auditor", "stub-b")
        rc, out = self.ar(r, "--base", "main", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"revisor : stub-a .* — origem: este computador \(git config sdd\.revisor1\)")
        self.assertRegex(out, r"auditor : stub-b .* — origem: este computador \(git config sdd\.auditor\)")

    def test_slot_vence_o_git_config_e_a_flag_vence_os_dois(self):
        r = self.projeto("  revisor1: stub-c\n  auditor: stub-b\n")
        self.git(r, "config", "--local", "sdd.revisor1", "stub-a")
        _, out = self.ar(r, "--base", "main", "--dry-run")
        self.assertRegex(out, r"revisor : stub-c .* — origem: sdd/config\.yaml")
        _, out = self.ar(r, "--base", "main", "--dry-run", "--reviewer", "stub-d")
        self.assertRegex(out, r"revisor : stub-d .* — origem: flag --reviewer")

    def test_slot_vazio_sem_git_config_e_64_citando_a_skill(self):
        r = self.projeto()
        rc, out = self.ar(r, "--base", "main", "--dry-run")
        self.assertEqual(rc, 64, out)
        self.assertIn("review.revisor1", out)
        self.assertIn("sdd-configurar-revisores", out)

    def test_dois_modelos_do_openrouter_sao_diversidade_modelo_e_o_mesmo_e_67(self):
        r = self.projeto(pacote=True)
        self.git(r, "config", "--local", "sdd.revisor1", "openrouter:prov/modelo-a")
        self.git(r, "config", "--local", "sdd.auditor", "openrouter:prov/modelo-b")
        rc, out = self.ar(r, "--base", "main", "--dry-run", env=self.env_real())
        self.assertEqual(rc, 0, out)
        self.assertIn("diversidade: modelo", out)
        self.git(r, "config", "--local", "sdd.auditor", "openrouter:prov/modelo-a")
        rc, out = self.ar(r, "--base", "main", "--dry-run", env=self.env_real())
        self.assertEqual(rc, 67, out)


class DryRun(Base):
    """AT-006."""

    def test_sem_diff_mostra_o_plano_e_sai_0_e_a_revisao_real_continua_64(self):
        r = self.projeto("  revisor1: stub-a\n  auditor: stub-b\n", com_diff=False)
        rc, out = self.ar(r, "--base", "main", "--dry-run")
        self.assertEqual(rc, 0, out)
        for trecho in ("revisor : stub-a", "auditor : stub-b", "diff: vazio", "RESULTADO: PLANO"):
            self.assertIn(trecho, out)
        rc, out = self.ar(r, "--base", "main")
        self.assertEqual(rc, 64, out)
        self.assertIn("está vazio", out)

    def test_sem_base_e_aviso_com_a_consequencia_e_sai_0(self):
        r = self.repo()
        self.git(r, "checkout", "-q", "-b", "outra")
        self.escreve(r, "sdd/config.yaml", "review:\n  registry: %s\n  revisor1: stub-a\n  auditor: stub-b\n" % REG_STUB)
        self.commit(r, "base")
        rc, out = self.ar(r, "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ diff: sem base para comparar", out)
        self.assertIn("a revisão real vai parar", out)

    def test_disponibilidade_e_papeis_extras_sem_engine(self):
        r = self.projeto(pacote=True)
        self.git(r, "config", "--local", "sdd.revisor1", "openrouter:prov/modelo-a")
        self.git(r, "config", "--local", "sdd.auditor", "openrouter:prov/modelo-b")
        _, out = self.ar(r, "--base", "main", "--dry-run", env=self.env_real())
        self.assertIn("indisponível (falta: OPENROUTER_API_KEY", out)
        self.assertIn("2º revisor (se acionado): nenhuma engine disponível", out)
        self.assertIn("--aceitar-sem-revisor2", out)
        self.assertIn("desempate (se acionado): nenhuma engine disponível", out)

    def test_com_a_chave_e_uma_cli_os_papeis_extras_sao_dela_e_a_chave_nunca_aparece(self):
        r = self.projeto(pacote=True)
        self.git(r, "config", "--local", "sdd.revisor1", "openrouter:prov/modelo-a")
        self.git(r, "config", "--local", "sdd.auditor", "openrouter:prov/modelo-b")
        rc, out = self.ar(r, "--base", "main", "--dry-run", env=self.env_real(chave=True, clis=("claude",)))
        self.assertEqual(rc, 0, out)
        self.assertEqual(out.count("· disponível"), 2, out)
        self.assertIn("2º revisor (se acionado): claude", out)
        self.assertIn("desempate (se acionado): claude", out)
        self.assertNotIn(CHAVE_FIXTURE, out)


class Coerencia(Base):
    """O diagnóstico e o --dry-run resolvem os mesmos ids, com a mesma origem."""

    def test_quatro_configuracoes(self):
        casos = (
            ("", {"sdd.revisor1": "openrouter:prov/a", "sdd.auditor": "openrouter:prov/b"}),
            ("  revisor1: openrouter:prov/c\n  auditor: openrouter:prov/d\n", {}),
            ("  revisor1: \"openrouter:prov/e\"   # do time\n  auditor: ''\n", {"sdd.auditor": "openrouter:prov/f"}),
            ("  revisor1: openrouter:prov/g\n  auditor: openrouter:prov/h\n", {"sdd.revisor1": "openrouter:prov/x"}),
        )
        for n, (cfg, gc) in enumerate(casos):
            with self.subTest(caso=n):
                r = self.projeto(cfg, pacote=True)
                for k, v in gc.items():
                    self.git(r, "config", "--local", k, v)
                env = self.env_real(chave=True)
                _, plano = self.ar(r, "--base", "main", "--dry-run", env=env)
                _, diag = self.diag(r, env=env)
                for papel in ("revisor", "auditor"):
                    m = re.search(r"^  %s : (\S+) .* — origem: (.+)$" % papel, plano, re.M)
                    d = re.search(r"^%s: (\S+) \(origem: (.+)\)$" % papel, diag, re.M)
                    self.assertTrue(m and d, plano + diag)
                    self.assertEqual(m.groups(), d.groups(), plano + diag)


if __name__ == "__main__":
    unittest.main()
