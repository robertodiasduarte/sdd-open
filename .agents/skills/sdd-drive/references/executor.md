# Executor do drive — brief do agente fresco de cada tarefa

Você faz **uma** tarefa e sai. Quem despacha este brief é a skill `sdd-drive`, pela escada de
`sdd-build/references/contexto-fresco.md`: subagente em contexto limpo; sem subagente, sessão nova
(`sdd-drive.sh aguardar … executor-drive …`, exit 40). Contrato de máquina: `sdd/WORKFLOW_CONTRACTS.yaml` › `sdd_drive`.

## Entrada (só isto chega — 5 campos)

```text
define: <caminho do DEFINE> · design: <caminho do DESIGN> · progress: sdd/reports/progress/PROGRESS_<F>.md · tarefa: <a linha do PROGRESS> · worktree: <raiz>
```

Se vier qualquer coisa além desses 5 campos (a conversa de quem despachou, hipóteses, o que a tarefa anterior tentou),
escreva `CONTAMINAÇÃO: sim — <o que veio>` no bloco e trabalhe **pelos arquivos** mesmo assim.

## Regras

1. Leia o DEFINE, o DESIGN e o `PROGRESS` desta sessão: você não tem memória da anterior.
2. Faça **só a tarefa do campo `tarefa:`**: o arquivo daquela linha do File Manifest, mais o teste dela. Nada adjacente.
3. Verifique a tarefa com o teste mais específico que existir. Vermelho ⇒ não marque; anote o erro na linha do `PROGRESS`, depois do
   nome do arquivo e de ` — `, para a próxima sessão.
4. Verde ⇒ `git add` por nome (nunca `-A`) e 1 commit só desta tarefa; depois troque `- [ ]` por `- [x]` na linha, mantendo
   o nome do arquivo primeiro. Não use `--amend` para citar o próprio commit.
5. **Não rode o Verify Gate do DEFINE**: quem roda é o script. Não mexa no bloco `## Verify Gate`.
6. **Nunca publique:** nada de `git push`, deploy ou `sdd-release`. Pergunta `[auto · de rotina]` vale a recomendada; as
   outras (D1 a D5) viram `bloqueio:`.
7. Precisou de arquivo fora do manifest ou o DESIGN contradiz o código? Não acomode: `bloqueio:`.

## Retorno (a última coisa da resposta)

```text
<<<RODADA
tarefa: <a linha do PROGRESS>
exit: <exit da verificação da tarefa>
sha: <commit curto, ou —>
bloqueio: <o que precisa de uma pessoa, ou —>
>>>
```
