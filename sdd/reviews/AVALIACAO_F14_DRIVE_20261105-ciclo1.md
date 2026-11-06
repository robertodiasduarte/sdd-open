<<<AVALIACAO
FEATURE: F14_DRIVE · ciclo: 1 · commit avaliado: 079f5fa · plataforma: macOS, /bin/bash 3.2.57, /usr/bin/python3 3.9.6
veredito: NEEDS_WORK

Motivo: 1 HIGH. `verificar` grava o HEAD depois que o gate termina, então um commit feito durante o gate recebe o verde sem ter sido testado, e `concluir` declara `gate-verde` (AT-008, AT-014). Há também 9 MEDIUM: 4 em AT-030 (arquivar documento de frente aberta) e 1 em cada um destes: AT-010, AT-011, AT-013, a variável vazada para o gate e `concluir` x `proximo`.

Testes do pacote (AVAL-01, em cópia de `git archive`, SDD_TEST_BASH=/bin/bash, Python 3.9), todos verdes:
- test_drive 59
- test_deploy_do_sha 27
- test_sdd_archive 17
- test_f14_drive_textos 19
- test_avaliador_guard 14
- test_playbook_curator 104
- test_fluxo 67
- test_verify_gate 27
- test_decisoes_lint 11
- test_inventario 24
- test_bash32 3
- test_docs 23

Os achados abaixo são de sondas além desses testes. A suíte inteira e o gate do DEFINE não foram rodados por mim, conforme a instrução.

## Tabela por AT

Logs em sdd/reports/evidence/F14_DRIVE/.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| 001 | AVAL-02, pasta com espaço e acento | estado, `ACAO`, `rodada: 1/N`, exit 10 | conforme | PASS |
| 002 | AVAL-14, AVAL-15 | recusas com exit 20 e sem estado; vizinho velho sai 2 | conforme. `master` sem slot nem origin passa (L7) | PASS |
| 003 | AVAL-02 | não roda nem grava | `sdd/reports` ausente, gate não rodou | PASS |
| 004 | AVAL-14 | 64 nomeando a origem; flag > slot > 3 | conforme | PASS |
| 005 | AVAL-28, AVAL-11 | ordem das ações | DESIGN, REVISAO_DESIGN, RODADA, VERIFICAR, ESPERAR, CORRIGIR, AVALIAR | PASS |
| 006 | AVAL-22 R7 | linha nova do manifest vira `- [ ]` | `x` não entra se existe `x y.md` | PASS com L6 |
| 007 | AVAL-15 | para na 3ª; HEAD novo zera | conforme | PASS |
| 008 | AVAL-03, 04, 11, 23, 27 | grava exit, HEAD e digital da execução | exits e numeração certos, mas o commit gravado é o de depois do gate | FAIL (H1) |
| 009 | AVAL-23 R2, AVAL-27 | mapa de exits sem gastar rodada | conforme, inclusive sinal `[exit=-9]` | PASS |
| 010 | AVAL-07, AVAL-08 | COMMITAR com mudança rastreada fora dos documentos | rename para a pasta de documento passa e roda o gate; `concluir` sem verde dá VERIFICAR | FAIL (M2, L1) |
| 011 | AVAL-09, AVAL-22 R4/R5, AVAL-05 | para, aceita, invalida o verde | caminho normal ok; aceite durante o gate valida gate não rodado | FAIL (M1, L4, L5) |
| 012 | AVAL-22 R3 | orçamento e `--resume --max` | conforme | PASS |
| 013 | AVAL-06 | estado inválido, exit 20, nunca adivinha | JSON ilegível ok; forma errada dá traceback, exit 1 | FAIL (M4) |
| 014 | AVAL-02, 03, 08 | `gate-verde` só com verde do HEAD | verde herdado de commit não testado; ignora tarefa pendente | FAIL (H1, M9) |
| 015 | AVAL-02, 15, 23 | relatório reescrito em toda parada | sim; texto do bloqueio se perde (L3) | PASS com L3 |
| 016 | AVAL-15 | recibo 0, bloqueio 20, aguardar 40; outro exit é repetido | conforme | PASS |
| 017 | AVAL-13, shim em todos os verbos | sem push, gh release ou workflow run | 359 chamadas, 0 proibidas | PASS |
| 018 | AVAL-21 | self-test com 12 motivos e exits; sabotagem derruba | verde, sabotagem sai 2. `sdd/fixtures/drive/` não existe (L10) | PASS com L10 |
| 019 | AVAL-01 (textos), AVAL-21, AVAL-26 | 12 motivos nos 4 lugares; skill-lint | presentes; `--conversa` sai 0 | PASS |
| 020 | AVAL-13, AVAL-15 | parada nomeia tarefa e `<<<RODADA`; aviso só na 1ª | conforme | PASS |
| 021 | AVAL-01, AVAL-26 | 0b por superfície | texto presente, teste verde | PASS (texto) |
| 022 | AVAL-17 | só branch padrão com push/dispatch | conforme: tag, outra branch, schedule, PR e release não contam | PASS |
| 023 | AVAL-01, AVAL-18 | substituto; incerto nunca decide | conforme nos testes do pacote e nos cenários A1–A18. A1 (run sem headSha) dá traceback (L12) | PASS |
| 024 | AVAL-17, AVAL-18 A8 | 1 redisparo, marca na pasta comum, nunca rerun | conforme, inclusive de outra worktree | PASS com L11 |
| 025 | AVAL-18 | sai 2 com motivo | conforme | PASS |
| 026 | AVAL-18 | 4, 3 e 64 | conforme | PASS com L13 |
| 027 | AVAL-26 | item 10 chama o script | conforme | PASS |
| 028 | AVAL-19, AVAL-20 Q12 | lotes; `git status` igual | conforme, também no próprio projeto | PASS com L15, L16 |
| 029 | AVAL-20 Q1, Q4, Q5, Q9 | `git mv` staged; pula e avisa; falha sai 2 | conforme | PASS |
| 030 | AVAL-19 P1–P5, AVAL-20 Q3, Q9 | ficha aberta protege | 4 caminhos movem documento de frente aberta | FAIL (M5, M6, M7, M8) |
| 031 | AVAL-26 | regra do changelog | presente | PASS (texto) |
| 032 | AVAL-24 | não rastreado nas 4 pastas não trava | rc=0 com contagem | PASS |
| 033 | AVAL-25, AVAL-24 | rastreado modificado e fora dos documentos saem 1 | conforme, inclusive rename para documentos | PASS |
| 034 | AVAL-24 | eco e diagnóstico não contam; achado real conta | conforme | PASS |
| 035 | AVAL-21 | slots; sem `max_tokens` | conforme | PASS |
| 036 | AVAL-21 | docs, manifesto, roadmap, 19 skills | conforme | PASS |
| 037 | AVAL-21 | `--checar` 0/5/64 sem rodar cmd; `--drive` para em D1 | conforme | PASS |
| 038 | não rodado | agente real | fica para depois, conforme instrução | NAO_VERIFICADO |

