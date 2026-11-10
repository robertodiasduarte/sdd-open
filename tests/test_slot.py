"""sdd/bin/slot.sh (F15_SLOTS): o executor dos 4 slots de extensão (smoke.before_ok_cmd, smoke.before_push_cmd,
smoke.after_deploy_cmd, schema.check_cmd). Contrato: vazio = PULADO (11) · 0 OK · 2 REPROVOU · 10 NADA A MEDIR ·
qualquer outro exit ou sinal = INCONCLUSIVO (3) · 64 uso. Os testes rodam o script de verdade com um comando falso
que grava o ambiente e os argumentos que recebeu (AT-001 a AT-005 do DEFINE_F15_SLOTS).
"""
from __future__ import annotations

import os
import signal
import subprocess
import time
import unittest
from pathlib import Path

from apoio import BASH, Sandbox

SCRIPT = "sdd/bin/slot.sh"
# O comando falso: o 1º argumento é o exit (ou "sinal"/"dorme"); os outros são os arquivos que o slot repassou.
FALSO = """#!/usr/bin/env bash
rc="$1"; shift
{
  echo "MOMENTO=${SDD_MOMENTO-UNSET}"
  echo "FEATURE=${SDD_FEATURE-UNSET}"
  echo "BASE=${SDD_BASE-UNSET}"
  echo "COMMIT=${SDD_COMMIT-UNSET}"
  echo "ARVORE=${SDD_ARVORE-UNSET}"
  echo "DIR=${SDD_SLOT_DIR-UNSET}"
  [ -d "${SDD_SLOT_DIR-/nao/existe}" ] && echo "DIR_EXISTE=sim"
  echo "PWD=$(pwd -P)"
  for a in "$@"; do echo "ARG=$a"; done
} > registro.txt
echo "saida do comando falso"
case "$rc" in
  sinal) kill -TERM $$ ;;
  dorme) sleep 30 ;;
esac
exit "$rc"
"""


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        self.r = self.repo()
        self.copia("sdd/bin/slot.sh", self.r)
        self.escreve(self.r, "falso.sh", FALSO)
        self.env["TMPDIR"] = str(self.tmp / "tmpdir")
        os.makedirs(self.env["TMPDIR"], exist_ok=True)

    def config(self, texto: str, base: Path | None = None) -> None:
        self.escreve(base or self.r, "sdd/config.yaml", "project:\n  name: x\n  default_branch: main\n" + texto)

    def smoke(self, cmd: str, chave: str = "before_ok_cmd") -> None:
        self.config("smoke:\n  %s: \"%s\"\n" % (chave, cmd))

    def slot(self, *args: str, cwd: Path | None = None) -> tuple[int, str]:
        rc, out, err = self.roda([BASH, str((cwd or self.r) / SCRIPT) if cwd else SCRIPT, *args], cwd or self.r)
        return rc, out + err

    def registro(self, base: Path | None = None) -> dict:
        p = (base or self.r) / "registro.txt"
        if not p.exists():
            return {}
        d: dict = {"ARG": []}
        for linha in p.read_text(encoding="utf-8").splitlines():
            k, _, v = linha.partition("=")
            if k == "ARG":
                d["ARG"].append(v)
            else:
                d[k] = v
        return d


class Contrato(Base):
    """AT-001: 0, 2 e 10 viram OK, REPROVOU e NADA A MEDIR, com a saída do comando repassada."""

    def test_os_tres_exits_do_contrato(self):
        for rc, palavra in ((0, "OK"), (2, "REPROVOU"), (10, "NADA A MEDIR")):
            with self.subTest(rc=rc):
                self.smoke("bash falso.sh %d" % rc)
                got, out = self.slot("smoke.before_ok_cmd")
                self.assertEqual(got, rc, out)
                self.assertIn("RESULTADO: " + palavra + "\n", out)
                self.assertIn("\n→ ", out)
                self.assertIn("saida do comando falso", out)

    def test_schema_recebe_os_arquivos_como_argumentos(self):
        self.config("schema:\n  check_cmd: \"bash falso.sh 0\"\n")
        rc, out = self.slot("schema.check_cmd", "db/a b.sql", "db/c.sql")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["ARG"], ["db/a b.sql", "db/c.sql"])

    def test_sem_arquivos_o_comando_nao_recebe_argumento_extra(self):
        self.smoke("bash falso.sh 0")
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["ARG"], [])


