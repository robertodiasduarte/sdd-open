# UX REVIEW: F12 Contexto, patterns e governança

> UX/CX review for `F12_CONTEXTO` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F12_CONTEXTO |
| **Date** | 2026-11-03 |
| **Author** | ux-review-command (sdd-ux-review 2.4.0) |
| **DEFINE** | [DEFINE_F12_CONTEXTO.md](../features/DEFINE_F12_CONTEXTO.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

Lidos antes: `UX_REVIEW_F7_EVIDENCIA.md`, `UX_REVIEW_F8_HOOKS.md`, `UX_REVIEW_F9_FLUXO.md` e `UX_REVIEW_F10_REVISAO.md`. Vêm deles:
- o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2);
- "símbolo sempre com palavra, sem cor" (F8 U8);
- a marca com rótulo em toda pergunta de decisão (F9 U1);
- "a linha de aviso diz a consequência, não só o fato" (F10 U4).

---

## UX Summary

A interface da F12 é texto, lido pelo aluno no chat do agente ou no terminal, em 6 superfícies:
1. **as linhas do Step 1.5** do `sdd-define`: o que o cartógrafo vai fazer (gerar, reusar, pular) e o resultado;
2. **as linhas e as perguntas do Step 6.5**: revisão em andamento, N.A., lacunas, uma pergunta `[D2]` por lacuna e o 🛑 da governança que não rodou;
3. **as duas paradas ⏸️** (cartógrafo e revisor) em agente que não abre sessão fresca sozinho;
4. **o exit 5 do `verify-gate.sh`** quando falta a linha `Governança` — o aluno vê isso no build ou na release, longe do Define, muitas vezes logo depois de atualizar o pacote;
5. **as saídas dos lints** (`contexto-lint`, `patterns-lint`, `governanca-fronteira`, `docs-extract-decisions`), que o agente traduz;
6. **a pergunta do `sdd-design`** quando o papel de uma surface ficou em aberto, mais `docs/context-and-governance.md` + PT.

O maior risco é o **susto do exit 5 depois da atualização**: o build de uma feature em andamento para com "CLARIFICAR" sem nada no DEFINE ter mudado. O teste do suporte falha na hora ("isso é bug?"). O segundo risco é a **parada dupla**: num agente sem subagente, o mesmo Define pode parar duas vezes pedindo para colar um bloco, e a 2ª parada parece repetição da 1ª. O terceiro é o **"nenhum" lido como erro**: `CONTEXTO de domínio: nenhum` aparece na maioria dos projetos (sem mapa de domínios) e não pode soar como falha.

