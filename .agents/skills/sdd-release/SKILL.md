---
name: sdd-release
description: >-
  Fase 4 do SDD Open — pipeline de publicação protegido em 4 fases: gate determinístico (lint, landmines, drift, Verify Gate), passadas de regressão e segurança, commit atômico com ledger em sdd/releases/, UMA aprovação humana antes do push/deploy, higiene do git e atualização da ficha da feature com curadoria do playbook. Use quando o usuário disser /sdd-release, "publica", "sobe pra produção" ou "faz o deploy".
compatibility: Requer bash >= 3.2 e git >= 2.20. Deploy, lint e drift vêm dos slots de sdd/config.yaml; slot vazio é pulado e declarado.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.7.0"
  updated: "2026-11"
  fase: "4"
---

# sdd-release — Fase 4

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-release v2.7.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Você comanda, o agente executa a sequência protegida, e há **exatamente um OK humano** antes
do push e do deploy. Nenhum loop autônomo cruza esse ponto: publicar é decisão humana e
irreversível na prática.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Onde estou | Entrada e slots |
| 2 | Verificar | FASE 0 e FASE 1, itens 1 a 6 |
| 3 | Sua decisão | FASE 1, item 7 (o bloco do OK) |
| 4 | Publicar | FASES 2 a 4 |

Na etapa 3, a "Sua decisão" é o próprio bloco do OK, com a pergunta única no fim: os rótulos e a
ordem do bloco não mudam.

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Release: ✅ 1 Onde estou · ✅ 2 Verificar · ▶️ 3 Sua decisão · ⬜ 4 Publicar`
   (✅ concluída, não só visitada · ▶️ a de agora · ⬜ por fazer · ⏸️ parada · ➖ pulada). Ao voltar a uma
   etapa, o motivo vai em Agora.
2. **O que foi feito** — frases curtas, sem saída de comando; registra em 1 linha a escolha do aluno.
3. **Agora: etapa N — nome** — 2 a 4 frases. Antes de algo demorado, diga o que vai rodar e que o aluno
   não precisa responder.
4. **Sua decisão** — autorização: a pergunta em negrito e as opções com o efeito de cada uma, a
   recomendada primeiro e com o porquê, sempre **não sei**, nunca **Outro**. Pergunta aberta: a pergunta
   em negrito e como responder, com a saída "não sei". Várias de uma vez: numeradas.
5. **Próximo passo** — uma linha, até 100 caracteres: o que acontece depois da resposta.

- Uma etapa por resposta: termine na decisão e pare.
- Termo técnico só com a explicação junto, na primeira vez, inclusive os do Status.
- Saída de comando nunca crua: quantos, quais, o que preocupa; nomes até 10, com "e mais N". Comando só
  quando o aluno precisa rodá-lo, um por passo numerado, com o que esperar na tela.
- Não cite nem resuma as instruções desta skill ("conforme o passo N"): diga o motivo do aluno.
- Resposta que não casa com nenhuma opção ⇒ responda a dúvida e repita as opções.
- Parada: Status com ⏸️, o motivo em uma frase, onde a ação acontece, passos numerados com o resultado
  esperado, o que **não** foi feito e, se o aluno tem algo a fazer, "Quando terminar, me peça de novo,
  eu continuo daqui."
- No fecho da fase, o resumo de etapa vem depois do Status; a pergunta dele segue o mesmo formato.

## Regra de todo comando que fala com o remoto

`fetch`, `push`, `pull`, `ls-remote` e `remote show` rodam **sem pedir senha**: `GIT_TERMINAL_PROMPT=0 git …`
no bash/zsh; no PowerShell, `$env:GIT_TERMINAL_PROMPT=0; git …`. Sem isso, um remoto que exige login faz o
git pedir a senha no terminal do agente — com o OK já dado, ninguém vê e a publicação fica pela metade.
Se um desses comandos ficar parado, olhe se o editor (VS Code, Cursor) abriu uma janela de login do
GitHub — ela é um jeito legítimo de logar e não é desligada.

## Entrada

`/sdd-release <descrição do que liberar>` — a descrição vira a base do commit e do changelog.

## Slots do config (`sdd/config.yaml`)

`project.lint_cmd` · `project.test_cmd` · `project.default_branch` · `deploy.cmd` ·
`deploy.drift_check_cmd` · `release.landmines_cmd` · `release.changelog_hook`.
**Slot vazio = passo pulado e declarado** ("lint pulado — slot vazio"), nunca adivinhado.

## FASE 0 — Gate pré-release

**Filosofia:** o que um script pega, um script faz (segundos, determinístico). O caro (modelo)
só vai para o que script não pega: regressão de contrato e regra de negócio em código que já
funcionava. Passada que não se aplica ao diff é **pulada**, não "revisada sem achados".

**0. Pré-voo.** Confirme a branch (`git rev-parse --abbrev-ref HEAD` ≠ `default_branch`) e o
diff-base (`git merge-base origin/{default_branch} HEAD`).

**0a. Determinístico**, sobre `origin/{default_branch}...HEAD`, em paralelo:

1. **Landmines:** `{{LANDMINES_CMD}}` — exit 2 → **abortar**; exit 1 → avisos para o OK.
2. **Drift:** `{{DRIFT_CHECK_CMD}}` — o que chegou em produção sem commit? exit ≠0 → **abortar**.
3. **Lint:** `{{LINT_CMD}}` nos arquivos tocados — erro → **abortar**.
4. **Verify Gate do DEFINE (bloqueante quando há DEFINE):**
   ```bash
   sdd/bin/verify-gate.sh --strict sdd/features/DEFINE_{F}.md
   ```
   | Situação / exit | Ação |
   |---|---|
   | DEFINE com gate, `0` | verde — seguir |
   | `2` | **abortar**; voltar ao build |
   | `3` | resolver antes (rodar onde a ferramenta exista); com evidência alternativa equivalente é **waivable** (0d) |
   | `4` | exigir o **recibo humano** no BUILD_REPORT; sem recibo, não publicar |
   | `5` | **abortar** e voltar ao Define — spec ambígua não se dispensa |
   | DEFINE sem bloco (`64`) | não abortar: registrar **Aviso** "DEFINE anterior ao gate" |
   | sem DEFINE (fix pequeno) | rodar `bash sdd/bin/verify-gate.sh --sem-define <F>` (registra no trace que nenhum gate rodou) e declarar "sem DEFINE — SDD formal dispensado" |
5. **Relatório:** `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{F}.md` — `true`
   sem evidência, ou migration listada sem a linha provada em `## Migrations aplicadas`, abre
   **abortar**. Depois, `python3 sdd/bin/report-lint.py --pendente sdd/reports/BUILD_REPORT_{F}.md`:
   exit ≠ 0 ⇒ **abortar**, citando o exit e o `arquivo:linha` (avaliação `PENDENTE` não vai para
   produção). Exit 64 ou 127 ⇒ acrescente "atualize `sdd/bin/`: rode o `doctor` e, para o que ele
   apontar, apague e rode o `init`" — um `report-lint.py` antigo não conhece `--pendente`.
