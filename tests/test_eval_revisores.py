"""sdd/bin/eval-revisores.sh — custo e resultado por papel, engine e modelo (F19: AT-001 a AT-005).

As 6 pastas de sdd/fixtures/revisao/custo/ são dados inventados que reproduzem casos reais: revisor por
assinatura com custo de tabela; o mesmo modelo de auditor por 2 provedores com custo diferente; um achado
NOVO do auditor repetido e rebatido em 2 rodadas; 2º revisor cobrado sem responder (exit 67); 2º revisor sem
credencial (exit 65); custo estimado (≈), custo `$?` e `assinatura` sem valor; achado sem linha no ledger;
linha do ledger que aponta achado inexistente; META vazio. Cada célula da tabela é afirmada.

O script só lê: não chama engine, não usa rede, não escreve arquivo.
"""
from __future__ import annotations

import hashlib
import re
import shutil

from apoio import BASH, RAIZ, Sandbox

ER = RAIZ / "sdd/bin/eval-revisores.sh"
FX = RAIZ / "sdd/fixtures/revisao/custo"
COLUNAS = ("Papel", "Engine (modelo)", "Cobrança", "Rodadas", "Falhas", "Pago US$", "Nominal US$", "Achados",
           "Aplicados", "Com dano", "Falsos positivos", "Fora de escopo", "Sem classificar", "Pago por dano",
           "Nominal por dano", "AGREE")
ESPERADO = [
    ("revisor", "claude (claude-x)", "assinatura", "6", "0", "0.0000", "≈7.0000", "9", "6 de 9", "3 de 9", "1 de 9",
     "1 de 9", "1 de 9", "0.0000", "≈2.3333", "—"),
    ("2º revisor", "codex (-)", "assinatura", "1", "0", "0.0000", "n/d", "1", "1 de 1", "1 de 1", "0 de 1", "0 de 1",
     "0 de 1", "0.0000", "—", "—"),
    ("2º revisor", "gemini (-)", "desconhecida", "0", "1 (1 credencial)", "n/d", "n/d", "0", "0", "0", "0", "0", "0",
     "—", "—", "—"),
    ("2º revisor", "openrouter (deep/seek)", "pay-per-token", "0", "1 (1 cota ou tempo)",
     "1.0000 (incerto em 1 de 1)", "1.0000 (incerto em 1 de 1)", "0", "0", "0", "0", "0", "0", "—", "—", "—"),
    ("auditor", "codex (-)", "assinatura", "0", "1 (1 trocada por outra engine)", "0.0000", "n/d", "0", "0", "0", "0",
     "0", "0", "—", "—", "n/a"),
    ("auditor", "openrouter (qwen/q-plus via ProvedorA)", "pay-per-token", "4", "0", "0.1500 (n/d em 1 de 4)",
     "0.1500 (n/d em 1 de 4)", "0", "0", "0", "0", "0", "0", "—", "—", "71.4% (5 de 7)"),
    ("auditor", "openrouter (qwen/q-plus via ProvedorB)", "pay-per-token", "2", "0", "0.6100", "0.6100", "2",
     "0 de 2", "0 de 2", "2 de 2", "0 de 2", "0 de 2", "—", "—", "100.0% (3 de 3)"),
]


def linhas(saida: str) -> list:
    """As linhas de dados da tabela, cada uma como tupla de células."""
    tabela = [ln for ln in saida.splitlines() if ln.startswith("|")]
    return [tuple(c.strip() for c in ln.strip("|").split("|")) for ln in tabela[2:]]


class Base(Sandbox):
    def er(self, *args, cwd=None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, ER, *args], cwd or self.tmp)
        return rc, out + err

    def fixtures(self) -> tuple[int, str]:
        return self.er(FX, "--ledgers", FX, "--registry", FX / "registry.tsv")


