---
description: "Executar a fase Build de um fluxo SDD/AgentSpec a partir dos arquivos Markdown de Brainstorm, Define e Design e de interações com o usuário. Usar quando o usuário quiser implementar uma feature já especificada: ler os três artefatos, extrair e ordenar o File Manifest, recomendar e confirmar o modo de execução, alterar somente o código previsto, verificar incrementalmente, tratar drift e prompts LLM, aplicar no banco a migration que o manifest trouxer (com confirmação do projeto por nome e ref e prova por leitura), executar o Verify Gate bloqueante do Define e gerar BUILD_REPORT_{FEATURE}.md com evidências. Requer acesso gravável ao projeto/código e deve terminar com o fluxo SDD concluído e o BUILD_REPORT conferido."
compatibility: "Requer um agente com acesso gravável ao projeto; não precisa do init do SDD Open: o Verify Gate se confere lendo a saída do comando."
---

# SDD Build

Na primeira resposta desta skill, comece com esta linha, uma vez só:
`sdd-build v2.10.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Executar implementação real. Não tratar Build como geração de um documento isolado.

## Fluxo resumido

1. Receber Brainstorm, Define e Design.
2. Confirmar acesso gravável ao projeto/código.
3. Extrair requisitos, Verify Gate, `LLM Prompts` e File Manifest.
4. Validar coerência entre os três artefatos e o estado real do projeto.
5. Criar plano de tarefas ordenado por dependências.
6. Recomendar um modo de execução e pedir decisão do usuário antes da primeira alteração.
7. Perguntar sobre revisão externa pré-build quando o caso justificar e a capacidade existir.
8. Executar cada tarefa de forma cirúrgica, com verificação incremental.
9. Aplicar drift detection e o gate de prompts LLM quando necessário.
10. Usar a retry ladder em falhas.
11. Aplicar a migration no banco — só quando o File Manifest tem migration — com confirmação do projeto (nome e ref) e prova por leitura, antes do Verify Gate.
12. Executar o Verify Gate do DEFINE como gate bloqueante.
13. Executar verificações complementares configuradas no projeto.
14. Perguntar sobre revisão externa pós-build quando o caso justificar e a capacidade existir.
15. Gerar o BUILD_REPORT usando [assets/BUILD_REPORT_TEMPLATE.md](assets/BUILD_REPORT_TEMPLATE.md).
16. Reler o relatório contra o checklist de conclusão desta skill.
17. Encerrar um build completo somente com `Execute o **SDD Handoff by RDD**.`

Ler [references/build-protocol.md](references/build-protocol.md) no início da execução.
Ler [references/execution-modes.md](references/execution-modes.md) ao selecionar o modo.
Usar [assets/PROGRESS_TEMPLATE.md](assets/PROGRESS_TEMPLATE.md) se o usuário escolher Ralph.
Usar [assets/WORKER_BRIEF_TEMPLATE.md](assets/WORKER_BRIEF_TEMPLATE.md) se o usuário escolher Briefs.
Ler [references/aplicar-migration.md](references/aplicar-migration.md) quando o File Manifest tiver migration, antes de aplicá-la.
Ler [references/verify-gate.md](references/verify-gate.md) antes do gate final.
Ler [references/llm-prompt-gate.md](references/llm-prompt-gate.md) somente quando houver sinal de runtime LLM/prompt.
Ler [references/retry-and-advisor.md](references/retry-and-advisor.md) quando houver falha repetida ou revisão externa formal.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: glossário desta skill e um exemplo completo.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Plano | 1 a 3 |
| 2 | Modo | 4 e 5 |
| 3 | Tarefas N/M | 6 a 11 (o contador no Status; uma frase antes de cada tarefa) |
| 4 | Verify Gate | 12 a 14 |
| 5 | Relatório | 15 a 17 |

Toda resposta, nesta ordem (pule a parte sem conteúdo): **Status** (`Build: ✅ 1 … · ▶️ 3 Tarefas 2/5 · ⬜ 4 …`;
✅ concluída, não só visitada; ⏸️ parada; ➖ pulada; ao voltar a uma etapa, o motivo vai em Agora) ·
**O que foi feito** (frases curtas, sem saída de comando; registra a escolha do aluno) ·
**Agora: etapa N — nome** (2 a 4 frases; antes de algo demorado, diga o que vai rodar e que não precisa
responder) · **Sua decisão** (autorização: pergunta em negrito + opções com o efeito de cada uma;
pergunta aberta: pergunta em negrito + como responder, com a saída "não sei"; agrupadas, numeradas) ·
**Próximo passo** (uma linha).

- Uma etapa por resposta; termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez — inclusive os do Status (glossário na referência).
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, "e mais N". Comando só quando
  o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, motivo em uma frase, onde a ação acontece, passos numerados com resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo — eu
  continuo daqui."

## Entradas obrigatórias

Exigir:
- `BRAINSTORM_{FEATURE}.md`;
- `DEFINE_{FEATURE}.md`;
- `DESIGN_{FEATURE}.md`;
- projeto/código gravável correspondente à feature.

Ler os três documentos integralmente antes de editar código. **Documento de uma fase anterior** (projeto começado antes desta versão): leia de onde estiver — `sdd/features/`, `sdd/` ou `.claude/sdd/` —, grave o novo na pasta desta versão e não pergunte onde está.

Se o projeto não estiver acessível (na web, ou sem ferramenta que grave arquivos), parar antes da primeira tarefa e
**recomendar** abrir o projeto num agente que grave arquivos (Claude Code, Codex, Cursor e outros), com os três
documentos. Se o usuário disser que só tem o chat, ou pedir, escrever o código no chat para ele salvar: nunca tomar
"ok" ou resposta vaga como escolha, nenhuma tarefa feita nem conferência afirmada sem o relato dele, e o relatório diz
que quem salvou e conferiu foi ele. Nunca fingir um Build feito só a partir dos documentos, nem dizer que há onde gravar.

Entradas opcionais:
- `UX_REVIEW_{FEATURE}.md`;
- orientação do projeto (`README`, guidance, conventions, config);
- comandos reais de lint/test/typecheck/build;
- ferramentas de agentes/subagentes;
- ferramenta de revisão externa;
- receipt humano de `manual-ux`.

## Hierarquia de autoridade

Para comportamento e aceite: (1) resposta explícita mais recente do usuário; (2) DEFINE; (3) DESIGN; (4) Brainstorm.

Para implementação técnica: (1) DESIGN; (2) código e padrões reais do projeto; (3) DEFINE; (4) Brainstorm.

Usar Brainstorm como proteção contra drift de intenção e contra reintrodução de itens cortados por YAGNI.

Nunca alterar requisito, arquitetura ou contrato silenciosamente para “fazer passar”. Se a implementação exigir mudança de especificação, parar a tarefa afetada e perguntar ao usuário.

## 1. Carregar e cruzar contexto

Extrair do Brainstorm:
- intenção original;
- abordagem escolhida;
- alternativas rejeitadas;
- YAGNI;
- limitações e dependências.

Extrair do DEFINE:
- MUST/SHOULD/COULD;
- Success Criteria;
- Acceptance Tests;
- Out of Scope;
- Constraints;
- Verify Gate;
- `LLM Prompts: true|false`.

Extrair do DESIGN:
- arquitetura;
- components;
- Key Decisions;
- File Manifest;
- Code Patterns;
- LLM Prompt Inventory quando aplicável;
- Data Flow;
- Integration Points;
- Testing Strategy;
- Error Handling;
- Configuration;
- Security;
- Observability;
- Requirements Traceability.

Se `LLM Prompts: true` no DEFINE e o DESIGN não tiver `## LLM Prompts`, parar e solicitar correção do Design.
Se `LLM Prompts: false` e o DESIGN tiver inventário de prompts, parar e resolver a divergência.
Se o File Manifest estiver ausente/incompleto, parar e corrigir o Design antes de implementar.

