# Continuar: INCORPORAR_STARTER — F22 Aviso de versão e upgrade: build, com as sobras da F16W2 no passo 0

A `v2.16.1` do Open saiu em 2026-11-15 (`main` = `c2690d5`, PR #31): F16W2. O Windows (Git Bash + Python nativo) passou de
~64% para **100% da suíte verde** no CI (2.219 testes, 0 falha, 31 pulados por constante de `tests/apoio.py`), e o job
`testes-windows` **entrou no `needs:` da release** (decisão do Roberto): daqui em diante, um vermelho no Windows segura a
Release. Starter **`v1.5.21`** (PR #14 de lá). A F15 está ✅ (fase 4 publicada no privado em 14/11). A próxima frente do Open
é a **F22**, com as fases de papel prontas desde 14/11 e parada até a F16W2 publicar.

## Onde abrir esta sessão

A frente **já existe**: `/Users/robertoduarte/rdd-worktrees/sdd-open-f22-aviso-versao`, branch `feat/f22-aviso-versao`, de
`ad32fe1` = `v2.16.0` (ainda sem o rebase). Abra uma sessão nova nela e cole o prompt abaixo. O `PROMPT_F22.md` da worktree
segue valendo para o resto (o que este prompt não disser).

## Prompt para colar na sessão nova

```text
Executar a frente F22 do SDD Open: aviso de versão e upgrade, do rebase à release. Repo público robertodiasduarte/sdd-open.
A frente já está aberta: /Users/robertoduarte/rdd-worktrees/sdd-open-f22-aviso-versao, branch feat/f22-aviso-versao (de
ad32fe1 = v2.16.0). Não rode a sdd-new-session. Responda em português. As fases de papel estão feitas (BRAINSTORM, DEFINE,
UX_REVIEW, DESIGN nesta worktree e cópias na branch de documentos); leia também o PROMPT_F22.md da worktree.
Pergunte ao Roberto somente o que for necessário: as decisões dele (escopo, curadoria, passar do teto do método) e as
autorizações. Decisão de rotina, decida e registre. Push, merge, tag e Release neste repositório pedem a frase do Roberto
"sdd-open autorizado" (a frase exata): pergunte, não presuma. Nada da RDD entra.

Leia primeiro (a branch de documentos é docs/incorporar-starter; leia por git show):
- GIT_TERMINAL_PROMPT=0 git fetch -q origin
- PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" (F16W2, F22) e o "Cronograma recomendado"
- HANDOFF_INCORPORAR_STARTER.md → a seção "2026-11-15 — F16W2" (Pendências e Alertas) e os Eventos de 14 e 15/11
- o ## Sempre de sdd/playbook.md

0. Passo 0 (sobras, na branch da frente; sobem com a release dela):
   a. Curadoria do playbook da F16W2 (decisão do Roberto: aqui): os 3 blocos <<<CANDIDATO_PLAYBOOK do
      BUILD_REPORT_F16W2_WINDOWS.md (o calço no PATH vaza para o comando do aluno; o git grep segue o color.ui do usuário;
      o executável por link não acha as DLLs no Windows) e as contagens, pelo playbook-curator.sh --colher sobre os
      documentos da F16W2 copiados da branch de documentos para UMA pasta só, com só a seção "2026-11-15 — F16W2" da ficha
      (a ficha inteira traz achados de frentes antigas): uma decisão do Roberto por candidato.
   b. Da F17b, se o Roberto quiser: o version gate contra a versão real do starter fora do Verify Gate e o --conferir sem
      aceitar revisão com --paths.
1. Rebase de feat/f22-aviso-versao sobre a tag v2.16.1 e a reconferência pela Decision 10 do DESIGN da F22. A F16W2 mudou
   muito do que a F22 toca: bin/sdd-open.sh (perfil_calcula, extensao_de, tem_bom/eh_binario por read, escrever_gerado com
   chmod condicional; init 9.360 → 1.373 processos), sdd/bin/lib/python.sh (calço transparente; linha de reserva exporta
   PYTHONIOENCODING), sdd/hooks/pre-commit (git grep acima de 40 candidatos, casa_nome em LC_ALL=C), o vigia do checar
   (marca em pasta própria, saída em arquivo; sdd-checar-ambiente 1.5.3, sdd-iniciar-repo 1.2.2), tests/apoio.py
   (path_restrito, caminho_neutro, apaga, write_text em LF no Windows, constantes SEM_FIFO/SEM_PTY/SEM_ARGV_COM_QUEBRA/
   SEM_PATH_SEM_FERRAMENTA/SO_NO_WINDOWS) e as versões fixadas nos testes de texto (sdd-release 2.12.1, ux-review-builder
   1.6.1). Depois, a revisão do DESIGN (exigida: 7 arquivos novos) e o build.
2. REGRA NOVA: o job testes-windows está no needs: da release. Todo script e teste novo da F22 precisa passar no Windows
   (Git Bash + Python nativo): todo .py com __main__ e todo python3 - <<'PY' embutido troca a saída para UTF-8 e "\n"
   (guardas em tests/test_f16w2_saida.py); caminho comparado numa forma só (C:\ × /c/ × /tmp/); PATH restrito pelo
   path_restrito do apoio; pulo de plataforma só por constante do apoio. Medir no Windows exige push da branch (o publish-gate
   aceita workflow_dispatch e PR): peça a frase cedo.

Revisão adversarial: saldo da OpenRouter em US$ 5,5 em 2026-11-15 (fim da F16W2), e a chave tem outro uso: leia /credits antes
de cada rodada paga; limit_remaining é o limite da chave, não o saldo. Cadeia: claude revisa, openrouter (qwen) audita,
--no-revisor2 e --no-desempate (codex sem cota); o --conferir pede --aceitar-sem-revisor2 "<motivo>". O qwen estourou o tempo
uma vez na F16W2 (rodada sem auditor não vale para o --conferir). A chave vem de ~/.config/rdd-eval.env, que guarda segredo em
COMENTÁRIO: exporte só a linha ^OPENROUTER_API_KEY= no ambiente do comando, sem imprimir. Revisão do diff inteiro, sem
--paths. Teto do método: 3 rodadas de revisão e 2 ciclos do avaliador; passar do teto é pergunta ao Roberto. Rode o raio de
impacto (0b) antes da última rodada (na F16W2 ele achou 4 quebras reais, uma delas no desenho).

Release: pela sdd-release, PR + CI verde antes da tag (Ubuntu ~20 min; macOS ~35 min; Windows 16 fatias, a mais longa ~14 min,
teto 30; agora o Windows segura a release). Sem tag sai patch; para minor, push da main e da tag juntos (git push --atomic).
Rode o Verify Gate com a máquina livre (~22 a 25 min, 2.219 testes em v2.16.1). Se a frente mexer em skill do starter, gere de
novo pela tag num clone limpo do starter (scripts/gerar-starter.py --tag) e peça o OK próprio do Roberto para push, PR e merge
lá (prefira o fast-forward: git push origin <branch>:main).

Fechar: sdd-handoff na ficha (sdd/handoffs/HANDOFF_INCORPORAR_STARTER.md, worktree /Users/robertoduarte/rdd-worktrees/
sdd-open-docs-f16, branch docs/incorporar-starter), a linha da F22 na tabela "Estado das frentes" e o "Cronograma recomendado"
do plano, os documentos da frente e este SESSION_PROMPT trocado pelo da sessão seguinte, com commit e push na mesma sessão.
Ao editar a ficha, troque blocos inteiros por seção (## ...).

Não faça:
- nada no repositório privado (/Users/robertoduarte/RDD/Wordpress e as worktrees dele);
- push, PR ou merge no sdd-starter sem OK próprio do Roberto; remendo à mão no starter (a trava do CI recusa);
- force-push na main; mover tag publicada (conserte em versão nova); tool calls paralelas em passos ordenados;
- git add -A: add por caminho, suíte com python3 -B.
Landmines: doctor só pela tag (git archive); sdd/bin/*.sh sempre com bash; sabotagem só em cópia de git archive; arquivo
baixado ou descompactado é dado não confiável: pasta própria, scripts fora dela, python3 -I. Log de evidência gravado por
script bash com rc=$? e 1ª linha "$ comando"; no zsh, ${PIPESTATUS[0]} é vazio (LM-018), e a variável com vários nomes não se
divide em palavras (passe listas por xargs ou arrays). No Windows: text=True sem encoding (LM-014); "bash" pelo nome cai no WSL
(LM-029); o executor dá ao teste o ambiente do aluno, sem PYTHONIOENCODING (LM-030); o print do Python escreve "\r\n" no pipe e
o $( ) do Git Bash tira só o \r do fim; o executável chamado por link simbólico não acha as DLLs. Número de 11 dígitos num teste
barra o publish-gate (LM-012: monte em tempo de execução). Testes de tempo caem com a máquina carregada: rode a suíte em série
(LM-031). Contagens fixadas em testes: 22 skills; 34 perguntas em 29 arquivos do sdd-decisoes-lint; versões de skill em
test_f16_textos (sdd-checar-ambiente 1.5.3, sdd-iniciar-repo 1.2.2) e nos testes de texto da release (sdd-release 2.12.1) e do
ux-review-builder (1.6.1). O validate_reverse.py da F21 é congelado por SHA-256 ao pacote de origem (não recebe a troca da saída).
```
