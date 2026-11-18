# DESIGN: F16W2 — Windows, porte das quebras

> Arquitetura e especificação técnica numa passada só.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W2_WINDOWS |
| **Date** | 2026-11-14 |
| **Author** | design-agent (worktree `sdd-open-f16w-windows`) |
| **DEFINE** | `sdd/features/DEFINE_F16W2_WINDOWS.md` v1.1 |
| **Diagnóstico** | `sdd/reports/evidence/F16W2_WINDOWS/DIAGNOSTICO.md` (as causas com arquivo:linha) |
| **Status** | Ready for Build (v1.2: Decision 2 revista no Build, pelo raio de impacto) |

---

## Architecture Overview

```text
 aluno no Git Bash ─┬─ python3 sdd/bin/<lint>.py …        (chamada direta)
                    │     __main__: stdout/stderr (e stdin) → UTF-8 e "\n"            ← Decision 1
                    └─ bash sdd/bin/<script>.sh …
                          . lib/python.sh  ── calço transparente, só sem python3 que serve
                          ├─ python3 - <<'PY'  1º comando: stdout/stderr → UTF-8 e "\n"   ← Decision 2 (v1.2)
                          ├─ linha de reserva (sem lib/): export PYTHONIOENCODING=utf-8
                          └─ caminhos: uma forma só, "/" (realpath do Python + replace)  ← Decision 3

 git commit ─► sdd/hooks/pre-commit  regras por arquivo com builtins do bash               ← Decision 4
 sdd-open.sh init                    perfil e renderização com menos processos por arquivo

 checar.sh / inventario.sh  vigia: ( sleep 10; echo corte > marca; corta … ) &              ← Decision 5
                            saída do ls-remote / gh num arquivo, lida depois do corte

 tests/apoio.py  path_restrito() · falso() · constantes de pulo                             ← Decision 6
 CI do PR  testes-windows (16 fatias) → medição 2 → até 2 rodadas → piso e frases            ← Decision 7
```

## Key Decisions

### Decision 1: cada script Python troca a própria saída para UTF-8 e `\n`

**Contexto:** no Windows, o Python com a saída num pipe escreve em cp1252 e troca `\n` por `\r\n`; o aluno chama vários
lints direto (`python3 sdd/bin/design-lint.py`, `governanca-bloco.py`, `deploy-espera-testes.py`), sem bash no meio.
**Escolha:** no início do bloco `__main__` de todo `.py` do pacote com `__main__` (fora de `tests/`), o mesmo trecho:
`reconfigure(encoding="utf-8", errors="replace", newline="\n")` em stdout e stderr; o `report-lint.py` também lê o
stdin em bytes e decodifica em UTF-8. Uma guarda em `tests/test_f16w2_saida.py` percorre o `MANIFEST.txt`.
**Alternativa recusada:** só `PYTHONIOENCODING` no `python.sh`: não vale na chamada direta nem com `-I`.
**Consequência:** no macOS e no Linux a saída já é UTF-8 e `\n`; nada muda (AT-009).

### Decision 2: UTF-8 e `\n` no próprio Python embutido; o calço segue transparente (revista no Build)

**Contexto:** ~45 chamadas `python3` embutidas em scripts bash; no Windows o bash que captura a saída recebe `\r` (o
`slot.sh` lia `VALOR\r`), e `-I` ignora o `PYTHONIOENCODING`.
**Escolha (v1.2):** cada programa embutido (`python3 - <<'PY'`) troca stdout e stderr para UTF-8 e `\n` no início
(depois do `from __future__`), o mesmo trecho da Decision 1; os `python3 -c` cuja saída vira valor no bash (a fronteira)
trocam o `newline`, ou escrevem sem fim de linha (o prefixo do `docs-extract`); o `slot.sh` ainda tira o `\r` do que lê
(rede local). A linha de reserva dos scripts e o `pre-commit` exportam `PYTHONIOENCODING=utf-8`. Guarda:
`GuardaEmbutidos` em `tests/test_f16w2_saida.py`.
**Alternativa recusada (era a escolha da v1.1):** no Windows, o calço sempre, com `-X utf8 -u` e `| tr -d '\r'`. O raio
de impacto mostrou que o calço vai no PATH e vaza para o comando de teste do aluno (o `pytest` dele em modo UTF-8, com
resultado diferente de quando roda direto), que o `tr` segura as linhas de progresso no buffer e que o curador devolve o
playbook byte a byte (CRLF incluso).
**Consequência:** o calço volta a ser o da `v2.16.0` (transparente, só com o atalho da Store); nada muda fora do Windows.

