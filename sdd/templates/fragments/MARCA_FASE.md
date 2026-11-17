# Fragmento — Marca de fase (custo por fase)

> Reusável. Lido pelas skills de fase (`sdd-brainstorm`, `sdd-define`, `sdd-ux-review`, `sdd-design`,
> `sdd-build`, `sdd-release`). É o **dono único** do porquê; cada skill traz só o comando.

## O que é

Duas linhas no trace da feature, uma quando a fase começa e outra quando termina:

```bash
bash sdd/bin/marca-fase.sh inicio <fase> <FEATURE>   # ao começar a fase
bash sdd/bin/marca-fase.sh fim <fase> <FEATURE>      # no encerramento, antes do resumo de etapa
```

`<fase>` é o nome da skill sem o `sdd-`: `brainstorm`, `define`, `ux-review`, `design`, `build`, `release`.
`<FEATURE>` é o `feature_id` dos artefatos (o `{F}` de `DEFINE_{F}.md`). A linha vai para
`sdd/traces/<FEATURE>.jsonl`, o mesmo arquivo em que o `verify-gate.sh` grava as voltas do gate.

## Por que existe

O registro local do agente guarda os tokens de cada mensagem, mas não diz de que fase ela era. Sem a marca,
o custo da sessão inteira cai em `sem fase`, e ninguém sabe se o Define custou mais que o Build, nem se uma
mudança no processo economizou. Com a marca, o `sdd/bin/custo-feature.sh <FEATURE>` (que a `sdd-release`
roda no encerramento) divide o custo por fase e grava `sdd/reports/CUSTO_<FEATURE>.md`.

## Regras

- **Sem terminal, ou sem o script no projeto, siga sem a marca.** A fase não depende dela; o custo daquele
  trecho vai para `sem fase`.
- **Brainstorm:** a marca de início entra assim que o nome da feature estiver decidido; a conversa antes dela
  fica fora da conta.
- **Fase encadeada** (uma fase chama a seguinte na mesma sessão): cada skill grava as suas duas marcas.
- **Fase que recomeça** (uma sessão nova retoma o build): grave `inicio` de novo; o contador conta as execuções.
- `SDD_TRACE=off` desliga as marcas, como desliga o trace do gate.
- A marca só leva fase, feature e horário: nada da conversa.

## Marca de papel

Um papel despachado em contexto fresco (avaliador, curador, cartógrafo…) também ganha marca, com o nome
`papel-<papel>`: `bash sdd/bin/marca-fase.sh inicio papel-avaliador <FEATURE>` antes do despacho e `fim` na volta
(a escada de `sdd-build/references/contexto-fresco.md` diz quando). A marca de papel não abre nem fecha fase: o que
cai na janela dela continua contando na fase em que ele rodou, e o `custo-feature.sh` mostra o papel numa sub-linha
`↳ papel <nome> · <modelos>`, fora do total. É por ela que se sabe se trocar o modelo de um papel economizou.
