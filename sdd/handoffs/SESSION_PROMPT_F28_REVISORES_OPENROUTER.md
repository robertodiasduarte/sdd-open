# Abrir: F28 Revisores pelo OpenRouter — skill que configura a revisão adversarial com o aluno

O Roberto pediu em 2026-11-18 uma skill do SDD Open que oriente o aluno e configure os revisores da revisão
adversarial pelo OpenRouter quando os revisores ainda não estão definidos e a chave do OpenRouter não está
disponível. Não houve brainstorm formal: o pedido, os fatos conferidos e as decisões de partida estão no prompt
abaixo, e a frente começa pelo `sdd-define`.

## Onde abrir esta sessão

- pasta: `/Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter`
- branch: `feat/f28-revisores-openrouter`, nascida de `origin/main` em `eaeb874` (`v2.24.0` mais 3 commits de
  documento), sem upstream
- feature_id: `F28_REVISORES_OPENROUTER`

Abra com `cursor "/Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter"` e cole o prompt.

## Prompt

```text
Frente F28_REVISORES_OPENROUTER do SDD Open (repo público robertodiasduarte/sdd-open). Responda sempre em português.
Pasta: /Users/robertoduarte/rdd-worktrees/sdd-open-f28-revisores-openrouter · branch feat/f28-revisores-openrouter
(sem upstream: o 1º push é `git push -u origin feat/f28-revisores-openrouter`, nunca `git push` puro).

O QUE FAZER: rodar o pipeline inteiro do SDD Open, começando pelo sdd-define e indo até a sdd-release:
sdd-define → sdd-ux-review (há interface: a conversa com o aluno e a saída do script) → sdd-design → sdd-build →
sdd-release. Não há brainstorm e não é para abrir um: o pedido e as decisões de partida estão neste prompt. Pode usar
a sdd-drive do DEFINE até "pronto para publicar".

O PEDIDO (Roberto, 2026-11-18): uma skill que oriente o aluno e configure os revisores da revisão adversarial pelo
OpenRouter quando `review.revisor1` e `review.auditor` ainda estão vazios e a OPENROUTER_API_KEY não está no ambiente.
Nas palavras dele: "fundamental explicar o passo a passo para alunos e não deixar o aluno sem orientação".

O PROBLEMA DE HOJE (conferido em origin/main, eaeb874; confirme antes de usar):
- O `init` não pergunta revisor nem auditor; o sdd/config.example.yaml traz `review.revisor1: ""` e `review.auditor: ""`.
- Com os slots vazios, a sdd-design (linha "vazios, pergunte à pessoa quais usar", perto da 228 do SKILL.md) e a
  sdd-build (passos 0 e 5c) só mandam perguntar; o adversarial-review.sh sai 64. O aluno recebe uma pergunta sobre
  "engines" sem saber o que responder.
- A sdd-release (FASE 0, item 8) exige a revisão desta versão do código ou uma dispensa com motivo escrito. Sem
  orientação, o caminho mais fácil para o aluno é dispensar sempre.
- O docs/pt-BR/guia-do-aluno.md não cita revisor1, auditor, registry nem OpenRouter; quem explica é o
  docs/pt-BR/adversarial-review.md, que é técnico.
- O checar.sh da sdd-checar-ambiente não olha nada disso.

FATOS QUE O DESENHO PRECISA RESPEITAR (leia os arquivos; não confie só neste resumo):
- sdd/bin/adapters/openrouter.sh: a chave vem SÓ de OPENROUTER_API_KEY no ambiente, lida dentro do Python; nunca de
  arquivo do repositório, argumento ou log. Sem ela, o adapter devolve 65. Toda chamada já leva
  provider.data_collection = "deny" e require_parameters = true.
- sdd/bin/adversarial-review.sh, função de identidade (perto da linha 342) e a checagem do exit 67 (perto da 501):
  "o mesmo adapter com o mesmo modelo é a mesma engine". Logo, dois modelos DIFERENTES do OpenRouter servem de revisor
  e auditor (`openrouter:<A>` e `openrouter:<B>`); o mesmo modelo nos dois dá 67.
- sdd/review/registry.tsv: a linha `openrouter` tem um modelo padrão; sdd/review/precos.tsv tem a tarifa de 2 modelos
  do OpenRouter, com fonte e data. Modelo fora do precos.tsv e sem custo reportado aparece como `$?`.
- O 2º revisor e o desempate são "a 1ª engine disponível do registry que não é o revisor nem o auditor". Com tudo
  pelo OpenRouter, confira no código o que sobra para esses papéis e o que o aluno vê quando não sobra nada.
- O OpenRouter cobra por token, fora de qualquer assinatura; o diff, o DEFINE, o DESIGN e o BUILD_REPORT saem do
  computador do aluno na chamada.
- O guia do aluno diz que no Windows o pacote roda em Git Bash ou WSL (bash 3.2 ou mais novo).

REQUISITO CENTRAL — O ALUNO NUNCA FICA SEM ORIENTAÇÃO. Isto vira AT no Define e régua na UX Review:
- Todo estado tem um próximo passo dito ao aluno. Monte no Define a tabela de estados (slots vazios ou cheios × chave
  presente ou ausente × CLIs instaladas × sessão reaberta ou não × chave recusada × sem crédito × modelo inexistente ×
  sem internet) e, para cada um, o que o aluno ouve e o que ele faz. Estado sem linha na tabela é defeito.
- Passo a passo numerado, um comando ou um clique por passo, com o que esperar na tela depois de cada um, no formato
  que as skills já usam ("Como falar com o aluno", references/como-falar.md, sdd/templates/fragments/PERGUNTA_DECISAO.md).
  Quem lê, em geral, nunca criou uma chave de API nem editou o perfil do terminal.
- Cobre o caminho inteiro fora do computador também: criar a conta no OpenRouter, pôr crédito, criar a chave, pôr um
  limite de gasto na chave, guardar a chave. Diga onde clicar pelo nome do que aparece na tela e confira esses nomes
  na página oficial no dia do Build, nunca de memória.
- Toda pergunta tem a opção recomendada primeiro, com o porquê, e a opção "não sei". Termo técnico (engine, revisor,
  auditor, chave de API, variável de ambiente, token) só com a explicação junto, na primeira vez.
- Toda parada é retomável: diz o que já foi feito, o que falta, e "quando terminar, me peça de novo, eu continuo
  daqui". A parada obrigatória é a da chave: o agente herda o ambiente de quando foi aberto, então depois de gravar a
  chave o aluno fecha e abre o agente, e a skill precisa reconhecer esse ponto ao voltar em vez de repetir tudo.
- Todo erro tem tradução: cada sinal que o registry.tsv já classifica (credencial 401/403, limite 429, sem crédito
  402, "No endpoints found", falha de rede) vira uma frase para o aluno e um passo. Nunca saída crua.
- Termina com prova: o aluno vê que funcionou (chave aceita, slots gravados, plano da revisão) antes de a skill dizer
  que está pronto.
- Quem não quer ou não pode usar o OpenRouter também tem caminho: as CLIs que ele já tem (claude, codex, gemini) ou o
  `--um-engine`, com a consequência dita ("diversidade: nenhuma").

DECISÕES DE PARTIDA (recomendações já aceitas como padrão; registre cada uma no DEFINE e mude só com motivo escrito):
 P1. Skill nova em .agents/skills/, nome sugerido `sdd-configurar-revisores`, no molde da sdd-checar-ambiente: um
     script de diagnóstico que só lê e decide por exit code, e a skill que traduz e conduz.
 P2. A chave nunca passa pela conversa. O aluno a cola no próprio terminal ou no perfil do terminal, com as próprias
     mãos. Se o aluno colar a chave no chat, a skill diz para revogar aquela chave e criar outra, e não a usa.
     O agente nunca imprime a variável: só testa se existe (`[ -n "${OPENROUTER_API_KEY:-}" ]`).
 P3. Antes do OpenRouter, a skill mostra o que o aluno já tem: com 2 CLIs instaladas e logadas, a opção sem custo
     extra vem junto na pergunta. O OpenRouter é o caminho de quem tem um agente só, e é o foco do passo a passo.
 P4. Modelo e preço só do registry.tsv e do precos.tsv. Se o par sugerido precisar de modelo novo, ele entra no
     precos.tsv com a URL e a data da conferência. Nada de nome de modelo de memória no SKILL.md.
 P5. Antes do OK de gravar, a skill diz em frases curtas: custa dinheiro (por uso, fora da assinatura), o que sai do
     computador, e que os provedores aceitos não retêm nem treinam com o dado. Lembra a sdd-higiene-dado.
 P6. Prova sem gastar: uma consulta de leitura à chave, se a API oficial do OpenRouter tiver uma (confira na
     documentação oficial no Design; não invente endpoint), e `adversarial-review.sh --dry-run`.
 P7. Ganchos: a sdd-design e a sdd-build passam a oferecer a skill onde hoje mandam "perguntar"; a sdd-release
     oferece no item 8 da FASE 0 antes de aceitar a dispensa; a sdd-checar-ambiente ganha um aviso (nunca
     impedimento) quando os revisores não estão configurados.
 P8. Documentação junto: seção nova no guia do aluno, ajuste no adversarial-review.md nas duas línguas (docs/ e
     docs/pt-BR/), README se a lista de skills mudar.

PONTOS EM ABERTO PARA O DEFINE E O DESIGN RESOLVEREM (com evidência, não por suposição):
 A1. Onde o aluno grava a chave em cada sistema (zsh no Mac, bash no Linux, Git Bash e WSL no Windows) e como cada
     agente herda o ambiente: agente aberto pelo terminal × extensão do editor aberta pelo ícone. Teste o que der
     para testar; o que não der, diga no documento que não foi testado.
 A2. Onde gravar `review.revisor1` e `review.auditor`: no sdd/config.yaml da frente o valor só chega à branch padrão
     na integração, e a pergunta voltaria em cada frente aberta até lá. A sdd-new-session resolveu o caso do editor
     com `git config --local sdd.editor`. Decida o equivalente aqui e registre o porquê.
 A3. O que acontece com o 2º revisor e o desempate quando revisor e auditor são do OpenRouter e não há outra engine.
 A4. Como a skill se comporta quando os slots já estão cheios, mas a chave falta, ou o contrário.
 A5. Se o diagnóstico entra na linha de avisos do checar.sh ou fica só na skill nova.

COMO DECIDIR (pedido do Roberto): em cada decisão, avalie prós e contras, recomende e ACEITE A RECOMENDAÇÃO COMO
PADRÃO, registrando-a no documento da fase (Advisor Ledger ou "Decidi sozinho"). Pergunte ao Roberto SÓ o que for
crítico:
  (1) o OK de publicar da sdd-release (sempre);
  (2) apagar qualquer coisa que não foi criada nesta frente;
  (3) afrouxar proteção existente (gate, varredura de segurança, publish-gate, regra do playbook, a regra
      "auditor diferente do revisor", a regra "chave só no ambiente");
  (4) mudar o escopo para além deste prompt (guardar a chave em arquivo ou em cofre do sistema, outro provedor além
      do OpenRouter, mudar a cadeia do adversarial-review.sh, tornar a revisão dispensável sem motivo);
  (5) rodada de revisão acima do teto;
  (6) qualquer passo que gaste dinheiro de verdade no OpenRouter ou que precise de uma chave real para ser provado.
O Roberto não é programador: quando perguntar, explique simples, com o efeito de cada opção.

PRIMEIRA AÇÃO: a sessão que abriu a frente estava presa a outro repositório e não commitou nada. Nesta branch:
 1. Acrescente a linha da F28 na tabela "Estado das frentes" de sdd/features/PLANO_F4_F15_CONSOLIDADO.md (estado 🔨,
    "aberta em 18/11, Define em curso", apontando para este prompt) e atualize a data do cabeçalho.
 2. Commit só desses dois caminhos, pelo nome, nunca `git add -A`:
      git add sdd/features/PLANO_F4_F15_CONSOLIDADO.md sdd/handoffs/SESSION_PROMPT_F28_REVISORES_OPENROUTER.md
      git commit -m "docs(F28_REVISORES_OPENROUTER): frente aberta, registrada no plano"
 3. Confira se a main andou: `GIT_TERMINAL_PROMPT=0 git fetch origin` e `git log --oneline HEAD..origin/main`. Se
    andou, `git rebase origin/main` agora, com a branch ainda quase vazia.
Os documentos da frente (DEFINE, UX_REVIEW, DESIGN, BUILD_REPORT, ledger) ficam NESTA branch, em sdd/, e vão para a
main no PR do código (regra da F26).

FORA DO ESCOPO: guardar a chave em qualquer arquivo do projeto; cofre do sistema (Keychain, Credential Manager);
outros provedores; mudar preço, cadeia ou prompts da revisão; mexer nos slots `papeis:` (modelo por papel é outra
conversa); corrigir direto no starter (a skill chega lá pelo gerador, scripts/gerar-starter.py, com o PR do starter na
release, como nas frentes anteriores); material de aula do repositório privado da RDD.

LEIA PRIMEIRO:
- docs/pt-BR/adversarial-review.md e docs/pt-BR/guia-do-aluno.md;
- sdd/bin/adversarial-review.sh (slots, exits 64 a 68, --dry-run, --um-engine, --conferir), sdd/bin/adapters/openrouter.sh,
  sdd/review/registry.tsv, sdd/review/precos.tsv, sdd/config.example.yaml (bloco review:);
- .agents/skills/sdd-checar-ambiente/ inteira (o molde: script que decide, tabela que traduz, teste que confere que
  toda mensagem do script tem linha na tabela) e .agents/skills/sdd-new-session/ (pergunta do editor, gravação por
  `git config`, "Como falar com o aluno");
- os trechos da sdd-design, da sdd-build e da sdd-release que tratam da revisão;
- a seção `## Sempre` de sdd/playbook.md e `bash sdd/bin/playbook-lint.sh --grep <termo> sdd/playbook.md` para
  MANIFEST, revisão, openrouter, credencial, Windows e starter;
