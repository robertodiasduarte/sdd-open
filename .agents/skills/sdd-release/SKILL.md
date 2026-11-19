---
name: sdd-release
description: >-
  Fase 4 do SDD Open — pipeline de publicação protegido em 4 fases: gate determinístico (lint, landmines, drift, Verify Gate), passadas de regressão e segurança, commit atômico com ledger em sdd/releases/, UMA aprovação humana antes do push/deploy e, depois dele, só papel: colheita do playbook para o lote, ficha por acréscimo e um commit só, sem nova pergunta (a única parada possível é o smoke vermelho depois do deploy). Use quando o usuário disser /sdd-release, "publica", "sobe pra produção" ou "faz o deploy".
compatibility: Requer bash >= 3.2 e git >= 2.20. Deploy, lint e drift vêm dos slots de sdd/config.yaml; slot vazio é pulado e declarado.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.19.0"
  updated: "2026-11"
  fase: "4"
---

# sdd-release — Fase 4

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-release v2.19.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Você comanda, o agente executa a sequência protegida, e há **exatamente um OK humano** antes do push e do
deploy. Nenhum loop autônomo cruza esse ponto: publicar é decisão humana e irreversível na prática.
**Projeto sem `sdd/bin/`** (sem o `init`; ex.: GitHub + Vercel com as skills soltas)? Siga `references/MODO_INICIANTE.md`.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Onde estou | Entrada e slots |
| 2 | Verificar | FASE 0 e FASE 1, itens 1 a 6b |
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
`deploy.drift_check_cmd` · `release.landmines_cmd` · `release.changelog_hook` · `smoke.before_ok_cmd` ·
`smoke.before_push_cmd` · `smoke.after_deploy_cmd`.
**Slot vazio = passo pulado e declarado** ("lint pulado — slot vazio"), nunca adivinhado. Os 3 de smoke rodam por
`bash sdd/bin/slot.sh <chave>`: `0` ok · `2` reprovou · `3` inconclusivo · `10` nada a medir · `11` pulado (slot
vazio) · `64` erro de configuração; nenhum deles vira "ok" fora do `0`.

## FASE 0 — Gate pré-release

**Filosofia:** o que um script pega, um script faz (segundos, determinístico). O caro (modelo)
só vai para o que script não pega: regressão de contrato e regra de negócio em código que já
funcionava. Passada que não se aplica ao diff é **pulada**, não "revisada sem achados".

**0. Pré-voo.** `bash sdd/bin/marca-fase.sh inicio release {F}` (custo da fase; sem o script, siga). Confirme a branch (`git rev-parse --abbrev-ref HEAD` ≠ `default_branch`) e o
diff-base (`git merge-base origin/{default_branch} HEAD`). Rode `bash sdd/bin/versao-nova.sh` (se existir):
exit 10 ⇒ a frase de versão nova (`references/como-falar.md`) no relatório e no bloco do OK, sem abortar; senão, nada.
Rode `bash sdd/bin/trilha.sh {F}` (base `origin/{default_branch}`): `TRILHA: curta` (sem DEFINE, até 3 arquivos e 100 linhas
fora dos documentos do SDD) ou `completa` (exit 1); o resultado vai para o ledger (`trilha:`). Exit 2 ou 64 (o script não decidiu) ⇒ grave `completa`, com o motivo.

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
   produção). Exit 64 ou 127 ⇒ acrescente "atualize `sdd/bin/`: rode o `upgrade` do pacote (o `doctor`
   diz o comando)" — um `report-lint.py` antigo não conhece `--pendente`.
6. **Playbook:** `sdd/bin/playbook-lint.sh sdd/playbook.md` — exit 2 → abortar.
7. **Exit dos logs:** `bash sdd/bin/gate-shell-evidencia.sh` (os logs de `sdd/reports/evidence/`
   do diff) — exit ≠ 0 ⇒ **abortar**, citando cada `arquivo:linha`: um `[exit=N]` que é o exit do
   `tail` não prova o comando. Exit 64 ou 127 ⇒ a mesma frase de atualizar `sdd/bin/` do item 5.