class Inconclusivo(Base):
    """AT-002: exit fora de {0, 2, 10}, sinal no comando ou no próprio slot.sh ⇒ 3, nunca 0."""

    def test_saida_fora_do_contrato_e_inconclusivo(self):
        for cmd, real in (("bash falso.sh 1", "1"), ("bash falso.sh 7", "7"), ("comando_que_nao_existe_xyz", "127")):
            with self.subTest(cmd=cmd):
                self.smoke(cmd)
                rc, out = self.slot("smoke.before_ok_cmd")
                self.assertEqual(rc, 3, out)
                self.assertIn("RESULTADO: INCONCLUSIVO", out)
                self.assertIn("saiu " + real, out)

    def test_comando_morto_por_sinal_e_inconclusivo(self):
        self.smoke("bash falso.sh sinal")
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 3, out)
        self.assertIn("sinal 15", out)
        self.assertIn("RESULTADO: INCONCLUSIVO", out)

    def test_term_no_proprio_slot_e_inconclusivo(self):
        self.smoke("bash falso.sh dorme")
        p = subprocess.Popen([BASH, SCRIPT, "smoke.before_ok_cmd"], cwd=str(self.r), env=self.env,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                             start_new_session=True)
        try:
            fim = time.time() + 20
            while not (self.r / "registro.txt").exists() and time.time() < fim:
                time.sleep(0.05)
            os.killpg(p.pid, signal.SIGTERM)
            out, _ = p.communicate(timeout=20)
        finally:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
        texto = out.decode("utf-8", "replace")
        self.assertEqual(p.returncode, 3, texto)
        self.assertIn("RESULTADO: INCONCLUSIVO", texto)


class Pulado(Base):
    """AT-003: slot vazio, ausente ou sem config ⇒ 11 e nada roda."""

    def test_vazio_ausente_e_sem_config_sao_pulados(self):
        casos = {
            "vazio": 'smoke:\n  before_ok_cmd: ""\n',
            "chave ausente": 'smoke:\n  before_push_cmd: "bash falso.sh 0"\n',
            "secao ausente": 'schema:\n  check_cmd: "bash falso.sh 0"\n',
            "aspas simples vazias": "smoke:\n  before_ok_cmd: ''\n",
            "vazio com comentario do yaml": 'smoke:\n  before_ok_cmd: ""  # preencher depois\n',
        }
        for nome, texto in casos.items():
            with self.subTest(caso=nome):
                self.config(texto)
                rc, out = self.slot("smoke.before_ok_cmd")
                self.assertEqual(rc, 11, out)
                self.assertIn("smoke.before_ok_cmd vazio: pulado", out)
                self.assertIn("RESULTADO: PULADO", out)
                self.assertFalse((self.r / "registro.txt").exists())
        (self.r / "sdd/config.yaml").unlink()
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 11, out)
        self.assertIn("RESULTADO: PULADO", out)

    def test_comentario_na_coluna_0_nao_fecha_a_secao(self):
        self.config('schema:\n# a checagem do projeto\n  check_cmd: "bash falso.sh 0"\n')
        rc, out = self.slot("schema.check_cmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["MOMENTO"], "schema_check")

    def test_valor_com_aspas_e_escape(self):
        self.config('smoke:\n  before_ok_cmd: "bash falso.sh 0 \\"um dois\\""  # comentario do yaml\n')
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["ARG"], ["um dois"])


