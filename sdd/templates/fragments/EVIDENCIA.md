# Fragmento — Prova de evidência (default-FAIL no BUILD_REPORT)

> Reusável. Lido por `/build` (Step 6), pelo `avaliador-fresco` (C1) e pelo
> `sdd/bin/report-lint.py`, que confere o BUILD_REPORT. É o **dono único**
> do formato de evidência: as superfícies apontam pra cá, nunca copiam o texto normativo.

## Por que existe

O BUILD_REPORT anterior a este contrato aceitava `✅ Por raciocínio` como evidência de
aceite — 9 ATs de uma feature real fecharam assim (`BUILD_REPORT_ZOOM_PRAZO_LIBERACAO_GRAVACAO`).
Uma feature foi para produção com "Enviar não faz NADA" e o relatório inteiro verde. **Auto-avaliação
por leitura de diff não é evidência.** Aqui o "done" vira estrutura:

1. Todo critério de aceite **nasce `false`** no BUILD_REPORT.
2. Virar `true` exige **evidência lida** — output real de comando/teste/clique, num arquivo
   que o lint consegue abrir e conferir. Sem arquivo, o lint **reprova** o report (exit 1).
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

## Formato do arquivo de evidência (o lint confere)

- **1ª linha = o comando executado, prefixado por `$ `.**
- Depois, o output **verbatim** (stdout+stderr).
- Arquivo vazio, sem a 1ª linha `$ `, ou inexistente → o lint nega.
- Última linha: `[exit=N]`, com o exit **do comando**, capturado antes de qualquer pipe.
- O arquivo tem de ir para o commit: evidência que o git ignora (`.gitignore`, `.git/info/exclude`)
  existe no disco e some no commit — o lint nega (`git check-ignore -v <arquivo>` mostra a regra).

Como produzir (o `$ cmd` na 1ª linha vem do próprio comando, não de mão; o `rc` é capturado
**antes** do `tail` — funciona em bash e em zsh):

```bash
mkdir -p sdd/reports/evidence/{FEATURE}
cmd='npm test -- src/x.test.ts'
out=$(eval "$cmd" 2>&1); rc=$?
log=sdd/reports/evidence/{FEATURE}/AT-001.log
printf '$ %s\n' "$cmd" > "$log"
printf '%s\n' "$out" | tail -n 200 >> "$log"
printf '[exit=%s]\n' "$rc" >> "$log"
```

`cmd | tail -5; echo "[exit=$?]"` grava o exit do `tail` (sempre 0): um teste que falhou vira
evidência verde. No zsh, `${PIPESTATUS[0]}` sai vazio e o log fica `[exit=]`. O
`sdd/bin/gate-shell-evidencia.sh` acusa os dois casos, e a fase Release o roda nos logs do diff.

## A tabela do BUILD_REPORT (formato que o lint parseia)

```markdown
| ID | Critério (EARS) | Resultado | Evidência |
|----|-----------------|-----------|-----------|
| AT-001 | When X, the system shall Y | false | — |
| AT-002 | If Z, then the system shall W | true | `evidence/{FEATURE}/AT-002.log` |
| AT-003 | manual-ux: fluxo no celular | true | recibo: nome 2026-08-28 · `AVALIACAO_{FEATURE}_20260828-1530.md` |
```

**`Resultado` aceita `true` \| `false`** (também ✅/❌, mas prefira o booleano). O lint só
inspeciona linhas com `true`/✅/`pass`/`verde` — `false` passa livre (é o default honesto).

O lint acha a tabela pelo **cabeçalho**: uma coluna que começa com `Evid` e outra com `Resultado`,
`Status`, `Passou` ou `Result` (o do template, ou o mesmo em inglês: `Result | Evidence`).
Relatório **sem** tabela reconhecida **reprova** (classe `[tabela]`): sem ela, nenhum critério
seria conferido. Use o cabeçalho do template.

### A linha do avaliador (o relatório prova a avaliação, não só a cita)

Todo BUILD_REPORT tem **uma** destas, e a ausência reprova (classe `[avaliação ausente]`):

| Forma | Quando | O lint confere |
|---|---|---|
| `AVALIACAO_{FEATURE}_{AAAAMMDD-HHMM}.md` em `sdd/reviews/` | o avaliador de contexto fresco rodou (passo 5d da `sdd-build`) | o arquivo existe, não está vazio e o git não o ignora; o relatório nem precisa citá-lo |
| `avaliador: N.A. (<motivo>)` | o File Manifest do DESIGN toca menos de N camadas de `layers:` | N vem de `evidence.require_avaliacao_layers` do `sdd/config.yaml` (default 2); com N camadas ou mais, reprova (`[declaração]`); sem como contar (`layers:` vazio, sem DESIGN), aceita com aviso |
| `avaliador: PENDENTE (<motivo>)` | o build travou antes do avaliador | passa aqui, com aviso; `report-lint.py --pendente` sai 1 e a fase Release aborta enquanto a linha existir |

