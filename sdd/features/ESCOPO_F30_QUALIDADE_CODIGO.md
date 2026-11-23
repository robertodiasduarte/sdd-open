# F30 — Qualidade do código gerado (achado e escopo)

> Registrado em 23/11/2026, na abertura da frente `qualidade-codigo` (worktree
> `~/rdd-worktrees/sdd-open-f30-qualidade-codigo`, nascida de `origin/main` `4aa0cce`). Origem: avaliação feita
> com o Roberto sobre o que o SDD Open já cobre das práticas consagradas por Robert C. Martin (Uncle Bob):
> *Clean Code*, *Clean Architecture*, TDD e SOLID. O Roberto escolheu fazer os **itens 1 a 8**.

## 1. O que já existe (não refazer)

O Open cobre bem a parte de **processo e prova**:

- **Verify Gate:** o aceite é um comando, escrito no Define antes do código.
- **Contrato de evidência:** `report-lint.py`; "deve funcionar" vale `false`.
- **Bugfix:** exige uma cláusula `shall continue to` (`fragments/EARS.md:14`).
- **Revisão:** a marca `dano=sim` exige um teste que falha no código antigo (`sdd-build/SKILL.md:241`).
- **Design:** ADRs inline, e o `design-lint.py` reprova dependência em ciclo no manifest. A estratégia de testes cobre cada AT.
- **Avaliador de contexto fresco** e **revisão de 2º vendor**.

Não cobre a **forma do código**. Não há nenhuma ocorrência de SOLID, *Clean Architecture*, regra do escoteiro, mutação, complexidade ou duplicação de código no `main`.

Também não há disciplina de **vermelho antes do verde**: o gate prova o verde no fim, nunca o vermelho no começo.

## 2. Achados concretos no código

| Achado | Onde | Efeito |
|---|---|---|
| O passo de verificar de cada tarefa do Build é uma frase genérica: "**Verificar** (lint, tipos, teste do arquivo)" | `.agents/skills/sdd-build/SKILL.md:188` | Não diz que comando rodar, não usa o slot `project.lint_cmd`, não deixa evidência. Cada agente interpreta de um jeito; na prática, o lint só roda de fato na `sdd-release` |
| `project.lint_cmd` só é **lido** pela `sdd-release` e **descoberto** pela `sdd-new-session` | `sdd-release/SKILL.md:78`, `sdd-new-session/SKILL.md:72,285` | O erro de estilo aparece no fim, com tudo pronto |
| A `sdd-new-session` só preenche o `lint_cmd` com evidência literal (workflow, `package.json`, `Makefile`). Projeto sem linter fica com o slot vazio, e nada é proposto | `sdd-new-session/SKILL.md:285` | O projeto típico de aluno não tem linter, então nunca roda lint |
| O `checar.sh` não olha linter nem checagem de tipos | `sdd-checar-ambiente/scripts/checar.sh` (nenhuma ocorrência de lint, eslint ou ruff) | — |
| Já existe um mecanismo de **regras por stack no AGENTS.md**: o placeholder `{{SEGURANCA}}` do template, que o `init`/`sync` preenche via `seguranca-varredura.sh --agents`; a `sdd-build` lê `--regras` antes de construir | `AGENTS.md.tmpl:44-49`, `bin/sdd-open.sh:446-457`, `sdd/bin/seguranca-varredura.sh:17-19,117,335-340` | É o molde a reutilizar no item 3 |
| A seção de estratégia de testes do Design é uma tabela vazia (Tipo, Escopo, Ferramenta, Meta) | `sdd-design/SKILL.md:199` | Não pede sabotagem nem "como saber que o teste pega o defeito" |
| O modo web do Build diz "não refatorar código adjacente sem necessidade" | `sdd-build/web/MODO_WEB.md:236` | Está certo para o agente. O item 7 tem de conciliar isso com refatorar **só o que a tarefa tocou** |

## 3. Escopo: os 8 itens