class Uso(Base):
    """AT-004: chamada ou config errado ⇒ 64 com causa e conserto, sem rodar comando."""

    def test_chamada_errada_e_64(self):
        self.smoke("bash falso.sh 0")
        for args in (["smoke.foo_cmd"], ["release.landmines_cmd"], [], ["smoke.before_ok_cmd", "--feature"],
                     ["smoke.before_ok_cmd", "--xyz", "1"], ["smoke.before_ok_cmd", "--commit", "nao-existe-abc"],
                     ["smoke.before_ok_cmd", "--feature", "--arvore", "/tmp"],  # avaliação ciclo 1, achado 1
                     ["smoke.before_ok_cmd", "--arvore", "--feature", "F1"],
                     ["smoke.before_ok_cmd", "--feature", "", "--base", "main"],
                     ["smoke.before_ok_cmd", "--base", "nao-existe-abc"]):
            with self.subTest(args=args):
                rc, out = self.slot(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)
                self.assertFalse((self.r / "registro.txt").exists())

    def test_config_que_nao_da_para_rodar_e_64(self):
        # caso → (config, a causa que a mensagem tem de dizer: o AT-004 pede a causa certa, não só o exit)
        casos = {
            "aspas yaml sem fechar": ('smoke:\n  before_ok_cmd: "bash falso.sh 0\n', "abre aspas e não fecha"),
            "comeca com pipe": ('smoke:\n  before_ok_cmd: "| cat"\n', "erro de sintaxe"),
            "aspa do shell sem fechar": ("smoke:\n  before_ok_cmd: \"bash falso.sh 0 'abc\"\n", "erro de sintaxe"),
            "comentario do shell": ('smoke:\n  before_ok_cmd: "bash falso.sh 0 # gate"\n', "comentário (#)"),
            # ciclo 2, achado 2
            "texto depois das aspas": ('smoke:\n  before_ok_cmd: "bash falso.sh 0" --url x\n', "texto depois das aspas"),
            "texto depois das aspas simples": ("smoke:\n  before_ok_cmd: 'bash falso.sh 0' x\n", "texto depois das aspas"),
            # revisão rodada 2, R1: com um separador no fim, o exit seria o do "$@" vazio (0), não o do comando
            "termina em ponto e virgula": ('smoke:\n  before_ok_cmd: "bash falso.sh 2;"\n', "separador"),
            "termina em e comercial": ('smoke:\n  before_ok_cmd: "bash falso.sh 2 &"\n', "separador"),
            "termina em pipe": ('smoke:\n  before_ok_cmd: "bash falso.sh 2 |"\n', "separador"),
            "termina em e logico": ('smoke:\n  before_ok_cmd: "bash falso.sh 2 &&"\n', "separador"),
        }
        for nome, (texto, causa) in casos.items():
            with self.subTest(caso=nome):
                self.config(texto)
                rc, out = self.slot("smoke.before_ok_cmd")
                self.assertEqual(rc, 64, out)
                self.assertIn(causa, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)
                self.assertFalse((self.r / "registro.txt").exists())


class Cerquilha(Base):
    """AT-001 × AT-004 (avaliação ciclo 1, achado 2): # só é comentário no início de uma palavra, fora de aspas."""

    def test_cerquilha_no_meio_da_palavra_roda(self):
        for arg in ("https://app.example.com/#/pedidos", "a#b"):
            with self.subTest(arg=arg):
                self.smoke("bash falso.sh 0 %s" % arg)
                rc, out = self.slot("smoke.before_ok_cmd")
                self.assertEqual(rc, 0, out)
                self.assertEqual(self.registro()["ARG"], [arg])

    def test_cerquilha_entre_aspas_roda(self):
        self.config("smoke:\n  before_ok_cmd: \"bash falso.sh 0 'x # y'\"\n")
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["ARG"], ["x # y"])

    def test_bordas_do_bash(self):
        # avaliação ciclo 2, achado 1: quem decide o que é comentário é o próprio bash
        self.config("smoke:\n  before_ok_cmd: 'bash falso.sh 0 a\\ #b'\n")
        rc, out = self.slot("smoke.before_ok_cmd", "f1.txt")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["ARG"], ["a #b", "f1.txt"])
        (self.r / "registro.txt").unlink()
        self.config("smoke:\n  before_ok_cmd: \"bash falso.sh 0 $'it\\\\'s' # c\"\n")
        rc, out = self.slot("smoke.before_ok_cmd", "f1.txt")
        self.assertEqual(rc, 64, out)
        self.assertFalse((self.r / "registro.txt").exists())

    def test_redirecao_no_fim_roda(self):
        # revisão rodada 3, R1@claude: o declare -f põe a redireção depois do "$@"; 2>&1, > e < são comandos válidos
        for redir in ("2>&1", "> saida.txt", "< /dev/null"):
            with self.subTest(redir=redir):
                self.smoke("bash falso.sh 0 %s" % redir)
                rc, out = self.slot("smoke.before_ok_cmd", "a.sql")
                self.assertEqual(rc, 0, out)
                self.assertEqual(self.registro()["ARG"], ["a.sql"])

    def test_ajuda_mostra_so_o_cabecalho(self):
        # revisão rodada 3, R1@glm: o -h não imprime código
        rc, out = self.slot("--help")
        self.assertEqual(rc, 64, out)
        self.assertIn("Exit: 0 OK", out)
        self.assertNotIn("set -uo pipefail", out)

    def test_comando_nao_escapa_da_checagem(self):
        # o bash -n vem antes da checagem de comentário (que define uma função com o comando): um comando que
        # fecha a chave da função não pode rodar nada durante a checagem, e sai 64 com a causa certa
        self.smoke("true; }; touch escapou.txt; __x() { :")
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 64, out)
        self.assertIn("erro de sintaxe", out)
        self.assertFalse((self.r / "escapou.txt").exists())

    def test_cerquilha_depois_de_ponto_e_virgula_e_comentario(self):
        self.smoke("bash falso.sh 0;# resto")
        rc, out = self.slot("smoke.before_ok_cmd")
        self.assertEqual(rc, 64, out)
        self.assertFalse((self.r / "registro.txt").exists())


