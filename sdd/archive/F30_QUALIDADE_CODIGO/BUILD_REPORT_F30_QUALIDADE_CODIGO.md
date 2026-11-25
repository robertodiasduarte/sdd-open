# BUILD REPORT: F30 — Qualidade do código gerado · fatia S3 (itens 5 e 8)

> Complexidade e duplicação do código novo, só aviso (`sdd/bin/metricas-diff.sh` e a seção `## Qualidade (avisos)`).
> O relatório da S2 está na versão de `fce8c61`; o da S1, na de `c4fa53c`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F30_QUALIDADE_CODIGO (fatia S3) |
| **Date** | 2026-11-25 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F30_QUALIDADE_CODIGO.md](../features/DEFINE_F30_QUALIDADE_CODIGO.md) (1.6) |
| **DESIGN** | [DESIGN_F30_QUALIDADE_CODIGO.md](../features/DESIGN_F30_QUALIDADE_CODIGO.md) (3.6) |
| **Status** | Complete |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 17/17 do File Manifest |
| **Files Created** | 4 (`metricas-diff.sh`, `metricas-do-diff.md`, 2 módulos de teste) |
| **Tests Passing** | os testes novos foram escritos antes do código e gravados vermelhos; a suíte inteira roda no Verify Gate |
| **Agents Used** | revisores externos (openrouter `qwen/qwen3.7-plus`, codex, auditor claude), avaliador de contexto fresco e 1 agente do raio de impacto |

---

