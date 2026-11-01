# REVISÃO DO DESIGN F10_REVISAO — contexto fresco (modo contrato, antes do build)

> Bloco devolvido pelo revisor em contexto fresco (subagente sem a conversa do design), sobre
> `DESIGN_F10_REVISAO.md` v1.0 e `DEFINE_F10_REVISAO.md` v1.2, com a branch em `89ac76f` (= `v2.2.10`).
> Logs das sondas em `sdd/reports/evidence/F10_REVISAO/AVAL-DESIGN-*.log` (8). Guard antes do despacho:
> `AVAL-DESIGN-guard.log` (VERDE). As decisões sobre cada nota estão no Advisor Ledger do DESIGN (v1.1)
> e no `## Contrato de aceite`; todas foram aplicadas no DEFINE v1.3.

```text
<<<CONTRATO
VEREDITO: NEEDS_WORK — 1 HIGH, 5 MEDIUM, 13 LOW

Medições:
- AVAL-DESIGN-diff-congelado.log — índice temporário + intent-to-add + `git diff --binary <merge-base>`: inclui untracked (texto e binário), exclui `sdd/features`, índice real intacto (INDICE_REAL_INTACTO=sim), sha256 igual em 2 execuções (ESTAVEL=sim) e diferente com 1 byte (MUDA_COM_1_BYTE=sim). Em WORKTREE `cp .git/index` falha ("Not a directory"); `git rev-parse --git-path index` funciona. [exit=0]
- AVAL-DESIGN-diff-commit.log — o sha256 é o mesmo antes do commit, depois do commit e depois de merge da main nova (IGUAL_APOS_COMMIT=sim, IGUAL_APOS_MERGE=sim). [exit=0]
- AVAL-DESIGN-checkignore.log — `git check-ignore -q <dir>/.sonda` sem a pasta existir: rc=1 sem regra, rc=0 com `dir/`; worktree herda o info/exclude comum; o `→` da U5 (`>> .git/info/exclude`) FALHA em worktree (rc=1, "Not a directory"); `$(git rev-parse --git-common-dir)/info/exclude` funciona. [exit=0]
- AVAL-DESIGN-flags-cli.log — claude 2.1.314, codex-cli 0.163.0, gemini 0.22.2: todas as flags da Decision 4 existem (0 ausentes); `codex exec` lê prompt do stdin; `--approval-mode default` do gemini = "prompt for approval", não "sem ferramenta". [exit=0]
- AVAL-DESIGN-adapter.log — `bash -c 'source "$1"; shift; adapter_invocar "$@"'` funciona no /bin/bash 3.2.57 (3 argumentos, modelo com espaço e `/`); `subprocess.run(timeout=)` estoura e o processo neto CONTINUA vivo; com `start_new_session`+`killpg` morre. [exit=0]
- AVAL-DESIGN-ledger-worktree.log — no worktree temporário do passo 5 da release (origin/main + cherry-pick) o ledger existe e `<pasta>/META.txt` não; `[0-9]{11,}` do publish-gate reprova um sha256 real (`…466403738843…`) e o float `0.06264225000000001`. [exit=0]
- AVAL-DESIGN-loop.log — `--self-test` atual VERDE; fixtures da F9 têm 0 chaves novas; META com 2º revisor `indisponível`/67 e auditor sem rodar + `revisor2: dispensado` no ledger → 10 "review inválida"; o mesmo META sem `revisor2_exit` → 0 no loop v2.2.10. [exit=0]
- AVAL-DESIGN-testes-tocados.log — test_fluxo + test_decisoes_lint + test_bash32 + test_agnostico: 69 testes em 10,0 s no piso; 744 `def test_` confere com o AT-038. [exit=0]

AJUSTES (≤5, os mais graves)
1. AT-015 / AT-022 / AT-028 / Decision 5 / manifest 28–33 · HIGH / estado sem critério + aceite circular · O AT-015 fixa só `revisor2_engine: indisponível`, sem `revisor2_exit`; a Decision 5 PARA o script no 1º papel de revisor ≠ 0, então o auditor não roda e o passo 1 do loop força 10 — o ramo de dispensa do AT-028 nunca chega a PRONTO. As fixtures 28–33 trazem `auditor.verdicts.jsonl` AGREE, um estado que o script não produz; se o build omitir `revisor2_exit`, o AT-028 manda o loop sair 64. O `--conferir` (AT-025) recusa um 2º revisor dispensado que o loop aceitou. Risco prático: `gemini` no PATH falha AUTH; numa máquina sem codex ele vira o 2º revisor e, com ≥ 8 arquivos, toda revisão para em 65 sem auditoria. O privado: `REV2_EC=EXIT_CADEIA_ESGOTADA; REV2_ENGINE="indisponível"` e "falha do 2º revisor NÃO derruba a cadeia" (adversarial-review.sh:675–686); exit só de REV/AUD (l. 988–990). · Ajuste: indisponível → `revisor2_exit: 67`; 2º revisor que falha (65/66 incluídos) registra o exit, imprime ⚠️ e o auditor roda sobre o 1º revisor; o exit do script vem só do revisor e do auditor; a dispensa é do loop; `--conferir` aceita `revisor2_exit ≠ 0` só com dispensa; teste que roda o `loop` sobre as pastas que o stub gera.
2. Decision 8 / AT-026 / AT-027 (passo 6 da sdd-release) · MEDIUM / falha de execução · os passos 5–6 rodam no worktree temporário de origin/main + cherry-pick (sdd-release/SKILL.md:156–160); a pasta da revisão é ignorada (R9) e só existe na worktree da frente → `--ledger` sai 2 e a release aborta sempre. · Ajuste: `--ledger` roda na pasta da frente depois do commit atômico (passo 4) e antes do passo 5; pasta ausente → 2 com "rode na pasta da frente"; teste de uma 2ª worktree.
3. Decision 3 / AT-009 · MEDIUM / premissa errada · "Copia `.git/index`" e o `→ printf … >> .git/info/exclude` falham em WORKTREE (`.git` é arquivo) — o caso principal (sdd-new-session; esta frente). · Ajuste: `git rev-parse --git-path index` (índice ausente = vazio) e `$(git rev-parse --git-common-dir)/info/exclude`; teste dos AT-006/AT-009 dentro de `git worktree add`.
4. AT-023 × AT-001/AT-003 / Decision 2 · MEDIUM / estado sem critério · o `→` do 65 imprime `(<auth_check>)`, mas o registry tem 9 colunas sem `auth_check` e linha ≠ 9 colunas sai 64. · Ajuste: cada adapter define `adapter_credencial` (onde a credencial vive); o `→` do 65 cita a saída dela.
5. AT-033 e AT-010 / manifest 51 · MEDIUM / gate não cobre AT · AT-033: `test_agnostico.py` não procura nome de engine; já há 56 ocorrências em `.agents/skills` (ex.: contexto-fresco.md:21). AT-010: flags, stdin e cwd vazia dos 3 adapters de CLI nunca executados. · Ajuste: assert nas seções que a F10 muda (`test_contrato_build_release.py`); binários falsos `claude`/`codex`/`gemini` no PATH que gravam argv, cwd e stdin.

NOTAS MENORES (LOW)
- Pattern 2: timeout deixa a CLI neta viva — `start_new_session=True` + `os.killpg`.
- Pattern 2 chama `"bash"` do PATH, não o bash da frente — passar `os.environ["BASH"]`.
- Pattern 1 `> "$out" 2>&1` mistura stderr no JSON — separar o stderr.
- `tests/apoio.py:35` herda `OPENROUTER_API_KEY` — no `test_revisao`, remover a chave, tirar as CLIs do PATH e fixar `SDD_REVIEW_OPENROUTER_URL=http://127.0.0.1:9/`.
- `[0-9]{11,}` do publish-gate e sha256 reais em fixtures — gerar em execução ou hex sem dígitos.
- Decision 4 / AT-036: `codex -s read-only` lê o FS inteiro; gemini mantém leitura e web — "sem ferramenta de escrita".
- AT-022 não fixa os textos `n/a (revisor1 raso` / `n/a (2º revisor raso` que o loop casa.
- Desempate: com 2 revisores o auditor pode devolver a base — `desempate_alvo` = id do jsonl do revisor.
- Determinismo do sha256 contra config do usuário — `-c diff.noprefix=false --no-renames --diff-algorithm=myers`.
- AT-040: o diff da F10 dispara o 2º revisor; `sdd/reports/reviews` não ignorada nesta worktree — `real.sh` fixa `--revisor2`/`--no-revisor2` e o exclude por `--git-common-dir`.
- AT-041 cita `tests/test_docs.py`, fora do manifest.
- Docs fora do manifest: `docs/adaptation-guide.md:92` ("Model names are deliberately absent"); `docs/chained-flow.md:75`; o roadmap fica *planned* até a F11.
- `--conferir`/`--ledger` sem `RESULTADO:` + `→` nos ATs; AT-021 "never a remembered value" não testável; doctor não vê `sdd/bin/adapters/`; `TERMOS` duplicado e `\bauth` casa `author` num caminho.
CONTRATO>>>
```
