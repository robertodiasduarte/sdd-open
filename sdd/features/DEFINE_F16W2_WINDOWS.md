# DEFINE: F16W2 — Windows, porte das quebras

> As quebras que a 1ª medição inteira do Windows achou (~36% dos testes) são consertadas por causa: primeiro o que o aluno
> no Git Bash vê (saída em cp1252 e com `\r`, caminhos `C:\` × `/c/`, o `pre-commit` e o `init` lentos), depois o que é só
> do arnês de testes; o CI do PR mede de novo e o Roberto decide o piso com os números.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W2_WINDOWS |
| **Date** | 2026-11-15 (v1.4) |
| **Author** | define-agent (worktree `sdd-open-f16w-windows`; branch `feat/f16w2-windows`, de `origin/main` `ad32fe1` = `v2.16.0`, mais o passo 0 em `10dc298`) |
| **Status** | Ready for Design |
| **Clarity Score** | 13/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F16W2_WINDOWS.md` (abordagem A, por causa) |

---

## Problem Statement

Na `v2.16.0`, o job `testes-windows` (Git Bash + Python nativo, a suíte inteira em 16 fatias) mediu **1.324 de 2.076
testes passando (~64%)**, 38 de 82 módulos inteiros verdes e 5 unidades no teto de 600 s. A releitura dos 169 logs
(quatro leituras independentes, 2026-11-14) mostra que mais da metade das quedas é defeito que o aluno no Windows vê:

1. **Saída do Python no Windows:** os scripts Python do pacote escrevem ✅, → e "ç" num stdout cp1252 (o
   `design-lint.py` sai 1 com `UnicodeEncodeError`; o `sdd-drive` cai em cascata), o `print` troca `\n` por `\r\n` (o
   `slot.sh` lê `VALOR\r` e diz que o slot está vazio), e `python3 -I` ignora o `PYTHONIOENCODING` que o `python.sh`
   exporta; o `pre-commit` chama o `report-lint.py` sem UTF-8 e um relatório válido bloqueia o commit.
2. **Caminhos do Windows:** o Python devolve `C:\x` e o Git Bash `/c/x` ou `/tmp/x`: a fronteira da governança recusa
   todo arquivo ("incluir fora do worktree"), o `test-baseline` e o `sdd-archive` juntam caminho com `\` e nunca casam
   com o git, o índice de ADRs sai com links quebrados, o gate da revisão se declara quebrado, o `core.hooksPath`
   absoluto `C:\…` não é reconhecido, o `report-lint` chama o `cmd.exe` por `os.popen` (que não conhece `/dev/null`).
3. **Lentidão no Git Bash:** o `pre-commit` lança ~18 processos por arquivo e o `init` dezenas por arquivo de skill; o
   1º commit depois do `init` (450 a 630 arquivos) passa de 120 s, e 5 unidades de teste batem no teto de 600 s.
4. **O vigia do `checar`:** com o askpass do editor ou o `gh` pendurados, ainda passa do teto (AT-004 da F16W).
5. **Os 4 achados guardados** (AT-005 da F16W) e nomes de arquivo que o Windows proíbe nos autotestes do produto.

O resto é do arnês de testes: PATH restrito montado com links simbólicos (o executável chamado pelo link não acha as
DLLs), comandos falsos sem extensão que o Python nativo não executa, o MSYS expandindo `{11,}` num argumento, JSON e
config do git montados com o caminho cru, nomes e permissões que o Windows não tem.

## Target Users

| User | Pain Point |
|---|---|
| Aluno no Windows (Git Bash + Python nativo) | os lints quebram ao imprimir; o slot diz "vazio" com valor; o 1º commit demora minutos; o `checar` passa do teto |
| Roberto, mantenedor | o job do Windows é vermelho em todo PR e não separa defeito de produto de defeito do teste |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | saída dos scripts Python em UTF-8 e `\n` no Windows, por chamada direta e por bash (inclusive `-I`) |
| **MUST** | caminhos do Windows comparados e escritos numa forma só, nos scripts que a medição acusou |
| **MUST** | `pre-commit` e `init` sem programa externo por arquivo onde um builtin do bash basta |
| **MUST** | o vigia do `checar` cortando askpass e `gh` pendurados no Windows |
| **MUST** | o arnês de testes rodando no Windows: PATH restrito, comandos falsos, `grep` pelo bash, nomes e permissões por constante de `tests/apoio.py` |
| **MUST** | nova medição no CI do PR; o piso e as 4 frases decididos pelo Roberto com ela |
| **SHOULD** | cada causa nova de Windows com candidato ao playbook |
| **COULD** | dividir mais as classes de teste que passam de 300 s no Windows |

---

## Success Criteria

- [ ] Com `PYTHONIOENCODING=cp1252` no ambiente, os 6 lints do `sdd/bin` e os scripts das skills imprimem ✅ e "ç" sem
  erro e com o mesmo exit de hoje; nenhum `.py` do pacote com `__main__` fica sem a troca para UTF-8 (guarda por teste).
- [ ] Todo programa Python embutido nos scripts do pacote troca a saída para UTF-8 e `\n` no início (guarda por teste); o calço segue transparente.
- [ ] O `pre-commit` sobre 600 arquivos novos lança no máximo 3 programas externos por arquivo (contados por armadilha no
  PATH; hoje ~18); o `init --vendors claude,codex` lança no máximo metade dos processos de hoje (mesma contagem).
- [ ] No CI do PR, a proporção de testes que passam no Windows sobe de ~64% para pelo menos 95%, com 0 unidade no teto;
  meta 100% (decisão do Roberto: até 2 rodadas de conserto no PR).
- [ ] Ubuntu e macOS (piso) verdes no CI do PR; Verify Gate verde no Mac.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Ubiquitous | Todo script Python do pacote com `__main__` (fora de `tests/`) **shall** trocar, antes da 1ª escrita, stdout e stderr para UTF-8 com `\n` (e stdin para UTF-8 onde lê a entrada padrão); com `PYTHONIOENCODING=cp1252` no ambiente, os lints (`design-lint`, `report-lint`, `handoff-lint`, `skill-lint`, `kb-dominios`, `governanca-bloco`) e os scripts das skills (`deploy-espera-testes`, `validate_kb`, `kb_normativo`, `collect_evidence`) **shall** imprimir ✅, → e "ç" sem erro e com o exit esperado | test |
| AT-002 | Where | **Where** o bash roda no Windows (Git Bash), todo programa Python embutido num script do pacote (`python3 - <<'PY'`, e os `python3 -c` cuja saída o bash usa como valor) **shall** escrever em UTF-8 e com `\n`, também com `-I`; a linha de reserva (sem a biblioteca) de cada script e o `pre-commit` **shall** exportar `PYTHONIOENCODING=utf-8`; o calço do `python.sh` **shall continue to** ser transparente (`exec`) e só existir quando o `python3` do PATH não serve, sem mudar o modo do Python que o comando de teste do projeto usa | test |
| AT-003 | Ubiquitous | No Windows, os scripts que a medição acusou (`governanca-fronteira.sh`, `test-baseline.sh`, `sdd-archive.py`, `docs-extract-decisions.sh`, `sdd-fluxo.sh`, `adversarial-review-gate.sh`, `hooks_path_e_nosso` em `sdd-open.sh` e `alarme.sh`, `validate_kb.py`, `report-lint.py`) **shall** comparar e escrever caminhos numa forma só (`/` como separador; `C:\…` e `/c/…` reconhecidos como absolutos) e **shall** achar a raiz do git sem passar pelo `cmd.exe` | test (Mac, com `ntpath` onde o caminho é do Python) + log do CI Windows |
| AT-004 | Unwanted | **If** um commit leva centenas de arquivos novos, **then** o `pre-commit` **shall** lançar no máximo 3 programas externos por arquivo (hoje ~18) e **shall continue to** recusar o commit com CPF ou CNPJ de dígito válido, `.pfx`/`.p12`/`.pem` com chave privada, `.env`, planilha nova e credencial em texto claro, como na `v2.16.0` (teste negativo de cada recusa, rodado também sobre o hook antigo); o `alarme.sh` **shall** reconhecer o próprio `core.hooksPath` também na forma `C:\…`; **if** o `init` instala as skills, **then** **shall** lançar no máximo metade dos processos que a `v2.16.0` lança | test (contagem por armadilha no PATH) |
| AT-005 | Unwanted | **If** o `ls-remote` do `checar.sh` (modo normal ou `--frente`) ou o `gh auth status` do `gh_estado` não respondem, inclusive com askpass ou neto segurando a saída, **then** o vigia **shall** anunciar o próprio corte (o resultado não depende do exit de um processo morto) e o script **shall** responder em até 12 s (14 s no Windows, onde a partida do Git Bash custa mais: CI do PR, 12,25 s com o corte certo); `gh_estado` **shall continue to** ser igual em `checar.sh` e `inventario.sh` | test (Mac) + log do CI Windows |
| AT-006 | Ubiquitous | O arnês **shall** rodar no Windows sem defeito próprio: PATH restrito por um ajudante de `tests/apoio.py` (pastas reais no Windows, links fora dele); comando falso chamável pelo Python nativo (o produto acha o `gh` por `shutil.which`); `grep` pelo bash; JSON e config do git com o caminho escapado ou com `/`; todo pulo de plataforma só por constante de `tests/apoio.py`, com o recurso nomeado no motivo | test + log do CI Windows |
| AT-007 | Unwanted | **If** o autoteste do `sdd-drive` ou do `playbook-curator` roda no Windows, **then** **shall** sair verde sem nome de arquivo proibido e sem deixar a pasta temporária; **if** a trava do `sdd-drive` é um link, **then** **shall** recusar sem criar arquivo fora, também sem `O_NOFOLLOW`; cada um dos 4 achados guardados (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`) **shall** passar no job do Windows ou ser pulado por constante com motivo | test + log do CI Windows |
| AT-008 | Event-driven | **When** o CI do PR mede o Windows, nenhuma unidade **shall** bater no teto de 600 s e a proporção de testes que passam **shall** ser registrada no BUILD_REPORT por módulo (antes e depois); **when** o Roberto decide o piso, os 2 workflows e as 4 frases de Windows (README EN/PT, quickstart EN/PT) **shall** refletir só o que a última medição provou | test (texto) + log do CI Windows |
| AT-009 | Non-regression | A suíte **shall continue to** passar no Ubuntu e no piso do macOS (bash 3.2, Python 3.9.6), e os scripts de `sdd/bin/` e das skills **shall continue to** dar a mesma saída no macOS e no Linux | test |

