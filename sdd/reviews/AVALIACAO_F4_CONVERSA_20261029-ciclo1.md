# AVALIACAO F4_CONVERSA — ciclo 1 (contexto fresco, sobre `4e77a1f`)

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build). O veredito,
> os achados e a contagem estão como ele escreveu; a tabela por AT (sonda · esperado · observado) foi
> resumida a uma linha, e as sondas completas estão nos logs. Logs das sondas em `sdd/reports/evidence/F4_CONVERSA/AVAL-*.log` (a pasta se chamava
> `evidence/F4/` quando ele os gravou). As decisões sobre cada achado estão no Advisor Ledger de
> `sdd/reports/BUILD_REPORT_F4_CONVERSA.md`.

```text
<<<AVALIACAO
VEREDITO: NEEDS_WORK

Os 21 ATs que dá para executar aqui passaram, todos provados por execução. O AT-022 não pôde ser verificado: depende de uma run real do CI no GitHub e não havia credenciais. O veredito é NEEDS_WORK por 4 achados MEDIUM: dois lints deixam passar ou reprovam o contrário do que o DEFINE manda, uma skill se contradiz e há regras do DEFINE que nenhum teste protege. Não encontrei nenhum HIGH.

Base da revisão: worktree destacada em 4e77a1f, comparada com v2.2.4. Piso usado: /usr/bin/python3 3.9 e /bin/bash 3.2.

Tabela por AT: AT-001 a AT-021 PASS (AT-002 ver L1; AT-004 ver M1, L3; AT-005 ver L2; AT-012 ver M2; AT-013 ver L5; AT-015 ver M4, L4; AT-021 PASS literal, ver M4); AT-022 NÃO VERIFICADO (só local: linha 109 usa --conversa; varredura de integridade "0 finding(s) in 57 file(s)").

ACHADOS
M1 — MEDIUM — o skill-lint --conversa pula sem aviso a pergunta cujas opções vêm depois de uma linha em branco ou usam o marcador `*`. Reprodução: cópia do conversa-controle com printf '\n**Posso apagar a pasta?**\n\n- **Outro** — você descreve.\n- **sim** — apago.\n' >> references/como-falar.md → "✅ … camada de conversa ok" exit=0. Log: AVAL-skill-lint-mutacoes.log.
M2 — MEDIUM — o handoff-lint reprova um HANDOFF válido quando o bloco do Prompt de retomada tem uma linha que começa por "## " (secao(brutas, …) encerra a seção no primeiro "## ", mesmo dentro da cerca). Reprodução: inserir "## Saída esperada" dentro do bloco ```text do HANDOFF_VALIDO.md → "🛑 …: ## Prompt de retomada ausente ou sem o bloco de código…" exit=1. Log: AVAL-handoff-lint.log.
M3 — MEDIUM — a sdd-handoff se contradiz: linha 22 diz "Gerar o prompt da próxima sessão (opcional quando não há continuação)"; o passo 3b manda corrigir, e o lint exige o prompt. Reprodução: ficha sem prompt e Status "✅ DoD fechado" → rc=1. Log: AVAL-achados-extra.log.
M4 — MEDIUM — 7 regras escritas no DEFINE não têm teste: design-lint (zero ### Decision, {UPPER_SNAKE}, dependência de si mesma); handoff-lint (linha Status da Ficha, "conforme combinado", {UPPER} fora de código); test_agnostico (tirar TodoWrite, PostToolUse, Agent tool ou subagent_type da lista não reprova nada). Log: AVAL-at021-sabotagens.log.
L1 — LOW — sem a flag, o skill-lint não é idêntico à v2.2.4: a dica de erro do frontmatter mudou, e "--verbose" saía 1 conferindo os outros arquivos e agora sai 64. Log: AVAL-at002-sem-flag-saida.log.
L2 — LOW — o limite de 100 caracteres não vê "**Próximo passo:**" nem a linha dentro de citação "> ". Log: AVAL-skill-lint-mutacoes.log.
L3 — LOW — "Outro" só é pego com rótulo exato ("**Outra coisa**", "**Outro (descreva)**" passam). Log: AVAL-skill-lint-mutacoes.log.
L4 — LOW — o test_agnostico deixa de fora arquivos sem extensão, .toml e .html do escopo, e diferencia maiúsculas ("Task Tool", "agent tool" passam). Log: AVAL-agnostico-adversarial.log.
L5 — LOW — design-lint e handoff-lint com arquivo chmod 000 dão PermissionError com traceback, sem 🛑 nem RESULTADO. Log: AVAL-at013-uso-e-erros.log.
L6 — LOW — o design-lint reprova «…» num DESIGN; o DEFINE só lista «» para o HANDOFF, e « » é aspa legítima. Log: AVAL-design-lint.log.
L7 — LOW — "Na primeira resposta desta skill, comece com esta linha" e "Toda resposta… 1. **Status**" disputam o começo da 1ª resposta. Log: AVAL-achados-extra.log.
L8 — LOW — o skill-lint conta a seção mesmo dentro de bloco de código ("seção … repetida (2 vezes)"). Log: AVAL-achados-extra.log.

Também conferido sem problema: comandos e ordem dos passos nas 14 skills (só as exceções (a)–(d)); nomes de etapa; nenhum literal do publish-gate; nenhum Unicode invisível; nenhum nome de ferramenta de um agente só; init copia sdd/bin e sdd/templates novos; testes antigos só com troca de versão; suíte inteira no piso.

CONTAGEM: HIGH 0 · MEDIUM 4 · LOW 8
>>>
```
