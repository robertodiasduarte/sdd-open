"""Contrato de texto da F14: o passo 17b da sdd-release, o brief do curador, o sdd/WORKFLOW_CONTRACTS.yaml, a
sdd-new-session, o molde do handoff, docs e versões (DEFINE F14 AT-023 a AT-025, AT-028, AT-029, AT-034 a AT-036).

O comportamento mecânico tem teste próprio; aqui se confere que o texto que o agente segue manda rodar cada peça, na
ordem, com os nomes que os scripts usam, e que as cópias desses nomes (brief, script, yaml) não divergiram.
"""
from __future__ import annotations

import os
import re
import unittest

from apoio import BASH, RAIZ, Sandbox


def ler(rel: str) -> str:
    return (RAIZ / rel).read_text(encoding="utf-8")


RELEASE = ler(".agents/skills/sdd-release/SKILL.md")
PASSO = RELEASE[RELEASE.index("17b. **Curadoria do playbook"):RELEASE.index("18. **Imprimir a ficha**")]
COMO_FALAR = ler(".agents/skills/sdd-release/references/como-falar.md")
CURATOR_MD = ler(".agents/skills/sdd-playbook/references/curator.md")
SCRIPT = ler("sdd/bin/playbook-curator.sh")
CONTRATOS = ler("sdd/WORKFLOW_CONTRACTS.yaml")
NOVOS = ("sdd/bin/playbook-curator.sh", ".agents/skills/sdd-new-session/scripts/copiar-docs.sh")


def lista_yaml(chave: str) -> list:
    bloco = re.search(r"(?ms)^curador:\n(.*?)(?=^\S|\Z)", CONTRATOS).group(1)
    corpo = re.search(r"(?ms)^  " + chave + r":\n((?:    - \"[^\"]*\"\n)+)", bloco).group(1)
    return re.findall(r'- "([^"]*)"', corpo)


