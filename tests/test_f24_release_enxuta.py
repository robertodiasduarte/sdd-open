"""F24 — release enxuta (DEFINE F24 AT-001 a AT-011): a release só colhe e põe na fila, um commit de papel coberto
pelo OK, uma parada só depois do OK, ficha por acréscimo, trilha curta por comando e a explicação ao aluno.

Os scripts rodam de verdade, por subprocess, em repositórios montados no teste; o texto das skills é conferido como
contrato escrito (as regras estão lá), não como obediência do agente.
"""
from __future__ import annotations

import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from apoio import BASH, PYTHON, RAIZ, Sandbox

CURATOR = RAIZ / "sdd/bin/playbook-curator.sh"
TRILHA = RAIZ / "sdd/bin/trilha.sh"
FICHA = RAIZ / "sdd/bin/ficha-publicado.py"
LINT_FICHA = RAIZ / "sdd/bin/handoff-lint.py"
PAPEL = RAIZ / ".agents/skills/sdd-release/scripts/push-de-papel.py"
FX_CUR = RAIZ / "sdd/fixtures/playbook/curadoria"
FX = RAIZ / "sdd/fixtures/f24"
RELEASE = (RAIZ / ".agents/skills/sdd-release/SKILL.md").read_text(encoding="utf-8")
COMO_FALAR = (RAIZ / ".agents/skills/sdd-release/references/como-falar.md").read_text(encoding="utf-8")
LOTE = (RAIZ / ".agents/skills/sdd-playbook/references/lote.md").read_text(encoding="utf-8")
HANDOFF = (RAIZ / ".agents/skills/sdd-handoff/SKILL.md").read_text(encoding="utf-8")
POS_PUSH = RELEASE[RELEASE.index('## FASE 2 — Após o "go"'):RELEASE.index("## Gates de ABORTAR")]
RE_FP = re.compile(r"\bfp=([0-9a-f,]+)")


def fps(texto: str) -> list:
    out = []
    for ln in texto.split("\n"):
        if ln.startswith(("DELTA ", "SUGESTAO ", "CANDIDATO #", "REJEITADO ")):
            for m in RE_FP.finditer(ln):
                out += m.group(1).split(",")
    return out


class Projeto(Sandbox):
    """Um projeto git com o playbook da fixture e os documentos de uma feature."""

    def setUp(self):
        super().setUp()
        self.env = dict(self.env, TMPDIR=str(self.tmp), SDD_TRACE="off")
        self.r = self.repo("p")

    def feature(self, f, ignora_evidencia=False):
        r = self.r
        (r / "sdd/features").mkdir(parents=True, exist_ok=True)
        if not (r / "sdd/playbook.md").exists():
            shutil.copyfile(FX_CUR / "playbook-base.md", r / "sdd/playbook.md")
        shutil.copyfile(FX_CUR / "DESIGN_FIXTURE.md", r / ("sdd/features/DESIGN_%s.md" % f))
        (r / "sdd/reports/evidence" / f).mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FX_CUR / "BUILD_REPORT_FIXTURE.md", r / ("sdd/reports/BUILD_REPORT_%s.md" % f))
        shutil.copyfile(FX_CUR / "AVAL-AT-002.log", r / "sdd/reports/evidence" / f / "AVAL-AT-002.log")
        if ignora_evidencia:
            self.escreve(r, ".gitignore", "sdd/reports/evidence/\n")
        self.commit(r, "docs " + f)

    def cur(self, *args):
        return self.roda([BASH, CURATOR, *args], self.r)

    def entradas(self, f):
        p = self.r / "sdd/curadoria/fila" / f
        return sorted(p.iterdir()) if p.is_dir() else []


