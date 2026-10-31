"""Contrato do bin/sdd-open.sh: init, sync, sync --check e doctor num projeto temporário.

O pacote roda a partir da raiz deste repositório; o projeto do usuário é um repo git temporário.
Exit: 0 ok · 1 divergente (sync --check) · 64 uso ou pré-condição (verbo, opção, fora de git).
"""
from __future__ import annotations

import os
import re
import shutil
import unittest

from apoio import BASH, RAIZ, Sandbox

CLI = RAIZ / "bin/sdd-open.sh"
ABRE = "<sdd-open-instructions>"
FECHA = "</sdd-open-instructions>"


class Uso(Sandbox):
    def test_verbo_desconhecido_e_64(self):
        rc, out, err = self.roda([BASH, CLI, "frobnicate"], self.repo())
        self.assertEqual(rc, 64, out + err)

    def test_opcao_desconhecida_e_64(self):
        rc, out, err = self.roda([BASH, CLI, "init", "--bogus"], self.repo())
        self.assertEqual(rc, 64, out + err)

    def test_init_fora_de_git_e_64(self):
        solta = self.tmp / "sem-git"
        solta.mkdir()
        rc, out, err = self.roda([BASH, CLI, "init", "--yes"], solta)
        self.assertEqual(rc, 64, out + err)
        self.assertEqual(sorted(p.name for p in solta.iterdir()), [], "init escreveu fora de git")

    def test_sem_argumentos_mostra_ajuda(self):
        rc, out, err = self.roda([BASH, CLI], self.repo())
        self.assertEqual(rc, 0, out + err)
        self.assertIn("init", out)


