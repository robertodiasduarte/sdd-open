# BUILD REPORT: F25 Skills duplicadas — alerta e limpeza com autorização

> A `sdd-checar-ambiente` avisa (⚠️) quando o mesmo agente lê a mesma skill do SDD em dois lugares, com caminho, versão,
> origem e qual roda; o `--duplicadas` mostra o plano sem mudar nada; o `--limpar <assinatura>` aplica só o plano
> mostrado, com lixeira conferida por hash, saída pelo `npx skills remove` protegendo a outra cópia e um `desfazer.sh`.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F25_SKILLS_DUPLICADAS |
| **Date** | 2026-11-17 |
| **Author** | build-agent (pelo `sdd-drive`: 11 executores frescos, um por tarefa) |
| **DEFINE** | [DEFINE_F25_SKILLS_DUPLICADAS.md](../features/DEFINE_F25_SKILLS_DUPLICADAS.md) (rev. 1.1) |
| **DESIGN** | [DESIGN_F25_SKILLS_DUPLICADAS.md](../features/DESIGN_F25_SKILLS_DUPLICADAS.md) (rev. 1.2) |
| **Status** | ✅ Complete — Verify Gate verde em `2fbc153` (rodada 3 do drive) e, depois do rebase na v2.21.0 e das 6 rodadas da revisão do código, em `c854f81` |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 11/11 linhas do manifest (10 do DESIGN 1.0 e a 11ª, do raio de impacto, no CORRIGIR da rodada 2) |
| **Files Created** | 2 (`scripts/duplicadas.sh`, `tests/test_f25_skills_duplicadas.py`) |
| **Lines of Code** | `git diff --stat 017f09a..2fbc153`: 11 arquivos, +1.327 / −19 |
| **Build Time** | 2026-11-17, do `iniciar` do drive ao gate verde da rodada 3 |
| **Tests Passing** | 2.540 de 2.540 (4 pulados) no Verify Gate final em `c854f81` (`VERIFY-GATE-c854f81.log`); 49 no módulo da F25, 21 deles da revisão do código, cada um vermelho antes (`REVISAO1/2/3/5/6-VERMELHO.log`) |
| **Agents Used** | 0 especialistas; 11 executores frescos e 1 avaliador fresco |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 11 linhas de manifest acopladas (biblioteca, modos, textos, testes de outros módulos) |
| Recomendação | `sdd-drive` (pedido do Roberto): uma tarefa por sessão nova, aplicando o protótipo validado no DESIGN |
| Decisão do usuário | drive, 2026-11-17 (pedido da sessão: "sdd-drive com o DEFINE … até pronto para publicar") |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-17 sobre `017f09a` (a mesma do DESIGN, `## Landmines aplicáveis`).

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| gate que confere fiação | LM-001 | ✔ tratado | o teste roda o `checar.sh` dos dois lados; mutante sem a proteção da outra cópia derrubado no teste nomeado (`MUTANTE-SEM-PROTECAO.log`) |
| asserção sem baseline | LM-002 | ✔ tratado | o módulo da F25 contra a árvore de `017f09a`: 29 falhas e 1 erro (`BASELINE-VERMELHO.log`) |
| review sobre diff vazio | LM-003 | ✔ tratado | 1 commit por tarefa; o avaliador provou por execução |
| gate sem `.git` | LM-006 | ✔ tratado | o gate roda de `git archive HEAD`; os testes montam o próprio repositório |
| `subprocess` no Windows | LM-014 · LM-029 | ✔ tratado | `encoding="utf-8"` em todo `subprocess`; o `desfazer` do teste usa o `BASH` do módulo |
| caminho do Windows | LM-017 | ✔ tratado | `dup_hash` por argumento relativo (Decision 12) |
| `[exit=]` no zsh | LM-018 | ✔ tratado | os logs AT-*, baseline e mutante saem de um script em `bash` com `rc=$?` |
| texto que só vale com o `init` | LM-035 | ✔ tratado | `test_gerar_starter` verde no gate (o rascunho com `` `sync` `` reprovou no protótipo) |
| arquivo novo fora do MANIFEST | LM-037 | ✔ tratado | tarefa 10; `publish-gate` verde na rodada 2 e na 3 |
| teto da SKILL.md | LM-038 | ✔ tratado | 330 linhas |

---

