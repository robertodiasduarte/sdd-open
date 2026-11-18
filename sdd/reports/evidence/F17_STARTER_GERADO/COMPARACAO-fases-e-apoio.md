# Comparação skill a skill, starter (v1.5.16 = origin/main a82c972) × Open (feat/f17 sobre v2.12.1) — fases e apoio

Agente em contexto novo, só leitura, 2026-11-12. Skills: sdd-auditoria-harness, sdd-prompt-builder, sdd-governanca,
sdd-brainstorm, sdd-handoff. Classes: (A) o Open cobre de outro jeito · (B) o Open trocou de propósito · (C) falta no Open
e vale trazer · (D) próprio do starter. ST = skill no starter; OP = skill no Open.

## Vale para as cinco
- (D) `agents/openai.yaml` existe nas 5 do starter e em nenhuma do Open.
- (D) O starter grava em `sdd/` plano; o Open em `sdd/features/`, `sdd/reviews/`, `sdd/handoffs/`.
- `sdd/templates/fragments/PERGUNTA_DECISAO.md` citado pelas 5 do Open: opcional, pode ir em references/.

## sdd-auditoria-harness
- (C) multi-motor: o starter lê AGENTS.md, `.agents/{skills,agents,scripts}`, `.codex/…`, `.agents/sdd` (ST/SKILL.md:4,20,32-42,89-92,121; ST/scripts/collect_evidence.py:71-99,146,165-185); o Open só `CLAUDE.md` e `.claude/` (OP/scripts/collect_evidence.py:73-81,146-154). **Conferido no código em 2026-11-12.**
- (C) aviso de precedência CLAUDE.md × AGENTS.md (ST/SKILL.md:94-102); (incerto) a afirmação de versão do Claude Code não foi conferida.
- (C) índice `sdd/_index.md` (ST/SKILL.md:91) além de `.claude/sdd/_index.md`.
- Dependência fora da pasta: só o fragmento PERGUNTA_DECISAO (opcional).

## sdd-prompt-builder
- (C) detecção de drift sem script, pelos sinais do código (ST/references/sdd-integration.md:41-55); o Open exige `sdd/bin/prompt-drift-scan.sh` e o slot `prompts.wrapper_pattern` (OP/references/sdd-integration.md:48-60).
- (C) linha `loop` sem skill específica (ST :76); o Open aponta `sdd-loop-builder` (OP :81).
- (B) "chamada pelas fases Design/Build" → no Open o Design só inventaria (OP/references/sdd-integration.md:3).
- Dependências opcionais: LLM_PROMPTS_DESIGN.md (pode ir), prompt-drift-scan.sh, wrapper_pattern, sdd-loop-builder.

## sdd-governanca
- (C) a coluna pós-build cita a skill `rdd-audita-schema`, que não existe no Open (OP/references/CATALOGO_GOVERNANCA.md:21; OP/references/PROCEDIMENTO.md:124; OP/assets/GOVERNANCA_REVIEW_TEMPLATE.md:59); o starter manda provar por leitura no passo "Aplicar a migration" da sdd-build. **Conferido no código em 2026-11-12.**
- (C) prova por script só quando há Verify Gate por comando (ST/SKILL.md:51-61); o Open torna o script obrigatório (OP/SKILL.md:77-92,119).
- (C) "Onde entregar" (chat × agente, ST/SKILL.md:73-78); (C) "Quando não usar" (ST :45-49); (C) exceção "mudar o catálogo" e texto canônico de recusa (ST :95-108).
- Essencial no texto do Open e ausente na web: psql + bloco verify_gate + `sdd/tests/governanca/`; `compatibility` diz bash e git.

## sdd-brainstorm
- (C) funciona sem acesso ao projeto, entrega o Markdown no chat (ST/SKILL.md:54,115,211,268).
- (C) fato × inferência (Provided/Observed/Inferred; ST/SKILL.md:110-115).
- (C) não fabricar: YAGNI com zero cortes vale; métrica não quantificável vira TBD (ST :167,232,270).
- (C) exceções: pular perguntas, requisitos completos, quando não usar (ST :35-37,264-265).
- (C) não sobrescrever em silêncio um BRAINSTORM existente (ST :209).
- (C, baixo) escolha híbrida, campos das amostras, mudança de direção (protocolo :63-68,88).
- (C) o template do Open traz restos de outro domínio: `{pydantic, gcp, gemini}`, `Terraform/Terragrunt`, `src/ | functions/ | gen/ | deploy/` (sdd/templates/BRAINSTORM_TEMPLATE.md:29-31).
- (A) Perfil de risco: ganho do Open, o starter recebe.
- Essencial fora da pasta: BRAINSTORM_TEMPLATE.md (pode ir em assets/).

## sdd-handoff
- (C) sem filesystem, entrega no chat com 3 avisos; "nunca fingir que gravou" (ST/SKILL.md:153-159,203,225-228).
- (C) modos continuar e entregar; checklist que não bloqueia; "sem decisão, siga" (ST :75,87-94,136-145).
- (C) pendências 🐛/✨ com "nenhuma" declarado (ST :128-134; ST/scripts/validate_handoff.py:36,66-71).
- (C) exceções: "só me dá o prompt", várias features, nada concluído, critério de pronto vago (ST :200-206).
- (C) exemplo preenchido (ST/assets/HANDOFF_EXAMPLE.md); (C, baixo) no prompt de retomada, "decisões que não se reabrem" e "como fechar"; (C, baixo) frase vaga "aquele jeito que" no lint.
- Essencial fora da pasta: HANDOFF_TEMPLATE.md (pode ir); handoff-lint.py (exige a linha Verify Gate, que não existe na web).
