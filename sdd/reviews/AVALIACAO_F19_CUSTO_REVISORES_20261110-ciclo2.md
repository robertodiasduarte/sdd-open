# Avaliação de contexto fresco — F19_CUSTO_REVISORES, ciclo 2 (2026-11-10)

Avisos do avaliador antes do bloco: avaliou o commit `661ef65` numa cópia de `git archive` fora do repositório; a árvore de trabalho mudou durante a avaliação (o conserto do `--ledgers ""`, ainda sem commit) e essa mudança não foi avaliada. Desvio dele: uma sabotagem saiu com o padrão `test_*.py` e rodou a suíte inteira numa cópia sabotada por cerca de 3 minutos; parou, não usou o resultado e refez só com os testes permitidos. Gravou 24 logs `AVAL-c2-*.log`. Os caminhos de máquina foram tirados deste registro.

<<<AVALIACAO
feature: F19_CUSTO_REVISORES · modo: veredito · ciclo: 2 · commit avaliado: 661ef65 (base 9581740) · DEFINE v1.2 · DESIGN v1.2
ambiente: /usr/bin/python3 3.9.6 + /bin/bash 3.2 (PATH=/usr/bin:/bin) e python3 3.15.0 do PATH; sem rede; sem credenciais
contaminação: nenhuma

ACHADOS DO CICLO 1

| Achado | Situação | Prova (log AVAL-c2-…) |
|---|---|---|
| A1 HIGH · linha some depois de linha em branco, id decorado ou 2º cabeçalho | RESOLVIDO nas formas do ciclo 1; continua ABERTO noutra forma (B1, B2, B3) | 10: as formas do ciclo 1 saem 2 no lint e são contadas ou listadas pelo medidor; 14 de 44 formas minhas ainda somem |
| A2 MED · traceback com exit 1 | RESOLVIDO nos dois casos: `{"achado": 5}` sai 0; pasta ou `--ledgers` com `chmod 000` sai 64 com causa. Há outros tracebacks (B4) | 11, 12, 12b |
| A3 LOW · rótulo `N1@openrouter:qwen/q-plus` recusado | RESOLVIDO: conta como falso positivo, `fora da conta: 0`; `N1@codex` continua recusado com o motivo | 11 |
| A4 LOW · custo que some sem aviso | RESOLVIDO para exit ilegível (`0 (ok)`) e para papel sem arquivo de vereditos, os dois avisados. Exit ausente ou vazio continua sem aviso: limite declarado (A-002 do DEFINE, Decision 3), ver B5 | 11, 22 |
| A5 LOW · cabeçalho fora do molde aprovado | RESOLVIDO: `dano` e `revisão` trocados saem 2, com uma mensagem só | 10 (caso 27), 30 (c36 a c38) |
| A6 notas | RESOLVIDAS as três: `US$ 0.00000001` imprime `<0.000001`; argumento `""` sai 64; `sem achados:` com linha de dados da mesma revisão sai 2 | 11, 30 (c44) |

REPROVA DOS ATs

