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
import time
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
    def pacote(self) -> Path:
        """Cópia de sdd/bin e sdd/review para sabotar sem tocar no repositório."""
        p = self.tmp / "pkg"
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
        t0 = time.time()
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
        self.assertLess(time.time() - t0, 120)

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

    def test_extracao_nula_derruba_uma_assercao_de_cada_engine(self):
        for eng in ("claude", "codex", "gemini", "openrouter"):
            with self.subTest(engine=eng):
                p = self.pacote()
                a = p / "sdd/bin/adapters" / (eng + ".sh")
                a.write_text(a.read_text(encoding="utf-8") + NULA, encoding="utf-8")
                rc, out = self.gate(p)
                self.assertEqual(rc, 2, out)
                self.assertRegex(out, r"(?m)^  ❌ \d+\. %s \((revisor|auditor)[^)]*\): (?!engine efetiva)" % eng)
                shutil.rmtree(str(p))

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