class Passo17b(unittest.TestCase):
    def test_as_pecas_vem_nesta_ordem(self):
        ordem = ("--preparar {F}", "--colher \"$STG\"", "BRIEF_curador_{F}.md", "--selar \"$STG\"", "governanca-fronteira.sh --snapshot",
                 "sdd-fluxo.sh despachar curador", "governanca-fronteira.sh --comparar", "--conferir-bloco",
                 "--cruzar -", "--aplicar \"$STG/delta.txt\"", "playbook-lint.sh \"$STG/novo.md\"", "--anti-collapse",
                 "--aplicar-inv", "--validar-inv", "cp \"$STG/novo.md\" sdd/playbook.md", "CURATOR-colheita.log",
                 "CURATOR-delta.log", "sdd/releases/{F}/CURATOR-colhidos.txt", "git add sdd/playbook.md", "[D1 · não se desfaz]")
        pos = -1
        for trecho in ordem:
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, PASSO)
                agora = PASSO.index(trecho, pos + 1) if trecho in PASSO[pos + 1:] else -1
                self.assertGreater(agora, pos, "fora de ordem: " + trecho)
                pos = agora

    def test_falha_de_coleta_nao_e_zero_deltas(self):
        self.assertIn("`Curadoria: 0 deltas`", PASSO)
        self.assertIn('**não é "0 deltas"**', PASSO)
        self.assertIn("`Curadoria: FALHOU (rc=N)`", PASSO)
        self.assertIn("a publicação não foi afetada", PASSO)
        self.assertIn("`1` com `RESULTADO: NADA A COLHER` em `colheita.txt`", PASSO)
        self.assertIn("inclusive `1` sem aquela linha", PASSO)
        self.assertRegex(PASSO, r"\(`2`, `64`, `126`, `127`")

    def test_so_o_conferidor_separa_contagem_de_regra(self):
        self.assertIn("Nunca separe contagem de regra à mão", PASSO)
        self.assertIn("linhas `AUTO <delta>`", " ".join(PASSO.split()))
        self.assertIn("`PERGUNTA <n> <tipo> <delta>`", PASSO)
        self.assertIn("**1 vez**", PASSO)
        self.assertIn("`Curadoria: FALHOU (bloco inválido)`", PASSO)
        self.assertIn("**nada é aplicado**", PASSO)

    def test_fala_com_a_pessoa(self):
        for trecho in ("a publicação já terminou", "`[D3 · muda a regra do método]`", "**aceitar**, **recusar** e **não sei**",
                       "até 5 por vez", "**uma opção só**", "**Decidi sozinho**", "`git revert <sha do commit da curadoria>`",
                       "invariantes: arquivo ausente, cruzamento pulado", "**deixar para a próxima publicação**",
                       "cada linha `REJEITADO`", "`🧹 curadoria:"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, " ".join(PASSO.split()))

    def test_sem_subagente_para_no_exit_40(self):
        self.assertIn("pare no exit 40", PASSO)
        self.assertIn("--retomar", PASSO)

    def test_retomada_nao_refaz_a_linha_de_base(self):
        t = " ".join(PASSO.split())
        self.assertIn('vá direto para a parte "Na volta" do item 3', t)
        self.assertIn("refazer o selo ou o snapshot de antes agora tomaria por linha de base", t)

    def test_redespacho_depois_de_escrita_refaz_a_linha_de_base_ou_para(self):
        t = " ".join(PASSO.split())
        for trecho in ("sem `FORA:` nem staging mexido, redespache com o mesmo selo", "**não redespache**",
                       "`Curadoria: FALHOU (curador escreveu no playbook)`", "refaça os itens 1 e 2, o selo e o snapshot de antes"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, t)

    def test_entrada_do_cruzar_nao_passa_pelo_shell(self):
        # R5@claude da rodada 2: crase no texto da lição, dentro de aspas duplas, é executada.
        for texto in (" ".join(PASSO.split()), " ".join(CURATOR_MD.split())):
            self.assertIn("<<'FIM_DOS_DELTAS'", texto)
            self.assertNotIn("printf '%s\\n' <", texto)

    def test_cruzar_sem_as_linhas_inv_e_licao_antiga(self):
        t = " ".join(PASSO.split())
        self.assertIn("sem as linhas de tipo inv", t)
        self.assertIn("`Curadoria: FALHOU (invariantes sem classificação)`", t)

    def test_promocao_nao_entra_no_delta_agora(self):
        t = " ".join(PASSO.split())
        self.assertIn("a promoção aceita vira pendência na ficha", t)

    def test_nada_aceito_tem_caminho_e_evidencia_nao_versionada_tambem(self):
        t = " ".join(PASSO.split())
        for trecho in ("`Curadoria: nada aplicado`", "git check-ignore -q", "git ls-files sdd/reports/evidence", "colheita.rc",
                       ': > "$STG/delta.txt"', "mkdir -p sdd/reports/briefs sdd/reports/evidence/{F} sdd/releases/{F}", "git ls-files sdd/releases",
                       "traga o registro e os logs do item 8 da frente", "a pasta temporária se perdeu", "`git cherry-pick --abort`"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, t)

    def test_o_commit_nao_sai_sem_um_sim_e_reconfere_na_base(self):
        i = PASSO.index("**Recibo e envio.**")
        envio = PASSO[i:]
        for trecho in ("**Posso enviar o commit da curadoria para a branch padrão?**", "`playbook-lint.sh`", "`--validar-inv`",
                       "`--aplicar`, que recalcula os IDs", "`--aplicar-inv`", "renumere o novo, nunca o da base"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, envio)

    def test_nunca_edita_invariantes_a_mao_nem_pula_o_hook(self):
        self.assertIn("edite as invariantes à mão", PASSO)
        self.assertIn("Nunca `--no-verify`", PASSO)

    def test_a_curadoria_nao_entra_nos_abortos_nem_no_bloco_do_ok(self):
        abortos = RELEASE[RELEASE.index("## Gates de ABORTAR"):RELEASE.index("## Quando pular")]
        self.assertNotIn("uradoria", abortos)
        ok = RELEASE[RELEASE.index("7. **PARAR e mostrar"):RELEASE.index("## FASE 2")]
        self.assertNotIn("uradoria", ok)

    def test_exemplos_no_como_falar(self):
        i = COMO_FALAR.index("## Exemplo — a curadoria")
        ex = COMO_FALAR[i:]
        for trecho in ("**Decidi sozinho**", "[D3 · muda a regra do método]", "[D1 · não se desfaz]", "(ref: LM-023)", "(ref: LM-004)",
                       "**aceitar** (recomendado)", "**não sei**", "A publicação não foi afetada", "esta feature não trouxe lição nova nem contagem",
                       "**uma opção só**"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, ex)
        for termo in ("curadoria —", "delta —", "aposentar (tombstone) —", "promover —", "invariante —"):
            with self.subTest(termo=termo):
                self.assertIn(termo, COMO_FALAR)

    def test_por_que_cada_regra_existe(self):
        por_que = RELEASE[RELEASE.index("## Por que cada regra existe"):RELEASE.index("## Encerramento")]
        for trecho in ('nunca vale como "nada a colher"', "é o conferidor", "fronteira de escrita", "não sai da máquina"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, por_que)


