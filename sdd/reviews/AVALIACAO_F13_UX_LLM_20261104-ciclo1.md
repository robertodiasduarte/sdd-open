# Avaliação de contexto fresco — F13_UX_LLM, ciclo 1

- **Modo:** veredito · HEAD 59420a9 · base v2.4.0
- **Evidência:** `sdd/reports/evidence/F13_UX_LLM/AVAL1-*.log`

<<<AVALIACAO
VEREDITO: NEEDS_WORK

Avaliado: HEAD 59420a9, base v2.4.0, macOS, bash 3.2, Python 3.9. Nesta máquina não há gawk nem mawk, então os scripts não foram testados com GNU grep ou awk (premissa A-002 do DEFINE). Não rodei a suíte inteira nem o agente real. Os logs estão em `sdd/reports/evidence/F13_UX_LLM/AVAL1-*.log`. Nada do projeto foi editado, e `git status` só lista as pastas fora do commit.

O que sustenta o NEEDS_WORK:
- **AT-013 falha:** `--conteudo <pasta>` conclui LIMPO.
- **AT-021 sem prova no HEAD:** o caminho feliz nunca passou em nenhum log.
- **Gate:** o log verde é do commit anterior.

## Tabela por AT

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| 001 | `contraste.sh` nos 3 pares | 4.54 PASSA · 4.47 REPROVA · 4.50 PASSA, com RESULTADO e → | igual; 1500 pares contra oráculo Decimal, 0 divergências | PASS |
| 002 | `#6c7b67`/`#fff` | 4.49 REPROVA, exit 2 | igual | PASS |
| 003 | `#000 #fff` com .5, 1, 0 | 3.97, 21.00, 1.00 | igual | PASS |
| 004 | `--piso 3` em 3 posições | 4.47 PASSA, exit 0 | igual | PASS |
| 005 | 37 entradas hostis | 64, com causa e correção, sem razão no stdout | igual (ver L10) | PASS |
| 006 | `LC_ALL=pt_BR.UTF-8`; awk confirma `0,5` | resultados iguais | igual; o teste é fraco (L8) | PASS |
| 007 | `--self-test` | 0; 2 nomeando o caso | 28 casos; mutantes geram exit 2 | PASS |
| 008 | caminho inexistente com SDK e com `system:` | DRIFT, exit 2 | igual | PASS |
| 009 | `./prompts/`, `x/prompts/v1`, `//`, `..`, link, nome em qualquer caixa | DRIFT | igual; ressalva em L5 | PASS |
| 010 | 35 variações do slot | 2 com literal; CRLF e comentário fora do valor | igual | PASS |
| 011 | exclusões do AT | LIMPO | igual; ressalva em L3 e L4 | PASS |
| 012 | vazio, comentário, sem chave, sem config | ⚠️ em stdout nos 2 resultados | igual | PASS |
| 013 | tabela de usos errados | 64, nunca LIMPO | **`--conteudo <pasta>` dá LIMPO, exit 0**; terminal, `(`, `[`, grep 2 ok | **FAIL (A2)** |
| 014 | vários arquivos | nomeia todos, 2 | igual | PASS |
| 015 | `--self-test` numa pasta vazia, caminhos relativo e absoluto, TMPDIR em repo | 0, sem resíduo, cobre todo motivo de 64 | 48 casos e sem resíduo, mas não cobre 2 motivos de 64 | PARCIAL (L9) |
| 016 | 45 DESIGNs inline | exit 1, frase v2.5.0 primeiro, aponta o fragmento | igual; ressalva em L7 | PASS |
| 017 | sem a seção; `test_design_lint` | sem mudança | rc=0; módulo OK | PASS |
| 018 | fragmento preenchido; `test_f13_textos` | exit 0; ponteiros | igual | PASS |
| 019 | `test_f13_textos` e leitura do passo 4 | roteador completo | frases presentes; lacunas em A3 e A4 | PASS (por letra) |
| 020 | texto e `ensaio2-sem-skill` | triagem; D2 | sem-skill PASSA; sem-tipo só passa com o conferidor novo (A1) | PASS (por letra) |
| 021 | `controles.sh`, `ensaio2-*`, conferidor | 3 execuções PASSA após o último conserto; 2 controles reprovam | controles rc=1 e rc=1; **feliz REPROVA, sem-skill PASSA, sem-tipo REPROVA nos logs** | **NÃO PROVADO (A1, A5)** |
| 022 | `skill-lint`, `--conversa` | 18 skills, exit 0 | igual; decisões-lint exit 0 | PASS |
| 023-024 | `test_f13_textos`, leitura | bloco único; sem prompts; para se faltar item | igual; ambiguidade em A6 | PASS |
| 025 | parse do exemplo | seções do perfil, LLM e código, orçamento | 53 checagens ok | PASS |
| 026 | `test_f13_textos`, grep | nomeia loop-builder, scan, entradas | igual | PASS |
| 027-028 | checagem do template, `test_f13_textos` | 7 critérios, nota, 2 herdados, 1 MUST por REPROVA | igual | PASS |
| 029 | grep no config e nos 2 guias | slot vazio; `callLLM` só no exemplo | igual | PASS |
| 030 | `init` real novo e existente, `sync --yes`, MANIFEST | presentes, `# meu` preservado, adaptador criado | igual; 12 de 12 arquivos novos no MANIFEST | PASS |
| 031 | links e menções, roadmap, README | abrem; 3 linhas; só sdd-drive | igual | PASS |
| 032 | grep de termos, `test_agnostico`, piso bash | sem achado | igual | PASS |
| 033 | `scripts/check-versions.py --base v2.4.0 --base-obrigatoria` | exit 0 | PASS, 18 skills; testes de versão OK | PASS |
| 034 | `git diff --quiet`; 11 módulos no HEAD | idêntico; suíte verde | diff vazio; módulos OK; **gate inteiro só em a63ed1a** | PARCIAL (A7) |
| Baseline | testes novos sobre v2.4.0 | vermelhos | os 4 módulos rc=1 | PASS |
| Sabotagem | 8 mutantes | teste falha | 7 caem; `LC_ALL` sobrevive (L8) | PASS, com L8 |

