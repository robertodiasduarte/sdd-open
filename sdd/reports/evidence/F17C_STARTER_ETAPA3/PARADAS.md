# Tabela de paradas — starter v1.5.18 × skill gerada pela F17c

"Parada" = pergunta obrigatória ao aluno, ponto de aprovação, comando que o aluno roda, condição que bloqueia o fim
(DEFINE_F17C_STARTER_ETAPA3, critério de aceite do Roberto, como na F17b). Montada lendo os dois textos: o da tag
`v1.5.18` do starter (clone `/Users/robertoduarte/rdd-worktrees/sdd-starter-f17c-ref`) e o gerado (geração de ensaio
da árvore `e1f1b42` sobre um clone da `v1.5.18`); o diff inteiro está em `PARADAS-diff-v1.5.18.log`. A base das linhas
é a tabela de paradas do lado do starter da comparação (`COMPARACAO-define-design-build.md`, §3). Toda linha **nova**
precisa do OK do Roberto; recusada, sai do caminho web.

## sdd-define

| Parada | v1.5.18 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| Brainstorm ausente ou ilegível: pedir o arquivo | sim | sim | não | — |
| Brainstorm contraditório: perguntar qual decisão prevalece | sim | sim | não | — |
| Perguntas de clarificação, uma por vez, até 5 por rodada, recomendada primeiro | sim | sim | não | — |
| Clarity Score < 12/15: continuar perguntando | sim | sim | não | — |
| Métrica sem número: perguntar o alvo | sim | sim | não | — |
| EARS reprovado bloqueia | sim | sim | não | — |
| LLM Prompts: 1 sinal fraco e intenção ambígua ⇒ perguntar | sim | sim | não | — |
| Verify Gate: "existe um comando que devolve 0?" / qual comando | sim | sim | não | — |
| Verify Gate ausente: o DEFINE não fica pronto | sim | sim | não | — |
| Lint estrutural (`validate_define.py`, "quando houver filesystem e Python") | sim (o agente roda) | não: releitura do checklist pelo agente | não (uma condição a menos) | — |
| Open Questions sem bloqueante / nenhum marcador ativo | sim | sim | não | — |
| Encerrar com pendência ⇒ rascunho `Needs Clarification` | sim | sim | não | — |
| Documento de fase anterior em outra pasta | — (tudo em `sdd/`) | lido de onde estiver, **sem pergunta** | não (a frase tira uma pergunta possível) | — |

## sdd-design

| Parada | v1.5.18 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| Brainstorm ausente: pedir o arquivo | sim | sim | não | — |
| DEFINE ausente: pedir; não desenhar só do Brainstorm | sim | sim | não | — |
| Prontidão da entrada (DEFINE fechado, flag literal, gate, Out of Scope) | sim | sim | não | — |
| Sem código acessível: perguntar stack e estrutura; greenfield só com confirmação | sim | sim | não | — |
| Conflito entre fontes (ou UX Review × DEFINE): perguntar | sim | sim | não | — |
| Decisões técnicas bloqueantes, uma por mensagem | sim | sim | não | — |
| LLM Prompts ausente/ambíguo: perguntar | sim | sim | não | — |
| `loop` × `one-shot` na dúvida: perguntar | sim | sim | não | — |
| Biblioteca ou serviço não confirmado e bloqueante: perguntar | sim | sim | não | — |
| Lint estrutural (`validate_design.py`) | sim (o agente roda) | não: releitura do checklist, com as regras que só o validador tinha | não | — |
| Sem placeholder/TBD em `Ready for Build` | sim | sim | não | — |
| Não sobrescrever DESIGN existente em silêncio | sim | sim | não | — |
| Encerrar com pendência ⇒ `Draft` | sim | sim | não | — |
| Revisão externa formal só se houver | sim | sim | não | — |

## sdd-build

