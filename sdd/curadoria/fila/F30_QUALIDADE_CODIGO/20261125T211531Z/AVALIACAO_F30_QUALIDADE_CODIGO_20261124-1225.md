# AVALIACAO — F30_QUALIDADE_CODIGO (fatia S2) · ciclo 1 · 2026-11-24

> Bloco do avaliador de contexto fresco (subagente novo, modo `veredito`, ciclo 1), sobre `b4c9f55`/`cc5c5d3` (só o
> relatório mudou entre os dois). Conteúdo do bloco devolvido, com as células condensadas. Logs das sondas em
> `sdd/reports/evidence/F30_QUALIDADE_CODIGO/AVAL-S2-*.log`.

<<<AVALIACAO
VEREDITO: NEEDS_WORK

Os sete ATs passaram nas sondas (27 casos de report-lint, 21 de sabotagem.sh, textos e starter, gate sem a suíte). O veredito é NEEDS_WORK pelo N1, violação do AT-013 que se reproduz em cerca de 6 de 8 rodadas.

| AT | sonda | esperado | observado | resultado |
|---|---|---|---|---|
| AT-010 | AVAL-S2-AT-010-012.log: antes válido (exit 1 e 139), vazio, ausente, verde, 126, 127, outro comando, sem `[exit=`, sem `$`, N.A., ignorado, outra feature, outro AT | válido 0; demais 1 com 1 linha `→` | como esperado | PASS |
| AT-011 | continua verde, vermelho, vazio, N.A., outro comando; manual-ux com N.A. | verde 0, vermelho 1, N.A. só no manual-ux | como esperado | PASS |
| AT-012 | sem a coluna com e sem DEFINE; com a coluna sem DEFINE; relatório da S1 por `--stdin` | 0 com 1 aviso; sem DEFINE, aviso com a causa | como esperado | PASS |
| AT-013 | forte, fraco, edição não commitada, arquivo não rastreado, TERM no meio; hash e TMPDIR | 0 com log; 2 com a mensagem; árvore igual; cópia apagada | como esperado nas sondas; falha no cenário do N1 | NEEDS_WORK |
| AT-014 | trecho ausente/duplo/só na edição local; absoluto; `..`; link; diretório-link; fora do HEAD; já falha; 126; 127; uso; fora de git | 3 ou 64, sem log, árvore igual | como esperado | PASS |
| AT-015 | textos do Open, ordem Verificar < Refatorar < Marcar, config, starter gerado (15 arquivos sem `sdd/bin/`) | presentes | como esperado; 11 testes OK | PASS |
| AT-016 | check-versions, publish-gate CI na cópia, 6 módulos, `test_f30_*`, relatórios sem `Antes` | tudo 0 | tudo 0 (133 + 101 testes); suíte inteira não rodada | PASS (recibo pendente) |

ACHADOS
N1 (média) — o `sabotagem.sh` dava "o teste não pega o defeito" (exit 2) para um teste forte quando o commit e a sabotagem caíam no mesmo segundo: a execução sabotada reusava a cópia da limpa; o `git archive` grava o mtime como a hora do commit e a troca de mesmo tamanho no mesmo segundo deixava o Python reaproveitar o `__pycache__`. Reprodução no `AVAL-S2-bordas.log`, bloco B5 (6 de 8 com 2; com `-B`, 4 de 4 com 0).
O1 — com a evidência só em `AVALIACAO_*.md`, a 1ª linha do antes não era comparada com o `AT-nnn.log` do disco.
O2 — só o cabeçalho exato `Antes` era reconhecido; `Antes (vermelho)` caía no modo antigo.
O3 — um `AT-nnn.sabotagem.log` de sucesso antigo fica na pasta quando uma rodada nova sai 3 ou 64.
O4 — o exit 2 grava o log com o mesmo nome do de sucesso (a última linha distingue).
>>>

## Tratamento (build, 2026-11-24)

- N1: APLICADO em `f583124`: a execução sabotada ganha uma cópia nova do `git archive`; teste determinístico
  `test_cache_da_execucao_limpa_nao_esconde_a_sabotagem` (vermelho antes do conserto, verde depois); a reprodução do
  avaliador, sem `-B`, deu 0 em 6 de 6.
- O1 e O2: APLICADOS, com os testes `test_evidencia_so_pela_avaliacao_ainda_confere_o_comando` e
  `test_cabecalho_antes_com_complemento_ainda_e_a_coluna`.
- O3: mantido. Apagar o log antigo numa rodada 3/64 mudaria a árvore, contra o AT-014; a última linha `[exit=…]` e a
  linha `# sabotagem:` do log dizem de qual rodada ele é.
- O4: mantido. O log do exit 2 é a prova de que o teste é fraco, e termina em `[exit=0]`.
