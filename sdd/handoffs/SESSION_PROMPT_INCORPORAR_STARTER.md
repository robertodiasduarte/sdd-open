# Continuar: INCORPORAR_STARTER — próxima frente do Open (F17 pelo plano, ou a F16W), com as sobras da F16 no passo 0

A `v2.11.0` do Open saiu em 2026-11-11 (`main` = `69b7f6b`): F16, ambiente agnóstico e proativo. As skills de entrada
descobrem cedo o `gh`, o login e o editor (a `sdd-new-session` pergunta o editor padrão uma vez e grava em
`git config sdd.editor`), funcionam sem editor, e os scripts acham o Python no Windows. O Windows ficou "sem teste automático":
só o caminho do aluno roda lá; o porte da suíte inteira virou a frente **F16W**. Pelo plano (seção 10), depois da F16 vem a
**F17 Starter gerado a partir do Open**; o Roberto escolhe entre ela e a F16W no começo da sessão.

## Onde abrir esta sessão

Worktree nova, nascida de `origin/main` = `69b7f6b` (use a `sdd-new-session`). A worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f16-ambiente` guarda as revisões da F16 (`sdd/reports/reviews/EXTERNAL_REVIEW_2026111*`):
não a apague sem arquivar essa pasta antes.

## Prompt para colar na sessão nova

```text
Executar a próxima frente do SDD Open: a F17 (Starter gerado a partir do Open) pelo plano, ou a F16W (porte da suíte ao
Windows) — pergunte ao Roberto qual antes de começar. Repo público robertodiasduarte/sdd-open, worktree nova de origin/main
69b7f6b (v2.11.0). Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do repositório privado) entra aqui.
O starter (robertodiasduarte/sdd-starter) pede OK próprio do Roberto: push em skills/** na main de lá publica Release sozinho.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes" (fonte única),
  a seção da frente escolhida (F17 ou F16W) e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de
  2026-11-10 e 2026-11-11 e a seção "2026-11-11 — F16 Ambiente agnóstico e proativo" (Pendências e Alertas)
- git show origin/docs/incorporar-starter:sdd/reports/BUILD_REPORT_F16_AMBIENTE.md → Windows (as 5 medições) e Candidatos
- o ## Sempre de sdd/playbook.md da worktree

0. Sobras da F16, na branch da frente nova (sobem com a release dela):
   a. Curadoria do playbook: 5 candidatos em sdd/reports/BUILD_REPORT_F16_AMBIENTE.md (blocos <<<CANDIDATO_PLAYBOOK, na
      branch de documentos), uma decisão do Roberto por candidato; colher as contagens com
      bash sdd/bin/playbook-curator.sh --colher <pasta com DESIGN, BUILD_REPORT e AVALIACAO da F16> sdd/playbook.md
      (LM-012 mordeu; lição que passa a ter mordeu ≥ 1 precisa de classificação em sdd/invariants.md: pergunte).
      Depois: bash sdd/bin/playbook-lint.sh sdd/playbook.md e o --validar-inv (exit 0), e rode tests/test_sdd_open.py (o init
      instala as invariantes: um check= que só existe no pacote reprova).
   b. Rodada 4, R1: com uma sdd-checar-ambiente anterior à 1.5.0 instalada, `checar.sh --editores` cai no modo normal e sai 0;
      a sdd-new-session deve conferir a versão da checar-ambiente (ou o formato "<nome><TAB><comando>") antes de usar a lista.
   c. Pequenos (decida com o Roberto se entram): aviso do Python repetido no doctor; o loop de deriva do doctor sem
      sdd/bin/lib/python.sh; governanca-fronteira.sh exige Python antes do --help; o resumo do checar mostra o editor
      detectado, não o do git config sdd.editor; o guia do aluno sem a linha gh: do inventário.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.11.0.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - F17: o starter é gerado a partir do Open; a 1ª geração exige comparar skill a skill antes (plano, seção da F17). As skills
     de entrada da v2.11.0 chegam ao starter por ela.
   - F16W: o 1º passo é medir módulo a módulo no windows-latest (Git Bash + Python nativo), com teto por módulo; prioridade:
     o teto do checar.sh no Windows (o vigia por grupo de processos não corta a rede pendurada; 5 testes pulados por SEM_SINAL).
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md e confere com bash sdd/bin/ledger-revisao-lint.sh; no fim,
     rode bash sdd/bin/eval-revisores.sh e guarde a tabela no relatório.

Revisão adversarial: saldo da OpenRouter em ~US$ 19,9 em 2026-11-11 (leia em /credits antes de cada rodada paga;
limit_remaining é o limite da chave, não o saldo). Cadeia que funcionou na F16: claude revisa, `openrouter` (qwen) audita,
--no-revisor2 (codex sem cota, gemini sem credencial; 2º revisor pago evitado pela LM-010) — registre a dispensa do 2º revisor
no --conferir. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY=
no ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir.
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto (na F16 foram 5 rodadas,
cada extra perguntada). Na release, rode o raio de impacto (0b) antes da última rodada: na F16 ele achou uma quebra.

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~26 min, teto 45; macOS 39 a 47 min, teto 75; Windows caminho
do aluno ~4 min, teto 30). Se a suíte crescer, olhe o teto ANTES da tag: tag com job cancelado fica sem Release e não se move.
Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Número com 11 dígitos em arquivo do pacote
(id de run do CI incluso) é barrado pelo publish-gate: cite o commit.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree de documentos da branch
docs/incorporar-starter), a linha da frente na tabela "Estado das frentes" do plano, os documentos da frente e este
SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.

Não faça:
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- nada no sdd-starter sem OK próprio do Roberto;
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Pulo de plataforma nos testes só por
constante de tests/apoio.py. gh_estado/instalar_gh existem iguais em checar.sh e inventario.sh; o bloco INSTALAR é igual nas 3
skills de entrada: mudou num, mude nos outros.
```
