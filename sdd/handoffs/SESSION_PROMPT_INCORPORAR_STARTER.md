# Continuar: INCORPORAR_STARTER — próxima frente do Open (pelo plano, a F16), com as sobras da F21 e da F19 no passo 0

A `v2.10.1` do Open saiu em 2026-11-10 (`main` = `36d0454`): F19, custo e benefício dos modelos de revisão (a tag `v2.10.0`
existe, sem Release: o teto do CI cancelou o job; não a mova). No mesmo dia
saiu a `v2.9.0` (`9581740`): F21, a skill `sdd-engenharia-reversa-saas`, que também foi para o starter (`v1.5.16`). As duas
frentes deixaram sobras pequenas, que entram no passo 0 da próxima frente. Pelo plano (seção 10), a próxima é a **F16
Ambiente agnóstico e proativo**, em sessão própria. Se o Roberto preferir outra frente, o passo 0 vale do mesmo jeito.

## Onde abrir esta sessão

Worktree nova, nascida de `origin/main` = `36d0454` (use a `sdd-new-session`). A worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19` guarda as revisões e os traces das duas frentes: não a apague sem
arquivar `sdd/reports/reviews/` e `sdd/traces/` antes.

## Prompt para colar na sessão nova

```text
Executar a próxima frente do SDD Open (pelo plano, F16 Ambiente agnóstico e proativo; confirme com o Roberto antes de começar).
Repo público robertodiasduarte/sdd-open, worktree nova de origin/main 36d0454 (v2.10.1). Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do repositório privado) entra aqui.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes" (fonte única),
  a seção da frente escolhida e a seção 10 (pares); para a F16, também sdd/features/ESCOPO_F16_AMBIENTE.md
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de 2026-11-10
  e a seção "2026-11-10 — F21 Engenharia reversa … + F19 Custo dos revisores" (Pendências e Alertas)
- AGENTS.md e o ## Sempre de sdd/playbook.md da worktree

0. Sobras da F21 e da F19, na branch da frente nova (sobem com a release dela):
   a. Curadoria do playbook: 3 candidatos em sdd/reports/BUILD_REPORT_F21_ENGENHARIA_REVERSA.md e 2 em
      sdd/reports/BUILD_REPORT_F19_CUSTO_REVISORES.md (blocos <<<CANDIDATO_PLAYBOOK, na branch de documentos). Uma decisão do
      Roberto por candidato. Depois: bash sdd/bin/playbook-lint.sh sdd/playbook.md (exit 0).
   b. docs/adversarial-review.md e docs/pt-BR/adversarial-review.md: a tabela de colunas da seção eval-revisores ganha a
      coluna Cobrança, que o script já imprime (tests/test_f19_textos.py confere as colunas).
   c. sdd/bin/eval-revisores.sh: papel com engine "indisponível", sem exit e sem custo no META.txt, hoje é pulado sem aviso;
      passa a ir para "fora da conta", com teste em tests/test_eval_revisores.py.
   d. .gitignore do pacote (__pycache__/, *.pyc, sdd/reports/reviews/, sdd/traces/): confira MANIFEST.txt e
      scripts/publish-gate.sh, que tratam arquivo não declarado como erro.
   Bump das skills tocadas e scripts/check-versions.py --base v2.10.1.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   Desde a v2.10.1 o passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md (molde em
   sdd/templates/LEDGER_REVISAO_TEMPLATE.md, critério em sdd/review/CRITERIO_DANO.md) e confere com
   bash sdd/bin/ledger-revisao-lint.sh; o item 8 da sdd-release confere o lint de novo. No fim, rode
   bash sdd/bin/eval-revisores.sh e guarde a tabela no relatório: é a 2ª frente com dano marcado.

Revisão adversarial: saldo da OpenRouter em US$ 0,07 em 2026-11-10 (a chamada do auditor não cabe: exit 67 em 2 segundos);
codex sem cota; gemini sem credencial. Antes da 1ª rodada, leia o saldo em /credits (limit_remaining é o limite da chave, não
o saldo) e pergunte ao Roberto: recarregar, ou rodar com uma engine só (--um-engine, a mesma revisa e audita, declarado no
ledger). A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no
ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir.
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador. Passar do teto é pergunta ao Roberto, nunca decisão do agente
(na F19 foram 5 e 3, cada extra perguntado).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~26 min, teto 45; macOS de 30 a 45 min, teto 60: se a suíte
crescer, olhe o teto ANTES da tag, porque tag com job cancelado fica sem Release).
Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic).

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree
/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16, branch docs/incorporar-starter), a linha da frente na tabela
"Estado das frentes" do plano e os documentos da frente (features, reports, reviews, evidence), com commit e push na mesma sessão.

Não faça:
- F20 junto da F18 sem brainstorm conjunto; F17 antes da F16;
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele): a página /sdd/ da F21 é frente de lá;
- nada no sdd-starter sem OK próprio do Roberto: push em skills/** na main de lá publica Release sozinho;
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A (o pacote ainda não tem .gitignore): add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I.
```

## O que não quebrar

- O arquivo `LEDGER_REVISAO_{F}.md` guarda só o ledger: toda linha de tabela dele é conferida, inclusive em comentário e
  em bloco cercado.
- `linhas_uteis` e `linha_solta` existem iguais em `ledger-revisao-lint.sh` e `eval-revisores.sh`: mudou num, mude no outro.
- Nada do privado no Open, inclusive nesta branch de documentos; nem nome de produto real de terceiro.

## Fechar

`sdd-handoff` aqui: linha em Eventos e "Falta" do `HANDOFF_INCORPORAR_STARTER.md`, a linha da frente na tabela "Estado das
frentes" e este prompt, substituído pelo da próxima sessão.
