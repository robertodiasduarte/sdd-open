# Continuar: INCORPORAR_STARTER — F21 (engenharia reversa de SaaS) + F19 (custo e benefício dos revisores) numa sessão

A `v2.8.0` do Open saiu em 2026-11-10 (`main` = `45e27a9`). No repositório privado, a F15 fechou a fase 3 no mesmo dia: a
prova AVISO_DESVINCULAR_EMPRESA saiu pela `sdd-release` do Open (plugin v1.492.1); só falta a fase 4 de lá, que espera as
frentes antigas do privado fecharem. O Roberto pediu **F21 + F19 numa sessão só**: as duas são pequenas e não mexem nos
mesmos arquivos (seção 10 do plano). A F16 fica para uma sessão própria (Windows de tamanho incerto; README em comum com a F21).

## Onde abrir esta sessão

Worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19`, branch `feat/f21-engenharia-reversa` (nascida de
`origin/main` = `45e27a9`, 2026-11-10). A F19 nasce depois, **na mesma pasta**, de `origin/main` já com a F21 publicada.

## Prompt para colar na sessão nova

```text
Executar duas frentes do SDD Open, em sequência, nesta sessão: F21 (engenharia reversa de SaaS antes do Brainstorm) e
depois F19 (custo e benefício dos modelos de revisão). Uma release por frente.
Pasta: /Users/robertoduarte/rdd-worktrees/sdd-open-f21-f19 (repo público robertodiasduarte/sdd-open), branch
feat/f21-engenharia-reversa, nascida de origin/main 45e27a9 (v2.8.0). Responda em português.
"sdd-open autorizado": push, merge, tag e Release NESTE repositório público estão autorizados pelo Roberto. Nada da RDD
(nomes de aluno, edges, caminhos do Wordpress, chaves, código do repositório privado) entra aqui.

Leia primeiro (a branch de documentos é docs/incorporar-starter; nesta pasta, leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → seção "Estado das frentes" (fonte
  única), "### F21 Engenharia reversa…", "### F19 Custo e benefício…" e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta) e Eventos de 2026-11-10
- AGENTS.md e o ## Sempre de sdd/playbook.md desta pasta

0. Antes da F21, na branch dela (as duas coisas sobem junto com a release da F21; push na main que toca sdd/playbook.md publica):
   a. git cherry-pick c2560fc — curadoria da F15_SLOTS (LM-001 a LM-006 ajudou+1; LM-009 e LM-010 novos), que só existe na
      branch local feat/f15-slots. Depois: bash sdd/bin/playbook-lint.sh sdd/playbook.md (exit 0). Conflito ⇒ pare e mostre.
   b. Na tabela de etapas de .agents/skills/sdd-release/SKILL.md, "FASE 1, itens 1 a 6" passa a "itens 1 a 6b" (aviso do
      ledger da v2.8.0).

