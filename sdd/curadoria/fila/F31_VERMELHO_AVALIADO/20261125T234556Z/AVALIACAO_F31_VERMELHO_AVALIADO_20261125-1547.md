<<<AVALIACAO
modo: veredito · ciclo: 1 · FEATURE: F31_VERMELHO_AVALIADO · commit avaliado: e0c134e · Python 3.9.6 (bordas também no 3.15)
CONTAMINAÇÃO: nenhuma. O brief não trouxe BUILD_REPORT, diff nem hipótese. Não abri os logs do build nem o ledger da revisão. O `report-lint.py` foi lido só para escolher bordas; todo resultado vem de execução.

Método: cada sonda monta um repositório git temporário fora do projeto e roda o lint de c747662 (velho) e o de e0c134e (novo). Compara exit, número de avisos `[casos avaliados]` e o resto da saída. Fonte das sondas em `AVAL-sondas-fonte.log` e `AVAL-sondas-fonte2.log`.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | alvo composto (0/0 com AT-005 em FAIL 3); 9 exits vermelhos; 0/126/127; 2 linhas somadas; kind `cmd`; marcas; cor ANSI; stdout ascii e LC_ALL=C; exit 1 por outro AT; mesmo AT em 2 tabelas | 1 aviso com id, log e conserto; exit igual ao do velho | igual em todas | PASS |
| AT-002 | FAIL 3 e 0/0 do vizinho; 10 ids parecidos (AT-0010, AT-001b, AT-001-b, AT-001_x, AT-1, BAT-001…) nos dois sentidos; contagem na 1ª linha; id no meio da linha | contagem alheia ignorada | certo, menos quando a contagem do vizinho é citada dentro da linha do próprio AT: o aviso some (A1b). Letra acentuada antes do id conta como marca (A5) | FAIL (A1) |
| AT-003 | comando próprio, compartilhado, 2 comandos, contagem parcial, AT `false`, `continue`, manual-ux, CRLF, 9 ATs | 0 com comando próprio; 1 por comando compartilhado, com os ids sem contagem | certo, menos com 1 AT só repetido em 2 tabelas: aviso falso (A2). Par com antes recusado: sem aviso (A3c) | FAIL (A2) |
| AT-004 | FAIL 1, 10, 99; PASS 5 · FAIL 1; módulo ausente em FAIL; soma de 2 linhas | 0 avisos | 0 nas sondas diretas; 1 aviso falso quando o título do caso cita `PASS 0 · FAIL 0` antes da contagem do fim (A1a) | FAIL (A1) |
| AT-005 | 3 contagens × UTF-8/cp1252/cp850 × LF/CRLF, mojibake simples e duplo, bytes misturados, log final, comando compartilhado CRLF × LF | igual ao UTF-8 com LF | igual. O único diferente é o comando da 1ª linha com acento em encodings diferentes, fora do contrato | PASS |
| AT-006 | exemplo extraído de cada um dos 3 textos e passado por `contagem_do_at` | reconhecido; regra do erro de carga presente | 3 de 3 → (0, 2); regra nos 3; `disciplina-de-teste.md` não cita `sdd/bin`; SKILL.md com 447 linhas. Ressalva: o texto diz que a linha "termina com a contagem", e o leitor usa a primeira (A1) | PASS (ressalva A1) |
| AT-007 | os 5 controles, mais smoke com 0/0, AT fora do DEFINE, antes ausente, `continue` vermelho; 51 BUILD_REPORTs velho × novo | exit e saída iguais, 0 avisos novos | iguais; 51 de 51 com exit e saída idênticos, 0 avisos novos | PASS |
| AT-008 | `check-versions --base origin/main`; 14 módulos vizinhos num clone de HEAD; MANIFEST | exit 0 | exit 0, 24 skills; 14 de 14 verdes (f31 33, f30_vermelho_antes 26, report_lint 32, report_lint_evidencia 37, f30_report_lint 17, f30_textos_s2 12, f30_sabotagem 21, f29_textos 11, gerar_starter 34, check_versions 16, gate_shell_evidencia 12, skill_lint 29, f30_starter 3, hooks 24); teste novo no MANIFEST | PASS no que foi medido. NÃO VERIFICADO: suíte inteira, `publish-gate` CI sobre `git archive`, CI Linux/Windows |
| AT-009 | a, b, c; a+b e alvo+b no mesmo AT (2 avisos); final com PASS 1, FAIL 1, exit 1, vizinho 0/0; sabotagem ao lado; caminho completo; somas | 1 aviso por log, exit igual | certo, menos: antes recusado cala o aviso do final 0/0 (A3); final próprio citado depois do de outra feature não é lido (A4) | FAIL (A3) |

Testes do repositório: 3 sabotagens minhas na cópia (já passava, 1ª linha, exit do final) foram pegas, cada uma com 1 falha.

