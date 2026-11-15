# Continuar: INCORPORAR_STARTER — fechar a F22 (Release v2.17.0, starter v1.5.22, curadoria)

A F22 (aviso de versão e upgrade) está na `main` (`7ba7eb0`) com a tag `v2.17.0` (PR #32, 2026-11-15); a Release estava
saindo quando a sessão parou. Faltam: conferir a Release, o starter `v1.5.22` (OK do Roberto), a curadoria do playbook da
F16W2 e da F22, e o fechamento. Detalhe na seção "2026-11-15 — F22" da ficha.

## Onde abrir esta sessão

Na worktree de documentos (`/Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16`, branch `docs/incorporar-starter`) ou na
da frente (`/Users/robertoduarte/rdd-worktrees/sdd-open-f22-aviso-versao`); cole o prompt abaixo.

## Prompt

```text
Fechar a frente F22 do SDD Open (aviso de versão e upgrade). Repo público robertodiasduarte/sdd-open. Responda em português.
Pergunte ao Roberto somente o que for dele: decisões (curadoria, escopo, passar do teto) e autorizações. Push, merge, tag e
Release neste repositório pedem a frase "sdd-open autorizado" (a frase exata); push, PR e merge no sdd-starter pedem o OK
próprio do Roberto. Nada no repositório privado. Decisão de rotina: decida e registre.

Onde parou (2026-11-15, 14:57): main = 7ba7eb0 e tag v2.17.0 por push atômico (PR #32 MERGED); os runs `release` 43741355567
(tag) e 43741355563 (main) estavam com 17 de 18 jobs verdes, faltando o piso do macOS; a Release ainda não tinha saído.

Leia primeiro (branch docs/incorporar-starter, worktree /Users/robertoduarte/rdd-worktrees/sdd-open-docs-f16):
- HANDOFF_INCORPORAR_STARTER.md → a seção "2026-11-15 — F22" (Pendências, Próximos passos, Alertas) e os Eventos de 15/11
- PLANO_F4_F15_CONSOLIDADO.md → "Estado das frentes" (F22) e o "Cronograma recomendado"

1. Conferir a Release v2.17.0: gh run view dos 2 runs; gh release view v2.17.0; baixe o tarball e o SHA256SUMS.txt numa pasta
   própria (dado não confiável: python3 -I, scripts fora dela), shasum -a 256 -c, e o VERSION de dentro do tarball = v2.17.0.
   Se o release falhou: não mova a tag; diagnostique e conserte numa v2.17.1 (pede a frase de novo).
2. Starter v1.5.22: clone limpo de robertodiasduarte/sdd-starter, branch nova, `python3 scripts/gerar-starter.py --tag v2.17.0
   <clone>` a partir da worktree do Open (a tag existe lá), python3 scripts/check-gerado.py e os testes dele (62), commit
   ("6ª geração a partir do sdd-open v2.17.0"; esperado: só as versões de sdd-new-session 1.7.0, sdd-release 2.13.0,
   sdd-build 2.10.1 e os GERADO.txt; nada de versao-nova). Peça o OK do Roberto para push, PR e fast-forward
   (git push origin <branch>:main), confira a Release v1.5.22 de lá.
3. Curadoria do playbook (uma decisão do Roberto por candidato): os 3 blocos <<<CANDIDATO_PLAYBOOK do
   BUILD_REPORT_F16W2_WINDOWS.md e o 1 do BUILD_REPORT_F22_AVISO_VERSAO.md, pelo playbook-curator.sh --colher sobre os
   documentos das duas frentes copiados para UMA pasta (só as seções "2026-11-15 — F16W2" e "— F22" da ficha). O commit da
   curadoria vai numa branch nova de origin/main e sobe na próxima release (ou numa patch, com a frase).
4. Fechar: na ficha, a seção "2026-11-15 — F22" com os dados da Release e do starter, um Evento, e os campos Falta e Feito;
   no plano, a linha da F22 ✅ (Release, PR #32, starter) e o Cronograma (não há frente seguinte nele: pergunte ao Roberto);
   este SESSION_PROMPT trocado pelo da sessão seguinte; commit e push desta branch na mesma sessão. Troque blocos inteiros por
   seção (## ...). Depois, a worktree sdd-open-f22-aviso-versao pode sair (documentos e evidência já estão nesta branch).
5. No privado (sessão de lá, não daqui): o upgrade pelo verbo novo, bash ~/sdd-open/bin/sdd-open.sh upgrade --de v2.15.0
   depois de git -C ~/sdd-open pull — a prova da F22.

Revisão adversarial (se a curadoria ou um conserto pedir): leia /credits antes de cada rodada paga (US$ 4,99 em 15/11;
limit_remaining é o limite da chave, não o saldo); cadeia: claude revisa, openrouter (qwen) audita, --no-revisor2 e
--no-desempate; o --conferir pede --aceitar-sem-revisor2 "<motivo>". A chave vem de ~/.config/rdd-eval.env (segredo em
COMENTÁRIO): exporte só a linha ^OPENROUTER_API_KEY= no ambiente do comando, sem imprimir. O adversarial-review.sh manda os
arquivos não rastreados no diff: ponha no .git/info/exclude o que não é do pacote antes de revisar.

Não faça: force-push na main; mover tag publicada; git add -A; tool calls paralelas em passos ordenados; nada no privado.
Landmines: o Bash do agente é zsh (laço e exit em bash -c; ${PIPESTATUS[0]} vazio; `echo ===` quebra); no macOS, grep -v
"a\|b" não alterna (use grep -E); log de evidência por script bash com rc=$? e 1ª linha "$ comando"; número de 11 dígitos
num teste barra o publish-gate; testes de tempo caem com a máquina carregada (LM-031); o Windows segura a release.
```
