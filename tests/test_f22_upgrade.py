"""F22 (AT-006, AT-007): o verbo upgrade.

O pacote "antigo" e o "novo" são cópias desta árvore com versões escritas pelo teste; o antigo difere do novo em
arquivos escolhidos (um que o pacote mudou, um que entrou numa skill que já existia, um que saiu). Roda em qualquer
lugar, inclusive no Verify Gate (cópia sem .git). O teste com o pacote real v2.12.1 roda só onde há a tag (o CI, que
faz checkout com tags; a máquina de quem mantém) e, sem ela, é pulado com o motivo: nunca troca de pacote calado.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox, SEM_CHMOD, SEM_PACOTE_ANTIGO, SOU_ROOT
from test_f22_versao import copia_pacote

MUDA = "sdd/bin/report-lint.py"                         # o pacote novo mudou; o projeto não editou ⇒ intacto
ENTRA = ".agents/skills/sdd-build/web/MODO_WEB.md"     # entrou numa skill que já existia ⇒ novo
SAI = ".agents/skills/sdd-build/references/velho.md"   # só no antigo ⇒ saiu (lista, nunca apaga)
EDITADOS = ("sdd/playbook.md", ".agents/skills/sdd-design/SKILL.md")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def foto(pasta: Path) -> dict[str, str]:
    return {p.relative_to(pasta).as_posix(): sha(p) for p in sorted(pasta.rglob("*"))
            if p.is_file() and ".git" not in p.relative_to(pasta).parts}


class Base(Sandbox):
    @classmethod
    def setUpClass(cls):
        cls._base = Path(tempfile.mkdtemp(prefix="sdd-open-f22u-")).resolve()
        cls.novo = copia_pacote(cls._base / "novo", "v9.8.7")
        cls.antigo = copia_pacote(cls._base / "sdd-open-v9.8.6", None)   # versão pelo nome da pasta
        a = cls.antigo
        (a / MUDA).write_text((a / MUDA).read_text(encoding="utf-8") + "# versão antiga\n", encoding="utf-8")
        (a / ENTRA).unlink()
        (a / SAI).write_text("saiu do pacote\n", encoding="utf-8")
        man = [ln for ln in (a / "MANIFEST.txt").read_text(encoding="utf-8").splitlines() if ln != ENTRA] + [SAI]
        (a / "MANIFEST.txt").write_text("\n".join(man) + "\n", encoding="utf-8")
        for e in EDITADOS:   # o pacote também mudou o que a pessoa editou: há o que mesclar
            (a / e).write_text((a / e).read_text(encoding="utf-8") + "\nlinha do pacote antigo\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(str(cls._base), ignore_errors=True)

    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        self.git(self.p, "commit", "-q", "--allow-empty", "-m", "raiz")
        self.git(self.p, "switch", "-q", "-c", "trabalho")
        rc, out = self.cli("init", "--yes", "--vendors", "claude", pkg=self.antigo)
        self.assertEqual(rc, 0, out)
        for e in EDITADOS:
            f = self.p / e
            f.write_text(f.read_text(encoding="utf-8") + "\nminha edição\n", encoding="utf-8")
        self.commit(self.p, "instala v9.8.6 e edita")

    def cli(self, *args: str, pkg: Path | None = None):
        rc, out, err = self.roda([BASH, (pkg or self.novo) / "bin/sdd-open.sh", *args], self.p)
        return rc, out + err

    def assertNadaEscrito(self, antes: dict[str, str]):
        self.assertEqual(foto(self.p), antes)


class ComRegistro(Base):
    def test_classifica_copia_e_lista_sem_commitar(self):
        commits = self.git(self.p, "rev-list", "--count", "HEAD").strip()
        edit_antes = {e: sha(self.p / e) for e in EDITADOS}
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertIn("▶ upgrade v9.8.6 → v9.8.7 — plano", out)
        self.assertRegex(out, r"= \d+ iguais ao pacote novo \(nada a fazer\)")
        self.assertRegex(out, r"\+ 1 novos \(copiar\)\n    " + ENTRA.replace(".", r"\."))
        self.assertRegex(out, r"~ \d+ do pacote, sem edição sua \(atualizar\)")
        self.assertIn("⚠️  2 editados por você — não serão tocados", out)
        self.assertIn("⚠️  1 saíram do pacote — não serão apagados\n    " + SAI, out)
        self.assertIn("Nada que você editou será tocado. Nada será commitado.", out)
        # o que é do pacote e você não editou: igual ao novo
        self.assertEqual(sha(self.p / MUDA), sha(self.novo / MUDA))
        self.assertEqual(sha(self.p / ENTRA), sha(self.novo / ENTRA))
        # editados: intocados, com a versão nova e o diff ao lado
        for e in EDITADOS:
            with self.subTest(editado=e):
                self.assertEqual(sha(self.p / e), edit_antes[e])
                novo = self.p / "sdd/upgrade/v9.8.7" / (e + ".novo")
                self.assertEqual(sha(novo), sha(self.novo / e))
                diff = (self.p / "sdd/upgrade/v9.8.7" / (e + ".diff")).read_text(encoding="utf-8")
                self.assertIn("-minha edição", diff)
                self.assertFalse((self.p / "sdd/upgrade/v9.8.7" / (e + ".pacote.diff")).exists())   # sem --de
                self.assertIn("%s — editado por você; a versão nova está em sdd/upgrade/v9.8.7/%s.novo e o que mudou "
                              "em sdd/upgrade/v9.8.7/%s.diff" % (e, e, e), out)
        self.assertTrue((self.p / SAI).is_file())   # saiu do pacote, nunca apagado
        reg = (self.p / "sdd/open-instalado.txt").read_text(encoding="utf-8")
        self.assertIn("\nversao: v9.8.7\n", reg)
        self.assertIn("%s  %s" % (sha(self.novo / MUDA), MUDA), reg)
        self.assertNotIn(SAI, reg)
        self.assertIn("RESULTADO: ATUALIZADO, 2 PARA MESCLAR", out)
        self.assertIn("→ confira com git status e commite numa frente (o upgrade não commita)", out)
        # nada commitado nem posto no índice
        self.assertEqual(self.git(self.p, "rev-list", "--count", "HEAD").strip(), commits)
        self.assertEqual(self.git(self.p, "diff", "--cached", "--name-only").strip(), "")
        # o doctor do fim: o que foi copiado não "difere do pacote"
        self.assertNotIn(MUDA + " difere do pacote", out)
        # rodar de novo: em dia
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: EM DIA", out)

    def test_dry_run_nao_escreve(self):
        antes = foto(self.p)
        rc, out = self.cli("upgrade", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: DRY-RUN", out)
        self.assertIn("⚠️  2 editados por você — não serão tocados", out)
        self.assertNadaEscrito(antes)

    def test_sem_yes_e_sem_terminal_cancela(self):
        antes = foto(self.p)
        rc, out = self.cli("upgrade")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: CANCELADO", out)
        self.assertNadaEscrito(antes)

    def test_pacote_mais_velho_que_o_projeto_e_64(self):
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        antes = foto(self.p)
        rc, out = self.cli("upgrade", "--yes", pkg=self.antigo)
        self.assertEqual(rc, 64, out)
        self.assertIn("este pacote (v9.8.6) é mais velho que o projeto (v9.8.7)", out)
        self.assertNadaEscrito(antes)

    def test_lista_longa_corta_em_10_e_verbose_mostra_tudo(self):
        templates = sorted(p for p in (self.p / "sdd/templates").rglob("*") if p.is_file())[:12]
        self.assertEqual(len(templates), 12)
        for f in templates:   # ausentes no projeto: viram "novos", 13 com o ENTRA
            f.unlink()
        rc, out = self.cli("upgrade", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("+ 13 novos (copiar)", out)
        bloco = out.split("+ 13 novos (copiar)\n", 1)[1].split("\n~ ", 1)[0]
        self.assertEqual(bloco.count("    "), 11, bloco)   # 10 nomes + "e mais 3"
        self.assertTrue(bloco.endswith("    e mais 3"), bloco)
        rc, out_v = self.cli("upgrade", "--dry-run", "--verbose")
        self.assertEqual(rc, 0, out_v)
        self.assertNotIn("    e mais ", out_v)

    @unittest.skipIf(*SEM_CHMOD)
    @unittest.skipIf(*SOU_ROOT)
    def test_escrita_que_falha_nao_mexe_no_registro_e_rodar_de_novo_retoma(self):
        reg_antes = (self.p / "sdd/open-instalado.txt").read_bytes()
        trava = self.p / "sdd/bin"
        modo = stat.S_IMODE(trava.stat().st_mode)
        trava.chmod(0o555)
        try:
            rc, out = self.cli("upgrade", "--yes")
        finally:
            trava.chmod(modo)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("o registro de versão não foi mudado; rode o upgrade de novo, ele retoma", out)
        self.assertEqual((self.p / "sdd/open-instalado.txt").read_bytes(), reg_antes)
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: ATUALIZADO, 2 PARA MESCLAR", out)
        self.assertEqual(sha(self.p / MUDA), sha(self.novo / MUDA))

    def test_ultimo_instalavel_ausente_nao_derruba_o_upgrade(self):
        # revisão do código, rodada 1, R3: com pipefail, `[ -f ] && printf` no último arquivo saía 1
        rc, out, err = self.roda([BASH, "-c", '. "$1"; instalaveis "$2" | tail -1', "x",
                                  str(self.novo / "bin/lib/versao.sh"), str(self.novo)], self.tmp)
        ultimo = out.strip()
        self.assertTrue(ultimo, out + err)
        (self.p / ultimo).unlink()
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        self.assertEqual(sha(self.p / ultimo), sha(self.novo / ultimo))

    def test_versao_nova_sem_instalavel_mudado_regrava_o_registro(self):
        # revisão do código, rodada 1, R2: sem isso o aviso de versão nova não saía nunca
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 0, out)
        mais_nova = copia_pacote(self.tmp / "mais-nova", "v9.8.8")
        rc, out = self.cli("upgrade", "--yes", pkg=mais_nova)
        self.assertEqual(rc, 0, out)
        self.assertIn("~ sdd/open-instalado.txt (registro: v9.8.7 → v9.8.8)", out)
        self.assertNotIn("RESULTADO: EM DIA", out)
        self.assertIn("\nversao: v9.8.8\n", (self.p / "sdd/open-instalado.txt").read_text(encoding="utf-8"))
        rc, out = self.cli("upgrade", "--yes", pkg=mais_nova)
        self.assertIn("RESULTADO: EM DIA", out)

    def test_falha_ao_por_a_versao_nova_ao_lado_termina_em_erro(self):
        # revisão do código, rodada 1, R5: o exit no laço saía sem RESULTADO: ERRO
        reg_antes = (self.p / "sdd/open-instalado.txt").read_bytes()
        (self.p / "sdd/upgrade").write_text("um arquivo no lugar da pasta\n", encoding="utf-8")
        rc, out = self.cli("upgrade", "--yes")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("RESULTADO: ERRO", out)
        self.assertIn("o registro de versão não foi mudado; rode o upgrade de novo, ele retoma", out)
        self.assertEqual((self.p / "sdd/open-instalado.txt").read_bytes(), reg_antes)

    def test_registro_com_asterisco_do_git_bash_e_lido(self):
        # o sha256sum do Git Bash pode escrever "<sha> *<caminho>": quem lê normaliza
        reg = self.p / "sdd/open-instalado.txt"
        linhas = reg.read_text(encoding="utf-8").splitlines()
        reg.write_text("\n".join(ln[:64] + " *" + ln[66:] if len(ln) > 66 and ln[64:66] == "  " else ln
                                 for ln in linhas) + "\n", encoding="utf-8")
        rc, out = self.cli("upgrade", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️  2 editados por você — não serão tocados", out)   # os intactos não viraram editados


class SemRegistro(Base):
    def setUp(self):
        super().setUp()
        (self.p / "sdd/open-instalado.txt").unlink()

    def test_sem_de_para_antes_de_escrever_com_os_comandos(self):
        antes = foto(self.p)
        rc, out = self.cli("upgrade", "--yes")
        self.assertEqual(rc, 64, out)
        self.assertIn("🛑 este projeto não tem o registro de versão", out)
        self.assertIn("RESULTADO: ERRO", out)
        self.assertIn("upgrade --de vX.Y.Z (a versão que o projeto tem)", out)
        self.assertIn("upgrade --de <pasta extraída>", out)
        self.assertIn("nada foi escrito", out)
        self.assertNadaEscrito(antes)

    def test_de_pasta_do_pacote_antigo(self):
        rc, out = self.cli("upgrade", "--de", str(self.antigo), "--yes")
        self.assertEqual(rc, 0, out)
        self.assertIn("▶ upgrade v9.8.6 → v9.8.7 — plano", out)
        self.assertIn("+ sdd/open-instalado.txt (registro da versão v9.8.7)", out)
        self.assertIn("RESULTADO: ATUALIZADO, 2 PARA MESCLAR", out)
        for e in EDITADOS:
            pd = (self.p / "sdd/upgrade/v9.8.7" / (e + ".pacote.diff")).read_text(encoding="utf-8")
            self.assertIn("-linha do pacote antigo", pd)   # com o pacote antigo à mão: antigo → novo
        self.assertEqual(sha(self.p / MUDA), sha(self.novo / MUDA))
        self.assertIn("\nversao: v9.8.7\n", (self.p / "sdd/open-instalado.txt").read_text(encoding="utf-8"))

    def test_de_que_nao_e_pacote_e_64(self):
        antes = foto(self.p)
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        rc, out = self.cli("upgrade", "--de", str(vazia), "--yes")
        self.assertEqual(rc, 64, out)
        self.assertIn("não é um pacote do sdd-open (sem MANIFEST.txt)", out)
        sem_versao = self.tmp / "velho"
        shutil.copytree(str(self.antigo), str(sem_versao))
        rc, out = self.cli("upgrade", "--de", str(sem_versao), "--yes")
        self.assertEqual(rc, 64, out)
        self.assertIn("não sei a versão do pacote em --de", out)
        self.assertIn("--prefix=sdd-open-vX.Y.Z/", out)
        rc, out = self.cli("upgrade", "--de", "2.12", "--yes")
        self.assertEqual(rc, 64, out)
        rc, out = self.cli("upgrade", "--de", "v9.0.0", "--yes")   # forma tag, mas o pacote novo não é clone
        self.assertEqual(rc, 64, out)
        self.assertNadaEscrito(antes)

    def test_de_de_outra_versao_avisa_antes_do_sim(self):
        outro = self.tmp / "sdd-open-v9.0.0"
        (outro / "sdd").mkdir(parents=True)
        (outro / "sdd/playbook.md").write_text("outro\n", encoding="utf-8")
        (outro / "sdd/invariants.md").write_text("outro\n", encoding="utf-8")
        (outro / "MANIFEST.txt").write_text("sdd/playbook.md\nsdd/invariants.md\n", encoding="utf-8")
        rc, out = self.cli("upgrade", "--de", str(outro), "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️  a pasta --de (v9.0.0) não parece a versão deste projeto: só 0 de 2 arquivos batem", out)


class PacoteReal(Sandbox):
    """O caso que o critério de sucesso promete: um projeto instalado pela v2.12.1 de verdade."""

    @unittest.skipIf(*SEM_PACOTE_ANTIGO)
    def test_upgrade_de_v2_12_1(self):
        rc, _, _ = self.roda(["git", "-C", str(RAIZ), "rev-parse", "-q", "--verify", "refs/tags/v2.12.1"], RAIZ)
        if not (RAIZ / ".git").exists() or rc != 0:
            self.skipTest("sem a tag v2.12.1 aqui (cópia de git archive, ou clone sem tags): o pacote real só roda "
                          "no CI e na máquina de quem mantém")
        velho = self.tmp / "velho.tar"
        self.roda(["git", "-C", str(RAIZ), "archive", "--prefix=sdd-open-v2.12.1/", "-o", str(velho), "v2.12.1"],
                  self.tmp)
        self.roda(["tar", "-xf", velho.name], self.tmp)
        p = self.repo("projeto")
        self.git(p, "commit", "-q", "--allow-empty", "-m", "raiz")
        self.git(p, "switch", "-q", "-c", "trabalho")
        rc, out, err = self.roda([BASH, self.tmp / "sdd-open-v2.12.1/bin/sdd-open.sh", "init", "--yes",
                                  "--vendors", "claude"], p)
        self.assertEqual(rc, 0, out + err)
        self.assertFalse((p / "sdd/open-instalado.txt").exists())   # a v2.12.1 não grava registro
        self.commit(p, "instala v2.12.1")
        rc, out, err = self.roda([BASH, RAIZ / "bin/sdd-open.sh", "upgrade", "--de", "v2.12.1", "--yes"], p)
        out += err
        self.assertEqual(rc, 0, out)
        self.assertIn("▶ upgrade v2.12.1 → ", out)
        self.assertNotIn("editados por você", out)   # nada foi editado: tudo é do pacote
        self.assertIn("RESULTADO: ATUALIZADO\n", out)
        # todo o resto instalável ficou igual ao pacote novo
        for ln in (p / "sdd/open-instalado.txt").read_text(encoding="utf-8").splitlines()[3:]:
            caminho = ln[66:]
            with self.subTest(arquivo=caminho):
                self.assertEqual(sha(p / caminho), ln[:64])


if __name__ == "__main__":
    unittest.main()
