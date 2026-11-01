"""sdd/bin/adversarial-review.sh — revisor → auditor sobre um diff congelado (F10), dos dois lados.

Cada teste roda o script do pacote de verdade, por subprocess, num repositório git temporário, com as
engines simuladas pelo adapter de teste `sdd/fixtures/revisao/adapters/stub.sh` (SDD_REVIEW_ADAPTERS) e o
registry `sdd/fixtures/revisao/registry-stub.tsv`. O contrato é o exit, as linhas do META.txt e da saída.

Nenhum teste usa rede nem engine de verdade: o ambiente perde OPENROUTER_API_KEY, o PATH só tem as
ferramentas listadas em FERRAMENTAS (sem claude, codex ou gemini) e a URL do OpenRouter aponta para uma
porta fechada. Um defeito na exclusão de papéis nunca gasta dinheiro de verdade.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

from apoio import BASH, RAIZ, Sandbox

AR = RAIZ / "sdd/bin/adversarial-review.sh"
FLUXO = RAIZ / "sdd/bin/sdd-fluxo.sh"
FXR = RAIZ / "sdd/fixtures/revisao"
REG_STUB = FXR / "registry-stub.tsv"
FERRAMENTAS = ("git", "bash", "sh", "cp", "ls", "grep", "tr", "cat", "mkdir", "sleep", "dirname", "sed", "env",
               "rm", "printf", "wc", "head", "tail", "awk")


def ler(p) -> str:
    return Path(p).read_text(encoding="utf-8")


def meta(pasta: Path) -> dict:
    out = {}
    for ln in ler(pasta / "META.txt").splitlines():
        m = re.match(r"^(\S+)\s*:\s*(.*?)\s*$", ln)
        if m:
            out[m.group(1)] = m.group(2)
    return out


class Base(Sandbox):
    def setUp(self):
        super().setUp()
        binp = self.tmp / "bin"
        binp.mkdir()
        for f in FERRAMENTAS:
            w = shutil.which(f)
            if w:
                (binp / f).symlink_to(w)
        (binp / "python3").symlink_to(sys.executable)
        self.estado = self.tmp / "estado"
        self.env = dict(self.env, PATH=str(binp), SDD_REVIEW_ADAPTERS=str(FXR / "adapters"),
                        SDD_REVIEW_ESPERA="0", SDD_REVIEW_STUB_ESTADO=str(self.estado),
                        SDD_REVIEW_OPENROUTER_URL="http://127.0.0.1:9/")
        self.env.pop("OPENROUTER_API_KEY", None)
        self.env.pop("SDD_REVIEW_STUB_CUSTO", None)

    def projeto(self, registry=REG_STUB, extra_cfg="", ignorar=True) -> Path:
        r = self.repo()
        self.git(r, "checkout", "-q", "-b", "main")
        self.escreve(r, "src/conta.sh", "a\n")
        self.commit(r, "base")
        self.git(r, "checkout", "-q", "-b", "feat")
        self.escreve(r, "src/conta.sh", "a\nb\n")
        self.escreve(r, "src/novo.sh", "novo\n")
        self.escreve(r, "sdd/config.yaml", "review:\n  registry: %s\n%s" % (registry, extra_cfg))
        if ignorar:
            with open(r / ".git/info/exclude", "a", encoding="utf-8") as h:
                h.write("sdd/reports/reviews/\n")
        return r

    def ar(self, r: Path, *args, env=None):
        rc, out, err = self.roda([BASH, AR, *args], r, env or self.env)
        return rc, out + err

    def rev(self, r: Path, *args, base="main"):
        return self.ar(r, "--base", base, *args)

    def pasta(self, r: Path) -> Path:
        ps = sorted((r / "sdd/reports/reviews").glob("EXTERNAL_REVIEW_*"))
        self.assertTrue(ps, "nenhuma pasta de revisão")
        return ps[-1]

    def chamadas(self) -> int:
        return len(list(self.estado.glob("prompt-*"))) if self.estado.exists() else 0

    def registry(self, linhas) -> Path:
        d = self.tmp / "reg"
        d.mkdir(exist_ok=True)
        cab = [l for l in ler(REG_STUB).splitlines() if l.startswith("#")]
        p = d / "registry.tsv"
        p.write_text("\n".join(cab + ["\t".join(x) for x in linhas]) + "\n", encoding="utf-8")
        return p

    @staticmethod
    def linha(eng, modelo, cobranca="assinatura", adapter="stub", timeout="5", papeis="revisor,auditor,desempate"):
        return [eng, adapter, modelo, cobranca, papeis, timeout, "FALHA-AUTH", "FALHA-429", "FALHA-QUOTA"]


class Registry(Base):
    """AT-001, AT-003, AT-021, AT-034."""

    def test_registry_de_fabrica_tem_as_4_engines_com_9_colunas_e_sem_cadeia(self):
        dados = [l.split("\t") for l in ler(RAIZ / "sdd/review/registry.tsv").splitlines()
                 if l.strip() and not l.startswith("#")]
        self.assertEqual([d[0] for d in dados], ["claude", "codex", "gemini", "openrouter"])
        self.assertTrue(all(len(d) == 9 for d in dados))
        texto = ler(RAIZ / "sdd/review/registry.tsv")
        for col in ("engine", "adapter", "modelo", "cobranca", "papeis", "timeout_s", "sinal_auth",
                    "sinal_transitorio", "sinal_persistente"):
            self.assertIn(col, texto)
        self.assertIn("-s read-only", ler(RAIZ / "sdd/bin/adapters/codex.sh"))
        self.assertIn("Não há cadeia padrão", texto)
        cfg = ler(RAIZ / "sdd/config.example.yaml")
        for slot in ('registry: sdd/review/registry.tsv', 'revisor1: ""', 'auditor: ""',
                     "output_dir: sdd/reports/reviews", "context_max_kb: 180", 'security_globs: ""'):
            self.assertIn(slot, cfg)
        self.assertNotRegex(cfg, r"(?m)^\s+vendors:")

    def test_precos_tem_fonte_url_e_data_iso(self):
        for ln in ler(RAIZ / "sdd/review/precos.tsv").splitlines():
            if ln.startswith("#") or not ln.strip():
                continue
            c = ln.split("\t")
            self.assertEqual(len(c), 6, ln)
            float(c[2]), float(c[3])
            self.assertTrue(c[4].startswith("https://"), ln)
            self.assertRegex(c[5], r"^\d{4}-\d{2}-\d{2}$")

    def test_sem_revisor_slot_vazio_e_64_sem_chamar_engine(self):
        r = self.projeto()
        rc, out = self.rev(r)
        self.assertEqual(rc, 64, out)
        self.assertIn("review.revisor1", out)
        self.assertIn("RESULTADO: PAROU", out)
        self.assertEqual(self.chamadas(), 0)

    def test_id_desconhecido_lista_as_validas(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "nao-existe", "--auditor", "stub-b")
        self.assertEqual(rc, 64, out)
        self.assertIn("engine desconhecida: 'nao-existe'", out)
        self.assertIn("stub-a, stub-b, stub-c, stub-d", out)

    def test_linha_do_registry_com_8_colunas_e_64(self):
        reg = self.tmp / "ruim.tsv"
        reg.write_text("stub-a\tstub\tx\tassinatura\trevisor\t5\ta\tb\n", encoding="utf-8")
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-a", "--um-engine")
        self.assertEqual(rc, 64, out)
        self.assertIn("tem 8 colunas (esperado 9", out)

    def test_slots_e_lista_vem_do_config(self):
        r = self.projeto(extra_cfg="  revisor1: stub-a:falha-quota, stub-c\n  auditor: stub-b\n")
        rc, out = self.rev(r, "--no-revisor2")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["reviewer_engine_default"], "stub-a:falha-quota")
        self.assertEqual(m["reviewer_engine_efetivo"], "stub-c")


class Exclusao(Base):
    """AT-004, AT-005."""

    def test_auditor_igual_ao_revisor_e_67_sem_chamar_nada(self):
        r = self.projeto(extra_cfg="  revisor1: stub-a\n  auditor: stub-a\n")
        rc, out = self.rev(r)
        self.assertEqual(rc, 67, out)
        self.assertIn("RESULTADO: PAROU", out)
        self.assertIn("→ escolha outra engine para auditar (review.auditor) ou rode com --um-engine", out)
        self.assertEqual(self.chamadas(), 0)
        self.assertFalse((r / "sdd/reports/reviews").exists())

    def test_um_engine_grava_diversidade_nenhuma_e_avisa_primeiro(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-ok+auditor-agree", "--um-engine", "--no-revisor2",
                           "--feature", "X")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["diversidade"], "nenhuma")
        avisos = [l for l in out.splitlines() if l.startswith("⚠️")]
        self.assertEqual(avisos[0], "⚠️ a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos "
                                    "da revisão")
        self.assertLess(out.index(avisos[0]), out.index("▶"))
        self.assertEqual(out.count(avisos[0]), 1)
        self.assertEqual(self.chamadas(), 2)

    def test_diversidade_modelo_e_vendor(self):
        r = self.projeto()
        self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(meta(self.pasta(r))["diversidade"], "modelo")
        ad = self.tmp / "adapters"
        ad.mkdir()
        shutil.copy(str(FXR / "adapters/stub.sh"), str(ad / "stub.sh"))
        shutil.copy(str(FXR / "adapters/stub.sh"), str(ad / "outro.sh"))
        reg = self.registry([self.linha("stub-a", "revisor-ok"), self.linha("x-b", "auditor-agree", adapter="outro")])
        r2 = self.tmp / "r2"
        shutil.copytree(str(r), str(r2))
        self.escreve(r2, "sdd/config.yaml", "review:\n  registry: %s\n" % reg)
        env = dict(self.env, SDD_REVIEW_ADAPTERS=str(ad), SDD_REVIEW_STUB_RESPOSTAS=str(FXR / "respostas"))
        rc, out = self.ar(r2, "--base", "main", "--reviewer", "stub-a", "--auditor", "x-b", "--no-revisor2", env=env)
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r2))["diversidade"], "vendor")


class Diff(Base):
    """AT-006, AT-007, AT-024."""

    def test_inclui_nao_rastreado_exclui_artefatos_sdd_e_a_pasta_de_saida(self):
        r = self.projeto()
        self.escreve(r, "sdd/features/DEFINE_X.md", "def\n")
        self.escreve(r, "sdd/reports/BUILD_REPORT_X.md", "rep\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r)
        patch = (p / "diff.patch").read_bytes()
        self.assertIn(b"b/src/novo.sh", patch)
        self.assertNotIn(b"sdd/features", patch)
        self.assertNotIn(b"sdd/reports", patch)
        m = meta(p)
        self.assertRegex(m["diff_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(m["diff_sha256"], hashlib.sha256(patch).hexdigest())
        self.assertEqual(self.git(r, "status", "--porcelain").count("?? src/novo.sh"), 1)

    def test_paths_inclui_o_que_nomeia(self):
        r = self.projeto()
        self.escreve(r, "sdd/features/DESIGN_X.md", "design\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2",
                           "--paths", "sdd/features/DESIGN_X.md")
        self.assertEqual(rc, 0, out)
        patch = (self.pasta(r) / "diff.patch").read_bytes()
        self.assertIn(b"sdd/features/DESIGN_X.md", patch)
        self.assertNotIn(b"src/novo.sh", patch)

    def test_config_do_usuario_nao_muda_o_sha(self):
        r = self.projeto()
        self.rev(r, "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        _, a = self.rev(r, "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.git(r, "config", "diff.noprefix", "true")
        self.git(r, "config", "diff.algorithm", "patience")
        _, b = self.rev(r, "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        sha = lambda s: re.search(r"diff_sha256: ([0-9a-f]{64})", s).group(1)
        self.assertEqual(sha(a), sha(b))

    def test_funciona_numa_worktree(self):
        r = self.projeto()
        self.commit(r, "feat")
        wt = self.tmp / "wt"
        self.git(r, "worktree", "add", "-q", "-b", "outra", str(wt), "feat")
        self.escreve(wt, "src/da-worktree.sh", "x\n")
        rc, out = self.rev(wt, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertIn(b"src/da-worktree.sh", (self.pasta(wt) / "diff.patch").read_bytes())

    def test_diff_vazio_base_invalida_e_acima_de_8_mb_sao_64(self):
        r = self.projeto()
        self.commit(r, "tudo")
        rc, out = self.ar(r, "--base", "feat", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 64, out)
        self.assertIn("está vazio", out)
        rc, out = self.ar(r, "--base", "nao-existe", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 64, out)
        self.assertIn("não resolve para um commit", out)
        self.escreve(r, "grande.txt", ("x" * 99 + "\n") * 90000)
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 64, out)
        self.assertIn("acima do teto de 8 MB", out)
        self.assertEqual(self.chamadas(), 0)

    def test_dry_run_nao_chama_engine_nem_cria_pasta(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--dry-run")
        self.assertEqual(rc, 0, out)
        for trecho in ("nada foi enviado a nenhuma engine", "revisor : stub-a", "auditor : stub-b",
                       "diff_sha256: ", "RESULTADO: PLANO"):
            self.assertIn(trecho, out)
        self.assertEqual(self.chamadas(), 0)
        self.assertFalse((r / "sdd/reports/reviews").exists())


class Contexto(Base):
    """AT-008, AT-009."""

    def test_contexto_na_ordem_e_brainstorm_sai_primeiro(self):
        r = self.projeto(extra_cfg="  context_max_kb: 2\n")
        self.escreve(r, "sdd/features/BRAINSTORM_X.md", "B" * 3000 + "\n")
        self.escreve(r, "sdd/features/DEFINE_X.md", "definição\n")
        self.escreve(r, "sdd/features/DESIGN_X.md", "desenho\n")
        self.escreve(r, "sdd/reports/BUILD_REPORT_X.md", "relatório\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2", "--feature", "X")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r)
        m = meta(p)
        self.assertEqual(m["docs_sdd"], "DEFINE_X.md, DESIGN_X.md, BUILD_REPORT_X.md")
        self.assertEqual(m["contexto_cortado"], "BRAINSTORM")
        ctx = ler(p / "context-sdd.md")
        self.assertNotIn("BBBB", ctx)
        self.assertLess(ctx.index("DEFINE_X.md"), ctx.index("DESIGN_X.md"))
        self.assertLess(ctx.index("DESIGN_X.md"), ctx.index("BUILD_REPORT_X.md"))
        self.assertIn("definição", ler(sorted(self.estado.glob("prompt-*"))[0]))
        self.assertNotIn("⚠️ sem --feature", out)

    def test_sem_feature_avisa(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertIn("⚠️ sem --feature: a revisão não leu BRAINSTORM, DEFINE nem DESIGN, e decisões já "
                      "documentadas podem voltar como achado", out)
        self.assertEqual(meta(self.pasta(r))["docs_sdd"], "-")

    def test_pasta_nao_ignorada_e_64_com_o_comando_que_resolve_tambem_na_worktree(self):
        r = self.projeto(ignorar=False)
        self.commit(r, "feat")
        wt = self.tmp / "wt"
        self.git(r, "worktree", "add", "-q", "-b", "outra", str(wt), "feat")
        self.escreve(wt, "src/x.sh", "x\n")
        rc, out = self.rev(wt, "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 64, out)
        self.assertIn("🛑 a pasta sdd/reports/reviews não está ignorada pelo git: o diff e as respostas das "
                      "engines iriam para o repositório.", out)
        cmd = re.search(r"→ rode: (.+)$", out, re.M).group(1)
        self.assertIn('"$(git rev-parse --git-common-dir)/info/exclude"', cmd)
        self.assertEqual(self.chamadas(), 0)
        rc2, _, err = self.roda([BASH, "-c", cmd], wt, self.env)
        self.assertEqual(rc2, 0, err)
        rc, out = self.rev(wt, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)


class Vereditos(Base):
    """AT-011, AT-012, AT-013, AT-022, AT-023."""

    def test_revisao_completa_grava_tudo_e_o_loop_le(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2", "--feature", "X")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r)
        self.assertIn("<<<VERDICTS", ler(p / "reviewer.md"))
        rv = ler(p / "reviewer.verdicts.jsonl").splitlines()
        self.assertEqual(len(rv), 2)
        for k in ('"achado": "R1"', '"severidade": "HIGH"', '"confianca"', '"arquivo"', '"linha"', '"resumo"'):
            self.assertIn(k, rv[0])
        self.assertIn('"veredito": "AGREE"', ler(p / "auditor.verdicts.jsonl"))
        m = meta(p)
        self.assertEqual((m["reviewer_exit"], m["auditor_exit"], m["convergencia_1o_passe"]), ("0", "0", "sim"))
        linhas = out.splitlines()
        self.assertIn("RESULTADO: REVIEW COMPLETA", linhas)
        self.assertIn("achados: 1 grave, 1 médio, 0 leves", linhas)
        self.assertTrue(linhas[-1].startswith("→ rode: bash sdd/bin/sdd-fluxo.sh loop --review "))
        rc2, _, _ = self.roda([BASH, FLUXO, "loop", "--review", p, "--rodada", "1"], r, self.env)
        self.assertEqual(rc2, 10)

    def test_bloco_vazio_e_zero_achados(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-vazio", "--auditor", "stub-b:auditor-vazio",
                           "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["reviewer_achados"], "0")
        self.assertEqual(ler(self.pasta(r) / "reviewer.verdicts.jsonl"), "")

    def test_revisor_sem_bloco_e_68_e_nunca_zero_achados(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-sem-bloco", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 68, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["reviewer_exit"], "68")
        self.assertIn("bloco <<<VERDICTS ausente", m["reviewer_motivo"])
        self.assertIn("RESULTADO: REVIEW INVÁLIDA", out)
        self.assertIn("revisor (stub-a:revisor-sem-bloco): a engine respondeu fora do formato; isto não é zero "
                      "achados", out)
        self.assertNotIn("achados: ", out)
        self.assertEqual(m["convergencia_1o_passe"], "n/a (auditor não rodou)")

    def test_auditor_sem_bloco_e_68(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b:auditor-sem-bloco", "--no-revisor2")
        self.assertEqual(rc, 68, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["reviewer_exit"], m["auditor_exit"]), ("0", "68"))
        self.assertEqual(m["convergencia_1o_passe"], "n/a (auditor falhou)")
        self.assertIn("→ rode de novo; se repetir, troque a engine do auditor", out)

    def test_convergencia_nao_com_refutacao(self):
        r = self.projeto()
        rc, _ = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b:auditor-refuta-high", "--no-revisor2",
                         "--no-desempate")
        self.assertEqual(rc, 0)
        m = meta(self.pasta(r))
        self.assertEqual((m["convergencia_1o_passe"], m["desempate_alvo"]), ("nao", "-"))

    def test_linha_de_inicio_por_papel(self):
        r = self.projeto()
        _, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertIn("▶ revisor: stub-a (revisor-ok) — até 1 min", out)
        self.assertIn("▶ auditor: stub-b (auditor-agree) — até 1 min", out)


class SegundoRevisor(Base):
    """AT-014, AT-015."""

    def test_gatilhos_e_constantes(self):
        texto = ler(AR)
        for c in ("SEGUNDO_REVISOR_MIN_ARQUIVOS = 8", "SEGUNDO_REVISOR_MIN_KB = 120", "SEGUNDO_REVISOR_MIN_CAMADAS = 2",
                  "RASO_SEGUNDOS = 30", "DIFF_MAX_MB = 8"):
            self.assertIn(c, texto)
        casos = (
            ("segurança", {"src/auth/login.sh": "x\n"}, "", "segurança (src/auth/login.sh)"),
            ("8 arquivos", {"src/f%d.sh" % k: "x\n" for k in range(7)}, "", "10 arquivos (limiar 8)"),
            ("120 KB", {"src/grande.txt": "y" * 130 * 1024}, "", "KB (limiar 120)"),
            ("2 camadas", {"api/a.sh": "x\n", "ui/b.sh": "x\n"}, "layers:\n  api: \"api/**\"\n  ui: \"ui/**\"\n",
             "camadas (limiar 2)"),
        )
        for nome, arqs, cfg, esperado in casos:
            with self.subTest(gatilho=nome):
                self.tmp_sub = self.tmp / nome.replace(" ", "")
                r = self.projeto(extra_cfg=cfg)
                for k, v in arqs.items():
                    self.escreve(r, k, v)
                rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--dry-run")
                self.assertIn(esperado, out)
                shutil.rmtree(str(r))

    def test_author_nao_e_superficie_de_seguranca(self):
        r = self.projeto()
        self.escreve(r, "docs/author.md", "x\n")
        _, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--dry-run")
        self.assertIn("sem gatilho no diff", out)

    def test_raso_aciona_o_segundo_revisor(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-vazio", "--auditor", "stub-b:auditor-agree-dois")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["revisor1_raso"], "sim")
        self.assertRegex(m["gatilho_2o_revisor"], r"^revisor1 raso \(\d+s, 0 achados\)$")
        self.assertEqual(m["revisor2_engine"], "stub-c")
        self.assertIn("⚠️ o revisor terminou em", out)

    def test_escolhe_a_primeira_disponivel_fora_do_revisor_e_do_auditor_e_rotula(self):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b:auditor-agree-dois")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r)
        m = meta(p)
        self.assertEqual((m["revisor2_engine"], m["revisor2_exit"]), ("stub-c", "0"))
        self.assertIn('"achado": "R1@stub-a"', ler(p / "reviewer.verdicts.jsonl"))
        self.assertIn('"achado": "R1@stub-c"', ler(p / "reviewer2.verdicts.jsonl"))
        self.assertIn("R1@stub-a", ler(sorted(self.estado.glob("prompt-*"))[-1]))

    def test_indisponivel_registra_67_avisa_e_o_auditor_roda(self):
        reg = self.registry([self.linha("stub-a", "revisor-ok"), self.linha("stub-b", "auditor-agree"),
                             self.linha("stub-c", "off-revisor-ok")])
        r = self.projeto(registry=reg)
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["revisor2_engine"], m["revisor2_exit"], m["auditor_exit"]), ("indisponível", "67", "0"))
        self.assertIn("⚠️ o 2º revisor (nenhuma engine) não tinha engine disponível", out)
        rc2, o2, _ = self.roda([BASH, FLUXO, "loop", "--review", self.pasta(r), "--rodada", "1"], r, self.env)
        self.assertEqual(rc2, 20, o2)

    def test_segundo_revisor_que_falha_nao_derruba_a_cadeia(self):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--revisor2", "stub-c:falha-auth")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["revisor2_exit"], m["auditor_exit"]), ("65", "0"))
        self.assertIn("⚠️ o 2º revisor (stub-c:falha-auth) falhou", out)
        self.assertIn("RESULTADO: REVIEW COMPLETA", out)

    def test_no_revisor2_registra_o_porque(self):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        m = meta(self.pasta(r))
        self.assertEqual(m["gatilho_2o_revisor"], "segurança (src/auth/login.sh) — dispensado por --no-revisor2")
        self.assertEqual(m["revisor2_engine"], "-")


class Desempate(Base):
    """AT-016, AT-030."""

    def reg(self, d_modelo="desempate-refutado"):
        return self.registry([self.linha("stub-a", "revisor-ok"), self.linha("stub-b", "auditor-refuta-high"),
                              self.linha("stub-d", d_modelo)])

    def test_refutado_fecha_no_loop(self):
        r = self.projeto(registry=self.reg())
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r)
        m = meta(p)
        self.assertEqual((m["desempate_alvo"], m["desempate_engine"], m["desempate_decisao"]),
                         ("R1", "stub-d", "DECISAO:REFUTADO"))
        rc2, o2, _ = self.roda([BASH, FLUXO, "loop", "--review", p, "--rodada", "1"], r, self.env)
        self.assertEqual(rc2, 0, o2)

    def test_sem_engine_elegivel_e_sem_desempate(self):
        reg = self.registry([self.linha("stub-a", "revisor-ok"), self.linha("stub-b", "auditor-refuta-high")])
        r = self.projeto(registry=reg)
        self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(meta(self.pasta(r))["desempate_engine"], "indisponível")
        rc, _ = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2", "--no-desempate")
        self.assertEqual(meta(self.pasta(r))["desempate_alvo"], "-")

    def test_desempate_sem_decisao_nao_muda_o_exit(self):
        r = self.projeto(registry=self.reg("revisor-vazio"))
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["desempate_decisao"], "-")
        self.assertIn("⚠️ o desempate (stub-d) não decidiu", out)


class Falhas(Base):
    """AT-017, AT-018, AT-019."""

    def test_auth_para_sem_chamar_a_proxima(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-auth,stub-c", "--auditor", "stub-b")
        self.assertEqual(rc, 65, out)
        self.assertEqual(self.chamadas(), 1)
        self.assertIn("RESULTADO: PAROU", out)
        self.assertIn("→ confira a credencial de stub-a:falha-auth (credencial do stub (exemplo de teste)); a revisão "
                      "não troca de engine por falha de credencial", out)

    def test_sinal_dentro_de_resposta_valida_nao_e_falha(self):
        resp = self.tmp / "resp"
        shutil.copytree(str(FXR / "respostas"), str(resp))
        (resp / "cita.md").write_text("A mensagem FALHA-AUTH e o FALHA-QUOTA aparecem no log do app.\n\n"
                                      "<<<VERDICTS\nVERDICTS>>>\n", encoding="utf-8")
        env = dict(self.env, SDD_REVIEW_STUB_RESPOSTAS=str(resp))
        r = self.projeto()
        (resp / "cita2.md").write_text((resp / "cita.md").read_text(encoding="utf-8"), encoding="utf-8")
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a:cita", "--auditor", "stub-b:cita2",
                          "--no-revisor2", env=env)
        self.assertEqual(rc, 0, out)

    def test_429_tenta_de_novo_na_mesma_engine(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-429+revisor-ok", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["reviewer_engine_efetivo"], "stub-a:falha-429+revisor-ok")
        self.assertEqual(self.chamadas(), 3)

    def test_429_persistente_faz_3_chamadas_e_avanca(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-429,stub-c", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self.chamadas(), 5)
        self.assertIn("seguiu no limite passageiro (429) depois de 3 tentativas", meta(self.pasta(r))["reviewer_motivo"])

    def test_quota_avanca_registra_e_avisa(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-quota,stub-c", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["reviewer_engine_default"], m["reviewer_engine_efetivo"], m["reviewer_fallback_usado"]),
                         ("stub-a:falha-quota", "stub-c", "sim"))
        self.assertIn("⚠️ o revisor previsto (stub-a:falha-quota) falhou", out)
        self.assertIn("quem revisou foi stub-c", out)

    def test_lista_esgotada_67_e_so_cli_ausente_66(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-quota", "--auditor", "stub-b")
        self.assertEqual(rc, 67, out)
        self.assertIn("→ acrescente outra engine à lista ou tente mais tarde", out)
        rc, out = self.rev(r, "--reviewer", "stub-a:sem-cli", "--auditor", "stub-b")
        self.assertEqual(rc, 66, out)

    def test_tempo_esgotado_mata_e_avanca(self):
        reg = self.registry([self.linha("stub-a", "dorme", timeout="1"), self.linha("stub-b", "auditor-agree"),
                             self.linha("stub-c", "revisor-ok")])
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "stub-a,stub-c", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertIn("stub-a passou do teto de tempo", meta(self.pasta(r))["reviewer_motivo"])


class Custo(Base):
    """AT-020."""

    def test_quatro_formas_e_nunca_zero_desconhecido(self):
        reg = self.registry([self.linha("stub-a", "revisor-ok", "assinatura"),
                             self.linha("stub-b", "auditor-agree", "pay-per-token"),
                             self.linha("stub-c", "revisor2-ok", "desconhecida")])
        (reg.parent / "precos.tsv").write_text("stub-b\tauditor-agree\t1.0\t2.0\thttps://exemplo.example/precos\t"
                                               "2026-10-31\n", encoding="utf-8")
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["reviewer_custo"], "assinatura")
        self.assertEqual(m["auditor_custo"], "≈US$ 0.0014")
        self.assertIn("revisor: stub-a (stub-modelo) — incluído na assinatura", out)
        self.assertIn("≈ US$ 0,0014 (estimado)", out)
        rc, out = self.rev(r, "--reviewer", "stub-c", "--auditor", "stub-a:auditor-agree", "--no-revisor2")
        m = meta(self.pasta(r))
        self.assertEqual(m["reviewer_custo"], "$?")
        self.assertIn("custo desconhecido", out)
        self.assertIn("(+ 1 papel(is) com custo desconhecido)", out)
        self.assertNotRegex(ler(self.pasta(r) / "META.txt"), r"reviewer_custo\s*:\s*(0|US\$ 0\.0000)")
        env = dict(self.env, SDD_REVIEW_STUB_CUSTO="0.0123")
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-c", "--auditor", "stub-a:auditor-agree", "--no-revisor2",
                          env=env)
        m = meta(self.pasta(r))
        self.assertEqual((m["reviewer_custo"], m["reviewer_tokens_entrada"], m["reviewer_tokens_total"]),
                         ("US$ 0.0123", "1000", "1200"))
        self.assertTrue(m["custo_total"].startswith("US$ 0.0246"))


class Conferir(Base):
    """AT-025, AT-026."""

    def revisado(self, *extra):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", *extra)
        self.assertEqual(rc, 0, out)
        return r

    def test_confere_e_deixa_de_conferir_com_1_byte(self):
        r = self.revisado("--no-revisor2")
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r).relative_to(r)
        self.assertIn("✅ a revisão %s é desta versão do código (sha256 igual)." % p, out)
        self.assertRegex(out, r"(?m)^review_externo: %s sha256=[0-9a-f]{64} diversidade=modelo$" % re.escape(str(p)))
        self.assertIn("RESULTADO: CONFERE", out)
        self.commit(r, "commit depois da revisão")
        rc, out = self.ar(r, "--conferir", str(p))
        self.assertEqual(rc, 0, out)
        self.escreve(r, "src/conta.sh", "a\nc\n")
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: NÃO CONFERE", out)
        self.assertIn("sha256 diferente", out)

    def test_segundo_revisor_sem_resultado_exige_dispensa(self):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--revisor2", "stub-c:falha-quota")
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 2, out)
        self.assertIn("o 2º revisor foi acionado e não deu resultado", out)
        rc, out = self.ar(r, "--conferir", "--aceitar-sem-revisor2", "engine do 2º revisor sem cota hoje")
        self.assertEqual(rc, 0, out)
        self.assertIn(" revisor2=dispensado — engine do 2º revisor sem cota hoje", out)

    def test_sem_revisao_nao_confere(self):
        r = self.projeto()
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 2, out)
        self.assertIn("nenhuma revisão em sdd/reports/reviews", out)

    def test_ledger(self):
        r = self.revisado("--no-revisor2")
        _, out = self.ar(r, "--conferir")
        linha = re.search(r"(?m)^review_externo: .+$", out).group(0)
        bom = self.escreve(r, "sdd/releases/X/s1_1.0.yaml", "feature_id: X\n" + linha + "\n")
        rc, out = self.ar(r, "--ledger", bom)
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: LEDGER OK", out)
        rc, out = self.ar(r, "--ledger", FXR / "ledger-sem-review.yaml")
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: LEDGER SEM REVIEW", out)
        rc, out = self.ar(r, "--ledger", FXR / "ledger-dispensado.yaml")
        self.assertEqual(rc, 0, out)
        ruim = self.escreve(r, "sdd/releases/X/s1_2.0.yaml", linha.replace("sha256=", "sha256=" + "f" * 64 + " x=") + "\n")
        rc, out = self.ar(r, "--ledger", ruim)
        self.assertEqual(rc, 2, out)
        sem_motivo = self.escreve(r, "sdd/releases/X/s1_3.0.yaml", "review_externo: dispensado — \n")
        rc, out = self.ar(r, "--ledger", sem_motivo)
        self.assertEqual(rc, 2, out)
        rc, out = self.ar(r, "--ledger", r / "nao-existe.yaml")
        self.assertEqual(rc, 64, out)

    def test_ledger_de_outra_worktree_diz_onde_rodar(self):
        r = self.revisado("--no-revisor2")
        _, out = self.ar(r, "--conferir")
        linha = re.search(r"(?m)^review_externo: .+$", out).group(0)
        self.commit(r, "feat")
        wt = self.tmp / "wt"
        self.git(r, "worktree", "add", "-q", "--detach", str(wt), "HEAD")
        led = self.escreve(wt, "sdd/releases/X/s1_1.0.yaml", linha + "\n")
        rc, out = self.ar(wt, "--ledger", led)
        self.assertEqual(rc, 2, out)
        self.assertIn("não existe aqui: rode na pasta da frente", out)


class Prompts(Base):
    """AT-036."""

    def test_prompts_sem_vendor_e_com_o_contrato(self):
        for nome, marca in (("reviewer", "<<<VERDICTS"), ("auditor", "<<<VERDICTS"), ("desempate", "DECISAO:REFUTADO")):
            texto = ler(RAIZ / "sdd/review/prompts" / (nome + ".md"))
            corpo = re.sub(r"^\s*<!--.*?-->", "", texto, flags=re.S)
            with self.subTest(prompt=nome):
                self.assertIn(marca, corpo)
                self.assertIn("inline", corpo)
                self.assertIn("Nenhuma ferramenta é necessária", corpo)
                self.assertNotRegex(corpo.lower(), r"\b(claude|codex|gemini|openrouter|anthropic|openai|google)\b")


class RevisaoReal(Base):
    """Achados da revisão real sobre o diff da F10 (EXTERNAL_REVIEW_20261031-233526, R1–R7)."""

    def test_r1_conferir_recusa_revisao_so_de_paths_e_o_padrao_a_pula(self):
        r = self.projeto()
        self.escreve(r, "sdd/features/DESIGN_X.md", "d\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2",
                           "--paths", "sdd/features/DESIGN_X.md")
        self.assertEqual(rc, 0, out)
        p = self.pasta(r).relative_to(r)
        rc, out = self.ar(r, "--conferir", str(p))
        self.assertEqual(rc, 2, out)
        self.assertIn("cobre só --paths sdd/features/DESIGN_X.md", out)
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 2, out)
        self.assertIn("nenhuma revisão em sdd/reports/reviews", out)

    def test_r2_conferir_recusa_revisao_rasa(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-vazio", "--auditor", "stub-b:auditor-vazio", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        rc, out = self.ar(r, "--conferir")
        self.assertEqual(rc, 2, out)
        self.assertIn("foi rasa", out)

    def test_r3_caminho_com_acento_conta_e_aciona_seguranca(self):
        r = self.projeto()
        self.escreve(r, "src/ação/auth.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--dry-run")
        self.assertEqual(rc, 0, out)
        self.assertIn("2º revisor: segurança (src/ação/auth.sh)", out)
        self.assertIn("diff: 4 arquivo(s)", out)

    def test_r4_segundos_sao_da_chamada_que_respondeu(self):
        r = self.projeto()
        env = dict(self.env, SDD_REVIEW_ESPERA="1")
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a:falha-429+revisor-ok", "--auditor", "stub-b",
                          "--no-revisor2", env=env)
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["reviewer_segundos"], "0")

    def test_r5_revisao_invalida_nao_grava_jsonl(self):
        r = self.projeto()
        rc, _ = self.rev(r, "--reviewer", "stub-a:revisor-sem-bloco", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 68)
        self.assertFalse((self.pasta(r) / "reviewer.verdicts.jsonl").exists())

    def test_r6_achado_numerico_nao_derruba_o_script(self):
        resp = self.tmp / "resp"
        shutil.copytree(str(FXR / "respostas"), str(resp))
        (resp / "num.md").write_text('Achado.\n\n<<<VERDICTS\n{"achado":1,"arquivo":"src/conta.sh","linha":1,'
                                     '"severidade":"HIGH","confianca":"CONFIRMED","resumo":"x"}\nVERDICTS>>>\n',
                                     encoding="utf-8")
        (resp / "aud.md").write_text('Auditoria.\n\n<<<VERDICTS\n{"achado":1,"veredito":"AGREE","justificativa":"x"}\n'
                                     'VERDICTS>>>\n', encoding="utf-8")
        env = dict(self.env, SDD_REVIEW_STUB_RESPOSTAS=str(resp))
        r = self.projeto()
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a:num", "--auditor", "stub-b:aud",
                          "--no-revisor2", env=env)
        self.assertEqual(rc, 0, out)
        self.assertNotIn("Traceback", out)
        self.assertEqual(meta(self.pasta(r))["convergencia_1o_passe"], "sim")

    def test_r7_custo_pequeno_nunca_aparece_como_zero(self):
        r = self.projeto()
        env = dict(self.env, SDD_REVIEW_STUB_CUSTO="0.00001")
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2", env=env)
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["reviewer_custo"], "US$ 0.000010")
        self.assertEqual(m["custo_total"], "US$ 0.000020")


class AvaliadorCiclo1(Base):
    """Achados do avaliador de contexto fresco, ciclo 1 (sdd/reviews/AVALIACAO_F10_REVISAO_20261101-ciclo1.md)."""

    def loop(self, r, ledger=None):
        args = [BASH, FLUXO, "loop", "--review", self.pasta(r), "--rodada", "1"] + (["--ledger", ledger] if ledger else [])
        rc, out, err = self.roda(args, r, self.env)
        return rc, out + err

    def com_r2(self, r2):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-vazio+revisor-vazio", "--auditor", "stub-b:auditor-vazio",
                           "--revisor2", r2)
        return r, rc, out

    def test_1_segundo_revisor_sem_cli_bloqueia_o_loop_d3(self):
        r, rc, out = self.com_r2("stub-c:sem-cli")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["revisor2_engine"], m["revisor2_exit"]), ("stub-c:sem-cli", "66"))
        self.assertIn("⚠️ o 2º revisor (stub-c:sem-cli) falhou", out)
        rc, out = self.loop(r)
        self.assertEqual(rc, 20, out)
        self.assertIn("D3: 2º revisor acionado e indisponível (stub-c:sem-cli, exit 66)", out)

    def test_1_segundo_revisor_sem_cota_e_tempo_esgotado_refazem(self):
        for cen in ("falha-quota", "dorme"):
            with self.subTest(cenario=cen):
                shutil.rmtree(str(self.tmp / "repo"), ignore_errors=True)
                r, rc, out = self.com_r2("stub-c:" + cen)
                self.assertEqual(rc, 0, out)
                m = meta(self.pasta(r))
                self.assertEqual((m["revisor2_engine"], m["revisor2_exit"]), ("stub-c:" + cen, "67"))
                rc, out = self.loop(r)
                self.assertEqual(rc, 10, out)
                self.assertIn("2º revisor acionado e falhou (stub-c:%s, exit 67)" % cen, out)

    def test_1_desempate_que_falhou_registra_a_engine(self):
        reg = self.registry([self.linha("stub-a", "revisor-ok"), self.linha("stub-b", "auditor-refuta-high"),
                             self.linha("stub-d", "falha-quota")])
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["desempate_engine"], m["desempate_decisao"]), ("stub-d", "-"))

    def test_2_custo_todo_desconhecido_nunca_e_zero(self):
        reg = self.registry([self.linha("x-a", "revisor-ok", "pay-per-token"), self.linha("x-b", "auditor-agree",
                                                                                            "pay-per-token")])
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "x-a", "--auditor", "x-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["custo_total"], "$?")
        self.assertIn("custo total: custo desconhecido", out)
        self.assertNotIn("0,0000", out)

    def test_3_contexto_do_diff_do_usuario_nao_muda_o_sha(self):
        r = self.projeto()
        self.escreve(r, "longo.txt", "".join("linha %d\n" % k for k in range(60)))
        self.commit(r, "longo")
        self.escreve(r, "longo.txt", "".join(("mudou %d\n" if k in (20, 30) else "linha %d\n") % k for k in range(60)))
        sha = lambda s: re.search(r"diff_sha256: ([0-9a-f]{64})", s).group(1)
        _, a = self.ar(r, "--base", "HEAD", "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.git(r, "config", "diff.context", "10")
        self.git(r, "config", "diff.interHunkContext", "20")
        _, b = self.ar(r, "--base", "HEAD", "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(sha(a), sha(b))

    def test_4_docs_sdd_sem_o_brainstorm_descartado(self):
        r = self.projeto(extra_cfg="  context_max_kb: 2\n")
        self.escreve(r, "sdd/features/BRAINSTORM_X.md", "B" * 3000 + "\n")
        self.escreve(r, "sdd/features/DEFINE_X.md", "definição\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2", "--feature", "X")
        self.assertEqual(rc, 0, out)
        m = meta(self.pasta(r))
        self.assertEqual(m["docs_sdd"], "DEFINE_X.md")
        self.assertIn("(1 doc SDD)", m["contexto"])

    def test_5_auditor_excluido_nao_e_diversidade_nenhuma(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-quota,stub-c", "--auditor", "stub-c", "--no-revisor2")
        self.assertEqual(rc, 67, out)
        self.assertNotIn("a mesma engine revisou e auditou", out)
        self.assertEqual(meta(self.pasta(r))["diversidade"], "-")


class AvaliadorCiclo2(Base):
    """Achados do avaliador de contexto fresco, ciclo 2 (sdd/reviews/AVALIACAO_F10_REVISAO_20261101-ciclo2.md)."""

    def longo(self, r):
        self.escreve(r, "longo.txt", "".join("linha %02d\n" % k for k in range(60)))
        self.commit(r, "longo")

    def test_1_edicao_do_mesmo_tamanho_no_mesmo_instante_do_indice_entra_no_diff(self):
        r = self.projeto()
        self.git(r, "config", "core.trustctime", "false")   # o ctime não volta; sem isto o git o compararia
        arq = self.escreve(r, "longo.txt", "".join("linha %02d\n" % k for k in range(60)))
        # o arquivo nasce 100 s no passado: o índice guarda esse mtime no commit, e o índice "agora" de uma
        # cópia sem o mtime original (copyfile) fica longe dele em qualquer relógio, com ou sem nanossegundos
        antigo = os.stat(str(arq)).st_mtime_ns - 100 * 10 ** 9
        os.utime(str(arq), ns=(antigo, antigo))
        self.commit(r, "longo")
        st = os.stat(str(arq))
        arq.write_text(ler(arq).replace("linha 30", "mudou 30"), encoding="utf-8")
        self.assertEqual(os.stat(str(arq)).st_size, st.st_size)
        # mesmo mtime do que o índice registrou e índice escrito no mesmo instante: só a checagem "racy" do
        # git (que exige o mtime original do índice) enxerga a mudança
        os.utime(str(arq), ns=(st.st_atime_ns, st.st_mtime_ns))
        os.utime(str(r / ".git/index"), ns=(st.st_atime_ns, st.st_mtime_ns))
        rc, out = self.ar(r, "--base", "HEAD", "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 0, out)
        self.assertIn("longo.txt", self.git(r, "diff", "HEAD", "--name-only"))
        rc, out = self.ar(r, "--base", "HEAD", "--reviewer", "stub-a", "--auditor", "stub-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertIn(b"+mudou 30", (self.pasta(r) / "diff.patch").read_bytes())

    def test_2_order_file_e_textconv_do_usuario_nao_mudam_o_sha(self):
        r = self.projeto()
        sha = lambda s: re.search(r"diff_sha256: ([0-9a-f]{64})", s).group(1)
        _, a = self.rev(r, "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.escreve(self.tmp, "ordem.txt", "src/novo.sh\n")
        self.git(r, "config", "diff.orderFile", str(self.tmp / "ordem.txt"))
        self.escreve(self.tmp, "atributos", "*.sh diff=maiusculo\n")
        self.git(r, "config", "core.attributesFile", str(self.tmp / "atributos"))
        self.git(r, "config", "diff.maiusculo.textconv", "tr a-z A-Z <")
        _, b = self.rev(r, "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(sha(a), sha(b))

    def test_3_lista_esgotada_registra_a_troca_e_nao_diz_quem_revisou(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:falha-quota,stub-c:falha-quota", "--auditor", "stub-b",
                           "--no-revisor2")
        self.assertEqual(rc, 67, out)
        m = meta(self.pasta(r))
        self.assertEqual((m["reviewer_engine_efetivo"], m["reviewer_fallback_usado"]), ("stub-c:falha-quota", "sim"))
        self.assertIn("revisor: falhou (exit 67) — última engine tentada: stub-c:falha-quota", out)
        self.assertNotIn("quem revisou", out)

    def test_5_comentario_de_security_globs_cita_o_segundo_revisor(self):
        cfg = ler(RAIZ / "sdd/config.example.yaml")
        bloco = cfg.split("review:", 1)[1].split('security_globs: ""', 1)[0]
        self.assertIn("aciona o 2º revisor", bloco)


class RevisaoFinal(Base):
    """Achados da revisão real final, rodada 1 (EXTERNAL_REVIEW_20261101-004259; ledger em
    sdd/reports/evidence/F10_REVISAO/ledger-review.md)."""

    def respostas(self, **arquivos):
        resp = self.tmp / "resp"
        if not resp.exists():
            shutil.copytree(str(FXR / "respostas"), str(resp))
        for nome, texto in arquivos.items():
            (resp / (nome + ".md")).write_text(texto, encoding="utf-8")
        return dict(self.env, SDD_REVIEW_STUB_RESPOSTAS=str(resp))

    def test_r1_codex_auditoria_parcial_e_68(self):
        env = self.respostas(parcial='Auditoria.\n\n<<<VERDICTS\n{"achado":"R1","veredito":"AGREE","justificativa":"x"}\n'
                                     'VERDICTS>>>\n')
        r = self.projeto()
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a", "--auditor", "stub-b:parcial", "--no-revisor2",
                          env=env)
        self.assertEqual(rc, 68, out)
        m = meta(self.pasta(r))
        self.assertIn("auditoria incompleta: sem veredito para R2", m["auditor_motivo"])
        self.assertFalse((self.pasta(r) / "auditor.verdicts.jsonl").exists())

    def test_r2_codex_revisor2_igual_ao_revisor_ou_ao_auditor_e_64(self):
        r = self.projeto()
        for r2 in ("stub-a", "stub-c:revisor-ok", "stub-b"):
            with self.subTest(revisor2=r2):
                rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--revisor2", r2)
                self.assertEqual(rc, 64, out)
                self.assertIn("precisa ser outra engine (adapter e modelo)", out)
        self.assertEqual(self.chamadas(), 0)

    def test_r1_claude_mesmo_adapter_e_modelo_e_a_mesma_engine(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b:revisor-ok")
        self.assertEqual(rc, 67, out)
        self.assertEqual(self.chamadas(), 0)

    def test_r2_claude_candidato_com_adapter_ausente_e_pulado(self):
        reg = self.registry([self.linha("stub-a", "revisor-ok"), self.linha("stub-b", "auditor-agree-dois"),
                             self.linha("x-sem", "revisor2-ok", adapter="nao-existe"),
                             self.linha("stub-c", "revisor2-ok")])
        r = self.projeto(registry=reg)
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["revisor2_engine"], "stub-c")

    def test_r3_supress_blank_empty_e_atributos_do_usuario_nao_mudam_o_sha(self):
        r = self.projeto()
        self.escreve(r, "longo.txt", "".join(("\n" if k % 5 == 0 else "linha %d\n" % k) for k in range(40)))
        self.commit(r, "longo")
        self.escreve(r, "longo.txt", "".join(("\n" if k % 5 == 0 else ("mudou %d\n" if k == 21 else "linha %d\n") % k)
                                            for k in range(40)))
        sha = lambda s: re.search(r"diff_sha256: ([0-9a-f]{64})", s).group(1)
        _, a = self.ar(r, "--base", "HEAD", "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.git(r, "config", "diff.suppressBlankEmpty", "true")
        self.escreve(self.tmp, "attr", "*.txt diff=fn\n")
        self.git(r, "config", "core.attributesFile", str(self.tmp / "attr"))
        self.git(r, "config", "diff.fn.xfuncname", "^(linha 1.*)$")
        _, b = self.ar(r, "--base", "HEAD", "--dry-run", "--reviewer", "stub-a", "--auditor", "stub-b")
        self.assertEqual(sha(a), sha(b))

    def test_r5_claude_aviso_de_uma_engine_antes_mesmo_com_auditor_falho(self):
        r = self.projeto()
        rc, out = self.rev(r, "--reviewer", "stub-a:revisor-ok+auditor-sem-bloco", "--um-engine", "--no-revisor2")
        self.assertEqual(rc, 68, out)
        aviso = "⚠️ a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos da revisão"
        self.assertTrue(out.startswith(aviso), out[:200])

    def test_r4_codex_preco_pelo_modelo_reportado(self):
        reg = self.registry([self.linha("x-a", "revisor-ok", "pay-per-token"), self.linha("x-b", "auditor-agree",
                                                                                            "assinatura")])
        (reg.parent / "precos.tsv").write_text("x-a\tstub-modelo\t1.0\t2.0\thttps://exemplo.example/p\t2026-11-01\n",
                                               encoding="utf-8")
        r = self.projeto(registry=reg)
        rc, out = self.rev(r, "--reviewer", "x-a", "--auditor", "x-b", "--no-revisor2")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["reviewer_custo"], "≈US$ 0.0014")

    def test_r5_codex_papel_chamado_que_falhou_tem_custo_desconhecido(self):
        r = self.projeto()
        self.escreve(r, "src/auth/login.sh", "x\n")
        rc, out = self.rev(r, "--reviewer", "stub-a", "--auditor", "stub-b", "--revisor2", "stub-c:falha-quota")
        self.assertEqual(rc, 0, out)
        self.assertEqual(meta(self.pasta(r))["revisor2_custo"], "$?")

    def test_n1_novo_sem_arquivo_e_68(self):
        env = self.respostas(novo='Auditoria.\n\n<<<VERDICTS\n{"achado":"R1","veredito":"AGREE","justificativa":"x"}\n'
                                  '{"achado":"R2","veredito":"AGREE","justificativa":"x"}\n'
                                  '{"achado":"N1","veredito":"NOVO","severidade":"HIGH","resumo":"x"}\nVERDICTS>>>\n')
        r = self.projeto()
        rc, out = self.ar(r, "--base", "main", "--reviewer", "stub-a", "--auditor", "stub-b:novo", "--no-revisor2",
                          env=env)
        self.assertEqual(rc, 68, out)
