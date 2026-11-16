# Lote de curadoria — o julgamento das colheitas da fila

A `sdd-release` só **colhe**: cada publicação deixa uma entrada em `sdd/curadoria/fila/<F>/<AAAAMMDDTHHMMSSZ>/`
(a colheita, o exit dela, as impressões já excluídas e a cópia dos documentos que ela cita). Este lote **julga** a
fila inteira, quando a pessoa pede ("rode o lote da curadoria", `/sdd-playbook lote`). Nada roda sozinho: a release
só avisa, em 1 linha, quando a fila passa de 5 entradas. As garantias de antes valem aqui, iguais: a falha da colheita
nunca vale como "nada a colher"; quem separa contagem de regra é o conferidor; o curador é conferido pela fronteira de
escrita; mudança de regra sempre pergunta.

Brief do curador: `.agents/skills/sdd-playbook/references/curator.md`; palavras e exemplo: `references/como-falar.md`
(exemplo do lote). Antes de começar, diga em 1 frase quantas publicações estão na fila e que o lote não mexe em nada
publicado.

0. **Onde.** O lote escreve no playbook e na branch padrão: rode numa frente própria (`/sdd-new-session`), nascida da
   branch padrão **atualizada**, nunca na pasta de uma publicação, com o playbook e as invariantes iguais ao commit
   (`git diff --quiet -- sdd/playbook.md sdd/invariants.md` sai 0; senão, pare e peça para commitar ou guardar a mudança
   antes: o item 3 pode precisar voltar os dois ao commit). `bash sdd/bin/playbook-curator.sh --fila` lista as
   entradas; fila vazia ⇒ diga isso e encerre. Entrada com `colheita FALHOU` não é julgada: diga a causa e que uma
   colheita nova da feature (`--enfileirar <F>` numa pasta com os documentos dela) a substitui.
1. **Conferir a entrada (uma por vez).** Para cada entrada `E` da fila, em ordem:
   `bash sdd/bin/playbook-curator.sh --conferir-entrada "$E" sdd/playbook.md [--inv sdd/invariants.md] > "$TMPDIR/conf-entrada.txt"; rc=$?`
   — `--inv` só quando `sdd/invariants.md` existe; sem o arquivo, diga "invariantes: arquivo ausente, cruzamento
   pulado" e siga só com o playbook. Ele refaz a colheita sobre a cópia da entrada, com o playbook de agora, e compara
   as impressões com a colheita guardada: a colheita que se julga é a refeita, nunca a guardada.
   | `rc` | Ação |
   |---|---|
   | `0` | `ENTRADA CONFERIDA`: guarde a linha `staging:` como `STG` e siga |
   | `1` | `NADA A JULGAR`: tudo já foi julgado; a entrada vai direto para o item 7 |
   | `2` | `ENTRADA RECUSADA`: diga o motivo (colheita alterada, pasta mexida depois do commit, colheita que falhou); **nada dela é aplicado**, ela fica na fila, marcada com `bash sdd/bin/playbook-curator.sh --recusar "$E" "<motivo>"` (a marca vai no commit do lote; a próxima colheita da feature traz as linhas de novo e tira a entrada); siga com a próxima |
   | outro (`64`, `126`, `127`…) | **não é "nada a julgar"**: pare o lote e diga a causa e o conserto |
   A linha `evidência ausente:` diz quantas linhas citam um log que o projeto não versiona: relate-as, nunca as conte.