## Candidatos ao playbook

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `env -i` `HOME` `node` `homedir` `npx`
regra: Com `env -i`, a pasta pessoal deixa de ser variável exportada: um `HOME=<teste>` dentro do script vale só para o shell, e o `node` de um CLI chamado por ele cai na pasta pessoal REAL do sistema (os.homedir). Na F25, um `npx skills remove -g` de teste teria apagado skills do HOME real; o classificador barrou. **Do instead:** passe `HOME=<pasta de teste>` na linha de cada comando (nunca só dentro do script) e, no programa que chama o CLI, `HOME="${HOME}" cli …`; todo invólucro de teste do CLI recusa (exit 99) HOME fora da pasta de teste.
evidencia: sdd/features/DESIGN_F25_SKILLS_DUPLICADAS.md (Decision 9)
ficha: —
mordeu_antes: —
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `publish-gate` `undeclared file` `sdd-drive` `COMMITAR` `documento`
regra: O `sdd-drive` pede para commitar `.sh`, `.py` e `.diff` dentro de `sdd/reports/` (contam como código), e o `publish-gate` reprova qualquer arquivo commitado fora do `MANIFEST.txt`, inclusive DEFINE e DESIGN: na F25, commitar os documentos na branch de código custou uma rodada do drive (`undeclared file` ×16). **Do instead:** documentos da frente ficam fora da branch de código (vão à branch de documentos na publicação); material de apoio com código dentro de `sdd/reports/` leva `.txt` no nome.
evidencia: sdd/reports/evidence/F25_SKILLS_DUPLICADAS/DRIVE-gate-r1.log
ficha: —
mordeu_antes: LM-037
>>>
```

```text
<<<CANDIDATO_PLAYBOOK
secao: Reviews / harness
sup: `test_decisoes_lint` `pergunta(s) em` `como-falar` `[D1`
regra: O `test_decisoes_lint` fixa quantas perguntas de decisão o pacote tem ("34 pergunta(s) em 29 arquivo(s)"); um exemplo novo com pergunta num `references/como-falar.md` derruba a suíte inteira e só aparece no gate (na F25, a rodada 2 do drive). **Do instead:** ao acrescentar uma pergunta `[Dn · …]` ou `[auto · de rotina]` a uma skill, rode `python3 -B -m unittest discover -s tests -p 'test_decisoes_lint.py'` antes do gate e suba o contador no mesmo commit.
evidencia: sdd/reports/evidence/F25_SKILLS_DUPLICADAS/DRIVE-gate-r2.log
ficha: —
mordeu_antes: —
>>>
```

---

## Drift detectado

| Item | DESIGN | Código | Ação |
|---|---|---|---|
| manifest | 10 linhas (1.0) | 11 arquivos | DESIGN 1.2 ganhou a tarefa 11 (`test_decisoes_lint.py`) no CORRIGIR da rodada 2 |
| protótipo | `prototipo/*.diff`, `*.sh`, `*.py` | renomeados com `.txt` | DESIGN 1.1 (o drive conta `.sh`/`.py`/`.diff` em `sdd/reports/` como código) |

Nenhum outro drift: os 10 arquivos das tarefas 1 a 10 são o protótipo aplicado (`cmp` e `git apply` limpos, conferidos por cada executor).

---

## Files Created

| Arquivo | Linhas | Propósito |
|---|---|---|
| `.agents/skills/sdd-checar-ambiente/scripts/duplicadas.sh` | 562 | varredura, grupos, plano, assinatura, limpeza protegida e `desfazer.sh` |
| `tests/test_f25_skills_duplicadas.py` | 630 | AT-001 a AT-010 (28 testes) |

Modificados: `checar.sh`, `SKILL.md` (v1.6.0), `references/como-falar.md`, `tests/test_checar.py`, `tests/test_bash32.py`,
`tests/test_f16_textos.py`, `tests/test_matriz_new_session.py`, `tests/test_decisoes_lint.py`, `MANIFEST.txt`.

---

## Verification Results

### Lint · Typecheck

N.A. (sem `{{LINT_CMD}}`/`{{TYPECHECK_CMD}}` no projeto). `skill-lint.py --conversa` verde na `SKILL.md` (tarefas 3 e 4);
`design-lint.py` verde no DESIGN 1.2.

### Testes

| Rodada | Resultado | Log |
|---|---|---|
| 1 | 194 testes nomeados OK; `publish-gate` vermelho (16 documentos commitados na branch de código) | `DRIVE-gate-r1.log` |
| 2 | `publish-gate` verde; suíte 2.463 com 1 falha (`test_decisoes_lint`: 35 perguntas, não 34) | `DRIVE-gate-r2.log` |
| 3 | ✅ verde: 194 nomeados, `publish-gate`, suíte 2.463 OK (4 pulados) | `DRIVE-gate-r3.log` |

Tempo do diagnóstico normal com 18 duplicatas reais (HOME só lido, DESIGN Decision 10): 0,31 a 0,35 s a mais (meta ≤ 1 s).

---

## Segurança

N.A. no DEFINE (nenhum gatilho). Requisitos de engenharia cumpridos: assinatura + `[D1]` antes de remover (AT-008,
AT-010); `desfazer.sh` com `%q` testado com espaço, aspas e `$` (AT-009); `HOME` explícito no npx; invólucros de teste
com trava de HOME (exit 99). O HOME real foi conferido intacto (15/18/7 skills, horários anteriores à sessão, sem
`~/.sdd-lixeira`) depois do comando barrado pelo classificador.

---

## Issues Encountered

| Issue | Resolução |
|---|---|
| `npx skills remove -g` apaga a cópia manual de mesmo nome (EXP-3) — contradizia a DC3 | pergunta `[D2]` ao Roberto: "Proteger e usar o npx" (Decision 9) |
| comando com `env -i` faria o CLI agir no HOME real | barrado pelo classificador antes de rodar; `HOME` explícito e trava nos testes |
| documentos commitados na branch de código (rodada 1) | commit de documentos desfeito (local, nunca enviado); protótipo com `.txt` |
| contador do `test_decisoes_lint` (rodada 2) | tarefa 11 |
| A1 (avaliador, baixa): se o npx tocasse uma pasta fora das 2 protegidas, a mensagem diria "Nada foi tirado" sem dizer qual pasta foi tocada (com o CLI 1.9.0 medido, não acontece: o `remove -g` não toca projeto nem `~/.codex`) | não corrigido nesta frente: mexer no código depois do gate verde da 3ª e última rodada reabriria o gate sem rodada; vira pendência ✨ na ficha (dizer a pasta tocada; não dizer "Nada foi tirado" nesse ramo) |
| A2 e A3 (avaliador, cosméticos): "Para desfazer" impresso quando nada saiu; dois parênteses seguidos na recomendação do atalho | idem, pendência ✨ junto com a A1 |
| A4 (avaliador, processo): os `AVAL-*.log` e os `AT-*.log` têm caminhos absolutos da máquina | os documentos não vão à branch de código; ao levá-los à branch de documentos (repositório público), a release tira os caminhos pessoais |
| revisão do código (release, FASE 0a item 8), 6 rodadas, ledger `sdd/reviews/LEDGER_REVISAO_F25_SKILLS_DUPLICADAS.md` | rodadas 1 a 3 (laço, PRONTO na 3ª, 0 graves): 17 achados, 14 aplicados com teste vermelho antes, 3 rebatidos com prova (o `checar.sh` não tem `trap`; o `relatorio()` junta o balde antes de decidir "Pronto"); rodadas 4 a 6 de confirmação da versão final: bordas de falha no meio do `--limpar`, todas aplicadas com teste; a 4ª e a 5ª com o OK do Roberto (D4), a 7ª dispensada por ele; A1 e A3 do avaliador corrigidos na rodada 1 |
| raio de impacto da release: o guia do aluno e o README do starter diziam que a skill "só lê, nada a perguntar" | `132643a`: dizem que ela só lê, exceto a limpeza das duplicadas, a pedido e com pergunta |
| rebase: a `main` andou para a v2.21.0 (F23 B2) durante a frente | rebase limpo (interseção só no `MANIFEST.txt`); a F25 sobe como v2.22.0 |
| o avaliador rodou 1 vez `codex --version` com o HOME real (só lê a versão; o Codex grava em `~/.codex/tmp`) | registrado; nenhuma pasta de skills do HOME real foi tocada |

---

## Deviations from Design

Só as do quadro de drift (DESIGN 1.1 e 1.2), as duas registradas no Revision History do DESIGN.

---

## Blockers (if any)

Nenhum.

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (a skill `sdd-checar-ambiente` e os testes dela)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)
**Veredito do avaliador (C1):** PASS — `sdd/reviews/AVALIACAO_F25_SKILLS_DUPLICADAS_20261117-1222.md` (ciclo 1; 10 de 10 ATs por execução, sondas próprias com HOME temporário, gate refeito: 2.463 OK; 4 achados baixos/cosméticos, nenhum bloqueante)

---

## Acceptance Test Verification

| AT | Critério | Passou | Evidência |
|----|----------|--------|-----------|
| AT-001 | Claude Code: 2 pastas, roda a global; `CLAUDE_CONFIG_DIR`; não lê `.agents` | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-001.log` · `EXP-1-CLAUDE-PRECEDENCIA.log` |
| AT-002 | Codex: 4 pastas, lista todas; `CODEX_HOME`; medição refeita sem modelo | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-002.log` · `EXP-2-CODEX-PASTAS.log` |
| AT-003 | registro do npx, pasta gerenciada, atalho conta como uma cópia | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-003.log` · `EXP-3-NPX.log` |
| AT-004 | tabela 2.1: 3 itens ⚠️ entre dado e o resto, árvore intacta; >3 ⇒ 1 item | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-004.log` |
| AT-005 | par gerado, agentes diferentes, atalho e terceiro não são duplicata | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-005.log` |
| AT-006 | plano só lê, global × projeto, aviso "todos os projetos", assinatura estável | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-006.log` |
| AT-007 | matriz da escolha (9 casos) | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-007.log` |
| AT-008 | sem/errada/plano mudado/sem npx/sem lixeira ⇒ ≠ 0, nada muda | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-008.log` |
| AT-009 | lixeira por hash, npx protegido, desfazer devolve a árvore; CLI de verdade | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-009.log` |
| AT-010 | exceção única, etapa 3, D1; `--frente` 0; bash 3.2; starter gerado | true | `sdd/reports/evidence/F25_SKILLS_DUPLICADAS/AT-010.log` |

---

## Final Status

✅ Complete. Verify Gate verde em `c854f81` (2.540 testes, sobre a v2.21.0); 10 de 10 ATs com evidência; baseline vermelho e mutante registrados; avaliador fresco PASS; revisão do código em 6 rodadas, sem achado aberto além das pendências do ledger da release.

---

## Next Step

**Ready for:** `/sdd-release F25 skills duplicadas` — com o OK do Roberto.
