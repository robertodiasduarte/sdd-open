# Avaliação do sdd-starter para incorporação no sdd-open

Data: 2026-10-29. Fontes: sdd-starter v1.5.15 (worktree feat/linguagem-aluno, commit 17c69c4) e sdd-open no commit 80d7887 de 24/10/2026. Objetivo: inventariar tudo que o starter faz bem, dizer o que o open já tem, e planejar a incorporação, inclusive a camada "Como falar com o aluno".

## Veredito em uma linha

O starter está na frente em quatro coisas: a camada de conversa, o terreno antes da spec (ambiente, dado de cliente, repositório), a disciplina de manutenção (versão, testes, release) e a migration de banco. O open está na frente no mecanismo (gate com estados, evidência, avaliador fresco, playbook, release com veredito). Nada do starter exige abrandar o open; tudo entra como camada ou como skill nova.

## 1. Componente por componente

| # | Componente do starter | O que faz bem | Já no open? | Entra no open como |
|---|---|---|---|---|
| 1 | Camada "Como falar com o aluno" (10 skills) | Etapas nomeadas, 5 partes fixas, glossário na 1ª vez, decisão com opções e efeito, parada com passos, nunca saída crua | Parcial: banner, RESUMO_ETAPA | Seção em cada skill + references/como-falar.md (seção 2) |
| 2 | sdd-checar-ambiente 1.2.0 | checar.sh de 446 linhas, só leitura, ordena por consequência, cada achado com o comando exato; pasta na nuvem, 4 casos de "não é repositório", identidade, remoto com teto de 10 s sem pedir senha, janela de login do editor, worktree órfã e integrada-mas-aberta, dependências, segredo já no histórico, repositório público; `--frente`; 53 testes sem rede | Não: doctor confere bash, git, python e adaptadores | Skill + `doctor --repo` que chama o mesmo script |
| 3 | sdd-higiene-dado 1.1.0 | pre-commit de 120 linhas: CPF/CNPJ com dígito verificador, .env, pfx/p12/pem com chave privada, planilha nova; não instala por cima de husky/lefthook/hooksPath; desinstala só o próprio; 28 testes; evals com controle negativo; manifest com "o que ainda não prova" | Não: landmines só na release, 3 regras genéricas | Skill + regras no landmines_cmd + padrões CPF/CNPJ no publish-gate |
| 4 | sdd-iniciar-repo 1.1.0 | 4 decisões do aluno; retomável por evidência do git; inventário sinaliza senha, certificado, planilha, >50 MB e o que já passou pelo histórico; "senha no histórico ⇒ não publique"; GitHub privado | Não: init exige git e para | Pré-passo opcional do init |
| 5 | sdd-new-session 1.3.0 | Pré-voo antes de criar; matriz de 12 achados traduzidos; descobre e grava sdd/ambiente.md (branch principal, cenário de branching com evidência, pasta das frentes, editor, preparação, arquivos locais, testes, sintaxe); "não pergunte o que dá para descobrir" | Parcial: 1.0.0 tem Passo 0 e slots do config preenchidos à mão | Descoberta que preenche os slots do config.yaml; matriz de achados |
| 6 | sdd-release 1.3.0, Fase 2 | Um bloco só, campos afirmados pela skill: O que sobe em palavras, O que muda em produção, O push publica sozinho?, O deploy espera os testes? (lido dos workflows; `continue-on-error` conta como não), Banco, Verificações; "verificação ausente dita como ausente"; nunca para duas vezes | Parcial: um OK, veredito, ledger; sem o bloco | Moldura do momento do "go" |
| 7 | sdd-build, references/aplicar-migration.md | Descobre ferramenta, projeto (nome E ref) e tipo de banco; para na divergência; exit 0 não é prova; prova por leitura; um passo por vez; `db reset` apaga tudo | Não: layers.sql e drift, sem procedimento | Referência + seção "Migrations aplicadas" no BUILD_REPORT + regra no report-lint |
| 8 | Validadores validate_define/design/build_report/handoff + gate.sh | Define: EARS, kinds, threshold numérico em eval, manual-ux com cmd e fallback, LLM Prompts literal. Design: manifest acíclico, Total Files bate, inventário LLM cruza com manifest, rastreabilidade. Handoff: ficha, placeholder, "como discutimos". gate.sh: o validador tem de aceitar o exemplo E rejeitar fixtures ruins | Parcial: verify-gate --print, report-lint, skill-lint | design-lint.py e handoff-lint.py em sdd/bin; gate.sh como padrão de teste |
| 9 | sdd-kb 2.1.0 | Conceitos × receitas, limites de tamanho, índice; perfil normativo com vigência, SHA-256 da fonte, conflitos e RULE_MAP regra → fonte → implementação → teste; revisão do profissional obrigatória | Não | Skill nova; RULE_MAP aponta o teste que o Verify Gate roda |
| 10 | ux-review-builder 1.4.0 | Entrevista sem vocabulário de UX; gera UX_STANDARD, skill ux-review do projeto e template; validador do bundle | Parcial: sdd-ux-review genérica com lentes | Entrevista de público e referências como entrada opcional da sdd-ux-review |
| 11 | Versão por skill | metadata.version e updated, linha de identificação na 1ª resposta com link da release, CHANGELOG, check-versions.py com 5 checagens, bump obrigatório no CI contra a última tag | Parcial: version no frontmatter, sem gate | check-versions no publish-gate; linha de identificação |
| 12 | Testes | 144 funções em 6 suítes; sem rede: GitHub falso em HTTP local, remotos bare, GIT_CONFIG_GLOBAL vazio | Não: 0 testes unitários | tests/ por script; step no CI |
| 13 | Auto-release | 2 jobs: testes só leitura, publicação com write e needs; tag por for-each-ref; zips + SHA256SUMS; comentários registram por que o desenho é assim | Não: nenhuma Release | Workflow equivalente |
| 14 | publish-check | CPF, telefone, e-mail pessoal, chaves, JWT, AWS; checa a seção do aluno | Parcial: gitleaks + padrões genéricos | Padrões de PII brasileira; checagem da seção |
| 15 | "Por que cada regra existe (não apague sem ler)" | Memória institucional dentro da skill, em new-session, release e iniciar-repo | Parcial: playbook cobre o projeto, não a skill | Seção nas skills portadas e nas de fase |
| 16 | Docs | Quickstart com "valide antes de seguir" e tabela onde roda → ferramenta; guia do aluno (494 linhas, sem commit); workflow | Parcial: quickstart por agente | Guia do aluno adaptado; regra do método no quickstart |
| 17 | agents/openai.yaml e manifest.json | Display name e prompt padrão para plataformas OpenAI; manifest com pending e o que não prova | Não | Opcional; manifest vale como contrato de honestidade |

