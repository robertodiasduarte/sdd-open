"""F25 — skills duplicadas: o alerta do diagnóstico, o plano (--duplicadas) e a limpeza com autorização (--limpar).

Tudo roda com HOME, projeto e (quando importa) CODEX_HOME em pasta temporária: nenhum teste lê ou escreve a pasta
pessoal de quem roda. O npx é um falso (SDD_CHECAR_NPX) que reproduz o efeito medido no CLI skills 1.9.0
(sdd/reports/evidence/F25_SKILLS_DUPLICADAS/EXP-3-NPX.log): o `remove -g` apaga ~/.claude/skills/<nome> e
~/.agents/skills/<nome>, registradas ou não, e tira a linha do registro. Todo npx de teste RECUSA rodar com um HOME fora
da pasta temporária (exit 99) — a trava contra um HOME que não chegou exportado.
O CLI de verdade roda quando SDD_F25_SKILLS_CLI aponta para um cli.mjs (fonte local, sem rede).
Os agentes (claude, codex) também são falsos no PATH: o `codex --version` de verdade grava em ~/.codex/tmp.
Rodar: python3 -B -m unittest discover -s tests -p "test_f25_skills_duplicadas.py"
"""
from __future__ import annotations

import hashlib
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from apoio import RAIZ, WINDOWS, caminho_bash as B

SKILL = Path(os.environ.get("SDD_F25_SKILL_DIR") or (RAIZ / ".agents/skills/sdd-checar-ambiente"))
SCRIPT = SKILL / "scripts" / "checar.sh"
BASH = os.environ.get("SDD_TEST_BASH") or shutil.which("bash") or "bash"
URL = {"open": "https://github.com/robertodiasduarte/sdd-open/releases/latest",
       "starter": "https://github.com/robertodiasduarte/sdd-starter/releases/latest", "outra": ""}