### Decision 3: uma forma de caminho, com `/`, onde o Python e o bash se encontram

**Contexto:** o Python devolve `C:\x`, o `pwd` do Git Bash `/c/x` ou `/tmp/x`, o git `C:/x`.
**Escolha:** onde um caminho do Python é comparado com o do bash, os dois passam pelo mesmo canonizador
(`realpath(...).replace("\\", "/")`, que no Windows dá `C:/…` e resolve nome curto `RUNNER~1`); onde o Python junta
caminhos que o git conhece, junta com `/` (`"sdd/" + sub`, `posixpath`); `C:\…` e `/c/…` contam como absolutos
(`cygpath -u` quando existe); a raiz do git vem de `subprocess.run(["git", "rev-parse", "--show-toplevel"])`, nunca do
`os.popen` (que passa pelo `cmd.exe`).
**Alternativa recusada:** `cygpath` em todo lugar: só existe no Git Bash, e o Python nativo não o chama.
**Consequência:** no macOS e no Linux `realpath` já devolve `/`; os testes do Mac usam `ntpath` onde dá para simular.

### Decision 4: `pre-commit` e `init` com builtins do bash, filtrando antes de abrir o arquivo

**Contexto:** o `pre-commit` lança ~18 processos por arquivo (`basename`, `cat-file` para um temporário, `head|od|tr`,
`wc`, `printf|grep`); o `init`, dezenas por arquivo de skill, em 2 passadas. No Git Bash cada processo custa 10 a 20 ms.
**Escolha:** nome e extensão por expansão do bash (`${f##*/}`, `[[ … =~ … ]]` com `nocasematch`, bash 3.2); o blob só é
lido para os candidatos a texto; tamanho por `git cat-file -s`; o perfil do arquivo do `init` calculado uma vez por
arquivo. A contagem é a prova: uma armadilha no PATH (`basename`, `od`, `tr`, `wc`, `grep`, `head`, `sed`, `tail`,
`cmp` que anotam a chamada e repassam ao de verdade) conta os programas lançados num commit de 600 arquivos e num `init`.
**Alternativa recusada:** reescrever o hook em Python (o `pre-commit` precisa rodar sem Python; a higiene não depende dele).
**Consequência:** as recusas do hook são as mesmas (os testes de `test_hooks.py` e `test_alarme.py` seguem verdes).

### Decision 5: o vigia anuncia o próprio corte e a saída vai para um arquivo

**Contexto:** no Windows, o exit de um processo morto pelo `taskkill` pode voltar 0 pelo Cygwin, e o `gh` pendurado vira
"ok"; um neto do askpass segura o pipe do `$( )` depois do corte.
**Escolha:** em `gh_estado` e `alcance` (iguais em `checar.sh` e `inventario.sh`), o vigia grava uma marca num arquivo
temporário antes de cortar; o resultado "sem resposta" vem da marca, não do exit; a saída do `git ls-remote` e do
`gh auth status` vai para um arquivo, lido depois do `wait`. O `rc_do_vigia` (heurística pelo relógio) sai.
**Alternativa recusada:** manter a heurística do relógio (LM-005: cobria só o rc ≠ 0).
**Consequência:** `sdd-checar-ambiente` e `sdd-iniciar-repo` mudam de versão; o starter é gerado de novo (decisão do
Roberto).

### Decision 6: o arnês do Windows mora em `tests/apoio.py`

**Contexto:** ~105 quedas vêm do PATH de links simbólicos; outras do `gh` falso sem extensão, do `grep` direto, de nomes
e permissões que o Windows não tem.
**Escolha:** `path_restrito(pasta, ferramentas, python=True)`: fora do Windows, os links de hoje; no Windows, as pastas
reais das ferramentas (e a do Python), conferindo que `claude`/`codex`/`gemini` (e, sem Python, `python`/`python3`/`py`)
não estão nelas. `falso(pasta, nome, corpo)`: o script com shebang e, no Windows, um `nome.bat` que o chama pelo bash. O
produto acha o `gh` por `shutil.which` antes de chamá-lo. `grep` dos testes pelo bash. Pulos novos só por constante de
`apoio.py` com o recurso no motivo (`SEM_NOME_ESPECIAL` passa a citar `"`, `:`, `|` e quebra de linha).
**Alternativa recusada:** `skipIf` de plataforma nos módulos (o `test_windows.py` reprova).

