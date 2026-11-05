"""Contrato do sdd/bin/sdd-archive.py (DEFINE F14_DRIVE AT-028 a AT-030): simulação por padrão, git mv por lote, proteção
pela ficha. Repositório na sandbox, com datas de commit fixas e --hoje fixo."""
from __future__ import annotations

from apoio import PYTHON, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/sdd-archive.py"
ANTIGA = "2026-01-01T12:00:00"
HOJE = "2026-11-05"


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.escreve(self.r, "README.md", "x\n")
        self.commit(self.r)

    def doc(self, rel, data=ANTIGA):
        self.escreve(self.r, rel, "x\n")
        self.git(self.r, "add", rel)
        rc, out, err = self.roda(["git", "commit", "-q", "-m", "c"], self.r, dict(self.env, GIT_COMMITTER_DATE=data, GIT_AUTHOR_DATE=data))
        self.assertEqual(rc, 0, out + err)

    def arquivo(self, *args):
        return self.roda([PYTHON, "-B", SCRIPT, "--hoje", HOJE, *args], self.r)

    def ficha(self, feature, status):
        self.escreve(self.r, "sdd/handoffs/HANDOFF_%s.md" % feature, "# H\n\n## Ficha da feature\n\n| Campo | Valor |\n|---|---|\n| **Status** | %s |\n" % status)


class Simulacao(Base):
    def test_lista_por_lote_e_nao_muda_nada(self):
        self.doc("sdd/features/DEFINE_A.md")
        self.doc("sdd/reports/BUILD_REPORT_A.md")
        self.doc("sdd/releases/A/s1.yaml")
        self.doc("sdd/features/DESIGN_B.md")
        self.doc("sdd/reviews/UX_REVIEW_C.md")
        self.doc("sdd/reports/solto.md")
        antes = self.git(self.r, "status", "--porcelain")
        rc, out, err = self.arquivo()
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.git(self.r, "status", "--porcelain"), antes)
        self.assertIn("== Lote com-ledger: 2 arquivo(s) ==", out)
        self.assertIn("sdd/features/DEFINE_A.md  →  sdd/archive/A/DEFINE_A.md", out)
        self.assertIn("== Lote sem-ledger: 1 arquivo(s) ==", out)
        self.assertIn("sdd/features/DESIGN_B.md  →  sdd/archive/B/DESIGN_B.md", out)
        self.assertIn("== Lote soltos: 2 arquivo(s) ==", out)
        self.assertIn("sdd/reviews/UX_REVIEW_C.md  →  sdd/archive/_REPORTS_2026-01/UX_REVIEW_C.md", out)
        self.assertIn("sdd/reports/solto.md  →  sdd/archive/_REPORTS_2026-01/solto.md", out)
        self.assertIn("Nada foi movido.", out)
        self.assertIn("TOTAIS: com-ledger=2 · sem-ledger=1 · soltos=2", out)
        self.assertResultado(out)

    def test_recente_fica(self):
        self.doc("sdd/features/DEFINE_A.md", "2026-10-30T12:00:00")
        self.doc("sdd/releases/A/s1.yaml", "2026-10-30T12:00:00")
        self.doc("sdd/features/DEFINE_B.md", "2026-09-30T12:00:00")
        _, out, _ = self.arquivo()
        self.assertIn("A (1 documento(s), quieto há 6 dia(s), limite 30)", out)
        self.assertIn("B (1 documento(s), quieto há 36 dia(s), limite 60)", out)
        self.assertIn("com-ledger=0 · sem-ledger=0", out)
        _, out, _ = self.arquivo("--dias-a", "1", "--dias-b", "1")
        self.assertIn("com-ledger=1 · sem-ledger=1", out)

    def test_atividade_mais_recente_do_grupo_manda(self):
        self.doc("sdd/features/DEFINE_A.md")
        self.doc("sdd/features/DESIGN_A.md", "2026-11-01T12:00:00")
        _, out, _ = self.arquivo()
        self.assertIn("sem-ledger=0", out)

    def test_nome_com_acento_e_slice_e_sufixo_maiusculo(self):
        self.doc("sdd/features/DEFINE_A_s2.md")
        self.doc("sdd/features/DESIGN_A.md")
        self.doc("sdd/features/DEFINE_A_V2.md")
        self.doc("sdd/reports/relatório antigo.md")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/features/DEFINE_A_s2.md  →  sdd/archive/A/DEFINE_A_s2.md", out, "slice minúsculo fica no grupo")
        self.assertIn("sdd/features/DEFINE_A_V2.md  →  sdd/archive/A_V2/DEFINE_A_V2.md", out, "sufixo maiúsculo é nome")
        self.assertIn("sdd/reports/relatório antigo.md  →  sdd/archive/_REPORTS_2026-01/", out)

    def test_nao_rastreado_aparece_e_e_pulado(self):
        self.escreve(self.r, "sdd/features/DEFINE_N.md", "x\n")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/features/DEFINE_N.md  →  sdd/archive/N/DEFINE_N.md  ⚠️ não rastreado: pulo", out)
        rc, out, _ = self.arquivo("--lote", "sem-ledger", "--aplicar")
        self.assertEqual(rc, 0)
        self.assertTrue((self.r / "sdd/features/DEFINE_N.md").is_file())
        self.assertIn("movi 0 arquivo(s)", out)