NPX_FALSO = r"""#!/usr/bin/env bash
h="$(cd "${HOME}" 2>/dev/null && pwd -P)"; case "${h}" in "@TMP@"/*) ;; *) echo "npx de teste: recusa, HOME fora da pasta de teste: ${HOME}" >&2; exit 99 ;; esac
echo "$*" >> "@TMP@/npx.log"
[ "$1" = --yes ] && shift
[ "$1" = skills ] && [ "$2" = remove ] || exit 64
n="$3"
echo "Successfully removed 1 skill(s)"
case "${NPX_STUB:-apaga}" in
  nada) exit 0 ;;
  demais) rm -rf "${CODEX_HOME:-${HOME}/.codex}/skills/${n}" ;;
  so-real) rm -rf "${HOME}/.agents/skills/${n}"; exit 0 ;;      # revisão R1: tira a pasta real e deixa o atalho
  so-atalho) rm -f "${HOME}/.claude/skills/${n}"; exit 0 ;;     # revisão R1: tira o atalho e deixa a pasta real
  so-pasta) rm -rf "${HOME}/.claude/skills/${n}" "${HOME}/.agents/skills/${n}"; exit 0 ;;   # rodada 5, R3: deixa a linha do registro
  metade) rm -f "${HOME}/.agents/skills/${n}/SKILL.md"; exit 0 ;;   # rodada 6, R3: apaga a pasta do plano só pela metade
esac
[ "${NPX_STUB_NADA:-}" = "${n}" ] && exit 0                     # revisão R3: esta skill o npx não tira
rm -rf "${HOME}/.claude/skills/${n}" "${HOME}/.agents/skills/${n}"
l="${HOME}/.agents/.skill-lock.json"
[ -f "$l" ] && awk -v n="$n" '$0 ~ "^    \"" n "\": \\{" { p = 1 } !p { print } p && /^    \}/ { p = 0 }' "$l" > "$l.t" && mv "$l.t" "$l"
[ "${NPX_STUB:-}" = interrompe ] && kill -KILL "${PPID}"          # revisão rodada 2, N2: a limpeza morre aqui
[ -n "${NPX_STUB_INTERROMPE:-}" ] && [ "${NPX_STUB_INTERROMPE}" = "${n}" ] && kill -KILL "${PPID}"   # rodada 3, N1: só neste item
exit 0
"""
NPX_REAL = """#!/bin/sh
h="$(cd "${HOME}" 2>/dev/null && pwd -P)"; case "${h}" in "@TMP@"/*) ;; *) echo "npx de teste: recusa, HOME fora da pasta de teste: ${HOME}" >&2; exit 99 ;; esac
[ "$1" = --yes ] && shift
[ "$1" = skills ] && shift
exec node "${SDD_F25_SKILLS_CLI}" "$@"
"""
AGENTE_FALSO = "#!/bin/sh\necho \"@NOME@ 9.9.9\"\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="f25-")).resolve()
        self.home = self.tmp / "home"
        self.proj = self.tmp / "meu-app"
        self.home.mkdir()
        self.proj.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for nome, texto in (("npx", NPX_FALSO), ("npx-real", NPX_REAL), ("claude", AGENTE_FALSO.replace("@NOME@", "2.1.0")),
                            ("codex", AGENTE_FALSO.replace("@NOME@", "codex-cli"))):
            p = self.bin / nome
            p.write_text(texto.replace("@TMP@", B(self.tmp)), encoding="utf-8")   # o bash compara no formato dele
            p.chmod(0o755)
        self.gitconfig = self.tmp / "gitconfig"
        self.gitconfig.write_text("[user]\n\tname = Teste\n\temail = teste@example.com\n[init]\n\tdefaultBranch = main\n",
                                  encoding="utf-8")
        self.git("init", "-q")
        (self.proj / "README.md").write_text("x\n", encoding="utf-8")
        self.commit()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ── fixtures ──
    def env(self, **extra: str) -> dict:
        e = {k: v for k, v in os.environ.items()
             if k not in ("CODEX_HOME", "CLAUDE_CONFIG_DIR", "XDG_STATE_HOME", "GIT_ASKPASS", "SSH_ASKPASS")}
        e.update({"HOME": str(self.home), "GIT_CONFIG_GLOBAL": str(self.gitconfig), "GIT_CONFIG_NOSYSTEM": "1",
                  "PATH": str(self.bin) + os.pathsep + e.get("PATH", ""), "SDD_CHECAR_NPX": str(self.bin / "npx"),
                  "SDD_CHECAR_GH": str(self.tmp / "sem-gh"), "SDD_CHECAR_EDITOR_PATH": str(self.tmp / "sem-editor"),
                  "SDD_APPS_DIRS": str(self.tmp / "sem-editor")})
        e.update(extra)
        return e

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.proj, check=True, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env={**os.environ, "GIT_CONFIG_GLOBAL": str(self.gitconfig), "GIT_CONFIG_NOSYSTEM": "1"}).stdout

    def commit(self) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "--no-verify", "--allow-empty", "-m", "t")

    def skill(self, pasta: Path, nome: str, versao: str | None, origem: str, extra: str = "") -> Path:
        d = pasta / nome
        d.mkdir(parents=True, exist_ok=True)
        meta = '  version: "%s"\n' % versao if versao is not None else ""
        ident = "`%s v%s · nov/2026 · versão atual: %s`\n" % (nome, versao, URL[origem]) if origem != "outra" else "Skill de outra origem.\n"
        (d / "SKILL.md").write_text("---\nname: %s\ndescription: \"teste\"\nmetadata:\n%s---\n\n%s%s" % (nome, meta, ident, extra),
                                    encoding="utf-8")
        return d

    def registro(self, *nomes: str, source: str = "robertodiasduarte/sdd-starter") -> None:
        corpo = ",\n".join('    "%s": {\n      "source": "%s",\n      "sourceType": "github"\n    }' % (n, source) for n in nomes)
        (self.home / ".agents").mkdir(exist_ok=True)
        (self.home / ".agents/.skill-lock.json").write_text(
            '{\n  "version": 3,\n  "skills": {\n%s\n  },\n  "dismissed": {}\n}' % corpo, encoding="utf-8")

    @property
    def g_claude(self) -> Path:
        return self.home / ".claude/skills"

    @property
    def g_agents(self) -> Path:
        return self.home / ".agents/skills"

    def tabela_21(self) -> None:
        """A tabela 2.1 do ESCOPO: 3 skills em ~/.claude (Open, à mão), ~/.agents (starter, npx) e .claude do projeto (Open, git)."""
        for s, a, b, c in (("sdd-brainstorm", "2.3.1", "2.5.0", "2.4.0"), ("sdd-define", "2.6.1", "2.8.0", "2.7.0"),
                           ("sdd-release", "2.11.1", "2.16.0", "2.12.0")):
            self.skill(self.g_claude, s, a, "open")
            self.skill(self.g_agents, s, b, "starter")
            self.skill(self.proj / ".claude/skills", s, c, "open")
        self.registro("sdd-brainstorm", "sdd-define", "sdd-release")
        self.commit()

    def arvore(self) -> str:
        """Hash de tudo em HOME e no projeto (caminho, tipo, destino do atalho, conteúdo); a lixeira fica de fora."""
        h = hashlib.sha256()
        for base in (self.home, self.proj):
            for raiz, dirs, arqs in os.walk(base):
                dirs.sort()
                if Path(raiz) == self.home and ".sdd-lixeira" in dirs:
                    dirs.remove(".sdd-lixeira")
                for nome in sorted(dirs + arqs):
                    p = Path(raiz) / nome
                    h.update(str(p.relative_to(self.tmp)).encode())
                    if p.is_symlink():
                        h.update(b"L" + os.readlink(p).encode())
                    elif p.is_file():
                        h.update(b"F" + p.read_bytes())
                    else:
                        h.update(b"D")
        return h.hexdigest()

    # ── execução ──
    def roda(self, *args: str, cwd: Path | None = None, **extra: str) -> tuple[int, str]:
        r = subprocess.run([BASH, str(SCRIPT), *args], cwd=cwd or self.proj, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=self.env(**extra), stdin=subprocess.DEVNULL, timeout=120)
        return r.returncode, r.stdout + r.stderr

    def plano(self, **extra: str) -> tuple[str, str]:
        rc, out = self.roda("--duplicadas", **extra)
        self.assertEqual(rc, 0, out)
        m = re.search(r"--limpar ([0-9a-f]{12})\s*$", out)
        return out, (m.group(1) if m else "")

    def limpar(self, **extra: str) -> tuple[int, str]:
        _, sig = self.plano(**extra)
        self.assertTrue(sig, "o plano não terminou com o comando de aplicar")
        return self.roda("--limpar", sig, **extra)

    def desfazer(self, out: str) -> tuple[int, str]:
        linha = out.strip().splitlines()[-1]
        self.assertTrue(linha.startswith("Para desfazer: bash "), linha)
        alvo = shlex.split(linha[len("Para desfazer: "):])
        alvo[0] = BASH   # LM-029: "bash" sem caminho, no Windows, pode ser o do WSL
        r = subprocess.run(alvo, cwd=self.proj, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env=self.env(), timeout=60)
        return r.returncode, r.stdout + r.stderr


class AT001Claude(Base):
    def test_global_e_projeto_o_claude_roda_a_global(self):
        self.skill(self.g_claude, "sdd-define", "2.6.1", "open")
        self.skill(self.proj / ".claude/skills", "sdd-define", "2.7.0", "open")
        self.commit()
        rc, out = self.roda()
        self.assertEqual(rc, 0, out)
        self.assertIn("A skill sdd-define está em 2 lugares que o Claude Code lê, e ele roda a global (a 2.6.1), "
                      "não a 2.7.0 do projeto:", out)

    def test_claude_config_dir_troca_a_pasta_global(self):
        cfg = self.home / "cfg"
        self.skill(cfg / "skills", "sdd-define", "2.6.1", "open")
        self.skill(self.g_claude, "sdd-kb", "2.2.1", "open")
        self.skill(self.proj / ".claude/skills", "sdd-define", "2.7.0", "open")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
        self.commit()
        rc, out = self.roda(CLAUDE_CONFIG_DIR=str(cfg))
        self.assertIn("sdd-define está em 2 lugares que o Claude Code lê", out)
        self.assertNotIn("sdd-kb está", out)   # ~/.claude/skills não vale com CLAUDE_CONFIG_DIR

    def test_o_claude_nao_le_as_pastas_agents(self):
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")
        self.skill(self.proj / ".claude/skills", "sdd-define", "2.7.0", "open")
        self.commit()
        _, out = self.roda()
        self.assertNotIn("sdd-define está", out)


