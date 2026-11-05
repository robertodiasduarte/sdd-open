"""Contrato do sdd/bin/deploy-do-sha.sh (DEFINE F14_DRIVE AT-022 a AT-026): o commit está no ar? gh de mentira no PATH,
com um cenário por teste, e git real; o registro do gh prova o que foi disparado. Sem rede."""
from __future__ import annotations

import json
import os
import shutil
import stat
import sys

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/deploy-do-sha.sh"
GH = """#!{python}
import json, os, sys
a = sys.argv[1:]
d = os.environ["GH_DIR"]
open(os.path.join(d, "gh.log"), "a").write(" ".join(a) + "\\n")
c = json.load(open(os.path.join(d, "cenario.json")))
if c.get("erro"):
    sys.stderr.write(c["erro"] + "\\n")
    sys.exit(1)
pos = os.path.join(d, "pos")
i = int(open(pos).read()) if os.path.exists(pos) else 0
passos = c["passos"]
if a[:2] == ["run", "list"]:
    if "--commit" in a:
        open(pos, "w").write(str(i + 1))
        p = passos[min(i, len(passos) - 1)]
        print(json.dumps([r for r in p["runs"] if r["headSha"] == a[a.index("--commit") + 1]]))
    else:
        p = passos[min(max(i - 1, 0), len(passos) - 1)]
        print(json.dumps(p["runs"]))
elif a[:2] == ["run", "view"]:
    print(json.dumps(dict(jobs=[dict(steps=[dict(name=c.get("passo", "x"), conclusion="failure")])])))
elif a[:2] == ["workflow", "run"]:
    if c.get("dispatch_recusado"):
        sys.stderr.write("HTTP 422: Workflow does not have workflow_dispatch trigger\\n")
        sys.exit(1)
    open(pos, "w").write(str(i + 1))
else:
    sys.exit(9)
"""


def run(ident, sha, status="completed", conclusion="success", criado="2026-01-01T00:00:00Z", branch="main", event="push"):
    return dict(databaseId=ident, headSha=sha, headBranch=branch, status=status, conclusion=conclusion, createdAt=criado, workflowName="deploy", event=event)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.bare = self.tmp / "remoto.git"
        self.roda(["git", "init", "-q", "--bare", self.bare], self.tmp)
        self.r = self.repo()
        self.git(self.r, "symbolic-ref", "HEAD", "refs/heads/main")
        self.escreve(self.r, "a.txt", "1\n")
        self.commit(self.r)
        self.git(self.r, "remote", "add", "origin", str(self.bare))
        self.git(self.r, "push", "-q", "origin", "main")
        self.x = self.git(self.r, "rev-parse", "HEAD").strip()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(GH.format(python=sys.executable), encoding="utf-8")
        gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
        self.dir_gh = self.tmp / "ghdir"
        self.dir_gh.mkdir()
        self.env = dict(self.env, PATH=str(self.bin) + os.pathsep + self.env["PATH"], GH_DIR=str(self.dir_gh))

    def novo_commit(self):
        self.escreve(self.r, "a.txt", self.git(self.r, "rev-parse", "HEAD"))
        self.commit(self.r)
        self.git(self.r, "push", "-q", "origin", "main")
        return self.git(self.r, "rev-parse", "HEAD").strip()

    def cenario(self, *passos, **extra):
        (self.dir_gh / "cenario.json").write_text(json.dumps(dict(passos=[dict(runs=list(p)) for p in passos], **extra)), encoding="utf-8")

    def sha(self, *flags, commit=None, env=None):
        return self.roda([BASH, SCRIPT, "--commit", commit or self.x, "--workflow", "deploy.yml", "--intervalo", "0", "--teto", "1", "--sem-run", "0", *flags], self.r, env)

    def log(self):
        p = self.dir_gh / "gh.log"
        return p.read_text(encoding="utf-8") if p.exists() else ""

    def assertSemRerun(self):
        self.assertNotIn("rerun", self.log())

    def assertSai(self, res, exitc, *trechos):
        rc, out, err = res
        self.assertEqual(rc, exitc, out + err)
        for t in trechos:
            self.assertIn(t, out + err)
        self.assertResultado(out if exitc != 64 else err)
        self.assertSemRerun()


