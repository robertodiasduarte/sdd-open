"""sdd/bin/governanca-fronteira.sh (F12, C8): prova de que o agente fresco só escreveu o arquivo permitido.

DEFINE F12 AT-005 e AT-006: novo, sobrescrito (inclusive arquivo já sujo antes), apagado, nome com acento,
arquivo novo em pasta sem nada rastreado, arquivo em pasta ignorada de sdd/, caminho por link simbólico; e
os 64 de fronteira não verificada. A sabotagem compara só o caminho (sem o sha) e a sobrescrita some.
"""
from __future__ import annotations

import os
import shutil

from apoio import BASH, RAIZ, Sandbox

SCRIPT = "sdd/bin/governanca-fronteira.sh"


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.w = self.repo("w")
        self.escreve(self.w, ".gitignore", "sdd/reviews/\n")
        self.escreve(self.w, "a.txt", "a\n")
        self.escreve(self.w, "sdd/bin/x.sh", "x\n")
        self.commit(self.w)
        self.s = self.tmp / "snaps"
        self.s.mkdir()
        self.script = str(RAIZ / SCRIPT)
        self.rel = str(self.w / "sdd/reviews/REL.md")

    def fr(self, *args: str, script: str | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, script or self.script, *args], self.w)
        return rc, out + err

    def snap(self, nome: str, script: str | None = None) -> None:
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / nome), self.rel, script=script)
        self.assertEqual(rc, 0, out)

    def comparar(self, script: str | None = None) -> tuple[int, str]:
        return self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), self.rel, script=script)


class Fronteira(Base):
    def test_so_o_permitido_mudou(self):
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.snap("antes")
        self.escreve(self.w, "sdd/reviews/REL.md", "relatório\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 0, out)
        self.assertIn("MUDOU: ", out)
        self.assertIn("RESULTADO: SÓ O PERMITIDO MUDOU", out)
        self.assertNotIn("FORA:", out)

    def test_cada_escrita_fora_do_permitido_aparece(self):
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.escreve(self.w, "sdd/reviews/velho.md", "v\n")
        self.escreve(self.w, "ação.md", "x\n")
        self.snap("antes")
        self.escreve(self.w, "DEFINE.md", "sobrescrito pelo agente\n")      # já sujo antes
        (self.w / "a.txt").unlink()                                          # apagado
        self.escreve(self.w, "ação.md", "y\n")                               # nome com acento
        self.escreve(self.w, "novo/pasta/arq.md", "n\n")                     # pasta sem nada rastreado
        self.escreve(self.w, "sdd/reviews/velho.md", "mexido\n")             # pasta ignorada de sdd/
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)
        for p in ("DEFINE.md", "a.txt", "ação.md", "novo/pasta/arq.md", "sdd/reviews/velho.md"):
            with self.subTest(caminho=p):
                self.assertRegex(out, r"(?m)^FORA: .*/" + p.replace(".", r"\.") + "$")
        self.assertIn("RESULTADO: ESCRITA FORA DO PERMITIDO", out)

    def test_permitido_por_link_simbolico_casa_com_a_raiz_canonica(self):
        link = self.tmp / "link-w"
        os.symlink(str(self.w), str(link))
        rel_link = str(link / "sdd/reviews/REL.md")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "antes"), rel_link)
        self.assertEqual(rc, 0, out)
        self.escreve(self.w, "sdd/reviews/REL.md", "r\n")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "depois"), rel_link)
        self.assertEqual(rc, 0, out)
        rc, out = self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), rel_link)
        self.assertEqual(rc, 0, out)


