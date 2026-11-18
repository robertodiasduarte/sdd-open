# AVALIACAO F27_DESEMPENHO_BANCO — ciclo 1 (avaliador de contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador, gravado como veio. Commit avaliado: `a5cf071`. Evidência dele em
> `sdd/reports/evidence/F27_DESEMPENHO_BANCO/AVAL-VEREDITO-C1-*.log`.

<<<AVALIACAO
**Veredito: NEEDS_WORK** (ciclo 1, F27_DESEMPENHO_BANCO)

**Commit avaliado.** O avaliado foi o `a5cf071`. Durante a avaliação, outra sessão gravou um commit novo na worktree: `4a1c413` → `a5cf071`, que acrescenta o bloco UTF-8 do F16W2 aos dois scripts. Às 20:05, essa mesma sessão também deixou os scripts como `M` por um instante. Por isso rodei de novo todas as sondas da varredura e do diagnóstico numa cópia congelada (`git archive a5cf071`), e são esses os resultados que valem. Os módulos de teste rodaram em `4a1c413` e foram repetidos em `a5cf071` (os 4 da frente e o `test_f16w2_saida`).

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | repositórios sintéticos, um par acusa/não acusa para cada ficha com padrão: P01 (`auth.uid`, `auth.jwt`, `current_setting`), P02, P03, P04, P05, P06, P07, P08, P10, P13, P15 (JS e vetor), P16; P01 em comentário `--`, em `/* */` e entre aspas | exit 1 com `⚠️ Pnn grav arq:linha` e o "confira" uma vez por ficha; o caso negativo sai 0 com `NADA ACHADO` | os 12 pares se comportam como esperado; com dois P01, o "confira" aparece uma vez só | PASS |
| AT-002 | FK na coluna; `foreign key (c) references` via alter; índice na mesma migration, em outra migration, composto com a chave em 2º, composto com a chave em 1º, único; FK composta (a,b) | acusa só quando não há índice com a chave na 1ª coluna | igual ao esperado nos 8 casos | PASS |
| AT-003 | achado que já estava na base; `--tudo`; `drop index` novo; sem `origin`; `--base b0`; `--base` inexistente | não conta o que já existia e mostra `ℹ️ n já existiam`; `(já existia)` com `--tudo`; o novo conta; sem base, avisa numa linha | igual ao esperado | PASS |
| AT-004 | dispensa na linha, dispensa na linha de cima, motivo vazio, motivo com 2 e com 3 caracteres, só espaços, id errado, dispensa no fim de uma linha de código com achado na linha seguinte, dispensa duas linhas acima, `//` em JS | `✔ aceito` só quando é válida; nos outros casos, aviso de que a dispensa não vale; a dispensa no fim da linha vale só para aquela linha | igual ao esperado nos 10 casos | PASS |
| AT-005 | opção desconhecida; `--saida` sem valor; catálogo sem um campo, inexistente e binário; fora do git; `security.stack: cobol`; `--raiz` inexistente; 10 avisos (1 alta, 2 media, 7 baixa); 40 arquivos SQL aleatórios mais binário, CRLF, symlink, arquivo de mais de 1 MB, comentário e `$$` sem fim | 64 com a causa e o conserto; nunca 2; na tela os 5 mais graves; `… e mais k: lista inteira em <arq>`; `--saida` com a lista inteira | 64 em todas as entradas inválidas; 0 saídas `2` em 69 execuções; ordem alta, media, baixa; "confira" 1× por ficha na tela e no arquivo; a linha do resto como esperado | PASS (a mensagem de erro tem 3 linhas, com `RESULTADO:` no meio, como manda a convenção) |
| AT-006 | projeto sem banco; `.sql` só em `sdd/` e em `.agents/`; `.sql` fora deles sem Supabase; slot `security.stack: supabase` | `SEM BANCO` em 2 linhas; fichas de `supabase` não disparam sem a stack; o slot vale mais que a detecção | igual ao esperado; a stack é a mesma do `seguranca-varredura.sh --stack` | PASS |
| AT-007 | `supabase` falso que registra cada chamada: `--coletar` sem consentimento, `--saida --consentimento`, `--ler x --saida --coletar`; com consentimento nas versões 2.100.1, 3.2.0 e 2.50.0 (com o JSON recusado); versão ilegível; sem CLI; SQL de `references/` | 0 chamadas sem consentimento; com ele, só a lista fixa | 0 chamadas em todos os casos sem consentimento; com ele, 13 chamadas, 0 fora da lista (`--linked` na 2.x, `--remote` na 3.x, sem advisors abaixo da 2.81); 11 blocos SQL, 0 verbos de escrita | PASS |
| AT-008 | `--ler` com `unused_index` sem data e com 29, 30 e 400 dias; outliers com literais `'…'`, número, `E'…'` e `$$…$$`; 9 lints; **index-stats do `inspect db` nos formatos `{"rows"}`, `{"results"}` e lista** | idade desconhecida ou curta ⇒ não apagar; linha do swap primeiro; literais trocados por `?`; no máximo 5, do mais grave, com o total | advisor, outliers e o formato `rows`: tudo como esperado. **Nos formatos `results` e lista, as linhas do index-stats viram lints falsos do advisor** (ACHADO 1) | **FALHA** |
| AT-009 | catálogo lido por script; títulos das seções da skill; passo 13 do `sdd-define`; `## Desempenho` no template e na `sdd-design`; item 11 do 0a da `sdd-release`; MANIFEST, lista do starter e README; `skill-lint --conversa` nas 4 skills; módulos `test_desempenho_catalogo`, `test_f27_textos`, `test_agnostico`, `test_skill_lint`, `test_gerar_starter` | tudo presente e os testes verdes | 17 fichas com os 11 campos na ordem, 12 delas com padrão; os 4 modos presentes; 4/4 skills no lint ✅; nenhum documento da frente no MANIFEST; os módulos dão OK | PASS |
| AT-010 | `git diff 2204a14` de `seguranca-varredura.sh`, `verify-gate.sh`, `publish-gate.sh` e `sdd-seguranca`; `AGENTS.md.tmpl`; `verify-gate --checar` com uma linha Desempenho sem valor final e sem a linha Governança; `check-versions --base v2.21.0`; `test_seguranca_varredura`; `test_bash32` | nenhuma mudança fora do previsto; a linha Desempenho não trava | diff vazio; o tmpl ganhou só a linha `\| Des \|`; Desempenho sem valor ⇒ 0, sem Governança ⇒ 5; check-versions VERDE; 59 e 3 testes OK; a release só ganhou CONCERNS, nenhuma causa nova de abortar | PASS (suíte inteira e Windows: ver pendências) |
| AT-011 | data inválida, `2026-1-5` e data futura; `postgresql://…:<senha>@`, `--db-url`, `-p`, `--password`; CLI que falha com a senha no stderr; senha em URL e em `password=`/`PASSWORD='…'`/`pwd="…"` dentro da saída lida; consulta com `\n`, ESC, BEL, U+2028 e instrução ao agente; TMPDIR dentro do projeto | 64 sem executar nada; senha trocada por `***`; texto do banco só no bloco marcado, sem mudar a recomendação; saída bruta fora do projeto | 0 chamadas e 0 ocorrências da senha (montada em tempo de execução); o texto sujo fica numa linha dentro do bloco; diff fora das linhas `│` vazio; TMPDIR dentro ⇒ 64, só `--version` chamado e nada gravado | PASS, com a ressalva do ACHADO 1: no formato `results`/lista, o nome do índice que vem do banco vai para a linha do achado, fora do bloco |

