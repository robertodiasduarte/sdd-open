# UX REVIEW: F22 Aviso de versão e upgrade

> UX/CX review for `F22_AVISO_VERSAO` after DEFINE and before DESIGN

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | F22_AVISO_VERSAO |
| **Date** | 2026-11-14 |
| **Author** | ux-review-command (sdd-ux-review 2.6.0) |
| **DEFINE** | [DEFINE_F22_AVISO_VERSAO.md](../features/DEFINE_F22_AVISO_VERSAO.md) |
| **Status** | Ready for Design |
| **Lentes** | 2 recomendações · 0 alerta. Não mudam o Status |

---

## UX Summary

A interface da F22 é texto, em 5 superfícies:
- (1) as linhas de versão do `doctor` (que também roda no fim do `init`);
- (2) o plano, as mensagens e o fecho do `upgrade`;
- (3) a linha de aviso que a `sdd-new-session` e a FASE 0 da `sdd-release` repassam ao aluno;
- (4) o arquivo de registro `sdd/open-instalado.txt`, que aparece no `git status` do aluno;
- (5) a documentação de como atualizar (`docs/`, EN e PT).

O maior risco é o **upgrade parecer perigoso ou opaco**: um comando que mexe em centenas de arquivos do projeto, rodado
por um aluno que não sabe o que é cada um. Se o plano despejar 600 linhas, ou se não disser em uma tela que **nada que
você editou será tocado e nada será commitado**, o aluno não confirma, ou confirma sem entender. O segundo risco é o
**aviso virar ruído**: um ⚠️ a cada `doctor` sem rede, ou uma pergunta no meio da abertura da frente, ensina a ignorar
a linha. Por isso: "não conferido" é informação (ℹ️), nunca atenção; o aviso de versão nova é uma linha, com a versão,
a atual e o que fazer, e não para nada.

Três achados centrais:
- **O plano do `upgrade` é por classe, com contagem**: iguais · novos · do pacote sem edição sua · editados por você
  (não tocados) · que saíram do pacote (não apagados); nomes até 10, com "e mais N"; a lista inteira só com `--verbose`.
- **O fecho do `upgrade` diz os 2 próximos passos**: revisar os arquivos editados (com o caminho do diff de cada um) e
  commitar numa frente, porque o `upgrade` não commita.
- **Projeto sem registro para antes de escrever** com os 2 comandos prontos que montam o pacote antigo, e a versão a
  usar quando a pessoa não sabe qual tem.

---

## User and Context

| Field | Value |
|-------|-------|
| **Primary User** | Aluno do Bravo (contador), em geral sem git nem terminal; o agente roda `doctor` e `upgrade` por ele e traduz |
| **Secondary User** | Roberto e quem lê a saída crua no terminal; o agente que abre a frente ou publica |
| **User Goal** | Ficar na versão em dia sem perder o que ajustou no próprio projeto |
| **Primary Pain** | "Saiu versão nova?" sem resposta; "se eu atualizar, perco o que mudei?"; atualizar à mão arquivo por arquivo |
| **Business/CX Goal** | Confiança: o aviso informa sem assustar; o upgrade prepara e a pessoa decide |
| **Device/Context** | Terminal ou chat do agente, desktop (macOS, Linux, Windows Git Bash); o aviso a cada frente e release; o upgrade algumas vezes por mês |

---

## Journey Map

| Step | User Intent | Emotion/Risk | Interface Need |
|------|-------------|--------------|----------------|
| Before | Abrir uma frente ou publicar | Rotina; não pensa em versão | A linha de versão nova aparece **uma vez**, como informação, sem pergunta |
| Entry | Saber se precisa atualizar | "É urgente? Quebrou algo?" | A linha diz a versão nova, a do projeto e o caminho ("quando quiser, peça ao agente…"); nunca ⚠️ por falta de rede |
| Core Action | Rodar o `upgrade` do pacote novo | Medo de perder edição | O plano por classe, com contagem, e a frase "não toca no que você editou e não commita" antes do `[y/N]` |
| Feedback | Ver o que mudou | "Deu certo? O que falta?" | Fecho com `RESULTADO: ATUALIZADO` (ou `ATUALIZADO, N PARA MESCLAR`), a lista dos editados com o diff de cada um e o `doctor` |
| Recovery | Escrita falha; projeto sem registro; pacote errado no `--de` | "Estraguei o projeto?" | 🛑 com a causa e o conserto; nada escrito, ou "rode de novo, ele retoma"; o registro só muda no fim |
| Interrupção → Retomada | Fechou a janela no meio | "Ficou pela metade?" | Rodar de novo retoma (o que já foi copiado vira "igual"); o registro velho continua valendo até o fim |
| Completion | Commitar a atualização | "Commito tudo?" | O `→` diz: confira com `git status` e commite numa frente; os N arquivos para mesclar à mão ficam para quando quiser |
| Follow-up | Próximo `doctor` | "Estou em dia?" | `✅ versão: projeto vX · pacote vX · última publicada vX` |