class LimiteDoRedespacho(unittest.TestCase):
    """R4 da rodada 4: sem subagente, a 2ª tentativa volta numa sessão sem memória da 1ª."""

    def test_o_brief_com_conferencia_marca_a_2a_tentativa(self):
        corrido = " ".join(PASSO.split())
        self.assertIn("se ele já tem o campo `conferencia:`, esta é a 2ª tentativa, e nova reprovação encerra aqui, sem redespachar", corrido)

    def test_a_1a_reprovacao_continua_redespachando(self):
        # o outro lado: a leitura do brief não pode tirar o redespacho da 1ª reprovação
        corrido = " ".join(PASSO.split())
        self.assertIn("Exit 2 ⇒ despache de novo **1 vez**, com os 5 campos mais o campo `conferencia:`", corrido)


class BriefDoCurador(unittest.TestCase):
    def test_campos_iguais_no_brief_no_passo_e_no_yaml(self):
        campos = lista_yaml("campos")
        self.assertEqual(campos, ["feature", "staging", "colheita", "playbook", "worktree"])
        linha_brief = re.search(r"(?m)^feature: .*$", CURATOR_MD).group(0)
        linha_passo = re.search(r"`(feature: \{F\}[^`]*)`", PASSO).group(1)
        for linha in (linha_brief, linha_passo):
            with self.subTest(linha=linha[:30]):
                self.assertEqual(re.findall(r"(?:^|· )(\w+):", linha), campos)

    def test_tipos_recomendacoes_colunas_e_finais_iguais_no_script_no_yaml_e_no_brief(self):
        def tupla(nome):
            return re.findall(r'"([^"]+)"', re.search(r"(?m)^" + nome + r" = \((.*)\)$", SCRIPT).group(1))
        for nome, chave in (("TIPOS", "tipos"), ("RECOMENDACOES", "recomendacoes"), ("COLUNAS", "colunas"), ("FINAIS", "finais")):
            with self.subTest(nome=nome):
                self.assertEqual(tupla(nome), lista_yaml(chave))
        for t in tupla("TIPOS") + tupla("COLUNAS")[1:] + ["NAO_JULGADO", "AUTO", "ACEITAR", "DESCARTAR", "PERGUNTA OBRIGATÓRIA"]:
            with self.subTest(item=t):
                self.assertIn(t, CURATOR_MD)
        for f in tupla("FINAIS"):
            with self.subTest(final=f):
                self.assertIn(f, CURATOR_MD)
        self.assertIn("| # | Tipo | LM | Delta | Evidência | Em linguagem simples | Recomendação |", CURATOR_MD)

    def test_proibicoes_e_contaminacao(self):
        for trecho in ("**Nunca escrever**", "CONTAMINAÇÃO: sim", "**Toda linha da colheita aparece no bloco.**", "`AUTO` só em linha `contador`",
                       "**Não rode** `playbook-curator.sh --colher`", "campo `conferencia:`", "sdd-fluxo.sh despachar curador",
                       "sdd-build/references/contexto-fresco.md", "<<<CURADORIA"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, CURATOR_MD)

    def test_o_bloco_de_exemplo_do_brief_passa_pelo_formato_das_colunas(self):
        tabela = [ln for ln in CURATOR_MD.split("\n") if re.match(r"^\| \d+ \| ", ln)]
        self.assertGreaterEqual(len(tabela), 5)
        for ln in tabela:
            with self.subTest(linha=ln[:30]):
                self.assertEqual(len(re.split(r"(?<!\\)\|", ln.strip().strip("|"))), 7)

    def test_nao_cita_ferramenta_de_um_agente_so(self):
        for proibido in ("AskUserQuestion", "subagent_type", "Task tool", "Agent tool", "PreToolUse"):
            with self.subTest(proibido=proibido):
                self.assertNotIn(proibido, CURATOR_MD)
                self.assertNotIn(proibido, PASSO)

    def test_os_caminhos_do_contrato_existem(self):
        bloco = re.search(r"(?ms)^curador:\n(.*?)(?=^\S|\Z)", CONTRATOS).group(1)
        for caminho in re.findall(r"`([^`]+)`", bloco):
            with self.subTest(caminho=caminho):
                self.assertTrue((RAIZ / caminho).exists(), caminho)

    def test_a_skill_aponta_o_brief_e_as_invariantes(self):
        skill = ler(".agents/skills/sdd-playbook/SKILL.md")
        self.assertNotIn("com OK humano por delta", skill)
        for trecho in ("references/curator.md", "`sdd/invariants.md`", "--validar-inv", "--cruzar", "--conferir-bloco"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, skill)


