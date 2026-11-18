# Ledger da revisão — F21_ENGENHARIA_REVERSA

Revisor claude, auditor qwen pela OpenRouter, 4 rodadas em 2026-11-10; o 2º revisor (codex) falhou por cota nas rodadas 1 a 3 e foi
dispensado pelo Roberto para a 4. A marca `dano` é de quem decidiu cada achado nesta frente, pelo `sdd/review/CRITERIO_DANO.md`.
Gravado depois da release, no formato que a F19 criou; durante a F21 as decisões ficaram no Advisor Ledger do BUILD_REPORT.

| achado | sev | veredito | rodada | evidência | dano | revisão |
|---|---|---|---|---|---|---|
| R1@claude | MED | APLICADA | rodada=1 | teste: `test_o_teste_do_lint_nao_grava_bytecode_na_pasta_da_skill` · sem `sys.dont_write_bytecode`, rodar a suíte sem `-B` gravava `.pyc` na pasta da skill, e o `init` e o zip do starter o publicariam (publicação) | sim | EXTERNAL_REVIEW_20261110-124230 |
| R2@claude | LOW | APLICADA | rodada=1 | exemplo de recusa do `como-falar.md` com instrução ao agente no corpo; `test_exemplo_de_recusa_nao_traz_instrucao_ao_agente`; texto de orientação, sem efeito sobre dado, acesso ou publicação | nao | EXTERNAL_REVIEW_20261110-124230 |
| R1@claude | LOW | APLICADA | rodada=2 | `esperado` de ER-08 e ER-09 sem as duas regras da 1.1.0; `test_cenarios_cobram_as_duas_regras_da_1_1_0`; documentação de cenário | nao | EXTERNAL_REVIEW_20261110-125915 |
| R2@claude | LOW | APLICADA | rodada=2 | manifesto sem a ressalva de que o ER-01 rodou com a redação anterior; declaração, sem efeito em execução | nao | EXTERNAL_REVIEW_20261110-125915 |
| R1@claude | LOW | APLICADA | rodada=3 | frase pronta de "instrução para a IA" sem fonte, trecho e registro; `test_instrucao_embutida_e_avisada_ao_usuario`; a regra do `SKILL.md` já mandava avisar e as 3 execuções reais avisaram | nao | EXTERNAL_REVIEW_20261110-130815 |
| R2@claude | LOW | APLICADA | rodada=3 | caminhos comparados como `str(Path)` falhariam em Windows; só o teste falharia, com a pasta correta | nao | EXTERNAL_REVIEW_20261110-130815 |
| R1@claude | LOW | REBATIDA_ESCOPO | rodada=4 | teste de dentes tautológico em `tests/test_f21_textos.py`; a 4ª rodada era a última (decisão do Roberto); a prova negativa é a sabotagem M3; pendência na ficha | nao | EXTERNAL_REVIEW_20261110-132950 |
