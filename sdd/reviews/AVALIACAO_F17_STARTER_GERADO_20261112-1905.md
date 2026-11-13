# Avaliação em contexto fresco — F17_STARTER_GERADO, ciclo 2 (bloco verbatim, resumido nas sondas longas)

<<<AVALIACAO
FEATURE: F17_STARTER_GERADO · modo: veredito · ciclo: 2 · HEAD avaliado: ec557ad

VEREDITO: PASS_PENDENTE_RECIBO

Os 10 ATs passam quando executados (repositório temporário com git archive HEAD + tag v9.9.0; clones temporários do
starter v1.5.16). Os dois achados do ciclo 1 estão consertados e foram reproduzidos de novo. Pendente dos recibos que o
DEFINE põe fora do gate: 1ª geração no clone real do starter; PR, CI e Release do starter com OK do Roberto; CI do PR nas 3
plataformas; Release do Open; D6.

| AT | Resultado | Observado (resumo) |
|---|---|---|
| AT-001 | PASS (achado 1) | rc 0; mudaram só as 10 skills, README, 2 scripts, 3 workflows, mais GERADO.txt e .gitattributes; congeladas, docs, exemplos, tests, LICENSE, NOTICE, CONTRIBUTING intactos; lixo na árvore de trabalho do Open não aparece; rede cortada por sandbox-exec e a geração sai igual |
| AT-002 | PASS | 64/65 com a causa em todos os casos; hash do destino idêntico antes e depois; controles 0 |
| AT-003 | PASS (achado 2) | 120 checagens ok; o compatibility da sdd-seguranca é reescrito por troca |
| AT-004 | PASS (achado 3) | crua 65 com 72 linhas; gerada VERDE; os 12 padrões reprovam; o par passa; fora do par reprova; README e workflow reprovam |
| AT-005 | PASS | diff -r vazio com outro caminho, TZ e locale |
| AT-006 | PASS | 18 adulterações ⇒ 1 com o caminho; ilegível 64; __pycache__ e congelada 0; trava é o 1º passo dos 3 workflows |
| AT-007 | PASS | passos do ci.yml no clone gerado e commitado: todos 0 (18 skills, gate.sh VERDE, 25 testes do Open OK em git archive) |
| AT-008 | PASS | só .agents/skills: 2 itens (v2.12.1: 0); com tudo: 6 tipados (v2.12.1: 0); precedência citada |
| AT-009 | PASS | greps vazios; 4 sabotagens fazem o teste falhar |
| AT-010 | PASS | skill-lint 21 ✅; agnóstico OK; check-versions VERDE; init sem scripts/; doctor avisa nos dois lugares e cala no limpo |

ACHADOS (todos baixos, de letra; nenhum bloqueia)
1. AT-001 diz "exatamente" e "tudo o mais byte a byte igual", mas o gerador cria .gitattributes (decisão do DESIGN, não do DEFINE).
2. AT-003 diz "o frontmatter da skill do Open", mas o compatibility da sdd-seguranca é reescrito por troca (nome, descrição e versão intactos).
3. AT-004: (a) lint-aceitos.tsv isenta 3 linhas do alarme.sh (decisão do DESIGN); (b) o padrão exige a barra, então "sdd/hooks" sem barra passa em ~15 linhas condicionais da higiene-dado.
4. gate.sh da kb perde o bit de execução (100755 → 100644): o modo vem da tag; todo uso é `bash …`.

NAO_VERIFICADO: GitHub Actions de verdade e as 3 plataformas; CRLF no Windows; a geração no clone real; PR e Release do starter, Release do Open, D6.
Evidência: sdd/reports/evidence/F17_STARTER_GERADO/AVAL2-*.log (20 logs).
>>>
