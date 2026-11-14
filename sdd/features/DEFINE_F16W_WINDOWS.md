# DEFINE: F16W — Windows, porte da suíte

> A suíte inteira do pacote passa a rodar no Windows do aluno (Git Bash + Python nativo), módulo a módulo, em fatias
> paralelas que cabem no teto do CI; cada quebra termina em conserto, pulo com motivo ou pendência aceita; o teto do
> `checar.sh` passa a valer no Windows; e o Roberto decide o piso com os números.

## Metadata

| Attribute | Value |
|---|---|
| **Feature** | F16W_WINDOWS |
| **Date** | 2026-11-14 (v1.2) |
| **Author** | define-agent (worktree `sdd-open-f16w-windows`; branch `feat/f16w-windows`, de `origin/main` `97503a7` = `v2.15.0`, mais o passo 0 em `0475445`) |
| **Status** | Ready for Design |
| **Clarity Score** | 13/15 |
| **Entrada** | `sdd/features/BRAINSTORM_F16W_WINDOWS.md` (abordagem A, fatias paralelas) |

---

## Problem Statement

O README e o quickstart dizem que o Windows (Git Bash/WSL) está "sem teste automático": desde a F16, o job
`testes-windows` roda só os 5 módulos do caminho do aluno (144 testes, ~4 min). Os outros 77 módulos (~2.000 testes)
nunca rodaram no Windows; a única tentativa, num job só, foi cancelada aos 90 min com 282 testes feitos e 156
quebras, sem dizer qual módulo pendurou. O aluno contador, que usa muito Windows, é o primeiro testador do resto. E um
defeito conhecido do produto fica escondido por pulo: no Git Bash o vigia do `checar.sh` (sinal ao grupo de
processos) não corta ssh, askpass ou rede pendurados, então o diagnóstico e o pré-voo da `sdd-new-session` podem
passar do teto de 10 s (LM-016). Os 4 achados guardados das revisões (`tasklist`, `report-lint`, `sdd-archive`,
`O_NOFOLLOW`) seguem sem medição.

## Target Users

| User | Pain Point |
|---|---|
| Aluno no Windows (Git Bash + Python nativo) | usa scripts que nunca rodaram no sistema dele; o `checar` pode travar sem rede |
| Roberto, mantenedor | não sabe o que quebra no Windows nem tem dado para decidir o piso |
| Quem revisa um PR | um vermelho do Windows hoje não diz o módulo, e a suíte inteira não cabe no teto |

---

## Goals

| Priority | Goal |
|---|---|
| **MUST** | executor por módulo (`scripts/testes-por-modulo.py`), com a classe de teste como unidade (classe com mais de 8 testes em partes): fatias estáveis e completas, teto por unidade que mata a árvore, tabela por unidade, exits 0/1/64 |
| **MUST** | job `testes-windows` dos 2 workflows com a suíte inteira em fatias paralelas pelo executor, saída de cada módulo como artefato |
| **MUST** | teto do `checar.sh` (modo normal, `--frente`) e do `gh_estado` valendo no Windows; os 5 testes `SEM_SINAL` de `test_checar.py` rodando lá |
| **MUST** | os 4 achados guardados medidos no Windows, com destino (passa, conserto com teste, pulo com motivo) |
| **MUST** | toda quebra da medição com destino: conserto de produto com teste, conserto do teste, pulo por constante de `tests/apoio.py` com motivo, ou pendência com o OK do Roberto |
| **MUST** | o piso decidido pelo Roberto com os números, aplicado nos 2 workflows e nas frases de Windows (README e quickstart, EN e PT) |
| **SHOULD** | tabela por módulo antes (1ª medição) e depois (última) no BUILD_REPORT, com tempo por fatia |
| **COULD** | causas novas de Windows que mordam viram candidatos ao playbook |

---

## Success Criteria

