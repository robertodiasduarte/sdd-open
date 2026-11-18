# Avaliação de contexto fresco — F13_UX_LLM, ciclo 3 (D4 do Roberto)

- **Modo:** veredito · HEAD 5ddc433 · base v2.4.0
- **Evidência:** `sdd/reports/evidence/F13_UX_LLM/AVAL3-*.log`

<<<AVALIACAO
VEREDITO: NEEDS_WORK

Avaliado: HEAD 5ddc433, base v2.4.0, macOS, bash 3.2, Python 3.9. Rodei tudo por comando. Os logs estão em `sdd/reports/evidence/F13_UX_LLM/AVAL3-*.log`. Não editei código nem documento, `git status` só lista as 5 pastas fora do commit, não há `__pycache__` e a pasta temporária foi apagada.

**O que sustenta o NEEDS_WORK:** 1 MEDIUM reproduzido (M1), regressão do conserto de L4 do ciclo 2 (`32cc42c`). O `prompt-drift-scan.sh` passou a dar LIMPO para `- role: "system"` e `self.system = "x"`, que em `08fbb5b` davam DRIFT. Todo o resto do DEFINE passou ou é LOW.

## Tabela por AT

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| 001 | 3 pares + `#ABC`; 300 pares contra oráculo Decimal externo | 4.54 PASSA · 4.47 REPROVA · 4.50 PASSA, com RESULTADO e → | igual; 0 divergências | PASS |
| 002 | `#6c7b67`/`#ffffff` (exato 4,49999958) | 4.49 REPROVA, exit 2 | igual | PASS |
| 003 | `#000 #fff` com .5, 1, 0 | 3.97 · 21.00 · 1.00 | igual | PASS |
| 004 | `--piso 3` em 3 posições | 4.47 PASSA, exit 0 | igual | PASS |
| 005 | 13 entradas ruins do AT + 12 de borda | 64, causa e correção, stdout vazio | igual; `RGBA(...)` e `#00000080` mostram o 3º valor | PASS |
| 006 | `LC_ALL=pt_BR.UTF-8`, awk confirma `0,5` | mesmos resultados | igual | PASS |
| 007 | `--self-test`; sabotagem com arredondamento | 0; com a sabotagem, 2 nomeando o caso | 30 casos, rc=0; sabotagem rc=2 com 7 casos nomeados | PASS |
| 008 | 4 SDKs, `system` por `:` e `=`, `role`, caminho inexistente; listas YAML e atributo | DRIFT, exit 2 | formas do AT e JSON/JS/Python certos; **`- role: "system"`, `- system: "x"` e `self.system = "x"` dão LIMPO** | **FAIL (M1)** |
| 009 | relativo, absoluto, por link, caixa, `prompts/test_a.txt`, `.md` em `prompts/` | DRIFT | igual, em `--conteudo` e em disco | PASS |
| 010 | slot: 3 literais, identificador, alternativa, comentário, CRLF, link válido, `&llm` | 2 com literal; 0 com identificador | igual | PASS |
| 011 | todas as convenções de teste, `tests/prompts/`, `.md`, nomes longos | LIMPO | igual; L4 do ciclo 2 fechado | PASS |
| 012 | `""`, `""  # c`, `''`, `null`, `~`, sem chave, `{}`, sem arquivo, `config.example.yaml` | ⚠️ em stdout nos 2 resultados | igual | PASS |
| 013 | 14 formas de pasta, slots inválidos, terminal por `script`, grep 2, cat e awk que falham, link, pasta, FIFO, `chmod 000`, `sdd/` sem permissão | 64, nunca LIMPO | todos 64. Minha sonda errou em `a)` (BSD aceita, expressão válida) e no slot `a\\\\`; `a\` sai 64 | PASS |
| 014 | 3 arquivos | nomeia os 2 com sinal, exit 2 | igual | PASS |
| 015 | `--self-test` em pasta vazia, absoluto, relativo, CDPATH, TMPDIR próprio | exit 0, sem resíduo | 83 casos, sem resíduo; 2 motivos só cobertos em `tests/` (L1) | PASS, com L1 |
| 016 | 76 casos de título, coluna, campo, traços, chaves, contagem; depois sonda da coluna `Tipo` corrigida | exit 1, frase primeiro, aponta o fragmento | igual | PASS |
| 017 | títulos que só começam igual, DESIGN sem a seção, DESIGN reais, `test_design_lint` | sem mudança | rc=0 | PASS |
| 018 | fragmento preenchido, `one-shot`, `loop`, CRLF; ponteiros; 5.5 | exit 0; 5.5 proíbe builder | igual | PASS |
| 019 | grep das rotas do passo 4; `test_f13_textos` | rotas presentes | presentes; 40 testes OK | PASS |
| 020 | texto de triagem e de skill ausente; `decisoes-lint --sites` | triagem; D2 à letra | presente; rc=0 | PASS |
| 021 | `controles.sh`, `confere_roteador.py` nos controles, resumo contra os arquivos | conferidor certo; resumo bate | 22 controles certos; as 10 linhas de N2 têm controle ou deixaram de valer por causa do calço; resumo confere | **RISCO ACEITO** |
| 022 | `skill-lint`, `--conversa`, módulos | 18 skills, exit 0, identidade v1.0.0 | igual | PASS |
| 023-024 | texto e `test_f13_textos` | bloco único; para se faltar item | igual | PASS |
| 025 | parse do exemplo | seções do perfil, LLM e código, orçamento | `standard`, 2 LLM + 2 código | PASS |
| 026 | grep nos 2 arquivos | nomeiam loop-builder e scan | igual | PASS |
| 027-028 | linhas do template e da skill | 7 critérios, 2 herdados, 1 MUST por REPROVA | igual | PASS |
| 029 | config e 2 guias | slot vazio; `callLLM` só no exemplo; sem `smoke.` | igual | PASS |
| 030 | `init` novo e existente, `sync`, MANIFEST | presentes, `# meu` preservado, adaptador criado | igual; 12 arquivos novos, todos no MANIFEST | PASS |
| 031 | `test_docs`, links, roadmap | links abrem; só sdd-drive; 3 linhas | igual; 0 links quebrados | PASS |
| 032 | grep de termos, `test_agnostico`, `test_bash32` | sem achado | só autoria e `callLLM` de exemplo; módulos OK | PASS |
| 033 | versões das 4 skills, `check-versions.py`, contagem 20 + 2 | exit 0 | igual | PASS |
| 034 | `git diff --quiet`; log do gate; 13 módulos | idêntico; verde | diff rc=0; gate 1134 testes OK, `[exit=0]`, posterior ao commit; 13 módulos rc=0 | PASS |
| Baseline | testes novos sobre v2.4.0 | vermelhos | 4 módulos rc=1 | PASS |
| Sabotagem | 15 mutantes dos consertos + 1 no contraste | teste falha | 16 de 16 mortos pelo módulo | PASS |

