# Avaliação de contexto fresco — F19_CUSTO_REVISORES, ciclo 3 (2026-11-10)

Ciclo extra, pedido pelo Roberto depois do teto de 2 ciclos. O avaliador avaliou o commit `0d4a730` em cópia de `git archive`, fora do repositório. Os consertos pedidos (C1, C1b, C2) e os limites declarados (C3 a C5) entraram no commit seguinte da frente. Bloco gravado como veio.

<<<AVALIACAO
feature: F19_CUSTO_REVISORES · modo: veredito · ciclo: 3 (extra) · commit avaliado: 0d4a730 (base 9581740) · DEFINE v1.3 · DESIGN v1.2
ambiente: /usr/bin/python3 3.9.6 + /bin/bash 3.2 (PATH=/usr/bin:/bin) e python3 3.15.0 do PATH; sem rede; sem credenciais
contaminação: nenhuma (o brief trouxe só os achados do ciclo 2 e os números a conferir; li o código dos dois scripts para desenhar as sondas, não o diff)

ACHADOS DO CICLO 2

| Achado | Situação | Prova (log AVAL-c3-…) |
|---|---|---|
| B1 MED · linha sem a barra inicial some | RESOLVIDO nas formas do ciclo 2 e em mais 8 minhas: sem barra, atrás de `>`, `-`, `*`, `+`, `1.`, `#`, `\`, espaço de largura zero, BOM, U+2060, NUL, colada a texto. O lint sai 2 citando a linha e o medidor a lista em "fora da conta". Restam formas raras (C3) | 10, casos a01 a a13, a29, a30 |
| B2 LOW · falsa cerca engole o resto | RESOLVIDO nas formas do ciclo 2: código em linha no começo da linha e ``` indentado por 4 espaços já não escondem nada; bloco ou comentário aberto sem fechar é acusado. Mas o conserto criou REGRESSÃO (C1) | 10, casos b01 a b04; 50 |
| B3 LOW · 1ª célula `achado …` some no medidor | RESOLVIDO: o medidor lista a linha; o lint sai 2 | 10, casos a33, a34 |
| B4 LOW · traceback com exit 1 | RESOLVIDO: nenhum traceback e nenhum exit fora de 0/2/64 em 60 tentativas nos dois pythons (custo de 31 dígitos, exit de 5000 dígitos, JSON aninhado, pasta atual apagada, `PYTHONIOENCODING=ascii`, `LC_ALL=C`, saída fechada, binário, NUL). A linha de 30 mil asteriscos caiu de 19–23 s para 6 s. Resta a mensagem sem o nome do arquivo (C5) | 12 |
| B5 LOW · exit ausente com custo some | RESOLVIDO para exit ausente ou vazio com custo (revisor, auditor, desempate): avisado com o valor. Restam exit ausente sem custo e engine ausente com custo (C4): limite | 11, casos a4b, a4c, a4d, e11c |
| B6 LOW · ledger cita testes que não existem | RESOLVIDO: os 9 testes citados existem em 0d4a730; a sabotagem `if vazios:` agora derruba `test_arquivo_vazio_nao_esconde_as_violacoes_de_outro` | 61 |
| B7 notas | RESOLVIDAS as três: `--ledgers ""` e `--registry ""` saem 64; `sem achados:` num arquivo e linha de dados da mesma revisão em outro saem 2 nas duas ordens; rebatida marcada `sim` não conta em "com dano" e é avisada | 11, casos B7a, B7b, B7c |

REPROVA DOS ATs

