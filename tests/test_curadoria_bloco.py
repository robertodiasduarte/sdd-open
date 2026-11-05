"""Contrato do --conferir-bloco e do --selar do sdd/bin/playbook-curator.sh (DEFINE F14 AT-020, AT-021): quem separa
contagem de mudança de regra é um programa que confere a colheita, não quem conduz a release nem o curador."""
from __future__ import annotations

import os
import shutil

from apoio import BASH, RAIZ, Sandbox

CURATOR = RAIZ / "sdd/bin/playbook-curator.sh"
FX = RAIZ / "sdd/fixtures/playbook/curadoria"
BASE = FX / "playbook-base.md"
BLOCO = (FX / "bloco-ok.txt").read_text(encoding="utf-8")
VERDE = "RESULTADO: SÓ O PERMITIDO MUDOU\n→ siga.\n"
LINHA_AUTO = "| 1 | contador | LM-020 | LM-020 ajudou+1 | DESIGN_FIXTURE.md:16 (✔ tratado) |"


class Base_(Sandbox):
    def setUp(self):
        super().setUp()
        self.env = dict(self.env, SDD_TRACE="off")
        self.stg = self.tmp / "stg"
        self.stg.mkdir()
        for n in ("DESIGN_FIXTURE.md", "BUILD_REPORT_FIXTURE.md", "AVAL-AT-002.log"):
            shutil.copyfile(str(FX / n), str(self.stg / n))
        rc, out, err = self.cur("--colher", self.stg, BASE)
        self.assertEqual(rc, 0, out + err)
        self.colheita = self.escreve(self.stg, "colheita.txt", out)
        self.selo = self.sela()
        self.comparar = self.escreve(self.tmp, "comparar.txt", VERDE)

    def cur(self, *args):
        return self.roda([BASH, CURATOR, *args], self.tmp)

    def sela(self):
        rc, out, err = self.cur("--selar", self.stg)
        self.assertEqual(rc, 0, err)
        return self.escreve(self.tmp, "selo.txt", out)

    def confere(self, bloco=BLOCO, colheita=None, selo=None, comparar=None):
        b = self.escreve(self.tmp, "bloco.txt", bloco)
        return self.cur("--conferir-bloco", colheita or self.colheita, b, BASE, selo or self.selo, comparar or self.comparar)

    def reprova(self, bloco, trecho, **kw):
        rc, out, err = self.confere(bloco, **kw)
        self.assertEqual(rc, 2, out + err)
        self.assertIn(trecho, err)
        self.assertIn("RESULTADO: BLOCO INVÁLIDO", out)
        self.assertNotIn("AUTO ", out)
        self.assertNotIn("PERGUNTA ", out)


class Valido(Base_):
    """AT-021"""

    def test_bloco_de_exemplo(self):
        rc, out, err = self.confere()
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(out, r"(?m)^AUTO LM-020 ajudou\+1$")
        self.assertRegex(out, r"(?m)^AUTO LM-016 mordeu\+1$")
        self.assertRegex(out, r"(?m)^PERGUNTA 4 add ADD Reviews / harness ")
        self.assertRegex(out, r"(?m)^PERGUNTA 5 add ADD Backend ")
        self.assertRegex(out, r"(?m)^PERGUNTA 6 promover LM-004 promovido_para=sdd/hooks/pre-commit$")
        self.assertIn("   simples: ", out)
        self.assertRegex(out, r"(?m)^resumo-bloco: auto=2 pergunta=3 descartar=1 nao_julgado=0 contaminacao=nao$")
        self.assertIn("RESULTADO: BLOCO VÁLIDO", out)

    def test_contaminacao_declarada_avisa(self):
        rc, out, _ = self.confere(BLOCO.replace("CONTAMINAÇÃO: não", "CONTAMINAÇÃO: sim — veio o diff"))
        self.assertEqual(rc, 0)
        self.assertIn("AVISO contaminação", out)
        self.assertIn("contaminacao=sim", out)

    def test_sugestao_confirmada_vira_pergunta_nunca_auto(self):
        confirmada = BLOCO.replace("| DESCARTAR (a causa do achado não é a regra do aviso) |", "| ACEITAR |")
        rc, out, err = self.confere(confirmada)
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(out, r"(?m)^PERGUNTA 3 sugestao LM-020 mordeu\+1$")
        self.assertNotIn("AUTO LM-020 mordeu", out)

    def test_barra_escapada_na_celula_nao_quebra_a_tabela(self):
        com_barra = BLOCO.replace("Regra sintética com evidência.", "Regra sobre cmd \\| tail.")
        rc, out, err = self.confere(com_barra)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("Regra sobre cmd | tail.", out)