## AT-021: o que conferi

- **`controles.sh`:** rc=0, 22 controles com o resultado esperado (`AVAL3-controles.log`).
- **Resumo contra os arquivos, tudo bate** (`AVAL3-prova-resumo.log`, `AVAL3-prova-resumo2.log`, `AVAL3-prova-diff.log`):
  - `prova-867d6de-feliz.LOOP_SPEC.txt`: `standard`, 2 estágios LLM;
  - `prova-867d6de-sem-tipo`: triagem `loop` no relatório, 2 estágios LLM;
  - `cdb85a9-codex-sem-skill.log`: `RESULTADO: PASSA`, com D2 à letra;
  - `cdb85a9-codex-feliz.log`: REPROVA, parou por faltar provedor e modelo; a amostra mudou às 16:24, depois da execução;
  - `cdb85a9-codex-sem-tipo.log`: `out of credits`;
  - `git diff 867d6de HEAD -- .agents/skills/sdd-build/SKILL.md` vazio, e na `sdd-loop-builder/SKILL.md` só muda a linha de exceção citada.

## Ciclos anteriores e revisão real: conferido por execução

| Nota | Conferido |
|---|---|
| N1 (config ilegível) | Fechado: link quebrado, pasta, FIFO, `chmod 000`, `sdd/` sem permissão e awk que falha saem 64; a reprodução do ciclo 2 dá 64 |
| N2 (conferidor) | Fechado pelo calço e pelos controles |
| L1 do ciclo 2 | Fechado para slot inválido; sobra em L1 abaixo |
| L3 e L4 do ciclo 2 | Formas pedidas certas; **o conserto de L4 trouxe M1** |
| L5, L6, L7, L8, L9 do ciclo 2 | Conferidos: traços, títulos, `prompts: {}`, `&`/`!`, rota "não é laço", "Depois da entrega", regra de perfil |
| Rodadas 1 a 4 (cat, âncora, fronteira do SDK, `.stream`, 1ª tabela, chaves, hífen, 2.5.8, WORKER_BRIEF) | Confirmados por sonda e pelos mutantes |
| Rodada 5 | `--conferir` com `--aceitar-sem-revisor2` dá CONFERE; `loop` PRONTO. Sem esse parâmetro dá NÃO CONFERE, e o log `real-rodada5.log` mostra o comando sem ele (L4) |

