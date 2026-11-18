# Ledger da revisão — F27_DESEMPENHO_BANCO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Revisão do DESIGN: claude revisa, openrouter qwen/qwen3.7-plus audita (diversidade: vendor). A rodada D1 ficou sem
auditor (a chave da OpenRouter não estava no ambiente da sessão); as notas do revisor da D1 eram as mesmas da D2 (R1
da D1 = índice apagado escondido como "já existia", aplicado na Decision 5; as outras repetem R3, R4, R9, R10 da D2 e
o molde de escrita no MCP, tirado da lista) e foram decididas pela D2, com auditor.

sem resultado: rodada=D1 EXTERNAL_REVIEW_20261117-190257 — auditor falhou por credencial (exit 65); revisor sem auditoria
revisor2: dispensado rodada=D2 — sem superfície de risco
revisor2: dispensado rodada=D3 — sem superfície de risco
revisor2: dispensado rodada=1 — sem superfície de risco (regra antiga: 47 arquivos (limiar 8))
revisor2: dispensado rodada=2 — sem superfície de risco (regra antiga: 48 arquivos (limiar 8))
revisor2: dispensado rodada=3 — sem superfície de risco (regra antiga: 48 arquivos (limiar 8))

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=D2 | `sdd/bin/desempenho-diagnostico.sh`: a coleta só roda com `--coletar` e depois da validação de todos os argumentos (consentimento incluído); `--ler` nunca chama o CLI; Pattern 4 do DESIGN corrigido | nao | EXTERNAL_REVIEW_20261117-190814 |
| R2 | MED | APLICADA | rodada=D2 | `CONSULTAS_DIAGNOSTICO.md`: as consultas 3, 7 e 8 trocam os valores por `?` no próprio SQL e cortam em 200 caracteres; nenhum texto cru chega ao agente | nao | EXTERNAL_REVIEW_20261117-190814 |
| R3 | MED | APLICADA | rodada=D2 | `desempenho-diagnostico.sh`: 1º passo é `validar` (data, consentimento, senha) antes de qualquer comando externo | nao | EXTERNAL_REVIEW_20261117-190814 |
| R4 | MED | APLICADA | rodada=D2 | P13 com `(?<![\w.])` no catálogo: `net.http_post(` não casa | nao | EXTERNAL_REVIEW_20261117-190814 |
| R5 | LOW | APLICADA | rodada=D2 | DEFINE 1.3: AT-004 com motivo de 3 ou mais caracteres, como a Decision 1 | nao | EXTERNAL_REVIEW_20261117-190814 |
| R6 | LOW | APLICADA | rodada=D2 | Decision 4: 9 regras e 3 `re:` | nao | EXTERNAL_REVIEW_20261117-190814 |
| R7 | LOW | APLICADA | rodada=D2 | mapa AT → teste com os pares de P02, P05, P08 e P15 | nao | EXTERNAL_REVIEW_20261117-190814 |
| R8 | MED | APLICADA | rodada=D2 | `erro()` do diagnóstico passa a causa pela máscara de senha (URL e `password=`) antes de imprimir | nao | EXTERNAL_REVIEW_20261117-190814 |
| R9 | LOW | APLICADA | rodada=D2 | tag `$…$` com dígito (`$fn1$`) nos dois leitores de SQL da varredura | nao | EXTERNAL_REVIEW_20261117-190814 |
| R10 | LOW | APLICADA | rodada=D2 | máscara cobre URL sem usuário, senha com `@` (até o último) e `password=`/`pwd=` | nao | EXTERNAL_REVIEW_20261117-190814 |
| N1 | MED | APLICADA | rodada=D2 | a coleta confere que a pasta temporária não fica dentro da raiz do projeto e sai 64 se ficar | nao | EXTERNAL_REVIEW_20261117-190814 |
| N2 | MED | APLICADA | rodada=D2 | os 2 scripts trocam o `sys.excepthook`: erro inesperado sai 64 com a causa, nunca 1 nem traceback; o `subprocess` da stack já tratava `OSError` | nao | EXTERNAL_REVIEW_20261117-190814 |
| R1 | MED | APLICADA | rodada=D3 | Decision 7: fora do caso permitido, nunca recomenda apagar | nao | EXTERNAL_REVIEW_20261117-191914 |
| R2 | MED | APLICADA | rodada=D3 | DEFINE 1.4: AT-003 com "achado que a base já tinha" | nao | EXTERNAL_REVIEW_20261117-191914 |
| R3 | MED | APLICADA | rodada=D3 | `CONTROLE` com C1 e U+2028/U+2029 no diagnóstico | nao | EXTERNAL_REVIEW_20261117-191914 |
| R4 | MED | APLICADA | rodada=D3 | lint sem ficha: linha só com o nome; título e link no bloco de dado | nao | EXTERNAL_REVIEW_20261117-191914 |
| R5 | LOW | APLICADA | rodada=D3 | o script já usava `\s*$`; Pattern 1 do DESIGN corrigido | nao | EXTERNAL_REVIEW_20261117-191914 |
| R6 | LOW | APLICADA | rodada=D3 | Decision 4 descreve o comentário de código; `test_padrao_em_comentario_nao_acusa` | nao | EXTERNAL_REVIEW_20261117-191914 |
| R7 | LOW | APLICADA | rodada=D3 | máscara de `E'…'` e `$tag$…$tag$` no diagnóstico | nao | EXTERNAL_REVIEW_20261117-191914 |
| R8 | LOW | APLICADA | rodada=D3 | Architecture Overview e Integration Points sem git diff | nao | EXTERNAL_REVIEW_20261117-191914 |
| R9 | LOW | APLICADA | rodada=D3 | item 15 do File Manifest com os 11 arquivos | nao | EXTERNAL_REVIEW_20261117-191914 |
| R1 | MED | APLICADA | rodada=1 | teste: `Consentimento.test_r1_coletar_como_valor_de_outra_opcao_nao_coleta` (falha no código de antes, `REVISAO-CODIGO-1-ANTES.log`); o modo vem da validação do Python | sim | EXTERNAL_REVIEW_20261117-194631 |
| R2 | MED | APLICADA | rodada=1 | teste: `RevisaoDoCodigo.test_r2_comentario_no_fim_ou_no_meio_da_linha_sql_nao_acusa` (falha no código de antes); padrões `re:` no SQL sem comentário e fora de aspas | nao | EXTERNAL_REVIEW_20261117-194631 |
| R3 | LOW | APLICADA | rodada=1 | `erro()` mascara `passwd=`; `Consentimento.test_versao_ilegivel_ou_tudo_falha` com `passwd=` na causa | nao | EXTERNAL_REVIEW_20261117-194631 |
| R4 | LOW | APLICADA | rodada=1 | `scripts/starter/raiz/README.md`: oito/eight skills complementares | nao | EXTERNAL_REVIEW_20261117-194631 |
| N1 | MED | REBATIDA_EVIDENCIA | rodada=1 | `RevisaoDoCodigo.test_n1_aspas_escapadas_com_parenteses_nao_quebram_a_politica` passa no código de antes: o `''` vira dois textos colados e `fecha_parenteses` (`desempenho-varredura.sh`) os pula | nao | EXTERNAL_REVIEW_20261117-194631 |
| N2 | MED | REBATIDA_EVIDENCIA | rodada=1 | `RevisaoDoCodigo.test_n2_ilike_dentro_de_texto_nao_e_busca` passa no código de antes: dentro de um texto entre aspas o `'` vira `''`, e `ILIKE_SQL` exige `ilike '%`, que ali não aparece | nao | EXTERNAL_REVIEW_20261117-194631 |
| R1 | MED | APLICADA | rodada=2 | teste: `RevisaoDoCodigo2.test_r1_politica_em_tabela_entre_aspas_duplas_acusa` (falha no código de antes, `REVISAO-CODIGO-2-ANTES.log`); `(?![\w$"])` no lugar do `\b` em CREATE/ALTER POLICY | nao | EXTERNAL_REVIEW_20261118-135108 |
| R2 | MED | APLICADA | rodada=2 | teste: `Consultas.test_r2_mascara_do_sql_falha_fechada` (falha no arquivo de antes); consultas 3, 7 e 8 omitem o texto com comentário, `\\`, `$tag$` ou apóstrofo que sobra; prova no Postgres 16: `REVISAO-CODIGO-2-R2-POSTGRES.log` | sim | EXTERNAL_REVIEW_20261118-135108 |
| R3 | MED | APLICADA | rodada=2 | teste: `RevisaoDoCodigo2.test_r3_chave_primaria_por_indice_nao_acusa_p04` (falha no código de antes); `primary key using index` marca a chave | nao | EXTERNAL_REVIEW_20261118-135108 |
| R4 | LOW | APLICADA | rodada=2 | teste: `RevisaoDoCodigo2.test_r4_politica_corrigida_em_migration_seguinte_some` (falha no código de antes); o achado de P01 guarda a política e sai com drop, alter e drop table | nao | EXTERNAL_REVIEW_20261118-135108 |
| R5 | LOW | APLICADA | rodada=2 | teste: `RevisaoDoCodigo2.test_r5_limite_da_consulta_seguinte_nao_esconde_a_lista` (falha no código de antes); a janela de P08 para na próxima `.from(` | nao | EXTERNAL_REVIEW_20261118-135108 |
| R1 | MED | APLICADA | rodada=3 | teste: `test_desempenho_diagnostico.RevisaoDoCodigo3.test_r1_comando_que_falha_aparece_no_relatorio` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); coleta grava `_falhou.txt`; o relatório diz `não lido: <fonte>` e não sai limpo | sim | EXTERNAL_REVIEW_20261118-141043 |
| R2 | MED | APLICADA | rodada=3 | teste: `test_desempenho_diagnostico.RevisaoDoCodigo3.test_r2_json_que_nao_reconheco_nao_vira_nenhum_achado (e test_r2_arquivo_vazio…, test_r2_inspect_com_outro_nome…)` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); JSON não reconhecido, inspect com outro nome, arquivo vazio e os 5 subcomandos sem regra aparecem no relatório; o ✅ só com tudo lido | sim | EXTERNAL_REVIEW_20261118-141043 |
| R3 | MED | APLICADA | rodada=3 | teste: `test_desempenho_diagnostico.RevisaoDoCodigo3.test_r3_indice_unico_ou_de_chave_primaria_nunca_e_candidato` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); index-stats pula `_pkey` e `_key`; o passo de apagar diz que índice único ou de chave primária nunca se apaga | sim | EXTERNAL_REVIEW_20261118-141043 |
| R4 | LOW | APLICADA | rodada=3 | teste: `test_desempenho_varredura.RevisaoDoCodigo3.test_r4_apostrofo_em_comentario_dentro_da_funcao_nao_esconde_o_p13` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); `trechos_entre_aspas` pula identificador entre aspas duplas e comentário dentro do corpo `$$` | nao | EXTERNAL_REVIEW_20261118-141043 |
| R5 | LOW | APLICADA | rodada=3 | teste: `test_desempenho_varredura.RevisaoDoCodigo3.test_r5_o_mesmo_indice_declarado_de_novo_nao_e_repetido` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); P07 não acusa o mesmo nome de índice declarado de novo | nao | EXTERNAL_REVIEW_20261118-141043 |
| R6 | LOW | APLICADA | rodada=3 | teste: `test_f27_textos.Skill.test_modos_e_regras` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); SKILL.md: no modo Define, vale o sentido do DEFINE para a stack | nao | EXTERNAL_REVIEW_20261118-141043 |
| N1 | MED | APLICADA | rodada=3 | teste: `test_desempenho_varredura.RevisaoDoCodigo3.test_n1_palavra_dentro_de_default_nao_vira_chave` (falha no código de antes, `REVISAO-CODIGO-3-ANTES.log`); texto entre aspas da definição de coluna vira espaço antes de procurar references, primary key e unique | nao | EXTERNAL_REVIEW_20261118-141043 |