| AT | Sonda (log AVAL-c2-…) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | fixtures com os dois pythons (01); padrões num projeto sem git, com `review.output_dir: minhas` e com o slot vazio (23) | uma linha por papel + engine + modelo com provedor, ordenada, `RESULTADO: MEDIDO` + `→`, exit 0; padrões lidos | 7 linhas na ordem revisor, 2º revisor, auditor; ProvedorA e ProvedorB separados; exit 0; os três padrões lidos | PASS |
| AT-002 | 7 pastas minhas com as formas de custo (20); 25 pastas reais (02, 03, 03b) | pago só de pay-per-token; nominal com todo custo numérico; `n/d em N de M`; `incerto`; decimal exato; 4 ou 6 casas; `≈` | 0.1+0.2 = 0.3000; 0.000090 e por dano 0.000030; `≈2.9200 (n/d em 2 de 6)`; assinatura paga 0.0000; cobrança desconhecida `n/d`; `1.0000 (n/d em 1 de 2, incerto em 1 de 2)`. Reais: 50.3657 em 21 parcelas e 5.1073 em 4, iguais à minha soma | PASS |
| AT-003 | 25 pastas reais + 6 ledgers reais (02); comparação com o log do ciclo 1 (03); `eval-agree.sh` nas mesmas pastas (42) | contagens por linha; AGREE igual ao `eval-agree.sh`; taxa com amostra | as 15 linhas da tabela são idênticas às do ciclo 1 (diff vazio). claude-opus-5-5: 83 achados, 62 aplicados, 28 com dano, nominal 50.3657. AGREE 78.0% (78 de 100) nos dois scripts | PASS |
| AT-004 | exits 65, 67, 68, 1, 124, -1; troca de engine; `indisponível`; desempate (21) | falhas por motivo fora das rodadas; custo da falha nas somas; `trocada por outra engine`; `indisponível` em fora da conta | `6 (1 cota ou tempo, 1 credencial, 3 outro, 1 resposta inválida)`, rodadas 0, pago 1.8750 `(n/d em 2 de 6)`; codex com `1 trocada por outra engine`; `2º revisor indisponível: nenhuma engine foi chamada` | PASS |
| AT-005 | uso, padrões, rede negada por `sandbox-exec`, hash das fixtures (23); 14 motivos de fora da conta (22); A2 a A6 (11); 44 formas de escrever a linha (10, 50); derrubadas (12, 12b) | 64 e 2 com causa; toda linha de dados fora da conta listada com `arquivo:linha`; avisos novos; sem traceback em pasta ilegível e argumento vazio; sem rede | 64 e 2 corretos; os 6 motivos do AT e os avisos novos listados; saída idêntica com a rede negada; fixtures com o mesmo hash. Mas linha de tabela sem a barra inicial some com `fora da conta: 0` (B1), e também atrás de falsa cerca (B2) e com 1ª célula `achado …` (B3) | FAIL (B1) |
| AT-006 | 11 fixtures do pacote e 57 casos meus (30); 44 formas (10); caso mínimo (50) | 0 no controle, retroativo e só-sem-achados; 2 com `arquivo:linha — motivo`; 64 em uso, ilegível ou vazio; nenhuma linha de tabela pulada | 7 fixtures saem 2, cada uma pelo seu motivo; controles 0; `sem-linhas.md` 64; 56 de 57 casos como esperado (o 57º é a nota B7). Mas o lint sai 0, VERDE, com uma linha `REBATIDA_EVIDENCIA` + `dano = sim` sem teste escrita sem a barra inicial (B1) | FAIL (B1) |
| AT-007 | `sdd-fluxo.sh loop --ledger` com 5 e 7 colunas, ids rotulados e sem rótulo (40); `test_fluxo`, `test_eval_agree` (05, 06) | 7 colunas fecha o HIGH como o de 5; sem mudança de contrato | saída idêntica nos dois pares (exit 0, `graves_abertos: 0`); sem ledger sai 10; diff de `sdd-fluxo.sh`, `eval-agree.sh`, `adversarial-review.sh` e adapters entre a base e 661ef65 tem 0 linhas; 69 e 9 testes OK | PASS |
| AT-008 | textos na cópia (43); `test_f19_textos`, `test_contrato_build_release`, `test_docs` (05, 06) | critério, molde, 5c e item 8 com bump; seção do medidor em EN e PT; `cli-conventions`; contratos; MANIFEST | tudo presente; `sdd-build` 2.7.0 → 2.8.0, `sdd-release` 2.9.1 → 2.10.0; MANIFEST igual a `git ls-tree` (511 e 511, diff vazio); nenhum nome de engine novo nas skills | PASS |
| AT-009 | `bin/sdd-open.sh init --vendors claude --yes` num projeto novo, depois `eval-revisores.sh` (41) | os 4 arquivos chegam; exit 2 `SEM DADOS` | os 4 presentes e idênticos aos do pacote; exit 2 `RESULTADO: SEM DADOS` | PASS |

