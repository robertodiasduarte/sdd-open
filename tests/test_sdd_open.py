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

    def test_init_copia_patterns_e_contratos_e_nunca_sobrescreve(self):
        # F12 AT-021: o README dos patterns e o contrato de máquina vêm com o pacote; o init completa o que
        # falta, mas nunca sobrescreve o que o projeto já mudou.
        for rel in ("sdd/patterns/README.md", "sdd/WORKFLOW_CONTRACTS.yaml", "sdd/bin/contexto-lint.sh",
                    "sdd/bin/governanca-fronteira.sh", "sdd/fixtures/contexto/dominio.md"):
            with self.subTest(arquivo=rel):
                self.assertTrue((self.p / rel).is_file(), rel)
        meu = self.p / "sdd/patterns/README.md"
        meu.write_text("# meus patterns\n", encoding="utf-8")
        (self.p / "sdd/WORKFLOW_CONTRACTS.yaml").unlink()
        rc, out = self.cli("init", "--yes", "--vendors", "claude")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meu.read_text(encoding="utf-8"), "# meus patterns\n")
        self.assertTrue((self.p / "sdd/WORKFLOW_CONTRACTS.yaml").is_file())

    def test_init_instala_as_invariantes_junto_com_o_playbook_do_pacote(self):
        # F14 AT-034: playbook e invariantes do pacote vieram juntos, e o par é válido.
        inv = (self.p / "sdd/invariants.md").read_text(encoding="utf-8")
        self.assertIn("[INV-001]", inv)
        rc, out, err = self.roda([BASH, self.p / "sdd/bin/playbook-curator.sh", "--validar-inv", "sdd/playbook.md", "sdd/invariants.md"], self.p)
        self.assertEqual(rc, 0, out + err)

    def test_init_leva_o_resolvedor_de_python_e_completa_quando_falta(self):
        # F16, rodada 1 da revisão (R5): os scripts de sdd/bin leem sdd/bin/lib/python.sh. O init copia sdd/bin
        # inteiro; um projeto anterior a ele recebe a biblioteca rodando o init de novo (o doctor avisa).
        lib = self.p / "sdd/bin/lib/python.sh"
        self.assertTrue(lib.is_file())
        rc, out, err = self.roda([BASH, "-c", '. sdd/bin/lib/python.sh && sdd_python_pronto && echo PRONTO'], self.p)
        self.assertEqual((rc, out.strip()), (0, "PRONTO"), err)
        lib.unlink()
        rc, out = self.cli("doctor")
        self.assertIn("sdd/ incompleto", out)
        rc, out = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.assertEqual(rc, 0, out)
        self.assertTrue(lib.is_file(), "o init de novo não repôs a biblioteca")

    def test_projeto_com_playbook_proprio_recebe_so_o_esqueleto(self):
        # A invariante do pacote aponta para a LM-004 do pacote: num playbook que já existia, ela pode não existir.
        (self.p / "sdd/invariants.md").unlink()
        self.escreve(self.p, "sdd/playbook.md", "# Meu\n\n## Sempre\n\n- [LM-001] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: —\n\n## Tombstones\n")
        rc, out = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.assertEqual(rc, 0, out)
        inv = (self.p / "sdd/invariants.md").read_text(encoding="utf-8")
        self.assertNotIn("[INV-001]", inv)
        for secao in ("## Invariantes", "## Descartados", "estado=ok|auto|humano"):
            with self.subTest(secao=secao):
                self.assertIn(secao, inv)
        self.assertIn("Meu", (self.p / "sdd/playbook.md").read_text(encoding="utf-8"))
        rc, o, e = self.roda([BASH, self.p / "sdd/bin/playbook-curator.sh", "--validar-inv", "sdd/playbook.md", "sdd/invariants.md"], self.p)
        self.assertEqual(rc, 0, o + e)

    def test_init_nunca_sobrescreve_as_invariantes_do_projeto(self):
        self.escreve(self.p, "sdd/invariants.md", "# minhas\n\n## Invariantes\n")
        rc, out = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual((self.p / "sdd/invariants.md").read_text(encoding="utf-8"), "# minhas\n\n## Invariantes\n")

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

    def test_init_copia_review_e_adapters_e_nunca_sobrescreve(self):
        # F10 (AT-035): sdd/review/ (registry, preços, prompts) e sdd/bin/adapters/ vêm com o init
        for rel in ("sdd/review/registry.tsv", "sdd/review/precos.tsv", "sdd/review/prompts/reviewer.md",
                    "sdd/review/prompts/auditor.md", "sdd/review/prompts/desempate.md",
                    "sdd/bin/adversarial-review.sh", "sdd/bin/adapters/openrouter.sh",
                    # F11 (AT-027): o gate offline, o eval-agree e os stubs por engine vêm junto
                    "sdd/bin/adversarial-review-gate.sh", "sdd/bin/eval-agree.sh", "sdd/review/stubs/cenarios.tsv",
                    "sdd/review/stubs/comum.py", "sdd/review/stubs/claude.py", "sdd/review/stubs/codex.py",
                    "sdd/review/stubs/gemini.py", "sdd/review/stubs/openrouter.py",
                    "sdd/review/stubs/respostas/revisor.md"):
            with self.subTest(arquivo=rel):
                self.assertTrue((self.p / rel).is_file(), rel)
        reg = self.p / "sdd/review/registry.tsv"
        reg.write_text(reg.read_text(encoding="utf-8") + "# minha engine\n", encoding="utf-8")
        (self.p / "sdd/review/prompts/auditor.md").unlink()
        rc, out = self.cli("init", "--yes", "--vendors", "claude,codex")
        self.assertEqual(rc, 0, out)
        self.assertIn("# minha engine", reg.read_text(encoding="utf-8"))
        self.assertTrue((self.p / "sdd/review/prompts/auditor.md").is_file())

    def test_doctor_avisa_adapter_diferente_do_pacote(self):
        ad = self.p / "sdd/bin/adapters/claude.sh"
        ad.write_text(ad.read_text(encoding="utf-8") + "# editado\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd/bin/adapters/claude.sh difere do pacote — se você não editou, apague e rode init", out)

    def test_doctor_avisa_lib_diferente_do_pacote(self):
        # F16, pequeno da ficha (corrigido na F18/F20): o laço de deriva não olhava sdd/bin/lib/
        lib = self.p / "sdd/bin/lib/python.sh"
        lib.write_text(lib.read_text(encoding="utf-8") + "# editado\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd/bin/lib/python.sh difere do pacote — se você não editou, apague e rode init", out)

    def test_doctor_diz_o_motivo_do_python_uma_vez(self):
        # F16, rodada 4, R4 (corrigido na F18/F20): dentro de $(…) o "dito uma vez" se perdia e o aviso repetia
        stubs = self.tmp / "sem-python"
        stubs.mkdir()
        for nome in ("python3", "python", "py"):
            s = stubs / nome
            s.write_text("#!/bin/sh\nexit 9009\n", encoding="utf-8")
            s.chmod(0o755)
        env = {k: v for k, v in self.env.items() if k not in ("SDD_PYTHON", "SDD_PYTHON_RESOLVIDO")}
        env["PATH"] = str(stubs) + os.pathsep + env.get("PATH", "")
        rc, out, err = self.roda([BASH, CLI, "doctor"], self.p, env)
        tudo = out + err
        self.assertEqual(rc, 0, tudo)
        self.assertIn("python3 ausente", tudo)
        self.assertEqual(tudo.count("existe, mas não roda"), 1, tudo)

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

    def test_hooks_path_relativo_com_barra_ou_ponto_e_nosso(self):
        # ciclo 2 do avaliador: o git aceita `sdd/hooks/` e `./sdd/hooks`; doctor e init os tratavam como OUTRO
        self.cli("init", "--yes", "--vendors", "codex")
        for hp in ("sdd/hooks/", "./sdd/hooks"):
            with self.subTest(hooksPath=hp):
                self.git(self.p, "config", "core.hooksPath", hp)
                rc, out = self.cli("doctor")
                self.assertIn("✅ hooks ligados (sdd/hooks:", out)
                self.assertNotIn("hooks do open não ligados", out)

    def test_gancho_encadeado_no_outro_gerenciador_e_reconhecido(self):
        # F15: com core.hooksPath de outro gerenciador, o doctor mandava acrescentar a linha e seguia com ⚠️ depois
        # de ela estar lá. Controle: sem a linha, ou só num comentário, o ⚠️ continua.
        self.git(self.p, "config", "core.hooksPath", ".githooks")
        self.cli("init", "--yes", "--vendors", "codex")
        pc = self.p / ".githooks/pre-commit"
        pc.parent.mkdir(exist_ok=True)
        casos = (
            ("#!/bin/sh\necho alheio\n", False),
            ("#!/bin/sh\n# bash sdd/hooks/pre-commit || exit 1\n", False),
            ("#!/bin/sh\necho alheio # bash sdd/hooks/pre-commit || exit 1\n", False),   # R1@codex, rodada 1
            ('#!/bin/sh\necho "rode: bash sdd/hooks/pre-commit || exit 1"\n', False),       # R1@codex, rodada 2
            ("#!/bin/sh\nif [ -f sdd/hooks/pre-commit ]; then\n  bash sdd/hooks/pre-commit || exit 1\nfi\n", True),
        )
        for texto, encadeado in casos:
            with self.subTest(texto=texto):
                pc.write_text(texto, encoding="utf-8")
                pc.chmod(0o755)
                rc, out = self.cli("doctor")
                if encadeado:
                    self.assertIn("✅ hooks encadeados (%s chama sdd/hooks/pre-commit" % pc, out)
                    self.assertNotIn("hooks do open não ligados", out)
                    self.assertNotIn("⚠️  hooks", out)
                else:
                    self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .githooks", out)
                    self.assertNotIn("hooks encadeados", out)
        rc, out = self.cli("init", "--yes", "--vendors", "codex", "--verbose")
        self.assertIn("= hooks encadeados (%s chama sdd/hooks/pre-commit) (já correto)" % pc, out)
        self.assertNotIn("hooks do open não ligados", out)
        self.assertEqual(self.hooks_path(), ".githooks")
        pc.chmod(0o644)
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks: %s (o hook que o git executa) está sem permissão de execução" % pc, out)
        pc.chmod(0o755)
        (self.p / "sdd/hooks/pre-commit").unlink()
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks: %s chama sdd/hooks/pre-commit, que está ausente" % pc, out)

    def test_husky_v9_linha_no_script_e_bit_no_stub(self):
        # R1@claude, rodada 1: no husky v9 o core.hooksPath é .husky/_ (stubs gerados); a linha vai em .husky/pre-commit.
        self.cli("init", "--yes", "--vendors", "codex")
        self.git(self.p, "config", "core.hooksPath", ".husky/_")
        stub, script = self.p / ".husky/_/pre-commit", self.p / ".husky/pre-commit"
        stub.parent.mkdir(parents=True)
        stub.write_text('#!/usr/bin/env sh\n. "$(dirname "$0")/h"\n', encoding="utf-8")
        stub.chmod(0o755)
        script.write_text("npm test\nbash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")
        rc, out = self.cli("doctor")   # R1@claude e R2@codex, rodada 2: pasta `_` sem o ajudante h não prova delegação
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        stub.write_text('#!/usr/bin/env sh\n# . "$(dirname "$0")/h"\n', encoding="utf-8")   # R1@codex, rodada 3: /h comentado
        (self.p / ".husky/_/h").write_text('#!/usr/bin/env sh\n', encoding="utf-8")
        script.write_text("bash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        stub.write_text('#!/usr/bin/env sh\necho "/h"\n', encoding="utf-8")   # R1@codex, rodada 5: só citar /h não carrega o h
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        stub.write_text('#!/usr/bin/env sh\n. ./helper.sh\n', encoding="utf-8")   # R1@codex, rodada 6: outro arquivo que começa por h
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        stub.write_text('#!/usr/bin/env sh\n. "$(dirname "$0")/h"\n', encoding="utf-8")
        (self.p / ".husky/_/h").write_text('#!/usr/bin/env sh\nsh -e "$(dirname "$(dirname "$0")")/$(basename "$0")"\n', encoding="utf-8")
        script.write_text("npm test\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky/_", out)
        script.write_text("npm test\nbash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")   # sem bit: o husky roda com sh
        rc, out = self.cli("doctor")
        self.assertIn("✅ hooks encadeados (%s chama sdd/hooks/pre-commit" % script, out)
        self.assertNotIn("⚠️  hooks", out)
        stub.chmod(0o644)
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks: %s (o hook que o git executa) está sem permissão de execução" % stub, out)
        self.git(self.p, "config", "core.hooksPath", ".husky")   # pasta que não é a de stubs: a linha tem de estar nela
        script.write_text("npm test\n", encoding="utf-8")
        (self.p / ".husky/_/pre-commit").write_text("#!/bin/sh\nbash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")
        rc, out = self.cli("doctor")
        self.assertIn("⚠️  hooks do open não ligados: já existe core.hooksPath = .husky", out)

    def test_hooks_path_com_til_e_expandido(self):
        # R1@claude, rodada 3: core.hooksPath = ~/… é expandido pelo git; o doctor o lia como <raiz>/~/…
        self.cli("init", "--yes", "--vendors", "codex")
        casa = self.tmp / "casa"
        (casa / ".githooks").mkdir(parents=True)
        pc = casa / ".githooks/pre-commit"
        pc.write_text("#!/bin/sh\nbash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")
        pc.chmod(0o755)
        self.git(self.p, "config", "core.hooksPath", "~/.githooks")
        rc, out, err = self.roda([BASH, CLI, "doctor"], self.p, env=dict(self.env, HOME=str(casa)))
        self.assertIn("✅ hooks encadeados (%s chama sdd/hooks/pre-commit" % pc, out + err)

    def test_pre_commit_legado_que_chama_o_nosso_e_encadeado(self):
        self.cli("init", "--yes", "--vendors", "codex")
        self.git(self.p, "config", "--unset", "core.hooksPath")
        self.legado().write_text("#!/bin/sh\nbash sdd/hooks/pre-commit || exit 1\n", encoding="utf-8")
        self.legado().chmod(0o755)
        rc, out = self.cli("doctor")
        self.assertIn("✅ hooks encadeados (", out)
        self.assertNotIn("hooks do open não ligados", out)

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


class SegurancaNoAgents(Sandbox):
    """F18/F20 (AT-007): o bloco do AGENTS.md traz as regras de maior risco da stack do projeto e o ponteiro."""

    INICIO = "### Segurança ao construir"
    FIM = "Agentes preparados neste projeto:"

    def bloco(self, p) -> str:
        texto = (p / "AGENTS.md").read_text(encoding="utf-8")
        return texto[texto.index(self.INICIO):texto.index(self.FIM)]

    def init(self, p, cli=CLI) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, cli, "init", "--yes", "--vendors", "codex"], p)
        return rc, out + err

    def regras(self, bloco: str) -> list:
        return [ln for ln in bloco.splitlines() if ln.startswith("- ")]

    def test_com_supabase_as_5_regras_e_o_ponteiro(self):
        p = self.repo("app")
        self.escreve(p, "supabase/config.toml", "")
        self.escreve(p, "package.json", "{}\n")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        b = self.bloco(p)
        self.assertEqual(len(self.regras(b)), 6, b)
        self.assertIn("RLS ligada", b)
        self.assertIn("seguranca-varredura.sh --regras", self.regras(b)[-1])
        self.assertNotIn("regras de segurança da stack fora", out)

    def test_sem_stack_so_a_regra_de_todas_e_o_ponteiro(self):
        p = self.repo("cli")
        rc, out = self.init(p)
        self.assertEqual(rc, 0, out)
        b = self.bloco(p)
        self.assertEqual(len(self.regras(b)), 2, b)
        self.assertNotIn("RLS", b)
        self.assertIn("Nenhuma chave secreta", b)

    def test_o_acrescimo_cabe_em_2_kb(self):
        p = self.repo("app")
        self.escreve(p, "supabase/config.toml", "")
        self.escreve(p, "package.json", "{}\n")
        self.escreve(p, "vercel.json", "{}\n")
        self.init(p)
        self.assertLessEqual(len(self.bloco(p).encode("utf-8")), 2048)

    def test_stack_nova_deixa_o_bloco_divergente_e_o_sync_refaz(self):
        p = self.repo("app")
        self.init(p)
        self.commit(p, "init")
        self.escreve(p, "supabase/config.toml", "")
        rc, out, err = self.roda([BASH, CLI, "sync", "--check", "--vendors", "codex"], p)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("AGENTS.md (bloco sdd-open)", out + err)
        rc, out, err = self.roda([BASH, CLI, "sync", "--yes", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RLS ligada", self.bloco(p))
        rc, out, err = self.roda([BASH, CLI, "sync", "--check", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)

    def test_sem_o_catalogo_fica_o_ponteiro_e_o_aviso(self):
        pacote = self.tmp / "pacote"
        shutil.copytree(str(RAIZ), str(pacote), ignore=shutil.ignore_patterns(".git", "tests", "__pycache__"))
        (pacote / ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md").unlink()
        p = self.repo("app")
        self.escreve(p, "supabase/config.toml", "")
        rc, out = self.init(p, pacote / "bin/sdd-open.sh")
        self.assertEqual(rc, 0, out)
        self.assertIn("AGENTS.md: regras de segurança da stack fora (o catálogo da sdd-seguranca não está no pacote)", out)
        regras = self.regras(self.bloco(p))
        self.assertEqual(len(regras), 1, regras)
        self.assertIn("seguranca-varredura.sh --regras", regras[0])

    def test_o_ponteiro_e_o_mesmo_nas_duas_copias(self):
        # LM-005: o init precisa do ponteiro quando o leitor do catálogo falha; as duas cópias não podem divergir.
        sh = (RAIZ / "bin/sdd-open.sh").read_text(encoding="utf-8")
        py = (RAIZ / "sdd/bin/seguranca-varredura.sh").read_text(encoding="utf-8")
        no_init = re.search(r"^SEG_PONTEIRO='(.*)'$", sh, re.M).group(1)
        partes = re.search(r'^PONTEIRO = \((.*?)\)$', py, re.M | re.S).group(1)
        no_script = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', partes))
        self.assertEqual(no_init, no_script)


class CausaDoPythonNoInit(Sandbox):
    """Raio de impacto da F18/F20: o bloco do AGENTS.md confere o Python, e a causa (dita uma vez) não pode sumir."""

    def test_init_sem_python_diz_a_causa_uma_vez(self):
        stubs = self.tmp / "sem-python"
        stubs.mkdir()
        for nome in ("python3", "python", "py"):
            s = stubs / nome
            s.write_text("#!/bin/sh\nexit 9009\n", encoding="utf-8")
            s.chmod(0o755)
        env = {k: v for k, v in self.env.items() if k not in ("SDD_PYTHON", "SDD_PYTHON_RESOLVIDO")}
        env["PATH"] = str(stubs) + os.pathsep + env.get("PATH", "")
        p = self.repo("app")
        rc, out, err = self.roda([BASH, CLI, "init", "--yes", "--vendors", "codex"], p, env)
        tudo = out + err
        self.assertEqual(rc, 0, tudo)
        self.assertEqual(tudo.count("existe, mas não roda"), 1, tudo)
        self.assertIn("regras de segurança da stack fora (sem Python 3.9 para ler o catálogo)", tudo)


class RaioDeImpactoSeguranca(Sandbox):
    """Raio de impacto da F18/F20: o caminho reserva diz a causa real; o doctor acusa a skill do pacote que falta."""

    def test_stack_invalida_no_config_vira_a_causa_do_aviso(self):
        p = self.repo("app")
        self.escreve(p, "sdd/config.yaml", "security:\n  stack: \"firebase\"\n")
        rc, out, err = self.roda([BASH, CLI, "init", "--yes", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("regras de segurança da stack fora (o leitor do catálogo falhou: security.stack", out + err)
        self.assertIn("firebase", out + err)

    def test_doctor_acusa_skill_do_pacote_que_falta_no_projeto(self):
        p = self.repo("app")
        rc, out, err = self.roda([BASH, CLI, "init", "--yes", "--vendors", "codex"], p)
        self.assertEqual(rc, 0, out + err)
        shutil.rmtree(p / ".agents/skills/sdd-seguranca")
        rc, out, err = self.roda([BASH, CLI, "doctor"], p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("sdd-seguranca está no pacote e não no projeto — para receber: rode init", out + err)
