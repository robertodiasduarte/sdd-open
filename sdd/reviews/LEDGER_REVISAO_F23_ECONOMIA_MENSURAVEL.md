# Ledger da revisão — F23_ECONOMIA_MENSURAVEL

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial desta frente. Gravado em
> `sdd/reviews/LEDGER_REVISAO_{FEATURE}.md` logo depois de cada rodada (passo 5c da `sdd-build`).
> Conferido por `bash sdd/bin/ledger-revisao-lint.sh`; lido por `bash sdd/bin/sdd-fluxo.sh loop --ledger`
> (as 4 primeiras células) e por `bash sdd/bin/eval-revisores.sh` (todas). Critério da coluna `dano`:
> `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`) e sem desempate
(`--no-desempate`), como na F16W2 e na F22. A revisão do DESIGN (1 rodada, com `--paths`) está no Advisor Ledger do
DESIGN e não entra aqui. Os artefatos SDD não rastreados (ESCOPO, ficha, evidências) ficaram fora do diff por um
`.gitignore` local que ignora a si mesmo; BRAINSTORM, DEFINE e DESIGN entraram, como contexto.

Rodada 1 (diff `origin/main..c32f48d` mais os 3 documentos SDD): claude US$ 1,2148 nominal (assinatura); o auditor
passou do teto de tempo (exit 67) e a rodada ficou sem auditoria. Os 5 achados foram conferidos um a um, e os 5 testes
novos de `AT004NuncaZero` falham no código de `c32f48d` (`evidence/F23_ECONOMIA_MENSURAVEL/REVISAO-R1-R5-VERMELHO.log`).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | APLICADA | rodada=1 | teste: `test_fase_marcada_sem_mensagem_lida_e_n_d` · fase com execução e nenhuma mensagem lida vira n/d com aviso (`marca_nd`), nunca 0.0000 | sim | EXTERNAL_REVIEW_20261115-234206 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_linha_ilegivel_deixa_toda_linha_da_janela_parcial` · registro ilegível deixa toda linha da janela parcial (`+ n/d`); a linha quebrada saiu da fixture principal | sim | EXTERNAL_REVIEW_20261115-234206 |
| R3 | MED | APLICADA | rodada=1 | teste: `test_leitor_que_falha_deixa_toda_linha_da_janela_parcial` · leitor que sai ≠ 0 ou não roda (`OSError`) fica `None` e toda linha da janela ganha n/d | sim | EXTERNAL_REVIEW_20261115-234206 |
| R4 | MED | APLICADA | rodada=1 | teste: `test_docs_sdd_com_caminho_e_outro_separador` · o `adversarial-review.sh:496-500` grava nomes soltos, mas o casamento agora aceita caminho e `,` `;` espaço | nao | EXTERNAL_REVIEW_20261115-234206 |
| R5 | LOW | APLICADA | rodada=1 | teste: `test_raiz_por_link_simbolico_acha_as_sessoes` · `realpath` nos 2 leitores; o agente grava o caminho físico (pastas `-private-tmp-…` em `~/.claude/projects`) | sim | EXTERNAL_REVIEW_20261115-234206 |

Rodada 2 (diff `origin/main..6b3a295` mais os 3 documentos SDD): claude US$ 1,4332 nominal, qwen US$ 0,0304; o auditor
concordou com R1, R2 e R4 e discordou de R3, R5 e R6. Os 4 testes novos caem no código de `6b3a295`
(`evidence/F23_ECONOMIA_MENSURAVEL/REVISAO-RODADA2-VERMELHO.log`).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_custo_incerto_da_revisao_leva_n_d` · `US$ n + $?` soma n e marca n/d (`custo_de` devolve incerto) | sim | EXTERNAL_REVIEW_20261116-004226 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=2 | `sdd/bin/adversarial-review.sh:1012` grava `custo(r)` ou `n/d` para o papel que rodou, nunca `-`; o auditor que falhou na rodada 1 ficou `$?` no META, que já conta n/d | nao | EXTERNAL_REVIEW_20261116-004226 |
| R3 | MED | REBATIDA_EVIDENCIA | rodada=2 | o META da revisão do DESIGN (`EXTERNAL_REVIEW_20261115-233040`) traz `docs_sdd : BRAINSTORM_…, DEFINE_F23_ECONOMIA_MENSURAVEL.md, DESIGN_…`: a revisão com `--feature` cita o DEFINE | nao | EXTERNAL_REVIEW_20261116-004226 |
| R4 | LOW | APLICADA | rodada=2 | teste: `test_sem_marca_e_leitor_que_falha_nao_e_zero` · sem marca e com leitor que falha, `sem fase` sai n/d | sim | EXTERNAL_REVIEW_20261116-004226 |
| R5 | LOW | APLICADA | rodada=2 | o tempo ativo do total conta só as sessões; a nota do relatório e a doc dizem isso; `test_tabela_por_fase_sem_fase_revisao_e_total` (0h07m00s) | nao | EXTERNAL_REVIEW_20261116-004226 |
| R6 | LOW | APLICADA | rodada=2 | teste: `test_total_do_codex_que_volta_atras_nao_some` · total que volta atrás é contagem nova, somada inteira | sim | EXTERNAL_REVIEW_20261116-004226 |

