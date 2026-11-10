# DEFINE: F19 — Custo e benefício dos modelos de revisão

> Um ledger por frente com a decisão de cada achado e a marca de dano, um lint que o confere, e um medidor só de leitura (`sdd/bin/eval-revisores.sh`) que junta custo e resultado por papel, engine e modelo.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F19_CUSTO_REVISORES |
| **Date** | 2026-11-10 |
| **Author** | define-agent (worktree `sdd-open-f21-f19`; branch `feat/f19-custo-revisores`, de `origin/main` depois da `v2.9.0`) |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |

---

## Problem Statement

A cadeia de revisão adversarial é escolhida por impressão. O custo de cada engine está espalhado em um `META.txt` por rodada, a decisão por achado (aplicado, rebatido) está num ledger de 5 colunas por frente sem a marca de dano e sem a pasta da rodada em cada linha (F10 a F14) ou só numa tabela do BUILD_REPORT (F15 e F21), o custo de assinatura não se separa do custo pago, e "falha real que poderia causar dano" não tem critério escrito. Nas 25 rodadas de F13 a F21 ninguém sabe dizer quanto custou cada falha real achada por cada engine.

---

## Target Users

| User | Role | Pain Point |
|---|---|---|
| Quem paga a revisão | escolhe `review.revisor1`, `review.auditor` e o 2º revisor | não sabe quanto cada engine custou nem o que ela achou que valia o conserto |
| Quem decide os achados | registra APLICADA ou REBATIDA depois de cada rodada | o registro muda de lugar e de formato a cada frente (ledger na evidência, ou tabela no relatório) e não diz se a falha causaria dano |
| Mantenedor do Open | mantém o `registry.tsv` | não tem número para dizer se o 2º revisor ou uma engine que falha por cota vale o que custa |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | critério de "falha real com dano" escrito em `sdd/review/CRITERIO_DANO.md` |
| **MUST** | ledger da revisão por frente, `sdd/reviews/LEDGER_REVISAO_{F}.md`, com a coluna `dano` e a pasta da rodada, e um lint (`sdd/bin/ledger-revisao-lint.sh`) |
| **MUST** | `sdd/bin/eval-revisores.sh`, só de leitura e sem rede: uma linha por papel + engine + modelo, com rodadas, falhas por motivo, custo pago, custo nominal, achados, aplicados, com dano, falsos positivos, sem classificar, custo por falha com dano e taxa de AGREE |
| **MUST** | `sdd-build` e `sdd-release` pedem o ledger e o lint no lugar da tabela solta |
| **MUST** | `docs/adversarial-review.md` + PT explicam como ler a tabela; `docs/cli-conventions.md` com os exits |
| **SHOULD** | relatório retroativo de F13 a F15 + F21, com a amostra por engine (branch de documentos, fora do gate) |
| **COULD** | saída em JSON (fica para depois) |

---

## Success Criteria