## Landmines lidas no build

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| testes novos | LM-001, LM-002 | ✔ tratado | executam o script dos dois lados; antes vermelho por falta do comportamento; `test -f` no gate |
| revisão | LM-003 | ✔ tratado | commit antes de cada revisão |
| `subprocess`, Windows | LM-014, LM-029, LM-034, LM-042 | ✔ tratado | `Sandbox.roda`, `BASH`, `path_restrito` e constantes de `tests/apoio.py` |
| teto de tempo | LM-016 | ✔ tratado | nenhum teto por grupo de processos |
| saída graciosa | LM-017 | ✔ tratado | cada causa de "não medido" tem teste |
| config do git | LM-033 | ✔ tratado | `color.ui` só não bastava: `color.diff` prevalece (rodada 13); `--no-color` nas chamadas |
| starter | LM-035 | ✔ tratado | texto sem `sdd/bin/`; teste gera o starter |
| MANIFEST, teto de linhas | LM-037, LM-038 | ✔ tratado | 4 arquivos no mesmo commit; `SKILL.md` 382 e `MODO_WEB.md` 490 |
| perguntas | LM-044 | N.A. | nenhuma pergunta nova |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `grep` `emoji` `Git Bash` `pre-commit` `Windows`
regra: No Git Bash do Windows, `grep -E '🛑'` não casa a linha que tem o emoji: o script cai calado no caminho de reserva (no pre-commit, as últimas 5 linhas) e perde parte da mensagem. **Do instead:** procure emoji em saída com `LC_ALL=C grep -F`, e tenha um teste com mais linhas do que o caminho de reserva mostra.
evidencia: CI do PR #45, run 45597467098, fatia 6/16 (test_hooks.Hooks.test_report_staged_passa_pelo_report_lint); conserto em sdd/hooks/pre-commit
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `jscpd` `min-lines` `ferramenta externa` `padrão implícito` `falso nenhum`
regra: Ferramenta externa com filtro padrão não declarado dá falso "nenhum": o `jscpd` sem `--min-lines` perde todo trecho repetido de até 5 linhas, com qualquer `--min-tokens`. **Do instead:** ao medir com ferramenta de fora, passe todo filtro de forma explícita e meça os valores de fronteira com a ferramenta real antes de afirmar.
evidencia: sdd/reviews/LEDGER_REVISAO_F30_QUALIDADE_CODIGO.md (rodada 17, R2)
ficha: —
mordeu_antes: —
>>>
```

---

## Task Execution with Agent Attribution

| # | Task | Agent | Status | Notes |
|---|------|-------|--------|-------|
| 1–2 | `tests/test_f30_metricas.py`, `test_f30_textos_s3.py` | (direct) | ✅ | antes do código |
| 3 | `sdd/bin/metricas-diff.sh` | (direct) | ✅ | |
| 4 | `sdd/bin/report-lint.py` | (direct) | ✅ | classe `[qualidade]` |
| 5–11 | referência, skill, modo web, moldes, contrato, config, convenções | (direct) | ✅ | `sdd-build` 2.17.0 |
| 12–17 | versões fixas em 5 testes e `MANIFEST.txt` | (direct) | ✅ | |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 17 itens acoplados, um autor |
| Recomendação | default |
| Decisão do usuário | default, pela autorização de seguir as recomendações (2026-11-25) |
| Refatorar | ligado: 3 funções do próprio script passavam de 10 caminhos e foram divididas; hoje nenhuma passa |

---

## Drift detectado

- O molde do relatório do starter (`sdd-build/web/assets/BUILD_REPORT_TEMPLATE.md`) não tinha linha própria no manifest; entrou no item 8.
- `sdd/hooks/pre-commit` (fora do manifest): no Windows, a recusa perdia linhas do lint; o CI do PR acusou com a linha nova. Corrigido.
- `tests/test_hooks.py` e `tests/test_claude_adapter.py` (fora do manifest): o relatório de exemplo ganhou a seção.

---

## Files Created

| File | Verified | Notes |
|------|----------|-------|
| `sdd/bin/metricas-diff.sh` | ✅ | |
| `.agents/skills/sdd-build/web/references/metricas-do-diff.md` | ✅ | vai ao starter |
| `tests/test_f30_metricas.py` · `tests/test_f30_textos_s3.py` | ✅ | |

---

## Verification Results

### Lint (`{{LINT_CMD}}`)

O pacote não tem `sdd/config.yaml`: `project.lint_cmd` e `project.typecheck_cmd` estão vazios.

lint: slot vazio

### Testes (`{{TEST_CMD}}`)

Ver o Verify Gate. A fixture do AT-017 roda também com `lizard` 1.26.1 e `jscpd` 5.4.3 reais (`evidence/F30_QUALIDADE_CODIGO/METRICAS_REAIS.log`); o CI não os instala e usa as ferramentas falsas, com a saída real gravada.

---

## Qualidade (avisos)

> Só o código novo ou alterado desde `origin/main` (fce8c61). Aviso: não reprova.

### Complexidade

- 81 funções medidas no diff, 1 acima do limite:
- `tests/test_f30_metricas.py:37-39` `par`: 6 parâmetros (limite 5)

### Duplicação

- nenhum aviso (9 de 9 arquivos do diff)

Medido com as ferramentas reais numa pasta temporária. As pastas do método (`sdd/`, `.agents/`) ficam fora da medição; o núcleo do `metricas-diff.sh`, medido à parte com o `lizard`, não tem função acima dos limites.

---

## Segurança

O script só lê o projeto: as ferramentas rodam numa cópia de `mktemp`, apagada por `trap`, sem a configuração do projeto; nada é instalado e o `npx` não é usado. Nomes do projeto entram na seção sem quebra de linha nem crase. Itens recusados ou adiados no Define: nenhum.

---

## Raio de impacto (adiantado da release, 0b)

1 agente fresco, só leitura. 5 testes antigos quebrados em 3 arquivos (`test_hooks`, `test_claude_adapter`, `test_f17c_textos`), corrigidos; `sdd-drive`, `sdd-fluxo`, `slot.sh`, `init`, `upgrade`, starter e leitores do config ok; INV-001 e INV-002 intactos.

Riscos baixos que ficam: com `qualidade:` no config, a falta da seção reprova o relatório na release, e o texto da `sdd-release` não cita essa causa; título da seção é exato; um limite inválido impede gerar a seção até ser corrigido.

---

## Deviations from Design

| Deviation | Reason | Impact |
|-----------|--------|--------|
| A sabotagem do AT-019 teve o texto do trecho ajustado depois do código | a refatoração mudou a linha; a troca (`if False:`) e o que o teste acusa são os declarados | nenhum |
| `--raiz` em subpasta, cópia em UTF-8, `--min-lines 0` | revisões e avaliador (DESIGN 3.2 a 3.6) | mais casos medidos |

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS (sobre `814a3a5`, antes dos consertos das rodadas 12 a 19) · ciclos: 1 · achados: 1 MED e 9 leves; aplicados M1, L3, L4, L7, L8 e L9; L6 documentado; ficam L1 (nome com aspas derruba a complexidade, com "não medido" honesto), L2 (causa imprecisa com saída vazia) e L5 (seção só com `---` conta como preenchida) · `AVALIACAO_F30_QUALIDADE_CODIGO_20261125-0720.md`

---

## Acceptance Test Verification

| ID | Critério (EARS, resumido do DEFINE) | Antes | Resultado | Evidência |
|----|-------------------------------------|-------|-----------|-----------|
| AT-017 | When o `metricas-diff.sh` roda com uma função de complexidade 15 e um bloco duplicado no diff, shall imprimir a seção com os dois, sair 0 e deixar a árvore idêntica | `evidence/F30_QUALIDADE_CODIGO/AT-017.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-017.log` · `evidence/F30_QUALIDADE_CODIGO/METRICAS_REAIS.log` |
| AT-018 | If a ferramenta falta, falha ou devolve saída ilegível, then shall escrever `não medido` com a causa, sair 0 e nunca dizer "nenhum" | `evidence/F30_QUALIDADE_CODIGO/AT-018.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-018.log` · `evidence/F30_QUALIDADE_CODIGO/AT-018.sabotagem.log` |
| AT-019 | While a função ou o par não tem linha no diff, shall ficar fora da seção | `evidence/F30_QUALIDADE_CODIGO/AT-019.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-019.log` · `evidence/F30_QUALIDADE_CODIGO/AT-019.sabotagem.log` |
| AT-020 | Where há limite em `qualidade.*`, shall usá-lo; vazio, o padrão; inválido, 64 | `evidence/F30_QUALIDADE_CODIGO/AT-020.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-020.log` |
| AT-021 | When o `report-lint.py` confere o relatório, shall exigir a seção se o config tem `qualidade:`; sem o mapa, aviso | `evidence/F30_QUALIDADE_CODIGO/AT-021.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-021.log` · `evidence/F30_QUALIDADE_CODIGO/AT-021.sabotagem.log` |
| AT-022 | When o Build termina as tarefas, os textos, moldes, config e o starter shall levar as métricas | `evidence/F30_QUALIDADE_CODIGO/AT-022.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-022.log` |
| AT-023 | The system shall continue to aprovar relatórios sem a seção em projeto sem `qualidade:` e passar os checks | `evidence/F30_QUALIDADE_CODIGO/AT-023.antes.log` | true | `evidence/F30_QUALIDADE_CODIGO/AT-023.log` |

**Verify Gate (`bash sdd/bin/verify-gate.sh sdd/features/DEFINE_F30_QUALIDADE_CODIGO.md`):** exit 0 em `cd70bed` (`evidence/F30_QUALIDADE_CODIGO/GATE_S3_cd70bed.log`: suíte inteira, 2.947 testes, 7 pulados). Um gate em `ebd73d5` foi interrompido de propósito (a rodada 19 mudou o texto do guia).

---

## Advisor Ledger

Ledger completo em `sdd/reviews/LEDGER_REVISAO_F30_QUALIDADE_CODIGO.md` (seção S3).

| Rodada | Revisor | Achados | Decisão |
|---|---|---|---|
| D3 (DESIGN) | openrouter qwen | 3 MED (do auditor) | APLICADA |
| 11 | openrouter qwen | 2 MED (do auditor) | APLICADA |
| 12 | codex | 1 HIGH, 2 MED | APLICADA |
| 13 | codex | 3 MED | APLICADA |
| 14 | codex | 2 MED, 1 LOW | APLICADA |
| 15 | codex | 1 MED | APLICADA |
| 16 | codex | 1 MED | APLICADA |
| 17 | codex | 3 MED | APLICADA |
| 18 | codex | nenhum | — |
| 19 | codex | 1 MED | APLICADA |
| 20 | codex | 1 LOW | REBATIDA_ESCOPO (pendência na ficha); CONFERE |

`diversidade: vendor` em todas. Custo: US$ 10,44 (a do DESIGN e 10 do código). O script dispensou o 2º revisor por falta de superfície de risco; nenhuma dispensa à mão.

---

## Final Status

### Overall: ✅ COMPLETE

## Next Step

`sdd-release`
