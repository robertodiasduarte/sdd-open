"""Contrato de texto da F12: passos 1.5 e 11 do sdd-define, os 2 briefs, o sdd-design, os templates e o
sdd/WORKFLOW_CONTRACTS.yaml (DEFINE F12 AT-008 a AT-011, AT-016, AT-017, AT-019 e AT-023).

O comportamento mecânico (lints, fronteira, bloco, gate) tem teste próprio; aqui se confere que o texto que
o agente segue manda rodar cada peça, com os campos, blocos e caminhos que os scripts usam — e que as
cópias desses campos (brief, passo, yaml, lint) não divergiram.
"""
from __future__ import annotations

import re
import unittest

from apoio import RAIZ


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


def secao(texto: str, titulo: str) -> str:
    i = texto.index(titulo)
    j = texto.find("\n### ", i + len(titulo))
    k = texto.find("\n## ", i + len(titulo))
    fins = [x for x in (j, k) if x > 0]
    return texto[i:min(fins)] if fins else texto[i:]


DEFINE = ler(".agents/skills/sdd-define/SKILL.md")
PASSO_15 = secao(DEFINE, "### 1.5. Contexto de domínio (cartógrafo)")
PASSO_11 = secao(DEFINE, "### 11. Governança")
CARTOGRAFO = ler(".agents/skills/sdd-define/references/cartografo.md")
REVISOR = ler(".agents/skills/sdd-governanca/references/revisor.md")
DESIGN = ler(".agents/skills/sdd-design/SKILL.md")
CONTRATOS = ler("sdd/WORKFLOW_CONTRACTS.yaml")
LINT = ler("sdd/bin/contexto-lint.sh")


def lista_yaml(bloco: str, chave: str) -> list:
    """Itens `- "x"` da lista `chave:` dentro do mapa de topo `bloco:`."""
    m = re.search(r"(?ms)^" + bloco + r":\n(.*?)(?=^\S|\Z)", CONTRATOS)
    corpo = m.group(1)
    m2 = re.search(r"(?ms)^  " + chave + r":\n((?:    - \"[^\"]*\"\n)+)", corpo)
    return re.findall(r'- "([^"]*)"', m2.group(1))


class Passo15(unittest.TestCase):
    def test_roda_as_pecas_na_ordem_e_nao_trava(self):
        for trecho in ("contexto-lint.sh --sugerir", "[auto · de rotina]", "governanca-fronteira.sh --snapshot",
                       "governanca-fronteira.sh --comparar", "references/cartografo.md",
                       "sdd-fluxo.sh despachar cartografo", "contexto-lint.sh --validade",
                       "**1 redespacho**", "nenhum (<motivo>)", "No máximo 2 domínios por feature",
                       "um despacho por vez", "parada 1 de 2", "🗺️ contexto: pulado", "sdd/patterns/README.md",
                       "**ajuda, não trava**", "`CONTEXTO de domínio`"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, PASSO_15)
        self.assertLess(PASSO_15.index("--snapshot"), PASSO_15.index("despachar cartografo"))
        # L5 (avaliador, ciclo 1): no degrau sem subagente o brief é gravado antes do snapshot
        self.assertLess(PASSO_15.index("BRIEF_cartografo_<F>.md"), PASSO_15.index("--snapshot"))
        self.assertLess(PASSO_11.index("BRIEF_revisor-governanca_<F>.md"), PASSO_11.index("--snapshot"))

    def test_os_4_campos_sao_os_do_brief_e_do_yaml(self):
        campos = ["ctx", "saida", "worktree", "dominio"]
        self.assertEqual(lista_yaml("cartografo", "campos"), campos)
        linha = "ctx: ctx:<slug> · saida: sdd/contexto/<slug>.md · worktree: <raiz> · dominio: sdd/patterns/dominio.md"
        self.assertIn(linha, PASSO_15)
        self.assertIn("ctx: ctx:<slug> · saida: sdd/contexto/<slug>.md · worktree: <caminho absoluto> · dominio: sdd/patterns/dominio.md", CARTOGRAFO)

    def test_secoes_do_brief_yaml_e_lint_sao_as_mesmas(self):
        no_lint = re.search(r'SECOES="([^"]*)"', LINT).group(1).split("\n")
        self.assertEqual(lista_yaml("cartografo", "secoes"), no_lint)
        bloco = re.search(r"(?s)## Saída.*?```text\n(.*?)```", CARTOGRAFO).group(1).strip().split("\n")
        self.assertEqual(bloco, no_lint)