## ACHADOS

As reproduções usam os ajudantes `mkrepo`, `drv`, `feito`, `novo`, `mkarq`, `velho`, `arq`, `cen`, `d1`, registrados em AVAL-29-lab-final.log. O comando exato de cada sonda está no início do log citado.

**HIGH**

**H1. O verde é gravado no commit errado (AT-008, AT-014).** Linha `sdd/bin/sdd-drive.sh:725`: `commit=p.head()` roda depois do gate. A forma de gate usada na sonda (`git archive HEAD`) é a do próprio DEFINE. O `--fundo`, feito para o agente seguir trabalhando, abre essa janela.

Reprodução (AVAL-03; 1º plano em AVAL-04):
```
mkrepo $V/x 'T=$(mktemp -d) && git archive HEAD | tar -x -C $T && sleep 3 && test ! -f $T/quebra.txt'
printf 'import sys\nsys.exit(0)\n' > sdd/bin/report-lint.py; git add -A; git commit -qm stub
drv iniciar $D; feito; drv verificar $D --fundo
sleep 1; echo q > quebra.txt; git add quebra.txt; git commit -qm durante
sleep 4; echo x > sdd/reports/BUILD_REPORT_F.md; drv concluir $D
```
Observado: `motivo: gate-verde`, exit 0, e o estado registra o commit novo. O mesmo gate nesse HEAD sai 1.
Conserto sugerido: capturar HEAD e digital antes de rodar o gate. Na volta, se o HEAD mudou com código, tratar como não provado.

**MEDIUM**

**M1. Aceite durante o gate valida um gate que nunca rodou (AT-011).** Linhas 723–725: a digital vem do estado recarregado depois do gate. Mesma raiz e mesmo conserto de H1.
Reprodução (AVAL-05): gate `sleep 3; true`, depois `verificar --fundo`. No meio, trocar `cmd` por `false`, commitar e rodar `--resume --aceitar-gate-novo`. Em seguida `concluir`.
Observado: `gate-verde`, com `gate_cmd: false`, que nunca rodou.

