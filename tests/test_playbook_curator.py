"""Contrato do sdd/bin/playbook-curator.sh: --preparar, --colher, --aplicar e --self-test
(DEFINE F14 AT-001 a AT-013, AT-022, AT-040, AT-041, AT-042). Os scripts rodam de verdade, por subprocess."""
from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

CURATOR = RAIZ / "sdd/bin/playbook-curator.sh"
LINT = RAIZ / "sdd/bin/playbook-lint.sh"
FX = RAIZ / "sdd/fixtures/playbook/curadoria"
BASE = FX / "playbook-base.md"

PLAYBOOK = """# P

## Sempre

- [LM-001] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `filas_de_envio` :: regra. **Do instead:** ação. · promovido_para: —
- [LM-002] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `curto` :: regra. **Do instead:** ação. · promovido_para: —

## Backend

- [LM-003] ajudou=1 mordeu=2 · conf=2026-01-01 · sup: `termo3` :: regra. **Do instead:** ação. · promovido_para: —
- [LM-004] ajudou=0 mordeu=3 · conf=2026-01-01 · sup: `termo4` :: regra. **Do instead:** ação. · promovido_para: sdd/hooks/pre-commit

## Tombstones

- [LM-009] ☠ 2026-01-01 :: aposentado
"""


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.traces = self.tmp / "traces"
        self.env = dict(self.env, SDD_TRACE_DIR=str(self.traces), TMPDIR=str(self.tmp))
        self.pb = self.escreve(self.tmp, "playbook.md", PLAYBOOK)
        self.dir = self.tmp / "stg"
        self.dir.mkdir()

    def cur(self, *args, env=None, cwd=None):
        return self.roda([BASH, CURATOR, *args], cwd or self.tmp, env)

    def colhe(self, *extra):
        return self.cur("--colher", self.dir, self.pb, *extra)

    def doc(self, nome, texto):
        return self.escreve(self.dir, nome, texto)


class TabelasDeLandmines(Base):
    """AT-001"""

    def tabela(self, celula, titulo="## Landmines aplicáveis", colunas=4):
        if colunas == 4:
            linha = "| aviso | `LM-001` | %s | como |" % celula
        else:
            linha = "| `LM-001` | %s | como |" % celula
        return "# D\n\n%s\n\n| a | b | c |\n|---|---|---|\n%s\n\n## Outra\n" % (titulo, linha)

    def test_veredito_decide_em_3_e_4_colunas_e_nas_2_secoes(self):
        for titulo in ("## Landmines aplicáveis", "## Landmines lidas no build"):
            for colunas in (3, 4):
                with self.subTest(titulo=titulo, colunas=colunas):
                    self.doc("DESIGN_F.md", self.tabela("✔ tratado", titulo, colunas))
                    rc, out, _ = self.colhe()
                    self.assertEqual(rc, 0)
                    self.assertRegex(out, r"(?m)^DELTA LM-001 ajudou\+1 · conf=\d{4}-\d\d-\d\d · evidencia=DESIGN_F\.md:\d+")
        self.doc("DESIGN_F.md", self.tabela("**mordeu**"))
        rc, out, _ = self.colhe()
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"(?m)^DELTA LM-001 mordeu\+1 ")
        self.assertNotIn("LM-001 ajudou", out)

    def test_na_e_linha_fora_da_secao_nao_contam(self):
        for celula in ("N.A.", "N/A"):
            with self.subTest(celula=celula):
                self.doc("DESIGN_F.md", self.tabela(celula))
                _, out, _ = self.colhe()
                self.assertNotIn("DELTA LM-001", out)
        self.doc("DESIGN_F.md", "# D\n\n## Outra seção\n\n| `LM-001` | ✔ tratado | x |\n")
        _, out, _ = self.colhe()
        self.assertNotIn("DELTA", out)


class Achados(Base):
    """AT-002, AT-003"""

    def test_marca_com_lm_vira_mordeu_em_cada_fonte(self):
        for nome in ("AVAL-AT-1.log", "AVAL2-x.log", "AVALIACAO_F_20261105.md", "r.yaml", "BUILD_REPORT_F.md", "HANDOFF_F.md"):
            for marca in ("❌", "NEEDS_WORK", "FAIL", "FAILED", "WAIVED", "mordeu_antes:"):
                with self.subTest(arquivo=nome, marca=marca):
                    for f in self.dir.iterdir():
                        f.unlink()
                    self.doc(nome, "linha\n%s por causa de LM-001\n" % marca)
                    rc, out, _ = self.colhe()
                    self.assertEqual(rc, 0, out)
                    self.assertIn("DELTA LM-001 mordeu+1", out)
                    self.assertIn("evidencia=%s:2" % nome, out)

    def test_linha_verde_e_palavra_dentro_de_identificador_nao_contam(self):
        for linha in ("AT-1 ✅ FAIL antes, LM-001 ok", "rodei com FORCE_FAIL=1 por LM-001", "FAIL_X de LM-001",
                      "NOT_WAIVED e LM-001"):
            with self.subTest(linha=linha):
                self.doc("AVAL-1.log", linha + "\n")
                _, out, _ = self.colhe()
                self.assertNotIn("DELTA LM-001", out)

    def test_arquivo_de_outro_nome_nao_e_fonte(self):
        self.doc("notas.md", "❌ LM-001\n")
        rc, out, _ = self.colhe()
        self.assertNotIn("DELTA", out)
        self.assertEqual(rc, 0, "LM-003 ainda pede promoção")

    def test_linha_de_tabela_de_landmines_nao_conta_como_achado(self):
        self.doc("BUILD_REPORT_F.md", "# B\n\n## Landmines lidas no build\n\n| `LM-001` | ✔ tratado | FAIL antes do conserto |\n")
        _, out, _ = self.colhe()
        self.assertIn("DELTA LM-001 ajudou+1", out)
        self.assertNotIn("LM-001 mordeu", out)

    def test_sugestao_por_termo_de_sup_nunca_vira_delta(self):
        self.doc("AVAL-1.log", "x\n❌ a filas_de_envio ficou parada\n")
        rc, out, _ = self.colhe()
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"(?m)^SUGESTAO mordeu\? LM-001 — termo `filas_de_envio` em AVAL-1\.log:2 ")
        self.assertNotIn("DELTA LM-001", out)

    def test_termo_curto_ou_so_digitos_nao_sugere(self):
        pb = self.escreve(self.tmp, "p2.md", PLAYBOOK.replace("`curto`", "`123456`"))
        self.doc("AVAL-1.log", "❌ curto 123456\n")
        _, out, _ = self.cur("--colher", self.dir, pb)
        self.assertNotIn("SUGESTAO", out)
        _, out, _ = self.colhe()
        self.assertNotIn("SUGESTAO", out)


