"""Contrato de texto da F13: o que os agentes seguem manda rodar cada peça, com os nomes que os scripts usam
(DEFINE F13 AT-018 a AT-020, AT-023 a AT-030, AT-032).

O comportamento mecânico tem teste próprio (test_contraste, test_prompt_drift_scan, test_design_lint), e a
obediência ao roteador é provada num agente real, fora da suíte. Aqui se confere que as frases existem e que as
cópias dos mesmos nomes (fragmento, template, lint, integração) não divergiram.
"""
from __future__ import annotations

import re
import shutil
import unittest

from apoio import BASH, RAIZ, Sandbox


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


FRAGMENTO = ler("sdd/templates/fragments/LLM_PROMPTS_DESIGN.md")
TEMPLATE_D = ler("sdd/templates/DESIGN_TEMPLATE.md")
TEMPLATE_UX = ler("sdd/templates/UX_REVIEW_TEMPLATE.md")
BUILD = ler(".agents/skills/sdd-build/SKILL.md")
DESIGN = ler(".agents/skills/sdd-design/SKILL.md")
UX = ler(".agents/skills/sdd-ux-review/SKILL.md")
INTEGRACAO = ler(".agents/skills/sdd-prompt-builder/references/sdd-integration.md")
PROMPT_SKILL = ler(".agents/skills/sdd-prompt-builder/SKILL.md")
BUILD_REPORT = ler("sdd/templates/fragments/LLM_PROMPTS_BUILD_REPORT.md")
WORKER = ler("sdd/templates/fragments/WORKER_BRIEF.md")
LOOP = ler(".agents/skills/sdd-loop-builder/SKILL.md")
REGRAS = ler(".agents/skills/sdd-loop-builder/references/loop-spec-rules.md")
EXEMPLO = ler(".agents/skills/sdd-loop-builder/references/exemplo-loop-spec.md")
COMO_FALAR = ler(".agents/skills/sdd-loop-builder/references/como-falar.md")

COLUNAS = ("Nome", "Tipo", "Arquivo de destino", "Versão", "Provedor/Modelo", "Origem da entrada",
           "Consumidor da saída", "Material de referência", "Completeness", "Refator de?")
CAMPOS = ("Tom/audiência", "Tipo de saída", "Fallback aprovado", "Autônomo?", "Verification interna",
          "Eval mínimo pré-ship")
PERFIS = {
    "lite": ("intent", "control_state", "observation", "verifier", "stop_rules", "budget"),
    "standard": ("intent", "control_state", "cycle_protocol", "context_assembly", "action_space", "observation",
                 "verifier", "recovery_and_convergence_policy", "stop_rules", "budget", "observability"),
}
PERFIS["high-risk"] = PERFIS["standard"] + ("safety_and_effects",)


def passo_4(texto: str) -> str:
    i = texto.index("### 4. Executar cada tarefa")
    return texto[i:texto.index("### 4b.", i)]


class Fragmento(unittest.TestCase):
    def test_tem_as_partes(self):
        for parte in ("## LLM Prompts", "### Roteador", "### Inventário", "### Contrato por prompt", "### Versionamento",
                      "### Gate do Build por Tipo", "`sdd-loop-builder`", "`prompts.builder_skill`",
                      "prompt-drift-scan.sh --conteudo", "LOOP_SPEC.md"):
            with self.subTest(parte=parte):
                self.assertIn(parte, FRAGMENTO)

    def test_colunas_e_campos_sao_os_mesmos_em_todas_as_copias(self):
        for nome in COLUNAS + CAMPOS:
            for rotulo, texto in (("fragmento", FRAGMENTO), ("template", TEMPLATE_D), ("integração", INTEGRACAO)):
                with self.subTest(nome=nome, onde=rotulo):
                    self.assertIn(nome, texto)
        lint = ler("sdd/bin/design-lint.py")
        for nome in ("Tipo", "Versão", "Completeness", "Refator de?", "Autônomo?", "Verification interna",
                     "Eval mínimo pré-ship"):
            with self.subTest(nome=nome, onde="lint"):
                self.assertIn('"%s"' % nome, lint)

    def test_template_so_aponta_com_um_comentario(self):
        self.assertIn("sdd/templates/fragments/LLM_PROMPTS_DESIGN.md", TEMPLATE_D)
        self.assertIsNone(re.search(r"(?m)^## LLM Prompts", TEMPLATE_D), "seção real no template")

    def test_design_copia_o_fragmento_e_nao_chama_builder(self):
        i = DESIGN.index("### 5.5. LLM Prompts")
        passo = DESIGN[i:DESIGN.index("### 6.", i)]
        self.assertIn("sdd/templates/fragments/LLM_PROMPTS_DESIGN.md", passo)
        self.assertIn("Não escreva o prompt nem chame skill de prompt aqui", passo)
        self.assertIn("design-lint.py", passo)


