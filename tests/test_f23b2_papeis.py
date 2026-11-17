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
import os
import re
import shutil
import signal
import subprocess
import time
import unittest
from pathlib import Path

from apoio import BASH, PYTHON, RAIZ, SEM_SINAL, WINDOWS, Sandbox

FLUXO = RAIZ / "sdd/bin/sdd-fluxo.sh"
MARCA = RAIZ / "sdd/bin/marca-fase.sh"
ESCADA = RAIZ / ".agents/skills/sdd-build/references/contexto-fresco.md"
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

    def test_papel_depois_do_fim_das_fases_conta_so_na_sub_linha(self):
        # raio de impacto da release: o curador do lote roda depois do fim da release; antes, a mensagem fora da janela
        # das fases era descartada e o papel saía n/d com "nenhuma mensagem lida"
        proj = self.cc / "projects" / pasta_claude(self.r)
        with (proj / "s.jsonl").open("a", encoding="utf-8") as h:
            h.write(json.dumps({"type": "assistant", "timestamp": "2026-11-16T11:00:00.000Z", "requestId": "r9",
                                "message": {"id": "m9", "model": "modelo-barato", "role": "assistant", "content": [],
                                            "usage": {"input_tokens": 1000, "output_tokens": 100000,
                                                      "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0}}})
                    + "\n")
        with (self.r / ("sdd/traces/%s.jsonl" % F)).open("a", encoding="utf-8") as h:
            for hora, ev in (("10:55:00", "inicio"), ("11:05:00", "fim")):
                h.write(json.dumps({"ts": "2026-11-16T%sZ" % hora, "feature": F, "src": "fase", "evento": ev,
                                    "fase": "papel-curador"}) + "\n")
        out, t = self.custo()
        sub = "↳ papel curador · modelo-barato"
        self.assertIn(sub, t, out)
        self.assertEqual(t[sub][6], "0.2005")
        self.assertEqual(t["**total**"][6], "2.4030", "fora das fases, o papel não entra no total")
        self.assertNotIn("nenhuma mensagem lida em papel-curador", out)

    def test_marca_de_papel_fora_das_fotos_nao_e_escrita_do_agente(self):
        # raio de impacto da release: sdd/traces/ entra na foto da fronteira; a marca no meio das fotos reprovava o
        # cartógrafo, a governança e o curador. A escada manda marcar o início antes da foto e o fim depois do --comparar
        texto = ESCADA.read_text(encoding="utf-8")
        self.assertIn("Grave o início **antes** da foto de antes e o fim **depois** do\n   `--comparar`", texto)
        fr = RAIZ / "sdd/bin/governanca-fronteira.sh"
        self.escreve(self.r, ".gitignore", "sdd/traces/\n")
        permitido = self.r / "sdd/contexto/x.md"
        fotos = self.tmp / "fotos"
        fotos.mkdir()

        def fronteira(no_meio):
            self.assertEqual(self.roda([BASH, MARCA, "inicio", "papel-cartografo", F], self.r)[0], 0)
            self.assertEqual(self.roda([BASH, fr, "--snapshot", self.r, fotos / "antes", permitido], self.r)[0], 0)
            self.escreve(self.r, "sdd/contexto/x.md", "mapa\n")      # a escrita permitida do agente
            if no_meio:
                self.roda([BASH, MARCA, "fim", "papel-cartografo", F], self.r)
            self.roda([BASH, fr, "--snapshot", self.r, fotos / "depois", permitido], self.r)
            rc = self.roda([BASH, fr, "--comparar", fotos / "antes", fotos / "depois", permitido], self.r)
            if not no_meio:
                self.assertEqual(self.roda([BASH, MARCA, "fim", "papel-cartografo", F], self.r)[0], 0)
            permitido.unlink()
            return rc
        rc, out, err = fronteira(no_meio=False)
        self.assertEqual(rc, 0, out + err)
        rc, out, _ = fronteira(no_meio=True)
        self.assertEqual(rc, 1, out)
        self.assertIn("FORA:", out)

    def test_escada_separa_slot_invalido_de_script_antigo(self):
        # raio de impacto da release: num projeto com o sdd-fluxo.sh antigo (editado, o upgrade o mantém), o verbo
        # modelo sai 64 no uso; lido como "slot inválido", o despacho travava
        texto = ESCADA.read_text(encoding="utf-8")
        self.assertIn("**Exit 64 com a linha `🛑 sdd-fluxo: papeis.<slot> inválido`**", texto)
        self.assertIn("**Outro exit 64**", texto)
        self.escreve(self.r, "sdd/config.yaml", 'papeis:\n  avaliador: "m 1"\n')
        rc, out, err = self.roda([BASH, FLUXO, "modelo", "avaliador"], self.r)
        self.assertEqual(rc, 64)
        self.assertIn("🛑 sdd-fluxo: papeis.avaliador inválido", out + err)
        rc, out, err = self.roda([BASH, FLUXO, "verbo-que-nao-existe"], self.r)
        self.assertEqual(rc, 64)
        self.assertNotIn("🛑 sdd-fluxo: papeis.", out + err)

    def test_marca_fase_aceita_o_nome_de_cada_papel_da_escada(self):
        # R4 da revisão do código: a escada manda marcar papel-<papel>; cada nome que ela lista tem de passar no
        # marca-fase.sh (o nome do slot, revisao_design, tem sublinhado e cairia em 64)
        texto = ESCADA.read_text(encoding="utf-8")
        trecho = texto[texto.index("o `<papel>` é o nome do despacho"):]
        nomes = re.findall(r"`([a-z][a-z-]*)`", trecho[:trecho.index(")")])
        self.assertEqual(nomes, ["cartografo", "revisor-governanca", "avaliador", "revisor-design", "executor-drive",
                                 "curador"])
        for n in nomes:
            for ev in ("inicio", "fim"):
                rc, out, err = self.roda([BASH, MARCA, ev, "papel-" + n, F], self.r)
                self.assertEqual(rc, 0, n + out + err)
        linhas = [json.loads(x) for x in (self.r / ("sdd/traces/%s.jsonl" % F)).read_text(encoding="utf-8").splitlines()]
        self.assertEqual({x["fase"] for x in linhas if x["fase"].startswith("papel-") and x["ts"] > "2026-11-17"},
                         {"papel-" + n for n in nomes})
        self.assertEqual(self.roda([BASH, MARCA, "inicio", "papel-revisao_design", F], self.r)[0], 64)


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
        self.assertIn("contagens: precisão 0.50", out)   # 2 certas de 4 propostas (o LM-003 vem 2 vezes: +2)
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

    def test_contagem_repetida_conta_em_dobro_na_precisao(self):
        # R3 da rodada 2: "LM-001 ajudou+1" duas vezes credita +2 (o --aplicar aceita); em conjunto, a precisão ficava 1
        s = self.serie("cur", "curador", [CARO, BARATO])
        self.assertEqual(self.rodar(s)[0], 0)
        saida = s / "execucoes/c1/barato/1/saida.txt"
        txt = saida.read_text(encoding="utf-8")
        dup = "| 95 | contador | LM-001 | LM-001 ajudou+1 | X.md:1 | x | AUTO |\n"
        saida.write_text(txt.replace("| 4 | promover", dup + "| 4 | promover"), encoding="utf-8")
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 1, out)
        self.assertIn("contagens: precisão 0.67", out)

    def test_execucao_gravada_com_outro_modelo_nao_vale(self):
        # N2 da rodada 2: trocar o modelo de um id e retomar mediria o modelo novo com as respostas do antigo
        s = self.serie("cur", "curador", [CARO, BARATO])
        self.assertEqual(self.rodar(s)[0], 0)
        (s / "candidatos.tsv").write_text("caro\tmodelo-caro\tassinatura\nbarato\tmodelo-medio\tassinatura\n",
                                          encoding="utf-8")
        n = len(self.chamadas())
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 64, out + err)
        self.assertIn("gravada com o modelo modelo-barato", err)
        self.assertEqual(len(self.chamadas()), n)
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 4, out)
        self.assertIn("gravada com o modelo modelo-barato, o candidatos.tsv diz modelo-medio", out)

    def test_um_add_proposto_nao_cobre_dois_esperados(self):
        # R2 da rodada 4: o mesmo ADD casava com os 2 esperados e a cobertura saía 2 de 2
        with (self.r / "gab/c1/esperado.txt").open("a", encoding="utf-8") as h:
            h.write("ADD Reviews / harness :: sup: `termo-a` `termo-d` :: Outra regra inventada. **Do instead:** outra "
                    "ação. → ficha: — · promovido_para: —\n")
        s = self.serie("cur", "curador", [BARATO])
        self.assertEqual(self.rodar(s)[0], 0)
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 3, out)
        self.assertIn("ADD/REFINE/TOMBSTONE: 1 de 2", out)

    def test_execucao_com_rc_diferente_de_zero_fica_fora_da_meta(self):
        # R2 da revisão do código: o barato responde certo e sai 1; sem olhar o rc ele seria o escolhido
        s = self.serie("cur", "curador", [CARO, BARATO])
        rc, out, _ = self.rodar(s, env=dict(self.env, FALSO_SAI="modelo-barato"))
        self.assertEqual(rc, 0, out)
        self.assertIn("rc: 1", (s / "execucoes/c1/barato/1/meta.txt").read_text(encoding="utf-8"))
        rc, out, _ = self.medir(s)
        self.assertEqual(rc, 1, out)
        self.assertIn("barato · c1 · rep 1 — o agente saiu 1", out)

    def test_gabarito_sem_o_que_comparar_e_recusado_antes_de_chamar(self):
        # N1 da revisão do código: esperado.txt sem VEREDITO e sem AT faria a resposta vazia passar (None == None)
        (self.r / "gab/a1/esperado.txt").write_text("nada a comparar\n", encoding="utf-8")
        s = self.serie("ava", "avaliador", [CARO, BARATO])
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 64, out + err)
        self.assertIn("recusa esta série", err)
        self.assertEqual(self.chamadas(), [])
        rc, _, err = self.medir(s)
        self.assertEqual(rc, 64)
        self.assertIn("sem VEREDITO", err)
        (self.r / "gab/c1/playbook.md").unlink()
        rc, _, err = self.medir(self.serie("cur", "curador", [CARO, BARATO]))
        self.assertEqual(rc, 64)
        self.assertIn("sem playbook.md", err)


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
        copia = self.tmp / "trab-interrompida/copia"
        copia.mkdir(parents=True)
        # parou antes de chamar o agente (sem o chamado.txt ao lado da cópia): descartada, sem custo (R3)
        self.escreve(pasta, "inicio.txt", "copia: %s\ncandidato: caro\ninicio: 2026-11-16T09:00:00Z\n" % copia)
        rc, out, _ = self.rodar(s)
        self.assertIn("não chegou a chamar o agente descartada", out)
        self.assertEqual(list(pasta.glob("interrompida-*")), [])
        self.assertIn("acumulado da medição: nominal 1.001", out)
        shutil.rmtree(str(pasta))
        self.log.unlink()
        (copia.parent / "chamado.txt").write_text("2026-11-16T10:00:00Z\n", encoding="utf-8")
        sess = self.tmp / "claude-config/projects" / pasta_claude(copia)
        sess.mkdir(parents=True)
        (sess / "s.jsonl").write_text(json.dumps(
            {"type": "assistant", "timestamp": "2026-11-16T10:00:00.000Z", "requestId": "r",
             "message": {"id": "m", "model": "modelo-caro", "content": [],
                         "usage": {"input_tokens": 1000, "output_tokens": 100000}}}) + "\n", encoding="utf-8")
        self.escreve(pasta, "inicio.txt", "copia: %s\ncandidato: caro\ninicio: 2026-11-16T10:00:00Z\n" % copia)
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 21, out)                  # sem a foto de antes, a fronteira não se confere (N1, rodada 3)
        self.assertIn("sem como conferir a fronteira", out)
        self.assertIn("execução interrompida medida", out)
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
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
        # R1 da rodada 3: a retomada guarda a inválida (o custo fica) e a refaz; antes, ela era pulada para sempre
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertIn("guardada como invalida-1.txt e refeita", out)
        self.assertIn("estado: invalida", (s / "execucoes/c1/caro/1/invalida-1.txt").read_text(encoding="utf-8"))
        self.assertIn("estado: ok", (s / "execucoes/c1/caro/1/meta.txt").read_text(encoding="utf-8"))
        self.assertIn("acumulado da medição: nominal 2.002", out)
        self.assertEqual(len(self.chamadas()), 2)
        self.assertEqual(self.medir(s)[0], 1)

    @unittest.skipIf(*SEM_SINAL)
    def test_interrompida_que_gravou_no_projeto_para_na_retomada(self):
        # N1 da rodada 3: a interrompida pulava a foto de depois; a escrita dela no projeto passava a ser a base nova
        s = self.serie("cur", "curador", [CARO])
        pidf = self.tmp / "agente.pid"
        env = dict(self.env, FALSO_MODO="sessao-e-dorme", FALSO_PID=str(pidf))
        p = subprocess.Popen([BASH, str(SERIE), str(s), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                              str(FX / "precos")], cwd=str(self.r), env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        agente = 0
        try:
            for _ in range(300):
                if pidf.exists() and pidf.read_text(encoding="utf-8").strip():
                    break
                time.sleep(0.1)
            else:
                self.fail("o agente falso não começou")
            agente = int(pidf.read_text(encoding="utf-8").strip())
            (self.r / "escrita-do-agente.txt").write_text("x\n", encoding="utf-8")   # o agente grava no projeto
        finally:
            alvos = [lambda: os.killpg(p.pid, signal.SIGKILL)]
            if agente > 0:
                alvos.append(lambda: os.kill(agente, signal.SIGKILL))
            for alvo in alvos:
                try:
                    alvo()
                except OSError:
                    pass
            p.wait()
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 21, out)
        self.assertIn("RESULTADO: FRONTEIRA", out)
        self.assertIn("escrita-do-agente.txt", (s / "PARADA.txt").read_text(encoding="utf-8"))
        intr = (s / "execucoes/c1/caro/1/interrompida-1.txt").read_text(encoding="utf-8")
        self.assertIn("nominal: 1.001", intr)
        self.assertIn("fronteira: fora", intr)
        self.assertTrue((self.r / "escrita-do-agente.txt").exists(), "nada fora da cópia é apagado")
        self.assertEqual(len(self.chamadas()), 1)
        rc, out, _ = self.rodar(s)                       # conferidos os caminhos, a retomada segue
        self.assertEqual(rc, 0, out)
        self.assertIn("acumulado da medição: nominal 2.002", out)

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

    def test_base_vira_tag_na_copia_para_o_teste_de_nao_regressao(self):
        self.git(self.r, "tag", "v9.9.9")
        self.escreve(self.r, "NOVO.md", "depois da base\n")
        self.git(self.r, "add", "NOVO.md")
        self.git(self.r, "commit", "-q", "-m", "depois da base")
        sha = self.git(self.r, "rev-parse", "HEAD").strip()
        (self.r / "gab/a1/caso.txt").write_text("papel: avaliador\ncommit: %s\nbase: v9.9.9\norigem: teste\n" % sha,
                                               encoding="utf-8")
        s = self.serie("ava", "avaliador", [CARO])
        viu = (self.tmp / "viu.txt").as_posix()
        espiao = self.tmp / "espiao.sh"
        espiao.write_text('git diff --name-only v9.9.9 HEAD > "%s"; git remote >> "%s"; bash "%s"\n'
                          % (viu, viu, AGENTE.as_posix()), encoding="utf-8")
        rc, out, err = self.roda([BASH, SERIE, str(s), "--cmd", 'bash "%s"' % espiao.as_posix(), "--precos",
                                  str(FX / "precos")], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((self.tmp / "viu.txt").read_text(encoding="utf-8").split(), ["NOVO.md"])
        # entrada/ fica por cima, fora do commit (como o DEFINE e o DESIGN estavam no projeto)
        self.escreve(self.r, "gab/a1/entrada/sdd/features/DEFINE_X.md", "define da época\n")
        espiao.write_text('git ls-files > "%s"; echo --- >> "%s"; git status --porcelain >> "%s"; bash "%s"\n'
                          % (viu, viu, viu, AGENTE.as_posix()), encoding="utf-8")
        rc, out, err = self.roda([BASH, SERIE, str(self.serie("ava3", "avaliador", [CARO])), "--cmd",
                                  'bash "%s"' % espiao.as_posix(), "--precos", str(FX / "precos")], self.r)
        self.assertEqual(rc, 0, out + err)
        rastreados, status = (self.tmp / "viu.txt").read_text(encoding="utf-8").split("---")
        self.assertNotIn("DEFINE_X.md", rastreados)
        self.assertIn("?? sdd/", status)
        (self.r / "gab/a1/caso.txt").write_text("papel: avaliador\ncommit: %s\nbase: nao-existe\n" % sha, encoding="utf-8")
        rc, _, err = self.rodar(self.serie("ava2", "avaliador", [CARO]))
        self.assertEqual(rc, 64, err)
        self.assertIn("base nao-existe não é uma ref", err)

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

    @unittest.skipIf(*SEM_SINAL)
    def test_refeita_em_pasta_nova_nao_cobra_a_interrompida_duas_vezes(self):
        # R1 da revisão do código: o registro de sessão é por pasta; a refeita no mesmo caminho somaria as 2 sessões
        s = self.serie("cur", "curador", [CARO])
        pidf = self.tmp / "agente.pid"
        env = dict(self.env, FALSO_MODO="sessao-e-dorme", FALSO_PID=str(pidf))
        p = subprocess.Popen([BASH, str(SERIE), str(s), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                              str(FX / "precos")], cwd=str(self.r), env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        try:
            for _ in range(300):
                if pidf.exists() and pidf.read_text(encoding="utf-8").strip():
                    break
                time.sleep(0.1)
            else:
                self.fail("o agente falso não começou")
        finally:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait()
            try:
                os.kill(int(pidf.read_text(encoding="utf-8").strip()), signal.SIGKILL)
            except (OSError, ValueError):
                pass
        pasta = s / "execucoes/c1/caro/1"
        self.assertTrue((pasta / "inicio.txt").exists())
        self.assertFalse((pasta / "meta.txt").exists())
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertIn("nominal: 1.001", (pasta / "interrompida-1.txt").read_text(encoding="utf-8"))
        self.assertIn("nominal: 1.001", (pasta / "meta.txt").read_text(encoding="utf-8"))   # só a sessão da refeita
        self.assertIn("acumulado da medição: nominal 2.002", out)

    @unittest.skipIf(*SEM_SINAL)
    def test_sinal_na_serie_mata_o_agente(self):
        # R1 da rodada 2: o agente roda em sessão própria; sem o except, Ctrl-C/SIGTERM na série o deixava vivo
        for sig in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(sinal=sig):
                s = self.serie("cur%d" % sig, "curador", [CARO])
                pidf = self.tmp / ("agente-%d.pid" % sig)
                env = dict(self.env, FALSO_MODO="sessao-e-dorme", FALSO_PID=str(pidf))
                p = subprocess.Popen([BASH, str(SERIE), str(s), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                                      str(FX / "precos")], cwd=str(self.r), env=env, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
                agente = 0
                try:
                    for _ in range(300):
                        if pidf.exists() and pidf.read_text(encoding="utf-8").strip():
                            break
                        time.sleep(0.1)
                    else:
                        self.fail("o agente falso não começou")
                    agente = int(pidf.read_text(encoding="utf-8").strip())
                    os.killpg(p.pid, sig)
                    p.wait(timeout=15)
                    vivo = True
                    for _ in range(50):
                        try:
                            os.kill(agente, 0)
                        except ProcessLookupError:
                            vivo = False
                            break
                        time.sleep(0.1)
                    self.assertFalse(vivo, "o agente seguiu vivo depois do sinal na série")
                finally:
                    alvos = [lambda: os.killpg(p.pid, signal.SIGKILL)]
                    if agente > 0:                     # nunca os.kill(0, …): mataria o grupo do próprio teste
                        alvos.append(lambda: os.kill(agente, signal.SIGKILL))
                    for alvo in alvos:
                        try:
                            alvo()
                        except OSError:
                            pass
                    p.wait()
                self.assertTrue((s / "execucoes/c1/caro/1/inicio.txt").exists())
                rc, out, _ = self.rodar(s)
                self.assertEqual(rc, 0, out)
                self.assertIn("nominal: 1.001", (s / "execucoes/c1/caro/1/interrompida-1.txt").read_text(encoding="utf-8"))

    def test_trava_da_pasta_de_medicao(self):
        # N1 da rodada 2, N2 da rodada 4: trava do sistema; quem a segura bloqueia a 2ª série, e ela some com o processo
        s = self.serie("cur", "curador", [CARO])
        trava = self.med / ".papel-serie.trava"
        trava.write_text("99999 antes\n", encoding="utf-8")       # arquivo velho, sem ninguém segurando: não trava
        fd = os.open(str(trava), os.O_RDWR)
        try:
            if WINDOWS:
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            rc, out, err = self.rodar(s)
            self.assertEqual(rc, 64, out + err)
            self.assertIn("outra série roda nesta pasta de medição", err)
            self.assertEqual(self.chamadas(), [])
        finally:
            os.close(fd)                                              # fechar solta a trava, como o fim do processo
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(len(self.chamadas()), 1)

    @unittest.skipIf(*SEM_SINAL)
    def test_agente_vivo_da_interrompida_trava_a_retomada(self):
        # N1 da rodada 4: com o executor morto por SIGKILL, o agente segue vivo; medir agora deixaria gasto fora do teto
        s = self.serie("cur", "curador", [CARO])
        pidf = self.tmp / "agente.pid"
        env = dict(self.env, FALSO_MODO="sessao-e-dorme", FALSO_PID=str(pidf))
        p = subprocess.Popen([BASH, str(SERIE), str(s), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                              str(FX / "precos")], cwd=str(self.r), env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        agente = 0
        try:
            for _ in range(300):
                if pidf.exists() and pidf.read_text(encoding="utf-8").strip():
                    break
                time.sleep(0.1)
            else:
                self.fail("o agente falso não começou")
            agente = int(pidf.read_text(encoding="utf-8").strip())
            os.killpg(p.pid, signal.SIGKILL)                          # só o executor: o agente fica vivo
            p.wait()
            rc, out, err = self.rodar(s)
            self.assertEqual(rc, 64, out + err)
            self.assertIn("ainda roda", err)
            self.assertFalse(list(s.rglob("interrompida-*.txt")), "nada medido com o agente vivo")
        finally:
            if agente > 0:
                try:
                    os.kill(agente, signal.SIGKILL)
                except OSError:
                    pass
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            p.wait()
        time.sleep(0.5)
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertIn("nominal: 1.001", (s / "execucoes/c1/caro/1/interrompida-1.txt").read_text(encoding="utf-8"))

    def test_parada_fica_se_a_retomada_sai_antes_de_chamar(self):
        # R1 da rodada 4: a retomada arquivava o PARADA.txt no começo; saindo antes de chamar (64), o medidor perdia o
        # PARCIAL e podia escolher sem o candidato que faltava
        self.teto("0.00", "1.50")
        s = self.serie("cur", "curador", [CARO], reps=2)
        self.assertEqual(self.rodar(s)[0], 20)
        (s / "candidatos.tsv").write_text("caro\tmodelo-medio\tassinatura\n", encoding="utf-8")
        rc, _, err = self.rodar(s)
        self.assertEqual(rc, 64, err)
        self.assertTrue((s / "PARADA.txt").exists())
        self.assertEqual(self.medir(s)[0], 4)

    def test_precos_relativo_vale_pela_pasta_atual(self):
        # R3 da rodada 4: --precos relativo era lido a partir da raiz e o custo saía n/d
        shutil.copytree(str(FX / "precos"), str(self.tmp / "pr"))
        s = self.serie("cur", "curador", [CARO])
        rc, out, err = self.roda([BASH, SERIE, s, "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos", "pr"], self.tmp)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("nominal: 1.001", (s / "execucoes/c1/caro/1/meta.txt").read_text(encoding="utf-8"))

    @unittest.skipIf(*SEM_SINAL)
    def test_parada_de_outra_serie_nao_conta_como_escrita_da_interrompida(self):
        # R4 da rodada 4: a outra série para (R5) e grava o PARADA.txt dela; a retomada não pode tomá-lo por escrita do
        # agente interrompido
        a = self.serie("cur", "curador", [CARO])
        b = self.serie("ava", "avaliador", [CARO])                  # montada antes: a montagem é edição da pessoa
        pidf = self.tmp / "agente.pid"
        env = dict(self.env, FALSO_MODO="sessao-e-dorme", FALSO_PID=str(pidf))
        p = subprocess.Popen([BASH, str(SERIE), str(a), "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                              str(FX / "precos")], cwd=str(self.r), env=env, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, start_new_session=True)
        agente = 0
        try:
            for _ in range(300):
                if pidf.exists() and pidf.read_text(encoding="utf-8").strip():
                    break
                time.sleep(0.1)
            else:
                self.fail("o agente falso não começou")
            agente = int(pidf.read_text(encoding="utf-8").strip())
        finally:
            for alvo in ([lambda: os.killpg(p.pid, signal.SIGKILL)]
                         + ([lambda: os.kill(agente, signal.SIGKILL)] if agente > 0 else [])):
                try:
                    alvo()
                except OSError:
                    pass
            p.wait()
        time.sleep(0.5)
        self.assertEqual(self.rodar(b)[0], 20)                      # para pela interrompida da outra série
        self.assertTrue((b / "PARADA.txt").exists())
        rc, out, _ = self.rodar(a)
        self.assertEqual(rc, 0, out)
        self.assertIn("fronteira conferida", out)

    def test_snapshot_que_falha_nao_deixa_execucao_interrompida(self):
        # R3 da revisão do código: o inicio.txt antes do snapshot virava "interrompida" com n/d e travava a medição
        s = self.serie("cur", "curador", [CARO])
        b = self.tmp / "bin"
        shutil.copytree(str(RAIZ / "sdd/bin"), str(b))
        (b / "governanca-fronteira.sh").write_text("#!/usr/bin/env bash\nexit 1\n", encoding="utf-8")
        rc, _, err = self.roda([BASH, b / "papel-serie.sh", s, "--cmd", 'bash "%s"' % AGENTE.as_posix(), "--precos",
                                FX / "precos"], self.r)
        self.assertEqual(rc, 64, err)
        self.assertIn("snapshot", err)
        self.assertEqual(self.chamadas(), [])
        self.assertEqual(list(s.rglob("inicio.txt")), [])
        rc, out, _ = self.rodar(s)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("interrompida", out)

    def test_interrompida_de_outra_serie_para_antes_de_chamar(self):
        # R5 da revisão do código: o gasto da interrompida de outra série ficaria fora do acumulado
        a = self.serie("cur", "curador", [CARO])
        self.escreve(a, "execucoes/c1/caro/1/inicio.txt", "copia: %s\ncandidato: caro\ninicio: x\n" % (self.tmp / "x"))
        b = self.serie("ava", "avaliador", [CARO])
        rc, out, _ = self.rodar(b)
        self.assertEqual(rc, 20, out)
        self.assertIn("interrompida sem custo medido em outra série", out)
        self.assertIn(os.path.join("cur", "execucoes", "c1", "caro", "1"),
                      (b / "PARADA.txt").read_text(encoding="utf-8"))
        self.assertEqual(self.chamadas(), [])

    def test_papel_sem_pontuador_com_candidatos_nao_paga_a_referencia(self):
        # R6 da revisão do código: antes, a referência inteira rodava e o 64 do medidor virava "fora da meta" (22)
        self.escreve(self.r, "gab/k1/caso.txt", "papel: cartografo\ncommit: -\n")
        self.escreve(self.r, "gab/k1/brief.md", "mapeie @COPIA@\n")
        s = self.serie("car", "cartografo", [CARO, BARATO])
        rc, out, err = self.rodar(s)
        self.assertEqual(rc, 64, out + err)
        self.assertIn("sem pontuador", err)
        self.assertEqual(self.chamadas(), [])

    def test_serie_cmd_entre_aspas_no_yaml_desfaz_os_escapes(self):
        # R7 da revisão do código: \" ficava literal e o bash -c procurava um arquivo com aspas no nome
        self.escreve(self.r, "sdd/config.yaml", 'papeis:\n  serie_cmd: "bash \\"%s\\""\n' % AGENTE.as_posix())
        s = self.serie("cur", "curador", [CARO])
        rc, out, err = self.roda([BASH, SERIE, s, "--precos", FX / "precos"], self.r)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(len(self.chamadas()), 1)
        self.assertIn("rc: 0", (s / "execucoes/c1/caro/1/meta.txt").read_text(encoding="utf-8"))


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

    def test_modo_contrato_despacha_como_revisor_design(self):
        # R2 da rodada 2: pelo nome avaliador, a parada diria o modelo do modo veredito
        texto = ESCADA.read_text(encoding="utf-8")
        secao = texto[texto.index("## Modelo do papel e marca de papel"):]
        self.assertIn("modo\n   `contrato` despacha e marca como `revisor-design` (`despachar revisor-design", secao)

    def test_escada_le_o_slot_antes_de_marcar_o_inicio(self):
        # R3 da rodada 3: marcar antes e sair 64 deixava um início sem fim, que alarga a janela do papel
        texto = ESCADA.read_text(encoding="utf-8")
        secao = texto[texto.index("## Modelo do papel e marca de papel"):]
        self.assertLess(secao.index("sdd-fluxo.sh modelo <slot>"), secao.index("marca-fase.sh inicio papel-<papel>"))
        self.assertIn("e, se não saiu 64,", secao)

    def test_doc_do_limiar_diz_queda_minima(self):
        # R4 da rodada 2: o código escolhe com queda de pelo menos --limiar%; a doc dizia o contrário
        self.assertIn("costs at least `--limiar`% less than the reference",
                      (RAIZ / "docs/model-per-role.md").read_text(encoding="utf-8"))
        self.assertIn("custa pelo menos `--limiar`% menos que a referência",
                      (RAIZ / "docs/pt-BR/model-per-role.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