class Candidatos(Base):
    """AT-004, AT-005, AT-010"""

    def bloco(self, *linhas):
        return "<<<CANDIDATO_PLAYBOOK\n" + "\n".join(linhas) + "\n>>>\n"

    def test_candidato_com_chave_propria_e_continuacao_numa_linha_so(self):
        self.doc("BUILD_REPORT_F.md", self.bloco("secao: Backend", "sup: `a` `b`", "regra: Parte um", "  parte dois.",
                                                 "evidencia: x.log:1", "Do instead: faça", "  isto."))
        rc, out, _ = self.colhe()
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"(?m)^CANDIDATO #1 → LM-010 · secao=Backend · sup=`a` `b` · evidencia=x\.log:1 ")
        self.assertIn("   delta: ADD Backend :: sup: `a` `b` :: Parte um parte dois. **Do instead:** faça isto. → ficha: — · promovido_para: —", out)

    def test_o_proximo_id_passa_do_tombstone_e_numera_em_sequencia(self):
        ok = self.bloco("secao: Backend", "sup: `a`", "regra: r. **Do instead:** x.", "evidencia: e")
        self.doc("BUILD_REPORT_F.md", ok + ok)
        _, out, _ = self.colhe()
        # o 2º é igual ao 1º: a impressão digital é a mesma, mas ainda não foi julgado; os 2 aparecem
        self.assertIn("CANDIDATO #1 → LM-010", out)
        self.assertIn("CANDIDATO #2 → LM-011", out)

    def test_cada_motivo_de_rejeicao(self):
        casos = {
            "sem linha 'evidencia:'": ("secao: Backend", "sup: `a`", "regra: r. **Do instead:** x."),
            "não é uma das seções ativas": ("secao: Inventada", "sup: `a`", "regra: r. **Do instead:** x.", "evidencia: e"),
            "sup: sem termo em crase": ("secao: Backend", "sup: a", "regra: r. **Do instead:** x.", "evidencia: e"),
            "regra: sem 'Do instead:'": ("secao: Backend", "sup: `a`", "regra: r.", "evidencia: e"),
        }
        for motivo, linhas in casos.items():
            with self.subTest(motivo=motivo):
                self.doc("BUILD_REPORT_F.md", "# B\n\n" + self.bloco(*linhas))
                rc, out, _ = self.colhe()
                self.assertEqual(rc, 0, "REJEITADO é o que relatar: a pessoa precisa saber")
                self.assertRegex(out, r"(?m)^REJEITADO candidato em BUILD_REPORT_F\.md:\d+ — .*" + re.escape(motivo))
                self.assertNotIn("CANDIDATO #", out)

    def test_tombstones_nao_e_secao_de_candidato(self):
        self.doc("BUILD_REPORT_F.md", self.bloco("secao: Tombstones", "sup: `a`", "regra: r. **Do instead:** x.", "evidencia: e"))
        _, out, _ = self.colhe()
        self.assertIn("não é uma das seções ativas", out)

    def test_playbook_sections_troca_a_lista(self):
        self.doc("BUILD_REPORT_F.md", self.bloco("secao: Banco", "sup: `a`", "regra: r. **Do instead:** x.", "evidencia: e"))
        _, out, _ = self.colhe()
        self.assertIn("REJEITADO", out)
        _, out, _ = self.cur("--colher", self.dir, self.pb, env=dict(self.env, PLAYBOOK_SECTIONS="Sempre|Banco|Tombstones"))
        self.assertIn("CANDIDATO #1", out)

    def test_o_default_de_secoes_e_igual_ao_do_lint(self):
        padrao = re.compile(r"Sempre\|[^\"'}]*Tombstones")
        self.assertEqual(padrao.search(LINT.read_text(encoding="utf-8")).group(0),
                         padrao.search(CURATOR.read_text(encoding="utf-8")).group(0))


class Promocao(Base):
    """AT-006, AT-007"""

    def test_so_mordeu_2_sem_mecanismo_e_com_pasta_vazia(self):
        rc, out, _ = self.colhe()
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"(?m)^PROMOVER\? LM-003 mordeu=2 ")
        self.assertIn("hook em sdd/hooks/", out)
        self.assertIn("release.landmines_cmd", out)
        self.assertIn("Verify Gate", out)
        self.assertNotIn("PROMOVER? LM-004", out)
        self.assertNotIn("PROMOVER? LM-001", out)

    def test_bullet_sem_o_campo_conta_como_nao_promovido(self):
        pb = self.escreve(self.tmp, "p3.md", PLAYBOOK.replace(
            "`termo3` :: regra. **Do instead:** ação. · promovido_para: —", "`termo3` :: regra. **Do instead:** ação."))
        _, out, _ = self.cur("--colher", self.dir, pb)
        self.assertIn("PROMOVER? LM-003", out)

    def test_caminho_entre_crases_e_mecanismo(self):
        pb = self.escreve(self.tmp, "p4.md", PLAYBOOK.replace(
            "`termo3` :: regra. **Do instead:** ação. · promovido_para: —",
            "`termo3` :: regra. **Do instead:** ação. · promovido_para: `sdd/hooks/x`"))
        _, out, _ = self.cur("--colher", self.dir, pb)
        self.assertNotIn("PROMOVER? LM-003", out)


