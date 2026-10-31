"""Os hooks de git que o init instala (sdd/hooks/pre-commit e pre-push), regra por regra, dos dois lados.

Cada teste monta um repositório com os hooks ligados (core.hooksPath = sdd/hooks), o sdd/bin/ e a skill
sdd-higiene-dado copiados do pacote, e commita de verdade: o contrato é o exit do `git commit` e o texto
da recusa (🛑 [classe], RESULTADO: COMMIT RECUSADO, → por classe). O que o publish-gate reprovaria em disco
(arquivo acima do teto, byte NUL, credencial, CPF) é montado aqui, em execução.
"""
from __future__ import annotations

import os
import random
import re
import shutil
import string
import subprocess
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox
from test_alarme import cnpj, com_mascara_cpf, cpf

HOOK = RAIZ / "sdd/hooks/pre-commit"
PRE_PUSH = RAIZ / "sdd/hooks/pre-push"
HIGIENE = ".agents/skills/sdd-higiene-dado"
RELATORIO_OK = (
    "# BUILD REPORT: X\n\n| ID | Critério (EARS) | Resultado | Evidência |\n|----|---|---|---|\n"
    "| AT-001 | When x, the system shall y | false | — |\n\navaliador: N.A. (1 camada)\n"
)

# PATH mínimo sem python3: no macOS /usr/bin tem python3 E git/awk/sed, então tirar /usr/bin levaria
# tudo junto. Um diretório só com links para o que o hook e o git usam prova a falha aberta.
FERRAMENTAS = ("bash", "sh", "git", "awk", "sed", "grep", "tr", "wc", "basename", "dirname", "mktemp",
               "cat", "head", "cmp", "od", "rm", "env", "cut", "sort", "uniq", "ls")


def valor_aleatorio(rng: random.Random, n: int = 14) -> str:
    return "".join(rng.choice(string.ascii_letters + string.digits) for _ in range(n))


