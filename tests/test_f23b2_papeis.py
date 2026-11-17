"""F23, fatia B2 — modelo por papel (DEFINE_F23B2_MODELO_POR_PAPEL: AT-001 a AT-011).

sdd-fluxo.sh modelo lê o slot papeis.<papel>; o despachar diz o modelo na parada; custo-feature.sh mostra o custo de
cada papel em sub-linhas fora do total e mede uma execução (--execucao); papel-serie.sh roda as séries com teto e
trava; papel-medir.sh só lê, pontua e escolhe.

As fixtures de sdd/fixtures/f23b2/ são inventadas (README de lá). Uma execução do agente falso custa, pelas tarifas
da fixture (1.000 tokens de entrada e 100.000 de saída): modelo-caro 0,001 + 1,0 = 1,001; modelo-medio 0,001 + 0,8 =
0,801; modelo-barato 0,0005 + 0,2 = 0,2005. Nenhum teste chama modelo nem rede.
"""
from __future__ import annotations

import json
import re
import shutil
import unittest
from pathlib import Path

from apoio import BASH, PYTHON, RAIZ, SEM_SINAL, Sandbox

FLUXO = RAIZ / "sdd/bin/sdd-fluxo.sh"
CUSTO = RAIZ / "sdd/bin/custo-feature.sh"
SERIE = RAIZ / "sdd/bin/papel-serie.sh"
MEDIR = RAIZ / "sdd/bin/papel-medir.sh"
FX = RAIZ / "sdd/fixtures/f23b2"
AGENTE = FX / "agente-falso.sh"
BRIEF_FLUXO = RAIZ / "sdd/fixtures/fluxo/brief-avaliador.md"
F = "F99_TESTE"


def pasta_claude(raiz: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(raiz.resolve()).replace("\\", "/"))


