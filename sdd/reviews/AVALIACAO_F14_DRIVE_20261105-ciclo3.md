<<<AVALIACAO
**Veredito: NEEDS_WORK.** Ciclo 3 focado, commit 79ea6c0. Não há HIGH; há 5 MEDIUM e 14 LOW. O caminho comum está fechado: rename, delete, modo, commits no meio do gate e HEAD que recua ou some não geram verde falso. O `gate-verde` falso ainda acontece por 3 caminhos fora do comum (M1, M2, M3). AT-038: NAO_VERIFICADO.

Ajudantes (`mkrepo`, `drv`, `feito`, `rel`, `verde`, `ficha`, `doc`, `mkarq`) estão em AVAL3-00-lab.log. O script inteiro de cada sonda está no início do log citado.

## Sondas

| Sonda | Esperado | Observado | Resultado | Log |
|---|---|---|---|---|
| Rename de código para documento, sujo e commitado, nos 2 sentidos | COMMITAR ou VERIFICAR | isso | OK | 01 |
| Delete, modo e arquivo virando symlink, sujo e commitado | COMMITAR, depois VERIFICAR | isso | OK | 01 |
| Nomes parecidos (`sdd/reports-velho/`, `sdd/reportsx`, `sdd/features.py`, `SDD/reports/`) | não contam como documento | não contam | OK | 01 |
| Código que é symlink para `sdd/reports/`, com o alvo alterado | VERIFICAR | `gate-verde`, com o gate agora em rc=1 | FALHA (M2) | 01 |
| Script do gate em `sdd/reports/`, alterado depois do verde | VERIFICAR | `gate-verde` | FALHA (M2) | 01 |
| Submodule sem `ignore`, ponteiro movido | COMMITAR, depois VERIFICAR | isso | OK | 02 |
| Submodule com `ignore=all` ou `diff.ignoreSubmodules=all`, ponteiro commitado | VERIFICAR | `gate-verde` | FALHA (M1) | 02 |
| `skip-worktree` ou `assume-unchanged` com edição local | COMMITAR | `gate-verde` | FALHA (L2) | 02 |
| reset, amend, reset --soft, merge, gc que apaga o commit testado | VERIFICAR se o conteúdo mudou; verde se é igual | isso | OK | 03 |
| `concluir` repetido, depois commit de código | verde, depois VERIFICAR | isso | OK | 03 |
| Gate trocado e voltado; troca com vermelho no meio | só vale o gate com a mesma digital | isso | OK | 03 |
| Estado forjado (gate `false`, log inexistente) | recusar | `gate-verde` | FALHA (M3) | 03 |
| Commit, rename, delete, amend ou reset durante `--fundo` | VERIFICAR | isso | OK | 04, 12 |
| Troca de gate aceita durante o gate | não vale como verde | VERIFICAR | OK | 12 |
| Variável `SDD_DRIVE_TRAVA_HERDADA` vinda de quem chama: sem trava, trava morta, trava viva | não abre nada | ignorada; o gate não a herda | OK | 04 |
| 8 `verificar` juntos, com e sem `--fundo`, trava limpa e morta: 32 rodadas | 1 gate por rodada | sempre 1 | OK | 05 |
| Bash ou python do filho morto com `kill -9` | ESPERAR | VERIFICAR; 2 gates juntos | FALHA (L8) | 04, 05 |
| verify-gate morto | `gate-inconclusivo` | isso | OK | 04 |
| Comando do gate morto | não gastar rodada | vermelho; com `contains:`, verde | FALHA (L7) | 04 |
| Estado apagado, corrompido ou recriado durante o gate; recibo e `--max` no meio | sem traceback; recibo preservado | isso | OK | 04 |
| Ctrl-C no gate em 1º plano | sem traceback | traceback | FALHA (L9) | 06 |
| Forma do estado (24 variações) | exit 20 | 3 passam e são inofensivas; `motivo:[]` ou `{}` sai 2; as outras saem 20 | FALHA (L10) | 12 |
| Archive: caixa, slices, sufixos, acento, NFD no arquivo e na ficha | protegido | protegido | OK | 07 |
| Archive: citação em NFD, em outra caixa ou por nome com acento | protegido | movido | FALHA (M4) | 07 |
| Archive: Status ✅ antes da `## Ficha` | aberta | movido | FALHA (L11) | 07 |
| Archive: ficha fechada, os 3 lotes | move | move | OK | 07 |
| Archive: `F1` aberta com `F14` fechada | F14 move | move | OK | 07 |
| Archive: proteção demais | só o necessário | prefixo, nome curto e prosa também bloqueiam | LOW (L12) | 07, 08, 10 |
| Deploy: todos os passos passageiros | redispara 1 vez, sem rerun | isso | OK | 09 |
| Deploy: um passo real, job falho sem passo, lista vazia | não redispara | isso | OK | 09 |
| Deploy: 404 e 403 no disparo | exit 2 | isso, sem marca gravada | OK | 09 |
| Deploy: consulta 502, workflow desconhecido, 401 | 4, 64, 3 | isso | OK | 09 |
| Deploy: 502 na consulta do run que depois volta | tenta de novo | isso | OK | 09 |
| Guarda: 18 casos (rename, espaço, ` -> `, acento, aspas, prefixo parecido) | AT-032 e AT-033 | isso, exceto `skip-worktree` | OK (L2) | 10 |
| `--checar`: exits 0, 5, 64, sem rodar o cmd nem gravar trace | isso | isso | OK | 10 |
| DEFINE com CRLF | checar e gate concordam | checar 0, gate 2 | FALHA (L14) | 10 |
| `seguir --drive`: release, `--parar`, slot inválido ignorado, revisão, HIGH aberto | isso | isso | OK | 10 |
| Curador: os casos da letra do AT-034 | não conta; achado real conta | isso | OK | 11 |
| Curador: colheita real de F14_DRIVE (66 arquivos) | sem DELTA falso | 3 DELTA, os 3 falsos | FALHA (M5) | 11 |
| Módulos em cópia: `test_drive` 91, `test_deploy_do_sha` 35, `test_sdd_archive` 29, `test_avaliador_guard` 14, `test_curadoria_bloco` 49, mais `--self-test` | OK | OK | OK | 13 |
| AT-038 | agente real | — | NAO_VERIFICADO | — |