class RestauracaoDoDefine(Sandbox):
    """R1@codex da rodada 1: a sequência escrita no passo 11, executada, com um link no nome intermediário."""

    def sequencia(self):
        passo = ler(".agents/skills/sdd-define/SKILL.md")
        m = re.search(r"`(rm -f sdd/features/DEFINE_<F>\.md\.restaurando && .*?)`", passo)
        self.assertIsNotNone(m)
        return m.group(1).replace("<F>", "X")

    def monta(self):
        p = self.tmp / "p"
        (p / "sdd/features").mkdir(parents=True)
        self.escreve(p, "sdd/features/DEFINE_X.md", "mexido\n")
        self.t = self.escreve(self.tmp, "t/DEFINE.antes", "original\n").parent
        return p

    def roda_seq(self, p, t=None):
        env = dict(self.env, T=str(t if t is not None else self.t))
        return self.roda([BASH, "-c", self.sequencia()], p, env)

    def test_restaura(self):
        p = self.monta()
        rc, out, err = self.roda_seq(p)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual((p / "sdd/features/DEFINE_X.md").read_text(encoding="utf-8"), "original\n")

    def test_link_no_intermediario_nao_escreve_no_alvo(self):
        p = self.monta()
        vitima = self.escreve(p, "vitima.txt", "vitima\n")
        os.symlink(str(vitima), str(p / "sdd/features/DEFINE_X.md.restaurando"))
        rc, out, err = self.roda_seq(p)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(vitima.read_text(encoding="utf-8"), "vitima\n")
        self.assertFalse(os.path.islink(str(p / "sdd/features/DEFINE_X.md")))
        self.assertEqual((p / "sdd/features/DEFINE_X.md").read_text(encoding="utf-8"), "original\n")

    def test_link_no_lugar_do_define_nao_escreve_no_alvo(self):
        p = self.monta()
        vitima = self.escreve(p, "vitima.txt", "vitima\n")
        (p / "sdd/features/DEFINE_X.md").unlink()
        os.symlink(str(vitima), str(p / "sdd/features/DEFINE_X.md"))
        self.assertEqual(self.roda_seq(p)[0], 0)
        self.assertEqual(vitima.read_text(encoding="utf-8"), "vitima\n")
        self.assertFalse(os.path.islink(str(p / "sdd/features/DEFINE_X.md")))

    def test_copia_inalcancavel_nao_apaga_o_define(self):
        p = self.monta()
        rc, _, _ = self.roda_seq(p, self.tmp / "nao-existe")
        self.assertNotEqual(rc, 0)
        self.assertEqual((p / "sdd/features/DEFINE_X.md").read_text(encoding="utf-8"), "mexido\n")


