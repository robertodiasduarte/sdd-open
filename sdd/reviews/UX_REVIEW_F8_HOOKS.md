# UX REVIEW: F8 Hooks de git

> UX/CX review for `F8_HOOKS` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F8_HOOKS |
| **Date** | 2026-10-30 |
| **Author** | ux-review-command (sdd-ux-review 2.3.1) |
| **DEFINE** | [DEFINE_F8_HOOKS.md](../features/DEFINE_F8_HOOKS.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 1 alerta. Não mudam o Status |

---

## UX Summary

A interface da F8 é texto de terminal, em 5 superfícies:
- (1) o plano e as mensagens do `init` e do `doctor` (a única vez em que o aluno é avisado de que o projeto passa a recusar commits);
- (2) a recusa do `pre-commit` e o aviso do `pre-push`, que aparecem no meio de um `git commit`/`git push` que o agente rodou;
- (3) as mensagens do `alarme.sh` da `sdd-higiene-dado`, que ganha um estado novo ("ligado pelos hooks do projeto");
- (4) a razão da negação dos 2 guards do Claude Code, que o agente lê e tem de traduzir;
- (5) `docs/hooks.md` e o guia do aluno.

O maior risco é o mesmo da F7, agora na operação mais frequente do aluno: **um commit que ontem passava e hoje é recusado**, pelo agente, no meio de uma tarefa. Se a recusa não disser em uma tela o que foi achado, por que importa e o que fazer, o aluno manda print ("isso é bug?") ou o agente aprende a pular com `--no-verify`. O segundo risco é a decisão do brainstorm: a versão é `v2.2.9` e **o aviso da mudança está só nestas telas** — a linha do plano, a recusa e o `doctor` são o produto do aviso.

Há três achados centrais:
- **A linha do plano precisa dizer o efeito**, não a configuração: `+ core.hooksPath = sdd/hooks` sozinho é jargão; a linha diz que 5 regras passam a conferir cada commit.
- **A recusa segue o molde do alarme da higiene** (que o aluno já conhece): achados → por que importa → como corrigir → `--no-verify` só depois de conferir, com a frase para o agente.
- **A migração do alarme nunca pode parecer perda**: quem tinha o alarme em `.git/hooks` precisa ler que ele continua ligado, agora pelos hooks do projeto.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do Bravo (contador), em geral sem git nem terminal; o agente roda `init`, `commit` e `push` por ele e traduz o que aparece |
| **Secondary User** | Quem usa o Claude Code na `sdd-build` (lê a razão do guard); mantenedor (Roberto), que lê a saída crua |
| **User Goal** | Salvar versões sem levar para o git o que não pode ir, sem descobrir isso depois |
| **Primary Pain** | Commit recusado sem explicação; alarme de CPF/CNPJ que some em silêncio; "o que mudou no meu projeto?" |
| **Business/CX Goal** | Confiança: a recusa protege e ensina; nenhuma proteção desliga sem aviso |
| **Device/Context** | Terminal ou chat do agente, desktop; a cada commit e push; uma vez no `init` |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Instalar ou atualizar o open | Rotina; não espera mudança | O plano do `init` mostra a linha dos hooks **com o efeito** antes do `[y/N]` |
| Entry | Confirmar o plano | "O que é hooksPath?" | A linha diz "5 regras passam a conferir cada commit; `git commit --no-verify` pula uma vez"; o `doctor` repete em ✅ |
| Core Action | Commitar pelo agente | Surpresa: commit recusado | Primeira linha `🛑 [H3] <arquivo>: <motivo>`; depois por que importa (1 linha), como corrigir (comando), e só no fim o `--no-verify` |
| Feedback | Corrigir e commitar de novo | "Passou mesmo?" | Sucesso silencioso do hook; o commit aparece; nada a traduzir |
| Recovery | Push com base velha; guard do Claude Code nega | "Quebrei algo?" | `⚠️` com N commits atrás e o que fazer; a razão do guard começa pelo que foi negado e por quê |
| Interrupção → Retomada | Projeto com husky ou alarme à mão | "O init vai apagar meu alarme?" | O `init` diz que **não** mexeu e mostra a linha para acrescentar ao alarme que existe |
| Completion | `init` termina | Alívio | `RESULTADO: INSTALADO` e o `doctor` com a linha dos hooks |
| Follow-up | Alarme da higiene depois do `init` | "Ainda estou protegido?" | `alarme.sh verificar` diz "ligado pelos hooks do projeto (`sdd/hooks`)"; o `init` avisou na migração |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | `+ core.hooksPath = sdd/hooks (novo)` é a única pista do aluno de que o projeto vai recusar commits; sozinha é jargão | Princípio 2; decisão 9 do brainstorm (o aviso mora no produto) | Linha do plano: `+ core.hooksPath = sdd/hooks (novo: 5 regras passam a conferir cada commit — teto do arquivo de contexto, credencial, playbook, byte NUL, branch padrão; git commit --no-verify pula uma vez)` |
| U2 | MUST | A recusa do privado é uma regra por vez, com cor e sem conserto para o aluno | Princípio 1 (causa **e** conserto); teste do suporte | Molde do alarme da higiene: cabeçalho `sdd-open: commit recusado.`, 1 linha `🛑 [Hn] <arquivo>: <motivo>` por achado, bloco "Por que importa" (1 frase por classe presente), "Como corrigir" com o comando pronto, `RESULTADO: COMMIT RECUSADO`, `→` por classe e, por último, `→ se você conferiu … git commit --no-verify` + "Agente de IA: não use --no-verify sem o OK explícito da pessoa." |
| U3 | MUST | H6 ("commit direto em main") tem uma saída certa e uma errada; o aluno não sabe qual | Princípio 2 | O `→` da H6 diz primeiro "abra uma frente: peça a `sdd-new-session`" e só depois cita `--no-verify`; nunca sugere trocar `default_branch` |
| U4 | MUST | H3 reimprimir o valor da credencial no terminal (e no log do agente) vaza o segredo de novo | Segurança; fonte do privado | A mensagem mostra só a chave (`chave: password`), nunca o valor; o teste confere a ausência |
| U5 | MUST | Quando o `init` não pode ligar os hooks (husky, alarme à mão), o aluno não sabe se perdeu algo | Princípio 2 (estado ambíguo) | `⚠️ hooks do open não ligados: já existe <o que> em <onde>. Nada foi alterado nele.` + `→ para ter as 5 regras, acrescente a ele a linha: bash sdd/hooks/pre-commit \|\| exit 1`; e `RESULTADO: INSTALADO` continua |
| U6 | MUST | Migração do alarme da higiene: o aluno viu "alarme instalado em .git/hooks" e agora o `init` liga outra coisa | Teste do suporte ("meu alarme sumiu?") | `⚠️ alarme da sdd-higiene-dado migrado: continua ligado, agora pelos hooks do projeto (sdd/hooks). Para desligar: bash .agents/skills/sdd-higiene-dado/scripts/alarme.sh desinstalar` |
| U7 | MUST | `doctor` precisa dizer o estado dos hooks com o mesmo vocabulário do `init` | Princípio 1 | `✅ hooks ligados (sdd/hooks: pre-commit com 5 regras + alarme da higiene <on/off>, pre-push)` ou um ⚠️ por causa, cada um com o comando (`rode init`, `chmod +x sdd/hooks/pre-commit`, a linha para o alarme alheio) |
| U8 | MUST | O privado usa `⛔` e cores ANSI; o open usa `🛑/⚠️/✅` + palavra e termina em `RESULTADO:` | `docs/cli-conventions.md` | Hooks, `alarme.sh` e `init` só com `🛑 ⚠️ ✅ ℹ️` seguidos de palavra; sem cor; recusa termina em `RESULTADO: COMMIT RECUSADO` + `→`; o aviso do pre-push é `⚠️` + frase, sem `RESULTADO:` (não é veredito, é aviso) |
| U9 | MUST | A razão de negação dos guards é lida pelo agente e repassada ao aluno; se começar pelo texto do lint, o aluno não sabe o que foi negado | Princípio 1 | 1ª linha: `🛑 sdd-open: gravação de <arquivo> negada — o relatório não passa no report-lint:` (ou `despacho do avaliador negado — há trabalho não commitado:`), depois o texto do script; todo `systemMessage` começa com `⚠️ sdd-open:` e diz "não conferido" quando falhou aberto |
| U10 | SHOULD | `alarme.sh verificar` ganha um estado novo; o texto atual fala de "arquivo em `.git/hooks`" | Continuidade | Estado `NOSSO (hooks do projeto)`: "o alarme está ligado pelos hooks do projeto (`sdd/hooks`), versão <v> da skill"; `instalar` diz "liguei o alarme nos hooks do projeto; nada foi gravado em `.git/`" |
| U11 | SHOULD | O aviso do pre-push diz o problema e não a saída | Princípio 1 | `⚠️ <branch> está N commit(s) atrás de origin/main (base velha). → traga a base: peça ao agente para rebasear a frente sobre origin/main antes de abrir o PR` |
| U12 | SHOULD | `docs/hooks.md` é o único lugar que explica tudo junto | Teste do estranho | Uma tabela: regra · o que recusa · como corrigir · exemplo de mensagem; seção "O limite: `--no-verify`" dizendo que a verdade final é o `report-lint` da release e o CI; seção "Desligar" com `git config --unset core.hooksPath`; seção do adaptador do Claude Code nomeando o vendor só ali |
| U13 | COULD | Sucesso do hook é silencioso; o aluno não vê que as regras rodaram | Princípio 2 vs. ruído | Manter silencioso (é a convenção do git); o `doctor` é onde o aluno confirma que estão ligadas |
| U14 | WONT | Cores ANSI | Acessibilidade e logs em `evidence/` | Saída sem cor |

---

## North Star Checks (Premium + Self-Evident)

| Check | Status | Note |
|---|---|---|
| Hierarquia em 200 ms | OK com U2 | 1ª linha diz a regra e o arquivo; última diz o que fazer |
| Estado ambíguo | MUST U5, U6 | "Liguei ou não?" e "meu alarme sumiu?" respondidos na mesma saída |
| Erro com causa e conserto | MUST U2, U3, U7, U9 | Comando pronto em toda recusa |
| Um símbolo por significado | MUST U8 | `🛑 ⚠️ ✅ ℹ️`, sem `⛔` |
| Teste do estranho | OK com U1/U12 | A linha do plano e a tabela do `docs/hooks.md` explicam sem abrir o hook |
| Teste do suporte | OK com U3/U6 | "por que não posso commitar em main?" e "cadê meu alarme?" respondidos |

---

## Gamification Strategy

Dispensada. Hooks são proteção; contar commits "aprovados" ensinaria a perseguir o verde e a usar `--no-verify`.

---

## 60/30/10 Visual Strategy

N.A.: saída de terminal sem cor (U14). A hierarquia vem da ordem (achados → por que → como corrigir → `RESULTADO:` → `→`) e dos 4 símbolos.

---

## Surface Assignment

| Surface | Quem lê | Papel |
|---|---|---|
| Plano e mensagens do `init`/`doctor` | aluno (via agente), mantenedor | O aviso da mudança de comportamento |
| Recusa do pre-commit, aviso do pre-push | agente, aluno curioso | Fonte da verdade; completa, com caminhos e comandos |
| Mensagens do `alarme.sh` | aluno (via skill) | Estado do alarme nos dois modos |
| Razão dos guards (JSON) | agente | O que foi negado e por quê, antes do texto do script |
| `docs/hooks.md` + PT, guia do aluno | aluno, mantenedor | Explicação completa; o limite do `--no-verify` |

---

## Interaction Requirements

- O `init` faz **uma** pergunta (a confirmação do plano que já existe); a linha dos hooks é parte do plano, não pergunta nova.
- Quando o `init` não liga os hooks, ele segue e termina `INSTALADO`: o resto da instalação não depende disso.
- A recusa do pre-commit lista **todos** os achados de uma vez; o aluno corrige num ciclo só.
- O agente nunca roda `--no-verify` por conta própria: a última linha da recusa diz isso em texto, como o alarme da higiene já faz.
- O `alarme.sh` nunca liga nem desliga os hooks do open; só a própria config `sdd.higieneDado`.

---

## Required States

| Estado | Superfície | O que aparece |
|---|---|---|
| Sucesso | hook | nada (convenção do git); `doctor` mostra ✅ |
| Erro (bloqueia) | pre-commit | `sdd-open: commit recusado.` + `🛑 [Hn] …` por achado + por que + como corrigir + `RESULTADO: COMMIT RECUSADO` + `→` por classe + `→` do `--no-verify` |
| Aviso | pre-push; regra pulada (`python3`/`playbook-lint` ausente) | `⚠️ …` + o que fazer; o commit/push segue |
| Parcial | `init` sem ligar os hooks | `⚠️ hooks do open não ligados: …` + a linha para acrescentar; `RESULTADO: INSTALADO` |
| Migração | `init` com alarme da higiene em `.git/hooks` | `⚠️ alarme … migrado: continua ligado …` |
| Vazio | pre-commit sem arquivo staged relevante | nada |
| Sem permissão / não conferido | guards (fail-open) | `{"systemMessage":"⚠️ sdd-open: … não conferido (motivo)"}` |
| Desligado | `SDD_AVALIADOR_GUARD=off` | `systemMessage` com "guard desligado — declare no BUILD_REPORT" |

---

## Content and Copy Guidance

- Português, frases curtas, verbo no imperativo no `→` ("tire", "troque", "abra uma frente", "acrescente").
- O motivo antes da regra: "este arquivo entra inteiro no contexto do agente em toda sessão", não "H2".
- Identificadores (`[H2]`, nome do slot) entre colchetes ou no fim, entre parênteses.
- Nunca o valor de uma credencial, nunca um CPF/CNPJ inteiro (a higiene já mascara).
- Nenhuma menção a ferramenta de um agente só fora de `bin/adapters/claude/`, do gerado e de `docs/hooks*.md`.

---

## Accessibility and Responsiveness

- Sem cor (U14); todo símbolo acompanhado de palavra (U8).
- Caminhos e comandos inteiros, um por linha, para colar.
- Texto puro, legível nos logs de `evidence/` e no Git Bash do Windows.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L1 Alcance | N.A. | Sem alvo de clique |
| L2 Escolhas por passo | RECOMENDAÇÃO | Na recusa, a ordem dos `→` é a do caminho certo: corrigir primeiro, `--no-verify` por último `(lente L2)` |
| L3 Retomada | OK | O `init` repetido mostra `=` para o que já está ligado e completa só o que falta |
| L4 Convenção | OK | Hook silencioso no sucesso e `--no-verify` são a convenção do git |
| L5 Progresso real | N.A. | Sem barra de progresso |
| L6 Destaque único | ALERTA | O `init` já emite ⚠️ de órfãos, segredo no git e skill atrasada; os ⚠️ dos hooks (não ligados, migração) devem vir juntos, em sequência, antes do `RESULTADO:` |
| L7 Agrupamento | RECOMENDAÇÃO | Achados da recusa agrupados por classe (`[H2]`, `[H3]`…), não na ordem dos arquivos `(lente L7)` |
| S Sinal de validação real | — | Não há sinal automático: o hook não grava trace (fora de escopo). O que diria se funcionou é "quantos commits recusados foram corrigidos sem `--no-verify`"; fica como pergunta aos alunos, não como critério |

---

## Design Handoff

- **Copy obrigatória:** U1 (linha do plano com efeito), U2 (molde da recusa), U3 (`→` da H6), U4 (só a chave), U5 (hooks não ligados), U6 (migração), U7 (`doctor`), U9 (1ª linha da razão dos guards).
- **Contrato de saída:** `🛑/⚠️/✅/ℹ️` + palavra; recusa termina em `RESULTADO: COMMIT RECUSADO` + `→`; pre-push só `⚠️`; sem cor.
- **`alarme.sh`:** estado novo com texto próprio (U10); `instalar`/`desinstalar` dizem o que gravaram e o que não.
- **Docs:** `docs/hooks.md` + PT com a tabela regra · recusa · conserto · exemplo, "O limite: `--no-verify`", "Desligar", seção do adaptador (U12); ficha da higiene no guia do aluno com os dois lugares.
- **Recomendações de lente:** L2 (ordem dos `→`), L7 (agrupar por classe), alerta L6 (⚠️ dos hooks juntos no `init`).
- **Como medir depois:** sem sinal automático (S); pergunta aos alunos.
- **Notas de aceite:** os testes conferem a 1ª linha, a classe, a ausência do valor (H3), o `RESULTADO:` e a frase do `--no-verify` (DEFINE AT-001 a AT-024).

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

`/sdd-design sdd/features/DEFINE_F8_HOOKS.md`
