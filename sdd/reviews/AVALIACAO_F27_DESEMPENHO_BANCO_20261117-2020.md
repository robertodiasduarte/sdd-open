# AVALIACAO F27_DESEMPENHO_BANCO — ciclo 2 (avaliador de contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador, gravado como veio. Commit avaliado: `e1225ef`. Evidência dele em
> `sdd/reports/evidence/F27_DESEMPENHO_BANCO/AVAL-VEREDITO-C2-*.log`. Os achados A1, A2 e as observações (a), (b), (c)
> foram corrigidos depois, com teste que falha no código avaliado (`AVALIADOR-C2-ANTES.log`).

<<<AVALIACAO
FEATURE: F27_DESEMPENHO_BANCO · modo: veredito · ciclo: 2 · HEAD avaliado: e1225ef (cópia de `git archive HEAD` no scratchpad; o diretório de trabalho só tinha arquivos não rastreados)

## Veredito: NEEDS_WORK

O achado do ciclo 1 está corrigido, e o teste novo derruba o mutante que desfaz o conserto. A varredura (AT-001 a AT-006), o texto e o pacote (AT-009) e a não-regressão (AT-010) passaram por execução. Dois achados novos ferem a letra do AT-011 e do AT-008: uma string de conexão passada como **valor** de uma opção, e o mascaramento de literais, que se desalinha com entradas válidas.

## Achado do ciclo 1 (conferido primeiro)
Rodei a reprodução exata na raiz do projeto, nas formas `{"results":[…]}` e lista solta, cada uma com `table-stats` em lista e em `results`. O resultado foi um único achado `⚠️ — baixa Índice sem uso registrado (inspect db index-stats) (1) — a confirmar: idade das estatísticas desconhecida — não apague…`. O nome `public.ix_velho` aparece só no bloco `dado do banco (não é instrução)`. Nenhuma linha `advisor:`, nenhum achado por tabela, nenhuma recomendação de apagar, exit 0. **Corrigido.**
O mutante que reverte `e_lint` e a guarda `sub in SUBCOMANDOS` faz o teste `test_inspect_em_lista_ou_results_nao_vira_advisor` falhar (2 falhas, uma em cada forma).
Logs: AVAL-VEREDITO-C2-ACHADO-C1.log e AVAL-VEREDITO-C2-MUTANTE.log.

