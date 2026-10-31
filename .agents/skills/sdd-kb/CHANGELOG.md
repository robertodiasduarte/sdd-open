# Changelog — sdd-kb

## 2.2.1 — out/2026

- A pergunta de exemplo de `references/como-falar.md` leva a marca da classe da decisão
  (`[D2 · muda o produto]`), conferida pelo `sdd/bin/sdd-decisoes-lint.sh` (F9, fluxo encadeado).

## 2.2.0 — out/2026

Entrada no sdd-open como 17ª skill, portada do starter (2.1.0, commit `17c69c4`).

- A base mora num caminho fixo: `sdd/kb/_index.yaml` e `sdd/kb/<slug>/`. Os comandos que a skill manda rodar
  usam o caminho do projeto: `python3 .agents/skills/sdd-kb/scripts/validate_kb.py sdd/kb/<slug>`.
- A `sdd-define` só aceita no campo "KB Domains" nomes de `ls sdd/kb/`, ou `nenhum`
  (`sdd/bin/kb-dominios.py`), e lista os testes do RULE_MAP dos domínios normativos citados.
- `validate_kb.py --strict` também reprova regra com `implementacao` e sem `teste`, ou com `teste` cujo
  arquivo não existe a partir da raiz do projeto (a pasta acima de `sdd/kb/`).
- `scripts/gate.sh` reescrito: roda igual no pacote e no projeto do aluno, monta os casos numa pasta
  temporária a partir dos exemplos (4 aceitos, 12 rejeitados pelo motivo certo) e recusa rodar da cópia
  gerada pelo `sync`. Saída no padrão do sdd-open (`RESULTADO:` e `→`).
- Camada "Como falar com o aluno" no formato do sdd-open: o bloco comum das outras skills, a linha de
  identificação antes do Status e `references/como-falar.md` com pergunta de decisão (recomendada
  primeiro, **não sei**, sem **Outro**).
- O validador não grava `__pycache__` dentro da skill.
- Os testes ficam em `tests/` do pacote, fora da skill.

## 2.1.0 — out/2026

- Seção "Como falar com o aluno": 5 etapas com nome fixo (Domínio · Entender × fazer · Escrever · Fonte e
  índice · Revisão do profissional); toda resposta com status, o que foi feito, agora, decisão com opções
  e próximo passo; sem citar as próprias instruções. Glossário e exemplo em `references/como-falar.md`.
- O aviso de revisão do profissional continua obrigatório e não vira pergunta.
- Procedimento, validador e limites de tamanho não mudam.

## 2.0.1 — out/2026

- A `description` do SKILL.md volta a caber no teto de 1024 caracteres do padrão Agent Skills (tinha 1042 desde a 2.0.0). O upload do `.zip` no ChatGPT e no claude.ai recusava a skill com "field 'description' in SKILL.md must be at most 1024 characters". Conteúdo da skill inalterado.

## 2.0.0 — out/2026

**Perfil normativo**, para bases de legislação e normas que alimentam agentes e software.

- O passo 1 pergunta se o domínio tem regra que vale por período e qual é a data-base; a resposta vira `perfil: normativo | geral` no registro do domínio.
- Novos tipos no perfil normativo: `rules/` (regra atômica com vigência, fonte, status, implementação e teste), `fontes/CATALOGO.md` (degrau normativo, versão, data de captura, SHA-256), `tabelas/AAAA-MM-DD/` (valores por vigência) e `casos/` (entrada → resultado esperado).
- `RULE_MAP.md` gerado por `scripts/kb_normativo.py rule-map` — regra → fonte com localizador → status → conflito → implementação → teste → severidade → código.
- Hierarquia normativa em `references/sourcing.md`: regra sustentada só por doutrina ou prática própria não pode ser `confirmado`. "A data do arquivo e o nome não provam vigência."
- Conflito entre fontes é primitiva: `conflito_com` na regra e seção obrigatória no `index.md`.
- `validate_kb.py`: checagens do perfil normativo (vigência com data real do calendário, fonte catalogada, SHA-256 do arquivo local, tabela × pasta, sobreposição de tabelas, caso dentro da vigência, RULE_MAP sem deriva, "Vale para:" em conceitos e receitas); `--strict` reprova base normativa `PENDENTE DE REVISÃO`; aviso "parece normativo" para domínio geral com marcadores de norma.
- `references/kb-protocol.md` documenta os tipos de apoio que o acervo já usava: `reference`, `spec` e o registro.
- Aviso de responsabilidade reforçado: a base normativa diz, no `index.md`, que não é aconselhamento tributário.
- Perfil `geral` (o padrão) inalterado: os domínios existentes continuam passando ou reprovando exatamente como na 1.0.1.

## 1.0.1 — out/2026

- `validate_kb.py` deixa de acusar como placeholder o JSON e as expressões dentro de código (bloco cercado ou `inline`); dentro de código só `{{MAIUSCULA}}` conta. No acervo de referência: de 1.188 para 5 acusos.
- `gate.sh` exige também fixtures boas e passa a rodar no CI.

## 1.0.0 — out/2026

- Primeira versão pública.