class Saidas(Base):
    """AT-007, AT-040: exit e resumo"""

    def semrisco(self):
        return self.escreve(self.tmp, "calmo.md", PLAYBOOK.replace("mordeu=2", "mordeu=1"))

    def test_nada_de_nenhum_tipo_sai_1(self):
        rc, out, err = self.cur("--colher", self.dir, self.semrisco())
        self.assertEqual(rc, 1, out + err)
        self.assertIn("0 deltas colhidos", err)
        self.assertRegex(out, r"(?m)^resumo: deltas=0 \(ajudou=0 mordeu=0\) candidatos=0 rejeitados=0 promocoes=0 sugestoes=0$")
        self.assertIn("RESULTADO: NADA A COLHER", out)

    def test_cada_tipo_sozinho_sai_0_porque_alguem_precisa_saber(self):
        casos = {
            "AVAL-1.log": "❌ filas_de_envio\n",                                    # só sugestão
            "BUILD_REPORT_F.md": "<<<CANDIDATO_PLAYBOOK\nsecao: Backend\n>>>\n",    # só rejeitado
            "AVAL-2.log": "❌ LM-777\n",                                             # só ignorado
        }
        for nome, texto in casos.items():
            with self.subTest(arquivo=nome):
                for f in self.dir.iterdir():
                    f.unlink()
                self.doc(nome, texto)
                rc, out, _ = self.cur("--colher", self.dir, self.semrisco())
                self.assertEqual(rc, 0, out)
                self.assertIn("RESULTADO: HÁ O QUE JULGAR", out)

    def test_falha_nunca_e_nada_a_colher(self):
        vazio = self.escreve(self.tmp, "vazio.md", "# sem bullet\n")
        for pb, motivo in ((self.tmp / "nao-existe.md", "não encontrado"), (vazio, "nenhum bullet")):
            with self.subTest(motivo=motivo):
                rc, out, err = self.cur("--colher", self.dir, pb)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(motivo, err)
                self.assertNotIn("NADA A COLHER", out + err)
                self.assertIn("RESULTADO:", err)
        rc, out, err = self.colhe("--inv", self.tmp / "nao-existe.md")
        self.assertEqual(rc, 2)
        self.assertIn("invariantes não encontradas", err)

    def test_uso_sai_64_com_resultado(self):
        for args in (["--colher"], ["--colher", self.tmp / "nao-existe", self.pb], ["--colher", self.dir, self.pb, "--nada"],
                     ["--colher", self.dir, self.pb, "--desde", "ontem"], ["--nada"], [], ["--aplicar", "x"],
                     ["--cruzar", "x"], ["--validar-inv", "x"], ["--conferir-bloco", "x"], ["--selar"],
                     ["--preparar"], ["--preparar", "../x"], ["--self-test", "x"]):
            with self.subTest(args=args):
                rc, out, err = self.cur(*args)
                self.assertEqual(rc, 64, out + err)
                self.assertEqual(out, "")
                self.assertIn("RESULTADO: ERRO DE USO", err)
                self.assertIn("→ ", err)

    def test_resultado_e_seta_sao_o_fim_do_stdout_e_o_resumo_vem_antes(self):
        _, out, _ = self.colhe()
        linhas = out.strip().split("\n")
        self.assertTrue(linhas[-1].startswith("→ "))
        self.assertTrue(linhas[-2].startswith("RESULTADO: "))
        self.assertTrue(linhas[-3].startswith("resumo: "))

    def test_um_delta_por_id_e_tipo_e_ignorado_uma_vez(self):
        self.doc("AVAL-1.log", "❌ LM-001\n❌ LM-001 de novo\n❌ LM-777\n❌ LM-777 de novo\n❌ LM-009\n")
        _, out, _ = self.colhe()
        self.assertEqual(out.count("DELTA LM-001 mordeu+1"), 1)
        self.assertEqual(out.count("IGNORADO LM-777"), 1)
        self.assertEqual(out.count("IGNORADO LM-009"), 1, "tombstone não recebe contagem")


class LinhasQueNaoSaoAchado(Base):
    """L1 do avaliador, ciclo 1"""

    def test_id_dentro_de_outra_palavra_nao_conta(self):
        for linha in ("❌ FILM-001", "❌ HELM-001", "❌ LM-0019", "❌ X_LM-001"):
            with self.subTest(linha=linha):
                self.doc("AVAL-1.log", linha + "\n")
                self.assertNotIn("LM-001", self.colhe()[1].replace("PROMOVER? LM-003", ""))

    def test_fail_composto_nao_e_achado(self):
        self.doc("AVAL-1.log", "FAIL-FAST ligado para LM-001\n")
        self.assertNotIn("DELTA LM-001", self.colhe()[1])

    def test_nota_depois_do_veredito_nao_recebe_contagem(self):
        self.doc("DESIGN_F.md", "## Landmines aplicáveis\n\n| `LM-001` | ✔ tratado | vizinha da LM-002 |\n")
        out = self.colhe()[1]
        self.assertIn("DELTA LM-001 ajudou+1", out)
        self.assertNotIn("DELTA LM-002", out)

    def test_id_na_propria_celula_do_veredito_vale_quando_nao_ha_outro(self):
        self.doc("DESIGN_F.md", "## Landmines aplicáveis\n\n| ✔ tratado LM-001 | x |\n")
        self.assertIn("DELTA LM-001 ajudou+1", self.colhe()[1])

    def test_frase_de_regra_que_comeca_com_mordeu_nao_e_veredito(self):
        self.doc("DESIGN_F.md", "## Landmines aplicáveis\n\n| mordeu quando o agendador caiu de madrugada | `LM-001` | ✔ tratado |\n")
        out = self.colhe()[1]
        self.assertIn("DELTA LM-001 ajudou+1", out)
        self.assertNotIn("LM-001 mordeu", out)


