"""Textos da F14_DRIVE (DEFINE AT-019 a AT-021, AT-027, AT-031, AT-035, AT-036): nomes e ordem iguais em todos os lugares, e o
que saiu da skill saiu mesmo. Efeito é provado em test_drive, test_deploy_do_sha e test_sdd_archive; aqui só o combinado."""
from __future__ import annotations

import re
import unittest

from apoio import BASH, RAIZ, Sandbox
from test_drive import FRASES


def ler(rel):
    return (RAIZ / rel).read_text(encoding="utf-8")


SKILL = ler(".agents/skills/sdd-drive/SKILL.md")
COMO = ler(".agents/skills/sdd-drive/references/como-falar.md")
EXECUTOR = ler(".agents/skills/sdd-drive/references/executor.md")
SCRIPT = ler("sdd/bin/sdd-drive.sh")
CONTRATOS = ler("sdd/WORKFLOW_CONTRACTS.yaml")
RELEASE = ler(".agents/skills/sdd-release/SKILL.md")
RAIO = ler(".agents/skills/sdd-release/references/raio-de-impacto.md")
DOCS = (ler("docs/sdd-drive.md"), ler("docs/pt-BR/sdd-drive.md"))
ITEM10 = RELEASE[RELEASE.index("10. **Verificar — pelo commit publicado"):RELEASE.index("11. **Changelog:**")]
PASSO0B = RELEASE[RELEASE.index("**0b. Raio de impacto"):RELEASE.index("**0c. Segurança")]
ACOES = ("ESPERAR", "DESIGN", "REVISAO_DESIGN", "RODADA", "CORRIGIR", "COMMITAR", "VERIFICAR", "AVALIAR_E_RELATAR")


def bloco(nome):
    m = re.search(r"(?ms)^%s:\n(.*?)(?=^\S)" % nome, CONTRATOS + "\nfim:\n")
    return m.group(1)


def lista(nome_bloco, chave):
    m = re.search(r'(?m)^  %s:\n((?:    - [^\n]*\n)+)' % chave, bloco(nome_bloco))
    return re.findall(r'"(.+?)"', m.group(1))


class MesmosNomes(unittest.TestCase):
    def test_12_motivos_nos_4_lugares(self):
        self.assertEqual(len(FRASES), 12)
        self.assertEqual(sorted(lista("sdd_drive", "motivos")), sorted(FRASES))
        for nome in FRASES:
            with self.subTest(motivo=nome):
                self.assertIn('"%s"' % nome, SCRIPT)
                self.assertIn("| `%s` |" % nome, SKILL)
                self.assertIn(FRASES[nome], SCRIPT)
                for doc in DOCS:
                    self.assertIn("| `%s` |" % nome, doc)
                    self.assertIn(FRASES[nome], doc)

    def test_exits_da_tabela_batem_com_o_script(self):
        for nome, exitc in re.findall(r"(?m)^\| `([a-z-]+)` \| (\d+) \|", SKILL):
            with self.subTest(motivo=nome):
                self.assertRegex(SCRIPT, r'(?s)"%s": \(.{0,160}?, %s, "' % (nome, exitc))
        for nome, exitc in (("concluido", "0"), ("continuar", "10"), ("parada", "20"), ("aguardando_humano", "40"), ("falha", "2"), ("uso", "64")):
            self.assertIn('%s: "%s"' % (nome, exitc), bloco("sdd_drive"))

    def test_acoes_iguais_no_script_na_skill_no_contrato_e_nos_docs(self):
        self.assertEqual(lista("sdd_drive", "acoes"), list(ACOES))
        for a in ACOES:
            with self.subTest(acao=a):
                self.assertIn('"%s":' % a, SCRIPT)
                self.assertIn("| `%s` |" % a, SKILL)
                for doc in DOCS:
                    self.assertIn("`%s`" % a, doc)

    def test_campos_do_brief_iguais_ao_contrato(self):
        for campo in lista("sdd_drive", "campos"):
            self.assertIn(campo + ":", EXECUTOR)
        self.assertIn("<<<RODADA", EXECUTOR)
        self.assertIn("<<<RODADA", SKILL)
        for campo in lista("raio_de_impacto", "campos"):
            self.assertIn(campo + ":", RAIO)
        self.assertIn("<<<RAIO", RAIO)


