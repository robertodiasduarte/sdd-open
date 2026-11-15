# Ledger da revisão — F22_AVISO_VERSAO

> Uma linha por achado decidido, de todas as rodadas da revisão adversarial do código desta frente. Conferido por
> `bash sdd/bin/ledger-revisao-lint.sh`; lido por `sdd-fluxo.sh loop --ledger` e por `eval-revisores.sh`.
> Critério da coluna `dano`: `sdd/review/CRITERIO_DANO.md`.

Cadeia: claude revisa, `openrouter` (qwen/qwen3.7-plus) audita, sem 2º revisor (`--no-revisor2`) e sem desempate
(`--no-desempate`), como na F16W2. A revisão do DESIGN (2 rodadas, antes do código, com `--paths`) está no Advisor Ledger
do DESIGN e não entra aqui. Rodada 1 do código (diff inteiro `v2.16.1..d1eda3e`, sem `--paths`): saldo da OpenRouter
US$ 5,51 antes; custo US$ 1,5143 (claude 1,4736 por assinatura nominal, qwen 0,0407); o auditor concordou com os 6. O
diff da rodada levou também o `PROMPT_F22.md` não rastreado (o script inclui os arquivos novos não ignorados): para as
rodadas seguintes, ele está no `.git/info/exclude` (local, fora do pacote). Em paralelo, o raio de impacto (8 superfícies)
achou 1 quebra leve (o `alarme.sh` da higiene não conhece o sdd/hooks de outra worktree: comentário corrigido, pendência
registrada) e 5 textos defasados ("apague e rode o init"), corrigidos; fora deste ledger: não são achados da revisão.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | HIGH | REBATIDA_EVIDENCIA | rodada=1 | `git ls-files PROMPT_F22.md` vazio e `git show --stat d1eda3e` sem ele: o arquivo nunca foi commitado; entrou só no diff da revisão, que inclui os não rastreados (`sdd/bin/adversarial-review.sh`, `congelar`, `--intent-to-add`); posto no `.git/info/exclude` | nao | EXTERNAL_REVIEW_20261115-065519 |
| R2 | MED | APLICADA | rodada=1 | teste: `test_versao_nova_sem_instalavel_mudado_regrava_o_registro` · `EM DIA` só com a mesma versão; senão o plano mostra `~ sdd/open-instalado.txt (registro: vA → vB)` e regrava | nao | EXTERNAL_REVIEW_20261115-065519 |
| R3 | MED | APLICADA | rodada=1 | teste: `test_ultimo_instalavel_ausente_nao_derruba_o_upgrade` · `if [ -f ]; then printf; fi` no filtro dos arquivos do projeto | nao | EXTERNAL_REVIEW_20261115-065519 |
| R4 | LOW | APLICADA | rodada=1 | o doctor aponta a skill do pacote (`<pacote>/.agents/skills/<s>/`), que sempre existe, em vez de `sdd/upgrade/<v>/` | nao | EXTERNAL_REVIEW_20261115-065519 |
| R5 | LOW | APLICADA | rodada=1 | teste: `test_falha_ao_por_a_versao_nova_ao_lado_termina_em_erro` · o laço do passo 5 guarda a falha e sai pelo `die` (RESULTADO: ERRO, como retomar) | nao | EXTERNAL_REVIEW_20261115-065519 |
| R6 | LOW | APLICADA | rodada=1 | a pasta de trabalho com mais de 1 dia sai no começo do upgrade seguinte (`find … -mmin +1440`, como o calço do `sdd/bin/lib/python.sh`) | nao | EXTERNAL_REVIEW_20261115-065519 |

Rodada 2 (diff inteiro `v2.16.1..97eb385`, sem `--paths`, sem o `PROMPT_F22.md`): saldo US$ 5,46 antes; custo US$ 2,1781
(claude 2,1406 nominal, qwen 0,0375); o auditor concordou com os 2.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=2 | teste: `test_checkout_com_crlf_nao_vira_edicao` · para os arquivos que não batem com nada, uma 2ª impressão sem o `\r` (`sha256_entrada`) decide; LF tem a mesma impressão nas duas | nao | EXTERNAL_REVIEW_20261115-073246 |
| R2 | LOW | APLICADA | rodada=2 | teste: `test_projeto_sem_registro_compara_com_a_versao_do_pacote` · sem registro, "este pacote está na vK; a versão do projeto não está registrada" | nao | EXTERNAL_REVIEW_20261115-073246 |