class AT001_SoColhe(Projeto):
    def test_enfileirar_grava_a_entrada_e_nao_mexe_no_playbook(self):
        self.feature("FA")
        antes = (self.r / "sdd/playbook.md").read_bytes()
        rc, out, err = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: ENFILEIRADO", out)
        [e] = self.entradas("FA")
        self.assertRegex(e.name, r"^\d{8}T\d{6}Z$")
        for nome in ("colheita.txt", "colheita.rc", "DESIGN_FA.md", "BUILD_REPORT_FA.md", "AVAL-AT-002.log"):
            with self.subTest(nome=nome):
                self.assertTrue((e / nome).is_file())
        self.assertEqual((e / "colheita.rc").read_text(encoding="utf-8").strip(), "0")
        self.assertIn("DELTA LM-020 ajudou+1", (e / "colheita.txt").read_text(encoding="utf-8"))
        self.assertEqual((self.r / "sdd/playbook.md").read_bytes(), antes)
        self.assertFalse((self.r / "sdd/releases/FA/CURATOR-colhidos.txt").exists())

    def test_colheita_que_falha_fica_na_fila_marcada_e_nunca_e_zero_deltas(self):
        self.feature("FA")
        rc, out, err = self.cur("--enfileirar", "FA", "sdd/nao-existe.md")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("COLHEITA FALHOU", out)
        self.assertIn('"Curadoria: FALHOU (rc=2)"', out)
        self.assertNotIn('registre "Curadoria: 0 deltas', out)
        self.assertIn('isto não é "0 deltas"', out)
        [e] = self.entradas("FA")
        self.assertEqual((e / "colheita.rc").read_text(encoding="utf-8").strip(), "2")
        # uma colheita boa depois substitui a falha
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("removida a entrada que falhou", out)
        [e2] = self.entradas("FA")
        self.assertEqual((e2 / "colheita.rc").read_text(encoding="utf-8").strip(), "0")

    def test_sem_documentos_e_nada_a_colher_nao_gravam_entrada(self):
        self.escreve(self.r, "sdd/playbook.md", (FX_CUR / "playbook-base.md").read_text(encoding="utf-8"))
        self.commit(self.r)
        rc, out, _ = self.cur("--enfileirar", "FIX1", "sdd/playbook.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("STAGING SEM DOCUMENTOS", out)
        self.assertIn("0 deltas (sem documentos)", out)
        self.assertEqual(self.entradas("FIX1"), [])

    def test_a_release_so_colhe(self):
        item13 = RELEASE[RELEASE.index("13. **Colheita.**"):RELEASE.index("14. **Ficha.**")]
        self.assertIn("playbook-curator.sh --enfileirar {F}", item13)
        for proibido in ("despachar curador", "--conferir-bloco", "playbook-curator.sh --aplicar", "BRIEF_curador", "[D3"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, POS_PUSH)
        self.assertNotIn("17b", RELEASE)


class AT002_UmaVezSo(Projeto):
    def test_duas_publicacoes_sem_lote_nao_contam_duas_vezes(self):
        self.feature("FA")
        self.assertEqual(self.cur("--enfileirar", "FA", "sdd/playbook.md")[0], 0)
        # 2ª publicação da mesma feature: a mesma DESIGN mais uma lição nova tratada
        d = self.r / "sdd/features/DESIGN_FA.md"
        d.write_text(d.read_text(encoding="utf-8").replace(
            "| Nota sem ID |", "| Outra | `LM-016` | ✔ tratado | nova linha da 2ª publicação |\n| Nota sem ID |"), encoding="utf-8")
        self.commit(self.r, "s2")
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        e1, e2 = self.entradas("FA")
        c1 = (e1 / "colheita.txt").read_text(encoding="utf-8")
        c2 = (e2 / "colheita.txt").read_text(encoding="utf-8")
        self.assertIn("DELTA LM-016 ajudou+1", c2)
        self.assertNotIn("DELTA LM-020 ajudou+1", c2, "a linha da 1ª publicação, ainda na fila, voltou")
        self.assertRegex(c2, r"(?m)^JA_JULGADO \d+ linha")
        todas = fps(c1) + fps(c2)
        self.assertEqual(len(todas), len(set(todas)), "impressão repetida entre entradas da fila")
        self.commit(self.r, "papel")
        rc, out, _ = self.cur("--registrar", str(e1), str(e2))
        self.assertEqual(rc, 0, out)
        reg = (self.r / "sdd/releases/FA/CURATOR-colhidos.txt").read_text(encoding="utf-8")
        registradas = [x for m in RE_FP.finditer(reg) for x in m.group(1).split(",")]
        self.assertEqual(sorted(registradas), sorted(set(todas)))  # cada impressão uma vez só
        self.assertEqual(self.entradas("FA"), [])
        self.commit(self.r, "lote")
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("NADA A COLHER", out)


class AT003_Lote(Projeto):
    def test_dois_candidatos_de_entradas_diferentes_saem_com_ids_seguidos(self):
        self.feature("FA")
        self.feature("FB")
        for f in ("FA", "FB"):
            self.assertEqual(self.cur("--enfileirar", f, "sdd/playbook.md")[0], 0)
        self.commit(self.r, "papel")
        adds = []
        for f in ("FA", "FB"):
            [e] = self.entradas(f)
            rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
            self.assertEqual(rc, 0, out + err)
            stg = Path(re.search(r"(?m)^staging: (.+)$", out).group(1))
            colheita = (stg / "colheita.txt").read_text(encoding="utf-8")
            self.assertRegex(colheita, r"(?m)^CANDIDATO #1 → LM-023 ")  # as duas propõem o mesmo número
            adds += [ln.strip()[len("delta: "):] for ln in colheita.split("\n") if ln.strip().startswith("delta: ADD ")]
        self.assertGreaterEqual(len(adds), 2)
        delta = self.escreve(self.tmp, "lote-delta.txt", "\n".join(adds) + "\n")
        rc, novo, err = self.roda([BASH, CURATOR, "--aplicar", delta, "sdd/playbook.md"], self.r)
        self.assertEqual(rc, 0, err)
        ids = re.findall(r"(?m)^- \[(LM-\d{3})\] ajudou=0 mordeu=0 · conf=", novo)
        novos = sorted(i for i in ids if int(i[3:]) >= 23)
        self.assertEqual(novos, ["LM-%03d" % n for n in range(23, 23 + len(adds))])  # seguidos, sem repetir o LM-023

    def test_o_lote_tem_as_garantias(self):
        corrido = " ".join(LOTE.split())
        for trecho in ("--conferir-entrada", "--conferir-bloco", "governanca-fronteira.sh --snapshot", "--selar",
                       "[D3 · muda a regra do método]", "um `--aplicar` só", "--registrar", "Nunca separe contagem de regra à mão"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, corrido)


class AT004_FalhaPorEntradaEPorLinha(Projeto):
    def test_log_que_o_projeto_nao_versiona_e_relatado_e_nao_segura_a_entrada(self):
        self.feature("FA", ignora_evidencia=True)
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        [e] = self.entradas("FA")
        self.assertFalse((e / "AVAL-AT-002.log").exists(), "log ignorado pelo projeto foi para a fila")
        aus = (e / "ausentes.txt").read_text(encoding="utf-8")
        self.assertIn("arquivo: AVAL-AT-002.log", aus)
        self.assertRegex(aus, r"fp=[0-9a-f]{10}")
        self.commit(self.r, "papel")
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("evidência ausente:", out)
        stg = Path(re.search(r"(?m)^staging: (.+)$", out).group(1))
        refeita = (stg / "colheita.txt").read_text(encoding="utf-8")
        # a contagem que só o log provava não vai ao curador (o candidato pode citar o log no texto dele: aí o curador
        # não acha o arquivo e não aceita, como qualquer evidência que não abre)
        self.assertNotRegex(refeita, r"(?m)^DELTA .*evidencia=AVAL-AT-002\.log:")
        self.assertIn("DELTA LM-020 ajudou+1", refeita)          # o resto da entrada segue

    def test_bloco_reprovado_e_envio(self):
        corrido = " ".join(LOTE.split())
        for trecho in ("2ª reprovação ⇒ registre `Curadoria: FALHOU (bloco inválido)` para esta entrada: **nada dela é aplicado**, ela fica na fila",
                       "**não redespache**", "[D1 · não se desfaz]", "push-de-papel.py",
                       "Entrada recusada ou com bloco reprovado 2 vezes **não** entra: ela fica na fila"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, corrido)


class AT005_LimiteDaFila(Projeto):
    def povoa(self, n):
        for k in range(n):
            e = self.r / "sdd/curadoria/fila" / ("F%d" % k) / ("20261116T1000%02dZ" % k)
            e.mkdir(parents=True)
            (e / "colheita.rc").write_text("0\n", encoding="utf-8")
            (e / "colheita.txt").write_text("DELTA LM-020 ajudou+1 · conf=2026-11-16 · evidencia=D.md:1 · fp=%010x\n" % k,
                                            encoding="utf-8")

    def test_ate_5_nao_diz_nada(self):
        self.povoa(5)
        rc, out, _ = self.cur("--fila")
        self.assertEqual(rc, 0, out)
        self.assertIn("FILA: 5 entrada(s)", out)
        self.assertNotIn("🧹", out)

    def test_6_diz_uma_linha_e_sai_10(self):
        self.povoa(6)
        rc, out, _ = self.cur("--fila")
        self.assertEqual(rc, 10, out)
        self.assertEqual(len([ln for ln in out.split("\n") if ln.startswith("🧹")]), 1)
        self.assertIn("sem perguntar e sem rodar o lote", out)

    def test_a_release_so_avisa(self):
        item13 = RELEASE[RELEASE.index("13. **Colheita.**"):RELEASE.index("14. **Ficha.**")]
        self.assertIn("--fila", item13)
        self.assertIn("sem perguntar e sem rodar o lote; nada roda sozinho", " ".join(item13.split()))


class AT006_CommitDePapel(Sandbox):
    ARQS = ("sdd/handoffs/HANDOFF_X.md", "CHANGELOG.md", "sdd/curadoria/fila/X/a/colheita.txt", "sdd/archive/X/DESIGN_X.md")

    def papel(self, workflow):
        p = Path(tempfile.mkdtemp(dir=str(self.tmp)))
        (p / ".github/workflows").mkdir(parents=True)
        shutil.copyfile(FX / "workflows" / (workflow + ".yml"), p / ".github/workflows" / (workflow + ".yml"))
        return self.roda([PYTHON, PAPEL, p, "--branch", "main", *self.ARQS], self.tmp)

    def test_matriz(self):
        casos = {"sem-filtro": (0, "PUBLICA"), "com-paths-ignore": (1, "NAO_PUBLICA"), "so-src": (1, "NAO_PUBLICA"),
                 "outra-branch": (1, "NAO_PUBLICA"), "so-testes": (1, "NAO_PUBLICA"), "workflow-run": (2, "NAO_SEI"),
                 "ilegivel": (2, "NAO_SEI")}
        for wf, (rc_esp, res) in casos.items():
            with self.subTest(workflow=wf):
                rc, out, err = self.papel(wf)
                self.assertEqual(rc, rc_esp, out + err)
                self.assertIn("RESULTADO: " + res + "\n", out)
        rc, out, _ = self.papel("sem-filtro")
        self.assertIn("paths-ignore: ['sdd/**', '**/*.md']", out)

    def test_sem_o_vizinho_e_uso_nunca_nao_publica(self):
        sozinho = self.tmp / "s"
        sozinho.mkdir()
        shutil.copyfile(PAPEL, sozinho / "push-de-papel.py")
        rc, out, err = self.roda([PYTHON, sozinho / "push-de-papel.py", self.tmp, "--branch", "main", "x.md"], self.tmp)
        self.assertEqual(rc, 64, out + err)
        self.assertNotIn("NAO_PUBLICA", out)

    def test_o_ok_diz_e_o_papel_sobe_sem_pergunta(self):
        bloco = RELEASE[RELEASE.index("7. **PARAR e mostrar"):RELEASE.index('## FASE 2')]
        self.assertIn("**O commit de papel publica?**", bloco)
        self.assertIn("**Posso finalizar (push + deploy + verificar + papel)?**", bloco)
        self.assertIn("push-de-papel.py", bloco)
        item16 = " ".join(RELEASE[RELEASE.index("16. **Commit de papel.**"):RELEASE.index("17. **Branch da frente.**")].split())
        for trecho in ("Um commit só", "**sem nova pergunta**", "`git diff --cached --name-only`", "Nunca `--no-verify`", "sem `--force`"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, item16)
        self.assertIn("a pendência ✨ de tirar os documentos do gatilho do deploy", " ".join(POS_PUSH.split()))


class AT007_UmaParadaSo(unittest.TestCase):
    def test_uma_pergunta_depois_do_ok(self):
        marcas = re.findall(r"\[D\d", POS_PUSH)
        self.assertEqual(marcas, ["[D1"], "depois do OK só pode haver a pergunta do smoke vermelho")
        self.assertIn("`2` ⇒ pare e pergunte `[D1 · não se desfaz]`", POS_PUSH)
        for oferta in ("oferecer", "Oferecer", "ofereça", "quer que eu", "Prompt da próxima sessão", "com 1 OK"):
            with self.subTest(oferta=oferta):
                self.assertNotIn(oferta, POS_PUSH.replace("não ofereça outro", ""))
        self.assertIn("não ofereça outro", POS_PUSH)  # o prompt de retomada já está na ficha

    def test_branch_remota_so_se_ancestral_e_com_recibo(self):
        item = " ".join(RELEASE[RELEASE.index("17. **Branch da frente.**"):RELEASE.index("## FASE 4")].split())
        for trecho in ("git cherry", "git push origin --delete <branch>", "git push origin <sha>:refs/heads/<branch>",
                       "não apague e diga por quê", "git worktree remove"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, item)

    def test_arquivamento_pelo_ledger_e_recibo(self):
        item = " ".join(RELEASE[RELEASE.index("15. **Arquivamento.**"):RELEASE.index("16. **Commit de papel.**")].split())
        self.assertIn("`estado: shipado`", item)
        self.assertIn("um a um", item)
        rel = " ".join(RELEASE[RELEASE.index("18. **Relatório final.**"):RELEASE.index("## Gates de ABORTAR")].split())
        self.assertIn("**Decidi sozinho**", rel)
        self.assertIn("com o comando que desfaz", rel)


class AT008_FichaPorAcrescimo(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo("p")
        rel = self.r / "sdd/releases/PEDIDOS"
        rel.mkdir(parents=True)
        for f in FX.joinpath("ledgers").iterdir():
            shutil.copyfile(f, rel / f.name)
        self.commit(self.r, "ledgers")
        self.ficha = self.escreve(self.r, "sdd/handoffs/HANDOFF_PEDIDOS.md",
                                  "# HANDOFF: PEDIDOS\n\n## Ficha\n\n| a | b |\n\n## Feito\n\n- texto da pessoa\n\n## Falta\n\n- algo\n")

    def gera(self):
        return self.roda([PYTHON, FICHA, "PEDIDOS"], self.r)

    def test_uma_linha_por_ledger_idempotente_e_resto_intacto(self):
        rc, out, err = self.gera()
        self.assertEqual(rc, 2, out + err)  # 1 ledger ilegível
        self.assertIn("LEDGER ILEGÍVEL", out)
        texto = self.ficha.read_text(encoding="utf-8")
        bloco = texto[texto.index("<!-- publicado:inicio"):texto.index("<!-- publicado:fim -->")]
        linhas = [ln for ln in bloco.split("\n") if ln.startswith("- ")]
        self.assertEqual(len(linhas), 3)
        self.assertRegex(linhas[0], r"^- 2026-11-12 · s2 · 1\.1\.0 · shipado · CONCERNS · deploy real · trilha curta · [0-9a-f]{7,12}$")
        self.assertRegex(linhas[1], r"^- 2026-11-10 · s1 · 1\.0\.0 · parcial · PASS · deploy real · trilha completa · [0-9a-f]{7,12}$")
        self.assertEqual(linhas[2], "- n/d (ledger ilegível: sdd/releases/PEDIDOS/s3_quebrado.yaml)")
        for resto in ("## Feito\n\n- texto da pessoa", "## Falta\n\n- algo"):
            self.assertIn(resto, texto)
        antes = self.ficha.read_bytes()
        self.gera()
        self.assertEqual(self.ficha.read_bytes(), antes)

    def test_sem_ledger_nao_grava(self):
        rc, out, _ = self.roda([PYTHON, FICHA, "OUTRA"], self.r)
        self.assertEqual(rc, 1, out)
        self.assertFalse((self.r / "sdd/handoffs/HANDOFF_OUTRA.md").exists())

    def test_o_agente_escreve_so_o_que_o_ledger_nao_diz(self):
        self.assertIn("você escreve **só**", " ".join(HANDOFF.split()))
        item14 = " ".join(RELEASE[RELEASE.index("14. **Ficha.**"):RELEASE.index("15. **Arquivamento.**")].split())
        self.assertIn("ficha-publicado.py {F}", item14)
        self.assertIn("Nada do que está no bloco Publicado se repete", item14)
        rel = " ".join(RELEASE[RELEASE.index("18. **Relatório final.**"):RELEASE.index("## Gates de ABORTAR")].split())
        self.assertIn("a ficha **pelo caminho**, sem imprimi-la", rel)
        self.assertIn("O resumo de etapa do encerramento não repete essas linhas", rel)
        self.assertNotIn("Imprimir a ficha", RELEASE)


class AT009_Trilha(Sandbox):
    def montar(self, nome, arquivos, define=None, commit=True):
        r = self.repo(nome)
        self.escreve(r, "README.md", "base\n")
        self.commit(r, "base")
        self.git(r, "branch", "-M", "main")
        self.git(r, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.git(r, "checkout", "-q", "-b", "feat")
        for rel, conteudo in arquivos.items():
            p = r / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            (p.write_bytes if isinstance(conteudo, bytes) else lambda c: p.write_text(c, encoding="utf-8"))(conteudo)
        if define:
            self.escreve(r, define, "# DEFINE\n")
        if commit:
            self.commit(r, "fix")
        return r

    def trilha(self, r):
        return self.roda([BASH, TRILHA, "X"], r)

    def test_matriz(self):
        linhas = lambda n: "".join("l%d\n" % k for k in range(n))
        casos = {
            "curta": ({"a.py": linhas(20), "b.py": linhas(20)}, None, True, 0, "curta"),
            "curta_sem_commit": ({"a.py": linhas(20), "b.py": linhas(20)}, None, False, 0, "curta"),
            "documentos_nao_contam": ({"a.py": linhas(10), "sdd/features/DESIGN_X.md": linhas(500), "CHANGELOG.md": linhas(50)},
                                      None, True, 0, "curta"),
            "com_define": ({"a.py": linhas(5)}, "sdd/features/DEFINE_X.md", True, 1, "tem DEFINE"),
            "define_arquivado": ({"a.py": linhas(5)}, "sdd/archive/X/DEFINE_X.md", True, 1, "tem DEFINE"),
            "4_arquivos": ({"a.py": "1\n", "b.py": "1\n", "c.py": "1\n", "d.py": "1\n"}, None, True, 1, "4 arquivos"),
            "101_linhas": ({"a.py": linhas(101)}, None, True, 1, "101 linhas"),
            "binario": ({"a.bin": b"\x00\x01\x02binario"}, None, True, 1, "binário"),
        }
        for nome, (arqs, define, commit, rc_esp, trecho) in casos.items():
            with self.subTest(caso=nome):
                r = self.montar(nome, arqs, define, commit)
                rc, out, err = self.trilha(r)
                self.assertEqual(rc, rc_esp, out + err)
                self.assertIn(trecho, out)

    def test_ficha_curta(self):
        ok = self.roda([PYTHON, LINT_FICHA, "--curta", FX / "ficha-curta.md"], self.tmp)
        self.assertEqual(ok[0], 0, ok[1] + ok[2])
        longa = self.roda([PYTHON, LINT_FICHA, "--curta", FX / "ficha-curta-longa.md"], self.tmp)
        self.assertEqual(longa[0], 1)
        self.assertIn("ficha curta com 21 linhas", longa[2])
        # sem --curta, a mesma ficha passa: o limite é só da trilha curta
        self.assertEqual(self.roda([PYTHON, LINT_FICHA, FX / "ficha-curta-longa.md"], self.tmp)[0], 0)

    def test_a_skill_decide_por_comando_e_as_fases_0_a_2_nao_mudam(self):
        quando = " ".join(RELEASE[RELEASE.index("## Quando pular o SDD formal"):RELEASE.index("## Por que cada regra existe")].split())
        self.assertIn("As FASES 0 a 2 valem **sempre**, nas duas trilhas", quando)
        self.assertIn("nunca o agente", quando)
        self.assertNotIn("0–20", RELEASE)
        self.assertIn("bash sdd/bin/trilha.sh {F}", RELEASE[:RELEASE.index("**0a. Determinístico**")])


class AT010_EntradaAlterada(Projeto):
    def enfileira(self):
        self.feature("FA")
        self.assertEqual(self.cur("--enfileirar", "FA", "sdd/playbook.md")[0], 0)
        self.commit(self.r, "papel")
        [e] = self.entradas("FA")
        return e

    def test_linha_plantada(self):
        e = self.enfileira()
        with open(e / "colheita.txt", "a", encoding="utf-8") as f:
            f.write("DELTA LM-016 mordeu+1 · conf=2026-11-16 · evidencia=DESIGN_FA.md:3 · fp=abcdef0123\n")
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("ENTRADA RECUSADA", out)
        self.assertIn("colheita alterada depois da publicação", err)

    def test_pasta_mexida_por_outro_commit(self):
        e = self.enfileira()
        with open(e / "DESIGN_FA.md", "a", encoding="utf-8") as f:
            f.write("\n")
        self.commit(self.r, "mexe")
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("mudou depois do commit que a criou", err)

    def test_entrada_fabricada_num_commit_so(self):
        self.feature("FA")
        e = self.r / "sdd/curadoria/fila/FA/20261116T120000Z"
        e.mkdir(parents=True)
        falso = (FX_CUR / "DESIGN_FIXTURE.md").read_text(encoding="utf-8").replace(
            "| Nota sem ID |", "| Forjada | `LM-016` | ✔ tratado | nunca esteve no repositório |\n| Nota sem ID |")
        (e / "DESIGN_FA.md").write_text(falso, encoding="utf-8")
        rc_c, colheita, _ = self.roda([BASH, CURATOR, "--colher", e, "sdd/playbook.md"], self.r)
        self.assertEqual(rc_c, 0)
        (e / "colheita.txt").write_text(colheita, encoding="utf-8")
        (e / "colheita.rc").write_text("0\n", encoding="utf-8")
        self.commit(self.r, "entrada fabricada")
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("nunca esteve", err)

    def test_entrada_integra_passa(self):
        e = self.enfileira()
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("ENTRADA CONFERIDA", out)


class AT011_DepoisDoPush(unittest.TestCase):
    @staticmethod
    def etapas_da_skill():
        nomes = []
        for m in re.finditer(r"(?m)^\d+b?\. \*\*([^*]+)\*\*", POS_PUSH):
            nomes.append(re.split(r"[:.]| —", m.group(1))[0].strip())
        return nomes

    @staticmethod
    def linhas_da_tabela():
        sec = COMO_FALAR[COMO_FALAR.index("## Depois do push — o que é cada etapa"):]
        sec = sec[:sec.index("\n## ", 5)] if "\n## " in sec[5:] else sec
        out = {}
        for ln in sec.split("\n"):
            if ln.startswith("| **"):
                cel = [c.strip() for c in ln.strip().strip("|").split("|")]
                out[cel[0].strip("*")] = cel
        return out

    def test_controle_da_extracao(self):
        self.assertGreaterEqual(len(self.etapas_da_skill()), 10)
        self.assertIn("Verificar", self.etapas_da_skill())

    def test_toda_etapa_tem_linha_e_toda_linha_tem_etapa(self):
        etapas, tabela = self.etapas_da_skill(), self.linhas_da_tabela()
        self.assertEqual(sorted(etapas), sorted(tabela), "skill e tabela 'Depois do push' divergiram")

    def test_cada_linha_tem_as_4_colunas_sem_numero_de_passo(self):
        for nome, cel in self.linhas_da_tabela().items():
            with self.subTest(etapa=nome):
                self.assertEqual(len(cel), 4)
                for c in cel[1:]:
                    self.assertTrue(c and c not in ("—", "-"), c)
                    self.assertIsNone(re.search(r"passo \d|item \d|\b\d+[a-z]?\.(?!\d)", c), c)

    def test_a_skill_manda_uma_frase_por_etapa(self):
        corrido = " ".join(POS_PUSH.split())
        self.assertIn("**uma frase por etapa**", corrido)
        self.assertIn('só quando ela pedir ou responder "não sei"', corrido)
        self.assertIn("sem número de passo", corrido)


class Revisao1(Projeto):
    """Rodada 1 da revisão do código (EXTERNAL_REVIEW_20261116-193502): um teste por achado aplicado, vermelho em 45bf1fe."""

    def test_r2_claude_log_sem_commit_vai_para_ausentes_e_nao_recusa_a_entrada(self):
        self.feature("FA")
        self.escreve(self.r, "sdd/reports/evidence/FA/AVAL-AT-009.log", "❌ AT-009 falhou: LM-016 mordeu de novo\n")
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        [e] = self.entradas("FA")
        self.assertFalse((e / "AVAL-AT-009.log").exists())
        self.assertIn("arquivo: AVAL-AT-009.log", (e / "ausentes.txt").read_text(encoding="utf-8"))
        self.git(self.r, "add", "--", "sdd/curadoria")
        self.git(self.r, "commit", "-q", "-m", "papel")
        rc, out, err = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        self.assertEqual(rc, 0, out + err)

    def test_r3_claude_retomar_nao_refaz_o_staging(self):
        self.feature("FA")
        self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.commit(self.r, "papel")
        [e] = self.entradas("FA")
        rc, out, _ = self.cur("--conferir-entrada", str(e), "sdd/playbook.md")
        stg = Path(re.search(r"(?m)^staging: (.+)$", out).group(1))
        (stg / "escrito-pelo-curador.txt").write_text("x", encoding="utf-8")
        rc, out, _ = self.cur("--conferir-entrada", str(e), "sdd/playbook.md", "--retomar")
        self.assertEqual(rc, 0, out)
        self.assertIn("RETOMADA", out)
        self.assertTrue((stg / "escrito-pelo-curador.txt").exists(), "a retomada apagou o que o curador escreveu")

    def test_r1_claude_mesma_impressao_em_duas_entradas_conta_na_mais_antiga(self):
        self.feature("FA")
        self.cur("--enfileirar", "FA", "sdd/playbook.md")
        [a] = self.entradas("FA")
        b = a.parent / "20991231T235959Z"  # a mesma colheita numa 2ª entrada (publicação em pasta paralela)
        shutil.copytree(a, b)
        self.commit(self.r, "papel")
        rc, out, err = self.cur("--conferir-entrada", str(b), "sdd/playbook.md")
        stg = Path(re.search(r"(?m)^staging: (.+)$", out).group(1))
        self.assertEqual(fps((stg / "colheita.txt").read_text(encoding="utf-8")), [])
        self.assertEqual(rc, 1, out + err)
        self.assertIn("NADA A JULGAR", out)


class Revisao1Sandbox(Sandbox):
    def test_r6_codex_aspas_sem_fechar_e_ledger_ilegivel(self):
        r = self.repo("p")
        self.escreve(r, "sdd/releases/X/s1.yaml", 'feature_id: X\nslice_id: s1\ndata: "2026-11-16\nestado: shipado\n')
        rc, out, err = self.roda([PYTHON, FICHA, "X"], r)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("ledger ilegível: sdd/releases/X/s1.yaml", (r / "sdd/handoffs/HANDOFF_X.md").read_text(encoding="utf-8"))

    def test_r7_codex_arquivo_novo_acentuado_conta(self):
        r = self.repo("p")
        self.escreve(r, "README.md", "base\n")
        self.commit(r, "base")
        self.git(r, "branch", "-M", "main")
        self.git(r, "update-ref", "refs/remotes/origin/main", "HEAD")
        self.escreve(r, "conferência.py", "".join("l%d\n" % k for k in range(101)))
        rc, out, err = self.roda([BASH, TRILHA, "X"], r)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("101 linhas", out)

    def test_r4_claude_ficha_curta_aberta_com_prompt_passa(self):
        texto = (FX / "ficha-curta.md").read_text(encoding="utf-8").replace("✅ DoD fechado", "🚢 publicado")
        texto += "\n## Prompt de retomada\n\n```text\nRetomar a feature PEDIDOS_FIX.\nPasta: a do projeto.\nPróxima ação: nenhuma.\n```\n"
        f = self.escreve(self.tmp, "HANDOFF_PEDIDOS_FIX.md", texto)
        rc, out, err = self.roda([PYTHON, LINT_FICHA, "--curta", f], self.tmp)
        self.assertEqual(rc, 0, out + err)

    def test_r7_claude_o_papel_e_conferido_com_a_lista_real(self):
        item16 = " ".join(RELEASE[RELEASE.index("16. **Commit de papel.**"):RELEASE.index("17. **Branch da frente.**")].split())
        self.assertIn("Rode de novo o `push-de-papel.py` com a lista real", item16)
        self.assertIn("o commit **não** é enviado", item16)
        ok = " ".join(RELEASE[RELEASE.index("7. **PARAR e mostrar"):RELEASE.index("## FASE 2")].split())
        self.assertIn("com os nomes **reais** que o commit vai ter", ok)

    def test_r5_codex_escrita_do_curador_isola_a_entrada(self):
        corrido = " ".join(LOTE.split())
        self.assertIn("siga com a próxima entrada; esta fica na fila", corrido)
        self.assertIn("git checkout -- sdd/playbook.md sdd/invariants.md", corrido)


class Revisao2(Projeto):
    """Rodada 2 da revisão do código (EXTERNAL_REVIEW_20261116-202240): vermelhos em 22caf6b."""

    def test_r1_documento_sem_commit_avisa_e_nao_vira_julgado(self):
        self.feature("FA")
        d = self.r / "sdd/features/DESIGN_FA.md"
        d.write_text(d.read_text(encoding="utf-8") + "\n", encoding="utf-8")  # mudou depois do último commit
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ DESIGN_FA.md", out)
        [e] = self.entradas("FA")
        self.git(self.r, "add", "--", "sdd/curadoria")
        self.git(self.r, "commit", "-q", "-m", "papel")
        sem = set(RE_FP.search((e / "ausentes.txt").read_text(encoding="utf-8")).group(1).split(","))
        self.assertEqual(self.cur("--registrar", str(e))[0], 0)
        reg = self.r / "sdd/releases/FA/CURATOR-colhidos.txt"
        texto = reg.read_text(encoding="utf-8") if reg.exists() else ""
        registradas = set(x for m in RE_FP.finditer(texto) for x in m.group(1).split(","))
        self.assertFalse(sem & registradas, "linha sem evidência foi registrada como julgada")

    def test_r3_impressao_da_entrada_mais_antiga_nao_e_registrada_pela_nova(self):
        self.feature("FA")
        self.cur("--enfileirar", "FA", "sdd/playbook.md")
        [a] = self.entradas("FA")
        b = a.parent / "20991231T235959Z"
        shutil.copytree(a, b)
        self.commit(self.r, "papel")
        self.assertEqual(self.cur("--registrar", str(b))[0], 0)
        reg = (self.r / "sdd/releases/FA/CURATOR-colhidos.txt")
        texto = reg.read_text(encoding="utf-8") if reg.exists() else ""
        ja = set(x for m in RE_FP.finditer(texto) for x in m.group(1).split(","))
        self.assertFalse(set(fps((a / "colheita.txt").read_text(encoding="utf-8"))) & ja,
                         "a entrada nova registrou o que ainda espera julgamento na mais antiga")


class Revisao2Textos(unittest.TestCase):
    def test_r2_sem_documentos_na_trilha_completa_e_falha(self):
        item13 = " ".join(RELEASE[RELEASE.index("13. **Colheita.**"):RELEASE.index("14. **Ficha.**")].split())
        self.assertIn("na trilha completa, é falha", item13)

    def test_r4_brief_e_fronteira_por_entrada(self):
        self.assertIn("BRIEF_curador_<F>_<entrada>.md", LOTE)
        self.assertIn("/<F>/curador-<entrada>", LOTE)

    def test_n1_o_lote_comeca_com_o_playbook_limpo(self):
        corrido = " ".join(LOTE.split())
        self.assertIn("git diff --quiet -- sdd/playbook.md sdd/invariants.md", corrido)


class Revisao3(Projeto):
    """Rodada 3 da revisão do código (EXTERNAL_REVIEW_20261116-203629): vermelhos em 4b3f4b2."""

    def test_r1_entrada_recusada_nao_prende_as_impressoes(self):
        self.feature("FA")
        self.cur("--enfileirar", "FA", "sdd/playbook.md")
        [a] = self.entradas("FA")
        self.commit(self.r, "papel")
        rc, out, err = self.cur("--recusar", str(a), "bloco reprovado 2 vezes")
        self.assertEqual(rc, 0, out + err)
        self.assertTrue((a.parent / (a.name + ".recusada")).is_file())
        self.commit(self.r, "lote")
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)  # as linhas voltam numa entrada nova
        self.assertIn("removida a entrada recusada", out)
        [b] = self.entradas("FA")
        self.assertIn("DELTA LM-020 ajudou+1", (b / "colheita.txt").read_text(encoding="utf-8"))
        self.assertFalse((a.parent / (a.name + ".recusada")).exists())

    def test_r4_linha_sem_evidencia_volta_na_colheita_seguinte(self):
        self.feature("FA")
        d = self.r / "sdd/features/DESIGN_FA.md"
        d.write_text(d.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.commit(self.r, "agora com o DESIGN commitado")
        rc, out, _ = self.cur("--enfileirar", "FA", "sdd/playbook.md")
        self.assertEqual(rc, 0, out)
        e1, e2 = self.entradas("FA")
        self.assertIn("DELTA LM-020 ajudou+1", (e2 / "colheita.txt").read_text(encoding="utf-8"))


class Revisao3Textos(unittest.TestCase):
    def test_r5_branch_integrada_por_conteudo(self):
        item = " ".join(RELEASE[RELEASE.index("17. **Branch da frente.**"):RELEASE.index("## FASE 4")].split())
        self.assertIn("git cherry origin/{default_branch} origin/<branch>", item)

    def test_r3_contrato_do_curador_por_entrada(self):
        contratos = (RAIZ / "sdd/WORKFLOW_CONTRACTS.yaml").read_text(encoding="utf-8")
        bloco = contratos[contratos.index("\ncurador:"):]
        self.assertIn("BRIEF_curador_<F>_<entrada>.md", bloco)
        self.assertIn("/<F>/curador-<entrada>/", bloco)

    def test_lote_marca_a_recusa(self):
        self.assertIn("--recusar", LOTE)


if __name__ == "__main__":
    unittest.main()