**M2. Rename de código para pasta de documento burla o COMMITAR (AT-010).** `fora_dos_documentos` olha só o nome novo do registro `R`. O avaliador-guard pega o mesmo caso.
Reprodução (AVAL-07): `git mv codigo.py sdd/reports/codigo.py; drv verificar $D`.
Observado: roda o gate e gasta rodada. Na variante com gate `true`, grava verde com a árvore suja.

**M3. `SDD_DRIVE_TRAVA_HERDADA=1` vaza para o gate (AT-008).** O `--fundo` passa a variável ao filho, e o gate a herda.
Reprodução (AVAL-12): `SDD_DRIVE_TRAVA_HERDADA=1 SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p test_drive.py`.
Observado: 4 FAIL. Um gate cuja suíte exercite o drive, como o deste repositório, sairia vermelho falso e gastaria rodada. Isso é inferência a partir desses 4 FAIL: não rodei o gate inteiro com `--fundo`. A skill recomenda `--fundo` justamente para gate longo.
Conserto sugerido: remover a variável do ambiente do `verify-gate`.

**M4. Estado com forma errada sai 1 com traceback (AT-013).** `le_estado` valida só o nível de cima.
Reprodução (AVAL-06): no JSON, `"gates":[{}]` ou `[1]`, depois `proximo`. Resultado: KeyError ou TypeError, exit 1. Variações:
- `"repeticao":3` quebra `proximo`.
- `"recibos":3`, `"trocas_gate":3`, `"gate_cmd":null` e `"inicio":null` quebram `recibo`.
- `"gates":[{"exit":"2"}]` não conta rodada vermelha em `proximo`, `concluir` e `--resume`; `recibo` quebra com `KeyError: 'n'`.
Esperado: `motivo: estado-invalido`, exit 20.

**M5. `FIX_REPORT_<F>` escapa da ficha aberta (AT-030).** Em `PREFIXOS`, `FIX` vem antes de `FIX_REPORT`, e o grupo vira `REPORT_F14`.
Reprodução (AVAL-19 P1, AVAL-20 Q8): `HANDOFF_F14` aberta e `FIX_REPORT_F14.md` antigo; `sdd-archive.py --lote soltos --aplicar`.
Observado: move o arquivo, enquanto os outros 3 ficam protegidos. No lote sem-ledger, o destino vira `sdd/archive/REPORT_F14/`.

**M6. Feature com minúscula ou hífen não tem proteção (AT-030).** `RX` só aceita maiúsculas, e `sem_grupo` nunca passa por `protecao`. O drive aceita esses nomes (`LETRAS`).
Reprodução (AVAL-19 P2): `HANDOFF_minha-frente.md` aberta, com `BUILD_REPORT_`, `DRIVE_REPORT_` e `AVALIACAO_minha-frente`.
Observado: os 3 são movidos, com `protegidos=0`. Reversível: fica só staged, nada é apagado.

**M7. Ficha aberta de slice não protege (AT-030).** `RX_INTEIRO` não casa `_s2`, então `inteiro` vira `G`.
Reprodução (AVAL-19 P4): `HANDOFF_G_s2.md` aberta, `DEFINE_G_s2.md` e `sdd/releases/G/`.
Observado: o documento entra no lote com-ledger, com `protegidos=0`.

**M8. Documento solto citado em ficha aberta é movido (AT-030, por extensão).** Mesma causa de `sem_grupo`.
Reprodução (AVAL-19 P3): ficha aberta citando `sdd/reports/NOTAS_DA_FRENTE.md`, `parecer.txt` e `BUILD_REPORT_ABC.json`.
Observado: os 3 são movidos.

**M9. `concluir` declara `gate-verde` onde `proximo` manda trabalhar (AT-005 x AT-014).** Reprodução (AVAL-08), depois do verde:
- Reabrir uma tarefa, o que a seta do `CORRIGIR` manda fazer: `proximo` dá RODADA, `concluir` dá `gate-verde`.
- Linha nova no manifest: mesmo resultado.
- DESIGN renomeado: `proximo` dá DESIGN, `concluir` dá `gate-verde`.
A letra do AT-014 é cumprida; a contradição é com a ordem do AT-005. O texto do AT-014 precisa decidir este caso.

**LOW**

