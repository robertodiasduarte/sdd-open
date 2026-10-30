<!-- Idioma: [English](../roadmap.md) · **Português** -->

# Roadmap

O que o SDD Open pretende acrescentar e o que ainda está pesando. O que já vem no pacote está no
[README](../../README.pt-BR.md) e na [comparação](comparison.md).

**Como ler a coluna de status.** *planejado* quer dizer que o trabalho está desenhado e na fila, sem
data: o ritmo depende dos ciclos de revisão, não de um calendário. *em avaliação* quer dizer que a
ideia está sendo pesada e pode não acontecer. Um tema sai desta página quando é publicado, e o
mecanismo chega com o próprio documento.

| Tema | O que traz | Status |
|---|---|---|
| **Fluxo encadeado** | cada fase oferece a seguinte; classes de decisão no formato de pergunta; parada com ponto de retomada quando o agente não abre uma sessão nova sozinho | *planejado* |
| **Revisão adversarial** | revisão por um segundo vendor sobre um diff congelado, com um registro editável de engines e um gate offline que confere que a revisão aconteceu | *planejado* |
| **Contexto e governança** | um mapa do domínio antes do Define, patterns do projeto que o Design cita, e governança que segura o Define de um sistema financeiro até rodar | *planejado* |
| **`sdd-loop-builder` e `sdd-drive`** | uma skill para código que chama um LLM em laço, e uma que conduz várias fases seguidas com as mesmas paradas humanas | *planejado* |
| **Reconciliação spec ↔ código** | conferir que o manifest de arquivos cobriu todo requisito, não só que o aceite passou | *planejado* |
| **Specs como deltas** | spec escrita como diferença contra um conjunto canônico de capacidades, no lugar de um documento de vida longa | *em avaliação* |

Todo tema mantém as regras que o pacote já segue: a verdade mora num script ou num hook do git que
roda nos sete agentes suportados, e o que depende da ferramenta de um agente só degrada para uma
parada manual, em vez de quebrar.