- [ ] `bash sdd/bin/eval-revisores.sh sdd/fixtures/revisao/custo` sai 0, sem rede, e imprime a tabela com as linhas e os números esperados das fixtures (valores fixados nos testes).
- [ ] As fixtures reproduzem 5 casos reais com dados inventados: o mesmo modelo por 2 provedores com custo diferente; engine que falha por credencial (exit 65); engine que falha por cota ou tempo (exit 67); revisor por assinatura com custo nominal e pago zero; auditor que repete um achado NOVO rebatido em 2 rodadas.
- [ ] `ledger-revisao-lint.sh` sai 2 em 7 fixtures, cada uma por 1 motivo nomeado, e 0 no controle, no retroativo e no arquivo só com rodadas sem achados.
- [ ] Linha de base vermelha: os testes novos falham em `origin/main` antes da frente.
- [ ] 3 sabotagens (soma do pago, regra do `dano: sim`, contagem de falso positivo) derrubam, cada uma, um teste nomeado.
- [ ] Verify Gate numa cópia de `git archive` sai 0 com a suíte inteira (a contagem só sobe).
- [ ] Retroativo (fora do gate): `sdd/reports/RETROATIVO_REVISORES_2026-11-10.md` na branch de documentos, com as 25 rodadas, a amostra por engine e a declaração de que F10 a F12 ficaram fora.
- [ ] Release `v2.10.0` publicada com `SHA256SUMS.txt` conferido.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Event-driven | **When** `bash sdd/bin/eval-revisores.sh [<pasta-das-revisões>] [--ledgers <pasta-ou-arquivo>]` roda sobre pastas `EXTERNAL_REVIEW_*` com `META.txt`, o script **shall** imprimir uma tabela com uma linha por papel (`revisor`, `2º revisor`, `auditor`, `desempate`) + engine + modelo como o `META.txt` o registra (com o provedor), ordenada por papel e engine, terminar em `RESULTADO: MEDIDO` + `→` e sair 0; o padrão da pasta é `review.output_dir` do `sdd/config.yaml` (`sdd/reports/reviews` se vazio) e o dos ledgers é `sdd/reviews/` | test |
| AT-002 | Ubiquitous | Para cada linha, o script **shall** somar em **pago** só o custo numérico das chamadas cuja engine o `registry.tsv` marca `pay-per-token`, e em **nominal** todo custo numérico (`US$ n` reportado ou `≈US$ n` estimado), inclusive de engine `assinatura`; de um custo `US$ n + $?` (a engine estourou o tempo) o `n` **shall** entrar na soma, com o aviso `incerto em N de M`; custo `assinatura` sem valor, `$?` e `n/d` **shall** contar como chamada sem custo informado, mostrada ao lado (`n/d em N de M`), nunca como zero; engine `assinatura` mostra pago `0.0000` e engine de cobrança desconhecida mostra pago `n/d`; as somas **shall** usar aritmética decimal exata (0.3100 + 0.3000 imprime 0.6100), com 4 casas, ou 6 quando o valor é menor que 0,0001; o sinal `≈` e a ressalva **shall** acompanhar também o custo por falha com dano, que sai nas duas bases e é `—` quando não há falha com dano | test |
| AT-003 | Ubiquitous | O script **shall** contar por linha: **achados** (linhas do arquivo de vereditos do papel; `NOVO` para o auditor), **aplicados** (`APLICADA` no ledger), **com dano** (`dano` = `sim`), **falsos positivos** (`REBATIDA_EVIDENCIA`), **fora de escopo** (`REBATIDA_ESCOPO`) e **sem classificar** (achado sem linha no ledger, ou `dano` = `?`), ligando cada linha do ledger ao papel pela pasta da rodada e pelo id do achado; e, para o auditor, a taxa de AGREE com a mesma conta do `eval-agree.sh`; toda taxa **shall** vir com a amostra (`3 de 7`) | test |
| AT-004 | State-driven | **While** uma chamada de engine tem exit diferente de 0 no `META.txt`, o script **shall** contá-la em **falhas**, separadas por motivo (`credencial` = 65, `cota ou tempo` = 67, `resposta inválida` = 68, `outro`), fora das rodadas com resposta e sem achados; o custo dela, quando informado, **shall** entrar no pago e no nominal (engine cobrada sem responder); quando o `META.txt` diz que a engine prevista falhou e outra respondeu (`<papel>_fallback_usado: sim`), a prevista **shall** ganhar uma falha `trocada por outra engine` na linha dela; um papel marcado `indisponível` (nenhuma engine chamada) **shall** ir para "fora da conta", sem virar linha de engine | test |
| AT-005 | Unwanted | **If** a pasta passada não existe, ou há argumento desconhecido, **then** o script **shall** sair 64 com a causa e o conserto; **if** não há nenhuma pasta com `META.txt` legível (ou a pasta padrão ainda não existe), **then** **shall** sair 2 com `RESULTADO: SEM DADOS`; **if** uma linha de dados do ledger não entra na conta (menos ou mais de 7 células, veredito fora da lista, revisão que não é pasta `EXTERNAL_REVIEW_*`, achado que não existe na pasta, achado repetido, rótulo `@engine` que não é o da engine que respondeu naquele papel), **then** o script **shall** listá-la em "fora da conta" com `arquivo:linha` e o motivo, e nunca descartá-la em silêncio; uma pasta sem linha em nenhum ledger **shall** ter custo e achados contados (os achados em "sem classificar") e ser avisada em "fora da conta"; também **shall** ser avisados ali: `dano` fora da lista, exit ilegível no `META.txt` (a chamada e o custo não contam), papel que respondeu sem arquivo de vereditos, e ledger que diz `sem achados` para uma revisão que tem achados; pasta que não se deixa ler e argumento vazio **shall** sair 64, nunca com traceback; o script **shall** não abrir conexão de rede nem chamar engine | test |
| AT-006 | Event-driven | **When** `bash sdd/bin/ledger-revisao-lint.sh <arquivo.md>…` roda, o script **shall** tratar toda linha de tabela do arquivo, inclusive dentro de bloco cercado e de comentário (o `loop` as lê), como do ledger; bloco cercado se reconhece como no CommonMark (3 ou mais crases ou tis, qualquer rótulo; fecha com o mesmo caractere, em quantidade igual ou maior, sem rótulo) e nele só as marcas de texto deixam de valer (o cabeçalho do molde, que pode se repetir entre rodadas, ou uma linha de dados; outra tabela no arquivo reprova, e nenhuma linha de tabela é pulada) ; uma linha fora da tabela com forma de linha do ledger (a barra inicial ausente, ou atrás de citação, item de lista ou barra invertida) **shall** reprovar, e um bloco cercado ou comentário aberto e não fechado também; e sair 0 se cada linha de dados tem as 7 células `achado` (o id como está no arquivo de vereditos: `R<n>` ou `N<n>`, com `@<engine>` opcional), `sev` (`HIGH`, `MED`, `LOW`), `veredito` (`APLICADA`, `REBATIDA_EVIDENCIA`, `REBATIDA_ESCOPO`), `rodada=<N>`, evidência não vazia, `dano` (`sim`, `nao`, `?`) e a pasta `EXTERNAL_REVIEW_<AAAAMMDD-HHMMSS>` (com `-<n>` quando o nome colidiu); uma rodada sem achados **shall** ser registrada pela linha `sem achados: rodada=<N> EXTERNAL_REVIEW_…`, que conta como conferida; e **shall** sair 2 com `arquivo:linha — motivo` quando: falta a célula `dano`; `dano` = `sim` sem `teste: <nome com forma de teste>` na evidência; `dano` = `sim` com veredito diferente de `APLICADA`; `dano` = `?` num arquivo sem a linha `retroativo: sim` (sozinha, fora de cerca; as quase-formas reprovam com a forma certa na mensagem); veredito, severidade, rodada ou pasta fora do formato; cabeçalho fora do molde, conferidos os 7 nomes (uma mensagem só); o mesmo achado repetido na mesma revisão, no mesmo arquivo ou entre os arquivos passados; uma revisão marcada `sem achados` que também tem linha de dados; 64 em uso, arquivo ilegível (lido antes de conferir qualquer um) ou, sem nenhuma violação a mostrar, arquivo sem linha de dados e sem linha `sem achados:` | test |
| AT-007 | Non-regression | O `sdd-fluxo.sh loop --ledger` **shall continue to** ler o ledger pelas 4 primeiras células (`achado`, `sev`, `veredito`, `rodada=N`): um ledger no formato novo, de 7 colunas, que o lint aprova, **shall** fechar um achado HIGH como o de 5 colunas fecha, tanto numa revisão com ids rotulados (`R1@rev`) quanto numa de um revisor só, com ids sem rótulo (`R1`, `N1`); o `eval-agree.sh` e o `adversarial-review.sh` **shall continue to** passar nos testes que já têm, sem mudança de contrato | test |
| AT-008 | Ubiquitous | O pacote **shall** trazer `sdd/review/CRITERIO_DANO.md` (o critério, quem marca, os 3 valores, o que é falso positivo, exemplos dos dois lados) e `sdd/templates/LEDGER_REVISAO_TEMPLATE.md`; a `sdd-build` (passo 5c) **shall** mandar gravar `sdd/reviews/LEDGER_REVISAO_{F}.md`, rodar o lint e passar esse arquivo ao `loop --ledger`, e a `sdd-release` (0a, item 8) **shall** mandar conferir o lint desse arquivo antes de publicar (o `loop` é do build), as duas com bump de versão; `docs/adversarial-review.md` e `docs/pt-BR/adversarial-review.md` **shall** ter a seção do medidor com as colunas e os limites (amostra pequena, sem juiz, o que o custo nominal é); `docs/cli-conventions.md` **shall** ter a linha de cada script; `sdd/WORKFLOW_CONTRACTS.yaml` e `MANIFEST.txt` **shall** listar os arquivos novos | test |
| AT-009 | Event-driven | **When** `bash bin/sdd-open.sh init --vendors claude --yes` roda num projeto novo, o projeto **shall** receber `sdd/bin/eval-revisores.sh`, `sdd/bin/ledger-revisao-lint.sh`, `sdd/review/CRITERIO_DANO.md` e o molde do ledger, e `bash sdd/bin/eval-revisores.sh` nesse projeto, ainda sem revisões, **shall** sair 2 com `RESULTADO: SEM DADOS` | test |