class AT002Codex(Base):
    def test_as_4_pastas_do_codex(self):
        pastas = {"~/.codex": self.home / ".codex/skills", "~/.agents": self.g_agents,
                  ".agents": self.proj / ".agents/skills", ".codex": self.proj / ".codex/skills"}
        nomes = list(pastas)
        for i, a in enumerate(nomes):
            for b in nomes[i + 1:]:
                with self.subTest(par=(a, b)):
                    for p in pastas.values():
                        shutil.rmtree(p, ignore_errors=True)
                    self.skill(pastas[a], "sdd-kb", "2.2.1", "open")
                    self.skill(pastas[b], "sdd-kb", "2.2.3", "open")
                    _, out = self.roda()
                    self.assertIn("A skill sdd-kb está em 2 lugares que o Codex lê, e ele escolhe uma sem dizer qual:", out)

    def test_codex_home_troca_a_pasta_do_codex(self):
        ch = self.tmp / "codexhome"
        self.skill(ch / "skills", "sdd-kb", "2.2.1", "open")
        self.skill(self.home / ".codex/skills", "sdd-define", "2.6.1", "open")
        self.skill(self.g_agents, "sdd-kb", "2.2.3", "open")
        self.skill(self.g_agents, "sdd-define", "2.8.0", "open")
        _, out = self.roda(CODEX_HOME=str(ch))
        self.assertIn("sdd-kb está em 2 lugares que o Codex lê", out)
        self.assertNotIn("sdd-define está", out)

    @unittest.skipUnless(shutil.which("codex"), "codex ausente: a medição do experimento 2 não se refaz aqui")
    def test_refaz_a_medicao_do_codex_sem_modelo(self):
        """O Codex instalado ainda lê exatamente as pastas que o checar.sh varre (EXP-2): sem modelo, sem rede."""
        ch = self.tmp / "codexhome"
        marcas = {"f25-home-agents": self.g_agents, "f25-codex-home": ch / "skills", "f25-proj-agents": self.proj / ".agents/skills",
                  "f25-proj-codex": self.proj / ".codex/skills", "f25-home-claude": self.g_claude,
                  "f25-proj-claude": self.proj / ".claude/skills"}
        for nome, pasta in marcas.items():
            self.skill(pasta, nome, "1.0.0", "open")
        codex = shutil.which("codex", path=os.environ.get("PATH"))
        r = subprocess.run([codex, "debug", "prompt-input", "oi"], cwd=self.proj, capture_output=True, text=True, encoding="utf-8",
                           errors="replace",
                           env={**self.env(CODEX_HOME=str(ch)), "PATH": os.environ.get("PATH", "")}, timeout=60)
        vistos = set(re.findall(r"(f25-[a-z-]+): ", r.stdout))
        self.assertEqual(vistos, {"f25-home-agents", "f25-codex-home", "f25-proj-agents", "f25-proj-codex"}, r.stdout[-2000:])


class AT003Npx(Base):
    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_copia_do_registro_e_atalho_contam_como_uma(self):
        self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")
        self.g_claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
        self.registro("sdd-kb")
        _, out = self.roda()
        self.assertNotIn("sdd-kb está", out)   # o atalho do npx não é duplicata
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
        self.commit()
        _, out = self.roda()
        self.assertIn("global: %s/sdd-kb — versão 2.2.1, do starter, instalada pelo npx" % B(self.g_claude), out)

    def test_quem_veio_do_npx(self):
        casos = (  # (onde está a cópia do npx, origem da cópia manual em ~/.claude, esperado para ~/.claude)
            ("so-claude", None, "instalada pelo npx"),        # -a claude-code: a cópia fica em ~/.claude, sem ~/.agents
            ("agents", "open", "copiada à mão"),              # o caso do ESCOPO: npx em ~/.agents e Open à mão em ~/.claude
        )
        for caso, manual, esperado in casos:
            with self.subTest(caso=caso):
                shutil.rmtree(self.home / ".claude", ignore_errors=True)
                shutil.rmtree(self.home / ".agents", ignore_errors=True)
                shutil.rmtree(self.proj / ".claude", ignore_errors=True)
                if caso == "so-claude":
                    self.skill(self.g_claude, "sdd-kb", "2.2.1", "starter")
                else:
                    self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")
                    self.skill(self.g_claude, "sdd-kb", "2.2.0", manual)
                self.registro("sdd-kb")
                self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
                _, out = self.roda()
                self.assertRegex(out, r"global: %s/sdd-kb — versão [0-9.]+, [^,]+, %s" % (re.escape(B(self.g_claude)), esperado))

    def test_registro_de_outro_repositorio_nao_marca_a_copia_open(self):
        self.skill(self.g_agents, "sdd-kb", "2.2.1", "open")
        self.skill(self.proj / ".agents/skills", "sdd-kb", "2.2.3", "open")
        self.registro("sdd-kb", source="robertodiasduarte/sdd-starter")
        _, out = self.roda()
        self.assertIn("global: %s/sdd-kb — versão 2.2.1, do SDD Open, copiada à mão" % B(self.g_agents), out)


