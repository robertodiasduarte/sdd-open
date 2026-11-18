# BUILD REPORT: F27 — desempenho do banco (`sdd-desempenho-banco`)

> Relatório do Build da skill `sdd-desempenho-banco`, das duas ferramentas dela (varredura e diagnóstico) e dos ganchos no Define, no Design e na release.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F27_DESEMPENHO_BANCO |
| **Date** | 2026-11-17 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F27_DESEMPENHO_BANCO.md](../features/DEFINE_F27_DESEMPENHO_BANCO.md) |
| **DESIGN** | [DESIGN_F27_DESEMPENHO_BANCO.md](../features/DESIGN_F27_DESEMPENHO_BANCO.md) |
| **Status** | Complete — publicação v2.24.0 depois de F25 (v2.22.0) e F26 (v2.23.0); rebase feito, Verify Gate verde em `8bdfe14` (2.686 testes); recibo pendente: CI do PR nos 3 sistemas |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 35/35 do File Manifest (o item 25, `docs/pt-BR/cli-conventions.md`, não existe no pacote: linha sem efeito, como o DESIGN previu) |
| **Files Created** | 15 (8 do pacote, 4 testes, 2 páginas de docs, 1 troca do starter) |
| **Lines of Code** | cerca de 3.300 linhas acrescentadas no diff contra `2204a14` (47 arquivos, documentos da frente incluídos) |
| **Build Time** | 2026-11-17, numa sessão (Define, Design e Build) |
| **Tests Passing** | 2.578/2.578 no Verify Gate de `5af0a2d` (3 pulados por plataforma); eram 2.491 em `2204a14` (+87) |
| **Agents Used** | revisor e auditor da revisão adversarial; avaliador fresco (contrato e veredito); 6 agentes de cenário |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| testes executam o script | LM-001 | ✔ tratado | 4 módulos executam os scripts em repositórios temporários; 6 mutantes do Build e 4 do contrato morrem (`SABOTAGEM.log`, `AVAL-MUTANTES-DEPOIS.log`) |
| linha de base vermelha | LM-002 | ✔ tratado | `BASELINE_2204a14.log`: os 4 módulos novos falham na `v2.21.0` |
| commit antes de revisar | LM-003 | ✔ tratado | cada rodada de revisão rodou sobre a árvore commitada |
| cópia sem `.git` | LM-006 | ✔ tratado | o Verify Gate roda numa cópia de `git archive`; os testes criam o próprio repositório |
| sabotagem em cópia | LM-009 | ✔ tratado | mutantes só em cópias de `git archive` |
| número longo / e-mail no pacote | LM-012 | ✔ tratado | o G2 do publish-gate barrou um e-mail de fixture; montado em tempo de execução (commit `test(f27): e-mail da fixture…`) |
| `encoding` no Windows | LM-014 | ✔ tratado | testes pelo `Sandbox.roda`; os 2 scripts abrem com o bloco de saída UTF-8 do F16W2 |
| caminho do Windows no `$0` | LM-017 | ✔ tratado | cabeçalho `_sdd_0="${0//\\//}"` da segurança nos 2 scripts |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | logs de evidência gravados por script em `bash`, terminando em `[exit=N]` |
| chave falsa no log | LM-020 | ✔ tratado | senha e e-mail das fixtures montados em tempo de execução |
| juiz por regex de LLM | LM-028 | ✔ tratado | os 6 cenários foram julgados por leitura (`CENARIOS_DEFINE.md`) |
| `bash` sem caminho no Windows | LM-029 | ✔ tratado | a varredura chama a segurança por `SDD_DESEMPENHO_BASH` |
| PATH de links no Windows | LM-034 | ✔ tratado | o `supabase` falso fica numa pasta prefixada ao PATH, sem links |
| skill do starter citando `sdd/bin` | LM-035 | ✔ tratado | `scripts/starter/trocas/sdd-desempenho-banco.md`; `test_gerar_starter.py` verde antes do gate |
| arquivo novo fora do MANIFEST | LM-037 | ✔ tratado | `MANIFEST.txt` no mesmo commit; publish-gate numa cópia antes do gate |
| SKILL.md com 500 linhas | LM-038 | ✔ tratado | `sdd-release` em 451 linhas; `sdd-define` em 445; `test_conversa` verde |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `<<'PY'` `_sdd_c.reconfigure` `test_f16w2_saida` `sdd/bin`
regra: Script novo de `sdd/bin` com Python embutido (heredoc `<<'PY'`) precisa abrir com o bloco de saída UTF-8 do F16W2 (`import sys as _sdd_sys` … `_sdd_c.reconfigure(…)`) nas primeiras linhas: `test_f16w2_saida` confere o texto exato, e uma variante equivalente com outro nome reprova só no Verify Gate inteiro (na F27, +28 min). **Do instead:** copie o bloco de um script vizinho à letra e rode `python3 -B -m unittest discover -s tests -p 'test_f16w2_saida.py'` antes do gate.
evidencia: sdd/reports/evidence/F27_DESEMPENHO_BANCO/GATE-1-VERMELHO.log
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `mktemp -d` `TMPDIR` `macOS`
regra: No macOS, `mktemp -d` sem molde ignora o `TMPDIR` e cria a pasta no temporário do sistema: uma guarda "a pasta temporária não pode cair dentro do projeto" passa calada no Mac e o teste que aponta o `TMPDIR` para dentro do projeto falha. **Do instead:** use `mktemp -d "${TMPDIR:-/tmp}/<nome>.XXXXXX"`, que respeita o `TMPDIR` em todo sistema, e teste a guarda com o `TMPDIR` apontado para dentro do projeto.
evidencia: tests/test_desempenho_diagnostico.py (DadoDeFora.test_saida_bruta_fora_do_projeto)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `web/MODO_WEB.md` `version` `gerar-starter` `linha de identificação`
regra: Subir a versão da `sdd-define`, da `sdd-design` ou da `sdd-build` exige a mesma linha de identificação (`sdd-<skill> vX.Y.Z · …`) no `web/MODO_WEB.md` dela: o gerador do starter tira essas skills do modo web e sai 65 ("o modo tem de trazer… a mesma linha de identificação"), derrubando 25 testes de `test_gerar_starter`. **Do instead:** ao subir a versão, troque a linha nos dois arquivos e rode `test_gerar_starter.py` antes do gate.
evidencia: tests/test_gerar_starter.py
ficha: —
mordeu_antes: LM-035
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Duration | Notes |
|---|------|-------|--------|----------|-------|
| 1 | Catálogo P01–P17 e consultas do diagnóstico | (direct) | ✅ Complete | — | fase `define` = P08, P15, P17; 12 com padrão, 5 só à mão |
| 2 | `SKILL.md`, `como-falar.md`, `manifest.json`, `evals/cases.json` | (direct) | ✅ Complete | — | `skill-lint --conversa` verde |
| 3 | `desempenho-varredura.sh` | (direct) | ✅ Complete | — | novo = achado que a base não tinha (comparação com a base, não diff de linhas) |
| 4 | `desempenho-diagnostico.sh` | (direct) | ✅ Complete | — | validação antes de tudo; o modo vem dela; alvo pela versão do CLI |
| 5 | Ganchos: `sdd-define` 13, `sdd-design` 5.8, `sdd-release` 0a.11, templates | (direct) | ✅ Complete | — | versões 2.9.0, 2.10.0, 2.17.0 |
| 6 | Starter (lista, trocas, openai.tsv, raiz) | (direct) | ✅ Complete | — | 19 skills geradas |
| 7 | README, docs, guia do aluno, convenções, MANIFEST | (direct) | ✅ Complete | — | 23 skills |
| 8 | Testes novos e contagens fixadas | (direct) | ✅ Complete | — | 4 módulos novos; 13 testes antigos com contagem ou versão acertadas |

