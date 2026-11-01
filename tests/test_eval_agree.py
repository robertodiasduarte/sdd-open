"""sdd/bin/eval-agree.sh — taxa de AGREE por auditor nas revisões já feitas (F11: AT-014–AT-017).

Fixture: sdd/fixtures/revisao/eval/ — 5 pastas EXTERNAL_REVIEW_*: codex audita 1 (2 AGREE, 1 DISAGREE_EVIDENCE,
1 NOVO); openrouter audita 2, com provedores diferentes (" via …") que somam numa linha só (3 AGREE, 1
DISAGREE_CONCERN); 1 auditoria com exit 68 e 1 sem auditor.verdicts.jsonl ficam fora da conta.
A 5ª pasta usa o id com slug (openrouter:qwen/…) e outro provedor: soma na mesma linha da 2ª.
O script só lê arquivos: o teste roda sem CLI de engine no PATH e com proxies mortos.
"""
from __future__ import annotations

import shutil
import sys

from apoio import BASH, RAIZ, Sandbox

EA = RAIZ / "sdd/bin/eval-agree.sh"
FIX = RAIZ / "sdd/fixtures/revisao/eval"


class EvalAgree(Sandbox):
    def setUp(self):
        super().setUp()
        binp = self.tmp / "bin"
        binp.mkdir()
        for f in ("git", "bash", "sh", "sed"):
            w = shutil.which(f)
            if w:
                (binp / f).symlink_to(w)
        (binp / "python3").symlink_to(sys.executable)
        self.env = dict(self.env, PATH=str(binp), http_proxy="http://127.0.0.1:9", https_proxy="http://127.0.0.1:9",
                        HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9")
        self.env.pop("OPENROUTER_API_KEY", None)

    def ea(self, *args, cwd=None):
        rc, out, err = self.roda([BASH, EA, *args], cwd or self.tmp)
        return rc, out + err

    def test_at014_numeros_exatos_da_fixture(self):
        rc, out = self.ea(FIX)
        self.assertEqual(rc, 0, out)
        self.assertIn("(5 pasta(s) lida(s) em ", out)
        self.assertIn("| codex (-) | 1 | 4 | 2 | 1 | 0 | 1 | 66.7% |", out)
        self.assertIn("| openrouter (qwen/qwen3.7-plus) | 2 | 4 | 3 | 0 | 1 | 0 | 75.0% |", out)
        self.assertNotIn("via", out.split("fora da conta")[0])
        self.assertIn("RESULTADO: MEDIDO", out)

    def test_at015_fora_da_conta_com_o_motivo(self):
        rc, out = self.ea(FIX)
        self.assertIn("fora da conta: 2 (EXTERNAL_REVIEW_20260101-000003: auditor_exit 68; "
                      "EXTERNAL_REVIEW_20260101-000004: sem auditor.verdicts.jsonl)", out)
        self.assertNotIn("claude (claude-exemplo)", out)
        self.assertNotIn("gemini (gemini-exemplo)", out)

    def test_at016_sem_dados_e_uso(self):
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        rc, out = self.ea(vazia)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: SEM DADOS", out)
        self.assertIn("(0 pasta(s) lida(s)", out)
        so_ruins = self.tmp / "ruins"
        for d in ("EXTERNAL_REVIEW_20260101-000003", "EXTERNAL_REVIEW_20260101-000004"):
            shutil.copytree(str(FIX / d), str(so_ruins / d))
        rc, out = self.ea(so_ruins)
        self.assertEqual(rc, 2, out)
        self.assertIn("fora da conta: 2", out)
        rc, out = self.ea(self.tmp / "nao-existe")
        self.assertEqual(rc, 64, out)
        rc, out = self.ea("--executar")
        self.assertEqual(rc, 64, out)
        rc, out = self.ea(FIX, "outra")
        self.assertEqual(rc, 64, out)

    def test_at014_pasta_padrao_vem_do_output_dir(self):
        r = self.repo()
        self.escreve(r, "sdd/config.yaml", "review:\n  output_dir: revisoes/adv  # comentário\n")
        shutil.copytree(str(FIX), str(r / "revisoes/adv"))
        rc, out = self.ea(cwd=r)
        self.assertEqual(rc, 0, out)
        self.assertIn("revisoes/adv", out)
        self.assertIn("| codex (-) | 1 | 4 | 2 | 1 | 0 | 1 | 66.7% |", out)

    def test_aval1_l3_projeto_sem_revisoes_ainda_e_sem_dados(self):
        r = self.repo()
        rc, out = self.ea(cwd=r)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: SEM DADOS", out)
        self.assertIn("(0 pasta(s) lida(s)", out)

    def test_aval1_l4_sem_git_no_path_usa_a_pasta_atual(self):
        d = self.tmp / "sem-git"
        shutil.copytree(str(FIX), str(d / "sdd/reports/reviews"))
        binp = self.tmp / "bin-sem-git"
        binp.mkdir()
        for f in ("bash", "sh", "sed"):
            w = shutil.which(f)
            if w:
                (binp / f).symlink_to(w)
        (binp / "python3").symlink_to(sys.executable)
        rc, out, err = self.roda([BASH, EA], d, dict(self.env, PATH=str(binp)))
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("Traceback", out + err)
        self.assertIn("| codex (-) | 1 | 4 | 2 | 1 | 0 | 1 | 66.7% |", out)

    def test_at017_so_le_arquivos(self):
        texto = EA.read_text(encoding="utf-8")
        for proibido in ("urllib", "socket", "adapters/", "http.client"):
            self.assertNotIn(proibido, texto)
        rc, out = self.ea(FIX)
        self.assertEqual(rc, 0, out)
