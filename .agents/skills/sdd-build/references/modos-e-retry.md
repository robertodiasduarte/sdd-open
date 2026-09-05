# Modos de execução do build e escada de retry

## Os três modos

| | Default (no contexto) | ralph | briefs (experimental) |
|---|---|---|---|
| Coerência entre arquivos | ✅ alta — um autor lembra schemas, nomes, assinaturas | ⚠️ cada volta re-deriva do DESIGN; pode divergir em naming | ⚠️ depende da curadoria dos briefs |
| Higiene de contexto em build longo | ⚠️ cresce; risco de perder o fio no fim | ✅ cada volta nasce limpa | ✅ workers sem estado |
| Commits | ao final ou por marco | ✅ atômico por tarefa | por wave |
| Retomável se cair no meio | ⚠️ perde o fio | ✅ arquivo de progresso retoma onde parou | ⚠️ por wave |
| Custo | menor | maior (relê a spec por tarefa) | workers baratos; orquestrador paga a compilação |
| Paralelismo | não | não | ✅ por wave de dependência |
| Melhor quando | arquivos acoplados, lógica sutil | volume independente, builds longos ou interrompíveis | volume paralelizável fora de segurança e de prompts LLM |

**Regras da recomendação:** empate → default. Superfície de segurança (permissões, autenticação,
migrations com lógica) e prompts LLM **nunca** vão para workers baratos. `briefs` só vira
recomendação quando, removidos esses itens, sobra volume paralelizável relevante — e é rotulado
como experimento.

## ralph — contexto fresco por tarefa

1. Crie `sdd/reports/progress/PROGRESS_{F}.md` com uma linha por item do manifest (pendente).
2. A cada volta, uma **sessão/agente novo** recebe: "faça a PRÓXIMA tarefa pendente do
   PROGRESS, commite atomicamente, atualize o PROGRESS, pare". Nada da conversa anterior.
3. Entre voltas, o orquestrador roda o Verify Gate como condição de parada: `0` termina; `2`
   continua; `3` resolve; `4` pede o humano. Orçamento default = 2× o número de itens.
4. Ao convergir, gere o BUILD_REPORT normalmente, com os SHAs por volta.

## briefs — workers paralelos por wave

1. Itens sem dependência mútua e com caminhos disjuntos formam uma wave.
2. Um brief autocontido por item (`sdd/templates/fragments/WORKER_BRIEF.md`): subtarefa,
   entradas inline, critérios de aceite numerados, formato de saída. A curadoria das
   entradas é o trabalho nobre do orquestrador.
3. Despache a wave; verifique cada retorno contra os critérios: PASS · FIX (brief fresco de
   correção) · ESCALATE. `INPUT GAP` no retorno = brief mal compilado; complete e redespache
   (não conta na escada).
4. Só então libere a próxima wave. Verify Gate e BUILD_REPORT seguem iguais.

## Escada de retry — por que redispatch fresco

Retry no mesmo contexto ancora o modelo na hipótese errada da primeira tentativa: ele conserta
na margem em vez de reconsiderar. O redispatch corta a âncora; o critério verbatim garante que
a nova tentativa mira o aceite certo.

```text
FAIL 1ª vez → corrigir no contexto (lint, typo, import).
FAIL 2ª vez → REDISPATCH FRESCO: brief com APENAS
              (1) o critério que falhou, verbatim;
              (2) o erro, verbatim;
              (3) "trate como tarefa nova — não assuma que a anterior estava quase certa".
              Sem o código nem o raciocínio da tentativa anterior.
FAIL 3ª vez → PARAR e reportar no BUILD_REPORT. Nunca contornar o critério.
```