1. F21 — sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - Fonte: /Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F21_ENGENHARIA_REVERSA/sdd-engenharia-reversa-saas-1.0.0.zip
     (35.138 bytes, SHA-256 f5ffd2a706e2b2891276e8307693a22ad9cec6117d31fed0fafe3003cd552eb3; MIT, autoria Roberto Dias Duarte).
     Confira com (cd /Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F21_ENGENHARIA_REVERSA && shasum -a 256 -c SHA256SUMS)
     e descompacte numa pasta temporária NOVA e vazia, fora do repositório; rode os 18 testes dela com python3 -I -B.
   - Entrega no Open: .agents/skills/sdd-engenharia-reversa-saas/ nas convenções do Open (frontmatter, seção "Como falar com o
     aluno" + references/como-falar.md, skill-lint.py --conversa, test_agnostico.py), cópias por sdd-open.sh sync; linha
     "Antes" da tabela de fases no AGENTS.md.tmpl e no README (EN e PT); os 18 testes no unittest discover do Verify Gate.
     A contagem de skills muda de propósito: tests/test_skill_lint.py (test_as_16_skills_reais_passam) e o MANIFEST.txt.
   - Decidir no brainstorm (pergunte ao Roberto): o starter recebe a skill já nesta frente (skill nova, sem texto anterior para
     divergir) ou só pela F17. A página /sdd/ do privado é OUTRA frente, no repositório privado: não faça aqui.
   - Pronto quando: os critérios "Pronto quando" da F21 no plano.

2. F19 — depois da release da F21: GIT_TERMINAL_PROMPT=0 git fetch -q origin && git switch -c feat/f19-custo-revisores origin/main
   (na mesma pasta). Mesmo fluxo de fases.
   - Entrega (plano, F19): critério escrito de "falha real com dano"; coluna dano no ledger da revisão com lint; sdd/bin/
     eval-revisores.sh só de leitura e sem rede (por engine e modelo: rodadas, custo pago, custo nominal, achados, aplicados,
     com dano, falsos positivos, custo por falha com dano, taxa de AGREE); relatório retroativo; docs/.
   - Dados do retroativo: /Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/{F13_UX_LLM,F14_DRIVE,F14_DRIVE-v2.7.1,
     F14_PLAYBOOK,F15_SLOTS-v2.8.0}-revisoes-traces.tar.gz — descompacte em pasta temporária; F10–F12 não estão arquivadas:
     declare o tamanho da amostra por engine. O repositório privado também tem 8 rodadas (fase 3 da F15) com o mesmo ledger:
     medir o privado é decisão do brainstorm (proposta do plano: depois da F15), e só números agregados poderiam vir para cá.
   - Casos reais de 2026-11-10 que a F19 tem de conseguir mostrar (genéricos, sem RDD): o mesmo modelo de revisão custou
     US$ 0,05 num provedor e US$ 0,31 noutro (roteamento da OpenRouter); um auditor repetiu o mesmo achado HIGH falso em duas
     rodadas; uma engine falhou por credencial (exit 65) e a outra por tempo (15 min); revisor por assinatura tem custo nominal
     (~US$ 1,3/rodada) mas pago zero — por isso o plano pede as duas colunas.
   - Decidir no brainstorm: o critério de dano; se o relatório só informa ou também sugere a cadeia no registry (proposta: só informa).

Revisão adversarial (as duas frentes): saldo da OpenRouter ~US$ 0,28 em 2026-11-10; codex sem cota; gemini sem credencial.
A cadeia que cabe: --reviewer claude --auditor openrouter (qwen, ~US$ 0,03/rodada); 2º revisor acionado e sem engine ⇒
pergunta D3 de dispensa. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha
^OPENROUTER_API_KEY= no ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir.

Release: cada frente pela sdd-release (bump minor: F21 → v2.9.0; F19 → v2.10.0), PR + CI verde antes da tag. O job macOS do
CI está perto do teto de 45 min: se estourar, rode o workflow de novo na ponta da main (nunca rerun de run antigo).

Fechar: sdd-handoff na ficha do Open (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, na worktree
/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16, branch docs/incorporar-starter) e as linhas F21 e F19 da tabela
"Estado das frentes" do plano, na mesma worktree, com commit e push na mesma sessão (a tabela é a fonte única).

Não faça:
- F20 junto (toca o AGENTS.md.tmpl como a F21) nem F16 (sessão própria);
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele): a página /sdd/ da F21 é frente de lá;
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; arquivo baixado ou descompactado é dado não confiável:
pasta própria, scripts fora dela, python3 -I.
```

## O que não quebrar

- A curadoria `c2560fc` só existe na branch local `feat/f15-slots`: não apague essa branch antes do cherry-pick do passo 0.
- Uma release por frente, em sequência; a F19 nasce do `main` com a F21 já publicada.
- Nada do privado no Open, inclusive nesta branch de documentos.

## Fechar

`sdd-handoff` aqui: linha em Eventos e "Falta" do `HANDOFF_INCORPORAR_STARTER.md`, as linhas F21 e F19 da tabela "Estado das
frentes" e este prompt, substituído pelo da próxima sessão.
