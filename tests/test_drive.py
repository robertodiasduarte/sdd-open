"""Contrato do sdd/bin/sdd-drive.sh (DEFINE F14_DRIVE AT-001 a AT-018): o script decide, conta e para; nunca publica.
O script roda de verdade, por subprocess, numa cópia dele com os vizinhos reais; o gate é um comando de fixture."""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import time
import unittest

from apoio import BASH, RAIZ, Sandbox

D = "sdd/features/DEFINE_F.md"
ESTADO = "sdd/reports/progress/DRIVE_F.json"
PROGRESS = "sdd/reports/progress/PROGRESS_F.md"
RELATORIO = "sdd/reports/DRIVE_REPORT_F.md"
MARCADOR = "[NEEDS " + "CLARIFICATION: qual?]"
# As 12 frases são contrato (UX_REVIEW_F14_DRIVE U2): fixas aqui, fora do script que as imprime.
FRASES = {
    "gate-verde": "O teste final passou e os relatórios estão prontos. Nada foi publicado.",
    "simulacao": "Simulação: nada foi executado nem gravado.",
    "orcamento-rodadas": "O teste final continuou vermelho nas rodadas permitidas. Nada foi publicado.",
    "manual-ux": "O teste final precisa da conferência de uma pessoa. Nada foi publicado.",
    "clarificacao-pendente": "O DEFINE ainda tem dúvida aberta ou a revisão de governança pendente.",
    "define-invalido": "O DEFINE não tem um teste final válido.",
    "gate-inconclusivo": "O teste final não chegou ao fim: isso não é vermelho e não gastou rodada.",
    "gate-alterado": "O comando do teste final mudou desde o início desta execução.",
    "bloqueio-humano": "A construção parou e precisa de você. Nada foi publicado.",
    "aguardando-sessao": "Esta etapa precisa de uma sessão nova do agente. Nada foi publicado.",
    "estado-invalido": "Não consegui ler onde a execução parou, e não vou adivinhar.",
    "branch-padrao": "O piloto não roda na branch principal: ele precisa de uma frente de trabalho própria.",
}
GOV = "## Technical Context\n\n| Aspect | Value | Notes |\n|---|---|---|\n| **Governança** | N.A. — teste | t |\n\n"


def define(cmd="echo x >> gate.calls; test -f .verde", kind="test", fallback="—", corpo=""):
    return ("# DEFINE: F\n\n" + corpo + "\n" + GOV + "## Verify Gate\n\n```yaml\nverify_gate:\n  kind: " + kind + "\n  cmd: \"" + cmd + "\"\n"
            "  pass_when: \"exit 0\"\n  threshold: \"—\"\n  manual_fallback: \"" + fallback + "\"\n```\n")


def design(arquivos=("a", "b"), acao="Modify", ledger=""):
    linhas = "".join("| %d | `%s` | %s | x | (general) | None |\n" % (k + 1, a, acao) for k, a in enumerate(arquivos))
    return ("# DESIGN: F\n\n## Metadata\n\n| Attribute | Value |\n|---|---|\n| **Status** | Ready for Build |\n\n## Key Decisions\n\n"
            "### Decision 1: x\n\nx\n\n## File Manifest\n\n| # | File | Action | Purpose | Agent / Owner | Dependencies |\n"
            "|---:|---|---|---|---|---|\n" + linhas + "\n**Total Files:** %d\n" % len(arquivos) + ledger)


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.git(self.r, "symbolic-ref", "HEAD", "refs/heads/frente")
        for s in ("sdd/bin/sdd-drive.sh", "sdd/bin/verify-gate.sh", "sdd/bin/sdd-fluxo.sh", "sdd/bin/design-lint.py"):
            self.copia(s, self.r)
        self.escreve(self.r, "sdd/bin/report-lint.py",
                     "import os, sys\nrc = int(open('.lint-rc').read()) if os.path.exists('.lint-rc') else 0\nprint('lint ' + ' '.join(sys.argv[1:]))\nsys.exit(rc)\n")
        self.escreve(self.r, ".gitignore", ".verde\ngate.calls\n.lint-rc\n.rc\nbrief.md\n")
        self.escreve(self.r, D, define())
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design())
        self.commit(self.r)

    def drive(self, *args, env=None):
        return self.roda([BASH, "sdd/bin/sdd-drive.sh", *args], self.r, env)

    def assertParada(self, res, motivo, exitc=20):
        rc, out, err = res
        self.assertEqual(rc, exitc, out + err)
        self.assertIn("motivo: " + motivo, out)
        self.assertIn(FRASES[motivo], out)
        self.assertResultado(out)

    def assertAcao(self, res, acao):
        rc, out, err = res
        self.assertEqual(rc, 10, out + err)
        self.assertRegex(out, r"(?m)^ACAO: %s$" % acao)
        self.assertRegex(out, r"(?m)^rodada: \d+/\d+$")
        self.assertIn("RESULTADO: CONTINUAR", out)

    def estado(self):
        return json.loads((self.r / ESTADO).read_text(encoding="utf-8"))

    def chamadas(self):
        p = self.r / "gate.calls"
        return len(p.read_text(encoding="utf-8").splitlines()) if p.exists() else 0

    def feito(self):
        self.escreve(self.r, PROGRESS, "- [x] a\n- [x] b\n")

    def verde(self):
        self.escreve(self.r, ".verde", "")

    def novo_commit(self, nome="codigo.txt"):
        self.escreve(self.r, nome, "x\n")
        self.git(self.r, "add", nome)
        self.git(self.r, "commit", "-q", "-m", "c")

    def existe(self, rel):
        return (self.r / rel).exists()


