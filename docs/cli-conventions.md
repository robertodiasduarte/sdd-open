# Convenções de saída dos comandos

Todo script do SDD Open fala a mesma língua. A regra única: **símbolo sempre acompanhado de
palavra**. Ninguém depende de cor nem de emoji isolado para entender o que aconteceu — leitores
de tela, pipes, terminais sem cor e o Git Bash do Windows leem o mesmo que você.

## Vocabulário

| Símbolo | Palavra | Significado | Exemplo |
|---|---|---|---|
| `▶` | ação | algo está sendo feito agora | `▶ init — plano` |
| `✅` | sucesso | um passo terminou bem | `✅ .agents/skills/ com 9 skill(s) sdd-*` |
| `⚠️` | atenção | algo merece olhar, **não bloqueia** | `⚠️ gemini: adaptador incompleto — rode sync --vendors gemini` |
| `🛑` | bloqueio | parou; a linha diz a causa | `🛑 este comando precisa de um repositório git` |
| `→` | próximo passo | o que fazer agora | `→ rode 'git init' aqui, ou entre na pasta do seu projeto` |
| `+` `~` `=` | plano | criar · atualizar · já correto | `+ AGENTS.md (novo)` |

## A linha final de todo comando

```text
RESULTADO: <PALAVRA>
→ <o que fazer agora>
```

Palavras usadas: `INSTALADO` · `SINCRONIZADO` · `EM DIA` · `DIVERGENTE (n)` · `DRY-RUN` ·
`CANCELADO` · `DIAGNÓSTICO CONCLUÍDO` · `ERRO` (sdd-open.sh) · `VERDE` · `VERMELHO` · `INCONCLUSIVO` ·
`ASSINATURA HUMANA` · `CLARIFICAR` · `SPEC INVÁLIDA` (verify-gate.sh, report-lint.py) · `PULADO` ·
`ERRO DE USO` (gate-baseline.sh, gate-shell-evidencia.sh, avaliador-guard.sh, test-baseline.sh) ·
`COMMIT RECUSADO` (sdd/hooks/pre-commit; ver [hooks.md](hooks.md)) · `PRONTO` · `CONTINUAR` · `BLOQUEADO` ·
`AGUARDANDO_RECIBO` · `AGUARDANDO_HUMANO` · `PARAR` · `MANIFEST ILEGÍVEL` · `ENTRADA ILEGÍVEL` · `SLOT INVÁLIDO`
(sdd-fluxo.sh; ver [chained-flow.md](chained-flow.md)).

Um estado que não é sucesso **nunca** termina em silêncio. É isto que impede o exit `3` do gate
(inconclusivo, que devolve `0`… sem `--strict`) de parecer verde para quem lê.

## Erros: causa e conserto, sempre

Todo erro tem **duas linhas**: a primeira diz o que aconteceu, a segunda o que fazer, com o
comando quando houver. "Erro inesperado" não existe.

```text
🛑 .gemini/settings.json não é JSON válido (linha 12: Expecting ',' delimiter)
RESULTADO: ERRO
→ corrija ou renomeie o arquivo e rode de novo — nada foi alterado
```

## Exit codes