6. **Playbook:** `sdd/bin/playbook-lint.sh sdd/playbook.md` — exit 2 → abortar.
7. **Exit dos logs:** `bash sdd/bin/gate-shell-evidencia.sh` (os logs de `sdd/reports/evidence/`
   do diff) — exit ≠ 0 ⇒ **abortar**, citando cada `arquivo:linha`: um `[exit=N]` que é o exit do
   `tail` não prova o comando. Exit 64 ou 127 ⇒ a mesma frase de atualizar `sdd/bin/` do item 5.
8. **Review externo (obrigatório, com dispensa registrada):** `bash sdd/bin/adversarial-review.sh --conferir`
   — confere se a revisão mais nova de `review.output_dir` é **desta** versão do código (mesmo
   `diff_sha256`) e completou. Exit 0 ⇒ guarde a linha `review_externo: …` que ele imprimiu para o
   ledger. Exit 2 ⇒ antes do bloco do OK, faça a pergunta própria `[D3 · muda a regra do método]` de
   `references/como-falar.md`: **rodar agora** (o script sem `--conferir`, com `--feature {F}`, e o
   `--conferir` de novo) ou **publicar sem revisão** (o motivo da pessoa vira
   `review_externo: dispensado — <motivo>`). 2º revisor acionado e sem resultado ⇒ rode de novo com
   outra engine ou registre a dispensa dele com `--aceitar-sem-revisor2 "<motivo>"`. O OK continua
   sendo uma pergunta só: a dispensa é decidida antes dele.

Se 0a abortou, **nem inicie** as passadas de modelo.

**0b. Raio de impacto / regressão (modelo).** Para cada contrato alterado (assinatura, shape
de retorno, coluna, rota, permissão): quem consome e **não foi modificado**? Invariante de
negócio violado? Teste ao lado do módulo tocado ficou vermelho? Consumidor não modificado
quebrado = **crítico**.

**0c. Segurança (modelo — só se o diff toca auth, dados, permissões, rota pública).**
Credencial hardcoded, permissão frouxa, dado pessoal em log ou resposta, gate de acesso
removido.

**0d. Síntese — um veredito.**

| Classe | Achados | Efeito |
|---|---|---|
| **NON_WAIVABLE** | segurança crítica · drift · lint · consumidor quebrado · invariante violado · Verify Gate `2` ou `5` | **abortar aqui** com `arquivo:linha` |
| **WAIVABLE** (lista fechada) | Verify Gate `3` com evidência alternativa · teste vermelho comprovadamente pré-existente · recibo manual-ux pendente quando o deploy não altera superfície visual | vira **FAIL-candidato** para a decisão humana no OK |

