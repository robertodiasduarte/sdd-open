# Raio de impacto (0b) — F17_STARTER_GERADO, sobre 2be8f36

Um agente fresco por superfície, brief `.agents/skills/sdd-release/references/raio-de-impacto.md`, só os 5 campos.

## Superfície 2 — CATALOGO_GOVERNANCA (coluna "prova pós-build", valores sim/—, fecho do PROCEDIMENTO e do template)

```text
<<<RAIO
superficie: CATALOGO_GOVERNANCA.md — última coluna ("pós-build" → "prova pós-build"), valores G01–G20 (número|— → sim|—), fecho de PROCEDIMENTO.md e GOVERNANCA_REVIEW_TEMPLATE.md
consumidor: sdd/bin/governanca-bloco.py:28-29,57-66 · ok — só lê os títulos `### Gnn — ` de `## Lacunas`
consumidor: tests/test_governanca_bloco.py:17-39 · ok
consumidor: .agents/skills/sdd-governanca/references/revisor.md:25-26,33-34 · ok — as linhas "à letra" são outras
consumidor: tests/test_f17_textos.py:25-46 · ok
consumidor: tests/test_f15_slots_textos.py:222-223 · ok — outra lista de arquivos
consumidor: .agents/skills/sdd-governanca/evals/cases.json · ok
consumidor: .agents/skills/sdd-governanca/references/PROCEDIMENTO.md:61-72 · ok — usa porte_min, não a coluna
consumidor: .agents/skills/sdd-build/references/aplicar-migration.md:174-197 · ok — `pg_trigger` coberto pela regra "um select por objeto" (sem exemplo próprio)
consumidor: .agents/skills/sdd-build/SKILL.md:178-184 · ok
consumidor: tests/test_gerar_starter.py:21-22 · ok — a governança do starter fica congelada
consumidor: sdd/bin/{sdd-fluxo,sdd-drive,verify-gate,governanca-fronteira,playbook-curator,seguranca-varredura} · ok — nenhum lê o catálogo
invariante: INV-001 · ok
invariante: INV-002 · ok
>>>
```
Rodou 76 testes (test_f17_textos, test_governanca_bloco, test_f12_textos, test_governanca_gate, test_governanca_fronteira): verdes.

## Superfície 3 — seguranca-varredura.sh, comentado()

Só fichas de padrão sem a S11 passam por ela (S02, S04, S12, S14, S15, S16, todas `bloqueia: nao`; o teste
`test_seguranca_catalogo.py:45` trava isso): no pior caso, aviso a mais, nunca bloqueio. O pacote varrido com a versão de
origin/main e com a atual: mesma saída (exit 0 com a stack detectada; exit 1 com os mesmos 4 S14 "já existia" com todas as
fichas ligadas; diff vazio). 69 testes verdes.

```text
<<<RAIO
superficie: sdd/bin/seguranca-varredura.sh, comentado(linha, col, sql)
consumidor: sdd/bin/seguranca-varredura.sh:472 · ok — único chamador; só fichas que não bloqueiam
consumidor: .agents/skills/sdd-release/SKILL.md:142 (0a item 10) · ok — mesmo resultado no pacote
consumidor: .agents/skills/sdd-release/references/seguranca.md:8 · ok
consumidor: .agents/skills/sdd-release/SKILL.md:157 (--checklist) · ok — sai antes da varredura
consumidor: bin/sdd-open.sh:422 (--agents) · ok — sai antes
consumidor: .agents/skills/sdd-build/SKILL.md:130 (--regras) · ok — sai antes
consumidor: tests/test_seguranca_varredura.py (casos novos e antigos) · ok
consumidor: tests/test_seguranca_catalogo.py:45 · ok
consumidor: docs/cli-conventions.md:71, docs/security.md:64 (EN/PT) · ok — dispensa não depende de comentado()
consumidor: sdd/bin/seguranca-varredura.sh:427 (ramo sql) · ok — sem efeito hoje (nenhuma ficha de padrão fora a S11 lê .sql)
consumidor: linha com dois comentários ("<!-- a --> <!-- eval( -->") · ok — aviso falso novo e menor, não bloqueia; a dispensa na linha resolve (aceito: o lado seguro é avisar)
invariante: INV-001 · ok
invariante: INV-002 · ok
>>>
```

## Superfície 4 — collect_evidence.py (inventário e "type")

Medido: no próprio Open, 252 itens em 3,96 s (origin/main) → 273 em 4,81 s (as 21 skills entram). 2 quebras em código não
modificado, consertadas com teste vermelho antes (`fix(sdd-auditoria-harness)`, sdd-auditoria-harness 1.2.1):
- `reference_needles` (collect_evidence.py:218) só procurava `/<nome>` para `/commands/`: o `.codex/prompts/x.md`, agora
  "comando", saía com 0 referências (falso NÃO UTILIZADO). Agora procura também `/prompts:<nome>`
  (`test_prompt_do_codex_chamado_como_prompts_nome_tem_referencia`).
- AUDIT_PROTOCOL §7 não dizia que a cópia gerada (`.claude/skills/X` com `sdd-open:generated`) espelha a fonte de propósito:
  risco de FUNDIR/APOSENTAR falso. Agora diz (`test_protocolo_diz_que_copia_gerada_nao_e_duplicata`).
Ficam como estavam (ruído anterior, mitigado pelo campo `note` e pelo §8): o needle `SKILL.md` dá a toda skill 19+
referências; caminhos relativos à skill viram candidatos de deriva; `endswith("AGENTS.md")` pegaria `SUBAGENTS.md` (0 no Open).
Invariantes: INV-001 e INV-002 não tocam o módulo.

## Superfície 1 — checar.sh (PRINCIPAL e o editor do resumo)

1 quebra de texto em código não modificado, consertada com teste vermelho antes (`fix(sdd-new-session)`):
`sdd-new-session/SKILL.md:108` chamava o `<b>` do pré-voo de "branch do remoto" e o `:240` o aceitava como "a do remoto"
para comparar com o slot; com o checar.sh preferindo o slot, a comparação era o slot contra ele mesmo e a regra "diverge
⇒ pare e pergunte" nunca disparava (slot `main` do modelo, origin com main e master, origin/HEAD em master). Agora a do
remoto vem só de `git remote show origin` (`test_a_do_remoto_nao_vem_do_pre_voo`).
Consumidores ok: checar.sh:515, :585, :602 (origin/<slot> existe por construção), :226 (aviso só no modo normal);
sdd-iniciar-repo/SKILL.md:353; bin/sdd-open.sh:863 (--segredo sai antes); a troca do starter (checar.sh:349 igual);
tests/test_checar.py (85), test_matriz_new_session (12), test_f16_textos (13).
Observações sem quebra: o resumo do checar não lê o slot `editor` do config (só o git config e o detectado), coerente com a
SKILL.md:192; config com CRLF faz o slot cair calado no comportamento antigo (não é regressão).
Invariantes: INV-001 e INV-002 não tocam o módulo.

## Síntese
4 superfícies, 3 quebras em código não modificado (todas consertadas com teste: 2 na auditoria, 1 na new-session), 0
invariante violada.
