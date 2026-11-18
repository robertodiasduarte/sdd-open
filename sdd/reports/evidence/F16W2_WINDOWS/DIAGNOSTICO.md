# F16W2 — diagnóstico das quebras do Windows (releitura da 1ª medição)

Fonte: os 169 logs de `sdd/reports/evidence/F16W_WINDOWS/windows/logs-quebrados/` (CI do PR #30, `491efa6`), lidos em
2026-11-14 por 4 agentes de leitura (só leitura, um grupo de módulos cada), com arquivo:linha conferido no código de
`ad32fe1`. Causas gerais: A cp1252 · B `\r\n` do stdout do Python · C `python3 -I` ignora `PYTHONIOENCODING` · D comando
falso sem extensão que o Python nativo não executa · E o MSYS expande argumentos · F forma de caminho · H1 PATH de links.

## Produto (o aluno no Windows vê)

| Causa | Onde | Efeito | Conserto |
|---|---|---|---|
| A | `design-lint.py:278`, `governanca-bloco.py:34,161,170`, `skill-lint`, `handoff-lint`, `kb-dominios`, `report-lint`, `deploy-espera-testes.py:407,418`, `kb_normativo`, `collect_evidence.py:353`, `check-versions.py`, `gerar-starter.py` | `UnicodeEncodeError`, exit 1; stderr com `\U0001f6d1` e "ã" como byte cp1252 | `reconfigure` de stdout/stderr (e stdin) em UTF-8 e `\n` |
| A | heredoc de `sdd-fluxo.sh:129` e `:653`; linha de reserva sem `lib/python.sh` | `→` derruba o `para()` | `PYTHONIOENCODING` também na reserva; o calço do item B |
| A | `sdd/hooks/pre-commit:208` chama `report-lint.py --stdin` sem `PYTHONIOENCODING`; `report-lint.py:596` lê o stdin em cp1252 | relatório válido bloqueia o commit | UTF-8 no hook e no stdin do lint |
| B | `slot.sh` (`ESTADO="${LIDO%%$'\n'*}"` vira `VALOR\r`), todo `$(python3 …)` | slot "vazio" com valor (39 quedas) | calço do Windows tira o `\r`; rede local no `slot.sh` |
| F | `governanca-fronteira.sh:86` (`canon` pelo `realpath` do Python) × `:149` (`pwd -P`); hasher `:177-199`; `:230` | "incluir fora do worktree" (~26) | uma forma só (`/`) em `canon`, `WT`, `OUT_DIR` e no hasher |
| F | `test-baseline.sh:225` (`os.path.join`) | id `src\foo.test.ts` nunca casa (6) | junção com `/` |
| F | `sdd-archive.py:189` (`os.path.join("sdd", sub)`) | `sdd\features/X.md` nunca casa com o git (21) | `"sdd/" + sub` |
| F | `docs-extract-decisions.sh:44` (`relpath` com `\`) + `awk -v` | links do índice de ADRs quebrados | `relpath(...).replace(os.sep, "/")` |
| F | `sdd-fluxo.sh:646` | `→ /sdd-build sdd/features\DESIGN_X.md` | junção com `/` |
| F | `adversarial-review-gate.sh:179-186` (compara `/tmp/…` com `C:\…`); `:28` `pwd` com espaço/metacaractere | "GATE QUEBRADO" (19) | comparar no bash (`-ef`); `pwd -W` |
| F | `hooks_path_e_nosso` (`bin/sdd-open.sh:545`, `alarme.sh:47`) só aceita `/*` | `core.hooksPath = C:\…` visto como "OUTRO" | `cygpath -u` quando `[A-Za-z]:` |
| F | `validate_kb.py:298` (`split(":",1)`) | `C:\…\fora.py` vira `C`, motivo errado | reconhecer `X:\` como absoluto |
| F | `report-lint.py:600` `os.popen("git … 2>/dev/null")` | passa pelo `cmd.exe`; raiz errada vinda de subpasta | `subprocess.run(["git", …])` |
| lentidão | `sdd/hooks/pre-commit`: `regra_h2` (`basename`), `regra_h5` (`cat-file` + `head|od|tr`, `wc`…), `regra_h3` (`printf|grep`) por arquivo | ~18 processos por arquivo; 1º commit depois do `init` (450 a 630 arquivos) passa de 120 s | builtins do bash; filtrar por extensão antes do `cat-file` |
| lentidão | `bin/sdd-open.sh` `perfil_arquivo`/`renderizar_gerado` (~263-307): `head|od|tr`, `tr|cmp`, `sed`, `tail`, `cmp` por arquivo, 2 passadas | `init` lento; 5 unidades no teto de 600 s | menos processos por arquivo |
| vigia | `checar.sh` `gh_estado` (~103) e `alcance` (~449): o exit de um processo morto pelo `taskkill` pode voltar 0 no Cygwin; o neto do askpass segura o pipe do `$( )` | `gh` pendurado vira "ok"; askpass passa do teto (3) | o vigia anuncia o corte (marcador); saída em arquivo, não no pipe |
| nomes | `playbook-curator.sh:1909` cria `BUILD_REPORT_qu"o te.md` | autoteste FALHA no Windows (2) | `qu&o te` |
| temp | `sdd-drive.sh:1267` `rmtree(ignore_errors=True)` | autoteste deixa `sdd-drive-*` (objetos do git só leitura) | `onerror` com `chmod` |
| trava | `sdd-drive.sh:355` sem `O_NOFOLLOW` no Windows; `larga_estado` deixa o arquivo da trava | link na trava cria arquivo fora (achado guardado) | `islink` antes do `open` |

## Arnês de testes (só o teste)

| Causa | Onde | Conserto |
|---|---|---|
| H1 | PATH de links em `test_revisao.py:46`, `test_eval_agree.py:24,94`, `test_revisao_adapters.py:96`, `test_playbook_curator.py:1059`, `test_hooks.py:78`, `test_sdd_open`/`test_claude_adapter` (`d/dirname`), `test_deploy_do_sha.py:400` | ajudante `path_restrito` em `apoio.py`: no Windows, as pastas reais |
| D | `gh` falso em `test_deploy_do_sha.py:79`; `env` sem `.exe` para o hook | `.bat` ao lado do falso; o produto acha o `gh` por `shutil.which` |
| E | `test_publish_gate_patterns.py:47,66` | `grep` pelo bash |
| F | `test_claude_adapter.py:59` (`__CWD__` cru), `test_gate_baseline.py:83` (`C:\U…` no config do git), `test_agnostico.py:37,49,53`, `test_sdd_kb.py:127`, `test_sdd_open` Hooks (`str(pc)`), `test_governanca_fronteira.py:367` | `json.dumps`, `as_posix()` |
| nomes | `a|b`, `"`, `:`, quebra de linha, `bytes` (`test_governanca_fronteira.py:356`, `test_playbook_curator.py:597`, `test_revisao.py:1072,459`, `test_copiar_docs`) | `SEM_NOME_ESPECIAL` |
| chmod | `test_sdd_open` doctor (644), `test_playbook_curator.py:884,900` | `SEM_CHMOD` |
| outros | `test_prompt_drift_scan.py:9` (`import pty`), `test_deploy_espera_testes.py:143` (`rename`), `test_playbook_invariantes.py:147` (link relativo), `test_fluxo.py:388` (`"F9\n"` no argv), `encoding="utf-8"` sem `errors` em `test_f17_textos.py:70`, `test_f17b_passo0.py:91`, `test_f17c_passo0.py:45`, `test_report_lint_evidencia.py:271,275`, `test_drive.py:55` e `test_fluxo.py:817` sem `lib/` | um por um |

## Por provar só no Windows

- A-003 (o executável por link não acha as DLLs) e o mecanismo do askpass que escapa do `taskkill`.
- A lentidão do `init` por etapa (`bash -x` com `$SECONDS`).
