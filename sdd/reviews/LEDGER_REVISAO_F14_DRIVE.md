# Ledger da revisão — F14_DRIVE (retroativo)

retroativo: sim

Convertido em 2026-11-10 do ledger de 5 colunas da frente (`sdd/reports/evidence/F14_DRIVE/ledger-review.md`), sem mudar veredito nem
evidência. Acrescentados: a pasta da rodada e a marca `dano`. Regra do retroativo: `sim` = APLICADA cuja evidência cita o teste
do conserto (o efeito sobre dado, dinheiro, acesso, publicação ou disponibilidade **não** foi julgado de novo); `?` = APLICADA
sem teste citado; `nao` = rebatida. Critério: `sdd/review/CRITERIO_DANO.md`.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | HIGH | REBATIDA_EVIDENCIA | rodada=1 | medido sem stub: o gate sem `--strict` sai 3 e o drive para em `gate-inconclusivo` (`r1-repro.log`); o que estava errado era a frase de `docs/cli-conventions.md` e o cabeçalho do `verify-gate.sh`, corrigidos, com teste real em `test_gate_real_sem_a_ferramenta_para_em_inconclusivo` | nao | EXTERNAL_REVIEW_20261105-200215 |
| R2@claude | MED | APLICADA | rodada=1 | `--resume` conta a repetição, e só depois de `bloqueio-humano` zera; o auditor citou a Decision 4, que mudou com isso | ? | EXTERNAL_REVIEW_20261105-200215 |
| R3@claude | MED | APLICADA | rodada=1 | `COMMITAR` na ordem das ações | ? | EXTERNAL_REVIEW_20261105-200215 |
| R4@claude | MED | APLICADA | rodada=1 | a troca aceita grava os campos do bloco que mudaram | ? | EXTERNAL_REVIEW_20261105-200215 |
| R5@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | `sdd-fluxo.sh:81` usa `-ef` e não copia sobre si mesmo; `test_brief_ja_no_destino_para_em_40` | nao | EXTERNAL_REVIEW_20261105-200215 |
| R6@claude | MED | APLICADA | rodada=1 | o script busca o SHA desconhecido no remoto antes do 64 | ? | EXTERNAL_REVIEW_20261105-200215 |
| R7@claude | MED | APLICADA | rodada=1 | o auditor discordou, mas no Windows o sinal 0 é CTRL_C_EVENT; `tasklist` nesse sistema, sem prova em Windows, declarado no relatório | ? | EXTERNAL_REVIEW_20261105-200215 |
| R8@claude | LOW | APLICADA | rodada=1 | anotação com `:` não cria tarefa; o brief fixa ` — ` | ? | EXTERNAL_REVIEW_20261105-200215 |
| R9@claude | LOW | APLICADA | rodada=1 | bloqueio gravado durante o gate segura | ? | EXTERNAL_REVIEW_20261105-200215 |
| R10@claude | LOW | APLICADA | rodada=1 | trava atômica, já com o pid | ? | EXTERNAL_REVIEW_20261105-200215 |
| R11@claude | LOW | APLICADA | rodada=1 | filtro e AT-034 alinhados | ? | EXTERNAL_REVIEW_20261105-200215 |
| R1@openrouter-deepseek-deepseek-v4-pro | MED | REBATIDA_ESCOPO | rodada=1 | `cmd` é uma linha de shell: só rodando se sabe se existe, e isso é `gate-inconclusivo`; AT-002 reescrito para dizer isso | nao | EXTERNAL_REVIEW_20261105-200215 |
| R1 | HIGH | APLICADA | rodada=2 | teste: `test_anotacao_nova_nao_zera_a_repeticao` · na tarefa, a repetição conta a posição, não o texto; anotação nova não zera; `test_anotacao_nova_nao_zera_a_repeticao` e o outro lado | sim | EXTERNAL_REVIEW_20261105-203417 |
| R2 | MED | APLICADA | rodada=2 | `confere_dentro`: link que sai do repositório sai 2, antes de gravar; log não segue link | ? | EXTERNAL_REVIEW_20261105-203417 |
| R3 | MED | APLICADA | rodada=2 | o item 10 diz que roda na pasta da frente | ? | EXTERNAL_REVIEW_20261105-203417 |
| R4 | LOW | APLICADA | rodada=2 | a frase soma, não substitui o detalhe | ? | EXTERNAL_REVIEW_20261105-203417 |
| R5 | LOW | APLICADA | rodada=2 | `--resume` com gate rodando responde ESPERAR e não grava; o auditor discordou olhando só o verificar | ? | EXTERNAL_REVIEW_20261105-203417 |
| R6 | LOW | APLICADA | rodada=2 | DEFINE fora de UTF-8 para em `define-invalido` | ? | EXTERNAL_REVIEW_20261105-203417 |
| N1 | MED | REBATIDA_EVIDENCIA | rodada=2 | `contem` só devolve True ou False com merge-base 0 ou 1, em que o git conhece os 2 commits; qualquer outro código devolve None e espera (`sdd/bin/deploy-do-sha.sh`, `test_commit_que_o_clone_nao_conhece_nunca_decide`) | nao | EXTERNAL_REVIEW_20261105-203417 |
| R1 | MED | APLICADA | rodada=3 | run cancelado espera um deploy mais novo aparecer até `--sem-run`, nos 2 lados | ? | EXTERNAL_REVIEW_20261105-205244 |
| R2 | MED | APLICADA | rodada=3 | marca antes do disparo; só HTTP 4xx é recusa; sem resposta clara, espera e não pede de novo | ? | EXTERNAL_REVIEW_20261105-205244 |
| R3 | LOW | APLICADA | rodada=3 | arquivo de controle (`.gitignore`) fica fora da varredura | ? | EXTERNAL_REVIEW_20261105-205244 |
| R1@claude | LOW | APLICADA | rodada=4 | fetch que falha com SHA desconhecido sai 4 | ? | EXTERNAL_REVIEW_20261106-062106 |
| R2@claude | LOW | APLICADA | rodada=4 | `COMMITAR` manda chamar `proximo`, que leva ao `verificar --fundo` | ? | EXTERNAL_REVIEW_20261106-062106 |
| R3@claude | LOW | APLICADA | rodada=4 | `proximo` que passa limpa a parada resolvida | ? | EXTERNAL_REVIEW_20261106-062106 |
| R4@claude | LOW | APLICADA | rodada=4 | manifest sem linha: `DESIGN` com o motivo do lint, agora com asserção | ? | EXTERNAL_REVIEW_20261106-062106 |
| R5@claude | LOW | APLICADA | rodada=4 | a seção do `--checar` também em PT | ? | EXTERNAL_REVIEW_20261106-062106 |
| R1@codex | HIGH | APLICADA | rodada=4 | teste: `test_duas_chamadas_juntas_repetem_uma_vez` · marca por criação exclusiva: quem perde não dispara (`test_duas_chamadas_juntas_repetem_uma_vez`) | sim | EXTERNAL_REVIEW_20261106-062106 |
| R2@codex | HIGH | APLICADA | rodada=4 | trava de estado curta: leitura, alteração e gravação de um verbo por vez; nunca durante o gate | ? | EXTERNAL_REVIEW_20261106-062106 |
| R3@codex | HIGH | APLICADA | rodada=4 | a limpeza da trava do gate roda dentro da trava de estado | ? | EXTERNAL_REVIEW_20261106-062106 |
| R1@claude | MED | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: repetir sem teto total, no item 10 | nao | EXTERNAL_REVIEW_20261106-072404 |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: marca sobra depois de 401 | nao | EXTERNAL_REVIEW_20261106-072404 |
| R3@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: laço de CPU se a trava abandonada não puder ser apagada | nao | EXTERNAL_REVIEW_20261106-072404 |
| R4@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: documento recente em sem classificação | nao | EXTERNAL_REVIEW_20261106-072404 |
| R1@codex | HIGH | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: trava de estado vence com o dono vivo, só com comando suspenso por mais de 60 s; nada é publicado por isso | nao | EXTERNAL_REVIEW_20261106-072404 |
| R1@claude | LOW | APLICADA | rodada=6 | teste: `test_trava_que_e_link_nao_cria_arquivo_fora` · a trava abre com `O_NOFOLLOW`: link no lugar dela sai 2, sem criar nada fora (`test_trava_que_e_link_nao_cria_arquivo_fora`, cai em `5a1e3fc`) | sim | EXTERNAL_REVIEW_20261107-132826 |
| R2@claude | LOW | APLICADA | rodada=6 | teste: `test_a_frase_que_para_a_repeticao_e_a_do_script` · `test_a_frase_que_para_a_repeticao_e_a_do_script` amarra a frase do item 10 ao `fim(4` do script, e o 4 do redisparo diz outra coisa | sim | EXTERNAL_REVIEW_20261107-132826 |
| R1@codex | MED | APLICADA | rodada=6 | o teste do link pula no Windows, como o outro teste da trava | ? | EXTERNAL_REVIEW_20261107-132826 |
| R1@claude | MED | REBATIDA_EVIDENCIA | rodada=7 | `ficha_do_nome` devolve a própria chave de `abertas`, e `arquivo_da_ficha` tem as mesmas chaves; medido com ficha e documento em caixas diferentes, inclusive slice: sem traceback e com a ficha certa (`r7-repro-claude.log`) | nao | EXTERNAL_REVIEW_20261107-133717 |
| N1 | MED | REBATIDA_EVIDENCIA | rodada=7 | `desmarcar()` não levanta: o `os.remove` está em `except OSError`, e `marca()` usa `git()`, que devolve None em OSError e timeout (`sdd/bin/deploy-do-sha.sh:173-216`) | nao | EXTERNAL_REVIEW_20261107-133717 |
| R1@codex | MED | REBATIDA_ESCOPO | rodada=7 | decisão D4 do Roberto, 2026-11-07: publicar `3d69536` como está; só no Windows nativo (sem `O_NOFOLLOW`) um link no lugar da trava cria arquivo vazio fora do repositório; o drive não tem prova em Windows (BUILD_REPORT); pendência da próxima frente | nao | EXTERNAL_REVIEW_20261107-133717 |

<!-- 41 linhas: 4 sim, 25 ?, 12 nao -->