Agrupados em 3 fatias, cada uma publicável sozinha. **Ordem recomendada: S1 → S2 → S3.** A S1 muda o código que o aluno recebe já na primeira feature; a S3 depende de S1 para calibrar os limites.

### Fatia S1 — Qualidade por stack (itens 1, 3, 4)

**Item 1. Lint e tipos de verdade dentro do Build, a cada tarefa.**

O passo "Verificar" do Build passa a ser:
1. rodar `project.lint_cmd` (e o comando de tipos, se houver slot; ver D1) sobre os arquivos da tarefa;
2. falha ⇒ seguir a escada de retry que já existe;
3. ao fim do Build, guardar um log com a 1ª linha `$ <comando>` em `sdd/reports/evidence/{F}/LINT.log`;
4. o `report-lint.py` exige esse log quando o slot está cheio.

Com o slot vazio: uma linha no BUILD_REPORT ("lint: slot vazio") e o aviso ao aluno, sem bloquear.

**Item 3. Regras de qualidade por stack no AGENTS.md.**

Um bloco `### Qualidade ao construir` no `AGENTS.md.tmpl`, com o placeholder `{{QUALIDADE}}`, preenchido pelo `init`/`sync` a partir de um catálogo, no mesmo molde da segurança (F18/F20).

Em torno de 6 regras, em frase positiva (lição da F29: nada de "não cite", nada de banner):
- erro tratado ou propagado, nunca engolido;
- nome que diz o que a coisa é;
- sem código morto nem comentado;
- **procurar e reusar a função que já existe antes de criar outra**;
- constante nomeada no lugar de número mágico;
- função que faz uma coisa só.

Mais as regras específicas de cada stack (Python, JS/TS, PHP, SQL).

**Atenção:** o **Starter não tem AGENTS.md** (são só skills). As regras precisam aparecer **também** no texto da `sdd-build`, a parte que vai para o Starter na próxima geração. Conferir no `scripts/gerar-starter.py`.

**Item 4. Descobrir o linter e, sem linter, propor o padrão da stack.**

- O `checar.sh` (ou a `sdd-new-session`) detecta a stack e, quando não há linter ou checagem de tipos, sugere o padrão:
  - Python: `ruff check`, mais `mypy` quando houver tipagem;
  - JS/TS: `eslint` + `prettier --check` e `tsc --noEmit`;
  - PHP: `php -l` + `phpcs`.
- **É pergunta, nunca instalação sozinha**: o comando exato de instalar, e o slot gravado no `sdd/config.yaml` da frente só com o sim do aluno.
- O texto sai na voz da `como-falar.md`, para quem nunca usou terminal.

### Fatia S2 — Disciplina de teste (itens 2, 6, 7)

**Item 2. Vermelho antes do verde.**

Para cada AT de **comportamento novo**, a evidência traz duas execuções do comando do gate:
1. antes do código da tarefa, **falhando**: `AT-nnn.antes.log`, exit diferente de 0;
2. depois, passando: `AT-nnn.log`, exit 0.

O `report-lint.py` exige o par.

Exceções explícitas:
- **`shall continue to`** (não-regressão) é o contrário: tem de estar **verde antes e depois**. O `antes` com exit 0 é a prova.
- AT de assinatura humana (exit 4) fica fora.

Ver D3.

**Item 6. Mutação mínima do gate (sabotagem).**

Prova que o gate pega o defeito:
1. aplicar uma sabotagem declarada (inverter a condição central, retornar vazio, remover a checagem) **numa cópia temporária** (worktree descartável), nunca na árvore de trabalho;
2. rodar o comando do AT;
3. esperar vermelho;
4. descartar a cópia.

Script novo, por exemplo `sdd/bin/sabotagem.sh`. O resultado vira `sdd/reports/evidence/{F}/AT-nnn.sabotagem.log`. Generaliza a regra do `dano=sim` (`sdd-build/SKILL.md:241`). Ver D4.