class AT004Diagnostico(Base):
    def test_tabela_21_tres_itens_sem_mudar_nada(self):
        self.tabela_21()
        (self.proj / ".env").write_text("X=1\n", encoding="utf-8")   # um ⚠️ de dado, que vem antes
        antes = self.arvore()
        rc, out = self.roda()
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.arvore(), antes, "o diagnóstico normal mudou algum arquivo")
        bloco = out.split("⚠️ Vale arrumar", 1)[1]
        for s, g, p in (("sdd-brainstorm", "2.3.1", "2.4.0"), ("sdd-define", "2.6.1", "2.7.0"), ("sdd-release", "2.11.1", "2.12.0")):
            self.assertIn("A skill %s está em 2 lugares que o Claude Code lê, e ele roda a global (a %s), não a %s do projeto:\n"
                          "    global: %s/%s — versão %s, do SDD Open, copiada à mão\n"
                          "    do projeto: %s/.claude/skills/%s — versão %s, do SDD Open, salva no git do projeto\n"
                          % (s, g, p, B(self.g_claude), s, g, B(self.proj), s, p), bloco)
        self.assertEqual(bloco.count("--duplicadas"), 3)
        i_env, i_dup, i_remoto = bloco.index(".env"), bloco.index("sdd-brainstorm"), bloco.index("não tem remoto")
        self.assertLess(i_env, i_dup)
        self.assertLess(i_dup, i_remoto)
        self.assertNotIn("🔴", out)

    def test_mais_de_3_vira_um_item_com_e_mais_n(self):
        for i in range(12):
            n = "sdd-x%02d" % i
            self.skill(self.g_claude, n, "1.0.0", "open")
            self.skill(self.proj / ".claude/skills", n, "1.0.1", "open")
        self.commit()
        _, out = self.roda()
        self.assertIn("12 skills do SDD estão em mais de um lugar que o mesmo agente lê (sdd-x00, sdd-x01, sdd-x02, sdd-x03, "
                      "sdd-x04, sdd-x05, sdd-x06, sdd-x07, sdd-x08, sdd-x09 e mais 2)", out)
        self.assertEqual(out.count("--duplicadas"), 1)


class AT005NaoEDuplicata(Base):
    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_falsos_positivos(self):
        # par gerado pelo sync do Open: .agents (fonte) → .claude (gerada), agentes diferentes
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.8.0", "open")
        self.skill(self.proj / ".claude/skills", "sdd-define", "2.8.0", "open", extra="<!-- GENERATED -->\n")
        # ~/.agents × ~/.claude: agentes diferentes
        self.skill(self.g_agents, "sdd-kb", "2.2.3", "starter")
        self.skill(self.g_claude, "sdd-kb", "2.2.1", "open")
        # atalho para a mesma pasta
        self.skill(self.home / ".codex/skills", "sdd-iterate", "1.0.0", "open")
        os.symlink(self.home / ".codex/skills/sdd-iterate", self.g_agents / "sdd-iterate")
        # skill de terceiro repetida (nome fora do SDD, sem a linha de identificação)
        self.skill(self.g_agents, "minha-skill", "1.0.0", "outra")
        self.skill(self.home / ".codex/skills", "minha-skill", "2.0.0", "outra")
        self.commit()
        rc, out = self.roda()
        self.assertEqual(rc, 0, out)
        self.assertNotIn("--duplicadas", out)
        plano, _ = self.plano()
        self.assertIn("Nenhuma skill do SDD está duplicada para o mesmo agente. Nada a limpar.", plano)


class AT006Plano(Base):
    def test_plano_da_tabela_21(self):
        self.tabela_21()
        antes = self.arvore()
        out, sig = self.plano()
        self.assertEqual(self.arvore(), antes)
        self.assertTrue(out.startswith("Plano de limpeza das skills duplicadas — nada mudou ainda.\n"), out)
        self.assertIn("(global = vale para todos os projetos deste computador · do projeto = só nesta pasta)", out)
        self.assertIn("1. sdd-brainstorm — o Claude Code lê 2 cópias e roda a global:", out)
        self.assertIn("   Recomendo: tirar a global %s/sdd-define (2.6.1, a mais velha).\n" % B(self.g_claude), out)
        self.assertIn("   Ela vale para todos os projetos deste computador: os que não têm cópia própria ficam sem a sdd-define.", out)
        self.assertRegex(out, r"Assinatura deste plano: [0-9a-f]{12} \(muda se qualquer cópia mudar\)\.")
        self.assertTrue(out.rstrip().splitlines()[-1].endswith("--duplicadas") is False)
        self.assertTrue(out.rstrip().splitlines()[-1].endswith("--limpar " + sig))
        self.assertEqual(self.plano()[1], sig, "a assinatura não é estável")


class AT007Matriz(Base):
    def caso(self, montar) -> str:
        for p in (self.home, self.proj / ".claude", self.proj / ".agents"):
            shutil.rmtree(p, ignore_errors=True)
        self.home.mkdir(exist_ok=True)
        montar()
        self.commit()
        out, _ = self.plano()
        return out

    def test_matriz(self):
        pc = self.proj / ".claude/skills"
        pa = self.proj / ".agents/skills"
        # versões diferentes, global mais velha e cópia do projeto fora do git ⇒ tira a mais velha
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "2.2.1", "open"), self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Recomendo: tirar a global %s/sdd-kb (2.2.1, a mais velha)." % B(self.g_claude), out)
        # mesma versão, mesma origem, mesmo conteúdo ⇒ sobra: sai a global
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "2.2.3", "open"), self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Recomendo: tirar a global %s/sdd-kb (2.2.3: a mesma versão da que fica; sobra)." % B(self.g_claude), out)
        # mesma versão, mesma origem, conteúdo diferente ⇒ não escolhe
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "2.2.3", "open", extra="editada\n"),
                                 self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Não escolho: as cópias", out)
        self.assertIn("dizem 2.2.3 e têm textos diferentes", out)
        self.assertNotIn("--limpar", out)
        # mesma versão, Open × starter ⇒ a mesma versão: sai a global
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "2.2.3", "starter"), self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Recomendo: tirar a global %s/sdd-kb (2.2.3: a mesma versão da que fica; sobra)." % B(self.g_claude), out)
        # versão ilegível ⇒ não escolhe
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", None, "open"), self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Não escolho: não consegui ler a versão de %s/sdd-kb" % B(self.g_claude), out)
        # uma cópia que não é do SDD ⇒ só avisa
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "9.0.0", "outra"), self.skill(pc, "sdd-kb", "2.2.3", "open")))
        self.assertIn("Não escolho: a cópia %s/sdd-kb não é do SDD" % B(self.g_claude), out)
        # a mais velha é a do projeto, salva no git ⇒ não tira; recomenda atualizar (Open)
        out = self.caso(lambda: (self.skill(self.g_claude, "sdd-kb", "2.2.3", "starter"), self.skill(pc, "sdd-kb", "2.2.1", "open")))
        self.assertIn("A mais velha é a do projeto, salva no git: não a tiro", out)
        self.assertIn("https://github.com/robertodiasduarte/sdd-open/blob/main/docs/pt-BR/upgrade.md", out)
        self.assertNotIn("--limpar", out)

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_matriz_com_atalhos(self):
        pc = self.proj / ".claude/skills"
        pa = self.proj / ".agents/skills"
        # atalho que não veio do npx ⇒ não escolhe
        def atalho():
            self.skill(self.home / "outra-pasta", "sdd-kb", "2.2.1", "open")
            self.g_claude.mkdir(parents=True)
            os.symlink(self.home / "outra-pasta/sdd-kb", self.g_claude / "sdd-kb")
            self.skill(pc, "sdd-kb", "2.2.3", "open")
        out = self.caso(atalho)
        self.assertIn("é um atalho para outra pasta", out)
        # tirar deixaria um agente sem a skill neste projeto ⇒ não escolhe
        def sem_saida():
            self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")    # Codex: ~/.agents (velha) × .agents do projeto
            self.skill(pa, "sdd-kb", "2.2.3", "open")
            self.g_claude.mkdir(parents=True)                          # Claude: só o atalho para ~/.agents
            os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
            self.registro("sdd-kb")
        out = self.caso(sem_saida)
        self.assertIn("tirar deixaria o Claude Code sem a versão mais nova da sdd-kb neste projeto", out)
        self.assertNotIn("--limpar", out)