O que o starter faz pior e não deve ir: gate sem runner e sem estados; pasta sdd/ plana; SKILL.md de até 496 linhas; links para "SpecGate", nome abandonado.

## 2. A camada "Como falar com o aluno"

### Anatomia

Os dez itens comuns, fixados no DEFINE_LINGUAGEM_ALUNO e presentes nas 10 skills:

1. Tabela de etapas com nome fixo, mapeando os passos da skill.
2. Cinco partes por resposta, nesta ordem, pulando a vazia: Status · O que foi feito · Agora: etapa N, nome · Sua decisão · Próximo passo.
3. Status com ✅ ▶️ ⬜ ⏸️ ➖; ✅ é concluída, não visitada; ao revisitar, o motivo vai em Agora.
4. Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
5. Saída de comando nunca crua: quantidades, nomes até 10 com "e mais N", o que preocupa.
6. Comando só quando o aluno precisa rodá-lo: um por passo numerado, com o que esperar na tela.
7. Sua decisão distingue autorização, pergunta em negrito com opções e efeito, de pergunta aberta, com como responder e a saída "não sei"; agrupadas vêm numeradas.
8. Resposta que não casa com opção: responder a dúvida e repetir as opções; a escolha fica registrada no "O que foi feito" seguinte.
9. Não citar as próprias instruções; dizer o motivo do aluno.
10. Parada com ⏸️: motivo em uma frase, onde a ação acontece, passos numerados com resultado esperado, o que não foi feito, e "Quando terminar, me peça de novo, eu continuo daqui."

Mais: antes de trabalho demorado, uma frase dizendo o que vai rodar e que não precisa responder; na build, contador Tarefas N/M a cada tarefa.

Dois níveis: Grupo 1, seção de 60 linhas com glossário dentro; Grupo 2, seção de 32 linhas mais references/como-falar.md com glossário, Status preenchido e um exemplo de resposta completa sem placeholder.

Garantias: publish-check reprova sem a seção ou sem o arquivo; só a camada de conversa muda, comandos e ordem dos passos idênticos, provado por diff por skill; evals revisadas uma a uma; SKILL.md até 500 linhas.

### Encaixe com o que o open já tem