class Iniciar(Base):
    def test_grava_o_estado_e_diz_a_1a_acao(self):
        res = self.drive("iniciar", D)
        self.assertAcao(res, "RODADA")
        self.assertIn("rodada: 1/3", res[1])
        self.assertIn("tarefa: 1 de 2 — a", res[1])
        st = self.estado()
        self.assertEqual((st["define"], st["maximo"], st["gates"]), (D, 3, []))
        self.assertEqual(st["inicio"], self.git(self.r, "rev-parse", "HEAD").strip())
        self.assertRegex(st["gate_sha"], r"^[0-9a-f]{64}$")

    def test_json_do_projeto_nao_entra_no_lugar_do_modulo(self):
        self.escreve(self.r, "json.py", "raise SystemExit('sombra')\n")
        self.assertEqual(self.drive("--dry-run", D)[0], 0)

    def test_vizinho_que_cai_sem_motivo_nao_vira_acao(self):
        self.drive("iniciar", D)
        self.escreve(self.r, "sdd/bin/sdd-fluxo.sh", "#!/bin/bash\n# --drive\necho quebrou >&2\nexit 1\n")
        rc, out, err = self.drive("proximo", D)
        self.assertEqual(rc, 2, out + err)
        self.assertNotIn("ACAO:", out)