While: N.A. — nenhum requisito depende de um estado contínuo além do "rodando no Windows", coberto pelo Where do AT-002.

---

## Clarifications

### Session 2026-11-14

- [x] (escopo) As 8 causas do prompt da frente, em ordem de peso, e o que a releitura dos logs achou a mais (Problem Statement); o piso e as 4 frases depois da medição (prompt da frente, Roberto).
- [x] (escopo) A causa (2) do prompt ("`settings.json` com caminho Windows sem escape") **não é do produto**: o `merge_claude_settings` grava por `json.dump`; o JSON inválido é montado pelo ajudante `payload()` de `tests/test_claude_adapter.py` (linha 59). Entra no AT-006.
- [x] (restrições) **Medir só no PR do fim** (Roberto, 2026-11-14, perguntado de novo nesta frente). Até lá, a causa da saída se prova no Mac por `PYTHONIOENCODING=cp1252` (ou `PYTHONUTF8=0 LC_ALL=en_US.ISO8859-1`); o resto, pelo log do CI do PR.
- [x] (sinal de conclusão) No PR, se sobrar quebra, consertar e medir de novo até 2 vezes (cada push com a frase); o job só entra no `needs:` com 100% verde; senão segue informativo com o número novo (Roberto, 2026-11-14).
- [x] (integrações) Se uma skill do starter mudar (`sdd-checar-ambiente`, `sdd-release`, `sdd-kb`, `sdd-auditoria-harness`, `sdd-higiene-dado`…), o starter é gerado de novo pela tag e publicado com o OK próprio do Roberto (Roberto, 2026-11-14).
- [x] (escopo, AT-001) Exceção: `.agents/skills/sdd-engenharia-reversa-saas/scripts/validate_reverse.py` fica igual ao pacote de origem da F21 (SHA-256 conferido por `test_f16w2_saida`/`test_f21_textos`, com `-text` no `.gitattributes`) e não recebe a troca da saída; todo caractere que ele escreve cabe no cp1252, então ele não quebra no Windows, mas lá a saída sai em cp1252, não em UTF-8 ("Inventário" aparece trocado no Git Bash) — limite aceito enquanto o pacote de origem não mudar (avaliador, ciclo 1, A2; ciclo 2, A1).
- [x] (dados) A amostra é o CI `windows-latest` e os 169 logs da 1ª medição; não há máquina Windows. Nada da RDD.
- [x] (UX) Sem interface: UX review pulado.

