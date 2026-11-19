---
name: sdd-configurar-revisores
license: MIT
description: "Configura, com o aluno, os revisores da revisão adversarial do SDD Open (review.revisor1 e review.auditor): mede o estado deste computador sem mudar nada (slots, chave do OpenRouter no ambiente, perfil do terminal, CLIs instaladas), recomenda o caminho (as CLIs que o aluno já tem, o OpenRouter com dois modelos diferentes, ou uma engine só, com a consequência dita), conduz passo a passo a conta, o crédito, a chave com limite de gasto e a gravação da chave no perfil, sem a chave passar pela conversa, grava a escolha no git config deste computador com o OK do aluno e termina com a prova sem gastar. Use quando uma fase disser que faltam revisores, quando o adversarial-review.sh sair 64 por slot vazio ou 65 por credencial do OpenRouter, quando o aluno disser /sdd-configurar-revisores, \"configurar os revisores\", \"OpenRouter\", ou pedir para continuar a configuração depois de reabrir o agente."
metadata:
  author: Roberto Dias Duarte
  version: "1.0.0"
  updated: "2026-11"
---

# Configurar os revisores

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-configurar-revisores v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Deixar a revisão adversarial pronta para rodar neste computador, sem deixar o aluno sem próximo passo em nenhum
estado. **Quem mede é o script** `scripts/diagnosticar.sh` (a pasta desta skill é a que contém este `SKILL.md`):
ele diz o estado, a frase do aluno e o passo. Você conduz, pergunta e pede o OK; nunca adivinhe o estado.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e os exemplos completos. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca criou uma chave de API nem editou o perfil do terminal.

| Etapa | Nome para o aluno | O que acontece |
|---|---|---|
| 1 | Conferir | `diagnosticar.sh`: o estado deste computador, sem mudar nada |
| 2 | Escolher | o caminho: CLIs que o aluno já tem, OpenRouter, uma engine só, ou agora não |
| 3 | Chave | o site do OpenRouter e a chave no perfil, pelas mãos do aluno (pulada no caminho das CLIs) |
| 4 | Gravar | custo e privacidade ditos, o OK, `diagnosticar.sh --gravar` |
| 5 | Provar | `--testar`, os valores lidos de volta e `adversarial-review.sh --dry-run` |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Revisores: ✅ 1 Conferir · ▶️ 2 Escolher · ⬜ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- A primeira resposta diz o que é a revisão adversarial, quanto tempo leva e se custa, antes de qualquer termo.
- Repasse a frase (`aluno:`) e o passo (`passo:`) que o script imprimiu; nunca o id nem o nome do estado.

## A chave nunca passa por aqui

- **Nunca peça, aceite, repita ou grave a chave.** O aluno a cola no terminal dele (`scripts/guardar-chave.sh`) ou
  na janela de variáveis do Windows, com as próprias mãos.
- Para saber se ela existe, só `[ -n "${OPENROUTER_API_KEY:-}" ]` ou o `diagnosticar.sh`. **Nunca** `echo` da
  variável, `env`, `printenv`, `ps`, `pgrep -fl`, `cat` do perfil: no macOS, alguns desses imprimem o ambiente
  inteiro dos processos.
- O aluno colou algo com a forma de uma chave (começa por `sk-or-`) na conversa ⇒ não use, não repita o texto, e
  mostre a parada do exemplo 4 de `references/como-falar.md` (apagar aquela chave, criar outra). Nada é gravado.
- Não rode o `guardar-chave.sh` pelo agente: ele recusa sem terminal, e a chave passaria pela conversa.

## Como executar

```bash
bash <pasta desta skill>/scripts/diagnosticar.sh          # etapa 1, e de novo a cada volta
bash <pasta desta skill>/scripts/diagnosticar.sh --testar # etapas 4 e 5: 2 consultas de leitura, nada é gasto
bash <pasta desta skill>/scripts/diagnosticar.sh --gravar '<revisor>' '<auditor>'   # só depois do OK
bash <pasta desta skill>/scripts/diagnosticar.sh --marcar-reabertura                # ao mostrar a parada de reabrir
bash sdd/bin/adversarial-review.sh --dry-run              # etapa 5: o plano, sem chamar engine
```

O `diagnosticar.sh` imprime `ESTADO:`, `aluno:`, `passo:`, as medidas (revisor e auditor com a origem, a chave neste
agente e no perfil, os agentes instalados, o par sugerido, o preço por milhão de tokens com a data, a estimativa por
revisão) e `RESULTADO:`. A classe sai no código: 0 pronto ou chave aceita · 10 escolha do aluno · 20 parada (o aluno
faz algo fora daqui) · 30 conserto da configuração · 40 o teste da chave falhou · 64 nada a configurar ou uso errado.