class Recusas(Base):
    def assertSemEstado(self):
        self.assertFalse(self.existe(ESTADO))

    def test_branch_padrao_pelo_slot_e_pelo_remoto_e_head_destacado(self):
        self.escreve(self.r, "sdd/config.yaml", "project:\n  default_branch: frente\n")
        self.assertParada(self.drive("iniciar", D), "branch-padrao")
        self.assertParada(self.drive("--dry-run", D), "branch-padrao")
        self.assertSemEstado()
        (self.r / "sdd/config.yaml").unlink()
        self.git(self.r, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/frente")
        self.assertParada(self.drive("iniciar", D), "branch-padrao")
        self.git(self.r, "symbolic-ref", "--delete", "refs/remotes/origin/HEAD")
        self.git(self.r, "checkout", "-q", "--detach")
        res = self.drive("iniciar", D)
        self.assertParada(res, "branch-padrao")
        self.assertIn("HEAD destacado", res[1])
        self.assertSemEstado()

    def test_outra_branch_com_slot_passa(self):
        # o outro lado: o slot de exemplo main não barra a frente
        self.escreve(self.r, "sdd/config.yaml", "project:\n  default_branch: main\n")
        self.assertAcao(self.drive("iniciar", D), "RODADA")

    def test_define_sem_gate_valido(self):
        for texto in ("# DEFINE: F\n\n" + GOV, define(kind="xyz"), define(cmd="N/A (x)")):
            with self.subTest(texto=texto[-80:]):
                self.escreve(self.r, D, texto)
                self.assertParada(self.drive("iniciar", D), "define-invalido")
                self.assertParada(self.drive("--dry-run", D), "define-invalido")
                self.assertSemEstado()

    def test_define_que_nao_existe(self):
        (self.r / D).unlink()
        self.assertParada(self.drive("iniciar", D), "define-invalido")

    def test_duvida_aberta_e_governanca_pendente(self):
        for texto in (define(corpo=MARCADOR), define().replace("N.A. — teste", "pendente")):
            with self.subTest():
                self.escreve(self.r, D, texto)
                self.assertParada(self.drive("iniciar", D), "clarificacao-pendente")
                self.assertSemEstado()

    def test_vizinho_antigo_sai_2_e_nao_acusa_o_define(self):
        for arq, marca in (("sdd/bin/verify-gate.sh", "--checar"), ("sdd/bin/sdd-fluxo.sh", "--drive")):
            with self.subTest(arq=arq):
                original = (self.r / arq).read_text(encoding="utf-8")
                (self.r / arq).write_text(original.replace(marca, "--outra"), encoding="utf-8")
                for verbo in ("iniciar", "--dry-run", "--resume"):
                    rc, out, err = self.drive(verbo, D)
                    self.assertEqual(rc, 2, out + err)
                    self.assertIn("RESULTADO: FALHA", err)
                    self.assertIn(arq, err)
                    self.assertIn("doctor", err)
                    self.assertNotIn("define-invalido", out + err)
                self.assertSemEstado()
                (self.r / arq).write_text(original, encoding="utf-8")

    def test_uso(self):
        for args in ((), ("xyz",), ("iniciar",), ("iniciar", "sdd/features/OUTRO.md"), ("iniciar", "../DEFINE_F.md"),
                     ("iniciar", D, "--max"), ("iniciar", D, "extra"), ("proximo",), ("bloqueio", D), ("recibo", D, " "),
                     ("aguardar", D, "x"), ("--self-test", "x")):
            with self.subTest(args=args):
                rc, out, err = self.drive(*args)
                self.assertEqual(rc, 64, out + err)
                self.assertIn("RESULTADO: ERRO DE USO", err)

    def test_fora_de_git_sai_64(self):
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, _o, e = self.roda([BASH, self.r / "sdd/bin/sdd-drive.sh", "iniciar", D], fora)
        self.assertEqual(rc, 64, e)

    def test_nao_consegue_gravar_sai_2(self):
        self.escreve(self.r, "sdd/reports", "arquivo no lugar da pasta\n")
        rc, out, err = self.drive("iniciar", D)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("RESULTADO: FALHA", err)


class Simulacao(Base):
    def test_mostra_o_plano_e_nao_grava_nem_roda(self):
        antes = self.git(self.r, "status", "--porcelain", "--ignored")
        res = self.drive("--dry-run", D)
        self.assertParada(res, "simulacao", 0)
        self.assertIn("kind: test", res[1])
        self.assertIn("cmd: echo x >> gate.calls", res[1])
        self.assertEqual(self.git(self.r, "status", "--porcelain", "--ignored"), antes)
        self.assertEqual(self.chamadas(), 0)
        self.assertFalse(self.existe("sdd/reports"))


class Limite(Base):
    def maximo(self, *args):
        self.assertAcao(self.drive("iniciar", D, *args), "RODADA")
        return self.estado()["maximo"]

    def test_flag_slot_e_default(self):
        self.assertEqual(self.maximo(), 3)
        (self.r / ESTADO).unlink()
        self.escreve(self.r, "sdd/config.yaml", "drive:\n  max_rounds: 5\n")
        self.assertEqual(self.maximo(), 5)
        (self.r / ESTADO).unlink()
        self.assertEqual(self.maximo("--max", "2"), 2)

    def test_valor_invalido_sai_64_dizendo_de_onde_veio(self):
        for arg, slot, onde in (("0", None, "--max"), ("x", None, "--max"), (None, "-1", "drive.max_rounds"), (None, "dois", "drive.max_rounds")):
            with self.subTest(arg=arg, slot=slot):
                if slot:
                    self.escreve(self.r, "sdd/config.yaml", "drive:\n  max_rounds: %s\n" % slot)
                rc, out, err = self.drive("iniciar", D, *(("--max", arg) if arg else ()))
                self.assertEqual(rc, 64, out + err)
                self.assertIn(onde, err)
                self.assertFalse(self.existe(ESTADO))


class Proxima(Base):
    def test_sem_design(self):
        (self.r / "sdd/features/DESIGN_F.md").unlink()
        self.git(self.r, "add", "-A")
        self.git(self.r, "commit", "-q", "-m", "c")
        self.assertAcao(self.drive("iniciar", D), "DESIGN")

    def test_design_que_nao_passa_no_lint_volta_ao_design_com_o_motivo(self):
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design().replace("**Total Files:** 2", "**Total Files:** 9"))
        res = self.drive("iniciar", D)
        self.assertAcao(res, "DESIGN")
        self.assertIn("design-lint", res[1])

    def test_revisao_exigida_sem_registro_e_com_high_aberto(self):
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design(("a", "b", "c"), "Create"))
        res = self.drive("iniciar", D)
        self.assertAcao(res, "REVISAO_DESIGN")
        led = "\n## Advisor Ledger\n\n| # | Nota | Severidade | Veredito |\n|---|---|---|---|\n| H1 | x | HIGH | %s |\n"
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design(("a", "b", "c"), "Create", led % "aberta"))
        self.assertAcao(self.drive("proximo", D), "REVISAO_DESIGN")
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design(("a", "b", "c"), "Create", led % "APLICADA"))
        self.assertAcao(self.drive("proximo", D), "RODADA")

    def test_saida_64_do_seguir_nao_vira_design(self):
        self.drive("iniciar", D)
        self.escreve(self.r, "sdd/bin/sdd-fluxo.sh", "#!/bin/bash\n# --drive\nexit 64\n")
        rc, out, err = self.drive("proximo", D)
        self.assertEqual(rc, 2, out + err)
        self.assertNotIn("ACAO: DESIGN", out)

    def test_tarefa_i_de_n_e_verificar_quando_acaba(self):
        self.drive("iniciar", D)
        self.escreve(self.r, PROGRESS, "- [x] a\n- [ ] b\n")
        res = self.drive("proximo", D)
        self.assertAcao(res, "RODADA")
        self.assertIn("tarefa: 2 de 2 — b", res[1])
        self.feito()
        self.assertAcao(self.drive("proximo", D), "VERIFICAR")

    def test_semeia_e_acrescenta_linha_nova_do_manifest(self):
        self.drive("iniciar", D)
        self.assertEqual((self.r / PROGRESS).read_text(encoding="utf-8").split("\n")[2:4], ["- [ ] a", "- [ ] b"])
        self.escreve(self.r, PROGRESS, "- [x] a · sha 123\n- [x] b\n")
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design(("a", "b", "c")))
        res = self.drive("proximo", D)
        self.assertAcao(res, "RODADA")
        self.assertIn("tarefa: 3 de 3 — c", res[1])
        self.assertEqual((self.r / PROGRESS).read_text(encoding="utf-8").count("- [ ]"), 1, "linha já feita não volta")

    def test_progress_ou_manifest_sem_linhas(self):
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design(()).replace("**Total Files:** 0", "**Total Files:** 0"))
        self.drive("iniciar", D)
        self.escreve(self.r, "sdd/features/DESIGN_F.md", design())
        self.escreve(self.r, PROGRESS, "só texto\n")
        res = self.drive("proximo", D)
        self.assertParada(res, "estado-invalido")
        self.assertIn(PROGRESS, res[1])

    def test_3a_repeticao_para_e_mudanca_de_head_zera(self):
        self.drive("iniciar", D)
        self.assertAcao(self.drive("proximo", D), "RODADA")
        self.assertAcao(self.drive("proximo", D), "RODADA")
        self.novo_commit()  # andou
        self.assertAcao(self.drive("proximo", D), "RODADA")
        self.assertAcao(self.drive("proximo", D), "RODADA")
        res = self.drive("proximo", D)
        self.assertParada(res, "bloqueio-humano")
        self.assertIn("tarefa: 1 de 2 — a", res[1])
        self.assertAcao(self.drive("--resume", D), "RODADA")
        self.assertAcao(self.drive("proximo", D), "RODADA", )


