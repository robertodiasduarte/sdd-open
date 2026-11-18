# Relatório retroativo — custo e resultado dos revisores, F13 a F21 (2026-11-10)

Primeira medição com o `sdd/bin/eval-revisores.sh` (F19). Só leitura, sem rede, sem modelo julgando modelo: o script contou o que já estava registrado.

## O que foi medido

- **25 rodadas** de revisão adversarial com `META.txt` legível: F13_UX_LLM (6), F14_PLAYBOOK (4), F14_DRIVE (7, com as 2 da v2.7.1), F15_SLOTS (4) e F21_ENGENHARIA_REVERSA (4). As pastas `EXTERNAL_REVIEW_*` ficam fora do git; vieram dos 5 arquivos `*-revisoes-traces.tar.gz` guardados fora do repositório e da pasta de revisões da F21.
- **5 ledgers** no formato de 7 colunas, 116 linhas, todos aprovados no `ledger-revisao-lint.sh`: `sdd/reviews/LEDGER_REVISAO_{F13_UX_LLM,F14_PLAYBOOK,F14_DRIVE,F15_SLOTS,F21_ENGENHARIA_REVERSA}.md`.
- **Fora da medição:** F10, F11 e F12 têm ledger de 5 colunas na evidência, mas as pastas das rodadas não foram guardadas; sem `META.txt` não há custo. Uma pasta da F21 (`EXTERNAL_REVIEW_20261110-125836`) é de uma rodada que eu interrompi e ficou sem `META.txt` completo. O repositório privado não foi medido (decisão do brainstorm).

## Como ler a marca de dano destes ledgers

| Frente | Linhas | `sim` | `nao` | `?` | Como a marca foi posta |
|---|---:|---:|---:|---:|---|
| F13_UX_LLM | 23 | 10 | 6 | 7 | retroativo: convertido do ledger de 5 colunas da frente |
| F14_PLAYBOOK | 33 | 19 | 7 | 7 | retroativo: idem |
| F14_DRIVE | 41 | 4 | 12 | 25 | retroativo: idem |
| F15_SLOTS | 12 | 6 | 4 | 2 | retroativo: transcrito do Advisor Ledger do BUILD_REPORT |
| F21_ENGENHARIA_REVERSA | 7 | 1 | 6 | 0 | julgado por quem decidiu, pelo `sdd/review/CRITERIO_DANO.md` |

**Nos 4 retroativos, `sim` quer dizer só "achado aplicado cuja evidência cita o teste do conserto".** A terceira condição do critério (o cenário afeta dado, dinheiro, acesso, publicação ou disponibilidade) **não** foi julgada de novo: ninguém releu 109 achados antigos para isso. O número de "com dano" abaixo é, portanto, um **teto** para F13 a F15: inclui consertos com teste em mensagem, texto e casos de borda que o critério completo marcaria `nao`. Na F21, onde o critério inteiro foi aplicado, 1 de 7 achados é dano. O `?` (41 linhas) é achado aplicado sem teste citado: fica em "sem classificar". A F14_DRIVE tem poucos `sim` porque o ledger dela quase não cita nomes de teste na evidência, não porque a revisão achou menos.

## A tabela

eval-revisores — custo e resultado por papel, engine e modelo (25 pasta(s) lida(s) em <pasta com as 25 rodadas, fora do repositório>; 5 ledger(s))

| Papel | Engine (modelo) | Cobrança | Rodadas | Falhas | Pago US$ | Nominal US$ | Achados | Aplicados | Com dano | Falsos positivos | Fora de escopo | Sem classificar | Pago por dano | Nominal por dano | AGREE |
|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| revisor | claude (claude-fable-5-2) | assinatura | 4 | 0 | 0.0000 | 5.1073 | 7 | 6 de 7 | 1 de 7 | 0 de 7 | 1 de 7 | 0 de 7 | 0.0000 | 5.1073 | — |
| revisor | claude (claude-opus-5-5) | assinatura | 21 | 0 | 0.0000 | 50.3657 | 83 | 62 de 83 | 28 de 83 | 6 de 83 | 15 de 83 | 34 de 83 | 0.0000 | 1.7988 | — |
| 2º revisor | codex (-) | assinatura | 9 | 5 (5 cota ou tempo) | 0.0000 | n/d | 18 | 16 de 18 | 9 de 18 | 0 de 18 | 2 de 18 | 7 de 18 | 0.0000 | — | — |
| 2º revisor | gemini (-) | desconhecida | 0 | 1 (1 credencial) | n/d | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |
| 2º revisor | openrouter (deepseek/deepseek-v4-pro via Novita) | pay-per-token | 1 | 0 | 0.3214 | 0.3214 | 1 | 0 de 1 | 0 de 1 | 0 de 1 | 1 de 1 | 0 de 1 | — | — | — |
| 2º revisor | openrouter (deepseek/deepseek-v4-pro via Relace) | pay-per-token | 1 | 0 | 0.1827 | 0.1827 | 1 | 0 de 1 | 0 de 1 | 1 de 1 | 0 de 1 | 0 de 1 | — | — | — |
| 2º revisor | openrouter (deepseek/deepseek-v4-pro) | pay-per-token | 0 | 3 (3 cota ou tempo) | n/d | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |
| 2º revisor | openrouter (z-ai/glm-5.3 via Relace) | pay-per-token | 1 | 0 | 0.2194 | 0.2194 | 1 | 1 de 1 | 1 de 1 | 0 de 1 | 0 de 1 | 0 de 1 | 0.2194 | 0.2194 | — |
| 2º revisor | openrouter (z-ai/glm-5.3) | pay-per-token | 0 | 1 (1 cota ou tempo) | n/d | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |
| auditor | codex (-) | assinatura | 0 | 4 (1 cota ou tempo, 3 trocada por outra engine) | 0.0000 | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | n/a |
| auditor | openrouter (qwen/qwen3.7-plus via Alibaba) | pay-per-token | 23 | 0 | 1.0933 | 1.0933 | 5 | 1 de 5 | 1 de 5 | 4 de 5 | 0 de 5 | 0 de 5 | 1.0933 | 1.0933 | 78.0% (78 de 100) |
| auditor | openrouter (qwen/qwen3.7-plus) | pay-per-token | 0 | 1 (1 cota ou tempo) | n/d | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | n/a |
| desempate | claude (claude-opus-5-5) | assinatura | 1 | 0 | 0.0000 | 1.8145 | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |
| desempate | codex (-) | assinatura | 1 | 0 | 0.0000 | n/d | 0 | 0 | 0 | 0 | 0 | 0 | — | — | — |

