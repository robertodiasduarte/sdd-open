"""Contrato do bin/sdd-open.sh: init, sync, sync --check e doctor num projeto temporário.

O pacote roda a partir da raiz deste repositório; o projeto do usuário é um repo git temporário.
Exit: 0 ok · 1 divergente (sync --check) · 64 uso ou pré-condição (verbo, opção, fora de git).
"""
from __future__ import annotations

import re
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
        self.commit(self.p, "p12")
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
