"""sdd/bin/adapters/*.sh — os 4 adapters reais da revisão adversarial (F10: AT-010, AT-020).

Três provas, todas sem rede e sem engine de verdade:
- extração: `adapter_extrair` sobre as saídas medidas das CLIs e da API (sdd/fixtures/revisao/saidas/);
- invocação das CLIs: binários falsos `claude`, `codex` e `gemini` (sdd/fixtures/revisao/bin/) gravam argv,
  pasta atual e stdin, e o teste confere as flags exatas, a pasta temporária vazia e o prompt por stdin;
- OpenRouter: um servidor HTTP local (SDD_REVIEW_OPENROUTER_URL) captura o corpo da requisição.
A chave usada aqui é gerada em execução e não vale em lugar nenhum.
"""
from __future__ import annotations

import http.server
import json
import os
import re
import secrets
import shutil
import sys
import threading
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

AR = RAIZ / "sdd/bin/adversarial-review.sh"
ADAPTERS = RAIZ / "sdd/bin/adapters"
SAIDAS = RAIZ / "sdd/fixtures/revisao/saidas"
FAKE = RAIZ / "sdd/fixtures/revisao/bin"
FERRAMENTAS = ("git", "bash", "sh", "cat", "ls", "pwd", "printf", "dirname", "mkdir", "env", "sed", "rm")


def ler(p) -> str:
    return Path(p).read_text(encoding="utf-8")


class Extracao(Sandbox):
    def extrai(self, adapter, arquivo):
        rc, out, err = self.roda([BASH, "-c", 'source "$1"; adapter_extrair "$2"', "_", ADAPTERS / (adapter + ".sh"),
                                  SAIDAS / arquivo], self.tmp)
        self.assertEqual(rc, 0, err)
        return json.loads(out.strip().splitlines()[-1])

    def test_os_4_formatos(self):
        c = self.extrai("claude", "claude.json")
        self.assertIn("<<<VERDICTS", c["texto"])
        self.assertEqual((c["tokens_entrada"], c["tokens_saida"], c["modelo"]), (3591, 4, "claude-opus-5-5"))
        self.assertAlmostEqual(c["custo_usd"], 0.0238641)
        x = self.extrai("codex", "codex.jsonl")
        self.assertEqual((x["tokens_entrada"], x["tokens_saida"], x["custo_usd"]), (24673, 5, None))
        self.assertIn("<<<VERDICTS", x["texto"])
        g = self.extrai("gemini", "gemini.json")
        self.assertEqual((g["tokens_entrada"], g["tokens_saida"], g["modelo"], g["custo_usd"]),
                         (1830, 42, "gemini-3.8-flash", None))
        o = self.extrai("openrouter", "openrouter.json")
        self.assertEqual((o["tokens_entrada"], o["tokens_saida"], o["modelo"]), (16, 136, "qwen/qwen3.7-plus via Alibaba"))
        self.assertAlmostEqual(o["custo_usd"], 0.0001792)

    def test_saida_de_erro_vira_texto_vazio(self):
        for adapter, conteudo in (("claude", '{"is_error": true, "result": "x"}'),
                                  ("codex", '{"type":"error","message":"401 Unauthorized"}'),
                                  ("gemini", '{"error": {"type": "ProjectIdRequiredError", "code": 41}}'),
                                  ("openrouter", '{"error": {"message": "User not found.", "code": 401}}'),
                                  ("claude", "não é json")):
            with self.subTest(adapter=adapter, conteudo=conteudo[:20]):
                f = self.escreve(self.tmp, "saida.txt", conteudo)
                rc, out, _ = self.roda([BASH, "-c", 'source "$1"; adapter_extrair "$2"', "_",
                                        ADAPTERS / (adapter + ".sh"), f], self.tmp)
                self.assertEqual(json.loads(out)["texto"], "")

    def test_cada_adapter_define_as_4_funcoes(self):
        for a in ("claude", "codex", "gemini", "openrouter"):
            rc, out, err = self.roda([BASH, "-c", 'source "$1"; for f in adapter_disponivel adapter_invocar '
                                      'adapter_extrair adapter_credencial; do type "$f" >/dev/null || exit 1; done; '
                                      'adapter_credencial', "_", ADAPTERS / (a + ".sh")], self.tmp)
            with self.subTest(adapter=a):
                self.assertEqual(rc, 0, err)
                self.assertTrue(out.strip())