2. **Despachar o curador em contexto fresco**, pela escada de `sdd-build/references/contexto-fresco.md`, com **só**
   os 5 campos: `feature: <F> · staging: $STG · colheita: $STG/colheita.txt · playbook: <raiz>/sdd/playbook.md · worktree: <raiz>`.
   Antes do despacho, nesta ordem: `mkdir -p sdd/reports/briefs`; grave o brief (os 5 campos e "leia e siga
   `.agents/skills/sdd-playbook/references/curator.md`") em `sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md` (um por
   entrada: duas entradas da mesma feature no mesmo lote não dividem brief, selo nem snapshot);
   `T="${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/<F>/curador-<entrada>"; mkdir -p "$T"`;
   `bash sdd/bin/playbook-curator.sh --selar "$STG" > "$T/selo.txt"` (o selo do staging fica **fora** dele);
   `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/antes" <raiz>/sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md`;
   imprima `🧹 curadoria: julgando em contexto novo (alguns minutos); você não precisa responder`.
   Sem subagente: `bash sdd/bin/sdd-fluxo.sh despachar curador <F> sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md`
   e pare no exit 40, repassando a parada que ele imprime. **Sessão nova depois da parada do curador:** recalcule
   `STG` com `--conferir-entrada "$E" sdd/playbook.md --retomar` (só diz onde o staging está; **não** o refaz, o que
   apagaria uma escrita do curador antes da conferência) e `T`, e vá direto para "Na volta"; refazer o
   selo ou o snapshot de antes agora tomaria por linha de base o que o curador já escreveu. `--retomar` com exit 1, ou
   `"$T/antes"` ausente = a pasta temporária se perdeu: recomece esta entrada do item 1; nada foi aplicado.
   Na volta, **sem editar nada no meio** e recalculando `STG` e `T` (variável de shell não passa de uma
   chamada para a outra): salve o bloco em `"$T/curadoria.txt"`;
   `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/depois" <raiz>/sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md`;
   `bash sdd/bin/governanca-fronteira.sh --comparar "$T/antes" "$T/depois" <raiz>/sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md > "$T/comparar.txt"`.
   Não repasse a linha `→` da fronteira (ela fala do DEFINE): quem lê o `comparar.txt` é o item 3.
3. **Conferir o bloco antes de qualquer pergunta.**
   `bash sdd/bin/playbook-curator.sh --conferir-bloco "$STG/colheita.txt" "$T/curadoria.txt" sdd/playbook.md "$T/selo.txt" "$T/comparar.txt" > "$T/conferido.txt"; rc=$?`.
   Ele reprova (exit 2) quando o curador escreveu no projeto (`FORA:`) ou a fronteira não foi verificada,
   quando o staging mudou depois do selo, quando falta uma linha da colheita e quando uma contagem não
   é igual à que o script colheu. Exit 2 ⇒ despache de novo **1 vez**, com os 5 campos mais o campo
   `conferencia:` (as linhas `🔴 bloco:`). Se o motivo foi só o bloco, sem `FORA:` nem staging mexido,
   redespache com o mesmo selo e o mesmo snapshot. Se houve `FORA:` ou staging mexido: liste à pessoa o
   que saiu (não apague nada); com `sdd/playbook.md` ou `sdd/invariants.md` na lista, **não redespache**:
   registre `Curadoria: FALHOU (curador escreveu no playbook)` para esta entrada, guarde
   `git diff -- sdd/playbook.md sdd/invariants.md` na evidência, volte os dois ao commit
   (`git checkout -- sdd/playbook.md sdd/invariants.md`: nada do lote foi aplicado ainda, a aplicação é no item 5) e
   siga com a próxima entrada; esta fica na fila. Nos outros casos, refaça o item 1,
   o selo e o snapshot de antes (o que a pessoa já viu vira linha de base) e só então redespache. 2ª
   reprovação ⇒ registre `Curadoria: FALHOU (bloco inválido)` para esta entrada: **nada dela é aplicado**, ela fica
   na fila, marcada com `--recusar` (como no item 1), e o lote segue com a próxima. Sem subagente, cada tentativa volta numa sessão nova, sem
   memória da anterior: leia `sdd/reports/briefs/BRIEF_curador_<F>_<entrada>.md`; se ele já tem o campo
   `conferencia:`, esta é a 2ª tentativa, e nova reprovação encerra esta entrada, sem redespachar. Nunca separe
   contagem de regra à mão: quem decide é o conferidor.