8. **Review externo (obrigatório, com dispensa registrada):** `bash sdd/bin/adversarial-review.sh --conferir`
   — confere se a revisão mais nova de `review.output_dir` é **desta** versão do código (mesmo
   `diff_sha256`) e completou. Exit 0 ⇒ guarde a linha `review_externo: …` que ele imprimiu para o
   ledger. Exit 2 ⇒ antes do bloco do OK; se os revisores não estão
   configurados (`adversarial-review.sh --dry-run` sai 64 "nenhum revisor") ou a credencial de uma engine falta,
   ofereça **antes** a skill `sdd-configurar-revisores` (a pergunta `[D2 · muda o produto]` de
   `references/como-falar.md`); configurada, rode a revisão. Depois disso, ou se o aluno não quer configurar, faça a
   pergunta própria `[D3 · muda a regra do método]` de `references/como-falar.md`: **rodar agora** (o script sem `--conferir`, com `--feature {F}`, e o
   `--conferir` de novo) ou **publicar sem revisão** (o motivo da pessoa vira
   `review_externo: dispensado — <motivo>`). 2º revisor acionado e sem resultado ⇒ rode de novo com
   outra engine ou registre a dispensa dele com `--aceitar-sem-revisor2 "<motivo>"`. O OK continua
   sendo uma pergunta só: a dispensa é decidida antes dele. Com revisão feita (não dispensada), confira
   também o ledger da revisão: `bash sdd/bin/ledger-revisao-lint.sh sdd/reviews/LEDGER_REVISAO_{F}.md` —
   exit 2 ⇒ **abortar**, citando cada `arquivo:linha` (achado sem a marca `dano`, `sim` sem o teste citado);
   exit 64 ⇒ o arquivo não existe ou está vazio: grave as linhas das rodadas pelo molde
   `sdd/templates/LEDGER_REVISAO_TEMPLATE.md` (rodada sem achados: `sem achados: rodada=N <pasta>`) e
   rode de novo. Sem esse registro, o custo por falha real de cada engine não se mede (`eval-revisores.sh`). Conserto de
   defeito de frente já publicada ⇒ a linha `escapou:` do molde no ledger da frente de origem (diz se a regra do 2º revisor volta atrás).

9. **Testes do diff:** `bash sdd/bin/test-baseline.sh --touched` (base `origin/{default_branch}`), **depois do item 4**,
   nunca em paralelo com ele (a suíte dos dois na mesma árvore inventa falha). Conta o teste alterado e o teste ao
   lado de cada fonte alterada (`foo.ts` → `foo.test.ts`). `2` ⇒ **abortar**, citando cada `🛑 nova:`; `3` ⇒
   WAIVABLE (0d); `0` com `RESULTADO: PULADO` ⇒ declare "pulado — test_cmd vazio"; as `⚠️ nova, fora do diff` vão
   para o bloco do OK.
10. **Segurança (varredura, em toda publicação):** `bash sdd/bin/seguranca-varredura.sh --saida sdd/reports/evidence/{F}/SEGURANCA.log`;
    com os documentos no repositório (trava `export-ignore` sob `sdd/`), também `bash sdd/bin/docs-varredura.sh .` (1 ⇒ FAIL; 64 ⇒ pulado e dito)
    — `2` ⇒ **abortar** (NON_WAIVABLE) com cada `🛑 Snn arquivo:linha` · `1` ⇒ CONCERNS · `64`/`127` ⇒ **abortar**; detalhe: `references/seguranca.md`.
11. **Desempenho (varredura, só aviso):** `bash sdd/bin/desempenho-varredura.sh --saida sdd/reports/evidence/{F}/DESEMPENHO.log`
    — `1` ⇒ CONCERNS · `64`/`127` ⇒ CONCERNS "varredura de desempenho não rodou: <causa>" · `0` siga; **nunca aborta**.

Se 0a abortou, **nem inicie** as passadas de modelo.

**0b. Raio de impacto por superfície (modelo).** O bug que passa está no código não modificado que depende do que
mudou. Liste, do diff, as superfícies com contrato: assinatura ou forma de retorno, coluna, rota, permissão, comando,
slot de configuração. Para cada uma, um agente fresco com o brief `references/raio-de-impacto.md` e só os 5 campos dele:
em paralelo quando o agente tem subagente; sem subagente, na própria sessão, uma superfície de cada vez, sem parada. O
brief pede os consumidores **não modificados**, as invariantes de `sdd/invariants.md` que tocam o módulo e o
`arquivo:linha` de cada um. Projeto sem `sdd/invariants.md`: passe `invariantes: ausente` e diga que essa parte foi pulada.
Se o teste ao lado do módulo tocado ficou vermelho, quem diz é o item 9 da 0a, não o modelo. Consumidor quebrado ou
invariante violada = **crítico** (0d). Diff sem
nenhuma superfície: declare a passada pulada, não "revisada sem achados".

