# UX REVIEW: F7 Evidência que não mente

> UX/CX review for `F7_EVIDENCIA` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F7_EVIDENCIA |
| **Date** | 2026-10-30 |
| **Author** | ux-review-command (sdd-ux-review 2.3.1) |
| **DEFINE** | [DEFINE_F7_EVIDENCIA.md](../features/DEFINE_F7_EVIDENCIA.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

---

## UX Summary

A interface da F7 é texto de terminal, em 3 superfícies:
- (1) a saída de 6 scripts (`report-lint.py`, `verify-gate.sh` e os 4 novos), que o agente lê e traduz e que o aluno curioso lê direto;
- (2) o texto novo da `sdd-build` e da `sdd-release`, que diz ao agente o que falar quando um desses scripts para o trabalho;
- (3) dois arquivos que o aluno edita ou lê: a linha do avaliador no `BUILD_REPORT` e o `sdd/baselines/tests.txt`.

O maior risco é que a F7 cria **paradas novas**: um relatório que ontem passava e hoje reprova, um avaliador que não é chamado, uma release que aborta. Toda parada nova sem causa **e** conserto na mesma mensagem vira um print no suporte ("isso é bug?").

Há dois achados centrais:
- **A saída final do `report-lint` fala só de evidência.** A linha `→` atual manda produzir `AT-nnn.log`, e isso é falso para "avaliação ausente" ou "tabela não reconhecida". A orientação final tem de vir da classe do problema.
- **`PENDENTE` sai verde.** Sai `RESULTADO: VERDE`, e isso só não fica ambíguo se a mesma saída disser que a release vai abortar.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do open (contador, analista), em geral sem git nem terminal; o agente é o intermediário de toda saída de script |
| **Secondary User** | Mantenedor (Roberto) e o agente de build, que leem a saída crua no terminal |
| **User Goal** | Fechar o build e publicar sem descobrir depois que a prova não existia |
| **Primary Pain** | Parada sem explicação; regra nova que parece burocracia; trabalho perdido |
| **Business/CX Goal** | Confiança: o verde quer dizer verde; o vermelho diz o que fazer |
| **Device/Context** | Terminal ou chat do agente, no desktop; uso a cada build e a cada release |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Terminar o build | Cansaço; quer o verde | Nada novo até um script parar |
| Entry | O agente roda o `report-lint` no passo 6 | Surpresa: "ontem passava" | A primeira linha diz **qual** regra, em palavras, com a classe entre colchetes |
| Core Action | Corrigir o relatório (linha do avaliador, tabela, evidência) | Medo de "mentir" no relatório | A saída mostra as 3 saídas válidas da avaliação ausente, nesta ordem: rodar o avaliador, `N.A. (motivo)` só com 1 camada, `PENDENTE (motivo)` |
| Feedback | Rodar de novo | "Passou mesmo?" | `RESULTADO: VERDE` só quando nada falta; com `PENDENTE`, a frase da release que aborta vem na mesma saída |
| Recovery | Guard nega o avaliador; baseline acusa falha nova; log com exit do `tail` | "Quebrei alguma coisa?" | Causa em 1 linha, a lista do que está sujo ou falhou, o comando que conserta |
| Interrupção → Retomada | O build trava antes do avaliador | Relatório pela metade parecendo pronto | `avaliador: PENDENTE (motivo)` registra o estado real; a release recusa e diz por quê |
| Completion | Release aborta ou segue | Alívio ou frustração | A 0a lista o `arquivo:linha` do `PENDENTE` e do log falso, e o que fazer |
| Follow-up | Entender quantas voltas o gate levou | — | O trace é silencioso: nenhuma linha nova na saída do gate |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | A linha `→` do `report-lint.py` (`report-lint.py:309-311`) sempre manda produzir `evidence/<F>/AT-nnn.log`; para "avaliação ausente" e "tabela não reconhecida", o conserto é outro | Princípio 1 ("erro com causa **e** conserto") | Uma classe por violação (`[tabela]`, `[evidência]`, `[avaliação ausente]`, `[declaração]`, `[migration]`) e uma linha `→` por classe presente, na ordem em que aparecem |
| U2 | MUST | `PENDENTE` sai 0 com `RESULTADO: VERDE`: "passou?" fica ambíguo | Princípio 2 (estado ambíguo é defeito) | ⚠️ "avaliação PENDENTE (motivo) — a release não sai enquanto esta linha existir" e `→` "rode o avaliador quando o build destravar e troque a linha pelo veredito" |
| U3 | MUST | "N.A. aceito sem conferir camadas" não diz como tornar a contagem possível | Princípio 1 | ⚠️ com a causa (`layers:` vazio, sem DESIGN, sem manifest) e o conserto ("preencha `layers:` em `sdd/config.yaml`") |
| U4 | MUST | Os scripts do privado usam `⛔`, `❌` e `🛑` para a mesma coisa | Princípio 1 ("um símbolo por significado, sempre com palavra") | Nos 4 scripts novos: `🛑` bloqueia, `⚠️` avisa, `✅` passou, `ℹ️` informa; nada de `⛔`/`❌`; todo símbolo seguido de palavra |
| U5 | MUST | Os scripts do privado terminam sem `RESULTADO:` | Contrato dos lints do open | Toda saída dos 4 scripts novos termina em `RESULTADO: <PALAVRA>` + `→ <o que fazer>`, inclusive em 64 |
| U6 | MUST | O `gate-shell-evidencia` mostra o problema, mas o aluno não sabe o que é "exit do formatador" | Teste do estranho | Cada acusação: `arquivo:linha`, o comando (até 110 caracteres) e a frase "o número gravado é o exit do `tail`, não do seu comando"; o `→` final traz a receita `out=$(cmd 2>&1); rc=$?; … [exit=$rc]` |
| U7 | MUST | O guard do avaliador nega sem dizer por que importa | Teste do suporte ("por que não chama o avaliador?") | 1 linha de motivo ("o avaliador usa o terminal e pode restaurar arquivos do último commit: trabalho não commitado se perde"), a lista dos caminhos e o comando de commit pronto |
| U8 | MUST | Falha nova e falha conhecida no `test-baseline` | Princípio 2 | Separar 3 listas com rótulo (`🛑 nova`, `ℹ️ conhecida`, `✅ sarou — removida do baseline`); a falha nova vem com "aceitar é decisão sua: `--aceitar <id>`" |
| U9 | SHOULD | O `gate-baseline` sai 2 com "asserção sem dentes" | Teste do estranho | Dizer o que fazer em termos do comportamento: "a asserção fica verde no código antigo; ancore no que a feature muda e rode de novo" |
| U10 | SHOULD | A `sdd-build` passa a ter 3 paradas novas (guard, baseline do gate, falha nova) | Camada de conversa F4 | Cada parada no formato ⏸️ do `PERGUNTA_DECISAO.md`, com o motivo do aluno (não o nome do script) |
| U11 | COULD | Listas longas (19 acusações, 30 caminhos sujos) | Densidade | O script lista tudo (o agente precisa); a skill resume em "quantos, quais até 10, e mais N" |
| U12 | WONT | Cores ANSI na saída | Acessibilidade e logs | Saída sem cor: os logs vão para `evidence/` e precisam ficar legíveis como texto puro |

---

## North Star Checks (Premium + Self-Evident)

| Check | Status | Note |
|---|---|---|
| Hierarquia em 200 ms | OK com U1/U5 | A 1ª linha diz a regra; a última diz o que fazer |
| Estado ambíguo | MUST U2 | `PENDENTE` verde precisa da frase da release |
| Erro com causa e conserto | MUST U1, U3, U6, U7 | Uma linha `→` por classe |
| Um símbolo por significado | MUST U4 | `🛑 ⚠️ ✅ ℹ️` |
| Teste do estranho | OK com U6/U7 | "exit do formatador" e "árvore suja" traduzidos em uma frase |
| Teste do suporte | OK com U2/U8 | "passou ou não?" e "por que meu teste antigo não trava?" respondidos na saída |

---

## Gamification Strategy

Dispensada. A F7 é conferência; recompensa por passar no lint ensinaria a perseguir o verde, o contrário do objetivo.

---

## 60/30/10 Visual Strategy

N.A.: saída de terminal sem cor (U12). A hierarquia vem da ordem (regra → lista → `RESULTADO:` → `→`) e dos 4 símbolos.

---

## Surface Assignment

| Surface | Quem lê | Papel |
|---|---|---|
| Saída dos scripts (stdout/stderr) | agente, mantenedor | Fonte da verdade; completa, com caminhos |
| Fala da skill ao aluno | aluno | Tradução: quantos, quais até 10, o que preocupa, o que fazer |
| Linha do avaliador no `BUILD_REPORT` | aluno, revisor | Declaração auditável |
| `sdd/baselines/tests.txt` | mantenedor | Lista de dívida aceita, com `#` comentando o motivo |

---

## Interaction Requirements

- Toda parada nova da `sdd-build` e da `sdd-release` usa o formato ⏸️ e diz o que **não** foi feito ("o avaliador não foi chamado", "nada foi publicado").
- O commit pedido pelo guard é rotina do build ("commite antes de qualquer revisão" já é regra da skill): a skill não abre pergunta nova para ele.
- `--aceitar <id>` nunca roda sem o aluno decidir; a skill pergunta no formato de autorização, com o id e a saída da falha.

---

## Required States

| Estado | Superfície | O que aparece |
|---|---|---|
| Sucesso | todos | `✅ …` + `RESULTADO: VERDE` + `→` próximo passo |
| Erro (bloqueia) | todos | `🛑 [classe] …` por item + `RESULTADO: VERMELHO` + `→` por classe |
| Parcial | `report-lint` com `PENDENTE` ou contagem impossível | `⚠️ …` + `RESULTADO: VERDE` + `→` que diz o que falta |
| Vazio | `gate-shell-evidencia` sem log, `test-baseline` sem `test_cmd` | `ℹ️ nada a conferir` + `RESULTADO: VERDE` ou `PULADO` |
| Inconclusivo | `gate-baseline` 3, `test-baseline` 3 | `⚠️ …` com a causa + `RESULTADO: INCONCLUSIVO` + `→` |
| Sem permissão / não conferido | `avaliador-guard` 2, `check-ignore` indisponível | `⚠️ não consegui conferir (motivo)`; nunca verde silencioso |
| Desligado | `SDD_AVALIADOR_GUARD=off` | `⚠️ guard desligado — declare no BUILD_REPORT` |

---

## Content and Copy Guidance

- Português, frases curtas, verbo no imperativo no `→` ("rode", "troque", "commite").
- O motivo antes da regra: "o git ignora este arquivo: ele não vai para o commit", não "violação E3".
- Identificadores técnicos (E1, LM-146) só entre parênteses, no fim, se existirem.
- O comando de conserto pronto para colar, um por linha.
- Nenhuma menção a ferramenta de um agente só.

---

## Accessibility and Responsiveness

- Sem cor (U12); todo símbolo acompanhado de palavra (U4).
- Linhas de comando truncadas em 110 caracteres com `...` (cabe num terminal de 120 colunas).
- Toda saída em texto puro, para os logs em `evidence/`.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | Sem alvo de clique |
| L2 Escolhas por passo | RECOMENDAÇÃO | A avaliação ausente oferece 3 saídas; listar na ordem do caminho certo (rodar o avaliador primeiro), com quando cada uma vale `(lente L2)` |
| L3 Retomada | OK | `PENDENTE (motivo)` preserva o estado real do build travado |
| L4 Convenção | OK | Exits 0/1/2/3/64 seguem os scripts que já existem |
| L5 Progresso real | N.A. | Sem barra de progresso |
| L6 Destaque único | ALERTA | Muitos ⚠️ juntos (contagem impossível, `check-ignore` indisponível, `PENDENTE`) diluem o aviso que importa; agrupar os avisos de ambiente numa linha só |
| L7 Agrupamento | RECOMENDAÇÃO | Violações agrupadas por classe, não na ordem do arquivo `(lente L7)` |
| S Sinal de validação real | — | `grep -c '"exit":2' sdd/traces/<F>.jsonl` (voltas vermelhas por feature) e a contagem de `PENDENTE` na release |

---

## Design Handoff

- **Copy obrigatória:** U1 (classe + `→` por classe), U2 (frase da release no `PENDENTE`), U3 (conserto da contagem), U6 (receita), U7 (motivo do guard), U8 (3 listas).
- **Contrato de saída dos 4 scripts novos:** `🛑/⚠️/✅/ℹ️` + palavra; termina em `RESULTADO:` + `→`; sem cor; comando truncado em 110.
- **`verify-gate.sh`:** o trace não acrescenta linha à saída (DEFINE AT-014/AT-016); `--sem-define` imprime `ℹ️` + `RESULTADO: VERDE`.
- **Skills:** 3 paradas novas da `sdd-build` no formato ⏸️ (U10); a 0a da `sdd-release` cita `arquivo:linha` ao abortar.
- **Recomendações de lente:** L2 (ordem das 3 saídas), L7 (agrupar por classe), alerta L6 (avisos de ambiente juntos).
- **Como medir depois:** voltas vermelhas por feature no trace; quantos `PENDENTE` a release barrou.
- **Notas de aceite:** os testes conferem a classe e o `RESULTADO:` de cada saída nova (DEFINE AT-001 a AT-025).

---

## Open UX Questions

None - ready for Design.

---

## Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-10-30 | ux-review-command | Versão inicial |

---

## Next Step

`/sdd-design sdd/features/DEFINE_F7_EVIDENCIA.md`
