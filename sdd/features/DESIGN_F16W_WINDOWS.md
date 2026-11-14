# DESIGN: F16W — Windows, porte da suíte

> Arquitetura e especificação técnica numa passada só.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W_WINDOWS |
| **Date** | 2026-11-14 |
| **Author** | design-agent (worktree `sdd-open-f16w-windows`) |
| **DEFINE** | `sdd/features/DEFINE_F16W_WINDOWS.md` v1.0 |
| **Status** | Ready for Build (v1.3, revisto no Build: unidade = classe em partes de até 8 testes, 16 fatias, ambiente do aluno na unidade, UTF-8 e bash pelo caminho) |

---

## Architecture Overview

```text
 PR / push main ─► publish-gate.yml / release.yml
                     ├─ gate (ubuntu) · testes-macos (piso)        ← sem mudança
                     └─ testes-windows  strategy.matrix fatia ∈ {1..16}, fail-fast: false
                          ├─ Git Bash + Python nativo afirmados
                          ├─ publish-gate.sh          (só na fatia 1)
                          ├─ scripts/testes-por-modulo.py --fatia i/16 --teto-unidade 600 --saida $RUNNER_TEMP/tpm
                          │     unidade (modulo.Classe) → processo próprio (python -B -m unittest -v u), saída num arquivo
                          │     teto ⇒ taskkill /F /T (Windows) | killpg (POSIX) ⇒ TETO
                          └─ upload-artifact (sempre, também no vermelho): tpm/*.log + resumo.tsv

 checar.sh  alcance() / gh_estado()  (gh_estado igual em inventario.sh)
   vigia: ( sleep 10; corta TERM p q; sleep 1; corta KILL p q ) &
   corta(): /proc/<pid>/winpid legível (só existe no Git Bash/MSYS) ⇒ taskkill /F /T /PID <winpid>; senão kill -SIG -- -<pid>
   rc: no Windows, wait devolve o código do TerminateProcess ⇒ rc≠0 com SECONDS-t0 ≥ 10 vira 137 (o vigia cortou)
```

## Key Decisions

### Decision 1: executor por módulo em `scripts/`, stdlib

**Contexto:** `unittest discover` num job só não tem teto por módulo nem diz qual módulo pendurou; a 1ª medição
morreu aos 90 min sem esse dado.
**Escolha:** `scripts/testes-por-modulo.py`; cada módulo é um `python -B -m unittest -v <m>` com `cwd=tests`;
saída num arquivo temporário (um neto vivo segurando um pipe prenderia a leitura, o mesmo defeito do vigia).
**Alternativas rejeitadas:** `pytest-xdist`/`pytest-timeout` (dependência fora da stdlib; o pacote promete só
stdlib); `timeout` do coreutils (não existe igual nos 3 sistemas, e não mata a árvore no Windows).
**Consequências:** o executor também roda no Mac (linha de base) e serve de instrumento no Build.

### Decision 2: unidade = classe de teste; fatias gulosas e estáveis pelo nº de testes

**Escolha (revista no Build):** a unidade é a classe (`modulo.Classe`, pelo id dos testes que o `unittest` carrega,
com os herdados; a classe importada de outro módulo conta uma vez, no módulo dela); módulo que não importa vira uma
unidade inteira (o erro aparece). Ordena as unidades por (-testes, nome) e põe cada uma na fatia de menor carga
(empate: menor índice). **Por quê a revisão:** na linha de base do Mac com 6 módulos ao mesmo tempo, o
`test_sdd_open` inteiro passou de 900 s; no Windows, sozinho, comeria a fatia. Em classes, ele vira 6 unidades.
**Alternativa rejeitada:** pesos por tempo medido (arquivo a manter que muda a cada medição); módulo como unidade.
**Consequências:** um processo por unidade (o custo de partida do Python). **Revisto de novo (avaliador, ciclo 1):** classe com mais de 8 testes vira partes `Classe[ideN]` de tamanho parecido (o `test_sdd_open.Projeto` sozinho deu ≥ 450 s no Mac com carga; no Windows bateria o teto de 600 s e a medição única do PR perderia o dado; com 12, o avaliador do ciclo 2 mostrou que `test_claude_adapter.Projeto`, 154 s no Mac, ainda bateria); 471 unidades, ~29 por fatia. **E a unidade vê o ambiente do aluno** (raio de impacto): o executor não põe `PYTHONIOENCODING` nela e tira o que viria de fora, como o `Sandbox`; só a leitura da saída dela é UTF-8.

### Decision 3: N = 16 fatias, teto do job 30 min, teto por unidade 600 s, em série