ACHADOS
Reprodução de todos: salvar a fonte de `AVAL-sondas-fonte*.log` e os dois lints (`git show c747662:sdd/bin/report-lint.py` como `lint_old.py`; `git show e0c134e:sdd/bin/report-lint.py` como `lint_new.py`) e rodar `python3 -B achados.py`. Saída em `AVAL-achados.log`. Em todos, o exit é igual no velho e no novo.

A1 (média · AT-002, AT-004, AT-006) — o leitor usa a PRIMEIRA contagem da linha, e o método ensina que a linha "termina com a contagem de casos" (`disciplina-de-teste.md:23`).
 - A1a, alarme falso: antes `$ bash gate.sh` / `AT-001 ❌ avisa quando a linha diz PASS 0 · FAIL 0 (PASS 0 · FAIL 2)` / `[exit=1]`. Esperado 0 avisos; observado 1 ("nenhum caso avaliado").
 - A1b, aviso perdido: `AT-001 ❌ ignora AT-002 PASS 0 · FAIL 3 (PASS 0 · FAIL 0)` / `[exit=1]`. Esperado 1; observado 0: o FAIL 3 do vizinho tirou o aviso.
 O DESIGN (Decision 2) escreve "a contagem é a primeira da linha": DESIGN e texto ensinado discordam. Conserto sugerido: ler a última da linha, e acertar o DESIGN.

A2 (média/baixa · AT-003) — o mesmo AT em 2 tabelas reconhecidas conta como 2 ATs. Comando só dele, antes sem contagem, linha `true` do AT-001 em 2 tabelas com `Antes`. Esperado 0; observado: `[casos avaliados] AT-001, AT-001: o antes roda …, o mesmo comando de outro AT`. É alarme falso com mensagem falsa, e a D2 mede alarmes falsos para decidir o bloqueio. Não ocorre em nenhum dos 51 relatórios. Conserto: agrupar por id distinto.

A3 (baixa · AT-009, AT-003) — antes recusado cala avisos que o DEFINE não condiciona ao antes.
 - A3a: coluna `Antes` = `—`, `AT-001.log` = `$ …` / `AT-001 ❌ caso (PASS 0 · FAIL 0)` / `[exit=0]`. Esperado violação + 1 aviso; observado só a violação.
 - A3b: igual, com antes em `[exit=0]` num AT novo.
 - A3c: AT-001 sem contagem em `[exit=1]` e AT-002 novo `true` com a mesma 1ª linha e antes em `[exit=0]`. Esperado 1 aviso de comando compartilhado; observado 0.
 Atenuante: o exit já é 1, e o aviso do final deve sair depois de consertado o antes (nas sondas com antes aceito ele sai). O DESIGN restringe de propósito ("só logs que passaram nela"; Decision 4: "com o antes aceito"), mas o texto do AT-009 e do AT-003 não. Conserto: emitir o aviso do final sem depender do antes, ou restringir o DEFINE.

A4 (baixa · AT-009) — evidência `` `evidence/OUTRA/AT-001.log` · `evidence/EX/AT-001.log` ``, com o segundo em `[exit=0]` e 0/0: relatório VERDE e 0 avisos. Só o primeiro caminho com aquele nome é olhado. Esperado 1.

A5 (observação · AT-002) — `é AT-001 (PASS 0 · FAIL 0)` é lida como linha do AT; o DEFINE admite antes do id só marca. A mesma folga é o que aceita o mojibake `âœ…` da marca no Windows. Aceitável se registrada.

Observações sem efeito no veredito: cor `ESC(B` (tput sgr0) ou `38:2::…` antes do id faz a linha não ser reconhecida; contagem de 5000 dígitos derruba o lint com ValueError no Python 3.15 (exit 1), não no 3.9; `AT-008.antes/depois` não foram abertos.

Arquivos gravados (só estes, em `sdd/reports/evidence/F31_VERMELHO_AVALIADO/`): AVAL-AT-001, 002, 003, 004, 005, 006, 007, 009, AVAL-AT-008-versions, AVAL-AT-008-vizinhos, AVAL-bordas, AVAL-achados, AVAL-relatorios, AVAL-sondas-fonte, AVAL-sondas-fonte2 (todos `.log`). `gate-shell-evidencia.sh` verde nos 14 gravados até ali; depois dele regravei o AVAL-AT-006 e gravei o AVAL-AT-008-vizinhos. O AVAL-AT-008-vizinhos tem 11 dos 14 módulos: `gerar_starter`, `f30_starter` e `hooks` rodaram verdes antes, fora desse log, e a saída deles está só na tabela acima. Nada commitado; nenhum outro arquivo do projeto mudou.

VEREDITO: NEEDS_WORK
Motivo: o alvo, os 3 vizinhos, os 5 controles e os 51 relatórios funcionam, e nenhuma das sondas do contrato mudou o exit. Faltam A1 e A2 (alarme falso e aviso perdido alcançáveis) e A3/A4 (o AT-009 literal). Consertos pequenos; em A3 vale também restringir o DEFINE.
>>>