Testes, sempre com -B, nos dois ambientes (05, 06): test_eval_revisores 42, test_ledger_revisao_lint 17, test_f19_textos 17, test_fluxo 69, test_eval_agree 9, test_contrato_build_release 29, test_docs 23, test_bash32 3. Todos OK.
Sabotagens minhas em cópia (60): 7 de 7 derrubam um teste nomeado (cabeçalho de 4 nomes, linha de id decorado pulada no lint e no medidor, `sem achados` + dados, exit ilegível, rótulo de id cru, `listar()` sem tratar erro). Os consertos do ciclo 1 têm teste com dentes.
NAO_VERIFICADO: Verify Gate com a suíte inteira e `publish-gate.sh` (proibido pelo brief); `tests/test_revisao.py` (fora da lista autorizada); linha de base vermelha; relatório retroativo e release v2.10.0 (não são AT); a mudança sem commit na árvore de trabalho.

ACHADOS

B1 · MED · AT-005 e AT-006 · resto do A1: linha de tabela sem a barra inicial some sem aviso no lint e no medidor
Os dois scripts só tratam como linha de tabela a que começa por `|`. Uma linha de dados colada à tabela sem a barra inicial (o GitHub a mostra como linha normal) é ignorada. O lint sai 0 dizendo "2 linha(s)" e o medidor mostra `fora da conta: 0`, com o achado em "sem classificar". Nenhum texto do pacote declara esse limite.
Reprodução, numa pasta com uma revisão de 3 achados (R1, R2, R3) e este ledger:
  | achado | sev | veredito | rodada | evidência | dano | revisão |
  |---|---|---|---|---|---|---|
  | R1 | LOW | APLICADA | rodada=1 | texto | nao | EXTERNAL_REVIEW_20260301-000001 |
  | R2 | LOW | APLICADA | rodada=2 | x | nao | EXTERNAL_REVIEW_20260301-000001 |
  R3 | HIGH | REBATIDA_EVIDENCIA | rodada=2 | sem teste | sim | EXTERNAL_REVIEW_20260301-000001 |
  bash sdd/bin/ledger-revisao-lint.sh LEDGER_REVISAO_MIN.md   → exit 0, VERDE, "2 linha(s)" (esperado: 2, citando a linha 5)
  bash sdd/bin/eval-revisores.sh rev --ledgers LEDGER_REVISAO_MIN.md   → "2 de 3" aplicados, "0 de 3" falsos positivos, "fora da conta: 0" (esperado: linha 5 contada ou listada)
Com a barra inicial na linha 5, o lint sai 2 e o medidor conta o falso positivo (controle no mesmo log).
- Mesma origem, mesmas saídas: `> | R3 …` (citação), `- | R3 …` (item de lista), `\| R3 …`, espaço de largura zero antes da barra, e BOM no início do arquivo quando a 1ª linha é de dados.
- O `sdd-fluxo.sh loop --ledger` também ignora a linha e mantém o HIGH aberto (exit 10), então o grave não fecha por engano (log 44).
- Duas saídas possíveis, a decidir por quem constrói: acusar toda linha fora da tabela que tenha forma de linha de ledger, ou declarar no DEFINE e na ajuda que linha do ledger começa por `|`.
Evidência: AVAL-c2-50-ACHADO-B1-linha-sem-barra-inicial.log; AVAL-c2-10-linha-que-some.log, casos 06, 07, 16a, 16b, 19a, 19b, 25.

B2 · LOW · AT-005 e AT-006 · falsa cerca engole o resto do arquivo sem aviso
Qualquer linha que comece por ``` ou ~~~ liga ou desliga o "bloco cercado", mesmo quando o Markdown não a trata como cerca.
- Uma linha de texto que começa por código em linha faz as linhas de dados seguintes sumirem: lint 0, medidor `fora da conta: 0`.
- O mesmo com ``` indentado por 4 espaços.
- Cerca ou comentário `<!--` aberto e nunca fechado engole o resto sem aviso. Isso é coerente com o Markdown e com "fora de bloco cercado e de comentário" do AT, mas nada avisa que o arquivo terminou dentro do bloco.
Evidência: AVAL-c2-10-linha-que-some.log, casos 11, 13, 14, 15.