### Decision 7: medir no PR, até 2 rodadas, piso só com 100% verde

**Contexto:** o Roberto escolheu medir só no PR do fim; até 2 rodadas de conserto no PR.
**Escolha:** a tabela antes × depois sai de `medicao-windows.sh` (branch de documentos) sobre os artefatos do run do
PR; com 100% verde, o job `testes-windows` entra no `needs:` da `release` nos 2 workflows e as 4 frases dizem isso; senão
segue informativo e as frases dizem o número novo. O que sobrar vira pendência com o OK do Roberto.

## File Manifest

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 1 | `sdd/bin/{design-lint,report-lint,handoff-lint,skill-lint,kb-dominios,governanca-bloco,sdd-archive}.py`, `.agents/skills/{sdd-release,sdd-kb,sdd-auditoria-harness,sdd-engenharia-reversa-saas,ux-review-builder}/scripts/*.py`, `scripts/{check-versions,gerar-starter,testes-por-modulo}.py`, `scripts/starter/raiz/scripts/*.py`, `bin/adapters/claude/*.py`, `sdd/review/stubs/*.py` | Modify | saída em UTF-8 e `\n` (Decision 1, AT-001) | — |
| 2 | `tests/test_f16w2_saida.py` | Create | guarda do `MANIFEST.txt` e os lints com `PYTHONIOENCODING=cp1252` | 1 |
| 3 | `sdd/bin/lib/python.sh` e a linha de reserva dos scripts de `sdd/bin/`, `sdd/hooks/pre-commit` | Modify | calço do Windows, `PYTHONIOENCODING` na reserva (Decision 2, AT-002) | — |
| 4 | `tests/test_python_resolver.py` (ou o módulo que já testa o `python.sh`) | Modify | modo Windows forçado, Python falso com `\r\n`, exit preservado | 3 |
| 5 | `sdd/bin/{governanca-fronteira,test-baseline,docs-extract-decisions,sdd-fluxo,adversarial-review-gate,adversarial-review,slot}.sh`, `sdd/bin/{sdd-archive,report-lint}.py`, `bin/sdd-open.sh`, `.agents/skills/sdd-higiene-dado/scripts/alarme.sh`, `.agents/skills/sdd-kb/scripts/validate_kb.py`, `sdd/bin/deploy-do-sha.sh` | Modify | uma forma de caminho; `git` sem `cmd.exe`; `gh` por `shutil.which` (Decision 3, AT-003) | 3 |
| 6 | `sdd/hooks/pre-commit`, `bin/sdd-open.sh` | Modify | menos processos por arquivo (Decision 4, AT-004) | 3 |
| 7 | `tests/test_f16w2_processos.py` | Create | a armadilha que conta os programas no commit e no `init` | 6 |
| 8 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh` | Modify | vigia com marca e saída em arquivo (Decision 5, AT-005) | — |
| 9 | `sdd/bin/sdd-drive.sh`, `sdd/bin/playbook-curator.sh` | Modify | autotestes sem nome proibido e sem sobra; trava sem `O_NOFOLLOW` (AT-007) | — |
| 10 | `tests/apoio.py`, `tests/test_windows.py` e os testes do diagnóstico | Modify | `path_restrito`, `falso`, constantes, consertos de teste (Decision 6, AT-006) | 5 |
| 11 | `.agents/skills/*/SKILL.md` das skills tocadas | Modify | bump de versão | 1, 5, 8 |
| 12 | `.github/workflows/{publish-gate,release}.yml`, `README.md`, `README.pt-BR.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md`, `tests/test_release_workflow.py` | Modify | piso e frases com a medição do PR (Decision 7, AT-008) | 10 |
| 13 | `MANIFEST.txt` | Modify | arquivos novos | 2, 7 |

**Total Files:** 13

## Code Patterns

```python
if __name__ == "__main__":
    # F16W2: no Windows, o stdout num pipe (o Git Bash do aluno) é cp1252 e o print troca \n por \r\n: o ✅ e o "ç"
    # quebrariam o script, e o bash que captura a saída veria um \r a mais. Saída em UTF-8 e \n, sempre.
    for _canal in (sys.stdout, sys.stderr):
        try:
            _canal.reconfigure(encoding="utf-8", errors="replace", newline="\n")
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv))
```

```bash
# lib/python.sh — o calço do Windows (Decision 2)
sdd_python_windows() { [ -n "${SDD_PYTHON_FORCA_WINDOWS:-}" ] || [ -r "/proc/$$/winpid" ]; }
printf '#!%s\nset -o pipefail\n%s -X utf8 "$@" | %s -d '"'"'\\r'"'"'\n' "${BASH}" "<py>" "$(command -v tr)" > "${d}/python3"
```

```bash
# pre-commit — nome e extensão sem processo (bash 3.2)
nome="${f##*/}"
shopt -s nocasematch
[[ "${f}" =~ ${TEXTO_RE} ]] && texto=1
shopt -u nocasematch
```

## Testing Strategy

| Camada | O quê | Onde |
|---|---|---|
| Saída | guarda do `MANIFEST.txt`; os lints com `PYTHONIOENCODING=cp1252` imprimem ✅ e saem com o exit esperado (linha de base: vermelho em `ad32fe1`) | `tests/test_f16w2_saida.py` |
| Embutidos | todo `<<'PY'` dos scripts do `MANIFEST.txt` troca a saída (guarda); a linha de reserva exporta `PYTHONIOENCODING`; o calço segue transparente | `tests/test_f16w2_saida.py`, `tests/test_python_resolver.py` |
| Caminhos | `sdd-archive` e `test-baseline` com `ntpath` (o caminho nasce no Python); fronteira e gate no Mac seguem verdes; o resto pelo CI | módulos de cada script + CI |
| Processos | armadilha no PATH: commit de 600 arquivos ≤ 3 programas por arquivo; `init` ≤ metade da `v2.16.0` (linha de base medida antes) | `tests/test_f16w2_processos.py` |
| Recusas do hook | CPF e CNPJ de dígito válido, `.pfx`/`.p12`/`.pem` com chave, `.env`, planilha nova, credencial em claro: recusados pelo hook novo **e** pelo de `ad32fe1` (o teste prova que mede a mesma coisa); `alarme.sh` com `core.hooksPath` em `C:\…` (governança dispensada, DEFINE v1.1) | `tests/test_f16w2_processos.py` + `tests/test_hooks.py` |
| Vigia | os testes de `test_checar.py` seguem verdes no Mac; os 3 do Windows pelo CI | `tests/test_checar.py` + CI |
| Arnês | `test_windows.py` vigia os pulos; o CI do PR prova o resto | CI |
| Emulação | a suíte com `PYTHONUTF8=0 LC_ALL=en_US.ISO8859-1` antes (`ad32fe1`) e depois, numa cópia de `git archive` | evidência do BUILD_REPORT |

## Varredura do playbook (superfícies tocadas)

| LM | Superfície | Tratamento |
|---|---|---|
| LM-001/002 | testes novos de saída, calço e contagem | rodam o código de verdade; linha de base vermelha em `ad32fe1` |
| LM-005 | heurística do vigia | sai: o corte é anunciado pela marca; teste do caso vizinho (resposta lenta que chega antes do teto) |
| LM-006 | Verify Gate na cópia sem `.git` | os testes novos criam o próprio repositório |
| LM-012 | ids de run do CI nos documentos | citar o commit, nunca o id, em arquivo do pacote |
| LM-013 | edições por script nos testes | contagem de `def test_` antes e depois de cada módulo tocado |
| LM-014/015 | subprocess de teste | `encoding="utf-8", errors="replace"` (os testes que caíam com `None`) |
| LM-016/017 | vigia no Windows | Decision 5; o ramo do `kill` segue fora do Windows |
| LM-018 | logs de evidência | por script bash com `rc=$?` |
| LM-029 | "bash" pelo nome | o calço usa `${BASH}`; `test_windows.py` segue barrando |
| LM-030 | executor com `PYTHONIOENCODING` | o executor segue sem a variável; o teste da saída a põe de propósito (`cp1252`) |
| LM-031 | testes de tempo com carga | a prova de lentidão é contagem, não relógio; a suíte em série |

## Segurança

N.A. (DEFINE). O calço só roda o Python que o resolvedor escolheu, pelo caminho absoluto; o vigia só corta a árvore que
o próprio script criou; o `pre-commit` mantém as mesmas recusas (AT-004).

## Next Step

Executar o **sdd-build** com este DESIGN.