## ACHADOS

**A1 — HIGH — AT-021 sem prova no HEAD; o caminho feliz nunca passou**
- Não existe `codex-*.log`.
- `ensaio-feliz` (a63ed1a) e `ensaio2-feliz` (59420a9) terminam em REPROVA.
- `ensaio2-sem-tipo` também termina em REPROVA.
- `amostra/DESIGN_NOTAS.md` e `confere_roteador.py` foram alterados às 13:37:43, depois das execuções.
- Reconferi o transcript de sem-tipo com o conferidor atual e deu PASSA, usando prompts substitutos. O feliz nunca foi reexecutado.
- Se a rodada final já estava prevista para depois deste ciclo, é pendência bloqueante, não defeito de código.
- Reprodução: `tail -4 sdd/reports/evidence/F13_UX_LLM/ensaio2-feliz.log; ls sdd/reports/evidence/F13_UX_LLM | grep '^codex-.*log'`
- Log: `AVAL1-at021-reconfere-transcript.log`.

**A2 — MEDIUM — AT-013: `--conteudo` com pasta conclui LIMPO**
- Também vale para `.`, `/`, `src/` e `novo/`.
- O self-test e `test_pasta` só cobrem o modo em disco.
- `docs/cli-conventions.md` promete 64 para "caminho que não dá para ler".
- Reprodução: `T=$(mktemp -d); cd $T; mkdir src; printf 'soma = 1\n' | bash <repo>/sdd/bin/prompt-drift-scan.sh --conteudo src; echo $?; cd -; rm -rf $T` (imprime LIMPO e 0)
- Log: `AVAL1-drift-hostil.log`.

**A3 — MEDIUM — o contrato do laço não se compila a partir do DESIGN, e o Build não tem rota para a recusa da skill**
1. A skill exige 5 itens. O fragmento não tem campo de Intenção.
2. As linhas `Perfil de risco` e `Ground truth` não são conferidas pelo lint: `Tipo=loop` sem elas dá rc=0.
3. A `sdd-build` manda compilar o contrato em `one-shot` e, em `loop`, diz só "recebe o contrato".
4. Num DESIGN antigo real, a rota "sem Tipo" chega à skill sem esses itens, e ela manda parar. A amostra do AT-021 só tira a coluna Tipo e mantém as 2 linhas, então não exercita esse caminho.
5. O Build não diz o que fazer quando a skill devolve "item faltando" ou "não é laço". Os 2 `ensaio*-feliz` caíram aí, e o agente inventou a pergunta D2 sozinho.

- Reprodução 1: `grep -nE 'Item faltando|item faltando|complete o DESIGN|chamada única' .agents/skills/sdd-build/SKILL.md; echo $?` (imprime 1)
- Reprodução 2: `tail -8 sdd/reports/evidence/F13_UX_LLM/ensaio2-feliz.log`
- Reprodução 3: caso "loop sem Perfil" em `AVAL1-design-lint-hostil.log`.