Considerados: **While** em AT-004 (o estado "a chamada falhou" muda o que se conta); **If/Then** em AT-005 e nas reprovações de AT-006; **Where** — N.A.: não há recurso opcional ligado por configuração (a pasta e os ledgers são argumentos). Não-regressão em AT-007, porque a frente cria um formato que o `loop` também lê.

O relatório retroativo não é AT: são dados reais transcritos à mão, na branch de documentos. A conta dele é a do AT-001 a AT-005, que as fixtures provam.

---

## Clarifications

### Session 2026-11-10

- [x] (terminologia) "Falha real com dano" → achado APLICADO, com teste que falha no código antigo, cujo cenário afeta dado, dinheiro, acesso, publicação ou disponibilidade; marcado por quem decide o achado (brainstorm, pergunta 1); integrado em AT-006 e AT-008.
- [x] (dados) Onde mora a decisão → `sdd/reviews/LEDGER_REVISAO_{F}.md` (pergunta 2); integrado em AT-006.
- [x] (dados) Ordem das colunas → as 5 primeiras são as que o `sdd-fluxo.sh loop` já lê (`achado`, `sev`, `veredito`, `rodada=N`, evidência); `dano` e a pasta da rodada vêm depois. No brainstorm a tabela foi mostrada com `dano` antes de `rodada`; a ordem mudou para o `loop` não precisar mudar. Mesmas informações; integrado em AT-006 e AT-007.
- [x] (escopo) Só informa, sem sugerir cadeia (pergunta 3).
- [x] (NFRs) Duas colunas de custo; "n/d" nunca vira zero (pergunta 4); integrado em AT-002.
- [x] (escopo) Retroativo F13 a F15 + F21, `dano` `?` com `retroativo: sim`; privado depois da F15 (perguntas 5 e 6).
- [x] (dados, correção) Os ledgers de 5 colunas de F10 a F14 existem em `sdd/reports/evidence/{F}/ledger-review.md` na branch de documentos; o brainstorm dizia que não. O retroativo converte os de F13, F14 Playbook e F14 Drive (as rodadas arquivadas) e transcreve F15_SLOTS e F21; F10 a F12 têm ledger mas não têm as pastas das rodadas, e continuam fora.
- [x] (edge cases) Chamada que falhou e foi cobrada → conta no custo e em falhas, não em rodadas com resposta; integrado em AT-004.
- [x] (integrações) P2: nomes de engine vêm do `META.txt` e do `registry.tsv`; nenhum nome de engine no texto das skills.
- [x] (UX) Sem interface: saída de terminal no padrão de `docs/cli-conventions.md`. UX review pulado.
- [x] (sinal de conclusão) Verify Gate + retroativo gravado.
- [x] (avaliação ciclo 1 e revisão adversarial, 2026-11-10) A regra "só a tabela cujo cabeçalho começa por `achado`" regrediu duas vezes (linha depois de linha em branco; id entre crases ou segundo cabeçalho): trocada pela regra estrutural "o arquivo é só do ledger" (LM-005); integrado em AT-006 e AT-005 (v1.2).
- [x] (revisão do DESIGN, 2026-11-10) 17 notas do revisor fresco, 2 HIGH; as que mudam o aceite entraram aqui (v1.1): AT-002 (custo `US$ n + $?`, 6 casas, `≈` no custo por dano), AT-004 (engine trocada, papel indisponível), AT-005 (nenhuma linha some em silêncio; rótulo errado; repetição; pasta sem ledger conta e é avisada; saiu o caso "nome de pasta repetido", que o script de uma pasta só não tem como ver), AT-006 (id como está no arquivo de vereditos, com `@engine` opcional; linha `sem achados:`; só a tabela do ledger, fora de cerca; forma única do `retroativo: sim`; pasta com sufixo de colisão; repetição entre arquivos) e AT-007 (revisão de ids sem rótulo). Ledger completo no DESIGN.