**Item 7. Refatorar depois do verde, só no que a tarefa tocou.**

Um passo novo na tarefa do Build, entre "Verificar" e "Marcar":
1. com os testes e o lint verdes, revisar **só os arquivos da tarefa** (nomes, duplicação interna, função grande);
2. rodar de novo lint e testes;
3. continuar verde.

Concilia a regra do escoteiro com a "mudança cirúrgica" do `MODO_WEB.md:236`. Pode ser desligado por config, para quem quiser economizar tokens (D7).

### Fatia S3 — Métricas no diff, só aviso (itens 5, 8)

**Item 5. Duplicação no código novo.**

Ferramenta multilinguagem (`jscpd` é a candidata) restrita aos arquivos do diff da frente, comparando contra o repositório inteiro. O alvo é o defeito nº 1 do código feito por agente: recriar um helper que já existe.

**Item 8. Complexidade no código novo.**

`lizard` (pip, multilinguagem), só nas funções novas ou alteradas. Limites iniciais (D5):
- complexidade ciclomática acima de 10;
- função com mais de 60 linhas;
- mais de 5 parâmetros.

**Os dois só avisam.** O resultado vai para uma seção `## Qualidade (avisos)` do BUILD_REPORT.

Ferramenta ausente: a seção diz "não medido: <ferramenta> ausente" e o comando para instalar. Nunca reprova o Build e nunca sai como "zero achados".

O `report-lint.py` exige só que a seção exista.

## 4. Decisões (perguntar no Define, juntas, com a recomendação)

| ID | Pergunta | Recomendação | Por quê |
|---|---|---|---|
| D1 | Erro de lint ou de tipos no Build **bloqueia** ou **avisa**? E o comando de tipos ganha slot próprio (`project.typecheck_cmd`) ou vai dentro do `lint_cmd`? | **Bloqueia** quando o slot está cheio, pela escada de retry. Tipos **dentro do `lint_cmd`**, sem slot novo | É objetivo e o projeto escolheu o comando. Slot novo exige migração de config em todos os projetos |
| D2 | Projeto sem linter: o Open **instala** ou só **propõe**? | **Propõe** o comando exato e grava o slot só com o sim | O aluno não pode ter o `package.json` alterado sem saber. Coerente com a `sdd-new-session` (slot só com evidência) |
| D3 | Vermelho antes do verde vale para **todo** AT ou só para os de comportamento novo? | Todo AT `kind: test` ou `cmd` de comportamento novo. `shall continue to` exige **verde** antes. Exit 4 fica fora | Regressão vermelha antes seria contradição; assinatura humana não roda |
| D4 | Sabotagem: **uma por feature** ou **uma por AT**? Quem escreve: o DESIGN declara ou o agente escolhe no Build? | **Uma por AT de superfície de risco** (dado, dinheiro, acesso, publicação, disponibilidade, o mesmo critério do `CRITERIO_DANO.md`) e **pelo menos uma por feature**. O **DESIGN declara** a sabotagem na estratégia de testes | Custo previsível. Declarada antes, o construtor não escolhe a sabotagem fácil |
| D5 | Limites do item 8 e mínimo de tokens do item 5 | Complexidade 10, 60 linhas, 5 parâmetros. `jscpd --min-tokens 50`. Tudo em `sdd/config.yaml` (`qualidade.*`), com esses valores como padrão | Valores usuais do mercado. Calibrar depois com projeto real |
| D6 | Catálogo de qualidade: **arquivo novo** ou **seção no catálogo de segurança**? | **Arquivo novo**, `.agents/skills/sdd-build/references/CATALOGO_QUALIDADE.md`, com script irmão (ou modo `--qualidade` no próprio `seguranca-varredura.sh`, decidir no Design) | Segurança e qualidade têm donos e frequências diferentes. Misturar polui a varredura de publicação |
| D7 | Item 7 ligado por padrão? | **Ligado**, com `build.refatorar: false` para desligar. Desligado no modo `lite` do loop | O ganho de forma é a razão da frente. Quem economiza escolhe |

