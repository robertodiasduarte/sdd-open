# Avaliação de contexto fresco — F19_CUSTO_REVISORES, ciclo 1 (2026-11-10)

Avisos do avaliador antes do bloco: avaliou o commit `b7c967e` numa cópia de `git archive` fora do repositório; o HEAD avançou para `e2e79a2` durante a avaliação e não foi avaliado. Gravou só 24 logs `AVAL-c1-*.log`. Dois desvios dele: rodou também `tests/test_revisao.py` (88 testes, OK), e numa sonda criou e apagou um arquivo temporário fora da pasta de rascunho. Os caminhos de máquina da cópia e dos casos dele foram tirados deste registro.

<<<AVALIACAO
feature: F19_CUSTO_REVISORES · modo: veredito · ciclo: 1 · commit avaliado: b7c967e (base 9581740)
ambiente: /usr/bin/python3 3.9.6 + /bin/bash 3.2.57 (PATH=/usr/bin:/bin) e python3 3.15.0 do PATH (o bash do PATH é o mesmo /bin/bash); sem rede; sem credenciais
contaminação: nenhuma

| AT | Sonda (log AVAL-c1-…) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | `eval-revisores.sh sdd/fixtures/revisao/custo --ledgers … --registry …` (01); padrões da pasta e dos ledgers num projeto sem git, com `review.output_dir: minhas` e com o slot vazio (14) | tabela com uma linha por papel + engine + modelo com provedor, ordenada, `RESULTADO: MEDIDO` + `→`, exit 0; padrões `review.output_dir` → `sdd/reports/reviews` e `sdd/reviews/` | 7 linhas na ordem revisor, 2º revisor, auditor; ProvedorA e ProvedorB em linhas separadas; exit 0; os três padrões lidos como especificado | PASS |
| AT-002 | 24 formas de custo (10); somas (11-caso-soma); recontagem independente com Decimal das 25 pastas reais (02, 03) | pago só de pay-per-token; nominal com todo custo numérico; `US$ n + $?` soma com `incerto em N de M`; sem valor vira `n/d em N de M`, nunca zero; assinatura paga `0.0000`; cobrança desconhecida `n/d`; decimal exato; 4 ou 6 casas; `≈` e ressalva no custo por dano | 0.1+0.2 = 0.3000; 10×0.1 = 1.0000; 0.3100+0.3000 = 0.6100; 0.00003+0.00004+0.00002 = 0.000090 e por dano 0.000030; `assinatura`, `$?`, `n/d`, vazio e formas desconhecidas saem `n/d`; `≈2.3333` e `(parcial)` presentes. Reais: 50.3657 (21 parcelas), 5.1073 (4) e 1.0933 (23) batem com a minha soma | PASS (notas em A6) |
| AT-003 | fixtures (01); contagem independente dos 6 ledgers reais contra as pastas (04); `eval-agree.sh` nas mesmas 25 pastas | achados, aplicados, com dano, falsos positivos, fora de escopo, sem classificar, ligados por pasta + id; AGREE igual ao `eval-agree.sh`; taxa com amostra | fixtures: revisor 9 achados, `6 de 9`, `3 de 9`, `1 de 9`, `1 de 9`, `1 de 9`; auditor ProvedorB com 2 NOVO, `2 de 2` falsos positivos. Reais: claude-opus-5-5 com 83 achados, 62 aplicados, 28 com dano, 34 sem classificar; codex 2º revisor 16, 9 e 7; todos iguais à minha contagem. AGREE 78.0% (78 de 100), igual ao `eval-agree.sh` | PASS |
| AT-004 | exits 65, 67, 68, 1, 124, -1 com e sem custo (11-caso-exits); troca de engine, `indisponível` e desempate (12-caso-troca); reais (02) | falhas por motivo, fora das rodadas; custo da falha entra nas somas; `trocada por outra engine` na linha da prevista; `indisponível` vai para fora da conta | `6 (1 cota ou tempo, 1 credencial, 3 outro, 1 resposta inválida)`, rodadas 0, pago 1.8750 (0.5+0.25+0.125+1) com `n/d em 2 de 6`; prevista com `1 trocada por outra engine`; `2º revisor indisponível: nenhuma engine foi chamada` em fora da conta | PASS |
| AT-005 | uso e exits (14); motivos de fora da conta (12-caso-fora); rede negada por `sandbox-exec` e escrita negada (15); linhas que somem (12-caso-some, 13, 20); travas (12-caso-crash, 14) | 64 com causa e conserto; 2 `SEM DADOS`; toda linha de dados fora da conta listada com `arquivo:linha` e motivo, nunca em silêncio; sem rede | 64 e 2 corretos; os 6 motivos do AT listados com `arquivo:linha`, mais pasta sem ledger; saída idêntica com a rede negada; 0 arquivos alterados. Mas linhas de dados somem com `fora da conta: 0` (A1) e há exit 1 com traceback (A2) | FAIL |
| AT-006 | fixtures do pacote (07); 55 casos meus (19); caso A1 (13, 20) | 0 no controle, no retroativo e no só-sem-achados; 2 com `arquivo:linha — motivo` por regra; 64 em uso, ilegível ou vazio; cabeçalho fora do molde reprova | 7 fixtures saem 2, cada uma pelo seu motivo; controles 0; `sem-linhas.md` 64; 53 de 55 casos meus como esperado. Mas o lint sai 0 com `dano = sim` sem teste e com REBATIDA nas linhas que ele pula (A1), e aceita cabeçalho com `dano` e `revisão` trocados (A5) | FAIL |
| AT-007 | `sdd-fluxo.sh loop --ledger` com 5 e 7 colunas, ids rotulados e sem rótulo (16); `test_fluxo`, `test_eval_agree`, `test_revisao` (05, 06, 17) | 7 colunas fecha o HIGH como o de 5; sem mudança de contrato | saída do loop idêntica entre 5 e 7 colunas nos dois casos (exit 0, `graves_abertos: 0`); sem ledger sai 10; diff de `sdd-fluxo.sh`, `eval-agree.sh`, `adversarial-review.sh` e adapters entre a base e b7c967e tem 0 linhas; 69, 9 e 88 testes OK | PASS |
| AT-008 | leitura dos textos na cópia, confrontados com o que os scripts fizeram; `test_f19_textos`, `test_contrato_build_release`, `test_docs`, `test_skill_lint` (05, 06) | critério, molde, 5c e item 8 mandam gravar, lintar e passar ao loop, com bump; seção do medidor em EN e PT; linhas no `cli-conventions`; contratos e MANIFEST | tudo presente; `sdd-build` 2.7.0 → 2.8.0 e `sdd-release` 2.9.1 → 2.10.0; MANIFEST igual a `git ls-tree` (0 diferenças); nenhum nome de engine novo nas skills. Os docs dizem "tudo o que ficou fora dos números vai para fora da conta" e "exits 0, 2, 64", o que A1, A2 e A4 contradizem | PASS (ressalva em A1, A2, A4) |
| AT-009 | `bin/sdd-open.sh init --vendors claude --yes` num projeto novo, depois `eval-revisores.sh` (18) | os 4 arquivos chegam; exit 2 com `RESULTADO: SEM DADOS` | os 4 presentes e idênticos aos do pacote; exit 2 `SEM DADOS` | PASS |