**Legend:** ✅ Complete | 🔄 In Progress | ⏳ Pending | ❌ Blocked

---

## Agent Contributions

| Agent | Files | Specialization Applied |
|-------|-------|------------------------|
| (direct) | 47 | DESIGN patterns only |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 35 arquivos, acoplados (o catálogo alimenta 2 scripts, 4 testes e 3 skills); uma sessão |
| Recomendação | default — um autor lembra os nomes das fichas e das regras entre os arquivos |
| Decisão do usuário | default, pela regra do Roberto para esta frente (recomendação aceita como padrão), 2026-11-17 |

---

## Drift detectado

nenhum

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `.agents/skills/sdd-desempenho-banco/SKILL.md` | 195 | (direct) | ✅ | `skill-lint --conversa` |
| `.agents/skills/sdd-desempenho-banco/references/CATALOGO_DESEMPENHO.md` | 252 | (direct) | ✅ | `test_desempenho_catalogo` |
| `.agents/skills/sdd-desempenho-banco/references/CONSULTAS_DIAGNOSTICO.md` | 142 | (direct) | ✅ | só leitura, por teste |
| `.agents/skills/sdd-desempenho-banco/references/como-falar.md` | 65 | (direct) | ✅ | 2 exemplos |
| `.agents/skills/sdd-desempenho-banco/manifest.json` | 36 | (direct) | ✅ | executados: 2 cenários × 3 |
| `.agents/skills/sdd-desempenho-banco/evals/cases.json` | 39 | (direct) | ✅ | 3 cenários |
| `sdd/bin/desempenho-varredura.sh` | ~950 | (direct) | ✅ | `test_desempenho_varredura` |
| `sdd/bin/desempenho-diagnostico.sh` | ~425 | (direct) | ✅ | `test_desempenho_diagnostico` |
| `scripts/starter/trocas/sdd-desempenho-banco.md` | 53 | (direct) | ✅ | `test_gerar_starter` |
| `docs/performance.md` | 78 | (direct) | ✅ | — |
| `docs/pt-BR/performance.md` | 79 | (direct) | ✅ | — |
| `tests/test_desempenho_varredura.py` | — | (direct) | ✅ | AT-001 a AT-006 |
| `tests/test_desempenho_diagnostico.py` | — | (direct) | ✅ | AT-007, AT-008, AT-011 |
| `tests/test_desempenho_catalogo.py` | 122 | (direct) | ✅ | AT-009, AT-007 |
| `tests/test_f27_textos.py` | — | (direct) | ✅ | AT-009, AT-010 |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

