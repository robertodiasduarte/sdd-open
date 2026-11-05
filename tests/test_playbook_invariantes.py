"""Contrato das invariantes: sdd/invariants.md e os modos --validar-inv, --cruzar, --aplicar-inv e --colher --inv
do sdd/bin/playbook-curator.sh (DEFINE F14 AT-014 a AT-019)."""
from __future__ import annotations

from apoio import BASH, RAIZ, Sandbox

CURATOR = RAIZ / "sdd/bin/playbook-curator.sh"
FX = RAIZ / "sdd/fixtures/playbook/curadoria"
PB, INV = FX / "playbook-inv.md", FX / "invariants-inv.md"

CABECA = "# I\n\n## Invariantes\n\n"
PLAYBOOK = """# P

## Sempre

- [LM-001] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: sdd/bin/report-lint.py
- [LM-002] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `b` :: r. **Do instead:** x. · promovido_para: —
- [LM-003] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `c` :: r. **Do instead:** x. · promovido_para: —

## Tombstones

- [LM-009] ☠ 2026-01-01 :: fora
"""
BASE = ("- [INV-001] estado=ok origem=LM-001 :: Regra · por quê: p\n"
        "- [INV-002] estado=humano origem=LM-002 :: Regra · por quê: p · motivo: m\n")


class Base_(Sandbox):
    def setUp(self):
        super().setUp()
        self.env = dict(self.env, SDD_TRACE="off")
        self.pb = self.escreve(self.tmp, "p.md", PLAYBOOK)
        self.link()

    def link(self):
        # os check= partem da pasta de quem chama
        self.escreve(self.tmp, "sdd/bin/report-lint.py", "x\n")

    def cur(self, *args, entrada=None):
        return self.roda([BASH, CURATOR, *args], self.tmp)

    def trava(self, corpo, pb=None):
        i = self.escreve(self.tmp, "i.md", CABECA + corpo)
        return self.cur("--validar-inv", pb or self.pb, i)


class Pacote(Sandbox):
    """AT-014"""

    def test_o_par_do_pacote_passa(self):
        rc, out, err = self.roda([BASH, CURATOR, "--validar-inv", "sdd/playbook.md", "sdd/invariants.md"], RAIZ,
                                 dict(self.env, SDD_TRACE="off"))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: PAR VÁLIDO", out)

    def test_o_arquivo_traz_a_gramatica_e_as_2_secoes(self):
        texto = (RAIZ / "sdd/invariants.md").read_text(encoding="utf-8")
        for trecho in ("estado=ok|auto|humano", "origem=seed|LM-nnn", "## Invariantes", "## Descartados", "[INV-001]"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, texto)