| Script | Códigos |
|---|---|
| `verify-gate.sh` | `0` verde · `2` vermelho · `3` inconclusivo · `4` assinatura humana · `5` clarificar · `64` spec inválida — `--strict` remapeia 3/4/5 → `1` |
| `sdd-open.sh` | `0` ok/ajuda/cancelado/dry-run · `1` divergente ou sem permissão · `64` uso/pré-condição · `65` marcadores do AGENTS.md · `66` JSON inválido |
| `playbook-lint.sh` | `0` ok · `1` zero hits / colapso · `2` formato inválido · `64` uso |
| `skill-lint.py` · `report-lint.py` · `design-lint.py` · `handoff-lint.py` · `kb-dominios.py` | `0` ok · `1` violações · `64` uso (no `skill-lint.py`, também opção desconhecida; `--conversa` liga a conferência da camada de conversa; no `report-lint.py`, `--pendente` sai `1` quando acha `avaliador: PENDENTE`) |
| `gate-baseline.sh` | `0` a base reprovou avaliando · `2` a base passou (sem dentes) · `3` inconclusivo · `64` uso |
| `gate-shell-evidencia.sh` | `0` nenhum exit de formatador · `2` ≥ 1 acusado · `64` uso ou git que falha |
| `avaliador-guard.sh` | `0` árvore commitada · `1` suja (lista e comando de commit) · `2` não conferido · `64` uso |
| `test-baseline.sh` | `0` só falhas conhecidas (ou `PULADO`) · `2` falha nova · `3` inconclusivo · `64` uso |
| `sdd/hooks/pre-commit` | `0` limpo (silêncio, ou `⚠️` de regra pulada) · `1` recusado — todos os achados `🛑 [classe]`, `RESULTADO: COMMIT RECUSADO`, um `→` por classe |
| `sdd/hooks/pre-push` | `0` sempre (só avisa `⚠️` quando atrás de `origin/<branch padrão>`) |
| `sdd-fluxo.sh` | `review-design`: `0` EXIGIDO · `1` DISPENSAVEL · `64` manifest ilegível (rode a revisão) · `loop`: `0` PRONTO · `10` CONTINUAR · `20` BLOQUEADO · `30` AGUARDANDO_RECIBO · `64` · `despachar`: `40` AGUARDANDO_HUMANO · `64` · `seguir`: `0` SEGUIR · `1` PARAR · `64` · `estado`: `0` ligado · `1` desligado · `64` valor inválido |
| `adversarial-review.sh` | `0` REVIEW COMPLETA · `64` uso, slot vazio, diff vazio ou > 8 MB, pasta não ignorada · `65` credencial (sem troca de engine) · `66` CLI ausente · `67` auditor = revisor ou lista esgotada · `68` REVIEW INVÁLIDA (resposta sem vereditos) · `--conferir`: `0` CONFERE · `2` NÃO CONFERE · `--ledger`: `0` LEDGER OK · `2` LEDGER SEM REVIEW · `64` ilegível ([adversarial-review.md](adversarial-review.md)) |
| `adversarial-review-gate.sh` | `0` GATE VERDE · `2` GATE VERMELHO (cada ❌ com o campo e o valor lido) · `3` GATE QUEBRADO (não conseguiu se isolar; nada foi chamado) · `64` uso ([adversarial-review.md](adversarial-review.md)) |
| `eval-agree.sh` | `0` MEDIDO · `2` SEM DADOS (inclusive sem a pasta padrão) · `64` uso ou pasta passada inexistente |
| `sdd-decisoes-lint.sh` | `0` ok · `2` violação (`arquivo:linha — motivo`) · `64` uso, caminho inexistente, tabela de marcas ausente ou nenhuma pergunta |
| `sdd-kb/scripts/gate.sh` | `0` verde · `2` vermelho (caso bom rejeitado, caso ruim aceito ou por outro motivo, âncora ausente, RULE_MAP do exemplo derivado, ou rodado da cópia gerada pelo `sync`) |
| `sdd-kb/scripts/validate_kb.py` · `kb_normativo.py` | `0` PASS · `2` FAIL · `64` uso |

O `kb-dominios.py` termina como os outros lints: no verde, `✅ <DEFINE>: KB Domains válido (…)`, os
testes do RULE_MAP (`<domínio>: <REGRA> → <teste>`), `RESULTADO: VERDE` e, se houver testes, `→ ponha
estes testes no cmd do Verify Gate…`; no vermelho, `🛑` por problema (o nome que falta vem com os que
existem, até 10, e "e mais N"), `RESULTADO: VERMELHO` e `→` com o conserto. O `gate.sh` imprime uma linha
só no verde (`RESULTADO: VERDE — 4 aceitas, 12 rejeitadas pelo motivo certo, …`).

**Exceção declarada:** `validate_kb.py` e `kb_normativo.py` vieram do starter com as mensagens em inglês
(`PASS:` · `FAIL:` · `WARN:`) e exit `2` na falha. Os testes portados conferem o texto dessas razões, então
elas ficam como estão; a skill `sdd-kb` manda o agente traduzir a saída para quem lê.

## Cor

`NO_COLOR` (convenção POSIX) desliga qualquer cor. Cor é só realce; nunca carrega significado.

## Comando sem argumento

`sdd-open.sh` sem argumento imprime a ajuda e sai `0`. Comando sem argumento é pedido de ajuda,
não erro de uso.