class Skill(unittest.TestCase):
    def test_abre_com_o_limite_e_a_barreira(self):
        self.assertIn("`até N rodadas`", SKILL)
        self.assertIn("`paro antes de publicar`", SKILL)
        self.assertIn("**O drive nunca publica.**", SKILL)

    def test_o_teste_final_longo_vai_para_o_fundo(self):
        self.assertIn("verificar <DEFINE> --fundo", SKILL)
        self.assertIn("limite de um comando", SKILL)

    def test_as_2_perguntas_com_marca_e_opcoes(self):
        d4 = COMO[COMO.index("[D4 · limite de tentativas]"):COMO.index("## A pergunta do teste final alterado")]
        for op in ("**corrigir o DESIGN e seguir** (recomendado)", "**dar mais 1 rodada**", "**parar aqui**", "**não sei**"):
            self.assertIn(op, d4)
        d2 = COMO[COMO.index("[D2 · muda o produto]"):COMO.index("## Exemplo de resposta completa")]
        for op in ("**voltar o comando antigo** (recomendado)", "**aceitar o novo**", "**não sei**"):
            self.assertIn(op, d2)
        self.assertIn("era `npm test`", d2)
        self.assertIn("`[D4 · limite de tentativas]`", SKILL)
        self.assertIn("`[D2 · muda o produto]`", SKILL)

    def test_rotina_vira_recibo_e_o_resto_e_perguntado(self):
        self.assertIn("`[auto · de rotina]` vale a", SKILL)
        self.assertIn("sdd-drive.sh recibo", SKILL)
        for marca in ("[D1 · não se desfaz]", "[D3 · muda a regra do método]", "[D5 · provas em conflito]"):
            self.assertIn(marca, SKILL)
        self.assertIn("nada muda em `flow.autonomous`", SKILL)

    def test_sem_subagente_grava_o_brief_e_para(self):
        self.assertIn("sdd/reports/briefs/BRIEF_executor-drive_{F}.md", SKILL)
        self.assertIn("sdd-drive.sh aguardar <DEFINE> executor-drive", SKILL)

    def test_formato_da_anotacao_de_erro(self):
        self.assertIn("` — `", EXECUTOR)

    def test_executor_nao_roda_o_gate_nem_publica(self):
        self.assertIn("**Não rode o Verify Gate do DEFINE**", EXECUTOR)
        self.assertIn("**Nunca publique:**", EXECUTOR)


class Despachar(Sandbox):
    def test_parada_do_executor(self):
        r = self.repo()
        self.copia("sdd/bin/sdd-fluxo.sh", r)
        self.escreve(r, "brief.md", "x\n")
        rc, out, _ = self.roda([BASH, "sdd/bin/sdd-fluxo.sh", "despachar", "executor-drive", "F", "brief.md"], r)
        self.assertEqual(rc, 40)
        for trecho in ("<<<RODADA", "PROGRESS_F.md", "nada foi publicado"):
            self.assertIn(trecho, out)


class Raio(unittest.TestCase):
    def test_passo_na_ordem(self):
        marcos = ("Liste, do diff, as superfícies", "um agente fresco com o brief `references/raio-de-impacto.md`", "em paralelo quando o agente tem subagente",
                  "sem subagente, na própria sessão", "**não modificados**", "`sdd/invariants.md`", "`arquivo:linha`", "invariantes: ausente", "declare a passada pulada")
        corrido = " ".join(PASSO0B.split())
        pos = [corrido.index(m) for m in marcos]
        self.assertEqual(pos, sorted(pos))
        self.assertEqual(corrido.count("**crítico**"), 1)