**0c. Segurança (modelo — em toda publicação, com a lista fixa).** O diff contra cada item de `bash sdd/bin/seguranca-varredura.sh --checklist`
(os de maior risco primeiro), mais credencial no código, permissão afrouxada, dado pessoal em log e proteção removida; como marcar: `references/seguranca.md`.

**0d. Síntese — um veredito.**

| Classe | Achados | Efeito |
|---|---|---|
| **NON_WAIVABLE** | segurança crítica · bloqueio da varredura de segurança (S01, S11) · drift · lint · consumidor quebrado · invariante violado · Verify Gate `2` ou `5` · testes do diff `2` | **abortar aqui** com `arquivo:linha` |
| **WAIVABLE** (lista fechada) | Verify Gate `3` com evidência alternativa · testes do diff `3` · teste vermelho comprovadamente pré-existente · recibo manual-ux pendente quando o deploy não altera superfície visual · smoke antes do OK `2` (6b) | vira **FAIL-candidato** para a decisão humana no OK |

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
   `feature_id`, `slice_id`, `versao`, `data`, `estado` (shipado | parcial | pausa), `veredito`, `deploy` (no-op | real),
   `dod`, `descricao`, `trilha` (do item 0) — o bloco Publicado da ficha sai desses campos — e a
   linha `review_externo:` da 0a item 8 (a que o `--conferir` imprimiu, ou a dispensa com motivo).
   Sem SHA (deriva do git). Arquivo novo a cada release: append-only. Ver `references/ledger.md`.
4. **Commit atômico.** `git add <arquivos específicos>` — **nunca `-A`**. Confira
   `git diff --cached --name-only`. Logo depois, **nesta pasta** (a da frente) e antes do passo 5:
   `bash sdd/bin/adversarial-review.sh --ledger sdd/releases/{F}/<arquivo>.yaml` — exit ≠ 0 ⇒
   **abortar**: sem `review_externo` válido não se publica. Roda aqui porque a pasta da revisão é
   ignorada pelo git e não existe no worktree temporário do passo 5.
5. **Landar na branch padrão** via worktree temporário fresco de `origin/{default_branch}` +
   cherry-pick. Conflito → tentar aplicar só o incremento por patch (`git apply --check`); só
   abortar se os hunks se sobrepõem de verdade. Conflito só no `CHANGELOG.md`: a regra do passo 11.
6. **Gates pré-push:** diff contra `origin/{default_branch}` tem só os arquivos esperados;
   nenhuma deleção de algo que está publicado; classificar se o diff deploya ou é no-op.
