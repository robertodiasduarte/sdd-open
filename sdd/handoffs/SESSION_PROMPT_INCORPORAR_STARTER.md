# Continuar: INCORPORAR_STARTER — F17 Starter gerado a partir do Open (frente aberta em 2026-11-12), com as sobras no passo 0

A `v2.12.0` do Open saiu em 2026-11-11 (`main` = `382ef04`): F18 + F20, segurança embutida no fluxo (skill `sdd-seguranca`,
varredura em toda publicação, regras da stack no `AGENTS.md`). A `v2.12.1` (2026-11-12, `main` = `e22a1b2`) traz só a curadoria do
playbook. Pelo **Cronograma recomendado** do plano, a próxima frente é a **F17 Starter gerado a partir do Open** (Decisão 5): o
starter deixa de ter texto próprio, e a 1ª geração já leva a F16 e a F18 + F20.

## Onde abrir esta sessão

A frente **já existe** (aberta em 2026-11-12 pela `sdd-new-session`): worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f17-starter-gerado`, branch `feat/f17-starter-gerado`, de `origin/main` = `e22a1b2`
(`v2.12.1`). A janela do Cursor foi aberta nela; cole o prompt abaixo lá. A worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f18-f20-seguranca` guarda as revisões da F18 + F20 (`sdd/reports/reviews/`): não a
apague sem arquivar essa pasta.

## Prompt para colar na sessão nova

