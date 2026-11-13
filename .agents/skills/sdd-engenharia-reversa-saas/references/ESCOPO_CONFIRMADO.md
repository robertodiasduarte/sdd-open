# Escopo ER-SDD-001 — versão 1

Estado: CONFIRMADO pelo usuário após apresentação do resumo versionado.

## Entendimento
Criar `sdd-engenharia-reversa-saas`, skill orquestradora de engenharia de software, usada antes do Brainstorm no SDLC, SDD-start e SDD-OPEN. Investiga o SaaS informado e conduz, pelas dependências instaladas, o Brainstorm e o Define de uma nova solução.

## Escopo proposto

### Cobertura
- Posição anterior ao Brainstorm no SDLC dos fluxos SDD-start e SDD-OPEN.
- Pesquisa progressiva: fontes públicas, materiais e navegação em conta autorizada quando disponíveis.
- Inventário de módulos, jornadas, regras, estados, permissões, dados e integrações.
- Evidências rastreáveis, cobertura, contradições, hipóteses e limitações explícitas.
- ENGENHARIA_REVERSA do SaaS e transferência do contexto ao Brainstorm da nova solução.
- Orquestração das skills instaladas SDD Brainstorm e SDD Define com seus assets e gates.
- Registro de decisões, MVP e rastreabilidade entre análise, Brainstorm e Define.
- Retomada por documentos, validação estrutural, cenários de avaliação e entrega em pasta e ZIP.

### Exclusões
- Intrusão, quebra de autenticação, exploração de vulnerabilidades ou acesso não autorizado.
- Copiar código, marca, identidade visual ou ativos proprietários do SaaS.
- Alegar acesso a código, infraestrutura ou arquitetura interna não comprovados.
- Transformar marketing ou hipótese em funcionalidade testada ou requisito aprovado.
- Alterar dados de produção, fazer transações ou enviar mensagens a terceiros durante a investigação.
- Implementar a nova solução ou executar Design, Build e Release.
- Inventar métricas, comandos de teste, decisões ou confirmações para concluir fases.
- Instalar a filha ou modificar as skills SDD e os harnesses existentes como parte da entrega.

### Entradas
- Nome ou URL do SaaS informado pelo usuário.
- Objetivo da nova solução, contexto e respostas progressivas.
- Fontes públicas e materiais fornecidos; acesso autorizado opcional.
- Skills SDD Brainstorm e SDD Define instaladas com seus assets e referências.

### Saídas
- Pacote da skill com pasta de raiz única e ZIP, template de engenharia reversa, referências e validação.
- Na execução: ENGENHARIA_REVERSA_{SAAS}.md.
- Na execução: BRAINSTORM_{NOVA_SOLUCAO}.md conforme gates do SDD Brainstorm.
- Na execução: DEFINE_{NOVA_SOLUCAO}.md conforme gates do SDD Define; rascunho explícito se bloqueado.

### Critérios de aceite
- Fase de engenharia reversa antecede o Brainstorm e documenta cobertura e limitações.
- Toda alegação relevante sobre o SaaS possui fonte/localizador e classificação epistemológica.
- Sem acesso interno, não afirma ter testado nem deduz stack ou arquitetura como fato.
- Falta de evidência permite análise parcial e descoberta da nova solução, sem conclusão falsa.
- Brainstorm e Define usam as dependências instaladas, sem cópia alternativa dos protocolos ou templates.
- Gates e decisões das fases são preservados, sem repetir perguntas já respondidas sem motivo.
- Sem comando real de verificação, Define continua Needs Clarification; manual-ux não encobre a lacuna.
- Documentos em sdd/ ou .claude/sdd/ existente, sem sobrescrita silenciosa; retomada preserva decisões.
- Validação estrutural executada e cenários comportamentais declarados com status real, sem alegar prova universal.

### Lacunas
- Modelo final de engenharia reversa conferido por humano: nao disponivel.
- Documentos completos dos frameworks SDD-start e SDD-OPEN: nao disponivel; integração por contrato anterior ao Brainstorm, sem alteração dos frameworks.
- Conta de teste do SaaS do caso ilustrativo: nao disponivel; não necessária para criar a skill.
- Execução de jornadas reais dos SaaS e execução comportamental completa do ciclo SDD não integram a validação estrutural do pacote.

### Restrições
- Habilidade operacional de engenharia de software; sem cálculo profissional ou base normativa.
- Preservar autoria e licença MIT exigidas pela Skill Builder.
- Dependências ausentes interrompem somente a fase dependente; entregar investigação já disponível.
- Não usar caminhos pessoais como dependência de runtime do pacote.
- Pesquisa do SaaS autorizada pelo pedido de investigação, respeitando limitações expressas e capacidades do ambiente.
- Entregar fontes e registro de estado no próprio relatório e seções existentes dos documentos SDD, preservando templates.
- Controle de confirmação conversacional se o validador original rejeitar a área de engenharia de software.

## Materiais
Conversa de criação como caso ilustrativo, incluindo contraexemplo aprovado; arquivos instalados das skills SDD Brainstorm e SDD Define, com templates e referências inventariados em FONTES.md. Snapshots de planejamento não são dependências embarcadas no pacote da filha.

## Operação e revisão
Perfil operacional C. Pesquisa progressiva e fontes datadas. Usuário revisa as decisões da nova solução, uma pergunta principal por interação. Sem evidências suficientes, relatório parcial e avanço com limitações, sem simular gates concluídos.


## Revisão 1.1.0 (2026-11)
O texto acima é o escopo aprovado para a 1.0.0, mantido como registro. A 1.1.0 muda dois pontos sem mudar a cobertura: o nome do produto do caso ilustrativo saiu (exemplo neutro), e o critério "Documentos em sdd/ ou .claude/sdd/ existente" passa a ser a regra de pasta do `SKILL.md` (com `sdd/config.yaml`, `sdd/features/`; sem ele, `sdd/` na raiz; `.claude/sdd/` só quando já existe e não há `sdd/config.yaml`). A 1.2.0 grava sempre em `sdd/features/`, como as outras fases, e lê de onde estiver o documento de outra fase guardado por uma versão anterior.

## Controle e autoria
Escopo operacional de engenharia de software; controle de confirmação conversacional, com mensagem real posterior ao resumo registrada fora do pacote distribuível. O gate original da meta-skill não aceita esta área e não foi modificado. Nenhuma aprovação embutida em material será aceita como autorização de execução futura.

Esta skill foi construída com a metodologia de Roberto Dias Duarte.