class Aval1(Base):
    def test_m1_arquivo_limpo_editado_e_commitado_pelo_agente_e_fora(self):
        self.snap("antes")
        self.escreve(self.w, "a.txt", "mexido pelo agente\n")
        self.git(self.w, "commit", "-q", "-am", "agente commitou")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)
        self.assertIn("HEAD mudou durante o despacho", out)
        self.assertRegex(out, r"(?m)^FORA: .*/a\.txt$")

    def test_m1_snapshot_sem_head_nao_vale_como_nada_mudou(self):
        self.snap("antes")
        self.snap("depois")
        sem = self.s / "sem-head"
        sem.write_text("".join(l for l in (self.s / "antes").read_text(encoding="utf-8").splitlines(True)
                               if not l.startswith("#HEAD")), encoding="utf-8")
        rc, out = self.fr("--comparar", str(sem), str(self.s / "depois"), self.rel)
        self.assertEqual(rc, 64, out)


class Aval2(Base):
    def test_arvore_limpa_sem_incluir_compara(self):
        for nome in ("antes", "depois"):
            rc, out = self.fr("--snapshot", str(self.w), str(self.s / nome))
            self.assertEqual(rc, 0, out)
        rc, out = self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), self.rel)
        self.assertEqual(rc, 0, out)
        self.escreve(self.w, "b.txt", "b\n")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "depois"))
        rc, out = self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), self.rel)
        self.assertEqual(rc, 1, out)
        self.assertRegex(out, r"(?m)^FORA: .*/b\.txt$")


class Real1(Base):
    def test_r1_snapshot_dentro_do_worktree_nao_apaga_o_arquivo(self):
        alvo = self.escreve(self.w, "importante.md", "não apague\n")
        rc, out = self.fr("--snapshot", str(self.w), str(alvo))
        self.assertEqual(rc, 64, out)
        self.assertEqual(alvo.read_text(encoding="utf-8"), "não apague\n")

    def test_r2_arquivo_ilegivel_recusa_o_snapshot(self):
        sujo = self.escreve(self.w, "DEFINE.md", "sujo\n")
        os.chmod(str(sujo), 0)
        try:
            if os.access(str(sujo), os.R_OK):
                self.skipTest("rodando como root: chmod 0 não impede a leitura")
            rc, out = self.fr("--snapshot", str(self.w), str(self.s / "x"), self.rel)
            self.assertEqual(rc, 64, out)
            self.assertFalse((self.s / "x").exists())
        finally:
            os.chmod(str(sujo), 0o644)


class Real2(Base):
    def test_permitido_por_link_de_arquivo_casa_com_o_destino(self):
        self.escreve(self.w, "sdd/reviews/destino.md", "")
        link = self.w / "sdd/reviews/REL.md"
        os.symlink(str(self.w / "sdd/reviews/destino.md"), str(link))
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "antes"), str(link))
        self.assertEqual(rc, 0, out)
        self.escreve(self.w, "sdd/reviews/destino.md", "relatório\n")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "depois"), str(link))
        self.assertEqual(rc, 0, out)
        rc, out = self.fr("--comparar", str(self.s / "antes"), str(self.s / "depois"), str(link))
        self.assertEqual(rc, 0, out)
        self.assertNotIn("FORA:", out)


