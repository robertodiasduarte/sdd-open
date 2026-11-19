# UX REVIEW: F28 Revisores pelo OpenRouter — a conversa que configura a revisão

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F28_REVISORES_OPENROUTER |
| **Date** | 2026-11-18 |
| **Author** | ux-review (sessão da frente) |
| **DEFINE** | `sdd/features/DEFINE_F28_REVISORES_OPENROUTER.md` (1.1) |
| **Status** | Ready for Design |
| **Lentes** | 3 recomendações · 0 alertas — não mudam o Status |
| **Escopo da revisão** | a "interface" é texto: as respostas da skill (Status, decisões, paradas, passo a passo), a saída do script de diagnóstico, o aviso novo do `checar.sh`, a oferta nas fases (design, build, release) e as linhas novas do `--dry-run` |

## UX Summary

O aluno chega aqui porque uma fase pediu revisores e ele não sabe o que são. A skill precisa responder, sem abrir
arquivo: **o que é isto, por que importa, quanto custa, o que eu faço agora e como volto depois.** O maior risco é a
parada obrigatória (gravar a chave e reabrir o agente): é ali que o aluno abandona, ou volta e ouve tudo de novo. A
recomendação mais forte: cada resposta abre com o que já foi feito, em palavras do aluno, e a volta depois da parada
começa pela prova de que a chave chegou.

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | aluno que nunca criou chave de API nem editou o perfil do terminal; um agente só |
| **User Goal** | ter a revisão rodando para seguir a fase sem dispensá-la |
| **Primary Pain** | pergunta sobre "engines" sem contexto; passos fora do computador (site, pagamento) sem guia; medo de gastar sem saber quanto |
| **Business/CX Goal** | confiança (o dinheiro e o código do aluno), menos dispensas de revisão, zero pedido de socorro "e agora?" |
| **Device/Context** | terminal ou extensão de editor, no Mac, no Linux ou no Windows (Git Bash, WSL); navegador aberto ao lado para o site do OpenRouter; tarefa de uma vez só, 10 a 20 minutos |

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | uma fase (design, build, release) ou o `checar` disse que faltam revisores | confusão: "revisor de quê?" | a oferta diz em 1 frase o que é e o efeito de não ter (a release pede para publicar sem revisão) |
| Entry | pedir a skill | receio de ser longo ou caro | a 1ª resposta diz quanto tempo leva e se custa, antes de qualquer termo |
| Core Action | escolher o caminho | escolher às cegas | opções com efeito e custo em números; a recomendada depende do que o computador já tem |
| Feedback | criar conta, pôr crédito, criar a chave | perder-se no site; não saber se acertou | um clique por passo, o nome do que aparece na tela, o que deve ver depois |
| Recovery | chave recusada, sem crédito, sem internet, chave colada no chat | sensação de ter estragado algo | causa em 1 frase, 1 passo, "nada foi gravado" quando for o caso |
| Interrupção → Retomada | gravar a chave e reabrir o agente | abandonar; ou voltar e ouvir tudo de novo | parada com o que foi feito e o que falta; a volta começa pela prova de que a chave chegou |
| Completion | ver que funcionou | "será que está mesmo configurado?" | 3 linhas de prova (chave aceita, valores gravados, plano) antes de "pronto" |
| Follow-up | a revisão roda numa fase | susto com o custo | o custo de cada revisão aparece no relatório dela; o limite de gasto da chave segura o teto |

## UX/CX Findings