class Desde(Base):
    """AT-008"""

    def test_documento_anterior_vira_ja_colhido(self):
        self.doc("BUILD_REPORT_F.md", "| **Date** | 2026-09-02 |\n\n## Landmines lidas no build\n\n| `LM-001` | ✔ x | y |\n")
        self.doc("DESIGN_F.md", "| **Date** | 2026-09-02 |\n\n## Landmines aplicáveis\n\n| `LM-002` | ✔ x | y |\n")
        _, out, _ = self.colhe("--desde", "2026-09-03")
        self.assertIn("JA_COLHIDO BUILD_REPORT_F.md", out)
        self.assertIn("JA_COLHIDO DESIGN_F.md", out)
        self.assertNotIn("DELTA", out)
        _, out, _ = self.colhe("--desde", "2026-09-02")
        self.assertIn("DELTA LM-001 ajudou+1", out)
        self.assertIn("DELTA LM-002 ajudou+1", out)


class JaJulgado(Base):
    """Decisão da revisão do DESIGN (D4): a mesma linha não conta 2 vezes em 2 releases da mesma feature."""

    def test_o_registro_tira_so_o_que_ja_foi_julgado(self):
        self.doc("r1.yaml", "WAIVED por LM-001\n")
        _, primeira, _ = self.colhe()
        self.assertIn("DELTA LM-001 mordeu+1", primeira)
        self.doc("CURATOR-colhidos.txt", "\n".join(ln for ln in primeira.split("\n") if " · fp=" in ln) + "\n")
        self.doc("r2.yaml", "WAIVED de novo, outro achado, LM-002\n")
        rc, out, _ = self.colhe()
        self.assertEqual(rc, 0)
        self.assertNotIn("DELTA LM-001", out)
        self.assertIn("DELTA LM-002 mordeu+1", out)
        self.assertRegex(out, r"(?m)^JA_JULGADO 1 linha")

    def test_mesmo_texto_noutra_linha_continua_julgado_e_texto_novo_conta(self):
        self.doc("r1.yaml", "WAIVED por LM-001\n")
        _, primeira, _ = self.colhe()
        self.doc("CURATOR-colhidos.txt", "\n".join(ln for ln in primeira.split("\n") if " · fp=" in ln) + "\n")
        self.doc("r1.yaml", "\n\nWAIVED por LM-001\n")
        self.assertNotIn("DELTA LM-001", self.colhe()[1])
        self.doc("r1.yaml", "WAIVED por LM-001, com motivo novo\n")
        self.assertIn("DELTA LM-001 mordeu+1", self.colhe()[1])

    def registra(self, saida):
        self.doc("CURATOR-colhidos.txt", "\n".join(ln for ln in saida.split("\n") if " · fp=" in ln) + "\n")

    def test_2_linhas_da_mesma_licao_nao_contam_em_2_releases(self):
        # H3 do avaliador: DESIGN e BUILD_REPORT citando a mesma lição é o caso normal.
        tab = "## Landmines aplicáveis\n\n| `LM-001` | ✔ %s | x |\n"
        self.doc("DESIGN_F.md", tab % "no desenho")
        self.doc("BUILD_REPORT_F.md", tab.replace("aplicáveis", "lidas no build") % "no build")
        primeira = self.colhe()[1]
        self.assertEqual(primeira.count("DELTA LM-001 ajudou+1"), 1)
        self.assertRegex(primeira, r"fp=[0-9a-f]{10},[0-9a-f]{10}")
        self.registra(primeira)
        segunda = self.colhe()[1]
        self.assertNotIn("DELTA LM-001", segunda)
        self.assertRegex(segunda, r"(?m)^JA_JULGADO 2 linha")

    def test_sugestao_ja_julgada_nao_volta_e_achado_novo_volta(self):
        self.doc("AVAL-1.log", "❌ a filas_de_envio parou\n❌ de novo filas_de_envio\n")
        primeira = self.colhe()[1]
        self.assertIn("SUGESTAO mordeu? LM-001", primeira)
        self.registra(primeira)
        self.assertNotIn("SUGESTAO", self.colhe()[1])
        self.doc("AVAL-2.log", "❌ outra filas_de_envio\n")
        self.assertIn("SUGESTAO mordeu? LM-001", self.colhe()[1])

    def test_candidato_ja_julgado_nao_volta(self):
        ok = "<<<CANDIDATO_PLAYBOOK\nsecao: Backend\nsup: `a`\nregra: r. **Do instead:** x.\nevidencia: e\n>>>\n"
        ruim = "<<<CANDIDATO_PLAYBOOK\nsecao: Backend\n>>>\n"
        self.doc("BUILD_REPORT_F.md", ok + ruim)
        primeira = self.colhe()[1]
        self.assertIn("CANDIDATO #1", primeira)
        self.assertIn("REJEITADO", primeira)
        self.registra(primeira)
        segunda = self.colhe()[1]
        self.assertNotIn("CANDIDATO #", segunda)
        self.assertNotIn("REJEITADO", segunda)

    def test_sem_registro_nada_muda(self):
        self.doc("r1.yaml", "WAIVED por LM-001\n")
        out = self.colhe()[1]
        self.assertNotIn("JA_JULGADO", out)
        self.assertIn("DELTA LM-001", out)


