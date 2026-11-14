# Continuar: INCORPORAR_STARTER — F16W Windows: porte da suíte, com as sobras da F17c no passo 0

A `v2.15.0` do Open saiu em 2026-11-14 (`main` = `97503a7`, PR #29): F17c. O sdd-starter passou a gerar **as 18 skills**
do Open, nenhuma congelada (define, design e build saem do modo web delas); starter **`v1.5.19`** (PR #12 de lá). A geração
do starter (Decisão 5) está completa. Pelo **Cronograma recomendado** do plano, a próxima frente é a **F16W** (porte da
suíte para o Windows); a F15 fase 4 continua esperando a última frente antiga do privado fechar.

## Onde abrir esta sessão

A frente **ainda não existe**. Abra com a `sdd-new-session` a partir do checkout principal do Open
(`/Users/robertoduarte/rdd-public/sdd-open` ou outra worktree limpa de `main`), nome sugerido `f16w-windows`, de
`origin/main` = `97503a7` = `v2.15.0`, e cole o prompt abaixo na janela que ela abrir. A worktree da F17c
(`/Users/robertoduarte/rdd-worktrees/sdd-open-f17c-starter-etapa3`), a da tag (`/Users/robertoduarte/rdd-worktrees/sdd-open-v2.15.0`)
e os clones do starter dela (`/Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-gerado`, `.../sdd-starter-f17c-ref`) podem ser
removidos depois de conferir que nada ficou só neles (documentos e evidência da F17c estão na branch de documentos; as 3
pastas `EXTERNAL_REVIEW_20261114-*` ficam só na worktree da F17c).

## Prompt para colar na sessão nova

```text
Executar a frente F16W do SDD Open: Windows, porte da suíte. Repo público robertodiasduarte/sdd-open. Abra a frente pela
sdd-new-session (se o Roberto ainda não abriu) de origin/main = 97503a7 = v2.15.0. Responda em português.
Execute o pipeline inteiro até a release (passo 0, brainstorm, define, design, build, release, fechamento) e pergunte ao
Roberto somente o que for necessário: as decisões dele (escopo, curadoria, passar do teto do método) e as autorizações.
Decisão de rotina, decida e registre. Push, merge, tag e Release neste repositório pedem a frase do Roberto
"sdd-open autorizado" (a frase exata; "push autorizado sdd-open" não vale): pergunte, não presuma. Nada da RDD entra.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" (F16, F16W, F17c)
  e o "Cronograma recomendado"
- git show origin/docs/incorporar-starter:sdd/features/ESCOPO_F16_AMBIENTE.md → §3.5 (testes no Windows)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md → as seções "2026-11-14 — F17c"
  (Pendências e Alertas) e "2026-11-11 — F16" (o que a 1ª medição no Windows achou) e os Eventos de 2026-11-14
- o ## Sempre de sdd/playbook.md da frente

0. Sobras da F17c, na branch da frente (sobem com a release dela):
   a. Curadoria do playbook da F17c (decisão do Roberto: aqui, não na release da F17c): os 2 candidatos do BUILD_REPORT
      (`claude -p --tools ""` não simula a web: anuncia uma pasta gravável; juiz por regex de comportamento de LLM é só
      triagem, quem julga é um leitor novo) e as contagens, pelo playbook-curator.sh --colher sobre os documentos da F17c
      copiados da branch de documentos para UMA pasta só (o --colher não desce em subpastas): uma decisão do Roberto por
      candidato.
   b. Pendentes (decida com o Roberto se entram): o build web do starter fechou 2 de 3 no teste do iniciante e o texto foi
      consertado depois sem nova medição (série 6 pela OpenRouter, ~US$ 1,40, julgada por leitor novo); o version gate
      contra a versão real do starter fora do Verify Gate e o --conferir sem aceitar revisão com --paths (da F17b).
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.15.0.

1. A frente (escopo no plano, linha F16W): medir a suíte no windows-latest módulo a módulo (a 1ª medição, em 2026-11-11,
   rodou 282 de ~1.900 testes em 90 min, com 156 quebras); prioridade: o teto do checar.sh no Windows (o vigia por grupo de
   processos não corta a rede pendurada, LM-016); os 4 achados guardados (tasklist, report-lint, sdd-archive, O_NOFOLLOW);
   depois, decidir com o Roberto o piso (quais módulos o job do Windows roda e se ele vira bloqueante). A frente toca
   .github/workflows/: não pareia com outra que mexa neles. Hoje o job testes-windows é informativo, só o caminho do aluno,
   ~5 min (teto 30).

Revisão adversarial: saldo da OpenRouter em US$ 8,73 em 2026-11-14 (fim da F17c), e a chave tem outro uso: leia /credits antes
de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia que funcionou da F16 à F17c: claude revisa,
openrouter (qwen) audita, --no-revisor2 e --no-desempate (codex sem cota); o --conferir pede --aceitar-sem-revisor2 "<motivo>".
A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no ambiente do
comando, sem imprimir. Revisão do diff inteiro, sem --paths. Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador;
passar do teto é pergunta ao Roberto. Rode o raio de impacto (0b) antes da última rodada.

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~32 min, teto 45; macOS ~51 min, teto 75; Windows ~5 min, teto
30). Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Rode o Verify Gate com a máquina livre
(~40 min, 2.151 testes em v2.15.0). Se a frente mexer em skill do starter, gere de novo pela tag num clone limpo do starter e
peça o OK próprio do Roberto para push, PR e merge lá (o modo automático bloqueia: entregue os comandos, com o número do PR em
gh pr checks/merge, e prefira o fast-forward: git push origin <branch>:main).

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F16W na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.
Ao editar a ficha, troque blocos inteiros por seção (## ...): uma troca que casa "## Eventos" no meio de uma célula deixou cópias
velhas na ficha até 2026-11-14.

Não faça:
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou merge no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a trava do CI recusa);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por script
bash com rc=$? e 1ª linha "$ comando" (o report-lint exige); no zsh, ${PIPESTATUS[0]} é vazio (LM-018). No Windows: text=True
sem encoding (LM-014), PYTHONIOENCODING no pipe do Git Bash (LM-015), kill de grupo de processos não funciona (LM-016).
Contagens fixadas em testes: 22 skills, 34 perguntas em 29 arquivos do sdd-decisoes-lint, versões de skill: skill ou pergunta
nova mexe nelas. O build gerado do starter está em 499 linhas (teto 500, test_as_3_geradas_cabem_em_500_linhas).
```