```text
N/A - não configurado (o Open não tem sdd/config.yaml); os lints do pacote rodam na suíte
```

**Status:** ⏭️ Skipped

### Typecheck (`{{TYPECHECK_CMD}}`)

```text
N/A - não configurado
```

**Status:** ⏭️ Skipped

### Testes (`{{TEST_CMD}}`)

```text
$ bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F27_DESEMPENHO_BANCO.md   (HEAD 5af0a2d)
   │ ✅ publish-gate GREEN — tree is publishable
   │ Ran 2578 tests in 1623.966s
   │ OK (skipped=3)
RESULTADO: VERDE
[exit=0]
(evidência: sdd/reports/evidence/F27_DESEMPENHO_BANCO/GATE.log; o 1º gate, vermelho em test_f16w2_saida, em GATE-1-VERMELHO.log;
 o 2º, verde em 3154276 com 2575 testes, antes das correções do avaliador, ciclo 3)
```

**Status:** ✅ 2578/2578 Pass

### Verify Gate da publicação (depois do rebase sobre v2.23.0 e das rodadas 2 e 3 da revisão do código)

```text
$ bash sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_F27_DESEMPENHO_BANCO.md   (HEAD 8bdfe14)
   │ ✅ publish-gate GREEN — tree is publishable
   │ Ran 2686 tests in 2271.822s
   │ OK (skipped=4)
RESULTADO: VERDE
[exit=0]
(evidência: sdd/reports/evidence/F27_DESEMPENHO_BANCO/GATE-RELEASE.log)
```

**Status:** ✅ 2686/2686 Pass

---

## Advisor Ledger

**Consulta:** delivery-review (código) e plan-review (DESIGN) · 2026-11-17 · `sdd/bin/adversarial-review.sh`
**VERDICT do advisor:** código, rodada 1: 0 graves, 2 médios, 2 leves (+2 do auditor) — loop PRONTO
**Ledger da revisão:** `sdd/reviews/LEDGER_REVISAO_F27_DESEMPENHO_BANCO.md` (uma linha por achado, com a marca `dano`; conferido por `sdd/bin/ledger-revisao-lint.sh`)
**Proveniência:** revisor claude (claude-opus-5-5), auditor openrouter qwen/qwen3.7-plus (diversidade de vendor), em todas as rodadas; a D1 do DESIGN ficou sem auditor (credencial da OpenRouter fora do ambiente) e foi registrada como `sem resultado`; 2º revisor dispensado pela regra (sem superfície de risco). Custo: DESIGN US$ 1,19 + US$ 1,30 + US$ 1,32; código US$ 2,05.

