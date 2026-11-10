# Revisão do DESIGN — F19_CUSTO_REVISORES (2026-11-10)

Revisor: agente de contexto novo, só leitura no repositório; rodou os dois protótipos (guardados fora do repositório) sobre as 25 pastas reais de revisão e sobre casos montados por ele numa pasta temporária, com `/bin/bash` 3.2.57. 21 chamadas de ferramenta, ~6 min.

**VEREDITO: NÃO PRONTO** — 2 HIGH, 7 MED, 8 LOW. As 2 HIGH quebravam a premissa de que o mesmo arquivo serve ao loop, ao lint e à release.

| # | Sev. | Nota | Evidência do revisor |
|---|---|---|---|
| 1 | HIGH | o lint exigia `@engine` no id; o `adversarial-review.sh` só rotula com 2 revisores e o loop só casa id exato ou a base | reprodução: lint VERDE e `loop` com "grave(s) sem veredito no ledger: N1 R1" (exit 10); trocando os ids, loop PRONTO e lint VERMELHO; 13 das 25 rodadas reais têm ids sem `@` |
| 2 | HIGH | rodada sem achados (ou só com dispensa) dá 64 no lint e abortaria a release | `ledger-revisao-lint.sh sdd/fixtures/fluxo/ledger-r2-dispensado.md` → 64 |
| 3 | MED | custo `US$ n + $?` lido como sem custo | META com `US$ 0.0500 + $?` → `0.0000 (n/d em 1 de 2)` |
| 4 | MED | engine que falhou antes da troca fora de "Falhas"; custo dela na linha da que respondeu | 3 pastas reais com `auditor_fallback_usado : sim` e a tabela mostrando 1 falha do codex |
| 5 | MED | 2º revisor `indisponível` virava linha de engine com falha por cota | saída do protótipo sobre `sdd/fixtures/fluxo/review-r2-indisponivel` |
| 6 | MED | o medidor descartava linhas do ledger em silêncio | 3 linhas sumidas numa execução (sem barra final, veredito digitado errado, pasta com sufixo) |
| 7 | MED | a mesma dupla (revisão, achado) em 2 ledgers contava em dobro; o lint não via | `Aplicados 2 de 2` com um achado só |
| 8 | MED | o lint não conhecia bloco cercado nem outra tabela; quase-formas de `retroativo: sim` sem aviso | 4 reproduções |
| 9 | LOW | rótulo `@engine` não conferido contra quem revisou | `R1@codex` contado na linha do claude |
| 10 | LOW | pasta com sufixo de colisão recusada | `adversarial-review.sh` cria `…-2` quando o nome existe |
| 11 | LOW | `≈` só no nominal; custo por dano sem ressalva; valor abaixo de 0,0001 vira 0.0000 | `≈US$ 0.000050` → `≈0.0000` |
| 12 | LOW | "pasta sem linha em nenhum ledger": DESIGN e protótipo divergiam | — |
| 13 | LOW | "nome de pasta repetido" não tem como acontecer com uma pasta só | — |
| 14 | MED | faltava `tests/test_correcoes_w0.py:145` (versão da `sdd-build`) no manifest | — |
| 15 | LOW | `teste:` aceitava qualquer palavra e era sensível a caixa | "o teste: falha" passava |
| 16 | LOW | cabeçalho fora do molde virava 6 violações | — |
| 17 | LOW | violações de um arquivo se perdiam se o seguinte era ilegível | — |

Conferidos sem achado: nomes dos campos do desempate; papel que não rodou; as somas em `Decimal` batem com conta independente (revisor opus 50.3657, fable 5.1073, auditor qwen 1.0933, desempate 1.8145); AGREE 78 de 100, igual ao `eval-agree.sh`; ids com dois revisores casam sem dobro; `\|`, `rodada=5a`, engine com `:` e `/`, CRLF; o loop lê o ledger de 7 colunas com ids rotulados (`PRONTO`, idêntico ao de 5 colunas); `tests/test_bash32.py` pega os scripts novos por glob; nenhum padrão do `publish-gate` casa com os nomes das fixtures; bash 3.2 e convenções de saída.

Vereditos por nota: Advisor Ledger do `DESIGN_F19_CUSTO_REVISORES.md` (as 17 APLICADA). Um erro meu apareceu no caminho, fora das notas: o brainstorm dizia que os ledgers de 5 colunas nunca tinham sido gravados; eles existem em `sdd/reports/evidence/{F}/ledger-review.md` para F10 a F14 (corrigido no BRAINSTORM, no DEFINE e no DESIGN).
