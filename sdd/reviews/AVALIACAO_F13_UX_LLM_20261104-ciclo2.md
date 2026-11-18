# Avaliação de contexto fresco — F13_UX_LLM, ciclo 2

- **Modo:** veredito · HEAD 08fbb5b · base v2.4.0
- **Evidência:** `sdd/reports/evidence/F13_UX_LLM/AVAL2-*.log`

<<<AVALIACAO
VEREDITO: NEEDS_WORK

Avaliado: HEAD 08fbb5b, base v2.4.0, macOS, bash 3.2, Python 3.9. Rodei tudo por comando. Os logs estão em `sdd/reports/evidence/F13_UX_LLM/AVAL2-*.log`, incluindo `AVAL2-stub-*.log`, gerados pelo `codex-roteador.sh` com codex falso e `PREFIXO=AVAL2-stub`. Não editei nada do projeto, e `git status` só lista as 5 pastas fora do commit.

**O que sustenta o NEEDS_WORK:** 2 achados MEDIUM reproduzidos, ambos consertos parciais do ciclo 1.
- **N1:** `sdd/config.yaml` ilegível ainda conclui LIMPO por portas vizinhas à que A8 fechou.
- **N2:** o conferidor do AT-021 aceita o scan que saiu 64 na forma que os transcripts reais usam.

**Deixei de fora, como pedido:**
- a execução real do AT-021 no HEAD (conferi só `confere_roteador.py` e `controles.sh`, mais o `codex-roteador.sh` com codex e HOME falsos, sem credencial real);
- o gate inteiro no commit final (A7);
- a revisão adversarial real.

**Também não rodei:** a suíte inteira (só 11 módulos) e o CI. Esta máquina não tem GNU grep nem GNU awk, então a premissa A-002 segue sem teste aqui.

## Tabela por AT

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| 001 | 3 pares + `#ABC`; 400 pares contra oráculo Decimal | 4.54 PASSA · 4.47 REPROVA · 4.50 PASSA, com RESULTADO e → | igual; 0 divergências | PASS |
| 002 | `#6c7b67`/`#ffffff` | 4.49 REPROVA, exit 2 | igual | PASS |
| 003 | `#000 #fff` com .5, 1, 0 | 3.97 · 21.00 · 1.00 | igual | PASS |
| 004 | `--piso 3` em 3 posições | 4.47 PASSA, exit 0 | igual | PASS |
| 005 | 15 entradas ruins | 64, causa e correção, stdout vazio | igual; `RGBA(...)` e `#00000080` mostram o 3º valor | PASS |
| 006 | `LC_ALL=pt_BR.UTF-8`; awk confirma `0,5` | mesmos resultados; não pula no macOS | igual; `assertNotEqual(sys.platform, "darwin")` na linha 123 do teste | PASS |
| 007 | `--self-test` | exit 0 | 30 casos, rc=0 | PASS |
| 008 | `system=`, `system:`, `role`, 4 SDKs, caminho inexistente | DRIFT, exit 2 | igual nas formas do AT | PASS (L3 e L4) |
| 009 | `prompts/test_a.txt`, `Prompts/`, `src/PROMPTS/a.spec.ts`, absoluto, link, subpasta, `..` | DRIFT | igual | PASS |
| 010 | slot: 3 literais, identificador, alternativa, comentário, CRLF, BOM | 2 com literal; 0 com identificador | igual | PASS |
| 011 | exclusões, `==`, `system_x`, `tests/prompts/` | LIMPO | igual; `"operating system": "linux"` dá DRIFT (L4) | PASS |
| 012 | vazio, comentário, sem chave, sem config | ⚠️ em stdout nos 2 resultados | igual | PASS |
| 013 | pastas (14 formas), `(`, `[`, terminal por `script`, grep 2, `chmod 000` no arquivo | 64, nunca LIMPO | tudo 64; **link quebrado, pasta no lugar do arquivo, FIFO e `sdd/` sem permissão dão LIMPO** | **FAIL (N1)** |
| 014 | 3 arquivos | nomeia os 2 com sinal, exit 2 | igual | PASS |
| 015 | `--self-test` em pasta vazia, relativo, CDPATH, TMPDIR hostil | exit 0, sem resíduo, cobre todo motivo de 64 | 66 casos, sem resíduo; **os casos de slot inválido passam por outro motivo** | PARCIAL (L1) |
| 016 | títulos, campos, loop sem campo, frase e rumo | exit 1, frase primeiro, aponta o fragmento | igual, exceto traços (L5) | PASS, com L5 |
| 017 | sem a seção; `test_design_lint` | sem mudança | rc=0; módulo OK | PASS |
| 018 | fragmento preenchido; amostra | exit 0 | rc=0; ponteiros conferidos pelo módulo | PASS |
| 019 | `test_f13_textos`; mutantes das rotas | roteador e rotas da recusa no texto | os 4 mutantes do passo 4 derrubam o teste | PASS (L7 e L8) |
| 020 | texto, decisões-lint, cópia sem a skill | triagem; D2 à letra | presentes; a cópia sem-skill não tem nenhum `sdd-loop-builder*` | PASS por letra |
| 021 | `controles.sh`, ataque ao conferidor | só passa o que cumpre o AT | 16 de 16 controles certos; **conferidor aceita 5 execuções montadas que deveriam reprovar** | **Execução real fora do ciclo; conferidor FAIL (N2)** |
| 022 | `skill-lint`, `--conversa`, decisões-lint | 18 skills, exit 0 | igual | PASS |
| 023-024 | `test_f13_textos`, rotas | bloco único; para se faltar item | módulo OK | PASS |
| 025 | parse do exemplo | seções do perfil, LLM, código | `standard`, 2 LLM + 2 código | PASS |
| 026 | grep nos 2 arquivos | nomeiam loop-builder e scan | igual | PASS |
| 027-028 | grep no template e na skill, módulo | 7 critérios, nota, 1 MUST por REPROVA | igual | PASS |
| 029 | grep no config e nos 2 guias | slot vazio; `callLLM` só no exemplo | igual | PASS |
| 030 | `init` novo e existente, `sync --yes`, MANIFEST | presentes, `# meu` preservado, adaptador criado | igual; 9 de 9 arquivos novos no MANIFEST | PASS |
| 031 | `test_docs`, grep | links abrem; só sdd-drive; 3 linhas | módulo OK; 3 linhas no roadmap | PASS |
| 032 | grep de termos, `test_agnostico`, piso bash | sem achado | grep rc=1 nos 2 | PASS |
| 033 | `check-versions.py --base v2.4.0 --base-obrigatoria` | exit 0 | rc=0; versões e linha de identidade batem | PASS |
| 034 | `git diff --quiet`; 11 módulos | idêntico; módulos verdes | diff rc=0; módulos OK | PASS na parte rodada; gate fora do ciclo |
| Baseline | testes novos sobre v2.4.0 | vermelhos | 4 módulos rc=1 | PASS |

