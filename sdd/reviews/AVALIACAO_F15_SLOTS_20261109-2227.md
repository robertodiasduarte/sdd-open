<<<AVALIACAO
FEATURE: F15_SLOTS · ciclo 1 · modo veredito · HEAD 9747f9b (base 9d8ac24)
VEREDITO: NEEDS_WORK

O Verify Gate passa. 10 dos 11 ATs passam quando executados. O AT-004 falha num caso que ele cita literalmente ("uma flag vem sem valor"). Quando uma flag sem valor vem seguida de outra flag, o slot.sh toma a flag seguinte como valor, roda o comando e sai 0, em vez de sair 64 sem rodar nada.

## Tabela por AT

| AT | Sonda (execução) | Esperado | Observado | Resultado |
|---|---|---|---|---|
| Verify Gate | o `cmd` do DEFINE, exatamente como está, numa cópia por git archive → AVAL-VERIFY-GATE.log | exit 0, suíte inteira, ≥1.669 testes | publish-gate GREEN; `Ran 1707 tests in 1327.969s`, `OK (skipped=1)`, `[exit=0]` | PASS |
| AT-001 | repo temporário com script falso que sai 0, 2 e 10, e args `"a b.txt" c.txt` → AVAL-AT001-004.log | OK/0, REPROVOU/2, NADA A MEDIR/10, com a linha `→`; um arquivo por argumento; roda na raiz | 0, 2 e 10 com RESULTADO e `→`; `arg<a b.txt>` `arg<c.txt>`, n=2; pwd = raiz, mesmo chamado da subpasta `sdd/` (AVAL-AT005.log) | PASS (ver achado 2) |
| AT-002 | comando que sai 1, 7, 127 e `kill -9 $$`; INT e TERM enviados ao slot.sh, só a ele e ao grupo, por Popen com os sinais no padrão → AVAL-AT001-004.log, AVAL-AT002-SINAL.log | exit real ou sinal, INCONCLUSIVO, 3 | "saiu 1/7/127, fora do contrato", "morreu pelo sinal 9 (saiu 137)"; INT e TERM nos 4 cenários: "slot.sh interrompido por sinal", INCONCLUSIVO, exit 3 | PASS |
| AT-003 | valor `""`, chave ausente com comentário na coluna 0, chave achada depois de comentário na coluna 0, sem config | PULADO/11 com o caminho do config, sem rodar nada | os 3 casos de vazio dão `vazio: pulado (<caminho>)`, exit 11; a chave depois do comentário é achada e roda (exit 2) | PASS |
| AT-004 | chave errada, `--feature` no fim, `--base` e `--commit` que não resolvem, aspas YAML abertas, `'` do shell aberta, `| cat`, `echo oi # c`; e `--feature --arvore /tmp`, `--arvore --feature F1` → AVAL-AT001-004.log, AVAL-AT004-BORDAS.log | 64 com a causa e o conserto, sem rodar | todos os casos de cima dão 64 com causa e `→`. **Os 2 últimos rodam o comando e saem 0** | **FAIL** (achado 1) |
| AT-005 | repo com origin/main=C1 e HEAD=C2, 2ª worktree, subpasta, symlink, `--dir`, sem feature, `default_branch` que não existe no remoto, pasta sem git → AVAL-AT005.log | 6 variáveis certas; SLOT_DIR igual em toda worktree, subpasta e symlink; pasta existe; before_ok esvazia só a pasta padrão | MOMENTO, FEATURE, BASE, COMMIT e ARVORE certos, padrões e `--` explícitos; mesmo `sdd-slot-b9d8160a1df5/F1` na raiz, na subpasta, na wt2 e pelo symlink; as marcas somem no before_ok; o `--dir` mantém `preexistente`; ⚠️ SDD_BASE vazio e SDD_COMMIT vazio sem git | PASS |
| AT-006 | `test-baseline.sh --touched` da HEAD contra o de 9d8ac24, com saída falsa: vitest ts/tsx, pytest test_calc e calc_test, unittest `pkg.test_calc`, deno .mjs, .cjs na raiz → AVAL-AT006-007.log | HEAD 2 com `🛑 nova:`; 9d8ac24 0 | HEAD: exit 2 nos 7 casos; 9d8ac24: exit 0 nos 7 (linha de base vermelha confirmada) | PASS |
| AT-007 | os falsos positivos `lib/foo.test.ts` e `test_calc_total` (unittest e pytest), Go, teste alterado direto, `sdd/`, fonte sem teste ao lado; exits 64, 3, 2, PULADO e poda → AVAL-AT006-007.log, AVAL-AT007-EXITS.log, AVAL-AT007-PODA.log | fora do diff com 0; comportamento antigo mantido | HEAD igual a 9d8ac24 em todos: `⚠️ nova, fora do diff` com exit 0; teste alterado dá 2; PULADO 0, uso 64, base inválida 64, saída que não reconhece 3, falha nova 2; o modo completo poda `m.T.test_velho` e o `--touched` não poda | PASS |
| AT-008 | `test_f15_slots_textos.Release` na suíte; sabotagens próprias A6 (item 9 some) e A7 (7b vira bloqueante) derrubam um teste nomeado; leitura dos itens 0a/9, 0b, 6b, 7b, 10, Gates e WAIVABLE no texto → AVAL-SABOTAGENS.log | o texto do AT | todas as cláusulas estão no SKILL.md; A6 derruba `test_0a_roda_os_testes_do_diff_depois_do_verify_gate`; A7 derruba `test_7b_smoke_antes_do_push_nunca_segura` | PASS |
| AT-009 | `test_contrato_build_release` (rótulos, ordem, pergunta única) e `test_f15_slots_textos` na suíte; diff dos testes antigos alterados | mesmos rótulos; a linha Verificações e o exemplo do como-falar atualizados | suíte verde; nos testes antigos só mudaram versões (2.8.1→2.9.0, 2.6.0→2.7.0), a contagem de perguntas (25→26) e a retirada de `smoke.` do proibido da F13, tudo coerente com o DEFINE | PASS |
| AT-010 | o bloco bash da seção 2b extraído da skill e executado como está escrito, com checagem falsa (ok, DROP TABLE→2, slot vazio) → AVAL-AT010.log; sabotagem A8 (linha Checagem some) | log com `$ cmd`, a saída e `[exit=N]` do slot.sh; ordem 2 → 2b → 3; os .sql chegam como argumentos | `[exit=0]`, `[exit=2]` com REPROVOU e "não aplique", `[exit=11]` PULADO; os 2 .sql chegam ao comando; seções na ordem 2, 2b, 3; A8 derruba `test_aplicar_migration_checa_antes_da_previa` | PASS |
| AT-011 | suíte (config, docs EN e PT, cli-conventions, WORKFLOW_CONTRACTS, MANIFEST) e um grep da família de termos de test_f12 sobre os 21 arquivos tocados → AVAL-AT011-TERMOS.log | itens presentes; 0 ocorrências | itens presentes. Ocorrências: aplicar-migration.md 36 (supabase, todas anteriores), test-baseline.sh 5 (`deno`, 1 delas numa linha nova, como nome do runner de teste), MANIFEST 1 (anterior); 0 nos outros arquivos do produto | PASS com ressalva (achado 3) |