## 2. Inspecionar o projeto

Antes de qualquer escrita:
- localizar a raiz do projeto;
- ler guidance/conventions relevantes;
- verificar estado do versionamento quando disponível;
- identificar a branch atual quando Git existir;
- ler os arquivos que serão modificados;
- localizar dependências diretas citadas no manifest;
- identificar comandos reais de validação existentes;
- confirmar que os paths do DESIGN ainda correspondem ao projeto.

Se Git estiver disponível:
- não trabalhar diretamente na branch de deployment/default quando houver política de feature branch;
- criar ou usar uma branch adequada antes de editar;
- não inventar commits/SHAs.

Se Git não estiver disponível:
- continuar somente se o projeto puder ser editado com segurança;
- registrar no relatório que branch/commit attribution não estava disponível.

## 3. Compilar o plano de Build

Converter o File Manifest em tarefas.

Para cada tarefa registrar internamente:
- manifest id;
- path;
- action;
- purpose;
- dependencies;
- acceptance criteria relevantes;
- incremental verification command;
- security surface?;
- LLM prompt item?;
- owner/executor.

Ordenar por dependências.
Não começar uma tarefa com dependência incompleta.

Se houver path collision entre tarefas, executá-las sequencialmente.

## 4. Selecionar modo com o usuário

