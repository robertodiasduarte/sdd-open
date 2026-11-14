# Continuar: INCORPORAR_STARTER — F16W2 Windows: porte das quebras, com as sobras da F16W no passo 0

A `v2.16.0` do Open saiu em 2026-11-14 (`main` = `ad32fe1`, PR #30): F16W. O job `testes-windows` passou a rodar **a suíte
inteira** no `windows-latest` (16 fatias, por classe de teste, informativo); a 1ª medição deu **1.324 de 2.076 testes
passando (~64%)**, 38 de 82 módulos inteiros verdes, e as quebras vêm de poucas causas, medidas e guardadas. O Roberto
decidiu publicar e portar as quebras numa frente própria: a **F16W2**. Starter **`v1.5.20`** (PR #13 de lá). A F15 fase 4
(no repositório privado) segue esperando a última frente antiga de lá fechar; as duas podem andar em paralelo (repositórios
diferentes), mas a fase 4 deve sincronizar o privado a partir da `v2.16.0` (os hooks do Claude Code e o `checar` mudaram).

## Onde abrir esta sessão

A frente **ainda não existe**. Abra com a `sdd-new-session` a partir do checkout principal do Open
(`/Users/robertoduarte/rdd-public/sdd-open` ou outra worktree limpa de `main`), nome sugerido `f16w2-windows`, de
`origin/main` = `ad32fe1` = `v2.16.0`, e cole o prompt abaixo na janela que ela abrir. A worktree da F16W
(`/Users/robertoduarte/rdd-worktrees/sdd-open-f16w-windows`) pode ser removida depois de conferir que nada ficou só nela
(documentos e evidência da F16W estão na branch de documentos; as 3 revisões `sdd/reports/reviews/EXTERNAL_REVIEW_20261114-*`
ficam só lá).

## Prompt para colar na sessão nova

```text
Executar a frente F16W2 do SDD Open: Windows, porte das quebras. Repo público robertodiasduarte/sdd-open. Abra a frente pela
sdd-new-session (se o Roberto ainda não abriu) de origin/main = ad32fe1 = v2.16.0. Responda em português.
Execute o pipeline inteiro até a release (passo 0, brainstorm, define, design, build, release, fechamento) e pergunte ao
Roberto somente o que for necessário: as decisões dele (escopo, curadoria, passar do teto do método) e as autorizações.
Decisão de rotina, decida e registre. Push, merge, tag e Release neste repositório pedem a frase do Roberto
"sdd-open autorizado" (a frase exata; escolher uma opção não vale como a frase): pergunte, não presuma. Nada da RDD entra.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" (F16W, F16W2)
  e o "Cronograma recomendado"
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md → a seção "2026-11-14 — F16W"
  (Pendências e Alertas) e os Eventos de 2026-11-14
- a medição: sdd/reports/evidence/F16W_WINDOWS/windows/ (MEDICAO-1-491efa6.md = a tabela por unidade, MEDICAO-1-causas.txt
  = as quedas agrupadas por causa, resumo-*.tsv por fatia, logs-quebrados/ = a saída de cada unidade que quebrou)
- o ## Sempre de sdd/playbook.md da frente

0. Sobras da F16W, na branch da frente (sobem com a release dela):
   a. Curadoria do playbook da F16W (decisão do Roberto: aqui, não na release da F16W): os 3 candidatos do BUILD_REPORT
      ("bash" pelo nome no subprocess cai no bash.exe do WSL em System32; módulos de teste em paralelo derrubam testes de
      tempo; executor que põe PYTHONIOENCODING nos testes mascara a quebra do aluno) e as contagens (LM-012 mordeu), pelo
      playbook-curator.sh --colher sobre os documentos da F16W copiados da branch de documentos para UMA pasta só (o
      --colher não desce em subpastas): uma decisão do Roberto por candidato.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.16.0.

1. A frente: consertar no Windows as causas que a F16W mediu, em ordem de peso, cada uma com teste:
   (1) os scripts Python do sdd/bin imprimem ✅ num stdout cp1252 (~156 quedas e o sdd-drive em cascata): defeito do
       produto, o aluno no Git Bash roda python3 sdd/bin/design-lint.py e vê erro; o stdout desses scripts passa a UTF-8
       (como o sdd-drive.sh já faz);
   (2) o .claude/settings.json gerado pelo init do adaptador do Claude Code com caminho Windows sem escape (JSON inválido):
       defeito do produto;
   (3) caminhos C:\ × /c/ (governanca-fronteira, slot);
   (4) o gh falso dos testes (script com shebang: o Python do Windows não executa) e o resolvedor de Python nos testes;
   (5) git commit pendurado 120 s com os hooks (test_sdd_open.Hooks);
   (6) o vigia do checar no Windows: o ssh pendurado já é cortado; o askpass do editor e o gh pendurados ainda passam do
       teto (AT-004 da F16W);
   (7) os 4 achados guardados (tasklist, report-lint, sdd-archive, O_NOFOLLOW; AT-005 da F16W);
   (8) as 5 unidades no teto de 600 s (test_sdd_open.Projeto, test_claude_adapter.Projeto).
   Depois, decidir com o Roberto o piso (o job do Windows no needs: da release, quando ficar verde) e as 4 frases de
   Windows do README e do quickstart (hoje: "cerca de 64% dos testes passam").
   Medir exige push da branch: peça a frase cedo, já para a 1ª medição do build. Na F16W o Roberto escolheu medir só no PR
   do fim, e o porte ficou às cegas. A tabela sai de bash sdd/reports/evidence/F16W_WINDOWS/scripts/medicao-windows.sh
   <run> <pasta nova> (na branch de documentos) sobre os artefatos testes-windows-fatia-1..16 do run.

Revisão adversarial: saldo da OpenRouter em US$ 6,00 em 2026-11-14 (fim da F16W), e a chave tem outro uso: leia /credits antes
de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia que funcionou da F16 à F16W: claude revisa,
openrouter (qwen) audita, --no-revisor2 e --no-desempate (codex sem cota); o --conferir pede --aceitar-sem-revisor2 "<motivo>".
A chave vem de ~/.config/rdd-eval.env, que guarda segredo em COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no ambiente do
comando, sem imprimir. Revisão do diff inteiro, sem --paths. Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador;
passar do teto é pergunta ao Roberto. Rode o raio de impacto (0b) antes da última rodada (na F16W ele achou 2 quebras reais).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu 33 a 41 min, teto 45: perto do teto, considere subir; macOS
~53 min, teto 75; Windows 16 fatias, a mais longa ~25 min, teto 30). Sem tag sai patch; para minor, push da main e da tag
juntos (git push --atomic). No push da main os 2 workflows abrem ~36 jobs e a fila do GitHub segura alguns: a Release
demora mais. Rode o Verify Gate com a máquina livre (~35 a 42 min, 2.176 testes em v2.16.0). Se a frente mexer em skill do
starter, gere de novo pela tag num clone limpo do starter e peça o OK próprio do Roberto para push, PR e merge lá (prefira o
fast-forward: git push origin <branch>:main).

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F16W2 na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.
Ao editar a ficha, troque blocos inteiros por seção (## ...).

Não faça:
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou merge no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a trava do CI recusa);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por script
bash com rc=$? e 1ª linha "$ comando" (o report-lint exige; o tail no fim de um pipe grava o exit errado); no zsh,
${PIPESTATUS[0]} é vazio (LM-018). No Windows: text=True sem encoding (LM-014), PYTHONIOENCODING no pipe do Git Bash (LM-015),
kill de grupo de processos não funciona (LM-016: o vigia agora usa taskkill pelo /proc/<pid>/winpid), "bash" pelo nome no
subprocess acha o do WSL (use o caminho). Número de 11 dígitos num teste barra o publish-gate (LM-012: monte em tempo de
execução). Testes de tempo caem com a máquina carregada: rode a suíte em série (o executor scripts/testes-por-modulo.py roda
por classe, --paralelo 1). Contagens fixadas em testes: 22 skills, 34 perguntas em 29 arquivos do sdd-decisoes-lint, versões
de skill (sdd-checar-ambiente 1.5.2, sdd-iniciar-repo 1.2.1 em test_f16_textos). O build gerado do starter está em 499 linhas
(teto 500, test_as_3_geradas_cabem_em_500_linhas).
```