class Ambiente(Base):
    """AT-005: as 6 variáveis SDD_* e a pasta comum aos 3 momentos."""

    def setUp(self):
        super().setUp()
        self.git(self.r, "checkout", "-q", "-b", "main")
        self.smoke("bash falso.sh 0")
        self.config('smoke:\n  before_ok_cmd: "bash falso.sh 0"\n  before_push_cmd: "bash falso.sh 0"\n'
                    '  after_deploy_cmd: "bash falso.sh 0"\nschema:\n  check_cmd: "bash falso.sh 0"\n')
        self.commit(self.r, "base")
        self.sha = self.git(self.r, "rev-parse", "HEAD").strip()

    def test_variaveis_do_momento(self):
        for chave, momento in (("smoke.before_ok_cmd", "before_ok"), ("smoke.before_push_cmd", "before_push"),
                               ("smoke.after_deploy_cmd", "after_deploy"), ("schema.check_cmd", "schema_check")):
            with self.subTest(chave=chave):
                rc, out = self.slot(chave, "--feature", "LOJA_CUPOM", "--base", "main", "--commit", "HEAD",
                                    "--arvore", str(self.tmp))
                self.assertEqual(rc, 0, out)
                reg = self.registro()
                self.assertEqual(reg["MOMENTO"], momento)
                self.assertEqual(reg["FEATURE"], "LOJA_CUPOM")
                self.assertEqual(reg["BASE"], self.sha)
                self.assertEqual(reg["COMMIT"], self.sha)
                self.assertEqual(reg["ARVORE"], str(self.tmp))
                self.assertEqual(reg.get("DIR_EXISTE"), "sim")
                self.assertTrue(reg["DIR"].startswith(self.env["TMPDIR"]), reg["DIR"])
                self.assertTrue(reg["DIR"].endswith("/LOJA_CUPOM"), reg["DIR"])
                self.assertEqual(reg["PWD"], str(self.r))

    def test_padroes_sem_flags(self):
        rc, out = self.slot("smoke.before_push_cmd")
        self.assertEqual(rc, 0, out)
        reg = self.registro()
        self.assertEqual(reg["FEATURE"], "")
        self.assertEqual(reg["BASE"], "")  # origin/main não existe neste repositório
        self.assertIn("SDD_BASE vazio", out)
        self.assertEqual(reg["COMMIT"], self.sha)
        self.assertEqual(reg["ARVORE"], str(self.r))
        self.assertTrue(reg["DIR"].endswith("/_sem-feature"), reg["DIR"])

    def test_mesma_pasta_de_outra_worktree_subpasta_e_symlink(self):
        rc, _ = self.slot("smoke.before_ok_cmd", "--feature", "F")
        self.assertEqual(rc, 0)
        pasta = self.registro()["DIR"]
        wt = self.tmp / "wt"
        self.git(self.r, "worktree", "add", "-q", str(wt), "-b", "outra")
        rc, out = self.slot("smoke.after_deploy_cmd", "--feature", "F", cwd=wt)
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro(wt)["DIR"], pasta)
        (self.r / "sub").mkdir()
        rc, out, err = self.roda([BASH, str(self.r / SCRIPT), "smoke.before_push_cmd", "--feature", "F"], self.r / "sub")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.registro()["DIR"], pasta)
        link = self.tmp / "atalho"
        link.symlink_to(self.r)
        rc, out, err = self.roda([BASH, SCRIPT, "smoke.before_push_cmd", "--feature", "F"], link)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.registro()["DIR"], pasta)

    def test_before_ok_esvazia_so_a_pasta_padrao(self):
        rc, _ = self.slot("smoke.before_ok_cmd", "--feature", "F")
        pasta = Path(self.registro()["DIR"])
        (pasta / "velho.txt").write_text("da release anterior", encoding="utf-8")
        rc, out = self.slot("smoke.before_push_cmd", "--feature", "F")
        self.assertEqual(rc, 0, out)
        self.assertTrue((pasta / "velho.txt").exists())
        rc, out = self.slot("smoke.before_ok_cmd", "--feature", "F")
        self.assertEqual(rc, 0, out)
        self.assertFalse((pasta / "velho.txt").exists())
        propria = self.tmp / "propria"
        propria.mkdir()
        (propria / "meu.txt").write_text("nao apagar", encoding="utf-8")
        rc, out = self.slot("smoke.before_ok_cmd", "--dir", str(propria))
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.registro()["DIR"], str(propria))
        self.assertTrue((propria / "meu.txt").exists())

    def test_before_ok_vazio_tambem_esvazia(self):
        # revisão claude, R2: com o slot de before_ok vazio, o que a release anterior deixou não pode ficar
        rc, _ = self.slot("smoke.before_ok_cmd", "--feature", "F")
        pasta = Path(self.registro()["DIR"])
        (pasta / "velho.txt").write_text("da release anterior", encoding="utf-8")
        self.config('smoke:\n  before_ok_cmd: ""\n  after_deploy_cmd: "bash falso.sh 0"\n')
        rc, out = self.slot("smoke.before_ok_cmd", "--feature", "F")
        self.assertEqual(rc, 11, out)
        self.assertFalse((pasta / "velho.txt").exists())

    def test_caminhos_relativos_valem_de_onde_foi_chamado(self):
        # revisão rodada 2, R2: o script vai para a raiz, mas arquivo, --arvore e --dir relativos são de quem chamou
        sub = self.r / "db"
        self.escreve(sub, "a b.sql", "select 1;\n")
        rc, out, err = self.roda([BASH, str(self.r / SCRIPT), "schema.check_cmd", "--arvore", "wt", "--dir", "comum",
                                  "a b.sql", "nao-existe.sql"], sub)
        self.assertEqual(rc, 0, out + err)
        reg = self.registro()
        self.assertEqual(reg["ARG"], ["db/a b.sql", "nao-existe.sql"])
        self.assertEqual(reg["ARVORE"], str(sub / "wt"))
        self.assertEqual(reg["DIR"], str(sub / "comum"))

    def test_sem_git_funciona_com_commit_vazio(self):
        solto = self.tmp / "solto"
        solto.mkdir()
        self.copia("sdd/bin/slot.sh", solto)
        self.escreve(solto, "falso.sh", FALSO)
        self.config('smoke:\n  before_ok_cmd: "bash falso.sh 0"\n', base=solto)
        rc, out, err = self.roda([BASH, SCRIPT, "smoke.before_ok_cmd", "--feature", "F"], solto)
        self.assertEqual(rc, 0, out + err)
        reg = self.registro(solto)
        self.assertEqual(reg["COMMIT"], "")
        self.assertIn("SDD_COMMIT vazio", out + err)
        self.assertEqual(reg.get("DIR_EXISTE"), "sim")


if __name__ == "__main__":
    unittest.main()
