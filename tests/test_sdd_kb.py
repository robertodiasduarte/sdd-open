"""Contrato da sdd-kb no sdd-open: o gate.sh, o --strict novo do validate_kb.py e o texto da skill.

O gate.sh roda igual no pacote e no projeto do aluno: acha o validador e os exemplos pela própria
pasta e monta os casos numa pasta temporária. Estes testes o rodam no pacote, numa cópia que só tem a
pasta da skill, numa cópia com o validador sabotado (o gate tem de ficar vermelho) e na cópia gerada
pelo init em .claude/skills (o gate recusa: lá os arquivos ganham cabeçalho e o exemplo não vale).
O --strict é conferido dos dois lados direto no validador. Exit do validador: 0 · 2 · 64.
"""
from __future__ import annotations

import re
import shutil
import unittest

from apoio import BASH, PYTHON, RAIZ, Sandbox

SKILL = RAIZ / ".agents/skills/sdd-kb"
GATE = SKILL / "scripts/gate.sh"
VALIDATOR = SKILL / "scripts/validate_kb.py"
RULEMAP = SKILL / "scripts/kb_normativo.py"
EXEMPLO_NORM = SKILL / "assets/example-kb-normativo"
VERDE = "RESULTADO: VERDE — 4 aceitas, 12 rejeitadas pelo motivo certo, RULE_MAP do exemplo em dia"
REVISOR_PENDENTE = "PENDENTE DE REVISÃO (exemplo didático da skill — conferir na NT antes de qualquer uso)"
REGRA = "rules/UB12-10-CRT3.md"


class Gate(Sandbox):
    def gate(self, script, cwd=None):
        env = dict(self.env, PYTHON=PYTHON)
        return self.roda([BASH, script], cwd or self.tmp, env)

    def copia_da_skill(self):
        destino = self.tmp / "aluno/.agents/skills/sdd-kb"
        shutil.copytree(SKILL, destino)
        return destino

    def test_no_pacote_fica_verde_em_uma_linha(self):
        rc, out, err = self.gate(GATE)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(out.strip().splitlines(), [VERDE], out + err)

    def test_numa_copia_so_da_skill_fica_verde(self):
        copia = self.copia_da_skill()
        rc, out, err = self.gate(copia / "scripts/gate.sh", copia.parent)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(VERDE, out)

    def test_validador_sabotado_deixa_o_gate_vermelho(self):
        copia = self.copia_da_skill()
        v = copia / "scripts/validate_kb.py"
        texto = v.read_text(encoding="utf-8")
        self.assertIn('"concept": 150', texto)
        v.write_text(texto.replace('"concept": 150', '"concept": 100000', 1), encoding="utf-8")
        rc, out, err = self.gate(copia / "scripts/gate.sh")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("🛑 limite-conceito: caso ruim ACEITO", out)
        self.assertIn("RESULTADO: VERMELHO", out)
        self.assertRegex(out, r"(?m)^→ ")

    def test_ancora_ausente_e_vermelho_com_a_moldura(self):
        copia = self.copia_da_skill()
        c = copia / "assets/example-kb/concepts/regime-de-competencia.md"
        texto = c.read_text(encoding="utf-8")
        self.assertIn("prática consolidada do escritório", texto)
        c.write_text(texto.replace("prática consolidada do escritório", "prática do escritório", 1),
                     encoding="utf-8")
        rc, out, err = self.gate(copia / "scripts/gate.sh")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("🛑 placeholder: âncora ausente", out)
        self.assertIn("RESULTADO: VERMELHO", out)
        self.assertIn("→ o exemplo mudou; atualize a âncora no gate.sh", out)

    def test_recusa_a_copia_gerada_pelo_init(self):
        p = self.repo("projeto")
        self.escreve(p, "README.md", "# projeto\n")
        self.commit(p, "base")
        rc, out, err = self.roda([BASH, RAIZ / "bin/sdd-open.sh", "init", "--yes", "--vendors", "claude"], p)
        self.assertEqual(rc, 0, out + err)
        gerado = p / ".claude/skills/sdd-kb/scripts/gate.sh"
        self.assertTrue(gerado.is_file())
        rc, out, err = self.gate(gerado, p)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("🛑 cópia gerada pelo sync", out)
        self.assertIn("→ rode bash .agents/skills/sdd-kb/scripts/gate.sh", out)
        rc, out, err = self.gate(p / ".agents/skills/sdd-kb/scripts/gate.sh", p)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(VERDE, out)