| AT | Sonda (log AVAL-c3-…) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | fixtures nos dois pythons; projeto sem git com `review.output_dir: minhas` e com o slot vazio (20) | uma linha por papel + engine + modelo, ordenada, `RESULTADO: MEDIDO` + `→`, exit 0; padrões lidos | 7 linhas na ordem revisor, 2º revisor, auditor; ProvedorA e ProvedorB separados; exit 0; saída idêntica nos dois pythons; os dois padrões lidos | PASS |
| AT-002 | somas em pastas minhas (20); 15 formas de custo (12, d15); 25 pastas reais (02, 03, 11) | pago só de pay-per-token; nominal com todo custo numérico; `n/d` nunca zero; decimal exato; 4 ou 6 casas | 0.3100 + 0.3000 = 0.6100; 0.1 + 0.2 = 0.3000; 0.000090; `≈`, `incerto` e `n/d em N de M` corretos; `US$ 1,234.56`, `US$ .5`, `USD 3` viram `n/d`, nunca zero. Reais: a coluna Nominal soma 59.1043, igual à soma dos `custo_total` dos 25 META | PASS |
| AT-003 | 25 pastas reais + 6 ledgers reais (02); recontagem própria (03); `eval-agree.sh` (20) | números iguais aos dos ciclos anteriores | as 16 linhas de tabela são idênticas às do ciclo 2 (diff vazio). claude-opus-5-5: 83 achados, 62 aplicados, 28 com dano, nominal 50.3657 em 21 parcelas, iguais à minha recontagem. AGREE 78.0% (78 de 100) nos dois scripts | PASS |
| AT-004 | fixtures (20); exits e papéis (11, 12 d16) | falhas por motivo; custo da falha nas somas; `trocada por outra engine`; `indisponível` em fora da conta | `1 credencial`, `1 cota ou tempo` com `1.0000 (incerto em 1 de 1)`, `1 trocada por outra engine`, `2º revisor indisponível: nenhuma engine foi chamada` | PASS |
| AT-005 | uso, SEM DADOS, pasta trancada, rede negada por `sandbox-exec` (20); B5 e números (11); derrubadas (12); formas da linha (10); C1 (50) | 64 e 2 com causa; nenhuma linha de dados descartada em silêncio; sem traceback; sem rede | 64 e 2 corretos; saída idêntica com a rede negada; nenhum traceback. Mas uma linha de dados entre dois blocos de rótulo incomum some com `fora da conta: 0` e o achado vai para "sem classificar" (C1) | FAIL (C1) |
| AT-006 | 6 ledgers reais, 14 arquivos do pacote (30); 68 casos meus contra o lint do ciclo 2 (10); C1 (50); uso (20) | 0 nos legítimos; 2 com `arquivo:linha — motivo`; nenhuma linha de tabela fora de bloco cercado pulada | os 6 ledgers reais saem 0 (126 linhas); controle, retroativo, só-sem-achados e exemplo saem 0; 7 fixtures saem 2 pelo motivo certo; `sem-linhas.md` e o molde vazio saem 64; o molde preenchido sai 0. Mas o lint sai 0, VERDE, "0 linha(s)", com uma linha `HIGH · REBATIDA_EVIDENCIA · dano = sim` não conferida (C1) | FAIL (C1) |
| AT-007 | `loop --ledger` com 5 e 7 colunas, ids rotulados e sem rótulo (20); `test_fluxo`, `test_eval_agree` (05, 06) | 7 colunas fecha o HIGH como o de 5; sem mudança de contrato | saída idêntica nos dois pares (PRONTO, exit 0); sem ledger sai 10; diff de `sdd-fluxo.sh`, `eval-agree.sh`, `adversarial-review.sh` e adapters entre a base e 0d4a730 tem 0 linhas | PASS |
| AT-008 | textos na cópia (20); `test_f19_textos`, `test_contrato_build_release`, `test_docs` (05, 06) | critério, molde, skills com bump, docs EN e PT, contratos, MANIFEST | tudo presente; `sdd-build` 2.7.0 → 2.8.0, `sdd-release` 2.9.1 → 2.10.0; MANIFEST igual a `git ls-tree` (511 e 511) | PASS |
| AT-009 | `bin/sdd-open.sh init --vendors claude --yes` num projeto novo, depois `eval-revisores.sh` (20) | os 4 arquivos chegam; exit 2 `SEM DADOS` | os 4 presentes e idênticos aos do pacote; exit 2 `RESULTADO: SEM DADOS` | PASS |

Testes, com -B, nos dois ambientes (05, 06): test_eval_revisores 51, test_ledger_revisao_lint 24, test_f19_textos 17, test_fluxo 69, test_eval_agree 9, test_contrato_build_release 29, test_docs 23, test_bash32 3. Todos OK.
Sabotagens minhas em cópia (60): 9 de 9 derrubam um teste nomeado. Os consertos do ciclo 2 têm teste com dentes.
NAO_VERIFICADO: Verify Gate com a suíte inteira e `publish-gate.sh` (proibido pelo brief); `tests/test_revisao.py` (fora da lista); linha de base vermelha; retroativo e release v2.10.0 (não são AT); a mudança sem commit na árvore de trabalho.

ACHADOS