**A4 — MEDIUM — no modo `briefs` o scan não tem quem o execute**
- O passo 4 manda escanear o conteúdo antes de gravar, "sempre".
- `WORKER_BRIEF.md` regra 2 diz: "Drift detection roda ANTES do despacho, sobre o manifest, no orquestrador — nunca no worker".
- Antes do despacho o conteúdo não existe, e quem grava é o worker. Os sinais de conteúdo (SDK, wrapper) não rodam nessa rota, e a verificação por wave não o manda rodar em disco.
- `test_modo_briefs_nao_ignora_o_roteador` só cobre a regra 3.
- Reprodução: `grep -n prompt-drift-scan sdd/templates/fragments/WORKER_BRIEF.md .agents/skills/sdd-build/references/modos-e-retry.md; echo $?` (imprime 1)

**A5 — MEDIUM — o conferidor do AT-021 aceita execuções que deveria reprovar**
Log: `AVAL1-at021-furos-conferencia.log`. Cada linha abaixo deu `RESULTADO: PASSA`.

| Execução montada | O que o conferidor deixa passar |
|---|---|
| `ls .../sdd-loop-builder/SKILL.md` e `echo prompt-drift-scan.sh --conteudo ...`, prompt de 1 espaço | "leitura" e "scan" são só substring no comando |
| scan com ` exited 64` | o AT-019 manda nunca ignorar 64 |
| scan depois de gravar | o AT-019 manda antes de gravar |
| `M sdd/features/DESIGN_NOTAS.md`, `sdd/reports/qualquer.sh`, `sdd/features/DEFINE_NOVO.md` | o AT-021 diz "no other path outside the report"; o filtro libera `sdd/features`, `sdd/traces` e todo `sdd/reports` |
| `cat prompt-builder loop-builder` no mesmo comando | a ordem usa o índice do comando, e o transcript real lê os 2 num comando só |
| sem-skill com prompt improvisado em `src/agente/` e D2 só na saída de um `cat` | não há `git status` nesse modo, e a marca é buscada nas últimas 80 linhas, não na mensagem final |
| sem-tipo com "Nenhuma triagem foi feita." e DESIGN reescrito | basta a palavra "triagem" |

Além disso, o controle b termina em ` succeeded` sem ` in`, então o parser nunca fecha o comando. Esse controle continuaria reprovando se a checagem passasse a procurar no texto inteiro em vez dos comandos executados.

Como fechar:
- exigir `cat`, `sed` ou `rg` antes do caminho da skill, e comparar posições na string;
- exigir que o comando de scan não feche com exit 64, e que venha antes da gravação do arquivo;
- filtrar `git status` para `src/notas/` e o relatório exato, também em sem-skill;
- buscar a marca D2 depois do último `exec`;
- acrescentar controles com 64, com DESIGN alterado e com a skill citada só em prosa.

**A6 — MEDIUM — o perfil não se decide só pelo risco, ao contrário do que a skill diz**
- A skill e o Princípio 10 dizem "pelo risco dos efeitos, nunca pelo tamanho".
- `lite` e `standard` têm o mesmo risco (reversível) e se separam por "curto" e "vários arquivos". "avaliação offline" está em lite e "juiz ou avaliador" em standard.
- O mesmo processo de notas de versão é `standard` no exemplo da skill e `lite` na execução real do agente.
- Reprodução: `grep -o 'perfil="[a-z-]*"' .agents/skills/sdd-loop-builder/references/exemplo-loop-spec.md sdd/reports/evidence/F13_UX_LLM/ensaio2-sem-tipo.LOOP_SPEC.txt`

**A7 — MEDIUM — o gate verde registrado é de a63ed1a, não do HEAD**
- Durou 1250 s e terminou às 13:46:10, logo começou às 13:25:20. O commit 59420a9 é de 13:32:02 e alterou `sdd-build`, `sdd-loop-builder` e `test_f13_textos.py`.
- No HEAD rodei só 11 módulos, todos OK.
- Reprodução: `head -1 sdd/reports/evidence/F13_UX_LLM/verify-gate-a63ed1a.log; git rev-parse --short HEAD`

**A8 — MEDIUM — `sdd/config.yaml` ilegível vira "slot vazio" e LIMPO**
- O wrapper do projeto fica invisível, com a mensagem errada, contra "nunca conclui LIMPO sem ter lido".
- Reprodução: num projeto com `wrapper_pattern: "systemPrompt:"`, rodar `chmod 000 sdd/config.yaml; printf 'ask({ systemPrompt: `x` })\n' | bash sdd/bin/prompt-drift-scan.sh --conteudo src/a.ts; echo $?` (imprime 0)
- Log: `AVAL1-drift-slot.log`.

**A9 — MEDIUM — formas comuns de prompt literal passam LIMPO, e a documentação não avisa (fora da letra do AT)**
- A documentação só declara o limite do literal na linha seguinte.
- Todos estes deram LIMPO com `--conteudo src/a.py`: `ask(system="You are")`, `{ role: "system", content: "You are" }`, `"system" : "You are"`, `systemPrompt: f"..."`, `client.responses.create(...)`, `model.generateContent(...)`.
- Decisão para o Roberto: ampliar os sinais ou documentar o limite.
- Log: `AVAL1-drift-hostil.log`, seção B.