### Session 2026-11-10 (governança)

- [x] (governança) dispensada — o revisor fresco achou tema de dinheiro (soma de custo em US$) e devolveu `PADRAO_AUSENTE` (o repositório do pacote não tem `sdd/GOVERNANCA_PADRAO.md`); o Roberto dispensou em 2026-11-10: o medidor só lê e soma custos já registrados de uma ferramenta de desenvolvimento, sem lançamento, saldo, nota nem dado pessoal. Dois cuidados do catálogo entram mesmo assim: soma com aritmética exata (decimal) e "sem custo informado" nunca vira zero, cada um com teste (AT-002).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 a AT-005 em `tests/test_eval_revisores.py` (fixtures de `sdd/fixtures/revisao/custo/`); AT-006 em `tests/test_ledger_revisao_lint.py` (fixtures de `sdd/fixtures/revisao/ledger/`); AT-007 em `tests/test_fluxo.py` (caso novo com o ledger de 7 colunas) mais `tests/test_eval_agree.py` e `tests/test_revisao.py` verdes; AT-008 e AT-009 em `tests/test_f19_textos.py`.

---

## Out of Scope

- Medir o repositório privado; reprocessar F10 a F12.
- Sugerir ou trocar a cadeia no `registry.tsv`.
- Saída em JSON ou CSV, gráfico, coluna de tempo.
- Outro modelo classificando o dano.
- Mudar o `adversarial-review.sh`, o `eval-agree.sh` ou o parser do `sdd-fluxo.sh loop`.
- `.gitignore` do repositório (pendência da F21).