class AT008Recusa(Base):
    def setUp(self):
        super().setUp()
        self.tabela_21()

    def sem_mudanca(self, rc: int, out: str, antes: str) -> None:
        self.assertNotEqual(rc, 0, out)
        self.assertIn("Nada foi tirado.", out)
        self.assertEqual(self.arvore(), antes)
        self.assertFalse((self.home / ".sdd-lixeira").exists(), out)

    def test_recusas(self):
        antes = self.arvore()
        self.sem_mudanca(*self.roda("--limpar"), antes)
        self.sem_mudanca(*self.roda("--limpar", "0123456789ab"), antes)
        _, sig = self.plano()
        (self.g_claude / "sdd-define/nova.md").write_text("x\n", encoding="utf-8")   # o plano muda depois de mostrado
        antes = self.arvore()
        rc, out = self.roda("--limpar", sig)
        self.sem_mudanca(rc, out, antes)
        self.assertIn("O plano mudou desde que você o viu", out)

    def test_sem_npx_e_sem_lixeira(self):
        shutil.rmtree(self.proj / ".claude")
        self.commit()
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")   # Codex: a do npx fica velha
        self.commit()
        _, sig = self.plano()
        antes = self.arvore()
        rc, out = self.roda("--limpar", sig, SDD_CHECAR_NPX=str(self.tmp / "nao-existe"))
        self.sem_mudanca(rc, out, antes)
        self.assertIn("o npx não está disponível", out)
        (self.home / ".sdd-lixeira").write_text("um arquivo no lugar da pasta\n", encoding="utf-8")
        rc, out = self.roda("--limpar", sig)
        self.assertNotEqual(rc, 0)
        self.assertIn("Não consegui criar a lixeira", out)
        self.assertIn("Nada foi tirado.", out)


class AT009Limpar(Base):
    def test_mover_e_desfazer(self):
        self.tabela_21()
        conteudo = {s: (self.g_claude / s / "SKILL.md").read_bytes() for s in ("sdd-brainstorm", "sdd-define", "sdd-release")}
        antes = self.arvore()
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        lix = sorted((self.home / ".sdd-lixeira").iterdir())
        self.assertEqual(len(lix), 1)
        self.assertRegex(lix[0].name, r"^\d{8}-\d{6}$")
        for s, dado in conteudo.items():
            self.assertFalse((self.g_claude / s).exists())
            self.assertEqual((lix[0] / "home-claude" / s / "SKILL.md").read_bytes(), dado)
        self.assertTrue((self.g_agents / "sdd-define").is_dir(), "tirou o que não estava no plano")
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertEqual(self.arvore(), antes)

    def misto(self) -> None:
        """O caso do EXP-3: a do npx em ~/.agents é a mais velha para o Codex; em ~/.claude há uma cópia à mão, fora do plano."""
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")
        self.skill(self.g_claude, "sdd-define", "2.6.1", "open", extra="à mão\n")
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.registro("sdd-define")
        self.commit()

    def test_npx_protege_a_outra_copia(self):
        self.misto()
        manual = (self.g_claude / "sdd-define/SKILL.md").read_bytes()
        antes = self.arvore()
        out, _ = self.plano()
        self.assertIn("sai pelo npx skills remove sdd-define -g -a codex -y.", out)
        self.assertIn("Esse comando também apagaria %s/sdd-define, que não está no plano" % B(self.g_claude), out)
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        self.assertIn("saiu pelo npx skills remove", out)
        self.assertFalse((self.g_agents / "sdd-define").exists())
        self.assertEqual((self.g_claude / "sdd-define/SKILL.md").read_bytes(), manual)
        self.assertNotIn('"sdd-define"', (self.home / ".agents/.skill-lock.json").read_text(encoding="utf-8"))
        self.assertIn("remove sdd-define -g -a codex -y", (self.tmp / "npx.log").read_text(encoding="utf-8"))
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertEqual(self.arvore(), antes)

    def test_npx_que_nao_tira_e_npx_que_tira_demais(self):
        self.misto()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="nada")
        self.assertEqual(rc, 1, out)
        self.assertIn("o npx não tirou", out)
        self.assertIn("Nada foi tirado.", out)
        self.assertEqual(self.arvore(), antes)
        shutil.rmtree(self.home / ".sdd-lixeira")
        self.skill(self.home / ".codex/skills", "sdd-define", "2.9.0", "open")   # uma cópia que o npx não deveria tocar
        rc, out = self.limpar(NPX_STUB="demais")
        self.assertEqual(rc, 1, out)
        self.assertIn("o npx mexeu numa pasta fora do plano", out)
        self.assertTrue((self.g_agents / "sdd-define/SKILL.md").is_file(), "a cópia não voltou")

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_atalho_do_npx_volta_com_o_desfazer(self):
        self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")
        self.g_claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
        self.skill(self.proj / ".agents/skills", "sdd-kb", "2.2.3", "open")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
        self.registro("sdd-kb")
        self.commit()
        antes = self.arvore()
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        self.assertIn("-a claude-code -a codex -y", (self.tmp / "npx.log").read_text(encoding="utf-8"))
        self.assertFalse(os.path.lexists(self.g_claude / "sdd-kb"))
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertTrue((self.g_claude / "sdd-kb").is_symlink())
        self.assertEqual(self.arvore(), antes)

    def test_caminho_com_espaco_aspas_e_cifrao(self):
        estranho = self.tmp / "Ana O'Neil $HOME \"x\""
        estranho.mkdir()
        self.home = estranho / "home"
        self.home.mkdir()
        self.misto()
        antes = self.arvore()
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertEqual(self.arvore(), antes)

    def test_desfazer_nao_sobrescreve(self):
        self.tabela_21()
        rc, out = self.limpar()
        self.skill(self.g_claude, "sdd-define", "3.0.0", "open")   # uma cópia nova apareceu no lugar
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 1, des)
        self.assertIn("existe de novo e é diferente: não sobrescrevi", des)
        self.assertIn('version: "3.0.0"', (self.g_claude / "sdd-define/SKILL.md").read_text(encoding="utf-8"))

    @unittest.skipUnless(os.environ.get("SDD_F25_SKILLS_CLI") and shutil.which("node"),
                         "SDD_F25_SKILLS_CLI não aponta para um cli.mjs do skills: o CLI de verdade não roda aqui")
    def test_com_o_cli_de_verdade(self):
        cli = os.environ["SDD_F25_SKILLS_CLI"]
        fonte = self.tmp / "fonte"
        self.skill(fonte / "skills", "sdd-define", "2.8.0", "starter")
        subprocess.run(["git", "init", "-q"], cwd=fonte, check=True)
        r = subprocess.run(["node", cli, "add", str(fonte), "-a", "codex", "-g", "-y", "--skill", "sdd-define"], cwd=self.proj,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env={**self.env(), "DO_NOT_TRACK": "1"}, timeout=120)
        self.assertTrue((self.g_agents / "sdd-define/SKILL.md").is_file(), r.stdout + r.stderr)
        self.skill(self.g_claude, "sdd-define", "2.6.1", "open", extra="à mão\n")
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.commit()
        manual = (self.g_claude / "sdd-define/SKILL.md").read_bytes()
        antes = self.arvore()
        real = {"SDD_CHECAR_NPX": str(self.bin / "npx-real"), "SDD_F25_SKILLS_CLI": cli, "DO_NOT_TRACK": "1"}
        rc, out = self.limpar(**real)
        self.assertEqual(rc, 0, out)
        self.assertFalse((self.g_agents / "sdd-define").exists())
        self.assertEqual((self.g_claude / "sdd-define/SKILL.md").read_bytes(), manual)
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertEqual(self.arvore(), antes)