Sabotagens refeitas por mim, com mutantes próprios numa cópia por git archive: A1 (exit 7 vira OK), A2 (11 vira 0), A3 (before_ok não esvazia), A4 (sem trap de sinal), A5 (unittest sem âncora), A6, A7 e A8. Cada uma derrubou um teste nomeado (AVAL-SABOTAGENS.log, AVAL-SABOTAGEM-A1.log). Na primeira tentativa, o padrão do A1 não casou com o arquivo; refeito, ele derruba `test_saida_fora_do_contrato_e_inconclusivo (cmd='bash falso.sh 7')`. No AVAL-SABOTAGENS.log, a linha `[exit=0]` é o exit do pipeline com grep; quem prova a queda é a linha `FAILED`.

## ACHADOS

**1. [média · AT-004] Flag sem valor seguida de outra flag: o slot.sh toma a flag seguinte como valor, roda o comando e sai 0.**
Reprodução, num repo temporário com `sdd/config.yaml` igual a `smoke:\n  before_push_cmd: "bash e.sh"` e o e.sh imprimindo as variáveis:
```
bash sdd/bin/slot.sh smoke.before_push_cmd --feature --arvore /tmp
→ FEATURE=[--arvore] … DIR=[…/sdd-slot-…/--arvore] args=[/tmp]   RESULTADO: OK  exit 0
bash sdd/bin/slot.sh smoke.before_push_cmd --arvore --feature F1
→ FEATURE=[] ARVORE=[--feature] … args=[F1]   RESULTADO: OK  exit 0
```
Esperado: 64, "--feature exige um nome", sem rodar nada. Na prática, se a release montar o 6b, 7b ou 10 com `{F}` vazio e sem aspas, `--feature --base origin/main` vira feature "--base", e `origin/main` cai como arquivo do smoke.
Causa: `sdd/bin/slot.sh` só testa `[ -n "${2}" ]`, não testa se `$2` começa com `--`. O teste existente só cobre a flag no fim da linha.
Conserto sugerido: recusar um valor que comece com `--` nas 5 flags e acrescentar esse caso ao `test_slot.Uso`.
Log: AVAL-AT004-BORDAS.log