---

## Constraints

| Type | Constraint | Impact |
|---|---|---|
| Technical | bash 3.2 + Python ≥ 3.9 stdlib; sem rede; só leitura | `tests/test_bash32.py`; o teste confere que o script não importa módulo de rede |
| Technical | `docs/cli-conventions.md`: erro com causa e conserto, `RESULTADO:` + `→` | os dois scripts |
| Público | fixtures com dados inventados; nada de outro repositório | `publish-gate.sh` |
| Método | sem viés de juiz: o script conta o que está registrado | nenhum modelo é chamado |
| Método | amostra pequena dita ao lado de cada taxa | AT-003 |
| Skills | skill tocada sobe `metadata.version` | `sdd-build` e `sdd-release` |
| Processo | `git add` por caminho; suíte com `-B` | lição da F21 |

---

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/eval-revisores.sh`, `sdd/bin/ledger-revisao-lint.sh`, `sdd/review/CRITERIO_DANO.md`, `sdd/templates/LEDGER_REVISAO_TEMPLATE.md`, `sdd/fixtures/revisao/custo/`, `sdd/fixtures/revisao/ledger/`, `.agents/skills/sdd-build/`, `.agents/skills/sdd-release/`, `docs/`, `sdd/WORKFLOW_CONTRACTS.yaml`, `tests/`, `MANIFEST.txt` | produto do Open |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/`; a skill `sdd-kb` cria uma base quando o projeto quiser |
| **IaC Impact** | None | CI existente |
| **LLM Prompts** | false | os scripts não chamam modelo; "engine" e "modelo" são dados lidos do `META.txt` |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | `contexto-lint.sh --sugerir` → PULAR |
| **Governança** | dispensada — medidor só de leitura de custo de ferramenta, sem lançamento, saldo, nota nem dado pessoal; aritmética exata e "n/d nunca é zero" aplicados no AT-002 | Roberto, 2026-11-10 |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | O `init` copia qualquer arquivo novo de `sdd/bin/`, `sdd/review/` e `sdd/templates/` | os scripts não chegariam ao projeto; AT-009 prova | [ ] |
| A-002 | Os campos `*_engine_efetivo`, `*_modelo`, `*_custo`, `*_exit` e `*_motivo` existem em todo `META.txt` desde a F10 (nas 21 rodadas arquivadas, sim; `revisor2_*` e `desempate_*` faltam quando o papel não rodou) | linhas incompletas; o script trata campo ausente como "papel não rodou" | [x] medido em 2026-11-10 |
| A-003 | O `loop` ignora células depois da 4ª | precisaria mudar o parser; AT-007 prova | [x] `sdd/bin/sdd-fluxo.sh`, leitura por célula `c[0..3]` |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | 4 lacunas nomeadas, com a medida das 25 rodadas |
| Users | 3 | 3 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 3 | números fixados nas fixtures, 6 reprovações, 3 sabotagens |
| Scope | 2 | retroativo fora do gate |
| **Total** | **14/15** | |

