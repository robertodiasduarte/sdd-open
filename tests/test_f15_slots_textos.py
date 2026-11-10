"""F15_SLOTS: o texto das skills, do config, dos docs e dos contratos que ligam o sdd/bin/slot.sh e o
test-baseline.sh --touched ao fluxo (AT-008 a AT-011 do DEFINE_F15_SLOTS). O comportamento dos scripts é
provado em tests/test_slot.py e tests/test_test_baseline.py; aqui se confere que cada passo chama o script
certo, no momento certo, e diz o que fazer com cada exit.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ

SKILLS = RAIZ / ".agents/skills"
RELEASE = SKILLS / "sdd-release/SKILL.md"
COMO_FALAR = SKILLS / "sdd-release/references/como-falar.md"
BUILD = SKILLS / "sdd-build/SKILL.md"
MIGRATION = SKILLS / "sdd-build/references/aplicar-migration.md"


def ler(p) -> str:
    return (p if hasattr(p, "read_text") else RAIZ / p).read_text(encoding="utf-8")


def entre(texto: str, inicio: str, fim: str) -> str:
    assert inicio in texto, inicio
    resto = texto.split(inicio, 1)[1]
    assert fim in resto, fim
    return resto.split(fim, 1)[0]


VERIFICACOES_TESTES = "testes do diff <ok | ok, N fora do diff | inconclusivo — WAIVABLE | pulado — test_cmd vazio>"
VERIFICACOES_SMOKE = ("smoke <ok | reprovou — FAIL-candidato | nada a medir | pulado — slot vazio | inconclusivo | "
                      "erro de configuração>")


class Release(unittest.TestCase):
    """AT-008 e AT-009."""

    @classmethod
    def setUpClass(cls):
        cls.txt = ler(RELEASE)
        cls.fase0a = entre(cls.txt, "**0a. Determinístico**", "**0b.")
        cls.fase1 = entre(cls.txt, "## FASE 1", "## FASE 2")
        cls.fase2 = entre(cls.txt, "## FASE 2", "## FASE 3")

    def test_versao(self):
        self.assertIn('version: "2.9.0"', self.txt)
        self.assertIn("`sdd-release v2.9.0 · nov/2026", self.txt)

    def test_slots_listados(self):
        slots = entre(self.txt, "## Slots do config", "## FASE 0")
        for chave in ("smoke.before_ok_cmd", "smoke.before_push_cmd", "smoke.after_deploy_cmd"):
            self.assertIn(chave, slots)
        self.assertIn("bash sdd/bin/slot.sh", slots)
        self.assertIn("11", slots)

    def test_0a_roda_os_testes_do_diff_depois_do_verify_gate(self):
        item = entre(self.fase0a, "9. **Testes do diff:**", "Se 0a abortou")
        self.assertIn("bash sdd/bin/test-baseline.sh --touched", item)
        self.assertIn("depois do item 4", item)
        self.assertIn("nunca em paralelo", item)
        for exit_, acao in (("`2`", "abortar"), ("`3`", "WAIVABLE"), ("PULADO", "pulado")):
            self.assertIn(exit_, item)
            self.assertIn(acao, item)
        self.assertIn("fora do diff", item)

    def test_0b_usa_o_resultado_dos_testes_do_diff(self):
        b = entre(self.txt, "**0b. Raio de impacto", "**0c.")
        self.assertIn("item 9 da 0a", b)
        self.assertNotIn("Teste ao lado do módulo tocado ficou vermelho?", b)

    def test_6b_smoke_antes_do_ok_sobre_o_worktree_landado(self):
        item = entre(self.fase1, "6b. **Smoke antes do OK", "7. **PARAR e mostrar")
        self.assertIn("bash sdd/bin/slot.sh smoke.before_ok_cmd", item)
        for flag in ("--feature {F}", "--base origin/{default_branch}", "--commit <SHA landado", "--arvore <worktree temporário"):
            self.assertIn(flag, item)
        for exit_, acao in (("`2`", "FAIL-candidato"), ("`3`", "aviso"), ("`64`", "erro de configuração"),
                            ("`10`", "nada a medir"), ("`11`", "pulado")):
            self.assertIn(exit_, item)
            self.assertIn(acao, item)

    def test_7b_smoke_antes_do_push_nunca_segura(self):
        item = entre(self.fase2, "7b. **Smoke antes do push", "8. **Push.**")
        self.assertIn("bash sdd/bin/slot.sh smoke.before_push_cmd", item)
        self.assertIn("nunca segura o push", item)

    def test_10_smoke_depois_do_deploy_confirmado(self):
        item = entre(self.fase2, "10. **Verificar", "11. **Changelog")
        smoke = entre(item, "**Smoke depois do deploy", "Verde não prova teste")
        self.assertIn("GIT_TERMINAL_PROMPT=0 git fetch", smoke)
        self.assertIn("bash sdd/bin/slot.sh smoke.after_deploy_cmd", smoke)
        self.assertIn("--commit <SHA publicado>", smoke)
        self.assertLess(smoke.index("git fetch"), smoke.index("slot.sh smoke.after_deploy_cmd"))
        self.assertIn("[D1 · não se desfaz]", smoke)
        for opcao in ("**reverter**", "**corrigir**", "**seguir com motivo**", "**não sei**"):
            self.assertIn(opcao, smoke)
        self.assertIn("nunca ✅", smoke)
        self.assertIn("não roda", smoke)
        self.assertIn("deploy.cmd", smoke)

    def test_abortar_lista_os_testes_do_diff(self):
        gates = entre(self.txt, "## Gates de ABORTAR", "## Quando pular")
        self.assertIn("testes do diff com falha nova", gates)

    def test_linha_verificacoes_do_bloco_do_ok(self):
        bloco = entre(entre(self.txt, "7. **PARAR e mostrar (o 1 OK)", "## FASE 2"), "```markdown", "```")
        self.assertEqual(bloco.count("**Verificações:**"), 1, bloco)
        verif = " ".join(entre(bloco, "**Verificações:**", "**Veredito:**").split())
        self.assertIn(VERIFICACOES_TESTES, verif)
        self.assertIn(VERIFICACOES_SMOKE, verif)

    def test_exemplo_do_como_falar_acompanha(self):
        cf = ler(COMO_FALAR)
        self.assertEqual(cf.count("**Verificações:**"), 1, "o exemplo do bloco do OK sumiu ou duplicou")
        verif = " ".join(entre(cf, "**Verificações:**", "**Veredito:**").split())
        self.assertIn("testes do diff", verif)
        self.assertIn("smoke", verif)
        self.assertIn("smoke.after_deploy_cmd", cf)
        self.assertIn("[D1 · não se desfaz]", cf)


class Build(unittest.TestCase):
    """AT-010."""

    def test_versao_e_4b(self):
        txt = ler(BUILD)
        self.assertIn('version: "2.7.0"', txt)
        self.assertIn("`sdd-build v2.7.0 · nov/2026", txt)
        passo = entre(txt, "### 4b. Migration", "### 5.")
        self.assertIn("schema.check_cmd", passo)

    def test_aplicar_migration_checa_antes_da_previa(self):
        txt = ler(MIGRATION)
        self.assertLess(txt.index("## 2. Já está aplicada?"), txt.index("## 2b. Checagem do SQL"))
        self.assertLess(txt.index("## 2b. Checagem do SQL"), txt.index("## 3. Prévia"))
        sec = entre(txt, "## 2b. Checagem do SQL", "## 3. Prévia")
        self.assertIn("bash sdd/bin/slot.sh schema.check_cmd --feature {F}", sec)
        self.assertIn('echo "[exit=$?]"', sec)
        self.assertIn("SCHEMA-CHECK.log", sec)
        self.assertNotIn("| tee", sec)
        self.assertIn("pulada: slot vazio", sec)
        self.assertIn("nada a conferir", sec)
        for exit_ in ("`0`", "`2`", "`3`", "`10`", "`11`", "`64`"):
            self.assertIn(exit_, sec)
        self.assertIn("não aplica", sec)
        self.assertIn("da ferramenta ou do config", sec)
        self.assertIn("SCHEMA-CHECK-2.log", sec)
        bloco = entre(txt, "## 4. A confirmação", "## 5. Aplicar")
        self.assertIn("**Checagem:**", bloco)


class ConfigEDocs(unittest.TestCase):
    """AT-011."""

    def test_config_tem_os_4_slots_vazios(self):
        cfg = ler("sdd/config.example.yaml")
        smoke = re.search(r"(?ms)^smoke:\n(.*?)^\S", cfg)
        schema = re.search(r"(?ms)^schema:\n(.*?)(?:^\S|\Z)", cfg)
        self.assertIsNotNone(smoke, "seção smoke: ausente")
        self.assertIsNotNone(schema, "seção schema: ausente")
        for chave in ("before_ok_cmd", "before_push_cmd", "after_deploy_cmd"):
            self.assertRegex(smoke.group(1), r'(?m)^  %s: ""$' % chave)
        self.assertRegex(schema.group(1), r'(?m)^  check_cmd: ""$')
        for termo in ("0 ok", "2 reprovou", "10 nada a", "SDD_SLOT_DIR", "SDD_ARVORE", "slot.sh"):
            self.assertIn(termo, cfg)

    def test_guias_de_adaptacao(self):
        for rel in ("docs/adaptation-guide.md", "docs/pt-BR/adaptation-guide.md"):
            with self.subTest(rel=rel):
                txt = ler(rel)
                for chave in ("smoke.before_ok_cmd", "smoke.before_push_cmd", "smoke.after_deploy_cmd",
                              "schema.check_cmd", "sdd/bin/slot.sh", "SDD_COMMIT", "SDD_ARVORE"):
                    self.assertIn(chave, txt)

    def test_cli_conventions(self):
        txt = ler("docs/cli-conventions.md")
        linha = [l for l in txt.splitlines() if l.startswith("| `slot.sh` |")]
        self.assertEqual(len(linha), 1)
        for cod in ("`0` OK", "`2` REPROVOU", "`3` INCONCLUSIVO", "`10` NADA A MEDIR", "`11` PULADO", "`64`"):
            self.assertIn(cod, linha[0])

    def test_contrato_de_maquina(self):
        txt = ler("sdd/WORKFLOW_CONTRACTS.yaml")
        bloco = entre(txt, "\nslot:\n", "\n\n")
        self.assertIn("`sdd/bin/slot.sh`", bloco)
        for chave in ("smoke.before_ok_cmd", "smoke.before_push_cmd", "smoke.after_deploy_cmd", "schema.check_cmd"):
            self.assertIn(chave, bloco)
        for k, v in (("ok", "0"), ("reprovou", "2"), ("inconclusivo", "3"), ("nada_a_medir", "10"),
                     ("pulado", "11"), ("uso", "64")):
            self.assertIn('%s: "%s"' % (k, v), bloco)

    def test_manifest(self):
        manifest = ler("MANIFEST.txt").splitlines()
        for rel in ("sdd/bin/slot.sh", "tests/test_slot.py", "tests/test_f15_slots_textos.py"):
            self.assertIn(rel, manifest)


class SemProjetoPrivado(unittest.TestCase):
    """AT-011: os arquivos do produto que a F15_SLOTS cria ou altera não citam projeto privado. A lista é fixa
    porque o gate roda numa cópia sem .git (não há diff para calcular); este arquivo fica de fora porque contém a
    própria família de termos."""

    ARQUIVOS = ("sdd/bin/slot.sh", "sdd/bin/test-baseline.sh", "sdd/config.example.yaml",
                ".agents/skills/sdd-release/SKILL.md", ".agents/skills/sdd-release/references/como-falar.md",
                ".agents/skills/sdd-build/SKILL.md", ".agents/skills/sdd-build/references/aplicar-migration.md",
                "docs/adaptation-guide.md", "docs/pt-BR/adaptation-guide.md", "docs/cli-conventions.md",
                "sdd/WORKFLOW_CONTRACTS.yaml", "tests/test_slot.py")

    def test_nada_de_projeto_privado(self):
        termo = re.compile(r"supabase|\bdeno\b|wordpress|wp-content|rdd-plataforma|hostinger|rdd/wordpress|rdd-eval|"
                           r"a11y|smoke-release|audita-schema|\bLM-1\d\d\b", re.I)
        for rel in self.ARQUIVOS:
            with self.subTest(rel=rel):
                txt = ler(rel)
                if rel == ".agents/skills/sdd-build/references/aplicar-migration.md":
                    # o protocolo de migration já usa o Supabase como caminho provado (F3); só o texto novo conta
                    txt = entre(txt, "## 2b. Checagem do SQL", "## 3. Prévia")
                achados = termo.findall(txt)
                if rel == "sdd/bin/test-baseline.sh":
                    # o deno é um dos 6 formatos de saída de teste que o script lê desde a F7, não um projeto
                    achados = [a for a in achados if a.lower() != "deno"]
                self.assertEqual(achados, [], rel)


if __name__ == "__main__":
    unittest.main()