class Item10(unittest.TestCase):
    def test_chama_o_script_e_mapeia_os_exits(self):
        self.assertIn("bash sdd/bin/deploy-do-sha.sh --commit", ITEM10)
        for exitc in ("0", "2", "3", "4", "64"):
            self.assertIn("| `%s` |" % exitc, ITEM10)
        self.assertIn("`--teto 300`", ITEM10)
        self.assertIn("segundo plano", ITEM10)
        # R1 de Claude, rodada 5: repetir o 4 tem teto total, e "nenhum run" não se repete
        corrido = " ".join(ITEM10.split())
        self.assertIn("**no máximo 8 chamadas** (os mesmos 40 minutos)", corrido)
        self.assertIn('Saiu 4 com "não achei nenhum run"? Não repita', corrido)
        self.assertIn("{{DRIFT_CHECK_CMD}}", ITEM10)
        self.assertIn("smoke", ITEM10)
        self.assertIn("Verde não prova teste", ITEM10)

    def test_a_frase_que_para_a_repeticao_e_a_do_script(self):
        # R2 de Claude, rodada 6: a regra "não repita" só vale se o script imprime esta frase, e só no caso sem run
        deploy = ler("sdd/bin/deploy-do-sha.sh")
        frase = re.search(r'Saiu 4 com "([^"]+)"\? Não repita', " ".join(ITEM10.split())).group(1)
        linhas = [ln for ln in deploy.splitlines() if frase in ln]
        self.assertEqual(len(linhas), 1, "a frase sai de um lugar só")
        self.assertIn("fim(4,", linhas[0])
        # o outro lado: o 4 do redisparo sem run novo diz outra coisa, e a regra não o confunde com "push que não aciona"
        redisparo = [ln for ln in deploy.splitlines() if "pedi para repetir o deploy" in ln]
        self.assertEqual(len(redisparo), 1)
        self.assertIn("fim(4,", redisparo[0])
        self.assertNotIn(frase, redisparo[0])

    def test_a_logica_saiu_do_texto(self):
        for velho in ("gh run list", "merge-base --is-ancestor", "gh workflow run <arquivo> --ref"):
            self.assertNotIn(velho, ITEM10)

    def test_changelog_e_archive(self):
        self.assertIn("a regra do passo 11", RELEASE)
        self.assertIn("`git show origin/{default_branch}:CHANGELOG.md > CHANGELOG.md`", RELEASE)
        corrido = " ".join(RELEASE.split())
        self.assertIn("`python3 sdd/bin/sdd-archive.py` (simulação por padrão;", corrido)


class Config(unittest.TestCase):
    def test_slots(self):
        cfg = ler("sdd/config.example.yaml")
        self.assertRegex(cfg, r"(?m)^drive:\n  max_rounds: 3$")
        self.assertIn('  workflow: ""', cfg)
        self.assertIn('  transient_steps: ""', cfg)
        self.assertNotIn("max_tokens", cfg)


class Pacote(unittest.TestCase):
    NOVOS = ("sdd/bin/sdd-drive.sh", "sdd/bin/deploy-do-sha.sh", "sdd/bin/sdd-archive.py", ".agents/skills/sdd-drive/SKILL.md",
             ".agents/skills/sdd-drive/references/como-falar.md", ".agents/skills/sdd-drive/references/executor.md",
             ".agents/skills/sdd-release/references/raio-de-impacto.md", "docs/sdd-drive.md", "docs/pt-BR/sdd-drive.md",
             "tests/test_drive.py", "tests/test_deploy_do_sha.py", "tests/test_sdd_archive.py", "tests/test_f14_drive_textos.py")

    def test_arquivos_novos_no_manifest(self):
        manifest = ler("MANIFEST.txt").split("\n")
        for rel in self.NOVOS:
            with self.subTest(rel=rel):
                self.assertTrue((RAIZ / rel).is_file())
                self.assertIn(rel, manifest)

    def test_agents_tmpl_cita_as_19_skills(self):
        # L15 do ciclo 2
        tmpl = ler("AGENTS.md.tmpl")
        faltam = [p.name for p in sorted((RAIZ / ".agents/skills").iterdir()) if (p / "SKILL.md").is_file() and p.name not in tmpl]
        self.assertEqual(faltam, [])

    def test_versoes(self):
        self.assertIn('version: "1.0.0"', SKILL)
        self.assertIn("`sdd-drive v1.0.0 · nov/2026", SKILL)
        self.assertIn('version: "2.8.1"', RELEASE)

    def test_bash_32(self):
        for rel in ("sdd/bin/sdd-drive.sh", "sdd/bin/deploy-do-sha.sh", "sdd/bin/avaliador-guard.sh"):
            self.assertIsNone(re.search(r"mapfile|declare -A|\$\{[a-zA-Z_]+\^\^", ler(rel)), rel)