fora da conta: 1 (EXTERNAL_REVIEW_20261110-125836: META ilegível ou incompleto)
RESULTADO: MEDIDO
→ leia cada taxa com a amostra ao lado: poucas rodadas dão número instável. O script conta o que está registrado; trocar a cadeia de revisão é decisão de quem lê.

## O que os números mostram (e o que não mostram)

- **Revisor por assinatura: pago zero, nominal alto.** O claude revisou as 25 rodadas. Custo de tabela: US$ 50,37 nas 21 de F13 a F15 (US$ 2,40 por rodada, em média) e US$ 5,11 nas 4 da F21 (US$ 1,28). Nada disso saiu do saldo. Por isso as duas colunas: quem olha só o pago conclui que o revisor é de graça; quem olha só o nominal não vê o que foi gasto de fato.
- **Auditor pago: US$ 1,09 em 23 rodadas** (qwen pela OpenRouter, de US$ 0,027 a US$ 0,087 por rodada, conforme o tamanho do diff). É o único custo recorrente que saiu do saldo. Concordou com o revisor em 78 de 100 vereditos. Dos 5 achados novos que ele levantou, **4 foram rebatidos com evidência** e 1 foi aplicado: amostra pequena, mas é o sinal de falso positivo mais forte da tabela, e inclui o caso do mesmo HIGH repetido em duas rodadas da F15.
- **2º revisor: metade das tentativas falhou.** Codex: 9 rodadas com resposta e 5 falhas por cota, mais 4 falhas quando era o auditor previsto (3 delas trocadas pela reserva). Deepseek: 2 respostas e 3 falhas. Glm: 1 resposta e 1 falha. Gemini: 1 falha por credencial. Quando respondeu, o codex trouxe 18 achados, 16 aplicados e nenhum rebatido com evidência; o custo dele não aparece porque a assinatura não informa valor (`n/d`, não zero).
- **O mesmo modelo custou diferente conforme o provedor.** O deepseek saiu por US$ 0,32 numa rodada (via um provedor) e US$ 0,18 em outra (via outro). São diffs diferentes, então a tabela não separa o efeito do provedor do efeito do tamanho; ela só deixa as duas linhas visíveis.
- **O custo que a tabela não vê.** O `META.txt` grava `$?` na chamada que estourou o tempo. Na F15 uma dessas chamadas custou cerca de US$ 1 sem responder (medido pelo saldo antes e depois; LM-010 do playbook). Aqui ela aparece como falha por "cota ou tempo" com custo `n/d`. O gasto real com o 2º revisor é maior do que a coluna Pago mostra.
- **Custo por falha com dano.** Para o revisor das frentes F13 a F15: US$ 1,80 nominal por achado "com dano" (28), que é teto de dano e portanto piso de custo. Para a F21, com o critério inteiro: US$ 5,11 nominal para 1 falha com dano. Para o auditor: US$ 1,09 pago para 1.

## Limites

- **Amostra pequena.** 25 rodadas, um revisor só, um auditor só. As linhas do 2º revisor têm de 1 a 9 rodadas. Nenhuma diferença entre engines aqui é estatisticamente firme.
- **Não é comparação controlada.** As engines não viram os mesmos diffs; frente maior tem mais achados.
- **O relatório só informa.** Trocar a cadeia de revisão é decisão do Roberto; o script não recomenda.
- **A marca de dano das frentes antigas é aproximada** (ver acima). Daqui para a frente a marca nasce na hora da decisão, pelo critério escrito.

## Reproduzir

```bash
bash sdd/bin/ledger-revisao-lint.sh sdd/reviews/LEDGER_REVISAO_*.md
bash sdd/bin/eval-revisores.sh <pasta com as EXTERNAL_REVIEW_*> --ledgers sdd/reviews
```
