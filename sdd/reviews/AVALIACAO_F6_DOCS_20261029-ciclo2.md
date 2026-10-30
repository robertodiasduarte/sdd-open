# AVALIAÇÃO F6_DOCS — ciclo 2 (contexto fresco, modo veredito)

> Bloco devolvido pelo avaliador do ciclo 2 (subagente sem a conversa do build), sobre o commit
> `aaae1b4` na worktree destacada, com os achados do ciclo 1 como brief. Piso Python 3.9.6 e bash 3.2.57.
> Logs em `sdd/reports/evidence/F6_DOCS/AVAL2-*.log` (14 arquivos). As decisões sobre os achados novos
> estão no Advisor Ledger do `BUILD_REPORT_F6_DOCS.md`.

<<<AVALIACAO
VEREDITO: PASS — 0 HIGH, 0 MEDIUM, 6 LOW (novos)

| achado do ciclo 1 | resultado |
|---|---|
| H1 "registra e libera" | resolvido (guia bate com sdd-higiene-dado:145; sabotagem AT-002g vermelha) |
| H2 ficha da sdd-design | resolvido (verify-gate na fixture de clarificação → 5; sdd-build manda parar no 5) |
| H3 item YAGNI da sdd-brainstorm | resolvido (bate com o passo 5) |
| M1 starter e doctor | resolvido no guia (HOME falso: doctor não vê o global; no projeto, avisa); quickstarts → L6 |
| M2 SDD_FORA_DO_GIT | resolvido no que foi pedido (2 frases do starter, "não entra", caixa alta vermelhos); sobra → L4 |
| M3 sdd/bin na atualização | resolvido (caminho do guia seguido de ponta a ponta: sync --check EM DIA, doctor em dia) |
| L1 caixa do link no macOS | resolvido (ROADMAP.md e PT-BR/ vermelhos) |
| L2 sync sem --yes | resolvido |
| L3 release recusada | resolvido |
| L4 títulos da sdd-design | resolvido (design-lint reprova "Decisão N:" e "ADR-N:") |
| L5 rótulo com "?" | resolvido (0 negritos com "?" nas 7 seções) |
| L6 "=", doctor, "prepare once" | resolvido |

AT-001 a AT-014: PASS (sabotagens AT-001a/b, 002a–g, 003a/b, 004a, 005e, 006a, 007a, 008a/b/b2/c, 009 ×13,
014a/b/c vermelhas; clone limpo verde; gate com 514 OK; contratos 0 linhas; check-versions VERDE; texto
normalizado igual à v2.2.6 nas 7; baseline v2.2.6 com 26 falhas). As 7 seções conferidas item a item contra
o corpo de cada skill. Nenhum caractere invisível nos 9 arquivos do fix.

ACHADOS NOVOS:
- L1 · guia :95 · "copia de volta só o que você apagou": o init também reescreve o bloco do AGENTS.md e os adaptadores.
- L2 · guia :91-92, :584, :627; quickstarts PT :180, EN :175/:180 · skill é apontada por versão mais velha; sdd/bin/ por qualquer diferença (sdd-open.sh:606-616); os docs trocam as duas regras.
- L3 · guia :41-42 · o verify-gate.sh é bash, não python.
- L4 · tests/test_docs.py:40-41 · "em qualquer redação" promete mais que o regex (4 paráfrases passam).
- L5 · guia :582 · o alarme também recusa planilha nova.
- L6 · quickstarts PT :223-224, EN :222 · "o doctor avisa se detectar os dois" desencontra do guia (não vê o global).
>>>