## Ciclo 1: o que foi mesmo consertado

| # | Veredito do Ledger | Conferido por execução |
|---|---|---|
| A2 | APLICADA | Confirmado: as 14 formas de pasta saem 64 |
| A3 | APLICADA | Confirmado: fragmento e lint exigem os 3 campos, a amostra tem rc=0, os mutantes das rotas caem. Ressalvas em L7 e L8 |
| A4 | APLICADA | Confirmado: a regra 4 do `WORKER_BRIEF` manda varrer na wave, e o mutante cai |
| A5 | APLICADA | **Parcial: N2** |
| A6 | APLICADA | Confirmado: os termos de tamanho saíram e o exemplo cumpre a regra. Lacuna em L9 |
| A8 | APLICADA | **Parcial: N1.** `chmod 000` no arquivo sai 64; as portas vizinhas, não |
| A9 | APLICADA | Confirmado nas formas pedidas. Limites restantes em L3 |
| L1, L2 | APLICADA | Parcial: o texto da própria skill ficou para trás (L8) |
| L3 | APLICADA | Confirmado, a ordem está certa |
| L4 | APLICADA | Confirmado nos 2 idiomas |
| L5 | em parte, link REBATIDO | Motivo se sustenta: `src/link.txt` ainda dá LIMPO, mas nenhum fluxo gera esse caso |
| L6 | em parte, sem git REBATIDO | Motivo se sustenta, está documentado nos 2 idiomas. O conserto trouxe L6 |
| L7 | em parte, 2ª seção e destino REBATIDOS | Destino se sustenta: o fragmento diz "item sem linha… não construído". **Para a 2ª seção, o motivo escrito não fala dela**; risco baixo, aceitável. `### LLM Prompts` estava na lista de L7 e segue rc=0 sem rebate (L5) |
| L8 | em parte, retirada REBATIDA | Motivo se sustenta: sem `LC_ALL` e com pt_BR, a saída fica igual |
| L9 | APLICADA | Grep 2 e terminal confirmados (terminal em `tests/`, por contrato). Lacuna em L1 |
| L10 | em parte, `--piso` repetido REBATIDO | Conserto confirmado, e o rebate é aceitável. O teste de CDPATH não guarda o conserto (L2) |
| L11 | APLICADA | Confirmado com HOME falso: sem `auth.json` sai 64, e não sobra nada na pasta temporária em nenhuma execução |

## ACHADOS