## ACHADOS

**M1 — MEDIUM — AT-008: regressão de `32cc42c`; prompt em lista YAML e em atributo conclui LIMPO**

- **Causa:** o conserto de L4 trocou a âncora `(^|[^[:alnum:]_-])`, que ainda é a descrita na Decision 2 do DESIGN, pela lista `INICIO`: início da linha, `{ , ( [` ou `const/let/var`. O traço de item de lista e o ponto de atributo ficaram de fora.
- **Efeito:** um arquivo fora do inventário com um prompt nessas formas é gravado sem a parada do Build, que é a função do script.
- **Por que MEDIUM:**
  - o AT-008 pede DRIFT para "a system `role`" sem restringir a forma;
  - lista de mensagens em YAML e `self.system = "..."` são casos que um usuário real encontra;
  - os limites em `docs/llm-in-code.md` não citam essas formas, e o doc trata YAML como varrido (`system: "linux"` "does fire").
- **Alcance:** JSON, JS, TS e dicionários Python seguem certos. Um SDK na mesma linha também dispara. Nenhum teste cobre essas formas.
- **Reprodução** (raiz do projeto; log `AVAL3-m1-repro-final.log`):
```
/bin/bash -c 'R=$PWD/sdd/bin/prompt-drift-scan.sh; T=$(mktemp -d); git show 08fbb5b:sdd/bin/prompt-drift-scan.sh > $T/antes.sh; cd $T; git init -q .; for c in "  - role: \"system\"" "- system: \"x\"" "self.system = \"x\"" "  - role: system"; do printf "%s\n" "$c" | /bin/bash $R --conteudo config/agente.yaml >/dev/null 2>&1; h=$?; printf "%s\n" "$c" | /bin/bash antes.sh --conteudo config/agente.yaml >/dev/null 2>&1; a=$?; echo "[$c] HEAD=$h 08fbb5b=$a"; done; cd /; rm -rf $T'
```
- **Observado:**
  - `[  - role: "system"] HEAD=0 08fbb5b=2`
  - `[- system: "x"] HEAD=0 08fbb5b=2`
  - `[self.system = "x"] HEAD=0 08fbb5b=2`
  - `[  - role: system] HEAD=0 08fbb5b=0`
