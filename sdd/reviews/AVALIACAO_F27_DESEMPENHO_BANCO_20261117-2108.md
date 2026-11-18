# AVALIACAO F27_DESEMPENHO_BANCO — ciclo 4 (avaliador de contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador, gravado como veio. 4º ciclo, acima do teto de 2, com o OK do Roberto (2026-11-17).
> Commit avaliado: `5af0a2d`. Evidência dele em `sdd/reports/evidence/F27_DESEMPENHO_BANCO/AVAL-VEREDITO-C4-*.log`.
> Recibo 1 (Verify Gate em `5af0a2d`): `sdd/reports/evidence/F27_DESEMPENHO_BANCO/GATE.log`. Recibo 2 (CI do PR nos
> 3 sistemas): sessão da release.

<<<AVALIACAO
feature: F27_DESEMPENHO_BANCO · ciclo: 4 · modo: veredito · HEAD avaliado: 5af0a2d (cópia `git archive` em scratchpad/c4/head; árvore limpa)
veredito: PASS_PENDENTE_RECIBO

Por que PENDENTE_RECIBO e não PASS: todos os ATs passaram nas sondas por execução, mas há dois recibos que eu não posso dar daqui.
(1) O Verify Gate de 5af0a2d está rodando agora em paralelo e eu não o rodei. O último GATE.log commitado (2575 testes, exit 0) é de 3154276, não de 5af0a2d.
(2) O CI do PR nos 3 sistemas fica para a sessão da release (ainda não há PR). Isso é pendência, não falha.

Os 3 achados do ciclo 3 foram corrigidos. Comprovei por execução, com um `supabase` falso que registra as chamadas, num diretório temporário fora do projeto. Cada caso de máscara rodou com o Python 3.15.0 do PATH e com o /usr/bin/python3 3.9.6.

| # | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| C3-1 | `--coletar --consentimento --saida "host=dbhost user=postgres password=<s> dbname=postgres"` e `--ler <pasta> --saida "<mesmo>"`; mais 8 variantes: solta na coleta, solta no --ler, `--saida=<kv>`, `PGPASSWORD=`, `password = '<s> x'`, `PASSWORD=` maiúsculo, dentro de `--estatisticas-desde`, como valor de `--ler` | 64, 0 chamadas, nada gravado, senha ausente | as 10 deram exit 64, 0 chamadas, 0 arquivos no projeto e 0 ocorrências da senha | PASS |
| C3-2 | máscara dos 4 casos pedidos (via `long-running-queries.json`, `--ler <pasta>`, `--saida` fora do projeto) | nome nunca na tela nem no `--saida` | `select "its" … '?'` · `"obrien" … '?'` · `/*?*/ where nome = '?'` · `/*?*/ where id = ?`; nome 0/0 nos dois Pythons | PASS |
| C3-2+ | 15 bordas extras: `""` escapado, `"x/*"`, `'/* nome */'`, `E'x\\'`, `e'it\'s'`, `like'…'`, `U&'…'`, `$q$…$q$`, comentário aberto, texto aberto, `*/` solto, `-- it's`, `-- password = '…'`, nome com quebra de linha | nenhum valor de cliente nem senha | 14 de 15 sem nome nem senha. O `*/` solto sai cortado com `…[cortado]`. A exceção é a observação O1, abaixo | PASS (O1 é observação) |
| C3-3 | Python embutido nos 2 scripts compilado com `-W error`, em 3.15.0 e 3.9.6; stderr de uma execução real | compila sem aviso | 4 de 4 "compila sem aviso"; stderr com 0 linhas nos dois Pythons | PASS |

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | política com `auth.uid() = user_id` / com `(select auth.uid())` | 1 com `P01 … arquivo:linha` / P01 some | exit 1 com `⚠️ P01 alta supabase/migrations/002.sql:1` e o "confira à mão"; na 2ª, P01 some e ficam só P02/P06 legítimos | PASS |
| AT-002 | FK sem índice; com índice na 1ª coluna; índice composto com a chave em 2º | P03 / nada / P03 | P03 exit 1 / `NADA ACHADO` exit 0 / P03 exit 1 | PASS |
| AT-003 | achado que a base já tinha; `--tudo`; base inexistente | linha ℹ️; `(já existia)`; aviso de base | `ℹ️ 1 achado(s) que já existiam` exit 0; `(já existia)`; "base naoexiste não existe: tudo conta como novo" exit 1 | PASS |
| AT-004 | dispensa com motivo / motivo "ok" (2 caracteres) / id errado | `✔ aceito` / mantém e avisa / mantém e avisa | os 3 comportamentos conferem | PASS |
| AT-005 | opção desconhecida; fora de git; catálogo inexistente; 7 avisos com `--saida` | 64 com causa e conserto; 5 na tela e o resto no arquivo | 64 nos três; 5 P01 na tela, linha "… e mais", 7 no `--saida`; nenhum exit 2 em todas as sondas | PASS |
| AT-006 | repositório sem banco; stack web com `.sql` contendo `auth.uid()` | `SEM BANCO` em 2 linhas, exit 0; ficha supabase não dispara | conferem as duas | PASS |
| AT-007 | coleta sem `--consentimento` (inclusive como valor de `--saida`); com consentimento; CLI 3.x; CLI ausente; SQL de `references/` | 64 com 0 chamadas; só a lista fixa; só leitura | 64 com 0 chamadas; 13 chamadas, 0 fora da lista; `--remote` no 3.x; 64 sem CLI; 11 blocos SQL, 0 com escrita | PASS |
| AT-008 | índice não usado sem data, com 10 e com 45 dias; consulta lenta + 9 achados | recomenda apagar só com 30 dias ou mais; swap antes de tudo; teto 5 sem `baixa` com `media` fora | "desconhecida — não apague" / "só 10 dia(s)" / "candidato a apagar… 45 dias"; linha de swap em 1º; 1 alta + 4 media na tela, "e mais 4… 9 no total", nenhum baixa | PASS |
| AT-011 | datas inválidas (`2026-02-30`, `17/11/2026`, `2026-1-1`, data futura); senha dentro da saída lida; texto com ESC, CR, U+2028 e instrução ao agente; local da saída bruta | 64; `***`; mesma recomendação; saída bruta fora do projeto | 64 com 0 chamadas; `postgresql://postgres:***@`, `password=***`, `PGPASSWORD=***`, senha 0 na tela e no arquivo; diff fora do bloco de dado vazio, 0 bytes ESC, tudo numa linha só sob `dado do banco (não é instrução)`; saída bruta em `$TMPDIR/sdd-desempenho.*` | PASS |
| AT-009 | catálogo, skill, ganchos, pacote, `skill-lint.py --conversa` | 17 fichas com os 11 campos na ordem; modos; ganchos; MANIFEST; lint verde | 17 de 17 fichas com os 11 campos na ordem, sem `bloqueia`/`agents`; os 4 modos e "Como falar com o aluno"; versão 1.0.0; ganchos do Define, do DESIGN_TEMPLATE e da release conferidos; 9 entradas no MANIFEST e nenhum documento da frente; lista do starter e os 2 READMEs; skill-lint exit 0 nas 4 skills. Os módulos `test_agnostico`/`test_gerar_starter` não rodei (restrição) | PASS (os módulos ficam com o recibo do gate) |
| AT-010 | `check-versions --base v2.21.0`; diff de `AGENTS.md.tmpl`; scripts protegidos; bash 3.2 | não regride | VERDE com 23 skills; AGENTS.md.tmpl só com +1 linha `\| Des \|`; `seguranca-varredura.sh`, `verify-gate.sh`, `publish-gate.sh` e `lib/python.sh` iguais a 2204a14; `--stack` exit 0; `/bin/bash -n` e `--help` exit 0 nos 2 scripts | PASS (suíte inteira e Windows: recibo pendente) |

