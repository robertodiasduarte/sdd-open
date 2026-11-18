# BUILD REPORT: F22 — Aviso de versão e upgrade

> O pacote sabe a própria versão, o `init` grava o registro do que instalou, o `doctor` e duas skills avisam versão
> nova sem parar nada, e o verbo `upgrade` leva a versão nova para o projeto sem tocar no que a pessoa editou.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F22_AVISO_VERSAO |
| **Date** | 2026-11-15 |
| **Author** | build-agent |
| **DEFINE** | [DEFINE_F22_AVISO_VERSAO.md](../features/DEFINE_F22_AVISO_VERSAO.md) |
| **DESIGN** | [DESIGN_F22_AVISO_VERSAO.md](../features/DESIGN_F22_AVISO_VERSAO.md) (v1.3) |
| **Status** | Complete — PASS (recibo: CI do PR #32 verde em `7ba7eb0`, 18 de 18 jobs, run 43737757795) |

---

## Summary

| Metric | Value |
|--------|-------|
| **Tasks Completed** | 24/24 linhas do manifest (a 10 trocada na v1.1 do DESIGN; a 22 com 4 arquivos; a 24 com 10) |
| **Files Created** | 7 (`VERSION`, `bin/lib/versao.sh`, `sdd/bin/versao-nova.sh`, `docs/upgrade.md`, `docs/pt-BR/upgrade.md`, `tests/test_f22_versao.py`, `tests/test_f22_upgrade.py`) |
| **Lines of Code** | ver `git diff --stat v2.16.1..258287d` (build `d1eda3e` + 6 commits de revisão) |
| **Build Time** | 2026-11-15, 05:46 (v2.16.1 publicada) a 11:30 |
| **Tests Passing** | Verify Gate exit 0 em `258287d`: 2.277 testes em 28 min, 3 pulados (`evidence/F22_AVISO_VERSAO/VERIFY-GATE-258287d.log`); partida: 2.219 em `v2.16.1` |
| **Agents Used** | 0 especialistas (build direto); 1 agente fresco no raio de impacto |

---

## Seleção de modo

| Item | Valor |
|---|---|
| Sinais | 24 linhas de manifest, acopladas: `bin/sdd-open.sh` usa `bin/lib/versao.sh` e o `sdd/bin/versao-nova.sh`; os testes usam os três |
| Recomendação | default — um autor lembra os nomes e as assinaturas entre os três arquivos |
| Decisão do usuário | default, 2026-11-15 (pedido do Roberto: "execute o pipeline até o release"; modo de rotina) |

---

## Landmines lidas no build

Varredura `sdd/bin/playbook-lint.sh --grep` em 2026-11-15 sobre `v2.16.1`, por superfície: doctor, init, MANIFEST,
hooksPath, worktree, git archive, sha256, ls-remote, teto, Windows, PIPESTATUS, 11 dígitos, winpid, export-subst,
starter, contagem, text=True, subprocess, bash, PYTHONIOENCODING, paralelo.

| Superfície | LM-nnn | Veredito | Como / onde |
|------------|--------|----------|-------------|
| `git archive` (Verify Gate sem `.git`) | LM-006 | ✔ tratado | `versao_do_pacote` cai até `desconhecida` sem `.git`; o teste do pacote real é pulado com o motivo sem a tag |
| sabotagem | LM-009 | ✔ tratado | sem `git checkout --`; as provas de dente rodam numa cópia |
| teto da OpenRouter | LM-010 | ✔ tratado | `/credits` antes de cada rodada; o estouro do auditor na rodada 2 do DESIGN custou US$ 0,03 |
| `MANIFEST`, sha256 | LM-012 | ✔ tratado | nenhum sha256 inteiro no pacote; os testes calculam em tempo de execução; o publish-gate passou |
| `text=True` | LM-014 | ✔ tratado | os testes novos usam o `roda` do `apoio` (UTF-8) |
| `PYTHONIOENCODING` | LM-015 | ✔ tratado | o reserva Python das `impressoes` escreve por `sys.stdout.buffer` em UTF-8 |
| teto no Git Bash | LM-016 | ✔ tratado | `versao-nova.sh`: o pai tem relógio próprio, o subshell solta o pipe, o corte é melhor esforço (`taskkill` pelo winpid) |
| reserva silenciosa | LM-017 | ✔ tratado | `VERSAO_FONTE` diz qual fonte respondeu; 1 teste por fonte |
| `PIPESTATUS` no zsh | LM-018 | ✔ tratado | logs de evidência por `bash -c` com `rc=$?` |
| `ls a b` | LM-025 | ✔ tratado | existência por `[ -f ]` |
| bash do WSL | LM-029 | ✔ tratado | os testes chamam o `BASH` do `apoio` |
| executor que mascara o cp1252 | LM-030 | ✔ tratado | os testes novos não põem `PYTHONIOENCODING` |
| teste de tempo sob carga | LM-031 | ✔ tratado | o teste do teto mede só o limite de cima (< 7 s); a suíte e as provas não rodaram em paralelo com ele |

---

## Candidatos ao playbook

nenhum candidato nesta build (o único proposto, o do grep BSD, foi descartado na curadoria de 2026-11-15: o mecanismo não se reproduz neste Mac; ver `sdd/reports/evidence/F16W2_F22/CURATOR-bloco.txt`, linha 26)

---

## Files Created

| File | Lines | Agent | Verified | Notes |
| ---- | ----- | ----- | -------- | ----- |
| `VERSION` | 1 | (direct) | ✅ | `$Format:%(describe:tags=true,match=v[0-9]*)$`; carimbo medido com git 2.54 (`v9.1.0`, `v9.1.0-1-g…`) |
| `bin/lib/versao.sh` | 128 | (direct) | ✅ | versão, instaláveis, impressões, registro |
| `sdd/bin/versao-nova.sh` | 125 | (direct) | ✅ | a consulta com teto; exits 0/10/20/30/64 |
| `docs/upgrade.md`, `docs/pt-BR/upgrade.md` | 83, 79 | (direct) | ✅ | U12 |
| `tests/test_f22_versao.py` | 509 | (direct) | ✅ | AT-001 a AT-005, AT-008, AT-009, guarda de rede |
| `tests/test_f22_upgrade.py` | 282 | (direct) | ✅ | AT-006, AT-007, pacote real v2.12.1 |

Modificados: `bin/sdd-open.sh`, `bin/lib/say.sh` (`info`, ℹ️), `.gitattributes`, os 2 workflows, `MANIFEST.txt`,
`sdd/config.example.yaml`, 3 skills (sdd-new-session 1.7.0, sdd-release 2.13.0 com `como-falar.md` e `MODO_INICIANTE.md`,
sdd-build 2.10.1 com `web/MODO_WEB.md`), a troca do starter, `README*`, quickstarts, guia do aluno,
`cli-conventions.md`, `tests/apoio.py` e 13 testes que fixavam texto ou versão.

---

## Verification Results

| Check | Resultado |
|---|---|
| Verify Gate (`verify-gate.sh sdd/features/DEFINE_F22_AVISO_VERSAO.md`) | exit 0 em `258287d`: 2.277 testes, 3 pulados (o pacote real v2.12.1 sem `.git` na cópia; 2 de antes), publish-gate verde na cópia de `git archive` (`VERIFY-GATE-258287d.log`). Antes: `d1eda3e` caiu em 1 teste (o do carimbo copiava o `VERSION` já carimbado da cópia; `97eb385`); `a68905f` verde; os gates de `97eb385`, `aae54ff`, `0463d8b` e `e57d064` foram interrompidos porque a revisão mudou o código antes do fim |
| Suíte no piso do macOS antes do commit (bash 3.2, Python 3.9) | 2.266 testes: 5 falhas e 1 erro, todos de texto ou trava que a F22 mudou de propósito (`(ref: LM-…)`, "rode init", comentário que citava o `gh release create`, `os.geteuid` fora do `apoio`, a lista literal do `find`); consertados e 186 testes dos módulos tocados verdes |
| `scripts/check-versions.py --base v2.16.1` | VERDE: 22 skills com versão coerente |
| `skill-lint.py` nas 3 skills | 0 erros; `sdd-release/SKILL.md` com 500 linhas (o teto do `test_conversa`) |
| publish-gate (cópia só com o que é do pacote) | GREEN |
| Linha de base (os testes da F22 sobre o código da `v2.16.1`) | vermelha: 45 falhas e 14 erros, rc=1 (`evidence/F22_AVISO_VERSAO/BASELINE-v2.16.1-vermelho.log`) |
| e2e manual: projeto instalado pela v2.12.1 real, 2 arquivos editados, `upgrade --de v2.12.1` | 46 novos e 77 intactos copiados, 2 editados intocados com `.novo`/`.diff`/`.pacote.diff`, nada commitado; 2ª rodada `EM DIA` |

---

## Segurança

nenhum (a linha Segurança do DEFINE é N.A.; a nota de construção — nome de tag é dado não confiável — está tratada:
só `refs/tags/vX.Y.Z` exatos contam, e nada do que volta é executado ou interpolado em comando; o `ls-remote` roda
com `credential.helper` vazio, sem prompt e sem enviar dado do projeto).

---

## Issues Encountered

1. A verificação de segurança do Claude Code barrou o comando que inseria o `upgrade` no `sdd-open.sh`, porque o texto
   do código tinha `rm` com caminho em variável. Nada foi executado. O código final não tem esse `rm`: o `.sddtmp` de
   uma cópia que falhou é sobrescrito na rodada seguinte, e a pasta de trabalho fica no TMPDIR (`mktemp`).
2. O auditor qwen falhou nas 2 rodadas da revisão do DESIGN: cortou o bloco de vereditos na 1ª e passou do teto de
   900 s na 2ª. Os achados do revisor foram decididos um a um (Advisor Ledger do DESIGN).
3. A cópia montada à mão para o publish-gate levou o PROMPT e os documentos da frente, e o gate barrou por caminho de home. Refeito com `grep -E`: GREEN. **Correção (curadoria, 2026-11-15):** a causa que eu dei aqui (o `\|` não alternaria no grep do macOS) é falsa: o curador testou neste Mac e o filtro alterna. A causa real não ficou registrada (não há log da linha de comando).

---

## Deviations from Design

| # | O quê | Por quê |
|---|---|---|
| 1 | `versao-nova.sh` ganhou `--curto` (só o dado: a versão, o motivo ou onde está desligada) | o `doctor` monta a linha única do U1 (`… · última publicada vX`) sem interpretar o texto da linha humana |
| 2 | o `doctor` diferencia "rode o upgrade" de "é edição sua" pelo registro na versão do pacote | achado 2·R6 da revisão do DESIGN (o conselho em laço) |
| 3 | o `upgrade` com a mesma versão do registro e só editados responde `EM DIA`, sem `.novo` | não há versão nova para pôr ao lado; o AT-007 pede "em dia" quando a versão é igual |
| 4 | a consulta do `versao-nova.sh` roda da pasta temporária, sem a config global, de sistema e do repositório do projeto | revisão do código, rodadas 4 e 5 (anônima de verdade: sem `insteadOf`, helper ou token do `.git/config`) |
| 5 | arquivo que não bate com nada ganha uma 2ª impressão sem `\r` | revisão do código, rodada 2 (checkout com CRLF no Windows não vira edição) |
| 6 | com `--de`, o registro existente também barra rebaixar; a forma tag exige o pacote na raiz de um clone e um `MANIFEST.txt` | revisão do código, rodadas 3, 5 e 6 |

---

## Contrato de aceite (C2) e avaliador de contexto fresco (C1)

**Camadas do manifest:** 1 (o pacote não declara `layers:`)
**Contrato de aceite (passo 1.5 da `sdd-build`):** N.A. (1 camada)

**Veredito do avaliador (C1):** PASS_PENDENTE_RECIBO · ciclos: 1 · `sdd/reviews/AVALIACAO_F22_AVISO_VERSAO_20261115-1209.md` sobre `258287d`: os 10 ATs provados por execução no piso do macOS, 0 achados bloqueantes, 4 observações (O1 a O4, em Pendências). Recibo: o CI do PR (Ubuntu e piso do macOS; o Windows entra no `needs:` da release desde a F16W2). O bloco foi gravado como veio, com 2 mudanças: a linha `VEREDITO:` repetida para o lint e os caminhos absolutos das evidências encurtados para `sdd/reports/evidence/…`

---

## Advisor Ledger

Revisão do DESIGN (antes do código): 2 rodadas, Advisor Ledger do DESIGN (15 achados: 13 aplicados, 2 rebatidos com
evidência). Revisão do código: ledger completo em `sdd/reviews/LEDGER_REVISAO_F22_AVISO_VERSAO.md`.

| Rodada | Pasta | Engines | Achados | Decisão |
|---|---|---|---|---|
| 1 (`v2.16.1..d1eda3e`) | `EXTERNAL_REVIEW_20261115-065519` | claude + qwen | 1 grave, 2 médios, 3 leves | R1 rebatido (o PROMPT não rastreado entrou só no diff da revisão); 5 aplicados (`97eb385`) |
| 2 (`..97eb385`) | `EXTERNAL_REVIEW_20261115-073246` | claude + qwen | 1 médio, 1 leve | 2 aplicados (`aae54ff`) |
| 3, teto (`..aae54ff`) | `EXTERNAL_REVIEW_20261115-074808` | claude + qwen | 2 leves | aplicados (`a68905f`) — 4ª rodada: decisão do Roberto |
| 4 (`..a68905f`) | `EXTERNAL_REVIEW_20261115-081159` | claude + qwen | 2 leves | aplicados (`0463d8b`) — 5ª: decisão do Roberto |
| 5 (`..0463d8b`) | `EXTERNAL_REVIEW_20261115-100754` | claude + qwen | 2 leves | aplicados (`e57d064`) — 6ª: decisão do Roberto |
| 6 (`..e57d064`) | `EXTERNAL_REVIEW_20261115-103313` | claude + qwen | 2 leves (o auditor os subiu a médios) | R1 aplicado (`258287d`), R2 rebatido — 7ª: decisão do Roberto |
| 7 (`..258287d`) | `EXTERNAL_REVIEW_20261115-105906` | claude + qwen | 2 leves | adiados para a ficha (só leves) |
| 8 (`..074ef5a`) | `EXTERNAL_REVIEW_20261115-133645` | claude + qwen | 2 médios | depois do CI do PR vermelho em `258287d` (o teto da checagem contava voltas de `sleep`: 7,2 s no piso do macOS; consertado em `074ef5a`); R1 aplicado (`7ba7eb0`: editado que o pacote não mudou não é para mesclar), R2 rebatido — decisões do Roberto |
| 9 (`..7ba7eb0`) | `EXTERNAL_REVIEW_20261115-135049` | claude + qwen | 2 leves | R1 adiado para a ficha, R2 rebatido; `--conferir` CONFERE nesta versão |

Sem `--paths` no código; sem 2º revisor (`--no-revisor2`, a cadeia combinada) e sem desempate. O raio de impacto rodou
antes da rodada 1 (8 superfícies, agente fresco) e foi refeito à mão para as mudanças até a rodada 3. Custo na OpenRouter
das 9 rodadas: US$ 0,37 (qwen, medido pelo `eval-revisores.sh`); o claude é por assinatura (US$ 20,71 nominal, com o DESIGN).

---

## Drift detectado

nenhum

---

## Acceptance Test Verification

| ID | Critério (resumo do EARS do DEFINE) | Resultado | Evidência |
|---|---|---|---|
| AT-001 | versão do pacote: carimbo → describe → pasta → desconhecida; tag local antes do archive | true | `evidence/F22_AVISO_VERSAO/AT-001.log` |
| AT-002 | `init` grava o registro só na 1ª instalação | true | `evidence/F22_AVISO_VERSAO/AT-002.log` |
| AT-003 | linhas de versão do `doctor`; aviso com o comando; exit igual | true | `evidence/F22_AVISO_VERSAO/AT-003.log` |
| AT-004 | "não conferido" com motivo em ≤ 7 s; desligada e onde; a suíte não vai à rede | true | `evidence/F22_AVISO_VERSAO/AT-004.log` |
| AT-005 | aviso nas 2 skills sem parar; o starter sem o passo | true | `evidence/F22_AVISO_VERSAO/AT-005.log` |
| AT-006 | `upgrade`: classes, cópia, `.novo`/`.diff`, registro, sync e doctor, nada commitado, `--dry-run` | true | `evidence/F22_AVISO_VERSAO/AT-006.log` (inclui o pacote real v2.12.1) |
| AT-007 | sem registro e sem `--de` para; `--de` inválido e pacote velho 64; em dia 0; falha no meio retoma | true | `evidence/F22_AVISO_VERSAO/AT-007.log` |
| AT-008 | hooks de outra worktree = ligados; de outro repositório = OUTRO | true | `evidence/F22_AVISO_VERSAO/AT-008.log` |
| AT-009 | sem `LM-nnn` nos textos das skills, com a lista de aceites | true | `evidence/F22_AVISO_VERSAO/AT-009.log` |
| AT-010 | não regressão: a suíte inteira | true | `evidence/F22_AVISO_VERSAO/VERIFY-GATE-258287d.log` |

---

## Pendências (para a ficha)

1. `alarme.sh` da `sdd-higiene-dado` não reconhece o `sdd/hooks` de outra worktree (diz "outro gerenciador"); o
   comentário do `sdd-open.sh` registra (raio de impacto).
2. Proxy configurado só no git (`http.proxy`) deixa a consulta "não conferida" (revisão, rodada 7, R1).
3. Com `autocrlf=true`, a 2ª impressão roda um arquivo por vez — desempenho no Git Bash (revisão, rodada 7, R2).
4. Um commit com duas tags `v[0-9]*` faria o carimbo do `VERSION` não bater e o Build da release cair (raio de impacto).
5. O1 do avaliador: hooksPath para o `sdd/hooks` de uma worktree removida aparece como "outro gerenciador".
6. O2: os `.diff` de `sdd/upgrade/` levam caminho absoluto e horário no cabeçalho.
7. O3: o aceite do AT-009 cobre o exemplo de conversa da `sdd-playbook/references/como-falar.md`, não só sintaxe.
8. O4: comentários `(LM-016)` em `checar.sh` e `inventario.sh` (fora do escopo do AT-009).
9. A-003: o teto da consulta no Git Bash do Windows só é provado pelo CI do PR (verde em `7ba7eb0`).
10. Revisão, rodada 9, R1: pacote de versão desconhecida e projeto com registro — o doctor manda o upgrade, que recusa com 64 dizendo o caminho.
11. O avaliador provou `258287d`; as 2 mudanças depois dele (`074ef5a` teto pelo relógio, `7ba7eb0` classe "seu") têm teste e passaram no CI do PR, sem 2º ciclo do avaliador.

---

## Final Status

### Overall: ✅ COMPLETE — PASS com o recibo do CI do PR #32 (`7ba7eb0`, Ubuntu, piso do macOS e Windows verdes); revisão do código em 9 rodadas (4ª a 9ª acima do teto, decisões do Roberto); `main` = `7ba7eb0` e tag `v2.17.0` por push atômico

---

## Next Step

**sdd-release**: PR, CI verde (o recibo do avaliador), o OK do Roberto ("sdd-open autorizado") para merge, tag e Release; regenerar o starter.
