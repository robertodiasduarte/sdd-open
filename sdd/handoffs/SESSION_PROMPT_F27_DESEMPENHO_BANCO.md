# Abrir: F27 Desempenho do banco — skill `sdd-desempenho-banco`

O Roberto pediu em 2026-11-17 uma skill do SDD Open para avaliar o desempenho do banco (Supabase/Postgres). O
brainstorm foi fechado com ele na mesma data e está nesta frente:
`sdd/features/BRAINSTORM_F27_DESEMPENHO_BANCO.md`. Ele traz a pesquisa, 13 decisões já aceitas e o rascunho de 17
fichas e de 8 critérios de aceite.

## Onde abrir esta sessão

- pasta: `/Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance`
- branch: `feat/f27-db-performance`, nascida de `origin/main` em `2204a14` (`v2.21.0`), sem upstream
- feature_id: `F27_DESEMPENHO_BANCO`

Abra com `cursor "/Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance"` e cole o prompt.

## Prompt

```text
Frente F27_DESEMPENHO_BANCO do SDD Open (repo público robertodiasduarte/sdd-open). Responda sempre em português.
Pasta: /Users/robertoduarte/rdd-worktrees/sdd-open-f27-db-performance · branch feat/f27-db-performance (sem upstream:
o 1º push é `git push -u origin feat/f27-db-performance`, nunca `git push` puro).

O QUE FAZER: rodar o pipeline inteiro do SDD Open para criar a skill nova `sdd-desempenho-banco`:
sdd-define → (sdd-ux-review, se o Define disser que há interface) → sdd-design → sdd-build → sdd-release. Pode usar a
sdd-drive do DEFINE até "pronto para publicar". O brainstorm está FECHADO: comece pelo sdd-define lendo
sdd/features/BRAINSTORM_F27_DESEMPENHO_BANCO.md (pesquisa, decisões D1–D13, rascunho das fichas P01–P17 e dos
critérios de aceite). Não reabra o brainstorm.

COMO DECIDIR (pedido do Roberto): em cada decisão, avalie prós e contras, recomende e ACEITE A RECOMENDAÇÃO COMO DEFAULT,
registrando-a no documento da fase (no Advisor Ledger ou como "Decidi sozinho"). Pergunte ao Roberto SÓ o que for
crítico:
  (1) o OK de publicar da sdd-release (sempre);
  (2) apagar qualquer coisa que não foi criada nesta frente;
  (3) afrouxar proteção existente (gate, varredura de segurança, publish-gate, regra do playbook);
  (4) mudar o escopo para além do brainstorm (mexer em skill não listada ali, mudar a sdd-seguranca além de
      reaproveitar a detecção de stack, fazer a varredura bloquear);
  (5) rodada de revisão acima do teto;
  (6) conflito do rebase que mude o comportamento que a F26 entregou.
O Roberto não é programador: quando perguntar, explique simples, com o efeito de cada opção.

PRIMEIRA AÇÃO (a sessão que abriu a frente estava presa ao espelho e o gancho barrou o commit): na worktree de
documentos ficaram SEM COMMIT só estas 2 mudanças, com o registro da F27: sdd/features/PLANO_F4_F15_CONSOLIDADO.md
(linha da F27 em "Estado das frentes", #2 do "Cronograma recomendado", data do cabeçalho) e
sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md (1 linha nos Eventos). Confira com
`git -C /Users/robertoduarte/rdd-worktrees/sdd-open-docs diff --stat` (2 arquivos, só inserções e a data) e faça o
commit SÓ desses dois caminhos, pelo nome, nunca `git add -A` (a pasta sdd/traces/ não rastreada não entra):
  git -C /Users/robertoduarte/rdd-worktrees/sdd-open-docs add sdd/features/PLANO_F4_F15_CONSOLIDADO.md sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md
  git -C /Users/robertoduarte/rdd-worktrees/sdd-open-docs commit -m "docs(f27): frente F27 Desempenho do banco registrada no plano"
  GIT_TERMINAL_PROMPT=0 git -C /Users/robertoduarte/rdd-worktrees/sdd-open-docs pull --rebase origin docs/incorporar-starter
  GIT_TERMINAL_PROMPT=0 git -C /Users/robertoduarte/rdd-worktrees/sdd-open-docs push origin docs/incorporar-starter
Se o diff já não estiver lá (outra sessão commitou), confira no `git log` que a linha da F27 entrou e siga.

ORDEM DA FILA — LEIA ANTES DE TUDO. A F25 (feat/f25-skills-duplicadas) estava em finalização e a F26
(feat/f26-docs-na-main, worktree /Users/robertoduarte/rdd-worktrees/sdd-open-f26-docs-na-main) está na fila. As duas
mexem no MANIFEST.txt, e a F26 mexe também no empacotamento, no publish-gate e na sdd-release. Regra (decisão D13):
- Define, Design e Build podem correr já, nesta branch.
- A Release da F27 só depois de F25 E F26 publicadas. Antes do passo de release, confira sem alterar nada:
    GIT_TERMINAL_PROMPT=0 git fetch origin
    gh pr list --state all --search "head:feat/f25-skills-duplicadas" --json number,state,title
    gh pr list --state all --search "head:feat/f26-docs-na-main" --json number,state,title
    gh release list --limit 3
    gh run list --workflow release.yml --limit 3
  Cada uma saiu quando o PR dela está MERGED, existe Release mais nova com as mudanças dela e nenhum run do
  release.yml está em andamento. Se alguma não saiu: PARE antes da release, deixe a frente pronta para publicar (BUILD_REPORT,
  gate verde) e diga ao Roberto o que falta. Se as duas saíram: `git rebase origin/main`, resolva os conflitos
  (esperados: MANIFEST.txt, sdd-release, guia do aluno, README; reaplique a mudança da F27 sobre a versão nova, sem
  desfazer nada da F26), rode a suíte inteira e o Verify Gate de novo, e só então siga para a release.
- Ao abrir, olhe também se a F25 já saiu; se saiu, rebase logo no começo (a branch ainda está vazia) para nascer da main
  atual.

ONDE FICAM OS DOCUMENTOS (decisão D12): os documentos da F27 (DEFINE, DESIGN, BUILD_REPORT, ledger, evidência legível)
ficam NESTA branch, em sdd/ — o estado-alvo da F26. Na branch de documentos (worktree
/Users/robertoduarte/rdd-worktrees/sdd-open-docs, branch docs/incorporar-starter) só se atualiza a linha da F27 na
tabela "Estado das frentes" e o "Cronograma recomendado" de sdd/features/PLANO_F4_F15_CONSOLIDADO.md, com commit e push
na mesma sessão, enquanto a F26 não aposentar essa branch. Depois da F26, siga a regra que ela publicou. Antes da F26, o
publish-gate do CI pode reprovar os documentos desta branch (G3, arquivo fora do MANIFEST.txt) num push: isso é
esperado, e o rebase sobre a F26 resolve. Não "conserte" o gate.

ESCOPO (do brainstorm, resumido):
- Skill nova em .agents/skills/sdd-desempenho-banco/ no molde da sdd-seguranca (SKILL.md com "Como falar com o aluno",
  manifest.json, references/CATALOGO_DESEMPENHO.md com as fichas Pnn, references/como-falar.md, evals/cases.json).
- Varredura estática sdd/bin/desempenho-varredura.sh (só leitura, sem rede; exit 0 nada · 1 avisos · 64 uso inválido;
  NUNCA 2), com dispensa por comentário `sdd-desempenho-banco: aceito Pnn — <motivo>`. Reaproveitar a detecção de stack
  da segurança (slot security.stack / seguranca-varredura.sh --stack), sem duplicar.
- Modos: Define (gatilho `banco`; no máximo 1 pergunta de volume; N.A. em 1 linha), Design (decisões das fichas da
  fase design), varredura na sdd-release como AVISO (nunca aborta) e diagnóstico a pedido (consentimento por execução,
  só leitura: MCP get_advisors/execute_sql de leitura ou CLI `supabase db advisors` / `supabase inspect db`; sem eles,
  roteiro à mão no painel). Nunca escreve no banco.
- Regras de interpretação do diagnóstico (D7): índice "não usado" só com a idade das estatísticas; achado confirmado
  antes de virar correção; tamanho da máquina antes de culpar a consulta; nunca EXPLAIN ANALYZE de escrita fora de
  BEGIN … ROLLBACK.
- Fora: agendamento, legado em massa, front-end, carga, outros bancos, frase no AGENTS.md (D11).
- Ganchos: sdd-define (passo de banco), sdd-design (seção), sdd-release (varredura), MANIFEST.txt, gerador do starter
  (scripts/gerar-starter.py), guia do aluno, README. A skill chega ao starter pelo gerador (F17), com o PR do starter
  na release, como nas frentes anteriores.
- Ponto a conferir no Design: como o Supabase CLI aplica migrations (transação?) antes de recomendar
  `create index concurrently`.

LEIA PRIMEIRO:
- sdd/features/BRAINSTORM_F27_DESEMPENHO_BANCO.md (esta branch);
- .agents/skills/sdd-seguranca/ inteira e sdd/bin/seguranca-varredura.sh (o molde);
- a seção `## Sempre` de sdd/playbook.md e `bash sdd/bin/playbook-lint.sh --grep <termo> sdd/playbook.md` para
  MANIFEST, varredura, stack, Windows e starter;
- na worktree de documentos: sdd/features/PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" e "Cronograma
  recomendado" (a linha da F27 já está lá).

NÃO FAÇA: pôr número ou nome medido no repositório privado da RDD em documento ou fixture do Open (o brainstorm já
traz a lição sem número; fixtures são sintéticas); corrigir direto no starter; mexer na F25 ou na F26; tornar a
varredura de desempenho bloqueante.

LANDMINES: MANIFEST.txt para todo arquivo novo do pacote (LM-037); teste que pergunta a plataforma usa as constantes
de tests/apoio.py, nunca os.name; rode test_windows e test_gerar_starter antes do gate; a suíte tem de passar no Windows
(o CI do PR; medir lá exige push da branch); o Bash do agente é zsh (variável com vários caminhos não se divide: use
array); número de 11+ dígitos em arquivo do pacote reprova o G2 do publish-gate.
```
