"""Contrato do .agents/skills/sdd-new-session/scripts/copiar-docs.sh (DEFINE F14 AT-026, AT-027): só nome idêntico."""
from __future__ import annotations

import os

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / ".agents/skills/sdd-new-session/scripts/copiar-docs.sh"


class Base_(Sandbox):
    def setUp(self):
        super().setUp()
        self.p = self.repo("principal")
        self.escreve(self.p, "README.md", "x\n")
        self.commit(self.p)
        self.f = self.tmp / "frente"
        self.f.mkdir()

    def copia(self, slug="relatorio-mensal"):
        return self.roda([BASH, SCRIPT, self.p, self.f, slug], self.tmp)

    def doc(self, rel, texto="x\n"):
        return self.escreve(self.p, rel, texto)


class Copia(Base_):
    def test_cada_prefixo_nas_2_pastas_e_cria_a_pasta_de_destino(self):
        rels = ("sdd/features/BRAINSTORM_RELATORIO_MENSAL.md", "sdd/features/DEFINE_RELATORIO_MENSAL.md",
                "sdd/features/DESIGN_RELATORIO_MENSAL.md", "sdd/reviews/UX_REVIEW_RELATORIO_MENSAL.md",
                "sdd/reviews/GOVERNANCA_REVIEW_RELATORIO_MENSAL.md")
        for r in rels:
            self.doc(r, r + "\n")
        rc, out, err = self.copia()
        self.assertEqual(rc, 0, out + err)
        for r in rels:
            with self.subTest(arquivo=r):
                self.assertIn("COPIADO " + r, out)
                self.assertEqual((self.f / r).read_text(encoding="utf-8"), r + "\n")
                self.assertTrue((self.p / r).is_file(), "o original fica")
        self.assertIn("RESULTADO: 5 COPIADO(S)", out)
        self.assertIn("→ ", out)

    def test_nada_a_copiar_sai_0(self):
        self.doc("sdd/features/DEFINE_OUTRA.md")
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("RESULTADO: NADA A COPIAR", out)
        self.assertNotIn("OUTRA", out)
        self.assertFalse((self.f / "sdd").exists())

    def test_sem_pasta_sdd_no_principal_sai_0(self):
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("NADA A COPIAR", out)

    def test_nome_com_acento_e_identico_ao_slug(self):
        self.doc("sdd/features/DEFINE_RELATÓRIO_MENSAL.md")
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("RESULTADO: 1 COPIADO(S)", out)
        self.assertTrue((self.f / "sdd/features/DEFINE_RELATÓRIO_MENSAL.md").is_file())

    def test_cada_vogal_acentuada_e_o_cedilha(self):
        for nome, slug in (("AÇÃO_É", "acao-e"), ("ÍNDICE_Ó", "indice-o"), ("MÊS_ÚTIL", "mes-util"), ("PÃO", "pao"), ("LÁ", "la")):
            with self.subTest(nome=nome):
                d = self.doc("sdd/features/DEFINE_%s.md" % nome)
                _, out, _ = self.copia(slug)
                self.assertIn("COPIADO sdd/features/DEFINE_%s.md" % nome, out)
                d.unlink()

    def test_arquivo_ignorado_pelo_git_tambem_vem(self):
        self.escreve(self.p, ".gitignore", "sdd/features/\n")
        self.commit(self.p)
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        self.assertIn("COPIADO sdd/features/DEFINE_RELATORIO_MENSAL.md", self.copia()[1])

    def test_nome_com_quebra_de_linha_nao_vira_2_caminhos(self):
        # N1 do auditor, rodada 1
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md\nlixo", "x\n")
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md", "certo\n")
        rc, out, err = self.copia()
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(out.count("COPIADO sdd/features/DEFINE_RELATORIO_MENSAL.md\n"), 1)
        self.assertEqual((self.f / "sdd/features/DEFINE_RELATORIO_MENSAL.md").read_text(encoding="utf-8"), "certo\n")

    def test_nome_com_espaco_chega_inteiro(self):
        self.doc("sdd/features/DEFINE_RELATORIO MENSAL.md")
        self.assertTrue(self.copia()[0] == 0 and (self.f / "sdd/features/DEFINE_RELATORIO MENSAL.md").is_file())


