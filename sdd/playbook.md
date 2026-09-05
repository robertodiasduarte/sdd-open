# Playbook de landmines — formato ACE-lite

Cada bullet tem ID estável (`LM-nnn`, nunca reusado), contadores `ajudou`/`mordeu`, `conf=` (última
confirmação) e `sup:` (superfícies greppáveis: nome de arquivo, comando, conceito). Regras completas na
skill `sdd-playbook`; formato validado por `sdd/bin/playbook-lint.sh`.

Como usar: a seção `## Sempre` é lida no início de toda sessão. O resto entra por superfície:
`sdd/bin/playbook-lint.sh --grep <termo> sdd/playbook.md` (fase Design e fase Build).
Nunca reescrever em massa, nunca renumerar, nunca apagar: aposentar = mover para `## Tombstones`
como `- [LM-nnn] ☠ data :: motivo`. Uma sessão só PROPÕE candidatos; quem aplica é a fase Release.

## Sempre

- [LM-001] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `grep -q` `verify-gate` `if (true)` `asserção` :: Um gate que só confere FIAÇÃO (o `grep` acha a chamada, a regra CSS existe) fica verde com `if (true)` — ele prova que o texto está lá, não que o comportamento acontece. **Do instead:** o gate EXECUTA o código com fixtures dos dois lados (caso que passa E caso que falha) e valida-se com um mutante que derruba uma asserção nomeada. · promovido_para: —
- [LM-002] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `exit 0` `baseline` `sed -n` `grep -c` :: Uma asserção que NÃO AVALIA NADA sai `exit 0`: quoting corrompido faz o `grep` nem rodar, âncora de `sed` casa o bloco errado e a contagem dá zero antes e depois. **Do instead:** toda asserção precisa de baseline VERMELHO — rode-a contra a árvore ANTES da mudança; se já passa, ela não prova a mudança. · promovido_para: —
- [LM-003] ajudou=0 mordeu=0 · conf=2026-09-05 · sup: `git status` `--uncommitted` `review` `untracked` :: Trabalho commitado com arquivos untracked ao lado faz um review de "não commitado" revisar o VAZIO — e um review que passou sobre diff nenhum é pior que review nenhum. **Do instead:** commitar antes de qualquer review externo; conferir que o diff revisado tem os arquivos que você mudou (`git diff --stat` bate com a lista do review). · promovido_para: —

## Tombstones
