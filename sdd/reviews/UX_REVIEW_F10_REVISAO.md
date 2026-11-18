# UX REVIEW: F10 Revisão adversarial — núcleo

> UX/CX review for `F10_REVISAO` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F10_REVISAO |
| **Date** | 2026-10-31 |
| **Author** | ux-review-command (sdd-ux-review 2.4.0) |
| **DEFINE** | [DEFINE_F10_REVISAO.md](../features/DEFINE_F10_REVISAO.md) |
| **Status** | Ready for Design |
| **Lentes** | 1 recomendação · 1 alerta. Não mudam o Status |

Lidos antes: `UX_REVIEW_F7_EVIDENCIA.md`, `UX_REVIEW_F8_HOOKS.md` e `UX_REVIEW_F9_FLUXO.md`. Vêm deles:
- o molde "achado → por que importa → como corrigir → `RESULTADO:` → `→`" (F8 U2);
- "símbolo sempre com palavra, sem cor" (F8 U8);
- a marca com rótulo em toda pergunta de decisão (F9 U1).

---

## UX Summary

A interface da F10 é texto, em 5 superfícies:
1. **o resumo final** do `adversarial-review.sh` que o agente traduz para o aluno: valeu ou não, quantos achados, quanto custou;
2. **as linhas ⚠️** do topo: troca de engine, mesma engine nos dois papéis, revisão sem contexto, revisão rasa;
3. **as paradas** 64/65/66/67/68, cada uma com o conserto;
4. **a pergunta D3 de dispensa** da `sdd-release`, a única pergunta nova que o aluno vê;
5. `docs/adversarial-review.md` + PT e o texto das 3 skills.

O maior risco é o **falso verde**: uma revisão que não valeu (auditor sem veredito, mesma engine auditando, revisor raso) lida como "zero achados". No privado, isso aconteceu 11 vezes com `auditor_exit 68` em 315 revisões. O segundo risco é o custo: `$?` cru não diz nada ao aluno, e `assinatura` pode ser lido como "custou o preço da assinatura".

Três achados centrais:
- **A palavra do resultado vem antes de qualquer número** (`REVIEW COMPLETA` / `REVIEW INVÁLIDA` / `PAROU`). "Inválida" diz por que não é "zero achados".
- **As linhas ⚠️ dizem a consequência**, não só o fato. Exemplo: "a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos da revisão".
- **A dispensa da release tem a revisão agora como opção recomendada** e o motivo escrito como saída. O motivo fica no registro da release.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do Bravo (contador), sem git nem terminal; o agente roda o script e traduz o resumo |
| **Secondary User** | Roberto e alunos avançados que configuram `review.revisor1`/`review.auditor` e leem o META |
| **User Goal** | Saber se a revisão por outra engine valeu, o que achou e quanto custou, sem abrir arquivo |
| **Primary Pain** | Revisão inválida lida como limpa; custo que não se entende; release que para sem dizer o que fazer |
| **Business/CX Goal** | Confiança: nada publica sem revisão ou sem dispensa escrita; toda revisão fraca se anuncia |
| **Device/Context** | Chat do agente ou terminal, desktop; uma revisão leva minutos e roda em segundo plano |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Terminar o build | "Preciso mesmo revisar?" | 5c diz que a release exige a revisão (AT-033) |
| Entry | Rodar a revisão | Configuração faltando | Slot vazio → 64 com o slot nomeado e os ids válidos |
| Core Action | Esperar | "Travou?" | Uma linha por papel ao começar: engine e o teto de tempo do registry |
| Feedback | Ler o resultado | Falso verde | Palavra do resultado primeiro; ⚠️ no topo |
| Recovery | Algo falhou | "E agora?" | Cada parada com o conserto concreto no `→` |
| Completion | Release | "Posso publicar?" | `--conferir` diz se a revisão é desta versão do código |
| Follow-up | Dispensar | Pular por pressa | Pergunta D3 com "rodar agora" recomendado e o motivo escrito |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | O resumo do AT-023 não fixa as palavras de cada `RESULTADO` nem o que o `→` diz em cada caso | 11 `auditor_exit 68` no privado; F8 U2 | `REVIEW COMPLETA` (0) · `REVIEW INVÁLIDA` (68: "a engine respondeu fora do formato; isto não é zero achados") · `PAROU` (64/65/66/67). Cada `→` traz o conserto: 65 "confira a credencial de <engine> (<onde ela vive>); a revisão não troca de engine por falha de credencial"; 67 por exclusão "escolha outra engine para auditar (`review.auditor`) ou rode com `--um-engine`"; 67 por lista esgotada "acrescente outra engine à lista ou tente mais tarde" |
| U2 | MUST | `$?` e `assinatura` crus no resumo | princípio de jargão; o aluno lê "assinatura" como preço | No resumo para pessoas: `US$ 0,0061`, `≈ US$ 0,01 (estimado)`, `incluído na assinatura`, `custo desconhecido`. O META mantém `US$`/`≈US$`/`assinatura`/`$?` (contrato de máquina). O total diz quantos papéis ficaram sem custo conhecido |
| U3 | MUST | A pergunta D3 de dispensa (AT-027) não tem texto | F9 U1, `PERGUNTA_DECISAO.md` | `**Sua decisão** — [D3 · muda a regra do método] **Esta versão não tem revisão por outra engine. Como seguimos?**` · **rodar agora** (recomendado) — roda revisor e auditor sobre o diff desta frente; leva em geral de 2 a 15 minutos e mostra o custo no fim · **publicar sem revisão** — peço o motivo em uma frase; ele fica no registro da release · **não sei** — explico o que a revisão confere, com o último achado dela nesta frente, se houver |
| U4 | MUST | As linhas ⚠️ (AT-005, AT-008, AT-019) dizem o fato, não a consequência | F8 "o aviso mora no produto" | Fallback: "⚠️ o auditor previsto (<a>) falhou (<motivo>); quem auditou foi <b>". Mesma engine: "⚠️ a mesma engine revisou e auditou: a auditoria tem os mesmos pontos cegos da revisão". Sem contexto: "⚠️ sem --feature: a revisão não leu BRAINSTORM, DEFINE nem DESIGN, e decisões já documentadas podem voltar como achado". Rasa: "⚠️ o revisor terminou em <n> s sem achados: isso não conta como revisão" |
| U5 | MUST | A parada da pasta não ignorada (AT-009) precisa dizer por quê | privacidade (R9) | "🛑 a pasta <dir> não está ignorada pelo git: o diff e as respostas das engines iriam para o repositório." + `→ rode: printf '%s\n' '<dir>/' >> .git/info/exclude` (comando exato, uma linha) |
| U6 | SHOULD | Uma revisão leva minutos e o script fica mudo | 315 META: revisor de 43 s a 497 s | Ao iniciar cada papel, uma linha: `▶ revisor: <engine> (<modelo>) — até <timeout_s/60> min`. O agente roda em segundo plano e avisa o aluno |
| U7 | SHOULD | Sem página que explique a revisão | F6/F9: o mecanismo vem com o seu documento | `docs/adversarial-review.md` + PT: o que é, os 2 slots a preencher, custo, privacidade, tabela de exits com o conserto de cada um, `--um-engine` e a dispensa |
| U8 | COULD | `--conferir` imprime a linha do ledger sem dizer o que ela prova | — | Antes da linha: `✅ a revisão <pasta> é desta versão do código (sha256 igual).` |

