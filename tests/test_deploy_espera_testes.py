"""Contrato do .agents/skills/sdd-release/scripts/deploy-espera-testes.py: o deploy espera os testes?

SIM 0 · NAO 1 · NAO_SEI 2 · NAO_SE_APLICA 3 · uso 64, sempre com a linha RESULTADO: e a frase →.
As fixtures DEPLOY_HOSTINGER e DENO_* derivam de dois workflows reais de um projeto que publica por
rsync no push da main, sem host, usuário, porta, caminho de servidor ou domínio reais: mantêm o que
importa para a heurística (o lint com "deploy bloqueado" no echo, o continue-on-error em passos que
não são teste, a suíte informativa com set +e … exit 0). O caso SIM por needs: é o release.yml do
próprio sdd-open.
"""
from __future__ import annotations

import unittest

from apoio import PYTHON, Sandbox

SCRIPT = ".agents/skills/sdd-release/scripts/deploy-espera-testes.py"

DEPLOY_HOSTINGER = """\
name: Deploy to Hostinger (Production)

# Sem --delete (rsync nunca remove arquivos do servidor).
on:
  workflow_dispatch:
  push:
    branches:
      - main

env:
  ALVO: ${{ secrets.ALVO_SSH }}
  STANDBY: ${{ secrets.STANDBY_SSH }}

jobs:
  deploy-production:
    name: Deploy to production
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Load SSH keys into agent
        uses: webfactory/ssh-agent@v0.9.0
        with:
          ssh-private-key: |
            ${{ secrets.SSH_KEY }}

      - name: Trust standby host
        continue-on-error: true
        run: |
          if [ -z "$STANDBY" ]; then
            echo "::notice::standby não configurado"
            exit 0
          fi
          ssh-keyscan deploy.invalid >> ~/.ssh/known_hosts 2>/dev/null

      - name: Show file counts BEFORE deploy
        run: find wp-content -type f | wc -l

      - name: Lint PHP (pre-flight)
        run: |
          EXIT=0
          while IFS= read -r file; do
            php -l "$file" > /dev/null || { echo "BROKEN: $file"; EXIT=1; }
          done < <(find wp-content -name "*.php")
          if [ "$EXIT" != "0" ]; then
            echo "::error::Falha no lint PHP - deploy bloqueado"
            exit 1
          fi

      - name: Sync theme patch
        run: |
          rsync -avzc --exclude 'CLAUDE.md' wp-content/themes/patch/ "$ALVO:site/wp-content/themes/patch/"

      - name: Sync standby (theme + plugins)
        continue-on-error: true
        run: |
          rsync -azc wp-content/ "$STANDBY:site/wp-content/" || echo "::warning::standby falhou"
"""

DENO_INFORMATIVO = """\
name: CI — deno test (anti-rot do baseline)

# NÃO deploya nada (o deploy é outro workflow). Só sinal de CI.
on:
  workflow_dispatch:
  pull_request:
  push:
    branches:
      - main

jobs:
  deno-test:
    name: deno test (gate por baseline)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Run suite vs baseline (informativo)
        run: |
          set +e
          OUT="$(deno test --allow-all supabase/functions)"; CODE=$?
          echo "$OUT"
          if [ "$CODE" = "2" ]; then
            echo "::warning::vermelhos fora do baseline"
          fi
          exit 0
"""

# A suíte informativa acima, agora no mesmo job do deploy: parece um gate, não segura nada.
DENO_GUARDA = DENO_INFORMATIVO.replace(
    "          exit 0\n",
    "          exit 0\n      - name: Deploy functions\n        run: supabase functions deploy --project-ref teste\n")


def wf(passos: str, on: str = "push:\n    branches: [main]", extra_jobs: str = "") -> str:
    return ("name: w\non:\n  " + on + "\njobs:\n" + extra_jobs +
            "  deploy:\n    runs-on: ubuntu-latest\n    steps:\n" + passos)


def passo(nome: str, run: str, extra: str = "") -> str:
    corpo = "".join("          " + l + "\n" for l in run.splitlines())
    return "      - name: " + nome + "\n" + extra + "        run: |\n" + corpo


PUBLICA = passo("Publicar", 'rsync -az dist/ "$ALVO:site/"')