class Verificar(Base):
    def pronto(self, *args):
        self.drive("iniciar", D, *args)
        self.feito()

    def test_log_com_o_comando_primeiro_e_o_exit_real(self):
        self.pronto()
        res = self.drive("verificar", D)
        self.assertAcao(res, "CORRIGIR")
        self.assertIn("restam 2 rodada(s)", res[1])
        log = (self.r / "sdd/reports/evidence/F/DRIVE-gate-r1.log").read_text(encoding="utf-8").split("\n")
        self.assertTrue(log[0].startswith("$ verify-gate.sh"))
        self.assertEqual(log[-2], "[exit=2]")
        g = self.estado()["gates"][0]
        self.assertEqual((g["exit"], g["rodada"], g["commit"]), (2, 1, self.git(self.r, "rev-parse", "HEAD").strip()))
        self.assertEqual(self.chamadas(), 1)

    def test_verde_vai_para_avaliar_e_gate_rodou_pelo_script(self):
        self.pronto()
        self.verde()
        self.assertAcao(self.drive("verificar", D), "AVALIAR_E_RELATAR")
        self.assertEqual(self.chamadas(), 1)

    def test_tarefa_pendente_nao_roda_o_gate(self):
        self.drive("iniciar", D)
        self.assertAcao(self.drive("verificar", D), "RODADA")
        self.assertEqual(self.chamadas(), 0)

    def test_sem_mudanca_de_codigo_nao_roda_de_novo_nem_gasta(self):
        self.pronto()
        self.drive("verificar", D)
        self.assertAcao(self.drive("verificar", D), "CORRIGIR")
        self.escreve(self.r, "sdd/reports/x.md", "doc\n")
        self.git(self.r, "add", "sdd/reports/x.md")
        self.git(self.r, "commit", "-q", "-m", "só documento")
        self.assertAcao(self.drive("verificar", D), "CORRIGIR")
        self.assertEqual(self.chamadas(), 1)
        self.novo_commit()
        self.assertAcao(self.drive("verificar", D), "CORRIGIR")
        self.assertEqual(self.chamadas(), 2, "commit de código roda de novo")
        self.assertEqual(len(self.estado()["gates"]), 2)

    def test_sujo_fora_dos_documentos_vira_commitar(self):
        self.pronto()
        for rel, adiciona in (("src/novo.py", False), ("sdd/bin/report-lint.py", False)):
            with self.subTest(rel=rel):
                self.escreve(self.r, rel, "x\n")
                res = self.drive("verificar", D)
                self.assertAcao(res, "COMMITAR")
                self.assertIn("   - " + rel, res[1])
                self.assertEqual(self.chamadas(), 0)
                self.git(self.r, "add", rel)
                self.git(self.r, "commit", "-q", "-m", "c")

    def test_documento_nao_rastreado_nao_trava(self):
        self.pronto()
        self.escreve(self.r, "sdd/reviews/X.md", "x\n")
        self.assertAcao(self.drive("verificar", D), "CORRIGIR")
        self.assertEqual(self.chamadas(), 1)

    def stub_gate(self):
        p = self.r / "sdd/bin/verify-gate.sh"
        (self.r / "sdd/bin/verify-gate-real.sh").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
        p.write_text('#!/bin/bash\n# --checar\ncase "$1" in --print|--checar) exec bash "$(dirname "$0")/verify-gate-real.sh" "$@" ;; esac\n'
                     'echo x >> gate.calls\nexit "$(cat .rc)"\n', encoding="utf-8")
        self.commit(self.r)

    def test_exits_que_nao_gastam_rodada(self):
        self.stub_gate()
        self.pronto()
        for codigo, motivo in ((3, "gate-inconclusivo"), (127, "gate-inconclusivo"), (1, "gate-inconclusivo"), (4, "manual-ux"),
                               (5, "clarificacao-pendente"), (64, "define-invalido")):
            with self.subTest(codigo=codigo):
                self.escreve(self.r, ".rc", str(codigo))
                self.assertParada(self.drive("verificar", D), motivo)
                self.assertAcao(self.drive("--resume", D), "VERIFICAR")
        st = self.estado()
        self.assertEqual(len(st["gates"]), 6)
        self.assertNotIn(2, [g["exit"] for g in st["gates"]])
        self.assertEqual(len(list((self.r / "sdd/reports/evidence/F").glob("DRIVE-gate-r*.log"))), 6, "nenhum log sobrescrito")

    def test_parada_do_gate_aparece_no_proximo_ate_o_resume(self):
        self.stub_gate()
        self.pronto()
        self.escreve(self.r, ".rc", "3")
        self.drive("verificar", D)
        self.assertParada(self.drive("proximo", D), "gate-inconclusivo")
        self.assertAcao(self.drive("--resume", D), "VERIFICAR")

    def test_limite(self):
        self.pronto("--max", "2")
        self.assertAcao(self.drive("verificar", D), "CORRIGIR")
        self.novo_commit()
        self.assertParada(self.drive("verificar", D), "orcamento-rodadas")
        self.assertEqual(self.chamadas(), 2)
        self.novo_commit("outro.txt")
        for verbo in ("proximo", "verificar", "concluir"):
            with self.subTest(verbo=verbo):
                self.assertParada(self.drive(verbo, D), "orcamento-rodadas")
        self.assertEqual(self.chamadas(), 2, "o limite barra por script")
        res = self.drive("--resume", D)
        self.assertParada(res, "orcamento-rodadas")
        self.verde()
        self.assertAcao(self.drive("--resume", D, "--max", "3"), "VERIFICAR")
        self.assertAcao(self.drive("verificar", D), "AVALIAR_E_RELATAR")