class NovaSessao(unittest.TestCase):
    def test_chama_o_script_e_repassa_em_palavras(self):
        skill = ler(".agents/skills/sdd-new-session/SKILL.md")
        i = skill.index("4. Na pasta nova: a preparação")
        item = skill[i:skill.index("5. Abra no editor.")]
        self.assertLess(skill.index("git worktree add <pasta das frentes>"), i)
        self.assertIn("<pasta das skills>/sdd-new-session/scripts/copiar-docs.sh", item)
        self.assertIn("rodado do checkout principal", item)
        for trecho in ("scripts/copiar-docs.sh", "**idêntico**", "`PARECIDO`", "`NAO_COPIADO`", "`NADA A COPIAR`", "Qualquer outro exit"):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, item)


class Handoff(unittest.TestCase):
    SECOES = ("## Eventos", "## Recomendações", "## Veredito", "## Setup", "## Tarefas", "## Ship")

    def test_as_6_secoes_no_molde_e_na_fixture_antes_do_prompt(self):
        for rel in ("sdd/templates/HANDOFF_TEMPLATE.md", "sdd/fixtures/handoff/HANDOFF_COMPLETO.md"):
            texto = ler(rel)
            fim = texto.index("## Prompt de retomada")
            for s in self.SECOES:
                with self.subTest(arquivo=rel, secao=s):
                    self.assertIn("\n" + s + "\n", texto[:fim])

    def test_tarefas_numeradas_e_ship_com_limpeza(self):
        molde = ler("sdd/templates/HANDOFF_TEMPLATE.md")
        tarefas = molde[molde.index("## Tarefas"):molde.index("## Ship")]
        self.assertIn("1. **", tarefas)
        self.assertIn("Pronto quando:", tarefas)
        self.assertIn("**Limpar:**", molde[molde.index("## Ship"):])

    def test_a_skill_explica_as_secoes(self):
        self.assertIn("`## Eventos`, `## Recomendações`, `## Veredito`, `## Setup`, `## Tarefas` e\n  `## Ship`",
                      ler(".agents/skills/sdd-handoff/SKILL.md"))


class Pacote(unittest.TestCase):
    def test_gatilho_de_release_cobre_as_invariantes(self):
        self.assertIn("- 'sdd/invariants.md'", ler(".github/workflows/release.yml"))

    def test_scripts_novos_no_piso(self):
        for rel in NOVOS:
            with self.subTest(script=rel):
                self.assertIsNone(re.search(r"mapfile|declare -A|\$\{[a-zA-Z_]+\^\^", ler(rel)))

    def test_testes_novos_existem(self):
        for nome in ("playbook_curator", "playbook_invariantes", "curadoria_bloco", "copiar_docs", "f14_textos", "apoio_ambiente"):
            with self.subTest(nome=nome):
                self.assertTrue((RAIZ / "tests" / ("test_%s.py" % nome)).is_file())

    def test_versoes_e_linha_de_identificacao(self):
        for skill, versao in (("sdd-playbook", "2.2.0"), ("sdd-release", "2.12.0"), ("sdd-new-session", "1.6.1"),
                              ("sdd-handoff", "2.2.0"), ("sdd-define", "2.6.1")):
            texto = ler(".agents/skills/%s/SKILL.md" % skill)
            with self.subTest(skill=skill):
                self.assertIn('version: "%s"' % versao, texto)
                self.assertIn('updated: "2026-11"', texto)
                self.assertIn("`%s v%s · nov/2026 ·" % (skill, versao), texto)

    def test_roadmap_e_doc_novo(self):
        for rel in ("README.md", "README.pt-BR.md"):
            with self.subTest(arquivo=rel):
                self.assertIn("playbook-curation.md", ler(rel))
        self.assertIn("playbook-curator.sh", ler("docs/cli-conventions.md"))
        self.assertIn("playbook-curation.md", ler("docs/pt-BR/guia-do-aluno.md"))
