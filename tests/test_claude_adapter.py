"""O adaptador do Claude Code que o `init --vendors claude` gera: os 2 guards de .claude/hooks/ (cópias
marcadas de bin/adapters/claude/), as 2 entradas em .claude/settings.json (merge que preserva o resto) e
o comportamento dos guards com o payload do hook no stdin — negar, silenciar ou avisar (falha aberta).

O nome da ferramenta do vendor mora só em bin/adapters/claude/, no gerado e aqui (tests/ e bin/ ficam fora
do escopo de tests/test_agnostico.py).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from apoio import BASH, PYTHON, RAIZ, Sandbox

CLI = RAIZ / "bin/sdd-open.sh"
FIX = RAIZ / "sdd/fixtures/hooks"
RELATORIO_OK = (
    "# BUILD REPORT: X\n\n| ID | Critério (EARS) | Resultado | Evidência |\n|----|---|---|---|\n"
    "| AT-001 | When x, the system shall y | false | — |\n\navaliador: N.A. (1 camada)\n"
)
GUARDS = ("sdd-report-guard.py", "sdd-avaliador-guard.py")
FERRAMENTAS = ("bash", "sh", "git", "awk", "sed", "grep", "tr", "wc", "basename", "dirname", "mktemp", "cat",
               "head", "tail", "cmp", "od", "rm", "env", "cut", "sort", "uniq", "ls", "cp", "mkdir", "chmod",
               "mv", "find", "paste", "touch", "uname", "readlink", "date")


class Projeto(Sandbox):
    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        self.escreve(self.p, "AGENTS.md", "# Meu projeto\n")
        self.commit(self.p, "base")

    def cli(self, *args: str, env: dict | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, CLI, *args], self.p, env=env)
        return rc, out + err

    def settings(self) -> dict:
        return json.loads((self.p / ".claude/settings.json").read_text(encoding="utf-8"))

    def comandos(self) -> list:
        pre = self.settings()["hooks"]["PreToolUse"]
        return [h["command"] for e in pre for h in e["hooks"]]

    def guard(self, nome: str, payload: dict, env: dict | None = None) -> tuple[int, str, str]:
        r = subprocess.run([PYTHON, "-B", str(self.p / ".claude/hooks" / nome)], cwd=str(self.p),
                           env=env or dict(self.env, CLAUDE_PROJECT_DIR=str(self.p)), input=json.dumps(payload),
                           capture_output=True, encoding="utf-8", errors="replace", timeout=120)
        return r.returncode, r.stdout, r.stderr

    def payload(self, nome: str, **troca: str) -> dict:
        texto = (FIX / nome).read_text(encoding="utf-8")
        for k, v in troca.items():
            texto = texto.replace("__%s__" % k, json.dumps(v)[1:-1])
        return json.loads(texto.replace("__CWD__", str(self.p)))

    # ── AT-020: geração ──────────────────────────────────────────────────────────────────────────
    def test_init_gera_os_guards_e_as_entradas_do_settings(self):
        rc, out = self.cli("init", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        for g in GUARDS:
            copia = self.p / ".claude/hooks" / g
            with self.subTest(guard=g):
                self.assertIn("+ .claude/hooks/%s (novo)" % g, out)
                texto = copia.read_text(encoding="utf-8")
                self.assertIn("# sdd-open:generated - fonte: bin/adapters/claude/%s (pacote sdd-open)" % g, texto)
                self.assertEqual(texto.count("sdd-open:generated"), 2)
                r = subprocess.run([PYTHON, "-B", "-m", "py_compile", str(copia)], capture_output=True)
                self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("+ .claude/settings.json (novo)", out)
        pre = self.settings()["hooks"]["PreToolUse"]
        self.assertEqual([e["matcher"] for e in pre], ["Write|Edit|MultiEdit", "Agent|Task"])
        self.assertEqual(self.comandos(), ['python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-report-guard.py"',
                                           'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/sdd-avaliador-guard.py"'])
        self.assertEqual(pre[0]["hooks"][0]["timeout"], 10)
        self.assertNotIn("timeout", pre[1]["hooks"][0])
        self.assertIn("✅ claude: gerado (.claude/skills · CLAUDE.md · .claude/hooks + settings.json)", out)

    # ── AT-021: merge, idempotência, --check, falhas ─────────────────────────────────────────────
    def test_merge_preserva_o_settings_do_usuario_e_nao_duplica(self):
        (self.p / ".claude").mkdir()
        shutil.copy2(str(FIX / "settings-com-outros-hooks.json"), str(self.p / ".claude/settings.json"))
        rc, out = self.cli("init", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        d = self.settings()
        self.assertEqual(d["permissions"]["allow"], ["Bash(git status:*)"])
        self.assertEqual(d["hooks"]["Stop"][0]["hooks"][0]["command"], "echo fim-da-sessao")
        self.assertEqual(self.comandos()[0], "echo hook-do-usuario")
        self.assertEqual(len(self.comandos()), 3)
        antes = (self.p / ".claude/settings.json").read_bytes()
        rc, out = self.cli("sync", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        self.assertEqual((self.p / ".claude/settings.json").read_bytes(), antes)
        rc, out = self.cli("sync", "--check", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: EM DIA", out)

    def test_check_acusa_guard_editado_e_entrada_removida(self):
        self.cli("init", "--yes", "--vendors", "claude")
        copia = self.p / ".claude/hooks/sdd-report-guard.py"
        copia.write_text(copia.read_text(encoding="utf-8") + "\n# editado\n", encoding="utf-8")
        rc, out = self.cli("sync", "--check", "--vendors", "claude")
        self.assertEqual(rc, 1, out)
        self.assertIn(".claude/hooks/sdd-report-guard.py (desatualizado: rode sync)", out)
        rc, out = self.cli("sync", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("# editado", copia.read_text(encoding="utf-8"))
        d = self.settings()
        d["hooks"]["PreToolUse"] = [e for e in d["hooks"]["PreToolUse"] if "avaliador" not in json.dumps(e)]
        (self.p / ".claude/settings.json").write_text(json.dumps(d, indent=2), encoding="utf-8")
        rc, out = self.cli("sync", "--check", "--vendors", "claude")
        self.assertEqual(rc, 1, out)
        self.assertIn(".claude/settings.json (guards do sdd-open fora de hooks.PreToolUse)", out)
        rc, out = self.cli("sync", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.comandos()), 2)

    def test_settings_invalido_aborta_antes_de_escrever(self):
        (self.p / ".claude").mkdir()
        (self.p / ".claude/settings.json").write_text("{ isto não é json\n", encoding="utf-8")
        rc, out = self.cli("init", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 66, out)
        self.assertIn(".claude/settings.json não é JSON válido", out)
        self.assertIn("nada foi alterado", out)
        self.assertFalse((self.p / ".claude/hooks").exists())
        self.assertFalse((self.p / "sdd").exists())

    def test_sem_python3_o_vendor_claude_para_antes_de_escrever(self):
        d = self.tmp / "path-sem-python3"
        d.mkdir()
        for f in FERRAMENTAS:
            alvo = shutil.which(f)
            if alvo:
                os.symlink(alvo, d / f)
        self.assertIsNone(shutil.which("python3", path=str(d)))
        rc, out = self.cli("init", "--yes", "--vendors", "claude", env=dict(self.env, PATH=str(d)))
        self.assertEqual(rc, 64, out)
        self.assertIn("precisa de python3", out)
        self.assertFalse((self.p / ".claude").exists())
        self.assertFalse((self.p / "sdd").exists())

    # ── AT-022/AT-023: sdd-report-guard.py ───────────────────────────────────────────────────────
    def test_report_guard_nega_write_que_o_lint_reprova(self):
        self.cli("init", "--yes", "--vendors", "claude")
        ruim = (RAIZ / "sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md").read_text(encoding="utf-8")
        alvo = str(self.p / "sdd/reports/BUILD_REPORT_X.md")
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-write-build-report.json", FILE=alvo, CONTENT=ruim))
        self.assertEqual(rc, 0, err)
        d = json.loads(out)
        self.assertEqual(d["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertEqual(d["hookSpecificOutput"]["hookEventName"], "PreToolUse")
        razao = d["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(razao.startswith("🛑 sdd-open: gravação de BUILD_REPORT_X.md negada — o relatório não passa no report-lint:"), razao)
        self.assertIn("[avaliação ausente]", razao)
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-write-build-report.json", FILE=alvo, CONTENT=RELATORIO_OK))
        self.assertEqual((rc, out), (0, ""))

    def test_report_guard_simula_o_edit(self):
        self.cli("init", "--yes", "--vendors", "claude")
        alvo = self.escreve(self.p, "sdd/reports/BUILD_REPORT_X.md", RELATORIO_OK)
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-edit-build-report.json", FILE=str(alvo),
                                                                       OLD="avaliador: N.A. (1 camada)", NEW=""))
        self.assertEqual(rc, 0, err)
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-edit-build-report.json", FILE=str(alvo),
                                                                       OLD="texto que não existe", NEW="x"))
        self.assertEqual((rc, out), (0, ""))
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-edit-build-report.json", FILE=str(alvo),
                                                                       OLD="| false |", NEW="| false |"))
        self.assertEqual((rc, out), (0, ""))

    def test_report_guard_ignora_outros_arquivos_fixtures_e_template(self):
        self.cli("init", "--yes", "--vendors", "claude")
        ruim = "# nada\n"
        for alvo in ("sdd/features/DEFINE_X.md", "sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md",
                     "sdd/templates/BUILD_REPORT_TEMPLATE.md"):
            with self.subTest(alvo=alvo):
                rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-write-build-report.json",
                                                                               FILE=str(self.p / alvo), CONTENT=ruim))
                self.assertEqual((rc, out, err), (0, "", ""))

    def test_report_guard_falha_aberta_com_aviso(self):
        self.cli("init", "--yes", "--vendors", "claude")
        alvo = str(self.p / "sdd/reports/BUILD_REPORT_X.md")
        vazio = self.tmp / "sem-sdd"
        vazio.mkdir()
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-write-build-report.json", FILE=alvo, CONTENT="# x\n"),
                                  env=dict(self.env, CLAUDE_PROJECT_DIR=str(vazio)))
        self.assertEqual(rc, 0, err)
        msg = json.loads(out)["systemMessage"]
        self.assertTrue(msg.startswith("⚠️ sdd-open: "), msg)
        self.assertIn("não conferido", msg)
        r = subprocess.run([PYTHON, "-B", str(self.p / ".claude/hooks/sdd-report-guard.py")], cwd=str(self.p), env=self.env,
                           input="isto não é json", capture_output=True, encoding="utf-8", timeout=120)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ilegível", json.loads(r.stdout)["systemMessage"])
        rc, out, err = self.guard("sdd-report-guard.py", self.payload("payload-write-build-report.json", FILE=alvo, CONTENT="# x\n"),
                                  env=dict(self.env, CLAUDE_PROJECT_DIR=str(self.p), SDD_REPORT_GUARD="off"))
        self.assertIn("desligado", json.loads(out)["systemMessage"])

    # ── AT-024: sdd-avaliador-guard.py ───────────────────────────────────────────────────────────
    def test_avaliador_guard_nega_com_arvore_suja_e_so_com_veredito(self):
        self.cli("init", "--yes", "--vendors", "claude")
        self.commit(self.p, "init")
        rc, out, err = self.guard("sdd-avaliador-guard.py", self.payload("payload-agent-veredito.json"))
        self.assertEqual((rc, out), (0, ""), err)
        self.escreve(self.p, "src/novo.py", "x = 1\n")
        rc, out, err = self.guard("sdd-avaliador-guard.py", self.payload("payload-agent-veredito.json"))
        self.assertEqual(rc, 0, err)
        razao = json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]
        self.assertTrue(razao.startswith("🛑 sdd-open: despacho do avaliador negado — há trabalho não commitado:"), razao)
        self.assertIn("src/novo.py", razao)
        sem = self.payload("payload-agent-veredito.json")
        sem["tool_input"]["prompt"] = "revise o DESIGN e devolva o bloco ADVISOR"
        rc, out, err = self.guard("sdd-avaliador-guard.py", sem)
        self.assertEqual((rc, out), (0, ""))
        rc, out, err = self.guard("sdd-avaliador-guard.py", self.payload("payload-agent-veredito.json"),
                                  env=dict(self.env, CLAUDE_PROJECT_DIR=str(self.p), SDD_AVALIADOR_GUARD="off"))
        self.assertIn("⚠️", json.loads(out)["systemMessage"])
        (self.p / "sdd/bin/avaliador-guard.sh").unlink()
        rc, out, err = self.guard("sdd-avaliador-guard.py", self.payload("payload-agent-veredito.json"))
        self.assertIn("não conferido", json.loads(out)["systemMessage"])


if __name__ == "__main__":
    import unittest
    unittest.main()
