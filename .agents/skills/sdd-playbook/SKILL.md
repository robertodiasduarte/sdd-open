---
name: sdd-playbook
description: >-
  Playbook de landmines do projeto em sdd/playbook.md, formato ACE-lite — bullets com ID estável (LM-nnn), contadores ajudou/mordeu, superfícies greppáveis e atualização só por delta. Ativa em toda sessão: lê apenas a seção "## Sempre" no início; o resto entra por superfície via sdd/bin/playbook-lint.sh --grep. Nunca reescreve, comprime ou apaga bullets — uma sessão só PROPÕE candidatos; quem aplica é a fase Release, com OK humano por delta. Use quando alguém disser "isso já mordeu antes?", "registra essa armadilha", /sdd-playbook, ou ao tocar qualquer superfície durante Design e Build.
compatibility: Requer bash >= 3.2 e git >= 2.20 (sdd/bin/playbook-lint.sh).
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.0.0"
  fase: "transversal"
---

# sdd-playbook — landmines com ID, contadores e delta updates

Fonte: ACE (Agentic Context Engineering, arXiv 2510.04618). O que portamos: **delta updates
itemizados** (sem eles o ganho do paper cai de +12,5 para +3,6) e um **papel que julga separado
do que executa**. O que **não** portamos: curador autônomo (lição auto-gerada sem verificação
piora), dedup por embedding, carga integral em toda sessão.

## Início de sessão (obrigatório, silencioso)

Ler **só** a seção `## Sempre` — nunca o arquivo inteiro:

```bash
awk '/^## Sempre/{f=1;next} /^## /{f=0} f' sdd/playbook.md
```

Aplicar sem anunciar. As demais seções entram **por superfície**, quando a superfície é tocada:

```bash
sdd/bin/playbook-lint.sh --grep "<arquivo|comando|tabela|conceito>" sdd/playbook.md
```

Casa os termos de `sup:`; imprime os `LM-nnn`; exit 1 quando não há nenhum (ausência é
informação). `--grep-all` busca no bloco inteiro quando você não sabe a superfície. A fase
Design faz isso por superfície do manifest e registra em `## Landmines aplicáveis`; a fase Build
repete e registra só os IDs em `## Landmines lidas no build`. É esse `✔ tratado` que vira
`ajudou` na curadoria.

## Formato (o lint é o juiz — `sdd/bin/playbook-lint.sh sdd/playbook.md`)

```markdown
- [LM-014] ajudou=1 mordeu=0 · conf=2026-09-02 · sup: `pedido` `status_pagamento` :: regra em 1–3 linhas. **Do instead:** ação concreta. → ficha: HANDOFF_X · promovido_para: —
- [LM-007] ☠ 2026-09-02 :: motivo da aposentadoria                      (só sob ## Tombstones)
```

- `LM-nnn` é único e **nunca reusado**; `sup:` ≥1 termo greppável em crase; `Do instead:`
  obrigatório; `→ ficha:` aponta para `sdd/handoffs/<nome>.md` ou incidente (o bullet aponta,
  nunca duplica); `promovido_para:` = path do mecanismo (hook, check, script) quando a landmine
  virou código, ou `—`.
- Seções na ordem fixa: `Sempre` (≤10 bullets, ≤1.500 palavras) · `Dados` · `Backend` ·
  `Frontend` · `Infra / deploy` · `Reviews / harness` · `Domínio` · `Tombstones` (última).
  Só `Sempre` e `Tombstones` são obrigatórias; troque as intermediárias em
  `PLAYBOOK_SECTIONS` se o seu projeto precisar (mesma ordem, `|` entre nomes).

## Papéis

| Papel | Quem | O que faz |
|---|---|---|
| Generator | você, em qualquer sessão | cita `LM-nnn` em `## Landmines aplicáveis` (`✔ tratado` vira `ajudou`); pode **propor** candidato |
| Reflector | artefatos existentes | achados do avaliador fresco, Advisor Ledger, incidentes, gate vermelho, `WAIVED` — achado cuja causa **já tinha bullet** ⇒ `mordeu+1` |
| Curator | passo 17b da fase Release, com o humano decidindo por delta | propõe `ajudou`/`mordeu` · `ADD` · `TOMBSTONE` · `REFINE` · `promovido_para=` com evidência `arquivo:linha`; aplica **só o aprovado** (lint verde, `--anti-collapse` verde, commit só do playbook); `mordeu ≥ 2` ⇒ pergunta de promoção obrigatória |

A escrita legítima no playbook é a fase Release (delta aprovado) — ou, fora dela, um commit
revisado com lint verde e OK humano. Nunca "no meio do trabalho".

## Proibições (o lint aplica)

- **Não reescrever, comprimir, reordenar em massa ou renumerar.** `--anti-collapse <antes>
  <depois>` bloqueia quando um `LM-` desaparece ou >20% dos bullets mudam de conteúdo/seção
  (contadores e `conf` não contam). Reescrita grande = 2+ commits.
- **Não apagar.** Aposentar = mover para `## Tombstones` como `- [LM-nnn] ☠ data :: motivo`.
- **Não escrever a partir da fase Design** (a varredura é read-only).
- **Não inflar `## Sempre`**: só landmine de sessão sem superfície greppável.

## Candidato — o único jeito de uma sessão "escrever"

No BUILD_REPORT (seção "Candidatos ao playbook") ou na ficha, bloco literal:

```text
<<<CANDIDATO_PLAYBOOK
secao: Backend
sup: `termo1` `termo2`
regra: … **Do instead:** …
evidencia: caminho do log/incidente/AT que prova que mordeu (ou DESIGN onde ajudou)
ficha: HANDOFF_X (se existir; senão "—")
mordeu_antes: LM-nnn (se a causa já tinha bullet) | —
>>>
```

Sem `evidencia:` o candidato não é candidato (lição sem verificação piora o contexto).

## Escada de promoção

`mordeu ≥ 2` = a regra escrita não bastou. O destino é um **mecanismo** (hook de pre-commit,
check no gate, script), e o bullet ganha `promovido_para:`; cai para `## Tombstones` só quando
o mecanismo tiver caso de teste que **falha** sem ele. `sdd/bin/playbook-lint.sh --stats`
conta por `mordeu`.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