class Roteador(unittest.TestCase):
    def setUp(self):
        self.p = passo_4(BUILD)

    def test_inventario_vai_direto_ao_roteador_sem_varredura_antes(self):
        i_rot = self.p.index("**Prompt no inventário**")
        i_fora = self.p.index("**Arquivo fora do inventário**")
        self.assertLess(i_rot, i_fora)
        self.assertIn("sem varredura antes", self.p[i_rot:i_fora])

    def test_por_tipo(self):
        for frase in ("**`one-shot`:**", "`sdd-prompt-builder`", "`prompts.builder_skill`", "**`loop`:**", "`sdd-loop-builder`",
                      "para cada estágio LLM", "<pasta do processo>/LOOP_SPEC.md", "contam como inventariados"):
            with self.subTest(frase=frase):
                self.assertIn(frase, self.p)

    def test_o_texto_gerado_passa_pelo_scan_e_2_e_esperado(self):
        i = self.p.index("**Antes de gravar**")
        self.assertIn("prompt-drift-scan.sh --conteudo", self.p[i:])
        self.assertIn("saída 2 aqui é o esperado e grava", self.p[i:])

    def test_fora_do_inventario_cada_saida_tem_destino(self):
        i = self.p.index("**Arquivo fora do inventário**")
        trecho = self.p[i:]
        for frase in ("prompt-drift-scan.sh --conteudo", "Saída 0", "Saída 64", "nunca ignore", "Saída 2", "**pare**",
                      "Drift detectado", "Arquivo vazio não precisa", "uma vez por"):
            with self.subTest(frase=frase):
                self.assertIn(frase, trecho)

    def test_nao_encerrar_o_turno(self):
        self.assertIn("Não encerre o turno ao receber o bloco de texto", self.p)
        self.assertIn("🔁 item em laço", self.p)

    def test_sem_tipo_e_skill_ausente(self):
        self.assertIn("o processo re-prompta o modelo com base na própria saída", self.p.replace("\n     ", " "))
        self.assertIn("na dúvida, `loop`", self.p)
        self.assertIn("Registre a triagem no relatório", self.p)
        self.assertIn("🛑 não encontrei a skill", self.p)
        self.assertIn("faça esta pergunta à letra, com a marca", self.p)
        self.assertIn("[D2 · muda o produto]", self.p)
        self.assertIn("nada foi improvisado", self.p)

    def test_rotas_da_recusa_da_skill(self):
        self.assertIn("**item faltando**", self.p)
        self.assertIn("**não é laço**", self.p)
        self.assertIn("o destino para o arquivo do prompt", self.p)
        self.assertIn("nada\n     é gravado neste item", self.p)

    def test_o_contrato_do_laco_se_compila_do_design(self):
        for campo in ("Intenção", "Perfil de risco dos efeitos", "Ground truth disponível"):
            with self.subTest(campo=campo):
                self.assertIn(campo, self.p.replace("\n     ", " "))
                self.assertIn("**%s**" % campo, FRAGMENTO)

    def test_tabela_de_estagios_e_prompts_pendentes_chegam_a_quem_escreve(self):
        self.assertIn("O bloco\n     inteiro vai para", self.p)
        for texto in (self.p, INTEGRACAO, FRAGMENTO, LOOP):
            self.assertIn("PROMPTS PENDENTES", texto)
        self.assertIn("grava o bloco inteiro", LOOP)

    def test_nome_fixo_sem_slot_da_skill(self):
        for texto in (BUILD, ler("sdd/config.example.yaml"), FRAGMENTO):
            self.assertNotIn("loop_builder_skill", texto)


