# Verify Gate

## Purpose

Transformar aceitação em um stop condition objetivo. O gate é um único mecanismo pass/fail que poderá ser usado depois por Build/Release ou por validação humana explícita.

## Se é a sua primeira vez

> Responda uma pergunta só: **existe um comando que devolve 0 quando funciona?**
> - **Sim →** `kind: test`, `cmd` é esse comando, `pass_when: "exit 0"`. Vale para teste, smoke e typecheck.
> - **Não →** `kind: manual-ux`, `cmd: "N/A (manual-ux)"`, `manual_fallback` com 3 a 5 frases "Eu abri … e vi …".
> - Saída de LLM também cabe em `test`: um script que lê N exemplos, conta os acertos e sai 0 no piso.
> - Exemplo pronto: [assets/DEFINE_EXEMPLO.md](../assets/DEFINE_EXEMPLO.md). A tabela Taxonomy, mais abaixo, é para quem quiser os outros kinds.

## Canonical block

```yaml
verify_gate:
  kind: test
  cmd: "comando real do projeto"
  pass_when: "exit 0"
  threshold: "—"
  manual_fallback: "—"
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| kind | sempre | `test`, `smoke`, `eval`, `typecheck` ou `manual-ux` |
| cmd | exceto manual-ux | comando executável real |
| pass_when | sempre | `exit 0`, `exit N`, `contains: TEXT` ou critério humano no manual-ux |
| threshold | eval | alvo numérico documentado e embutido no comando |
| manual_fallback | manual-ux | checklist humano objetivo |

Não usar comentário inline nos valores do bloco.

## Taxonomy

| kind | Quando usar |
|---|---|
| test | lógica/estado/comportamento testável |
| smoke | endpoint ou integração real |
| eval | qualidade medida contra threshold |
| typecheck | compilação/tipos é o done signal |
| manual-ux | percepção/UX genuinamente humana, ou não existe comando (o aluno respondeu à pergunta da caixa) |

## From EARS to gate

- `When` → disparar evento e verificar resposta.
- `If/Then` → provocar falha/trigger pelo caminho real e verificar handling.
- `While` → montar o estado e verificar comportamento.
- `Where` → testar matriz on/off.
- `shall continue to` → caso explícito de regressão.

## Rules

- Nunca inventar comando de projeto.
- O agente não escolhe `manual-ux` por não saber o comando: faz ao aluno a pergunta da caixa acima; se a resposta é que não existe comando, `manual-ux` é o caminho.
- Um Verify Gate incompleto bloqueia conclusão do DEFINE.
- Para eval, o threshold precisa ser numérico.
- Para manual-ux, `cmd` deve ser `N/A (manual-ux)` e o checklist deve ser verificável.