**LOW**

- **L1 — `PROMPTS PENDENTES` não chega à skill de prompt.** A `sdd-loop-builder` dá o contrato de saída por estágio, mas `sdd-build`, `sdd-integration.md` e o fragmento só mandam passar o bloco da linha e a linha do estágio. Um `Tipo de saída` único serve para todos os estágios. Reprodução: `grep -n 'PROMPTS PENDENTES' .agents/skills/sdd-build/SKILL.md .agents/skills/sdd-prompt-builder/references/sdd-integration.md sdd/templates/fragments/LLM_PROMPTS_DESIGN.md` não acha nada.
- **L2 — O texto não diz que a tabela de estágios vai para `LOOP_SPEC.md`.** Ele diz "A LOOP_SPEC vai para…", o AT-021 exige a tabela nesse arquivo, e o bloco tem 4 partes. Quem gravar só `<LOOP_SPEC>…</LOOP_SPEC>` reprova.
- **L3 — A exclusão de teste vence o sinal de pasta.** `src/prompts/test_plan.txt`, `prompts/a.spec.txt` e `src/test_generator.py` com `messages.create` dão LIMPO. É um conflito entre AT-009 e AT-011 que nunca foi decidido.
- **L4 — "Em qualquer linguagem" é falso.** Script, `docs/llm-in-code.md` e o nome do teste afirmam isso, mas `src/FooTest.java` e `spec/a_spec.rb` dão DRIFT.
- **L5 — Caminhos:** `src/Prompts/a.txt` dá LIMPO, e um link de arquivo `src/link.txt -> ../prompts/a.txt` também.
- **L6 — Slot em formas válidas de YAML:**
  - `prompts: { wrapper_pattern: "x" }` e BOM no início dizem "vazio" e LIMPO;
  - `null`, `~` e `>-` viram expressão literal, dão LIMPO e não avisam;
  - sem git, numa subpasta, o config não é achado, porque a raiz é a pasta atual.
- **L7 — `design-lint.py`:**
  - `## LLM Prompts (v1)`, `## LLM Prompts: 1`, `##  LLM Prompts` e `### LLM Prompts` passam sem conferência;
  - uma 2ª seção `## LLM Prompts` e um campo `—` também passam;
  - destino do inventário fora do manifest passa, e esse prompt nunca seria construído;
  - um Tipo `lop` num DESIGN novo recebe "formato antigo" e "nada no código precisa mudar";
  - com erro de prompt e de manifest juntos, o rumo final só cita o fragmento.
- **L8 — O teste do AT-006 não fiscaliza o que promete.** Sem `export LC_ALL=C`, teste e self-test seguem verdes neste macOS, porque este awk lê `.5` em pt_BR e a saída é inteira. A regra "não pular no job macOS" também não está no teste (`grep -n darwin tests/test_contraste.py` não acha nada). Log: `AVAL1-at006-mutacao-locale.log`.
- **L9 — AT-015:** o self-test não cobre terminal nem grep com exit 2; os 2 mutantes deixam o self-test em rc=0. Os testes em `tests/` pegam. Log: `AVAL1-mutacoes.log`.
- **L10 — `contraste.sh`:**
  - `RGBA(0,0,0,.5)` e `#00000080` não mostram a forma com o 3º valor;
  - `CDPATH=. bash sdd/bin/contraste.sh --self-test` reprova 28 de 28 com exit 127 (falha segura); em `prompt-drift-scan.sh` todos os casos conferidos também saem 127;
  - `--piso 3 --piso 7` usa o último sem avisar.
- **L11 — `codex-roteador.sh` sem `trap`.** Os `exit 64` depois do `cp auth.json` deixariam a credencial em `$BASE`. Vi isso lendo as linhas 9-17, sem executar. Não há sobra agora (`tmp.*/codex-home` deu 0).

## Sem defeito sob ataque

- **`contraste.sh`:** a conta e a validação resistiram, incluindo quebra de linha, `1.`, `0.`, `,` e `%`.
- **Parser do slot:** expressão inválida, CRLF, comentário e aspas simples estão corretos.
- **`GIT_DIR` herdado:** tratado corretamente.
- **Arquivos especiais:** binário, não-UTF-8, FIFO e stdin fechado têm a saída certa.
- **Self-test:** não deixa resíduo e funciona com TMPDIR dentro de repo e em pasta com espaço.
- **Tabela WCAG:** os níveis conferem com a norma.
- **`init` e `sync`:** o `init` não sobrescreve arquivo do usuário, e o `sync` só aplica com `--yes` fora de terminal.
>>>
