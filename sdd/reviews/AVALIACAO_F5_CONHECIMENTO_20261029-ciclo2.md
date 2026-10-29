# AVALIACAO F5_CONHECIMENTO — ciclo 2 (contexto fresco, sobre `0e0dba5`)

> Bloco devolvido pelo avaliador em contexto fresco do ciclo 2 (subagente sem a conversa do build nem o
> ciclo 1), numa worktree destacada em `0e0dba5`. Veredito e achados como ele escreveu; reprodução de cada
> achado do ciclo 1 resumida a uma linha. Logs em `sdd/reports/evidence/F5_CONHECIMENTO/AVAL2-*.log`.

```text
<<<AVALIACAO
VEREDITO: PASS

Os 9 achados do ciclo 1 estão resolvidos em 0e0dba5: a reprodução original de cada um foi refeita
contra o commit, e cada correção desfeita numa cópia deixa vermelho o teste novo correspondente (15/15
mutações reversas pegas). O Verify Gate inteiro sai 0 no piso (publish-gate ci verde, 495 testes OK).
As correções trouxeram 3 defeitos novos, todos LOW; nenhum HIGH ou MEDIUM aberto.

Achados do ciclo 1: M1, M2, M3, L1, L2, L3, L4, L5, L6 — RESOLVIDO (reprodução contra 0e0dba5 e
mutação reversa em AVAL2-mutacao-reversa.log).
Tabela por AT tocado: AT-003, AT-005, AT-008, AT-009, AT-011, AT-012, AT-017 e a suíte — PASS.

ACHADOS (novos)
L1 — LOW — kb-dominios.py: pasta de domínio ilegível (chmod 000 sdd/kb/fiscal) dá traceback no
     rm.is_file() (PermissionError); DEFINE que abre com BOM direto em "## Technical Context" passou a
     "falta a linha" (fecha em vermelho). Log: AVAL2-kb-dominios-sondas.log.
L2 — LOW — gate.sh: kb_normativo.py quebrado (raise SystemExit(2), erro de sintaxe) sai como "RULE_MAP do
     exemplo não bate" e o → manda rodar o próprio script quebrado. Continua exit 2.
     Log: AVAL2-gate-mutacoes.log.
L3 — LOW — validate_kb.py --strict: o .resolve() segue link simbólico, então teste dentro da árvore que é
     link para fora reprova como "outside the project root" (falso positivo, fecha em vermelho).
     Log: AVAL2-strict-sondas.log.
>>>
```