```text
Executar a frente F17 do SDD Open: starter gerado a partir do Open (Decisão 5). Repo público robertodiasduarte/sdd-open.
A frente já está aberta: /Users/robertoduarte/rdd-worktrees/sdd-open-f17-starter-gerado, branch feat/f17-starter-gerado, de
origin/main = e22a1b2 = v2.12.1. Não rode a sdd-new-session. Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
A F17 toca dois repositórios: o gerador mora no Open; o robertodiasduarte/sdd-starter recebe a cópia gerada e pede OK PRÓPRIO
do Roberto para cada push, PR e Release lá. Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do
repositório privado, texto do e-book de segurança) entra em nenhum dos dois.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes", o "Cronograma
  recomendado" (com as sobras do passo 0), a seção da F17 (objetivo, entrega, decidir, depende de) e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de 2026-11-11 e
  a seção "2026-11-11 — F18 + F20" (Pendências e Alertas)
- git show origin/docs/incorporar-starter:sdd/features/AVALIACAO_STARTER_PARA_OPEN.md → o que o starter tem e o Open não
- o ## Sempre de sdd/playbook.md da frente
- o starter publicado: gh release view --repo robertodiasduarte/sdd-starter (só leitura) e o README dele. O clone local
  /Users/robertoduarte/rdd-public/sdd-starter estava 5 commits atrás do origin (v1.5.15 local × v1.5.16 publicada) e com um
  docs/guia-do-aluno.pt-BR.md não rastreado que não é desta frente: compare pelo origin (fetch + git show/git archive da tag),
  não pela pasta, e não toque no arquivo não rastreado.

0. Sobras da F18 + F20, na branch da frente (sobem com a release dela):
   a. Cenário incidente-chave da sdd-seguranca (evals/cases.json) em contexto novo, 3 execuções, critério escrito antes (LM-011);
      registre em manifest.json → executados.
   b. Pequenos (decida com o Roberto se entram): o --help da governanca-fronteira.sh exige Python; o resumo do checar mostra o
      editor detectado, não o do git config sdd.editor; o guia do aluno sem a linha gh: do inventário; a ambiguidade "item 10"
      (FASE 2 × 0a) da sdd-release (docs/adaptation-guide.md, slot.sh, deploy-do-sha.sh); a recuperação "rode só o passo 11"
      do verify-gate.sh pula o passo 12.
   c. Achados do pacote vindos do repositório privado em 2026-11-12 (decida com o Roberto se entram; 3 LOW de uma revisão
      claude): o resumo "quando abortar" da sdd-release sem o exit 127 da varredura e sem o exit 2 do ledger-revisao-lint.sh
      (itens 8 e 10 mandam abortar); a heurística comentado() da seguranca-varredura.sh trata " #" ou "<!--" anterior na mesma
      linha como comentário e esconde aviso S12/S16/S14 real; o metadado updated da sdd-brainstorm ficou 2026-10 com a versão
      2.3.0 e a linha de identificação em nov/2026. E o checar.sh --frente lê só refs/remotes/origin/HEAD local: com a ref velha
      (apontando para outra branch) ele diz a principal errada mesmo com project.default_branch certo no config.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.12.1.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - Brainstorm com as decisões abertas do plano: a lista de skills que vão ao starter (só as que funcionam sozinhas: no mínimo
     sdd-checar-ambiente, sdd-iniciar-repo, sdd-new-session, sdd-higiene-dado, sdd-kb; a sdd-seguranca tem a forma "confira à
     mão" em todo item do catálogo); o que acontece com as skills que existem só no starter; geração manual (comando na release
     do Open) ou automática (workflow que abre PR no starter); como o sdd/ambiente.md do starter convive com os slots do
     sdd/config.yaml do Open. Antes da 1ª geração, compare skill a skill o starter publicado com o Open.
   - Entrega (4) do plano (D6): as cópias de usuário ~/.claude/skills/sdd-* estão velhas (em 2026-11-12: sdd-release v2.8.1,
     sdd-new-session v1.4.1, contra v2.11.0 e v1.5.0 no pacote); regenerar pela tag publicada, nunca pela branch.
   - P2 (agnóstico) e a web: o starter é a porta de quem usa claude.ai ou ChatGPT sem terminal; teste no Open que reprova skill
     gerada que cite arquivo criado pelo init.
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md (ledger-revisao-lint.sh); no fim, eval-revisores.sh no relatório.
   - Documentos SDD (features, reports, reviews, evidence) ficam fora do git na pasta da frente e vão no fim para a branch de
     documentos (worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16).

Revisão adversarial: saldo da OpenRouter em US$ 15,59 em 2026-11-12 (fim do dia), e a chave tem outro uso (o saldo caiu mais que o custo das
rodadas): leia /credits antes de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia que funcionou na F16
e na F18 + F20: claude revisa, `openrouter` (qwen) audita, --no-revisor2 e --no-desempate (codex sem cota) — registre a dispensa
do 2º revisor. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha
^OPENROUTER_API_KEY= no ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir; desacordo sobre
comportamento de ferramenta se decide por medição registrada (LM-021).
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto. Rode o raio de impacto
(0b) antes da última rodada: na F18 + F20 ele achou 4 quebras. Diff grande estoura o auditor: em 2026-11-12 o qwen passou do teto
de 15 min com um diff de 576 KB (sync do pacote inteiro); se a 1ª geração do starter vier no diff, revise por partes (--paths). Avaliador de segurança: chave falsa montada em tempo de
execução, nunca por extenso nos logs (LM-020).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~29 min, teto 45; macOS ~44 min, teto 75; Windows caminho do
aluno ~4 min, teto 30). A varredura de segurança roda no próprio pacote (item 10 da 0a): log de evidência com chave por
extenso bloqueia. Se a suíte crescer, olhe o teto ANTES da tag. Sem tag sai patch; para minor, push da main e da tag juntos
(git push --atomic). Número com 11 dígitos em arquivo do pacote é barrado pelo publish-gate: cite o commit.
Rode a suíte com a máquina livre: o teste de tempo da sdd-drive (test_fundo_devolve_na_hora…, 1,9 s) cai sob carga.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F17 na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.

Não faça:
- nada da F15 nesta sessão se a geração tocar a sdd-release;
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou Release no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a Decisão 5 é gerar);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por script
bash com rc=$? (no zsh, ${PIPESTATUS[0]} é vazio: LM-018). Não cale com 2>/dev/null um aviso dito uma vez (LM-019). Pulo de
plataforma nos testes só por constante de tests/apoio.py. Script novo de sdd/bin que chama python3 lê sdd/bin/lib/python.sh.
O catálogo da sdd-seguranca tem gramática rígida e um leitor só (seguranca-varredura.sh); o ponteiro do AGENTS.md existe em 2
cópias com teste. sdd-release em 500 linhas (teto do teste). Contagens fixadas em testes antigos (21 skills, 30 perguntas do
sdd-decisoes-lint, versões de skill): skill ou pergunta nova mexe nelas.
```