C1 · MED · AT-006 e AT-005 · REGRESSÃO do conserto do B2 · PEDE CONSERTO ANTES DE PUBLICAR
A cerca agora só é reconhecida quando o rótulo depois de ``` tem apenas letras, dígitos, `_`, `+`, `.` e `-`. Um bloco aberto por ` ```c# `, ` ```sh title=x `, ` ```{.python} `, ` ``` yaml ` ou por 4 crases não é visto como abertura; a linha ``` que o fecha passa a abrir um bloco.
- Com DOIS blocos assim, a paridade fecha e tudo o que fica entre eles some sem aviso.
- O lint sai 0 e o `sdd-fluxo.sh loop` fecha o HIGH com a linha não conferida.
- É raro (os 6 ledgers reais não têm bloco cercado), mas cai no dano nº 1 do brief.
Reprodução (arquivo `LEDGER_REVISAO_C1.md`):
  linha 5:  ```c#        (ou ```sh title=medicao)
  linha 6:  bash sdd/bin/verify-gate.sh
  linha 7:  ```
  linha 9:  | achado | sev | veredito | rodada | evidência | dano | revisão |
  linha 10: |---|---|---|---|---|---|---|
  linha 11: | R2@rev | MED | APLICADA | rodada=1 | nome trocado | nao | EXTERNAL_REVIEW_20260201-000001 |
  linha 12: | R1@rev | HIGH | REBATIDA_EVIDENCIA | rodada=1 | sem teste | sim | EXTERNAL_REVIEW_20260201-000001 |
  linhas 16 a 18: o mesmo bloco das linhas 5 a 7
  linha 20: sem achados: rodada=2 EXTERNAL_REVIEW_20260201-000002
  bash sdd/bin/ledger-revisao-lint.sh LEDGER_REVISAO_C1.md
    → exit 0, VERDE, "0 linha(s) e 1 rodada(s) sem achados" (esperado: 2, citando a linha 12; o lint de 661ef65 sai 2 com esse motivo)
  bash sdd/bin/sdd-fluxo.sh loop --review sdd/fixtures/fluxo/review-ok --ledger LEDGER_REVISAO_C1.md --rodada 1 --avaliacao sdd/fixtures/fluxo/AVALIACAO_pass.md --ciclo-avaliador 1
    → PRONTO, exit 0, "grave(s) rebatido(s) no ledger: R1@rev"
  bash sdd/bin/eval-revisores.sh <pasta com essa revisão> --ledgers LEDGER_REVISAO_C1.md
    → "0 de 2" aplicados, "2 de 2" sem classificar; nenhuma linha do ledger em "fora da conta" (só o aviso genérico de pasta sem ledger)
- Com outras linhas da mesma revisão fora dos blocos, o medidor mostra `fora da conta: 0` e o achado some em silêncio (log 10, casos b05 e b05b).
- Com ` ```sh ` no lugar, lint e medidor acusam a linha 12 (controle no log 50).
- Sugestão: seguir o CommonMark. Abre com 3 ou mais crases ou tis e qualquer rótulo (sem crase no rótulo, para a cerca de crases); fecha só com o mesmo caractere, em quantidade igual ou maior, sem rótulo. Isso fecha C1 e C1b sem reabrir o B2.
Evidência: AVAL-c3-50-ACHADO-C1-cerca-com-info-string.log; AVAL-c3-10-formas-da-linha-e-falso-positivo.log, casos b05, b05b, b05d.

C1b · LOW · AT-006 · mesma causa do C1 · falso positivo novo; some com o conserto do C1
Um ledger legítimo com UM bloco desses passa a reprovar com "bloco cercado aberto e não fechado", apontando para a linha que fecha o bloco. O lint do ciclo 2 saía 0 em todos estes casos:
- ` ```sh title=x ` antes da tabela: lint 2; o medidor não lê as linhas seguintes (avisa, mas os achados vão para "sem classificar");
- bloco de 4 crases com tabela de exemplo dentro: lint 2 ("a linha tem 3 célula(s)");
- bloco `~~~` com uma linha ``` dentro, e o inverso: lint 2.
A `sdd-release` aborta com lint diferente de 0, então isso trava a publicação com uma mensagem que não explica a causa. Erra para o lado seguro.
Evidência: log 10, casos b06, b07, b08, b11; log 50, arquivo `LEDGER_REVISAO_C1_um_bloco.md`.