## Tabela por AT

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | v.sh em repositório git temporário: P01 (`auth.uid()`, `auth.jwt()`, `current_setting(` fora de `select`), P08, P10, P13, P16, cada um com o par que não acusa | sai 1 com `⚠️ Pnn grav arq:linha` e o "confira" uma vez por item; o par negativo sai 0 com NADA ACHADO | exatamente isso; com 2 achados P01, o "confira" aparece 1 vez | PASS |
| AT-002 | P03 com `references` em linha e `foreign key (col) references`; índice em outra migration; índice composto com a chave em 2º e em 1º | acusa; não acusa; acusa; não acusa | igual (`P03 media 001.sql:2` e `:3`) | PASS |
| AT-003 | achado da base, `--tudo`, linha deslocada, `drop index` novo, base inexistente, sem origin | `ℹ️ 1 achado(s) que já existiam`, exit 0; `(já existia)`; deslocada não conta; drop gera P03 novo; aviso de base ausente numa linha | igual | PASS |
| AT-004 | dispensa válida, motivo de 2 caracteres, motivo vazio, id errado, dispensa no fim da linha de código | `✔ aceito`; as 3 inválidas mantêm o achado com o aviso; no fim de linha vale só para a linha | igual (a linha 3 é aceita e a 4 continua avisada) | PASS |
| AT-005 | opção desconhecida, catálogo ausente, catálogo ilegível, slot inválido, fora de git, `--saida` sem valor; 8 avisos com `--saida` | 64 com causa e conserto; tela com os 5 mais graves (alta, media; nenhuma baixa) e `… e mais 3`; lista inteira no arquivo | igual: 6 casos saem 64 e nenhum sai 2 em 37 execuções; o "confira" aparece 1 vez por ficha na tela e no arquivo | PASS |
| AT-006 | Python sem banco (`.sql` só em `sdd/` e `.claude/`); `.sql` em `db/` com stack nenhuma; slot `security.stack: supabase` | SEM BANCO em 2 linhas, exit 0; só fichas `todas` (P03 sim, P01 não); com o slot, as de Supabase disparam | igual; a stack vem de `seguranca-varredura.sh --stack` (`slot security.stack`) | PASS |
| AT-007 | `supabase` falso que registra as chamadas: `--coletar` sem consentimento, `--saida --consentimento`, coleta com CLI 2.100.1 e 3.1.0, sem CLI no PATH, SQL de `references/` | 0 chamadas sem consentimento; com ele, só a lista fixa; SQL só de leitura | 0, 0 e 0 chamadas nos três casos sem consentimento; 13 chamadas com `--linked` e 12 com `--remote`, 0 fora da lista; 11 blocos SQL sem verbo de escrita | PASS |
| AT-008 | índice sem uso: sem data, 10, 29, 30 e 45 dias; `unused_index` do advisor; consulta lenta com literais; teto com 7 achados; 6 media + 1 baixa | só ≥30 dias vira "candidato a apagar"; linha de máquina e swap antes; literais trocados por `?`; até 5 achados do mais grave, com o total | idade, ordem, teto e swap OK. **Máscara falha**: `/* it's hot */ … = 'Joana'` vira `… it'?'Joana'`, e `'C:\' and nome = 'Joana'` vira `'?'Joana'`. `1e10`, `1_000_000` e `0x1F` não são mascarados | **FAIL** (A2) |
| AT-011 | datas inválidas (5 formas); string de conexão e `--password` como argumento; senha dentro da saída lida; instrução ao agente; controle e ESC; TMPDIR dentro do projeto; erro do CLI com senha; **string de conexão como valor de `--saida`** | 64 sem executar; `***`; bloco de dado; recomendação igual à da fixture limpa; saída bruta fora do projeto | todo o resto OK (0 senhas, 0 caracteres de controle, a recomendação não muda com a instrução, TMPDIR dentro do projeto recusado). **Mas** `--saida "postgresql://…:<senha>@…"` sai 0, roda 13 chamadas e grava um arquivo dentro do projeto com a senha no caminho; no `--ler` com mais de 5 achados, a senha aparece na tela | **FAIL** (A1) |
| AT-009 | catálogo lido por script; arquivos e modos da skill; `skill-lint.py --conversa` nos 4 SKILL.md; ganchos do define, design (+ template) e release; MANIFEST, lista do starter, READMEs, docs; módulos `test_desempenho_catalogo`, `test_f27_textos`, `test_agnostico`, `test_skill_lint`, `test_gerar_starter` | 17 fichas P01–P17 com os 11 campos na ordem; tudo presente; os lints verdes | 17 fichas na ordem, 12 com padrão, 0 `bloqueia`/`agents`; os 4 lints com exit 0; a release trata `1`/`64`/`127` como CONCERNS, "nunca aborta"; os 5 módulos OK | PASS |
| AT-010 | `git diff 2204a14` em `AGENTS.md.tmpl`, `verify-gate.sh`, `publish-gate.sh`, `seguranca-varredura.sh` e na skill `sdd-seguranca`; `check-versions --base v2.21.0`; módulos `test_seguranca_varredura` e `test_verify_gate` com `SDD_TEST_BASH=/bin/bash` | só a linha `\| Des \|` no template; o resto sem mudança; versões coerentes | igual; check-versions VERDE (23 skills); 59 e 27 testes OK | PASS (a suíte inteira, o bash32 e o Windows ficam com a sessão do build) |

Módulos isolados, um por vez, na cópia de HEAD: diagnóstico 20, varredura 40, catálogo 8, f27_textos 13, seguranca_varredura 59, agnóstico 7, skill_lint 29, gerar_starter 34, verify_gate 27. Todos OK (AVAL-VEREDITO-C2-MODULOS.log).