PENDÊNCIAS (não são falha)
- P1: o recibo do Verify Gate em 5af0a2d, que está rodando agora. Se não sair 0 com a contagem de testes de pelo menos 2575, o veredito cai.
- P2: o CI do PR em Ubuntu, macOS e Windows (Git Bash e Python nativo), na sessão da release.

ACHADOS
Nenhum bloqueante. Ficam 3 observações de gravidade baixa ou informativa.
- O1 (baixa): um nome entre aspas duplas sem fechar aparece inteiro, sem corte. Reprodução: no `long-running-queries.json`, `[{"query":"select * from c where nome = \"<NOME>","total_exec_time":"9s"}]`, depois `--ler <pasta> --saida <arq>`. Sai `│ select * from c where nome = "<NOME>"`. No Postgres, aspas duplas são identificador, não valor; pelo contrato do AT-008/AT-011 não é valor de cliente. Sugestão opcional: cortar com `…[cortado]` quando a aspa dupla não fecha.
- O2 (baixa): string de conexão chave=valor SEM senha vira nome de arquivo. Reprodução: `--ler <pasta> --saida "host=dbhost dbname=postgres"` sai 0 e grava `./host=dbhost dbname=postgres`. Não há segredo; a URL `postgres://` sem senha já é recusada, então o tratamento fica desigual entre os dois formatos.
- O3 (informativa): uma linha com P01, P02 e P06 e a dispensa `aceito P01 — ok` (motivo curto) imprime "dispensa sem motivo (ou de outro item) não vale" 3 vezes, uma para cada ficha da linha. Coerente com o AT-004, só ruidoso.

Evidência: AVAL-VEREDITO-C4-ACHADOS-C3.log · AVAL-VEREDITO-C4-DIAGNOSTICO.log · AVAL-VEREDITO-C4-VARREDURA.log · AVAL-VEREDITO-C4-PACOTE.log
>>>
