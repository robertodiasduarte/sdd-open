# Continuar: INCORPORAR_STARTER — F17c Starter gerado, etapa 3 (define, design e build em modo web), com as sobras da F17b no passo 0

A `v2.14.0` do Open saiu em 2026-11-13 (`main` = `e583889`, PR #28): F17b. O sdd-starter passou a gerar **15 skills** do
Open (as 10 da F17 mais brainstorm, handoff, governança, release em modo iniciante e ux-review-builder), e `docs/`,
`exemplos/` e `tests/` vêm do gerador; starter **`v1.5.18`** (PR #11 de lá). Pelo **Cronograma recomendado** do plano, a
próxima frente é a **F17c**: `sdd-define`, `sdd-design` e `sdd-build`, as 3 mais baixadas do starter, ainda congeladas.

## Onde abrir esta sessão

A frente **já existe** (aberta em 2026-11-13 pela `sdd-new-session`): worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3`, branch `feat/f17c-starter-etapa3`, de `origin/main` =
`e583889` (`v2.14.0`). A janela do Cursor foi aberta nela; cole o prompt abaixo lá. A worktree da F17b (`/Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2`) e o clone do
starter dela (`/Users/robertoduarte/rdd-worktrees/sdd-starter-f17b-gerado`) podem ser removidos depois de conferir que nada
ficou só neles (os documentos e a evidência da F17b estão na branch de documentos).

## Prompt para colar na sessão nova

```text
Executar a frente F17c do SDD Open: starter gerado, etapa 3 (Decisão 5) — sdd-define, sdd-design e sdd-build em modo web,
geradas do Open. Repo público robertodiasduarte/sdd-open. A frente já está aberta:
/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3, branch feat/f17c-starter-etapa3, de origin/main = e583889 =
v2.14.0. Não rode a sdd-new-session. Responda em português.
Execute o pipeline inteiro até a release (passo 0, brainstorm, define, design, build, release, fechamento) e pergunte ao
Roberto somente o que for necessário: as decisões dele (escopo, paradas novas, curadoria, passar do teto do método) e as
autorizações (a frase do Open; o OK de cada push, PR e merge no starter). Decisão de rotina, decida e registre.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado" (a frase exata): pergunte, não presuma.
A F17c toca dois repositórios: o gerador mora no Open; o robertodiasduarte/sdd-starter recebe a cópia gerada e pede OK PRÓPRIO
do Roberto para cada push, PR e merge lá (merge na main do starter publica a Release automática). Na F17b o classificador do
modo automático do Claude Code bloqueou push, PR e merge no starter mesmo com o OK: entregue os comandos exatos para o Roberto
rodar (ou ele cria uma regra de permissão). Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do
repositório privado, texto do e-book de segurança) entra em nenhum dos dois.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes" (F17, F17b, F17c)
  e o "Cronograma recomendado"
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → a seção "2026-11-13 — F17b"
  (Pendências e Alertas) e os Eventos de 2026-11-13
- git show origin/docs/incorporar-starter:sdd/features/BRAINSTORM_F17B_STARTER_ETAPA2.md e DESIGN_F17B_STARTER_ETAPA2.md
  (a abordagem A1 por peso: skill pesada ganha references/<MODO>.md e o gerador monta a skill do starter dele, regra "skill
  de modo" em scripts/starter/modos.tsv; a simplicidade do iniciante como critério medido)
- git show origin/docs/incorporar-starter:sdd/reports/evidence/F17B_STARTER_ETAPA2/PARADAS.md (o formato da tabela de
  paradas) e .../scripts/ (iniciante.py, ensaio.sh, checagens-starter.sh, sabotagem.sh: reaproveite)
- o ## Sempre de sdd/playbook.md da frente; o starter publicado: gh release view --repo robertodiasduarte/sdd-starter

0. Sobras da F17b, na branch da frente (sobem com a release dela):
   a. Curadoria do playbook da F17b (decisão do Roberto: aqui, não na release da F17b): os 2 candidatos do BUILD_REPORT
      ("ls a b" sai ≠ 0 quando um caminho falta; teste de texto por regex de comando deixa passar a obrigação em prosa)
      e as contagens, pelo playbook-curator.sh (--colher sobre os documentos da F17b copiados da branch de documentos):
      uma decisão do Roberto por candidato.
   b. Pendentes da F17b (decida com o Roberto se entram): o version gate contra a v1.5.17 real ficou fora do Verify Gate
      (a réplica do teste não pode ter as versões reais; hoje a prova é a geração de ensaio antes do PR); o --conferir não
      aceita revisão feita com --paths, mesmo quando o resto do diff é cópia byte a byte já publicada (na F17b precisou de
      dispensa do Roberto); o exemplo preenchido da handoff do starter (HANDOFF_EXAMPLE.md) saiu na geração.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.14.0.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - Antes do brainstorm, compare item a item (agente em contexto novo, só leitura) as skills define, design e build do
     starter v1.5.18 (congeladas) com as do Open: o que o starter tem melhor para quem está na web, e as paradas de cada uma
     (a tabela de paradas é critério de aceite, como na F17b).
   - Brainstorm com as decisões abertas: o modo web das 3 (molde dentro da skill, prova sem script, entrega no chat) pela
     regra "skill de modo" (references/<MODO>.md + 1 linha no SKILL.md do Open) ou no próprio texto; o alinhamento das
     pastas (as congeladas gravam em sdd/ sem subpastas; as geradas, nas pastas do Open); o exemplos/baixar-nfse (kit do build
     congelado, grava em sdd/); se o starter fica sem nenhuma congelada ao fim. Meta do Roberto: manutenção num repositório
     só; o modo de trabalhar do iniciante continua simples, sem restrições complexas (paradas novas só com o OK dele).
   - O gerador: skill nova na lista pede linha no scripts/starter/openai.tsv (semente: o agents/openai.yaml do starter),
     trocas em scripts/starter/trocas/ e versão maior que a do starter (o gerador confere). Moldes mudados por troca
     (_moldes/) mudam toda skill que os leva: o gerador pede versão nova em cada uma.
   - Teste do iniciante (claude -p --tools "", pasta vazia, sem MCP, várias voltas, roteiro e critério escritos ANTES,
     3 de 3 por skill; pergunta sem entrega reprova) e tabela de paradas com o OK do Roberto em cada parada nova.
   - A geração final parte da tag publicada desta frente, num clone limpo do starter (do GitHub), numa branch; as 9 checagens
     do CI de lá (scripts/checagens-starter.sh) antes do PR.
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md; no fim, eval-revisores.sh no relatório.
   - Documentos SDD (features, reports, reviews, evidence) ficam fora do git na pasta da frente e vão no fim para a branch de
     documentos (worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16).

Revisão adversarial: saldo da OpenRouter em US$ 13,72 em 2026-11-13 (fim da F17b; as 3 rodadas dela custaram US$ 0,13 pagos),
e a chave tem outro uso: leia /credits antes de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia que
funcionou na F16, F18 + F20, F17 e F17b: claude revisa, openrouter (qwen) audita, --no-revisor2 e --no-desempate (codex sem
cota). A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no
ambiente do comando, sem imprimir. O --conferir da release exige revisão do diff inteiro, sem --paths: se a frente copiar
arquivos grandes do starter, decida antes com o Roberto (rodar sem --paths, ou dispensa com a prova do diff -rq).
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto. Rode o raio de impacto
(0b) antes da última rodada (na F17b achou o aviso do doctor calado).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~27 min, teto 45; macOS ~46 min, teto 75; Windows ~5 min, teto
30). Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Rode o Verify Gate com a máquina livre.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F17c na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.

Não faça:
- nada da F15 nesta sessão se a frente tocar a sdd-release;
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou merge no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a trava do CI recusa);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por script
bash com rc=$? e 1ª linha "$ comando" (o report-lint exige); no zsh, ${PIPESTATUS[0]} é vazio (LM-018) e "$c" não se divide em
palavras (use um script bash). O gerador só roda igual ao da tag (senão 64): para gerar, use uma worktree da tag; para ensaiar
antes da tag, um repositório temporário com tag local (scripts/ensaio.sh). sdd-release em 500 linhas (teto do teste). Contagens
fixadas em testes: 22 skills, 31 perguntas em 26 arquivos do sdd-decisoes-lint, versões de skill: skill ou pergunta nova mexe
nelas. A ux-review-builder não segue o padrão sdd-*: o init, o sync, o lint do CI e os testes a listam à parte.
```
