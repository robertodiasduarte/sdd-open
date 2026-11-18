# UX REVIEW: F25 Skills duplicadas — o texto que o aluno lê

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F25_SKILLS_DUPLICADAS |
| **Date** | 2026-11-17 |
| **DEFINE** | `sdd/features/DEFINE_F25_SKILLS_DUPLICADAS.md` |
| **Status** | Ready for Design |
| **Escopo da revisão** | curta, por pedido do Roberto: a "interface" é texto de terminal e de conversa — o Status, o item ⚠️ do diagnóstico, o plano (`--duplicadas`), a pergunta de confirmação, a saída do `--limpar` e o desfazer |

## UX Summary

O aluno recebe três textos: o aviso no diagnóstico de sempre, o plano quando pede para limpar, e o resultado
da limpeza com o comando que desfaz. Os três precisam responder, sem abrir arquivo: **o que está acontecendo
com o meu agente, onde estão as cópias, o que vai sair, e como volto atrás.** O risco de UX é o aluno ler
"duplicata" e não entender por que importa, ou ler um caminho e não saber se é "do computador" ou "do projeto".

## User and Context

Aluno que nunca usou terminal, com o agente aberto na pasta do projeto, que viu uma skill se comportar
diferente do que esperava, ou que rodou o diagnóstico antes de abrir uma frente. Lê na janela do agente; não
abre pastas ocultas (`~/.claude`) por conta própria.

## Journey Map

| Passo | Intenção | Risco | O sistema confirma | Quando falha |
|---|---|---|---|---|
| Antes | rodar o diagnóstico de sempre | ignorar mais um ⚠️ | o item diz a consequência primeiro ("roda a mais velha") | — |
| Entrada | entender o aviso | "global" e "do projeto" sem sentido | cada cópia numa linha, com o lugar dito em palavras | — |
| Ação central | pedir o plano | medo de apagar algo | "Nada mudou ainda" no topo do plano | — |
| Decisão | dizer sim | sim sem saber o que autoriza | a pergunta repete quantas cópias saem e para onde vão | "não" ⇒ nada muda, dito |
| Feedback | ver o que saiu | não saber se deu certo | cada cópia tirada com o lugar de origem e o lugar na lixeira | plano mudou ⇒ "Nada foi tirado", motivo e o próximo passo |
| Recuperação | desfazer | perder o comando | o desfazer é a **última linha** da resposta, com o que ele faz | pasta que reapareceu não é sobrescrita, dito |
| Conclusão | conferir | duplicata volta | rodar o diagnóstico de novo ⇒ o ⚠️ some | — |

## UX/CX Findings

