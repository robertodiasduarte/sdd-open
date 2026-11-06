# Ledger da revisão adversarial real — F14_DRIVE

Revisor claude, 2º revisor `openrouter:deepseek/deepseek-v4-pro` (decisão do Roberto no brainstorm: Codex sem créditos), auditor `openrouter:qwen/qwen3.7-plus`. Nas rodadas 2 e 3, o DeepSeek caiu com HTTP 402: o saldo da conta acabou (US$ 29,93 de US$ 30, medido). Rodada 4 por decisão D4 do Roberto, 2026-11-05, com o Codex de volta como 2º revisor.

| id | severidade | veredito | rodada | motivo |
|---|---|---|---|---|
| R1@claude | HIGH | REBATIDA_EVIDENCIA | rodada=1 | medido sem stub: o gate sem `--strict` sai 3 e o drive para em `gate-inconclusivo` (`r1-repro.log`); o que estava errado era a frase de `docs/cli-conventions.md` e o cabeçalho do `verify-gate.sh`, corrigidos, com teste real em `test_gate_real_sem_a_ferramenta_para_em_inconclusivo` |
| R2@claude | MED | APLICADA | rodada=1 | `--resume` conta a repetição, e só depois de `bloqueio-humano` zera; o auditor citou a Decision 4, que mudou com isso |
| R3@claude | MED | APLICADA | rodada=1 | `COMMITAR` na ordem das ações |
| R4@claude | MED | APLICADA | rodada=1 | a troca aceita grava os campos do bloco que mudaram |
| R5@claude | MED | REBATIDA_EVIDENCIA | rodada=1 | `sdd-fluxo.sh:81` usa `-ef` e não copia sobre si mesmo; `test_brief_ja_no_destino_para_em_40` |
| R6@claude | MED | APLICADA | rodada=1 | o script busca o SHA desconhecido no remoto antes do 64 |
| R7@claude | MED | APLICADA | rodada=1 | o auditor discordou, mas no Windows o sinal 0 é CTRL_C_EVENT; `tasklist` nesse sistema, sem prova em Windows, declarado no relatório |
| R8@claude | LOW | APLICADA | rodada=1 | anotação com `:` não cria tarefa; o brief fixa ` — ` |
| R9@claude | LOW | APLICADA | rodada=1 | bloqueio gravado durante o gate segura |
| R10@claude | LOW | APLICADA | rodada=1 | trava atômica, já com o pid |
| R11@claude | LOW | APLICADA | rodada=1 | filtro e AT-034 alinhados |
| R1@openrouter-deepseek-deepseek-v4-pro | MED | REBATIDA_ESCOPO | rodada=1 | `cmd` é uma linha de shell: só rodando se sabe se existe, e isso é `gate-inconclusivo`; AT-002 reescrito para dizer isso |
| R1 | HIGH | APLICADA | rodada=2 | na tarefa, a repetição conta a posição, não o texto; anotação nova não zera; `test_anotacao_nova_nao_zera_a_repeticao` e o outro lado |
| R2 | MED | APLICADA | rodada=2 | `confere_dentro`: link que sai do repositório sai 2, antes de gravar; log não segue link |
| R3 | MED | APLICADA | rodada=2 | o item 10 diz que roda na pasta da frente |
| R4 | LOW | APLICADA | rodada=2 | a frase soma, não substitui o detalhe |
| R5 | LOW | APLICADA | rodada=2 | `--resume` com gate rodando responde ESPERAR e não grava; o auditor discordou olhando só o verificar |
| R6 | LOW | APLICADA | rodada=2 | DEFINE fora de UTF-8 para em `define-invalido` |
| N1 | MED | REBATIDA_EVIDENCIA | rodada=2 | `contem` só devolve True ou False com merge-base 0 ou 1, em que o git conhece os 2 commits; qualquer outro código devolve None e espera (`sdd/bin/deploy-do-sha.sh`, `test_commit_que_o_clone_nao_conhece_nunca_decide`) |
| R1 | MED | APLICADA | rodada=3 | run cancelado espera um deploy mais novo aparecer até `--sem-run`, nos 2 lados |
| R2 | MED | APLICADA | rodada=3 | marca antes do disparo; só HTTP 4xx é recusa; sem resposta clara, espera e não pede de novo |
| R3 | LOW | APLICADA | rodada=3 | arquivo de controle (`.gitignore`) fica fora da varredura |
| R1@claude | LOW | APLICADA | rodada=4 | fetch que falha com SHA desconhecido sai 4 |
| R2@claude | LOW | APLICADA | rodada=4 | `COMMITAR` manda chamar `proximo`, que leva ao `verificar --fundo` |
| R3@claude | LOW | APLICADA | rodada=4 | `proximo` que passa limpa a parada resolvida |
| R4@claude | LOW | APLICADA | rodada=4 | manifest sem linha: `DESIGN` com o motivo do lint, agora com asserção |
| R5@claude | LOW | APLICADA | rodada=4 | a seção do `--checar` também em PT |
| R1@codex | HIGH | APLICADA | rodada=4 | marca por criação exclusiva: quem perde não dispara (`test_duas_chamadas_juntas_repetem_uma_vez`) |
| R2@codex | HIGH | APLICADA | rodada=4 | trava de estado curta: leitura, alteração e gravação de um verbo por vez; nunca durante o gate |
| R3@codex | HIGH | APLICADA | rodada=4 | a limpeza da trava do gate roda dentro da trava de estado |
| R1@claude | MED | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: repetir sem teto total, no item 10 |
| R2@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: marca sobra depois de 401 |
| R3@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: laço de CPU se a trava abandonada não puder ser apagada |
| R4@claude | LOW | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: documento recente em sem classificação |
| R1@codex | HIGH | REBATIDA_ESCOPO | rodada=5 | decisão D4 do Roberto, 2026-11-06: publicar `b0663d3` como está, com este achado como 1ª tarefa da próxima frente: trava de estado vence com o dono vivo, só com comando suspenso por mais de 60 s; nada é publicado por isso |