class SegundoPlano(Base):
    def setUp(self):
        super().setUp()
        self.escreve(self.r, D, define(cmd="echo x >> gate.calls; sleep 2; test -f .verde"))
        self.commit(self.r)
        self.drive("iniciar", D)
        self.feito()

    def espera_acabar(self):
        for _ in range(100):
            if not self.existe("sdd/reports/progress/DRIVE_F.lock"):
                return
            time.sleep(0.1)
        self.fail("o teste final do fundo não terminou")

    def test_fundo_devolve_na_hora_e_o_resultado_chega_pelo_proximo(self):
        self.verde()
        inicio = time.time()
        res = self.drive("verificar", D, "--fundo")
        self.assertAcao(res, "ESPERAR")
        self.assertLess(time.time() - inicio, 1.9, "não pode esperar o gate")
        self.assertAcao(self.drive("proximo", D), "ESPERAR")
        self.assertAcao(self.drive("verificar", D), "ESPERAR")
        self.espera_acabar()
        self.assertAcao(self.drive("proximo", D), "AVALIAR_E_RELATAR")
        self.assertEqual(self.chamadas(), 1, "2ª chamada não abre outro gate")

    def test_duas_chamadas_juntas_rodam_um_gate_so(self):
        import subprocess
        procs = [subprocess.Popen([BASH, "sdd/bin/sdd-drive.sh", "verificar", D], cwd=str(self.r), env=self.env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  stdin=subprocess.DEVNULL) for _ in range(2)]
        saidas = [p.communicate()[0].decode("utf-8", "replace") for p in procs]
        self.assertEqual(self.chamadas(), 1, saidas)
        self.assertTrue(any("ACAO: ESPERAR" in s for s in saidas), saidas)
        self.assertEqual(len(self.estado()["gates"]), 1)

    def test_trava_de_processo_morto_se_libera(self):
        self.escreve(self.r, "sdd/reports/progress/DRIVE_F.lock", "999999")
        self.assertAcao(self.drive("proximo", D), "VERIFICAR")
        self.assertFalse(self.existe("sdd/reports/progress/DRIVE_F.lock"))

    def test_recibo_gravado_durante_o_gate_nao_se_perde(self):
        self.verde()
        self.assertAcao(self.drive("verificar", D, "--fundo"), "ESPERAR")
        self.assertEqual(self.drive("recibo", D, "decidi x")[0], 0)
        self.espera_acabar()
        st = self.estado()
        self.assertEqual(st["recibos"], ["decidi x"])
        self.assertEqual(len(st["gates"]), 1)


