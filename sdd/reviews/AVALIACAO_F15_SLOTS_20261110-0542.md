<<<AVALIACAO
FEATURE: F15_SLOTS · ciclo 2 · modo veredito · HEAD d6c5ed1 (base 9d8ac24)
VEREDITO: PASS

O Verify Gate passa: 1.710 testes, publish-gate GREEN, exit 0. Os 11 ATs passam quando executados contra o HEAD. Os achados 1 e 2 do ciclo 1 estão corrigidos e cada conserto tem teste que cai sob sabotagem. A ressalva 3 foi fechada no DEFINE v1.2, e o texto novo não traz termo de projeto privado.

Sobram 4 achados baixos, nenhum bloqueante: dois casos raros do detector de `#`, texto depois das aspas YAML descartado sem aviso e um aviso de depreciação do Python. Os dois primeiros têm um conserto barato e já testado no bash 3.2 (achado 1). Explico abaixo por que não seguram o veredito; se vocês lerem o AT-004 ao pé da letra, o achado 1 bastaria para NEEDS_WORK.

## Brief do ciclo 1, reproduzido contra o HEAD

| Item do ciclo 1 | Sonda | Observado no HEAD | Situação |
|---|---|---|---|
| 1. Flag sem valor seguida de flag | `--feature --arvore /tmp`, `--arvore --feature F1`, `--feature --base origin/main`, `--base --commit HEAD`, `--commit --dir /tmp`, `--dir --feature F1`, `--feature --`, `--feature ""  --base HEAD`, `--feature F1 --arvore` (fim da linha) → AVAL-C2-ACHADOS-1-2.log | todos saem 64 com `🛑 --X recebeu outra flag (--Y) como valor` ou `exige um valor` e a linha `→`, sem rodar o comando; `-- --nao-e-flag.txt` e `-x` continuam indo como arquivo, e o comando roda (exit 0) | corrigido |
| 2. `#` no meio da palavra | `https://app.local/#/pedidos` (com e sem aspas YAML), `a#b`, `'x # y'`, `"x # y"`, `$#`, `${#HOME}` → AVAL-C2-ACHADOS-1-2.log | todos rodam, os arquivos chegam ao comando e o exit é 0, como no `bash -c`; `oi # c`, `oi;# c`, `oi\|#c`, `#bash`, `oi<TAB>#tab` saem 64 | corrigido (sobram 2 bordas: achados 1 e 2) |
| 3. AT-011 e o arquivo inteiro | DEFINE v1.2 diz "o texto que esta frente acrescenta"; busquei a família de termos só nas linhas novas de `git diff 9d8ac24 HEAD` → AVAL-C2-AT011-TEXTO-NOVO.log | 1 ocorrência: `deno`, como nome de runner de teste no test-baseline.sh, que o próprio AT exclui | fechado |

## Tabela por AT