- [ ] `python3 scripts/testes-por-modulo.py --lista --fatia I/N`, para N de 1 a 8, devolve fatias disjuntas cuja união é a lista de todas as unidades (que cobrem os 82+ módulos), iguais em duas execuções.
- [ ] Uma unidade que pendura com um neto segurando a saída sai `TETO` dentro de teto + 60 s, o neto morre junto, e as outras unidades da fatia seguem.
- [ ] No CI do PR: o job do Windows roda todas as fatias e cada fatia termina dentro do teto do job; a tabela por módulo está no log.
- [ ] Os 5 testes de rede pendurada de `test_checar.py` sem `SEM_SINAL`, verdes no Windows com `t ≤ 12 s`.
- [ ] Os 4 testes de `ACHADOS` (`test_windows.py`) verdes ou pulados por constante com motivo no log do Windows.
- [ ] Última medição do Windows: 0 módulo `FALHOU`, `ERRO` ou `TETO` dentro do piso; cada módulo fora do piso com o motivo na ficha.
- [ ] Ubuntu e macOS (piso) verdes no CI do PR, dentro dos tetos; Verify Gate verde no Mac.
- [ ] As 4 frases de Windows (README EN/PT, quickstart EN/PT) dizem só o que a última medição provou.

---

## Acceptance Tests

| ID | Padrão | Critério (EARS) | Gate (`kind`) |
|---|---|---|---|
| AT-001 | Ubiquitous | O executor `scripts/testes-por-modulo.py` **shall** dividir os testes dos `test_*.py` da pasta em unidades (a classe de teste, pelo id que o `unittest` carrega, cada teste contado uma vez; classe com mais de 8 testes em partes `Classe[ideN]`; módulo que não importa = uma unidade) e as unidades em N fatias disjuntas que juntas cobrem todas, iguais a cada execução (maior primeiro, na fatia mais leve); `--lista` **shall** imprimir as unidades da fatia e sair 0; ao rodar, **shall** imprimir uma linha por unidade com estado (`OK`, `FALHOU`, `ERRO`, `TETO`), testes, falhas, erros, pulados e segundos, os testes que caíram, um total e `RESULTADO: VERDE` (exit 0) ou `RESULTADO: VERMELHO` (exit 1); com `--saida DIR`, **shall** gravar a saída de cada unidade e um `resumo.tsv`; o próprio stdout **shall** ser UTF-8 | test |
| AT-002 | Unwanted | **If** uma unidade passa do `--teto-unidade`, inclusive com um neto vivo segurando a saída, **then** o executor **shall** matar a árvore da unidade, neto incluído (no Windows por `taskkill /T`), marcar `TETO`, mostrar as últimas linhas da saída e seguir para a próxima, sem esperar o neto; **if** a chamada é inválida (fatia fora de 1..N ou N acima de 1000, número que não é número ou não é finito, módulo ou unidade inexistente, pasta sem testes, argumento desconhecido, seleção vazia ao rodar), **then** **shall** sair 64 com `RESULTADO: ERRO DE USO` sem rodar nada | test |
| AT-003 | Ubiquitous | O job `testes-windows` de `publish-gate.yml` e de `release.yml` **shall** rodar em `windows-latest`, com Git Bash e Python nativo afirmados, uma `strategy.matrix` de fatias com `fail-fast: false`, cada uma pelo executor com `--fatia ${{ matrix.fatia }}/N`, teto por job e por unidade, e a pasta `--saida` publicada como artefato do run por uma action fixada por SHA; o número de fatias **shall** ser o mesmo nos 2 workflows; o publish-gate **shall** rodar em uma só das fatias | test |
| AT-004 | Unwanted | **If** o `ls-remote` do `checar.sh` (modo normal ou `--frente`) ou o `gh auth status` do `gh_estado` (em `checar.sh` e na cópia de `inventario.sh`) não respondem, inclusive com um neto (ssh, askpass) segurando a saída, **then** no Windows o vigia **shall** cortar a árvore pelo pid do Windows (`taskkill /F /T`) e o script **shall** responder em até 12 s com a mensagem de hoje; fora do Windows, o corte por grupo de processos **shall continue to** valer; os 5 testes de rede pendurada de `tests/test_checar.py` **shall** rodar sem `SEM_SINAL` e passar no job do Windows | test (Mac) + log do CI Windows |
| AT-005 | Ubiquitous | Cada um dos 4 achados guardados (`tasklist` do `sdd-drive.sh`, `report-lint`, `sdd-archive`, trava sem `O_NOFOLLOW`) **shall** ter o teste que o mede rodando no job do Windows, com resultado no log: passa, ou conserto de produto com teste, ou pulo por constante de `tests/apoio.py` com o motivo do recurso; o mapa `ACHADOS` de `tests/test_windows.py` **shall** citar só testes que existem | log do CI Windows |
| AT-006 | Unwanted | **If** um teste quebra no Windows, **then** o destino **shall** ser um destes, registrado no BUILD_REPORT por causa: conserto do produto (com teste que falha antes), conserto do teste, pulo por uma constante de `tests/apoio.py` cujo motivo nomeia o recurso que o Windows não tem, ou pendência com o OK do Roberto; nenhum `skipIf`/`skipUnless` de plataforma **shall** ficar fora de `tests/apoio.py` (`test_windows.py` continua a vigiar) | test + log do CI Windows |
| AT-007 | Event-driven | **When** o Roberto decide o piso, os 2 workflows **shall** refletir a decisão (módulos do job e, se bloqueante, `testes-windows` no `needs:` do job `release`, sem `continue-on-error`), e as frases de Windows de `README.md`, `README.pt-BR.md`, `docs/quickstart.md` e `docs/pt-BR/quickstart.md` **shall** dizer só o que a última medição provou | test |
| AT-008 | Non-regression | A suíte **shall continue to** passar no Ubuntu e no piso do macOS (bash 3.2, Python 3.9.6); os testes do caminho do aluno **shall continue to** passar no Windows; os scripts de `sdd/bin/` e das skills **shall continue to** dar a mesma saída no macOS e no Linux | test |