A declaração vale em linha própria, fora de bloco cercado, e também na forma do template
(`**Veredito do avaliador (C1):** N.A. (1 camada)`). Sem o `(motivo)`, reprova.

A **forma mínima** de um relatório que passa é, portanto: a tabela de critérios reconhecida e a
linha do avaliador. Um BUILD_REPORT anterior a esta regra precisa das duas para passar de novo.

### O que conta como evidência para `true` (uma das três)

| Forma | Quando | O lint confere |
|---|---|---|
| `` `evidence/{FEATURE}/AT-nnn.log` `` | critério com `cmd` (test/smoke/eval/typecheck) | path contém `evidence/{FEATURE}/` **da mesma feature do report**, `.log`/`.txt`, existe, não-vazio, 1ª linha começa com `$ ` |
| `` `AVALIACAO_{FEATURE}_{ts}.md` `` | critério provado pelo avaliador de contexto fresco (C1) — inclusive cliques | nome começa com `AVALIACAO_{FEATURE}_`, existe em `sdd/reviews/` e o git não o ignora |
| `recibo: {nome} {YYYY-MM-DD}` | gate `manual-ux` percorrido por humano | padrão textual (nome + data ISO) **e** `DEFINE_{FEATURE}.md` com `kind: manual-ux` (DEFINE ausente → aceita com aviso) |

Evidência de OUTRA feature, `README.md` com `$ ` na 1ª linha, recibo em feature com gate
`test` — tudo negado (buracos fechados no review adversarial de 28/08). Critério com `|` no
texto: escape como `\|` (o lint respeita e conta as colunas a partir do fim da linha).

### Migration aplicada (seção `## Migrations aplicadas`)

Migration listada nos arquivos do relatório exige a linha dela, com o mesmo caminho, projeto
`nome · ref`, data `AAAA-MM-DD` e **prova por leitura**: `` `evidence/{FEATURE}/MIG-nnn.log` ``
(mesmas regras do log acima, com a saída de `migration list` e do `select`) ou
`recibo: {nome} {YYYY-MM-DD}` — aqui em qualquer `kind` de gate, porque no modo manual quem lê o
banco é o aluno. `exit 0` na célula é negado: o comando ter saído bem não diz que a migration está
no banco certo. Procedimento: `.agents/skills/sdd-build/references/aplicar-migration.md`.

### O que o lint NEGA

- Relatório sem tabela de critérios reconhecida.
- `true` sem nenhuma das três formas acima, ou com evidência que o git ignora.
- Evidência contendo `por raciocínio`, `by reasoning`, `by inspection`, `deve funcionar`,
  `provavelmente` — declaração fantasiada de prova.
- `**Veredito do avaliador (C1):** PASS` ou `NEEDS_WORK` sem um `AVALIACAO_*.md` existente
  (e não ignorado) no mesmo parágrafo — inclusive em título seguido de parágrafo, ou numa linha
  de tabela. Veredito citado dentro de bloco cercado é documentação e não conta.
- Avaliação ausente: nenhum `AVALIACAO_{FEATURE}_*.md` e nenhuma linha do avaliador.
- `N.A.` com N camadas ou mais, e `N.A.`/`PENDENTE` sem motivo.

Cada problema sai com a classe (`[tabela]`, `[evidência]`, `[avaliação ausente]`,
`[declaração]`, `[migration]`), e cada classe ganha a sua linha `→` com o conserto.

## Regras de ouro

1. **Evidência ≠ conclusão.** O arquivo contém o output; a conclusão (`true`) fica na tabela.
   Se o output não sustenta o `true`, o reviewer vê a contradição — é o objetivo.
2. **Nada de evidência "compartilhada"** entre ATs sem justificativa: 1 AT = 1 arquivo, ou
   cite o mesmo arquivo em cada linha (o lint aceita; o revisor questiona).
3. **`manual-ux` não é atalho.** Recibo humano vale para o que um humano percorreu; se o
   avaliador C1 clicou, cite o `AVALIACAO_*.md` — não o recibo.
4. **O lint falha FECHADO em erro interno**: exceção sai ≠0 com traceback, e relatório que não
   saiu 0 no `report-lint.py` não está conferido — nunca declare sucesso por cima dele.
5. **Bypass é decisão do humano responsável**, não do agente: pular o `report-lint.py`
   desliga a conferência — e isso vai declarado no BUILD_REPORT e no resumo da sessão.
