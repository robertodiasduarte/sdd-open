"""sdd/bin/sdd-decisoes-lint.sh — a marca da classe e o formato de cada pergunta de decisão (F9).

O lint acha as perguntas com o perguntas() do skill-lint.py (blocos ```markdown abertos; só a linha com
**Sua decisão**) e confere, em cada uma: 1 marca `[<código> · <rótulo>]` logo antes do negrito, com o
rótulo da tabela do item 9 do PERGUNTA_DECISAO.md; 1 opção (recomendado), a primeira; **não sei**; sem
**Outro**; nenhum identificador técnico fora do `(ref: …)` final. Cada regra tem um caso que reprova pelo
motivo certo e o caso que passa; os alvos reais (.agents/skills e os fragmentos) passam.
"""
from __future__ import annotations

import os
import shutil

from apoio import BASH, RAIZ, Sandbox

LINT = RAIZ / "sdd/bin/sdd-decisoes-lint.sh"
OPCOES = ("- **sim** (recomendado) — gravo o arquivo e sigo para o Verify Gate (ref: AT-001).\n"
          "- **mostrar antes** — mostro os 6 testes e pergunto de novo.\n"
          "- **não sei** — explico o que é um teste de aceitação.\n")
PERGUNTA = "**Posso gravar o DEFINE com estes 6 testes de aceitação?**"


class Base(Sandbox):
    def lint(self, *args, env=None):
        rc, out, err = self.roda([BASH, LINT, *args], self.tmp, env)
        return rc, out + err

    def caso(self, linha: str, opcoes: str = OPCOES, nome: str = "caso.md") -> str:
        return str(self.escreve(self.tmp, nome, "# Caso\n\n" + linha + "\n" + opcoes))


class AlvosReais(Base):
    def test_skills_do_pacote_15_perguntas(self):
        rc, out = self.lint("--sites", RAIZ / ".agents/skills")
        self.assertEqual(rc, 0, out)
        self.assertIn("15 pergunta(s) em 15 arquivo(s)", out)

    def test_fragmentos_2_perguntas(self):
        rc, out = self.lint("--sites", RAIZ / "sdd/templates/fragments")
        self.assertEqual(rc, 0, out)
        self.assertIn("2 pergunta(s) em 2 arquivo(s)", out)

    def test_o_ok_da_release_nao_conta_e_a_heuristica_da_kb_tambem_nao(self):
        for rel in (".agents/skills/sdd-release/SKILL.md", ".agents/skills/sdd-kb/references/kb-protocol.md"):
            with self.subTest(arquivo=rel):
                rc, out = self.lint("--sites", RAIZ / rel)
                self.assertEqual(rc, 64, out)
                self.assertIn("nenhuma pergunta de decisão", out)


class Regras(Base):
    def test_controle_passa_com_ref_no_fim(self):
        rc, out = self.lint("--sites", self.caso("**Sua decisão** — [auto · de rotina] " + PERGUNTA))
        self.assertEqual(rc, 0, out)
        self.assertIn("🟢", out)

    def test_cada_regra_reprova_pelo_motivo_certo(self):
        sd = "**Sua decisão** — "
        casos = (
            ("sem marca", sd + PERGUNTA, OPCOES, "sem marca de classe"),
            ("duas marcas", sd + "[D1 · não se desfaz] [auto · de rotina] " + PERGUNTA, OPCOES, "2 marcas"),
            ("marca fora do lugar", sd + "[auto · de rotina] isto: " + PERGUNTA, OPCOES, "marca fora do lugar"),
            ("marca sem rótulo", sd + "[D1] " + PERGUNTA, OPCOES, "marca sem o rótulo: [D1]"),
            ("marca desconhecida", sd + "[D7 · outra coisa] " + PERGUNTA, OPCOES, "marca desconhecida [D7 · outra coisa]"),
            ("rótulo diferente", sd + "[D1 · irreversível] " + PERGUNTA, OPCOES, "rótulo 'irreversível' diferente de 'não se desfaz'"),
            ("nenhuma recomendada", sd + "[auto · de rotina] " + PERGUNTA, OPCOES.replace(" (recomendado)", ""),
             "nenhuma opção (recomendado)"),
            ("duas recomendadas", sd + "[auto · de rotina] " + PERGUNTA,
             OPCOES.replace("**mostrar antes**", "**mostrar antes** (recomendado)"), "2 opções (recomendado)"),
            ("recomendada depois", sd + "[auto · de rotina] " + PERGUNTA,
             "- **mostrar antes** — mostro.\n- **sim** (recomendado) — gravo.\n- **não sei** — explico.\n",
             "a opção (recomendado) não é a primeira"),
            ("sem não sei", sd + "[auto · de rotina] " + PERGUNTA, OPCOES.replace("**não sei**", "**talvez**"),
             "sem a opção **não sei**"),
            ("com Outro", sd + "[auto · de rotina] " + PERGUNTA, OPCOES + "- **outra** — você descreve.\n",
             "tem a opção **Outro**"),
            ("AT no efeito", sd + "[auto · de rotina] " + PERGUNTA,
             OPCOES.replace("gravo o arquivo e", "gravo o AT-003 e"), "identificador técnico fora do (ref: …): AT-003"),
            ("LM na pergunta", sd + "[D3 · muda a regra do método] **Promovo a LM-004 para uma conferência?**", OPCOES,
             "identificador técnico fora do (ref: …): LM-004"),
            ("SHA no efeito", sd + "[auto · de rotina] " + PERGUNTA,
             OPCOES.replace("pergunto de novo", "comparo com 7c640eb"), "identificador técnico fora do (ref: …): 7c640eb"),
        )
        for nome, linha, opcoes, motivo in casos:
            with self.subTest(caso=nome):
                rc, out = self.lint("--sites", self.caso(linha, opcoes))
                self.assertEqual(rc, 2, out)
                self.assertIn(motivo, out)
                self.assertIn("RESULTADO: VERMELHO", out)
                self.assertIn("PERGUNTA_DECISAO.md", out)

    def test_pergunta_em_bloco_markdown_conta_em_outro_bloco_nao(self):
        corpo = "**Sua decisão** — " + PERGUNTA + "\n" + OPCOES
        rc, out = self.lint("--sites", self.escreve(self.tmp, "md.md", "# X\n\n```markdown\n" + corpo + "```\n"))
        self.assertEqual(rc, 2, out)
        self.assertIn("md.md:4 — sem marca de classe", out)
        rc, out = self.lint("--sites", self.escreve(self.tmp, "txt.md", "# X\n\n```text\n" + corpo + "```\n"))
        self.assertEqual(rc, 64, out)

    def test_citacao_e_pasta_com_varios_arquivos(self):
        bom = "> **Sua decisão** — [auto · de rotina] " + PERGUNTA + "\n" + "".join("> " + l + "\n" for l in OPCOES.splitlines())
        self.escreve(self.tmp, "p/a.md", "# A\n\n" + bom)
        self.escreve(self.tmp, "p/sub/b.md", "# B\n\n**Sua decisão** — " + PERGUNTA + "\n" + OPCOES)
        rc, out = self.lint("--sites", self.tmp / "p")
        self.assertEqual(rc, 2, out)
        self.assertIn("b.md:3 — sem marca de classe", out)
        self.assertNotIn("a.md:", out)


