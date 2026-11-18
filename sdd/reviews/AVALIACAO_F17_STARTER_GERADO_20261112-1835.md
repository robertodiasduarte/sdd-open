# Avaliação em contexto fresco — F17_STARTER_GERADO, ciclo 1 (bloco verbatim)

<<<AVALIACAO
FEATURE: F17_STARTER_GERADO · ciclo 1 · modo veredito · HEAD avaliado: 4b6a2df (branch feat/f17-starter-gerado)

VEREDITO: NEEDS_WORK

Por quê: 9 dos 10 ATs passaram por execução, e o Verify Gate ficou verde. O AT-004 passou só em parte, pela letra do DEFINE. O DEFINE (o contrato) manda o lint reprovar `.agents/skills/<nome>/` como caminho de leitura. O DESIGN (Decision 11) estreitou isso para "só as skills que o starter não recebe", e o DEFINE v1.1 não foi ajustado. Por causa desse buraco, a saída gerada leva ao aluno um comando que não existe numa instalação do Claude Code. Isso piorou em relação ao starter v1.5.16 (ACHADO 1). Se o Roberto aceitar o estreitamento e emendar o AT-004, o veredito passa a PASS_PENDENTE_RECIBO, e o ACHADO 1 fica como conserto recomendado antes da 1ª geração real.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| Verify Gate | o `cmd` do DEFINE, literal | exit 0 | publish-gate GREEN; `Ran 2082 tests in 1752.867s OK (skipped=1)`; rc=0 | PASS |
| AT-001 | gerar-starter.py --tag v9.9.0 num clone v1.5.16 (Python 3.9.6) + git diff --stat nas 8 congeladas, docs, exemplos, tests, LICENSE, NOTICE, CONTRIBUTING | exit 0; 10 skills + README, scripts e workflows; o resto byte a byte igual | rc=0, as 10 com ✅, diff vazio no resto; marca na árvore de trabalho do Open sem commit não chega ao destino; sem import de rede; grava também .gitattributes e GERADO.txt na raiz (Decision 11) | PASS |
| AT-002 | 13 casos, cada um seguido de git status --porcelain | 64 / 65 com a causa; nada gravado | tag inexistente 64 · pasta vazia 64 · sem check-versions.py 64 · sem git 64 · mudança não commitada 64 · não rastreado 64 · troca 0 vez 65 · troca 12 vezes 65 · sem linha no openai.tsv 65 · lint .md 65 · lint .sh 65 · versão que não sobe 65 · gerador ≠ o da tag 64; status limpo em todos | PASS (ver ACHADO 2) |
| AT-003 | probes/at003.py nas 10 skills | todas as propriedades | 99 OK; os 5 FAIL da sonda triados, nenhum defeito do produto | PASS |
| AT-004 | --lint na cópia crua; --lint na gerada; um arquivo por padrão | crua vermelha; gerada verde; cada padrão com arquivo:linha | crua rc=65 (36 achados); gerada rc=0; 13 padrões reprovados; porém `.agents/skills/sdd-kb/scripts/kb_normativo.py` (skill GERADA) não reprova em .md nem em .py | FAIL parcial (ACHADO 1) |
| AT-005 | 2 gerações em TMPDIR diferentes; diff -r; grep de caminho da máquina | idêntico | diff_rc=0; nenhum /private, /Users ou scratchpad; modo = o da tag | PASS |
| AT-006 | 16 casos + 1 refeito | 1 com o caminho; 0 sem mudança | mudou/falta/sobra em skill, scripts/, workflows, README, .gitattributes ⇒ 1; GERADO.txt da raiz apagado, skill apagada, GERADO da skill recalculado ou apagado ⇒ 1; ilegível 64; congelada editada 0; __pycache__ 0; sem mudança 0; workflows rodam a trava antes dos testes | PASS |
| AT-007 | os passos do ci.yml no clone gerado e commitado | tudo 0 | check-gerado VERDE · publish-check PASS · check-versions --base v1.5.16 (e --base-obrigatoria) PASS, 18 skills · py_compile · bash -n · testes das skills OK · gate.sh VERDE · tests/ da raiz 62 OK · package.sh 18 zips | PASS |
| AT-008 | collect_evidence.py com AGENTS.md, .agents/ e .codex/, contra o de main; grep da new-session | HEAD acha; main não | HEAD: os 5 itens; main: os 5 ausentes; new-session com pré-voo à mão, skills fora do git e "Por que" | PASS |
| AT-009 | git grep rdd-audita-schema; grep do molde; baseline em main | vazio | vazio; em main 3 arquivos e 2 linhas no molde | PASS |
| AT-010 | skill-lint, check-versions, test_agnostico, init + find, doctor com e sem openai.yaml | verde; aviso só com a skill do starter; nada de scripts/starter no projeto | 21/21; VERDE; 7 OK; init sem scripts/starter; aviso nos 2 casos, ausente no controle | PASS |

ACHADOS

1. [MEDIUM — viola o AT-004 pela letra; piora em relação ao v1.5.16] A sdd-kb gerada manda o aluno usar caminhos e conceitos que só existem no Open: `.agents/skills/sdd-kb/` sobra nos scripts gerados (gate.sh, kb_normativo.py, validate_kb.py), e o texto do `sync` sobra no SKILL.md (:32, :303); `skills/sdd-engenharia-reversa-saas/SKILL.md:116` virou condição sempre verdadeira; `skills/sdd-higiene-dado/scripts/pre-commit.sh:103` com o caminho de desinstalar. Reprodução: validate_kb.py de `.claude/skills/sdd-kb` manda rodar `python3 .agents/skills/sdd-kb/scripts/kb_normativo.py rule-map <domain>`, que não existe (rc=2). Prova do buraco no lint: um .md e um .py com `.agents/skills/sdd-kb/scripts/kb_normativo.py` passam no --lint (AVAL-AT-004-padroes.log).
2. [LOW] O conserto sugerido no exit 64 "gerador difere da tag" (git show … > /tmp/g.py) não funciona: RAIZ_OPEN sai de __file__ (AVAL-ACHADO-conserto-gerador-da-tag.log).
3. [LOW, observação] skills/sdd-kb/scripts/gate.sh perde o bit de execução (100755 → 100644) na 1ª geração; todo uso conhecido é `bash …/gate.sh`.

Evidência: sdd/reports/evidence/F17_STARTER_GERADO/AVAL-*.log (verify-gate, AT-001…AT-010, os 2 ACHADO).
>>>