class RevisaoRodada1(Base):
    """Achados da revisão do código, rodada 1 (claude revisa, codex audita): R1 a R4 e N1."""

    def atalho_npx(self) -> None:
        self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")
        self.g_claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
        self.skill(self.proj / ".agents/skills", "sdd-kb", "2.2.3", "open")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
        self.registro("sdd-kb")
        self.commit()

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_r1_npx_que_tira_so_a_pasta_real_devolve_tudo(self):
        self.atalho_npx()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="so-real")
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.arvore(), antes, "a cópia que o npx tirou não voltou da lixeira")

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio; o npx de lá copia em vez de ligar")
    def test_r1_npx_que_tira_so_o_atalho_devolve_tudo(self):
        self.atalho_npx()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="so-atalho")
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.arvore(), antes, "o atalho que o npx tirou não voltou")

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio")
    def test_r2_pasta_pessoal_por_atalho_nao_protege_a_propria_copia(self):
        dot = self.tmp / "dotfiles" / "claude"
        (dot / "skills").mkdir(parents=True)
        os.symlink(dot, self.home / ".claude")
        self.skill(self.g_claude, "sdd-kb", "2.2.1", "starter")   # npx só para o Claude Code: sem ~/.agents/skills
        self.registro("sdd-kb")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "open")
        self.commit()
        out, _ = self.plano()
        self.assertIn("sai pelo npx skills remove sdd-kb -g -a claude-code -y.", out)
        self.assertNotIn("também apagaria", out)
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        self.assertFalse((dot / "skills/sdd-kb").exists(), "a cópia do plano foi protegida e voltou")

    def dois_do_npx(self) -> None:
        for s in ("sdd-brainstorm", "sdd-define"):
            self.skill(self.g_agents, s, "2.5.0", "starter")
            self.skill(self.proj / ".agents/skills", s, "2.6.0", "open")
        self.registro("sdd-brainstorm", "sdd-define")
        self.commit()

    def test_r3_falha_no_2o_item_nao_devolve_o_registro_do_1o(self):
        self.dois_do_npx()
        rc, out = self.limpar(NPX_STUB_NADA="sdd-define")
        self.assertEqual(rc, 1, out)
        reg = (self.home / ".agents/.skill-lock.json").read_text(encoding="utf-8")
        self.assertFalse((self.g_agents / "sdd-brainstorm").exists())
        self.assertNotIn('"sdd-brainstorm"', reg, "a linha do item que saiu voltou ao registro")
        self.assertIn('"sdd-define"', reg)
        self.assertTrue((self.g_agents / "sdd-define/SKILL.md").is_file())

    def test_r4_a_lista_do_que_vai_sair_fica_na_lixeira_antes_de_tirar(self):
        self.dois_do_npx()
        rc, out = self.limpar(NPX_STUB_NADA="sdd-define")
        lix = next((self.home / ".sdd-lixeira").iterdir())
        plano = (lix / "PLANO.txt").read_text(encoding="utf-8")
        for s in ("sdd-brainstorm", "sdd-define"):
            self.assertIn(B(self.g_agents / s), plano)

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio")
    def test_n1_o_codex_nao_perde_a_versao_mais_nova(self):
        self.skill(self.g_agents, "sdd-kb", "2.0.0", "starter")   # a global do npx, dos dois agentes
        self.g_claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
        self.registro("sdd-kb")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "3.0.0", "open")   # Claude: a do projeto é a mais nova
        self.skill(self.proj / ".agents/skills", "sdd-kb", "1.0.0", "open")   # Codex: a do projeto (no git) é a mais velha
        self.commit()
        out, _ = self.plano()
        self.assertIn("tirar deixaria o Codex sem a versão mais nova da sdd-kb neste projeto", out)
        self.assertNotIn("--limpar", out)