While: no AT-004 (enquanto a rede não responde). Where: no AT-002 e no AT-004 (no Windows; fora dele).

Fora do gate do Mac, com evidência no BUILD_REPORT: o log do CI do Windows (AT-003 a AT-006 rodando de verdade), a
tabela por módulo da 1ª e da última medição, e a decisão do piso pelo Roberto.

---

## Clarifications

### Session 2026-11-14

- [x] (escopo) Medir a suíte inteira módulo a módulo; prioridade no teto do `checar` e nos 4 achados; o piso é do Roberto, com os números (plano, linha F16W).
- [x] (restrições) Push da branch só com "sdd-open autorizado"; passo 0: "ainda não" — perguntar antes da 1ª medição.
- [x] (restrições, 2ª pergunta depois do Design) **Medir só no PR do fim** (Roberto): nenhuma medição intermediária no Windows. AT-003 a AT-006 se provam pelo log do CI do PR da release; o que a medição acusar entra nesta frente só se o Roberto autorizar mais pushes na release, senão vira pendência com a tabela por módulo.
- [x] (sinal de conclusão) Regra de parada: depois da 1ª medição inteira, se o que sobra não couber na sessão, o corte vai ao Roberto.
- [x] (corte e piso, Roberto, 2026-11-14, com a 1ª medição do CI do PR #30: 1.324 de 2.076 testes passam, 38 de 82 módulos inteiros verdes, ~6 causas) **Publicar agora:** o job do Windows segue informativo (fora do `needs:`) com a suíte inteira; o porte das quebras vira a próxima frente; as 4 frases dizem o número medido ("cerca de 64% dos testes passam"). AT-004 (askpass e `gh` pendurados) e AT-005 (os 4 achados quebram) ficam abertos como pendência dessa frente.
- [x] (dados) A amostra é o CI `windows-latest`; não há máquina Windows. Nada da RDD.
- [x] (UX) Sem interface: UX review pulado.

### Session 2026-11-14 (governança)

- [x] (governança) N.A. — revisor em contexto novo (passo 11, fronteira conferida, bloco válido), 2026-11-14: ver a linha Governança do Technical Context.

### Segurança

- [x] N.A. para a feature: sem login, rota, dado de terceiros, banco nem chamada paga. No CI, o token segue só leitura (`permissions: contents: read`), a action de artefato é fixada por SHA, e o `taskkill` do vigia só alcança a árvore que o próprio script criou.

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

Cobertura: AT-001 e AT-002 em `tests/test_testes_por_modulo.py` (pasta de testes falsa, módulo que pendura com neto);
AT-003 e AT-007 em testes de texto sobre os workflows e as frases; AT-004 no Mac pelos testes de hoje (o corte por
grupo segue valendo) e por um teste do ramo do Windows; AT-006 em `test_windows.py`; AT-008 nas suítes existentes. O
Windows de verdade (AT-003 a AT-006) se prova pelo log do CI, fora deste gate.

---

## Out of Scope

- Paralelizar a suíte no Ubuntu e no macOS; WSL.
- Skills com `python3` no texto (o aluno no Windows digita o atalho da Store), salvo se a medição mostrar teste que dependa disso.
- As pendências da F17b (version gate do starter, `--conferir` com `--paths`): decisão do Roberto no passo 0.
- O repositório privado e o starter (nenhuma skill do starter muda, salvo `checar-ambiente`/`iniciar-repo` se o vigia mudar; aí a geração vai com OK próprio).

## Constraints

- bash 3.2 e Python 3.9 stdlib, também no executor; pulo de plataforma só por constante de `tests/apoio.py`.
- `MANIFEST.txt` a cada arquivo novo; sem número de 11 dígitos no pacote (id de run do CI incluso: cite o commit, LM-012).
- `gh_estado`/`sistema`/`instalar_gh` iguais em `checar.sh` e `inventario.sh` (`test_f16_textos.py` compara).
- Teto do método: 3 rodadas de revisão, 2 ciclos do avaliador; acima disso, pergunta ao Roberto.

## Technical Context

| Aspect | Value | Notes |
|---|---|---|
| **Deployment Location** | `scripts/testes-por-modulo.py`, `.github/workflows/{publish-gate,release}.yml`, `.agents/skills/sdd-checar-ambiente/scripts/checar.sh`, `.agents/skills/sdd-iniciar-repo/scripts/inventario.sh`, `tests/`, e o que a medição acusar em `sdd/bin/` | `scripts/` é do mantenedor; o `init` não o copia |
| **KB Domains** | nenhum | o Open não tem `sdd/kb/` |
| **IaC Impact** | None | só os 2 workflows do CI |
| **LLM Prompts** | false | — |
| **CONTEXTO de domínio** | nenhum (o Open não tem `sdd/patterns/dominio.md`) | — |
| **Governança** | N.A. — o DEFINE trata só da suíte de testes, do CI e do vigia de tempo do checar.sh no Windows, sem dinheiro, saldo, lançamento, nota fiscal, tributo, folha ou dado pessoal | revisor fresco, 2026-11-14 |
| **Segurança** | N.A. (ver Clarifications) | — |

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|---|---|---|---|
| A-001 | No Git Bash, `/proc/<pid>/winpid` dá o pid do Windows de um filho em segundo plano, e `taskkill /F /T` mata `git.exe` e os netos (ssh, sh, sleep) | o teto do `checar` no Windows precisa de outro corte (arquivo de saída + abandono); o Design mede no CI | [ ] |
| A-002 | Com o ritmo do caminho do aluno (~1,7 s por teste), 8 fatias fazem a suíte em ~10 a 15 min cada | mais fatias ou teto maior; a 1ª medição diz | [ ] |
| A-003 | A maior parte das quebras é de causa já conhecida (decodificação, caminho, fim de linha, recurso ausente) | a regra de parada leva o corte ao Roberto | [ ] |

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---|---|---|
| Problem | 3 | medido na F16 (282/~1.900, 156 quebras; 5 pulos `SEM_SINAL`) |
| Users | 3 | 3 papéis |
| Goals | 3 | MUST/SHOULD/COULD |
| Success | 2 | depende da 1ª medição para o tamanho |
| Scope | 2 | o piso só se decide depois da medição |
| **Total** | **13/15** | |

## Open Questions

- ~~O piso (módulos e bloqueio)~~ — decidido pelo Roberto em 2026-11-14 com a 1ª medição (ver Clarifications).

## Revision History

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-11-14 | primeira versão, do brainstorm |
| 1.1 | 2026-11-14 | decisão do Roberto: medir só no PR do fim (Clarifications) |
| 1.2 | 2026-11-14 | AT-001/AT-002 com o contrato do Build (unidade = classe, partes de até 12 (depois 8), `--teto-unidade`, nan/inf e seleção vazia = 64, neto morto, stdout UTF-8): DESIGN v1.1 e avaliador ciclo 1, A5 |
| 1.3 | 2026-11-14 | partes de até 8 testes, N ≤ 1000 (avaliador, ciclo 2) |
| 1.4 | 2026-11-14 | corte e piso decididos pelo Roberto com a 1ª medição (Clarifications) |

## Next Step

Executar o **sdd-design** com este DEFINE.