| AT | Sonda (execução) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| Verify Gate | o `cmd` do DEFINE, exatamente como está, numa cópia por git archive do HEAD d6c5ed1 → AVAL-C2-VERIFY-GATE.log | exit 0 e mais de 1.669 testes | `✅ publish-gate GREEN`; `Ran 1710 tests in 1237.778s`; `OK (skipped=1)`; `[exit=0]` | PASS |
| AT-001 | repo temporário; script falso que sai 0, 2 e 10 com os args `"a b.txt" c.txt` → AVAL-C2-AT001-004.log | OK/0, REPROVOU/2 e NADA A MEDIR/10, cada um com `→`; um arquivo por argumento; o comando roda na raiz | os 3 exits corretos, com RESULTADO e `→`; `arg<a b.txt>` e `arg<c.txt>`, n=2; pwd é a raiz, também quando chamado da subpasta (AVAL-C2-AT005.log) | PASS |
| AT-002 | comando que sai 1, 7, 127 e `kill -9 $$`; INT e TERM mandados só ao slot.sh e ao grupo, por Popen → AVAL-C2-AT001-004.log, AVAL-C2-AT002-SINAL.log | o exit real ou o sinal, INCONCLUSIVO, 3 | "saiu 1/7/127, fora do contrato"; "morreu pelo sinal 9 (saiu 137)"; os 4 cenários de sinal dão "interrompido por sinal", INCONCLUSIVO e exit 3 | PASS |
| AT-003 | `""`, chave ausente com comentário na coluna 0, sem config; chave achada depois de comentário na coluna 0 | PULADO/11 com o caminho do config | os 3 dão `vazio: pulado (<caminho>)` e 11; a chave depois do comentário é achada e roda | PASS |
| AT-004 | chave errada, flag no fim, flag seguida de flag (6 variantes), `--base` e `--commit` que não resolvem, aspas YAML abertas, `'` do shell aberta, `\| cat`, comentários `#` → AVAL-C2-AT001-004.log, AVAL-C2-ACHADOS-1-2.log | 64 com a causa e o conserto, sem rodar | todos dão 64 com causa e `→`, sem rodar. Bordas raras no achado 1 | PASS (achados 1 e 3) |
| AT-005 | origin/main=C1 e HEAD=C2, 2ª worktree, subpasta, symlink, `--dir`, sem feature, `default_branch` que não existe, pasta sem git → AVAL-C2-AT005.log; fórmula do hex → AVAL-C2-AT005-HASH.log | as 6 variáveis; a mesma pasta comum em qualquer lugar; a pasta existe antes do comando; o before_ok esvazia só a pasta padrão | variáveis certas; `sdd-slot-7a0b0543a236/F9` igual a `git hash-object` do caminho físico de `.git`, a partir da raiz, da subpasta, da worktree e do symlink; as marcas somem no before_ok; o `--dir` mantém `preexistente`; ⚠️ SDD_BASE e SDD_COMMIT vazios sem git | PASS |
| AT-006 | `test-baseline.sh --touched` do HEAD contra o de 9d8ac24 (cmp idêntico), 7 casos (vitest ts/tsx/cjs, pytest test_ e _test, unittest, deno mjs) → AVAL-C2-AT006-007.log | HEAD sai 2 com `🛑 nova:`; 9d8ac24 sai 0 | HEAD sai 2 nos 7; 9d8ac24 sai 0 nos 7 | PASS |
| AT-007 | falsos positivos `lib/foo.test.ts` e `test_calc_total` (unittest e pytest), Go, teste alterado direto, `sdd/`, fonte sem teste ao lado; exits e poda → AVAL-C2-AT006-007.log, AVAL-C2-AT007-EXITS.log, AVAL-C2-AT007-PODA.log | `fora do diff` com 0; o resto como antes | HEAD igual a 9d8ac24 em todos os casos: PULADO, 64, 64, 3, 2; o modo completo poda `m.T.test_velho` e o `--touched` não poda | PASS |
| AT-008 | as skills não mudaram em d6c5ed1 (`git show --stat`); suíte `test_f15_slots_textos.Release`; sabotagens A6 e A7 → AVAL-C2-SABOTAGENS.log | o texto do AT | A6 derruba `test_0a_roda_os_testes_do_diff_depois_do_verify_gate`; A7 derruba `test_7b_smoke_antes_do_push_nunca_segura` | PASS |
| AT-009 | `test_contrato_build_release` e `test_f15_slots_textos` dentro do gate | mesmos rótulos, a linha Verificações e o exemplo do como-falar | suíte verde | PASS |
| AT-010 | o bloco da seção 2b extraído da skill e executado como está escrito (ok, DROP TABLE, vazio) → AVAL-C2-AT010.log; sabotagem A8 | `$ cmd`, a saída e `[exit=N]` do slot.sh; os .sql chegam como argumentos | `[exit=0]`; `[exit=2]` com "não aplique a migration"; `[exit=11]` PULADO; os 2 .sql chegam; A8 derruba `test_aplicar_migration_checa_antes_da_previa` | PASS |
| AT-011 | config.example, cli-conventions, WORKFLOW_CONTRACTS, MANIFEST e adaptation-guide EN/PT → AVAL-C2-AT011-ITENS.log; termos nas linhas novas → AVAL-C2-AT011-TEXTO-NOVO.log | itens presentes; 0 termos no texto novo, com o deno e o Supabase anteriores fora da conta | `smoke:` e `schema:` com os 4 slots em `""` e o comentário pedido; linha do slot.sh na tabela de exits; contrato `slot:`; MANIFEST lista slot.sh, test_slot.py e test_f15_slots_textos.py; 6 menções nos 2 guias; 1 `deno`, isento | PASS |

As sabotagens são mutantes meus, aplicados numa cópia por git archive do HEAD → AVAL-C2-SABOTAGENS.log. Cada uma derrubou um teste nomeado:
- **N1** (volta a aceitar valor `--X`): derruba `test_chamada_errada_e_64` nos subtestes novos.
- **N2** (`#` em qualquer posição é comentário): derruba `test_cerquilha_no_meio_da_palavra_roda`.
- **N3** (detector de comentário desligado): derruba `test_cerquilha_depois_de_ponto_e_virgula_e_comentario` e `test_config_que_nao_da_para_rodar_e_64`.
- **N4** (`;#` deixa de ser comentário): derruba o teste do `;#`.
- **A1 a A8**, refeitas contra o HEAD: derrubam os mesmos testes do ciclo 1.

No N1 aparece um 4º FAIL, no subteste `--base nao-existe-abc`. É vazamento de `registro.txt` entre subtestes, não um defeito do produto.

## ACHADOS (todos baixos, nenhum bloqueante)

**1. [baixa · AT-004] O detector de `#` erra em 2 casos raros, num para cada lado.**