**N1 — MEDIUM — AT-013: `sdd/config.yaml` que não se lê ainda conclui LIMPO, dizendo que o slot está vazio**
- **Causa:** `carregar_slot` só recusa o arquivo quando `[ -f ]` é verdadeiro e `[ -r ]` é falso. Link quebrado, pasta no lugar do arquivo, FIFO e `sdd/` sem permissão caem em "ausente". Um awk que falha em `ler_slot` também vira slot vazio.
- **Efeito:** o wrapper do projeto fica invisível, com a instrução errada de "preencher o slot". Isso contradiz `docs/cli-conventions.md` ("config ilegível… nunca conclui LIMPO sem ter lido").
- **Alcance real:** a porta mais provável é o link quebrado. `sdd/` em 000 só ocorre com o script chamado de fora, porque ele mora em `sdd/bin`. Mantive MEDIUM pela letra do AT-013 e pela severidade de A8; quem conduz pode reavaliar o alcance.
- **Reprodução** (a partir da raiz do projeto; imprime `RESULTADO: LIMPO` e rc=0):
```
R=$PWD/sdd/bin/prompt-drift-scan.sh; T=$(mktemp -d); cd $T; mkdir -p sdd src; ln -s /inexistente/config.yaml sdd/config.yaml; printf 'ask({ systemPrompt: `x` })\n' | bash $R --conteudo src/a.ts; echo $?; cd -; rm -rf $T
```
- **Logs:** `AVAL2-n1-repro.log`; `AVAL2-drift-hostil.log`, seção D.

**N2 — MEDIUM — AT-021: o conferidor aceita execuções que deveria reprovar, na forma dos transcripts reais**
- **Causa:** `confere_roteador.py` só olha o status do comando inteiro. Nos ensaios reais, o scan roda dentro de Python e imprime o código (`ensaio2-feliz.log:2190`, `ensaio-sem-tipo.log:1574`), e o próprio controle válido usa um `for`, cujo status é o da última volta. Assim, o `st != 64` de A5 quase nunca dispara.
- **Por que importa:** a prova final depende deste conferidor, e o AT-019 manda nunca ignorar 64.

| Execução montada, dá `RESULTADO: PASSA` | O que deveria acontecer |
|---|---|
| scan com `; echo rc=$?` e saída `ERRO DE USO` | reprovar: o scan saiu 64 |
| python com `scan exit 64` e comando fechando 0 | reprovar: é a forma real |
| `apply patch` / `patch: completed` antes do scan (formato real de escrita do Codex) | reprovar: gravou antes de varrer; só `>`, `tee`, `write_text` e `.write(` contam como escrita |
| 1 scan, com os outros 2 arquivos só citados em `wc -l` | reprovar: o AT pede scan "for each written file" |
| `grep -- --conteudo sdd/bin/prompt-drift-scan.sh …` | reprovar: não é scan |
| `printf` com o nome do scan | reprovar: não é scan |
| scan com `exited 127` | reprovar: o script nem rodou |
| `echo cat …/SKILL.md` | reprovar: não é leitura |
| `cat …/SKILL.md` com `exited 1` | reprovar: a leitura falhou |
| relatório "A triagem não foi feita; loop ignorado" | reprovar: não há triagem |

- **Menor:** o controle "3 arquivos vazios" cria só 2 arquivos.
- **Como fechar:**
  - guardar a saída de cada comando e reprovar com `ERRO DE USO` ou `scan exit 64`;
  - exigir `bash …prompt-drift-scan.sh` ou a lista `['bash', …]` como chamada, com um scan por arquivo;
  - tratar `patch: completed` como escrita;
  - exigir status 0 na leitura;
  - acrescentar esses controles a `controles.sh`.
- **Reprodução** (montada sobre `base`, `log_ok` e `conf` de `controles.sh`): `log_ok | sed 's#< /tmp/x; done#< /tmp/x; echo rc=$?; done#; s/RESULTADO: LIMPO/RESULTADO: ERRO DE USO/' > z.log; conf feliz "$d" z.log`
- **Logs:** `AVAL2-conferidor-repro.log`, `AVAL2-conferidor-hostil.log`, `AVAL2-ats2.log`.

**LOW**

- **L1 — AT-015: os casos de slot inválido do `--self-test` passam por outro motivo.** Eles usam `src/t.ts`, que não existe em disco, então saem 64 por "caminho inexistente" com qualquer slot. Cinco mutantes deixam o self-test em rc=0: expressão inválida, aspa sem fechar, texto depois da aspa, `>-` e mapa em linha. `tests/` pegou os 2 mutantes de mapa e BOM que rodei; não rodei os outros 3 contra o módulo. Também sobrevivem ao self-test `*Tests.*` e `generate_content`. Conserto: usar `src/r.py`, que existe. Logs: `AVAL2-selftest-vacuo.log`, `AVAL2-selftest-cobertura.log`.
- **L2 — Mutantes que sobrevivem ao módulo de teste** (`AVAL2-mutantes.log`, 4 de 30):
  - `contraste.sh` sem `unset CDPATH`: o teste usa caminho absoluto, e o mutante só cai com caminho relativo, com rc=2 (`AVAL2-cdpath.log`);
  - `role` sem fechar a aspa: `role: "system:admin"` passaria a disparar sem teste;
  - `generate_content` fora da lista;
  - `irreversível` fora da linha `high-risk` nas regras.