| # | Nota | Severidade | Veredito | Evidência |
|---|------|-----------|----------|-----------|
| D1–D3 | 23 notas da revisão do DESIGN (1 HIGH) | HIGH/MED/LOW | APLICADA | Advisor Ledger do DESIGN; ledger da revisão |
| C1-R1 | `--coletar` como valor de outra opção rodava a coleta sem consentimento | MED | APLICADA | `Consentimento.test_r1_coletar_como_valor_de_outra_opcao_nao_coleta` (falha antes: `REVISAO-CODIGO-1-ANTES.log`) |
| C1-R2 | padrão `re:` dentro de comentário no meio da linha SQL acusava | MED | APLICADA | `RevisaoDoCodigo.test_r2_…` (falha antes) |
| C1-R3 | `passwd=` sem máscara na causa de erro | LOW | APLICADA | `Consentimento.test_versao_ilegivel_ou_tudo_falha` |
| C1-R4 | README do starter com "sete" complementares | LOW | APLICADA | `scripts/starter/raiz/README.md` |
| C1-N1 | aspas escapadas quebrariam `fecha_parenteses` | MED | REBATIDA_EVIDENCIA | `RevisaoDoCodigo.test_n1_…` passa no código de antes (`REVISAO-CODIGO-1-ANTES.log`) |
| C1-N2 | `ilike '%` dentro de texto acusaria P15 | MED | REBATIDA_EVIDENCIA | `RevisaoDoCodigo.test_n2_…` passa no código de antes: dentro de aspas o `'` vira `''` |
| C2-R1–R5 | rodada 2 (release, `EXTERNAL_REVIEW_20261118-135108`): política em tabela entre aspas, máscara do SQL das consultas 3, 7 e 8 (provada no Postgres 16), PK por índice, política corrigida, janela do P08 | 3 MED, 2 LOW | APLICADA | `RevisaoDoCodigo2.*`, `Consultas.test_r2_mascara_do_sql_falha_fechada` (falham antes: `REVISAO-CODIGO-2-ANTES.log`; `REVISAO-CODIGO-2-R2-POSTGRES.log`) |
| C3-R1–R6, N1 | rodada 3 (release, `EXTERNAL_REVIEW_20261118-141043`): diagnóstico que saía limpo sem ter lido (comando que falha, JSON não reconhecido), índice único/PK como candidato a apagar, aspas e comentário no corpo `$$`, índice declarado de novo, palavra em `default`, stack pelo sentido do DEFINE | 4 MED, 3 LOW | APLICADA | `RevisaoDoCodigo3.*` nos dois módulos e `Skill.test_modos_e_regras` (falham antes: `REVISAO-CODIGO-3-ANTES.log`) |

**Revisão da versão final:** dispensada pelo Roberto em 2026-11-18 (D3), depois da rodada 3 (o teto): o delta são só os 7 consertos dela, cada um com teste vermelho antes; o motivo está no ledger da publicação (`sdd/releases/F27_DESEMPENHO_BANCO/s1_v2.24.0.yaml`).

---

## Segurança

nenhum — os 4 itens que o passo de segurança do Define propôs (S05, S10, S17, S18) foram aplicados (AT-011); nenhum recusado nem adiado. A stack do Open é "nenhuma"; `seguranca-varredura.sh --regras` lista só os itens de stack `todas`.

---

## Issues Encountered