---

## UX/CX Findings

| # | Severidade | Achado | Evidência | Recomendação |
|---|---|---|---|---|
| U1 | MUST | O `doctor` diz a versão em 3 lugares possíveis (projeto, pacote, publicada); 3 linhas viram ruído e 1 linha confusa vira pergunta | Princípio 2 | Uma linha de versão: `✅ versão: projeto v2.17.0 · pacote v2.17.0 · última publicada v2.17.0`. Projeto sem registro: `ℹ️ versão: projeto sem registro (instalado antes da v2.17.0) · pacote v2.17.0`. Versão nova: uma 2ª linha `⚠️ saiu a v2.18.0 (seu projeto está na v2.17.0) — veja como atualizar: <URL da Release>` + o comando do `upgrade` na linha `→` do bloco |
| U2 | MUST | Sem rede, um ⚠️ a cada `doctor` ensina a ignorar o ⚠️ de verdade | Princípio 2; "um símbolo por significado" | `ℹ️ versão nova: não conferida — <motivo em palavras: sem resposta em 5 s · o endereço recusou · nenhuma versão na lista> (o resto do diagnóstico vale)` |
| U3 | MUST | Checagem desligada sem dizer onde religar é estado ambíguo | Princípio 2 | `ℹ️ versão nova: checagem desligada (open.check_updates: false em sdd/config.yaml)` ou `(SDD_OPEN_CHECK_UPDATES=0 no ambiente)` |
| U4 | MUST | O plano do `upgrade` com 600 linhas não é lido; sem a promessa, não é confirmado | Princípio 1 (hierarquia em 200 ms); teste do suporte ("vai apagar meu playbook?") | Cabeçalho `▶ upgrade v2.17.0 → v2.18.0 — plano`, depois uma linha por classe com contagem e até 10 nomes (`e mais N`): `= 157 iguais ao pacote novo (nada a fazer)` · `+ 46 novos` · `~ 43 do pacote, sem edição sua (atualizar)` · `⚠️ 3 editados por você — não serão tocados` · `⚠️ 2 saíram do pacote — não serão apagados`; antes do `[y/N]`: "Nada que você editou será tocado. Nada será commitado." `--verbose` lista tudo |
| U5 | MUST | Depois do `upgrade`, o aluno não sabe o que fazer com os editados nem se deve commitar | Princípio 1 (próximo passo); teste do suporte | Para cada editado: `⚠️ <caminho> — editado por você; a versão nova está em <pasta>/<caminho>.novo e o que mudou em <pasta>/<caminho>.diff`; fecho `RESULTADO: ATUALIZADO` ou `RESULTADO: ATUALIZADO, 3 PARA MESCLAR` + `→ confira com git status e commite numa frente (o upgrade não commita); os arquivos para mesclar ficam para quando quiser` |
| U6 | MUST | Projeto sem registro: parar sem dizer como seguir trava o aluno | Princípio 1 (erro com causa e conserto) | `🛑 este projeto não tem o registro de versão (foi instalado antes da v2.17.0); para separar o que é do pacote do que você editou, preciso do pacote da versão que ele tem` + `RESULTADO: ERRO` + `→` com os 2 comandos prontos (baixar o pacote da versão e rodar `upgrade --de <pasta>`) e como descobrir a versão (a mensagem do commit que instalou, ou o `CHANGELOG`/a Release que você baixou) |
| U7 | MUST | O aviso na abertura da frente não pode virar pergunta nem parada | Decisão do brainstorm (nunca bloqueia) | A skill repassa em 1 frase, depois do "pronto para abrir": "Saiu a versão v2.18.0 do SDD Open (este projeto está na v2.17.0). Não precisa parar agora; quando quiser, peça ao agente para atualizar." Sem versão nova, sem rede ou desligado: **nada** (o aluno não precisa saber que conferimos) |
| U8 | MUST | O mesmo vocabulário em `doctor`, `upgrade` e skills | Continuidade; `docs/cli-conventions.md` | Só `▶ ✅ ⚠️ ℹ️ 🛑 → + ~ =`, sempre com palavra, sem cor; `ATUALIZADO` e `ATUALIZADO, N PARA MESCLAR` entram na lista de palavras do `RESULTADO:` em `docs/cli-conventions.md` |
| U9 | SHOULD | `--de` com a pasta de outra versão classifica errado sem avisar | Teste do estranho (quem não sabe a própria versão chuta) | Se menos da metade dos arquivos instaláveis do projeto bate com o pacote do `--de`: `⚠️ a pasta --de (v2.12.1) não parece a versão deste projeto: só N de M arquivos batem` antes do `[y/N]` |
| U10 | SHOULD | `sdd/open-instalado.txt` aparece no `git status` sem explicar o que é | Teste do suporte ("posso apagar isso?") | 1ª linha do arquivo, em comentário: o que é, quem grava (`init`, `upgrade`) e "não edite; apagar faz o próximo upgrade pedir --de" |
| U11 | SHOULD | Hooks de outra worktree: "ligados" sem dizer de onde esconde que a regra vem de outro checkout | Princípio 2 | `✅ hooks ligados (pelo sdd/hooks de outra worktree deste repositório: <caminho>)` |
| U12 | SHOULD | A documentação de "como atualizar" não existe | Teste do estranho | Uma página por idioma: quando atualizar, os 3 comandos (baixar, `upgrade --dry-run`, `upgrade`), o que cada classe do plano significa, o caso sem registro, como mesclar um editado |
| U13 | COULD | `upgrade --dry-run` como 1º passo sugerido | Confiança | A linha do `doctor` com versão nova sugere o `--dry-run` primeiro |
| U14 | WONT | Notas da Release no aviso; atualização automática; cores | YAGNI do brainstorm; acessibilidade | — |