class Passo11(unittest.TestCase):
    def test_trava_antes_do_despacho_e_todas_as_pecas(self):
        for trecho in ("inclusive com `--parar`", "NEEDS CLARIFICATION", "governança não rodou",
                       "`cp sdd/features/DEFINE_<F>.md \"$T/DEFINE.antes\"`", "governanca-fronteira.sh --snapshot",
                       "sdd-fluxo.sh despachar revisor-governanca", "governanca-bloco.py",
                       "--comparar \"$T/comparar.txt\"", "**redespache uma vez**", "PADRAO_AUSENTE",
                       "[D2 · muda o produto]", "nunca \"aplicar todas\"", "**este passo é o dono da prova**",
                       "sdd/tests/governanca/<F>_<Gnn>.sql", "psql -v ON_ERROR_STOP=1 -f",
                       "**nunca produção**", "prova_manual", "`cmp`", "parada 2 de 2",
                       "⚖️ governança: revisando em contexto fresco", "↻ governança:", "🛑 governança não rodou",
                       "não o Define inteiro", "Projeto com revisão N.A. nunca ouve essas perguntas"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, PASSO_11)
        self.assertLess(PASSO_11.index("governança não rodou"), PASSO_11.index("despachar revisor-governanca"))

    def test_a_linha_governanca_so_aparece_como_linha_da_tabela(self):
        self.assertNotRegex(PASSO_11, r"`Governança: ")
        for valor in ("| **Governança** | N.A. — <motivo>", "| **Governança** | GOVERNANCA_REVIEW_<F>.md",
                      "| **Governança** | dispensada — <motivo>", "| **Governança** | falhou — <motivo>"):
            with self.subTest(valor=valor):
                self.assertIn(valor, PASSO_11)
        self.assertIn("**e** trocar o marcador", PASSO_11)

    def test_5_campos_e_resultados_batem_com_brief_yaml_e_validador(self):
        campos = ["define", "skill", "padrao", "worktree", "saida"]
        self.assertEqual(lista_yaml("revisor_governanca", "campos"), campos)
        for c in campos:
            self.assertIn(c + ": <", PASSO_11.replace("<raiz>", "<abs>") + REVISOR)
        resultados = lista_yaml("revisor_governanca", "resultados")
        self.assertEqual(resultados, ["NA", "REVISADO", "PADRAO_AUSENTE", "FALHA"])
        bloco = ler("sdd/bin/governanca-bloco.py")
        self.assertIn('RESULTADOS = ("NA", "REVISADO", "PADRAO_AUSENTE", "FALHA")', bloco)
        self.assertIn("resultado: NA | REVISADO | PADRAO_AUSENTE | FALHA", REVISOR)

    def test_redespacho_do_cartografo_refaz_brief_e_snapshot(self):
        self.assertIn("**refazendo antes** o brief", PASSO_15)

    def test_restauracao_do_define_desfaz_link_antes_do_cp(self):
        self.assertIn('`rm -f sdd/features/DEFINE_<F>.md && cp "$T/DEFINE.antes" sdd/features/DEFINE_<F>.md`', PASSO_11)

    def test_padrao_ausente_refaz_o_snapshot(self):
        self.assertIn("**refaça o\n   snapshot de antes**", PASSO_11)

    def test_briefs_proibem_commit(self):
        self.assertIn("**Não faz commit**", CARTOGRAFO)
        self.assertIn("sem crase, e cada um casa ao menos um arquivo versionado", CARTOGRAFO)
        self.assertIn("Fazer commit ou `git add`", REVISOR)

    def test_brief_do_revisor_diz_quem_e_dono_da_prova(self):
        self.assertIn("**Quem grava o `.sql` em\n   `sdd/tests/governanca/` e o liga ao `cmd` do Verify Gate é o passo 11 do Define**", REVISOR)
        self.assertIn("o Design só lista o arquivo no File Manifest", REVISOR)
        self.assertIn("`**Decisão:** pendente`", REVISOR)
        self.assertIn("Passos 5 e 6: não execute.", REVISOR)

    def test_proximo_passo_do_define_nao_manda_mais_para_a_governanca_avulsa(self):
        enc = DEFINE[DEFINE.index("## Encerramento"):]
        self.assertNotIn("/sdd-governanca", enc)
        self.assertIn("(ux-review ou design)", enc)