# ── AT-001 e AT-002: o slot e o despachar ────────────────────────────────────────────────────────────
class AT001AT002Slot(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()

    def fluxo(self, *a):
        return self.roda([BASH, FLUXO, *a], self.r)

    def config(self, corpo: str):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  name: x\n\npapeis:\n" + corpo)

    def brief(self, papel="avaliador"):
        return self.r / "sdd/reports/briefs" / ("BRIEF_%s_X.md" % papel)

    def test_vazio_ou_ausente_sai_como_hoje_sem_linha_de_modelo(self):
        for corpo in (None, '  avaliador: ""\n', "  curador: modelo-um\n"):
            with self.subTest(corpo=corpo):
                if corpo is not None:
                    self.config(corpo)
                rc, out, err = self.fluxo("modelo", "avaliador")
                self.assertEqual((rc, out), (0, "\n"), err)
                rc, out, _ = self.fluxo("despachar", "avaliador", "X", str(BRIEF_FLUXO))
                self.assertEqual(rc, 40)
                self.assertNotIn("Modelo:", out)

    def test_preenchido_vale_para_o_despacho_e_para_o_subagente(self):
        self.config("  avaliador: modelo-um\n  revisao_design: org/modelo-dois:v1\n  executor: modelo.tres\n"
                    "  curador: modelo-quatro\n  cartografo: modelo-cinco\n")
        for papel, valor in (("avaliador", "modelo-um"), ("revisao_design", "org/modelo-dois:v1"),
                             ("revisor-design", "org/modelo-dois:v1"), ("executor", "modelo.tres"),
                             ("executor-drive", "modelo.tres"), ("curador", "modelo-quatro"),
                             ("cartografo", "modelo-cinco")):
            with self.subTest(papel=papel):
                rc, out, err = self.fluxo("modelo", papel)
                self.assertEqual((rc, out.strip()), (0, valor), err)
        for papel, valor in (("avaliador", "modelo-um"), ("revisor-design", "org/modelo-dois:v1"),
                             ("executor-drive", "modelo.tres")):
            with self.subTest(despachar=papel):
                rc, out, _ = self.fluxo("despachar", papel, "X", str(BRIEF_FLUXO))
                self.assertEqual(rc, 40)
                self.assertIn("**Modelo:** abra a sessão nova com o modelo %s" % valor, out)
        rc, out, _ = self.fluxo("despachar", "revisor-governanca", "X", str(BRIEF_FLUXO))
        self.assertEqual(rc, 40)
        self.assertNotIn("Modelo:", out)   # governança não tem slot (fora dos 5 papéis)

    def test_valor_invalido_sai_64_sem_repetir_o_valor_e_sem_gravar_brief(self):
        ruins = ['"modelo um"', '"-x"', "'--opcao'", "modelo;rm", "x" * 81, '"a\\"b"', "modelo$(id)", "modelo`id`"]
        for v in ruins:
            with self.subTest(valor=v):
                self.config("  avaliador: %s\n" % v)
                rc, out, err = self.fluxo("modelo", "avaliador")
                self.assertEqual(rc, 64, out)
                self.assertIn("papeis.avaliador inválido", err)
                self.assertEqual(out, "")
                rc, out, err = self.fluxo("despachar", "avaliador", "X", str(BRIEF_FLUXO))
                self.assertEqual(rc, 64, out)
                self.assertFalse(self.brief().exists(), "o brief não pode ser gravado com o slot inválido")

    def test_papel_fora_da_lista_sai_64(self):
        rc, _, err = self.fluxo("modelo", "juiz")
        self.assertEqual(rc, 64)
        self.assertIn("modelo exige um papel", err)


# ── AT-003: o custo por papel ────────────────────────────────────────────────────────────────────────
class AT003CustoPorPapel(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo("projeto")
        self.cc = self.tmp / "claude-config"
        proj = self.cc / "projects" / pasta_claude(self.r)
        proj.mkdir(parents=True)
        msgs = [("10:00:00", None, None), ("10:05:00", "m1", "modelo-caro"), ("10:15:00", "m2", "modelo-barato"),
                ("10:35:00", "m3", "modelo-barato"), ("10:45:00", "m4", "modelo-caro")]
        linhas = []
        for hora, mid, modelo in msgs:
            ts = "2026-11-16T%s.000Z" % hora
            if mid is None:
                linhas.append({"type": "user", "timestamp": ts, "message": {"role": "user", "content": "pedido"}})
                continue
            linhas.append({"type": "assistant", "timestamp": ts, "requestId": "r" + mid,
                           "message": {"id": mid, "model": modelo, "role": "assistant", "content": [],
                                       "usage": {"input_tokens": 1000, "output_tokens": 100000,
                                                 "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}})
        (proj / "s.jsonl").write_text("".join(json.dumps(x) + "\n" for x in linhas), encoding="utf-8")
        marcas = [("09:59:00", "inicio", "build"), ("10:10:00", "inicio", "papel-avaliador"),
                  ("10:20:00", "fim", "papel-avaliador"), ("10:30:00", "inicio", "papel-avaliador"),
                  ("10:40:00", "fim", "papel-avaliador"), ("10:50:00", "fim", "build")]
        self.escreve(self.r, "sdd/traces/%s.jsonl" % F, "".join(
            json.dumps({"ts": "2026-11-16T%sZ" % h, "feature": F, "src": "fase", "evento": e, "fase": f}) + "\n"
            for h, e, f in marcas))
        self.env = dict(self.env, CLAUDE_CONFIG_DIR=str(self.cc))

    def custo(self):
        rc, out, err = self.roda([BASH, CUSTO, F, "--precos", str(FX / "precos"), "--saida", "-"], self.r)
        self.assertEqual(rc, 0, err + out)
        linhas = {}
        for ln in out.splitlines():
            c = [x.strip() for x in ln.split("|")][1:-1]
            if len(c) == 9 and c[0] != "Fase" and not c[0].startswith("---"):
                linhas[c[0]] = c[1:]
        return out, linhas

    def test_sub_linha_por_papel_fora_do_total(self):
        out, t = self.custo()
        self.assertEqual(t["build"][0], "1")
        self.assertEqual(t["build"][6], "2.4030")   # m1 + m2 + m3 + m4 = 1,001 + 0,2005 + 0,2005 + 1,001 = 2,403
        sub = "↳ papel avaliador · modelo-barato"
        self.assertIn(sub, t, out)
        self.assertEqual(t[sub][0], "2")             # 2 janelas = 2 execuções do papel
        self.assertEqual(t[sub][6], "0.4010")
        self.assertEqual(t["**total**"][6], "2.4030", "a sub-linha do papel não entra no total")
        self.assertNotIn("fase sem fim", out)       # a marca de papel não fecha a fase

    def test_marca_de_papel_sem_par_vai_para_fora_da_conta(self):
        with (self.r / "sdd/traces" / ("%s.jsonl" % F)).open("a", encoding="utf-8") as h:
            h.write(json.dumps({"ts": "2026-11-16T10:46:00Z", "feature": F, "src": "fase", "evento": "fim",
                                "fase": "papel-curador"}) + "\n")
        out, t = self.custo()
        self.assertIn("fim sem início: papel-curador", out)
        self.assertEqual(t["**total**"][6], "2.4030")

    def test_execucao_mede_so_a_pasta_pedida_e_sem_sessao_e_nd(self):
        rc, out, err = self.roda([BASH, CUSTO, "--execucao", str(self.r), "--precos", str(FX / "precos")], self.r)
        self.assertEqual(rc, 0, err)
        self.assertIn("nominal=2.403", out)
        self.assertIn("modelos=modelo-barato,modelo-caro", out)
        vazia = self.tmp / "sem-sessao"
        vazia.mkdir()
        rc, out, _ = self.roda([BASH, CUSTO, "--execucao", str(vazia), "--precos", str(FX / "precos")], self.r)
        self.assertEqual(rc, 2)
        self.assertIn("nominal=n/d", out)
        rc, _, err = self.roda([BASH, CUSTO, F, "--execucao", str(vazia)], self.r)
        self.assertEqual(rc, 64, err)


# ── séries: base comum ───────────────────────────────────────────────────────────────────────────────
class BaseSerie(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo("projeto")
        self.escreve(self.r, "LEIAME.md", "projeto de teste\n")
        self.commit(self.r)
        shutil.copytree(str(FX / "gabarito"), str(self.r / "gab"))
        self.med = self.r / "med"
        self.teto("0.00", "50.00")
        self.log = self.tmp / "chamadas.log"
        self.env = dict(self.env, CLAUDE_CONFIG_DIR=str(self.tmp / "claude-config"), FALSO_LOG=str(self.log),
                        FALSO_RESPOSTAS=str(FX / "respostas"), FALSO_PYTHON=PYTHON, FALSO_PROJETO=str(self.r))

    def teto(self, pago, nominal):
        self.escreve(self.med, "teto.txt", "teto_pago: %s\nteto_nominal: %s\n" % (pago, nominal))

    def serie(self, nome, papel, candidatos, reps=1):
        s = self.med / nome
        self.escreve(s, "serie.txt", "papel: %s\ngabarito: ../../gab\nrepeticoes: %d\n" % (papel, reps))
        self.escreve(s, "candidatos.tsv", "".join("%s\t%s\t%s\n" % c for c in candidatos))
        return s

    def rodar(self, s, *extra, env=None):
        return self.roda([BASH, SERIE, str(s), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                          str(FX / "precos"), *extra], self.r, env)

    def medir(self, s, *extra):
        return self.roda([BASH, MEDIR, str(s), *extra], self.r)

    def chamadas(self):
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []


CARO = ("caro", "modelo-caro", "assinatura")
MEDIO = ("medio", "modelo-medio", "assinatura")
BARATO = ("barato", "modelo-barato", "assinatura")


# ── AT-004 a AT-007: o medidor ───────────────────────────────────────────────────────────────────────
class AT004AT007Medidor(BaseSerie):
    def test_curador_escolhe_o_barato_e_reprova_o_que_descarta_o_add(self):
        s = self.serie("cur", "curador", [CARO, BARATO, MEDIO], reps=2)
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(len(self.chamadas()), 6)
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: ESCOLHIDO: barato", out)
        self.assertIn("medio · c1 · rep 1 — ADD/REFINE/TOMBSTONE: 0 de 1", out)
        self.assertIn("| barato | modelo-barato | 2 de 2 | 0.2005 | 80.0% |", out)

    def test_curador_contagem_a_mais_e_delta_recusado_ficam_fora(self):
        s = self.serie("cur", "curador", [CARO, BARATO])
        self.assertEqual(self.rodar(s)[0], 0)
        saida = s / "execucoes/c1/barato/1/saida.txt"
        txt = saida.read_text(encoding="utf-8")
        mais = "".join("| 9%d | contador | LM-00%d | LM-00%d ajudou+1 | X.md:1 | x | AUTO |\n" % (k, k, k) for k in (3, 3))
        saida.write_text(txt.replace("| 4 | promover", mais + "| 4 | promover"), encoding="utf-8")
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 1, out)
        self.assertIn("contagens: precisão 0.67", out)
        saida.write_text(txt.replace("LM-002 ajudou+1 |", "REFINE LM-999 :: inventado. |"), encoding="utf-8")
        rc, out, _ = self.medir(s)
        self.assertIn("o --aplicar recusou o delta", out)
        self.assertEqual((s.parent.parent / "gab/c1/playbook.md").read_text(encoding="utf-8"),
                         (FX / "gabarito/c1/playbook.md").read_text(encoding="utf-8"), "o gabarito nunca é escrito")

    def test_avaliador_falso_pass_reprova_mesmo_com_o_veredito_igual(self):
        s = self.serie("ava", "avaliador", [CARO, BARATO, MEDIO])
        self.assertEqual(self.rodar(s)[0], 0)
        rc, out, _ = self.medir(s)
        self.assertRegex(out, r"barato · a1 · rep 1 — .*AT que falha dado como aprovado: AT-002")
        self.assertEqual(rc, 1, out)                 # medio na meta, mas 20% < 30%
        self.assertIn("SEM GANHO MEDIDO", out)
        rc, out, _ = self.medir(s, "--limiar", "15")
        self.assertEqual(rc, 0, out)
        self.assertIn("ESCOLHIDO: medio", out)

    def test_avaliador_at_ausente_ou_palavra_fora_da_lista_nunca_vira_pass(self):
        s = self.serie("ava", "avaliador", [CARO, MEDIO])
        self.assertEqual(self.rodar(s)[0], 0)
        saida = s / "execucoes/a1/medio/1/saida.txt"
        txt = saida.read_text(encoding="utf-8")
        for troca, motivo in ((("| AT-003 |", "| AT-009 |"), "ATs iguais: 2 de 3"),
                              (("| FAIL |", "| ok |"), "ATs iguais: 2 de 3"),
                              (("VEREDITO: NEEDS_WORK", "VEREDITO: PASS"), "veredito PASS, esperado NEEDS_WORK")):
            with self.subTest(troca=troca):
                saida.write_text(txt.replace(*troca), encoding="utf-8")
                rc, out, _ = self.medir(s, "--limiar", "15")
                self.assertEqual(rc, 1, out)
                self.assertIn(motivo, out)

    def test_referencia_fora_da_meta_nao_escolhe(self):
        s = self.serie("ava", "avaliador", [BARATO, MEDIO])
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 22, out + err)
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 3, out)
        self.assertIn("REFERÊNCIA FORA DA META", out)

    def test_candidato_com_custo_nd_nunca_e_o_mais_barato(self):
        s = self.serie("cur", "curador", [CARO, BARATO])
        self.assertEqual(self.rodar(s)[0], 0)
        meta = s / "execucoes/c1/barato/1/meta.txt"
        meta.write_text(meta.read_text(encoding="utf-8").replace("nominal: 0.2005", "nominal: n/d"), encoding="utf-8")
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 1, out)
        self.assertIn("| barato | modelo-barato | 1 de 1 | n/d |", out)
        self.assertNotIn("ESCOLHIDO", out)

    def test_parcial_vem_antes_da_referencia_e_candidato_sem_execucao_nao_vence(self):
        s = self.serie("ava", "avaliador", [BARATO, MEDIO], reps=2)
        (s / "execucoes/a1/barato/1").mkdir(parents=True)
        (s / "execucoes/a1/barato/1/meta.txt").write_text("estado: invalida\nnominal: 1\n", encoding="utf-8")
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 4, out)                 # inválida e faltando: PARCIAL, nunca "referência fora da meta"
        self.assertIn("PARCIAL", out)


# ── AT-008, AT-009 e AT-011: o executor das séries ───────────────────────────────────────────────────
class AT008AT011Executor(BaseSerie):
    def test_pay_per_token_com_teto_pago_zero_nao_e_chamado(self):
        s = self.serie("cur", "curador", [CARO, ("pago", "modelo-barato", "pay-per-token")])
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 20, out)
        self.assertIn("PARADO PELO TETO", out)
        self.assertEqual([c.split()[3] for c in self.chamadas()], ["modelo-caro"])
        self.assertIn("pay-per-token (pago) com teto pago zero", (s / "PARADA.txt").read_text(encoding="utf-8"))
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 4, out)

    def test_cobranca_desconhecida_nunca_roda(self):
        s = self.serie("cur", "curador", [("x", "modelo-caro", "desconhecida")])
        self.assertEqual(self.rodar(s)[0], 20)
        self.assertEqual(self.chamadas(), [])

    def test_teto_nominal_vale_para_a_medicao_inteira(self):
        self.teto("0.00", "2.50")
        a = self.serie("cur", "curador", [CARO], reps=2)
        self.assertEqual(self.rodar(a)[0], 0)          # 1,001 + 1,001 = 2,002
        b = self.serie("ava", "avaliador", [CARO], reps=2)
        rc, out, _ = self.rodar(b)                      # 2,002 + estimativa 1,001 > 2,50: nem a 1ª roda
        self.assertEqual(rc, 20, out)
        self.assertEqual(len(self.chamadas()), 2)
        self.assertIn("acumulado_nominal: 2.002", (b / "PARADA.txt").read_text(encoding="utf-8"))

    def test_acumulado_com_nd_para_a_serie(self):
        s = self.serie("cur", "curador", [CARO], reps=2)
        rc, out, _ = self.rodar(s, env=dict(self.env, FALSO_MODO="sem-sessao"))
        self.assertEqual(rc, 20, out)
        self.assertEqual(len(self.chamadas()), 1)
        self.assertIn("acumulado com n/d", (s / "PARADA.txt").read_text(encoding="utf-8"))

    def test_retomada_nao_repete_e_move_a_parada_antiga(self):
        self.teto("0.00", "1.50")
        s = self.serie("cur", "curador", [CARO], reps=2)
        self.assertEqual(self.rodar(s)[0], 20)          # roda 1, para na 2ª
        self.teto("0.00", "50.00")
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self.chamadas()), 2)
        self.assertFalse((s / "PARADA.txt").exists())
        self.assertEqual(len(list((s / "paradas").iterdir())), 1)
        rc, out, _ = self.rodar(s)
        self.assertEqual((rc, len(self.chamadas())), (0, 2))
        self.assertIn("acumulado da medição: nominal 2.002", out)
        self.assertEqual(self.medir(s)[0], 1)           # só a referência: completa, nada a escolher

    def test_execucao_interrompida_tem_o_custo_somado_antes_de_refazer(self):
        s = self.serie("cur", "curador", [CARO])
        pasta = s / "execucoes/c1/caro/1"
        copia = self.tmp / "copia-interrompida"
        copia.mkdir()
        sess = self.tmp / "claude-config/projects" / pasta_claude(copia)
        sess.mkdir(parents=True)
        (sess / "s.jsonl").write_text(json.dumps(
            {"type": "assistant", "timestamp": "2026-11-16T10:00:00.000Z", "requestId": "r",
             "message": {"id": "m", "model": "modelo-caro", "content": [],
                         "usage": {"input_tokens": 1000, "output_tokens": 100000}}}) + "\n", encoding="utf-8")
        self.escreve(pasta, "inicio.txt", "copia: %s\ncandidato: caro\ninicio: 2026-11-16T10:00:00Z\n" % copia)
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertIn("execução interrompida medida", out)
        self.assertIn("nominal: 1.001", (pasta / "interrompida-1.txt").read_text(encoding="utf-8"))
        self.assertIn("acumulado da medição: nominal 2.002", out)   # a interrompida e a refeita
        self.assertEqual(len(self.chamadas()), 1)

    def test_barreira_de_calibracao_antes_de_qualquer_candidato(self):
        s = self.serie("ava", "avaliador", [BARATO, CARO, MEDIO])
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 22, out)
        self.assertEqual([c.split()[3] for c in self.chamadas()], ["modelo-barato"])
        self.assertIn("nenhum candidato foi chamado", (s / "PARADA.txt").read_text(encoding="utf-8"))

    def test_candidatos_filtra_quais_rodam(self):
        s = self.serie("cur", "curador", [CARO, BARATO, MEDIO])
        rc, out, _ = self.rodar(s, "--candidatos", "medio")
        self.assertEqual(rc, 0, out)
        self.assertEqual([c.split()[3] for c in self.chamadas()], ["modelo-caro", "modelo-medio"])
        rc, _, err = self.rodar(s, "--candidatos", "caro")
        self.assertEqual(rc, 64, err)

    def test_modelo_do_candidato_e_validado_como_o_slot(self):
        for ruim in ("-x", "modelo um", "a;b", "x" * 81):
            with self.subTest(modelo=ruim):
                s = self.serie("cur", "curador", [("x", ruim, "assinatura")])
                rc, _, err = self.rodar(s)
                self.assertEqual(rc, 64, err)
        self.assertEqual(self.chamadas(), [])

    def test_agente_que_grava_no_projeto_invalida_a_execucao(self):
        s = self.serie("cur", "curador", [CARO])
        rc, out, _ = self.rodar(s, env=dict(self.env, FALSO_MODO="grava-projeto"))
        self.assertEqual(rc, 21, out)
        self.assertIn("RESULTADO: FRONTEIRA", out)
        meta = (s / "execucoes/c1/caro/1/meta.txt").read_text(encoding="utf-8")
        self.assertIn("estado: invalida", meta)
        parada = (s / "PARADA.txt").read_text(encoding="utf-8")
        self.assertIn("vazou.txt", parada)
        self.assertTrue((self.r / "vazou.txt").exists(), "nada fora da cópia é apagado")
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 4, out)

    def test_copia_com_remoto_invalida_e_copia_vem_do_commit_sem_remoto(self):
        sha = self.git(self.r, "rev-parse", "HEAD").strip()
        (self.r / "gab/a1/caso.txt").write_text("papel: avaliador\ncommit: %s\norigem: teste\n" % sha, encoding="utf-8")
        self.escreve(self.r, "gab/a1/entrada/sdd/extra.md", "posto por cima\n")
        s = self.serie("ava", "avaliador", [CARO])
        espiao = self.tmp / "espiao.sh"
        espiao.write_text('ls LEIAME.md sdd/extra.md > "%s" && git remote >> "%s"; bash "%s"\n'
                          % ((self.tmp / "viu.txt").as_posix(), (self.tmp / "viu.txt").as_posix(), AGENTE.as_posix()),
                          encoding="utf-8")
        rc, out, err = self.roda([BASH, SERIE, str(s), "--cmd", 'bash "%s"' % espiao.as_posix(), "--precos",
                                  str(FX / "precos")], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((self.tmp / "viu.txt").read_text(encoding="utf-8").split(), ["LEIAME.md", "sdd/extra.md"])
        s2 = self.serie("ava2", "avaliador", [CARO])
        rc, out, _ = self.rodar(s2, env=dict(self.env, FALSO_MODO="remoto"))
        self.assertEqual(rc, 21, out)
        self.assertIn("a cópia ganhou remoto git", out)

    @unittest.skipIf(*SEM_SINAL)
    def test_teto_de_tempo_corta_a_execucao(self):
        s = self.serie("cur", "curador", [CARO])
        rc, out, _ = self.rodar(s, "--teto-s", "2", env=dict(self.env, FALSO_MODO="dorme"))
        self.assertEqual(rc, 0, out)
        self.assertIn("rc: 124", (s / "execucoes/c1/caro/1/meta.txt").read_text(encoding="utf-8"))

    def test_erros_de_uso(self):
        s = self.serie("cur", "curador", [CARO])
        (self.med / "teto.txt").unlink()
        rc, _, err = self.rodar(s)
        self.assertEqual(rc, 64)
        self.assertIn("teto.txt", err)
        self.teto("0.00", "50.00")
        rc, _, err = self.roda([BASH, SERIE, str(s)], self.r)
        self.assertEqual(rc, 64)
        self.assertIn("papeis.serie_cmd", err)
        fora = self.tmp / "fora-do-git"
        shutil.copytree(str(self.med), str(fora / "med"))
        rc, _, err = self.roda([BASH, SERIE, str(fora / "med/cur"), "--cmd", "true"], fora)
        self.assertEqual(rc, 64)
        self.assertIn("repositório git", err)
        self.assertEqual(self.chamadas(), [])


# ── AT-010: o pacote não leva nome de modelo nesta fatia, e os arquivos novos estão no MANIFEST ────────
NOME_DE_MODELO = re.compile(r"(?i)\b(opus|sonnet|haiku|fable|gpt|gemini|qwen|llama|mistral|claude|deepseek|grok)"
                            r"[-_ ]?\d|\b(opus|sonnet|haiku)\b")


def nomes_de_modelo(texto: str) -> list:
    return [m.group(0) for m in NOME_DE_MODELO.finditer(texto)]


class AT010Pacote(unittest.TestCase):
    NOVOS = ("sdd/bin/papel-serie.sh", "sdd/bin/papel-medir.sh", "docs/model-per-role.md",
             "docs/pt-BR/model-per-role.md", "tests/test_f23b2_papeis.py")

    def trecho(self, rel, ini, fim=None):
        txt = (RAIZ / rel).read_text(encoding="utf-8")
        a = txt.index(ini)
        b = txt.index(fim, a + 1) if fim else len(txt)
        return txt[a:b]

    def test_guarda_pega_um_nome_plantado(self):
        self.assertEqual(nomes_de_modelo("use o Sonnet aqui"), ["Sonnet"])
        self.assertEqual(nomes_de_modelo("papeis:\n  avaliador: gpt-5\n"), ["gpt-5"])
        self.assertEqual(nomes_de_modelo("rode claude -p --model \"$SDD_MODELO\""), [])

    def test_sem_nome_de_modelo_no_que_esta_fatia_escreve(self):
        textos = {rel: (RAIZ / rel).read_text(encoding="utf-8") for rel in self.NOVOS if rel != "tests/test_f23b2_papeis.py"}
        textos["config papeis"] = self.trecho("sdd/config.example.yaml", "papeis:", "\n# ")
        textos["contexto-fresco"] = self.trecho(".agents/skills/sdd-build/references/contexto-fresco.md",
                                                "## Modelo do papel")
        textos["MARCA_FASE"] = self.trecho("sdd/templates/fragments/MARCA_FASE.md", "## Marca de papel")
        for p in FX.rglob("*"):
            if p.is_file():
                textos[str(p.relative_to(RAIZ))] = p.read_text(encoding="utf-8")
        for rel, txt in textos.items():
            with self.subTest(arquivo=rel):
                self.assertEqual(nomes_de_modelo(txt), [])

    def test_arquivos_novos_no_manifest(self):
        manifest = set((RAIZ / "MANIFEST.txt").read_text(encoding="utf-8").split())
        novos = list(self.NOVOS) + [str(p.relative_to(RAIZ)).replace("\\", "/") for p in FX.rglob("*") if p.is_file()]
        for rel in novos:
            with self.subTest(arquivo=rel):
                self.assertIn(rel, manifest)

    def test_slots_documentados_no_config(self):
        papeis = self.trecho("sdd/config.example.yaml", "papeis:", "\n# ")
        for chave in ("curador", "avaliador", "revisao_design", "cartografo", "executor", "serie_cmd"):
            with self.subTest(chave=chave):
                self.assertRegex(papeis, r"\n  %s: \"\"" % chave)


if __name__ == "__main__":
    unittest.main()