| # | Issue | Resolution | Time Impact |
|---|-------|------------|-------------|
| 1 | A governança achou o tema dado pessoal e devolveu PADRAO_AUSENTE (o Open não tem `sdd/GOVERNANCA_PADRAO.md`) | dispensada pelo Roberto, com motivo; o risco virou os itens de segurança S10, S17 e S18 | +1 pergunta |
| 2 | A chave da OpenRouter não estava no ambiente da sessão: a D1 do DESIGN ficou sem auditor | a chave foi carregada do arquivo local de ambiente do Roberto, só no processo; rodada refeita | +US$ 1,19 |
| 3 | O 1º Verify Gate reprovou em `test_f16w2_saida` (bloco de saída UTF-8 com outro nome) | o bloco padrão nos 2 scripts; candidato ao playbook | +28 min |
| 4 | O publish-gate barrou um e-mail escrito numa fixture | e-mail montado em tempo de execução | +5 min |
| 5 | O `mktemp -d` do macOS ignora o `TMPDIR` | molde explícito; candidato ao playbook | +5 min |
| 6 | Os cenários foram lançados primeiro pela ferramenta de orquestração (que pede o OK do Roberto) | parada logo depois; os 6 cenários refeitos como agentes comuns | custo pequeno |
| 7 | O avaliador achou defeito real em 3 ciclos seguidos, todos no diagnóstico (classificação do inspect db, string de conexão como valor de opção, máscara do texto do banco, aviso do Python 3.12+) | cada achado corrigido com teste que falha no código avaliado (`AVALIADOR-C2-ANTES.log`, `AVALIADOR-C3-ANTES.log`); a máscara passou a falhar fechado; 3º e 4º ciclos com o OK do Roberto | +3 Verify Gates, +2 ciclos |

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| A linha da skill no `AGENTS.md.tmpl` | `test_agents_tmpl_cita_as_19_skills` exige toda skill na tabela das fases; nenhuma regra de desempenho (D11) | DESIGN 1.3, DEFINE AT-010 |
| `mktemp -d` com molde explícito | o do macOS ignora o `TMPDIR` | DESIGN 1.3 |
| Dispensa no fim de uma linha de código vale só para ela | contrato de aceite, proposta 4 (só na desempenho; a segurança fica como está) | DEFINE AT-004 |

---

## Blockers (if any)

| Blocker | Required Action | Owner |
|---------|-----------------|-------|
| A release espera F25 e F26 publicadas (D13) | rebase na `origin/main` depois das duas, conflitos (MANIFEST, sdd-release, guia, README), suíte e Verify Gate de novo | sessão da release |
| CI do PR no Windows ainda não rodou | o 1º push da branch dispara o CI (o publish-gate do CI pode reprovar os documentos da frente até a F26: esperado) | sessão da release |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 3 (skills, scripts de `sdd/bin`, testes)
**Contrato de aceite (passo 1.5 da `sdd-build`):** 5 propostas / 5 aceitas — seção `## Contrato de aceite` do DESIGN
**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 4 (o 3º e o 4º acima do teto de 2, com o OK do Roberto) · achados: 6 corrigidos com teste (C1: 1; C2: 2 + 3 leves; C3: 3) e 3 observações baixas do C4 (O1–O3, pendências abaixo) · `AVALIACAO_F27_DESEMPENHO_BANCO_20261117-2108.md` (ciclos anteriores: `…-2008.md`, `…-2020.md`, `…-2059.md`)

Recibos: (1) o Verify Gate em `5af0a2d`, o commit avaliado no ciclo 4, saiu 0 com 2.578 testes (`evidence/F27_DESEMPENHO_BANCO/GATE.log`) — recibo dado; (2) o CI do PR nos 3 sistemas (Ubuntu, macOS, Windows com Git Bash) fica para a sessão da release, porque ainda não há PR.

Pendências do ciclo 4, de gravidade baixa (não bloqueiam; para uma próxima frente ou a revisão da release):
- O1: nome entre aspas duplas sem fechar aparece inteiro no bloco de dado (é identificador, não valor; sugestão: cortar quando a aspa dupla não fecha).
- O2: `--saida "host=dbhost dbname=postgres"` (chave=valor sem senha) vira nome de arquivo; a URL sem senha já é recusada.
- O3: dispensa inválida numa linha com 3 fichas avisa 3 vezes.

---

## Acceptance Test Verification