class Uso(Base):
    def test_64_caminho_inexistente_zero_perguntas_e_tabela_ausente(self):
        rc, out = self.lint("--sites", self.tmp / "nao-existe")
        self.assertEqual(rc, 64, out)
        rc, out = self.lint("--sites", self.escreve(self.tmp, "vazio.md", "# nada aqui\n"),
                            self.escreve(self.tmp, "vazio2.md", "**Pergunta aberta?** responda com um número\n"))
        self.assertEqual(rc, 64, out)
        self.assertIn("nada conferido nunca é verde", out)
        frag = self.escreve(self.tmp, "frag.md", "# fragmento sem a tabela\n")
        rc, out = self.lint("--sites", self.caso("**Sua decisão** — [auto · de rotina] " + PERGUNTA),
                            env=dict(self.env, PERGUNTA_FRAG=str(frag)))
        self.assertEqual(rc, 64, out)
        self.assertIn("tabela das 6 marcas", out)
        for args in ((), ("--sites",), ("--outra",)):
            with self.subTest(args=args):
                rc, out = self.lint(*args)
                self.assertEqual(rc, 64, out)
                self.assertIn("RESULTADO: ERRO DE USO", out)

    def test_sem_python3_sai_64(self):
        bin_ = self.tmp / "bin"
        bin_.mkdir()
        for f in ("bash", "sh", "sed", "grep", "dirname", "cat"):
            achado = shutil.which(f)
            if achado:
                os.symlink(achado, str(bin_ / f))
        rc, out = self.lint("--sites", RAIZ / ".agents/skills", env=dict(self.env, PATH=str(bin_)))
        self.assertEqual(rc, 64, out)
        self.assertIn("python3 não encontrado", out)


class SelfTest(Base):
    def test_as_4_fixtures_reprovam_e_o_controle_passa(self):
        rc, out = self.lint("--self-test")
        self.assertEqual(rc, 0, out)
        for linha in ("sem-classe → exit 2", "com-outro → exit 2", "com-jargao → exit 2",
                      "dois-recomendados → exit 2", "controle → exit 0", "RESULTADO: VERDE"):
            self.assertIn(linha, out)

    def test_fixture_que_passa_deixa_o_self_test_vermelho(self):
        copia = self.tmp / "pacote"
        copia.mkdir()
        self.copia("sdd", copia)
        shutil.copy(str(RAIZ / "sdd/fixtures/conversa/decisoes/controle.md"),
                    str(copia / "sdd/fixtures/conversa/decisoes/com-jargao.md"))
        rc, out, err = self.roda([BASH, copia / "sdd/bin/sdd-decisoes-lint.sh", "--self-test"], copia)
        self.assertEqual(rc, 1, out + err)
        self.assertIn("🛑 com-jargao", out)