6b. **Smoke antes do OK**, da pasta da frente (onde estão as dependências do projeto), sobre o que vai subir:
   `bash sdd/bin/slot.sh smoke.before_ok_cmd --feature {F} --base origin/{default_branch} --commit <SHA landado no passo 5> --arvore <worktree temporário do passo 5>`.
   `0` ok · `2` ⇒ FAIL-candidato no Veredito · `3` ⇒ aviso (inconclusivo) · `64` ⇒ aviso "erro de configuração" ·
   `10` ⇒ "nada a medir" · `11` ⇒ "pulado — slot vazio". Vai para a linha Verificações; nunca vira uma 2ª pergunta.
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
   **O commit de papel publica?** <a frase da linha → do push-de-papel.py, traduzida>
   **Banco:** <migration `<arquivo>` em `<projeto nome · ref>` em <data>, provada por leitura — de
   `## Migrations aplicadas` do BUILD_REPORT | sem migração nesta frente>
   **Segurança:** <varredura: nada achado | N aviso(s), os mais graves pelo id e arquivo> · recusados ou adiados no Define: <Snn, … | nenhum>
   **Desempenho:** <varredura: nada achado | nada novo (N já existiam) | sem banco | N aviso(s) novo(s), os mais graves pelo id e arquivo | não rodou: <causa>>
   **Verificações:** Verify Gate <exit> · report-lint <ok> · lint <ok | pulado — slot vazio> ·
   landmines <ok | N avisos> · drift <ok | pulado — slot vazio> ·
   testes do diff <ok | ok, N fora do diff | inconclusivo — WAIVABLE | pulado — test_cmd vazio> ·
   smoke <ok | reprovou — FAIL-candidato | nada a medir | pulado — slot vazio | inconclusivo | erro de configuração>
   **Veredito:** <🟢 PASS | 🟡 CONCERNS com a lista | FAIL-candidatos, cada um: corrigir ou WAIVED
   com `motivo=` seu> · achados que não abortaram
   **Ledger:** `feature_id` <id> · `estado` <shipado | parcial>

   **Posso finalizar (push + deploy + verificar + papel)?**
   ```

   - **"O deploy espera os testes?"** é afirmação, não pergunta: vem do `RESULTADO:` do script.
     `SIM` ⇒ "sim — …"; `NAO` ⇒ "não — … um teste vermelho não impede a publicação"; `NAO_SE_APLICA`
     ⇒ "não se aplica: o push não publica"; `NAO_SEI` ⇒ leia os workflows citados e escreva **"não
     consegui afirmar: <motivo>"** — nunca "sim". Sem o script (pacote antigo), leia os workflows:
     teste com `continue-on-error`, `|| true` ou `exit 0` fixo **não** segura nada.
   - **"O commit de papel publica?"** é afirmação: depois do deploy sai um commit só com a ficha, o changelog, a
     colheita e o arquivamento, enviado sem nova pergunta. Rode
     `python3 .agents/skills/sdd-release/scripts/push-de-papel.py . --branch {default_branch} <arquivos>` com os nomes
     **reais** que o commit vai ter: `sdd/handoffs/HANDOFF_{F}.md`, o arquivo do changelog (o `CHANGELOG.md` ou o que o
     hook grava), `sdd/curadoria/fila/{F}/<horário>/colheita.txt` e, com `estado: shipado`, cada documento da família
     que sai de `sdd/features/`, `sdd/reports/` e `sdd/reviews/` e o mesmo nome em `sdd/archive/{F}/`.
     `PUBLICA` ⇒ "sim — … : esse push publica de novo, sem código novo", e a ficha ganha a pendência ✨ com o trecho
     `paths-ignore` que o script imprime; `NAO_PUBLICA` ⇒ "não"; `NAO_SEI` ⇒ "não consegui afirmar: <motivo>", nunca "não".
   - **"Banco:"** é afirmação: vem de `## Migrations aplicadas`. Migration no diff sem a linha ⇒ o
     report-lint já abortou na 0a.5.
   - **Verificação ausente dita como ausente** é informação; em silêncio, é falsa segurança.
   - **Uma pergunta só**, a última linha. Os rótulos com `?` são preenchidos por você. Ambiguidade
     (qual arquivo pertence à frente) vai **dentro** do bloco, antes da última linha — nunca pare
     duas vezes. Sem o OK, termine aqui: nada de push nem deploy.

## FASE 2 — Após o "go"

Ao entrar aqui, diga à pessoa, **uma frase por etapa**, o que vem e se é obrigatório agora ou pode esperar: a
coluna "Para que serve" da tabela `## Depois do push — o que é cada etapa` de `references/como-falar.md`, sem
número de passo. A linha inteira (o que acontece sem a etapa) só quando ela pedir ou responder "não sei". Daqui
até o fim há **uma parada possível**: o smoke vermelho depois do deploy (item 10). O resto roda sem pergunta e
vai para o recibo **Decidi sozinho** do relatório final.

7b. **Smoke antes do push** (a produção ainda tem o código velho), com os argumentos do 6b:
   `bash sdd/bin/slot.sh smoke.before_push_cmd --feature {F} --base origin/{default_branch} --commit <SHA landado> --arvore <worktree temporário>`.
   O resultado nunca segura o push nem pede pergunta, seja qual for o exit: vai para o relatório final e para a ficha.
8. **Push.** Re-check de base: `GIT_TERMINAL_PROMPT=0 git fetch` + `git merge-base --is-ancestor origin/{default_branch} HEAD`
   (falhou → base moveu; re-landar). **Nunca `--force`.** `GIT_TERMINAL_PROMPT=0 git push origin HEAD:{default_branch}`.
   Recusado por permissão (`403`, `Permission denied`, `could not read Username`) ou por branch protegida
   (`protected branch`, `GH006`)? Pare e diga o que conferir, nesta ordem: `gh auth status` (logado, com a
   conta certa?); o papel no repositório (publicar exige escrita); e se a branch padrão é protegida — aí o
   caminho é push da branch + PR (`gh pr create`, ou o link que o próprio push imprime), não insistir.