class Hooks(Sandbox):
    def setUp(self):
        super().setUp()
        self.rng = random.Random(20261030)
        self.p = self.repo("projeto")
        self.git(self.p, "symbolic-ref", "HEAD", "refs/heads/main")
        for rel in ("sdd/hooks", "sdd/bin", "sdd/playbook.md", HIGIENE):
            self.copia(rel, self.p)
        shutil.copy2(str(RAIZ / "sdd/config.example.yaml"), str(self.p / "sdd/config.yaml"))
        self.git(self.p, "config", "core.hooksPath", "sdd/hooks")
        self.escreve(self.p, "README.md", "# projeto\n")
        self.commit(self.p, "base")

    # ── apoio ────────────────────────────────────────────────────────────────────────────────────
    def tenta_commit(self, *extra: str, env: dict | None = None) -> tuple[int, str]:
        self.roda(["git", "add", "-A"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t", *extra], self.p, env=env)
        return rc, out + err

    def slot(self, chave: str, valor: str) -> None:
        cfg = self.p / "sdd/config.yaml"
        texto = cfg.read_text(encoding="utf-8")
        novo, n = re.subn(r"(?m)^  %s:.*$" % re.escape(chave), "  %s: %s" % (chave, valor), texto)
        self.assertEqual(n, 1, chave)
        cfg.write_text(novo, encoding="utf-8")

    def assertRecusa(self, saida: str, *classes: str) -> None:
        self.assertIn("sdd-open: commit recusado", saida)
        self.assertEqual(saida.count("RESULTADO: COMMIT RECUSADO"), 1)
        for c in classes:
            self.assertIn("🛑 [%s]" % c, saida)
            self.assertIn("→ [%s]" % c, saida)
        self.assertIn("git commit --no-verify", saida)
        self.assertIn("Agente de IA: não use --no-verify", saida)
        self.assertLess(saida.index("RESULTADO: COMMIT RECUSADO"), saida.rindex("git commit --no-verify"))

    def remoto_main(self) -> None:
        self.git(self.p, "update-ref", "refs/remotes/origin/main", "HEAD")

    def path_sem_python(self) -> dict:
        d = self.tmp / "path-sem-python3"
        d.mkdir()
        for f in FERRAMENTAS:
            alvo = shutil.which(f)
            if alvo:
                os.symlink(alvo, d / f)
        env = dict(self.env, PATH=str(d))
        self.assertIsNone(shutil.which("python3", path=str(d)))
        return env

    # ── contrato entre o hook e o pacote ─────────────────────────────────────────────────────────
    def test_lista_de_arquivos_de_contexto_igual_a_do_pacote(self):
        hook = re.search(r'^ARQUIVOS_CONTEXTO="([^"]+)"', HOOK.read_text(encoding="utf-8"), re.M).group(1)
        vendors = re.search(r'^VENDOR_ARQUIVOS_CONTEXTO="([^"]+)"',
                            (RAIZ / "bin/lib/vendors.sh").read_text(encoding="utf-8"), re.M).group(1)
        self.assertEqual(sorted(hook.split()), sorted(vendors.split()))
        for nome in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".cursorrules"):
            self.assertIn(nome, hook.split())
        self.assertIn("# sdd-open: dispatcher de hooks (pre-commit)", HOOK.read_text(encoding="utf-8").splitlines()[1])

    # ── AT-015: commit limpo é silencioso; vários achados saem juntos ────────────────────────────
    def test_commit_limpo_passa_em_silencio(self):
        self.escreve(self.p, "nota.md", "tudo certo\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.strip(), "")

    def test_varios_achados_numa_recusa_so_e_no_verify_grava(self):
        self.slot("context_file_max_kb", "1")
        self.escreve(self.p, "AGENTS.md", "x" * 3000)
        self.escreve(self.p, "cfg.json", '{"password": "%s"}\n' % valor_aleatorio(self.rng))
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1)
        self.assertRecusa(saida, "H2", "H3")
        self.assertIn("Por que importa:", saida)
        rc, saida = self.tenta_commit("--no-verify")
        self.assertEqual(rc, 0, saida)

    # ── AT-007: H2 ───────────────────────────────────────────────────────────────────────────────
    def test_h2_teto_do_arquivo_de_contexto(self):
        self.slot("context_file_max_kb", "1")
        self.escreve(self.p, "sub/CLAUDE.md", "x" * 2000)
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1)
        self.assertRecusa(saida, "H2")
        self.assertIn("🛑 [H2] sub/CLAUDE.md: 2000 bytes (teto 1 KB)", saida)
        self.assertIn("project.context_file_max_kb", saida)
        (self.p / "sub/CLAUDE.md").write_text("x" * 1000, encoding="utf-8")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_h2_default_100kb_com_slot_vazio_ou_invalido(self):
        for valor in ('""', "abc", "0"):
            with self.subTest(slot=valor):
                self.slot("context_file_max_kb", valor)
                self.escreve(self.p, ".cursorrules", "x" * (101 * 1024))
                rc, saida = self.tenta_commit()
                self.assertEqual(rc, 1, saida)
                self.assertIn("(teto 100 KB)", saida)
                (self.p / ".cursorrules").write_text("x" * (90 * 1024), encoding="utf-8")
                rc, saida = self.tenta_commit()
                self.assertEqual(rc, 0, saida)

    # ── AT-008/AT-009: H3 ────────────────────────────────────────────────────────────────────────
    def test_h3_credencial_em_config_mostra_a_chave_e_nunca_o_valor(self):
        segredo = valor_aleatorio(self.rng)
        for nome, texto in (("app.json", '{\n  "db_password": "%s"\n}\n' % segredo),
                            ("settings.yml", "smtp:\n  api_token: '%s'\n" % segredo),
                            (".env", 'DB_PASSWORD="%s"\n' % segredo),
                            (".env.prod", "PASSWORD=%s\n" % segredo)):      # dotenv sem aspas (ciclo 1)
            with self.subTest(arquivo=nome):
                self.escreve(self.p, nome, texto)
                rc, saida = self.tenta_commit()
                self.assertEqual(rc, 1, saida)
                self.assertRecusa(saida, "H3")
                self.assertIn("🛑 [H3] %s: credencial em texto claro (chave: " % nome, saida)
                self.assertNotIn(segredo, saida)
                self.roda(["git", "rm", "-q", "--cached", nome], self.p)
                (self.p / nome).unlink()

    def test_h3_placeholder_antes_nao_absolve_a_credencial_real(self):
        # ciclo 2 do avaliador: a regra decidia pela primeira ocorrência; um placeholder ou uma versão antes da
        # credencial real deixava o arquivo passar
        segredo = valor_aleatorio(self.rng)
        for nome, texto in (("cfg.json", '{"dependencies": {"token": "^2.0.0"}, "db_password": "%s"}\n' % segredo),
                            (".env.prod", "DB_HOST=${DB_HOST}\nPASSWORD=${DB_PASSWORD}\nSECRET=%s\n" % segredo)):
            with self.subTest(arquivo=nome):
                self.escreve(self.p, nome, texto)
                rc, saida = self.tenta_commit()
                self.assertEqual(rc, 1, saida)
                self.assertIn("🛑 [H3] %s: credencial em texto claro (chave: " % nome, saida)
                self.assertNotIn(segredo, saida)
                self.roda(["git", "rm", "-q", "--cached", nome], self.p)
                (self.p / nome).unlink()

    def test_h3_placeholder_e_package_lock_passam(self):
        shutil.copy2(str(RAIZ / "sdd/fixtures/hooks/config-placeholder.json"), str(self.p / "config.json"))
        self.escreve(self.p, "package-lock.json",
                     '{\n  "parse-passwd": "^1.0.0",\n  "token-types": "2.0.0",\n  "dependencies": {"token": "^2.0.0", "secret": "~1.4.2"}\n}\n')
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_h3_gitleaks_quando_instalado(self):
        d = self.tmp / "bin-gitleaks"
        d.mkdir()
        falso = d / "gitleaks"
        falso.write_text('#!/bin/sh\necho "Finding: x"; echo "File: cfg.json"; echo "RuleID: generic-api-key"; echo "leaks found: 1"\nexit "${GL_RC:-1}"\n',
                         encoding="utf-8")
        falso.chmod(0o755)
        env = dict(self.env, PATH=str(d) + os.pathsep + self.env["PATH"])
        self.escreve(self.p, "nota.md", "sem credencial\n")
        rc, saida = self.tenta_commit(env=dict(env, GL_RC="1"))
        self.assertEqual(rc, 1, saida)
        self.assertRecusa(saida, "H3")
        self.assertIn("🛑 [H3] gitleaks: File: cfg.json RuleID: generic-api-key", saida)
        rc, saida = self.tenta_commit(env=dict(env, GL_RC="3"))
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: gitleaks saiu 3", saida)
        self.escreve(self.p, "outra.md", "também sem credencial\n")
        rc, saida = self.tenta_commit(env=dict(env, GL_RC="0"))
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.strip(), "")

    # ── AT-010: H4 ───────────────────────────────────────────────────────────────────────────────
    def playbook(self, nome: str, commit: bool = False) -> None:
        shutil.copy2(str(RAIZ / "sdd/fixtures/playbook" / nome), str(self.p / "sdd/playbook.md"))
        if commit:  # trocar o playbook real pela fixture perde IDs: a base entra sem o hook
            self.roda(["git", "add", "-A"], self.p)
            self.git(self.p, "commit", "-q", "--no-verify", "-m", "playbook")

    def test_h4_playbook_que_perde_conhecimento_e_recusado(self):
        self.playbook("playbook-valido.md", commit=True)
        self.playbook("playbook-colapso.md")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertRecusa(saida, "H4")
        self.assertIn("perderia conhecimento", saida)
        self.playbook("playbook-delta-ok.md")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_h4_apagar_ou_renomear_o_playbook_e_recusado(self):
        self.roda(["git", "rm", "-q", "sdd/playbook.md"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t"], self.p)
        self.assertEqual(rc, 1)
        self.assertIn("🛑 [H4] sdd/playbook.md seria apagado ou renomeado", out + err)
        self.roda(["git", "reset", "-q", "--hard"], self.p)
        self.roda(["git", "mv", "sdd/playbook.md", "sdd/antigo.md"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t"], self.p)
        self.assertEqual(rc, 1)
        self.assertIn("🛑 [H4]", out + err)

    def test_h4_sem_playbook_lint_avisa_e_segue(self):
        (self.p / "sdd/bin/playbook-lint.sh").unlink()
        self.playbook("playbook-valido.md", commit=True)
        self.playbook("playbook-colapso.md")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: sdd/bin/playbook-lint.sh ausente", saida)

    # ── AT-011: H5 ───────────────────────────────────────────────────────────────────────────────
    def test_h5_byte_nul_em_texto_e_recusado_e_binario_passa(self):
        (self.p / "n.md").write_bytes(b"a\x00b\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertRecusa(saida, "H5")
        self.assertIn("🛑 [H5] n.md: 1 byte(s) NUL em arquivo de texto", saida)
        (self.p / "n.md").unlink()
        self.roda(["git", "rm", "-q", "--cached", "n.md"], self.p)
        (self.p / "img.png").write_bytes(b"\x89PNG\x00\x00\x00")
        (self.p / "saida.txt").write_bytes("﻿nome;valor\n".encode("utf-16-le"))   # BOM FF FE: UTF-16
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_h5_sem_extensao_so_com_shebang(self):
        (self.p / "script").write_bytes(b"#!/bin/sh\necho a\x00b\n")
        (self.p / "dados").write_bytes(b"\x00\x01\x02")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertIn("🛑 [H5] script:", saida)
        self.assertNotIn("🛑 [H5] dados", saida)             # sem extensão e sem shebang: não é texto

    # ── AT-012: H6 ───────────────────────────────────────────────────────────────────────────────
    def test_h6_recusa_so_na_branch_padrao_com_remoto(self):
        self.escreve(self.p, "a.md", "a\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)                      # sem origin/main: passa
        self.remoto_main()
        self.escreve(self.p, "b.md", "b\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertRecusa(saida, "H6")
        self.assertIn("🛑 [H6] commit direto em main", saida)
        self.assertIn("git switch -c", saida)
        self.assertIn("sdd-new-session", saida)
        self.assertLess(saida.index("git switch -c"), saida.index("sdd-new-session"))
        self.git(self.p, "switch", "-q", "-c", "frente")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.git(self.p, "checkout", "-q", "--detach")
        self.escreve(self.p, "c.md", "c\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_h6_le_default_branch_do_config(self):
        self.slot("default_branch", "trunk")
        self.remoto_main()
        self.escreve(self.p, "a.md", "a\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)                      # main não é mais a padrão
        self.git(self.p, "switch", "-q", "-c", "trunk")
        self.git(self.p, "update-ref", "refs/remotes/origin/trunk", "HEAD")
        self.escreve(self.p, "b.md", "b\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertIn("🛑 [H6] commit direto em trunk", saida)

    # ── AT-013: REPORT ───────────────────────────────────────────────────────────────────────────
    def test_report_staged_passa_pelo_report_lint(self):
        (self.p / "sdd/reports").mkdir(exist_ok=True)
        shutil.copy2(str(RAIZ / "sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md"), str(self.p / "sdd/reports/BUILD_REPORT_X.md"))
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertRecusa(saida, "REPORT")
        self.assertIn("🛑 [REPORT] sdd/reports/BUILD_REPORT_X.md não passa no report-lint:", saida)
        self.assertIn("[avaliação ausente]", saida)
        self.escreve(self.p, "sdd/reports/BUILD_REPORT_X.md", RELATORIO_OK)
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)

    def test_report_confere_o_staged_e_nao_o_disco(self):
        (self.p / "sdd/reports").mkdir(exist_ok=True)
        self.escreve(self.p, "sdd/reports/BUILD_REPORT_X.md", RELATORIO_OK)
        self.roda(["git", "add", "-A"], self.p)
        self.escreve(self.p, "sdd/reports/BUILD_REPORT_X.md", "# quebrado no disco, mas não staged\n")
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "t"], self.p)
        self.assertEqual(rc, 0, out + err)

    def test_report_pula_fixtures_e_template_copiados_pelo_init(self):
        for rel in ("sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md", "sdd/templates/BUILD_REPORT_TEMPLATE.md"):
            self.copia(rel, self.p)
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.assertEqual(saida.strip(), "")

    def test_report_sem_python3_ou_sem_lint_avisa_e_segue(self):
        (self.p / "sdd/reports").mkdir(exist_ok=True)
        shutil.copy2(str(RAIZ / "sdd/fixtures/evidencia/BUILD_REPORT_sem_avaliacao.md"), str(self.p / "sdd/reports/BUILD_REPORT_X.md"))
        rc, saida = self.tenta_commit(env=self.path_sem_python())
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: python3 ausente: sdd/reports/BUILD_REPORT_X.md não foi conferido", saida)
        (self.p / "sdd/bin/report-lint.py").unlink()
        self.escreve(self.p, "sdd/reports/BUILD_REPORT_Y.md", "# y\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: sdd/bin/report-lint.py ausente", saida)

    # ── AT-014: alarme da higiene pelo dispatcher ────────────────────────────────────────────────
    def test_higiene_ligada_recusa_cpf_env_e_diz_como_desinstalar_sem_rm(self):
        self.git(self.p, "config", "sdd.higieneDado", "on")
        self.escreve(self.p, "clientes.md", "cliente %s\n" % com_mascara_cpf(cpf(self.rng)))
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertIn("sdd-higiene-dado: commit recusado", saida)
        self.assertIn("CPF", saida)
        self.assertEqual(saida.count("RESULTADO: COMMIT RECUSADO"), 1)
        self.assertIn("alarme.sh desinstalar", saida)
        self.assertNotIn("rm ", saida)
        # só o alarme falhou: cabeçalho próprio, sem bloco vazio de achados, e um → da classe alarme (ciclo 1)
        self.assertIn("commit recusado pelo alarme da sdd-higiene-dado", saida)
        self.assertNotIn("Encontrei o que não pode entrar", saida)
        self.assertIn("→ [alarme]", saida)
        (self.p / "clientes.md").unlink()
        self.roda(["git", "rm", "-q", "--cached", "clientes.md"], self.p)
        self.escreve(self.p, "nota.md", "cnpj %s\n" % cnpj(self.rng))
        self.escreve(self.p, ".env", "X=1\n")
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 1, saida)
        self.assertIn("CNPJ", saida)
        self.assertIn("arquivo de senhas", saida)

    def test_higiene_desligada_ou_sem_script(self):
        self.escreve(self.p, "clientes.md", "cliente %s\n" % com_mascara_cpf(cpf(self.rng)))
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)                      # desligada: só H2–H6 rodam
        self.git(self.p, "config", "sdd.higieneDado", "on")
        (self.p / HIGIENE / "scripts/pre-commit.sh").unlink()
        self.escreve(self.p, "outro.md", "cliente %s\n" % com_mascara_cpf(cpf(self.rng)))
        rc, saida = self.tenta_commit()
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: alarme da sdd-higiene-dado ligado", saida)

    # ── AT-016: pre-push ─────────────────────────────────────────────────────────────────────────
    def pre_push(self, linhas: str) -> tuple[int, str]:
        r = subprocess.run([BASH, str(self.p / "sdd/hooks/pre-push"), "origin", "x"], cwd=str(self.p), env=self.env,
                           input=linhas, capture_output=True, encoding="utf-8", errors="replace", timeout=60)
        return r.returncode, r.stdout + r.stderr

    def test_pre_push_avisa_base_velha_e_sai_0(self):
        base = self.git(self.p, "rev-parse", "HEAD").strip()
        self.git(self.p, "switch", "-q", "-c", "frente")
        self.escreve(self.p, "f.md", "f\n")
        self.commit(self.p, "f1")
        self.git(self.p, "checkout", "-q", "main")
        self.escreve(self.p, "m.md", "m\n")
        self.commit(self.p, "m1")
        self.escreve(self.p, "m2.md", "m\n")
        self.commit(self.p, "m2")
        self.git(self.p, "update-ref", "refs/remotes/origin/main", "HEAD")
        frente = self.git(self.p, "rev-parse", "frente").strip()
        rc, saida = self.pre_push("refs/heads/frente %s refs/heads/frente %s\n" % (frente, base))
        self.assertEqual(rc, 0, saida)
        self.assertIn("⚠️  sdd-open: frente está 2 commit(s) atrás de origin/main", saida)
        self.assertIn("→ traga a base", saida)
        rc, saida = self.pre_push("refs/heads/main %s refs/heads/main %s\n" % (self.git(self.p, "rev-parse", "HEAD").strip(), base))
        self.assertEqual((rc, saida.strip()), (0, ""))
        rc, saida = self.pre_push("(delete) %s refs/heads/frente %s\n" % ("0" * 40, frente))
        self.assertEqual((rc, saida.strip()), (0, ""))
        self.git(self.p, "update-ref", "-d", "refs/remotes/origin/main")
        rc, saida = self.pre_push("refs/heads/frente %s refs/heads/frente %s\n" % (frente, base))
        self.assertEqual((rc, saida.strip()), (0, ""))


if __name__ == "__main__":
    import unittest
    unittest.main()