B3 · LOW · AT-005 · o medidor pula sem aviso a linha cuja 1ª célula começa por "achado"
`| achado R3 | HIGH | REBATIDA_EVIDENCIA | … |` sai 2 no lint, como cabeçalho fora do molde, mas no medidor some com `fora da conta: 0`. O comentário na linha 184 de `sdd/bin/eval-revisores.sh` ainda descreve a regra antiga ("Só a tabela cujo cabeçalho começa por `achado`").
Evidência: AVAL-c2-10-linha-que-some.log, casos 18 e 18b.

B4 · LOW · AT-005 (espírito do A2) · ainda há exit 1 com traceback em dado corrompido
O AT só exige 64 sem traceback para pasta ilegível e argumento vazio, e isso passa. Fora da letra, o medidor ainda cai com:
- `reviewer_custo : US$ 1000000000000000000000000000000` → `decimal.InvalidOperation`, nos dois pythons;
- `reviewer_exit` com 5000 dígitos → `ValueError`, só no 3.15;
- arquivo de vereditos com JSON muito aninhado → `RecursionError`, só no 3.9;
- pasta atual apagada → `FileNotFoundError`, nos dois;
- `PYTHONIOENCODING=ascii` → `UnicodeEncodeError`, nos dois scripts.
Uma guarda única no topo fecharia a classe. O lint não caiu em nenhuma das minhas tentativas; só demora 19 a 23 segundos numa linha de 30 mil asteriscos.
Evidência: AVAL-c2-12-derrubar-os-scripts.log, AVAL-c2-12b-tracebacks-verbatim.log.

B5 · LOW · AT-004 e AT-005 · resto do A4: exit ausente ou vazio, com engine e custo presentes, some sem aviso
Sem a linha `auditor_exit` (ou com ela vazia) e com `auditor_custo : US$ 7`, a pasta conta como lida, o auditor não vira linha e `fora da conta` fica em 0. Sem `reviewer_exit`, o revisor some e a linha dele no ledger é acusada como "achado R1 não está em …", o que engana. É o limite declarado na A-002 e na Decision 3, mas os docs dizem "tudo o que ficou fora dos números vai para fora da conta".
Evidência: AVAL-c2-11-achados-A2-a-A6.log, casos a4b, a4c, a4d.

B6 · LOW · registro · o ledger desta frente cita testes que não existem no commit avaliado
`sdd/reviews/LEDGER_REVISAO_F19_CUSTO_REVISORES.md` cita dois testes que saíram da suíte neste ciclo:
- linha 10 (R1, `dano = sim`): `test_linhas_depois_de_linha_em_branco_continuam_sendo_o_ledger`;
- linha 12 (R3): `test_arquivo_vazio_nao_esconde_as_violacoes_de_outro`.
O comportamento do segundo ficou sem teste: sabotado (`if vazios:` no lugar de `if vazios and not violacoes:`), `test_ledger_revisao_lint` continua OK com 17 testes. O lint não confere se o teste citado existe (limite declarado na Decision 2).
Evidência: AVAL-c2-61-testes-citados-no-ledger-da-F19.log, AVAL-c2-62-sabotagens-testes-retirados.log.

B7 · notas, sem pedido de correção obrigatório
- `--ledgers ""` é aceito e lê a pasta atual, em vez de sair 64 (log 11, caso a6b). A mudança sem commit na árvore de trabalho parece tratar disso; não avaliei.
- `sem achados:` num arquivo e linha de dados da mesma revisão em outro, passados juntos, saem 0 (log 30, c45). O AT só fala de "entre os arquivos" para achado repetido.
- O medidor conta em "com dano" uma linha `REBATIDA_EVIDENCIA` com `dano = sim`, que o lint reprova (log 50, controle).

Contagem: 6 achados (1 MED, 5 LOW) + 3 notas. Do ciclo 1: A2, A3, A5 e A6 resolvidos; A4 resolvido com limite declarado; A1 resolvido nas formas reproduzidas e aberto na forma B1.
VEREDITO: NEEDS_WORK
>>>
