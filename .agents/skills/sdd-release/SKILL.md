---
name: sdd-release
description: >-
  Fase 4 do SDD Open — pipeline de publicação protegido em 4 fases: gate determinístico (lint, landmines, drift, Verify Gate), passadas de regressão e segurança, commit atômico com ledger em sdd/releases/, UMA aprovação humana antes do push/deploy, higiene do git e atualização da ficha da feature com curadoria do playbook. Use quando o usuário disser /sdd-release, "publica", "sobe pra produção" ou "faz o deploy".
compatibility: Requer bash >= 3.2 e git >= 2.20. Deploy, lint e drift vêm dos slots de sdd/config.yaml; slot vazio é pulado e declarado.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.4.0"
  updated: "2026-10"
  fase: "4"
---

# sdd-release — Fase 4

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-release v2.4.0 · out/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

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
   `feature_id`, `slice_id`, `versao`, `estado` (shipado | parcial | pausa), `dod`, `descricao`.
   Sem SHA (deriva do git). Arquivo novo a cada release: append-only. Ver `references/ledger.md`.
4. **Commit atômico.** `git add <arquivos específicos>` — **nunca `-A`**. Confira
   `git diff --cached --name-only`.
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
17b. **Curadoria do playbook (propõe; aplica só com OK por delta).** Colha do DESIGN
    (`✔ tratado` ⇒ `ajudou+1`), do BUILD_REPORT (`<<<CANDIDATO_PLAYBOOK` com `evidencia:` ⇒
    candidato `ADD`; sem evidência ⇒ rejeitado) e dos achados do avaliador/review cuja causa
    **já tinha bullet** (⇒ `mordeu+1`). Apresente cada delta como opção (múltipla escolha);
    aplique **só o aprovado**, rode `sdd/bin/playbook-lint.sh sdd/playbook.md` (exit 0
    obrigatório) e `--anti-collapse <antes> <depois>`, commite **só o playbook**. `mordeu ≥ 2`
    ⇒ pergunta obrigatória: promover a mecanismo (hook, check, script)? Detalhes na skill
    `sdd-playbook`.
18. **Imprimir a ficha** como último bloco do relatório.
19. **DoD fechado?** Oferecer arquivar (15b) e marcar a ficha como ✅ — com 1 OK.
20. **Prompt da próxima sessão** (o único opcional): se "Falta" não está vazio, oferecer.

## Gates de ABORTAR (parar e reportar, nunca pushar)

Fase 0a: landmines exit 2 · drift ≠0 · lint · Verify Gate `2` ou `5` · `3` não resolvido ·
`4` sem recibo · report-lint ≠0 · report-lint --pendente ≠0 · gate-shell-evidencia ≠0. Fase 0b: consumidor não modificado quebrado · invariante
violado. Fase 0c: credencial hardcoded · permissão frouxa · dado pessoal exposto. Fase 1:
arquivo inesperado no diff · conflito real · base moveu · escrita em produção sem source.

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
- **Avaliação `PENDENTE` aborta a release** — o build que travou antes do avaliador pode registrar o
  estado real; o que não pode é esse estado chegar a produção sem que ninguém tenha provado os critérios.
- **O exit de cada log é conferido** — `cmd | tail` grava o exit do `tail`, sempre 0: sem a
  conferência, um teste que falhou passa como evidência verde.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-release`. O resumo complementa a ficha, não a substitui.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