class Trace(Base):
    """AT-009"""

    def test_linha_jsonl_por_feature(self):
        self.doc("BUILD_REPORT_FEAT_A.md", "x\n")
        self.doc("DESIGN_FEAT_A.md", "x\n")
        self.doc("DESIGN_FEAT_B.md", "x\n")
        rc, _, _ = self.colhe()
        self.assertEqual(sorted(p.name for p in self.traces.iterdir()), ["FEAT_A.jsonl", "FEAT_B.jsonl"])
        linhas = (self.traces / "FEAT_A.jsonl").read_text(encoding="utf-8").strip().split("\n")
        self.assertEqual(len(linhas), 1, "o mesmo nome em BUILD_REPORT e DESIGN é 1 feature")
        j = json.loads(linhas[0])
        self.assertEqual((j["feature"], j["src"], j["kind"], j["exit"]), ("FEAT_A", "curator", "colher", rc))
        for chave in ("ts", "deltas", "ajudou", "mordeu", "candidatos", "rejeitados", "promocoes", "sugestoes"):
            self.assertIn(chave, j)

    def test_desligado_ou_sem_documento_nao_grava(self):
        self.doc("DESIGN_F.md", "x\n")
        self.cur("--colher", self.dir, self.pb, env=dict(self.env, SDD_TRACE="off"))
        self.assertFalse(self.traces.exists())
        (self.dir / "DESIGN_F.md").unlink()
        self.colhe()
        self.assertFalse(self.traces.exists())

    def test_nome_esquisito_e_sanitizado(self):
        self.doc('DESIGN_qu"o te.md', "x\n")
        self.colhe()
        json.loads((self.traces / "qu_o_te.jsonl").read_text(encoding="utf-8"))

    def test_nome_com_ponto_no_inicio_nao_vira_arquivo_oculto(self):
        self.doc("DESIGN_.x.md", "x\n")
        self.colhe()
        self.assertEqual([p.name for p in self.traces.iterdir()], ["_.x.jsonl"])

    def test_trace_que_nao_grava_nao_muda_o_exit(self):
        self.doc("AVAL-1.log", "❌ LM-001\n")
        self.doc("DESIGN_F.md", "x\n")
        ocupado = self.escreve(self.tmp, "arquivo", "x")
        rc, out, _ = self.cur("--colher", self.dir, self.pb, env=dict(self.env, SDD_TRACE_DIR=str(ocupado)))
        self.assertEqual(rc, 0, out)