## 5. Fora do escopo (decidido em 23/11)

- **Regra de dependência da *Clean Architecture*** (item 13 da avaliação): fica para uma opção da Turma Bravo, numa frente futura.
- **Mutação completa** (Stryker, mutmut): o item 6 cobre o essencial.
- **Checklist SOLID como gate**: subjetivo.
- **Dimensão "manutenibilidade" na revisão adversarial** (item 9): reavaliar depois da S3.
- Código morto (knip/vulture), cobertura no diff e hook de formatação (itens 10–12).
- **Medir a nota de aderência** (a régua "mesma feature com e sem o método": violações por mil linhas, complexidade média, % de duplicação, mutantes mortos): candidata a frente seguinte. A estimativa de 23/11, só julgamento, sem medição, é ≈ 5,8 hoje e ≈ 7,5 com os itens 1–8.

## 6. Proposta de Verify Gate (refinar no Define)

Um teste por mecanismo, em `tests/test_f30_*.py`, mais a suíte inteira:

| AT | Prova |
|---|---|
| S1-a | `report-lint.py` reprova um BUILD_REPORT com o `lint_cmd` cheio e sem `LINT.log`; aprova com o log; aprova com o slot vazio e a linha "lint: slot vazio" |
| S1-b | `init` e `sync` num projeto de fixture Python e noutro JS geram o bloco `### Qualidade ao construir` com as regras da stack; sem stack reconhecida, só as gerais. Rodar duas vezes não duplica o bloco |
| S1-c | `checar.sh` em fixture sem linter imprime a sugestão da stack e **não** altera arquivo nenhum (`git status` limpo) |
| S1-d | O starter gerado numa pasta temporária traz as regras de qualidade no texto da `sdd-build` e passa os `grep` da F29 (nenhum padrão que o Snyk marca) |
| S2-a | `report-lint.py` reprova um AT de comportamento novo sem `AT-nnn.antes.log` vermelho; reprova `shall continue to` com `antes` vermelho; aprova os pares certos |
| S2-b | `sabotagem.sh` sobre uma fixture: gate vermelho com a sabotagem ⇒ exit 0 e log; gate **verde** com a sabotagem ⇒ exit 2 ("o teste não pega o defeito"); a árvore de trabalho fica intacta nos dois casos (hash antes = depois) |
| S2-c | O texto da `sdd-build` tem o passo "Refatorar" entre Verificar e Marcar, e o `config.example.yaml` tem `build.refatorar` |
| S3-a | O script de métricas numa fixture com uma função de complexidade 15 e um bloco duplicado ⇒ seção de avisos com os dois achados, **exit 0** |
| S3-b | O mesmo script com `lizard`/`jscpd` ausentes ⇒ "não medido" mais o comando de instalar, exit 0, e **nunca** "0 achados" |
| todos | `python3 -m unittest discover -s tests` verde; `bash tests/run-bash32.sh` (ou o equivalente do repo) verde; CI 18 de 18 |

## 7. Riscos

- **Aluno travado por lint de código antigo:** o lint do Build roda sobre os **arquivos da tarefa**, não sobre o repo inteiro. Se o `lint_cmd` do projeto não aceitar lista de arquivos, registrar no Design como cair para o repo inteiro sem bloquear pelo que é antigo.
- **Custo em tokens:** os itens 2, 6 e 7 acrescentam execuções por AT. Medir no Build da própria F30 (o `eval-revisores.sh` e o relatório trazem o custo) e registrar no BUILD_REPORT.
- **Snyk de novo:** texto novo em skill passa pelos `grep` da F29 antes da release.
- **Windows:** scripts novos rodam no Git Bash, e o CI do Windows cobre (F16W).
- **Starter:** cada fatia publicada no Open pede a geração seguinte do Starter (fluxo do README do starter). A S1 muda o texto de skill que o Starter recebe.