Testes rodados, sempre com -B: test_eval_revisores 35, test_ledger_revisao_lint 18, test_f19_textos 17, test_fluxo 69, test_eval_agree 9, test_contrato_build_release 29, test_docs 23, test_bash32 3, test_decisoes_lint 11, test_skill_lint 29, test_conversa 19. Todos OK nos dois ambientes (05, 06).
Sabotagens minhas em cópia (21): soma do pago derruba 12 asserções; regra `sim` só com APLICADA derruba `sim-rebatida.md`; falso positivo derruba 6. Os testes têm dentes.
NAO_VERIFICADO: Verify Gate com a suíte inteira e `publish-gate.sh` (proibido pelo brief: outro processo roda a suíte); linha de base vermelha em `origin/main`; relatório retroativo e release v2.10.0 (não são AT).

ACHADOS

A1 · HIGH · AT-005 e AT-006 · linha de dados bem formada some sem aviso no medidor e no lint
Depois de uma linha em branco, se a primeira linha do bloco não começa por um id `R<n>`/`N<n>` puro (id entre crases, em negrito, `R2 (claude)`), o bloco inteiro é tratado como "outra tabela" e pulado. O mesmo acontece com um segundo cabeçalho como `| Achado (rodada 3) |`. O lint sai 0 dizendo "1 linha(s)", e o medidor mostra `fora da conta: 0`. Uma linha `R3 … REBATIDA_EVIDENCIA … dano = sim` sem teste passa pelo lint que a release usa como gate. As mesmas linhas sem a linha em branco reprovam (exit 2) e aparecem no medidor.
Reprodução, numa pasta temporária com uma revisão de 3 achados (R1, R2, R3) e este ledger:
  | achado | sev | veredito | rodada | evidência | dano | revisão |
  |---|---|---|---|---|---|---|
  | R1 | LOW | APLICADA | rodada=1 | texto | nao | EXTERNAL_REVIEW_20260301-000001 |
  (linha em branco)
  | `R2` | LOW | APLICADA | rodada=2 | x | nao | EXTERNAL_REVIEW_20260301-000001 |
  | R3 | HIGH | REBATIDA_EVIDENCIA | rodada=2 | sem teste | sim | EXTERNAL_REVIEW_20260301-000001 |
  bash sdd/bin/ledger-revisao-lint.sh LEDGER_REVISAO_MIN.md   → exit 0, "1 linha(s)" (esperado: 2, com as linhas 5 e 6)
  bash sdd/bin/eval-revisores.sh . --ledgers LEDGER_REVISAO_MIN.md   → "1 de 3" aplicados, "fora da conta: 0" (esperado: linhas 5 e 6 contadas ou listadas)
