"""Desenho dos workflows lido como texto: permissões, ordem dos jobs, gatilhos e checks que não mudam.

Sem parser YAML (só stdlib): os asserts procuram as linhas que sustentam cada garantia. O que só se
prova rodando no GitHub (a Release publicada) é conferido depois do merge, fora desta suíte.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

RELEASE = (RAIZ / ".github/workflows/release.yml").read_text(encoding="utf-8")
GATE = (RAIZ / ".github/workflows/publish-gate.yml").read_text(encoding="utf-8")


def sem_comentarios(texto: str) -> str:
    """Só as linhas de YAML: os comentários explicam as garantias e citam as palavras proibidas."""
    return "\n".join(l for l in texto.splitlines() if not l.lstrip().startswith("#"))

PRODUTO = [".agents/skills/**", "bin/**", "sdd/bin/**", "sdd/templates/**", "sdd/fixtures/**",
           "sdd/playbook.md", "sdd/config.example.yaml", "AGENTS.md.tmpl"]


def job(texto: str, nome: str) -> str:
    """Bloco de um job: da linha `  nome:` até o próximo job de mesmo recuo ou o fim."""
    m = re.search(r"^  " + re.escape(nome) + r":\n(.*?)(?=^  [a-z][a-z0-9_-]*:\n|\Z)", texto, re.M | re.S)
    assert m, "job ausente: " + nome
    return m.group(1)


class Release(unittest.TestCase):
    def test_token_global_so_le(self):
        topo = RELEASE.split("\njobs:\n", 1)[0]
        self.assertRegex(topo, r"(?m)^permissions:\n  contents: read$")

    def test_testes_nao_tem_escrita(self):
        self.assertNotIn("contents: write", job(RELEASE, "testes"))

    def test_release_depende_dos_testes_e_e_o_unico_com_escrita(self):
        bloco = job(RELEASE, "release")
        self.assertRegex(bloco, r"(?m)^    needs: testes$")
        self.assertIn("contents: write", bloco)
        self.assertEqual(sem_comentarios(RELEASE).count("contents: write"), 1)

    def test_nada_que_mascara_falha(self):
        for texto, nome in ((RELEASE, "release.yml"), (GATE, "publish-gate.yml")):
            texto = sem_comentarios(texto)
            with self.subTest(workflow=nome):
                self.assertNotIn("continue-on-error", texto)
                self.assertNotIn("|| true", texto)

    def test_gatilho_push_em_main_nos_paths_do_produto(self):
        self.assertRegex(RELEASE, r"(?m)^    branches: \[main\]$")
        for p in PRODUTO:
            with self.subTest(path=p):
                self.assertIn("      - '" + p + "'", RELEASE)

    def test_tag_manual_tambem_publica(self):
        self.assertRegex(RELEASE, r"(?m)^    tags: \['v\*'\]$")

    def test_fila_sem_cancelar(self):
        self.assertIn("cancel-in-progress: false", RELEASE)

    def test_testes_rodam_gate_suite_e_versao_com_base_obrigatoria(self):
        bloco = job(RELEASE, "testes")
        self.assertIn("bash scripts/publish-gate.sh", bloco)
        self.assertIn("python3 -B -m unittest discover -s tests -p 'test_*.py'", bloco)
        self.assertIn("bash scripts/next-version.sh", bloco)
        self.assertIn("--base-obrigatoria", bloco)
        self.assertIn("PUBLISH_GATE_MODE: ci", bloco)

    def test_publicacao_com_pacote_hash_e_release_idempotente(self):
        bloco = job(RELEASE, "release")
        self.assertIn("bash scripts/next-version.sh", bloco)
        self.assertIn("git archive --format=tar.gz", bloco)
        self.assertIn("sha256sum", bloco)
        self.assertIn("SHA256SUMS.txt", bloco)
        self.assertIn('gh release view "$TAG"', bloco)
        self.assertIn('gh release create "$TAG" --target "$GITHUB_SHA"', bloco)
        self.assertLess(bloco.index("gh release view"), bloco.index("gh release create"))

    def test_checkout_com_historico_e_tags(self):
        for nome in ("testes", "release"):
            with self.subTest(job=nome):
                self.assertIn("fetch-depth: 0", job(RELEASE, nome))

    def test_actions_fixadas_por_sha(self):
        for texto, nome in ((RELEASE, "release.yml"), (GATE, "publish-gate.yml")):
            for uso in re.findall(r"uses: (\S+)", texto):
                with self.subTest(workflow=nome, uses=uso):
                    self.assertRegex(uso, r"@[0-9a-f]{40}$")


class PublishGate(unittest.TestCase):
    """AT-025 no CI: os checks inline continuam; a suíte e o gate de versão foram acrescentados."""

    def test_checks_inline_das_fixtures_continuam(self):
        for linha in ("check DEFINE_FIXTURE_NEEDS_CLARIFICATION.md 5",
                      "check DEFINE_FIXTURE_CONTROLE.md 0",
                      "check DEFINE_FIXTURE_SEM_BLOCO.md 64",
                      "bash sdd/bin/playbook-lint.sh --self-test",
                      "python3 sdd/bin/skill-lint.py .agents/skills/sdd-*/SKILL.md",
                      'bash "$GITHUB_WORKSPACE/bin/sdd-open.sh" sync --check'):
            with self.subTest(linha=linha):
                self.assertIn(linha, GATE)

    def test_roda_a_suite_e_o_gate_de_versao(self):
        self.assertIn("python3 -B -m unittest discover -s tests -p 'test_*.py'", GATE)
        self.assertIn("scripts/check-versions.py --base", GATE)
        self.assertIn("fetch-depth: 0", GATE)


if __name__ == "__main__":
    unittest.main()
