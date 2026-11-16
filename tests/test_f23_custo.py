"""F23, fatia B1 — custo por fase e por feature (DEFINE_F23_ECONOMIA_MENSURAVEL: AT-001 a AT-010).

sdd/bin/marca-fase.sh grava as marcas de fase no trace; sdd/bin/adapters/sessao-claude.py e sessao-codex.py leem os
registros locais dos agentes e devolvem só números; sdd/bin/custo-feature.sh soma por fase e por feature.

As fixtures de sdd/fixtures/custo/ são inventadas (README de lá). Cada número esperado abaixo foi feito à mão, a
partir das tarifas inventadas da fixture (US$ por milhão de tokens: modelo-a 3,00 entrada, 15,00 saída, 0,30 cache
lido, 3,75 cache criado; modelo-c 1,25 e 10,00, sem preço de cache):

  define    m1 (10, 100, 1000 lido, 200 criado) = 0,000030 + 0,001500 + 0,000300 + 0,000750 = 0,002580
            m4 do subagente (100, 10)            = 0,000300 + 0,000150                       = 0,000450 → 0,003030
  sem fase  m2 (5, 50, 2000 lido)                = 0,000015 + 0,000750 + 0,000600            = 0,001365
  build     m3 (modelo com "|" → "?", sem preço) e as 2 mensagens do codex (cache sem preço) → n/d
  revisão   1,5000 + 0,0200 (110000, pelo docs_sdd) + ≈0,5000 + 0,0100 (130000, citada pelo ledger) = ≈2,0300
            pago: só o openrouter (pay-per-token) = 0,0300; a 120000 é de outra feature e fica de fora
  total     0,003030 + 0,001365 + 2,0300 = 2,034395 → ≈2.0344 + n/d

O script só lê: não chama modelo, não usa rede.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

import os
import unittest

from apoio import BASH, RAIZ, SEM_SYMLINK, Sandbox

MARCA = RAIZ / "sdd/bin/marca-fase.sh"
CUSTO = RAIZ / "sdd/bin/custo-feature.sh"
LEITOR_CLAUDE = RAIZ / "sdd/bin/adapters/sessao-claude.py"
LEITOR_CODEX = RAIZ / "sdd/bin/adapters/sessao-codex.py"
ER = RAIZ / "sdd/bin/eval-revisores.sh"
FX = RAIZ / "sdd/fixtures/custo"
F = "F99_TESTE"
SEGREDOS = ("segredo-ficticio-123", "/pasta-secreta/segredo.txt", "texto da conversa", "segundo pedido", "cat ",
            "forjado", "linha | falsa")
FASES = ("brainstorm", "define", "ux-review", "design", "build", "release")


def pasta_claude(raiz: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(raiz.resolve()).replace("\\", "/"))


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.raiz = self.repo("projeto")
        # sessões do Claude Code na pasta que o leitor deriva da raiz
        claude = self.tmp / "claude-config"
        proj = claude / "projects" / pasta_claude(self.raiz)
        shutil.copytree(str(FX / "claude"), str(proj))
        # sessões do Codex, com a pasta de trabalho trocada pela raiz deste teste
        codex = self.tmp / "codex-home"
        shutil.copytree(str(FX / "codex"), str(codex))
        for arq in (codex / "sessions").rglob("*.jsonl"):
            txt = arq.read_text(encoding="utf-8").replace("__RAIZ__", str(self.raiz.resolve()).replace("\\", "/"))
            arq.write_text(txt, encoding="utf-8")
        self.copiado = {"traces": self.raiz / "sdd/traces", "reviews": self.raiz / "sdd/reports/reviews",
                        "ledgers": self.raiz / "sdd/reviews", "precos": self.tmp / "precos"}
        for nome, alvo in self.copiado.items():
            shutil.copytree(str(FX / nome), str(alvo))
        self.env = dict(self.env, CLAUDE_CONFIG_DIR=str(claude), CODEX_HOME=str(codex))

    def custo(self, *args: str, cwd: Path | None = None) -> tuple[int, str, str]:
        return self.roda([BASH, CUSTO, *args], cwd or self.raiz)

    def custo_padrao(self) -> tuple[int, str, str]:
        return self.custo(F, "--precos", str(self.copiado["precos"]))

    @staticmethod
    def tabela(texto: str) -> dict:
        linhas = {}
        for ln in texto.splitlines():
            c = [x.strip() for x in ln.split("|")][1:-1]
            if len(c) == 9 and c[0] not in ("Fase",) and not c[0].startswith("---"):
                linhas[c[0]] = c[1:]
        return linhas


class AT001Marca(Sandbox):
    """AT-001: marca de início e fim no trace; recusa de controle (S17); SDD_TRACE=off (Where)."""

    def setUp(self):
        super().setUp()
        self.r = self.repo()

    def marca(self, *args: str, env: dict | None = None, cwd: Path | None = None):
        return self.roda([BASH, MARCA, *args], cwd or self.r, env)

    def linhas(self, base: Path | None = None) -> list:
        arq = (base or self.r) / "sdd/traces/F23_X.jsonl"
        return [json.loads(x) for x in arq.read_text(encoding="utf-8").splitlines()] if arq.exists() else []

    def test_inicio_e_fim_acrescentam_uma_linha_cada_sem_apagar(self):
        self.escreve(self.r, "sdd/traces/F23_X.jsonl",
                     '{"ts":"2026-11-15T09:00:00Z","feature":"F23_X","src":"verify-gate","kind":"test","exit":2}\n')
        for evento in ("inicio", "fim"):
            rc, out, err = self.marca(evento, "define", "F23_X")
            self.assertEqual(rc, 0, err)
            self.assertIn("RESULTADO: MARCADO", out)
        ls = self.linhas()
        self.assertEqual(len(ls), 3)
        self.assertEqual(ls[0]["src"], "verify-gate")
        for linha, evento in zip(ls[1:], ("inicio", "fim")):
            self.assertEqual({k: linha[k] for k in ("feature", "src", "evento", "fase")},
                             {"feature": "F23_X", "src": "fase", "evento": evento, "fase": "define"})
            self.assertRegex(linha["ts"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_controle_quebra_de_linha_e_tabulacao_sao_recusados_sem_gravar(self):
        forjada = '{"ts":"2026-01-01T00:00:00Z","feature":"F23_X","src":"fase","evento":"inicio","fase":"build"}'
        casos = [("inicio", "x\n" + forjada + "\nok", "F23_X"),   # quebra no meio: a última linha casaria sozinha
                 ("inicio", "define\n", "F23_X"),                  # quebra no fim
                 ("inicio", "de\tfine", "F23_X"),
                 ("inicio", "define", "F23_X\nok"),
                 ("inicio", "define", "F23 X"),
                 ("inicio", "define", 'F23"X'),
                 ("inicio", "Define", "F23_X"),
                 ("comeco", "define", "F23_X")]
        for args in casos:
            with self.subTest(args=args):
                rc, out, err = self.marca(*args)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: PAROU", err)
        self.assertEqual(self.linhas(), [])

    def test_sdd_trace_off_nao_grava(self):
        rc, out, _ = self.marca("inicio", "build", "F23_X", env=dict(self.env, SDD_TRACE="off"))
        self.assertEqual(rc, 0)
        self.assertIn("RESULTADO: DESLIGADO", out)
        self.assertEqual(self.linhas(), [])

    def test_sdd_trace_dir_e_fora_de_repositorio(self):
        fora = self.tmp / "sem-git"
        fora.mkdir()
        rc, _, err = self.marca("fim", "release", "F23_X", cwd=fora)
        self.assertEqual(rc, 0, err)
        self.assertEqual(len(self.linhas(fora)), 1)
        outra = self.tmp / "traces-aqui"
        rc, _, err = self.marca("inicio", "design", "F23_X", env=dict(self.env, SDD_TRACE_DIR=str(outra)))
        self.assertEqual(rc, 0, err)
        self.assertTrue((outra / "F23_X.jsonl").is_file())


class AT002Leitores(Base):
    """AT-002 e AT-006: só números saem; repetição agrupada; subagente; sessão da revisão (outra pasta) fora."""

    def leitor(self, prog: Path) -> tuple[int, list, str]:
        rc, out, err = self.roda([sys.executable, "-B", prog, "--raiz", self.raiz], self.raiz)
        return rc, [json.loads(x) for x in out.splitlines() if x.strip()], out

    def test_claude_agrupa_a_mesma_mensagem_e_conta_o_subagente(self):
        sessao = self.tmp / "claude-config/projects" / pasta_claude(self.raiz) / "sessao-1.jsonl"
        with open(sessao, "a", encoding="utf-8") as h:
            h.write("{isto não é json\n")
        rc, regs, out = self.leitor(LEITOR_CLAUDE)
        self.assertEqual(rc, 0)
        msgs = [r for r in regs if r["tipo"] == "msg"]
        self.assertEqual(len(msgs), 4)   # m1 (3 linhas) + m2 + m3 + m4 do subagente
        m1 = next(m for m in msgs if m["t"].startswith("2026-11-15T10:00:05"))
        self.assertEqual((m1["entrada"], m1["saida"], m1["cache_lido"], m1["cache_criado"]), (10, 100, 1000, 200))
        self.assertEqual([r["t"][:19] for r in regs if r["tipo"] == "turno"],
                         ["2026-11-15T10:00:00", "2026-11-15T10:10:00"])   # tool_result, isMeta e subagente não são turno
        self.assertEqual([r for r in regs if r["tipo"] == "ilegivel"], [{"tipo": "ilegivel", "n": 1}])
        self.assertEqual({m["modelo"] for m in msgs}, {"modelo-a", "?"})

    def test_nenhum_texto_sai_dos_leitores(self):
        for prog in (LEITOR_CLAUDE, LEITOR_CODEX):
            with self.subTest(prog=prog.name):
                rc, regs, out = self.leitor(prog)
                self.assertEqual(rc, 0)
                for s in SEGREDOS:
                    self.assertNotIn(s, out)
                for r in regs:
                    self.assertLessEqual(set(r), {"tipo", "t", "modelo", "entrada", "saida", "cache_lido",
                                                  "cache_criado", "n"})

    def test_codex_diferenca_de_totais_e_cache_fora_da_entrada(self):
        rc, regs, _ = self.leitor(LEITOR_CODEX)
        self.assertEqual(rc, 0)
        msgs = [(r["entrada"], r["saida"], r["cache_lido"], r["cache_criado"]) for r in regs if r["tipo"] == "msg"]
        # 1º total (1000, 600 em cache, 10); o repetido é descartado; 2º total (1500, 700, 30) dá a diferença
        self.assertEqual(msgs, [(400, 10, 600, 0), (400, 20, 100, 0)])
        self.assertEqual([r["t"][:19] for r in regs if r["tipo"] == "turno"], ["2026-11-15T10:20:00"])
        # a sessão da revisão (90.000 tokens, outra pasta de trabalho) nunca entra
        self.assertNotIn(90000, [r.get("entrada") for r in regs])

    def test_sem_registro_sai_2(self):
        outra = self.tmp / "outra"
        outra.mkdir()
        for prog in (LEITOR_CLAUDE, LEITOR_CODEX):
            with self.subTest(prog=prog.name):
                rc, out, err = self.roda([sys.executable, "-B", prog, "--raiz", outra], outra)
                self.assertEqual(rc, 2, out + err)
                self.assertIn("SEM REGISTRO", err)
                rc, _, err = self.roda([sys.executable, "-B", prog], outra)
                self.assertEqual(rc, 64)


class AT003Contador(Base):
    """AT-003 a AT-007: a tabela inteira, célula por célula, com a conta à mão do docstring."""

    def test_tabela_por_fase_sem_fase_revisao_e_total(self):
        rc, out, err = self.custo_padrao()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: MEDIDO", out)
        arq = self.raiz / "sdd/reports/CUSTO_F99_TESTE.md"
        self.assertTrue(arq.is_file())
        t = self.tabela(arq.read_text(encoding="utf-8"))
        #                  execuções, entrada, saída, cache lido, cache criado, pago, nominal, tempo ativo
        self.assertEqual(t["define"], ["1", "110", "110", "1000", "200", "0.0000", "0.0030", "0h05m00s"])
        self.assertEqual(t["build"], ["1", "801", "31", "700", "0", "0.0000", "n/d", "0h01m00s"])
        self.assertEqual(t["sem fase"], ["0", "5", "50", "2000", "0", "0.0000", "0.0014", "0h01m00s"])
        self.assertEqual(t["revisão"], ["2", "1500", "250", "0", "0", "0.0300", "≈2.0300", "0h08m00s"])
        self.assertEqual(t["**total**"], ["4", "2416", "441", "3700", "200", "0.0300", "≈2.0344 + n/d", "0h15m00s"])
        self.assertEqual(list(t), ["define", "build", "sem fase", "revisão", "**total**"])

    def test_voltas_do_gate_avisos_e_nenhum_texto(self):
        rc, out, _ = self.custo_padrao()
        self.assertEqual(rc, 0)
        self.assertIn("Voltas do Verify Gate: 2 (verde na 2ª).", out)
        self.assertIn("fase sem fim: build (fechada no fim da última sessão)", out)   # AT-007
        self.assertIn("claude · ? (entrada e saída, precos.tsv)", out)                # AT-004
        self.assertIn("codex · modelo-c (cache, precos-cache.tsv)", out)              # AT-005
        self.assertIn("claude LIDO · codex LIDO", out)
        for s in SEGREDOS:
            self.assertNotIn(s, out)

    def test_cache_sem_preco_nunca_vira_preco_de_entrada(self):
        """AT-005 — mutante: sem a precos-cache.tsv, o define (que tem cache) sai n/d, não só entrada e saída."""
        (self.copiado["precos"] / "precos-cache.tsv").unlink()
        rc, out, _ = self.custo(F, "--precos", str(self.copiado["precos"]), "--saida", "-")
        self.assertEqual(rc, 0)
        t = self.tabela(out)
        self.assertEqual(t["define"][6], "0.0004 + n/d")   # só m4, sem cache: 0,000450 (meio par, como o eval-revisores.sh); m1 tem cache → n/d
        self.assertEqual(t["sem fase"][6], "n/d")

    def test_leitor_que_falha_e_n_d_nunca_zero(self):
        """AT-004: sem preço nenhum, toda célula de sessão é n/d e o total diz + n/d."""
        vazia = self.tmp / "sem-precos"
        vazia.mkdir()
        rc, out, _ = self.custo(F, "--precos", str(vazia), "--saida", "-")
        self.assertEqual(rc, 0)
        t = self.tabela(out)
        for fase in ("define", "build", "sem fase"):
            self.assertEqual(t[fase][6], "n/d")
        self.assertEqual(t["**total**"][6], "≈2.0300 + n/d")

    def test_sem_marca_as_sessoes_ficam_n_d_com_aviso(self):
        """R6 da revisão do DESIGN: sem marca, a linha sem fase é n/d, nunca um zero que parece economia."""
        (self.copiado["traces"] / "F99_TESTE.jsonl").unlink()
        rc, out, _ = self.custo(F, "--precos", str(self.copiado["precos"]), "--saida", "-")
        self.assertEqual(rc, 0, out)
        t = self.tabela(out)
        self.assertEqual(t["sem fase"][6], "n/d")
        self.assertIn("nenhuma marca de fase: as sessões não foram atribuídas", out)

    def test_soma_exata_em_decimal(self):
        """0,1 + 0,2 em ponto flutuante não dá 0,3 exato; em decimal, sim."""
        self.escreve(self.raiz, "sdd/reports/reviews/EXTERNAL_REVIEW_20261115-140000/META.txt",
                     "docs_sdd : DEFINE_F99_TESTE.md\nreviewer_engine_efetivo : openrouter\nreviewer_exit : 0\n"
                     "reviewer_custo : US$ 0.1\nauditor_engine_efetivo : openrouter\nauditor_exit : 0\n"
                     "auditor_custo : US$ 0.2\n")
        rc, out, _ = self.custo(F, "--precos", str(self.copiado["precos"]), "--saida", "-")
        self.assertEqual(rc, 0)
        self.assertEqual(self.tabela(out)["revisão"][5], "0.3300")   # 0,02 + 0,01 + 0,1 + 0,2

    def test_sem_dados_e_uso(self):
        outra = self.repo("vazio")
        rc, out, _ = self.custo("F99_NADA", cwd=outra)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: SEM DADOS", out)
        for args in (("F 99",), (), ("F99", "--saida"), ("F99", "--nada", "x"), ("F99", "--precos", "/nao/existe")):
            with self.subTest(args=args):
                rc, _, err = self.custo(*args)
                self.assertEqual(rc, 64, err)
                self.assertIn("RESULTADO: PAROU", err)


class AT004NuncaZero(Base):
    """AT-004 e R1 a R5 da revisão do código: o que não foi lido vira n/d em toda linha afetada, nunca zero."""

    def tabela_saida(self, *extra: str, raiz: Path | None = None) -> tuple[dict, str]:
        rc, out, err = self.custo(F, "--precos", str(self.copiado["precos"]), "--saida", "-", *extra)
        self.assertEqual(rc, 0, out + err)
        return self.tabela(out), out

    def test_fase_marcada_sem_mensagem_lida_e_n_d(self):
        """R1: uma fase com marca e nenhuma mensagem (agente sem leitor, sessão não achada) não sai 0.0000."""
        with open(self.copiado["traces"] / "F99_TESTE.jsonl", "a", encoding="utf-8") as h:
            h.write('{"ts":"2026-11-15T10:40:00Z","feature":"F99_TESTE","src":"fase","evento":"inicio","fase":"design"}\n')
            h.write('{"ts":"2026-11-15T10:50:00Z","feature":"F99_TESTE","src":"fase","evento":"fim","fase":"design"}\n')
        t, out = self.tabela_saida()
        self.assertEqual(t["design"], ["1", "0", "0", "0", "0", "n/d", "n/d", "0h00m00s"])
        self.assertIn("nenhuma mensagem lida em design", out)
        self.assertIn("+ n/d", t["**total**"][5])

    def test_linha_ilegivel_deixa_toda_linha_da_janela_parcial(self):
        """R2: não se sabe a que fase a linha perdida pertencia: toda linha da janela vira parcial."""
        sessao = self.tmp / "claude-config/projects" / pasta_claude(self.raiz) / "sessao-1.jsonl"
        with open(sessao, "a", encoding="utf-8") as h:
            h.write("{isto não é json\n")
        t, out = self.tabela_saida()
        self.assertEqual(t["define"][5:7], ["0.0000 + n/d", "0.0030 + n/d"])
        self.assertEqual(t["sem fase"][6], "0.0014 + n/d")
        self.assertEqual(t["**total**"][5], "0.0300 + n/d")
        self.assertIn("1 linha(s) ilegível(is)", out)

    def test_leitor_que_falha_deixa_toda_linha_da_janela_parcial(self):
        """R3: um leitor que sai com erro não some: toda fase e o sem fase ganham n/d."""
        pkg = self.tmp / "pacote"
        shutil.copytree(str(RAIZ / "sdd/bin"), str(pkg / "sdd/bin"))
        shutil.copytree(str(RAIZ / "sdd/review"), str(pkg / "sdd/review"))
        (pkg / "sdd/bin/adapters/sessao-quebrado.py").write_text("import sys\nsys.exit(1)\n", encoding="utf-8")
        rc, out, err = self.roda([BASH, pkg / "sdd/bin/custo-feature.sh", F, "--precos", self.copiado["precos"],
                                  "--saida", "-"], self.raiz)
        self.assertEqual(rc, 0, out + err)
        t = self.tabela(out)
        self.assertEqual(t["define"][6], "0.0030 + n/d")
        self.assertEqual(t["sem fase"][6], "0.0014 + n/d")
        self.assertIn("quebrado FALHOU (exit 1)", out)

    def test_docs_sdd_com_caminho_e_outro_separador(self):
        """R4: o META que traz caminho ou ponto e vírgula continua atribuído à feature."""
        self.escreve(self.raiz, "sdd/reports/reviews/EXTERNAL_REVIEW_20261115-150000/META.txt",
                     "docs_sdd : sdd/features/DEFINE_F99_TESTE.md; sdd/features/DESIGN_F99_TESTE.md\n"
                     "reviewer_engine_efetivo : openrouter\nreviewer_exit : 0\nreviewer_custo : US$ 1.0000\n")
        t, _ = self.tabela_saida()
        self.assertEqual(t["revisão"][0], "3")
        self.assertEqual(t["revisão"][5], "1.0300")

    @unittest.skipIf(*SEM_SYMLINK)
    def test_raiz_por_link_simbolico_acha_as_sessoes(self):
        """R5: o agente grava o caminho físico; a raiz dada por um link simbólico é resolvida antes."""
        link = self.tmp / "atalho"
        os.symlink(str(self.raiz), str(link))
        t, out = self.tabela_saida("--raiz", str(link))
        self.assertIn("claude LIDO · codex LIDO", out)
        self.assertEqual(t["define"][6], "0.0030")


class AT006Revisao(Base):
    """AT-006 e Decision 8: o nominal da revisão bate com o eval-revisores.sh sobre as mesmas pastas."""

    def test_nominal_da_revisao_bate_com_o_eval_revisores(self):
        so_feature = self.tmp / "so-f99"
        so_feature.mkdir()
        for n in ("EXTERNAL_REVIEW_20261115-110000", "EXTERNAL_REVIEW_20261115-130000"):
            shutil.copytree(str(FX / "reviews" / n), str(so_feature / n))
        rc, out, err = self.roda([BASH, ER, so_feature, "--ledgers", self.tmp / "nenhum-ledger"], self.raiz)
        if rc == 64:   # --ledgers inexistente: usa uma pasta vazia
            vazia = self.tmp / "ledgers-vazio"
            vazia.mkdir()
            rc, out, err = self.roda([BASH, ER, so_feature, "--ledgers", vazia], self.raiz)
        self.assertEqual(rc, 0, out + err)
        soma = 0.0
        for ln in out.splitlines():
            c = [x.strip() for x in ln.split("|")][1:-1]
            if len(c) == 16 and c[0] in ("revisor", "auditor"):
                soma += float(re.match(r"≈?([0-9.]+)", c[6]).group(1))
        self.assertAlmostEqual(soma, 2.03, places=6)
        rc, out, _ = self.custo(F, "--precos", str(self.copiado["precos"]), "--saida", "-")
        self.assertEqual(self.tabela(out)["revisão"][6], "≈2.0300")


class AT008LinhaDeBase(Base):
    """AT-008: uma linha por feature, sem divisão por fase."""

    def test_mapa_com_duas_features(self):
        mapa = self.escreve(self.tmp, "mapa.tsv",
                            "# feature\traiz\tledger\n"
                            "F99_TESTE\t%s\t%s\n" % (self.raiz, self.copiado["ledgers"] / "LEDGER_REVISAO_F99_TESTE.md")
                            + "F98_SEM_NADA\t%s\t-\n" % (self.tmp / "nao-existe"))
        rc, out, err = self.custo("--linha-de-base", str(mapa), "--precos", str(self.copiado["precos"]),
                                  "--reviews", str(self.copiado["reviews"]))
        self.assertEqual(rc, 0, out + err)
        linhas = {c[0]: c[1:] for c in ([x.strip() for x in ln.split("|")][1:-1] for ln in out.splitlines())
                  if len(c) == 5 and c[0].startswith("F9")}
        # sessões: m1 + m4 + m2 = 0,004395 → 0.0044; m3 e o codex sem preço → + n/d
        self.assertEqual(linhas["F99_TESTE"], ["0.0044 + n/d", "≈2.0300", "2", "1"])
        self.assertEqual(linhas["F98_SEM_NADA"], ["n/d", "n/d", "—", "—"])
        self.assertIn("RESULTADO: MEDIDO", out)

    def test_mapa_invalido(self):
        mapa = self.escreve(self.tmp, "mapa.tsv", "só uma coluna\n")
        rc, _, err = self.custo("--linha-de-base", str(mapa))
        self.assertEqual(rc, 64)
        rc, _, err = self.custo("--linha-de-base", str(mapa), "F99")
        self.assertEqual(rc, 64)


class AT009Skills(Sandbox):
    """AT-009: as 6 skills de fase mandam marcar início e fim; a release roda o contador; nenhuma passa de 500."""

    def test_skills_de_fase_marcam(self):
        for fase in FASES:
            with self.subTest(fase=fase):
                txt = (RAIZ / (".agents/skills/sdd-%s/SKILL.md" % fase)).read_text(encoding="utf-8")
                self.assertRegex(txt, r"marca-fase\.sh inicio %s (<FEATURE>|\{F\})" % fase)
                self.assertRegex(txt, r"marca-fase\.sh fim %s (<FEATURE>|\{F\})" % fase)
                self.assertLessEqual(len(txt.splitlines()), 500)
        release = (RAIZ / ".agents/skills/sdd-release/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("bash sdd/bin/custo-feature.sh {F}", release)
        self.assertIn("sdd/reports/CUSTO_{F}.md", release)
        frag = (RAIZ / "sdd/templates/fragments/MARCA_FASE.md").read_text(encoding="utf-8")
        for fase in FASES:
            self.assertIn("`%s`" % fase, frag)

    def test_pacote_sem_preco_de_modelo_no_cache(self):
        """Vendor-agnóstico: a precos-cache.tsv do pacote só tem o cabeçalho."""
        linhas = [x for x in (RAIZ / "sdd/review/precos-cache.tsv").read_text(encoding="utf-8").splitlines()
                  if x.strip() and not x.startswith("#")]
        self.assertEqual(linhas, [])
