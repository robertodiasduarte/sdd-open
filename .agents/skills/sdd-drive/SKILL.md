---
name: sdd-drive
description: "Leva um DEFINE até \"pronto para publicar\" sozinho: desenha, constrói uma tarefa por sessão nova, roda o teste final, corrige e repete até o limite de rodadas, e para antes de publicar. Um script decide a próxima ação e conta as rodadas; o agente executa. Use quando a pessoa disser /sdd-drive, \"pilote esta feature\", \"leve até o fim\", \"construa e confira sozinho\" ou quiser retomar uma execução que caiu. Não publica: publicar é sempre pela sdd-release, com o OK da pessoa."
compatibility: Requer bash >= 3.2, Python >= 3.9 e git >= 2.20; roda sdd/bin/sdd-drive.sh. Funciona com ou sem subagente; sem ele, para a cada tarefa e pede uma sessão nova.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "1.0.0"
  updated: "2026-11"
  fase: "orquestração"
---

# sdd-drive — o piloto

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-drive v1.0.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Levar um DEFINE aprovado até o teste final verde e os relatórios prontos, voltando à pessoa só quando a decisão
é dela. **Quem decide é o script** `sdd/bin/sdd-drive.sh`: ele guarda o estado, roda o teste final, conta as rodadas e
diz a próxima ação. Você executa a ação e pergunta de novo. Nunca conte rodada de cabeça nem rode o Verify Gate por
conta própria para decidir.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Ações do script |
|---|---|---|
| 1 | Conferir | `iniciar`, `--dry-run`, `--resume` |
| 2 | Desenhar | `DESIGN`, `REVISAO_DESIGN` |
| 3 | Construir | `RODADA`, `COMMITAR`, `CORRIGIR` |
| 4 | Teste final | `VERIFICAR`, `ESPERAR` |
| 5 | Relatório | `AVALIAR_E_RELATAR`, `concluir` |

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Drive: ✅ 1 Conferir · ✅ 2 Desenhar · ▶️ 3 Construir (rodada 1/3 · tarefa 4 de 12) · ⬜ 4 Teste final · ⬜ 5 Relatório`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare. Nas ações de rotina não há decisão: siga para a próxima.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- Repasse a frase do motivo que o script imprimiu, nunca o nome (`estado-invalido` é jargão).

## Entrada

`/sdd-drive sdd/features/DEFINE_{FEATURE}.md [--max N]`, numa frente de trabalho própria, com o DEFINE já com Verify
Gate e revisão de governança. Para retomar: "continue o drive" numa sessão nova.

## O laço

1. **Abra dizendo o combinado**, em 1 frase: o que vai fazer, `até N rodadas` (uma rodada é construir o que falta e
   rodar o teste final) e `paro antes de publicar`.
2. **Comece.** `bash sdd/bin/sdd-drive.sh iniciar <DEFINE> [--max N]`; para só ver o plano, `--dry-run`. Execução que já
   existe: `bash sdd/bin/sdd-drive.sh --resume <DEFINE>`.
3. **Leia a saída e faça o que ela manda.** Exit 10 traz `ACAO:`; faça a ação da tabela e chame
   `bash sdd/bin/sdd-drive.sh proximo <DEFINE>`. Repita. Exit 0, 20 ou 40 terminam o laço: siga a tabela de motivos.

| `ACAO:` | Quem faz | Como |
|---|---|---|
| `DESIGN` | você, pela fase Design | rode a `sdd-design` sobre o DEFINE; se a saída trouxer o motivo, corrija só esse ponto |
| `REVISAO_DESIGN` | agente fresco | revisão de contexto fresco do DESIGN, pela escada abaixo; registre cada nota no Advisor Ledger, nenhum HIGH aberto |
| `RODADA` | agente fresco, um por tarefa | brief `references/executor.md`, com só os 5 campos dele e a tarefa da linha `tarefa:` |
| `COMMITAR` | você | commite os arquivos listados (`git add` por nome) e chame `verificar` |
| `VERIFICAR` | o script | `bash sdd/bin/sdd-drive.sh verificar <DEFINE> --fundo` e, depois, `proximo` |
| `ESPERAR` | ninguém | espere alguns minutos e chame `proximo`; o teste final roda destacado de você |
| `CORRIGIR` | você | leia o log citado; se o DESIGN estava errado, corrija-o; se foi uma tarefa, reabra a linha com `- [ ]` no `PROGRESS`; commite e chame `proximo` |
| `AVALIAR_E_RELATAR` | agente fresco e você | avaliador de contexto fresco (`sdd-build/references/contexto-fresco.md`, modo `veredito`, até 2 ciclos) e o `BUILD_REPORT`; depois `bash sdd/bin/sdd-drive.sh concluir <DEFINE>` |

**O teste final pode levar mais que o limite de um comando do seu agente:** por isso `verificar --fundo`, que devolve na
hora e deixa o teste rodando destacado. Só o script roda o teste que decide: o resultado do executor não conta.

**Contexto fresco:** pela escada de `sdd-build/references/contexto-fresco.md`. Com subagente, um por tarefa, com o brief
como prompt inteiro. Sem subagente, grave o brief em `sdd/reports/briefs/BRIEF_executor-drive_{F}.md` e rode
`bash sdd/bin/sdd-drive.sh aguardar <DEFINE> executor-drive sdd/reports/briefs/BRIEF_executor-drive_{F}.md`: ele para
com exit 40 e a parada ⏸️. Repasse a parada; na volta, `--resume`.

**O bloco `<<<RODADA` que volta do executor:** `bloqueio:` preenchido ⇒ `bash sdd/bin/sdd-drive.sh bloqueio <DEFINE> "<o motivo>"`. O
resto serve só para o relatório: quem diz se a tarefa andou é o `PROGRESS` em disco.

## Decisões durante a execução

Chamar o drive liga o encadeamento só nesta execução; nada muda em `flow.autonomous`. `[auto · de rotina]` vale a
recomendada, sem pergunta, e vai para o recibo: `bash sdd/bin/sdd-drive.sh recibo <DEFINE> "<o que decidi e como desfazer>"`, que
sai na seção `Decidi sozinho` do `DRIVE_REPORT`. As marcadas `[D1 · não se desfaz]`, `[D2 · muda o produto]`,
`[D3 · muda a regra do método]`, `[D4 · limite de tentativas]` e `[D5 · provas em conflito]` são sempre perguntadas à pessoa.

## Os motivos de parada

| `motivo:` | Exit | O que fazer |
|---|---|---|
| `gate-verde` | 0 | diga a frase, o resumo do `DRIVE_REPORT` e a barreira |
| `simulacao` | 0 | mostre o plano; nada foi gravado |
| `orcamento-rodadas` | 20 | pergunta `[D4 · limite de tentativas]` de `references/como-falar.md` |
| `gate-alterado` | 20 | pergunta `[D2 · muda o produto]` de `references/como-falar.md`, com os 2 comandos |
| `manual-ux` | 20 | mostre o checklist do `manual_fallback`; é terminal: o recibo vai ao `BUILD_REPORT`, e o drive não assina por ninguém |
| `clarificacao-pendente` | 20 | volte ao Define; nunca construa por cima de dúvida |
| `define-invalido` | 20 | volte ao Define |
| `gate-inconclusivo` | 20 | diga o que faltou (no log) e, resolvido, `--resume`; não gastou rodada |
| `bloqueio-humano` | 20 | parada ⏸️ com o texto do script; resolvido, `--resume` |
| `aguardando-sessao` | 40 | repasse a parada; na volta, `--resume` |
| `estado-invalido` | 20 | diga qual arquivo e as 2 saídas da seta; nunca edite o estado à mão |
| `branch-padrao` | 20 | ofereça a `sdd-new-session` |

Exit 2 é falha do próprio script (não conseguiu gravar, ou `sdd/bin/` desatualizado): diga a causa e a seta. Exit 64 é
chamada errada: corrija.

## ⛔ A barreira

**O drive nunca publica.** Nenhuma ação leva a `git push`, a deploy ou à `sdd-release`. Ao terminar, pare: quem chama a
`sdd-release` é a pessoa, e ela pede o OK de sempre. Verde no teste final não é "no ar".

## Por que cada regra existe

- **O script decide, o agente executa** — limite que mora no texto vira sugestão no fim de uma sessão longa; exit code não cansa.
- **Só o script roda o teste que decide** — quem construiu tende a ler o próprio resultado com boa vontade.
- **A impressão digital do teste final** — um agente com pressa pode enfraquecer o comando, e o verde deixaria de provar algo.
- **Parada na 3ª repetição** — uma tarefa que nunca anda giraria para sempre, já que a rodada não tem teto de tarefas.
- **Publicar fora do piloto** — publicar não se desfaz, e é a única decisão que nunca pode ser de rotina.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é `/sdd-drive`.

**Próximo passo:** com `gate-verde`, `/sdd-release <descrição do que liberar>`, chamado pela pessoa.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