**Contexto:** 2.164 testes; no Mac, a soma dos módulos com carga deu ~53 min; o Windows é várias vezes mais lento.
**Escolha (revista no Build, era 8, depois 12):** 16 fatias; teto do job 30 (o de hoje); 600 s por unidade; as unidades de uma
fatia em série (`--paralelo 1`): com 6 ao mesmo tempo no Mac, 2 testes de tempo do `test_deploy_do_sha` caíram e
passaram sozinhos.
**Consequências:** o mesmo job nos 2 workflows (o teste compara o bloco inteiro); 16 + Ubuntu + macOS cabem no
limite de 20 jobs simultâneos da conta no PR (no push da `main` os 2 workflows rodam juntos e o resto espera na fila).

### Decision 4: o vigia do `checar.sh` no Windows corta a árvore por `taskkill`

**Contexto:** LM-016: `kill -- -<pgid>` não alcança o `git.exe` nativo nem os netos no Git Bash; 5 testes pulados.
**Escolha:** função `corta <SINAL> <pid>...` dentro do bloco `# ── gh e instalação por sistema (F16)` (que existe
igual em `checar.sh` e `inventario.sh`): com `/proc/<pid>/winpid` legível (o arquivo só existe no Git Bash/MSYS, então
ele mesmo é o sinal do Windows, sem `uname`), `MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' taskkill /F /T /PID <winpid>`; senão, o `kill -SIG -- -<pid>`
de hoje. `alcance()` e `gh_estado()` passam a chamar `corta` no vigia e na limpeza. Como o `taskkill` não devolve
143/137 ao `wait`, no Windows um rc ≠ 0 depois de ≥ 10 s (`SECONDS`) vira 137, e a classificação de hoje segue igual.
**Alternativas rejeitadas:** saída em arquivo e abandonar o processo (deixaria `git.exe` vivo no computador do
aluno); marca em arquivo para o "cortou" (o `checar` é só leitura; um temporário a mais sem necessidade).
**Consequências:** `checar-ambiente` e `iniciar-repo` ganham bump patch; o starter recebe pela próxima geração (OK
próprio do Roberto). Fora do Windows o caminho é o mesmo (os testes de hoje provam). A1 do DEFINE se prova no CI.

### Decision 5: destino das quebras por causa, nunca por módulo