Rodada 3 (diff inteiro `v2.16.1..aae54ff`; o raio de impacto das mudanças desde `d1eda3e` foi refeito antes dela, sem
consumidor quebrado): saldo US$ 5,43 antes; custo US$ 2,0118 (claude 1,9732 nominal, qwen 0,0386); o auditor concordou com
os 2. Rodada 3 = teto; aplicar os 2 pedia uma 4ª rodada: decisão do Roberto em 2026-11-15, "Corrigir + 4ª rodada".

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=3 | teste: `test_de_tag_com_pacote_dentro_de_outro_repositorio_e_64` · a forma tag exige o pacote na raiz de um clone (`-ef`, como a `versao_do_pacote`) | nao | EXTERNAL_REVIEW_20261115-074808 |
| R2 | LOW | APLICADA | rodada=3 | teste: `test_doctor_sem_o_sdd_instalado_manda_o_init` · sem `sdd/`, o doctor diz que o SDD Open não está instalado e manda o init | nao | EXTERNAL_REVIEW_20261115-074808 |

Rodada 4, acima do teto (decisão do Roberto, 2026-11-15; diff inteiro `v2.16.1..a68905f`): saldo US$ 5,39 antes; custo
US$ 2,0852 (claude 2,0406 nominal, qwen 0,0446); o auditor concordou com os 2. Verify Gate de `a68905f` VERDE. Corrigir
pedia uma 5ª rodada: decisão do Roberto, "Corrigir + 5ª rodada".

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=4 | teste: `test_consulta_ignora_a_configuracao_global_do_git` · o `ls-remote` roda com `GIT_CONFIG_GLOBAL` vazio e `GIT_CONFIG_NOSYSTEM=1` (sem `insteadOf`, sem helper); o script de `a68905f` seguia o `insteadOf` (rc=10) e o novo não (rc=20) | nao | EXTERNAL_REVIEW_20261115-081159 |
| R2 | LOW | APLICADA | rodada=4 | teste: `test_pacote_mais_velho_que_o_projeto_manda_atualizar_o_pacote` · com o registro acima do pacote, o doctor manda atualizar o pacote, não rodar o upgrade dele | nao | EXTERNAL_REVIEW_20261115-081159 |

Rodada 5, acima do teto (decisão do Roberto; diff inteiro `v2.16.1..0463d8b`): saldo US$ 5,34 antes; custo US$ 2,2738
(claude 2,2316 nominal, qwen 0,0422); o auditor concordou com os 2. Corrigir pedia uma 6ª rodada: decisão do Roberto,
"Corrigir + 6ª rodada" (se a 6ª trouxer só leves, a recomendação é adiá-los).

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=5 | teste: `test_consulta_ignora_a_configuracao_do_repositorio_do_projeto` · o `ls-remote` roda da pasta temporária, com `GIT_CEILING_DIRECTORIES` e `GIT_DIR` fora de qualquer repositório (sem o `.git/config` do projeto) | nao | EXTERNAL_REVIEW_20261115-100754 |
| R2 | LOW | APLICADA | rodada=5 | teste: `test_de_tag_sem_manifest_e_64` · a forma tag confere o `MANIFEST.txt` do pacote montado e sai 64 | nao | EXTERNAL_REVIEW_20261115-100754 |

Rodada 6, acima do teto (decisão do Roberto; diff inteiro `v2.16.1..e57d064`): saldo US$ 5,28 antes; custo US$ 2,3598
(claude 2,3194 nominal, qwen 0,0404); o auditor concordou com os 2 e os subiu a MED. Corrigir o R1 pedia uma 7ª rodada:
decisão do Roberto, "Corrigir + 7ª rodada".

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | APLICADA | rodada=6 | teste: `test_de_com_registro_mais_novo_nao_rebaixa` · com `--de`, a versão do registro que já existe também barra o rebaixamento (64, nada escrito) | nao | EXTERNAL_REVIEW_20261115-103313 |
| R2 | LOW | REBATIDA_EVIDENCIA | rodada=6 | as duas listas pegam o mesmo conjunto: `bin/lib/versao.sh:67` casa `.agents/skills/sdd-*/` e `ux-review-builder/`, e `bin/sdd-open.sh:138-143` (`skills_da_fonte`) lista as pastas `sdd-*/` e `ux-review-builder/` | nao | EXTERNAL_REVIEW_20261115-103313 |