Três achados centrais:
- **O exit 5 da governança tem texto próprio** (U1): diz que é a versão nova do método, não um defeito no DEFINE, e dá as 2 saídas com a linha exata de dispensa.
- **Cada parada ⏸️ diz o papel, o que o agente fresco vai ler e escrever, e "1 de 2"** (U2).
- **"pulado" sempre vem com o motivo e o que fazer se quiser o mapa** (U3).

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do Bravo (contador), sem git nem terminal; o agente conduz o Define e traduz as saídas dos scripts |
| **Secondary User** | Roberto e alunos avançados que escrevem `sdd/patterns/dominio.md` e patterns, e leem os lints |
| **User Goal** | Terminar o Define sabendo que o domínio foi mapeado e a governança revista, sem decidir o que não é dele |
| **Primary Pain** | Parada que parece bug; pergunta que não sabe responder (padrão do projeto num app que não é financeiro); bloco para colar sem saber de onde |
| **Business/CX Goal** | Confiança: nada chega ao build sem a revisão de governança, e toda trava diz o conserto |
| **Device/Context** | Chat do agente ou terminal, desktop; o cartógrafo e o revisor levam minutos cada |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Começar o Define | Não sabe que há 2 revisões novas | O Status do Define mostra as etapas; a linha de início do Step 1.5 diz o que vai acontecer |
| Entry (1.5) | Mapear o domínio | "Pulou? deu erro?" | U3: `🗺️ contexto: pulado — <motivo>` com o conserto opcional |
| Core Action (1.5) | Esperar o cartógrafo | "Travou?" | `🗺️ contexto: mapeando ctx:<slug> em contexto fresco (alguns minutos)` antes do despacho |
| Interrupção (1.5 e 6.5) | Parada ⏸️ | Colar o bloco errado; achar que é repetição | U2: papel, o que ele lê e grava, `parada 1 de 2` / `2 de 2`, o bloco que começa com `<<<CONTEXTO` ou `<<<GOVERNANCA` |
| Feedback (6.5) | Ler a governança | N.A. ou lacunas | `✅ governança: N.A. — <motivo>` · `⚖️ governança: <n> lacuna(s) — <n> pergunta(s)` |
| Decisão (6.5) | Decidir cada lacuna | Medo de errar; "aplicar todos" | Uma pergunta `[D2]` por lacuna, com severidade, o que muda no app e o AT antes/depois; nunca "aplicar todas" |
| Recovery (6.5) | Revisão falhou 2 vezes | "E agora?" | U4: 🛑 com a consequência (build e release param) e as 2 saídas numeradas |
| Completion | Build/release | Exit 5 inesperado | U1: texto próprio do exit 5 da governança |
| Follow-up (Design) | Papel de surface em aberto | Design decide por ele | U6: pergunta `[D2]` que trava, antes do DESIGN |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | O exit 5 por linha `Governança` ausente (AT-012) usaria o texto do marcador de ambiguidade: "resolva os marcadores de ambiguidade no DEFINE e volte ao Define" — falso para um DEFINE antigo, que não tem marcador nenhum | teste do suporte; decisão 3 do brainstorm (trava sempre) | Mensagem própria: `🛑 GOVERNANÇA NÃO REVISADA (exit 5) — <DEFINE> não tem a linha Governança com um valor final (encontrado: ausente \| "<valor>").` + `Desde a v2.4.0, todo DEFINE passa pela revisão de governança antes do build; DEFINEs escritos antes disso param aqui uma vez.` + `1. Numa sessão nova do agente, peça: "rode só o Step 6.5 do sdd-define sobre <DEFINE>".` + `2. Ou dispense: na tabela Technical Context, a linha \| **Governança** \| dispensada — <motivo> \| <seu nome, data> \|.` e o `→` próprio: `→ rode a revisão de governança (Step 6.5) ou dispense com motivo; o build e a release ficam parados até lá.` |
| U2 | MUST | O `despachar` (F9) diz, para qualquer papel, "o agente começa a ler o DEFINE" e "o relatório não foi gravado" — errado para o cartógrafo, que lê o código e grava um CONTEXTO; e duas paradas no mesmo Define parecem repetição | AT-007; F9 U-ref | Texto por papel: cartógrafo "o agente começa a ler o código do domínio <slug>" · "copie o bloco que começa com `<<<CONTEXTO`" · "nada foi gravado em sdd/contexto/"; revisor "o agente começa a ler o DEFINE" · "`<<<GOVERNANCA`" · "o relatório de governança não foi gravado; o DEFINE está marcado como pendente (o build não passa até a revisão voltar)". A skill escreve antes da saída do script a linha `⏸️ parada 1 de 2 deste Define (o cartógrafo); a 2ª é a revisão de governança.` quando as duas vão ocorrer, e `parada 2 de 2` na do revisor |
| U3 | MUST | `nenhum (pulado: sem sdd/patterns/dominio.md)` é o caso comum e pode soar como falha | princípio 2; L5 | Linha do Step 1.5: `🗺️ contexto: pulado — este projeto ainda não tem mapa de domínios (sdd/patterns/dominio.md). Sem problema: o Define segue; para ter o mapa, veja sdd/patterns/README.md.` A linha no DEFINE fica curta (`nenhum (pulado: sem mapa de domínios)`) |
| U4 | MUST | O 🛑 da 2ª falha da governança precisa dizer a consequência e as 2 saídas, e não pode sugerir `/sdd-define <DEFINE>` (refaria a spec) | privado `define.md` passo 10; F10 U4 | `🛑 governança não rodou — <motivo em palavras>. Efeito: o build e a release param até resolver.` + `1. Numa sessão nova, peça: "rode só o Step 6.5 do sdd-define sobre <DEFINE>" — não rode o Define inteiro de novo, ele regravaria a spec.` + `2. Ou dispense com motivo (linha exata).` |
| U5 | MUST | As 5 perguntas do padrão do projeto (AT-011) num app sem dinheiro, tributo ou dado pessoal seriam cerimônia | decisão do Define; "Se tem que explicar, está errado" | Mantido como no DEFINE: só com `PADRAO_AUSENTE`. Antes das perguntas, 1 frase: `A revisão achou <gatilho> neste Define e o projeto ainda não tem o padrão de governança; são 5 perguntas, uma vez por projeto.` Cada pergunta com a marca `[D2 · muda o produto]` |
| U6 | MUST | C11: o `sdd-design` decide sozinho o papel de uma surface que a UX deixou em aberto | AT-017; privado `UX_REVIEW_TEMPLATE.md:273-276` | Pergunta `[D2 · muda o produto]` **Qual o papel da surface "<nome>"?** · **operacional** (recomendada quando a surface é lista, tabela ou painel denso) · **destaque** · **sobreposição** · **não sei** — "eu mostro um exemplo de cada papel nesta tela". O `UX_REVIEW_TEMPLATE.md` diz: "papel em aberto trava o Design até a resposta" |
| U7 | SHOULD | Os lints imprimem classes estáveis (`path-morto`, `lm-morto`…) que o aluno não entende | F8 U2 | Cada achado: `🛑 <arquivo>:<linha> — path-morto: o arquivo citado não existe mais (<path>).` + `→ cite o caminho atual ou remova a linha`; a classe fica no texto (o self-test a exige), seguida da explicação em palavras. `RESULTADO:` + `→` em toda saída |
| U8 | SHOULD | Os despachos levam minutos e o Define fica mudo | F10 U6 | `🗺️ contexto: mapeando ctx:<slug> em contexto fresco (alguns minutos)` e `⚖️ governança: revisando em contexto fresco (alguns minutos)` antes de cada despacho; sem tempo inventado |
| U9 | SHOULD | Sem página que explique o mecanismo | F6/F9/F10: o mecanismo vem com o seu documento | `docs/context-and-governance.md` + PT: o que o Step 1.5 e o 6.5 fazem, a linha de dispensa, como escrever o `dominio.md` e um pattern, o exit 5 depois da atualização |
| U10 | COULD | `patterns-lint --design` bloqueia por pattern vencido sem dizer a idade | — | `🛑 sdd/patterns/<p>.md citado no DESIGN foi validado em <data> (<n> dias; o limite é <L>).` + `→ revalide o esqueleto e atualize validado_em, ou deixe de citá-lo` |