4. **Contagem entra, regra pergunta.** Comece o lote com `: > "$TMPDIR/lote-delta.txt"; : > "$TMPDIR/lote-inv.txt"`. As
   linhas `AUTO <delta>` de cada `conferido.txt` vão, sem pergunta, para `"$TMPDIR/lote-delta-<entrada>.txt"` (um por
   entrada: o envio do item 9 pode precisar tirar as linhas de uma entrada só), e o `lote-delta.txt` é a junção deles,
   na ordem da fila. As linhas `PERGUNTA <n> <tipo> <delta>`
   (lição nova, aposentadoria, refino, promoção, invariante, sugestão que o curador confirmou e contagem que põe uma
   lição entre as invariantes) viram perguntas `[D3 · muda a regra do método]`, uma por item, numeradas, no formato
   de `references/como-falar.md`: a frase da linha `simples:`, o ID só no fim como `(ref: …)`, as
   respostas **aceitar**, **recusar** e **não sei**; até 5 por vez (acima disso, em lotes). A mesma pergunta (o mesmo
   delta, como uma promoção que volta em toda colheita) vinda de entradas diferentes é feita **uma vez**. Diga também,
   em palavras, cada linha `REJEITADO` da colheita: o candidato que não entrou e por quê. Com
   `sdd/invariants.md`, antes de perguntar:
   `bash sdd/bin/playbook-curator.sh --cruzar - sdd/playbook.md sdd/invariants.md <<'FIM_DOS_DELTAS'`, os deltas AUTO e PERGUNTA, sem as linhas de tipo inv, um por linha, e `FIM_DOS_DELTAS` (com o delimitador entre aspas, o shell não executa nada do texto da lição)
   — `INV_AFETADA` ⇒ o item daquela aposentadoria leva o `ajuste:` junto, como **uma opção só**;
   `INV_PENDENTE` ⇒ a contagem e a classificação vão na mesma opção (virar regra permanente com a
   linha `inv` do curador, descartar com motivo, ou não aplicar a contagem). Lição antiga que já mordeu e
   nunca foi classificada aparece na colheita como `INV_PENDENTE` e pede o mesmo item, uma vez: sem a
   resposta, a trava do item 5 segura tudo, e aí registre `Curadoria: FALHOU (invariantes sem
   classificação)`. Os itens aceitos entram no `lote-delta.txt`, menos a promoção: o delta `promovido_para=`
   só entra quando o mecanismo já está na branch padrão, então a promoção aceita vira pendência; as linhas de
   invariante aceitas (a `inv` do curador, o `ajuste:`, ou `REMOVER INV-nnn` / `REMOVER LM-nnn`), em
   `lote-inv.txt`. Sem linha `PERGUNTA`, não há pergunta de regra.
5. **Aplicar numa cópia e conferir 3 vezes — um `--aplicar` só para o lote inteiro.** Com `lote-delta.txt` e
   `lote-inv.txt` vazios (nada contado, nada aceito), pule este item e registre `Curadoria: nada aplicado`.
   `bash sdd/bin/playbook-curator.sh --aplicar "$TMPDIR/lote-delta.txt" sdd/playbook.md > "$TMPDIR/novo.md"`
   (exit 2 ⇒ nada foi impresso: corrija o delta). O `--aplicar` numera as lições novas pelo maior ID do playbook que
   recebe o delta: com um `--aplicar` só, os IDs saem seguidos e sem colidir, mesmo quando duas entradas propuseram o
   mesmo número; o recibo mostra o ID final. →
   `bash sdd/bin/playbook-lint.sh "$TMPDIR/novo.md"` (exit 0 obrigatório) →
   `bash sdd/bin/playbook-lint.sh --anti-collapse sdd/playbook.md "$TMPDIR/novo.md"` (bloqueou pelo
   tamanho ⇒ aplique em 2 ou mais commits: contadores e `ADD` primeiro, depois uma mudança de
   conteúdo por vez) → com invariantes,
   `bash sdd/bin/playbook-curator.sh --aplicar-inv "$TMPDIR/lote-inv.txt" sdd/invariants.md > "$TMPDIR/inv.md"`
   (sem linha aprovada, `cp sdd/invariants.md "$TMPDIR/inv.md"`) e
   `bash sdd/bin/playbook-curator.sh --validar-inv "$TMPDIR/novo.md" "$TMPDIR/inv.md"` (exit 0
   obrigatório; `🔴 trava INV:` diz a regra, a lição e as saídas: volte à pessoa, nunca copie; nunca
   edite as invariantes à mão).
   Só então `cp "$TMPDIR/novo.md" sdd/playbook.md` e, se mudou, `cp "$TMPDIR/inv.md" sdd/invariants.md`.
6. **Evidência** em `sdd/reports/evidence/LOTE_<AAAAMMDD>/`, no formato `$ comando`, a saída e `[exit=N]` com o
   exit real do comando: `CURATOR-entradas.log` (o `--conferir-entrada` de cada entrada, com o exit) e
   `CURATOR-delta.log` (o comando do item 5, o `lote-delta.txt` e o exit dele).