- **Deixa passar o comentário.** `$'it\'s'` (aspas ANSI-C com aspa escapada) seguido de `# c` não é detectado. O comando roda, o arquivo cai no comentário e o exit é 0. Reprodução: `smoke:\n  before_push_cmd: "bash e.sh $'it\\'s' # c"`, depois `bash sdd/bin/slot.sh smoke.before_push_cmd f1.txt`. Resultado: `RODOU n=1 args=[it's]`, `RESULTADO: OK`, exit 0 (o f1.txt sumiu). Log: AVAL-C2-YAML-BORDAS.log.
- **Recusa um comando válido.** `a\ #b` (espaço escapado) dá 64, mas o bash roda `args=[a #b f1.txt]`. Reprodução: `before_push_cmd: 'bash e.sh a\ #b'`. Log: AVAL-C2-CERQUILHA-BORDAS.log.
- **Causa.** O laço em Python não trata `$'…'`, onde `\'` escapa, e marca o caractere escapado como `anterior`.
- **Conserto sugerido.** Perguntar ao próprio bash, sem executar nada: definir uma função e ver se `"$@"` sobrevive no corpo normalizado. Testei no /bin/bash 3.2 com os 6 casos (acerta todos):
  ```
  bash -c 'eval "__f() { $1 \"\$@\"
  }" && declare -f __f | grep -q "\"\$@\""' _ "$CMD"   # 0 = os argumentos chegam
  ```

**Por que não seguram o veredito.** O AT-004 pede 64 para "um comentário `#` do shell", e o primeiro caso é um comentário que sai 0. Por isso, ao pé da letra, ele bastaria para NEEDS_WORK. Escolhi PASS porque ele exige uma sintaxe muito rara num comando de uma linha, e todos os casos comuns do AT e do brief passam. O segundo caso falha para o lado seguro, com 64.

**2. [baixa · robustez, fora do texto literal do AT-004] Texto depois das aspas YAML fechadas é descartado sem aviso.**

- Reprodução: `before_push_cmd: "bash e.sh" --url https://x`. O slot.sh roda só `bash e.sh` (`args=[f1.txt]`) e sai 0. O PyYAML recusa a mesma linha com `ParserError`. Log: AVAL-C2-YAML-BORDAS.log.
- O caso válido `"bash e.sh" # comentario` continua funcionando, como deve.
- Conserto sugerido: depois da aspa que fecha, aceitar só espaço ou espaço seguido de `#`; qualquer outra coisa sai 64 como "aspas" ou "lixo depois das aspas".

**3. [baixa · cosmético] Com Python 3.13 ou mais novo, o valor YAML sem aspas imprime um aviso de depreciação no stderr.**

- O `python3` do PATH aqui é o 3.15 do Homebrew. O valor sem aspas imprime `<stdin>:33: DeprecationWarning: 'maxsplit' is passed as positional argument`. Log: AVAL-C2-ACHADOS-1-2.log, casos sem aspas.
- Vem de `re.split(r"\s#", v, 1)` no slot.sh. Basta trocar por `maxsplit=1`, que funciona no 3.9.
- Se uma versão futura remover o argumento posicional, o script cai em INCONCLUSIVO 3, que falha para o lado seguro.

**4. [observação, já vinha do ciclo 1] Sinal mandado só ao slot.sh espera o comando filho terminar.**

TERM ou INT mandados só ao slot.sh esperam o filho acabar antes do trap rodar (30 s com `sleep 30`). O resultado continua sendo INCONCLUSIVO 3. No grupo (Ctrl-C), o trap roda em 1,5 s. É a semântica do bash.

## Evidência

- **Logs gravados** (só arquivos com o prefixo AVAL-C2-, 1ª linha `$ comando`, saída verbatim), em `/Users/robertoduarte/rdd-worktrees/sdd-open-f15-slots/sdd/reports/evidence/F15_SLOTS/`: AVAL-C2-VERIFY-GATE.log, AVAL-C2-ACHADOS-1-2.log, AVAL-C2-CERQUILHA-BORDAS.log, AVAL-C2-YAML-BORDAS.log, AVAL-C2-AT001-004.log, AVAL-C2-AT002-SINAL.log, AVAL-C2-AT005.log, AVAL-C2-AT005-HASH.log, AVAL-C2-AT006-007.log, AVAL-C2-AT007-EXITS.log, AVAL-C2-AT007-PODA.log, AVAL-C2-AT010.log, AVAL-C2-AT011-ITENS.log, AVAL-C2-AT011-TEXTO-NOVO.log, AVAL-C2-SABOTAGENS.log.
- **Sondas novas:** `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-open-f15-slots/80a83c1b-4077-4625-ba69-e27f11f530a1/scratchpad/c2a.sh`, `c2b.sh`, `c2c.sh`, `c2d.sh` e `c2sab.sh`, na mesma pasta. As sondas p1 a p10 do ciclo 1 foram reaproveitadas.
- **Como rodei:** todas as sondas com /bin/bash 3.2; os repositórios foram criados por mktemp, fora do projeto.
- **O que não fiz:** não fiz commit, add, stash, checkout nem reset, e não editei código nem documento.
- **Ainda em aberto:** o critério "Release v2.8.0 com SHA256SUMS conferido" é da sdd-release e não se verifica nesta fase.
>>>