| # | Prioridade | Achado | Requisito para o Design |
|---|---|---|---|
| U1 | MUST | "Duplicada" não diz por que importa | A 1ª frase do item diz o efeito no agente: "o Claude Code roda a global, a 2.6.1, e não a 2.7.0 que o projeto traz" / "o Codex vê as 3 e escolhe uma sem dizer qual". |
| U2 | MUST | "global" e "do projeto" são jargão | Rótulos fixos com o sentido junto na 1ª vez: **global** (vale para todos os projetos deste computador) e **do projeto** (só nesta pasta). No `como-falar.md`, entram no glossário. |
| U3 | MUST | Caminho sem contexto | Cada cópia numa linha: rótulo, caminho completo, `versão X`, origem em palavras ("do SDD Open", "do starter", "de outra origem"), como chegou ("instalada pelo npx", "salva no git do projeto", "copiada à mão"). |
| U4 | MUST | Recomendação sem consequência | Cada item do plano termina com o que acontece depois: "Depois disso, o Claude Code passa a rodar a 2.7.0 do projeto." Cópia global: "Os projetos sem cópia própria ficam sem esta skill." |
| U5 | MUST | "Não escolho" parece defeito | Quando o plano não escolhe, diz por quê em 1 frase e o que o aluno pode fazer ("as duas dizem 2.4.0 e têm textos diferentes: alguém editou uma delas; compare e diga qual quer manter"). |
| U6 | MUST | Confirmação genérica | Pergunta `[D1 · não se desfaz]` com o número de cópias e o destino: **"Posso tirar estas 2 cópias mais velhas (vão para a lixeira e dá para desfazer)?"** com **sim** (recomendado), **mostrar o plano como veio**, **não**, **não sei**. (No Design, "mostrar uma por uma" virou "mostrar o plano como veio": a assinatura cobre o plano inteiro, e aplicar só uma parte seria outro plano.) |
| U7 | MUST | Erro do `--limpar` sem conserto | Toda saída ≠ 0 diz "Nada foi tirado." (ou o que voltou), o motivo em palavras e o próximo passo ("peça o plano de novo"). Nunca o erro cru do `npx`. |
| U8 | MUST | Desfazer escondido | O comando de desfazer é a última linha da saída do `--limpar`, precedido de "Para desfazer:", com o caminho completo. |
| U9 | SHOULD | Muitas duplicatas viram muro de texto | Diagnóstico normal: até 3 detalhadas; acima disso, 1 item com até 10 nomes e "e mais N", e o plano tem o detalhe. |
| U10 | SHOULD | Status sem a etapa nova | Etapa 3 **Limpar** na tabela de etapas: `Ambiente: ✅ 1 Verificar · ✅ 2 Explicar · ▶️ 3 Limpar`. |
| U11 | COULD | — | — |
| U12 | WONT | Cor ou ícone por cópia (velha em vermelho) | Terminal sem cor garantida e significado nunca só por cor; a palavra "mais velha" basta. |

## North Star Checks (Premium + Self-Evident)

### Premium (padrão de qualidade percebida)

Um símbolo por significado, sempre com palavra (⚠️ do diagnóstico, ✅ do resultado). Erro com causa e
conserto (U7). Nenhum parágrafo antes do relatório: a skill repassa a saída do script, como hoje.

### Self-Evident / Zero-Explanation

Teste do suporte: "isso é bug?" viria de um plano que não escolhe sem dizer por quê (U5) ou de um ⚠️ que
não diz o efeito (U1). Os dois viraram MUST.

## Gamification Strategy

N.A. — diagnóstico e limpeza; não há progresso nem hábito a reforçar.

## 60/30/10 Visual Strategy

N.A. — texto de terminal e de conversa, sem superfície visual.

## Accessibility and Responsiveness

N.A. (WCAG 2.2 AA) — sem superfície visual. Texto: significado nunca só por símbolo (U12); linhas curtas, uma
cópia por linha (U3).

## Lentes cognitivas (não bloqueiam)

- L2 Escolhas por passo: OK — uma pergunta só, 4 opções (U6).
- L3 Retomada: OK — o plano se recalcula; aplicar um plano velho é recusado com o próximo passo (U7).
- L6 Destaque único: OK — a recomendação é a única linha "Recomendo:" por item.
- L7 Agrupamento: OK — cópias agrupadas por agente e skill.
- L1, L4, L5: N.A. (sem tela, sem convenção visual, sem progresso).
- S Sinal de validação real: depois da F25 publicada, o 1º uso real na máquina do Roberto deixa o diagnóstico sem o ⚠️ de duplicata.

## Design Handoff

- Textos dos itens: U1–U5, U9 (`checar.sh`); a pergunta (U6) e o glossário (U2) no `references/como-falar.md`.
- Saídas do `--limpar`: U7 e U8.
- Etapa 3 **Limpar** na tabela de etapas da `SKILL.md` (U10).
- Notas de aceite: o teste de texto confere U1 (efeito na 1ª frase), U3 (rótulo, caminho, versão, origem, como chegou), U4 (consequência), U7 ("Nada foi tirado." em toda saída ≠ 0) e U8 (última linha).

## Open UX Questions

Nenhuma.

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-11-17 | ux-review | Revisão curta do texto que o aluno lê |

## Next Step

**Ready for:** `/sdd-design sdd/features/DEFINE_F25_SKILLS_DUPLICADAS.md`