7. **Registrar o julgado e tirar da fila.** Só as entradas julgadas (conferidas e com bloco válido, ou `NADA A
   JULGAR`): `bash sdd/bin/playbook-curator.sh --registrar <entrada> [<entrada>…]` — grava as impressões em
   `sdd/releases/<F>/CURATOR-colhidos.txt` (a próxima publicação da feature não conta de novo) e apaga a entrada da
   fila. Entrada recusada ou com bloco reprovado 2 vezes **não** entra: ela fica na fila.
8. **Commit do lote:** `git add sdd/playbook.md` (e `sdd/invariants.md`, se mudou), os
   `sdd/releases/<F>/CURATOR-colhidos.txt` e a remoção das entradas (`git add -- sdd/curadoria/fila/<F>`, só as
   pastas registradas), e os 2 logs `CURATOR-*.log` só se o projeto versiona evidência (`git check-ignore -q` neles
   sai 1 e `git ls-files sdd/reports/evidence` não vem vazio). `git diff --cached --name-only` só pode listar esses
   arquivos; commit `chore(playbook): lote de curadoria — <n> publicação(ões), <d> delta(s)`. Nunca `--no-verify`:
   o pre-commit vigia o playbook.
9. **Recibo e envio.** Mostre o recibo **Decidi sozinho**: 1 linha por contagem aplicada, em palavras
   simples, e como desfazer (`git revert <sha do commit do lote>`). Depois, rode
   `python3 .agents/skills/sdd-release/scripts/push-de-papel.py . --branch <branch padrão> <arquivos do commit>` e faça a
   pergunta `[D1 · não se desfaz]` **Posso enviar o commit do lote para a branch padrão?**, dizendo se esse push
   publica (a frase da linha `→` do script). **sim** ⇒ aterrisse como no passo 5 da `sdd-release` (worktree temporário
   de `origin/<branch padrão>` + cherry-pick; em conflito, não resolva à mão: `git cherry-pick --abort`, e reaplique o
   `lote-delta.txt` sobre o playbook da base com `--aplicar`, que recalcula os IDs dos `ADD`, o `lote-inv.txt` sobre as
   invariantes da base com `--aplicar-inv`, e traga os logs do item 8 com `git checkout <sha do commit do lote> -- <cada
   log>`; os registros e as remoções da fila **nunca por checkout**, que apagaria o que outro lote gravou na base: para
   cada entrada julgada, se ela ainda está na fila da base, rode ali `--registrar` dela; se não está, outra frente já a
   julgou: tire do lote as linhas dela (o `lote-delta-<entrada>.txt`) antes de reaplicar), rode ali de novo o `playbook-lint.sh` e, com
   invariantes, o `--validar-inv` (ID repetido com a base ⇒ renumere o novo, nunca o da base) e faça o push como no
   passo 8 da `sdd-release`. **deixar para depois** ⇒ o commit fica na branch do lote, e as entradas continuam na fila
   da branch padrão até o envio. Com mudança de regra e envio na mesma resposta, as 2 perguntas vão numeradas.

Promoção aceita ⇒ o mecanismo é uma correção própria, com um caso que falha antes dele; o delta `promovido_para=`
só entra quando o mecanismo já está na branch padrão. Detalhes do formato na `SKILL.md` desta skill.

## Por que cada regra existe

- **A falha da colheita nunca vale como "nada a colher"** — o script sai 1 quando leu tudo e não achou
  nada, e 2 ou 64 quando não conseguiu ler; tratar os dois igual apagaria lições em silêncio.
- **Quem separa contagem de regra é o conferidor, não quem conduz o lote** — uma contagem só entra
  sem pergunta se o script a colheu e a evidência abre; assim ninguém inventa um `+1`.
- **O curador é conferido pela fronteira de escrita** — "não escreva" num brief é só texto; o snapshot de
  antes e de depois prova que ele só leu.
- **O lote julga a colheita refeita, não a guardada** — a guardada passa dias no git; refazê-la sobre a cópia dos
  documentos recusa a linha plantada depois da publicação e traz os IDs e as promoções do playbook de agora.
- **Um `--aplicar` só** — várias entradas propõem o mesmo número de lição nova; quem numera é o playbook que recebe.
- **Uma impressão conta na entrada mais antiga** — duas publicações da mesma feature em pastas paralelas podem colher
  a mesma linha; o `--conferir-entrada` a tira das entradas mais novas, e o lote nunca soma +2 por ela.
- **O commit do lote não sai da máquina sem um sim** — em muitos projetos, um push na branch padrão
  publica; a contagem entra no arquivo sem pergunta, o envio não.