class SkillDoLaco(unittest.TestCase):
    def test_entrada_e_saida(self):
        for frase in ("**Intenção:**", "**Risco dos efeitos:**", "**Referência normativa literal:**",
                      "**Decisões já fechadas:**", "**Ground truth disponível:**", "exatamente um bloco de texto",
                      "Os prompts dos estágios nunca nascem aqui"):
            with self.subTest(frase=frase):
                self.assertIn(frase, LOOP)

    def test_saidas_de_excecao(self):
        self.assertIn("recomende a skill de prompt e", LOOP)
        self.assertIn("Nunca\n   preencha por conta própria", LOOP)

    def test_orcamento_por_estagio_e_desenho_da_skill_nao_item_do_contrato(self):
        # Prova real no Codex: sem esta frase, o agente parava pedindo os tetos ao DESIGN.
        self.assertIn("**não**\n   são itens do contrato", LOOP)
        self.assertIn("proponha e marque como proposta, sem parar", LOOP)

    def test_regras_tem_o_contrato_inteiro(self):
        self.assertIn('<LOOP_SPEC v="2" perfil="lite|standard|high-risk"', REGRAS)
        for perfil, secoes in PERFIS.items():
            for s in secoes:
                with self.subTest(perfil=perfil, secao=s):
                    self.assertIn("`%s`" % s, REGRAS)
                    self.assertIn("<%s>" % s, REGRAS)
        for frase in ("VERIFIER_FAILURE", "NEEDS_APPROVAL", "NON_CONVERGENCE", "ESTÁGIOS:", "PROMPTS PENDENTES:", "VERIFY GATE:",
                      "`tipo` é `LLM` ou `código`", "por estágio", "Código antes do modelo"):
            with self.subTest(frase=frase):
                self.assertIn(frase, REGRAS)

    def test_perfil_se_decide_sem_ambiguidade(self):
        self.assertIn("efeito externo ou irreversível é sempre `high-risk`", REGRAS)
        self.assertIn("**1** estágio LLM", REGRAS)
        self.assertIn("**2 ou mais** estágios LLM", REGRAS)
        self.assertIn("em todo outro caso", REGRAS)
        self.assertNotIn("avaliação offline", REGRAS)
        estagios_llm = [ln for ln in EXEMPLO.splitlines() if re.match(r"^\| \d+ \|", ln) and "| LLM |" in ln]
        self.assertEqual((len(estagios_llm), 'perfil="standard"' in EXEMPLO), (2, True))

    def test_exemplo_cumpre_o_proprio_perfil(self):
        m = re.search(r'<LOOP_SPEC v="2" perfil="([a-z-]+)" nome="', EXEMPLO)
        self.assertIsNotNone(m)
        for s in PERFIS[m.group(1)]:
            with self.subTest(secao=s):
                self.assertIn("<%s>" % s, EXEMPLO)
                self.assertIn("</%s>" % s, EXEMPLO)
        estagios = [ln for ln in EXEMPLO.splitlines() if re.match(r"^\| \d+ \|", ln)]
        tipos = [ln.split("|")[3].strip() for ln in estagios]
        self.assertIn("LLM", tipos)
        self.assertIn("código", tipos)
        for ln in estagios:
            cels = [c.strip() for c in ln.strip("|").split("|")]
            with self.subTest(estagio=cels[1]):
                if cels[2] == "LLM":
                    self.assertTrue(cels[5].isdigit(), "estágio LLM sem teto de tokens")
                    self.assertRegex(cels[7], r"\.txt$")
                else:
                    self.assertEqual((cels[5], cels[7]), ("—", "—"))
        self.assertIn("redigir: 4000 tokens", EXEMPLO)
        self.assertIn("reescrever: 2000 tokens", EXEMPLO)

    def test_glossario_para_quem_nunca_viu(self):
        for termo in ("LOOP_SPEC —", "perfil —", "estágio —", "verificador —", "Isto é uma chamada única"):
            with self.subTest(termo=termo):
                self.assertIn(termo, COMO_FALAR)


class Integracao(unittest.TestCase):
    def test_integracao_da_skill_de_prompt(self):
        for frase in ("`sdd-loop-builder`", "prompt-drift-scan.sh --conteudo", "`prompts.wrapper_pattern`",
                      "o contrato dele é o bloco da linha `Tipo=loop` mais a\n   linha do estágio",
                      "1 entrada pela LOOP_SPEC e 1 por estágio", "a fase Design só inventaria"):
            with self.subTest(frase=frase):
                self.assertIn(frase, INTEGRACAO)

    def test_skill_de_prompt_e_da_fase_build(self):
        self.assertIn("a fase Build de um fluxo SDD", PROMPT_SKILL)
        self.assertNotIn("fluxo SDD design/build", PROMPT_SKILL)
        self.assertNotIn("fases Design/Build", INTEGRACAO)

    def test_relatorio_do_build(self):
        for frase in ("`sdd-loop-builder`", "LOOP_SPEC.md", "1 entrada pela LOOP_SPEC e 1 por estágio LLM", "prompt-drift-scan.sh",
                      "o eval fica para antes da release"):
            with self.subTest(frase=frase):
                self.assertIn(frase, BUILD_REPORT)

    def test_modo_briefs_nao_ignora_o_roteador(self):
        self.assertIn("`sdd-loop-builder`", WORKER)
        self.assertIn("roteador do passo 4", WORKER)
        self.assertIn("bash sdd/bin/prompt-drift-scan.sh <arquivos da wave>", WORKER)
        self.assertNotIn("Drift detection roda ANTES do despacho", WORKER)