9. **Deploy:** `{{DEPLOY_CMD}}` (vazio → declarar "deploy pulado — slot vazio"). Tudo que sobe
   para produção tem commit correspondente — deploy sem source commitado é proibido.
10. **Verificar — pelo commit publicado, não pelo último run.** `{{DRIFT_CHECK_CMD}}` exit 0; o smoke depois do deploy (abaixo); e, se
    a publicação roda num workflow:
    `bash sdd/bin/deploy-do-sha.sh --commit <SHA publicado> --workflow <arquivo> --branch {default_branch}`, na pasta da frente, a que
    tem o `sdd/config.yaml` (o worktree temporário do passo 5 pode não ter os passos passageiros). O `--workflow` vem do
    slot `deploy.workflow`; vazio, passe o arquivo que a linha ✅ do `deploy-espera-testes.py` citou no item 7. No caminho do PR, o
    SHA publicado é o do merge. O script espera até 40 minutos: rode em segundo plano, onde o agente permite; onde não, chame com
    `--teto 300` e repita enquanto sair 4, **no máximo 8 chamadas** (os mesmos 40 minutos), o que é seguro (nada é repetido por
    causa disso). Saiu 4 com "não achei nenhum run"? Não repita: diga que não achou o run do commit e que o push pode não
    acionar o workflow (`paths`, branch). Esgotadas as 8, diga "ainda não sei" citando o run, nunca ✅.

    | Exit | O que dizer |
    |---|---|
    | `0` | no ar, citando o run (a frase do script, com o substituto quando houver) |
    | `2` | não está no ar: a frase traz o run, o passo e por que não repetiu; para repetir, um push novo ou `gh workflow run` na ponta, **nunca `gh run rerun` de um run antigo** (com fila, ele publica código velho por cima do novo) |
    | `3` | "publicado, sem verificação automática disponível" — nunca ✅ sem ter olhado |
    | `4` | "ainda não sei": não é falha; repita ou abra o run citado, nunca "nada a verificar" |
    | `64` | chamada errada, SHA que o remoto também não conhece, ou `sdd/bin/` antigo: confira o SHA; o script antigo se resolve com o `upgrade` do pacote (o `doctor` diz o comando) |

    **Smoke depois do deploy.** Roda quando o deploy está confirmado: `deploy-do-sha.sh` `0` ou `3`, ou, sem workflow,
    `{{DEPLOY_CMD}}` saiu 0. Antes, `GIT_TERMINAL_PROMPT=0 git fetch` (o SHA do merge de um PR nasce no remoto); depois,
    da pasta da frente, `bash sdd/bin/slot.sh smoke.after_deploy_cmd --feature {F} --base origin/{default_branch} --commit <SHA publicado>`.
    Com `deploy-do-sha.sh` `2` ou `4`, `deploy.cmd` ≠ 0, deploy pulado ou diff que não publica, ele não roda, e o relatório diz por quê.
    `0` ok · `2` ⇒ pare e pergunte `[D1 · não se desfaz]` (formato em `references/como-falar.md`): **reverter** (`git revert`
    do commit, publicado por este mesmo fluxo), **corrigir** (volta ao build; pendência 🐛), **seguir com motivo** (falso
    positivo; o motivo vai para a ficha) ou **não sei** · `3` e `64` ⇒ pendência 🐛 na ficha, nunca ✅ · `10` e `11` declarados.

    **Evidência bruta.** Com a Release desta publicação no ar, `bash .agents/skills/sdd-release/scripts/anexar-bruto.sh {F} <tag>`
    anexa `sdd/reports/evidence/{F}/bruto/` (fora do git), varrido antes; sem parada: a frase e o 🐛 em `references/bruto.md`.

    Verde não prova teste: step de teste com `continue-on-error`, `|| true` ou `exit 0` fixo ⇒ "o deploy terminou, mas o
    workflow não roda testes antes de publicar" (o `deploy-espera-testes.py` do item 7 já disse isso no bloco do OK).
