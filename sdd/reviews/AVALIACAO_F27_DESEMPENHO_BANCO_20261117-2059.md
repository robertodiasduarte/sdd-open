# AVALIACAO F27_DESEMPENHO_BANCO — ciclo 3 (avaliador de contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador, gravado como veio. 3º ciclo, acima do teto de 2, com o OK do Roberto (2026-11-17).
> Commit avaliado: `a5a5c5e`. Evidência dele em `sdd/reports/evidence/F27_DESEMPENHO_BANCO/AVAL-VEREDITO-C3-*.log`.
> Os achados 1, 2 e 3 foram corrigidos depois, com teste que falha no código avaliado (`AVALIADOR-C3-ANTES.log`).

<<<AVALIACAO
feature: F27_DESEMPENHO_BANCO · modo: veredito · ciclo: 3 · HEAD avaliado: a5a5c5e (cópia `git archive` em scratchpad/c3/head)
veredito: NEEDS_WORK

Resumo: o A1 do ciclo 2 está fechado para a string de conexão em formato URL, e o A2 está fechado para os dois casos citados (apóstrofo dentro de comentário e `'C:\'`). As observações leves também estão resolvidas: `1e10`, `1_000_000`, `0x1F` e `3.5e-2` saem mascarados, `PGPASSWORD=` e `password = '…'` também, e a varredura sem banco grava o `--saida` com `RESULTADO: SEM BANCO`. Sobram três achados novos. Dois são da mesma família de A1 e A2 e reabrem AT-011 e AT-008 por caminhos diferentes: a string de conexão no formato `chave=valor` e o texto entre aspas duplas (ou dentro de comentário aninhado). O terceiro é um aviso do Python que aparece em toda execução do diagnóstico.

Logs gravados, cada um com a 1ª linha `$ comando` e a saída verbatim, sem senha nem nome por extenso: AVAL-VEREDITO-C3-DIAGNOSTICO.log, AVAL-VEREDITO-C3-DIAGNOSTICO-BORDAS.log, AVAL-VEREDITO-C3-VARREDURA.log, AVAL-VEREDITO-C3-MODULOS.log, AVAL-VEREDITO-C3-PACOTE.log.

## Conferência dos achados do ciclo 2

| Item | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| A1.1 | `--coletar --consentimento --saida "postgresql://postgres:<SENHA>@dbhost:5432/postgres"` | 64, 0 chamadas, nada gravado, senha ausente | exit 64, 0 chamadas, nenhum arquivo gravado, senha 0 vezes | PASS |
| A1.2 | `--ler <pasta> --saida "postgres://u:<SENHA>@h/db"` (7 achados) | o mesmo | exit 64, 0 chamadas, nada gravado, senha 0 vezes | PASS |
| A1.3 | `--saida=URL`, URL em `--estatisticas-desde`, `POSTGRES://` em `--ler`, URL como argumento solto | 64 | todas com exit 64, 0 chamadas, senha 0 vezes | PASS |
| A2 | `/* it's hot */ … nome = '<NOME>'` e `dir = 'C:\' and nome = '<NOME>'` | o nome nunca na saída | `/*?*/ where nome = '?'` e `dir = '?' and nome = '?'`; o nome aparece 0 vezes | PASS |
| leves | `1e10`, `1_000_000`, `0x1F`, `3.5e-2`; `/* PGPASSWORD=<SENHA> */`; `-- password = '<SENHA>'`; varredura `--saida` sem banco | mascarado; arquivo com SEM BANCO | tudo vira `?` ou `/*?*/`; o arquivo do `--saida` traz `RESULTADO: SEM BANCO` | PASS |

