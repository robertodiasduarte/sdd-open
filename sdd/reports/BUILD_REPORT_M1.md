# BUILD REPORT: M1 — manutenção do CI (parâmetro P2)

> Manutenção sem BRAINSTORM/DEFINE/DESIGN (regra "Quando pular o SDD formal" da `sdd-release`); escopo em
> `sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, seção 8, "Manutenção M1".

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | M1 |
| **Date** | 2026-10-29 |
| **Author** | SDD Build by RDD |
| **BRAINSTORM / DEFINE / DESIGN** | dispensados (manutenção; plano consolidado, seção 8) |
| **Status** | Complete |

Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-w0-m1`, branch `feat/m1`, commits `eac5484` (build) e `dd27ef6`
(notas da revisão de contexto fresco), sobre `303cc87` = `v2.2.4`. PR https://github.com/robertodiasduarte/sdd-open/pull/5.

---

## Summary

| Item | Entrega |
|---|---|
| CI em macOS | job `testes-macos` (`macos-latest`) no `publish-gate.yml` e no `release.yml`: afirma Python 3.9 e bash 3.2 (sai ≠0 se a imagem mudar), põe o `python3` do piso na frente do PATH, instala gitleaks darwin (nenhuma classe pulada) e roda a suíte com `/usr/bin/python3` + `SDD_TEST_BASH=/bin/bash`. `release` passa a `needs: [testes, testes-macos]` |
| Pin do checkout | `actions/checkout` v4.4.0 `11d5960a…` (Node 20) → v5.1.0 `fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09` (tag leve no commit, `using: node24`) nos 3 `uses:` |
| Integridade das skills | passo "Skill integrity" no job `gate` e no `testes` da release: reprova, em `.agents/skills/`, Unicode invisível/bidi/tag/seletor de variação (fora U+200D e U+FE0F, de emoji), código remoto entregue a shell ou interpretador (`curl\|wget … \| sh/python/perl`, `bash <(curl)`, `sh -c "$(curl)"`, `source <(curl)`, `eval "$(curl)"`, `base64 -d\|-D \| sh`), arquivo não-UTF-8, e alvo inexistente ou vazio |

**Desvio do plano, decidido pelo Roberto:** o plano previa "baseline da `sdd-auditoria-harness` no CI, falha com
HIGH/CRITICAL". O `collect_evidence.py` não lê `.agents/skills/` (só `.claude/skills/*/SKILL.md`), não tem severidade e
sempre sai 0; a skill é de higiene e manda segurança para outra skill, que não está no pacote. Opções levadas: varredura
inline no CI (escolhida), tirar o item da M1, rodar o `collect_evidence.py` só como smoke.

---

## Files Changed

| # | Arquivo | Ação |
|---|---|---|
| 1 | `.github/workflows/publish-gate.yml` | Modificado (checkout v5, varredura no `gate`, job `testes-macos`) |
| 2 | `.github/workflows/release.yml` | Modificado (checkout v5, varredura nos `testes`, job `testes-macos`, `needs` do `release`) |
| 3 | `tests/test_release_workflow.py` | Modificado (17 → 27 testes) |

Nenhuma skill mudou de versão; push só em `.github/**` e `tests/` não dispara a Release (`paths` do `release.yml`) —
a M1 **não gera tag** (`evidence/M1/escopo.log`).

---

## Verification Results

### Verify Gate

Sem DEFINE (manutenção): `PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh <cópia de git archive HEAD>` → exit 0
(`evidence/M1/GATE.log`).

### Complementary Checks

| Check | Resultado | Evidência |
|---|---|---|
| Suíte no piso local (Python 3.9.6, bash 3.2.57) | 326 OK | `evidence/M1/suite-piso.log` |
| CI do PR, run 40929387392 (`dd27ef6`) | `gate` (ubuntu) 326 OK · `testes-macos` 326 OK, 3.9.6 e 3.2.57 afirmados, `python3` do PATH = piso · varredura 0 achados em 43 arquivos | `evidence/M1/ci-pr5.log` |
| `check-versions.py --base v2.2.4 --base-obrigatoria` | VERDE | `evidence/M1/check-versions.log` |
| `deploy-espera-testes.py .` | SIM | `evidence/M1/deploy-espera-testes.log` |
| SHA do checkout v5.1.0 no GitHub | `fbc6f399…` = `refs/tags/v5.1.0` | `evidence/M1/checkout-v5.log` |
| Baseline vermelho: `test_release_workflow` novo sobre `v2.2.4` | 8 FAIL + 25 ERROR | `evidence/M1/baseline.log` |
| Sabotagem: uma garantia desfeita por vez nos workflows | 8 de 8 vermelhas com o nome do teste, verdes depois | `evidence/M1/sabotagem.log` |

