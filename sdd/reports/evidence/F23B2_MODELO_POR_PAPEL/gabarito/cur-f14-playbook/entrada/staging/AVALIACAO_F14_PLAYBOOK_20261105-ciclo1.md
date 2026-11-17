# AVALIACAO: F14_PLAYBOOK — ciclo 1

- **Modo:** veredito · **Base:** HEAD `864fd8d` · **Data:** 2026-11-05
- **Quem avaliou:** agente de contexto fresco; não viu a conversa do build
- **Evidência:** `sdd/reports/evidence/F14_PLAYBOOK/AVAL-T*.log`, `AVAL-P*.log`, `AVAL-M*.log`, `verify-gate-864fd8d.log`

<<<AVALIACAO
VEREDITO: NEEDS_WORK

## Resumo por AT

PASS: 001, 002, 003, 004, 005, 009, 010, 012, 013, 014, 016, 017, 019, 023, 025, 026, 027, 028, 029, 030, 031, 032, 034, 035, 036, 037, 041, 042, 043, 045.
PARCIAL: 006 (M1), 008 (L2), 011 (L2), 015 (M1, L3), 018 (M3), 020 (H2, M4, L4), 024 (H4, M5, M6, M7), 033 (relatório ainda não existe), 039 (M8), 040 (L8).
REPROVA: 007 (M2), 021 (H2), 022 (H1), 044 (H3).
NAO_VERIFICADO: 038 (agente de fora do Claude; não rodou).

## Passo 17b seguido à letra (projeto de brinquedo, `sdd-open init`, remoto bare)

Itens 1, 2 e 3 funcionam. Item 4 trava com lição de seção da lista (H4). Item 5 manda passar as linhas `inv` ao `--cruzar`, que sai 2 (M5). Item 6 sem nada aceito não tem caminho (L9). Item 8 num projeto que ignora `sdd/reports` sai 1 sem instrução (M7). Item 9: o pouso limpo funciona, o de conflito pisa a invariante da base (M6). 2ª release: sem nada novo, a contagem sobe de novo (H3).

## Mutantes (`AVAL-M02`, cópia com `git init`, controle verde)

23 plantados, 11 mortos, 12 vivos: M02 sugestão já julgada · M03 candidato já julgado · M05 link no selo · M06 "—" como linguagem simples · M08 bullet já no universo vira pendente · M09 troca do `check=` · M10 archive vence `sdd/` · M16 staging que é link · M17 trace com ponto inicial · M19 `frente/sdd` como link · M20 destino como link · M21 anti-collapse sem piso.

## ACHADOS

### HIGH

- **H1.** O Verify Gate está vermelho em HEAD: `test_playbook_curator.SelfTest` falha em toda cópia sem `.git`, porque o self-test chama o `playbook-lint.sh` com a pasta do pacote como `cwd`.
- **H2.** O conferidor deixa contagem inventada e omissão entrarem sem pergunta: linha repetida, ou com a coluna LM diferente da Delta, soma +2 e some com a contagem do outro bullet; `LM-001 LM-002` na coluna LM cobre 2 linhas DELTA e só 1 é aplicada. Contraria AT-020 e AT-021.
- **H3.** A contagem dobra entre 2 releases da mesma feature: `fp=` só existe na linha impressa; a 2ª linha do mesmo bullet e tipo é descartada pela deduplicação, não entra no registro e conta como nova na release seguinte. Contraria AT-044.
- **H4.** Lição de seção da lista não entra no playbook que o pacote instala (só `## Sempre` e `## Tombstones`): `--conferir-bloco`, `--cruzar` e `--aplicar` saem 2 pedindo "crie o título", e o curador não pode gravar.

### MEDIUM

- **M1.** O curador só lê a 1ª linha do bullet: `promovido_para` na continuação (forma válida para o lint) dá PROMOVER? falso, bullet promovido fora do universo e um 2º campo no `--aplicar`.
- **M2.** Só IGNORADO ou só JA_COLHIDO sai 1, contra AT-007.
- **M3.** O ajuste do `--cruzar` nem sempre destrava: `promovido_para` em texto livre ou para arquivo que saiu gera `check=` morto; `estado=ok` com origem promovida para arquivo inexistente passa verde.
- **M4.** O selo não vê arquivo derivado plantado no staging (`delta.txt`, `selo*`, subpastas).
- **M5.** O texto do 17b erra em 3 pontos: item 5 passa as linhas `inv` ao `--cruzar`; a retomada "continue do item 3" refaz selo e snapshot; o redespacho depois de FORA usa o mesmo `antes` e nunca passa.
- **M6.** No pouso com conflito, `--aplicar-inv` pisa o ID igual da base em silêncio.
- **M7.** Lacunas: projeto com lições antigas não recebe a pergunta prometida; aposentar lição descartada faz o curador fiel ao brief terminar em FALHOU; no próprio sdd-open, os `CURATOR-*` violam a Constraint e o G3.
- **M8.** 12 de 23 mutantes vivos; o teste do piso do anti-collapse não prova o piso (1 de 5 = 20%).

### LOW

- **L1.** `LM-\d{3}` sem fronteira; nota de tabela dá delta a toda LM citada; célula de regra que começa com "mordeu" vence o ✔; `FAIL-FAST` conta.
- **L2.** Datas impossíveis aceitas; CRLF e bytes inválidos alterados por delta só de comentário.
- **L3.** `· tarefa:` e `· motivo:` vazios passam; `check=.` e caminho absoluto passam.
- **L4.** `colheita.txt:1` vale como evidência; DESCARTAR sem motivo, `CONTAMINAÇÃO:` vazia e `#` repetido passam; DELTA de arquivo com espaço some da cobertura.
- **L5.** O exemplo da pergunta D1 diz "1 arquivo", e o commit leva até 5.
- **L6.** `principal/sdd` como link não imprime IGNORADO; a seta diz "nenhum documento" mesmo com IGNORADO; pasta de evidência que é link é seguida.
- **L7.** `wrapper_pattern` em lista de bloco vira slot vazio.
- **L8.** `--selar` termina no stderr; erros de exit 2 também, contra o texto do AT-040.
- **L9.** Promoção aceita "entra no `delta.txt`" no item 5 e "só depois do mecanismo" no fecho; sem nada aceito não há caminho; `rc` perdido para o `[exit=N]`; seta do `--cruzar` contradiz o item 5.
- **L10.** Logs de sonda e relatórios do avaliador são colhidos como achado real.
>>>