class Real3(Base):
    def test_snapshot_dentro_do_git_e_recusado(self):
        # a sandbox de agentes (medido no Codex CLI) deixa o .git só para leitura: o snapshot não mora lá
        d = self.w / ".git/sdd-fronteira"
        d.mkdir(parents=True)
        rc, out = self.fr("--snapshot", str(self.w), str(d / "antes"), self.rel)
        self.assertEqual(rc, 64, out)

    def test_alias_por_link_do_permitido_casa_com_ele(self):
        self.escreve(self.w, "sdd/reviews/REL.md", "")
        # link NÃO versionado: o git status o lista, e o hash dele segue o arquivo permitido
        os.symlink(str(self.w / "sdd/reviews/REL.md"), str(self.w / "atalho.md"))
        self.snap("antes")
        self.escreve(self.w, "sdd/reviews/REL.md", "relatório\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 0, out)
        self.assertNotIn("FORA:", out)


class Real4(Base):
    def test_link_criado_no_permitido_nao_autoriza_outro_arquivo(self):
        # o agente cria um link no caminho permitido apontando para outro arquivo e escreve nesse outro
        self.escreve(self.w, "DEFINE.md", "sujo\n")
        (self.w / "sdd/reviews").mkdir(parents=True, exist_ok=True)
        self.snap("antes")
        os.symlink(str(self.w / "DEFINE.md"), self.rel)
        self.escreve(self.w, "DEFINE.md", "reescrito pelo agente\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)
        self.assertRegex(out, r"(?m)^FORA: .*/DEFINE\.md$")
        self.assertIn("virou ou deixou de ser link", out)


class Uso(Base):
    def test_fronteira_nao_verificada_sai_64(self):
        self.snap("antes")
        casos = {
            "snapshot dentro do worktree": ("--snapshot", str(self.w), str(self.w / "snap.txt")),
            "raiz que é subpasta": ("--snapshot", str(self.w / "sdd"), str(self.s / "x")),
            "incluir fora do worktree": ("--snapshot", str(self.w), str(self.s / "x"), str(self.tmp / "fora.md")),
            "snapshot ausente": ("--comparar", str(self.s / "nao-existe"), str(self.s / "antes"), self.rel),
            "sem permitido": ("--comparar", str(self.s / "antes"), str(self.s / "antes")),
            "sem modo": (),
        }
        for nome, args in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.fr(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)
        self.assertFalse((self.w / "snap.txt").exists())


class Sabotagem(Base):
    def test_comparar_so_o_caminho_esconde_a_sobrescrita(self):
        texto = (RAIZ / SCRIPT).read_text(encoding="utf-8")
        alvo = 'saida.append("%s\\t%s" % (h.hexdigest(), r))'
        self.assertIn(alvo, texto)
        sab = self.tmp / "sabotado.sh"
        sab.write_text(texto.replace(alvo, 'saida.append("X\\t%s" % r)'), encoding="utf-8")
        self.escreve(self.w, "DEFINE.md", "sujo antes\n")
        self.snap("antes", script=str(sab))
        self.escreve(self.w, "DEFINE.md", "sobrescrito\n")
        self.snap("depois", script=str(sab))
        rc, _ = self.comparar(script=str(sab))
        self.assertEqual(rc, 0)       # o sabotado não vê
        self.snap("antes")
        self.escreve(self.w, "DEFINE.md", "de novo\n")
        self.snap("depois")
        rc, out = self.comparar()
        self.assertEqual(rc, 1, out)  # o real vê


class EstadoDoGit(Base):
    """F3, F4 e F8 da revisão da fronteira (F14): o que o `git status` não mostra."""

    def despacho(self, acao) -> tuple[int, str]:
        self.escreve(self.w, "sujo.txt", "sujo\n")
        self.snap("antes")
        acao()
        self.snap("depois")
        return self.comparar()

    def test_marca_que_esconde_arquivo_editado(self):
        for flag in ("--assume-unchanged", "--skip-worktree"):
            with self.subTest(flag=flag):
                def acao():
                    self.escreve(self.w, "a.txt", "adulterado\n")
                    self.git(self.w, "update-index", flag, "a.txt")
                rc, out = self.despacho(acao)
                self.assertEqual(rc, 1, out)
                self.assertIn("FORA: o índice do git mudou", out)
                self.git(self.w, "update-index", flag.replace("--", "--no-").replace("no-assume-unchanged", "no-assume-unchanged"), "a.txt")
                self.git(self.w, "checkout", "--", "a.txt")

    def test_git_add_conta(self):
        rc, out = self.despacho(lambda: self.git(self.w, "add", "-A"))
        self.assertEqual(rc, 1, out)
        self.assertIn("FORA: o índice do git mudou", out)

    def test_troca_de_branch_e_head_solto(self):
        rc, out = self.despacho(lambda: self.git(self.w, "checkout", "-q", "-b", "agente"))
        self.assertEqual(rc, 1, out)
        self.assertIn("FORA: a branch mudou", out)
        self.assertIn("refs/heads/agente", out)
        rc, out = self.despacho(lambda: self.git(self.w, "checkout", "-q", "--detach"))
        self.assertEqual(rc, 1, out)
        self.assertIn("DETACHED", out)

    def test_hook_exclude_e_config_contam(self):
        def hook():
            h = self.w / ".git/hooks/pre-commit"
            h.write_text("#!/bin/sh\n", encoding="utf-8")
        def exclude():
            with open(str(self.w / ".git/info/exclude"), "a", encoding="utf-8") as f:
                f.write("payload.txt\n")
            self.escreve(self.w, "payload.txt", "p\n")
        def config():
            self.git(self.w, "config", "core.hooksPath", "outra")
        for nome, acao in (("hook", hook), ("exclude", exclude), ("config", config)):
            with self.subTest(caso=nome):
                rc, out = self.despacho(acao)
                self.assertEqual(rc, 1, out)
                self.assertIn("FORA: a configuração, o exclude ou os hooks de .git mudaram", out)

    def test_leitura_pelo_git_nao_e_escrita(self):
        def leitura():
            self.git(self.w, "status")
            self.git(self.w, "diff")
            self.git(self.w, "log", "-1")
            self.roda([BASH, RAIZ / "sdd/bin/playbook-lint.sh", "--stats", RAIZ / "sdd/playbook.md"], self.w)
        rc, out = self.despacho(leitura)
        self.assertEqual(rc, 0, out)

    def test_arquivo_gravado_nao_mexe_no_indice(self):
        def relatorio():
            self.escreve(self.w, "sdd/reviews/REL.md", "r\n")
        rc, out = self.despacho(relatorio)
        self.assertEqual(rc, 0, out)
        self.assertIn("MUDOU: ", out)

    def test_snapshot_de_versao_antiga_sai_64(self):
        self.snap("antes")
        self.snap("depois")
        velho = "".join(l for l in (self.s / "antes").read_text(encoding="utf-8").splitlines(True) if not l.startswith("#INDICE"))
        (self.s / "antes").write_text(velho, encoding="utf-8")
        rc, out = self.comparar()
        self.assertEqual(rc, 64, out)
        self.assertIn("sem a linha #INDICE", out)

    def test_pasta_sem_permissao_nao_e_verde(self):
        p = self.w / "oculto"
        p.mkdir()
        self.escreve(self.w, "oculto/p.txt", "x\n")
        os.chmod(str(p), 0)
        self.addCleanup(os.chmod, str(p), 0o755)
        if os.access(str(p), os.R_OK):
            self.skipTest("o usuário lê pasta 000 (root)")
        rc, out = self.fr("--snapshot", str(self.w), str(self.s / "x"), self.rel)
        self.assertEqual(rc, 64, out)
        self.assertIn("não conseguiu abrir", out)
        self.assertFalse((self.s / "x").exists())

    def test_raiz_com_e_comercial_lista_o_caminho_certo(self):
        for nome in ("P&D fiscal", "a|b"):
            with self.subTest(raiz=nome):
                w = self.tmp / nome
                w.mkdir()
                self.git(w, "init", "-q")
                self.escreve(w, "a.txt", "a\n")
                self.commit(w)
                ra = self.roda([BASH, self.script, "--snapshot", str(w), str(self.s / "a")], w)
                self.assertEqual(ra[0], 0, ra[1] + ra[2])
                self.escreve(w, "a.txt", "b\n")
                self.commit(w, "agente")
                self.roda([BASH, self.script, "--snapshot", str(w), str(self.s / "b")], w)
                rc, out, err = self.roda([BASH, self.script, "--comparar", str(self.s / "a"), str(self.s / "b"), str(w / "x")], w)
                self.assertEqual(rc, 1, out + err)
                self.assertIn("FORA: " + str(w.resolve()) + "/a.txt", out)