class Tabela(Base):
    """AT-001 a AT-004 sobre as fixtures."""

    def setUp(self):
        super().setUp()
        self.rc, self.out = self.fixtures()

    def test_sai_0_medido_com_a_seta(self):
        self.assertEqual(self.rc, 0, self.out)
        self.assertIn("RESULTADO: MEDIDO\n→ ", self.out)
        self.assertIn("6 pasta(s) lida(s)", self.out)
        self.assertIn("1 ledger(s)", self.out)

    def test_cabecalho_tem_as_16_colunas_na_ordem(self):
        cab = next(ln for ln in self.out.splitlines() if ln.startswith("| Papel"))
        self.assertEqual(tuple(c.strip() for c in cab.strip("|").split("|")), COLUNAS)

    def test_cada_celula_da_tabela(self):
        obtido = linhas(self.out)
        self.assertEqual(len(obtido), len(ESPERADO), self.out)
        for esperada, real in zip(ESPERADO, obtido):
            for coluna, a, b in zip(COLUNAS, esperada, real):
                with self.subTest(linha=esperada[0] + " " + esperada[1], coluna=coluna):
                    self.assertEqual(b, a)

    def test_o_mesmo_modelo_por_dois_provedores_fica_em_duas_linhas(self):
        auditores = [ln for ln in linhas(self.out) if ln[0] == "auditor" and ln[1].startswith("openrouter")]
        self.assertEqual([a[1] for a in auditores],
                         ["openrouter (qwen/q-plus via ProvedorA)", "openrouter (qwen/q-plus via ProvedorB)"])
        self.assertNotEqual(auditores[0][5].split()[0], auditores[1][5])

    def test_soma_decimal_exata(self):
        # 0.3100 + 0.3000: em ponto flutuante a soma não fecha em 0.61; a saída tem de ser exata.
        self.assertIn("| 0.6100 | 0.6100 |", self.out)

    def test_sem_custo_informado_nunca_vira_zero(self):
        provedor_a = next(ln for ln in linhas(self.out) if ln[1].endswith("via ProvedorA)"))
        self.assertEqual(provedor_a[5], "0.1500 (n/d em 1 de 4)")
        codex = next(ln for ln in linhas(self.out) if ln[1] == "codex (-)")
        self.assertEqual(codex[6], "n/d")           # assinatura sem valor: nominal desconhecido, não 0.0000
        gemini = next(ln for ln in linhas(self.out) if ln[1] == "gemini (-)")
        self.assertEqual((gemini[5], gemini[6]), ("n/d", "n/d"))

    def test_chamada_que_falhou_conta_em_falhas_e_o_custo_dela_entra(self):
        deep = next(ln for ln in linhas(self.out) if ln[1] == "openrouter (deep/seek)")
        self.assertEqual((deep[3], deep[4], deep[7]), ("0", "1 (1 cota ou tempo)", "0"))
        # `US$ 1.0000 + $?`: o 1.0000 entra na soma e a linha avisa que o resto é incerto
        self.assertEqual((deep[5], deep[6]), ("1.0000 (incerto em 1 de 1)", "1.0000 (incerto em 1 de 1)"))

    def test_engine_prevista_que_falhou_e_foi_trocada_ganha_a_falha(self):
        codex = next(ln for ln in linhas(self.out) if ln[:2] == ("auditor", "codex (-)"))
        self.assertEqual((codex[3], codex[4]), ("0", "1 (1 trocada por outra engine)"))

    def test_estimado_leva_o_sinal_tambem_no_custo_por_dano(self):
        revisor = linhas(self.out)[0]
        self.assertEqual((revisor[6], revisor[14]), ("≈7.0000", "≈2.3333"))

    def test_novo_do_auditor_rebatido_duas_vezes_e_falso_positivo_dele(self):
        b = next(ln for ln in linhas(self.out) if ln[1].endswith("via ProvedorB)"))
        self.assertEqual((b[7], b[10]), ("2", "2 de 2"))

    def test_fora_da_conta_diz_o_motivo_de_cada_exclusao(self):
        fora = next(ln for ln in self.out.splitlines() if ln.startswith("fora da conta:"))
        self.assertTrue(fora.startswith("fora da conta: 4 ("), fora)
        for trecho in ("EXTERNAL_REVIEW_20260201-000006: META ilegível ou incompleto",
                       "EXTERNAL_REVIEW_20260201-000007: 2º revisor indisponível: nenhuma engine foi chamada",
                       "LEDGER_REVISAO_EXEMPLO.md:20: achado R1@codex: o rótulo @codex não é o da engine que "
                       "respondeu como revisor (claude)",
                       "LEDGER_REVISAO_EXEMPLO.md:21: achado R9@claude não está em EXTERNAL_REVIEW_20260201-000005"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, fora)

    def test_rodada_sem_achados_registrada_nao_e_pasta_sem_ledger(self):
        self.assertNotIn("EXTERNAL_REVIEW_20260201-000007: sem linha", self.out)


