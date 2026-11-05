"""Contrato do sdd/bin/sdd-archive.py (DEFINE F14_DRIVE AT-028 a AT-030): simulação por padrão, git mv por lote, proteção
pela ficha. Repositório na sandbox, com datas de commit fixas e --hoje fixo."""
from __future__ import annotations

import os

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

    def test_edicao_sem_commit_conta_como_atividade(self):
        # L15 do ciclo 1: rastreado sujo e não rastreado recente não são "quietos"
        self.doc("sdd/features/DEFINE_A.md")
        self.escreve(self.r, "sdd/features/DEFINE_A.md", "editado\n")
        self.escreve(self.r, "sdd/reports/novo.md", "x\n")
        import time
        agora = time.mktime((2026, 11, 4, 12, 0, 0, 0, 0, -1))
        os.utime(str(self.r / "sdd/features/DEFINE_A.md"), (agora, agora))
        os.utime(str(self.r / "sdd/reports/novo.md"), (agora, agora))
        _, out, _ = self.arquivo()
        self.assertIn("sem-ledger=0 · soltos=0", out)
        self.assertNotIn("_REPORTS_0000-00", out)

    def test_sujo_com_mtime_velho_tambem_e_atividade(self):
        # L7 do ciclo 2
        self.doc("sdd/features/DEFINE_A.md")
        self.escreve(self.r, "sdd/features/DEFINE_A.md", "editado\n")
        import time
        velho = time.mktime((2020, 1, 1, 12, 0, 0, 0, 0, -1))
        os.utime(str(self.r / "sdd/features/DEFINE_A.md"), (velho, velho))
        _, out, _ = self.arquivo()
        self.assertIn("sem-ledger=0", out)

    def test_documento_que_so_existe_no_merge_usa_a_edicao(self):
        # L8 do ciclo 2
        self.git(self.r, "checkout", "-q", "-b", "lado")
        self.doc("sdd/reports/a.md", "2026-11-04T12:00:00")
        principal = self.git(self.r, "rev-parse", "--abbrev-ref", "HEAD@{1}") if False else None
        self.git(self.r, "checkout", "-q", "-")
        self.doc("sdd/reports/b.md", "2026-11-04T12:00:00")
        self.git(self.r, "merge", "-q", "--no-commit", "--no-ff", "lado")
        self.escreve(self.r, "sdd/reports/feito_no_merge.md", "x\n")
        self.git(self.r, "add", "sdd/reports/feito_no_merge.md")
        self.git(self.r, "commit", "-q", "-m", "merge")
        _, out, _ = self.arquivo("--hoje", HOJE) if False else self.arquivo()
        self.assertNotIn("_REPORTS_0000-00", out)

    def test_nao_rastreado_antigo_vai_para_o_mes_da_edicao(self):
        # o outro lado
        self.escreve(self.r, "sdd/reports/antigo.md", "x\n")
        import time
        velho = time.mktime((2026, 2, 3, 12, 0, 0, 0, 0, -1))
        os.utime(str(self.r / "sdd/reports/antigo.md"), (velho, velho))
        _, out, _ = self.arquivo()
        self.assertIn("sdd/reports/antigo.md  →  sdd/archive/_REPORTS_2026-02/antigo.md  ⚠️ não rastreado: pulo", out)

    def test_saida_em_utf8_mesmo_com_cp1252(self):
        # L14 do ciclo 1
        self.doc("sdd/features/DEFINE_A.md")
        rc, out, err = self.roda([PYTHON, "-B", SCRIPT, "--hoje", HOJE], self.r, dict(self.env, PYTHONIOENCODING="cp1252"))
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("Traceback", err)

    def test_nao_rastreado_aparece_e_e_pulado(self):
        self.escreve(self.r, "sdd/features/DEFINE_N.md", "x\n")
        import time
        velho = time.mktime((2026, 2, 3, 12, 0, 0, 0, 0, -1))
        os.utime(str(self.r / "sdd/features/DEFINE_N.md"), (velho, velho))
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
        self.assertIn("citada numa ficha aberta", out)
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

    def test_prefixo_longo_e_o_nome_da_feature(self):
        # M5 do ciclo 1: FIX_REPORT_F1 é da F1, não da feature REPORT_F1
        self.ficha("F1", "🔨 em andamento")
        self.doc("sdd/reports/FIX_REPORT_F1.md")
        _, out, _ = self.arquivo()
        self.assertIn("F1 (2 documento(s)): ficha aberta", out)
        self.assertNotIn("FIX_REPORT_F1.md  →", out)

    def test_feature_com_minuscula_ou_hifen_e_protegida(self):
        # M6 do ciclo 1
        self.ficha("minha-frente", "aberta")
        self.doc("sdd/reports/BUILD_REPORT_minha-frente.md")
        self.doc("sdd/reports/AVALIACAO_minha-frente.md")
        _, out, _ = self.arquivo()
        self.assertIn("minha-frente (2 documento(s)): ficha aberta", out)
        self.assertNotIn("BUILD_REPORT_minha-frente.md  →", out)

    def test_ficha_aberta_de_slice_protege_a_feature(self):
        # M7 do ciclo 1
        self.ficha("G_s2", "aberta")
        self.doc("sdd/features/DEFINE_G_s2.md")
        self.doc("sdd/features/DESIGN_G.md")
        self.doc("sdd/releases/G/s1.yaml")
        _, out, _ = self.arquivo()
        self.assertNotIn("DEFINE_G_s2.md  →", out)
        self.assertNotIn("DESIGN_G.md  →", out)
        self.assertIn("G (2 documento(s)): ficha aberta", out)

    def test_documento_solto_citado_em_ficha_aberta_fica(self):
        # M8 do ciclo 1
        self.doc("sdd/reports/NOTAS_DA_FRENTE.md")
        self.doc("sdd/reports/parecer.txt")
        self.doc("sdd/reports/outro.txt")
        self.escreve(self.r, "sdd/handoffs/HANDOFF_OUTRA.md", "| **Status** | aberta |\n\nver sdd/reports/NOTAS_DA_FRENTE.md e parecer.txt\n")
        _, out, _ = self.arquivo()
        self.assertNotIn("NOTAS_DA_FRENTE.md  →", out)
        self.assertNotIn("parecer.txt  →", out)
        self.assertIn("NOTAS_DA_FRENTE.md (1 documento(s)): documento citado", out)
        self.assertIn("sdd/reports/outro.txt  →", out, "o que não foi citado segue")

    def test_nome_com_outras_palavras_e_da_ficha_aberta(self):
        # M2 do ciclo 2
        self.ficha("F14_DRIVE", "aberta")
        for rel in ("sdd/reviews/REVISAO_FRONTEIRA_F14_DRIVE_20261105.md", "sdd/reviews/AVALIACAO_F14_DRIVE-ciclo2.md", "sdd/reports/BUILD_REPORT_F14_DRIVE.md"):
            self.doc(rel)
        _, out, _ = self.arquivo()
        self.assertNotIn("F14_DRIVE-ciclo2.md  →", out)
        self.assertNotIn("REVISAO_FRONTEIRA_F14_DRIVE_20261105.md  →", out)

    def test_palavra_inteira_nao_protege_vizinho(self):
        # o outro lado de M2
        self.ficha("F14_DRIVE", "aberta")
        self.doc("sdd/reports/BUILD_REPORT_F14_DRIVEX.md")
        self.doc("sdd/reports/BUILD_REPORT_XF14_DRIVE.md")
        _, out, _ = self.arquivo()
        self.assertIn("BUILD_REPORT_F14_DRIVEX.md  →", out)
        self.assertIn("BUILD_REPORT_XF14_DRIVE.md  →", out)

    def test_outra_caixa_e_acento_protegem(self):
        # M3 do ciclo 2
        self.ficha("f14", "aberta")
        self.ficha("ação", "aberta")
        self.doc("sdd/reports/BUILD_REPORT_F14.md")
        self.doc("sdd/reports/BUILD_REPORT_ação.md")
        _, out, _ = self.arquivo()
        self.assertNotIn("BUILD_REPORT_F14.md  →", out)
        self.assertNotIn("BUILD_REPORT_ação.md  →", out)

    def test_citacao_em_outra_caixa_e_acento(self):
        # M4 do ciclo 3
        self.doc("sdd/features/DEFINE_F14_FOO.md")
        self.doc("sdd/reports/NOTAS_B.md")
        self.doc("sdd/reports/BUILD_REPORT_ação.md")
        self.escreve(self.r, "sdd/handoffs/HANDOFF_OUTRA.md", "| **Status** | aberta |\n\nver f14_foo, sdd/reports/notas_b.md e ação\n")
        _, out, _ = self.arquivo()
        for nome in ("DEFINE_F14_FOO.md  →", "NOTAS_B.md  →"):
            self.assertNotIn(nome, out)
        self.assertIn("sdd/features/DEFINE_F1.md  →", out, "o que não foi citado segue")

    def test_status_de_fora_da_ficha_nao_fecha(self):
        # L11 do ciclo 3
        self.escreve(self.r, "sdd/handoffs/HANDOFF_F1.md", "| Status | ✅ velho |\n\n## Ficha da feature\n\n| Campo | Valor |\n|---|---|\n| **Status** | 🔨 aberta |\n")
        _, out, _ = self.arquivo()
        self.assertNotIn("sdd/features/DEFINE_F1.md  →", out)
        self.escreve(self.r, "sdd/handoffs/HANDOFF_F1.md", "```\n| **Status** | ✅ exemplo |\n```\n\n| **Status** | 🔨 aberta |\n")
        _, out, _ = self.arquivo()
        self.assertNotIn("sdd/features/DEFINE_F1.md  →", out)

    def test_ficha_com_nome_de_prefixo_nao_protege_todos(self):
        # L12 do ciclo 3
        self.ficha("DESIGN", "aberta")
        self.doc("sdd/features/DESIGN_FECHADA.md")
        _, out, _ = self.arquivo()
        self.assertIn("sdd/features/DESIGN_FECHADA.md  →", out)

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
