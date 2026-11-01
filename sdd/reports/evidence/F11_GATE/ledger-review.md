# Ledger da revisão adversarial do build — F11_GATE

Rodada 1: `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-081440` (revisor claude, 2º revisor codex — 39 arquivos —,
auditor openrouter:qwen/qwen3.7-plus; diff de `06e5a9d`; `loop` PRONTO, 0 HIGH; convergência `sim`; US$ 1,13).
Rodada 2: `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-082625` (mesmas engines; diff de `ab2f252`; `loop` PRONTO, 0 HIGH;
`--conferir` CONFERE; US$ 1,17).
Rodada 3 (teto): `sdd/reports/reviews/EXTERNAL_REVIEW_20261101-083920` (mesmas engines; diff de `9508ff0`; `loop` PRONTO,
0 HIGH; `--conferir` CONFERE; US$ 1,19). Esta é a revisão da release.
Lido por `sdd/bin/sdd-fluxo.sh loop` por célula.

| achado | sev | veredito | rodada | evidência / motivo |
|---|---|---|---|---|
| R1@claude | MED | APLICADA | rodada=1 | a suíte rodava o gate ~23 vezes: extrações nulas e sinais de credencial das 4 engines viraram 1 execução cada (19 testes em 135 s → 21 em 109 s); `verde-real1.log` |
| R2@claude | LOW | APLICADA | rodada=1 | o teto de 120 s saiu da asserção (fica na evidência local, como o DESIGN diz) |
| R3@claude | LOW | APLICADA | rodada=1 | cenários e respostas conferidos no pré-voo (exit 3 antes de qualquer chamada); servidor que não sobe no meio vira ❌ do cenário, não exit 3; `test_real1_cenario_ausente_sai_3_antes_de_qualquer_chamada` |
| R1@codex | MED | APLICADA | rodada=1 | wrapper com `shlex.quote`; `test_real1_caminho_com_metacaractere_de_shell` (vermelho em `baseline-real1.log`) |
| R2@codex | MED | APLICADA | rodada=1 | mesmo conserto do R2@claude |
| R1@claude | MED | APLICADA | rodada=2 | o stub da OpenRouter é provado no pré-voo (exit 3 sem nenhuma chamada); no meio, segue como ❌ do cenário; `test_real2_servidor_que_nao_sobe_e_gate_quebrado` |
| R2@claude | LOW | APLICADA | rodada=2 | eval-agree usa o modelo principal (antes do `+`) do gemini; `test_real2_gemini_com_varios_modelos_fica_numa_linha` |
| R1@codex | MED | APLICADA | rodada=2 | comentário sem indentação não fecha o bloco `review:`; `test_real2_comentario_sem_indentacao_no_bloco_review` |
| R2@codex | MED | APLICADA | rodada=2 | mesmo conserto do R1@claude |
| R3@codex | MED | APLICADA | rodada=2 | o anel confere `auditor_exit 0`; `test_real2_anel_confere_auditor_exit` |
| R1@claude | LOW | REBATIDA_EVIDENCIA | rodada=3 | tirar o slug do id é a decisão do DESIGN (Advisor Ledger L4; Decision 3) para `openrouter` e `openrouter:<slug>` somarem; o modelo que respondeu continua na chave; o auditor refutou com evidência (`test_at014_numeros_exatos_da_fixture`) |
| R1@codex | MED | REBATIDA_EVIDENCIA | rodada=3 | agrupar pelo modelo principal do gemini é a correção da rodada 2 (R2@claude), para o mesmo auditor não virar várias linhas por roteamento interno; o auditor refutou com evidência (`test_real2_gemini_com_varios_modelos_fica_numa_linha`) |