- sdd/handoffs/HANDOFF_F27_DESEMPENHO_BANCO.md, como exemplo recente de skill nova publicada de ponta a ponta.

SEGURANÇA DESTA FRENTE:
- Nenhum teste chama o OpenRouter de verdade: use os stubs de sdd/review/stubs/ e SDD_REVIEW_OPENROUTER_URL com
  servidor local. Fixture de chave é texto que não parece chave real (o publish-gate e a varredura de segredo olham).
- Nunca rode `ps`, `pgrep -fl` ou `env` cru para "ver se a chave está lá": no macOS esses comandos podem imprimir o
  ambiente inteiro dos processos. Só o teste de existência.
- Rode `bash sdd/bin/seguranca-varredura.sh --regras` antes do Build e passe a frente pela sdd-seguranca no Define.

NÃO FAÇA: pôr número, nome de aluno ou dado medido no repositório privado da RDD em documento ou fixture do Open;
pedir, aceitar ou repetir uma chave na conversa; escrever nome de modelo ou preço de memória; deixar um estado do
aluno sem próximo passo; afrouxar o adversarial-review.sh para a skill "passar".

LANDMINES: MANIFEST.txt para todo arquivo novo do pacote (LM-037); teste que pergunta a plataforma usa as constantes
de tests/apoio.py, nunca os.name; rode test_windows e test_gerar_starter antes do gate; a suíte tem de passar no
Windows (o CI do PR; medir lá exige push da branch); o Bash do agente é zsh (variável com vários caminhos não se
divide: use array; PIPESTATUS não existe); os scripts do pacote rodam em bash 3.2; número de 11 ou mais dígitos em
arquivo do pacote reprova o G2 do publish-gate; identidade de git em teste só por GIT_AUTHOR_* e GIT_COMMITTER_*,
nunca `git config user.*` dentro de worktree ligada.
```