**Sem bash** (PowerShell puro): a revisão adversarial também precisa de bash; diga isso (R22) e pare.

## Os estados

Uma linha por estado. `script` = o `diagnosticar.sh` reconhece e imprime a frase; `conversa` = você reconhece na
conversa ou na saída de outra ferramenta. Estado sem linha aqui é defeito: um teste compara esta tabela com o script.

| Estado | Quem reconhece | Situação | O que fazer |
|---|---|---|---|
| R01 | script | não há a revisão do SDD Open aqui, ou não é um repositório git | dizer que não há o que configurar e onde abrir o agente; parar |
| R02 | script | configurado e disponível | etapa 5 (Provar) direto, sem perguntas |
| R03 | script | slots vazios, 2 ou mais agentes de IA instalados | pergunta do caminho com **usar os que você já tem** primeiro (sem custo extra; servem se logados e com cota), depois OpenRouter, uma engine só, **não sei** |
| R04 | script | slots vazios, 1 ou nenhum agente, sem chave | pergunta do exemplo 1 de `references/como-falar.md` (OpenRouter recomendado) |
| R05 | script | a chave está no perfil, e o agente foi aberto antes dela | `--marcar-reabertura` e a parada do exemplo 2 |
| R06 | script | já houve a parada de reabrir, e a chave ainda não chegou | a parada de novo, com o passo do script (abrir pelo terminal; no Windows, sair e entrar na conta) |
| R07 | script | a chave chegou, slots vazios | `--testar`; depois o aviso de custo e privacidade e o OK do exemplo 3 |
| R08 | script | os slots usam o OpenRouter e falta a chave | só os blocos 2 e 3 de `references/PASSO_A_PASSO.md`, sem perguntar modelos |
| R09 | script | a CLI de um slot não está instalada | instalar a CLI; se a origem é este computador, oferecer trocar |
| R10 | script | só um dos dois papéis escolhido | perguntar o que falta (outra engine ou outro modelo) |
| R11 | script | revisor e auditor são a mesma engine | perguntar outro auditor |
| R12 | script | nome fora da lista de engines | mostrar os nomes válidos e perguntar |
| R13 | script | teste: chave aceita, com limite | seguir para a etapa que o `passo:` diz |
| R14 | script | teste: chave aceita, sem limite de gasto | recomendar pôr o limite (bloco 2, passo 2) e seguir |
| R15 | script | teste: chave recusada | apagar a chave e criar outra (blocos 2 e 3) |
| R16 | script | teste: a conta nunca pôs crédito | bloco 1, passo 3 |
| R17 | script | teste: o limite de gasto da chave acabou | aumentar o limite na página da chave, ou criar outra |
| R18 | script | teste: muitas chamadas agora (429) | esperar 1 minuto e testar de novo |
| R19 | script | teste: sem internet ou sem resposta em 10 s | conferir a internet e testar de novo |
| R20 | script | teste: erro do lado do OpenRouter | testar de novo em alguns minutos |
| R21 | script | teste: um modelo do par não está mais na lista | `upgrade` do SDD Open, ou o aluno diz outro modelo (preço desconhecido) |
| R22 | conversa | sem bash (PowerShell puro) | abrir o agente pelo Git Bash (ou WSL) e pedir de novo |
| R23 | conversa | a revisão real falhou com "No endpoints found" | nenhum provedor daquele modelo aceita não guardar o dado: trocar o modelo daquele papel (`--gravar`) |
| R24 | conversa | o aluno colou algo com a forma de chave | exemplo 4: não usar, não repetir, revogar e criar outra |
| R25 | conversa | o aluno escolheu uma engine só | dizer "diversidade: nenhuma" e o efeito; nada é gravado, e cada fase oferece rodar a revisão com `--reviewer <o agente> --um-engine` |
| R26 | conversa | o aluno escolheu "agora não" | dizer a consequência (a publicação pede o motivo de seguir sem revisão) e como voltar |

A revisão real que falhar depois (exit 65 com a credencial do OpenRouter, 402 sem crédito, 429 repetido) volta para
esta skill: rode o `diagnosticar.sh --testar` e siga a linha do estado que ele der.

## O caminho do OpenRouter

1. **Escolher** (R03/R04): a pergunta, com a estimativa por revisão que o script mediu.
2. **Chave** (etapa 3): os blocos de `references/PASSO_A_PASSO.md`, **um por resposta** (conta e crédito; a chave com
   limite; guardar a chave; reabrir). Os nomes de página vêm de lá, com a fonte e a data; não invente rótulo de botão.