---

## North Star Checks (Premium + Self-Evident)

### Premium (padrão de qualidade percebida)

| Check | Status | Note |
|---|---|---|
| Hierarquia em 200 ms | OK com U1, U4 | 1 linha de versão; o plano por classe |
| Erro com causa e conserto | MUST U5, U6 | comandos prontos |
| Um símbolo por significado | MUST U2, U8 | ℹ️ para informação, ⚠️ só para o que pede ação |

### Self-Evident / Zero-Explanation

| Check | Status | Note |
|---|---|---|
| Estado ambíguo | MUST U3, U5 | "desligado onde?", "commito?" respondidos na saída |
| Teste do estranho | OK com U4, U12 | o plano diz o que cada classe faz |
| Teste do suporte | OK com U4, U6, U10 | "vai apagar meu playbook?", "e sem registro?", "posso apagar este arquivo?" |

---

## Gamification Strategy

Dispensada. Atualizar é manutenção; um placar de "versões em dia" empurraria a atualizar sem revisar os editados.

---

## 60/30/10 Visual Strategy

N.A.: saída de terminal sem cor (U14). A hierarquia vem da ordem (versão → plano por classe → promessa → `[y/N]` →
editados → `RESULTADO:` → `→`) e dos símbolos com palavra.

---

## Surface Assignment

| Surface | Quem lê | Papel |
|---|---|---|
| Linhas de versão do `doctor` | aluno (via agente), mantenedor | estado da versão e o caminho do upgrade |
| Plano, mensagens e fecho do `upgrade` | aluno (via agente), mantenedor | o que vai mudar, o que não vai, o que fazer depois |
| Linha da `sdd-new-session` e da `sdd-release` | aluno | informação em 1 frase, sem decisão |
| `sdd/open-instalado.txt` | quem olha o `git status` | registro; a 1ª linha diz o que é |
| `docs/` (EN e PT) | aluno, mantenedor | o passo a passo e o caso sem registro |

---

## Interaction Requirements