Ler [references/execution-modes.md](references/execution-modes.md).

Antes da primeira alteração:
1. medir os sinais do caso;
2. recomendar um modo;
3. apresentar a recomendação primeiro e justificar com sinais concretos;
4. pedir que o usuário escolha.

Modos:
- `default`: loop sequencial no contexto atual;
- `ralph`: um contexto limpo por tarefa, se o ambiente suportar reexecução/subagentes;
- `briefs`: experimental, workers stateless por wave, se o ambiente suportar paralelismo.

Nunca oferecer um modo que a plataforma ativa não consegue executar.
Se `ralph`/`briefs` não estiverem disponíveis, explicar isso na pergunta e recomendar `default`.

Registrar no BUILD_REPORT:
- sinais;
- recomendação;
- decisão do usuário;
- indisponibilidades da plataforma, se houver.

## 5. Decidir revisão pré-build

Uma revisão formal externa é opcional e depende de ferramenta/capacidade disponível.

Recomendar **sim** quando:
- arquitetura nova com 3+ arquivos;
- superfície de segurança;
- rota pública/cacheada;
- alteração de contrato crítica.

Recomendar **não** para ajuste trivial de 1–2 arquivos sem mudança de contrato.

A decisão é do usuário.

Se a capacidade externa não existir, não fingir revisão; registrar `Not available`.

Se ocorrer revisão formal, aplicar [references/retry-and-advisor.md](references/retry-and-advisor.md) e registrar toda nota como `APPLIED` ou `REBUTTED`.

## 6. Executar cada tarefa

Seguir cinco invariantes:
1. **Assumption becomes a question**: ambiguidade material → perguntar.
2. **Simplicity**: nada além do que o manifest exige.
3. **Surgical change**: não refatorar código adjacente sem necessidade.
4. **Criterion before code**: saber como verificar antes de escrever.
5. **Evidence**: não declarar sucesso sem executar a verificação.

Para cada item:
1. reler o contexto mínimo necessário;
2. executar drift detection;
3. executar prompt gate se aplicável;
4. criar/modificar/excluir somente o path previsto;
5. preservar estilo e abstrações existentes;
6. executar verificação incremental;
7. capturar comando, exit code e saída relevante;
8. marcar tarefa completa somente com evidência.

Antes de cada tarefa, uma frase ao aluno — qual tarefa (N de M), o que vai rodar e que não precisa
responder — com o contador no Status.

Não deixar TODO/FIXME como substituto de requisito.

## 7. Drift detection

Executar antes de cada item.

Perguntar:
- o path ou conteúdo introduz runtime prompt/LLM não inventariado?
- a implementação exige arquivo não previsto?
- o código necessário muda uma decisão arquitetural?
- aparece requisito fora de scope?
- um item removido por YAGNI está sendo reintroduzido?
- um contrato real do projeto contradiz o DESIGN?

Se houver drift:
- parar a tarefa afetada;
- explicar a divergência;
- oferecer opções ao usuário;
- atualizar especificação primeiro quando a mudança for material;
- registrar o evento no BUILD_REPORT.

Nunca “acomodar” drift silenciosamente no código.

## 8. Gate de prompts LLM

Ler [references/llm-prompt-gate.md](references/llm-prompt-gate.md) quando:
- `LLM Prompts: true`; ou
- drift detection encontrar runtime prompt/LLM.

Não inventar provider, model, prompt final ou output schema que o Design já deveria ter fechado.

Se o DESIGN exigir uma skill de prompt engineering ou loop-specification e ela não estiver disponível:
- não improvisar o prompt;
- perguntar/registrar a dependência;
- bloquear somente os itens LLM afetados.

## 9. Retry ladder

Em falha de verificação de uma tarefa, usar [references/retry-and-advisor.md](references/retry-and-advisor.md):

