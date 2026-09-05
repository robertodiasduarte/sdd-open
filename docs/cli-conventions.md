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
`ASSINATURA HUMANA` · `CLARIFICAR` · `SPEC INVÁLIDA` (verify-gate.sh, report-lint.py).

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
| `skill-lint.py` · `report-lint.py` | `0` ok · `1` violações · `64` uso |

## Cor

`NO_COLOR` (convenção POSIX) desliga qualquer cor. Cor é só realce; nunca carrega significado.

## Comando sem argumento

`sdd-open.sh` sem argumento imprime a ajuda e sai `0`. Comando sem argumento é pedido de ajuda,
não erro de uso.