- **L3 — Formas de prompt e de role que dão LIMPO, fora dos limites documentados:** `system := "x"`, `system: str = "x"`, `msg['role'] = 'system'`, `"role" => "system"`, `role: :system`, `'system' => 'x'`, `messages.stream`, `system=("x"`. O AT-008 fala em "system role" sem restringir a forma. Conserto: ampliar o sinal ou o parágrafo de limites. Log: `AVAL2-drift-hostil.log`, seção B.
- **L4 — Sinais falsos:**
  - os sinais de SDK não têm fronteira no fim: `messages.createdAt`, `messages.create_index`, `responses.createdAt`, `generateContentHash` e `generate_content_type` dão DRIFT, e fora do inventário o Build para e pergunta;
  - `"operating system": "linux"` e `file system: "ext4"` também dão DRIFT, embora o AT-011 exclua `system` no fim de nome mais longo;
  - no próprio repositório não houve sinal falso: em disco, só `prompt-drift-scan.sh` dispara, pelo nome.
- **L5 — `design-lint.py`:**
  - `–`, `--`, `---`, `` `—` `` e `**—**` num campo obrigatório dão rc=0, contra "a dash counting as empty" no AT-016; a skill do laço ainda devolveria item faltando depois;
  - `### LLM Prompts`, `## LLM prompts`, `## LLM Prompt`, `## 5. LLM Prompts` e `## **LLM Prompts**` passam sem conferência;
  - os blocos valem por posição: com rótulos trocados, um "Prompt 2" `loop` sem os campos dá rc=0, e 2 blocos "Prompt 1" também.
  - Log: `AVAL2-lint-hostil.log`.
- **L6 — Efeito colateral do conserto de L6 do ciclo 1, e formas de YAML restantes:**
  - `prompts: {}` e `prompts: { builder_skill: x }` são YAML válidos e agora saem 64, com a mensagem "wrapper_pattern malformado", e o scan não roda nesse projeto até corrigir;
  - `"wrapper_pattern":`, `"prompts":` e `prompts :` dizem "vazio" e LIMPO;
  - `&a "x"` e `!!str "x"` viram expressão literal, sem aviso;
  - sub-chave aninhada é lida como o slot.
  - Log: `AVAL2-drift-hostil.log`, seção D.
- **L7 — Rota "não é laço" sem destino.** A `sdd-build` manda trocar o `Tipo` e seguir como `one-shot`, mas o destino da linha `loop` é `<pasta>/LOOP_SPEC.md`, então o prompt cairia nesse arquivo. Na rota sem `Tipo`, a coluna nem existe para trocar. Reprodução: `grep -n destino .agents/skills/sdd-build/SKILL.md` só acha a linha 148.
- **L8 — `sdd-loop-builder/SKILL.md`, "Depois da entrega", ficou para trás.** O item 1 diz "grava a LOOP_SPEC", e a `sdd-build` diz que "o bloco inteiro" vai para o arquivo. O item 2 não cita PROMPTS PENDENTES. Quem seguir a skill ao pé da letra reprova no conferidor, por falta da tabela. Reprodução: linhas 111 e 113 da skill em `AVAL2-ats.log`.
- **L9 — Regra de perfil.** Resolve A6, com 2 restos:
  - `lite` exige verificador por código de saída, e `standard` exige 2 ou mais estágios LLM ou modelo juiz, logo 1 estágio LLM com verificador humano não cai em nenhuma linha;
  - a skill ainda diz "nunca pelo tamanho", e a contagem de estágios é uma medida de tamanho, embora a regra 55 a declare.

## Sem defeito sob ataque

- **Ordem de exclusão:** pasta de teste → `prompts` → nome de teste está certa em `--conteudo` e em disco, em subpasta, por link e fora da raiz. `prompts/tests/a.txt` e `src/prompt_spec.txt` dão LIMPO, como o AT-011 manda.
- **Sinais novos sem falso alarme:** `==`, `===`, `!=`, `os.system(`, `system_x`, `role: "system:admin"`.
- **Saída 64 com pasta:** todas as formas, incluindo link, barra final, `novo/` e caminho absoluto.
- **`codex-roteador.sh`:** as 3 cópias estão certas (sem-tipo tira a coluna, sem-skill tira a skill), e a conferência reprova o codex falso.
- **`init` e `sync`:** não sobrescrevem arquivo do usuário.
- **`contraste.sh`:** nenhuma divergência contra o oráculo.
>>>