- primeira falha: corrigir no mesmo contexto se for erro local/trivial;
- segunda falha: reexecutar como tarefa fresca, sem carregar a hipótese anterior, usando somente critério que falhou + erro + inputs necessários;
- terceira falha: parar e registrar blocker; não contornar o critério.

Se a plataforma não suporta reexecução fresca:
- simular o FIX brief com contexto mínimo;
- declarar a limitação;
- não fingir que um novo contexto foi criado.

## 10. Verificar incrementalmente

Usar o comando real mais específico para a tarefa, por exemplo:
- teste unitário correspondente;
- typecheck do módulo;
- lint do arquivo;
- import/compile check;
- smoke local.

Não inventar comando.
Se nenhum comando existir, derivar um método observável apenas quando sustentado pelo projeto/Design; caso contrário perguntar.

Registrar resultado por tarefa.

## 11. Aplicar a migration no banco

Só quando o File Manifest tem migration (`*.sql`, pasta `migrations/`, ou ação descrita como migration).
Sem migration, pular sem mencionar banco.

Ler [references/aplicar-migration.md](references/aplicar-migration.md) — o protocolo inteiro está lá. As
regras, em resumo:

1. **Descobrir sem perguntar:** ferramenta (CLI do Supabase no PATH · MCP do Supabase na sessão · nenhuma
   ⇒ caminho manual pelo SQL Editor), projeto ligado (`supabase/.temp/project-ref`, `.env`, lista de
   projetos — o `project_id` do `config.toml` é nome local, não a ref), banco local × remoto.
2. **Projeto divergente para antes de tudo:** se o arquivo aponta para um projeto e a CLI/MCP está em
   outro, mostre os dois (nome e ref) e não aplique nada até o aluno escolher.
3. **Uma confirmação só**, com nome **e** ref do projeto, o SQL inteiro de toda migration pendente, e
   aviso em destaque quando há DDL destrutivo ou quando o destino é o único banco (produção).
4. **Aplicar antes do Verify Gate** — um passo por vez: aplicar, ler o resultado, provar, e só então o gate.
5. **Provar por leitura** (`information_schema`, `pg_proc`, `pg_policies`, `migration list`); exit 0 do
   comando não é prova. Migration já aplicada não é reaplicada — é registrada como "já aplicada em <data>".
6. **Registrar:** a seção `## Migrations aplicadas` do BUILD_REPORT (obrigatória quando *Files Changed*
   lista `.sql`/`migrations/`).

Nunca reescrever a migration para escapar de uma confirmação do servidor (`declined`); nunca aplicar SQL
que o aluno não viu.

## 12. Executar Verify Gate bloqueante

Ler [references/verify-gate.md](references/verify-gate.md).

O Verify Gate do DEFINE é a autoridade. Antes de rodá-lo, uma frase ao aluno: o que vai rodar e que não
precisa responder.

Rodar o `cmd` do gate, somente se for um comando real, seguro e disponível, e avaliar o `pass_when`:
- `exit 0` (o caso comum): `0` é green → seguir; qualquer outro código (inclusive `4` e `5` do pytest) é red →
  Build não pode ser concluído; corrigir código e repetir;
- `exit N` ou `contains: TEXT`: green só com esse código ou com esse texto na saída; senão, red;
- saída mostrando que a ferramenta não rodou (comando não encontrado, dependência ausente): inconclusivo →
  resolver ferramenta/infra; não marcar green;
- `kind: manual-ux` (`cmd: "N/A (manual-ux)"`): mostrar o checklist e aguardar receipt humano.

Nunca declarar sucesso com red ou inconclusivo.
Com manual-ux, exigir no relatório: quem validou, data e resultado.
O runner automático, com contrato próprio de exit codes, é do SpecGate/sdd-open — ver
[references/verify-gate.md](references/verify-gate.md); o exit do `cmd` cru não segue aquela tabela.
Com migration no manifest, red e inconclusivo têm uma primeira hipótese antes de qualquer outra: a migration não foi
aplicada, ou foi aplicada em outro projeto — repetir a prova por leitura da seção 11 antes de mexer em código.

## 13. Verificações complementares

Depois do gate, executar quando configurado:
- lint;
- typecheck;
- test suite relevante;
- build/compile;
- smoke não coberto pelo gate.

Esses checks complementam; não substituem o Verify Gate.

Se uma verificação complementar falhar, o Build continua incompleto até resolução ou blocker explícito.

## 14. Revisão pós-build