CAB = "| achado | sev | veredito | rodada | evidência | dano | revisão |\n|---|---|---|---|---|---|---|\n"
P1 = "EXTERNAL_REVIEW_20260201-000001"


class Ledgers(Base):
    """A ligação entre a linha do ledger e o papel (AT-003 e AT-005)."""

    def com(self, corpo: str, nome: str = "LEDGER_REVISAO_X.md") -> tuple[int, str]:
        led = self.escreve(self.tmp, nome, "# x\n\n" + CAB + corpo)
        return self.er(FX, "--ledgers", led, "--registry", FX / "registry.tsv")

    def fora(self, out: str) -> str:
        return next(ln for ln in out.splitlines() if ln.startswith("fora da conta:"))

    def test_sem_ledger_tudo_fica_sem_classificar_e_a_saida_diz(self):
        vazio = self.tmp / "ledgers"
        vazio.mkdir()
        rc, out = self.er(FX, "--ledgers", vazio, "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        revisor = linhas(out)[0]
        self.assertEqual((revisor[8], revisor[9], revisor[12], revisor[13], revisor[14]),
                         ("0 de 9", "0 de 9", "9 de 9", "—", "—"))
        self.assertIn("0 ledger(s)", out)
        self.assertIn("nenhum ledger lido: os achados das 6 pasta(s) ficam em sem classificar", self.fora(out))

    def test_pasta_sem_linha_conta_custo_e_achados_e_e_avisada(self):
        rc, out = self.com("| R1 | HIGH | APLICADA | rodada=1 | x | nao | %s |\n" % P1)
        self.assertEqual(rc, 0, out)
        revisor = linhas(out)[0]
        self.assertEqual((revisor[3], revisor[6], revisor[7], revisor[8], revisor[12]),
                         ("6", "≈7.0000", "9", "1 de 9", "8 de 9"))
        self.assertIn("EXTERNAL_REVIEW_20260201-000002: sem linha em nenhum ledger", self.fora(out))

    def test_linha_fora_do_formato_nunca_some_em_silencio(self):
        corpo = ("| R1 | HIGH | APLICADA | rodada=1 | formato antigo, de 5 colunas |\n"
                 "| R2 | MED | REBATIDA_EVIDENCA | rodada=1 | veredito digitado errado | nao | %s |\n" % P1 +
                 "| R3 | LOW | APLICADA | rodada=1 | pasta que não é de revisão | nao | rodada-1 |\n")
        rc, out = self.com(corpo)
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "0 de 9")
        fora = self.fora(out)
        for trecho in ("LEDGER_REVISAO_X.md:5: linha com 5 célula(s), o ledger tem 7",
                       "LEDGER_REVISAO_X.md:6: veredito `REBATIDA_EVIDENCA` fora da lista",
                       "LEDGER_REVISAO_X.md:7: revisão `rodada-1` não é uma pasta EXTERNAL_REVIEW_*"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, fora)

    def test_linhas_depois_de_linha_em_branco_entram_na_conta_ou_no_aviso(self):
        rc, out = self.com("| R1 | HIGH | APLICADA | rodada=1 | x | nao | %s |\n\n"
                           "| R2 | MED | APLICADA | rodada=1 | outra rodada, sem repetir o cabeçalho | nao | %s |\n\n"
                           "| R3 | LOW | APLICADA | rodada=1 | sem a marca de dano |\n" % (P1, P1))
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "2 de 9")
        self.assertIn("LEDGER_REVISAO_X.md:9: linha com 5 célula(s)", self.fora(out))

    def test_dano_fora_da_lista_e_avisado_e_nao_conta(self):
        rc, out = self.com("| R1 | HIGH | APLICADA | rodada=1 | teste: `test_x` | Sim | %s |\n" % P1)
        self.assertEqual(rc, 0, out)
        revisor = linhas(out)[0]
        self.assertEqual((revisor[8], revisor[9]), ("0 de 9", "0 de 9"))
        self.assertIn("LEDGER_REVISAO_X.md:5: dano `Sim` fora de sim, nao, ?", self.fora(out))

    def test_ledger_sem_rotulo_casa_com_id_rotulado_quando_nao_ha_ambiguidade(self):
        p3, p5 = P1[:-1] + "3", P1[:-1] + "5"
        rc, out = self.com("| R1 | MED | APLICADA | rodada=3 | na rodada 3 só há R1@claude | nao | %s |\n"
                           "| R2 | HIGH | APLICADA | rodada=5 | na rodada 5 só há R2@claude | nao | %s |\n"
                           "| R1 | MED | APLICADA | rodada=5 | na rodada 5 há R1@claude e R1@codex | nao | %s |\n"
                           % (p3, p5, p5))
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "2 de 9")
        self.assertEqual(next(ln for ln in linhas(out) if ln[1] == "codex (-)")[8], "0 de 1")
        self.assertIn("LEDGER_REVISAO_X.md:7: achado R1: sem rótulo e ambíguo: a revisão tem R1@claude, R1@codex",
                      self.fora(out))

    def test_linha_sem_barra_no_fim_conta(self):
        rc, out = self.com("| R1 | HIGH | APLICADA | rodada=1 | x | nao | %s\n" % P1)
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "1 de 9")

    def test_achado_repetido_conta_uma_vez_inclusive_com_interrogacao_e_em_dois_arquivos(self):
        pasta = self.tmp / "dois"
        self.escreve(pasta, "LEDGER_REVISAO_A.md", "# a\n\nretroativo: sim\n\n" + CAB +
                     "| R1 | HIGH | APLICADA | rodada=1 | x | ? | %s |\n" % P1)
        self.escreve(pasta, "LEDGER_REVISAO_B.md", "# b\n\nretroativo: sim\n\n" + CAB +
                     "| R1 | HIGH | APLICADA | rodada=1 | x | ? | %s |\n" % P1)
        rc, out = self.er(FX, "--ledgers", pasta, "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "1 de 9")
        self.assertIn("LEDGER_REVISAO_B.md:7: achado R1 repetido (1ª vez em LEDGER_REVISAO_A.md:7)", self.fora(out))
        self.assertIn("2 ledger(s)", out)

    def test_rotulo_da_engine_certa_casa_com_id_sem_rotulo(self):
        rc, out = self.com("| R1@claude | HIGH | APLICADA | rodada=1 | x | nao | %s |\n"
                           "| N1@openrouter-qwen-q-plus | HIGH | REBATIDA_EVIDENCIA | rodada=2 | x | nao | %s2 |\n"
                           % (P1, P1[:-1]))
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "1 de 9")
        b = next(ln for ln in linhas(out) if ln[1].endswith("via ProvedorB)"))
        self.assertEqual(b[10], "1 de 2")

    def test_rotulo_escrito_como_o_id_cru_da_engine_tambem_casa(self):
        rc, out = self.com("| N1@openrouter:qwen/q-plus | HIGH | REBATIDA_EVIDENCIA | rodada=2 | x | nao | %s2 |\n" % P1[:-1])
        self.assertEqual(rc, 0, out)
        self.assertEqual(next(ln for ln in linhas(out) if ln[1].endswith("via ProvedorB)"))[10], "1 de 2")
        self.assertNotIn("rótulo", self.fora(out))

    def test_sem_achados_dito_para_revisao_que_tem_achados_e_avisado(self):
        led = self.escreve(self.tmp, "LEDGER_REVISAO_X.md", "# x\n\nsem achados: rodada=2 %s2\nsem achados: rodada=7 %s7\n"
                           % (P1[:-1], P1[:-1]))
        rc, out = self.er(FX, "--ledgers", led, "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        fora = self.fora(out)
        self.assertIn("LEDGER_REVISAO_X.md:3: o ledger diz `sem achados` para EXTERNAL_REVIEW_20260201-000002, mas a "
                      "revisão tem 3 achado(s)", fora)
        self.assertNotIn("EXTERNAL_REVIEW_20260201-000007, mas", fora)   # a 7 não tem achado mesmo

    def test_tabela_que_nao_e_o_ledger_e_bloco_cercado_nao_sao_lidos(self):
        led = self.escreve(self.tmp, "LEDGER_REVISAO_X.md",
                           "# x\n\n| Engine | Papel |\n|---|---|\n| claude | revisor |\n\n```markdown\n" + CAB +
                           "| R2 | MED | APLICADA | rodada=1 | exemplo cercado | nao | %s |\n```\n\n" % P1 + CAB +
                           "| R1 | HIGH | APLICADA | rodada=1 | x | nao | %s |\n" % P1)
        rc, out = self.er(FX, "--ledgers", led, "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "1 de 9")
        self.assertNotIn("LEDGER_REVISAO_X.md", self.fora(out))

    def test_sem_registry_a_cobranca_e_desconhecida_e_o_pago_e_nd(self):
        reg = self.escreve(self.tmp, "registry.tsv", "# vazio\n")
        rc, out = self.er(FX, "--ledgers", FX, "--registry", reg)
        self.assertEqual(rc, 0, out)
        for ln in linhas(out):
            with self.subTest(linha=ln[1]):
                self.assertEqual((ln[2], ln[5], ln[13]), ("desconhecida", "n/d", "—"))


class Custo(Base):
    """As formas do campo *_custo do META.txt (AT-002)."""

    def uma(self, custo: str, engine: str = "openrouter:m/x", modelo: str = "m/x via P") -> tuple:
        d = self.tmp / "reviews/EXTERNAL_REVIEW_20260301-000001"
        self.escreve(d, "META.txt", "reviewer_engine_efetivo : %s\nreviewer_modelo : %s\nreviewer_custo : %s\n"
                                    "reviewer_exit : 0\n" % (engine, modelo, custo))
        self.escreve(d, "reviewer.verdicts.jsonl", "")
        rc, out = self.er(self.tmp / "reviews", "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        return linhas(out)[0]

    def test_formas_do_custo(self):
        casos = {
            "US$ 0.1000": ("0.1000", "0.1000"),
            "≈US$ 0.1000": ("≈0.1000", "≈0.1000"),
            "US$ 0.1000 + $?": ("0.1000 (incerto em 1 de 1)", "0.1000 (incerto em 1 de 1)"),
            "US$ 0,25": ("0.2500", "0.2500"),
            "≈US$ 0.000050": ("≈0.000050", "≈0.000050"),
            "$?": ("n/d", "n/d"),
            "n/d": ("n/d", "n/d"),
            "assinatura": ("n/d", "n/d"),
        }
        for custo, (pago, nominal) in casos.items():
            with self.subTest(custo=custo):
                ln = self.uma(custo)
                self.assertEqual((ln[5], ln[6]), (pago, nominal))

    def test_assinatura_tem_pago_zero_e_nominal_do_que_a_engine_reporta(self):
        ln = self.uma("US$ 1.2500", engine="claude", modelo="claude-x")
        self.assertEqual((ln[2], ln[5], ln[6]), ("assinatura", "0.0000", "1.2500"))

    def test_papel_com_exit_ausente_ou_engine_traco_nao_rodou(self):
        d = self.tmp / "reviews/EXTERNAL_REVIEW_20260301-000001"
        self.escreve(d, "META.txt", "reviewer_engine_efetivo : claude\nreviewer_modelo : claude-x\n"
                                    "reviewer_custo : US$ 1.0000\nreviewer_exit : 0\nrevisor2_engine : -\n"
                                    "revisor2_exit : -\nauditor_engine_efetivo : codex\nauditor_exit : -\n")
        rc, out = self.er(self.tmp / "reviews", "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        self.assertEqual([ln[0] for ln in linhas(out)], ["revisor"])

    def test_pasta_com_sufixo_de_colisao_e_lida_e_casa_com_o_ledger(self):
        nome = "EXTERNAL_REVIEW_20260301-000001-2"
        d = self.tmp / "reviews" / nome
        self.escreve(d, "META.txt", "reviewer_engine_efetivo : claude\nreviewer_modelo : claude-x\n"
                                    "reviewer_custo : US$ 1.0000\nreviewer_exit : 0\n")
        self.escreve(d, "reviewer.verdicts.jsonl", '{"achado": "R1", "severidade": "LOW"}\n')
        led = self.escreve(self.tmp, "LEDGER_REVISAO_X.md", "# x\n\n" + CAB +
                           "| R1 | LOW | APLICADA | rodada=1 | x | nao | %s |\n" % nome)
        rc, out = self.er(self.tmp / "reviews", "--ledgers", led, "--registry", FX / "registry.tsv")
        self.assertEqual(rc, 0, out)
        self.assertEqual(linhas(out)[0][8], "1 de 1")


class SemDadosEUso(Base):
    """AT-005."""

    def test_pasta_sem_revisao_e_2_sem_dados(self):
        vazia = self.tmp / "reviews"
        vazia.mkdir()
        rc, out = self.er(vazia)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: SEM DADOS\n→ ", out)

    def test_pasta_padrao_que_ainda_nao_existe_e_2(self):
        p = self.repo("projeto")
        rc, out = self.er(cwd=p)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: SEM DADOS", out)

    def test_fora_de_git_usa_a_pasta_atual(self):
        solta = self.tmp / "solta"
        shutil.copytree(str(FX), str(solta / "sdd/reports/reviews"))
        rc, out = self.er("--registry", FX / "registry.tsv", cwd=solta)
        self.assertEqual(rc, 0, out)
        self.assertIn("6 pasta(s) lida(s)", out)

    def test_le_o_output_dir_do_config(self):
        p = self.repo("projeto")
        shutil.copytree(str(FX), str(p / "onde/ficam"))
        self.escreve(p, "sdd/config.yaml", 'review:\n  output_dir: "onde/ficam"\n')
        rc, out = self.er("--registry", FX / "registry.tsv", cwd=p)
        self.assertEqual(rc, 0, out)
        self.assertIn("6 pasta(s) lida(s)", out)

    def test_uso_errado_e_64_com_causa_e_conserto(self):
        casos = {
            "pasta inexistente": ((self.tmp / "nao-existe",), "não existe"),
            "opção desconhecida": (("--json",), "opção desconhecida"),
            "argumento a mais": ((FX, FX), "argumento a mais"),
            "--ledgers sem valor": ((FX, "--ledgers"), "pede um caminho"),
            "--ledgers inexistente": ((FX, "--ledgers", self.tmp / "nada"), "não existe"),
            "--registry inexistente": ((FX, "--registry", self.tmp / "nada.tsv"), "não existe"),
        }
        for nome, (args, trecho) in casos.items():
            with self.subTest(caso=nome):
                rc, out = self.er(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn(trecho, out)
                self.assertIn("RESULTADO: PAROU\n→ ", out)

    def test_ajuda_mostra_so_o_uso(self):
        rc, out = self.er("--help")
        self.assertEqual(rc, 0, out)
        self.assertIn("0 MEDIDO · 2 SEM DADOS", out)
        self.assertNotIn("set -u", out)

    def test_nao_escreve_nada_na_pasta_lida(self):
        copia = self.tmp / "copia"
        shutil.copytree(str(FX), str(copia))

        def impressao():
            h = hashlib.sha256()
            for f in sorted(copia.rglob("*")):
                h.update(str(f.relative_to(copia)).encode())
                if f.is_file():
                    h.update(f.read_bytes())
            return h.hexdigest()

        antes = impressao()
        rc, out = self.er(copia, "--ledgers", copia, "--registry", copia / "registry.tsv")
        self.assertEqual(rc, 0, out)
        self.assertEqual(impressao(), antes)

    def test_o_script_nao_tem_rede_nem_chama_engine(self):
        fonte = ER.read_text(encoding="utf-8")
        nucleo = fonte.split("<<'PY'", 1)[1]
        self.assertEqual(re.findall(r"\b(socket|urllib|http\.client|requests|curl|wget)\b", nucleo), [])
        self.assertNotIn("adapters", nucleo)
        self.assertEqual(re.findall(r"^(?:import|from) (.+)$", nucleo, re.M),
                         ["json, os, re, subprocess, sys", "decimal import Decimal"])
        # o único subprocess é o `git rev-parse` que acha a raiz
        self.assertEqual(re.findall(r"subprocess\.run\(\[([^\]]*)\]", nucleo), ['"git", "rev-parse", "--show-toplevel"'])


if __name__ == "__main__":
    import unittest
    unittest.main()