class Projeto(Sandbox):
    """Projeto com init feito e commitado: o ponto de partida de sync, --check e doctor."""

    USUARIO = "# Meu projeto\n\nRegra local: testes antes do merge.\n"

    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        self.escreve(self.p, "AGENTS.md", self.USUARIO)
        self.commit(self.p, "base")
        self.init = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.commit(self.p, "init")

    def cli(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, CLI, *args], self.p)
        return rc, out + err

    def status(self) -> str:
        return self.git(self.p, "status", "--porcelain")

    def test_init_cria_a_estrutura(self):
        rc, out = self.init
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: INSTALADO", out)
        for rel in ("sdd/templates/DEFINE_TEMPLATE.md", "sdd/bin/verify-gate.sh", "sdd/playbook.md",
                    "sdd/config.yaml", ".agents/skills/sdd-define/SKILL.md", "AGENTS.md", "CLAUDE.md",
                    ".claude/skills/sdd-define/SKILL.md"):
            with self.subTest(arquivo=rel):
                self.assertTrue((self.p / rel).is_file(), rel)

    def test_init_copia_fixtures_de_exemplo_mas_nunca_os_testes(self):
        # fixtures são exemplo na 1ª instalação (aplicar(), bin/sdd-open.sh); tests/ é do pacote.
        self.assertTrue((self.p / "sdd/fixtures/DEFINE_FIXTURE_CONTROLE.md").is_file())
        self.assertFalse((self.p / "tests").exists())

    def test_init_de_novo_e_idempotente(self):
        rc, out = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.status(), "")

    def test_sync_e_idempotente_e_check_fica_em_dia(self):
        rc, out = self.cli("sync", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.status(), "")
        rc, out = self.cli("sync", "--check")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: EM DIA", out)

    def test_check_acusa_copia_gerada_editada_a_mao(self):
        copia = self.p / ".claude/skills/sdd-define/SKILL.md"
        copia.write_text(copia.read_text(encoding="utf-8") + "\nEditado à mão.\n", encoding="utf-8")
        rc, out = self.cli("sync", "--check")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("RESULTADO: DIVERGENTE", out)

    def test_sync_preserva_o_texto_do_usuario_no_agents_md(self):
        agents = self.p / "AGENTS.md"
        texto = agents.read_text(encoding="utf-8")
        self.assertTrue(texto.startswith(self.USUARIO), texto[:200])
        self.assertEqual(texto.count(ABRE), 1)
        acrescimo = "\n## Depois do bloco\n\nTexto do usuário depois dos marcadores.\n"
        agents.write_text(texto + acrescimo, encoding="utf-8")
        antes = agents.read_bytes()
        rc, out = self.cli("sync", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertEqual(agents.read_bytes(), antes, "sync alterou bytes fora dos marcadores")

    def test_sync_reescreve_so_o_bloco_quando_a_fonte_muda(self):
        agents = self.p / "AGENTS.md"
        texto = agents.read_text(encoding="utf-8")
        i, j = texto.index(ABRE), texto.index(FECHA)
        agents.write_text(texto[:i + len(ABRE)] + "\nbloco velho\n" + texto[j:], encoding="utf-8")
        rc, out = self.cli("sync", "--check")
        self.assertNotEqual(rc, 0, out)
        rc, out = self.cli("sync", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertEqual(agents.read_text(encoding="utf-8"), texto)

    def test_doctor_termina_em_resultado(self):
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertResultado(out)
        self.assertIn("AGENTS.md com o bloco sdd-open", out)

    def test_doctor_acusa_env_salvo_no_git_e_sai_0(self):
        self.escreve(self.p, ".env", "SENHA=x\n")
        self.commit(self.p, "env")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️  O arquivo de senhas .env está salvo no git", out)
        self.assertIn('git rm --cached ".env"', out)
        self.assertIn("não apaga do histórico", out)
        self.assertResultado(out)

    def test_doctor_nao_perde_o_resto_de_nome_com_quebra_de_linha(self):
        self.escreve(self.p, "nova\nlinha.p12", "x\n")
        # com os hooks ligados pelo init (F8), o gitleaks instalado recusa um .p12 (pkcs12-file): o commit
        # deste teste passa por cima do hook, porque o alvo aqui é a mensagem do doctor, não a recusa
        self.git(self.p, "add", "-A")
        self.git(self.p, "commit", "-q", "--no-verify", "-m", "p12")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("O certificado digital nova", out)
        self.assertIn("linha.p12 está salvo no git", out)

    def test_doctor_sem_segredo_diz_que_esta_limpo(self):
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("✅ nenhum segredo salvo no git", out)

    def test_doctor_com_pacote_sem_checar_avisa_e_sai_0(self):
        pacote = self.tmp / "pacote"
        for rel in ("bin", ".agents", "sdd", "AGENTS.md.tmpl"):
            self.copia(rel, pacote)
        (pacote / ".agents/skills/sdd-checar-ambiente/scripts/checar.sh").unlink()
        rc, out, err = self.roda([BASH, pacote / "bin/sdd-open.sh", "doctor"], self.p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("pacote incompleto", out + err)
        self.assertResultado(out + err)

    def versao_da_skill(self, skill_md, versao: str) -> None:
        texto = skill_md.read_text(encoding="utf-8")
        novo = re.sub(r'(?m)^(\s+version: )"[0-9.]+"', r'\g<1>"' + versao + '"', texto, count=1)
        self.assertNotEqual(novo, texto)
        skill_md.write_text(novo, encoding="utf-8")

    def test_doctor_avisa_skill_mais_velha_que_a_do_pacote(self):
        pacote = re.search(r'version: "([0-9.]+)"',
                           (RAIZ / ".agents/skills/sdd-build/SKILL.md").read_text(encoding="utf-8")).group(1)
        self.versao_da_skill(self.p / ".agents/skills/sdd-build/SKILL.md", "1.0.0")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd-build 1.0.0 no projeto, " + pacote + " no pacote", out)
        self.assertIn("apague .agents/skills/sdd-build e rode init", out)
        self.assertNotIn("em dia com o pacote", out)
        self.assertResultado(out)

    def test_doctor_avisa_sdd_bin_diferente_do_pacote(self):
        lint = self.p / "sdd/bin/report-lint.py"
        lint.write_text(lint.read_text(encoding="utf-8") + "# editado\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd/bin/report-lint.py difere do pacote — se você não editou, apague e rode init", out)
        self.assertResultado(out)

    def test_doctor_em_dia_com_o_pacote(self):
        # versão do projeto MAIOR que a do pacote é evolução da pessoa, não atraso
        self.versao_da_skill(self.p / ".agents/skills/sdd-release/SKILL.md", "9.0.0")
        # a mesma versão do pacote entre aspas simples é YAML válido, não atraso
        md = self.p / ".agents/skills/sdd-design/SKILL.md"
        md.write_text(re.sub(r'(?m)^(\s+version: )"([0-9.]+)"', r"\g<1>'\g<2>'", md.read_text(encoding="utf-8"), count=1),
                      encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("✅ skills e sdd/bin/ em dia com o pacote", out)
        self.assertNotIn("no pacote — para receber", out)

    def test_copias_geradas_dos_scripts_portados_passam_bash_n(self):
        for rel in ("sdd-checar-ambiente/scripts/checar.sh", "sdd-higiene-dado/scripts/alarme.sh",
                    "sdd-higiene-dado/scripts/pre-commit.sh", "sdd-iniciar-repo/scripts/inventario.sh"):
            copia = self.p / ".claude/skills" / rel
            with self.subTest(copia=rel):
                self.assertIn("sdd-open:generated", copia.read_text(encoding="utf-8"))
                rc, out, err = self.roda([BASH, "-n", copia], self.p)
                self.assertEqual(rc, 0, out + err)


if __name__ == "__main__":
    unittest.main()


class Hooks(Sandbox):
    """F8: o init copia sdd/hooks/, liga core.hooksPath sob a confirmação única e nunca desliga alarme alheio;
    o doctor diz o estado dos hooks com o comando que resolve."""

    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        self.git(self.p, "symbolic-ref", "HEAD", "refs/heads/main")
        self.escreve(self.p, "AGENTS.md", "# Meu projeto\n")
        self.commit(self.p, "base")

    def cli(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, CLI, *args], self.p)
        return rc, out + err

    def hooks_path(self) -> str:
        rc, out, _ = self.roda(["git", "config", "--get", "core.hooksPath"], self.p)
        return out.strip() if rc == 0 else ""

    def legado(self):
        return self.p / ".git/hooks/pre-commit"

    def test_init_liga_os_hooks_e_a_linha_do_plano_diz_o_efeito(self):
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertIn("+ core.hooksPath = sdd/hooks — 5 regras + relatório + alarme passam a conferir cada commit", out)
        self.assertIn("git commit --no-verify pula uma vez", out)
        self.assertEqual(self.hooks_path(), "sdd/hooks")
        for h in ("pre-commit", "pre-push"):
            self.assertTrue(os.access(self.p / "sdd/hooks" / h, os.X_OK), h)
        self.assertIn("✅ hooks ligados (sdd/hooks: pre-commit com 5 regras + relatório + alarme da higiene off, pre-push)", out)
        self.assertNotIn("git switch -c", out)
        # o 1º commit depois do init passa: fixtures e template de BUILD_REPORT são pulados pelo hook
        self.roda(["git", "add", "-A"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "init"], self.p)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((out + err).strip(), "")

    def test_dry_run_mostra_a_linha_e_nao_liga(self):
        rc, out = self.cli("init", "--dry-run", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertIn("+ core.hooksPath = sdd/hooks", out)
        self.assertIn("RESULTADO: DRY-RUN", out)
        self.assertEqual(self.hooks_path(), "")
        self.assertFalse((self.p / "sdd").exists())

    def test_outro_hooks_path_nao_e_tocado(self):
        self.git(self.p, "config", "core.hooksPath", ".husky/_")
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.hooks_path(), ".husky/_")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        self.assertIn("Nada foi alterado nele.", out)
        self.assertIn("bash sdd/hooks/pre-commit || exit 1", out)
        self.assertIn("RESULTADO: INSTALADO", out)
        self.assertTrue((self.p / "sdd/hooks/pre-commit").is_file())
        self.assertNotIn("+ core.hooksPath", out)

    def test_pre_commit_alheio_nao_e_tocado(self):
        alheio = "#!/bin/sh\necho alheio\n"
        self.legado().write_text(alheio, encoding="utf-8")
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.hooks_path(), "")
        self.assertEqual(self.legado().read_text(encoding="utf-8"), alheio)
        self.assertIn("hooks do open não ligados: já existe um pre-commit em", out)
        self.assertIn("bash sdd/hooks/pre-commit || exit 1", out)

    def test_migra_o_alarme_da_higiene_sem_perder_a_protecao(self):
        rc, out, err = self.roda([BASH, RAIZ / ".agents/skills/sdd-higiene-dado/scripts/alarme.sh", "instalar"], self.p)
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(self.legado().is_file())
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.hooks_path(), "sdd/hooks")
        rc, cfg, _ = self.roda(["git", "config", "--get", "sdd.higieneDado"], self.p)
        self.assertEqual(cfg.strip(), "on")
        self.assertTrue(self.legado().is_file(), "o arquivo antigo fica (inerte); quem o remove é o desinstalar")
        self.assertIn("⚠️  alarme da sdd-higiene-dado migrado: continua ligado, agora pelos hooks do projeto (sdd/hooks)", out)
        self.assertIn("alarme.sh desinstalar", out)
        self.assertIn("alarme da higiene on", out)
        # a proteção continua: .env é recusado pelo dispatcher
        self.escreve(self.p, ".env", "X=1\n")
        self.roda(["git", "add", "-A"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "env"], self.p)
        self.assertEqual(rc, 1)
        self.assertIn("arquivo de senhas", out + err)
        self.assertIn("RESULTADO: COMMIT RECUSADO", out + err)

    def test_init_repetido_e_idempotente_e_completa_hook_apagado(self):
        self.cli("init", "--yes", "--vendors", "codex")
        self.roda(["git", "add", "-A"], self.p)
        self.roda(["git", "commit", "-q", "-m", "init"], self.p)
        rc, out = self.cli("init", "--yes", "--vendors", "codex", "--verbose")
        self.assertEqual(rc, 0, out)
        self.assertIn("= core.hooksPath = sdd/hooks (já correto)", out)
        self.assertNotIn("+ core.hooksPath", out)
        self.assertEqual(self.git(self.p, "status", "--porcelain"), "")
        (self.p / "sdd/hooks/pre-push").unlink()
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertTrue(os.access(self.p / "sdd/hooks/pre-push", os.X_OK))

    def test_doctor_diz_o_estado_dos_hooks_com_o_comando(self):
        self.cli("init", "--yes", "--vendors", "codex")
        rc, out = self.cli("doctor")
        self.assertIn("✅ hooks ligados (sdd/hooks:", out)
        self.roda(["git", "config", "--unset", "core.hooksPath"], self.p)
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados (core.hooksPath vazio) — rode init", out)
        self.git(self.p, "config", "core.hooksPath", "sdd/hooks")
        (self.p / "sdd/hooks/pre-commit").chmod(0o644)
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks: sdd/hooks/pre-commit sem permissão de execução (o git o ignora em silêncio) — rode: chmod +x sdd/hooks/pre-commit", out)
        self.assertNotIn("✅ hooks ligados", out)
        (self.p / "sdd/hooks/pre-commit").chmod(0o755)
        (self.p / "sdd/hooks/pre-push").unlink()
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks: sdd/hooks/pre-push ausente — rode init", out)
        self.git(self.p, "config", "core.hooksPath", ".husky/_")
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        self.assertIn("bash sdd/hooks/pre-commit || exit 1", out)
        self.assertResultado(out)

    def test_hooks_path_absoluto_por_link_simbolico_e_nosso(self):
        # ciclo 1 do avaliador: /tmp é link para /private/tmp no macOS; o caminho pelo link era tratado como OUTRO
        self.cli("init", "--yes", "--vendors", "codex")
        link = self.tmp / "link-para-o-projeto"
        os.symlink(self.p, link)
        self.git(self.p, "config", "core.hooksPath", str(link / "sdd/hooks"))
        rc, out = self.cli("doctor")
        self.assertIn("✅ hooks ligados (sdd/hooks:", out)
        self.assertNotIn("hooks do open não ligados", out)
        rc, out = self.cli("init", "--yes", "--vendors", "codex", "--verbose")
        self.assertIn("= core.hooksPath = sdd/hooks (já correto)", out)

    def test_init_repetido_sem_paste_no_path_mantem_os_vendors(self):
        # ciclo 1 do avaliador: a união dos vendors passava por `paste`; sem ele no PATH a lista esvaziava em
        # silêncio e o init terminava INSTALADO sem vendor nenhum
        self.cli("init", "--yes", "--vendors", "codex")
        d = self.tmp / "path-sem-paste"
        d.mkdir()
        for f in ("bash", "sh", "git", "awk", "sed", "grep", "tr", "wc", "basename", "dirname", "mktemp", "cat",
                  "head", "tail", "cmp", "od", "rm", "env", "cut", "sort", "uniq", "ls", "cp", "mkdir", "chmod",
                  "mv", "find", "touch", "uname", "readlink", "date", "python3"):
            alvo = shutil.which(f)
            if alvo:
                os.symlink(alvo, d / f)
        rc, out, err = self.roda([BASH, CLI, "init", "--yes", "--vendors", "kimi"], self.p, env=dict(self.env, PATH=str(d)))
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("command not found", out + err)
        vendors = re.search(r"(?m)^vendors: (.*)$", (self.p / "sdd/config.yaml").read_text(encoding="utf-8")).group(1)
        self.assertEqual(sorted(vendors.split(",")), ["codex", "kimi"])

    def test_init_na_branch_padrao_com_remoto_diz_como_commitar(self):
        self.git(self.p, "update-ref", "refs/remotes/origin/main", "HEAD")
        rc, out = self.cli("init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: INSTALADO", out)
        self.assertIn("→ leve a instalação para uma branch nova antes de commitar", out)
        self.assertIn("git switch -c sdd-open-init", out)
        self.roda(["git", "add", "-A"], self.p)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "init"], self.p)
        self.assertEqual(rc, 1)
        self.assertIn("🛑 [H6] commit direto em main", out + err)
        self.git(self.p, "switch", "-q", "-c", "sdd-open-init")
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "init"], self.p)
        self.assertEqual(rc, 0, out + err)