class Trava(Base_):
    """AT-015"""

    def test_controle_passa(self):
        rc, out, err = self.trava(BASE)
        self.assertEqual(rc, 0, out + err)

    def test_cada_defeito_sai_2_nomeando_o_id(self):
        casos = {
            "origem aposentada": (BASE + "- [INV-003] estado=humano origem=LM-009 :: R · por quê: p · motivo: m\n", "INV-003 tem origem=LM-009, que está aposentada"),
            "origem inexistente": (BASE + "- [INV-003] estado=humano origem=LM-777 :: R · por quê: p · motivo: m\n", "INV-003 tem origem=LM-777, que não existe"),
            "universo sem classificação": ("- [INV-001] estado=ok origem=LM-001 :: R · por quê: p\n", "LM-002 entra no universo sem classificação"),
            "ID repetido": (BASE + "- [INV-001] estado=humano origem=seed :: R · por quê: p · motivo: m\n", "INV-001 aparece 2 vezes"),
            "linha fora da gramática": (BASE + "- solta\n", "fora da gramática"),
            "linha colchete sem gramática antes da 1ª": ("- [INV-003] estado=talvez origem=seed :: R · por quê: p\n" + BASE, "fora da gramática"),
            "auto sem tarefa": (BASE + "- [INV-003] estado=auto origem=seed :: R · por quê: p\n", "INV-003 é estado=auto sem"),
            "humano sem motivo": (BASE + "- [INV-003] estado=humano origem=seed :: R · por quê: p\n", "INV-003 é estado=humano sem"),
            "ok sem check nem promovida": (BASE + "- [INV-003] estado=ok origem=seed :: R · por quê: p\n", "INV-003 é estado=ok sem check="),
            "check que não existe": (BASE + "- [INV-003] estado=ok origem=seed check=sdd/nao/existe.sh :: R · por quê: p\n", "check=sdd/nao/existe.sh, que não existe"),
            "descarte repetido": (BASE + "\n## Descartados\n\n- [LM-003] descartado :: a\n- [LM-003] descartado :: b\n", "LM-003 aparece 2 vezes"),
            "descarte aposentado": (BASE + "\n## Descartados\n\n- [LM-009] descartado :: a\n", "LM-009 está em ## Descartados e foi aposentada"),
            "descarte que é origem": (BASE + "\n## Descartados\n\n- [LM-002] descartado :: a\n", "LM-002 é origem de uma invariante"),
            "descarte inexistente": (BASE + "\n## Descartados\n\n- [LM-777] descartado :: a\n", "LM-777 está em ## Descartados e não existe"),
        }
        for nome, (corpo, trecho) in casos.items():
            with self.subTest(caso=nome):
                rc, out, err = self.trava(corpo)
                self.assertEqual(rc, 2, out + err)
                self.assertIn("🔴 trava INV:", err)
                self.assertIn(trecho, err)
                self.assertIn("RESULTADO: TRAVA", out)

    def test_campo_vazio_e_check_que_nao_e_arquivo(self):
        casos = {"tarefa vazia": ("- [INV-003] estado=auto origem=seed :: R · por quê: p · tarefa: \n", "sem '· tarefa:'"),
                 "motivo vazio": ("- [INV-003] estado=humano origem=seed :: R · por quê: p · motivo:  \n", "sem '· motivo:'"),
                 "check pasta atual": ("- [INV-003] estado=ok origem=seed check=. :: R · por quê: p\n", "relativo à raiz"),
                 "check absoluto": ("- [INV-003] estado=ok origem=seed check=/etc/hosts :: R · por quê: p\n", "relativo à raiz")}
        for nome, (linha, trecho) in casos.items():
            with self.subTest(caso=nome):
                rc, _, err = self.trava(BASE + linha)
                self.assertEqual(rc, 2, err)
                self.assertIn(trecho, err)

    def test_check_em_pasta_com_ponto_e_legitimo(self):
        # N3-M1 do avaliador, ciclo 3: o conserto do N-L6 recusava .github/ e .agents/.
        self.escreve(self.tmp, ".github/workflows/x.yml", "x\n")
        rc, out, err = self.trava(BASE + "- [INV-003] estado=ok origem=seed check=.github/workflows/x.yml :: R · por quê: p\n")
        self.assertEqual(rc, 0, out + err)
        pb = self.escreve(self.tmp, "p5.md", PLAYBOOK.replace("promovido_para: sdd/bin/report-lint.py", "promovido_para: .github/workflows/x.yml"))
        rc, out, err = self.trava(BASE, pb=pb)
        self.assertEqual(rc, 0, out + err)

    def test_check_e_promovido_que_saem_da_raiz(self):
        self.escreve(self.tmp.parent, "fora-%s.txt" % self.tmp.name, "x\n")
        fora = "../fora-%s.txt" % self.tmp.name
        self.addCleanup(lambda: (self.tmp.parent / ("fora-%s.txt" % self.tmp.name)).unlink())
        rc, _, err = self.trava(BASE + "- [INV-003] estado=ok origem=seed check=%s :: R · por quê: p\n" % fora)
        self.assertEqual(rc, 2, err)
        self.assertIn("relativo à raiz", err)
        pb = self.escreve(self.tmp, "p6.md", PLAYBOOK.replace("promovido_para: sdd/bin/report-lint.py", "promovido_para: " + fora))
        rc, _, err = self.trava(BASE, pb=pb)
        self.assertEqual(rc, 2, err)
        self.assertIn("INV-001 é estado=ok sem check=", err)

    def test_check_e_promovido_que_nao_sao_arquivo_do_projeto(self):
        # N-L6 do avaliador, ciclo 2
        for caminho in (".", "/", "..", "/etc/hosts", "sdd"):
            with self.subTest(promovido=caminho):
                pb = self.escreve(self.tmp, "p4.md", PLAYBOOK.replace("promovido_para: sdd/bin/report-lint.py", "promovido_para: " + caminho))
                rc, _, err = self.trava(BASE, pb=pb)
                self.assertEqual(rc, 2, err)
                self.assertIn("INV-001 é estado=ok sem check=", err)
            with self.subTest(check=caminho):
                rc, _, err = self.trava(BASE + "- [INV-003] estado=ok origem=seed check=%s :: R · por quê: p\n" % caminho)
                self.assertEqual(rc, 2, err)
                self.assertIn("relativo à raiz", err)
        rc, _, err = self.trava(BASE + "- [INV-003] estado=auto origem=seed :: R · por quê: p · tarefa: · motivo: m\n")
        self.assertEqual(rc, 2, err)
        self.assertIn("sem '· tarefa:'", err)

    def test_ok_com_origem_promovida_para_arquivo_que_saiu_reprova(self):
        pb = self.escreve(self.tmp, "p2.md", PLAYBOOK.replace("promovido_para: sdd/bin/report-lint.py", "promovido_para: sdd/bin/saiu.py"))
        rc, _, err = self.trava(BASE, pb=pb)
        self.assertEqual(rc, 2, err)
        self.assertIn("INV-001 é estado=ok sem check= e sem origem promovida para um arquivo que existe", err)

    def test_promovido_na_continuacao_entra_no_universo(self):
        texto = PLAYBOOK.replace("`c` :: r. **Do instead:** x. · promovido_para: —\n", "`c` :: r\n  longa. **Do instead:** x. · promovido_para: `sdd/bin/report-lint.py`\n")
        rc, _, err = self.trava(BASE, pb=self.escreve(self.tmp, "p3.md", texto))
        self.assertEqual(rc, 2, err)
        self.assertIn("LM-003 entra no universo", err)

    def test_ok_com_origem_promovida_nao_precisa_de_check(self):
        rc, out, err = self.trava("- [INV-001] estado=ok origem=LM-001 :: R · por quê: p\n- [INV-002] estado=humano origem=LM-002 :: R · por quê: p · motivo: m\n")
        self.assertEqual(rc, 0, out + err)

    def test_check_que_existe_passa(self):
        rc, out, err = self.trava(BASE + "- [INV-003] estado=ok origem=seed check=sdd/bin/report-lint.py :: R · por quê: p\n")
        self.assertEqual(rc, 0, out + err)

    def test_descartado_tira_do_universo(self):
        corpo = "- [INV-001] estado=ok origem=LM-001 :: R · por quê: p\n\n## Descartados\n\n- [LM-002] descartado :: ferramenta\n"
        rc, out, err = self.trava(corpo)
        self.assertEqual(rc, 0, out + err)

    def test_licao_que_nunca_mordeu_fica_fora_do_universo(self):
        self.assertNotIn("LM-003", self.trava(BASE)[2])

    def test_so_pendentes_traz_a_frase_do_registro_novo(self):
        rc, _, err = self.trava("")
        self.assertEqual(rc, 2)
        self.assertIn("o registro de invariantes é novo na v2.6.0: 2 lição(ões)", err.split("\n")[0])

    def test_com_outro_defeito_nao_finge_que_e_so_o_registro_novo(self):
        _, _, err = self.trava("- [INV-003] estado=auto origem=seed :: R · por quê: p\n")
        self.assertNotIn("novo na v2.6.0", err)

    def test_arquivo_ausente_e_sem_secao(self):
        rc, out, err = self.cur("--validar-inv", self.pb, self.tmp / "nao.md")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("arquivo ausente", err)
        i = self.escreve(self.tmp, "sem.md", "# nada\n")
        rc, _, err = self.cur("--validar-inv", self.pb, i)
        self.assertEqual(rc, 2)
        self.assertIn("não tem a seção", err)