11. **Changelog:** `{{CHANGELOG_HOOK}}` ou entrada curta (≤600 caracteres) no topo do `CHANGELOG.md`; ela entra no
    commit de papel (item 16). O detalhe vive no ledger e no BUILD_REPORT. Conflito de changelog (a base moveu): pegue o
    da branch padrão, com as entradas das outras frentes, e ponha a sua no topo:
    `git show origin/{default_branch}:CHANGELOG.md > CHANGELOG.md`, sem depender de qual lado é "ours" na operação.
12. **Limpeza.** Remova o worktree temporário do passo 5 e rode `git worktree prune`.

## FASE 3 — Papel (sem pergunta; a publicação já terminou)

Toda mensagem daqui em diante diz que a publicação já terminou: uma espera sem isso parece deploy travado.

13. **Colheita.** O que esta feature ensinou para as próximas é só **colhido** aqui; quem julga é o lote da
    `sdd-playbook`, sob demanda (`.agents/skills/sdd-playbook/references/lote.md`). Nada de curador, pergunta de regra,
    playbook ou invariante mexidos nesta release.
    A ficha ainda não tem o que o item 14 vai escrever: um candidato anotado lá entra na próxima colheita da feature.
    `bash sdd/bin/playbook-curator.sh --enfileirar {F} sdd/playbook.md [--inv sdd/invariants.md]` (`--inv` só com o arquivo):
    | exit | Ação |
    |---|---|
    | `0` | a entrada `sdd/curadoria/fila/{F}/<horário>/` (a linha `fila:`) vai no commit de papel; na ficha, `Curadoria: na fila`. Uma linha `⚠️ … não está commitado` quer dizer que as linhas daquele documento ficaram sem julgamento: diga isso na ficha, com o comando que a linha dá |
    | `1` com `RESULTADO: NADA A COLHER` | `Curadoria: 0 deltas` na ficha |
    | `1` com `RESULTADO: STAGING SEM DOCUMENTOS` | na trilha curta (conserto sem DESIGN nem BUILD_REPORT): `Curadoria: 0 deltas (sem documentos)`; na trilha completa, é falha: `Curadoria: FALHOU (sem documentos)` — confira o nome da feature |
    | `2` | **não é "0 deltas"**: a entrada fica na fila marcada com o exit (vai no commit de papel), a ficha diz `Curadoria: FALHOU (rc=N)` com a causa que o script imprimiu; a publicação não foi afetada |
    | outro (`64`, `126`, `127`…) | **não é "0 deltas"**: `Curadoria: FALHOU (rc=N)` na ficha, com a causa e o conserto |
    Depois, `bash sdd/bin/playbook-curator.sh --fila`: exit 10 ⇒ repasse a linha 🧹 em 1 frase no relatório final (a fila
    passou de 5 publicações), sem perguntar e sem rodar o lote; nada roda sozinho.
14. **Ficha.** `python3 sdd/bin/ficha-publicado.py {F} --ref origin/{default_branch}` (depois de um `git fetch`: o SHA é
    o do commit publicado, não o da frente) grava o bloco `## Publicado` da ficha a partir dos ledgers
    (exit 2 ⇒ um ledger ilegível: a linha dele diz `n/d`; cite-o no relatório). Depois, pela `sdd-handoff`, você escreve
    **só** o que o ledger não diz: `## Falta` (pendências em 🐛 bug fix e ✨ melhoria, os avisos da Fase 0 que não
    abortaram), os alertas (as de segurança e a linha fixa `/sdd-seguranca app <URL>`: `references/seguranca.md`), a
    linha `Curadoria:` do item 13, o veredito 0d (WAIVED com registro completo) e, com `PUBLICA` no item 7, a pendência
    ✨ de tirar os documentos do gatilho do deploy, e o Status (✅ com `estado: shipado`; senão 🚢). Nada do que está no
    bloco Publicado se repete no "Histórico de slices". Ledger com `trilha: curta` ⇒ **ficha curta**: Ficha, Publicado e Falta, até 20 linhas.
    `python3 sdd/bin/handoff-lint.py sdd/handoffs/HANDOFF_{F}.md` sai 0 (na trilha curta, com `--curta`, que reprova
    acima de 20 linhas fora do prompt de retomada).