| Veredito | Quando |
|---|---|
| 🟢 PASS | zero achado |
| 🟡 CONCERNS | zero crítico, ≥1 aviso → cada aviso vira pendência na ficha |
| 🔴 FAIL | ≥1 NON_WAIVABLE, ou FAIL-candidato que o humano mandou corrigir |
| ⚪ WAIVED | só FAIL-candidato dispensado **pelo humano** no OK, com registro `WAIVED · classe= · finding= · motivo= · por= · data=` |

**O agente nunca emite WAIVED.** Reporte também o que foi **pulado**.

## FASE 1 — Autônoma (só aborta se um gate falhar)

1. **Escopo.** Liste os arquivos desta release. Ignore WIP de outras frentes.
2. **Versão** (se o projeto versiona): bump a partir da versão em `origin/{default_branch}`,
   não da branch local. Colisão → próxima livre.
3. **Ledger** (dentro do commit atômico): `sdd/releases/{F}/{slice}_{versão-ou-data}.yaml` com
   `feature_id`, `slice_id`, `versao`, `estado` (shipado | parcial | pausa), `dod`, `descricao` e a
   linha `review_externo:` da 0a item 8 (a que o `--conferir` imprimiu, ou a dispensa com motivo).
   Sem SHA (deriva do git). Arquivo novo a cada release: append-only. Ver `references/ledger.md`.
4. **Commit atômico.** `git add <arquivos específicos>` — **nunca `-A`**. Confira
   `git diff --cached --name-only`. Logo depois, **nesta pasta** (a da frente) e antes do passo 5:
   `bash sdd/bin/adversarial-review.sh --ledger sdd/releases/{F}/<arquivo>.yaml` — exit ≠ 0 ⇒
   **abortar**: sem `review_externo` válido não se publica. Roda aqui porque a pasta da revisão é
   ignorada pelo git e não existe no worktree temporário do passo 5.
5. **Landar na branch padrão** via worktree temporário fresco de `origin/{default_branch}` +
   cherry-pick. Conflito → tentar aplicar só o incremento por patch (`git apply --check`); só
   abortar se os hunks se sobrepõem de verdade.
6. **Gates pré-push:** diff contra `origin/{default_branch}` tem só os arquivos esperados;
   nenhuma deleção de algo que está publicado; classificar se o diff deploya ou é no-op.
7. **PARAR e mostrar (o 1 OK) — um bloco só.** Antes, rode
   `python3 .agents/skills/sdd-release/scripts/deploy-espera-testes.py .` (só lê
   `.github/workflows/`). No **Agora**, duas frases: os campos já foram conferidos por você; a pessoa
   só responde à última linha — **sim** publica exatamente o descrito, **não** encerra sem publicar.
   Depois, **um bloco**, nesta ordem, preenchido (não acrescente perguntas):

   ```markdown
   **O que sobe:** <quantos arquivos e quais, pelo nome, em palavras — do diff contra a base,
   novos marcados como novos; até 10 nomes, "e mais N"; nunca o --stat colado>
   **O que muda em produção:** <uma frase em português — "muda o cálculo do relatório mensal", não
   "altera handler.js">
   **O push publica sozinho?** <sim, o workflow X publica ao receber o push na {default_branch} |
   não: <por quê>>
   **O deploy espera os testes?** <a frase da linha → do script, traduzida>
   **Banco:** <migration `<arquivo>` em `<projeto nome · ref>` em <data>, provada por leitura — de
   `## Migrations aplicadas` do BUILD_REPORT | sem migração nesta frente>
   **Verificações:** Verify Gate <exit> · report-lint <ok> · lint <ok | pulado — slot vazio> ·
   landmines <ok | N avisos> · drift <ok | pulado — slot vazio>
   **Veredito:** <🟢 PASS | 🟡 CONCERNS com a lista | FAIL-candidatos, cada um: corrigir ou WAIVED
   com `motivo=` seu> · achados que não abortaram
   **Ledger:** `feature_id` <id> · `estado` <shipado | parcial>

   **Posso finalizar (push + deploy + verificar)?**
   ```

   - **"O deploy espera os testes?"** é afirmação, não pergunta: vem do `RESULTADO:` do script.
     `SIM` ⇒ "sim — …"; `NAO` ⇒ "não — … um teste vermelho não impede a publicação"; `NAO_SE_APLICA`
     ⇒ "não se aplica: o push não publica"; `NAO_SEI` ⇒ leia os workflows citados e escreva **"não
     consegui afirmar: <motivo>"** — nunca "sim". Sem o script (pacote antigo), leia os workflows:
     teste com `continue-on-error`, `|| true` ou `exit 0` fixo **não** segura nada.
   - **"Banco:"** é afirmação: vem de `## Migrations aplicadas`. Migration no diff sem a linha ⇒ o
     report-lint já abortou na 0a.5.
   - **Verificação ausente dita como ausente** é informação; em silêncio, é falsa segurança.
   - **Uma pergunta só**, a última linha. Os rótulos com `?` são preenchidos por você. Ambiguidade
     (qual arquivo pertence à frente) vai **dentro** do bloco, antes da última linha — nunca pare
     duas vezes. Sem o OK, termine aqui: nada de push nem deploy.