class Cruzar(Sandbox):
    """AT-016, AT-017, AT-018, AT-019, sobre as fixtures do pacote"""

    def setUp(self):
        super().setUp()
        self.env = dict(self.env, SDD_TRACE="off")

    def cruza(self, delta, pb=PB, inv=INV):
        d = self.escreve(self.tmp, "d.txt", delta)
        return self.roda([BASH, CURATOR, "--cruzar", d, pb, inv], RAIZ)

    def test_origem_unica_promovida_vira_seed_com_o_check_do_bullet(self):
        rc, out, _ = self.cruza("TOMBSTONE LM-030 :: t\n")
        self.assertEqual(rc, 3, out)
        self.assertIn("INV_AFETADA INV-001 origem=LM-030 · delta: TOMBSTONE LM-030", out)
        self.assertIn("   ajuste: - [INV-001] estado=ok origem=seed check=sdd/bin/playbook-curator.sh :: Regra um", out)
        self.assertIn("   ou: retirar o TOMBSTONE LM-030", out)
        self.assertRegex(out, r"(?m)^resumo-inv: afetadas=1 pendentes=0$")

    def test_uma_de_duas_origens_e_as_duas_juntas(self):
        _, out, _ = self.cruza("TOMBSTONE LM-031 :: t\n")
        self.assertIn("   ajuste: - [INV-002] estado=humano origem=LM-032 :: Regra dois", out)
        _, out, _ = self.cruza("TOMBSTONE LM-031 :: t\nTOMBSTONE LM-032 :: t\n")
        self.assertEqual(out.count("ajuste:"), 1)
        self.assertIn("   ajuste: - [INV-002] estado=humano origem=seed :: Regra dois", out)

    def test_origem_unica_com_check_curado_mantem_o_check(self):
        _, out, _ = self.cruza("TOMBSTONE LM-033 :: t\n")
        self.assertIn("   ajuste: - [INV-003] estado=ok origem=seed check=sdd/bin/playbook-lint.sh ::", out)

    def test_licao_descartada_aposentada(self):
        rc, out, _ = self.cruza("TOMBSTONE LM-035 :: t\n")
        self.assertEqual(rc, 3)
        self.assertIn("INV_AFETADA descarte LM-035", out)
        self.assertIn("   ajuste: REMOVER LM-035", out)

    def test_licao_nova_no_universo_propoe_a_e_b_em_sequencia(self):
        rc, out, _ = self.cruza("LM-036 mordeu+1\nLM-037 promovido_para=sdd/bin/x.sh\n")
        self.assertEqual(rc, 3)
        self.assertIn("INV_PENDENTE LM-036 (mordeu 0→1)", out)
        self.assertIn("INV_PENDENTE LM-037 (promovido)", out)
        self.assertIn("proposta A: - [INV-006] estado=<ok|auto|humano> origem=LM-036", out)
        self.assertIn("proposta A: - [INV-007] estado=<ok|auto|humano> origem=LM-037", out)
        self.assertIn("proposta B: - [LM-036] descartado :: <motivo>", out)

    def test_promovido_para_que_nao_e_arquivo_nao_vira_check(self):
        # M3: texto livre não vigia nada; o ajuste não pode propor check=Verify nem trocar um check bom.
        pb = self.escreve(self.tmp, "p.md", "# P\n\n## Sempre\n\n- [LM-040] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: Verify Gate\n\n## Tombstones\n")
        inv = self.escreve(self.tmp, "i.md", CABECA + "- [INV-001] estado=ok origem=LM-040 check=sdd/bin/playbook-lint.sh :: R · por quê: p\n")
        rc, out, _ = self.cruza("TOMBSTONE LM-040 :: t\n", pb, inv)
        self.assertEqual(rc, 3)
        self.assertIn("origem=seed check=sdd/bin/playbook-lint.sh ::", out)
        self.assertNotIn("check=Verify", out)

    def test_check_curado_e_trocado_pelo_do_bullet_promovido(self):
        # Mutante vivo nos ciclos 2 e 3: a troca do check= virava no-op sem nenhum teste notar.
        pb = self.escreve(self.tmp, "p.md", "# P\n\n## Sempre\n\n- [LM-040] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: sdd/bin/report-lint.py\n\n## Tombstones\n")
        inv = self.escreve(self.tmp, "i.md", CABECA + "- [INV-001] estado=ok origem=LM-040 check=sdd/bin/playbook-lint.sh :: R · por quê: p\n")
        rc, out, _ = self.cruza("TOMBSTONE LM-040 :: t\n", pb, inv)
        self.assertEqual(rc, 3)
        self.assertIn("origem=seed check=sdd/bin/report-lint.py ::", out)
        self.assertNotIn("check=sdd/bin/playbook-lint.sh", out.split("ajuste:")[1])

    def test_licao_ja_no_universo_nao_e_entrada_nova(self):
        rc, out, _ = self.cruza("LM-030 mordeu+1\n")
        self.assertEqual(rc, 0, out)
        self.assertNotIn("INV_PENDENTE", out)

    def test_sem_aviso_sai_0(self):
        rc, out, _ = self.cruza("LM-031 mordeu+1\nLM-030 ajudou+1\n")
        self.assertEqual(rc, 0, out)
        self.assertRegex(out, r"(?m)^resumo-inv: afetadas=0 pendentes=0$")
        self.assertNotIn("INV_", out)

    def test_le_o_delta_do_stdin(self):
        r = __import__("subprocess").run([BASH, str(CURATOR), "--cruzar", "-", str(PB), str(INV)], cwd=str(RAIZ), env=self.env,
                                         input="TOMBSTONE LM-030 :: t\n", capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("INV_AFETADA INV-001", r.stdout)

    def test_invalido_sai_2_com_stdout_vazio(self):
        rc, out, _ = self.cruza("LM-030 ajudou++\n")
        self.assertEqual((rc, out), (2, ""))
        sem = self.escreve(self.tmp, "sem.md", "# nada\n")
        rc, out, err = self.cruza("LM-030 ajudou+1\n", inv=sem)
        self.assertEqual((rc, out), (2, ""))
        self.assertIn("sem a seção", err)

    def test_seed_invalido_diz_que_nao_ha_saida_em_vez_de_propor(self):
        pb = self.escreve(self.tmp, "p.md", "# P\n\n## Sempre\n\n- [LM-040] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: —\n\n## Tombstones\n")
        inv = self.escreve(self.tmp, "i.md", CABECA + "- [INV-001] estado=ok origem=LM-040 :: R · por quê: p\n")
        rc, out, _ = self.cruza("TOMBSTONE LM-040 :: t\n", pb, inv)
        self.assertEqual(rc, 3)
        self.assertIn("não é saída válida", out)
        self.assertNotIn("ajuste:", out)

    def test_ajuste_proposto_destrava_e_sem_ele_trava(self):
        d = self.escreve(self.tmp, "d.txt", "TOMBSTONE LM-030 :: t\n")
        _, novo, _ = self.roda([BASH, CURATOR, "--aplicar", d, PB, "2026-09-24"], RAIZ)
        novo_pb = self.escreve(self.tmp, "novo.md", novo)
        rc, _, err = self.roda([BASH, CURATOR, "--validar-inv", novo_pb, INV], RAIZ)
        self.assertEqual(rc, 2)
        self.assertIn("INV-001 tem origem=LM-030", err)
        self.assertIn("retire o TOMBSTONE LM-030", err)
        _, cruzou, _ = self.roda([BASH, CURATOR, "--cruzar", d, PB, INV], RAIZ)
        ajuste = next(l[len("   ajuste: "):] for l in cruzou.split("\n") if l.startswith("   ajuste: "))
        linhas = self.escreve(self.tmp, "l.txt", ajuste + "\n")
        rc, novas, err = self.roda([BASH, CURATOR, "--aplicar-inv", linhas, INV], RAIZ)
        self.assertEqual(rc, 0, err)
        novo_inv = self.escreve(self.tmp, "ni.md", novas)
        rc, out, err = self.roda([BASH, CURATOR, "--validar-inv", novo_pb, novo_inv], RAIZ)
        self.assertEqual(rc, 0, out + err)

    def test_licao_antiga_sem_classificacao_entra_na_colheita(self):
        # M7: sem isto, a trava para no item 6 e ninguém pergunta.
        pb = self.escreve(self.tmp, "p.md", "# P\n\n## Sempre\n\n- [LM-040] ajudou=0 mordeu=1 · conf=2026-01-01 · sup: `a` :: r. **Do instead:** x. · promovido_para: —\n- [LM-041] ajudou=0 mordeu=0 · conf=2026-01-01 · sup: `b` :: r. **Do instead:** x. · promovido_para: —\n\n## Tombstones\n")
        inv = self.escreve(self.tmp, "i.md", CABECA + "- [INV-005] estado=auto origem=seed :: R · por quê: p · tarefa: t\n")
        vazia = self.tmp / "vazia"
        vazia.mkdir()
        rc, out, _ = self.roda([BASH, CURATOR, "--colher", vazia, pb, "--inv", inv], self.tmp)
        self.assertEqual(rc, 0, out)
        self.assertIn("INV_PENDENTE LM-040 (já no universo, sem classificação)", out)
        self.assertIn("proposta A: - [INV-006]", out)
        self.assertNotIn("LM-041", out)
        rc, out, _ = self.roda([BASH, CURATOR, "--colher", vazia, pb], self.tmp)
        self.assertNotIn("INV_PENDENTE", out)

    def test_colher_com_inv_anexa_a_pendencia_sem_mudar_o_exit(self):
        rp = FX / "replay"
        args = [BASH, CURATOR, "--colher", rp, rp / "playbook-replay.md"]
        rc1, sem, _ = self.roda(args, self.tmp)
        rc2, com, _ = self.roda(args + ["--inv", INV], self.tmp)
        self.assertEqual(rc1, rc2)
        self.assertNotIn("INV_PENDENTE", sem)
        self.assertIn("INV_PENDENTE LM-005 (mordeu 0→1)", com)


class AplicarInv(Base_):
    """D6 da revisão do DESIGN: quem grava as invariantes é um modo, não a mão do agente."""

    def aplica(self, linhas, corpo=BASE):
        i = self.escreve(self.tmp, "i.md", CABECA + corpo + "\n## Descartados\n")
        return self.cur("--aplicar-inv", self.escreve(self.tmp, "l.txt", linhas), i)

    def test_troca_acrescenta_descarta_e_remove(self):
        rc, out, err = self.aplica("- [INV-002] estado=humano origem=seed :: Regra · por quê: p · motivo: nova\n"
                                   "- [INV-003] estado=auto origem=seed :: Outra · por quê: p · tarefa: t\n"
                                   "- [LM-003] descartado :: ferramenta\nREMOVER INV-001\n")
        self.assertEqual(rc, 0, err)
        self.assertNotIn("INV-001", out)
        self.assertEqual(out.count("[INV-002]"), 1)
        self.assertIn("origem=seed :: Regra · por quê: p · motivo: nova", out)
        self.assertLess(out.index("[INV-003]"), out.index("## Descartados"))
        self.assertGreater(out.index("[LM-003] descartado"), out.index("## Descartados"))
        self.assertNotIn("RESULTADO:", out)
        self.assertIn("RESULTADO: INVARIANTES APLICADAS", err)

    def test_fora_da_gramatica_sai_2_com_stdout_vazio(self):
        for linha, trecho in (("qualquer coisa\n", "fora da gramática"), ("REMOVER INV-999\n", "nada a remover")):
            with self.subTest(linha=linha):
                rc, out, err = self.aplica(linha)
                self.assertEqual((rc, out), (2, ""))
                self.assertIn(trecho, err)

    def test_id_igual_com_outra_regra_nao_pisa_a_da_base(self):
        # M6: no pouso com conflito, uma invariante nova com o mesmo ID apagaria a da outra frente.
        rc, out, err = self.aplica("- [INV-002] estado=humano origem=seed :: Regra de outra frente · por quê: p · motivo: m\n")
        self.assertEqual((rc, out), (2, ""))
        self.assertIn("renumere a nova", err)

    def test_2_novas_com_o_mesmo_id_nao_somem_em_silencio(self):
        # N-L8
        for a, b in (("Uma", "Outra"), ("Uma", "Uma")):
            with self.subTest(a=a, b=b):
                rc, out, err = self.aplica("- [INV-009] estado=auto origem=seed :: %s · por quê: p · tarefa: t\n- [INV-009] estado=auto origem=seed :: %s · por quê: p · tarefa: t\n" % (a, b))
                self.assertEqual((rc, out), (2, ""))
                self.assertIn("aparece 2 vezes", err)

    def test_mesma_regra_com_origem_ajustada_troca(self):
        rc, out, err = self.aplica("- [INV-002] estado=humano origem=seed :: Regra · por quê: p · motivo: m\n")
        self.assertEqual(rc, 0, err)
        self.assertIn("[INV-002] estado=humano origem=seed", out)
        self.assertEqual(out.count("[INV-002]"), 1)

    def test_sem_a_secao_de_descartados_ela_nasce(self):
        i = self.escreve(self.tmp, "i.md", CABECA + BASE)
        rc, out, _ = self.cur("--aplicar-inv", self.escreve(self.tmp, "l.txt", "- [LM-003] descartado :: x\n"), i)
        self.assertEqual(rc, 0)
        self.assertIn("## Descartados", out)
        self.assertIn("- [LM-003] descartado :: x", out)
