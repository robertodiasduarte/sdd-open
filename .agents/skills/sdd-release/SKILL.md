---
name: sdd-release
description: >-
  Fase 4 do SDD Open — pipeline de publicação protegido em 4 fases: gate determinístico (lint, landmines, drift, Verify Gate), passadas de regressão e segurança, commit atômico com ledger em sdd/releases/, UMA aprovação humana antes do push/deploy, higiene do git e atualização da ficha da feature com curadoria do playbook. Use quando o usuário disser /sdd-release, "publica", "sobe pra produção" ou "faz o deploy".
compatibility: Requer bash >= 3.2 e git >= 2.20. Deploy, lint e drift vêm dos slots de sdd/config.yaml; slot vazio é pulado e declarado.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.0.0"
  fase: "4"
---

# sdd-release — Fase 4

> Abra a resposta com o banner: `🧠 RELEASE`.

Você comanda, o agente executa a sequência protegida, e há **exatamente um OK humano** antes
do push e do deploy. Nenhum loop autônomo cruza esse ponto: publicar é decisão humana e
irreversível na prática.

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
   | sem DEFINE (fix pequeno) | pular e declarar "sem DEFINE — SDD formal dispensado" |
5. **Relatório:** `python3 sdd/bin/report-lint.py sdd/reports/BUILD_REPORT_{F}.md` — `true`
   sem evidência abre **abortar**.
6. **Playbook:** `sdd/bin/playbook-lint.sh sdd/playbook.md` — exit 2 → abortar.

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
7. **PARAR e mostrar (o 1 OK).** `git diff --stat`, classificação, o que cada mudança faz em
   produção, estado do Verify Gate (0a.4), veredito 0d (PASS / CONCERNS com a lista / ou os
   FAIL-candidatos — para cada um, **corrigir** ou **WAIVED** com `motivo=` do humano),
   achados que não abortaram, `feature_id` do ledger. Perguntar: **"Posso finalizar (push +
   deploy + verificar)?"**

## FASE 2 — Após o "go"

8. **Push.** Re-check de base: `git fetch` + `git merge-base --is-ancestor origin/{default_branch} HEAD`
   (falhou → base moveu; re-landar). **Nunca `--force`.** `git push origin HEAD:{default_branch}`.
9. **Deploy:** `{{DEPLOY_CMD}}` (vazio → declarar "deploy pulado — slot vazio"). Tudo que sobe
   para produção tem commit correspondente — deploy sem source commitado é proibido.
10. **Verificar:** pipeline verde; `{{DRIFT_CHECK_CMD}}` exit 0; smoke da rota principal.
11. **Changelog:** `{{CHANGELOG_HOOK}}` ou entrada curta (≤600 caracteres) no topo do
    `CHANGELOG.md`. O detalhe vive no ledger e no BUILD_REPORT.
12. **Limpeza** do worktree temporário.

## FASE 3 — Higiene do git

13. `git fetch` · `git worktree prune`. 14. Branches já mergeadas: oferecer deletar.
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
`4` sem recibo · report-lint ≠0. Fase 0b: consumidor não modificado quebrado · invariante
violado. Fase 0c: credencial hardcoded · permissão frouxa · dado pessoal exposto. Fase 1:
arquivo inesperado no diff · conflito real · base moveu · escrita em produção sem source.

## Quando pular o SDD formal

Fix pequeno com decisão clara pode pular BRAINSTORM/DEFINE/DESIGN — mas a sequência 0–20
vale **sempre**.

## Encerramento (obrigatório)

Feche com o **resumo de etapa** (`sdd/templates/fragments/RESUMO_ETAPA.md`); o 🏃 é
`/sdd-release`. O resumo complementa a ficha, não a substitui.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
