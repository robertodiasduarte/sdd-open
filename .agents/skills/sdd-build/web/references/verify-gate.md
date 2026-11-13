# Verify Gate no Build

## Regra

O bloco `verify_gate` do DEFINE é o acceptance gate bloqueante.

Não substituir por lint/test genérico.

Campos esperados:
- `kind`;
- `cmd`;
- `pass_when`;
- `threshold`;
- `manual_fallback`.

Kinds:
- `test`;
- `smoke`;
- `eval`;
- `typecheck`;
- `manual-ux`.

## Runner

Rodar o `cmd` e ler o código de saída — o starter não traz runner; o runner automático é do SpecGate/sdd-open.

- ler o `cmd`;
- verificar se é real, pertinente e não destrutivo;
- executar no contexto correto;
- avaliar `pass_when`.

Leitura do `cmd` pelo `pass_when`:
- `exit 0` (o caso comum) → `0` é green; qualquer outro código é red (inclusive `4` e `5`, que no pytest são
  erro de uso e nenhum teste coletado);
- `exit N` → só o código `N` é green;
- `contains: TEXT` → green só se a saída contém `TEXT`;
- saída mostrando que a ferramenta não rodou (comando não encontrado, dependência ausente) → inconclusivo, nunca green;
- `kind: manual-ux` (`cmd: "N/A (manual-ux)"`) → mostrar o checklist e exigir receipt.

Nunca instalar pacote ou executar mudança destrutiva apenas para “fazer o gate rodar” sem consentimento.

## Exit contract

Só vale para o runner do SpecGate/sdd-open; o exit do `cmd` cru segue a leitura da seção Runner, não esta tabela.

| Exit | Significado | Ação |
|---:|---|---|
| 0 | green | prosseguir |
| 2 | red | abortar sucesso; corrigir e rerodar |
| 3 | inconclusivo | resolver tool/infra; não marcar green |
| 4 | manual-ux | mostrar checklist e exigir receipt |
| 5 | clarification pending | voltar ao humano/spec |
| 64 | gate malformado/ausente | DEFINE inválido |

## manual-ux

Nunca autoaprovar.

Receipt mínimo:
- pessoa que validou;
- data;
- resultado;
- observações, se houver.

Somente receipt positivo libera o Build como Complete.

## Red ou inconclusivo com migration no manifest

Quando o File Manifest tem migration (`*.sql`, `migrations/`), um gate inconclusivo ou vermelho
tem uma **primeira hipótese**, antes de "infra" e antes de corrigir código: a **migration não
aplicada** — ou aplicada em **outro projeto** do Supabase (a conta tem vários; a versão aparece no
histórico de um e a coluna não aparece no outro).

Testar a hipótese pela leitura (seção 5 de [aplicar-migration.md](aplicar-migration.md)):
- a versão consta em `supabase migration list --linked` / `list_migrations` **do projeto confirmado**?
- o `select` em `information_schema`/`pg_proc`/`pg_policies` mostra o **efeito esperado** da migration —
  objeto criado aparece; objeto removido **não** aparece (ausência esperada); valor alterado está novo?

Resultado contrário ao efeito esperado ⇒ voltar à seção 11 da skill (descobrir o projeto, confirmar,
aplicar, provar) e só então rerodar o gate. Só com a prova do efeito em mãos é que vermelho vira "defeito no
código" e inconclusivo vira "infra".

## smoke 403 / infra noise

Não assumir regression automaticamente.

Se a evidência indicar bloqueio do runner/WAF:
- classificar como inconclusivo;
- executar a partir de ambiente apropriado quando possível;
- registrar no relatório.

## Build Report

Registrar:
- kind;
- comando/método;
- resultado;
- exit;
- output/evidência;
- receipt humano se aplicável.

Sem essa evidência, Final Status não pode ser COMPLETE.
