# Histórico

## 1.1.0 — nov/2026

Entrada no sdd-open como 20ª skill, portada da 1.0.0 sem mudar o protocolo do escopo ER-SDD-001.

- Camada "Como falar com o aluno": linha de identificação, Status por etapa, seção no `SKILL.md` e
  `references/como-falar.md` com glossário e exemplos.
- Pasta de saída: com `sdd/config.yaml` no projeto, `sdd/features/`; sem ele, `sdd/` na raiz; `.claude/sdd/`
  só quando ela já existe e não há `sdd/config.yaml`. Antes, `.claude/sdd/` tinha preferência sempre que existia.
- Com `.agents/skills/sdd-engenharia-reversa-saas/` no projeto, o molde e o lint são lidos dessa pasta: a
  cópia gerada para cada agente tem cabeçalho, e um levantamento feito do molde copiado reprova no lint.
- Dependências citadas pelo nome técnico, `sdd-brainstorm` e `sdd-define`, com ou sem prefixo de plugin.
- Exemplo ilustrativo em domínio neutro ("um sistema de BPO financeiro"), sem nome de produto.
- Python 3.9 ou mais novo (a 1.0.0 declarava 3.10; os 18 testes do lint passam no 3.9).
- Pacote: saem `LICENSE.txt` (vale a licença MIT do pacote) e `VALIDACAO.md` (o que rodou em cada versão
  está no `manifest.json`); os testes do lint vão para a suíte do pacote.
- O texto canônico de recusa passa a ser dito inteiro, palavra por palavra: na 1ª série de execuções do
  cenário de acesso indevido, as 3 recusaram e só 1 usou a frase literal.
- Instrução embutida em página ou anexo: além de não seguir, a skill avisa o usuário e registra no
  levantamento. Numa execução do cenário, o agente não seguiu a instrução, mas também não contou que ela existia.
- `scripts/validate_reverse.py` e `assets/ENGENHARIA_REVERSA_TEMPLATE.md` não mudaram.

## 1.0.0 — 2026-11-09

- Criação sob o escopo ER-SDD-001 V1.
- Engenharia reversa funcional anterior ao Brainstorm, com pesquisa progressiva e continuidade com limites explícitos.
- Orquestração das dependências SDD instaladas, com preservação de seus templates e gates.
- Template próprio de investigação, retomada, validação estrutural e cenários de avaliação.

Implementação nova; não é boilerplate oficial nem certificação de integração com os frameworks.