class RevisaoRodada2(Base):
    """Achados da revisão do código, rodada 2: R1 (array "or" no gawk), R3, R4 (rebatido, com prova), N1 e N2."""

    def test_r1_nenhum_nome_embutido_do_gawk_como_variavel_nos_awk(self):
        # no gawk (o awk do Git Bash), and/or/xor/compl/lshift/rshift/… são funções: usá-los como array é erro de sintaxe
        # e o plano sairia vazio. Sem gawk nesta máquina, a regra é conferida no texto.
        texto = (SKILL / "scripts/duplicadas.sh").read_text(encoding="utf-8") + (SKILL / "scripts/checar.sh").read_text(encoding="utf-8")
        ruins = re.findall(r"\b(and|or|xor|compl|lshift|rshift|strftime|systime|mktime|gensub|patsplit|isarray|typeof|asorti?|func)\s*[\[=]", texto)
        self.assertEqual([r for r in ruins], [], "nome reservado do gawk usado como variável")

    def test_r3_sobra_do_projeto_no_git_nao_e_a_mais_velha(self):
        self.skill(self.proj / ".agents/skills", "sdd-kb", "2.2.3", "open")
        self.skill(self.proj / ".codex/skills", "sdd-kb", "2.2.3", "open")
        self.commit()
        out, _ = self.plano()
        self.assertIn("tem a mesma versão da que fica e está salva no git: não a tiro", out)
        self.assertNotIn("A mais velha é a do projeto", out)

    def test_r4_so_duplicatas_nao_sai_como_pronto(self):
        self.tabela_21()
        bare = self.tmp / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        self.git("remote", "add", "origin", str(bare))
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.git("remote", "set-head", "origin", "main")
        rc, out = self.roda()
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ Vale arrumar", out)
        self.assertIn("✅ Repo meu-app", out)
        self.assertNotIn("✅ Pronto", out)

    @unittest.skipIf(WINDOWS, "atalho (symlink) no Windows pede privilégio")
    def test_n1_copia_compartilhada_com_escolha_em_aberto_nao_sai(self):
        self.skill(self.g_agents, "sdd-kb", "2.2.3", "starter")   # a global do npx, dos dois agentes
        self.g_claude.mkdir(parents=True)
        os.symlink("../../.agents/skills/sdd-kb", self.g_claude / "sdd-kb")
        self.registro("sdd-kb")
        self.skill(self.proj / ".claude/skills", "sdd-kb", "2.2.3", "starter", extra="editada\n")   # Claude: em aberto
        self.skill(self.proj / ".agents/skills", "sdd-kb", "2.2.4", "open")                          # Codex: a global é velha
        self.commit()
        out, _ = self.plano()
        self.assertIn("também é lida pelo outro agente, e lá a escolha ficou em aberto", out)
        self.assertNotIn("--limpar", out)

    def test_n2_limpeza_interrompida_depois_do_npx_desfaz_o_registro(self):
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.registro("sdd-define")
        self.commit()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="interrompe")
        self.assertNotEqual(rc, 0, out)
        lix = next((self.home / ".sdd-lixeira").iterdir())
        r = subprocess.run([BASH, str(lix / "desfazer.sh")], cwd=self.proj, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=self.env(), timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.arvore(), antes, "o desfazer não devolveu a árvore (o registro?)")


class RevisaoRodada3(Base):
    """Achados da revisão do código, rodada 3: R1 (pasta pessoal como pasta atual), R2 (texto da protegida), N1."""

    def test_r1_na_pasta_pessoal_as_globais_nao_viram_do_projeto(self):
        self.skill(self.g_agents, "sdd-kb", "2.2.1", "starter")
        self.skill(self.home / ".codex/skills", "sdd-kb", "2.2.3", "open")
        self.registro("sdd-kb")
        rc, out = self.roda("--duplicadas", cwd=self.home)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("do projeto:", out)
        self.assertIn("global: %s/sdd-kb — versão 2.2.1, do starter, instalada pelo npx" % B(self.g_agents), out)
        self.assertIn("Recomendo: tirar a global %s/sdd-kb (2.2.1, a mais velha)." % B(self.g_agents), out)

    def test_r2_protegida_que_tambem_sai_no_plano(self):
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")          # Codex: a do npx é a mais velha
        self.skill(self.g_claude, "sdd-define", "2.6.1", "open")             # Claude: a manual é a mais velha
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.skill(self.proj / ".claude/skills", "sdd-define", "2.9.0", "open")
        self.registro("sdd-define")
        self.commit()
        out, _ = self.plano()
        self.assertNotIn("que não está no plano", out)
        self.assertIn("Esse comando também apagaria %s/sdd-define, que sai neste plano na vez dela" % B(self.g_claude), out)
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        self.assertFalse((self.g_agents / "sdd-define").exists())
        self.assertFalse((self.g_claude / "sdd-define").exists())

    def test_n1_interrompida_no_2o_item_do_npx_desfaz_o_registro(self):
        for s in ("sdd-brainstorm", "sdd-define"):
            self.skill(self.g_agents, s, "2.5.0", "starter")
            self.skill(self.proj / ".agents/skills", s, "2.6.0", "open")
        self.registro("sdd-brainstorm", "sdd-define")
        self.commit()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB_INTERROMPE="sdd-define")
        self.assertNotEqual(rc, 0, out)
        lix = next((self.home / ".sdd-lixeira").iterdir())
        r = subprocess.run([BASH, str(lix / "desfazer.sh")], cwd=self.proj, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=self.env(), timeout=60)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.arvore(), antes, "o desfazer não devolveu a árvore (o registro?)")


