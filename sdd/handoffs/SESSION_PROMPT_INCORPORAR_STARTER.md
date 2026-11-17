# Continuar: INCORPORAR_STARTER — sem frente aberta (F22 ✅ em 15/11); próxima frente: decisão do Roberto

A F22 fechou em 2026-11-15: `v2.17.0` (aviso de versão nova e verbo `upgrade`), `v2.17.1` (curadoria do playbook da F16W2 e
da F22) e starter `v1.5.22`. O Cronograma recomendado está vazio. A prova da F22 é o upgrade do privado pelo verbo novo, na
sessão de lá.

## Onde abrir esta sessão

Na worktree de documentos (`/Users/robertoduarte/rdd-worktrees/sdd-open-docs`) para decidir a próxima frente; a frente
nova nasce pela `sdd-new-session`.

## Prompt

```text
Sessão do SDD Open sem frente aberta. Repo público robertodiasduarte/sdd-open; main = 8f944fc = v2.17.1 (a F22, aviso de
versão e upgrade, fechou em 2026-11-15: v2.17.0, curadoria v2.17.1, starter v1.5.22). Responda em português. Pergunte ao
Roberto qual é a próxima frente: o Cronograma recomendado do plano está vazio. Push, merge, tag e Release pedem a frase
"sdd-open autorizado"; push, PR e merge no sdd-starter pedem o OK próprio dele. Nada no repositório privado daqui.

Leia primeiro (branch docs/incorporar-starter, worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs):
- PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" e o "Cronograma recomendado"
- HANDOFF_INCORPORAR_STARTER.md → a seção "2026-11-15 — F22" (Pendências e Alertas) e os Eventos de 15/11

Candidatas a frente (o Roberto escolhe; abra com a sdd-new-session):
- pendências leves da F22: alarme.sh da higiene e worktree; proxy só no git; CRLF um a um; duas tags v no commit; pacote de
  versão desconhecida e projeto com registro; O1 a O4 do avaliador; o teste de curadoria que aceita conjunto vazio;
- medição dos revisores entre frentes (as pastas EXTERNAL_REVIEW_* somem com a worktree; guardar META.txt e vereditos na
  branch de documentos para o eval-revisores.sh somar o histórico);
- a ficha desta família reprova no handoff-lint (formato anterior ao molde).

Fora daqui, na sessão do privado: a prova da F22 — git -C ~/sdd-open pull e bash ~/sdd-open/bin/sdd-open.sh upgrade --de v2.15.0.

Lições da F22 para a próxima frente: o teto de tempo de script é por relógio (SECONDS), não por voltas de sleep (o piso do
macOS no CI pegou 7,2 s); o adversarial-review.sh manda os arquivos não rastreados no diff (ponha no .git/info/exclude o que não
é do pacote); teste que fixa contagem do playbook quebra na curadoria seguinte; rode a suíte inteira antes do PR, não só os
módulos tocados. Landmines de sempre: o Bash do agente é zsh (laço e exit em bash -c; ${PIPESTATUS[0]} vazio); log de evidência
por script bash com rc=$? e 1ª linha "$ comando"; o Windows segura a release; leia /credits antes de cada rodada paga
(US$ 14,67 em 15/11 depois da recarga).
```
