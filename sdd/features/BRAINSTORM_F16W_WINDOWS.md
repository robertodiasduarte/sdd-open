# BRAINSTORM: F16W Windows, porte da suíte

> Sessão exploratória para clarear intenção e abordagem antes dos requisitos.

## Metadata

| Atributo | Valor |
|-----------|-------|
| **Feature** | F16W_WINDOWS |
| **Data** | 2026-11-14 |
| **Autor** | brainstorm-agent (sessão com o Roberto) |
| **Status** | Ready for Define |
| **Base** | `feat/f16w-windows`, nascida de `origin/main` `97503a7` (`v2.15.0`); passo 0 em `0475445` |

---

## Ideia inicial

**Entrada:** executar a F16W do plano (`sdd/features/PLANO_F4_F15_CONSOLIDADO.md`, linha F16W da tabela "Estado das
frentes"; escopo de origem em `sdd/features/ESCOPO_F16_AMBIENTE.md` §3.5, branch `docs/incorporar-starter`): medir a
suíte no `windows-latest` módulo a módulo, consertar o teto do `checar.sh` no Windows (LM-016), medir os 4 achados
guardados (`tasklist`, `report-lint`, `sdd-archive`, `O_NOFOLLOW`) e decidir com o Roberto o piso (quais módulos o
job do Windows roda e se ele vira bloqueante).

**Contexto levantado (conferido em `97503a7`):**
- **A 1ª medição (F16, 2026-11-11, `416c0d5`)** rodou a suíte inteira num job só e foi cancelada no teto de 90 min
  com 282 de ~1.900 testes (126 ok, 145 falhas, 11 erros). O ritmo de ~19 s por teste veio das quebras: o caminho
  do aluno, já portado, roda 144 testes em 4 min (~1,7 s por teste). A suíte inteira tem hoje **2.153 testes em 82
  módulos** (`def test_` contados); com o ritmo do caminho do aluno, ~60 a 90 min seriais no Windows.
- **Causas já conhecidas** (da F16): `text=True` sem `encoding` (LM-014, 81 de 136 quebras do caminho do aluno);
  saída cp1252 do Python num pipe (LM-015); caminho `C:\…` no `$0` (LM-017); recursos que o Windows não tem (trava
  `fcntl`, link simbólico, `chmod`, sinal, nome com aspas), pulados só por constante de `tests/apoio.py`.
- **Só 9 módulos** usam hoje uma constante de pulo (`test_checar`, `test_inventario`, `test_drive`,
  `test_playbook_curator`, `test_kb_dominios`, `test_prompt_drift_scan`, `test_eval_revisores`, `test_f17_passo0`,
  `test_f17b_passo0`); os outros 73 nunca rodaram no Windows.
- **O teto do `checar.sh`:** `gh_estado()` (`checar.sh:71-85`, cópia igual em `inventario.sh`) e `alcance()`
  (`checar.sh:395-435`) rodam o comando num grupo de processos (`set -m`) e o vigia faz `kill -- -<pgid>`. No Git
  Bash isso não corta o `git.exe` nativo nem os netos (ssh, askpass): 5 testes de `test_checar.py` e o pré-voo
  `--frente` estão pulados por `SEM_SINAL`. O Windows tem `taskkill /T` (mata a árvore pelo pid do Windows, que o
  Git Bash expõe em `/proc/<pid>/winpid`).
- **Os 4 achados** já têm o teste que os mede (`tests/test_windows.py`, `ACHADOS`), em módulos que o job de hoje
  não roda (`test_drive`, `test_report_lint`, `test_sdd_archive`).
- **CI:** o job `testes-windows` existe nos 2 workflows (`publish-gate.yml:195`, `release.yml:189`), informativo
  (fora do `needs:` da `release`), teto 30 min, só os 5 módulos do caminho do aluno. Repositório público: runner
  Windows sem custo, jobs em paralelo permitidos.
- **Instrumento novo** (`scripts/testes-por-modulo.py`, escrito nesta sessão): cada módulo num processo próprio,
  com teto, contagem e a saída guardada; fatias estáveis (`--fatia I/N`, pelo nº de testes) para jobs paralelos; no
  Windows, o teto mata a árvore com `taskkill /T` e a saída vai para arquivo, não para pipe.

**Contexto técnico para o Define:**

| Aspecto | Observação | Implicação |
|--------|-------------|-------------|
| Onde mora | `tests/` (o porte), `scripts/testes-por-modulo.py`, `.github/workflows/` (2), `checar.sh` e `inventario.sh` (o vigia), `sdd/bin/sdd-drive.sh` e o que mais a medição acusar | sem skill nova; `checar-ambiente` e `iniciar-repo` ganham bump patch se o vigia mudar |
| Medição | só no CI (`windows-latest`); exige push da branch | o push da branch pede "sdd-open autorizado" (resposta "ainda não" no passo 0: pergunto antes da 1ª medição) |
| Pulos | só por constante de `tests/apoio.py` (`test_windows.py` reprova pergunta de plataforma fora dele) | causa nova de recurso ausente ⇒ constante nova com motivo |

---

## Perguntas e respostas

| # | Pergunta | Resposta | Impacto |
|---|----------|--------|--------|
| 1 | Posso dar push da branch para medir? (passo 0) | **Ainda não**: brainstorm, define e design aqui; perguntar de novo antes da 1ª medição | a 1ª medição fica no começo do Build |
| 1b | Push da branch para a 1ª medição (perguntado de novo depois do Design, com a explicação do que o push faz) | **Medir só no PR do fim** (Roberto, 2026-11-14) | sem medição intermediária: no Build entram as causas já conhecidas e as que se acham sem medir (varredura estática, provada no Mac); a 1ª medição inteira, módulo a módulo, sai no CI do PR da release e é a tabela para a decisão do piso; o que ela acusar e não couber vira pendência ou frente seguinte |
| 2 | Até onde vai o porte nesta frente? | **Rotina, decidida e registrada** (o plano já fixa: medir tudo módulo a módulo, priorizar o teto do `checar` e os 4 achados, depois decidir o piso com o Roberto) | a pergunta do piso vai ao Roberto com os números, no Build |
| 3 | Regra de parada | **Rotina, decidida e registrada:** depois da 1ª medição inteira, se as quebras restantes não couberem nesta sessão (causas novas que pedem mais que conserto mecânico em muitos módulos), paro e levo ao Roberto o corte: o que entra no piso agora e o que vira pendência | o tamanho real só aparece na 1ª medição |

---

## Inventário de amostras

| Tipo | Onde | Qtde | Notas |
|------|----------|-------|-------|
| Medição Windows | job `testes-windows` (`windows-latest`, Git Bash, Python do `setup-python` 3.12) | — | o caso real do aluno contador; única medição possível (não há máquina Windows) |
| Linha de base | este Mac, `scripts/testes-por-modulo.py --paralelo 6` sobre `0475445` | 1 | módulos verdes aqui e tempo de cada um |
| Logs da F16 | `sdd/reports/evidence/F16_AMBIENTE/windows/` (branch de documentos) | 5 | as causas já vistas no caminho do aluno |

---

## Abordagens exploradas

### Abordagem A: Fatias paralelas, medir tudo, consertar por causa ⭐ Recomendada

**Descrição:** o job `testes-windows` passa a rodar a suíte inteira em N fatias paralelas (`strategy.matrix`), cada
uma pelo `scripts/testes-por-modulo.py` com teto por módulo; a 1ª medição dá a tabela módulo a módulo; as quebras
viram consertos por causa (decodificação, caminho, fim de linha, interpretador), conserto de produto com teste, ou
pulo por constante com motivo; o vigia do `checar.sh` ganha o corte por `taskkill /T` e os 5 pulos `SEM_SINAL`
saem; no fim, o Roberto decide o piso com os números.

**Prós:** cabe no teto do job (as fatias rodam juntas); um módulo pendurado não come o job e diz o próprio nome; a
mesma ferramenta mede e depois guarda o piso.

**Contras:** N jobs a mais no CI de cada PR (sem custo no repositório público, mas mais linhas no run); o tamanho do
conserto só aparece depois da 1ª medição.

### Abordagem B: Ampliar o caminho do aluno módulo a módulo

**Descrição:** acrescentar módulos à lista do job atual à medida que ficarem verdes, sem medir tudo de uma vez.

**Prós:** cada passo é pequeno.
**Contras:** não mede módulo a módulo a suíte inteira (o pedido do plano); cada rodada de CI mede poucos módulos;
o piso seria decidido sem saber o resto.

### Abordagem C: WSL

**Prós:** perto do Ubuntu, quase tudo passaria.
**Contras:** não é o caso do aluno (Git Bash + Python nativo); rejeitada já na F16.

---

## Abordagem escolhida

| Atributo | Valor |
|-----------|-------|
| **Escolhida** | Abordagem A (decisão de rotina: é o que o plano pede, "medir módulo a módulo") |
| **Confirmação** | registrada em 2026-11-14; vai ao Roberto junto com a pergunta do push |
| **Motivo** | é a única que mede tudo dentro do teto e localiza o módulo que pendura |

---

## Decisões

| # | Decisão | Motivo | Alternativa rejeitada |
|---|----------|-----------|----------------------|
| 1 | Executor por módulo em `scripts/testes-por-modulo.py` (stdlib, Python ≥ 3.9) | `scripts/` é do mantenedor; o `init` não o copia; o job e o mantenedor usam o mesmo | `unittest discover` num job só (sem teto por módulo, sem nome do que pendurou) |
| 2 | Fatias pelo nº de testes de cada módulo, estáveis (maior primeiro, na fatia mais leve) | sem arquivo de pesos para manter; a mesma fatia roda os mesmos módulos em toda execução | pesos por tempo medido (arquivo a manter, muda a cada medição) |
| 3 | O vigia do `checar.sh` e do `gh_estado` no Windows: `taskkill /F /T` pelo `winpid`, mesmo bloco nas 2 cópias | o sinal ao grupo não vale no Git Bash (LM-016); a árvore do Windows sim | deixar pulado (`SEM_SINAL`) e declarar o limite |
| 4 | Pulo só por constante de `tests/apoio.py`; recurso novo ⇒ constante nova com motivo | regra da F16, vigiada por `test_windows.py` | `skipIf(os.name == "nt")` solto |
| 5 | O job Windows segue informativo até o Roberto decidir o piso com os números | regra do plano | promover antes de medir |

---

## Features removidas (YAGNI)

- **Paralelizar a suíte no Ubuntu e no macOS** com o mesmo executor (cortaria os 32 e 51 min do CI): fora da
  frente; testes de teto de tempo poderiam oscilar com carga. Fica como ideia na ficha.
- **WSL:** já rejeitado na F16.
- **Skills com `python3` no texto** (o aluno no Windows digita o atalho da Store): pendência da F16 que não é a
  suíte; fica na ficha, salvo se a medição mostrar que um teste depende disso.

---

## Requisitos sugeridos para o Define

- o job `testes-windows` roda a suíte inteira em fatias, cada uma pelo executor por módulo, com a tabela por módulo
  no log e a saída de cada módulo guardada como artefato do run;
- o executor: fatias estáveis e disjuntas que cobrem todos os módulos; teto por módulo que mata a árvore e marca
  `TETO`; contagem lida do `unittest`; exit 0 só com todos os módulos verdes; uso errado sai 64;
- no Windows, o `checar.sh` (modo normal e `--frente`) e o `gh_estado` respeitam o teto de 10 s com ssh, askpass
  ou rede pendurados: os 5 testes `SEM_SINAL` de `test_checar.py` deixam de ser pulados e passam no job;
- os 4 achados guardados medidos no job: passam, ou viram conserto com teste, ou pulo por constante com o motivo;
- toda quebra da medição termina em conserto (produto ou teste), pulo por constante com motivo, ou pendência com o
  OK do Roberto; o relatório traz a tabela por módulo antes e depois;
- o piso decidido pelo Roberto aplicado nos 2 workflows e nas frases de Windows do README e do quickstart (só o que
  foi provado).

---

## Próximo passo

Executar o **sdd-define** com este brainstorm.