class TabelaWcag(unittest.TestCase):
    def setUp(self):
        i = TEMPLATE_UX.index("## Accessibility and Responsiveness")
        self.secao = TEMPLATE_UX[i:TEMPLATE_UX.index("## Lentes cognitivas", i)]

    def test_sete_criterios_com_nivel(self):
        for sc, nivel in (("1.4.3", "AA"), ("1.4.11", "AA"), ("1.4.1", "A"), ("2.4.7", "AA"), ("4.1.2", "A"),
                          ("2.1.1", "A"), ("2.5.8", "AA")):
            with self.subTest(sc=sc):
                self.assertRegex(self.secao, r"(?m)^\| %s \| %s \|" % (re.escape(sc), nivel))

    def test_cinco_com_veredito_e_dois_herdados(self):
        linhas = [ln for ln in self.secao.splitlines() if re.match(r"^\| \d\.\d", ln)]
        self.assertEqual(len(linhas), 7)
        self.assertEqual(sum("PASSA / REPROVA / N.A." in ln for ln in linhas), 5)
        self.assertEqual(sum("herdado → Acceptance notes" in ln for ln in linhas), 2)

    def test_nota_de_nivel(self):
        self.assertIn("3.3.7 é nível A e 2.4.13 é AAA", self.secao)
        self.assertIsNone(re.search(r"(?m)^\| (3\.3\.7|2\.4\.13) ", self.secao))

    def test_segue_o_texto_da_norma(self):
        # 1.4.3 isenta componente inativo; 2.4.7 só pede foco visível (o 3:1 do anel vem de 1.4.11).
        self.assertNotIn("desabilitado", self.secao)
        linha_247 = next(ln for ln in self.secao.splitlines() if ln.startswith("| 2.4.7"))
        self.assertNotIn("3:1", linha_247)
        linha_1411 = next(ln for ln in self.secao.splitlines() if ln.startswith("| 1.4.11"))
        self.assertIn("anel de foco", linha_1411)

    def test_acceptance_notes_tem_os_herdados(self):
        self.assertIn("- [ ] 2.1.1 (herdado da tabela WCAG)", TEMPLATE_UX)
        self.assertIn("- [ ] 2.5.8 (herdado da tabela WCAG)", TEMPLATE_UX)

    def test_skill_exige_a_tabela(self):
        i = UX.index("4.5. **WCAG 2.2 AA.**")
        passo = UX[i:UX.index("5. **Lentes", i)]
        for frase in ("sdd/bin/contraste.sh", "N.A. — <motivo>", "**1 MUST**", "com o critério e o par medido", "por tema",
                      "1.4.3", "2.5.8", "Acceptance notes"):
            with self.subTest(frase=frase):
                self.assertIn(frase, passo)
        self.assertIn("Tabela WCAG preenchida com evidência", UX)


class Configuracao(unittest.TestCase):
    def test_slot_com_exemplo_e_sem_os_cortados(self):
        cfg = ler("sdd/config.example.yaml")
        self.assertRegex(cfg, r'(?m)^  wrapper_pattern: ""$')
        self.assertIn("systemPrompt:", cfg)
        for proibido in ("smoke.", "smoke:", "urls_cmd", "a11y_cmd", "loop_builder_skill"):
            self.assertNotIn(proibido, cfg)

    def test_guias_de_adaptacao(self):
        for rel in ("docs/adaptation-guide.md", "docs/pt-BR/adaptation-guide.md"):
            with self.subTest(guia=rel):
                self.assertIn('wrapper_pattern: ""', ler(rel))


