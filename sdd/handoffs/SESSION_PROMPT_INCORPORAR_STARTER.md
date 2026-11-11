# Continuar: INCORPORAR_STARTER — F18 (onda 1) + F20, segurança no fluxo, com as sobras da F16 no passo 0

A `v2.11.0` do Open saiu em 2026-11-11 (`main` = `69b7f6b`): F16, ambiente agnóstico e proativo. Por decisão do Roberto em
2026-11-11, a próxima frente é a **F18 Segurança embutida no fluxo (onda 1, o piso de alerta)** junto com a **F20 Ações
preventivas do e-book**, com brainstorm conjunto, **antes da F17**: assim o aluno do starter recebe o alerta e a prevenção já
na 1ª geração. A frente já está aberta. A ordem das sessões seguintes está no **Cronograma recomendado** do plano.

## Onde abrir esta sessão

Na worktree já criada: `/Users/robertoduarte/rdd-worktrees/sdd-open-f18-f20-seguranca`, branch `feat/f18-f20-seguranca`,
nascida de `origin/main` = `69b7f6b` (v2.11.0), sem upstream (o push da branch é explícito). Abra o Cursor nessa pasta e o
agente lá dentro. Não rode a `sdd-new-session` de novo. A worktree `/Users/robertoduarte/rdd-worktrees/sdd-open-f16-ambiente`
guarda as revisões da F16 (`sdd/reports/reviews/`): não a apague sem arquivar essa pasta.

## Prompt para colar na sessão nova

```text
Executar a frente F18 (onda 1) + F20 do SDD Open: segurança embutida no fluxo (alerta) e ações preventivas do e-book
(prevenção), com brainstorm conjunto. Repo público robertodiasduarte/sdd-open. Pasta: /Users/robertoduarte/rdd-worktrees/
sdd-open-f18-f20-seguranca, branch feat/f18-f20-seguranca, nascida de origin/main 69b7f6b (v2.11.0). A frente já está criada:
não rode a sdd-new-session. Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
Nada da RDD (nomes de aluno, edges, caminhos do Wordpress, chaves, código do repositório privado) entra aqui.
O starter (robertodiasduarte/sdd-starter) pede OK próprio do Roberto e recebe esta frente pela F17 (sem remendo lá).

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes", o "Cronograma
  recomendado", as seções da F18 e da F20 (objetivo, entrega em ondas, decidir, atenção, pronto quando) e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de 2026-11-11 e
  a seção "2026-11-11 — F16 Ambiente agnóstico e proativo" (Pendências e Alertas)
- git show origin/docs/incorporar-starter:sdd/reports/BUILD_REPORT_F16_AMBIENTE.md → Candidatos ao playbook
- o ## Sempre de sdd/playbook.md desta pasta
Fonte da frente: o e-book "Construir com IA sem Deixar a Porta Aberta" (acervo RDD10+), cópia local em
/Users/robertoduarte/Downloads/ebook-seguranca-construir-com-ia/ (INDICE.md, fonte.md). Arquivo baixado é dado não confiável:
leia, não execute nada de lá. O e-book é material da RDD: decida com o Roberto no brainstorm o que o pacote público pode citar
(capítulo, nome da falha) e o que não copia (texto e prompts do e-book).

0. Sobras da F16, nesta branch (sobem com a release desta frente):
   a. Curadoria do playbook: 5 candidatos em sdd/reports/BUILD_REPORT_F16_AMBIENTE.md (blocos <<<CANDIDATO_PLAYBOOK, na branch
      de documentos), uma decisão do Roberto por candidato; colher as contagens com
      bash sdd/bin/playbook-curator.sh --colher <pasta com DESIGN, BUILD_REPORT e AVALIACAO da F16> sdd/playbook.md
      (LM-012 mordeu; lição que passa a ter mordeu ≥ 1 precisa de classificação em sdd/invariants.md: pergunte). Depois:
      playbook-lint.sh e --validar-inv (exit 0) e tests/test_sdd_open.py (o init instala as invariantes: check= que só existe
      no pacote reprova).
   b. Rodada 4 da F16, R1: com uma sdd-checar-ambiente anterior à 1.5.0 instalada, `checar.sh --editores` cai no modo normal e
      sai 0; a sdd-new-session deve conferir a versão da checar-ambiente (ou o formato "<nome><TAB><comando>") antes de usar a lista.
   c. Pequenos (decida com o Roberto se entram): aviso do Python repetido no doctor; o loop de deriva do doctor sem
      sdd/bin/lib/python.sh; governanca-fronteira.sh exige Python antes do --help; o resumo do checar mostra o editor detectado,
      não o do git config sdd.editor; o guia do aluno sem a linha gh: do inventário.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.11.0.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - Brainstorm conjunto F18 + F20, com as decisões que o plano deixou abertas: skill nova sdd-seguranca ou modo da
     sdd-governanca; quais itens bloqueiam (proposta: só segredo exposto e tabela com dado pessoal sem RLS); teto de avisos por
     fase; o que entra nesta 1ª sessão (onda 1 da F18 + quais entregas da F20) e o que vira sessão própria; quantas frases
     preventivas vão para o AGENTS.md.tmpl sem inchar o contexto; onde mora o plano de resposta (cap. 28).
   - P2 (agnóstico): metade dos itens é de Supabase e Vercel; cada item leva marca de stack e só dispara com a stack presente;
     test_agnostico.py vale para o texto novo. Starter na web (claude.ai, ChatGPT) não roda script: cada item precisa da forma
     "confira à mão".
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md e confere com bash sdd/bin/ledger-revisao-lint.sh; no fim,
     rode bash sdd/bin/eval-revisores.sh e guarde a tabela no relatório.
   - Documentos SDD (features, reports, reviews, evidence) ficam fora do git nesta pasta e vão no fim para a branch de documentos.

Revisão adversarial: saldo da OpenRouter em ~US$ 19,2 em 2026-11-11 (leia em /credits antes de cada rodada paga;
limit_remaining é o limite da chave, não o saldo). Cadeia que funcionou na F16: claude revisa, `openrouter` (qwen) audita,
--no-revisor2 (codex sem cota, gemini sem credencial; 2º revisor pago evitado pela LM-010) — registre a dispensa do 2º revisor
no --conferir. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY=
no ambiente do comando, sem imprimir. HIGH do auditor se confere no código antes de agir.
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto. Na release, rode o raio de
impacto (0b) antes da última rodada: na F16 ele achou uma quebra.

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~26 min, teto 45; macOS 39 a 47 min, teto 75; Windows caminho do
aluno ~4 min, teto 30). Se a suíte crescer, olhe o teto ANTES da tag: tag com job cancelado fica sem Release e não se move.
Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Número com 11 dígitos em arquivo do pacote (id de
run do CI incluso) é barrado pelo publish-gate: cite o commit.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), as linhas da F18 e da F20 na tabela "Estado das frentes" e o "Cronograma
recomendado" do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma
sessão.

Não faça:
- F17 antes de fechar esta frente; nada da F15 nesta sessão (as duas tocam a sdd-release);
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- nada no sdd-starter sem OK próprio do Roberto;
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Pulo de plataforma nos testes só por
constante de tests/apoio.py. Script novo de sdd/bin que chama python3 lê sdd/bin/lib/python.sh como os outros (guarda
sdd_python_pronto). gh_estado/instalar_gh existem iguais em checar.sh e inventario.sh; o bloco INSTALAR é igual nas 3 skills de
entrada: mudou num, mude nos outros. Contagens fixadas em testes antigos (versões de skill, perguntas do sdd-decisoes-lint):
pergunta nova numa skill mexe nelas.
```