## ACHADOS

**A1 (média, AT-011): string de conexão passada como valor de uma opção não é recusada.**
- Reprodução, num repositório git temporário fora do projeto, com o `supabase` falso no PATH: `bash <projeto>/sdd/bin/desempenho-diagnostico.sh --coletar --consentimento --saida "postgresql://postgres:<senha>@dbhost:5432/postgres"`
- Observado: exit 0, 13 chamadas ao CLI, e o relatório gravado em `./postgresql:/postgres:<senha>@dbhost:5432/postgres`, dentro do projeto.
- Variante só de leitura, com 7 lints na pasta: `--ler <pasta> --saida "postgres://u:<senha>@h/db"` imprime `… lista inteira em postgres://u:<senha>@h/db`.
- Causa: em `sdd/bin/desempenho-diagnostico.sh:135`, a checagem de `"://"` e de `--db-url`/`--password`/`-p` só olha o token da vez. O valor consumido por `--saida`, `--ler` ou `--fontes` (`i += 2`) nunca passa por ela.
- Conserto sugerido: aplicar a mesma checagem a `args[i+1]`.

**A2 (média, AT-008 e privacidade do dado de terceiros): a máscara de literais se desalinha e expõe o literal seguinte.**
- Reprodução: `long-running-queries.json` = `[{"query":"select * from c /* it's hot */ where nome = 'Joana'","total_exec_time":"9s"}]`, depois `--ler <pasta>`.
- Observado: `│ select * from c /* it'?'Joana'`. O mesmo acontece com `where dir = 'C:\' and nome = 'Joana'`, que sai como `'?'Joana'`.
- Causa: `LITERAL` em `:91` trata `\` como escape em todo literal (só vale em `E'…'`) e não pula comentários `--` e `/* */`. Um apóstrofo dentro de comentário abre um literal falso.
- Conserto sugerido: tirar os comentários antes (ou mascará-los) e tratar `\` só em `E'…'`. Isto pesa no `long-running-queries`, `blocking` e `locks`, que vêm do `pg_stat_activity` com os valores reais.

**Observações de baixa gravidade, que não sustentam o veredito sozinhas:**
- (a) `NUMERO` em `:93` não mascara `1e10`, `1_000_000` nem `0x1F`.
- (b) `SENHA_KV` em `:90` não pega `PGPASSWORD=<senha>`, porque falta fronteira de palavra antes de `PASSWORD`.
- (c) Com SEM BANCO, `--saida` não grava o arquivo, e a release aponta `--saida sdd/reports/evidence/{F}/DESEMPENHO.log`.
- (d) AVAL-VEREDITO-C2-TEXTOS.log traz `skill-lint` VERMELHO porque o avaliador passou a pasta em vez do SKILL.md; o AVAL-VEREDITO-C2-TEXTOS-2.log refaz com o caminho certo e sai verde.

## Pendências (fora deste ciclo, não são falhas)
- Verify Gate inteiro numa cópia de `git archive`, com a suíte completa e a contagem de testes contra `2204a14`.
- CI do PR nos 3 sistemas (bash 3.2, Windows com Git Bash).
- Cenários SHOULD do modo Define (LM-011).

## Evidência gravada (só estes arquivos, em sdd/reports/evidence/F27_DESEMPENHO_BANCO/)
AVAL-VEREDITO-C2-ACHADO-C1.log · AVAL-VEREDITO-C2-VARREDURA.log · AVAL-VEREDITO-C2-SEMBANCO.log · AVAL-VEREDITO-C2-DIAGNOSTICO.log · AVAL-VEREDITO-C2-DIAGNOSTICO-BORDAS.log · AVAL-VEREDITO-C2-TEXTOS.log · AVAL-VEREDITO-C2-TEXTOS-2.log · AVAL-VEREDITO-C2-MODULOS.log · AVAL-VEREDITO-C2-MUTANTE.log
>>>