**2. [baixa · AT-001/AT-004] Um `#` no meio de uma palavra é tratado como comentário do shell, e o comando válido é recusado com 64.**
Reprodução: com o config `smoke:\n  before_push_cmd: "bash e.sh https://app.local/#/pedidos"`, `bash sdd/bin/slot.sh smoke.before_push_cmd` responde `🛑 … tem um comentário (#)`, exit 64. O mesmo acontece com `"echo a#b"`. Pelo `bash -c`, os dois rodam normalmente: o `#` só abre comentário no início de uma palavra.
Causa: o `shlex.split(v, comments=True)` trata `#` como comentário também dentro de uma palavra.
É fail-closed e a mensagem ensina a contornar (pôr entre aspas), mas recusa um comando que o AT-001 mandaria rodar.
Logs: AVAL-AT001-004.log e AVAL-AT004-BORDAS.log

**3. [ressalva · AT-011 / critério de sucesso] O critério pede 0 ocorrências nos arquivos tocados, mas o teste só confere o texto novo.**
Os 36 `supabase` do aplicar-migration.md são anteriores e fazem parte do caminho de migration provado na F3. O `deno` do test-baseline.sh é um dos formatos de saída de teste. Nenhum dos dois é termo de projeto privado.
`tests/test_f15_slots_textos.py` só confere a seção 2b do aplicar-migration.md e filtra `deno` no test-baseline.sh. Ao pé da letra, o DEFINE não fecha ("nenhum arquivo do produto tocado shall casar"); pela intenção, fecha. Recomendo ajustar o texto do DEFINE para "texto novo", não o código.
Reprodução: AVAL-AT011-TERMOS.log

## Observações (não bloqueiam)
- No unittest, um módulo com o mesmo nome em outro pacote conta como do diff. Com `pkg/calc.py` alterado, `FAIL: test_x (outro.test_calc.T)` dá exit 2. É o casamento por segmento que o AT-006 especifica e erra para o lado seguro, mas pode abortar a release por falha alheia (AVAL-AT006-007.log, caso NOTA).
- No passo 10, depois do `git fetch`, `origin/{default_branch}` já é o SHA publicado. Por isso `SDD_BASE` e `SDD_COMMIT` chegam iguais ao smoke depois do deploy. O "antes" só existe pela `SDD_SLOT_DIR`, como os docs dizem. Vale uma frase no adaptation-guide.
- Quando um shell não interativo põe o slot.sh em segundo plano com `&`, o INT chega ignorado e o trap não dispara. É a semântica do bash, não do script; em terminal e via Popen o resultado é 3.
- Critério "Release v2.8.0 com SHA256SUMS conferido": não se verifica nesta fase, porque é da sdd-release.
- Apareceu `sdd/traces/F15_SLOTS.jsonl`, não rastreado, com hora 22:07, antes destas sondas. Não fui eu que gravei.

## Evidência
Gravei só arquivos `sdd/reports/evidence/F15_SLOTS/AVAL-*.log` (1ª linha `$ comando`, saída verbatim): AVAL-VERIFY-GATE, AVAL-AT001-004, AVAL-AT002-SINAL, AVAL-AT004-BORDAS, AVAL-AT005, AVAL-AT006-007, AVAL-AT007-EXITS, AVAL-AT007-PODA, AVAL-AT010, AVAL-AT011-TERMOS, AVAL-SABOTAGENS, AVAL-SABOTAGEM-A1.
As sondas estão em `/private/tmp/claude-501/-Users-robertoduarte-rdd-worktrees-sdd-open-f15-slots/80a83c1b-4077-4625-ba69-e27f11f530a1/scratchpad/p1.sh` a `p10.sh`. Todos os repositórios das sondas foram criados por mktemp, fora do projeto. Não fiz commit, add, stash, checkout nem reset, e não editei código nem documento.
>>>