---

## Open Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-11-10 | define-agent | Initial version |
| 1.1 | 2026-11-10 | define-agent | notas da revisão fresca do DESIGN: AT-002, AT-004, AT-005, AT-006, AT-007 |
| 1.3 | 2026-11-10 | define-agent | avaliação ciclo 2 (B1 a B7): AT-006 e AT-005 passam a exigir que a linha com forma de linha do ledger **fora** da tabela (sem a barra inicial, atrás de citação ou item de lista) seja acusada pelo lint e avisada pelo medidor; cerca é só a linha inteira e bloco aberto sem fechar é acusado; dado corrompido no medidor sai 64 com a causa, nunca traceback; exit ausente com custo é avisado |
| 1.4 | 2026-11-10 | define-agent | revisão rodada 4 (R2, R3) e avaliação ciclo 3 (C1, C2): AT-008 separa o que é do build (gravar, lint, `loop --ledger`) do que é da release (conferir o lint); AT-006 passa a conferir a linha de tabela também dentro de bloco cercado e de comentário, porque o `loop` a lê, e reconhece a cerca como o CommonMark; a mensagem, a ajuda e o molde dizem como escrever texto corrido com 4 ou mais barras |
| 1.2 | 2026-11-10 | define-agent | revisão adversarial (rodadas 1 e 2) e avaliação ciclo 1: AT-006 passa a dizer que toda linha de tabela do arquivo é do ledger (a regra que escolhia "a tabela do ledger" deixou linha sem conferir duas vezes); AT-005 ganha os avisos novos e o 64 sem traceback |

---

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F19_CUSTO_REVISORES.md` — UX review pulado: a feature não tem interface (scripts de terminal, um arquivo de critério e texto de skill).