---

## Interaction States

- **Sucesso:** `REVIEW COMPLETA`; achados por severidade em palavras ("2 graves, 1 médio, 0 leves"); custo por papel e total.
- **Inválida:** `REVIEW INVÁLIDA`; diz qual papel e por quê; nunca mostra "0 achados".
- **Parou:** `PAROU`; o `→` traz o conserto.
- **Fraca, mas válida:** `diversidade: nenhuma` ou fallback → ⚠️ no topo; o resultado continua `REVIEW COMPLETA`.
- **Dry-run:** "nada foi enviado a nenhuma engine", com o plano.

---

## Content and Copy Guidance

- Português, frases curtas. "engine" é o termo do método; na primeira vez num documento, "engine (o modelo de IA que revisa)".
- Nome da engine sempre com o modelo entre parênteses no resumo, porque o mesmo adapter roda modelos diferentes.
- Número com unidade: "8 arquivos", "120 KB", "30 s".
- Nas skills, "engine do registry" e "papel"; nunca o nome de um vendor (regra 10).

---

## Accessibility and Responsiveness

- Sem cor; todo símbolo com palavra (✅ 🛑 ⚠️ ▶).
- Linhas do resumo com até 100 caracteres; o caminho da pasta numa linha só, para colar.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | Sem alvo de clique |
| L2 Escolhas por passo | OK | A pergunta D3 tem 2 saídas de trabalho + "não sei" |
| L3 Retomada | OK com U1 | Toda parada diz o conserto; rodar de novo refaz do zero (diff congelado de novo) |
| L4 Convenção | OK | `RESULTADO:` + `→`, como os outros scripts de `sdd/bin/` |
| L5 Progresso real | RECOMENDAÇÃO | U6: linha por papel ao começar; não há porcentagem a inventar `(lente L5)` |
| L6 Destaque único | ALERTA | Com fallback, mesma engine e sem contexto, o topo acumula 3 ⚠️; o resultado vem logo depois, numa linha só |
| L7 Agrupamento | OK | Achados agrupados por severidade |
| S Sinal de validação real | — | `convergencia_1o_passe` e o número de `REVIEW INVÁLIDA` por mês no `output_dir` medem a saúde; fica para a F15, não como critério |

---

## Design Handoff

- **Resultado (U1):** 3 palavras de `RESULTADO` e o texto do `→` por exit, no código e em `docs/`.
- **Custo (U2):** formato humano no resumo, contrato de máquina no META.
- **Dispensa (U3):** a pergunta no `references/como-falar.md` da `sdd-release` (conta 1 pergunta a mais no `sdd-decisoes-lint --sites`: 16).
- **Avisos (U4) e pasta (U5):** texto exato no script, conferido nos testes.
- **Progresso (U6) e doc (U7):** linha `▶` por papel; `docs/adversarial-review.md` + PT, com link nos READMEs.
- **Notas de aceite:** o DEFINE sobe para v1.1 com U1–U5 em AT-009, AT-019, AT-020, AT-023 e AT-027, e com U6/U7 em AT-041.

---

## Open UX Questions

None.
