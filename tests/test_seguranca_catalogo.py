"""Contrato do catálogo da sdd-seguranca (F18/F20, AT-008).

O catálogo é a fonte única: a gramática é conferida pelo próprio leitor (sdd/bin/seguranca-varredura.sh, LM-005:
um parser só); aqui ficam o conteúdo (22 itens, quem bloqueia, quem vai para o AGENTS.md), a cobertura de cada
padrão por um caso que acusa e um que não acusa, e a regra de não citar o material de origem.
"""
from __future__ import annotations

import os
import re
import unittest

from apoio import BASH, RAIZ, Sandbox

SCRIPT = RAIZ / "sdd/bin/seguranca-varredura.sh"
CATALOGO = RAIZ / ".agents/skills/sdd-seguranca/references/CATALOGO_SEGURANCA.md"
TESTE_VARREDURA = RAIZ / "tests/test_seguranca_varredura.py"


def fichas() -> dict:
    texto = CATALOGO.read_text(encoding="utf-8").split("\n## Itens\n", 1)[1]
    saida = {}
    for bloco in re.split(r"(?m)^### ", texto)[1:]:
        cab, *linhas = bloco.strip().splitlines()
        sid, falha = cab.split(" — ", 1)
        campos = dict(re.match(r"^- ([a-z]+): (.*)$", ln).groups() for ln in linhas if ln.startswith("- "))
        saida[sid] = dict(campos, falha=falha)
    return saida


class Catalogo(Sandbox):
    def test_o_leitor_aceita_o_catalogo_do_pacote(self):
        p = self.repo()
        rc, out, err = self.roda([BASH, SCRIPT, "--catalogo", CATALOGO, "--stack"], p)
        self.assertEqual(rc, 0, out + err)

    def test_22_itens_em_sequencia_com_os_13_campos(self):
        f = fichas()
        self.assertEqual(list(f), ["S%02d" % k for k in range(1, 23)])
        for sid, c in f.items():
            with self.subTest(item=sid):
                self.assertEqual(len(c), 14, c)   # 13 campos + o nome da falha

    def test_so_s01_e_s11_bloqueiam(self):
        self.assertEqual(sorted(s for s, c in fichas().items() if c["bloqueia"] == "sim"), ["S01", "S11"])

    def test_os_5_de_maior_risco_vao_para_o_agents(self):
        f = fichas()
        self.assertEqual(sorted(s for s, c in f.items() if c["agents"] == "sim"), ["S01", "S07", "S08", "S11", "S13"])
        self.assertTrue(all(f[s]["gravidade"] in ("alta", "media") for s in ("S01", "S07", "S08", "S11", "S13")))

    def test_bancada_fora_do_app(self):
        self.assertEqual(sorted(s for s, c in fichas().items() if c["fase"] == "bancada"), ["S21", "S22"])

    def test_todo_padrao_tem_caso_que_acusa_e_caso_que_nao_acusa(self):
        texto = TESTE_VARREDURA.read_text(encoding="utf-8")
        casos = re.search(r"    CASOS = \{(.*?)\n    \}", texto, re.S).group(1)
        pares = re.search(r"    PARES = \{(.*?)\n    \}", texto, re.S).group(1)
        for sid, c in fichas().items():
            if c["padrao"] == "só à mão":
                continue
            with self.subTest(item=sid):
                if sid == "S11":
                    self.assertIn("def test_segredo_novo_bloqueia_com_arquivo_e_linha", texto)
                    self.assertIn("def test_leitura_pelo_nome_nao_e_segredo", texto)
                elif sid == "S01":
                    self.assertIn("def test_tabela_nova_sem_rls_bloqueia", texto)
                    self.assertIn("def test_rls_em_outra_migracao_libera", texto)
                else:
                    self.assertIn('"%s":' % sid, casos)
                    self.assertIn('"%s":' % sid, pares)

    def test_toda_referencia_e_publica(self):
        for sid, c in fichas().items():
            with self.subTest(item=sid):
                self.assertRegex(c["ref"], r"^(OWASP [A-Z0-9:]+|CWE-\d+)( · (OWASP [A-Z0-9:]+|CWE-\d+))*$")

    def test_at_em_ears_com_palavra_chave(self):
        for sid, c in fichas().items():
            with self.subTest(item=sid):
                self.assertRegex(c["at"], r"^(If|When|While|Where)\b")
                self.assertIn("shall", c["at"])


class SemMaterialDeOrigem(unittest.TestCase):
    """Decisão do brainstorm: o pacote não cita o material de origem (termos montados aqui, para este arquivo não citar)."""

    PROIBIDOS = re.compile("|".join(["porta " + "aberta", "e-" + "book", "e" + "book", "construir " + "com ia"]), re.I)
    FORA = ("sdd/features/", "sdd/reports/", "sdd/reviews/", "sdd/traces/", "sdd/releases/", "sdd/contexto/", ".git/")
    DESTA_FRENTE = (".agents/skills/sdd-seguranca/", "sdd/bin/seguranca-varredura.sh", "docs/security.md",
                    "docs/pt-BR/security.md")

    def arquivos(self):
        for raiz, pastas, nomes in os.walk(RAIZ):
            rel_raiz = os.path.relpath(raiz, RAIZ).replace(os.sep, "/")
            rel_raiz = "" if rel_raiz == "." else rel_raiz + "/"
            pastas[:] = [p for p in pastas if not (rel_raiz + p + "/").startswith(self.FORA) and p != "__pycache__"]
            for n in nomes:
                yield rel_raiz + n

    def test_nenhum_arquivo_cita_o_material_de_origem(self):
        achados = []
        for rel in self.arquivos():
            try:
                texto = (RAIZ / rel).read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if self.PROIBIDOS.search(texto):
                achados.append(rel)
        self.assertEqual(achados, [])

    def test_os_arquivos_da_frente_nao_citam_a_rdd_alem_da_assinatura(self):
        for rel in self.arquivos():
            if not rel.startswith(self.DESTA_FRENTE):
                continue
            texto = (RAIZ / rel).read_text(encoding="utf-8").replace("SDD Open by RDD", "")
            with self.subTest(arquivo=rel):
                self.assertNotRegex(texto, r"RDD10|\bRDD\b")


if __name__ == "__main__":
    unittest.main()