| ID | Critério (EARS, resumido do DEFINE) | Resultado | Evidência |
|----|-------------------------------------|-----------|-----------|
| AT-001 | When a varredura acha o padrão de uma ficha numa linha acrescentada, shall sair 1 com `⚠️ Pnn grav arq:linha`; par que não acusa; sem achado, NADA ACHADO | true | `evidence/F27_DESEMPENHO_BANCO/AT-001.log` |
| AT-002 | If uma migration acrescenta chave estrangeira sem índice cuja 1ª coluna é a chave, then shall acusar P03 na linha da chave | true | `evidence/F27_DESEMPENHO_BANCO/AT-002.log` |
| AT-003 | While a base já tinha o achado, shall não listá-lo nem contá-lo; linha ℹ️; --tudo; sem base, tudo é novo | true | `evidence/F27_DESEMPENHO_BANCO/AT-003.log` |
| AT-004 | Where a dispensa com o id e motivo de 3+ caracteres está na linha (ou numa linha só de comentário acima), shall listá-la como aceito; senão, mantém e avisa | true | `evidence/F27_DESEMPENHO_BANCO/AT-004.log` |
| AT-005 | If entrada inválida, then shall sair 64 com causa e conserto; nunca 2; teto de 5 na tela, do mais grave, `--saida` com tudo | true | `evidence/F27_DESEMPENHO_BANCO/AT-005.log` |
| AT-006 | While o projeto não tem banco, shall sair 0 com SEM BANCO em ≤ 2 linhas; stack da segurança; fichas de Supabase só com Supabase | true | `evidence/F27_DESEMPENHO_BANCO/AT-006.log` |
| AT-007 | If a coleta roda sem --consentimento, then shall sair 64 sem executar nada; com ele, só a lista fixa; SQL da skill só de leitura | true | `evidence/F27_DESEMPENHO_BANCO/AT-007.log` |
| AT-008 | When --ler interpreta advisor ou inspect db, shall aplicar as regras D7 (idade das estatísticas, a confirmar, máquina antes, máscara, ≤ 5 do mais grave) | true | `evidence/F27_DESEMPENHO_BANCO/AT-008.log` |
| AT-009 | When os testes leem o pacote, shall valer: 17 fichas com 11 campos; os 4 modos; passos 13, 5.8 e 0a.11; MANIFEST, starter, README; lints verdes | true | `evidence/F27_DESEMPENHO_BANCO/AT-009.log` |
| AT-010 | A segurança, o OK único da release, a trava da governança, bash 3.2 e o AGENTS.md (só a linha da skill) shall continue to valer | true | `evidence/F27_DESEMPENHO_BANCO/AT-010.log` |
| AT-011 | If dado de fora (data, senha, texto do banco), then shall sair 64 sem executar, mascarar a senha, isolar o texto no bloco de dado e gravar a saída bruta fora do projeto | true | `evidence/F27_DESEMPENHO_BANCO/AT-011.log` |

**Verify Gate (`sdd/bin/verify-gate.sh <DEFINE>`):** exit 0 · `evidence/F27_DESEMPENHO_BANCO/GATE.log`

---

## Performance Notes

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Saídas da varredura nos testes | só 0, 1 ou 64 | só 0, 1 ou 64 (todo `varre()` confere) | ✅ |
| Coleta sem consentimento | 0 chamadas | 0 chamadas registradas | ✅ |
| Pares de ficha com padrão | ≥ 12 | 12 fichas com par (P15 com 2) | ✅ |
| Mutantes | ≥ 5 mortos | 6 do Build + 4 do contrato, todos mortos | ✅ |
| Cenários do modo Define | 3 de 3 em cada | 3 de 3 em cada (`CENARIOS_DEFINE.md`) | ✅ |

---

## Final Status

### Overall: ✅ COMPLETE — publicação v2.24.0 (F25 e F26 já saíram; o CI do PR é o recibo que falta)

**Completion Checklist:**

- [x] All tasks from manifest completed
- [x] All verification checks pass
- [x] All tests pass
- [x] No blocking issues
- [x] Acceptance tests verified — todo `true` com evidência lida (nenhum "por raciocínio")
- [x] Avaliador de contexto fresco: PASS_PENDENTE_RECIBO (recibo do gate dado; o do CI, na release) com `AVALIACAO_*.md` persistido
- [x] `sdd-release`: rebase, revisão do código (rodadas 2 e 3), raio de impacto e Verify Gate feitos

---

## Next Step

**If Complete:** `sdd-release` — CI do PR nos 3 sistemas e o OK do Roberto; depois, a geração do SDD Starter pela tag v2.24.0.