class Strict(Sandbox):
    """--strict: regra implementada aponta um teste que existe a partir da raiz do projeto."""

    def setUp(self):
        super().setUp()
        self.raiz = self.tmp / "proj"
        self.kb = self.raiz / "sdd/kb/dom"
        shutil.copytree(EXEMPLO_NORM, self.kb)
        (self.raiz / "sdd/kb/_index.yaml").write_text(
            'version: "1.0"\ndomains:\n  dom:\n    name: t\n    description: t\n    path: dom/\n'
            "    perfil: normativo\n    updated: 2026-10-29\n", encoding="utf-8")
        self.troca("index.md", REVISOR_PENDENTE, "Revisora do Exemplo, registro de teste")

    def troca(self, rel, de, para):
        p = self.kb / rel
        texto = p.read_text(encoding="utf-8")
        self.assertIn(de, texto, rel)
        p.write_text(texto.replace(de, para, 1), encoding="utf-8")

    def valida(self, *extra):
        self.roda([PYTHON, "-B", RULEMAP, "rule-map", self.kb], self.tmp)
        rc, out, err = self.roda([PYTHON, "-B", VALIDATOR, self.kb, *extra], self.tmp)
        return rc, out + err

    def test_revisado_sem_implementacao_passa(self):
        rc, out = self.valida("--strict")
        self.assertEqual(rc, 0, out)

    def test_implementacao_sem_teste_reprova(self):
        self.troca(REGRA, "implementacao: null", "implementacao: src/engine.py:vbc")
        rc, out = self.valida("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("rules/UB12-10-CRT3.md: implementacao 'src/engine.py:vbc' has no teste", out)

    def test_teste_de_arquivo_inexistente_reprova(self):
        self.troca(REGRA, "implementacao: null", "implementacao: src/engine.py:vbc")
        self.troca(REGRA, "teste: null", "teste: tests/test_engine.py::test_vbc")
        rc, out = self.valida("--strict")
        self.assertEqual(rc, 2, out)
        self.assertIn("tests/test_engine.py not found from the project root", out)

    def test_teste_que_existe_passa(self):
        self.troca(REGRA, "implementacao: null", "implementacao: src/engine.py:vbc")
        self.troca(REGRA, "teste: null", "teste: tests/test_engine.py::test_vbc")
        self.escreve(self.raiz, "tests/test_engine.py", "# teste\n")
        rc, out = self.valida("--strict")
        self.assertEqual(rc, 0, out)

    def test_sem_strict_nao_confere_teste(self):
        self.troca(REGRA, "implementacao: null", "implementacao: src/engine.py:vbc")
        rc, out = self.valida()
        self.assertEqual(rc, 0, out)
        self.troca(REGRA, "teste: null", "teste: tests/nao_existe.py")
        rc, out = self.valida()
        self.assertEqual(rc, 0, out)

    def test_uso_errado_e_64(self):
        for args in ([], ["--xyz", str(self.kb)], [str(self.tmp / "nao-existe")]):
            with self.subTest(args=args):
                rc, out, err = self.roda([PYTHON, "-B", VALIDATOR, *args], self.tmp)
                self.assertEqual(rc, 64, out + err)


class RuleMapCheck(Sandbox):
    """rule-map --check: 0 com o RULE_MAP em dia, 2 quando ele derivou de rules/ (sabotagem da F5)."""

    def test_check_dos_dois_lados(self):
        kb = self.tmp / "dom"
        shutil.copytree(EXEMPLO_NORM, kb)
        rc, out, err = self.roda([PYTHON, "-B", RULEMAP, "rule-map", "--check", kb], self.tmp)
        self.assertEqual(rc, 0, out + err)
        self.assertIn("PASS: RULE_MAP.md matches rules/", out)
        regra = kb / REGRA
        texto = regra.read_text(encoding="utf-8")
        self.assertIn("teste: null", texto)
        regra.write_text(texto.replace("teste: null", "teste: tests/test_x.py", 1), encoding="utf-8")
        rc, out, err = self.roda([PYTHON, "-B", RULEMAP, "rule-map", "--check", kb], self.tmp)
        self.assertEqual(rc, 2, out + err)
        self.assertIn("FAIL: RULE_MAP.md differs from rules/", out)
        self.assertIn("python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map", out)


class TextoDaSkill(unittest.TestCase):
    """A skill portada fala do projeto do open: sdd/kb/ e os scripts em .agents/skills/sdd-kb/."""

    PROIBIDO = re.compile(
        r"pasta de bases|\.claude/kb|kb_dir|sdd-starter|\]\((?:assets|scripts)/"
        r"|(?<!\.agents/skills/sdd-kb/)scripts/(?:validate_kb|kb_normativo)\.py")

    def textos(self):
        for f in sorted(SKILL.rglob("*")):
            if not f.is_file() or f.suffix not in (".md", ".py", ".sh", ".yaml", ".json", ".txt"):
                continue
            texto = f.read_text(encoding="utf-8")
            if f.name == "CHANGELOG.md":
                # O histórico abaixo da 2.2.0 descreve a skill como ela era: só a entrada nova conta.
                texto = texto.split("\n## 2.1.0", 1)[0]
            yield f, texto

    def test_cita_sdd_kb_e_os_scripts_do_projeto(self):
        texto = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("sdd/kb/_index.yaml", texto)
        self.assertIn("python3 .agents/skills/sdd-kb/scripts/validate_kb.py", texto)
        self.assertIn("python3 .agents/skills/sdd-kb/scripts/kb_normativo.py", texto)

    def test_nenhum_caminho_de_fora_do_open(self):
        achados = []
        for f, texto in self.textos():
            for n, linha in enumerate(texto.splitlines(), 1):
                m = self.PROIBIDO.search(linha)
                if m:
                    achados.append("%s:%d: %s" % (f.relative_to(RAIZ), n, m.group(0)))
        self.assertEqual(achados, [])

    def test_sem_adaptador_de_outra_plataforma(self):
        self.assertFalse((SKILL / "agents").exists())


if __name__ == "__main__":
    unittest.main()