class ImpressaoDigital(Base):
    def test_cmd_alterado_para_em_todo_verbo_sem_rodar(self):
        self.drive("iniciar", D)
        self.feito()
        self.escreve(self.r, D, define(cmd="true"))
        for verbo in ("proximo", "verificar", "concluir", "--resume"):
            with self.subTest(verbo=verbo):
                res = self.drive(verbo, D)
                self.assertParada(res, "gate-alterado")
                self.assertIn("antes: echo x", res[1])
                self.assertIn("agora: true", res[1])
        self.assertEqual(self.chamadas(), 0)

    def test_checklist_do_manual_tambem_conta(self):
        self.escreve(self.r, D, define(cmd="N/A (manual-ux)", kind="manual-ux", fallback="Eu abri A"))
        self.commit(self.r)
        self.drive("iniciar", D)
        self.escreve(self.r, D, define(cmd="N/A (manual-ux)", kind="manual-ux", fallback="Eu abri B"))
        self.assertParada(self.drive("proximo", D), "gate-alterado")

    def test_mudanca_fora_do_bloco_nao_para(self):
        self.drive("iniciar", D)
        self.escreve(self.r, D, define(corpo="uma nota nova"))
        self.assertAcao(self.drive("proximo", D), "RODADA")

    def test_aceitar_invalida_o_verde_antigo(self):
        self.drive("iniciar", D)
        self.feito()
        self.verde()
        self.drive("verificar", D)
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.escreve(self.r, D, define(cmd="echo x >> gate.calls; test -f .outro"))
        self.commit(self.r)
        self.assertAcao(self.drive("--resume", D, "--aceitar-gate-novo"), "VERIFICAR")
        self.assertAcao(self.drive("concluir", D), "VERIFICAR")
        rel = (self.r / RELATORIO)
        self.drive("recibo", D, "x")
        texto = rel.read_text(encoding="utf-8")
        self.assertIn("test -f .verde", texto)
        self.assertIn("test -f .outro", texto)

    def test_aceitar_depois_de_vermelho_roda_no_mesmo_head(self):
        self.drive("iniciar", D)
        self.feito()
        self.drive("verificar", D)
        self.assertEqual(self.chamadas(), 1)
        self.escreve(self.r, D, define(cmd="echo x >> gate.calls; true"))
        self.commit(self.r)
        self.git(self.r, "reset", "-q", "--soft", "HEAD~1")
        self.git(self.r, "commit", "-q", "-m", "mesmo conteúdo")
        self.assertAcao(self.drive("--resume", D, "--aceitar-gate-novo"), "VERIFICAR")
        self.assertAcao(self.drive("verificar", D), "AVALIAR_E_RELATAR")
        self.assertEqual(self.chamadas(), 2)