- O `upgrade` faz **uma** pergunta (a confirmação do plano, como o `init`); `--yes` pula; `--dry-run` não pergunta.
- O aviso de versão nova nunca pergunta nem para: nem no `doctor`, nem na frente, nem na release.
- O `upgrade` nunca roda `git add`/`git commit`; o `→` final diz que a pessoa commita.
- Rodar o `upgrade` de novo depois de uma interrupção retoma sem perguntas novas além do `[y/N]`.

---

## Required States

| Estado | Superfície | O que aparece |
|---|---|---|
| Sucesso (em dia) | `doctor` | `✅ versão: projeto vX · pacote vX · última publicada vX` |
| Atenção (versão nova) | `doctor`; skills | `⚠️ saiu a vN (seu projeto está na vX) — …`; nas skills, a frase do U7 |
| Informação (não conferido / desligado / sem registro) | `doctor` | `ℹ️ …` com o motivo e onde mudar |
| Vazio (nada a atualizar) | `upgrade` | `RESULTADO: EM DIA` + `→ nada a fazer` |
| Parcial (editados) | `upgrade` | lista dos editados com `.novo` e `.diff`; `RESULTADO: ATUALIZADO, N PARA MESCLAR` |
| Erro (bloqueia) | `upgrade` | `🛑` causa + `RESULTADO: ERRO` + `→` conserto; nada escrito ou "rode de novo" |
| Simulação | `upgrade --dry-run` | o plano e `RESULTADO: DRY-RUN` |
| Cancelado | `upgrade` com `N` | `RESULTADO: CANCELADO`, nada escrito |

---

## Content and Copy Guidance

- Português, frases curtas; a versão sempre com o `v` (`v2.18.0`), nunca "2.18".
- "editado por você", não "modificado localmente"; "do pacote, sem edição sua", não "intacto".
- "não serão tocados" e "não será commitado" ditos **antes** do `[y/N]`.
- Nas skills, o aluno não vê `doctor` nem `ls-remote`: só a frase do U7.
- Inglês nos docs EN com os mesmos termos traduzidos de forma estável ("edited by you", "from the package, unedited").

---

## Accessibility and Responsiveness

N.A. visual — saída de terminal sem cor; o significado vem da palavra junto de cada símbolo (regra do `say.sh`), e
os nomes longos ficam numa linha cada, sem tabela de largura fixa.

### Responsiveness

N.A. — terminal; linhas longas quebram pelo terminal, e cada informação cabe numa linha própria.

---

## Lentes cognitivas (não bloqueiam)

| Lente | Status | Evidência |
|---|---|---|
| L2 Escolhas por passo | RECOMENDAÇÃO | o plano tem 1 decisão (`[y/N]`); o `--dry-run` sugerido antes (U13) separa "ver" de "fazer" |
| L3 Retomada | OK | rodar de novo retoma; o registro só muda no fim |
| L7 Agrupamento | RECOMENDAÇÃO | plano em 5 grupos com nome e contagem (U4) |
| L1, L4, L5, L6 | N.A. | terminal, sem alvo de clique nem progresso visual |
| S Sinal de validação real | — | o projeto privado faz o upgrade dele pelo verbo e conta quantos arquivos precisou mesclar à mão (meta: só os editados de verdade) |

---

## Design Handoff

- Copiar os textos dos U1 a U7 e U9 a U11 como estão (ajuste fino de palavras no Design, sem mudar a ordem nem os símbolos).
- `ATUALIZADO` e `ATUALIZADO, N PARA MESCLAR` em `docs/cli-conventions.md`; o `upgrade` na ajuda do `sdd-open.sh` e na tabela de exits.
- O comando do upgrade nas linhas do `doctor` e dos docs: do pacote novo, de dentro do projeto.
- Pasta dos `.novo`/`.diff`: decisão do Design (dentro do projeto, ignorável, ou temporária com o caminho impresso), contanto que sobreviva até a pessoa mesclar.
- Recomendações `(lente L2)`: `--dry-run` sugerido primeiro; `(lente L7)`: plano em grupos.
- Como medir depois: o upgrade do projeto privado pelo verbo (sinal S).

---

## Open UX Questions

- nenhuma

---

## Revision History

| Versão | Data | Mudança |
|---|---|---|
| 1.0 | 2026-11-14 | primeira versão |

---

## Next Step

**sdd-design** com o DEFINE e esta revisão.