3. **Parada** (R05): `--marcar-reabertura` e a parada do exemplo 2. Na volta, rode o `diagnosticar.sh` antes de
   dizer qualquer coisa: R07 ⇒ abra a resposta com "a chave chegou" e siga; R05/R06 ⇒ repita só a reabertura.
4. **Gravar** (etapa 4): `--testar`; com R13 ou R14, o aviso em 4 frases (quanto custa, pelo preço e pela estimativa
   do script; que cobra por uso, fora de qualquer assinatura; o que sai do computador: a mudança do código e os
   documentos da frente; só entram provedores que não guardam nem treinam com o dado) e a lembrança da
   `sdd-higiene-dado`; depois a pergunta `[D1 · não se desfaz]` do exemplo 3, com o par que o script sugeriu.
   **Nunca escreva nome de modelo nem preço de memória**: só o que o script imprimiu.
5. **Provar** (etapa 5): `--testar` de novo, `git config --get sdd.revisor1` e `sdd.auditor` (lidos de volta) e
   `adversarial-review.sh --dry-run`; as 3 linhas ✅ do exemplo 5 antes de "pronto". Se o plano disser que não há
   engine para o 2º revisor ou o desempate, diga a consequência em 1 frase (a publicação pede o motivo quando a
   mudança mexe em login ou senha; um achado grave em disputa fica para você decidir).

## O caminho das CLIs e o de uma engine só

- **CLIs que o aluno já tem** (R03): revisor = o agente que roda esta skill, se estiver na lista; auditor = outro da
  lista. Mesma pergunta `[D1 · não se desfaz]` do exemplo 3, sem as frases de custo do OpenRouter (diga que usa a
  cota da assinatura de cada um). Etapa 3 ➖.
- **Uma engine só** (R25): nada é gravado (gravar a mesma engine nos dois papéis afrouxaria a regra "auditor
  diferente do revisor"); diga que cada fase vai oferecer rodar a revisão com `--reviewer <o agente> --um-engine` (com o nome da engine
  na flag: sem ela, o script para em "nenhum revisor") e que o registro fica
  "diversidade: nenhuma". Etapas 3 e 4 ➖.
- **Agora não** (R26): nada é gravado. O `checar` continua avisando, e a publicação pede o motivo.

## Onde fica a escolha

`git config --local sdd.revisor1` e `sdd.auditor` (pelo `--gravar`), como o editor da `sdd-new-session`: vale na
hora para todas as frentes deste projeto e nunca vai para o GitHub. O `sdd/config.yaml` do projeto (`review.revisor1`,
`review.auditor`) é a escolha do time e vence o `git config`; quem quer fixar para todos preenche o slot. Para
trocar depois, peça esta skill de novo, ou `git config --local sdd.auditor '<outro>'`.

## Regras

- **O diagnóstico só lê.** Só o `--gravar` (depois do OK) e o `--marcar-reabertura` (na parada) gravam, e só no
  `git config` local. Nenhum arquivo do projeto muda.
- **A prova não gasta.** O `--testar` lê a chave e a lista pública de modelos; nunca uma chamada de modelo.
- **Nunca afrouxe a revisão para ela "passar"**: auditor diferente do revisor, chave só no ambiente, dispensa só
  com motivo escrito.

## Por que cada regra existe

- **A chave nunca passa pela conversa** — o histórico do agente fica guardado, e uma chave ali vale para qualquer
  um que o leia; a única saída segura é apagá-la e criar outra.
- **O script mede, a skill conduz** — "estado sem próximo passo" só some quando cada estado tem um id, uma frase e
  uma linha nesta tabela, conferidos por teste.
- **A volta começa pelo que foi medido** — o aluno que reabriu o agente desconfia de ter perdido tudo; a frase "a
  chave chegou" mostra o progresso real e evita repetir o site inteiro.
- **Limite de gasto na chave** — um erro de configuração não pode gastar o saldo inteiro; o teto fica na chave.
- **Modelo e preço só das tabelas do pacote** — preço muda; a tabela tem a fonte e a data, a memória não.
- **A escolha mora no git config** — o slot do `sdd/config.yaml` de uma frente só chega aos outros na integração,
  e a escolha depende do que este computador tem.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é `/sdd-configurar-revisores`.

**Próximo passo:** voltar à fase que pediu os revisores (`sdd-design`, `sdd-build` ou `sdd-release`).

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