---

## Interaction States

- **Step 1.5 — gerar:** linha de início (U8); resultado `✅ contexto: sdd/contexto/<slug>.md (<n> regras vigentes)`.
- **Step 1.5 — reusar:** `✅ contexto: reusando sdd/contexto/<slug>.md, válido (nada mudou nas superfícies desde <data>)`; vencido: `⚠️ contexto: sdd/contexto/<slug>.md venceu (<n> arquivos mudaram)` + oferta de gerar.
- **Step 1.5 — pulado:** U3. **Falhou 2 vezes:** `⚠️ contexto: o mapa não ficou válido (<classe em palavras>); o Define segue sem ele.`
- **Step 6.5 — N.A.:** `✅ governança: N.A. — <motivo>`. **0 lacunas:** `✅ governança: 0 lacunas — <cobertura>`. **Lacunas:** `⚖️ governança: <n> lacuna(s) — <n> pergunta(s)` e o caminho do relatório uma vez.
- **Step 6.5 — falhou 1 vez:** `↻ governança: a 1ª tentativa falhou (<motivo>); tentando de novo em contexto fresco.` **2 vezes:** U4.
- **Fronteira violada:** `⚠️ o agente gravou fora do permitido: <paths>. Nada foi apagado; confira esses arquivos.` (DEFINE em `FORA:` é regravado e isso é dito.)
- **Parada:** U2.