- **L1.** `concluir` sem verde e com arquivo sujo dá VERIFICAR, não COMMITAR. AVAL-08.
- **L2.** A parada de `clarificacao-pendente` ou `define-invalido` vinda de `confere_gate` fica presa até o `--resume`, mesmo com `--checar` já em 0, e a seta diz "rode de novo". AVAL-10.
- **L3.** `recibo` reescreve o relatório sem o texto do `bloqueio`. O contador de XYZ vai de 1 para 0. AVAL-15.
- **L4.** A troca aceita só entra no DRIVE_REPORT na próxima parada; depois do aceite e do `verificar` ainda diz "Nenhuma troca.". AVAL-23 R5b.
- **L5.** `gate-alterado` por `kind`, `pass_when`, `threshold` ou `manual_fallback` mostra `antes` igual a `agora` e afirma que o comando mudou. AVAL-09.
- **L6.** Linha nova `x` não é acrescentada se já existe `x y.md` (`startswith(i + " ")`). AVAL-22 R7.
- **L7.** Na `master`, sem slot e sem origin, `iniciar` passa: o fallback só conhece `main`. AVAL-14.
- **L8.** Três efeitos da trava (AVAL-11):
  - pid vivo reaproveitado dá ESPERAR sem fim, sem citar o arquivo da trava;
  - `kill -9` no python deixa o gate órfão rodando enquanto `proximo` diz VERIFICAR;
  - o bash 3.2 despeja o script inteiro (cerca de 46 KB no log) no stderr.
- **L9.** `commit.gpgsign=true` global faz o self-test sair 2 dizendo que o script não cumpre o contrato: `GIT_CONFIG_GLOBAL` não é isolado. AVAL-21.
- **L10.** AT-018 e o Technical Context citam `sdd/fixtures/drive/`, que não existe. O DESIGN (linha 340) decidiu não depender dela, mas o DEFINE não foi alinhado. AVAL-21.
- **L11.** `passo_falho` olha só o 1º passo falho. Passageiro no job 1 e real no job 2 redispara. AVAL-18 A4.
- **L12.** `gh` com forma inesperada dá traceback, exit 1: run sem `headSha` (`contem(None)`) e `run view` devolvendo lista. Formas sintéticas. AVAL-18 A1, A2.
- **L13.** A linha `consulta falhou` sai a cada intervalo, sem o limite de 1 por minuto. Workflow com nome errado espera o teto inteiro (40 min por padrão). AVAL-18 A11, A12.
- **L14.** `sdd-archive.py` quebra com UnicodeEncodeError sob stdout cp1252, simulando Git Bash com pipe (o README promete Windows). O `skill-lint.py` também; o `report-lint.py` não quebrou na mesma sonda. Nada é movido antes da quebra. Simulei por PYTHONIOENCODING; não testei em Windows. AVAL-20 Q10, AVAL-24.
- **L15.** "Quieto" ignora edição sem commit, e documento novo não rastreado conta 10^6 dias. O grupo se parte: DEFINE movido, DESIGN novo fica. Destino falso `_REPORTS_0000-00`. AVAL-20 Q6, Q7.
- **L16.** Arquivo rastreado com nome NFD aparece como "não rastreado: pulo". AVAL-20 Q1.

## Não coberto

- `gh` real, rede, Linux e Windows.
- O gate do DEFINE e a suíte inteira.
- AT-038.
- Estado como diretório: o bloqueio do harness a `rm` derrubou essa sonda; refiz sem ela.

## Para ler os logs

- `[exit=1]` em AVAL-02, 17 e 20 vem do último comando da sonda, não do script.
- Em AVAL-02, a falta do DRIVE_REPORT é esperada: `concluir` real parou no report-lint.
- A seção R1 de AVAL-23 está inválida: meu `=>` num `echo` criou arquivo e gerou COMMITAR. Vale AVAL-27.
- R1 e R2 de AVAL-22 foram mascarados pelo orçamento. Valem AVAL-23 R2 e AVAL-27.
- `rc=141` em AVAL-24 é SIGPIPE do meu `head`. Vale AVAL-25.
- O último caso de AVAL-09 foi mascarado por L2. Vale AVAL-22 R4.
- AVAL-00 e AVAL-16 são versões parciais dos ajudantes. Vale AVAL-29.

## Estado da árvore

- Só gravei AVAL-00 a AVAL-29 de propósito. Sem código alterado, `__pycache__`, push ou rede.
- Apareceu `sdd/traces/F14_DRIVE.jsonl`, com uma linha de 21:17:21Z: `verify-gate` sobre o DEFINE, exit 0, `src: verify-gate`. Não rodei esse comando nesse DEFINE nem nesta pasta. Provavelmente é o gate da outra sessão, mas não confirmei.
- Sobras para remover à mão, porque o harness bloqueia `rm` em script: `/var/folders/_s/_r8ph5yx5vgbqp_knw08v1380000gn/T/tmp.RRzJHrBpTz` e as pastas `tmp.*` que as sondas criaram em `/var/folders/_s/_r8ph5yx5vgbqp_knw08v1380000gn/T/`.
>>>
