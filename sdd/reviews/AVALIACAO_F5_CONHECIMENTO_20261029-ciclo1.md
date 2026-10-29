# AVALIACAO F5_CONHECIMENTO — ciclo 1 (contexto fresco, sobre `7e5b25c`)

> Bloco devolvido pelo avaliador em contexto fresco (subagente sem a conversa do build), numa worktree
> destacada em `7e5b25c`. Veredito, achados e contagem como ele escreveu; a tabela por AT está resumida a
> uma linha. Logs das sondas em `sdd/reports/evidence/F5_CONHECIMENTO/AVAL-*.log`. As decisões sobre cada
> achado estão no Advisor Ledger de `sdd/reports/BUILD_REPORT_F5_CONHECIMENTO.md`.

```text
<<<AVALIACAO
VEREDITO: NEEDS_WORK

No piso (Python 3.9.6, bash 3.2.57), o Verify Gate completo sai 0 (publish-gate ci verde, 487 testes OK);
as 4 sabotagens, a baseline vermelha, os contratos byte a byte, comandos intactos, check-versions e o
gate.sh em cenários adversos (outra pasta, cópia, caminho com espaço, .claude/skills depois do init)
passam. Não sai PASS por 3 achados MEDIUM; o resto é LOW.

Tabela por AT: AT-001, AT-002, AT-004–AT-007, AT-009–AT-017 PASS (AT-005 ver L3; AT-009 ver L2; AT-011
ver L5; AT-012 ver L4; AT-017 ver L6); AT-003 FAIL (M2, M3, L1); AT-008 FAIL (M1).

ACHADOS
M1 — MEDIUM — kb-dominios.py lê a 1ª linha KB Domains do arquivo inteiro, não a do ## Technical Context:
     linha em outra seção passa (exit 0) e um `nenhum` anterior esconde nome inexistente.
     Log: AVAL-kb-dominios-sondas.log.
M2 — MEDIUM — o ramo do RULE_MAP derivado do gate.sh nunca é alcançado: o caso aceito `normativo` cai antes,
     com "caso bom REJEITADO" e o conserto errado. Log: AVAL-gate-mutacoes.log.
M3 — MEDIUM — 2 dos 5 gatilhos do AT-003 (caso bom rejeitado, rejeitado por outro motivo) e o bloco
     rule-map --check sem teste: mutação que os tira deixa a suíte verde. Log: AVAL-cobertura-mutacoes.log.
L1 — LOW — falha() imprime o $T/saida do caso anterior (âncora ausente mostra "is not registered").
L2 — LOW — sdd/kb ilegível dá traceback no kb-dominios.py.
L3 — LOW — --strict aceita teste absoluto ou com ../ fora da raiz do projeto.
L4 — LOW — PROIBIDO do TextoDaSkill diferencia caixa e não casa ](./assets/ nem ](../assets/.
L5 — LOW — ABERTA ≥ 3 não confere quais perguntas existem.
L6 — LOW — a linha 🛑 da cópia gerada não traz o caminho rodado.
>>>
```