| Parte do starter | Equivalente no open | Decisão proposta |
|---|---|---|
| Status intra-fase (etapas da skill) | Kanban do RESUMO_ETAPA, entre fases, derivado do filesystem | Os dois: Status abre cada resposta; kanban fecha a fase |
| Símbolos ✅ ▶️ ⬜ ⏸️ ➖ | ✅ 🏃 ⬜ ➖ | Unificar em ▶️ e adotar ⏸️; ➖ continua exigindo decisão registrada |
| Sua decisão com opções e "não sei" | "O que precisa de você", só se N ≥ 1, decidível sem abrir arquivo | Mesma regra de omissão; acrescentar opções e efeito |
| Banner `🧠 DEFINE (Fase 1)` | | Vira a primeira palavra do Status: `Define: ✅ 1 … · ▶️ 2 …` |
| Não repassar saída crua | Scripts já terminam em `RESULTADO:` + `→` | A skill traduz a linha RESULTADO, nunca cola |
| Glossário por skill | | Termos do open sem equivalente no starter: exit 0/2/3/4/5/64, landmine, ledger, drift, slot vazio, adaptador e sync, waiver, vendor, contexto fresco, iterate |
| Modo pedido por `--mode` | Flag ou pergunta | Flag continua; sem flag, pergunta com opções e "não sei" |
| 10 skills do starter | 13 do open, 3 em comum | Cobrir as 13, inclusive governanca, prompt-builder e auditoria, que o starter deixou para depois |

Risco a aceitar: o open mantém skills curtas. Usar o padrão do Grupo 2 em todas: seção curta mais referência.

## 3. Plano de incorporação

Decisões antes de começar:

1. Fonte canônica de governanca, auditoria-harness e prompt-builder: o open, que está mais novo nas três.
2. Camada de conversa ligada por padrão, sem toggle no config. Quem lê terminal perde nada; o toggle é YAGNI.
3. Símbolos e banner: definir antes de portar qualquer skill, para não portar duas vezes.
4. Descoberta de ambiente grava nos slots do config.yaml, não num sdd/ambiente.md paralelo.
5. Futuro do starter: depois disto, ele vira a distribuição do open para agentes sem sistema de arquivos. Gerar os zips a partir da fonte do open encerra a divergência.

Frentes, em ordem:

| Frente | Conteúdo | Gate |
|---|---|---|
| F1 Manutenção | Testes unitários dos scripts; check-versions e linha de identificação; auto-release com SHA256SUMS; design-lint e handoff-lint com gate.sh; padrões de PII no publish-gate; doctor com segredo no histórico | publish-gate.yml verde com os steps novos |
| F2 Terreno | checar-ambiente, higiene-dado, iniciar-repo portadas com seus testes e com a seção do aluno já ajustada aos símbolos; new-session com pré-voo, matriz e descoberta dos slots | testes das 3 suítes + fixtures do gate |
| F3 Build e Release | aplicar-migration e seção Migrations aplicadas com regra no report-lint; bloco da Fase 2 no momento do go, com "o deploy espera os testes?" | report-lint reprova migration sem prova; fixture de workflow com continue-on-error |
| F4 Conversa | Seção e como-falar.md nas 13 skills; glossário do open; skill-lint confere a seção; diff por skill prova que comandos não mudaram | skill-lint + diff review no BUILD_REPORT |
| F5 Conhecimento | sdd-kb com validate_kb e gate.sh; entrevista do ux-review-builder como entrada da sdd-ux-review | gate.sh da KB |
| F6 Docs | Quickstart com "valide antes de seguir"; guia do aluno adaptado ao open; "Por que cada regra existe" nas skills de fase | publish-gate |

Ordem: F1 → F2 → F3 → F4 → F5 → F6. F2 e F3 antes de F4 porque as skills portadas já chegam com a seção do aluno; F4 cobre só as nativas do open.

**Atualização 2026-10-29 (depois da F3, `v2.2.3`):** F4–F6 foram cruzadas com o plano do porte do SDD privado (ondas W0–W5) em `sdd/features/PLANO_F4_F15_CONSOLIDADO.md` — sequência `W0 → F4 → F5 → F6 → F7…F14 → F15`, em que F7–F14 são as ondas W1–W5 do porte como frentes desta mesma família e F15 substitui o SDD privado pelo Open. O programa inteiro responde a 4 parâmetros fixados pelo Roberto (corrigir erros · manter o padrão agnóstico · incorporar o que o starter faz melhor · acabar com o SDD privado), na seção 0 do plano.
