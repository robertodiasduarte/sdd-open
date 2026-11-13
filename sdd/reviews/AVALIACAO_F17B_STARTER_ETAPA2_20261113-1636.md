# Avaliação de contexto novo — F17B_STARTER_ETAPA2, ciclo 2

> Bloco devolvido pelo avaliador (subagente em contexto novo, modo `veredito`, ciclo 2), sobre `1d8fc65`. Os achados 1 e
> 2 (baixos) foram consertados em `f9a0af1`; o 3 é recibo, no BUILD_REPORT.

<<<AVALIACAO
VEREDITO: PASS_PENDENTE_RECIBO

Avaliado: `1d8fc65`, em contexto fresco e só por execução. Montagem: `git archive HEAD` (`.agents/skills`, `sdd/templates`, `scripts/starter`, `scripts/gerar-starter.py`) num repositório temporário com a tag `v9.9.9`; starter clonado de `/Users/robertoduarte/rdd-public/sdd-starter` e posto em `checkout -B x v1.5.17` (`d2f3085`); gerador rodado da cópia da tag. Nada tocado no clone original nem no Open; gravados só `AVAL2-*.log`.

| AT | Sonda | Esperado | Observado | Resultado |
|---|---|---|---|---|
| AT-001 | `AVAL2-AT001-gerar.log`; extra em `AVAL2-AT003-AT009-negativos.log` (`tests/test_sobra.py`, `docs/sobra.md` commitados no clone) | 15 skills; docs/exemplos/tests iguais à semente; o resto byte a byte igual; README 15 + 3 em PT e EN; sobra apagada | rc=0, 15 `GERADO.txt`; diff de 0 linhas nos 6 caminhos; as 3 pastas iguais à semente; README "Quinze… / As outras três…" e "Fifteen… / The other three…"; as 2 sobras ` D` | PASS |
| AT-002 | `AVAL2-AT002-release-de-modo.log` | name/version/license do Open; description/compatibility do modo; GENERATED; corpo do modo com identificação do starter; "Quando migrar"; só o fecho | iguais campo a campo; corpo = modo com a URL do starter; MIGRAR = `blocos/MIGRAR.md`; arquivos `SKILL.md`, `agents/openai.yaml`, `GERADO.txt`; nada de `sdd/bin/`, ledger ou Fase 4 pesada | PASS |
| AT-003 | `AVAL2-AT003-AT009-negativos.log` (5 mutantes; `--lint` na cópia crua) | 65 com a causa, starter intocado; crua reprova | os 5 com rc=65 e causa específica, "starter intocado: sim"; `--lint` crua rc=65 | PASS |
| AT-004 | `AVAL2-AT004-modo-iniciante.log` | 1 OK; só git e gh; sem token; Vercel pelo status/checks e URL; workflow continua; falha sem redeploy; ponteiro | só "Posso publicar?"; "token" só na varredura de segredo e em "Nenhum token, nunca"; 0 CLI da Vercel; status, `environment_url`, `gh pr checks`, preview; `gh run list --commit`; "Não refaça o deploy…"; SKILL.md só ganha o ponteiro, 500 linhas | PASS |
| AT-005 | `AVAL2-AT005-A1-A3.log` | trechos de brainstorm, handoff, governança | todos presentes | PASS |
| AT-006 | `AVAL2-AT006-sem-terminal.log` (regex mais larga que a do build) | sem comando; sem Verify Gate exigido; governança só no condicionado | brainstorm e handoff sem cerca de shell nem pedido de comando; restam um exemplo de Status do Build em `PERGUNTA_DECISAO.md`, um `git rev-parse` na tabela de inferência do `RESUMO_ETAPA.md` (instrução ao agente) e o conteúdo do prompt de retomada; molde da ficha sem Verify Gate; governança: `psql` só em `SKILL.md:84` e `CATALOGO:88`, condicionados | PASS (achados 1 e 2) |
| AT-007 | `AVAL2-AT007-AT010-open.log` | builder 1.5.0, seção, como-falar, identificação, lint, 22, ux-review lê o padrão | tudo presente; lint rc=0 nas 22; `sdd-ux-review` 2.6.0 linha 89 | PASS |
| AT-008 | `AVAL2-AT008-saida-gerada.log` | 5 checagens 0; 1 byte ⇒ 1 | publish-check 0; check-versions `--base v1.5.17` 0 (18); gate.sh 0; check-gerado 0; 62 testes OK; 1 byte em 3 arquivos ⇒ rc=1 | PASS |
| AT-009 | `AVAL2-AT003-AT009-negativos.log` | 65 antes de gravar | 6 casos rc=65, starter intocado | PASS |
| AT-010 | `AVAL2-AT007-AT010-open.log`, `AVAL2-AT010-testes-existentes.log` | regressões verdes; release ≤ 500; init sem `scripts/starter` | lint, check-versions (22), `test_agnostico` 7 OK; 500 linhas; init com 22 skills, sem starter; 69 testes OK | PASS |

A1–A3 do ciclo 1: CORRIGIDOS (`AVAL2-AT005-A1-A3.log`), cada um com mutante morto (`AVAL2-sabotagem-A1-A3.log`).

Verify Gate: só o publish-gate sobre `git archive HEAD` (GREEN, rc=0); a suíte completa não rodou por instrução.

PENDENTES DE RECIBO: OK do Roberto nas 3 paradas novas; recibo do que mudou entre as séries da brainstorm no teste do iniciante; 2ª geração real, PR e Release do starter, Release e CI do Open; suíte completa em `1d8fc65`.

ACHADOS (nenhum bloqueia um AT)
- 1 (baixa) — `references/PROCEDIMENTO.md:91-92` ("quando a forma de entrega pede script") e `assets/GOVERNANCA_REVIEW_TEMPLATE.md:21` (prova_manual | prova_script como alternativas) oferecem o script sem dizer "Verify Gate por comando". Não é regressão (PROCEDIMENTO igual ao da v1.5.17).
- 2 (baixa) — brainstorm e segurança geradas citam `fragments/RESUMO_ETAPA.md` (forma curta, não reescrita; no starter o arquivo está em `references/`).
- 3 (informativo) — brainstorm 2 de 3 na 1ª série e 3 de 3 na `s2`: o BUILD_REPORT diz se o texto mudou entre as séries.
>>>
