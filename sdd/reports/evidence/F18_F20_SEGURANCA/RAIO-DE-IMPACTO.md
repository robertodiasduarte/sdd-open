# Raio de impacto (0b) — antes da última rodada de revisão, sobre a2230d2

4 agentes em contexto novo, brief `.agents/skills/sdd-release/references/raio-de-impacto.md`, um por superfície.

| Superfície | Consumidores | Quebras | Destino |
|---|---|---|---|
| bloco do AGENTS.md (`gerar_corpo_agents` + `{{SEGURANCA}}`) | 17 | (1) `sdd_python_pronto 2>/dev/null` calava a causa do Python no init/sync (reproduzido com python3 falso que sai 9009); (2) no Windows, `\r\n` do Python deixaria o bloco sempre divergente (por leitura); piora: projeto atualizado só com sync fica com ponteiro para script e skill ausentes; o aviso de stack inválida dizia só "o leitor falhou" | consertados em `ff164c6`, com `test_init_sem_python_diz_a_causa_uma_vez`, `test_fim_de_linha_sempre_unix`, `test_doctor_acusa_skill_do_pacote_que_falta_no_projeto`, `test_stack_invalida_no_config_vira_a_causa_do_aviso` (os 4 caem em `a2230d2`) |
| templates (DEFINE, DESIGN, BUILD_REPORT, BRAINSTORM) | 29 | nenhuma (3 falhas vistas vieram de edição simultânea na árvore) | — |
| slots `security:` do config | 30 | nenhuma; nota: projeto com config antigo fica sem `security:` e usa os padrões | — |
| passos da release e do define, e o doctor | 49 | a mesma do Python (1ª linha acima); `test_docs.py` com 20 skills | consertados em `ff164c6` |

Invariantes INV-001 e INV-002: ok nas 4 superfícies.
Pontos de atenção que não quebram: "item 10" da FASE 2 da release citado em `docs/adaptation-guide.md`, `slot.sh` e
`deploy-do-sha.sh` agora convive com o item 10 da 0a; a sessão de recuperação "rode só o passo 11" do `verify-gate.sh`
pula o passo 12 (sem trava, não bloqueia).
