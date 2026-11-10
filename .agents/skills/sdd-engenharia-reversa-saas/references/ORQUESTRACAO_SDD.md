# Contrato entre investigação e SDD

## Posição no ciclo

`Pedido e contexto do projeto → Engenharia reversa do SaaS → Brainstorm da nova solução → Define da nova solução → próximo gate do projeto`.

Esta skill fornece uma entrada opcional, anterior ao Brainstorm. Não é uma nova implementação desses frameworks e não instala comandos/hooks, renumera fases ou altera configuração. Os documentos completos dos frameworks não foram auditados na criação do pacote; compatibilidade é por este contrato de entrada, não certificação de integração.

## Resolver dependências

1. Procurar no catálogo de skills e nas instruções do projeto as implementações indicadas de `sdd-brainstorm` e `sdd-define`; os nomes podem vir com prefixo de plugin (`<plugin>:sdd-brainstorm`), e as duas formas valem.
2. Dar precedência à localização/implementação explicitamente indicada pelo usuário ou projeto. Se houver conflito sem precedência, esclarecer antes da fase dependente.
3. Ler o arquivo de entrada real. Resolver assets e referências a partir dessa raiz, usando o mecanismo do ambiente: filesystem para arquivos locais, ferramentas do provedor para recursos remotos. Não construir um caminho pessoal fixo.
4. Registrar nome, caminho ou identificador resolvido e versão declarada. Não inventar versão quando não houver frontmatter/versionamento.
5. Se faltar uma dependência ou asset obrigatório, conservar o relatório e pausar apenas a fase dependente. Informar o recurso necessário e o estado. Não instalar nem reconstruir uma cópia de memória.

As dependências carregadas são a fonte de verdade de seus protocolos. As regras abaixo descrevem o contrato observado no escopo aprovado, não substituem sua leitura. Uma versão posterior incompatível exige explicitar o conflito; não enfraquecer gates para acomodá-la.

## Entrada do Brainstorm

Entregar ao contexto da dependência:

- Texto original do pedido de construir a nova solução, sem substituí-lo por um texto do concorrente.
- Relatório de engenharia reversa e seu status de cobertura.
- Público, problemas e restrições já informados; distinguir fatos do SaaS e decisões da nova solução.
- Achados relevantes com IDs F/E, hipóteses e limites de uso.
- Respostas anteriores da descoberta, quando realmente pertinentes, com sua origem.

O Brainstorm investiga a solução nova. Informação de marketing não vale como resposta sobre a dor do usuário. Uma comparação anterior de funcionalidades não substitui alternativas de abordagem validadas.

No contrato disponível: no mínimo três respostas de descoberta antes de abordagens; pergunta de amostras; duas ou três abordagens; seleção confirmada; revisão YAGNI; pelo menos dois checkpoints. Não contar a pergunta de amostras como descoberta, inferir respostas ou transformar decisões sobre o concorrente em confirmações da nova solução. Aproveitar respostas explícitas já existentes em vez de repetir perguntas apenas para contar interações.

Usar o molde `BRAINSTORM_TEMPLATE.md` no lugar que a dependência indicar (no SDD Open, `sdd/templates/`; em outras distribuições, um asset da própria skill). Colocar o link do levantamento e os IDs de apoio em `Context Gathered`, `Sample Data Inventory`, `Key Decisions Made` ou outras seções pertinentes já existentes. Distinguir influência de evidência e confirmação do usuário. Não acrescentar seções que alterem a estrutura canônica.

Nomear o novo produto/feature com identificador próprio e estável. O nome não precisa conter o SaaS de referência. Lacunas sobre o concorrente podem permanecer sem bloquear decisões próprias, quando não forem necessárias à aceitação da nova solução.

O `Next Step` do Brainstorm permanece exatamente o canônico da dependência. Depois de salvar e concluir seu gate, o pedido do ciclo completo permite carregar Define e continuar, sem uma pergunta genérica para autorizar a transição. Respeitar a pausa se o usuário pediu uma fase isolada ou se uma resposta/validação está pendente.

## Entrada do Define

Ler o Brainstorm final salvo inteiro. O relatório do SaaS é fonte de contexto; requisitos precisam derivar das decisões validadas no Brainstorm ou das clarificações do usuário nesta fase. Não fazer uma segunda descoberta geral nem preencher escopo para atingir clareza artificialmente.

No contrato disponível: molde `DEFINE_TEMPLATE.md` (no lugar que a dependência indicar), critérios observáveis, EARS, varredura de nove categorias de ambiguidades, Clarity Score de pelo menos 12/15, zero bloqueios e exatamente um Verify Gate válido. Pontuação não substitui esses requisitos.

Se ainda não há implementação/comando real, não fabricar `npm test`, `pytest` ou outro comando apenas plausível. Fazer a clarificação prevista. Sem resolução, salvar `Needs Clarification`; não mudar para `manual-ux` por conveniência e não emitir o encerramento de documento pronto. A criação de uma solução nova pode terminar legitimamente em rascunho nessa situação.

Rastreabilidade no Define: referenciar decisões do Brainstorm e, quando útil, achados F/E em critérios e clarificações já existentes. Uma mudança posterior do usuário prevalece sobre decisão anterior, com atualização das seções afetadas e registro em Clarifications.

Executar o script real de validação da dependência quando existir e puder ser executado; resolver a raiz corretamente. Sua aprovação estrutural não prova a semântica ou a existência/eficácia do comando de aceitação.

O documento final pronto termina com o próximo passo canônico da dependência. Atualizar o estado no relatório de engenharia reversa, sem acrescentar ações depois da seção final canônica do DEFINE. Não executar Design, UX review, Build ou Release neste ciclo, nem uma revisão de governança por conta própria; o passo de governança que a `sdd-define` instalada conduz dentro dela faz parte do Define e não é pulado; reconhecer as instruções do projeto para o handoff posterior sem modificar seus artefatos.

## Arquivos e mudanças

As três saídas ficam lado a lado. Com `sdd/config.yaml` no projeto, gravar em `sdd/features/`. Sem ele, gravar em `sdd/` na raiz. `.claude/sdd/` só quando ela já existe e não há `sdd/config.yaml`. Se não houver filesystem, fornecer Markdown completo com nome indicado, sem alegar que salvou.

Evitar um quarto documento de estado: manter retomada no levantamento e registros canônicos de decisões/revisões nos documentos SDD. Não renomear um ciclo em andamento silenciosamente. Antes de alterar material existente, ler e preservar as partes válidas e o histórico.