## ACHADOS

### MEDIUM

**M1. Ponteiro de submodule some do diff e vira `gate-verde` (AT-014, AT-010).** `sdd-drive.sh:478` e `:547` não passam `--ignore-submodules=none`, e o `ignore = all` no `.gitmodules` vale para os dois comandos. O `.gitmodules` entra no commit, então a configuração viaja com o repositório.

Reprodução (AVAL3-02, casos `s_all` e `s_cfg`):
```
L=$(novo); (cd $L; git init -q; echo v1>lib.txt; git add -A; git commit -qm v1; echo v2>lib.txt; git add -A; git commit -qm v2)
mkrepo "$(novo)"; git -c protocol.file.allow=always submodule --quiet add $L sub; git -C sub checkout -q $(git -C $L rev-parse HEAD~1); git add sub
git config -f .gitmodules submodule.sub.ignore all; git add -A; git commit -qm sub; verde
git -C sub checkout -q $(git -C $L rev-parse HEAD); drv concluir $D       # gate-verde, sem commit
git add -f sub; git commit -qm ponteiro; drv concluir $D                  # gate-verde; name-only vazio
```
Variantes: `git config diff.ignoreSubmodules all` dá o mesmo resultado. Com `ignore=dirty`, uma edição dentro do submodule passa.

**M2. Código ou gate guardado em pasta de documento muda sem novo gate (AT-014).** A letra do AT-014 permite isso, então a correção começa por uma decisão. Hoje nenhum dos 15 DEFINEs reais tem gate em pasta de documento: todos usam `git archive HEAD` (AVAL3-14). O risco é de outro projeto.

Reprodução (AVAL3-01, casos `a_sym1` e `a_sym2`):
```
mkrepo "$(novo)" "echo x >> gate.calls; sh codigo.sh"; mkdir -p sdd/reports
echo "exit 0" > sdd/reports/impl.sh; ln -s sdd/reports/impl.sh codigo.sh
git add -f sdd/reports/impl.sh codigo.sh; git commit -qm cod
drv iniciar $D; feito; rel; drv verificar $D
echo "exit 1" > sdd/reports/impl.sh; git add sdd/reports/impl.sh; git commit -qm muda; drv concluir $D   # gate-verde; gate.calls=1
```
O mesmo ocorre com o cmd `sh sdd/reports/gate.sh`.

