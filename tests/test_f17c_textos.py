"""F17c (AT-004 a AT-007, AT-010): o modo web de define, design e build, os moldes do Open e o "não finja".

AT-004 e AT-005 valem para o texto gerado (o que o aluno do starter recebe); AT-006, AT-007 e AT-010, para o Open.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ
from test_gerar_starter import DA_F17C, Base

SKILLS = RAIZ / ".agents/skills"
# comando que o aluno roda: bloco de shell, ou crase/linha começando por bash/python/python3 (LM-026: e também a
# obrigação em prosa, que os testes abaixo conferem pelo nome dos validadores)
COMANDO = re.compile(r"```(?:bash|sh|shell|zsh|powershell)|`(?:bash|python|python3) |^\s*(?:bash|python|python3) ", re.M)
VALIDADORES = ("validate_define", "validate_design", "validate_build_report")
LEITURA = ("**Documento de uma fase anterior** (projeto começado antes desta versão): leia de onde estiver — `sdd/features/`, "
           "`sdd/` ou `.claude/sdd/` —, grave o novo na pasta desta versão e não pergunte onde está.")


def ler(p) -> str:
    return p.read_text(encoding="utf-8")


class ModoWebGerado(Base):
    def setUp(self):
        super().setUp()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)

    def textos(self, skill: str, com_assets: bool = True):
        d = self.starter / "skills" / skill
        for p in sorted(d.rglob("*.md")):
            if com_assets or "assets" not in p.relative_to(d).parts:
                yield p.relative_to(self.starter).as_posix(), ler(p)

    def test_at004_pastas_do_open_e_entrega_no_chat(self):
        onde = {"sdd-define": "`sdd/features/DEFINE_{FEATURE_NAME}.md`", "sdd-design": "`sdd/features/DESIGN_{FEATURE_NAME}.md`",
                "sdd-build": "`sdd/reports/BUILD_REPORT_{FEATURE}.md`"}
        for skill in DA_F17C:
            s = ler(self.starter / "skills" / skill / "SKILL.md")
            with self.subTest(skill=skill):
                self.assertIn(onde[skill], s)
            with self.subTest(leitura=skill):
                self.assertEqual(s.count(LEITURA), 1)   # nota 5 da revisão do DESIGN: projeto começado antes
            for rel, tx in self.textos(skill):
                tx = tx.replace(LEITURA, "")
                with self.subTest(arquivo=rel):
                    self.assertNotIn(".claude/sdd", tx)
                    self.assertNotIn("sem subpastas", tx)
                    self.assertIsNone(re.search(r"(?<![\w/])sdd/(?:DEFINE|DESIGN|BUILD_REPORT|BRAINSTORM)_", tx), rel)
                    self.assertNotIn("sdd.config.yaml", tx)
                    self.assertNotIn("ambiente.md", tx)
                    self.assertNotIn("- banco:", tx)
        for skill in ("sdd-define", "sdd-design"):
            with self.subTest(entrega=skill):
                self.assertIn("dizendo que ele não foi gravado; nunca dê a entender que gravou",
                              ler(self.starter / "skills" / skill / "SKILL.md"))

    def test_at004_handoffs_dos_protocolos_coerentes(self):
        dp = ler(self.starter / "skills/sdd-define/references/define-protocol.md")
        self.assertIn("→ `HANDOFF_TO_DESIGN`", dp)
        self.assertNotIn("HANDOFF_TO_UX_REVIEW", dp)
        self.assertIn("Execute o **SDD Design by RDD**.", ler(self.starter / "skills/sdd-define/SKILL.md"))
        bp = ler(self.starter / "skills/sdd-build/references/build-protocol.md")
        self.assertNotIn("HANDOFF_TO_RELEASE", bp)
        for rel, tx in self.textos("sdd-build"):     # avaliador, ciclo 1, achado 4: nada "validado" sem validador
            with self.subTest(validado=rel):
                self.assertNotIn("validado", tx)
        for rel, tx in self.textos("sdd-build"):     # revisão, rodada 1, R2: nenhum resto do fim na Release
            with self.subTest(arquivo=rel):
                self.assertNotIn("handoff de Release", tx)
        self.assertIn("Execute o **SDD Handoff by RDD**.", ler(self.starter / "skills/sdd-build/SKILL.md"))

    def test_at005_define_e_design_nao_pedem_comando_ao_aluno(self):
        for skill in ("sdd-define", "sdd-design"):
            # o DEFINE de exemplo traz o `cmd` do Verify Gate do projeto dele: é o documento, não um pedido ao aluno
            for rel, tx in self.textos(skill, com_assets=False):
                with self.subTest(arquivo=rel):
                    self.assertIsNone(COMANDO.search(tx), rel)

    def test_at005_nenhuma_das_3_cita_validador(self):
        for skill in DA_F17C:
            for rel, tx in self.textos(skill):
                for v in VALIDADORES:
                    with self.subTest(arquivo=rel, validador=v):
                        self.assertNotIn(v, tx)
                with self.subTest(arquivo=rel):
                    self.assertNotIn("quando executável", tx)    # a obrigação em prosa que citava o lint (LM-026)

    def test_build_sem_o_projeto_recomenda_um_agente_que_grave(self):
        # decisão do Roberto (avaliador, ciclo 2): escrever no chat para o aluno salvar não é o recomendado
        s = ler(self.starter / "skills/sdd-build/SKILL.md")
        for trecho in ("**recomendar** abrir o projeto num agente que grave arquivos no computador do usuário",
                       "Escrever o código no chat para o usuário salvar só se ele pedir; aí nenhuma tarefa é marcada\nfeita",
                       "nem dizer\nque há onde gravar sem ter"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, s)

    def test_at005_build_le_a_saida_do_comando_sem_o_verify_gate_sh(self):
        vg = ler(self.starter / "skills/sdd-build/references/verify-gate.md")
        for trecho in ("`exit 0` (o caso comum) → `0` é green; qualquer outro código é red",
                       "a ferramenta não rodou (comando não encontrado, dependência ausente) → inconclusivo, nunca green"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, vg)
        for rel, tx in self.textos("sdd-build"):
            with self.subTest(arquivo=rel):
                self.assertNotIn("verify-gate.sh", tx)


class UmJeitoSoDePasta(Base):
    """Decisão do Roberto (revisão do DESIGN, nota 4): as 18 geradas guardam os documentos nas pastas do Open."""

    def test_nenhuma_gerada_manda_gravar_lado_a_lado_em_sdd(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for p in sorted((self.starter / "skills").rglob("*")):
            if not p.is_file() or p.name == "CHANGELOG.md" or p.suffix not in (".md", ".py"):
                continue
            tx = p.read_text(encoding="utf-8")
            with self.subTest(arquivo=str(p.relative_to(self.starter))):
                self.assertNotIn("sem subpastas", tx)
                self.assertNotIn("Sem ele, gravar em `sdd/` na raiz", tx)
                self.assertNotIn("Se o projeto já tiver `.claude/sdd/`, continue nela", tx)
        filha = (self.starter / "skills/ux-review-builder/assets/UX_REVIEW_SKILL_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("`DEFINE_{FEATURE}.md`, em `sdd/features/`", filha)
        self.assertIn("Gravar `UX_REVIEW_{FEATURE}.md` em `sdd/reviews/`", filha)


class ValidadorDaBuilder(unittest.TestCase):
    """Decision 9: o validador da ux-review-builder aceita só sdd/features/ e sdd/reviews/; os testes dela rodam aqui
    (a suíte do Open não desce nos tests/ das skills; o CI do starter desce)."""

    def test_os_testes_da_builder_passam(self):
        import subprocess, sys
        r = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s",
                            str(SKILLS / "ux-review-builder/tests"), "-p", "test_*.py"],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class MoldesDoOpen(unittest.TestCase):
    def test_at006_relatorio_com_as_secoes_que_a_skill_pede(self):
        molde = ler(RAIZ / "sdd/templates/BUILD_REPORT_TEMPLATE.md")
        for secao in ("## Seleção de modo", "## Drift detectado"):
            with self.subTest(secao=secao):
                self.assertIn("\n%s\n" % secao, molde)
        self.assertIn("| Decisão do usuário |", molde)
        skill = ler(SKILLS / "sdd-build/SKILL.md")
        self.assertIn("Seções obrigatórias: Seleção de modo", skill)
        self.assertIn("Drift detectado (mesmo que \"nenhum\")", skill)

    def test_at006_moldes_sem_sobras_de_outro_projeto(self):
        proibidos = ("Terraform", "Terragrunt", "GCP", "Cloud Run", "Cloud Logging", "Pydantic", "ruff", "mypy", "pytest",
                     "functions/", "`/build`", "/release", "/iterate", "`/define`", "WAF", "SSH", "```python",
                     "Cloud Monitoring", "Cloud ")   # revisão, rodada 1, R1: qualquer "Cloud <serviço>" de um vendor
        for nome in ("DEFINE_TEMPLATE.md", "DESIGN_TEMPLATE.md", "BUILD_REPORT_TEMPLATE.md"):
            tx = ler(RAIZ / "sdd/templates" / nome)
            for p in proibidos:
                with self.subTest(molde=nome, sobra=p):
                    self.assertNotIn(p, tx)


class NaoFinjaNoOpen(unittest.TestCase):
    def test_at007_as_3_dizem_sem_acesso_nao_finja(self):
        # avaliador, ciclo 1, achado 2 (LM-026): a frase inteira, não só o título
        frase = ("**Sem acesso, não finja:** não diga que leu, inspecionou, escreveu, gravou ou rodou o que não leu, "
                 "inspecionou,\nescreveu, gravou ou rodou; sem o código à vista, não invente caminho, comando nem biblioteca")
        for skill in DA_F17C:
            with self.subTest(skill=skill):
                self.assertIn(frase, ler(SKILLS / skill / "SKILL.md"))
        self.assertIn("Sem código e sem a stack escrita no projeto (`AGENTS.md`, `sdd/config.yaml`, README), pergunte a stack e a estrutura mínima", ler(SKILLS / "sdd-design/SKILL.md"))
        self.assertIn("peça o projeto e não monte um BUILD_REPORT só a partir dos documentos", ler(SKILLS / "sdd-build/SKILL.md"))

    def test_at007_define_pergunta_na_primeira_vez(self):
        s = ler(SKILLS / "sdd-define/SKILL.md")
        passo = s.split("### 8. Verify Gate", 1)[1].split("### 9.", 1)[0]
        for trecho in ("\"**existe um comando que devolve 0 quando funciona?**\"", "Não ⇒ `kind: manual-ux`",
                       "3 a 5 frases \"Eu abri … e vi …\"", "`manual-ux` nunca é atalho para não perguntar",
                       "só a UX\npura (aparência, que nenhum comando julga) vai direto a `manual-ux`"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, passo)
        frag = ler(RAIZ / "sdd/templates/fragments/VERIFY_GATE.md")
        self.assertIn("\"Eu abri … e vi …\"", frag)
        # avaliador, ciclo 1, achado 5: o exemplo segue a regra
        self.assertIn('manual_fallback: "Eu abri o app no celular', frag)


class CaminhoDoOpen(unittest.TestCase):
    def test_at010_linha_do_modo_condicionada_e_o_caminho_de_hoje_fica(self):
        linha = ("**Projeto sem `sdd/bin/` (sem o `init`) ou sem acesso aos arquivos (claude.ai, ChatGPT)?** Siga "
                 "`web/MODO_WEB.md`\ndesta skill; os caminhos que ele cita (`references/`, `assets/`) são os de dentro de `web/`.")
        for skill in DA_F17C:
            s = ler(SKILLS / skill / "SKILL.md")
            with self.subTest(skill=skill):
                self.assertEqual(s.count(linha), 1)
                self.assertTrue((SKILLS / skill / "web/MODO_WEB.md").is_file())
                self.assertIn("sdd/bin/", s.replace(linha, ""))   # o caminho do Open continua no SKILL.md
        self.assertIn("sdd/bin/verify-gate.sh sdd/features/DEFINE_{F}.md", ler(SKILLS / "sdd-build/SKILL.md"))

    def test_at010_modo_web_traz_a_mesma_identificacao_do_open(self):
        for skill in DA_F17C:
            s, m = ler(SKILLS / skill / "SKILL.md"), ler(SKILLS / skill / "web/MODO_WEB.md")
            ident = next(ln for ln in s.split("\n") if ln.startswith("`%s v" % skill))
            with self.subTest(skill=skill):
                self.assertEqual(m.count(ident), 1)

    def test_at010_modo_web_nao_e_um_skill_md(self):
        # um SKILL.md aninhado poderia virar uma skill fantasma no agente ou no `npx skills add`
        for skill in DA_F17C:
            with self.subTest(skill=skill):
                self.assertEqual(list((SKILLS / skill / "web").rglob("SKILL.md")), [])


if __name__ == "__main__":
    unittest.main()
