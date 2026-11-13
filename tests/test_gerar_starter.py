"""F17 (AT-001 a AT-007, AT-010): scripts/gerar-starter.py e a trava check-gerado.py que ele grava no starter.

O Open de teste é um repositório temporário com as pastas que o gerador lê, copiadas da árvore e marcadas com uma
tag (o Verify Gate roda a suíte numa cópia sem .git: nada aqui depende do .git do pacote). O starter de teste é
uma réplica mínima da v1.5.16: a infra de scripts/starter/raiz, as 8 skills congeladas e as 8 geradas que já
existiam lá, com as versões reais daquela tag.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import sys
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

PY = sys.executable
URL_STARTER = "https://github.com/robertodiasduarte/sdd-starter/releases/latest"
LISTA = [ln.strip() for ln in (RAIZ / "scripts/starter/lista.txt").read_text(encoding="utf-8").splitlines()
         if ln.strip() and not ln.startswith("#")]
CONGELADAS = {"sdd-brainstorm": "1.1.0", "sdd-define": "1.2.0", "sdd-design": "1.1.0", "sdd-build": "1.2.0",
              "sdd-handoff": "1.1.0", "sdd-release": "1.3.0", "sdd-governanca": "1.0.1", "ux-review-builder": "1.4.0"}
# as geradas que já estavam no starter v1.5.16, com a versão de lá (as outras 2 são novas)
NO_STARTER = {"sdd-checar-ambiente": "1.2.0", "sdd-iniciar-repo": "1.1.0", "sdd-higiene-dado": "1.1.0",
              "sdd-new-session": "1.3.0", "sdd-kb": "2.1.0", "sdd-auditoria-harness": "1.0.0",
              "sdd-prompt-builder": "1.0.0", "sdd-engenharia-reversa-saas": "1.1.0"}
COM_REFERENCIA = {"sdd-brainstorm", "sdd-define", "sdd-design", "sdd-build", "sdd-handoff", "ux-review-builder"}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def skill_minima(nome: str, versao: str, updated: str = "2026-10") -> str:
    ano, mes = updated.split("-")
    return ("---\nname: %s\ndescription: Skill de teste.\nmetadata:\n  version: \"%s\"\n  updated: \"%s\"\n---\n\n"
            "`%s v%s · %s/%s · versão atual: %s`\n\n## Como falar com o aluno\n\nTexto.\n"
            % (nome, versao, updated, nome, versao, MESES[int(mes) - 1], ano, URL_STARTER))


def arvore(pasta: Path) -> dict[str, str]:
    return {p.relative_to(pasta).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(pasta.rglob("*")) if p.is_file() and ".git" not in p.relative_to(pasta).parts}


class Base(Sandbox):
    TAG = "v9.9.9"

    def setUp(self):
        super().setUp()
        self.open = self.repo("open")
        sem_cache = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
        for rel in (".agents/skills", "sdd/templates", "scripts/starter"):
            shutil.copytree(str(RAIZ / rel), str(self.open / rel), ignore=sem_cache)
        shutil.copy2(str(RAIZ / "scripts/gerar-starter.py"), str(self.open / "scripts/gerar-starter.py"))
        self.commit(self.open, "open")
        self.git(self.open, "tag", self.TAG)
        self.starter = self.replica("starter")

    def replica(self, nome: str) -> Path:
        s = self.repo(nome)
        raiz = RAIZ / "scripts/starter/raiz"
        for rel in ("scripts/check-versions.py", "scripts/publish-check.sh", "scripts/package.sh"):
            shutil.copy2(str(raiz / rel), str(s / rel)) if (s / "scripts").is_dir() else (
                (s / "scripts").mkdir(), shutil.copy2(str(raiz / rel), str(s / rel)))
        self.escreve(s, "README.md", "# SDD Starter (versão antiga)\n")
        self.escreve(s, "LICENSE", "MIT\n")
        self.escreve(s, "docs/quickstart.md", "# Quickstart\n")
        self.escreve(s, "exemplos/baixar-nfse/README.md", "# Exemplo\n")
        self.escreve(s, "tests/test_vazio.py", "import unittest\n")
        for nome, versao in {**CONGELADAS, **NO_STARTER}.items():
            self.escreve(s, "skills/%s/SKILL.md" % nome, skill_minima(nome, versao))
            if nome in COM_REFERENCIA or nome == "sdd-kb":
                self.escreve(s, "skills/%s/references/como-falar.md" % nome, "# Como falar\n")
        self.commit(s, "v1.5.16")
        self.git(s, "tag", "v1.5.16")
        return s

    def gerar(self, destino: Path | None = None, tag: str | None = None, script: Path | None = None):
        return self.roda([PY, "-B", script or self.open / "scripts/gerar-starter.py", "--tag", tag or self.TAG,
                          destino or self.starter], self.tmp)

    def reetiquetar(self) -> None:
        self.commit(self.open, "muda")
        self.git(self.open, "tag", "-f", self.TAG)

    def limpo(self, repo: Path) -> bool:
        return self.git(repo, "status", "--porcelain", "--untracked-files=all").strip() == ""


class Gera(Base):
    def test_at001_gera_as_10_e_nao_toca_no_resto(self):
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: GERADO", out)
        depois = arvore(self.starter)
        for rel, h in antes.items():
            dono = rel.split("/")[0] in ("scripts", ".github") or rel == "README.md" or \
                (rel.startswith("skills/") and rel.split("/")[1] in LISTA)
            if not dono:
                with self.subTest(rel=rel):
                    self.assertEqual(depois.get(rel), h)
        for skill in LISTA:
            with self.subTest(skill=skill):
                self.assertTrue((self.starter / "skills" / skill / "GERADO.txt").is_file())
        for rel in ("GERADO.txt", ".gitattributes", "scripts/check-gerado.py", ".github/workflows/ci.yml",
                    ".github/workflows/auto-release.yml", ".github/workflows/release.yml"):
            with self.subTest(rel=rel):
                self.assertTrue((self.starter / rel).is_file())
        self.assertNotIn("versão antiga", (self.starter / "README.md").read_text(encoding="utf-8"))

    def test_at003_cada_skill_gerada(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for skill in LISTA:
            d = self.starter / "skills" / skill
            s = (d / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill):
                fim_fm = s.index("\n---\n", 4) + 5
                self.assertTrue(s[fim_fm:].startswith("<!-- GENERATED pelo sdd-open"), s[fim_fm:fim_fm + 80])
                self.assertIn("· versão atual: %s`" % URL_STARTER, s)
                self.assertIn("## Quando migrar para o SDD Open", s[-1200:])
                self.assertNotIn("### Fluxo encadeado", s)
                self.assertNotIn("v9.9.9", s)   # a tag só no GERADO.txt da raiz (revisão do DESIGN, item 2)
                y = (d / "agents/openai.yaml").read_text(encoding="utf-8")
                self.assertTrue(y.startswith('interface:\n  display_name: "'), y)
                for p in d.rglob("*"):
                    if p.is_file() and p.suffix in (".md", ".py", ".sh", ".json"):
                        self.assertNotIn("sdd-open/releases/latest", p.read_text(encoding="utf-8"), str(p))
                listados = {}
                for ln in (d / "GERADO.txt").read_text(encoding="utf-8").splitlines():
                    if ln and not ln.startswith("#"):
                        h, rel = ln.split("  ", 1)
                        listados[rel] = h
                reais = {k: v for k, v in arvore(d).items() if k != "GERADO.txt"}
                self.assertEqual(listados, reais)
        # moldes de sdd/templates/ vão para dentro, já sem o encadeamento
        self.assertTrue((self.starter / "skills/sdd-checar-ambiente/references/PERGUNTA_DECISAO.md").is_file())
        self.assertFalse((self.starter / "skills/sdd-checar-ambiente/references/FLUXO_ENCADEADO.md").exists())
        self.assertIn("<pasta desta skill>/references/PERGUNTA_DECISAO.md",
                      (self.starter / "skills/sdd-checar-ambiente/SKILL.md").read_text(encoding="utf-8"))
        self.assertIn("v9.9.9", (self.starter / "GERADO.txt").read_text(encoding="utf-8"))

    def test_regra_de_pasta_so_no_markdown_e_o_par_que_define_a_pasta_fica(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        hook_p = self.starter / "skills/sdd-higiene-dado/scripts/pre-commit.sh"
        hook = hook_p.read_text(encoding="utf-8")
        # num script, o marcador só pode estar em mensagem entre aspas, nunca num comando que o shell executa
        com_marcador = [ln for ln in hook.splitlines() if "<pasta" in ln]
        self.assertEqual(len(com_marcador), 1, com_marcador)
        self.assertTrue(com_marcador[0].strip().startswith("DESINSTALAR='"), com_marcador)
        rc, out, err = self.roda([BASH, "-n", hook_p], self.tmp)
        self.assertEqual(rc, 0, out + err)
        s = (self.starter / "skills/sdd-iniciar-repo/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("`.claude/skills/sdd-iniciar-repo/` ou\n`.agents/skills/sdd-iniciar-repo/`", s)

    def test_aval1_kb_gerada_sem_caminho_nem_sync_do_open(self):
        # avaliador, ciclo 1, achado 1: o validate_kb.py gerado mandava rodar .agents/skills/sdd-kb/…, que não existe
        # numa instalação do Claude Code (.claude/skills/sdd-kb)
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for skill in ("sdd-kb", "sdd-engenharia-reversa-saas", "sdd-higiene-dado"):
            for p in (self.starter / "skills" / skill).rglob("*"):
                if p.is_file() and p.name not in ("CHANGELOG.md", "GERADO.txt"):
                    with self.subTest(arquivo=str(p.relative_to(self.starter))):
                        tx = p.read_text(encoding="utf-8")
                        self.assertNotIn("`sync`", tx)
                        sem_par = re.sub(r"\.claude/skills/(sdd-[a-z0-9-]+)/`\s+ou\s+`\.agents/skills/\1/", "", tx)
                        self.assertNotIn(".agents/skills/%s/" % skill, sem_par)
        v = (self.starter / "skills/sdd-kb/scripts/validate_kb.py").read_text(encoding="utf-8")
        self.assertIn("python3 <pasta da skill sdd-kb>/scripts/kb_normativo.py rule-map", v)

    def test_at005_duas_geracoes_iguais_byte_a_byte(self):
        outro = self.replica("starter2")
        for destino in (self.starter, outro):
            rc, out, err = self.gerar(destino)
            self.assertEqual(rc, 0, out + err)
        self.assertEqual(arvore(self.starter), arvore(outro))

    def test_gerar_de_novo_a_mesma_tag_nao_muda_nada(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.commit(self.starter, "1a geracao")
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertTrue(self.limpo(self.starter))

    def test_r6_ds_store_no_destino_nao_conta_como_mudanca(self):
        # revisão, rodada 6, R1: o Finder cria .DS_Store (ignorado pelo git); o gerador não pode pedir versão nova por ele
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.commit(self.starter, "1a geracao")
        (self.starter / "skills/sdd-kb/.DS_Store").write_bytes(b"\x00\x01finder")
        self.escreve(self.starter, ".gitignore", ".DS_Store\n")
        self.commit(self.starter, "gitignore")
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)

    def test_r2_arquivo_que_saiu_da_semente_sai_do_destino(self):
        # revisão, rodada 1, R2: scripts/ e .github/workflows/ são inteiros do gerador; um arquivo antigo que ficasse
        # lá seria "sobra" na trava e pediria remendo à mão no starter
        self.escreve(self.starter, "scripts/velho.sh", "echo velho\n")
        self.escreve(self.starter, ".github/workflows/velho.yml", "name: velho\n")
        self.commit(self.starter, "infra antiga")
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        self.assertFalse((self.starter / "scripts/velho.sh").exists())
        self.assertFalse((self.starter / ".github/workflows/velho.yml").exists())
        rc, out, err = self.roda([PY, "-B", "scripts/check-gerado.py"], self.starter)
        self.assertEqual(rc, 0, out + err)

    def test_r1_testes_de_skill_sem_nenhuma_pasta_tests_nao_quebram(self):
        for wf in ("ci.yml", "auto-release.yml"):
            t = (RAIZ / "scripts/starter/raiz/.github/workflows" / wf).read_text(encoding="utf-8")
            with self.subTest(wf=wf):
                self.assertIn('[ -d "$t" ] || continue', t)

    def test_at007_o_starter_passa_nas_checagens_dele(self):
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        for nome, args in (("publish-check", [BASH, "scripts/publish-check.sh"]),
                           ("check-versions", [PY, "-B", "scripts/check-versions.py", "--base", "v1.5.16"]),
                           ("kb gate", [BASH, "skills/sdd-kb/scripts/gate.sh"]),
                           ("check-gerado", [PY, "-B", "scripts/check-gerado.py"])):
            with self.subTest(passo=nome):
                rc, out, err = self.roda(args, self.starter)
                self.assertEqual(rc, 0, out + err)


class Recusa(Base):
    def nada_gravado(self, rc: int, esperado: int, out: str, err: str, antes: dict) -> None:
        self.assertEqual(rc, esperado, out + err)
        self.assertIn("NADA FOI GRAVADO", out)
        self.assertEqual(arvore(self.starter), antes)

    def test_at002_tag_inexistente(self):
        antes = arvore(self.starter)
        rc, out, err = self.gerar(tag="v0.0.0-nao-existe")
        self.nada_gravado(rc, 64, out, err, antes)
        self.assertIn("a tag v0.0.0-nao-existe não existe", out)

    def test_at002_destino_sujo_ou_sem_a_forma_do_starter(self):
        self.escreve(self.starter, "rascunho.txt", "x\n")
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.nada_gravado(rc, 64, out, err, antes)
        outra = self.repo("nao-e-starter")
        rc, out, err = self.gerar(outra)
        self.assertEqual(rc, 64, out + err)
        self.assertIn("não tem a forma do sdd-starter", out)

    def test_at002_troca_que_nao_casa_exatamente_uma_vez(self):
        self.escreve(self.open, "scripts/starter/trocas/sdd-loop-builder.md",
                     "## SKILL.md\n<<<< antes\ntrecho que não existe no Open\n====\nnovo\n>>>> depois\n")
        self.reetiquetar()
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.nada_gravado(rc, 65, out, err, antes)
        self.assertIn("sdd-loop-builder.md, bloco 1: o trecho casou 0 vez(es) em SKILL.md", out)

    def test_at002_skill_sem_linha_no_openai_tsv(self):
        tsv = self.open / "scripts/starter/openai.tsv"
        tsv.write_text("".join(ln for ln in tsv.read_text(encoding="utf-8").splitlines(True)
                               if not ln.startswith("sdd-kb\t")), encoding="utf-8")
        self.reetiquetar()
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.nada_gravado(rc, 65, out, err, antes)
        self.assertIn("sdd-kb não tem linha em scripts/starter/openai.tsv", out)

    def test_at002_lint_do_init_acha_citacao(self):
        p = self.open / ".agents/skills/sdd-loop-builder/SKILL.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nRode `bash sdd/bin/verify-gate.sh`.\n", encoding="utf-8")
        self.reetiquetar()
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.nada_gravado(rc, 65, out, err, antes)
        self.assertIn("skills/sdd-loop-builder/SKILL.md:", out)
        self.assertIn("sdd/bin/", out)

    def test_at007_versao_que_nao_sobe_reprova_antes_de_gravar(self):
        # caso vermelho do version gate do starter: a gerada mudou e ficou com a mesma versão que lá
        p = self.open / ".agents/skills/sdd-engenharia-reversa-saas/SKILL.md"
        t = p.read_text(encoding="utf-8")
        v = t.split('version: "', 1)[1].split('"', 1)[0]
        p.write_text(t.replace('version: "%s"' % v, 'version: "1.1.0"').replace(
            "sdd-engenharia-reversa-saas v%s ·" % v, "sdd-engenharia-reversa-saas v1.1.0 ·"), encoding="utf-8")
        self.reetiquetar()
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.nada_gravado(rc, 65, out, err, antes)
        self.assertIn("sdd-engenharia-reversa-saas: a cópia gerada mudou e a versão não subiu", out)

    def test_r6_tag_anterior_ao_gerador_diz_a_causa(self):
        # revisão, rodada 6, R2: uma tag sem o gerador dava traceback com exit 1
        g = self.open / "scripts/gerar-starter.py"
        guardado = g.read_bytes()
        self.git(self.open, "rm", "-q", "-r", "scripts")
        self.commit(self.open, "antes da F17")
        self.git(self.open, "tag", "v0.1.0")
        g.parent.mkdir(parents=True, exist_ok=True)
        g.write_bytes(guardado)
        antes = arvore(self.starter)
        rc, out, err = self.gerar(tag="v0.1.0")
        self.assertEqual(rc, 64, out + err)
        self.assertIn("não tem o gerador do starter", out)
        self.assertNotIn("Traceback", out + err)
        self.assertEqual(arvore(self.starter), antes)

    def test_gerador_diferente_do_da_tag(self):
        g = self.open / "scripts/gerar-starter.py"   # mudança não commitada: a tag tem o gerador antigo
        g.write_text(g.read_text(encoding="utf-8") + "\n# mudou\n", encoding="utf-8")
        antes = arvore(self.starter)
        rc, out, err = self.gerar()
        self.assertEqual(rc, 64, out + err)
        self.assertIn("difere do que está na tag", out)
        self.assertIn("worktree add", out)   # revisão, rodada 1, R5: rodar de /tmp tirava o gerador do repositório
        self.assertEqual(arvore(self.starter), antes)


class Lint(Base):
    def test_aval1_lint_pega_caminho_da_skill_gerada_fora_do_par(self):
        pasta = self.tmp / "l"
        self.escreve(pasta, "sdd-kb/scripts/x.py", "print('rode python3 .agents/skills/sdd-kb/scripts/kb_normativo.py')\n")
        self.escreve(pasta, "sdd-kb/SKILL.md", "Use `.agents/skills/sdd-kb/assets/`.\n")
        self.escreve(pasta, "sdd-kb/references/ok.md", "A pasta: `.claude/skills/sdd-kb/` ou\n`.agents/skills/sdd-kb/`, no projeto.\n")
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", pasta], self.tmp)
        self.assertEqual(rc, 65, out + err)
        self.assertIn("sdd-kb/scripts/x.py:1", out)
        self.assertIn("sdd-kb/SKILL.md:1", out)
        self.assertNotIn("ok.md", out)   # o par que define a pasta é texto certo
        # revisão, rodada 5, R2: o par só isenta skill gerada; o de uma skill que o starter não recebe reprova
        self.escreve(pasta, "sdd-kb/references/fora.md", "Veja `.claude/skills/sdd-playbook/` ou\n`.agents/skills/sdd-playbook/`.\n")
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", pasta], self.tmp)
        self.assertIn("sdd-kb/references/fora.md:2", out)

    def test_r4_aceite_nao_isenta_outra_citacao_na_mesma_linha(self):
        # revisão, rodada 2, R4: o aceite de uma citação não pode calar outra citação na mesma linha
        pasta = self.tmp / "l2"
        aceito = '[ -f "${ROOT}/sdd/hooks/pre-commit" ] && grep -qF "${MARCA_DISPATCHER}" "${ROOT}/sdd/hooks/pre-commit"'
        self.escreve(pasta, "skills/sdd-higiene-dado/scripts/alarme.sh", aceito + " && bash sdd/bin/x.sh\n")
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", pasta], self.tmp)
        self.assertEqual(rc, 65, out + err)
        self.assertIn("alarme.sh:1: sdd/bin/", out)
        self.escreve(pasta, "skills/sdd-higiene-dado/scripts/alarme.sh", aceito + "\n")
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", pasta], self.tmp)
        self.assertEqual(rc, 0, out + err)
        # rodada 3, R2: o mesmo trecho aceito duas vezes na linha cobre as duas ocorrências
        self.escreve(pasta, "skills/sdd-higiene-dado/scripts/alarme.sh", aceito + " || " + aceito + "\n")
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", pasta], self.tmp)
        self.assertEqual(rc, 0, out + err)

    def test_at004_a_copia_crua_reprova_e_a_gerada_passa(self):
        crua = self.tmp / "crua"
        for skill in LISTA:
            shutil.copytree(str(RAIZ / ".agents/skills" / skill), str(crua / skill))
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", crua], self.tmp)
        self.assertEqual(rc, 65, out + err)
        self.assertIn("sdd/bin/", out)
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)
        rc, out, err = self.roda([PY, "-B", RAIZ / "scripts/gerar-starter.py", "--lint", self.starter], self.tmp)
        self.assertEqual(rc, 0, out + err)


class Trava(Base):
    def setUp(self):
        super().setUp()
        rc, out, err = self.gerar()
        self.assertEqual(rc, 0, out + err)

    def trava(self):
        return self.roda([PY, "-B", "scripts/check-gerado.py"], self.starter)

    def test_at006_tudo_igual_sai_0(self):
        rc, out, err = self.trava()
        self.assertEqual(rc, 0, out + err)
        self.assertIn("RESULTADO: VERDE", out)

    def test_at006_cada_mudanca_a_mao_sai_1(self):
        casos = {
            "mudou": lambda s: (s / "skills/sdd-kb/SKILL.md").write_text("editado\n", encoding="utf-8"),
            "sobra": lambda s: (s / "skills/sdd-kb/extra.md").write_text("x\n", encoding="utf-8"),
            "falta": lambda s: (s / "skills/sdd-kb/references/como-falar.md").unlink(),
            "infra mudou": lambda s: (s / ".github/workflows/ci.yml").write_text("x\n", encoding="utf-8"),
            "infra sobra": lambda s: (s / "scripts/meu.sh").write_text("x\n", encoding="utf-8"),
            "GERADO da skill apagado": lambda s: (s / "skills/sdd-kb/GERADO.txt").unlink(),
            "GERADO da raiz apagado": lambda s: (s / "GERADO.txt").unlink(),
            "skill gerada apagada": lambda s: shutil.rmtree(str(s / "skills/sdd-kb")),
        }
        for nome, mexe in casos.items():
            with self.subTest(caso=nome):
                self.commit(self.starter, "gerado") if not self.limpo(self.starter) else None
                mexe(self.starter)
                rc, out, err = self.trava()
                self.assertEqual(rc, 1, out + err)
                self.assertIn("RESULTADO: ARQUIVO GERADO MUDOU AQUI", out)
                self.git(self.starter, "checkout", "--", ".")
                self.git(self.starter, "clean", "-fdq")

    def test_at006_gerado_ilegivel_sai_64(self):
        (self.starter / "skills/sdd-kb/GERADO.txt").write_text("isto não é sha\n", encoding="utf-8")
        rc, out, err = self.trava()
        self.assertEqual(rc, 64, out + err)

    def test_at006_os_workflows_rodam_a_trava_antes_dos_testes(self):
        for wf in ("ci.yml", "auto-release.yml", "release.yml"):
            t = (self.starter / ".github/workflows" / wf).read_text(encoding="utf-8")
            with self.subTest(wf=wf):
                self.assertIn("run: python3 scripts/check-gerado.py", t)
                self.assertLess(t.index("check-gerado.py"), t.index("Content safety gate"))


class ReadmeEInit(Base):
    def test_readme_sem_ambiente_md(self):
        # revisão, rodada 1, R4: a new-session gerada é a do Open, que não grava sdd/ambiente.md
        self.assertNotIn("ambiente.md", (RAIZ / "scripts/starter/raiz/README.md").read_text(encoding="utf-8"))

    def test_readme_cita_toda_skill_gerada(self):
        r = (RAIZ / "scripts/starter/raiz/README.md").read_text(encoding="utf-8")
        for skill in LISTA:
            with self.subTest(skill=skill):
                self.assertEqual(r.count("[`%s`](skills/%s/)" % (skill, skill)), 2)   # PT e EN

    def test_at010_o_init_nao_copia_scripts(self):
        # o init copia de sdd/ só estas pastas e arquivos (sdd_faltantes) e de .agents/skills; scripts/ nunca
        sh = (RAIZ / "bin/sdd-open.sh").read_text(encoding="utf-8")
        linha = next(ln for ln in sh.splitlines() if "find templates bin hooks review patterns" in ln)
        self.assertIn('cd "${PKG}/sdd"', linha)
        self.assertNotIn("scripts", linha)