class RevisaoRodada5(Base):
    """Achados da revisão de confirmação (rodada 5, codex revisa, claude audita): R1, R2 e R3."""

    def test_r1_desfazer_nao_apaga_a_guardada_se_o_lugar_virou_atalho_para_ela(self):
        self.tabela_21()
        rc, out = self.limpar()
        self.assertEqual(rc, 0, out)
        lix = next((self.home / ".sdd-lixeira").iterdir())
        guardada = lix / "home-claude" / "sdd-define"
        os.symlink(guardada, self.g_claude / "sdd-define")   # alguém pôs à mão um atalho para dentro da lixeira
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 1, des)
        self.assertTrue((guardada / "SKILL.md").is_file(), "o desfazer apagou a única cópia guardada")

    def test_r2_sem_a_linha_do_desfazer_nada_sai(self):
        self.tabela_21()
        antes = self.arvore()
        rc, out = self.limpar(SDD_CHECAR_FALHA_DESFAZER="1")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("não consegui gravar o desfazer", out)
        self.assertEqual(self.arvore(), antes, "uma cópia saiu sem a linha do desfazer")

    def test_r3_npx_que_deixa_a_linha_no_registro_e_falha(self):
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.registro("sdd-define")
        self.commit()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="so-pasta")
        self.assertEqual(rc, 1, out)
        self.assertIn("deixou a skill no registro", out)
        self.assertEqual(self.arvore(), antes, "a cópia não voltou")


class RevisaoRodada6(Base):
    """Achados da revisão de confirmação, rodada 6 (codex revisa, claude audita): R1, R2, R3 e N1 — falhas no meio."""

    def um_do_npx(self, manual: bool = False) -> None:
        self.skill(self.g_agents, "sdd-define", "2.8.0", "starter")
        if manual:
            d = self.skill(self.g_claude, "sdd-define", "2.6.1", "open", extra="à mão\n")
            (d / "sub").mkdir()
            (d / "sub/nota.md").write_text("x\n", encoding="utf-8")
        self.skill(self.proj / ".agents/skills", "sdd-define", "2.9.0", "open")
        self.registro("sdd-define")
        self.commit()

    def test_r1_sem_a_copia_do_registro_o_npx_nao_roda(self):
        self.um_do_npx()
        antes = self.arvore()
        rc, out = self.limpar(SDD_CHECAR_FALHA_REGISTRO="1")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("não consegui guardar o registro do npx", out)
        self.assertFalse((self.tmp / "npx.log").exists(), "o npx rodou sem a cópia do registro")
        self.assertEqual(self.arvore(), antes)

    def test_r2_desfazer_nunca_apaga_a_copia_guardada(self):
        self.tabela_21()
        rc, out = self.limpar()
        lix = next((self.home / ".sdd-lixeira").iterdir())
        guardada = lix / "home-claude" / "sdd-define"
        shutil.copytree(guardada, self.g_claude / "sdd-define", symlinks=True)   # a mesma cópia voltou por outro caminho
        rc, des = self.desfazer(out)
        self.assertEqual(rc, 0, des)
        self.assertTrue((guardada / "SKILL.md").is_file(), "o desfazer apagou a cópia guardada")

    def test_r3_pasta_do_plano_apagada_pela_metade_volta_inteira(self):
        self.um_do_npx()
        antes = self.arvore()
        rc, out = self.limpar(NPX_STUB="metade")
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.arvore(), antes, "a pasta que o npx apagou pela metade não voltou inteira")

    @unittest.skipIf(WINDOWS, "permissão de pasta (chmod) não vale igual no Windows")
    def test_n1_protegida_que_nao_sai_inteira_para_o_item(self):
        self.um_do_npx(manual=True)
        trava = self.g_claude / "sdd-define/sub"
        trava.chmod(0o555)   # o rm -rf da protegida falha pela metade (o arquivo de dentro não sai)
        self.addCleanup(lambda: [p.chmod(0o755) for p in self.home.rglob("sub") if p.is_dir()])
        antes = self.arvore()
        rc, out = self.limpar()
        self.assertNotEqual(rc, 0, out)
        self.assertFalse((self.tmp / "npx.log").exists(), "o npx rodou com a protegida meio apagada")
        self.assertEqual(self.arvore(), antes, "a pasta protegida ficou meio apagada")


class AT010Textos(Base):
    def test_frente_continua_saindo_0_com_duplicatas(self):
        self.tabela_21()
        bare = self.tmp / "remoto.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        self.git("remote", "add", "origin", str(bare))
        self.git("push", "-q", "origin", "HEAD:refs/heads/main")
        self.git("remote", "set-head", "origin", "main")
        rc, out = self.roda("--frente")
        self.assertEqual(rc, 0, out)
        self.assertIn("✅ Pronto para abrir a frente", out)
        self.assertNotIn("skill", out.split("·")[0])

    def test_skill_md_tem_a_excecao_unica_e_a_etapa_limpar(self):
        t = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn('version: "1.6.0"', t)
        regra = t.split("- **Somente leitura.**", 1)[1].split("\n- **", 1)[0]
        self.assertIn("`--limpar <assinatura>`", regra)
        self.assertEqual(t.count("Exceção única"), 1)
        self.assertIn("e esse `desfazer.sh`, só quando o aluno pede para desfazer", regra)   # revisão rodada 2, R2
        self.assertIn("| 3 | Limpar |", t)
        self.assertIn("`--duplicadas`", t)

    def test_como_falar_tem_a_pergunta_d1_e_o_desfazer(self):
        t = (SKILL / "references/como-falar.md").read_text(encoding="utf-8")
        self.assertIn("[D1 · não se desfaz] **Posso tirar", t)
        for termo in ("- **sim** (recomendado)", "- **mostrar o plano como veio**", "- **não**", "- **não sei**",
                      "global —", "do projeto —", "lixeira —", "desfazer.sh"):
            self.assertIn(termo, t)

    def test_o_gerador_do_starter_nao_quebra_a_origem(self):
        """O gerador troca a URL completa do Open pela do starter em todo arquivo: a detecção da origem não pode usá-la."""
        t = (SKILL / "scripts/duplicadas.sh").read_text(encoding="utf-8")
        self.assertNotIn(URL["open"], t)
        self.assertIn(r"/sdd-open\/releases\/latest/", t)
        self.assertIn(r"/sdd-starter\/releases\/latest/", t)


if __name__ == "__main__":
    unittest.main()
