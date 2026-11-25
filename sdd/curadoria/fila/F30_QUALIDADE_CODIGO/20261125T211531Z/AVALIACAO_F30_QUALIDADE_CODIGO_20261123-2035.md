# AVALIACAO — F30_QUALIDADE_CODIGO (fatia S1) · ciclo 1 · 2026-11-23

> Bloco do avaliador de contexto fresco (subagente, modo `veredito`, ciclo 1), sobre o commit `07198f3`. Conteúdo
> do bloco devolvido, com a formatação das células condensada (os fatos e os números são os do avaliador). Logs das sondas em `sdd/reports/evidence/F30_QUALIDADE_CODIGO/AVAL-*.log`.

<<<AVALIACAO
VEREDITO: NEEDS_WORK

Motivo único: AT-006 pede, para PHP, "`php -l` e `phpcs`"; o `checar.sh` sugere só `vendor/bin/phpcs --standard=PSR12` e nenhum comando de tipos. Todos os outros ATs da S1 passaram nas sondas. AT-009 parcial (a suíte inteira não foi rodada por instrução; o recibo vem do Verify Gate em andamento). Sem o achado 1, o veredito seria PASS_PENDENTE_RECIBO, pendente do recibo do gate.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-001 | AVAL-AT-001-002.log (A1–A12), AVAL-AT-001-bordas.log | slot cheio exige LINT.log/TIPOS.log com o comando do slot e [exit=0]; ausente, outro comando, sem [exit=], exit≠0 ou ignorado ⇒ rc 1 com conserto; dívida antiga ⇒ aviso | A1 rc1 com conserto; A2 rc0; A3/A3b rc1 (inclusive prefixo `ruff checkx`); A4 rc1; A5 rc0 com aviso de dívida antiga; A6/A7 rc1; A8 rc1; A9 rc1; A10 rc1, A11 rc0; A12 só tipos cheio não exige LINT.log; slot com aspas duplas, simples, sem aspas e com comentário lidos | PASS |
| AT-002 | AVAL-AT-001-002.log (B1–B3) | slots vazios rc 0; com a linha sem aviso; sem ela, aviso que nomeia a linha | B1 rc0 sem aviso; B2 rc0 com aviso; B3 sem config rc0 com o aviso | PASS |
| AT-003 | AVAL-AT-003-007.log | o verificar nomeia 2 slots, 2 logs, `lint: slot vazio`, arquivos da tarefa, escada | SKILL.md:195-200 traz tudo; test_f30_textos 8 OK | PASS |
| AT-004 | AVAL-AT-004-005.log | 1 bloco com 6 gerais + stack; sem stack só gerais; sync 2× = 1 bloco | Python 6+2+ponteiro; JS 6+1; TS 6+JS+TS; sem stack 6; sync 2× rc0, 1 bloco; sync --check rc0 | PASS |
| AT-005 | AVAL-AT-004-005.log (5a–5c) | ponteiro e aviso com a causa; segurança igual | catálogo ausente, fora do formato e sem Python: o aviso certo e só o ponteiro; segurança igual (sem Python, a segurança cai para o ponteiro dela, comportamento anterior à F30) | PASS |
| AT-006 | AVAL-AT-006.log (7 fixtures, hash antes/depois) | ⚠️ com o comando da stack (Python ruff/mypy; JS/TS eslint/tsc; PHP php -l/phpcs) e o instalar; nada gravado | Python, JS, TS como esperado; PHP só phpcs, tipos "—", sem php -l; com config, slot cheio ou sem stack: nada; hash igual em todas | FAIL (PHP) |
| AT-007 | AVAL-AT-003-007.log, AVAL-AT-006.log | --linter, voz da como-falar, [D2], grava só com sim, sem instalar | texto e modo --linter conferidos; a conversa não tem sessão para executar | PASS |
| AT-008 | AVAL-AT-008.log | build do starter com regras e lint/tipos, sem sdd/bin, grep F29 = 0 | rc_gerar 0; catálogo copiado; 6 gerais, slots, `lint: slot vazio`; sdd/bin 0; F29 0; check-gerado VERDE | PASS |
| AT-009 | AVAL-AT-009.log | suíte, publish-gate, check-versions, segurança igual | check-versions VERDE; publish-gate CI rc0; segurança igual HEAD~1 × HEAD; suíte inteira não rodada | PASS parcial, recibo pendente |

ACHADOS
1. [AT-006] A sugestão para PHP não traz `php -l`. Reprodução: `d=$(mktemp -d); cd $d; git init -q .; echo '{}' > composer.json; echo '<?php echo 1;' > index.php; bash <worktree>/.agents/skills/sdd-checar-ambiente/scripts/checar.sh --linter` ⇒ `php	vendor/bin/phpcs --standard=PSR12	—	composer require --dev squizlabs/php_codesniffer`, rc 0. Consertos: pôr `php -l` nas 2 cópias, ou emendar o AT-006 com changelog.
2. [AT-009] Recibo da suíte inteira pendente do Verify Gate em andamento.
>>>

## Tratamento (build, 2026-11-23)

- Achado 1: emenda do AT-006 (DEFINE 1.4). O `php -l` confere um arquivo por chamada e não tem modo de projeto
  inteiro: no slot de tipos, que roda como está (Decision 4), ele leria a entrada padrão e travaria o Build. Ciclo 2
  do avaliador confere a emenda.
- Achado 2: recibo do Verify Gate em `evidence/F30_QUALIDADE_CODIGO/GATE_S1.log`.
