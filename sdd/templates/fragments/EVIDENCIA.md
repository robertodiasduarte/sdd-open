# Fragmento — Prova de evidência (default-FAIL no BUILD_REPORT)

> Reusável. Lido por `/build` (Step 6), pelo `avaliador-fresco` (C1) e pelo hook
> `.githooks/claude-build-report-guard.py` (PreToolUse em `Write|Edit`). É o **dono único**
> do formato de evidência: as superfícies apontam pra cá, nunca copiam o texto normativo.

## Por que existe

O BUILD_REPORT anterior a este contrato aceitava `✅ Por raciocínio` como evidência de
aceite — 9 ATs de uma feature real fecharam assim (`BUILD_REPORT_ZOOM_PRAZO_LIBERACAO_GRAVACAO`).
Uma feature foi para produção com "Enviar não faz NADA" e o relatório inteiro verde. **Auto-avaliação
por leitura de diff não é evidência.** Aqui o "done" vira estrutura:

1. Todo critério de aceite **nasce `false`** no BUILD_REPORT.
2. Virar `true` exige **evidência lida** — output real de comando/teste/clique, num arquivo
   que o hook consegue abrir e conferir. Sem arquivo, o hook **nega a escrita** do report.
3. Evidência é o que um terceiro consegue reproduzir; "o código faz X" é declaração, não prova.

Landmines que este contrato materializa: *asserção de FIAÇÃO ≠ COMPORTAMENTO* (grep de código
fica verde com `if (true)`) · *régua validada contra o par que a construiu é CIRCULAR*.

## Onde a evidência mora

```text
sdd/reports/evidence/{FEATURE}/
├── AT-001.log        # 1 arquivo por critério (AT-nnn do DEFINE)
├── AT-002.log
├── GATE.log          # output do sdd/bin/verify-gate.sh
└── AVAL-roteiro-3.log  # passos do avaliador (C1) — prefixo AVAL-
```

Versionado junto com o report (é rastreabilidade, não lixo). **Teto: 200 linhas por
arquivo** (`| tail -n 200`) — evidência é o trecho que prova, não o log inteiro.

## Formato do arquivo de evidência (o hook confere)

- **1ª linha = o comando executado, prefixado por `$ `.**
- Depois, o output **verbatim** (stdout+stderr).
- Arquivo vazio, sem a 1ª linha `$ `, ou inexistente → o hook nega.

Como produzir (o `$ cmd` na 1ª linha vem do próprio comando, não de mão):

```bash
mkdir -p sdd/reports/evidence/{FEATURE}
cmd='npm test -- src/x.test.ts'
{ echo "\$ $cmd"; eval "$cmd" 2>&1 | tail -n 200; } > sdd/reports/evidence/{FEATURE}/AT-001.log
```

## A tabela do BUILD_REPORT (formato que o hook parseia)

```markdown
| ID | Critério (EARS) | Resultado | Evidência |
|----|-----------------|-----------|-----------|
| AT-001 | When X, the system shall Y | false | — |
| AT-002 | If Z, then the system shall W | true | `evidence/{FEATURE}/AT-002.log` |
| AT-003 | manual-ux: fluxo no celular | true | recibo: nome 2026-08-28 · `AVALIACAO_{FEATURE}_20260828-1530.md` |
```

**`Resultado` aceita `true` \| `false`** (também ✅/❌, mas prefira o booleano). O hook só
inspeciona linhas com `true`/✅ — `false` passa livre (é o default honesto).

### O que conta como evidência para `true` (uma das três)

| Forma | Quando | O hook confere |
|---|---|---|
| `` `evidence/{FEATURE}/AT-nnn.log` `` | critério com `cmd` (test/smoke/eval/typecheck) | path contém `evidence/{FEATURE}/` **da mesma feature do report**, `.log`/`.txt`, existe, não-vazio, 1ª linha começa com `$ ` |
| `` `AVALIACAO_{FEATURE}_{ts}.md` `` | critério provado pelo avaliador de contexto fresco (C1) — inclusive cliques | nome começa com `AVALIACAO_{FEATURE}_` e existe em `sdd/reviews/` |
| `recibo: {nome} {YYYY-MM-DD}` | gate `manual-ux` percorrido por humano | padrão textual (nome + data ISO) **e** `DEFINE_{FEATURE}.md` com `kind: manual-ux` (DEFINE ausente → aceita com aviso) |

Evidência de OUTRA feature, `README.md` com `$ ` na 1ª linha, recibo em feature com gate
`test` — tudo negado (buracos fechados no review adversarial de 28/08). Critério com `|` no
texto: escape como `\|` (o hook respeita e conta as colunas a partir do fim da linha).

### O que o hook NEGA sempre

- `true` sem nenhuma das três formas acima.
- Evidência contendo `por raciocínio`, `by reasoning`, `by inspection`, `deve funcionar`,
  `provavelmente` — declaração fantasiada de prova.
- `**Veredito do avaliador (C1):** PASS` ou `NEEDS_WORK` sem citar um
  `AVALIACAO_*.md` existente. (`N.A.` com motivo — ex. "1 camada" — passa.)

## Regras de ouro

1. **Evidência ≠ conclusão.** O arquivo contém o output; a conclusão (`true`) fica na tabela.
   Se o output não sustenta o `true`, o reviewer vê a contradição — é o objetivo.
2. **Nada de evidência "compartilhada"** entre ATs sem justificativa: 1 AT = 1 arquivo, ou
   cite o mesmo arquivo em cada linha (o hook aceita; o revisor questiona).
3. **`manual-ux` não é atalho.** Recibo humano vale para o que um humano percorreu; se o
   avaliador C1 clicou, cite o `AVALIACAO_*.md` — não o recibo.
4. **O hook falha ABERTO em erro interno** (bug de parser não pode travar todo report), mas
   registra `systemMessage` — se aparecer, o guard não conferiu nada; trate como não-conferido.
5. **Bypass é decisão do humano responsável**, não do agente: pular o `report-lint.py`
   da sessão desliga o hook — e isso vai declarado no BUILD_REPORT e no resumo da sessão.