class Retomada(Base):
    def test_diz_onde_parou_e_nao_gasta(self):
        self.drive("iniciar", D)
        self.feito()
        self.drive("verificar", D)
        self.novo_commit()
        rodada = self.estado()["gates"]
        res = self.drive("--resume", D)
        self.assertAcao(res, "VERIFICAR")
        self.assertIn("retomando: rodada 2/3 · 2 de 2 tarefas prontas · último teste final: 2 · não gastei rodada", res[1])
        self.assertEqual(self.estado()["gates"], rodada)

    def test_estado_invalido_em_todo_verbo(self):
        for verbo, extra in (("--resume", ()), ("proximo", ()), ("verificar", ()), ("concluir", ()), ("bloqueio", ("x",)), ("recibo", ("x",)),
                             ("aguardar", ("executor-drive", "brief.md"))):
            with self.subTest(verbo=verbo, caso="ausente"):
                self.assertParada(self.drive(verbo, D, *extra), "estado-invalido")
        self.escreve(self.r, ESTADO, "{ nao é json")
        self.assertParada(self.drive("proximo", D), "estado-invalido")
        self.assertIn("{ nao é json", (self.r / ESTADO).read_text(encoding="utf-8"), "nunca reescreve o que não entendeu")
        self.escreve(self.r, ESTADO, "[1]")
        self.assertParada(self.drive("proximo", D), "estado-invalido")
        (self.r / ESTADO).unlink()
        self.drive("iniciar", D)
        st = self.estado()
        st["define"] = "sdd/features/DEFINE_OUTRO.md"
        self.escreve(self.r, ESTADO, json.dumps(st))
        res = self.drive("proximo", D)
        self.assertParada(res, "estado-invalido")
        self.assertIn("outro DEFINE", res[1])

    def test_iniciar_com_estado_recusa_e_aponta_a_saida(self):
        self.drive("iniciar", D)
        res = self.drive("iniciar", D)
        self.assertParada(res, "estado-invalido")
        self.assertIn("--resume", res[1])
        self.assertIn(ESTADO, res[1])


class Concluir(Base):
    def verde_ate_avaliar(self):
        self.drive("iniciar", D)
        self.feito()
        self.verde()
        self.assertAcao(self.drive("verificar", D), "AVALIAR_E_RELATAR")

    def test_sem_gate_nao_conclui(self):
        self.drive("iniciar", D)
        self.feito()
        self.assertAcao(self.drive("concluir", D), "VERIFICAR")

    def test_sem_relatorio_nao_conclui(self):
        self.verde_ate_avaliar()
        res = self.drive("concluir", D)
        self.assertAcao(res, "AVALIAR_E_RELATAR")
        self.assertIn("BUILD_REPORT_F.md", res[1])

    def test_conclui_com_documento_depois_do_verde(self):
        self.verde_ate_avaliar()
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.git(self.r, "add", "sdd/reports/BUILD_REPORT_F.md")
        self.git(self.r, "commit", "-q", "-m", "relatório")
        res = self.drive("concluir", D)
        self.assertParada(res, "gate-verde", 0)
        self.assertIn("sdd-release", res[1])
        self.assertIn("Nada foi publicado.", res[1])

    def test_codigo_depois_do_verde_volta_ao_gate(self):
        self.verde_ate_avaliar()
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.novo_commit()
        res = self.drive("concluir", D)
        self.assertAcao(res, "VERIFICAR")
        self.assertIn("código novo", res[1])

    def test_codigo_sujo_depois_do_verde_vira_commitar(self):
        self.verde_ate_avaliar()
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.escreve(self.r, "src/a.py", "x\n")
        self.assertAcao(self.drive("concluir", D), "COMMITAR")

    def test_relatorio_que_reprova_volta_com_as_linhas(self):
        self.verde_ate_avaliar()
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.escreve(self.r, ".lint-rc", "1")
        res = self.drive("concluir", D)
        self.assertAcao(res, "AVALIAR_E_RELATAR")
        self.assertIn("lint sdd/reports/BUILD_REPORT_F.md", res[1])


class Relatorio(Base):
    def test_toda_parada_reescreve_com_o_motivo(self):
        self.drive("iniciar", D, "--max", "1")
        self.feito()
        self.drive("verificar", D)
        texto = (self.r / RELATORIO).read_text(encoding="utf-8")
        self.assertIn(FRASES["orcamento-rodadas"] + " Rodadas vermelhas: 1 de 1.", texto.split("\n")[2])
        self.assertIn("| Motivo | orcamento-rodadas |", texto)
        self.assertIn("DRIVE-gate-r1.log", texto)
        self.assertIn("Nada foi publicado", texto.split("\n")[-2])
        self.drive("--resume", D, "--max", "2")
        self.drive("bloqueio", D, "falta a chave do banco")
        texto = (self.r / RELATORIO).read_text(encoding="utf-8")
        self.assertIn("| Motivo | bloqueio-humano |", texto)
        self.assertIn("falta a chave do banco", texto)

    def test_commits_desde_o_inicio(self):
        self.drive("iniciar", D)
        self.novo_commit()
        self.drive("bloqueio", D, "x")
        self.assertRegex((self.r / RELATORIO).read_text(encoding="utf-8"), r"(?m)^- [0-9a-f]+ c$")

    def test_recibo_na_secao_e_sai_0(self):
        self.drive("iniciar", D)
        rc, out, _ = self.drive("recibo", D, "usei o modo de sempre; desfaça com git revert")
        self.assertEqual(rc, 0, out)
        texto = (self.r / RELATORIO).read_text(encoding="utf-8")
        self.assertIn("## Decidi sozinho\n\n- usei o modo de sempre; desfaça com git revert", texto)