class Aplicar(Base):
    """AT-011, AT-012, AT-013"""

    def aplica(self, delta, *extra):
        return self.cur("--aplicar", self.escreve(self.tmp, "d.txt", delta), self.pb, *extra)

    def test_cada_verbo(self):
        rc, out, err = self.aplica(
            "# comentário\nLM-001 ajudou+2\nLM-002 mordeu+1\nLM-003 promovido_para=sdd/hooks/x\n"
            "ADD Backend :: sup: `n` :: Nova. **Do instead:** y.\nADD Sempre :: sup: `m` :: Outra. **Do instead:** z. → ficha: F · promovido_para: —\n"
            "TOMBSTONE LM-004 :: saiu\nREFINE LM-001 :: Texto novo. **Do instead:** w.\n", "conf=2026-02-02")
        self.assertEqual(rc, 0, err)
        self.assertIn("- [LM-001] ajudou=2 mordeu=0 · conf=2026-02-02 · sup: `filas_de_envio` :: Texto novo. **Do instead:** w. · promovido_para: —", out)
        self.assertIn("- [LM-002] ajudou=0 mordeu=1 · conf=2026-02-02", out)
        self.assertRegex(out, r"(?m)^- \[LM-003\] ajudou=1 mordeu=2 · conf=2026-02-02 .*promovido_para: sdd/hooks/x$")
        self.assertIn("- [LM-010] ajudou=0 mordeu=0 · conf=2026-02-02 · sup: `n` :: Nova. **Do instead:** y. · promovido_para: —", out)
        self.assertIn("- [LM-011] ajudou=0 mordeu=0 · conf=2026-02-02 · sup: `m` :: Outra.", out)
        self.assertIn("- [LM-004] ☠ 2026-02-02 :: saiu", out)
        self.assertNotIn("- [LM-004] ajudou", out)
        self.assertLess(out.index("[LM-011]"), out.index("## Backend"), "o ADD fica no fim da seção dele")
        self.assertLess(out.index("[LM-010]"), out.index("## Tombstones"))
        self.assertGreater(out.index("[LM-004] ☠"), out.index("## Tombstones"))
        saida = self.escreve(self.tmp, "novo.md", out)
        r = self.repo("lint")
        rc, o, e = self.roda([BASH, LINT, saida], r)
        self.assertEqual(rc, 0, o + e)

    def test_stdout_e_so_o_playbook(self):
        rc, out, err = self.aplica("LM-001 ajudou+1\n")
        self.assertEqual(rc, 0)
        self.assertNotIn("RESULTADO:", out)
        self.assertNotIn("→ ", out.replace("→ ficha", ""))
        self.assertIn("RESULTADO: DELTA APLICADO", err)
        self.assertIn("→ ", err)

    def test_so_contagem_nao_mexe_em_mais_nada(self):
        _, out, _ = self.aplica("LM-001 ajudou+1\n", "2026-01-01")
        self.assertEqual(out, PLAYBOOK.replace("[LM-001] ajudou=0", "[LM-001] ajudou=1"))

    def test_continuacao_fica_no_ativo_e_sai_com_o_aposentado(self):
        texto = PLAYBOOK.replace("`curto` :: regra. **Do instead:** ação. · promovido_para: —\n",
                                 "`curto` :: regra. **Do instead:** ação. · promovido_para: —\n  continuação de 2\n")
        pb = self.escreve(self.tmp, "c.md", texto)
        _, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "LM-002 ajudou+1\n"), pb)
        self.assertIn("  continuação de 2\n", out)
        _, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "TOMBSTONE LM-002 :: fora\n"), pb)
        self.assertNotIn("continuação de 2", out)

    def test_refine_guarda_ficha_e_promovido(self):
        pb = self.escreve(self.tmp, "r.md", PLAYBOOK.replace(
            "`termo3` :: regra. **Do instead:** ação. · promovido_para: —",
            "`termo3` :: regra. **Do instead:** ação. → ficha: HANDOFF_X · promovido_para: sdd/hooks/y"))
        _, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "REFINE LM-003 :: Novo. **Do instead:** k.\n"), pb, "2026-02-02")
        self.assertIn(":: Novo. **Do instead:** k. → ficha: HANDOFF_X · promovido_para: sdd/hooks/y", out)

    def test_promovido_para_em_bullet_sem_o_campo_acrescenta(self):
        pb = self.escreve(self.tmp, "s.md", PLAYBOOK.replace(
            "`termo3` :: regra. **Do instead:** ação. · promovido_para: —", "`termo3` :: regra. **Do instead:** ação."))
        rc, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "LM-003 promovido_para=sdd/hooks/x\n"), pb)
        self.assertEqual(rc, 0)
        self.assertRegex(out, r"(?m)^- \[LM-003\].*· promovido_para: sdd/hooks/x$")

    def test_delta_so_com_comentario_devolve_a_entrada(self):
        rc, out, err = self.aplica("# nada\n\n")
        self.assertEqual(rc, 0)
        self.assertEqual(out, PLAYBOOK)
        self.assertIn("RESULTADO: NADA A APLICAR", err)

    def test_secao_da_lista_que_falta_nasce_no_lugar_certo(self):
        # H4: o playbook do pacote só tem Sempre e Tombstones, e a colheita aceita as outras seções da lista.
        rc, out, err = self.aplica("ADD Dados :: sup: `d` :: R. **Do instead:** a.\nADD Domínio :: sup: `e` :: R. **Do instead:** b.\n")
        self.assertEqual(rc, 0, err)
        posicoes = [out.index(t) for t in ("## Sempre", "## Dados", "[LM-010]", "## Backend", "## Domínio", "[LM-011]", "## Tombstones")]
        self.assertEqual(posicoes, sorted(posicoes))
        saida = self.escreve(self.tmp, "novo.md", out)
        rc, o, e = self.roda([BASH, LINT, saida], self.repo("lint"))
        self.assertEqual(rc, 0, o + e)

    def test_promovido_na_continuacao_e_lido_e_trocado_la(self):
        # M1: o lint aceita o campo na linha de continuação.
        texto = PLAYBOOK.replace("`termo3` :: regra. **Do instead:** ação. · promovido_para: —\n",
                                 "`termo3` :: regra longa\n  e continua. **Do instead:** ação. · promovido_para: `sdd/hooks/a`\n")
        pb = self.escreve(self.tmp, "c.md", texto)
        self.assertNotIn("PROMOVER? LM-003", self.cur("--colher", self.dir, pb)[1])
        rc, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "LM-003 promovido_para=sdd/hooks/b\n"), pb)
        self.assertEqual(rc, 0)
        self.assertEqual(out.count("promovido_para: sdd/hooks/b"), 1)
        self.assertNotIn("sdd/hooks/a", out)
        linha = next(l for l in out.split("\n") if l.startswith("- [LM-003]"))
        self.assertNotIn("promovido_para", linha)

    def test_delta_so_com_comentario_preserva_os_bytes(self):
        pb = self.tmp / "crlf.md"
        bruto = PLAYBOOK.replace("\n", "\r\n").encode("utf-8") + b"\xff\r\n"
        pb.write_bytes(bruto)
        d = self.escreve(self.tmp, "d.txt", "# nada\n")
        import subprocess
        r = subprocess.run([BASH, str(CURATOR), "--aplicar", str(d), str(pb)], cwd=str(self.tmp), env=self.env, capture_output=True)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, bruto)

    def test_data_impossivel_sai_64(self):
        self.assertEqual(self.aplica("LM-001 ajudou+1\n", "conf=2026-99-99")[0], 64)
        self.assertEqual(self.colhe("--desde", "2026-13-45")[0], 64)

    def test_invalido_sai_2_com_stdout_vazio_e_todos_os_erros_com_a_linha(self):
        rc, out, err = self.aplica("LM-001 ajudou+1\nLM-999 ajudou+1\n# c\nLM-009 ajudou+1\n"
                                   "ADD Inventada :: sup: `x` :: r. **Do instead:** y.\nADD Tombstones :: sup: `x` :: r. **Do instead:** y.\n"
                                   "ADD Backend :: sup: `x` :: sem a ação\nREFINE LM-001 :: sem a ação\nLM-001 ajudou++\n")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "", "nada a copiar")
        for trecho in ("delta linha 2: LM-999", "delta linha 4: LM-009", "delta linha 5: ADD em seção fora da lista",
                       "delta linha 6: ADD em Tombstones", "delta linha 7: ADD sem 'Do instead:'",
                       "delta linha 8: REFINE sem 'Do instead:'", "delta linha 9: linha fora da gramática"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, err)
        self.assertIn("RESULTADO: DELTA INVÁLIDO", err)

    def test_aposentar_e_alterar_o_mesmo_id_e_invalido(self):
        rc, out, err = self.aplica("TOMBSTONE LM-001 :: x\nLM-001 ajudou+1\n")
        self.assertEqual(rc, 2)
        self.assertEqual(out, "")
        self.assertIn("aposentado e alterado", err)

    def test_arquivos_ausentes_e_conf_invalida(self):
        rc, out, _ = self.cur("--aplicar", self.tmp / "nao", self.pb)
        self.assertEqual((rc, out), (2, ""))
        rc, out, _ = self.cur("--aplicar", self.escreve(self.tmp, "d.txt", "LM-001 ajudou+1\n"), self.tmp / "nao")
        self.assertEqual((rc, out), (2, ""))
        rc, out, _ = self.aplica("LM-001 ajudou+1\n", "conf=ontem")
        self.assertEqual((rc, out), (64, ""))

    def test_so_contagem_atravessa_o_anti_collapse(self):
        _, out, _ = self.aplica("LM-001 ajudou+3\nLM-002 mordeu+2\nLM-003 ajudou+1\n")
        novo = self.escreve(self.tmp, "n.md", out)
        rc, o, e = self.roda([BASH, LINT, "--anti-collapse", self.pb, novo], self.repo("lint"))
        self.assertEqual(rc, 0, o + e)
        self.assertIn("0 (0%)", o)