class Reprova(Base_):
    """AT-020"""

    def test_sem_o_par(self):
        self.reprova(BLOCO.replace("<<<CURADORIA\n", ""), "exatamente 1 linha <<<CURADORIA")
        self.reprova(BLOCO.replace(">>>\n", ""), "linha >>> de fechamento")
        self.reprova(BLOCO + BLOCO, "exatamente 1 linha <<<CURADORIA")

    def test_cada_linha_da_colheita_precisa_aparecer(self):
        casos = {"| contador | LM-020 |": "DELTA LM-020 ajudou+1", "| contador | LM-016 |": "DELTA LM-016 mordeu+1",
                 "| sugestao | LM-020 |": "SUGESTAO para LM-020", "| add | LM-023 |": "CANDIDATO #1 → LM-023",
                 "| add | LM-024 |": "CANDIDATO #2 → LM-024", "| promover | LM-004 |": "PROMOVER? LM-004"}
        for marca, trecho in casos.items():
            with self.subTest(marca=marca):
                self.reprova("\n".join(l for l in BLOCO.split("\n") if marca not in l), "a colheita tem " + trecho)
        self.reprova(BLOCO.replace("BUILD_REPORT_FIXTURE.md:24 — sem evidência · ", ""), "REJEITADO em BUILD_REPORT_FIXTURE.md:24")

    def test_ignorado_e_ja_colhido_precisam_aparecer(self):
        colheita = self.escreve(self.tmp, "c.txt", self.colheita.read_text(encoding="utf-8") + "IGNORADO LM-777 (x)\nJA_COLHIDO X.md (y)\n")
        selo = self.selo
        rc, _, err = self.cur("--conferir-bloco", colheita, self.escreve(self.tmp, "bl.txt", BLOCO), BASE, selo, self.comparar)
        self.assertEqual(rc, 2)
        self.assertIn("IGNORADO/JA_COLHIDO LM-777", err)
        self.assertIn("IGNORADO/JA_COLHIDO X.md", err)

    def test_refine_que_cita_o_candidato_cobre_a_linha(self):
        l5 = next(l for l in BLOCO.split("\n") if "| add | LM-024 |" in l)
        novo = "| 5 | refine | LM-016 | REFINE LM-016 :: Texto novo. **Do instead:** k. | candidato #2, BUILD_REPORT_FIXTURE.md:35 | Duplica o aviso do preflight. | DESCARTAR (duplica) |"
        rc, out, err = self.confere(BLOCO.replace(l5, novo))
        self.assertEqual(rc, 0, out + err)

    def test_contador_auto_inventado(self):
        self.reprova(BLOCO.replace("| 1 | contador | LM-020 | LM-020 ajudou+1 |", "| 1 | contador | LM-021 | LM-021 ajudou+1 |"), "não está na colheita")

    def test_contador_auto_de_mais_de_1(self):
        self.reprova(BLOCO.replace("| LM-020 ajudou+1 |", "| LM-020 ajudou+5 |"), "AUTO pede um delta de contador com +1")

    def test_auto_com_outra_linha_que_existe_nao_vale(self):
        self.reprova(BLOCO.replace("DESIGN_FIXTURE.md:16 (", "DESIGN_FIXTURE.md:15 ("), "tem de ser a da colheita (DESIGN_FIXTURE.md:16)")

    def test_auto_fora_de_contador(self):
        self.reprova(BLOCO.replace("| DESCARTAR (a causa do achado não é a regra do aviso) |", "| AUTO |"), "AUTO só vale para contador")
        self.reprova(BLOCO.replace("| Uma armadilha nova apareceu nesta feature. Guardar a lição avisa toda sessão que mexer nessa área. | ACEITAR |",
                                   "| Uma armadilha nova apareceu nesta feature. Guardar a lição avisa toda sessão que mexer nessa área. | AUTO |"), "AUTO só vale para contador")

    def test_aceitar_sem_evidencia_que_abre(self):
        self.reprova(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| por raciocínio |"), "exige a Evidência começando por arquivo:linha")
        self.reprova(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| NAO_EXISTE.md:13 |"), "não existe na pasta da colheita")
        self.reprova(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| BUILD_REPORT_FIXTURE.md:9999 |"), "uma linha que o arquivo não tem")

    def test_promocao_so_com_pergunta_obrigatoria(self):
        self.reprova(BLOCO.replace("| PERGUNTA OBRIGATÓRIA |", "| ACEITAR |"), "não usa ACEITAR")

    def test_contador_repetido_ou_com_outro_id_nao_soma(self):
        # H2: 2 linhas AUTO iguais somavam +2 e sumiam com a contagem do outro bullet.
        l2 = next(l for l in BLOCO.split("\n") if "| contador | LM-016 |" in l)
        self.reprova(BLOCO.replace(l2, "| 2 | contador | LM-016 | LM-020 ajudou+1 | DESIGN_FIXTURE.md:16 | x. | AUTO |"), "a coluna LM")
        self.reprova(BLOCO.replace(l2, "| 2 | contador | LM-020 | LM-020 ajudou+1 | DESIGN_FIXTURE.md:16 | x. | AUTO |"), "aparece em 2 linhas")

    def test_uma_linha_nao_cobre_2_da_colheita(self):
        l2 = next(l for l in BLOCO.split("\n") if "| contador | LM-016 |" in l)
        sem = BLOCO.replace(l2 + "\n", "").replace("| 1 | contador | LM-020 |", "| 1 | contador | LM-020 LM-016 |")
        self.reprova(sem, "a coluna LM")

    def test_cobertura_le_o_delta_nao_a_coluna_lm(self):
        l1 = next(l for l in BLOCO.split("\n") if "| contador | LM-020 |" in l)
        self.reprova(BLOCO.replace(l1, "| 1 | contador | LM-020 | LM-020 mordeu+1 | DESIGN_FIXTURE.md:16 | x. | DESCARTAR (x) |"),
                     "a colheita tem DELTA LM-020 ajudou+1")

    def test_contador_descartado_cobre_a_linha(self):
        l1 = next(l for l in BLOCO.split("\n") if "| contador | LM-020 |" in l)
        rc, out, err = self.confere(BLOCO.replace(l1, "| 1 | contador | LM-020 | LM-020 ajudou+1 | DESIGN_FIXTURE.md:16 | A evidência não bate. | DESCARTAR (a linha não diz isso) |"))
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("AUTO LM-020", out)

    def test_detalhes_que_passavam(self):
        # L4 do avaliador, ciclo 1
        self.reprova(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| colheita.txt:1 |"), "a colheita não é evidência de si mesma")
        self.reprova(BLOCO.replace("| DESCARTAR (a causa do achado não é a regra do aviso) |", "| DESCARTAR |"), "DESCARTAR pede o motivo")
        self.reprova(BLOCO.replace("CONTAMINAÇÃO: não", "CONTAMINAÇÃO:"), "precisa dizer 'não' ou 'sim")
        self.reprova(BLOCO.replace("| 2 | contador |", "| 1 | contador |"), "o número 1 aparece em mais de uma linha")
        for vazia in ("—", "-", "`—`"):
            with self.subTest(simples=vazia):
                self.reprova(BLOCO.replace("| O aviso sobre o agendador sem o segredo foi seguido no desenho e evitou o erro. |", "| %s |" % vazia), "'Em linguagem simples' está vazia")

    def test_arquivo_com_espaco_no_nome_passa_e_conta_igual(self):
        # N-L1 do avaliador, ciclo 2
        d = self.tmp / "st"
        d.mkdir()
        self.escreve(d, "AVAL-a b.log", "❌ por LM-020\n")
        _, col, _ = self.cur("--colher", d, BASE)
        c = self.escreve(d, "colheita.txt", col)
        _, selo, _ = self.cur("--selar", d)
        s = self.escreve(self.tmp, "s2.txt", selo)
        cab = "<<<CURADORIA\n| # | Tipo | LM | Delta | Evidência | Em linguagem simples | Recomendação |\n|---|---|---|---|---|---|---|\n"
        fim = "| 2 | promover | LM-004 | LM-004 promovido_para=sdd/hooks/pre-commit | x | y. | PERGUNTA OBRIGATÓRIA |\nREJEITADOS: nenhum\nNAO_JULGADO: nenhum\nIGNORADOS/JA_COLHIDOS: nenhum\nCONTAMINAÇÃO: não\n>>>\n"
        for evid, rc_esperado in (("AVAL-a b.log:1", 0), ("AVAL-a b.log:2", 2), ("AVAL-a b.log:11", 2)):
            with self.subTest(evidencia=evid):
                b = self.escreve(self.tmp, "b.txt", cab + "| 1 | contador | LM-020 | LM-020 mordeu+1 | %s | x. | AUTO |\n" % evid + fim)
                rc, out, err = self.cur("--conferir-bloco", c, b, BASE, s, self.comparar)
                self.assertEqual(rc, rc_esperado, out + err)

    def test_mais_detalhes_que_passavam(self):
        # N-L7 do avaliador, ciclo 2
        self.escreve(self.tmp, "x", "")
        self.reprova(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| colheita.rc:1 |"), "a colheita não é evidência de si mesma")
        self.reprova(BLOCO.replace("| DESCARTAR (a causa do achado não é a regra do aviso) |", "| DESCARTAR () |"), "DESCARTAR pede o motivo")
        self.reprova(BLOCO.replace("CONTAMINAÇÃO: não", "CONTAMINAÇÃO: nãosei"), "precisa dizer 'não' ou 'sim")

    def test_contador_e_aposentadoria_da_mesma_licao_param_aqui(self):
        # N-L2: passavam 1 a 1 e travavam no --cruzar, sem instrução.
        linha = "| 7 | tombstone | LM-020 | TOMBSTONE LM-020 :: saiu | DESIGN_FIXTURE.md:16 | A regra saiu. | ACEITAR |\nREJEITADOS:"
        self.reprova(BLOCO.replace("REJEITADOS:", linha, 1), "o conjunto do bloco não vale junto")

    def test_promocao_e_aposentadoria_da_mesma_licao_param_aqui(self):
        # Mutante vivo no ciclo 3: o conjunto ignorava a PERGUNTA OBRIGATÓRIA.
        linha = "| 7 | tombstone | LM-004 | TOMBSTONE LM-004 :: saiu | DESIGN_FIXTURE.md:16 | A regra saiu. | ACEITAR |\nREJEITADOS:"
        self.reprova(BLOCO.replace("REJEITADOS:", linha, 1), "o conjunto do bloco não vale junto")

    def test_aceitar_com_evidencia_em_arquivo_com_espaco(self):
        # N3-L1
        shutil.copyfile(str(FX / "AVAL-AT-002.log"), str(self.stg / "AVAL a b.log"))
        selo = self.sela()
        rc, out, err = self.confere(BLOCO.replace("| BUILD_REPORT_FIXTURE.md:13 |", "| AVAL a b.log:1 |"), selo=selo)
        self.assertEqual(rc, 0, out + err)

    def test_tabela_sem_cabecalho_precisa_ser_relatada(self):
        self.escreve(self.stg, "DESIGN_Y.md", "## Landmines aplicáveis\n\n| `LM-021` | ✔ x | y |\n")
        _, col, _ = self.cur("--colher", self.stg, BASE)
        c = self.escreve(self.stg, "colheita.txt", col)
        selo = self.sela()
        self.reprova(BLOCO, "IGNORADO/JA_COLHIDO DESIGN_Y.md:3", selo=selo, colheita=c)
        rc, out, err = self.confere(BLOCO.replace("IGNORADOS/JA_COLHIDOS: nenhum", "IGNORADOS/JA_COLHIDOS: DESIGN_Y.md:3 — sem cabeçalho"), selo=selo, colheita=c)
        self.assertEqual(rc, 0, out + err)

    def test_aposentadoria_de_outra_licao_passa(self):
        linha = "| 7 | tombstone | LM-021 | TOMBSTONE LM-021 :: saiu | DESIGN_FIXTURE.md:16 | A regra saiu. | ACEITAR |\nREJEITADOS:"
        rc, out, err = self.confere(BLOCO.replace("REJEITADOS:", linha, 1))
        self.assertEqual(rc, 0, out + err)

    def test_remover_e_valido_na_linha_inv(self):
        linha = "| 7 | inv | LM-021 | REMOVER LM-021 | --cruzar: INV_AFETADA descarte LM-021 | Tira o descarte junto. | ACEITAR |\nREJEITADOS:"
        rc, out, err = self.confere(BLOCO.replace("REJEITADOS:", linha, 1))
        self.assertEqual(rc, 0, out + err)
        self.assertRegex(out, r"(?m)^PERGUNTA 7 inv REMOVER LM-021$")

    def test_linguagem_simples_vazia(self):
        self.reprova(BLOCO.replace("| O aviso sobre o agendador sem o segredo foi seguido no desenho e evitou o erro. |", "|  |"), "'Em linguagem simples' está vazia")

    def test_sem_a_linha_de_contaminacao(self):
        self.reprova(BLOCO.replace("CONTAMINAÇÃO: não\n", ""), "falta a linha CONTAMINAÇÃO:")

    def test_delta_fora_da_gramatica(self):
        self.reprova(BLOCO.replace("| LM-004 promovido_para=sdd/hooks/pre-commit |", "| promover LM-004 |"), "Delta fora da gramática")

    def test_linha_inv_fora_da_gramatica(self):
        linha = "| 7 | inv | INV-009 | isto não é uma invariante | x | Regra nova. | ACEITAR |\nREJEITADOS:"
        self.reprova(BLOCO.replace("REJEITADOS:", linha, 1), "a linha completa da invariante")

    def test_tipo_recomendacao_colunas(self):
        self.reprova(BLOCO.replace("| 2 | contador |", "| 2 | outro |"), "Tipo 'outro' fora da lista")
        self.reprova(BLOCO.replace("(✔ tratado) | O aviso sobre o agendador sem o segredo foi seguido no desenho e evitou o erro. | AUTO |",
                                   "(✔ tratado) | O aviso sobre o agendador sem o segredo foi seguido no desenho e evitou o erro. | TALVEZ |"), "Recomendação 'TALVEZ' fora da lista")
        self.reprova(BLOCO.replace("| # | Tipo |", "| N | Tipo |"), "a tabela não tem o cabeçalho")
        self.reprova(BLOCO.replace("| Evidência | Em linguagem simples |", "| Prova | Em linguagem simples |"), "cabeçalho da tabela diferente")
        self.reprova(BLOCO.replace(LINHA_AUTO, "| 1 | contador | LM-020 ajudou+1 |"), "células")


class Fronteira(Base_):
    """D5 da revisão do DESIGN e F1 da revisão da fronteira: curador que escreveu não vale, nem com o bloco perfeito."""

    def test_fora_no_projeto(self):
        c = self.escreve(self.tmp, "c.txt", "FORA: /x/sdd/playbook.md\nRESULTADO: ESCRITA FORA DO PERMITIDO\n→ x\n")
        self.reprova(BLOCO, "a fronteira acusou escrita fora", comparar=c)

    def test_fronteira_nao_verificada(self):
        for nome, texto in (("vazio", ""), ("sem veredito", "MUDOU: /x\n"), ("outro veredito", "RESULTADO: x\n")):
            with self.subTest(caso=nome):
                self.reprova(BLOCO, "fronteira não verificada", comparar=self.escreve(self.tmp, "c.txt", texto))

    def test_mudou_o_brief_com_veredito_verde_passa(self):
        c = self.escreve(self.tmp, "c.txt", "MUDOU: /x/sdd/reports/briefs/BRIEF_curador_F.md\n" + VERDE)
        self.assertEqual(self.confere(comparar=c)[0], 0)

    def test_staging_mexido_depois_do_selo(self):
        with open(str(self.stg / "AVAL-AT-002.log"), "a", encoding="utf-8") as f:
            f.write("AT-009 ❌ plantada\n")
        self.reprova(BLOCO, "o staging mudou depois do selo: AVAL-AT-002.log mudou")

    def test_colheita_mexida_depois_do_selo(self):
        with open(str(self.colheita), "a", encoding="utf-8") as f:
            f.write("DELTA LM-021 ajudou+1 · conf=2026-11-05 · evidencia=DESIGN_FIXTURE.md:16\n")
        self.reprova(BLOCO, "o staging mudou depois do selo: colheita.txt mudou")

    def test_arquivo_novo_e_arquivo_sumido_no_staging(self):
        self.escreve(self.stg, "novo.log", "x\n")
        self.reprova(BLOCO, "novo.log apareceu")
        (self.stg / "novo.log").unlink()
        (self.stg / "AVAL-AT-002.log").unlink()
        self.reprova(BLOCO, "AVAL-AT-002.log sumiu")

    def test_derivado_plantado_depois_do_selo_reprova(self):
        # M4: a release só grava delta.txt depois de conferir; antes disso, quem gravou foi o curador.
        for rel in ("delta.txt", "inv-linhas.txt", "novo.md", "selo-falso.txt", "sub/x.txt"):
            with self.subTest(arquivo=rel):
                self.escreve(self.stg, rel, "LM-020 mordeu+99\n")
                self.reprova(BLOCO, "o staging mudou depois do selo")
                (self.stg / rel).unlink()

    def test_link_plantado_no_staging_reprova(self):
        os.symlink(str(self.stg / "AVAL-AT-002.log"), str(self.stg / "plantado.log"))
        self.reprova(BLOCO, "plantado.log apareceu")

    def test_selo_sem_a_colheita(self):
        self.reprova(BLOCO, "o selo não cobre a colheita.txt", selo=self.escreve(self.tmp, "s.txt", "# vazio\n"))

    def test_selar_sem_colheita_falha(self):
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        rc, out, err = self.cur("--selar", vazia)
        self.assertEqual((rc, out), (2, ""))
        self.assertIn("sele depois de colher", err)

    def test_arquivos_faltando_saem_2(self):
        b = self.escreve(self.tmp, "b.txt", BLOCO)
        for i, nome in enumerate(("colheita", "bloco", "selo", "saída do --comparar")):
            args = [self.colheita, b, BASE, self.selo, self.comparar]
            args[[0, 1, 3, 4][i]] = self.tmp / "nao-existe"
            with self.subTest(arquivo=nome):
                rc, _, err = self.cur("--conferir-bloco", *args)
                self.assertEqual(rc, 2)
                self.assertIn(nome, err)


class UniversoDasInvariantes(Sandbox):
    """D2 da revisão do DESIGN: a contagem que põe a lição entre as invariantes decide junto com a classificação."""

    def test_mordeu_com_pendencia_vira_pergunta(self):
        env = dict(self.env, SDD_TRACE="off")
        rp = FX / "replay"
        stg = self.tmp / "stg"
        stg.mkdir()
        shutil.copyfile(str(rp / "BUILD_REPORT_REPLAY.md"), str(stg / "BUILD_REPORT_REPLAY.md"))
        pb = rp / "playbook-replay.md"
        _, col, _ = self.roda([BASH, CURATOR, "--colher", stg, pb, "--inv", FX / "invariants-inv.md"], self.tmp, env)
        colheita = self.escreve(stg, "colheita.txt", col)
        _, selo, _ = self.roda([BASH, CURATOR, "--selar", stg], self.tmp, env)
        s = self.escreve(self.tmp, "selo.txt", selo)
        c = self.escreve(self.tmp, "c.txt", VERDE)
        cab = "<<<CURADORIA\n| # | Tipo | LM | Delta | Evidência | Em linguagem simples | Recomendação |\n|---|---|---|---|---|---|---|\n"
        fim = "REJEITADOS: nenhum\nNAO_JULGADO: nenhum\nIGNORADOS/JA_COLHIDOS: nenhum\nCONTAMINAÇÃO: não\n>>>\n"
        import re
        ev = dict(re.findall(r"(?m)^DELTA (LM-\d{3}) \w+\+1 .*?evidencia=(\S+)", col))
        corpo = ("| 1 | contador | LM-003 | LM-003 ajudou+1 | %s | Seguido. | AUTO |\n"
                 "| 2 | contador | LM-005 | LM-005 mordeu+1 | %s | Mordeu. | AUTO |\n"
                 "| 3 | inv | LM-005 | - [LM-005] descartado :: ferramenta | INV_PENDENTE LM-005 | Não vira regra. | ACEITAR |\n"
                 % (ev["LM-003"], ev["LM-005"]))
        b = self.escreve(self.tmp, "b.txt", cab + corpo + fim)
        rc, out, err = self.roda([BASH, CURATOR, "--conferir-bloco", colheita, b, pb, s, c], self.tmp, env)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("AUTO LM-003 ajudou+1", out)
        self.assertNotIn("AUTO LM-005", out)
        self.assertRegex(out, r"(?m)^PERGUNTA 2 contador LM-005 mordeu\+1$")
        self.assertRegex(out, r"(?m)^PERGUNTA 3 inv - \[LM-005\] descartado")