## FASE 2 — Após o "go"

8. **Push.** Re-check de base: `GIT_TERMINAL_PROMPT=0 git fetch` + `git merge-base --is-ancestor origin/{default_branch} HEAD`
   (falhou → base moveu; re-landar). **Nunca `--force`.** `GIT_TERMINAL_PROMPT=0 git push origin HEAD:{default_branch}`.
   Recusado por permissão (`403`, `Permission denied`, `could not read Username`) ou por branch protegida
   (`protected branch`, `GH006`)? Pare e diga o que conferir, nesta ordem: `gh auth status` (logado, com a
   conta certa?); o papel no repositório (publicar exige escrita); e se a branch padrão é protegida — aí o
   caminho é push da branch + PR (`gh pr create`, ou o link que o próprio push imprime), não insistir.
9. **Deploy:** `{{DEPLOY_CMD}}` (vazio → declarar "deploy pulado — slot vazio"). Tudo que sobe
   para produção tem commit correspondente — deploy sem source commitado é proibido.
10. **Verificar — pelo commit publicado, não pelo último run.** `{{DRIFT_CHECK_CMD}}` exit 0; smoke da rota
    principal; e, se a publicação roda num workflow:
    - `gh run list --commit <SHA publicado> --branch {default_branch} --json databaseId,status,conclusion,workflowName,event`
      — o run **do workflow que publica**, na branch padrão (`event` = `push`, ou `workflow_dispatch` quando foi
      o redisparo manual do item abaixo). Com dois pushes seguidos,
      "o último run" é de outro commit; um run do mesmo SHA em outra branch ou de PR pode ter pulado o deploy.
    - `completed` + `success` ⇒ no ar (cite o run). `queued`/`in_progress` ⇒ esperar.
    - Lista vazia ⇒ o GitHub ainda não registrou o run: esperar alguns segundos e consultar de novo; vazia
      depois de ~2 min ⇒ dizer que não achou o run do commit — nunca concluir "nada a verificar". No caminho
      do PR, o SHA que chega à branch padrão é o do merge: consulte por ele.
    - `cancelled` ⇒ um push mais novo pode ter substituído o seu: `GIT_TERMINAL_PROMPT=0 git fetch origin
      {default_branch}`, depois `gh run list --workflow <arquivo> --branch {default_branch} --limit 20 --json databaseId,headSha,status,conclusion,createdAt`;
      só vale run `success` criado depois do seu **e** de um commit que contém o seu
      (`git merge-base --is-ancestor <seu SHA> <SHA dele>` sai 0). Sai 1 = aquele run **não** contém o seu
      commit (procure outro ou espere); qualquer outro código (commit não encontrado) = "não consegui
      confirmar", nunca "não incluído".
    - `failure` ⇒ para repetir, **nunca `gh run rerun` de um run antigo** (com fila, ele publica código
      velho por cima do novo): redisparar na ponta — `gh workflow run <arquivo> --ref {default_branch}` só se
      o workflow tiver `workflow_dispatch` no `on:`; sem ele (o GitHub responde 422), um push novo.
    - Verde não prova teste: step de teste com `continue-on-error`, `|| true` ou `exit 0` fixo ⇒ "o deploy
      terminou, mas o workflow não roda testes antes de publicar" (o `deploy-espera-testes.py` do
      item 7 já disse isso no bloco do OK).
    Sem `gh`: "publicado, sem verificação automática disponível" — nunca ✅ sem ter olhado.
11. **Changelog:** `{{CHANGELOG_HOOK}}` ou entrada curta (≤600 caracteres) no topo do
    `CHANGELOG.md`. O detalhe vive no ledger e no BUILD_REPORT.
12. **Limpeza** do worktree temporário.

## FASE 3 — Higiene do git

13. `GIT_TERMINAL_PROMPT=0 git fetch` · `git worktree prune`. 14. Branches já mergeadas: oferecer deletar.
15. Worktree/branch da feature: se a feature fechou, oferecer o comando de remoção (rodado
    fora dele). **15b.** Se esta release **fechou o DoD**, mover os artefatos SDD da família
    para `sdd/archive/{F}/` com `git mv` — um a um, nunca glob que arraste features de nome
    parecido. Feature aberta → pular (slices seguintes ainda leem os arquivos).