- **Em arquivo completo:** `AVAL3-m1-repro.log` mostra o mesmo com um YAML de 5 linhas e uma classe Python, em disco e em `--conteudo`. `AVAL3-drift-regressao.log` tem a comparação com `08fbb5b`, `32cc42c` e `867d6de`.
- **Como fechar:**
  - aceitar `-[[:space:]]+` depois do início da linha e `.` antes da chave em `INICIO`, mantendo `file system:` e `package-ecosystem:` limpos;
  - decidir `role: system` sem aspas, a forma mais comum em YAML, que nunca disparou: ampliar o sinal ou citar no parágrafo de limites dos 2 idiomas;
  - acrescentar casos no self-test e em `tests/`;
  - atualizar a Decision 2.

**LOW (não mudam o veredito)**

- **L1 — AT-015: 2 motivos de saída 64 não têm dente no self-test.** Os mutantes "sem `sdd/` sem permissão" e "rc do awk ignorado" deixam `--self-test` em rc=0; `tests/` os mata. O AT só libera terminal para `tests/`. Log: `AVAL3-mutantes.log`.
- **L2 — Mesma causa de M1, formas mais raras:** `String system = "x";`, `ask system: "x"`, `a = 1; system = "x"` dão LIMPO, e davam 2 em `08fbb5b`. `Role: "system"` (Go) e `obj.role = "system"` também dão LIMPO. Log: `AVAL3-drift-at008-015.log`, seção de sondas.
- **L3 — `design-lint.py`, títulos fora do padrão passam sem conferência:** `## LLM Prompts v2`, `## LLM Prompts do sistema`, `## LLM prompts de produção` dão rc=0. É vizinho de R1 da rodada 5, mas não é o mesmo caso. Log: `AVAL3-lint-titulos.log`.
- **L4 — Evidência:** `real-rodada.sh` grava no log `--conferir <pasta>`, mas executa com `--aceitar-sem-revisor2`. Quem repetir o comando do log recebe NÃO CONFERE. Log: `AVAL3-revisao-rodada5.log`.
- **L5 — DESIGN defasado:** a Decision 2 ainda descreve a âncora antiga, embora o Ledger registre a nova. Log: `AVAL3-doc-limites.log`.

**Fora da contagem, como pedido:** AT-021 como risco aceito, os 3 LOW da rodada 5 e a dispensa do 2º revisor.

## O que não rodei

- `codex` nem a execução real do AT-021; `codex-roteador.sh` também não.
- A suíte inteira: conferi só o log do gate de `5ddc433` e rodei 13 módulos.
- O CI, GNU grep e mawk: esta máquina não os tem e não há rede. A premissa A-002 e os regex novos seguem sem prova em Ubuntu aqui.
- `publish-gate` isolado: consta só do log do gate.
- Tag, Release v2.5.0 e `SHA256SUMS.txt`, que são passos posteriores.
- A receita da seção 8.3 do plano: usei um grep próprio de termos, mais `test_agnostico`.

## Desvios meus nos logs

- `AVAL3-prova-resumo.log` termina em `head -1 <arquivo>`, leitura de arquivo sem pipe, contra a regra do `ev.sh`. Por isso gravei `AVAL3-prova-resumo2.log`, que repete a parte principal. Não há exit de comando que dependa disso.
- A 1ª versão de `AVAL3-testes-modulos.log` e de `AVAL3-at033.log` também terminava em formatador. Regravei as 2, com rc real.
- `AVAL3-at016-032.log` traz uma chamada minha errada de `sdd-decisoes-lint.sh`, sem `--sites`, com rc=64. A chamada certa, rc=0, está em `AVAL3-baseline.log`.
- `AVAL3-baseline.log` termina em `[exit=1]` só por causa do meu `ls` final, que confirma não haver `__pycache__`.
- `AVAL3-at001-007.log`, `AVAL3-drift-at008-015.log` e `AVAL3-drift-regressao.log` citam scripts de sonda da pasta temporária, já apagada. Só `AVAL3-m1-repro-final.log` é repetível do jeito que está.
>>>