class NoAr(Base):
    def test_proprio_verde(self):
        self.cenario([run(11, self.x)])
        self.assertSai(self.sha(), 0, "✅ no ar — run 11", self.x[:7])

    def test_nao_contam_outra_branch_tag_nem_outro_evento(self):
        for r in (run(1, self.x, branch="v1.0.0"), run(2, self.x, branch="feat/x"), run(3, self.x, event="schedule"), run(4, self.x, event="pull_request")):
            with self.subTest(r=r):
                self.cenario([r])
                self.assertSai(self.sha(), 4, "ainda não sei")

    def test_workflow_dispatch_conta(self):
        self.cenario([run(5, self.x, event="workflow_dispatch")])
        self.assertSai(self.sha(), 0, "✅ no ar — run 5")

    def test_espera_o_run_em_andamento_com_progresso_em_stderr(self):
        self.cenario([run(7, self.x, status="queued", conclusion=None)], [run(7, self.x, status="in_progress", conclusion=None)], [run(7, self.x)])
        rc, out, err = self.sha()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("✅ no ar", out)
        self.assertIn("⏳ queued", err)
        self.assertIn("⏳ in_progress", err)
        self.assertNotIn("⏳", out)


class Substituto(Base):
    def test_contem_o_commit_e_terminou_bem(self):
        y = self.novo_commit()
        for conclusao in ("cancelled", "failure", "timed_out"):
            with self.subTest(conclusao=conclusao):
                (self.dir_gh / "pos").write_text("0")
                self.cenario([run(1, self.x, conclusion=conclusao), run(2, y, criado="2026-01-01T00:01:00Z")])
                self.assertSai(self.sha(), 0, "✅ no ar via substituto", "run 2")

    def test_mais_novo_que_nao_contem_nao_vale(self):
        self.git(self.r, "checkout", "-q", "-b", "outra", "HEAD")
        self.escreve(self.r, "b.txt", "x\n")
        self.commit(self.r)
        outro = self.git(self.r, "rev-parse", "HEAD").strip()
        self.git(self.r, "checkout", "-q", "main")
        y = self.novo_commit()
        self.cenario([run(1, y, conclusion="cancelled"), run(2, outro, criado="2026-01-01T00:01:00Z")])
        self.assertSai(self.sha(commit=y), 2, "🔴 não está no ar", "nenhum deploy mais novo contém")

    def test_substituto_que_terminou_mal_e_nomeado(self):
        y = self.novo_commit()
        self.cenario([run(1, self.x, conclusion="cancelled"), run(2, y, conclusion="failure", criado="2026-01-01T00:01:00Z")])
        self.assertSai(self.sha(), 2, "🔴 não está no ar", "run 2")

    def test_substituto_andando_e_esperado(self):
        y = self.novo_commit()
        self.cenario([run(1, self.x, conclusion="cancelled"), run(2, y, status="in_progress", conclusion=None, criado="2026-01-01T00:01:00Z")],
                     [run(1, self.x, conclusion="cancelled"), run(2, y, criado="2026-01-01T00:01:00Z")])
        self.assertSai(self.sha(), 0, "via substituto")

    def test_commit_que_o_clone_nao_conhece_nunca_decide(self):
        desconhecido = "a" * 40
        self.cenario([run(1, self.x, conclusion="cancelled"), run(2, desconhecido, criado="2026-01-01T00:01:00Z")])
        self.assertSai(self.sha(), 4, "ainda não sei")