class Invocacao(Sandbox):
    def setUp(self):
        super().setUp()
        binp = self.tmp / "bin"
        binp.mkdir()
        for f in FERRAMENTAS:
            w = shutil.which(f)
            if w:
                (binp / f).symlink_to(w)
        (binp / "python3").symlink_to(sys.executable)
        for c in ("claude", "codex", "gemini"):
            (binp / c).symlink_to(FAKE / c)
        self.log = self.tmp / "log"
        self.log.mkdir()
        self.env = dict(self.env, PATH=str(binp), SDD_FAKE_LOG=str(self.log), SDD_FAKE_SAIDAS=str(SAIDAS),
                        SDD_REVIEW_ESPERA="0")
        for k in ("OPENROUTER_API_KEY", "SDD_REVIEW_ADAPTERS", "SDD_REVIEW_OPENROUTER_URL"):
            self.env.pop(k, None)
        r = self.repo()
        self.git(r, "checkout", "-q", "-b", "main")
        self.escreve(r, "src/a.sh", "a\n")
        self.commit(r, "base")
        self.escreve(r, "src/a.sh", "a\nmudou\n")
        with open(r / ".git/info/exclude", "a", encoding="utf-8") as h:
            h.write("sdd/reports/reviews/\n")
        self.r = r

    def ar(self, *args):
        rc, out, err = self.roda([BASH, AR, "--base", "main", "--no-revisor2", "--no-desempate", *args], self.r, self.env)
        return rc, out + err

    def confere(self, cli, flags):
        argv = ler(self.log / (cli + ".argv")).splitlines()
        self.assertEqual(argv, flags)
        cwd = ler(self.log / (cli + ".cwd")).strip()
        self.assertNotEqual(os.path.realpath(cwd), os.path.realpath(str(self.r)))
        self.assertEqual(ler(self.log / (cli + ".ls")), "")
        stdin = ler(self.log / (cli + ".stdin"))
        self.assertIn("## DIFF", stdin)
        self.assertIn("+mudou", stdin)

    def test_claude_e_codex_com_as_flags_exatas(self):
        rc, out = self.ar("--reviewer", "claude", "--auditor", "codex")
        self.assertEqual(rc, 0, out)
        self.confere("claude", ["-p", "--output-format", "json", "--tools", "", "--safe-mode",
                                "--no-session-persistence"])
        self.confere("codex", ["exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral", "--json", "-"])
        meta = ler(sorted((self.r / "sdd/reports/reviews").glob("EXTERNAL_REVIEW_*"))[-1] / "META.txt")
        self.assertRegex(meta, r"(?m)^reviewer_custo\s*:\s*US\$ 0\.0239$")
        self.assertRegex(meta, r"(?m)^auditor_custo\s*:\s*assinatura$")
        self.assertRegex(meta, r"(?m)^diversidade\s*:\s*vendor$")

    def test_gemini_e_modelo_explicito(self):
        rc, out = self.ar("--reviewer", "claude:claude-sonnet-5-5", "--auditor", "gemini")
        self.assertEqual(rc, 0, out)
        self.confere("claude", ["-p", "--output-format", "json", "--tools", "", "--safe-mode",
                                "--no-session-persistence", "--model", "claude-sonnet-5-5"])
        self.confere("gemini", ["-o", "json", "--approval-mode", "default"])
        meta = ler(sorted((self.r / "sdd/reports/reviews").glob("EXTERNAL_REVIEW_*"))[-1] / "META.txt")
        self.assertRegex(meta, r"(?m)^auditor_custo\s*:\s*\$\?$")

    def test_openrouter_manda_data_collection_deny_e_le_o_custo(self):
        corpos, cabecalhos = [], []
        resposta = (SAIDAS / "openrouter.json").read_bytes()

        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                n = int(self.headers.get("Content-Length") or 0)
                corpos.append(json.loads(self.rfile.read(n)))
                cabecalhos.append(dict(self.headers))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(resposta)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        chave = "teste-" + secrets.token_hex(8)
        self.env = dict(self.env, OPENROUTER_API_KEY=chave,
                        SDD_REVIEW_OPENROUTER_URL="http://127.0.0.1:%d/v1/chat/completions" % srv.server_port)
        rc, out = self.ar("--reviewer", "claude", "--auditor", "openrouter:qwen/qwen3.7-plus")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(corpos), 1)
        c = corpos[0]
        self.assertEqual(c["model"], "qwen/qwen3.7-plus")
        self.assertEqual(c["provider"], {"data_collection": "deny", "require_parameters": True})
        self.assertEqual(c["usage"], {"include": True})
        self.assertIn("## REVISÕES", c["messages"][0]["content"])
        self.assertEqual(cabecalhos[0].get("Authorization"), "Bearer " + chave)
        pasta = sorted((self.r / "sdd/reports/reviews").glob("EXTERNAL_REVIEW_*"))[-1]
        meta = ler(pasta / "META.txt")
        self.assertRegex(meta, r"(?m)^auditor_custo\s*:\s*US\$ 0\.0002$")
        self.assertRegex(meta, r"(?m)^auditor_modelo\s*:\s*qwen/qwen3\.7-plus via Alibaba$")
        for f in pasta.iterdir():
            self.assertNotIn(chave, f.read_text(encoding="utf-8", errors="replace"), f.name)
        self.assertNotIn(chave, out)

    def test_openrouter_sem_chave_e_65_com_onde_ela_mora(self):
        rc, out = self.ar("--reviewer", "openrouter", "--auditor", "claude")
        self.assertEqual(rc, 65, out)
        self.assertIn("OPENROUTER_API_KEY no ambiente", out)

    def test_openrouter_401_e_auth(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length") or 0))
                self.send_response(401)
                self.end_headers()
                self.wfile.write(b'{"error":{"message":"User not found.","code":401}}')

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        self.env = dict(self.env, OPENROUTER_API_KEY="teste-" + secrets.token_hex(8),
                        SDD_REVIEW_OPENROUTER_URL="http://127.0.0.1:%d/" % srv.server_port)
        rc, out = self.ar("--reviewer", "openrouter,claude", "--auditor", "codex")
        self.assertEqual(rc, 65, out)
        self.assertFalse((self.log / "claude.argv").exists())

    def test_openrouter_401_sem_corpo_e_auth(self):
        # rodada 2 da revisão real (R3@codex): erro HTTP sem corpo JSON também é classificado
        class H(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length") or 0))
                self.send_response(401)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        self.env = dict(self.env, OPENROUTER_API_KEY="teste-" + secrets.token_hex(8),
                        SDD_REVIEW_OPENROUTER_URL="http://127.0.0.1:%d/" % srv.server_port)
        rc, out = self.ar("--reviewer", "openrouter,claude", "--auditor", "codex")
        self.assertEqual(rc, 65, out)
        self.assertFalse((self.log / "claude.argv").exists())
