"""sdd/bin/sdd-fluxo.sh — os decisores do fluxo encadeado (F9), verbo por verbo, dos dois lados.

Cada teste roda o script do pacote de verdade, por subprocess, contra as fixtures de sdd/fixtures/fluxo/
(rastreadas: o Verify Gate roda numa cópia por `git archive`, sem sdd/features/) ou contra um repositório
temporário montado aqui. O contrato é o exit e a linha de saída (ESTADO:, EXIGIDO:, PARAR:, a linha de
transição, a parada ⏸️), nunca a implementação. Também confere o texto que liga o mecanismo às skills:
a subseção `### Fluxo encadeado` das 9 skills de fase, os itens F6/F8/F10/F11 do PORTE e os slots.
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

FLUXO = RAIZ / "sdd/bin/sdd-fluxo.sh"
FX = RAIZ / "sdd/fixtures/fluxo"
SKILLS = RAIZ / ".agents/skills"
FASE = ("sdd-brainstorm", "sdd-define", "sdd-governanca", "sdd-ux-review", "sdd-design", "sdd-build",
        "sdd-iterate", "sdd-release", "sdd-new-session")
ENCADEIAM = ("sdd-define", "sdd-governanca", "sdd-ux-review", "sdd-design")
LEDGER_CAB = "| achado | sev | veredito | rodada | evidência |\n|---|---|---|---|---|\n"
FERRAMENTAS = ("bash", "sh", "git", "sed", "grep", "dirname", "cat", "mktemp", "rm", "env")


def ler(p) -> str:
    return Path(p).read_text(encoding="utf-8")


class Base(Sandbox):
    def fluxo(self, *args, cwd=None, env=None):
        rc, out, err = self.roda([BASH, FLUXO, *args], cwd or self.tmp, env)
        return rc, out + err

    def projeto(self, autonomo=True) -> Path:
        r = self.repo()
        (r / "sdd/features").mkdir(parents=True)
        if autonomo is not None:
            self.escreve(r, "sdd/config.yaml", "flow:\n  autonomous: %s\n" % ("true" if autonomo else "false"))
        return r

    def poe(self, r: Path, fixture: str, nome: str) -> Path:
        alvo = r / "sdd/features" / nome
        shutil.copy(str(FX / fixture), str(alvo))
        return alvo


class ReviewDesign(Base):
    def test_tres_arquivos_novos_exige_e_modify_nao_conta(self):
        rc, out = self.fluxo("review-design", FX / "DESIGN_novos.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("EXIGIDO: 3 arquivo(s) novo(s) (limiar 3)", out)

    def test_titulo_numerado_com_qualificador_e_acoes_novo_new(self):
        rc, out = self.fluxo("review-design", FX / "DESIGN_numerado.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("EXIGIDO: 3 arquivo(s) novo(s)", out)

    def test_termo_de_seguranca_exige_com_um_arquivo_novo(self):
        rc, out = self.fluxo("review-design", FX / "DESIGN_seguranca.md")
        self.assertEqual(rc, 0, out)
        self.assertIn("superfície de segurança (termo login)", out)
        self.assertNotIn("limiar 3", out)

    def test_dispensavel(self):
        rc, out = self.fluxo("review-design", FX / "DESIGN_dispensavel.md")
        self.assertEqual(rc, 1, out)
        self.assertIn("DISPENSAVEL: 2 arquivo(s) novo(s), sem superfície de segurança no manifest", out)

    def test_glob_do_slot_e_de_layers_sql_exigem(self):
        r = self.repo()
        self.escreve(r, "sdd/config.yaml", 'review:\n  security_globs: "api/public/**, x/*"\nlayers:\n  sql: "db/migrations/**"\n')
        base = ler(FX / "DESIGN_dispensavel.md")
        for caminho, sinal in (("api/public/rota.ts", "glob api/public/**"), ("db/migrations/001.sql", "glob db/migrations/**")):
            with self.subTest(caminho=caminho):
                d = self.escreve(r, "sdd/features/DESIGN_G.md", base.replace("tests/test_mensal.py", caminho))
                rc, out = self.fluxo("review-design", d, cwd=r)
                self.assertEqual(rc, 0, out)
                self.assertIn(sinal, out)
        rc, out = self.fluxo("review-design", self.escreve(r, "sdd/features/DESIGN_H.md", base), cwd=r)
        self.assertEqual(rc, 1, out)

    def test_manifest_ilegivel_sai_64_com_o_default_seguro(self):
        sem_linhas = self.escreve(self.tmp, "D.md", "# D\n\n## File Manifest\n\n| # | File | Action |\n|---|---|---|\n")
        for d in (FX / "DESIGN_sem_manifest.md", sem_linhas, self.tmp / "nao-existe.md"):
            with self.subTest(design=d.name):
                rc, out = self.fluxo("review-design", d)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: MANIFEST ILEGÍVEL", out)
                self.assertIn("default seguro", out)


class Loop(Base):
    def loop(self, review, *extra, rodada="1"):
        return self.fluxo("loop", "--review", FX / review if isinstance(review, str) else review,
                          "--rodada", rodada, *extra)

    def ledger(self, linhas: str) -> Path:
        return self.escreve(self.tmp, "ledger.md", LEDGER_CAB + linhas)

    def test_pronto_com_rebatida_e_justificativa_que_cita_outro_veredito(self):
        rc, out = self.loop("review-ok", "--ledger", FX / "ledger-rebatida.md",
                            "--avaliacao", FX / "AVALIACAO_pass.md", "--ciclo-avaliador", "1")
        self.assertEqual(rc, 0, out)
        for linha in ("ESTADO: PRONTO", "rodada: 1 de 3", "graves_abertos: 0", "rebatidas: 1", "RESULTADO: PRONTO"):
            self.assertIn(linha, out)

    def test_continuar_por_cada_causa(self):
        casos = (
            ("aplicada", ("review-ok", "--ledger", FX / "ledger-aplicada.md"), "exige nova review"),
            ("sem ledger", ("review-ok",), "grave(s) sem veredito no ledger: R1@rev"),
            ("outra rodada", ("review-ok", "--ledger", self.ledger("| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=2 | x |\n")), "sem veredito"),
            ("linha MED", ("review-ok", "--ledger", self.ledger("| R1@rev | MED | REBATIDA_EVIDENCIA | rodada=1 | x |\n")), "sem veredito"),
            ("needs work", ("review-ok", "--ledger", FX / "ledger-rebatida.md", "--avaliacao",
                            FX / "AVALIACAO_needs_work.md", "--ciclo-avaliador", "1"), "NEEDS_WORK (ciclo 1)"),
        )
        for nome, args, motivo in casos:
            with self.subTest(caso=nome):
                rc, out = self.loop(*args)
                self.assertEqual(rc, 10, out)
                self.assertIn("ESTADO: CONTINUAR", out)
                self.assertIn(motivo, out)

    def test_review_invalida_nao_le_os_jsonl_e_sai_10(self):
        d = self.tmp / "inv"
        d.mkdir()
        shutil.copy(str(FX / "review-invalida/META.txt"), str(d / "META.txt"))
        rc, out = self.loop(d)
        self.assertEqual(rc, 10, out)
        self.assertIn("review inválida (reviewer_exit=0 auditor_exit=68)", out)

    def test_bloqueado_d4_teto_d4_ciclos_e_d5(self):
        casos = (
            ("teto", ("review-ok",), "3", "D4 teto"),
            ("ciclos", ("review-ok", "--ledger", FX / "ledger-rebatida.md", "--avaliacao",
                        FX / "AVALIACAO_needs_work.md", "--ciclo-avaliador", "2"), "1", "D4 ciclos"),
            ("impasse", ("review-impasse",), "1", "D5 impasse de evidência"),
        )
        for nome, args, rodada, motivo in casos:
            with self.subTest(caso=nome):
                rc, out = self.loop(*args, rodada=rodada)
                self.assertEqual(rc, 20, out)
                self.assertIn("ESTADO: BLOQUEADO", out)
                self.assertIn(motivo, out)

    def test_bordas_da_fonte_needs_work_no_teto_e_high_com_recibo_pendente_saem_10(self):
        rc, out = self.loop("review-ok", "--ledger", self.ledger("| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=3 | x |\n"),
                            "--avaliacao", FX / "AVALIACAO_needs_work.md", "--ciclo-avaliador", "1", rodada="3")
        self.assertEqual(rc, 10, out)
        rc, out = self.loop("review-ok", "--avaliacao", FX / "AVALIACAO_recibo.md")
        self.assertEqual(rc, 10, out)
        self.assertIn("aguardando o recibo humano", out)

    def test_aguardando_recibo_e_recibo_com_data(self):
        args = ("review-ok", "--ledger", FX / "ledger-rebatida.md", "--avaliacao", FX / "AVALIACAO_recibo.md")
        rc, out = self.loop(*args)
        self.assertEqual(rc, 30, out)
        self.assertIn("ESTADO: AGUARDANDO_RECIBO", out)
        rc, out = self.loop(*args, "--recibo", "sem data")
        self.assertEqual(rc, 30, out)
        rc, out = self.loop(*args, "--recibo", "Fulana 2026-10-31")
        self.assertEqual(rc, 0, out)
        self.assertIn("recibo humano — Fulana 2026-10-31", out)

    def test_entrada_ausente_ou_malformada_sai_64_nunca_0(self):
        def rev(nome, revisor, auditor):
            d = self.tmp / nome
            d.mkdir()
            (d / "META.txt").write_text("reviewer_exit: 0\nauditor_exit: 0\n", encoding="utf-8")
            if revisor is not None:
                (d / "reviewer.verdicts.jsonl").write_text(revisor, encoding="utf-8")
            if auditor is not None:
                (d / "auditor.verdicts.jsonl").write_text(auditor, encoding="utf-8")
            return d
        ok = '{"achado":"R1","severidade":"LOW"}\n'
        casos = (
            ("sem META", (self.tmp,), "META.txt ausente"),
            ("sem jsonl do revisor", (rev("a", None, ""),), "reviewer.verdicts.jsonl ausente"),
            ("linha que não é JSON", (rev("b", "isto não é json\n", ""),), "linha inválida para revisor"),
            ("revisor sem severidade", (rev("c", '{"achado":"R1"}\n', ""),), "linha inválida para revisor"),
            ("auditor com veredito errado", (rev("d", ok, '{"achado":"R1","veredito":"TALVEZ"}\n'),), "linha inválida para auditor"),
            ("NOVO sem severidade", (rev("e", ok, '{"achado":"N1","veredito":"NOVO"}\n'),), "linha inválida para auditor"),
            ("avaliação ambígua", (FX / "review-ok", "--avaliacao", FX / "AVALIACAO_ambigua.md"), "ambígua"),
            ("avaliação sem veredito", (FX / "review-ok", "--avaliacao", FX / "ledger-aplicada.md"), "ambígua"),
            ("ledger ilegível", (FX / "review-ok", "--ledger", self.tmp / "nao-existe.md"), "ledger ilegível"),
        )
        for nome, args, motivo in casos:
            with self.subTest(caso=nome):
                rc, out = self.loop(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn(motivo, out)
        for args in (("--rodada", "x"), ("--rodada", "1", "--teto", "a"), ("--rodada", "1", "--ledger")):
            with self.subTest(args=args):
                rc, out = self.fluxo("loop", "--review", FX / "review-ok", *args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)

    def test_log_grava_o_exit_real_e_tee_e_acusado(self):
        ev = self.tmp / "ev"
        ev.mkdir()
        log = ev / "LOOP-rodada-1.log"
        rc, out = self.loop("review-impasse", "--log", log)
        self.assertEqual(rc, 20, out)
        texto = ler(log)
        self.assertTrue(texto.startswith("$ sdd-fluxo.sh loop "), texto)
        self.assertNotIn("--log", texto.splitlines()[0])
        self.assertTrue(texto.rstrip().endswith("[exit=20]"), texto)
        gate = RAIZ / "sdd/bin/gate-shell-evidencia.sh"
        rc, out, err = self.roda([BASH, gate, ev], self.tmp)
        self.assertEqual(rc, 0, out + err)
        tee = self.tmp / "tee"
        tee.mkdir()
        (tee / "LOOP-rodada-1.log").write_text(
            "$ bash sdd/bin/sdd-fluxo.sh loop --review r --rodada 1 | tee loop.out\nESTADO: BLOQUEADO\n[exit=0]\n",
            encoding="utf-8")
        rc, out, err = self.roda([BASH, gate, tee], self.tmp)
        self.assertEqual(rc, 2, out + err)


class Despachar(Base):
    def test_grava_o_brief_imprime_a_parada_e_sai_40(self):
        r = self.repo()
        rc, out = self.fluxo("despachar", "avaliador", "PAGAMENTOS", FX / "brief-avaliador.md", cwd=r)
        self.assertEqual(rc, 40, out)
        destino = r / "sdd/reports/briefs/BRIEF_avaliador_PAGAMENTOS.md"
        self.assertEqual(ler(destino), ler(FX / "brief-avaliador.md"))
        for rotulo in ("⏸️", "**Por que parei:**", "**Onde:**", "**Passos:**", "1. ", "2. ", "3. ",
                       "**O que não foi feito:**", "**Brief:** sdd/reports/briefs/BRIEF_avaliador_PAGAMENTOS.md",
                       "**Sessão nova:**", "Quando terminar, me peça de novo, eu continuo daqui.",
                       "VEREDITO: …", "RESULTADO: AGUARDANDO_HUMANO", "→ "):
            self.assertIn(rotulo, out)

    def test_retorno_de_outro_papel_e_o_bloco_final(self):
        r = self.repo()
        rc, out = self.fluxo("despachar", "revisor-design", "X", FX / "brief-avaliador.md", cwd=r)
        self.assertEqual(rc, 40, out)
        self.assertIn("o bloco final da resposta (o que começa com <<<)", out)
        self.assertNotIn("VEREDITO: …", out)

    def test_brief_ja_no_destino_por_caminho_relativo_e_absoluto(self):
        r = self.repo()
        destino = self.escreve(r, "sdd/reports/briefs/BRIEF_avaliador_X.md", "modo: veredito\n")
        os.utime(str(destino), (1000000000, 1000000000))
        for caminho in ("sdd/reports/briefs/BRIEF_avaliador_X.md", destino):
            with self.subTest(caminho=str(caminho)):
                rc, out = self.fluxo("despachar", "avaliador", "X", caminho, cwd=r)
                self.assertEqual(rc, 40, out)
                self.assertEqual(ler(destino), "modo: veredito\n")
                self.assertEqual(int(destino.stat().st_mtime), 1000000000)

    def test_erros_saem_64_e_nada_e_gravado(self):
        r = self.repo()
        vazio = self.escreve(self.tmp, "vazio.md", "")
        brief = FX / "brief-avaliador.md"
        for args in (("avaliador", "X", self.tmp / "nao-existe.md"), ("avaliador", "X", vazio),
                     ("../fora", "X", brief), ("avaliador", "X/Y", brief), ("avaliador", "X")):
            with self.subTest(args=[str(a) for a in args]):
                rc, out = self.fluxo("despachar", *args, cwd=r)
                self.assertEqual(rc, 64, out)
                self.assertFalse((r / "sdd/reports/briefs").exists() and any((r / "sdd/reports/briefs").iterdir()))


class Estado(Base):
    def test_ligado_desligado_e_invalido(self):
        casos = ((True, 0, "encadeamento: ligado"), (False, 1, "encadeamento: desligado"),
                 (None, 1, "encadeamento: desligado"))
        for valor, esperado, linha in casos:
            with self.subTest(valor=valor):
                r = self.projeto(valor)
                rc, out = self.fluxo("estado", cwd=r)
                self.assertEqual(rc, esperado, out)
                self.assertIn(linha, out)
                shutil.rmtree(str(r))
        r = self.projeto(None)
        for conteudo, esperado in (("flow:\n  autonomous:\n", 1), ('flow:\n  autonomous: "true"  # liga\n', 0),
                                   ("flow:\n  autonomous: sim\n", 64)):
            with self.subTest(conteudo=conteudo):
                self.escreve(r, "sdd/config.yaml", conteudo)
                rc, out = self.fluxo("estado", cwd=r)
                self.assertEqual(rc, esperado, out)
        self.assertIn('⚠️ sdd-open: flow.autonomous = "sim" em sdd/config.yaml não é true nem false — '
                      "encadeamento desligado.", out)
        self.assertIn("→ troque por true (liga) ou false (desliga)", out)


class Seguir(Base):
    def test_segue_com_tudo_pronto_e_a_linha_cabe_em_100(self):
        r = self.projeto()
        self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
        rc, out = self.fluxo("seguir", "define", "sdd/features/DEFINE_X.md", "design", cwd=r)
        self.assertEqual(rc, 0, out)
        linhas = out.splitlines()
        self.assertEqual(linhas[0], "✅ DEFINE pronto → seguindo para o DESIGN (encadeamento ligado em sdd/config.yaml)")
        self.assertLessEqual(len(linhas[0]), 100)
        self.assertEqual(linhas[1], "→ /sdd-design sdd/features/DEFINE_X.md")

    def test_concordancia_e_artigo_por_documento(self):
        r = self.projeto()
        self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
        self.escreve(r, "sdd/reviews/UX_REVIEW_X.md", "# UX\n\n| **Status** | Ready for Design |\n")
        casos = (("define", "governanca", "✅ DEFINE pronto → seguindo para a GOVERNANÇA"),
                 ("define", "ux-review", "✅ DEFINE pronto → seguindo para a UX REVIEW"),
                 ("governanca", "design", "✅ GOVERNANÇA pronta → seguindo para o DESIGN"),
                 ("ux-review", "design", "✅ UX REVIEW pronta → seguindo para o DESIGN"))
        for fase, prox, linha in casos:
            with self.subTest(fase=fase, prox=prox):
                rc, out = self.fluxo("seguir", fase, "sdd/features/DEFINE_X.md", prox, cwd=r)
                self.assertEqual(rc, 0, out)
                self.assertTrue(out.startswith(linha), out)

    def test_design_segue_com_a_revisao_registrada_ou_dispensavel(self):
        r = self.projeto()
        self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
        self.poe(r, "DESIGN_pronto.md", "DESIGN_X.md")
        rc, out = self.fluxo("seguir", "design", "sdd/features/DEFINE_X.md", "build", cwd=r)
        self.assertEqual(rc, 0, out)
        self.assertIn("✅ DESIGN pronto → seguindo para o BUILD", out)
        self.assertIn("→ /sdd-build sdd/features/DESIGN_X.md", out)
        dois = ler(FX / "DESIGN_ledger_vazio.md").replace(
            "| 3 | `tests/test_conta.py` | Create | Conta a amostra e confere `12 linhas` | (general) | 1, 2 |\n", "")
        self.assertNotIn("tests/test_conta.py` | Create", dois)
        self.escreve(r, "sdd/features/DESIGN_X.md", dois.replace("**Total Files:** 3", "**Total Files:** 2"))
        rc, out = self.fluxo("seguir", "design", "sdd/features/DEFINE_X.md", "build", cwd=r)
        self.assertEqual(rc, 0, out)

    def test_para_por_cada_motivo(self):
        r = self.projeto()
        self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
        self.poe(r, "DEFINE_rascunho.md", "DEFINE_R.md")
        self.poe(r, "DEFINE_sem_kind.md", "DEFINE_K.md")
        marcador = ler(FX / "DEFINE_pronto.md") + "\n## Clarifications\n\n- [NEEDS" + " CLARIFICATION: o mês fecha quando?]\n"
        self.escreve(r, "sdd/features/DEFINE_M.md", marcador)
        self.poe(r, "DEFINE_pronto.md", "DEFINE_V.md")
        self.poe(r, "DESIGN_ledger_vazio.md", "DESIGN_V.md")
        self.poe(r, "DEFINE_pronto.md", "DEFINE_H.md")
        aberto = ler(FX / "DESIGN_pronto.md").replace("| HIGH | APLICADA (Decision 1) |", "| HIGH | em análise |")
        self.escreve(r, "sdd/features/DESIGN_H.md", aberto)
        self.escreve(r, "sdd/reviews/UX_REVIEW_X.md", "# UX\n\n| **Status** | Needs Requirement Iteration |\n")
        casos = (
            (("define", "DEFINE_X", "design", "--parar"), "pedido de parar nesta chamada"),
            (("define", "DEFINE_R", "design"), "DEFINE não está pronto (Status: Draft)"),
            (("define", "DEFINE_K", "design"), "Verify Gate sem kind ou cmd"),
            (("define", "DEFINE_M", "design"), "o DEFINE tem marcador de clarificação aberto"),
            (("ux-review", "DEFINE_X", "design"), "UX REVIEW não está pronto (Status: Needs Requirement Iteration)"),
            (("design", "DEFINE_R", "build"), "DESIGN não encontrado"),
            (("design", "DEFINE_V", "build"), "revisão do DESIGN exigida e não registrada no Advisor Ledger"),
            (("design", "DEFINE_H", "build"), "HIGH aberto no Advisor Ledger: A1"),
            (("build", "DEFINE_X", "release"), "publicar não se desfaz — é decisão sua (D1)"),
            (("define", "DEFINE_X", "release"), "publicar não se desfaz — é decisão sua (D1)"),
        )
        for (fase, define, prox, *extra), motivo in casos:
            with self.subTest(fase=fase, define=define, prox=prox):
                rc, out = self.fluxo("seguir", fase, "sdd/features/%s.md" % define, prox, *extra, cwd=r)
                self.assertEqual(rc, 1, out)
                self.assertIn("PARAR: " + motivo, out)
                self.assertIn("RESULTADO: PARAR", out)
                self.assertIn("→ Próximo passo: /sdd-%s " % prox, out)

    def test_desligado_ou_sem_config_para_em_silencio_de_motivo(self):
        for autonomo in (False, None):
            with self.subTest(autonomo=autonomo):
                r = self.projeto(autonomo)
                self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
                rc, out = self.fluxo("seguir", "define", "sdd/features/DEFINE_X.md", "design", cwd=r)
                self.assertEqual(rc, 1, out)
                self.assertIn("PARAR: encadeamento desligado", out)
                shutil.rmtree(str(r))

    def test_uso_errado_e_slot_invalido_saem_64(self):
        r = self.projeto()
        self.poe(r, "DEFINE_pronto.md", "DEFINE_X.md")
        for args in (("build", "sdd/features/DEFINE_X.md", "design"), ("design", "sdd/features/DEFINE_X.md", "define"),
                     ("define", "sdd/features/NAO.md", "design"), ("define", "sdd/features/DEFINE_X.md")):
            with self.subTest(args=args):
                rc, out = self.fluxo("seguir", *args, cwd=r)
                self.assertEqual(rc, 64, out)
        self.escreve(r, "sdd/config.yaml", "flow:\n  autonomous: sim\n")
        rc, out = self.fluxo("seguir", "define", "sdd/features/DEFINE_X.md", "design", cwd=r)
        self.assertEqual(rc, 64, out)
        self.assertIn("→ troque por true (liga) ou false (desliga)", out)


class UsoESemPython(Base):
    def test_sem_verbo_ou_verbo_desconhecido_mostra_o_uso(self):
        for args in ((), ("pular",)):
            with self.subTest(args=args):
                rc, out = self.fluxo(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn("sdd-fluxo.sh review-design <DESIGN.md>", out)
                self.assertIn("RESULTADO: ERRO DE USO", out)

    def test_sem_python3_todo_verbo_sai_64(self):
        bin_ = self.tmp / "bin"
        bin_.mkdir()
        for f in FERRAMENTAS:
            achado = shutil.which(f)
            if achado:
                os.symlink(achado, str(bin_ / f))
        env = dict(self.env, PATH=str(bin_))
        for verbo in (("review-design", FX / "DESIGN_novos.md"), ("estado",), ("--self-test",),
                      ("despachar", "avaliador", "X", FX / "brief-avaliador.md")):
            with self.subTest(verbo=verbo[0]):
                rc, out = self.fluxo(*verbo, env=env)
                self.assertEqual(rc, 64, out)
                self.assertIn("python3 não encontrado", out)


class SelfTest(Base):
    def test_self_test_numa_copia_sem_git(self):
        copia = self.tmp / "pacote"
        copia.mkdir()
        self.copia("sdd", copia)
        rc, out, err = self.roda([BASH, copia / "sdd/bin/sdd-fluxo.sh", "--self-test"], copia)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: VERDE", out)
        for cenario in ("review-design DISPENSAVEL → exit 1", "loop AGUARDANDO_RECIBO → exit 30",
                        "despachar AGUARDANDO_HUMANO → exit 40", "seguir SEGUIR (define) → exit 0",
                        "| tee: log acusado pelo gate-shell-evidencia → exit 2"):
            self.assertIn(cenario, out)

    def test_self_test_fica_vermelho_com_fixture_trocada(self):
        copia = self.tmp / "pacote"
        copia.mkdir()
        self.copia("sdd", copia)
        shutil.copy(str(FX / "DESIGN_novos.md"), str(copia / "sdd/fixtures/fluxo/DESIGN_dispensavel.md"))
        rc, out, err = self.roda([BASH, copia / "sdd/bin/sdd-fluxo.sh", "--self-test"], copia)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("🛑 review-design DISPENSAVEL", out)


class Subsecao(Base):
    def test_bloco_comum_igual_nas_9_dentro_do_encerramento(self):
        blocos = {}
        for s in FASE:
            texto = ler(SKILLS / s / "SKILL.md")
            with self.subTest(skill=s):
                self.assertEqual(texto.count("\n### Fluxo encadeado\n"), 1)
                enc = texto.index("\n## Encerramento (obrigatório)\n")
                sub = texto.index("\n### Fluxo encadeado\n")
                rodape = texto.rindex("\n---\n\nParte do SDD Open by RDD")
                self.assertLess(enc, sub)
                self.assertLess(sub, rodape)
                self.assertNotIn("\n## ", texto[enc + 5:rodape])
                if "**Próximo passo:**" in texto[enc:]:
                    self.assertLess(texto.index("**Próximo passo:**", enc), sub)
                bloco = texto[sub:texto.index("\nNesta skill: ", sub)]
                blocos[s] = bloco
                linha = texto[texto.index("\nNesta skill: ", sub):rodape]
                if s in ENCADEIAM or s == "sdd-build":
                    self.assertIn("`seguir ", linha)
                else:
                    self.assertIn("não encadeia", linha)
        self.assertEqual(len(set(blocos.values())), 1, "o bloco comum diverge entre as skills")
        bloco = next(iter(blocos.values()))
        for trecho in ("sdd/templates/fragments/FLUXO_ENCADEADO.md", "bash sdd/bin/sdd-fluxo.sh seguir",
                       "encadeamento desligado", "**Decidi sozinho**", "[auto · de rotina]", "--parar"):
            self.assertIn(trecho, bloco)

    def test_build_nunca_segue_para_a_release(self):
        texto = ler(SKILLS / "sdd-build/SKILL.md")
        self.assertIn("`seguir build sdd/features/DEFINE_{FEATURE}.md release` sempre para", texto)


class TextoDoPorte(Base):
    def test_f6_design_decide_sozinho_so_com_o_encadeamento_ligado(self):
        texto = ler(SKILLS / "sdd-design/SKILL.md")
        for trecho in ("bash sdd/bin/sdd-fluxo.sh estado", "o lado conservador", "[auto] <decisão> — porque",
                       "Ausente ou em branco → ambíguo: pergunte antes de"):
            self.assertIn(trecho, texto)

    def test_f8_define_pontua_forte_e_fraco(self):
        texto = ler(SKILLS / "sdd-define/SKILL.md")
        for trecho in ("1 forte → `true`", "2 fracos → `true`", "1 fraco → `true` com a nota \"conservador\"",
                       "candidato a loop"):
            self.assertIn(trecho, texto)

    def test_f10_brainstorm_trata_cada_tipo_de_entrada(self):
        texto = ler(SKILLS / "sdd-brainstorm/SKILL.md")
        for trecho in ("Como tratar cada tipo de entrada", "\"conte mais\"", "questione a necessidade",
                       "o que se ganha e o que se perde"):
            self.assertIn(trecho, texto)

    def test_f11_ux_review_le_as_revisoes_anteriores(self):
        self.assertIn("os `sdd/reviews/UX_REVIEW_*.md` anteriores", ler(SKILLS / "sdd-ux-review/SKILL.md"))

    def test_despacho_sem_papel_fresco_para_no_exit_40(self):
        for p in (SKILLS / "sdd-build/SKILL.md", SKILLS / "sdd-build/references/contexto-fresco.md",
                  SKILLS / "sdd-design/SKILL.md"):
            with self.subTest(arquivo=p.name):
                texto = ler(p)
                self.assertRegex(texto, r"bash sdd/bin/sdd-fluxo\.sh despachar (avaliador|revisor-design)")
                self.assertIn("exit 40", texto)
        self.assertIn("review-design sdd/features/DESIGN_{FEATURE}.md", ler(SKILLS / "sdd-design/SKILL.md"))


class Fragmentos(Base):
    def test_pergunta_decisao_tem_as_6_marcas_e_o_estado(self):
        texto = ler(RAIZ / "sdd/templates/fragments/PERGUNTA_DECISAO.md")
        for marca in ("[D1 · não se desfaz]", "[D2 · muda o produto]", "[D3 · muda a regra do método]",
                      "[D4 · limite de tentativas]", "[D5 · provas em conflito]", "[auto · de rotina]"):
            self.assertIn("| `%s` |" % marca, texto)
        for trecho in ("[Dn]", "bash sdd/bin/sdd-fluxo.sh estado", "Posso finalizar", "**Por que parei:**"):
            self.assertIn(trecho, texto)

    def test_fluxo_encadeado_tem_o_contrato(self):
        texto = ler(RAIZ / "sdd/templates/fragments/FLUXO_ENCADEADO.md")
        for trecho in ("flow.autonomous", "seguir <fase> <DEFINE> <próxima>", "review-design <DESIGN>",
                       "✅ DEFINE pronto → seguindo para o DESIGN", "**Decidi sozinho:**", " — porque ",
                       "para desfazer:", "AGUARDANDO_HUMANO", "AGUARDANDO_RECIBO", "3 rodadas", "2 ciclos",
                       "[D4 · limite de tentativas]", "--parar", "nunca com `| tee`"):
            self.assertIn(trecho, texto)


class Slots(Base):
    def test_config_example_tem_os_dois_slots_com_default(self):
        texto = ler(RAIZ / "sdd/config.example.yaml")
        self.assertRegex(texto, r"(?m)^flow:\n(?:\s+#.*\n)*\s+autonomous: false$")
        self.assertRegex(texto, r"(?m)^review:\n(?:\s+.*\n)*?\s+security_globs: \"\"$")