class PisoDoAntiCollapse(Base):
    """AT-042"""

    def compara(self, depois):
        novo = self.escreve(self.tmp, "n.md", depois)
        rc, o, e = self.roda([BASH, LINT, "--anti-collapse", self.pb, novo], self.repo("lint" + str(len(depois))))
        return rc, o + e

    def test_um_alterado_passa_em_playbook_pequeno(self):
        # 3 bullets: 1 alterado são 33%, acima do limite de 20%. Com 5, os 20% passariam com ou sem o piso.
        pequeno = re.sub(r"- \[LM-00[34]\].*\n", "", PLAYBOOK)
        self.pb = self.escreve(self.tmp, "pequeno.md", pequeno)
        rc, out = self.compara(pequeno.replace("`curto` :: regra.", "`curto` :: regra nova."))
        self.assertEqual(rc, 0, out)

    def test_dois_alterados_acima_do_limite_bloqueiam(self):
        rc, out = self.compara(PLAYBOOK.replace("`curto` :: regra.", "`curto` :: nova.").replace("`termo3` :: regra.", "`termo3` :: nova."))
        self.assertEqual(rc, 1, out)

    def test_sumico_de_id_continua_bloqueando_com_1(self):
        rc, out = self.compara(re.sub(r"- \[LM-002\].*\n", "", PLAYBOOK))
        self.assertEqual(rc, 1, out)
        self.assertIn("DESAPARECERAM", out)


class Preparar(Sandbox):
    """AT-041 e D7, D8, D13 da revisão do DESIGN"""

    def setUp(self):
        super().setUp()
        self.temp = self.tmp / "temp"
        self.temp.mkdir()
        self.env = dict(self.env, TMPDIR=str(self.temp))
        self.r = self.repo()

    def prep(self, *args):
        return self.roda([BASH, CURATOR, "--preparar", *args], self.r)

    def staging(self, out) -> Path:
        return Path(re.search(r"(?m)^staging: (.+)$", out).group(1))

    def povoa(self):
        for rel in ("sdd/features/DESIGN_F_A.md", "sdd/features/DESIGN_F_A_LONGO.md", "sdd/reports/BUILD_REPORT_F_A.md",
                    "sdd/reports/BUILD_REPORT_F_A_LONGO.md", "sdd/reports/evidence/F_A/AVAL-1.log",
                    "sdd/reports/evidence/F_A/AVAL2-x.log", "sdd/reports/evidence/F_A/outro.log",
                    "sdd/reports/evidence/F_A_LONGO/AVAL-9.log", "sdd/reviews/AVALIACAO_F_A_20261105.md",
                    "sdd/reviews/AVALIACAO_F_A_LONGO_20261105.md", "sdd/releases/F_A/s1.yaml", "sdd/handoffs/HANDOFF_F_A.md",
                    "sdd/handoffs/HANDOFF_F_A_LONGO.md"):
            self.escreve(self.r, rel, "x\n")

    def test_copia_so_a_feature_e_nao_toca_nos_originais(self):
        self.povoa()
        rc, out, err = self.prep("F_A")
        self.assertEqual(rc, 0, out + err)
        s = self.staging(out)
        self.assertEqual(sorted(p.name for p in s.iterdir()),
                         sorted(["DESIGN_F_A.md", "BUILD_REPORT_F_A.md", "AVAL-1.log", "AVAL2-x.log",
                                 "AVALIACAO_F_A_20261105.md", "s1.yaml", "HANDOFF_F_A.md"]))
        self.assertTrue((self.r / "sdd/features/DESIGN_F_A.md").is_file())
        self.assertIn("RESULTADO: STAGING PRONTO (7 arquivo(s))", out)
        self.assertTrue(str(s).startswith(str(self.temp.resolve())) or str(s).startswith(str(self.temp)))

    def test_o_nome_da_pasta_se_refaz_igual_e_depende_da_raiz(self):
        self.povoa()
        a = self.staging(self.prep("F_A")[1])
        self.assertEqual(a, self.staging(self.prep("F_A")[1]))
        outro = self.repo("outro")
        b = self.staging(self.roda([BASH, CURATOR, "--preparar", "F_A"], outro)[1])
        self.assertNotEqual(a, b)

    def test_link_nao_e_copiado(self):
        self.povoa()
        fora = self.escreve(self.tmp, "fora.md", "segredo\n")
        (self.r / "sdd/features/DESIGN_F_A.md").unlink()
        os.symlink(str(fora), str(self.r / "sdd/features/DESIGN_F_A.md"))
        _, out, _ = self.prep("F_A")
        self.assertIn("ignorado (link", out)
        self.assertFalse((self.staging(out) / "DESIGN_F_A.md").exists())

    def test_procura_no_archive_e_sem_documento_sai_1(self):
        rc, out, _ = self.prep("F_A")
        self.assertEqual(rc, 1, "sem DESIGN nem BUILD_REPORT não é '0 deltas'")
        self.assertIn("RESULTADO: STAGING SEM DOCUMENTOS", out)
        self.escreve(self.r, "sdd/archive/F_A/DESIGN_F_A.md", "x\n")
        rc, out, _ = self.prep("F_A")
        self.assertEqual(rc, 0)
        self.assertTrue((self.staging(out) / "DESIGN_F_A.md").is_file())

    def test_release_seguinte_limpa_o_que_sobrou_e_retomar_nao_mexe(self):
        self.povoa()
        s = self.staging(self.prep("F_A")[1])
        (s / "colheita.txt").write_text("velha\n", encoding="utf-8")
        rc, out, _ = self.prep("F_A", "--retomar")
        self.assertEqual(rc, 0)
        self.assertIn("RETOMADA: colheita anterior encontrada", out)
        self.assertTrue((s / "colheita.txt").is_file())
        self.prep("F_A")
        self.assertFalse((s / "colheita.txt").exists())
        rc, out, _ = self.prep("F_A", "--retomar")
        self.assertEqual(rc, 1)
        self.assertIn("RESULTADO: NADA A RETOMAR", out)

    def test_o_de_sdd_vence_o_do_archive(self):
        self.escreve(self.r, "sdd/features/DESIGN_F_A.md", "vivo\n")
        self.escreve(self.r, "sdd/archive/F_A/DESIGN_F_A.md", "arquivado\n")
        s = self.staging(self.prep("F_A")[1])
        self.assertEqual((s / "DESIGN_F_A.md").read_text(encoding="utf-8"), "vivo\n")

    def test_pasta_de_evidencia_que_e_link_nao_e_seguida(self):
        self.povoa()
        fora = self.tmp / "fora"
        fora.mkdir()
        self.escreve(fora, "AVAL-plantado.log", "x\n")
        e = self.r / "sdd/reports/evidence/F_A"
        for f in e.iterdir():
            f.unlink()
        e.rmdir()
        os.symlink(str(fora), str(e))
        _, out, _ = self.prep("F_A")
        self.assertIn("ignorado (link", out)
        self.assertFalse((self.staging(out) / "AVAL-plantado.log").exists())

    def test_staging_ou_pasta_pai_que_e_link_recusa(self):
        self.povoa()
        s = self.staging(self.prep("F_A")[1])
        alvo = self.tmp / "alvo"
        alvo.mkdir()
        shutil.rmtree(str(s))
        os.symlink(str(alvo), str(s))
        rc, out, err = self.prep("F_A")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("é um link", err)
        self.assertEqual(list(alvo.iterdir()), [])

    def test_limpa_subpasta_da_release_anterior(self):
        self.povoa()
        s = self.staging(self.prep("F_A")[1])
        (s / "sobra").mkdir()
        self.escreve(s, "sobra/x.txt", "x\n")
        self.prep("F_A")
        self.assertFalse((s / "sobra").exists())

    def test_nome_invalido_sai_64(self):
        for nome in ("../x", "a/b", ".x", "v2.6", "á", ""):
            with self.subTest(nome=nome):
                rc, out, err = self.prep(nome)
                self.assertEqual(rc, 64, out + err)
                self.assertNotIn("staging:", out)

    def test_o_alfabeto_e_o_do_despachar(self):
        brief = self.escreve(self.tmp, "b.md", "x\n")
        for args, rc_esperado in ((("v2.6",), 64), (("F-a_1",), 1)):
            with self.subTest(args=args):
                self.assertEqual(self.prep(*args)[0], rc_esperado)
                rc, _, _ = self.roda([BASH, RAIZ / "sdd/bin/sdd-fluxo.sh", "despachar", "curador", args[0], brief], self.r)
                self.assertEqual(rc, 64 if rc_esperado == 64 else 40)


