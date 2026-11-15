"""F22 (AT-001 a AT-005, AT-008, AT-009): versão do pacote, registro do init, aviso de versão nova e hooks de outra
worktree.

Nenhum teste depende da versão deste clone: o pacote de teste é uma cópia da árvore com o VERSION escrito pelo teste
(ou o nome sdd-open-vX.Y.Z), e o "repositório público" é um repositório local com tags. A suíte nunca vai à rede
(tests/apoio.py desliga a checagem); os testes que a ligam apontam SDD_OPEN_REMOTO para uma pasta local.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import stat
import sys
import time
import unittest
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox, caminho_bash, caminho_neutro, SEM_CHMOD, SEM_SYMLINK
from test_gerar_starter import Base as BaseStarter

CLI = RAIZ / "bin/sdd-open.sh"
VERSAO_NOVA = RAIZ / "sdd/bin/versao-nova.sh"
LIB = RAIZ / "bin/lib/versao.sh"
SEM_COPIA = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".DS_Store", "features", "reports", "reviews",
                                   "handoffs", "releases", "upgrade")


def copia_pacote(destino: Path, versao: str | None) -> Path:
    """Uma cópia do pacote desta árvore (sem .git), com o VERSION que o teste quer (None = sem VERSION)."""
    shutil.copytree(str(RAIZ), str(destino), ignore=SEM_COPIA)
    v = destino / "VERSION"
    if versao is None:
        if v.exists():
            v.unlink()
    else:
        v.write_text(versao + "\n", encoding="utf-8")
    return destino


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class Pacotes(Sandbox):
    """Um pacote de teste por classe (copiar a árvore leva um instante; os testes só leem)."""

    VERSAO = "v9.8.7"

    @classmethod
    def setUpClass(cls):
        import tempfile
        cls._base = Path(tempfile.mkdtemp(prefix="sdd-open-f22-")).resolve()
        cls.pkg = copia_pacote(cls._base / "pacote", cls.VERSAO)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(str(cls._base), ignore_errors=True)

    def cli(self, cwd: Path, *args: str, env: dict | None = None, pkg: Path | None = None):
        rc, out, err = self.roda([BASH, (pkg or self.pkg) / "bin/sdd-open.sh", *args], cwd, env=env)
        return rc, out + err

    def remoto(self, *tags: str) -> Path:
        r = self.repo("remoto-%d" % len(list(self.tmp.glob("remoto-*"))))
        self.git(r, "commit", "-q", "--allow-empty", "-m", "x")
        for t in tags:
            self.git(r, "tag", t)
        return r

    def env_ligada(self, remoto: Path) -> dict:
        return dict(self.env, SDD_OPEN_CHECK_UPDATES="1", SDD_OPEN_REMOTO=str(remoto))


# ── AT-001 ─────────────────────────────────────────────────────────────────────────────────────────
class VersaoDoPacote(Sandbox):
    """Cada fonte de versao_do_pacote prova que respondeu (LM-017: reserva silenciosa esconde o caminho errado)."""

    def fonte(self, pasta: Path) -> str:
        rc, out, err = self.roda([BASH, "-c", '. "$1"; versao_do_pacote "$2"; printf "%s %s\\n" "$VERSAO_PKG" '
                                  '"$VERSAO_FONTE"', "x", caminho_bash(LIB), caminho_bash(pasta)], self.tmp)
        self.assertEqual(rc, 0, out + err)
        return out.strip()

    def test_carimbo(self):
        p = self.tmp / "qualquer"
        p.mkdir()
        (p / "VERSION").write_text("v9.8.7\n", encoding="utf-8")
        self.assertEqual(self.fonte(p), "v9.8.7 carimbo")
        (p / "VERSION").write_text("v9.8.7-3-gabc1234\r\n", encoding="utf-8")
        self.assertEqual(self.fonte(p), "v9.8.7-3-gabc1234 carimbo")

    def test_describe_so_na_raiz_de_um_clone(self):
        r = self.repo("sdd-open")
        (r / "VERSION").write_text("$Format:%(describe:tags=true,match=v[0-9]*)$\n", encoding="utf-8")
        self.commit(r, "x")
        self.git(r, "tag", "v9.8.6")
        self.assertEqual(self.fonte(r), "v9.8.6 describe")
        self.git(r, "commit", "-q", "--allow-empty", "-m", "y")
        self.assertRegex(self.fonte(r), r"^v9\.8\.6-1-g[0-9a-f]+ describe$")
        # pacote extraído DENTRO de outro repositório: não herda a versão dele
        dentro = r / "sdd-open-dentro"
        dentro.mkdir()
        self.assertEqual(self.fonte(dentro), "desconhecida desconhecida")

    @unittest.skipIf(*SEM_SYMLINK)
    def test_describe_pelo_caminho_de_um_link(self):
        # revisão do DESIGN, rodada 2, R1: "é a raiz do clone" compara a pasta (-ef), não a grafia do caminho
        r = self.repo("sdd-open")
        self.commit(r, "x")
        self.git(r, "tag", "v9.8.3")
        link = self.tmp / "atalho"
        os.symlink(str(r), str(link))
        self.assertEqual(self.fonte(link), "v9.8.3 describe")

    def test_pasta_e_desconhecida(self):
        p = self.tmp / "sdd-open-v9.8.5"
        p.mkdir()
        (p / "VERSION").write_text("$Format:%(describe)$\n", encoding="utf-8")   # carimbo que não pegou: segue
        self.assertEqual(self.fonte(p), "v9.8.5 pasta")
        q = self.tmp / "sdd-open"
        q.mkdir()
        self.assertEqual(self.fonte(q), "desconhecida desconhecida")
        lixo = self.tmp / "sdd-open-v9.8"
        lixo.mkdir()
        self.assertEqual(self.fonte(lixo), "desconhecida desconhecida")

    def test_git_archive_carimba_a_tag(self):
        rc, out, _ = self.roda(["git", "--version"], self.tmp)
        m = re.search(r"(\d+)\.(\d+)", out)
        if not m or (int(m.group(1)), int(m.group(2))) < (2, 35):
            self.skipTest("git anterior ao 2.35 não tem %(describe:tags=…) no export-subst")
        r = self.repo("fonte")
        # o texto do carimbo escrito aqui: numa cópia de git archive (o Verify Gate), o VERSION do pacote já vem carimbado
        (r / "VERSION").write_text("$Format:%(describe:tags=true,match=v[0-9]*)$\n", encoding="utf-8")
        (r / ".gitattributes").write_text("VERSION export-subst\n", encoding="utf-8")
        self.commit(r, "x")
        self.git(r, "tag", "v9.8.4")
        tar = self.tmp / "p.tar"
        self.git(r, "archive", "--prefix=sdd-open-v9.8.4/", "-o", str(tar), "v9.8.4")
        self.roda(["tar", "-xf", tar.name], self.tmp)
        self.assertEqual(self.fonte(self.tmp / "sdd-open-v9.8.4"), "v9.8.4 carimbo")

    def test_o_pacote_tem_o_carimbo_e_o_atributo(self):
        # no clone, o texto do carimbo; numa cópia de git archive (o Verify Gate), a versão já carimbada
        v = (RAIZ / "VERSION").read_text(encoding="utf-8").strip()
        if v.startswith("$Format"):
            self.assertEqual(v, "$Format:%(describe:tags=true,match=v[0-9]*)$")
        else:
            self.assertRegex(v, r"^(v[0-9]+\.[0-9]+\.[0-9]+(-[0-9]+-g[0-9a-f]+)?)?$")
        self.assertIn("\nVERSION export-subst\n", (RAIZ / ".gitattributes").read_text(encoding="utf-8"))

    def test_release_cria_a_tag_antes_do_archive_e_confere_o_carimbo(self):
        yml = (RAIZ / ".github/workflows/release.yml").read_text(encoding="utf-8")
        passo = yml.split("- name: Build package and checksums", 1)[1].split("- name:", 1)[0]
        tag = passo.index('git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || git tag "$TAG" "$GITHUB_SHA"')
        self.assertLess(tag, passo.index("git archive --format"))
        self.assertIn('sdd-open-$TAG/VERSION', passo)
        self.assertIn('[ "$carimbo" = "$TAG" ] || {', passo)
        self.assertNotIn("git push", passo)   # a tag é local; quem publica é o gh release create


# ── AT-002 ─────────────────────────────────────────────────────────────────────────────────────────
class RegistroDoInit(Pacotes):
    def instalaveis(self) -> list[str]:
        rc, out, err = self.roda([BASH, "-c", '. "$1"; instalaveis "$2"', "x", caminho_bash(LIB),
                                  caminho_bash(self.pkg)], self.tmp)
        self.assertEqual(rc, 0, out + err)
        return out.splitlines()

    def test_1a_instalacao_grava_versao_e_impressoes_do_pacote(self):
        p = self.repo("projeto")
        rc, out = self.cli(p, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertIn("+ sdd/open-instalado.txt (registro da versão v9.8.7", out)
        reg = (p / "sdd/open-instalado.txt").read_text(encoding="utf-8").splitlines()
        self.assertTrue(reg[0].startswith("# ") and reg[1].startswith("# "), reg[:2])
        self.assertIn("não edite; apagar faz o próximo upgrade pedir --de", reg[1].lower())
        self.assertEqual(reg[2], "versao: v9.8.7")
        linhas = reg[3:]
        caminhos = [ln[66:] for ln in linhas]
        self.assertEqual(caminhos, self.instalaveis())
        self.assertGreater(len(caminhos), 100)
        for ln in linhas:
            self.assertRegex(ln, r"^[0-9a-f]{64}  \S")
        for c in caminhos:
            self.assertFalse(c.startswith(("sdd/fixtures/", "sdd/config")), c)
            self.assertTrue(c.startswith((".agents/skills/sdd-", ".agents/skills/ux-review-builder/", "sdd/")), c)
        amostra = dict((ln[66:], ln[:64]) for ln in linhas)
        for c in (".agents/skills/sdd-build/SKILL.md", "sdd/bin/versao-nova.sh", "sdd/playbook.md"):
            self.assertEqual(amostra[c], sha(self.pkg / c), c)   # a impressão é a do conteúdo DO PACOTE
        # 2º init: o registro não muda, byte a byte
        antes = (p / "sdd/open-instalado.txt").read_bytes()
        rc, out = self.cli(p, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertEqual((p / "sdd/open-instalado.txt").read_bytes(), antes)

    def test_projeto_que_ja_tinha_sdd_fica_sem_registro(self):
        p = self.repo("projeto")
        self.escreve(p, "sdd/playbook.md", "# meu playbook\n")
        rc, out = self.cli(p, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertFalse((p / "sdd/open-instalado.txt").exists())
        self.assertIn("versão: projeto sem registro de versão (instalado antes da v2.17.0, ou o registro foi apagado) "
                      "· pacote v9.8.7", out)

    def test_pacote_de_versao_desconhecida_instala_sem_registro(self):
        sem = copia_pacote(self.tmp / "sem-versao", None)
        p = self.repo("projeto")
        rc, out = self.cli(p, "init", "--yes", "--vendors", "codex", pkg=sem)
        self.assertEqual(rc, 0, out)
        self.assertFalse((p / "sdd/open-instalado.txt").exists())
        self.assertIn("não sei a versão deste pacote", out)


# ── AT-003 e AT-004 ─────────────────────────────────────────────────────────────────────────────────
class AvisoNoDoctor(Pacotes):
    def setUp(self):
        super().setUp()
        self.p = self.repo("projeto")
        rc, out = self.cli(self.p, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)

    def test_em_dia(self):
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.8.7", "v9.8.6", "v1.0.0")))
        self.assertEqual(rc, 0, out)
        self.assertIn("✅ versão: projeto v9.8.7 · pacote v9.8.7 · última publicada v9.8.7", out)
        self.assertNotIn("saiu a", out)

    def test_versao_nova_avisa_com_o_comando_e_o_exit_nao_muda(self):
        rc0, _ = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.8.7")))
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.8.7", "v9.10.0", "v9.9.1")))
        self.assertEqual(rc, rc0)
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️  saiu a v9.10.0 (seu projeto está na v9.8.7) — veja como atualizar: "
                      "https://github.com/robertodiasduarte/sdd-open/releases/tag/v9.10.0", out)
        # o pacote de teste não é um clone: a URL e o comando com a pasta do pacote novo (U13: --dry-run primeiro)
        self.assertIn("bash <pasta do pacote novo>/bin/sdd-open.sh upgrade --dry-run", out)

    def test_clone_sugere_pull_e_dry_run(self):
        clone = self.tmp / "clone"
        shutil.copytree(str(self.pkg), str(clone))
        self.git(clone, "init", "-q")
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.9.0")), pkg=clone)
        self.assertEqual(rc, 0, out)
        self.assertRegex(caminho_neutro(out), r"→ git -C \S+/clone pull, depois bash \S+/clone/bin/sdd-open\.sh "
                                              r"upgrade --dry-run")

    def test_tags_fora_da_forma_sao_ignoradas(self):
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.8.7", "v10.0.0-rc", "v99.0",
                                                                             "v99.0.0.1", "lixo")))
        self.assertEqual(rc, 0, out)
        self.assertIn("última publicada v9.8.7", out)

    def test_sem_nenhuma_versao_na_lista(self):
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("lixo", "v1.2")))
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️  versão nova: não conferida — nenhuma versão na lista (o resto do diagnóstico vale)", out)

    def test_remoto_que_nao_existe_e_informacao_nao_atencao(self):
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.tmp / "nao-existe"))
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"ℹ️  versão nova: não conferida — .+ \(o resto do diagnóstico vale\)")
        self.assertNotIn("⚠️  versão", out)
        self.assertIn("✅ versão: projeto v9.8.7 · pacote v9.8.7\n", out)

    def test_desligada_pela_variavel_e_pelo_slot(self):
        rc, out = self.cli(self.p, "doctor")   # a suíte desliga pela variável (tests/apoio.py)
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️  versão nova: checagem desligada (SDD_OPEN_CHECK_UPDATES=0 no ambiente)", out)
        cfg = self.p / "sdd/config.yaml"
        texto = cfg.read_text(encoding="utf-8")
        self.assertIn("\nopen:\n  check_updates: true\n", texto)   # o init copia o bloco do config.example.yaml
        cfg.write_text(texto.replace("  check_updates: true\n", "  check_updates: false   # sem rede aqui\n"),
                       encoding="utf-8")
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.9.0")))
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️  versão nova: checagem desligada (open.check_updates: false em sdd/config.yaml)", out)
        self.assertNotIn("saiu a", out)

    def test_projeto_sem_registro_compara_com_a_versao_do_pacote(self):
        (self.p / "sdd/open-instalado.txt").unlink()
        rc, out = self.cli(self.p, "doctor", env=self.env_ligada(self.remoto("v9.9.0")))
        self.assertEqual(rc, 0, out)
        self.assertIn("ℹ️  versão: projeto sem registro de versão (instalado antes da v2.17.0, ou o registro foi "
                      "apagado) · pacote v9.8.7 — o 1º upgrade pede --de <a versão que o projeto tem>", out)
        self.assertIn("saiu a v9.9.0 (seu projeto está na v9.8.7)", out)

    def test_avisos_antigos_apontam_o_upgrade(self):
        alvo = self.p / "sdd/bin/report-lint.py"
        alvo.write_text(alvo.read_text(encoding="utf-8") + "# minha mudança\n", encoding="utf-8")
        reg = self.p / "sdd/open-instalado.txt"
        # registro de uma versão anterior: o upgrade é o caminho
        reg.write_text(reg.read_text(encoding="utf-8").replace("versao: v9.8.7", "versao: v9.8.6"), encoding="utf-8")
        rc, out = self.cli(self.p, "doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd/bin/report-lint.py difere do pacote — rode o upgrade (ele copia o que é do pacote e não "
                      "toca no que você editou)", out)
        self.assertNotIn("apague e rode init", out)
        # já na versão do pacote: é edição sua, e o upgrade não resolveria (revisão do DESIGN, rodada 2, R6)
        reg.write_text(reg.read_text(encoding="utf-8").replace("versao: v9.8.6", "versao: v9.8.7"), encoding="utf-8")
        rc, out = self.cli(self.p, "doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("sdd/bin/report-lint.py difere do pacote — é edição sua, que o upgrade não toca; para voltar à "
                      "do pacote, apague o arquivo e rode o upgrade", out)


class ChecagemComTeto(Sandbox):
    """O script do projeto, direto: o teto vale sem depender de o git morrer, e desligada não chama o git."""

    def falso(self, corpo: str) -> dict:
        d = self.tmp / "falso"
        d.mkdir(exist_ok=True)
        g = d / "git"
        g.write_text("#!/bin/sh\n" + corpo, encoding="utf-8")
        g.chmod(0o755)
        return dict(self.env, SDD_OPEN_CHECK_UPDATES="1", PATH=str(d) + os.pathsep + self.env["PATH"])

    @unittest.skipIf(*SEM_CHMOD)
    def test_git_pendurado_com_neto_sai_em_ate_7_s(self):
        env = self.falso("sleep 30 &\nsleep 30\n")
        t0 = time.monotonic()
        rc, out, err = self.roda([BASH, VERSAO_NOVA, "--atual", "v1.0.0"], self.tmp, env=env)
        dt = time.monotonic() - t0
        self.assertEqual(rc, 20, out + err)
        self.assertIn("ℹ️  versão nova: não conferida — sem resposta em 5 s (o resto do diagnóstico vale)", out)
        self.assertLess(dt, 7.0)   # LM-031: só o limite de cima

    @unittest.skipIf(*SEM_CHMOD)
    def test_desligada_nao_chama_o_git(self):
        marca = self.tmp / "chamado"
        env = self.falso("touch '%s'\n" % caminho_bash(marca))
        env["SDD_OPEN_CHECK_UPDATES"] = "0"
        rc, out, err = self.roda([BASH, VERSAO_NOVA, "--atual", "v1.0.0"], self.tmp, env=env)
        self.assertEqual(rc, 30, out + err)
        self.assertFalse(marca.exists())
        env["SDD_OPEN_CHECK_UPDATES"] = "1"
        self.escreve(self.tmp, "sdd/config.yaml", "open:\n  check_updates: false\n")
        rc, out, err = self.roda([BASH, VERSAO_NOVA, "--raiz", self.tmp, "--atual", "v1.0.0"], self.tmp, env=env)
        self.assertEqual(rc, 30, out + err)
        self.assertFalse(marca.exists())

    def test_sem_versao_atual_nao_consulta(self):
        env = dict(self.env, SDD_OPEN_CHECK_UPDATES="1")
        rc, out, err = self.roda([BASH, VERSAO_NOVA, "--raiz", self.tmp], self.tmp, env=env)
        self.assertEqual(rc, 20, out + err)
        self.assertIn("este projeto ainda não tem o registro de versão", out)

    def test_uso(self):
        for args in (["--atual", "2.0"], ["--bogus"], ["--raiz"]):
            with self.subTest(args=args):
                rc, out, err = self.roda([BASH, VERSAO_NOVA, *args], self.tmp)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)

    def test_curto_e_exits(self):
        r = self.repo("remoto")
        self.git(r, "commit", "-q", "--allow-empty", "-m", "x")
        self.git(r, "tag", "v1.2.0")
        self.git(r, "tag", "v1.10.0")
        env = dict(self.env, SDD_OPEN_CHECK_UPDATES="1", SDD_OPEN_REMOTO=str(r))
        casos = (("v1.2.0", 10, "⚠️  saiu a v1.10.0 (este projeto está na v1.2.0)"),
                 ("v1.10.0", 0, "✅ versão: em dia — a última publicada é v1.10.0"),
                 ("v1.10.0-4-gabc1234", 0, "✅ versão: em dia — a última publicada é v1.10.0"),
                 ("v2.0.0", 0, "✅ versão: em dia — a última publicada é v1.10.0"))
        for atual, exit_, linha in casos:
            with self.subTest(atual=atual):
                rc, out, err = self.roda([BASH, VERSAO_NOVA, "--atual", atual], self.tmp, env=env)
                self.assertEqual((rc, out.strip()), (exit_, linha), err)
        rc, out, _ = self.roda([BASH, VERSAO_NOVA, "--atual", "v1.2.0", "--curto"], self.tmp, env=env)
        self.assertEqual((rc, out.strip()), (10, "v1.10.0"))


class SuiteSemRede(unittest.TestCase):
    def test_a_suite_desliga_a_checagem(self):
        if os.environ.get("SDD_OPEN_CHECK_UPDATES") != "0":
            self.skipTest("quem roda a suíte ligou a checagem de propósito")
        self.assertNotIn("github.com", os.environ.get("SDD_OPEN_REMOTO", ""))

    def test_todo_modulo_que_roda_o_sdd_open_importa_o_apoio(self):
        faltam = []
        for f in sorted((RAIZ / "tests").glob("test_*.py")):
            t = f.read_text(encoding="utf-8")
            roda = "sdd-open.sh" in t or "versao-nova.sh" in t
            importa = re.search(r"^(from apoio import|import apoio|from test_\w+ import)", t, re.M)
            if roda and not importa:
                faltam.append(f.name)
        self.assertEqual(faltam, [], "módulo que roda o sdd-open.sh sem importar o tests/apoio.py (a trava de rede)")

    def test_workflows_tem_a_segunda_trava(self):
        for nome in ("release.yml", "publish-gate.yml"):
            yml = (RAIZ / ".github/workflows" / nome).read_text(encoding="utf-8")
            with self.subTest(workflow=nome):
                # os 3 jobs de teste (e, no publish-gate, também o smoke do init)
                self.assertGreaterEqual(yml.count("SDD_OPEN_CHECK_UPDATES: '0'"), 3)


# ── AT-005 ─────────────────────────────────────────────────────────────────────────────────────────
FRASE = ("Saiu a versão v2.18.0 do SDD Open (este projeto está na v2.17.0). Não precisa parar agora; quando quiser, "
         "peça ao agente para atualizar.")


def sem_quebra(t: str) -> str:
    return re.sub(r"\s+", " ", t)


class AvisoNasSkills(unittest.TestCase):
    def test_new_session_repassa_sem_parar(self):
        s = (RAIZ / ".agents/skills/sdd-new-session/SKILL.md").read_text(encoding="utf-8")
        passo = sem_quebra(s.split("## Passo 3 — Responda", 1)[1].split("\n## ", 1)[0])
        self.assertIn("`bash sdd/bin/versao-nova.sh`", passo)
        self.assertIn("Exit 10 ⇒ uma frase", passo)
        self.assertIn(FRASE, passo)
        self.assertIn("Qualquer outro exit, ou sem o script: nada. Nunca vira pergunta nem parada.", passo)
        self.assertLess(passo.index("versao-nova.sh"), passo.index("Última linha, destacada"))

    def test_release_repassa_na_fase_0_sem_abortar(self):
        s = (RAIZ / ".agents/skills/sdd-release/SKILL.md").read_text(encoding="utf-8")
        fase0 = sem_quebra(s.split("## FASE 0", 1)[1].split("**0a.", 1)[0])
        self.assertIn("Rode `bash sdd/bin/versao-nova.sh` (se existir): exit 10 ⇒ a frase de versão nova "
                      "(`references/como-falar.md`) no relatório e no bloco do OK, sem abortar; senão, nada.", fase0)
        cf = sem_quebra((RAIZ / ".agents/skills/sdd-release/references/como-falar.md").read_text(encoding="utf-8"))
        self.assertIn("## Versão nova do SDD Open (FASE 0, item 0)", cf)
        self.assertIn(FRASE, cf)
        self.assertIn("Nunca é pergunta, nunca para nem muda o OK", cf)


class StarterSemOAviso(BaseStarter):
    def test_new_session_e_release_geradas_sem_o_passo(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for skill in ("sdd-new-session", "sdd-release"):
            with self.subTest(skill=skill):
                texto = "".join(p.read_text(encoding="utf-8") for p in (self.starter / "skills" / skill).rglob("*.md"))
                self.assertNotIn("versao-nova", texto)
                self.assertNotIn("Saiu a versão", texto)
        ns = (self.starter / "skills/sdd-new-session/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("5. **Última linha, destacada**", ns)


# ── AT-008 ─────────────────────────────────────────────────────────────────────────────────────────
class HooksDeOutraWorktree(Pacotes):
    def setUp(self):
        super().setUp()
        self.a = self.repo("principal")
        self.git(self.a, "commit", "-q", "--allow-empty", "-m", "raiz")
        rc, out = self.cli(self.a, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.commit(self.a, "init")
        self.b = self.tmp / "frente"
        self.git(self.a, "worktree", "add", "-q", "-b", "frente", str(self.b))
        # a outra worktree gravou o caminho absoluto (o .git/config é de todas)
        self.git(self.a, "config", "core.hooksPath", str(self.a / "sdd/hooks"))

    def test_doctor_diz_ligados_e_de_onde(self):
        rc, out = self.cli(self.b, "doctor")
        self.assertEqual(rc, 0, out)
        self.assertRegex(caminho_neutro(out),
                         r"✅ hooks ligados \(pelo sdd/hooks de outra worktree deste repositório: \S*principal\)")
        self.assertNotIn("outro gerenciador", out)

    def test_init_trata_como_ligado(self):
        rc, out = self.cli(self.b, "init", "--yes", "--vendors", "codex")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("husky, lefthook ou outro gerenciador", out)
        self.assertEqual(caminho_neutro(self.git(self.b, "config", "--get", "core.hooksPath").strip()),
                         caminho_neutro(str(self.a / "sdd/hooks")))

    def test_caminho_de_outro_repositorio_segue_outro(self):
        outro = self.repo("outro")
        (outro / "sdd/hooks").mkdir(parents=True)
        self.git(self.a, "config", "core.hooksPath", str(outro / "sdd/hooks"))
        rc, out = self.cli(self.b, "doctor")
        self.assertEqual(rc, 0, out)
        self.assertIn("husky, lefthook ou outro gerenciador", out)
        self.assertNotIn("hooks ligados", out)


# ── AT-009 ─────────────────────────────────────────────────────────────────────────────────────────
# Os exemplos de sintaxe do próprio caderno: mostram o formato da linha, do delta e da pergunta da curadoria.
ACEITOS = {
    ".agents/skills/sdd-playbook/SKILL.md": "exemplo do formato da linha e do delta do curador",
    ".agents/skills/sdd-playbook/references/curator.md": "exemplo do delta e do bloco de curadoria",
    ".agents/skills/sdd-playbook/references/como-falar.md": "exemplo de conversa da própria curadoria",
}


class SemLmNasSkills(unittest.TestCase):
    def test_skill_e_references_sem_lm_nnn(self):
        achados = []
        # SKILL.md e qualquer arquivo de references/, não só .md (revisão do DESIGN, rodada 2, R3)
        for f in sorted((RAIZ / ".agents/skills").rglob("*")):
            rel = f.relative_to(RAIZ).as_posix()
            if not f.is_file() or rel in ACEITOS:
                continue
            if f.name != "SKILL.md" and "/references/" not in rel:
                continue
            for i, ln in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if re.search(r"\bLM-[0-9]{3}\b", ln):
                    achados.append("%s:%d" % (rel, i))
        self.assertEqual(achados, [], "cite a regra pelo texto: o número só vale no playbook que o nomeou")

    def test_aceites_ainda_existem_e_citam(self):
        for rel in ACEITOS:
            with self.subTest(arquivo=rel):
                self.assertRegex((RAIZ / rel).read_text(encoding="utf-8"), r"\bLM-[0-9]{3}\b")


if __name__ == "__main__":
    unittest.main()