Evidência: AVAL-c1-20-ACHADO-linhas-que-somem.log, com o controle sem a linha em branco; AVAL-c1-12-caso-some.log e AVAL-c1-13-lint-caso-some.log, com o cabeçalho `Achado (rodada 3)` e a linha sem barra inicial. Origem: o ramo `na_tabela = "outra"` nos dois scripts.

A2 · MED · AT-005 · exit 1 com traceback, fora do contrato 0, 2, 64
(a) Arquivo de vereditos com `achado` que não é texto (`{"achado": 5}`) → `AttributeError: 'int' object has no attribute 'split'`, exit 1 (AVAL-c1-12-caso-crash.log)
(b) Pasta de revisões ou pasta de `--ledgers` sem permissão de leitura (`chmod 000`) → `PermissionError`, exit 1, sem `RESULTADO:` (AVAL-c1-14-uso-e-exits.log)

A3 · LOW · AT-005 · o medidor recusa o rótulo que o controle do próprio lint usa
`sdd/fixtures/revisao/ledger/controle.md` traz `N1@openrouter:qwen/q-plus` como forma boa. O medidor põe essa forma em fora da conta com uma mensagem que se contradiz: "o rótulo @openrouter:qwen/q-plus não é o da engine que respondeu como auditor (openrouter:qwen/q-plus)". Ele só aceita `@openrouter` ou `@openrouter-qwen-q-plus`. (AVAL-c1-12-caso-fora.log)

A4 · LOW · AT-004 e AT-005 (espírito) · pasta contada como lida cujo custo some sem aviso
Com `reviewer_engine_efetivo` e `reviewer_custo` numérico, mas `reviewer_exit` ausente ou não numérico (`0 (ok)`), a pasta entra em "N pasta(s) lida(s)", não gera linha e não vai para fora da conta. No caso `meta`, US$ 5, US$ 7 e US$ 9 de auditor com exit vazio sumiram, com "4 pasta(s) lida(s)" e só o aviso de ledger. Papel com exit 0 e sem arquivo de vereditos conta a rodada com 0 achados, também sem aviso. É o comportamento da Decision 3 do DESIGN, mas contradiz o "tudo o que ficou fora dos números vai para fora da conta" dos docs. (AVAL-c1-11-caso-meta.log)

A5 · LOW · AT-006 · cabeçalho fora do molde aprovado
O lint só confere os 4 primeiros nomes e a contagem de 7. `| achado | sev | veredito | rodada | evidência | revisão | dano |` sai 0. (AVAL-c1-19-lint-casos-do-avaliador.log)

A6 · notas, sem pedido de correção obrigatório
- `US$ 0.00000001` imprime `0.000000`: custo não nulo exibido como zero. Segue a letra do AT-002 (6 casas abaixo de 0,0001) e os META reais têm 4 casas (AVAL-c1-10).
- `bash sdd/bin/eval-revisores.sh ""` mede a pasta atual em vez de sair 64 (AVAL-c1-14).
- O lint aceita `sem achados: rodada=1 <pasta>` junto com linha de dados para a mesma pasta (c55, AVAL-c1-19).

Contagem: 5 achados (1 HIGH, 1 MED, 3 LOW) + 3 notas.
VEREDITO: NEEDS_WORK
>>>