class DeployEsperaTestes(Sandbox):
    def setUp(self):
        super().setUp()
        self.p = self.tmp / "projeto"
        self.p.mkdir()

    def workflow(self, nome: str, texto: str) -> None:
        self.escreve(self.p, ".github/workflows/" + nome, texto)

    def roda_script(self, *args: str) -> tuple[int, str]:
        rc, out, err = self.roda([PYTHON, "-B", self.tmp / "s.py", *args], self.p)
        return rc, out + err

    def resultado(self) -> tuple[int, str]:
        self.copia(SCRIPT, self.tmp)
        (self.tmp / SCRIPT).rename(self.tmp / "s.py")
        rc, out = self.roda_script(str(self.p))
        self.assertResultado(out)
        self.assertIn("→ O deploy espera os testes?", out)
        return rc, out

    # ── SIM ──────────────────────────────────────────────────────────────────
    def test_release_do_sdd_open_espera_por_needs(self):
        self.copia(".github/workflows/release.yml", self.p)
        rc, out = self.resultado()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: SIM", out)
        self.assertIn("needs: testes", out)

    def test_teste_no_mesmo_job_com_continue_on_error_so_fora_do_teste_e_sim(self):
        self.workflow("deploy.yml", wf(
            "      - uses: actions/checkout@v4\n" +
            passo("Unit tests", "npm test") +
            passo("Aquece o standby", "ssh-keyscan deploy.invalid", "        continue-on-error: true\n") +
            passo("Lint", "npm run lint") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 0, out)
        self.assertIn("RESULTADO: SIM", out)
        self.assertIn("'Unit tests'", out)

    def test_lista_de_passos_no_mesmo_recuo_da_chave_e_lida(self):
        self.workflow("deploy.yml", "on: push\njobs:\n  deploy:\n    steps:\n    - run: pytest -q\n"
                                    "    - run: gh release create v1 dist/*\n")
        rc, out = self.resultado()
        self.assertEqual(rc, 0, out)

    # ── NAO ──────────────────────────────────────────────────────────────────
    def test_workflow_real_que_publica_sem_teste_e_nao(self):
        self.workflow("deploy-hostinger.yml", DEPLOY_HOSTINGER)
        self.workflow("ci-deno-test.yml", DENO_INFORMATIVO)
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("RESULTADO: NAO", out)
        self.assertIn("deploy-hostinger.yml · job deploy-production", out)
        self.assertIn("'Sync theme patch'", out)
        self.assertNotIn("Lint PHP (pre-flight)' testa", out)

    def test_lint_sozinho_nao_conta_como_teste(self):
        self.workflow("deploy.yml", wf(passo("Lint", "npm run lint") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("sem passo de teste antes", out)

    def test_suite_informativa_com_set_e_e_exit_0_nao_segura(self):
        self.workflow("ci-deno-test.yml", DENO_GUARDA)
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("'Run suite vs baseline (informativo)'", out)
        self.assertIn("set +e", out)

    def test_continue_on_error_no_passo_de_teste_nao_segura(self):
        self.workflow("deploy.yml", wf(passo("Unit tests", "npm test", "        continue-on-error: true\n") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("continue-on-error", out)
        self.assertIn("'Unit tests'", out)

    def test_continue_on_error_no_job_de_teste_nao_segura(self):
        testes = "  testes:\n    continue-on-error: true\n    steps:\n" + passo("Unit tests", "pytest")
        texto = wf(PUBLICA, extra_jobs=testes).replace("  deploy:\n", "  deploy:\n    needs: testes\n")
        self.workflow("deploy.yml", texto)
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("o job tem continue-on-error", out)

    def test_ou_true_no_comando_de_teste_nao_segura(self):
        for engole in ("|| true", "|| :", "|| exit 0", "|| echo falhou"):
            with self.subTest(engole=engole):
                self.workflow("deploy.yml", wf(passo("Unit tests", "pytest -q " + engole) + PUBLICA))
                rc, out = self.resultado()
                self.assertEqual(rc, 1, out)
                self.assertIn("termina em", out)

    def test_if_always_no_job_que_publica_nao_segura(self):
        testes = "  testes:\n    steps:\n" + passo("Unit tests", "go test ./...")
        texto = wf(PUBLICA, extra_jobs=testes).replace(
            "  deploy:\n", "  deploy:\n    needs: [testes]\n    if: ${{ always() }}\n")
        self.workflow("deploy.yml", texto)
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("always()", out)

    # ── revisão pós-build: nunca SIM falso ───────────────────────────────────
    def test_instalar_a_ferramenta_de_teste_nao_e_testar(self):
        for instala in ("pip install -r requirements.txt pytest", "npm install --save-dev jest",
                        "python3 -m pip install pytest"):
            with self.subTest(instala=instala):
                self.workflow("deploy.yml", wf(passo("Install", instala) + PUBLICA))
                rc, out = self.resultado()
                self.assertEqual(rc, 1, out)

    def test_alvo_de_make_que_comeca_com_test_nao_e_teste(self):
        self.workflow("deploy.yml", wf(passo("Deps", "make test-deps") + PUBLICA))
        rc, out = self.resultado()
        self.assertNotIn("RESULTADO: SIM", out)

    def test_teste_com_if_nao_garante_e_nao_sei(self):
        self.workflow("deploy.yml", wf(passo("Unit tests", "pytest", "        if: github.event_name == 'pull_request'\n")
                                       + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("só roda com if:", out)

    def test_if_always_em_qualquer_passo_que_publica_nao_segura(self):
        self.workflow("deploy.yml", wf(passo("Unit tests", "pytest") + passo("Release", "gh release upload v1 x") +
                                       passo("Espelho", 'rsync -az dist/ "$ALVO:site/"', "        if: always()\n")))
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("'Espelho' publica com if: always()", out)

    def test_if_always_num_job_do_meio_do_needs_nao_segura(self):
        meio = ("  testes:\n    steps:\n" + passo("Unit tests", "pytest") +
                "  build:\n    needs: testes\n    if: ${{ always() }}\n    steps:\n" + passo("Build", "make build"))
        self.workflow("deploy.yml", wf(PUBLICA, extra_jobs=meio).replace("  deploy:\n", "  deploy:\n    needs: build\n"))
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("needs: build roda com if:", out)

    def test_set_e_sem_exit_0_no_fim_e_nao_sei(self):
        self.workflow("deploy.yml", wf(passo("Unit tests", 'set +e\npytest\necho "terminou com $?"') + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("set +e", out)

    def test_pipe_sem_pipefail_nao_segura_e_shell_bash_segura(self):
        self.workflow("deploy.yml", wf(passo("Unit tests", "pytest | tee teste.log") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)
        self.assertIn("pipefail", out)
        self.workflow("deploy.yml", wf(passo("Unit tests", "pytest | tee teste.log", "        shell: bash\n") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 0, out)

    def test_job_com_nome_de_deploy_nao_reconhecido_impede_o_sim(self):
        self.copia(".github/workflows/release.yml", self.p)
        self.workflow("deploy.yml", "name: Deploy prod\non: push\njobs:\n  deploy:\n    steps:\n"
                                    + passo("Deploy via SSH", "ssh deploy.invalid 'cd app && git pull'"))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("deploy.yml · job deploy: o nome fala em publicar", out)

    def test_acao_que_faz_push_de_imagem_publica(self):
        self.workflow("docker.yml", "on: push\njobs:\n  img:\n    steps:\n      - uses: docker/build-push-action@v5\n"
                                    "        with:\n          push: true\n")
        rc, out = self.resultado()
        self.assertEqual(rc, 1, out)

    def test_workflow_so_de_workflow_call_e_avaliado_por_quem_chama(self):
        self.workflow("ci.yml", "on: push\njobs:\n  test:\n    steps:\n" + passo("Unit tests", "pytest") +
                      "  deploy:\n    needs: test\n    uses: ./.github/workflows/deploy.yml\n")
        self.workflow("deploy.yml", wf(PUBLICA, on="workflow_call:"))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertNotIn("deploy.yml · job deploy publica", out)

    def test_arquivo_que_nao_abre_e_nao_sei_com_resultado(self):
        (self.p / ".github/workflows/pasta.yml").mkdir(parents=True)
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("não consegui ler pasta.yml", out)

    # ── NAO_SEI ──────────────────────────────────────────────────────────────
    def test_workflow_run_e_nao_sei(self):
        self.workflow("deploy.yml", wf(PUBLICA, on="workflow_run:\n    workflows: [CI]\n    types: [completed]"))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("RESULTADO: NAO_SEI", out)
        self.assertIn("workflow_run", out)

    def test_workflow_reutilizavel_e_nao_sei(self):
        self.workflow("deploy.yml", "on: push\njobs:\n  deploy:\n    uses: ./.github/workflows/publicar.yml\n"
                                    "    secrets: inherit\n")
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("reutilizável", out)

    def test_teste_em_script_proprio_e_nao_sei_nunca_nao(self):
        self.workflow("deploy.yml", wf(passo("Run tests", "./scripts/ci.sh") + PUBLICA))
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("'Run tests' parece teste", out)

    def test_yaml_que_nao_consigo_ler_e_nao_sei(self):
        self.workflow("deploy.yml", "on: push\ndefaults: &padrao\n  run:\n    shell: bash\njobs:\n"
                                    "  deploy:\n    <<: *padrao\n    steps:\n" + PUBLICA)
        rc, out = self.resultado()
        self.assertEqual(rc, 2, out)
        self.assertIn("não consegui ler deploy.yml", out)

    # ── NAO_SE_APLICA ────────────────────────────────────────────────────────
    def test_sem_pasta_de_workflows_nao_se_aplica(self):
        rc, out = self.resultado()
        self.assertEqual(rc, 3, out)
        self.assertIn("RESULTADO: NAO_SE_APLICA", out)

    def test_workflow_que_so_testa_nao_se_aplica(self):
        self.workflow("ci-deno-test.yml", DENO_INFORMATIVO)
        rc, out = self.resultado()
        self.assertEqual(rc, 3, out)

    def test_workflow_so_de_pull_request_nao_publica_a_main(self):
        self.workflow("preview.yml", wf(PUBLICA, on="pull_request:\n    branches: [main]"))
        rc, out = self.resultado()
        self.assertEqual(rc, 3, out)

    # ── uso ──────────────────────────────────────────────────────────────────
    def test_argumento_que_nao_e_pasta_e_64(self):
        self.resultado()
        rc, out = self.roda_script(str(self.p / "nao-existe"))
        self.assertEqual(rc, 64, out)
        rc, out = self.roda_script(".", "a-mais")
        self.assertEqual(rc, 64, out)


if __name__ == "__main__":
    unittest.main()