Decisão para o responsável:
- **Recusar:** tratar como não documento um symlink que aponte para essas pastas e um `cmd` que as cite. Fecha o caso, com um pouco mais de código.
- **Declarar como limite:** escrever em `docs/sdd-drive.md`. Recomendo só se o custo do conserto parecer alto, porque o limite continua invisível para quem usa.

**M3. Estado editado gera verde de gate que nunca rodou (AT-014; nenhum AT cobre).** `ultimo_valido` (`:319`) e `proxima` (`:581`) confiam no JSON e não olham se o log existe.

Reprodução (AVAL3-03, casos `e_forja`, `e_forja_head`, `e_troca_sha`, `e_opcao`):
```
mkrepo "$(novo)" "false"; drv iniciar $D; feito; rel
# no JSON, em "gates": {"n":1,"rodada":1,"commit":"<HEAD>","exit":0,"log":"nao/existe.log","impressao":"<gate_sha>"}
drv concluir $D    # gate-verde; o gate é "false" e nunca rodou
```
Variantes:
- `"commit":"HEAD"` continua verde depois de um commit de código.
- `"commit":"--output=INJETADO"` faz o `git diff` gravar esse arquivo.

Conserto mínimo: exigir que o log exista e termine em `[exit=0]`, e exigir commit em hexadecimal. Isso barra edição descuidada, não forja deliberada; o limite que sobra precisa ficar escrito.

**M4. Citação em ficha aberta escapa pela forma do nome (AT-030).** `sdd-archive.py:214`, `:217` e `:249` comparam texto cru. Só o nome da ficha foi normalizado.

Reprodução (AVAL3-07), com `doc` de arquivo antigo e ficha `HANDOFF_OUTRA` aberta:
- `p_cit_nfd`: arquivo NFD em disco, citado em NFC como `sdd/reports/NOTAS_ação.md`: lote `soltos`.
- `p_cit_caixa`: `f14_foo` citado, com `DEFINE_F14_FOO.md`: lote `sem-ledger`. `sdd/reports/notas_b.md` citado, com `NOTAS_B.md`: lote `soltos`.
- `p_cit_acento`: `ação` citado, com `BUILD_REPORT_ação.md`: lote `soltos`. O nome com acento fica fora de `RX` e não passa pela citação de grupo.

Reversível: fica só staged.

**M5. Filtro do curador: a colheita real desta feature dá 3 DELTA, os 3 falsos (AT-034).** `playbook-curator.sh:100` olha só o início da linha, e um `$ cmd` de várias linhas só tem `$ ` na 1ª. A letra do AT-034 é cumprida; o objetivo dele não.

Reprodução (AVAL3-11, seções 9 e 10): copiar `AVAL-*.log`, `AVAL2-*.log` e as `AVALIACAO_F14_DRIVE_*` para uma pasta e rodar `--colher` com o playbook real.
- LM-001 e LM-002 vêm de `AVAL-24:7`, linha de um comando `echo == AT-034 colheita…`.
- LM-005 vem de `AVAL-DESIGN-11:46`, saída de uma colheita anterior, com caminho temporário.

Também contam como achado (seções 5 e 6):
- `   │ ❌ delta linha 3: LM-001`, o prefixo que o próprio verify-gate põe;
- `+ grep FAIL LM-002`;
- `  $ grep FAIL LM-003`;
- `/tmp/com espaco/playbook.md:3: ❌ LM-001 x`;
- `sdd/playbook.novo:3: ❌ LM-002 x`.

Efeito: contador `mordeu` falso, e com 2 mordidas sai `PROMOVER?`. O curador julga antes de aplicar.

**Atenção:** os meus logs AVAL3 contêm essas linhas de fixture. AVAL3-11 e AVAL3-10 vão somar DELTA falso numa colheita real, como já acontece com os logs dos ciclos anteriores.

### LOW