class Aguardar(Base):
    def setUp(self):
        super().setUp()
        self.drive("iniciar", D)
        self.escreve(self.r, "brief.md", "faça a tarefa\n")

    def test_parada_com_a_tarefa_e_o_aviso_das_paradas(self):
        res = self.drive("aguardar", D, "executor-drive", "brief.md")
        self.assertParada(res, "aguardando-sessao", 40)
        self.assertIn("tarefa: a", res[1])
        self.assertIn("até 2 parada(s)", res[1])
        self.assertIn("nada foi publicado", res[1])
        self.assertIn("<<<RODADA", res[1])
        self.assertTrue(self.existe("sdd/reports/briefs/BRIEF_executor-drive_F.md"))
        self.assertAcao(self.drive("--resume", D), "RODADA")
        self.assertNotIn("até 2 parada(s)", self.drive("aguardar", D, "executor-drive", "brief.md")[1], "avisa uma vez")

    def test_despachar_com_erro_e_repetido_sem_gravar_o_motivo(self):
        rc, out, err = self.drive("aguardar", D, "executor-drive", "nao-existe.md")
        self.assertEqual(rc, 64, out + err)
        self.assertNotIn("motivo: aguardando-sessao", out)
        self.assertEqual(self.estado()["motivo"], "")

    def test_bloqueio(self):
        res = self.drive("bloqueio", D, "falta a chave")
        self.assertParada(res, "bloqueio-humano")
        self.assertIn("falta a chave", res[1])


class Barreira(Base):
    """AT-017: a sequência inteira com git e gh de mentira; o registro mostra que nada publica."""

    def test_nenhum_verbo_publica(self):
        shims = self.tmp / "shims"
        shims.mkdir()
        registro = self.tmp / "chamadas.log"
        real = shutil.which("git")
        for nome, destino in (("git", 'exec "%s" "$@"' % real), ("gh", "exit 0")):
            p = shims / nome
            p.write_text('#!/bin/sh\necho "%s $*" >> "%s"\n%s\n' % (nome, registro, destino), encoding="utf-8")
            p.chmod(p.stat().st_mode | stat.S_IEXEC)
        env = dict(self.env, PATH=str(shims) + os.pathsep + self.env["PATH"])
        self.escreve(self.r, "brief.md", "x\n")
        self.assertEqual(self.drive("--dry-run", D, env=env)[0], 0)
        self.assertEqual(self.drive("iniciar", D, env=env)[0], 10)
        self.assertEqual(self.drive("proximo", D, env=env)[0], 10)
        self.assertEqual(self.drive("recibo", D, "r", env=env)[0], 0)
        self.assertEqual(self.drive("aguardar", D, "executor-drive", "brief.md", env=env)[0], 40)
        self.assertEqual(self.drive("--resume", D, env=env)[0], 10)
        self.feito()
        self.assertEqual(self.drive("verificar", D, env=env)[0], 10)
        self.verde()
        self.novo_commit()
        self.assertEqual(self.drive("verificar", D, env=env)[0], 10)
        self.escreve(self.r, "sdd/reports/BUILD_REPORT_F.md", "x\n")
        self.assertEqual(self.drive("concluir", D, env=env)[0], 0)
        self.assertEqual(self.drive("bloqueio", D, "b", env=env)[0], 20)
        log = registro.read_text(encoding="utf-8")
        self.assertIn("git ", log, "o shim precisa ter sido chamado, senão o teste não prova nada")
        for proibido in (r"\bpush\b", r"^gh ", r"\brelease\b", r"workflow run", r"\bfetch\b"):
            self.assertIsNone(re.search(proibido, log, re.M), proibido)

    def test_o_script_nao_cita_comando_que_publica(self):
        texto = (RAIZ / "sdd/bin/sdd-drive.sh").read_text(encoding="utf-8")
        for proibido in ("git push", "\"push\"", "gh release", "workflow run", "deploy.cmd", "DEPLOY_CMD"):
            self.assertNotIn(proibido, texto)


class SelfTest(Sandbox):
    def test_verde_sem_git_e_sem_deixar_nada(self):
        temp = self.tmp / "temp"
        temp.mkdir()
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, out, err = self.roda([BASH, RAIZ / "sdd/bin/sdd-drive.sh", "--self-test"], fora, dict(self.env, TMPDIR=str(temp)))
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: VERDE", out)
        self.assertEqual(list(temp.iterdir()), [])
        self.assertEqual(list(fora.iterdir()), [])
        for motivo in FRASES:
            self.assertIn(motivo, out)
        self.assertLess(out.index("branch-padrao"), out.index("verde: iniciar"), "vermelhos antes dos verdes")


if __name__ == "__main__":
    unittest.main()
