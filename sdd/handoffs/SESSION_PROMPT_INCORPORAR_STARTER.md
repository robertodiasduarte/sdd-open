# Continuar: INCORPORAR_STARTER — F17b Starter gerado, etapa 2 (frente aberta em 2026-11-13), com as sobras da F17 no passo 0

A `v2.13.0` do Open saiu em 2026-11-13 (`main` = `d813954`, PR #27): F17, o sdd-starter passa a ser gerado a partir do Open
(`scripts/gerar-starter.py`). A 1ª geração publicou o starter **`v1.5.17`** (PR #10 de lá): 10 skills geradas, com
`GERADO.txt` e a trava `check-gerado.py` no CI do starter. Pelo **Cronograma recomendado** do plano, a próxima frente é a
**F17b**: a etapa 2 da geração, para que nenhuma skill do starter fique com texto próprio.

## Onde abrir esta sessão

A frente **já existe** (aberta em 2026-11-13 pela `sdd-new-session`): worktree
`/Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2`, branch `feat/f17b-starter-etapa2`, de `origin/main` =
`d813954` (`v2.13.0`). A janela do Cursor foi aberta nela; cole o prompt abaixo lá. A worktree e o clone do starter da F17 foram
removidos em 2026-11-13; as 7 revisões, os documentos e os traces da F17 estão em
`/Users/robertoduarte/rdd-worktrees/arquivo-sdd-open/F17_STARTER_GERADO-v2.13.0-documentos-revisoes-traces.tar.gz`.

## Prompt para colar na sessão nova

```text
Executar a frente F17b do SDD Open: starter gerado, etapa 2 (Decisão 5). Repo público robertodiasduarte/sdd-open.
A frente já está aberta: /Users/robertoduarte/rdd-worktrees/sdd-open-f17b-starter-etapa2, branch feat/f17b-starter-etapa2,
de origin/main = d813954 = v2.13.0. Não rode a sdd-new-session. Responda em português.
Push, merge, tag e Release neste repositório pedem a frase do Roberto "sdd-open autorizado": pergunte, não presuma.
A F17b toca dois repositórios: o gerador mora no Open; o robertodiasduarte/sdd-starter recebe a cópia gerada e pede OK PRÓPRIO
do Roberto para cada push, PR e Release lá (merge na main do starter publica a Release automática). Nada da RDD (nomes de
aluno, edges, caminhos do Wordpress, chaves, código do repositório privado, texto do e-book de segurança) entra em nenhum dos dois.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- git show origin/docs/incorporar-starter:sdd/features/PLANO_F4_F15_CONSOLIDADO.md  → "Estado das frentes" (F17 e F17b), o
  "Cronograma recomendado" (com as sobras do passo 0), a seção da F17 e a seção 10 (pares)
- git show origin/docs/incorporar-starter:sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md  → Ficha (Falta), Eventos de 2026-11-12 e
  2026-11-13 e a seção "2026-11-12 — F17" (Pendências e Alertas)
- git show origin/docs/incorporar-starter:sdd/features/BRAINSTORM_F17_STARTER_GERADO.md (decisões e YAGNI) e
  sdd/features/DESIGN_F17_STARTER_GERADO.md (Decisions 1–11: trocas exatas, regras mecânicas, lint, trava, versão)
- git show origin/docs/incorporar-starter:sdd/reports/evidence/F17_STARTER_GERADO/COMPARACAO-fases-e-apoio.md → o que o
  starter tem melhor em brainstorm, handoff e governança (modo web), item a item
- o ## Sempre de sdd/playbook.md da frente; o starter publicado: gh release view --repo robertodiasduarte/sdd-starter

0. Sobras da F17, na branch da frente (sobem com a release dela):
   a. Curadoria dos 3 candidatos ao playbook do BUILD_REPORT da F17 (tag no arquivo gerado muda tudo; aceite que isenta a
      linha inteira; comparação que vira "o slot contra ele mesmo"): uma decisão do Roberto por candidato.
   b. Pendentes da revisão da F17, sem ocorrência hoje (decida com o Roberto se entram): o CI do starter sem os testes de
      tests/ da raiz (a v1.5.16 também não rodava); collect_evidence.py sem excluir node_modules/; copiar byte a byte o que
      nenhuma regra muda (CRLF); trazer_moldes lendo o CHANGELOG; caminho de skill irmã nos scripts (os dois últimos falham alto,
      com 65); "sdd/hooks" sem barra passa no lint (~15 linhas condicionais da higiene-dado); o gate.sh da kb cai para 644 no starter.
   Bump das skills tocadas e python3 scripts/check-versions.py --base v2.13.0.

1. A frente: sdd-brainstorm → sdd-define → sdd-design → sdd-build → sdd-release.
   - Brainstorm com as decisões abertas: o modo web (sem terminal, entregar o documento no chat sem fingir que gravou; fato ×
     inferência; pendências 🐛/✨; prova por script só quando há gate) em brainstorm, handoff e governança no Open, para elas
     entrarem na lista do gerador; o destino de define, design, build, release e ux-review-builder (modo sem script dentro do
     Open, ou sair do starter, com os zips da v1.5.17 ainda baixáveis); se docs/ e exemplos/ do starter passam a ser gerados.
     Meta do Roberto: manutenção num repositório só; o starter simples para o aluno iniciante.
   - O gerador já existe: skill nova na lista pede linha no scripts/starter/openai.tsv, trocas em scripts/starter/trocas/ e,
     se a cópia mudar, versão maior que a do starter (o gerador confere antes de gravar). O README do starter vem de
     scripts/starter/raiz/README.md (teste exige toda skill gerada citada nos 2 idiomas).
   - A 2ª geração parte da tag publicada desta frente, num clone limpo do starter, numa branch; as 9 checagens do CI de lá
     antes do PR; trava, publish-check, check-versions --base <última tag do starter>, gate.sh da kb.
   - O passo 5c da sdd-build grava sdd/reviews/LEDGER_REVISAO_{F}.md (ledger-revisao-lint.sh); no fim, eval-revisores.sh no relatório.
   - Documentos SDD (features, reports, reviews, evidence) ficam fora do git na pasta da frente e vão no fim para a branch de
     documentos (worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16).

Revisão adversarial: saldo da OpenRouter em US$ 14,67 em 2026-11-12 (fim do dia), e a chave tem outro uso: leia /credits antes
de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia que funcionou na F16, na F18 + F20 e na F17:
claude revisa, openrouter (qwen) audita, --no-revisor2 e --no-desempate (codex sem cota) — o --conferir pede
--aceitar-sem-revisor2 "<motivo>" com diff acima de 8 arquivos. A chave vem de ~/.config/rdd-eval.env, que guarda segredo em
COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no ambiente do comando, sem imprimir. HIGH do auditor se confere no código
antes de agir; desacordo sobre comportamento de ferramenta se decide por medição registrada (LM-021).
Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto. Rodada só do delta com 0
achados em segundos é marcada "rasa" pelo --conferir e não conta: a última rodada antes da release cobre o diff inteiro.
Rode o raio de impacto (0b) antes da última rodada (na F17 achou 3 quebras em código não modificado).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~30 min, teto 45; macOS ~43 min, teto 75; Windows caminho do
aluno ~5 min, teto 30). Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic). Rode o Verify Gate
com a máquina livre: com a revisão rodando junto, caíram teste de tempo da sdd-drive (F18) e da deploy-do-sha (F17); confira
isolado em cópia de git archive e rode o gate de novo.

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F17b na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.

Não faça:
- nada da F15 nesta sessão se a frente tocar a sdd-release;
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou Release no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a trava do CI recusa);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por script
bash com rc=$? e 1ª linha "$ comando" (o report-lint exige); no zsh, ${PIPESTATUS[0]} é vazio (LM-018). Não cale com
2>/dev/null um aviso dito uma vez (LM-019). Pulo de plataforma nos testes só por constante de tests/apoio.py. O gerador só roda
igual ao da tag (senão 64): para gerar, use uma worktree da tag. sha256 escrito inteiro traz 11 dígitos seguidos (LM-012):
o publish-check do starter pula o GERADO.txt. sdd-release em 500 linhas (teto do teste). Contagens fixadas em testes antigos
(21 skills, 30 perguntas do sdd-decisoes-lint, versões de skill): skill ou pergunta nova mexe nelas.
```