- **L1. Edição temporária durante o gate.** O gate rodou com `fix.py` presente, o arquivo saiu antes do `concluir`, e deu `gate-verde` (`m_edit_volta`, AVAL3-04). Não há como fechar por completo; conferir `git status` ao fim do gate pegaria este caso.
- **L2. `skip-worktree` e `assume-unchanged`.** `git update-index --skip-worktree codigo.py` com o conserto só local dá `gate-verde`, e o commit não tem o conserto (`i_skip2`, AVAL3-02). A guarda também sai 0 (`t13`, AVAL3-10). `core.fileMode=false` esconde chmod (`i_mode`). Gates com `git archive HEAD`, como os reais, não caem nisso.
- **L3. `BUILD_REPORT` velho.** Depois de código novo e verde novo, o `concluir` aceita o relatório antigo sem exigir nova avaliação (`c_rel`, AVAL3-03). O `report-lint.py` era de mentira nessa sonda; não testei com o real.
- **L4. `bloqueio-humano` não segura.** `drv bloqueio $D x; drv concluir $D` dá `gate-verde` e sobrescreve o motivo, embora a seta mande usar `--resume` (`c_bloq`). A parada por repetição faz o mesmo (`c_bloq3`). AVAL3-03.
- **L5. Branch só é conferida no início.** `git checkout -b main` depois de `iniciar`: `verificar` roda e `concluir` dá `gate-verde`; com HEAD destacado também (`h_branch`, `h_detached`, `h_verif_main`, AVAL3-03). Cumpre a letra do AT-002, e nada é publicado.
- **L6. Arquivo ignorado.** Mover `.verde` depois do verde mantém `gate-verde`, com o gate agora em rc=1 (`m7`, AVAL3-12). O AT-010 exclui ignorados: é limite do contrato, e convém escrevê-lo.
- **L7. Gate morto por sinal.** `kill -9` no comando dá rc=137, vermelho, e gasta rodada (`f_kill_cmd`). Com `pass_when: contains:`, se o texto saiu antes do kill, dá verde e `gate-verde` (`f_kill_contains`). AVAL3-04.
- **L8. Efeitos da trava.**
  - `kill -9` no bash ou no python do filho: `proximo` diz VERIFICAR com o gate órfão rodando, e um 2º gate sobe.
  - `solta_trava` (`:538`) não confere o dono: o 1º gate, ao terminar, apaga a trava do 2º (AVAL3-05, fim). Confirma o L8 do ciclo 1, antes não retestado.
  - A janela da trava vazia (`:513-519` com `:498`) só abriu com sleep injetado numa cópia: 2 gates juntos (AVAL3-06). Em 32 rodadas × 8 processos sem injeção, nunca (AVAL3-05).
  - `printf 99999999999999999999 > …/DRIVE_F.lock`: `OverflowError`, exit 2, sem citar o arquivo (AVAL3-12).
- **L9. Ctrl-C.** SIGINT no gate em 1º plano dá traceback de `KeyboardInterrupt`; `:1108` só pega `Exception` (AVAL3-06).
- **L10. `"motivo":[]` ou `{}` no estado.** `TypeError`, exit 2, quando o AT-013 pede 20; `:273` testa pertinência num dict (AVAL3-12).
- **L11. Status fora da Ficha.** Tabela com `| Status | ✅ … |` antes da `## Ficha`, ou dentro de cerca, faz a ficha aberta contar como fechada e os documentos entram no lote (`p_status_antes`, `p_status_fence`, AVAL3-07). `sdd-archive.py:101` lê a 1ª linha do arquivo, e `handoff-lint.py:72` lê só a Ficha, embora o AT-030 peça a mesma regra. É LOW porque o molde abre com a Ficha.
- **L12. Proteção demais.**
  - `HANDOFF_DESIGN` e `HANDOFF_REPORT` abertas protegem `DESIGN_*` e `BUILD_REPORT_*` de feature fechada, porque o prefixo entra na busca.
  - `HANDOFF_F` protege `F_X`.
  - "A API" na ficha protege `DEFINE_API`, e "rapido" protege `DEFINE_api` (`:214` aceita vizinho minúsculo).
  - Neste repositório, a simulação dá `protegidos=21` e 0 movíveis, incluindo os grupos `M1` e `W0`, nomes curtos (AVAL3-08). Só existe 1 ficha em `sdd/handoffs/`. Não conferi se cada grupo está mesmo fechado.
  - Não há opção para liberar.