class Redisparo(Base):
    def falho(self, **extra):
        self.cenario([run(1, self.x, conclusion="failure")], [run(1, self.x, conclusion="failure"), run(2, self.x, event="workflow_dispatch", criado="2026-01-01T00:01:00Z")], passo="Verify SSH", **extra)

    def test_passo_passageiro_na_ponta_repete_uma_vez(self):
        self.falho()
        res = self.sha("--transitorios", "Trust host,Verify SSH")
        self.assertSai(res, 0, "repetindo o deploy", "✅ no ar — run 2")
        self.assertEqual(self.log().count("workflow run deploy.yml --ref main"), 1)
        self.assertTrue((self.r / (".git/deploy-do-sha/redisparado-" + self.x)).is_file())

    def test_slots_preenchem_workflow_passos_e_branch(self):
        self.escreve(self.r, "sdd/config.yaml", 'project:\n  default_branch: main\ndeploy:\n  workflow: "deploy.yml"\n  transient_steps: "Verify SSH"\n')
        self.falho()
        res = self.roda([BASH, SCRIPT, "--commit", self.x, "--intervalo", "0", "--teto", "1"], self.r)
        self.assertSai(res, 0, "✅ no ar — run 2")

    def test_marca_de_outra_chamada_espera_e_nao_repete(self):
        marca = self.r / (".git/deploy-do-sha/redisparado-" + self.x)
        marca.parent.mkdir()
        marca.write_text("x\n", encoding="utf-8")
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH")
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 4, "o run novo não apareceu")
        self.assertNotIn("workflow run", self.log())

    def test_corrida_sem_o_run_novo_sai_4_nunca_2(self):
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH")
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 4, "isso não é falha")
        self.assertEqual(self.log().count("workflow run"), 1)

    def test_nao_repete(self):
        y = self.novo_commit()
        casos = (
            ("passo fora da lista", dict(passo="Compilar"), ("--transitorios", "Verify SSH"), self.x, [run(1, y, conclusion="failure")], "não está em deploy.transient_steps"),
            ("lista vazia", dict(passo="Verify SSH"), (), self.x, [run(1, y, conclusion="failure")], "deploy.transient_steps está vazio"),
        )
        for nome, extra, flags, _c, runs, frase in casos:
            with self.subTest(nome):
                (self.dir_gh / "pos").write_text("0")
                self.cenario(runs, **extra)
                self.assertSai(self.sha(*flags, commit=y), 2, "🔴 falhou — run 1", frase)
                self.assertNotIn("workflow run", self.log())

    def test_nao_e_mais_a_ponta(self):
        y = self.novo_commit()
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH")
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 2, "não é mais a ponta", y[:7])
        self.assertNotIn("workflow run", self.log())

    def test_fetch_que_falha_nao_repete(self):
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH")
        self.git(self.r, "remote", "set-url", "origin", str(self.tmp / "sumiu.git"))
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 2, "git fetch falhou")
        self.assertNotIn("workflow run", self.log())

    def test_ja_repetido_por_workflow_dispatch(self):
        self.cenario([run(1, self.x, conclusion="failure"), run(2, self.x, conclusion="failure", event="workflow_dispatch", criado="2026-01-01T00:01:00Z")], passo="Verify SSH")
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 2, "já foi repetido 1 vez")
        self.assertNotIn("workflow run", self.log())

    def test_deploy_mais_novo_nao_repete(self):
        self.git(self.r, "checkout", "-q", "-b", "outra", "HEAD")
        self.escreve(self.r, "b.txt", "x\n")
        self.commit(self.r)
        outro = self.git(self.r, "rev-parse", "HEAD").strip()
        self.git(self.r, "checkout", "-q", "main")
        y = self.novo_commit()
        self.cenario([run(1, y, conclusion="failure"), run(2, outro, status="in_progress", conclusion=None, criado="2026-01-01T00:01:00Z")], passo="Verify SSH")
        self.assertSai(self.sha("--transitorios", "Verify SSH", commit=y), 2, "já existe deploy mais novo")
        self.assertNotIn("workflow run", self.log())

    def test_dispatch_recusado_diz_o_caminho(self):
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH", dispatch_recusado=True)
        self.assertSai(self.sha("--transitorios", "Verify SSH"), 2, "workflow_dispatch", "push novo")

    def test_teto_que_ja_passou_nao_repete(self):
        self.cenario([run(1, self.x, conclusion="failure")], passo="Verify SSH")
        rc, out, err = self.roda([BASH, SCRIPT, "--commit", self.x, "--workflow", "deploy.yml", "--teto", "0", "--transitorios", "Verify SSH"], self.r)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("o teto de 0 min já passou", out)
        self.assertNotIn("workflow run", self.log())