**Critérios de sucesso fora dos AT:**
- **Linha de base vermelha:** confirmada. Os 4 módulos novos sobre `2204a14` dão 54F+1E, 28F, 6E e 29F+4E.
- **Testes isolados:** verdes. Em `4a1c413`, varredura 40, diagnóstico 19, catálogo 8, f27_textos 13, seguranca 59, agnóstico 7, skill_lint 29, gerar_starter 34 e bash32 3. Em `a5cf071`, `test_f16w2_saida` dá 5 OK e os 4 módulos da frente dão OK.
- **Sabotagens:** não rodei de novo; já há evidência em `SABOTAGEM.log` e `AVAL-MUTANTES*.log`.
- **Cenários do modo Define (SHOULD):** não verifiquei.

**ACHADOS**

1. **[AT-008 / AT-011] Linhas do `inspect db` com a coluna `name` são lidas como lints do advisor.** Isso acontece quando vêm em lista solta ou no envelope `{"results": […]}`, que a DESIGN, Decision 10, declara como o formato do `--output-format json` do CLI.

   Reprodução, na raiz do projeto:
   ```
   D=$(mktemp -d); echo '{"results":[{"name":"public.ix_velho","index_scans":0,"unused":true},{"name":"public.ix_bom","index_scans":9000,"unused":false}]}' > $D/index-stats.json
   bash sdd/bin/desempenho-diagnostico.sh --ler $D
   ```
   - **Esperado:** `⚠️ — baixa Índice sem uso registrado (inspect db index-stats) (1) — a confirmar: idade das estatísticas desconhecida — não apague…`, com `public.ix_velho` no bloco `dado do banco`.
   - **Observado:** `⚠️ — baixa advisor: publicix_bom (1) — … abra o link do advisor … (o link está no bloco de dado)` e o mesmo para `publicix_velho`.
   - **O que isso quebra:** o índice **usado** aparece como achado; o aviso de idade das estatísticas some; o passo manda abrir um link que não existe; o nome do índice, texto que veio do banco, sai fora do bloco marcado.
   - **Alcance:** o mesmo vale para `table-stats` em lista, onde cada tabela vira um achado. Com `{"rows": …}` funciona, e é o único formato que o teste cobre (`tests/test_desempenho_diagnostico.py:208`).
   - **Causa:** `lints_de()` (`sdd/bin/desempenho-diagnostico.sh`, ~l.175) trata como lint qualquer dict com a chave `name` dentro de lista, `results` ou `data`, antes de tentar `linhas_de()`.
   - **Conserto sugerido:** decidir pelo nome do arquivo (`advisors*.json` contra `<subcomando>.json`, que a coleta já grava assim) ou por chaves que só o advisor tem (`categories`/`facing`/`remediation`). Acrescentar testes de index-stats e table-stats em lista e em `results`.
   - **Ressalva:** não há CLI real aqui para confirmar a forma exata do JSON (chave em minúscula ou não). O defeito reproduz com o formato que a própria DESIGN diz aceitar.
   - **Prova:** `AVAL-VEREDITO-C1-DIAGNOSTICO.log`, seção d3.

**NAO_VERIFICADO / pendências de recibo**
- **Verify Gate com a suíte inteira:** proibido aqui. O `GATE-1-VERMELHO.log` da outra sessão mostra vermelho em `4a1c413` (`test_f16w2_saida`, 2 falhas). O `a5cf071` corrige isso; neste commit, só o módulo isolado está verde.
- **CI do PR nos 3 sistemas:** não existe PR para `feat/f27-db-performance` (`gh pr list` volta vazio).
- **Superfície visual:** nenhuma; não há roteiro clicável.

**Evidência** (só estes arquivos foram gravados; nenhum código ou documento do projeto foi tocado), em `sdd/reports/evidence/F27_DESEMPENHO_BANCO/`: `AVAL-VEREDITO-C1-VARREDURA.log`, `AVAL-VEREDITO-C1-DIAGNOSTICO.log`, `AVAL-VEREDITO-C1-TEXTOS.log`, `AVAL-VEREDITO-C1-MODULOS.log`, `AVAL-VEREDITO-C1-MODULOS-A5CF071.log`.

Os logs não trazem senha nem e-mail por extenso (conferido com grep).
>>>