class NaoCopia(Base_):
    def test_destino_existente_fica(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md", "do principal\n")
        self.escreve(self.f, "sdd/features/DEFINE_RELATORIO_MENSAL.md", "da frente\n")
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("JA_EXISTE sdd/features/DEFINE_RELATORIO_MENSAL.md", out)
        self.assertEqual((self.f / "sdd/features/DEFINE_RELATORIO_MENSAL.md").read_text(encoding="utf-8"), "da frente\n")

    def test_parecido_dos_2_lados_nao_copia_e_diz_o_motivo(self):
        for feature, slug in (("RELATORIO_MENSAL_V2", "relatorio-mensal"), ("RELATORIO", "relatorio-mensal")):
            with self.subTest(feature=feature):
                d = self.doc("sdd/features/DEFINE_%s.md" % feature)
                rc, out, _ = self.copia(slug)
                self.assertEqual(rc, 0)
                self.assertIn("PARECIDO sdd/features/DEFINE_%s.md" % feature, out)
                self.assertIn("não copiei, porque o nome não é idêntico", out)
                self.assertIn("NADA A COPIAR", out)
                self.assertIn("copie à mão", out)
                self.assertFalse((self.f / "sdd").exists())
                d.unlink()

    def test_prefixo_desconhecido_e_subpasta_e_outra_extensao(self):
        for rel in ("sdd/features/NOTAS_RELATORIO_MENSAL.md", "sdd/features/sub/DEFINE_RELATORIO_MENSAL.md",
                    "sdd/features/DEFINE_RELATORIO_MENSAL.txt", "outra/DEFINE_RELATORIO_MENSAL.md"):
            self.doc(rel)
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("NADA A COPIAR", out)
        self.assertFalse((self.f / "sdd").exists())

    def test_link_na_origem_nao_e_seguido(self):
        fora = self.escreve(self.tmp, "fora.md", "segredo\n")
        (self.p / "sdd/features").mkdir(parents=True)
        os.symlink(str(fora), str(self.p / "sdd/features/DEFINE_RELATORIO_MENSAL.md"))
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("IGNORADO sdd/features/DEFINE_RELATORIO_MENSAL.md", out)
        self.assertFalse((self.f / "sdd/features/DEFINE_RELATORIO_MENSAL.md").exists())

    def test_pasta_de_destino_que_e_link_nao_recebe(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        (self.f / "sdd").mkdir()
        os.symlink(str(fora), str(self.f / "sdd/features"))
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("IGNORADO", out)
        self.assertEqual(list(fora.iterdir()), [])

    def test_frente_sdd_que_e_link_nao_recebe(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        os.symlink(str(fora), str(self.f / "sdd"))
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("IGNORADO", out)
        self.assertIn("com link não foram copiados", out)
        self.assertEqual(list(fora.iterdir()), [])

    def test_destino_que_e_link_quebrado_nao_recebe(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md", "novo\n")
        (self.f / "sdd/features").mkdir(parents=True)
        alvo = self.tmp / "alvo.md"
        os.symlink(str(alvo), str(self.f / "sdd/features/DEFINE_RELATORIO_MENSAL.md"))
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("JA_EXISTE", out)
        self.assertFalse(alvo.exists())

    def test_sdd_do_principal_que_e_link_e_dito(self):
        fora = self.tmp / "sdd-fora"
        self.escreve(fora, "features/DEFINE_RELATORIO_MENSAL.md", "x\n")
        os.symlink(str(fora), str(self.p / "sdd"))
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("IGNORADO sdd/features", out)
        self.assertFalse((self.f / "sdd").exists())

    def test_documento_commitado_e_nao_enviado_e_dito(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        self.commit(self.p)
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("NAO_COPIADO sdd/features/DEFINE_RELATORIO_MENSAL.md", out)
        self.assertIn("ainda não foi enviado", out)
        self.assertFalse((self.f / "sdd/features/DEFINE_RELATORIO_MENSAL.md").exists())

    def test_so_no_indice_e_copiado_nao_e_commit_nao_enviado(self):
        # R5@claude da rodada 3
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        self.git(self.p, "add", "sdd/features/DEFINE_RELATORIO_MENSAL.md")
        rc, out, _ = self.copia()
        self.assertEqual(rc, 0)
        self.assertIn("COPIADO sdd/features/DEFINE_RELATORIO_MENSAL.md", out)
        self.assertNotIn("NAO_COPIADO", out)

    def test_link_so_no_indice_nao_e_dito_como_salvo(self):
        # o outro lado do R5: a lista de salvos vem do commit; o índice não é "salvo no git" para a frente
        fora = self.escreve(self.tmp, "fora.md", "x\n")
        (self.p / "sdd/features").mkdir(parents=True, exist_ok=True)
        os.symlink(str(fora), str(self.p / "sdd/features/DEFINE_RELATORIO_MENSAL.md"))
        self.git(self.p, "add", "sdd/features/DEFINE_RELATORIO_MENSAL.md")
        _, out, _ = self.copia()
        self.assertIn("IGNORADO sdd/features/DEFINE_RELATORIO_MENSAL.md", out)
        self.assertNotIn("NAO_COPIADO", out)

    def test_link_ignorado_aparece_na_seta_mesmo_com_copia(self):
        # R6@claude da rodada 3
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        fora = self.escreve(self.tmp, "fora.md", "x\n")
        os.symlink(str(fora), str(self.p / "sdd/features/DESIGN_RELATORIO_MENSAL.md"))
        _, out, _ = self.copia()
        self.assertIn("COPIADO", out)
        self.assertIn("IGNORADO sdd/features/DESIGN_RELATORIO_MENSAL.md", out)
        self.assertIn("com link não foram copiados", out)
        self.assertNotIn("já estão na frente", out)

    def test_seta_com_ignorado_e_parecido_diz_os_dois(self):
        # R3 da rodada 4: a precedência escondia para onde copiar o PARECIDO
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL_V2.md")
        fora = self.escreve(self.tmp, "fora.md", "x\n")
        (self.p / "sdd/features").mkdir(parents=True, exist_ok=True)
        os.symlink(str(fora), str(self.p / "sdd/features/DESIGN_RELATORIO_MENSAL.md"))
        _, out, _ = self.copia()
        seta = [l for l in out.split("\n") if l.startswith("→ ")]
        self.assertEqual(len(seta), 1, out)
        self.assertIn("com link não foram copiados", seta[0])
        self.assertIn("copie à mão para %s/sdd/features/" % self.f, seta[0])

    def test_seta_com_os_3_casos_junta_os_3(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        self.commit(self.p)
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL_V2.md")
        fora = self.escreve(self.tmp, "fora.md", "x\n")
        os.symlink(str(fora), str(self.p / "sdd/features/DESIGN_RELATORIO_MENSAL.md"))
        _, out, _ = self.copia()
        seta = [l for l in out.split("\n") if l.startswith("→ ")]
        self.assertEqual(len(seta), 1, out)
        for frase in ("ainda não foi enviado", "com link não foram copiados", "Se algum PARECIDO"):
            self.assertIn(frase, seta[0])

    def test_so_parecido_nao_fala_de_link_nem_de_commit(self):
        # o outro lado: cada frase só aparece com o caso dela
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL_V2.md")
        _, out, _ = self.copia()
        self.assertIn("Se algum PARECIDO", out)
        self.assertNotIn("com link não foram copiados", out)
        self.assertNotIn("ainda não foi enviado", out)
        self.assertNotIn("já estão na frente", out)

    def test_commitado_que_ja_esta_na_frente_nao_e_dito(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        self.commit(self.p)
        self.escreve(self.f, "sdd/features/DEFINE_RELATORIO_MENSAL.md", "x\n")
        self.assertNotIn("NAO_COPIADO", self.copia()[1])

    def test_copia_que_falha_sai_2(self):
        self.doc("sdd/features/DEFINE_RELATORIO_MENSAL.md")
        (self.f / "sdd").mkdir()
        self.escreve(self.f, "sdd/features", "é um arquivo, não uma pasta\n")
        rc, out, err = self.copia()
        self.assertEqual(rc, 2, out + err)
        self.assertIn("RESULTADO: FALHA", out)


class Uso(Base_):
    def test_argumentos_e_pastas_saem_64(self):
        sem_git = self.tmp / "sem-git"
        sem_git.mkdir()
        for args in ((), (self.p,), (self.p, self.f), (self.p, self.f, "x", "y"), (self.tmp / "nao", self.f, "x"),
                     (self.p, self.tmp / "nao", "x"), (sem_git, self.f, "x"), (self.p, self.f, ""),
                     (self.p, self.f, "Com Maiuscula"), (self.p, self.f, "../x")):
            with self.subTest(args=args):
                rc, out, err = self.roda([BASH, SCRIPT, *args], self.tmp)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)
                self.assertEqual(out, "")