15. **Arquivamento.** Ledger desta release com `estado: shipado` ⇒ mova os artefatos SDD da família para
    `sdd/archive/{F}/` com `git mv`, um a um, nunca glob que arraste features de nome parecido (o Status ✅ da ficha já
    veio no item 14). `parcial` ou `pausa` ⇒ pule (slices seguintes ainda leem os arquivos). A faxina retroativa do passivo é outra
    operação, deliberada: `python3 sdd/bin/sdd-archive.py` (simulação por padrão; depois, `--lote <nome> --aplicar`,
    um lote por commit).
16. **Commit de papel.** Um commit só, com a ficha, o `CHANGELOG.md`, a fila da feature (a entrada nova, a falha
    registrada ou a remoção de uma falha antiga que a colheita substituiu: `git add -- sdd/curadoria/fila/{F}`) e os
    `git mv` do item 15: `git add` por nome, `git diff --cached --name-only` só com esses, commit
    `docs({F}): ficha, changelog e colheita`. Nunca `--no-verify`. Rode de novo o `push-de-papel.py` com a lista real
    (`git diff --cached --name-only` antes do commit): se ele disser `PUBLICA` ou `NAO_SEI` e o item 7 disse "não", o
    commit **não** é enviado (o OK não cobriu um deploy a mais): fica na branch da frente, e o relatório diz por quê e dá
    o comando de envio. Senão, `GIT_TERMINAL_PROMPT=0 git fetch`, aterrisse como no passo 5 e envie como no passo 8,
    **sem nova pergunta**: o OK já cobriu o papel; depois, remova o worktree temporário do aterrissamento. Push recusado ou conflito que a regra do item 11 não resolve ⇒ o commit fica na branch da frente, sem
    `--force`, e o relatório final dá o comando de envio; nada é apagado no item 17.
17. **Branch da frente.** Com o commit de papel em `origin/{default_branch}`: se a branch da frente existe no remoto
    (`git ls-remote --heads origin <branch>`) e já está toda integrada (a release aterrissa por cherry-pick, então o
    teste é por conteúdo: `GIT_TERMINAL_PROMPT=0 git fetch origin <branch>` e `git cherry origin/{default_branch} origin/<branch>`
    sem nenhuma linha `+`; `git cherry` que sai ≠ 0 ⇒ não apague, porque saída vazia de um comando que falhou não prova nada), apague-a: `GIT_TERMINAL_PROMPT=0 git push origin --delete <branch>`, com a linha
    de recibo e o comando que desfaz (`git push origin <sha>:refs/heads/<branch>`). Sobra linha `+` (commit que não
    entrou), ou o item 16 não enviou ⇒ não apague e diga por quê. A branch local e a worktree não se apagam de dentro dela: o relatório final
    dá o comando, rodado de fora (`git worktree remove "<pasta>"` e `git branch -D <branch>`: o `-d` recusa, porque a
    release aterrissa por cherry-pick; a integração já foi conferida pelo `git cherry`, e sem ela o comando não vai).

## FASE 4 — Relatório

18. **Relatório final.** Versão, SHAs, deploy, drift, os 3 smokes (resultado de cada um), o que foi para produção, o
    commit de papel (enviado ou o comando de envio), o recibo **Decidi sozinho** (uma linha por coisa feita sem
    pergunta, com o comando que desfaz: arquivamento, branch remota, papel), a linha 🧹 da fila se houve, o comando
    de limpeza local e a ficha **pelo caminho**, sem imprimi-la. O resumo de etapa do encerramento não repete essas
    linhas: ele diz onde estamos e o que vem depois. A ficha já tem o "Prompt de retomada"; não ofereça outro.

## Gates de ABORTAR (parar e reportar, nunca pushar)

Fase 0a: landmines exit 2 · drift ≠0 · lint · Verify Gate `2` ou `5` · `3` não resolvido · testes do diff com falha nova ·
`4` sem recibo · report-lint ≠0 · report-lint --pendente ≠0 · gate-shell-evidencia ≠0 · playbook-lint `2` · review externo sem revisão nem dispensa · ledger-revisao-lint `2`. Fase 0b: consumidor não modificado quebrado · invariante
violado. Fase 0a.10: varredura de segurança `2` · `64` · `127`. Fase 0c: credencial hardcoded · permissão frouxa · dado pessoal exposto. Fase 1:
arquivo inesperado no diff · conflito real · base moveu · escrita em produção sem source · `--ledger` ≠ 0.

## Quando pular o SDD formal