Rodada 3, teto (diff `origin/main..e451071` mais os 3 documentos SDD): claude US$ 1,3814 nominal, qwen US$ 0,0382; o
auditor concordou com R1, R3 e R4, discordou de R2 e trouxe N1. Os 3 testes novos caem no código de `e451071`
(`evidence/F23_ECONOMIA_MENSURAVEL/REVISAO-RODADA3-VERMELHO.log`). Os consertos vieram depois da rodada do teto: uma
4ª rodada é decisão do Roberto.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=3 | teste: `test_pasta_citada_pelo_ledger_e_ausente_e_n_d` · pasta citada pelo ledger e ausente do disco vira n/d com aviso | sim | EXTERNAL_REVIEW_20261116-005125 |
| R2 | LOW | APLICADA | rodada=3 | teste: `test_agente_sem_leitor_deixa_sem_fase_n_d` · nenhuma mensagem lida na janela: `sem fase` também n/d | sim | EXTERNAL_REVIEW_20261116-005125 |
| R3 | LOW | REBATIDA_ESCOPO | rodada=3 | erra para o lado seguro (marca parcial a mais, nunca zero); dar horário ao registro ilegível fica como pendência na ficha | nao | EXTERNAL_REVIEW_20261116-005125 |
| R4 | LOW | APLICADA | rodada=3 | teste: `test_papel_que_rodou_sem_custo_gravado_e_n_d` · papel com engine e custo `-` ou ausente vira n/d (META antigo) | sim | EXTERNAL_REVIEW_20261116-005125 |
| N1 | LOW | REBATIDA_EVIDENCIA | rodada=3 | `CUSTO_RE` (`sdd/bin/custo-feature.sh:72`) não casa `US$ 1.000,00` (dois separadores): `custo_de` devolve None, que conta n/d, e o `Decimal` nunca recebe o texto | nao | EXTERNAL_REVIEW_20261116-005125 |

Rodada 4, acima do teto (decisão do Roberto em 2026-11-16: "Rodar a 4ª rodada"). Uma 1ª tentativa sobre `b494810`
(`EXTERNAL_REVIEW_20261116-072212`) foi interrompida por mim antes de qualquer veredito, porque o CI do Windows mostrou um
teste que não vale lá (`b606eca`); a rodada valendo é sobre `b606eca`: claude US$ 1,7362 nominal; o auditor passou do
teto de tempo (exit 67) de novo, e a rodada ficou sem auditoria. Os 3 achados conferidos um a um; os 3 testes novos caem
no código de `b606eca` (`evidence/F23_ECONOMIA_MENSURAVEL/REVISAO-RODADA4-VERMELHO.log`).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=4 | teste: `test_pasta_citada_sem_meta_legivel_e_n_d` · pasta citada pelo ledger sem META legível conta a execução e vira n/d com aviso | sim | EXTERNAL_REVIEW_20261116-072338 |
| R2 | MED | APLICADA | rodada=4 | teste: `test_modelo_com_quebra_de_linha_no_fim_sai_interrogacao` · `\Z` no lugar de `$` nos padrões (o `$` do Python aceita "nome\n"): modelo, feature, fase, pasta e rodada | sim | EXTERNAL_REVIEW_20261116-072338 |
| R3 | LOW | APLICADA | rodada=4 | teste: `test_ledger_ilegivel_e_n_d_com_aviso` · ledger que existe e não se lê vira n/d com aviso | sim | EXTERNAL_REVIEW_20261116-072338 |

Rodada 5, acima do teto (decisão do Roberto em 2026-11-16: "5ª rodada com o codex auditando"), sobre `ef217b9`: claude
US$ 1,6122 nominal, codex por assinatura; o auditor concordou com os 2 e trouxe N1. Nenhum conserto entrou depois dela:
os 3 ficam como pendência na ficha, porque qualquer mudança pediria uma 6ª rodada e nenhum faz o custo sair zero.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | REBATIDA_ESCOPO | rodada=5 | sessão do Codex com `session_meta` ilegível não diz de que pasta é: atribuí-la ao projeto contaria a de outro; marcá-la `ilegivel` deixaria todo relatório de todo projeto parcial. Pendência na ficha (ex.: aviso global no rodapé) | nao | EXTERNAL_REVIEW_20261116-075121 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=5 | mapa só com features inválidas sai MEDIDO vazio em vez de 64; o mapa é dado do mantenedor e o `Fora da conta` lista cada feature recusada. Pendência na ficha | nao | EXTERNAL_REVIEW_20261116-075121 |
| N1 | LOW | REBATIDA_ESCOPO | rodada=5 | sessões concorrentes no mesmo projeto misturam os turnos e subcontam o tempo ativo (o custo não muda); separar turnos por sessão fica como pendência | nao | EXTERNAL_REVIEW_20261116-075121 |