| # | Priority | Area | Finding | Recommendation |
|---|----------|------|---------|----------------|
| U1 | MUST | Clarity | "Engine", "revisor", "auditor" chegam antes do sentido | A 1ª resposta abre com 2 frases: "A revisão adversarial é uma outra IA lendo o que foi construído, e uma terceira conferindo essa leitura. Sem ela configurada, a publicação pede para seguir sem revisão." Depois, o glossário na 1ª vez de cada termo. |
| U2 | MUST | Confidence | Custo e tempo aparecem tarde | A 1ª resposta diz o tempo ("uns 10 minutos, quase tudo no site do OpenRouter") e se o caminho recomendado custa (com 2 CLIs: "sem custo extra"; com OpenRouter: "por uso, centavos de dólar por revisão, fora da sua assinatura"). |
| U3 | MUST | Efficiency | Pergunta do caminho igual para todos | A recomendada vem do estado: 2+ CLIs ⇒ **usar as que você já tem** (sem custo extra); 1 ou 0 ⇒ **OpenRouter**. No máximo 4 opções e **não sei**; **agora não** diz a consequência (a publicação vai pedir o motivo de seguir sem revisão). |
| U4 | MUST | Self-Evident | Passo a passo fora do computador vira muro | Blocos de no máximo 5 passos por resposta: (1) conta e crédito, (2) chave com limite, (3) guardar a chave. Cada passo: um clique ou um comando, o nome do que aparece na tela, o endereço direto (`openrouter.ai/settings/credits`, `openrouter.ai/settings/keys`) e "→ você vê …". Os nomes de tela conferidos na documentação oficial, com a data em `references/`. |
| U5 | MUST | Confidence | Guardar a chave é o passo mais arriscado | Mac, Linux e WSL: **um comando**, rodado numa janela de terminal sua (não na conversa), que pede a chave sem mostrá-la e diz onde gravou; "→ você vê: Chave gravada em ~/.zshrc." Windows com Git Bash: a janela "Variáveis de ambiente", um clique por passo. Uma frase de alerta: o perfil não pode ir para pasta sincronizada nem para repositório público. Nunca "cole a chave aqui". |
| U6 | MUST | Interrupção → Retomada | A parada da chave é onde se abandona | Parada no formato do fragmento: Status ⏸️, "Por que parei: o agente só enxerga a chave depois de reaberto", **Onde**, passos para os 2 casos (agente no terminal: fechar a janela, abrir outra, entrar na pasta, abrir o agente; agente no editor: fechar o editor por completo e abrir), **O que já foi feito** (conta, crédito, chave criada, chave gravada), **O que não foi feito** (nada gravado no projeto), a frase para pedir de novo ("continue a configuração dos revisores") e "Quando terminar, me peça de novo, eu continuo daqui." |
| U7 | MUST | Retomada | Repetir tudo na volta | A volta abre com o resultado do teste da chave: "A chave chegou e o OpenRouter respondeu que ela vale." e vai direto à escolha dos modelos. Se a chave ainda não chegou mas está gravada: dizer isso e repetir **só** o passo de reabrir. |
| U8 | MUST | Confidence | OK de gravar sem saber o que autoriza | Antes da pergunta, 4 frases curtas: quanto custa (preço do par por milhão de tokens e a estimativa por revisão, em US$, lidos das tabelas, com a data); que cobra por uso, fora de qualquer assinatura; o que sai do computador (o diff do código e os documentos da frente); que só entram provedores que não guardam nem treinam com o dado. Lembra a `sdd-higiene-dado` em 1 frase. A pergunta: `[D1 · não se desfaz]` **"Posso gravar estes dois modelos como revisor e auditor deste computador?"** com **sim** (recomendado), **outro par** (o aluno diz o modelo; preço desconhecido), **não**, **não sei**. |
| U9 | MUST | Recovery | Erro cru do servidor | Cada classe vira 1 frase de causa e 1 passo; o código (401, 402, 429) só no fim, entre parênteses. Nunca o corpo da resposta. "Nada foi gravado" quando nada foi. |
| U10 | MUST | Completion | "Pronto" sem prova | A conclusão mostra 3 linhas antes de "pronto": ✅ chave aceita (com o limite e o que resta, em centavos); ✅ revisor e auditor gravados neste computador (lidos de volta); ✅ plano da revisão (diversidade, quem faria o 2º revisor e o desempate, ou "nenhuma engine — consequência"). Sem chave (caminho das CLIs), a 1ª linha some. |
| U11 | MUST | Recovery | Chave colada no chat | Resposta imediata, sem repetir o texto: "Não vou usar esta chave: ela ficou nesta conversa." + 3 passos (página de chaves → apagar aquela chave → criar outra) + "Nada foi gravado." |
| U12 | MUST | Self-Evident | Saída do script com jargão | O script imprime, para cada estado, a frase do aluno e o passo; as linhas `ESTADO:` e `RESULTADO:` são para o agente. A skill repassa a frase, nunca o id do estado. |
| U13 | MUST | Clarity | Status sem as etapas | `Revisores: ✅ 1 Conferir · ▶️ 2 Escolher · ⬜ 3 Chave · ⬜ 4 Gravar · ⬜ 5 Provar`; no caminho das CLIs, a 3 é ➖ (pulada) com o motivo em Agora. |
| U14 | SHOULD | Before | Oferta nas fases solta | Na `sdd-design`, na `sdd-build` e na `sdd-release`, a oferta é uma pergunta: **configurar agora** (recomendado, "uns 10 minutos") · **seguir sem revisão** (com o efeito: motivo escrito na release) · **não sei**. |
| U15 | SHOULD | Before | Aviso do `checar` sem consequência | 1ª frase com o efeito: "Os revisores da revisão adversarial não estão configurados — sem eles, a publicação pede para seguir sem revisão."; linha do comando: "peça: use a skill sdd-configurar-revisores". Sempre ⚠️. |
| U16 | SHOULD | Clarity | Linhas novas do `--dry-run` | Cada linha nova com palavra, não só símbolo: `origem: este computador (git config)`, `disponível` / `indisponível — <o que falta>`, `2º revisor: nenhuma engine disponível — a release pede o motivo (--aceitar-sem-revisor2)`. |
| U17 | COULD | Progress | — | Dentro do bloco do site, "passo 2 de 5" no começo de cada passo. |
| U18 | WONT | Gamification | Selo ou contagem de "configurado" | Tarefa de uma vez; a prova final já fecha o ciclo. |
| U19 | WONT | Visual | Cor por estado | Terminal sem cor garantida; significado nunca só por cor; cada símbolo vem com palavra. |

## North Star Checks (Premium + Self-Evident)