Fix pequeno com decisão clara pode pular BRAINSTORM/DEFINE/DESIGN. As FASES 0 a 2 valem **sempre**, nas duas trilhas;
o que muda é a parte depois do push. Quem decide a trilha é o `trilha.sh` do item 0, nunca o agente: **curta** (sem
DEFINE, até 3 arquivos e 100 linhas fora dos documentos do SDD, sem binário) ⇒ ficha curta (Ficha, Publicado e Falta,
até 20 linhas) e a colheita, que sem DESIGN nem BUILD_REPORT dá `0 deltas (sem documentos)`; **completa** ⇒ tudo.

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
- **Os testes do diff rodam antes do OK, por script** — perguntar ao modelo se o teste ao lado do código mudado
  ficou vermelho dá a resposta que ele imaginou; o `--touched` roda o teste e só aborta pela falha nova do diff.
- **O smoke tem peso por momento** — antes do OK, quem decide é a pessoa, no mesmo bloco; depois do "sim", uma 2ª
  parada antes do push quebraria o OK único; depois do deploy, o que está no ar pede a decisão de reverter na hora.
- **Review externo obrigatório, com dispensa registrada** — quando era opcional, no projeto de origem só
  13 de 84 features tiveram review; a dispensa continua possível, mas com motivo escrito no ledger. O
  `sha256` liga a revisão a esta versão do código: uma revisão antiga não vale para um código novo.

- **A falha da colheita nunca vale como "nada a colher"** — o script sai 1 quando leu tudo e não achou
  nada, e 2 ou 64 quando não conseguiu ler; tratar os dois igual apagaria lições em silêncio. A entrada que falhou
  fica na fila, marcada, até uma colheita nova a substituir.
- **A release só colhe; o julgamento é do lote** — no projeto de origem, 18 de 30 curadorias não trouxeram regra nova,
  e 37 de 43 deltas eram só contagem: julgar uma por publicação, no meio da release, custava as paradas depois do OK.
  As garantias (conferidor, fronteira de escrita, pergunta para toda mudança de regra) foram junto para o lote.
- **Um commit de papel, coberto pelo OK** — 28 de 49 deploys medidos não tinham arquivo publicável; um commit só, com
  a pessoa sabendo antes se ele publica, troca várias paradas e vários deploys por nenhuma.
- **Uma parada só depois do OK** — o que está no ar e quebrou pede decisão na hora; o resto (arquivar, apagar a
  branch remota já integrada, colher) se desfaz com um comando, que vai no recibo.
- **A ficha cresce por acréscimo** — a mesma publicação escrita 6 vezes (ficha, histórico, ledger, changelog,
  relatório, resumo) deixa fichas de 140 a 234 linhas; o bloco Publicado sai do ledger por script, e o agente
  escreve só o que o ledger não diz.
- **A trilha é decidida por comando** — "conserto pequeno" no juízo do agente vira o que ele quiser naquele dia.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-release`. O resumo não repete o relatório final nem a ficha: diz onde estamos e o que vem depois. Antes dele, `bash sdd/bin/marca-fase.sh fim release {F}` e `bash sdd/bin/custo-feature.sh {F}`, que grava `sdd/reports/CUSTO_{F}.md` (`sdd/templates/fragments/MARCA_FASE.md`).

### Fluxo encadeado

Ao fechar, rode `bash sdd/bin/sdd-fluxo.sh seguir <fase> <DEFINE> <próxima>` só quando a linha
"Nesta skill" abaixo nomeia o `seguir` (contrato em `sdd/templates/fragments/FLUXO_ENCADEADO.md`).
Exit 0: escreva a linha de transição que o script imprimiu, o recibo **Decidi sozinho** (se houver) e
chame a próxima fase nesta sessão. Exit 1 com `encadeamento desligado`: só o Próximo passo acima, sem
repassar a linha. Exit 1 por outro motivo: diga o motivo em 1 frase e mostre o Próximo passo. Exit 64:
repasse a saída e trate como desligado. A pergunta `[auto · de rotina]` com o encadeamento ligado
vira a opção recomendada e uma linha do recibo; as marcadas D1 a D5 continuam perguntadas. "Pare"
desliga nesta chamada (`--parar`).

Nesta skill: não encadeia — publicar não se desfaz; a release sempre pergunta antes de publicar (D1, o OK).

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