class Design(unittest.TestCase):
    def test_c2_c3_c4_c10(self):
        for trecho in ("contexto-lint.sh --validade sdd/contexto/<slug>.md", "nunca uma trava",
                       "patterns-lint.sh --design", "§Esqueleto", "validado_em", "docs-extract-decisions.sh",
                       "`### Decision N: <nome>`", "**abra a entrada\ninteira**", "→ ficha:", "Do instead"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, DESIGN)

    def test_c11_papel_em_aberto_trava_com_pergunta(self):
        self.assertIn("`| Surface (funcional) | Papel | …`", DESIGN)
        self.assertIn("(não na tabela 60/30/10)", DESIGN)
        self.assertIn("**Sua decisão** — [D2 · muda o produto] **Qual o papel da surface", DESIGN)
        ux = ler("sdd/templates/UX_REVIEW_TEMPLATE.md")
        self.assertIn("**Papel em aberto trava o Design:**", ux)


class Contratos(unittest.TestCase):
    def test_todo_caminho_entre_crases_existe(self):
        caminhos = re.findall(r"`([A-Za-z0-9_./-]+\.(?:sh|py|md|yaml))`", CONTRATOS)
        self.assertGreaterEqual(len(caminhos), 8)
        for c in caminhos:
            with self.subTest(caminho=c):
                self.assertTrue((RAIZ / c).is_file(), c)

    def test_exits_do_yaml_batem_com_o_verify_gate(self):
        # R5@claude (rodada 3): os exits do contrato são os do cabeçalho do verify-gate.sh
        bloco = re.search(r"(?ms)^  exits:\n((?:    \w+: \"\d+\"\n)+)", CONTRATOS).group(1)
        do_yaml = sorted(int(x) for x in re.findall(r'"(\d+)"', bloco))
        gate = ler("sdd/bin/verify-gate.sh")
        contrato = gate[gate.index("# Contrato de exit"):gate.index("# Toda saída termina")]
        do_gate = sorted(int(x) for x in re.findall(r"(?m)^#\s+(\d+)\s+=", contrato))
        self.assertEqual(do_yaml, do_gate)
        self.assertEqual(do_yaml, [0, 2, 3, 4, 5, 64])

    def test_snapshot_num_lugar_fixo_e_lint_no_redespacho(self):
        # R1@claude e R3@claude (rodada 3)
        # fixo por projeto e gravável em sandbox: a pasta temporária com o hash da raiz, nunca o .git
        self.assertIn('"${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/<F>/governanca"', PASSO_11)
        self.assertIn('"${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/<F>/cartografo-<slug>"', PASSO_15)
        self.assertNotIn("git-common-dir", PASSO_11 + PASSO_15 + CONTRATOS)
        self.assertIn("5º campo `lint:`", PASSO_15)
        self.assertIn("`lint: <a saída do contexto-lint.sh", CARTOGRAFO)
        self.assertIn('campo_redespacho: "lint"', CONTRATOS)

    def test_retornos_e_permitidos(self):
        self.assertIn('retorno: "<<<CONTEXTO"', CONTRATOS)
        self.assertIn("<<<CONTEXTO", CARTOGRAFO)
        self.assertIn('retorno: "<<<GOVERNANCA"', CONTRATOS)
        self.assertIn("<<<GOVERNANCA", REVISOR)
        self.assertIn('permitido: "sdd/contexto/<slug>.md"', CONTRATOS)
        self.assertIn('permitido: "sdd/reviews/GOVERNANCA_REVIEW_<F>.md"', CONTRATOS)


class SemRDD(unittest.TestCase):
    ARQUIVOS = ("sdd/bin/contexto-lint.sh", "sdd/bin/patterns-lint.sh", "sdd/bin/governanca-fronteira.sh",
                "sdd/bin/docs-extract-decisions.sh", "sdd/bin/governanca-bloco.py", "sdd/patterns/README.md",
                "sdd/WORKFLOW_CONTRACTS.yaml", ".agents/skills/sdd-define/references/cartografo.md",
                ".agents/skills/sdd-governanca/references/revisor.md", "docs/context-and-governance.md",
                "docs/pt-BR/context-and-governance.md")

    def test_nada_especifico_da_rdd(self):
        termo = re.compile(r"supabase|deno|wordpress|wp-content|rdd-plataforma|hostinger|RDD/Wordpress|rdd-eval", re.I)
        arquivos = list(self.ARQUIVOS) + [str(p.relative_to(RAIZ)) for p in (RAIZ / "sdd/fixtures/contexto").rglob("*") if p.is_file()]
        arquivos += [str(p.relative_to(RAIZ)) for p in (RAIZ / "sdd/fixtures/patterns").glob("*.md")]
        for a in arquivos:
            with self.subTest(arquivo=a):
                self.assertIsNone(termo.search(ler(a)), a)