- **L13. Deploy, formas sintéticas (AVAL3-09).**
  - Passageiro em job `success` e outro job `timed_out`: redispara (`:165` só olha `failure`).
  - View falhando até o teto, com o run já falho: "o deploy não terminou… isso não é falha", frase falsa (`:384`).
  - Run sem `headSha` e verde: NO AR (`:285`).
  - `HTTP 503: workflow service not found upstream`: exit 64 (`:140`).
- **L14. DEFINE com CRLF.** `verify-gate.sh:229` tira a aspas antes do CR, e o cmd vira `echo ok"`. `--checar` sai 0, o gate sai 2 e gasta rodada (`c10`, AVAL3-10). Não verifiquei se é anterior a esta frente.

Um achado real em arquivo `.md` também se perde em silêncio: `docs/manual.md:12: ❌ LM-001 …` no log, ou `docs/x.md:3: ❌ LM-003 real` no HANDOFF. Com `- ` na frente, conta (AVAL3-11, seção 4). É o L14 do ciclo 2 pelo outro lado, e o AT-034 permite.

## O que testei e não consegui quebrar

- **Verde:** rename nos 2 sentidos (inclusive durante `--fundo` e depois de vermelho), delete, modo, nomes parecidos, submodule normal, reset, amend, gc que apaga o commit testado, `concluir` repetido, gate trocado e voltado, troca aceita durante o gate.
- **`--fundo`:** a variável de quem chama não abre nada (forjar exige `exec` com pid plantado, e o gate roda de verdade, sem verde falso), e o gate não a herda. Pai morto antes de gravar o pid só atrasa cerca de 2 s; simulei com trava de pid morto, sem matar o pai nessa janela.
- **Estado:** apagado, corrompido, recriado ou com `--max` reduzido durante o gate. Recibo no meio é preservado.
- **Archive:** toda a proteção por palavra inteira, caixa, slice, acento e NFD, e os 3 lotes de ficha fechada.
- **Deploy:** todos os consertos, nos 2 lados. Nunca houve `gh run rerun`.
- **Guarda, `--checar` e `seguir --drive`:** tudo, exceto `skip-worktree` (L2) e CRLF (L14).
- **Consertos anteriores:** H1 do ciclo 1 e H1 do ciclo 2 seguram. M1, M2, M3 e M4 do ciclo 2 também, com o resto em L10 e M5.

## Não coberto

- `gh` real, rede, Linux e Windows.
- Suíte inteira, gate do DEFINE e `report-lint.py` real nas sondas do drive.
- Corrida de escrita entre `proximo` e o fim do gate: vi pelo código, não provoquei.
- Drive chamado com `GIT_DIR` no ambiente.
- AT-038.

## Limites desta avaliação

- **`[exit=N]` dos logs:** nos logs 01 a 12, vale para o script inteiro; o resultado de cada caso está no `[rc=]`. Muitos casos filtram a saída com `grep` ou `cut` dentro do script. No AVAL3-13 o script termina em `exit 0` e cada módulo passa por `tail`: a prova é a linha `OK` do unittest, não o exit.
- **Comandos recusados:** o verificador de segurança recusou 2 tentativas da sonda 01, porque o script `-c` continha `rm`. Não contornei: troquei toda remoção por `mv` para fora do repositório temporário.
- **Pasta do laboratório:** por isso não apaguei nada, e `/var/folders/_s/_r8ph5yx5vgbqp_knw08v1380000gn/T/tmp.IaPhB1vDIh` continua lá. Quem quiser limpar apaga à mão.
- **Casos inválidos no macOS, sem caixa:** em `p_goX` o 2º `doc` falhou, valendo só `go_x`. Em `o_cit_prosa`, `DEFINE_api` falhou e foi refeito no fim de AVAL3-10.
- **Árvore do projeto:** `git status` igual ao do início, e só gravei `sdd/reports/evidence/F14_DRIVE/AVAL3-*.log`. Os processos `sdd-open-_dhd_po1` que vi rodando são da outra sessão, e não os toquei.

Logs: `/Users/robertoduarte/rdd-worktrees/sdd-open-f14-drive/sdd/reports/evidence/F14_DRIVE/AVAL3-00` a `AVAL3-14`.
>>>