### Premium (padrão de qualidade percebida)

| Dimensão | Status | Evidência / Risco |
|----------|--------|-------------------|
| Hierarquia visual em 200ms | ✅ | Status na 1ª linha; a decisão em negrito no fim (U13, U8) |
| Densidade calibrada (respira) | ⚠️ | risco no passo a passo; U4 limita a 5 passos por resposta |
| Tipografia com propósito | N.A. | texto de terminal e de conversa |
| Movimento curto | N.A. | sem animação |
| Microinterações completas | N.A. | sem controles |
| Surfaces do design system | N.A. | sem design system |
| Estados vazios como delight | ✅ | "nada configurado" é o começo guiado, não um erro (U1, U3) |
| Acabamento "shipada" | ✅ | prova antes de "pronto" (U10); erro com causa e conserto (U9) |

### Self-Evident / Zero-Explanation

| Anti-padrão | Está presente? | Onde / como remover |
|-------------|----------------|---------------------|
| Tooltip-muleta | ✅ Não | — |
| Helper text explicando o óbvio | ✅ Não | glossário só na 1ª vez de cada termo |
| Estado ambíguo | ❌ Sim, no rascunho | "a chave chegou?" e "está configurado?": resolvidos por U7 e U10 |
| Cor conflitando com semântica | ✅ Não | — |
| Onboarding/tour obrigatório | ✅ Não | a skill só roda a pedido ou oferecida por uma fase |
| Documentação como contrato de UX | ❌ Sim, hoje | o guia técnico (`adversarial-review.md`) é o único caminho; a skill leva o caminho para a conversa |

**Teste do estranho:** um aluno sem chave completa o caminho sem perguntar se cada passo diz o que ele verá; o ponto
de hesitação é a reabertura do agente dentro do editor (U6 cobre os 2 casos).

**Teste do suporte:** "colei a chave aqui, e agora?" (U11); "fechei e abri e diz que não tem chave" (U7, estado
"gravada, agente não reaberto"); "quanto vou gastar?" (U2, U8, limite de gasto). Todos viraram MUST.

## Gamification Strategy

```text
Gamification decision: Not recommended because é uma configuração de uma vez só; o progresso real (Status e a prova final) basta.
```

## 60/30/10 Visual Strategy

N.A. — sem superfície visual: texto de terminal e de conversa. Hierarquia por posição (Status primeiro, decisão por
último) e por negrito na pergunta.

## Accessibility and Responsiveness

N.A. — sem superfície visual. Regra que vale no texto: nenhum significado só por símbolo ou cor (✅, ⚠️, ⏸️ sempre com
palavra); o texto funciona lido por leitor de tela, linha a linha.

## Lentes cognitivas

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | sem alvo de clique próprio |
| L2 Escolhas por passo | RECOMENDAÇÃO | no máximo 4 opções e **não sei** por pergunta; no site, uma ação por passo (U3, U4) |
| L3 Retomada | RECOMENDAÇÃO | a parada diz o que foi feito; a volta começa pela prova e não repete (U6, U7) |
| L4 Convenção | OK | formato das outras skills (Status, decisão, parada) |
| L5 Progresso real | RECOMENDAÇÃO | o Status vem do estado que o script mede, não da conversa (U12, U13) |
| L6 Destaque único | OK | uma pergunta em negrito por resposta |
| L7 Agrupamento | OK | passos do site em 3 blocos com nome (U4) |
| S Sinal de validação | — | depois da entrega: menos dispensas de `review_externo` nas releases dos alunos |

## Handoff para o Design

- **Etapas e Status:** 1 Conferir · 2 Escolher · 3 Chave · 4 Gravar · 5 Provar (U13).
- **Estados obrigatórios:** todos os da tabela do DEFINE, cada um com frase e passo no script e na skill (U12).
- **Copy:** abertura com o sentido e o custo (U1, U2); aviso de custo e privacidade com números antes do OK (U8);
  erro com causa, passo e "nada foi gravado" (U9); conclusão com 3 provas (U10); chave no chat (U11).
- **Interação:** passo a passo em blocos de até 5 (U4); guardar a chave por comando que não mostra o valor, ou pela
  janela do Windows (U5); parada da reabertura com os 2 casos e a frase para pedir de novo (U6); volta que não repete
  (U7).
- **Classes de decisão:** escolher o caminho `[D2 · muda o produto]`; gravar o par pago `[D1 · não se desfaz]` (autoriza
  uso pago com credencial); nenhuma `[auto · de rotina]` nesta skill.
- **Ganchos:** oferta nas fases como pergunta (U14); aviso do `checar` com a consequência (U15); linhas do
  `--dry-run` com palavras (U16).
- **Como medir depois (S):** contar `review_externo: dispensado` nas releases antes e depois.

## Acceptance notes

- Os nomes de tela do OpenRouter e da janela do Windows são conferidos no dia do Build e datados em `references/`.
- O comportamento numa conversa real fica nos 3 cenários × 2 execuções do DEFINE (SHOULD), com o critério de
  aprovado escrito antes.