---

## Content and Copy Guidance

- Português, frases curtas. "cartógrafo" na 1ª vez: "o cartógrafo (um agente novo que lê o código do domínio e anota as regras que já valem, com o arquivo e a linha)". "governança" na 1ª vez: como a `sdd-governanca` já explica.
- Símbolo por significado, sempre com palavra: 🗺️ contexto · ⚖️ governança · ✅ pronto · ⚠️ aviso · 🛑 parou · ⏸️ aguardando você · ↻ tentando de novo.
- Nas skills, "agente fresco" e "sessão nova"; nunca o nome de uma ferramenta de um agente só (regra 10).
- A linha de dispensa aparece sempre inteira, pronta para colar.

---

## Accessibility and Responsiveness

- Sem cor; todo símbolo com palavra.
- Linhas de status com até 100 caracteres; caminho de arquivo numa linha só, para colar.
- O bloco a colar nas paradas é nomeado pela primeira linha dele (`<<<CONTEXTO`, `<<<GOVERNANCA`), que o aluno acha sem rolar.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | Sem alvo de clique |
| L2 Escolhas por passo | OK | Uma pergunta por lacuna, 3 saídas + "não sei"; o `[auto · de rotina]` do 1.5 não pergunta com o encadeamento ligado |
| L3 Retomada | RECOMENDAÇÃO | Com o marcador gravado antes do despacho, sair na parada deixa o DEFINE travado e explicado; a skill diz isso na própria parada (U2) `(lente L3)` |
| L4 Convenção | OK | `RESULTADO:` + `→`, como os outros scripts de `sdd/bin/` |
| L5 Progresso real | RECOMENDAÇÃO | "parada 1 de 2" só quando as duas paradas vão ocorrer (U2); sem porcentagem inventada `(lente L5)` |
| L6 Destaque único | ALERTA | Um Define com cartógrafo e governança pode imprimir 4 a 6 linhas de status; cada uma numa linha só, com o símbolo do passo, para a pergunta seguinte continuar sendo o destaque |
| L7 Agrupamento | OK | Linhas agrupadas por passo (🗺️ e ⚖️) |
| S Sinal de validação real | — | Quantos DEFINEs saem com `Governança: dispensada` por mês e quantas lacunas `aplicadas` por feature; fica para a F15, não como critério |

---

## Design Handoff

- **Exit 5 da governança (U1):** mensagem e `→` próprios no `verify-gate.sh`, conferidos no teste do AT-012; o exit 5 do marcador de ambiguidade não muda.
- **Paradas (U2):** texto por papel no `sdd-fluxo.sh despachar` (AT-007) e a linha "parada i de n" no `SKILL.md` do `sdd-define`.
- **Step 1.5 e 6.5 (U3, U4, U5, U8):** linhas fixas no `SKILL.md`, conferidas por teste de texto (AT-008, AT-009, AT-011).
- **C11 (U6):** pergunta no `sdd-design` (conta 1 pergunta a mais no `sdd-decisoes-lint --sites`) e frase no `UX_REVIEW_TEMPLATE.md`.
- **Lints (U7, U10):** classe estável + explicação + `RESULTADO:`/`→`.
- **Doc (U9):** `docs/context-and-governance.md` + PT, com link nos READMEs.
- **Notas de aceite:** o DEFINE sobe para v1.1 com U1 no AT-012, U2 no AT-007/AT-009, U3/U8 no AT-008, U4 no AT-009, U5 no AT-011, U6 no AT-017 e U7 no AT-001/AT-014.

---

## Open UX Questions

None - ready for Design.