### Session 2026-11-14 (governança)

- [x] (governança) dispensada — o revisor em contexto novo (fronteira conferida, bloco válido) achou o tema pelo sentido (o AT-004 reescreve o `pre-commit` que recusa CPF/CNPJ, certificado e credencial; o AT-003 mexe no `alarme.sh` da `sdd-higiene-dado`) e devolveu `PADRAO_AUSENTE`; o Open não guarda dado de negócio e um `sdd/GOVERNANCA_PADRAO.md` iria no pacote para o aluno. O ponto real do revisor entrou no AT-004: as recusas continuam, com teste negativo (Roberto, 2026-11-14).

### Segurança

- [x] N.A. para a feature: sem login, rota, dado de terceiros, banco nem chamada paga. O calço do Python e o vigia só tocam processos que o próprio script criou; o `pre-commit` mais rápido mantém as mesmas recusas (AT-004).

---

## Verify Gate

```yaml
verify_gate:
  kind: test
  cmd: "T=$(mktemp -d) && git archive HEAD | tar -x -C $T && PUBLISH_GATE_MODE=ci bash scripts/publish-gate.sh $T && cd $T && SDD_TEST_BASH=/bin/bash /usr/bin/python3 -B -m unittest discover -s tests -p 'test_*.py'"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

Cobertura: AT-001 em `tests/test_f16w2_saida.py` (guarda sobre os `.py` do `MANIFEST.txt` e os lints com
`PYTHONIOENCODING=cp1252`); AT-002 em testes do `python.sh` com o modo Windows forçado por variável de teste e um Python
falso que escreve `\r\n`; AT-003 em testes por script (no Mac, `ntpath` onde o caminho nasce no Python); AT-004 por
armadilha no PATH que conta os programas lançados; AT-005 pelos testes de `test_checar.py`; AT-006 e AT-007 em
`test_windows.py` e nos módulos tocados; AT-008 em testes de texto sobre workflows e frases; AT-009 nas suítes existentes.
O Windows de verdade (AT-003, AT-005 a AT-008) se prova pelo log do CI do PR, fora deste gate.

---

## Out of Scope

- WSL; PowerShell sem Git Bash; paralelizar a suíte no Ubuntu e no macOS.
- Skills com `python3` no texto que o aluno digita (o atalho da Store): só se a medição mostrar teste que dependa disso.
- As pendências da F17b (version gate do starter, `--conferir` com `--paths`) e o teto do Ubuntu (33 a 41 min de 45).
- O repositório privado.

## Constraints

- bash 3.2 e Python 3.9 stdlib; pulo de plataforma só por constante de `tests/apoio.py` (`test_windows.py` vigia).
- `MANIFEST.txt` a cada arquivo novo; sem número de 11 dígitos no pacote (LM-012); "bash" sempre pelo caminho (LM-029).
- `corta` e `gh_estado` iguais em `checar.sh` e `inventario.sh` (`test_f16_textos.py` compara).
- O executor dá ao teste o ambiente do aluno, sem `PYTHONIOENCODING` (LM-030); suíte em série (LM-031).
- Contagens fixadas em testes: 22 skills; 34 perguntas em 29 arquivos do `sdd-decisoes-lint`; versões de skill em
  `test_f16_textos.py`; o build gerado do starter em 499 de 500 linhas.
- Teto do método: 3 rodadas de revisão, 2 ciclos do avaliador; acima disso, pergunta ao Roberto.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `sdd/bin/` (scripts e `lib/python.sh`), `sdd/hooks/pre-commit`, `bin/sdd-open.sh`, `bin/lib/`, `.agents/skills/*/scripts/`, `scripts/`, `tests/`, `.github/workflows/` (só o piso), README e quickstart | `scripts/` é do mantenedor; o `init` não o copia |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | só os 2 workflows do CI, se o piso mudar |
| **LLM Prompts** | false | nenhum prompt de runtime |
| **CONTEXTO de domínio** | nenhum (pulado: o Open não tem `sdd/patterns/dominio.md`) | — |
| **Governança** | dispensada — revisor fresco devolveu `PADRAO_AUSENTE` (o tema é o `pre-commit` que barra CPF/CNPJ, certificado e credencial, não dado de negócio); as recusas viraram teste negativo no AT-004 | Roberto, 2026-11-14 |
| **Segurança** | N.A. — sem login, rota pública, dado de terceiros, envio de arquivo, banco nem chamada paga | 2026-11-14 |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | (superada na v1.2) o calço com `-X utf8` vazava para o comando de teste do aluno; a troca vai no próprio programa | — | [x] |
| A-002 | (derrubada pelo raio de impacto: o curador devolve o playbook byte a byte, CRLF incluso) nada tira `\r` de fora; cada programa escreve `\n` | — | [x] |
| A-003 | No Windows, o executável chamado por link simbólico não acha as DLLs ao lado (por isso o `dirname` "existe" e devolve vazio) | o ajudante do PATH restrito precisa de outra forma; o CI do PR diz | [ ] |
| A-004 | A lentidão do `pre-commit` e do `init` é o custo de processo do Git Bash, não um travamento | as unidades no teto pedem outra causa; a contagem e o CI dizem | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | medido: 169 logs, quatro leituras com arquivo:linha |
| Users | 3 | 2 papéis com a dor de cada um |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 2 | a proporção final só o CI do PR diz |
| Scope | 2 | o piso depende da medição |
| **Total** | **13/15** | |

## Open Questions

- O piso e as 4 frases: decisão do Roberto com a medição do PR (AT-008).

## Revision History

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-11-14 | primeira versão, do brainstorm e da releitura dos 169 logs |
| 1.1 | 2026-11-14 | governança dispensada pelo Roberto; AT-004 com as recusas do `pre-commit` e do alarme como teste negativo |
| 1.4 | 2026-11-15 | AT-005: 14 s no Windows (medição do PR #31) |
| 1.3 | 2026-11-14 | exceção do arquivo congelado da F21 no AT-001 (avaliador, ciclo 1, A2) |
| 1.2 | 2026-11-14 | AT-002 revisto pelo raio de impacto: o calço volta a ser transparente; UTF-8 e `\n` em cada Python embutido; `rc_do_vigia` saiu das Constraints |

## Next Step

Executar o **sdd-design** com este DEFINE.
