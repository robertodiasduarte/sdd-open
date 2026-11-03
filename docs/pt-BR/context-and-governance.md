<!-- Idioma: [English](../context-and-governance.md) · **Português** -->

# Contexto e governança

Desde a v2.4.0, o `sdd-define` roda duas revisões feitas por um **agente fresco** — um que não viu a
conversa que escreveu a spec — e o `sdd-design` lê o que elas deixam:

1. **Passo 1.5, contexto de domínio.** Antes de escrever a spec, um *cartógrafo* lê o código do domínio
   que a feature toca e grava `sdd/contexto/<slug>.md`: os dados, as operações, as interfaces e as regras
   que o código já impõe, cada uma com `arquivo:linha`. Ele **ajuda, não trava**: se falhar duas vezes, o
   Define segue sem ele.
2. **Passo 11, governança.** Depois de gravado o DEFINE, um *revisor* o compara com o catálogo de
   governança da `sdd-governanca` (lançamento que não se apaga, trilha de auditoria, fechamento de
   período, aritmética exata…). Roda em **todo** Define: sem dinheiro, tributo, folha ou dado pessoal,
   responde N.A. em uma linha. Ele **trava**: até fechar, o `verify-gate.sh` sai 5 e o build e a release
   param.

Os dois agentes só podem gravar um arquivo cada. O `sdd/bin/governanca-fronteira.sh` tira o sha256 de cada
arquivo do repositório antes e depois do despacho e acusa qualquer outra escrita (`FORA:`). O agente que
não abre uma sessão fresca sozinho para com `⏸️` e exit 40 (`sdd-fluxo.sh despachar`): você abre uma
sessão nova, cola o brief, e cola de volta o bloco `<<<CONTEXTO` ou `<<<GOVERNANCA`.

## Depois de atualizar: o exit 5 num DEFINE que já existia

Um DEFINE escrito antes da v2.4.0 não tem a linha `Governança`, e o build dele para uma vez com:

```text
🛑 GOVERNANÇA NÃO REVISADA (exit 5) — … não tem a linha Governança com um valor final
RESULTADO: CLARIFICAR
```

Duas saídas:

1. Numa sessão nova do agente, peça: *"rode só o passo 11 (Governança) do sdd-define sobre
   sdd/features/DEFINE_X.md"*. Não rode o Define inteiro de novo: ele regravaria a spec.
2. Ou dispense, com motivo, na tabela do `## Technical Context` (um DEFINE antigo sem essa seção a ganha, com o
   cabeçalho `| Aspect | Value | Notes |`):

   ```markdown
   | **Governança** | dispensada — <motivo> | <seu nome, data> |
   ```

   Se o DEFINE também tiver o marcador "governança não rodou" (o passo 11 falhou duas vezes), troque-o por
   `- [x] (governança) dispensada — <motivo>`: enquanto o marcador estiver lá, o gate continua em 5.

Os valores finais que o gate aceita são `N.A. — <motivo>`, `GOVERNANCA_REVIEW_<F>.md · …` e
`dispensada — <motivo>`. `pendente` e `falhou` mantêm o exit 5.

## O mapa de domínios e os patterns

O cartógrafo só roda quando o projeto tem um mapa de domínios, `sdd/patterns/dominio.md`; sem ele, o passo
1.5 diz "pulado" e o Define segue. O mapa e os patterns do projeto (o esqueleto que se copia para uma
operação, tela ou migration nova) moram em `sdd/patterns/`; o formato está em
[`sdd/patterns/README.md`](../../sdd/patterns/README.md). O Design cita um pattern como
`**Pattern:** \`patterns/<x>.md §Esqueleto\` (validado_em AAAA-MM-DD)`, e um pattern citado com mais de 90
dias ou com âncora morta reprova o Design.

## Scripts

| Script | O que faz | Exits |
|---|---|---|
| `sdd/bin/contexto-lint.sh` | confere um CONTEXTO (cabeçalho, 7 seções, âncoras `arquivo:linha`, `LM-nnn` vivo, `ctx:` conhecido); `--validade` (ainda vale contra `origin/<branch padrão>`?); `--sugerir` (gerar, reusar ou pular, no máximo 2 domínios); `--self-test` | `0` ok · `1` vencido (`--validade`) · `2` inválido · `64` uso |
| `sdd/bin/patterns-lint.sh` | confere a pasta de patterns; `--design <DESIGN>` reprova pattern citado vencido ou com âncora morta; `--self-test` | `0` · `2` · `64` |
| `sdd/bin/governanca-fronteira.sh` | `--snapshot` / `--comparar`: prova que o agente fresco só gravou o arquivo permitido | `0` só o permitido · `1` `FORA:` · `64` não verificado |
| `sdd/bin/governanca-bloco.py` | confere o bloco `<<<GOVERNANCA` que o revisor devolve contra o relatório e a fronteira | `0` válido · `1` `resultado: FALHA` · `2` bloco inválido · `64` |
| `sdd/bin/docs-extract-decisions.sh` | monta `docs/adr/index.md` com os títulos `### Decision N:` dos DESIGNs, com os órfãos | `0` · `2` conservação violada · `64` |

O `--self-test` dos dois lints precisa de `sdd/fixtures/contexto/` e `sdd/fixtures/patterns/`. O `init` copia
`sdd/fixtures/` só na 1ª instalação: num projeto instalado antes da v2.4.0, copie essas duas pastas do
pacote (sem elas, o self-test sai 64 nomeando a pasta).

O contrato de máquina das três passagens (gate, cartógrafo, revisor) está em
[`sdd/WORKFLOW_CONTRACTS.yaml`](../../sdd/WORKFLOW_CONTRACTS.yaml).