C2 · LOW · AT-006 · falso positivo da regra nova, por desenho e não declarado · PEDE CONSERTO DE TEXTO ANTES DE PUBLICAR (mensagem, ajuda e molde)
Toda linha de texto com 4 ou mais barras verticais soltas reprova no lint e vira aviso no medidor. O ciclo 2 saía 0. Exemplos que reprovam:
- `A condição era `a || b || c`.`
- `Medição: `grep x log | sort | uniq -c | sort -rn | head``
- `O cabeçalho é `| achado | sev | … |`.`
- uma linha de navegação com 5 links separados por `|`.
A mensagem ("linha com forma de linha do ledger fora da tabela: toda linha do ledger começa por `|`") não diz que o gatilho são as 4 barras nem como sair. A regra só está escrita no código; ajuda, molde e docs dizem "texto corrido pode ficar".
- Passam, como devem: texto com até 3 barras, barras escapadas com `\|`, evidência com `\|`, citação, listas, régua, CRLF, cabeçalho em negrito repetido, tabela dentro de item de lista, o molde preenchido, os 6 ledgers reais.
- Saída barata: a mensagem dizer "4 ou mais `|` numa linha de texto: escape com `\|` ou ponha num bloco cercado" e a ajuda e o molde declararem a regra. As duas saídas funcionam (casos c06 e b09).
Evidência: log 10, casos c03, c04, c08, c13, c17.

C3 · LOW · AT-006 · resto do B1 · LIMITE ACEITÁVEL A DECLARAR
Formas em que a linha ruim ainda some com lint 0 e `fora da conta: 0`. Nenhuma é regressão: o ciclo 2 também saía 0.
- depois de um comentário fechado na mesma linha: `<!-- nota --> | R3 | HIGH | … |`, ou depois do `-->` que fecha um comentário de várias linhas. É a mais plausível das quatro; conserto de uma linha (ler o resto depois do `-->`);
- menos de 4 barras soltas e sem a barra inicial (células coladas, ou parte das barras escapadas);
- barras de largura cheia (`｜`);
- todas as barras escapadas (é texto puro; não considero falha).
Evidência: log 10, casos a14, a16, a17, a18, a19, a36.

C4 · LOW · AT-005 · resto do B5 e números · LIMITE ACEITÁVEL A DECLARAR (A-002 já cobre parte)
O medidor deixa de fora, sem linha própria em "fora da conta":
- papel sem `*_exit` e sem custo, mas com achados no arquivo de vereditos: os achados não contam; as linhas do ledger aparecem como "achado R1 não está em …", o que engana (casos e10, e10c);
- papel com exit e custo mas com a engine `-` ou ausente: o custo de US$ 7 some sem aviso (casos e11, e11b). O `adversarial-review.sh` sempre grava a engine; só acontece com META editado à mão;
- linha truncada ou sem a chave `achado` no arquivo de vereditos: o achado não conta e nada avisa (casos e01, e01b). Nas 25 pastas reais, 0 linhas ilegíveis.
Evidência: AVAL-c3-11-B5-B7-e-numeros.log.

C5 · notas, sem pedido de correção
- Dado corrompido sai 64 sem traceback, mas a mensagem ("não consegui medir (InvalidOperation: …)" + "corrija o arquivo citado acima") não cita arquivo nem pasta; com 25 pastas, não dá para saber qual (log 12, d01, d15j).
- O medidor conta em "com dano" uma linha `APLICADA` + `dano = sim` sem `teste:`, que o lint reprova. Ele confia no ledger sem dizer que não foi conferido (log 11, B7c).
- Arredondamento bancário na exibição: `US$ 1.00005` imprime 1.0000 e `US$ 1.00015` imprime 1.0002 (log 12, d15h, d15i).
- Pasta copiada (`… copy`, `…-2`) conta como rodada nova, com o aviso "sem linha em nenhum ledger" (log 11, e02).
- "Sem achados graves nesta rodada." em texto corrido reprova, com mensagem clara; já era assim no ciclo 2 (log 10, c09).

O QUE PEDE CONSERTO ANTES DE PUBLICAR
- C1 (junto com C1b, mesma causa): reconhecimento da cerca. Único achado em que o lint sai 0 com linha não conferida e que o ciclo anterior pegava.
- C2: só texto (mensagem do lint, ajuda, molde). Sem isso, um ledger legítimo trava a release sem explicação.
O QUE É LIMITE ACEITÁVEL A DECLARAR
- C3, C4 e as notas de C5.

Contagem: 5 achados (1 MED, 4 LOW) + 5 notas. Do ciclo 2: B3, B6 e B7 resolvidos; B1, B4 e B5 resolvidos com resto declarável (C3, C5, C4); B2 resolvido nas formas reproduzidas, com regressão nova (C1, C1b).
VEREDITO: NEEDS_WORK
>>>
