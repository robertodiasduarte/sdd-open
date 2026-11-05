---
name: sdd-playbook
description: >-
  Playbook de landmines do projeto em sdd/playbook.md, formato ACE-lite — bullets com ID estável (LM-nnn), contadores ajudou/mordeu, superfícies greppáveis e atualização só por delta. Ativa em toda sessão: lê apenas a seção "## Sempre" no início; o resto entra por superfície via sdd/bin/playbook-lint.sh --grep. Nunca reescreve, comprime ou apaga bullets — uma sessão só PROPÕE candidatos; quem aplica é a fase Release, com OK humano por delta. Use quando alguém disser "isso já mordeu antes?", "registra essa armadilha", /sdd-playbook, ou ao tocar qualquer superfície durante Design e Build.
compatibility: Requer bash >= 3.2 e git >= 2.20 (sdd/bin/playbook-lint.sh); a curadoria (sdd/bin/playbook-curator.sh) também pede python3 >= 3.9.
license: MIT
metadata:
  author: Roberto Dias Duarte
  version: "2.2.0"
  updated: "2026-11"
  fase: "transversal"
---

# sdd-playbook — landmines com ID, contadores e delta updates

Na primeira resposta desta skill, comece com esta linha, uma vez só, antes do Status:
`sdd-playbook v2.2.0 · nov/2026 · versão atual: https://github.com/robertodiasduarte/sdd-open/releases/latest`

Fonte: ACE (Agentic Context Engineering, arXiv 2510.04618). O que portamos: **delta updates
itemizados** (sem eles o ganho do paper cai de +12,5 para +3,6) e um **papel que julga separado
do que executa**. O que **não** portamos: curador autônomo (lição auto-gerada sem verificação
piora), dedup por embedding, carga integral em toda sessão.

## Como falar com o aluno

Leia `references/como-falar.md` antes da primeira resposta: o glossário desta skill, o Status preenchido
e um exemplo completo. Pergunta e parada seguem `sdd/templates/fragments/PERGUNTA_DECISAO.md`.
Quem usa esta skill, em geral, nunca usou git nem terminal.

| Etapa | Nome para o aluno | Passos desta skill |
|---|---|---|
| 1 | Leitura | Início de sessão |
| 2 | Candidato | Candidato |
| 3 | Promoção | Escada de promoção |

A etapa 1 é silenciosa: não gera resposta própria. A camada vale quando a skill fala com o aluno
(propor um candidato, pedir o OK de uma promoção).

Toda resposta, nesta ordem (pule a parte sem conteúdo):

1. **Status** — uma linha que começa pelo nome da fase: `Playbook: ✅ 1 Leitura · ▶️ 2 Candidato · ⬜ 3 Promoção`
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
| Curator | passo 17b da fase Release: um script colhe, um agente sem a conversa julga, a pessoa decide | `sdd/bin/playbook-curator.sh --colher` lê `ajudou`/`mordeu` das tabelas, `mordeu` dos achados, candidatos e promoções; o curador (`references/curator.md`) confere cada linha contra o `arquivo:linha` e devolve o bloco de curadoria, sem escrever nada; `--conferir-bloco` reprova bloco incompleto e separa a contagem com evidência (entra sem pergunta, vai para o recibo) da mudança de regra — `ADD`, `TOMBSTONE`, `REFINE`, `promovido_para=`, invariante —, que só entra com o seu OK; `mordeu ≥ 2` ⇒ pergunta de promoção obrigatória |

A escrita legítima no playbook é a fase Release (delta aprovado) — ou, fora dela, um commit
revisado com lint verde e OK humano. Nunca "no meio do trabalho". Quem aplica é sempre
`sdd/bin/playbook-curator.sh --aplicar <delta> sdd/playbook.md`, que valida o delta inteiro antes de
editar e imprime o playbook novo; o resultado passa pelo lint antes de ser copiado por cima.

Gramática do delta (1 verbo por linha):

```text
LM-020 ajudou+1
LM-016 mordeu+1
LM-004 promovido_para=<caminho do mecanismo>
ADD <seção> :: sup: `termo1` `termo2` :: regra. **Do instead:** ação. → ficha: — · promovido_para: —
TOMBSTONE LM-nnn :: motivo
REFINE LM-nnn :: novo texto. **Do instead:** ação.
```

## Proibições (o lint aplica)

- **Não reescrever, comprimir, reordenar em massa ou renumerar.** `--anti-collapse <antes>
  <depois>` bloqueia quando um `LM-` desaparece ou >20% dos bullets mudam de conteúdo/seção
  (contadores e `conf` não contam). Reescrita grande = 2+ commits.
- **Não apagar.** Aposentar = mover para `## Tombstones` como `- [LM-nnn] ☠ data :: motivo`.
  Uma mudança de conteúdo por commit sempre passa; de 2 para cima vale o limite de 20%.
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

## Invariantes — a regra que nunca pode ser quebrada

A landmine diz "isto me mordeu". A invariante, em `sdd/invariants.md`, diz "isto nunca pode ser violado,
e aqui está o que vigia": uma linha por regra, com a landmine de origem e o estado (`ok` = um check roda
sozinho; `auto` = dá para automatizar, com a tarefa; `humano` = exige julgamento, com o motivo). Toda
landmine ativa que já mordeu, ou que foi promovida, precisa estar classificada lá: como origem de uma
invariante, ou em `## Descartados` com o motivo.

- **Só a curadoria escreve** em `sdd/invariants.md`, com o seu OK por item.
- **A trava:** `bash sdd/bin/playbook-curator.sh --validar-inv sdd/playbook.md sdd/invariants.md` reprova
  invariante com origem aposentada, landmine do universo sem classificação, ID repetido e `check=` que
  não existe. Aposentar uma landmine que é origem de uma invariante só passa junto com o ajuste que o
  `--cruzar` propõe: é uma decisão só, não duas.
- Projeto sem `sdd/invariants.md`: a curadoria diz que pulou o cruzamento e segue só com o playbook.

---

Parte do SDD Open by RDD — https://github.com/robertodiasduarte/sdd-open