Quando houver ferramenta externa disponível, recomendar revisão pós-build se:
- segurança foi alterada;
- rota pública/cacheada foi alterada;
- lógica cross-file é sutil;
- modo ralph/briefs foi usado.

Recomendar não para fix trivial.

Se houver findings:
- verificar HIGH/MED no código antes de aceitar;
- registrar cada nota como APPLIED/REBUTTED;
- após HIGH aplicado, repetir o Verify Gate.

## 15. Gerar BUILD_REPORT

Usar [assets/BUILD_REPORT_TEMPLATE.md](assets/BUILD_REPORT_TEMPLATE.md) como única fonte estrutural do relatório.

O relatório deve ser baseado em evidências executadas, não estimativas apresentadas como fatos.

Incluir:
- metadata e fontes;
- Mode Selection;
- summary;
- task execution;
- arquivos criados/modificados/excluídos;
- migrations aplicadas (arquivo, projeto nome e ref, data/hora, prova por leitura) quando o manifest tem migration;
- prompts gerados/refatorados quando aplicável;
- drift;
- Verification Results;
- Verify Gate receipt;
- Acceptance Test Verification;
- Advisor Ledger quando houve revisão;
- issues/deviations/blockers;
- Final Status.

Se o Build estiver bloqueado:
- usar `Status: Blocked`;
- não inserir o handoff de conclusão (`Execute o **SDD Handoff by RDD**.`) como se estivesse completo;
- indicar a ação necessária para desbloqueio.

Se completo:
- usar `Status: Complete`;
- Final Status `COMPLETE`;
- inserir a seção final padrão.

## 16. Conferir o BUILD_REPORT

Releia o relatório inteiro contra o checklist de conclusão desta skill (seções do asset, Verify Gate, migration registrada quando houver, Next Step só em build completo).

A releitura confere estrutura e coerência básica do relatório.

Corrigir falhas antes de entregar.

## 17. Salvar outputs

Código:
- nos paths do File Manifest.

Relatório:

**Onde salvar.** Grave em `sdd/reports/` na raiz do projeto — pasta visível, igual em qualquer agente. Cada documento tem a sua pasta: BRAINSTORM, DEFINE e DESIGN em `sdd/features/`, BUILD_REPORT em `sdd/reports/`, revisões em `sdd/reviews/`, fichas em `sdd/handoffs/`.

- gravar como `sdd/reports/BUILD_REPORT_{FEATURE}.md`.

Não sobrescrever artefato histórico sem informar o usuário.

## Quality gate de conclusão

Antes de declarar Build completo:

- [ ] Brainstorm lido.
- [ ] DEFINE lido.
- [ ] DESIGN lido.
- [ ] Projeto real acessível e alterado (ou, no caminho do chat, salvo e conferido pelo usuário, com o relato dele).
- [ ] Modo escolhido pelo usuário e registrado.
- [ ] Todos os itens do File Manifest tratados.
- [ ] Nenhuma alteração fora do manifest sem decisão explícita.
- [ ] Drift registrado.
- [ ] Verificação incremental executada com evidência.
- [ ] Retry ladder respeitada.
- [ ] `LLM Prompts=true` tem receipt para cada item do inventory.
- [ ] Itens de segurança não foram delegados a worker barato.
- [ ] Manifest com migration: projeto confirmado pelo aluno (nome e ref) e migration aplicada — ou registrada como já aplicada.
- [ ] Manifest com migration: prova por leitura e seção `## Migrations aplicadas` no relatório.
- [ ] Verify Gate green (`0`), ou manual-ux com receipt humano.
- [ ] Checks complementares aplicáveis passam.
- [ ] Acceptance Tests têm evidência.
- [ ] Advisor findings, quando existentes, têm APPLIED/REBUTTED.
- [ ] Não há TODO/FIXME usado como implementação pendente.
- [ ] BUILD_REPORT foi gerado pelo asset, com Mode Selection (recomendação e decisão do usuário) e a tabela do Verify Gate.
- [ ] A releitura do relatório contra este checklist foi feita.
- [ ] Next Step completo contém somente `Execute o **SDD Handoff by RDD**.`

## Handoff de Build completo

A última seção do BUILD_REPORT completo deve ser exatamente:

```markdown
## Next Step

Execute o **SDD Handoff by RDD**.
```

Não acrescentar slash command, caminho, instrução de upload, menção a GPT/Skill ou tarefa paralela depois desse texto.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