class SelfTest(Sandbox):
    """AT-022"""

    def test_verde_vermelhos_antes_e_sem_residuo(self):
        r = self.repo()
        rc, out, err = self.roda([BASH, CURATOR, "--self-test"], r)
        self.assertEqual(rc, 0, out + err)
        self.assertLess(out.index("VERMELHOS"), out.index("VERDES"))
        self.assertIn("RESULTADO: SELF-TEST OK", out)
        self.assertEqual(self.git(r, "status", "--porcelain"), "")
        self.assertFalse((r / "sdd").exists())

    def test_fixtures_ausentes_saem_2_dizendo_o_que_falta(self):
        rc, out, err = self.roda([BASH, CURATOR, "--self-test"], self.repo(),
                                 dict(self.env, PLAYBOOK_CURATOR_FIXTURES=str(self.tmp / "nao")))
        self.assertEqual(rc, 2)
        self.assertIn("fixture ausente", err)
        self.assertIn("RESULTADO: SELF-TEST FALHOU", out)


class SelfTestSemGit(Sandbox):
    """H1 do avaliador: o Verify Gate roda numa cópia sem .git, e só ali o self-test falhava."""

    def test_roda_numa_copia_sem_repositorio(self):
        copia = self.tmp / "copia"
        for rel in ("sdd/bin/playbook-curator.sh", "sdd/bin/playbook-lint.sh", "sdd/fixtures/playbook/curadoria"):
            self.copia(rel, copia)
        rc, out, err = self.roda([BASH, copia / "sdd/bin/playbook-curator.sh", "--self-test"], copia)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: SELF-TEST OK", out)

    def test_o_bloqueio_do_anti_collapse_nao_aceita_outro_erro_do_lint(self):
        # Antes, qualquer exit ≠ 0 do lint (até "não é um repo git") contava como "bloqueou".
        self.assertIn('rc == 1 and "reescritos" in saida', CURATOR.read_text(encoding="utf-8"))


class Fixtures(Base):
    """O critério de pronto do plano: os 4 tipos de linha sobre as fixtures do pacote."""

    def test_os_4_tipos(self):
        _, out, _ = self.cur("--colher", FX, BASE)
        for inicio in ("DELTA ", "CANDIDATO #", "REJEITADO ", "SUGESTAO ", "PROMOVER? "):
            with self.subTest(inicio=inicio):
                self.assertRegex(out, "(?m)^" + re.escape(inicio))

    def test_nada_especifico_do_projeto_de_origem(self):
        proibido = re.compile(r"supabase|deno|wordpress|wp-content|rdd-plataforma|hostinger|rdd-eval|kimi|codex|gemini|qwen", re.I)
        for p in sorted(FX.rglob("*")) + [CURATOR, RAIZ / "sdd/invariants.md"]:
            if p.is_file():
                with self.subTest(arquivo=p.name):
                    self.assertIsNone(proibido.search(p.read_text(encoding="utf-8")))