class Empacotamento(unittest.TestCase):
    ARQUIVOS = ("sdd/bin/contraste.sh", "sdd/bin/prompt-drift-scan.sh", "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md",
                ".agents/skills/sdd-loop-builder/SKILL.md", ".agents/skills/sdd-loop-builder/references/como-falar.md",
                ".agents/skills/sdd-loop-builder/references/loop-spec-rules.md",
                ".agents/skills/sdd-loop-builder/references/exemplo-loop-spec.md", "docs/llm-in-code.md",
                "docs/pt-BR/llm-in-code.md")

    def test_tudo_no_manifest(self):
        manifest = ler("MANIFEST.txt").splitlines()
        for rel in self.ARQUIVOS + ("tests/test_contraste.py", "tests/test_prompt_drift_scan.py", "tests/test_f13_textos.py"):
            with self.subTest(rel=rel):
                self.assertIn(rel, manifest)

    def test_nada_especifico_da_rdd(self):
        proibido = re.compile(r"supabase|\bdeno\b|wordpress|wp-content|rdd-plataforma|hostinger|rdd/wordpress|rdd-eval|"
                              r"\bkimi\b|\bcodex\b|\bgemini\b|\bmuse\b|\bqwen\b|LM-\d|fp-eval|\bWARM\b|\bCOOL\b|\bLBI\b", re.I)
        for rel in self.ARQUIVOS:
            with self.subTest(rel=rel):
                self.assertEqual(proibido.findall(ler(rel)), [])

    def test_call_llm_so_como_exemplo(self):
        # O self-test do scan precisa de uma amostra; fora dele, o nome só aparece como exemplo do slot.
        for rel in self.ARQUIVOS + ("sdd/config.example.yaml", "docs/adaptation-guide.md", "docs/pt-BR/adaptation-guide.md"):
            if rel == "sdd/bin/prompt-drift-scan.sh":
                continue
            for ln in ler(rel).splitlines():
                if "callLLM" in ln:
                    with self.subTest(rel=rel, linha=ln):
                        self.assertRegex(ln, r"callLLM\\+\(|\bcallLLM\b.*(wrapper|expressão)")

    def test_scripts_no_piso_do_bash(self):
        for rel in ("sdd/bin/contraste.sh", "sdd/bin/prompt-drift-scan.sh"):
            with self.subTest(rel=rel):
                self.assertIsNone(re.search(r"mapfile|declare -A|\$\{[a-zA-Z_]+\^\^", ler(rel)))

    def test_textos_chamam_os_scripts_com_bash(self):
        # 20 de 25 arquivos de sdd/bin nascem sem o bit de execução.
        for rel in (".agents/skills/sdd-build/SKILL.md", ".agents/skills/sdd-ux-review/SKILL.md",
                    "sdd/templates/UX_REVIEW_TEMPLATE.md", "docs/llm-in-code.md", "docs/pt-BR/llm-in-code.md",
                    "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md"):
            for m in re.finditer(r"[^\n]*sdd/bin/(contraste|prompt-drift-scan)\.sh '?[-#<$]", ler(rel)):
                with self.subTest(rel=rel, trecho=m.group(0)):
                    self.assertIn("bash sdd/bin/", m.group(0))


class Instalacao(Sandbox):
    def test_init_completa_e_nao_sobrescreve_e_sync_gera_o_adaptador(self):
        cli = RAIZ / "bin/sdd-open.sh"
        repo = self.tmp / "proj"
        repo.mkdir()
        self.git(repo, "init", "-q")
        rc, out, err = self.roda([BASH, cli, "init", "--yes", "--vendors", "claude"], repo)
        self.assertEqual(rc, 0, out + err)
        novos = ("sdd/bin/contraste.sh", "sdd/bin/prompt-drift-scan.sh", "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md",
                 ".agents/skills/sdd-loop-builder/SKILL.md", ".claude/skills/sdd-loop-builder/SKILL.md")
        for rel in novos:
            with self.subTest(rel=rel):
                self.assertTrue((repo / rel).is_file())
        # Instalação anterior: faltam os novos, e o que o usuário já tem não muda.
        (repo / "sdd/bin/contraste.sh").write_text("# meu\n", encoding="utf-8")
        (repo / "sdd/bin/prompt-drift-scan.sh").unlink()
        (repo / "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md").unlink()
        shutil.rmtree(str(repo / ".agents/skills/sdd-loop-builder"))
        shutil.rmtree(str(repo / ".claude/skills/sdd-loop-builder"))
        rc, out, err = self.roda([BASH, cli, "init", "--yes", "--vendors", "claude"], repo)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((repo / "sdd/bin/contraste.sh").read_text(encoding="utf-8"), "# meu\n")
        self.assertTrue((repo / "sdd/bin/prompt-drift-scan.sh").is_file())
        self.assertTrue((repo / "sdd/templates/fragments/LLM_PROMPTS_DESIGN.md").is_file())
        self.assertTrue((repo / ".agents/skills/sdd-loop-builder/references/loop-spec-rules.md").is_file())
        self.assertTrue((repo / ".claude/skills/sdd-loop-builder/SKILL.md").is_file())
        # O sync gera a cópia do adaptador a partir da skill que está em .agents/skills/.
        shutil.rmtree(str(repo / ".claude/skills/sdd-loop-builder"))
        rc, out, err = self.roda([BASH, cli, "sync", "--yes", "--vendors", "claude"], repo)
        self.assertEqual(rc, 0, out + err)
        self.assertTrue((repo / ".claude/skills/sdd-loop-builder/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