## Tabela por AT

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | `auth.uid() = user_id` numa política nova, depois `(select auth.uid())`; módulo test_desempenho_varredura | P01 com exit 1; a versão com select não acusa P01 | `⚠️ P01 alta …/002.sql:1` com exit 1; com `(select …)` some o P01; módulo: 41 testes OK | PASS |
| AT-002 | chave estrangeira sem índice, com índice em que ela é a 1ª coluna, com índice composto em que ela é a 2ª | P03, nada, P03 | P03 com exit 1; NADA ACHADO com exit 0; P03 com exit 1 | PASS |
| AT-003 | `--base` com o achado já na base; `--tudo`; base inexistente | linha ℹ️, `(já existia)`, aviso de que tudo conta como novo | `ℹ️ 1 achado(s) que já existiam`, NADA NOVO com exit 0; `--tudo` mostra `(já existia)`; `⚠️ base naoexiste não existe: tudo conta como novo` | PASS |
| AT-004 | dispensa com motivo; motivo de 2 caracteres; id de outra ficha | aceito; aviso de que não vale; aviso de que não vale | `✔ aceito P01 … — tabela de 10 linhas`; com "ok", P01 fica com o aviso; com P02 na dispensa, P01 fica com o aviso | PASS |
| AT-005 | opção desconhecida, fora de git, catálogo inexistente; 7 políticas novas com `--saida` | 64 em 2 linhas; 5 na tela e linha do resto; lista inteira no arquivo | 64 nos três casos; 5 P01 na tela, `… e mais 22 aviso(s): lista inteira em …`; o `--saida` tem os 7 P01 | PASS |
| AT-006 | repositório sem banco; stack sem Supabase com `.sql` que traz `auth.uid()` | 0 e SEM BANCO em 2 linhas; ficha de Supabase não dispara | 0 e SEM BANCO em 2 linhas, também no arquivo do `--saida`; stack `web` dá NADA ACHADO | PASS |
| AT-007 | `supabase` falso: `--coletar` sem consentimento; `--coletar --saida --consentimento`; coleta com consentimento | 64 e 0 chamadas; só a lista fixa de leitura | 64 com 0 chamadas nos dois primeiros; com consentimento, 13 chamadas da lista; módulo: 22 testes OK | PASS |
| AT-008 | índice não usado sem data, com 10 dias e com 45 dias; máscara de literais | só recomenda apagar com 30 dias ou mais; nenhum literal na saída | idade OK; a máscara deixa o nome passar com aspas duplas e com comentário aninhado (ACHADO 2) | FAIL |
| AT-009 | módulos test_desempenho_catalogo, test_f27_textos, test_agnostico, test_skill_lint, test_gerar_starter, test_verify_gate; MANIFEST, lista do starter e catálogo | tudo verde; 17 fichas; skill no pacote | 8, 13, 7, 29, 34 e 27 testes, todos OK; 17 fichas; skill 1.0.0 no MANIFEST e em `scripts/starter/lista.txt` | PASS |
| AT-010 | test_seguranca_varredura; test_bash32; `git diff 2204a14 HEAD -- AGENTS.md.tmpl` | sem regressão; o template muda só pela linha `Des` | 59 e 3 testes OK com `SDD_TEST_BASH=/bin/bash`; o diff do template é uma linha | PASS (Windows só no CI, ver pendências) |
| AT-011 | data `2026-02-30`; string de conexão em URL e em `chave=valor`; texto com ESC, quebra de linha e "IGNORE AS INSTRUCOES…"; pasta da coleta | 64 sem executar; senha nunca na saída; recomendação igual à da entrada limpa; saída bruta fora do projeto | data: 64 com 0 chamadas; URL: 64; `chave=valor` é aceito (ACHADO 1); injeção: as linhas fora do bloco de dado são idênticas às da entrada limpa; a saída bruta vai para `$TMPDIR/sdd-desempenho.*` | FAIL |

## ACHADOS

**ACHADO 1 (AT-011, mesma família de A1).** Uma string de conexão no formato `chave=valor` da libpq, passada como valor de opção, não é recusada. A validação só olha `"://"`, embora a máscara do próprio script (`SENHA_KV`) já trate `password=` como segredo. Reprodução, num repositório git temporário com o `supabase` falso no PATH: `--coletar --consentimento --saida "host=dbhost user=postgres password=$SEG dbname=postgres"` → exit 0, 13 chamadas ao CLI, e o projeto ganha um arquivo com a senha no nome. Variante `--ler <pasta com 7 lints> --saida "host=… password=$SEG …"`: a senha aparece 1 vez na tela. Esperado: exit 64, 0 chamadas, nada gravado, senha ausente.

**ACHADO 2 (AT-008 e AT-011, mesma família de A2).** O leitor de `mascara_sql` não conhece o identificador entre aspas duplas nem o comentário aninhado do Postgres. Casos: `select "it's" from c where nome = '<NOME>'`; `select * from "o'brien" where nome = '<NOME>'`; `select * from c /* a /* x */ it's */ where nome = '<NOME>'`; `select * from c /* a /* x */ <NOME> */ where id = 1`. Esperado: o nome aparece 0 vezes. Observado: 1 vez em cada caso.

**ACHADO 3 (convenção de saída e risco futuro).** A docstring de `mascara_sql` tem a sequência `` `\` `` sem ser string raw. No Python 3.12 ou mais novo, toda execução do diagnóstico imprime `SyntaxWarning: "\`" is an invalid escape sequence` duas vezes no stderr; com `-W error`, o núcleo não compila. A suíte não pega porque roda com o Python 3.9.

## Pendências (não são falha)
- CI do PR nos 3 sistemas (Ubuntu, macOS, Windows com Git Bash): sessão da release; ainda não há PR.
- Verify Gate inteiro: não rodado de novo (o GATE.log verde é do commit 3154276; HEAD a5a5c5e só acrescenta documentos).
- O SHOULD de cenários do modo Define está fora do escopo destas sondas.
- Sem superfície visual.
>>>
