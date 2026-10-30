"""Trace do sdd/bin/verify-gate.sh (F7): 1 linha JSONL por execução, sem mudar exit nem saída, e
--sem-define. Os seis exits e as fixtures continuam em tests/test_verify_gate.py.
"""
from __future__ import annotations

import json
import os
import unittest

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/verify-gate.sh"
FIXTURES = ("DEFINE_FIXTURE_CONTROLE.md", "DEFINE_FIXTURE_GOVERNANCA.md",
            "DEFINE_FIXTURE_NEEDS_CLARIFICATION.md", "DEFINE_FIXTURE_SEM_BLOCO.md")


class Trace(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin", self.r)
        self.copia("sdd/fixtures", self.r)

    def gate(self, *args: str, env: dict | None = None, cwd=None) -> tuple[int, str, str]:
        return self.roda([BASH, SCRIPT if cwd is None else "bin/verify-gate.sh", *args], cwd or self.r, env)

    def linhas(self, feature: str, pasta: str = "sdd/traces") -> list:
        p = self.r / pasta / (feature + ".jsonl")
        if not p.is_file():
            return []
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]

    def test_uma_linha_por_execucao_com_os_campos(self):
        for _ in range(2):
            rc, _, _ = self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md")
            self.assertEqual(rc, 0)
        ls = self.linhas("FIXTURE_CONTROLE")
        self.assertEqual(len(ls), 2)
        self.assertEqual(sorted(ls[0]), ["define", "exit", "feature", "kind", "src", "ts"])
        self.assertEqual((ls[0]["src"], ls[0]["kind"], ls[0]["exit"]), ("verify-gate", "test", 0))
        self.assertEqual(ls[0]["define"], "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md")
        self.assertRegex(ls[0]["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_grava_o_exit_original_mesmo_com_strict(self):
        rc, _, _ = self.gate("--strict", "sdd/fixtures/DEFINE_FIXTURE_NEEDS_CLARIFICATION.md")
        self.assertEqual(rc, 1)
        self.assertEqual(self.linhas("FIXTURE_NEEDS_CLARIFICATION")[-1]["exit"], 5)
        rc, _, _ = self.gate("sdd/fixtures/DEFINE_FIXTURE_SEM_BLOCO.md")
        self.assertEqual(rc, 64)
        self.assertEqual(self.linhas("FIXTURE_SEM_BLOCO")[-1]["exit"], 64)

    def test_vermelho_conta_no_trace(self):
        self.escreve(self.r, "sdd/features/DEFINE_X.md",
                     '## Verify Gate\n\n```yaml\nverify_gate:\n  kind: test\n  cmd: "false"\n  pass_when: "exit 0"\n```\n')
        for _ in range(3):
            self.gate("sdd/features/DEFINE_X.md")
        self.assertEqual([l["exit"] for l in self.linhas("X")], [2, 2, 2])

    def test_print_nao_grava(self):
        rc, _, _ = self.gate("--print", "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md")
        self.assertEqual(rc, 0)
        self.assertFalse((self.r / "sdd/traces").exists())

    def test_sdd_trace_off_nao_grava(self):
        rc, _, _ = self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md", env=dict(self.env, SDD_TRACE="off"))
        self.assertEqual(rc, 0)
        self.assertFalse((self.r / "sdd/traces").exists())

    def test_sdd_trace_dir_troca_a_pasta(self):
        self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md", env=dict(self.env, SDD_TRACE_DIR="outra/pasta"))
        self.assertEqual(len(self.linhas("FIXTURE_CONTROLE", "outra/pasta")), 1)

    def test_pasta_sem_escrita_nao_muda_exit_nem_saida(self):
        self.escreve(self.r, "sdd/traces", "um arquivo no lugar da pasta\n")
        for fx in FIXTURES:
            with self.subTest(fixture=fx):
                a = self.gate("sdd/fixtures/" + fx, env=dict(self.env, SDD_TRACE="off"))
                b = self.gate("sdd/fixtures/" + fx)
                self.assertEqual(a, b)

    def test_trace_sem_permissao_nao_muda_a_saida(self):
        (self.r / "sdd/traces").mkdir(parents=True)
        arq = self.escreve(self.r, "sdd/traces/FIXTURE_CONTROLE.jsonl", "")
        arq.chmod(0o444)
        tranca = self.r / "trancada"
        tranca.mkdir()
        tranca.chmod(0o555)
        try:
            a = self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md", env=dict(self.env, SDD_TRACE="off"))
            self.assertEqual(self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md"), a)
            for pasta in ("trancada", "trancada/sub"):
                with self.subTest(pasta=pasta):
                    self.assertEqual(self.gate("sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md",
                                               env=dict(self.env, SDD_TRACE_DIR=pasta)), a)
        finally:
            tranca.chmod(0o755)
            arq.chmod(0o644)

    def test_saida_igual_com_e_sem_trace(self):
        for fx in FIXTURES:
            for flags in ((), ("--strict",)):
                with self.subTest(fixture=fx, flags=flags):
                    a = self.gate(*flags, "sdd/fixtures/" + fx, env=dict(self.env, SDD_TRACE="off"))
                    b = self.gate(*flags, "sdd/fixtures/" + fx)
                    self.assertEqual(a, b)

    def test_trace_flag_e_aceita(self):
        rc, _, _ = self.gate("--trace", "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md")
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.linhas("FIXTURE_CONTROLE")), 1)

    def test_de_subpasta_com_caminho_relativo(self):
        rc, out, err = self.gate("fixtures/DEFINE_FIXTURE_CONTROLE.md", cwd=self.r / "sdd")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.linhas("FIXTURE_CONTROLE")[-1]["define"], "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md")

    def test_erro_de_uso_antes_da_raiz_nao_grava(self):
        rc, _, _ = self.gate("sdd/features/NAO_EXISTE.md")
        self.assertEqual(rc, 64)
        self.assertFalse((self.r / "sdd/traces").exists())


class SemDefine(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia(SCRIPT, self.r)

    def test_grava_release_no_define_e_sai_0(self):
        rc, out, err = self.roda([BASH, SCRIPT, "--sem-define", "HOTFIX_X"], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("release sem DEFINE", out)
        self.assertResultado(out)
        linha = json.loads((self.r / "sdd/traces/HOTFIX_X.jsonl").read_text(encoding="utf-8"))
        self.assertEqual((linha["src"], linha["kind"], linha["exit"], linha["define"]), ("release", "no-define", 0, ""))

    def test_sem_feature_e_64(self):
        rc, out, err = self.roda([BASH, SCRIPT, "--sem-define"], self.r)
        self.assertEqual(rc, 64, out + err)
        self.assertFalse((self.r / "sdd/traces").exists())

    def test_nome_vira_nome_de_arquivo_seguro(self):
        rc, _, _ = self.roda([BASH, SCRIPT, "--sem-define", 'a/b "c"'], self.r)
        self.assertEqual(rc, 0)
        self.assertEqual(os.listdir(str(self.r / "sdd/traces")), ["a_b__c_.jsonl"])

    def test_sdd_trace_off_diz_que_nao_gravou(self):
        rc, out, _ = self.roda([BASH, SCRIPT, "--sem-define", "X"], self.r, dict(self.env, SDD_TRACE="off"))
        self.assertEqual(rc, 0)
        self.assertIn("NÃO gravado", out)
        self.assertFalse((self.r / "sdd/traces").exists())


if __name__ == "__main__":
    unittest.main()
