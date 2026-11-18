# Prova real do roteador no Codex CLI: o que existe e o que se perdeu

**Por que este resumo existe:** a repetição em `cdb85a9` usou os mesmos nomes de arquivo e sobrescreveu os transcritos e os
registros do calço de `867d6de`. Erro de quem conduziu o build. Depois, a conta do Codex ficou sem créditos, e a prova não
pôde ser refeita. Decisão D4 do Roberto (2026-11-04): aceitar a prova anterior como risco registrado.

## `867d6de`: as 3 execuções (o resultado da conferência foi lido na hora; os transcritos se perderam)

| Execução | Resultado | O que sobrou |
|---|---|---|
| `feliz` | Efeito certo: LOOP_SPEC `standard` + 2 prompts; 3 varreduras com `rc=0` e `existia=0`. A conferência apontou só a leitura da skill, por defeito dela: o comando composto terminava em `review-design`, que sai 1. Antes de ser sobrescrito, o transcrito passou nessa checagem na conferência corrigida | `prova-867d6de-feliz.LOOP_SPEC.txt` |
| `sem-skill` | PASSA | nada nesta rodada; ver `cdb85a9` |
| `sem-tipo` | PASSA: triagem `loop` no relatório, LOOP_SPEC + 2 prompts | `prova-867d6de-sem-tipo.LOOP_SPEC.txt`, `prova-867d6de-sem-tipo.relatorio.txt` |

## `cdb85a9`: transcritos íntegros

| Execução | Resultado | Arquivo |
|---|---|---|
| `sem-skill` | PASSA: nada gravado no destino, pergunta `[D2 · muda o produto]` à letra | `cdb85a9-codex-sem-skill.log` |
| `feliz` | REPROVA, parou certo: a amostra não nomeava provedor e modelo, e a skill manda parar. A amostra foi corrigida depois, sem nova execução | `cdb85a9-codex-feliz.log` |
| `sem-tipo` | Incompleta: `Your workspace is out of credits` | `cdb85a9-codex-sem-tipo.log` |

## Outras execuções reais com transcrito

- `ensaio-*.log` (`a63ed1a`) e `ensaio2-*.log` (`59420a9`): mostraram os defeitos corrigidos em `59420a9`. Em `ensaio2-sem-tipo.log`, a cadeia inteira rodou; o avaliador, ciclo 1, reconferiu esse transcrito e deu PASSA (`AVAL1-at021-reconfere-transcript.log`).

## O que muda no texto depois de `867d6de`

`726c43c` (regra de efeito sem reversão, na skill e nas regras; `WORKER_BRIEF.md`) e `cdb85a9` (uma linha da `sdd-ux-review`). Nada no
passo 4 da `sdd-build` nem na rota da skill mudou depois de `867d6de`. `726c43c` e `5ddc433` mudam também os sinais e o `design-lint`,
cobertos por testes.
