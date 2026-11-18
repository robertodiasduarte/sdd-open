# Abrir: F26 Documentos na main — os documentos das frentes saem da branch de documentos e vão para a `main`

Decisão do Roberto em 2026-11-17, depois de pesquisa e medição: os documentos das frentes (DEFINE, DESIGN, relatórios,
ledgers, fichas, plano, fila da curadoria) passam a viver na `main`, no mesmo PR do código, com duas travas para que
nenhum deles chegue ao pacote do aluno. A evidência bruta sai do git. Até esta frente publicar, a branch
`docs/incorporar-starter` continua valendo como está.

## Quando começar

**Só depois da release da F25.** A F25 (`feat/f25-skills-duplicadas`) estava em andamento em 17/11, sem PR ainda, e mexe
no `MANIFEST.txt`, o mesmo arquivo que esta frente usa como lista do pacote. O prompt abaixo começa conferindo isso e
para se a F25 ainda não saiu.

## Onde abrir esta sessão

A frente já está criada (pela `sdd-new-session`, em 2026-11-17), vazia, à espera:

- pasta: `/Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main`
- branch: `feat/f26-docs-na-main`, nascida de `origin/main` em `2204a14` (`v2.21.0`), sem upstream
- feature_id: `F26_DOCS_NA_MAIN`

Abra o editor nessa pasta (`cursor "/Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main"`) e cole o prompt.
Os documentos de hoje estão na worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-docs` (branch
`docs/incorporar-starter`).

## Prompt

```text
Frente F26_DOCS_NA_MAIN do SDD Open (repo público robertodiasduarte/sdd-open). Responda sempre em português.
Pasta: /Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main · branch feat/f26-docs-na-main (sem upstream: o
1º push é `git push -u origin feat/f26-docs-na-main`, nunca `git push` puro).

PASSO 0, ANTES DE QUALQUER COISA — esta frente só começa depois da release da F25 (feat/f25-skills-duplicadas), que
mexe no MANIFEST.txt. Confira, sem alterar nada:
  GIT_TERMINAL_PROMPT=0 git fetch origin
  gh pr list --state all --search "head:feat/f25-skills-duplicadas" --json number,state,title
  gh release list --limit 3
  gh run list --workflow release.yml --limit 3
A F25 saiu quando o PR dela está MERGED, existe uma Release mais nova que a v2.21.0 com as mudanças dela e nenhum run
do release.yml está em andamento. Se ainda não saiu: PARE, diga ao Roberto o que falta e não faça mais nada (nem
Define, nem arquivo, nem marca de fase). Se saiu: traga a branch para a main atual antes de começar — ela está vazia,
então `git rebase origin/main` só a adianta; confira com `git log --oneline -1` que o topo é o da origin/main.

O Roberto não é programador: explique simples, com prós e contras, e recomende; o que é limite do método vira pergunta
a ele, nunca decisão sua. Rode o pipeline inteiro (define → design → build → release). Publicar (push, PR, main, tag,
Release) pede o OK dele.

Objetivo: os documentos das frentes passam a viver na main, no mesmo PR do código, sem nunca entrar no pacote que o
aluno instala; a evidência bruta sai do git; a branch docs/incorporar-starter e a worktree sdd-open-docs são aposentadas.

Por que (pesquisa de 2026-11-17): o conselho corrente é guardar decisão e especificação no repositório do código a que
se aplicam (Fowler, ADR; docs-as-code "ao lado do código" para documentação interna); nenhum arranjo descrito usa branch
separada de longa duração; tirar arquivo do pacote com export-ignore é prática corrente, com a ressalva de que nada
confere o pacote final sozinho. São convenções de praticantes, não norma. Fontes:
martinfowler.com/bliki/ArchitectureDecisionRecord.html · passo.uno/docs-as-code-topologies ·
php.watch/articles/composer-gitattributes

