# AVALIACAO — F30_QUALIDADE_CODIGO (fatia S1) · ciclo 2 · 2026-11-23

> Bloco do avaliador de contexto fresco (subagente novo, modo `veredito`, ciclo 2), sobre o commit `dac782a`. Conteúdo
> do bloco devolvido, com a formatação das células condensada (os fatos e os números são os do avaliador). Logs das
> sondas em `sdd/reports/evidence/F30_QUALIDADE_CODIGO/AVAL2-*.log`.

<<<AVALIACAO
VEREDITO: PASS_PENDENTE_RECIBO

Escopo: fatia S1 (AT-001 a AT-009), HEAD `dac782a`. Todos os ATs passaram por execução, em fixtures `mktemp -d`. Pendente só o recibo da suíte inteira (Verify Gate). A emenda do AT-006 (DEFINE 1.4) está conferida: o achado 1 do ciclo 1 está fechado.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | AVAL2-AT-001-002.log, C1–C17 | slot cheio exige o log com `$ <slot>[ arquivos]` e `[exit=0]`; falhas ⇒ rc 1 com conserto; dívida antiga ⇒ aviso | C1 rc1 com conserto; C2 rc0; C3/C3b rc1; C4 rc1; C5 (antes `ruff check velho.py` exit 1, depois com arquivo novo) rc0 com aviso; C6/C7 rc1; C8/C9 rc1; C10 rc1 "o git o IGNORA"; C11–C13 tipos; C14/C15 só tipos cheio; C16/C17 aspas e comentário | PASS |
| AT-002 | AVAL2-AT-001-002.log, D1–D3 | vazios rc0; aviso sem a linha; nunca violação | D1 rc0 sem aviso; D2 rc0 com aviso; D3 sem config rc0 com aviso | PASS |
| AT-003 | AVAL2-AT-003-007.log | o verificar nomeia slots, logs, `lint: slot vazio`, arquivos da tarefa, escada | todos os termos presentes; testes F30 Ran 53 OK | PASS |
| AT-004 | AVAL2-AT-004-005.log | 1 bloco com 6 gerais + stack; sync 2× = 1 bloco | Python 6+Q07+Q08; JS 6+Q09; TS 6+Q09+Q10; sem stack 6; sync 2× 1 bloco; sync --check rc0; um só leitor do catálogo | PASS |
| AT-005 | AVAL2-AT-004-005.log, 5a–5c | ponteiro e ⚠️ com a causa; segurança igual | catálogo ausente, fora do formato, sem Python: aviso certo e só o ponteiro; segurança igual | PASS |
| AT-006 | AVAL2-AT-006.log (7 fixtures, hash) | sugestão da stack (PHP só phpcs, pela emenda) e instalar; nada gravado | Python, JS, TS e PHP como o DEFINE 1.4; com config, slot cheio ou sem stack: nada; hash IGUAL nas 7 | PASS |
| AT-007 | AVAL2-AT-003-007.log, AVAL2-AT-006.log | --linter, tradução, [D2], só com sim, sem instalar | texto e modo conferidos; sem sessão interativa para a conversa | PASS |
| AT-008 | AVAL2-AT-008.log | build do starter com regras, sem sdd/bin, F29 = 0 | rc_gerar 0; catálogo presente; regras, slots e `lint: slot vazio` no SKILL.md; sdd/bin 0; F29 0; check-gerado VERDE | PASS |
| AT-009 | AVAL2-AT-009.log, AVAL2-AT-009-seg.log | suíte, publish-gate, check-versions, segurança igual | check-versions VERDE; publish-gate CI rc0; segurança IGUAL origin/main × HEAD em 5 fixtures (o exit 1 do 1º log é recorte errado da sonda, refeito no seg.log); suíte não rodada | PASS (recibo pendente) |

ACHADOS
1. [AT-009, recibo] O GATE_S1.log em andamento roda sobre `07198f3`, não sobre o HEAD `dac782a`. Conserto: recibo de um `verify-gate.sh` iniciado com HEAD = `dac782a`, com `git rev-parse HEAD` no log.
2. [observação] JS puro (sem tsconfig.json) não recebe comando de tipos; leitura "JS → eslint, TS → tsc", coerente com o DESIGN ("ts soma-se à js").
>>>

## Tratamento (build, 2026-11-23)

- Achado 1: o gate roda de novo sobre `dac782a`, com o `git rev-parse HEAD` na 1ª linha do log (`GATE_S1_dac782a.log`).
- Achado 2: mantido; é a leitura do DESIGN (o `tsc` só existe com `tsconfig.json`).