class AindaNaoSei(Base):
    def test_sem_run_nunca_diz_que_nao_ha_o_que_verificar(self):
        self.cenario([])
        rc, out, err = self.sha()
        self.assertEqual(rc, 4, out + err)
        self.assertIn("não achei nenhum run", out)
        self.assertIn("isso não diz que não há o que verificar", out)

    def test_teto_com_run_em_andamento_nao_e_falha(self):
        self.cenario([run(7, self.x, status="in_progress", conclusion=None)])
        rc, out, err = self.roda([BASH, SCRIPT, "--commit", self.x, "--workflow", "deploy.yml", "--teto", "0"], self.r)
        self.assertEqual(rc, 4, out + err)
        self.assertIn("run 7", out)
        self.assertIn("isso não é falha", out)

    def test_consulta_falhando_cita_o_erro_no_teto(self):
        self.cenario([], erro="HTTP 500: deu ruim")
        rc, out, err = self.roda([BASH, SCRIPT, "--commit", self.x, "--workflow", "deploy.yml", "--teto", "0"], self.r)
        self.assertEqual(rc, 4, out + err)
        self.assertIn("HTTP 500", out)


class Ausentes(Base):
    def test_sem_gh_e_sem_git_sai_3(self):
        so = self.tmp / "so"
        so.mkdir()
        os.symlink(sys.executable, str(so / "python3"))
        os.symlink(shutil.which("git"), str(so / "git"))
        rc, out, err = self.sha(env=dict(self.env, PATH=str(so)))
        self.assertEqual(rc, 3, out + err)
        self.assertIn("gh não está instalado", out)
        self.assertIn("RESULTADO: INCONCLUSIVO", out)

    def test_gh_sem_login_sai_3(self):
        self.cenario([], erro="To get started with GitHub CLI, please run: gh auth login")
        rc, out, err = self.sha()
        self.assertEqual(rc, 3, out + err)
        self.assertIn("inconclusivo", out)


class Uso(Base):
    def test_sai_64(self):
        self.cenario([])
        for args in ((), ("--commit",), ("--commit", self.x), ("--commit", "nao-existe", "--workflow", "w"), ("--commit", self.x, "--workflow", "w", "--teto", "x"),
                     ("--commit", self.x, "--workflow", "w", "--intervalo", "-1"), ("--commit", self.x, "--workflow", "w", "--xyz", "1"),
                     ("--commit", self.x, "--workflow", "w", "--repo", "nao/existe")):
            with self.subTest(args=args):
                rc, out, err = self.roda([BASH, SCRIPT, *args], self.r)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)
                self.assertEqual(self.log(), "")

    def test_branch_do_origin_head_sem_slot(self):
        self.git(self.r, "branch", "-m", "main", "tronco")
        self.git(self.r, "push", "-q", "origin", "tronco")
        self.git(self.r, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/tronco")
        self.cenario([run(1, self.x, branch="tronco")])
        rc, out, err = self.roda([BASH, SCRIPT, "--commit", self.x, "--workflow", "w.yml", "--intervalo", "0", "--teto", "1"], self.r)
        self.assertEqual(rc, 0, out + err)