| Parada | v1.5.18 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|
| Entradas: Brainstorm, DEFINE, DESIGN e projeto gravável; sem projeto, pedir | sim | sim — e **recomenda** abrir num agente que grave arquivos; se o aluno diz que só tem o chat (ou pede), o código vai no chat para ele salvar, sem tomar "ok" como escolha e sem marcar tarefa feita sem o relato dele | não (a mesma parada, com as duas saídas descritas) | OK do Roberto, 2026-11-14 (avaliador, ciclos 2 e 3) |
| `LLM Prompts` do DEFINE × DESIGN divergem: parar | sim | sim | não | — |
| Manifest ausente ou incompleto: parar | sim | sim | não | — |
| Branch padrão: não trabalhar nela | sim | sim | não | — |
| Modo de execução: recomendar e o aluno escolhe | sim | sim | não | — |
| Revisão externa pré e pós-build: perguntar quando a ferramenta existe | sim | sim | não | — |
| Ambiguidade material / mudança de especificação ⇒ parar e perguntar | sim | sim | não | — |
| Drift detectado (6 perguntas) ⇒ parar e perguntar | sim | sim | não | — |
| Skill de prompt ausente ⇒ bloquear o item e perguntar | sim | sim | não | — |
| 3ª falha da escada de retry ⇒ parar | sim | sim | não | — |
| Sem comando de verificação ⇒ perguntar | sim | sim | não | — |
| Migration: projetos divergentes, nenhum descoberto, pendente fora do manifest ⇒ parar e perguntar | sim | sim | não | — |
| Migration: a confirmação "Posso aplicar neste projeto?" com o SQL inteiro | sim | sim | não | — |
| Migration manual / `declined`: o aluno cola o SQL e diz "rodei" | sim | sim | não | — |
| Migration: senha do banco pedida pela CLI | sim | sim | não | — |
| Migration: gravar `- banco:` em `sdd/ambiente.md` (condição do checklist) | sim | não: só a seção `## Migrations aplicadas` | não (uma exigência a menos) | — |
| Verify Gate vermelho/inconclusivo/manual-ux com recibo | sim | sim | não | — |
| Checks complementares falham ⇒ build incompleto | sim | sim | não | — |
| Lint do relatório (`validate_build_report.py`) | sim (o agente roda) | não: releitura do checklist | não | — |
| Build bloqueado ⇒ `Status: Blocked`, sem handoff | sim | sim | não | — |
| Não sobrescrever relatório histórico sem avisar | sim | sim | não | — |

## As duas que mudaram de pasta (decisão do Roberto, revisão do DESIGN, nota 4)

| Skill | Parada | v1.5.18 | gerada | nova? | OK do Roberto |
|---|---|---|---|---|---|
| `ux-review-builder` | projeto com os documentos do Define em outro lugar: perguntar onde ficam | sim | sim | não | — |
| `ux-review-builder` | documento de uma versão anterior em `sdd/` ou `.claude/sdd/` | — | lido de onde estiver, sem pergunta | não | — |
| `sdd-engenharia-reversa-saas` | duas pastas com documentos do mesmo ciclo: perguntar a pasta ativa | sim (qualquer documento do ciclo) | só para o mesmo documento deste ciclo em duas pastas | não (a pergunta fica mais rara) | — |
| `sdd-engenharia-reversa-saas` | sem projeto identificado: perguntar onde salvar | sim | sim | não | — |

**Paradas novas: 0.** Nenhuma pergunta ao Roberto.

## Diferenças que não são paradas, mas mudam o que o aluno vê

- **Pastas:** DEFINE e DESIGN em `sdd/features/`, BUILD_REPORT em `sdd/reports/`; a ux-review gerada lê o DEFINE em
  `sdd/features/` e grava o UX_REVIEW em `sdd/reviews/`; a engenharia reversa grava em `sdd/features/`. Na web, tudo
  no chat, dizendo que não foi gravado.
- **Sem validador:** os 3 scripts Python e os testes deles não vão mais no zip; o quickstart perdeu a seção "valide os
  artefatos localmente".
- **Versão:** a linha de identificação passa de `v1.2.0`/`v1.1.0`/`v1.2.0` para `v2.7.0`/`v2.7.0`/`v2.10.0` (a do Open).
- **Exemplos sem número de documento:** o DEFINE de exemplo descreve o CPF de teste em palavras.
- **Marcas nos exemplos de pergunta:** os exemplos dos 3 `references/como-falar.md` ganharam `[D2 · muda o produto]`
  ou `[auto · de rotina]` antes da pergunta (o lint de decisões do Open lê `.agents/skills/` inteiro); é texto de
  exemplo para o agente, não pergunta nova. Nos logs do teste do iniciante nenhuma marca apareceu para o aluno.
- **Fim do build bloqueado:** "não inserir o handoff de conclusão como se estivesse completo" no lugar de "handoff de
  Release" (revisão, rodada 1, R2).