class Protecao(Base):
    def setUp(self):
        super().setUp()
        self.doc("sdd/features/DEFINE_F1.md")
        self.doc("sdd/features/DEFINE_F14.md")

    def test_ficha_aberta_protege_e_diz_por_que(self):
        self.ficha("F1", "🔨 em andamento")
        _, out, _ = self.arquivo()
        self.assertIn("F1 (1 documento(s)): ficha aberta em HANDOFF_F1.md", out)
        self.assertIn("sdd/features/DEFINE_F14.md  →", out, "F1 não protege F14")
        self.assertNotIn("sdd/features/DEFINE_F1.md  →", out)

    def test_status_comeca_em_check_e_a_regra_do_lint(self):
        self.ficha("F1", "✅ DoD fechado")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/features/DEFINE_F1.md  →", out)
        self.ficha("F1", "🔨 em andamento — parte ✅")
        _, out, _ = self.arquivo()
        self.assertNotIn("sdd/features/DEFINE_F1.md  →", out)

    def test_citada_em_ficha_aberta(self):
        self.escreve(self.r, "sdd/handoffs/HANDOFF_OUTRA.md", "| **Status** | aberta |\n\nversa sobre DEFINE_F14.md e nada mais\n")
        _, out, _ = self.arquivo()
        self.assertIn("documento citado numa ficha aberta", out)
        self.assertNotIn("sdd/features/DEFINE_F14.md  →", out)
        self.assertIn("sdd/features/DEFINE_F1.md  →", out)

    def test_citacao_por_palavra_inteira(self):
        self.escreve(self.r, "sdd/handoffs/HANDOFF_OUTRA.md", "| **Status** | aberta |\n\na F1 ainda não fechou\n")
        _, out, _ = self.arquivo()
        self.assertIn("F1 (1 documento(s)): citada numa ficha aberta", out)
        self.assertIn("sdd/features/DEFINE_F14.md  →", out)

    def test_ficha_fechada_nao_protege_quem_ela_cita(self):
        self.escreve(self.r, "sdd/handoffs/HANDOFF_OUTRA.md", "| **Status** | ✅ fechada |\n\nversa sobre F1\n")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/features/DEFINE_F1.md  →", out)

    def test_pastas_que_nunca_saem(self):
        self.doc("sdd/reports/evidence/F1/DEFINE_F1.md")
        self.doc("sdd/archive/X/DEFINE_X.md")
        self.doc("sdd/releases/F1/s1.yaml")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/reports/evidence/", out)
        self.assertNotIn("sdd/reports/evidence/F1/DEFINE_F1.md  →", out)
        self.assertNotIn("sdd/archive/X/DEFINE_X.md  →", out)
        self.assertNotIn("sdd/releases/F1/s1.yaml  →", out)


class Aplicar(Base):
    def test_move_so_o_lote_com_git_mv_sem_commitar(self):
        self.doc("sdd/features/DEFINE_A.md")
        self.doc("sdd/reports/solto.md")
        head = self.git(self.r, "rev-parse", "HEAD")
        rc, out, err = self.arquivo("--lote", "sem-ledger", "--aplicar")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("movi 1 arquivo(s) com git mv; nada foi apagado", out)
        self.assertIn("commite", out)
        self.assertTrue((self.r / "sdd/archive/A/DEFINE_A.md").is_file())
        self.assertFalse((self.r / "sdd/features/DEFINE_A.md").exists())
        self.assertTrue((self.r / "sdd/reports/solto.md").is_file(), "outro lote fica")
        self.assertEqual(self.git(self.r, "rev-parse", "HEAD"), head)
        self.assertIn("R  sdd/features/DEFINE_A.md -> sdd/archive/A/DEFINE_A.md", self.git(self.r, "status", "--porcelain"))

    def test_destino_que_existe_avisa_e_pula(self):
        self.doc("sdd/features/DEFINE_A.md")
        self.doc("sdd/archive/A/DEFINE_A.md")
        rc, out, err = self.arquivo("--lote", "sem-ledger", "--aplicar")
        self.assertEqual(rc, 0, out + err)
        self.assertIn("destino já existe", err)
        self.assertTrue((self.r / "sdd/features/DEFINE_A.md").is_file())

    def test_git_mv_que_falha_sai_2(self):
        self.doc("sdd/features/DEFINE_A.md")
        self.escreve(self.r, "sdd/archive", "arquivo no lugar da pasta\n")
        rc, out, err = self.arquivo("--lote", "sem-ledger", "--aplicar")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("RESULTADO: FALHA", err)


class Uso(Base):
    def test_aplicar_sem_lote_e_opcoes_invalidas_saem_64(self):
        for args in (("--aplicar",), ("--lote", "xyz"), ("--xyz",), ("--dias-a", "x")):
            with self.subTest(args=args):
                rc, out, err = self.arquivo(*args)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)
        rc, _o, e = self.roda([PYTHON, "-B", SCRIPT, "--hoje", "ontem"], self.r)
        self.assertEqual(rc, 64, e)
        rc, _o, e = self.roda([PYTHON, "-B", SCRIPT, "--dias-b", "-1"], self.r)
        self.assertEqual(rc, 64, e)

    def test_fora_de_repositorio_e_sem_sdd_saem_2(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, _o, e = self.roda([PYTHON, "-B", SCRIPT], fora)
        self.assertEqual(rc, 2, e)
        self.assertIn("RESULTADO: FALHA", e)
        rc, _o, e = self.roda([PYTHON, "-B", SCRIPT], self.r)
        self.assertEqual(rc, 2, e)
        self.assertIn("sdd/", e)

    def test_sem_nada_a_mover_sai_0(self):
        self.escreve(self.r, "sdd/features/.gitkeep", "")
        rc, out, _ = self.arquivo()
        self.assertEqual(rc, 0)
        self.assertIn("com-ledger=0 · sem-ledger=0 · soltos=0", out)
        self.assertIn("Nada foi movido.", out)