16. **Report final:** versão, SHAs, deploy, drift, o que foi para produção, arquivamento.

## FASE 4 — Ficha da feature e playbook

17. **Atualizar a ficha** (`/sdd-handoff`, incondicional): `sdd/handoffs/HANDOFF_{F}.md` — o
    que foi publicado, veredito 0d (WAIVED com registro completo), pendências separadas em
    🐛 bug fix e ✨ melhoria, avisos da Fase 0 que não abortaram, próximos passos com comandos,
    alertas. Ficha curta de "publicado, sem pendências" ainda documenta.
17b. **Curadoria do playbook (incondicional; roda depois do push e nunca desfaz a publicação).** Um
    script colhe, um agente sem esta conversa julga, e um conferidor separa a contagem da mudança de
    regra. Antes de começar, diga em 1 frase que a publicação já terminou e que agora você confere o que
    esta feature ensinou para as próximas. Brief do curador:
    `.agents/skills/sdd-playbook/references/curator.md`; palavras e exemplos: `references/como-falar.md`.
    1. **Staging por cópia.** `bash sdd/bin/playbook-curator.sh --preparar {F}` copia (nunca move) os
       documentos da feature, de `sdd/` ou de `sdd/archive/{F}/`, para a pasta que ele imprime em
       `staging:`; guarde-a como `STG`. Exit 1 = não achou DESIGN nem BUILD_REPORT: num conserto sem SDD
       formal, registre `Curadoria: 0 deltas (sem documentos)` e encerre o 17b; senão é falha (confira o
       nome da feature). **Sessão nova depois da parada do curador:** rode com `--retomar`, que não copia
       nem limpa, recalcule `STG` e `T` e vá direto para a parte "Na volta" do item 3: refazer o selo ou o
       snapshot de antes agora tomaria por linha de base o que o curador já escreveu. `--retomar` com exit 1, ou
       `"$T/antes"` ausente = a pasta temporária se perdeu: recomece deste item, sem `--retomar`; nada foi
       aplicado.
    2. **Colher, lendo o exit.**
       `bash sdd/bin/playbook-curator.sh --colher "$STG" sdd/playbook.md [--inv sdd/invariants.md] > "$STG/colheita.txt"; rc=$?; echo "$rc" > "$STG/colheita.rc"`
       — `--inv` só quando `sdd/invariants.md` existe; sem o arquivo, diga "invariantes: arquivo ausente,
       cruzamento pulado" e siga só com o playbook. O que uma curadoria anterior desta feature já julgou
       (`CURATOR-colhidos.txt`, item 7) não conta de novo: aparece como `JA_JULGADO`.
       | `rc` | Ação |
       |---|---|
       | `0` | há o que julgar ou relatar: seguir |
       | `1` | nada, de nenhum tipo: registre `Curadoria: 0 deltas` na ficha, diga que esta feature não trouxe lição nova nem contagem e encerre o 17b |
       | qualquer outro (`2`, `64`, `126`, `127`…) | **não é "0 deltas"**: pare o 17b, registre `Curadoria: FALHOU (rc=N)` e diga à pessoa a causa que o script imprimiu, o conserto e que a publicação não foi afetada |
    3. **Despachar o curador em contexto fresco**, pela escada de
       `sdd-build/references/contexto-fresco.md`, com **só** os 5 campos:
       `feature: {F} · staging: $STG · colheita: $STG/colheita.txt · playbook: <raiz>/sdd/playbook.md · worktree: <raiz>`.
       Antes do despacho, nesta ordem: `mkdir -p sdd/reports/briefs sdd/reports/evidence/{F} sdd/releases/{F}`;
       grave o brief (os 5 campos e "leia e siga
       `.agents/skills/sdd-playbook/references/curator.md`") em `sdd/reports/briefs/BRIEF_curador_{F}.md`;
       `T="${TMPDIR:-/tmp}/sdd-fronteira-$(git rev-parse --show-toplevel | git hash-object --stdin | cut -c1-12)/{F}/curador"; mkdir -p "$T"`;
       `bash sdd/bin/playbook-curator.sh --selar "$STG" > "$T/selo.txt"` (o selo do staging fica **fora** dele);
       `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/antes" <raiz>/sdd/reports/briefs/BRIEF_curador_{F}.md`;
       imprima `🧹 curadoria: julgando em contexto novo (alguns minutos); você não precisa responder`.
       Sem subagente: `bash sdd/bin/sdd-fluxo.sh despachar curador {F} sdd/reports/briefs/BRIEF_curador_{F}.md`
       e pare no exit 40, repassando a parada que ele imprime.
       Na volta, **sem editar nada no meio** e recalculando `STG` e `T` (variável de shell não passa de uma
       chamada para a outra): salve o bloco em `"$T/curadoria.txt"`;
       `bash sdd/bin/governanca-fronteira.sh --snapshot <raiz> "$T/depois" <raiz>/sdd/reports/briefs/BRIEF_curador_{F}.md`;
       `bash sdd/bin/governanca-fronteira.sh --comparar "$T/antes" "$T/depois" <raiz>/sdd/reports/briefs/BRIEF_curador_{F}.md > "$T/comparar.txt"`.
       Não repasse a linha `→` da fronteira (ela fala do DEFINE): quem lê o `comparar.txt` é o item 4.
    4. **Conferir o bloco antes de qualquer pergunta.**
       `bash sdd/bin/playbook-curator.sh --conferir-bloco "$STG/colheita.txt" "$T/curadoria.txt" sdd/playbook.md "$T/selo.txt" "$T/comparar.txt" > "$T/conferido.txt"; rc=$?`.
       Ele reprova (exit 2) quando o curador escreveu no projeto (`FORA:`) ou a fronteira não foi verificada,
       quando o staging mudou depois do selo, quando falta uma linha da colheita e quando uma contagem não
       é igual à que o script colheu. Exit 2 ⇒ despache de novo **1 vez**, com os 5 campos mais o campo
       `conferencia:` (as linhas `🔴 bloco:`). Se o motivo foi só o bloco, sem `FORA:` nem staging mexido,
       redespache com o mesmo selo e o mesmo snapshot. Se houve `FORA:` ou staging mexido: liste à pessoa o
       que saiu (não apague nada); com `sdd/playbook.md` ou `sdd/invariants.md` na lista, **não redespache**:
       registre `Curadoria: FALHOU (curador escreveu no playbook)`; nos outros casos, refaça os itens 1 e 2,
       o selo e o snapshot de antes (o que a pessoa já viu vira linha de base) e só então redespache. 2ª
       reprovação ⇒ registre `Curadoria: FALHOU (bloco inválido)`, diga que a curadoria fica para a próxima
       publicação e encerre: **nada é aplicado**. Nunca separe contagem de regra à mão: quem decide é o
       conferidor.
    5. **Contagem entra, regra pergunta.** Comece `: > "$STG/delta.txt"; : > "$STG/inv-linhas.txt"`. As linhas
       `AUTO <delta>` de `conferido.txt` vão para `"$STG/delta.txt"` sem pergunta. As linhas `PERGUNTA <n> <tipo> <delta>` (lição nova, aposentadoria,
       refino, promoção, invariante, sugestão que o curador confirmou e contagem que põe uma lição entre
       as invariantes) viram perguntas `[D3 · muda a regra do método]`, uma por item, numeradas, no formato
       de `references/como-falar.md`: a frase da linha `simples:`, o ID só no fim como `(ref: …)`, as
       respostas **aceitar**, **recusar** e **não sei**; até 5 por vez (acima disso, em lotes). Diga também,
       em palavras, cada linha `REJEITADO` da colheita: o candidato que não entrou e por quê. Com
       `sdd/invariants.md`, antes de perguntar:
       `printf '%s\n' <os deltas AUTO e PERGUNTA, sem as linhas de tipo inv> | bash sdd/bin/playbook-curator.sh --cruzar - sdd/playbook.md sdd/invariants.md`
       — `INV_AFETADA` ⇒ o item daquela aposentadoria leva o `ajuste:` junto, como **uma opção só**;
       `INV_PENDENTE` ⇒ a contagem e a classificação vão na mesma opção (virar regra permanente com a
       linha `inv` do curador, descartar com motivo, ou não aplicar a contagem). Lição antiga que já mordeu e
       nunca foi classificada aparece na colheita como `INV_PENDENTE` e pede o mesmo item, uma vez: sem a
       resposta, a trava do item 6 segura tudo, e aí registre `Curadoria: FALHOU (invariantes sem
       classificação)`. Os itens aceitos entram no `delta.txt`, menos a promoção: o delta `promovido_para=`
       só entra quando o mecanismo já está na branch padrão, então a promoção aceita vira pendência na
       ficha; as linhas de invariante aceitas (a `inv` do curador, o `ajuste:`, ou
       `REMOVER INV-nnn` / `REMOVER LM-nnn`), em `"$STG/inv-linhas.txt"`. Sem linha `PERGUNTA`, não há
       pergunta de regra.
    6. **Aplicar numa cópia e conferir 3 vezes.** Com `delta.txt` e `inv-linhas.txt` vazios (nada
       contado, nada aceito), pule este item, o commit e o envio, faça o item 7 e registre
       `Curadoria: nada aplicado`.
       `bash sdd/bin/playbook-curator.sh --aplicar "$STG/delta.txt" sdd/playbook.md > "$STG/novo.md"`
       (exit 2 ⇒ nada foi impresso: corrija o delta) →
       `bash sdd/bin/playbook-lint.sh "$STG/novo.md"` (exit 0 obrigatório) →
       `bash sdd/bin/playbook-lint.sh --anti-collapse sdd/playbook.md "$STG/novo.md"` (bloqueou pelo
       tamanho ⇒ aplique em 2 ou mais commits: contadores e `ADD` primeiro, depois uma mudança de
       conteúdo por vez) → com invariantes,
       `bash sdd/bin/playbook-curator.sh --aplicar-inv "$STG/inv-linhas.txt" sdd/invariants.md > "$STG/inv.md"`
       (sem linha aprovada, `cp sdd/invariants.md "$STG/inv.md"`) e
       `bash sdd/bin/playbook-curator.sh --validar-inv "$STG/novo.md" "$STG/inv.md"` (exit 0
       obrigatório; `🔴 trava INV:` diz a regra, a lição e as saídas: volte à pessoa, nunca copie; nunca
       edite as invariantes à mão).
       Só então `cp "$STG/novo.md" sdd/playbook.md` e, se mudou, `cp "$STG/inv.md" sdd/invariants.md`.
    7. **Evidência** em `sdd/reports/evidence/{F}/`, no formato `$ comando`, a saída e `[exit=N]` com o
       exit real do comando: `CURATOR-colheita.log` (o comando do item 2, `colheita.txt` e o exit guardado em
       `colheita.rc`) e `CURATOR-delta.log` (o comando do item 6, o `delta.txt` e o exit dele). E o registro do que já foi julgado, para a próxima publicação desta feature não contar
       de novo, ao lado do ledger: `grep ' · fp=' "$STG/colheita.txt" >> sdd/releases/{F}/CURATOR-colhidos.txt`.
    8. **Commit à parte:** `git add sdd/playbook.md` (e `sdd/invariants.md`, se mudou) e
       `sdd/releases/{F}/CURATOR-colhidos.txt` (sem o registro, a próxima publicação desta feature conta tudo
       de novo); os 2 logs `CURATOR-*.log` entram só se o projeto versiona evidência (`git check-ignore -q`
       neles sai 1 e `git ls-files sdd/reports/evidence` não vem vazio). Se o projeto não versiona nem
       `sdd/releases/`, diga que o registro fica só nesta pasta e que uma frente nova da mesma feature pode
       contar de novo. `git diff --cached --name-only` só pode listar esses arquivos; commit
       `chore(playbook): curadoria {F} — <n> delta(s)`. Nunca `--no-verify`: o pre-commit vigia o playbook.
    9. **Recibo e envio.** Mostre o recibo **Decidi sozinho**: 1 linha por contagem aplicada, em palavras
       simples, e como desfazer (`git revert <sha do commit da curadoria>`). Depois, a pergunta
       `[D1 · não se desfaz]` **Posso enviar o commit da curadoria para a branch padrão?**, dizendo se
       esse push publica sozinho (a resposta do item 7 da FASE 1). **sim** ⇒ aterrisse como no passo 5
       (worktree temporário de `origin/{default_branch}` + cherry-pick; em conflito, não resolva à mão:
       `git cherry-pick --abort`, e reaplique o `"$STG/delta.txt"` sobre o playbook da base com `--aplicar`, que recalcula os IDs dos
       `ADD`, e o `"$STG/inv-linhas.txt"` sobre as invariantes da base com `--aplicar-inv`), rode ali de novo o `playbook-lint.sh` e, com invariantes, o `--validar-inv` (ID repetido
       com a base ⇒ renumere o novo, nunca o da base) e faça o push como no passo 8. **deixar para a
       próxima publicação** ⇒ o commit fica na branch da frente; registre na ficha
       `Curadoria: commit <sha> não enviado` e o comando de envio. Com mudança de regra e envio na mesma
       resposta, as 2 perguntas vão numeradas.
    A ficha (18) ganha `Curadoria: <n> propostos / <m> aplicados / <p> promoções`. Promoção aceita ⇒ o
    mecanismo é uma correção própria, com um caso que falha antes dele; o delta `promovido_para=` só
    entra quando o mecanismo já está na branch padrão. Detalhes do formato na skill `sdd-playbook`.
18. **Imprimir a ficha** como último bloco do relatório.
19. **DoD fechado?** Oferecer arquivar (15b) e marcar a ficha como ✅ — com 1 OK.
20. **Prompt da próxima sessão** (o único opcional): se "Falta" não está vazio, oferecer.

## Gates de ABORTAR (parar e reportar, nunca pushar)

Fase 0a: landmines exit 2 · drift ≠0 · lint · Verify Gate `2` ou `5` · `3` não resolvido ·
`4` sem recibo · report-lint ≠0 · report-lint --pendente ≠0 · gate-shell-evidencia ≠0 · review externo sem revisão nem dispensa. Fase 0b: consumidor não modificado quebrado · invariante
violado. Fase 0c: credencial hardcoded · permissão frouxa · dado pessoal exposto. Fase 1:
arquivo inesperado no diff · conflito real · base moveu · escrita em produção sem source · `--ledger` ≠ 0.

## Quando pular o SDD formal

Fix pequeno com decisão clara pode pular BRAINSTORM/DEFINE/DESIGN — mas a sequência 0–20
vale **sempre**.

## Por que cada regra existe

- **O OK vem antes do push** — com deploy automático, depois do push não há "antes" para onde voltar.
- **`git add` por nome, nunca `-A`** — com outra frente aberta na mesma máquina, o `-A` publica o
  trabalho que nem terminou.
- **A base é integrada antes do OK e reconferida antes do push** — o que se aprova tem de ser o que vai
  subir; se outra frente entrou no meio, re-landar, nunca `--force`, que apagaria o trabalho dela.
- **Ledger dentro do commit atômico, append-only, sem SHA** — o registro e o código entram juntos ou não
  entram; o SHA sai do git, e copiá-lo no arquivo criaria um segundo dono para o mesmo fato.
- **O deploy é conferido pelo SHA publicado** — com dois pushes seguidos, o "último run" é de outro
  commit, e um run verde de outro commit não diz nada sobre o seu.
- **Nunca redisparar um run antigo** — o rerun usa o commit daquele run; com fila, ele roda depois do
  push mais novo e publica código velho por cima.
- **Uma pergunta só, na última linha do bloco** — duas paradas viram duas aprovações pela metade; a
  ambiguidade vai dentro do bloco, antes da pergunta.
- **A resposta sobre os testes antes do deploy vem do script** — a memória de como o workflow era não vale;
  `continue-on-error` ou `|| true` fazem um teste vermelho não segurar nada.
- **O agente nunca emite WAIVED** — dispensar um achado é decisão de quem responde pela publicação, e
  fica registrada com motivo e nome.
- **Comando remoto sem pedir senha** — o pedido de senha aparece no terminal do agente, não na tela da
  pessoa; com o OK já dado, a publicação trava pela metade sem ninguém ver.
- **Release sem DEFINE também deixa registro** — o trace com `no-define` separa o hotfix que pulou o
  gate de propósito do gate que ninguém rodou; sem ele, os dois somem do histórico do mesmo jeito.
- **Avaliação `PENDENTE` aborta a release** — o build que travou antes do avaliador pode registrar o
  estado real; o que não pode é esse estado chegar a produção sem que ninguém tenha provado os critérios.
- **O exit de cada log é conferido** — `cmd | tail` grava o exit do `tail`, sempre 0: sem a
  conferência, um teste que falhou passa como evidência verde.
- **Review externo obrigatório, com dispensa registrada** — quando era opcional, no projeto de origem só
  13 de 84 features tiveram review; a dispensa continua possível, mas com motivo escrito no ledger. O
  `sha256` liga a revisão a esta versão do código: uma revisão antiga não vale para um código novo.

- **A falha da colheita nunca vale como "nada a colher"** — o script sai 1 quando leu tudo e não achou
  nada, e 2 ou 64 quando não conseguiu ler; tratar os dois igual apagaria lições em silêncio.
- **Quem separa contagem de regra é o conferidor, não quem conduz a release** — uma contagem só entra
  sem pergunta se o script a colheu e a evidência abre; assim ninguém inventa um `+1`.
- **O curador é conferido pela fronteira de escrita** — "não escreva" num brief é só texto; o snapshot de
  antes e de depois prova que ele só leu.
- **O commit da curadoria não sai da máquina sem um sim** — em muitos projetos, um push na branch padrão
  publica; a contagem entra no arquivo sem pergunta, o envio não.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-release`. O resumo complementa a ficha, não a substitui.

### Fluxo encadeado

Ao fechar, rode `bash sdd/bin/sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só quando a linha
"Nesta skill" abaixo nomeia o `seguir` (contrato em `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
Exit 0: escreva a linha de transição que o script imprimiu, o recibo **Decidi sozinho** (se houver) e
chame a próxima fase nesta sessão. Exit 1 com `encadeamento desligado`: só o Próximo passo acima, sem
repassar a linha. Exit 1 por outro motivo: diga o motivo em 1 frase e mostre o Próximo passo. Exit 64:
repasse a saída e trate como desligado. A pergunta `[auto · de rotina]` com o encadeamento ligado
vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam perguntadas. "Pare"
desliga nesta chamada (`--parar`).

Nesta skill: não encadeia — publicar não se desfaz; a release sempre termina perguntando (D1).

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