Rodada 7, acima do teto (decisão do Roberto; diff inteiro `v2.16.1..258287d`): saldo US$ 5,24 antes; custo US$ 2,4587
(claude 2,4187 nominal, qwen 0,0400); o auditor confirmou os 2 como leves. Só leves: adiados como pendência da ficha
(a recomendação combinada com o Roberto na rodada 5), sem mudar o código; esta rodada vale para a versão da release.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_ESCOPO | rodada=7 | pendência na ficha: proxy configurado só no git (`http.proxy`) deixa a consulta "não conferida" (ℹ️, nunca bloqueia; `HTTPS_PROXY` no ambiente continua valendo); a troca é ler só `http.proxy` do global sem o resto | nao | EXTERNAL_REVIEW_20261115-105906 |
| R2 | LOW | REBATIDA_ESCOPO | rodada=7 | pendência na ficha: com `autocrlf=true`, a 2ª impressão sem `\r` roda um arquivo por vez (desempenho no Git Bash, não correção); a troca é um lote só por `python3` ou `awk` | nao | EXTERNAL_REVIEW_20261115-105906 |

Rodada 8 (diff inteiro `v2.16.1..074ef5a`, depois do CI do PR #32 vermelho no piso do macOS — o teto da checagem por
voltas de `sleep` levou 7,2 s; conserto em `074ef5a`, decisão do Roberto "Seguir com o conserto"): saldo US$ 5,03 antes;
custo US$ 2,1189 (claude 2,0825 nominal, qwen 0,0364). O auditor concordou com o R1 e discordou do R2. R1 médio: decisão
do Roberto, "Aplicar + 9ª rodada + CI".

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | MED | APLICADA | rodada=8 | teste: `test_editado_que_o_pacote_nao_mudou_nao_e_para_mesclar` · editado por você e igual entre o pacote antigo e o novo vira a classe "seu" (`= N editados por você que o pacote não mudou (nada a mesclar)`), sem `.novo`, fora do PARA MESCLAR | nao | EXTERNAL_REVIEW_20261115-133645 |
| R2 | MED | REBATIDA_EVIDENCIA | rodada=8 | `.github/workflows/release.yml:305`: o `gh release create` já roda com `--target "$GITHUB_SHA"`, que é o que o `gh` pede quando a tag existe só no local; no minor, a tag chega ao remoto pelo push atômico antes do workflow | nao | EXTERNAL_REVIEW_20261115-133645 |

Rodada 9 (diff inteiro `v2.16.1..7ba7eb0`): saldo US$ 4,99 antes; custo US$ 2,0037 (claude 1,9567 nominal, qwen 0,0470);
o auditor manteve os 2 como leves. Só leves: o R1 adiado para a ficha e o R2 rebatido (o mesmo da rodada 6), sem mudar o
código; esta rodada vale para a versão da release.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1 | LOW | REBATIDA_ESCOPO | rodada=9 | pendência na ficha: pacote de versão desconhecida e projeto com registro ⇒ o doctor manda o upgrade, que recusa com 64 dizendo o caminho (baixar pela Release ou rodar do clone) | nao | EXTERNAL_REVIEW_20261115-135049 |
| R2 | LOW | REBATIDA_EVIDENCIA | rodada=9 | o mesmo conjunto: `bin/lib/versao.sh:67` casa `.agents/skills/sdd-*/` e `ux-review-builder/`, e `bin/sdd-open.sh:138-143` (`skills_da_fonte`) lista as pastas `sdd-*/` e `ux-review-builder/` (rebatido também na rodada 6) | nao | EXTERNAL_REVIEW_20261115-135049 |
