"""sdd/bin/adversarial-review-gate.sh — o gate offline da revisão adversarial (F11: AT-001–AT-013).

O gate roda adversarial-review.sh com os adapters REAIS e stubs por engine (sdd/review/stubs/). Aqui se prova que:
- no pacote como está, ele sai 0 sem rede, e cada asserção diz o que conferiu;
- ele pega o defeito: cada sabotagem (numa cópia de sdd/bin + sdd/review) faz o gate sair 2 nomeando a asserção;
- uma extração toda nula num adapter derruba uma asserção daquela engine (os campos discriminam);
- ele não fura o isolamento: BASH_ENV e função exportada não fazem a CLI real ser chamada;
- sem stub ou sem engine no registry, ele sai 3 antes de qualquer chamada.
Nenhum teste usa rede nem engine de verdade (a chave do gate é falsa e gerada por ele).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

GATE_REL = "sdd/bin/adversarial-review-gate.sh"

NULA = r'''
eval "$(declare -f adapter_extrair | sed '1s/adapter_extrair/_extrair_original/')"
adapter_extrair() {
  _extrair_original "$@" | python3 -c 'import json, sys
d = json.loads(sys.stdin.read().splitlines()[-1])
print(json.dumps({"texto": d.get("texto"), "tokens_entrada": None, "tokens_saida": None, "modelo": None, "custo_usd": None}))'
}
'''


class Gate(Sandbox):
    def pacote(self, nome: str = "pkg") -> Path:
        """Cópia de sdd/bin e sdd/review para sabotar sem tocar no repositório."""
        p = self.tmp / nome
        for d in ("sdd/bin", "sdd/review"):
            shutil.copytree(str(RAIZ / d), str(p / d))
        return p

    def gate(self, raiz: Path = RAIZ, *args, env=None):
        rc, out, err = self.roda([BASH, raiz / GATE_REL, *args], self.tmp, env or self.env)
        return rc, out + err

    def troca(self, arq: Path, antes: str, depois: str):
        t = arq.read_text(encoding="utf-8")
        self.assertEqual(t.count(antes), 1, "âncora da sabotagem não achada em %s: %s" % (arq.name, antes))
        arq.write_text(t.replace(antes, depois), encoding="utf-8")

    def test_pacote_intacto_sai_0_sem_rede(self):
        # o tempo (alvo ≤ 120 s no piso) é medido na evidência local, não asserido aqui: um runner lento da CI não
        # pode avermelhar o gate (revisão real, rodada 1, R2)
        rc, out = self.gate()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: GATE VERDE", out)
        n = int(re.search(r"(?m)^(\d+) asserções, 0 falha\(s\) em \d+ s$", out).group(1))
        self.assertGreaterEqual(n, 80)
        self.assertNotIn("❌", out)
        for rot in ("claude (revisor): custo de total_cost_usd", "codex (auditor): tokens de turn.completed",
                    "gemini (auditor): modelo de stats.models", "openrouter (revisor): modelo e provedor",
                    "a OpenRouter recebeu Authorization: Bearer <chave gerada>", "revisor caiu na engine do auditor"):
            self.assertIn(rot, out)

    def test_verboso_mostra_o_valor_lido(self):
        rc, out = self.gate(RAIZ, "-v")
        self.assertEqual(rc, 0, out)
        self.assertIn("lido: US$ 0.0421", out)
        self.assertIn("lido: qwen/qwen3.7-plus via StubProvider", out)

    def test_uso(self):
        rc, out = self.gate(RAIZ, "--rede")
        self.assertEqual(rc, 64, out)
        rc, out = self.gate(RAIZ, "--help")
        self.assertEqual(rc, 0, out)
        self.assertIn("3 o gate não conseguiu se isolar", out)

    def sabotado(self, arq_rel, antes, depois, rotulo):
        p = self.pacote()
        self.troca(p / arq_rel, antes, depois)
        rc, out = self.gate(p)
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: GATE VERMELHO", out)
        self.assertRegex(out, r"(?m)^  ❌ \d+\. .*%s" % re.escape(rotulo))

    def test_sabotagem_custo_do_claude(self):
        self.sabotado("sdd/bin/adapters/claude.sh",
                      'custo = d.get("total_cost_usd") if', 'custo = None if',
                      "claude (revisor): custo de total_cost_usd")

    def test_sabotagem_tokens_do_codex(self):
        self.sabotado("sdd/bin/adapters/codex.sh", 'elif t == "turn.completed":', 'elif False:',
                      "codex (auditor): tokens de turn.completed")

    def test_sabotagem_modelo_do_gemini(self):
        self.sabotado("sdd/bin/adapters/gemini.sh", 'modelo = "+".join(nomes) or None', 'modelo = None',
                      "gemini (auditor): modelo de stats.models")

    def test_sabotagem_custo_da_openrouter(self):
        self.sabotado("sdd/bin/adapters/openrouter.sh",
                      'custo = u.get("cost") if isinstance', 'custo = None if isinstance',
                      "openrouter (auditor): custo de usage.cost")

    def test_sabotagem_exclusao_dentro_do_papel(self):
        self.sabotado("sdd/bin/adversarial-review.sh", "        if chave(d) in excluir:", "        if False:",
                      "revisor caiu na engine do auditor")

    def test_sabotagem_tarifa_do_modelo_configurado(self):
        self.sabotado("sdd/bin/adversarial-review.sh",
                      'reportado if reportado and reportado != d["modelo"] else d["modelo"]', 'd["modelo"]',
                      "openrouter (revisor, modelo-sem-preco): custo estimado pelo precos.tsv")

    def test_aval1_m1_parser_que_so_aceita_agree_e_pego(self):
        self.sabotado("sdd/bin/adversarial-review.sh",
                      'j.get("veredito") in ("AGREE", "DISAGREE_EVIDENCE", "DISAGREE_CONCERN", "NOVO")',
                      'j.get("veredito") in ("AGREE",)', "auditor com DISAGREE e NOVO")

    def test_aval1_l1_custo_do_claude_lido_do_modelusage_e_pego(self):
        self.sabotado("sdd/bin/adapters/claude.sh",
                      'custo = d.get("total_cost_usd") if isinstance(d.get("total_cost_usd"), (int, float)) else None',
                      'custo = sum((v or {}).get("costUSD") or 0 for v in mu.values()) if mu else None',
                      "claude (revisor): custo de total_cost_usd")

    def test_aval1_l2_sinal_de_credencial_de_cada_engine(self):
        # os 4 sinais inertes numa cópia só: cada cenário 65 é independente e nomeia a própria engine
        # (uma execução do gate em vez de 4 — o tempo da suíte no macOS, revisão real rodada 1, R1@claude)
        p = self.pacote()
        reg = p / "sdd/review/registry.tsv"
        linhas = []
        for ln in reg.read_text(encoding="utf-8").splitlines():
            c = ln.split("\t")
            if len(c) == 9 and not ln.startswith("#"):
                c[6] = "(?i)(NUNCA-CASA-XYZ)"
                ln = "\t".join(c)
            linhas.append(ln)
        reg.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        rc, out = self.gate(p)
        self.assertEqual(rc, 2, out)
        for eng in ("claude", "codex", "gemini", "openrouter"):
            with self.subTest(engine=eng):
                self.assertRegex(out, r"(?m)^  ❌ \d+\. falha de credencial \(%s\)" % eng)

    def test_aval2_l1_severidade_do_novo_e_conferida(self):
        self.sabotado("sdd/bin/adversarial-review.sh",
                      '            j["severidade"] = "MED" if s == "MEDIUM" else s\n',
                      '            j["severidade"] = "HIGH"\n', "auditor com DISAGREE e NOVO: jsonl")

    def test_aval2_h1_git_dir_herdado_de_um_hook_nao_toca_o_repositorio_do_usuario(self):
        # um hook numa worktree exporta GIT_DIR e GIT_INDEX_FILE absolutos: o gate não pode commitar no repo de quem
        # o chamou, nem trocar a branch dele
        r = self.repo("usuario")
        self.git(r, "checkout", "-q", "-b", "main")
        self.escreve(r, "a.txt", "a\n")
        self.commit(r, "base")
        wt = self.tmp / "wt"
        self.git(r, "worktree", "add", "-q", str(wt), "-b", "minha-feature")
        self.escreve(wt, "meu.txt", "trabalho\n")
        self.git(wt, "add", "meu.txt")
        gd = self.git(wt, "rev-parse", "--absolute-git-dir").strip()
        antes = (self.git(wt, "rev-parse", "HEAD").strip(), self.git(r, "branch", "--list").strip())
        fora = self.tmp / "fora"
        fora.mkdir()
        rc, out, err = self.roda([BASH, RAIZ / GATE_REL], fora,
                                 dict(self.env, GIT_DIR=gd, GIT_INDEX_FILE=gd + "/index", GIT_WORK_TREE=str(wt)))
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self.git(wt, "branch", "--show-current").strip(), "minha-feature")
        self.assertEqual((self.git(wt, "rev-parse", "HEAD").strip(), self.git(r, "branch", "--list").strip()), antes)
        self.assertEqual(self.git(wt, "diff", "--cached", "--name-only").strip(), "meu.txt")

    def test_extracao_nula_derruba_uma_assercao_de_cada_engine(self):
        # as 4 extrações nulas numa cópia só: as asserções de campo são por engine, então cada uma aparece pelo
        # próprio nome (uma execução do gate em vez de 4)
        p = self.pacote()
        for eng in ("claude", "codex", "gemini", "openrouter"):
            a = p / "sdd/bin/adapters" / (eng + ".sh")
            a.write_text(a.read_text(encoding="utf-8") + NULA, encoding="utf-8")
        rc, out = self.gate(p)
        self.assertEqual(rc, 2, out)
        for eng in ("claude", "codex", "gemini", "openrouter"):
            with self.subTest(engine=eng):
                self.assertRegex(out, r"(?m)^  ❌ \d+\. %s \((revisor|auditor)[^)]*\): (?!engine efetiva)" % eng)

    def test_real1_caminho_com_metacaractere_de_shell(self):
        # R1@codex: o wrapper gerado não pode expandir $ nem crase do caminho do pacote
        p = self.pacote("pkg $ZZ_NAO_DEFINIDA `x` 'a'")
        rc, out = self.gate(p)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: GATE VERDE", out)

    def test_real1_cenario_ausente_sai_3_antes_de_qualquer_chamada(self):
        # R3@claude: "nada foi chamado" tem de ser verdade — a tabela é conferida no pré-voo
        p = self.pacote()
        cen = p / "sdd/review/stubs/cenarios.tsv"
        cen.write_text("\n".join(l for l in cen.read_text(encoding="utf-8").splitlines()
                                 if not l.startswith("gemini\tauditor-misto\t")) + "\n", encoding="utf-8")
        rc, out = self.gate(p)
        self.assertEqual(rc, 3, out)
        self.assertIn("gemini/auditor-misto", out)
        self.assertNotIn("✅", out)

    def test_preco_atualizado_no_projeto_nao_quebra_o_gate(self):
        p = self.pacote()
        precos = p / "sdd/review/precos.tsv"
        precos.write_text(precos.read_text(encoding="utf-8").replace("\t0.32\t1.28\t", "\t0.40\t1.60\t"),
                          encoding="utf-8")
        rc, out = self.gate(p)
        self.assertEqual(rc, 0, out)

    def test_bash_env_e_funcao_exportada_nao_chamam_a_cli_real(self):
        real = self.tmp / "real"
        real.mkdir()
        marca = self.tmp / "marca"
        (real / "claude").write_text("#!/bin/sh\necho chamada-real >> '%s'\nexit 0\n" % marca, encoding="utf-8")
        (real / "claude").chmod(0o755)
        rc_env = self.tmp / "bashenv.sh"
        rc_env.write_text('PATH="%s:$PATH"\n' % real, encoding="utf-8")
        for nome, extra in (("BASH_ENV", {"BASH_ENV": str(rc_env)}),
                            ("BASH_FUNC", {"BASH_FUNC_claude%%": "() {  echo chamada-funcao >> '%s'; }" % marca})):
            with self.subTest(caso=nome):
                rc, out = self.gate(RAIZ, env=dict(self.env, **extra))
                self.assertEqual(rc, 0, out)
                self.assertFalse(marca.exists(), "a CLI real foi chamada: " + (marca.read_text() if marca.exists() else ""))

    def test_sem_stub_sai_3_antes_de_chamar(self):
        p = self.pacote()
        (p / "sdd/review/stubs/codex.py").unlink()
        rc, out = self.gate(p)
        self.assertEqual(rc, 3, out)
        self.assertIn("stub ausente", out)
        self.assertIn("RESULTADO: GATE QUEBRADO", out)
        self.assertNotIn("✅", out)

    def test_registry_sem_engine_sai_3(self):
        p = self.pacote()
        reg = p / "sdd/review/registry.tsv"
        reg.write_text("\n".join(l for l in reg.read_text(encoding="utf-8").splitlines() if not l.startswith("gemini\t"))
                       + "\n", encoding="utf-8")
        rc, out = self.gate(p)
        self.assertEqual(rc, 3, out)
        self.assertIn("não tem a engine gemini", out)