O que foi medido em 2026-11-17 (confira de novo antes de usar, a main andou):
- o tarball da Release sai de `git archive` (release.yml), então export-ignore vale nele;
- no CI, o publish-gate roda sobre a PASTA do checkout (`scripts/publish-gate.sh "$GITHUB_WORKSPACE"`), não sobre o
  pacote: o G3 reprova todo arquivo fora do MANIFEST.txt e o G2 barra número de 11+ dígitos; 131 documentos da branch
  de documentos têm número assim. Com os documentos na main, o gate do CI precisa conferir o pacote MONTADO (o Verify
  Gate local já faz: `git archive HEAD | tar -x` e o publish-gate na cópia);
- nenhum teste lê sdd/features, sdd/reports, sdd/handoffs, sdd/reviews ou sdd/releases do próprio repositório;
- a branch de documentos tem 3.189 arquivos e 27 MB; 22 MB e 2.827 arquivos são sdd/reports/evidence; os documentos
  escritos são uns 350 arquivos, mais 118 de resumo das revisões (reviews-medicao);
- a main ignora sdd/reports/reviews/ e sdd/traces/ (.gitignore); os documentos na branch de documentos não passam por
  nenhuma varredura automática (a de dado privado e número longo foi feita à mão na B2).

Desenho recomendado (o Design confirma ou troca, com o porquê):
1. Trava 1: export-ignore no .gitattributes para sdd/features, sdd/reports, sdd/handoffs, sdd/reviews, sdd/releases,
   sdd/archive, sdd/curadoria (e sdd/traces, se passar a ser commitado).
2. Trava 2: o publish-gate do CI confere o pacote montado contra o MANIFEST.txt; documento que escapar reprova. Um
   teste abre o tarball e falha com qualquer arquivo dessas pastas.
3. Varredura própria dos documentos (segredo e dado privado), que hoje não existe; decidir se a regra do número longo
   vale para documento ou só para o pacote.
4. Evidência: no git fica o que um lint ou uma pessoa lê (logs por AT, logs de gate, relatórios, META e vereditos das
   revisões); o bruto (gabaritos copiados, respostas de modelo, logs de série) vira anexo da Release ou artefato do CI.
5. Migração: trazer os documentos da branch docs/incorporar-starter para a main (decidir: com o histórico ou só o
   estado atual) e, com tudo conferido na main, aposentar a branch e a worktree. Isso apaga coisa: é pergunta ao Roberto.
6. Fluxo: no Open, os documentos da frente vão no PR dela e o commit de papel da release vai para a main, como num
   projeto comum; tirar dos prompts e fichas a regra "documento só na branch de documentos".

A conferir no Define (não sei a resposta):
- o init e o upgrade instalam também de um clone (`git -C ~/sdd-open pull` e `bin/sdd-open.sh upgrade`), não só do
  tarball: confirme que copiam por lista (MANIFEST.txt, SDD_ENTRADAS_PACOTE), nunca a árvore inteira de sdd/;
- o gerador do starter (scripts/gerar-starter.py) e o check-versions não devem enxergar os documentos;
- commit só de documento na main não dispara a Release (os paths do release.yml já excluem essas pastas): prove com o
  push-de-papel.py;
- a pendência da F24 que isto resolve: a fila da curadoria na branch de documentos e o playbook na main.

Leia primeiro (worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs, branch docs/incorporar-starter):
- sdd/features/PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" e "Cronograma recomendado";
- sdd/handoffs/HANDOFF_F24_RELEASE_ENXUTA.md → Falta (a pendência da fila);
- na main: scripts/publish-gate.sh, MANIFEST.txt, .gitattributes, .github/workflows/release.yml e publish-gate.yml,
  a seção Sempre de sdd/playbook.md.

Não faça: pôr número medido no repositório privado em documento do Open; corrigir direto no starter; apagar a branch
de documentos antes de o Roberto conferir a main; afrouxar o G2 ou o G3 para o pacote.
Landmines: MANIFEST.txt para todo arquivo novo do pacote (LM-037); teste que pergunta a plataforma usa as constantes de
tests/apoio.py, nunca os.name; rode test_windows e test_gerar_starter antes do gate; a suíte tem de passar no Windows
(o CI do PR); o Bash do agente é zsh (variável com vários caminhos não se divide: use array).
```