**Escolha:** a 1ª medição é agrupada por causa (decodificação, caminho `C:\`, fim de linha, interpretador, recurso
ausente, defeito do produto); cada causa tem um conserto (no teste ou no produto, com linha de base vermelha
quando é produto) ou uma constante de pulo em `tests/apoio.py` com o motivo do recurso.
**Consequências:** constante nova ⇒ `test_windows.py::test_cada_constante_tem_motivo_que_nomeia_o_recurso` ganha
a linha.

### Decision 6: sem medição intermediária, as causas achadas por varredura (decisão do Roberto: medir só no PR)

**Escolha:** no Build entram só as causas que se acham e se provam no Mac: subprocess em modo texto sem `encoding`
(LM-014) no produto e nos testes, com um teste que vigia pelo `MANIFEST.txt`; `"bash"` chamado pelo nome a partir do
Python (no Windows, o `CreateProcess` acha o `bash.exe` do WSL em `System32` antes do `PATH`); teste que manda sinal
ao grupo (`os.killpg`) pula por `SEM_SINAL`. Fora: os arquivos que vão ao starter como estão (`scripts/starter/raiz/`)
e 2 de skill que leem só ASCII (lista com motivo no teste). O resto da medição sai no CI do PR.

---

## File Manifest

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 1 | `scripts/testes-por-modulo.py` | Create | executor por módulo (AT-001, AT-002) | — |
| 2 | `tests/test_testes_por_modulo.py` | Create | unidades por classe, fatias, contagem, teto com neto, exits | 1 |
| 3 | `.github/workflows/publish-gate.yml` | Modify | `testes-windows` com matriz de 16 fatias e artefato (AT-003) | 1 |
| 4 | `.github/workflows/release.yml` | Modify | o mesmo job (AT-003) | 1 |
| 5 | `tests/test_release_workflow.py` | Modify | o job do Windows nos 2 workflows: matriz, N igual, executor, artefato por SHA, fora do `needs:` | 3, 4 |
| 6 | `.agents/skills/sdd-checar-ambiente/scripts/checar.sh` | Modify | `corta`, vigia de `alcance` e `gh_estado` (AT-004) | — |
| 7 | `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh` | Modify | a cópia do bloco do `gh` | 6 |
| 8 | `.agents/skills/sdd-checar-ambiente/SKILL.md`, `.agents/skills/sdd-iniciar-repo/SKILL.md` | Modify | bump patch (1.5.2, 1.2.1) | 6, 7 |
| 9 | `tests/test_checar.py` | Modify | os 5 `SEM_SINAL` saem; teste do ramo Windows de `corta` | 6 |
| 10 | `tests/*` e `sdd/bin/*` acusados pela medição | Modify | consertos por causa (Decisão 5) | medição |
| 11 | `tests/apoio.py`, `tests/test_windows.py` | Modify | constantes novas, se a medição pedir; `ACHADOS` | medição |
| 12 | `README.md`, `README.pt-BR.md`, `docs/quickstart.md`, `docs/pt-BR/quickstart.md` | Modify | frase do piso (AT-007) | decisão do Roberto |
| 13 | `MANIFEST.txt` | Modify | arquivos novos | 1, 2 |
| 14 | `sdd/bin/{adversarial-review,adversarial-review-gate,eval-agree,eval-revisores,playbook-curator,sdd-fluxo}.sh`, `sdd/bin/adapters/openrouter.sh`, `sdd/review/stubs/*.py`, `bin/adapters/claude/*.py`, `scripts/check-versions.py` e 9 testes | Modify | UTF-8 e bash pelo caminho (Decision 6) | — |

**Total Files:** 14 linhas (item 14 com 13 arquivos de produto; item 10 vazio até a medição do PR)

## Code Patterns

```bash
# dentro do bloco do gh (igual em checar.sh e inventario.sh)
corta() {   # corta SINAL pid...: o grupo (POSIX) ou a árvore do Windows
  local s="$1" p w; shift
  for p in "$@"; do
    [ -n "${p}" ] || continue
    if [ "${SDD_SO:-$(sistema)}" = windows ] && [ -r "/proc/${p}/winpid" ]; then
      w="$(cat "/proc/${p}/winpid" 2>/dev/null)"
      [ -n "${w}" ] && MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' taskkill /F /T /PID "${w}" >/dev/null 2>&1
    else
      kill -"${s}" -- "-${p}" 2>/dev/null
    fi
  done
}
```

```yaml
  testes-windows:
    strategy:
      fail-fast: false
      matrix:
        fatia: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    ...
      - name: Unit tests by module (slice ${{ matrix.fatia }}/16, Git Bash + native Python)
        env:
          PYTHONUNBUFFERED: '1'
        run: python -B scripts/testes-por-modulo.py --fatia "${{ matrix.fatia }}/16" --teto-unidade 600 --saida "$RUNNER_TEMP/tpm"
      - uses: actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2
        if: always()
```

## Testing Strategy

| Camada | O quê | Onde |
|---|---|---|
| Executor | fatias disjuntas e completas, estáveis; `--lista`; contagem de OK/FAILED/skipped; TETO com neto segurando a saída em < teto + 30 s; exits 64 | `tests/test_testes_por_modulo.py` (pasta de testes falsa) |
| Workflows | matriz, N igual, executor chamado, artefato fixado por SHA, `fail-fast: false`, publish-gate só na fatia 1, Windows fora do `needs:` (até o piso) | `tests/test_release_workflow.py` |
| Vigia | Mac: os 5 testes de rede pendurada seguem verdes (corte por grupo; sem `/proc`, o ramo do `taskkill` nunca roda aqui); Windows real: os 5 testes no CI do PR | `tests/test_checar.py` + log do CI |
| Porte | cada causa da medição com um teste que a cobre ou uma constante | log do CI, BUILD_REPORT |

## Varredura do playbook (superfícies tocadas)

| LM | Superfície | Tratamento |
|---|---|---|
| LM-002 | testes novos | linha de base vermelha (o teste do executor contra a ausência do script; os 5 testes do vigia no Windows contra o job anterior, que os pulava) |
| LM-005 | heurística nova (rc pelo relógio) | só no Windows; fora dele, o rc de hoje; teste do caso vizinho (rc 0 depois de 10 s não vira corte) |
| LM-006 | executor no Verify Gate | o teste roda na cópia de `git archive` (sem `.git`): o executor não usa git |
| LM-012 | id de run do CI | citar o commit, nunca o id do run, em arquivo do pacote |
| LM-013 | edições por script em testes | contagem de `def test_` antes e depois |
| LM-014/015 | subprocess de teste | `encoding="utf-8"` e `PYTHONIOENCODING` (o executor exporta) |
| LM-016 | vigia | é o conserto desta frente |
| LM-017 | fallback | o ramo do `kill` quando `/proc/<pid>/winpid` falta: o log do Windows prova que o ramo do `taskkill` rodou (o teste passa em ≤ 12 s, o que o `kill` não conseguia) |
| LM-018 | logs de evidência | gravados por script bash com `rc=$?` |

## Segurança

N.A. (DEFINE). O `taskkill` só recebe o pid do Windows de um filho que o próprio script criou; a action nova é
fixada por SHA; o token do job segue só leitura.

## Next Step

Executar o **sdd-build** com este DESIGN.