---

## Acceptance Test Verification

| ID | Critério | Resultado | Evidência |
|----|----------|-----------|-----------|
| AT-001 | Os workflows têm job em `macos-latest` que afirma o piso e roda a suíte com `/usr/bin/python3` + `/bin/bash`; `release` espera por ele | true | `evidence/M1/testes-m1.log` |
| AT-002 | Todo `actions/checkout` está no SHA da v5.1.0 e `test_actions_fixadas_por_sha` continua verde | true | `evidence/M1/checkout-v5.log` |
| AT-003 | A varredura reprova cada sinal e passa nas skills do pacote | true | `evidence/M1/testes-m1.log` |
| AT-004 | Suíte inteira verde no piso local | true | `evidence/M1/suite-piso.log` |
| AT-005 | publish-gate em modo ci sobre `git archive HEAD` sai 0 | true | `evidence/M1/GATE.log` |
| AT-006 | Só os 2 workflows e o teste mudaram | true | `evidence/M1/escopo.log` |

---

## Revisão de contexto fresco

Revisor sem a conversa, só leitura, sobre `eac5484`. Veredito **FIX FIRST**: 0 HIGH, 4 MEDIUM, 6 LOW. Confirmou YAML, heredoc
(os escapes chegam intactos), SHA e `node24` do checkout, `deploy-espera-testes` SIM, publish-gate verde, 324 OK no piso.

| # | Nota | Decisão |
|---|---|---|
| 1 | MEDIUM — alvo inexistente passava com 0 achados | aplicada: diretório ausente ou nenhum arquivo lido reprova; teste e sabotagem |
| 2 | MEDIUM — "Floor versions" só imprimia; scripts que chamam `python3` do PATH rodavam no 3.15 do Homebrew | aplicada: versões afirmadas; `$RUNNER_TEMP/piso/python3` → `/usr/bin/python3` na frente do PATH. `macos-latest` não foi fixado em `macos-26`: a afirmação reprova se a imagem mudar |
| 3 | MEDIUM — `bash <(curl)`, `sh -c "$(curl)"`, `source <(curl)`, pipe para `python3`/`perl`/`/bin/bash`/`sudo -E`, `base64 -D` passavam | aplicada, com 6 amostras novas. Lacunas declaradas no comentário: `\| tee x \| sh`, pipe quebrado por `\`, PowerShell `iex` |
| 4 | MEDIUM — U+061C, seletores de variação, soft hyphen, fillers, U+2028/2029 (`splitlines`) | aplicada; U+FE0F fica de fora (55 usos legítimos em emoji nas skills). `split("\n")` no lugar de `splitlines()` |
| 5 | LOW — varrer também `AGENTS.md.tmpl`, `sdd/templates/**`, `sdd/playbook.md` | rebatida nesta M1: escopo declarado `.agents/skills/`; pendência registrada |
| 6 | LOW — texto que alerta contra `curl … \| sh` reprova; asset binário reprova | aceito: a regra é não escrever o padrão literal numa skill; binário em skill é suspeito por desenho |
| 7 | LOW — o teste varria a árvore local (`.DS_Store`) | aplicada: varre a cópia do que está no `MANIFEST.txt` |
| 8 | LOW — teste não conferia a classe do achado nem o argumento | aplicada |
| 9 | LOW — gitleaks darwin sem `-f` e sem `version` | aplicada no darwin; o passo do Ubuntu (anterior à M1) fica como está |
| 10 | LOW — `release` depende de runner macOS (fila; falha só do macOS segura a Release) | aceito: é o preço de o piso valer; repositório público, minutos sem custo; re-run manual destrava |

## Pendências levadas adiante

- Varredura de integridade também em `AGENTS.md.tmpl`, `sdd/templates/**`, `sdd/playbook.md` (nota 5).
- `curl -sSL` sem `-f` e sem checksum no gitleaks do Ubuntu (anterior à M1).

## Final Status

### Overall: COMPLETE

## Next Step

Feito: OK do Roberto ("finalizar (push + deploy + verificar) sdd-open") → push fast-forward `303cc87..dd27ef6` em `main`, PR #5 MERGED, `publish-gate` run 40931927983 verde (ubuntu + macOS), nenhuma Release (`evidence/M1/main-push.log`). Próxima frente: F4 Conversa.
